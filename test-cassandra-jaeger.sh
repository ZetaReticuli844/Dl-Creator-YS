#!/bin/bash

# Test script for Cassandra-Jaeger integration
# This script validates that Cassandra and Jaeger are properly connected

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

# Check if Docker is running
if ! docker ps >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Testing Cassandra-Jaeger Integration..."

# Test 1: Check if Cassandra container is running
print_status "Checking Cassandra container..."
if docker ps | grep -q "dl-creator-cassandra"; then
    print_success "Cassandra container is running"
else
    print_error "Cassandra container is not running"
    exit 1
fi

# Test 2: Check if Cassandra is accepting connections
print_status "Testing Cassandra connectivity..."
if docker exec dl-creator-cassandra cqlsh -e "DESCRIBE KEYSPACES;" >/dev/null 2>&1; then
    print_success "Cassandra is accepting connections"
else
    print_error "Cassandra is not accepting connections"
    exit 1
fi

# Test 3: Check if Jaeger keyspace exists
print_status "Checking Jaeger keyspace..."
if docker exec dl-creator-cassandra cqlsh -e "DESCRIBE KEYSPACE jaeger_v1_dc1;" >/dev/null 2>&1; then
    print_success "Jaeger keyspace exists in Cassandra"
else
    print_warning "Jaeger keyspace does not exist - may need schema initialization"
fi

# Test 4: Check if Jaeger collector is running
print_status "Checking Jaeger collector..."
if docker ps | grep -q "dl-creator-jaeger-collector"; then
    print_success "Jaeger collector is running"
else
    print_error "Jaeger collector is not running"
    exit 1
fi

# Test 5: Check if Jaeger query service is running
print_status "Checking Jaeger query service..."
if docker ps | grep -q "dl-creator-jaeger-query"; then
    print_success "Jaeger query service is running"
else
    print_error "Jaeger query service is not running"
    exit 1
fi

# Test 6: Test OTLP endpoint
print_status "Testing OTLP endpoint connectivity..."
if curl -s --max-time 5 --connect-timeout 5 http://localhost:4317 >/dev/null 2>&1; then
    print_success "OTLP endpoint is accessible"
else
    print_warning "OTLP endpoint may not be fully ready (this is expected for gRPC)"
fi

# Test 7: Test Jaeger UI
print_status "Testing Jaeger UI..."
if curl -s --max-time 5 http://localhost:16686 | grep -q "Jaeger UI" >/dev/null 2>&1; then
    print_success "Jaeger UI is accessible"
else
    print_error "Jaeger UI is not accessible"
    exit 1
fi

# Test 8: Check for any traces in Cassandra
print_status "Checking for traces in Cassandra..."
TRACE_COUNT=$(docker exec dl-creator-cassandra cqlsh -e "SELECT COUNT(*) FROM jaeger_v1_dc1.traces;" 2>/dev/null | grep -E '^\s*[0-9]+\s*$' || echo "0")
if [ "$TRACE_COUNT" -gt 0 ]; then
    print_success "Found $TRACE_COUNT traces in Cassandra"
else
    print_warning "No traces found in Cassandra yet (this is normal for a fresh setup)"
fi

print_success "All tests completed! Cassandra-Jaeger integration appears to be working."
print_status "You can access Jaeger UI at: http://localhost:16686"
print_status "To generate test traces, start your backend application and make some API calls."
