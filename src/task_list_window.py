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
from utils.logger import log_call, logger


class TasksListWindow(tk.Toplevel): 

    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.callback = callback
        self.geometry("1000x700")
        self.title("Tasker - Reminder")
        self.resizable(False, False)
        self.transient(None)
        font = ("Segoe UI", 10, "bold")

        self.protocol("WM_DELETE_WINDOW", self.close_window)

        self.warning_shown = False

        def get_asset_path(relative_path):
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, relative_path)
            return os.path.join(os.path.abspath("."), relative_path)

        self.iconbitmap(get_asset_path("Assets/favicon.ico"))

        style = ttk.Style(self)

        style.configure("Treeview",
                        background="grey",
                        foreground="black",
                        fieldbackground="white")
        
        style.map("Treeview",
                  background=[('selected', 'lightblue')],
                  foreground=[('selected', 'black')])

        self.tree = ttk.Treeview(self, columns=("ID", "Title", "Status", "Notified", "Due Date"), show="headings", selectmode="extended")
        self.tree.heading("ID",       text="ID",       command=lambda: self.sort_by("ID", False))
        self.tree.heading("Title",    text="Title")
        self.tree.heading("Status",   text="Status")
        self.tree.heading("Notified", text="Notified")
        self.tree.heading("Due Date", text="Due Date", command=lambda: self.sort_by("Due Date", False))

        self.tree.column("ID",        width=50,  minwidth=50,  stretch=False, anchor=tk.CENTER)
        self.tree.column("Status",    width=80,  minwidth=80,  stretch=False, anchor=tk.CENTER)
        self.tree.column("Notified",    width=70,  minwidth=70,  stretch=False, anchor=tk.CENTER)
        self.tree.column("Due Date",  width=120, minwidth=120, stretch=False, anchor=tk.CENTER)
        self.tree.column("Title",     width=300, minwidth=150, stretch=True,  anchor=tk.W)

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.tree.bind("<Button-1>", self.on_tree_click, add="+")

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        self.mark_done_btn = tk.Button(self.button_frame, text="✅ Mark as Done", command=self.on_mark_done, bg="darkgreen")
        self.mark_done_btn.pack(pady=10)

        self.mark_done_btn = tk.Button(self.button_frame, text="❌ Delete Task", command=self.on_delete, bg="darkred")
        self.mark_done_btn.pack(pady=10)

        self.refresh_list_open = ttk.Button(self.button_frame, text="🔃 Show Open Tasks", command=self.refresh_tree)
        self.refresh_list_open.pack(pady=10)

        self.refresh_list_closed= ttk.Button(self.button_frame, text="🔃 Show Complete Tasks", command=self.refresh_closed_tasks)
        self.refresh_list_closed.pack(pady=10)

        self.refresh_list_all = ttk.Button(self.button_frame, text="🔃 Show All Tasks", command=self.refresh_all_tasks)
        self.refresh_list_all.pack(pady=10)

        self.bind("<Control-a>", self.select_all)

        self.refresh_tree()
    
    def get_task_list(self):
        sql_connection = sqlite3.connect("tasks.db")
        connection_cursor = sql_connection.cursor()

        connection_cursor.execute("SELECT id, name, status, notified, due_date FROM tasks WHERE status = 'open' ORDER BY due_date ASC")
        rows = connection_cursor.fetchall()

        sql_connection.close()
        tasks = [
            (task_id, name, status, 'Yes' if notified else 'No', due_date)
            for task_id, name, status, notified, due_date in rows]
        return tasks
    
    @log_call
    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for task in self.get_task_list():
            self.tree.insert("", tk.END, values=task)

    @log_call
    def on_mark_done(self):
        selected_items = self.tree.selection()
        if not selected_items:
            if not self.warning_shown:
                self.warning_shown = True
                messagebox.showwarning("No Selection", "Please select a task to mark as done.", parent=self)
                self.warning_shown = False
            return

        for item in selected_items:
            task_id = self.tree.item(item, "values")[0]
            self.mark_task_as_done(task_id)

        self.refresh_tree()

    @log_call
    def mark_task_as_done(self, task_id):
        sql_connection = sqlite3.connect('tasks.db')
        connection_cursor = sql_connection.cursor()
        connection_cursor.execute('UPDATE tasks SET status = "complete", notified = 1 WHERE id = ?', (task_id,))
        sql_connection.commit()
        sql_connection.close()

    @log_call
    def delete_task(self, task_id):
        sql_connection = sqlite3.connect('tasks.db')
        connection_cursor = sql_connection.cursor()
        connection_cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        sql_connection.commit()
        sql_connection.close()

    @log_call
    def on_delete(self):
        selected_items = self.tree.selection()
        if not selected_items:
            if not self.warning_shown:
                self.warning_shown = True
                messagebox.showwarning("No Selection", "Please select a task to delete.", parent=self)
                self.warning_shown = False
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected task(s)?")
        if not confirm:
            return

        for item in selected_items:
            task_id = self.tree.item(item, "values")[0]
            self.delete_task(task_id)

        self.refresh_tree()
    
    @log_call
    def refresh_all_tasks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for task in self.get_all_tasks_list():
            self.tree.insert("", tk.END, values=task)

    @log_call
    def get_all_tasks_list(self):
        sql_connection = sqlite3.connect("tasks.db")
        connection_cursor = sql_connection.cursor()

        connection_cursor.execute("SELECT id, name, status, notified, due_date FROM tasks ORDER BY due_date ASC")
        rows = connection_cursor.fetchall()
        sql_connection.close()

        tasks = [
            (task_id, name, status, 'Yes' if notified else 'No', due_date)
            for task_id, name, status, notified, due_date in rows]

        return tasks
    
    @log_call
    def refresh_closed_tasks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for task in self.get_closed_tasks_list():
            self.tree.insert("", tk.END, values=task)

    @log_call
    def get_closed_tasks_list(self):
        sql_connection = sqlite3.connect("tasks.db")
        connection_cursor = sql_connection.cursor()

        connection_cursor.execute("SELECT id, name, status, notified, due_date FROM tasks WHERE status = 'complete' ORDER BY due_date ASC")
        rows = connection_cursor.fetchall()
        sql_connection.close()

        tasks = [
            (task_id, name, status, 'Yes' if notified else 'No', due_date)
            for task_id, name, status, notified, due_date in rows]
        
        return tasks
    
    @log_call
    def on_tree_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            for sel in self.tree.selection():
                self.tree.selection_remove(sel)
    @log_call
    def select_all(self, event):
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    @log_call
    def sort_by(self, column, descending):
        data = [(self.tree.set(item, column), item) for item in self.tree.get_children('')]

        if column == "ID":
            keyfunc = lambda t: int(t[0])
        elif column == "Due Date":
            keyfunc = lambda t: datetime.strptime(t[0], "%Y-%m-%d %H:%M")
        else:
            keyfunc = lambda t: t[0].lower()

        data.sort(key=keyfunc, reverse=descending)

        for index, (_, item) in enumerate(data):
            self.tree.move(item, '', index)

        self.tree.heading(
            column,
            text=column,
            command=lambda: self.sort_by(column, not descending)
        )

    @log_call
    def close_window(self):
        self.destroy()
