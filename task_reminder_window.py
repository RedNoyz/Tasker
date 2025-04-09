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

class TasksReminderWindow(tk.Toplevel): 

    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.callback = callback
        self.geometry("500x320")
        self.title("Tasker - Reminder")
        self.resizable(False, False)
        self.iconbitmap("favicon.ico")

        font = ("Segoe UI", 10, "bold")

        self.center_window()

        self.grid_columnconfigure(0, weight=1, minsize=166)
        self.grid_columnconfigure(1, weight=1, minsize=166)
        self.grid_columnconfigure(2, weight=1, minsize=166)

        self.grid_rowconfigure(0, weight=0)  # Label row
        self.grid_rowconfigure(1, weight=0)  # Task Title row
        self.grid_rowconfigure(2, weight=0)  # Date label row
        self.grid_rowconfigure(3, weight=0)  # Date entry row
        self.grid_rowconfigure(4, weight=0)  # Time label row
        self.grid_rowconfigure(5, weight=0)  # Time entry row
        self.grid_rowconfigure(6, weight=0)  # Buttons row

        tk.Label(self, text="Task:", font=font).grid(row=0, column=1, pady=(10, 0), sticky="n", padx=10)

        self.selectable_label = tk.Text(self, height=1, width=50, wrap=tk.WORD, font=("Segoe UI", 12, "bold"), bd=0)
        self.selectable_label.insert(tk.END, "This is a selectable label!")
        self.selectable_label.config(state=tk.DISABLED)
        self.selectable_label.grid(row=1, column=0, pady=10, padx=10, sticky="nsew", columnspan=3)

        tk.Label(self, text="Select New Due Date:", font=font).grid(row=2, column=1, pady=5, sticky="s", padx=10)
        self.date_entry = DateEntry(
            self, width=12, background="darkblue", foreground="white", borderwidth=2, year=2025
        )
        self.date_entry.grid(row=3, column=1, pady=10, padx=10)

        tk.Label(self, text="Select Time:", font=font).grid(row=4, column=1, pady=5, sticky="n", padx=10)
        self.time_frame = tk.Frame(self)
        self.time_frame.grid(row=5, column=1, pady=10, padx=10)

        self.hour_var = tk.StringVar(value="12")
        self.minute_var = tk.StringVar(value="00")

        self.hour_spin = ttk.Spinbox(
            self.time_frame,
            from_=0,
            to=23,
            wrap=True,
            textvariable=self.hour_var,
            width=5,
            format="%02.0f",
        )
        self.minute_spin = ttk.Spinbox(
            self.time_frame,
            from_=0,
            to=59,
            wrap=True,
            textvariable=self.minute_var,
            width=5,
            format="%02.0f",
        )

        self.hour_spin.grid(row=0, column=1, padx=(0, 5))
        self.minute_spin.grid(row=0, column=2)

        self.new_date_btn = ttk.Button(self, text="New Date")
        self.new_date_btn.grid(row=6, column=0, pady=10, padx=10, sticky="ew")

        self.submit_btn = ttk.Button(self, text="Snooze 1h")
        self.submit_btn.grid(row=6, column=1, pady=10, padx=10, sticky="ew")
        
        self.complete_btn = ttk.Button(self, text="Complete")
        self.complete_btn.grid(row=6, column=2, pady=10, padx=10, sticky="ew")

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 500
        window_height = 320
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
