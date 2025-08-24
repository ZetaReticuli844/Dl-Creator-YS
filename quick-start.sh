#!/bin/bash

# DL Creator Quick Start Script
# Interactive menu for starting the application

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
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        return 1
    fi
    return 0
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check for Java
    if ! command -v java >/dev/null 2>&1; then
        print_error "Java is not installed. Please install Java 11 or higher."
        return 1
    fi
    
    # Check for Node.js
    if ! command -v node >/dev/null 2>&1; then
        print_error "Node.js is not installed. Please install Node.js 16 or higher."
        return 1
    fi
    
    # Check for Python
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        return 1
    fi
    
    print_success "All prerequisites are satisfied!"
    return 0
}

# Function to show menu
show_menu() {
    clear
    echo "=========================================="
    echo "    DL Creator Application Quick Start"
    echo "=========================================="
    echo ""
    echo "Choose an option:"
    echo ""
    echo "1. Start with Docker (Production)"
    echo "2. Start with Docker (Development)"
    echo "3. Start without Docker (Development)"
    echo "4. Stop all services"
    echo "5. View logs"
    echo "6. Check status"
    echo "7. Install dependencies"
    echo "8. Exit"
    echo ""
    echo "=========================================="
}

# Function to start with Docker production
start_docker_prod() {
    print_status "Starting with Docker (Production)..."
    if check_docker; then
        docker-compose up -d
        print_success "Services started successfully!"
        echo ""
        echo "Application URLs:"
        echo "  Frontend: http://localhost:3000"
        echo "  Backend API: http://localhost:7500"
        echo "  Rasa Server: http://localhost:5005"
    else
        print_error "Failed to start Docker services"
    fi
}

# Function to start with Docker development
start_docker_dev() {
    print_status "Starting with Docker (Development)..."
    if check_docker; then
        docker-compose -f docker-compose.dev.yml up -d
        print_success "Development services started successfully!"
        echo ""
        echo "Application URLs:"
        echo "  Frontend: http://localhost:3000"
        echo "  Backend API: http://localhost:7500"
        echo "  Rasa Server: http://localhost:5005"
    else
        print_error "Failed to start Docker development services"
    fi
}

# Function to start without Docker
start_without_docker() {
    print_status "Starting without Docker (Development)..."
    if check_prerequisites; then
        chmod +x dev-start.sh
        ./dev-start.sh
    else
        print_error "Prerequisites not met. Please install required software."
    fi
}

# Function to stop all services
stop_services() {
    print_status "Stopping all services..."
    
    # Stop Docker services
    docker-compose down 2>/dev/null || true
    docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
    
    # Stop development services
    chmod +x dev-stop.sh
    ./dev-stop.sh 2>/dev/null || true
    
    print_success "All services stopped!"
}

# Function to view logs
view_logs() {
    echo ""
    echo "Choose log type:"
    echo "1. All services (Docker)"
    echo "2. Frontend logs"
    echo "3. Backend logs"
    echo "4. Rasa logs"
    echo "5. Back to main menu"
    echo ""
    read -p "Enter your choice: " log_choice
    
    case $log_choice in
        1)
            docker-compose logs -f
            ;;
        2)
            docker-compose logs -f frontend
            ;;
        3)
            docker-compose logs -f backend
            ;;
        4)
            docker-compose logs -f rasa-server action-server
            ;;
        5)
            return
            ;;
        *)
            print_error "Invalid choice"
            ;;
    esac
}

# Function to check status
check_status() {
    print_status "Checking service status..."
    echo ""
    
    # Check Docker services
    if docker-compose ps >/dev/null 2>&1; then
        echo "Docker Services:"
        docker-compose ps
        echo ""
    fi
    
    # Check if services are responding
    echo "Service Health Check:"
    
    # Frontend
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo "  Frontend: ✅ Running"
    else
        echo "  Frontend: ❌ Not responding"
    fi
    
    # Backend
    if curl -s http://localhost:7500/actuator/health >/dev/null 2>&1; then
        echo "  Backend: ✅ Running"
    else
        echo "  Backend: ❌ Not responding"
    fi
    
    # Rasa Server
    if curl -s http://localhost:5005/status >/dev/null 2>&1; then
        echo "  Rasa Server: ✅ Running"
    else
        echo "  Rasa Server: ❌ Not responding"
    fi
    
    # Rasa Actions
    if curl -s http://localhost:5055 >/dev/null 2>&1; then
        echo "  Rasa Actions: ✅ Running"
    else
        echo "  Rasa Actions: ❌ Not responding"
    fi
    
    echo ""
    read -p "Press Enter to continue..."
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Frontend dependencies
    print_status "Installing frontend dependencies..."
    cd frontend/dl-creator && npm install && cd ../..
    
    # Backend dependencies
    print_status "Installing backend dependencies..."
    cd backend/dl_creator && ./mvnw dependency:resolve && cd ../..
    
    # Rasa dependencies
    print_status "Installing Rasa dependencies..."
    cd chatbot
    if [ ! -d "rasa_env" ]; then
        python3 -m venv rasa_env
    fi
    source rasa_env/bin/activate && pip install -r requirements.txt
    cd ..
    
    print_success "All dependencies installed successfully!"
    echo ""
    read -p "Press Enter to continue..."
}

# Main menu loop
while true; do
    show_menu
    read -p "Enter your choice: " choice
    
    case $choice in
        1)
            start_docker_prod
            echo ""
            read -p "Press Enter to continue..."
            ;;
        2)
            start_docker_dev
            echo ""
            read -p "Press Enter to continue..."
            ;;
        3)
            start_without_docker
            ;;
        4)
            stop_services
            echo ""
            read -p "Press Enter to continue..."
            ;;
        5)
            view_logs
            ;;
        6)
            check_status
            ;;
        7)
            install_dependencies
            ;;
        8)
            print_status "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please try again."
            sleep 2
            ;;
    esac
done
