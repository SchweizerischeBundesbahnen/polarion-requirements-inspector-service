"""Types for RequirementsInspectorController"""

from pydantic import BaseModel, Field


class VersionSchema(BaseModel):
    """
    Type Class for the return value of /version
    """

    python: str
    polarion_requirements_inspector: str
    polarion_requirements_inspector_service: str


class WorkItemSchema(BaseModel, extra="allow"):
    id: str | None = Field(default=None)
    title: str | None = Field(default=None)
    description: str | None = Field(default=None)
    language: str | None = Field(default=None)
