"""
Keyboard and hotkey handling functions
"""
import keyboard as kb_module
from pynput import keyboard
from config import *

# Global keyboard listener and pressed keys
listener = None
capture_listener = None
pressed_keys = set()
captured_keys = set()

def is_modifier(key):
    """Check if a key is a modifier key"""
    return key in MODIFIERS

def key_to_string(key):
    """Convert any key to a readable string"""
    if isinstance(key, keyboard.KeyCode):
        if key.char:
            return key.char.upper()
        else:
            # Handle special keys like F1-F12, etc.
            return f"KeyCode(vk={key.vk})"
    elif isinstance(key, keyboard.Key):
        # Remove 'Key.' prefix and make it readable
        key_name = str(key).replace("Key.", "")
        # Handle special cases
        if key_name.startswith("f") and key_name[1:].isdigit():
            return key_name.upper()  # F1, F2, etc.
        return key_name.replace("_", " ").upper()
    return str(key)

def combo_text(combo):
    """Convert a key combo to display text"""
    if not combo or combo[1] is None:
        return "None"
    mod, key = combo
    key_str = key_to_string(key)
    return f"{mod}+{key_str}" if mod else key_str

def start_listener(on_press_callback, on_release_callback):
    """Start the global keyboard listener"""
    global listener
    listener = keyboard.Listener(
        on_press=on_press_callback,
        on_release=on_release_callback
    )
    listener.start()
    return listener

def stop_listener():
    """Stop the global keyboard listener"""
    global listener
    if listener:
        listener.stop()
        listener = None

def start_capture_listener(on_press_callback, on_release_callback):
    """Start a temporary listener for hotkey capture"""
    global capture_listener
    capture_listener = keyboard.Listener(
        on_press=on_press_callback,
        on_release=on_release_callback,
        suppress=True
    )
    capture_listener.start()
    return capture_listener

def stop_capture_listener():
    """Stop the capture listener"""
    global capture_listener
    if capture_listener:
        capture_listener.stop()
        capture_listener = None