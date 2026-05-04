"""
Add ST Engineering (Singapore) to all MDR vendor files with full research,
scoring, rationale, and excerpts.

ST Engineering Cyber — https://www.stengg.com/en/cybersecurity
- 25+ years cybersecurity experience, SGX-listed conglomerate (S63)
- Wholly owned subsidiary D'Crypt for advanced crypto/security products
- Dedicated MDR service, IT/OT SOC architect (20+ SOCs deployed)
- AI-Enabled Threat Elimination & Response (AETER) for SMEs
- Agentic AI SOC solution, AICYMO (OT cybersecurity), CTI platform
- Cloud Security Monitoring, Supply Chain Monitoring, VAPT
- ISO 27001:2022 certified; analysts hold CISSP, OSCP, ECIH
- Sectors: aviation, banking, energy, government, healthcare, land transport,
  maritime, security, water — CII and enterprise
- Hardware products: NetCrypt, EtherCrypt, DiskCrypt, CyberTransporter,
  Quantum-Safe Encryptors, SCA-LE (zero trust)
- AGIL SecureAI, AGIL Trust (deepfake detection)
"""

import json, os, copy
from datetime import datetime

BASE = os.path.dirname(__file__)

# ── Source URLs & excerpts ────────────────────────────────────────────────
URLS = {
    "cyber_main": "https://www.stengg.com/en/cybersecurity",
    "mdr": "https://www.stengg.com/en/cybersecurity/services/managed-detection-and-response",
    "services": "https://www.stengg.com/en/cybersecurity/services",
    "solutions": "https://www.stengg.com/en/cybersecurity/solutions",
    "agentic_soc": "https://www.stengg.com/en/cybersecurity/solutions/agentic-ai-soc",
    "aicymo": "https://www.stengg.com/en/cybersecurity/solutions/aicymo",
    "cti": "https://www.stengg.com/en/cybersecurity/solutions/cyber-threat-intelligence",
    "it_soc": "https://www.stengg.com/en/cybersecurity/solutions/it-soc",
    "cloud": "https://www.stengg.com/en/cybersecurity/services/cloud-security-monitoring",
    "supply_chain": "https://www.stengg.com/en/cybersecurity/services/supply-chain-monitoring",
    "vapt": "https://www.stengg.com/en/cybersecurity/services/vapt",
    "aeter": "https://www.stengg.com/en/cybersecurity/services/ai-enabled-threat-elimination-and-response",
    "products": "https://www.stengg.com/en/cybersecurity/products",
    "agil_secureai": "https://www.stengg.com/en/cybersecurity/solutions/agil-secureai",
}

# ── Excerpts scraped from ST Engineering website ──────────────────────────
EXCERPTS = {
    "mdr_main": "Our Managed Detection and Response (MDR) service provides round-the-clock proactive threat hunting, behavioural analysis, and robust digital forensics with incident response. Leveraging cutting-edge threat intelligence, we swiftly detect and address incidents, ensuring comprehensive protection.",
    "mdr_hunting": "Hunts for unknown and sophisticated threats in real time using advanced automated analytics methods. Our skilled analyst provides actionable insights to proactively defend against evolving threats.",
    "mdr_supply_chain": "Identifies and mitigates supply chain vulnerabilities to ensure business continuity.",
    "mdr_cloud_ir": "Automates incident response tasks for faster and more efficient investigations.",
    "cyber_leader": "As a cybersecurity leader with over 25 years of experience, we offer a comprehensive suite of cybersecurity products, services, and solutions designed to safeguard IT, OT, and cloud environments.",
    "soc_20plus": "We have designed, architected and operated more than 20 Security Operations Centres (SOC) spanning across IT, OT and cloud environments for governments, Critical Information Infrastructure (CII) and enterprises.",
    "soc_orchestration": "We develop playbooks and workflows tailored to enhance the operational efficiency of your SOC.",
    "soc_threat_content": "Drawing on decades of experience managing SOCs across government agencies, CIIs, and enterprises, we deliver SOCs equipped with specially curated threat content to respond to threats proactively.",
    "soc_future_ready": "Our advanced methodology ensures seamless integration of your SOC without disrupting operations. Adopting the technology agnostic approach empowers your organisation to stay ahead of evolving threats.",
    "agentic_soc_main": "The use of Agentic AI in the Security Operations Centre (SOC) is not just about making detection of threat faster or more accurate — it should represent a transformational capability that redefines workflows and re-architects cybersecurity operations for greater operational effectiveness.",
    "agentic_soc_agents": "Dynamically coordinates agents for triage, enrichment, and remediation, with humans serving as final validators and decision-makers.",
    "agentic_soc_tools": "Connects with SIEM, SOAR, EDR, ticketing, and threat intelligence platforms for cohesive, end-to-end operations.",
    "agentic_soc_incident": "Correlates logs and attributes (hostname, user, IPs, domains) for unified visibility across IT, OT, and cloud environments.",
    "agentic_soc_chat": "Provides analysts with enriched, correlated investigative insights from trusted sources (e.g., MITRE ATT&CK, internal rules) through an intuitive chat interface.",
    "agentic_soc_grounded": "Leverages validated cybersecurity frameworks and incident history to enable contextual, evidence-based reasoning.",
    "agentic_soc_resolve": "Reduces dwell time by automating enrichment, triage, and remediation at scale.",
    "agentic_soc_speed": "This paradigm shift reduces alert fatigue, overcome blindspots and accelerates incident remediation, cutting incident handling time from many hours to seconds or minutes.",
    "cti_main": "Our AI-enabled Cyber Threat Intelligence (CTI) platform fully automates intel translation with natural language processing, delivering valuable insights and actionable intelligence for informed decision-making.",
    "cti_ai": "The custom AI engine automates tasks traditionally performed by analysts and streamlines the collection and analysis of unstructured intelligence from various sources and languages.",
    "cti_multilang": "Our platform ingests and analyses threat data in multiple languages, providing a holistic view of global cyber threats.",
    "cti_stix": "Beyond standard STIX format dissemination over TAXII protocols, our platform accommodates custom data channels and formats.",
    "aicymo_main": "Adaptive & Intelligent Cyber Monitoring of OT Systems (AICYMO) leverages AI and machine learning (ML) to develop advanced detectors for Operational Technology (OT) environments.",
    "aicymo_twin": "A digital twin of the SCADA system replicates plant behaviour to simulate, facilitating advanced anomaly detection and detailed analysis.",
    "aicymo_mlops": "Equips plant operators with a custom machine learning operations (MLOps) platform and a comprehensive data management system.",
    "cloud_main": "Our cloud security monitoring provides real-time proactive threat hunting, delivering enhanced visibility and comprehensive protection for your organisation's cloud environments.",
    "cloud_auto": "We implement automation to accelerate investigations and responses, ensuring rapid threat mitigation.",
    "supply_chain_main": "Our supply chain monitoring service continuously assesses and secures the security posture of your suppliers and partners, identifying and mitigating risks from third-party vendors to prevent breaches.",
    "aeter_main": "AI-Enabled Threat Elimination and Response is designed to close that gap by providing SMEs with enterprise-grade cybersecurity at an affordable cost.",
    "aeter_hunt": "Automatically scans and baselines environments to detect vulnerabilities before they can be exploited, while AI-driven behavioural analytics continuously monitor for anomalies in real time.",
    "aeter_monitor": "Provides continuous visibility into your systems through cybersecurity experts, enhanced by behavioural analytics and threat intelligence, and delivers monthly reports with actionable insights.",
    "aeter_ir": "Customises incident response playbooks tailored to your business and includes remote support to enable rapid threat containment.",
    "iso_cert": "We are ISO 27001:2022 certified, demonstrating our commitment to information security management. Our team of analysts hold a range of industry-recognised certifications, including CISSP, OSCP, and ECIH.",
    "vapt_main": "A comprehensive security testing approach designed to identify and address cyber security vulnerabilities across networks, wireless systems, and web and mobile applications.",
    "vapt_ir": "In addition to VAPT, we offer a range of end-to-end services, including threat intelligence, incident response, and security consulting.",
    "products_cross_domain": "Our Cross Domain Solutions (CDS) provide high-performance and robust, secure data transfer between networks or domains operating at different security levels.",
    "agil_trust": "Discover how our AI-powered tools — from real-time operational threat detection with AICYMO, to automated analysis and deepfake detection with AGIL Trust — help organisations respond faster, act smarter, and stay ahead of evolving threats.",
    "multi_pronged": "We integrate trusted hardware, deep engineering expertise, and advanced cybersecurity services to protect IT, OT, and cloud environments. Our multi-layered approach leveraging innovative tools like cloud incident response, attack surface management, and zero trust computing builds robust resilience.",
}

# ── Sub-pillar scoring with rationale ─────────────────────────────────────
# Scale 0-5: 0=No Evidence, 1=Minimal, 2=Generic Claims, 3=Demonstrated,
#             4=Advanced, 5=Market-Leading

SUB_PILLAR_SCORES = {
    # === TDR: Standard Threat Detection, Investigation & Response ===
    "TDR-01": {
        "score": 4,
        "label": "Signal Correlation & Alert Triage",
        "rationale": "ST Engineering operates 20+ SOCs spanning IT, OT, and cloud with real-time signal correlation. MDR service provides round-the-clock proactive threat hunting and behavioural analysis. Agentic AI SOC connects with SIEM, SOAR, EDR, ticketing, and threat intelligence platforms for cohesive end-to-end operations. Correlates logs and attributes (hostname, user, IPs, domains) for unified visibility across IT, OT, and cloud.",
        "excerpts": [EXCERPTS["soc_20plus"], EXCERPTS["agentic_soc_tools"], EXCERPTS["agentic_soc_incident"]],
        "urls": [URLS["solutions"], URLS["agentic_soc"], URLS["mdr"]],
    },
    "TDR-02": {
        "score": 3,
        "label": "Investigation & Root Cause Analysis",
        "rationale": "MDR service provides behavioural analysis and digital forensics. Agentic AI SOC delivers enriched, correlated investigative insights from trusted sources via chat interface and leverages incident history for evidence-based reasoning. AICYMO correlation engine links anomalies and alerts for complex cyber breaches. Investigation workflows documented but specific root cause analysis tooling not extensively detailed on public site.",
        "excerpts": [EXCERPTS["mdr_main"], EXCERPTS["agentic_soc_chat"], EXCERPTS["agentic_soc_grounded"]],
        "urls": [URLS["mdr"], URLS["agentic_soc"], URLS["aicymo"]],
    },
    "TDR-03": {
        "score": 4,
        "label": "Response Orchestration & Containment",
        "rationale": "Agentic AI SOC dynamically coordinates agents for triage, enrichment, and remediation, with humans as final validators. Automated incident response in cloud environments. Tailored playbooks and workflows for SOC operational efficiency. Remote support for rapid threat containment via AETER service. Documented orchestration across SIEM, SOAR, EDR stack.",
        "excerpts": [EXCERPTS["agentic_soc_agents"], EXCERPTS["mdr_cloud_ir"], EXCERPTS["soc_orchestration"], EXCERPTS["aeter_ir"]],
        "urls": [URLS["agentic_soc"], URLS["mdr"], URLS["it_soc"], URLS["aeter"]],
    },
    "TDR-04": {
        "score": 2,
        "label": "SLA & MTTD/MTTR Performance",
        "rationale": "ST Engineering claims incident handling time reduced from hours to seconds/minutes via Agentic AI. However, no specific MTTD/MTTR metrics or published SLAs found on public website. No third-party performance validation. Score reflects aspiration and Agentic AI claims but lack of published performance benchmarks.",
        "excerpts": [EXCERPTS["agentic_soc_speed"]],
        "urls": [URLS["agentic_soc"]],
    },

    # === PTI: Preemptive Threat Intelligence ===
    "PTI-01": {
        "score": 4,
        "label": "Threat Intelligence Operationalization",
        "rationale": "Dedicated AI-enabled CTI platform with automated intel translation via NLP. Supports STIX/TAXII protocols plus custom data channels. Custom AI engine automates collection and analysis of unstructured intelligence. Multi-language threat data ingestion. SOCs equipped with specially curated threat content. MITRE ATT&CK integration documented via Agentic AI SOC chat assistant.",
        "excerpts": [EXCERPTS["cti_main"], EXCERPTS["cti_stix"], EXCERPTS["cti_ai"], EXCERPTS["soc_threat_content"]],
        "urls": [URLS["cti"], URLS["it_soc"]],
    },
    "PTI-02": {
        "score": 3,
        "label": "Predictive Threat Analytics",
        "rationale": "AETER proactively scans and baselines environments to detect vulnerabilities before exploitation. AI-driven behavioural analytics continuously monitor for anomalies in real time. AICYMO uses ML-developed advanced detectors for OT environments. Predictive capability demonstrated in OT but less specifically detailed for IT/enterprise MDR.",
        "excerpts": [EXCERPTS["aeter_hunt"], EXCERPTS["aicymo_main"]],
        "urls": [URLS["aeter"], URLS["aicymo"]],
    },
    "PTI-03": {
        "score": 3,
        "label": "Behavior-Based Anomaly Detection",
        "rationale": "Multiple services reference behavioural analytics: MDR uses behavioural analysis, AETER employs AI-driven behavioural analytics for real-time anomaly monitoring, and AICYMO uses ML for anomaly detection in OT with digital twin simulation. UEBA-like capabilities are embedded across offerings though not a named standalone product.",
        "excerpts": [EXCERPTS["mdr_main"], EXCERPTS["aeter_hunt"], EXCERPTS["aicymo_twin"]],
        "urls": [URLS["mdr"], URLS["aeter"], URLS["aicymo"]],
    },
    "PTI-04": {
        "score": 2,
        "label": "Dark Web & Adversary Tracking",
        "rationale": "Supply chain monitoring assesses security posture of partners and identifies third-party risks. CTI platform gathers intelligence from various sources. However, no specific dark web monitoring, leaked credential monitoring, or adversary tracking services are described publicly. VAPT page mentions threat intelligence but no specific dark web capabilities.",
        "excerpts": [EXCERPTS["supply_chain_main"], EXCERPTS["cti_main"]],
        "urls": [URLS["supply_chain"], URLS["cti"]],
    },

    # === ADA: Autonomous Deception & AMTD ===
    "ADA-01": {
        "score": 1,
        "label": "Deception Technology & Honeypots",
        "rationale": "Cloud Security Monitoring mentions advanced detection capability that 'deceives and uncovers nesting threats', suggesting some deception technology. However, no named deception product, honeypot platform, or deception-as-a-service offering is documented. Minimal evidence beyond a single mention.",
        "excerpts": [EXCERPTS["cloud_main"]],
        "urls": [URLS["cloud"]],
    },
    "ADA-02": {
        "score": 1,
        "label": "Automated Moving Target Defense",
        "rationale": "ST Engineering mentions attack surface management and zero trust computing via SCA-LE product. Dynamic attack surface concepts are referenced but no specific AMTD product (runtime mutation, polymorphic defense) is documented. Cross-domain solutions provide secure data transfer between domains at different security levels, suggesting network segmentation capability.",
        "excerpts": [EXCERPTS["multi_pronged"], EXCERPTS["products_cross_domain"]],
        "urls": [URLS["cyber_main"], URLS["products"]],
    },
    "ADA-03": {
        "score": 2,
        "label": "Dynamic Attack Surface Management",
        "rationale": "Multi-pronged approach explicitly references attack surface management as an innovative tool. Supply chain monitoring provides third-party risk visibility. VAPT identifies vulnerabilities across networks, wireless, web, and mobile. However, no named EASM product or continuous external attack surface discovery tool is documented separately.",
        "excerpts": [EXCERPTS["multi_pronged"], EXCERPTS["vapt_main"]],
        "urls": [URLS["cyber_main"], URLS["vapt"]],
    },
    "ADA-04": {
        "score": 2,
        "label": "Counter-Adversary Operations",
        "rationale": "MDR includes proactive threat hunting as core capability. CTI platform enables campaign tracking via automated intelligence processing. However, no specific takedown services, adversary infrastructure disruption, or counter-adversary operations are documented publicly.",
        "excerpts": [EXCERPTS["mdr_hunting"], EXCERPTS["cti_ai"]],
        "urls": [URLS["mdr"], URLS["cti"]],
    },

    # === DIS: Disinformation & Identity Security ===
    "DIS-01": {
        "score": 3,
        "label": "Deepfake & Synthetic Media Detection",
        "rationale": "ST Engineering explicitly offers AGIL Trust for deepfake detection and automated analysis. AI-powered tools described as helping organisations detect deepfakes and respond faster. This is a named product with specific capability, though depth of technical documentation is limited.",
        "excerpts": [EXCERPTS["agil_trust"]],
        "urls": [URLS["cyber_main"]],
    },
    "DIS-02": {
        "score": 1,
        "label": "Identity Impersonation Defense",
        "rationale": "No specific BEC detection, executive impersonation defense, or identity verification product documented. Identity security is referenced indirectly through SOC monitoring and CTI but no dedicated identity impersonation service exists.",
        "excerpts": [EXCERPTS["cyber_leader"]],
        "urls": [URLS["cyber_main"]],
    },
    "DIS-03": {
        "score": 1,
        "label": "Narrative & Social Engineering Detection",
        "rationale": "VAPT and training services reference social engineering testing but no dedicated narrative attack detection, influence operation monitoring, or disinformation campaign service. Cyber Wargaming platform available for training but not operational detection.",
        "excerpts": [EXCERPTS["vapt_ir"]],
        "urls": [URLS["vapt"]],
    },
    "DIS-04": {
        "score": 1,
        "label": "Brand & Executive Protection",
        "rationale": "No specific brand monitoring, domain squatting detection, or executive digital identity protection service documented. Supply chain monitoring covers third-party risk but not brand/executive protection specifically.",
        "excerpts": [EXCERPTS["supply_chain_main"]],
        "urls": [URLS["supply_chain"]],
    },

    # === IRA: IR Support & Assistance ===
    "IRA-01": {
        "score": 3,
        "label": "Incident Scoping & Triage",
        "rationale": "MDR service includes digital forensics and incident response. AETER customises incident response playbooks tailored to each business. Agentic AI SOC automates triage with human validators. Incident scoping inherent in MDR service but specific triage methodology not deeply documented.",
        "excerpts": [EXCERPTS["mdr_main"], EXCERPTS["aeter_ir"], EXCERPTS["agentic_soc_agents"]],
        "urls": [URLS["mdr"], URLS["aeter"], URLS["agentic_soc"]],
    },
    "IRA-02": {
        "score": 3,
        "label": "Containment & Isolation Support",
        "rationale": "AETER provides remote support for rapid threat containment. MDR automates incident response tasks in cloud environments. Agentic AI SOC coordinates remediation with human validation. Cross-domain solutions provide network-level segmentation capability. Containment documented as a service capability.",
        "excerpts": [EXCERPTS["aeter_ir"], EXCERPTS["mdr_cloud_ir"], EXCERPTS["agentic_soc_resolve"]],
        "urls": [URLS["aeter"], URLS["mdr"], URLS["agentic_soc"]],
    },
    "IRA-03": {
        "score": 2,
        "label": "Recovery & Restoration Guidance",
        "rationale": "VAPT page mentions incident response and security consulting services. MDR covers comprehensive protection but specific recovery guidance, backup verification, or persistence eradication services are not detailed. The focus appears more on detection/response than post-incident recovery.",
        "excerpts": [EXCERPTS["vapt_ir"], EXCERPTS["mdr_main"]],
        "urls": [URLS["vapt"], URLS["mdr"]],
    },
    "IRA-04": {
        "score": 3,
        "label": "Post-Incident Review & Reporting",
        "rationale": "AETER delivers monthly reports with actionable insights to strengthen cyber defences. ISO 27001:2022 certification implies structured review processes. Agentic AI SOC leverages incident history for evidence-based reasoning suggesting lessons are captured. Reporting quality is documented though PIR-specific process not extensively detailed.",
        "excerpts": [EXCERPTS["aeter_monitor"], EXCERPTS["iso_cert"], EXCERPTS["agentic_soc_grounded"]],
        "urls": [URLS["aeter"], URLS["mdr"], URLS["agentic_soc"]],
    },

    # === AIO: AI Adoption in MDR Operations ===
    "AIO-01": {
        "score": 4,
        "label": "AI in Detection Engineering",
        "rationale": "AICYMO uses AI/ML for advanced OT detectors. CTI platform uses custom AI engine for automated threat intelligence processing. Agentic AI SOC integrates with SIEM, SOAR, EDR for detection. AETER uses AI-driven behavioural analytics for real-time anomaly monitoring. Multiple named AI-powered detection tools across IT, OT, and cloud.",
        "excerpts": [EXCERPTS["aicymo_main"], EXCERPTS["cti_ai"], EXCERPTS["aeter_hunt"]],
        "urls": [URLS["aicymo"], URLS["cti"], URLS["aeter"]],
    },
    "AIO-02": {
        "score": 4,
        "label": "AI in Investigation & Triage",
        "rationale": "Agentic AI SOC is specifically designed for autonomous triage, enrichment, and investigation. Chat assistant provides enriched, correlated investigative insights from MITRE ATT&CK and internal rules. Grounded knowledge integration enables evidence-based reasoning. Reduces alert fatigue by minimising false positives and repetitive workloads.",
        "excerpts": [EXCERPTS["agentic_soc_agents"], EXCERPTS["agentic_soc_chat"], EXCERPTS["agentic_soc_grounded"]],
        "urls": [URLS["agentic_soc"]],
    },
    "AIO-03": {
        "score": 4,
        "label": "AI in Response Automation",
        "rationale": "Agentic AI SOC autonomously handles complex detection, triage, and response processes. Dynamically coordinates agents for remediation with humans as final validators. Cuts incident handling time from hours to seconds/minutes. Cloud security monitoring implements automation to accelerate investigations and responses.",
        "excerpts": [EXCERPTS["agentic_soc_speed"], EXCERPTS["agentic_soc_agents"], EXCERPTS["cloud_auto"]],
        "urls": [URLS["agentic_soc"], URLS["cloud"]],
    },
    "AIO-04": {
        "score": 3,
        "label": "AI Transparency & Explainability",
        "rationale": "Agentic AI SOC uses grounded knowledge integration with validated frameworks for evidence-based reasoning. Chat interface provides human-readable insights. Human-in-the-loop design with humans as final validators. However, specific explainability documentation, AI audit trails, or hallucination rate metrics are not published.",
        "excerpts": [EXCERPTS["agentic_soc_grounded"], EXCERPTS["agentic_soc_agents"]],
        "urls": [URLS["agentic_soc"]],
    },

    # === AID: AI Development & Platform Maturity ===
    "AID-01": {
        "score": 4,
        "label": "Domain-Specific AI/LLM Investment",
        "rationale": "Multiple named AI products: AICYMO (OT AI monitoring), AI-enabled CTI platform with custom NLP engine, AGIL Trust (deepfake detection), AGIL SecureAI, Agentic AI SOC. Custom AI engine pre-trained on industry data with bespoke model customization. MLOps platform for AICYMO. Clear investment in domain-specific security AI beyond generic GPT wrappers.",
        "excerpts": [EXCERPTS["aicymo_main"], EXCERPTS["cti_ai"], EXCERPTS["aicymo_mlops"], EXCERPTS["agil_trust"]],
        "urls": [URLS["aicymo"], URLS["cti"], URLS["agil_secureai"]],
    },
    "AID-02": {
        "score": 3,
        "label": "AI Model Governance & Lifecycle",
        "rationale": "AICYMO includes MLOps platform for model management. Digital twin replicates system behaviour for simulation and testing. Custom AI engine can be further customised with proprietary data. Model governance is implicit in the engineering approach but specific versioning, monitoring, and drift detection practices are not detailed publicly.",
        "excerpts": [EXCERPTS["aicymo_mlops"], EXCERPTS["aicymo_twin"]],
        "urls": [URLS["aicymo"]],
    },
    "AID-03": {
        "score": 3,
        "label": "AI Supply Chain & Trustworthiness",
        "rationale": "AGIL SecureAI and AGIL Trust suggest investment in AI safety/trust. D'Crypt subsidiary develops advanced high-security products. Quantum-safe encryption products suggest deep cryptographic expertise. Innovation stories cover 'How to Build Robust Safeguards for AI and GenAI Security'. However, specific NIST AI RMF or EU AI Act compliance not documented.",
        "excerpts": [EXCERPTS["agil_trust"], EXCERPTS["cyber_leader"]],
        "urls": [URLS["agil_secureai"], URLS["cyber_main"]],
    },
    "AID-04": {
        "score": 4,
        "label": "AI-Driven Service Innovation",
        "rationale": "Active innovation pipeline: Agentic AI SOC (autonomous multi-agent orchestration), AICYMO (OT digital twins), AI-enabled CTI (multilingual NLP), AGIL Trust (deepfake detection), AETER (AI-enabled SME MDR). Each represents distinct AI-driven service innovation. 'Transforming Security Operation Centres with Agentic AI' published as innovation story.",
        "excerpts": [EXCERPTS["agentic_soc_main"], EXCERPTS["aicymo_main"], EXCERPTS["aeter_main"]],
        "urls": [URLS["agentic_soc"], URLS["aicymo"], URLS["aeter"]],
    },

    # === SOG: Service Operations & Governance ===
    "SOG-01": {
        "score": 4,
        "label": "24/7 SOC Coverage & Analyst Model",
        "rationale": "20+ SOCs designed and operated across IT, OT, and cloud for governments, CII, and enterprises. 24/7 monitoring explicitly stated across MDR, AETER, and cloud security services. ISO 27001:2022 certified with analysts holding CISSP, OSCP, ECIH certifications. Covered sectors include aviation, banking, energy, government, healthcare, transport, maritime.",
        "excerpts": [EXCERPTS["soc_20plus"], EXCERPTS["iso_cert"], EXCERPTS["mdr_main"]],
        "urls": [URLS["solutions"], URLS["mdr"]],
    },
    "SOG-02": {
        "score": 3,
        "label": "Client Engagement & Transparency",
        "rationale": "AETER delivers monthly reports with actionable insights. ISO 27001 implies structured client engagement. 25+ years of customer experience across CII and enterprise. However, specific onboarding processes, business review cadences, or client portal documentation are not detailed on the public website.",
        "excerpts": [EXCERPTS["aeter_monitor"], EXCERPTS["cyber_leader"]],
        "urls": [URLS["aeter"], URLS["cyber_main"]],
    },
    "SOG-03": {
        "score": 4,
        "label": "Compliance & Regulatory Alignment",
        "rationale": "ISO 27001:2022 certified explicitly documented. Serves government CII across 10+ regulated sectors (aviation, banking, energy, healthcare, transport, water, etc.). SOCs designed for national critical information infrastructure. Singapore government ecosystem alignment. Analyst certifications (CISSP, OSCP, ECIH) demonstrate professional compliance standards.",
        "excerpts": [EXCERPTS["iso_cert"], EXCERPTS["soc_20plus"]],
        "urls": [URLS["mdr"], URLS["solutions"]],
    },
    "SOG-04": {
        "score": 3,
        "label": "Reporting Quality & Metrics",
        "rationale": "AETER delivers monthly reports with actionable insights to strengthen defences. CTI platform delivers actionable intelligence for informed decision-making. Agentic AI SOC provides analyst insights through chat interface. Reporting is documented across services but specific dashboard screenshots, KPI frameworks, or ROI reporting are not publicly detailed.",
        "excerpts": [EXCERPTS["aeter_monitor"], EXCERPTS["cti_main"]],
        "urls": [URLS["aeter"], URLS["cti"]],
    },
}

# ── Build pillar scores from sub-pillar scores ──
PILLAR_IDS = ["TDR", "PTI", "ADA", "DIS", "IRA", "AIO", "AID", "SOG"]
pillar_scores = {}
for p in PILLAR_IDS:
    subs = [v["score"] for k, v in SUB_PILLAR_SCORES.items() if k.startswith(p)]
    pillar_scores[p] = round(sum(subs) / len(subs), 2) if subs else 0

sub_pillar_scores_current = {k: v["score"] for k, v in SUB_PILLAR_SCORES.items()}
sub_pillar_schema_labels = {k: v["label"] for k, v in SUB_PILLAR_SCORES.items()}
capability_coverage = [k for k, v in SUB_PILLAR_SCORES.items() if v["score"] >= 1]

# ── Build evidence dict ──
sub_pillar_evidence = {}
for sub_id, data in SUB_PILLAR_SCORES.items():
    excerpts_list = []
    for i, exc in enumerate(data["excerpts"]):
        url = data["urls"][i] if i < len(data["urls"]) else data["urls"][-1]
        terms = []
        for kw in ["MDR", "SOC", "AI", "threat", "detection", "response", "monitoring",
                    "incident", "forensics", "intelligence", "AICYMO", "Agentic",
                    "behavioural", "analytics", "automation", "MITRE"]:
            if kw.lower() in exc.lower():
                terms.append(kw)
        excerpts_list.append({
            "url": url,
            "excerpt": exc,
            "matched_terms": terms[:6],
            "relevance_score": min(9, 5 + len(terms))
        })
    sub_pillar_evidence[sub_id] = {
        "source_urls": list(dict.fromkeys(data["urls"])),
        "excerpts": excerpts_list,
        "notes": data["rationale"]
    }

# ── Build the complete vendor entry ──
vendor_entry = {
    "vendor": "ST Engineering",
    "website": "https://www.stengg.com",
    "headquarters": "Singapore",
    "year_founded": 1997,
    "employee_count_range": "20000+",
    "funding_stage": "Public (SGX: S63)",
    "total_funding": "N/A (Public company, FY2024 revenue ~SGD 10.1B)",
    "is_startup": False,
    "is_ai_first": False,
    "region": "Asia-Pacific",
    "mdr_service_type": "Extended MDR",
    "ir_focus_type": "Assistance Component",
    "target_market": "Government & Enterprise",
    "primary_capability": "TDR",
    "description": "Singapore-headquartered global technology, defence, and engineering conglomerate (SGX: S63) with 25+ years of cybersecurity experience. Through its Cyber division, ST Engineering delivers a comprehensive suite of MDR, IT/OT SOC solutions, AI-enabled threat intelligence, and managed security services. Has designed and operated 20+ SOCs across governments, Critical Information Infrastructure (CII), and enterprises spanning aviation, banking, energy, government, healthcare, transport, maritime, and water sectors. Wholly owned subsidiary D'Crypt develops advanced high-security cryptographic products. Offerings include Agentic AI SOC for autonomous multi-agent security operations, AICYMO for OT cyber monitoring with digital twins, AI-enabled CTI with multilingual NLP, and AGIL Trust/SecureAI for deepfake detection and AI security.",
    "key_differentiators": "20+ SOC deployments across IT/OT/cloud for CII and government; Agentic AI SOC with autonomous multi-agent orchestration; AICYMO digital twin OT monitoring; domain-specific AI with custom NLP-powered CTI platform; D'Crypt cryptographic subsidiary with quantum-safe capabilities; deep defence/public security expertise; strong Singapore government ecosystem alignment; multi-sector CII experience across APAC",
    "product_names": [
        "ST Engineering MDR",
        "Agentic AI SOC",
        "AICYMO",
        "AI-Enabled Threat Elimination and Response (AETER)",
        "Cyber Threat Intelligence Platform",
        "Cloud Security Monitoring",
        "Supply Chain Monitoring",
        "AGIL SecureAI",
        "AGIL Trust",
        "NetCrypt",
        "CyberTransporter",
        "SCA-LE"
    ],
    "telemetry_sources": ["Endpoint", "Network", "Cloud", "OT/IoT", "Identity", "SCADA"],
    "mitre_coverage": "MITRE ATT&CK integration documented via Agentic AI SOC chat assistant that provides enriched investigative insights from MITRE ATT&CK framework",
    "pillar_scores": pillar_scores,
    "sub_pillar_scores_current": sub_pillar_scores_current,
    "sub_pillar_schema_labels": sub_pillar_schema_labels,
    "capability_coverage": capability_coverage,
    "capability_coverage_count": len(capability_coverage),
    "sub_pillar_evidence": sub_pillar_evidence,
    "research_status": "completed",
    "capability_analysis_source": "https://www.stengg.com/en/cybersecurity",
}

# ── Pricing data ──
pricing_entry = {
    "vendor": "ST Engineering",
    "website": "https://www.stengg.com",
    "headquarters": "Singapore",
    "region": "Asia-Pacific",
    "mdr_service_type": "Extended MDR",
    "target_market": "Government & Enterprise",
    "pricing_model_type": "Opaque/Custom",
    "pricing_dimension_scores": {
        "PRC-SUB": 2,   # Services exist but pricing is entirely opaque — no public tiers or structure
        "PRC-USG": 1,   # No usage-based pricing documented
        "PRC-FIX": 2,   # Fixed delivery likely for SOC build projects (20+ SOCs built)
        "PRC-SUC": 1,   # No success/outcome fee model documented
        "PRC-COM": 2,   # Multiple service components (MDR, cloud, supply chain) suggest some composability
        "PRC-OUT": 1,   # No pricing-to-outcomes alignment documented
    },
    "pricing_overall_score": 1.5,
    "outcome_maturity_rating": 1,
    "pricing_evidence": {
        "PRC-SUB": {
            "source_urls": [URLS["services"], URLS["aeter"]],
            "excerpts": [{"url": URLS["aeter"], "excerpt": EXCERPTS["aeter_main"], "matched_terms": ["MDR", "affordable", "SME"], "relevance_score": 5}],
            "notes": "AETER marketed as affordable for SMEs, suggesting subscription model exists. However, no pricing tiers, rate cards, or subscription structures are published publicly. Typical government/CII pricing is through custom RFP processes."
        },
        "PRC-USG": {
            "source_urls": [URLS["services"]],
            "excerpts": [],
            "notes": "No usage-based pricing components documented. Government and enterprise contracts typically use fixed or subscription models."
        },
        "PRC-FIX": {
            "source_urls": [URLS["solutions"], URLS["it_soc"]],
            "excerpts": [{"url": URLS["it_soc"], "excerpt": EXCERPTS["soc_future_ready"], "matched_terms": ["SOC", "integration", "architecture"], "relevance_score": 5}],
            "notes": "20+ SOC build projects imply significant fixed delivery pricing for SOC architecture and implementation. IT SOC and OT SOC solutions would involve fixed-fee project delivery. No published pricing."
        },
        "PRC-SUC": {
            "source_urls": [URLS["services"]],
            "excerpts": [],
            "notes": "No success fees, outcome bonuses, or fees-at-risk documented. Government contract models typically do not include success-based pricing."
        },
        "PRC-COM": {
            "source_urls": [URLS["services"]],
            "excerpts": [{"url": URLS["services"], "excerpt": "Managed Detection and Response, Supply Chain Monitoring, Cloud Security Monitoring, AI-Enabled Threat Elimination and Response", "matched_terms": ["MDR", "monitoring", "AI"], "relevance_score": 5}],
            "notes": "Multiple distinct managed services (MDR, cloud, supply chain, AETER) suggest modular offerings that could be composed. However, no documented pricing composability or a la carte selection."
        },
        "PRC-OUT": {
            "source_urls": [URLS["services"]],
            "excerpts": [],
            "notes": "No pricing-to-outcomes alignment documented. No published KPI-linked pricing or outcome-based commercial models."
        },
    },
}

# ── Helper: load/save JSON ──
def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Saved {os.path.basename(path)}")

# ── Add to MDR vendor files ──
MDR_FILES = [
    "MDR Services Vendor 1-0 Seed.json",
    "MDR Services Vendor 2-0 Researched.json",
    "MDR Services Vendor 2-1 Consolidated.json",
]
MDR_PRICING_FILES = [
    "MDR Services Vendor Pricing 1-0 Seed.json",
    "MDR Services Vendor Pricing 2-0 Researched.json",
    "MDR Services Vendor Pricing 2-1 AI Enriched.json",
]

print("═══ Adding ST Engineering to MDR vendor files ═══\n")

for fname in MDR_FILES:
    fpath = os.path.join(BASE, fname)
    if not os.path.exists(fpath):
        print(f"  ⚠ {fname} not found, skipping")
        continue
    data = load_json(fpath)

    # Determine structure: {vendors: [...]} or bare list
    if isinstance(data, dict) and "vendors" in data:
        vendors = data["vendors"]
    elif isinstance(data, list):
        vendors = data
    else:
        print(f"  ⚠ {fname} unexpected structure, skipping")
        continue

    # Check if already present
    existing = [v for v in vendors if v.get("vendor", "").lower() == "st engineering"]
    if existing:
        print(f"  ⚠ {fname}: ST Engineering already present, skipping")
        continue

    # For 1-0 Seed, use a reduced entry (fewer fields)
    if "1-0" in fname:
        seed_entry = {
            "vendor": vendor_entry["vendor"],
            "website": vendor_entry["website"],
            "headquarters": vendor_entry["headquarters"],
            "year_founded": vendor_entry["year_founded"],
            "employee_count_range": vendor_entry["employee_count_range"],
            "funding_stage": vendor_entry["funding_stage"],
            "total_funding": vendor_entry["total_funding"],
            "is_startup": vendor_entry["is_startup"],
            "is_ai_first": vendor_entry["is_ai_first"],
            "region": vendor_entry["region"],
            "mdr_service_type": vendor_entry["mdr_service_type"],
            "ir_focus_type": vendor_entry["ir_focus_type"],
            "target_market": vendor_entry["target_market"],
            "primary_capability": vendor_entry["primary_capability"],
            "description": vendor_entry["description"],
            "key_differentiators": vendor_entry["key_differentiators"],
            "product_names": vendor_entry["product_names"],
            "telemetry_sources": vendor_entry["telemetry_sources"],
            "mitre_coverage": vendor_entry["mitre_coverage"],
            "pillar_scores": vendor_entry["pillar_scores"],
            "sub_pillar_scores_current": vendor_entry["sub_pillar_scores_current"],
            "sub_pillar_schema_labels": vendor_entry["sub_pillar_schema_labels"],
            "capability_coverage": vendor_entry["capability_coverage"],
            "capability_coverage_count": vendor_entry["capability_coverage_count"],
        }
        vendors.append(seed_entry)
    else:
        vendors.append(copy.deepcopy(vendor_entry))

    save_json(fpath, data)
    print(f"  {fname}: {len(vendors)} vendors")

print()
print("═══ Adding ST Engineering to MDR pricing files ═══\n")

for fname in MDR_PRICING_FILES:
    fpath = os.path.join(BASE, fname)
    if not os.path.exists(fpath):
        print(f"  ⚠ {fname} not found, skipping")
        continue
    data = load_json(fpath)

    if isinstance(data, dict) and "vendors" in data:
        vendors = data["vendors"]
    elif isinstance(data, list):
        vendors = data
    else:
        print(f"  ⚠ {fname} unexpected structure, skipping")
        continue

    existing = [v for v in vendors if v.get("vendor", "").lower() == "st engineering"]
    if existing:
        print(f"  ⚠ {fname}: ST Engineering already present, skipping")
        continue

    vendors.append(copy.deepcopy(pricing_entry))
    save_json(fpath, data)
    print(f"  {fname}: {len(vendors)} vendors")

# ── Summary ──
print()
print("═══ Scoring Summary ═══")
print(f"  Vendor: ST Engineering (Singapore)")
print(f"  MDR Service Type: Extended MDR")
print(f"  Coverage: {len(capability_coverage)}/32 sub-pillars ({round(len(capability_coverage)/32*100)}%)")
for p in PILLAR_IDS:
    print(f"    {p}: {pillar_scores[p]}")
print(f"  Pricing Model: Opaque/Custom (Score: 1.5)")
print(f"\n✅ Done. ST Engineering added to all MDR vendor and pricing files.")
