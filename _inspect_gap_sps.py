import json
s = json.load(open('CNAPP_MQ_Gap_Schema_App.json', encoding='utf-8'))
# find sub-pillars
sps = []
for p in s.get('pillars', []):
    for sp in p.get('sub_pillars', []):
        sps.append((sp['id'], sp['name'], sp.get('description', '')[:140]))
print('count:', len(sps))
for sid, name, desc in sps:
    print(f'{sid:8s} {name}')
    print(f'         {desc}')
