"""Tests for TankuOS layout persistence."""

import os
import pytest
from pathlib import Path
from tankuos.layout import (
    LayoutManager,
    Layout,
    PaneState,
    CONFIG_DIR,
    LAYOUTS_FILE,
)


@pytest.fixture
def tmp_layout_manager(tmp_path):
    """Create a LayoutManager with a temp config dir."""
    manager = LayoutManager(config_dir=tmp_path / "tankuos")
    return manager


class TestPaneState:
    def test_create(self):
        state = PaneState(title="Test", command="/bin/bash", pane_id="t1")
        assert state.title == "Test"
        assert state.command == "/bin/bash"
        assert state.pane_id == "t1"
        assert state.row == 0
        assert state.col == 0

    def test_defaults(self):
        state = PaneState(title="T", command="cmd", pane_id="p1")
        assert state.row_span == 1
        assert state.col_span == 1
        assert state.focused is False


class TestLayout:
    def test_create(self):
        layout = Layout(name="test")
        assert layout.name == "test"
        assert layout.theme == "midnight"
        assert layout.grid_rows == 2
        assert layout.grid_cols == 2
        assert layout.panes == []

    def test_timestamps(self):
        layout = Layout(name="test")
        assert layout.created != ""
        assert layout.updated != ""

    def test_with_panes(self):
        panes = [
            PaneState(title="A", command="cmd1", pane_id="p1"),
            PaneState(title="B", command="cmd2", pane_id="p2"),
        ]
        layout = Layout(name="test", panes=panes)
        assert len(layout.panes) == 2


class TestLayoutManager:
    def test_ensure_config_dir(self, tmp_layout_manager):
        assert tmp_layout_manager.config_dir.exists()

    def test_save_and_load(self, tmp_layout_manager):
        layout = Layout(
            name="test",
            theme="nord",
            panes=[
                PaneState(title="Shell", command="/bin/bash", pane_id="main"),
            ],
        )
        tmp_layout_manager.save_layout(layout)
        
        loaded = tmp_layout_manager.load_layout("test")
        assert loaded is not None
        assert loaded.name == "test"
        assert loaded.theme == "nord"
        assert len(loaded.panes) == 1
        assert loaded.panes[0].title == "Shell"

    def test_load_nonexistent(self, tmp_layout_manager):
        assert tmp_layout_manager.load_layout("nonexistent") is None

    def test_list_layouts(self, tmp_layout_manager):
        assert tmp_layout_manager.list_layouts() == []
        
        tmp_layout_manager.save_layout(Layout(name="a"))
        tmp_layout_manager.save_layout(Layout(name="b"))
        
        layouts = tmp_layout_manager.list_layouts()
        assert "a" in layouts
        assert "b" in layouts

    def test_delete_layout(self, tmp_layout_manager):
        tmp_layout_manager.save_layout(Layout(name="to-delete"))
        assert tmp_layout_manager.delete_layout("to-delete") is True
        assert tmp_layout_manager.load_layout("to-delete") is None

    def test_delete_nonexistent(self, tmp_layout_manager):
        assert tmp_layout_manager.delete_layout("nonexistent") is False

    def test_overwrite(self, tmp_layout_manager):
        layout = Layout(name="test", theme="midnight")
        tmp_layout_manager.save_layout(layout)
        
        layout.theme = "dracula"
        tmp_layout_manager.save_layout(layout)
        
        loaded = tmp_layout_manager.load_layout("test")
        assert loaded.theme == "dracula"

    def test_multiple_panes(self, tmp_layout_manager):
        layout = Layout(
            name="multi",
            grid_rows=2,
            grid_cols=2,
            panes=[
                PaneState(title="A", command="cmd1", pane_id="p1", row=0, col=0),
                PaneState(title="B", command="cmd2", pane_id="p2", row=0, col=1),
                PaneState(title="C", command="cmd3", pane_id="p3", row=1, col=0),
            ],
        )
        tmp_layout_manager.save_layout(layout)
        
        loaded = tmp_layout_manager.load_layout("multi")
        assert len(loaded.panes) == 3
        assert loaded.grid_rows == 2
        assert loaded.grid_cols == 2
