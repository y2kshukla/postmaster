from __future__ import annotations

from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from postmaster.models.request import HttpRequest


class RequestItem(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    name: str = "New Request"
    request: HttpRequest = Field(default_factory=HttpRequest)
    tags: list[str] = Field(default_factory=list)
    favorite: bool = False


class Folder(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    name: str = "New Folder"
    items: list[RequestItem | Folder] = Field(default_factory=list)


class Collection(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    name: str = "New Collection"
    items: list[RequestItem | Folder] = Field(default_factory=list)
    variables: dict[str, str] = Field(default_factory=dict)
