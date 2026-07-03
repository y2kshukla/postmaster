from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static


class HSplitter(Horizontal):
    DEFAULT_CSS = """
    HSplitter {
        height: 1;
        min-height: 1;
        background: #252526;
    }
    #hsplitter-grip {
        width: 12;
        height: 1;
        color: #808080;
        content-align: center middle;
        text-style: bold;
    }
    """

    def __init__(self) -> None:
        super().__init__(id="hsplitter")

    def compose(self) -> ComposeResult:
        yield Static("\u2501" * 12, id="hsplitter-grip")

    def on_mount(self) -> None:
        # Keep the separator decorative only. The request bar should remain a
        # compact, fixed-height control row so it cannot be accidentally dragged
        # into a large blank spacer between the request controls and panels.
        self.styles.cursor = "default"
