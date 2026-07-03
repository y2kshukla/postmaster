from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import ContentSwitcher, Label, Static, TabPane, TabbedContent, Tabs

from postmaster.widgets.body_editor import BodyEditor
from postmaster.widgets.auth_editor import AuthEditor
from postmaster.widgets.kv_table import KvTable


class LeftPanel(Vertical):
    def __init__(self) -> None:
        super().__init__(id="left-panel")

    def compose(self) -> ComposeResult:
        yield Static("Left Panel", classes="section-label")
        with TabbedContent(initial="params", id="request-tabs"):
            with TabPane("Headers", id="headers"):
                with VerticalScroll():
                    yield KvTable(id="headers-table")
            with TabPane("Params", id="params"):
                with VerticalScroll():
                    yield KvTable(id="params-table")
            with TabPane("Path", id="path"):
                with VerticalScroll():
                    yield KvTable(id="path-table")
            with TabPane("Body", id="body"):
                with VerticalScroll():
                    yield BodyEditor()
            with TabPane("Auth", id="auth"):
                with VerticalScroll():
                    yield AuthEditor()
