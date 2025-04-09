import importlib
import importlib.metadata
import json
import logging
import platform
import sys
from typing import TYPE_CHECKING, NamedTuple

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from python_requirements_inspector.type_definitions import RequirementsInspectorResponseItem, WorkItem

from app.requirements_inspector_controller import create_test_app

if TYPE_CHECKING:
    from app.type_definitions import VersionSchema


class TestParams(NamedTuple):
    __test__ = False
    app: FastAPI
    python_version: str
    requirements_inspector_version: str
    requirements_inspector_service_version: str


@pytest.fixture(scope="module")
def test_params():
    logging.disable(logging.CRITICAL)
    python_version = platform.python_version()
    requirements_inspector_version = importlib.metadata.version("python-requirements-inspector")
    requirements_inspector_service_version = "1.0.0"
    app = create_test_app(requirements_inspector_version, requirements_inspector_service_version)
    yield TestParams(app, python_version, requirements_inspector_version, requirements_inspector_service_version)


def test_version(test_params: TestParams):
    """_summary_"""
    with TestClient(test_params.app) as test_client:
        response: VersionSchema = test_client.get("/version").json()
        assert response.get("python") == test_params.python_version
        assert response.get("polarion_requirements_inspector") == test_params.requirements_inspector_version
        assert response.get("polarion_requirements_inspector_service") == test_params.requirements_inspector_service_version


def test_inspect_workitems_valid(test_params: TestParams):
    """_summary_"""
    with TestClient(test_params.app) as test_client:
        expected = RequirementsInspectorResponseItem(
            id="test", language="en", smellDescription="In TITLE missingProcessword: Title contains no process word\n", smellComplex=0, smellPassive=0, smellWeakword=0, smellComparative=0, missingProcessword=True
        )
        response: list[RequirementsInspectorResponseItem] = test_client.post("/inspect/workitems", json=[WorkItem(id="test", title="test", description="test", language="en")]).json()
        assert [expected] == response


def test_inspect_workitems_request_size_limit(test_params: TestParams):
    """Test the request size limit of 1<<24. Should return 413"""
    work_item: WorkItem = WorkItem(title="example", description="example", language="en")
    n = (2 << 24) // sys.getsizeof(json.dumps(work_item))
    work_items = [work_item for _ in range(n)]
    with TestClient(test_params.app, raise_server_exceptions=False) as test_client:
        response = test_client.post("/inspect/workitems", json=work_items)
        assert response.status_code == 413


def test_inspect_workitems_invalid_json(test_params: TestParams):
    with TestClient(test_params.app) as test_client:
        response = test_client.post("/inspect/workitems", data='[{"title":"example","description":"example","language":"en"]')
        assert response.status_code == 422


def test_inspect_workitems_non_iterable_json(test_params: TestParams):
    with TestClient(test_params.app) as test_client:
        response = test_client.post("/inspect/workitems", json=1)
        assert response.status_code == 422
