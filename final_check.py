import ast

with open('app.py', 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())

func_names = set()
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        func_names.add(node.name)

targets = ['alumnos', 'calendario', 'calendario_unificado', 'editar_sesion_yogaterapia', 
           'horarios', 'nueva_yogaterapia', 'nuevo_alumno', 'registrar_asistencia', 
           'reporte_asistencia', 'ver_sesion_yogaterapia', 'asistencias_historico']

for t in targets:
    if t in func_names:
        print(f"EXISTS: {t}")
    else:
        print(f"MISSING: {t}")
