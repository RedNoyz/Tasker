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

class MainWindow(tk.Tk): 

    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.callback = callback
        self.geometry("500x500")
        self.resizable(False, False)
        self.title("Tasker")
        self.focus()
        self.iconbitmap("Assets\\favicon.ico")

        font = ("Segoe UI", 10, "bold")

        self.grid_columnconfigure(0, weight=1, minsize=166)
        self.grid_columnconfigure(1, weight=1, minsize=166)
        self.grid_columnconfigure(2, weight=1, minsize=166)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0)
        self.grid_rowconfigure(5, weight=0)
        self.grid_rowconfigure(6, weight=0)

        self.hide_main_button = ttk.Button(self, text="Hide Main Window", command=self.hide_main_window)
        self.hide_main_button.grid(row=0, column=1, pady=10, padx=10)

        # tk.Label(self, text="Made by RedNoyz", font=("Segoe UI", 10)).grid(row=6, column=2, pady=(10, 0), sticky="s", padx=10)


    def hide_main_window(self):
        self.withdraw()