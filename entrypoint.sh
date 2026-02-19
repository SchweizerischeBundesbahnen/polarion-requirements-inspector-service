#!/bin/bash

# Use environment variables with defaults already set in Dockerfile
BUILD_TIMESTAMP="$(cat /opt/requirements_inspector/.build_timestamp)"
export REQUIREMENTS_INSPECTOR_SERVICE_BUILD_TIMESTAMP=${BUILD_TIMESTAMP}

echo "Starting Requirements Inspector service on port $PORT with log level $LOG_LEVEL"

# Convert log level to lowercase for uvicorn
LOG_LEVEL_LOWER=$(echo "$LOG_LEVEL" | tr '[:upper:]' '[:lower:]')

# Execute the service application with python
exec python -m app.requirements_inspector_service --port $PORT --log-level $LOG_LEVEL_LOWER --request-size-limit $REQUEST_SIZE_LIMIT
