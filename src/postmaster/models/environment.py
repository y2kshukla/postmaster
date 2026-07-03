from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, Field


class EnvironmentVariable(BaseModel):
    name: str = ""
    value: str = ""
    secret: bool = False


class Environment(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    name: str = "Default Environment"
    variables: list[EnvironmentVariable] = Field(default_factory=list)
