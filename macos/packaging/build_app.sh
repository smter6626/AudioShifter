#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPOSITORY_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILD_DIR="$REPOSITORY_ROOT/macos/build"
DIST_DIR="$REPOSITORY_ROOT/macos/dist"
PYTHON="$REPOSITORY_ROOT/macos/.venv/bin/python"
PYINSTALLER="$REPOSITORY_ROOT/macos/.venv/bin/pyinstaller"

if [[ "$(uname -m)" != "arm64" ]]; then
  echo "AudioShifter packaging requires a native arm64 build host." >&2
  exit 1
fi
if [[ ! -x "$PYTHON" || ! -x "$PYINSTALLER" ]]; then
  echo "Restore macos/.venv and install macos/requirements-dev.txt before packaging." >&2
  exit 1
fi

for path in "$BUILD_DIR" "$DIST_DIR"; do
  if [[ -d "$path" ]]; then
    find "$path" -depth -delete
  fi
done
mkdir -p "$BUILD_DIR" "$DIST_DIR"

"$SCRIPT_DIR/build_icon.sh"
"$PYTHON" "$SCRIPT_DIR/collect_macho_dependencies.py" \
  --output "$BUILD_DIR/external_dependencies.json" >/dev/null

export PYINSTALLER_CONFIG_DIR="$BUILD_DIR/pyinstaller-config"
export PYINSTALLER_STRICT_BUNDLE_CODESIGN_ERROR=1
export PYINSTALLER_VERIFY_BUNDLE_SIGNATURE=1
"$PYINSTALLER" \
  --noconfirm \
  --clean \
  --distpath "$DIST_DIR" \
  --workpath "$BUILD_DIR/pyinstaller" \
  "$SCRIPT_DIR/AudioShifter.spec"

COLLECTION_DIR="$DIST_DIR/AudioShifter"
if [[ -d "$COLLECTION_DIR" ]]; then
  find "$COLLECTION_DIR" -depth -delete
fi

echo "Built: $DIST_DIR/AudioShifter.app"
