import importlib
import importlib.metadata
import json
import re
import sys
import time
from typing import NamedTuple

import docker
import pytest
import requests
from docker.models.containers import Container
from python_requirements_inspector.type_definitions import RequirementsInspectorResponseItem, WorkItem
import subprocess

from app.constants import (
    POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION_HEADER,
    POLARION_REQUIREMENTS_INSPECTOR_VERSION_HEADER,
    PYTHON_VERSION_HEADER,
)
from app.type_definitions import VersionSchema

port = 9081
requirements_inspector_version = importlib.metadata.version("python-requirements-inspector")
requirements_inspector_service_version = "3.0.0"


class TestParams(NamedTuple):
    __test__ = False
    port: int
    base_url: str
    session: requests.Session
    version: VersionSchema
    container: Container


@pytest.fixture(scope="module")
def requirements_inspector_container():
    """
    Setup function for building and starting the requirements-inspector-service image.
    Runs once per module and is cleaned up after execution

    Yields:
        Container: Built docker container
    """
    container = None
    image = None
    try:
        client = docker.from_env()
        build_process = subprocess.run([
            "docker",
            "build",
            "--build-arg",
            f"APP_IMAGE_VERSION={requirements_inspector_service_version}",
            "--file",
            "Dockerfile",
            "--tag",
            "requirements_inspector_service",
            "."
        ])
        if build_process.returncode != 0:
            raise Exception("Build process failed")
        container = client.containers.run(image="requirements_inspector_service", detach=True, name="requirements_inspector_service", ports={"9081": port}, init=True)
        time.sleep(5)
        yield container
    finally:
        if container:
            container.stop()
            container.remove(v=True)
        subprocess.run([
            "docker",
            "image",
            "rm",
            "requirements_inspector_service"
        ])


@pytest.fixture(scope="module")
def test_params(requirements_inspector_container: Container):
    base_url = f"http://localhost:{port}"
    session = requests.Session()
    version = VersionSchema(
        python="3.12.7",
        polarion_requirements_inspector=requirements_inspector_version,
        polarion_requirements_inspector_service=requirements_inspector_service_version,
    )
    yield TestParams(port, base_url, session, version, requirements_inspector_container)
    session.close()


def test_version(test_params: TestParams) -> None:
    """
    Test and compare the returned versions to the ones of requirements.txt
    and python platform version. Should return 200
    """
    res = test_params.session.get(f"{test_params.base_url}/version")
    assert res.status_code == 200
    version: VersionSchema = res.json()
    assert version.get("python") == test_params.version.python
    assert version.get("polarion_requirements_inspector") == test_params.version.polarion_requirements_inspector
    assert version.get("polarion_requirements_inspector_service") == test_params.version.polarion_requirements_inspector_service


def test_response_fields(test_params: TestParams) -> None:
    """
    Test if all the fields of type RequirementsInspectorResponseItem are present in the response.
    Should return 200
    """
    res = test_params.session.post(
        f"{test_params.base_url}/inspect/workitems",
        json=[WorkItem(title="Example", description="Example", language="en")],
    )
    data: list[RequirementsInspectorResponseItem] = res.json()
    assert res.status_code == 200
    assert len(data) > 0
    assert data[0].keys() == RequirementsInspectorResponseItem.__annotations__.keys()


def test_response_version_headers(test_params: TestParams) -> None:
    """
    Test if all the headers contain python_version and requirements_inspector_version.
    Should return 200
    """
    res = test_params.session.post(
        f"{test_params.base_url}/inspect/workitems",
        json=[WorkItem(title="Example", description="Example", language="en")],
    )
    assert res.status_code == 200
    assert res.headers.get(PYTHON_VERSION_HEADER) == test_params.version.python
    assert res.headers.get(POLARION_REQUIREMENTS_INSPECTOR_VERSION_HEADER) == test_params.version.polarion_requirements_inspector
    assert res.headers.get(POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION_HEADER) == test_params.version.polarion_requirements_inspector_service


def test_invalid_json(test_params: TestParams) -> None:
    """Test a json that cannot be deserialized. Should return 400"""
    res = test_params.session.post(
        f"{test_params.base_url}/inspect/workitems",
        data='[{"title":"example","description":"example","language":"en"]',
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=10000,
    )
    assert res.status_code == 422


def test_non_iterable_json(test_params: TestParams) -> None:
    """Test an object that is not iterable. Should return 500"""
    res = test_params.session.post(f"{test_params.base_url}/inspect/workitems", data="1")
    assert res.status_code == 422


def test_request_size_limit(test_params: TestParams) -> None:
    """Test the request size limit of 1<<24. Should return 413"""
    work_item: WorkItem = WorkItem(title="example", description="example", language="en")
    n = (2 << 24) // sys.getsizeof(json.dumps(work_item))
    work_items = [work_item for _ in range(n)]
    res = test_params.session.post(f"{test_params.base_url}/inspect/workitems", data=json.dumps(work_items))
    assert res.status_code == 413


def test_openapi_endpoint(test_params: TestParams) -> None:
    """Test that the openapi docs are available"""
    res = test_params.session.get(f"{test_params.base_url}/static/openapi.json")
    assert b"/version" in res.content
    assert b"/inspect/workitems" in res.content


def test_docs_endpoint(test_params: TestParams) -> None:
    """Test that the docs endpoint works"""
    res = test_params.session.get(f"{test_params.base_url}/api/docs")
    assert res.status_code == 200
