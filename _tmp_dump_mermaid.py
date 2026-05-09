import json
data = json.load(open('static/docs_architecture.json', encoding='utf-8'))
sections = [s for t in data['tabs'] for s in t['sections']]
for s in sections:
    for b in s.get('content', []):
        if b.get('type') == 'mermaid':
            lines = b['value'].split('\n')
            print(f'=== {s["title"]} ({len(lines)} lines) ===')
            for i, l in enumerate(lines, 1):
                print(f'{i:3}: {l}')
            print()
