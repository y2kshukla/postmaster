from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, ContentSwitcher, Label, Static, TabPane, TabbedContent, Tabs

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
                yield KvTable(id="headers-table")
                yield Button("Batch Edit", id="batch-edit-btn", classes="link-btn")
            with TabPane("Params", id="params"):
                yield KvTable(id="params-table")
                yield Button("Batch Edit", id="batch-edit-params", classes="link-btn")
            with TabPane("Path", id="path"):
                yield KvTable(id="path-table")
            with TabPane("Body", id="body"):
                yield BodyEditor()
            with TabPane("Auth", id="auth"):
                yield AuthEditor()
