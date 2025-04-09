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
        self.iconbitmap("favicon.ico")

        font = ("Segoe UI", 10, "bold")

        self.hide_main_button = ttk.Button(self, text="Hide Main Window", command=self.hide_main_window)
        self.hide_main_button.grid(row=1, column=0, pady=10, padx=10)

    def hide_main_window(self):
        self.withdraw()