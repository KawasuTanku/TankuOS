"""TankuOS v2 — Retro desktop on curses."""

import curses
import os
import subprocess
from typing import Dict, List, Optional, Tuple


class Pane:
    """A single pane in the desktop."""

    def __init__(self, pane_id: str, title: str, x: int, y: int, w: int, h: int):
        self.pane_id = pane_id
        self.title = title
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.focused = False
        self.content_lines: List[str] = []
        self.scroll_offset = 0

    def resize(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def add_content(self, text: str):
        """Add text to the pane's content buffer."""
        lines = text.split('\n')
        self.content_lines.extend(lines)
        # Auto-scroll to bottom if we have more lines than visible
        visible_lines = self.h - 3  # minus titlebar and borders
        if len(self.content_lines) > visible_lines:
            self.scroll_offset = len(self.content_lines) - visible_lines

    def clear(self):
        self.content_lines = []
        self.scroll_offset = 0

    def draw(self, stdscr):
        """Draw this pane on screen."""
        if self.w < 3 or self.h < 3:
            return

        # Determine colors
        if self.focused:
            title_color = curses.color_pair(3) | curses.A_BOLD  # green
            border_color = curses.color_pair(4)  # accent
        else:
            title_color = curses.color_pair(1) | curses.A_BOLD  # primary
            border_color = curses.color_pair(1)  # primary

        # Draw border
        try:
            # Top border with title
            stdscr.addch(self.y, self.x, '┌', border_color)
            title_text = f" {self.title} "
            title_x = self.x + 2
            for i, ch in enumerate(title_text):
                if title_x + i < self.x + self.w - 1:
                    stdscr.addch(self.y, title_x + i, ch, title_color)
            # Fill rest of top border
            title_end = title_x + len(title_text)
            for i in range(title_end, self.x + self.w - 1):
                stdscr.addch(self.y, i, '─', border_color)
            stdscr.addch(self.y, self.x + self.w - 1, '┐', border_color)

            # Bottom border
            stdscr.addch(self.y + self.h - 1, self.x, '└', border_color)
            for i in range(1, self.w - 1):
                stdscr.addch(self.y + self.h - 1, self.x + i, '─', border_color)
            stdscr.addch(self.y + self.h - 1, self.x + self.w - 1, '┘', border_color)

            # Side borders
            for row in range(1, self.h - 1):
                stdscr.addch(self.y + row, self.x, '│', border_color)
                stdscr.addch(self.y + row, self.x + self.w - 1, '│', border_color)

            # Clear content area
            for row in range(1, self.h - 1):
                for col in range(1, self.w - 1):
                    stdscr.addch(self.y + row, self.x + col, ' ')

            # Draw content
            visible_lines = self.h - 3
            start = self.scroll_offset
            end = min(start + visible_lines, len(self.content_lines))
            for i, line_idx in enumerate(range(start, end)):
                line = self.content_lines[line_idx]
                # Truncate to fit
                max_w = self.w - 2
                if len(line) > max_w:
                    line = line[:max_w]
                try:
                    stdscr.addstr(self.y + 1 + (i - start), self.x + 1, line)
                except curses.error:
                    pass

        except curses.error:
            pass


class ShellPane(Pane):
    """A pane running an interactive shell."""

    def __init__(self, pane_id: str, x: int, y: int, w: int, h: int):
        super().__init__(pane_id, "Shell", x, y, w, h)
        self.input_buffer = ""
        self.history: List[str] = []
        self.history_idx = 0
        self.add_content("$ ")

    def execute(self, command: str):
        """Execute a shell command and capture output."""
        self.history.append(command)
        self.history_idx = len(self.history)

        if not command.strip():
            self.add_content("$ ")
            return

        if command.strip() == "clear":
            self.clear()
            self.add_content("$ ")
            return

        if command.strip() == "help":
            self.add_content("Available commands: help, clear, ls, pwd, date, whoami, echo")
            self.add_content("$ ")
            return

        try:
            # Save curses state, leave curses mode, run command, restore state
            curses.def_prog_mode()
            curses.endwin()

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5,
                env={**os.environ, "TERM": "xterm-256color"}
            )
            output = result.stdout + result.stderr
            if output.strip():
                self.add_content(output.rstrip())

            # Restore curses mode
            curses.reset_prog_mode()
            curses.doupdate()
        except subprocess.TimeoutExpired:
            self.add_content("Command timed out")
            curses.reset_prog_mode()
            curses.doupdate()
        except Exception as e:
            self.add_content(f"Error: {e}")
            curses.reset_prog_mode()
            curses.doupdate()

        self.add_content("$ ")

    def backspace(self):
        if self.input_buffer:
            self.input_buffer = self.input_buffer[:-1]
            # Redraw input line
            self._redraw_input()

    def _redraw_input(self):
        """Redraw the current input line."""
        # Remove last line (the current $ prompt) and redraw
        if self.content_lines and self.content_lines[-1].startswith("$ "):
            self.content_lines.pop()
        self.add_content(f"$ {self.input_buffer}")

    def add_char(self, ch: str):
        self.input_buffer += ch
        # Update last line
        if self.content_lines and self.content_lines[-1].startswith("$ "):
            self.content_lines[-1] = f"$ {self.input_buffer}"
        else:
            self.add_content(f"$ {self.input_buffer}")

    def submit(self):
        cmd = self.input_buffer.strip()
        self.input_buffer = ""
        self.execute(cmd)


class TankuOS:
    """Main TankuOS desktop."""

    def __init__(self):
        self.panes: Dict[str, Pane] = {}
        self.pane_order: List[str] = []
        self.active_pane_id: Optional[str] = None
        self.next_id = 0
        self.menubar_items = ["TankuOS", "View", "Apps", "Help"]
        self.active_menu = -1
        self.stdscr = None
        self.running = False

    def init_colors(self):
        """Initialize color pairs."""
        curses.start_color()
        curses.use_default_colors()

        # Color pairs
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)    # primary
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLUE)   # accent
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_GREEN)   # focused title
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # focused border
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)   # menu highlight
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)   # statusbar

    def launch_app(self, app_name: str):
        """Launch an app in a new pane."""
        pane_id = f"pane-{self.next_id}"
        self.next_id += 1

        # Calculate layout
        self._calculate_layout()

        # Create pane
        if app_name == "Shell":
            # Find position for new pane
            idx = len(self.panes)
            max_panes = self._max_panes()
            if idx >= max_panes:
                return  # No room

            # Get geometry from layout
            x, y, w, h = self._pane_geometry(idx)
            pane = ShellPane(pane_id, x, y, w, h)
        else:
            x, y, w, h = self._pane_geometry(len(self.panes))
            pane = Pane(pane_id, app_name, x, y, w, h)
            pane.add_content(f"{app_name}")
            pane.add_content("")
            pane.add_content("[Plugin content goes here]")

        self.panes[pane_id] = pane
        self.pane_order.append(pane_id)
        self.active_pane_id = pane_id
        self._update_focus()

    def close_pane(self, pane_id: str):
        """Close a pane."""
        if pane_id in self.panes:
            del self.panes[pane_id]
            self.pane_order.remove(pane_id)
            if self.active_pane_id == pane_id:
                self.active_pane_id = self.pane_order[-1] if self.pane_order else None
            self._calculate_layout()
            self._update_focus()

    def _max_panes(self) -> int:
        """Max panes based on screen size."""
        if not self.stdscr:
            return 3
        h, w = self.stdscr.getmaxyx()
        # Each pane needs at least 20 cols and 10 rows
        max_cols = max(1, (w - 4) // 40)
        max_rows = max(1, (h - 4) // 12)
        return min(max_cols * max_rows, 6)

    def _pane_geometry(self, idx: int) -> Tuple[int, int, int, int]:
        """Calculate geometry for pane at given index."""
        if not self.stdscr:
            return (0, 0, 80, 24)

        h, w = self.stdscr.getmaxyx()
        menubar_h = 1
        statusbar_h = 1
        grid_top = menubar_h
        grid_h = h - menubar_h - statusbar_h
        grid_w = w

        n = len(self.panes) + (1 if idx >= len(self.panes) else 0)
        if n == 0:
            n = 1

        # Simple layout: divide horizontally
        cols = min(n, 3)
        rows = (n + cols - 1) // cols

        cell_w = grid_w // cols
        cell_h = grid_h // rows

        col = idx % cols
        row = idx // cols

        x = col * cell_w
        y = grid_top + row * cell_h
        pw = cell_w
        ph = cell_h

        return (x, y, pw, ph)

    def _calculate_layout(self):
        """Recalculate pane geometries."""
        for i, pane_id in enumerate(self.pane_order):
            pane = self.panes[pane_id]
            x, y, w, h = self._pane_geometry(i)
            pane.resize(x, y, w, h)

    def _update_focus(self):
        """Update focus state of all panes."""
        for pane_id, pane in self.panes.items():
            pane.focused = (pane_id == self.active_pane_id)

    def draw_menubar(self):
        """Draw the menubar."""
        if not self.stdscr:
            return
        h, w = self.stdscr.getmaxyx()
        try:
            # Clear menubar line
            for col in range(w):
                self.stdscr.addch(0, col, ' ', curses.color_pair(1))

            x = 1
            for i, item in enumerate(self.menubar_items):
                text = f" {item} "
                if i == self.active_menu:
                    attr = curses.color_pair(5) | curses.A_BOLD
                else:
                    attr = curses.color_pair(1) | curses.A_BOLD
                try:
                    self.stdscr.addstr(0, x, text, attr)
                except curses.error:
                    pass
                x += len(text) + 1
        except curses.error:
            pass

    def draw_statusbar(self):
        """Draw the statusbar."""
        if not self.stdscr:
            return
        h, w = self.stdscr.getmaxyx()
        try:
            y = h - 1
            for col in range(w):
                self.stdscr.addch(y, col, ' ', curses.color_pair(6))
            status = " F1 Help | F2 Theme | F3 Apps | Ctrl+Q Quit"
            self.stdscr.addstr(y, 0, status[:w-1], curses.color_pair(6))
        except curses.error:
            pass

    def draw(self):
        """Draw the entire desktop."""
        if not self.stdscr:
            return

        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()

        # Draw menubar
        self.draw_menubar()

        # Draw statusbar
        self.draw_statusbar()

        # Draw panes
        for pane_id in self.pane_order:
            self.panes[pane_id].draw(self.stdscr)

        self.stdscr.refresh()

    def run(self, stdscr):
        """Main run loop."""
        self.stdscr = stdscr
        curses.curs_set(0)  # Hide cursor
        self.init_colors()
        stdscr.keypad(True)
        stdscr.nodelay(True)  # Non-blocking input

        self.running = True
        dirty = True  # Track if screen needs redraw

        # Launch initial shell
        self.launch_app("Shell")

        while self.running:
            if dirty:
                self.draw()
                dirty = False

            try:
                ch = stdscr.getch()
            except curses.error:
                ch = -1

            if ch == -1:
                # No input, sleep to avoid busy loop
                curses.napms(30)
                continue

            dirty = True  # Mark screen as needing redraw

            # Handle keypress
            if ch == curses.KEY_RESIZE:
                self._calculate_layout()
                continue

            if ch == ord('q') - ord('a') + 1:  # Ctrl+Q
                self.running = False
                continue

            if ch == curses.KEY_F1:
                self.show_help()
                continue

            if ch == curses.KEY_F3:
                self.show_apps()
                continue

            if ch == 9:  # Tab - cycle panes
                self.cycle_pane()
                continue

            if ch == 27:  # Escape
                self.active_menu = -1
                continue

            # Pass to active pane if it's a ShellPane
            if self.active_pane_id and self.active_pane_id in self.panes:
                pane = self.panes[self.active_pane_id]
                if isinstance(pane, ShellPane):
                    if ch == 10 or ch == 13:  # Enter
                        pane.submit()
                    elif ch == curses.KEY_BACKSPACE or ch == 127:
                        pane.backspace()
                    elif ch == curses.KEY_UP:
                        # History up
                        if pane.history and pane.history_idx > 0:
                            pane.history_idx -= 1
                            pane.input_buffer = pane.history[pane.history_idx]
                            pane._redraw_input()
                    elif ch == curses.KEY_DOWN:
                        # History down
                        if pane.history and pane.history_idx < len(pane.history) - 1:
                            pane.history_idx += 1
                            pane.input_buffer = pane.history[pane.history_idx]
                            pane._redraw_input()
                        elif pane.history_idx == len(pane.history) - 1:
                            pane.history_idx = len(pane.history)
                            pane.input_buffer = ""
                            pane._redraw_input()
                    elif 32 <= ch < 127:
                        pane.add_char(chr(ch))

    def cycle_pane(self):
        """Cycle focus to next pane."""
        if not self.pane_order:
            return
        if self.active_pane_id is None:
            self.active_pane_id = self.pane_order[0]
        else:
            idx = self.pane_order.index(self.active_pane_id)
            idx = (idx + 1) % len(self.pane_order)
            self.active_pane_id = self.pane_order[idx]
        self._update_focus()

    def show_help(self):
        """Show help overlay."""
        if not self.stdscr:
            return
        h, w = self.stdscr.getmaxyx()
        help_text = [
            "TankuOS Help",
            "",
            "F1      - This help",
            "F2      - Cycle theme",
            "F3      - Apps menu",
            "Tab     - Cycle panes",
            "Ctrl+Q  - Quit",
            "",
            "Press any key to close..."
        ]
        # Simple popup
        max_w = max(len(line) for line in help_text) + 4
        max_h = len(help_text) + 4
        start_y = (h - max_h) // 2
        start_x = (w - max_w) // 2

        # Draw box
        for row in range(max_h):
            for col in range(max_w):
                y = start_y + row
                x = start_x + col
                if 0 <= y < h and 0 <= x < w:
                    if row == 0 or row == max_h - 1:
                        self.stdscr.addch(y, x, '─', curses.color_pair(1))
                    elif col == 0 or col == max_w - 1:
                        self.stdscr.addch(y, x, '│', curses.color_pair(1))
                    else:
                        self.stdscr.addch(y, x, ' ')

        # Corners
        self.stdscr.addch(start_y, start_x, '┌', curses.color_pair(1))
        self.stdscr.addch(start_y, start_x + max_w - 1, '┐', curses.color_pair(1))
        self.stdscr.addch(start_y + max_h - 1, start_x, '└', curses.color_pair(1))
        self.stdscr.addch(start_y + max_h - 1, start_x + max_w - 1, '┘', curses.color_pair(1))

        # Text
        for i, line in enumerate(help_text):
            y = start_y + 2 + i
            x = start_x + 2
            if 0 <= y < h and 0 <= x < w:
                try:
                    self.stdscr.addstr(y, x, line[:max_w-4], curses.A_BOLD if i == 0 else curses.A_NORMAL)
                except curses.error:
                    pass

        self.stdscr.refresh()
        self.stdscr.getch()

    def show_apps(self):
        """Show apps menu."""
        if not self.stdscr:
            return
        h, w = self.stdscr.getmaxyx()
        apps = ["Shell", "Retirement", "Monster", "MontcoMonitor", "Glances"]
        max_w = 24
        max_h = len(apps) + 4
        start_y = (h - max_h) // 2
        start_x = (w - max_w) // 2

        # Draw box
        for row in range(max_h):
            for col in range(max_w):
                y = start_y + row
                x = start_x + col
                if 0 <= y < h and 0 <= x < w:
                    if row == 0 or row == max_h - 1:
                        self.stdscr.addch(y, x, '─', curses.color_pair(1))
                    elif col == 0 or col == max_w - 1:
                        self.stdscr.addch(y, x, '│', curses.color_pair(1))
                    else:
                        self.stdscr.addch(y, x, ' ')

        self.stdscr.addch(start_y, start_x, '┌', curses.color_pair(1))
        self.stdscr.addch(start_y, start_x + max_w - 1, '┐', curses.color_pair(1))
        self.stdscr.addch(start_y + max_h - 1, start_x, '└', curses.color_pair(1))
        self.stdscr.addch(start_y + max_h - 1, start_x + max_w - 1, '┘', curses.color_pair(1))

        # Title
        title = " Applications "
        self.stdscr.addstr(start_y + 1, start_x + 2, title, curses.A_BOLD)

        # Apps
        for i, app in enumerate(apps):
            y = start_y + 3 + i
            x = start_x + 2
            if 0 <= y < h and 0 <= x < w:
                try:
                    self.stdscr.addstr(y, x, f" {app:<20}")
                except curses.error:
                    pass

        self.stdscr.refresh()

        # Simple selection
        selected = 0
        while True:
            # Redraw selection
            for i, app in enumerate(apps):
                y = start_y + 3 + i
                x = start_x + 2
                if 0 <= y < h and 0 <= x < w:
                    attr = curses.color_pair(5) | curses.A_BOLD if i == selected else curses.A_NORMAL
                    try:
                        self.stdscr.addstr(y, x, f" {app:<20}", attr)
                    except curses.error:
                        pass
            self.stdscr.refresh()

            ch = self.stdscr.getch()
            if ch == 27:  # Escape
                return
            elif ch == curses.KEY_UP:
                selected = (selected - 1) % len(apps)
            elif ch == curses.KEY_DOWN:
                selected = (selected + 1) % len(apps)
            elif ch == 10 or ch == 13:  # Enter
                self.launch_app(apps[selected])
                return


def main():
    """Entry point."""
    app = TankuOS()
    curses.wrapper(app.run)


if __name__ == "__main__":
    main()
