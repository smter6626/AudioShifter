# AudioShifter third-party notices

This file inventories the third-party runtime components embedded in the local
PyInstaller build of `AudioShifter.app`. The inventory is based on the exact
installed bottles, their `INSTALL_RECEIPT.json` records, `otool -L` recursion,
and the license files shipped in each installed prefix on 2026-08-04.

This is a factual engineering record, not legal advice.

## Distribution boundary

The `v0.1.0-alpha.2` application is being prepared as a GitHub Draft
Pre-release with a matching corresponding-source attachment. Covered
AudioShifter-owned code is licensed under `GPL-3.0-or-later`, subject to the
scope and exclusions in the root `LICENSING.md`. The AudioShifter name, logo,
application icon and official branding are governed separately by
`TRADEMARKS.md`; all `windows/` history is excluded from the project GPL grant.
The Draft remains unpublished pending owner review and non-development-Mac
acceptance.

Before providing the application binary to another person, publishing it, or
uploading it to a release service, the distributor must separately confirm and
fulfil all applicable obligations. In particular:

- the Homebrew FFmpeg build is configured with `--enable-gpl` and
  `--enable-version3`, and Homebrew identifies it as GPL-3.0-or-later;
- Rubber Band is GPL-2.0-or-later unless a separate commercial licence has
  been obtained; no commercial licence is claimed here;
- x264 and x265 are GPL-2.0-or-later components of the selected FFmpeg build;
- LGPL components may require notices, licence copies, corresponding source,
  and a practical relinking or replacement route, depending on the manner of
  distribution;
- a public binary distribution must keep the version-matched corresponding
  source attachment available for the applicable GPL components and preserve
  all project and third-party licence materials.

No Developer ID signing, notarization, commercial licence purchase, or public
publication decision is made by this build step.

## Runtime inventory

The `Packaged file(s)` column names the material actually embedded in the app.
System frameworks and `/usr/lib` libraries are supplied by Apple and are not
copied into the app.

| Component | Actual version | Upstream | Licence recorded by source/formula | Local source | Packaged file(s) | Relationship |
|---|---:|---|---|---|---|---|
| CPython | 3.11.15 | <https://www.python.org/> | PSF License | Homebrew `python@3.11` bottle | Python runtime library, stdlib and extension modules | PyInstaller runtime |
| mpdecimal | 4.0.1 | <https://www.bytereef.org/mpdecimal/> | BSD-2-Clause | Homebrew `mpdecimal` bottle | `libmpdec.4.dylib` | CPython `_decimal` transitive |
| XZ Utils / liblzma | 5.8.3 | <https://tukaani.org/xz/> | 0BSD for the packaged `liblzma` library | Homebrew `xz` bottle | `liblzma.5.dylib` | CPython `_lzma` transitive |
| Tcl/Tk | 8.6.18 | <https://www.tcl-lang.org/> | BSD-style Tcl/Tk terms | Homebrew `tcl-tk@8` via `python-tk@3.11` | Tcl/Tk dylibs, scripts and Tk resources | Tkinter runtime |
| PyInstaller bootloader/runtime hooks | 6.21.0 | <https://pyinstaller.org/> | GPL-2.0-or-later with bootloader exception; runtime hooks Apache-2.0 | pinned PyPI wheel in `macos/.venv` | arm64 bootloader and frozen loader/hooks | application freezer |
| FFmpeg / FFprobe | 8.1.2 (`8.1.2_1`) | <https://ffmpeg.org/> | GPL-3.0-or-later for this configured build | Homebrew `ffmpeg` bottle | `bin/ffmpeg`, `bin/ffprobe`, `libavdevice.62`, `libavfilter.11`, `libavformat.62`, `libavcodec.62`, `libswresample.6`, `libswscale.9`, `libavutil.60` | direct audio CLI |
| Rubber Band | 4.0.0 | <https://breakfastquay.com/rubberband/> | GPL-2.0-or-later or separate commercial licence | Homebrew `rubberband` bottle | `bin/rubberband` | direct audio CLI |
| libvmaf | 3.2.0 | <https://github.com/Netflix/vmaf> | BSD-2-Clause-Patent | Homebrew bottle | `libvmaf.3.dylib` | FFmpeg transitive |
| OpenSSL | 3.6.3 | <https://openssl-library.org/> | Apache-2.0 | Homebrew `openssl@3` bottle | `libssl.3.dylib`, `libcrypto.3.dylib` | FFmpeg transitive |
| libvpx | 1.16.0 | <https://www.webmproject.org/code/> | BSD-3-Clause | Homebrew bottle | `libvpx.12.dylib` | FFmpeg transitive |
| dav1d | 1.5.3 | <https://code.videolan.org/videolan/dav1d> | BSD-2-Clause | installed Homebrew bottle receipt | `libdav1d.7.dylib` | FFmpeg transitive |
| LAME | 4.0 | <https://lame.sourceforge.io/> | LGPL-2.0-or-later | Homebrew bottle | `libmp3lame.0.dylib` | FFmpeg encoder and libsndfile transitive |
| Opus | 1.6.1 | <https://www.opus-codec.org/> | BSD-3-Clause | Homebrew bottle | `libopus.0.dylib` | FFmpeg/libsndfile transitive |
| SVT-AV1 | 4.1.0 | <https://gitlab.com/AOMediaCodec/SVT-AV1> | BSD-3-Clause | installed Homebrew bottle receipt | `libSvtAv1Enc.4.dylib` | FFmpeg transitive |
| x264 | r3222 | <https://www.videolan.org/developers/x264.html> | GPL-2.0-or-later | Homebrew bottle | `libx264.165.dylib` | FFmpeg transitive |
| x265 | 4.2 | <https://bitbucket.org/multicoreware/x265_git> | GPL-2.0-or-later | Homebrew bottle | `libx265.216.dylib` | FFmpeg transitive |
| libsamplerate | 0.2.2 | <https://github.com/libsndfile/libsamplerate> | BSD-2-Clause | Homebrew bottle | `libsamplerate.0.dylib` | Rubber Band transitive |
| libsndfile | 1.2.2 (`1.2.2_1`) | <https://libsndfile.github.io/libsndfile/> | LGPL-2.1-or-later | Homebrew bottle | `libsndfile.1.dylib` | Rubber Band transitive |
| mpg123 | 1.33.6 | <https://www.mpg123.de/> | LGPL-2.1-only | Homebrew bottle | `libmpg123.0.dylib` | LAME/libsndfile transitive |
| libogg | 1.3.6 | <https://www.xiph.org/ogg/> | BSD-3-Clause | Homebrew bottle | `libogg.0.dylib` | libsndfile transitive |
| libvorbis | 1.3.7 | <https://xiph.org/vorbis/> | BSD-3-Clause | Homebrew bottle | `libvorbis.0.dylib`, `libvorbisenc.2.dylib` | libsndfile transitive |
| FLAC library | 1.5.0 | <https://xiph.org/flac/> | Xiph BSD-style terms for the packaged library; the full source distribution has additional licences | Homebrew bottle | `libFLAC.14.dylib` | libsndfile transitive |

The exact recursive external-CLI collection manifest is regenerated at
`macos/build/external_dependencies.json` by the build command. It is a local
build artifact and is not committed.

## Licence texts included

The matching licence and notice texts are kept in `macos/licenses/` and copied
into `AudioShifter.app/Contents/Resources/licenses/` by the spec. They were
copied verbatim from the actual installed prefixes or the installed
PyInstaller wheel, not reconstructed from memory.

## Source acquisition

`macos/release/collect_corresponding_source.py` obtains the exact source
versions above from the installed SPDX SBOMs, verifies formula SHA-256 values,
stores the matching historical homebrew-core formula revision and applicable
patches, and maps every packaged Mach-O to one of these components. It also
stores sanitised bottle receipts and build evidence. The generated archive is:

```text
AudioShifter-v0.1.0-alpha.2-corresponding-source.tar.gz
```

Homebrew's independent source-oriented entry points include:

```bash
brew info --json=v2 <formula>
brew fetch --build-from-source <formula>
```

For Python and PyInstaller, the collector fixes the matching upstream release
tag/commit. Prebuilt PyInstaller bootloaders present in its upstream tag archive
are excluded from the corresponding-source copy while its complete bootloader
source and build scripts remain included. For FFmpeg and Rubber Band, the
recorded upstream archives are `ffmpeg-8.1.2.tar.xz` and
`rubberband-4.0.0.tar.bz2`. A public binary release must publish or offer the
corresponding source in the manner required by the applicable licence; merely
linking to an upstream homepage may not be sufficient for that release.
