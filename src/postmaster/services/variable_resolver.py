from __future__ import annotations

import re
from typing import Optional

from postmaster.models.environment import Environment
from postmaster.services.generators import get_generator

_VARIABLE_PATTERN = re.compile(r"\{\{(\$?\w[\w.]*)\}\}")


class VariableResolver:
    def __init__(self) -> None:
        self._local_variables: dict[str, str] = {}
        self._global_variables: dict[str, str] = {}

    def set_local(self, name: str, value: str) -> None:
        self._local_variables[name] = value

    def set_global(self, name: str, value: str) -> None:
        self._global_variables[name] = value

    def resolve(self, text: str, environment: Optional[Environment] = None) -> str:
        if not text:
            return text

        def _replace(match: re.Match) -> str:
            var_name = match.group(1)

            gen = get_generator(var_name)
            if gen:
                return gen()

            if var_name in self._local_variables:
                return self._local_variables[var_name]

            if var_name.startswith("env.") and environment:
                env_var = var_name[4:]
                for v in environment.variables:
                    if v.name == env_var:
                        return v.value

            if environment:
                for v in environment.variables:
                    if v.name == var_name:
                        return v.value

            if var_name in self._global_variables:
                return self._global_variables[var_name]

            return match.group(0)

        return _VARIABLE_PATTERN.sub(_replace, text)

    def resolve_request(
        self,
        url: str,
        headers: list[dict],
        body: str,
        environment: Optional[Environment] = None,
    ) -> tuple[str, list[dict], str]:
        resolved_url = self.resolve(url, environment)
        resolved_headers = []
        for h in headers:
            resolved_headers.append({
                "key": self.resolve(h.get("key", ""), environment),
                "value": self.resolve(h.get("value", ""), environment),
                "enabled": h.get("enabled", True),
            })
        resolved_body = self.resolve(body, environment)
        return resolved_url, resolved_headers, resolved_body
