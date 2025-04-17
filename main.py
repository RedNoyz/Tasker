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
from queue import Queue, Empty

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main_window import MainWindow
from src.task_window import TasksWindow
from src.task_reminder_window import TasksReminderWindow
from src.task_list_window import TasksListWindow
from src.window_manager import task_window_instance, task_window_opening
from src.window_manager import task_reminder_windows
import src.window_manager as window_manager

due_queue = Queue()

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

def show_reminder_window(task_id, task_name, task_due_date):
    inst = TasksReminderWindow(task_id, task_name, task_due_date)
    window_manager.task_reminder_windows.append(inst)

    def on_close():
        try:
            window_manager.task_reminder_windows.remove(inst)
        except ValueError:
            pass
        inst.destroy()

    inst.protocol("WM_DELETE_WINDOW", on_close)
    inst.deiconify()
    inst.lift()
    inst.focus_force()
    inst.attributes('-topmost', True)
    inst.after(100, lambda: inst.attributes('-topmost', False))

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
            WHERE due_date IS NOT NULL
              AND status = 'open'
              AND notified = 0
              AND due_date <= ?
            ORDER BY due_date ASC
            """,
            (now,),
        )
        due_tasks = c.fetchall()

        for task_id, name, due_date in due_tasks:
            due_queue.put((task_id, name, due_date))
            c.execute("UPDATE tasks SET notified = 1 WHERE id = ?", (task_id,))

        conn.commit()
        conn.close()
        time.sleep(10)

def process_due_queue():
    try:
        while True:
            task_id, name, due_date = due_queue.get_nowait()
            show_reminder_window(task_id, name, due_date)
    except Empty:
        pass
    finally:
        main_window.after(100, process_due_queue)

def reset_notified_worker(interval_secs=30):
    while True:
        conn = sqlite3.connect("tasks.db")
        c = conn.cursor()

        live_ids = []
        for inst in list(window_manager.task_reminder_windows):
            if inst.winfo_exists():
                live_ids.append(inst.return_task_id())
            else:
                window_manager.task_reminder_windows.remove(inst)

        if live_ids:
            placeholders = ",".join("?" for _ in live_ids)
            sql = (
                "UPDATE tasks SET notified = 0 "
                "WHERE notified = 1 AND status = 'open' "
                f"AND id NOT IN ({placeholders})"
            )
            c.execute(sql, live_ids)
        else:
            c.execute(
                "UPDATE tasks SET notified = 0 WHERE notified = 1 AND status = 'open'"
            )

        updated = c.rowcount

        conn.commit()
        conn.close()

        if updated:
            print(f"[reset_notified_worker] reset {updated} tasks")
            
        time.sleep(interval_secs)

main_window = MainWindow()

main_window.after(100, process_due_queue)

def hotkey_listener():
    keyboard.add_hotkey("ctrl+shift+space", main_window.show_task_window)
    keyboard.wait()

init_db()

threading.Thread(target=check_for_due_tasks, daemon=True).start()
threading.Thread(target=reset_notified_worker, daemon=True).start()
threading.Thread(target=hotkey_listener, daemon=True).start()
threading.Thread(target=setup_tray, daemon=True).start()

sv_ttk.set_theme("dark")
main_window.mainloop()