"""
Module containing the flask app running the python-requirements-inspector-service
"""

import json
import logging
import platform
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, TypedDict

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from python_requirements_inspector.workitem_analyzer import WorkitemAnalyzer  # type: ignore

from app.type_definitions import VersionSchema, WorkItemSchema

if TYPE_CHECKING:
    from python_requirements_inspector.type_definitions import RequirementsInspectorResponseItem  # type: ignore


class Config(TypedDict):
    polarion_requirements_inspector_version: str
    polarion_requirements_inspector_service_version: str
    request_size_limit: int


config = Config(polarion_requirements_inspector_version="", polarion_requirements_inspector_service_version="", request_size_limit=0)

app = FastAPI(
    openapi_url="/static/openapi.json",
    docs_url="/api/docs",
)


@app.middleware("http")
async def check_request_size(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    size = len(await request.body())

    if size > config["request_size_limit"]:
        return Response("JSON Body too large", status_code=413, media_type="plain/text")

    response = await call_next(request)
    return response


@app.get("/version", response_model=VersionSchema)
async def version() -> VersionSchema:
    """
    Returns:
        VersionDto: python, requirements-inspector and requirements-inspector-service versions
    """
    return VersionSchema(
        python=platform.python_version(),
        polarion_requirements_inspector=config["polarion_requirements_inspector_version"],
        polarion_requirements_inspector_service=config["polarion_requirements_inspector_service_version"],
    )


@app.post(
    "/inspect/workitems",
    responses={
        400: {"content": {"text/plain": {}}, "description": "JSON Body invalid"},
        413: {"content": {"text/plain": {}}, "description": "JSON Body too large"},
        500: {"content": {"text/plain": {}}, "description": "Unknown internal Exception handled during processing"},
    },
    response_model=WorkItemSchema,
)
async def inspect_workitems(work_items: list[WorkItemSchema]) -> Response:
    """
    POST-endpoint to perform requirements inspection on a list of work items of type WorkItem
    Returns:
        list[RequirementsInspectorResponseItem]: List of results of inspected work items
    """
    try:
        work_item_analyzer = WorkitemAnalyzer()
        for work_item in work_items:
            work_item_analyzer.analyze_workitem(work_item.model_dump(exclude_none=True))
        output_data: list[RequirementsInspectorResponseItem] = work_item_analyzer.get_collected_data()
        return Response(
            json.dumps(output_data),
            headers={
                "python_version": platform.python_version(),
                "polarion_requirements_inspector_version": config["polarion_requirements_inspector_version"],
                "polarion_requirements_inspector_service_version": config["polarion_requirements_inspector_service_version"],
            },
            media_type="application/json",
            status_code=200,
        )
    except Exception as e:  # pylint: disable=broad-except
        return process_error(e, "Unknown exception handled during processing", 500)


def create_test_app(polarion_requirements_inspector_version: str, polarion_requirements_inspector_service_version: str, request_size_limit: int = (1 << 24)) -> FastAPI:
    config["polarion_requirements_inspector_version"] = polarion_requirements_inspector_version
    config["polarion_requirements_inspector_service_version"] = polarion_requirements_inspector_service_version
    config["request_size_limit"] = request_size_limit
    return app


def start_server(port: int, polarion_requirements_inspector_version: str, polarion_requirements_inspector_service_version: str, request_size_limit: int) -> None:
    """Starts the Requirements Inspector Service"""
    config["polarion_requirements_inspector_version"] = polarion_requirements_inspector_version
    config["polarion_requirements_inspector_service_version"] = polarion_requirements_inspector_service_version
    config["request_size_limit"] = request_size_limit

    uvicorn.run(app=app, host="", port=port)


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
    raise HTTPException(status_code=status, detail=err_msg)
