import subprocess
import threading
from memory.conversation import conversation_messages
from llm.models import MODELS

# Global lock: prevents multiple parallel summarizations
_is_summarizing = False


# ---------------------------
#   Summarization helper
# ---------------------------
def summarize_messages(messages, summarizer_model):
    """
    Summarize a list of message dicts into short bullet points.
    Returns summary text, always non-empty.
    """
    if not messages:
        return "Summary: (no content)"

    joined = "\n\n".join(
        f"{m['role'].capitalize()}: {m['content']}" for m in messages
    )

    prompt = (
        "Summarize the following conversation into 3–8 concise bullet points. "
        "Preserve important facts, decisions, user preferences, and tasks. "
        "Do NOT include code blocks.\n\nConversation:\n"
        + joined +
        "\n\nSummary:"
    )

    try:
        result = subprocess.run(
            ["ollama", "run", summarizer_model, prompt],
            capture_output=True, text=True, check=True
        )
        text = result.stdout.strip()
        return text or "Summary: (empty result)"
    except Exception:
        return "Summary: (error generating summary)"


# ---------------------------
#   Core trimming logic
# ---------------------------
def _select_messages_to_summarize(max_messages):
    """
    Determine which messages should be summarized (oldest non-code messages).
    Returns a list of indices.
    """
    if len(conversation_messages) <= max_messages:
        return []

    excess = len(conversation_messages) - max_messages
    non_code_indices = [i for i, m in enumerate(conversation_messages) if not m["is_code"]]

    if not non_code_indices:
        return []

    to_remove = []
    for idx in non_code_indices:
        to_remove.append(idx)
        if len(to_remove) >= excess:
            break

    return to_remove


def _apply_summary(indices, summary_text):
    """
    Remove messages at the given indices and insert a summary message in their place.
    """
    if not indices:
        return

    summary_msg = {"role": "summary", "content": summary_text, "is_code": False}

    # Remove from conversation_messages in reverse order
    for idx in sorted(indices, reverse=True):
        del conversation_messages[idx]

    # Insert summary at earliest removed position
    first = min(indices)
    conversation_messages.insert(first, summary_msg)


# ---------------------------
#   Public API
# ---------------------------
def trim_and_summarize_if_needed(max_messages, summarizer_model, output_text=None, auto=True):
    """
    Reduce the length of conversation_messages by summarizing old non-code messages.
    - max_messages: number of recent messages to keep unsummarized
    - summarizer_model: the ollama model name to call
    - output_text: UI widget (or None for CLI mode)
    - auto: if True, summarization occurs in background; if False, synchronous
    """
    global _is_summarizing

    if _is_summarizing:
        return

    indices = _select_messages_to_summarize(max_messages)
    if not indices:
        return

    # Synchronous path (executor call before sending prompt to model)
    if not auto:
        _is_summarizing = True
        try:
            msgs = [conversation_messages[i] for i in indices]
            summary = summarize_messages(msgs, summarizer_model)
            _apply_summary(indices, summary)
        finally:
            _is_summarizing = False

        # UI log
        if output_text is not None:
            try:
                output_text.insert("end", "[Synchronous summarization completed]\n")
                output_text.see("end")
            except Exception:
                pass

        return

    # ---------------------------
    # Asynchronous background path
    # ---------------------------
    def _thread():
        global _is_summarizing
        _is_summarizing = True

        msgs = [conversation_messages[i] for i in indices]
        summary = summarize_messages(msgs, summarizer_model)
        _apply_summary(indices, summary)

        _is_summarizing = False

        # UI log
        if output_text is not None:
            try:
                output_text.insert("end", "[Automatic summarization completed]\n")
                output_text.see("end")
            except Exception:
                pass

    t = threading.Thread(target=_thread, daemon=True)
    t.start()

