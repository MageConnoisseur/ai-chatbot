import tkinter as tk
from gui.widgets import create_widgets
from gui.events import bind_events

def run_app():
    root = tk.Tk()
    root.title("ChatBot Application")
    root.minsize(700, 500)

    widgets = create_widgets(root)
    bind_events(root, widgets)

    root.mainloop()

if __name__ == "__main__":
    run_app()
    