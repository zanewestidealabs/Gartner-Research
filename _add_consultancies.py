"""Seed PwC, Accenture, Deloitte as services-led benchmark vendors in the
3-0 SVC Pricing file. The renderer + revalidator will fill in real evidence
and corrected scores; this just adds the minimal vendor record so they
participate in the pipeline.

Run AFTER `_render_precyber_zero_vendors.py --vendor PwC ...` (or in any order
— the renderer + rescore step will pick them up via ZERO_VENDOR_URLS).
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json"
SCHEMA = ROOT / "Preemptive_Cybersecurity_Schema_v2.json"

schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
SUB_IDS = list(schema["preemptive_cybersecurity_taxonomy_v2.0"]["sub_pillars"].keys())
PILLARS = sorted({s.split("-")[0] for s in SUB_IDS})

CONSULTANCIES = [
    {
        "vendor": "PwC",
        "headquarters": "London, UK",
        "region": "Global",
        "specialization": "Cybersecurity Consulting & Managed Services",
        "is_startup": False,
        "is_ai_first": False,
        "primary_capability": "SVC",
        "description": (
            "PwC is a Big Four professional services firm with a global cybersecurity "
            "and privacy practice spanning strategy, transformation, managed security "
            "services, threat intelligence, incident response, identity, and "
            "third-party risk management. The Cybersecurity & Privacy practice "
            "operates regional managed SOCs and the annual Digital Trust Insights "
            "research program."
        ),
        "key_differentiators": (
            "Global delivery footprint, regulator-grade advisory, board-level "
            "executive reporting, integrated Strategy + Risk + Audit lineage, "
            "Digital Trust Insights benchmarking, sector-specific managed services."
        ),
        # Services-led firms peak in SVC; have meaningful coverage of EXM (third-party
        # risk advisory), ADR (threat intel and IR retainers), PPM (CTEM program design)
        "expected_coverage": [
            "SVC-01", "SVC-02", "SVC-03", "SVC-04",
            "EXM-04", "ADR-02", "ADR-03", "PPM-03",
        ],
        "ir_focus_type": "Retainer + Project",
    },
    {
        "vendor": "Accenture",
        "headquarters": "Dublin, Ireland",
        "region": "Global",
        "specialization": "Cybersecurity Consulting & Managed Services",
        "is_startup": False,
        "is_ai_first": False,
        "primary_capability": "SVC",
        "description": (
            "Accenture Security is one of the largest pure-play cybersecurity "
            "services businesses globally, with capabilities spanning cyber "
            "strategy, managed security operations, identity, cloud security, "
            "industrial / OT cyber, and resilience. Operates a network of "
            "regional cyber fusion centres and a dedicated threat intelligence "
            "group built around the Symantec Cyber Threat Intel acquisition."
        ),
        "key_differentiators": (
            "Industrial-strength managed services, global cyber fusion centre "
            "network, AI-driven SOC modernization, deep industry cybersecurity "
            "practices (FS, Public Sector, Energy), iDefense / Symantec CTI heritage."
        ),
        "expected_coverage": [
            "SVC-01", "SVC-02", "SVC-03", "SVC-04",
            "EXM-04", "ADR-02", "ADR-03", "PPM-03",
        ],
        "ir_focus_type": "Retainer + Project",
    },
    {
        "vendor": "Deloitte",
        "headquarters": "London, UK",
        "region": "Global",
        "specialization": "Cybersecurity Consulting & Managed Services",
        "is_startup": False,
        "is_ai_first": False,
        "primary_capability": "SVC",
        "description": (
            "Deloitte's Cyber & Strategic Risk practice delivers cyber strategy, "
            "detect & respond services, managed cyber operations, identity and "
            "access transformation, application security, threat intelligence "
            "and cloud cyber across a global cyber centre network. Largest "
            "professional services cyber practice by headcount."
        ),
        "key_differentiators": (
            "Largest cyber consulting workforce, 24/7 global cyber intelligence "
            "centres, integrated risk + cyber + audit advisory, deep regulatory "
            "and industry sector expertise, end-to-end CTEM program delivery."
        ),
        "expected_coverage": [
            "SVC-01", "SVC-02", "SVC-03", "SVC-04",
            "EXM-04", "ADR-02", "ADR-03", "PPM-03",
        ],
        "ir_focus_type": "Retainer + Project",
    },
]


def _empty_record(meta: dict) -> dict:
    """Build a vendor record skeleton with zero placeholders so the
    revalidator + renderer can fill it in."""
    rec = dict(meta)
    rec["capability_coverage_count"] = len(meta["expected_coverage"])
    rec["pillar_scores"] = {p: 0.0 for p in PILLARS}
    rec["sub_pillar_scores_current"] = {sid: 0.0 for sid in SUB_IDS}
    rec["sub_pillar_schema_labels"] = {}
    rec["sub_pillar_evidence"] = {}
    rec["sub_pillar_scores_v2_researched"] = {sid: 0.0 for sid in SUB_IDS}
    rec["pillar_scores_v2_researched"] = {p: 0.0 for p in PILLARS}
    rec["sub_pillar_rationale_v2"] = {}
    rec["pricing_dimension_scores"] = {}
    rec["pricing_evidence"] = {}
    rec["pricing_rationales"] = {}
    rec["delivery_model"] = "Consulting + Managed Services"
    rec["services_maturity_level"] = 5
    rec["outcome_maturity_rating"] = 4
    rec["outcome_maturity_label"] = "Outcome-Aligned"
    rec["coverage_grade"] = "B"
    rec["research_flag"] = "seed_consultancy_benchmark"
    return rec


def main() -> int:
    data = json.loads(TARGET.read_text(encoding="utf-8-sig"))
    if isinstance(data, dict):
        vendor_list = data.get("vendors", [])
        wrap = "dict"
    else:
        vendor_list = data
        wrap = "list"

    existing = {v.get("vendor") for v in vendor_list}
    added = []
    for meta in CONSULTANCIES:
        if meta["vendor"] in existing:
            print(f"  SKIP {meta['vendor']}: already in dataset")
            continue
        vendor_list.append(_empty_record(meta))
        added.append(meta["vendor"])
        print(f"  ADD  {meta['vendor']}  expected_coverage={meta['expected_coverage']}")

    if not added:
        print("Nothing to add.")
        return 0

    out = {"vendors": vendor_list} if wrap == "dict" else vendor_list
    TARGET.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[done] {TARGET.name}: {len(vendor_list)} vendors (added {len(added)})")
    print("Next:")
    print("  1) python _render_precyber_zero_vendors.py --vendor PwC")
    print("  2) python _render_precyber_zero_vendors.py --vendor Accenture")
    print("  3) python _render_precyber_zero_vendors.py --vendor Deloitte")
    print("  4) python _revalidate_precyber_scoring.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
