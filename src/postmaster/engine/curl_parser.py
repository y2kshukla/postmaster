from __future__ import annotations

import shlex

from postmaster.models.request import AuthConfig, AuthType, BodyConfig, BodyType, HttpRequest, KeyValueEntry


def parse_curl(text: str) -> HttpRequest | None:
    text = text.strip()
    if not text.lower().startswith("curl"):
        return None

    try:
        tokens = shlex.split(text)
    except ValueError:
        return None

    if not tokens:
        return None

    request = HttpRequest()

    request.method = "GET"
    i = 1

    while i < len(tokens):
        token = tokens[i]

        if token in ("-X", "--request"):
            i += 1
            if i < len(tokens):
                request.method = tokens[i].upper()
        elif token in ("-H", "--header"):
            i += 1
            if i < len(tokens):
                header = tokens[i]
                if ":" in header:
                    key, _, value = header.partition(":")
                    request.headers.append(
                        KeyValueEntry(key=key.strip(), value=value.strip(), enabled=True)
                    )
        elif token in ("-d", "--data", "--data-raw"):
            i += 1
            if i < len(tokens):
                if request.method == "GET":
                    request.method = "POST"
                request.body.type = BodyType.raw
                request.body.content = tokens[i]
        elif token == "--data-binary":
            i += 1
            if i < len(tokens):
                if request.method == "GET":
                    request.method = "POST"
                request.body.type = BodyType.binary
                request.body.content = tokens[i]
        elif token in ("-u", "--user"):
            i += 1
            if i < len(tokens):
                userinfo = tokens[i]
                request.auth.type = AuthType.basic
                if ":" in userinfo:
                    username, _, password = userinfo.partition(":")
                    request.auth.basic.username = username
                    request.auth.basic.password = password
                else:
                    request.auth.basic.username = userinfo
        elif token == "--oauth2-bearer":
            i += 1
            if i < len(tokens):
                request.auth.type = AuthType.bearer
                request.auth.bearer.token = tokens[i]
        elif token in ("-k", "--insecure"):
            request.verify_ssl = False
        elif token in ("-L", "--location"):
            request.follow_redirects = True
        elif token == "--connect-timeout":
            i += 1
            if i < len(tokens):
                try:
                    request.timeout = float(tokens[i])
                except ValueError:
                    pass
        elif not token.startswith("-"):
            request.url = token
        i += 1

    return request
