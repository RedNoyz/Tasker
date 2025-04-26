import tkinter as tk
from tkinter import ttk, messagebox
import requests
import subprocess
import os
import threading
import sv_ttk
import psutil
import sys

GITHUB_API_RELEASES_URL = "https://api.github.com/repos/RedNoyz/Tasker/releases/latest"
DOWNLOAD_URL = "https://github.com/RedNoyz/Tasker/releases/latest/download/Tasker.exe"
LOCAL_EXE = "Tasker.exe"

stop_event = threading.Event()
threads = []

def get_asset_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def is_tasker_running():
    for process in psutil.process_iter(['name']):
        if process.info['name'] == "Tasker.exe":
            return True
    return False

def launch_and_exit():
    try:
        subprocess.Popen([LOCAL_EXE])
    finally:
        root.quit()
        sys.exit() 

def show_success_and_exit():
    messagebox.showinfo("Update Complete", "Tasker has been updated successfully.")
    root.after(0, launch_and_exit)

def get_local_version():
    try:
        result = subprocess.run([LOCAL_EXE, "--version"], capture_output=True, text=True, timeout=3)
        return result.stdout.strip()
    except Exception:
        return "0.0.0"

def get_remote_version():
    try:
        response = requests.get(GITHUB_API_RELEASES_URL, timeout=5)
        data = response.json()
        return data["tag_name"].lstrip("v")
    except Exception:
        return None

def download_file(url, target_file, progress_callback):
    temp_target_file = target_file + ".tmp"

    if os.path.exists(temp_target_file):
        try:
            os.remove(temp_target_file)
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not delete the old temp file {temp_target_file}: {e}")

    with requests.get(url, stream=True) as open_request:
        open_request.raise_for_status()
        total = int(open_request.headers.get('content-length', 0))
        with open(temp_target_file, 'wb') as file:
            downloaded = 0
            for chunk in open_request.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    percent = int((downloaded / total) * 100)
                    progress_callback(percent)
    try:
        if is_tasker_running():
            root.after(0, lambda: messagebox.showwarning("Close Tasker", "Please close Tasker.exe before updating."))
            return
        os.replace(temp_target_file, target_file)
    except Exception as e:
        messagebox.showwarning(f"Could not replace the old version: {e}")

def update_progress(value):
    progress["value"] = value
    root.update_idletasks()

def start_download():
    def task():
        try:
            if is_tasker_running():
                root.after(0, lambda: messagebox.showwarning("Close Tasker", "Please close Tasker.exe before updating."))
                return

            download_file(DOWNLOAD_URL, LOCAL_EXE, update_progress)

            root.after(0, show_success_and_exit)

        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Error", f"Update failed: {e}"))

    download_thread = threading.Thread(target=task)
    download_thread.daemon = True
    download_thread.start()
    threads.append(download_thread)

def compare_versions(local, remote):
    def version_tuple(v):
        return tuple(map(int, (v.split("."))))
    return version_tuple(local) < version_tuple(remote)

def full_exit():
    root.destroy()
    root.quit()
    sys.exit()

def exit_updater():
    label.config(text="Update Canceled! Closing Updater!")
    print("Exiting app...")
    
    stop_event.set()
    for thread in threads:
        thread.join(timeout=2)
    
    temp_file = LOCAL_EXE + ".tml"
    if os.path.exists(temp_file):
        try:
            os.remove(temp_file)
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not delete the old temp file {temp_file}: {e}")
    
    root.after(500, full_exit)



root = tk.Tk()
root.title("Tasker Updater")
root.geometry("300x120")
root.resizable(False, False)

label = tk.Label(root, text="Checking for updates...")
label.pack(pady=10)

progress = ttk.Progressbar(root, orient="horizontal", length=250, mode="determinate")
progress.pack(pady=5)

local_version = get_local_version()
remote_version = get_remote_version()

if remote_version is None:
    label.config(text="Failed to check for updates.")
    ttk.Button(root, text="Close", command=root.destroy).pack(pady=10)
elif compare_versions(local_version, remote_version):
    label.config(text=f"Update available: {remote_version}")
    tk.Button(root, text="Update Now", command=start_download).pack(pady=10)
elif local_version is None:
    label.config(text=f"Update available: {remote_version}")
    ttk.Button(root, text="Update Now", command=start_download).pack(pady=10)
else:
    label.config(text="Tasker is up to date.")
    ttk.Button(root, text="Close", command=root.destroy).pack(pady=10)

root.protocol("WM_DELETE_WINDOW", exit_updater)

root.iconbitmap(get_asset_path("Assets/updater.ico"))
sv_ttk.set_theme("dark")
root.mainloop()