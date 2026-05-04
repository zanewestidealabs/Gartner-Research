import json
d = json.load(open('CNAPP MQ Vendor 1-2 Researched.json', encoding='utf-8'))
enriched = [v for v in d['vendors'] if 'sub_pillar_scores_v12' in v]
print(f"total={len(d['vendors'])}  enriched={len(enriched)}")
missing = [v['vendor'] for v in d['vendors'] if 'sub_pillar_scores_v12' not in v]
print('missing:', missing)
ledger = json.load(open('CNAPP MQ Evidence Ledger.json', encoding='utf-8'))
rows = ledger['rows'] if isinstance(ledger, dict) and 'rows' in ledger else ledger
print(f"ledger rows={len(rows)}")
print()
print('--- v1.1 vs v1.2 averages (sorted by v1.2 desc) ---')
def avg(d):
    return sum(d.values()) / len(d)
ranked = sorted(enriched, key=lambda v: -avg(v['sub_pillar_scores_v12']))
for v in ranked:
    a12 = avg(v['sub_pillar_scores_v12'])
    a11 = avg(v['sub_pillar_scores_current'])
    print(f"{v['vendor']:<25} {a11:.2f} -> {a12:.2f}  ({a12-a11:+.2f})")
