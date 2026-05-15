import json
d = json.load(open('CNAPP MQ Vendor 1-3 Researched.json', encoding='utf-8'))
for v in d['vendors']:
    print(f"{v['vendor']:24s}  {v.get('website','')}")
