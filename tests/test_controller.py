import json
import logging
import platform
import sys
from typing import TYPE_CHECKING
from unittest import TestCase

from flask import Flask
from python_requirements_inspector.type_definitions import RequirementsInspectorResponseItem, WorkItem

from app.requirements_inspector_controller import create_test_app

if TYPE_CHECKING:
    from app.type_definitions import VersionDto


class PolarionRequirementsInspectorServiceTest(TestCase):
    polarion_requirements_inspector_version = "1.0.0"
    polarion_requirements_inspector_service_version = "1.0.0"
    python_version = platform.python_version()
    app: Flask

    @classmethod
    def setUpClass(cls):
        cls.app = create_test_app(cls.polarion_requirements_inspector_version, cls.polarion_requirements_inspector_service_version)
        logging.disable(logging.CRITICAL)

    def test_version(self):
        """_summary_"""
        with self.app.test_client() as test_client:
            response: VersionDto = test_client.get("/version").json
            self.assertEqual(response.get("python"), self.python_version)
            self.assertEqual(response.get("polarion_requirements_inspector"), self.polarion_requirements_inspector_version)
            self.assertEqual(response.get("polarion_requirements_inspector_service"), self.polarion_requirements_inspector_service_version)

    def test_inspect_workitems_valid(self):
        """_summary_"""
        with self.app.test_client() as test_client:
            expected = RequirementsInspectorResponseItem(
                id="test", language="en", smellDescription="In TITLE missingProcessword: Title contains no process word\n", smellComplex=0, smellPassive=0, smellWeakword=0, smellComparative=0, missingProcessword=True
            )
            response: list[RequirementsInspectorResponseItem] = test_client.post("/inspect/workitems", json=[WorkItem(id="test", title="test", description="test", language="en")]).json

            self.assertEqual([expected], response)

    def test_inspect_workitems_request_size_limit(self):
        """Test the request size limit of 1<<24. Should return 413"""
        work_item: WorkItem = WorkItem(title="example", description="example", language="en")
        n = (2 << 24) // sys.getsizeof(json.dumps(work_item))
        work_items = [work_item for _ in range(n)]
        with self.app.test_client() as test_client:
            response = test_client.post("/inspect/workitems", json=work_items)

            self.assertEqual(response.status_code, 413)

    def test_inspect_workitems_invalid_json(self):
        with self.app.test_client() as test_client:
            response = test_client.post("/inspect/workitems", data='[{"title":"example","description":"example","language":"en"]')
            self.assertEqual(response.status_code, 400)

    def test_inspect_workitems_non_iterable_json(self):
        with self.app.test_client() as test_client:
            response = test_client.post("/inspect/workitems", json=1)
            self.assertEqual(response.status_code, 500)
