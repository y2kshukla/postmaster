from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.events import MouseDown, MouseMove, MouseUp
from textual.widgets import Static

from postmaster.widgets.left_panel import LeftPanel
from postmaster.widgets.right_panel import RightPanel
from postmaster.widgets.sidebar import Sidebar
from postmaster.widgets.splitter import Splitter


class ActionPanel(Vertical):
    DEFAULT_CSS = """
    ActionPanel {
        height: 1fr;
    }
    #action-grip {
        height: 1;
        min-height: 1;
        background: #252526;
        color: #808080;
        content-align: center middle;
        text-style: bold;
    }
    #action-grip:hover {
        background: #2d2d2d;
    }
    ActionPanel.-dragging #action-grip {
        background: #094771;
    }
    #content-horizontal {
        height: 1fr;
    }
    """

    def __init__(self) -> None:
        super().__init__(id="action-panel")
        self._dragging = False
        self._start_y = 0
        self._start_height = 0

    def compose(self) -> ComposeResult:
        yield Static("Action Panel", classes="section-label")
        yield Static(" \u2509 " * 6, id="action-grip")
        with Horizontal(id="content-horizontal"):
            yield Sidebar()
            yield LeftPanel()
            yield Splitter()
            yield RightPanel()

    def on_mouse_down(self, event: MouseDown) -> None:
        if event.widget is not None and event.widget.id == "action-grip":
            self._dragging = True
            self._start_y = event.screen_y
            self._start_height = self.size.height
            self.capture_mouse()
            self.add_class("-dragging")

    def on_mouse_move(self, event: MouseMove) -> None:
        if self._dragging:
            delta = event.screen_y - self._start_y
            new_height = max(10, self._start_height + delta)
            self.styles.height = new_height

    def on_mouse_up(self, event: MouseUp) -> None:
        if self._dragging:
            self._dragging = False
            self.release_mouse()
            self.remove_class("-dragging")
