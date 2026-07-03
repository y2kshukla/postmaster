from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class KeyValueEntry(BaseModel):
    key: str = ""
    value: str = ""
    description: str = ""
    enabled: bool = True


class BodyType(str, Enum):
    none = "none"
    json = "json"
    xml = "xml"
    form_data = "form-data"
    x_www_form_urlencoded = "x-www-form-urlencoded"
    raw = "raw"
    binary = "binary"


class AuthType(str, Enum):
    none = "None"
    bearer = "Bearer Token"
    basic = "Basic Auth"
    api_key = "API Key"
    oauth2 = "OAuth 2.0"


class BasicAuthConfig(BaseModel):
    username: str = ""
    password: str = ""


class BearerTokenConfig(BaseModel):
    token: str = ""


class APIKeyConfig(BaseModel):
    key: str = ""
    value: str = ""
    add_to: str = "Header"


class OAuth2Config(BaseModel):
    grant_type: str = "authorization_code"
    callback_url: str = ""
    auth_url: str = ""
    access_token_url: str = ""
    client_id: str = ""
    client_secret: str = ""
    scope: str = ""
    client_auth: str = "send_as_basic_auth"


class AuthConfig(BaseModel):
    type: AuthType = AuthType.none
    basic: BasicAuthConfig = Field(default_factory=BasicAuthConfig)
    bearer: BearerTokenConfig = Field(default_factory=BearerTokenConfig)
    api_key: APIKeyConfig = Field(default_factory=APIKeyConfig)
    oauth2: OAuth2Config = Field(default_factory=OAuth2Config)


class BodyConfig(BaseModel):
    type: BodyType = BodyType.none
    content: str = ""
    form_fields: list[KeyValueEntry] = Field(default_factory=list)
    binary_path: str = ""
    content_type: Optional[str] = None


class HttpRequest(BaseModel):
    method: str = "POST"
    url: str = ""
    protocol: str = "http/1.1"
    headers: list[KeyValueEntry] = Field(default_factory=list)
    query_params: list[KeyValueEntry] = Field(default_factory=list)
    path_params: list[KeyValueEntry] = Field(default_factory=list)
    body: BodyConfig = Field(default_factory=BodyConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    cookies: list[KeyValueEntry] = Field(default_factory=list)
    timeout: float = 30.0
    follow_redirects: bool = True
    verify_ssl: bool = True
