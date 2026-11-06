"""CLI: `python -m dashboard serve` o `python -m dashboard cast [--device X]`."""

import argparse
import socket
import subprocess
import sys

import uvicorn


def lan_ip() -> str:
    """IP local accesible desde la red (para que el Chromecast llegue al servidor)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"


def main() -> None:
    parser = argparse.ArgumentParser(prog="dashboard")
    sub = parser.add_subparsers(dest="cmd", required=True)
    serve = sub.add_parser("serve", help="Arranca el servidor web")
    serve.add_argument("--host", default="0.0.0.0")
    serve.add_argument("--port", type=int, default=8000)
    cast = sub.add_parser("cast", help="Castea el dashboard con catt")
    cast.add_argument("--port", type=int, default=8000)
    cast.add_argument("-d", "--device", help="Nombre o IP del dispositivo catt")
    args = parser.parse_args()

    if args.cmd == "serve":
        uvicorn.run("dashboard.app:app", host=args.host, port=args.port)
    else:
        url = f"http://{lan_ip()}:{args.port}/"
        cmd = (
            ["catt"] + (["-d", args.device] if args.device else []) + ["cast_site", url]
        )
        print("→", " ".join(cmd))
        sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
