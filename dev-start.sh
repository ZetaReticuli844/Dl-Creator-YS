#!/bin/bash

# DL Creator Development Startup Script
# This script starts all services in development mode without Docker

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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to wait for a service to be ready
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=1

    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://$host:$port" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start within expected time"
    return 1
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check for Java
if ! command_exists java; then
    print_error "Java is not installed. Please install Java 11 or higher."
    exit 1
fi

# Check for Node.js
if ! command_exists node; then
    print_error "Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Check for Python
if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check for pip
if ! command_exists pip3; then
    print_error "pip3 is not installed. Please install pip3."
    exit 1
fi

print_success "All prerequisites are satisfied!"

# Check if ports are available
print_status "Checking port availability..."

if port_in_use 3000; then
    print_error "Port 3000 is already in use. Please free up the port."
    exit 1
fi

if port_in_use 7500; then
    print_error "Port 7500 is already in use. Please free up the port."
    exit 1
fi

if port_in_use 5005; then
    print_error "Port 5005 is already in use. Please free up the port."
    exit 1
fi

if port_in_use 5055; then
    print_error "Port 5055 is already in use. Please free up the port."
    exit 1
fi

print_success "All required ports are available!"

# Create logs directory
mkdir -p logs

# Function to start backend
start_backend() {
    print_status "Starting Spring Boot Backend..."
    cd backend/dl_creator
    
    # Check if Maven wrapper exists
    if [ ! -f "./mvnw" ]; then
        print_error "Maven wrapper not found. Please run 'mvn wrapper:wrapper' in the backend directory."
        exit 1
    fi
    
    # Make mvnw executable
    chmod +x ./mvnw
    
    # Start the application
    nohup ./mvnw spring-boot:run > ../../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../../logs/backend.pid
    
    cd ../..
    print_success "Backend started with PID: $BACKEND_PID"
}

# Function to start frontend
start_frontend() {
    print_status "Starting React Frontend..."
    cd frontend/dl-creator
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    # Start the development server
    nohup npm run dev > ../../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../../logs/frontend.pid
    
    cd ../..
    print_success "Frontend started with PID: $FRONTEND_PID"
}

# Function to start Rasa
start_rasa() {
    print_status "Starting Rasa Chatbot..."
    cd chatbot
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "rasa_env" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv rasa_env
    fi
    
    # Activate virtual environment
    source rasa_env/bin/activate
    
    # Install dependencies
    print_status "Installing Rasa dependencies..."
    pip install -r requirements.txt
    
    # Train the model if it doesn't exist
    if [ ! -d "models" ] || [ -z "$(ls -A models)" ]; then
        print_status "Training Rasa model..."
        rasa train
    fi
    
    # Start action server
    print_status "Starting Rasa Action Server..."
    nohup rasa run actions --port 5055 --cors "*" > ../logs/rasa-actions.log 2>&1 &
    RASA_ACTIONS_PID=$!
    echo $RASA_ACTIONS_PID > ../logs/rasa-actions.pid
    
    # Start Rasa server
    print_status "Starting Rasa Server..."
    nohup rasa run --port 5005 --cors "*" --enable-api > ../logs/rasa-server.log 2>&1 &
    RASA_SERVER_PID=$!
    echo $RASA_SERVER_PID > ../logs/rasa-server.pid
    
    cd ..
    print_success "Rasa started with PIDs: Actions=$RASA_ACTIONS_PID, Server=$RASA_SERVER_PID"
}

# Function to cleanup on exit
cleanup() {
    print_status "Shutting down services..."
    
    # Kill processes if PID files exist
    if [ -f "logs/backend.pid" ]; then
        kill $(cat logs/backend.pid) 2>/dev/null || true
        rm logs/backend.pid
    fi
    
    if [ -f "logs/frontend.pid" ]; then
        kill $(cat logs/frontend.pid) 2>/dev/null || true
        rm logs/frontend.pid
    fi
    
    if [ -f "logs/rasa-actions.pid" ]; then
        kill $(cat logs/rasa-actions.pid) 2>/dev/null || true
        rm logs/rasa-actions.pid
    fi
    
    if [ -f "logs/rasa-server.pid" ]; then
        kill $(cat logs/rasa-server.pid) 2>/dev/null || true
        rm logs/rasa-server.pid
    fi
    
    print_success "All services stopped."
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start all services
print_status "Starting DL Creator Development Environment..."

start_backend
sleep 5

start_rasa
sleep 5

start_frontend

# Wait for services to be ready
print_status "Waiting for services to be ready..."

wait_for_service "localhost" 7500 "Backend API" &
wait_for_service "localhost" 5005 "Rasa Server" &
wait_for_service "localhost" 5055 "Rasa Action Server" &
wait_for_service "localhost" 3000 "Frontend" &

# Wait for all background processes
wait

print_success "All services are ready!"
print_status "Application URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:7500"
echo "  H2 Console: http://localhost:7500/h2-console"
echo "  Rasa Server: http://localhost:5005"
echo "  Rasa Action Server: http://localhost:5055"

print_status "Press Ctrl+C to stop all services"

# Keep the script running
while true; do
    sleep 1
done
