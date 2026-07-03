import sys
sys.path.insert(0, 'src')

import json

from postmaster.models.request import (
    AuthConfig, AuthType, BasicAuthConfig, BearerTokenConfig,
    BodyConfig, BodyType, HttpRequest, KeyValueEntry,
)
from postmaster.models.response import HttpResponse, TimingBreakdown
from postmaster.models.collection import Collection, Folder, RequestItem
from postmaster.models.environment import Environment, EnvironmentVariable


class TestHttpRequest:
    def test_defaults(self):
        req = HttpRequest()
        assert req.method == "POST"
        assert req.url == ""
        assert req.protocol == "http/1.1"
        assert len(req.headers) == 0
        assert req.body.type == BodyType.none
        assert req.auth.type == AuthType.none

    def test_serialization(self):
        req = HttpRequest(method="GET", url="https://example.com")
        data = json.loads(req.model_dump_json())
        assert data["method"] == "GET"
        assert data["url"] == "https://example.com"

    def test_with_headers(self):
        req = HttpRequest(
            headers=[
                KeyValueEntry(key="Content-Type", value="application/json"),
                KeyValueEntry(key="Authorization", value="Bearer test", enabled=False),
            ]
        )
        assert len(req.headers) == 2
        assert req.headers[0].key == "Content-Type"
        assert req.headers[0].enabled is True
        assert req.headers[1].enabled is False


class TestHttpResponse:
    def test_defaults(self):
        resp = HttpResponse()
        assert resp.status_code == 0
        assert resp.body == b""
        assert resp.timing.total == 0.0

    def test_with_data(self):
        resp = HttpResponse(
            status_code=200,
            status_text="OK",
            body_text='{"ok": true}',
            headers={"content-type": "application/json"},
            timing=TimingBreakdown(total=0.245),
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/json"
        assert resp.timing.total == 0.245


class TestCollection:
    def test_defaults(self):
        col = Collection()
        assert col.name == "New Collection"
        assert len(col.items) == 0
        assert len(col.variables) == 0

    def test_with_items(self):
        req = RequestItem(name="Test Request")
        folder = Folder(name="Test Folder", items=[req])
        col = Collection(name="API", items=[folder])
        assert col.name == "API"
        assert len(col.items) == 1

    def test_serialization_roundtrip(self):
        req = RequestItem(name="Get Users", request=HttpRequest(method="GET", url="/users"))
        col = Collection(name="My API", items=[req])
        data = json.loads(col.model_dump_json())
        restored = Collection.model_validate(data)
        assert restored.name == "My API"
        assert restored.items[0].name == "Get Users"


class TestEnvironment:
    def test_defaults(self):
        env = Environment()
        assert env.name == "Default Environment"
        assert len(env.variables) == 0

    def test_with_variables(self):
        env = Environment(
            name="Production",
            variables=[
                EnvironmentVariable(name="base_url", value="https://api.example.com"),
                EnvironmentVariable(name="token", value="secret123", secret=True),
            ],
        )
        assert len(env.variables) == 2
        assert env.variables[0].name == "base_url"
        assert env.variables[1].secret is True


class TestAuthConfig:
    def test_basic_auth(self):
        auth = AuthConfig(
            type=AuthType.basic,
            basic=BasicAuthConfig(username="admin", password="pass"),
        )
        assert auth.basic.username == "admin"

    def test_bearer(self):
        auth = AuthConfig(
            type=AuthType.bearer,
            bearer=BearerTokenConfig(token="tok_xxx"),
        )
        assert auth.bearer.token == "tok_xxx"


class TestBodyConfig:
    def test_json_body(self):
        body = BodyConfig(type=BodyType.json, content='{"key": "value"}')
        assert body.type == BodyType.json
        assert body.content == '{"key": "value"}'

    def test_form_fields(self):
        body = BodyConfig(
            type=BodyType.form_data,
            form_fields=[
                KeyValueEntry(key="file", value="test.txt"),
            ],
        )
        assert len(body.form_fields) == 1
        assert body.form_fields[0].key == "file"
