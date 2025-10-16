.PHONY: help install dev test coverage lint format clean docker-up docker-down migrate init-db

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Run development server
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	pytest

coverage: ## Run tests with coverage
	pytest --cov=app --cov-report=html --cov-report=term-missing

lint: ## Run linters
	flake8 app tests
	mypy app

format: ## Format code with black
	black app tests

clean: ## Clean cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-rebuild: ## Rebuild and restart Docker containers
	docker-compose down
	docker-compose build
	docker-compose up -d

migrate: ## Run database migrations
	alembic upgrade head

migrate-create: ## Create a new migration (use MSG="description")
	alembic revision --autogenerate -m "$(MSG)"

migrate-down: ## Rollback last migration
	alembic downgrade -1

init-db: ## Initialize database with sample data
	python scripts/init_db.py

generate-secret: ## Generate a new secret key
	python scripts/generate_secret.py

shell: ## Open Python shell with app context
	python -i -c "from app.main import app; from app.db.session import AsyncSessionLocal"

psql: ## Connect to PostgreSQL database
	docker-compose exec postgres psql -U user -d userdb

redis-cli: ## Connect to Redis
	docker-compose exec redis redis-cli
