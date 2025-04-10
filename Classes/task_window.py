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

class TasksWindow(tk.Toplevel): 

    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.callback = callback
        self.geometry("500x320")
        self.title("Tasker - Add Task")
        self.resizable(False, False)
        self.iconbitmap("Assets\\favicon.ico")

        font = ("Segoe UI", 10, "bold")

        self.center_window()

        self.grid_columnconfigure(0, weight=1)  # Centering the widgets horizontally
        self.grid_rowconfigure(0, weight=0)  # Label row
        self.grid_rowconfigure(1, weight=0)  # Entry row
        self.grid_rowconfigure(2, weight=0)  # Date label row
        self.grid_rowconfigure(3, weight=0)  # Date entry row
        self.grid_rowconfigure(4, weight=0)  # Time label row
        self.grid_rowconfigure(5, weight=0)  # Time entry row
        self.grid_rowconfigure(6, weight=0)  # Submit button row
        self.grid_rowconfigure(7, weight=0)  # Cancel button row

        tk.Label(self, text="New Task:", font=font).grid(row=0, column=0, pady=(10, 0), sticky="n", padx=10)
        self.entry = tk.Entry(self, width=50, font=("Segoe UI", 12))
        self.entry.grid(row=1, column=0, pady=10, padx=10)

        tk.Label(self, text="Select Date:", font=font).grid(row=2, column=0, pady=5, sticky="n", padx=10)
        self.date_entry = DateEntry(
            self, width=12, background="darkblue", foreground="white", borderwidth=2, year=2025
        )
        self.date_entry.grid(row=3, column=0, pady=10, padx=10)

        tk.Label(self, text="Select Time:", font=font).grid(row=4, column=0, pady=5, sticky="n", padx=10)
        self.time_frame = tk.Frame(self)
        self.time_frame.grid(row=5, column=0, pady=10, padx=10)

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

        self.hour_spin.grid(row=0, column=0, padx=(0, 5))
        self.minute_spin.grid(row=0, column=1)

        self.submit_btn = ttk.Button(self, text="Log Task", command=self.print_task)
        self.submit_btn.grid(row=6, column=0, pady=10, padx=10)
        self.submit_btn.config(state="disabled")
        self.entry.bind("<KeyRelease>", self.check_entry)

        dismiss_btn = ttk.Button(self, text="Cancel", command=self.hide_task_window)
        dismiss_btn.grid(row=7, column=0, pady=10, padx=10)

    def get_task_and_time(self):
        task = self.entry.get()
        selected_date = self.date_entry.get_date() 
        selected_hour = self.hour_var.get()
        selected_minute = self.minute_var.get()
        selected_time = f"{selected_hour}:{selected_minute}"
        full_datetime = f"{selected_date} {selected_time}"
        return task, full_datetime
            
    def print_task(self):
        task_description, due_date = self.get_task_and_time()

        print(task_description)
        print(due_date)

        self.save_task_to_db(task_description, due_date)

        self.entry.delete(0, tk.END)

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 500
        window_height = 320
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def hide_task_window(self):
        self.withdraw()

    def save_task_to_db(self, name, due_date):
        conn = sqlite3.connect("tasks.db")
        c = conn.cursor()
        c.execute("INSERT INTO tasks (name, due_date) VALUES (?, ?)", (name, due_date))
        conn.commit()
        conn.close()
        print("task logged")
        self.hide_task_window()

    def check_entry(self, event=None):
        if self.entry.get().strip():
            self.submit_btn.config(state="normal")
        else:
            self.submit_btn.config(state="disabled")