"""Quick inspection of MDR schema and vendor data for report planning."""
import json

# Schema
with open('MDR_Services_Schema.json', 'r', encoding='utf-8-sig') as f:
    schema = json.load(f)['mdr_services_taxonomy_v1.0']

print("=== PILLARS ===")
for code, p in schema['pillars'].items():
    print(f"  {code}: {p['name']}")

print("\n=== SUB-PILLARS ===")
sps = schema['sub_pillars']
for sp_id in sorted(sps.keys()):
    sp = sps[sp_id]
    wv = sp.get('what_to_verify_publicly', [])
    print(f"  {sp_id}: {sp['name']} ({len(wv)} criteria)")

# Vendor data
with open('MDR Services Vendor 2-1 Consolidated.json', 'r', encoding='utf-8-sig') as f:
    vdata = json.load(f)

vendors = vdata['vendors']
print(f"\n=== VENDORS ({len(vendors)} total) ===")
for v in vendors[:5]:
    name = v.get('vendor', 'unknown')
    ps = v.get('pillar_scores_v2_1', {})
    sps_scores = v.get('sub_pillar_scores_v2_1', {})
    print(f"  {name}: {len(ps)} pillars, {len(sps_scores)} sub-pillars")

# Check for overall_score or computed field
v0 = vendors[0]
print(f"\n=== SAMPLE VENDOR: {v0['vendor']} ===")
print(f"  pillar_scores_v2_1 keys: {list(v0.get('pillar_scores_v2_1',{}).keys())}")
for field in ['overall_score_v2_1', 'overall_score', 'evidence_flag', 'evidence_quality_summary',
              'research_confidence_v2_1', 'v2_1_adjustment_summary', 'capability_analysis',
              'notable_differentiation_v2_1', 'key_differentiators', 'sub_pillar_evidence']:
    val = v0.get(field)
    if val is not None:
        if isinstance(val, str):
            print(f"  {field}: str ({len(val)} chars): {val[:120]}")
        elif isinstance(val, dict):
            print(f"  {field}: dict ({len(val)} keys)")
        elif isinstance(val, list):
            print(f"  {field}: list ({len(val)} items)")
        else:
            print(f"  {field}: {val}")
    else:
        print(f"  {field}: NOT PRESENT")

# Check sub_pillar_evidence structure
spe = v0.get('sub_pillar_evidence', {})
if spe:
    k1 = list(spe.keys())[0]
    print(f"\n=== sub_pillar_evidence sample ({k1}) ===")
    print(json.dumps(spe[k1], indent=2)[:500])
