from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button, Label, Select, Static

from postmaster.models.environment import Environment


class TopBar(Horizontal):
    class TabSelected(Message):
        def __init__(self, tab: str) -> None:
            super().__init__()
            self.tab = tab

    def __init__(self, environments: list[Environment] | None = None) -> None:
        super().__init__(id="top-bar")
        self._environments = environments or [Environment(name="Default Environment")]

    def compose(self) -> ComposeResult:
        yield Static("Top Bar", classes="section-label")
        with Horizontal(id="tab-group"):
            yield Label("Design", classes="tab")
            yield Label("Debug", classes="tab tab-active")
        yield Static("HTTP Request", id="title-field")
        with Horizontal(id="action-group"):
            yield Button("Generate Data", id="gen-data-btn", classes="icon-btn")
            yield Select(
                [(e.name, e.id) for e in self._environments],
                value=self._environments[0].id if self._environments else "",
                id="env-select",
                prompt="Default Environment",
            )
            yield Button("\u2630", id="menu-btn", classes="icon-btn")
