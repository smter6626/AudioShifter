# macOS release tooling

This directory contains the reproducible tooling and notes for
`v0.1.0-alpha.3`. Generated applications, downloaded source archives, release
assets, and verification caches are intentionally excluded from Git.

`release_config.py` is the single source of the current tag, application
version, Release title, and asset names. Pass the configured tag explicitly if
desired; the script rejects a different tag instead of silently mixing
versions.

After the release preparation commit has been pushed and annotated tag
`v0.1.0-alpha.3` points at that exact commit, run from the repository root:

```bash
macos/release/build_release_assets.sh v0.1.0-alpha.3
```

The command reruns pytest, creates a temporary detached worktree at the release
tag, rebuilds and audits `AudioShifter.app` from that tag, creates the app ZIP
with `ditto`, collects exact corresponding source and Homebrew build metadata,
verifies freshly extracted copies, and atomically publishes the three local
assets into `macos/release-dist/`. The temporary tag worktree uses the existing
development virtual environment only as a build tool; it is not copied into the
application or either release archive.

The source collector uses installed Homebrew SBOMs and receipts as version and
checksum authority. It fetches the matching historical homebrew-core formula
revision, includes local and remote formula patches, and rejects a source
download whose SHA-256 does not match the installed package metadata. If an
official upstream source archive itself contains precompiled objects, the
collector records the original checksum and excluded paths, then emits a
source-only derivative while retaining all source and build scripts.

The generated source bundle is a factual compliance aid, not legal advice. It
includes the tagged repository source, the project `LICENSE`, `LICENSING.md`
and `TRADEMARKS.md`, exact third-party source and checksums, applicable
Homebrew metadata and patches, and the licence texts shipped in the app.

Covered AudioShifter-owned code is licensed under `GPL-3.0-or-later` as defined
in the root `LICENSING.md`. The AudioShifter name, logo, application icon and
official branding are excluded from that grant and governed by
`TRADEMARKS.md`; `windows/` is also excluded. The alpha.3 GitHub Release is
prepared only as a Draft until owner review and non-development-Mac acceptance
are complete.

Ordinary users need only the app ZIP and `SHA256SUMS.txt`. They can validate
the app without downloading corresponding source:

```bash
grep 'AudioShifter-v0.1.0-alpha.3-macOS27-arm64.zip$' SHA256SUMS.txt \
  | shasum -a 256 -c -
```

The corresponding-source archive remains a required Release asset for licence
compliance, inspection, modification, and rebuilding, but it is not required to
run the app. When both archives are present, `shasum -a 256 -c SHA256SUMS.txt`
validates both.
