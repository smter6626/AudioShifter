#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai
"""Audit the built macOS app for architecture, linking, paths, and signing."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import plistlib
import re
import subprocess
import sys
from pathlib import Path
from typing import Sequence


BUNDLE_IDENTIFIER = "io.github.smter6626.audioshifter"
SYSTEM_PREFIXES = (Path("/System/Library"), Path("/usr/lib"))
FORBIDDEN_LOAD_PATH_FRAGMENTS = ("/opt/homebrew", "/macos/.venv", "/Workspace/Tools/AudioShifter")
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT / "macos" / "release"))

from release_config import BUNDLE_SHORT_VERSION, BUNDLE_VERSION


GPL_V3_OFFICIAL_SHA256 = "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986"


def run(args: Sequence[str | Path], *, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        [str(value) for value in args],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        shell=False,
    )
    if check and completed.returncode != 0:
        stdout = completed.stdout.decode("utf-8", errors="replace")
        stderr = completed.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Command failed ({completed.returncode}): {args!r}\nstdout={stdout}\nstderr={stderr}"
        )
    return completed


def output(args: Sequence[str | Path]) -> str:
    return run(args).stdout.decode("utf-8", errors="replace")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_system_path(value: str) -> bool:
    candidate = Path(value)
    return any(candidate == prefix or prefix in candidate.parents for prefix in SYSTEM_PREFIXES)


def macho_files(app: Path) -> tuple[Path, ...]:
    items: list[Path] = []
    for path in app.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        description = output(("file", "-b", path))
        if "Mach-O" in description:
            items.append(path)
    return tuple(sorted(items))


def linked_references(path: Path) -> tuple[str, ...]:
    lines = output(("otool", "-L", path)).splitlines()[1:]
    references = [line.strip().split(" (compatibility version", 1)[0] for line in lines]
    identifier_result = run(("otool", "-D", path), check=False)
    identifier_lines = identifier_result.stdout.decode("utf-8", errors="replace").splitlines()
    identifier = identifier_lines[1].strip() if len(identifier_lines) > 1 else None
    return tuple(value for value in references if value and value != identifier)


def load_rpaths(path: Path) -> tuple[str, ...]:
    lines = output(("otool", "-l", path)).splitlines()
    values: list[str] = []
    for index, line in enumerate(lines):
        if line.strip() != "cmd LC_RPATH":
            continue
        for candidate in lines[index + 1 : index + 5]:
            stripped = candidate.strip()
            if stripped.startswith("path "):
                values.append(stripped[5:].split(" (offset", 1)[0])
                break
    return tuple(values)


def expand_loader_token(value: str, *, loader: Path, executable_dir: Path) -> Path | None:
    roots = {"@loader_path": loader.parent, "@executable_path": executable_dir}
    for token, root in roots.items():
        if value == token:
            return root
        if value.startswith(token + "/"):
            return root / value[len(token) + 1 :]
    if value.startswith("/"):
        return Path(value)
    return None


def resolve_internal_reference(
    reference: str,
    *,
    loader: Path,
    executable_dir: Path,
    rpaths: tuple[str, ...],
) -> tuple[Path, tuple[Path, ...]]:
    candidates: list[Path] = []
    direct = expand_loader_token(reference, loader=loader, executable_dir=executable_dir)
    if direct is not None:
        candidates.append(direct)
    elif reference.startswith("@rpath/"):
        suffix = reference[len("@rpath/") :]
        for rpath in rpaths:
            root = expand_loader_token(rpath, loader=loader, executable_dir=executable_dir)
            if root is not None:
                candidates.append(root / suffix)
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve(), tuple(candidates)
    raise FileNotFoundError(
        f"Unresolved load command {reference!r} in {loader}; candidates={candidates!r}"
    )


def ensure_inside(path: Path, root: Path, description: str) -> None:
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise RuntimeError(f"{description} escapes application bundle: {path}") from exc


def audit_app(app: Path) -> dict[str, object]:
    app = app.resolve()
    if not app.is_dir() or app.name != "AudioShifter.app":
        raise FileNotFoundError(f"AudioShifter.app was not found: {app}")

    contents = app / "Contents"
    info_path = contents / "Info.plist"
    executable = contents / "MacOS" / "AudioShifter"
    frameworks = contents / "Frameworks"
    resources = contents / "Resources"
    for required in (info_path, executable, frameworks, resources):
        if not required.exists():
            raise FileNotFoundError(f"Required bundle item is missing: {required}")

    with info_path.open("rb") as handle:
        info = plistlib.load(handle)
    expected_info = {
        "CFBundleIdentifier": BUNDLE_IDENTIFIER,
        "CFBundleExecutable": "AudioShifter",
        "CFBundleIconFile": "AudioShifter.icns",
        "CFBundlePackageType": "APPL",
        "CFBundleShortVersionString": BUNDLE_SHORT_VERSION,
        "CFBundleVersion": BUNDLE_VERSION,
    }
    for key, expected in expected_info.items():
        if info.get(key) != expected:
            raise RuntimeError(f"Info.plist {key}={info.get(key)!r}; expected {expected!r}")
    if re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", str(info["CFBundleShortVersionString"])) is None:
        raise RuntimeError("CFBundleShortVersionString must contain three numeric components")
    icon_path = resources / str(info["CFBundleIconFile"])
    if not icon_path.is_file():
        raise FileNotFoundError(f"Configured application icon is missing: {icon_path}")

    legal_paths = {
        "LICENSE": resources / "LICENSE",
        "LICENSING.md": resources / "LICENSING.md",
        "TRADEMARKS.md": resources / "TRADEMARKS.md",
        "THIRD_PARTY_NOTICES.md": resources / "THIRD_PARTY_NOTICES.md",
        "third_party_licenses": resources / "licenses",
    }
    for name, path in legal_paths.items():
        if not path.exists() or (name != "third_party_licenses" and not path.is_file()):
            raise FileNotFoundError(f"Packaged legal material is missing: {name}: {path}")
    if not legal_paths["third_party_licenses"].is_dir():
        raise RuntimeError("Packaged third-party licences path is not a directory")
    if sha256_file(legal_paths["LICENSE"]) != GPL_V3_OFFICIAL_SHA256:
        raise RuntimeError("Packaged LICENSE is not the verified official GNU GPLv3 text")
    licensing_text = legal_paths["LICENSING.md"].read_text(encoding="utf-8")
    trademarks_text = legal_paths["TRADEMARKS.md"].read_text(encoding="utf-8")
    for required in ("GPL-3.0-or-later", "windows/", "TRADEMARKS.md"):
        if required not in licensing_text:
            raise RuntimeError(f"Packaged LICENSING.md is missing required scope: {required}")
    for required in ("unofficial fork", "commercially distribute", "must not impersonate"):
        if required not in trademarks_text:
            raise RuntimeError(f"Packaged TRADEMARKS.md is missing required rule: {required}")

    tool_paths = {name: frameworks / "bin" / name for name in ("ffmpeg", "ffprobe", "rubberband")}
    for name, path in tool_paths.items():
        if not path.is_file() or not os.access(path, os.X_OK):
            raise RuntimeError(f"Packaged {name} is missing or not executable: {path}")

    symlinks = tuple(sorted(path for path in app.rglob("*") if path.is_symlink()))
    for link in symlinks:
        try:
            target = link.resolve(strict=True)
        except FileNotFoundError as exc:
            raise RuntimeError(f"Broken bundle symlink: {link} -> {os.readlink(link)}") from exc
        ensure_inside(target, app, "Symlink target")

    machos = macho_files(app)
    if not machos:
        raise RuntimeError("No Mach-O files found in application bundle")
    executable_dir = executable.parent
    total_references = 0
    total_rpaths = 0
    for binary in machos:
        architectures = output(("lipo", "-archs", binary)).strip().split()
        if architectures != ["arm64"]:
            raise RuntimeError(f"Non-arm64-only Mach-O: {binary}: {architectures}")
        rpaths = load_rpaths(binary)
        total_rpaths += len(rpaths)
        for rpath in rpaths:
            if any(fragment in rpath for fragment in FORBIDDEN_LOAD_PATH_FRAGMENTS):
                raise RuntimeError(f"Development LC_RPATH in {binary}: {rpath}")
            if rpath.startswith("/") and not is_system_path(rpath):
                raise RuntimeError(f"External absolute LC_RPATH in {binary}: {rpath}")
        for reference in linked_references(binary):
            total_references += 1
            if any(fragment in reference for fragment in FORBIDDEN_LOAD_PATH_FRAGMENTS):
                raise RuntimeError(f"Development load command in {binary}: {reference}")
            if is_system_path(reference):
                continue
            if reference.startswith("/"):
                raise RuntimeError(f"External non-system load command in {binary}: {reference}")
            resolved, _ = resolve_internal_reference(
                reference,
                loader=binary,
                executable_dir=executable_dir,
                rpaths=rpaths,
            )
            ensure_inside(resolved, app, "Dynamic dependency")

    codesign_verify = run(("codesign", "--verify", "--deep", "--strict", "--verbose=4", app))
    codesign_display = run(("codesign", "-dvvv", app))
    signing_text = (
        codesign_display.stdout + codesign_display.stderr
    ).decode("utf-8", errors="replace")
    if "Signature=adhoc" not in signing_text or "TeamIdentifier=not set" not in signing_text:
        raise RuntimeError(f"Expected an ad-hoc signature without a team identity:\n{signing_text}")
    spctl = run(("spctl", "--assess", "--type", "execute", "--verbose=4", app), check=False)

    size_bytes = sum(path.stat().st_size for path in app.rglob("*") if path.is_file() and not path.is_symlink())
    return {
        "app": str(app),
        "size_bytes": size_bytes,
        "bundle_identifier": info["CFBundleIdentifier"],
        "version": info["CFBundleShortVersionString"],
        "icon": str(icon_path),
        "legal_resources": {name: str(path) for name, path in legal_paths.items()},
        "gpl_v3_sha256": GPL_V3_OFFICIAL_SHA256,
        "packaged_tools": {name: str(path) for name, path in tool_paths.items()},
        "macho_count": len(machos),
        "architecture": "arm64-only",
        "dynamic_reference_count": total_references,
        "lc_rpath_count": total_rpaths,
        "external_non_system_load_commands": 0,
        "forbidden_development_load_commands": 0,
        "symlink_count": len(symlinks),
        "broken_or_external_symlinks": 0,
        "codesign_verify_returncode": codesign_verify.returncode,
        "signature": "adhoc",
        "team_identifier": None,
        "spctl_returncode": spctl.returncode,
        "spctl_output": (spctl.stdout + spctl.stderr).decode("utf-8", errors="replace").strip(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "app",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "dist" / "AudioShifter.app",
    )
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    result = audit_app(args.app)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
