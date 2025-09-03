#!/bin/bash

# Query Traces Script - Easy Cassandra trace inspection
# Usage: ./query-traces.sh [option]

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

# Check if Cassandra is running
if ! docker ps | grep -q "dl-creator-cassandra"; then
    print_error "Cassandra container is not running. Start it first with:"
    echo "docker run -d --name dl-creator-cassandra --network dl-creator-monitoring -p 9042:9042 cassandra:3.11"
    exit 1
fi

# Function to execute CQL commands
execute_cql() {
    docker exec -it dl-creator-cassandra cqlsh -e "$1"
}

show_help() {
    echo "Usage: $0 [option]"
    echo ""
    echo "Options:"
    echo "  stats          - Show trace statistics"
    echo "  services       - List all services"
    echo "  operations     - List all operations by service"
    echo "  recent         - Show 10 most recent traces"
    echo "  traces [limit] - Show traces (default limit: 10)"
    echo "  trace <id>     - Show details for specific trace ID"
    echo "  search <term>  - Search for traces containing term"
    echo "  cleanup        - Show cleanup commands"
    echo "  interactive    - Start interactive CQL shell"
    echo "  help           - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 stats"
    echo "  $0 traces 20"
    echo "  $0 trace 0xabe700d7273054c3e92cd52667a38188"
    echo "  $0 search 'auth/login'"
}

show_stats() {
    print_status "📊 Trace Statistics"
    echo ""
    
    print_status "Total Spans:"
    execute_cql "SELECT COUNT(*) FROM jaeger_v1_dc1.traces;"
    
    echo ""
    print_status "Services:"
    execute_cql "SELECT COUNT(*) as service_count FROM jaeger_v1_dc1.service_names;"
    
    echo ""
    print_status "Recent Traces (sample):"
    execute_cql "SELECT trace_id FROM jaeger_v1_dc1.traces LIMIT 3;"
}

show_services() {
    print_status "🔧 Services with Traces"
    echo ""
    execute_cql "SELECT * FROM jaeger_v1_dc1.service_names;"
}

show_operations() {
    print_status "⚙️ Operations by Service"
    echo ""
    execute_cql "SELECT service_name, span_kind, operation_name FROM jaeger_v1_dc1.operation_names_v2 ORDER BY service_name, span_kind, operation_name;"
}

show_recent() {
    print_status "🕒 Recent Traces (Last 10)"
    echo ""
    execute_cql "SELECT trace_id, operation_name, start_time, duration, process.service_name FROM jaeger_v1_dc1.traces LIMIT 10;"
}

show_traces() {
    local limit=${1:-10}
    print_status "📋 Traces (Limit: $limit)"
    echo ""
    execute_cql "SELECT trace_id, span_id, operation_name, start_time, duration, process.service_name FROM jaeger_v1_dc1.traces LIMIT $limit;"
}

show_trace_details() {
    local trace_id=$1
    if [ -z "$trace_id" ]; then
        print_error "Please provide a trace ID"
        echo "Example: $0 trace 0xabe700d7273054c3e92cd52667a38188"
        exit 1
    fi
    
    print_status "🔍 Trace Details for: $trace_id"
    echo ""
    execute_cql "SELECT trace_id, span_id, operation_name, start_time, duration, process.service_name, tags FROM jaeger_v1_dc1.traces WHERE trace_id = $trace_id;"
}

search_traces() {
    local search_term=$1
    if [ -z "$search_term" ]; then
        print_error "Please provide a search term"
        echo "Example: $0 search 'auth/login'"
        exit 1
    fi
    
    print_status "🔎 Searching for traces containing: $search_term"
    echo ""
    execute_cql "SELECT trace_id, operation_name, start_time, process.service_name FROM jaeger_v1_dc1.traces WHERE operation_name LIKE '%$search_term%' ALLOW FILTERING LIMIT 20;"
}

show_cleanup() {
    print_status "🧹 Cleanup Commands"
    echo ""
    echo "To delete traces older than X days:"
    echo "docker exec -it dl-creator-cassandra cqlsh -e \"DELETE FROM jaeger_v1_dc1.traces WHERE start_time < \$(date -d '7 days ago' +%s%6N);\""
    echo ""
    echo "To delete all traces:"
    echo "docker exec -it dl-creator-cassandra cqlsh -e \"TRUNCATE jaeger_v1_dc1.traces;\""
    echo ""
    echo "To delete specific service traces:"
    echo "docker exec -it dl-creator-cassandra cqlsh -e \"DELETE FROM jaeger_v1_dc1.traces WHERE process.service_name = 'service-name' IF EXISTS;\""
    
    print_warning "⚠️  Use cleanup commands carefully - data cannot be recovered!"
}

start_interactive() {
    print_status "🔧 Starting Interactive CQL Shell"
    echo "You can now run CQL commands directly. Type 'exit' to quit."
    echo "Useful commands:"
    echo "  USE jaeger_v1_dc1;"
    echo "  DESCRIBE TABLES;"
    echo "  SELECT COUNT(*) FROM traces;"
    echo ""
    docker exec -it dl-creator-cassandra cqlsh
}

# Main logic
case "${1:-help}" in
    "stats")
        show_stats
        ;;
    "services")
        show_services
        ;;
    "operations")
        show_operations
        ;;
    "recent")
        show_recent
        ;;
    "traces")
        show_traces "$2"
        ;;
    "trace")
        show_trace_details "$2"
        ;;
    "search")
        search_traces "$2"
        ;;
    "cleanup")
        show_cleanup
        ;;
    "interactive")
        start_interactive
        ;;
    "help"|*)
        show_help
        ;;
esac
