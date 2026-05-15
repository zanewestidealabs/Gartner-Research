"""Analyze PreCyber vendor pillar coverage for market insights report."""
import json
from collections import Counter

VENDOR_FILE = "Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json"
PILLARS = ['EXM', 'AMT', 'ADR', 'PPM', 'SVC']
PILLAR_NAMES = {
    'EXM': 'Exposure Management',
    'AMT': 'Adversary Management & Threat Intel',
    'ADR': 'Adversary Disruption',
    'PPM': 'Posture & Policy Management',
    'SVC': 'Services & Capabilities'
}
THRESHOLD = 2.0

with open(VENDOR_FILE, 'r', encoding='utf-8') as f:
    vendors = json.load(f)

print('=' * 80)
print('PREEMPTIVE CYBERSECURITY VENDOR PILLAR COVERAGE ANALYSIS')
print('=' * 80)

# 1. Pillar coverage per vendor
coverage_counts = {}
vendor_pillars = {}
for v in vendors:
    name = v.get('vendor', '?')
    pillar_scores = v.get('pillar_scores', {})
    active = [p for p in PILLARS if pillar_scores.get(p, 0) >= THRESHOLD]
    coverage_counts[name] = len(active)
    vendor_pillars[name] = active

# Distribution
dist = Counter(coverage_counts.values())
print('\n--- PILLAR COVERAGE DISTRIBUTION ---')
for cnt in sorted(dist.keys()):
    vendors_at = [n for n, c in coverage_counts.items() if c == cnt]
    print(f'\n{cnt} pillars ({dist[cnt]} vendors):')
    for n in sorted(vendors_at):
        vobj = next(v for v in vendors if v['vendor'] == n)
        pillar_scores = vobj.get('pillar_scores', {})
        score_strs = []
        for p in PILLARS:
            s = pillar_scores.get(p, 0)
            score_strs.append(f"{p}={s:.1f}")
        scores_line = ' '.join(score_strs)
        active = vendor_pillars[n]
        print(f'  {n:<28} [{scores_line}] active: {",".join(active) if active else "none"}')

# 2. Pillar penetration rates
print('\n--- PILLAR PENETRATION RATES ---')
for p in PILLARS:
    count = sum(1 for v in vendors if v.get('pillar_scores', {}).get(p, 0) >= THRESHOLD)
    pct = count / len(vendors) * 100
    print(f'  {p} ({PILLAR_NAMES[p]}): {count}/{len(vendors)} = {pct:.0f}%')

# 3. Full-spectrum vendors (4+ pillars)
print('\n--- FULL-SPECTRUM CANDIDATES (4+ pillars >= 2.0) ---')
full = [(n, vendor_pillars[n]) for n in sorted(coverage_counts, key=lambda x: -coverage_counts[x])
        if coverage_counts[n] >= 4]
for n, pillars in full:
    vobj = next(v for v in vendors if v['vendor'] == n)
    pillar_scores = vobj.get('pillar_scores', {})
    dm = vobj.get('delivery_model', '?')
    score_strs = [f"{p}={pillar_scores.get(p, 0):.1f}" for p in PILLARS]
    print(f'  {n:<28} {len(pillars)} pillars [{" ".join(score_strs)}] model={dm}')

# 4. Delivery model breakdown
print('\n--- DELIVERY MODEL DISTRIBUTION ---')
dm_counter = Counter(v.get('delivery_model', 'unknown') for v in vendors)
for dm, c in dm_counter.most_common():
    print(f'  {dm}: {c} vendors')

# 5. Average pillar scores by delivery model
print('\n--- AVERAGE PILLAR SCORES BY DELIVERY MODEL ---')
for dm in ['direct_service', 'platform_plus_partner', 'platform_only']:
    group = [v for v in vendors if v.get('delivery_model') == dm]
    if not group:
        continue
    print(f'\n  {dm} ({len(group)} vendors):')
    for p in PILLARS:
        scores = [v.get('pillar_scores', {}).get(p, 0) for v in group]
        avg = sum(scores) / len(scores)
        print(f'    {p}: {avg:.2f}')

# 6. Cross-pillar gap analysis
print('\n--- CROSS-PILLAR GAPS (pillars with < 2.0 by vendor model) ---')
for dm in ['direct_service', 'platform_plus_partner', 'platform_only']:
    group = [v for v in vendors if v.get('delivery_model') == dm]
    if not group:
        continue
    print(f'\n  {dm} ({len(group)} vendors):')
    for p in PILLARS:
        below = [v['vendor'] for v in group if v.get('pillar_scores', {}).get(p, 0) < THRESHOLD]
        if below:
            pct = len(below) / len(group) * 100
            print(f'    {p} gap: {len(below)}/{len(group)} ({pct:.0f}%) vendors below {THRESHOLD}')

# 7. Top-10 most balanced vendors (highest minimum pillar score)
print('\n--- TOP-10 MOST BALANCED VENDORS (by minimum pillar score) ---')
balance_data = []
for v in vendors:
    name = v.get('vendor', '?')
    pillar_scores = v.get('pillar_scores', {})
    vals = [pillar_scores.get(p, 0) for p in PILLARS]
    min_s = min(vals) if vals else 0
    avg_s = sum(vals) / len(vals) if vals else 0
    balance_data.append((name, min_s, avg_s, vals))
balance_data.sort(key=lambda x: (-x[1], -x[2]))
for name, min_s, avg_s, vals in balance_data[:10]:
    vobj = next(v for v in vendors if v['vendor'] == name)
    dm = vobj.get('delivery_model', '?')
    score_strs = [f"{PILLARS[i]}={vals[i]:.1f}" for i in range(len(PILLARS))]
    print(f'  {name:<28} min={min_s:.1f} avg={avg_s:.2f} [{" ".join(score_strs)}] {dm}')

# 8. Composite market stats
print('\n--- COMPOSITE MARKET STATISTICS ---')
total = len(vendors)
one_or_fewer = sum(1 for c in coverage_counts.values() if c <= 1)
two_or_fewer = sum(1 for c in coverage_counts.values() if c <= 2)
three_or_fewer = sum(1 for c in coverage_counts.values() if c <= 3)
four_plus = sum(1 for c in coverage_counts.values() if c >= 4)
five = sum(1 for c in coverage_counts.values() if c >= 5)
print(f'  Total vendors: {total}')
print(f'  0-1 pillar coverage: {one_or_fewer} ({one_or_fewer/total*100:.0f}%)')
print(f'  1-2 pillar coverage: {two_or_fewer} ({two_or_fewer/total*100:.0f}%)')
print(f'  1-3 pillar coverage: {three_or_fewer} ({three_or_fewer/total*100:.0f}%)')
print(f'  4+ pillar coverage:  {four_plus} ({four_plus/total*100:.0f}%)')
print(f'  5 pillar coverage:   {five} ({five/total*100:.0f}%)')
avg_coverage = sum(coverage_counts.values()) / total
print(f'  Average pillar coverage: {avg_coverage:.1f}')
