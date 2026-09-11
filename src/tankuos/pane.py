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
        layout: vertical;
        height: 1fr;
        border: solid #ff5555;
        padding: 1;
    }

    #titlebar {
        height: 1;
        background: #1a1a40;
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
        """Set title bar content after mount."""
        self._update_titlebar()

    def on_resize(self) -> None:
        """Update title bar on resize."""
        self._update_titlebar()

    def _update_titlebar(self) -> None:
        """Render title bar with Rich Text."""
        width = self.size.width or 80
        padding = max(0, width - len(self.title) - 4)
        text = Text()
        text.append(" ")
        text.append(self.title, style="bold white")
        text.append(" " * padding)
        text.append("[x]", style="bold red")
        text.stylize("on #1a1a40")
        titlebar = self.query_one("#titlebar", Static)
        titlebar.update(text)

    def on_click(self, event):
        """Click on titlebar [x] closes pane."""
        widget = event.widget
        if widget and widget.id == "titlebar":
            x = event.x
            width = self.size.width or 80
            if x >= width - 3:
                self.post_message(ClosePaneRequest(self.pane_id))

    def on_close_pane_request(self, message: ClosePaneRequest) -> None:
        if message.pane_id == self.pane_id:
            self.remove()
