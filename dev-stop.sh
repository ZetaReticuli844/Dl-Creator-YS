#!/bin/bash

# DL Creator Development Stop Script
# This script stops all services started by dev-start.sh

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

print_status "Stopping DL Creator Development Environment..."

# Function to kill process by PID file
kill_process() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            print_status "Stopping $service_name (PID: $pid)..."
            kill "$pid"
            sleep 2
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                print_warning "Force killing $service_name..."
                kill -9 "$pid"
            fi
            
            print_success "$service_name stopped"
        else
            print_warning "$service_name was not running"
        fi
        rm -f "$pid_file"
    else
        print_warning "PID file for $service_name not found"
    fi
}

# Kill all services
kill_process "logs/backend.pid" "Backend"
kill_process "logs/frontend.pid" "Frontend"
kill_process "logs/rasa-actions.pid" "Rasa Action Server"
kill_process "logs/rasa-server.pid" "Rasa Server"

# Kill any remaining processes on our ports
print_status "Cleaning up any remaining processes on our ports..."

# Kill processes on port 3000 (Frontend)
pkill -f "vite\|npm.*dev" 2>/dev/null || true

# Kill processes on port 7500 (Backend)
pkill -f "spring-boot:run\|java.*dl_creator" 2>/dev/null || true

# Kill processes on port 5005 (Rasa Server)
pkill -f "rasa.*run.*5005" 2>/dev/null || true

# Kill processes on port 5055 (Rasa Actions)
pkill -f "rasa.*actions.*5055" 2>/dev/null || true

print_success "All services stopped successfully!"

# Optional: Clean up logs
if [ "$1" = "--clean-logs" ]; then
    print_status "Cleaning up log files..."
    rm -rf logs/*
    print_success "Log files cleaned up"
fi

print_status "Development environment stopped."
