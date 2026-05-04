import json
d = json.load(open(r"CNAPP Vendor 1-2 Researched.json", encoding="utf-8"))
print(f"{'Vendor':<22}{'Grade':<7}{'Cov':<5}{'HighConf':<10}{'MedConf':<10}{'None':<6}")
print("-" * 60)
for v in sorted(d["vendors"], key=lambda x: -x["capability_coverage_count"]):
    rs = v["rationales_v1"].values()
    hi = sum(1 for r in rs if r["confidence"] == "high")
    md = sum(1 for r in rs if r["confidence"] == "medium")
    no = sum(1 for r in rs if r["confidence"] == "none")
    print(f"{v['vendor']:<22}{v['coverage_grade']:<7}{v['capability_coverage_count']:<5}{hi:<10}{md:<10}{no:<6}")
