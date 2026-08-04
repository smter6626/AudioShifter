"""Chinese Tkinter interface for the macOS runnable MVP."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .controller import ApplicationController
from .errors import AppError
from .models import OutputAllocation, ProcessingResult


class AudioShifterView:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.controller: ApplicationController | None = None
        self.input_path = tk.StringVar(value="")
        self.pitch = tk.StringVar(value="0")
        self.speed = tk.StringVar(value="0")
        self.status = tk.StringVar(value="就绪：请选择音频文件。")

        root.title("AudioShifter 音频变调变速")
        root.geometry("760x430")
        root.minsize(680, 400)
        self._build_widgets()

    def attach_controller(self, controller: ApplicationController) -> None:
        self.controller = controller
        self.root.protocol("WM_DELETE_WINDOW", controller.request_close)

    def _build_widgets(self) -> None:
        container = ttk.Frame(self.root, padding=24)
        container.pack(fill=tk.BOTH, expand=True)
        container.columnconfigure(1, weight=1)

        title = ttk.Label(container, text="AudioShifter", font=("Helvetica Neue", 24, "bold"))
        title.grid(row=0, column=0, columnspan=3, sticky="w")
        subtitle = ttk.Label(
            container,
            text="在本机完成音频变调与变速；源文件不会被修改。",
        )
        subtitle.grid(row=1, column=0, columnspan=3, sticky="w", pady=(2, 20))

        ttk.Label(container, text="输入音频").grid(row=2, column=0, sticky="w", padx=(0, 12))
        self.path_entry = ttk.Entry(container, textvariable=self.input_path, state="readonly")
        self.path_entry.grid(row=2, column=1, sticky="ew")
        self.choose_button = ttk.Button(container, text="选择文件…", command=self.choose_file)
        self.choose_button.grid(row=2, column=2, padx=(12, 0))

        ttk.Label(container, text="变调（半音）").grid(row=3, column=0, sticky="w", pady=(18, 0))
        self.pitch_entry = ttk.Entry(container, textvariable=self.pitch, width=14)
        self.pitch_entry.grid(row=3, column=1, sticky="w", pady=(18, 0))
        ttk.Label(container, text="整数范围：-24 至 +24；0 表示保持原调").grid(
            row=4, column=1, columnspan=2, sticky="w", pady=(4, 0)
        )

        ttk.Label(container, text="变速（相对变化）").grid(row=5, column=0, sticky="w", pady=(18, 0))
        self.speed_entry = ttk.Entry(container, textvariable=self.speed, width=14)
        self.speed_entry.grid(row=5, column=1, sticky="w", pady=(18, 0))
        ttk.Label(
            container,
            text="范围：-95 至 +400；非零值请写正负号，无需输入 %（例如 -20）",
        ).grid(row=6, column=1, columnspan=2, sticky="w", pady=(4, 0))

        actions = ttk.Frame(container)
        actions.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(26, 18))
        self.start_button = ttk.Button(actions, text="开始处理", command=self.start_processing)
        self.start_button.pack(side=tk.LEFT)
        self.cancel_button = ttk.Button(
            actions, text="取消", command=self.cancel_processing, state=tk.DISABLED
        )
        self.cancel_button.pack(side=tk.LEFT, padx=(12, 0))

        separator = ttk.Separator(container)
        separator.grid(row=8, column=0, columnspan=3, sticky="ew", pady=(0, 14))
        ttk.Label(container, text="当前状态", font=("Helvetica Neue", 12, "bold")).grid(
            row=9, column=0, sticky="nw", padx=(0, 12)
        )
        ttk.Label(container, textvariable=self.status, wraplength=540).grid(
            row=9, column=1, columnspan=2, sticky="w"
        )
        ttk.Label(
            container,
            text="结果固定保存到当前用户的 Downloads，格式为 320 kbps / 44.1 kHz / 双声道 MP3。",
            foreground="#555555",
            wraplength=700,
        ).grid(row=10, column=0, columnspan=3, sticky="w", pady=(24, 0))

    def choose_file(self) -> None:
        selected = filedialog.askopenfilename(
            title="选择音频文件",
            filetypes=[
                ("支持的音频", "*.mp3 *.MP3 *.m4a *.M4A *.wav *.WAV *.flac *.FLAC"),
                ("MP3 音频", "*.mp3 *.MP3"),
                ("M4A 音频", "*.m4a *.M4A"),
                ("WAV 音频", "*.wav *.WAV"),
                ("FLAC 音频", "*.flac *.FLAC"),
            ],
        )
        if selected:
            self.input_path.set(selected)
            self.status.set("已选择音频，可以设置参数并开始处理。")

    def start_processing(self) -> None:
        if self.controller is not None:
            self.controller.start(self.input_path.get(), self.pitch.get(), self.speed.get())

    def cancel_processing(self) -> None:
        if self.controller is not None:
            self.controller.cancel()

    def set_running(self, running: bool) -> None:
        self.start_button.configure(state=tk.DISABLED if running else tk.NORMAL)
        self.choose_button.configure(state=tk.DISABLED if running else tk.NORMAL)
        self.cancel_button.configure(state=tk.NORMAL if running else tk.DISABLED)

    def set_status(self, message: str) -> None:
        self.status.set(message)

    def confirm_output_conflict(self, allocation: OutputAllocation) -> bool:
        return messagebox.askokcancel(
            "输出文件已存在",
            "原目标文件已经存在，已有文件不会被覆盖。\n\n"
            f"本次将改用：\n{allocation.output_path}\n\n是否继续？",
            icon=messagebox.INFO,
            parent=self.root,
        )

    def show_success(self, result: ProcessingResult) -> None:
        warning = ""
        if result.warnings:
            warning = "\n\n注意：" + "；".join(result.warnings)
        messagebox.showinfo(
            "处理完成",
            f"音频已保存到：\n{result.output_path}{warning}",
            parent=self.root,
        )

    def show_error(self, error: AppError) -> None:
        path = error.details.get("path") if error.details else None
        suffix = f"\n\n相关路径：\n{path}" if path else ""
        messagebox.showerror("无法完成处理", f"{error.user_message}{suffix}", parent=self.root)

    def show_cancelled(self) -> None:
        messagebox.showinfo("已取消", "处理已取消，未保留残缺输出。", parent=self.root)

    def show_already_running(self) -> None:
        messagebox.showinfo("正在处理", "当前已有任务，请等待完成或先取消。", parent=self.root)

    def confirm_exit_running(self) -> bool:
        return messagebox.askyesno(
            "取消任务并退出？",
            "音频仍在处理中。是否取消当前任务、清理临时文件并退出？",
            parent=self.root,
        )


def create_application(root: tk.Tk | None = None) -> tuple[tk.Tk, AudioShifterView, ApplicationController]:
    application_root = root or tk.Tk()
    view = AudioShifterView(application_root)
    controller = ApplicationController(application_root, view)
    view.attach_controller(controller)
    return application_root, view, controller


def run() -> None:
    root, _, _ = create_application()
    root.mainloop()
