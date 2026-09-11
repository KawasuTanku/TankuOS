"""Core shell — TankuOS retro desktop.

Clean step 1: static retro layout.
  - Single-line menu bar at top
  - Full-width workspace with ASCII-bordered pane
  - Status bar at bottom with key hints
"""

from typing import Dict, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button, Label
from textual.binding import Binding

from tankuos.theme import theme


class Shell(App):
    """TankuOS desktop shell — retro Pascal IDE style."""

    CSS = """
    #desktop {
        layout: vertical;
    }

    /* Menu bar */
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

    /* Workspace */
    #workspace {
        height: 1fr;
        padding: 1;
    }

    /* Pane grid */
    #pane-grid {
        layout: grid;
        grid-size: 2 2;
        height: 1fr;
        padding: 0;
    }

    /* Status bar */
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

    def compose(self) -> ComposeResult:
        """Compose the desktop."""
        with Container(id="desktop"):
            # Menu bar
            with Horizontal(id="menubar"):
                yield Button("File", id="menu-file")
                yield Button("Edit", id="menu-edit")
                yield Button("View", id="menu-view")
                yield Button("Apps", id="menu-apps")
                yield Button("Help", id="menu-help")

            # Workspace with a single pane placeholder
            with Container(id="workspace"):
                with Container(id="pane-grid"):
                    yield Static("Pane content here", id="pane-main")

            # Status bar
            with Horizontal(id="statusbar"):
                yield Static(" F1 Help")
                yield Static(" F2 Theme")
                yield Static(" F3 Apps")
                yield Static(" Q Quit")

    def on_mount(self) -> None:
        """Initialize."""
        self.title = "TankuOS"
        self.sub_title = "Retro Desktop"
        theme.set_palette(self.theme_name)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle menu clicks."""
        self.notify(f"{event.button.id} clicked")

    def action_cycle_theme(self) -> None:
        """Cycle themes."""
        themes = ["turbopascal", "midnight", "nord", "gruvbox"]
        idx = themes.index(self.theme_name)
        self.theme_name = themes[(idx + 1) % len(themes)]
        theme.set_palette(self.theme_name)
        self.notify(f"Theme: {self.theme_name}")

    def action_toggle_apps(self) -> None:
        """Open app menu (placeholder)."""
        self.notify("Apps menu (step 2)")

    def action_help(self) -> None:
        """Show help."""
        self.notify("TankuOS — Retro Desktop Environment")

    def action_quit(self) -> None:
        """Quit."""
        self.exit()


def main():
    """Entry point."""
    shell = Shell()
    shell.run()


if __name__ == "__main__":
    main()
