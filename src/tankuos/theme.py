"""Theme system for TankuOS.

Provides a unified look across all TankuOS applications.
Apps import and use these classes to automatically match the active theme.
"""

from typing import Optional
from textual.color import Color
from textual.widget import Widget
from textual.widgets import Header, Footer, Static, Label, Button

from tankuos.palettes import Palette, get_palette, PALETTES


class Theme:
    """The active TankuOS theme.

    Holds the current palette and notifies subscribers when it changes.
    Uses a simple observer pattern — no Textual reactive needed for a singleton.
    """

    _instance: Optional["Theme"] = None
    _listeners: list = []

    def __new__(cls) -> "Theme":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._palette = get_palette("midnight")
        return cls._instance

    @property
    def palette(self) -> Palette:
        return self._palette

    def set_palette(self, name: str) -> None:
        """Switch to a different palette by name."""
        self._palette = get_palette(name)
        for callback in self._listeners:
            callback(self._palette)

    def on_change(self, callback) -> None:
        """Register a callback for theme changes."""
        self._listeners.append(callback)

    def remove_listener(self, callback) -> None:
        """Remove a theme-change listener."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    # Convenience accessors for common colors
    @property
    def bg_primary(self) -> str:
        return self._palette.bg_primary

    @property
    def bg_secondary(self) -> str:
        return self._palette.bg_secondary

    @property
    def bg_surface(self) -> str:
        return self._palette.bg_surface

    @property
    def text_primary(self) -> str:
        return self._palette.text_primary

    @property
    def text_secondary(self) -> str:
        return self._palette.text_secondary

    @property
    def accent_primary(self) -> str:
        return self._palette.accent_primary

    @property
    def accent_secondary(self) -> str:
        return self._palette.accent_secondary

    @property
    def accent_success(self) -> str:
        return self._palette.accent_success

    @property
    def accent_warning(self) -> str:
        return self._palette.accent_warning

    @property
    def accent_error(self) -> str:
        return self._palette.accent_error

    @property
    def accent_info(self) -> str:
        return self._palette.accent_info

    @property
    def border_primary(self) -> str:
        return self._palette.border_primary

    @property
    def border_focus(self) -> str:
        return self._palette.border_focus

    @property
    def selection_bg(self) -> str:
        return self._palette.selection_bg

    @property
    def cursor(self) -> str:
        return self._palette.cursor

    def color(self, hex_str: str) -> Color:
        """Convert a hex string to a Textual Color."""
        return Color.parse(hex_str)


# Global singleton
theme = Theme()


class TankuHeader(Widget):
    """A TankuOS-styled header bar."""

    def __init__(self, title: str = "TankuOS", **kwargs):
        super().__init__(**kwargs)
        self.title = title

    def render(self):
        p = theme.palette
        return f"[{p.accent_primary}]{self.title}[/]"


class TankuFooter(Widget):
    """A TankuOS-styled footer / status bar."""

    def __init__(self, status: str = "Ready", **kwargs):
        super().__init__(**kwargs)
        self.status = status

    def render(self):
        p = theme.palette
        return (
            f"[{p.accent_primary}]●[/{p.accent_primary}] "
            f"[{p.text_primary}]{self.status}[/{p.text_primary}]  "
            f"[{p.text_secondary}]F1 Help  F2 Theme  F3 Apps[/{p.text_secondary}]  "
            f"[{p.accent_success}]●[/{p.accent_success}][{p.text_secondary}] OK[/{p.text_secondary}]"
        )


class TankuPane(Widget):
    """A TankuOS pane — a container for hosted applications."""

    def __init__(self, title: str = "", content: str = "", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.content = content
        self.focused = False

    def render(self):
        p = theme.palette
        border_color = p.border_focus if self.focused else p.border_primary
        title_bar = f"[{border_color}]┌─ [/{border_color}][{p.accent_primary}]{self.title}[/{p.accent_primary}][{border_color}] ─{'─' * max(0, self.size.width - len(self.title) - 6)}┐[/{border_color}]"
        # Simplified rendering — real implementation would handle content and scrolling
        return title_bar


class TankuButton(Button):
    """A TankuOS-styled button."""

    def __init__(self, label: str = "", **kwargs):
        super().__init__(label, **kwargs)

    def render(self):
        p = theme.palette
        if self.disabled:
            return f"[{p.text_disabled}]{self.label}[/]"
        if self.has_focus:
            return f"[{p.bg_surface} {p.accent_primary}]{self.label}[/]"
        return f"[{p.accent_primary}]{self.label}[/]"


class TankuLabel(Static):
    """A TankuOS-styled label."""

    def __init__(self, text: str = "", variant: str = "primary", **kwargs):
        super().__init__(text, **kwargs)
        self.variant = variant

    def render(self):
        p = theme.palette
        colors = {
            "primary": p.text_primary,
            "secondary": p.text_secondary,
            "accent": p.accent_primary,
            "success": p.accent_success,
            "warning": p.accent_warning,
            "error": p.accent_error,
            "info": p.accent_info,
        }
        color = colors.get(self.variant, p.text_primary)
        return f"[{color}]{self.renderable}[/]"


class TankuSidebar(Widget):
    """A TankuOS sidebar for app navigation."""

    def __init__(self, items: list[str] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.items = items or []
        self.selected = 0

    def render(self):
        p = theme.palette
        lines = [f"[{p.accent_primary}]═══ TankuOS ═══[/]", ""]
        for i, item in enumerate(self.items):
            if i == self.selected:
                lines.append(f"[{p.bg_surface} {p.accent_primary}] ► {item}[/]")
            else:
                lines.append(f"[{p.text_primary}]   {item}[/]")
        return "\n".join(lines)
