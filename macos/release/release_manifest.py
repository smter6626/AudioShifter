#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai
"""Shared release component inventory and bundle-to-source mapping."""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence


@dataclass(frozen=True)
class Component:
    key: str
    name: str
    formulae: tuple[str, ...]
    licence: str
    upstream: str
    patterns: tuple[str, ...]


COMPONENTS: tuple[Component, ...] = (
    Component(
        "cpython",
        "CPython",
        ("python@3.11",),
        "PSF License / Python-2.0",
        "https://www.python.org/",
        (
            "Contents/Frameworks/Python.framework/Versions/3.11/Python",
            "Contents/Frameworks/python3__dot__11/lib-dynload/*.so",
        ),
    ),
    Component(
        "mpdecimal",
        "mpdecimal",
        ("mpdecimal",),
        "BSD-2-Clause",
        "https://www.bytereef.org/mpdecimal/",
        ("Contents/Frameworks/libmpdec.*.dylib",),
    ),
    Component(
        "xz",
        "XZ Utils / liblzma",
        ("xz",),
        "0BSD for packaged liblzma; full source also contains GPL material",
        "https://tukaani.org/xz/",
        ("Contents/Frameworks/liblzma.*.dylib",),
    ),
    Component(
        "tcl-tk",
        "Tcl/Tk and Python Tk integration",
        ("tcl-tk@8", "python-tk@3.11"),
        "BSD-style Tcl/Tk terms; Python integration under PSF terms",
        "https://www.tcl-lang.org/",
        (
            "Contents/Frameworks/libtcl*.dylib",
            "Contents/Frameworks/libtk*.dylib",
            "Contents/Frameworks/_tkinter*.so",
        ),
    ),
    Component(
        "pyinstaller",
        "PyInstaller bootloader and frozen runtime",
        (),
        "GPL-2.0-or-later with bootloader exception; runtime hooks Apache-2.0",
        "https://pyinstaller.org/",
        ("Contents/MacOS/AudioShifter",),
    ),
    Component(
        "ffmpeg",
        "FFmpeg / FFprobe",
        ("ffmpeg",),
        "GPL-3.0-or-later for the configured Homebrew build",
        "https://ffmpeg.org/",
        (
            "Contents/Frameworks/bin/ffmpeg",
            "Contents/Frameworks/bin/ffprobe",
            "Contents/Frameworks/libav*.dylib",
            "Contents/Frameworks/libsw*.dylib",
        ),
    ),
    Component(
        "rubberband",
        "Rubber Band",
        ("rubberband",),
        "GPL-2.0-or-later (no commercial licence claimed)",
        "https://breakfastquay.com/rubberband/",
        ("Contents/Frameworks/bin/rubberband",),
    ),
    Component("libvmaf", "libvmaf", ("libvmaf",), "BSD-2-Clause-Patent", "https://github.com/Netflix/vmaf", ("Contents/Frameworks/libvmaf.*.dylib",)),
    Component("openssl", "OpenSSL", ("openssl@3",), "Apache-2.0", "https://openssl-library.org/", ("Contents/Frameworks/libssl.*.dylib", "Contents/Frameworks/libcrypto.*.dylib")),
    Component("libvpx", "libvpx", ("libvpx",), "BSD-3-Clause", "https://www.webmproject.org/code/", ("Contents/Frameworks/libvpx.*.dylib",)),
    Component("dav1d", "dav1d", ("dav1d",), "BSD-2-Clause", "https://code.videolan.org/videolan/dav1d", ("Contents/Frameworks/libdav1d.*.dylib",)),
    Component("lame", "LAME", ("lame",), "LGPL-2.0-or-later", "https://lame.sourceforge.io/", ("Contents/Frameworks/libmp3lame.*.dylib",)),
    Component("opus", "Opus", ("opus",), "BSD-3-Clause", "https://www.opus-codec.org/", ("Contents/Frameworks/libopus.*.dylib",)),
    Component("svt-av1", "SVT-AV1", ("svt-av1",), "BSD-3-Clause", "https://gitlab.com/AOMediaCodec/SVT-AV1", ("Contents/Frameworks/libSvtAv1Enc.*.dylib",)),
    Component("x264", "x264", ("x264",), "GPL-2.0-or-later", "https://www.videolan.org/developers/x264.html", ("Contents/Frameworks/libx264.*.dylib",)),
    Component("x265", "x265", ("x265",), "GPL-2.0-or-later", "https://bitbucket.org/multicoreware/x265_git", ("Contents/Frameworks/libx265.*.dylib",)),
    Component("libsamplerate", "libsamplerate", ("libsamplerate",), "BSD-2-Clause", "https://github.com/libsndfile/libsamplerate", ("Contents/Frameworks/libsamplerate.*.dylib",)),
    Component("libsndfile", "libsndfile", ("libsndfile",), "LGPL-2.1-or-later", "https://libsndfile.github.io/libsndfile/", ("Contents/Frameworks/libsndfile.*.dylib",)),
    Component("mpg123", "mpg123", ("mpg123",), "LGPL-2.1-only", "https://www.mpg123.de/", ("Contents/Frameworks/libmpg123.*.dylib",)),
    Component("libogg", "libogg", ("libogg",), "BSD-3-Clause", "https://www.xiph.org/ogg/", ("Contents/Frameworks/libogg.*.dylib",)),
    Component("libvorbis", "libvorbis", ("libvorbis",), "BSD-3-Clause", "https://xiph.org/vorbis/", ("Contents/Frameworks/libvorbis*.dylib",)),
    Component("flac", "FLAC library", ("flac",), "Xiph BSD-style terms for packaged library; full source has additional terms", "https://xiph.org/flac/", ("Contents/Frameworks/libFLAC.*.dylib",)),
)


FORMULAE: tuple[str, ...] = tuple(
    dict.fromkeys(formula for component in COMPONENTS for formula in component.formulae)
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command_output(args: Sequence[str | Path]) -> str:
    completed = subprocess.run(
        [str(value) for value in args],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        shell=False,
    )
    if completed.returncode:
        raise RuntimeError(
            f"Command failed ({completed.returncode}): {args!r}\n"
            + completed.stderr.decode("utf-8", errors="replace")
        )
    return completed.stdout.decode("utf-8", errors="replace")


def macho_paths(app: Path) -> tuple[Path, ...]:
    found: list[Path] = []
    for path in app.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        if "Mach-O" in command_output(("file", "-b", path)):
            found.append(path)
    return tuple(sorted(found))


def _matches(path: PurePosixPath, pattern: str) -> bool:
    return path.match(pattern)


def map_machos(app: Path, paths: Iterable[Path] | None = None) -> dict[str, tuple[str, ...]]:
    app = app.resolve()
    mapped: dict[str, list[str]] = {component.key: [] for component in COMPONENTS}
    unmatched: list[str] = []
    duplicate: list[str] = []
    for path in paths if paths is not None else macho_paths(app):
        relative = PurePosixPath(path.resolve().relative_to(app).as_posix())
        matches = [
            component.key
            for component in COMPONENTS
            if any(_matches(relative, pattern) for pattern in component.patterns)
        ]
        if not matches:
            unmatched.append(str(relative))
        elif len(matches) > 1:
            duplicate.append(f"{relative}: {matches}")
        else:
            mapped[matches[0]].append(str(relative))
    empty = [key for key, values in mapped.items() if not values]
    if unmatched or duplicate or empty:
        raise RuntimeError(
            f"Incomplete Mach-O component mapping: unmatched={unmatched}, "
            f"duplicate={duplicate}, empty={empty}"
        )
    return {key: tuple(sorted(values)) for key, values in mapped.items()}
