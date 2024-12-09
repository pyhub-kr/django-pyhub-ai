build:
	uv run -m build --wheel

test:
	uv run -m pytest tests/

format:
	uv run -m black ./src ./tests/
	uv run -m isort ./src ./tests/

doc-server:
	cd docs && uv run sphinx-autobuild . _build/html

doc-build:
	cd docs && uv run sphinx-build -b html -d _build/doctrees -W --keep-going . _build/html
