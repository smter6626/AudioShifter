# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai
from __future__ import annotations

import re
import tkinter as tk
from tkinter import ttk

import pytest

from audioshifter.gui import AudioShifterView
from audioshifter.legal import LicenseWindowController, load_license_document
from audioshifter.macos_menu import (
    APPLICATION_MENU_LABEL,
    LICENSE_MENU_LABEL,
    install_application_menu,
)


def descendant_button_labels(widget: tk.Misc) -> list[str]:
    labels: list[str] = []
    for child in widget.winfo_children():
        if isinstance(child, ttk.Button):
            labels.append(str(child.cget("text")))
        labels.extend(descendant_button_labels(child))
    return labels


@pytest.mark.integration
def test_LEGAL_UI_T001_complete_readonly_scrollable_copyable_english_window() -> None:
    root = tk.Tk()
    root.withdraw()
    controller = LicenseWindowController(root)
    try:
        window = controller.show()
        root.update_idletasks()
        assert window is not None
        assert window.title() == "AudioShifter License"
        assert tuple(bool(value) for value in window.resizable()) == (True, True)
        text = controller.text_widget
        assert text is not None
        rendered = text.get("1.0", "end-1c")
        document = load_license_document()
        assert rendered.endswith(document.text)
        assert "AudioShifter 0.1.0-alpha.3" in rendered
        assert not re.search(r"[\u3400-\u9fff]", rendered)
        assert str(text.cget("state")) == tk.DISABLED
        assert str(text.cget("yscrollcommand"))
        assert text.bind("<Command-c>")
        assert window.bind("<Command-w>")
        text.tag_add(tk.SEL, "1.0", "1.12")
        assert text.tag_ranges(tk.SEL)
    finally:
        controller.close()
        root.destroy()


@pytest.mark.integration
def test_LEGAL_UI_T002_window_is_singleton_then_reopens_after_close() -> None:
    root = tk.Tk()
    root.withdraw()
    controller = LicenseWindowController(root)
    try:
        first = controller.show()
        second = controller.show()
        assert first is not None and second is first
        controller.close()
        root.update_idletasks()
        assert controller.window is None
        reopened = controller.show()
        assert reopened is not None and reopened is not first
    finally:
        controller.close()
        root.destroy()


@pytest.mark.integration
def test_LEGAL_UI_T003_native_aqua_application_menu_has_exact_license_item() -> None:
    root = tk.Tk()
    root.withdraw()
    calls: list[str] = []
    try:
        registration = install_application_menu(root, lambda: calls.append("License"))
        assert registration.windowing_system == "aqua"
        assert registration.installed
        assert registration.menubar_path == ".menubar"
        assert registration.application_menu_path == ".menubar.apple"
        menubar: tk.Menu = root._audioshifter_menubar  # type: ignore[attr-defined]
        application_menu: tk.Menu = root._audioshifter_application_menu  # type: ignore[attr-defined]
        assert menubar.entrycget(0, "label") == APPLICATION_MENU_LABEL
        assert menubar.entrycget(0, "menu") == ".menubar.apple"
        assert application_menu.entrycget(0, "label") == LICENSE_MENU_LABEL
        assert [menubar.entrycget(index, "label") for index in range(menubar.index("end") + 1)] == [
            "AudioShifter"
        ]
        application_menu.invoke(0)
        assert calls == ["License"]
    finally:
        root.destroy()


@pytest.mark.integration
def test_LEGAL_UI_T004_main_gui_has_no_license_button_file_or_help_menu() -> None:
    root = tk.Tk()
    root.withdraw()
    try:
        view = AudioShifterView(root)
        root.update_idletasks()
        assert "License" not in descendant_button_labels(root)
        assert view.application_menu.application_menu_path == ".menubar.apple"
        menubar: tk.Menu = root._audioshifter_menubar  # type: ignore[attr-defined]
        labels = [menubar.entrycget(index, "label") for index in range(menubar.index("end") + 1)]
        assert labels == ["AudioShifter"]
        assert "File" not in labels
        assert "Help" not in labels
    finally:
        root.destroy()
