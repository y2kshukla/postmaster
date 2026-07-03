from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import ContentSwitcher, Input, Label, Select

from postmaster.utils.constants import AUTH_TYPES


class AuthEditor(Vertical):
    def __init__(self, id: str = "auth-editor") -> None:
        super().__init__(id=id)

    def compose(self) -> ComposeResult:
        yield Select(
            [(t, t) for t in AUTH_TYPES],
            value="None",
            id="auth-type-select",
            prompt="Auth Type",
        )
        with ContentSwitcher(initial="none", id="auth-config"):
            yield Label("No authentication", id="none")
            with Vertical(id="bearer"):
                yield Label("Token")
                yield Input(placeholder="Enter bearer token", id="bearer-token", classes="auth-input")
            with Vertical(id="basic"):
                yield Label("Username")
                yield Input(placeholder="Username", id="basic-username", classes="auth-input")
                yield Label("Password")
                yield Input(placeholder="Password", id="basic-password", password=True, classes="auth-input")
            with Vertical(id="api-key"):
                yield Label("Key")
                yield Input(placeholder="API Key name", id="apikey-key", classes="auth-input")
                yield Label("Value")
                yield Input(placeholder="API Key value", id="apikey-value", classes="auth-input")
                yield Label("Add to")
                yield Select([("Header", "Header"), ("Query Params", "Query Params")], value="Header", id="apikey-addto")
            with Vertical(id="oauth2"):
                yield Label("Grant Type")
                yield Select(
                    [("Authorization Code", "authorization_code"), ("Client Credentials", "client_credentials"),
                     ("Password", "password"), ("Implicit", "implicit")],
                    value="authorization_code",
                    id="oauth2-grant",
                )
                yield Label("Callback URL")
                yield Input(id="oauth2-callback", classes="auth-input")
                yield Label("Auth URL")
                yield Input(id="oauth2-auth-url", classes="auth-input")
                yield Label("Access Token URL")
                yield Input(id="oauth2-token-url", classes="auth-input")
                yield Label("Client ID")
                yield Input(id="oauth2-client-id", classes="auth-input")
                yield Label("Client Secret")
                yield Input(id="oauth2-client-secret", password=True, classes="auth-input")
                yield Label("Scope")
                yield Input(id="oauth2-scope", classes="auth-input")

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "auth-type-select":
            switcher = self.query_one("#auth-config", ContentSwitcher)
            mapping = {
                "None": "none",
                "Bearer Token": "bearer",
                "Basic Auth": "basic",
                "API Key": "api-key",
                "OAuth 2.0": "oauth2",
            }
            switcher.current = mapping.get(event.value, "none")
