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

```sh
just run
# o: uv run python -m dashboard [--port 8000] [-d "Salón"] [--no-cast]
```

El programa es autocontenido: arranca el servidor (puerto 8000, accesible desde
la red) y, una vez listo, envía el dashboard a pantalla completa al dispositivo
**por defecto de `catt`** con `catt cast_site`. Al cerrar el servidor desconecta
el dispositivo (`catt stop`). Si el envío falla, reintenta 5 veces cada 15 s.

- `-d`, `--device`: nombre o IP del dispositivo, en lugar del predeterminado.
- `--no-cast`: solo servidor, sin castear.
- Se puede apagar de forma limpia desde `/admin` (botón "Apagar servidor").
- Puedes listar dispositivos con `catt scan` y fijar el predeterminado con
  `catt set_default "Salón"`.

La IP local de la máquina se usa para que el dispositivo llegue al servidor, por
lo que el puerto no debe estar bloqueado por el firewall. También puedes abrir
<http://localhost:8000/> en un navegador.

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
| `just run`       | Arranca servidor y castea     |

## Estructura

```
src/dashboard/
├── __main__.py      # CLI
├── cast.py          # Envío automático con catt
├── app.py           # FastAPI + WebSocket + métricas
└── static/index.html
```
