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
from main_window import MainWindow
from task_window import TasksWindow
from task_reminder_window import TasksReminderWindow

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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notified INTEGER DEFAULT 0,
            status TEXT DEFAULT 'open'
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

def show_reminder_window():
    task_window = TasksReminderWindow()
    task_window.deiconify()
    task_window.lift()
    task_window.focus_force() 
    task_window.attributes('-topmost', True)
    task_window.after(100, lambda: task_window.attributes('-topmost', False ))

def show_main_window():
    main_window.deiconify()
    main_window.lift()
    main_window.focus_force()
    

def hotkey_listener():
    keyboard.add_hotkey("shift+space", show_task_window)
    keyboard.wait()

def hotkey_listener_reminder():
    keyboard.add_hotkey("ctrl+space", show_reminder_window)
    keyboard.wait()


init_db()

threading.Thread(target=hotkey_listener, daemon=True).start()
threading.Thread(target=hotkey_listener_reminder, daemon=True).start()
threading.Thread(target=setup_tray, daemon=True).start()

main_window = MainWindow()
main_window.mainloop()