import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading
import shutil
import sys
import hashlib
import winreg  # <--- 新增这行！用于读取注册表

# ==========================================
#           核心配置 (必须与注册机一致)
# ==========================================
# 这个盐值是验证的关键，必须和你的 admin_keygen.py 里的一样
SECRET_SALT = "AudioShifter_2025_My_Secret_Salt_$$$" 

# ==========================================
#           1. 激活验证模块 (机器码逻辑)
# ==========================================
def get_machine_code():
    """
    获取本机机器码
    方案：优先读取 Windows 注册表 MachineGuid (最稳定，无需管理员权限)
    备选：如果失败，尝试读取主板 UUID
    """
    # 方案 A: 注册表 MachineGuid
    try:
        # 打开注册表路径: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Cryptography", 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        value, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
        return value.strip()
    except Exception as e:
        print(f"DEBUG: 注册表读取失败: {e}")
    
    # 方案 B: 主板 UUID (备选)
    try:
        cmd = "wmic csproduct get uuid"
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        output = subprocess.check_output(cmd, shell=True, startupinfo=startupinfo).decode()
        # 更加稳健的解析方式：找非空的最后一行
        lines = [line.strip() for line in output.split('\n') if line.strip()]
        if len(lines) > 1:
             # lines[0] 是标题 "UUID"，lines[1] 是值
            return lines[1]
    except Exception as e:
        print(f"DEBUG: WMIC读取失败: {e}")

    # 如果都失败了
    return "UNKNOWN-DEVICE-ID"

def verify_key(user_key):
    """验证逻辑：软件自己在心里算一遍，看对不对"""
    machine_code = get_machine_code()
    
    # --- 核心算法 (和注册机一模一样) ---
    raw_str = str(machine_code).strip() + SECRET_SALT
    sha_signature = hashlib.sha256(raw_str.encode()).hexdigest().upper()
    true_key_raw = sha_signature[:16]
    expected_key = '-'.join([true_key_raw[i:i+4] for i in range(0, len(true_key_raw), 4)])
    # --------------------------------
    
    return user_key.strip() == expected_key

def check_activation_startup():
    """启动检查：没激活就弹窗，死循环直到激活"""
    license_file = resource_path("license.dat") # 优先存放在运行目录
    
    # 为了防止打包后无法写入，我们在 exe 所在目录存文件
    # sys.executable 是 exe 的路径，os.getcwd() 也可以
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    license_path = os.path.join(exe_dir, "license.dat")

    # 1. 自动静默检查
    if os.path.exists(license_path):
        try:
            with open(license_path, "r") as f:
                saved_key = f.read().strip()
            if verify_key(saved_key):
                return True # 已激活
        except:
            pass

    # 2. 弹出激活窗口
    machine_code = get_machine_code()
    
    # 创建一个简单的激活窗口
    auth_win = tk.Tk()
    auth_win.title("需要激活")
    auth_win.geometry("450x300")
    
    # 居中显示
    screen_width = auth_win.winfo_screenwidth()
    screen_height = auth_win.winfo_screenheight()
    x = (screen_width - 450) // 2
    y = (screen_height - 300) // 2
    auth_win.geometry(f"450x300+{x}+{y}")

    is_success = [False] # 闭包状态

    tk.Label(auth_win, text="🔒 软件未激活", font=("Arial", 16, "bold"), pady=10).pack()
    tk.Label(auth_win, text="请复制下方机器码，发送给管理员获取激活码:", fg="#555").pack()
    
    entry_mc = tk.Entry(auth_win, width=40, font=("Arial", 10), justify="center", bg="#f0f0f0")
    entry_mc.insert(0, machine_code)
    entry_mc.config(state="readonly")
    entry_mc.pack(pady=5)
    
    tk.Label(auth_win, text="输入激活码:", pady=5).pack()
    entry_key = tk.Entry(auth_win, width=40, font=("Arial", 12), justify="center")
    entry_key.pack(pady=5)
    
    def on_confirm():
        k = entry_key.get().strip()
        if verify_key(k):
            try:
                with open(license_path, "w") as f:
                    f.write(k)
                messagebox.showinfo("成功", "激活成功！\n请点击确定进入软件。")
                is_success[0] = True
                auth_win.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"无法写入授权文件:\n{e}\n请尝试以管理员身份运行。")
        else:
            messagebox.showerror("失败", "激活码错误！\n请检查是否对应本机机器码。")

    tk.Button(auth_win, text="激活解锁", command=on_confirm, bg="#0078D7", fg="white", font=("bold"), width=15).pack(pady=20)
    
    # 拦截关闭窗口事件：如果不激活，直接退出整个程序
    def on_close():
        auth_win.destroy()
        sys.exit(0)
        
    auth_win.protocol("WM_DELETE_WINDOW", on_close)
    auth_win.mainloop()
    
    return is_success[0]

# ==========================================
#           2. 资源路径与依赖 (原逻辑)
# ==========================================
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

FFMPEG_BIN = "ffmpeg.exe" if os.name == 'nt' else "ffmpeg"
RUBBERBAND_BIN = "rubberband.exe" if os.name == 'nt' else "rubberband"
SNDFILE_BIN = "sndfile.dll" if os.name == 'nt' else "sndfile.dll" # 确保打包时包含

def check_dependencies():
    # 简单检查，防止文件丢失
    missing = []
    if not os.path.exists(resource_path(FFMPEG_BIN)): missing.append(FFMPEG_BIN)
    if not os.path.exists(resource_path(RUBBERBAND_BIN)): missing.append(RUBBERBAND_BIN)
    # sndfile.dll 是 rubberband 的依赖，通常不直接调用，但也得在
    return missing

# ==========================================
#           3. 音频处理逻辑 (原逻辑)
# ==========================================
def process_audio_rubberband(input_path, n_steps, speed_percent, status_label, run_btn):
    home_dir = os.path.expanduser("~")
    downloads_dir = os.path.join(home_dir, "Downloads")
    temp_wav_in = os.path.join(downloads_dir, "temp_rb_process_in.wav")
    temp_wav_out = os.path.join(downloads_dir, "temp_rb_process_out.wav")
    
    cmd_ffmpeg = resource_path(FFMPEG_BIN)
    cmd_rubberband = resource_path(RUBBERBAND_BIN)

    try:
        status_label.config(text="⏳ 正在预处理音频...")
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        # 1. 解码
        subprocess.run([cmd_ffmpeg, "-y", "-i", input_path, "-ac", "2", "-ar", "44100", temp_wav_in], 
                       capture_output=True, startupinfo=startupinfo, check=True)

        # 2. 变调
        status_label.config(text=f"🎹 正在处理...")
        tempo_ratio = speed_percent / 100.0
        subprocess.run([cmd_rb := cmd_rubberband, "-p", str(n_steps), "-T", str(tempo_ratio), "--fine", "--formant", temp_wav_in, temp_wav_out],
                       capture_output=True, startupinfo=startupinfo, check=True)

        # 3. 编码
        status_label.config(text="💾 封装 MP3...")
        input_dir = os.path.dirname(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        pitch_sign = "+" if n_steps >= 0 else "" 
        output_path = os.path.join(input_dir, f"{base_name}_{int(speed_percent)}%{pitch_sign}{n_steps}.mp3")
        
        subprocess.run([cmd_ffmpeg, "-y", "-i", temp_wav_out, "-b:a", "320k", "-f", "mp3", output_path],
                       capture_output=True, startupinfo=startupinfo, check=True)

        status_label.config(text="✅ 完成！")
        messagebox.showinfo("成功", f"文件已保存到:\n{output_path}")

    except Exception as e:
        status_label.config(text="❌ 失败")
        messagebox.showerror("错误", str(e))
    finally:
        if os.path.exists(temp_wav_in): os.remove(temp_wav_in)
        if os.path.exists(temp_wav_out): os.remove(temp_wav_out)
        run_btn.config(state="normal")

def start_thread():
    missing = check_dependencies()
    if missing:
        messagebox.showerror("缺少文件", f"程序内部丢失: {', '.join(missing)}")
        return
    
    input_path = entry_path.get()
    if not input_path: return messagebox.showwarning("提示", "请选择文件")
    
    try:
        n_steps = float(entry_steps.get())
        speed = float(entry_speed.get())
        if not (0 < speed < 1000): raise ValueError
    except:
        return messagebox.showerror("错误", "参数输入有误")

    btn_run.config(state="disabled")
    threading.Thread(target=process_audio_rubberband, 
                     args=(input_path, n_steps, speed, lbl_status, btn_run)).start()

def select_file():
    f = filedialog.askopenfilename(filetypes=[("Audio", "*.mp3 *.wav *.m4a *.flac")])
    if f:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, f)

# ==========================================
#           4. 主程序入口
# ==========================================
if __name__ == "__main__":
    # --- 第一步：先检查激活 ---
    # 如果这里返回 False，程序会直接结束，不会显示主界面
    if check_activation_startup():
        
        # --- 第二步：显示主界面 ---
        root = tk.Tk()
        root.title("MyAudioShifter (已激活)")
        root.geometry("450x550")
        root.configure(bg="#333")

        tk.Label(root, text="MyAudioShifter Pro", font=("Arial", 20, "bold"), fg="white", bg="#333", pady=15).pack()
        
        frame_file = tk.LabelFrame(root, text="1. 选择音频", bg="#333", fg="white"); frame_file.pack(padx=20, fill="x")
        entry_path = tk.Entry(frame_file, width=30); entry_path.pack(side="left", fill="x", expand=True)
        tk.Button(frame_file, text="浏览", command=select_file).pack(side="right")

        frame_pitch = tk.LabelFrame(root, text="2. 变调", bg="#333", fg="white"); frame_pitch.pack(padx=20, fill="x", pady=10)
        tk.Label(frame_pitch, text="半音 (0.0):", bg="#333", fg="white").pack()
        entry_steps = tk.Entry(frame_pitch); entry_steps.insert(0, "0"); entry_steps.pack()

        frame_speed = tk.LabelFrame(root, text="3. 变速", bg="#333", fg="white"); frame_speed.pack(padx=20, fill="x")
        tk.Label(frame_speed, text="百分比 (100):", bg="#333", fg="white").pack()
        entry_speed = tk.Entry(frame_speed); entry_speed.insert(0, "100"); entry_speed.pack()

        btn_run = tk.Button(root, text="开始处理", command=start_thread, bg="#6200EA", fg="white", height=2)
        btn_run.pack(padx=20, pady=20, fill="x")
        
        lbl_status = tk.Label(root, text="就绪", bg="#333", fg="white"); lbl_status.pack()

        root.mainloop()