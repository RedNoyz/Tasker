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

from src.task_window import TasksWindow
from src.task_list_window import TasksListWindow
from src.window_manager import task_window_instance, task_window_opening
import src.window_manager as window_manager

task_window_instance = None
task_list_windwow_instance = None

class MainWindow(tk.Tk): 

    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.callback = callback
        self.geometry("500x500")
        self.resizable(False, False)
        self.title("Tasker")
        self.focus()

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

        self.hide_main_button = ttk.Button(self, text="Hide Main Window", command=self.hide_main_window)
        self.hide_main_button.grid(row=0, column=1, pady=10, padx=10)

        self.new_task = ttk.Button(self, text="New Task", command=self.show_task_window)
        self.new_task.grid(row=1, column=1, pady=10, padx=10)

        self.new_task = ttk.Button(self, text="Show Task List", command=self.show_task_list_window)
        self.new_task.grid(row=2, column=1, pady=10, padx=10)

        # tk.Label(self, text="Made by RedNoyz", font=("Segoe UI", 10)).grid(row=6, column=2, pady=(10, 0), sticky="s", padx=10)


    def hide_main_window(self):
        self.withdraw()

    def show_task_window(self):
        if window_manager.task_window_opening:
            return

        try:
            window_manager.task_window_opening = True

            if window_manager.task_window_instance is None or not window_manager.task_window_instance.winfo_exists():
                from src.task_window import TasksWindow
                window_manager.task_window_instance = TasksWindow()
            else:
                win = window_manager.task_window_instance
                win.deiconify()
                win.lift()
                win.focus_force()
                win.attributes('-topmost', True)
                win.after(100, lambda: win.attributes('-topmost', False))

        except Exception as e:
            print("Error showing task window:", e)
            window_manager.task_window_instance = None
        finally:
            window_manager.task_window_opening = False

    def show_task_list_window(self):
        global task_list_windwow_instance
        try:
            if task_list_windwow_instance is None or not task_list_windwow_instance.winfo_exists():
                task_list_windwow_instance = TasksListWindow()
            else:
                task_list_windwow_instance.deiconify()
                task_list_windwow_instance.lift()
                task_list_windwow_instance.focus_force()
        except Exception as e:
            print("Error showing task list window:", e)
            task_list_windwow_instance = None