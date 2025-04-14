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


class TasksListWindow(tk.Toplevel): 

    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.callback = callback
        self.geometry("1000x700")
        self.title("Tasker - Reminder")
        self.resizable(False, False)
        self.iconbitmap("Assets\\favicon.ico")
        self.transient(None)
        font = ("Segoe UI", 10, "bold")

        self.tree = ttk.Treeview(self, columns=("ID", "Title", "Status", "Due Date"), show="headings", selectmode="extended")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Due Date", text="Due Date")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        self.mark_done_btn = tk.Button(self.button_frame, text="✅ Mark as Done", command=self.on_mark_done)
        self.mark_done_btn.pack(pady=20)

        self.mark_done_btn = tk.Button(self.button_frame, text="❌ Delete Task", command=self.on_delete)
        self.mark_done_btn.pack(pady=30)

        self.refresh_list = tk.Button(self.button_frame, text="🔃 Refresh", command=self.refresh_tree)
        self.refresh_list.pack(pady=40)

        self.refresh_tree()
    
    def get_task_list(self):
        conn = sqlite3.connect("tasks.db")
        c = conn.cursor()

        c.execute("SELECT id, name, status, due_date FROM tasks")
        tasks = c.fetchall()

        conn.close()
        return tasks
    
    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for task in self.get_task_list():
            self.tree.insert("", tk.END, values=task)

    def on_mark_done(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a task to mark as done.")
            return

        for item in selected_items:
            task_id = self.tree.item(item, "values")[0]
            self.mark_task_as_done(task_id)

        self.refresh_tree()

    def mark_task_as_done(self, task_id):
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET status = "complete" WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()

    def delete_task(self, task_id):
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()

    def on_delete(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a task to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected task(s)?")
        if not confirm:
            return

        for item in selected_items:
            task_id = self.tree.item(item, "values")[0]
            self.delete_task(task_id)

        self.refresh_tree()