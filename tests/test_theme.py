"""Tests for TankuOS theme system."""

import pytest
from tankuos.theme import Theme, theme
from tankuos.palettes import Palette, get_palette, list_palettes, PALETTES


class TestPalettes:
    def test_all_palettes_exist(self):
        assert "midnight" in PALETTES
        assert "nord" in PALETTES
        assert "gruvbox" in PALETTES
        assert "dracula" in PALETTES

    def test_palette_has_all_colors(self):
        for name, palette in PALETTES.items():
            assert isinstance(palette, Palette)
            assert palette.name == name
            for attr in [
                "bg_primary", "bg_secondary", "bg_surface", "bg_inset",
                "text_primary", "text_secondary", "text_disabled",
                "accent_primary", "accent_secondary", "accent_success",
                "accent_warning", "accent_error", "accent_info",
                "border_primary", "border_secondary", "border_focus",
                "selection_bg", "cursor",
            ]:
                value = getattr(palette, attr)
                assert isinstance(value, str)
                assert value.startswith("#")

    def test_get_palette_valid(self):
        p = get_palette("nord")
        assert p.name == "nord"

    def test_get_palette_invalid_falls_back(self):
        p = get_palette("nonexistent")
        assert p.name == "midnight"

    def test_list_palettes(self):
        names = list_palettes()
        assert "midnight" in names
        assert "nord" in names


class TestTheme:
    def setup_method(self):
        """Reset theme to default before each test."""
        Theme().set_palette("midnight")

    def teardown_method(self):
        """Clean up theme after each test."""
        Theme().set_palette("midnight")

    def test_singleton(self):
        t1 = Theme()
        t2 = Theme()
        assert t1 is t2

    def test_default_palette(self):
        t = Theme()
        # Default is midnight
        assert t.palette.name == "midnight"

    def test_set_palette(self):
        t = Theme()
        t.set_palette("nord")
        assert t.palette.name == "nord"

    def test_color_accessors(self):
        t = Theme()
        assert t.bg_primary == t.palette.bg_primary
        assert t.accent_primary == t.palette.accent_primary
        assert t.text_primary == t.palette.text_primary

    def test_on_change_callback(self):
        t = Theme()
        called = []

        def on_change(palette):
            called.append(palette.name)

        t.on_change(on_change)
        t.set_palette("dracula")
        assert "dracula" in called
        t.remove_listener(on_change)
