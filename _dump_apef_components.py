import json
d = json.load(open('ai_platform_ecosystem_framework_v1.json', encoding='utf-8-sig'))
for key, v in d['vendor_role_profiles'].items():
    print(f"\n=== {v.get('display_name', key)} ({key}) ===")
    for c in v.get('components', []):
        print(f"  [{c.get('layer','?')}] {c['name']:38s} type={c.get('type','?'):16s} id={c['id']}")
