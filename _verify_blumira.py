import json, os
base = "/home/vm-ssh/gartner"
files = [
    ("MDR", "MDR Services Vendor 2-1 Consolidated.json"),
    ("Pricing", "MDR Services Vendor Pricing 2-1 AI Enriched.json"),
    ("PreCyber", "Preemptive Cybersecurity Vendor 2-1 Consolidated.json"),
    ("DFIR", "Vendor 3-7.json"),
    ("PMR", "Product Market Readiness Vendor 1-1 Enriched.json"),
]
for label, fn in files:
    d = json.load(open(os.path.join(base, fn)))
    cnt = d.get("vendor_count", len(d["vendors"]))
    has = any(v["vendor"] == "Blumira" for v in d["vendors"])
    print(f"{label}: {cnt} vendors, Blumira={has}")
