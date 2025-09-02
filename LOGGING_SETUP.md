# DL Creator Logging Setup with Loki and Promtail

This document describes the logging infrastructure setup for the DL Creator application using Grafana Loki and Promtail.

## Overview

The logging setup includes:
- **Loki**: Log aggregation system that stores and indexes logs
- **Promtail**: Log shipper that collects logs and sends them to Loki
- **Grafana**: Visualization platform with pre-configured Loki datasource and dashboards
- **JSON Logging**: Structured logging in Spring Boot for better log parsing

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Spring Boot   │    │     Rasa        │    │    Frontend     │
│    Backend      │    │    Server       │    │   (React)       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Log Files                                │
│  data/backend-logs/backend.log                                 │
│  logs/rasa-server.log                                          │
│  logs/frontend.log                                             │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Promtail                                 │
│              (Log Shipper)                                      │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Loki                                    │
│              (Log Aggregation)                                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Grafana                                   │
│              (Log Visualization)                                │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Loki Configuration (`loki-config.yml`)

Loki is configured with:
- Single instance setup for development
- File system storage
- 24-hour retention period
- No authentication (development only)

### 2. Promtail Configuration (`promtail-config.yml`)

Promtail is configured to scrape logs from:
- **Backend**: `data/backend-logs/*.log` (JSON format)
- **Rasa Server**: `logs/rasa-server.log`
- **Frontend**: `logs/frontend.log`

Each log source has specific parsing rules for optimal log processing.

### 3. Spring Boot Logging

The Spring Boot application is configured with:
- **JSON Logging**: Structured logs using Logstash Logback Encoder
- **Log Rotation**: 10MB max file size, 30 days retention
- **Multiple Appenders**: Console and file appenders
- **Profile-based Configuration**: Different settings for dev/prod

### 4. Grafana Integration

Grafana is pre-configured with:
- **Loki Datasource**: Automatically configured
- **Logs Dashboard**: Pre-built dashboard for log visualization
- **Trace Correlation**: Links between logs and traces

## Usage

### Starting the Logging Stack

1. **Using Docker Compose (Recommended)**:
   ```bash
   # Start all services including Loki and Promtail
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **Using Development Script**:
   ```bash
   # Start all services including logging
   ./dev-start.sh
   ```

### Accessing Logs

1. **Grafana UI**: http://localhost:3001 (admin/admin123)
   - Go to "Explore" → Select "Loki" datasource
   - Use LogQL queries to search logs

2. **Loki API**: http://localhost:3100
   - Direct API access for log queries
   - Useful for debugging and automation

### LogQL Queries

Common queries for log analysis:

```logql
# All backend logs
{job="dl-creator-backend"}

# Backend logs with ERROR level
{job="dl-creator-backend"} |= "ERROR"

# Backend logs from specific logger
{job="dl-creator-backend"} | json | logger="com.dlyog.dl_creator.service.DrivingLicenseService"

# Logs with specific message pattern
{job="dl-creator-backend"} |~ "User.*created"

# Logs from last 5 minutes
{job="dl-creator-backend"} |= "INFO" [5m]

# Rate of log entries per minute
rate({job="dl-creator-backend"}[1m])
```

### Testing the Setup

Run the test script to verify everything is working:

```bash
./test-logging.sh
```

This script will:
- Check if Loki and Grafana are running
- Test Loki API endpoints
- Verify log ingestion
- Check Grafana datasource configuration

## Configuration Files

### Key Files

- `loki-config.yml`: Loki server configuration
- `promtail-config.yml`: Promtail log shipper configuration
- `backend/dl_creator/src/main/resources/logback-spring.xml`: Spring Boot logging configuration
- `backend/dl_creator/grafana/provisioning/datasources/loki.yml`: Grafana Loki datasource
- `backend/dl_creator/grafana/dashboards/logs-dashboard.json`: Pre-built logs dashboard

### Docker Compose Services

- `loki-dev`: Loki log aggregation service
- `promtail-dev`: Promtail log shipper
- `grafana`: Grafana visualization (existing)

## Troubleshooting

### Common Issues

1. **Loki not starting**:
   - Check if port 3100 is available
   - Verify loki-config.yml syntax
   - Check Docker logs: `docker logs dl-creator-loki`

2. **Promtail not collecting logs**:
   - Verify log file paths in promtail-config.yml
   - Check if log files exist and are readable
   - Check Docker logs: `docker logs dl-creator-promtail`

3. **No logs in Grafana**:
   - Verify Loki datasource is configured
   - Check if Promtail is sending logs to Loki
   - Test Loki API directly: `curl http://localhost:3100/loki/api/v1/labels`

4. **JSON parsing errors**:
   - Verify Spring Boot is outputting valid JSON
   - Check logback-spring.xml configuration
   - Ensure logstash-logback-encoder dependency is included

### Debugging Commands

```bash
# Check Loki status
curl http://localhost:3100/ready

# List available labels
curl http://localhost:3100/loki/api/v1/labels

# Query logs
curl "http://localhost:3100/loki/api/v1/query?query={job=\"dl-creator-backend\"}"

# Check Promtail targets
curl http://localhost:9080/targets

# View container logs
docker logs dl-creator-loki
docker logs dl-creator-promtail
```

## Performance Considerations

### Development Setup
- Single Loki instance (not suitable for production)
- File system storage (limited scalability)
- No authentication (security risk in production)

### Production Recommendations
- Use Loki in distributed mode
- Configure object storage (S3, GCS, etc.)
- Enable authentication and TLS
- Set up proper retention policies
- Use multiple Promtail instances for high availability

## Monitoring

The logging setup integrates with the existing monitoring stack:
- **Prometheus**: Metrics from Loki and Promtail
- **Grafana**: Unified view of logs, metrics, and traces
- **Jaeger**: Distributed tracing with log correlation

## Next Steps

1. **Log Analysis**: Use Grafana to analyze application behavior
2. **Alerting**: Set up alerts based on log patterns
3. **Dashboards**: Create custom dashboards for specific use cases
4. **Retention**: Configure appropriate log retention policies
5. **Security**: Implement authentication and access controls for production

## Resources

- [Loki Documentation](https://grafana.com/docs/loki/)
- [Promtail Documentation](https://grafana.com/docs/loki/latest/clients/promtail/)
- [LogQL Reference](https://grafana.com/docs/loki/latest/logql/)
- [Grafana Logs Documentation](https://grafana.com/docs/grafana/latest/explore/logs/)
