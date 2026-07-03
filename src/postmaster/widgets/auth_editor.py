from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import ContentSwitcher, Input, Label, Select

from postmaster.models.request import (
    APIKeyConfig,
    AuthConfig,
    AuthType,
    BasicAuthConfig,
    BearerTokenConfig,
    OAuth2Config,
)
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

    def get_auth_config(self) -> AuthConfig:
        type_select = self.query_one("#auth-type-select", Select)
        auth_type = str(type_select.value) if type_select.value else "None"

        config = AuthConfig(type=AuthType(auth_type))

        if auth_type == "Bearer Token":
            config.bearer = BearerTokenConfig(
                token=self.query_one("#bearer-token", Input).value,
            )
        elif auth_type == "Basic Auth":
            config.basic = BasicAuthConfig(
                username=self.query_one("#basic-username", Input).value,
                password=self.query_one("#basic-password", Input).value,
            )
        elif auth_type == "API Key":
            add_to = self.query_one("#apikey-addto", Select)
            config.api_key = APIKeyConfig(
                key=self.query_one("#apikey-key", Input).value,
                value=self.query_one("#apikey-value", Input).value,
                add_to=str(add_to.value) if add_to.value else "Header",
            )
        elif auth_type == "OAuth 2.0":
            config.oauth2 = OAuth2Config(
                grant_type=str(self.query_one("#oauth2-grant", Select).value or ""),
                callback_url=self.query_one("#oauth2-callback", Input).value,
                auth_url=self.query_one("#oauth2-auth-url", Input).value,
                access_token_url=self.query_one("#oauth2-token-url", Input).value,
                client_id=self.query_one("#oauth2-client-id", Input).value,
                client_secret=self.query_one("#oauth2-client-secret", Input).value,
                scope=self.query_one("#oauth2-scope", Input).value,
            )

        return config

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
