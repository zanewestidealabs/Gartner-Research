"""Quick check of rationale quality in v2.1."""
import json

with open("Offensive Security Vendor 2-1 Consolidated.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Show 3 adequate rationales
print("=== ADEQUATE RATIONALES ===")
count = 0
for v in data["vendors"]:
    ev = v.get("sub_pillar_evidence", {})
    scores = v.get("sub_pillar_scores_current", {})
    for sp_id, e in ev.items():
        rat = e.get("rationale", "")
        sc = scores.get(sp_id, 0)
        if rat and len(rat) >= 100 and "provides this capability" not in rat and sc >= 3:
            print(f"\n--- {v['vendor']} / {sp_id} (score {sc}) ---")
            print(rat)
            count += 1
            if count >= 3:
                break
    if count >= 3:
        break

# Show 3 thin rationales
print("\n\n=== THIN RATIONALES ===")
count = 0
for v in data["vendors"]:
    ev = v.get("sub_pillar_evidence", {})
    scores = v.get("sub_pillar_scores_current", {})
    for sp_id, e in ev.items():
        rat = e.get("rationale", "")
        sc = scores.get(sp_id, 0)
        if rat and "provides this capability" in rat and sc >= 3:
            print(f"\n--- {v['vendor']} / {sp_id} (score {sc}) ---")
            print(rat)
            excerpts = e.get("excerpts", [])
            if excerpts:
                print(f"  [Has {len(excerpts)} excerpts, top relevance: {excerpts[0]['relevance_score']}]")
                print(f"  Top excerpt: {excerpts[0]['excerpt'][:200]}")
            count += 1
            if count >= 3:
                break
    if count >= 3:
        break
