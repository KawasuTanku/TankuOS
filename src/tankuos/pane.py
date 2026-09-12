"""Pane widget - a container for plugin content."""

from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Vertical
from textual.app import ComposeResult
from textual.message import Message
from rich.text import Text


class ClosePaneRequest(Message):
    """Request to close a pane."""
    def __init__(self, pane_id: str) -> None:
        super().__init__()
        self.pane_id = pane_id


class Pane(Vertical):
    """A TankuOS pane - title bar + content."""

    CSS = """
    Pane {
        height: 1fr;
    }
    """

    can_focus = True

    def __init__(self, title: str, content: Widget, pane_id: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.pane_id = pane_id or f"pane-{id(self)}"
        self.title = title
        self.content_widget = content
        self._is_focused = False

    def compose(self) -> ComposeResult:
        yield Static("", id="titlebar")
        self.content_widget.add_class("pane-content")
        yield self.content_widget

    def on_mount(self) -> None:
        self._update_titlebar()

    def on_resize(self) -> None:
        self._update_titlebar()

    def set_focused(self, value: bool) -> None:
        """Set focus state and update visuals."""
        self._is_focused = value
        self._update_titlebar()

    def _update_titlebar(self) -> None:
        try:
            titlebar = self.query_one("#titlebar", Static)
            width = self.size.width or 40
            padding = max(0, width - len(self.title) - 4)
            text = Text()
            text.append(" ")
            if self._is_focused:
                text.append(self.title, style="bold white on green")
                text.append(" " * padding, style="on green")
                text.append("[x]", style="bold red on green")
            else:
                text.append(self.title, style="bold white on blue")
                text.append(" " * padding, style="on blue")
                text.append("[x]", style="bold red on blue")
            titlebar.update(text)
        except:
            pass

    def on_click(self, event):
        """Handle clicks on this widget."""
        x = event.x
        width = self.size.width or 80
        if x >= width - 4:
            self.post_message(ClosePaneRequest(self.pane_id))

    def on_close_pane_request(self, message: ClosePaneRequest) -> None:
        if message.pane_id == self.pane_id:
            self.remove()
