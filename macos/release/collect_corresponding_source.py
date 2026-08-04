#!/usr/bin/env python3
"""Collect exact corresponding source and reproducibility evidence for a release."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Sequence

from release_manifest import COMPONENTS, FORMULAE, command_output, macho_paths, map_machos, sha256_file


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RELEASE_VERSION = "v0.1.0-alpha.1"
PYINSTALLER_VERSION = "6.21.0"
HOMEBREW_CORE = "https://raw.githubusercontent.com/Homebrew/homebrew-core"
FORBIDDEN_TEXT = (str(Path.home()), str(REPOSITORY_ROOT))


def run(
    args: Sequence[str | Path],
    *,
    cwd: Path | None = None,
    stdout: int | None = subprocess.PIPE,
) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        [str(value) for value in args],
        cwd=cwd,
        stdin=subprocess.DEVNULL,
        stdout=stdout,
        stderr=subprocess.PIPE,
        check=False,
        shell=False,
    )
    if completed.returncode:
        error = completed.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"Command failed ({completed.returncode}): {args!r}\n{error}")
    return completed


def text_output(args: Sequence[str | Path], *, cwd: Path | None = None) -> str:
    return run(args, cwd=cwd).stdout.decode("utf-8", errors="replace")


def safe_reset_directory(path: Path, required_parent: Path) -> None:
    path = path.resolve()
    required_parent = required_parent.resolve()
    if path.parent != required_parent or not path.name:
        raise RuntimeError(f"Refusing to reset unsafe directory: {path}")
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, str):
        result = value.replace(str(REPOSITORY_ROOT), "<REPOSITORY_ROOT>")
        result = result.replace(str(Path.home()), "<HOME>")
        return result
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sanitize(value), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def download(url: str, destination: Path, expected_sha256: str | None = None) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".partial")
    if partial.exists():
        partial.unlink()
    run(
        (
            "curl",
            "--fail",
            "--location",
            "--retry",
            "3",
            "--retry-all-errors",
            "--silent",
            "--show-error",
            "--output",
            partial,
            url,
        )
    )
    actual = sha256_file(partial)
    if expected_sha256 and actual.lower() != expected_sha256.lower():
        partial.unlink()
        raise RuntimeError(
            f"Source checksum mismatch for {url}: expected {expected_sha256}, got {actual}"
        )
    if partial.stat().st_size < 1024:
        preview = partial.read_bytes()[:512].decode("utf-8", errors="replace")
        partial.unlink()
        raise RuntimeError(f"Source download is implausibly small: {url}: {preview!r}")
    partial.replace(destination)
    verify_source_archive(destination)
    return actual


def verify_source_archive(path: Path) -> None:
    completed = subprocess.run(
        ["tar", "-tf", str(path)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            f"Downloaded source is not a readable tar archive: {path}\n"
            + completed.stderr.decode("utf-8", errors="replace")
        )


def source_package(sbom: dict[str, Any], formula: str) -> dict[str, Any]:
    for package in sbom.get("packages", []):
        if package.get("name") == formula:
            return package
    raise RuntimeError(f"Installed SBOM has no primary source package for {formula}")


def source_sha256(package: dict[str, Any]) -> str | None:
    for checksum in package.get("checksums", []):
        if checksum.get("algorithm") == "SHA256" and checksum.get("checksumValue"):
            return str(checksum["checksumValue"])
    return None


def formula_path(formula: str) -> str:
    shard = "lib" if formula.startswith("lib") else formula[0].lower()
    return f"Formula/{shard}/{formula}.rb"


def formula_commits(formula: str) -> tuple[str, ...]:
    payload = json.loads(
        text_output(
        (
            "gh",
            "api",
            "-X",
            "GET",
            "repos/Homebrew/homebrew-core/commits",
            "-f",
            f"path={formula_path(formula)}",
            "-f",
            "per_page=100",
        )
        )
    )
    commits = tuple(item.get("sha", "") for item in payload)
    if not commits or any(not re.fullmatch(r"[0-9a-f]{40}", value) for value in commits):
        raise RuntimeError(f"Could not enumerate historical formula commits for {formula}")
    return commits


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "AudioShifter-release-builder"})
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read()
    return body.decode("utf-8")


def historical_formula(formula: str, expected_source_identity: str) -> tuple[str, str]:
    path = formula_path(formula)
    for commit in formula_commits(formula):
        content = fetch_text(f"{HOMEBREW_CORE}/{commit}/{path}")
        if content.startswith("class ") and expected_source_identity in content:
            return commit, content
    raise RuntimeError(
        f"No recent historical formula for {formula} matches installed source identity "
        f"{expected_source_identity!r}"
    )


def formula_patch_blocks(content: str) -> tuple[tuple[str, str], ...]:
    patches: list[tuple[str, str]] = []
    for block in re.findall(r"(?ms)^\s*patch do\n(.*?)^\s*end\s*$", content):
        url_match = re.search(r'^\s*url\s+["\']([^"\']+)', block, re.MULTILINE)
        sha_match = re.search(r'^\s*sha256\s+["\']([0-9a-f]{64})', block, re.MULTILINE)
        if url_match and sha_match:
            patches.append((url_match.group(1), sha_match.group(1)))
        elif url_match or sha_match:
            raise RuntimeError(f"Incomplete remote patch declaration:\n{block}")
    return tuple(patches)


def local_formula_patches(content: str) -> tuple[str, ...]:
    return tuple(sorted(set(re.findall(r'["\'](Patches/[^"\']+)["\']', content))))


def archive_name(url: str, fallback: str) -> str:
    name = Path(urllib.parse.unquote(urllib.parse.urlparse(url).path)).name
    if not name or ".tar" not in name.lower() and not name.lower().endswith(".tgz"):
        return fallback
    return name


def collect_formula(
    formula: str,
    root: Path,
    source_directory: Path,
) -> dict[str, Any]:
    prefix = Path(text_output(("brew", "--prefix", formula)).strip()).resolve()
    receipt_path = prefix / "INSTALL_RECEIPT.json"
    sbom_path = prefix / "sbom.spdx.json"
    if not receipt_path.is_file() or not sbom_path.is_file():
        raise FileNotFoundError(f"Installed metadata is missing for {formula}: {prefix}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    sbom = json.loads(sbom_path.read_text(encoding="utf-8"))
    package = source_package(sbom, formula)
    version = str(package["versionInfo"])
    url = str(package["downloadLocation"])
    expected_sha = source_sha256(package)

    source_identity = expected_sha or version
    commit, formula_text = historical_formula(formula, source_identity)
    if expected_sha and expected_sha not in formula_text:
        raise RuntimeError(
            f"Historical formula {formula}@{commit} does not contain installed source SHA {expected_sha}"
        )

    formula_file = root / "homebrew" / "formulae" / f"{formula}.rb"
    formula_file.parent.mkdir(parents=True, exist_ok=True)
    formula_file.write_text(formula_text, encoding="utf-8")
    commit_file = root / "homebrew" / "formula-commits" / f"{formula}.txt"
    commit_file.parent.mkdir(parents=True, exist_ok=True)
    commit_file.write_text(commit + "\n", encoding="utf-8")
    stored_receipt = root / "homebrew" / "install-receipts" / formula / "INSTALL_RECEIPT.json"
    stored_sbom = root / "homebrew" / "sbom" / formula / "sbom.spdx.json"
    write_json(stored_receipt, receipt)
    write_json(stored_sbom, sbom)
    build_options = {
        "formula": formula,
        "installed_prefix_version": prefix.name,
        "used_options": receipt.get("used_options", []),
        "unused_options": receipt.get("unused_options", []),
        "compiler": receipt.get("compiler"),
        "arch": receipt.get("arch"),
        "built_on": receipt.get("built_on"),
        "runtime_dependencies": receipt.get("runtime_dependencies", []),
        "source": receipt.get("source"),
        "formula_commit": commit,
        "formula_path": formula_path(formula),
    }
    build_options_path = root / "homebrew" / "build-options" / f"{formula}.json"
    write_json(build_options_path, build_options)

    source_directory.mkdir(parents=True, exist_ok=True)
    if formula == "x264" and not expected_sha:
        revision_match = re.search(r'revision:\s*["\']([0-9a-f]{40})["\']', formula_text)
        if not revision_match:
            raise RuntimeError("Exact x264 git revision is absent from its historical formula")
        revision = revision_match.group(1)
        url = f"https://code.videolan.org/videolan/x264/-/archive/{revision}/x264-{revision}.tar.gz"
        filename = f"x264-{revision}.tar.gz"
    else:
        filename = archive_name(url, f"{formula}-{version}.tar.gz")
    source_path = source_directory / filename
    actual_sha = download(url, source_path, expected_sha)

    patch_paths: list[str] = []
    for relative in local_formula_patches(formula_text):
        destination = root / "homebrew" / "patches" / formula / Path(relative).name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(fetch_text(f"{HOMEBREW_CORE}/{commit}/{relative}"), encoding="utf-8")
        patch_paths.append(destination.relative_to(root).as_posix())
    for index, (patch_url, patch_sha) in enumerate(formula_patch_blocks(formula_text), start=1):
        suffix = Path(urllib.parse.urlparse(patch_url).path).suffix or ".patch"
        destination = root / "homebrew" / "patches" / formula / f"remote-{index}{suffix}"
        download_patch(patch_url, destination, patch_sha)
        patch_paths.append(destination.relative_to(root).as_posix())

    return {
        "formula_name": formula,
        "version": version,
        "installed_prefix_version": prefix.name,
        "source_url": url,
        "source_archive": source_path.relative_to(root).as_posix(),
        "source_sha256": actual_sha,
        "expected_source_sha256": expected_sha,
        "formula_file": formula_file.relative_to(root).as_posix(),
        "formula_commit": commit,
        "formula_commit_evidence": commit_file.relative_to(root).as_posix(),
        "receipt": stored_receipt.relative_to(root).as_posix(),
        "sbom": stored_sbom.relative_to(root).as_posix(),
        "build_options": build_options_path.relative_to(root).as_posix(),
        "patches": patch_paths,
    }


def download_patch(url: str, destination: Path, expected_sha: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    run(("curl", "--fail", "--location", "--retry", "3", "--silent", "--show-error", "--output", destination, url))
    actual = sha256_file(destination)
    if actual != expected_sha:
        destination.unlink()
        raise RuntimeError(f"Patch checksum mismatch for {url}: expected {expected_sha}, got {actual}")


def collect_pyinstaller(root: Path) -> dict[str, Any]:
    tag = f"v{PYINSTALLER_VERSION}"
    commit = text_output(
        ("gh", "api", f"repos/pyinstaller/pyinstaller/commits/{tag}", "--jq", ".sha")
    ).strip()
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise RuntimeError(f"Could not resolve PyInstaller {tag} commit: {commit!r}")
    url = f"https://github.com/pyinstaller/pyinstaller/archive/refs/tags/{tag}.tar.gz"
    directory = root / "third-party" / "pyinstaller"
    directory.mkdir(parents=True, exist_ok=True)
    upstream_archive = directory / f"pyinstaller-{tag}-upstream.tar.gz"
    upstream_sha = download(url, upstream_archive)
    destination = directory / f"pyinstaller-{tag}-source-only.tar.gz"
    excluded_prebuilt: list[str] = []
    with tempfile.TemporaryDirectory(prefix="pyinstaller-source-", dir=directory) as temporary:
        extracted = Path(temporary) / "extracted"
        extracted.mkdir()
        with tarfile.open(upstream_archive, "r:gz") as archive:
            archive.extractall(extracted, filter="data")
        roots = tuple(extracted.iterdir())
        if len(roots) != 1 or not roots[0].is_dir():
            raise RuntimeError("PyInstaller tag archive has an unexpected root layout")
        for candidate in roots[0].rglob("*"):
            if not candidate.is_file():
                continue
            description = text_output(("file", "-b", candidate))
            if any(kind in description for kind in ("Mach-O", "PE32", "ELF")):
                excluded_prebuilt.append(candidate.relative_to(roots[0]).as_posix())
                candidate.unlink()
        if not excluded_prebuilt:
            raise RuntimeError("Expected PyInstaller's upstream tag archive to contain prebuilt bootloaders")
        with tarfile.open(destination, "w:gz", format=tarfile.PAX_FORMAT) as archive:
            archive.add(roots[0], arcname=roots[0].name, recursive=True)
    upstream_archive.unlink()
    verify_source_archive(destination)
    actual = sha256_file(destination)
    return {
        "version": PYINSTALLER_VERSION,
        "source_url": url,
        "source_archive": destination.relative_to(root).as_posix(),
        "source_sha256": actual,
        "expected_source_sha256": None,
        "upstream_archive_sha256": upstream_sha,
        "upstream_tag": tag,
        "upstream_commit": commit,
        "excluded_upstream_prebuilt_files": sorted(excluded_prebuilt),
        "formula_name": None,
        "formula_file": None,
        "formula_commit": None,
        "formula_commit_evidence": None,
        "receipt": None,
        "sbom": None,
        "build_options": "build-evidence/pyinstaller-version.txt",
        "patches": [],
    }


def collect_build_evidence(root: Path, app: Path, mapping: dict[str, tuple[str, ...]]) -> None:
    evidence = root / "build-evidence"
    evidence.mkdir(parents=True)
    commands = {
        "ffmpeg-version.txt": (app / "Contents/Frameworks/bin/ffmpeg", "-version"),
        "ffmpeg-buildconf.txt": (app / "Contents/Frameworks/bin/ffmpeg", "-buildconf"),
        "ffprobe-version.txt": (app / "Contents/Frameworks/bin/ffprobe", "-version"),
        "rubberband-version.txt": (app / "Contents/Frameworks/bin/rubberband", "--version"),
        "pyinstaller-version.txt": (REPOSITORY_ROOT / "macos/.venv/bin/pyinstaller", "--version"),
        "python-version.txt": (REPOSITORY_ROOT / "macos/.venv/bin/python", "--version"),
        "macos-version.txt": ("sw_vers",),
        "host-architecture.txt": ("uname", "-m"),
        "git-show.txt": ("git", "show", "-s", "--format=fuller", "HEAD"),
    }
    for name, command in commands.items():
        (evidence / name).write_text(sanitize(text_output(command)), encoding="utf-8")
    with (app / "Contents/Info.plist").open("rb") as handle:
        write_json(evidence / "info-plist.json", plistlib.load(handle))

    inventory: list[dict[str, Any]] = []
    by_path = {path: component for component, paths in mapping.items() for path in paths}
    for binary in macho_paths(app):
        relative = binary.resolve().relative_to(app.resolve()).as_posix()
        inventory.append(
            {
                "path": relative,
                "component": by_path[relative],
                "sha256": sha256_file(binary),
                "architecture": text_output(("lipo", "-archs", binary)).strip(),
                "linked_libraries": text_output(("otool", "-L", binary)).splitlines()[1:],
            }
        )
    write_json(evidence / "macho-inventory.json", inventory)
    write_json(
        evidence / "packaged-file-mapping.json",
        {"macho_count": len(inventory), "components": mapping, "unmapped": []},
    )
    external_manifest = REPOSITORY_ROOT / "macos/build/external_dependencies.json"
    if not external_manifest.is_file():
        raise FileNotFoundError(f"Packaging dependency manifest is missing: {external_manifest}")
    write_json(
        evidence / "external-dependencies.json",
        json.loads(external_manifest.read_text(encoding="utf-8")),
    )
    for name in ("packaging_test_report.md", "THIRD_PARTY_NOTICES.md"):
        source = REPOSITORY_ROOT / "macos" / name
        (evidence / name).write_text(sanitize(source.read_text(encoding="utf-8")), encoding="utf-8")


def internal_sha256s(root: Path) -> None:
    checksum_file = root / "SHA256SUMS.txt"
    lines: list[str] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file() and item != checksum_file):
        lines.append(f"{sha256_file(path)}  {path.relative_to(root).as_posix()}")
    checksum_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default=RELEASE_VERSION)
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    args = parser.parse_args()

    app = args.app.resolve()
    if not app.is_dir():
        raise FileNotFoundError(f"Built app is missing: {app}")
    tag_commit = text_output(("git", "rev-parse", f"{args.tag}^{{commit}}"), cwd=REPOSITORY_ROOT).strip()
    head_commit = text_output(("git", "rev-parse", "HEAD"), cwd=REPOSITORY_ROOT).strip()
    if tag_commit != head_commit:
        raise RuntimeError(f"Release tag {args.tag}={tag_commit} does not match HEAD={head_commit}")
    if text_output(("git", "status", "--porcelain"), cwd=REPOSITORY_ROOT):
        raise RuntimeError("Corresponding source must be generated from a clean tagged worktree")

    work_parent = args.work_dir.resolve()
    work_parent.mkdir(parents=True, exist_ok=True)
    package_name = f"AudioShifter-{args.tag}-corresponding-source"
    package_root = work_parent / package_name
    safe_reset_directory(package_root, work_parent)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    partial_output = output.with_name(output.name + ".partial")
    if partial_output.exists():
        partial_output.unlink()

    audioshifter = package_root / "audioshifter"
    audioshifter.mkdir()
    repository_archive = audioshifter / "repository-source.tar.gz"
    run(("git", "archive", "--format=tar.gz", f"--output={repository_archive}", args.tag), cwd=REPOSITORY_ROOT)
    (audioshifter / "git-commit.txt").write_text(tag_commit + "\n", encoding="utf-8")
    (audioshifter / "git-tag.txt").write_text(args.tag + "\n", encoding="utf-8")

    mapping = map_machos(app)
    formula_records: dict[str, dict[str, Any]] = {}
    for formula in FORMULAE:
        component_key = next(item.key for item in COMPONENTS if formula in item.formulae)
        formula_records[formula] = collect_formula(
            formula,
            package_root,
            package_root / "third-party" / component_key,
        )
    pyinstaller_record = collect_pyinstaller(package_root)
    collect_build_evidence(package_root, app, mapping)

    dependency_graph = {
        formula: json.loads(
            (package_root / "homebrew" / "build-options" / f"{formula}.json").read_text(
                encoding="utf-8"
            )
        ).get("runtime_dependencies", [])
        for formula in FORMULAE
    }
    write_json(package_root / "homebrew" / "dependency-graph" / "runtime-dependencies.json", dependency_graph)
    shutil.copytree(REPOSITORY_ROOT / "macos/licenses", package_root / "licenses")

    component_records: list[dict[str, Any]] = []
    for component in COMPONENTS:
        sources = (
            [pyinstaller_record]
            if component.key == "pyinstaller"
            else [formula_records[formula] for formula in component.formulae]
        )
        versions = sorted({str(source["version"]) for source in sources})
        component_records.append(
            {
                "id": component.key,
                "name": component.name,
                "version": ", ".join(versions),
                "licence": component.licence,
                "upstream": component.upstream,
                "packaged_files": mapping[component.key],
                "sources": sources,
                "build_evidence": [
                    "build-evidence/macho-inventory.json",
                    "build-evidence/packaged-file-mapping.json",
                ],
            }
        )

    manifest = {
        "release": args.tag,
        "release_commit": tag_commit,
        "generated_at_utc": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
        "scope": "Corresponding source and build evidence for the embedded non-Apple runtime components",
        "project_licence_status": "MISSING — public publication blocked pending owner decision",
        "audioshifter_source": {
            "archive": repository_archive.relative_to(package_root).as_posix(),
            "sha256": sha256_file(repository_archive),
            "tag": args.tag,
            "commit": tag_commit,
        },
        "component_count": len(component_records),
        "macho_count": sum(len(paths) for paths in mapping.values()),
        "unmapped_macho_files": [],
        "components": component_records,
    }
    write_json(package_root / "MANIFEST.json", manifest)
    (package_root / "README.md").write_text(
        f"""# AudioShifter {args.tag} corresponding source

该源码包对应 AudioShifter {args.tag} 的 macOS arm64 二进制。
应用源码同时固定在 `{args.tag}` Git tag，commit `{tag_commit}`。
本包包含实际内置第三方组件的源码、许可证、Homebrew 构建元数据、
适用补丁和复现证据。`MANIFEST.json` 将每个组件映射到打包文件和源码。

This archive accompanies the AudioShifter macOS arm64 binary. It contains the
tagged AudioShifter repository source plus exact third-party source archives,
licences, historical Homebrew formulae, receipts, applicable patches, and build
evidence for the embedded runtime components. Verify every file with the internal
`SHA256SUMS.txt`. This package is a factual compliance aid, not legal advice.

AudioShifter currently has no root-level project licence; accordingly the GitHub
Release must remain a Draft until the owner selects a compatible licence.
""",
        encoding="utf-8",
    )
    internal_sha256s(package_root)

    for text_file in package_root.rglob("*"):
        if not text_file.is_file() or text_file.suffix.lower() in {".gz", ".xz", ".bz2", ".tgz"}:
            continue
        content = text_file.read_text(encoding="utf-8", errors="ignore")
        for forbidden in FORBIDDEN_TEXT:
            if forbidden and forbidden in content:
                raise RuntimeError(f"Private absolute path leaked into corresponding source: {text_file}")

    with tarfile.open(partial_output, "w:gz", format=tarfile.PAX_FORMAT) as archive:
        archive.add(package_root, arcname=package_root.name, recursive=True)
    with tarfile.open(partial_output, "r:gz") as archive:
        if not archive.getmembers():
            raise RuntimeError("Corresponding source archive is empty")
    partial_output.replace(output)
    print(
        json.dumps(
            {
                "output": str(output),
                "sha256": sha256_file(output),
                "size_bytes": output.stat().st_size,
                "component_count": len(component_records),
                "macho_count": manifest["macho_count"],
                "tag": args.tag,
                "commit": tag_commit,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
