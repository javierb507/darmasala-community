import ast

with open('app.py', 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == 'crear_contexto_calendario':
            print(f"FOUND: crear_contexto_calendario at line {node.lineno}")
