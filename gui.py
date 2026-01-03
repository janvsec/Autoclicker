"""
Main GUI application for the autoclicker
"""
import tkinter as tk
from config import *
from keyboard_handler import *
from clicker_functions import *
from hotkey_manager import *

class AutoclickerGUI:
    def __init__(self):
        self.app = tk.Tk()
        self.setup_gui()
        self.setup_listeners()
        
    def setup_gui(self):
        """Setup the GUI layout"""
        self.app.title("Autoclicker")
        self.app.geometry("420x820")
        self.app.configure(bg="#1e1e1e")
        self.app.resizable(False, False)
        
        # Variables
        self.std_click = tk.StringVar(value="left")
        self.cp_click = tk.StringVar(value="left")
        self.std_interval = tk.StringVar(value="0.1")
        self.cp_interval = tk.StringVar(value="0.1")
        self.cp_delay = tk.StringVar(value="1.0")
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Section 1: Standard Clicker
        section1 = tk.LabelFrame(self.app, text="Standard Clicker", bg="#1e1e1e", fg="white", padx=10, pady=10)
        section1.pack(fill="x", padx=10, pady=5)
        
        tk.Label(section1, text="Mouse Button:", bg="#1e1e1e", fg="white").pack(anchor="w")
        tk.Radiobutton(section1, text="Left Click", variable=self.std_click, value="left",
                      bg="#1e1e1e", fg="white", selectcolor="#1e1e1e", activebackground="#1e1e1e").pack(anchor="w")
        tk.Radiobutton(section1, text="Right Click", variable=self.std_click, value="right",
                      bg="#1e1e1e", fg="white", selectcolor="#1e1e1e", activebackground="#1e1e1e").pack(anchor="w")
        
        tk.Label(section1, text="Click Interval (seconds):", bg="#1e1e1e", fg="white").pack(anchor="w", pady=(10,0))
        self.std_interval_entry = tk.Entry(section1, bg="#2b2b2b", fg="white", insertbackground="white", 
                                          textvariable=self.std_interval)
        self.std_interval_entry.pack(fill="x")
        
        self.std_key_btn = tk.Button(section1, text="Set Start/Stop Hotkey",
                                    bg="#2d2d2d", fg="white", activebackground="#3d3d3d",
                                    command=lambda: start_capture(self.std_key_btn, self.app, self.on_hotkey_captured))
        self.std_key_btn.pack(fill="x", pady=10)
        
        self.std_status = tk.Label(section1, text="STOPPED", bg="#1e1e1e", fg="red", font=("Arial", 10, "bold"))
        self.std_status.pack()
        
        # Section 2: Checkpoint Clicker
        section2 = tk.LabelFrame(self.app, text="Checkpoint Clicker", bg="#1e1e1e", fg="white", padx=10, pady=10)
        section2.pack(fill="both", expand=True, padx=10, pady=5)
        
        tk.Label(section2, text="Mouse Button:", bg="#1e1e1e", fg="white").pack(anchor="w")
        tk.Radiobutton(section2, text="Left Click", variable=self.cp_click, value="left",
                      bg="#1e1e1e", fg="white", selectcolor="#1e1e1e", activebackground="#1e1e1e").pack(anchor="w")
        tk.Radiobutton(section2, text="Right Click", variable=self.cp_click, value="right",
                      bg="#1e1e1e", fg="white", selectcolor="#1e1e1e", activebackground="#1e1e1e").pack(anchor="w")
        
        tk.Label(section2, text="Move Interval (seconds):", bg="#1e1e1e", fg="white").pack(anchor="w", pady=(10,0))
        self.cp_interval_entry = tk.Entry(section2, bg="#2b2b2b", fg="white", insertbackground="white",
                                         textvariable=self.cp_interval)
        self.cp_interval_entry.pack(fill="x")
        
        tk.Label(section2, text="Click Delay (seconds):", bg="#1e1e1e", fg="white").pack(anchor="w", pady=(10,0))
        self.cp_delay_entry = tk.Entry(section2, bg="#2b2b2b", fg="white", insertbackground="white",
                                      textvariable=self.cp_delay)
        self.cp_delay_entry.pack(fill="x")
        
        # Control buttons frame
        control_frame = tk.Frame(section2, bg="#1e1e1e")
        control_frame.pack(fill="x", pady=10)
        
        self.add_key_btn = tk.Button(control_frame, text="Set Add-Checkpoint Hotkey",
                                    bg="#2d2d2d", fg="white", activebackground="#3d3d3d",
                                    command=lambda: start_capture(self.add_key_btn, self.app, self.on_hotkey_captured))
        self.add_key_btn.pack(fill="x", pady=5)
        
        self.cp_key_btn = tk.Button(control_frame, text="Set Start/Stop Hotkey",
                                   bg="#2d2d2d", fg="white", activebackground="#3d3d3d",
                                   command=lambda: start_capture(self.cp_key_btn, self.app, self.on_hotkey_captured))
        self.cp_key_btn.pack(fill="x", pady=5)
        
        # Checkpoint list
        list_frame = tk.Frame(section2, bg="#1e1e1e")
        list_frame.pack(fill="both", expand=True, pady=10)
        
        tk.Label(list_frame, text="Checkpoints:", bg="#1e1e1e", fg="white").pack(anchor="w")
        self.cp_list = tk.Listbox(list_frame, bg="#121212", fg="white", height=6)
        self.cp_list.pack(fill="both", expand=True)
        
        # Clear checkpoints button
        clear_btn = tk.Button(section2, text="Clear All Checkpoints",
                             bg="#4a2d2d", fg="white", activebackground="#5a3d3d",
                             command=self.clear_checkpoints)
        clear_btn.pack(fill="x", pady=5)
        
        self.cp_status = tk.Label(section2, text="STOPPED", bg="#1e1e1e", fg="red", font=("Arial", 10, "bold"))
        self.cp_status.pack()
        
        # Instructions
        instructions = tk.Label(self.app, 
                               text="Instructions:\n"
                                    "1. Set hotkeys for each function\n"
                                    "2. Hotkeys work as toggle: press to start, press again to stop\n"
                                    "3. Add checkpoint: position mouse, press add-checkpoint hotkey\n"
                                    "4. Use the same hotkey to stop clicking",
                               bg="#1e1e1e", fg="#aaaaaa", justify="left")
        instructions.pack(fill="x", padx=10, pady=10)
        
    def clear_checkpoints(self):
        """Clear all checkpoints"""
        result = clear_checkpoints()
        self.refresh_checkpoint_list()
        return result
        
    def refresh_checkpoint_list(self):
        """Refresh the checkpoint list display"""
        self.cp_list.delete(0, "end")
        checkpoints_data = get_checkpoints()
        
        if checkpoints_data["status"] == "success":
            for i, cp in enumerate(checkpoints_data["checkpoints"]):
                self.cp_list.insert(
                    "end",
                    f"{i+1}: ({cp['x']},{cp['y']}) {cp['click']} click, "
                    f"interval={cp['interval']}s, delay={cp['delay']}s"
                )
                
    def on_hotkey_captured(self, combo, btn):
        """Callback when a hotkey is captured"""
        global std_combo, cp_combo, add_combo
        
        if not combo or combo[1] is None:
            btn.config(text="Set Hotkey", bg="#2d2d2d")
            return
        
        # Update the appropriate combo
        if btn == self.std_key_btn:
            std_combo = combo
        elif btn == self.cp_key_btn:
            cp_combo = combo
        elif btn == self.add_key_btn:
            add_combo = combo
        
        btn.config(text=combo_text(combo), bg="#2d2d2d")
        
    def update_status(self, action_result):
        """Update GUI status based on action result"""
        if action_result.get("action") == "start_std":
            self.std_status.config(text="RUNNING", fg="green")
        elif action_result.get("action") == "start_cp":
            self.cp_status.config(text="RUNNING", fg="green")
        elif action_result.get("action") == "stop_all":
            self.std_status.config(text="STOPPED", fg="red")
            self.cp_status.config(text="STOPPED", fg="red")
        elif action_result.get("action") == "add_cp":
            self.refresh_checkpoint_list()
            
    def setup_listeners(self):
        """Setup keyboard listeners"""
        def on_press(key):
            if listening:
                return
            
            pressed_keys.add(key)
            
            # Handle the hotkey press
            result = handle_hotkey_press(
                key, 
                self.std_click.get(),
                self.std_interval.get(),
                self.cp_click.get(),
                self.cp_interval.get(),
                self.cp_delay.get()
            )
            
            self.update_status(result)
            
        def on_release(key):
            pressed_keys.discard(key)
        
        # Start the keyboard listener
        start_listener(on_press, on_release)
        
    def run(self):
        """Run the application"""
        def on_closing():
            stop_capture_listener()
            stop_listener()
            self.app.destroy()
            
        self.app.protocol("WM_DELETE_WINDOW", on_closing)
        self.app.mainloop()