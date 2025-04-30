import sys
from utils.version import __version__

if "--version" in sys.argv:
    print(__version__)
    sys.exit(0)

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
import sv_ttk
from queue import Queue, Empty
import functools, inspect
import logging
import ctypes
from ctypes import wintypes
import subprocess
from utils.version import __version__ as app_version
from src.main_window import GITHUB_API_RELEASES_URL


sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main_window import MainWindow
from src.task_window import TasksWindow
from src.task_reminder_window import TasksReminderWindow
from src.task_list_window import TasksListWindow
from src.window_manager import task_window_instance, task_window_opening
from src.window_manager import task_reminder_windows
import window_manager as window_manager
from utils.logger import log_call, logger


due_queue = Queue()

is_reminder_open = False

stop_listening = False

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
user32   = ctypes.WinDLL("user32",   use_last_error=True)

MUTEX_NAME = "TaskerSingletonMutex"
hMutex = kernel32.CreateMutexW(None, wintypes.BOOL(False), MUTEX_NAME)

last_error = ctypes.get_last_error()
print(f"[singleton] CreateMutexW returned handle={hMutex}, err={last_error}")
logger.info(f"[singleton] CreateMutexW returned handle={hMutex}, err={last_error}")

if last_error == 183:
    print("[singleton] another instance detected, forwarding focus…")
    logger.warning("[singleton] another instance detected, forwarding focus…")
    TITLE = "Tasker"
    hwnd = user32.FindWindowW(None, TITLE)
    print(f"[singleton] FindWindowW({TITLE!r}) -> hwnd={hwnd}")
    if hwnd:
        SW_RESTORE = 9
        user32.ShowWindow(hwnd, SW_RESTORE)
        user32.SetForegroundWindow(hwnd)
        print("[singleton] focus sent successfully")
        logger.info("[singleton] focus sent successfully")
    else:
        print("[singleton] could not find window to focus")
        logger.info("[singleton] could not find window to focus")
    sys.exit(0)

print("[singleton] no other instance, continuing startup")
logger.info("[singleton] no other instance, continuing startup")


def init_db():
    sql_connection = sqlite3.connect("tasks.db")
    connection_cursor = sql_connection.cursor()
    connection_cursor.execute(
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

    connection_cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            name TEXT
        )
    """ 
    )
    sql_connection.commit()
    sql_connection.close()

def create_image():
    image = Image.new("RGB", (64, 64), "blue")
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 16, 48, 48), fill="white")
    return image

def setup_tray():
    menu = Menu(
        MenuItem("📂 Open Main Window", lambda icon, item: show_main_window()),
        Menu.SEPARATOR,
        MenuItem("📃 Show Task List", lambda icon, item: main_window.show_task_list_window()),
        Menu.SEPARATOR,
        MenuItem("❌ Exit", lambda icon, item: quit_app())
    )
    icon = Icon("QuickTask", create_image(), "Quick Task", menu)
    icon.run()

def quit_app(icon):
    stop_hotkey_listener()
    icon.stop()
    main_window.destroy()
    sys.exit()

@log_call
def show_reminder_window(task_id, task_name, task_due_date):
    global is_reminder_open

    print(f"[show_reminder_window] Opening reminder for task: {task_name} (due {task_due_date})")
    logger.info(f"[show_reminder_window] Opening reminder for task: {task_name} (due {task_due_date})")

    pending_reminders = due_queue.qsize()

    inst = TasksReminderWindow(task_id, task_name, task_due_date, callback=check_due_queue, pending_reminders=pending_reminders)
    window_manager.task_reminder_windows.append(inst)
    is_reminder_open = True

    def on_close():
        global is_reminder_open

        try:
            if not inst.user_action_taken:
                inst.snooze_task_hour()

            if inst in window_manager.task_reminder_windows:
                window_manager.task_reminder_windows.remove(inst)
        except ValueError:
            pass

        inst.hide_reminder_window()
        
    inst.protocol("WM_DELETE_WINDOW", on_close)
    inst.deiconify()
    inst.lift()
    inst.focus_force()
    inst.attributes('-topmost', True)
    inst.after(100, lambda: inst.attributes('-topmost', False))

@log_call
def show_main_window():
    main_window.deiconify()
    main_window.lift()
    main_window.focus_force()

@log_call
def check_due_queue():
    global is_reminder_open

    active_reminders = [inst for inst in window_manager.task_reminder_windows if inst.winfo_exists()]

    is_reminder_open = bool(active_reminders)

    print(f"[check_due_queue] is_reminder_open={is_reminder_open} due_queue size={due_queue.qsize()}")
    logger.info(f"[check_due_queue] is_reminder_open={is_reminder_open} due_queue size={due_queue.qsize()}")

    if not is_reminder_open and not due_queue.empty():
        task_id, task_name, task_due_date = due_queue.get()
        main_window.after(0, show_reminder_window, task_id, task_name, task_due_date)

@log_call
def check_for_due_tasks():
    while True:
        current_time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
        sql_connection = sqlite3.connect("tasks.db")
        connection_cursor = sql_connection.cursor()
        connection_cursor.execute(
            """
            SELECT id, name, due_date FROM tasks
            WHERE due_date IS NOT NULL
              AND status = 'open'
              AND notified = 0
              AND due_date <= ?
            ORDER BY due_date ASC
            """,
            (current_time_now,),
        )
        due_tasks = connection_cursor.fetchall()

        print(f"[check_for_due_tasks] Found {len(due_tasks)} tasks due.")
        logger.info(f"[check_for_due_tasks] Found {len(due_tasks)} tasks due.")

        for task_id, name, due_date in due_tasks:
            due_queue.put((task_id, name, due_date))
            connection_cursor.execute("UPDATE tasks SET notified = 1 WHERE id = ?", (task_id,))

        sql_connection.commit()
        sql_connection.close()

        check_due_queue()

        time.sleep(10)

def reset_notified_worker(interval_secs=30):
    while True:
        try:
            if is_reminder_open:

                print("[reset_notified_worker] Reminder is open, skipping reset.")
                logger.info("[reset_notified_worker] Reminder is open, skipping reset.")

                time.sleep(interval_secs)
                continue

            sql_connection = sqlite3.connect("tasks.db")
            connection_cursor = sql_connection.cursor()

            now = datetime.now().strftime("%Y-%m-%d %H:%M")

            print(f"[reset_notified_worker] Checking overdue tasks before {now}...")
            logger.info(f"[reset_notified_worker] Checking overdue tasks before {now}...")

            connection_cursor.execute(
                """
                SELECT id
                FROM tasks
                WHERE notified = 1
                  AND status = 'open'
                  AND due_date IS NOT NULL
                  AND due_date <= ?
                """,
                (now,)
            )

            tasks_to_reset = connection_cursor.fetchall()

            if tasks_to_reset:
                ids = [task[0] for task in tasks_to_reset]
                print(f"[reset_notified_worker] Found {len(ids)} tasks to reset.")
                logger.info(f"[reset_notified_worker] Found {len(ids)} tasks to reset.")

                placeholders = ",".join("?" for _ in ids)
                sql = f"UPDATE tasks SET notified = 0 WHERE id IN ({placeholders})"
                connection_cursor.execute(sql, ids)
                sql_connection.commit()

                print(f"[reset_notified_worker] Reset {len(ids)} tasks.")
                logger.info(f"[reset_notified_worker] Reset {len(ids)} tasks.")

            else:
                print(f"[reset_notified_worker] No overdue tasks to reset.")
                logger.info(f"[reset_notified_worker] No overdue tasks to reset.")

        except Exception as e:
            print(f"[reset_notified_worker] ERROR: {e}")
            logger.warning(f"[reset_notified_worker] ERROR: {e}")

        finally:
            try:
                sql_connection.close()
            except:
                pass

            time.sleep(interval_secs)

main_window = MainWindow()

def hotkey_action():
    if not stop_listening:
        main_window.show_task_window()

def hotkey_listener():
    global stop_listening

    keyboard.add_hotkey('ctrl+shift+space', hotkey_action, suppress=False, trigger_on_release=False)

    while not stop_listening:
        keyboard.wait('shift')

def stop_hotkey_listener():
    global stop_listening
    if not stop_listening:
        stop_listening = True
        keyboard.unhook_all_hotkeys()
        keyboard.press_and_release('shift')

init_db()

def start_background_threads():
    threading.Thread(target=check_for_due_tasks, daemon=True).start()
    threading.Thread(target=lambda: reset_notified_worker(30), daemon=True).start()
    threading.Thread(target=hotkey_listener, daemon=True).start()
    threading.Thread(target=setup_tray, daemon=True).start()



sv_ttk.set_theme("dark")

remote_version = main_window.get_remote_version()

if main_window.compare_versions(app_version, remote_version):
    answer = messagebox.askyesno("Update Available", "Do you want to update Tasker?")
    if answer:
        try:
            subprocess.Popen(["updater.exe"], shell=True)
        except Exception as e:
            print(f"Failed to run updater: {e}")
            logger.warning(f"Failed to run updater: {e}")
    else:
        pass

main_window.after(100, start_background_threads)
main_window.mainloop()