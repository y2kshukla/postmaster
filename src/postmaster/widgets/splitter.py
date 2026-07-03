from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.events import MouseDown, MouseMove, MouseUp
from textual.message import Message
from textual.widgets import Button, Static


class Splitter(Vertical):
    class LeftPanelToggled(Message):
        def __init__(self, visible: bool) -> None:
            super().__init__()
            self.visible = visible

    DEFAULT_CSS = """
    Splitter {
        width: 3;
        min-width: 3;
        background: #252526;
        border-left: solid #3c3c3c;
    }
    Splitter:hover {
        background: #2d2d2d;
    }
    Splitter.-dragging {
        background: #094771;
    }
    #collapse-btn {
        width: 3;
        height: 3;
        min-width: 3;
        min-height: 3;
        background: transparent;
        border: none;
        color: #808080;
        text-style: bold;
    }
    #collapse-btn:hover {
        background: #383838;
        color: #cccccc;
    }
    """

    def __init__(self) -> None:
        super().__init__(id="splitter")
        self._dragging = False
        self._start_x = 0
        self._start_width = 0
        self._left_visible = True

    def compose(self) -> ComposeResult:
        yield Static("Splitter", classes="section-label")
        yield Button("\u25c0", id="collapse-btn")

    def on_mount(self) -> None:
        try:
            self._left_panel = self.screen.query_one("#left-panel")
        except Exception:
            self._left_panel = None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "collapse-btn":
            self._toggle_left_panel()

    def _toggle_left_panel(self) -> None:
        self._left_visible = not self._left_visible
        self._left_panel.display = self._left_visible
        btn = self.query_one("#collapse-btn")
        btn.label = "\u25c0" if self._left_visible else "\u25b6"
        self.post_message(self.LeftPanelToggled(self._left_visible))

    def on_mouse_down(self, event: MouseDown) -> None:
        self._dragging = True
        self._start_x = event.screen_x
        if self._left_panel and self._left_visible:
            self._start_width = self._left_panel.size.width
        self.capture_mouse()
        self.add_class("-dragging")

    def on_mouse_move(self, event: MouseMove) -> None:
        if self._dragging and self._left_panel and self._left_visible:
            delta = event.screen_x - self._start_x
            new_width = max(20, min(120, self._start_width + delta))
            self._left_panel.styles.width = new_width

    def on_mouse_up(self, event: MouseUp) -> None:
        if self._dragging:
            self._dragging = False
            self.release_mouse()
            self.remove_class("-dragging")
