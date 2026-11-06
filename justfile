default: check

check: lint typecheck

typecheck:
    uv run ty check

lint:
    uv run ruff check

fmt:
    uv run ruff format
    uv run ruff check --fix

# Arranca el servidor web (puerto 8000)
run:
    uv run python -m dashboard serve

# Castea a pantalla completa: just cast "Salón"
cast device="":
    uv run python -m dashboard cast {{ if device != "" { "-d " + device } else { "" } }}
