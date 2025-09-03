# Cassandra-Jaeger Integration Guide

This document explains how to use Cassandra as the storage backend for Jaeger tracing in the DL Creator application.

## Overview

The DL Creator application has been configured to use Apache Cassandra as the persistent storage backend for Jaeger traces instead of the default in-memory storage. This provides:

- **Persistent storage**: Traces survive container restarts
- **Scalability**: Better performance for high-volume tracing
- **Production readiness**: Suitable for production environments
- **Data retention**: Configurable trace retention policies

## Architecture

```
Application → OpenTelemetry → Jaeger Collector → Cassandra
                                    ↓
                            Jaeger Query ← Cassandra
                                    ↓
                              Jaeger UI
```

### Components

1. **Cassandra Database**: Stores trace data persistently
2. **Jaeger Collector**: Receives traces via OTLP and stores them in Cassandra
3. **Jaeger Query**: Retrieves traces from Cassandra for the UI
4. **Jaeger Agent**: (Optional) Local agent for trace forwarding
5. **Jaeger UI**: Web interface to view and analyze traces

## Configuration

### Environment Variables

The following environment variables configure the Cassandra-Jaeger integration:

```bash
# Cassandra Configuration
CASSANDRA_SERVERS=localhost:9042
CASSANDRA_KEYSPACE=jaeger_v1_dc1
CASSANDRA_LOCAL_DC=dc1

# OpenTelemetry Configuration
OTEL_SERVICE_NAME=dl-creator-backend
OTEL_TRACES_EXPORTER=otlp
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_EXPORTER_OTLP_PROTOCOL=grpc
OTEL_TRACES_SAMPLER=always_on
```

### Port Configuration

| Service | Port | Description |
|---------|------|-------------|
| Cassandra | 9042 | CQL native transport |
| Jaeger UI | 16686 | Web interface |
| Jaeger Collector (gRPC) | 14250 | Jaeger native gRPC |
| Jaeger Collector (HTTP) | 14268 | Jaeger native HTTP |
| OTLP gRPC | 4317 | OpenTelemetry gRPC receiver |
| OTLP HTTP | 4318 | OpenTelemetry HTTP receiver |
| Jaeger Agent (UDP) | 6831/6832 | Legacy UDP receivers |
| Jaeger Agent (HTTP) | 5778 | Agent configuration |

## Usage

### Starting with Development Script

The `dev-start.sh` script automatically starts all components in the correct order:

```bash
./dev-start.sh
```

This will:
1. Start Cassandra and wait for it to be ready
2. Initialize Jaeger schema in Cassandra
3. Start Jaeger components (collector, query, agent)
4. Start other application services

### Starting with Docker Compose

#### Development Mode
```bash
docker-compose -f docker-compose.dev.yml up -d
```

#### Production Mode
```bash
docker-compose up -d
```

## Verification

### 1. Test the Integration

Use the provided test script to verify everything is working:

```bash
./test-cassandra-jaeger.sh
```

### 2. Manual Verification

#### Check Cassandra Health
```bash
docker exec dl-creator-cassandra cqlsh -e "DESCRIBE KEYSPACES;"
```

#### Check Jaeger Keyspace
```bash
docker exec dl-creator-cassandra cqlsh -e "DESCRIBE KEYSPACE jaeger_v1_dc1;"
```

#### View Traces in Cassandra
```bash
docker exec dl-creator-cassandra cqlsh -e "SELECT COUNT(*) FROM jaeger_v1_dc1.traces;"
```

### 3. Access Jaeger UI

Open http://localhost:16686 in your browser to view the Jaeger UI.

## Troubleshooting

### Common Issues

#### 1. Cassandra Not Ready
```
Error: Cassandra failed to start within expected time
```

**Solution**: Cassandra can take 30-60 seconds to fully start. Wait longer or check logs:
```bash
docker logs dl-creator-cassandra
```

#### 2. Schema Initialization Failed
```
Warning: Schema initialization may have failed
```

**Solution**: Manually initialize the schema:
```bash
docker run --rm --network dl-creator-monitoring \
    jaegertracing/jaeger-cassandra-schema:latest \
    dl-creator-cassandra
```

#### 3. No Traces Visible
- Ensure your application is generating traces
- Check that the backend is sending traces to the correct endpoint (localhost:4317)
- Verify the OpenTelemetry configuration in your application

#### 4. Connection Refused
```
Error: Connection refused to Cassandra
```

**Solution**: 
- Check if Cassandra container is running: `docker ps | grep cassandra`
- Verify network connectivity: `docker network ls | grep dl-creator`
- Check Cassandra logs: `docker logs dl-creator-cassandra`

### Debug Commands

#### View Jaeger Collector Logs
```bash
docker logs dl-creator-jaeger-collector
```

#### View Jaeger Query Logs
```bash
docker logs dl-creator-jaeger-query
```

#### Check Cassandra Tables
```bash
docker exec dl-creator-cassandra cqlsh -e "USE jaeger_v1_dc1; DESCRIBE TABLES;"
```

#### Monitor Cassandra Performance
```bash
docker exec dl-creator-cassandra nodetool status
```

## Data Management

### Backup Traces
```bash
# Create a backup of the Cassandra data
docker exec dl-creator-cassandra nodetool snapshot jaeger_v1_dc1
```

### Clean Old Traces
```bash
# Delete traces older than 7 days (example)
docker exec dl-creator-cassandra cqlsh -e "
DELETE FROM jaeger_v1_dc1.traces 
WHERE ts < $(date -d '7 days ago' +%s%6N);"
```

### View Trace Statistics
```bash
docker exec dl-creator-cassandra cqlsh -e "
SELECT operation_name, COUNT(*) as trace_count 
FROM jaeger_v1_dc1.traces 
GROUP BY operation_name 
ALLOW FILTERING;"
```

## Performance Tuning

### Cassandra Configuration

For production environments, consider tuning these Cassandra parameters:

- `MAX_HEAP_SIZE`: Adjust based on available memory
- `HEAP_NEWSIZE`: Set to 1/4 of MAX_HEAP_SIZE
- `CASSANDRA_NUM_TOKENS`: Default is 256, consider reducing for better performance
- `CASSANDRA_CONCURRENT_READS/WRITES`: Adjust based on workload

### Jaeger Configuration

- `CASSANDRA_CONNECTION_PER_HOST`: Increase for higher throughput
- `CASSANDRA_MAX_RETRY_ATTEMPTS`: Adjust retry behavior
- `CASSANDRA_TIMEOUT`: Set appropriate timeouts

## Security Considerations

### Cassandra Security
```bash
# Enable authentication (production)
CASSANDRA_AUTHENTICATOR=PasswordAuthenticator
CASSANDRA_AUTHORIZER=CassandraAuthorizer

# Use SSL/TLS (production)
CASSANDRA_SSL_ENABLED=true
```

### Network Security
- Use Docker networks to isolate components
- Configure firewall rules for production deployments
- Consider using Cassandra user authentication

## Monitoring

### Metrics Collection

Jaeger exposes metrics that can be collected by Prometheus:
- Collector metrics: http://localhost:14269/metrics
- Query metrics: http://localhost:16687/metrics

### Cassandra Monitoring

Monitor Cassandra performance using:
- Built-in JMX metrics
- External tools like DataStax OpsCenter
- Custom monitoring solutions

## Migration from In-Memory Storage

If migrating from the previous in-memory Jaeger setup:

1. Stop the old Jaeger all-in-one container
2. Start the new Cassandra-based setup
3. Note that previous traces will be lost (they were in-memory)
4. Update any scripts or configurations that reference the old container names

## Conclusion

This Cassandra-Jaeger integration provides a robust, scalable tracing solution for the DL Creator application. The persistent storage ensures trace data survives container restarts and provides better performance for production workloads.

For additional support or questions, refer to:
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Cassandra Documentation](https://cassandra.apache.org/doc/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
