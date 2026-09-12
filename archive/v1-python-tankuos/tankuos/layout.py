"""Layout persistence for TankuOS.

Saves and restores pane layouts to TOML files.
Layouts remember which apps are open, their positions, and sizes.
"""

import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import toml

from tankuos.theme import theme


CONFIG_DIR = Path.home() / ".config" / "tankuos"
LAYOUTS_FILE = CONFIG_DIR / "layouts.toml"


@dataclass
class PaneState:
    """State of a single pane."""
    title: str
    command: str
    pane_id: str
    row: int = 0
    col: int = 0
    row_span: int = 1
    col_span: int = 1
    focused: bool = False


@dataclass
class Layout:
    """A complete desktop layout."""
    name: str
    created: str = ""
    updated: str = ""
    theme: str = "midnight"
    grid_rows: int = 2
    grid_cols: int = 2
    panes: List[PaneState] = field(default_factory=list)

    def __post_init__(self):
        if not self.created:
            self.created = datetime.now().isoformat()
        if not self.updated:
            self.updated = datetime.now().isoformat()


class LayoutManager:
    """Manages saving and loading of TankuOS layouts."""

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or CONFIG_DIR
        self.layouts_file = self.config_dir / "layouts.toml"
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Create config directory if it doesn't exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def save_layout(self, layout: Layout) -> None:
        """Save a layout to disk."""
        layout.updated = datetime.now().isoformat()
        
        # Load existing layouts
        data = self._load_all()
        
        # Convert to dict and store
        data[layout.name] = {
            "created": layout.created,
            "updated": layout.updated,
            "theme": layout.theme,
            "grid_rows": layout.grid_rows,
            "grid_cols": layout.grid_cols,
            "panes": [asdict(p) for p in layout.panes],
        }
        
        # Write back
        with open(self.layouts_file, "w") as f:
            toml.dump(data, f)

    def load_layout(self, name: str) -> Optional[Layout]:
        """Load a layout by name."""
        data = self._load_all()
        if name not in data:
            return None
        
        layout_data = data[name]
        panes = [PaneState(**p) for p in layout_data.get("panes", [])]
        
        return Layout(
            name=name,
            created=layout_data.get("created", ""),
            updated=layout_data.get("updated", ""),
            theme=layout_data.get("theme", "midnight"),
            grid_rows=layout_data.get("grid_rows", 2),
            grid_cols=layout_data.get("grid_cols", 2),
            panes=panes,
        )

    def delete_layout(self, name: str) -> bool:
        """Delete a layout. Returns True if deleted."""
        data = self._load_all()
        if name in data:
            del data[name]
            with open(self.layouts_file, "w") as f:
                toml.dump(data, f)
            return True
        return False

    def list_layouts(self) -> List[str]:
        """List all saved layout names."""
        data = self._load_all()
        return list(data.keys())

    def _load_all(self) -> dict:
        """Load all layouts from disk."""
        if not self.layouts_file.exists():
            return {}
        try:
            with open(self.layouts_file, "r") as f:
                return toml.load(f)
        except Exception:
            return {}

    def save_from_shell(self, name: str, shell) -> Layout:
        """Extract layout state from a running shell and save."""
        panes = []
        for pane_id, pane in shell.panes.items():
            panes.append(PaneState(
                title=pane.title,
                command=pane.command,
                pane_id=pane_id,
                row=getattr(pane, "row", 0),
                col=getattr(pane, "col", 0),
                row_span=getattr(pane, "row_span", 1),
                col_span=getattr(pane, "col_span", 1),
                focused=pane_id == shell.active_pane_id,
            ))
        
        layout = Layout(
            name=name,
            theme=shell.theme_name,
            grid_rows=getattr(shell, "grid_rows", 2),
            grid_cols=getattr(shell, "grid_cols", 2),
            panes=panes,
        )
        
        self.save_layout(layout)
        return layout

    def restore_to_shell(self, name: str, shell) -> bool:
        """Restore a layout to a running shell."""
        layout = self.load_layout(name)
        if not layout:
            return False
        
        # Clear existing panes
        for pane_id in list(shell.panes.keys()):
            shell.remove_pane(pane_id)
        
        # Restore theme
        shell.theme_name = layout.theme
        theme.set_palette(layout.theme)
        
        # Restore panes
        for pane_state in layout.panes:
            pane = shell.add_pane(
                title=pane_state.title,
                command=pane_state.command,
                pane_id=pane_state.pane_id,
            )
            pane.row = pane_state.row
            pane.col = pane_state.col
            pane.row_span = pane_state.row_span
            pane.col_span = pane_state.col_span
        
        # Focus the last focused pane
        for pane_state in layout.panes:
            if pane_state.focused:
                shell.focus_pane(pane_state.pane_id)
                break
        
        return True


# Global singleton
layout_manager = LayoutManager()
