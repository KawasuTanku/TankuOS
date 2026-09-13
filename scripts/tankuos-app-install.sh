#!/bin/sh
# TankuOS App Installer
# Installs an app from the catalog into ~/TankuOS/Apps/<name>/
# with its own venv, configs, and dependencies.
#
# Usage: tankuos-app-install <app-name> [source-path]

set -eu

APPS_DIR="$HOME/TankuOS/Apps"
APP_NAME="${1:-}"
SOURCE_PATH="${2:-}"

if [ -z "$APP_NAME" ]; then
    echo "Usage: tankuos-app-install <app-name> <source>"
    echo ""
    echo "Examples:"
    echo "  # Install from local path"
    echo "  tankuos-app-install WarpStrand-Driver ~/Projects/WarpStrand-Driver"
    echo ""
    echo "  # Install from GitHub"
    echo "  tankuos-app-install WarpStrand-Driver https://github.com/KawasuTanku/WarpStrand-Driver.git"
    echo ""
    echo "  # Install multiple apps from catalog"
    echo "  tankuos-app-install-all"
    exit 1
fi

APP_DIR="$APPS_DIR/$APP_NAME"
CONFIGS_DIR="$APP_DIR/configs"
VENV_DIR="$APP_DIR/.venv"

echo "Installing $APP_NAME to $APP_DIR..."

# Preserve existing configs across reinstall/update.
CONFIGS_TMP=""
if [ -d "$CONFIGS_DIR" ] && [ "$(ls -A "$CONFIGS_DIR" 2>/dev/null)" ]; then
    CONFIGS_TMP=$(mktemp -d)
    cp -r "$CONFIGS_DIR/"* "$CONFIGS_TMP/" 2>/dev/null || true
fi

# Create directory structure
mkdir -p "$APP_DIR" "$CONFIGS_DIR"

# Copy or clone source
if [ -n "$SOURCE_PATH" ] && [ -d "$SOURCE_PATH" ]; then
    echo "Copying source from $SOURCE_PATH..."
    rsync -a --exclude='.venv/' --exclude='__pycache__/' --exclude='*.pyc' \
        "$SOURCE_PATH/" "$APP_DIR/"
elif [ -n "$SOURCE_PATH" ]; then
    echo "Cloning from: $SOURCE_PATH..."
    tmp_dir=$(mktemp -d)
    git clone --depth 1 "$SOURCE_PATH" "$tmp_dir"
    rm -rf "$tmp_dir/.git"
    # Move contents into app dir
    mv "$tmp_dir"/* "$tmp_dir"/.[!.]* "$APP_DIR/" 2>/dev/null || true
    rm -rf "$tmp_dir"
fi

# Migrate .env credentials into the TankuOS configs dir
# (.env is gitignored, so it won't be in cloned repos — check CWD for legacy)
if [ -f ".env" ] && [ -s ".env" ]; then
    echo "Migrating .env to configs..."
    cp .env "$CONFIGS_DIR/.env"
elif [ ! -f "$CONFIGS_DIR/.env" ]; then
    # Create a template for the user to fill in
    cat > "$CONFIGS_DIR/.env" << 'TEMPLATE'
# Robinhood credentials for Retirement
# Fill these in to enable --fetch
ROBINHOOD_USERNAME=
ROBINHOOD_PASSWORD=
# Optional: 2FA TOTP secret (not the 6-digit code)
ROBINHOOD_TOTP=
TEMPLATE
fi

# Restore preserved configs
if [ -n "$CONFIGS_TMP" ] && [ -d "$CONFIGS_TMP" ]; then
    cp -r "$CONFIGS_TMP/"* "$CONFIGS_DIR/" 2>/dev/null || true
    rm -rf "$CONFIGS_TMP"
fi

# Create venv
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating venv..."
    python3 -m venv "$VENV_DIR"
fi

# Activate and install dependencies
. "$VENV_DIR/bin/activate"

if [ -f "$APP_DIR/requirements.txt" ]; then
    echo "Installing requirements..."
    pip install -r "$APP_DIR/requirements.txt"
fi

if [ -f "$APP_DIR/pyproject.toml" ]; then
    echo "Installing package..."
    pip install -e "$APP_DIR/"
fi

# Migrate configs (app-specific)
case "$APP_NAME" in
    WarpStrand-Driver)
        mkdir -p "$CONFIGS_DIR/warpstrand"
        if [ -f ~/.config/warpstrand/client.yaml ]; then
            echo "Migrating WarpStrand config..."
            cp ~/.config/warpstrand/client.yaml "$CONFIGS_DIR/warpstrand/"
        fi
        ;;
esac

# Create meta file
INSTALL_DATE=$(date +%Y-%m-%d)
VERSION=$(python3 -c "
import json
with open('$APP_DIR/pyproject.toml') as f:
    for line in f:
        if line.startswith('version'):
            print(line.split('\"')[1])
            break
" 2>/dev/null || echo "0.1.0")

cat > "$APP_DIR/.tankuos-meta.json" << EOF
{
  "name": "$APP_NAME",
  "version": "$VERSION",
  "install_date": "$INSTALL_DATE",
  "source": "${SOURCE_PATH:-catalog}"
}
EOF

# Create bin wrapper for catalog detection and PATH access
# Name matches the repo/project name exactly (e.g. Retirement, WarpStrand-Driver)
BIN_DIR="${HOME}/.local/bin"
mkdir -p "$BIN_DIR"
BIN_NAME="$APP_NAME"
BIN_PATH="$BIN_DIR/$BIN_NAME"

# Determine how to launch: prefer the pip-installed entry point if the app
# defines one in [project.scripts], otherwise fall back to a module/wrapper.
ENTRY_POINT=""
if [ -f "$APP_DIR/pyproject.toml" ]; then
    ENTRY_POINT=$(python3 -c "
import re
with open('$APP_DIR/pyproject.toml') as f:
    text = f.read()
m = re.search(r'\[project\.scripts\]\s*\n\s*(\w+)\s*=\s*\"([^\"]+)\"', text)
if m: print(m.group(1))
" 2>/dev/null || true)
fi

if [ -n "$ENTRY_POINT" ]; then
    # App defines a console_scripts entry point — exec the venv binary
    cat > "$BIN_PATH" << WRAPPER
#!/bin/sh
set -eu
export XDG_CONFIG_HOME="$APP_DIR/configs"
. "$APP_DIR/.venv/bin/activate"
cd "$APP_DIR"
exec $ENTRY_POINT "\$@"
WRAPPER
else
    # Fallback: exec a module/wrapper (e.g. WarpStrand-Driver's warpwrap.py)
    cat > "$BIN_PATH" << 'WRAPPER'
#!/bin/sh
set -eu
APP_DIR="__APP_DIR__"
export XDG_CONFIG_HOME="$APP_DIR/configs"
. "$APP_DIR/.venv/bin/activate"
cd "$APP_DIR"
exec python "$APP_DIR/warpwrap.py" "$@"
WRAPPER
    sed -i "s|__APP_DIR__|$APP_DIR|g" "$BIN_PATH"
fi
chmod +x "$BIN_PATH"

echo ""
echo "Installed $APP_NAME to $APP_DIR"
echo "  Source:  $APP_DIR"
echo "  Configs: $CONFIGS_DIR"
echo "  Venv:    $VENV_DIR"
echo "  Run:     $APP_DIR/run.sh"
echo ""
echo "To check version: tankuos-app-version $APP_NAME"
