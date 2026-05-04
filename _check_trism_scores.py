import json

with open('AI TRiSM Vendor 1-1 Validated.json', encoding='utf-8') as fh:
    data = json.load(fh)

vendors = data['vendors']
print(f"Total vendors: {len(vendors)}")

diff_sp = 0
same_sp = 0
diff_pillar = 0
examples = []

for v in vendors:
    cur = v.get('sub_pillar_scores_current', {})
    val = v.get('sub_pillar_scores_validated', {})
    ps = v.get('pillar_scores', {})
    ps_val = v.get('pillar_scores_validated', {})
    
    for k in set(list(cur.keys()) + list(val.keys())):
        if cur.get(k) != val.get(k):
            diff_sp += 1
            if len(examples) < 8:
                examples.append(f"  {v['vendor']} | {k}: current={cur.get(k)}, validated={val.get(k)}")
        else:
            same_sp += 1
    
    for k in set(list(ps.keys()) + list(ps_val.keys())):
        if ps.get(k) != ps_val.get(k):
            diff_pillar += 1

print(f"\nSub-pillar diffs: {diff_sp} different, {same_sp} same")
print(f"Pillar-level diffs: {diff_pillar}")

if examples:
    print("\nExamples of differences:")
    for e in examples:
        print(e)
else:
    print("\nNO DIFFERENCES FOUND - current and validated are identical!")

# Check evidence data
ev_count = sum(1 for v in vendors if v.get('sub_pillar_evidence') and len(v.get('sub_pillar_evidence', {})) > 0)
print(f"\nVendors with sub_pillar_evidence: {ev_count}/{len(vendors)}")

# Show what a vendor's evidence looks like
for v in vendors[:1]:
    ev = v.get('sub_pillar_evidence', {})
    if ev:
        for sp_id, sp_ev in list(ev.items())[:1]:
            print(f"\nEvidence sample for {v['vendor']} - {sp_id}:")
            print(f"  source_urls: {len(sp_ev.get('source_urls', []))} urls")
            print(f"  excerpts: {len(sp_ev.get('excerpts', []))} excerpts")
            print(f"  hit_count: {sp_ev.get('hit_count')}")
            print(f"  specific_hit_count: {sp_ev.get('specific_hit_count')}")
            print(f"  ai_signal_score: {sp_ev.get('ai_signal_score')}")
