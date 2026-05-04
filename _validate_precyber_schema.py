"""Validate Preemptive Cybersecurity Schema and app.py registration."""
import json

# 1. Validate JSON
with open('Preemptive_Cybersecurity_Schema.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

top = data['preemptive_cybersecurity_taxonomy_v1.0']
print('=== Schema loaded OK ===')

# 2. Count pillars and sub-pillars
pillars = top['pillars']
sub_pillars = top['sub_pillars']
print(f'Pillars: {len(pillars)} - {list(pillars.keys())}')
print(f'Sub-pillars: {len(sub_pillars)}')
for sp_id, sp_data in sub_pillars.items():
    print(f'  {sp_id}: {sp_data["name"]}')

# 3. Verify structure matches app.py expectations
for sp_id, sp_data in sub_pillars.items():
    pillar_code = sp_id.split('-')[0]
    assert pillar_code in pillars, f'{sp_id} has no parent pillar {pillar_code}'
    assert 'name' in sp_data
    assert 'expanded_definition' in sp_data
    assert 'what_to_verify_publicly' in sp_data
print('\nAll sub-pillars have valid parent pillars and required fields')

# 4. Verify SCHEMA_REGISTRY entry
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()
assert 'Preemptive_Cybersecurity_Schema.json' in app_code
print('Found in SCHEMA_REGISTRY')
assert 'PreCyber' in app_code
print('Found in SCHEMA_DISPLAY')
assert 'preemptive_cybersecurity_taxonomy' in app_code
print('Found in auto-detect logic')

print('\n=== ALL CHECKS PASSED ===')
