"""Core shell — the main TankuOS desktop.

A retro text-mode IDE layout inspired by Turbo Pascal:
  - Single-line menu bar at top (always visible)
  - Full-width workspace with ASCII-bordered panes
  - Status bar at bottom with key hints
  - Themeable (turbopascal default)
"""

from typing import Dict, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button, Label
from textual.binding import Binding
from textual.screen import ModalScreen

from tankuos.theme import theme
from tankuos.pane import Pane


class AppMenuItem:
    """Compat stub — kept for backward compat with tests."""

    def __init__(self, name: str = "", icon: str = "", **kwargs):
        self.app_name = name
        self.icon = icon

    def render(self) -> str:
        return f"  {self.icon} {self.app_name}"


# Nerd Font icons for apps
APP_ICONS = {
    "Shell": "",
    "Retirement": "󰃖",
    "Monster": "󰍵",
    "MontcoMonitor": "󰜟",
    "Glances": "󰄩",
    "default": "󰲌",
}


class AppMenuScreen(ModalScreen):
    """Modal popup showing available applications."""

    CSS = """
    Screen {
        align: center middle;
    }

    #app-menu {
        width: 30;
        height: auto;
        background: $surface;
        border: solid $accent;
        padding: 1;
    }

    #app-menu Button {
        width: 100%;
        height: 1;
        background: $surface;
        border: none;
        margin: 0;
        text-style: bold;
    }

    #app-menu Button:focus {
        background: $accent;
        color: $surface;
    }

    #app-menu Button:hover {
        background: $accent;
        color: $surface;
    }
    """

    def __init__(self, apps: Dict[str, str] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.apps = apps or {}

    def compose(self) -> ComposeResult:
        with Vertical(id="app-menu"):
            yield Label("Select Application", classes="menu-title")
            for name, icon in self.apps.items():
                yield Button(f" {icon} {name}", id=name)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)


class Shell(App):
    """The TankuOS desktop shell."""

    CSS = """
    #desktop {
        layout: vertical;
    }

    /* Top menu bar */
    #menubar {
        height: 1;
        background: $primary;
        padding: 0 1;
    }

    #menubar Button {
        background: $primary;
        color: $accent;
        border: none;
        min-width: 6;
        height: 1;
        padding: 0 1;
        text-style: bold;
    }

    #menubar Button:focus {
        background: $accent;
        color: $surface;
    }

    /* Workspace */
    #workspace {
        height: 1fr;
        padding: 1;
    }

    #pane-grid {
        layout: grid;
        grid-size: 2 2;
        height: 1fr;
        padding: 0;
    }

    /* Bottom status bar */
    #statusbar {
        height: 1;
        background: $secondary;
        padding: 0 1;
    }

    #statusbar Static {
        width: auto;
        color: $accent;
    }

    /* Pane styling */
    .pane {
        border: solid $primary;
        margin: 0;
    }

    .pane:focus-within {
        border: solid $accent;
    }
    """

    BINDINGS = [
        Binding("f1", "help", "Help"),
        Binding("f2", "cycle_theme", "Theme"),
        Binding("f3", "toggle_apps", "Apps"),
        Binding("f5", "run", "Run"),
        Binding("f9", "compile", "Compile"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, apps: Optional[Dict[str, str]] = None, **kwargs):
        super().__init__(**kwargs)
        self.panes: Dict[str, Pane] = {}
        self.active_pane_id: Optional[str] = None
        self.theme_name = "turbopascal"
        self.apps = apps or {
            "Shell": APP_ICONS["Shell"],
            "Retirement": APP_ICONS["Retirement"],
            "Monster": APP_ICONS["Monster"],
            "MontcoMonitor": APP_ICONS["MontcoMonitor"],
            "Glances": APP_ICONS["Glances"],
        }

    def compose(self) -> ComposeResult:
        """Compose the desktop layout."""
        with Container(id="desktop"):
            # Top menu bar — single line, always visible
            with Horizontal(id="menubar"):
                yield Button("File", id="menu-file")
                yield Button("Edit", id="menu-edit")
                yield Button("View", id="menu-view")
                yield Button("Apps", id="menu-apps")
                yield Button("Help", id="menu-help")

            # Workspace area
            with Container(id="workspace"):
                with Container(id="pane-grid"):
                    pane = Pane(
                        title="Shell",
                        command="/bin/bash",
                        pane_id="main",
                        classes="pane",
                    )
                    self.panes["main"] = pane
                    yield pane

            # Bottom status bar
            with Horizontal(id="statusbar"):
                yield Static(" F1 Help")
                yield Static(" F2 Theme")
                yield Static(" F3 Apps")
                yield Static(" F5 Run")
                yield Static(" F9 Compile")
                yield Static(" Q Quit", id="status-quit")

    def on_mount(self) -> None:
        """Initialize the shell."""
        self.title = "TankuOS"
        self.sub_title = "Retro Desktop Environment"
        theme.set_palette(self.theme_name)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle menu bar button presses."""
        if event.button.id == "menu-apps":
            self.action_toggle_apps()
        elif event.button.id == "menu-help":
            self.action_help()
        elif event.button.id == "menu-file":
            self.notify("File menu (not yet implemented)")
        elif event.button.id == "menu-edit":
            self.notify("Edit menu (not yet implemented)")
        elif event.button.id == "menu-view":
            self.notify("View menu (not yet implemented)")

    def action_cycle_theme(self) -> None:
        """Cycle through available themes."""
        themes = ["turbopascal", "midnight", "nord", "gruvbox"]
        idx = themes.index(self.theme_name)
        self.theme_name = themes[(idx + 1) % len(themes)]
        theme.set_palette(self.theme_name)
        self.notify(f"Theme: {self.theme_name}")

    def action_toggle_apps(self) -> None:
        """Open the app menu modal."""
        self.push_screen(AppMenuScreen(apps=self.apps), self._on_app_selected)

    def _on_app_selected(self, app_name: Optional[str]) -> None:
        """Handle app selection."""
        if app_name:
            self.notify(f"Launching: {app_name}")

    def action_help(self) -> None:
        """Show help."""
        self.notify("TankuOS — Retro Desktop Environment | F2: Theme | F3: Apps | Q: Quit")

    def action_run(self) -> None:
        """Run (placeholder)."""
        self.notify("Run (not yet implemented)")

    def action_compile(self) -> None:
        """Compile (placeholder)."""
        self.notify("Compile (not yet implemented)")

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

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
