#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai
"""Single source of release identity for packaging and release tooling."""

from __future__ import annotations

import argparse


RELEASE_TAG = "v0.1.0-alpha.3"
RELEASE_TITLE = "AudioShifter v0.1.0-alpha.3 — macOS arm64 preview"
PYTHON_VERSION = "0.1.0a3"
BUNDLE_SHORT_VERSION = "0.1.0"
BUNDLE_VERSION = "3"
MACOS_ASSET_LABEL = "macOS27-arm64"


def app_asset_name(tag: str = RELEASE_TAG) -> str:
    return f"AudioShifter-{tag}-{MACOS_ASSET_LABEL}.zip"


def source_asset_name(tag: str = RELEASE_TAG) -> str:
    return f"AudioShifter-{tag}-corresponding-source.tar.gz"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "field",
        choices=(
            "tag",
            "title",
            "python-version",
            "bundle-short-version",
            "bundle-version",
            "app-asset",
            "source-asset",
        ),
    )
    args = parser.parse_args()
    values = {
        "tag": RELEASE_TAG,
        "title": RELEASE_TITLE,
        "python-version": PYTHON_VERSION,
        "bundle-short-version": BUNDLE_SHORT_VERSION,
        "bundle-version": BUNDLE_VERSION,
        "app-asset": app_asset_name(),
        "source-asset": source_asset_name(),
    }
    print(values[args.field])


if __name__ == "__main__":
    main()
