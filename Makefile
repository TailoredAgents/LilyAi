.PHONY: help up down build restart logs shell migrate seed test format lint typecheck clean

help:
	@echo "Available commands:"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make build       - Build containers"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - Show logs"
	@echo "  make shell       - Open API shell"
	@echo "  make migrate     - Run database migrations"
	@echo "  make seed        - Seed database with initial data"
	@echo "  make test        - Run all tests"
	@echo "  make format      - Format code"
	@echo "  make lint        - Run linters"
	@echo "  make typecheck   - Run type checking"
	@echo "  make clean       - Clean up containers and volumes"

up:
	docker compose -f infra/compose.core.yml up -d
	docker compose -f infra/compose.satellites.yml up -d
	@echo "Services started!"
	@echo "API: http://localhost:8000/docs"
	@echo "Web: http://localhost:3000"
	@echo "Chatwoot: http://localhost:8080"
	@echo "n8n: http://localhost:5678"

down:
	docker compose -f infra/compose.satellites.yml down
	docker compose -f infra/compose.core.yml down

build:
	docker compose -f infra/compose.core.yml build
	docker compose -f infra/compose.satellites.yml build

restart: down up

logs:
	docker compose -f infra/compose.core.yml logs -f

logs-all:
	docker compose -f infra/compose.core.yml logs -f &
	docker compose -f infra/compose.satellites.yml logs -f

shell:
	docker compose -f infra/compose.core.yml exec api /bin/bash

migrate:
	docker compose -f infra/compose.core.yml exec api alembic upgrade head

migration:
	@read -p "Enter migration name: " name; \
	docker compose -f infra/compose.core.yml exec api alembic revision --autogenerate -m "$$name"

seed:
	docker compose -f infra/compose.core.yml exec api python -m app.db.seed

test:
	docker compose -f infra/compose.core.yml exec api pytest
	cd web && npm test

test-backend:
	docker compose -f infra/compose.core.yml exec api pytest -v

test-frontend:
	cd web && npm test

format:
	docker compose -f infra/compose.core.yml exec api black .
	docker compose -f infra/compose.core.yml exec api isort .
	cd web && npm run format

lint:
	docker compose -f infra/compose.core.yml exec api ruff check .
	cd web && npm run lint

typecheck:
	docker compose -f infra/compose.core.yml exec api mypy app
	cd web && npm run typecheck

clean:
	docker compose -f infra/compose.satellites.yml down -v
	docker compose -f infra/compose.core.yml down -v
	docker system prune -f

dev-install:
	cd backend && pip install -e .
	cd web && npm install

redis-cli:
	docker compose -f infra/compose.core.yml exec redis redis-cli

psql:
	docker compose -f infra/compose.core.yml exec postgres psql -U lily -d lily_saas