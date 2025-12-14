#the purpose of this module is to impliment logic so that rag is only applied in certain cases.
import subprocess
import numpy as np
import json
import llm.models
from pathlib import Path



def determine_rag_necessity(prompt: str) -> bool:
    """
    This funcitons sole purpose is to improve query response by determining if a rag search is neccessary.  
    returns rag_necessity as True if rag is determined to be neccessary
    """


    #simple heuristic checks for keywords that might indicate the need for RAG
    rag_necessity = hueristic_checker(prompt)

    #rag_necessity =
    








    return rag_necessity

#simple heuristic checks for keywords that might indicate the need for RAG
def hueristic_checker(prompt:str) -> bool:
    lower_prompt = prompt.lower()
    heuristic_check_list = ["in the context", 
                            "from the context", 
                            "using the file", 
                            "from the file", 
                            "included in the",
                            "in the provided"]
    for check in heuristic_check_list:
        if check in lower_prompt:
            return True
        
    return False

def cosine_similarity(a, b):
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    # Handle edge case where one vector has zero norm
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

def embedding_checker(prompt: str) -> bool:
    try:
        result = subprocess.run(
            ["ollama", "run", "embeddinggemma:300m", prompt],
            capture_output=True,
            text=True,  
            check=True
        )
        stdout = result.stdout.strip()
        
    except subprocess.CalledProcessError as e:
        print(f"Error running Ollama: {e.stderr}")
        return False  
    
    try:
        query_vector = np.array(json.loads(stdout))
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in stdout from Ollama: {e}")
        return False
    
    vector_file = Path("knowledge_base/embeddings/rag_check_vectors.json")  
    try:
        with vector_file.open("r", encoding="utf-8") as f:
            reference_vector = np.array(json.load(f))
    except FileNotFoundError:
        print(f"Reference vector file not found: {vector_file}")
        return False
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in reference vector file: {e}")
        return False
    
    similarity = cosine_similarity(query_vector, reference_vector)
    threshold = 0.5
    
    return similarity >= threshold


# Test function with examples
def test_determine_rag_necessity():
    """Test cases for the RAG necessity function"""
    
    test_cases = [
        ("Please review the context file", True),
        ("Show me the document", True),
        ("How do you feel today?", False),
        ("Include this information", True),
        ("FILE contains important data", True),
        ("General question about programming", False),
        ("Context matters here", True),
        ("No special keywords here", False)
    ]
    
    print("Testing determine_rag_necessity function:")
    print("-" * 50)
    
    for prompt, expected in test_cases:
        result = determine_rag_necessity(prompt)
        status = "✓" if result == expected else "✗"
        print(f"{status} Prompt: '{prompt}'")
        print(f"   Expected: {expected}, Got: {result}")
        print()

# Run the tests
if __name__ == "__main__":
    test_determine_rag_necessity()