"""Quick check of v2.1 rationale content."""
import json

data = json.load(open('Offensive Security Vendor 2-1 Consolidated.json', encoding='utf-8'))

# Check first 3 vendors, 3 sub-pillars each
for v in data['vendors'][:3]:
    print(f"=== {v['vendor']} ===")
    spe = v.get('sub_pillar_evidence', {})
    count = 0
    for sp_id, ev in spe.items():
        if count >= 3:
            break
        r = ev.get('rationale', '')
        print(f"  {sp_id}: keys={list(ev.keys())}")
        print(f"    rationale ({len(r)} chars): {r[:300]}")
        print(f"    excerpts: {len(ev.get('excerpts', []))}")
        print(f"    sources: {len(ev.get('sources', []))}")
        print(f"    hit_count: {ev.get('hit_count', 'NONE')}")
        print()
        count += 1
    print()

# Also check a vendor with score 0
for v in data['vendors']:
    spe = v.get('sub_pillar_evidence', {})
    for sp_id, ev in spe.items():
        score = v.get('sub_pillar_scores_current', {}).get(sp_id, -1)
        if score == 0:
            print(f"=== ZERO SCORE: {v['vendor']} {sp_id} ===")
            print(f"  rationale: {ev.get('rationale', 'NONE')[:200]}")
            print(f"  score: {score}")
            print()
            break
    else:
        continue
    break

# Count rationale stats
total = 0
has_rationale = 0
empty_rationale = 0
for v in data['vendors']:
    spe = v.get('sub_pillar_evidence', {})
    for sp_id, ev in spe.items():
        total += 1
        r = ev.get('rationale', '')
        if r:
            has_rationale += 1
        else:
            empty_rationale += 1

print(f"Total evidence entries: {total}")
print(f"With rationale: {has_rationale}")
print(f"Without rationale: {empty_rationale}")

# Check scores without evidence
scores_total = 0
scores_with_evidence = 0
scores_without_evidence = 0
for v in data['vendors']:
    sps = v.get('sub_pillar_scores_current', {})
    spe = v.get('sub_pillar_evidence', {})
    for sp_id, score in sps.items():
        if score > 0:
            scores_total += 1
            if sp_id in spe and spe[sp_id].get('rationale', ''):
                scores_with_evidence += 1
            else:
                scores_without_evidence += 1

print(f"\nScored > 0: {scores_total}")
print(f"  with rationale: {scores_with_evidence}")
print(f"  WITHOUT rationale: {scores_without_evidence}")
