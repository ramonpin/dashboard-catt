"""Envío automático del dashboard a un dispositivo `catt`."""

import asyncio
import contextlib
import logging
import os
import socket

log = logging.getLogger("uvicorn.error")

RETRIES = 5
RETRY_DELAY = 15.0  # segundos entre reintentos
STOP_TIMEOUT = 20.0  # segundos máximos para `catt stop`


def lan_ip() -> str:
    """IP local accesible desde la red (para que el dispositivo llegue al servidor)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"


def dashboard_url(port: int) -> str:
    return f"http://{lan_ip()}:{port}/"


async def cast_dashboard(port: int, device: str | None = None) -> bool:
    """Ejecuta `catt cast_site`; sin `device` usa el dispositivo por defecto de catt."""
    url = dashboard_url(port)
    cmd = ["catt", *(["-d", device] if device else []), "cast_site", url]
    for attempt in range(1, RETRIES + 1):
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            out, _ = await proc.communicate()
        except FileNotFoundError:
            log.error("No se encontró el ejecutable `catt`")
            return False
        if proc.returncode == 0:
            log.info("Dashboard enviado al dispositivo: %s", url)
            return True
        log.warning(
            "catt falló (intento %d/%d): %s",
            attempt,
            RETRIES,
            out.decode(errors="replace").strip(),
        )
        await asyncio.sleep(RETRY_DELAY)
    return False


async def stop_cast(device: str | None = None) -> bool:
    """Ejecuta `catt stop` para desconectar el dashboard del dispositivo."""
    cmd = ["catt", *(["-d", device] if device else []), "stop"]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
        )
        out, _ = await asyncio.wait_for(proc.communicate(), STOP_TIMEOUT)
    except FileNotFoundError, TimeoutError:
        log.warning("No se pudo desconectar el dispositivo")
        return False
    if proc.returncode != 0:
        log.warning("catt stop falló: %s", out.decode(errors="replace").strip())
        return False
    log.info("Dispositivo desconectado")
    return True


async def cast_when_ready(port: int, device: str | None) -> bool:
    """Espera a que el servidor acepte conexiones y entonces castea."""
    for _ in range(50):
        with contextlib.suppress(OSError):
            _, w = await asyncio.open_connection("127.0.0.1", port)
            w.close()
            break
        await asyncio.sleep(0.2)
    return await cast_dashboard(port, device)


def config_from_env() -> tuple[bool, int, str | None]:
    """(castear, puerto, dispositivo) según las variables que fija el CLI."""
    return (
        os.environ.get("DASHBOARD_CAST", "1") == "1",
        int(os.environ.get("DASHBOARD_PORT", "8000")),
        os.environ.get("DASHBOARD_CAST_DEVICE") or None,
    )
