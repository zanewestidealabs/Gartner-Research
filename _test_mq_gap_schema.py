"""Quick test: verify MQ Gap schema + vendor data integration."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import SCHEMA_REGISTRY, SCHEMA_DISPLAY, load_schema_data, extract_sub_pillars

print('=== SCHEMA_REGISTRY check ===')
entry = SCHEMA_REGISTRY.get('MQ_Gap_Schema_App.json')
print(f'Registry entry: {entry}')

print('\n=== SCHEMA_DISPLAY check ===')
display = SCHEMA_DISPLAY.get('MQ_Gap_Schema_App.json')
print(f'Display entry: {display}')

print('\n=== load_schema_data check ===')
body = load_schema_data('MQ_Gap_Schema_App.json')
print(f'Top keys: {list(body.keys())[:8]}')
pillars = body.get('pillars', {})
print(f'Pillars: {list(pillars.keys())}')
sub_pillars = body.get('sub_pillars', {})
print(f'Sub-pillars count: {len(sub_pillars)}')
via01 = sub_pillars.get('VIA-01', {})
print(f'Sample sub-pillar (VIA-01): name={via01.get("name")}')
print(f'Has scoring_guidance: {"scoring_guidance" in via01}')
print(f'Has what_to_verify_publicly: {"what_to_verify_publicly" in via01}')
print(f'Has search_terms: {"search_terms" in via01}')

print('\n=== extract_sub_pillars check ===')
sps = extract_sub_pillars('MQ_Gap_Schema_App.json')
print(f'Extracted {len(sps)} sub-pillars')
for sp in sps[:3]:
    print(f'  {sp["id"]}: {sp["name"]} — activities: {len(sp.get("activities", []))}')

# Test 2: Vendor file
print('\n=== Vendor file check ===')
with open(os.path.join(os.path.dirname(__file__), 'MQ_Gap Vendor 2-1 Consolidated.json'), 'r', encoding='utf-8') as f:
    vdata = json.load(f)
v0 = vdata['vendors'][0]
print(f'Vendor count: {vdata["vendor_count"]}')
print(f'First vendor: {v0["vendor"]}')
fields = ['pillar_scores_v2_1', 'sub_pillar_scores_v2_1', 'sub_pillar_evidence',
          'sub_pillar_rationale_v2_1', 'sub_pillar_schema_labels', 'capability_analysis',
          'capability_coverage', 'research_status']
for field in fields:
    print(f'  Has {field}: {field in v0}')
print(f'Pillar scores: {v0["pillar_scores_v2_1"]}')
ev = v0.get('sub_pillar_evidence', {}).get('VIA-01', {})
print(f'Evidence sample (VIA-01) keys: {list(ev.keys())}')
print(f'Evidence excerpts count: {len(ev.get("excerpts", []))}')

print('\nAll checks passed!')
