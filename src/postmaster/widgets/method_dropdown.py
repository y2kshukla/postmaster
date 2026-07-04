from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Select

from postmaster.utils.constants import HTTP_METHODS


class MethodDropdown(Select):
    def __init__(
        self,
        *,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(
            [(m, m) for m in HTTP_METHODS],
            value="POST",
            id=id,
            classes=classes,
            allow_blank=False,
        )

    def on_mount(self) -> None:
        self.styles.min_width = 8
        self.styles.height = 3
        self.styles.padding = 0
