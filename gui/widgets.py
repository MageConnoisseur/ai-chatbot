import tkinter as tk
from tkinter import ttk, scrolledtext, font
from llm.models import MODELS, DEFAULT_MAX_MESSAGES, AUTO_SUMMARIZE

def create_widgets(root):
    widgets = {}


    '''
    --------   Top Control Frame   --------
    '''

    # Top frame for model selection and controls
    top_frame = tk.Frame(root)
    top_frame.pack(fill="x", padx = 10, pady = 6)

    tk.Label(top_frame, text = "Select Model:").pack(side="left")
    model_var = tk.StringVar(value=list(MODELS.keys())[0])
    model_menu = ttk.Combobox(top_frame, textvariable=model_var,
                              values=list(MODELS.keys()), state="readonly", width=30)
    model_menu.pack(side="left", padx=(6,20))
    #pass into widgets dict
    widgets["model_var"] = model_var
    widgets["model_menu"] = model_menu


    #max messages setting also on top frame
    tk.Label(top_frame, text="Max messages:").pack(side="left")
    max_messages_var = tk.StringVar(value=str(DEFAULT_MAX_MESSAGES))
    max_messages_entry = tk.Entry(top_frame, textvariable=max_messages_var, width=6)
    max_messages_entry.pack(side="left", padx=(6,6))
    #pass into widgets dict
    widgets["max_messages_var"] = max_messages_var
    widgets["max_messages_entry"] = max_messages_entry

    #Auto summarize checkbox
    auto_var = tk.BooleanVar(value=AUTO_SUMMARIZE)
    auto_chk = tk.Checkbutton(top_frame, text="Auto-summarize", variable=auto_var)
    auto_chk.pack(side="left", padx=6)
    #pass into widgets dict
    widgets["auto_summarize_var"] = auto_var




    '''
    --------   Prompt Box   --------
    '''

    #prompt area
    tk.Label(root, text = "Enter Prompt:").pack(anchor="w", padx=10)
    prompt_text = scrolledtext.ScrolledText(root, wrap="word", height = 8)
    prompt_text.pack(padx =10, pady = (0,6), fill="both", expand = True)
    #pass into widgets dict
    widgets["prompt_text"] = prompt_text

    '''
    --------    Button Row   --------
    '''

    btn_row = tk.Frame(root)
    btn_row.pack(fill = "x", padx = 10, pady = (0,6))

    widgets["run_btn"] = tk.Button(btn_row, text="Run Prompt")
    widgets["run_btn"].pack(side="left")

    widgets["save_btn"] = tk.Button(btn_row, text = "Save Conversation")
    widgets["save_btn"].pack(side="left", padx = 6)

    widgets["load_btn"] = tk.Button(btn_row, text = "Load Conversation")
    widgets["load_btn"].pack(side="left", padx = 6)

    #Clear Conversation Button
    widgets["clear_btn"] = tk.Button(btn_row, text = "Clear Conversation")
    widgets["clear_btn"].pack(side = "left", padx = 6)


    '''
    --------   Output Box   --------
    '''

    tk.Label(root, text = "Conversation / Logs:").pack(anchor = "w", padx = 10)
    output_text = scrolledtext.ScrolledText(root, wrap="word")
    output_text.pack(padx=10, pady=(0,10), fill="both", expand=True)
    #pass into widgets dict
    widgets["output_text"] = output_text


    # Text Styles
    header_font = font.Font(size = 12, family = "Helvetica", weight = "bold")
    user_font   = font.Font(family="Helvetica", size=11)
    assistant_font = font.Font(family="Helvetica", size=11)

    # User Message tags
    output_text.tag_config("user_header", font=header_font, foreground="#1a73e8")
    output_text.tag_config("user_text", font=user_font, foreground="#1558b0")
    # Assistant Message tags
    output_text.tag_config("assistant_header", font=header_font, foreground="#34a853")
    output_text.tag_config("assistant_text", font=assistant_font, foreground="#2d7d46")
    # Thinking text tag
    output_text.tag_config("thinking", font=user_font, foreground="gray")
    
    # spacer tag (just a blank line)
    output_text.tag_config("spacer", font=user_font)
    

    # Code block tags
    output_text.tag_config("code_keyword", foreground="#005cc5")  # Blue
    output_text.tag_config("code_string", foreground="#032f62")   # Dark teal
    output_text.tag_config("code_comment", foreground="#22863a")  # Green
    output_text.tag_config("code_number", foreground="#b31d28")   # Red-ish
    output_text.tag_config("code_plain", foreground="#24292e")    # Black
    # Code block separator tag
    output_text.tag_config("code_separator", foreground="#8a8a8a", font=("Helvetica", 10, "italic"))

    return widgets

