"""Quick audit of PMR vendor distribution for enrichment prioritization."""
import json
from collections import Counter

d = json.load(open("Product Market Readiness Vendor 1-0 Seed.json", encoding="utf-8-sig"))
vendors = d["vendors"]

grades = Counter(v.get("coverage_grade", "?") for v in vendors)
types = Counter(v.get("vendor_type", "?") for v in vendors)
url_count = sum(1 for v in vendors if v.get("website", ""))

print("Coverage grades:", dict(sorted(grades.items())))
print("Vendor types:", dict(sorted(types.items())))
print("Have website URL:", url_count, "/", len(vendors))
print()

# Top 20 vendors by overall GTM
top = sorted(vendors, key=lambda x: x.get("overall_gtm_score", 0), reverse=True)[:20]
print("Top 20 by GTM score:")
for v in top:
    srcs = v.get("source_schemas", [])
    web = "Yes" if v.get("website", "") else "No"
    name = v["vendor"]
    gtm = v["overall_gtm_score"]
    proof = v["overall_proof_score"]
    grade = v.get("coverage_grade", "?")
    print(f"  {name}: GTM={gtm}, Proof={proof}, Grade={grade}, Sources={len(srcs)}, Web={web}")
