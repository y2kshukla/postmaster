from __future__ import annotations

import random
import string
import time
import uuid
from typing import Callable

_BUILTIN_GENERATORS: dict[str, Callable[[], str]] = {}


def _register(name: str) -> Callable:
    def decorator(fn: Callable[[], str]) -> Callable:
        _BUILTIN_GENERATORS[name] = fn
        return fn
    return decorator


@_register("$uuid")
def _uuid() -> str:
    return uuid.uuid4().hex


@_register("$guid")
def _guid() -> str:
    return str(uuid.uuid4()).upper()


@_register("$timestamp")
def _timestamp() -> str:
    return str(int(time.time()))


@_register("$isoTimestamp")
def _iso_timestamp() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


@_register("$randomInt")
def _random_int() -> str:
    return str(random.randint(1, 999999))


@_register("$randomEmail")
def _random_email() -> str:
    domains = ["example.com", "test.org", "mail.net"]
    name = "".join(random.choices(string.ascii_lowercase, k=8))
    return f"{name}{random.randint(1, 999)}@{random.choice(domains)}"


@_register("$randomString")
def _random_string() -> str:
    length = random.randint(6, 16)
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


@_register("$randomName")
def _random_name() -> str:
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace"]
    last_names = ["Smith", "Jones", "Brown", "Davis", "Wilson", "Taylor"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


@_register("$randomPhone")
def _random_phone() -> str:
    return f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"


@_register("$randomBool")
def _random_bool() -> str:
    return random.choice(["true", "false"])


def get_generator(name: str) -> Callable[[], str] | None:
    return _BUILTIN_GENERATORS.get(name)
