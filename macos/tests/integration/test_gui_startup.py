import tkinter as tk

import pytest

from audioshifter.gui import AudioShifterView


@pytest.mark.integration
def test_GUI_T001_T002_T012_window_creates_updates_and_destroys(monkeypatch) -> None:
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
        focused = []
        monkeypatch.setattr(view.pitch_entry, "focus_set", lambda: focused.append(True))
        monkeypatch.setattr(
            "audioshifter.gui.filedialog.askopenfilename", lambda **kwargs: "/tmp/source.wav"
        )
        view.choose_file()
        assert focused == [True]
        assert view.input_path.get() == "/tmp/source.wav"
    finally:
        root.destroy()
