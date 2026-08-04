# AudioShifter licensing

Copyright (C) 2026 Yeming Dai

This document explains which AudioShifter materials are licensed under the GNU
General Public License version 3 or any later version (`GPL-3.0-or-later`), and
which materials are governed separately. It does not alter the verbatim licence
terms in [`LICENSE`](LICENSE).

## Code copyright licence

Unless a file says otherwise, Yeming Dai licenses the following
AudioShifter-owned material under `GPL-3.0-or-later`:

- source code, tests, build scripts, packaging tools, and release tools under
  `macos/`;
- current and future project source code, tests, and build tools under
  `mobile/`;
- root-level shared project code and build configuration supporting those
  implementations, including `pyproject.toml`; and
- project documentation supporting the covered implementations, including the
  macOS design and rebuild documentation.

The full, unmodified GNU GPL version 3 text is in [`LICENSE`](LICENSE). The
`-or-later` grant means recipients may use GPL version 3 or, at their option,
any later version published by the Free Software Foundation.

The GPL permits use, study, modification, redistribution, commercial use, and
charging money, subject to its terms. Nothing in the branding policy prohibits
publishing or commercially distributing the covered GPL code under a different
product name and brand.

## Material excluded from this GPL grant

The following material is not licensed by Yeming Dai under this project's
`GPL-3.0-or-later` grant:

1. **Windows history.** All content under `windows/` is historical material and
   is excluded and is not offered under the project GPL grant. Its presence in
   the repository or a repository source archive does not grant permission
   under this project licence.
2. **AudioShifter branding.** The AudioShifter name, logo, application icon,
   official release visual identity, and other source-identifying brand
   elements are excluded. The known tracked brand asset files are:

   ```text
   macos/assets/source/audioshifter_icon.png
   macos/assets/AudioShifter.icns
   ```

   Brand use is governed by [`TRADEMARKS.md`](TRADEMARKS.md), not by the GPL.
   A separate, narrow permission allows copying the AudioShifter name, icon,
   and other brand assets only as necessary to reproduce an unmodified
   official build from an official AudioShifter tag or to redistribute an
   unmodified official Release. This does not place those assets under the GPL
   and does not permit their use for a modified version or fork.
3. **Third-party material.** Third-party programs, libraries, source archives,
   licence texts, notices, and other third-party material remain governed by
   their respective licences and copyright holders. The project GPL grant does
   not relicense them.

A file-specific copyright or licence notice takes priority for that file.

## Modified versions and branding

The GPL rights to the covered code are independent of permission to present a
modified product as an official AudioShifter release. A modified version or
fork may use and commercially distribute the covered GPL code, but—unless the
project owner gives written permission—it must:

- use a different product and application name;
- use a different bundle identifier;
- replace the AudioShifter logo and application icon;
- replace other brand elements likely to imply an official source; and
- clearly identify itself as an unofficial fork as described in
  [`TRADEMARKS.md`](TRADEMARKS.md).

Accurate descriptive references such as “based on AudioShifter” remain
permitted under the branding policy.

An unmodified build reproduced from an official AudioShifter tag may retain the
official name, bundle identifier, and brand assets only for that reproduction.
Any code or product modification ends that narrow permission unless the project
owner gives prior written permission.

## Official binaries and corresponding source

An official AudioShifter macOS binary combines covered AudioShifter-owned code
with separately licensed third-party components, including GPL and LGPL
components. Each binary Release therefore provides a version-specific
corresponding-source attachment containing:

- the exact tagged AudioShifter repository source;
- the exact third-party source used for embedded runtime components;
- applicable Homebrew formulae, receipts, build options, and patches;
- build and packaged-file mapping evidence; and
- the relevant third-party licence texts and notices.

The corresponding-source attachment supplements the tagged repository source;
GitHub's automatically generated repository archives do not replace it for the
embedded third-party components.

## Which document answers which question?

- [`LICENSE`](LICENSE) is the complete GNU GPL version 3 legal text governing
  covered AudioShifter-owned code under the `GPL-3.0-or-later` grant.
- [`LICENSING.md`](LICENSING.md) defines the project-specific copyright scope,
  exclusions, and relationship between official binaries and corresponding
  source.
- [`TRADEMARKS.md`](TRADEMARKS.md) governs the AudioShifter name, icon, official
  identity, attribution, and avoidance of source confusion. It does not revoke
  or narrow GPL code rights.
- [`macos/THIRD_PARTY_NOTICES.md`](macos/THIRD_PARTY_NOTICES.md) inventories
  embedded third-party runtime components, their versions, licences, source,
  and distribution considerations.
- Files under [`macos/licenses/`](macos/licenses/) contain the third-party
  licence and notice texts shipped with the application.

This document is a project licensing statement, not legal advice about any
particular redistribution.
