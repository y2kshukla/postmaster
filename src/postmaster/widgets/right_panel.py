from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, ContentSwitcher, DataTable, Label, RichLog, Static, TabPane, TabbedContent


class RightPanel(Vertical):
    def __init__(self) -> None:
        super().__init__(id="right-panel")
        self._current_response = None
        self._actual_request_text: str = ""
        self._console_text: str = ""

    def compose(self) -> ComposeResult:
        yield Static("Right Panel", classes="section-label")
        with TabbedContent(initial="response", id="response-tabs"):
            with TabPane("Response", id="response"):
                with ContentSwitcher(initial="empty", id="response-switcher"):
                    yield Vertical(
                        Label("\U0001F989", id="owl-icon"),
                        Label("Enter the URL and click Send to get a response"),
                        Label("or import a cURL command"),
                        id="response-empty",
                    )
                    yield Vertical(
                        RichLog(id="response-body", highlight=True, markup=True),
                        Button("Copy", id="copy-response-btn", classes="copy-btn"),
                        id="response-viewer",
                    )
            with TabPane("Headers", id="headers-pane"):
                yield DataTable(id="response-headers-table")
            with TabPane("Cookie", id="cookie-pane"):
                yield DataTable(id="response-cookies-table")
            with TabPane("Actual Request", id="actual-pane"):
                yield Vertical(
                    RichLog(id="actual-request-log", markup=True),
                    Button("Copy", id="copy-request-btn", classes="copy-btn"),
                    id="actual-request-viewer",
                )
            with TabPane("Console", id="console-pane"):
                yield Vertical(
                    RichLog(id="console-log", markup=True),
                    Button("Copy", id="copy-console-btn", classes="copy-btn"),
                    id="console-viewer",
                )

    def on_mount(self) -> None:
        self.query_one("#response-headers-table", DataTable).add_columns("Key", "Value")
        self.query_one("#response-cookies-table", DataTable).add_columns("Name", "Value", "Domain", "Path")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        import pyperclip

        if event.button.id == "copy-response-btn":
            if self._current_response and self._current_response.body_text:
                pyperclip.copy(self._current_response.body_text)
                self.app.notify("Response copied to clipboard", timeout=2)
        elif event.button.id == "copy-request-btn":
            if self._actual_request_text:
                pyperclip.copy(self._actual_request_text)
                self.app.notify("Request copied to clipboard", timeout=2)
        elif event.button.id == "copy-console-btn":
            if self._console_text:
                pyperclip.copy(self._console_text)
                self.app.notify("Console copied to clipboard", timeout=2)

    def write_console(self, text: str) -> None:
        if self._console_text:
            self._console_text += "\n" + text
        else:
            self._console_text = text
        self.query_one("#console-log", RichLog).write(text)

    def clear_console(self) -> None:
        self._console_text = ""
        self.query_one("#console-log", RichLog).clear()

    def display_response(self, response) -> None:
        from postmaster.models.response import HttpResponse
        self._current_response = response

        switcher = self.query_one("#response-switcher", ContentSwitcher)
        switcher.current = "response-viewer"

        body_widget = self.query_one("#response-body", RichLog)
        body_widget.clear()

        if response.error:
            body_widget.write(f"[red]Error: {response.error}[/]")
            return

        content_type = response.content_type.lower() if response.content_type else ""

        if "json" in content_type:
            try:
                import json
                parsed = json.loads(response.body_text)
                pretty = json.dumps(parsed, indent=2)
                from rich.syntax import Syntax
                body_widget.write(Syntax(pretty, "json", theme="monokai"))
            except (json.JSONDecodeError, ValueError):
                body_widget.write(response.body_text)
        elif "xml" in content_type:
            body_widget.write(response.body_text)
        elif "html" in content_type:
            body_widget.write(response.body_text)
        else:
            body_widget.write(response.body_text)

        headers_table = self.query_one("#response-headers-table", DataTable)
        headers_table.clear()
        for key, value in response.headers.items():
            headers_table.add_row(key, value)

        cookies_table = self.query_one("#response-cookies-table", DataTable)
        cookies_table.clear()
        for cookie in response.cookies:
            cookies_table.add_row(
                cookie.get("name", ""),
                cookie.get("value", ""),
                cookie.get("domain", ""),
                cookie.get("path", ""),
            )

        try:
            status_bar = self.app.query_one("#status-bar")
            status_bar.update_status(response)
        except Exception:
            pass
