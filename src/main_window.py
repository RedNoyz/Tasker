import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import keyboard
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime, timedelta
import os
import time
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import sys
import subprocess
import requests

from src.task_window import TasksWindow
from src.task_list_window import TasksListWindow
from src.window_manager import task_window_instance, task_window_opening
import src.window_manager as window_manager
from utils.logger import log_call, logger
from utils.version import __version__ as app_version

task_list_window_instance = None

GITHUB_API_RELEASES_URL = "https://api.github.com/repos/RedNoyz/Tasker/releases/latest"

class MainWindow(tk.Tk): 

    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.callback = callback
        self.geometry("500x500")
        self.resizable(False, False)
        self.title("Tasker")
        self.focus()

        self.protocol("WM_DELETE_WINDOW", self.notified_set_to_false)

        def get_asset_path(relative_path):
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, relative_path)
            return os.path.join(os.path.abspath("."), relative_path)

        self.iconbitmap(get_asset_path("Assets/favicon.ico"))

        font = ("Segoe UI", 10, "bold")

        self.grid_columnconfigure(0, weight=1, minsize=166)
        self.grid_columnconfigure(1, weight=1, minsize=166)
        self.grid_columnconfigure(2, weight=1, minsize=166)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0)
        self.grid_rowconfigure(5, weight=0)
        self.grid_rowconfigure(6, weight=0)

        self.hide_main_window_btn = ttk.Button(self, text="Hide Main Window", command=self.hide_main_window)
        self.hide_main_window_btn.grid(row=0, column=1, pady=10, padx=10)

        self.new_task_btn = ttk.Button(self, text="New Task", command=self.show_task_window)
        self.new_task_btn.grid(row=1, column=1, pady=10, padx=10)

        self.show_task_list_btn = ttk.Button(self, text="Show Task List", command=self.show_task_list_window)
        self.show_task_list_btn.grid(row=2, column=1, pady=10, padx=10)

        self.check_for_update_btn = tk.Button(self, text="Check For Update", command=self.run_updater, bg="darkgreen")
        self.check_for_update_btn.grid(row=3, column=1, pady=10, padx=10)

        tk.Label(self, text=f"Version v{app_version}", font=("Segoe UI", 10)).grid(row=6, column=2, pady=(10, 0), sticky="s", padx=10)


    def hide_main_window(self):
        self.withdraw()

    @log_call
    def show_task_window(self):
        if window_manager.task_window_opening:
            return

        try:
            window_manager.task_window_opening = True

            if window_manager.task_window_instance is None or not window_manager.task_window_instance.winfo_exists():
                window_manager.task_window_instance = TasksWindow()
            else:
                task_window = window_manager.task_window_instance
                task_window.deiconify()
                task_window.lift()
                task_window.focus_force()
                task_window.attributes('-topmost', True)
                task_window.after(100, lambda: task_window.attributes('-topmost', False))

        except Exception as e:
            print("Error showing task window:", e)
            window_manager.task_window_instance = None
        finally:
            window_manager.task_window_opening = False

    @log_call
    def show_task_list_window(self):
        global task_list_window_instance
        try:
            if task_list_window_instance is None or not task_list_window_instance.winfo_exists():
                task_list_window_instance = TasksListWindow()
            else:
                task_list_window_instance.deiconify()
                task_list_window_instance.lift()
                task_list_window_instance.focus_force()
        except Exception as e:
            print("Error showing task list window:", e)
            task_list_window_instance = None

    @log_call
    def notified_set_to_false(self):
        sql_connection = sqlite3.connect("tasks.db")
        connection_cursor = sql_connection.cursor()

        for inst in list(window_manager.task_reminder_windows):
            if inst.winfo_exists():
                task_id = inst.return_task_id()
                connection_cursor.execute(
                    "UPDATE tasks SET notified = 0 WHERE id = ?",
                    (task_id,)
                )
            else:
                window_manager.task_reminder_windows.remove(inst)

        sql_connection.commit()
        sql_connection.close()

        try:
            window_manager.task_reminder_windows.remove(self)
        except ValueError:
            pass

        self.destroy()

    def get_remote_version(self):
        try:
            response = requests.get(GITHUB_API_RELEASES_URL, timeout=5)
            data = response.json()
            return data["tag_name"].lstrip("v")
        except Exception:
            return None

    def run_updater(self):
        if self.get_remote_version() == app_version:
            messagebox.showinfo("Latest Version", "You have the latest version.")
        else:
            try:
                subprocess.Popen(["updater.exe"], shell=True)
            except Exception as e:
                print(f"Failed to run updater: {e}")