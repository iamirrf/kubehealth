import json
from jsonschema import validate, ValidationError

# Define the schema for pipeline reports
PIPELINE_REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "timestamp": {
            "type": "string",
            "format": "date-time"
        },
        "total_jobs": {
            "type": "integer",
            "minimum": 0
        },
        "successful_jobs": {
            "type": "integer",
            "minimum": 0
        },
        "failed_jobs": {
            "type": "integer",
            "minimum": 0
        },
        "running_jobs": {
            "type": "integer",
            "minimum": 0
        },
        "pending_jobs": {
            "type": "integer",
            "minimum": 0
        },
        "jobs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["success", "failed", "running", "pending"]
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "duration": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "pipeline_type": {
                        "type": "string",
                        "enum": ["build", "test", "deploy"]
                    }
                },
                "required": ["name", "status", "timestamp", "duration", "pipeline_type"]
            }
        }
    },
    "required": [
        "timestamp",
        "total_jobs",
        "successful_jobs",
        "failed_jobs",
        "running_jobs",
        "pending_jobs",
        "jobs"
    ]
}

def validate_report(report):
    """
    Validate a pipeline report against the schema
    Returns True if valid, False otherwise
    """
    try:
        validate(instance=report, schema=PIPELINE_REPORT_SCHEMA)
        return True
    except ValidationError as e:
        print(f"Schema validation error: {e.message}")
        return False

def load_schema_from_file(schema_path):
    """
    Load schema from a file
    """
    try:
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        return schema
    except Exception as e:
        print(f"Error loading schema from file: {str(e)}")
        return None

def validate_report_with_file_schema(report, schema_path):
    """
    Validate a report against a schema loaded from file
    """
    schema = load_schema_from_file(schema_path)
    if schema is None:
        return False

    try:
        validate(instance=report, schema=schema)
        return True
    except ValidationError as e:
        print(f"Schema validation error: {e.message}")
        return False
