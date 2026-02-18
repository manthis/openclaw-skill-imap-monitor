#!/bin/bash
# Wrapper for imap-monitor.py — sources config.env automatically

SCRIPT_DIR="$HOME/.openclaw/workspace/skills/imap-monitor"
CONFIG_FILE="$SCRIPT_DIR/config.env"
PYTHON_SCRIPT="$SCRIPT_DIR/scripts/imap-monitor.py"

# Source config if exists
# shellcheck source=/dev/null
if [[ -f "$CONFIG_FILE" ]]; then
    set -a  # auto-export all variables
    source "$CONFIG_FILE"
    set +a
fi

# Call the Python script with all args
exec python3 "$PYTHON_SCRIPT" "$@"
