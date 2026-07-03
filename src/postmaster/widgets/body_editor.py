from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Select, TextArea

from postmaster.utils.constants import BODY_TYPES


class BodyEditor(Vertical):
    def __init__(self, id: str = "body-editor") -> None:
        super().__init__(id=id)

    def compose(self) -> ComposeResult:
        yield Select(
            [(t.upper(), t) for t in BODY_TYPES],
            value="none",
            id="body-type-select",
            prompt="Body Type",
        )
        yield TextArea(
            id="body-content",
            language="json",
            show_line_numbers=True,
        )

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "body-type-select":
            body_type = event.value
            editor = self.query_one("#body-content", TextArea)
            if body_type == "json":
                editor.language = "json"
                editor.text = "{\n  \n}"
            elif body_type == "xml":
                editor.language = "xml"
                editor.text = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<root>\n  \n</root>"
            elif body_type == "none":
                editor.text = ""
            else:
                editor.language = None
                editor.text = ""
