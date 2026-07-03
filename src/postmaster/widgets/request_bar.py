from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button, Input, Select

from postmaster.utils.constants import PROTOCOLS

from postmaster.widgets.method_dropdown import MethodDropdown


class RequestBar(Horizontal):
    class SendRequest(Message):
        def __init__(self) -> None:
            super().__init__()

    class SaveRequest(Message):
        def __init__(self) -> None:
            super().__init__()

    def __init__(self) -> None:
        super().__init__(id="request-bar")

    def compose(self) -> ComposeResult:
        yield MethodDropdown()
        yield Input(
            placeholder="Enter URL or paste cURL text",
            id="url-input",
        )
        yield Select(
            [(p, p) for p in PROTOCOLS],
            value="http/1.1",
            id="proto-select",
            allow_blank=False,
        )
        yield Button("Send", id="send-btn", variant="primary")
        yield Button("Save", id="save-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send-btn":
            self.post_message(self.SendRequest())
        elif event.button.id == "save-btn":
            self.post_message(self.SaveRequest())

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "url-input":
            self.post_message(self.SendRequest())

    def on_input_paste(self, event: Input.Paste) -> None:
        text = event.text.strip()
        if text.lower().startswith("curl"):
            from postmaster.engine.curl_parser import parse_curl
            parsed = parse_curl(text)
            if parsed:
                self.app.query_one("#method-dropdown", Select).value = parsed.method
                self.app.query_one("#url-input", Input).value = parsed.url
