"""Check high-scored rationales to verify excerpts are present."""
import json

data = json.load(open('Offensive Security Vendor 2-2 Researched.json', encoding='utf-8'))

# Find a vendor with high ASM-01 score (Tenable should be 4+)
for v in data['vendors'][:5]:
    rat = v.get('sub_pillar_rationale_researched', {})
    sps = v.get('sub_pillar_scores_current', {})
    for sp_id in ['ASM-01', 'VUL-01', 'OFT-01']:
        score = sps.get(sp_id, 0)
        if score >= 3:
            print(f"=== {v['vendor']} {sp_id} (score={score}) ===")
            print(rat.get(sp_id, 'NONE'))
            print()
            break
