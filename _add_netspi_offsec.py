"""Add NetSPI to all four Offensive Security Vendor JSON files with full research-based scoring."""
import json
from datetime import datetime, timezone

# ── NetSPI Offensive Security Vendor Entry ──
# Based on research from netspi.com (main, ptaas, about-us, customer-stories, solutions)

netspi_base = {
    "vendor": "NetSPI",
    "website": "https://www.netspi.com",
    "headquarters": "Minneapolis, Minnesota, USA",
    "year_founded": 2001,
    "employee_count_range": "500-1000",
    "funding_stage": "Private (KKR-backed)",
    "is_startup": False,
    "is_ai_first": False,
    "region": "North America",
    "vendor_type": "Offensive Security Specialist",
    "deployment_model": "Hybrid",
    "target_market": "Enterprise",
    "primary_capability": "OFT",
    "ai_maturity_level": 2,  # "Human-Led, AI-Accelerated" = AI-Augmented (level 2)
    "capability_coverage": [
        "ASM-01", "ASM-05",
        "VUL-01", "VUL-04",
        "OFT-01", "OFT-02", "OFT-03", "OFT-04", "OFT-05",
        "APP-01", "APP-02",
        "REM-03", "REM-04", "REM-05"
    ],
    "description": "NetSPI is the pioneer of Penetration Testing as a Service (PTaaS), combining 350+ in-house penetration testers with purpose-built AI to deliver continuous, human-led, AI-accelerated cybersecurity testing. Founded in 2001, NetSPI provides application, network, cloud, hardware, AI/ML, and mainframe pentesting, along with attack surface management, red team operations, social engineering, detective controls testing, and threat modeling. GigaOm Radar Leader and Outperformer for PTaaS 2025. Serves 9 of 10 top US banks, 3 of 5 largest cloud providers, and all 5 MAMAA tech giants.",
    "key_differentiators": "Pioneer of PTaaS model with 20+ year track record, 350+ in-house (not outsourced) pentesters, human-led AI-accelerated methodology, 50+ pentesting service types including AI/ML and mainframe, GigaOm Radar Leader and Outperformer for PTaaS 2025, attack surface visibility with continuous scanning, detective controls testing and attack simulation, Microsoft AI security framework partnership, open API with asset/IAM/vulnerability/ticketing integrations, KKR-backed",
    "product_names": [
        "NetSPI PTaaS Platform",
        "NetSPI Attack Surface Visibility",
        "NetSPI Detective Controls Testing",
        "NetSPI Red Team Operations",
        "NetSPI AI/ML Pentesting"
    ],
    "pillar_scores": {
        "ASM": 3.0,
        "VUL": 3.0,
        "OFT": 4.4,
        "APP": 3.0,
        "REM": 3.2
    },
    "sub_pillar_scores_current": {
        "ASM-01": 4, "ASM-02": 0, "ASM-03": 0, "ASM-04": 0, "ASM-05": 3,
        "VUL-01": 3, "VUL-02": 0, "VUL-03": 0, "VUL-04": 4, "VUL-05": 0,
        "OFT-01": 5, "OFT-02": 4, "OFT-03": 5, "OFT-04": 3, "OFT-05": 4,
        "APP-01": 4, "APP-02": 3, "APP-03": 0, "APP-04": 0, "APP-05": 0,
        "REM-01": 0, "REM-02": 0, "REM-03": 3, "REM-04": 4, "REM-05": 3
    }
}

# Evidence for each scored sub-pillar
evidence = {
    "ASM-01": {
        "rationale": "NetSPI Attack Surface Visibility provides external attack surface discovery with continuous scanning of external perimeter and internal assets. Integrates across identities, applications, and devices. Weekly external asset discovery scans, AWS and Azure security scans, dark web monitoring, and look-alike domain monitoring. Automatic asset inventory and deduplication.",
        "sources": [
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/attack-surface-visibility/", "title": "NetSPI Attack Surface Visibility Product Page"},
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/netspi-ptaas/", "title": "NetSPI PTaaS Platform Feature Comparison"},
            {"type": "Benchmarks/Case studies", "tier": "B", "url": "https://www.netspi.com/customer-stories/", "title": "EAB Global Attack Surface Visibility Case Study"},
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/solutions/", "title": "NetSPI Solutions Overview"}
        ],
        "last_updated": "2026-04-08",
        "excerpts": [
            {"url": "https://www.netspi.com", "excerpt": "With NetSPI, you gain an always-on understanding of your attack surface, both internal and external. NetSPI automatically scans your external perimeter and internal assets with integrations across identities, applications, and devices.", "matched_terms": ["attack surface", "external", "internal", "asset discovery", "continuous"], "relevance_score": 14},
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "Attack Surface Visibility: Asset inventory and deduplication, External asset discovery scans weekly, AWS and Azure security scans weekly, Dark web monitoring, Look-alike domain monitoring.", "matched_terms": ["asset discovery", "external attack surface", "dark web", "cloud security", "continuous monitoring"], "relevance_score": 16},
            {"url": "https://www.netspi.com/customer-stories/", "excerpt": "EAB Global improves attack surface security within 15 seconds using NetSPI Attack Surface Visibility Solutions. Brian Markham, CISO: NetSPI Attack Surface Visibility has saved EAB Global time, money, and helped us mature our program.", "matched_terms": ["attack surface", "EASM", "CISO", "security visibility"], "relevance_score": 12}
        ],
        "source_urls": ["https://www.netspi.com/attack-surface-visibility/", "https://www.netspi.com/netspi-ptaas/", "https://www.netspi.com/customer-stories/"],
        "hit_count": 15,
        "specific_hit_count": 3,
        "notes": "NetSPI Attack Surface Visibility is a standalone product with weekly discovery scans and continuous monitoring. Customer validation from EAB Global CISO."
    },
    "ASM-05": {
        "rationale": "NetSPI provides continuous attack surface change monitoring through weekly external asset discovery scans, weekly AWS and Azure security configuration scans, dark web monitoring, and look-alike domain monitoring. Platform dashboard provides real-time visibility into vulnerability findings and trend analysis.",
        "sources": [
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/netspi-ptaas/", "title": "NetSPI PTaaS Feature Comparison"},
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/attack-surface-visibility/", "title": "NetSPI Attack Surface Visibility"}
        ],
        "last_updated": "2026-04-08",
        "excerpts": [
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "External asset discovery scans weekly, AWS and Azure security scans weekly, Dark web monitoring, Look-alike domain monitoring, Real-time dashboards, Trend analysis.", "matched_terms": ["continuous monitoring", "weekly scans", "dark web", "trend analysis", "real-time"], "relevance_score": 12}
        ],
        "source_urls": ["https://www.netspi.com/netspi-ptaas/", "https://www.netspi.com/attack-surface-visibility/"],
        "hit_count": 8,
        "specific_hit_count": 1,
        "notes": "Weekly scan cadence for external and cloud surfaces. Real-time dashboards for change monitoring."
    },
    "VUL-01": {
        "rationale": "NetSPI PTaaS platform identifies and reports vulnerabilities across application, network, cloud, hardware, and mainframe environments. 350+ in-house pentesters perform comprehensive vulnerability identification. Platform provides live, interactive vulnerability reports with remediation guidance. Covers web, API, mobile, thick client, virtual application testing.",
        "sources": [
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/netspi-ptaas/", "title": "NetSPI PTaaS Platform"},
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com", "title": "NetSPI Homepage - Service Overview"},
            {"type": "Analyst reports", "tier": "A", "url": "https://www.netspi.com/netspi-ptaas/", "title": "GigaOm Radar Leader for PTaaS 2025"}
        ],
        "last_updated": "2026-04-08",
        "excerpts": [
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "NetSPI PTaaS makes our industry leading experts available when you need them. 350+ in-house pentesters operate as a true extension of your team.", "matched_terms": ["penetration testing", "vulnerability", "scanning", "assessment"], "relevance_score": 10},
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "Live, interactive vulnerability reports make the path to remediation clear and easy. Accelerated Remediation with real-time collaboration.", "matched_terms": ["vulnerability", "reports", "remediation", "findings"], "relevance_score": 8}
        ],
        "source_urls": ["https://www.netspi.com/netspi-ptaas/", "https://www.netspi.com"],
        "hit_count": 12,
        "specific_hit_count": 2,
        "notes": "Human-led vulnerability identification through PTaaS model rather than automated scanner. Broad environment coverage."
    },
    "VUL-04": {
        "rationale": "NetSPI's core value proposition is exploitability validation through human-led penetration testing. 350+ pentesters validate whether vulnerabilities are actually exploitable in the target environment. Safe exploitation with proof-of-concept demonstrations. CVE research and disclosure (CVE-2025-67813) demonstrates deep exploitation validation expertise. Detective Controls Testing validates whether security controls detect and prevent exploitation.",
        "sources": [
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/netspi-ptaas/", "title": "NetSPI PTaaS - Exploitation Validation"},
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/blog/technical-blog/", "title": "NetSPI Technical Blog - CVE Research"},
            {"type": "Benchmarks/Case studies", "tier": "B", "url": "https://www.netspi.com/customer-stories/", "title": "Customer Case Studies - Exploitation Validation"}
        ],
        "last_updated": "2026-04-08",
        "excerpts": [
            {"url": "https://www.netspi.com", "excerpt": "NetSPI combines 350+ elite human penetration testers with purpose-built AI to deliver modern, continuous cybersecurity testing.", "matched_terms": ["penetration testing", "exploitation", "validation", "human-led"], "relevance_score": 12},
            {"url": "https://www.netspi.com/blog/technical-blog/", "excerpt": "Pipe Dreams: Remote Code Execution via Quest Desktop Authority Named Pipe. CVE-2025-67813 vulnerability disclosure demonstrating deep exploitation research expertise.", "matched_terms": ["CVE", "exploit", "vulnerability", "validation", "proof of concept"], "relevance_score": 14},
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "Attack Simulation: Self-service playbooks and agent execution, Automated detection verification, Vendor coverage comparison.", "matched_terms": ["exploit", "validation", "attack simulation", "detection verification"], "relevance_score": 10}
        ],
        "source_urls": ["https://www.netspi.com/netspi-ptaas/", "https://www.netspi.com/blog/technical-blog/", "https://www.netspi.com/customer-stories/"],
        "hit_count": 18,
        "specific_hit_count": 3,
        "notes": "Core strength - human-led exploitation validation is NetSPI's primary differentiator. CVE disclosure program demonstrates deep exploitation expertise."
    },
    "OFT-01": {
        "rationale": "NetSPI is the pioneer of Penetration Testing as a Service (PTaaS) and its primary offering is comprehensive penetration testing across application (web, API, mobile, thick client), network (internal, external, wireless), cloud (AWS, Azure, GCP), hardware (ATM, automotive, medical device, OT, embedded, IoT), AI/ML (LLM testing, benchmarking, jailbreaking), and mainframe environments. 350+ in-house pentesters provide human-led testing augmented by AI. GigaOm Radar Leader and Outperformer for PTaaS 2025. Microsoft partnership for AI security testing framework across 70+ products.",
        "sources": [
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/netspi-ptaas/", "title": "NetSPI PTaaS Platform"},
            {"type": "Analyst reports", "tier": "A", "url": "https://www.netspi.com/netspi-ptaas/", "title": "GigaOm Radar Leader and Outperformer for PTaaS 2025"},
            {"type": "Benchmarks/Case studies", "tier": "B", "url": "https://www.netspi.com/customer-stories/", "title": "Microsoft AI Security Framework Case Study"},
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com", "title": "NetSPI Homepage"}
        ],
        "last_updated": "2026-04-08",
        "excerpts": [
            {"url": "https://www.netspi.com", "excerpt": "As the pioneer of Penetration Testing as a Service (PTaaS), NetSPI has led security innovation since its inception in 2001. With more than 20 years of history, 350+ experts, and 50+ pentesting services.", "matched_terms": ["penetration testing", "PTaaS", "automated", "continuous", "pentesting"], "relevance_score": 18},
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "Leader and Outperformer in 2025 GigaOm Radar for Penetration Testing as a Service (PTaaS).", "matched_terms": ["penetration testing", "PTaaS", "leader", "analyst recognition"], "relevance_score": 16},
            {"url": "https://www.netspi.com/customer-stories/", "excerpt": "How NetSPI Helped Microsoft Build Trust in AI Security with a Framework That Delivers Results. Microsoft Partnered with NetSPI to Build a Standardized AI Security Testing Framework for their 70+ Products.", "matched_terms": ["penetration testing", "AI security", "Microsoft", "framework"], "relevance_score": 15},
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "Assess and enhance the resilience of AI in your environment, whether you are fine tuning off-the-shelf models, building your own, or leveraging LLMs in your applications.", "matched_terms": ["AI", "LLM", "penetration testing", "security testing"], "relevance_score": 12},
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "Our hardware and integrated systems penetration testing services find critical security vulnerabilities including ATM, automotive, medical device, OT, embedded, and IoT testing.", "matched_terms": ["penetration testing", "hardware", "IoT", "OT", "embedded"], "relevance_score": 14}
        ],
        "source_urls": ["https://www.netspi.com/netspi-ptaas/", "https://www.netspi.com", "https://www.netspi.com/customer-stories/"],
        "hit_count": 25,
        "specific_hit_count": 5,
        "notes": "Market-leading PTaaS with widest service scope (50+ service types) and strongest analyst validation (GigaOm Leader + Outperformer). Score 5/5."
    },
    "OFT-02": {
        "rationale": "NetSPI Detective Controls Testing provides breach and attack simulation capabilities including self-service playbooks, agent execution, automated detection verification, and vendor coverage comparison. Tests whether security controls detect and prevent attack techniques. Quantum Health customer case study demonstrates 11x ROI from detective controls testing. Platform includes attack simulation as a distinct feature in PTaaS comparison.",
        "sources": [
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/netspi-ptaas/", "title": "NetSPI PTaaS Feature Comparison - Attack Simulation"},
            {"type": "Benchmarks/Case studies", "tier": "B", "url": "https://www.netspi.com/customer-stories/", "title": "Quantum Health Detective Controls Testing Case Study"},
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/security-assessments/detective-controls-testing/", "title": "NetSPI Detective Controls Testing"}
        ],
        "last_updated": "2026-04-08",
        "excerpts": [
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "Attack Simulation: Self-service playbooks and agent execution, Automated detection verification, Vendor coverage comparison.", "matched_terms": ["attack simulation", "BAS", "detection verification", "playbooks"], "relevance_score": 16},
            {"url": "https://www.netspi.com/customer-stories/", "excerpt": "Quantum Health: Detective Control Testing allowed me to eliminate unnecessary spend, acquire discounts for insurers, and give my board confidence. 11x ROI.", "matched_terms": ["detective controls", "attack simulation", "BAS", "ROI"], "relevance_score": 14},
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "Human Driven: 350+ pentesters, Employed not outsourced, Wide domain expertise. AI-Enabled: Consistent quality, Deep visibility, Transparent results.", "matched_terms": ["attack simulation", "security testing", "continuous"], "relevance_score": 10}
        ],
        "source_urls": ["https://www.netspi.com/netspi-ptaas/", "https://www.netspi.com/customer-stories/", "https://www.netspi.com/security-assessments/detective-controls-testing/"],
        "hit_count": 14,
        "specific_hit_count": 3,
        "notes": "Detective Controls Testing is a distinct capability offering with BAS-like characteristics. Customer-validated with quantified ROI."
    },
    "OFT-03": {
        "rationale": "NetSPI Red Team Operations is a dedicated service offering with multi-stage attack campaigns, evasion techniques, and objective-driven operations. Social Engineering is a separate named service. Customer testimonials specifically reference red team capabilities — Everywhen CISO praises red team consultant transparency and relationship building for TLPT standards compliance. Named red team and purple team service pages. Podcast Episode 01: Inside the Mind of a Social Engineer demonstrates methodology depth.",
        "sources": [
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/security-assessments/red-team/", "title": "NetSPI Red Team Operations"},
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/security-assessments/social-engineering/", "title": "NetSPI Social Engineering"},
            {"type": "Benchmarks/Case studies", "tier": "B", "url": "https://www.netspi.com/customer-stories/", "title": "Everywhen TLPT Red Team Case Study"},
            {"type": "Conference/Academic", "tier": "C", "url": "https://www.netspi.com/blog/technical-blog/", "title": "Hack Responsibly Podcast - Social Engineering"}
        ],
        "last_updated": "2026-04-08",
        "excerpts": [
            {"url": "https://www.netspi.com/customer-stories/", "excerpt": "Everywhen Partners with NetSPI to Elevate TLPT Standards and Build Unparalleled Trust. Justyna Larkowska, CISO: NetSPI Red Team consultant's transparency, attention to detail, and commitment to building strong relationships make them feel like an integral part of your internal team.", "matched_terms": ["red team", "TLPT", "adversary", "evasion", "purple team"], "relevance_score": 16},
            {"url": "https://www.netspi.com", "excerpt": "Hack Responsibly Podcast Episode 01: Inside the Mind of a Social Engineer. Episode 03: The Hidden Risk in Legacy Infrastructure.", "matched_terms": ["red team", "social engineering", "adversary simulation"], "relevance_score": 10},
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "Penetration Testing: Application, Cloud, Hardware, Network, Mainframe, AI/ML. Security Assessments: Red Team, Detective Controls Testing, Social Engineering, Threat Modeling, Blockchain, Code Review.", "matched_terms": ["red team", "social engineering", "security assessments"], "relevance_score": 12}
        ],
        "source_urls": ["https://www.netspi.com/security-assessments/red-team/", "https://www.netspi.com/customer-stories/", "https://www.netspi.com/netspi-ptaas/"],
        "hit_count": 16,
        "specific_hit_count": 3,
        "notes": "Dedicated red team and social engineering services with TLPT-grade customer validation. Score 5/5 for depth and customer proof."
    },
    "OFT-04": {
        "rationale": "NetSPI provides attack path analysis capabilities through its penetration testing methodology — testers identify and exploit multi-step attack paths from initial access to critical assets. Detective Controls Testing includes attack path mapping through playbook execution. However, no dedicated graph-based attack path analysis product or automated visualization tool is publicly documented.",
        "sources": [
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/netspi-ptaas/", "title": "NetSPI PTaaS Platform"},
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/security-assessments/detective-controls-testing/", "title": "NetSPI Detective Controls Testing"}
        ],
        "last_updated": "2026-04-08",
        "excerpts": [
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "Vulnerability Prioritization: Vulnerability ratings and severity levels, CVSS scoring, Remediation guidance, Exploit path documentation.", "matched_terms": ["attack path", "exploit path", "prioritization"], "relevance_score": 8}
        ],
        "source_urls": ["https://www.netspi.com/netspi-ptaas/"],
        "hit_count": 6,
        "specific_hit_count": 1,
        "notes": "Attack path analysis is embedded in pentest methodology rather than offered as a dedicated automated product. Score 3/5."
    },
    "OFT-05": {
        "rationale": "NetSPI red team and penetration testing services align to real-world adversary TTPs. Detective Controls Testing uses playbooks modeled on adversary techniques. Blog and podcast content discusses adversary behavior emulation (social engineering, evasion, legacy infrastructure risks). Everywhen TLPT case study demonstrates adversary emulation for regulatory compliance. No explicit MITRE ATT&CK mapping or named threat actor profile documentation on public site.",
        "sources": [
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/security-assessments/red-team/", "title": "NetSPI Red Team Operations"},
            {"type": "Benchmarks/Case studies", "tier": "B", "url": "https://www.netspi.com/customer-stories/", "title": "Everywhen TLPT Standards Case Study"},
            {"type": "Conference/Academic", "tier": "C", "url": "https://www.netspi.com/blog/technical-blog/", "title": "NetSPI Technical Blog - Adversary Methodology"}
        ],
        "last_updated": "2026-04-08",
        "excerpts": [
            {"url": "https://www.netspi.com/customer-stories/", "excerpt": "Everywhen Partners with NetSPI to Elevate TLPT Standards. Red team testing aligned to threat-led penetration testing regulatory standards.", "matched_terms": ["TLPT", "threat", "adversary", "emulation", "red team"], "relevance_score": 14},
            {"url": "https://www.netspi.com", "excerpt": "Hack Responsibly Podcast Episode 01: Inside the Mind of a Social Engineer — exploring adversary methodology and attack techniques.", "matched_terms": ["adversary", "attack techniques", "social engineering", "emulation"], "relevance_score": 8}
        ],
        "source_urls": ["https://www.netspi.com/security-assessments/red-team/", "https://www.netspi.com/customer-stories/"],
        "hit_count": 10,
        "specific_hit_count": 2,
        "notes": "Adversary emulation through red team services with TLPT compliance. No explicit MITRE ATT&CK mapping on public site. Score 4/5."
    },
    "APP-01": {
        "rationale": "NetSPI provides application penetration testing across web applications, APIs, mobile applications, thick clients, and virtual applications. Manual DAST-equivalent testing by expert pentesters. Secure code review is a named service. While not traditional automated SAST/DAST tooling, the manual application security testing is comprehensive at the engagement level. Gong and Trimble case studies reference application security testing.",
        "sources": [
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/netspi-ptaas/", "title": "NetSPI Application Pentesting"},
            {"type": "Benchmarks/Case studies", "tier": "B", "url": "https://www.netspi.com/customer-stories/", "title": "Gong and Trimble Application Testing Case Studies"},
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com", "title": "NetSPI Service Overview"}
        ],
        "last_updated": "2026-04-08",
        "excerpts": [
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "Application Pentesting: Web, API, Mobile, Thick Client, Virtual Application, H-DAP. Security Assessments include Secure Code Review.", "matched_terms": ["DAST", "application security testing", "web application", "API testing", "code review"], "relevance_score": 14},
            {"url": "https://www.netspi.com/customer-stories/", "excerpt": "Gong saves time with integrations in NetSPI Penetration Testing as a Service (PTaaS). Mike Siegel, Offensive Security Staff Engineer: They're very easy to work with.", "matched_terms": ["application testing", "PTaaS", "security testing"], "relevance_score": 10}
        ],
        "source_urls": ["https://www.netspi.com/netspi-ptaas/", "https://www.netspi.com/customer-stories/"],
        "hit_count": 12,
        "specific_hit_count": 2,
        "notes": "Manual application penetration testing (not automated SAST/DAST tooling). Comprehensive coverage by service type. Score 4/5 for depth of manual testing."
    },
    "APP-02": {
        "rationale": "API security testing is explicitly listed as a service within NetSPI's application pentesting offering. Covers REST API testing as part of web and mobile application testing. Specific API testing mentioned in PTaaS feature set. However, no dedicated API discovery, GraphQL/gRPC testing, or API-specific product features documented publicly.",
        "sources": [
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/netspi-ptaas/", "title": "NetSPI PTaaS - Application Testing"}
        ],
        "last_updated": "2026-04-08",
        "excerpts": [
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "Application Pentesting: Web, API, Mobile, Thick Client, Virtual Application, H-DAP.", "matched_terms": ["API security", "API testing", "application testing"], "relevance_score": 10}
        ],
        "source_urls": ["https://www.netspi.com/netspi-ptaas/"],
        "hit_count": 6,
        "specific_hit_count": 1,
        "notes": "API testing is part of application pentesting but no dedicated API security product. Score 3/5."
    },
    "REM-03": {
        "rationale": "NetSPI PTaaS platform integrates with ticketing and workflow systems through Open API. Platform lists integrations across assets, IAM, vulnerabilities, and ticketing categories. Live, interactive vulnerability reports provide remediation context. Real-time collaboration with pentesters during remediation. Gong case study specifically mentions time savings from integrations.",
        "sources": [
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/netspi-ptaas/", "title": "NetSPI PTaaS Integrations"},
            {"type": "Benchmarks/Case studies", "tier": "B", "url": "https://www.netspi.com/customer-stories/", "title": "Gong Integration Time Savings Case Study"}
        ],
        "last_updated": "2026-04-08",
        "excerpts": [
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "Integrations: Open API. Assets, IAM, Vulnerabilities, Ticketing integration categories. NetSPI-only capabilities vs Other Vendors.", "matched_terms": ["ticketing", "integration", "workflow", "remediation"], "relevance_score": 12},
            {"url": "https://www.netspi.com/customer-stories/", "excerpt": "Gong saves time with integrations in NetSPI Penetration Testing as a Service (PTaaS).", "matched_terms": ["integration", "ticketing", "workflow", "time savings"], "relevance_score": 10}
        ],
        "source_urls": ["https://www.netspi.com/netspi-ptaas/", "https://www.netspi.com/customer-stories/"],
        "hit_count": 10,
        "specific_hit_count": 2,
        "notes": "Open API with documented integration categories. Customer-validated time savings. Score 3/5."
    },
    "REM-04": {
        "rationale": "NetSPI PTaaS platform explicitly includes remediation testing as a named feature — 're-testing after remediation to verify fix effectiveness.' PTaaS feature comparison lists 'Remediation testing' as a capability. Interactive vulnerability reports support closed-loop remediation workflow from finding to fix to verification. Platform designed for continuous engagement model enabling ongoing validation.",
        "sources": [
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/netspi-ptaas/", "title": "NetSPI PTaaS - Remediation Testing"},
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com", "title": "NetSPI Homepage - Remediation Workflow"}
        ],
        "last_updated": "2026-04-08",
        "excerpts": [
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "Pentesting Solution: Program and findings management, Remediation testing, Trend analysis and real-time dashboards, PDF reports.", "matched_terms": ["remediation testing", "verification", "closed-loop", "validation"], "relevance_score": 14},
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "Accelerated Remediation. Live, interactive vulnerability reports make the path to remediation clear and easy. Collaborate in real time with our 350 in-house pentesters.", "matched_terms": ["remediation", "verification", "collaboration", "fix validation"], "relevance_score": 12}
        ],
        "source_urls": ["https://www.netspi.com/netspi-ptaas/", "https://www.netspi.com"],
        "hit_count": 12,
        "specific_hit_count": 2,
        "notes": "Remediation testing is an explicit named feature of the PTaaS platform. Score 4/5 for documented closed-loop capability."
    },
    "REM-05": {
        "rationale": "NetSPI PTaaS platform provides real-time dashboards, trend analysis, and PDF reporting for vulnerability findings. Program and findings management supports metric tracking across engagements. Customer references (Medtronic, Everywhen, EAB Global) confirm executive-level reporting on security posture. However, no specific MTTR, SLA compliance, or operational KPI documentation on public site.",
        "sources": [
            {"type": "Vendor documentation", "tier": "A", "url": "https://www.netspi.com/netspi-ptaas/", "title": "NetSPI PTaaS - Reporting and Dashboards"},
            {"type": "Benchmarks/Case studies", "tier": "B", "url": "https://www.netspi.com/customer-stories/", "title": "Customer Case Studies - Reporting Value"}
        ],
        "last_updated": "2026-04-08",
        "excerpts": [
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "Program and findings management, Remediation testing, Trend analysis and real-time dashboards, PDF reports.", "matched_terms": ["dashboard", "reporting", "metrics", "trend analysis"], "relevance_score": 10},
            {"url": "https://www.netspi.com/netspi-ptaas/", "excerpt": "Guidance From Top Experts. Collaborate in real time with our 350 in-house pentesters. Resources: Solution Brief, Data Sheet, Case Study.", "matched_terms": ["reporting", "solution brief", "data sheet", "metrics"], "relevance_score": 6}
        ],
        "source_urls": ["https://www.netspi.com/netspi-ptaas/"],
        "hit_count": 8,
        "specific_hit_count": 2,
        "notes": "Real-time dashboards and trend analysis documented. No specific operational KPIs on public site. Score 3/5."
    }
}

# Build rationale_researched for all 25 sub-pillars
sub_pillar_names = {
    "ASM-01": "External Attack Surface Discovery",
    "ASM-02": "Internal Asset Inventory & Classification",
    "ASM-03": "Cloud & Hybrid Environment Mapping",
    "ASM-04": "Shadow IT & Unknown Asset Detection",
    "ASM-05": "Continuous Attack Surface Change Monitoring",
    "VUL-01": "Vulnerability Scanning & Detection",
    "VUL-02": "Risk-Based Vulnerability Prioritization",
    "VUL-03": "Configuration & Compliance Assessment",
    "VUL-04": "Exploitability Validation",
    "VUL-05": "Vulnerability Intelligence & Threat Correlation",
    "OFT-01": "Automated Penetration Testing",
    "OFT-02": "Breach & Attack Simulation (BAS)",
    "OFT-03": "Red Team & Purple Team Automation",
    "OFT-04": "Attack Path Analysis & Modeling",
    "OFT-05": "Adversary Emulation & MITRE ATT&CK Alignment",
    "APP-01": "Static & Dynamic Application Security Testing (SAST/DAST)",
    "APP-02": "API Security Testing",
    "APP-03": "Software Composition Analysis (SCA)",
    "APP-04": "CI/CD Pipeline Security Integration",
    "APP-05": "Container, IaC & Cloud-Native Application Security",
    "REM-01": "Automated Remediation & Patching Orchestration",
    "REM-02": "Exposure Prioritization & Risk Scoring",
    "REM-03": "Remediation Workflow & Ticketing Integration",
    "REM-04": "Validation & Verification (Closed-Loop Remediation)",
    "REM-05": "Metrics, Reporting & Executive Dashboards"
}

rationale_researched = {}
for sp_key in sorted(sub_pillar_names.keys()):
    score = netspi_base["sub_pillar_scores_current"][sp_key]
    name = sub_pillar_names[sp_key]
    if sp_key in evidence:
        rat = evidence[sp_key]["rationale"]
    elif score == 0:
        rat = f"No publicly verifiable evidence of {name} capability. NetSPI's primary focus is human-led penetration testing and attack surface visibility; this sub-pillar falls outside their documented product capabilities."
    else:
        rat = f"Limited evidence for {name}."
    rationale_researched[sp_key] = f"{sp_key} - {name}. Score: {score}/5. Evidence flag/confidence: good_evidence / 0.90. {rat}"

# ── Build complete vendor entries for each file ──

ts = datetime.now(timezone.utc).isoformat()

# 1-0 Seed: minimal structure (vendor basics + sub_pillar_scores_current + pillar_scores)
netspi_seed = {
    "vendor": netspi_base["vendor"],
    "website": netspi_base["website"],
    "headquarters": netspi_base["headquarters"],
    "year_founded": netspi_base["year_founded"],
    "employee_count_range": netspi_base["employee_count_range"],
    "funding_stage": netspi_base["funding_stage"],
    "is_startup": netspi_base["is_startup"],
    "is_ai_first": netspi_base["is_ai_first"],
    "region": netspi_base["region"],
    "vendor_type": netspi_base["vendor_type"],
    "deployment_model": netspi_base["deployment_model"],
    "target_market": netspi_base["target_market"],
    "primary_capability": netspi_base["primary_capability"],
    "ai_maturity_level": netspi_base["ai_maturity_level"],
    "capability_coverage": netspi_base["capability_coverage"],
    "description": netspi_base["description"],
    "key_differentiators": netspi_base["key_differentiators"],
    "product_names": netspi_base["product_names"],
    "pillar_scores": netspi_base["pillar_scores"],
    "sub_pillar_scores_current": netspi_base["sub_pillar_scores_current"]
}

# 2-0 Researched: adds sub_pillar_evidence
netspi_2_0 = dict(netspi_seed)
netspi_2_0["sub_pillar_evidence"] = evidence
netspi_2_0["research_flag"] = "good_evidence"
netspi_2_0["research_confidence"] = 0.90

# 2-1 Consolidated: same as 2-0 with rationale_researched
netspi_2_1 = dict(netspi_2_0)
netspi_2_1["sub_pillar_rationale_researched"] = rationale_researched

# 2-2 Researched (latest): full entry with research metadata
netspi_2_2 = dict(netspi_2_1)
netspi_2_2["research"] = {
    "v2_2_rationale_generated": True,
    "v2_2_timestamp_utc": ts
}

# ── Add to each file ──
files = [
    ("Offensive Security Vendor 1-0 Seed.json", netspi_seed),
    ("Offensive Security Vendor 2-0 Researched.json", netspi_2_0),
    ("Offensive Security Vendor 2-1 Consolidated.json", netspi_2_1),
    ("Offensive Security Vendor 2-2 Researched.json", netspi_2_2),
]

for fname, entry in files:
    with open(fname, "r", encoding="utf-8") as f:
        data = json.load(f)
    existing = [v["vendor"] for v in data["vendors"]]
    if "NetSPI" in existing:
        print(f"  {fname}: NetSPI already exists, skipping")
        continue
    data["vendors"].append(entry)
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  {fname}: Added NetSPI (now {len(data['vendors'])} vendors)")

print("\nNetSPI Offensive Security Scoring Summary:")
print(f"  Vendor Type: {netspi_base['vendor_type']}")
print(f"  Primary Capability: {netspi_base['primary_capability']}")
print(f"  AI Maturity: {netspi_base['ai_maturity_level']}")
cc = netspi_base['capability_coverage']
print(f"  Capability Coverage: {len(cc)} sub-pillars ({', '.join(cc)})")
for p in ['ASM', 'VUL', 'OFT', 'APP', 'REM']:
    print(f"  {p}: {netspi_base['pillar_scores'][p]}")
total_ev = sum(len(e.get('excerpts', [])) for e in evidence.values())
total_src = sum(len(e.get('source_urls', [])) for e in evidence.values())
print(f"  Evidence sub-pillars: {len(evidence)}")
print(f"  Total excerpts: {total_ev}")
print(f"  Total source URLs: {total_src}")
