import json, statistics

data = json.load(open('Product Market Readiness Vendor 1-0 Seed.json','r',encoding='utf-8'))
vendors = data['vendors']

sp_codes = [f'{p}-0{i}' for p in ['PPD','PCS','TDT','PCM','CTL'] for i in range(1,6)]

# Lowest scoring sub-pillar
lowest_sp = None
lowest_mean = 999
for sp in sp_codes:
    vals = [v.get('sub_pillar_scores',{}).get(sp,{}).get('gtm_messaging_score',0) for v in vendors]
    m = sum(vals)/len(vals)
    if m < lowest_mean:
        lowest_mean = m
        lowest_sp = sp
print(f'Lowest sub-pillar (all): {lowest_sp} = {lowest_mean:.2f}')

lowest_sp_nz = None
lowest_mean_nz = 999
for sp in sp_codes:
    vals = [v.get('sub_pillar_scores',{}).get(sp,{}).get('gtm_messaging_score',0) for v in vendors]
    nz = [x for x in vals if x > 0]
    if nz:
        m = sum(nz)/len(nz)
        if m < lowest_mean_nz:
            lowest_mean_nz = m
            lowest_sp_nz = sp
print(f'Lowest sub-pillar (non-zero): {lowest_sp_nz} = {lowest_mean_nz:.2f}')

# Vendors with gap < -1.0
neg_big = [v for v in vendors if v['overall_credibility_gap'] < -1.0]
print(f'Vendors with gap < -1.0: {len(neg_big)}')
for v in neg_big:
    print(f"  {v['vendor']}: {v['overall_credibility_gap']:.2f}")

# Gap distribution
print('\nGap distribution:')
bins = {'<-1.0': 0, '-1.0 to -0.5': 0, '-0.5 to -0.1': 0, '-0.1 to 0.1': 0, '0.1 to 0.5': 0, '0.5 to 1.0': 0, '>1.0': 0}
for v in vendors:
    g = v['overall_credibility_gap']
    if g < -1.0: bins['<-1.0'] += 1
    elif g < -0.5: bins['-1.0 to -0.5'] += 1
    elif g < -0.1: bins['-0.5 to -0.1'] += 1
    elif g <= 0.1: bins['-0.1 to 0.1'] += 1
    elif g <= 0.5: bins['0.1 to 0.5'] += 1
    elif g <= 1.0: bins['0.5 to 1.0'] += 1
    else: bins['>1.0'] += 1
for b, c in bins.items():
    print(f'  {b}: {c} ({100*c/len(vendors):.1f}%)')

# Pillar coverage
print('\nPillar coverage:')
for p in ['PPD','PCS','TDT','PCM','CTL']:
    nz = sum(1 for v in vendors if v['pillar_gtm_scores'].get(p,0) > 0)
    print(f'  {p} non-zero: {nz}/{len(vendors)} ({100*nz/len(vendors):.0f}%)')

# Top 10 over-claimers and under-marketers
print('\nTop 10 over-claimers:')
by_gap = sorted(vendors, key=lambda v: v['overall_credibility_gap'], reverse=True)
for v in by_gap[:10]:
    print(f"  {v['vendor']}: gap={v['overall_credibility_gap']:.2f}, GTM={v['overall_gtm_score']:.2f}, Proof={v['overall_proof_score']:.2f}")

print('\nTop 10 under-marketers:')
for v in by_gap[-10:]:
    print(f"  {v['vendor']}: gap={v['overall_credibility_gap']:.2f}, GTM={v['overall_gtm_score']:.2f}, Proof={v['overall_proof_score']:.2f}")

# PCM zero-coverage analysis
pcm_zero = sum(1 for v in vendors if v['pillar_gtm_scores'].get('PCM',0) == 0)
ctl_zero = sum(1 for v in vendors if v['pillar_gtm_scores'].get('CTL',0) == 0)
print(f'\nPCM zero vendors: {pcm_zero} ({100*pcm_zero/len(vendors):.0f}%)')
print(f'CTL zero vendors: {ctl_zero} ({100*ctl_zero/len(vendors):.0f}%)')

# Strong PPD+CTL but weak PCS+TDT pattern
pattern = sum(1 for v in vendors if 
    v['pillar_gtm_scores'].get('PPD',0) > 2.5 and v['pillar_gtm_scores'].get('CTL',0) > 2.5 and 
    v['pillar_gtm_scores'].get('PCS',0) < 2.5 and v['pillar_gtm_scores'].get('TDT',0) < 2.5)
print(f'Strong PPD+CTL but weak PCS+TDT: {pattern}/{len(vendors)} ({100*pattern/len(vendors):.1f}%)')

# Max gap in any sub-pillar per vendor
print('\nVendors with ANY sub-pillar gap > 1.0:')
big_sp_gap = 0
for v in vendors:
    max_sp_gap = max((sp_data.get('credibility_gap',0) for sp_data in v.get('sub_pillar_scores',{}).values()), default=0)
    if max_sp_gap > 1.0:
        big_sp_gap += 1
print(f'  {big_sp_gap}/{len(vendors)} ({100*big_sp_gap/len(vendors):.1f}%)')
