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
    task_window = TasksWindow()
    task_window.deiconify()
    task_window.lift()
    task_window.focus_force() 
    task_window.attributes('-topmost', True)
    task_window.after(100, lambda: task_window.attributes('-topmost', False))

def show_main_window():
    main_window.deiconify()
    main_window.lift()
    main_window.focus_force()

def hotkey_listener():
    keyboard.add_hotkey("shift+space", show_task_window)
    keyboard.wait()


init_db()

main_window = MainWindow()


threading.Thread(target=hotkey_listener, daemon=True).start()
threading.Thread(target=setup_tray, daemon=True).start()


main_window.mainloop()