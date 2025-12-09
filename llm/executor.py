import subprocess
import threading
import tkinter as tk
import time
import re

from llm.prompt_builder import build_prompt_for_model
from llm.summarizer import trim_and_summarize_if_needed
from llm.models import MODELS, SUMMARIZER_MODEL
from gui.code_highlight import insert_code_block
from memory.conversation import append_message
from tools.weather import get_current_weather
from gui.thinking_timer import start_thinking_timer, stop_thinking_timer
from tools.rag.rag_search import simple_search

# ============================================================
#   MAIN ENTRY POINT
# ============================================================

def run_ollama(root, widgets):
    """Main execution entry for running the model and updating the UI."""

    # Extract widget references
    model_var          = widgets["model_var"]
    prompt_text        = widgets["prompt_text"]
    output_text        = widgets["output_text"]
    max_messages_var   = widgets["max_messages_var"]
    auto_summarize_var = widgets["auto_summarize_var"]

    model_name  = model_var.get()
    user_prompt = prompt_text.get("1.0", tk.END).strip()

    # Prevent empty prompts
    if not user_prompt:
        output_text.insert(tk.END, "Please enter a prompt.\n")
        return

    # Save user message to memory
    append_message("user", user_prompt)

    # Display user bubble
    display_user_message(output_text, user_prompt)

    # Parse max messages setting
    max_messages = parse_max_messages(max_messages_var)

    # Summarization passes
    run_summarization(output_text, auto_summarize_var, max_messages)

    # Check if asking for weather
    if "weather" in user_prompt.lower():
        reply = get_current_weather(user_prompt)
        output_text.insert(tk.END, f"Assistant:\n", "assistant_header")
        output_text.insert(tk.END, reply + "\n\n", "assistant_text")
        return

    # Build final model prompt
    #fix the double user input issue
    prompt_for_model = build_prompt_for_model(user_prompt)

    # Show "Running" message
    output_text.insert(tk.END, f"> Running {model_name}...\n")
    output_text.update()

    # Start thinking timer
    thinking_state = start_thinking_timer(root, output_text)

    # Start model call in background thread
    threading.Thread(
        target=_run_model_thread,
        daemon=True,
        args=(root, output_text, prompt_for_model, model_name, thinking_state)
    ).start()


# ============================================================
#   USER MESSAGE DISPLAY
# ============================================================

def display_user_message(output_text, user_prompt):
    """Insert formatted user message into the output window."""
    output_text.insert(tk.END, "User:\n", "user_header")
    output_text.insert(tk.END, user_prompt + "\n\n", "user_text")
    output_text.insert(tk.END, "\n", "spacer")
    output_text.see(tk.END)



# ============================================================
#   PARSE SETTINGS
# ============================================================

def parse_max_messages(max_messages_var):
    """Parse the max_messages value safely."""
    from llm.models import DEFAULT_MAX_MESSAGES
    try:
        return int(max_messages_var.get())
    except Exception:
        return DEFAULT_MAX_MESSAGES



# ============================================================
#   SUMMARIZATION LOGIC
# ============================================================

def run_summarization(output_text, auto_summarize_var, max_messages):
    """Perform auto and manual summarization steps."""

    # Auto summarization (background)
    if auto_summarize_var.get():
        trim_and_summarize_if_needed(
            max_messages=max_messages,
            summarizer_model=SUMMARIZER_MODEL,
            output_text=output_text,
            auto=True
        )

    # Manual synchronous summarization
    trim_and_summarize_if_needed(
        max_messages=max_messages,
        summarizer_model=SUMMARIZER_MODEL,
        output_text=output_text,
        auto=False
    )



# ============================================================
#   MODEL CALL (BACKGROUND THREAD)
# ============================================================

def _run_model_thread(root, output_text, prompt_for_model, model_name, thinking_state):
    """Executed in background — runs ollama and updates UI afterward."""

    # Run model
    model_reply = run_ollama_process(prompt_for_model, model_name)

    # Update GUI on main thread
    root.after(0, lambda: handle_model_reply(root, output_text, model_reply, thinking_state))



def run_ollama_process(prompt, model_name):
    """Call the actual Ollama subprocess."""
    try:
        result = subprocess.run(
            ["ollama", "run", MODELS[model_name], prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"



# ============================================================
#   FINAL ASSISTANT REPLY PROCESSING
# ============================================================

def handle_model_reply(root, output_text, model_reply, thinking_state):
    """Insert the assistant reply into the UI and stop timer."""

    stop_thinking_timer(root, output_text, thinking_state)

    # Save memory
    append_message("assistant", model_reply)

    # Display assistant header
    output_text.insert(tk.END, "Assistant:\n", "assistant_header")

    # Insert reply with code block parsing
    insert_model_reply_with_code(output_text, model_reply)

    output_text.insert(tk.END, "\n\n", "spacer")
    output_text.see(tk.END)



# ============================================================
#   CODE BLOCK PARSER
# ============================================================

def insert_model_reply_with_code(text_widget, reply):
    """Parse and insert assistant text, splitting code from normal text."""

    lines = reply.split("\n")
    inside_code = False
    code_buffer = []

    for line in lines:
        # Detect ``` fences
        if line.strip().startswith("```"):
            if not inside_code:
                inside_code = True
                code_buffer = []
            else:
                inside_code = False
                code = "\n".join(code_buffer)
                insert_code_block(text_widget, code)
                text_widget.insert("end", "\n")
            continue

        # Collect code
        if inside_code:
            code_buffer.append(line)
        else:
            text_widget.insert("end", line + "\n", "assistant_text")
            