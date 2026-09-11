"""Core shell — the main TankuOS desktop.

Manages panes in a grid, provides launcher sidebar and status bar.
"""

from typing import Dict, List, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button, Input, Label
from textual.css.query import NoMatches
from textual.binding import Binding
from textual import work

from tankuos.theme import theme, TankuHeader, TankuFooter, TankuSidebar
from tankuos.pane import Pane


class Shell(App):
    """The TankuOS desktop shell."""

    CSS = """
    #desktop {
        layout: horizontal;
    }

    #sidebar {
        width: 25;
        height: 100%;
        border-right: solid #1e293b;
        background: #0f1420;
    }

    #main-area {
        layout: vertical;
        width: 1fr;
    }

    #pane-grid {
        layout: grid;
        grid-size: 2 2;
        height: 1fr;
        padding: 1;
    }

    #status-bar {
        height: 3;
        border-top: solid #1e293b;
        background: #0f1420;
    }

    .pane {
        border: solid #1e293b;
        margin: 1;
    }

    .pane:focus-within {
        border: solid #22d3ee;
    }
    """

    BINDINGS = [
        Binding("f1", "help", "Help"),
        Binding("f2", "cycle_theme", "Theme"),
        Binding("f3", "toggle_launcher", "Launcher"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.panes: Dict[str, Pane] = {}
        self.active_pane_id: Optional[str] = None
        self.theme_name = "midnight"

    def compose(self) -> ComposeResult:
        """Compose the desktop layout."""
        with Container(id="desktop"):
            yield TankuSidebar(
                items=["Shell", "Retirement", "Monster", "MontcoMonitor", "Glances"],
                id="sidebar",
            )
            with Container(id="main-area"):
                with Container(id="pane-grid"):
                    # Default: one shell pane
                    pane = Pane(
                        title="Shell",
                        command="/bin/bash",
                        pane_id="main",
                        classes="pane",
                    )
                    self.panes["main"] = pane
                    yield pane
                yield TankuFooter(status="TankuOS ready", id="status-bar")

    def on_mount(self) -> None:
        """Initialize the shell."""
        self.title = "TankuOS"
        self.sub_title = "Desktop Environment"

    def action_cycle_theme(self) -> None:
        """Cycle through available themes."""
        themes = ["midnight", "nord", "gruvbox", "dracula"]
        idx = themes.index(self.theme_name)
        self.theme_name = themes[(idx + 1) % len(themes)]
        theme.set_palette(self.theme_name)

    def action_toggle_launcher(self) -> None:
        """Toggle the launcher sidebar."""
        try:
            sidebar = self.query_one("#sidebar", TankuSidebar)
            if sidebar.display:
                sidebar.display = False
            else:
                sidebar.display = True
        except NoMatches:
            pass

    def action_help(self) -> None:
        """Show help."""
        self.notify("F1 Help | F2 Theme | F3 Launcher | Q Quit")

    def add_pane(self, title: str, command: str, pane_id: str = "") -> Pane:
        """Add a new pane to the desktop."""
        pane_id = pane_id or f"pane-{len(self.panes)}"
        pane = Pane(title=title, command=command, pane_id=pane_id, classes="pane")
        self.panes[pane_id] = pane
        return pane

    def remove_pane(self, pane_id: str) -> None:
        """Remove a pane from the desktop."""
        if pane_id in self.panes:
            self.panes[pane_id].kill()
            del self.panes[pane_id]

    def focus_pane(self, pane_id: str) -> None:
        """Focus a specific pane."""
        if pane_id in self.panes:
            if self.active_pane_id and self.active_pane_id in self.panes:
                self.panes[self.active_pane_id].has_focus = False
            self.active_pane_id = pane_id
            self.panes[pane_id].has_focus = True
            self.panes[pane_id].focus()


def main():
    """Entry point for TankuOS shell."""
    shell = Shell()
    shell.run()


if __name__ == "__main__":
    main()
