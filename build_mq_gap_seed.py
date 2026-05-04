#!/usr/bin/env python3
"""
Build MQ Gap Seed from existing MDR vendor data.

Reads MDR Services Vendor 2-1 Consolidated.json and produces
MDR Services Vendor MQ Gap 1-0 Seed.json with:
  - All vendor metadata carried over
  - Gap pillar/sub-pillar score stubs (null) ready for research
  - Pre-populated hints from existing data to guide researchers
"""
import json, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).parent

# Load MDR vendor data
mdr_file = ROOT / "MDR Services Vendor 2-1 Consolidated.json"
with open(mdr_file, "r", encoding="utf-8") as f:
    mdr_data = json.load(f)

# Load MQ Gap schema for pillar/sub-pillar structure
schema_file = ROOT / "MQ_Gap_Schema_1_0.json"
with open(schema_file, "r", encoding="utf-8") as f:
    schema = json.load(f)

# Build sub-pillar list from schema
gap_pillars = []
gap_sub_pillars = []
for p in schema["pillars"]:
    gap_pillars.append(p["pillar_id"])
    for sp in p["sub_pillars"]:
        gap_sub_pillars.append(sp["sub_pillar_id"])

def _assign_tier(vendor):
    """Assign research tier based on average pillar score (v2_1 preferred)."""
    ps = vendor.get("pillar_scores_v2_1") or vendor.get("pillar_scores", {})
    if ps:
        avg = sum(ps.values()) / len(ps)
    else:
        avg = 0
    if avg >= 3.5:
        return "tier_1"
    elif avg >= 2.5:
        return "tier_2"
    else:
        return "tier_3"

# Process each vendor
seed_vendors = []
for v in mdr_data["vendors"]:
    vendor_entry = {
        "vendor": v["vendor"],
        "website": v.get("website", ""),
        "headquarters": v.get("headquarters", ""),
        "year_founded": v.get("year_founded"),
        "employee_count_range": v.get("employee_count_range", ""),
        "funding_stage": v.get("funding_stage", ""),
        "total_funding": v.get("total_funding", ""),
        "region": v.get("region", ""),
        "target_market": v.get("target_market", ""),
        "mdr_service_type": v.get("mdr_service_type", ""),
        "delivery_model": v.get("delivery_model", ""),
        "description": v.get("description", ""),
        "key_differentiators": v.get("key_differentiators", ""),
        # Pre-populated research hints from existing data
        "existing_data_hints": {
            "funding_stage": v.get("funding_stage", ""),
            "employee_count_range": v.get("employee_count_range", ""),
            "year_founded": v.get("year_founded"),
            "region": v.get("region", ""),
            "target_market": v.get("target_market", ""),
            "is_startup": v.get("is_startup", False),
            "is_ai_first": v.get("is_ai_first", False),
            "mdr_overall_score": round(sum((v.get("pillar_scores_v2_1") or v.get("pillar_scores", {})).values()) / max(len((v.get("pillar_scores_v2_1") or v.get("pillar_scores", {})).values()), 1), 2),
            "pillar_scores": v.get("pillar_scores_v2_1") or v.get("pillar_scores", {}),
        },
        # Gap scores — all null, ready for research
        "mq_gap_pillar_scores": {pid: None for pid in gap_pillars},
        "mq_gap_sub_pillar_scores": {spid: None for spid in gap_sub_pillars},
        # Rationale stubs
        "mq_gap_rationales": {
            pid: {
                sp["sub_pillar_id"]: {
                    "score": None,
                    "rationale": "",
                    "evidence_sources": [],
                    "confidence": "low"
                }
                for sp in p["sub_pillars"]
            }
            for p in schema["pillars"]
            for pid in [p["pillar_id"]]
        },
        "mq_gap_research_status": "not_started",
        "mq_gap_research_tier": _assign_tier(v)
    }
    seed_vendors.append(vendor_entry)

# Sort by vendor name
seed_vendors.sort(key=lambda x: x["vendor"])

output = {
    "schema_ref": "MQ_Gap_Schema_1_0.json",
    "schema_version": "1.0",
    "source_schema": "MDR",
    "source_file": "MDR Services Vendor 2-1 Consolidated.json",
    "assessment_type": "mq_gap_seed",
    "description": "MQ Gap criteria seed data for MDR vendors. Sub-pillar scores are null and require research.",
    "vendor_count": len(seed_vendors),
    "gap_pillars": gap_pillars,
    "gap_sub_pillars": gap_sub_pillars,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "script": "build_mq_gap_seed.py",
    "vendors": seed_vendors
}

out_file = ROOT / "MDR Services Vendor MQ Gap 1-0 Seed.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Generated {out_file.name}")
print(f"  Vendors: {len(seed_vendors)}")
print(f"  Gap pillars: {len(gap_pillars)}")
print(f"  Gap sub-pillars: {len(gap_sub_pillars)}")

# Tier breakdown
tiers = {}
for sv in seed_vendors:
    t = sv["mq_gap_research_tier"]
    tiers[t] = tiers.get(t, 0) + 1
for t in sorted(tiers):
    print(f"  {t}: {tiers[t]} vendors")
