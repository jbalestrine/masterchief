import ast
import sys

def reformat_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    try:
        # Parse the AST
        tree = ast.parse(content)
        
        # Use ast.unparse if available (Python 3.9+), otherwise use a simple approach
        if hasattr(ast, 'unparse'):
            reformatted = ast.unparse(tree)
        else:
            # For older Python, just return the original
            reformatted = content
        
        with open(file_path, 'w') as f:
            f.write(reformatted)
        
        print("File reformatted successfully")
        return True
    except SyntaxError as e:
        print(f"SyntaxError: {e}")
        return False

if __name__ == "__main__":
    reformat_file('features/manager.py')