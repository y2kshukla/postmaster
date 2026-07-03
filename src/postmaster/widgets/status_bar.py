from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Label

from postmaster.models.response import HttpResponse


class StatusBar(Horizontal):
    def __init__(self) -> None:
        super().__init__(id="status-bar")

    def compose(self) -> ComposeResult:
        yield Label("", id="status-timing", classes="stat")
        yield Label("", id="status-size", classes="stat")
        yield Label("", id="status-code", classes="stat")
        yield Label("", id="status-version", classes="stat")

    def update_status(self, response: HttpResponse) -> None:
        timing = response.timing
        timing_text = f"{timing.total*1000:.0f}ms" if timing.total > 0 else ""
        self.query_one("#status-timing", Label).update(timing_text)

        size_text = ""
        if response.content_length:
            if response.content_length > 1024 * 1024:
                size_text = f"{response.content_length / (1024*1024):.1f}MB"
            elif response.content_length > 1024:
                size_text = f"{response.content_length / 1024:.1f}KB"
            else:
                size_text = f"{response.content_length}B"
        self.query_one("#status-size", Label).update(size_text)

        code_text = f"{response.status_code} {response.status_text}" if response.status_code else ""
        code_widget = self.query_one("#status-code", Label)
        code_widget.update(code_text)
        if response.status_code >= 400:
            code_widget.styles.color = "#f44747"
        elif response.status_code >= 300:
            code_widget.styles.color = "#cca700"
        else:
            code_widget.styles.color = "#ffffff"

        self.query_one("#status-version", Label).update(response.http_version)
