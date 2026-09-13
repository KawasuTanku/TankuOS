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
    echo "Usage: tankuos-app-install <app-name> [source-path]"
    echo ""
    echo "Examples:"
    echo "  tankuos-app-install warpstrand-driver ~/Projects/WarpStrand-Driver"
    echo "  tankuos-app-install retirement ~/Projects/Retirement"
    exit 1
fi

APP_DIR="$APPS_DIR/$APP_NAME"
CONFIGS_DIR="$APP_DIR/configs"
VENV_DIR="$APP_DIR/.venv"

echo "Installing $APP_NAME to $APP_DIR..."

# Create directory structure
mkdir -p "$APP_DIR" "$CONFIGS_DIR"

# Copy source if provided
if [ -n "$SOURCE_PATH" ] && [ -d "$SOURCE_PATH" ]; then
    echo "Copying source from $SOURCE_PATH..."
    # Copy everything except .venv and __pycache__
    rsync -a --exclude='.venv/' --exclude='__pycache__/' --exclude='*.pyc' \
        "$SOURCE_PATH/" "$APP_DIR/"
fi

# Create venv
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating venv..."
    python3 -m venv "$VENV_DIR"
fi

# Activate and install dependencies
source "$VENV_DIR/bin/activate"

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
    warpstrand-driver)
        if [ -f ~/.config/warpstrand/client.yaml ]; then
            echo "Migrating WarpStrand config..."
            cp ~/.config/warpstrand/client.yaml "$CONFIGS_DIR/"
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

# Create run.sh wrapper
cat > "$APP_DIR/run.sh" << 'RUNEOF'
#!/bin/sh
# Auto-generated run script for TankuOS app
set -eu
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$APP_DIR/.venv/bin/activate"
cd "$APP_DIR"
RUNEOF

# Add app-specific run command
case "$APP_NAME" in
    warpstrand-driver)
        cat >> "$APP_DIR/run.sh" << 'RUNEOF'
exec python "$APP_DIR/warpwrap.py" "$@"
RUNEOF
        ;;
    *)
        cat >> "$APP_DIR/run.sh" << 'RUNEOF'
exec python "$APP_DIR/main.py" "$@"
RUNEOF
        ;;
esac

chmod +x "$APP_DIR/run.sh"

echo ""
echo "Installed $APP_NAME to $APP_DIR"
echo "  Source:  $APP_DIR"
echo "  Configs: $CONFIGS_DIR"
echo "  Venv:    $VENV_DIR"
echo "  Run:     $APP_DIR/run.sh"
echo ""
echo "To check version: tankuos-app-version $APP_NAME"
