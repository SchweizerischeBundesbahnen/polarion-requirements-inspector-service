"""Types for RequirementsInspectorController"""

from typing import TypedDict


class VersionDto(TypedDict):
    """
    Type Class for the return value of /version
    """

    python: str
    polarion_requirements_inspector: str
    polarion_requirements_inspector_service: str


class RequestSizeException(Exception):
    """
    Thrown on POST-endpoint /analyze/workitems if the request size is too large
    """
