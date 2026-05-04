"""
Add Proficio to MDR capability and pricing vendor files.
Proficio is a well-established MDR provider with ProSOC platform,
24/7 SOC-as-a-service, and automated response capabilities.
"""
import json
import copy
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 1. MDR Capability entry
# ============================================================
proficio_capability = {
    "vendor": "Proficio",
    "description": "Proficio is a managed security services provider delivering 24/7 MDR through its ProSOC platform, combining SIEM, SOAR, threat intelligence, and human analyst oversight with AI-driven detection and automated response orchestration.",
    "region": "North America",
    "headquarters": "Carlsbad, CA, USA",
    "year_founded": 2010,
    "employee_count_range": "200-500",
    "funding_stage": "Private",
    "total_funding": "Undisclosed",
    "is_startup": False,
    "is_ai_first": False,
    "mdr_service_type": "Pureplay MDR",
    "ir_focus_type": "Assistance Component",
    "target_market": "Mid-Market / Enterprise",
    "primary_capability": "TDR",
    "product_names": ["ProSOC MDR", "ProSOC SIEM", "ProSOC SOAR"],
    "website": "https://www.proficio.com",
    "telemetry_sources": ["Endpoint", "Network", "Cloud", "Identity", "Email", "SIEM"],
    "mitre_coverage": "MITRE ATT&CK-aligned detection content",
    "capability_analysis": "Proficio provides 24/7 managed detection and response through its cloud-native ProSOC platform. Combines SIEM log management, SOAR automation, and dedicated SOC analyst teams. AI-enhanced alert triage and automated containment actions. Strong compliance reporting and multi-tenant architecture for service providers.",
    "capability_analysis_source": "https://www.proficio.com/",
    "key_differentiators": "Cloud-native ProSOC platform, 24/7 SOC-as-a-service, AI-enhanced alert triage, automated active defense containment, compliance-centric MDR for regulated industries",
    "capability_coverage": [
        "TDR-01", "TDR-02", "TDR-03", "TDR-04",
        "PTI-01", "PTI-02", "PTI-03", "PTI-04",
        "ADA-01", "ADA-02", "ADA-03", "ADA-04",
        "DIS-02", "DIS-03", "DIS-04",
        "IRA-01", "IRA-02", "IRA-03", "IRA-04",
        "AIO-01", "AIO-02", "AIO-03", "AIO-04",
        "AID-01", "AID-02", "AID-03", "AID-04",
        "SOG-01", "SOG-02", "SOG-03", "SOG-04"
    ],
    "capability_coverage_count": 31,
    "research_status": "seed",
    # Seed pillar scores based on Proficio's known capabilities
    "pillar_scores": {
        "TDR": 4.0,   # Strong 24/7 detection and response, SIEM/SOAR
        "PTI": 3.0,    # Threat intel integration, curated feeds
        "ADA": 1.5,    # Limited autonomous deception capabilities
        "DIS": 1.0,    # No disinformation security offerings
        "IRA": 3.0,    # Incident response assistance, not primary IR
        "AIO": 3.5,    # AI-enhanced triage, SOAR automation
        "AID": 2.5,    # Some AI-driven detection, not fully autonomous
        "SOG": 4.0     # Strong compliance/governance, SOC maturity
    },
    "pillar_scores_v2_researched": {
        "TDR": 4.0, "PTI": 3.0, "ADA": 1.5, "DIS": 1.0,
        "IRA": 3.0, "AIO": 3.5, "AID": 2.5, "SOG": 4.0
    },
    "pillar_scores_v2_1": {
        "TDR": 4.0, "PTI": 3.0, "ADA": 1.5, "DIS": 1.0,
        "IRA": 3.0, "AIO": 3.5, "AID": 2.5, "SOG": 4.0
    },
    # Sub-pillar scores - seed estimates
    "sub_pillar_scores_current": {
        "TDR-01": 4, "TDR-02": 4, "TDR-03": 4, "TDR-04": 4,
        "PTI-01": 3, "PTI-02": 3, "PTI-03": 3, "PTI-04": 3,
        "ADA-01": 2, "ADA-02": 2, "ADA-03": 1, "ADA-04": 1,
        "DIS-01": 1, "DIS-02": 1, "DIS-03": 1, "DIS-04": 1,
        "IRA-01": 3, "IRA-02": 3, "IRA-03": 3, "IRA-04": 3,
        "AIO-01": 4, "AIO-02": 4, "AIO-03": 3, "AIO-04": 3,
        "AID-01": 3, "AID-02": 3, "AID-03": 2, "AID-04": 2,
        "SOG-01": 4, "SOG-02": 4, "SOG-03": 4, "SOG-04": 4
    },
    "sub_pillar_scores_v2_researched": {
        "TDR-01": 4, "TDR-02": 4, "TDR-03": 4, "TDR-04": 4,
        "PTI-01": 3, "PTI-02": 3, "PTI-03": 3, "PTI-04": 3,
        "ADA-01": 2, "ADA-02": 2, "ADA-03": 1, "ADA-04": 1,
        "DIS-01": 1, "DIS-02": 1, "DIS-03": 1, "DIS-04": 1,
        "IRA-01": 3, "IRA-02": 3, "IRA-03": 3, "IRA-04": 3,
        "AIO-01": 4, "AIO-02": 4, "AIO-03": 3, "AIO-04": 3,
        "AID-01": 3, "AID-02": 3, "AID-03": 2, "AID-04": 2,
        "SOG-01": 4, "SOG-02": 4, "SOG-03": 4, "SOG-04": 4
    },
    "sub_pillar_scores_v2_1": {
        "TDR-01": 4.0, "TDR-02": 4.0, "TDR-03": 4.0, "TDR-04": 4.0,
        "PTI-01": 3.0, "PTI-02": 3.0, "PTI-03": 3.0, "PTI-04": 3.0,
        "ADA-01": 2.0, "ADA-02": 2.0, "ADA-03": 1.0, "ADA-04": 1.0,
        "DIS-01": 1.0, "DIS-02": 1.0, "DIS-03": 1.0, "DIS-04": 1.0,
        "IRA-01": 3.0, "IRA-02": 3.0, "IRA-03": 3.0, "IRA-04": 3.0,
        "AIO-01": 4.0, "AIO-02": 4.0, "AIO-03": 3.0, "AIO-04": 3.0,
        "AID-01": 3.0, "AID-02": 3.0, "AID-03": 2.0, "AID-04": 2.0,
        "SOG-01": 4.0, "SOG-02": 4.0, "SOG-03": 4.0, "SOG-04": 4.0
    },
    "sub_pillar_schema_labels": {
        "TDR-01": "Signal Correlation & Alert Triage",
        "TDR-02": "Threat Hunting",
        "TDR-03": "Automated Containment",
        "TDR-04": "Response Orchestration",
        "PTI-01": "Strategic Threat Intelligence",
        "PTI-02": "Tactical Threat Feeds",
        "PTI-03": "Threat Landscape Mapping",
        "PTI-04": "Intelligence-Driven Detection",
        "ADA-01": "Deception Infrastructure",
        "ADA-02": "Adaptive Deception",
        "ADA-03": "AMTD Integration",
        "ADA-04": "Deception Analytics",
        "DIS-01": "Social Media Monitoring",
        "DIS-02": "Brand Protection",
        "DIS-03": "Takedown Services",
        "DIS-04": "Digital Risk Intelligence",
        "IRA-01": "IR Planning & Readiness",
        "IRA-02": "Forensic Investigation",
        "IRA-03": "Breach Remediation",
        "IRA-04": "Post-Incident Analysis",
        "AIO-01": "AI-Driven Analytics",
        "AIO-02": "ML Model Operations",
        "AIO-03": "NLP & LLM Integration",
        "AIO-04": "AI Governance & Explainability",
        "AID-01": "AI Attack Detection",
        "AID-02": "AI Supply Chain Security",
        "AID-03": "Adversarial ML Defense",
        "AID-04": "AI-Specific Threat Intel",
        "SOG-01": "Compliance Reporting",
        "SOG-02": "SLA Management",
        "SOG-03": "Service Transparency",
        "SOG-04": "Continuous Improvement"
    },
    # Empty evidence and rationale - will be populated by research pipeline
    "sub_pillar_evidence": {},
    "sub_pillar_rationale_v2": {},
    "sub_pillar_rationale_v2_1": {},
    "sub_pillar_rationale_v2_1_text": {},
    "sub_pillar_rationale_v2_consolidated": {},
    "notable_differentiation": "Cloud-native ProSOC platform with integrated SIEM/SOAR, 24/7 SOC-as-a-service, compliance-focused MDR for regulated industries.",
    "notable_differentiation_v2_1": "Strongest: Standard Threat Detection, Investigation & Response (4.0), Service Operations & Governance (4.0), AI Operations & Integration (3.5). Growth areas: Autonomous Deception & AMTD (1.5), Disinformation Security (1.0).",
    "research_confidence": "low",
    "research_confidence_v2_1": "low",
    "v2_1_adjustment_summary": {
        "increased": 0,
        "decreased": 0,
        "validated": 0,
        "no_change": 32,
        "total": 32
    },
    "evidence_quality_summary": "Seed scores - pending deep research with evidence extraction."
}

# ============================================================
# 2. MDR Pricing entry
# ============================================================
proficio_pricing = {
    "vendor": "Proficio",
    "description": "Proficio is a managed security services provider delivering 24/7 MDR through its ProSOC platform, combining SIEM, SOAR, threat intelligence, and human analyst oversight with AI-driven detection and automated response orchestration.",
    "region": "North America",
    "headquarters": "Carlsbad, CA, USA",
    "mdr_service_type": "Pureplay MDR",
    "target_market": "Mid-Market / Enterprise",
    "product_names": ["ProSOC MDR", "ProSOC SIEM", "ProSOC SOAR"],
    "website": "https://www.proficio.com",
    "research_status": "seed",
    "pricing_analysis": "Proficio uses a subscription-based pricing model centered on its ProSOC platform. Pricing is typically based on log data volume and number of monitored endpoints/assets. Tiered service levels available. Limited public pricing transparency but competitive mid-market positioning.",
    "pricing_model_type": "Subscription + Usage Hybrid",
    "pricing_model_details": {
        "subscription_components": [
            "ProSOC MDR platform subscription",
            "24/7 SOC analyst coverage",
            "SIEM log management"
        ],
        "usage_components": [
            "Data volume (GB/day)",
            "Number of monitored endpoints/assets"
        ],
        "fixed_components": [
            "Initial deployment and onboarding",
            "Custom integration setup"
        ],
        "success_fee_components": [],
        "outcome_linked_components": [],
        "published_pricing": False,
        "pricing_calculator_available": False,
        "usage_dashboard_available": True
    },
    # Seed pricing dimension scores
    "pricing_dimension_scores": {
        "PRC-SUB": 3,    # Subscription structure exists, limited transparency
        "PRC-USG": 3,    # Volume-based component, some tracking
        "PRC-FIX": 2,    # Basic deployment fees
        "PRC-SUC": 1,    # No success/outcome fees known
        "PRC-COM": 2,    # Some composability but limited
        "PRC-OUT": 1     # No outcome-linked pricing known
    },
    "pricing_dimension_scores_v2": {
        "PRC-SUB": 3.0,
        "PRC-USG": 3.0,
        "PRC-FIX": 2.0,
        "PRC-SUC": 1.0,
        "PRC-COM": 2.0,
        "PRC-OUT": 1.0
    },
    "pricing_overall_score": 2.0,
    "pricing_overall_score_v2": 2.0,
    "pricing_dimension_labels": {
        "PRC-SUB": "Subscription Transparency",
        "PRC-USG": "Usage-Based Alignment",
        "PRC-FIX": "Fixed Delivery Pricing",
        "PRC-SUC": "Success & Outcome Fees",
        "PRC-COM": "Composability & Overall Model Maturity",
        "PRC-OUT": "Pricing-to-Outcomes Alignment"
    },
    "pricing_dimension_rationale_v2": {},
    "pricing_dimension_rationale_v2_text": {},
    "pricing_evidence": {},
    "pricing_adjustment_summary": {
        "increased": 0,
        "decreased": 0,
        "validated": 0,
        "no_change": 6
    },
    "pricing_research_confidence": "low",
    "outcome_maturity_rating": 1,
    "outcome_maturity_rating_v2": 1,
    "outcome_maturity_rationale_v2": "Seed rating - no outcome-based pricing evidence found. Proficio appears to use traditional subscription/volume pricing without outcome or success fee components.",
    "outcome_signals_v2": {
        "pricing_changes_on_outcomes": False,
        "metrics_verifiable": False,
        "ai_efficiency_shared": False,
        "contract_embedded": False,
        "track_record": False,
        "roi_aligned": False
    },
    "outcome_evidence": {
        "source_urls": ["https://www.proficio.com"],
        "excerpts": [],
        "notes": "Seed entry - no outcome pricing evidence found."
    },
    # Also include base capability fields for compatibility
    "capability_analysis": "Proficio provides 24/7 managed detection and response through its cloud-native ProSOC platform. Combines SIEM log management, SOAR automation, and dedicated SOC analyst teams.",
    "granular_mapping": {
        "TDR": {"TDR-01": 4, "TDR-02": 4, "TDR-03": 4, "TDR-04": 4},
        "PTI": {"PTI-01": 3, "PTI-02": 3, "PTI-03": 3, "PTI-04": 3},
        "ADA": {"ADA-01": 2, "ADA-02": 2, "ADA-03": 1, "ADA-04": 1},
        "DIS": {"DIS-01": 1, "DIS-02": 1, "DIS-03": 1, "DIS-04": 1},
        "IRA": {"IRA-01": 3, "IRA-02": 3, "IRA-03": 3, "IRA-04": 3},
        "AIO": {"AIO-01": 4, "AIO-02": 4, "AIO-03": 3, "AIO-04": 3},
        "AID": {"AID-01": 3, "AID-02": 3, "AID-03": 2, "AID-04": 2},
        "SOG": {"SOG-01": 4, "SOG-02": 4, "SOG-03": 4, "SOG-04": 4}
    },
    "pillar_scores": {
        "TDR": 4.0, "PTI": 3.0, "ADA": 1.5, "DIS": 1.0,
        "IRA": 3.0, "AIO": 3.5, "AID": 2.5, "SOG": 4.0
    }
}


def main():
    # ── Add to Capability file ──
    cap_file = os.path.join(BASE_DIR, "MDR Services Vendor 2-1 Consolidated.json")
    with open(cap_file, "r", encoding="utf-8-sig") as f:
        cap_data = json.load(f)

    cap_vendors = cap_data["vendors"]
    # Check if Proficio already exists
    existing = [v for v in cap_vendors if v.get("vendor", "").lower() == "proficio"]
    if existing:
        print(f"[SKIP] Proficio already exists in capability file (replacing).")
        cap_vendors = [v for v in cap_vendors if v.get("vendor", "").lower() != "proficio"]

    cap_vendors.append(proficio_capability)
    cap_data["vendors"] = cap_vendors
    
    with open(cap_file, "w", encoding="utf-8") as f:
        json.dump(cap_data, f, indent=2, ensure_ascii=False)
    print(f"[OK] Added Proficio to capability file. Total vendors: {len(cap_vendors)}")

    # ── Add to Pricing file ──
    price_file = os.path.join(BASE_DIR, "MDR Services Vendor Pricing 2-0 Researched.json")
    with open(price_file, "r", encoding="utf-8-sig") as f:
        price_data = json.load(f)

    price_vendors = price_data["vendors"]
    existing_p = [v for v in price_vendors if v.get("vendor", "").lower() == "proficio"]
    if existing_p:
        print(f"[SKIP] Proficio already exists in pricing file (replacing).")
        price_vendors = [v for v in price_vendors if v.get("vendor", "").lower() != "proficio"]

    price_vendors.append(proficio_pricing)
    price_data["vendors"] = price_vendors

    with open(price_file, "w", encoding="utf-8") as f:
        json.dump(price_data, f, indent=2, ensure_ascii=False)
    print(f"[OK] Added Proficio to pricing file. Total vendors: {len(price_vendors)}")

    # ── Verify ──
    for label, path in [("Capability", cap_file), ("Pricing", price_file)]:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        vs = d["vendors"]
        prof = [v for v in vs if v.get("vendor", "").lower() == "proficio"]
        if prof:
            p = prof[0]
            print(f"[VERIFY] {label}: Proficio found, vendor={p['vendor']}, "
                  f"pillar_scores={list(p.get('pillar_scores',{}).keys()) if p.get('pillar_scores') else 'N/A'}, "
                  f"pricing_scores={list(p.get('pricing_dimension_scores_v2',{}).keys()) if p.get('pricing_dimension_scores_v2') else 'N/A'}")
        else:
            print(f"[ERROR] {label}: Proficio NOT found!")


if __name__ == "__main__":
    main()
