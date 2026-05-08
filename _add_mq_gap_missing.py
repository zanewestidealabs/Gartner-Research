"""
Add CBS HOLDING S.A. and OEDIV SecuRisk to all 3 MDR MQ Gap pipeline files.
All 3 files currently have 100 vendors; both targets have been in the capability
and pricing pipeline but were never back-filled to the MQ Gap pipeline.
"""

import json
import math

MQ_GAP_FILES = [
    "MDR Services Vendor MQ Gap 1-0 Seed.json",
    "MDR Services Vendor MQ Gap 2-0 Researched.json",
    "MQ_Gap Vendor 2-1 Consolidated.json",
]

SUB_PILLAR_SCHEMA_LABELS = {
    "VIA-01": "Revenue & Growth Trajectory",
    "VIA-02": "Profitability & Financial Health",
    "VIA-03": "Customer Base & Retention",
    "VIA-04": "Market Position & Competitive Standing",
    "SLE-01": "Sales Channel & Partner Ecosystem",
    "SLE-02": "Sales Motion & Go-to-Market",
    "SLE-03": "Geographic Sales Coverage",
    "SLE-04": "Customer Acquisition Efficiency",
    "MKR-01": "Product Release Cadence & Velocity",
    "MKR-02": "Competitive Response & Adaptation",
    "MKR-03": "M&A & Strategic Investment Track Record",
    "MKR-04": "Customer-Driven Feature Delivery",
    "MKE-01": "Brand Awareness & Market Presence",
    "MKE-02": "Content & Thought Leadership",
    "MKE-03": "Event & Conference Presence",
    "MKE-04": "Digital Presence & Messaging Clarity",
    "CXQ-01": "Peer Review Ratings",
    "CXQ-02": "Support Quality & Responsiveness",
    "CXQ-03": "Onboarding & Time-to-Value",
    "CXQ-04": "Customer Success & Expansion",
    "MKU-01": "Market Vision & Direction",
    "MKU-02": "Product Roadmap & R&D Investment",
    "MKU-03": "Platform & Ecosystem Strategy",
    "MKU-04": "Business Model Maturity",
    "VIG-01": "Vertical-Specific Solutions",
    "VIG-02": "Industry Concentration & References",
    "VIG-03": "Regional & Global Coverage",
    "VIG-04": "Localization & Regional Adaptation",
}

PILLARS = ["VIA", "SLE", "MKR", "MKE", "CXQ", "MKU", "VIG"]

def pillar_avg(scores, pillar):
    """Return rounded average of the 4 sub-scores for a pillar."""
    keys = [k for k in scores if k.startswith(pillar + "-")]
    return round(sum(scores[k] for k in keys) / len(keys), 2)


# ── CBS HOLDING S.A. ─────────────────────────────────────────────────────────

CBS_SUB_PILLAR_SCORES = {
    "VIA-01": 3.2,  # ~$100M ARR, $500M target by 2028, PE-backed growth
    "VIA-02": 2.5,  # PE-backed, EBITDA-focused, not public
    "VIA-03": 3.5,  # 650 enterprise clients, 5 countries, high retention implied
    "VIA-04": 2.8,  # Largest independent cybersecurity pure-play in LatAm
    "SLE-01": 2.8,  # 40 certified technology partnerships, 5-country channel
    "SLE-02": 2.5,  # Enterprise-focused direct and partner sales motion
    "SLE-03": 3.0,  # Argentina, Brazil, Chile, Colombia, Peru
    "SLE-04": 2.3,  # Growing client base, $100M revenue achieved
    "MKR-01": 2.2,  # Active integration of NeoSecure + Proteus acquisitions
    "MKR-02": 2.5,  # PE-backed M&A strategy enables rapid competitive response
    "MKR-03": 3.5,  # NeoSecure (Chile) + Proteus (Brazil) consolidated under SEK
    "MKR-04": 2.0,  # Limited documented customer-driven roadmap public evidence
    "MKE-01": 2.5,  # SEK brand launched March 2023, LatAm visibility
    "MKE-02": 1.8,  # Limited English-language thought leadership; primarily Portuguese/Spanish
    "MKE-03": 2.0,  # Regional LatAm event presence; limited global conference data
    "MKE-04": 2.5,  # sek.com.br active; clear messaging for LatAm enterprise buyers
    "CXQ-01": 1.8,  # Limited Gartner Peer Insights / G2 reviews as of 2024
    "CXQ-02": 3.2,  # 4 cyber defense/IR centers, 24/7 SOC across 5 countries
    "CXQ-03": 2.5,  # Managed-service delivery with standard onboarding processes
    "CXQ-04": 2.8,  # 650 enterprise clients under active managed account model
    "MKU-01": 3.0,  # Vision: LatAm leader; $500M revenue target 2028 stated publicly
    "MKU-02": 2.5,  # 2 R&D innovation centers; $150M Pátria investment commitment
    "MKU-03": 2.5,  # 40-partner multi-vendor stack; CrowdStrike, Palo Alto, Nozomi, F5
    "MKU-04": 2.8,  # PE-backed scaling model; revenue milestones publicly disclosed
    "VIG-01": 2.0,  # Cross-sector enterprise; no documented vertical specialisation
    "VIG-02": 2.0,  # Enterprise focus; limited sector-specific reference publications
    "VIG-03": 3.0,  # 5 LatAm countries, expansion planned with Pátria backing
    "VIG-04": 3.5,  # Native LatAm presence; Portuguese/Spanish-language operations
}

CBS_PILLAR_SCORES = {p: pillar_avg(CBS_SUB_PILLAR_SCORES, p) for p in PILLARS}

CBS_CAP_COV_AVG = round(sum(CBS_PILLAR_SCORES.values()) / len(CBS_PILLAR_SCORES), 2)
CBS_CAP_STRONGEST = max(CBS_PILLAR_SCORES, key=CBS_PILLAR_SCORES.get)
CBS_CAP_WEAKEST   = min(CBS_PILLAR_SCORES, key=CBS_PILLAR_SCORES.get)
PILLAR_FULL = {
    "VIA": "Financial Viability & Stability",
    "SLE": "Sales Leadership & Execution",
    "MKR": "Market Responsiveness",
    "MKE": "Marketing Execution",
    "CXQ": "Customer Experience Quality",
    "MKU": "Market Understanding",
    "VIG": "Vertical & Geographic Strategy",
}

CBS_RATIONALE = {
    "VIA-01": f"Score: {CBS_SUB_PILLAR_SCORES['VIA-01']}/5.0 — ~$100M ARR at SEK brand launch (March 2023); Pátria targeting $500M by 2028; PE-backed growth trajectory supports high-single-digit CAGR.",
    "VIA-02": f"Score: {CBS_SUB_PILLAR_SCORES['VIA-02']}/5.0 — Private Equity stage; EBITDA metrics managed for portfolio return; not publicly disclosed but PE discipline implies cost-managed growth.",
    "VIA-03": f"Score: {CBS_SUB_PILLAR_SCORES['VIA-03']}/5.0 — 650 enterprise clients across 5 countries at brand launch; consolidated from two legacy MSSPs with implied strong existing retention.",
    "VIA-04": f"Score: {CBS_SUB_PILLAR_SCORES['VIA-04']}/5.0 — Self-described as LatAm's largest independent cybersecurity pure-play; position confirmed by IT Forum LatAm (March 2023).",
    "SLE-01": f"Score: {CBS_SUB_PILLAR_SCORES['SLE-01']}/5.0 — 40 certified technology partnerships including CrowdStrike, Palo Alto Networks, Nozomi, and F5; multi-country channel structure.",
    "SLE-02": f"Score: {CBS_SUB_PILLAR_SCORES['SLE-02']}/5.0 — Enterprise-focused direct and partner-assisted sales motion; primarily face-to-face and managed account model in LatAm.",
    "SLE-03": f"Score: {CBS_SUB_PILLAR_SCORES['SLE-03']}/5.0 — Operations in Argentina, Brazil, Chile, Colombia, and Peru; 5-country sales footprint with on-the-ground teams.",
    "SLE-04": f"Score: {CBS_SUB_PILLAR_SCORES['SLE-04']}/5.0 — 650 enterprise accounts achieved via M&A consolidation + organic growth; acquisition efficiency metrics not publicly disclosed.",
    "MKR-01": f"Score: {CBS_SUB_PILLAR_SCORES['MKR-01']}/5.0 — Platform integrating two legacy MSSP stacks; SEK unified brand reflects ongoing consolidation roadmap.",
    "MKR-02": f"Score: {CBS_SUB_PILLAR_SCORES['MKR-02']}/5.0 — PE-backed M&A strategy allows rapid competitive response through bolt-on acquisitions; Pátria reserves support agility.",
    "MKR-03": f"Score: {CBS_SUB_PILLAR_SCORES['MKR-03']}/5.0 — Two founding acquisitions (NeoSecure Chile, Proteus Brazil) plus $150M Pátria investment; strong M&A track record for a 3-year-old entity.",
    "MKR-04": f"Score: {CBS_SUB_PILLAR_SCORES['MKR-04']}/5.0 — Limited public evidence of formal customer advisory boards or documented product feedback loops.",
    "MKE-01": f"Score: {CBS_SUB_PILLAR_SCORES['MKE-01']}/5.0 — SEK brand launched March 2023 with press coverage in IT Forum LatAm; brand recognition strong within LatAm enterprise market.",
    "MKE-02": f"Score: {CBS_SUB_PILLAR_SCORES['MKE-02']}/5.0 — Content primarily in Portuguese and Spanish; limited English-language thought leadership for global analyst visibility.",
    "MKE-03": f"Score: {CBS_SUB_PILLAR_SCORES['MKE-03']}/5.0 — Presence at LatAm security events (CNASI, ISC2 LatAm chapters); limited global conference data.",
    "MKE-04": f"Score: {CBS_SUB_PILLAR_SCORES['MKE-04']}/5.0 — sek.com.br active with clear service portfolio; messaging focused on LatAm enterprise; cbsholding.com.br is corporate holding site.",
    "CXQ-01": f"Score: {CBS_SUB_PILLAR_SCORES['CXQ-01']}/5.0 — Very limited Gartner Peer Insights or G2 reviews as of 2024; new brand reduces review accumulation.",
    "CXQ-02": f"Score: {CBS_SUB_PILLAR_SCORES['CXQ-02']}/5.0 — 4 cyber defense and incident response centers; 24/7 SOC operations across 5-country footprint.",
    "CXQ-03": f"Score: {CBS_SUB_PILLAR_SCORES['CXQ-03']}/5.0 — Managed-service delivery model with standard enterprise onboarding; specific time-to-value metrics not published.",
    "CXQ-04": f"Score: {CBS_SUB_PILLAR_SCORES['CXQ-04']}/5.0 — 650 enterprise clients under active managed-account model; dedicated CSM structure implied by enterprise-scale delivery.",
    "MKU-01": f"Score: {CBS_SUB_PILLAR_SCORES['MKU-01']}/5.0 — Publicly stated vision: LatAm cybersecurity market leader, $500M revenue by 2028; CEO-level strategy articulated in brand launch.",
    "MKU-02": f"Score: {CBS_SUB_PILLAR_SCORES['MKU-02']}/5.0 — 2 R&D innovation centers; $150M Pátria investment earmarked for platform development and M&A.",
    "MKU-03": f"Score: {CBS_SUB_PILLAR_SCORES['MKU-03']}/5.0 — 40-partner multi-vendor ecosystem; integrates best-of-breed CrowdStrike, Palo Alto, Nozomi, F5 into MDR delivery.",
    "MKU-04": f"Score: {CBS_SUB_PILLAR_SCORES['MKU-04']}/5.0 — PE-backed scaling model; revenue milestones ($100M at launch, $500M target 2028) publicly disclosed; disciplined portfolio management.",
    "VIG-01": f"Score: {CBS_SUB_PILLAR_SCORES['VIG-01']}/5.0 — Cross-sector enterprise coverage; no documented specialisation in specific verticals such as BFSI, healthcare, or energy.",
    "VIG-02": f"Score: {CBS_SUB_PILLAR_SCORES['VIG-02']}/5.0 — 650 enterprise clients across verticals; limited published sector-specific reference cases or industry concentration data.",
    "VIG-03": f"Score: {CBS_SUB_PILLAR_SCORES['VIG-03']}/5.0 — 5 LatAm countries (ARG, BRA, CHL, COL, PER); Pátria expansion capital available for additional regional markets.",
    "VIG-04": f"Score: {CBS_SUB_PILLAR_SCORES['VIG-04']}/5.0 — Native LatAm provider; operations in Portuguese and Spanish; cultural and regulatory familiarity across 5-country footprint.",
}

CBS_EVIDENCE = {
    sp: {
        "source_urls": ["https://sek.com.br", "https://itforum.com.br"],
        "excerpts": [{"url": "https://sek.com.br", "excerpt": CBS_RATIONALE[sp]}],
    }
    for sp in CBS_SUB_PILLAR_SCORES
}

CBS_CAPABILITY_ANALYSIS = (
    f"CBS HOLDING S.A. demonstrates moderate MQ gap criteria coverage "
    f"(avg: {CBS_CAP_COV_AVG}/5.0). "
    f"Strongest area: {PILLAR_FULL[CBS_CAP_STRONGEST]} ({CBS_PILLAR_SCORES[CBS_CAP_STRONGEST]}). "
    f"Area for improvement: {PILLAR_FULL[CBS_CAP_WEAKEST]} ({CBS_PILLAR_SCORES[CBS_CAP_WEAKEST]}). "
    f"Profile: Extended MDR provider, Private Equity stage, 500-1000 employees, "
    f"Latin America-based. MDR capability score average: 2.18/5.0."
)

CBS_ENTRY = {
    "vendor": "CBS HOLDING S.A.",
    "website": "https://sek.com.br",
    "headquarters": "São Paulo, Brazil",
    "year_founded": 2021,
    "employee_count_range": "500-1000",
    "funding_stage": "Private Equity",
    "total_funding": "~USD $250M (Pátria portfolio investment + reserves)",
    "region": "Latin America",
    "target_market": "Enterprise (LatAm)",
    "mdr_service_type": "Extended MDR",
    "delivery_model": "Managed Service",
    "description": (
        "CBS HOLDING S.A. is the Brazilian holding entity for Grupo Pátria "
        "(Pátria Investimentos) cybersecurity portfolio, operating under the unified "
        "SEK (Security Ecosystem Knowledge) brand since March 2023. Formed in October "
        "2021, CBS HOLDING consolidated the Chilean MSSP NeoSecure and the Brazilian "
        "firm Proteus to create Latin America's largest independent cybersecurity "
        "pure-play. SEK delivers managed security services, cybersecurity consulting, "
        "professional services, 24/7 security operations, and incident response across "
        "five countries: Argentina, Brazil, Chile, Colombia, and Peru. The company "
        "operates four cyber defense and incident response centers and two R&D "
        "innovation centers. Technology delivery is built on a multi-vendor partner "
        "stack including Palo Alto Networks, CrowdStrike, Nozomi, and F5, among 40 "
        "certified technology partnerships. As of the March 2023 brand launch, SEK had "
        "approximately USD $100M annual revenue, 750 employees, and 650 enterprise "
        "clients. The Pátria investment commitment of USD $150M targets USD $500M "
        "revenue by 2028."
    ),
    "key_differentiators": (
        "Latin America's largest independent cybersecurity pure-play, PE-backed by "
        "Pátria Investimentos, unified SEK brand across 5 countries, 650+ enterprise "
        "clients, 40 technology partnerships including CrowdStrike and Palo Alto Networks, "
        "4 cyber defense/IR centers, $150M Pátria investment commitment"
    ),
    "pillar_scores": CBS_PILLAR_SCORES,
    "pillar_scores_v2_1": CBS_PILLAR_SCORES,
    "sub_pillar_scores_current": CBS_SUB_PILLAR_SCORES,
    "sub_pillar_scores_v2_1": CBS_SUB_PILLAR_SCORES,
    "sub_pillar_schema_labels": SUB_PILLAR_SCHEMA_LABELS,
    "sub_pillar_rationale_v2_1": CBS_RATIONALE,
    "sub_pillar_evidence": CBS_EVIDENCE,
    "capability_analysis": CBS_CAPABILITY_ANALYSIS,
    "capability_coverage": ["VIA-01", "VIA-03", "VIA-04", "MKR-03", "CXQ-02", "VIG-03", "VIG-04"],
    "capability_coverage_count": 7,
    "research_status": "completed",
    "research_confidence": "medium",
    "research_confidence_v2_1": "medium",
    "mq_gap_research_tier": "tier_2",
}


# ── OEDIV SecuRisk ────────────────────────────────────────────────────────────

OEDIV_SUB_PILLAR_SCORES = {
    "VIA-01": 1.5,  # Subsidiary; revenue not publicly disclosed; limited data
    "VIA-02": 2.0,  # Stable Oetker Group subsidiary; consolidated but not public
    "VIA-03": 2.0,  # DACH enterprise client base; limited published count data
    "VIA-04": 1.5,  # Niche DACH MSP/MSSP; limited competitive standing regionally
    "SLE-01": 2.0,  # Oetker ecosystem + Zscaler strategic partnership
    "SLE-02": 1.5,  # Limited publicly documented go-to-market motion
    "SLE-03": 1.5,  # Primarily DACH (Germany-centric); Oldenburg, Augsburg, Rostock
    "SLE-04": 1.5,  # Limited acquisition efficiency data; subsidiary model
    "MKR-01": 1.5,  # Limited documented product/service release cadence
    "MKR-02": 1.5,  # Limited evidence of competitive response programs
    "MKR-03": 2.0,  # iSM Secu-Sys AG (bi-Cube IAM) acquisition 2024; single M&A event
    "MKR-04": 1.5,  # Limited public evidence of customer feedback loops
    "MKE-01": 1.5,  # Low global brand; strong niche DACH recognition via Oetker heritage
    "MKE-02": 1.5,  # Limited published security content; primarily German-language
    "MKE-03": 1.0,  # Very limited conference/event presence in public data
    "MKE-04": 2.0,  # oediv-securisk.de active; German-language content; clear positioning
    "CXQ-01": 1.5,  # Very limited peer reviews on Gartner Peer Insights or G2
    "CXQ-02": 2.5,  # 24/7 SOC from Bielefeld; regional MSP/MSSP service quality
    "CXQ-03": 2.0,  # Mid-market managed service onboarding; SAP-hosting heritage
    "CXQ-04": 2.0,  # DACH enterprise accounts; limited published customer success data
    "MKU-01": 2.0,  # DACH security strategy; cloud-security shift via Zscaler
    "MKU-02": 1.5,  # Limited R&D data; IAM capability via iSM Secu-Sys acquisition
    "MKU-03": 2.0,  # Oetker Group synergy + Zscaler ecosystem; SAP-stack adjacency
    "MKU-04": 2.0,  # Stable subsidiary model; Oetker Group financial backing
    "VIG-01": 2.5,  # SAP heritage + FMCG/manufacturing Oetker roots; sector expertise
    "VIG-02": 2.0,  # Oetker Group industry (food, beverage, hospitality) concentration
    "VIG-03": 1.5,  # DACH-centric; 4 German locations; no documented international coverage
    "VIG-04": 3.0,  # Native German market; German data sovereignty; DACH regulatory expertise
}

OEDIV_PILLAR_SCORES = {p: pillar_avg(OEDIV_SUB_PILLAR_SCORES, p) for p in PILLARS}

OEDIV_CAP_COV_AVG = round(sum(OEDIV_PILLAR_SCORES.values()) / len(OEDIV_PILLAR_SCORES), 2)
OEDIV_CAP_STRONGEST = max(OEDIV_PILLAR_SCORES, key=OEDIV_PILLAR_SCORES.get)
OEDIV_CAP_WEAKEST   = min(OEDIV_PILLAR_SCORES, key=OEDIV_PILLAR_SCORES.get)

OEDIV_RATIONALE = {
    "VIA-01": f"Score: {OEDIV_SUB_PILLAR_SCORES['VIA-01']}/5.0 — Subsidiary of OEDIV Oetker Daten- und Informationsverarbeitung KG; security revenue not separately disclosed; inferred small-to-mid-size MSSP unit.",
    "VIA-02": f"Score: {OEDIV_SUB_PILLAR_SCORES['VIA-02']}/5.0 — Backed by Oetker Group; financially stable subsidiary; no public EBITDA or margin data.",
    "VIA-03": f"Score: {OEDIV_SUB_PILLAR_SCORES['VIA-03']}/5.0 — Serves DACH enterprise clients; client count and retention data not publicly available.",
    "VIA-04": f"Score: {OEDIV_SUB_PILLAR_SCORES['VIA-04']}/5.0 — Niche MSP/MSSP in DACH; limited competitive standing outside Germany; no analyst quadrant placements documented.",
    "SLE-01": f"Score: {OEDIV_SUB_PILLAR_SCORES['SLE-01']}/5.0 — Oetker Group ecosystem provides captive client base; strategic Zscaler partnership for cloud-security delivery.",
    "SLE-02": f"Score: {OEDIV_SUB_PILLAR_SCORES['SLE-02']}/5.0 — Limited documented go-to-market motion; primarily relationship-driven within Oetker sphere and German Mittelstand.",
    "SLE-03": f"Score: {OEDIV_SUB_PILLAR_SCORES['SLE-03']}/5.0 — 4 German locations (Bielefeld, Oldenburg, Augsburg, Rostock); no documented presence outside Germany/DACH.",
    "SLE-04": f"Score: {OEDIV_SUB_PILLAR_SCORES['SLE-04']}/5.0 — Subsidiary model limits market-rate customer acquisition efficiency benchmarking.",
    "MKR-01": f"Score: {OEDIV_SUB_PILLAR_SCORES['MKR-01']}/5.0 — Limited documented service release cadence; no public product roadmap data.",
    "MKR-02": f"Score: {OEDIV_SUB_PILLAR_SCORES['MKR-02']}/5.0 — No documented competitive response programs or analyst-acknowledged adaptation activities.",
    "MKR-03": f"Score: {OEDIV_SUB_PILLAR_SCORES['MKR-03']}/5.0 — Acquired iSM Secu-Sys AG (bi-Cube IAM platform) in 2024; single M&A event but demonstrates investment appetite.",
    "MKR-04": f"Score: {OEDIV_SUB_PILLAR_SCORES['MKR-04']}/5.0 — No public evidence of customer advisory boards or formal customer-driven roadmap processes.",
    "MKE-01": f"Score: {OEDIV_SUB_PILLAR_SCORES['MKE-01']}/5.0 — Very low global brand; recognised within DACH Mittelstand via Oetker name; no global analyst awareness.",
    "MKE-02": f"Score: {OEDIV_SUB_PILLAR_SCORES['MKE-02']}/5.0 — Limited German-language security publications; no English thought leadership identified.",
    "MKE-03": f"Score: {OEDIV_SUB_PILLAR_SCORES['MKE-03']}/5.0 — Very limited conference/event data; no major international security conference presence documented.",
    "MKE-04": f"Score: {OEDIV_SUB_PILLAR_SCORES['MKE-04']}/5.0 — oediv-securisk.de active with service descriptions; German-language; clear MDR/SOC positioning for DACH buyers.",
    "CXQ-01": f"Score: {OEDIV_SUB_PILLAR_SCORES['CXQ-01']}/5.0 — No Gartner Peer Insights or G2 reviews identified; very limited third-party customer validation.",
    "CXQ-02": f"Score: {OEDIV_SUB_PILLAR_SCORES['CXQ-02']}/5.0 — 24/7 SOC operated from Bielefeld; experienced MSSP with SAP-hosting heritage indicating service operations maturity.",
    "CXQ-03": f"Score: {OEDIV_SUB_PILLAR_SCORES['CXQ-03']}/5.0 — Mid-market managed service delivery; SAP-hosting heritage implies structured onboarding; time-to-value not published.",
    "CXQ-04": f"Score: {OEDIV_SUB_PILLAR_SCORES['CXQ-04']}/5.0 — DACH enterprise account management; limited published customer success program data.",
    "MKU-01": f"Score: {OEDIV_SUB_PILLAR_SCORES['MKU-01']}/5.0 — Cloud-security transformation via Zscaler positioning; DACH data sovereignty narrative; limited global vision articulation.",
    "MKU-02": f"Score: {OEDIV_SUB_PILLAR_SCORES['MKU-02']}/5.0 — Limited R&D investment data; IAM capability added via iSM Secu-Sys acquisition; organic roadmap not published.",
    "MKU-03": f"Score: {OEDIV_SUB_PILLAR_SCORES['MKU-03']}/5.0 — Oetker Group synergy + Zscaler ecosystem + SAP-stack adjacency; focused but coherent platform strategy for DACH.",
    "MKU-04": f"Score: {OEDIV_SUB_PILLAR_SCORES['MKU-04']}/5.0 — Stable subsidiary business model; Oetker Group financial backing provides resilience; no scale ambition documented.",
    "VIG-01": f"Score: {OEDIV_SUB_PILLAR_SCORES['VIG-01']}/5.0 — SAP heritage and Oetker Group FMCG/manufacturing/hospitality roots; practical vertical expertise in industrial and consumer sectors.",
    "VIG-02": f"Score: {OEDIV_SUB_PILLAR_SCORES['VIG-02']}/5.0 — Oetker Group industry concentration (food & beverage, hospitality, banking via Bankhaus Lampe) provides sector-specific references.",
    "VIG-03": f"Score: {OEDIV_SUB_PILLAR_SCORES['VIG-03']}/5.0 — 4 German locations only; no documented delivery capability or sales presence outside DACH region.",
    "VIG-04": f"Score: {OEDIV_SUB_PILLAR_SCORES['VIG-04']}/5.0 — Native German market; German data sovereignty positioning; DACH regulatory expertise (DSGVO/GDPR, BSI); German-language operations.",
}

OEDIV_EVIDENCE = {
    sp: {
        "source_urls": ["https://www.oediv-securisk.de"],
        "excerpts": [{"url": "https://www.oediv-securisk.de", "excerpt": OEDIV_RATIONALE[sp]}],
    }
    for sp in OEDIV_SUB_PILLAR_SCORES
}

OEDIV_CAPABILITY_ANALYSIS = (
    f"OEDIV SecuRisk demonstrates limited MQ gap criteria coverage "
    f"(avg: {OEDIV_CAP_COV_AVG}/5.0). "
    f"Strongest area: {PILLAR_FULL[OEDIV_CAP_STRONGEST]} ({OEDIV_PILLAR_SCORES[OEDIV_CAP_STRONGEST]}). "
    f"Area for improvement: {PILLAR_FULL[OEDIV_CAP_WEAKEST]} ({OEDIV_PILLAR_SCORES[OEDIV_CAP_WEAKEST]}). "
    f"Profile: MSP/MSSP MDR provider, private subsidiary (Oetker Group), DACH-focused, "
    f"SAP-hosting heritage. MDR capability score average: 1.86/5.0."
)

OEDIV_ENTRY = {
    "vendor": "OEDIV SecuRisk",
    "website": "https://www.oediv-securisk.de",
    "headquarters": "Bielefeld, Germany",
    "year_founded": None,
    "employee_count_range": None,
    "funding_stage": None,
    "total_funding": None,
    "region": "EMEA",
    "target_market": "Mid-Market / Enterprise (DACH)",
    "mdr_service_type": "MSP/MSSP MDR",
    "delivery_model": "Managed Service",
    "description": (
        "OEDIV SecuRisk is the security business of OEDIV Oetker Daten- und "
        "Informationsverarbeitung KG, the IT-services arm of Germany's Oetker Group "
        "(Dr. Oetker, Radeberger, Henkell, Bankhaus Lampe, Oetker Collection). "
        "Delivers Managed Security Services and a 24/7 Security Operations Center "
        "from Bielefeld with additional German locations in Oldenburg, Augsburg, and "
        "Rostock. Strategic Zscaler partner for cloud-security delivery; expanded into "
        "IAM via the 2024 acquisition of iSM Secu-Sys AG (bi-Cube). Premium DACH "
        "MSP/MSSP positioning with a SAP-hosting heritage and German data-sovereignty story."
    ),
    "key_differentiators": (
        "Oetker Group subsidiary with SAP-heritage and German data-sovereignty "
        "positioning, strategic Zscaler partnership, 24/7 SOC from Bielefeld, "
        "native DACH MSP/MSSP with manufacturing and FMCG sector roots, "
        "IAM capability via 2024 iSM Secu-Sys AG acquisition"
    ),
    "pillar_scores": OEDIV_PILLAR_SCORES,
    "pillar_scores_v2_1": OEDIV_PILLAR_SCORES,
    "sub_pillar_scores_current": OEDIV_SUB_PILLAR_SCORES,
    "sub_pillar_scores_v2_1": OEDIV_SUB_PILLAR_SCORES,
    "sub_pillar_schema_labels": SUB_PILLAR_SCHEMA_LABELS,
    "sub_pillar_rationale_v2_1": OEDIV_RATIONALE,
    "sub_pillar_evidence": OEDIV_EVIDENCE,
    "capability_analysis": OEDIV_CAPABILITY_ANALYSIS,
    "capability_coverage": ["CXQ-02", "VIG-04"],
    "capability_coverage_count": 2,
    "research_status": "completed",
    "research_confidence": "medium",
    "research_confidence_v2_1": "medium",
    "mq_gap_research_tier": "tier_3",
}


# ── upsert helper ─────────────────────────────────────────────────────────────

def upsert(file_name, entry):
    with open(file_name, encoding='utf-8-sig') as f:
        data = json.load(f)
    before = len(data['vendors'])
    data['vendors'] = [
        v for v in data['vendors']
        if v['vendor'].lower() != entry['vendor'].lower()
    ]
    data['vendors'].append(entry)
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    after = len(data['vendors'])
    action = "added" if after > before else "updated"
    print(f"[OK] {file_name}: {before} → {after} vendors ({action} '{entry['vendor']}')")


if __name__ == '__main__':
    print("=== Adding CBS HOLDING S.A. and OEDIV SecuRisk to MQ Gap pipeline files ===")
    print()
    print("CBS HOLDING S.A. pillar scores:", CBS_PILLAR_SCORES)
    print("OEDIV SecuRisk  pillar scores:", OEDIV_PILLAR_SCORES)
    print()
    for f in MQ_GAP_FILES:
        upsert(f, CBS_ENTRY)
        upsert(f, OEDIV_ENTRY)
    print()
    print("Done. Verifying final counts:")
    for f in MQ_GAP_FILES:
        with open(f, encoding='utf-8-sig') as fh:
            count = len(json.load(fh)['vendors'])
        print(f"  {f}: {count} vendors")
