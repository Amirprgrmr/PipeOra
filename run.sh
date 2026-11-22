#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="$SCRIPT_DIR/.venv"

# Create virtual environment with system site packages if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment with system-site-packages..."
    if command -v uv >/dev/null 2>&1; then
        uv venv --system-site-packages "$VENV_DIR"
        uv pip install -r requirements.txt --python "$VENV_DIR/bin/python"
    else
        python3 -m venv --system-site-packages "$VENV_DIR"
        "$VENV_DIR/bin/pip" install -r requirements.txt
    fi
fi

# Run AM Audio Control
exec "$VENV_DIR/bin/python" -m app.main "$@"
