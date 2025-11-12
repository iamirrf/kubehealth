# Automation Architecture

## Overview
This document explains how the CI/CD and CLI layers interact in the kubehealth system.

## System Architecture

### CLI Layer
The CLI layer provides a set of Makefile targets that automate the entire development and deployment workflow:

- `make install` - Sets up the Python virtual environment and installs dependencies
- `make api` - Runs the Flask API server
- `make monitor` - Runs the pipeline monitoring system
- `make reports` - Generates pipeline reports by starting the API and running the monitor
- `make test` - Runs unit tests with pytest
- `make lint` - Performs code linting and security scanning
- `make sbom` - Generates a Software Bill of Materials
- `make docker-build` - Builds the Docker image
- `make compose-up` - Runs the system with Docker Compose
- `make remediate` - Runs the Ansible remediation playbook
- `make publish` - Runs the full pipeline (install, reports, test, lint, sbom, docker-build, compose-up)
- `make clean` - Cleans up generated files and containers

### CI/CD Layer
The CI/CD layer is implemented as a GitHub Actions workflow in `.github/workflows/test.yml`. It:

1. Checks out the code
2. Sets up Python 3.11
3. Caches pip dependencies
4. Installs dependencies
5. Runs linter (ruff)
6. Runs security scan (bandit)
7. Runs tests (pytest)
8. Builds Docker image
9. Generates SBOM
10. Uploads artifacts (test results, SBOM, audit log)

## Interaction Flow

1. Developers use the CLI layer for local development and testing
2. When code is pushed to the main branch, the CI/CD layer automatically triggers
3. The CI/CD layer performs the same validation steps as the CLI layer to ensure consistency
4. If all checks pass, the code is considered production-ready

## Audit Trail

All CLI actions are logged to `AUDIT_LOG.txt` with the format:
```
[timestamp] <command> → <exit_code>
```

This provides a complete audit trail of all operations performed on the system.

## Security & Compliance

The system implements several security measures:
- Dependency pinning via `constraints.txt`
- Security scanning with Bandit
- SBOM generation for supply chain transparency
- Pre-commit hooks for code quality
- Docker security best practices (non-root user, minimal base image)

## OpenShift Integration Path

Future integration with OpenShift will involve:
1. Replacing the mock endpoint with real OpenShift API calls (`oc get builds -o json`)
2. Extending the Ansible stub to real playbooks for pod restarts
3. Adding Prometheus exporter for metrics
4. Deploying on OpenShift using Helm
