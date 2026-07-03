from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import RichLog, Select

from postmaster.widgets.action_panel import ActionPanel
from postmaster.widgets.auth_editor import AuthEditor
from postmaster.widgets.body_editor import BodyEditor
from postmaster.widgets.kv_table import KvRow, KvTable
from postmaster.widgets.request_bar import RequestBar
from postmaster.widgets.right_panel import RightPanel
from postmaster.widgets.sidebar import Sidebar
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
        yield ActionPanel()
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

        actual_text = self._format_request(request)
        actual_log = right_panel.query_one("#actual-request-log", RichLog)
        actual_log.clear()
        actual_log.write(actual_text)

        right_panel._actual_request_text = actual_text

        response = await self._http_engine.execute(request)
        right_panel.display_response(response)

    def _build_request(self):
        from postmaster.models.request import HttpRequest

        method_select = self.query_one("#method-dropdown", Select)
        url_input = self.query_one("#url-input")
        proto_select = self.query_one("#proto-select", Select)

        right_panel = self.query_one(RightPanel)
        right_panel.clear_console()

        params_table = self.query_one("#params-table", KvTable)
        params_rows = list(params_table.query(KvRow))
        right_panel.write_console(f"[yellow]Params KvRow count:[/] {len(params_rows)}")
        params_entries = params_table.get_entries()
        right_panel.write_console(f"[yellow]Params entries returned:[/] {len(params_entries)}")
        for p in params_entries:
            right_panel.write_console(f"  [cyan]{p.key}[/] = [green]{p.value}[/]")

        path_table = self.query_one("#path-table", KvTable)
        path_rows = list(path_table.query(KvRow))
        right_panel.write_console(f"[yellow]Path KvRow count:[/] {len(path_rows)}")
        path_entries = path_table.get_entries()
        right_panel.write_console(f"[yellow]Path entries returned:[/] {len(path_entries)}")
        for p in path_entries:
            right_panel.write_console(f"  [cyan]{p.key}[/] = [green]{p.value}[/]")

        request = HttpRequest(
            method=str(method_select.value) if method_select.value else "GET",
            url=url_input.value if hasattr(url_input, 'value') else "",
            protocol=str(proto_select.value) if proto_select.value else "http/1.1",
            headers=self.query_one("#headers-table", KvTable).get_entries(),
            query_params=params_entries,
            path_params=path_entries,
            body=self.query_one(BodyEditor).get_body_config(),
            auth=self.query_one(AuthEditor).get_auth_config(),
        )
        right_panel.write_console(f"[yellow]Final URL:[/] {request.url}")
        right_panel.write_console(f"[yellow]Query params count:[/] {len(request.query_params)}")
        right_panel.write_console(f"[yellow]Path params count:[/] {len(request.path_params)}")
        return request

    def _format_request(self, request) -> str:
        lines = [
            f"[bold]{request.method}[/] [cyan]{request.url}[/] [dim]{request.protocol}[/]"
        ]

        headers = [h for h in request.headers if h.enabled and h.key]
        if headers:
            lines.append("")
            lines.append("[underline]Headers[/]")
            for h in headers:
                lines.append(f"  [dim]{h.key}:[/] {h.value}")

        params = [p for p in request.query_params if p.enabled and p.key]
        if params:
            lines.append("")
            lines.append("[underline]Query Params[/]")
            for p in params:
                lines.append(f"  {p.key} = {p.value}")

        path = [p for p in request.path_params if p.enabled and p.key]
        if path:
            lines.append("")
            lines.append("[underline]Path Params[/]")
            for p in path:
                lines.append(f"  {p.key} = {p.value}")

        if request.body.content:
            lines.append("")
            lines.append(f"[underline]Body ({request.body.type.value})[/]")
            lines.append(request.body.content)

        if request.auth.type.value != "None":
            lines.append("")
            lines.append(f"[underline]Auth ({request.auth.type.value})[/]")

        return "\n".join(lines)

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
