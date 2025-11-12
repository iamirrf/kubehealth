import os
import random
from datetime import datetime
from flask import Flask, jsonify

# Set deterministic randomness
RANDOM_SEED = int(os.getenv('RANDOM_SEED', 42))
random.seed(RANDOM_SEED)

app = Flask(__name__)

# Configuration
PORT = int(os.getenv('PORT', 8080))
DEFAULT_TIMEOUT = 5  # seconds
RETRY_INTERVAL = 0.5  # seconds

@app.route('/mock/pipeline/status', methods=['GET'])
def get_pipeline_status():
    """Mock endpoint that simulates OpenShift pipeline results"""
    try:
        # Simulate pipeline data with different statuses
        pipeline_jobs = [
            {
                "name": f"build-job-{i}",
                "status": random.choice(["success", "failed", "running", "pending"]),
                "timestamp": datetime.now().isoformat(),
                "duration": random.randint(30, 300),  # Duration in seconds
                "pipeline_type": random.choice(["build", "test", "deploy"])
            }
            for i in range(random.randint(5, 15))  # Random number of jobs between 5-15
        ]

        response_data = {
            "timestamp": datetime.now().isoformat(),
            "total_jobs": len(pipeline_jobs),
            "successful_jobs": len([j for j in pipeline_jobs if j["status"] == "success"]),
            "failed_jobs": len([j for j in pipeline_jobs if j["status"] == "failed"]),
            "running_jobs": len([j for j in pipeline_jobs if j["status"] == "running"]),
            "pending_jobs": len([j for j in pipeline_jobs if j["status"] == "pending"]),
            "jobs": pipeline_jobs
        }

        return jsonify(response_data), 200
    except Exception as e:
        app.logger.error(f"Error generating pipeline status: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/healthz', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    # In a real implementation, this would return Prometheus-formatted metrics
    # For now, return basic metrics
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "total_requests": 0,
            "active_connections": 1,
            "cpu_usage": 0.1,
            "memory_usage": 0.2
        }
    }), 200

def run_api():
    """Run the Flask application"""
    app.run(host='0.0.0.0', port=PORT, debug=False)

if __name__ == '__main__':
    # Try different ports if default is taken
    ports_to_try = [PORT, 8081, 8082, 8083]
    for port in ports_to_try:
        try:
            app.run(host='0.0.0.0', port=port, debug=False)
            break
        except OSError:
            if port == 8083:  # Last port in the list
                print(f"Could not bind to any of the ports: {ports_to_try}")
                exit(1)
            else:
                continue
