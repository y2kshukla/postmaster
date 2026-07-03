import sys
sys.path.insert(0, 'src')

import pytest

from postmaster.engine.curl_parser import parse_curl
from postmaster.models.request import AuthType, BodyType, HttpRequest


class TestCurlParser:
    def test_simple_get(self):
        result = parse_curl("curl https://example.com")
        assert result is not None
        assert result.method == "GET"
        assert result.url == "https://example.com"

    def test_post_with_data(self):
        result = parse_curl("curl -X POST https://api.example.com -d 'name=test'")
        assert result is not None
        assert result.method == "POST"
        assert result.body.type == BodyType.raw
        assert result.body.content == "name=test"

    def test_with_headers(self):
        result = parse_curl(
            "curl -H 'Content-Type: application/json' -H 'Accept: */*' https://api.example.com"
        )
        assert result is not None
        assert len(result.headers) == 2
        assert result.headers[0].key == "Content-Type"
        assert result.headers[0].value == "application/json"

    def test_basic_auth(self):
        result = parse_curl("curl -u admin:secret https://api.example.com")
        assert result is not None
        assert result.auth.type == AuthType.basic
        assert result.auth.basic.username == "admin"
        assert result.auth.basic.password == "secret"

    def test_bearer_auth(self):
        result = parse_curl("curl --oauth2-bearer tok_xxx https://api.example.com")
        assert result is not None
        assert result.auth.type == AuthType.bearer
        assert result.auth.bearer.token == "tok_xxx"

    def test_insecure(self):
        result = parse_curl("curl -k https://example.com")
        assert result is not None
        assert result.verify_ssl is False

    def test_follow_redirects(self):
        result = parse_curl("curl -L https://example.com")
        assert result is not None
        assert result.follow_redirects is True

    def test_not_curl(self):
        result = parse_curl("echo hello")
        assert result is None

    def test_empty(self):
        result = parse_curl("")
        assert result is None
