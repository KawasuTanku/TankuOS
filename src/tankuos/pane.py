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

    .pane-titlebar {
        height: 1;
        layout: horizontal;
        background: $accent;
        padding: 0;
    }

    .pane-titlebar Static {
        width: 1fr;
        height: 1;
        color: $surface;
        text-style: bold;
        padding-left: 1;
    }

    .pane-titlebar Button {
        width: auto;
        height: 1;
        background: $accent;
        color: $surface;
        border: none;
        padding: 0 1;
    }

    .pane-titlebar Button:hover {
        background: $error;
    }
    """

    def __init__(self, title: str, content: Widget, pane_id: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.pane_id = pane_id or f"pane-{id(self)}"
        self.title = title
        self.content_widget = content

    def compose(self) -> ComposeResult:
        with Horizontal(classes="pane-titlebar"):
            yield Static(self.title)
            yield Button("[x]", id=f"close-{self.pane_id}")
        yield self.content_widget

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Close button sends request to parent app."""
        if event.button.id == f"close-{self.pane_id}":
            self.post_message(ClosePaneRequest(self.pane_id))
