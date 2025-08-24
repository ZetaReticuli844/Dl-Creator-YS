#!/bin/bash

# Docker build and deployment script for DL Creator

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to build production image
build_production() {
    print_status "Building production Docker image..."
    docker build -t dl-creator:latest .
    print_success "Production image built successfully"
}

# Function to build development image
build_development() {
    print_status "Building development Docker image..."
    docker build -f Dockerfile.dev -t dl-creator:dev .
    print_success "Development image built successfully"
}

# Function to run development environment
run_development() {
    print_status "Starting development environment..."
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
    print_success "Development environment started"
    print_status "Frontend: http://localhost:5173"
    print_status "Backend: http://localhost:7500"
    print_status "Rasa: http://localhost:5005"
}

# Function to run production environment
run_production() {
    print_status "Starting production environment..."
    docker-compose up -d
    print_success "Production environment started"
    print_status "Application: http://localhost:3000"
}

# Function to stop all containers
stop_containers() {
    print_status "Stopping all containers..."
    docker-compose down
    print_success "All containers stopped"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker system prune -f
    docker volume prune -f
    print_success "Cleanup completed"
}

# Function to show logs
show_logs() {
    print_status "Showing logs..."
    docker-compose logs -f
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build-prod    Build production Docker image"
    echo "  build-dev     Build development Docker image"
    echo "  dev           Start development environment"
    echo "  prod          Start production environment"
    echo "  stop          Stop all containers"
    echo "  logs          Show container logs"
    echo "  cleanup       Clean up Docker resources"
    echo "  help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build-prod"
    echo "  $0 dev"
    echo "  $0 prod"
}

# Main script logic
main() {
    check_docker

    case "${1:-help}" in
        "build-prod")
            build_production
            ;;
        "build-dev")
            build_development
            ;;
        "dev")
            run_development
            ;;
        "prod")
            run_production
            ;;
        "stop")
            stop_containers
            ;;
        "logs")
            show_logs
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"
