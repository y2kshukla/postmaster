from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Select

from postmaster.widgets.left_panel import LeftPanel
from postmaster.widgets.request_bar import RequestBar
from postmaster.widgets.right_panel import RightPanel
from postmaster.widgets.sidebar import Sidebar
from postmaster.widgets.splitter import Splitter
from postmaster.widgets.status_bar import StatusBar
from postmaster.widgets.top_bar import TopBar


class MainScreen(Screen):
    BINDINGS = [
        ("ctrl+enter", "send_request", "Send"),
        ("ctrl+s", "save_request", "Save"),
        ("ctrl+b", "toggle_sidebar", "Sidebar"),
        ("ctrl+n", "toggle_section_names", "Names"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._http_engine = None
        self._sidebar_visible = False

    def compose(self) -> ComposeResult:
        yield TopBar()
        yield RequestBar()
        with Horizontal():
            yield Sidebar()
            yield LeftPanel()
            yield Splitter()
            yield RightPanel()
        yield StatusBar()

    def on_mount(self) -> None:
        sidebar = self.query_one(Sidebar)
        sidebar.display = False

    def on_request_bar_send_request(self, message: RequestBar.SendRequest) -> None:
        self.run_send_request()

    def on_request_bar_save_request(self, message: RequestBar.SaveRequest) -> None:
        self.notify("Request saved", severity="information", timeout=2)

    def run_send_request(self) -> None:
        request = self._build_request()
        if not request.url:
            self.notify("Please enter a URL", severity="error", timeout=3)
            return
        from postmaster.models.request import HttpRequest
        self.run_worker(self._execute_request(request), exclusive=True)

    async def _execute_request(self, request) -> None:
        from postmaster.engine.client import AsyncHttpEngine

        if self._http_engine is None:
            self._http_engine = AsyncHttpEngine()

        right_panel = self.query_one(RightPanel)
        switcher = right_panel.query_one("#response-switcher")
        switcher.current = "response-viewer"

        right_panel.query_one("#response-body").clear()
        right_panel.query_one("#response-body").write("[yellow]Sending request...[/]")

        response = await self._http_engine.execute(request)
        right_panel.display_response(response)

    def _build_request(self):
        from postmaster.models.request import HttpRequest

        method_select = self.query_one("#method-dropdown", Select)
        url_input = self.query_one("#url-input")
        proto_select = self.query_one("#proto-select", Select)

        request = HttpRequest(
            method=str(method_select.value) if method_select.value else "GET",
            url=url_input.value if hasattr(url_input, 'value') else "",
            protocol=str(proto_select.value) if proto_select.value else "http/1.1",
        )
        return request

    def action_send_request(self) -> None:
        self.run_send_request()

    def action_save_request(self) -> None:
        request = self._build_request()
        self.notify(f"Request saved: {request.method} {request.url or '(no URL)'}", timeout=2)

    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one(Sidebar)
        self._sidebar_visible = not self._sidebar_visible
        sidebar.display = self._sidebar_visible
        status = "opened" if self._sidebar_visible else "closed"
        self.notify(f"Collections {status}", timeout=1)

    def action_toggle_section_names(self) -> None:
        self.screen.toggle_class("show-section-names")
