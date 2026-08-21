import os, re
root = r'C:\Gartner'
pattern = re.compile(r'(?i)AEOF|APEF')
name_matches = []
content_matches = []
for dirpath, dirnames, filenames in os.walk(root):
    path = dirpath.replace('\\', '/')
    if '/.venv/' in path or '/research/cache/' in path or '/.git/' in path:
        continue
    for fn in filenames:
        full = os.path.join(dirpath, fn)
        if pattern.search(fn):
            name_matches.append(full)
        if fn.lower().endswith(('.py', '.md', '.json', '.txt', '.js', '.html')):
            try:
                with open(full, 'r', encoding='utf-8', errors='replace') as f:
                    txt = f.read()
                if pattern.search(txt):
                    content_matches.append(full)
            except Exception:
                pass
print('name_matches', len(name_matches))
for p in name_matches[:50]:
    print('NAME', p)
print('content_matches', len(content_matches))
for p in content_matches[:50]:
    print('CONTENT', p)
