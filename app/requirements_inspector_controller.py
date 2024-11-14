"""
Module containing the flask app running the python-requirements-inspector-service
"""

import json
import logging
import platform
from typing import TYPE_CHECKING

from flask import Flask, Response, request
from gevent.pywsgi import WSGIServer  # type: ignore
from python_requirements_inspector.workitem_analyzer import WorkitemAnalyzer  # type: ignore

from app.constants import (
    CONTENT_LENGTH_LIMIT,
    POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION_HEADER,
    POLARION_REQUIREMENTS_INSPECTOR_VERSION_HEADER,
    PYTHON_VERSION_HEADER,
)
from app.type_definitions import (
    RequestSizeException,
    VersionDto,
)

if TYPE_CHECKING:
    from python_requirements_inspector.type_definitions import RequirementsInspectorResponseItem, WorkItem  # type: ignore

app = Flask(__name__)


@app.route("/version")
def version() -> VersionDto:
    """
    Returns:
        VersionDto: python, requirements-inspector and requirements-inspector-service versions
    """
    return VersionDto(
        python=platform.python_version(),
        polarion_requirements_inspector=app.config[POLARION_REQUIREMENTS_INSPECTOR_VERSION_HEADER.upper()],
        polarion_requirements_inspector_service=app.config[POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION_HEADER.upper()],
    )


@app.route("/inspect/workitems", methods=["POST"])
def inspect_workitems() -> Response:
    """
    POST-endpoint to perform requirements inspection on a list of work items of type WorkItem
    Returns:
        list[RequirementsInspectorResponseItem]: List of results of inspected work items
    """
    try:
        content_length_limit = app.config[CONTENT_LENGTH_LIMIT]
        if request.content_length > content_length_limit:
            raise RequestSizeException("JSON File too large")
        work_items: list[WorkItem] = json.loads(request.data)
        work_item_analyzer = WorkitemAnalyzer()
        for work_item in work_items:
            work_item_analyzer.analyze_workitem(work_item)
        output_data: list[RequirementsInspectorResponseItem] = work_item_analyzer.get_collected_data()
        return Response(
            json.dumps(output_data),
            headers={
                PYTHON_VERSION_HEADER: platform.python_version(),
                POLARION_REQUIREMENTS_INSPECTOR_VERSION_HEADER: app.config[POLARION_REQUIREMENTS_INSPECTOR_VERSION_HEADER.upper()],
                POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION_HEADER: app.config[POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION_HEADER.upper()],
            },
            mimetype="application/json",
            status=200,
        )
    except RequestSizeException as e:
        return process_error(e, str(e), 413)
    except json.JSONDecodeError as e:
        return process_error(e, "JSON file invalid", 400)
    except Exception as e:  # pylint: disable=broad-except
        return process_error(e, "Unknown exception handled during processing", 500)


def create_test_app(polarion_requirements_inspector_version: str, polarion_requirements_inspector_service_version: str, content_length_limit: int = (1 << 24)) -> Flask:
    app.config[POLARION_REQUIREMENTS_INSPECTOR_VERSION_HEADER.upper()] = polarion_requirements_inspector_version
    app.config[POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION_HEADER.upper()] = polarion_requirements_inspector_service_version
    app.config[CONTENT_LENGTH_LIMIT] = content_length_limit
    return app


def start_server(port: int, polarion_requirements_inspector_version: str, polarion_requirements_inspector_service_version: str, content_length_limit: int) -> None:
    """Starts the Requirements Inspector Service"""
    app.config[POLARION_REQUIREMENTS_INSPECTOR_VERSION_HEADER.upper()] = polarion_requirements_inspector_version
    app.config[POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION_HEADER.upper()] = polarion_requirements_inspector_service_version
    app.config[CONTENT_LENGTH_LIMIT] = content_length_limit
    http_server = WSGIServer(("", port), app)
    http_server.serve_forever()


def process_error(e: Exception, err_msg: str, status: int) -> Response:
    """Processes common errors, logs them and returns a Response

    Args:
        e (Exception): The thrown exception
        err_msg (str): Custom error message for the response object
        status (int): Status code (400+)

    Returns:
        flask.Response: Flask Response object sent back to the client
    """
    logging.exception(e)
    return Response(err_msg, mimetype="plain/text", status=status)
