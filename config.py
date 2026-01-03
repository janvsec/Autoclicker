"""
Configuration and constants for the autoclicker
"""

# Modes
MODE_NONE = 0
MODE_STD = 1
MODE_CP = 2

# Initial state
current_mode = MODE_NONE
listening = False

# Hotkey combos
std_combo = None
cp_combo = None
add_combo = None

# Checkpoints storage
checkpoints = []

# Modifier keys mapping
from pynput import keyboard

MODIFIERS = {
    keyboard.Key.shift: "SHIFT",
    keyboard.Key.shift_l: "SHIFT",
    keyboard.Key.shift_r: "SHIFT",
    keyboard.Key.ctrl: "CTRL",
    keyboard.Key.ctrl_l: "CTRL",
    keyboard.Key.ctrl_r: "CTRL",
    keyboard.Key.alt: "ALT",
    keyboard.Key.alt_l: "ALT",
    keyboard.Key.alt_r: "ALT",
    keyboard.Key.cmd: "WIN",
    keyboard.Key.cmd_l: "WIN",
    keyboard.Key.cmd_r: "WIN",
}