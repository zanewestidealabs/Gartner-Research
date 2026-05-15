import json, re

# 1. Inventory v12 enrichment script
src = open('_enrich_cnapp_mq_v12.py', encoding='utf-8').read()
blocks = re.split(r'# -+\s+([A-Z][^\n]+)', src)
counts = {}
for i in range(1, len(blocks), 2):
    name = blocks[i].strip()
    body = blocks[i+1] if i+1 < len(blocks) else ''
    n = len(re.findall(r'\{"sp":', body))
    if n:
        counts[name] = n
print('=== _enrich_cnapp_mq_v12.py EVIDENCE entries per vendor ===')
for k, v in sorted(counts.items(), key=lambda x: -x[1]):
    print(f'  {k:30s}  {v} ledger entries')
print(f'Total vendors in v12 EVIDENCE: {len(counts)}')
print()

# 2. Inventory 1-2 vendor file
d = json.load(open('CNAPP MQ Vendor 1-2 Researched.json', encoding='utf-8'))
print('=== CNAPP MQ Vendor 1-2 Researched.json ===')
print(f'Total vendors: {len(d["vendors"])}')
print()
print(f'{"Vendor":30s} {"ledger":>8s} {"rationales":>12s} {"unique_sps":>12s}')
for v in d['vendors']:
    name = v['vendor']
    led = v.get('evidence_ledger') or []
    rat = v.get('mq_gap_rationales') or {}
    rat_count = sum(len(sub) if isinstance(sub, dict) else 0 for sub in rat.values())
    sps = set(e.get('sub_pillar') for e in led if e.get('sub_pillar'))
    print(f'{name:30s} {len(led):>8d} {rat_count:>12d} {len(sps):>12d}')

# 3. List ALL CNAPP-related JSON files in workspace
print()
print('=== All CNAPP-related files ===')
import os
for f in sorted(os.listdir('.')):
    if 'cnapp' in f.lower() and f.endswith('.json'):
        size = os.path.getsize(f)
        print(f'  {f:55s}  {size/1024:>8.1f} KB')
