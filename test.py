import tkinter as tk

def minimize():
    root.iconify()

def close():
    root.destroy()

def custom_action():
    print("Toolbar button clicked!")

def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def on_motion(event):
    x = (event.x_root - root.x)
    y = (event.y_root - root.y)
    root.geometry(f"+{x}+{y}")

root = tk.Tk()
root.overrideredirect(True)  # Remove native title bar
root.geometry("500x300")

# Custom title bar
title_bar = tk.Frame(root, bg="#2e2e2e", relief='raised', bd=0, height=30)
title_bar.pack(fill=tk.X)

# Drag support
title_bar.bind("<ButtonPress-1>", start_move)
title_bar.bind("<B1-Motion>", on_motion)

# Custom button
toolbar_button = tk.Button(title_bar, text="🔔", command=custom_action, bg="#2e2e2e", fg="white", bd=0)
toolbar_button.pack(side=tk.LEFT, padx=5)

# Spacer
title = tk.Label(title_bar, text="Custom Toolbar", bg="#2e2e2e", fg="white")
title.pack(side=tk.LEFT, padx=10)

# Minimize and close buttons
btn_min = tk.Button(title_bar, text="_", command=minimize, bg="#2e2e2e", fg="white", bd=0)
btn_min.pack(side=tk.RIGHT, padx=5)

btn_close = tk.Button(title_bar, text="✕", command=close, bg="#2e2e2e", fg="white", bd=0)
btn_close.pack(side=tk.RIGHT, padx=5)

# Main content
main_frame = tk.Frame(root, bg="white")
main_frame.pack(fill=tk.BOTH, expand=True)

tk.Label(main_frame, text="Main content here").pack(pady=50)

root.mainloop()
