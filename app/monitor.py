import os
import json
import requests
import time
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .schema_validator import validate_report

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8080')
DEFAULT_TIMEOUT = 5  # seconds
RETRY_INTERVAL = 0.5  # seconds
MAX_RETRIES = 10  # Total time = MAX_RETRIES * RETRY_INTERVAL

def get_pipeline_status_with_retry():
    """Fetch pipeline status with retry logic"""
    url = f"{API_BASE_URL}/mock/pipeline/status"

    # Set up retry strategy
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Attempt to get status with retries
    for attempt in range(MAX_RETRIES):
        try:
            response = session.get(url, timeout=DEFAULT_TIMEOUT)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Attempt {attempt + 1}: Got status code {response.status_code}, retrying...")
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1}: Request failed: {str(e)}, retrying...")

        time.sleep(RETRY_INTERVAL)

    raise Exception(f"Failed to fetch pipeline status after {MAX_RETRIES} attempts")

def generate_reports():
    """Generate JSON and Markdown reports based on pipeline status"""
    try:
        # Fetch pipeline status
        pipeline_data = get_pipeline_status_with_retry()

        # Generate JSON report
        json_report = {
            "timestamp": datetime.now().isoformat(),
            "total_jobs": pipeline_data["total_jobs"],
            "successful_jobs": pipeline_data["successful_jobs"],
            "failed_jobs": pipeline_data["failed_jobs"],
            "running_jobs": pipeline_data["running_jobs"],
            "pending_jobs": pipeline_data["pending_jobs"],
            "jobs": pipeline_data["jobs"]
        }

        # Validate report against schema
        if not validate_report(json_report):
            raise Exception("Report validation failed against schema")

        # Save JSON report
        with open('pipeline_report.json', 'w') as f:
            json.dump(json_report, f, indent=2)

        # Generate Markdown report
        status_emojis = {
            "success": "✅",
            "failed": "❌",
            "running": "🔄",
            "pending": "⏳"
        }

        markdown_content = f"""# Pipeline Health Report

**Generated at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Total Jobs:** {json_report['total_jobs']}
- **Successful:** {json_report['successful_jobs']} {status_emojis['success']}
- **Failed:** {json_report['failed_jobs']} {status_emojis['failed']}
- **Running:** {json_report['running_jobs']} {status_emojis['running']}
- **Pending:** {json_report['pending_jobs']} {status_emojis['pending']}

## Job Details
"""

        for job in json_report['jobs']:
            status_emoji = status_emojis.get(job['status'], '❓')
            markdown_content += f"- **{job['name']}**: {job['status']} {status_emoji} (Duration: {job['duration']}s)\n"

        # Save Markdown report
        with open('pipeline_report.md', 'w') as f:
            f.write(markdown_content)

        print("Reports generated successfully:")
        print("- JSON report: pipeline_report.json")
        print("- Markdown report: pipeline_report.md")
        print(f"- Total jobs: {json_report['total_jobs']}")
        print(f"- Failed jobs: {json_report['failed_jobs']}")

        return json_report

    except Exception as e:
        print(f"Error generating reports: {str(e)}")
        raise

def run_monitor():
    """Main function to run the monitoring process"""
    print("Starting pipeline monitor...")
    try:
        report = generate_reports()
        return report
    except Exception as e:
        print(f"Monitor failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_monitor()
