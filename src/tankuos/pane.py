"""Pane widget — a container for plugin content."""

from textual.widget import Widget
from textual.widgets import Static, Button
from textual.containers import Horizontal, Vertical
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
        border: solid $primary;
    }

    Pane:focus-within {
        border: solid $accent;
    }

    .pane-titlebar {
        height: 1;
        layout: horizontal;
        background: $primary;
        padding: 0;
    }

    .pane-title {
        width: 1fr;
        color: $accent;
        text-style: bold;
        padding-left: 1;
    }

    .pane-close {
        width: auto;
        height: 1;
        background: $primary;
        color: $error;
        border: none;
        padding: 0 1;
    }

    .pane-close:focus {
        background: $error;
        color: $surface;
    }

    .pane-close:hover {
        background: $error;
        color: $surface;
    }

    .pane-content {
        height: 1fr;
    }
    """

    def __init__(self, title: str, content: Widget, pane_id: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.pane_id = pane_id or f"pane-{id(self)}"
        self.title = title
        self.content_widget = content

    def compose(self) -> ComposeResult:
        with Horizontal(classes="pane-titlebar"):
            yield Static(self.title, classes="pane-title")
            yield Button("[x]", classes="pane-close", id=f"close-{self.pane_id}")
        yield self.content_widget

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Close button sends request to parent app."""
        if event.button.id == f"close-{self.pane_id}":
            self.post_message(ClosePaneRequest(self.pane_id))
