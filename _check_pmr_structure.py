import json
with open("Product Market Readiness Vendor 1-1 Enriched.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)
vendors = data.get("vendors", data) if isinstance(data, dict) else data
v = vendors[0] if isinstance(vendors, list) else list(vendors.values())[0]
print("Vendor:", v.get("vendor_name", "unknown"))
print("Top-level keys:", list(v.keys()))
sps = v.get("sub_pillar_scores", {})
first_key = list(sps.keys())[0] if sps else "NONE"
print(f"First sub_pillar_scores key: {first_key}")
print(f"Fields in sub_pillar_scores['{first_key}']:")
sp = sps[first_key]
for k, val in sp.items():
    if isinstance(val, str):
        print(f"  {k}: (string) {val[:80]}..." if len(val) > 80 else f"  {k}: (string) {val}")
    elif isinstance(val, list):
        print(f"  {k}: (list, len={len(val)})")
        if val and isinstance(val[0], dict):
            print(f"    [0] keys: {list(val[0].keys())}")
    elif isinstance(val, dict):
        print(f"  {k}: (dict) {list(val.keys())}")
    else:
        print(f"  {k}: {val}")
print()
print("Has sub_pillar_rationale_researched:", "sub_pillar_rationale_researched" in v)
print("Has sub_pillar_evidence:", "sub_pillar_evidence" in v)
print("Has sub_pillar_rationale_v2:", "sub_pillar_rationale_v2" in v)
