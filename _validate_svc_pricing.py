import json

d = json.load(open("Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json", "r", encoding="utf-8"))
print(f"Total vendors: {len(d)}")

v = d[0]
print(f"First vendor: {v['vendor']}")
print(f"Sub-pillar codes: {sorted(v.get('sub_pillar_scores_current', {}).keys())}")
print(f"Sub-pillar count: {len(v.get('sub_pillar_scores_current', {}))}")
print(f"Pricing dims: {sorted(v.get('pricing_dimension_scores', {}).keys())}")
print(f"Outcome maturity: {v.get('outcome_maturity_rating')} ({v.get('outcome_maturity_label')})")
print(f"Services maturity: {v.get('services_maturity_level')}")
print(f"Coverage grade: {v.get('coverage_grade')}")
print(f"Coverage count: {v.get('capability_coverage_count')}")
print(f"Pillar scores: {v.get('pillar_scores')}")
print(f"Research meta: {v.get('svc_pricing_research', {})}")

# Check all vendors
all_ok = all("pricing_dimension_scores" in vv for vv in d)
print(f"\nAll vendors have pricing data: {all_ok}")
all_svc = all("SVC-01" in vv.get("sub_pillar_scores_current", {}) for vv in d)
print(f"All vendors have SVC scores: {all_svc}")
all_05 = all("EXM-05" in vv.get("sub_pillar_scores_current", {}) for vv in d)
print(f"All vendors have EXM-05: {all_05}")

# Show top scorers for SVC-03 (managed ops)
print("\nTop SVC-03 (Managed Ops) scores:")
for vv in sorted(d, key=lambda x: x.get("sub_pillar_scores_current", {}).get("SVC-03", 0), reverse=True)[:10]:
    s = vv.get("sub_pillar_scores_current", {}).get("SVC-03", 0)
    print(f"  {vv['vendor']:30s}  SVC-03: {s:.2f}")

# Show distribution of outcome maturity
print("\nOutcome maturity distribution:")
labels = {}
for vv in d:
    lbl = vv.get("outcome_maturity_label", "Unknown")
    labels[lbl] = labels.get(lbl, 0) + 1
for lbl, cnt in sorted(labels.items(), key=lambda x: -x[1]):
    print(f"  {lbl}: {cnt}")
