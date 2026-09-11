"""Core shell — TankuOS retro desktop.

Clean step 2: app menu via ModalScreen.
"""

from typing import Dict, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button
from textual.binding import Binding
from textual.screen import ModalScreen

from tankuos.theme import theme


# App registry
APPS = {
    "Shell": {"icon": "", "description": "Terminal shell"},
    "Retirement": {"icon": "󰃖", "description": "IRA portfolio tracker"},
    "Monster": {"icon": "󰍵", "description": "Energy drink P&L"},
    "MontcoMonitor": {"icon": "󰜟", "description": "VoIP monitor"},
    "Glances": {"icon": "󰄩", "description": "System monitor"},
}


class AppMenuScreen(ModalScreen):
    """App selection modal."""

    CSS = """
    Screen {
        align: left top;
    }

    #app-menu {
        width: 30;
        height: auto;
        background: $surface;
        border: solid $accent;
        padding: 1;
        offset: 18 1;
    }

    #app-menu Button {
        width: auto;
        content-align: left middle;
        height: 1;
        background: $surface;
        border: none;
        text-style: bold;
        padding: 0;
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        with Vertical(id="app-menu"):
            yield Static("Select Application")
            for name, info in APPS.items():
                yield Button(name, id=name)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Return selected app name."""
        self.dismiss(event.button.id)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)


class Shell(App):
    """TankuOS desktop shell."""

    CSS = """
    #desktop {
        layout: vertical;
    }

    #menubar {
        height: 1;
        background: $primary;
        padding: 0;
    }

    #menubar Button {
        background: $primary;
        color: $accent;
        border: none;
        height: 1;
        min-width: 6;
        padding: 0;
        text-style: bold;
        padding: 0;
    }

    #menubar Button:focus {
        background: $accent;
        color: $surface;
    }

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

    #statusbar {
        height: 1;
        background: $secondary;
        padding: 0;
    }

    #statusbar Static {
        width: auto;
        content-align: left middle;
        color: $accent;
    }
    """

    BINDINGS = [
        Binding("f1", "help", "Help"),
        Binding("f2", "cycle_theme", "Theme"),
        Binding("f3", "toggle_apps", "Apps"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_name = "turbopascal"

    def compose(self) -> ComposeResult:
        with Container(id="desktop"):
            with Horizontal(id="menubar"):
                yield Button("File", id="menu-file")
                yield Button("Edit", id="menu-edit")
                yield Button("View", id="menu-view")
                yield Button("Apps", id="menu-apps")
                yield Button("Help", id="menu-help")

            with Container(id="workspace"):
                with Container(id="pane-grid"):
                    yield Static("Pane content here", id="pane-main")

            with Horizontal(id="statusbar"):
                yield Static(" F1 Help")
                yield Static(" F2 Theme")
                yield Static(" F3 Apps")
                yield Static(" Q Quit")

    def on_mount(self) -> None:
        self.title = "TankuOS"
        self.sub_title = "Retro Desktop"
        theme.set_palette(self.theme_name)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "menu-apps":
            self.action_toggle_apps()
        elif event.button.id == "menu-help":
            self.action_help()
        else:
            self.notify(f"{event.button.id} (not yet)")

    def action_cycle_theme(self) -> None:
        themes = ["turbopascal", "midnight", "nord", "gruvbox"]
        idx = themes.index(self.theme_name)
        self.theme_name = themes[(idx + 1) % len(themes)]
        theme.set_palette(self.theme_name)
        self.notify(f"Theme: {self.theme_name}")

    def action_toggle_apps(self) -> None:
        self.push_screen(AppMenuScreen(), self._on_app_selected)

    def _on_app_selected(self, app_name: Optional[str]) -> None:
        if app_name:
            self.notify(f"Selected: {app_name}")

    def action_help(self) -> None:
        self.notify("TankuOS — Retro Desktop | F2: Theme | F3: Apps | Q: Quit")

    def action_quit(self) -> None:
        self.exit()


def main():
    shell = Shell()
    shell.run()


if __name__ == "__main__":
    main()
