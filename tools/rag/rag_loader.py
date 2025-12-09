import os

def load_documents(folder_path = "knowledge_base"):
    """ 
    Loads all text like files from knowledge base folder
    Returns a list of dicts: {'filename': str, 'content':str}
    """

    compatible_extensions = (".txt", ".md", ".py", ".json")

    documents = []

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(compatible_extensions):
            continue  # Inverted if for fewer nests

        full_path = os.path.join(folder_path, filename)

        if not can_load_file(full_path):
            continue

        content = read_file_content(full_path)
        
        documents.append({
            "filename" : filename,
            "content": content
        })

    return documents

def can_load_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            f.read() #just trying to open the file to test for issues
        return True
    except Exception as e:
        print(f"Failed to open {filepath}: {e}")
        return False

def read_file_content(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Failed to read {filepath}: {e}")
        return "" # or raise the exception if you want to halt execution
    