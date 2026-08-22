import os
import sys

# Allow tests/ to import lexer.py, parser.py, semantic.py, main.py
# which live one directory up in the project root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
