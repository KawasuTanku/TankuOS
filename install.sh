#!/bin/sh
# TankuOS installer — downloads the latest prebuilt binary for your platform.
#
#   curl -fsSL https://raw.githubusercontent.com/KawasuTanku/TankuOS/main/install.sh | sh
#
# Override the install directory with TANKUOS_BIN_DIR (default: ~/.local/bin).
set -eu

REPO="KawasuTanku/TankuOS"
BIN_DIR="${TANKUOS_BIN_DIR:-$HOME/.local/bin}"

# Stock Debian often has wget but not curl; accept either.
fetch() {
  if command -v curl >/dev/null 2>&1; then curl -fsSL "$1"
  elif command -v wget >/dev/null 2>&1; then wget -qO- "$1"
  else echo "tankuos: need curl or wget to download" >&2; return 1
  fi
}

# Resolve the latest release tag WITHOUT the api.github.com REST endpoint.
# That endpoint is rate-limited to 60 requests/hour per IP and answers 403 once
# the budget is spent. The web redirect github.com/OWNER/REPO/releases/latest 302s
# to .../releases/tag/vX.Y.Z off a different, effectively-unlimited path; we read
# the tag straight out of its Location header. The REST API is only a fallback
# for when the redirect can't be parsed.
latest_tag() {
  redirect="https://github.com/$REPO/releases/latest"
  loc=""
  if command -v curl >/dev/null 2>&1; then
    loc="$(curl -fsSI "$redirect" | tr -d '\r' | awk 'tolower($1)=="location:"{print $2}' | tail -1)"
  elif command -v wget >/dev/null 2>&1; then
    loc="$(wget -qS --max-redirect=0 -O /dev/null "$redirect" 2>&1 | tr -d '\r' | awk 'tolower($1)=="location:"{print $2}' | tail -1)"
  fi
  case "$loc" in
    */releases/tag/*) printf '%s\n' "${loc##*/}"; return 0 ;;
  esac
  fetch "https://api.github.com/repos/$REPO/releases/latest" \
    | grep '"tag_name"' | head -1 | cut -d'"' -f4
}

os="$(uname -s)"
arch="$(uname -m)"
case "$os/$arch" in
  Darwin/arm64)        target="aarch64-apple-darwin" ;;
  Darwin/x86_64)       target="x86_64-apple-darwin" ;;
  Linux/x86_64)        target="x86_64-unknown-linux-gnu" ;;
  Linux/aarch64)       target="aarch64-unknown-linux-gnu" ;;
  *)
    echo "tankuos: no prebuilt binary for $os/$arch."
    echo "Install with Rust instead:  cargo install --git https://github.com/$REPO"
    exit 1 ;;
esac

echo "tankuos: finding latest release…"
tag="$(latest_tag || true)"
if [ -z "${tag:-}" ]; then
  echo "tankuos: couldn't resolve the latest release (GitHub unreachable or rate-limited)."
  echo "Install with Rust instead:  cargo install --git https://github.com/$REPO"
  exit 1
fi

url="https://github.com/$REPO/releases/download/$tag/tankuos-$target.tar.gz"
echo "tankuos: downloading $tag ($target)…"
mkdir -p "$BIN_DIR"
if ! fetch "$url" | tar -xz -C "$BIN_DIR" 2>/dev/null || [ ! -f "$BIN_DIR/tankuos" ]; then
  echo "tankuos: no prebuilt binary for $target in $tag."
  echo "Install with Rust instead:  cargo install --git https://github.com/$REPO"
  exit 1
fi
chmod +x "$BIN_DIR/tankuos"

echo "tankuos: installed $tag -> $BIN_DIR/tankuos"

# Optional, OS-aware dependency step. Installs helpers some features need:
#   blueutil (macOS)  — Bluetooth tray control
#   gpm (Linux)       — mouse on a bare console / VT
#   sshpass           — automates the one-time password for Systems → Add Remote
# Transparent and skippable: it prints what it runs, skips silently with no
# package manager, honours TANKUOS_SKIP_DEPS, and in a non-interactive
# `curl | sh` requires explicit TANKUOS_INSTALL_DEPS=1 so piping the installer
# never surprises you with package installs.
install_optional_deps() {
  [ "${TANKUOS_SKIP_DEPS:-0}" = "1" ] && return 0
  if [ ! -t 0 ] && [ "${TANKUOS_INSTALL_DEPS:-0}" != "1" ]; then return 0; fi
  case "$(uname -s)" in
    Darwin)
      if command -v brew >/dev/null 2>&1; then
        if ! command -v blueutil >/dev/null 2>&1; then
          echo "tankuos: installing optional dependency blueutil (Bluetooth control)…"
          brew install blueutil || echo "tankuos: blueutil install skipped (run 'brew install blueutil' later for Bluetooth control)"
        fi
        if ! command -v sshpass >/dev/null 2>&1; then
          echo "tankuos: installing optional dependency sshpass (remote-system setup)…"
          brew install sshpass 2>/dev/null \
            || brew install esolitos/ipa/sshpass 2>/dev/null \
            || echo "tankuos: sshpass install skipped (Add Remote will prompt for the password interactively instead)"
        fi
      fi ;;
    Linux)
      pkgs=""
      command -v gpm >/dev/null 2>&1 || pkgs="gpm"
      command -v sshpass >/dev/null 2>&1 || pkgs="$pkgs sshpass"
      pkgs="$(echo "$pkgs" | sed 's/^ *//')"
      if [ -n "$pkgs" ]; then
        echo "tankuos: installing optional dependencies: $pkgs …"
        sudo apt-get install -y $pkgs 2>/dev/null \
          || sudo dnf install -y $pkgs 2>/dev/null \
          || sudo pacman -S --noconfirm $pkgs 2>/dev/null \
          || sudo zypper install -y $pkgs 2>/dev/null \
          || echo "tankuos: optional deps skipped (install '$pkgs' with your package manager later)"
        if command -v gpm >/dev/null 2>&1 && command -v systemctl >/dev/null 2>&1; then
          sudo systemctl enable --now gpm 2>/dev/null || true
        fi
      fi ;;
  esac
}
install_optional_deps

case ":$PATH:" in
  *":$BIN_DIR:"*) echo "Run it with:  tankuos" ;;
  *) echo "Add $BIN_DIR to your PATH, then run:  tankuos"
     echo "  e.g.  echo 'export PATH=\"$BIN_DIR:\$PATH\"' >> ~/.zprofile" ;;
esac
