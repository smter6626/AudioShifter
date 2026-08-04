import tkinter as tk

import pytest

from audioshifter.gui import AudioShifterView


@pytest.mark.integration
def test_GUI_T001_T002_T012_window_creates_updates_and_destroys() -> None:
    root = tk.Tk()
    root.withdraw()
    try:
        view = AudioShifterView(root)
        root.update_idletasks()
        assert "AudioShifter" in root.title()
        assert view.pitch.get() == "0"
        assert view.speed.get() == "0"
        assert "就绪" in view.status.get()
        view.set_running(True)
        root.update_idletasks()
        assert str(view.start_button["state"]) == tk.DISABLED
        assert str(view.cancel_button["state"]) == tk.NORMAL
        view.set_running(False)
        root.update_idletasks()
        assert str(view.start_button["state"]) == tk.NORMAL
    finally:
        root.destroy()
