"""Arranca el servidor del dashboard y lo envía al dispositivo `catt`."""

import argparse
import os

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="dashboard",
        description="Servidor del dashboard; castea automáticamente al arrancar.",
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "-d",
        "--device",
        help="Nombre o IP del dispositivo catt (por defecto, el de catt)",
    )
    parser.add_argument(
        "--no-cast", action="store_true", help="No enviar el dashboard al dispositivo"
    )
    args = parser.parse_args()

    os.environ["DASHBOARD_CAST"] = "0" if args.no_cast else "1"
    os.environ["DASHBOARD_PORT"] = str(args.port)
    os.environ["DASHBOARD_CAST_DEVICE"] = args.device or ""
    uvicorn.run("dashboard.app:app", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
