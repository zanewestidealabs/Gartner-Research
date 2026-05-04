"""Extract sub-pillar IDs and names from schema."""
import json

schema = json.load(open('Offensive_Security_Schema.json', encoding='utf-8'))
tax = schema.get('offensive_security_taxonomy_v1.0', schema)

subs = tax.get('sub_pillars', {})
with open('_sp_names.txt', 'w') as f:
    for sp_id in sorted(subs.keys()):
        name = subs[sp_id].get('name', '')
        f.write(f"{sp_id}|{name}\n")

print(f"Wrote {len(subs)} sub-pillars")

# Also get scoring rubric
scoring = tax.get('metadata', {}).get('capability_scoring_scale', {}).get('scoring_logic', {})
with open('_scoring_rubric.txt', 'w') as f:
    for level, desc in sorted(scoring.items()):
        f.write(f"{level}|{desc}\n")

print("Done")
