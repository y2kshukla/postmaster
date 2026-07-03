from __future__ import annotations

from pathlib import Path

from textual.app import App

from postmaster.screens.main_screen import MainScreen
from postmaster.theme import DARK_THEME


class PostmasterApp(App):
    CSS_PATH = Path(__file__).parent / "theme.tcss"
    SCREENS = {"main": MainScreen}
    TITLE = "Postmaster"
    SUB_TITLE = "HTTP Client"

    def on_mount(self) -> None:
        self.register_theme(DARK_THEME)
        self.theme = "postmaster-dark"
        self.push_screen("main")
