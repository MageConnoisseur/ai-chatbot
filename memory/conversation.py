import re
from tkinter import messagebox
import tkinter as tk

conversation_messages = []
loaded_history = ""

def clear_conversation():
    ''' clear all conversation data.'''
    global conversation_messages, loaded_history
    conversation_messages.clear()
    loaded_history = ""


def detect_code_block(text: str) -> bool:
    """Return True if text contains fenced code block or looks like code."""
    if re.search(r"```.+?```", text, flags=re.S):
        return True
    # simple heuristic: many lines ending with ';' or contains 'def ' or 'class ' or 'import '
    lines = text.strip().splitlines()
    if len(lines) <= 6 and any(l.strip().startswith(("def ", "class ", "import ", "#!")) for l in lines):
        return True
    return False

def append_message(role: str, content: str):
    """Append a message object to conversation_messages. Preserve code flag."""
    conversation_messages.append({
        "role": role,
        "content": content,
        "is_code": detect_code_block(content)
    })

def clear_conversation_data():
    ''' clear all conversation data so you can start a fresh conversation.'''
    global conversation_messages, loaded_history
    conversation_messages.clear()
    loaded_history = ""


