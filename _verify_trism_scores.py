"""Quick verification of TRiSM evidence_refined scores."""
import json

d = json.load(open("AI TRiSM Vendor 1-1 Validated.json", encoding="utf-8"))
v = d["vendors"][0]
print(f"Vendor: {v['vendor']}")

keys = [k for k in v if "pillar" in k.lower() or "score" in k.lower()]
print(f"Score keys: {keys}")

er = v.get("sub_pillar_scores_evidence_refined", {})
print(f"Evidence refined sub-pillars: {list(er.keys())[:4]}")
print(f"Evidence refined pillar: {v.get('pillar_scores_evidence_refined', {})}")

val = v.get("sub_pillar_scores_validated", {})
print(f"\nValidated vs Evidence-Refined comparison:")
for sid in ["GOV-01", "GOV-02", "RUN-01", "INF-01"]:
    print(f"  {sid}: validated={val.get(sid)} → refined={er.get(sid)}")
