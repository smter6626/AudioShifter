# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai
"""Locate and present the complete bundled AudioShifter project licence."""

from __future__ import annotations

import hashlib
import sys
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Callable

from . import __display_version__


GPL_V3_SHA256 = "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986"
REQUIRED_GPL_MARKERS = (
    "GNU GENERAL PUBLIC LICENSE",
    "Version 3, 29 June 2007",
    "END OF TERMS AND CONDITIONS",
)


class LicenseResourceError(RuntimeError):
    """Raised when the complete packaged project licence cannot be loaded."""


@dataclass(frozen=True, slots=True)
class LicenseDocument:
    path: Path
    text: str
    sha256: str


def source_repository_root() -> Path:
    """Derive the repository root from this module without using cwd."""

    return Path(__file__).resolve().parents[3]


def packaged_contents_root() -> Path:
    """Return the Contents directory for the running PyInstaller macOS app."""

    executable = Path(sys.executable).resolve()
    if executable.parent.name != "MacOS" or executable.parent.parent.name != "Contents":
        raise LicenseResourceError(
            f"The frozen executable is not inside a macOS application bundle: {executable}"
        )
    return executable.parent.parent


def license_candidates() -> tuple[Path, ...]:
    """Return ordered development/frozen candidates for the complete GPL text."""

    if bool(getattr(sys, "frozen", False)):
        candidates = [packaged_contents_root() / "Resources" / "LICENSE"]
        resource_root = getattr(sys, "_MEIPASS", None)
        if resource_root:
            candidates.append(Path(resource_root).resolve() / "LICENSE")
        return tuple(dict.fromkeys(candidates))
    return (source_repository_root() / "LICENSE",)


def locate_license_file() -> Path:
    """Find the complete project LICENSE using a deterministic local search."""

    candidates = license_candidates()
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    rendered = ", ".join(str(path) for path in candidates)
    raise LicenseResourceError(f"The complete LICENSE file was not found. Checked: {rendered}")


def load_license_document(path: Path | None = None) -> LicenseDocument:
    """Load and validate the exact official GPLv3 text shipped with the app."""

    selected = (path or locate_license_file()).resolve()
    try:
        payload = selected.read_bytes()
    except OSError as exc:
        raise LicenseResourceError(f"The complete LICENSE file could not be read: {selected}") from exc
    digest = hashlib.sha256(payload).hexdigest()
    if digest != GPL_V3_SHA256:
        raise LicenseResourceError(
            f"The LICENSE file failed its integrity check: expected {GPL_V3_SHA256}, got {digest}"
        )
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise LicenseResourceError("The LICENSE file is not valid UTF-8 text") from exc
    missing = [marker for marker in REQUIRED_GPL_MARKERS if marker not in text]
    if missing:
        raise LicenseResourceError(f"The LICENSE file is incomplete; missing: {', '.join(missing)}")
    return LicenseDocument(path=selected, text=text, sha256=digest)


def license_intro(display_version: str = __display_version__) -> str:
    return (
        f"AudioShifter {display_version}\n"
        "Copyright (C) 2026 Yeming Dai\n\n"
        "AudioShifter-owned code covered by this release is licensed under\n"
        "the GNU General Public License version 3 or any later version.\n\n"
        "The complete GNU GPL version 3 text follows."
    )


def complete_window_text(document: LicenseDocument) -> str:
    """Compose the English introduction followed by the unmodified GPL text."""

    return f"{license_intro()}\n\n{document.text}"


class LicenseWindowController:
    """Own a single non-modal, reusable licence viewer for the application."""

    def __init__(
        self,
        root: tk.Misc,
        *,
        document_loader: Callable[[], LicenseDocument] = load_license_document,
    ) -> None:
        self.root = root
        self._document_loader = document_loader
        self.window: tk.Toplevel | None = None
        self.text_widget: tk.Text | None = None

    def show(self) -> tk.Toplevel | None:
        if self.window is not None and self.window.winfo_exists():
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
            return self.window
        try:
            document = self._document_loader()
        except LicenseResourceError as exc:
            messagebox.showerror(
                "License unavailable",
                "The complete licence text could not be loaded from the application resources.\n\n"
                f"{exc}",
                parent=self.root,
            )
            return None

        window = tk.Toplevel(self.root)
        window.title("AudioShifter License")
        window.geometry("760x620")
        window.minsize(560, 420)
        window.resizable(True, True)
        window.protocol("WM_DELETE_WINDOW", self.close)
        window.bind("<Command-w>", self._close_event)

        frame = ttk.Frame(window, padding=14)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        text = tk.Text(
            frame,
            wrap=tk.WORD,
            font="TkFixedFont",
            padx=10,
            pady=10,
            undo=False,
            yscrollcommand=scrollbar.set,
        )
        scrollbar.configure(command=text.yview)
        text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        text.insert("1.0", complete_window_text(document))
        text.configure(state=tk.DISABLED)
        text.bind("<Command-c>", self._copy_event)

        close_button = ttk.Button(frame, text="Close", command=self.close)
        close_button.grid(row=1, column=0, columnspan=2, pady=(12, 0))

        window.bind("<Destroy>", self._destroyed, add=True)
        self.window = window
        self.text_widget = text
        text.focus_set()
        return window

    def close(self) -> None:
        window = self.window
        if window is not None and window.winfo_exists():
            window.destroy()
        self.window = None
        self.text_widget = None

    def _close_event(self, _event: tk.Event[tk.Misc]) -> str:
        self.close()
        return "break"

    @staticmethod
    def _copy_event(event: tk.Event[tk.Text]) -> str:
        event.widget.event_generate("<<Copy>>")
        return "break"

    def _destroyed(self, event: tk.Event[tk.Misc]) -> None:
        if self.window is not None and event.widget is self.window:
            self.window = None
            self.text_widget = None
