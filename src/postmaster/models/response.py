from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TimingBreakdown(BaseModel):
    dns: float = 0.0
    tcp: float = 0.0
    tls: float = 0.0
    waiting: float = 0.0
    download: float = 0.0
    total: float = 0.0


class HttpRedirect(BaseModel):
    status_code: int
    location: str
    headers: dict[str, str] = Field(default_factory=dict)


class HttpResponse(BaseModel):
    status_code: int = 0
    status_text: str = ""
    http_version: str = ""
    headers: dict[str, str] = Field(default_factory=dict)
    body: bytes = b""
    body_text: str = ""
    cookies: list[dict[str, str]] = Field(default_factory=list)
    timing: TimingBreakdown = Field(default_factory=TimingBreakdown)
    redirect_chain: list[HttpRedirect] = Field(default_factory=list)
    content_type: str = ""
    content_length: int = 0
    error: Optional[str] = None
