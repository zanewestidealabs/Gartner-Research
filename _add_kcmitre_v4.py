"""
Add v4 of the Kill Chain + MITRE ATT&CK market insight report to precyber_market_insight_reports.json.
Changes from v3:
  1. Summary condensed to <300 characters (was 737)
  2. Analysis sections restructured around findings→recommendations mappings
  3. Clearer cross-references between findings and recommendations
"""
import json

with open("precyber_market_insight_reports.json", "r", encoding="utf-8") as f:
    data = json.load(f)

v4 = {
    "id": "cpo-killchain-mitre-v4",
    "label": "CPO / Threat Defense: Kill Chain + ATT&CK Dual-Framework (v4 - Findings-Aligned)",
    "title": "Market Insight: Preemptive Cybersecurity Through the Kill Chain and MITRE ATT&CK Dual-Framework Lens",

    # Summary: <300 characters, preserving all meaning
    "summary": "Four defensive pillars map to kill chain phases and ATT\u0026CK tactics. ~68% of vendor capability clusters in reactive phases. Adversary management is the critical bottleneck. Services maturity is the cross-cutting enabler separating effective vendors from technology-only providers.",

    "spa": "By 2028, ~35% of enterprise preemptive cybersecurity evaluations will use adversary lifecycle phase coverage as a primary vendor selection criterion, up from <10% today. Services maturity will be the decisive tiebreaker as buyers recognise that technology without operational depth delivers inferior outcomes.",

    "findings": [
        {
            "header": "F1: Four defensive pillars map to adversary lifecycle phases; services maturity is the cross-cutting enabler.",
            "body": "Exposure management \u2192 Kill Chain Phase 1 / ATT\u0026CK TA0043, TA0007. Adversary management \u2192 Phases 1-2 / TA0042, TA0005, TA0006. Posture and policy management \u2192 Phases 2-3 / TA0001, TA0004. Autonomous detection and response \u2192 Phases 4-7 / TA0002 through TA0040. Services maturity does not map to specific phases - it determines how effectively each pillar is delivered. High-maturity vendors translate technology into operational defence; low-maturity vendors cannot."
        },
        {
            "header": "F2: ~68% of vendor capability concentrates in the reactive lifecycle half, perpetuating the detection-and-response paradigm.",
            "body": "Despite the preemptive label, autonomous detection and response dominates market investment. Autonomous Detection \u0026 Response maps to Phases 4-7 and ATT\u0026CK Execution through Impact - territory traditionally claimed by EDR, XDR, and SIEM. Market penetration is strongest in these late phases, making the right side of the lifecycle better served than the left. Services maturity determines whether reactive technology translates into effective containment: vendors with mature managed operations measurably outperform those delivering technology alone."
        },
        {
            "header": "F3: Adversary management is the critical bottleneck: lowest penetration, widest delivery-model gap.",
            "body": "Adversary Management covers the most technically demanding capabilities: polymorphic defence, moving target defence, runtime protection, and credential rotation. These disrupt Kill Chain Phases 1-2 and ATT\u0026CK TA0042, TA0005, TA0006. Yet only ~55% of vendors offer meaningful Adversary Management capability. ~49% of the market (platform-only vendors) fall below the competency threshold entirely, leaving the earliest adversary phases, where preemptive value is greatest - undefended."
        },
        {
            "header": "F4: Services maturity is the cross-cutting differentiator separating effective vendors from technology-only providers.",
            "body": "Services \u0026 Capability Maturity does not compete with the four pillars for lifecycle phase coverage. It multiplies their delivered value. The four maturity dimensions - implementation, advisory, managed operations, autonomous delivery - form a spectrum from basic deployment to fully autonomous operations. Vendors with high Services \u0026 Capability Maturity scores achieve higher effective coverage across all four pillars. Platform-only vendors (~49% of market) show the starkest gap: strong technology that underperforms in practice because no service layer operationalises it."
        },
        {
            "header": "F5: ATT\u0026CK tactic mapping validates the kill chain findings through a complementary tactical lens.",
            "body": "Reconnaissance (TA0043): strong coverage via Exposure Management. Resource Development (TA0042): weakest coverage; depends on Adversary Management, which ~45% of the market lacks. Initial Access (TA0001): moderate-to-strong through Exposure Management + Posture \u0026 Policy Management + Autonomous Detection \u0026 Response convergence. Execution through Impact (TA0002-TA0040): well-covered by Autonomous Detection \u0026 Response, but effectiveness depends on Services \u0026 Capability Maturity maturity. Lateral Movement (TA0008): weakly covered overall. The gap pattern is consistent: vendors invest in tactics they can detect, not tactics they could prevent."
        },
        {
            "header": "F6: ~25% of vendors achieve full-spectrum coverage; services maturity is the strongest predictor.",
            "body": "Roughly one quarter of assessed vendors demonstrate meaningful competency across all four defensive pillars with coverage spanning both preemptive phases (Kill Chain Phases 1-3) and reactive phases (Kill Chain Phases 4-7). The remaining ~75% have at least one lifecycle phase with no meaningful defence. Services maturity is the strongest predictor of full-spectrum status: high-Services \u0026 Capability Maturity vendors are disproportionately represented among full-spectrum vendors, while low-Services \u0026 Capability Maturity vendors cluster in narrow-spectrum regardless of technology strength."
        }
    ],

    "recommendations": [
        {
            "header": "R1: Map your portfolio against both frameworks to find where shift-left coverage drops below threshold. [Responds to F1, F5]",
            "body": "Conduct a dual-framework mapping: for each of the seven kill chain phases, identify product capabilities that provide measurable defence. Cross-reference against the 14 ATT\u0026CK enterprise tactics. Any phase or tactic below baseline is a structural gap that limits competitive positioning. Prioritise early-phase gaps - Reconnaissance and Weaponization are where preemptive cybersecurity creates differentiated value and where most vendors are weakest. Finding F1 establishes that four pillars map to specific adversary lifecycle phases; F5 confirms ATT\u0026CK tactic mapping validates and extends those gaps at technique level. Together, these findings make dual-framework mapping the essential first step."
        },
        {
            "header": "R2: Prioritise adversary management as the highest-leverage shift-left investment. [Responds to F3]",
            "body": "Adversary Management is the critical market gap identified in Finding F3. Focus on four capabilities: polymorphic defence (dynamic attack surface), runtime application protection (real-time exploitation blocking), dynamic infrastructure defence (invalidates recon), and credential rotation (renders stolen access worthless within hours). Each maps to high-value ATT\u0026CK tactics: TA0042, TA0005, TA0006. Only ~55% of vendors offer meaningful Adversary Management capability, and ~49% of platform-only vendors fall below the competency threshold entirely. Strong Adversary Management differentiates as genuinely preemptive while competitors remain stuck in detection-and-response."
        },
        {
            "header": "R3: Reframe go-to-market messaging around adversary lifecycle coverage, not feature checklists. [Responds to F2]",
            "body": "Finding F2 reveals that ~68% of vendor capability concentrates in the reactive lifecycle half despite preemptive branding. Buyers speak the language of MITRE ATT\u0026CK and Kill Chain frameworks. Restructure marketing to show which phases and tactics each product addresses, what percentage of adversary techniques are disrupted, and the measurable difference between preemptive intervention and reactive response. Vendors who adopt lifecycle messaging first will define the evaluation framework competitors must follow. The reactive concentration documented in F2 means most competitors cannot credibly claim left-side coverage - making lifecycle messaging a structural differentiator, not just a positioning choice."
        },
        {
            "header": "R4: Invest in services maturity as the cross-cutting multiplier across all four pillars. [Responds to F1, F4, F6]",
            "body": "Findings F1, F4, and F6 collectively establish services maturity as the single most important cross-cutting investment. F1 shows services maturity determines how effectively each pillar is delivered. F4 documents the stark gap between platform-only and services-mature vendors. F6 reveals services maturity as the strongest predictor of full-spectrum status. Invest across all four dimensions: implementation (rapid deployment), advisory (findings \u2192 action), managed operations (24/7 expert operation), and autonomous delivery (automation at scale). Platform-only vendors that neglect services maturity will find their technology capabilities increasingly commoditised as buyers recognise that capability without maturity delivers inferior outcomes."
        },
        {
            "header": "R5: Develop a Shift-Left Readiness Index as a customer-facing metric. [Responds to F5, F6]",
            "body": "Findings F5 and F6 provide the analytical foundation for a measurable readiness index. F5 identifies the specific ATT\u0026CK tactics where preemptive differentiation is greatest (TA0042, TA0005, TA0006, TA0008). F6 establishes that only ~25% of vendors achieve full-spectrum coverage. Create a measurable index quantifying: percentage of adversary techniques neutralised before exploitation, detection-time reduction via proactive hunting, attack paths eliminated through Exposure Management and Posture \u0026 Policy Management, and credential/infrastructure rotation frequency. Weight by services maturity to reflect operational depth. This index becomes a competitive differentiator, renewal metric, and expansion vehicle."
        }
    ],

    # Analysis sections restructured around finding→recommendation mappings
    "analysis_sections": [
        {
            "title": "The Dual-Framework Lens: Mapping Pillars to Adversary Phases (F1 \u2192 R1)",
            "body": "Finding F1 establishes the structural mapping: four defensive pillars align to specific adversary lifecycle phases across both the Kill Chain and MITRE ATT\u0026CK. Recommendation R1 operationalises this mapping as a portfolio assessment tool.\n\nThe Lockheed Martin Cyber Kill Chain describes seven sequential adversary phases: Reconnaissance, Weaponisation, Delivery, Exploitation, Installation, Command and Control, and Actions on Objectives. MITRE ATT\u0026CK complements this with 14 enterprise tactics providing granular technique-level detail. Traditional cybersecurity focuses on Phases 4-7: detecting exploitation, finding malware, disrupting C2, and responding to data theft. Preemptive cybersecurity shifts investment left - into Phases 1-3 where interventions prevent adversary success before exploitation.\n\nFour defensive pillars map directly to adversary phases:\n\u2022 Exposure Management \u2192 Phase 1 / TA0043, TA0007 - eliminates discoverable attack surface\n\u2022 Adversary Management \u2192 Phases 1-2 / TA0042, TA0005, TA0006 - invalidates adversary preparation\n\u2022 Posture \u0026 Policy Management \u2192 Phases 2-3 / TA0001, TA0004 - validates controls before weapons arrive\n\u2022 Autonomous Detection \u0026 Response \u2192 Phases 4-7 / TA0002 through TA0040 - deception, hunting, containment, response\n\nServices maturity is not phase-mapped. It operates as a cross-cutting enablement layer determining how effectively each pillar delivers at every phase. CPOs should use this dual-framework mapping as the starting point for portfolio assessment (R1): any phase or tactic below baseline represents a structural gap that limits competitive positioning."
        },
        {
            "title": "Reactive Concentration and the Case for Lifecycle Messaging (F2 \u2192 R3)",
            "body": "Finding F2 documents the market's most consequential structural imbalance: ~68% of vendor capability concentrates in the reactive lifecycle half. Recommendation R3 addresses this directly by reframing go-to-market around lifecycle phase coverage.\n\nDespite the preemptive label, Autonomous Detection \u0026 Response dominates market investment. It maps to Phases 4-7 and ATT\u0026CK Execution through Impact - territory traditionally claimed by EDR, XDR, and SIEM. Market penetration is strongest in these late phases, making the right side of the lifecycle better served than the left.\n\nThe concentration has three strategic implications. First, it means most vendors compete on capabilities buyers already have. The reactive zone is well-served; incremental detection-and-response investment yields diminishing returns. Second, it perpetuates the detection paradigm that preemptive cybersecurity was designed to replace. Third, it creates a structural messaging opportunity: vendors who can credibly demonstrate left-side coverage immediately differentiate against competitors stuck in the reactive half.\n\nR3 recommends restructuring marketing to show which phases and tactics each product addresses, what percentage of adversary techniques are disrupted, and the measurable difference between preemptive intervention and reactive response. The reactive concentration documented in F2 means most competitors cannot credibly claim left-side coverage - making lifecycle messaging a structural differentiator, not just a positioning choice."
        },
        {
            "title": "The Adversary Management Bottleneck: Highest Leverage, Lowest Penetration (F3 \u2192 R2)",
            "body": "Finding F3 identifies Adversary Management as the critical market bottleneck. Recommendation R2 positions it as the highest-leverage shift-left investment.\n\nAdversary Management is the most technically demanding and strategically important pillar. Its four capabilities each map to specific adversary disruption mechanisms:\n\u2022 Polymorphic defence \u2192 invalidates recon data (Kill Chain Phase 1 / TA0043)\n\u2022 Runtime application protection \u2192 blocks exploitation at runtime (Kill Chain Phases 2,4 / TA0005)\n\u2022 Dynamic infrastructure defence \u2192 frustrates delivery and C2 (Kill Chain Phases 1,3,6 / TA0011)\n\u2022 Credential rotation \u2192 renders stolen access worthless (Kill Chain Phases 2,4,6 / TA0006)\n\nAdversary Management has the lowest vendor penetration (~55%) and the widest delivery-model gap. Platform-plus-partner vendors lead; platform-only vendors (~49% of market) fall well below the competency threshold.\n\nR2 recommends focusing investment on all four Adversary Management capabilities. Each maps to ATT\u0026CK tactics (TA0042, TA0005, TA0006) that most competitors struggle to address. Moving target defence, polymorphic defence, and credential rotation are nascent capabilities most vendors have not prioritised. A vendor with strong Adversary Management immediately differentiates as genuinely preemptive while the ~68% reactive concentration (F2) means competitors cannot easily follow."
        },
        {
            "title": "Services Maturity: The Cross-Cutting Multiplier (F4, F6 \u2192 R4)",
            "body": "Findings F4 and F6 establish services maturity as the single most important cross-cutting investment. Recommendation R4 prescribes investment across all four maturity dimensions.\n\nServices \u0026 Capability Maturity does not compete with the four pillars for lifecycle phase coverage - it multiplies their delivered value. The four maturity dimensions form a compounding spectrum:\n\u2022 Implementation: rapid deployment, configuration, integration\n\u2022 Advisory: translate findings into actionable risk guidance\n\u2022 Managed operations: 24/7 expert-operated security services\n\u2022 Autonomous delivery: automation at scale, self-tuning, minimal human intervention\n\nDirect service providers achieve the highest effective lifecycle coverage - not because of superior technology, but because service delivery operationalises it. Platform-plus-partner vendors show variable effectiveness depending on partner quality. Platform-only vendors (~49% of market) consistently underperform relative to their technology scores because no service layer operationalises capability.\n\nF6 provides the decisive evidence: services maturity is the strongest predictor of full-spectrum status. Only ~25% of vendors achieve meaningful competency across all four pillars. High-Services \u0026 Capability Maturity vendors are disproportionately represented among this full-spectrum group, while low-Services \u0026 Capability Maturity vendors cluster in narrow-spectrum regardless of technology strength. The implication for R4 is clear: services maturity investment yields returns across all pillars simultaneously, making it the highest-leverage cross-cutting initiative in the preemptive stack."
        },
        {
            "title": "ATT\u0026CK Tactic Validation and the Shift-Left Readiness Index (F5 \u2192 R1, R5)",
            "body": "Finding F5 validates kill chain findings through the complementary ATT\u0026CK tactical lens and feeds both Recommendation R1 (dual-framework mapping) and R5 (Shift-Left Readiness Index).\n\nATT\u0026CK's 14 tactics provide technique-level validation of the kill chain coverage patterns:\n\u2022 TA0043 Reconnaissance: Strong coverage via Exposure Management (>90% of vendors)\n\u2022 TA0042 Resource Development: Weakest coverage; depends on Adversary Management (~55% penetration)\n\u2022 TA0001 Initial Access: Moderate-to-strong via three-pillar convergence\n\u2022 TA0002 Execution / TA0003 Persistence: Well-covered by Autonomous Detection \u0026 Response\n\u2022 TA0005 Defence Evasion: Split - Adversary Management preemptive, Autonomous Detection \u0026 Response detective\n\u2022 TA0006 Credential Access: Partially covered by credential rotation; mostly reactive detection\n\u2022 TA0008 Lateral Movement: Weakly covered; dynamic segmentation rarely deployed\n\u2022 TA0009-TA0011, TA0040 Collection through Impact: Covered by Autonomous Detection \u0026 Response; effectiveness depends on services maturity\n\nConsistent pattern: the market invests in tactics it can detect, not tactics it could prevent. TA0042, TA0005, TA0006, and TA0008 represent the greatest preemptive differentiation opportunities.\n\nFor R1, this tactic-level mapping is the second dimension of the dual-framework portfolio assessment. Phase-level gaps show where; tactic-level gaps show what specifically must be addressed.\n\nFor R5, these tactic gaps provide the foundation for a Shift-Left Readiness Index: percentage of adversary techniques neutralised before exploitation, detection-time reduction via proactive hunting, attack paths eliminated through Exposure Management and Posture \u0026 Policy Management, and credential/infrastructure rotation frequency. Weighted by services maturity, this index becomes a competitive differentiator, renewal metric, and expansion vehicle. F6's finding that only ~25% achieve full-spectrum coverage establishes the market context that makes such an index immediately differentiating."
        },
        {
            "title": "Strategic Roadmap: Findings to Full Lifecycle Coverage by 2028",
            "body": "Each roadmap phase maps directly to the finding\u2192recommendation pairs that justify its priorities.\n\nPhase 1 (2025-2026) - Assess and Map [F1\u2192R1, F5\u2192R1]:\nConduct dual-framework portfolio mapping informed by F1's pillar-to-phase alignment and F5's ATT\u0026CK tactic validation. Assess Services \u0026 Capability Maturity across all four dimensions. Identify where technology exists but service delivery is insufficient. Begin development of the Shift-Left Readiness Index (R5).\n\nPhase 2 (2026-2027) - Build Preemptive Core [F3\u2192R2, F2\u2192R3]:\nInvest in or acquire the four Adversary Management capabilities identified in F3: polymorphic defence, runtime protection, dynamic infrastructure defence, credential rotation. Each maps to high-value ATT\u0026CK tactics competitors struggle to address (R2). Simultaneously reframe go-to-market messaging around lifecycle coverage (R3), leveraging F2's reactive concentration finding to demonstrate structural differentiation.\n\nPhase 3 (2027-2028) - Maturity-Amplified Coverage [F4\u2192R4, F6\u2192R4, R5]:\nMature Services \u0026 Capability Maturity across all four pillars (R4), informed by F4's evidence that services maturity multiplies delivered value and F6's evidence that services maturity predicts full-spectrum status. Deploy the Shift-Left Readiness Index (R5) as a customer-facing metric. Develop outcome-based pricing tied to phase coverage.\n\nSuccess by 2028: Coverage across all seven Kill Chain phases and 14 ATT\u0026CK tactics. Adversary Management well above market average (addressing F3). Services maturity above threshold across all dimensions (addressing F4, F6). Lifecycle messaging is standard practice (addressing F2). Shift-Left Readiness Index deployed (addressing F5). All marketing references lifecycle coverage and services maturity as complementary evaluation criteria.\n\nThe differentiation window is 2-3 years. By 2028, lifecycle phase coverage plus mature service delivery transitions from competitive advantage to minimum requirement."
        }
    ],

    "background": "The Lockheed Martin Cyber Kill Chain (2011) provides a seven-phase model of adversary behaviour widely adopted by security operations, threat intelligence, and enterprise architecture teams. MITRE ATT\u0026CK complements it with 14 enterprise tactics and hundreds of techniques providing granular, technique-level evaluation of defensive coverage.\n\nThe preemptive cybersecurity market is defined by four defensive pillars (Exposure Management, Adversary Management, Posture \u0026 Policy Management, Autonomous Detection \u0026 Response) and one cross-cutting enablement layer (Services \u0026 Capability Maturity). The four pillars map to adversary lifecycle phases; Services \u0026 Capability Maturity determines how effectively each pillar is delivered. This research maps pillars onto both kill chain phases and ATT\u0026CK tactics, then examines how services maturity amplifies or diminishes defensive value at every phase.",

    "impact": "For CPOs and Product Strategy Leaders:\n\n1. Portfolio Reassessment [F1, F5 \u2192 R1]: Dual-framework mapping will likely reveal Adversary Management (early phases) as the primary structural gap and Services \u0026 Capability Maturity as the delivery bottleneck. Investment cases can now be framed in adversary lifecycle terms using the pillar-to-phase mapping established in F1 and validated by F5.\n\n2. Go-to-Market Transformation [F2 \u2192 R3]: Shift from feature-list messaging to phase-coverage messaging. F2 documents that ~68% of vendor capability clusters in reactive phases; lifecycle messaging structurally differentiates vendors with genuine left-side coverage.\n\n3. Competitive Intelligence [F4, F6 \u2192 R4]: Evaluate competitors on two dimensions - lifecycle phase coverage (four pillars) and services maturity (cross-cutting). F4 and F6 establish that a high-tech/low-services vendor is fundamentally different from a moderate-tech/high-services vendor. Services maturity predicts full-spectrum status.\n\nFor Engineering Leaders [F3 \u2192 R2]: Prioritise Adversary Management capabilities (polymorphic defence, MTD, credential rotation) as technically demanding but strategically valuable moats mapping to ATT\u0026CK tactics competitors struggle to address.\n\nFor Corporate Development [F3, F4 \u2192 R2, R4]: Evaluate acquisitions on both phase coverage (especially Adversary Management per F3) and service delivery capability (per F4). Services maturity acquisitions yield returns across all pillars simultaneously.",

    "conclusion": "When four defensive pillars are mapped to seven kill chain phases and 14 ATT\u0026CK tactics, the market's structural dynamics are clear: exposure management and posture validation anchor the preemptive zone (F1), adversary management is the critical bottleneck (F3), autonomous detection and response provides broad reactive coverage that dominates market investment (F2), and services maturity is the cross-cutting differentiator predicting full-spectrum status (F4, F6).\n\nThe strategic imperative maps directly from findings to action: dual-framework assessment (F1, F5 \u2192 R1), adversary management investment (F3 \u2192 R2), lifecycle messaging (F2 \u2192 R3), services maturity as the multiplier (F4, F6 \u2192 R4), and a measurable shift-left readiness index (F5, F6 \u2192 R5).\n\nThe vendors that will define next-generation preemptive cybersecurity are those that combine genuine shift-left capability with the services maturity to deliver operational results across the entire adversary lifecycle.",

    "glossary": [
        {"term": "Cyber Kill Chain", "definition": "Lockheed Martin's seven-phase adversary model: Reconnaissance, Weaponisation, Delivery, Exploitation, Installation, C2, Actions on Objectives."},
        {"term": "MITRE ATT\u0026CK", "definition": "Knowledge base of 14 enterprise tactics and hundreds of techniques based on real-world adversary behaviour. Complements the kill chain with granular technique-level mapping."},
        {"term": "ATT\u0026CK Tactics", "definition": "14 enterprise tactics: Reconnaissance, Resource Development, Initial Access, Execution, Persistence, Privilege Escalation, Defence Evasion, Credential Access, Discovery, Lateral Movement, Collection, Exfiltration, C2, Impact."},
        {"term": "Shift-Left", "definition": "Moving defensive investment from late adversary phases (detection/response) to early phases (prevention/disruption before exploitation)."},
        {"term": "Preemptive Zone", "definition": "Kill Chain Phases 1-3 / ATT\u0026CK Reconnaissance through Initial Access, where preemptive capabilities prevent attacks before exploitation."},
        {"term": "Reactive Zone", "definition": "Kill Chain Phases 4-7 / ATT\u0026CK Execution through Impact, where capabilities detect and respond after exploitation."},
        {"term": "Exposure Management", "definition": "Attack surface discovery, vulnerability prioritisation, CTEM. Maps to Kill Chain Phase 1 / TA0043, TA0007."},
        {"term": "Adversary Management", "definition": "Polymorphic defence, MTD, runtime protection, credential rotation. Maps to Kill Chain Phases 1-2 / TA0042, TA0005, TA0006. Critical market bottleneck."},
        {"term": "Posture \u0026 Policy Management", "definition": "BAS, CSPM, control validation, pen testing. Maps to Kill Chain Phases 2-3 / TA0001, TA0004."},
        {"term": "Autonomous Detection \u0026 Response", "definition": "Deception, hunting, containment, incident response. Maps to Kill Chain Phases 4-7 / TA0002 through TA0040."},
        {"term": "Services \u0026 Capability Maturity", "definition": "Cross-cutting enablement layer: implementation, advisory, managed operations, autonomous delivery. Not phase-mapped; multiplies effectiveness of all four pillars."},
        {"term": "Finding\u2192Recommendation Mapping", "definition": "Each analysis section maps specific findings (F1-F6) to the recommendations (R1-R5) they justify, creating traceable lineage from evidence to action."}
    ],

    "evidence": [
        "Gartner Preemptive Cybersecurity Vendor Assessment, 2025-2026: Multi-vendor evaluation across 4 defensive pillars, 1 cross-cutting Services \u0026 Capability Maturity dimension, and 24 sub-pillar dimensions.",
        "Lockheed Martin Cyber Kill Chain (Hutchins, Cloppert, Amin, 2011): Intelligence-Driven Computer Network Defence. Foundational framework for mapping defensive capabilities to adversary behaviour.",
        "MITRE ATT\u0026CK Framework v14 (2024): Enterprise tactics and techniques knowledge base for granular tactic-level pillar mapping.",
        "Pillar-to-Kill-Chain and Pillar-to-ATT\u0026CK mappings derived from sub-pillar capability definitions and documented defensive mechanisms. Services \u0026 Capability Maturity assessed separately as cross-cutting delivery effectiveness.",
        "Vendor delivery model classification (Direct Service, Platform-Plus-Partner, Platform-Only) based on public documentation, service pages, and partner program analysis.",
        "Full-spectrum classification: vendors achieving meaningful competency across all four pillars with strong Services \u0026 Capability Maturity, equating to effective coverage across both frameworks.",
        "NIST CSF 2.0 (2024): Cross-referenced with lifecycle mapping for Govern, Identify, Protect, Detect, Respond, Recover alignment.",
        "Finding\u2192Recommendation traceability matrix derived from capability gap analysis: F1/F5\u2192R1 (dual mapping), F3\u2192R2 (adversary management), F2\u2192R3 (lifecycle messaging), F1/F4/F6\u2192R4 (services maturity), F5/F6\u2192R5 (readiness index)."
    ]
}

# Verify summary length
summary_len = len(v4["summary"])
print(f"Summary length: {summary_len} characters (limit: 300)")
assert summary_len < 300, f"Summary too long: {summary_len}"

# Check if id already exists
existing_ids = [r["id"] for r in data["reports"]]
if v4["id"] in existing_ids:
    print(f"Report {v4['id']} already exists. Removing old version.")
    data["reports"] = [r for r in data["reports"] if r["id"] != v4["id"]]

data["reports"].append(v4)

with open("precyber_market_insight_reports.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Added report: {v4['id']}")
print(f"Total reports: {len(data['reports'])}")
print(f"Summary: {v4['summary']}")
print(f"Findings: {len(v4['findings'])}")
print(f"Recommendations: {len(v4['recommendations'])}")
print(f"Analysis sections: {len(v4['analysis_sections'])}")
print("\nAnalysis section titles:")
for s in v4["analysis_sections"]:
    print(f"  - {s['title']}")
