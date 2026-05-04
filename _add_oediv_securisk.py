"""
Add OEDIV SecuRisk (Oetker Group, Germany) to all MDR pipeline files.

OEDIV Oetker Daten- und Informationsverarbeitung KG is the IT-services arm of
the Oetker Group (the German family conglomerate; food, breweries, banking,
hotels). Founded 1999, headquartered in Bielefeld with offices in Oldenburg,
Augsburg, and Rostock. OEDIV provides hosting, managed services, and IT
consulting; its security business unit is OEDIV SecuRisk (Managed Security
Services + Security Operations Center). Strategic partnership with Zscaler
for cloud-security delivery; 2024 acquisition of iSM Secu-Sys AG added the
bi-Cube IAM platform. Premium German MSP/MSSP with strong data-sovereignty
and SAP-hosting heritage; primarily DACH mid-market / enterprise.

Conservative seed scoring: not present in Gartner MQ/MG; no proprietary
detection platform (delivers SOC on partner stack); limited public threat-
intel publication. Strengths concentrate in operational governance (SOG)
and hosted/managed delivery (TDR, IRA).
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENDOR_NAME = "OEDIV SecuRisk"
VENDOR_KEY = VENDOR_NAME.lower()

# ============================================================
# 1. MDR Capability entry
# ============================================================
oediv_capability = {
    "vendor": VENDOR_NAME,
    "description": (
        "OEDIV SecuRisk is the security business of OEDIV Oetker Daten- und "
        "Informationsverarbeitung KG, the IT-services arm of Germany's Oetker "
        "Group (Dr. Oetker, Radeberger, Henkell, Bankhaus Lampe, Oetker "
        "Collection). Delivers Managed Security Services and a 24/7 Security "
        "Operations Center from Bielefeld with additional German locations in "
        "Oldenburg, Augsburg, and Rostock. Strategic Zscaler partner for "
        "cloud-security delivery; expanded into IAM via the 2024 acquisition "
        "of iSM Secu-Sys AG (bi-Cube). Premium DACH MSP/MSSP positioning with "
        "a SAP-hosting heritage and German data-sovereignty story."
    ),
    "region": "EMEA",
    "headquarters": "Bielefeld, Germany",
    "founding_year": 1999,
    "funding_status": "Private (Oetker Group subsidiary)",
    "mdr_service_type": "MSP/MSSP MDR",
    "target_market": "Mid-Market / Enterprise (DACH)",
    "product_names": [
        "OEDIV SecuRisk Managed Security Services",
        "OEDIV Security Operations Center",
        "Zscaler Cloud Security (managed)",
        "bi-Cube IAM (via iSM Secu-Sys)",
        "OEDIV Hosting & Private Cloud"
    ],
    "telemetry_sources": [
        "SIEM",
        "EDR (partner)",
        "Cloud (Zscaler ZIA/ZPA, M365)",
        "SAP application logs",
        "Network traffic",
        "Identity (bi-Cube IAM)"
    ],
    "mitre_coverage": (
        "Use-case-driven MITRE ATT&CK alignment delivered through partner "
        "SIEM/EDR detection content; no published proprietary technique "
        "matrix."
    ),
    "website": "https://www.oediv-securisk.de",
    "capability_coverage": [
        "TDR-01", "TDR-02", "TDR-04",
        "PTI-02",
        "IRA-01", "IRA-02", "IRA-03", "IRA-04",
        "AIO-01",
        "SOG-01", "SOG-02", "SOG-03", "SOG-04"
    ],
    "research_status": "seed",
    "pillar_scores": {
        "TDR": 2.50, "PTI": 1.50, "ADA": 0.50, "DIS": 1.00,
        "IRA": 2.50, "AIO": 1.50, "AID": 0.50, "SOG": 3.00
    },
    "pillar_scores_v2_researched": {
        "TDR": 2.50, "PTI": 1.50, "ADA": 0.50, "DIS": 1.00,
        "IRA": 2.50, "AIO": 1.50, "AID": 0.50, "SOG": 3.00
    },
    "pillar_scores_v2_1": {
        "TDR": 2.50, "PTI": 1.50, "ADA": 0.50, "DIS": 1.00,
        "IRA": 2.50, "AIO": 1.50, "AID": 0.50, "SOG": 3.00
    },
    "sub_pillar_scores_current": {
        "TDR-01": 3.0, "TDR-02": 2.0, "TDR-03": 2.5, "TDR-04": 2.5,
        "PTI-01": 1.5, "PTI-02": 2.0, "PTI-03": 1.0, "PTI-04": 1.5,
        "ADA-01": 0.5, "ADA-02": 0.5, "ADA-03": 0.5, "ADA-04": 0.5,
        "DIS-01": 1.0, "DIS-02": 1.0, "DIS-03": 1.0, "DIS-04": 1.0,
        "IRA-01": 3.0, "IRA-02": 2.5, "IRA-03": 2.5, "IRA-04": 2.0,
        "AIO-01": 2.0, "AIO-02": 1.5, "AIO-03": 1.0, "AIO-04": 1.5,
        "AID-01": 0.5, "AID-02": 0.5, "AID-03": 0.5, "AID-04": 0.5,
        "SOG-01": 3.5, "SOG-02": 3.0, "SOG-03": 3.0, "SOG-04": 2.5
    },
    "sub_pillar_scores_v2_1": {
        "TDR-01": 3.0, "TDR-02": 2.0, "TDR-03": 2.5, "TDR-04": 2.5,
        "PTI-01": 1.5, "PTI-02": 2.0, "PTI-03": 1.0, "PTI-04": 1.5,
        "ADA-01": 0.5, "ADA-02": 0.5, "ADA-03": 0.5, "ADA-04": 0.5,
        "DIS-01": 1.0, "DIS-02": 1.0, "DIS-03": 1.0, "DIS-04": 1.0,
        "IRA-01": 3.0, "IRA-02": 2.5, "IRA-03": 2.5, "IRA-04": 2.0,
        "AIO-01": 2.0, "AIO-02": 1.5, "AIO-03": 1.0, "AIO-04": 1.5,
        "AID-01": 0.5, "AID-02": 0.5, "AID-03": 0.5, "AID-04": 0.5,
        "SOG-01": 3.5, "SOG-02": 3.0, "SOG-03": 3.0, "SOG-04": 2.5
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
    "notable_differentiation": (
        "German family-owned (Oetker Group) MSP/MSSP with strong data-"
        "sovereignty and audit-grade hosting heritage. ISO 27001 / BSI-aligned "
        "operations across four German data-center locations. SAP-hosting "
        "lineage drives deep enterprise-application telemetry. Strategic "
        "Zscaler partnership for cloud-security delivery. 2024 acquisition of "
        "iSM Secu-Sys AG added the bi-Cube IAM platform, expanding identity "
        "coverage. Premium DACH positioning rather than scale play."
    ),
    "notable_differentiation_v2_1": (
        "Strongest: Compliance Reporting (3.5), Signal Correlation & Alert "
        "Triage (3.0), IR Planning & Readiness (3.0), SLA Management (3.0), "
        "Service Transparency (3.0). Growth areas: Autonomous Deception & "
        "AMTD (0.5), AI-Specific Threat Intel (0.5), Adversarial ML Defense "
        "(0.5). No proprietary detection platform — delivery rests on partner "
        "SIEM/EDR/cloud stacks."
    ),
    "research_confidence": "low",
    "research_confidence_v2_1": "low",
    "v2_1_adjustment_summary": {
        "increased": 0,
        "decreased": 0,
        "validated": 0,
        "no_change": 32,
        "total": 32
    },
    "evidence_quality_summary": (
        "Seed scores derived from public OEDIV Group corporate site, OEDIV "
        "SecuRisk product pages, public press announcements (Zscaler "
        "partnership, iSM Secu-Sys acquisition, 25th-anniversary release), "
        "and the Oetker Group corporate description. OEDIV SecuRisk is not "
        "covered by Gartner Magic Quadrant or Market Guide for MDR. No "
        "primary customer references or analyst peer-review evidence "
        "available; scoring intentionally conservative."
    )
}

# ============================================================
# 2. MDR Pricing entry
# ============================================================
oediv_pricing = {
    "vendor": VENDOR_NAME,
    "description": (
        "OEDIV SecuRisk is the security business of Germany's Oetker Group "
        "IT-services subsidiary OEDIV KG, providing 24/7 SOC, Managed "
        "Security Services, and Zscaler-based cloud-security delivery to "
        "DACH mid-market and enterprise customers."
    ),
    "region": "EMEA",
    "headquarters": "Bielefeld, Germany",
    "mdr_service_type": "MSP/MSSP MDR",
    "target_market": "Mid-Market / Enterprise (DACH)",
    "product_names": [
        "OEDIV SecuRisk Managed Security Services",
        "OEDIV SOC",
        "Zscaler Cloud Security (managed)",
        "bi-Cube IAM"
    ],
    "website": "https://www.oediv-securisk.de",
    "research_status": "seed",
    "pricing_analysis": (
        "OEDIV operates as a German premium MSP/MSSP with bespoke contract "
        "structures typical of the segment: per-asset / per-user subscription "
        "for SOC and managed-security tiers, fixed onboarding and integration "
        "fees, and consulting-led add-ons. No published price list, no public "
        "outcome-based commercial commitments, and no public pricing "
        "calculator. Cloud-security delivery is bundled with Zscaler "
        "subscriptions; IAM is licensed via bi-Cube. Pricing transparency "
        "follows DACH MSSP norms (RFP / quote-driven)."
    ),
    "pricing_model_type": "Subscription + Consulting Add-ons",
    "pricing_model_details": {
        "subscription_components": [
            "SOC monitoring tier subscription",
            "Managed Security Services per-endpoint / per-user fee",
            "Zscaler cloud-security subscription pass-through",
            "bi-Cube IAM platform subscription"
        ],
        "usage_components": [
            "Number of endpoints / identities monitored",
            "Log volume / SIEM ingestion",
            "Number of integrated data sources"
        ],
        "fixed_components": [
            "Onboarding and integration project fee",
            "Custom use-case engineering",
            "Incident-response retainer"
        ],
        "success_fee_components": [],
        "outcome_linked_components": [],
        "published_pricing": False,
        "pricing_calculator_available": False,
        "usage_dashboard_available": False
    },
    "pricing_dimension_scores": {
        "PRC-SUB": 2,
        "PRC-USG": 2,
        "PRC-FIX": 2,
        "PRC-SUC": 1,
        "PRC-COM": 2,
        "PRC-OUT": 1
    },
    "pricing_dimension_scores_v2": {
        "PRC-SUB": 2.0,
        "PRC-USG": 2.0,
        "PRC-FIX": 2.0,
        "PRC-SUC": 1.0,
        "PRC-COM": 2.0,
        "PRC-OUT": 1.0
    },
    "pricing_overall_score": 1.67,
    "pricing_overall_score_v2": 1.67,
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
    "outcome_maturity_rationale_v2": (
        "Seed rating - no outcome-based pricing evidence found. OEDIV "
        "SecuRisk uses subscription + consulting add-on model typical of "
        "DACH MSP/MSSP segment without documented outcome or success-fee "
        "components."
    ),
    "outcome_signals_v2": {
        "pricing_changes_on_outcomes": False,
        "metrics_verifiable": False,
        "ai_efficiency_shared": False,
        "contract_embedded": False,
        "track_record": False,
        "roi_aligned": False
    },
    "outcome_evidence": {
        "source_urls": [
            "https://www.oediv-securisk.de",
            "https://www.oediv.de"
        ],
        "excerpts": [],
        "notes": (
            "Seed entry - no outcome-pricing evidence found. Family-owned "
            "(Oetker Group) governance suggests conservative commercial "
            "posture; outcome-based evolution unlikely without market "
            "pressure."
        )
    },
    "capability_analysis": (
        "OEDIV SecuRisk delivers 24/7 SOC and managed-security services "
        "from four German data-center locations (Bielefeld, Oldenburg, "
        "Augsburg, Rostock). SOC operates on partner SIEM/EDR/cloud-"
        "security stacks (notably Zscaler) rather than a proprietary "
        "platform. Strong SAP-hosting heritage drives deep enterprise-"
        "application telemetry. ISO 27001 / BSI-aligned governance and "
        "German data sovereignty are the headline differentiators. The "
        "2024 iSM Secu-Sys acquisition added the bi-Cube IAM platform."
    ),
    "granular_mapping": {
        "TDR": {"TDR-01": 3.0, "TDR-02": 2.0, "TDR-03": 2.5, "TDR-04": 2.5},
        "PTI": {"PTI-01": 1.5, "PTI-02": 2.0, "PTI-03": 1.0, "PTI-04": 1.5},
        "ADA": {"ADA-01": 0.5, "ADA-02": 0.5, "ADA-03": 0.5, "ADA-04": 0.5},
        "DIS": {"DIS-01": 1.0, "DIS-02": 1.0, "DIS-03": 1.0, "DIS-04": 1.0},
        "IRA": {"IRA-01": 3.0, "IRA-02": 2.5, "IRA-03": 2.5, "IRA-04": 2.0},
        "AIO": {"AIO-01": 2.0, "AIO-02": 1.5, "AIO-03": 1.0, "AIO-04": 1.5},
        "AID": {"AID-01": 0.5, "AID-02": 0.5, "AID-03": 0.5, "AID-04": 0.5},
        "SOG": {"SOG-01": 3.5, "SOG-02": 3.0, "SOG-03": 3.0, "SOG-04": 2.5}
    },
    "pillar_scores": {
        "TDR": 2.50, "PTI": 1.50, "ADA": 0.50, "DIS": 1.00,
        "IRA": 2.50, "AIO": 1.50, "AID": 0.50, "SOG": 3.00
    }
}

# ============================================================
# Helper: write to a pipeline file (capability or pricing)
# ============================================================
def upsert(file_name, entry):
    path = os.path.join(BASE_DIR, file_name)
    if not os.path.exists(path):
        print(f"[SKIP] {file_name}: file not found")
        return

    with open(path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if isinstance(data, dict) and "vendors" in data:
        vendors = data["vendors"]
        wrap = "dict"
    elif isinstance(data, list):
        vendors = data
        wrap = "list"
    else:
        print(f"[SKIP] {file_name}: unknown format")
        return

    before = len(vendors)
    vendors = [v for v in vendors if v.get("vendor", "").lower() != VENDOR_KEY]
    vendors.append(entry)

    if wrap == "dict":
        data["vendors"] = vendors
    else:
        data = vendors

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[OK] {file_name}: {before} -> {len(vendors)} vendors")


def main():
    capability_files = [
        "MDR Services Vendor 1-0 Seed.json",
        "MDR Services Vendor Capability 1-0 Seed.json",
        "MDR Services Vendor 2-0 Researched.json",
        "MDR Services Vendor 2-1 Consolidated.json",
    ]
    pricing_files = [
        "MDR Services Vendor Pricing 1-0 Seed.json",
        "MDR Services Vendor Pricing 2-0 Researched.json",
        "MDR Services Vendor Pricing 2-1 AI Enriched.json",
    ]

    print(f"=== Adding {VENDOR_NAME} to MDR capability files ===")
    for f in capability_files:
        upsert(f, oediv_capability)

    print(f"\n=== Adding {VENDOR_NAME} to MDR pricing files ===")
    for f in pricing_files:
        upsert(f, oediv_pricing)

    # Verify in the two files the app reads at runtime
    print("\n=== Verification (runtime files) ===")
    for label, fname in [
        ("Capability", "MDR Services Vendor 2-1 Consolidated.json"),
        ("Pricing",    "MDR Services Vendor Pricing 2-1 AI Enriched.json"),
    ]:
        path = os.path.join(BASE_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        match = [v for v in d["vendors"] if v.get("vendor", "").lower() == VENDOR_KEY]
        if match:
            v = match[0]
            print(f"[VERIFY] {label}: {v['vendor']} | "
                  f"HQ={v.get('headquarters','?')} | "
                  f"pillars={list(v.get('pillar_scores',{}).keys()) or 'N/A'} | "
                  f"pricing={list(v.get('pricing_dimension_scores_v2',{}).keys()) or 'N/A'}")
        else:
            print(f"[ERROR] {label}: {VENDOR_NAME} NOT found!")


if __name__ == "__main__":
    main()
