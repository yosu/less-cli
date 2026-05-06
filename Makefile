.PHONY: test lint clean-db index search

test:
	python3 -m poetry run pytest -v

lint:
	python3 -m poetry run ruff check .

clean-db:
	rm -rf chroma_data

index:
	python3 -m poetry run less index $(DIR)

search:
	python3 -m poetry run less search "$(Q)"
