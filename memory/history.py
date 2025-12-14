import json
from tkinter import filedialog, messagebox
import memory.conversation as mem

def save_conversation(output_text):
    """Save conversation_messages (full structure) to JSON file."""
    filepath = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
    )
    if not filepath:
        return

    if not filepath.endswith(".json"):
        filepath += ".json"

    data = {
        "loaded_history": mem.loaded_history,
        "conversation_messages": mem.conversation_messages
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    output_text.insert("end", f"[Conversation saved to {filepath}]\n")


def load_conversation(output_text):
    """Load saved JSON conversation and overwrite memory."""
    filepath = filedialog.askopenfilename(
        title="Open Conversation JSON",
        filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
    )
    if not filepath:
        return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Clear existing memory

        # Load data
        mem.loaded_history = data.get("loaded_history", "")
        loaded_msgs = data.get("conversation_messages", [])

        # Merge messages
        mem.conversation_messages.extend(loaded_msgs)

        output_text.insert(
            "end",
            f"[Start loaded conversation from {filepath}]\n"
        )
        for msg in loaded_msgs:
            if msg.get("role") == "user":
                output_text.insert("end", f"User:\n{msg.get('content','')}\n", "user_history")
            elif msg.get("role") == "assistant":
                output_text.insert("end", f"Assistant:\n{msg.get('content','')}\n", "assistant_history")

        output_text.insert(
            "end",
            f"[End loaded conversation from {filepath}]\n"
        )


    except Exception as e:
        messagebox.showerror("Load Error", f"Failed to load conversation: {e}")

