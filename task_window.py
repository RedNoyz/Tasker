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
        self.geometry("500x220")
        self.title("Tasker - Add Task")
        self.resizable(False, False)

        self.center_window()

        tk.Label(self, text="New Task:").pack(pady=(10, 0))
        self.entry = tk.Entry(self, width=50)
        self.entry.pack(pady=5)
        tk.Label(self, text="Select Date:").pack()
        self.date_entry = DateEntry(
            self, width=12, background="darkblue", foreground="white", borderwidth=2, year=2025
)
        self.date_entry.pack(pady=5)

        tk.Label(self, text="Select Time:").pack()
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

        submit_btn = ttk.Button(self, text="Log Task", command=self.print_task)
        submit_btn.pack(pady=10)
        
    def get_task_and_time(self):
        task = self.entry.get()
        selected_date = self.date_entry.get_date() 
        selected_hour = self.hour_var.get()
        selected_minute = self.minute_var.get()
        selected_time = f"{selected_hour}:{selected_minute}"
        full_datetime = f"{selected_date} {selected_time}"
        # print("Selected DateTime:", full_datetime)
        return task, full_datetime
            
    def print_task(self):
        task_description, time_of_task = self.get_task_and_time()

        print(task_description)
        print(time_of_task)

        # save_task_to_db(task_description, time_of_task)

        self.entry.delete(0, tk.END)

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 500
        window_height = 220
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def hide_task_window(self):
        self.withdraw()

    def save_task_to_db(name, due_date):
        conn = sqlite3.connect("tasks.db")
        c = conn.cursor()
        c.execute("INSERT INTO tasks (name, due_date) VALUES (?, ?)", (name, due_date))
        conn.commit()
        conn.close()
        print("task logged")