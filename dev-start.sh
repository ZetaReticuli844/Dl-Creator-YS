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

# Check for Docker
if ! command_exists docker; then
    print_error "Docker is not installed. Please install Docker."
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

if port_in_use 16686; then
    print_error "Port 16686 is already in use. Please free up the port."
    exit 1
fi

if port_in_use 14250; then
    print_error "Port 14250 is already in use. Please free up the port."
    exit 1
fi

if port_in_use 4317; then
    print_error "Port 4317 is already in use. Please free up the port."
    exit 1
fi

if port_in_use 9090; then
    print_error "Port 9090 is already in use. Please free up the port."
    exit 1
fi

if port_in_use 3001; then
    print_error "Port 3001 is already in use. Please free up the port."
    exit 1
fi

if port_in_use 9042; then
    print_error "Port 9042 is already in use. Please free up the port."
    exit 1
fi

print_success "All required ports are available!"

# Create logs directory
mkdir -p logs

# Create Docker network for monitoring
create_monitoring_network() {
    if ! docker network ls | grep -q "dl-creator-monitoring"; then
        print_status "Creating Docker network for monitoring..."
        docker network create dl-creator-monitoring >/dev/null 2>&1
    fi
}

# Function to start Cassandra
start_cassandra() {
    print_status "Starting Cassandra..."
    
    # Check if Cassandra container exists (running or stopped)
    if docker ps -aq -f name=dl-creator-cassandra | grep -q .; then
        print_warning "Cassandra container already exists, removing it first..."
        docker stop dl-creator-cassandra >/dev/null 2>&1
        docker rm dl-creator-cassandra >/dev/null 2>&1
    fi
    
    # Start Cassandra container
    docker run -d \
        --name dl-creator-cassandra \
        --network dl-creator-monitoring \
        -p 9042:9042 \
        -e CASSANDRA_CLUSTER_NAME=jaeger \
        -e CASSANDRA_DC=dc1 \
        -e CASSANDRA_RACK=rack1 \
        -e CASSANDRA_ENDPOINT_SNITCH=GossipingPropertyFileSnitch \
        cassandra:3.11 > logs/cassandra.log 2>&1
    
    if [ $? -eq 0 ]; then
        print_success "Cassandra started successfully"
        echo "docker ps -q -f name=dl-creator-cassandra" > logs/cassandra.pid
        
        # Wait for Cassandra to be ready
        print_status "Waiting for Cassandra to be ready..."
        sleep 30
        
        # Check if Cassandra is responding
        local attempt=1
        local max_attempts=20
        while [ $attempt -le $max_attempts ]; do
            if docker exec dl-creator-cassandra cqlsh -e "DESCRIBE KEYSPACES;" >/dev/null 2>&1; then
                print_success "Cassandra is ready!"
                break
            fi
            echo -n "."
            sleep 3
            attempt=$((attempt + 1))
        done
        
        if [ $attempt -gt $max_attempts ]; then
            print_error "Cassandra failed to start within expected time"
            exit 1
        fi
        
        # Initialize Jaeger schema
        print_status "Initializing Jaeger schema in Cassandra..."
        docker run --rm --network dl-creator-monitoring \
            -e CQLSH_HOST=dl-creator-cassandra \
            -e CQLSH_PORT=9042 \
            jaegertracing/jaeger-cassandra-schema:latest >/dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            print_success "Jaeger schema initialized successfully"
        else
            print_warning "Schema initialization may have failed, but continuing..."
        fi
    else
        print_error "Failed to start Cassandra"
        exit 1
    fi
}

# Function to start Jaeger
start_jaeger() {
    print_status "Starting Jaeger with Cassandra backend..."
    
    # Check if Jaeger containers exist (running or stopped)
    print_status "Cleaning up any existing Jaeger containers..."
    docker stop dl-creator-jaeger-collector dl-creator-jaeger-query dl-creator-jaeger-agent >/dev/null 2>&1 || true
    docker rm dl-creator-jaeger-collector dl-creator-jaeger-query dl-creator-jaeger-agent >/dev/null 2>&1 || true
    
    # Start Jaeger collector
    docker run -d \
        --name dl-creator-jaeger-collector \
        --network dl-creator-monitoring \
        -p 14250:14250 \
        -p 14268:14268 \
        -p 4317:4317 \
        -p 4318:4318 \
        -e SPAN_STORAGE_TYPE=cassandra \
        -e CASSANDRA_SERVERS=dl-creator-cassandra:9042 \
        -e CASSANDRA_KEYSPACE=jaeger_v1_dc1 \
        -e CASSANDRA_LOCAL_DC=dc1 \
        -e COLLECTOR_OTLP_ENABLED=true \
        jaegertracing/jaeger-collector:latest > logs/jaeger-collector.log 2>&1
    
    if [ $? -ne 0 ]; then
        print_error "Failed to start Jaeger collector"
        exit 1
    fi
    
    # Start Jaeger query
    docker run -d \
        --name dl-creator-jaeger-query \
        --network dl-creator-monitoring \
        -p 16686:16686 \
        -e SPAN_STORAGE_TYPE=cassandra \
        -e CASSANDRA_SERVERS=dl-creator-cassandra:9042 \
        -e CASSANDRA_KEYSPACE=jaeger_v1_dc1 \
        -e CASSANDRA_LOCAL_DC=dc1 \
        jaegertracing/jaeger-query:latest > logs/jaeger-query.log 2>&1
    
    if [ $? -ne 0 ]; then
        print_error "Failed to start Jaeger query"
        exit 1
    fi
    
    # Start Jaeger agent
    docker run -d \
        --name dl-creator-jaeger-agent \
        --network dl-creator-monitoring \
        -p 6831:6831/udp \
        -p 6832:6832/udp \
        -p 5778:5778 \
        -e REPORTER_GRPC_HOST_PORT=dl-creator-jaeger-collector:14250 \
        jaegertracing/jaeger-agent:latest > logs/jaeger-agent.log 2>&1
    
    if [ $? -eq 0 ]; then
        print_success "Jaeger started successfully with Cassandra backend"
        echo "docker ps -q -f name=dl-creator-jaeger-collector" > logs/jaeger.pid
    else
        print_error "Failed to start Jaeger agent"
        exit 1
    fi
}

# Function to start Prometheus
start_prometheus() {
    print_status "Starting Prometheus..."
    
    # Check if Prometheus container exists (running or stopped)
    if docker ps -aq -f name=dl-creator-prometheus | grep -q .; then
        print_warning "Prometheus container already exists, removing it first..."
        docker stop dl-creator-prometheus >/dev/null 2>&1
        docker rm dl-creator-prometheus >/dev/null 2>&1
    fi
    
    # Start Prometheus container
    docker run -d \
        --name dl-creator-prometheus \
        --network dl-creator-monitoring \
        -p 9090:9090 \
        --add-host=host.docker.internal:host-gateway \
        -v "$(pwd)/backend/dl_creator/prometheus.yml:/etc/prometheus/prometheus.yml" \
        prom/prometheus:latest \
        --config.file=/etc/prometheus/prometheus.yml \
        --storage.tsdb.path=/prometheus \
        --web.console.libraries=/etc/prometheus/console_libraries \
        --web.console.templates=/etc/prometheus/consoles \
        --storage.tsdb.retention.time=15d \
        --web.enable-lifecycle > logs/prometheus.log 2>&1
    
    if [ $? -eq 0 ]; then
        print_success "Prometheus started successfully"
        echo "docker ps -q -f name=dl-creator-prometheus" > logs/prometheus.pid
    else
        print_error "Failed to start Prometheus"
        exit 1
    fi
}

# Function to start Grafana
start_grafana() {
    print_status "Starting Grafana..."
    
    # Check if Grafana container exists (running or stopped)
    if docker ps -aq -f name=dl-creator-grafana | grep -q .; then
        print_warning "Grafana container already exists, removing it first..."
        docker stop dl-creator-grafana >/dev/null 2>&1
        docker rm dl-creator-grafana >/dev/null 2>&1
    fi
    
    # Start Grafana container
    docker run -d \
        --name dl-creator-grafana \
        --network dl-creator-monitoring \
        -p 3001:3000 \
        -e GF_SECURITY_ADMIN_USER=admin \
        -e GF_SECURITY_ADMIN_PASSWORD=admin123 \
        -e GF_USERS_ALLOW_SIGN_UP=false \
        -v "$(pwd)/backend/dl_creator/grafana/provisioning:/etc/grafana/provisioning" \
        -v "$(pwd)/backend/dl_creator/grafana/dashboards:/var/lib/grafana/dashboards" \
        grafana/grafana:latest > logs/grafana.log 2>&1
    
    if [ $? -eq 0 ]; then
        print_success "Grafana started successfully"
        echo "docker ps -q -f name=dl-creator-grafana" > logs/grafana.pid
    else
        print_error "Failed to start Grafana"
        exit 1
    fi
}

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
    
    # Download OpenTelemetry Java agent if it doesn't exist
    if [ ! -f "opentelemetry-javaagent.jar" ]; then
        print_status "Downloading OpenTelemetry Java agent..."
        curl -L -o opentelemetry-javaagent.jar 'https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar'
    fi
    
    # Build the JAR file
    print_status "Building backend JAR file..."
    ./mvnw clean package -DskipTests
    
    if [ $? -ne 0 ]; then
        print_error "Failed to build backend JAR file"
        exit 1
    fi
    
    # Find the JAR file (it should be in target directory)
    JAR_FILE=$(find target -name "*.jar" -not -name "*-sources.jar" | head -1)
    
    if [ -z "$JAR_FILE" ]; then
        print_error "JAR file not found in target directory"
        exit 1
    fi
    
    print_status "Found JAR file: $JAR_FILE"
    
    # Start the application with OpenTelemetry agent
    nohup java -javaagent:opentelemetry-javaagent.jar \
        -Dotel.service.name=dl-creator-backend \
        -Dotel.traces.exporter=otlp \
        -Dotel.metrics.exporter=none \
        -Dotel.logs.exporter=none \
        -Dotel.exporter.otlp.endpoint=http://localhost:4317 \
        -Dotel.exporter.otlp.protocol=grpc \
        -Dotel.traces.sampler=always_on \
        -jar "$JAR_FILE" > ../../logs/backend.log 2>&1 &
    
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
    export API_BASE_URL=http://localhost:7500
    nohup rasa run actions --port 5055 --cors "*"  > ../logs/rasa-actions.log 2>&1 &
    RASA_ACTIONS_PID=$!
    echo $RASA_ACTIONS_PID > ../logs/rasa-actions.pid
    
    # Start Rasa server
    print_status "Starting Rasa Server..."
    export API_BASE_URL=http://localhost:7500
    nohup rasa run --port 5005 --cors "*"   > ../logs/rasa-server.log 2>&1 &
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
    
    # Stop Docker containers
    if [ -f "logs/jaeger.pid" ]; then
        docker stop dl-creator-jaeger-collector >/dev/null 2>&1 || true
        docker rm dl-creator-jaeger-collector >/dev/null 2>&1 || true
        docker stop dl-creator-jaeger-query >/dev/null 2>&1 || true
        docker rm dl-creator-jaeger-query >/dev/null 2>&1 || true
        docker stop dl-creator-jaeger-agent >/dev/null 2>&1 || true
        docker rm dl-creator-jaeger-agent >/dev/null 2>&1 || true
        rm logs/jaeger.pid
    fi
    
    if [ -f "logs/cassandra.pid" ]; then
        docker stop dl-creator-cassandra >/dev/null 2>&1 || true
        docker rm dl-creator-cassandra >/dev/null 2>&1 || true
        rm logs/cassandra.pid
    fi
    
    if [ -f "logs/prometheus.pid" ]; then
        docker stop dl-creator-prometheus >/dev/null 2>&1 || true
        docker rm dl-creator-prometheus >/dev/null 2>&1 || true
        rm logs/prometheus.pid
    fi
    
    if [ -f "logs/grafana.pid" ]; then
        docker stop dl-creator-grafana >/dev/null 2>&1 || true
        docker rm dl-creator-grafana >/dev/null 2>&1 || true
        rm logs/grafana.pid
    fi
    
    # Clean up Docker network
    docker network rm dl-creator-monitoring >/dev/null 2>&1 || true
    
    print_success "All services stopped."
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start all services
print_status "Starting DL Creator Development Environment..."

create_monitoring_network

start_cassandra
sleep 10

start_jaeger
sleep 5

start_prometheus
sleep 5

start_grafana
sleep 10

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
wait_for_service "localhost" 9090 "Prometheus" &
wait_for_service "localhost" 3001 "Grafana" &

# Wait for all background processes
wait

print_success "All services are ready!"
print_status "Application URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:7500"
echo "  H2 Console: http://localhost:7500/h2-console"
echo "  Rasa Server: http://localhost:5005"
echo "  Rasa Action Server: http://localhost:5055"
echo "  Jaeger UI: http://localhost:16686"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana: http://localhost:3001 (admin/admin123)"

print_status "Press Ctrl+C to stop all services"

# Keep the script running
while true; do
    sleep 1
done
