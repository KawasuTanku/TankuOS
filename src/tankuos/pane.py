"""Pane widget — a container for plugin content."""

from textual.widget import Widget
from textual.widgets import Static, Header, Button
from textual.containers import Horizontal
from textual.app import ComposeResult
from textual.message import Message


class ClosePaneRequest(Message):
    """Request to close a pane."""
    def __init__(self, pane_id: str) -> None:
        super().__init__()
        self.pane_id = pane_id


class Pane(Widget):
    """A TankuOS pane — hosts a plugin widget with title bar."""

    CSS = """
    Pane {
        layout: vertical;
        height: 1fr;
        border: solid #22d3ee;
    }

    #titlebar {
        height: 1;
        background: #1a1a40;
    }

    #ttl {
        width: 1fr;
        color: white;
        text-style: bold;
    }

    #cls {
        width: auto;
        background: #1a1a40;
        color: #ff5555;
        border: none;
    }

    #cls:hover {
        background: #ff5555;
        color: white;
    }

    #content {
        height: 1fr;
    }
    """

    def __init__(self, title: str, content: Widget, pane_id: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.pane_id = pane_id or f"pane-{id(self)}"
        self.title = title
        self.content_widget = content

    def compose(self) -> ComposeResult:
        with Horizontal(id="titlebar"):
            yield Static(self.title, id="ttl")
            yield Button("[x]", id="cls")
        self.content_widget.add_class("pane-content")
        yield self.content_widget

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Close button sends request to parent app."""
        self.post_message(ClosePaneRequest(self.pane_id))
