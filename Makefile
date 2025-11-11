lint:
	ruff format .
	mypy .
	ruff check --fix .
	flake8 .

test:
	pytest --cov context_async_sqlalchemy exmaples/fastapi_example/tests --cov-report=term-missing

uv:
	uv sync
	source .venv/bin/activate

build:
	uv build

publish:
	uv publish
