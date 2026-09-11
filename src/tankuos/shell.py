"""Core shell — the main TankuOS desktop.

Manages panes in a grid, provides dropdown app menu and status bar.
Based on WarpStrand-Client's topbar pattern.
"""

from typing import Dict, List, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button, Input, Label
from textual.css.query import NoMatches
from textual.binding import Binding

from tankuos.theme import theme, TankuHeader
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


class AppMenuItem(Static):
    """A single item in the dropdown app menu."""

    def __init__(self, name: str = "", icon: str = "", **kwargs):
        self.app_name = name
        self.icon = icon
        super().__init__(f"  {icon} {name}", **kwargs)
        self.add_class("dropdown-item")

    def render(self) -> str:
        """Render the menu item with proper styling."""
        return f"  {self.icon} {self.app_name}"


class AppDropdown(Vertical):
    """Dropdown application menu."""

    expanded: bool = False

    def __init__(self, apps: Dict[str, str] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.apps = apps or {}
        self.selected = 0

    def compose(self) -> ComposeResult:
        """Compose the dropdown button + menu items."""
        yield Button("TankuOS ▾", id="dropdown-toggle", classes="dropdown-toggle")
        for name, icon in self.apps.items():
            item = AppMenuItem(app_name=name, icon=icon)
            item.styles.display = "none"
            yield item

    def on_mount(self) -> None:
        """Items are hidden at compose time via styles.display."""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Toggle dropdown on toggle button press."""
        if event.button.id == "dropdown-toggle":
            self.expanded = not self.expanded
            for item in self.query(".dropdown-item"):
                item.styles.display = "block" if self.expanded else "none"
            self.refresh()


class Shell(App):
    """The TankuOS desktop shell."""

    CSS = """
    #desktop {
        layout: vertical;
    }

    #topbar {
        height: auto;
        background: $primary;
    }

    #tb_left {
        width: auto;
        padding-left: 1;
        color: $accent;
        text-style: bold;
    }

    #tb_center {
        width: 1fr;
        text-align: center;
    }

    #tb_right {
        width: auto;
        padding-right: 1;
    }

    #dropdown-toggle {
        background: $primary;
        color: $accent;
        min-width: 12;
        height: 1;
        border: none;
        padding: 0;
    }

    #dropdown-toggle:focus {
        border: none;
    }

    .dropdown-item {
        background: $surface;
        border: solid $primary;
        min-width: 20;
        height: 1;
    }

    .dropdown-item:focus {
        background: $primary;
        border: solid $accent;
    }

    .dropdown-item:hover {
        background: $primary;
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

    #bottombar {
        height: 1;
        background: $secondary;
    }

    #bb_left {
        width: auto;
        padding-left: 1;
        color: $accent;
    }

    #bb_center {
        width: 1fr;
        text-align: center;
    }

    #bb_right {
        width: auto;
        padding-right: 1;
        color: $success;
    }

    .pane {
        border: solid $primary;
        margin: 1;
    }

    .pane:focus-within {
        border: solid $accent;
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
            # Top bar — WarpStrand-Client style
            with Horizontal(id="topbar"):
                yield AppDropdown(apps=self.apps, id="tb_left")
                yield Static("", id="tb_center")
                yield Static("CPU --%  MEM --%", id="tb_right")

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

            # Bottom bar — WarpStrand-Client style
            with Horizontal(id="bottombar"):
                yield Static("● TankuOS ready", id="bb_left")
                yield Static("F1 Help  F2 Theme  F3 Apps", id="bb_center")
                yield Static("● OK", id="bb_right")

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
        try:
            dropdown = self.query_one("#tb_left", AppDropdown)
            dropdown.expanded = not dropdown.expanded
            for item in dropdown.query(".dropdown-item"):
                if dropdown.expanded:
                    item.styles.display = "block"
                else:
                    item.styles.display = "none"
        except NoMatches:
            pass

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
