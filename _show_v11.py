import json
with open('CNAPP Vendor 1-1 Researched.json', encoding='utf-8') as f:
    d = json.load(f)
print(f'Vendors: {len(d["vendors"])}')
print(f'{"Vendor":25s} {"Pgs":>3} {"Grade":>5}  CSPM CWPP CIEM SHIFT CDR DSPM FRNG')
print('-' * 78)
for v in d['vendors']:
    meta = v.get('research_metadata', {})
    ps = v.get('pillar_scores', {})
    parts = ' '.join(f'{ps.get(p,0):>4}' for p in ['CSPM','CWPP','CIEM','SHIFT','CDR','DSPM','FRNG'])
    print(f'{v["vendor"]:25s} {meta.get("pages_fetched",0):>3} {v.get("coverage_grade","?"):>5}  {parts}')
