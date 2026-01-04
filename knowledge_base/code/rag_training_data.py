TRAINING_PROMPTS = [
    # RAG REQUIRED
    ("Review the provided file and explain the error", True),
    ("Using the context above, refactor this function", True),
    ("Here is a traceback from my app", True),
    ("Based on the document I shared", True),
    ("Analyze this Unity C# movement script", True),
    ("Analyze this code snippet and find bugs", True),
    ("Compare these two JSON configs I shared", True),
    ("Here is the error log from my application, what caused it?", True),
    ("Staying cosistent with the project structure write a movement script for the jester piece", True),
    ("From what I shared earlier, explain the issue", True),
    ("Here's my error log.  Also, generally, why does this happen in Python?", True),
    ("I shared a design doc - what would you change, and explain SOLID principles", True),


    # NO RAG
    ("Tell me a joke", False),
    ("What is polymorphism?", False),
    ("Explain Python decorators", False),
    ("How does gravity work?", False),
    ("Write a haiku about winter", False),
    ("Summarize the plot of 'The wise mans fear' by Patrick Rothfuss", False),
    ("What does this regex do: \\w+@\\w+\\.\\w+", False),
    ("Explain what a stack trace is", False),
    ("Write a Unity movement script from scratch", False),
]
