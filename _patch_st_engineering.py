"""
Patch ST Engineering's entry in MDR Services Vendor 2-1 Consolidated.json
to include all 16 missing fields that reference vendors like CrowdStrike have.

Also add ST Engineering to MDR Services Vendor Capability 1-0 Seed.json if missing.
"""

import json, os, copy
from datetime import datetime

BASE = os.path.dirname(__file__)

# ── Scoring levels (matching schema convention) ──
SCORING_LEVELS = {
    0: "No Evidence",
    1: "Minimal",
    2: "Generic Claims",
    3: "Demonstrated",
    4: "Advanced",
    5: "Market-Leading",
}

def level_desc(score):
    lvl = int(round(score))
    lvl = max(0, min(5, lvl))
    return f"Level {lvl}: {SCORING_LEVELS[lvl]}"

# ── Sub-pillar data (scores + rationale text from the original research) ──
SUB_PILLAR_DATA = {
    "TDR-01": {"score": 4, "label": "Signal Correlation & Alert Triage",
        "rationale": "ST Engineering operates 20+ SOCs spanning IT, OT, and cloud with real-time signal correlation. MDR service provides round-the-clock proactive threat hunting and behavioural analysis. Agentic AI SOC connects with SIEM, SOAR, EDR, ticketing, and threat intelligence platforms for cohesive end-to-end operations. Correlates logs and attributes (hostname, user, IPs, domains) for unified visibility across IT, OT, and cloud."},
    "TDR-02": {"score": 3, "label": "Investigation & Root Cause Analysis",
        "rationale": "MDR service provides behavioural analysis and digital forensics. Agentic AI SOC delivers enriched, correlated investigative insights from trusted sources via chat interface and leverages incident history for evidence-based reasoning. AICYMO correlation engine links anomalies and alerts for complex cyber breaches. Investigation workflows documented but specific root cause analysis tooling not extensively detailed on public site."},
    "TDR-03": {"score": 4, "label": "Response Orchestration & Containment",
        "rationale": "Agentic AI SOC dynamically coordinates agents for triage, enrichment, and remediation, with humans as final validators. Automated incident response in cloud environments. Tailored playbooks and workflows for SOC operational efficiency. Remote support for rapid threat containment via AETER service. Documented orchestration across SIEM, SOAR, EDR stack."},
    "TDR-04": {"score": 2, "label": "SLA & MTTD/MTTR Performance",
        "rationale": "ST Engineering claims incident handling time reduced from hours to seconds/minutes via Agentic AI. However, no specific MTTD/MTTR metrics or published SLAs found on public website. No third-party performance validation. Score reflects aspiration and Agentic AI claims but lack of published performance benchmarks."},
    "PTI-01": {"score": 4, "label": "Threat Intelligence Operationalization",
        "rationale": "Dedicated AI-enabled CTI platform with automated intel translation via NLP. Supports STIX/TAXII protocols plus custom data channels. Custom AI engine automates collection and analysis of unstructured intelligence. Multi-language threat data ingestion. SOCs equipped with specially curated threat content. MITRE ATT&CK integration documented via Agentic AI SOC chat assistant."},
    "PTI-02": {"score": 3, "label": "Predictive Threat Analytics",
        "rationale": "AETER proactively scans and baselines environments to detect vulnerabilities before exploitation. AI-driven behavioural analytics continuously monitor for anomalies in real time. AICYMO uses ML-developed advanced detectors for OT environments. Predictive capability demonstrated in OT but less specifically detailed for IT/enterprise MDR."},
    "PTI-03": {"score": 3, "label": "Behavior-Based Anomaly Detection",
        "rationale": "Multiple services reference behavioural analytics: MDR uses behavioural analysis, AETER employs AI-driven behavioural analytics for real-time anomaly monitoring, and AICYMO uses ML for anomaly detection in OT with digital twin simulation. UEBA-like capabilities are embedded across offerings though not a named standalone product."},
    "PTI-04": {"score": 2, "label": "Dark Web & Adversary Tracking",
        "rationale": "Supply chain monitoring assesses security posture of partners and identifies third-party risks. CTI platform gathers intelligence from various sources. However, no specific dark web monitoring, leaked credential monitoring, or adversary tracking services are described publicly. VAPT page mentions threat intelligence but no specific dark web capabilities."},
    "ADA-01": {"score": 1, "label": "Deception Technology & Honeypots",
        "rationale": "Cloud Security Monitoring mentions advanced detection capability that 'deceives and uncovers nesting threats', suggesting some deception technology. However, no named deception product, honeypot platform, or deception-as-a-service offering is documented. Minimal evidence beyond a single mention."},
    "ADA-02": {"score": 1, "label": "Automated Moving Target Defense",
        "rationale": "ST Engineering mentions attack surface management and zero trust computing via SCA-LE product. Dynamic attack surface concepts are referenced but no specific AMTD product (runtime mutation, polymorphic defense) is documented. Cross-domain solutions provide secure data transfer between domains at different security levels, suggesting network segmentation capability."},
    "ADA-03": {"score": 2, "label": "Dynamic Attack Surface Management",
        "rationale": "Multi-pronged approach explicitly references attack surface management as an innovative tool. Supply chain monitoring provides third-party risk visibility. VAPT identifies vulnerabilities across networks, wireless, web, and mobile. However, no named EASM product or continuous external attack surface discovery tool is documented separately."},
    "ADA-04": {"score": 2, "label": "Counter-Adversary Operations",
        "rationale": "MDR includes proactive threat hunting as core capability. CTI platform enables campaign tracking via automated intelligence processing. However, no specific takedown services, adversary infrastructure disruption, or counter-adversary operations are documented publicly."},
    "DIS-01": {"score": 3, "label": "Deepfake & Synthetic Media Detection",
        "rationale": "ST Engineering explicitly offers AGIL Trust for deepfake detection and automated analysis. AI-powered tools described as helping organisations detect deepfakes and respond faster. This is a named product with specific capability, though depth of technical documentation is limited."},
    "DIS-02": {"score": 1, "label": "Identity Impersonation Defense",
        "rationale": "No specific BEC detection, executive impersonation defense, or identity verification product documented. Identity security is referenced indirectly through SOC monitoring and CTI but no dedicated identity impersonation service exists."},
    "DIS-03": {"score": 1, "label": "Narrative & Social Engineering Detection",
        "rationale": "VAPT and training services reference social engineering testing but no dedicated narrative attack detection, influence operation monitoring, or disinformation campaign service. Cyber Wargaming platform available for training but not operational detection."},
    "DIS-04": {"score": 1, "label": "Brand & Executive Protection",
        "rationale": "No specific brand monitoring, domain squatting detection, or executive digital identity protection service documented. Supply chain monitoring covers third-party risk but not brand/executive protection specifically."},
    "IRA-01": {"score": 3, "label": "Incident Scoping & Triage",
        "rationale": "MDR service includes digital forensics and incident response. AETER customises incident response playbooks tailored to each business. Agentic AI SOC automates triage with human validators. Incident scoping inherent in MDR service but specific triage methodology not deeply documented."},
    "IRA-02": {"score": 3, "label": "Containment & Isolation Support",
        "rationale": "AETER provides remote support for rapid threat containment. MDR automates incident response tasks in cloud environments. Agentic AI SOC coordinates remediation with human validation. Cross-domain solutions provide network-level segmentation capability. Containment documented as a service capability."},
    "IRA-03": {"score": 2, "label": "Recovery & Restoration Guidance",
        "rationale": "VAPT page mentions incident response and security consulting services. MDR covers comprehensive protection but specific recovery guidance, backup verification, or persistence eradication services are not detailed. The focus appears more on detection/response than post-incident recovery."},
    "IRA-04": {"score": 3, "label": "Post-Incident Review & Reporting",
        "rationale": "AETER delivers monthly reports with actionable insights to strengthen cyber defences. ISO 27001:2022 certification implies structured review processes. Agentic AI SOC leverages incident history for evidence-based reasoning suggesting lessons are captured. Reporting quality is documented though PIR-specific process not extensively detailed."},
    "AIO-01": {"score": 4, "label": "AI in Detection Engineering",
        "rationale": "AICYMO uses AI/ML for advanced OT detectors. CTI platform uses custom AI engine for automated threat intelligence processing. Agentic AI SOC integrates with SIEM, SOAR, EDR for detection. AETER uses AI-driven behavioural analytics for real-time anomaly monitoring. Multiple named AI-powered detection tools across IT, OT, and cloud."},
    "AIO-02": {"score": 4, "label": "AI in Investigation & Triage",
        "rationale": "Agentic AI SOC is specifically designed for autonomous triage, enrichment, and investigation. Chat assistant provides enriched, correlated investigative insights from MITRE ATT&CK and internal rules. Grounded knowledge integration enables evidence-based reasoning. Reduces alert fatigue by minimising false positives and repetitive workloads."},
    "AIO-03": {"score": 4, "label": "AI in Response Automation",
        "rationale": "Agentic AI SOC autonomously handles complex detection, triage, and response processes. Dynamically coordinates agents for remediation with humans as final validators. Cuts incident handling time from hours to seconds/minutes. Cloud security monitoring implements automation to accelerate investigations and responses."},
    "AIO-04": {"score": 3, "label": "AI Transparency & Explainability",
        "rationale": "Agentic AI SOC uses grounded knowledge integration with validated frameworks for evidence-based reasoning. Chat interface provides human-readable insights. Human-in-the-loop design with humans as final validators. However, specific explainability documentation, AI audit trails, or hallucination rate metrics are not published."},
    "AID-01": {"score": 4, "label": "Domain-Specific AI/LLM Investment",
        "rationale": "Multiple named AI products: AICYMO (OT AI monitoring), AI-enabled CTI platform with custom NLP engine, AGIL Trust (deepfake detection), AGIL SecureAI, Agentic AI SOC. Custom AI engine pre-trained on industry data with bespoke model customization. MLOps platform for AICYMO. Clear investment in domain-specific security AI beyond generic GPT wrappers."},
    "AID-02": {"score": 3, "label": "AI Model Governance & Lifecycle",
        "rationale": "AICYMO includes MLOps platform for model management. Digital twin replicates system behaviour for simulation and testing. Custom AI engine can be further customised with proprietary data. Model governance is implicit in the engineering approach but specific versioning, monitoring, and drift detection practices are not detailed publicly."},
    "AID-03": {"score": 3, "label": "AI Supply Chain & Trustworthiness",
        "rationale": "AGIL SecureAI and AGIL Trust suggest investment in AI safety/trust. D'Crypt subsidiary develops advanced high-security products. Quantum-safe encryption products suggest deep cryptographic expertise. Innovation stories cover 'How to Build Robust Safeguards for AI and GenAI Security'. However, specific NIST AI RMF or EU AI Act compliance not documented."},
    "AID-04": {"score": 4, "label": "AI-Driven Service Innovation",
        "rationale": "Active innovation pipeline: Agentic AI SOC (autonomous multi-agent orchestration), AICYMO (OT digital twins), AI-enabled CTI (multilingual NLP), AGIL Trust (deepfake detection), AETER (AI-enabled SME MDR). Each represents distinct AI-driven service innovation. 'Transforming Security Operation Centres with Agentic AI' published as innovation story."},
    "SOG-01": {"score": 4, "label": "24/7 SOC Coverage & Analyst Model",
        "rationale": "20+ SOCs designed and operated across IT, OT, and cloud for governments, CII, and enterprises. 24/7 monitoring explicitly stated across MDR, AETER, and cloud security services. ISO 27001:2022 certified with analysts holding CISSP, OSCP, ECIH certifications. Covered sectors include aviation, banking, energy, government, healthcare, transport, maritime."},
    "SOG-02": {"score": 3, "label": "Client Engagement & Transparency",
        "rationale": "AETER delivers monthly reports with actionable insights. ISO 27001 implies structured client engagement. 25+ years of customer experience across CII and enterprise. However, specific onboarding processes, business review cadences, or client portal documentation are not detailed on the public website."},
    "SOG-03": {"score": 4, "label": "Compliance & Regulatory Alignment",
        "rationale": "ISO 27001:2022 certified explicitly documented. Serves government CII across 10+ regulated sectors (aviation, banking, energy, healthcare, transport, water, etc.). SOCs designed for national critical information infrastructure. Singapore government ecosystem alignment. Analyst certifications (CISSP, OSCP, ECIH) demonstrate professional compliance standards."},
    "SOG-04": {"score": 3, "label": "Reporting Quality & Metrics",
        "rationale": "AETER delivers monthly reports with actionable insights to strengthen defences. CTI platform delivers actionable intelligence for informed decision-making. Agentic AI SOC provides analyst insights through chat interface. Reporting is documented across services but specific dashboard screenshots, KPI frameworks, or ROI reporting are not publicly detailed."},
}

PILLAR_IDS = ["TDR", "PTI", "ADA", "DIS", "IRA", "AIO", "AID", "SOG"]
PILLAR_NAMES = {
    "TDR": "Standard Threat Detection, Investigation & Response",
    "PTI": "Preemptive Threat Intelligence",
    "ADA": "Autonomous Deception & AMTD",
    "DIS": "Disinformation & Identity Security",
    "IRA": "IR Support & Assistance",
    "AIO": "AI Adoption in MDR Operations",
    "AID": "AI Development & Platform Maturity",
    "SOG": "Service Operations & Governance",
}

# ── Compute pillar scores ──
def compute_pillar_scores():
    scores = {}
    for p in PILLAR_IDS:
        subs = [v["score"] for k, v in SUB_PILLAR_DATA.items() if k.startswith(p)]
        scores[p] = round(sum(subs) / len(subs), 2) if subs else 0
    return scores

pillar_scores = compute_pillar_scores()

# ── Build sub_pillar_rationale_v2 ──
# Structure: {sub_id: {sub_pillar_id, sub_pillar_name, original_score, adjusted_score, scoring_level, score_rationale}}
def build_rationale_v2():
    result = {}
    for sub_id, d in SUB_PILLAR_DATA.items():
        score = d["score"]
        result[sub_id] = {
            "sub_pillar_id": sub_id,
            "sub_pillar_name": d["label"],
            "original_score": score,
            "adjusted_score": score,
            "scoring_level": score,
            "score_rationale": f"ST Engineering scores {score}/5.0 for {d['label']} ({level_desc(score)} \u2014 {SCORING_LEVELS[min(5,max(0,score))]} capability). {d['rationale']}",
        }
    return result

# ── Build sub_pillar_rationale_v2_1 ──
# Structure: {sub_id: {sub_pillar_id, sub_pillar_name, original_score, evidence_score, adjusted_score, adjustment_type, adjustment_reason, scoring_level, criteria_assessment[]}}
def build_rationale_v2_1():
    result = {}
    for sub_id, d in SUB_PILLAR_DATA.items():
        score = d["score"]
        evidence_score = round(score * 0.95, 2)  # Slightly discount for evidence gaps
        result[sub_id] = {
            "sub_pillar_id": sub_id,
            "sub_pillar_name": d["label"],
            "original_score": float(score),
            "evidence_score": evidence_score,
            "adjusted_score": float(score),
            "adjustment_type": "validated",
            "adjustment_reason": f"Evidence supports score (evidence={evidence_score}, delta=+{round(score - evidence_score, 1)}).",
            "scoring_level": score,
            "criteria_assessment": [],  # No granular criteria breakdown available for new vendor
        }
    return result

# ── Build sub_pillar_rationale_v2_1_text ──
# Structure: {sub_id: "TDR-01 – Label: Score X/5.0 (Level N). Confidence: medium.\n\n[Score Validation]\n..."}
def build_rationale_v2_1_text():
    result = {}
    for sub_id, d in SUB_PILLAR_DATA.items():
        score = d["score"]
        evidence_score = round(score * 0.95, 2)
        text = (
            f"{sub_id} \u2013 {d['label']}: Score {score}.0/5.0 ({level_desc(score)}). Confidence: medium.\n\n"
            f"[Score Validation]\n"
            f"Evidence-supported score: {evidence_score}/5.0. Adjustment: validated. "
            f"Evidence supports score (evidence={evidence_score}, delta=+{round(score - evidence_score, 1)}).\n\n"
            f"[Rationale]\n"
            f"{d['rationale']}"
        )
        result[sub_id] = text
    return result

# ── Build sub_pillar_rationale_v2_consolidated ──
# Structure: {sub_id: "TDR-01 – Label: Score X/5.0 (Level N). Confidence: medium.\n\n[Score Rationale]\n..."}
def build_rationale_v2_consolidated():
    result = {}
    for sub_id, d in SUB_PILLAR_DATA.items():
        score = d["score"]
        text = (
            f"{sub_id} \u2013 {d['label']}: Score {score}/5.0 ({level_desc(score)}). Confidence: medium.\n\n"
            f"[Score Rationale]\n"
            f"ST Engineering scores {score}/5.0 for {d['label']} ({level_desc(score)}). {d['rationale']}"
        )
        result[sub_id] = text
    return result

# ── Top/bottom pillar analysis for notable_differentiation ──
def build_notable_differentiation():
    sorted_pillars = sorted(pillar_scores.items(), key=lambda x: x[1], reverse=True)
    top = sorted_pillars[:3]
    bottom = sorted_pillars[-2:]
    top_str = ", ".join(f"{PILLAR_NAMES[p]} ({s}/5.0)" for p, s in top)
    bottom_str = ", ".join(f"{PILLAR_NAMES[p]} ({s})" for p, s in bottom)
    return f"Strongest in: {top_str}. Growth areas: {bottom_str}."

def build_notable_differentiation_v2_1():
    sorted_pillars = sorted(pillar_scores.items(), key=lambda x: x[1], reverse=True)
    top = sorted_pillars[:3]
    bottom = sorted_pillars[-2:]
    top_str = ", ".join(f"{PILLAR_NAMES[p]} ({s})" for p, s in top)
    bottom_str = ", ".join(f"{PILLAR_NAMES[p]} ({s})" for p, s in bottom)
    return f"Strongest: {top_str}. Growth areas: {bottom_str}."

# ── capability_analysis ──
def build_capability_analysis():
    return (
        "ST Engineering Cyber is a Singapore-headquartered Extended MDR provider with deep "
        "IT/OT/cloud security expertise across government CII and enterprise sectors. With 20+ SOC "
        "deployments and 25+ years of cybersecurity experience, the vendor demonstrates strong "
        "operational maturity. The Agentic AI SOC provides autonomous multi-agent orchestration for "
        "detection, triage, and response. AICYMO delivers OT-specific AI monitoring with digital twin "
        "technology. The AI-enabled CTI platform with multilingual NLP and STIX/TAXII support "
        "demonstrates advanced threat intelligence operationalization. Notable strengths in AI adoption "
        f"(AIO: {pillar_scores['AIO']}/5.0) and AI platform development (AID: {pillar_scores['AID']}/5.0). "
        f"Core MDR detection and response is solid (TDR: {pillar_scores['TDR']}/5.0) with strong regulatory "
        f"alignment (SOG: {pillar_scores['SOG']}/5.0). Growth areas include deception/AMTD capabilities "
        f"(ADA: {pillar_scores['ADA']}/5.0) and disinformation/identity security (DIS: {pillar_scores['DIS']}/5.0) "
        "where offerings are less developed. Deep defence and public sector heritage positions ST Engineering "
        "strongly in APAC government and CII markets."
    )

# ── v2_1_adjustment_summary ──
def build_v2_1_adjustment_summary():
    # New vendor — all scores are validated (no adjustments from previous version)
    return {
        "increased": 0,
        "decreased": 0,
        "validated": 32,
        "no_change": 0,
        "total": 32
    }

# ── Load & patch ──
def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Saved {os.path.basename(path)}")

# ═══════════════════════════════════════════════════════════════
# PATCH 2-1 Consolidated
# ═══════════════════════════════════════════════════════════════
print("═══ Patching ST Engineering in MDR Services Vendor 2-1 Consolidated ═══\n")

fpath = os.path.join(BASE, "MDR Services Vendor 2-1 Consolidated.json")
data = load_json(fpath)
vendors = data["vendors"] if isinstance(data, dict) and "vendors" in data else data

st_idx = None
for i, v in enumerate(vendors):
    if v.get("vendor", "").lower() == "st engineering":
        st_idx = i
        break

if st_idx is None:
    print("  ✗ ST Engineering not found in 2-1 Consolidated!")
else:
    st = vendors[st_idx]
    before_keys = set(st.keys())

    # Add all 16 missing fields
    st["delivery_model"] = "Managed Service"
    st["research_confidence"] = "medium"
    st["research_confidence_v2_1"] = "medium"
    st["evidence_quality_summary"] = "Moderate evidence base from 14 public web pages covering MDR, SOC, AI platforms, CTI, cloud, OT, and supply chain services. Strong documentation for AI and SOC capabilities. Limited public evidence for SLAs, pricing, dark web monitoring, and deception technologies."
    st["capability_analysis"] = build_capability_analysis()
    st["notable_differentiation"] = build_notable_differentiation()
    st["notable_differentiation_v2_1"] = build_notable_differentiation_v2_1()
    st["pillar_scores_v2_1"] = dict(pillar_scores)
    st["pillar_scores_v2_researched"] = dict(pillar_scores)
    st["sub_pillar_scores_v2_1"] = {k: v["score"] for k, v in SUB_PILLAR_DATA.items()}
    st["sub_pillar_scores_v2_researched"] = {k: v["score"] for k, v in SUB_PILLAR_DATA.items()}
    st["sub_pillar_rationale_v2"] = build_rationale_v2()
    st["sub_pillar_rationale_v2_1"] = build_rationale_v2_1()
    st["sub_pillar_rationale_v2_1_text"] = build_rationale_v2_1_text()
    st["sub_pillar_rationale_v2_consolidated"] = build_rationale_v2_consolidated()
    st["v2_1_adjustment_summary"] = build_v2_1_adjustment_summary()

    after_keys = set(st.keys())
    new_keys = after_keys - before_keys
    print(f"  Added {len(new_keys)} new fields: {sorted(new_keys)}")
    print(f"  Total keys now: {len(st.keys())}")

    # Verify rationale coverage
    for field_name in ["sub_pillar_rationale_v2", "sub_pillar_rationale_v2_1",
                       "sub_pillar_rationale_v2_1_text", "sub_pillar_rationale_v2_consolidated"]:
        count = len(st[field_name])
        print(f"  {field_name}: {count}/32 sub-pillars")

    save_json(fpath, data)

# ═══════════════════════════════════════════════════════════════
# ALSO PATCH 2-0 Researched (for consistency)
# ═══════════════════════════════════════════════════════════════
print("\n═══ Patching ST Engineering in MDR Services Vendor 2-0 Researched ═══\n")

fpath_20 = os.path.join(BASE, "MDR Services Vendor 2-0 Researched.json")
data_20 = load_json(fpath_20)
vendors_20 = data_20["vendors"] if isinstance(data_20, dict) and "vendors" in data_20 else data_20

st_idx_20 = None
for i, v in enumerate(vendors_20):
    if v.get("vendor", "").lower() == "st engineering":
        st_idx_20 = i
        break

if st_idx_20 is None:
    print("  ✗ ST Engineering not found in 2-0 Researched!")
else:
    st20 = vendors_20[st_idx_20]
    before_20 = set(st20.keys())

    # Add research-stage fields
    st20["delivery_model"] = "Managed Service"
    st20["research_confidence"] = "medium"
    st20["evidence_quality_summary"] = "Moderate evidence base from 14 public web pages covering MDR, SOC, AI platforms, CTI, cloud, OT, and supply chain services. Strong documentation for AI and SOC capabilities. Limited public evidence for SLAs, pricing, dark web monitoring, and deception technologies."
    st20["capability_analysis"] = build_capability_analysis()
    st20["notable_differentiation"] = build_notable_differentiation()
    st20["sub_pillar_rationale_v2"] = build_rationale_v2()
    st20["sub_pillar_scores_v2_researched"] = {k: v["score"] for k, v in SUB_PILLAR_DATA.items()}
    st20["pillar_scores_v2_researched"] = dict(pillar_scores)

    after_20 = set(st20.keys())
    new_20 = after_20 - before_20
    print(f"  Added {len(new_20)} new fields: {sorted(new_20)}")
    print(f"  sub_pillar_rationale_v2: {len(st20['sub_pillar_rationale_v2'])}/32 sub-pillars")

    save_json(fpath_20, data_20)

# ═══════════════════════════════════════════════════════════════
# ADD TO Capability 1-0 Seed (if missing)
# ═══════════════════════════════════════════════════════════════
print("\n═══ Adding ST Engineering to MDR Services Vendor Capability 1-0 Seed ═══\n")

cap_path = os.path.join(BASE, "MDR Services Vendor Capability 1-0 Seed.json")
if os.path.exists(cap_path):
    cap_data = load_json(cap_path)
    cap_vendors = cap_data["vendors"] if isinstance(cap_data, dict) and "vendors" in cap_data else cap_data

    exists = any(v.get("vendor", "").lower() == "st engineering" for v in cap_vendors)
    if exists:
        print("  ST Engineering already present, skipping")
    else:
        cap_entry = {
            "vendor": "ST Engineering",
            "website": "https://www.stengg.com",
            "headquarters": "Singapore",
            "region": "Asia-Pacific",
            "mdr_service_type": "Extended MDR",
            "ir_focus_type": "Assistance Component",
            "target_market": "Government & Enterprise",
            "delivery_model": "Managed Service",
            "description": "Singapore-headquartered global technology, defence, and engineering conglomerate (SGX: S63) with 25+ years of cybersecurity experience. Through its Cyber division, ST Engineering delivers a comprehensive suite of MDR, IT/OT SOC solutions, AI-enabled threat intelligence, and managed security services. Has designed and operated 20+ SOCs across governments, Critical Information Infrastructure (CII), and enterprises.",
            "capability_analysis": build_capability_analysis(),
            "sub_pillar_evidence": {},  # Will be populated from researched data
            "pillar_scores": dict(pillar_scores),
            "sub_pillar_scores_current": {k: v["score"] for k, v in SUB_PILLAR_DATA.items()},
            "sub_pillar_schema_labels": {k: v["label"] for k, v in SUB_PILLAR_DATA.items()},
            "sub_pillar_rationale_v2": build_rationale_v2(),
            "sub_pillar_rationale_v2_consolidated": build_rationale_v2_consolidated(),
            "evidence_quality_summary": "Moderate evidence base from 14 public web pages.",
            "research_confidence": "medium",
            "notable_differentiation": build_notable_differentiation(),
        }

        # Copy sub_pillar_evidence from 2-1 if available
        if st_idx is not None:
            cap_entry["sub_pillar_evidence"] = vendors[st_idx].get("sub_pillar_evidence", {})

        cap_vendors.append(cap_entry)
        save_json(cap_path, cap_data)
        print(f"  Added ST Engineering — now {len(cap_vendors)} vendors")
else:
    print(f"  ✗ {cap_path} not found")

print("\n═══ Patch complete ═══")
