"""
Add Cyberoo to MDR capability and pricing vendor files.
Cyberoo is an Italian publicly-listed cybersecurity company providing
MDR (Cypeer), Threat Intelligence (CSI), Incident Response, and
compliance services (Titaan Suite). Named Gartner Representative
Vendor for MDR in 2021, 2023, and 2024.
"""
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 1. MDR Capability entry
# ============================================================
cyberoo_capability = {
    "vendor": "Cyberoo",
    "description": "Cyberoo is a European cybersecurity company specializing in Managed Detection and Response (MDR). Its Cyber Security Suite combines the Cypeer MDR platform with CSI Threat Intelligence, leveraging AI/ML and an i-SOC of 60+ specialists operating 24/7. Publicly listed on Euronext Growth Milan, Cyberoo serves 700+ customers in EMEA.",
    "region": "EMEA",
    "headquarters": "Reggio Emilia, Italy",
    "founding_year": 2008,
    "funding_status": "Public (Euronext Growth Milan, IPO 2019)",
    "mdr_service_type": "Pureplay MDR",
    "target_market": "Mid-Market / Enterprise",
    "product_names": ["Cypeer (MDR)", "CSI (Cyber Threat Intelligence)", "Cypeer Sonic (Automatic Remediation)", "Titaan Neemesi (GDPR Compliance)", "Titaan Croono (IT Network Management)", "KEATRIX (Security Awareness Training)"],
    "telemetry_sources": ["EDR", "Network Traffic (Cypher Probe)", "Cloud", "Mail Server", "DNS", "Industrial OT", "Log Management"],
    "mitre_coverage": "Broad MITRE ATT&CK alignment via Cypeer platform IoC-based detection with global and custom indicators.",
    "website": "https://www.cyberoo.com",
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
    "research_status": "seed",
    "pillar_scores": {
        "TDR": 3.63, "PTI": 3.31, "ADA": 0.63, "DIS": 2.88,
        "IRA": 3.19, "AIO": 2.56, "AID": 1.0, "SOG": 3.38
    },
    "pillar_scores_v2_researched": {
        "TDR": 3.63, "PTI": 3.31, "ADA": 0.63, "DIS": 2.88,
        "IRA": 3.19, "AIO": 2.56, "AID": 1.0, "SOG": 3.38
    },
    "pillar_scores_v2_1": {
        "TDR": 3.63, "PTI": 3.31, "ADA": 0.63, "DIS": 2.88,
        "IRA": 3.19, "AIO": 2.56, "AID": 1.0, "SOG": 3.38
    },
    "sub_pillar_scores_current": {
        "TDR-01": 4.0, "TDR-02": 3.25, "TDR-03": 3.75, "TDR-04": 3.5,
        "PTI-01": 3.5, "PTI-02": 3.25, "PTI-03": 3.0, "PTI-04": 3.5,
        "ADA-01": 1.0, "ADA-02": 0.5, "ADA-03": 0.5, "ADA-04": 0.5,
        "DIS-01": 2.5, "DIS-02": 3.5, "DIS-03": 2.0, "DIS-04": 3.5,
        "IRA-01": 3.5, "IRA-02": 3.25, "IRA-03": 3.0, "IRA-04": 3.0,
        "AIO-01": 3.75, "AIO-02": 3.0, "AIO-03": 1.5, "AIO-04": 2.0,
        "AID-01": 1.5, "AID-02": 1.0, "AID-03": 0.5, "AID-04": 1.0,
        "SOG-01": 3.5, "SOG-02": 3.25, "SOG-03": 3.5, "SOG-04": 3.25
    },
    "sub_pillar_scores_v2_1": {
        "TDR-01": 4.0, "TDR-02": 3.25, "TDR-03": 3.75, "TDR-04": 3.5,
        "PTI-01": 3.5, "PTI-02": 3.25, "PTI-03": 3.0, "PTI-04": 3.5,
        "ADA-01": 1.0, "ADA-02": 0.5, "ADA-03": 0.5, "ADA-04": 0.5,
        "DIS-01": 2.5, "DIS-02": 3.5, "DIS-03": 2.0, "DIS-04": 3.5,
        "IRA-01": 3.5, "IRA-02": 3.25, "IRA-03": 3.0, "IRA-04": 3.0,
        "AIO-01": 3.75, "AIO-02": 3.0, "AIO-03": 1.5, "AIO-04": 2.0,
        "AID-01": 1.5, "AID-02": 1.0, "AID-03": 0.5, "AID-04": 1.0,
        "SOG-01": 3.5, "SOG-02": 3.25, "SOG-03": 3.5, "SOG-04": 3.25
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
    "notable_differentiation": "Only Italian company named Gartner Representative Vendor for MDR (2021, 2023, 2024). Publicly listed on Euronext Growth Milan. Cypeer platform combines AI/ML Level-0 triage with multi-tier i-SOC (60+ specialists). Cypeer Sonic automatic remediation. CSI threat intelligence with deep/dark web monitoring, brand protection, and supply chain scanning. CYB-CERT accredited by TF-CSIRT/Trusted Introducer. Cybersecurity Made in Europe label from ECSO.",
    "notable_differentiation_v2_1": "Strongest: Signal Correlation & Alert Triage (4.0), Automated Containment (3.75), AI-Driven Analytics (3.75), Brand Protection (3.5), Digital Risk Intelligence (3.5), IR Planning (3.5), Service Transparency (3.5). Growth areas: Autonomous Deception & AMTD (0.63), AI Development & Platform Maturity (1.0), NLP & LLM Integration (1.5).",
    "research_confidence": "medium",
    "research_confidence_v2_1": "medium",
    "v2_1_adjustment_summary": {
        "increased": 0,
        "decreased": 0,
        "validated": 0,
        "no_change": 32,
        "total": 32
    },
    "evidence_quality_summary": "Seed scores based on web research of Cyberoo product pages (Cypeer MDR, CSI threat intelligence, incident response, company profile, certifications). Gartner Representative Vendor status across 3 consecutive Market Guides provides strong MDR baseline confidence. Detailed capability evidence from English-language product pages."
}

# ============================================================
# 2. MDR Pricing entry
# ============================================================
cyberoo_pricing = {
    "vendor": "Cyberoo",
    "description": "Cyberoo is a European cybersecurity company providing MDR (Cypeer), Threat Intelligence (CSI), Incident Response, and compliance/network management services (Titaan Suite).",
    "region": "EMEA",
    "headquarters": "Reggio Emilia, Italy",
    "mdr_service_type": "Pureplay MDR",
    "target_market": "Mid-Market / Enterprise",
    "product_names": ["Cypeer (MDR)", "CSI (Cyber Threat Intelligence)", "Cypeer Sonic", "Titaan Neemesi", "Titaan Croono"],
    "website": "https://www.cyberoo.com",
    "research_status": "seed",
    "pricing_analysis": "Cyberoo operates a platform subscription model with its Cyber Security Suite (Cypeer + CSI). Two MDR tiers available: Cypeer Pure and Cypeer Sonic (with automatic remediation). Additional modules for compliance (Titaan Neemesi), network management (Titaan Croono), and security awareness (KEATRIX). Incident Response available as retainer or on-demand. No published pricing; enterprise quoting model. Listed on Euronext Growth Milan since 2019.",
    "pricing_model_type": "Subscription + Module Add-ons",
    "pricing_model_details": {
        "subscription_components": [
            "Cypeer MDR platform subscription",
            "CSI Threat Intelligence platform subscription",
            "24/7 i-SOC analyst coverage",
            "Cypeer Sonic automatic remediation tier"
        ],
        "usage_components": [
            "Number of endpoints/assets monitored",
            "Data volume and log ingestion",
            "Number of integrated security tools"
        ],
        "fixed_components": [
            "Integration assessment and deployment",
            "Configuration and turnkey setup",
            "Incident Response retainer fee"
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
        "PRC-FIX": 2,
        "PRC-SUC": 1,
        "PRC-COM": 2,
        "PRC-OUT": 1
    },
    "pricing_dimension_scores_v2": {
        "PRC-SUB": 3.0,
        "PRC-USG": 2.0,
        "PRC-FIX": 2.0,
        "PRC-SUC": 1.0,
        "PRC-COM": 2.0,
        "PRC-OUT": 1.0
    },
    "pricing_overall_score": 1.83,
    "pricing_overall_score_v2": 1.83,
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
    "outcome_maturity_rationale_v2": "Seed rating - no outcome-based pricing evidence found. Cyberoo uses subscription/module-based pricing (Cypeer Pure, Cypeer Sonic tiers) without documented outcome or success fee components.",
    "outcome_signals_v2": {
        "pricing_changes_on_outcomes": False,
        "metrics_verifiable": False,
        "ai_efficiency_shared": False,
        "contract_embedded": False,
        "track_record": False,
        "roi_aligned": False
    },
    "outcome_evidence": {
        "source_urls": ["https://www.cyberoo.com"],
        "excerpts": [],
        "notes": "Seed entry - no outcome pricing evidence found. Cyberoo is publicly listed, suggesting potential for pricing transparency evolution."
    },
    "capability_analysis": "Cyberoo delivers 24/7 MDR through its Cypeer platform, combining AI-driven Level-0 triage with a multi-tier i-SOC (60+ specialists across Italy, Ukraine, Poland). The Cyber Security Suite bundles Cypeer (internal monitoring) with CSI (external threat intelligence via deep/dark web). Cypeer Sonic adds automatic remediation. Supports EDR, network, cloud, industrial OT, mail, and DNS telemetry sources.",
    "granular_mapping": {
        "TDR": {"TDR-01": 4.0, "TDR-02": 3.25, "TDR-03": 3.75, "TDR-04": 3.5},
        "PTI": {"PTI-01": 3.5, "PTI-02": 3.25, "PTI-03": 3.0, "PTI-04": 3.5},
        "ADA": {"ADA-01": 1.0, "ADA-02": 0.5, "ADA-03": 0.5, "ADA-04": 0.5},
        "DIS": {"DIS-01": 2.5, "DIS-02": 3.5, "DIS-03": 2.0, "DIS-04": 3.5},
        "IRA": {"IRA-01": 3.5, "IRA-02": 3.25, "IRA-03": 3.0, "IRA-04": 3.0},
        "AIO": {"AIO-01": 3.75, "AIO-02": 3.0, "AIO-03": 1.5, "AIO-04": 2.0},
        "AID": {"AID-01": 1.5, "AID-02": 1.0, "AID-03": 0.5, "AID-04": 1.0},
        "SOG": {"SOG-01": 3.5, "SOG-02": 3.25, "SOG-03": 3.5, "SOG-04": 3.25}
    },
    "pillar_scores": {
        "TDR": 3.63, "PTI": 3.31, "ADA": 0.63, "DIS": 2.88,
        "IRA": 3.19, "AIO": 2.56, "AID": 1.0, "SOG": 3.38
    }
}


def main():
    # ── Add to Capability file ──
    cap_file = os.path.join(BASE_DIR, "MDR Services Vendor 2-1 Consolidated.json")
    with open(cap_file, "r", encoding="utf-8-sig") as f:
        cap_data = json.load(f)

    cap_vendors = cap_data["vendors"]
    existing = [v for v in cap_vendors if v.get("vendor", "").lower() == "cyberoo"]
    if existing:
        print(f"[SKIP] Cyberoo already exists in capability file (replacing).")
        cap_vendors = [v for v in cap_vendors if v.get("vendor", "").lower() != "cyberoo"]

    cap_vendors.append(cyberoo_capability)
    cap_data["vendors"] = cap_vendors

    with open(cap_file, "w", encoding="utf-8") as f:
        json.dump(cap_data, f, indent=2, ensure_ascii=False)
    print(f"[OK] Added Cyberoo to capability file. Total vendors: {len(cap_vendors)}")

    # ── Add to Pricing file ──
    price_file = os.path.join(BASE_DIR, "MDR Services Vendor Pricing 2-0 Researched.json")
    with open(price_file, "r", encoding="utf-8-sig") as f:
        price_data = json.load(f)

    price_vendors = price_data["vendors"]
    existing_p = [v for v in price_vendors if v.get("vendor", "").lower() == "cyberoo"]
    if existing_p:
        print(f"[SKIP] Cyberoo already exists in pricing file (replacing).")
        price_vendors = [v for v in price_vendors if v.get("vendor", "").lower() != "cyberoo"]

    price_vendors.append(cyberoo_pricing)
    price_data["vendors"] = price_vendors

    with open(price_file, "w", encoding="utf-8") as f:
        json.dump(price_data, f, indent=2, ensure_ascii=False)
    print(f"[OK] Added Cyberoo to pricing file. Total vendors: {len(price_vendors)}")

    # ── Verify ──
    for label, path in [("Capability", cap_file), ("Pricing", price_file)]:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        vs = d["vendors"]
        cy = [v for v in vs if v.get("vendor", "").lower() == "cyberoo"]
        if cy:
            p = cy[0]
            print(f"[VERIFY] {label}: Cyberoo found, vendor={p['vendor']}, "
                  f"pillar_scores={list(p.get('pillar_scores',{}).keys()) if p.get('pillar_scores') else 'N/A'}, "
                  f"pricing_scores={list(p.get('pricing_dimension_scores_v2',{}).keys()) if p.get('pricing_dimension_scores_v2') else 'N/A'}")
        else:
            print(f"[ERROR] {label}: Cyberoo NOT found!")


if __name__ == "__main__":
    main()
