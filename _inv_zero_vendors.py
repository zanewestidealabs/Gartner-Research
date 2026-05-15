import json
d = json.load(open('Preemptive Cybersecurity Vendor 2-2 Validated.json', encoding='utf-8'))

# Identify vendors with zero evidence across ALL product sub-pillars (likely scrape failures)
print('=== vendors with NO evidence across all 16 product sub-pillars ===')
PROD_SIDS = [f'{p}-{i:02d}' for p in ('EXM','AMT','ADR','PPM') for i in range(1,5)]
for v in d['vendors']:
    spe = v.get('sub_pillar_evidence') or {}
    total_excerpts = sum(len((spe.get(sid,{}) or {}).get('excerpts', [])) for sid in PROD_SIDS)
    total_urls = sum(len((spe.get(sid,{}) or {}).get('source_urls', [])) for sid in PROD_SIDS)
    if total_excerpts == 0:
        print(f'  {v["vendor"]:35} excerpts=0 urls={total_urls} expected={v.get("expected_coverage")}')

print()
print('=== research targets file count ===')
t = json.load(open('precyber_research_targets.json', encoding='utf-8'))
print('count:', t['count'])
# group by vendor
from collections import Counter
by_vendor = Counter()
for r in t['targets']:
    by_vendor[r['vendor']] += 1
print('vendors with targets:', len(by_vendor))
for vname, n in by_vendor.most_common(15):
    print(f'  {vname:40} {n}')

# Check what URLs were tried originally (sub_pillar_evidence -> source_urls union)
print()
print('=== representative original URLs for one zero-evidence vendor ===')
zero_v_names = []
for v in d['vendors']:
    spe = v.get('sub_pillar_evidence') or {}
    total_excerpts = sum(len((spe.get(sid,{}) or {}).get('excerpts', [])) for sid in PROD_SIDS)
    if total_excerpts == 0:
        zero_v_names.append(v['vendor'])
        # print all keys to see what fields exist
        print(f'\n--- {v["vendor"]} ---')
        print('keys:', sorted([k for k in v.keys() if not k.startswith('_')])[:40])
        # any URL-like fields?
        for k in ['research', 'urls', 'source_urls', 'website', 'homepage', 'evidence_urls', 'all_urls']:
            if k in v:
                val = v[k]
                if isinstance(val, list): print(f'  {k}: {val[:3]}')
                elif isinstance(val, dict): print(f'  {k} keys: {list(val.keys())[:10]}')
                else: print(f'  {k}: {str(val)[:200]}')
        break
print()
print('all zero-evidence vendors:', zero_v_names)
