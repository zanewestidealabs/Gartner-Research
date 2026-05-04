"""Check SVC sub-pillar scores in the v3-0 data."""
import json

with open("Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)

vendors = data if isinstance(data, list) else data.get("vendors", [])
print(f"{len(vendors)} vendors loaded\n")

svc_codes = ["EXM-05", "AMT-05", "ADR-05", "PPM-05", "SVC-01", "SVC-02", "SVC-03", "SVC-04"]
prc_codes = ["PRC-SUB", "PRC-USG", "PRC-FIX", "PRC-SUC", "PRC-COM", "PRC-OUT"]

print("=== SVC Sub-Pillar Scores (first 10 vendors) ===")
for v in vendors[:10]:
    scores = v.get("sub_pillar_scores_current", {})
    name = v["vendor"]
    svc = {k: scores.get(k, "MISSING") for k in svc_codes}
    print(f"  {name}: {svc}")

print("\n=== Pricing Scores (first 10 vendors) ===")
for v in vendors[:10]:
    prc = v.get("pricing_dimension_scores", {})
    name = v["vendor"]
    print(f"  {name}: {prc}")

print("\n=== SVC Score Distribution ===")
for code in svc_codes:
    vals = [v.get("sub_pillar_scores_current", {}).get(code, 0) for v in vendors]
    nonzero = [x for x in vals if x > 0]
    avg = sum(vals)/len(vals) if vals else 0
    print(f"  {code}: avg={avg:.2f}, min={min(vals):.1f}, max={max(vals):.1f}, >0: {len(nonzero)}/{len(vals)}")

print("\n=== Pricing Score Distribution ===") 
for code in prc_codes:
    vals = [v.get("pricing_dimension_scores", {}).get(code, 0) for v in vendors]
    nonzero = [x for x in vals if x > 0]
    avg = sum(vals)/len(vals) if vals else 0
    print(f"  {code}: avg={avg:.2f}, min={min(vals):.1f}, max={max(vals):.1f}, >0: {len(nonzero)}/{len(vals)}")

print("\n=== Sub-pillar evidence check (first 3 vendors) ===")
for v in vendors[:3]:
    name = v["vendor"]
    evidence = v.get("sub_pillar_evidence", {})
    for code in svc_codes:
        ev = evidence.get(code, {})
        excerpts = ev.get("excerpts", [])
        st_hits = ev.get("search_term_hits", 0)
        ct_hits = ev.get("criteria_text_hits", 0)
        score = v.get("sub_pillar_scores_current", {}).get(code, "MISSING")
        print(f"  {name} | {code}: score={score}, excerpts={len(excerpts)}, st_hits={st_hits}, ct_hits={ct_hits}")

# Check ALL sub-pillar codes present
print("\n=== All sub-pillar codes in first vendor ===")
v0 = vendors[0]
all_codes = sorted(v0.get("sub_pillar_scores_current", {}).keys())
print(f"  {len(all_codes)} codes: {all_codes}")

# Check what keys each vendor has
print("\n=== Top-level keys in first vendor ===")
print(f"  {sorted(v0.keys())}")
