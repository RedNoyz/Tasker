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


class TasksReminderWindow(tk.Toplevel): 

    def __init__(self, task_id, task_name, task_due_date, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)

        sound_thread = threading.Thread(target=self.play_sound)
        sound_thread.start()

        self.callback = callback
        self.geometry("700x400")
        self.title("Tasker - Reminder")
        self.resizable(False, False)
        self.iconbitmap("Assets\\favicon.ico")
        self.overrideredirect(True)

        font = ("Segoe UI", 10, "bold")

        self.task_id = task_id

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
        self.selectable_label.insert(tk.END, f"{task_name} | Due: {task_due_date}")
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

        self.hour_spin.grid(row=0, column=1, padx=(0, 5))
        self.minute_spin.grid(row=0, column=2)

        self.hour_spin.bind("<FocusOut>", self.format_hour_input)
        self.minute_spin.bind("<FocusOut>", self.format_minute_input)

        self.new_date_btn = ttk.Button(self, text="New Date")
        self.new_date_btn.grid(row=6, column=0, pady=10, padx=10, sticky="ew")

        self.submit_btn = ttk.Button(self, text="Snooze 1h", command=self.snooze_task_hour)
        self.submit_btn.grid(row=6, column=1, pady=10, padx=10, sticky="ew")
        
        self.complete_btn = ttk.Button(self, text="Complete")
        self.complete_btn.grid(row=6, column=2, pady=10, padx=10, sticky="ew")

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 700
        window_height = 400
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def play_sound(self):
        winsound.PlaySound('E:\\My Projects\\Tasker\\Assets\\notification_sound.wav', winsound.SND_FILENAME)
    
    def hide_reminder_window(self):
        self.withdraw()

    def get_task_and_time(self):
        task = self.task_id
        selected_date = self.date_entry.get_date()
        selected_hour = self.hour_var.get()
        selected_minute = self.minute_var.get()
        selected_time = f"{selected_hour}:{selected_minute}"
        full_datetime = f"{selected_date} {selected_time}"
        return task, full_datetime
    
    def validate_time_input(self, P, max_val):
        if P == "" or (P.isdigit() and 0 <= int(P) <= max_val and len(P) <= 2):
            return True
        return False

    def format_time_input(self, value):
        return value.zfill(2)

    def on_validate_hour_input(self, P):
        return self.validate_time_input(P, 23)

    def on_validate_minute_input(self, P):
        return self.validate_time_input(P, 59)

    def format_hour_input(self, event=None):
        self.hour_var.set(self.format_time_input(self.hour_var.get()))

    def format_minute_input(self, event=None):
        self.minute_var.set(self.format_time_input(self.minute_var.get()))
    
    def update_task_status(task_id, status):
        conn = sqlite3.connect("tasks.db")
        c = conn.cursor()
        c.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        conn.commit()
        conn.close()

# TODO: Add the snooze with new date functionality
# TODO: Add the Complete task functionality

    def snooze_task_hour(self):
        conn = sqlite3.connect("tasks.db")
        c = conn.cursor()

        now_date = datetime.now()

        new_due_date = now_date + timedelta(hours=1)

        c.execute(
            "UPDATE tasks SET due_date = ?, notified = 0 WHERE id = ?",
            (new_due_date.strftime("%Y-%m-%d %H:%M"), self.task_id),
        )
        conn.commit()
        self.hide_reminder_window()
