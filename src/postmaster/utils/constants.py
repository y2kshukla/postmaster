from typing import Final

HTTP_METHODS: Final[list[str]] = [
    "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD",
]

PROTOCOLS: Final[list[str]] = ["http/1.1", "http/2"]

STATUS_TEXT: Final[dict[int, str]] = {
    200: "OK",
    201: "Created",
    204: "No Content",
    301: "Moved Permanently",
    302: "Found",
    304: "Not Modified",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    415: "Unsupported Media Type",
    422: "Unprocessable Entity",
    429: "Too Many Requests",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
}

BODY_TYPES: Final[list[str]] = [
    "none", "json", "xml", "form-data", "x-www-form-urlencoded", "raw", "binary",
]

AUTH_TYPES: Final[list[str]] = [
    "None", "Bearer Token", "Basic Auth", "API Key", "OAuth 2.0",
]
