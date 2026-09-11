"""Pane widget — a container for plugin content."""

from textual.widget import Widget
from textual.widgets import Static
from textual.app import ComposeResult
from textual.message import Message

from tankuos.theme import theme


class ClosePaneRequest(Message):
    """Request to close a pane."""
    def __init__(self, pane_id: str) -> None:
        super().__init__()
        self.pane_id = pane_id


class PaneTitleBar(Static):
    """Title bar with inline close button."""
    
    def __init__(self, title: str, pane_id: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.title = title
        self.pane_id = pane_id
        self.add_class("pane-titlebar")

    def render(self):
        p = theme.palette
        width = self.size.width or 80
        title_text = f"{self.title:<{width - 5}}[x]"
        return f"[{p.accent_primary}]{title_text}[/{p.accent_primary}]"

    def on_click(self, event):
        """Click on [x] closes pane."""
        x = event.x
        width = self.size.width or 80
        if x >= width - 4:
            self.post_message(ClosePaneRequest(self.pane_id))


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
        background: $accent;
        color: $surface;
        text-style: bold;
    }
    """

    def __init__(self, title: str, content: Widget, pane_id: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.pane_id = pane_id or f"pane-{id(self)}"
        self.title = title
        self.content_widget = content

    def compose(self) -> ComposeResult:
        yield PaneTitleBar(self.title, self.pane_id)
        yield self.content_widget

    def on_close_pane_request(self, message: ClosePaneRequest) -> None:
        """Handle close request from title bar click."""
        if message.pane_id == self.pane_id:
            self.remove()
