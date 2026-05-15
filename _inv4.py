import json
data = json.load(open('CNAPP_MQ_Gap_Schema_App.json'))['cnapp_mq_gap_taxonomy_v1.0']
sp = data['sub_pillars']
print('SP type:', type(sp).__name__)
if isinstance(sp, dict):
    k0 = list(sp.keys())[0]
    print('first key:', k0)
    print('value:', json.dumps(sp[k0], indent=2)[:400])
elif isinstance(sp, list):
    print('first:', json.dumps(sp[0], indent=2)[:400])
