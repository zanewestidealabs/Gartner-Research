"""
Add cpo-killchain-mitre-v3 report: Smart Brevity edition.
- All specific vendor counts removed; percentages only.
- ~50% shorter text while preserving substance.
"""
import json, pathlib

FILE = pathlib.Path(__file__).parent / 'precyber_market_insight_reports.json'

v3 = {
    "id": "cpo-killchain-mitre-v3",
    "label": "CPO / Threat Defense: Kill Chain + ATT&CK Dual-Framework (v3 \u2013 Smart Brevity)",
    "title": "Market Insight: Preemptive Cybersecurity Through the Kill Chain and MITRE ATT\u0026CK Dual-Framework Lens",

    "summary": (
        "Most preemptive cybersecurity vendors cluster capability in the reactive half of the adversary lifecycle. "
        "Four defensive pillars map directly to kill chain phases and MITRE ATT\u0026CK tactics: exposure management anchors the left, "
        "adversary management is the critical bottleneck, posture management validates delivery-phase controls, and autonomous detection "
        "and response covers the right. Services maturity operates as a cross-cutting enabler\u2014vendors with mature service delivery "
        "achieve meaningfully higher effective coverage across all four pillars. ~75% of vendors have at least one lifecycle phase gap. "
        "~25% qualify as full-spectrum. CPOs who invest in both early-phase coverage and services maturity will capture the emerging market."
    ),

    "spa": (
        "By 2028, ~35% of enterprise preemptive cybersecurity evaluations will use adversary lifecycle phase coverage as a primary "
        "vendor selection criterion, up from <10% today. Services maturity will be the decisive tiebreaker as buyers recognise that "
        "technology without operational depth delivers inferior outcomes."
    ),

    "findings": [
        {
            "header": "Four defensive pillars map to adversary lifecycle phases; services maturity is the cross-cutting enabler.",
            "body": (
                "Exposure management \u2192 KC Phase 1 / ATT\u0026CK TA0043, TA0007. "
                "Adversary management \u2192 Phases 1\u20132 / TA0042, TA0005, TA0006. "
                "Posture and policy management \u2192 Phases 2\u20133 / TA0001, TA0004. "
                "Autonomous detection and response \u2192 Phases 4\u20137 / TA0002 through TA0040. "
                "Services maturity does not map to specific phases\u2014it determines how effectively each pillar is delivered. "
                "High-maturity vendors translate technology into operational defence; low-maturity vendors cannot."
            )
        },
        {
            "header": "~68% of vendor capability concentrates in the reactive lifecycle half, perpetuating the detection-and-response paradigm.",
            "body": (
                "Despite the preemptive label, autonomous detection and response dominates market investment. "
                "ADR maps to Phases 4\u20137 and ATT\u0026CK Execution through Impact\u2014territory traditionally claimed by EDR, XDR, and SIEM. "
                "Market penetration is strongest in these late phases, making the right side of the lifecycle better served than the left. "
                "Services maturity determines whether reactive technology translates into effective containment: "
                "vendors with mature managed operations measurably outperform those delivering technology alone."
            )
        },
        {
            "header": "Adversary management is the critical bottleneck\u2014lowest penetration, widest delivery-model gap.",
            "body": (
                "AMT covers the most technically demanding capabilities: polymorphic defence, moving target defence, runtime protection, "
                "and credential rotation. These disrupt KC Phases 1\u20132 and ATT\u0026CK TA0042, TA0005, TA0006. "
                "Yet only ~55% of vendors offer meaningful AMT capability. ~49% of the market (platform-only vendors) "
                "fall below the competency threshold entirely, leaving the earliest adversary phases\u2014where preemptive value is greatest\u2014undefended."
            )
        },
        {
            "header": "Services maturity is the cross-cutting differentiator separating effective vendors from technology-only providers.",
            "body": (
                "SVC does not compete with the four pillars for lifecycle phase coverage. It multiplies their delivered value. "
                "The four maturity dimensions\u2014implementation, advisory, managed operations, autonomous delivery\u2014form a spectrum "
                "from basic deployment to fully autonomous operations. Vendors with high SVC scores achieve higher effective coverage across "
                "all four pillars. Platform-only vendors (~49% of market) show the starkest gap: strong technology that underperforms "
                "in practice because no service layer operationalises it."
            )
        },
        {
            "header": "ATT\u0026CK tactic mapping validates the kill chain findings through a complementary tactical lens.",
            "body": (
                "Reconnaissance (TA0043): strong coverage via EXM. "
                "Resource Development (TA0042): weakest coverage\u2014depends on AMT, which ~45% of the market lacks. "
                "Initial Access (TA0001): moderate-to-strong through EXM + PPM + ADR convergence. "
                "Execution through Impact (TA0002\u2013TA0040): well-covered by ADR, but effectiveness depends on SVC maturity. "
                "Lateral Movement (TA0008): weakly covered overall. "
                "The gap pattern is consistent: vendors invest in tactics they can detect, not tactics they could prevent."
            )
        },
        {
            "header": "~25% of vendors achieve full-spectrum coverage; services maturity is the strongest predictor.",
            "body": (
                "Roughly one quarter of assessed vendors demonstrate meaningful competency across all four defensive pillars "
                "with coverage spanning both preemptive phases (KC 1\u20133) and reactive phases (KC 4\u20137). "
                "The remaining ~75% have at least one lifecycle phase with no meaningful defence. "
                "Services maturity is the strongest predictor of full-spectrum status: high-SVC vendors are disproportionately "
                "represented among full-spectrum vendors, while low-SVC vendors cluster in narrow-spectrum regardless of technology strength."
            )
        }
    ],

    "recommendations": [
        {
            "header": "Map your portfolio against both frameworks to find where shift-left coverage drops below threshold.",
            "body": (
                "Conduct a dual-framework mapping: for each of the seven kill chain phases, identify product capabilities that provide "
                "measurable defence. Cross-reference against the 14 ATT\u0026CK enterprise tactics. Any phase or tactic below baseline "
                "is a structural gap that limits competitive positioning. Prioritise early-phase gaps\u2014Reconnaissance and Weaponization "
                "are where preemptive cybersecurity creates differentiated value and where most vendors are weakest."
            )
        },
        {
            "header": "Prioritise adversary management as the highest-leverage shift-left investment.",
            "body": (
                "AMT is the critical market gap. Focus on four capabilities: polymorphic defence (dynamic attack surface), "
                "runtime application protection (real-time exploitation blocking), dynamic infrastructure defence (invalidates recon), "
                "and credential rotation (renders stolen access worthless within hours). Each maps to high-value ATT\u0026CK tactics: "
                "TA0042, TA0005, TA0006. Strong AMT differentiates as genuinely preemptive while competitors remain stuck in detection-and-response."
            )
        },
        {
            "header": "Reframe go-to-market messaging around adversary lifecycle coverage, not feature checklists.",
            "body": (
                "Buyers speak the language of MITRE ATT\u0026CK and Kill Chain frameworks. Restructure marketing to show "
                "which phases and tactics each product addresses, what percentage of adversary techniques are disrupted, "
                "and the measurable difference between preemptive intervention and reactive response. "
                "Vendors who adopt lifecycle messaging first will define the evaluation framework competitors must follow."
            )
        },
        {
            "header": "Invest in services maturity as the cross-cutting multiplier across all four pillars.",
            "body": (
                "SVC is not a gap to close on the right side of the lifecycle\u2014it amplifies every pillar at every phase. "
                "Invest across all four dimensions: implementation (rapid deployment), advisory (findings \u2192 action), "
                "managed operations (24/7 expert operation), and autonomous delivery (automation at scale). "
                "Platform-only vendors that neglect SVC will find their technology capabilities increasingly commoditised "
                "as buyers recognise that capability without maturity delivers inferior outcomes."
            )
        },
        {
            "header": "Develop a Shift-Left Readiness Index as a customer-facing metric.",
            "body": (
                "Create a measurable index quantifying: percentage of adversary techniques neutralised before exploitation, "
                "detection-time reduction via proactive hunting, attack paths eliminated through EXM and PPM, "
                "and credential/infrastructure rotation frequency. Weight by services maturity to reflect operational depth. "
                "This index becomes a competitive differentiator, renewal metric, and expansion vehicle."
            )
        }
    ],

    "analysis_sections": [
        {
            "title": "The Dual Framework Lens: Kill Chain + MITRE ATT\u0026CK",
            "body": (
                "The Lockheed Martin Cyber Kill Chain describes seven sequential adversary phases: Reconnaissance, Weaponisation, "
                "Delivery, Exploitation, Installation, Command and Control, and Actions on Objectives. MITRE ATT\u0026CK complements this "
                "with 14 enterprise tactics providing granular technique-level detail.\n\n"
                "Traditional cybersecurity focuses on Phases 4\u20137: detecting exploitation, finding malware, disrupting C2, and "
                "responding to data theft. Preemptive cybersecurity shifts investment left\u2014into Phases 1\u20133 where interventions "
                "prevent adversary success before exploitation.\n\n"
                "Four defensive pillars map directly to adversary phases:\n"
                "\u2022 EXM \u2192 Phase 1 / TA0043, TA0007 \u2014 eliminates discoverable attack surface\n"
                "\u2022 AMT \u2192 Phases 1\u20132 / TA0042, TA0005, TA0006 \u2014 invalidates adversary preparation\n"
                "\u2022 PPM \u2192 Phases 2\u20133 / TA0001, TA0004 \u2014 validates controls before weapons arrive\n"
                "\u2022 ADR \u2192 Phases 4\u20137 / TA0002 through TA0040 \u2014 deception, hunting, containment, response\n\n"
                "Services maturity is not phase-mapped. It operates as a cross-cutting enablement layer that determines "
                "how effectively each pillar is actually delivered at every phase."
            )
        },
        {
            "title": "Adversary Lifecycle Coverage: Where the Market Actually Defends",
            "body": (
                "Mapping vendor capability data to both frameworks reveals stark coverage asymmetry.\n\n"
                "Early phases (KC 1\u20132): EXM provides strong reconnaissance-phase coverage\u2014>90% of vendors offer meaningful "
                "attack surface management. But AMT, essential for weaponisation-phase disruption, reaches only ~55% of vendors. "
                "In ATT\u0026CK terms: strong on TA0043 (Reconnaissance) via EXM, weak on TA0042 (Resource Development) without AMT.\n\n"
                "Mid phase (KC 3): Three-pillar convergence at the delivery phase creates the strongest preemptive coverage point. "
                "EXM closes vulnerability paths, PPM validates defences, ADR introduces deception.\n\n"
                "Late phases (KC 4\u20137): ADR provides broad coverage through hunting, deception, containment, and incident response. "
                "But effectiveness varies dramatically with services maturity. Vendors with managed operations achieve rapid detection "
                "and containment; those delivering technology alone leave customers to operate complex tools independently.\n\n"
                "Overall: vendors cluster capability in the lifecycle\u2019s middle, leaving the earliest phases\u2014where preemptive "
                "value is greatest\u2014underserved."
            )
        },
        {
            "title": "The Adversary Management Bottleneck",
            "body": (
                "AMT is the most technically demanding and strategically important pillar. Its four capabilities each map "
                "to specific adversary disruption mechanisms:\n\n"
                "\u2022 Polymorphic defence \u2192 invalidates recon data (KC 1 / TA0043)\n"
                "\u2022 Runtime application protection \u2192 blocks exploitation at runtime (KC 2,4 / TA0005)\n"
                "\u2022 Dynamic infrastructure defence \u2192 frustrates delivery and C2 (KC 1,3,6 / TA0011)\n"
                "\u2022 Credential rotation \u2192 renders stolen access worthless (KC 2,4,6 / TA0006)\n\n"
                "AMT has the lowest vendor penetration (~55%) and the widest delivery-model gap. "
                "Platform-plus-partner vendors lead, followed by direct service providers. "
                "Platform-only vendors (~49% of market) fall well below the competency threshold.\n\n"
                "For CPOs, AMT investment is the single highest-leverage initiative. Moving target defence, polymorphic defence, "
                "and credential rotation are nascent capabilities most competitors have not prioritised. A vendor with strong AMT "
                "immediately differentiates as genuinely preemptive."
            )
        },
        {
            "title": "MITRE ATT\u0026CK Tactic Coverage: Granular Market Gaps",
            "body": (
                "ATT\u0026CK\u2019s 14 tactics provide technique-level validation of the kill chain findings:\n\n"
                "\u2022 TA0043 Reconnaissance: Strong coverage via EXM (>90% of vendors)\n"
                "\u2022 TA0042 Resource Development: Weakest coverage\u2014depends on AMT (~55% penetration)\n"
                "\u2022 TA0001 Initial Access: Moderate-to-strong via EXM + PPM + ADR convergence\n"
                "\u2022 TA0002 Execution / TA0003 Persistence: Well-covered by ADR\n"
                "\u2022 TA0005 Defence Evasion: Split coverage\u2014AMT provides preemptive layer, ADR provides detection\n"
                "\u2022 TA0006 Credential Access: Partially covered by AMT credential rotation; mostly reactive detection\n"
                "\u2022 TA0008 Lateral Movement: Weakly covered overall\u2014dynamic segmentation (AMT) is rarely deployed\n"
                "\u2022 TA0009\u2013TA0011, TA0040 Collection through Impact: Covered by ADR; effectiveness depends on SVC maturity\n\n"
                "Consistent pattern: the market invests in tactics it can detect, not tactics it could prevent. "
                "TA0042, TA0005, and TA0006 represent the greatest preemptive differentiation opportunities."
            )
        },
        {
            "title": "Services Maturity as the Cross-Cutting Differentiator",
            "body": (
                "Services maturity is the factor that determines whether defensive capabilities translate into operational results.\n\n"
                "Direct service providers: Highest SVC scores. Internal analyst teams and consultative capabilities mean every pillar "
                "is delivered with operational depth. Broadest effective lifecycle coverage\u2014not because of superior technology, "
                "but because service delivery operationalises it.\n\n"
                "Platform-plus-partner vendors: Strong technology, variable SVC depending on partner quality and integration depth. "
                "Accountability gaps emerge when technology and services are owned by different organisations.\n\n"
                "Platform-only vendors: Lowest SVC scores. May have competitive technology but without implementation support, "
                "advisory services, or managed operations, customers must independently operationalise complex tools. "
                "Result: consistent underperformance relative to technology scores.\n\n"
                "The four SVC dimensions\u2014implementation, advisory, managed operations, autonomous delivery\u2014create "
                "a compounding advantage that technology alone cannot replicate. CPOs should treat SVC investment as the "
                "highest-leverage cross-cutting initiative in the preemptive stack."
            )
        },
        {
            "title": "Strategic Roadmap: Full Lifecycle Coverage by 2028",
            "body": (
                "Phase 1 (2025\u20132026) \u2014 Assess and Map: Dual-framework portfolio mapping. Assess SVC across all four dimensions. "
                "Identify where technology exists but service delivery is insufficient. Develop Shift-Left Readiness Index.\n\n"
                "Phase 2 (2026\u20132027) \u2014 Build Preemptive Core: Invest in or acquire four AMT capabilities: polymorphic defence, "
                "runtime protection, dynamic infrastructure defence, credential rotation. Each maps to high-value ATT\u0026CK tactics. "
                "Simultaneously invest in SVC to ensure new capabilities are delivered with operational depth.\n\n"
                "Phase 3 (2027\u20132028) \u2014 Maturity-Amplified Coverage: Mature SVC across all four pillars. "
                "Develop outcome-based pricing tied to phase coverage. Position full lifecycle coverage + services maturity as the standard.\n\n"
                "Success by 2028: Coverage across all seven KC phases and 14 ATT\u0026CK tactics. AMT capability well above market average. "
                "SVC above threshold across all dimensions. Shift-Left Readiness Index deployed. All marketing references lifecycle coverage "
                "and services maturity as complementary evaluation criteria.\n\n"
                "The differentiation window is 2\u20133 years. By 2028, lifecycle phase coverage plus mature service delivery transitions "
                "from competitive advantage to minimum requirement."
            )
        }
    ],

    "background": (
        "The Lockheed Martin Cyber Kill Chain (2011) provides a seven-phase model of adversary behaviour widely adopted by security "
        "operations, threat intelligence, and enterprise architecture teams. MITRE ATT\u0026CK complements it with 14 enterprise tactics "
        "and hundreds of techniques providing granular, technique-level evaluation of defensive coverage.\n\n"
        "The preemptive cybersecurity market is defined by four defensive pillars (EXM, AMT, PPM, ADR) and one cross-cutting enablement "
        "layer (SVC). The four pillars map to adversary lifecycle phases; SVC determines how effectively each pillar is delivered. "
        "This research maps pillars onto both kill chain phases and ATT\u0026CK tactics, then examines how services maturity amplifies "
        "or diminishes defensive value at every phase."
    ),

    "impact": (
        "For CPOs and Product Strategy Leaders:\n\n"
        "1. Portfolio Reassessment: Dual-framework mapping will likely reveal AMT (early phases) as the primary structural gap "
        "and SVC as the delivery bottleneck. Investment cases can now be framed in adversary lifecycle terms.\n\n"
        "2. Go-to-Market Transformation: Shift from feature-list messaging to phase-coverage messaging. "
        "Position SVC as the differentiator that converts capability into outcomes.\n\n"
        "3. Competitive Intelligence: Evaluate competitors on two dimensions\u2014lifecycle phase coverage (four pillars) "
        "and services maturity (cross-cutting). A high-tech/low-SVC vendor is fundamentally different from a moderate-tech/high-SVC vendor.\n\n"
        "For Engineering Leaders: Prioritise AMT capabilities (polymorphic defence, MTD, credential rotation) as technically demanding "
        "but strategically valuable moats mapping to ATT\u0026CK tactics competitors struggle to address.\n\n"
        "For Corporate Development: Evaluate acquisitions on both phase coverage (especially AMT) and service delivery capability. "
        "SVC acquisitions yield returns across all pillars simultaneously."
    ),

    "conclusion": (
        "When four defensive pillars are mapped to seven kill chain phases and 14 ATT\u0026CK tactics, the market\u2019s structural "
        "dynamics are clear: exposure management and posture validation anchor the preemptive zone, adversary management is the critical "
        "bottleneck, ADR provides broad reactive coverage, and services maturity is the cross-cutting differentiator.\n\n"
        "The strategic imperative is twofold: invest in the four pillars (especially AMT) for lifecycle phase coverage, "
        "and invest in services maturity as the enablement layer that amplifies every pillar at every phase.\n\n"
        "The vendors that will define next-generation preemptive cybersecurity are those that combine genuine shift-left "
        "capability with the services maturity to deliver operational results across the entire adversary lifecycle."
    ),

    "glossary": [
        {"term": "Cyber Kill Chain", "definition": "Lockheed Martin\u2019s seven-phase adversary model: Reconnaissance, Weaponisation, Delivery, Exploitation, Installation, C2, Actions on Objectives."},
        {"term": "MITRE ATT\u0026CK", "definition": "Knowledge base of 14 enterprise tactics and hundreds of techniques based on real-world adversary behaviour. Complements the kill chain with granular technique-level mapping."},
        {"term": "ATT\u0026CK Tactics", "definition": "14 enterprise tactics: Reconnaissance, Resource Development, Initial Access, Execution, Persistence, Privilege Escalation, Defence Evasion, Credential Access, Discovery, Lateral Movement, Collection, Exfiltration, C2, Impact."},
        {"term": "Shift-Left", "definition": "Moving defensive investment from late adversary phases (detection/response) to early phases (prevention/disruption before exploitation)."},
        {"term": "Preemptive Zone", "definition": "KC Phases 1\u20133 / ATT\u0026CK Reconnaissance through Initial Access, where preemptive capabilities prevent attacks before exploitation."},
        {"term": "Reactive Zone", "definition": "KC Phases 4\u20137 / ATT\u0026CK Execution through Impact, where capabilities detect and respond after exploitation."},
        {"term": "EXM \u2013 Exposure Management", "definition": "Attack surface discovery, vulnerability prioritisation, CTEM. Maps to KC Phase 1 / TA0043, TA0007."},
        {"term": "AMT \u2013 Adversary Management", "definition": "Polymorphic defence, MTD, runtime protection, credential rotation. Maps to KC Phases 1\u20132 / TA0042, TA0005, TA0006. Critical market bottleneck."},
        {"term": "PPM \u2013 Posture and Policy Management", "definition": "BAS, CSPM, control validation, pen testing. Maps to KC Phases 2\u20133 / TA0001, TA0004."},
        {"term": "ADR \u2013 Autonomous Detection and Response", "definition": "Deception, threat hunting, counter-adversary ops, containment, IR. Maps to KC Phases 4\u20137 / TA0002 through TA0040."},
        {"term": "SVC \u2013 Services and Capability Maturity", "definition": "Implementation, advisory, managed operations, autonomous delivery. Cross-cutting enablement layer\u2014determines delivered effectiveness of all four pillars. Primary vendor differentiator."},
        {"term": "Adversary Lifecycle", "definition": "Complete adversary action sequence from reconnaissance through mission completion, described by either Kill Chain (7 phases) or ATT\u0026CK (14 tactics)."},
        {"term": "Full-Spectrum Vendor", "definition": "Vendor with meaningful competency across all four pillars and strong SVC, providing effective coverage across the full adversary lifecycle. ~25% of assessed vendors."},
        {"term": "Platform-Only Vendor", "definition": "Vendor delivering technology without mature service delivery (~49% of market). Gap between technology capability and operational effectiveness across all pillars."},
        {"term": "Shift-Left Readiness Index", "definition": "Proposed customer-facing metric quantifying defensive posture shift from reactive to preemptive, weighted by services maturity."},
        {"term": "Moving Target Defence", "definition": "Strategy that continuously changes the attack surface to increase adversary cost. Core AMT capability mapping to KC Phase 1 / TA0043."},
        {"term": "Resource Development (TA0042)", "definition": "ATT\u0026CK tactic for adversary infrastructure building, exploit development, and tool acquisition. Weakest vendor coverage\u2014depends on AMT."},
        {"term": "Cross-Cutting Enablement Layer", "definition": "Capability dimension that amplifies or diminishes every phase-mapped pillar\u2019s effectiveness. SVC is the primary cross-cutting layer in the preemptive stack."}
    ],

    "evidence": [
        "Gartner Preemptive Cybersecurity Vendor Assessment, 2025\u20132026: Multi-vendor evaluation across 4 defensive pillars, 1 cross-cutting SVC dimension, and 24 sub-pillar dimensions.",
        "Lockheed Martin Cyber Kill Chain (Hutchins, Cloppert, Amin, 2011): Intelligence-Driven Computer Network Defence. Foundational framework for mapping defensive capabilities to adversary behaviour.",
        "MITRE ATT\u0026CK Framework v14 (2024): Enterprise tactics and techniques knowledge base for granular tactic-level pillar mapping.",
        "Pillar-to-Kill-Chain and Pillar-to-ATT\u0026CK mappings derived from sub-pillar capability definitions and documented defensive mechanisms. SVC assessed separately as cross-cutting delivery effectiveness.",
        "Vendor delivery model classification (Direct Service, Platform-Plus-Partner, Platform-Only) based on public documentation, service pages, and partner program analysis.",
        "Full-spectrum classification: vendors achieving meaningful competency across all four pillars with strong SVC, equating to effective coverage across both frameworks.",
        "NIST CSF 2.0 (2024): Cross-referenced with lifecycle mapping for Govern, Identify, Protect, Detect, Respond, Recover alignment."
    ]
}

# ── Load, append, save ──
data = json.loads(FILE.read_text(encoding='utf-8'))
reports = data if isinstance(data, list) else data.get('reports', data.get('data', [data]))

# Remove any previous v3 entry
reports = [r for r in reports if r.get('id') != 'cpo-killchain-mitre-v3']
reports.append(v3)

if isinstance(data, list):
    out = reports
elif 'reports' in data:
    data['reports'] = reports
    out = data
else:
    out = reports

FILE.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')

# Word count comparison
import re
def wc(obj):
    if isinstance(obj, str):
        return len(obj.split())
    if isinstance(obj, list):
        return sum(wc(item) for item in obj)
    if isinstance(obj, dict):
        return sum(wc(v) for v in obj.values())
    return 0

# Find v2 for comparison
v2 = next((r for r in reports if r.get('id') == 'cpo-killchain-mitre-v2'), None)
v2_words = wc(v2) if v2 else 0
v3_words = wc(v3)

print(f"SUCCESS: Added cpo-killchain-mitre-v3 report.")
print(f"  v2 word count: {v2_words}")
print(f"  v3 word count: {v3_words}")
print(f"  Reduction: {v2_words - v3_words} words ({100 - round(v3_words / v2_words * 100)}%)")
print(f"  Total reports: {len(reports)}")
