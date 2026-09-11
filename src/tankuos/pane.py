"""Pane widget — a container for plugin content."""

from textual.widget import Widget
from textual.widgets import Static
from textual.app import ComposeResult
from textual.message import Message
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
        height: 1fr;
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
        yield Static("", id="titlebar")
        self.content_widget.add_class("pane-content")
        yield self.content_widget

    def on_mount(self) -> None:
        self._update_titlebar()

    def on_resize(self) -> None:
        self._update_titlebar()

    def _update_titlebar(self) -> None:
        width = self.size.width or 80
        text = Text()
        # Build title line: title + padding + [x]
        padding = max(0, width - len(self.title) - 4)
        text.append(" ")
        text.append(self.title, style="bold white on blue")
        text.append(" " * padding, style="on blue")
        text.append("[x]", style="bold red on blue")
        titlebar = self.query_one("#titlebar", Static)
        titlebar.update(text)

    def on_click(self, event):
        widget = event.widget
        if widget and widget.id == "titlebar":
            x = event.x
            width = self.size.width or 80
            if x >= width - 4:
                self.post_message(ClosePaneRequest(self.pane_id))

    def on_close_pane_request(self, message: ClosePaneRequest) -> None:
        if message.pane_id == self.pane_id:
            self.remove()
