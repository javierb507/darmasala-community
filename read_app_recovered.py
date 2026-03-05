import os

file_path = 'app_recovered.py'
start_line = 4500
end_line = 4600

try:
    with open(file_path, 'r', encoding='utf-16') as f:
        lines = f.readlines()
except:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

for i in range(max(0, start_line-1), min(len(lines), end_line)):
    print(f"{i+1}: {lines[i].strip()}")
