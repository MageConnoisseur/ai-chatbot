from llm.executor import run_ollama
from memory.history import save_conversation, load_conversation
from memory.conversation import clear_conversation_data
from knowledge_base.code.indexer import index_files
from tkinter import messagebox

def bind_events(root, w):
    w["run_btn"]["command"] = lambda: run_ollama(root, w)
    w["save_btn"]["command"] = lambda: save_conversation(w["output_text"])
    w["load_btn"]["command"] = lambda: load_conversation(w["output_text"])
    w["clear_btn"]["command"] = lambda: clear_conversation(root, w)
    w["man_index_btn"]["command"] = lambda: index_files()


def clear_conversation(root, w):
    if not messagebox.askyesno("Confirm", "Clear the entire conversation?"):
        return
    
    #Clear the memory layer
    clear_conversation_data()

    #clear UI
    w["output_text"].delete("1.0", "end")
    