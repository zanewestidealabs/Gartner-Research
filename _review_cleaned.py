"""Review cleaned AIUC-1 report text for quality."""
import json

d = json.load(open('analyst_take_reports.json', 'r', encoding='utf-8'))
r = d['reports'][1]

print("LABEL:", r['label'])
print("TITLE:", r['title'])
print("SUBTITLE:", r['subtitle'][:120])
print()

for i, bs in enumerate(r['body_sections']):
    print(f"=== Body {i}: {bs['heading']} ===")
    print(bs['body'])
    print()

for i, ps in enumerate(r['positioning_statements']):
    print(f"=== PS {i}: {ps['label']} ===")
    print("POS:", ps['position'][:200])
    print("DRAMA:", ps['positionComponents']['drama'][:200])
    print("CONTEXT:", ps['justification']['context'][:200])
    print()
