# dashboard-catt

Web dashboard that shows the machine's CPU, memory and temperature in real time,
plus the weather in Madrid. It updates itself over WebSockets and can be cast
full-screen to any device supported by
[`catt`](https://github.com/skorokithakis/catt) (Chromecast, Google TV, etc.).

## Requirements

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/)
- [just](https://github.com/casey/just) (optional, for the shortcuts)
- A `catt`-compatible device on the same local network (only needed for casting)

## Installation

```sh
uv sync
```

## Usage

```sh
just run
# or: uv run python -m dashboard [--port 8000] [-d "Living room"] [--no-cast]
```

The program is self-contained: it starts the server (port 8000, reachable from
the network) and, once it is ready, sends the dashboard full-screen to `catt`'s
**default device** with `catt cast_site`. When the server shuts down it
disconnects the device (`catt stop`). If casting fails, it retries 5 times, 15 s
apart.

- `-d`, `--device`: device name or IP, instead of the default one.
- `--no-cast`: server only, no casting.
- It can be shut down cleanly from `/admin` (the "Apagar servidor" button).
- You can list devices with `catt scan` and set the default with
  `catt set_default "Living room"`.

The machine's local IP is used so the device can reach the server, so the port
must not be blocked by the firewall. You can also open <http://localhost:8000/>
in a browser.

## How it works

- `GET /` serves the page ([`index.html`](src/dashboard/static/index.html)).
- `WS /ws` sends a JSON message every 2 s with `cpu`, `cpu_per_core`,
  `mem_percent`, `mem_used`, `mem_total`, `temp` and `weather`.
- System metrics are read with `psutil`. If there are no temperature sensors,
  the card shows "n/d" (not available).
- The Madrid weather comes from [Open-Meteo](https://open-meteo.com/) (no API
  key), refreshed in the background every 10 minutes.
- The UI reconnects automatically if the WebSocket is lost and scales to the
  screen size.

## Development

| Recipe           | Description                |
| ---------------- | -------------------------- |
| `just check`     | Lint and type check        |
| `just lint`      | `ruff check`               |
| `just typecheck` | `ty check`                 |
| `just fmt`       | Format and fix with `ruff` |
| `just run`       | Start the server and cast  |

## Structure

```
src/dashboard/
├── __main__.py      # CLI
├── cast.py          # Automatic casting with catt
├── app.py           # FastAPI + WebSocket + metrics
└── static/index.html
```
