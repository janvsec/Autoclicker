import tkinter as tk
import threading
import time
from pynput.mouse import Controller, Button
from pynput import keyboard

mouse = Controller()

std_running = False
cp_running = False
checkpoints = []

pressed = set()
capturing = None

std_combo = None
cp_combo = None
add_combo = None

MODIFIERS = {
    keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r,
    keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
    keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r,
}

def is_modifier(k):
    return k in MODIFIERS

def normalize_modifier(k):
    if k in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
        return "SHIFT"
    if k in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        return "CTRL"
    if k in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
        return "ALT"
    return None

def combo_to_text(combo):
    mod, key = combo
    if isinstance(key, keyboard.KeyCode) and key.char:
        return f"{mod}+{key.char.upper()}"
    return f"{mod}+{str(key).replace('Key.', '').upper()}"

def valid_final_combo(mod, key):
    if mod is None:
        return False
    if is_modifier(key):
        return False
    return True

def stop_all():
    global std_running, cp_running
    std_running = False
    cp_running = False
    std_status.config(text="STOPPED")
    cp_status.config(text="STOPPED")

def std_loop():
    while std_running:
        btn = Button.left if std_click.get() == "left" else Button.right
        mouse.click(btn)
        time.sleep(float(std_interval.get()))

def cp_loop():
    while cp_running:
        for cp in checkpoints:
            if not cp_running:
                break
            mouse.position = (cp["x"], cp["y"])
            time.sleep(cp["interval"])
            btn = Button.left if cp["click"] == "left" else Button.right
            mouse.click(btn)
            time.sleep(cp["delay"])

def toggle_std():
    global std_running, cp_running
    if capturing:
        return
    if std_running:
        std_running = False
        std_status.config(text="STOPPED")
    else:
        cp_running = False
        cp_status.config(text="STOPPED")
        std_running = True
        std_status.config(text="RUNNING")
        threading.Thread(target=std_loop, daemon=True).start()

def toggle_cp():
    global cp_running, std_running
    if capturing:
        return
    if cp_running:
        cp_running = False
        cp_status.config(text="STOPPED")
    else:
        if not checkpoints:
            return
        std_running = False
        std_status.config(text="STOPPED")
        cp_running = True
        cp_status.config(text="RUNNING")
        threading.Thread(target=cp_loop, daemon=True).start()

def add_checkpoint():
    if capturing:
        return
    x, y = mouse.position
    checkpoints.append({
        "x": x,
        "y": y,
        "click": cp_click.get(),
        "interval": float(cp_interval.get()),
        "delay": float(cp_delay.get())
    })
    refresh_list()

def refresh_list():
    cp_list.delete(0, "end")
    for i, cp in enumerate(checkpoints):
        cp_list.insert(
            "end",
            f"{i+1}: {cp['x']},{cp['y']} {cp['click']} i={cp['interval']} d={cp['delay']}"
        )

def start_capture(target_btn):
    global capturing
    stop_all()
    pressed.clear()
    capturing = target_btn
    target_btn.config(text="LISTENING...")

def finish_capture(combo):
    global std_combo, cp_combo, add_combo, capturing
    if capturing == std_key_btn:
        std_combo = combo
    elif capturing == cp_key_btn:
        cp_combo = combo
    elif capturing == add_key_btn:
        add_combo = combo
    capturing.config(text=combo_to_text(combo))
    capturing = None
    pressed.clear()

def on_press(key):
    pressed.add(key)

    if capturing:
        mods = [normalize_modifier(k) for k in pressed if is_modifier(k)]
        mods = [m for m in mods if m is not None]
        if len(mods) != 1:
            return
        non_mods = [k for k in pressed if not is_modifier(k)]
        if len(non_mods) != 1:
            return
        mod = mods[0]
        key_final = non_mods[0]
        if not valid_final_combo(mod, key_final):
            return
        finish_capture((mod, key_final))
        return

    if std_combo:
        mod, key_final = std_combo
        if key_final in pressed and any(normalize_modifier(k) == mod for k in pressed):
            toggle_std()

    if cp_combo:
        mod, key_final = cp_combo
        if key_final in pressed and any(normalize_modifier(k) == mod for k in pressed):
            toggle_cp()

    if add_combo:
        mod, key_final = add_combo
        if key_final in pressed and any(normalize_modifier(k) == mod for k in pressed):
            add_checkpoint()

def on_release(key):
    pressed.discard(key)

keyboard.Listener(on_press=on_press, on_release=on_release).start()

app = tk.Tk()
app.geometry("420x820")
app.resizable(False, False)
app.configure(bg="#1e1e1e")
app.title("Autoclicker")

def label(p, t):
    return tk.Label(p, text=t, bg="#1e1e1e", fg="white")

def entry(p, d):
    e = tk.Entry(p, bg="#2b2b2b", fg="white")
    e.insert(0, d)
    return e

section1 = tk.LabelFrame(app, text="Standard Clicker", bg="#1e1e1e", fg="white", padx=10, pady=10)
section1.pack(fill="x", padx=10, pady=10)

std_click = tk.StringVar(value="left")
tk.Radiobutton(section1, text="Left Click", variable=std_click, value="left",
               bg="#1e1e1e", fg="white", selectcolor="#1e1e1e").pack(anchor="w")
tk.Radiobutton(section1, text="Right Click", variable=std_click, value="right",
               bg="#1e1e1e", fg="white", selectcolor="#1e1e1e").pack(anchor="w")

label(section1, "Interval (sec)").pack()
std_interval = entry(section1, "0.1")
std_interval.pack(fill="x")

std_key_btn = tk.Button(section1, text="Set Start/Stop Hotkey",
                        bg="#2d2d2d", fg="white",
                        command=lambda: start_capture(std_key_btn))
std_key_btn.pack(fill="x", pady=5)

std_status = label(section1, "STOPPED")
std_status.pack()

section2 = tk.LabelFrame(app, text="Checkpoint Clicker", bg="#1e1e1e", fg="white", padx=10, pady=10)
section2.pack(fill="both", expand=True, padx=10, pady=10)

cp_click = tk.StringVar(value="left")
tk.Radiobutton(section2, text="Left Click", variable=cp_click, value="left",
               bg="#1e1e1e", fg="white", selectcolor="#1e1e1e").pack(anchor="w")
tk.Radiobutton(section2, text="Right Click", variable=cp_click, value="right",
               bg="#1e1e1e", fg="white", selectcolor="#1e1e1e").pack(anchor="w")

label(section2, "Interval before click").pack()
cp_interval = entry(section2, "0.1")
cp_interval.pack(fill="x")

label(section2, "Delay after click").pack()
cp_delay = entry(section2, "1")
cp_delay.pack(fill="x")

add_key_btn = tk.Button(section2, text="Set Add-Checkpoint Hotkey",
                        bg="#2d2d2d", fg="white",
                        command=lambda: start_capture(add_key_btn))
add_key_btn.pack(fill="x", pady=5)

cp_key_btn = tk.Button(section2, text="Set Start/Stop Hotkey",
                       bg="#2d2d2d", fg="white",
                       command=lambda: start_capture(cp_key_btn))
cp_key_btn.pack(fill="x", pady=5)

cp_list = tk.Listbox(section2, bg="#121212", fg="white")
cp_list.pack(fill="both", expand=True)

cp_status = label(section2, "STOPPED")
cp_status.pack()

app.mainloop()
