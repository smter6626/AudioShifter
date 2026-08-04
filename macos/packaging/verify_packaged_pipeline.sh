#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPOSITORY_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PYTHON="$REPOSITORY_ROOT/macos/.venv/bin/python"
APP_PATH="${1:-$REPOSITORY_ROOT/macos/dist/AudioShifter.app}"

"$PYTHON" "$SCRIPT_DIR/verify_packaged_pipeline.py" "$APP_PATH" \
  --json-output "$REPOSITORY_ROOT/macos/build/packaged_pipeline_verification.json"
