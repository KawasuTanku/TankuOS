# Driving the desktop

These commands talk to the running tankuos daemon (same user, local socket).
They are how you open windows and arrange the user's desktop.

- `tankuos launch <command> [args…]`   open a new app window running <command>
  - Launching a catalog-tagged **CLI tool** (gum, himalaya, khal, dust, …)
    with **no args** automatically opens a shell with the tool's `--help`
    printed first, instead of a window that prints usage and dies. Passing
    args runs the command exactly as given.
- `tankuos tile`                       tile all windows into the configured grid
- `tankuos theme <name>`               switch theme (midnight|nord|gruvbox|dracula)
- `tankuos reload`                     reload the UI (apps keep running)
- `tankuos msg '<json>'`               raw control message (ClientMsg JSON), e.g.

```sh
tankuos msg '"MaximizeFocused"'
tankuos msg '{"SnapFocused":"Left"}'
tankuos msg '{"SendToCell":3}'
tankuos msg '{"Launch":{"name":"btop","command":"btop","args":[]}}'
```

Examples of arranging a workspace:

```sh
tankuos launch btop          # system monitor
tankuos launch lazygit       # git UI
tankuos tile                 # arrange everything into the grid
```

Apps are installed via the in-app Store (600+ curated TUIs), or you can
install them yourself with the user's package manager and then `tankuos launch`.

Other things worth knowing when helping the user:
- Scroll the mouse wheel over any app window to read its scrollback; typing
  jumps back to the live bottom.
- Updating tankuos is **Settings → Updates** (default channel downloads the
  latest prebuilt release; a "dev" channel builds the dev branch from source).
- The version is in `Cargo.toml`; release notes are in `CHANGELOG.md`.
