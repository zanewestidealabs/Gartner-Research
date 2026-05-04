"""Get schema info for v2.2 build."""
import json

schema = json.load(open('Offensive_Security_Schema.json', encoding='utf-8'))

# Get all sub-pillar IDs and names
for p in schema.get('pillars', []):
    print(f"Pillar: {p['pillar_id']} - {p['pillar_name']}")
    for s in p.get('sub_pillars', []):
        print(f"  {s['sub_pillar_id']}: {s['sub_pillar_name']}")
    print()

# Scoring rubric
sr = schema.get('scoring_rubric', schema.get('scoring_methodology', {}))
print("Scoring rubric type:", type(sr).__name__)
if isinstance(sr, dict):
    for k, v in sr.items():
        desc = v if isinstance(v, str) else str(v)[:200]
        print(f"  {k}: {desc}")
elif isinstance(sr, list):
    for item in sr:
        print(f"  {item}")
