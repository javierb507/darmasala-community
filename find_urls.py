import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

urls = re.findall(r"url_for\('([^']+)'", content)
for url in sorted(set(urls)):
    print(url)
