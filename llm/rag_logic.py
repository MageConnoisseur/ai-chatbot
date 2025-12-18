#the purpose of this module is to impliment logic so that rag is only applied in certain cases.
import subprocess
import re
import numpy as np
import json


RAG_SIMILARITY_THRESHOLD = 0.5 # Adjust this threshold based on empirical testing



def determine_rag_necessity(prompt: str) -> bool:
    """
    Determine whether RAG is necessary for a prompt.
    """

    # FAST PATH — obvious RAG cases
    if fast_heuristic_checker(prompt):
        return True

    # FAST NEGATIVE — obvious non-RAG cases
    if is_definitely_non_rag(prompt):
        return False

    # SLOW PATH — ambiguous cases
    return slow_embedding_checker(prepare_for_embedding(prompt))


#simple heuristic checks for keywords that might indicate the need for RAG
def fast_heuristic_checker(prompt:str) -> bool:

    lower_prompt = prompt.lower()


    # Length check
    if len(prompt) > 1200:
        return True

    # Code block present
    if "```" in prompt:
        return True

    # File or path references
    if re.search(r"\.(py|cs|json|yaml|yml)", lower_prompt):
        return True


    # Heuristic checks for context-related keywords
    heuristic_check_list = ["in the context", 
                            "from the context", 
                            "using the file", 
                            "from the file", 
                            "included in the",
                            "in the provided",
                            "tkinter", "unity", "c#", "script", 
                            "error", "traceback", "wizard", "piece", 
                            "movement", "teleport", "artifact",
                            "game", "mechanic", "design", "lore"]
    for check in heuristic_check_list:
        if check in lower_prompt:
            return True
        
    return False


def is_definitely_non_rag(prompt: str) -> bool:
    """
    Returns True if we are confident this prompt does NOT need RAG.
    """
    lower = prompt.lower()

    if len(prompt) < 60:
        return True

    casual_phrases = [
        "tell me a joke",
        "how are you",
        "what do you think",
        "explain generally",
        "in general",
        "philosophically",
        "give me advice",
        "what is love",
        "how to be",
        "what is the meaning",
    ]

    return any(p in lower for p in casual_phrases)


def cosine_similarity(a, b):
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    # Handle edge case where one vector has zero norm
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

def normalize(v):
    norm = np.linalg.norm(v)
    return v if norm == 0 else v / norm

def slow_embedding_checker(prompt: str) -> bool:
    try:
        result = subprocess.run(
            ["ollama", "run", "embeddinggemma:300m"],
            input=prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  
            check=True
        )
        stdout = result.stdout.strip()
        
    except subprocess.CalledProcessError as e:
        print(f"Error running Ollama: {e.stderr}")
        return False  
    
    query_vector = extract_embedding(stdout)
    if query_vector is None:
        print("Failed to extract embedding from Ollama output")
        return False

    
    vector_file_path= "knowledge_base/embeddings/rag_check_vectors.json"
    try:
        with open(vector_file_path, "r", encoding="utf-8") as f:
            
            data = json.load(f)

            if "rag_intent_vectors" not in data:
                print("Invalid RAG vector file format")
                return False

            reference_vectors = [
                np.array(v, dtype=np.float32)
                for v in data["rag_intent_vectors"]
            ]


    except FileNotFoundError:
        print(f"Reference vector file not found: {vector_file_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in reference vector file: {e}")
        return False
    
    
    query_vector = normalize(query_vector)

    similarities = [
        cosine_similarity(query_vector, normalize(ref))
        for ref in reference_vectors
]


    if not reference_vectors:
        print("No reference RAG vectors found")
        return False

    threshold = RAG_SIMILARITY_THRESHOLD
    return max(similarities) >= threshold



def prepare_for_embedding(prompt: str) -> str:
    """
    Cleanes prompt up to eleminate noise for embedding
    """
    front_end_length = 500
    back_end_length = 300

    prompt = re.sub(r"```.*?```", "", prompt, flags=re.S)

    front_part = prompt[:front_end_length]
    back_part = prompt[-back_end_length:]

    return front_part + "\n...\n" + back_part



def extract_embedding(stdout: str) -> np.ndarray | None:
    """
    Safely extract an embedding vector from Ollama stdout.
    Supports both raw list and {"embedding": [...]} formats.
    """
    try:
        data = json.loads(stdout)

        if isinstance(data, dict) and "embedding" in data:
            return np.array(data["embedding"], dtype=np.float32)

        if isinstance(data, list):
            return np.array(data, dtype=np.float32)

        return None

    except json.JSONDecodeError:
        return None










def run_all_tests():
    print("\n================ RAG MODULE TEST SUITE ================\n")

    # -----------------------------------------------------
    # fast_heuristic_checker tests
    # -----------------------------------------------------
    print("[TEST] fast_heuristic_checker")

    heuristic_tests = [
        ("Here is some code ```print('hi')```", True),
        ("This references file main.py", True),
        ("Unity C# movement script", True),
        ("How are you today?", False),
        ("Tell me a joke", False),
        ("Error traceback occurred", True),
        ("Short harmless question", False),
    ]

    for prompt, expected in heuristic_tests:
        result = fast_heuristic_checker(prompt)
        status = "✓" if result == expected else "✗"
        print(f" {status} '{prompt[:40]}...' → {result}")

    # -----------------------------------------------------
    # prepare_for_embedding tests
    # -----------------------------------------------------
    print("\n[TEST] prepare_for_embedding")

    raw_prompt = (
        "START CONTEXT\n"
        "```python\nprint('this should be removed')\n```\n"
        "MIDDLE CONTENT\n"
        "END QUESTION?"
    )

    cleaned = prepare_for_embedding(raw_prompt)

    assert "print(" not in cleaned, "❌ Code block not removed"
    assert "START CONTEXT" in cleaned, "❌ Front not preserved"
    assert "END QUESTION?" in cleaned, "❌ Back not preserved"
    assert "..." in cleaned, "❌ Separator missing"

    print(" ✓ Code blocks removed")
    print(" ✓ Front/back preserved")
    print(" ✓ Separator inserted")

    # -----------------------------------------------------
    # normalize tests
    # -----------------------------------------------------
    print("\n[TEST] normalize")

    v = np.array([3.0, 4.0])
    n = normalize(v)
    assert np.isclose(np.linalg.norm(n), 1.0), "❌ Vector not normalized"

    zero = np.array([0.0, 0.0])
    nz = normalize(zero)
    assert np.array_equal(zero, nz), "❌ Zero vector altered"

    print(" ✓ Normal vector normalized")
    print(" ✓ Zero vector safe")

    # -----------------------------------------------------
    # cosine_similarity tests
    # -----------------------------------------------------
    print("\n[TEST] cosine_similarity")

    a = np.array([1.0, 0.0])
    b = np.array([1.0, 0.0])
    c = np.array([0.0, 1.0])

    assert cosine_similarity(a, b) > 0.99, "❌ Same vectors mismatch"
    assert abs(cosine_similarity(a, c)) < 1e-6, "❌ Orthogonal vectors mismatch"
    assert cosine_similarity(a, np.array([0.0, 0.0])) == 0.0, "❌ Zero vector case failed"

    print(" ✓ Identical vectors")
    print(" ✓ Orthogonal vectors")
    print(" ✓ Zero vector safe")

    # -----------------------------------------------------
    # extract_embedding tests
    # -----------------------------------------------------
    print("\n[TEST] extract_embedding")

    valid_list = "[1.0, 2.0, 3.0]"
    valid_dict = '{"embedding": [4.0, 5.0]}'
    invalid_json = "{not json}"
    invalid_struct = '{"foo": 123}'

    assert extract_embedding(valid_list) is not None, "❌ List format failed"
    assert extract_embedding(valid_dict) is not None, "❌ Dict format failed"
    assert extract_embedding(invalid_json) is None, "❌ Invalid JSON not caught"
    assert extract_embedding(invalid_struct) is None, "❌ Invalid structure not caught"

    print(" ✓ List format supported")
    print(" ✓ Dict format supported")
    print(" ✓ Invalid JSON rejected")
    print(" ✓ Invalid structure rejected")

    # -----------------------------------------------------
    # determine_rag_necessity (heuristic-only path)
    # -----------------------------------------------------
    print("\n[TEST] determine_rag_necessity (heuristic only)")

    # Monkey-patch slow checker to ensure it's not used
    def fake_slow_checker(_):
        raise RuntimeError("❌ slow_embedding_checker should not run")

    global slow_embedding_checker
    original_slow = slow_embedding_checker
    slow_embedding_checker = fake_slow_checker

    try:
        assert determine_rag_necessity("Unity movement script") is True
        assert determine_rag_necessity("Tell me a joke") is False
        print(" ✓ Heuristic short-circuit works")
    finally:
        slow_embedding_checker = original_slow

    print("\n================ ALL TESTS COMPLETE ================\n")

if __name__ == "__main__":
    run_all_tests()

