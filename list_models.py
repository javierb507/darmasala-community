import ast

with open('app.py', 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        # Check if it inherits from db.Model
        for base in node.bases:
            if isinstance(base, ast.Attribute) and base.attr == 'Model':
                print(f"Model: {node.name}")
            elif isinstance(base, ast.Name) and base.id == 'db.Model': # unlikely
                print(f"Model: {node.name}")
