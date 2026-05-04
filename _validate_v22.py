"""Validate v2.2 output matches frontend expectations."""
import json

data = json.load(open('Offensive Security Vendor 2-2 Researched.json', encoding='utf-8'))
vendors = data['vendors']

print(f"Vendors: {len(vendors)}")
print(f"Version: {data.get('metadata', {}).get('version')}")
print()

# Check first vendor
v = vendors[0]
print(f"=== {v['vendor']} ===")
print(f"Top-level keys: {sorted(v.keys())}")
print(f"Has sub_pillar_rationale_researched: {'sub_pillar_rationale_researched' in v}")

rat = v.get('sub_pillar_rationale_researched', {})
print(f"Rationale entries: {len(rat)}")
print()

# Show first rationale
sp_id = sorted(rat.keys())[0]
print(f"--- {sp_id} rationale ({len(rat[sp_id])} chars) ---")
print(rat[sp_id])
print()

# Show another vendor (less well-known)
v2 = vendors[20]
print(f"=== {v2['vendor']} ===")
rat2 = v2.get('sub_pillar_rationale_researched', {})
sp_id2 = sorted(rat2.keys())[0]
print(f"--- {sp_id2} rationale ({len(rat2[sp_id2])} chars) ---")
print(rat2[sp_id2])
print()

# Check a zero-scored sub-pillar
for v3 in vendors:
    sps = v3.get('sub_pillar_scores_current', {})
    rat3 = v3.get('sub_pillar_rationale_researched', {})
    for sp_id3, score in sps.items():
        if score == 0 and sp_id3 in rat3:
            print(f"=== ZERO SCORE: {v3['vendor']} {sp_id3} ===")
            print(f"Score: {score}")
            print(f"Rationale ({len(rat3[sp_id3])} chars): {rat3[sp_id3][:300]}")
            print()
            break
    else:
        continue
    break

# Stats
total = 0
min_len = 99999
max_len = 0
for v4 in vendors:
    rat4 = v4.get('sub_pillar_rationale_researched', {})
    for sp_id4, text in rat4.items():
        total += 1
        min_len = min(min_len, len(text))
        max_len = max(max_len, len(text))

print(f"Total rationales: {total}")
print(f"Min length: {min_len} chars")
print(f"Max length: {max_len} chars")
print(f"research_flag count: {sum(1 for v5 in vendors if 'research_flag' in v5)}")
