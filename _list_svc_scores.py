"""List all 51 vendors' SVC scores + description for classification."""
import json

with open("Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json", "r", encoding="utf-8") as f:
    vendors = json.load(f)

rows = []
for v in vendors:
    ps = v.get("pillar_scores", {})
    sps = v.get("sub_pillar_scores_current", {})
    name = v.get("vendor", "?")
    svc = ps.get("SVC", 0)
    s1 = sps.get("SVC-01", 0)
    s2 = sps.get("SVC-02", 0)
    s3 = sps.get("SVC-03", 0)
    s4 = sps.get("SVC-04", 0)
    sml = v.get("services_maturity_level", "-")
    desc = v.get("description", "")[:100]
    rows.append((svc, name, s1, s2, s3, s4, sml, desc))

rows.sort(key=lambda x: -x[0])
hdr = f"{'Vendor':<28} {'SVC':>4} {'01':>4} {'02':>4} {'03':>4} {'04':>4}  {'SML':<15}"
print(hdr)
print("-" * len(hdr))
for svc, name, s1, s2, s3, s4, sml, desc in rows:
    print(f"{name:<28} {svc:>4} {s1:>4} {s2:>4} {s3:>4} {s4:>4}  {sml:<15}")
    print(f"  {desc}")
