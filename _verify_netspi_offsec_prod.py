import json
files = [
    "Offensive Security Vendor 1-0 Seed.json",
    "Offensive Security Vendor 2-0 Researched.json",
    "Offensive Security Vendor 2-1 Consolidated.json",
    "Offensive Security Vendor 2-2 Researched.json",
]
for fname in files:
    d = json.load(open(f"/home/vm-ssh/gartner/{fname}"))
    vs = [v["vendor"] for v in d["vendors"]]
    found = "NetSPI" in vs
    print(f"{fname}: {len(vs)} vendors, NetSPI={found}")
    if found:
        ns = [v for v in d["vendors"] if v["vendor"] == "NetSPI"][0]
        print(f"  type={ns['vendor_type']}, primary={ns['primary_capability']}")
        print(f"  pillar_scores={ns['pillar_scores']}")
        if "sub_pillar_evidence" in ns:
            print(f"  evidence_keys={len(ns['sub_pillar_evidence'])}")
