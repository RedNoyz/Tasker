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
        self.geometry("500x220")
        self.title("Tasker - Reminder")
        self.resizable(False, False)
        self.iconbitmap("favicon.ico")

        font = ("Segoe UI", 10, "bold")

        self.center_window()

        tk.Label(self, text="Task Reminder:", font=font).pack(pady=(10, 0))
        tk.Label(self, text="Select Date:").pack()
        self.date_entry = DateEntry(
            self, width=12, background="darkblue", foreground="white", borderwidth=2, year=2025
)
        self.date_entry.pack(pady=5)

        tk.Label(self, text="Select Time:", font=font).pack()
        self.time_frame = tk.Frame(self)
        self.time_frame.pack(pady=5)

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

        self.hour_spin.pack(side=tk.LEFT, padx=(0, 5))
        self.minute_spin.pack(side=tk.LEFT)
        

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 500
        window_height = 220
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
