"""Tests for TankuOS core shell and pane."""

import pytest
from tankuos.shell import Shell, AppMenuItem, APP_ICONS
from tankuos.pane import Pane, ClosePaneRequest
from tankuos.theme import theme, Theme
from textual.widgets import Static


class TestAppIcons:
    def test_icons_exist(self):
        assert "Shell" in APP_ICONS
        assert "Retirement" in APP_ICONS
        assert "Monster" in APP_ICONS
        assert "MontcoMonitor" in APP_ICONS
        assert "Glances" in APP_ICONS

    def test_default_icon(self):
        assert "default" in APP_ICONS


class TestAppMenuItem:
    def test_create(self):
        item = AppMenuItem(name="Test", icon="󰲌")
        assert item.app_name == "Test"
        assert item.icon == "󰲌"

    def test_render(self):
        item = AppMenuItem(name="Test", icon="󰲌")
        result = item.render()
        assert "Test" in result
        assert "󰲌" in result


class TestPane:
    def test_pane_creation(self):
        content = Static("Test content")
        pane = Pane(title="Test", content=content, pane_id="test-1")
        assert pane.title == "Test"
        assert pane.pane_id == "test-1"

    def test_pane_default_id(self):
        content = Static("Test content")
        pane = Pane(title="Test", content=content)
        assert pane.pane_id.startswith("pane-")


class TestShell:
    def test_shell_creation(self):
        shell = Shell()
        assert shell.theme_name == "turbopascal"
        assert isinstance(shell.panes, dict)

    def test_cycle_theme(self):
        shell = Shell()
        shell.action_cycle_theme()
        assert shell.theme_name == "midnight"
        shell.action_cycle_theme()
        assert shell.theme_name == "nord"
        shell.action_cycle_theme()
        assert shell.theme_name == "gruvbox"
        shell.action_cycle_theme()
        assert shell.theme_name == "turbopascal"
        # Reset
        theme.set_palette("midnight")


class TestClosePaneRequest:
    def test_message(self):
        msg = ClosePaneRequest("pane-test")
        assert msg.pane_id == "pane-test"
