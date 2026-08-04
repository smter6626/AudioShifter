#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPOSITORY_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PYTHON="$REPOSITORY_ROOT/macos/.venv/bin/python"
TAG="v0.1.0-alpha.1"
WORK_ROOT="$REPOSITORY_ROOT/macos/release-work"
STAGING_DIR="$WORK_ROOT/staging"
SOURCE_WORK="$WORK_ROOT/corresponding-source"
VERIFY_WORK="$WORK_ROOT/verification"
TAG_TREE="$WORK_ROOT/tag-worktree"
FINAL_DIR="$REPOSITORY_ROOT/macos/release-dist"
APP="$REPOSITORY_ROOT/macos/dist/AudioShifter.app"
APP_ASSET="AudioShifter-$TAG-macOS27-arm64.zip"
SOURCE_ASSET="AudioShifter-$TAG-corresponding-source.tar.gz"

reset_exact_directory() {
  local target="$1"
  case "$target" in
    "$WORK_ROOT"/*|"$FINAL_DIR") ;;
    *) echo "Refusing to reset unexpected path: $target" >&2; exit 1 ;;
  esac
  if [[ -d "$target" ]]; then
    find "$target" -depth -delete
  fi
  mkdir -p "$target"
}

cleanup_tag_tree() {
  if [[ -L "$TAG_TREE/macos/.venv" ]]; then
    unlink "$TAG_TREE/macos/.venv"
  fi
  for generated in "$TAG_TREE/macos/build" "$TAG_TREE/macos/dist"; do
    if [[ -d "$generated" ]]; then
      find "$generated" -depth -delete
    fi
  done
  if git worktree list --porcelain | grep -Fqx "worktree $TAG_TREE"; then
    git worktree remove "$TAG_TREE"
  elif [[ -d "$TAG_TREE" ]]; then
    find "$TAG_TREE" -depth -delete
  fi
}

cd "$REPOSITORY_ROOT"

if [[ ! -x "$PYTHON" ]]; then
  echo "Restore macos/.venv before building release assets." >&2
  exit 1
fi
if ! git merge-base --is-ancestor "$TAG^{commit}" HEAD; then
  echo "$TAG must be an ancestor of the release-tooling commit." >&2
  exit 1
fi
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Release assets must be built from a clean tagged worktree." >&2
  exit 1
fi

"$PYTHON" -m pytest
mkdir -p "$WORK_ROOT"
cleanup_tag_tree
git worktree add --detach "$TAG_TREE" "$TAG"
trap cleanup_tag_tree EXIT
ln -s "$REPOSITORY_ROOT/macos/.venv" "$TAG_TREE/macos/.venv"
"$TAG_TREE/macos/packaging/build_app.sh"

if [[ -d "$REPOSITORY_ROOT/macos/dist" ]]; then
  find "$REPOSITORY_ROOT/macos/dist" -depth -delete
fi
mkdir -p "$REPOSITORY_ROOT/macos/dist"
ditto "$TAG_TREE/macos/dist/AudioShifter.app" "$APP"
cleanup_tag_tree
"$PYTHON" "$REPOSITORY_ROOT/macos/packaging/verify_app.py" "$APP" \
  --json-output "$REPOSITORY_ROOT/macos/build/app_verification.json"
"$PYTHON" "$REPOSITORY_ROOT/macos/packaging/verify_packaged_pipeline.py" "$APP" \
  --json-output "$REPOSITORY_ROOT/macos/build/packaged_pipeline_verification.json"

reset_exact_directory "$STAGING_DIR"
reset_exact_directory "$SOURCE_WORK"
if [[ -d "$VERIFY_WORK" ]]; then
  find "$VERIFY_WORK" -depth -delete
fi

ditto -c -k --sequesterRsrc --keepParent "$APP" "$STAGING_DIR/$APP_ASSET"
"$PYTHON" "$SCRIPT_DIR/collect_corresponding_source.py" \
  --tag "$TAG" \
  --app "$APP" \
  --work-dir "$SOURCE_WORK" \
  --output "$STAGING_DIR/$SOURCE_ASSET"

(
  cd "$STAGING_DIR"
  shasum -a 256 "$APP_ASSET" "$SOURCE_ASSET" > SHA256SUMS.txt
  shasum -a 256 -c SHA256SUMS.txt
)

"$PYTHON" "$SCRIPT_DIR/verify_release_assets.py" \
  --assets-dir "$STAGING_DIR" \
  --tag "$TAG" \
  --work-dir "$VERIFY_WORK" \
  --json-output "$WORK_ROOT/release-assets-verification.json"

reset_exact_directory "$FINAL_DIR"
find "$STAGING_DIR" -mindepth 1 -maxdepth 1 -exec mv {} "$FINAL_DIR/" \;
rmdir "$STAGING_DIR"

echo "Verified release assets: $FINAL_DIR"
ls -l "$FINAL_DIR"
