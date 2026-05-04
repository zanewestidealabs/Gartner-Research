import json, collections, re

d = json.load(open(r"CNAPP Vendor 1-2 Researched.json", encoding="utf-8"))

# Per-vendor inspection
for vname in ["Upwind", "Datadog", "Caveonix", "Uptycs", "Sweet Security"]:
    v = [x for x in d["vendors"] if x["vendor"] == vname][0]
    cnt = collections.Counter(r["confidence"] for r in v["rationales_v1"].values())
    print(f"\n{vname}: {dict(cnt)}")
    # show the highest-evidence sub-pillar and a none one
    items = sorted(v["rationales_v1"].items(), key=lambda kv: -kv[1]["evidence_count"])
    top = items[0]
    print(f"  TOP {top[0]}: ev={top[1]['evidence_count']} conf={top[1]['confidence']}")
    print(f"    {top[1]['rationale'][:220]}")
    # an SP with no evidence
    nones = [k for k, r in v["rationales_v1"].items() if r["confidence"] == "none"]
    if nones:
        k = nones[0]
        print(f"  NONE {k}: {v['rationales_v1'][k]['rationale'][:220]}")
