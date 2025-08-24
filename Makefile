# DL Creator Application Makefile

.PHONY: help build up down dev-up dev-down logs clean start stop install

# Default target
help:
	@echo "DL Creator Application - Available Commands:"
	@echo ""
	@echo "Docker Commands:"
	@echo "  build     - Build all Docker images"
	@echo "  up        - Start all services in production mode"
	@echo "  down      - Stop and remove all containers"
	@echo "  dev-up    - Start all services in development mode"
	@echo "  dev-down  - Stop development containers"
	@echo "  logs      - Show logs from all services"
	@echo "  clean     - Remove all containers, images, and volumes"
	@echo ""
	@echo "Development Commands:"
	@echo "  start     - Start all services without Docker"
	@echo "  stop      - Stop all development services"
	@echo "  install   - Install dependencies for all services"
	@echo ""
	@echo "Individual Service Commands:"
	@echo "  frontend  - Start only frontend service"
	@echo "  backend   - Start only backend service"
	@echo "  rasa      - Start only Rasa services"

# Docker Commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

dev-up:
	docker-compose -f docker-compose.dev.yml up -d

dev-down:
	docker-compose -f docker-compose.dev.yml down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v --rmi all --remove-orphans
	docker system prune -f

# Development Commands
start:
	@echo "Starting development environment..."
	@chmod +x dev-start.sh
	./dev-start.sh

stop:
	@echo "Stopping development environment..."
	@chmod +x dev-stop.sh
	./dev-stop.sh

install:
	@echo "Installing dependencies..."
	@echo "Installing frontend dependencies..."
	cd frontend/dl-creator && npm install
	@echo "Installing backend dependencies..."
	cd backend/dl_creator && ./mvnw dependency:resolve
	@echo "Installing Rasa dependencies..."
	cd chatbot && python3 -m venv rasa_env && source rasa_env/bin/activate && pip install -r requirements.txt
	@echo "Dependencies installed successfully!"

# Individual Service Commands
frontend:
	docker-compose up frontend

backend:
	docker-compose up backend

rasa:
	docker-compose up rasa-server action-server

# Production Commands
prod-up:
	docker-compose --profile production up -d

prod-down:
	docker-compose --profile production down

# Utility Commands
status:
	docker-compose ps

restart:
	docker-compose restart

rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

# Database Commands
db-reset:
	docker-compose down -v
	docker-compose up -d postgres

# Log Commands
logs-frontend:
	docker-compose logs -f frontend

logs-backend:
	docker-compose logs -f backend

logs-rasa:
	docker-compose logs -f rasa-server action-server

# Health Check
health:
	@echo "Checking service health..."
	@curl -f http://localhost:3000 > /dev/null 2>&1 && echo "Frontend: OK" || echo "Frontend: FAILED"
	@curl -f http://localhost:7500/actuator/health > /dev/null 2>&1 && echo "Backend: OK" || echo "Backend: FAILED"
	@curl -f http://localhost:5005/status > /dev/null 2>&1 && echo "Rasa Server: OK" || echo "Rasa Server: FAILED"
	@curl -f http://localhost:5055 > /dev/null 2>&1 && echo "Rasa Actions: OK" || echo "Rasa Actions: FAILED"

# Docker Hub Commands
hub-login:
	@echo "Logging in to Docker Hub..."
	docker login

hub-push:
	@echo "Building and pushing to Docker Hub..."
	@chmod +x docker-hub-push.sh
	./docker-hub-push.sh

hub-push-version:
	@echo "Building and pushing versioned images to Docker Hub..."
	@chmod +x docker-hub-push.sh
	./docker-hub-push.sh --version $(VERSION)

hub-run:
	@echo "Running from Docker Hub images..."
	docker-compose -f docker-compose.hub.yml up -d

hub-run-version:
	@echo "Running specific version from Docker Hub..."
	DOCKER_USERNAME=$(DOCKER_USERNAME) VERSION=$(VERSION) docker-compose -f docker-compose.hub.yml up -d
