"""
Core clicking functionality
"""
import time
import threading
from pynput.mouse import Controller, Button
from config import *

# Mouse controller
mouse = Controller()

def stop_all():
    """Stop all clicking activities"""
    global current_mode
    current_mode = MODE_NONE
    return {"status": "stopped", "mode": MODE_NONE}

def std_loop(click_type, interval):
    """Standard clicking loop"""
    global current_mode
    
    btn = Button.left if click_type == "left" else Button.right
    interval_float = float(interval)
    
    while current_mode == MODE_STD:
        try:
            mouse.click(btn)
            time.sleep(interval_float)
        except Exception as e:
            print(f"Error in std_loop: {e}")
            break
    
    return {"status": "finished", "loop": "standard"}

def start_standard_clicker(click_type, interval):
    """Start the standard clicker"""
    global current_mode
    
    if current_mode == MODE_STD:
        return {"status": "already_running", "mode": MODE_STD}
    
    stop_all()
    current_mode = MODE_STD
    
    # Start clicking in a separate thread
    thread = threading.Thread(
        target=std_loop,
        args=(click_type, interval),
        daemon=True
    )
    thread.start()
    
    return {"status": "started", "mode": MODE_STD, "click_type": click_type, "interval": interval}

def cp_loop(checkpoints_data):
    """Checkpoint clicking loop"""
    global current_mode
    
    while current_mode == MODE_CP:
        for cp in checkpoints_data:
            if current_mode != MODE_CP:
                break
            try:
                mouse.position = (cp["x"], cp["y"])
                time.sleep(cp["interval"])
                btn = Button.left if cp["click"] == "left" else Button.right
                mouse.click(btn)
                time.sleep(cp["delay"])
            except Exception as e:
                print(f"Error in cp_loop: {e}")
                break
    
    return {"status": "finished", "loop": "checkpoint"}

def start_checkpoint_clicker():
    """Start the checkpoint clicker"""
    global current_mode
    
    if current_mode == MODE_CP:
        return {"status": "already_running", "mode": MODE_CP}
    
    stop_all()
    current_mode = MODE_CP
    
    # Start clicking in a separate thread
    thread = threading.Thread(
        target=cp_loop,
        args=(checkpoints,),
        daemon=True
    )
    thread.start()
    
    return {"status": "started", "mode": MODE_CP, "checkpoint_count": len(checkpoints)}

def add_checkpoint(mouse_x, mouse_y, click_type, interval, delay):
    """Add a new checkpoint"""
    if current_mode != MODE_NONE:
        return {"status": "error", "message": "Cannot add checkpoint while clicking is active"}
    
    checkpoint = {
        "x": mouse_x,
        "y": mouse_y,
        "click": click_type,
        "interval": float(interval),
        "delay": float(delay)
    }
    
    checkpoints.append(checkpoint)
    
    return {
        "status": "added", 
        "checkpoint": checkpoint,
        "total_checkpoints": len(checkpoints)
    }

def clear_checkpoints():
    """Clear all checkpoints"""
    global checkpoints
    checkpoints.clear()
    return {"status": "cleared", "count": 0}

def get_checkpoints():
    """Get all checkpoints"""
    return {
        "status": "success",
        "checkpoints": checkpoints,
        "count": len(checkpoints)
    }