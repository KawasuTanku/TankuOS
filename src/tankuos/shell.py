"""Core shell — the main TankuOS desktop.

Manages panes in a grid, provides dropdown app menu and status bar.
"""

from typing import Dict, List, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button, Input, Label
from textual.css.query import NoMatches
from textual.binding import Binding
from textual import work

from tankuos.theme import theme, TankuHeader, TankuFooter
from tankuos.pane import Pane


# Nerd Font icons for apps
APP_ICONS = {
    "Shell": "",        # nf-fa-terminal
    "Retirement": "󰃖",   # nf-mdi-chart_line
    "Monster": "󰍵",     # nf-mdi-cash
    "MontcoMonitor": "󰜟", # nf-mdi-phone
    "Glances": "󰄩",     # nf-mdi-monitor_dashboard
    "default": "󰲌",     # nf-mdi-application
}


class AppMenuItem(Button):
    """A single app entry in the dropdown menu."""

    def __init__(self, name: str, icon: str = "", **kwargs):
        super().__init__(**kwargs)
        self.app_name = name
        self.icon = icon or APP_ICONS.get("default", "󰲌")

    def render(self):
        p = theme.palette
        if self.has_focus:
            return f"[{p.bg_surface} {p.accent_primary}] {self.icon}  {self.app_name}[/]"
        return f"[{p.text_primary}] {self.icon}  {self.app_name}[/]"


class Shell(App):
    """The TankuOS desktop shell."""

    CSS = """
    #desktop {
        layout: vertical;
    }

    #header {
        height: 1;
        border-bottom: solid #1e293b;
        background: #0f1420;
        layout: horizontal;
    }

    #header-apps {
        width: 18;
        content-align: left middle;
        padding-left: 1;
    }

    #header-spacer {
        width: 1fr;
    }

    #header-status {
        width: 30;
        content-align: right middle;
        padding-right: 1;
    }

    #main-area {
        layout: vertical;
        height: 1fr;
    }

    #pane-grid {
        layout: grid;
        grid-size: 2 2;
        height: 1fr;
        padding: 1;
    }

    #status-bar {
        height: 1;
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

    .dropdown-item {
        display: none;
        background: #141b2d;
        border: solid #1e293b;
        min-width: 20;
        height: 1;
    }

    .dropdown-item:focus {
        background: #1e293b;
        border: solid #22d3ee;
    }
    """

    BINDINGS = [
        Binding("f1", "help", "Help"),
        Binding("f2", "cycle_theme", "Theme"),
        Binding("f3", "toggle_launcher", "Apps"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, apps: Optional[Dict[str, str]] = None, **kwargs):
        super().__init__(**kwargs)
        self.panes: Dict[str, Pane] = {}
        self.active_pane_id: Optional[str] = None
        self.theme_name = "midnight"
        self.apps = apps or {
            "Shell": APP_ICONS["Shell"],
            "Retirement": APP_ICONS["Retirement"],
            "Monster": APP_ICONS["Monster"],
            "MontcoMonitor": APP_ICONS["MontcoMonitor"],
            "Glances": APP_ICONS["Glances"],
        }
        self.dropdown_expanded = False

    def compose(self) -> ComposeResult:
        """Compose the desktop layout."""
        with Container(id="desktop"):
            # Header bar with TankuOS menu and status
            with Container(id="header"):
                yield Label(" 󰲌 TankuOS ▾", id="header-apps")
                yield Static("", id="header-spacer")
                yield Label("󰥔  --:--  󰍛 --%", id="header-status")

            # Main area with pane grid
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
        """Toggle the app dropdown."""
        self.dropdown_expanded = not self.dropdown_expanded
        # Show/hide dropdown items
        for item in self.query(".dropdown-item"):
            item.display = self.dropdown_expanded

    def action_help(self) -> None:
        """Show help."""
        self.notify("F1 Help | F2 Theme | F3 Apps | Q Quit")

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
