"""
Add First Watch Technologies to MDR capability and pricing vendor files.
First Watch Technologies, Inc. is a cybersecurity company providing MDR,
MxDR, SMB cyber solutions, and identity theft protection services.
Uses SentinelOne platform with proprietary detections and Devo SIEM.
"""
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 1. MDR Capability entry
# ============================================================
firstwatch_capability = {
    "vendor": "First Watch Technologies",
    "description": "First Watch Technologies, Inc. is a cybersecurity company providing managed detection and response (MDR), managed extended detection and response (MxDR), SMB cyber solutions, and identity theft protection services. The company combines SentinelOne's AI-driven threat detections with proprietary behavior-based detections and a dedicated human analyst model (Squad Model) for 24/7/365 monitoring, threat hunting, and remediation.",
    "region": "North America",
    "headquarters": "United States",
    "year_founded": 2015,
    "employee_count_range": "20-50",
    "funding_stage": "Private",
    "total_funding": "Undisclosed",
    "is_startup": False,
    "is_ai_first": False,
    "mdr_service_type": "Platform MDR",
    "ir_focus_type": "Core Competency",
    "target_market": "SMB",
    "primary_capability": "TDR",
    "product_names": [
        "First Watch MDR",
        "First Watch MxDR",
        "First Watch SMB Cyber Solutions",
        "First Watch ID"
    ],
    "website": "https://www.firstwatchcorp.com",
    "telemetry_sources": ["Endpoint", "Network", "Email", "Firewall", "Proxy", "SIEM"],
    "mitre_coverage": "Proprietary behavior-based detections aligned to MITRE ATT&CK techniques, tactics, and procedures (TTPs)",
    "capability_analysis": "First Watch Technologies delivers 24/7/365 MDR services built on top of SentinelOne's AI-driven endpoint protection platform, augmented with proprietary behavior-based detections. Service tiers range from basic EPP/monitoring to full MxDR with cloud-based Devo SIEM, network traffic correlation, and multi-source log ingestion. Higher tiers include unlimited incident response with root cause analysis, enterprise forensic investigations, and a dedicated Squad Model with assigned cyber analysts and project managers. The company also provides SMB-focused compliance tooling (WISP, risk assessments) and identity theft protection services.",
    "capability_analysis_source": "https://www.firstwatchcorp.com/MDR.html",
    "key_differentiators": "SentinelOne + proprietary detection layering, Squad Model with dedicated analysts and PM, unlimited incident response with full RCA in higher tiers, enterprise forensic investigation capability, Slack-based analyst collaboration, MxDR tier with Devo SIEM and multi-source log correlation, bundled SMB compliance and identity protection services",
    "capability_coverage": [
        "TDR-01", "TDR-02", "TDR-03", "TDR-04",
        "PTI-01", "PTI-02", "PTI-03", "PTI-04",
        "ADA-01", "ADA-02", "ADA-03", "ADA-04",
        "DIS-01", "DIS-02", "DIS-03", "DIS-04",
        "IRA-01", "IRA-02", "IRA-03", "IRA-04",
        "AIO-01", "AIO-02", "AIO-03", "AIO-04",
        "AID-01", "AID-02", "AID-03", "AID-04",
        "SOG-01", "SOG-02", "SOG-03", "SOG-04"
    ],
    "capability_coverage_count": 32,
    "research_status": "seed",
    # Seed pillar scores based on First Watch's known capabilities
    "pillar_scores": {
        "TDR": 3.5,    # Solid 24/7 MDR via SentinelOne + proprietary detections, multi-tier service
        "PTI": 2.0,    # Relies primarily on SentinelOne Intel, limited proprietary threat intel
        "ADA": 1.0,    # No deception technology, honeypots, or AMTD capabilities mentioned
        "DIS": 1.5,    # Identity theft protection exists but not MDR-context disinformation defense
        "IRA": 3.5,    # Unlimited IR in higher tiers, forensic investigations, RCA, strong certs
        "AIO": 2.5,    # Leverages SentinelOne AI/ML, proprietary behavioral detections, no own ML ops
        "AID": 1.0,    # No AI-specific threat defense capabilities mentioned
        "SOG": 3.25    # Squad Model, dedicated PM, quarterly reviews, Slack collaboration, tiered SLAs
    },
    "pillar_scores_v2_researched": {
        "TDR": 3.5, "PTI": 2.0, "ADA": 1.0, "DIS": 1.5,
        "IRA": 3.5, "AIO": 2.5, "AID": 1.0, "SOG": 3.25
    },
    "pillar_scores_v2_1": {
        "TDR": 3.5, "PTI": 2.0, "ADA": 1.0, "DIS": 1.5,
        "IRA": 3.5, "AIO": 2.5, "AID": 1.0, "SOG": 3.25
    },
    # Sub-pillar scores - seed estimates
    "sub_pillar_scores_current": {
        "TDR-01": 4.0,  # SentinelOne AI + proprietary detections for correlation/triage
        "TDR-02": 3.5,  # Active threat hunting in higher tiers
        "TDR-03": 3.5,  # Automated threat response including ransomware rollback
        "TDR-04": 3.0,  # Response orchestration via SentinelOne, Slack collaboration
        "PTI-01": 2.5,  # Some threat landscape awareness via SentinelOne feeds
        "PTI-02": 2.0,  # Limited predictive analytics, primarily reactive
        "PTI-03": 2.0,  # Behavior-based detections aligned to ATT&CK but limited scope
        "PTI-04": 1.5,  # No specific dark web or adversary tracking mentioned
        "ADA-01": 1.0,  # No deception technology mentioned
        "ADA-02": 1.0,  # No moving target defense
        "ADA-03": 1.0,  # No dynamic attack surface management
        "ADA-04": 1.0,  # No counter-adversary operations
        "DIS-01": 1.0,  # No deepfake/synthetic media detection
        "DIS-02": 2.0,  # Identity theft protection has some identity defense aspects
        "DIS-03": 1.5,  # Limited social engineering detection focus
        "DIS-04": 1.5,  # Identity monitoring provides limited brand/exec protection
        "IRA-01": 3.5,  # Strong IR scoping/triage with forensic-certified team
        "IRA-02": 4.0,  # Containment and isolation via SentinelOne + analyst response
        "IRA-03": 3.5,  # Ransomware rollback, remediation, recovery guidance
        "IRA-04": 3.0,  # Root Cause Analysis, Initial Infection Vector analysis
        "AIO-01": 3.5,  # SentinelOne Static AI + Behavioral AI drives analytics
        "AIO-02": 2.0,  # No own ML model operations, relies on SentinelOne
        "AIO-03": 2.0,  # No NLP/LLM integration mentioned
        "AIO-04": 2.5,  # Some AI governance through tiered service transparency
        "AID-01": 1.0,  # No AI attack detection capabilities
        "AID-02": 1.0,  # No AI supply chain security
        "AID-03": 1.0,  # No adversarial ML defense
        "AID-04": 1.0,  # No AI-specific threat intelligence
        "SOG-01": 3.5,  # 24/7 coverage, Squad Model with dedicated analysts
        "SOG-02": 3.0,  # Tiered SLA structure across service levels
        "SOG-03": 3.25, # Slack collaboration, documented threat responses, quarterly reviews
        "SOG-04": 3.25  # Quarterly threat landscape reviews, continuous posture improvement
    },
    "sub_pillar_scores_v2_researched": {
        "TDR-01": 4.0, "TDR-02": 3.5, "TDR-03": 3.5, "TDR-04": 3.0,
        "PTI-01": 2.5, "PTI-02": 2.0, "PTI-03": 2.0, "PTI-04": 1.5,
        "ADA-01": 1.0, "ADA-02": 1.0, "ADA-03": 1.0, "ADA-04": 1.0,
        "DIS-01": 1.0, "DIS-02": 2.0, "DIS-03": 1.5, "DIS-04": 1.5,
        "IRA-01": 3.5, "IRA-02": 4.0, "IRA-03": 3.5, "IRA-04": 3.0,
        "AIO-01": 3.5, "AIO-02": 2.0, "AIO-03": 2.0, "AIO-04": 2.5,
        "AID-01": 1.0, "AID-02": 1.0, "AID-03": 1.0, "AID-04": 1.0,
        "SOG-01": 3.5, "SOG-02": 3.0, "SOG-03": 3.25, "SOG-04": 3.25
    },
    "sub_pillar_scores_v2_1": {
        "TDR-01": 4.0, "TDR-02": 3.5, "TDR-03": 3.5, "TDR-04": 3.0,
        "PTI-01": 2.5, "PTI-02": 2.0, "PTI-03": 2.0, "PTI-04": 1.5,
        "ADA-01": 1.0, "ADA-02": 1.0, "ADA-03": 1.0, "ADA-04": 1.0,
        "DIS-01": 1.0, "DIS-02": 2.0, "DIS-03": 1.5, "DIS-04": 1.5,
        "IRA-01": 3.5, "IRA-02": 4.0, "IRA-03": 3.5, "IRA-04": 3.0,
        "AIO-01": 3.5, "AIO-02": 2.0, "AIO-03": 2.0, "AIO-04": 2.5,
        "AID-01": 1.0, "AID-02": 1.0, "AID-03": 1.0, "AID-04": 1.0,
        "SOG-01": 3.5, "SOG-02": 3.0, "SOG-03": 3.25, "SOG-04": 3.25
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
    "sub_pillar_evidence": {},
    "sub_pillar_rationale_v2": {},
    "sub_pillar_rationale_v2_1": {},
    "sub_pillar_rationale_v2_1_text": {},
    "sub_pillar_rationale_v2_consolidated": {},
    "notable_differentiation": "SentinelOne AI-driven detections layered with proprietary behavior-based detections, Squad Model with dedicated cyber analysts and project manager, unlimited incident response with full root cause analysis and initial infection vector determination, enterprise forensic investigation capability, Slack-based real-time collaboration, MxDR tier with Devo cloud SIEM and multi-source log ingestion, bundled SMB compliance (WISP) and identity theft protection.",
    "notable_differentiation_v2_1": "Strongest: Signal Correlation & Alert Triage (4.0), Containment & Isolation (4.0), IR Scoping & Triage (3.5), AI-Driven Analytics (3.5), 24/7 SOC Coverage (3.5). Growth areas: Autonomous Deception & AMTD (1.0), AI Development & Platform Maturity (1.0), Disinformation Defense (1.5).",
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
firstwatch_pricing = {
    "vendor": "First Watch Technologies",
    "description": "First Watch Technologies, Inc. is a cybersecurity company providing MDR, MxDR, SMB cyber solutions, and identity theft protection services.",
    "region": "North America",
    "headquarters": "United States",
    "mdr_service_type": "Platform MDR",
    "target_market": "SMB",
    "product_names": [
        "First Watch MDR",
        "First Watch MxDR",
        "First Watch SMB Cyber Solutions",
        "First Watch ID"
    ],
    "website": "https://www.firstwatchcorp.com",
    "research_status": "seed",
    "pricing_analysis": "First Watch Technologies uses a tiered subscription model with four service levels increasing in capability scope. Pricing is endpoint-based with tiers adding active threat hunting, incident response, forensic investigation, Squad Model (dedicated analysts), and MxDR with SIEM. SMB Cyber Solutions bundles compliance tooling (WISP, risk assessments) with cyber liability insurance. Specific pricing not publicly available. The company advertises itself as having the lowest retail price in market.",
    "pricing_model_type": "Tiered Subscription",
    "pricing_model_details": {
        "subscription_components": [
            "Next-Gen AV (EPP) with SentinelOne AI",
            "Managed threat detection and response",
            "24x7 threat monitoring and alerting"
        ],
        "usage_components": [
            "Number of endpoints monitored",
            "Log volume for MxDR/SIEM tier (Email, Firewall, Proxy)",
            "Number of data sources ingested"
        ],
        "fixed_components": [
            "Customized EPP configuration and setup",
            "Onboarding and environment tuning",
            "Initial deployment"
        ],
        "success_fee_components": [],
        "outcome_linked_components": [],
        "published_pricing": False,
        "pricing_calculator_available": False,
        "usage_dashboard_available": True
    },
    "pricing_dimension_scores": {
        "PRC-SUB": 3,
        "PRC-USG": 2,
        "PRC-FIX": 3,
        "PRC-SUC": 1,
        "PRC-COM": 3,
        "PRC-OUT": 1
    },
    "pricing_dimension_scores_v2": {
        "PRC-SUB": 3.0,
        "PRC-USG": 2.0,
        "PRC-FIX": 3.0,
        "PRC-SUC": 1.0,
        "PRC-COM": 3.0,
        "PRC-OUT": 1.0
    },
    "pricing_overall_score": 2.17,
    "pricing_overall_score_v2": 2.17,
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
    "outcome_maturity_rationale_v2": "Seed rating - no outcome-based pricing evidence found. First Watch Technologies uses tiered subscription pricing without documented outcome or success fee components.",
    "outcome_signals_v2": {
        "pricing_changes_on_outcomes": False,
        "metrics_verifiable": False,
        "ai_efficiency_shared": False,
        "contract_embedded": False,
        "track_record": False,
        "roi_aligned": False
    },
    "outcome_evidence": {
        "source_urls": ["https://www.firstwatchcorp.com/MDR.html"],
        "excerpts": [],
        "notes": "Seed entry - no outcome pricing evidence found. Company advertises lowest retail price."
    },
    "capability_analysis": "First Watch Technologies delivers 24/7/365 MDR services built on SentinelOne's AI-driven endpoint protection, augmented with proprietary behavior-based detections and a dedicated Squad Model analyst team.",
    "granular_mapping": {
        "TDR": {"TDR-01": 4.0, "TDR-02": 3.5, "TDR-03": 3.5, "TDR-04": 3.0},
        "PTI": {"PTI-01": 2.5, "PTI-02": 2.0, "PTI-03": 2.0, "PTI-04": 1.5},
        "ADA": {"ADA-01": 1.0, "ADA-02": 1.0, "ADA-03": 1.0, "ADA-04": 1.0},
        "DIS": {"DIS-01": 1.0, "DIS-02": 2.0, "DIS-03": 1.5, "DIS-04": 1.5},
        "IRA": {"IRA-01": 3.5, "IRA-02": 4.0, "IRA-03": 3.5, "IRA-04": 3.0},
        "AIO": {"AIO-01": 3.5, "AIO-02": 2.0, "AIO-03": 2.0, "AIO-04": 2.5},
        "AID": {"AID-01": 1.0, "AID-02": 1.0, "AID-03": 1.0, "AID-04": 1.0},
        "SOG": {"SOG-01": 3.5, "SOG-02": 3.0, "SOG-03": 3.25, "SOG-04": 3.25}
    },
    "pillar_scores": {
        "TDR": 3.5, "PTI": 2.0, "ADA": 1.0, "DIS": 1.5,
        "IRA": 3.5, "AIO": 2.5, "AID": 1.0, "SOG": 3.25
    }
}


def main():
    ts = datetime.utcnow().isoformat() + "Z"

    # ── Add to Capability file ──
    cap_file = os.path.join(BASE_DIR, "MDR Services Vendor 2-1 Consolidated.json")
    with open(cap_file, "r", encoding="utf-8-sig") as f:
        cap_data = json.load(f)

    cap_vendors = cap_data["vendors"]
    existing = [v for v in cap_vendors if v.get("vendor", "").lower() == "first watch technologies"]
    if existing:
        print(f"[SKIP] First Watch Technologies already exists in capability file (replacing).")
        cap_vendors = [v for v in cap_vendors if v.get("vendor", "").lower() != "first watch technologies"]

    cap_vendors.append(firstwatch_capability)
    cap_data["vendors"] = cap_vendors
    cap_data["vendor_count"] = len(cap_vendors)

    with open(cap_file, "w", encoding="utf-8") as f:
        json.dump(cap_data, f, indent=2, ensure_ascii=False)
    print(f"[OK] Added First Watch Technologies to capability file. Total vendors: {len(cap_vendors)}")

    # ── Add to Pricing base file ──
    price_file = os.path.join(BASE_DIR, "MDR Services Vendor Pricing 2-0 Researched.json")
    with open(price_file, "r", encoding="utf-8-sig") as f:
        price_data = json.load(f)

    price_vendors = price_data["vendors"]
    existing_p = [v for v in price_vendors if v.get("vendor", "").lower() == "first watch technologies"]
    if existing_p:
        print(f"[SKIP] First Watch Technologies already exists in pricing base file (replacing).")
        price_vendors = [v for v in price_vendors if v.get("vendor", "").lower() != "first watch technologies"]

    price_vendors.append(firstwatch_pricing)
    price_data["vendors"] = price_vendors

    with open(price_file, "w", encoding="utf-8") as f:
        json.dump(price_data, f, indent=2, ensure_ascii=False)
    print(f"[OK] Added First Watch Technologies to pricing base file. Total vendors: {len(price_vendors)}")

    # ── Add to Pricing enriched file ──
    enriched_file = os.path.join(BASE_DIR, "MDR Services Vendor Pricing 2-1 AI Enriched.json")
    with open(enriched_file, "r", encoding="utf-8-sig") as f:
        enriched_data = json.load(f)

    enriched_vendors = enriched_data["vendors"]
    existing_e = [v for v in enriched_vendors if v.get("vendor", "").lower() == "first watch technologies"]
    if existing_e:
        print(f"[SKIP] First Watch Technologies already exists in pricing enriched file (replacing).")
        enriched_vendors = [v for v in enriched_vendors if v.get("vendor", "").lower() != "first watch technologies"]

    enriched_vendors.append(firstwatch_pricing)
    enriched_data["vendors"] = enriched_vendors

    with open(enriched_file, "w", encoding="utf-8") as f:
        json.dump(enriched_data, f, indent=2, ensure_ascii=False)
    print(f"[OK] Added First Watch Technologies to pricing enriched file. Total vendors: {len(enriched_vendors)}")

    # ── Verify ──
    for label, path in [
        ("Capability", cap_file),
        ("Pricing-Base", price_file),
        ("Pricing-Enriched", enriched_file)
    ]:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        vs = d["vendors"]
        fw = [v for v in vs if v.get("vendor", "").lower() == "first watch technologies"]
        if fw:
            p = fw[0]
            print(f"[VERIFY] {label}: First Watch Technologies found, vendor={p['vendor']}, "
                  f"pillar_scores={list(p.get('pillar_scores',{}).keys()) if p.get('pillar_scores') else 'N/A'}, "
                  f"pricing_scores={list(p.get('pricing_dimension_scores_v2',{}).keys()) if p.get('pricing_dimension_scores_v2') else 'N/A'}")
        else:
            print(f"[ERROR] {label}: First Watch Technologies NOT found!")


if __name__ == "__main__":
    main()
