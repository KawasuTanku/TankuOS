"""TankuOS v2 — Retro desktop on curses."""

import curses
import os
import subprocess
import signal
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
        lines = text.split('\n')
        self.content_lines.extend(lines)
        visible_lines = max(1, self.h - 3)
        if len(self.content_lines) > visible_lines:
            self.scroll_offset = len(self.content_lines) - visible_lines

    def clear(self):
        self.content_lines = []
        self.scroll_offset = 0

    def draw(self, stdscr):
        if self.w < 3 or self.h < 3:
            return

        if self.focused:
            title_color = curses.color_pair(3) | curses.A_BOLD
            border_color = curses.color_pair(4) | curses.A_BOLD
        else:
            title_color = curses.color_pair(1) | curses.A_BOLD
            border_color = curses.color_pair(1)

        try:
            # Top border
            stdscr.addch(self.y, self.x, '┌', border_color)
            title_text = f" {self.title} "
            title_x = self.x + 2
            for i, ch in enumerate(title_text):
                if title_x + i < self.x + self.w - 1:
                    stdscr.addch(self.y, title_x + i, ch, title_color)
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
                line = ' ' * (self.w - 2)
                try:
                    stdscr.addstr(self.y + row, self.x + 1, line)
                except curses.error:
                    pass

            # Draw content
            visible_lines = max(1, self.h - 3)
            start = self.scroll_offset
            end = min(start + visible_lines, len(self.content_lines))
            for i, line_idx in enumerate(range(start, end)):
                line = self.content_lines[line_idx]
                max_w = self.w - 2
                if len(line) > max_w:
                    line = line[:max_w]
                try:
                    stdscr.addstr(self.y + 1 + i, self.x + 1, line)
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
            self.add_content("Commands: help, clear, ls, pwd, date, whoami, echo")
            self.add_content("$ ")
            return

        try:
            curses.def_prog_mode()
            curses.endwin()
            try:
                curses.nocbreak()
                curses.echo()
                curses.nl(True)
            except:
                pass

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

            try:
                curses.nonl()
                curses.noecho()
                curses.cbreak()
            except:
                pass
            curses.reset_prog_mode()
            curses.doupdate()
        except subprocess.TimeoutExpired:
            self.add_content("Command timed out")
            try:
                curses.nonl()
                curses.noecho()
                curses.cbreak()
            except:
                pass
            curses.reset_prog_mode()
            curses.doupdate()
        except Exception as e:
            self.add_content(f"Error: {e}")
            try:
                curses.nonl()
                curses.noecho()
                curses.cbreak()
            except:
                pass
            curses.reset_prog_mode()
            curses.doupdate()

        self.add_content("$ ")

    def backspace(self):
        if self.input_buffer:
            self.input_buffer = self.input_buffer[:-1]
            self._redraw_input()

    def _redraw_input(self):
        if self.content_lines and self.content_lines[-1].startswith("$ "):
            self.content_lines.pop()
        self.add_content(f"$ {self.input_buffer}")

    def add_char(self, ch: str):
        self.input_buffer += ch
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
        self.stdscr = None
        self.running = False
        # Menu state machine
        self.menu_active = False  # True when a menu overlay is showing
        self.menu_type = None     # 'apps', 'help', or None
        self.menu_selection = 0
        self.apps = ["Shell", "Retirement", "Monster", "MontcoMonitor", "Glances"]

    def init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)    # primary
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLUE)   # accent
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_GREEN)   # focused title
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # focused border
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)   # menu highlight
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)   # statusbar

    def launch_app(self, app_name: str):
        pane_id = f"pane-{self.next_id}"
        self.next_id += 1

        if app_name == "Shell":
            pane = ShellPane(pane_id, 0, 0, 10, 10)
        else:
            pane = Pane(pane_id, app_name, 0, 0, 10, 10)
            pane.add_content(f"{app_name}")
            pane.add_content("")
            pane.add_content("[Plugin content goes here]")

        self.panes[pane_id] = pane
        self.pane_order.append(pane_id)
        self.active_pane_id = pane_id

        self._calculate_layout()
        self._update_focus()

    def close_pane(self, pane_id: str):
        if pane_id in self.panes:
            del self.panes[pane_id]
            self.pane_order.remove(pane_id)
            if self.active_pane_id == pane_id:
                self.active_pane_id = self.pane_order[-1] if self.pane_order else None
            self._calculate_layout()
            self._update_focus()

    def _pane_geometry(self, idx: int, total: int) -> Tuple[int, int, int, int]:
        if not self.stdscr:
            return (0, 0, 80, 24)

        h, w = self.stdscr.getmaxyx()
        menubar_h = 1
        statusbar_h = 1
        grid_top = menubar_h
        grid_h = h - menubar_h - statusbar_h
        grid_w = w

        if total == 0:
            total = 1

        cols = min(total, 3)
        rows = (total + cols - 1) // cols

        cell_w = grid_w // cols
        cell_h = grid_h // rows

        # Distribute remainder pixels to last column/row
        rem_w = grid_w - (cell_w * cols)
        rem_h = grid_h - (cell_h * rows)

        col = idx % cols
        row = idx // cols

        x = col * cell_w
        y = grid_top + row * cell_h
        pw = cell_w + (rem_w if col == cols - 1 else 0)
        ph = cell_h + (rem_h if row == rows - 1 else 0)

        return (x, y, pw, ph)

    def _calculate_layout(self):
        total = len(self.pane_order)
        for i, pane_id in enumerate(self.pane_order):
            pane = self.panes[pane_id]
            x, y, w, h = self._pane_geometry(i, total)
            pane.resize(x, y, w, h)

    def _update_focus(self):
        for pane_id, pane in self.panes.items():
            pane.focused = (pane_id == self.active_pane_id)

    def draw_menubar(self):
        if not self.stdscr:
            return
        h, w = self.stdscr.getmaxyx()
        try:
            line = ' ' * w
            self.stdscr.addstr(0, 0, line, curses.color_pair(1))

            x = 1
            items = ["TankuOS", "View", "Apps", "Help"]
            for i, item in enumerate(items):
                text = f" {item} "
                attr = curses.color_pair(1) | curses.A_BOLD
                try:
                    self.stdscr.addstr(0, x, text, attr)
                except curses.error:
                    pass
                x += len(text) + 1
        except curses.error:
            pass

    def draw_statusbar(self):
        if not self.stdscr:
            return
        h, w = self.stdscr.getmaxyx()
        try:
            y = h - 1
            line = ' ' * w
            self.stdscr.addstr(y, 0, line, curses.color_pair(6))
            active = self.active_pane_id or "none"
            status = f" F1 Help | F3 Apps | Tab: cycle | Active: {active} | 'q' or Ctrl+Q: Quit"
            self.stdscr.addstr(y, 0, status[:w-1], curses.color_pair(6))
        except curses.error:
            pass

    def draw(self):
        if not self.stdscr:
            return

        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()

        self.draw_menubar()
        self.draw_statusbar()

        for pane_id in self.pane_order:
            self.panes[pane_id].draw(self.stdscr)

        # Draw menu overlay if active
        if self.menu_active:
            if self.menu_type == 'apps':
                self._draw_apps_menu()
            elif self.menu_type == 'help':
                self._draw_help_menu()

        self.stdscr.refresh()

    def _draw_apps_menu(self):
        """Draw apps menu as overlay."""
        if not self.stdscr:
            return
        h, w = self.stdscr.getmaxyx()
        max_w = 24
        max_h = len(self.apps) + 4
        start_y = max(1, (h - max_h) // 2)
        start_x = max(0, (w - max_w) // 2)

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

        if start_y < h and start_x < w:
            self.stdscr.addch(start_y, start_x, '┌', curses.color_pair(1))
        if start_y < h and start_x + max_w - 1 < w:
            self.stdscr.addch(start_y, start_x + max_w - 1, '┐', curses.color_pair(1))
        if start_y + max_h - 1 < h and start_x < w:
            self.stdscr.addch(start_y + max_h - 1, start_x, '└', curses.color_pair(1))
        if start_y + max_h - 1 < h and start_x + max_w - 1 < w:
            self.stdscr.addch(start_y + max_h - 1, start_x + max_w - 1, '┘', curses.color_pair(1))

        title = " Applications "
        if start_y + 1 < h:
            self.stdscr.addstr(start_y + 1, start_x + 2, title, curses.A_BOLD)

        for i, app in enumerate(self.apps):
            y = start_y + 3 + i
            x = start_x + 2
            if 0 <= y < h and 0 <= x < w:
                attr = curses.color_pair(5) | curses.A_BOLD if i == self.menu_selection else curses.A_NORMAL
                try:
                    self.stdscr.addstr(y, x, f" {app:<20}", attr)
                except curses.error:
                    pass

    def _draw_help_menu(self):
        """Draw help as overlay."""
        if not self.stdscr:
            return
        h, w = self.stdscr.getmaxyx()
        help_text = [
            "TankuOS Help",
            "",
            "F1      - This help",
            "F3      - Apps menu",
            "Tab     - Cycle panes",
            "'q'     - Quit",
            "",
            "Press any key to close..."
        ]
        max_w = max(len(line) for line in help_text) + 4
        max_h = len(help_text) + 4
        start_y = max(1, (h - max_h) // 2)
        start_x = max(0, (w - max_w) // 2)

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

        if start_y < h and start_x < w:
            self.stdscr.addch(start_y, start_x, '┌', curses.color_pair(1))
        if start_y < h and start_x + max_w - 1 < w:
            self.stdscr.addch(start_y, start_x + max_w - 1, '┐', curses.color_pair(1))
        if start_y + max_h - 1 < h and start_x < w:
            self.stdscr.addch(start_y + max_h - 1, start_x, '└', curses.color_pair(1))
        if start_y + max_h - 1 < h and start_x + max_w - 1 < w:
            self.stdscr.addch(start_y + max_h - 1, start_x + max_w - 1, '┘', curses.color_pair(1))

        for i, line in enumerate(help_text):
            y = start_y + 2 + i
            x = start_x + 2
            if 0 <= y < h and 0 <= x < w:
                try:
                    self.stdscr.addstr(y, x, line[:max_w-4], curses.A_BOLD if i == 0 else curses.A_NORMAL)
                except curses.error:
                    pass

    def run(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)
        self.init_colors()
        stdscr.keypad(True)
        stdscr.nodelay(True)

        self.running = True
        dirty = True

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
                curses.napms(50)
                continue

            dirty = True

            # Always handle quit first
            if ch == ord('q') or ch == ord('Q'):
                self.running = False
                continue

            if ch == curses.KEY_RESIZE:
                self.calculate_layout()
                continue

            # Handle menu state
            if self.menu_active:
                if ch == 27:  # Escape closes menu
                    self.menu_active = False
                    self.menu_type = None
                elif ch == curses.KEY_UP:
                    self.menu_selection = (self.menu_selection - 1) % len(self.apps)
                elif ch == curses.KEY_DOWN:
                    self.menu_selection = (self.menu_selection + 1) % len(self.apps)
                elif ch == 10 or ch == 13:  # Enter
                    if self.menu_type == 'apps':
                        self.launch_app(self.apps[self.menu_selection])
                    self.menu_active = False
                    self.menu_type = None
                elif self.menu_type == 'help':
                    # Any key closes help
                    self.menu_active = False
                    self.menu_type = None
                continue

            # Main keybinds
            if ch == curses.KEY_F1:
                self.menu_active = True
                self.menu_type = 'help'
                continue

            if ch == curses.KEY_F3:
                self.menu_active = True
                self.menu_type = 'apps'
                self.menu_selection = 0
                continue

            if ch == 9:  # Tab
                self.cycle_pane()
                continue

            if ch == 27:  # Escape
                continue

            # Pass to active ShellPane
            if self.active_pane_id and self.active_pane_id in self.panes:
                pane = self.panes[self.active_pane_id]
                if isinstance(pane, ShellPane):
                    if ch == 10 or ch == 13:
                        pane.submit()
                    elif ch == curses.KEY_BACKSPACE or ch == 127:
                        pane.backspace()
                    elif ch == curses.KEY_UP:
                        if pane.history and pane.history_idx > 0:
                            pane.history_idx -= 1
                            pane.input_buffer = pane.history[pane.history_idx]
                            pane._redraw_input()
                    elif ch == curses.KEY_DOWN:
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

    def calculate_layout(self):
        """Alias for _calculate_layout for external access."""
        self._calculate_layout()

    def cycle_pane(self):
        if not self.pane_order:
            return
        if self.active_pane_id is None:
            self.active_pane_id = self.pane_order[0]
        else:
            idx = self.pane_order.index(self.active_pane_id)
            idx = (idx + 1) % len(self.pane_order)
            self.active_pane_id = self.pane_order[idx]
        self._update_focus()


def main():
    app = TankuOS()
    curses.wrapper(app.run)


if __name__ == "__main__":
    main()
