import os

file_path = 'app_recovered.py'
search_str = '@app.route'

try:
    with open(file_path, 'r', encoding='utf-16') as f:
        lines = f.readlines()
except:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

for i, line in enumerate(lines):
    if '/api/alumno' in line:
        print(f"Line {i+1}: {line.strip()}")
