"""Quick verification of re-scored data."""
import json

with open("Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json", "r", encoding="utf-8-sig") as f:
    vendors = json.load(f)

print(f"{len(vendors)} vendors\n")

codes05 = ["EXM-05", "AMT-05", "ADR-05", "PPM-05"]
codesS = ["SVC-01", "SVC-02", "SVC-03", "SVC-04"]

print("=== Score Distributions ===")
for c in codes05 + codesS:
    vals = [v.get("sub_pillar_scores_current", {}).get(c, 0) for v in vendors]
    avg = sum(vals) / len(vals)
    nz = len([x for x in vals if x > 0])
    print(f"  {c}: avg={avg:.2f}  min={min(vals):.1f}  max={max(vals):.1f}  >0={nz}/51")

print("\n=== Top Scorers Per -05 ===")
for c in codes05:
    top = sorted(vendors, key=lambda v: v.get("sub_pillar_scores_current", {}).get(c, 0), reverse=True)[:5]
    for v in top:
        sc = v.get("sub_pillar_scores_current", {}).get(c, 0)
        print(f"  {c}: {v['vendor']} = {sc:.1f}")
    print()

print("=== Coverage Grades ===")
grades = {}
for v in vendors:
    g = v.get("coverage_grade", "?")
    grades[g] = grades.get(g, 0) + 1
print(f"  {dict(sorted(grades.items()))}")

print("\n=== Pillar Score Impact (sample) ===")
for name in ["Tenable", "CrowdStrike", "Palo Alto Networks", "Rapid7", "ZeroFox"]:
    v = next(x for x in vendors if x["vendor"] == name)
    ps = v.get("pillar_scores", {})
    print(f"  {name}: EXM={ps.get('EXM',0):.2f} AMT={ps.get('AMT',0):.2f} ADR={ps.get('ADR',0):.2f} PPM={ps.get('PPM',0):.2f} SVC={ps.get('SVC',0):.2f}")
