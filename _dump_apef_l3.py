import json
d = json.load(open('ai_platform_ecosystem_framework_v1.json', encoding='utf-8'))
v = d['vendor_role_profiles']
for k, vv in v.items():
    comps = vv.get('components', [])
    print(f'\n=== {k} ({len(comps)}) ===')
    for layer in ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']:
        items = [c['name'] for c in comps if c.get('layer') == layer]
        print(f'  {layer} ({len(items)}): {", ".join(items)}')
