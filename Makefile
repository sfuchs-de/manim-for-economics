.PHONY: setup doctor demo test preview frames qa docker-build docker-demo

setup:
	uv sync --frozen

doctor:
	uv run econ-manim doctor --strict

demo:
	uv run econ-manim demo

test:
	uv run ruff check .
	uv run pytest

preview:
	uv run econ-manim preview starter --overlay

frames:
	uv run econ-manim frames starter

qa:
	uv run econ-manim qa starter

docker-build:
	docker compose build

docker-demo:
	docker compose run --rm econ-manim demo
