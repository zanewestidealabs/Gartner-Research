"""Get schema info for v2.2 build - writes to file."""
import json

schema = json.load(open('Offensive_Security_Schema.json', encoding='utf-8'))

lines = []

# Get all sub-pillar IDs and names
for p in schema.get('pillars', []):
    lines.append(f"Pillar: {p['pillar_id']} - {p['pillar_name']}")
    for s in p.get('sub_pillars', []):
        lines.append(f"  {s['sub_pillar_id']}: {s['sub_pillar_name']}")
    lines.append("")

# Scoring rubric
sr = schema.get('scoring_rubric', schema.get('scoring_methodology', {}))
lines.append(f"Scoring rubric type: {type(sr).__name__}")
if isinstance(sr, dict):
    for k, v in sr.items():
        desc = v if isinstance(v, str) else str(v)[:200]
        lines.append(f"  {k}: {desc}")
elif isinstance(sr, list):
    for item in sr:
        lines.append(f"  {item}")

with open('_schema_info_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("Done. Wrote to _schema_info_output.txt")
