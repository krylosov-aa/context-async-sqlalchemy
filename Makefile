lint:
	ruff format .
	mypy .
	ruff check --fix .
	flake8 .

test:
	pytest --cov context_async_sqlalchemy tests examples/fastapi_example/tests examples/starlette_example/tests examples/fastapi_with_pure_asgi_example/tests --cov-report=term-missing

test_fastapi:
	pytest examples/fastapi_example/tests

test_starlette:
	pytest examples/starlette_example/tests

uv:
	uv sync
	source .venv/bin/activate

build:
	uv build

publish:
	uv publish
