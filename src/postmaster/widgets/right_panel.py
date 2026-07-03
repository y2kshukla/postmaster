from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import ContentSwitcher, DataTable, Label, RichLog, TabPane, TabbedContent


class RightPanel(Vertical):
    def __init__(self) -> None:
        super().__init__(id="right-panel")
        self._current_response = None

    def compose(self) -> ComposeResult:
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
                        id="response-viewer",
                    )
            with TabPane("Headers", id="headers-pane"):
                yield DataTable(id="response-headers-table")
            with TabPane("Cookie", id="cookie-pane"):
                yield DataTable(id="response-cookies-table")
            with TabPane("Actual Request", id="actual-pane"):
                yield RichLog(id="actual-request-log", markup=True)
            with TabPane("Console", id="console-pane"):
                yield RichLog(id="console-log", markup=True)

    def on_mount(self) -> None:
        self.query_one("#response-headers-table", DataTable).add_columns("Key", "Value")
        self.query_one("#response-cookies-table", DataTable).add_columns("Name", "Value", "Domain", "Path")

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
