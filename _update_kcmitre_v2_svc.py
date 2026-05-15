"""
Update cpo-killchain-mitre-v2 report to reframe SVC as a cross-cutting enabler
instead of a framework-mapped pillar.

Changes:
- Remove SVC from all kill chain phase and MITRE ATT&CK tactic mappings
- Reassign late-phase tactics (TA0009, TA0010, TA0040) to ADR
- Reframe SVC as cross-cutting services maturity enabler across all 4 pillars
- Add services maturity as vendor differentiator emphasis
- Update all findings, recommendations, analysis sections, glossary, etc.
"""
import json, os

path = os.path.join(os.path.dirname(__file__), 'precyber_market_insight_reports.json')
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

report = None
for r in data['reports']:
    if r['id'] == 'cpo-killchain-mitre-v2':
        report = r
        break

if not report:
    print("ERROR: Report cpo-killchain-mitre-v2 not found!")
    exit(1)

# ── Update Summary ──
report['summary'] = (
    "The preemptive cybersecurity market offers a fundamentally different value proposition when "
    "viewed through the lens of two complementary adversary frameworks: the Lockheed Martin Cyber "
    "Kill Chain and the MITRE ATT&CK knowledge base. Rather than concentrating investment on "
    "detection and response after exploitation has occurred, preemptive capabilities shift defensive "
    "coverage into the earliest stages of adversary operations, where reconnaissance, weaponization, "
    "and delivery occur. Among 51 vendors assessed, four defensive pillars map directly to adversary "
    "lifecycle phases: exposure management, adversary management, posture and policy management, and "
    "adversary disruption. Services and capability maturity operates as a cross-cutting "
    "enablement layer that determines how effectively each defensive pillar is actually delivered. "
    "The strongest coverage maps to early kill chain phases through exposure management and posture "
    "validation, but a significant gap in adversary management capabilities undermines the preemptive "
    "promise. Services maturity emerges as the critical vendor differentiator: vendors with mature "
    "service delivery capabilities achieve meaningfully higher effective coverage across all four "
    "defensive pillars, while platform-only vendors with low services maturity cannot translate their "
    "technology capabilities into operational defensive value. Chief Product Officers who invest in "
    "both adversary lifecycle phase coverage and services maturity as a delivery multiplier will "
    "capture the emerging preemptive cybersecurity market."
)

# ── Update SPA ──
report['spa'] = (
    "By 2028, 35% of enterprise preemptive cybersecurity evaluations will use adversary lifecycle "
    "phase coverage, mapped to kill chain phases or MITRE ATT&CK tactics, as a primary vendor "
    "selection criterion, up from less than 10% today. Services maturity will emerge as the decisive "
    "differentiator, as buyers recognize that technology capability without mature service delivery "
    "produces ineffective defensive coverage. Vendors that demonstrate both strong phase coverage and "
    "high services maturity across all four defensive pillars will achieve significantly higher win "
    "rates in competitive evaluations."
)

# ── Update Findings ──
report['findings'] = [
    {
        "header": "Four defensive pillars map directly to the adversary lifecycle, while services maturity operates as a cross-cutting enabler that determines actual delivered value.",
        "body": (
            "When the preemptive cybersecurity pillars are mapped to the seven-phase Lockheed Martin "
            "Cyber Kill Chain, four pillars align to specific adversary lifecycle phases. Exposure "
            "management maps primarily to Phase 1 (Reconnaissance), reducing what adversaries can "
            "discover through attack surface management and continuous threat exposure management. "
            "Adversary management spans Phases 1 and 2 (Reconnaissance and Weaponization), using "
            "polymorphic defense, moving target defense, and dynamic infrastructure to make adversary "
            "preparation ineffective. Posture and policy management maps to Phases 2 and 3 "
            "(Weaponization and Delivery), validating security controls through breach and attack "
            "simulation before weapons reach their targets. Adversary disruption covers "
            "Phases 4 through 7 (Exploitation through Actions on Objectives), providing deception, "
            "threat hunting, counter-adversary operations, containment, and managed incident response. "
            "This same mapping holds when viewed through MITRE ATT&CK: exposure management addresses "
            "Reconnaissance (TA0043) and Discovery (TA0007), adversary management disrupts Resource "
            "Development (TA0042) and Defense Evasion (TA0005), posture and policy management validates "
            "against Initial Access (TA0001) and Privilege Escalation (TA0004), and adversary disruption"
            " covers Execution (TA0002) through Impact (TA0040). Services and capability "
            "maturity does not map to specific adversary phases because it is not a defensive capability "
            "deployed against adversary actions. Instead, it operates as a cross-cutting enablement "
            "layer that determines how effectively each of the four defensive pillars is delivered. A "
            "vendor with strong technology but weak service delivery cannot translate capability into "
            "operational defensive value."
        )
    },
    {
        "header": "The majority of vendor capability concentrates in the reactive half of the adversary lifecycle, perpetuating the detection-and-response paradigm that preemptive cybersecurity is designed to replace.",
        "body": (
            "Despite the preemptive label, the market's actual capability distribution reveals a "
            "reactive bias. Adversary disruption capabilities map primarily to Phases 4 "
            "through 7 (Exploitation through Actions on Objectives), territory traditionally claimed by "
            "endpoint detection and response, extended detection and response, and security information "
            "and event management solutions. In ATT&CK terms, this spans Execution (TA0002), "
            "Persistence (TA0003), Lateral Movement (TA0008), Command and Control (TA0011), Collection "
            "(TA0009), Exfiltration (TA0010), and Impact (TA0040). Detection and response has strong "
            "market penetration, making the mid-to-right adversary lifecycle phases better served than "
            "the earliest preemptive phases where adversary management operates. This paradox, a "
            "preemptive market that is structurally more reactive than preemptive, presents a critical "
            "product strategy opportunity. Vendors that genuinely invest in the earliest adversary "
            "lifecycle phases distinguish themselves from the detection-and-response crowd. Critically, "
            "services maturity determines whether detection and response technology translates into "
            "effective incident containment and remediation: vendors with mature managed operations "
            "achieve measurably better outcomes at every phase than those delivering technology alone."
        )
    },
    {
        "header": "Adversary management is the critical bottleneck in the shift-left thesis, with the lowest market penetration and the widest delivery model gap among all pillars.",
        "body": (
            "Adversary management is the linchpin of genuine preemptive defense. Its core capabilities, "
            "polymorphic and morphing defense, runtime application protection, dynamic network and "
            "infrastructure defense, and identity and credential rotation, represent the most technically "
            "demanding capabilities in the preemptive stack. In kill chain terms, these capabilities "
            "disrupt Phases 1 and 2. In ATT&CK terms, they counter Resource Development (TA0042), "
            "Defense Evasion (TA0005), and Credential Access (TA0006). Yet adversary management has the "
            "lowest vendor penetration among the pillars, and the widest gap between delivery models. "
            "Direct service providers and platform-plus-partner vendors maintain meaningful adversary "
            "management capability, but platform-only vendors, representing nearly half the market, fall "
            "well below the competency threshold. In adversary lifecycle terms, this means nearly half "
            "the market cannot provide meaningful coverage during reconnaissance or weaponization, "
            "precisely where the preemptive value proposition is strongest."
        )
    },
    {
        "header": "Services maturity is the cross-cutting differentiator that separates effective vendors from technology-only providers across all four defensive pillars.",
        "body": (
            "Services and capability maturity does not compete with the four defensive pillars for "
            "adversary lifecycle phase coverage. Instead, it acts as a multiplier that determines how "
            "effectively each pillar's technology capabilities are delivered. The four services "
            "sub-pillars, implementation and onboarding, consultative and advisory services, managed "
            "operations and continuous delivery, and autonomous service delivery, represent a maturity "
            "spectrum from basic deployment to fully autonomous operations. Vendors with high services "
            "maturity achieve meaningfully higher effective coverage across all four defensive pillars: "
            "their exposure management is more actionable because advisory services translate findings "
            "into remediation programs, their adversary management is more effective because managed "
            "operations teams tune and operate the technology continuously, their posture validation is "
            "more thorough because implementation teams configure controls comprehensively, and their "
            "detection and response achieves faster containment because trained analysts operate the "
            "technology around the clock. Platform-only vendors, with the lowest services maturity "
            "scores, represent the starkest example: strong technology capabilities that underperform "
            "in practice because there is no service delivery layer to operationalize them. For "
            "enterprise buyers, this means evaluating services maturity alongside defensive capability "
            "is essential. A high-capability, low-maturity vendor delivers less defensive value than "
            "a moderate-capability, high-maturity vendor."
        )
    },
    {
        "header": "MITRE ATT&CK mapping reveals the same structural gaps visible in kill chain analysis, validating the shift-left thesis through a complementary tactical lens.",
        "body": (
            "The MITRE ATT&CK framework provides 14 enterprise tactics that describe what adversaries "
            "are trying to achieve at each stage of an operation. Mapping the four defensive pillars to "
            "ATT&CK tactics confirms the kill chain findings through a more granular lens. Exposure "
            "management addresses Reconnaissance (TA0043) and Discovery (TA0007). Adversary management "
            "counters Resource Development (TA0042), Defense Evasion (TA0005), and Credential Access "
            "(TA0006). Posture and policy management validates defenses against Initial Access (TA0001) "
            "and Privilege Escalation (TA0004). Adversary disruption covers Execution "
            "(TA0002), Persistence (TA0003), Lateral Movement (TA0008), Command and Control (TA0011), "
            "Collection (TA0009), Exfiltration (TA0010), and Impact (TA0040). The gap pattern is "
            "consistent: the ATT&CK tactics that correspond to the preemptive zone, particularly "
            "Resource Development and Defense Evasion, have the weakest vendor coverage because they "
            "depend on adversary management capabilities. Services maturity, while not mapped to "
            "specific tactics, determines how effectively each tactic is actually addressed. Vendors "
            "with mature managed operations and advisory services translate ATT&CK tactic coverage from "
            "theoretical capability into operational reality."
        )
    },
    {
        "header": "Only a quarter of vendors achieve meaningful coverage across the full adversary lifecycle, and services maturity is the strongest predictor of complete coverage.",
        "body": (
            "Regardless of whether market coverage is measured through kill chain phases or ATT&CK "
            "tactics, roughly one in four vendors achieves full-spectrum coverage with meaningful "
            "capabilities across all four defensive pillars. These vendors demonstrate genuine "
            "defense-in-depth: strong scores across both the preemptive phases (kill chain 1 through 3, "
            "or ATT&CK Reconnaissance through Initial Access) and the reactive phases (kill chain 4 "
            "through 7, or ATT&CK Execution through Impact). The remaining three quarters of the "
            "market have at least one adversary lifecycle phase where they offer no meaningful defense. "
            "The strongest predictor of full-spectrum coverage is services maturity: vendors with high "
            "services and capability scores are disproportionately represented among full-spectrum "
            "vendors, while those with low services maturity cluster in the narrow-spectrum category "
            "regardless of their technology capabilities. This finding reinforces the thesis that "
            "services maturity is the cross-cutting enabler that transforms technology capability into "
            "operational defensive value across the entire adversary lifecycle."
        )
    },
]

# ── Update Recommendations ──
report['recommendations'] = [
    {
        "header": "Map your product portfolio against both the kill chain and MITRE ATT&CK to identify where shift-left coverage drops below competitive threshold.",
        "body": (
            "Chief Product Officers should conduct a dual-framework mapping exercise for their current "
            "product portfolio. For each of the seven kill chain phases, identify which product "
            "capabilities provide measurable defense. Then cross-reference against the 14 MITRE ATT&CK "
            "enterprise tactics to validate coverage at a more granular level. Any phase or tactic "
            "where coverage falls below baseline represents a structural gap that limits competitive "
            "positioning. Pay particular attention to the earliest phases: Reconnaissance and "
            "Weaponization in kill chain terms, or Reconnaissance and Resource Development in ATT&CK "
            "terms. These are the phases where preemptive cybersecurity creates differentiated value, "
            "yet where most vendors are weakest. Products that demonstrate strong early-phase coverage "
            "can command a pricing premium because they prevent incidents rather than merely detecting "
            "them."
        )
    },
    {
        "header": "Prioritize adversary management investment as the single highest-leverage initiative for shift-left positioning.",
        "body": (
            "Adversary management is the critical gap in the market. With the lowest penetration among "
            "the pillars, Chief Product Officers have a rare opportunity to create competitive "
            "separation through targeted investment. Focus on four specific capabilities: polymorphic "
            "and morphing defense that changes the attack surface dynamically, runtime application "
            "self-protection that blocks exploitation in real time, dynamic network infrastructure "
            "defense that invalidates adversary reconnaissance, and identity and credential rotation "
            "that renders stolen credentials worthless within hours. Each of these maps directly to the "
            "earliest kill chain phases and counters high-priority ATT&CK tactics including Resource "
            "Development, Defense Evasion, and Credential Access. Vendors that build strong adversary "
            "management capability differentiate as genuinely shift-left, while competitors remain "
            "positioned around detection and response."
        )
    },
    {
        "header": "Reframe go-to-market messaging around adversary lifecycle phase coverage rather than feature checklists.",
        "body": (
            "Enterprise security leaders speak the language of frameworks: MITRE ATT&CK, Lockheed "
            "Martin Kill Chain, and NIST Cybersecurity Framework. Yet most preemptive cybersecurity "
            "vendors market capabilities as feature lists that buyers must mentally map to their "
            "defense architecture. Chief Product Officers should restructure product marketing to "
            "explicitly show which kill chain phases and ATT&CK tactics each product addresses, what "
            "percentage of adversary techniques are disrupted at each phase, and the measurable "
            "difference between preemptive intervention and reactive response in terms of containment "
            "time, impact radius, and incident cost. This reframing converts a technical product "
            "conversation into a strategic risk conversation that security leaders and boards can act "
            "on. Vendors who adopt adversary lifecycle messaging first will define the evaluation "
            "framework that competitors must then follow."
        )
    },
    {
        "header": "Invest in services maturity as a cross-cutting differentiator that amplifies defensive value across all four pillars.",
        "body": (
            "Services and capability maturity is not a gap to close on the right side of the adversary "
            "lifecycle. It is the cross-cutting enablement layer that determines whether technology "
            "capability translates into operational defensive value at every phase. Chief Product "
            "Officers should invest across the four services maturity dimensions: implementation and "
            "onboarding that ensures rapid, comprehensive deployment; consultative and advisory services "
            "that translate findings into action; managed operations and continuous delivery that "
            "provide around-the-clock expert operation; and autonomous service delivery that uses "
            "automation to scale human expertise. The market data is clear: vendors with mature service "
            "delivery achieve measurably higher effective coverage across all four defensive pillars. "
            "Platform-only vendors that neglect services maturity will find their technology "
            "capabilities increasingly commoditized as buyers recognize that capability without "
            "operational maturity delivers inferior outcomes. Building services maturity is not about "
            "adding a managed service line. It is about ensuring every pillar, from exposure management "
            "through detection and response, is delivered with the operational depth that converts "
            "capability into results."
        )
    },
    {
        "header": "Develop a Shift-Left Readiness Index as a customer-facing metric that quantifies preemptive posture improvement.",
        "body": (
            "Create a measurable, customer-facing metric that quantifies the shift-left impact of your "
            "product. This index should measure the percentage of adversary techniques neutralized "
            "before the exploitation phase, the reduction in detection time achieved through proactive "
            "threat hunting versus reactive alerting, the number of attack paths eliminated through "
            "exposure management and posture validation, and the frequency of credential and "
            "infrastructure rotation that invalidates adversary preparation. Incorporate services "
            "maturity as a weighting factor: the index should reflect not just technology capability "
            "but the operational maturity with which that capability is delivered. This index becomes "
            "a competitive differentiator, a renewal metric, and an expansion vehicle. Buyers can "
            "track their shift-left progress over time, and vendors can demonstrate return on "
            "investment in terms of attacks prevented rather than incidents responded to."
        )
    },
]

# ── Update Analysis Sections ──
report['analysis_sections'] = [
    {
        "title": "The Dual Framework Lens: Lockheed Martin Kill Chain and MITRE ATT&CK",
        "body": (
            "The Lockheed Martin Cyber Kill Chain, introduced in 2011, describes seven sequential "
            "phases an adversary must complete to achieve their objective: Reconnaissance (identifying "
            "and selecting targets), Weaponization (coupling an exploit with a backdoor into a "
            "deliverable payload), Delivery (transmitting the weapon to the target environment), "
            "Exploitation (triggering the weapon to exploit a vulnerability), Installation (installing "
            "a backdoor or persistent access mechanism), Command and Control (establishing a channel "
            "to remotely manipulate the victim), and Actions on Objectives (accomplishing the "
            "adversary's original goal).\n\n"
            "The MITRE ATT&CK framework complements the kill chain with 14 enterprise tactics that "
            "describe adversary objectives at each stage of an operation. Where the kill chain "
            "provides a linear model of attack progression, ATT&CK provides a matrix of specific "
            "techniques adversaries use within each tactic category. Together, these frameworks create "
            "a comprehensive lens for evaluating defensive coverage.\n\n"
            "Traditional cybersecurity has focused overwhelmingly on the middle and late phases of "
            "both frameworks: detecting exploitation (kill chain Phase 4, ATT&CK Execution), finding "
            "installed malware (Phase 5, Persistence), disrupting command and control channels "
            "(Phase 6, Command and Control), and responding to data theft (Phase 7, Exfiltration and "
            "Impact). This reactive posture accepts that adversaries will reach the exploitation "
            "phase and attempts to minimize damage after the fact.\n\n"
            "Preemptive cybersecurity represents a fundamental paradigm shift: moving defensive "
            "investment to the earliest adversary phases, where interventions prevent adversary "
            "success before exploitation ever occurs. Four defensive pillars map directly to adversary "
            "lifecycle phases:\n\n"
            "Exposure management eliminates discoverable attack surface, addressing kill chain Phase 1 "
            "(Reconnaissance) and ATT&CK Reconnaissance (TA0043) and Discovery (TA0007).\n\n"
            "Adversary management uses polymorphic defense, moving target defense, and dynamic "
            "infrastructure to invalidate adversary preparation, addressing kill chain Phases 1 and 2 "
            "and ATT&CK Resource Development (TA0042), Defense Evasion (TA0005), and Credential "
            "Access (TA0006).\n\n"
            "Posture and policy management validates that security controls will stop known weapons "
            "before they arrive, addressing kill chain Phases 2 and 3 and ATT&CK Initial Access "
            "(TA0001) and Privilege Escalation (TA0004).\n\n"
            "Adversary disruption provides deception, threat hunting, counter-adversary "
            "operations, containment, and managed incident response across the middle and late phases, "
            "addressing kill chain Phases 4 through 7 and ATT&CK Execution (TA0002), Persistence "
            "(TA0003), Lateral Movement (TA0008), Command and Control (TA0011), Collection (TA0009), "
            "Exfiltration (TA0010), and Impact (TA0040).\n\n"
            "Services and capability maturity is distinct from the four defensive pillars. Rather than "
            "mapping to specific adversary phases, it operates as a cross-cutting enablement layer "
            "that determines how effectively each pillar is delivered. A vendor's services maturity, "
            "spanning implementation, advisory, managed operations, and autonomous delivery, amplifies "
            "or diminishes the defensive value of every pillar across every phase of the adversary "
            "lifecycle."
        )
    },
    {
        "title": "Adversary Lifecycle Phase Coverage: Where the Market Actually Defends",
        "body": (
            "Mapping vendor capability data to both kill chain phases and ATT&CK tactics reveals a "
            "stark coverage asymmetry across the market.\n\n"
            "In the earliest phases, exposure management provides strong reconnaissance-phase "
            "coverage. The overwhelming majority of vendors offer meaningful attack surface management, "
            "continuous threat exposure management, and third-party supply chain visibility. However, "
            "adversary management, which is essential for disrupting adversary preparation at the "
            "weaponization phase, reaches only about half the vendor population. In ATT&CK terms, "
            "this means the market has strong coverage for Reconnaissance (TA0043) through exposure "
            "management but weak coverage for Resource Development (TA0042), which requires adversary "
            "management capabilities that most vendors lack.\n\n"
            "Posture and policy management provides strong validation at the delivery phase. Breach "
            "and attack simulation, cloud security posture management, and control validation ensure "
            "that defenses are tested before real adversaries challenge them. In ATT&CK terms, this "
            "covers Initial Access (TA0001) and Privilege Escalation (TA0004) validation.\n\n"
            "The convergence of three pillars at the delivery phase creates the strongest coverage "
            "point in the preemptive zone. Exposure management closes vulnerability delivery paths, "
            "posture management validates defenses, and detection and response introduces deception. "
            "This is the best-defended early phase.\n\n"
            "In the late phases, adversary disruption provides coverage through threat "
            "hunting, deception, counter-adversary operations, containment, and incident response. "
            "Detection and response now spans Phases 4 through 7 and the corresponding ATT&CK "
            "tactics from Execution through Impact. However, the effectiveness of this coverage "
            "varies dramatically based on services maturity. Vendors with strong managed operations "
            "achieve rapid detection and containment, while those delivering technology without "
            "service support leave customers to operate complex detection and response tools "
            "independently, with predictably mixed results.\n\n"
            "The overall pattern is consistent across both frameworks: vendors cluster their "
            "capabilities in the middle of the adversary lifecycle, leaving the earliest phases "
            "(where preemptive value is greatest) underserved. Services maturity determines whether "
            "the coverage that exists on paper translates into effective defense in practice."
        )
    },
    {
        "title": "The Adversary Management Bottleneck: Why It Determines Shift-Left Success",
        "body": (
            "Adversary management represents the most technically demanding and strategically "
            "important pillar in the preemptive stack. Its four core capabilities each map to specific "
            "adversary disruption mechanisms across both frameworks:\n\n"
            "Polymorphic and morphing defense changes the shape of the defense surface dynamically, "
            "invalidating adversary reconnaissance data. In kill chain terms, this disrupts Phase 1. "
            "In ATT&CK terms, it counters Reconnaissance (TA0043) techniques such as Active Scanning "
            "(T1595) and Gather Victim Network Information (T1590).\n\n"
            "Runtime application protection blocks exploitation attempts at runtime without signature "
            "dependence. This maps to kill chain Phases 2 and 4, and ATT&CK Defense Evasion (TA0005) "
            "techniques such as Process Injection (T1055) and Obfuscated Files (T1027).\n\n"
            "Dynamic network and infrastructure defense uses moving target principles to change "
            "network topology, addresses, and service configurations, frustrating delivery and command "
            "and control. This maps to kill chain Phases 1, 3, and 6, and ATT&CK Command and Control "
            "(TA0011) techniques.\n\n"
            "Identity and credential rotation automates rotation of credentials and session tokens, "
            "rendering stolen access worthless within hours. This maps to kill chain Phases 2, 4, "
            "and 6, and counters ATT&CK Credential Access (TA0006) techniques such as Brute Force "
            "(T1110) and Credential Dumping (T1003).\n\n"
            "The market data tells a sobering story. Adversary management has the lowest vendor "
            "penetration among all pillars and the widest delivery model gap. Platform-plus-partner "
            "vendors lead, followed by direct service providers, while platform-only vendors, "
            "representing nearly half the market, fall well below the competency threshold. The gap "
            "between the best-performing delivery model and the largest market segment represents a "
            "significant capability deficit in the market's most critical preemptive pillar.\n\n"
            "For Chief Product Officers, adversary management investment is the single "
            "highest-leverage initiative for differentiation. Moving target defense, polymorphic "
            "defense, and automated credential rotation are nascent capabilities that most competitors "
            "have not prioritized. A vendor that achieves strong adversary management capability "
            "immediately differentiates as genuinely preemptive because they can demonstrate disruption "
            "at the earliest phases of the adversary lifecycle, territory that detection-and-response "
            "vendors simply cannot claim."
        )
    },
    {
        "title": "MITRE ATT&CK Tactic Coverage: A Granular View of Market Gaps",
        "body": (
            "While the kill chain provides a valuable linear model of adversary progression, MITRE "
            "ATT&CK offers a more granular view that maps specific adversary techniques to the four "
            "defensive pillars. This tactic-level analysis reveals coverage patterns that the kill "
            "chain view alone cannot capture.\n\n"
            "Reconnaissance (TA0043) has strong coverage through exposure management. Most vendors "
            "offer attack surface discovery and vulnerability prioritization that directly counters "
            "adversary reconnaissance techniques such as Active Scanning and Search Open Websites.\n\n"
            "Resource Development (TA0042) has the weakest coverage in the market. Only adversary "
            "management capabilities address the techniques adversaries use to build their attack "
            "infrastructure: Acquire Infrastructure (T1583), Develop Capabilities (T1587), and Obtain "
            "Capabilities (T1588). With adversary management reaching only about half the market, "
            "this tactic represents the broadest gap.\n\n"
            "Initial Access (TA0001) has moderate-to-strong coverage through the convergence of "
            "exposure management (reducing entry points), posture management (validating controls), "
            "and detection and response (deploying deception). When three pillars converge on a "
            "single ATT&CK tactic, coverage improves significantly.\n\n"
            "Execution (TA0002) and Persistence (TA0003) are well-covered by adversary disruption"
            " capabilities including endpoint detection, behavioral analytics, and threat "
            "hunting.\n\n"
            "Defense Evasion (TA0005) is partially covered by adversary management (runtime "
            "protection) but largely depends on detection and response capabilities, creating a "
            "split-coverage pattern where the preemptive layer is thin.\n\n"
            "Credential Access (TA0006) is partially covered by adversary management through "
            "credential rotation, but most vendors address this reactively through detection rather "
            "than preemptively through rotation.\n\n"
            "Lateral Movement (TA0008) is weakly covered overall. While detection and response "
            "provides monitoring, the preemptive strategy of dynamic network segmentation (an "
            "adversary management capability) is rarely deployed.\n\n"
            "Collection (TA0009), Exfiltration (TA0010), Command and Control (TA0011), and Impact "
            "(TA0040) are covered by adversary disruption capabilities, placing them "
            "in the later phases of the adversary lifecycle. The effectiveness of this coverage is "
            "heavily influenced by services maturity: vendors with strong managed operations achieve "
            "significantly faster detection and containment of these late-stage adversary actions.\n\n"
            "The ATT&CK view reinforces the kill chain finding: the market invests in the adversary "
            "tactics it knows how to detect, not the adversary tactics it could prevent. Resource "
            "Development, Defense Evasion, and Credential Access represent the greatest opportunities "
            "for preemptive differentiation."
        )
    },
    {
        "title": "Services Maturity as the Cross-Cutting Vendor Differentiator",
        "body": (
            "The most significant finding in this analysis is not about which adversary phase is "
            "best or worst covered. It is about the role of services maturity as the cross-cutting "
            "factor that determines whether defensive capabilities translate into operational "
            "results.\n\n"
            "Each delivery model exhibits a distinct services maturity profile that directly affects "
            "its effectiveness across all four defensive pillars.\n\n"
            "Direct service providers maintain the highest services maturity scores. Their internal "
            "analyst teams, security operations infrastructure, and consultative capabilities mean "
            "that every defensive pillar, from exposure management through detection and response, "
            "is delivered with human expertise and operational depth. The result is the broadest "
            "effective adversary lifecycle coverage, not because their technology is necessarily "
            "superior, but because their service delivery operationalizes that technology.\n\n"
            "Platform-plus-partner vendors show strong technology capabilities but rely on partner "
            "ecosystems for service delivery. Their services maturity profiles vary depending on "
            "partner quality and integration depth, creating accountability gaps. When technology "
            "and service delivery are owned by different organizations, response coordination "
            "introduces latency and the customer bears the integration burden.\n\n"
            "Platform-only vendors exhibit the lowest services maturity scores and the most dramatic "
            "gap between technology capability and effective delivery. These vendors may offer "
            "competitive exposure management or detection and response technology, but without "
            "implementation support, advisory services, or managed operations, their customers must "
            "independently operationalize complex security tools. The result is that platform-only "
            "vendors consistently underperform their technology scores in practice.\n\n"
            "The four services maturity dimensions reveal where the gaps are deepest. Implementation "
            "and onboarding determines first-value time and deployment completeness. Consultative and "
            "advisory services determine whether findings are translated into strategic action. "
            "Managed operations and continuous delivery determine whether defensive tools run "
            "effectively around the clock. Autonomous service delivery determines the scalability of "
            "expert-level operations. Vendors that invest across all four dimensions create a "
            "compounding advantage that technology capability alone cannot replicate.\n\n"
            "For Chief Product Officers, the strategic implication is clear: services maturity "
            "investment yields returns across every pillar and every adversary lifecycle phase, making "
            "it the highest-leverage cross-cutting investment in the preemptive cybersecurity stack."
        )
    },
    {
        "title": "Strategic Roadmap: Building Full Adversary Lifecycle Coverage by 2028",
        "body": (
            "Based on the dual-framework analysis, the following phased roadmap provides Chief "
            "Product Officers a path to full adversary lifecycle coverage, with services maturity "
            "as the foundational enablement layer.\n\n"
            "Phase 1 (2025 to 2026), Assess and Map: Conduct a dual-framework mapping exercise for "
            "your current portfolio. Map the four defensive pillars to both kill chain phases and "
            "ATT&CK tactics. Separately assess services maturity across all four dimensions "
            "(implementation, advisory, managed operations, autonomous delivery) and evaluate how "
            "services maturity affects the effective delivery of each pillar. Identify where "
            "technology capability exists but service delivery is insufficient to operationalize it. "
            "Develop a Shift-Left Readiness Index metric for customer communication.\n\n"
            "Phase 2 (2026 to 2027), Build the Preemptive Core: Invest in or acquire four key "
            "adversary management capabilities: polymorphic defense that changes the attack surface "
            "dynamically, runtime application protection that blocks exploitation in real time, "
            "dynamic infrastructure defense that invalidates adversary reconnaissance, and credential "
            "rotation that renders stolen access worthless. Each maps directly to high-value ATT&CK "
            "tactics (Resource Development, Defense Evasion, Credential Access). Simultaneously, "
            "invest in services maturity to ensure new capabilities are delivered with operational "
            "depth, not just released as features.\n\n"
            "Phase 3 (2027 to 2028), Achieve Maturity-Amplified Coverage: Mature services delivery "
            "across all four defensive pillars. Develop outcome-based delivery models that tie "
            "pricing to adversary lifecycle phase coverage rather than feature deployment. Launch "
            "positioning around full adversary lifecycle coverage, enabled by services maturity, as "
            "the competitive standard.\n\n"
            "Success Metrics by 2028: Meaningful coverage across all seven kill chain phases and all "
            "14 ATT&CK enterprise tactics through the four defensive pillars. Strong adversary "
            "management capability well above today's market average. Services maturity scores above "
            "threshold across all four dimensions. Shift-Left Readiness Index deployed as a "
            "customer-facing metric. All product marketing references adversary lifecycle phase "
            "coverage and services maturity as complementary evaluation criteria.\n\n"
            "The window for differentiation is two to three years. By 2028, as buyers mature in "
            "their use of MITRE ATT&CK and kill chain frameworks for vendor evaluation, the ability "
            "to demonstrate both preemptive coverage across the earliest adversary phases and mature "
            "service delivery across all pillars will transition from a competitive advantage to a "
            "minimum requirement."
        )
    },
]

# ── Update Background ──
report['background'] = (
    "The Lockheed Martin Cyber Kill Chain provides a seven-phase model of adversary behavior that "
    "has been widely adopted by security operations teams, threat intelligence analysts, and "
    "enterprise security architects. Originally developed to analyze advanced persistent threats, "
    "the kill chain framework has become the common language for describing how attacks progress "
    "from initial reconnaissance through mission completion.\n\n"
    "The MITRE ATT&CK framework complements the kill chain with a globally accessible knowledge "
    "base of adversary tactics and techniques based on real-world observations. Its 14 enterprise "
    "tactics, mapped to hundreds of specific techniques, provide the granular detail needed to "
    "evaluate defensive coverage at the technique level. Where the kill chain describes the shape of "
    "an attack, ATT&CK describes the content.\n\n"
    "Simultaneously, the preemptive cybersecurity market has emerged as a category distinct from "
    "traditional detection-and-response solutions. Defined by four defensive pillars (Exposure "
    "Management, Adversary Management and Threat Intelligence, Posture and Policy Management, and "
    "Adversary Disruption) and a cross-cutting enablement layer (Services and "
    "Capability Maturity), preemptive cybersecurity aims to neutralize threats before they cause "
    "damage, rather than detecting and remediating after the fact. The four defensive pillars map "
    "directly to adversary lifecycle phases, while services maturity determines how effectively "
    "those pillars are delivered across all phases.\n\n"
    "This research note bridges these frameworks, mapping the four defensive pillars onto both the "
    "seven kill chain phases and the ATT&CK tactic categories, and examining how services maturity "
    "acts as a cross-cutting differentiator that amplifies or diminishes the defensive value of "
    "every pillar. By understanding where each pillar creates defensive value and how services "
    "maturity determines actual delivered effectiveness, product leaders can prioritize investment, "
    "identify structural gaps, and articulate their value proposition in terms that resonate with "
    "enterprise security buyers."
)

# ── Update Impact ──
report['impact'] = (
    "For Chief Product Officers and Product Strategy Leaders:\n\n"
    "The dual-framework mapping fundamentally reshapes product investment priorities. Chief Product "
    "Officers should expect three immediate impacts:\n\n"
    "1. Portfolio Reassessment: Current product capabilities will be evaluated against both kill "
    "chain phases and ATT&CK tactics through the four defensive pillars, likely revealing adversary "
    "management (early phases) as the primary structural gap. Services maturity assessment will "
    "reveal whether existing technology capabilities are being effectively delivered. Investment "
    "cases for both defensive capability and service delivery can now be framed in adversary "
    "lifecycle terms that executives and boards understand.\n\n"
    "2. Go-to-Market Transformation: Sales and marketing teams need new messaging frameworks that "
    "translate product features into adversary lifecycle phase coverage. The shift from feature-list "
    "messaging to phase-coverage messaging converts technical conversations into strategic ones. "
    "Services maturity should be positioned as the differentiator that converts capability into "
    "outcomes.\n\n"
    "3. Competitive Intelligence Redefinition: Competitive analyses should now include two "
    "dimensions: adversary lifecycle phase coverage (through the four defensive pillars) and "
    "services maturity (the cross-cutting enablement layer). A vendor with strong technology but "
    "weak services is a fundamentally different competitor than one with moderate technology and "
    "mature service delivery.\n\n"
    "For Technology and Engineering Leaders:\n\n"
    "Engineering roadmaps should prioritize adversary management capabilities (polymorphic defense, "
    "moving target defense, credential rotation) as the technically hardest but strategically most "
    "valuable investments. These capabilities require deep systems engineering expertise, including "
    "runtime instrumentation, network-level manipulation, and cryptographic automation, making them "
    "sustainable competitive moats that map to ATT&CK tactics competitors struggle to address.\n\n"
    "For Corporate Development and Strategy Leaders:\n\n"
    "Acquisition evaluation should incorporate both adversary lifecycle phase coverage and services "
    "maturity as criteria. Acquisitions that fill phase gaps (particularly adversary management) "
    "create strategic value in one dimension, while acquisitions that add service delivery capability "
    "create value across all pillars simultaneously, potentially yielding higher strategic return."
)

# ── Update Conclusion ──
report['conclusion'] = (
    "The Lockheed Martin Cyber Kill Chain and MITRE ATT&CK framework together provide the missing "
    "strategic lens for the preemptive cybersecurity market. When four defensive pillars are mapped "
    "against seven kill chain phases and 14 ATT&CK tactics, the market's structural dynamics become "
    "unmistakable: the preemptive zone is anchored by strong exposure management and posture "
    "validation but undermined by a critical adversary management gap; adversary disruption and "
    "response provides broad coverage across the middle and late phases; and services maturity "
    "emerges as the cross-cutting differentiator that determines whether any pillar's capability "
    "translates into operational defensive value.\n\n"
    "For Chief Product Officers, the strategic imperative is twofold. First, invest in the four "
    "defensive pillars to achieve adversary lifecycle phase coverage, with particular emphasis on "
    "the adversary management bottleneck that constrains the earliest phases. Second, invest in "
    "services maturity as the cross-cutting enablement layer that amplifies the value of every "
    "defensive pillar across every adversary phase.\n\n"
    "The shift-left thesis is compelling: investing in the earliest adversary phases (Reconnaissance, "
    "Weaponization, Delivery in kill chain terms; Reconnaissance, Resource Development, Initial "
    "Access in ATT&CK terms) prevents incidents rather than responding to them, yielding "
    "dramatically higher return on investment. But achieving this requires investment in the hardest "
    "pillar, adversary management, where the market is weakest, and the maturation of service "
    "delivery that ensures technology capability is operationalized effectively.\n\n"
    "The vendors that will define the next generation of preemptive cybersecurity are not those with "
    "the most features or the broadest technology portfolio. They are those that combine genuine "
    "shift-left defensive capability with the services maturity to deliver operational results "
    "across the entire adversary lifecycle."
)

# ── Update Glossary ──
report['glossary'] = [
    {
        "term": "Cyber Kill Chain",
        "definition": "Lockheed Martin's seven-phase model of adversary behavior: Reconnaissance, Weaponization, Delivery, Exploitation, Installation, Command and Control, and Actions on Objectives. Used to map defensive capabilities to specific adversary actions."
    },
    {
        "term": "MITRE ATT&CK",
        "definition": "A globally accessible knowledge base of adversary tactics, techniques, and procedures based on real-world observations. Provides 14 enterprise tactics and hundreds of techniques that complement the kill chain's linear model with a granular technique-level view."
    },
    {
        "term": "ATT&CK Tactics",
        "definition": "The 14 enterprise tactics in MITRE ATT&CK: Reconnaissance, Resource Development, Initial Access, Execution, Persistence, Privilege Escalation, Defense Evasion, Credential Access, Discovery, Lateral Movement, Collection, Exfiltration, Command and Control, and Impact."
    },
    {
        "term": "Shift-Left",
        "definition": "The strategic movement of defensive investment from later adversary lifecycle phases (detection and response after exploitation) to earlier phases (prevention and disruption before exploitation)."
    },
    {
        "term": "Preemptive Zone",
        "definition": "Kill Chain Phases 1 through 3 (Reconnaissance, Weaponization, Delivery) or ATT&CK tactics Reconnaissance through Initial Access, where preemptive cybersecurity capabilities prevent attacks before exploitation occurs."
    },
    {
        "term": "Reactive Zone",
        "definition": "Kill Chain Phases 5 through 7 (Installation, Command and Control, Actions on Objectives) or ATT&CK tactics Lateral Movement through Impact, where defensive capabilities detect and respond after exploitation."
    },
    {
        "term": "Exposure Management",
        "definition": "Continuous discovery, prioritization, and remediation of exploitable vulnerabilities and attack surface exposures. Maps to Kill Chain Phase 1 and ATT&CK Reconnaissance (TA0043) and Discovery (TA0007). Abbreviated as EXM in graphics."
    },
    {
        "term": "Adversary Management and Threat Intelligence",
        "definition": "Polymorphic defense, moving target defense, runtime protection, and credential rotation. Maps to Kill Chain Phases 1 and 2 and ATT&CK Resource Development (TA0042), Defense Evasion (TA0005), and Credential Access (TA0006). The critical market bottleneck. Abbreviated as AMT in graphics."
    },
    {
        "term": "Adversary Disruption",
        "definition": "Deception technology, threat intelligence operationalization, proactive threat hunting, counter-adversary operations, containment, and incident response. Maps to Kill Chain Phases 4 through 7 and ATT&CK Execution (TA0002), Persistence (TA0003), Lateral Movement (TA0008), Command and Control (TA0011), Collection (TA0009), Exfiltration (TA0010), and Impact (TA0040). Abbreviated as ADR in graphics."
    },
    {
        "term": "Posture and Policy Management",
        "definition": "Breach and attack simulation, security control validation, penetration testing, and cloud security posture management. Maps to Kill Chain Phases 2 and 3 and ATT&CK Initial Access (TA0001) and Privilege Escalation (TA0004). Abbreviated as PPM in graphics."
    },
    {
        "term": "Services and Capability Maturity",
        "definition": "Implementation, advisory, managed operations, and autonomous service delivery. A cross-cutting enablement layer that does not map to specific adversary lifecycle phases but instead determines how effectively each of the four defensive pillars is delivered. Services maturity is the primary vendor differentiator, with higher-maturity vendors achieving meaningfully greater effective coverage across all pillars. Abbreviated as SVC in graphics."
    },
    {
        "term": "Adversary Lifecycle",
        "definition": "The complete sequence of adversary actions from initial reconnaissance through mission completion, as described by either the Lockheed Martin Kill Chain (7 phases) or MITRE ATT&CK (14 tactics). Used in this report as a framework-neutral term for the adversary journey."
    },
    {
        "term": "Full-Spectrum Vendor",
        "definition": "A vendor demonstrating meaningful competency across all four defensive pillars and strong services maturity, providing effective coverage across the full adversary lifecycle. Roughly one in four assessed vendors achieves this status."
    },
    {
        "term": "Platform-Only Vendor",
        "definition": "A vendor delivering technology without mature service delivery, resulting in a gap between technology capability and operational effectiveness across all defensive pillars. These vendors may have strong technology but weak delivered outcomes."
    },
    {
        "term": "Shift-Left Readiness Index",
        "definition": "A proposed customer-facing metric quantifying how much of a customer's defensive posture shifts from reactive (late phases) to preemptive (early phases) after product deployment, weighted by services maturity."
    },
    {
        "term": "Moving Target Defense",
        "definition": "A cybersecurity strategy that continuously changes the attack surface to increase cost and complexity for adversaries. A core adversary management capability mapping to kill chain Phase 1 and ATT&CK Reconnaissance."
    },
    {
        "term": "Resource Development (TA0042)",
        "definition": "The MITRE ATT&CK tactic describing adversary actions to build attack infrastructure, develop exploits, and obtain tools. Has the weakest vendor coverage among all ATT&CK tactics because it depends on adversary management capabilities."
    },
    {
        "term": "Cross-Cutting Enablement Layer",
        "definition": "A capability dimension that does not map to specific adversary lifecycle phases but instead amplifies or diminishes the effectiveness of every phase-mapped defensive pillar. Services and capability maturity is the primary cross-cutting enablement layer in the preemptive cybersecurity stack."
    },
]

# ── Update Evidence ──
report['evidence'] = [
    "Gartner Preemptive Cybersecurity Vendor Assessment, 2025-2026: 51-vendor evaluation across 4 defensive pillars, 1 cross-cutting services maturity dimension, and 24 sub-pillar dimensions, providing the quantitative foundation for adversary lifecycle phase mapping and services maturity analysis.",
    "Lockheed Martin Cyber Kill Chain (Hutchins, Cloppert, Amin, 2011): Intelligence-Driven Computer Network Defense Informed by Analysis of Adversary Campaigns and Intrusion Kill Chains. The foundational framework for mapping defensive capabilities to adversary behavior phases.",
    "MITRE ATT&CK Framework v14 (2024): Enterprise tactics and techniques knowledge base used for granular tactic-level mapping of the four defensive pillars. Provides complementary validation of kill chain phase coverage analysis.",
    "Pillar-to-Kill-Chain and Pillar-to-ATT&CK mappings derived from sub-pillar capability definitions and their documented defensive mechanisms against specific adversary techniques documented in both frameworks. Services maturity assessed separately as a cross-cutting delivery effectiveness dimension.",
    "Vendor delivery model classification (Direct Service, Platform-Plus-Partner, and Platform-Only) based on public documentation, service pages, partner program structures, and managed service partner analysis. Services maturity profiles assessed for each delivery model.",
    "Full-spectrum classification based on vendors achieving meaningful competency across all four defensive pillars and demonstrating strong services maturity, equating to effective coverage across both the full kill chain and all ATT&CK tactic categories.",
    "NIST Cybersecurity Framework (CSF) 2.0 (2024): Cross-referenced with adversary lifecycle mapping to ensure alignment with the Govern, Identify, Protect, Detect, Respond, and Recover functions.",
]

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("SUCCESS: Updated cpo-killchain-mitre-v2 report with SVC as cross-cutting enabler.")
print(f"  - Findings: {len(report['findings'])}")
print(f"  - Recommendations: {len(report['recommendations'])}")
print(f"  - Analysis sections: {len(report['analysis_sections'])}")
print(f"  - Glossary entries: {len(report['glossary'])}")
print(f"  - Evidence items: {len(report['evidence'])}")
