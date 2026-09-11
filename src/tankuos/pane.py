"""Pane widget — hosts a child process in a PTY.

Spawns a process, reads its output, renders to a TankuOS pane,
and forwards keyboard input.
"""

import os
import threading
import time
from typing import Optional

from textual.widget import Widget
from textual.widgets import Static
from textual.message import Message
from textual.geometry import Size
from ptyprocess import PtyProcessUnicode

from tankuos.theme import theme


class PaneOutput(Message):
    """Message sent when new output is available."""

    def __init__(self, pane_id: str, data: str) -> None:
        super().__init__()
        self.pane_id = pane_id
        self.data = data


class Pane(Widget):
    """A TankuOS pane hosting a child process in a PTY.

    Each pane runs a single process. Output is captured and rendered.
    Keyboard input is forwarded to the process.
    """

    has_focus: bool = False

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
        self._process: Optional[PtyProcessUnicode] = None
        self._output_lines: list[str] = []
        self._reader_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()

    def compose(self):
        """Compose the pane — title bar + content area."""
        yield PaneTitleBar(self.title, self.pane_id)
        yield PaneContent(self.pane_id)

    def on_mount(self) -> None:
        """Start the child process when the pane mounts."""
        self._start_process()

    def _start_process(self) -> None:
        """Spawn the child process in a PTY."""
        try:
            self._process = PtyProcessUnicode.spawn(
                [self.command] if isinstance(self.command, str) else self.command,
                dimensions=(24, 80),
            )
            self._running = True
            self._reader_thread = threading.Thread(
                target=self._read_output, daemon=True
            )
            self._reader_thread.start()
        except Exception as e:
            self._output_lines.append(f"Failed to start: {e}")

    def _read_output(self) -> None:
        """Read output from the PTY in a background thread."""
        while self._running and self._process and self._process.isalive():
            try:
                data = self._process.read(1024)
                if data:
                    with self._lock:
                        self._output_lines.append(data)
                        # Keep only last 1000 lines
                        if len(self._output_lines) > 1000:
                            self._output_lines = self._output_lines[-1000:]
                    # Notify the UI
                    self.post_message(PaneOutput(self.pane_id, data))
            except EOFError:
                break
            except OSError:
                break
            except Exception:
                break

    def write_input(self, data: str) -> None:
        """Write keyboard input to the PTY."""
        if self._process and self._process.isalive():
            try:
                self._process.write(data)
            except (OSError, EOFError):
                pass

    def resize(self, rows: int, cols: int) -> None:
        """Resize the PTY."""
        if self._process and self._process.isalive():
            try:
                self._process.setwinsize(rows, cols)
            except (OSError, EOFError):
                pass

    def kill(self) -> None:
        """Kill the child process and stop the reader."""
        self._running = False
        if self._process and self._process.isalive():
            try:
                self._process.terminate(force=True)
            except Exception:
                pass

    def on_pane_output(self, message: PaneOutput) -> None:
        """Handle new output — update the content widget."""
        if message.pane_id == self.pane_id:
            try:
                content = self.query_one(f"#content-{self.pane_id}", PaneContent)
                with self._lock:
                    content.text = "".join(self._output_lines)
                content.scroll_end()
            except Exception:
                pass

    def on_key(self, event) -> None:
        """Forward key events to the PTY."""
        if not self.has_focus:
            return
        # Forward the key to the child process
        self.write_input(event.key)

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


class PaneTitleBar(Static):
    """Title bar for a pane."""

    focused: bool = False

    def __init__(self, title: str = "", pane_id: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.title = title
        self.pane_id = pane_id
        self.add_class("pane-title")

    def render(self):
        p = theme.palette
        border = p.border_focus if self.focused else p.border_primary
        return (
            f"[{border}]┌─[/{border}]"
            f"[{p.accent_primary}] {self.title} [/{p.accent_primary}]"
            f"[{border}]{'─' * max(0, self.size.width - len(self.title) - 6)}┐[/{border}]"
        )


class PaneContent(Static):
    """Content area of a pane — displays process output."""

    text: str = ""

    def __init__(self, pane_id: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.pane_id = pane_id
        self.add_class("pane-content")

    def render(self):
        p = theme.palette
        return self.text or f"[{p.text_secondary}]...[/{p.text_secondary}]"
