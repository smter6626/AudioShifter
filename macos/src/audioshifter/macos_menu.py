# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai
"""Install AudioShifter commands in Tk's native macOS application menu."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from typing import Callable


APPLICATION_MENU_LABEL = "AudioShifter"
LICENSE_MENU_LABEL = "License"


@dataclass(frozen=True, slots=True)
class ApplicationMenuRegistration:
    windowing_system: str
    installed: bool
    menubar_path: str | None = None
    application_menu_path: str | None = None


def install_application_menu(
    root: tk.Tk,
    on_license: Callable[[], object],
) -> ApplicationMenuRegistration:
    """Install .menubar.apple before attaching it, as required by Tk Aqua."""

    windowing_system = str(root.tk.call("tk", "windowingsystem"))
    if windowing_system != "aqua":
        return ApplicationMenuRegistration(windowing_system=windowing_system, installed=False)

    menubar = tk.Menu(root, name="menubar", tearoff=False)
    application_menu = tk.Menu(menubar, name="apple", tearoff=False)
    application_menu.add_command(label=LICENSE_MENU_LABEL, command=on_license)
    menubar.add_cascade(label=APPLICATION_MENU_LABEL, menu=application_menu)
    root.configure(menu=menubar)

    # Keep Python objects alive and make the exact native menu structure inspectable.
    root._audioshifter_menubar = menubar  # type: ignore[attr-defined]
    root._audioshifter_application_menu = application_menu  # type: ignore[attr-defined]
    return ApplicationMenuRegistration(
        windowing_system=windowing_system,
        installed=True,
        menubar_path=str(menubar),
        application_menu_path=str(application_menu),
    )
