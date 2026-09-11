"""Pane widget — a container for plugin content."""

from textual.widget import Widget
from textual.widgets import Static
from textual.app import ComposeResult
from textual.message import Message
from rich.panel import Panel
from rich.text import Text
from rich import box


class ClosePaneRequest(Message):
    """Request to close a pane."""
    def __init__(self, pane_id: str) -> None:
        super().__init__()
        self.pane_id = pane_id


class PaneTitleBar(Static):
    """Title bar rendered as a Rich Panel for reliable background."""

    def __init__(self, title: str, pane_id: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.title = title
        self.pane_id = pane_id

    def render(self) -> Panel:
        width = self.size.width or 80
        text = Text()
        text.append(" ")
        text.append(self.title, style="bold")
        text.append(" " * max(0, width - len(self.title) - 4))
        text.append("[x]", style="bold red")
        return Panel(text, style="bold cyan on #1a1a40", box=box.SIMPLE, height=1, padding=(0, 0))

    def on_click(self, event):
        """Click on [x] closes pane."""
        x = event.x
        width = self.size.width or 80
        if x >= width - 3:
            self.post_message(ClosePaneRequest(self.pane_id))


class Pane(Widget):
    """A TankuOS pane — hosts a plugin widget with title bar."""

    CSS = """
    Pane {
        layout: vertical;
        height: 1fr;
        border: solid #22d3ee;
    }

    .title-bar {
        height: 1;
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
        yield PaneTitleBar(self.title, self.pane_id, classes="title-bar")
        self.content_widget.add_class("pane-content")
        yield self.content_widget

    def on_close_pane_request(self, message: ClosePaneRequest) -> None:
        if message.pane_id == self.pane_id:
            self.remove()
