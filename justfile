default: check

check: lint typecheck

typecheck:
    uv run ty check

lint:
    uv run ruff check

fmt:
    uv run ruff format
    uv run ruff check --fix

# Start the server and cast to catt's default device
run *args:
    uv run python -m dashboard {{args}}
