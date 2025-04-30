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
import winsound
from utils.logger import log_call, logger

class TasksWindow(tk.Toplevel): 

    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.callback = callback
        self.geometry("700x400")
        self.title("Tasker - Add Task")
        self.resizable(False, False)
        self.transient(None)
        self.attributes("-topmost", False)
        self.focus_force()

        def get_asset_path(relative_path):
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, relative_path)
            return os.path.join(os.path.abspath("."), relative_path)
        
        self.iconbitmap(get_asset_path("Assets/favicon.ico"))

        font = ("Segoe UI", 10, "bold")

        self.center_window()

        self.grid_columnconfigure(0, weight=1)  # Centering the widgets horizontally
        self.grid_columnconfigure(1, weight=1)  # Centering the widgets horizontally

        self.grid_rowconfigure(0, weight=0)  # Label row
        self.grid_rowconfigure(1, weight=0)  # Entry row
        self.grid_rowconfigure(2, weight=0)  # Date label row
        self.grid_rowconfigure(3, weight=0)  # Date entry row
        self.grid_rowconfigure(4, weight=0)  # Time label row
        self.grid_rowconfigure(5, weight=0)  # Time entry row
        self.grid_rowconfigure(6, weight=0)  # Submit button row
        self.grid_rowconfigure(7, weight=0)  # Cancel button row

        #Row 0 Elements
        tk.Label(self, text="New Task:", font=font).grid(row=0, column=0, pady=(10, 0), sticky="s", padx=10)
        tk.Label(self, text="Select Date:", font=font).grid(row=0, column=1, pady=(10, 0), sticky="s", padx=10)

        #Row 1 Elements
        self.entry = tk.Entry(self, width=70, font=("Segoe UI", 12))
        self.entry.grid(row=1, column=0, pady=10, padx=10)

        self.date_entry = DateEntry(
            self, width=12, background="darkblue", foreground="white", borderwidth=2, year=2025
        )
        self.date_entry.grid(row=1, column=1, pady=10, padx=10, sticky="n")

        #Row 2 Elements
        self.submit_btn = ttk.Button(self, text="Log Task", command=self.print_task)
        self.submit_btn.grid(row=2, column=0, pady=10, padx=10)
        self.submit_btn.config(state="disabled")
        tk.Label(self, text="Select Time:", font=font).grid(row=2, column=1, pady=5, sticky="s", padx=10)

        #Row 3 Elements
        dismiss_btn = ttk.Button(self, text="Cancel", command=self.hide_task_window)
        dismiss_btn.grid(row=3, column=0, pady=10, padx=10)

        self.time_frame = tk.Frame(self)
        self.time_frame.grid(row=3, column=1, padx=10, sticky="n")

        now = datetime.now()
        current_hour = (now + timedelta(hours=1)).hour
        current_minute = now.minute

        self.hour_var = tk.StringVar(value=self.format_time_input(str(current_hour)))
        self.minute_var = tk.StringVar(value=self.format_time_input(str(current_minute)))

        self.vcmd_hour = (self.register(self.on_validate_hour_input), "%P")
        self.vcmd_minute = (self.register(self.on_validate_minute_input), "%P")

        self.hour_spin = ttk.Spinbox(
            self.time_frame,
            from_=0,
            to=23,
            wrap=True,
            textvariable=self.hour_var,
            width=5,
            format="%02.0f",
            validate="key",
            validatecommand=self.vcmd_hour,
            command=self.format_hour_input
        )
        self.minute_spin = ttk.Spinbox(
            self.time_frame,
            from_=0,
            to=59,
            wrap=True,
            textvariable=self.minute_var,
            width=5,
            format="%02.0f",
            validate="key",
            validatecommand=self.vcmd_minute,
            command=self.format_minute_input
        )

        self.hour_spin.grid(row=0, column=0, padx=(0, 5))
        self.minute_spin.grid(row=0, column=1)

        self.hour_spin.bind("<FocusOut>", self.format_hour_input)
        self.minute_spin.bind("<FocusOut>", self.format_minute_input)

        self.bind("<Return>", self.on_enter)
        self.entry.bind("<KeyRelease>", self.check_entry)

        self.bind("<Escape>", self.on_escape)

    @log_call
    def get_task_and_time(self):
        task = self.entry.get()
        selected_date = self.date_entry.get_date() 
        selected_hour = self.hour_var.get()
        selected_minute = self.minute_var.get()
        selected_time = f"{selected_hour}:{selected_minute}"
        full_datetime = f"{selected_date} {selected_time}"
        return task, full_datetime
    
    def validate_time_input(self, time_input, max_val):
        if time_input == "" or (time_input.isdigit() and 0 <= int(time_input) <= max_val and len(time_input) <= 2):
            return True
        return False

    def format_time_input(self, value):
        return value.zfill(2)

    def on_validate_hour_input(self, hour_input):
        return self.validate_time_input(hour_input, 23)

    def on_validate_minute_input(self, minute_input):
        return self.validate_time_input(minute_input, 59)

    def format_hour_input(self, event=None):
        self.hour_var.set(self.format_time_input(self.hour_var.get()))

    def format_minute_input(self, event=None):
        self.minute_var.set(self.format_time_input(self.minute_var.get()))

    @log_call
    def print_task(self):
        task_description, due_date = self.get_task_and_time()

        print(task_description)
        print(due_date)

        self.save_task_to_db(task_description, due_date)

    @log_call
    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 930
        window_height = 200
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def hide_task_window(self):
        self.destroy()

    @log_call
    def save_task_to_db(self, name, due_date):
        sql_connection = sqlite3.connect("tasks.db")
        connection_cursor = sql_connection.cursor()
        connection_cursor.execute("INSERT INTO tasks (name, due_date) VALUES (?, ?)", (name, due_date))
        sql_connection.commit()
        sql_connection.close()
        print("task logged")

        messagebox.showinfo("New Task", f"Task added due: {due_date}")

        self.hide_task_window()

    @log_call
    def check_entry(self, event=None):
        if self.entry.get().strip():
            self.submit_btn.config(state="normal")
        else:
            self.submit_btn.config(state="disabled")

    def on_enter(self, event=None):
        self.submit_btn.invoke()

    def on_escape(self, event=None):
        self.hide_task_window()