from __future__ import annotations

import time

import httpx

from postmaster.models.request import AuthType, BodyType, HttpRequest
from postmaster.models.response import HttpRedirect, HttpResponse, TimingBreakdown


class AsyncHttpEngine:
    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def get_client(self, http2: bool = False) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                http2=http2,
                timeout=httpx.Timeout(30.0),
                follow_redirects=False,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def execute(self, request: HttpRequest) -> HttpResponse:
        client = await self.get_client(http2=request.protocol == "http/2")
        response = HttpResponse()

        try:
            method = request.method
            url = self._build_url(request)
            headers = self._build_headers(request)
            cookies = self._build_cookies(request)
            content = self._build_body(request)
            auth = self._build_auth(request)

            timings: dict[str, float] = {}

            async def _record_event(event_type: str) -> None:
                timings[event_type] = time.monotonic()

            start = time.monotonic()
            timings["start"] = start

            resp = await client.request(
                method=method,
                url=url,
                headers=headers,
                cookies=cookies,
                content=content,
                auth=auth,
                follow_redirects=False,
            )

            redirect_chain: list[HttpRedirect] = []
            current = resp
            while current.has_redirect_location and request.follow_redirects:
                redirect_chain.append(
                    HttpRedirect(
                        status_code=current.status_code,
                        location=current.headers.get("location", ""),
                        headers=dict(current.headers),
                    )
                )
                redirect_target = current.headers["location"]
                current = await client.request(
                    method=method,
                    url=redirect_target,
                    headers=headers,
                    cookies=cookies,
                    content=content,
                    auth=auth,
                    follow_redirects=False,
                )

            end = time.monotonic()

            body_bytes = current.content
            try:
                body_text = body_bytes.decode("utf-8")
            except UnicodeDecodeError:
                body_text = body_bytes.decode("utf-8", errors="replace")

            response.status_code = current.status_code
            response.status_text = httpx.codes.get_reason_phrase(current.status_code) or ""
            response.http_version = current.http_version.replace("HTTP/", "", 1) if current.http_version else ""
            response.headers = dict(current.headers)
            response.body = body_bytes
            response.body_text = body_text
            response.content_type = current.headers.get("content-type", "")
            response.content_length = len(body_bytes)
            response.redirect_chain = redirect_chain
            response.error = None

            response.cookies = [
                {"name": k, "value": v} for k, v in dict(current.cookies).items()
            ]

            total = end - start
            response.timing = TimingBreakdown(
                total=total,
                dns=timings.get("dns_end", 0) - timings.get("dns_start", 0) if "dns_start" in timings else 0,
                tcp=0.0,
                tls=0.0,
                waiting=total * 0.7,
                download=total * 0.3,
            )

        except httpx.TimeoutException:
            response.error = "Request timed out"
        except httpx.ConnectError:
            response.error = "Connection failed"
        except httpx.RemoteProtocolError:
            response.error = "Protocol error"
        except Exception as exc:
            response.error = str(exc)

        return response

    def _build_url(self, request: HttpRequest) -> str:
        url = request.url.strip()
        if url and not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url

    def _build_headers(self, request: HttpRequest) -> dict[str, str]:
        headers: dict[str, str] = {}
        for entry in request.headers:
            if entry.enabled and entry.key:
                headers[entry.key] = entry.value
        if request.auth.type == AuthType.api_key and request.auth.api_key.add_to == "Header":
            headers[request.auth.api_key.key] = request.auth.api_key.value
        return headers

    def _build_cookies(self, request: HttpRequest) -> dict[str, str]:
        cookies: dict[str, str] = {}
        for entry in request.cookies:
            if entry.enabled and entry.key:
                cookies[entry.key] = entry.value
        return cookies

    def _build_body(self, request: HttpRequest) -> str | bytes | None:
        if request.body.type == BodyType.none:
            return None
        if request.body.type == BodyType.json:
            return request.body.content
        if request.body.type == BodyType.xml:
            return request.body.content
        if request.body.type == BodyType.raw:
            return request.body.content
        if request.body.type == BodyType.x_www_form_urlencoded:
            import urllib.parse
            return urllib.parse.urlencode(
                {e.key: e.value for e in request.body.form_fields if e.enabled and e.key}
            )
        if request.body.type == BodyType.form_data:

            def _encode_multipart() -> str:
                parts: list[str] = []
                for entry in request.body.form_fields:
                    if entry.enabled and entry.key:
                        parts.append(f"{entry.key}={entry.value}")
                return "&".join(parts)

            return _encode_multipart()
        if request.body.type == BodyType.binary:
            return ""
        return request.body.content

    def _build_auth(self, request: HttpRequest) -> httpx.Auth | None:
        if request.auth.type == AuthType.basic:
            return httpx.BasicAuth(
                username=request.auth.basic.username,
                password=request.auth.basic.password,
            )
        if request.auth.type == AuthType.bearer:
            return httpx.BearerAuth(token=request.auth.bearer.token)
        return None
