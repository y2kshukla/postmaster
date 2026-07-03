from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.events import MouseDown, MouseMove, MouseUp
from textual.widgets import Static


class HSplitter(Horizontal):
    DEFAULT_CSS = """
    HSplitter {
        height: 1;
        min-height: 1;
        background: #252526;
    }
    HSplitter:hover {
        background: #2d2d2d;
    }
    HSplitter.-dragging {
        background: #094771;
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
        self._dragging = False
        self._start_y = 0
        self._start_height = 0

    def compose(self) -> ComposeResult:
        yield Static("\u2501" * 12, id="hsplitter-grip")

    def on_mount(self) -> None:
        try:
            self._request_bar = self.screen.query_one("#request-bar")
        except Exception:
            self._request_bar = None

    def on_mouse_down(self, event: MouseDown) -> None:
        self._dragging = True
        self._start_y = event.screen_y
        if self._request_bar:
            self._start_height = self._request_bar.size.height
        self.capture_mouse()
        self.add_class("-dragging")

    def on_mouse_move(self, event: MouseMove) -> None:
        if self._dragging and self._request_bar:
            delta = event.screen_y - self._start_y
            new_height = max(2, min(15, self._start_height + delta))
            self._request_bar.styles.height = new_height

    def on_mouse_up(self, event: MouseUp) -> None:
        if self._dragging:
            self._dragging = False
            self.release_mouse()
            self.remove_class("-dragging")
