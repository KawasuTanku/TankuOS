#!/bin/bash
# TankuOS installer — downloads the latest prebuilt binary for your platform.
#
#   curl -fsSL https://raw.githubusercontent.com/KawasuTanku/TankuOS/main/install.sh | bash
#
# Override the install directory with TANKUOS_BIN_DIR (default: ~/.local/bin).
set -euo pipefail

REPO="KawasuTanku/TankuOS"
BIN_DIR="${TANKUOS_BIN_DIR:-$HOME/.local/bin}"
SHARE_DIR="${TANKUOS_SHARE_DIR:-$HOME/.local/share/TankuOS}"

# Stock Debian often has wget but not curl; accept either.
fetch() {
  if command -v curl >/dev/null 2>&1; then curl -fsSL "$1"
  elif command -v wget >/dev/null 2>&1; then wget -qO- "$1"
  else echo "TankuOS: need curl or wget to download" >&2; return 1
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
    echo "TankuOS: no prebuilt binary for $os/$arch."
    echo "Install with Rust instead:  cargo install --git https://github.com/$REPO"
    exit 1 ;;
esac

echo "TankuOS: finding latest release…"
tag="$(latest_tag || true)"
if [ -z "${tag:-}" ]; then
  echo "TankuOS: couldn't resolve the latest release (GitHub unreachable or rate-limited)."
  echo "Install with Rust instead:  cargo install --git https://github.com/$REPO"
  exit 1
fi

url="https://github.com/$REPO/releases/download/$tag/TankuOS-$target.tar.gz"
echo "TankuOS: downloading $tag ($target)…"
mkdir -p "$BIN_DIR"
tmp_dir="$(mktemp -d)"
if ! fetch "$url" | tar -xz -C "$tmp_dir" 2>/dev/null || [ ! -f "$tmp_dir/TankuOS" ]; then
  echo "TankuOS: no prebuilt binary for $target in $tag."
  echo "Install with Rust instead:  cargo install --git https://github.com/$REPO"
  rm -rf "$tmp_dir"
  exit 1
fi
# Atomic install
mv -f "$tmp_dir/TankuOS" "$BIN_DIR/TankuOS"
chmod +x "$BIN_DIR/TankuOS"

echo "TankuOS: installed $tag -> $BIN_DIR/TankuOS"

# Extract bundled scripts to ~/.local/share/TankuOS/scripts/
mkdir -p "$SHARE_DIR/scripts"
cp -f "$tmp_dir/scripts/"* "$SHARE_DIR/scripts/" 2>/dev/null || true
chmod +x "$SHARE_DIR/scripts/"* 2>/dev/null || true

# Clean up temp dir after extracting scripts
rm -rf "$tmp_dir"

# Optional dependency step
install_optional_deps() {
  [ "${TANKUOS_SKIP_DEPS:-0}" = "1" ] && return 0
  if [ ! -t 0 ] && [ "${TANKUOS_INSTALL_DEPS:-0}" != "1" ]; then return 0; fi
  case "$(uname -s)" in
    Darwin)
      if command -v brew >/dev/null 2>&1; then
        command -v blueutil >/dev/null 2>&1 || {
          echo "TankuOS: installing optional dependency blueutil…"
          brew install blueutil || echo "TankuOS: blueutil install skipped"
        }
        command -v sshpass >/dev/null 2>&1 || {
          echo "TankuOS: installing optional dependency sshpass…"
          brew install sshpass 2>/dev/null \
            || brew install esolitos/ipa/sshpass 2>/dev/null \
            || echo "TankuOS: sshpass install skipped"
        }
      fi ;;
    Linux)
      pkgs=""
      command -v gpm >/dev/null 2>&1 || pkgs="gpm"
      command -v sshpass >/dev/null 2>&1 || pkgs="$pkgs sshpass"
      pkgs="$(echo "$pkgs" | sed 's/^ *//')"
      if [ -n "$pkgs" ]; then
        echo "TankuOS: installing optional dependencies: $pkgs …"
        sudo apt-get install -y $pkgs 2>/dev/null \
          || sudo dnf install -y $pkgs 2>/dev/null \
          || sudo pacman -S --noconfirm $pkgs 2>/dev/null \
          || sudo zypper install -y $pkgs 2>/dev/null \
          || echo "TankuOS: optional deps skipped"
      fi ;;
  esac
}
install_optional_deps

case ":$PATH:" in
  *":$BIN_DIR:"*) echo "Run it with:  TankuOS" ;;
  *) echo "Add $BIN_DIR to your PATH, then run:  TankuOS"
     echo "  e.g.  echo 'export PATH=\"$BIN_DIR:\$PATH\"' >> ~/.bashrc" ;;
esac
