import time
import tkinter as tk
#==============================================================================
#Thinking Timer module
#==============================================================================
def start_thinking_timer(root, output_text):
    """Start the 'Thinking...' timer and return state control container."""
    state = {"running": True, "id": None, "start": time.time()}

    def update():
        if not state["running"]:
            return
        
        # Remove old thinking tag text
        ranges = output_text.tag_ranges("thinking")
        if ranges:
            try:
                output_text.delete(ranges[0], ranges[1])
            except tk.TclError:
                pass

        elapsed = int(time.time() - state["start"])
        output_text.insert(tk.END, f"Thinking... {elapsed} seconds\n", "thinking")
        output_text.see(tk.END)

        state["id"] = root.after(1000, update)

    update()
    return state



def stop_thinking_timer(root, output_text, thinking_state):
    """Stop and clean up the thinking timer."""
    thinking_state["running"] = False

    try:
        if thinking_state["id"] is not None:
            root.after_cancel(thinking_state["id"])
    except Exception:
        pass

    # Remove thinking text
    ranges = output_text.tag_ranges("thinking")
    if ranges:
        try:
            output_text.delete(ranges[0], ranges[1])
        except tk.TclError:
            pass

