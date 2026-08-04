#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPOSITORY_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PYTHON="$REPOSITORY_ROOT/macos/.venv/bin/python"
APP_PATH="${1:-$REPOSITORY_ROOT/macos/dist/AudioShifter.app}"

"$PYTHON" "$SCRIPT_DIR/verify_app.py" "$APP_PATH" \
  --json-output "$REPOSITORY_ROOT/macos/build/app_verification.json"
