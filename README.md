# TankuOS

**TankuOS** is a desktop environment for the terminal — a windowing shell that runs *inside* your terminal emulator. Floating, overlapping windows, each hosting a real TUI application in its own pseudo-terminal, with a mouse cursor, menubar, dock, app launcher, and configurable grid tiling.

This project is a fork of [tuiui](https://github.com/jaylfc/tuiui) by [jaylfc](https://github.com/jaylfc), modified to serve as the foundation for a unified terminal application suite. All credit goes to the original tuiui author for the architecture, compositor, PTY hosting, and window management that TankuOS builds on top of.

## What changed from tuiui

- Renamed from `tuiui` to `TankuOS`
- Menubar label changed to "Applications" (was "tuiui")
- Power menu / host menu label changed to "TankuOS ▾" (was machine hostname)
- Default app catalog replaced with TankuOS-integrated apps
- Your apps (Retirement, Monster, MailVault, Montco Monitor) become first-class pane plugins

## What works today

- **Floating, overlapping windows** with drop shadows, each running a real TUI (btop, a shell, vim, …) in its own pseudo-terminal
- **Faithful rendering** via a full terminal emulator (`alacritty_terminal`) — even demanding apps like btop render correctly
- **Mouse-driven**: drag titlebars to move, drag edges to resize, click the dock to focus, scroll wheel to page through scrollback
- **Configurable grid tiling** — set a rows×columns grid and use drag-to-cell snapping
- **Persistent daemon** — apps survive UI reloads, detach and reattach from any terminal or over SSH
- **Apps menu** (top-left) — browse and launch applications
- **Power menu** (top-right "TankuOS ▾") — Exit, Restart, Shutdown with confirmation dialogs

## Build & run

Requires a Rust toolchain (1.75+, but 1.95+ recommended — see note below).

```bash
cargo build --release
cargo run
```

Or install directly:

```bash
curl -fsSL https://raw.githubusercontent.com/KawasuTanku/TankuOS/main/install.sh | sh
```

### Rust version note

The upstream `Cargo.lock` uses lockfile v4 and some dependencies require Cargo features only available in newer Rust (edition2024). On Rust 1.75 (shipped with Ubuntu 24.04), you may need to `rm Cargo.lock` and let Cargo regenerate it, which may pull in newer dependency versions. For a guaranteed build, use Rust 1.95+ via [rustup](https://rustup.rs):

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup default stable
```

## Configuration

```toml
# ~/.config/tankuos/config.toml

# Tiling grid (also editable in Settings → Windows)
grid_rows = 2
grid_cols = 3
tile_gap = 0
auto_tile = false
```

## Architecture

TankuOS runs three processes so apps survive UI reloads:

```
client (tankuos)  ←socket→  daemon (tankuos --daemon)  ←socket→  apphost (tankuos --apphost)
thin renderer              owns SessionCore (all UI state)    owns the PTY apps
real terminal              composites frames, routes input    survives UI reloads
```

Each app gets its own PTY and terminal emulator instance — apps don't know they're running inside TankuOS.

## Adding your apps

Your Python/CLI apps become TankuOS plugins by adding them to the app catalog (`assets/catalog.json`):

```json
{
  "name": "Retirement",
  "bin": "retirement-tui",
  "category": "Finance",
  "description": "Portfolio tracker for Robinhood IRAs",
  "homepage": "https://github.com/KawasuTanku/Retirement"
}
```

Then add an install recipe in `assets/recipes.json`. Your app gets window management, persistence, and a menu entry for free.

## License

MIT — same as the original tuiui. See `THIRD-PARTY-LICENSES.md` for bundled dependency credits.

## Credits

- [tuiui](https://github.com/jaylfc/tuiui) — original project by jaylfc (MIT)
- [alacritty_terminal](https://docs.rs/alacritty_terminal) — terminal emulation
- [crossterm](https://docs.rs/crossterm) — terminal I/O
- [portable-pty](https://docs.rs/portable-pty) — pseudo-terminal support
- [rothgar/awesome-tuis](https://github.com/rothgar/awesome-tuis) — app catalog source
