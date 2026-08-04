#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPOSITORY_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SOURCE_ICON="$REPOSITORY_ROOT/macos/assets/source/audioshifter_icon.png"
OUTPUT_ICON="$REPOSITORY_ROOT/macos/assets/AudioShifter.icns"

if [[ ! -r "$SOURCE_ICON" ]]; then
  echo "Icon source is missing or unreadable: $SOURCE_ICON" >&2
  exit 1
fi

WIDTH="$(sips -g pixelWidth "$SOURCE_ICON" | awk '/pixelWidth:/ {print $2}')"
HEIGHT="$(sips -g pixelHeight "$SOURCE_ICON" | awk '/pixelHeight:/ {print $2}')"
if [[ -z "$WIDTH" || "$WIDTH" != "$HEIGHT" || "$WIDTH" -lt 1024 ]]; then
  echo "Icon source must be a square PNG at least 1024x1024; got ${WIDTH:-unknown}x${HEIGHT:-unknown}." >&2
  exit 1
fi

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/AudioShifter-icon.XXXXXX")"
ICONSET_DIR="$WORK_DIR/AudioShifter.iconset"
mkdir -p "$ICONSET_DIR" "$(dirname "$OUTPUT_ICON")"

cleanup() {
  if [[ "$WORK_DIR" == "${TMPDIR:-/tmp}"/AudioShifter-icon.* && -d "$WORK_DIR" ]]; then
    find "$WORK_DIR" -depth -delete
  fi
}
trap cleanup EXIT

while read -r filename pixels; do
  sips -z "$pixels" "$pixels" "$SOURCE_ICON" --out "$ICONSET_DIR/$filename" >/dev/null
done <<'SIZES'
icon_16x16.png 16
icon_16x16@2x.png 32
icon_32x32.png 32
icon_32x32@2x.png 64
icon_128x128.png 128
icon_128x128@2x.png 256
icon_256x256.png 256
icon_256x256@2x.png 512
icon_512x512.png 512
icon_512x512@2x.png 1024
SIZES

iconutil -c icns "$ICONSET_DIR" -o "$OUTPUT_ICON"
file "$OUTPUT_ICON"
