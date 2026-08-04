# macOS release tooling

This directory contains the reproducible tooling and notes for
`v0.1.0-alpha.1`. Generated applications, downloaded source archives, release
assets, and verification caches are intentionally excluded from Git.

After the release preparation commit has been pushed and annotated tag
`v0.1.0-alpha.1` points at that exact commit, run from the repository root:

```bash
macos/release/build_release_assets.sh
```

The command reruns pytest, rebuilds and audits `AudioShifter.app`, creates the
app ZIP with `ditto`, collects exact corresponding source and Homebrew build
metadata, verifies freshly extracted copies, and atomically publishes the
three local assets into `macos/release-dist/`.

The source collector uses installed Homebrew SBOMs and receipts as version and
checksum authority. It fetches the matching historical homebrew-core formula
revision, includes local and remote formula patches, and rejects a source
download whose SHA-256 does not match the installed package metadata.

The generated source bundle is a factual compliance aid, not legal advice.
Public publication remains blocked while the repository has no root-level
project licence compatible with the bundled GPL components.
