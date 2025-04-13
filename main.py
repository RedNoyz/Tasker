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
import sv_ttk

from src.main_window import MainWindow
from src.task_window import TasksWindow
from src.task_reminder_window import TasksReminderWindow

task_window_instance = None

def init_db():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute(
        """
            CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            due_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
            notified INTEGER DEFAULT 0,
            status TEXT DEFAULT 'open',
            complete_date TIMESTAMP,
            snooze_counter INTEGER DEFAULT 0
        )
    """ 
    )

    c.execute(
        """
            CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            name TEXT
        )
    """ 
    )
    conn.commit()
    conn.close()

def create_image():
    image = Image.new("RGB", (64, 64), "blue")
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 16, 48, 48), fill="white")
    return image

def setup_tray(): 
    menu = Menu(MenuItem("Open Main Window", show_main_window), MenuItem("Exit", quit_app))
    icon = Icon("QuickTask", create_image(), "Quick Task", menu)
    icon.run()

def quit_app(icon):
    icon.stop()
    main_window.destroy()
    sys.exit()

def show_task_window():
    global task_window_instance
    try:
        if task_window_instance is None or not task_window_instance.winfo_exists():
            task_window_instance = TasksWindow()
        else:
            task_window_instance.deiconify()
            task_window_instance.lift()
            task_window_instance.focus_force()
            task_window_instance.attributes('-topmost', True)
            task_window_instance.after(100, lambda: task_window_instance.attributes('-topmost', False))
    except Exception as e:
        print("Error showing task window:", e)
        task_window_instance = None

def show_reminder_window(task_id, task_name, task_due_date):
    task_window = TasksReminderWindow(task_id, task_name, task_due_date)
    task_window.deiconify()
    task_window.lift()
    task_window.focus_force() 
    task_window.attributes('-topmost', True)
    task_window.after(100, lambda: task_window.attributes('-topmost', False ))

def show_main_window():
    main_window.deiconify()
    main_window.lift()
    main_window.focus_force()
    

def check_for_due_tasks():
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn = sqlite3.connect("tasks.db")
        c = conn.cursor()
        c.execute(
            """
            SELECT id, name, due_date FROM tasks
            WHERE due_date IS NOT NULL AND status = 'open' AND notified = 0 AND due_date <= ?
            ORDER BY due_date ASC
        """,
            (now,),
        )
        due_tasks = c.fetchall()

        for task in due_tasks:
            task_id, name, due_date = task
            show_reminder_window(task_id, name, due_date)
            # Mark as notified so it doesn't remind again
            c.execute("UPDATE tasks SET notified = 1 WHERE id = ?", (task_id,))

        conn.commit()
        conn.close()
        time.sleep(10)



def hotkey_listener():
    keyboard.add_hotkey("ctrl+shift+space", show_task_window)
    keyboard.wait()

def hotkey_listener_reminder():
    keyboard.add_hotkey("ctrl+space", show_reminder_window)
    keyboard.wait()


init_db()

threading.Thread(target=hotkey_listener, daemon=True).start()
threading.Thread(target=check_for_due_tasks, daemon=True).start()
threading.Thread(target=setup_tray, daemon=True).start()



main_window = MainWindow()
sv_ttk.set_theme("dark")
main_window.mainloop()