import ast
import sys

def fix_indentation(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    try:
        # Parse the AST
        tree = ast.parse(content)
        
        # If parsing succeeds, the file is syntactically correct
        print("File is syntactically correct")
        return True
    except SyntaxError as e:
        print(f"SyntaxError at line {e.lineno}: {e.msg}")
        return False

if __name__ == "__main__":
    fix_indentation('features/manager.py')