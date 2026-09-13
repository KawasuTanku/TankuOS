#!/bin/sh
# TankuOS App Uninstaller
# Removes an app from ~/TankuOS/Apps/<name>/
#
# Usage: tankuos-app-uninstall <app-name>

set -eu

APPS_DIR="$HOME/TankuOS/Apps"
APP_NAME="${1:-}"

if [ -z "$APP_NAME" ]; then
    echo "Usage: tankuos-app-uninstall <app-name>"
    exit 1
fi

APP_DIR="$APPS_DIR/$APP_NAME"

if [ ! -d "$APP_DIR" ]; then
    echo "App not installed: $APP_NAME"
    exit 1
fi

echo "Uninstalling $APP_NAME..."
echo "  Removing $APP_DIR"
rm -rf "$APP_DIR"

echo "Uninstalled $APP_NAME"
