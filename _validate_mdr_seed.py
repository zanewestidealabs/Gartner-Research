import json

data = json.load(open('MDR Services Vendor 1-0 Seed.json', 'r', encoding='utf-8'))
vendors = data['vendors']
print(f'Total vendors: {len(vendors)}')
print()

regions = {}
types = {}
primaries = {}
pricing = {}
ir_types = {}

for v in vendors:
    r = v['region']
    t = v['mdr_service_type']
    p = v['primary_capability']
    pr = v['pricing_model_type']
    ir = v['ir_focus_type']
    regions[r] = regions.get(r, 0) + 1
    types[t] = types.get(t, 0) + 1
    primaries[p] = primaries.get(p, 0) + 1
    pricing[pr] = pricing.get(pr, 0) + 1
    ir_types[ir] = ir_types.get(ir, 0) + 1

print('--- By Region ---')
for k, v in sorted(regions.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}')

print('\n--- By MDR Service Type ---')
for k, v in sorted(types.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}')

print('\n--- By Primary Capability ---')
for k, v in sorted(primaries.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}')

print('\n--- By Pricing Model Type ---')
for k, v in sorted(pricing.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}')

print('\n--- By IR Focus Type ---')
for k, v in sorted(ir_types.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}')

startups = [v['vendor'] for v in vendors if v['is_startup']]
ai_first = [v['vendor'] for v in vendors if v['is_ai_first']]
print(f'\nStartups ({len(startups)}): {startups}')
print(f'\nAI-First ({len(ai_first)}): {ai_first}')

# List all vendors
print('\n--- Full Vendor List ---')
for i, v in enumerate(vendors, 1):
    print(f'{i:3}. {v["vendor"]:40} | {v["region"]:15} | {v["mdr_service_type"]:18} | {v["primary_capability"]}')
