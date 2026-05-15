import json
d = json.load(open('Preemptive Cybersecurity Vendor 2-2 Validated.json', encoding='utf-8'))

# Re-check: which vendors have ALL 4 of (ADR-01, ADR-02, ADR-03, ADR-04) = 0.0?
PROD_SIDS = [f'{p}-{i:02d}' for p in ('EXM','AMT','ADR','PPM') for i in range(1,5)]
all_zero = []
mostly_zero = []
for v in d['vendors']:
    sp = v['sub_pillar_scores_validated_v22']
    spe = v.get('sub_pillar_evidence') or {}
    zeros = [sid for sid in PROD_SIDS if sp.get(sid, 0) == 0]
    excerpts = sum(len((spe.get(sid,{}) or {}).get('excerpts', [])) for sid in PROD_SIDS)
    urls = sum(len((spe.get(sid,{}) or {}).get('source_urls', [])) for sid in PROD_SIDS)
    if len(zeros) == 16:
        all_zero.append((v['vendor'], excerpts, urls, v.get('expected_coverage')))
    elif len(zeros) >= 12:
        mostly_zero.append((v['vendor'], len(zeros), excerpts, urls))

print('=== vendors with ALL 16 product cells = 0 ===')
for n, e, u, exp in all_zero:
    print(f'  {n:35} excerpts={e:4} urls={u:4} expected={exp}')

print()
print('=== vendors with >=12 product cells = 0 ===')
for n, z, e, u in mostly_zero:
    print(f'  {n:35} zeros={z:2} excerpts={e:4} urls={u:4}')

# Also show Axonius `research` block
ax = next(v for v in d['vendors'] if v['vendor']=='Axonius')
r = ax.get('research', {})
print()
print('=== Axonius research block ===')
for k in ('status','source','urls_used','pages_ok','timestamp_utc'):
    val = r.get(k)
    if isinstance(val, list): print(f'  {k} ({len(val)}): {val[:5]}')
    else: print(f'  {k}: {val}')
