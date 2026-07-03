from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Checkbox, DataTable, Input, Label

from postmaster.models.request import KeyValueEntry


class KvTable(Vertical):
    def __init__(
        self,
        id: str = "kv-table",
        entries: list[KeyValueEntry] | None = None,
    ) -> None:
        super().__init__(id=id)
        self._entries = entries or [KeyValueEntry()]
        self._editing_row: int | None = None

    def compose(self) -> ComposeResult:
        with Horizontal(id="kv-header"):
            Label("Key", classes="col-header")
            Label("Value", classes="col-header")
            Label("Description", classes="col-header")
        for entry in self._entries:
            yield self._build_row(entry)

    def _build_row(self, entry: KeyValueEntry) -> DataTable:
        table = DataTable(classes="kv-row")
        table.add_columns("", "", "", "")
        table.add_row(
            "\u23bf",  # drag handle
            entry.key,
            entry.value,
            entry.description,
        )
        return table
