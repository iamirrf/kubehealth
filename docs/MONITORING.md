# Monitoring and Metrics

## Overview
This document describes the metrics export, log levels, and Prometheus integration in the kubehealth system.

## Metrics Export

The kubehealth system exposes metrics through multiple endpoints:

### Health Check Endpoint
- **Path**: `/healthz`
- **Method**: GET
- **Purpose**: Provides basic health status of the application
- **Response**: JSON object with status and timestamp

### Metrics Endpoint
- **Path**: `/metrics`
- **Method**: GET
- **Purpose**: Provides application metrics in a format suitable for monitoring
- **Response**: JSON object with various metrics

### Pipeline Status Endpoint
- **Path**: `/mock/pipeline/status`
- **Method**: GET
- **Purpose**: Provides simulated OpenShift pipeline status for monitoring
- **Response**: JSON object with pipeline job details

## Log Levels

The system implements the following log levels:

- **DEBUG**: Detailed diagnostic information for troubleshooting
- **INFO**: General operational information
- **WARNING**: Indications of potential issues that don't affect operation
- **ERROR**: Errors that affect operation but don't cause system failure
- **CRITICAL**: Serious errors that cause system failure

Logs are written to standard output and can be redirected as needed.

## Prometheus Integration

The system is designed for Prometheus integration:

1. The `/metrics` endpoint can be enhanced to provide Prometheus-formatted metrics
2. Standard Prometheus metrics like request counts, response times, and error rates are collected
3. Custom metrics related to pipeline health are exposed

### Sample Prometheus Configuration
```yaml
scrape_configs:
  - job_name: 'kubehealth'
    static_configs:
      - targets: ['localhost:8080']
```

## Report Generation

The monitoring system generates two types of reports:

### JSON Reports
- File: `pipeline_report.json`
- Contains detailed pipeline status information
- Validated against the schema in `schemas/pipeline_report.schema.json`

### Markdown Reports
- File: `pipeline_report.md`
- Human-readable format with emojis for status visualization
- Includes timestamp, total jobs, and job details

## Monitoring Workflow

1. The monitor component fetches pipeline status from the API
2. It analyzes the health of pipeline jobs
3. It generates validated reports
4. It logs the results to the audit trail

## Alerting

The system can be integrated with alerting systems through:
- Health check endpoint for uptime monitoring
- Metrics endpoint for custom alerting rules
- Log output for log-based alerting

## Performance Considerations

- The system implements retry logic with 0.5s intervals and 5s timeout
- Metrics collection has minimal performance impact
- Report generation is optimized for large numbers of pipeline jobs
