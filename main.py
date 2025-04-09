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


class TasksWindow(tk.Toplevel): 

    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.callback = callback
        self.geometry("500x220")
        self.title("Tasker - Add Task")
        self.resizable(False, False)
        tk.Label(self, text="New Task:").pack(pady=(10, 0))
        self.entry = tk.Entry(self, width=50)
        self.entry.pack(pady=5)
        self.center_window()

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

class MainWindow(tk.Tk): 

    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.callback = callback
        self.geometry("500x500")
        self.resizable(False, False)
        self.title("Tasker")
        self.focus()
        self.hide_main_button = ttk.Button(self, text="Hide Main Window", command=self.hide_main_window)
        self.hide_main_button.pack(pady=10)

    def hide_main_window(self):
        self.withdraw()

init_db()

main_window = MainWindow()


threading.Thread(target=hotkey_listener, daemon=True).start()
threading.Thread(target=setup_tray, daemon=True).start()


main_window.mainloop()