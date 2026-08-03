import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading
import shutil
import sys
import hashlib
import winreg

# ==========================================
#           Core Configuration
# ==========================================
SECRET_SALT = "AudioShifter_2025_My_Secret_Salt_$$$"

# ==========================================
#           1. Activation Module
# ==========================================
def get_machine_code():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            "SOFTWARE\\Microsoft\\Cryptography",
            0,
            winreg.KEY_READ | winreg.KEY_WOW64_64KEY
        )
        value, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
        return value.strip()
    except Exception as e:
        print(f"DEBUG: Registry read failed: {e}")

    try:
        cmd = "wmic csproduct get uuid"
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        output = subprocess.check_output(cmd, shell=True, startupinfo=startupinfo).decode()
        lines = [line.strip() for line in output.split('\n') if line.strip()]
        if len(lines) > 1:
            return lines[1]
    except Exception as e:
        print(f"DEBUG: WMIC read failed: {e}")

    return "UNKNOWN-DEVICE-ID"

def verify_key(user_key):
    machine_code = get_machine_code()
    raw_str = str(machine_code).strip() + SECRET_SALT
    sha_signature = hashlib.sha256(raw_str.encode()).hexdigest().upper()
    true_key_raw = sha_signature[:16]
    expected_key = '-'.join([true_key_raw[i:i+4] for i in range(0, len(true_key_raw), 4)])
    return user_key.strip() == expected_key

def check_activation_startup():
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    license_path = os.path.join(exe_dir, "license.dat")

    if os.path.exists(license_path):
        try:
            with open(license_path, "r") as f:
                saved_key = f.read().strip()
            if verify_key(saved_key):
                return True
        except:
            pass

    machine_code = get_machine_code()

    auth_win = tk.Tk()
    auth_win.title("Activation Required")
    auth_win.geometry("450x300")

    screen_width = auth_win.winfo_screenwidth()
    screen_height = auth_win.winfo_screenheight()
    x = (screen_width - 450) // 2
    y = (screen_height - 300) // 2
    auth_win.geometry(f"450x300+{x}+{y}")

    is_success = [False]

    tk.Label(auth_win, text="🔒 Software Not Activated", font=("Arial", 16, "bold"), pady=10).pack()
    tk.Label(auth_win, text="Copy the machine code below and send it to the administrator to obtain an activation key:", fg="#555").pack()

    entry_mc = tk.Entry(auth_win, width=40, font=("Arial", 10), justify="center", bg="#f0f0f0")
    entry_mc.insert(0, machine_code)
    entry_mc.config(state="readonly")
    entry_mc.pack(pady=5)

    tk.Label(auth_win, text="Enter Activation Key:", pady=5).pack()
    entry_key = tk.Entry(auth_win, width=40, font=("Arial", 12), justify="center")
    entry_key.pack(pady=5)

    def on_confirm():
        k = entry_key.get().strip()
        if verify_key(k):
            try:
                with open(license_path, "w") as f:
                    f.write(k)
                messagebox.showinfo("Success", "Activation successful!\nClick OK to continue.")
                is_success[0] = True
                auth_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Unable to write license file:\n{e}\nPlease try running as administrator.")
        else:
            messagebox.showerror("Failure", "Invalid activation key!\nPlease verify it matches your machine code.")

    tk.Button(auth_win, text="Activate", command=on_confirm, bg="#0078D7", fg="white", font=("bold"), width=15).pack(pady=20)

    def on_close():
        auth_win.destroy()
        sys.exit(0)

    auth_win.protocol("WM_DELETE_WINDOW", on_close)
    auth_win.mainloop()

    return is_success[0]

# ==========================================
#           2. Resource Paths
# ==========================================
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

FFMPEG_BIN = "ffmpeg.exe" if os.name == 'nt' else "ffmpeg"
RUBBERBAND_BIN = "rubberband.exe" if os.name == 'nt' else "rubberband"
SNDFILE_BIN = "sndfile.dll" if os.name == 'nt' else "sndfile.dll"

def check_dependencies():
    missing = []
    if not os.path.exists(resource_path(FFMPEG_BIN)): missing.append(FFMPEG_BIN)
    if not os.path.exists(resource_path(RUBBERBAND_BIN)): missing.append(RUBBERBAND_BIN)
    return missing

# ==========================================
#           3. Audio Processing
# ==========================================
def process_audio_rubberband(input_path, n_steps, speed_percent, status_label, run_btn):
    home_dir = os.path.expanduser("~")
    downloads_dir = os.path.join(home_dir, "Downloads")
    temp_wav_in = os.path.join(downloads_dir, "temp_rb_process_in.wav")
    temp_wav_out = os.path.join(downloads_dir, "temp_rb_process_out.wav")

    cmd_ffmpeg = resource_path(FFMPEG_BIN)
    cmd_rubberband = resource_path(RUBBERBAND_BIN)

    try:
        status_label.config(text="⏳ Preprocessing audio...")
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        subprocess.run([cmd_ffmpeg, "-y", "-i", input_path, "-ac", "2", "-ar", "44100", temp_wav_in],
                       capture_output=True, startupinfo=startupinfo, check=True)

        status_label.config(text="🎹 Processing...")
        tempo_ratio = speed_percent / 100.0
        subprocess.run([cmd_rubberband, "-p", str(n_steps), "-T", str(tempo_ratio), "--fine", "--formant", temp_wav_in, temp_wav_out],
                       capture_output=True, startupinfo=startupinfo, check=True)

        status_label.config(text="💾 Exporting MP3...")
        input_dir = os.path.dirname(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        pitch_sign = "+" if n_steps >= 0 else ""
        output_path = os.path.join(input_dir, f"{base_name}_{int(speed_percent)}%{pitch_sign}{n_steps}.mp3")

        subprocess.run([cmd_ffmpeg, "-y", "-i", temp_wav_out, "-b:a", "320k", "-f", "mp3", output_path],
                       capture_output=True, startupinfo=startupinfo, check=True)

        status_label.config(text="✅ Completed!")
        messagebox.showinfo("Success", f"File saved to:\n{output_path}")

    except Exception as e:
        status_label.config(text="❌ Failed")
        messagebox.showerror("Error", str(e))
    finally:
        if os.path.exists(temp_wav_in): os.remove(temp_wav_in)
        if os.path.exists(temp_wav_out): os.remove(temp_wav_out)
        run_btn.config(state="normal")

def start_thread():
    missing = check_dependencies()
    if missing:
        messagebox.showerror("Missing Files", f"Missing internal files: {', '.join(missing)}")
        return

    input_path = entry_path.get()
    if not input_path:
        return messagebox.showwarning("Warning", "Please select a file.")

    try:
        n_steps = float(entry_steps.get())
        speed = float(entry_speed.get())
        if not (0 < speed < 1000): raise ValueError
    except:
        return messagebox.showerror("Error", "Invalid parameter input.")

    btn_run.config(state="disabled")
    threading.Thread(target=process_audio_rubberband,
                     args=(input_path, n_steps, speed, lbl_status, btn_run)).start()

def select_file():
    f = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.m4a *.flac")])
    if f:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, f)

# ==========================================
#           4. Main Program
# ==========================================
if __name__ == "__main__":
    if check_activation_startup():

        root = tk.Tk()
        root.title("MyAudioShifter (Activated)")
        root.geometry("450x550")
        root.configure(bg="#333")

        tk.Label(root, text="MyAudioShifter Pro", font=("Arial", 20, "bold"), fg="white", bg="#333", pady=15).pack()

        frame_file = tk.LabelFrame(root, text="1. Select Audio File", bg="#333", fg="white")
        frame_file.pack(padx=20, fill="x")
        entry_path = tk.Entry(frame_file, width=30)
        entry_path.pack(side="left", fill="x", expand=True)
        tk.Button(frame_file, text="Browse", command=select_file).pack(side="right")

        frame_pitch = tk.LabelFrame(root, text="2. Pitch Shift", bg="#333", fg="white")
        frame_pitch.pack(padx=20, fill="x", pady=10)
        tk.Label(frame_pitch, text="Semitones (0.0):", bg="#333", fg="white").pack()
        entry_steps = tk.Entry(frame_pitch)
        entry_steps.insert(0, "0")
        entry_steps.pack()

        frame_speed = tk.LabelFrame(root, text="3. Tempo Adjustment", bg="#333", fg="white")
        frame_speed.pack(padx=20, fill="x")
        tk.Label(frame_speed, text="Percentage (100):", bg="#333", fg="white").pack()
        entry_speed = tk.Entry(frame_speed)
        entry_speed.insert(0, "100")
        entry_speed.pack()

        btn_run = tk.Button(root, text="Start Processing", command=start_thread, bg="#6200EA", fg="white", height=2)
        btn_run.pack(padx=20, pady=20, fill="x")

        lbl_status = tk.Label(root, text="Ready", bg="#333", fg="white")
        lbl_status.pack()

        root.mainloop()