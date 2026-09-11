"""Pane widget — a container for plugin content."""

from textual.widget import Widget
from textual.widgets import Static
from textual.app import ComposeResult
from textual.message import Message
from rich.panel import Panel
from rich.text import Text


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

    #titlebar {
        height: 1;
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
        title_text = Text()
        title_text.append(" ")
        title_text.append(self.title, style="bold")
        title_text.append(" ")
        title_text.append("[x]", style="bold red")
        yield Static(title_text, id="titlebar")
        self.content_widget.add_class("pane-content")
        yield self.content_widget

    def on_click(self, event):
        """Click on titlebar [x] closes pane."""
        widget = event.widget
        if widget and widget.parent is self:
            x = event.x
            width = self.size.width or 80
            if x >= width - 3:
                self.post_message(ClosePaneRequest(self.pane_id))
