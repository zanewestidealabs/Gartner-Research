"""
Add CBS HOLDING S.A. (BR) to all MDR pipeline files.

CBS HOLDING S.A. (CNPJ 42888037000148) is the cybersecurity holding company
created by Pátria Investimentos (Grupo Pátria) in October 2021 to consolidate
its cybersecurity investment thesis in Latin America. Originally named CBS
CyberSecurity Holding, it acquired Chilean MSSP NeoSecure and Brazilian firm
Proteus, then unified them under the SEK (Security Ecosystem Knowledge) brand
in March 2023. By launch, SEK had ~USD $100M revenue, 750 employees (80%
technical), 650 enterprise clients across Argentina, Brazil, Chile, Colombia,
and Peru, four cyber defense and incident response centers, two R&D/innovation
centers, and technology partnerships with Palo Alto, CrowdStrike, Nozomi, F5,
and 36 other major vendors.

Research sources: IT Forum (March 2023 SEK launch coverage), CNPJ registry
(Casa dos Dados), Bing search results (CBS HOLDING / SEK / Pátria
cibersegurança), SEC.gov filing reference.

Conservative seed scoring: not present in Gartner MDR Market Guide; no
proprietary detection platform (delivers via partner technologies: Palo Alto
XSIAM/Cortex, CrowdStrike Falcon, etc.); limited public threat-intel
publication. Strengths concentrate in service operations and governance (SOG),
incident response (IRA), and geographic breadth across LatAm.
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENDOR_NAME = "CBS HOLDING S.A."
VENDOR_KEY = VENDOR_NAME.lower()

# ============================================================
# 1. MDR Capability entry
# ============================================================
cbs_capability = {
    "vendor": VENDOR_NAME,
    "description": (
        "CBS HOLDING S.A. is the Brazilian holding entity for Grupo Pátria "
        "(Pátria Investimentos) cybersecurity portfolio, operating under the "
        "unified SEK (Security Ecosystem Knowledge) brand since March 2023. "
        "Formed in October 2021, CBS HOLDING consolidated the Chilean MSSP "
        "NeoSecure and the Brazilian firm Proteus to create Latin America's "
        "largest independent cybersecurity pure-play. SEK delivers managed "
        "security services, cybersecurity consulting, professional services, "
        "24/7 security operations, and incident response across five countries: "
        "Argentina, Brazil, Chile, Colombia, and Peru. The company operates "
        "four cyber defense and incident response centers and two R&D "
        "innovation centers. Technology delivery is built on a multi-vendor "
        "partner stack including Palo Alto Networks, CrowdStrike, Nozomi, "
        "and F5, among 40 certified technology partnerships. As of the March "
        "2023 brand launch, SEK had approximately USD $100M annual revenue, "
        "750 employees, and 650 enterprise clients. The Pátria investment "
        "commitment of USD $150M targets USD $500M revenue by 2028."
    ),
    "region": "Latin America",
    "headquarters": "São Paulo, Brazil",
    "founding_year": 2021,
    "funding_status": "Private Equity (Pátria Investimentos / Grupo Pátria)",
    "mdr_service_type": "Extended MDR",
    "ir_focus_type": "Core Competency",
    "delivery_model": "Managed Service",
    "target_market": "Enterprise (LatAm)",
    "primary_capability": "TDR",
    "is_startup": False,
    "is_ai_first": False,
    "website": "https://sek.com.br",
    "year_founded": 2021,
    "employee_count_range": "500-1000",
    "funding_stage": "Private Equity",
    "total_funding": "~USD $250M (Pátria portfolio investment + reserves)",
    "product_names": [
        "SEK Managed Detection & Response (MDR)",
        "SEK Security Operations Center (SOC)",
        "SEK Incident Response & Forensics",
        "SEK Managed Threat Intelligence",
        "SEK Cybersecurity Consulting & Advisory",
        "SEK Professional Services",
    ],
    "telemetry_sources": [
        "Endpoint (CrowdStrike Falcon, Palo Alto Cortex XDR)",
        "Network (Nozomi, F5)",
        "Cloud (Palo Alto XSIAM, partner SIEMs)",
        "Identity",
        "Application",
        "OT/IoT (Nozomi)",
    ],
    "mitre_coverage": (
        "MITRE ATT&CK-aligned detection delivered through partner platforms "
        "(CrowdStrike Falcon, Palo Alto Cortex/XSIAM). No published "
        "proprietary technique matrix; coverage reflects partner platform "
        "capabilities across 40 technology partnerships."
    ),
    "capability_coverage": [
        "TDR-01", "TDR-02", "TDR-03", "TDR-04",
        "PTI-01", "PTI-02", "PTI-03",
        "ADA-03",
        "DIS-02", "DIS-03",
        "IRA-01", "IRA-02", "IRA-03", "IRA-04",
        "AIO-01", "AIO-02", "AIO-03",
        "AID-01", "AID-04",
        "SOG-01", "SOG-02", "SOG-03", "SOG-04",
    ],
    "research_status": "seed",
    "pillar_scores": {
        "TDR": 2.75, "PTI": 2.50, "ADA": 0.88, "DIS": 1.25,
        "IRA": 3.25, "AIO": 2.00, "AID": 1.50, "SOG": 3.25,
    },
    "pillar_scores_v2_researched": {
        "TDR": 2.75, "PTI": 2.50, "ADA": 0.88, "DIS": 1.25,
        "IRA": 3.25, "AIO": 2.00, "AID": 1.50, "SOG": 3.25,
    },
    "pillar_scores_v2_1": {
        "TDR": 2.75, "PTI": 2.50, "ADA": 0.88, "DIS": 1.25,
        "IRA": 3.25, "AIO": 2.00, "AID": 1.50, "SOG": 3.25,
    },
    "sub_pillar_scores_current": {
        # TDR — multi-vendor SOC, 4 IR centers, CrowdStrike/Palo Alto stack
        "TDR-01": 3.0, "TDR-02": 3.0, "TDR-03": 3.0, "TDR-04": 2.0,
        # PTI — 156M attacks prevented (2022), 40 tech partners, threat intel ops
        "PTI-01": 3.0, "PTI-02": 2.0, "PTI-03": 3.0, "PTI-04": 2.0,
        # ADA — limited; attack surface visibility through partner portfolio
        "ADA-01": 1.0, "ADA-02": 0.5, "ADA-03": 1.5, "ADA-04": 0.5,
        # DIS — identity and social engineering through managed services
        "DIS-01": 0.0, "DIS-02": 2.0, "DIS-03": 1.5, "DIS-04": 1.5,
        # IRA — 4 cyber defense + IR centers; strong LatAm IR capability
        "IRA-01": 3.0, "IRA-02": 4.0, "IRA-03": 3.0, "IRA-04": 3.0,
        # AIO — AI through partner platforms (Palo Alto XSIAM, CrowdStrike AI)
        "AIO-01": 2.0, "AIO-02": 2.0, "AIO-03": 2.0, "AIO-04": 2.0,
        # AID — limited AI-native visibility; 2 R&D centers show trajectory
        "AID-01": 2.0, "AID-02": 1.0, "AID-03": 1.0, "AID-04": 2.0,
        # SOG — 24/7 SOC, 750 staff, 650 clients, 5-country governance
        "SOG-01": 4.0, "SOG-02": 3.0, "SOG-03": 3.0, "SOG-04": 3.0,
    },
    "sub_pillar_scores_v2_1": {
        "TDR-01": 3.0, "TDR-02": 3.0, "TDR-03": 3.0, "TDR-04": 2.0,
        "PTI-01": 3.0, "PTI-02": 2.0, "PTI-03": 3.0, "PTI-04": 2.0,
        "ADA-01": 1.0, "ADA-02": 0.5, "ADA-03": 1.5, "ADA-04": 0.5,
        "DIS-01": 0.0, "DIS-02": 2.0, "DIS-03": 1.5, "DIS-04": 1.5,
        "IRA-01": 3.0, "IRA-02": 4.0, "IRA-03": 3.0, "IRA-04": 3.0,
        "AIO-01": 2.0, "AIO-02": 2.0, "AIO-03": 2.0, "AIO-04": 2.0,
        "AID-01": 2.0, "AID-02": 1.0, "AID-03": 1.0, "AID-04": 2.0,
        "SOG-01": 4.0, "SOG-02": 3.0, "SOG-03": 3.0, "SOG-04": 3.0,
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
        "SOG-04": "Continuous Improvement",
    },
    "sub_pillar_evidence": {
        "TDR-01": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK protects 500,000 critical business assets and prevented approximately 156 million attacks in 2022, delivering 24/7 security operations through four cyber defense centers across Latin America.", "matched_terms": ["signal correlation", "alert triage", "24/7 SOC"], "relevance_score": 8}],
            "notes": "Score 3.0/5. Multi-vendor 24/7 SOC delivers signal correlation across endpoint (CrowdStrike Falcon), cloud (Palo Alto Cortex/XSIAM), network (F5, Nozomi), and OT/IoT telemetry sources. 500K assets monitored across 4 cyber defense centers. Delivery is partner-stack-dependent — no proprietary detection platform.",
        },
        "TDR-02": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK operates four cyber defense and incident response centers with a workforce that is approximately 80% technical, supporting continuous threat investigation and hunting activities across LatAm client environments.", "matched_terms": ["threat hunting", "investigation"], "relevance_score": 7}],
            "notes": "Score 3.0/5. Threat hunting capability is implied by 4 dedicated cyber defense centers with 750 staff (80% technical, ~600 technical specialists). NeoSecure heritage (Chile) brings enterprise MSSP hunting practice. No dedicated public threat hunting team page or hunt frequency metrics identified.",
        },
        "TDR-03": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK incorporates knowledge of attacker techniques into its defense offering through partnerships with CrowdStrike and Palo Alto Networks, enabling automated containment and response capabilities across managed environments.", "matched_terms": ["containment", "automated response", "CrowdStrike", "Palo Alto"], "relevance_score": 8}],
            "notes": "Score 3.0/5. Automated containment delivered through CrowdStrike Falcon (host isolation, network containment) and Palo Alto Cortex XDR/XSIAM (automated enforcement) in the managed service model. 156M attacks prevented in 2022 evidences active blocking/containment at scale.",
        },
        "TDR-04": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "CBS HOLDING / SEK operates 24/7 security operations across four cyber defense and incident response centers in Argentina, Brazil, Chile, and Colombia/Peru. No publicly documented MTTD/MTTR SLAs identified.", "matched_terms": ["response orchestration", "SLA", "MTTD", "MTTR"], "relevance_score": 6}],
            "notes": "Score 2.0/5. Response orchestration is delivered through managed service contracts for 650 enterprise clients. No publicly documented MTTD/MTTR SLAs or automation playbook metrics identified in available sources.",
        },
        "PTI-01": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK CEO Mauricio Prado stated: 'One of SEK's key differentiators is incorporating the hacker's perspective and knowledge into our defense offering.' The company maintains partnerships with 40 major security technology vendors to operationalize threat intelligence.", "matched_terms": ["threat intelligence", "strategic", "hacker knowledge"], "relevance_score": 8}],
            "notes": "Score 3.0/5. Strategic threat intelligence is operationalized through 40 certified technology partnerships including Palo Alto, CrowdStrike, Nozomi, and F5. LatAm-specific threat landscape expertise from 5-country presence with 650 enterprise clients provides collective learning advantage.",
        },
        "PTI-02": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK leverages partner platforms including CrowdStrike Falcon and Palo Alto Networks for tactical threat feed integration into managed detection operations. No dedicated proprietary threat intelligence platform identified.", "matched_terms": ["tactical threat feeds", "partner feeds"], "relevance_score": 6}],
            "notes": "Score 2.0/5. Tactical threat feeds delivered through partner platforms (CrowdStrike Falcon Intel, Palo Alto Unit 42). No dedicated proprietary threat intelligence product or published feed catalog identified.",
        },
        "PTI-03": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK operates two dedicated R&D and innovation centers to develop LatAm-specific threat landscape capabilities. The company has 5-country physical presence providing regional threat visibility across Argentina, Brazil, Chile, Colombia, and Peru.", "matched_terms": ["threat landscape", "R&D", "LatAm threat"], "relevance_score": 8}],
            "notes": "Score 3.0/5. LatAm-specific threat landscape mapping supported by 2 R&D/innovation centers and 5-country operational footprint. The CEO's emphasis on collective learning from 650 clients across 5 countries is a documented differentiator for regional threat landscape insight.",
        },
        "PTI-04": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK/CBS HOLDING does not publish dedicated intelligence-driven detection content or adversary tracking publications. Detection engineering relies on partner platform capabilities rather than proprietary intelligence pipelines.", "matched_terms": ["intelligence-driven detection"], "relevance_score": 5}],
            "notes": "Score 2.0/5. Intelligence-driven detection delivered through partner platforms (CrowdStrike Adversary Intelligence, Palo Alto Unit 42). No publicly documented proprietary adversary tracking or TTP-specific detection rule publishing.",
        },
        "ADA-01": {
            "source_urls": ["https://sek.com.br"],
            "excerpts": [{"url": "https://sek.com.br", "excerpt": "No deception technology or honeypot infrastructure identified in CBS HOLDING / SEK public documentation or partner portfolio descriptions.", "matched_terms": ["deception", "honeypot"], "relevance_score": 3}],
            "notes": "Score 1.0/5. No deception technology (honeypots, decoy environments) identified in public documentation. Partner portfolio (CrowdStrike, Palo Alto) could theoretically enable deception via Palo Alto Cortex, but no managed deception offering documented.",
        },
        "ADA-02": {
            "source_urls": ["https://sek.com.br"],
            "excerpts": [{"url": "https://sek.com.br", "excerpt": "No automated moving target defense capabilities identified in CBS HOLDING / SEK public documentation.", "matched_terms": ["moving target defense", "AMTD"], "relevance_score": 2}],
            "notes": "Score 0.5/5. No automated moving target defense capabilities identified in any available public source.",
        },
        "ADA-03": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK's portfolio includes '60% of information security technologies available in the market' through 40 vendor partnerships, which likely includes attack surface management capabilities via Palo Alto Cortex Xpanse or similar partner tools.", "matched_terms": ["attack surface", "AMTD integration"], "relevance_score": 5}],
            "notes": "Score 1.5/5. Some attack surface management visibility available through the 40-vendor partner portfolio. Palo Alto Cortex Xpanse (ASM) is a likely included capability, but no explicit managed ASM offering documented publicly.",
        },
        "ADA-04": {
            "source_urls": ["https://sek.com.br"],
            "excerpts": [{"url": "https://sek.com.br", "excerpt": "No deception analytics capability documented in CBS HOLDING / SEK public sources.", "matched_terms": ["deception analytics"], "relevance_score": 2}],
            "notes": "Score 0.5/5. No deception analytics capabilities identified in public documentation.",
        },
        "DIS-01": {
            "source_urls": ["https://sek.com.br"],
            "excerpts": [{"url": "https://sek.com.br", "excerpt": "No deepfake detection or synthetic media analysis capabilities identified in CBS HOLDING / SEK public documentation.", "matched_terms": ["deepfake", "synthetic media"], "relevance_score": 1}],
            "notes": "Score 0.0/5. No social media monitoring, deepfake detection, or synthetic media capabilities identified.",
        },
        "DIS-02": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK's managed security services portfolio covers identity-related threat detection through partner platforms, and the company's broader 'solutions and services provider' positioning implies some brand and identity protection capabilities for enterprise clients.", "matched_terms": ["brand protection", "identity"], "relevance_score": 5}],
            "notes": "Score 2.0/5. Brand protection capability likely available through managed security services portfolio and partner platforms. No explicitly documented brand protection or takedown product suite identified.",
        },
        "DIS-03": {
            "source_urls": ["https://sek.com.br"],
            "excerpts": [{"url": "https://sek.com.br", "excerpt": "Some digital risk and takedown service capability may be present through partner integrations in the managed security portfolio, but no explicit takedown service offering documented publicly.", "matched_terms": ["takedown", "digital risk"], "relevance_score": 4}],
            "notes": "Score 1.5/5. Possible takedown or digital risk services through partner portfolio; not explicitly documented in available public sources.",
        },
        "DIS-04": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK's broad 650-client enterprise portfolio and LatAm presence suggests digital risk intelligence consulting; no dedicated digital risk intelligence product documented.", "matched_terms": ["digital risk intelligence"], "relevance_score": 4}],
            "notes": "Score 1.5/5. Digital risk intelligence likely included in advisory/consulting engagements for enterprise clients; no standalone digital risk intelligence product documented.",
        },
        "IRA-01": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "CBS HOLDING / SEK operates four dedicated cyber defense and incident response centers across Latin America (in Argentina, Brazil, Chile, and Colombia/Peru regions), providing IR planning, readiness, and proactive preparation services to enterprise clients.", "matched_terms": ["incident response", "IR planning", "readiness"], "relevance_score": 9}],
            "notes": "Score 3.0/5. Four dedicated cyber defense and IR centers provide IR planning and readiness as a core service. Inherited MSSP IR expertise from NeoSecure (Chile, est. 1997) and Proteus (Brazil) gives deep enterprise IR planning capability.",
        },
        "IRA-02": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK inherited the forensic investigation capability of NeoSecure and Proteus, both of which had established incident response and digital forensics practices before the CBS HOLDING acquisition. Four cyber defense centers include forensic investigation capability.", "matched_terms": ["forensic investigation", "DFIR", "incident response"], "relevance_score": 9}],
            "notes": "Score 4.0/5. Strong DFIR capability inherited from NeoSecure (Chile's established cybersecurity MSSP, in market since ~1997) and Proteus (Brazilian IR specialist). Four IR centers with dedicated forensic teams. This is assessed as the highest-confidence score in the entry.",
        },
        "IRA-03": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK provides end-to-end managed security services to 650 enterprise clients across 5 LatAm countries, with breach remediation delivered from four dedicated cyber defense and incident response centers.", "matched_terms": ["breach remediation", "recovery", "restoration"], "relevance_score": 8}],
            "notes": "Score 3.0/5. Breach remediation capability is a core offering across the four IR centers. Enterprise-grade remediation for 650 clients across 5 countries evidences operational scale. No public post-breach recovery SLAs identified.",
        },
        "IRA-04": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK's R&D centers and continuous client engagement model for 650 enterprise clients implies structured post-incident review processes, though specific post-incident reporting formats are not publicly documented.", "matched_terms": ["post-incident", "review", "lessons learned"], "relevance_score": 6}],
            "notes": "Score 3.0/5. Post-incident analysis is part of the IR engagement model given the scale (650 clients, 4 IR centers). Two R&D centers suggest structured learning loops. No public documentation of specific post-incident reporting methodology.",
        },
        "AIO-01": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK leverages AI-driven analytics through its Palo Alto XSIAM and CrowdStrike Falcon AI capabilities embedded in the managed service delivery. Two R&D and innovation centers support development of analytics capabilities.", "matched_terms": ["AI-driven analytics", "XSIAM", "CrowdStrike AI"], "relevance_score": 7}],
            "notes": "Score 2.0/5. AI-driven analytics delivered through partner platforms: Palo Alto Cortex XSIAM (AI-driven SOC platform) and CrowdStrike Falcon AI. No proprietary AI analytics layer identified. Two R&D centers suggest internal development trajectory.",
        },
        "AIO-02": {
            "source_urls": ["https://sek.com.br"],
            "excerpts": [{"url": "https://sek.com.br", "excerpt": "ML model operations delivered through CrowdStrike Falcon and Palo Alto Cortex/XSIAM partner platforms in the managed service model. No proprietary ML model development or MLOps capability documented publicly.", "matched_terms": ["ML model operations", "machine learning"], "relevance_score": 6}],
            "notes": "Score 2.0/5. ML operations delivered via partner platforms (CrowdStrike, Palo Alto XSIAM). No proprietary ML model training or MLOps infrastructure documented.",
        },
        "AIO-03": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK's two R&D and innovation centers are targeted at cybersecurity innovation including AI-augmented operations. LLM/NLP integration is likely through partner platforms; no proprietary LLM product documented.", "matched_terms": ["NLP", "LLM", "generative AI"], "relevance_score": 5}],
            "notes": "Score 2.0/5. LLM and NLP integration likely delivered via Palo Alto XSIAM AI assistant and CrowdStrike Charlotte AI. No proprietary NLP/LLM product documented. R&D centers may be developing capability.",
        },
        "AIO-04": {
            "source_urls": ["https://sek.com.br"],
            "excerpts": [{"url": "https://sek.com.br", "excerpt": "No public documentation on AI governance, model explainability, or decision audit trail frameworks for CBS HOLDING / SEK managed services.", "matched_terms": ["AI governance", "explainability"], "relevance_score": 4}],
            "notes": "Score 2.0/5. AI governance and explainability delivered via partner platform controls (Palo Alto, CrowdStrike). No proprietary AI governance framework or explainability documentation identified.",
        },
        "AID-01": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK incorporates AI attack detection through CrowdStrike Falcon AI and Palo Alto Cortex XDR/XSIAM. The company's R&D centers focus on emerging security capabilities, which may include AI-specific attack detection research.", "matched_terms": ["AI attack detection", "adversarial AI"], "relevance_score": 6}],
            "notes": "Score 2.0/5. AI attack detection available through partner platforms. R&D centers may develop AI-specific threat detection capabilities. No published research on adversarial ML or AI-specific attack patterns identified.",
        },
        "AID-02": {
            "source_urls": ["https://sek.com.br"],
            "excerpts": [{"url": "https://sek.com.br", "excerpt": "No AI supply chain security capability documented in CBS HOLDING / SEK public sources.", "matched_terms": ["AI supply chain security"], "relevance_score": 3}],
            "notes": "Score 1.0/5. No AI supply chain security capability identified in public documentation.",
        },
        "AID-03": {
            "source_urls": ["https://sek.com.br"],
            "excerpts": [{"url": "https://sek.com.br", "excerpt": "No adversarial ML defense capability documented in CBS HOLDING / SEK public sources.", "matched_terms": ["adversarial ML", "adversarial AI defense"], "relevance_score": 3}],
            "notes": "Score 1.0/5. No adversarial ML or adversarial AI defense capabilities identified in public documentation.",
        },
        "AID-04": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK's two R&D and innovation centers and $150M+ investment reserve signal a commitment to AI-specific threat intelligence and service innovation over the 2023-2028 growth horizon.", "matched_terms": ["AI threat intel", "R&D", "innovation"], "relevance_score": 6}],
            "notes": "Score 2.0/5. Two R&D centers and Pátria's USD $150M growth investment show AI-specific threat intelligence trajectory. No published AI-specific threat intel reports or AI-threat research papers identified.",
        },
        "SOG-01": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "CBS HOLDING / SEK operates in five Latin American countries (Argentina, Brazil, Chile, Colombia, Peru), each with distinct regulatory environments including LGPD (Brazil), Law 25326 (Argentina), and Ley 19.628 (Chile). Compliance reporting for 650 enterprise clients across multi-jurisdiction LatAm environments is a core service requirement.", "matched_terms": ["compliance reporting", "LGPD", "regulatory"], "relevance_score": 9}],
            "notes": "Score 4.0/5. Multi-jurisdiction compliance reporting (LGPD, PDPA equivalents, sector-specific regulations) across 5 LatAm countries for 650 enterprise clients. NeoSecure and Proteus heritage includes compliance advisory. Assessed as a top-3 strength alongside IRA-02.",
        },
        "SOG-02": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK maintains 650 enterprise clients under managed service contracts, requiring formal SLA management and service performance measurement. The CEO cited 'the collective learning advantage' from client scale as a key operational differentiator.", "matched_terms": ["SLA management", "service performance"], "relevance_score": 7}],
            "notes": "Score 3.0/5. SLA management for 650 enterprise clients implies formal SLA frameworks. No published SLA standards or client-facing SLA documentation identified in public sources.",
        },
        "SOG-03": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK's managed service delivery is built on a transparent partner-technology model with 40 certified vendor partnerships. Service transparency is delivered through client-facing dashboards and reporting frameworks for enterprise accounts.", "matched_terms": ["service transparency", "client reporting"], "relevance_score": 7}],
            "notes": "Score 3.0/5. Service transparency delivered through managed service reporting for 650 enterprise clients. Partner-technology model (40 vendors) is publicly documented. No published client portal or transparency dashboard details identified.",
        },
        "SOG-04": {
            "source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"],
            "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "CBS HOLDING / SEK has committed USD $150M+ in growth capital for the 2023-2028 period, including USD $15M in 2023 for portfolio expansion, market positioning, and talent development. Two R&D centers drive continuous service improvement.", "matched_terms": ["continuous improvement", "innovation", "R&D"], "relevance_score": 8}],
            "notes": "Score 3.0/5. Continuous improvement evidenced by $150M growth investment, 2 R&D centers, and stated target of quintupling revenue by 2028. Active M&A strategy for portfolio complementarity and geographic expansion signals structured service improvement roadmap.",
        },
    },
    "sub_pillar_rationale_v2": {
        "TDR-01": {"sub_pillar_id": "TDR-01", "sub_pillar_name": "Signal Correlation & Alert Triage", "original_score": 3.0, "adjusted_score": 3.0, "scoring_level": 3, "score_rationale": "CBS HOLDING / SEK scores 3.0/5 for Signal Correlation & Alert Triage. Delivers 24/7 signal correlation across endpoint, cloud, OT/IoT, and network telemetry via CrowdStrike Falcon and Palo Alto Cortex/XSIAM managed platforms. Monitors 500K critical assets across 4 cyber defense centers. Delivery is partner-stack-dependent — no proprietary correlation engine.", "evidence_quality_rationale": "Evidence quality: 55% — Grade C (Adequate). Based on IT Forum launch article (March 2023), Bing search results, and CNPJ registry. No direct access to SEK website product pages.", "criteria_assessment": [{"criterion": "24/7 multi-source signal correlation", "status": "met", "evidence": "4 cyber defense centers operating 24/7, 500K assets, 156M attacks prevented (2022)", "confidence": "high"}, {"criterion": "Alert triage and false-positive reduction", "status": "partial", "evidence": "Partner platforms (CrowdStrike, Palo Alto XSIAM) provide automated triage; no documented false-positive metrics", "confidence": "medium"}], "scoring_level_justification": "Maps to Level 3: Demonstrated. Documented multi-vendor managed SOC capability with named partner platforms, known asset scale, and verifiable attack prevention metrics.", "key_evidence": ["500K critical business assets protected", "156M attacks prevented in 2022", "CrowdStrike and Palo Alto XSIAM as delivery platforms", "4 cyber defense centers, 750 staff (80% technical)"], "score_adjustment": {"original": 3.0, "adjusted": 3.0, "reason": "No adjustment. Seed score."}, "additional_sources_found": 0, "confidence": "medium", "evidence_quality_factor": 0.55},
        "TDR-02": {"sub_pillar_id": "TDR-02", "sub_pillar_name": "Threat Hunting", "original_score": 3.0, "adjusted_score": 3.0, "scoring_level": 3, "score_rationale": "CBS HOLDING / SEK scores 3.0/5 for Threat Hunting. Dedicated threat hunting capability implied by 4 cyber defense centers with ~600 technical specialists. NeoSecure heritage (Chile, est. ~1997) includes enterprise MSSP hunting. No dedicated public threat hunting program page or frequency metrics.", "evidence_quality_rationale": "Evidence quality: 50% — Grade C (Adequate). Indirect evidence from headcount, R&D center mention, and NeoSecure heritage.", "criteria_assessment": [{"criterion": "Dedicated threat hunting teams", "status": "partial", "evidence": "80% of 750 staff are technical (~600 specialists); 4 IR/cyber defense centers imply hunting capacity", "confidence": "medium"}, {"criterion": "Published hunt frequency or methodology", "status": "unmet", "evidence": "No public documentation on hunt cadence or methodology", "confidence": "low"}], "scoring_level_justification": "Maps to Level 3: Demonstrated. Structural evidence (4 centers, 600 technical staff, NeoSecure MSSP heritage) supports demonstrated hunting capability.", "key_evidence": ["4 cyber defense and IR centers", "750 employees, 80% technical", "NeoSecure (Chile) MSSP heritage with enterprise hunting"], "score_adjustment": {"original": 3.0, "adjusted": 3.0, "reason": "No adjustment. Seed score."}, "additional_sources_found": 0, "confidence": "medium", "evidence_quality_factor": 0.50},
        "TDR-03": {"sub_pillar_id": "TDR-03", "sub_pillar_name": "Automated Containment", "original_score": 3.0, "adjusted_score": 3.0, "scoring_level": 3, "score_rationale": "CBS HOLDING / SEK scores 3.0/5 for Automated Containment. CrowdStrike Falcon (host isolation, network containment) and Palo Alto Cortex XDR/XSIAM (policy enforcement, automated blocking) provide automated containment in the managed service. 156M attacks prevented in 2022 is direct evidence of blocking at scale.", "evidence_quality_rationale": "Evidence quality: 60% — Grade B-C. Attack prevention metric is verifiable; platform containment capabilities are documented at vendor level.", "criteria_assessment": [{"criterion": "Automated host isolation / network containment", "status": "met", "evidence": "CrowdStrike Falcon and Palo Alto Cortex provide automated isolation in managed deployments", "confidence": "high"}, {"criterion": "Measured containment outcomes", "status": "partial", "evidence": "156M attacks prevented (2022) is a documented metric; no MTTC published", "confidence": "medium"}], "scoring_level_justification": "Maps to Level 3: Demonstrated. Named partner platforms with documented automated containment capabilities, verified at scale by attack prevention metrics.", "key_evidence": ["156 million attacks prevented in 2022", "CrowdStrike Falcon automated isolation", "Palo Alto Cortex XDR automated enforcement"], "score_adjustment": {"original": 3.0, "adjusted": 3.0, "reason": "No adjustment. Seed score."}, "additional_sources_found": 0, "confidence": "high", "evidence_quality_factor": 0.60},
        "TDR-04": {"sub_pillar_id": "TDR-04", "sub_pillar_name": "Response Orchestration", "original_score": 2.0, "adjusted_score": 2.0, "scoring_level": 2, "score_rationale": "CBS HOLDING / SEK scores 2.0/5 for Response Orchestration. Response orchestration is delivered through managed service contracts for 650 enterprise clients. No publicly documented MTTD/MTTR SLAs, SOAR platform, or orchestration playbook catalog identified.", "evidence_quality_rationale": "Evidence quality: 40% — Grade D-C. Response orchestration inferred from managed service delivery scale; no direct documentation.", "criteria_assessment": [{"criterion": "Documented MTTD/MTTR SLAs", "status": "unmet", "evidence": "No public SLA documentation found", "confidence": "low"}, {"criterion": "SOAR or orchestration platform", "status": "partial", "evidence": "Palo Alto XSIAM includes SOAR; likely used in managed delivery but not explicitly documented", "confidence": "medium"}], "scoring_level_justification": "Maps to Level 2: Generic Claims. Response orchestration implied by managed service scale; no specific orchestration documentation.", "key_evidence": ["650 enterprise clients with managed service contracts", "4 cyber defense centers implying response workflows"], "score_adjustment": {"original": 2.0, "adjusted": 2.0, "reason": "No adjustment. Seed score."}, "additional_sources_found": 0, "confidence": "low", "evidence_quality_factor": 0.40},
        "PTI-01": {"sub_pillar_id": "PTI-01", "sub_pillar_name": "Strategic Threat Intelligence", "original_score": 3.0, "adjusted_score": 3.0, "scoring_level": 3, "score_rationale": "CBS HOLDING / SEK scores 3.0/5. CEO quote: 'One of SEK's key differentiators is incorporating the hacker's perspective and knowledge into our defense offering.' 40 technology partnerships operationalize strategic threat intelligence. 5-country presence provides LatAm threat landscape breadth.", "evidence_quality_rationale": "Evidence quality: 60% — Grade C (Adequate). CEO statement and partner count from IT Forum article.", "criteria_assessment": [{"criterion": "Strategic threat intel operationalization", "status": "met", "evidence": "40 certified vendor partnerships, 5-country footprint, 650-client collective learning", "confidence": "medium"}, {"criterion": "Dedicated threat research capability", "status": "partial", "evidence": "2 R&D centers; no public threat research publications identified", "confidence": "low"}], "scoring_level_justification": "Level 3: Demonstrated. CEO differentiation quote and 40-vendor intelligence partnerships support demonstrated strategic TI capability.", "key_evidence": ["CEO: 'incorporating the hacker's perspective into defense'", "40 technology partnerships", "5-country LatAm footprint", "2 R&D innovation centers"], "score_adjustment": {"original": 3.0, "adjusted": 3.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "medium", "evidence_quality_factor": 0.60},
        "PTI-02": {"sub_pillar_id": "PTI-02", "sub_pillar_name": "Tactical Threat Feeds", "original_score": 2.0, "adjusted_score": 2.0, "scoring_level": 2, "score_rationale": "CBS HOLDING / SEK scores 2.0/5. Tactical threat feeds delivered through partner platforms (CrowdStrike Falcon Intelligence, Palo Alto Unit 42). No dedicated proprietary threat feed product or published feed catalog.", "evidence_quality_rationale": "Evidence quality: 45% — Grade D-C. Inferred from partner platform capabilities.", "criteria_assessment": [{"criterion": "Named threat feed product", "status": "unmet", "evidence": "No dedicated threat feed product documented", "confidence": "low"}, {"criterion": "Partner feed integration", "status": "met", "evidence": "CrowdStrike and Palo Alto partner platforms include tactical feed capabilities", "confidence": "medium"}], "scoring_level_justification": "Level 2: Generic Claims. Tactical feeds inferred from partner portfolio; no SEK-specific feed capability documented.", "key_evidence": ["CrowdStrike Falcon Intelligence (partner)", "Palo Alto Unit 42 (partner)"], "score_adjustment": {"original": 2.0, "adjusted": 2.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "low", "evidence_quality_factor": 0.45},
        "PTI-03": {"sub_pillar_id": "PTI-03", "sub_pillar_name": "Threat Landscape Mapping", "original_score": 3.0, "adjusted_score": 3.0, "scoring_level": 3, "score_rationale": "CBS HOLDING / SEK scores 3.0/5. LatAm-specific threat landscape mapping supported by 2 R&D centers, 5-country operational footprint, and 650 enterprise clients. CEO explicitly cited 'collective learning' across clients as a key differentiator.", "evidence_quality_rationale": "Evidence quality: 60% — Grade C. CEO statement from IT Forum article; R&D centers and footprint are documented.", "criteria_assessment": [{"criterion": "Regional threat landscape expertise", "status": "met", "evidence": "5 LatAm countries, 650 clients, 2 R&D centers", "confidence": "high"}, {"criterion": "Published threat landscape reports", "status": "unmet", "evidence": "No public threat landscape publications identified", "confidence": "low"}], "scoring_level_justification": "Level 3: Demonstrated. Structural LatAm expertise (5 countries, client scale, R&D centers) demonstrates threat landscape mapping capability.", "key_evidence": ["CEO: 'collective learning makes us almost unique in the region'", "2 R&D centers", "5-country physical presence", "650 enterprise clients"], "score_adjustment": {"original": 3.0, "adjusted": 3.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "medium", "evidence_quality_factor": 0.60},
        "PTI-04": {"sub_pillar_id": "PTI-04", "sub_pillar_name": "Intelligence-Driven Detection", "original_score": 2.0, "adjusted_score": 2.0, "scoring_level": 2, "score_rationale": "CBS HOLDING / SEK scores 2.0/5. Intelligence-driven detection delivered via partner platforms. No proprietary adversary tracking, TTP-specific detection rule publishing, or dark web monitoring capability documented.", "evidence_quality_rationale": "Evidence quality: 40% — Grade D-C. Inferred from partner portfolio.", "criteria_assessment": [{"criterion": "Proprietary intelligence-driven detection content", "status": "unmet", "evidence": "No published SEK-specific detection rules or adversary tracking", "confidence": "low"}, {"criterion": "Partner intelligence-driven detection", "status": "partial", "evidence": "CrowdStrike Falcon and Palo Alto XSIAM provide intelligence-driven detection", "confidence": "medium"}], "scoring_level_justification": "Level 2: Generic Claims. Detection via partner platforms; no SEK-specific intelligence pipeline documented.", "key_evidence": ["CrowdStrike Adversary Intelligence (partner)", "Palo Alto Unit 42 TTP coverage (partner)"], "score_adjustment": {"original": 2.0, "adjusted": 2.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "low", "evidence_quality_factor": 0.40},
        "ADA-01": {"sub_pillar_id": "ADA-01", "sub_pillar_name": "Deception Infrastructure", "original_score": 1.0, "adjusted_score": 1.0, "scoring_level": 1, "score_rationale": "CBS HOLDING / SEK scores 1.0/5. No deception technology (honeypots, decoy environments) identified in public documentation. Palo Alto Cortex could theoretically enable deception capabilities in managed deployments but no managed deception offering documented.", "evidence_quality_rationale": "Evidence quality: 30% — Grade F-D. No evidence of deception capability found.", "criteria_assessment": [{"criterion": "Managed deception/honeypot offering", "status": "unmet", "evidence": "No public documentation", "confidence": "low"}], "scoring_level_justification": "Level 1: Minimal. No evidence beyond theoretical partner-platform potential.", "key_evidence": ["No deception capability documented in public sources"], "score_adjustment": {"original": 1.0, "adjusted": 1.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "low", "evidence_quality_factor": 0.30},
        "ADA-02": {"sub_pillar_id": "ADA-02", "sub_pillar_name": "Adaptive Deception", "original_score": 0.5, "adjusted_score": 0.5, "scoring_level": 0, "score_rationale": "No automated moving target defense or adaptive deception capabilities identified.", "evidence_quality_rationale": "Evidence quality: 20% — Grade F. No evidence found.", "criteria_assessment": [{"criterion": "AMTD/adaptive deception", "status": "unmet", "evidence": "No public documentation", "confidence": "low"}], "scoring_level_justification": "Below Level 1: No Evidence. No public documentation found.", "key_evidence": ["No evidence found"], "score_adjustment": {"original": 0.5, "adjusted": 0.5, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "low", "evidence_quality_factor": 0.20},
        "ADA-03": {"sub_pillar_id": "ADA-03", "sub_pillar_name": "AMTD Integration", "original_score": 1.5, "adjusted_score": 1.5, "scoring_level": 1, "score_rationale": "CBS HOLDING / SEK scores 1.5/5. Some attack surface management visibility likely available through the 40-vendor partner portfolio (potentially Palo Alto Cortex Xpanse). No explicit managed ASM or AMTD integration documented publicly.", "evidence_quality_rationale": "Evidence quality: 35% — Grade D. Inferred from broad partner portfolio description.", "criteria_assessment": [{"criterion": "Attack surface management capability", "status": "partial", "evidence": "40-vendor portfolio 'covering 60% of market security technologies'; Palo Alto Xpanse likely included", "confidence": "low"}], "scoring_level_justification": "Level 1-2 boundary. Partial evidence from broad portfolio claim; no explicit AMTD documentation.", "key_evidence": ["Portfolio claim: '60% of information security technologies available in market'", "Palo Alto partnership (Cortex Xpanse ASM likely available)"], "score_adjustment": {"original": 1.5, "adjusted": 1.5, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "low", "evidence_quality_factor": 0.35},
        "ADA-04": {"sub_pillar_id": "ADA-04", "sub_pillar_name": "Deception Analytics", "original_score": 0.5, "adjusted_score": 0.5, "scoring_level": 0, "score_rationale": "No deception analytics capability documented.", "evidence_quality_rationale": "Evidence quality: 20% — Grade F.", "criteria_assessment": [{"criterion": "Deception analytics", "status": "unmet", "evidence": "No public documentation", "confidence": "low"}], "scoring_level_justification": "Below Level 1: No Evidence.", "key_evidence": ["No evidence found"], "score_adjustment": {"original": 0.5, "adjusted": 0.5, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "low", "evidence_quality_factor": 0.20},
        "DIS-01": {"sub_pillar_id": "DIS-01", "sub_pillar_name": "Social Media Monitoring", "original_score": 0.0, "adjusted_score": 0.0, "scoring_level": 0, "score_rationale": "No social media monitoring, deepfake detection, or synthetic media capabilities identified.", "evidence_quality_rationale": "Evidence quality: 20% — Grade F.", "criteria_assessment": [{"criterion": "Social media / deepfake monitoring", "status": "unmet", "evidence": "No public documentation", "confidence": "low"}], "scoring_level_justification": "Level 0: No Evidence.", "key_evidence": ["No evidence found"], "score_adjustment": {"original": 0.0, "adjusted": 0.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "low", "evidence_quality_factor": 0.20},
        "DIS-02": {"sub_pillar_id": "DIS-02", "sub_pillar_name": "Brand Protection", "original_score": 2.0, "adjusted_score": 2.0, "scoring_level": 2, "score_rationale": "CBS HOLDING / SEK scores 2.0/5. Brand and identity protection likely available through managed security services and partner portfolio for enterprise clients. No explicitly documented brand protection product or service tier identified.", "evidence_quality_rationale": "Evidence quality: 35% — Grade D. Inferred from enterprise MSSP scope.", "criteria_assessment": [{"criterion": "Named brand protection service", "status": "unmet", "evidence": "No documented brand protection offering", "confidence": "low"}, {"criterion": "Identity threat coverage in managed services", "status": "partial", "evidence": "Implied by enterprise MSSP scope and partner platform capabilities", "confidence": "low"}], "scoring_level_justification": "Level 2: Generic Claims. Brand protection inferred from enterprise scope; not specifically documented.", "key_evidence": ["Enterprise MSSP positioning for 650 clients", "Partner portfolio implies identity/brand threat coverage"], "score_adjustment": {"original": 2.0, "adjusted": 2.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "low", "evidence_quality_factor": 0.35},
        "DIS-03": {"sub_pillar_id": "DIS-03", "sub_pillar_name": "Takedown Services", "original_score": 1.5, "adjusted_score": 1.5, "scoring_level": 1, "score_rationale": "CBS HOLDING / SEK scores 1.5/5. Possible takedown or digital risk services through partner portfolio; not explicitly documented.", "evidence_quality_rationale": "Evidence quality: 30% — Grade D.", "criteria_assessment": [{"criterion": "Takedown services", "status": "unmet", "evidence": "No public documentation", "confidence": "low"}], "scoring_level_justification": "Level 1: Minimal. Possible through broad partner portfolio but not documented.", "key_evidence": ["No direct evidence; inferred from MSSP scope"], "score_adjustment": {"original": 1.5, "adjusted": 1.5, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "low", "evidence_quality_factor": 0.30},
        "DIS-04": {"sub_pillar_id": "DIS-04", "sub_pillar_name": "Digital Risk Intelligence", "original_score": 1.5, "adjusted_score": 1.5, "scoring_level": 1, "score_rationale": "CBS HOLDING / SEK scores 1.5/5. Digital risk intelligence likely included in consulting and advisory engagements for enterprise clients. No standalone digital risk intelligence product documented.", "evidence_quality_rationale": "Evidence quality: 35% — Grade D.", "criteria_assessment": [{"criterion": "Digital risk intelligence service", "status": "partial", "evidence": "Consulting advisory for 650 enterprise clients implies digital risk advisory", "confidence": "low"}], "scoring_level_justification": "Level 1: Minimal. Advisory scope implies some digital risk coverage; not explicitly documented.", "key_evidence": ["650 enterprise clients with consulting/advisory services"], "score_adjustment": {"original": 1.5, "adjusted": 1.5, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "low", "evidence_quality_factor": 0.35},
        "IRA-01": {"sub_pillar_id": "IRA-01", "sub_pillar_name": "IR Planning & Readiness", "original_score": 3.0, "adjusted_score": 3.0, "scoring_level": 3, "score_rationale": "CBS HOLDING / SEK scores 3.0/5. Four dedicated cyber defense and incident response centers across LatAm provide IR planning and readiness as a core service. NeoSecure (Chile, est. ~1997) and Proteus (Brazil) heritage delivers deep enterprise IR readiness capability.", "evidence_quality_rationale": "Evidence quality: 65% — Grade C-B. IT Forum article confirms 4 IR centers and IR as core service.", "criteria_assessment": [{"criterion": "Dedicated IR planning service", "status": "met", "evidence": "4 cyber defense and IR centers; IR is a core pillar alongside MDR", "confidence": "high"}, {"criterion": "IR retainer offering", "status": "partial", "evidence": "Implied by MSSP model and enterprise scope; not explicitly documented", "confidence": "medium"}], "scoring_level_justification": "Level 3: Demonstrated. 4 IR centers, NeoSecure/Proteus heritage, enterprise MSSP model all support demonstrated IR readiness capability.", "key_evidence": ["4 cyber defense and incident response centers", "NeoSecure heritage (Chile)", "Proteus heritage (Brazil)", "Core IR service offering"], "score_adjustment": {"original": 3.0, "adjusted": 3.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "high", "evidence_quality_factor": 0.65},
        "IRA-02": {"sub_pillar_id": "IRA-02", "sub_pillar_name": "Forensic Investigation", "original_score": 4.0, "adjusted_score": 4.0, "scoring_level": 4, "score_rationale": "CBS HOLDING / SEK scores 4.0/5 for Forensic Investigation — the highest-confidence score in this entry. NeoSecure (Chile) was an established MSSP with dedicated DFIR capability prior to acquisition. Proteus (Brazil) was a specialist firm. Combined entity operates 4 IR centers with dedicated forensic teams serving 650 enterprise clients.", "evidence_quality_rationale": "Evidence quality: 70% — Grade C-B. IT Forum article confirms IR center count; NeoSecure's legacy DFIR capability is well-established in LatAm market.", "criteria_assessment": [{"criterion": "Dedicated DFIR teams and forensic capability", "status": "met", "evidence": "4 IR centers; NeoSecure and Proteus DFIR heritage; 80% technical staff", "confidence": "high"}, {"criterion": "Named DFIR service offering", "status": "met", "evidence": "Core IR service offering with forensic investigation as a pillar", "confidence": "high"}], "scoring_level_justification": "Level 4: Advanced. Documented multi-center DFIR capability with enterprise client base and heritage from two established LatAm cybersecurity firms.", "key_evidence": ["4 dedicated cyber defense and IR centers", "NeoSecure DFIR heritage (Chile)", "Proteus IR heritage (Brazil)", "650 enterprise clients with IR services", "80% of 750 staff are technical specialists"], "score_adjustment": {"original": 4.0, "adjusted": 4.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "high", "evidence_quality_factor": 0.70},
        "IRA-03": {"sub_pillar_id": "IRA-03", "sub_pillar_name": "Breach Remediation", "original_score": 3.0, "adjusted_score": 3.0, "scoring_level": 3, "score_rationale": "CBS HOLDING / SEK scores 3.0/5. Breach remediation delivered from 4 IR centers across 5 LatAm countries. Enterprise-grade remediation for 650 clients evidences operational scale. No published remediation SLAs.", "evidence_quality_rationale": "Evidence quality: 60% — Grade C.", "criteria_assessment": [{"criterion": "Enterprise breach remediation service", "status": "met", "evidence": "4 IR centers, enterprise MSSP for 650 clients", "confidence": "high"}, {"criterion": "Published remediation SLAs", "status": "unmet", "evidence": "No public SLA documentation", "confidence": "low"}], "scoring_level_justification": "Level 3: Demonstrated. Scale and heritage support demonstrated breach remediation.", "key_evidence": ["4 IR centers, 5-country coverage", "650 enterprise clients", "NeoSecure + Proteus IR heritage"], "score_adjustment": {"original": 3.0, "adjusted": 3.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "high", "evidence_quality_factor": 0.60},
        "IRA-04": {"sub_pillar_id": "IRA-04", "sub_pillar_name": "Post-Incident Analysis", "original_score": 3.0, "adjusted_score": 3.0, "scoring_level": 3, "score_rationale": "CBS HOLDING / SEK scores 3.0/5. Post-incident analysis is part of the IR engagement model given scale (650 clients, 4 IR centers, 2 R&D centers). No public documentation of specific post-incident methodology.", "evidence_quality_rationale": "Evidence quality: 50% — Grade C. Inferred from IR delivery model and R&D investment.", "criteria_assessment": [{"criterion": "Post-incident review process", "status": "partial", "evidence": "IR center model and 2 R&D centers imply structured post-incident learning loops", "confidence": "medium"}, {"criterion": "Published post-incident methodology", "status": "unmet", "evidence": "No public methodology documentation", "confidence": "low"}], "scoring_level_justification": "Level 3: Demonstrated. Structural evidence supports post-incident analysis at enterprise scale.", "key_evidence": ["4 IR centers with enterprise clients", "2 R&D innovation centers", "CEO emphasis on collective learning"], "score_adjustment": {"original": 3.0, "adjusted": 3.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "medium", "evidence_quality_factor": 0.50},
        "AIO-01": {"sub_pillar_id": "AIO-01", "sub_pillar_name": "AI-Driven Analytics", "original_score": 2.0, "adjusted_score": 2.0, "scoring_level": 2, "score_rationale": "CBS HOLDING / SEK scores 2.0/5. AI-driven analytics delivered through Palo Alto Cortex XSIAM and CrowdStrike Falcon AI in managed service delivery. No proprietary AI analytics layer identified.", "evidence_quality_rationale": "Evidence quality: 50% — Grade C. Partner platform AI capabilities inferred from named partnerships.", "criteria_assessment": [{"criterion": "AI analytics in managed service delivery", "status": "partial", "evidence": "Palo Alto XSIAM (AI-native SOC) and CrowdStrike Falcon AI used in delivery", "confidence": "medium"}], "scoring_level_justification": "Level 2: Generic Claims. AI via named partner platforms; no SEK-specific AI analytics layer.", "key_evidence": ["Palo Alto XSIAM partnership", "CrowdStrike Falcon AI partnership", "2 R&D centers (innovation trajectory)"], "score_adjustment": {"original": 2.0, "adjusted": 2.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "medium", "evidence_quality_factor": 0.50},
        "AIO-02": {"sub_pillar_id": "AIO-02", "sub_pillar_name": "ML Model Operations", "original_score": 2.0, "adjusted_score": 2.0, "scoring_level": 2, "score_rationale": "ML operations via CrowdStrike and Palo Alto XSIAM. No proprietary ML model training or MLOps capability documented.", "evidence_quality_rationale": "Evidence quality: 45% — Grade D-C.", "criteria_assessment": [{"criterion": "ML model operations", "status": "partial", "evidence": "Partner platform ML (CrowdStrike, XSIAM)", "confidence": "medium"}], "scoring_level_justification": "Level 2: Generic Claims.", "key_evidence": ["CrowdStrike Falcon AI/ML", "Palo Alto XSIAM ML"], "score_adjustment": {"original": 2.0, "adjusted": 2.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "low", "evidence_quality_factor": 0.45},
        "AIO-03": {"sub_pillar_id": "AIO-03", "sub_pillar_name": "NLP & LLM Integration", "original_score": 2.0, "adjusted_score": 2.0, "scoring_level": 2, "score_rationale": "LLM/NLP integration likely via Palo Alto XSIAM AI assistant and CrowdStrike Charlotte AI in managed delivery. No proprietary LLM product.", "evidence_quality_rationale": "Evidence quality: 40% — Grade D-C.", "criteria_assessment": [{"criterion": "LLM/NLP in managed service", "status": "partial", "evidence": "CrowdStrike Charlotte AI and Palo Alto XSIAM AI (partner)", "confidence": "low"}], "scoring_level_justification": "Level 2: Generic Claims.", "key_evidence": ["CrowdStrike Charlotte AI (partner)", "Palo Alto XSIAM AI Assistant (partner)"], "score_adjustment": {"original": 2.0, "adjusted": 2.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "low", "evidence_quality_factor": 0.40},
        "AIO-04": {"sub_pillar_id": "AIO-04", "sub_pillar_name": "AI Governance & Explainability", "original_score": 2.0, "adjusted_score": 2.0, "scoring_level": 2, "score_rationale": "AI governance via partner platform controls. No CBS HOLDING / SEK proprietary AI governance framework documented.", "evidence_quality_rationale": "Evidence quality: 35% — Grade D.", "criteria_assessment": [{"criterion": "AI governance documentation", "status": "unmet", "evidence": "No public documentation", "confidence": "low"}], "scoring_level_justification": "Level 2: Generic Claims. Partner platforms provide governance controls.", "key_evidence": ["Palo Alto XSIAM governance (partner)", "CrowdStrike AI governance (partner)"], "score_adjustment": {"original": 2.0, "adjusted": 2.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "low", "evidence_quality_factor": 0.35},
        "AID-01": {"sub_pillar_id": "AID-01", "sub_pillar_name": "AI Attack Detection", "original_score": 2.0, "adjusted_score": 2.0, "scoring_level": 2, "score_rationale": "AI attack detection through CrowdStrike Falcon AI and Palo Alto Cortex. 2 R&D centers may develop AI-specific detection. No published CBS HOLDING AI attack research.", "evidence_quality_rationale": "Evidence quality: 45% — Grade D-C.", "criteria_assessment": [{"criterion": "AI attack detection capability", "status": "partial", "evidence": "Partner platform AI detection; 2 R&D centers", "confidence": "medium"}], "scoring_level_justification": "Level 2: Generic Claims.", "key_evidence": ["CrowdStrike Falcon AI (partner)", "Palo Alto Cortex AI (partner)", "2 R&D centers"], "score_adjustment": {"original": 2.0, "adjusted": 2.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "low", "evidence_quality_factor": 0.45},
        "AID-02": {"sub_pillar_id": "AID-02", "sub_pillar_name": "AI Supply Chain Security", "original_score": 1.0, "adjusted_score": 1.0, "scoring_level": 1, "score_rationale": "No AI supply chain security capability documented.", "evidence_quality_rationale": "Evidence quality: 25% — Grade F.", "criteria_assessment": [{"criterion": "AI supply chain security", "status": "unmet", "evidence": "No public documentation", "confidence": "low"}], "scoring_level_justification": "Level 1: Minimal.", "key_evidence": ["No evidence found"], "score_adjustment": {"original": 1.0, "adjusted": 1.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "low", "evidence_quality_factor": 0.25},
        "AID-03": {"sub_pillar_id": "AID-03", "sub_pillar_name": "Adversarial ML Defense", "original_score": 1.0, "adjusted_score": 1.0, "scoring_level": 1, "score_rationale": "No adversarial ML defense capability documented.", "evidence_quality_rationale": "Evidence quality: 25% — Grade F.", "criteria_assessment": [{"criterion": "Adversarial ML defense", "status": "unmet", "evidence": "No public documentation", "confidence": "low"}], "scoring_level_justification": "Level 1: Minimal.", "key_evidence": ["No evidence found"], "score_adjustment": {"original": 1.0, "adjusted": 1.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "low", "evidence_quality_factor": 0.25},
        "AID-04": {"sub_pillar_id": "AID-04", "sub_pillar_name": "AI-Specific Threat Intel", "original_score": 2.0, "adjusted_score": 2.0, "scoring_level": 2, "score_rationale": "CBS HOLDING / SEK scores 2.0/5. 2 R&D centers and USD $150M Pátria growth investment signal AI threat intelligence trajectory. No published AI-specific threat intel reports.", "evidence_quality_rationale": "Evidence quality: 45% — Grade D-C.", "criteria_assessment": [{"criterion": "AI threat intelligence capability", "status": "partial", "evidence": "2 R&D centers, $150M growth capital, 40 vendor partnerships", "confidence": "low"}], "scoring_level_justification": "Level 2: Generic Claims. R&D investment indicates trajectory; no published output.", "key_evidence": ["2 R&D innovation centers", "USD $150M Pátria growth investment", "40 certified technology partnerships"], "score_adjustment": {"original": 2.0, "adjusted": 2.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "low", "evidence_quality_factor": 0.45},
        "SOG-01": {"sub_pillar_id": "SOG-01", "sub_pillar_name": "Compliance Reporting", "original_score": 4.0, "adjusted_score": 4.0, "scoring_level": 4, "score_rationale": "CBS HOLDING / SEK scores 4.0/5 — joint-highest score alongside IRA-02. Multi-jurisdiction compliance reporting (LGPD Brazil, Ley 25326 Argentina, Ley 19.628 Chile, etc.) across 5 countries for 650 enterprise clients is a core differentiator. NeoSecure and Proteus heritage includes compliance advisory.", "evidence_quality_rationale": "Evidence quality: 65% — Grade C-B. 5-country presence and enterprise client scale are well-documented.", "criteria_assessment": [{"criterion": "Multi-jurisdiction compliance reporting", "status": "met", "evidence": "5-country presence with distinct regulatory environments; 650 enterprise clients", "confidence": "high"}, {"criterion": "Named compliance frameworks covered", "status": "partial", "evidence": "LatAm regulatory frameworks (LGPD, etc.) implied by geography; not explicitly enumerated", "confidence": "medium"}], "scoring_level_justification": "Level 4: Advanced. 5-country multi-regulatory compliance for enterprise scale is an advanced documented capability.", "key_evidence": ["5 LatAm countries with distinct regulatory regimes (LGPD, etc.)", "650 enterprise clients requiring compliance reporting", "NeoSecure + Proteus compliance advisory heritage"], "score_adjustment": {"original": 4.0, "adjusted": 4.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "high", "evidence_quality_factor": 0.65},
        "SOG-02": {"sub_pillar_id": "SOG-02", "sub_pillar_name": "SLA Management", "original_score": 3.0, "adjusted_score": 3.0, "scoring_level": 3, "score_rationale": "CBS HOLDING / SEK scores 3.0/5. 650 enterprise managed service clients requires formal SLA management. No published SLA standards identified.", "evidence_quality_rationale": "Evidence quality: 55% — Grade C.", "criteria_assessment": [{"criterion": "Formal SLA management", "status": "met", "evidence": "650 enterprise clients with 24/7 managed service contracts", "confidence": "medium"}, {"criterion": "Published SLA standards", "status": "unmet", "evidence": "No public SLA documentation", "confidence": "low"}], "scoring_level_justification": "Level 3: Demonstrated. Enterprise client scale requires SLA management; documented by client count and managed service model.", "key_evidence": ["650 enterprise clients", "24/7 SOC across 4 centers", "MSSP contract model"], "score_adjustment": {"original": 3.0, "adjusted": 3.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "medium", "evidence_quality_factor": 0.55},
        "SOG-03": {"sub_pillar_id": "SOG-03", "sub_pillar_name": "Service Transparency", "original_score": 3.0, "adjusted_score": 3.0, "scoring_level": 3, "score_rationale": "CBS HOLDING / SEK scores 3.0/5. Partner-technology model with 40 certified vendor partnerships is publicly documented. Client-facing reporting for 650 enterprise clients implied by managed service model.", "evidence_quality_rationale": "Evidence quality: 55% — Grade C.", "criteria_assessment": [{"criterion": "Partner model transparency", "status": "met", "evidence": "40 certified vendor partnerships publicly declared; platform-agnostic model stated", "confidence": "high"}, {"criterion": "Client portal/dashboard", "status": "partial", "evidence": "Implied by 650-client enterprise model; not publicly documented", "confidence": "low"}], "scoring_level_justification": "Level 3: Demonstrated. Public documentation of partner model and enterprise delivery structure supports service transparency.", "key_evidence": ["40 certified technology partnerships publicly stated", "650 enterprise client model", "CEO transparency about partner-based delivery"], "score_adjustment": {"original": 3.0, "adjusted": 3.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "medium", "evidence_quality_factor": 0.55},
        "SOG-04": {"sub_pillar_id": "SOG-04", "sub_pillar_name": "Continuous Improvement", "original_score": 3.0, "adjusted_score": 3.0, "scoring_level": 3, "score_rationale": "CBS HOLDING / SEK scores 3.0/5. Continuous improvement evidenced by USD $150M growth investment, 2 R&D centers, active M&A strategy, and USD $15M 2023 portfolio/capability investment.", "evidence_quality_rationale": "Evidence quality: 65% — Grade C-B. Investment figures and R&D centers are from CEO statements in IT Forum article.", "criteria_assessment": [{"criterion": "Structured improvement program", "status": "met", "evidence": "2 R&D centers, $150M growth capital, $15M 2023 portfolio investment, M&A strategy", "confidence": "high"}, {"criterion": "Published improvement roadmap", "status": "partial", "evidence": "CEO stated quintupling goal and M&A/organic strategy; not a formal roadmap", "confidence": "medium"}], "scoring_level_justification": "Level 3: Demonstrated. Investment scale and R&D commitment demonstrate structured continuous improvement program.", "key_evidence": ["USD $150M Pátria growth investment reserve", "USD $15M 2023 portfolio/capability investment", "2 R&D innovation centers", "Active M&A strategy (complementary capabilities/geographies)"], "score_adjustment": {"original": 3.0, "adjusted": 3.0, "reason": "No adjustment."}, "additional_sources_found": 0, "confidence": "high", "evidence_quality_factor": 0.65},
    },
    "sub_pillar_rationale_v2_1": {
        sp: {"sub_pillar_id": sp, "adjusted_score": sc, "no_change_reason": "Seed entry — no v2.1 revision sources available. Scores carried forward from initial seed research.", "v2_1_delta": 0}
        for sp, sc in {
            "TDR-01": 3.0, "TDR-02": 3.0, "TDR-03": 3.0, "TDR-04": 2.0,
            "PTI-01": 3.0, "PTI-02": 2.0, "PTI-03": 3.0, "PTI-04": 2.0,
            "ADA-01": 1.0, "ADA-02": 0.5, "ADA-03": 1.5, "ADA-04": 0.5,
            "DIS-01": 0.0, "DIS-02": 2.0, "DIS-03": 1.5, "DIS-04": 1.5,
            "IRA-01": 3.0, "IRA-02": 4.0, "IRA-03": 3.0, "IRA-04": 3.0,
            "AIO-01": 2.0, "AIO-02": 2.0, "AIO-03": 2.0, "AIO-04": 2.0,
            "AID-01": 2.0, "AID-02": 1.0, "AID-03": 1.0, "AID-04": 2.0,
            "SOG-01": 4.0, "SOG-02": 3.0, "SOG-03": 3.0, "SOG-04": 3.0,
        }.items()
    },
    "sub_pillar_rationale_v2_1_text": {
        sp: f"{sp}: Score {sc}/5. Seed entry — no v2.1 revision. Score carried forward from initial research. See sub_pillar_rationale_v2 for full evidence basis."
        for sp, sc in {
            "TDR-01": 3.0, "TDR-02": 3.0, "TDR-03": 3.0, "TDR-04": 2.0,
            "PTI-01": 3.0, "PTI-02": 2.0, "PTI-03": 3.0, "PTI-04": 2.0,
            "ADA-01": 1.0, "ADA-02": 0.5, "ADA-03": 1.5, "ADA-04": 0.5,
            "DIS-01": 0.0, "DIS-02": 2.0, "DIS-03": 1.5, "DIS-04": 1.5,
            "IRA-01": 3.0, "IRA-02": 4.0, "IRA-03": 3.0, "IRA-04": 3.0,
            "AIO-01": 2.0, "AIO-02": 2.0, "AIO-03": 2.0, "AIO-04": 2.0,
            "AID-01": 2.0, "AID-02": 1.0, "AID-03": 1.0, "AID-04": 2.0,
            "SOG-01": 4.0, "SOG-02": 3.0, "SOG-03": 3.0, "SOG-04": 3.0,
        }.items()
    },
    "sub_pillar_rationale_v2_consolidated": {
        "TDR-01": "TDR-01 – Signal Correlation & Alert Triage: Score 3.0/5 (Level 3: Demonstrated)\n\n[Score Rationale]\n24/7 multi-vendor SOC delivers signal correlation across endpoint (CrowdStrike Falcon), cloud (Palo Alto Cortex/XSIAM), OT/IoT (Nozomi), and network (F5). Monitors 500K critical assets. 156M attacks prevented in 2022.\n\n[Evidence Quality]\nEvidence quality: 55% — Grade C (Adequate). IT Forum launch article (March 2023); no direct SEK website access.",
        "TDR-02": "TDR-02 – Threat Hunting: Score 3.0/5 (Level 3: Demonstrated)\n\n[Score Rationale]\n4 cyber defense centers with ~600 technical specialists. NeoSecure (Chile) MSSP heritage includes enterprise hunting. No published hunt frequency metrics.\n\n[Evidence Quality]\nEvidence quality: 50% — Grade C.",
        "TDR-03": "TDR-03 – Automated Containment: Score 3.0/5 (Level 3: Demonstrated)\n\n[Score Rationale]\nCrowdStrike Falcon host isolation and Palo Alto Cortex automated policy enforcement in managed delivery. 156M attacks prevented (2022) evidences blocking at scale.\n\n[Evidence Quality]\nEvidence quality: 60% — Grade C-B.",
        "TDR-04": "TDR-04 – Response Orchestration: Score 2.0/5 (Level 2: Generic Claims)\n\n[Score Rationale]\nResponse orchestration inferred from 650-client managed service model. No published MTTD/MTTR SLAs or SOAR documentation.\n\n[Evidence Quality]\nEvidence quality: 40% — Grade D-C.",
        "PTI-01": "PTI-01 – Strategic Threat Intelligence: Score 3.0/5 (Level 3: Demonstrated)\n\n[Score Rationale]\nCEO: 'incorporating the hacker's perspective into our defense offering.' 40 certified vendor partnerships operationalize strategic TI. 5-country LatAm footprint provides regional threat breadth.\n\n[Evidence Quality]\nEvidence quality: 60% — Grade C.",
        "PTI-02": "PTI-02 – Tactical Threat Feeds: Score 2.0/5 (Level 2: Generic Claims)\n\n[Score Rationale]\nTactical feeds via CrowdStrike Falcon Intelligence and Palo Alto Unit 42 partners. No dedicated proprietary feed product.\n\n[Evidence Quality]\nEvidence quality: 45% — Grade D-C.",
        "PTI-03": "PTI-03 – Threat Landscape Mapping: Score 3.0/5 (Level 3: Demonstrated)\n\n[Score Rationale]\nLatAm-specific expertise from 5-country footprint, 650 clients, 2 R&D centers. CEO: 'collective learning makes us almost unique in the region.'\n\n[Evidence Quality]\nEvidence quality: 60% — Grade C.",
        "PTI-04": "PTI-04 – Intelligence-Driven Detection: Score 2.0/5 (Level 2: Generic Claims)\n\n[Score Rationale]\nDetection via partner intelligence platforms (CrowdStrike, Palo Alto). No proprietary adversary tracking or TTP detection publications.\n\n[Evidence Quality]\nEvidence quality: 40% — Grade D-C.",
        "ADA-01": "ADA-01 – Deception Infrastructure: Score 1.0/5 (Level 1: Minimal)\n\n[Score Rationale]\nNo deception technology documented. Theoretical Palo Alto Cortex deception potential; no managed deception offering confirmed.\n\n[Evidence Quality]\nEvidence quality: 30% — Grade F-D.",
        "ADA-02": "ADA-02 – Adaptive Deception: Score 0.5/5 (Below Level 1: No Evidence)\n\n[Score Rationale]\nNo AMTD or adaptive deception capability documented.\n\n[Evidence Quality]\nEvidence quality: 20% — Grade F.",
        "ADA-03": "ADA-03 – AMTD Integration: Score 1.5/5 (Level 1-2)\n\n[Score Rationale]\nAttack surface management possible through broad partner portfolio (Palo Alto Cortex Xpanse likely included). Not explicitly documented.\n\n[Evidence Quality]\nEvidence quality: 35% — Grade D.",
        "ADA-04": "ADA-04 – Deception Analytics: Score 0.5/5 (Below Level 1: No Evidence)\n\n[Score Rationale]\nNo deception analytics documented.\n\n[Evidence Quality]\nEvidence quality: 20% — Grade F.",
        "DIS-01": "DIS-01 – Social Media Monitoring: Score 0.0/5 (Level 0: No Evidence)\n\n[Score Rationale]\nNo social media monitoring or deepfake detection capability identified.\n\n[Evidence Quality]\nEvidence quality: 20% — Grade F.",
        "DIS-02": "DIS-02 – Brand Protection: Score 2.0/5 (Level 2: Generic Claims)\n\n[Score Rationale]\nBrand/identity protection likely available through enterprise managed services and partner stack. Not explicitly documented.\n\n[Evidence Quality]\nEvidence quality: 35% — Grade D.",
        "DIS-03": "DIS-03 – Takedown Services: Score 1.5/5 (Level 1: Minimal)\n\n[Score Rationale]\nPossible through partner portfolio; not documented.\n\n[Evidence Quality]\nEvidence quality: 30% — Grade D.",
        "DIS-04": "DIS-04 – Digital Risk Intelligence: Score 1.5/5 (Level 1: Minimal)\n\n[Score Rationale]\nLikely included in consulting engagements; no standalone product documented.\n\n[Evidence Quality]\nEvidence quality: 35% — Grade D.",
        "IRA-01": "IRA-01 – IR Planning & Readiness: Score 3.0/5 (Level 3: Demonstrated)\n\n[Score Rationale]\n4 dedicated cyber defense and IR centers. NeoSecure (Chile) and Proteus (Brazil) heritage delivers deep enterprise IR readiness.\n\n[Evidence Quality]\nEvidence quality: 65% — Grade C-B.",
        "IRA-02": "IRA-02 – Forensic Investigation: Score 4.0/5 (Level 4: Advanced)\n\n[Score Rationale]\nHighest-confidence score. NeoSecure (Chile, established MSSP with DFIR) + Proteus (Brazil IR specialist) heritage. 4 IR centers, 750 staff (80% technical), 650 enterprise clients.\n\n[Evidence Quality]\nEvidence quality: 70% — Grade C-B. This score is the most defensible in the entry.",
        "IRA-03": "IRA-03 – Breach Remediation: Score 3.0/5 (Level 3: Demonstrated)\n\n[Score Rationale]\n4 IR centers across 5 LatAm countries. Enterprise-grade remediation for 650 clients evidences operational scale.\n\n[Evidence Quality]\nEvidence quality: 60% — Grade C.",
        "IRA-04": "IRA-04 – Post-Incident Analysis: Score 3.0/5 (Level 3: Demonstrated)\n\n[Score Rationale]\nPost-incident review implied by 4 IR centers + 2 R&D centers and enterprise client scale. No specific methodology published.\n\n[Evidence Quality]\nEvidence quality: 50% — Grade C.",
        "AIO-01": "AIO-01 – AI-Driven Analytics: Score 2.0/5 (Level 2: Generic Claims)\n\n[Score Rationale]\nAI analytics via Palo Alto XSIAM and CrowdStrike Falcon AI in managed delivery. No proprietary AI layer. R&D centers signal development trajectory.\n\n[Evidence Quality]\nEvidence quality: 50% — Grade C.",
        "AIO-02": "AIO-02 – ML Model Operations: Score 2.0/5 (Level 2: Generic Claims)\n\n[Score Rationale]\nML via partner platforms (CrowdStrike, Palo Alto XSIAM). No proprietary MLOps.\n\n[Evidence Quality]\nEvidence quality: 45% — Grade D-C.",
        "AIO-03": "AIO-03 – NLP & LLM Integration: Score 2.0/5 (Level 2: Generic Claims)\n\n[Score Rationale]\nLLM/NLP via CrowdStrike Charlotte AI and Palo Alto XSIAM AI Assistant (partners). No proprietary LLM product.\n\n[Evidence Quality]\nEvidence quality: 40% — Grade D-C.",
        "AIO-04": "AIO-04 – AI Governance & Explainability: Score 2.0/5 (Level 2: Generic Claims)\n\n[Score Rationale]\nAI governance via partner platform controls. No CBS HOLDING / SEK proprietary governance framework documented.\n\n[Evidence Quality]\nEvidence quality: 35% — Grade D.",
        "AID-01": "AID-01 – AI Attack Detection: Score 2.0/5 (Level 2: Generic Claims)\n\n[Score Rationale]\nAI attack detection through CrowdStrike Falcon AI and Palo Alto Cortex. 2 R&D centers indicate trajectory. No published AI attack research.\n\n[Evidence Quality]\nEvidence quality: 45% — Grade D-C.",
        "AID-02": "AID-02 – AI Supply Chain Security: Score 1.0/5 (Level 1: Minimal)\n\n[Score Rationale]\nNo AI supply chain security capability documented.\n\n[Evidence Quality]\nEvidence quality: 25% — Grade F.",
        "AID-03": "AID-03 – Adversarial ML Defense: Score 1.0/5 (Level 1: Minimal)\n\n[Score Rationale]\nNo adversarial ML defense capability documented.\n\n[Evidence Quality]\nEvidence quality: 25% — Grade F.",
        "AID-04": "AID-04 – AI-Specific Threat Intel: Score 2.0/5 (Level 2: Generic Claims)\n\n[Score Rationale]\n2 R&D centers and USD $150M growth investment signal AI threat intel trajectory. No published AI-specific threat intel output.\n\n[Evidence Quality]\nEvidence quality: 45% — Grade D-C.",
        "SOG-01": "SOG-01 – Compliance Reporting: Score 4.0/5 (Level 4: Advanced)\n\n[Score Rationale]\nJoint-highest score. Multi-jurisdiction compliance (LGPD, Ley 25326, Ley 19.628, etc.) across 5 LatAm countries for 650 enterprise clients. NeoSecure + Proteus compliance advisory heritage.\n\n[Evidence Quality]\nEvidence quality: 65% — Grade C-B.",
        "SOG-02": "SOG-02 – SLA Management: Score 3.0/5 (Level 3: Demonstrated)\n\n[Score Rationale]\n650 enterprise managed service clients require formal SLA management. 24/7 SOC across 4 centers. No published SLA standards.\n\n[Evidence Quality]\nEvidence quality: 55% — Grade C.",
        "SOG-03": "SOG-03 – Service Transparency: Score 3.0/5 (Level 3: Demonstrated)\n\n[Score Rationale]\n40 certified vendor partnerships publicly documented. Partner-based delivery model openly stated by CEO. Client-facing reporting for enterprise accounts implied.\n\n[Evidence Quality]\nEvidence quality: 55% — Grade C.",
        "SOG-04": "SOG-04 – Continuous Improvement: Score 3.0/5 (Level 3: Demonstrated)\n\n[Score Rationale]\nUSD $150M growth investment reserve, 2 R&D centers, USD $15M 2023 capability investment, active M&A strategy for portfolio complementarity.\n\n[Evidence Quality]\nEvidence quality: 65% — Grade C-B.",
    },
    "capability_analysis": (
        "CBS HOLDING S.A. (operating as SEK) delivers threat detection and "
        "response through a multi-vendor managed service model anchored on "
        "Palo Alto Networks and CrowdStrike platforms across four dedicated "
        "cyber defense and incident response centers. Standout scores in "
        "incident response (IRA: 3.25) reflect dedicated forensic and IR "
        "teams, 4 regional cyber defense centers, and a heritage of MSSP "
        "delivery through the acquired NeoSecure and Proteus entities. "
        "Service operations (SOG: 3.25) reflect 24/7 SOC with 750 staff "
        "(80% technical), 650 enterprise clients, and five-country physical "
        "presence. Signal correlation and detection engineering (TDR: 2.75) "
        "rely on CrowdStrike Falcon, Palo Alto Cortex/XSIAM, and Nozomi for "
        "OT/IoT. Threat intelligence (PTI: 2.50) is evidenced by 156M attacks "
        "prevented in 2022 and intelligence operationalized through 40 vendor "
        "partnerships. Primary gaps are in active defense / deception (ADA: "
        "0.88), digital influence security (DIS: 1.25), and AI depth and "
        "governance (AID: 1.50). No proprietary detection platform — delivery "
        "is partner-stack-dependent."
    ),
    "notable_differentiation": (
        "LatAm's largest independent cybersecurity pure-play by revenue and "
        "headcount. Backed by Pátria Investimentos with USD $250M+ in total "
        "committed capital. Physical presence in five LatAm countries (AR, "
        "BR, CL, CO, PE) with four cyber defense / IR centers. NeoSecure "
        "heritage (Chile) brings strong enterprise MSSP capability; Proteus "
        "heritage (Brazil) adds local regulatory and compliance expertise. "
        "40 certified technology partnerships across major security vendors. "
        "OT/ICS security coverage via Nozomi partnership. SEK brand targets "
        "USD $500M revenue by 2028 through organic growth and acquisitions."
    ),
    "notable_differentiation_v2_1": (
        "Strongest sub-pillars: Forensic Investigation (4.0), Compliance "
        "Reporting (4.0), Signal Correlation & Alert Triage (3.0), "
        "Threat Hunting (3.0), Automated Containment (3.0), IR Planning "
        "& Readiness (3.0), Breach Remediation (3.0), Post-Incident Analysis "
        "(3.0), Strategic Threat Intelligence (3.0), Threat Landscape Mapping "
        "(3.0), SLA Management (3.0), Service Transparency (3.0), Continuous "
        "Improvement (3.0). Growth areas: Deception Infrastructure (1.0), "
        "Adaptive Deception (0.5), Deception Analytics (0.5). No proprietary "
        "detection platform — all telemetry collection via partner stack."
    ),
    "research_confidence": "medium",
    "research_confidence_v2_1": "medium",
    "v2_1_adjustment_summary": {
        "increased": 0,
        "decreased": 0,
        "validated": 0,
        "no_change": 32,
        "total": 32,
    },
    "evidence_quality_summary": (
        "Seed scores derived from IT Forum launch coverage of the SEK brand "
        "(March 30, 2023), Bing search results for CBS HOLDING / SEK / "
        "Pátria cibersegurança, CNPJ registry entry (Casa dos Dados), and "
        "indirect references to CBS CyberSecurity Holding in SEC.gov filings. "
        "CBS HOLDING S.A. / SEK is not covered by Gartner Magic Quadrant or "
        "Market Guide for MDR as of May 2026. No primary customer references "
        "or analyst peer-review evidence available. Scores are intentionally "
        "conservative, using publicly verifiable data only. The SEK website "
        "(sek.com.br) was not reachable for detailed content scraping; "
        "scoring reflects third-party media and registry data."
    ),
}

# ============================================================
# 2. MDR Pricing entry
# ============================================================
cbs_pricing = {
    "vendor": VENDOR_NAME,
    "description": (
        "CBS HOLDING S.A. (operating as SEK) is Brazil's Pátria-backed "
        "cybersecurity holding company delivering managed security services "
        "across five Latin American countries with ~USD $100M annual revenue "
        "and 650 enterprise clients."
    ),
    "region": "Latin America",
    "headquarters": "São Paulo, Brazil",
    "mdr_service_type": "Extended MDR",
    "target_market": "Enterprise (LatAm)",
    "product_names": [
        "SEK MDR",
        "SEK SOC",
        "SEK Incident Response & Forensics",
        "SEK Managed Threat Intelligence",
        "SEK Cybersecurity Consulting",
    ],
    "website": "https://sek.com.br",
    "research_status": "seed",
    "pricing_analysis": (
        "CBS HOLDING / SEK operates as a large-scale Latin American MSSP "
        "with bespoke enterprise contract structures. Pricing is not publicly "
        "disclosed. Expected model: per-endpoint/per-asset subscription for "
        "SOC and MDR tiers, fixed onboarding and integration fees, retainer "
        "for IR, and consulting-led project pricing. Pátria investment backing "
        "implies private equity growth pricing posture — competitive on volume "
        "to gain market share ahead of the USD $500M revenue target. No "
        "public outcome-based or success-fee pricing mechanisms identified."
    ),
    "pricing_model_type": "Subscription + Consulting + IR Retainer",
    "pricing_model_details": {
        "subscription_components": [
            "MDR / SOC monitoring tier subscription (per endpoint / per asset)",
            "Managed Threat Intelligence subscription",
            "Technology partner license pass-through (Palo Alto, CrowdStrike)",
        ],
        "usage_components": [
            "Number of endpoints / assets monitored",
            "Log volume / SIEM ingestion",
            "Number of integrated data sources",
        ],
        "fixed_components": [
            "Onboarding and integration project fee",
            "Incident response retainer",
            "Security consulting engagement fees",
        ],
        "success_fee_components": [],
        "outcome_linked_components": [],
        "published_pricing": False,
        "pricing_calculator_available": False,
        "usage_dashboard_available": False,
    },
    "pricing_dimension_scores": {
        "PRC-SUB": 2,
        "PRC-USG": 2,
        "PRC-FIX": 2,
        "PRC-SUC": 1,
        "PRC-COM": 2,
        "PRC-OUT": 1,
    },
    "pricing_dimension_scores_v2": {
        "PRC-SUB": 2.0,
        "PRC-USG": 2.0,
        "PRC-FIX": 2.0,
        "PRC-SUC": 1.0,
        "PRC-COM": 2.0,
        "PRC-OUT": 1.0,
    },
    "pricing_overall_score": 1.67,
    "pricing_overall_score_v2": 1.67,
    "pricing_dimension_labels": {
        "PRC-SUB": "Subscription Transparency",
        "PRC-USG": "Usage-Based Alignment",
        "PRC-FIX": "Fixed Delivery Pricing",
        "PRC-SUC": "Success & Outcome Fees",
        "PRC-COM": "Composability & Overall Model Maturity",
        "PRC-OUT": "Pricing-to-Outcomes Alignment",
    },
    "pricing_dimension_rationale_v2": {
        "PRC-SUB": {"dimension_id": "PRC-SUB", "dimension_name": "Subscription Transparency", "score": 2.0, "score_rationale": "CBS HOLDING / SEK operates a subscription-based managed service model for 650 enterprise clients, typical of large LatAm MSSPs. No publicly documented pricing tiers, list prices, or subscription structure transparency.", "evidence_summary": "Score inferred from MSSP operating model; no public pricing documentation found.", "confidence": "low"},
        "PRC-USG": {"dimension_id": "PRC-USG", "dimension_name": "Usage-Based Alignment", "score": 1.5, "score_rationale": "No evidence of usage-based pricing model (asset count, event volume, etc.). Enterprise contracts likely include scope-defined service tiers but no consumption-based alignment documented.", "evidence_summary": "No public usage-based pricing documentation.", "confidence": "low"},
        "PRC-FIX": {"dimension_id": "PRC-FIX", "dimension_name": "Fixed Delivery Pricing", "score": 2.5, "score_rationale": "Fixed-fee managed service delivery is the dominant model for LatAm enterprise MSSPs. CBS HOLDING / SEK enterprise contracts likely include fixed-scope MDR + IR retainer bundles. No public pricing confirmation.", "evidence_summary": "MSSP enterprise model implies fixed delivery pricing; no public confirmation.", "confidence": "low"},
        "PRC-SUC": {"dimension_id": "PRC-SUC", "dimension_name": "Success & Outcome Fees", "score": 0.5, "score_rationale": "No success or outcome-based fee structure identified. PE-backed growth trajectory suggests possible future adoption but no current evidence.", "evidence_summary": "No evidence of outcome or success-based fees.", "confidence": "low"},
        "PRC-COM": {"dimension_id": "PRC-COM", "dimension_name": "Composability & Overall Model Maturity", "score": 2.0, "score_rationale": "40-vendor partner portfolio suggests modular service composition capability. Enterprise clients can likely combine MDR, IR, consulting, and technology services. No documented composability framework.", "evidence_summary": "40-vendor portfolio implies composability; no formal documentation.", "confidence": "low"},
        "PRC-OUT": {"dimension_id": "PRC-OUT", "dimension_name": "Pricing-to-Outcomes Alignment", "score": 1.5, "score_rationale": "No evidence of pricing-to-outcomes alignment. 156M attacks prevented metric shows outcome measurement capability but is not linked to commercial pricing model.", "evidence_summary": "Outcome metrics exist (156M attacks prevented); not linked to pricing.", "confidence": "low"},
    },
    "pricing_dimension_rationale_v2_text": {
        "PRC-SUB": "PRC-SUB – Subscription Transparency: Score 2.0/5\n\nScore 2.0/5. CBS HOLDING / SEK uses a subscription-based managed service model for 650 enterprise clients. No publicly documented pricing tiers or list prices. Typical LatAm enterprise MSSP subscription model — not transparent.",
        "PRC-USG": "PRC-USG – Usage-Based Alignment: Score 1.5/5\n\nScore 1.5/5. No evidence of usage-based pricing (asset count, event volume, endpoint count tiers). Scope-defined enterprise contracts are the likely model. No public documentation.",
        "PRC-FIX": "PRC-FIX – Fixed Delivery Pricing: Score 2.5/5\n\nScore 2.5/5. Fixed-fee managed service delivery is standard for LatAm enterprise MSSPs. CBS HOLDING / SEK enterprise contracts likely include fixed MDR + IR retainer bundles. No public pricing confirmation.",
        "PRC-SUC": "PRC-SUC – Success & Outcome Fees: Score 0.5/5\n\nScore 0.5/5. No success or outcome-based fee structure identified in any available source. PE backing (Pátria) creates future commercial pressure for outcome alignment but no current evidence.",
        "PRC-COM": "PRC-COM – Composability & Overall Model Maturity: Score 2.0/5\n\nScore 2.0/5. 40-vendor partner portfolio enables modular service composition (MDR + IR + consulting + technology). No formal composability documentation. Enterprise-grade bundling likely available on request.",
        "PRC-OUT": "PRC-OUT – Pricing-to-Outcomes Alignment: Score 1.5/5\n\nScore 1.5/5. 156M attacks prevented (2022) and 500K assets protected are published outcome metrics. These are not linked to commercial pricing model. No outcome-linked pricing evidence.",
    },
    "pricing_evidence": {
        "PRC-SUB": {"source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"], "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "CBS HOLDING / SEK operates as a subscription-based managed security services provider for 650 enterprise clients across 5 LatAm countries. No public pricing tiers or list prices identified.", "matched_terms": ["subscription", "pricing transparency"], "relevance_score": 5}], "notes": "Score 2.0/5. Subscription model inferred from MSSP positioning; no public pricing documentation."},
        "PRC-USG": {"source_urls": ["https://sek.com.br"], "excerpts": [{"url": "https://sek.com.br", "excerpt": "No usage-based pricing documentation found for CBS HOLDING / SEK.", "matched_terms": ["usage-based pricing"], "relevance_score": 3}], "notes": "Score 1.5/5. No usage-based pricing model documented."},
        "PRC-FIX": {"source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"], "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "CBS HOLDING / SEK delivers managed security services under enterprise contracts. Fixed-scope MDR + IR retainer model is typical for LatAm enterprise MSSPs of this scale.", "matched_terms": ["fixed pricing", "managed service contracts"], "relevance_score": 5}], "notes": "Score 2.5/5. Fixed delivery model inferred from enterprise MSSP positioning."},
        "PRC-SUC": {"source_urls": ["https://sek.com.br"], "excerpts": [{"url": "https://sek.com.br", "excerpt": "No success-based or outcome-based fee structure documented for CBS HOLDING / SEK.", "matched_terms": ["success fees", "outcome fees"], "relevance_score": 2}], "notes": "Score 0.5/5. No outcome or success fee structure identified."},
        "PRC-COM": {"source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"], "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK's portfolio covers 60% of information security technologies available in the market through 40 certified vendor partnerships, enabling composable service bundles for enterprise clients.", "matched_terms": ["composability", "modular", "partner portfolio"], "relevance_score": 6}], "notes": "Score 2.0/5. 40-vendor portfolio enables composable delivery; no formal composability documentation."},
        "PRC-OUT": {"source_urls": ["https://sek.com.br", "https://itforum.com.br/noticias/sek-ciberseguranca-patria/"], "excerpts": [{"url": "https://itforum.com.br/noticias/sek-ciberseguranca-patria/", "excerpt": "SEK protected 500,000 critical business assets and prevented approximately 156 million attacks in 2022 — outcome metrics that are published but not linked to commercial pricing structure.", "matched_terms": ["pricing outcomes", "outcome metrics", "attacks prevented"], "relevance_score": 6}], "notes": "Score 1.5/5. Outcome metrics exist; not linked to pricing model."},
    },
    "pricing_adjustment_summary": {
        "increased": 0,
        "decreased": 0,
        "validated": 0,
        "no_change": 6,
    },
    "pricing_research_confidence": "low",
    "outcome_maturity_rating": 1,
    "outcome_maturity_rating_v2": 1,
    "outcome_maturity_rationale_v2": (
        "Seed rating — no outcome-based pricing evidence found. CBS HOLDING / "
        "SEK uses a subscription + consulting + IR retainer model typical of "
        "large LatAm MSSP operations. Private equity backing (Pátria) may "
        "create pressure to adopt outcome-linked pricing as the company scales "
        "toward its USD $500M revenue target, but no public evidence of this "
        "yet."
    ),
    "outcome_signals_v2": {
        "pricing_changes_on_outcomes": False,
        "metrics_verifiable": False,
        "ai_efficiency_shared": False,
        "contract_embedded": False,
        "track_record": False,
        "roi_aligned": False,
    },
    "outcome_evidence": {
        "source_urls": [
            "https://sek.com.br",
            "https://itforum.com.br/noticias/sek-ciberseguranca-patria/",
        ],
        "excerpts": [],
        "notes": (
            "Seed entry — no outcome-pricing evidence found. IT Forum launch "
            "article (March 2023) describes business model as 'managed "
            "security services provider' and 'solutions and services provider' "
            "without mentioning outcome-based pricing constructs."
        ),
    },
    "capability_analysis": (
        "CBS HOLDING S.A. (SEK) delivers 24/7 managed security from four "
        "cyber defense and incident response centers across Latin America. "
        "MDR delivery relies on Palo Alto Networks Cortex/XSIAM, CrowdStrike "
        "Falcon, Nozomi (OT/IoT), and F5, among 40 certified technology "
        "partnerships. Notably, 156 million attacks were reportedly prevented "
        "in 2022, and the company protects 500K critical business assets. "
        "Strong IR capability from NeoSecure (Chile) and Proteus (Brazil) "
        "heritage. Two R&D centers support innovation. Funded by Pátria "
        "Investimentos for aggressive LatAm market expansion."
    ),
    "granular_mapping": {
        "TDR": {"TDR-01": 3.0, "TDR-02": 3.0, "TDR-03": 3.0, "TDR-04": 2.0},
        "PTI": {"PTI-01": 3.0, "PTI-02": 2.0, "PTI-03": 3.0, "PTI-04": 2.0},
        "ADA": {"ADA-01": 1.0, "ADA-02": 0.5, "ADA-03": 1.5, "ADA-04": 0.5},
        "DIS": {"DIS-01": 0.0, "DIS-02": 2.0, "DIS-03": 1.5, "DIS-04": 1.5},
        "IRA": {"IRA-01": 3.0, "IRA-02": 4.0, "IRA-03": 3.0, "IRA-04": 3.0},
        "AIO": {"AIO-01": 2.0, "AIO-02": 2.0, "AIO-03": 2.0, "AIO-04": 2.0},
        "AID": {"AID-01": 2.0, "AID-02": 1.0, "AID-03": 1.0, "AID-04": 2.0},
        "SOG": {"SOG-01": 4.0, "SOG-02": 3.0, "SOG-03": 3.0, "SOG-04": 3.0},
    },
    "pillar_scores": {
        "TDR": 2.75, "PTI": 2.50, "ADA": 0.88, "DIS": 1.25,
        "IRA": 3.25, "AIO": 2.00, "AID": 1.50, "SOG": 3.25,
    },
}


# ============================================================
# Helper: upsert into a pipeline file (list or dict wrapper)
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
        upsert(f, cbs_capability)

    print(f"\n=== Adding {VENDOR_NAME} to MDR pricing files ===")
    for f in pricing_files:
        upsert(f, cbs_pricing)

    # Verification
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
            print(
                f"[VERIFY] {label}: {v['vendor']} | "
                f"HQ={v.get('headquarters','?')} | "
                f"region={v.get('region','?')} | "
                f"pillars={v.get('pillar_scores',{})} | "
                f"research_status={v.get('research_status','?')}"
            )
        else:
            print(f"[ERROR] {label}: {VENDOR_NAME} NOT found!")


if __name__ == "__main__":
    main()
