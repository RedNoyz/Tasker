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
import src.window_manager as window_manager
from utils.logger import log_call, logger


class TasksReminderWindow(tk.Toplevel):
    sound_played = False

    def __init__(self, task_id, task_name, task_due_date, *args, callback=None, pending_reminders=0, **kwargs):
        super().__init__(*args, **kwargs)

        if not TasksReminderWindow.sound_played:
            threading.Thread(target=self._play_sound, daemon=True).start()
            TasksReminderWindow.sound_played = True
            
        window_manager.task_reminder_windows.append(self)

        self.user_action_taken = False

        self.pending_reminders = pending_reminders

        self.callback = callback
        self.title("Tasker - Reminder")
        self.resizable(False, False)
        self.transient(None)
        self.attributes("-topmost", False)
        self.deiconify()
        self.focus_force()
        self.protocol("WM_DELETE_WINDOW", self.snooze_task_hour)

        self.iconbitmap(self.get_asset_path("Assets/favicon.ico"))

        font = ("Segoe UI", 10, "bold")

        self.task_id = task_id

        self.center_window()

        self.grid_columnconfigure(0, weight=1, minsize=166)
        self.grid_columnconfigure(1, weight=1, minsize=166)
        self.grid_columnconfigure(2, weight=1, minsize=166)
        self.grid_columnconfigure(3, weight=1, minsize=166)
        self.grid_columnconfigure(4, weight=1, minsize=166)

        self.grid_rowconfigure(0, weight=0)  # Label row
        self.grid_rowconfigure(1, weight=0)  # Task Title row
        self.grid_rowconfigure(2, weight=0)  # Due Date label row
        self.grid_rowconfigure(3, weight=0)  # Date label row
        self.grid_rowconfigure(4, weight=0)  # Date entry row
        self.grid_rowconfigure(5, weight=0)  # Time label row
        self.grid_rowconfigure(6, weight=0)  # Time entry row
        self.grid_rowconfigure(7, weight=0)  # Buttons row

        tk.Label(self, text="Task:", font=font).grid(row=0, column=2, pady=(10, 0), sticky="n", padx=10)

        self.selectable_label = tk.Text(self, height=1, width=100, wrap=tk.WORD, font=("Segoe UI", 12, "bold"), bd=0)
        self.selectable_label.insert(tk.END, f"{task_name}")
        self.selectable_label.config(state=tk.DISABLED)
        self.selectable_label.grid(row=1, column=0, pady=10, padx=10, sticky="nsew", columnspan=5)
        tk.Label(self, text=f"Due: {task_due_date}", font=("Segoe UI", 10), foreground="red").grid(row=2, column=0, pady=5, sticky="s", padx=10)

        if self.pending_reminders > 0:
            foreground = "red" if self.pending_reminders > 5 else "gray"
            reminder_text = f"{self.pending_reminders} reminder{'s' if self.pending_reminders > 1 else ''} waiting"
            tk.Label(self, text=reminder_text, font=("Segoe UI", 10), foreground=foreground).grid(row=2, column=4, pady=5, sticky="s", padx=10)

        self.datetime_frame = tk.Frame(self)
        self.datetime_frame.grid(row=3, column=0, columnspan=5, pady=(10, 0))

        tk.Label(self.datetime_frame, text="Select New Due Date:", font=font).pack(pady=5)
        self.date_entry = DateEntry(self.datetime_frame, width=12, background="darkblue", foreground="white", borderwidth=2, year=2025)
        self.date_entry.pack(pady=5)

        tk.Label(self.datetime_frame, text="Select Time:", font=font).pack(pady=5)

        now = datetime.now()
        current_hour = (now + timedelta(hours=1)).hour
        current_minute = now.minute

        self.hour_var = tk.StringVar(value=self.format_time_input(str(current_hour)))
        self.minute_var = tk.StringVar(value=self.format_time_input(str(current_minute)))

        self.vcmd_hour = (self.register(self.on_validate_hour_input), "%P")
        self.vcmd_minute = (self.register(self.on_validate_minute_input), "%P")

        self.time_frame = tk.Frame(self.datetime_frame)
        self.time_frame.pack(pady=5)

        self.hour_spin = ttk.Spinbox(
            self.time_frame,
            from_=0,
            to=23,
            wrap=True,
            textvariable=self.hour_var,
            width=2,
            font=("Segoe UI", 12),
            justify="center",
            format="%02.0f",
            validate="key",
            validatecommand=self.vcmd_hour,
            command=self.format_hour_input
        )
        self.hour_spin.pack(side="left", padx=(0, 5))

        tk.Label(self.time_frame, text=":", font=("Segoe UI", 12, "bold")).pack(side="left")

        self.minute_spin = ttk.Spinbox(
            self.time_frame,
            from_=0,
            to=59,
            wrap=True,
            textvariable=self.minute_var,
            width=2,
            font=("Segoe UI", 12),
            justify="center",
            format="%02.0f",
            validate="key",
            validatecommand=self.vcmd_minute,
            command=self.format_minute_input
        )
        self.minute_spin.pack(side="left", padx=(5, 0))

        self.hour_spin.bind("<FocusOut>", self.format_hour_input)
        self.minute_spin.bind("<FocusOut>", self.format_minute_input)

        self.snooze_options = ["Snooze 3h", "Tomorrow 9AM", "Next Monday 9AM"]
        self.snooze_var = tk.StringVar()

        self.snooze_dropdown = ttk.Combobox(
            self,
            textvariable=self.snooze_var,
            values=self.snooze_options,
            state="readonly",
            font=("Segoe UI", 10)
        )
        self.snooze_dropdown.grid(row=7, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        self.snooze_dropdown.set("Snooze...")

        self.snooze_dropdown.bind("<<ComboboxSelected>>", self.handle_snooze_selection)

        self.snooze_hour = ttk.Button(self, text="Snooze 1h", command=self.snooze_task_hour)
        self.snooze_hour.grid(row=7, column=2, pady=10, padx=10, sticky="ew")

        self.new_date_btn = ttk.Button(self, text="New Date", command=self.snooze_task_new_date)
        self.new_date_btn.grid(row=7, column=3, pady=10, padx=10, sticky="ew")
        
        self.complete_btn = ttk.Button(self, text="Complete", command=self.complete_task)
        self.complete_btn.grid(row=7, column=4, pady=10, padx=10, sticky="ew")

    @log_call
    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 840
        window_height = 380
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    @log_call
    def _play_sound(self):
        winsound.PlaySound(
            self.get_asset_path('Assets/notification_sound.wav'),
            winsound.SND_FILENAME
        )
    
    @log_call
    def hide_reminder_window(self):
        global is_reminder_open

        print(f"[hide_reminder_window] Called for task id {self.task_id}")
        logger.info(f"[hide_reminder_window] Called for task id {self.task_id}")

        if self in window_manager.task_reminder_windows:
            window_manager.task_reminder_windows.remove(self)

        is_reminder_open = False

        self.destroy()

        if self.callback:
            print(f"[hide_reminder_window] Calling callback after hide.")
            logger.info(f"[hide_reminder_window] Calling callback after hide.")
            self.callback()

    @log_call
    def get_task_and_time(self):
        selected_date = self.date_entry.get_date()
        selected_hour = self.hour_var.get()
        selected_minute = self.minute_var.get()
        selected_time = f"{selected_hour}:{selected_minute}"
        full_datetime = f"{selected_date} {selected_time}"
        return full_datetime
    

    def validate_time_input(self, time_input, max_val):
        if time_input == "" or (time_input.isdigit() and 0 <= int(time_input) <= max_val and len(time_input) <= 2):
            return True
        return False

    def format_time_input(self, value):
        return value.zfill(2)

    def on_validate_hour_input(self, time_input):
        return self.validate_time_input(time_input, 23)

    def on_validate_minute_input(self, time_input):
        return self.validate_time_input(time_input, 59)

    def format_hour_input(self, event=None):
        self.hour_var.set(self.format_time_input(self.hour_var.get()))

    def format_minute_input(self, event=None):
        self.minute_var.set(self.format_time_input(self.minute_var.get()))
    
    @log_call
    def update_task_status(task_id, status):
        sql_connection = sqlite3.connect("tasks.db")
        connection_cursor = sql_connection.cursor()
        connection_cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        sql_connection.commit()
        sql_connection.close()

    @log_call
    def snooze_task_hour(self):
        sql_connection = sqlite3.connect("tasks.db")
        connection_cursor = sql_connection.cursor()

        connection_cursor.execute("SELECT snooze_counter FROM tasks WHERE id = ?", (self.task_id,))
        row = connection_cursor.fetchone()
        snooze_counter = (row[0] if row and row[0] is not None else 0) + 1

        now_date = datetime.now()

        new_due_date = now_date + timedelta(hours=1)

        formatted_due_date = new_due_date.strftime("%Y-%m-%d %H:%M")

        connection_cursor.execute(
            "UPDATE tasks SET due_date = ?, notified = 0, snooze_counter = ? WHERE id = ?",
            (formatted_due_date, snooze_counter, self.task_id),
        )
        sql_connection.commit()
        sql_connection.close()

        self.user_action_taken = True

        messagebox.showinfo("Snoozed", f"Task snoozed to: {formatted_due_date}\n\nSnoozed {snooze_counter} times", parent=self)

        self.hide_reminder_window()

    @log_call
    def snooze_task_three_hour(self):
        sql_connection = sqlite3.connect("tasks.db")
        connection_cursor = sql_connection.cursor()

        connection_cursor.execute("SELECT snooze_counter FROM tasks WHERE id = ?", (self.task_id,))
        row = connection_cursor.fetchone()
        snooze_counter = (row[0] if row and row[0] is not None else 0) + 1

        now_date = datetime.now()

        new_due_date = now_date + timedelta(hours=3)

        formatted_due_date = new_due_date.strftime("%Y-%m-%d %H:%M")

        connection_cursor.execute(
            "UPDATE tasks SET due_date = ?, notified = 0, snooze_counter = ? WHERE id = ?",
            (formatted_due_date, snooze_counter, self.task_id),
        )
        sql_connection.commit()
        sql_connection.close()

        self.user_action_taken = True

        messagebox.showinfo("Snoozed", f"Task snoozed to: {formatted_due_date}\n\nSnoozed {snooze_counter} times", parent=self)

        self.hide_reminder_window()

    @log_call
    def snooze_task_tomorrow_morning(self):
        sql_connection = sqlite3.connect("tasks.db")
        connection_cursor = sql_connection.cursor()

        connection_cursor.execute("SELECT snooze_counter FROM tasks WHERE id = ?", (self.task_id,))
        row = connection_cursor.fetchone()
        snooze_counter = (row[0] if row and row[0] is not None else 0) + 1

        now = datetime.now()

        tomorrow_morning = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)

        formatted_due_date = tomorrow_morning.strftime("%Y-%m-%d %H:%M")

        connection_cursor.execute(
                "UPDATE tasks SET due_date = ?, notified = 0, snooze_counter = ? WHERE id = ?",
                (formatted_due_date, snooze_counter, self.task_id),
            )
        sql_connection.commit()
        sql_connection.close()

        self.user_action_taken = True

        messagebox.showinfo(
                "Snoozed",
                f"Task snoozed to: {formatted_due_date}\n\nSnoozed {snooze_counter} times",
                parent=self
            )

        self.hide_reminder_window()

    @log_call
    def snooze_task_next_monday_morning(self):
        sql_connection = sqlite3.connect("tasks.db")
        connection_cursor = sql_connection.cursor()

        connection_cursor.execute("SELECT snooze_counter FROM tasks WHERE id = ?", (self.task_id,))
        row = connection_cursor.fetchone()
        snooze_counter = (row[0] if row and row[0] is not None else 0) + 1

        now = datetime.now()

        days_until_monday = (7 - now.weekday() + 0) % 7
        if days_until_monday == 0:
            days_until_monday = 7

        next_monday = now + timedelta(days=days_until_monday)
        next_monday_morning = next_monday.replace(hour=9, minute=0, second=0, microsecond=0)

        formatted_due_date = next_monday_morning.strftime("%Y-%m-%d %H:%M")

        connection_cursor.execute(
            "UPDATE tasks SET due_date = ?, notified = 0, snooze_counter = ? WHERE id = ?",
            (formatted_due_date, snooze_counter, self.task_id),
        )
        sql_connection.commit()
        sql_connection.close()

        self.user_action_taken = True

        messagebox.showinfo(
            "Snoozed",
            f"Task snoozed to: {formatted_due_date}\n\nSnoozed {snooze_counter} times",
            parent=self
        )

        self.hide_reminder_window()


    @log_call
    def snooze_task_new_date(self):
        sql_connection = sqlite3.connect("tasks.db")
        connection_cursor = sql_connection.cursor()

        connection_cursor.execute("SELECT snooze_counter FROM tasks WHERE id = ?", (self.task_id,))
        row = connection_cursor.fetchone()
        snooze_counter = (row[0] if row and row[0] is not None else 0) + 1

        formatted_due_date = self.get_task_and_time()
        

        connection_cursor.execute(
            "UPDATE tasks SET due_date = ?, notified = 0, snooze_counter = ? WHERE id = ?",
            (formatted_due_date, snooze_counter, self.task_id),
        )
        sql_connection.commit()
        sql_connection.close()

        self.user_action_taken = True

        messagebox.showinfo("Snoozed", f"Task snoozed to: {formatted_due_date}\n\nSnoozed {snooze_counter} times", parent=self)

        self.hide_reminder_window()

    @log_call
    def complete_task(self):
        sql_connection = sqlite3.connect("tasks.db")
        connection_cursor = sql_connection.cursor()

        completed_date = datetime.now().strftime("%Y-%m-%d %H:%M")

        connection_cursor.execute(
            "UPDATE tasks SET status = 'complete', complete_date = ? WHERE id = ?",
            (completed_date, self.task_id)
        )

        print("Rows affected:", connection_cursor.rowcount)
        logger.info("Rows affected:", connection_cursor.rowcount)
        
        sql_connection.commit()
        sql_connection.close()

        print(completed_date)

        self.user_action_taken = True

        messagebox.showinfo("Completed", f"Task completed on: {completed_date}", parent=self)

        self.hide_reminder_window()

    def get_asset_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
    
    def get_task_id(self, task_id):
        self.task_id = int(task_id)

    def return_task_id(self):
        return self.task_id
    
    def handle_snooze_selection(self, event):
        choice = self.snooze_var.get()

        if choice == "Snooze 3h":
            self.snooze_task_three_hour()
        elif choice == "Tomorrow 9AM":
            self.snooze_task_tomorrow_morning()
        elif choice == "Next Monday 9AM":
            self.snooze_task_next_monday_morning()

        if self.winfo_exists():
            self.snooze_dropdown.set("Snooze...")