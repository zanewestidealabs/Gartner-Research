import json

d = json.load(open('CNAPP Vendor 1-2 Researched.json', encoding='utf-8'))
v = d['vendors'][0]
print('Wiz rationales_v1 keys:', list((v.get('rationales_v1') or {}).keys())[:5])
rv1 = v.get('rationales_v1') or {}
sample_keys = list(rv1.keys())[:2]
for k in sample_keys:
    print(f'\n--- {k} ---')
    val = rv1[k]
    if isinstance(val, str):
        print(val[:500])
    else:
        print(json.dumps(val, indent=2)[:500])

# Check for any other rationale-like fields with URLs
print()
print('All vendor keys for Wiz:')
for k in v.keys():
    val = v[k]
    if isinstance(val, dict) and val:
        print(f'  {k}: dict with {len(val)} keys')
    elif isinstance(val, list):
        print(f'  {k}: list len={len(val)}')
    else:
        print(f'  {k}: {type(val).__name__}')
