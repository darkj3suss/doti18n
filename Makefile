.PHONY: lint format check

lint:
	ruff check .

format:
	ruff check . --fix
	black .

check:
	ruff check .
	black --check .
	mypy .
