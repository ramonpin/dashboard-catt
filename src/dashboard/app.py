"""Servidor del dashboard: métricas del sistema y tiempo en Madrid por WebSocket."""

import asyncio
import contextlib
import time
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any, Literal

import httpx
import psutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

STATIC = Path(__file__).parent / "static"
WEATHER_TTL = 600.0  # segundos entre consultas al tiempo

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=40.4168&longitude=-3.7038"
    "&current=temperature_2m,apparent_temperature,relative_humidity_2m,"
    "wind_speed_10m,weather_code"
    "&daily=temperature_2m_max,temperature_2m_min"
    "&timezone=Europe%2FMadrid&forecast_days=1"
)


class Cards(BaseModel):
    cpu: bool = True
    mem: bool = True
    temp: bool = True
    weather: bool = True


class Settings(BaseModel):
    """Ajustes de visualización modificables desde la página de administración."""

    interval: float = Field(default=2.0, ge=1, le=60)  # segundos entre envíos
    units: Literal["C", "F"] = "C"
    cards: Cards = Cards()


settings = Settings()
_changed: set[asyncio.Event] = set()  # una por conexión; despierta al cambiar ajustes
_weather: dict[str, Any] | None = None


def cpu_temperature() -> float | None:
    """Devuelve la temperatura de CPU en °C, si hay sensores disponibles."""
    try:
        sensors = psutil.sensors_temperatures()
    except AttributeError:
        return None
    for name in ("coretemp", "k10temp", "cpu_thermal", "zenpower", "acpitz"):
        if sensors.get(name):
            return sensors[name][0].current
    for entries in sensors.values():
        if entries:
            return entries[0].current
    return None


def system_metrics() -> dict[str, Any]:
    mem = psutil.virtual_memory()
    return {
        "cpu": psutil.cpu_percent(interval=None),
        "cpu_per_core": psutil.cpu_percent(interval=None, percpu=True),
        "mem_percent": mem.percent,
        "mem_used": mem.used,
        "mem_total": mem.total,
        "temp": cpu_temperature(),
        "time": time.time(),
    }


async def refresh_weather() -> None:
    """Consulta el tiempo en Madrid (Open-Meteo); conserva el último valor si falla."""
    global _weather
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(WEATHER_URL)
            r.raise_for_status()
            data = r.json()
        _weather = {
            "temp": data["current"]["temperature_2m"],
            "feels": data["current"]["apparent_temperature"],
            "humidity": data["current"]["relative_humidity_2m"],
            "wind": data["current"]["wind_speed_10m"],
            "code": data["current"]["weather_code"],
            "max": data["daily"]["temperature_2m_max"][0],
            "min": data["daily"]["temperature_2m_min"][0],
        }
    except httpx.HTTPError, KeyError, ValueError:
        pass


async def weather_loop() -> None:
    """Actualiza el tiempo cada WEATHER_TTL segundos, con independencia de los clientes."""
    while True:
        await refresh_weather()
        await asyncio.sleep(WEATHER_TTL)


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    psutil.cpu_percent(interval=None)  # primera llamada de calibración
    task = asyncio.create_task(weather_loop())
    yield
    task.cancel()


app = FastAPI(title="dashboard-catt", lifespan=lifespan)


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/admin", include_in_schema=False)
async def admin() -> FileResponse:
    """Página de administración (no enlazada desde el dashboard)."""
    return FileResponse(STATIC / "admin.html")


@app.get("/api/settings", include_in_schema=False)
async def get_settings() -> Settings:
    return settings


@app.put("/api/settings", include_in_schema=False)
async def put_settings(new: Settings) -> Settings:
    global settings
    settings = new
    for event in _changed:
        event.set()
    return settings


@app.websocket("/ws")
async def ws(websocket: WebSocket) -> None:
    await websocket.accept()
    changed = asyncio.Event()
    _changed.add(changed)
    try:
        while True:
            payload = system_metrics()
            payload["weather"] = _weather
            payload["settings"] = settings.model_dump()
            await websocket.send_json(payload)
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(changed.wait(), settings.interval)
            changed.clear()
    except WebSocketDisconnect, RuntimeError:
        pass
    finally:
        _changed.discard(changed)
