#!/usr/bin/env bash
set -euo pipefail

PLIST_SRC="$(dirname "$0")/com.example.staywithme.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.example.staywithme.plist"

if [ ! -f "$PLIST_SRC" ]; then
  echo "Plist file not found: $PLIST_SRC" >&2
  exit 1
fi

mkdir -p "$(dirname "$PLIST_DST")"
cp "$PLIST_SRC" "$PLIST_DST"
chmod 644 "$PLIST_DST"

echo "Loaded plist to $PLIST_DST"
echo "To load it now run:"
echo "  launchctl load -w $PLIST_DST"
