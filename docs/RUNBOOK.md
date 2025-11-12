# Runbook

## Overview
This document provides operational procedures for the kubehealth system, including CI/CD workflows and rollback commands.

## CI/CD Pipeline

### Local Development Workflow
1. Set up the environment: `make install`
2. Run tests: `make test`
3. Run linting and security scans: `make lint`
4. Generate reports: `make reports`
5. Build Docker image: `make docker-build`
6. Test with Docker Compose: `make compose-up`

### Full Pipeline Execution
Run the complete pipeline with: `make publish`

This executes:
- Install dependencies
- Generate reports
- Run tests
- Run linting and security scans
- Generate SBOM
- Build Docker image
- Test with Docker Compose

## Deployment Commands

### Running the API Server
```bash
make api
```

### Running the Monitor
```bash
make monitor
```

### Running Both Together
```bash
make reports
```

## Rollback Commands

### Clean Up
To clean up all generated files and containers:
```bash
make clean
```

This removes:
- Virtual environment
- Cache files
- Test results
- Generated reports
- Docker containers (if any running)

### Reinstall Dependencies
```bash
make install
```

### Reset to Clean State
```bash
make clean && make install
```

## Troubleshooting

### API Server Issues
If the API server fails to start:
1. Check if the port is already in use: `lsof -i :8080`
2. Kill any processes using the port: `kill -9 <PID>`
3. Try alternative ports (8081-8083) - the application will automatically try these

### Monitor Issues
If the monitor fails to connect to the API:
1. Verify the API is running: `curl http://localhost:8080/healthz`
2. Check the API logs for errors
3. Ensure the correct API_BASE_URL is set in environment variables

### Docker Issues
If Docker builds fail:
1. Clean up Docker resources: `docker system prune -a`
2. Ensure Docker daemon is running
3. Check available disk space

## Security Scanning

### Run Security Scan
```bash
make lint
```

This runs Bandit security scanner on the app directory.

### Generate SBOM
```bash
make sbom
```

This generates a Software Bill of Materials in `artifacts/sbom.json`.

## Monitoring and Logging

### Audit Log
All operations are logged to `AUDIT_LOG.txt` with timestamps and exit codes.

### Generated Reports
- JSON report: `pipeline_report.json`
- Markdown report: `pipeline_report.md`

## Ansible Remediation

### Run Remediation
```bash
make remediate
```

This runs the Ansible playbook for simulated remediation of failed pipeline jobs.

## GitHub Actions CI

The CI pipeline runs automatically on:
- Push to main branch
- Pull requests to main branch

It performs the same checks as the local `make publish` command.
