"""Inspect TRiSM vendor data structure for rationale script design."""
import json

d = json.load(open("AI TRiSM Vendor 1-1 Validated.json", encoding="utf-8"))
v = d["vendors"][0]
print("Vendor:", v["vendor"])
print()

# Show all top-level keys
print("All keys:", sorted(v.keys()))
print()

# Show evidence structure for one sub-pillar
ev = v.get("sub_pillar_evidence", {})
sid = "GOV-01"
e = ev.get(sid, {})
print(f"Evidence for {sid}:")
for k2, v2 in e.items():
    if k2 != "excerpts":
        print(f"  {k2}: {v2}")
excs = e.get("excerpts", [])
print(f"  excerpts ({len(excs)}):")
for i, ex in enumerate(excs[:3]):
    print(f"    [{i}] terms={ex.get('matched_terms')}, rel={ex.get('relevance_score')}")
    print(f"        {ex.get('excerpt', '')[:140]}...")

# Check rationale keys
print()
for k in sorted(v.keys()):
    if "rationale" in k.lower():
        val = v[k]
        if isinstance(val, dict):
            print(f"  {k}: {list(val.keys())[:4]}...")
        else:
            print(f"  {k}: {type(val).__name__}")

# Show scores
print()
print("sub_pillar_scores_validated:", v.get("sub_pillar_scores_validated"))
print("sub_pillar_scores_evidence_refined:", v.get("sub_pillar_scores_evidence_refined"))

# Evidence quality analysis
eq = v.get("evidence_quality_analysis", {})
print()
print("evidence_quality_analysis keys:", list(eq.keys())[:4] if eq else "MISSING")
if eq:
    eq1 = eq.get(sid, {})
    print(f"  {sid}: quality={eq1.get('quality_factor')}, notes={eq1.get('notes')}")
    comps = eq1.get("components", {})
    print(f"  components: {comps}")
    print(f"  raw_counts: {eq1.get('raw_counts')}")

# Schema info
print()
print("Schema file:", d.get("schema_file"))
print("Vendor count:", len(d.get("vendors", [])))

# Check a second vendor for comparison
v2 = d["vendors"][30]
print()
print("Vendor #30:", v2["vendor"])
ev2 = v2.get("sub_pillar_evidence", {}).get(sid, {})
print(f"  {sid} excerpts: {len(ev2.get('excerpts', []))}")
print(f"  specificity: {ev2.get('sub_pillar_specificity')}")
print(f"  schema_criteria_hits: {ev2.get('schema_criteria_hits')}")
