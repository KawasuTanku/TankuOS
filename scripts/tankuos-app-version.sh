#!/bin/sh
# TankuOS App Version Checker
# Compares installed app version vs catalog version
#
# Usage: tankuos-app-version <app-name>
# Returns: "up-to-date", "update-available", or "not-installed"

set -eu

APPS_DIR="$HOME/TankuOS/Apps"
APP_NAME="${1:-}"
CATALOG="${2:-/usr/share/tankuos/catalog.json}"

if [ -z "$APP_NAME" ]; then
    echo "Usage: tankuos-app-version <app-name> [catalog-path]"
    exit 1
fi

APP_DIR="$APPS_DIR/$APP_NAME"
META_FILE="$APP_DIR/.tankuos-meta.json"

# Check if installed
if [ ! -f "$META_FILE" ]; then
    echo "not-installed"
    exit 0
fi

# Read installed version
INSTALLED_VERSION=$(python3 -c "
import json,sys
with open('$META_FILE') as f:
    print(json.load(f).get('version','unknown'))
" 2>/dev/null || echo "unknown")

# Read catalog version
CATALOG_VERSION=$(python3 -c "
import json,sys
with open('$CATALOG') as f:
    catalog = json.load(f)
for app in catalog:
    if app.get('name') == '$APP_NAME' or app.get('bin','').endswith('$APP_NAME'):
        print(app.get('version','unknown'))
        break
" 2>/dev/null || echo "unknown")

if [ "$INSTALLED_VERSION" = "unknown" ] || [ "$CATALOG_VERSION" = "unknown" ]; then
    echo "unknown"
    exit 0
fi

if [ "$INSTALLED_VERSION" = "$CATALOG_VERSION" ]; then
    echo "up-to-date"
else
    echo "update-available"
    echo "installed: $INSTALLED_VERSION"
    echo "available: $CATALOG_VERSION"
fi
