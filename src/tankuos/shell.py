"""Core shell — TankuOS retro desktop.

Clean step 2: app menu via ModalScreen.
"""

from typing import Dict, List, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button
from textual.binding import Binding
from textual.screen import ModalScreen

from tankuos.theme import theme
from tankuos.pane import Pane


APP_ICONS = {
    "Shell": "\\ue795",
    "Retirement": "\\U000f00d6",
    "Monster": "\\U000f0375",
    "MontcoMonitor": "\\U000f071f",
    "Glances": "\\U000f0129",
    "default": "\\U000f0b0c",
}


class AppMenuItem:
    """Compat stub — kept for backward compat with tests."""

    def __init__(self, name: str = "", icon: str = "", **kwargs):
        self.app_name = name
        self.icon = icon

    def render(self) -> str:
        return f"  {self.icon} {self.app_name}"


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
        offset: 18 1;
    }

    #app-menu Button {
        width: 100%;
        height: 1;
        background: $surface;
        border: none;
        text-style: bold;
        content-align: left middle;
        padding: 0 1;
    }

    #app-menu Button:hover {
        background: $accent;
        color: $surface;
    }

    #app-menu Button:focus {
        background: $accent;
        color: $surface;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_mount(self) -> None:
        """Prevent first button from auto-highlighting."""
        for button in self.query("Button"):
            button.has_focus = False

    def compose(self) -> ComposeResult:
        with Vertical(id="app-menu"):
            for name in ["Shell", "Retirement", "Monster", "MontcoMonitor", "Glances"]:
                yield Button(name, id=name)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Return selected app name."""
        self.dismiss(event.button.id)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)

    def on_click(self, event) -> None:
        """Click outside menu dismisses."""
        if event.widget is self:
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
        padding: 0 1;
    }

    #menubar Button {
        background: $primary;
        color: $accent;
        border: none;
        height: 1;
        min-width: 6;
        padding: 0 1;
        text-style: bold;
    }

    #menubar Button:focus {
        background: $accent;
        color: $surface;
    }

    #menubar Button.active {
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
        padding: 0 1;
    }

    #statusbar Static {
        width: auto;
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
        self._menu_button = None
        self.panes: Dict[str, Pane] = {}
        self.active_pane_id: Optional[str] = None

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
        # Clear any active button
        self._clear_active_menu()
        
        if event.button.id == "menu-apps":
            # Mark this button as active
            event.button.add_class("active")
            self._menu_button = event.button
            self.action_toggle_apps()
        elif event.button.id == "menu-help":
            event.button.add_class("active")
            self._menu_button = event.button
            self.action_help()
        elif event.button.id in ["menu-file", "menu-edit", "menu-view"]:
            event.button.add_class("active")
            self._menu_button = event.button
            self.notify(f"{event.button.id} (not yet)")

    def _clear_active_menu(self) -> None:
        """Remove active class from menu button."""
        if self._menu_button:
            self._menu_button.remove_class("active")
            self._menu_button = None

    def action_cycle_theme(self) -> None:
        themes = ["turbopascal", "midnight", "nord", "gruvbox"]
        idx = themes.index(self.theme_name)
        self.theme_name = themes[(idx + 1) % len(themes)]
        theme.set_palette(self.theme_name)
        self.notify(f"Theme: {self.theme_name}")

    def action_toggle_apps(self) -> None:
        self.push_screen(AppMenuScreen(), self._on_app_selected)

    def _on_app_selected(self, app_name: Optional[str]) -> None:
        """Handle app selection and clear menu highlight."""
        self._clear_active_menu()
        if app_name:
            self.notify(f"Selected: {app_name}")

    def action_help(self) -> None:
        self.notify("TankuOS — Retro Desktop | F2: Theme | F3: Apps | Q: Quit")
        self._clear_active_menu()

    def action_quit(self) -> None:
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
    shell = Shell()
    shell.run()


if __name__ == "__main__":
    main()
