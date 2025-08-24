#!/bin/bash

# DL Creator - Run Script
# This script provides easy commands to run the application

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
}

# Function to check if Maven is installed
check_maven() {
    if ! command -v mvn &> /dev/null; then
        print_error "Maven is not installed. Please install Maven and try again."
        exit 1
    fi
}

# Function to check if Java is installed
check_java() {
    if ! command -v java &> /dev/null; then
        print_error "Java is not installed. Please install Java 17 or higher and try again."
        exit 1
    fi
    
    # Check Java version
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2 | cut -d'.' -f1)
    if [ "$JAVA_VERSION" -lt 17 ]; then
        print_error "Java 17 or higher is required. Current version: $JAVA_VERSION"
        exit 1
    fi
}

# Function to show H2 console info
show_h2_info() {
    print_success "Application started successfully!"
    print_status "Access points:"
    print_status "  - API: http://localhost:7500"
    print_status "  - H2 Console: http://localhost:7500/h2-console"
    print_status "    JDBC URL: jdbc:h2:mem:dl_creator_db"
    print_status "    Username: sa"
    print_status "    Password: (leave empty)"
}

# Function to run locally
run_local() {
    print_status "Running application locally..."
    check_java
    check_maven
    
    print_status "Building project..."
    mvn clean install -DskipTests
    
    print_status "Starting application with H2 in-memory database..."
    mvn spring-boot:run &
    
    # Wait a moment for the application to start
    sleep 5
    show_h2_info
}

# Function to run with Docker
run_docker() {
    print_status "Running application with Docker..."
    check_docker
    
    print_status "Building and starting application with H2 database..."
    docker-compose up --build
}

# Function to run with Docker in background
run_docker_detached() {
    print_status "Running application with Docker in background..."
    check_docker
    
    print_status "Building and starting application with H2 database in background..."
    docker-compose up -d --build
    
    print_success "Application is starting in background..."
    show_h2_info
    print_status "You can check logs with: docker-compose logs -f"
    print_status "Stop services with: docker-compose down"
}

# Function to stop Docker services
stop_docker() {
    print_status "Stopping Docker services..."
    docker-compose down
    print_success "Docker services stopped"
}

# Function to show logs
show_logs() {
    print_status "Showing application logs..."
    docker-compose logs -f
}

# Function to clean up
cleanup() {
    print_status "Cleaning up..."
    docker-compose down -v
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to show help
show_help() {
    echo "DL Creator - Run Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  local           Run application locally (requires Java 17+ and Maven)"
    echo "  docker          Run application with Docker Compose"
    echo "  docker-bg       Run application with Docker Compose in background"
    echo "  stop            Stop Docker services"
    echo "  logs            Show Docker logs"
    echo "  cleanup         Clean up Docker containers and volumes"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 local        # Run locally"
    echo "  $0 docker       # Run with Docker"
    echo "  $0 docker-bg    # Run with Docker in background"
    echo "  $0 stop         # Stop Docker services"
}

# Main script logic
case "${1:-help}" in
    "local")
        run_local
        ;;
    "docker")
        run_docker
        ;;
    "docker-bg")
        run_docker_detached
        ;;
    "stop")
        stop_docker
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
