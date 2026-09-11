"""Color palettes for TankuOS.

Each palette defines a complete set of colors for the desktop chrome
and child applications to reference.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Palette:
    """A complete color palette for TankuOS.

    Colors are stored as hex strings for use with Textual's color system.
    """

    name: str
    description: str

    # Background colors
    bg_primary: str      # Main background
    bg_secondary: str    # Panel backgrounds, sidebar
    bg_surface: str      # Cards, elevated surfaces
    bg_inset: str        # Inputs, code blocks

    # Foreground colors
    text_primary: str    # Main text
    text_secondary: str  # Muted/secondary text
    text_disabled: str   # Disabled text

    # Accent colors
    accent_primary: str   # Primary action, focus, links
    accent_secondary: str # Secondary highlights
    accent_success: str   # Success states
    accent_warning: str   # Warning states
    accent_error: str     # Error states
    accent_info: str      # Info states

    # Border colors
    border_primary: str   # Main borders
    border_secondary: str # Subtle borders
    border_focus: str     # Focused element border

    # Special
    selection_bg: str    # Selected text background
    cursor: str           # Cursor color


PALETTES: Dict[str, Palette] = {
    "midnight": Palette(
        name="midnight",
        description="Deep navy and cyan — the default TankuOS experience",
        bg_primary="#0a0e17",
        bg_secondary="#0f1420",
        bg_surface="#141b2d",
        bg_inset="#080c14",
        text_primary="#e2e8f0",
        text_secondary="#94a3b8",
        text_disabled="#475569",
        accent_primary="#22d3ee",
        accent_secondary="#818cf8",
        accent_success="#34d399",
        accent_warning="#fbbf24",
        accent_error="#f871f8",
        accent_info="#60a5fa",
        border_primary="#1e293b",
        border_secondary="#1e293b",
        border_focus="#22d3ee",
        selection_bg="#1e3a5f",
        cursor="#22d3ee",
    ),
    "nord": Palette(
        name="nord",
        description="Arctic blues and muted grays — calm and focused",
        bg_primary="#2e3440",
        bg_secondary="#3b4252",
        bg_surface="#434c5e",
        bg_inset="#2e3440",
        text_primary="#eceff4",
        text_secondary="#d8dee9",
        text_disabled="#4c566a",
        accent_primary="#88c0d0",
        accent_secondary="#5e81ac",
        accent_success="#a3be8c",
        accent_warning="#ebcb8b",
        accent_error="#bf616a",
        accent_info="#81a1c1",
        border_primary="#4c566a",
        border_secondary="#434c5e",
        border_focus="#88c0d0",
        selection_bg="#434c5e",
        cursor="#d8dee9",
    ),
    "gruvbox": Palette(
        name="gruvbox",
        description="Warm earthy browns with retro groove — easy on the eyes",
        bg_primary="#282828",
        bg_secondary="#3c3836",
        bg_surface="#504945",
        bg_inset="#1d2021",
        text_primary="#ebdbb2",
        text_secondary="#d5c4a1",
        text_disabled="#928374",
        accent_primary="#fabd2f",
        accent_secondary="#83a598",
        accent_success="#b8bb26",
        accent_warning="#fe8019",
        accent_error="#fb4934",
        accent_info="#83a598",
        border_primary="#504945",
        border_secondary="#3c3836",
        border_focus="#fabd2f",
        selection_bg="#504945",
        cursor="#ebdbb2",
    ),
    "dracula": Palette(
        name="dracula",
        description="Deep purple with pastel accents — modern and vibrant",
        bg_primary="#282a36",
        bg_secondary="#282a36",
        bg_surface="#44475a",
        bg_inset="#1a1b26",
        text_primary="#f8f8f2",
        text_secondary="#bfbfcf",
        text_disabled="#6272a4",
        accent_primary="#bd93f9",
        accent_secondary="#ff79c6",
        accent_success="#50fa7b",
        accent_warning="#f1fa8c",
        accent_error="#ff5555",
        accent_info="#8be9fd",
        border_primary="#44475a",
        border_secondary="#282a36",
        border_focus="#bd93f9",
        selection_bg="#44475a",
        cursor="#f8f8f2",
    ),
    "turbopascal": Palette(
        name="turbopascal",
        description="Classic Turbo Pascal IDE — blue background, white text, ASCII art",
        bg_primary="#0000aa",
        bg_secondary="#000088",
        bg_surface="#0000cc",
        bg_inset="#000066",
        text_primary="#ffffff",
        text_secondary="#aaaaaa",
        text_disabled="#555555",
        accent_primary="#ffff55",
        accent_secondary="#ff55ff",
        accent_success="#55ff55",
        accent_warning="#ffff55",
        accent_error="#ff5555",
        accent_info="#55ffff",
        border_primary="#ffffff",
        border_secondary="#aaaaaa",
        border_focus="#ffff55",
        selection_bg="#aaaaaa",
        cursor="#ffffff",
    ),
}


def get_palette(name: str) -> Palette:
    """Get a palette by name. Falls back to midnight if not found."""
    return PALETTES.get(name, PALETTES["midnight"])


def list_palettes() -> list[str]:
    """List all available palette names."""
    return list(PALETTES.keys())
