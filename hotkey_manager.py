"""
Hotkey management and capture functionality
"""
import tkinter as tk
from keyboard_handler import *
from config import *
from clicker_functions import start_standard_clicker, start_checkpoint_clicker, add_checkpoint

# Global variables for hotkey capture
capture_btn = None
capture_modifier = None
capture_key = None
capture_window = None

def start_capture(btn, app_window, on_capture_complete):
    """
    Start capturing a hotkey
    
    Args:
        btn: The button that triggered the capture
        app_window: The main application window
        on_capture_complete: Callback function when capture is complete
    """
    global listening, capture_btn, capture_modifier, capture_key, capture_window
    
    if listening:
        return
    
    from clicker_functions import stop_all
    stop_all()
    
    pressed_keys.clear()
    captured_keys.clear()
    
    listening = True
    capture_btn = btn
    capture_modifier = None
    capture_key = None
    
    btn.config(text="Press a key...", bg="#4a4a4a")
    
    # Create capture window
    capture_window = tk.Toplevel(app_window)
    capture_window.title("Hotkey Capture")
    capture_window.geometry("350x200")
    capture_window.configure(bg="#1e1e1e")
    capture_window.resizable(False, False)
    capture_window.transient(app_window)
    capture_window.grab_set()
    
    # Center the capture window
    app_x = app_window.winfo_x()
    app_y = app_window.winfo_y()
    app_width = app_window.winfo_width()
    capture_window.geometry(f"+{app_x + app_width//2 - 175}+{app_y + 100}")
    
    # UI Elements
    tk.Label(capture_window, text="Press a key combination", 
             bg="#1e1e1e", fg="white", font=("Arial", 14, "bold")).pack(pady=15)
    
    instruction = tk.Label(capture_window, 
                          text="Hold a modifier (Ctrl/Shift/Alt) then press a key,\n or press a single function key\n\nRelease both keys when done",
                          bg="#1e1e1e", fg="#aaaaaa", wraplength=300)
    instruction.pack(pady=5)
    
    current_keys = tk.Label(capture_window, text="", 
                           bg="#1e1e1e", fg="yellow", font=("Arial", 12, "bold"))
    current_keys.pack(pady=15)
    
    def update_display():
        """Update the display with current key combination"""
        if capture_modifier and capture_key:
            key_str = key_to_string(capture_key)
            current_keys.config(text=f"{capture_modifier} + {key_str}")
        elif capture_modifier:
            current_keys.config(text=f"{capture_modifier} + ?")
        elif capture_key:
            current_keys.config(text=f"{key_to_string(capture_key)}")
        else:
            current_keys.config(text="Waiting for input...")
    
    def finish():
        """Finish the capture process"""
        global listening
        
        stop_capture_listener()
        
        if capture_key or (capture_modifier and capture_key):
            combo = (capture_modifier, capture_key) if capture_modifier else (None, capture_key)
            on_capture_complete(combo, btn)
        
        if capture_window:
            capture_window.destroy()
    
    def cancel():
        """Cancel the capture process"""
        global listening
        
        stop_capture_listener()
        
        if capture_window:
            capture_window.destroy()
        
        btn.config(text="Set Hotkey", bg="#2d2d2d")
        listening = False
    
    # Button frame
    button_frame = tk.Frame(capture_window, bg="#1e1e1e")
    button_frame.pack(pady=10)
    
    tk.Button(button_frame, text="Done", command=finish, 
              bg="#2d2d2d", fg="white", width=12, height=1,
              activebackground="#3d3d3d").pack(side="left", padx=10)
    tk.Button(button_frame, text="Cancel", command=cancel,
              bg="#2d2d2d", fg="white", width=12, height=1,
              activebackground="#3d3d3d").pack(side="right", padx=10)
    
    # Capture listener callbacks
    def on_press_capture(key):
        global capture_modifier, capture_key
        
        captured_keys.add(key)
        
        # Check for modifiers
        if key in MODIFIERS:
            capture_modifier = MODIFIERS[key]
        else:
            # This is the main key
            capture_key = key
        
        update_display()
        return False
    
    def on_release_capture(key):
        captured_keys.discard(key)
        
        # If all keys are released, update display
        if not captured_keys:
            update_display()
        
        return False
    
    # Start capture listener
    start_capture_listener(on_press_capture, on_release_capture)
    
    capture_window.protocol("WM_DELETE_WINDOW", cancel)
    
    # Auto-finish after 3 seconds if both keys are captured
    def auto_finish():
        if capture_window and (capture_key or (capture_modifier and capture_key)):
            finish()
    
    capture_window.after(3000, auto_finish)

def handle_hotkey_press(key, std_click_type, std_interval, cp_click_type, cp_interval, cp_delay):
    """
    Handle hotkey presses for starting/stopping actions
    
    Args:
        key: The key that was pressed
        std_click_type: Standard clicker button type
        std_interval: Standard clicker interval
        cp_click_type: Checkpoint clicker button type
        cp_interval: Checkpoint clicker interval
        cp_delay: Checkpoint clicker delay
        
    Returns:
        Dictionary with action result
    """
    from clicker_functions import stop_all, start_standard_clicker, start_checkpoint_clicker
    from pynput.mouse import Controller
    
    mouse = Controller()
    result = {"action": "none"}
    
    # Check for standard clicker hotkey
    if std_combo and current_mode == MODE_NONE:
        mod, key_val = std_combo
        if key_val == key:
            if mod:
                # Check if modifier is pressed
                mod_pressed = False
                for k in pressed_keys:
                    if k in MODIFIERS and MODIFIERS[k] == mod:
                        mod_pressed = True
                        break
                if mod_pressed:
                    result = start_standard_clicker(std_click_type, std_interval)
                    result["action"] = "start_std"
            else:
                result = start_standard_clicker(std_click_type, std_interval)
                result["action"] = "start_std"
    
    # Check for checkpoint clicker hotkey
    elif cp_combo and current_mode == MODE_NONE:
        mod, key_val = cp_combo
        if key_val == key:
            if mod:
                mod_pressed = False
                for k in pressed_keys:
                    if k in MODIFIERS and MODIFIERS[k] == mod:
                        mod_pressed = True
                        break
                if mod_pressed:
                    result = start_checkpoint_clicker()
                    result["action"] = "start_cp"
            else:
                result = start_checkpoint_clicker()
                result["action"] = "start_cp"
    
    # Check for add checkpoint hotkey
    elif add_combo and current_mode == MODE_NONE:
        mod, key_val = add_combo
        if key_val == key:
            if mod:
                mod_pressed = False
                for k in pressed_keys:
                    if k in MODIFIERS and MODIFIERS[k] == mod:
                        mod_pressed = True
                        break
                if mod_pressed:
                    x, y = mouse.position
                    result = add_checkpoint(x, y, cp_click_type, cp_interval, cp_delay)
                    result["action"] = "add_cp"
            else:
                x, y = mouse.position
                result = add_checkpoint(x, y, cp_click_type, cp_interval, cp_delay)
                result["action"] = "add_cp"
    
    # Check for stop hotkeys
    elif current_mode != MODE_NONE:
        if (std_combo and std_combo[1] == key) or (cp_combo and cp_combo[1] == key):
            # Check modifier if needed
            if std_combo and std_combo[1] == key:
                mod, _ = std_combo
                if mod:
                    mod_pressed = False
                    for k in pressed_keys:
                        if k in MODIFIERS and MODIFIERS[k] == mod:
                            mod_pressed = True
                            break
                    if not mod_pressed:
                        return result
            elif cp_combo and cp_combo[1] == key:
                mod, _ = cp_combo
                if mod:
                    mod_pressed = False
                    for k in pressed_keys:
                        if k in MODIFIERS and MODIFIERS[k] == mod:
                            mod_pressed = True
                            break
                    if not mod_pressed:
                        return result
            
            result = stop_all()
            result["action"] = "stop_all"
    
    return result