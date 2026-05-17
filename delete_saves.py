import os
import glob
import tkinter as tk
from pynput import keyboard as pynput_keyboard

SAVE_PATH = os.path.join(os.environ["LOCALAPPDATA"], "EscapeTheBackrooms", "Saved", "SaveGames")
current_keybind = [None]
listening = [False]

def get_save_files():
    if not os.path.exists(SAVE_PATH):
        return []
    all_sav_files = glob.glob(os.path.join(SAVE_PATH, "*.sav"))
    return [f for f in all_sav_files if os.path.basename(f).startswith("MULTIPLAYER") or os.path.basename(f).startswith("SINGLEPLAYER")]

def refresh_list():
    files = get_save_files()
    listbox.delete(0, tk.END)
    if files:
        for f in files:
            listbox.insert(tk.END, os.path.basename(f))
        if auto_delete.get():
            for f in files:
                os.remove(f)
    else:
        listbox.insert(tk.END, "No save files found.")
    root.after(1000, refresh_list)

def delete_saves():
    for f in get_save_files():
        os.remove(f)
    refresh_list_now()

def refresh_list_now():
    files = get_save_files()
    listbox.delete(0, tk.END)
    if files:
        for f in files:
            listbox.insert(tk.END, os.path.basename(f))
    else:
        listbox.insert(tk.END, "No save files found.")

def toggle_always_on_top():
    root.attributes("-topmost", always_on_top.get())

import ctypes

GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
WS_EX_LAYERED = 0x00080000

def get_hwnd():
    return ctypes.windll.user32.GetParent(root.winfo_id())

def enable_click_through():
    if click_through.get():
        hwnd = get_hwnd()
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT)

def disable_click_through():
    hwnd = get_hwnd()
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style & ~WS_EX_TRANSPARENT)

def toggle_click_through():
    if click_through.get():
        enable_click_through()
    else:
        disable_click_through()

def start_listening():
    listening[0] = True
    keybind_btn.config(text="Press any key...", bg="#555555")

def on_global_key(key):
    if listening[0]:
        try:
            key_name = key.name if hasattr(key, 'name') else key.char
        except:
            key_name = str(key)
        current_keybind[0] = key
        listening[0] = False
        root.after(0, lambda: keybind_btn.config(text="Set Keybind", bg="#2a2a2a"))
        root.after(0, lambda k=key_name: keybind_label.config(text=f"Current: {k}"))
    else:
        if current_keybind[0] is not None and key == current_keybind[0]:
            delete_saves()

root = tk.Tk()
root.title("Bog's ETB Save Deleter")
root.geometry("320x420")
root.resizable(False, False)
root.configure(bg="#1a1a1a")

root.iconbitmap("")

label = tk.Label(root, text="Escape the Backrooms", bg="#1a1a1a", fg="#aaaaaa", font=("Segoe UI", 10))
label.pack(pady=(14, 6))

frame = tk.Frame(root, bg="#2a2a2a", bd=0)
frame.pack(padx=16, fill="both", expand=True)

listbox = tk.Listbox(
    frame,
    bg="#2a2a2a",
    fg="#dddddd",
    font=("Segoe UI", 9),
    relief="flat",
    highlightthickness=0,
    selectbackground="#3a3a3a",
    borderwidth=0,
)
listbox.pack(fill="both", expand=True, padx=6, pady=6)

btn = tk.Button(
    root,
    text="Delete All Saves",
    command=delete_saves,
    bg="#c0392b",
    fg="white",
    activebackground="#e74c3c",
    activeforeground="white",
    font=("Segoe UI", 11, "bold"),
    relief="flat",
    padx=16,
    pady=8,
    cursor="hand2",
)
btn.pack(pady=(10, 4))

auto_delete = tk.BooleanVar()
chk = tk.Checkbutton(
    root,
    text="Auto-Delete  (only use for resetless IL's)",
    variable=auto_delete,
    bg="#1a1a1a",
    fg="#aaaaaa",
    activebackground="#1a1a1a",
    activeforeground="#ffffff",
    selectcolor="#1a1a1a",
    font=("Segoe UI", 9),
    cursor="hand2",
)
chk.pack(pady=(0, 2))

always_on_top = tk.BooleanVar()
chk_top = tk.Checkbutton(
    root,
    text="Always On Top",
    variable=always_on_top,
    command=toggle_always_on_top,
    bg="#1a1a1a",
    fg="#aaaaaa",
    activebackground="#1a1a1a",
    activeforeground="#ffffff",
    selectcolor="#1a1a1a",
    font=("Segoe UI", 9),
    cursor="hand2",
)
chk_top.pack(pady=(0, 2))

click_through = tk.BooleanVar()
chk_click = tk.Checkbutton(
    root,
    text="Ignore Mouse Cursor",
    variable=click_through,
    command=toggle_click_through,
    bg="#1a1a1a",
    fg="#aaaaaa",
    activebackground="#1a1a1a",
    activeforeground="#ffffff",
    selectcolor="#1a1a1a",
    font=("Segoe UI", 9),
    cursor="hand2",
)
chk_click.pack(pady=(0, 6))

def remove_keybind():
    current_keybind[0] = None
    keybind_label.config(text="Current: none")

keybind_frame = tk.Frame(root, bg="#1a1a1a")
keybind_frame.pack(pady=(0, 4))

keybind_btn = tk.Button(
    keybind_frame,
    text="Set Keybind",
    command=start_listening,
    bg="#2a2a2a",
    fg="#dddddd",
    activebackground="#3a3a3a",
    activeforeground="white",
    relief="flat",
    font=("Segoe UI", 9),
    cursor="hand2",
    padx=8,
    pady=4,
)
keybind_btn.pack(side="left", padx=(0, 6))

remove_keybind_btn = tk.Button(
    keybind_frame,
    text="Remove Keybind",
    command=remove_keybind,
    bg="#2a2a2a",
    fg="#dddddd",
    activebackground="#3a3a3a",
    activeforeground="white",
    relief="flat",
    font=("Segoe UI", 9),
    cursor="hand2",
    padx=8,
    pady=4,
)
remove_keybind_btn.pack(side="left")

keybind_label = tk.Label(root, text="Current: none", bg="#1a1a1a", fg="#666666", font=("Segoe UI", 8))
keybind_label.pack(pady=(0, 10))

listener = pynput_keyboard.Listener(on_press=on_global_key)
listener.daemon = True
listener.start()

root.bind("<FocusIn>", lambda e: disable_click_through())
root.bind("<FocusOut>", lambda e: enable_click_through())

refresh_list()
root.mainloop()
