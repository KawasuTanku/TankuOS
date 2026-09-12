"""Core shell — TankuOS retro desktop."""

from typing import Dict, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Static, Button
from textual.binding import Binding
from textual.screen import ModalScreen

from tankuos.theme import theme
from tankuos.pane import Pane, ClosePaneRequest
from tankuos import plugins


APP_ICONS: Dict[str, str] = {
    "Shell": "\\ue795",
    "Retirement": "\\U000f00d6",
    "Monster": "\\U000f0375",
    "MontcoMonitor": "\\U000f071f",
    "Glances": "\\U000f0129",
    "default": "\\U000f0b0c",
}


class SystemMenuScreen(ModalScreen):
    """System menu — session options."""

    CSS = """
    Screen {
        background: $surface;
        align: left top;
    }

    #system-menu {
        width: 20;
        height: auto;
        background: $surface;
        border: solid $accent;
        offset: 0 1;
    }

    .sys-row {
        width: 20;
        height: 1;
        padding: 0 1;
    }

    .sys-row:hover {
        background: $accent;
    }

    .sys-row:focus {
        background: $accent;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._items = ["Exit"]

    def compose(self) -> ComposeResult:
        with Vertical(id="system-menu"):
            for name in self._items:
                yield Static(name, id=name, classes="sys-row")

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
        elif event.key == "enter":
            focused = self.focused
            if focused and hasattr(focused, 'id'):
                self.dismiss(focused.id)

    def on_click(self, event) -> None:
        widget = event.widget
        if widget is self:
            self.dismiss(None)
        elif hasattr(widget, 'id'):
            self.dismiss(widget.id)


class AppMenuItem:
    """Compat stub for tests."""

    def __init__(self, name: str = "", icon: str = "", **kwargs) -> None:
        self.app_name = name
        self.icon = icon

    def render(self) -> str:
        return f"  {self.icon} {self.app_name}"


class AppMenuScreen(ModalScreen):
    """App selection modal."""

    CSS = """
    Screen {
        background: $surface;
        align: left top;
    }

    #app-menu {
        width: 20;
        height: auto;
        background: $surface;
        border: solid $accent;
        offset: 16 1;
    }

    .menu-row {
        width: 20;
        height: 1;
        padding: 0;
    }

    .menu-row:hover {
        background: $accent;
    }

    .menu-row:focus {
        background: $accent;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._apps = ["Shell", "Retirement", "Monster", "MontcoMonitor", "Glances"]

    def compose(self) -> ComposeResult:
        with Vertical(id="app-menu"):
            for name in self._apps:
                yield Static(name, id=name, classes="menu-row")

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
        elif event.key == "enter":
            focused = self.focused
            if focused and hasattr(focused, 'id'):
                self.dismiss(focused.id)

    def on_click(self, event) -> None:
        widget = event.widget
        if widget is self:
            self.dismiss(None)
        elif hasattr(widget, 'id'):
            self.dismiss(widget.id)


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
        padding: 0;
    }

    #pane-grid {
        height: 1fr;
        padding: 0;
        layout: vertical;
    }
    
    #pane-grid > Horizontal {
        height: 1fr;
    }
    
    #pane-grid > Horizontal > Pane {
        width: 1fr;
        height: 1fr;
        border: solid $primary;
    }
    
    #pane-grid > Horizontal > Pane:focus-within {
        border: solid $accent;
    }
    
    #pane-grid > Horizontal > Pane.focused {
        border: solid $accent;
    }

    #statusbar {
        height: 1;
        background: $secondary;
        padding: 0;
    }

    #statusbar Static {
        width: 20;
        color: $accent;
    }

    """

    BINDINGS = [
        Binding("f1", "help", "Help"),
        Binding("f2", "cycle_theme", "Theme"),
        Binding("f3", "toggle_apps", "Apps"),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.theme_name = "turbopascal"
        self._menu_button = None
        self.panes: Dict[str, dict] = {}
        self.active_pane_id: Optional[str] = None

    def compose(self) -> ComposeResult:
        with Container(id="desktop"):
            with Horizontal(id="menubar"):
                yield Button("TankuOS", id="menu-file")
                yield Button("View", id="menu-view")
                yield Button("Apps", id="menu-apps")
                yield Button("Help", id="menu-help")

            with Container(id="workspace"):
                with Container(id="pane-grid"):
                    pass

            with Horizontal(id="statusbar"):
                yield Static(" F1 Help")
                yield Static(" F2 Theme")
                yield Static(" F3 Apps")

    def on_mount(self) -> None:
        self.title = "TankuOS"
        self.sub_title = "Retro Desktop"
        theme.set_palette(self.theme_name)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self._clear_active_menu()
        if event.button.id == "menu-file":
            event.button.add_class("active")
            self._menu_button = event.button
            self.action_system_menu()
        elif event.button.id == "menu-apps":
            event.button.add_class("active")
            self._menu_button = event.button
            self.action_toggle_apps()
        elif event.button.id == "menu-help":
            event.button.add_class("active")
            self._menu_button = event.button
            self.action_help()
        elif event.button.id == "menu-view":
            event.button.add_class("active")
            self._menu_button = event.button
            self.notify(f"{event.button.id} (not yet)")

    def _clear_active_menu(self) -> None:
        if self._menu_button:
            self._menu_button.remove_class("active")
            self._menu_button = None

    def action_system_menu(self) -> None:
        self.push_screen(SystemMenuScreen(), self._on_system_menu_selected)

    def _on_system_menu_selected(self, choice: Optional[str]) -> None:
        self._clear_active_menu()
        if choice == "Exit":
            self.exit()

    def action_cycle_theme(self) -> None:
        themes = ["turbopascal", "midnight", "nord", "gruvbox"]
        idx = themes.index(self.theme_name)
        self.theme_name = themes[(idx + 1) % len(themes)]
        theme.set_palette(self.theme_name)
        self.notify(f"Theme: {self.theme_name}")

    def action_toggle_apps(self) -> None:
        self.push_screen(AppMenuScreen(), self._on_app_selected)

    def _on_app_selected(self, app_name: Optional[str]) -> None:
        self._clear_active_menu()
        if app_name:
            self._launch_app(app_name)

    def _launch_app(self, app_name: str) -> None:
        """Launch an application in a new pane."""
        if app_name == "Shell":
            content = plugins.ShellPane(classes="shell-pane")
        else:
            content = Static(f"{app_name}\n\n[Plugin content goes here]", classes="pane-content")

        # Generate unique pane ID (allow multiple instances of same app)
        base_id = f"pane-{app_name.lower()}"
        pane_id = base_id
        counter = 1
        while pane_id in self.panes:
            pane_id = f"{base_id}-{counter}"
            counter += 1
        
        # Store pane state (title + content widget)
        self.panes[pane_id] = {"title": app_name, "content": content}
        self._rebuild_grid()
        self.notify(f"Launched: {app_name}")

    def _rebuild_grid(self) -> None:
        """Rebuild the grid using nested Horizontal/Vertical containers."""
        grid = self.query_one("#pane-grid", Container)
        
        # Clear existing children
        for child in list(grid.children):
            child.remove()

        # Calculate grid size
        count = len(self.panes)
        if count <= 1:
            cols, rows = 1, 1
        elif count == 2:
            cols, rows = 2, 1
        elif count <= 4:
            cols, rows = 2, 2
        elif count <= 6:
            cols, rows = 3, 2
        else:
            cols, rows = 3, 3

        # Build nested Horizontal/Vertical layout
        panes_list = list(self.panes.items())
        for r in range(rows):
            row = Horizontal()
            grid.mount(row)
            for c in range(cols):
                idx = r * cols + c
                if idx < len(panes_list):
                    pane_id, pane_info = panes_list[idx]
                    # Create a fresh Pane wrapper (reuses content widget)
                    pane = Pane(
                        title=pane_info["title"],
                        content=pane_info["content"],
                        pane_id=pane_id,
                    )
                    row.mount(pane)

    def action_help(self) -> None:
        self.notify("TankuOS — Retro Desktop | F1: Help | F2: Theme | F3: Apps | TankuOS → Exit to Quit")
        self._clear_active_menu()

    def action_quit(self) -> None:
        self.exit()

    def on_close_pane_request(self, message: ClosePaneRequest) -> None:
        """Handle close request from pane title bar."""
        self.remove_pane(message.pane_id)

    def add_pane(self, title: str, content: Widget, pane_id: str = "") -> None:
        """Add a new pane with plugin content."""
        pid = pane_id or f"pane-{title.lower()}"
        self.panes[pid] = {"title": title, "content": content}
        self._rebuild_grid()

    def remove_pane(self, pane_id: str) -> None:
        """Remove a pane from the desktop."""
        if pane_id in self.panes:
            del self.panes[pane_id]
            self._rebuild_grid()

    def focus_pane_by_id(self, pane_id: str) -> None:
        """Focus a specific pane by ID, unfocus all others."""
        # Unfocus all panes
        grid = self.query_one("#pane-grid", Container)
        for pane in grid.query(Pane):
            pane.set_focused(False)
        
        # Focus the requested pane
        for pane in grid.query(Pane):
            if pane.pane_id == pane_id:
                pane.set_focused(True)
                self.active_pane_id = pane_id
                break


def main() -> None:
    shell = Shell()
    shell.run()


if __name__ == "__main__":
    main()
