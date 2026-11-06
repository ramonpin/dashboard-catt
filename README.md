# dashboard-catt

Dashboard web que muestra en tiempo real la CPU, la memoria y la temperatura de
la máquina, además del tiempo en Madrid. Se actualiza solo por WebSockets y se
puede castear a pantalla completa a cualquier dispositivo compatible con
[`catt`](https://github.com/skorokithakis/catt) (Chromecast, Google TV, etc.).

## Requisitos

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/)
- [just](https://github.com/casey/just) (opcional, para los atajos)
- Un dispositivo compatible con `catt` en la misma red local (solo para castear)

## Instalación

```sh
uv sync
```

## Uso

Arrancar el servidor (puerto 8000, accesible desde la red):

```sh
just run
# o: uv run python -m dashboard serve [--host 0.0.0.0] [--port 8000]
```

Abrir <http://localhost:8000/> en el navegador.

Castear a pantalla completa:

```sh
just cast "Salón"
# o: uv run python -m dashboard cast [-d "Salón"] [--port 8000]
```

Sin dispositivo se usa el predeterminado de `catt`. Puedes listar los
disponibles con `catt scan`. El comando `cast` usa la IP local de la máquina
para que el dispositivo pueda llegar al servidor, por lo que el servidor debe
estar en marcha y el puerto no debe estar bloqueado por el firewall.

## Cómo funciona

- `GET /` sirve la página ([`index.html`](src/dashboard/static/index.html)).
- `WS /ws` envía cada 2 s un JSON con `cpu`, `cpu_per_core`, `mem_percent`,
  `mem_used`, `mem_total`, `temp` y `weather`.
- Las métricas del sistema se leen con `psutil`. Si no hay sensores de
  temperatura, la tarjeta muestra "n/d".
- El tiempo de Madrid viene de [Open-Meteo](https://open-meteo.com/) (sin clave
  de API), actualizado en segundo plano cada 10 minutos.
- La interfaz se reconecta automáticamente si se pierde el WebSocket y escala al
  tamaño de la pantalla.

## Desarrollo

| Receta           | Descripción                   |
| ---------------- | ----------------------------- |
| `just check`     | Lint y comprobación de tipos  |
| `just lint`      | `ruff check`                  |
| `just typecheck` | `ty check`                    |
| `just fmt`       | Formatea y corrige con `ruff` |
| `just run`       | Arranca el servidor           |
| `just cast`      | Castea el dashboard           |

## Estructura

```
src/dashboard/
├── __main__.py      # CLI: serve / cast
├── app.py           # FastAPI + WebSocket + métricas
└── static/index.html
```
