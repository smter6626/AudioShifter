# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from audioshifter.dependencies import DevelopmentDependencyResolver, ResolvedDependencies


@pytest.fixture(scope="session")
def dependencies() -> ResolvedDependencies:
    return DevelopmentDependencyResolver().resolve()


def _run(args: list[str | Path]) -> None:
    completed = subprocess.run(
        [str(value) for value in args],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        shell=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.decode("utf-8", errors="replace"))


@pytest.fixture(scope="session")
def synthetic_sources(
    tmp_path_factory: pytest.TempPathFactory,
    dependencies: ResolvedDependencies,
) -> dict[str, Path]:
    root = tmp_path_factory.mktemp("AudioShifter synthetic sources")
    wav = root / "中文 音频 (test) & sample.WAV"
    _run(
        [
            dependencies.ffmpeg_path,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:sample_rate=48000:duration=1.2",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            "-f",
            "wav",
            wav,
        ]
    )
    formats = {
        "wav": wav,
        "mp3": root / "song.final.v2.MP3",
        "m4a": root / "quote'file.M4A",
        "flac": root / "audio.FLAC",
    }
    _run(
        [
            dependencies.ffmpeg_path,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-i",
            wav,
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            "-f",
            "mp3",
            formats["mp3"],
        ]
    )
    _run(
        [
            dependencies.ffmpeg_path,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-i",
            wav,
            "-c:a",
            "aac",
            "-f",
            "ipod",
            formats["m4a"],
        ]
    )
    _run(
        [
            dependencies.ffmpeg_path,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-i",
            wav,
            "-c:a",
            "flac",
            "-f",
            "flac",
            formats["flac"],
        ]
    )
    return formats
