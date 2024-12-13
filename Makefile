build:
	uv run -m build --wheel

test:
	uv run -m pytest tests/

format:
	uv run -m black ./src ./tests/
	uv run -m isort ./src ./tests/

tailwind-start:
	cd src/pyhub_ai/static_src && npm run start

tailwind-build:
	cd src/pyhub_ai/static_src && npm run build:clean && npm run build

tailwind-dev:
	cd src/pyhub_ai/static_src && npm run dev

doc-server:
	cd docs && uv run sphinx-autobuild . _build/html

doc-build:
	cd docs && uv run sphinx-build -b html -d _build/doctrees -W --keep-going . _build/html

test-dev-server:
	cd tests && uv run python manage.py runserver
