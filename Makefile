build:
	uv run python -m build --wheel

test:
	uv run python -m pytest tests/
