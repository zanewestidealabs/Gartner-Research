import json
from collections import Counter, defaultdict

# Load validated data
d = json.load(open('Preemptive Cybersecurity Vendor 2-2 Validated.json', encoding='utf-8'))
targets = json.load(open('precyber_research_targets.json', encoding='utf-8'))

print('=== research targets summary ===')
print(f'total targets: {len(targets) if isinstance(targets, list) else "N/A"}')
if isinstance(targets, dict):
    print('keys:', list(targets.keys())[:10])
    targets = targets.get('targets', targets)

# Inspect structure
print('sample target:', json.dumps(targets[0] if isinstance(targets, list) else next(iter(targets.values())), indent=2)[:600])
print()

# Across all vendors, count zero-score cells per sub-pillar
print('=== zero-score cells per sub-pillar ===')
zero_by_sid = Counter()
zero_in_expected = Counter()
total_by_sid = Counter()
for v in d['vendors']:
    expected = set(v.get('expected_coverage') or [])
    for sid, sc in v['sub_pillar_scores_validated_v22'].items():
        total_by_sid[sid] += 1
        if sc == 0.0:
            zero_by_sid[sid] += 1
            if sid in expected or sid.split('-')[0] in expected:
                zero_in_expected[sid] += 1

print(f'{"SID":10} {"zero":>6} {"in_exp":>8} {"total":>6}')
for sid in sorted(total_by_sid):
    print(f'{sid:10} {zero_by_sid[sid]:6} {zero_in_expected[sid]:8} {total_by_sid[sid]:6}')

print()
print('=== vendors with the most zero-score cells (where they claim coverage) ===')
zero_vendors = []
for v in d['vendors']:
    expected = set(v.get('expected_coverage') or [])
    zeros_in_exp = []
    zeros_other = []
    for sid, sc in v['sub_pillar_scores_validated_v22'].items():
        if sc != 0.0: continue
        if sid in expected or sid.split('-')[0] in expected:
            zeros_in_exp.append(sid)
        else:
            zeros_other.append(sid)
    zero_vendors.append((v['vendor'], len(zeros_in_exp), len(zeros_other), zeros_in_exp))

zero_vendors.sort(key=lambda r: -r[1])
print(f'{"vendor":40} {"in_exp_zeros":>14} {"other_zeros":>12}  cells_in_exp')
for name, ze, zo, cells in zero_vendors[:20]:
    print(f'{name:40} {ze:14} {zo:12}  {cells[:8]}')
