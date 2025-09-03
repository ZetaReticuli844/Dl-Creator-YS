# DL Creator Monitoring Stack

This document describes the monitoring setup for the DL Creator application, which includes Prometheus for metrics collection and Grafana for visualization.

## Components

### Prometheus
- **Purpose**: Metrics collection and storage
- **Port**: 9090
- **URL**: http://localhost:9090
- **Configuration**: `prometheus.yml`

### Grafana
- **Purpose**: Metrics visualization and dashboards
- **Port**: 3001
- **URL**: http://localhost:3001
- **Default Credentials**: admin/admin123
- **Configuration**: `grafana/` directory

## Metrics Collected

The Spring Boot application exposes the following metrics through the `/actuator/prometheus` endpoint:

### System Metrics
- CPU usage (system and process)
- Memory usage (JVM heap and non-heap)
- Thread count (live and daemon)
- Garbage collection statistics

### Application Metrics
- HTTP request rates and response times
- Custom business metrics (if added)
- Database connection pool metrics
- JVM metrics

## Dashboards

### Spring Boot Application Dashboard
A comprehensive dashboard that includes:
- CPU Usage monitoring
- JVM Memory usage
- HTTP request rates
- Response time percentiles (50th, 95th, 99th)
- Thread monitoring
- Garbage collection metrics

## Getting Started

1. **Start the monitoring stack**: The `dev-start.sh` script automatically starts Prometheus and Grafana
2. **Access Grafana**: Navigate to http://localhost:3001 and login with admin/admin123
3. **View dashboards**: The Spring Boot dashboard is automatically provisioned
4. **Explore metrics**: Use the Grafana explore feature to query Prometheus directly

## Configuration Files

```
backend/dl_creator/
├── prometheus.yml                          # Prometheus configuration
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── prometheus.yml             # Grafana datasource config
│   │   └── dashboards/
│   │       └── dashboard.yml              # Dashboard provisioning config
│   └── dashboards/
│       └── spring-boot-dashboard.json     # Pre-built Spring Boot dashboard
```

## Troubleshooting

### Prometheus not collecting metrics
- Verify the Spring Boot application is running on port 7500
- Check that `/actuator/prometheus` endpoint is accessible
- Review prometheus.yml configuration

### Grafana dashboard not showing data
- Ensure Prometheus datasource is configured correctly
- Verify Prometheus is collecting metrics from the application
- Check that the dashboard queries match the available metrics

### Container startup issues
- Check Docker is running
- Verify ports 9090 and 3001 are not in use
- Review container logs in the `logs/` directory

## Adding Custom Metrics

To add custom metrics to your Spring Boot application:

1. Add Micrometer dependencies to your `pom.xml`
2. Use `@Timed`, `@Counted`, or inject `MeterRegistry` for custom metrics
3. Metrics will automatically be available in Prometheus and Grafana

Example:
```java
@RestController
public class MyController {
    
    @Timed(name = "license.creation.time", description = "Time taken to create license")
    @PostMapping("/api/licenses")
    public ResponseEntity<?> createLicense(@RequestBody LicenseRequest request) {
        // Implementation
    }
}
```

## Security Considerations

- Default Grafana credentials should be changed in production
- Consider enabling authentication for Prometheus in production
- Monitor access to metrics endpoints
