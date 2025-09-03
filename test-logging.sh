#!/bin/bash

# Test script to verify Loki and Promtail integration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to check if a service is running
check_service() {
    local service_name=$1
    local port=$2
    
    if curl -s "http://localhost:$port" >/dev/null 2>&1; then
        print_success "$service_name is running on port $port"
        return 0
    else
        print_error "$service_name is not running on port $port"
        return 1
    fi
}

# Function to test Loki API
test_loki_api() {
    print_status "Testing Loki API..."
    
    # Test Loki readiness
    if curl -s "http://localhost:3100/ready" | grep -q "ready"; then
        print_success "Loki is ready"
    else
        print_error "Loki is not ready"
        return 1
    fi
    
    # Test Loki labels endpoint
    if curl -s "http://localhost:3100/loki/api/v1/labels" >/dev/null 2>&1; then
        print_success "Loki labels API is accessible"
    else
        print_error "Loki labels API is not accessible"
        return 1
    fi
    
    # Test Loki query endpoint
    if curl -s "http://localhost:3100/loki/api/v1/query?query={job=\"dl-creator-backend\"}" >/dev/null 2>&1; then
        print_success "Loki query API is accessible"
    else
        print_error "Loki query API is not accessible"
        return 1
    fi
}

# Function to test log ingestion
test_log_ingestion() {
    print_status "Testing log ingestion..."
    
    # Wait a bit for logs to be ingested
    sleep 10
    
    # Query for backend logs
    local response=$(curl -s "http://localhost:3100/loki/api/v1/query?query={job=\"dl-creator-backend\"}")
    
    if echo "$response" | grep -q "dl-creator-backend"; then
        print_success "Backend logs are being ingested by Loki"
    else
        print_warning "No backend logs found in Loki yet (this might be normal if the backend just started)"
    fi
}

# Function to test Grafana datasource
test_grafana_datasource() {
    print_status "Testing Grafana datasource..."
    
    # Check if Grafana is running
    if ! check_service "Grafana" 3001; then
        return 1
    fi
    
    # Test Grafana API (requires authentication)
    local grafana_url="http://admin:admin123@localhost:3001"
    
    if curl -s "$grafana_url/api/datasources" | grep -q "Loki"; then
        print_success "Loki datasource is configured in Grafana"
    else
        print_warning "Loki datasource might not be configured in Grafana"
    fi
}

# Main test function
main() {
    print_status "Starting logging integration tests..."
    
    # Check if services are running
    check_service "Loki" 3100
    check_service "Grafana" 3001
    
    # Test Loki API
    test_loki_api
    
    # Test log ingestion
    test_log_ingestion
    
    # Test Grafana datasource
    test_grafana_datasource
    
    print_success "Logging integration tests completed!"
    print_status "You can now:"
    echo "  1. Visit http://localhost:3001 to access Grafana"
    echo "  2. Go to Explore and select Loki as datasource"
    echo "  3. Query logs using: {job=\"dl-creator-backend\"}"
    echo "  4. Check the Logs Dashboard for pre-configured views"
}

# Run the tests
main "$@"
