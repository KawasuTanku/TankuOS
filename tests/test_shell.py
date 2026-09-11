"""Tests for TankuOS core shell and pane."""

import pytest
from tankuos.shell import Shell
from tankuos.pane import Pane, PaneTitleBar, PaneContent
from tankuos.theme import theme, Theme


class TestPane:
    def test_pane_creation(self):
        pane = Pane(title="Test", command="/bin/bash", pane_id="test-1")
        assert pane.title == "Test"
        assert pane.command == "/bin/bash"
        assert pane.pane_id == "test-1"

    def test_pane_default_id(self):
        pane = Pane(title="Test")
        assert pane.pane_id.startswith("pane-")

    def test_pane_title_bar_render(self):
        bar = PaneTitleBar(title="Test", pane_id="t1")
        bar.focused = True
        result = bar.render()
        assert "Test" in result

    def test_pane_content_render(self):
        content = PaneContent(pane_id="t1")
        content.text = "Hello World"
        result = content.render()
        assert "Hello World" in result


class TestShell:
    def test_shell_creation(self):
        shell = Shell()
        assert shell.theme_name == "midnight"
        assert isinstance(shell.panes, dict)

    def test_add_pane(self):
        shell = Shell()
        pane = shell.add_pane("Test", "/bin/bash", "test-1")
        assert "test-1" in shell.panes
        assert pane.title == "Test"

    def test_remove_pane(self):
        shell = Shell()
        shell.add_pane("Test", "/bin/bash", "test-1")
        shell.remove_pane("test-1")
        assert "test-1" not in shell.panes

    def test_focus_pane(self):
        shell = Shell()
        shell.add_pane("Test", "/bin/bash", "test-1")
        # Mock focus() since it requires an active Textual app context
        shell.panes["test-1"].focus = lambda: None
        shell.focus_pane("test-1")
        assert shell.active_pane_id == "test-1"
        assert shell.panes["test-1"].has_focus is True

    def test_cycle_theme(self):
        shell = Shell()
        shell.action_cycle_theme()
        assert shell.theme_name == "nord"
        shell.action_cycle_theme()
        assert shell.theme_name == "gruvbox"
        shell.action_cycle_theme()
        assert shell.theme_name == "dracula"
        shell.action_cycle_theme()
        assert shell.theme_name == "midnight"
        # Reset
        theme.set_palette("midnight")
