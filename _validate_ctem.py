import json

with open('CTEM_Offensive_Security_Schema.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

root = data['ctem_offensive_security_taxonomy_v1.0']
pillars = root['pillars']
subs = root['sub_pillars']
pricing = root['pricing_evaluation']['dimensions']
ai_levels = root['ai_maturity_model']['levels']

print(f"Pillars: {len(pillars)}")
print(f"Sub-pillars: {len(subs)}")
print(f"Pricing dimensions: {len(pricing)}")
print(f"AI maturity levels: {len(ai_levels)}")
print()
print("Pillar codes:", list(pillars.keys()))
print()
for code, p in pillars.items():
    sub_count = sum(1 for k in subs if k.startswith(code))
    print(f"  {code}: {p['name']} ({sub_count} sub-pillars)")
    for k in sorted(subs):
        if k.startswith(code):
            print(f"    {k}: {subs[k]['name']}")
            wtvp = subs[k].get('what_to_verify_publicly', [])
            print(f"         what_to_verify: {len(wtvp)} items, search_terms: {len(subs[k].get('search_terms', []))}")
print()
print("Pricing dimensions:")
for d in pricing:
    print(f"  {d['id']}: {d['name']}")
    print(f"         what_to_evaluate: {len(d.get('what_to_evaluate', []))} items")
print()
print("AI Maturity Levels:")
for level, info in ai_levels.items():
    print(f"  Level {level}: {info['name']} ({len(info.get('indicators', []))} indicators)")
print()
print("Vendor classification fields:", list(root['vendor_classification']['fields'].keys()))
print()
print("VALID JSON - Schema created successfully!")
