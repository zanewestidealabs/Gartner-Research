import json

CBS = {
    "vendor": "CBS HOLDING S.A.",
    "website": "https://sek.com.br",
    "headquarters": "Sao Paulo, Brazil",
    "region": "Latin America",
    "employee_count_range": "500-1000",
    "funding_stage": "Private Equity",
    "mdr_service_type": "Extended MDR",
    "target_market": "Enterprise (LatAm)",
    "ability_to_execute": {
        "composite_score": 2.93,
        "criteria": {
            "ATE-1": {"name": "Products/Services",        "score": 2.80, "weight": 0.20},
            "ATE-2": {"name": "Overall Viability",         "score": 3.20, "weight": 0.18},
            "ATE-3": {"name": "Sales Execution/Pricing",   "score": 2.40, "weight": 0.12},
            "ATE-4": {"name": "Market Responsiveness",     "score": 2.80, "weight": 0.12},
            "ATE-5": {"name": "Marketing Execution",       "score": 2.50, "weight": 0.06},
            "ATE-6": {"name": "Customer Experience",       "score": 3.00, "weight": 0.18},
            "ATE-7": {"name": "Operations",                "score": 3.40, "weight": 0.14},
        }
    },
    "completeness_of_vision": {
        "composite_score": 2.70,
        "criteria": {
            "COV-1": {"name": "Market Understanding",       "score": 2.80, "weight": 0.18},
            "COV-2": {"name": "Marketing Strategy",         "score": 2.30, "weight": 0.10},
            "COV-3": {"name": "Sales Strategy",             "score": 2.50, "weight": 0.10},
            "COV-4": {"name": "Offering Strategy",          "score": 2.80, "weight": 0.18},
            "COV-5": {"name": "Business Model",             "score": 2.90, "weight": 0.12},
            "COV-6": {"name": "Vertical/Industry Strategy", "score": 2.30, "weight": 0.08},
            "COV-7": {"name": "Innovation",                 "score": 2.50, "weight": 0.16},
            "COV-8": {"name": "Geographic Strategy",        "score": 3.50, "weight": 0.08},
        }
    },
    "quadrant": "Niche Players",
    "mq_gap_research_tier": "tier_2"
}

# Verify composites
ate = sum(v["score"] * v["weight"] for v in CBS["ability_to_execute"]["criteria"].values())
cov = sum(v["score"] * v["weight"] for v in CBS["completeness_of_vision"]["criteria"].values())
print(f"ATE computed: {ate:.4f}  stored: {CBS['ability_to_execute']['composite_score']}")
print(f"COV computed: {cov:.4f}  stored: {CBS['completeness_of_vision']['composite_score']}")

with open("MDR Services Vendor MQ Scores.json", encoding="utf-8") as f:
    data = json.load(f)

vendors = data.get("vendors", [])
before = len(vendors)
vendors = [v for v in vendors if v.get("vendor", "").lower() != "cbs holding s.a."]
vendors.append(CBS)
data["vendors"] = vendors

with open("MDR Services Vendor MQ Scores.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Saved. Vendors: {before} -> {len(vendors)}")
print(f"CBS HOLDING added | Quadrant: Niche Players | ATE={ate:.2f} | COV={cov:.2f}")
