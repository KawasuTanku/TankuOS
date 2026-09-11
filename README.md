# TankuOS

A TUI desktop skeleton for unified terminal application suites. Build cohesive, themed terminal desktops where multiple applications feel like one system.

## Vision

TankuOS provides the chrome — window management, theming, layout persistence, and a launcher — so your applications can focus on what they do best. Built on [Textual](https://github.com/Textualize/textual).

## Roadmap

### Chunk 1: Theme Module ✅ (current)
- [x] Color palette system
- [x] Common widgets (Header, Footer, Sidebar, Pane)
- [x] Typography conventions
- [x] Theme switching (midnight, nord, gruvbox, dracula)

### Chunk 2: Core Shell ✅ (current)
- [x] Grid layout with panes
- [x] Launcher sidebar
- [x] Status bar
- [x] Pane management (open, close, focus, resize)
- [x] Child process hosting (PTY)

### Chunk 3: Layout Persistence
- [ ] Save/restore pane positions to TOML
- [ ] Remember which apps were open
- [ ] Multiple named layouts

### Chunk 4: Password Lock
- [ ] Per-app lock toggle
- [ ] Password hash in config
- [ ] Blur/lock screen on locked panes

### Chunk 5: App Protocol
- [ ] Base class / decorator for apps to register
- [ ] Standardized lifecycle (mount, unmount, status updates)
- [ ] Inter-app communication

### Chunk 6: First-Party Integration
- [ ] Retrofit MailVault to use TankuOS theme
- [ ] Retrofit MontcoMonitor to use TankuOS theme
- [ ] Retrofit Retirement to use TankuOS theme
- [ ] Proof that the skeleton works for other apps

### Chunk 7: Advanced Features
- [ ] Remote session support (SSH)
- [ ] Notifications system
- [ ] File manager
- [ ] App store / catalog

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
tankuos
```

## Configuration

Configuration lives at `~/.config/tankuos/config.toml`.

## License

MIT
