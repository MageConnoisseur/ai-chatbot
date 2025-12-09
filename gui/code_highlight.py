from pygments import lex
from pygments.lexers import guess_lexer, PythonLexer, JsonLexer
from pygments.token import Token

def insert_code_block(text_widget, code: str):
    """Insert syntax-highlighted code into a Tkinter Text widget."""
    # Add visible separators ABOVE and BELOW
    text_widget.insert("end", "------- CODE BLOCK START -------\n", "code_separator")

    try:
        lexer = guess_lexer(code)
    except Exception:
        lexer = PythonLexer()

    for token_type, token_value in lex(code, lexer):
        if token_type in Token.Keyword:
            tag = "code_keyword"
        elif token_type in Token.String:
            tag = "code_string"
        elif token_type in Token.Comment:
            tag = "code_comment"
        elif token_type in Token.Number:
            tag = "code_number"
        else:
            tag = "code_plain"

        text_widget.insert("end", token_value, tag)

    text_widget.insert("end", "\n------- CODE BLOCK END -------\n", "code_separator")


def classify_token(tok):
    """Return the Tkinter tag name for a Pygments token."""
    t = str(tok)

    if t.startswith("Token.Keyword"):
        return "code_keyword"
    if t.startswith("Token.String"):
        return "code_string"
    if t.startswith("Token.Comment"):
        return "code_comment"
    if t.startswith("Token.Number"):
        return "code_number"

    return "code_plain"