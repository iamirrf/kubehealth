import pytest
import json
from unittest.mock import patch, MagicMock
from app.main import app
from app.monitor import generate_reports
from app.schema_validator import validate_report, PIPELINE_REPORT_SCHEMA

def test_api_healthz():
    """Test the healthz endpoint"""
    with app.test_client() as client:
        response = client.get('/healthz')
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert 'status' in data
        assert data['status'] == 'healthy'

def test_api_metrics():
    """Test the metrics endpoint"""
    with app.test_client() as client:
        response = client.get('/metrics')
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert 'timestamp' in data
        assert 'metrics' in data

def test_api_pipeline_status():
    """Test the pipeline status endpoint"""
    with app.test_client() as client:
        response = client.get('/mock/pipeline/status')
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))

        # Check required fields
        assert 'timestamp' in data
        assert 'total_jobs' in data
        assert 'successful_jobs' in data
        assert 'failed_jobs' in data
        assert 'running_jobs' in data
        assert 'pending_jobs' in data
        assert 'jobs' in data

        # Check that total matches sum of statuses
        total_calc = (data['successful_jobs'] + data['failed_jobs'] +
                     data['running_jobs'] + data['pending_jobs'])
        assert data['total_jobs'] == total_calc

        # Check jobs structure
        for job in data['jobs']:
            assert 'name' in job
            assert 'status' in job
            assert 'timestamp' in job
            assert 'duration' in job
            assert 'pipeline_type' in job
            assert job['status'] in ['success', 'failed', 'running', 'pending']
            assert job['pipeline_type'] in ['build', 'test', 'deploy']

def test_schema_validation():
    """Test schema validation with valid data"""
    valid_report = {
        "timestamp": "2023-10-01T12:00Z",
        "total_jobs": 10,
        "successful_jobs": 7,
        "failed_jobs": 1,
        "running_jobs": 1,
        "pending_jobs": 1,
        "jobs": [
            {
                "name": "test-job-1",
                "status": "success",
                "timestamp": "2023-10-01T11:55:00Z",
                "duration": 120,
                "pipeline_type": "build"
            }
        ]
    }

    assert validate_report(valid_report) == True

def test_schema_validation_invalid():
    """Test schema validation with invalid data"""
    invalid_report = {
        "timestamp": "invalid-date",  # Invalid date format
        "total_jobs": -5,  # Invalid negative number
        "successful_jobs": 7,
        "failed_jobs": 1,
        "running_jobs": 1,
        "pending_jobs": 1,
        "jobs": [
            {
                "name": "test-job-1",
                "status": "invalid-status",  # Invalid status
                "timestamp": "2023-10-01T1:55:00Z",
                "duration": 120,
                "pipeline_type": "build"
            }
        ]
    }

    assert validate_report(invalid_report) == False

def test_schema_structure():
    """Test that the schema structure is correct"""
    assert isinstance(PIPELINE_REPORT_SCHEMA, dict)
    assert 'type' in PIPELINE_REPORT_SCHEMA
    assert 'properties' in PIPELINE_REPORT_SCHEMA
    assert PIPELINE_REPORT_SCHEMA['type'] == 'object'

@patch('app.monitor.get_pipeline_status_with_retry')
def test_generate_reports(mock_get_status):
    """Test report generation"""
    # Mock the API response
    mock_response = {
        "timestamp": "2023-10-01T12:00Z",
        "total_jobs": 5,
        "successful_jobs": 3,
        "failed_jobs": 1,
        "running_jobs": 1,
        "pending_jobs": 0,
        "jobs": [
            {
                "name": "job-1",
                "status": "success",
                "timestamp": "2023-10-01T11:55:00Z",
                "duration": 120,
                "pipeline_type": "build"
            },
            {
                "name": "job-2",
                "status": "failed",
                "timestamp": "2023-10-01T11:56:00Z",
                "duration": 90,
                "pipeline_type": "test"
            },
            {
                "name": "job-3",
                "status": "success",
                "timestamp": "2023-10-01T1:57:00Z",
                "duration": 150,
                "pipeline_type": "build"
            },
            {
                "name": "job-4",
                "status": "success",
                "timestamp": "2023-10-01T1:58:00Z",
                "duration": 180,
                "pipeline_type": "test"
            },
            {
                "name": "job-5",
                "status": "running",
                "timestamp": "2023-10-01T11:59:00Z",
                "duration": 60,
                "pipeline_type": "deploy"
            }
        ]
    }

    mock_get_status.return_value = mock_response

    # Generate reports
    report = generate_reports()

    # Verify the report structure
    assert 'timestamp' in report
    assert report['total_jobs'] == 5
    assert report['successful_jobs'] == 3
    assert report['failed_jobs'] == 1
    assert report['running_jobs'] == 1
    assert report['pending_jobs'] == 0
    assert len(report['jobs']) == 5

    # Verify validation was performed
    assert validate_report(report) == True

if __name__ == '__main__':
    pytest.main()
