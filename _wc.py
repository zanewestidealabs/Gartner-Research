import json
d = json.load(open('analyst_take_reports.json', 'r', encoding='utf-8'))
for i, s in enumerate(d['reports'][1]['body_sections']):
    wc = len(s['body'].split())
    print(f"Section {i}: {wc} words - {s['heading']}")
total = sum(len(s['body'].split()) for s in d['reports'][1]['body_sections'])
print(f"Total: {total}")
