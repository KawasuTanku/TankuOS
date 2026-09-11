"""Pane widget — a container for plugin content."""

from textual.widget import Widget
from textual.widgets import Static, Button
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
        border: solid $accent;
    }

    .title-bar {
        height: 1;
        layout: horizontal;
        background: $accent;
    }

    .title-bar Static {
        width: 1fr;
        height: 1;
        background: $accent;
        color: $surface;
        text-style: bold;
        padding-left: 1;
    }

    .title-bar Button {
        width: auto;
        height: 1;
        background: $accent;
        color: $surface;
        border: none;
        padding: 0 1;
    }

    .title-bar Button:hover {
        background: $error;
    }

    #content {
        height: 1fr;
        padding: 0;
    }
    """

    def __init__(self, title: str, content: Widget, pane_id: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.pane_id = pane_id or f"pane-{id(self)}"
        self.title = title
        self.content_widget = content

    def compose(self) -> ComposeResult:
        with Horizontal(classes="title-bar"):
            yield Static(f"{self.title}")
            yield Button("[x]")
        self.content_widget.add_class("pane-content")
        yield self.content_widget

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Close button sends request to parent app."""
        self.post_message(ClosePaneRequest(self.pane_id))
