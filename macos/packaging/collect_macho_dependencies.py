#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai
"""Recursively inventory non-system Mach-O dependencies for external CLIs."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


SYSTEM_PREFIXES = (Path("/System/Library"), Path("/usr/lib"))
TOOL_NAMES = ("ffmpeg", "ffprobe", "rubberband")


@dataclass(frozen=True, slots=True)
class CollectedBinary:
    source: Path
    destination: str
    required_by: Path | None

    def as_pyinstaller_tuple(self) -> tuple[str, str]:
        return str(self.source), str(Path(self.destination).parent)


def _run(args: Sequence[str | Path]) -> str:
    completed = subprocess.run(
        [str(value) for value in args],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        shell=False,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"Command failed ({completed.returncode}): {args!r}\n{stderr}")
    return completed.stdout.decode("utf-8", errors="replace")


def linked_references(path: Path) -> tuple[str, ...]:
    lines = _run(("otool", "-L", path)).splitlines()[1:]
    references: list[str] = []
    for line in lines:
        value = line.strip().split(" (compatibility version", 1)[0]
        if value:
            references.append(value)
    return tuple(references)


def load_rpaths(path: Path) -> tuple[str, ...]:
    lines = _run(("otool", "-l", path)).splitlines()
    values: list[str] = []
    for index, line in enumerate(lines):
        if line.strip() == "cmd LC_RPATH":
            for candidate in lines[index + 1 : index + 5]:
                stripped = candidate.strip()
                if stripped.startswith("path "):
                    values.append(stripped[5:].split(" (offset", 1)[0])
                    break
    return tuple(values)


def is_system_reference(reference: str) -> bool:
    candidate = Path(reference)
    return any(candidate == prefix or prefix in candidate.parents for prefix in SYSTEM_PREFIXES)


def _expand_token(value: str, *, loader_dir: Path, executable_dir: Path) -> Path | None:
    replacements = {
        "@loader_path": loader_dir,
        "@executable_path": executable_dir,
    }
    for token, root in replacements.items():
        if value == token:
            return root
        if value.startswith(token + "/"):
            return root / value[len(token) + 1 :]
    if value.startswith("/"):
        return Path(value)
    return None


def resolve_reference(reference: str, *, loader: Path, executable: Path) -> Path:
    loader_dir = loader.parent
    executable_dir = executable.parent
    direct = _expand_token(reference, loader_dir=loader_dir, executable_dir=executable_dir)
    candidates: list[Path] = [direct] if direct is not None else []
    if reference.startswith("@rpath/"):
        suffix = reference[len("@rpath/") :]
        for rpath in load_rpaths(loader):
            expanded = _expand_token(rpath, loader_dir=loader_dir, executable_dir=executable_dir)
            if expanded is not None:
                candidates.append(expanded / suffix)
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"Unable to resolve {reference!r} required by {loader}; candidates={candidates!r}"
    )


def resolve_tools(overrides: dict[str, Path] | None = None) -> dict[str, Path]:
    configured = overrides or {}
    result: dict[str, Path] = {}
    for name in TOOL_NAMES:
        value = configured.get(name) or shutil.which(name)
        if value is None:
            raise FileNotFoundError(f"Required build tool is missing from PATH: {name}")
        path = Path(value)
        if not path.is_file() or not os.access(path, os.X_OK):
            raise PermissionError(f"Required build tool is not executable: {path}")
        result[name] = path
    return result


def collect_external_binaries(
    tool_paths: dict[str, Path] | None = None,
) -> tuple[CollectedBinary, ...]:
    tools = resolve_tools(tool_paths)
    queue: deque[tuple[Path, Path | None, str, Path]] = deque()
    for name, source in tools.items():
        queue.append((source, None, f"bin/{name}", source))

    collected: list[CollectedBinary] = []
    seen_sources: set[Path] = set()
    destinations: dict[str, Path] = {}
    while queue:
        source, required_by, destination, executable = queue.popleft()
        canonical = source.resolve()
        if canonical in seen_sources:
            continue
        existing = destinations.get(destination)
        if existing is not None and existing != canonical:
            raise RuntimeError(
                f"Bundle destination collision for {destination}: {existing} and {canonical}"
            )
        seen_sources.add(canonical)
        destinations[destination] = canonical
        collected.append(CollectedBinary(source, destination, required_by))
        for reference in linked_references(source):
            if is_system_reference(reference):
                continue
            dependency = resolve_reference(reference, loader=source, executable=executable)
            dependency_destination = f"lib/{Path(reference).name}"
            queue.append((dependency, source, dependency_destination, executable))
    return tuple(collected)


def pyinstaller_tool_binaries() -> list[tuple[str, str]]:
    """Return CLI roots; PyInstaller relocates their inventoried dependency graph."""

    tools = resolve_tools()
    return [(str(source), "bin") for source in tools.values()]


def manifest(items: Iterable[CollectedBinary]) -> dict[str, object]:
    entries = [
        {
            "source": str(item.source),
            "resolved_source": str(item.source.resolve()),
            "destination": item.destination,
            "required_by": str(item.required_by) if item.required_by else None,
        }
        for item in items
    ]
    return {"count": len(entries), "entries": entries}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = manifest(collect_external_binaries())
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
