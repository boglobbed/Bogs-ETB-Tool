import os
import sys
import string
import ctypes
import shutil
import glob
import tkinter as tk
from tkinter import ttk
from pynput import keyboard as pynput_keyboard

class CURSORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_ulong),
        ("flags", ctypes.c_ulong),
        ("hCursor", ctypes.c_void_p),
        ("ptScreenPos", ctypes.wintypes.POINT)
    ]

if not ctypes.windll.shell32.IsUserAnAdmin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

def find_game_path():
    rel_paths = [
        r"SteamLibrary\steamapps\common\EscapeTheBackrooms",
        r"Steam\steamapps\common\EscapeTheBackrooms",
        r"steamapps\common\EscapeTheBackrooms",
    ]
    for letter in string.ascii_uppercase:
        for rel in rel_paths:
            candidate = os.path.join(f"{letter}:\\", rel)
            if os.path.exists(candidate):
                return candidate
    return None

GAME_PATH = find_game_path()
SAVE_PATH = os.path.join(os.environ["LOCALAPPDATA"], "EscapeTheBackrooms", "Saved", "SaveGames")

current_keybind = [None]
listening = [False]

def launch_etb():
    os.startfile(r"steam://rungameid/1943950")

def get_exe_dir():
    return os.path.dirname(os.path.abspath(__file__))

def get_versions_dir():
    return os.path.join(get_exe_dir(), "versions")

def get_current_version():
    path = os.path.join(get_exe_dir(), "current_version.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read().strip()
    return None

def set_current_version(name):
    path = os.path.join(get_exe_dir(), "current_version.txt")
    with open(path, "w") as f:
        f.write(name)

def get_versions():
    versions_dir = get_versions_dir()
    if not os.path.exists(versions_dir):
        try:
            os.makedirs(versions_dir)
        except Exception:
            return []
        return []
    current = get_current_version()
    order_path = os.path.join(get_exe_dir(), "versions_order.txt")
    
    try:
        all_versions = [f for f in os.listdir(versions_dir) if os.path.isdir(os.path.join(versions_dir, f)) and f != current]
    except Exception:
        return []

    if os.path.exists(order_path):
        try:
            with open(order_path, "r") as f:
                order = [line.strip() for line in f.readlines()]
            ordered = [v for v in order if v in all_versions]
            unordered = [v for v in all_versions if v not in ordered]
            return ordered + unordered
        except Exception:
            return all_versions
    return all_versions

def save_order():
    versions = []
    for i in range(version_listbox.size()):
        item = version_listbox.get(i)
        if item != "No versions found.":
            versions.append(item)
    current = get_current_version()
    if current:
        versions.insert(0, current)
    with open(os.path.join(get_exe_dir(), "versions_order.txt"), "w") as f:
        f.write("\n".join(versions))

def move_up():
    selected = version_listbox.curselection()
    if not selected or selected[0] == 0:
        return
    idx = selected[0]
    val = version_listbox.get(idx)
    version_listbox.delete(idx)
    version_listbox.insert(idx - 1, val)
    version_listbox.selection_set(idx - 1)
    save_order()

def move_down():
    selected = version_listbox.curselection()
    if not selected or selected[0] == version_listbox.size() - 1:
        return
    idx = selected[0]
    val = version_listbox.get(idx)
    version_listbox.delete(idx)
    version_listbox.insert(idx + 1, val)
    version_listbox.selection_set(idx + 1)
    save_order()

def get_save_files():
    if not os.path.exists(SAVE_PATH):
        return []
    all_sav_files = glob.glob(os.path.join(SAVE_PATH, "*.sav"))
    return [f for f in all_sav_files if os.path.basename(f).startswith("MULTIPLAYER") or os.path.basename(f).startswith("SINGLEPLAYER")]

def show_save_deleter():
    version_frame.pack_forget()
    mod_frame.pack_forget()
    keybind_frame_tool.pack_forget()
    save_frame.pack(fill="both", expand=True)
    subtitle_label.config(text="Save File Deleter")
    refresh_saves_now()

def show_version_switcher():
    save_frame.pack_forget()
    mod_frame.pack_forget()
    keybind_frame_tool.pack_forget()
    version_frame.pack(fill="both", expand=True)
    subtitle_label.config(text="Version Switcher")
    refresh_versions_now()

def show_mod_manager():
    save_frame.pack_forget()
    version_frame.pack_forget()
    keybind_frame_tool.pack_forget()
    mod_frame.pack(fill="both", expand=True)
    subtitle_label.config(text="Mod Manager")

def show_keybind_editor():
    save_frame.pack_forget()
    version_frame.pack_forget()
    mod_frame.pack_forget()
    keybind_frame_tool.pack(fill="both", expand=True)
    subtitle_label.config(text="Keybind Editor")
    refresh_keybinds_now()

def on_mode_change(event):
    if mode_var.get() == "Save File Deleter":
        show_save_deleter()
    elif mode_var.get() == "Version Switcher":
        show_version_switcher()
    elif mode_var.get() == "Mod Manager":
        show_mod_manager()
    else:
        show_keybind_editor()

def delete_saves():
    for f in get_save_files():
        try:
            os.remove(f)
        except Exception:
            pass
    refresh_saves_now()

def refresh_saves_now():
    save_listbox.delete(0, tk.END)
    files = get_save_files()
    if files:
        for f in files:
            save_listbox.insert(tk.END, os.path.basename(f))
    else:
        save_listbox.insert(tk.END, "No save files found.")

def refresh_saves():
    if mode_var.get() == "Save File Deleter":
        refresh_saves_now()
    root.after(1000, refresh_saves)

ignore_mouse_checkbox = [None]
app_has_focus = [True]
current_transparency_state = [False]

def toggle_always_on_top():
    root.attributes("-topmost", always_on_top.get())
    if settings_popup[0] and tk.Toplevel.winfo_exists(settings_popup[0]):
        settings_popup[0].attributes("-topmost", always_on_top.get())
    
    if ignore_mouse_checkbox[0] and ignore_mouse_checkbox[0].winfo_exists():
        if always_on_top.get():
            ignore_mouse_checkbox[0].config(state="normal", fg="#aaaaaa")
        else:
            ignore_mouse_checkbox[0].config(state="disabled", fg="#444444")
            
    if not always_on_top.get() and click_through.get():
        click_through.set(False)
        disable_click_through()

def enable_click_through():
    if not current_transparency_state[0]:
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x00080000 | 0x00000020)
        current_transparency_state[0] = True

def disable_click_through():
    if current_transparency_state[0]:
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, style & ~0x00000020)
        current_transparency_state[0] = False

def toggle_click_through():
    if not click_through.get():
        disable_click_through()

def on_app_focus_in(event):
    app_has_focus[0] = True
    disable_click_through()

def on_app_focus_out(event):
    app_has_focus[0] = False

def monitor_cursor_state():
    if click_through.get() and always_on_top.get() and not app_has_focus[0] and not listening[0]:
        ci = CURSORINFO()
        ci.cbSize = ctypes.sizeof(CURSORINFO)
        if ctypes.windll.user32.GetCursorInfo(ctypes.byref(ci)):
            if ci.flags == 1:
                disable_click_through()
            else:
                enable_click_through()
    else:
        if app_has_focus[0] or not click_through.get():
            disable_click_through()
            
    root.after(100, monitor_cursor_state)

def start_listening():
    listening[0] = True
    keybind_btn.config(text="Press any key...", bg="#555555")

def remove_keybind():
    current_keybind[0] = None
    keybind_label.config(text="Current: none")

def on_global_key(key):
    if listening[0]:
        try:
            key_name = key.name if hasattr(key, 'name') else key.char
        except Exception:
            key_name = str(key)
        current_keybind[0] = key
        listening[0] = False
        root.after(0, lambda: keybind_btn.config(text="Set Keybind", bg="#2a2a2a"))
        root.after(0, lambda k=key_name: keybind_label.config(text=f"Current: {k}"))
    else:
        if current_keybind[0] is not None and key == current_keybind[0]:
            delete_saves()

def refresh_versions_now():
    selected = version_listbox.curselection()
    selected_name = version_listbox.get(selected[0]) if selected else None
    
    version_listbox.delete(0, tk.END)
    versions = get_versions()
    if versions:
        for v in versions:
            version_listbox.insert(tk.END, v)
        if selected_name and selected_name in versions:
            idx = versions.index(selected_name)
            version_listbox.selection_set(idx)
    else:
        version_listbox.insert(tk.END, "No versions found.")

def refresh_versions():
    if mode_var.get() == "Version Switcher":
        try:
            refresh_versions_now()
        except Exception:
            pass
    root.after(2000, refresh_versions)

def switch_version():
    global GAME_PATH
    if not GAME_PATH:
        from tkinter import filedialog, messagebox
        messagebox.showwarning("Game Not Found", "Could not find your EscapeTheBackrooms install.\nPlease select the game folder manually.")
        chosen = filedialog.askdirectory(title="Select EscapeTheBackrooms Folder")
        if chosen:
            GAME_PATH = chosen
        else:
            version_status.config(text="No game folder selected.", fg="#e74c3c")
            return

    selection = version_listbox.curselection()
    if not selection:
        version_status.config(text="No version selected.", fg="#e74c3c")
        return
    version_name = version_listbox.get(selection[0])
    if version_name == "No versions found.":
        return
    version_path = os.path.join(get_versions_dir(), version_name)
    try:
        all_files = []
        for item in os.listdir(version_path):
            if item == "Engine":
                continue
            src = os.path.join(version_path, item)
            if os.path.isdir(src):
                for root_dir, dirs, files in os.walk(src):
                    for file in files:
                        all_files.append((os.path.join(root_dir, file), item, os.path.relpath(root_dir, src)))
            else:
                all_files.append((src, item, None))

        total = len(all_files)
        progress_bar["maximum"] = total
        progress_bar["value"] = 0

        for i, (src_file, item, rel) in enumerate(all_files):
            dst_base = os.path.join(GAME_PATH, item)
            if rel and rel != ".":
                dst_dir = os.path.join(dst_base, rel)
            else:
                dst_dir = dst_base if rel is None else dst_base
            os.makedirs(dst_dir if rel is not None else os.path.dirname(dst_base), exist_ok=True)
            dst_file = os.path.join(dst_dir, os.path.basename(src_file)) if rel is not None else dst_base
            try:
                shutil.copy2(src_file, dst_file)
            except Exception:
                pass
            progress_bar["value"] = i + 1
            root.update_idletasks()

        set_current_version(version_name)
        current_ver_label.config(text=f"Current: {version_name}")
        version_status.config(text=f"Switched to {version_name}!", fg="#2ecc71")
        progress_bar["value"] = 0
        if auto_launch.get():
            launch_etb()
    except Exception as e:
        version_status.config(text=f"Error: {e}", fg="#e74c3c")

def rename_version():
    selection = version_listbox.curselection()
    if not selection:
        return
    old_name = version_listbox.get(selection[0])
    if old_name == "No versions found.":
        return

    popup = tk.Toplevel(root)
    popup.title("Rename Version")
    popup.geometry("260x100")
    popup.configure(bg="#1a1a1a")
    popup.resizable(False, False)
    popup.transient(root)

    tk.Label(popup, text=f"Rename '{old_name}' to:", bg="#1a1a1a", fg="#aaaaaa", font=("Segoe UI", 9)).pack(pady=(12, 4))

    entry = tk.Entry(popup, font=("Segoe UI", 9), bg="#2a2a2a", fg="#dddddd", insertbackground="white", relief="flat")
    entry.insert(0, old_name)
    entry.pack(padx=16, fill="x")
    entry.focus()

    def do_rename():
        new_name = entry.get().strip()
        if new_name and new_name != old_name:
            old_path = os.path.join(get_versions_dir(), old_name)
            new_path = os.path.join(get_versions_dir(), new_name)
            os.rename(old_path, new_path)
        popup.destroy()
        refresh_versions_now()

    entry.bind("<Return>", lambda e: do_rename())
    tk.Button(popup, text="Rename", command=do_rename, bg="#c0392b", fg="white", relief="flat", font=("Segoe UI", 9), cursor="hand2", padx=8, pady=4).pack(pady=8)

def delete_version():
    selection = version_listbox.curselection()
    if not selection:
        return
    version_name = version_listbox.get(selection[0])
    if version_name == "No versions found.":
        return

    popup = tk.Toplevel(root)
    popup.title("Delete Version")
    popup.geometry("260x100")
    popup.configure(bg="#1a1a1a")
    popup.resizable(False, False)
    popup.transient(root)

    tk.Label(popup, text=f"Delete '{version_name}'? This cannot be undone.", bg="#1a1a1a", fg="#aaaaaa", font=("Segoe UI", 9), wraplength=230).pack(pady=(12, 8))

    btn_frame = tk.Frame(popup, bg="#1a1a1a")
    btn_frame.pack()

    def do_delete():
        shutil.rmtree(os.path.join(get_versions_dir(), version_name))
        popup.destroy()
        refresh_versions_now()

    tk.Button(btn_frame, text="Delete", command=do_delete, bg="#c0392b", fg="white", relief="flat", font=("Segoe UI", 9), cursor="hand2", padx=8, pady=4).pack(side="left", padx=(0, 6))
    tk.Button(btn_frame, text="Cancel", command=popup.destroy, bg="#2a2a2a", fg="#dddddd", relief="flat", font=("Segoe UI", 9), cursor="hand2", padx=8, pady=4).pack(side="left")

settings_popup = [None]

def open_settings():
    if settings_popup[0] is not None and tk.Toplevel.winfo_exists(settings_popup[0]):
        settings_popup[0].lift()
        settings_popup[0].focus_force()
        return

    popup = tk.Toplevel(root)
    popup.title("Settings")
    popup.geometry("220x95")
    popup.configure(bg="#1a1a1a")
    popup.resizable(False, False)
    
    popup.transient(root)
    popup.attributes("-topmost", always_on_top.get())
    
    settings_popup[0] = popup

    root.update_idletasks()
    rx = root.winfo_x()
    ry = root.winfo_y()
    rw = root.winfo_width()
    popup.geometry(f"220x95+{rx + rw - 230}+{ry + 36}")

    inner = tk.Frame(popup, bg="#1a1a1a")
    inner.pack(padx=12, pady=10, fill="both", expand=True)

    tk.Checkbutton(
        inner, text="Always On Top",
        variable=always_on_top, command=toggle_always_on_top,
        bg="#1a1a1a", fg="#aaaaaa",
        activebackground="#1a1a1a", activeforeground="#ffffff",
        selectcolor="#1a1a1a", font=("Segoe UI", 9), cursor="hand2"
    ).pack(anchor="w", pady=(0, 4))

    init_state = "normal" if always_on_top.get() else "disabled"
    init_color = "#aaaaaa" if always_on_top.get() else "#444444"

    ignore_mouse_checkbox[0] = tk.Checkbutton(
        inner, text="Ignore Mouse Cursor",
        variable=click_through, command=toggle_click_through,
        bg="#1a1a1a", fg=init_color,
        activebackground="#1a1a1a", activeforeground="#ffffff",
        selectcolor="#1a1a1a", font=("Segoe UI", 9), cursor="hand2",
        state=init_state, disabledforeground="#444444"
    )
    ignore_mouse_checkbox[0].pack(anchor="w")

root = tk.Tk()
root.title("Bog's ETB Tool")
root.geometry("320x520")
root.resizable(False, False)
root.configure(bg="#1a1a1a")

root.bind("<FocusIn>", on_app_focus_in)
root.bind("<FocusOut>", on_app_focus_out)

mode_var = tk.StringVar(value="Save File Deleter")
mode_dropdown = ttk.Combobox(root, textvariable=mode_var, values=["Save File Deleter", "Version Switcher", "Mod Manager", "Keybind Editor"], state="readonly", font=("Segoe UI", 9), width=22)

style = ttk.Style()
style.theme_use("clam")
style.configure("red.Horizontal.TProgressbar", troughcolor="#2a2a2a", background="#c0392b", bordercolor="#1a1a1a", lightcolor="#c0392b", darkcolor="#c0392b")
style.configure("TCombobox", fieldbackground="#2a2a2a", background="#2a2a2a", foreground="#dddddd", selectbackground="#2a2a2a", selectforeground="#dddddd", arrowcolor="#dddddd")
style.map("TCombobox", fieldbackground=[("readonly", "#2a2a2a")], selectbackground=[("readonly", "#2a2a2a")], selectforeground=[("readonly", "#dddddd")])

auto_delete = tk.BooleanVar()
always_on_top = tk.BooleanVar()
click_through = tk.BooleanVar()

top_bar = tk.Frame(root, bg="#1a1a1a")
top_bar.pack(fill="x", pady=(10, 0))

title_label = tk.Label(top_bar, text="Escape the Backrooms", bg="#1a1a1a", fg="#aaaaaa", font=("Segoe UI", 10))
title_label.pack(side="left", padx=(10, 0))

cog_canvas = tk.Canvas(top_bar, width=24, height=24, bg="#1a1a1a", highlightthickness=0, borderwidth=0, cursor="hand2")
cog_canvas.pack(side="right", padx=(0, 12))

def draw_industrial_gear(color="#666666"):
    cog_canvas.delete("all")
    cog_canvas.create_oval(5, 5, 19, 19, outline=color, width=2)
    cog_canvas.create_oval(9, 9, 15, 15, outline=color, width=1.5)
    teeth_coords = [
        (10, 1, 14, 5), (10, 19, 14, 23), (1, 10, 5, 14), (19, 10, 23, 14),
        (4, 4, 7, 7), (17, 4, 20, 7), (4, 17, 7, 20), (17, 17, 20, 20)
    ]
    for x1, y1, x2, y2 in teeth_coords:
        cog_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

cog_canvas.bind("<Enter>", lambda e: draw_industrial_gear("#dddddd"))
cog_canvas.bind("<Leave>", lambda e: draw_industrial_gear("#666666"))
cog_canvas.bind("<Button-1>", lambda e: open_settings())
draw_industrial_gear()

mode_dropdown.pack(pady=(4, 4))
mode_dropdown.bind("<<ComboboxSelected>>", on_mode_change)

subtitle_label = tk.Label(root, text="Save File Deleter", bg="#1a1a1a", fg="#666666", font=("Segoe UI", 8))
subtitle_label.pack(pady=(0, 4))

save_frame = tk.Frame(root, bg="#1a1a1a")
save_frame.pack(fill="both", expand=True)

save_list_frame = tk.Frame(save_frame, bg="#2a2a2a")
save_list_frame.pack(padx=16, fill="both", expand=True)

save_listbox = tk.Listbox(save_list_frame, bg="#2a2a2a", fg="#dddddd", font=("Segoe UI", 9), relief="flat", highlightthickness=0, selectbackground="#3a3a3a", borderwidth=0)
save_listbox.pack(fill="both", expand=True, padx=6, pady=6)

delete_btn = tk.Button(save_frame, text="Delete All Saves", command=delete_saves, bg="#c0392b", fg="white", activebackground="#e74c3c", activeforeground="white", font=("Segoe UI", 11, "bold"), relief="flat", padx=16, pady=8, cursor="hand2")
delete_btn.pack(pady=(10, 2))

auto_delete_checkbox = tk.Checkbutton(
    save_frame, text="Auto-Delete  (resetless ILs only)",
    variable=auto_delete,
    bg="#1a1a1a", fg="#aaaaaa",
    activebackground="#1a1a1a", activeforeground="#ffffff",
    selectcolor="#1a1a1a", font=("Segoe UI", 9), cursor="hand2"
)
auto_delete_checkbox.pack(pady=(0, 6))

keybind_frame = tk.Frame(save_frame, bg="#1a1a1a")
keybind_frame.pack(pady=(0, 4))

keybind_btn = tk.Button(keybind_frame, text="Set Keybind", command=start_listening, bg="#2a2a2a", fg="#dddddd", activebackground="#3a3a3a", activeforeground="white", relief="flat", font=("Segoe UI", 9), cursor="hand2", padx=8, pady=4)
keybind_btn.pack(side="left", padx=(0, 6))

remove_keybind_btn = tk.Button(keybind_frame, text="Remove Keybind", command=remove_keybind, bg="#2a2a2a", fg="#dddddd", activebackground="#3a3a3a", activeforeground="white", relief="flat", font=("Segoe UI", 9), cursor="hand2", padx=8, pady=4)
remove_keybind_btn.pack(side="left")

keybind_label = tk.Label(save_frame, text="Current: none", bg="#1a1a1a", fg="#666666", font=("Segoe UI", 8))
keybind_label.pack(pady=(0, 10))

version_frame = tk.Frame(root, bg="#1a1a1a")

current_ver = get_current_version()
current_ver_label = tk.Label(version_frame, text=f"Current: {current_ver if current_ver else 'Unknown'}", bg="#1a1a1a", fg="#666666", font=("Segoe UI", 8))
current_ver_label.pack(pady=(0, 4))

ver_list_container = tk.Frame(version_frame, bg="#1a1a1a")
ver_list_container.pack(padx=16, fill="both", expand=True)

ver_list_frame = tk.Frame(ver_list_container, bg="#2a2a2a")
ver_list_frame.pack(side="left", fill="both", expand=True)

version_listbox = tk.Listbox(ver_list_frame, bg="#2a2a2a", fg="#dddddd", font=("Segoe UI", 9), relief="flat", highlightthickness=0, selectbackground="#c0392b", selectforeground="white", borderwidth=0)
version_listbox.pack(fill="both", expand=True, padx=6, pady=6)

arrow_frame = tk.Frame(ver_list_container, bg="#1a1a1a")
arrow_frame.pack(side="left", padx=(6, 0), pady=6)

up_btn = tk.Button(arrow_frame, text="▲", command=move_up, bg="#2a2a2a", fg="#dddddd", activebackground="#3a3a3a", activeforeground="white", relief="flat", font=("Segoe UI", 9), cursor="hand2", width=2)
up_btn.pack(pady=(0, 4))

down_btn = tk.Button(arrow_frame, text="▼", command=move_down, bg="#2a2a2a", fg="#dddddd", activebackground="#3a3a3a", activeforeground="white", relief="flat", font=("Segoe UI", 9), cursor="hand2", width=2)
down_btn.pack()

switch_btn = tk.Button(version_frame, text="Switch Version", command=switch_version, bg="#c0392b", fg="white", activebackground="#e74c3c", activeforeground="white", font=("Segoe UI", 11, "bold"), relief="flat", padx=16, pady=8, cursor="hand2")
switch_btn.pack(pady=(10, 4))

auto_launch = tk.BooleanVar()
chk_auto_launch = tk.Checkbutton(version_frame, text="Auto-Launch after switch", variable=auto_launch, bg="#1a1a1a", fg="#aaaaaa", activebackground="#1a1a1a", activeforeground="#ffffff", selectcolor="#1a1a1a", font=("Segoe UI", 9), cursor="hand2")
chk_auto_launch.pack(pady=(0, 4))

ver_btn_frame = tk.Frame(version_frame, bg="#1a1a1a")
ver_btn_frame.pack(pady=(0, 4))

rename_btn = tk.Button(ver_btn_frame, text="Rename", command=rename_version, bg="#2a2a2a", fg="#dddddd", activebackground="#3a3a3a", activeforeground="white", relief="flat", font=("Segoe UI", 9), cursor="hand2", padx=8, pady=4)
rename_btn.pack(side="left", padx=(0, 6))

del_ver_btn = tk.Button(ver_btn_frame, text="Delete Version", command=delete_version, bg="#2a2a2a", fg="#dddddd", activebackground="#3a3a3a", activeforeground="white", relief="flat", font=("Segoe UI", 9), cursor="hand2", padx=8, pady=4)
del_ver_btn.pack(side="left")

open_folder_btn = tk.Button(version_frame, text="Open Versions Folder", command=lambda: os.startfile(get_versions_dir()), bg="#2a2a2a", fg="#dddddd", activebackground="#3a3a3a", activeforeground="white", relief="flat", font=("Segoe UI", 9), cursor="hand2", padx=8, pady=4)
open_folder_btn.pack(pady=(2, 0))

progress_bar = ttk.Progressbar(version_frame, style="red.Horizontal.TProgressbar", orient="horizontal", length=288, mode="determinate")
progress_bar.pack(pady=(8, 4))

version_status = tk.Label(version_frame, text="Select a version to switch to.", bg="#1a1a1a", fg="#666666", font=("Segoe UI", 8), wraplength=290)
version_status.pack(pady=(0, 10))

mod_frame = tk.Frame(root, bg="#1a1a1a")

def get_mods_path():
    path = os.path.join(get_exe_dir(), "mods_path.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read().strip()
    return None

def save_mods_path(p):
    with open(os.path.join(get_exe_dir(), "mods_path.txt"), "w") as f:
        f.write(p)

def pick_mods_folder():
    from tkinter import filedialog
    game = GAME_PATH or ""
    paks_path = os.path.join(game, "EscapeTheBackrooms", "Content", "Paks")
    folder = filedialog.askdirectory(title="Select your mods folder inside Paks", initialdir=paks_path if os.path.exists(paks_path) else "/")
    if folder:
        save_mods_path(folder)
        mods_path_label.config(text=f"Mods folder: ...{folder[-30:]}")
        refresh_mods()

def get_mod_files():
    path = get_mods_path()
    if not path or not os.path.exists(path):
        return []
    return [f for f in os.listdir(path) if f.endswith(".pak") or f.endswith(".pak.disabled")]

def refresh_mods():
    mod_listbox.delete(0, tk.END)
    files = get_mod_files()
    if files:
        for f in files:
            mod_listbox.insert(tk.END, f)
            if f.endswith(".disabled"):
                mod_listbox.itemconfig(tk.END, fg="#666666")
    else:
        mod_listbox.insert(tk.END, "No mods found.")

def toggle_mod():
    selection = mod_listbox.curselection()
    if not selection:
        return
    mod_name = mod_listbox.get(selection[0])
    if mod_name == "No mods found.":
        return
    path = get_mods_path()
    src = os.path.join(path, mod_name)
    if mod_name.endswith(".pak.disabled"):
        dst = os.path.join(path, mod_name[:-9])
    else:
        dst = os.path.join(path, mod_name + ".disabled")
    os.rename(src, dst)
    refresh_mods()

def delete_mod():
    selection = mod_listbox.curselection()
    if not selection:
        return
    mod_name = mod_listbox.get(selection[0])
    if mod_name == "No mods found.":
        return

    popup = tk.Toplevel(root)
    popup.title("Delete Mod")
    popup.geometry("260x100")
    popup.configure(bg="#1a1a1a")
    popup.resizable(False, False)
    popup.transient(root)

    tk.Label(popup, text=f"Delete '{mod_name}'? This cannot be undone.", bg="#1a1a1a", fg="#aaaaaa", font=("Segoe UI", 9), wraplength=230).pack(pady=(12, 8))

    btn_frame = tk.Frame(popup, bg="#1a1a1a")
    btn_frame.pack()

    def do_delete():
        os.remove(os.path.join(get_mods_path(), mod_name))
        popup.destroy()
        refresh_mods()

    tk.Button(btn_frame, text="Delete", command=do_delete, bg="#c0392b", fg="white", relief="flat", font=("Segoe UI", 9), cursor="hand2", padx=8, pady=4).pack(side="left", padx=(0, 6))
    tk.Button(btn_frame, text="Cancel", command=popup.destroy, bg="#2a2a2a", fg="#dddddd", relief="flat", font=("Segoe UI", 9), cursor="hand2", padx=8, pady=4).pack(side="left")

saved_path = get_mods_path()
mods_path_label = tk.Label(mod_frame, text=f"Mods folder: ...{saved_path[-30:]}" if saved_path else "No mods folder selected.", bg="#1a1a1a", fg="#666666", font=("Segoe UI", 8), wraplength=290)
mods_path_label.pack(pady=(4, 4))

pick_btn = tk.Button(mod_frame, text="Select Mods Folder", command=pick_mods_folder, bg="#2a2a2a", fg="#dddddd", activebackground="#3a3a3a", activeforeground="white", relief="flat", font=("Segoe UI", 9), cursor="hand2", padx=8, pady=4)
pick_btn.pack(pady=(0, 6))

mod_list_frame = tk.Frame(mod_frame, bg="#2a2a2a")
mod_list_frame.pack(padx=16, fill="both", expand=True)

mod_listbox = tk.Listbox(mod_list_frame, bg="#2a2a2a", fg="#dddddd", font=("Segoe UI", 9), relief="flat", highlightthickness=0, selectbackground="#c0392b", selectforeground="white", borderwidth=0)
mod_listbox.pack(fill="both", expand=True, padx=6, pady=6)

mod_status = tk.Label(mod_frame, text="Grey = disabled, White = enabled.", bg="#1a1a1a", fg="#666666", font=("Segoe UI", 8))
mod_status.pack(pady=(6, 4))

mod_btn_frame = tk.Frame(mod_frame, bg="#1a1a1a")
mod_btn_frame.pack(pady=(0, 10))

toggle_btn = tk.Button(mod_btn_frame, text="Enable/Disable", command=toggle_mod, bg="#2a2a2a", fg="#dddddd", activebackground="#3a3a3a", activeforeground="white", relief="flat", font=("Segoe UI", 9), cursor="hand2", padx=8, pady=4)
toggle_btn.pack(side="left", padx=(0, 6))

del_mod_btn = tk.Button(mod_btn_frame, text="Delete Mod", command=delete_mod, bg="#c0392b", fg="white", activebackground="#e74c3c", activeforeground="white", relief="flat", font=("Segoe UI", 9), cursor="hand2", padx=8, pady=4)
del_mod_btn.pack(side="left")

if saved_path:
    refresh_mods()

INPUT_INI = os.path.join(os.environ["LOCALAPPDATA"], "EscapeTheBackrooms", "Saved", "Config", "WindowsNoEditor", "Input.ini")
GAMEPAD_PREFIXES = ["Gamepad_", "OculusTouch_", "Vive_", "ValveIndex_", "MagicLeap_"]

def is_keyboard_key(key):
    for prefix in GAMEPAD_PREFIXES:
        if key.startswith(prefix):
            return False
    return True

def parse_keybinds():
    if not os.path.exists(INPUT_INI):
        return []
    bindings = []
    import re
    in_input_settings = False
    try:
        with open(INPUT_INI, "r") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("["):
                    in_input_settings = stripped == "[/Script/Engine.InputSettings]"
                    continue
                if not in_input_settings:
                    continue
                if not stripped.startswith("ActionMappings="):
                    continue
                action = re.search(r'ActionName="([^"]+)"', stripped)
                key = re.search(r'Key=(\S+)\)', stripped)
                shift = re.search(r'bShift=(True|False)', stripped)
                ctrl = re.search(r'bCtrl=(True|False)', stripped)
                alt = re.search(r'bAlt=(True|False)', stripped)
                if not action or not key:
                    continue
                key_val = key.group(1)
                if not is_keyboard_key(key_val):
                    continue
                mods = []
                if shift and shift.group(1) == "True":
                    mods.append("Shift")
                if ctrl and ctrl.group(1) == "True":
                    mods.append("Ctrl")
                if alt and alt.group(1) == "True":
                    mods.append("Alt")
                display = " + ".join(mods + [key_val]) if mods else key_val
                bindings.append((action.group(1), display, stripped))
    except Exception:
        pass
    return bindings

def refresh_keybinds_now():
    top = keybind_listbox.yview()[0]
    selected = keybind_listbox.curselection()
    selected_name = keybind_listbox.get(selected[0]) if selected else None
    keybind_listbox.delete(0, tk.END)
    bindings = parse_keybinds()
    if bindings:
        for action, display, _ in bindings:
            keybind_listbox.insert(tk.END, f"{action}  =  {display}")
        if selected_name:
            for i in range(keybind_listbox.size()):
                if keybind_listbox.get(i) == selected_name:
                    keybind_listbox.selection_set(i)
                    break
    else:
        keybind_listbox.insert(tk.END, "No keybinds found.")
    keybind_listbox.yview_moveto(top)

def refresh_keybinds():
    if mode_var.get() == "Keybind Editor":
        refresh_keybinds_now()
    root.after(1000, refresh_keybinds)

def save_keybinds(new_action_lines):
    if not os.path.exists(INPUT_INI):
        return
    with open(INPUT_INI, "r") as f:
        all_lines = f.readlines()

    result = []
    current_section = ""
    input_settings_written = False

    for line in all_lines:
        stripped = line.strip()
        if stripped.startswith("["):
            current_section = stripped
            if current_section == "[/Script/Engine.InputSettings]" and not input_settings_written:
                result.append(line)
                for new_line in new_action_lines:
                    result.append(new_line.strip() + "\n")
                input_settings_written = True
            else:
                result.append(line)
        elif stripped.startswith("ActionMappings="):
            continue
        else:
            result.append(line)

    with open(INPUT_INI, "w") as f:
        f.writelines(result)

def delete_keybind():
    selection = keybind_listbox.curselection()
    if not selection:
        return
    bindings = parse_keybinds()
    if not bindings or selection[0] >= len(bindings):
        return
    remaining = [b[2] for i, b in enumerate(bindings) if i != selection[0]]
    save_keybinds(remaining)
    refresh_keybinds_now()

def add_keybind():
    bindings = parse_keybinds()
    actions = sorted(set(b[0] for b in bindings)) if bindings else ["Jump", "Interact", "Crouch", "Sprint", "Flashlight"]

    popup = tk.Toplevel(root)
    popup.title("Add Keybind")
    popup.geometry("280x180")
    popup.configure(bg="#1a1a1a")
    popup.resizable(False, False)
    popup.transient(root)

    tk.Label(popup, text="Action:", bg="#1a1a1a", fg="#aaaaaa", font=("Segoe UI", 9)).pack(pady=(10, 2))
    action_var = tk.StringVar(value=actions[0] if actions else "")
    action_dd = ttk.Combobox(popup, textvariable=action_var, values=actions, font=("Segoe UI", 9), width=20)
    action_dd.pack()

    tk.Label(popup, text="Key (e.g. C, SpaceBar, F1):", bg="#1a1a1a", fg="#aaaaaa", font=("Segoe UI", 9)).pack(pady=(8, 2))
    key_entry = tk.Entry(popup, font=("Segoe UI", 9), bg="#2a2a2a", fg="#dddddd", insertbackground="white", relief="flat")
    key_entry.pack(padx=16, fill="x", ipady=4)

    mod_frame_p = tk.Frame(popup, bg="#1a1a1a")
    mod_frame_p.pack(pady=(6, 0))
    shift_var = tk.BooleanVar()
    ctrl_var = tk.BooleanVar()
    alt_var = tk.BooleanVar()
    tk.Checkbutton(mod_frame_p, text="Shift", variable=shift_var, bg="#1a1a1a", fg="#aaaaaa", selectcolor="#1a1a1a", activebackground="#1a1a1a", font=("Segoe UI", 8)).pack(side="left", padx=4)
    tk.Checkbutton(mod_frame_p, text="Ctrl", variable=ctrl_var, bg="#1a1a1a", fg="#aaaaaa", selectcolor="#1a1a1a", activebackground="#1a1a1a", font=("Segoe UI", 8)).pack(side="left", padx=4)
    tk.Checkbutton(mod_frame_p, text="Alt", variable=alt_var, bg="#1a1a1a", fg="#aaaaaa", selectcolor="#1a1a1a", activebackground="#1a1a1a", font=("Segoe UI", 8)).pack(side="left", padx=4)

    def do_add():
        action = action_var.get().strip()
        key = key_entry.get().strip()
        if not action or not key:
            return
        s = "True" if shift_var.get() else "False"
        c = "True" if ctrl_var.get() else "False"
        a = "True" if alt_var.get() else "False"
        new_line = f'ActionMappings=(ActionName="{action}",bShift={s},bCtrl={c},bAlt={a},bCmd=False,Key={key})'
        existing = [b[2] for b in parse_keybinds()]
        existing.append(new_line)
        save_keybinds(existing)
        popup.destroy()
        refresh_keybinds_now()

    tk.Button(popup, text="Add", command=do_add, bg="#c0392b", fg="white", relief="flat", font=("Segoe UI", 9), cursor="hand2", padx=8, pady=4).pack(pady=8)

keybind_frame_tool = tk.Frame(root, bg="#1a1a1a")

kb_list_frame = tk.Frame(keybind_frame_tool, bg="#2a2a2a")
kb_list_frame.pack(padx=16, pady=(4, 0), fill="both", expand=True)

keybind_listbox = tk.Listbox(kb_list_frame, bg="#2a2a2a", fg="#dddddd", font=("Segoe UI", 9), relief="flat", highlightthickness=0, selectbackground="#c0392b", selectforeground="white", borderwidth=0)
keybind_listbox.pack(fill="both", expand=True, padx=6, pady=6)

kb_btn_frame = tk.Frame(keybind_frame_tool, bg="#1a1a1a")
kb_btn_frame.pack(pady=(6, 10))

add_kb_btn = tk.Button(kb_btn_frame, text="Add Keybind", command=add_keybind, bg="#2a2a2a", fg="#dddddd", activebackground="#3a3a3a", activeforeground="white", relief="flat", font=("Segoe UI", 9), cursor="hand2", padx=8, pady=4)
add_kb_btn.pack(side="left", padx=(0, 6))

del_kb_btn = tk.Button(kb_btn_frame, text="Delete Keybind", command=delete_keybind, bg="#c0392b", fg="white", activebackground="#e74c3c", activeforeground="white", relief="flat", font=("Segoe UI", 9), cursor="hand2", padx=8, pady=4)
del_kb_btn.pack(side="left")

def auto_delete_worker():
    if auto_delete.get():
        files = get_save_files()
        if files:
            delete_saves()
    root.after(500, auto_delete_worker)

listener = pynput_keyboard.Listener(on_press=on_global_key)
listener.start()

refresh_saves()
refresh_versions()
refresh_keybinds()
auto_delete_worker()
monitor_cursor_state()

root.mainloop()
