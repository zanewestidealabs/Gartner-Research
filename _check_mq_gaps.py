import json

files = [
    "MDR Services Vendor MQ Gap 1-0 Seed.json",
    "MDR Services Vendor MQ Gap 2-0 Researched.json",
    "MQ_Gap Vendor 2-1 Consolidated.json",
]

cap_file = "MDR Services Vendor 2-1 Consolidated.json"
with open(cap_file, encoding="utf-8") as f:
    cap_data = json.load(f)
cap_names = sorted(v["vendor"].lower() for v in cap_data["vendors"])
print(f"Capability: {len(cap_names)} vendors\n")

for fname in files:
    try:
        with open(fname, encoding="utf-8-sig") as f:
            data = json.load(f)
        vendors = data.get("vendors", data if isinstance(data, list) else [])
        vnames = sorted(v["vendor"].lower() for v in vendors)
        print(f"{fname}: {len(vendors)} vendors")
        cbs = [v["vendor"] for v in vendors if "cbs" in v.get("vendor", "").lower()]
        print(f"  CBS: {cbs if cbs else 'NOT FOUND'}")
        missing = [n for n in cap_names if n not in vnames]
        print(f"  Missing from cap ({len(missing)}): {missing}")
    except Exception as e:
        print(f"{fname}: ERROR - {e}")
    print()
