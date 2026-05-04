"""Inspect MDR schema sub-pillar criteria and scoring scale."""
import json

with open('MDR_Services_Schema.json', 'r', encoding='utf-8-sig') as f:
    d = json.load(f)

body = d.get('mdr_services_taxonomy_v1.0', d)

# Scoring scale
meta = body.get('metadata', {})
scoring = meta.get('capability_scoring_scale', meta.get('scoring_scale', {}))
print("=== SCORING SCALE ===")
levels = scoring.get('scoring_logic', scoring.get('levels', {}))
for lvl_key in sorted(levels.keys()):
    lvl = levels[lvl_key]
    if isinstance(lvl, dict):
        print(f"  Level {lvl_key}: {lvl.get('label', '')} — {lvl.get('description', '')}")
    else:
        print(f"  Level {lvl_key}: {lvl}")

# Sub-pillars with criteria
sp = body.get('sub_pillars', {})
print(f"\n=== SUB-PILLARS ({len(sp)} total) ===")
for sp_id in sorted(sp.keys()):
    info = sp[sp_id]
    name = info.get('name', sp_id)
    criteria = info.get('ai_evaluation_criteria', [])
    verify = info.get('what_to_verify_publicly', [])
    evidence = info.get('ai_specific_evidence', [])
    print(f"\n{sp_id}: {name}")
    if criteria:
        print(f"  ai_evaluation_criteria ({len(criteria)}):")
        for c in criteria:
            print(f"    - {c}")
    if verify:
        print(f"  what_to_verify_publicly ({len(verify)}):")
        for v in verify:
            print(f"    - {v}")
    if evidence:
        print(f"  ai_specific_evidence ({len(evidence)}):")
        for e in evidence[:3]:
            print(f"    - {e}")
