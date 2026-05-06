.PHONY: test lint

test:
	python3 -m poetry run pytest -v

lint:
	python3 -m poetry run ruff check .
