from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Button, Input, Label, Tree


class CollectionTree(Tree):
    pass


class Sidebar(Vertical):
    class RequestSelected(Message):
        def __init__(self, request) -> None:
            super().__init__()
            self.request = request

    def __init__(self) -> None:
        super().__init__(id="sidebar")

    def compose(self) -> ComposeResult:
        yield Label("Collections", id="sidebar-title")
        yield Input(placeholder="Search collections...", id="sidebar-search")
        yield CollectionTree("Collections", id="collection-tree")

    def on_mount(self) -> None:
        tree = self.query_one("#collection-tree", CollectionTree)
        tree.root.expand()
        default = tree.root.add("Default Collection")
        default.add("New Request")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        pass

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        node = event.node
        if node.data:
            self.post_message(self.RequestSelected(node.data))
