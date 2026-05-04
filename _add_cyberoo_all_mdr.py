"""Add Cyberoo to all remaining MDR pipeline files."""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))

# Load Cyberoo data from the already-populated files
con_file = os.path.join(BASE, "MDR Services Vendor 2-1 Consolidated.json")
with open(con_file, "r", encoding="utf-8-sig") as f:
    con = json.load(f)
cyberoo_cap = [v for v in con["vendors"] if v["vendor"] == "Cyberoo"][0]

price_file = os.path.join(BASE, "MDR Services Vendor Pricing 2-0 Researched.json")
with open(price_file, "r", encoding="utf-8-sig") as f:
    pr = json.load(f)
cyberoo_price = [v for v in pr["vendors"] if v["vendor"] == "Cyberoo"][0]

# Files to add Cyberoo to (capability files get cap entry, pricing files get price entry)
targets = [
    ("MDR Services Vendor 1-0 Seed.json", cyberoo_cap),
    ("MDR Services Vendor 2-0 Researched.json", cyberoo_cap),
    ("MDR Services Vendor Capability 1-0 Seed.json", cyberoo_cap),
    ("MDR Services Vendor Pricing 1-0 Seed.json", cyberoo_price),
    ("MDR Services Vendor Pricing 2-1 AI Enriched.json", cyberoo_price),
]

for fname, entry in targets:
    fpath = os.path.join(BASE, fname)
    if not os.path.exists(fpath):
        print(f"[SKIP] {fname}: file not found")
        continue

    with open(fpath, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if isinstance(data, dict) and "vendors" in data:
        vendors = data["vendors"]
    elif isinstance(data, list):
        vendors = data
    else:
        print(f"[SKIP] {fname}: unknown format")
        continue

    # Remove existing Cyberoo if any
    before = len(vendors)
    vendors = [v for v in vendors if v.get("vendor", "").lower() != "cyberoo"]
    vendors.append(entry)

    if isinstance(data, dict) and "vendors" in data:
        data["vendors"] = vendors
    else:
        data = vendors

    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[OK] {fname}: {before} -> {len(vendors)} vendors")

print("\nDone. Cyberoo added to all MDR pipeline files.")
