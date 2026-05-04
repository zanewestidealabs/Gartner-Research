"""Validate MDR 2.0 Researched output."""
import json

with open("MDR Services Vendor 2-0 Researched.json", "r", encoding="utf-8-sig") as f:
    d = json.load(f)

print("Top-level keys:", list(d.keys()))
print("Vendor count:", d["vendor_count"])
print("v2_research_metadata:", json.dumps(d["v2_research_metadata"], indent=2))

vendors = d["vendors"]
v_ok = 0
for v in vendors:
    rat = v.get("sub_pillar_rationale_v2", {})
    con = v.get("sub_pillar_rationale_v2_consolidated", {})
    v2s = v.get("sub_pillar_scores_v2_researched", {})
    if len(rat) == 32 and len(con) == 32 and len(v2s) == 32:
        v_ok += 1
print(f"\nVendors with complete 32-sp rationale: {v_ok}/{len(vendors)}")

# Confidence distribution
conf = {}
for v in vendors:
    c = v.get("research_confidence", "unknown")
    conf[c] = conf.get(c, 0) + 1
print("Confidence distribution:", conf)

# Evidence quality grade distribution
grades = {}
for v in vendors:
    for sp_id, rat in v.get("sub_pillar_rationale_v2", {}).items():
        eqf = rat.get("evidence_quality_factor", 0)
        if eqf >= 0.80: g = "A"
        elif eqf >= 0.60: g = "B"
        elif eqf >= 0.40: g = "C"
        elif eqf >= 0.20: g = "D"
        else: g = "F"
        grades[g] = grades.get(g, 0) + 1
print("Evidence quality grades:", dict(sorted(grades.items())))

# Criteria status distribution
statuses = {}
for v in vendors:
    for sp_id, rat in v.get("sub_pillar_rationale_v2", {}).items():
        for c in rat.get("criteria_assessment", []):
            s = c.get("status", "unknown")
            statuses[s] = statuses.get(s, 0) + 1
print("Criteria assessment:", dict(sorted(statuses.items())))

# Spot check a mid-tier vendor
for v in vendors:
    if v["vendor"] == "Arctic Wolf":
        print(f"\n=== Arctic Wolf spot check ===")
        print(f"  research_confidence: {v['research_confidence']}")
        print(f"  notable_differentiation: {v['notable_differentiation']}")
        print(f"  evidence_quality_summary: {v['evidence_quality_summary']}")
        # Show AIO-02 rationale
        r = v["sub_pillar_rationale_v2"].get("AIO-02", {})
        print(f"  AIO-02: score={r.get('original_score')}, level={r.get('scoring_level')}, conf={r.get('confidence')}, eqf={r.get('evidence_quality_factor')}")
        print(f"  Rationale: {r.get('score_rationale', '')[:250]}")
        for c in r.get("criteria_assessment", []):
            print(f"    [{c['status'].upper()}] {c['criterion'][:65]}")
        # Show consolidated
        con = v["sub_pillar_rationale_v2_consolidated"].get("AIO-02", "")
        print(f"  Consolidated (first 400 chars): {con[:400]}")
        break

# Show file size
import os
fsize = os.path.getsize("MDR Services Vendor 2-0 Researched.json")
print(f"\nFile size: {fsize / 1024 / 1024:.1f} MB")
