"""
Add Intezer as vendor #97 to all MDR vendor files.

Intezer Profile (from deep research):
- Founded: 2015, Tel Aviv, Israel (NYC office)
- Founders: Itai Tevet (CEO), Roy Halevi (CEO), Alon Cohen (Chairman) - Israeli intelligence backgrounds
- Funding: ~$60M total raised (Series A: $15M 2019, Series B: $45M 2022 led by Norwest)
- Employees: ~100-200
- Product: AI SOC (formerly Intezer Analyze) - Forensic AI SOC platform
- Customers: 150+ enterprises (MGM Resorts, DPD, Wyndham, Friedhelm LOH Group, Lionbridge)
- Pricing: Endpoint-based (Starter / Complete tiers)
- Certifications: SOC 2 Type II
- Microsoft AI Cloud Partner Program top-tier partner
- Integrations: 100+ security tools (CrowdStrike, SentinelOne, Microsoft Defender, Palo Alto Cortex XDR, etc.)
- Key stats: 98% verdict accuracy, <1 min median triage, <2% alerts escalated, 100% alert coverage
- Delivery model: Platform + Partner (sells direct to enterprises AND through MSSP partners)
"""

import json
import copy

# ── Build Intezer vendor entry ──────────────────────────────────────────

INTEZER = {
    "vendor": "Intezer",
    "website": "https://www.intezer.com",
    "headquarters": "Tel Aviv, Israel",
    "year_founded": 2015,
    "employee_count_range": "100-200",
    "funding_stage": "Series B",
    "total_funding": "$60M",
    "is_startup": False,
    "is_ai_first": True,
    "region": "Israel / Global",
    "mdr_service_type": "Platform MDR",
    "delivery_model": "Platform + Partner",
    "ir_focus_type": "Assistance Component",
    "target_market": "Enterprise",
    "primary_capability": "AIO",
    "description": "Intezer delivers Forensic AI SOC, an autonomous AI-powered alert triage, investigation, and response platform that combines proprietary forensic capabilities (endpoint analysis, memory scanning, reverse engineering, sandboxing) with agentic AI to investigate 100% of alerts at forensic depth. Trusted by 150+ enterprises including MGM Resorts, DPD, and Wyndham. Platform integrates with 100+ security tools and delivers 98% verdict accuracy with sub-minute median triage times. Also serves MSSPs through a multi-tenant partner platform. Microsoft AI Cloud Partner Program top-tier solutions partner. SOC 2 Type II certified.",
    "key_differentiators": "Forensic-grade AI triage combining proprietary forensic tools with agentic AI, 98% verdict accuracy with <1 minute median triage time, 100% alert coverage including low-severity alerts, endpoint-based predictable pricing, built-in forensic capabilities (memory scanning, reverse engineering, sandboxing), MSSP multi-tenant support, 150+ enterprise customers, Microsoft AI Cloud Partner, SOC 2 Type II",
    "product_names": ["Intezer AI SOC", "Intezer Forensic AI SOC", "Intezer Analyze"],
    "telemetry_sources": ["Endpoint", "Network", "Cloud", "Identity", "Email"],
    "mitre_coverage": "AI-driven alert analysis with MITRE ATT&CK context enrichment through multi-source telemetry correlation",

    # ── Capability Scores ────────────────────────────────────────────────
    # Based on public evidence from website, product pages, case studies, news
    "pillar_scores": {
        "TDR": 4.0,    # Strong: 100% alert coverage, sub-minute triage, auto-resolution, multi-source correlation
        "PTI": 2.25,   # Limited: some threat intel enrichment but not primary TI platform
        "ADA": 1.0,    # Minimal: no deception/AMTD capabilities
        "DIS": 1.0,    # Minimal: no deepfake/disinfo capabilities
        "IRA": 2.5,    # Moderate: automated containment, evidence collection, but not DFIR company
        "AIO": 4.75,   # Excellent: core value prop is AI-driven SOC automation with forensic depth
        "AID": 4.25,   # Strong: proprietary AI models + commercial LLMs, domain-specific forensic ML, continuous improvement
        "SOG": 3.25    # Good: SOC 2 Type II, 150+ customers, MSSP support, partner program, customer success
    },
    "sub_pillar_scores_current": {
        "TDR-01": 5,   # Signal Correlation & Alert Triage - core value prop: 100% alerts, multi-source, sub-minute
        "TDR-02": 4,   # Investigation & Root Cause - automated investigation chains with forensic depth
        "TDR-03": 4,   # Response Orchestration - auto-resolution, auto-remediation, SOAR integration
        "TDR-04": 3,   # SLA & MTTD/MTTR - <1 min median triage, but no published SLA guarantees
        "PTI-01": 3,   # TI Operationalization - built-in threat intel enrichment, IOC correlation
        "PTI-02": 2,   # Predictive Analytics - some ML-driven analysis but not primary focus
        "PTI-03": 2,   # Behavior Anomaly Detection - some behavioral analysis through AI models
        "PTI-04": 2,   # Dark Web Tracking - not a primary capability
        "ADA-01": 1,   # Deception - none
        "ADA-02": 1,   # AMTD - none
        "ADA-03": 1,   # Attack Surface Mgmt - not primary focus
        "ADA-04": 1,   # Counter-Adversary - not primary focus
        "DIS-01": 1,   # Deepfake Detection - none
        "DIS-02": 1,   # Identity Impersonation - none
        "DIS-03": 1,   # Narrative Detection - none
        "DIS-04": 1,   # Brand Protection - none
        "IRA-01": 3,   # Incident Scoping - automated evidence collection and scoping
        "IRA-02": 3,   # Containment Support - auto-remediation and containment through integrations
        "IRA-03": 2,   # Recovery Guidance - limited recovery guidance, not a DFIR provider
        "IRA-04": 2,   # Post-Incident Review - case management and reporting
        "AIO-01": 5,   # AI in Detection Engineering - core: AI-driven detection with forensic ML
        "AIO-02": 5,   # AI in Investigation - core: autonomous investigation chains with evidence
        "AIO-03": 5,   # AI in Response Automation - auto-resolves 96-97% of alerts
        "AIO-04": 4,   # AI Transparency - transparent triage logic, human-in-the-loop, audit trail
        "AID-01": 5,   # Domain-Specific AI - proprietary forensic ML + code similarity analysis + GenAI
        "AID-02": 4,   # AI Model Governance - continuous improvement, QA process, self-testing
        "AID-03": 4,   # AI Supply Chain - uses both proprietary and commercial AI models with controls
        "AID-04": 4,   # AI Innovation - Forensic AI SOC evolution, MSSP platform, expanding use cases
        "SOG-01": 3,   # 24/7 Coverage - AI-powered 24/7 monitoring, on-demand human analysts
        "SOG-02": 3,   # Client Engagement - customer success, Microsoft partner program, case studies
        "SOG-03": 4,   # Compliance - SOC 2 Type II, AWS/Azure hosted, encryption, data protection
        "SOG-04": 3    # Reporting Quality - case management, investigation reports, dashboards
    },
    "sub_pillar_schema_labels": {
        "TDR-01": "Signal Correlation & Alert Triage",
        "TDR-02": "Investigation & Root Cause Analysis",
        "TDR-03": "Response Orchestration & Containment",
        "TDR-04": "SLA & MTTD/MTTR Performance",
        "PTI-01": "Threat Intelligence Operationalization",
        "PTI-02": "Predictive Threat Analytics",
        "PTI-03": "Behavior-Based Anomaly Detection",
        "PTI-04": "Dark Web & Adversary Tracking",
        "ADA-01": "Deception Technology & Honeypots",
        "ADA-02": "Automated Moving Target Defense",
        "ADA-03": "Dynamic Attack Surface Management",
        "ADA-04": "Counter-Adversary Operations",
        "DIS-01": "Deepfake & Synthetic Media Detection",
        "DIS-02": "Identity Impersonation Defense",
        "DIS-03": "Narrative & Social Engineering Detection",
        "DIS-04": "Brand & Executive Protection",
        "IRA-01": "Incident Scoping & Triage",
        "IRA-02": "Containment & Isolation Support",
        "IRA-03": "Recovery & Restoration Guidance",
        "IRA-04": "Post-Incident Review & Reporting",
        "AIO-01": "AI in Detection Engineering",
        "AIO-02": "AI in Investigation & Triage",
        "AIO-03": "AI in Response Automation",
        "AIO-04": "AI Transparency & Explainability",
        "AID-01": "Domain-Specific AI/LLM Investment",
        "AID-02": "AI Model Governance & Lifecycle",
        "AID-03": "AI Supply Chain & Trustworthiness",
        "AID-04": "AI-Driven Service Innovation",
        "SOG-01": "24/7 SOC Coverage & Analyst Model",
        "SOG-02": "Client Engagement & Transparency",
        "SOG-03": "Compliance & Regulatory Alignment",
        "SOG-04": "Reporting Quality & Metrics"
    },

    # ── Derived fields ───────────────────────────────────────────────────
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
    "capability_coverage_count": 28,  # Sub-pillars with score >= 1 (excludes 0s, but all are >=1)
    "capability_analysis": "Intezer is an AI-native security operations platform from Israel that has evolved from malware analysis (Intezer Analyze, founded on code similarity/genome analysis) into a comprehensive Forensic AI SOC. The platform combines proprietary forensic capabilities (endpoint memory scanning, file reverse engineering, sandboxing, static analysis) with agentic AI and commercial LLMs to deliver autonomous alert triage at 98% accuracy. Core differentiator is the forensic depth: rather than relying solely on LLMs, Intezer uses deterministic forensic methods alongside AI, reducing hallucination risk and achieving predictable per-endpoint pricing. 150+ enterprise customers including MGM Resorts International. Strong MSSP partner program with multi-tenant support. SOC 2 Type II certified with AWS/Azure hosting. Key gap: no deception/AMTD (ADA), no disinformation/identity protection (DIS), and limited standalone IR capability (IRA). AI investment is genuinely deep with proprietary models for code analysis, forensic investigation, and threat classification. Microsoft AI Cloud Partner Program top-tier partner. Endpoint-based pricing model is notable for cost predictability versus per-alert competitors.",
    "research_status": "completed",

    # ── Evidence for key sub-pillars ───────────────────────────────────
    "sub_pillar_evidence": {
        "TDR-01": {
            "sources": [
                {"url": "https://www.intezer.com/forensic-ai-soc/", "title": "Intezer Forensic AI SOC Product Page", "excerpt": "Ingest, triage and respond to 100% of alerts, regardless of severity across EDR, Network, Cloud, Email, Identity and SIEM, for consistent, transparent and fully auditable outcomes.", "tier": "A"},
                {"url": "https://www.intezer.com/", "title": "Intezer Homepage", "excerpt": "Get trusted verdicts in minutes with 98% accuracy. Investigations are based on powerful AI agents combined with proven, forensic capabilities.", "tier": "A"}
            ]
        },
        "TDR-02": {
            "sources": [
                {"url": "https://www.intezer.com/forensic-ai-soc/", "title": "Intezer AI SOC Platform", "excerpt": "Intezer combines deep forensic capabilities, including endpoint analysis, memory scanning, reverse engineering, and built-in threat intelligence, with flexible LLMs to deliver fast, consistent, and accurate alert triage.", "tier": "A"}
            ]
        },
        "TDR-03": {
            "sources": [
                {"url": "https://www.intezer.com/pricing/", "title": "Intezer Pricing Page", "excerpt": "Auto-resolution of false positive alerts. Auto-remediation of true positive alerts. Custom response workflows.", "tier": "A"}
            ]
        },
        "AIO-01": {
            "sources": [
                {"url": "https://www.intezer.com/forensic-ai-soc/", "title": "AI SOC Platform", "excerpt": "Intezer AI SOC combines multiple AI models, both proprietary and commercial, with deterministic methods such as endpoint forensics, reverse engineering, network artifact forensics, sandboxing, static analysis and more.", "tier": "A"}
            ]
        },
        "AIO-02": {
            "sources": [
                {"url": "https://www.intezer.com/ai-soc-for-mssps/", "title": "Intezer for MSSPs", "excerpt": "Intezer automatically resolves 96-97% of alerts with high confidence. Only 3-4% require human intervention.", "tier": "A"}
            ]
        },
        "AIO-03": {
            "sources": [
                {"url": "https://www.intezer.com/forensic-ai-soc/", "title": "AI SOC Platform", "excerpt": "Contain threats in minutes, with human controlled or automated response. Auto-resolves false positives and pushes assessment and recommended actions back to endpoint tools.", "tier": "A"}
            ]
        },
        "AIO-04": {
            "sources": [
                {"url": "https://www.intezer.com/forensic-ai-soc/", "title": "AI SOC Human-in-the-Loop", "excerpt": "Intezer maintains true human-in-the-loop oversight with transparent triage logic, clear explanations, and the ability for analysts to review or override escalated alerts.", "tier": "A"}
            ]
        },
        "AID-01": {
            "sources": [
                {"url": "https://www.intezer.com/forensic-ai-soc/", "title": "AI SOC Technology", "excerpt": "Intezer AI SOC combines multiple AI models, both proprietary and commercial, with deterministic methods such as endpoint forensics, reverse engineering, network artifact forensics, sandboxing, static analysis.", "tier": "A"},
                {"url": "https://www.intezer.com/ai-soc-for-mssps/", "title": "MSSP Platform", "excerpt": "We don't just rely on generative AI. Intezer combines proprietary machine learning, deterministic methods, and generative AI to ensure precise, evidence-based threat analysis.", "tier": "A"}
            ]
        },
        "SOG-03": {
            "sources": [
                {"url": "https://www.intezer.com/security/", "title": "Intezer Security Page", "excerpt": "Intezer has successfully completed a SOC 2 Type II examination. Platforms are hosted on leading cloud infrastructure providers AWS and Azure. Encryption In-Transit (TLS 1.2), Encryption At-Rest (AES-256).", "tier": "A"}
            ]
        }
    },

    # ── Pricing ──────────────────────────────────────────────────────────
    "pricing_dimension_scores": {
        "PRC-SUB": {
            "score": 3,
            "notes": "Score 3/5 (Structured). Endpoint-based subscription pricing with Starter and Complete tiers. Clear component breakdown between tiers."
        },
        "PRC-USG": {
            "score": 2,
            "notes": "Score 2/5 (Basic). Pricing is endpoint-based, not usage-based. No per-alert or per-query charging, which is actually a stated differentiator."
        },
        "PRC-FIX": {
            "score": 2,
            "notes": "Score 2/5 (Basic). Setup and integration appear included. No complex implementation fees evident."
        },
        "PRC-SUC": {
            "score": 1,
            "notes": "Score 1/5 (Opaque). No evidence of success-fee or outcome-linked pricing components."
        },
        "PRC-COM": {
            "score": 2,
            "notes": "Score 2/5 (Basic). Two-tier model (Starter/Complete) with add-ons (managed SIEM, premium SLA). Limited composability."
        },
        "PRC-OUT": {
            "score": 2,
            "notes": "Score 2/5 (Outcome-Aware). Claims 98% accuracy and sub-minute triage in marketing, but pricing is not structurally linked to these outcomes."
        }
    },
    "pricing_model_type": "Subscription-Only",
    "outcome_maturity_rating": 2
}

# ── Compute coverage count (score >= 1) ─────────────────────────────
covered = [k for k, v in INTEZER["sub_pillar_scores_current"].items() if v >= 1]
INTEZER["capability_coverage"] = covered
INTEZER["capability_coverage_count"] = len(covered)

# ── Add to vendor files ─────────────────────────────────────────────
FILES = [
    "MDR Services Vendor 1-0 Seed.json",
    "MDR Services Vendor 2-0 Researched.json",
    "MDR Services Vendor 2-1 Consolidated.json",
    "MDR Services Vendor Capability 1-0 Seed.json",
    "MDR Services Vendor Pricing 1-0 Seed.json",
    "MDR Services Vendor Pricing 2-0 Researched.json",
    "MDR Services Vendor Pricing 2-1 AI Enriched.json",
]

import os

for fname in FILES:
    if not os.path.exists(fname):
        print(f"SKIP: {fname}")
        continue

    with open(fname, "r", encoding="utf-8") as f:
        data = json.load(f)

    vendors = data.get("vendors", [])

    # Check if already added
    if any(v.get("vendor") == "Intezer" for v in vendors):
        print(f"SKIP (already exists): {fname}")
        continue

    vendors.append(copy.deepcopy(INTEZER))
    data["vendor_count"] = len(vendors)

    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"OK: {fname} - now {len(vendors)} vendors")

# ── Final verification ──────────────────────────────────────────────
with open("MDR Services Vendor 2-1 Consolidated.json", "r", encoding="utf-8") as f:
    data = json.load(f)
v = [x for x in data["vendors"] if x["vendor"] == "Intezer"][0]
print(f"\nIntezer added successfully:")
print(f"  Vendor: {v['vendor']}")
print(f"  HQ: {v['headquarters']}")
print(f"  Type: {v['mdr_service_type']}")
print(f"  Delivery: {v['delivery_model']}")
print(f"  Primary: {v['primary_capability']}")
print(f"  Coverage: {v['capability_coverage_count']}/32")
print(f"  AI-First: {v['is_ai_first']}")
print(f"  Total vendors: {data['vendor_count']}")
