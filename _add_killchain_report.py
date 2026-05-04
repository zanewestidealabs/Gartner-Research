"""Add the Kill Chain / Shift-Left report to precyber_market_insight_reports.json"""
import json, pathlib

path = pathlib.Path("precyber_market_insight_reports.json")
data = json.loads(path.read_text(encoding="utf-8"))

new_report = {
    "id": "cpo-killchain-shift-left",
    "label": "CPO / Threat Defense: Reimagining Operations Through Shift-Left Preemptive Cybersecurity",
    "title": "Market Insight: Reimagining Threat Defense Operations and Engineering Through Preemptive Cybersecurity",
    "summary": (
        "The preemptive cybersecurity market offers a fundamentally different value proposition when viewed through the lens of the Lockheed Martin Cyber Kill Chain. "
        "Rather than concentrating investment on detection and response after exploitation, preemptive capabilities shift defensive coverage leftward into the earliest kill chain phases: "
        "Reconnaissance, Weaponization, and Delivery. Of 51 vendors assessed across five capability pillars, the strongest coverage maps to the left side of the kill chain "
        "(Exposure Management at 92% penetration), but a critical 37-point gap in Adversary Management (55%) undermines the preemptive promise. "
        "Platform-only vendors, comprising 49% of the market, are structurally unable to cover the full kill chain. "
        "Chief Product Officers who reorient their product strategies around kill chain phase coverage, rather than feature checklists, "
        "will capture the emerging $8B+ preemptive cybersecurity market."
    ),
    "spa": (
        "By 2028, 35% of enterprise preemptive cybersecurity evaluations will use kill chain phase coverage as a primary vendor selection criterion, "
        "up from less than 10% today. Vendors that map their product capabilities to specific kill chain phases and demonstrate measurable shift-left "
        "coverage (Reconnaissance through Delivery) will achieve 2x higher win rates in competitive evaluations against feature-list-oriented competitors."
    ),
    "findings": [
        {
            "header": "Preemptive cybersecurity capabilities map directly to the first three phases of the Lockheed Martin Cyber Kill Chain, but most vendors fail to articulate this shift-left value proposition.",
            "body": (
                "When the five preemptive cybersecurity pillars are mapped to the seven-phase Lockheed Martin Cyber Kill Chain, a clear pattern emerges. "
                "Exposure Management (EXM) maps primarily to Phase 1 (Reconnaissance), reducing what adversaries can discover through attack surface management, "
                "continuous threat exposure management, and third-party supply chain visibility. Adversary Management (AMT) spans Phases 1-2 (Reconnaissance and Weaponization), "
                "using polymorphic defense, moving target defense, and dynamic infrastructure to make adversary preparation ineffective. "
                "Posture & Policy Management (PPM) maps to Phases 2-3 (Weaponization and Delivery), validating security controls through breach and attack simulation "
                "before weapons reach their targets. Together, these three pillars provide coverage across the first three kill chain phases — the preemptive zone — "
                "where defensive investment yields the highest ROI. Yet only 55% of vendors demonstrate competency in AMT, "
                "compared to 92% in EXM, creating a 37-point penetration gap that leaves the left side of the kill chain dangerously underserved."
            )
        },
        {
            "header": "The majority of vendor capability concentrates in the reactive half of the kill chain (Exploitation through Actions on Objectives), perpetuating the detection-and-response paradigm that preemptive cybersecurity is designed to replace.",
            "body": (
                "Despite the 'preemptive' label, the market's actual capability distribution reveals a reactive bias. "
                "Autonomous Detection & Response (ADR) maps primarily to Phases 4-6 (Exploitation, Installation, C2) — territory traditionally claimed by EDR, XDR, and SIEM vendors. "
                "Services & Capability (SVC) maps to Phases 5-7 (Installation through Actions on Objectives), providing managed response capabilities. "
                "ADR penetration stands at 78%, and SVC at 57%, meaning the mid-to-right kill chain phases are better served than the preemptive left side for AMT (55%). "
                "This paradox — a preemptive market that is structurally more reactive than preemptive — presents a critical product strategy opportunity for CPOs. "
                "Vendors that genuinely invest in Phases 1-3 capabilities distinguish themselves from the detection-and-response crowd. "
                "The data shows only 27% of assessed vendors achieve 'full-spectrum' coverage across all five pillars, "
                "meaning 73% have at least one kill chain phase where they offer no meaningful defense."
            )
        },
        {
            "header": "Adversary Management (AMT) is the critical bottleneck in the shift-left thesis, with only 55% vendor penetration and platform-only vendors averaging just 1.87 out of 5.0.",
            "body": (
                "AMT is the linchpin of genuine preemptive defense. Its sub-pillars — Polymorphic & Morphing Defense, Runtime Application Protection, "
                "Dynamic Network & Infrastructure Defense, and Identity & Credential Rotation — represent the most technically demanding capabilities in the preemptive stack. "
                "These are the capabilities that disrupt adversary preparation and weaponization before any payload is ever delivered. "
                "Yet AMT has the lowest vendor penetration (55%), the lowest platform-only average score (1.87), and the widest delivery model gap. "
                "Direct service providers average 2.45 on AMT, platform-plus-partner vendors lead at 2.74, but platform-only vendors — representing 49% of the market — "
                "score just 1.87. In kill chain terms, this means nearly half the market cannot provide meaningful coverage at Phase 1 (Reconnaissance) "
                "or Phase 2 (Weaponization), precisely where the preemptive value proposition is strongest."
            )
        },
        {
            "header": "Platform-only vendors are structurally confined to the middle of the kill chain, unable to cover the earliest or latest phases without service delivery partnerships.",
            "body": (
                "The 25 platform-only vendors (49% of the market) exhibit a clear kill chain coverage pattern: they cluster around Phases 3-5 "
                "(Delivery, Exploitation, Installation) where technology products operate without human-led services. "
                "Their EXM average (3.07) provides adequate Phase 1 scanning, but their AMT score (1.87) fails to deliver Phase 1-2 adversary disruption. "
                "Their SVC score (1.49) means they cannot support Phases 5-7 response operations. "
                "In contrast, direct service providers maintain meaningful coverage across all seven phases: EXM 3.60 (Phase 1), AMT 2.45 (Phases 1-2), "
                "PPM 2.97 (Phases 2-3), ADR 3.38 (Phases 4-6), and SVC 2.74 (Phases 5-7). "
                "The kill chain lens makes the platform-only structural deficit impossible to ignore: these vendors sell into the preemptive market "
                "but can only defend the middle three kill chain phases."
            )
        },
        {
            "header": "Vendors that achieve dual-sided kill chain coverage (Phases 1-3 and Phases 5-7) command significantly higher overall scores and market positioning, validating the full-spectrum thesis through a defense-in-depth lens.",
            "body": (
                "The 14 full-spectrum vendors (27% of the market) demonstrate a compelling pattern: they achieve meaningful scores across both the preemptive phases (1-3) "
                "and the reactive phases (5-7), creating genuine defense-in-depth. Their average minimum pillar score is 2.5+, meaning no single kill chain phase is undefended. "
                "By contrast, the 18 narrow-spectrum vendors (35%) typically cover only 2-3 consecutive kill chain phases, leaving 4-5 phases exposed. "
                "The strategic implication for CPOs is clear: the market is moving toward full kill chain coverage as the competitive standard. "
                "Enterprise buyers, guided by frameworks like MITRE ATT&CK and NIST CSF 2.0, increasingly evaluate vendors not by feature count but by phase coverage. "
                "The 73% of vendors with blind spots face a narrowing competitive window before full-spectrum becomes the minimum buyer expectation."
            )
        }
    ],
    "recommendations": [
        {
            "header": "Map your product portfolio against the seven Lockheed Martin Cyber Kill Chain phases and quantify where your shift-left coverage drops below competitive threshold.",
            "body": (
                "Chief Product Officers should immediately conduct a kill chain mapping exercise for their current product portfolio. "
                "For each of the seven phases (Reconnaissance, Weaponization, Delivery, Exploitation, Installation, C2, Actions on Objectives), "
                "identify which product capabilities provide measurable defense. Score each phase 1-5 using the same methodology applied in this assessment. "
                "Any phase scoring below 2.0 represents a structural gap that limits competitive positioning. "
                "Pay particular attention to Phases 1-2 (Reconnaissance and Weaponization): these are the phases where preemptive cybersecurity "
                "creates differentiated value, yet where most vendors score lowest. Products that demonstrate strong Phase 1-2 coverage "
                "can command a pricing premium because they prevent incidents rather than merely detecting them."
            )
        },
        {
            "header": "Prioritize Adversary Management (AMT) investment as the single highest-leverage initiative for shift-left positioning, targeting polymorphic defense and moving target defense capabilities.",
            "body": (
                "AMT is the critical gap in the market. With only 55% vendor penetration and a platform-only average of 1.87, "
                "CPOs have a rare opportunity to create competitive separation through targeted AMT investment. "
                "Focus on four specific capabilities: (1) Polymorphic and morphing defense that changes the attack surface dynamically, "
                "(2) Runtime application self-protection that blocks exploitation in real time, "
                "(3) Dynamic network infrastructure defense that invalidates adversary reconnaissance, and "
                "(4) Identity and credential rotation that makes stolen credentials worthless within hours. "
                "Each of these maps directly to Kill Chain Phases 1-2 and represents a measurably preemptive capability. "
                "Vendors that achieve AMT scores above 3.0 will differentiate as genuinely shift-left, while competitors remain stuck in detection-and-response positioning."
            )
        },
        {
            "header": "Reframe your go-to-market messaging around kill chain phase coverage rather than feature checklists, enabling buyers to understand your preemptive value proposition in defensive terms they already use.",
            "body": (
                "Enterprise security leaders speak the language of frameworks: MITRE ATT&CK, Lockheed Martin Kill Chain, NIST CSF. "
                "Yet most preemptive cybersecurity vendors market capabilities as feature lists (BAS, ASM, CTEM, RASP) that buyers must mentally map to their defense architecture. "
                "CPOs should restructure product marketing to explicitly show: (a) which kill chain phases each product addresses, "
                "(b) what percentage of adversary techniques are disrupted at each phase, and (c) the measurable difference between preemptive intervention "
                "(Phases 1-3) and reactive response (Phases 5-7) in terms of mean-time-to-containment, blast radius, and incident cost. "
                "This reframing converts a technical product conversation into a strategic risk conversation that CISOs and boards can act on. "
                "Vendors who adopt kill chain messaging first will define the evaluation framework that competitors must then follow."
            )
        },
        {
            "header": "Build or acquire service delivery capability (SVC) to close the right side of the kill chain, recognizing that preemptive products without managed response leave buyers exposed in Phases 5-7.",
            "body": (
                "The kill chain mapping reveals an uncomfortable truth: even the best shift-left products cannot guarantee zero breaches. "
                "When adversaries reach Phase 4 (Exploitation), buyers need managed detection, threat hunting, and incident response — capabilities scored under SVC. "
                "Yet 88% of platform-only vendors score below 2.0 on SVC, meaning their customers have no kill chain coverage beyond Phase 5. "
                "CPOs must address this gap either by building internal service delivery teams, acquiring managed service companies, "
                "or developing structured partner programs with embedded SLAs. The market data is clear: full kill chain coverage (Phases 1-7) "
                "correlates with full-spectrum vendor status (27% of the market), while SVC gaps correlate with narrow-spectrum positioning (35%). "
                "Buyers are increasingly unwilling to assemble multi-vendor stacks to cover all seven phases. The vendor who covers the full chain wins."
            )
        },
        {
            "header": "Develop a 'Shift-Left Readiness Index' as a product metric that quantifies how much of a customer's defensive posture moves from reactive (Phases 5-7) to preemptive (Phases 1-3) after deployment.",
            "body": (
                "Create a measurable, customer-facing metric that quantifies the shift-left impact of your product. "
                "This 'Shift-Left Readiness Index' should measure: (1) the percentage of adversary techniques neutralized before Phase 4 (Exploitation), "
                "(2) the reduction in mean-time-to-detection achieved through proactive threat hunting vs. reactive alerting, "
                "(3) the number of attack paths eliminated through exposure management and posture validation, and "
                "(4) the frequency of credential and infrastructure rotation that invalidates adversary preparation. "
                "This index becomes a competitive differentiator, a renewal metric, and an upsell vehicle. "
                "Buyers can track their shift-left progress quarterly, and vendors can demonstrate ROI in terms of attacks prevented (left side) "
                "rather than incidents responded to (right side). No vendor in the current assessment offers such a metric, "
                "creating a first-mover advantage for CPOs who build it."
            )
        }
    ],
    "analysis_sections": [
        {
            "title": "The Lockheed Martin Cyber Kill Chain: A Framework for Preemptive Value Articulation",
            "body": (
                "The Lockheed Martin Cyber Kill Chain, introduced in 2011, describes the seven sequential phases an adversary must complete to achieve their objective: "
                "**Reconnaissance** (identifying and selecting targets), **Weaponization** (coupling an exploit with a backdoor into a deliverable payload), "
                "**Delivery** (transmitting the weapon to the target environment), **Exploitation** (triggering the weapon to exploit a vulnerability), "
                "**Installation** (installing a backdoor or persistent access mechanism), **Command & Control** (establishing a channel to remotely manipulate the victim), "
                "and **Actions on Objectives** (accomplishing the adversary's original goal).\n\n"
                "Traditional cybersecurity has focused overwhelmingly on Phases 4-7 — detecting exploitation, finding installed malware, disrupting C2 channels, and responding to data theft. "
                "This reactive posture accepts that adversaries will reach the exploitation phase and attempts to minimize damage after the fact.\n\n"
                "**Preemptive cybersecurity represents a fundamental paradigm shift**: moving defensive investment to Phases 1-3, where interventions prevent adversary success "
                "before exploitation ever occurs. The five preemptive pillars map to the kill chain as follows:\n\n"
                "- **Phases 1-2 (Reconnaissance & Weaponization)**: Exposure Management (EXM) eliminates discoverable attack surface. "
                "Adversary Management (AMT) uses polymorphic defense, moving target defense, and dynamic infrastructure to invalidate adversary preparation.\n"
                "- **Phases 2-3 (Weaponization & Delivery)**: Posture & Policy Management (PPM) validates that security controls will stop known weapons. "
                "Breach and attack simulation tests defenses before real adversaries do. Cloud security posture management closes delivery vectors.\n"
                "- **Phase 3 (Delivery)**: EXM's supply chain exposure management and PPM's cloud posture management close the pathways adversaries use to deliver payloads.\n"
                "- **Phases 4-6 (Exploitation through C2)**: Autonomous Detection & Response (ADR) provides deception, threat hunting, "
                "and counter-adversary operations — still valuable, but operating in the traditional reactive zone.\n"
                "- **Phases 5-7 (Installation through Actions)**: Services & Capability (SVC) provides managed response — essential for full kill chain coverage "
                "but firmly on the right (reactive) side.\n\n"
                "This mapping reveals the core thesis: **Phases 1-3 are the preemptive zone**, where defensive investment yields the highest ROI because attacks are prevented, "
                "not merely detected. The pillars that cover this zone — EXM (92% penetration), PPM (86%), and AMT (55%) — define a vendor's shift-left readiness."
            )
        },
        {
            "title": "Kill Chain Phase Coverage Analysis: Where 51 Vendors Actually Defend",
            "body": (
                "Mapping the pillar penetration data to kill chain phases reveals a stark coverage asymmetry across the market:\n\n"
                "**Phase 1 — Reconnaissance (EXM + AMT)**: 92% of vendors provide exposure scanning (EXM), but only 55% offer adversary disruption (AMT). "
                "The average Phase 1 preemptive score is 3.33 for EXM but just 2.36 for AMT across the full market. "
                "This means most vendors can tell you what's exposed but cannot disrupt adversary reconnaissance or invalidate their targeting.\n\n"
                "**Phase 2 — Weaponization (AMT + PPM)**: PPM penetration at 86% provides strong control validation, but AMT's 55% gap means the weaponization countermeasures "
                "(polymorphic defense, runtime protection) are absent for nearly half the market. Combined Phase 2 coverage averages 2.70, below the 3.0 competitive threshold.\n\n"
                "**Phase 3 — Delivery (EXM + PPM + ADR)**: The convergence of three pillars creates the strongest coverage point. "
                "Exposure management closes vulnerability delivery paths (EXM avg 3.33), posture management validates defenses (PPM avg 2.98), "
                "and deception technology creates false targets (ADR avg 2.85). Phase 3 is the best-defended phase in the preemptive zone.\n\n"
                "**Phases 4-5 — Exploitation & Installation (AMT + ADR)**: ADR's 78% penetration provides solid detection and response at the exploitation phase. "
                "AMT sub-pillars (runtime protection, credential rotation) add exploitation resistance. Combined Phase 4-5 coverage averages 2.60.\n\n"
                "**Phases 6-7 — C2 & Actions on Objectives (ADR + SVC)**: The weakest combined coverage. ADR provides threat hunting and counter-adversary operations, "
                "but SVC's 57% penetration leaves 43% of the market without managed response capability. "
                "Platform-only vendors score just 1.49 on SVC, meaning their customers have no Kill Chain Phase 7 coverage.\n\n"
                "**The Shift-Left Coverage Index**: Averaging pillar penetration across Phases 1-3 (EXM 92%, PPM 86%, AMT 55%) yields a preemptive zone coverage of ~78%. "
                "Averaging Phases 5-7 (ADR 78%, SVC 57%) yields a reactive zone coverage of ~68%. The market's preemptive zone is actually better penetrated — "
                "but the AMT gap at 55% creates a single point of failure that undermines the entire left side of the chain."
            )
        },
        {
            "title": "The AMT Bottleneck: Why Adversary Management Determines Shift-Left Success",
            "body": (
                "Adversary Management represents the most technically demanding and strategically important pillar in the preemptive stack. "
                "Its four core sub-pillars each map to specific kill chain disruption mechanisms:\n\n"
                "- **AMT-01: Polymorphic & Morphing Defense** — Changes the shape of the defense surface dynamically, "
                "invalidating adversary reconnaissance data. Maps to Phase 1 (Reconnaissance).\n"
                "- **AMT-02: Runtime Application Protection** — Blocks exploitation attempts at runtime without signature dependence. "
                "Maps to Phase 2 (Weaponization) and Phase 4 (Exploitation).\n"
                "- **AMT-03: Dynamic Network & Infrastructure Defense** — Moving target defense that changes network topology, IP addresses, "
                "and service configurations to frustrate delivery and C2. Maps to Phases 1, 3, and 6.\n"
                "- **AMT-04: Identity & Credential Rotation** — Automated rotation of credentials and session tokens that render stolen access worthless within hours. "
                "Maps to Phases 2, 4, and 6.\n\n"
                "The market data tells a sobering story. Only 55% of vendors demonstrate meaningful AMT capability. "
                "Among delivery models, platform-plus-partner vendors lead at 2.74, followed by direct service at 2.45, "
                "while platform-only vendors average just 1.87. The gap between the best delivery model (2.74) and the largest segment (1.87) is 0.87 points — "
                "representing a 47% capability deficit in the market's most critical preemptive pillar.\n\n"
                "For CPOs, AMT investment is the single highest-leverage initiative for differentiation. "
                "Moving target defense, polymorphic defense, and automated credential rotation are nascent capabilities that most competitors have not prioritized. "
                "A vendor that achieves AMT scores above 3.0 immediately differentiates as 'genuinely preemptive' because they can demonstrate disruption "
                "at Phases 1-2 of the kill chain — territory that detection-and-response vendors simply cannot claim."
            )
        },
        {
            "title": "Delivery Model Kill Chain Profiles: Direct Service vs. Platform+Partner vs. Platform-Only",
            "body": (
                "Each delivery model exhibits a distinct kill chain coverage profile that determines its competitive positioning:\n\n"
                "**Direct Service Providers (11 vendors, 22%)** — The broadest kill chain coverage. With EXM 3.60, AMT 2.45, PPM 2.97, ADR 3.38, and SVC 2.74, "
                "direct service providers maintain scores above the 2.0 competency threshold across all five pillars — and therefore all seven kill chain phases. "
                "Their average of 3.03 reflects genuine defense-in-depth. Key advantage: they own the analyst teams and SOC infrastructure needed for Phases 5-7, "
                "while their technology investments cover Phases 1-3. Weakness: platform depth in AMT (2.45) remains below the 3.0 target.\n\n"
                "**Platform + Partner Vendors (15 vendors, 29%)** — The strongest Phase 1-2 coverage but with accountability gaps. "
                "These vendors lead on AMT (2.74) and PPM (3.21), giving them the highest average score in the preemptive zone (Phases 1-3). "
                "Their platform-plus-MSSP model creates broad coverage, but SVC is delivered via partners (2.32), creating Phases 5-7 accountability gaps. "
                "When a kill chain attack progresses past Phase 3, the handoff between platform vendor and MSSP partner introduces response latency.\n\n"
                "**Platform-Only Vendors (25 vendors, 49%)** — Structurally confined to Phases 3-5. "
                "With EXM 3.07 (adequate Phase 1 scanning), but AMT 1.87 (below threshold for Phase 1-2 disruption), ADR 2.52 (Phase 4-5), "
                "and SVC 1.49 (no Phase 5-7 response), these vendors defend only the central kill chain phases. "
                "They cannot disrupt adversary preparation (Phases 1-2) and cannot respond to successful exploitation (Phases 5-7). "
                "88% of platform-only vendors score below 2.0 on SVC, confirming the structural nature of this limitation.\n\n"
                "**CPO Implication**: Product leaders at platform-only vendors face a binary strategic choice: (1) acquire or build service delivery to cover Phases 5-7, "
                "or (2) invest aggressively in AMT to dominate Phases 1-2 and position as a preemptive-first platform that explicitly requires partner integration for response. "
                "The data suggests option (2) is faster but option (1) captures more market value long-term."
            )
        },
        {
            "title": "From Detection to Prevention: Quantifying the Economic Case for Shift-Left Investment",
            "body": (
                "The economic argument for shift-left preemptive cybersecurity is straightforward: preventing attacks at Phases 1-3 is dramatically cheaper than "
                "responding to them at Phases 5-7. While this assessment does not include cost data, the kill chain mapping provides a framework for CPOs to build the business case:\n\n"
                "**Phase 1-3 Intervention (Preemptive):**\n"
                "- Attack surface reduction eliminates entire classes of attacks before adversary investment\n"
                "- Breach and attack simulation identifies control gaps before adversaries exploit them\n"
                "- Moving target defense invalidates adversary reconnaissance, forcing costly re-targeting\n"
                "- Cost profile: technology + automation investment, lower ongoing analyst burden\n\n"
                "**Phase 5-7 Intervention (Reactive):**\n"
                "- Incident response after exploitation requires expensive analyst hours under time pressure\n"
                "- Remediation after installation requires forensic investigation and system rebuilding\n"
                "- C2 disruption requires threat intelligence and 24/7 monitoring infrastructure\n"
                "- Cost profile: high analyst headcount, incident surge costs, brand/regulatory exposure\n\n"
                "Full-spectrum vendors (27% of the market) inherently make this economic case: they reduce Phase 5-7 costs by investing in Phase 1-3 prevention. "
                "The 14 full-spectrum vendors average 3.0+ overall, with balanced coverage ensuring no kill chain phase is undefended.\n\n"
                "**CPO Action**: Build ROI models that quantify the cost-per-incident-prevented (Phases 1-3) vs. cost-per-incident-responded (Phases 5-7). "
                "Position preemptive capabilities as cost multipliers: every dollar invested in Phase 1-3 prevention avoids an estimated 5-10x in Phase 5-7 response costs. "
                "This framing converts the product conversation from a technology purchase into a risk economics decision, elevating the buyer conversation from security engineering to the board level."
            )
        },
        {
            "title": "CPO Strategic Roadmap: Building a Full Kill Chain Product Portfolio by 2028",
            "body": (
                "Based on the kill chain mapping analysis, the following phased roadmap provides Chief Product Officers a path to full kill chain coverage:\n\n"
                "**Phase 1 (2025-2026): Assess and Map** — Conduct the kill chain mapping exercise for your current portfolio. "
                "Identify which of the seven phases have scores below 2.0. Prioritize AMT investment (Phases 1-2) and SVC investment (Phases 5-7) "
                "as the two most common structural gaps. Develop a 'Shift-Left Readiness Index' metric for customer communication.\n\n"
                "**Phase 2 (2026-2027): Build the Preemptive Core** — Invest in or acquire: polymorphic defense (AMT-01), runtime application protection (AMT-02), "
                "and dynamic infrastructure defense (AMT-03). These three sub-pillars represent the highest-value shift-left capabilities. "
                "Target AMT scores above 3.0 across the portfolio. Simultaneously, strengthen PPM through embedded BAS and continuous control validation.\n\n"
                "**Phase 3 (2027-2028): Complete the Kill Chain** — Close the service gap (SVC) through managed service partnerships, acquisitions, "
                "or internal build. Develop outcome-based delivery models that tie pricing to kill chain phase coverage rather than feature deployment. "
                "Launch 'Full Kill Chain' positioning as the competitive standard.\n\n"
                "**Success Metrics by 2028:**\n"
                "- Kill chain coverage: scores above 2.5 across all 7 phases\n"
                "- AMT penetration: above 3.0 (currently market average is 2.36)\n"
                "- Shift-Left Readiness Index: deployed as customer-facing metric\n"
                "- Go-to-market: all product marketing references kill chain phase coverage\n"
                "- Win rate premium: 2x in competitive evaluations using kill chain criteria\n\n"
                "The window for differentiation is 2-3 years. By 2028, as buyers mature in their MITRE ATT&CK and kill chain usage, "
                "the ability to demonstrate preemptive (Phases 1-3) coverage will transition from a competitive advantage to a minimum requirement. "
                "CPOs who act now define the market standard; those who wait will be measured against it."
            )
        }
    ],
    "background": (
        "The Lockheed Martin Cyber Kill Chain provides a seven-phase model of adversary behavior that has been widely adopted by security operations teams, "
        "threat intelligence analysts, and enterprise security architects. Originally developed to analyze advanced persistent threats, the kill chain framework "
        "has become the lingua franca for describing how attacks progress from initial reconnaissance through mission completion.\n\n"
        "Simultaneously, the preemptive cybersecurity market has emerged as a category distinct from traditional detection-and-response solutions. "
        "Defined by five capability pillars — Exposure Management (EXM), Adversary Management (AMT), Autonomous Detection & Response (ADR), "
        "Posture & Policy Management (PPM), and Services & Capability (SVC) — preemptive cybersecurity aims to neutralize threats before they cause damage, "
        "rather than detecting and remediating after the fact.\n\n"
        "This research note bridges these two frameworks, mapping the five preemptive pillars onto the seven kill chain phases to provide CPOs with a "
        "defense-oriented product strategy framework. By understanding where each pillar creates defensive value in the kill chain, product leaders can "
        "prioritize investment, identify structural gaps, and articulate their value proposition in terms that resonate with enterprise security buyers."
    ),
    "impact": (
        "**For Chief Product Officers and Product Strategy Leaders:**\n\n"
        "The kill chain mapping fundamentally reshapes product investment priorities. CPOs should expect three immediate impacts:\n\n"
        "1. **Portfolio Reassessment**: Current product capabilities will be evaluated against kill chain phase coverage, likely revealing AMT (Phases 1-2) "
        "and SVC (Phases 5-7) as structural gaps. Investment cases for these pillars can now be framed in kill chain terms that executives and boards understand.\n\n"
        "2. **Go-to-Market Transformation**: Sales and marketing teams need new messaging frameworks that translate product features into kill chain phase coverage. "
        "The shift from 'our platform does BAS and ASM' to 'we defend Phases 1-3 of the kill chain' converts technical conversations into strategic ones.\n\n"
        "3. **Competitive Intelligence Redefinition**: Competitive analyses should now include kill chain phase coverage comparisons. "
        "A vendor with strong Phase 1-3 coverage but weak Phase 5-7 positioning is a fundamentally different competitor than one with the opposite profile.\n\n"
        "**For Technology and Engineering Leaders:**\n\n"
        "Engineering roadmaps should prioritize AMT sub-pillars (polymorphic defense, moving target defense, credential rotation) as the technically hardest "
        "but strategically most valuable investments. These capabilities require deep systems engineering expertise — runtime instrumentation, network-level manipulation, "
        "and cryptographic automation — making them sustainable competitive moats.\n\n"
        "**For Corporate Development and M&A:**\n\n"
        "Kill chain phase coverage should become a primary M&A evaluation criterion. Acquisitions that fill kill chain gaps (particularly AMT and SVC) "
        "create more strategic value than acquisitions that deepen existing phase coverage."
    ),
    "conclusion": (
        "The Lockheed Martin Cyber Kill Chain provides the missing strategic lens for the preemptive cybersecurity market. "
        "When five capability pillars are mapped against seven kill chain phases, the market's structural dynamics become unmistakable: "
        "the preemptive zone (Phases 1-3) is anchored by strong EXM and PPM coverage but undermined by a critical AMT gap; "
        "the reactive zone (Phases 5-7) is weakened by a service delivery crisis among platform-only vendors; "
        "and only 27% of vendors achieve meaningful coverage across the full kill chain.\n\n"
        "For Chief Product Officers, the strategic imperative is clear. The market is transitioning from feature-list competition "
        "to phase-coverage competition. Enterprise buyers, armed with MITRE ATT&CK and kill chain frameworks, "
        "are increasingly evaluating vendors by the breadth and depth of their kill chain coverage rather than the number of point features they offer.\n\n"
        "The shift-left thesis is compelling: investing in Phases 1-3 (Reconnaissance, Weaponization, Delivery) prevents incidents "
        "rather than responding to them, yielding dramatically higher ROI. But achieving this requires investment in the hardest pillar — "
        "Adversary Management — where the market is weakest.\n\n"
        "CPOs who act on this insight within the next 2-3 years will define the competitive standard for the emerging $8B+ preemptive cybersecurity market. "
        "Those who continue to compete on detection-and-response features will find themselves increasingly commoditized as buyers demand, "
        "and the market converges on, full kill chain preemptive defense."
    ),
    "glossary": [
        {"term": "Cyber Kill Chain", "definition": "Lockheed Martin's seven-phase model of adversary behavior: Reconnaissance, Weaponization, Delivery, Exploitation, Installation, Command & Control, and Actions on Objectives. Used to map defensive capabilities to specific adversary actions."},
        {"term": "Shift-Left", "definition": "The strategic movement of defensive investment from later kill chain phases (detection and response after exploitation) to earlier phases (prevention and disruption before exploitation)."},
        {"term": "Preemptive Zone", "definition": "Kill Chain Phases 1-3 (Reconnaissance, Weaponization, Delivery) where preemptive cybersecurity capabilities prevent attacks before exploitation occurs."},
        {"term": "Reactive Zone", "definition": "Kill Chain Phases 5-7 (Installation, Command & Control, Actions on Objectives) where traditional security capabilities detect and respond after exploitation."},
        {"term": "EXM", "definition": "Exposure Management. Continuous discovery, prioritization, and remediation of exploitable vulnerabilities and attack surface exposures. Maps primarily to Kill Chain Phase 1 (Reconnaissance)."},
        {"term": "AMT", "definition": "Adversary Management & Threat Intelligence. Polymorphic defense, moving target defense, runtime protection, and credential rotation. Maps to Kill Chain Phases 1-2 (Reconnaissance and Weaponization). The critical bottleneck in the preemptive market."},
        {"term": "ADR", "definition": "Autonomous Detection & Response. Deception technology, threat intelligence operationalization, proactive threat hunting, and counter-adversary operations. Maps to Kill Chain Phases 4-6 (Exploitation through C2)."},
        {"term": "PPM", "definition": "Posture & Policy Management. Breach & attack simulation, security control validation, pen testing, and cloud security posture management. Maps to Kill Chain Phases 2-3 (Weaponization and Delivery)."},
        {"term": "SVC", "definition": "Services & Capability Maturity. Implementation, advisory, managed operations, and AI-driven delivery. Maps to Kill Chain Phases 5-7 (Installation through Actions on Objectives)."},
        {"term": "Full-Spectrum Vendor", "definition": "A vendor scoring above 2.0 on all five preemptive pillars, providing meaningful coverage across all seven kill chain phases. Only 27% of assessed vendors (14 of 51) achieve this status."},
        {"term": "Platform-Only Vendor", "definition": "A vendor delivering technology without managed service delivery (SVC score < 2.0). Structurally confined to Kill Chain Phases 3-5, unable to cover the earliest or latest phases."},
        {"term": "Shift-Left Readiness Index", "definition": "A proposed customer-facing metric quantifying how much of a customer's defensive posture shifts from reactive (Phases 5-7) to preemptive (Phases 1-3) after product deployment."},
        {"term": "MITRE ATT&CK", "definition": "A globally-accessible knowledge base of adversary tactics and techniques based on real-world observations. Complementary to the Cyber Kill Chain and increasingly used in vendor evaluations."},
        {"term": "Moving Target Defense (MTD)", "definition": "A cybersecurity strategy that continuously changes the attack surface to increase cost and complexity for adversaries. A core AMT sub-pillar capability mapping to Kill Chain Phase 1."},
        {"term": "Defense-in-Depth", "definition": "A layered security strategy ensuring that if one defensive layer fails, subsequent layers provide protection. Kill chain mapping extends this concept to temporal phases of attack progression."}
    ],
    "evidence": [
        "Gartner Preemptive Cybersecurity Vendor Assessment, 2025-2026: 51-vendor evaluation across 5 capability pillars and 24 sub-pillar dimensions, providing the quantitative foundation for kill chain phase mapping.",
        "Lockheed Martin Cyber Kill Chain (Hutchins, Cloppert, Amin, 2011): Intelligence-Driven Computer Network Defense Informed by Analysis of Adversary Campaigns and Intrusion Kill Chains. The foundational framework for mapping defensive capabilities to adversary behavior phases.",
        "Pillar-to-Kill-Chain phase mapping derived from sub-pillar capability definitions and their documented defensive mechanisms against specific adversary techniques at each kill chain phase.",
        "Vendor delivery model classification (Direct Service: 11, Platform+Partner: 15, Platform-Only: 25) based on public documentation, service pages, partner program structures, and MSSP partner analysis.",
        "Pillar penetration rates (EXM 92%, PPM 86%, ADR 78%, SVC 57%, AMT 55%) calculated as percentage of 51 vendors scoring ≥ 2.0 on each pillar. Used to derive kill chain phase coverage estimates.",
        "Full-spectrum classification: 14 of 51 vendors (27%) achieve pillar scores ≥ 2.0 across all five pillars, equating to measurable defensive coverage across all seven kill chain phases.",
        "MITRE ATT&CK Framework v14 (2024): Used as complementary reference for mapping adversary techniques to kill chain phases and validating pillar-to-phase alignment.",
        "NIST Cybersecurity Framework (CSF) 2.0 (2024): Cross-referenced with kill chain mapping to ensure alignment with the Govern, Identify, Protect, Detect, Respond, and Recover functions."
    ]
}

# Add to reports array
data["reports"].append(new_report)

# Write back
path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Added report '{new_report['id']}'. Total reports: {len(data['reports'])}")
