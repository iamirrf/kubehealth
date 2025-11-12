.PHONY: install api monitor reports test lint sbom docker-build compose-up remediate publish clean

# Install dependencies
install:
	python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt -c constraints.txt

# Run API server
api:
	python run.py

# Run monitor
monitor:
	python -c "from app.monitor import run_monitor; run_monitor()"

# Generate reports (starts API, runs monitor, stops API)
reports: start-api
	python -c "import time; time.sleep(2); from app.monitor import run_monitor; run_monitor()"
	@echo "Reports generated successfully"

start-api:
	@echo "Starting API server..."
	@nohup python run.py > api.log 2>&1 & echo $$! > api.pid

stop-api:
	@echo "Stopping API server..."
	@-kill `cat api.pid` 2>/dev/null || true
	@-rm -f api.pid 2>/dev/null || true

# Run tests
test:
	PYTHONPATH=. pytest --junitxml=./test-results/junit.xml

# Run linting and security checks
lint:
	ruff check app
	bandit -r app

# Generate SBOM
sbom:
	mkdir -p artifacts
	cyclonedx-py -j -o ./artifacts/sbom.json

# Build Docker image
docker-build:
	docker build -t kubehealth .

# Run with Docker Compose
compose-up:
	docker-compose up --abort-on-container-exit

# Run remediation (Ansible stub)
remediate:
	ansible-playbook ansible/remediation.yml

# Run full pipeline (publish)
publish: install reports test lint sbom docker-build compose-up
	@echo "Full pipeline completed successfully"

# Clean up
clean:
	rm -rf .venv __pycache__ */__pycache__ test-results artifacts
	rm -f api.log api.pid pipeline_report.json pipeline_report.md
	docker-compose down 2>/dev/null || true
	@echo "Cleanup completed"
