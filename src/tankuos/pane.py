"""Pane widget — hosts a child process in a PTY."""

import re
import threading
from typing import Optional

from textual.widget import Widget
from textual.widgets import Static, Button
from textual.containers import Horizontal, Vertical
from textual.message import Message

from tankuos.theme import theme

# ANSI escape code pattern
_ANSI_RE = re.compile(r'\x1b\[[0-9;]*[A-Za-z]|\x1b\][^\x07]*\x07|\x1b\[[\?0-9]*[hl]')


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences and process backspaces."""
    text = _ANSI_RE.sub('', text)
    result = []
    for char in text:
        if char == '\x08':
            if result:
                result.pop()
        else:
            result.append(char)
    return ''.join(result)


class PaneOutput(Message):
    """Message sent when new output is available."""

    def __init__(self, pane_id: str, data: str) -> None:
        super().__init__()
        self.pane_id = pane_id
        self.data = data


class Pane(Widget):
    """A TankuOS pane hosting a child process in a PTY."""

    has_focus: bool = False
    can_focus: bool = True

    _KEY_MAP = {
        "enter": "\r",
        "backspace": "\x08",
        "tab": "\t",
        "escape": "\x1b",
        "space": " ",
        "up": "\x1b[A",
        "down": "\x1b[B",
        "right": "\x1b[C",
        "left": "\x1b[D",
        "home": "\x1b[H",
        "end": "\x1b[F",
        "pageup": "\x1b[5~",
        "pagedown": "\x1b[6~",
        "delete": "\x1b[3~",
    }

    def __init__(
        self,
        title: str = "Pane",
        command: str = "/bin/bash",
        pane_id: str = "",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.title = title
        self.command = command
        self.pane_id = pane_id or f"pane-{id(self)}"
        self._process = None
        self._output_lines: list[str] = []
        self._reader_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()

    def compose(self):
        yield PaneTitleBar(self.title, self.pane_id, id=f"title-{self.pane_id}")
        yield PaneContent(self.pane_id, id=f"content-{self.pane_id}")

    def on_mount(self) -> None:
        self._start_process()
        self.set_interval(0.1, self._refresh_content)

    def _refresh_content(self) -> None:
        try:
            content = self.query_one(f"#content-{self.pane_id}", PaneContent)
            content.refresh()
        except Exception:
            pass

    def _start_process(self) -> None:
        try:
            from ptyprocess import PtyProcessUnicode
            self._process = PtyProcessUnicode.spawn(
                [self.command] if isinstance(self.command, str) else self.command,
                dimensions=(24, 80),
                env={"TERM": "xterm-256color", "PATH": "/usr/local/bin:/usr/bin:/bin"},
            )
            self._running = True
            self._reader_thread = threading.Thread(
                target=self._read_output, daemon=True
            )
            self._reader_thread.start()
        except Exception as e:
            self._output_lines.append(f"Failed to start: {e}")

    def _read_output(self) -> None:
        while self._running and self._process and self._process.isalive():
            try:
                data = self._process.read(1024)
                if data:
                    with self._lock:
                        cleaned = strip_ansi(data)
                        self._output_lines.append(cleaned)
                        if len(self._output_lines) > 1000:
                            self._output_lines = self._output_lines[-1000:]
                    self.post_message(PaneOutput(self.pane_id, data))
            except (EOFError, OSError):
                break
            except Exception:
                break

    def write_input(self, data: str) -> None:
        if self._process and self._process.isalive():
            try:
                self._process.write(data)
            except (OSError, EOFError):
                pass

    def resize(self, rows: int, cols: int) -> None:
        if self._process and self._process.isalive():
            try:
                self._process.setwinsize(rows, cols)
            except (OSError, EOFError):
                pass

    def kill(self) -> None:
        self._running = False
        if self._process and self._process.isalive():
            try:
                self._process.terminate(force=True)
            except Exception:
                pass

    def on_pane_output(self, message: PaneOutput) -> None:
        if message.pane_id == self.pane_id:
            try:
                content = self.query_one(f"#content-{self.pane_id}", PaneContent)
                with self._lock:
                    content.update("".join(self._output_lines))
                content.scroll_end()
            except Exception:
                pass

    def on_key(self, event) -> None:
        if not self.has_focus:
            return
        key = event.key
        if key in self._KEY_MAP:
            self.write_input(self._KEY_MAP[key])
        elif len(key) == 1:
            self.write_input(key)
        elif key.startswith("ctrl+"):
            char = key.replace("ctrl+", "")
            if len(char) == 1:
                self.write_input(chr(ord(char) - ord('a') + 1))

    def on_focus(self) -> None:
        self.has_focus = True
        try:
            title_bar = self.query_one(f"#title-{self.pane_id}", PaneTitleBar)
            title_bar.focused = True
        except Exception:
            pass

    def on_blur(self) -> None:
        self.has_focus = False
        try:
            title_bar = self.query_one(f"#title-{self.pane_id}", PaneTitleBar)
            title_bar.focused = False
        except Exception:
            pass


class PaneTitleBar(Widget):
    """Title bar for a pane — title + close button."""

    focused: bool = False

    CSS = """
    PaneTitleBar {
        height: 1;
        layout: horizontal;
        padding: 0;
    }

    .title-text {
        width: 1fr;
        height: 1;
    }

    .close-btn {
        width: auto;
        height: 1;
        border: none;
        background: $primary;
        color: $accent;
        padding: 0 1;
    }

    .close-btn:focus {
        background: $error;
        color: $surface;
    }

    .close-btn:hover {
        background: $error;
        color: $surface;
    }
    """

    def __init__(self, title: str = "", pane_id: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.title = title
        self.pane_id = pane_id

    def compose(self):
        yield Static(self.title, classes="title-text", id=f"ttl-{self.pane_id}")
        yield Button("[x]", classes="close-btn", id=f"close-{self.pane_id}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Close button kills process and removes pane."""
        if event.button.id == f"close-{self.pane_id}":
            pane = self.parent
            if pane:
                pane.kill()
                pane.remove()


class PaneContent(Static):
    """Content area of a pane — displays process output."""

    def __init__(self, pane_id: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.pane_id = pane_id
        self.add_class("pane-content")

    def render(self):
        p = theme.palette
        text = self.content or f"[{p.text_secondary}]...[/{p.text_secondary}]"
        return text
