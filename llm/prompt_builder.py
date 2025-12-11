from memory.conversation import conversation_messages, loaded_history
from tools.rag.rag_search import simple_search
from knowledge_base.code.retriever import retrieve, format_for_prompt
"""
Constructs a single prompt string from loaded_history and conversation_messages.
Formated like:

    Summary: ... (if present)
    User: ...
    Assistant: ...

Code Blocks are wrapped in ```code...  ```
"""

def build_prompt_for_model(user_prompt: str):
    parts = []

    results = retrieve(user_prompt, top_k_ret=5)

    context = format_for_prompt(results, char_length=1500)
    

    parts.append(f"Use the following context to answer the question IF HELPFUL:\n {context}\n")

    if loaded_history:
        parts.append(f"[LOADED HISTORY START]\n{loaded_history}\n[LOADED HISTORY END]\n")

    for m in conversation_messages:
        role = m["role"].capitalize()
        content = m["content"]
        if role == "SUMMARY":
            # keep summary short and clear for the model"
            parts.append(f"Summary: {content}\n")
        elif m["is_code"]:
            #ensure code is clearly marked
            if role == "USER":
                parts.append(f"User:\n```code\n{content}\n```\n")
            elif role == "ASSISTANT":
                parts.append(f"Assistant:\n```code\n{content}\n```\n")
            else:
                parts.append(f"{role.capitalize()}:\n```code\n{content}\n```\n")
        else:
            #normal text line
            if role == "USER":
                parts.append(f"User: {content}\n")
            elif role == "ASSISTANT":
                parts.append(f"Assistant: {content}\n")
            else:
                parts.append(f"{role.capitalize()}: {content}\n")
    #append user prompt and assistant queue, then join parts and return
    parts.append("\nAssistant:")
    print("\n".join(parts))
    return "\n".join(parts)


