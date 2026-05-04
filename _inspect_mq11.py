import json
d = json.load(open('CNAPP MQ Vendor 1-1 Researched.json', encoding='utf-8'))
print('top-level keys:', list(d.keys())[:10] if isinstance(d, dict) else 'list')
v = d.get('vendors') if isinstance(d, dict) else d
print('vendor count:', len(v))
print('first vendor keys:', list(v[0].keys())[:25])
key = 'vendor_name' if 'vendor_name' in v[0] else ('vendor' if 'vendor' in v[0] else list(v[0].keys())[0])
print('using key:', key)
for i, x in enumerate(v):
    print(f'  {i+1:2d}. {x[key]}')
# show one sub-pillar score block
print('\nsample sub_pillar_scores_current:')
print(json.dumps(v[0].get('sub_pillar_scores_current', {}), indent=2)[:800])
print('\nsample mq_gap_sub_pillar_rationales (first 2):')
rats = v[0].get('mq_gap_sub_pillar_rationales', {})
for k in list(rats.keys())[:2]:
    print(f'  {k}: {rats[k][:200]}')
