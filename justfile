default: check

check: lint typecheck

typecheck:
    uv run ty check

lint:
    uv run ruff check

fmt:
    uv run ruff format
    uv run ruff check --fix

# Arranca el servidor y castea al dispositivo por defecto de catt
run *args:
    uv run python -m dashboard {{args}}
