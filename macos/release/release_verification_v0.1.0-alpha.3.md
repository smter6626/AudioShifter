# AudioShifter v0.1.0-alpha.3 Draft verification

## Final status

```text
PARTIAL — v0.1.0-alpha.3 Draft prepared; awaiting user review and manual non-development-Mac acceptance
```

All automated, packaging, corresponding-source, native-menu, upload, and
download-back checks passed. The GitHub Release remains a Draft and was not
published. The remaining action is the project owner's review and manual
acceptance on a non-development Apple Silicon Mac.

## Version and legal viewer

- Git/Release display version: `0.1.0-alpha.3`.
- Python project version: `0.1.0a3`.
- Bundle identifier: `io.github.smter6626.audioshifter`.
- `CFBundleShortVersionString`: `0.1.0`, matching
  `^[0-9]+\.[0-9]+\.[0-9]+$`.
- `CFBundleVersion`: `3`.
- Main window title remains `AudioShifter 音频变调变速`.

On Aqua Tk 8.6, the application creates the special `.menubar.apple` menu
before assigning `.menubar` to the root window. Tk maps that special menu to
the real macOS Application menu and supplies the normal Services, Hide, and
Quit items. The project adds exactly one custom item named `License`; it does
not create a second ordinary cascade, File menu, Help menu, or main-window
button.

`License` opens a reusable, non-modal, resizable `AudioShifter License` window.
The window is English-only, uses a read-only but selectable Text widget with a
vertical scrollbar, supports Command-C and Command-W, and is recreated after
being closed. Repeated invocation while open raises the same window instead of
creating duplicates.

The viewer resolves and reads `Contents/Resources/LICENSE` in a frozen app and
the repository-root `LICENSE` in source mode. It does not use the current
working directory, a developer absolute path, or the network, and it does not
hard-code GPL text in Python. Root, tag application, ZIP-extracted application,
and Draft-downloaded application all reported the same 35,149-byte GPLv3 text
with SHA-256:

```text
3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986
```

The text includes `GNU GENERAL PUBLIC LICENSE`, `Version 3, 29 June 2007`,
`END OF TERMS AND CONDITIONS`, and the complete post-terms application
instructions through the final `why-not-lgpl.html` line. No ellipsis,
truncation marker, summary substitute, or network link replaces the licence.

## Native macOS menu evidence

Computer Use inspected both the tag-built final ZIP extraction and a fresh
extraction made only from the GitHub Draft download. In each case, the real
menu immediately to the right of the Apple menu was `AudioShifter`. Its
accessibility tree contained:

```text
AudioShifter
  License
  Preferences… (disabled, system-provided)
  Services
  Hide AudioShifter
  Hide Others
  Show All
  Quit AudioShifter
```

Selecting `License` opened `AudioShifter License` with the English alpha.3
heading and GPL beginning. Command-End on the text scrolled to the actual end;
Command-W returned to the Chinese main window; selecting the same menu item
again recreated the viewer. Selecting the item while the viewer was already
open left exactly one licence window. No Accessibility permission or system
privacy/security setting was requested or changed.

This is direct visual and accessibility evidence from the final packaged app,
not an inference from unit tests. The final user acceptance on a separate,
non-development Mac remains intentionally pending.

## Licensing and branding

- Covered AudioShifter-owned code uses `GPL-3.0-or-later`, as scoped by root
  `LICENSING.md`.
- `windows/` history, third-party material, and AudioShifter source-identifying
  brand assets remain outside that GPL grant.
- `TRADEMARKS.md` and `LICENSING.md` grant only the brand permission needed to
  reproduce an unmodified official build from an official tag or redistribute
  an unchanged official Release.
- Modified versions must use another name, bundle identifier, icon, logo, and
  source-identifying branding unless prior written permission is obtained.
- The policy does not prohibit commercial use, charging, modification, or
  distribution of the GPL-covered code under another brand.

The final app contains `LICENSE`, `LICENSING.md`, `TRADEMARKS.md`,
`THIRD_PARTY_NOTICES.md`, and `licenses/` in `Contents/Resources`.

## Git and GitHub Draft

- Release tag: `v0.1.0-alpha.3`.
- Release/application/tooling commit:
  `a6174b45666a586c2920afdd42e600dce7a8bcda`.
- Annotated tag object: `301d4ef331a2344cf0231601e696319d8870f3da`.
- Draft database ID: `364860803`.
- Draft URL (authenticated collaborators only):
  <https://github.com/smter6626/AudioShifter/releases/tag/untagged-eb4c98469e0200c34d24>
- Title: `AudioShifter v0.1.0-alpha.3 — macOS arm64 preview`.
- State: Draft = `true`, Pre-release = `true`, published time = `null`.
- Creation, upload, inspection, and download path: authenticated GitHub CLI.

The remote annotated tag resolves to the exact release commit. The app and
embedded repository source snapshot were both built from a detached worktree
at that tag. No alpha.1 or alpha.2 tag, Draft, note, or asset was moved,
replaced, deleted, re-uploaded, or published.

## Build environment and command

- Date: 2026-08-04.
- Host architecture: Apple Silicon `arm64`.
- macOS: 27.0, build `26A5378n`.
- Python: 3.11.15.
- Tcl/Tk: 8.6.18, Aqua.
- PyInstaller: 6.21.0.
- FFmpeg / FFprobe: 8.1.2.
- Rubber Band: 4.0.0.
- Reproducible command:

  ```bash
  macos/release/build_release_assets.sh v0.1.0-alpha.3
  ```

The command ran all tests, built from a detached tag worktree, created the app
ZIP with `ditto`, collected exact corresponding source and Homebrew build
metadata, verified fresh extractions, and atomically installed the three local
assets into the ignored `macos/release-dist/` directory.

## Draft assets and checksums

| Asset | Bytes | SHA-256 |
|---|---:|---|
| `AudioShifter-v0.1.0-alpha.3-macOS27-arm64.zip` | 27,764,722 | `a7866775734cbcde12d1b3d5186a09f71da71fe380650438d67a8d1f2987711d` |
| `AudioShifter-v0.1.0-alpha.3-corresponding-source.tar.gz` | 200,051,018 | `2936187f84081c322e3d43254ec2a7f829037db84dc9b7e3532fc868dd9546d2` |
| `SHA256SUMS.txt` | 234 | `611171939727f40a008c514f6664b5d2ddd5d04b17b23827622fc8babb88d9c2` |

Exact `SHA256SUMS.txt` content:

```text
a7866775734cbcde12d1b3d5186a09f71da71fe380650438d67a8d1f2987711d  AudioShifter-v0.1.0-alpha.3-macOS27-arm64.zip
2936187f84081c322e3d43254ec2a7f829037db84dc9b7e3532fc868dd9546d2  AudioShifter-v0.1.0-alpha.3-corresponding-source.tar.gz
```

GitHub reported all three assets as `uploaded` with independently matching
sizes and SHA-256 digests.

## App ZIP and standalone verification

The application ZIP was created with
`ditto -c -k --sequesterRsrc --keepParent`. All results below were reproduced
on a fresh `ditto -x -k` extraction from the final asset, then again from the
asset downloaded from the Draft:

- Extracted application logical size: 63,410,941 bytes.
- Custom `AudioShifter.icns` and all required legal resources are present.
- 75 Mach-O files, all thin `arm64`.
- 324 dynamic references and 20 `LC_RPATH` commands audited.
- External non-system load commands: 0.
- `/opt/homebrew`, `.venv`, and repository runtime load commands: 0.
- Symlinks: 47; broken or bundle-external links: 0.
- `codesign --verify --deep --strict --verbose=4`: return code 0.
- Signature: ad-hoc; `TeamIdentifier=not set`.
- `spctl`: rejected as expected because no Developer ID identity or Apple
  notarization is present.
- Restricted launch used PATH `/usr/bin:/bin:/usr/sbin:/sbin`, no
  `VIRTUAL_ENV`, and a system temporary working directory.

Only the following packaged commands were invoked:

```text
AudioShifter.app/Contents/Frameworks/bin/ffmpeg
AudioShifter.app/Contents/Frameworks/bin/ffprobe
AudioShifter.app/Contents/Frameworks/bin/rubberband
```

## Real pipeline, source protection, conflict, and cancellation

The ZIP-extracted app processed synthetic WAV, MP3, M4A, and FLAC under the
restricted PATH. Every output stream reported:

```text
codec_name=mp3
sample_rate=44100
channels=2
bit_rate=320000
```

Representative WAV output duration was 2.500000 seconds and SHA-256 was
`c9232e4a165f4de240b5a061b6b1ab628e49e7a71748f4b6e10697ec8ac047a9`.
All four source hashes remained unchanged. Conflict allocation created `_2`
and `_3`, preserved the prior output hash, and never overwrote a file.

A real bundle-internal Rubber Band process was observed during cancellation,
then reaped. It left zero partial outputs and zero workspace leaks and
preserved the source hash. No alpha.3 verifier subprocess remained afterward;
an unrelated pre-existing `/Applications/AudioShifter.app` process was not
modified.

## Corresponding source

- Project licence status:
  `GPL-3.0-or-later for covered AudioShifter-owned code`.
- The manifest records the `windows/`, branding, and third-party exclusions,
  plus the narrow permission for unmodified official builds and redistribution.
- Conceptual third-party runtime components: 22.
- Exact source archive records: 23.
- Historical Homebrew formulae and receipts: 22 each.
- Applicable patches included and hashed: 8.
- Packaged Mach-O mappings: 75 of 75; unmapped = 0.
- Internal corresponding-source checksum entries: 201.
- Source tag, release commit, and tooling commit all resolve to alpha.3 /
  `a6174b45666a586c2920afdd42e600dce7a8bcda`.

The archive includes the exact tag source, GPL text, licensing and brand
policy, License viewer implementation, release tools, exact third-party source,
formulae, receipts, applicable patches, build evidence, packaged-file mapping,
and third-party licence texts. Verification found no missing component, patch,
hash, or Mach-O mapping and no compiled third-party binary in the final source
package.

## Ordinary-user checksum and Draft download-back

An independent directory containing only the App ZIP and `SHA256SUMS.txt`
(without corresponding source) successfully ran the documented command:

```bash
grep 'AudioShifter-v0.1.0-alpha.3-macOS27-arm64.zip$' SHA256SUMS.txt \
  | shasum -a 256 -c -
```

It reported:

```text
AudioShifter-v0.1.0-alpha.3-macOS27-arm64.zip: OK
```

### Portability correction after non-development-Mac acceptance

The command above, including its trailing `$` grep anchor, passed in the build
verification environment and is retained as the original historical record.
On the downloaded copy used for acceptance on the non-development Mac, that
form did not produce a checksum line that `shasum` could recognise. The ZIP and
`SHA256SUMS.txt` assets themselves were not incorrect and were not changed.

The target Mac returned `OK` with the portable public command below, which
removes a possible carriage-return character before passing the selected line
to `shasum`:

```bash
grep 'AudioShifter-v0.1.0-alpha.3-macOS27-arm64.zip' SHA256SUMS.txt \
  | tr -d '\r' \
  | shasum -a 256 -c -
```

A direct `shasum -a 256` calculation on the target Mac independently reported
`a7866775734cbcde12d1b3d5186a09f71da71fe380650438d67a8d1f2987711d`,
exactly matching the Draft asset record. All current public user instructions
and the Release notes now use the portable form.

All three assets were also downloaded from Draft ID `364860803` into a fresh
ignored directory using `gh release download`. They were byte-for-byte equal
to the local final assets. The full two-archive checksum produced two `OK`
results, and the full verifier ran only against the downloaded copies. ZIP
extraction, version plist, legal resources, native License menu/viewer,
codesign, Mach-O, dynamic paths, symlinks, restricted launch, four formats,
conflict, cancellation, corresponding-source MANIFEST, patches, and all
internal hashes passed.

## Tests, Gatekeeper, compatibility, and remaining acceptance

Automated result:

```text
165 passed, 0 failed, 0 skipped
```

Release notes state that ordinary users need only the App ZIP and checksum
file; corresponding source is optional for running the application. They also
state that the app uses PyInstaller ad-hoc signing, has no Developer ID,
notarization, or stapling, and may require the per-application “系统设置 →
隐私与安全性 → 仍要打开” action. They do not recommend disabling Gatekeeper.

The application is built and verified only on Apple Silicon arm64, macOS 27.0
build `26A5378n`. Older macOS releases are untested and may not run. Intel Mac,
Rosetta, and universal2 are unsupported.

The Draft must remain unpublished until the project owner reviews it and
performs manual acceptance on a non-development Mac. No Developer ID signing,
notarization, stapling, DMG, public Release publication, alpha.1/alpha.2
mutation, Windows modification, or Android active-step change occurred.
