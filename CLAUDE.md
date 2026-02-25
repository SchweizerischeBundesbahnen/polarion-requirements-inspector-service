# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python FastAPI service that provides a REST API for the Polarion Requirements Inspector functionality. The service analyzes work items (requirements/tickets) and provides inspection results via HTTP endpoints.

## Architecture

The codebase follows a simple layered architecture:

- **app/requirements_inspector_service.py**: Main application entry point with CLI argument parsing
- **app/requirements_inspector_controller.py**: FastAPI application with HTTP endpoints and middleware
- **app/type_definitions.py**: Pydantic models for request/response schemas
- **app/constants.py**: Application constants and header definitions
- **tests/**: Test suite with unit tests for service, controller, and container

The service wraps the `python-requirements-inspector` library and exposes two main endpoints:
- `GET /version`: Returns version information
- `POST /inspect/workitems`: Analyzes work items and returns inspection results

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync --all-groups
```

### Testing
```bash
# Run all tests and linting via tox
uv run tox

# Run tests for specific environment
uv run tox -e py312

# Run tests directly with pytest
uv run coverage run -m pytest tests/ --junitxml="junittest.xml" -v
uv run coverage report -m --fail-under 80
```

### Linting and Formatting
```bash
# Run linting environment
uv run tox -e lint

# Run individual tools
uv run ruff format
uv run ruff check
uv run mypy .
```

### Running the Service
```bash
# Run service locally
uv run python -m app.requirements_inspector_service --port 9081

# With custom request size limit
uv run python -m app.requirements_inspector_service --port 9081 --request-size-limit 16777216
```

### Docker Operations
```bash
# Build Docker image
docker build --build-arg APP_IMAGE_VERSION=0.0.0-dev --file Dockerfile --tag polarion-requirements-inspector-service:0.0.0-dev .

# Run Docker container
docker run --init --detach --publish 9081:9081 --name polarion-requirements-inspector-service polarion-requirements-inspector-service:0.0.0-dev

# Test Docker image structure
docker build -t polarion-requirements-inspector-service:local .
container-structure-test test --image polarion-requirements-inspector-service:local --config .config/container-structure-test.yaml
```

## Key Configuration

- **Python Version**: 3.12 (pinned in `.tool-versions`)
- **Package Manager**: uv (lock file: `uv.lock`)
- **Main Dependencies**: FastAPI, uvicorn, python-requirements-inspector
- **Test Coverage**: Minimum 80% required
- **Code Style**: Ruff (line length 240)
- **Type Checking**: mypy with strict settings

## Important Notes

- The service requires the `POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION` environment variable to be set
- Request size limit is configurable via `--request-size-limit` (default: 16MB)
- Tests exclude from linting with specific ruff ignore rules
- The project uses uv for dependency management (`uv sync`, `uv run`, `uv lock`)
- Pre-commit hooks include security scans, linting, uv-lock check, and various code quality checks
- The Docker image is based on Red Hat UBI9 minimal and runs as a non-root user (`appuser`)
- The `numpy>=1.25,<2.0` override in `pyproject.toml` is intentional — numpy is a transitive dependency via spacy/thinc from `python-requirements-inspector`

## Testing Endpoints

```bash
# Test version endpoint
curl -X GET -H "Content-Type: application/json" http://localhost:9081/version

# Test workitem inspection
curl -X POST -H "Content-Type: application/json" -H "Accept: application/json" --data '[{"title":"example","description":"example","language":"en"}]' http://localhost:9081/inspect/workitems
```
