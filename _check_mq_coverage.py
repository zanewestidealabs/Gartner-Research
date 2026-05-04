import json

mdr = json.load(open("MDR Services Vendor 2-1 Consolidated.json", encoding="utf-8"))
mdr_names = {v["vendor"].lower() for v in mdr["vendors"]}

pmr_files = ["PMR Vendor 1-0 Seed.json", "PMR Vendor 2-0 Researched.json"]
for f in pmr_files:
    try:
        d = json.load(open(f, encoding="utf-8"))
        vlist = d.get("vendors", d) if isinstance(d, dict) else d
        pmr_names = {v["vendor"].lower() for v in vlist}
        overlap = mdr_names & pmr_names
        print(f"{f}: {len(vlist)} vendors, {len(overlap)} overlap with MDR")
        if overlap:
            print(f"  Overlapping: {sorted(list(overlap))[:20]}")
    except Exception as e:
        print(f"{f}: {e}")

total = len(mdr["vendors"])
fields = ["employee_count_range", "funding_stage", "year_founded", "region",
           "target_market", "delivery_model", "mdr_service_type", "is_startup", "is_ai_first"]
print(f"\nMDR vendor field coverage ({total} total):")
for fld in fields:
    count = sum(1 for v in mdr["vendors"] if v.get(fld))
    print(f"  {fld}: {count}/{total}")

# Check funding_stage distribution
from collections import Counter
stages = Counter(v.get("funding_stage", "N/A") for v in mdr["vendors"])
print(f"\nFunding stage distribution:")
for stage, cnt in stages.most_common():
    print(f"  {stage}: {cnt}")

# Check employee_count_range distribution
sizes = Counter(v.get("employee_count_range", "N/A") for v in mdr["vendors"])
print(f"\nEmployee size distribution:")
for size, cnt in sizes.most_common():
    print(f"  {size}: {cnt}")
