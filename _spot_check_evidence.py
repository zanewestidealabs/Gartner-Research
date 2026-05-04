import json
cap = json.load(open('MDR Services Vendor Capability 1-0 Seed.json','r',encoding='utf-8'))
prc = json.load(open('MDR Services Vendor Pricing 1-0 Seed.json','r',encoding='utf-8'))

for vname in ['CrowdStrike', 'Performanta', 'Radiant Security', 'Lumu Technologies']:
    v = next((v for v in cap['vendors'] if v['vendor'] == vname), None)
    if v:
        ev = v['sub_pillar_evidence']
        print("=== " + vname + " (Cap) ===")
        for sp in ['TDR-01', 'ADA-01', 'AIO-01', 'SOG-01']:
            e = ev.get(sp, {})
            urls = e.get('source_urls', [])
            notes = e.get('notes', '')[:140]
            print("  " + sp + ": URLs=" + str(len(urls)) + ", Notes=" + notes)
        print()

for vname in ['CrowdStrike', 'Performanta']:
    v = next((v for v in prc['vendors'] if v['vendor'] == vname), None)
    if v:
        pe = v['pricing_evidence']
        oe = v['outcome_evidence']
        print("=== " + vname + " (Pricing) ===")
        for dim in ['PRC-SUB', 'PRC-OUT']:
            e = pe.get(dim, {})
            urls = e.get('source_urls', [])
            notes = e.get('notes', '')[:140]
            print("  " + dim + ": URLs=" + str(len(urls)) + ", Notes=" + notes)
        oe_urls = oe.get('source_urls', [])
        oe_notes = oe.get('notes', '')[:140]
        print("  Outcome: URLs=" + str(len(oe_urls)) + ", Notes=" + oe_notes)
        print()
