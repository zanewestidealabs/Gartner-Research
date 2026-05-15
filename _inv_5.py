import json
d = json.load(open('Preemptive Cybersecurity Vendor 2-2 Validated.json', encoding='utf-8'))

PROD_SIDS = [f'{p}-{i:02d}' for p in ('EXM','AMT','ADR','PPM') for i in range(1,5)]
ALL_SIDS = PROD_SIDS + [f'{p}-05' for p in ('EXM','AMT','ADR','PPM')] + [f'SVC-{i:02d}' for i in range(1,5)]

print(f'{"vendor":40} {"prod_sum":>9} {"prod_zeros":>11} {"all_sum":>8} {"all_zeros":>10}  expected')
print('-' * 120)
suspects = []
for v in d['vendors']:
    sp = v['sub_pillar_scores_validated_v22']
    prod_scores = [sp.get(s,0) for s in PROD_SIDS]
    all_scores = [sp.get(s,0) for s in ALL_SIDS]
    prod_sum = sum(prod_scores); prod_zeros = sum(1 for s in prod_scores if s==0)
    all_sum = sum(all_scores); all_zeros = sum(1 for s in all_scores if s==0)
    if prod_sum == 0 or prod_zeros >= 14:
        suspects.append((v['vendor'], prod_sum, prod_zeros, all_sum, all_zeros, v.get('expected_coverage')))

for s in suspects:
    print(f'{s[0]:40} {s[1]:9} {s[2]:11} {s[3]:8} {s[4]:10}  {s[5]}')

# also list any vendor with 0 sum across ANY meaningful subset
print()
print(f'count with prod_sum==0: {sum(1 for v in d["vendors"] if sum(v["sub_pillar_scores_validated_v22"].get(s,0) for s in PROD_SIDS)==0)}')
print(f'count with all_sum==0:  {sum(1 for v in d["vendors"] if sum(v["sub_pillar_scores_validated_v22"].get(s,0) for s in ALL_SIDS)==0)}')

# Maybe user is looking at pillar scores
print()
print('=== vendors where ALL 5 pillars (incl SVC) score 0 ===')
for v in d['vendors']:
    ps = v.get('pillar_scores_validated_v22', {})
    if all(ps.get(p,0)==0 for p in ('EXM','AMT','ADR','PPM','SVC')):
        print(f'  {v["vendor"]}  pillar_scores={ps}')

print()
print('=== bottom-5 vendors by total pillar score ===')
ranked = sorted(d['vendors'], key=lambda v: sum(v.get('pillar_scores_validated_v22',{}).values()))
for v in ranked[:8]:
    print(f'  {v["vendor"]:35} pillars={v.get("pillar_scores_validated_v22")}')
