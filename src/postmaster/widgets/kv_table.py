from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Label

from postmaster.models.request import KeyValueEntry


class KvRow(Horizontal):
    def __init__(self, entry: KeyValueEntry | None = None) -> None:
        super().__init__(classes="kv-row")
        self._entry = entry or KeyValueEntry()

    def compose(self) -> ComposeResult:
        yield Button("󰄬" if self._entry.enabled else "󰄱", classes="kv-enabled")
        yield Input(value=self._entry.key, placeholder="Key", classes="kv-key")
        yield Input(value=self._entry.value, placeholder="Value", classes="kv-value")
        yield Button("󰆴", classes="kv-remove")

    def get_entry(self) -> KeyValueEntry:
        inputs = self.query(Input)
        self._entry.key = inputs[0].value
        self._entry.value = inputs[1].value
        return self._entry

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.has_class("kv-enabled"):
            self._entry.enabled = not self._entry.enabled
            event.button.label = "󰄬" if self._entry.enabled else "󰄱"
        elif event.button.has_class("kv-remove"):
            siblings = list(self.parent.query(KvRow))
            if len(siblings) > 1:
                self.remove()


class KvTable(Vertical):
    def __init__(
        self,
        id: str = "kv-table",
        entries: list[KeyValueEntry] | None = None,
    ) -> None:
        super().__init__(id=id)
        self._entries = entries or [KeyValueEntry()]

    def compose(self) -> ComposeResult:
        with Horizontal(id="kv-header"):
            Label("", classes="kv-spacer")
            Label("Key", classes="col-header")
            Label("Value", classes="col-header")
            Label("", classes="kv-spacer")
        for entry in self._entries:
            yield KvRow(entry)
        yield Button("  Add", id="add-row-btn")

    def get_entries(self) -> list[KeyValueEntry]:
        return [row.get_entry() for row in self.query(KvRow) if row.get_entry().key.strip()]

    def add_row(self, entry: KeyValueEntry | None = None) -> None:
        row = KvRow(entry)
        self.mount(row, before=self.query_one("#add-row-btn"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add-row-btn":
            self.add_row()
