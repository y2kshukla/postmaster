from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Select

from postmaster.utils.constants import HTTP_METHODS


class MethodDropdown(Select):
    def __init__(self) -> None:
        options = [(m, m) for m in HTTP_METHODS]
        super().__init__(options, value="POST", id="method-dropdown", allow_blank=False)

    def on_mount(self) -> None:
        self.styles.min_width = 8
