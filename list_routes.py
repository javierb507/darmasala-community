import ast
import re

file_path = 'app.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
    tree = ast.parse(content)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute) and decorator.func.attr == 'route':
                route = decorator.args[0].value if isinstance(decorator.args[0], ast.Constant) else "???"
                print(f"Line {node.lineno}: {route} -> {node.name}")
