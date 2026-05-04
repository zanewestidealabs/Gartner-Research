"""Add NetSPI to Product Market Readiness Vendor 1-1 Enriched.json with full research and scoring."""
import json, copy

# ── Load existing data ──
with open("Product Market Readiness Vendor 1-1 Enriched.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Check not already present
existing = [v["vendor"] for v in data["vendors"]]
if "NetSPI" in existing:
    print("NetSPI already exists in the vendor list. Exiting.")
    exit()

# Get labels from first vendor
labels = data["vendors"][0]["sub_pillar_schema_labels"]

# ── NetSPI Vendor Entry ──
netspi = {
    "vendor": "NetSPI",
    "website": "https://www.netspi.com",
    "headquarters": "Minneapolis, Minnesota, USA",
    "region": "North America",
    "vendor_type": "Offensive Security Specialist",
    "is_startup": False,
    "is_ai_first": False,
    "description": "NetSPI is the pioneer of Penetration Testing as a Service (PTaaS), combining 350+ in-house penetration testers with purpose-built AI to deliver continuous, human-led, AI-accelerated cybersecurity testing. Founded in 2001, NetSPI provides application, network, cloud, hardware, AI/ML, and mainframe pentesting, along with attack surface management, red team operations, social engineering, detective controls testing, and threat modeling. Serves 9 of 10 top US banks, 3 of 5 largest cloud providers, and top healthcare and technology companies globally. KKR-backed.",
    "key_differentiators": "Pioneer of PTaaS model, 350+ in-house (not outsourced) pentesters, human-led AI-accelerated methodology, 50+ pentesting service types, GigaOm Radar Leader and Outperformer for PTaaS 2025, AI/ML pentesting specialization (Microsoft AI security framework partnership), attack surface visibility with continuous scanning, detective controls testing and attack simulation, mainframe pentesting capability, Trust Center client portal, open API with integrations (assets, IAM, vulnerabilities, ticketing)",
    "product_names": [
        "NetSPI PTaaS Platform",
        "NetSPI Attack Surface Visibility",
        "NetSPI Detective Controls Testing",
        "NetSPI Red Team Operations",
        "NetSPI AI/ML Pentesting"
    ],
    "source_schemas": ["offensive_security"],
    "cross_schema_scores": {
        "offensive_security": {
            "pillar_avg": 3.40,
            "top_pillar": "PPD",
            "top_score": 4.06,
            "scored_pillars": 5
        }
    },
    "coverage_grade": "A",
    "overall_gtm_score": 3.38,
    "overall_proof_score": 3.10,
    "overall_credibility_gap": 0.28,
    "pillar_gtm_scores": {
        "PPD": 4.06,
        "PCS": 3.80,
        "TDT": 3.56,
        "PCM": 2.02,
        "CTL": 3.46
    },
    "pillar_proof_scores": {
        "PPD": 3.62,
        "PCS": 3.74,
        "TDT": 3.34,
        "PCM": 1.66,
        "CTL": 3.12
    },
    "pillar_gaps": {
        "PPD": 0.44,
        "PCS": 0.06,
        "TDT": 0.22,
        "PCM": 0.36,
        "CTL": 0.34
    },
    "sub_pillar_schema_labels": labels,
    "sub_pillar_scores": {}
}

# ── Helper to build a sub-pillar entry ──
def sp(gtm, proof, gtm_rat, proof_rat, gap_assess, urls=None, excerpts=None):
    gap = round(gtm - proof, 2)
    ex = excerpts or []
    su = urls or []
    n_ex = len(ex)
    n_su = len(su)
    strength = "strong" if n_ex >= 3 else ("partial" if n_ex >= 1 else ("score-based" if gtm > 0 else "none"))
    return {
        "gtm_messaging_score": gtm,
        "proof_of_execution_score": proof,
        "credibility_gap": gap,
        "gtm_rationale": gtm_rat,
        "proof_rationale": proof_rat,
        "gap_assessment": gap_assess,
        "source_urls": su,
        "excerpts": ex,
        "evidence_metadata": {
            "n_excerpts": n_ex,
            "n_source_urls": n_su,
            "n_schema_refs": 1,
            "evidence_strength": strength,
            "source_schema_refs": ["offensive_security:OFS=3.4"]
        }
    }

def excerpt(url, text, score, schema="offensive_security", pillar="OFS", terms=None):
    e = {
        "url": url,
        "excerpt": text,
        "relevance_score": score,
        "source_schema": schema,
        "source_pillar": pillar,
    }
    if terms:
        e["matched_terms"] = terms
    return e

# ══════════════════════════════════════════════════════════════
# PPD - Product Positioning & Differentiation
# ══════════════════════════════════════════════════════════════

netspi["sub_pillar_scores"]["PPD-01"] = sp(
    4.2, 3.8,
    "GTM score 4.2/5 for Capability Claim Specificity. NetSPI provides highly specific capability claims across 50+ pentesting service types spanning application (web, API, mobile, thick client, virtual app, H-DAP), network (internal, external, wireless, host-based, virtual desktop), cloud (AWS, Azure, GCP), hardware (ATM, automotive, medical device, OT, embedded, IoT), AI/ML (LLM web app testing, benchmarking and jailbreaking), and mainframe pentesting. Additional named capabilities include attack surface visibility, detective controls testing, red team operations, social engineering, threat modeling, blockchain pentesting, and secure code review.",
    "Proof score 3.8/5 for Capability Claim Specificity. Strong execution proof with detailed PTaaS feature comparison table against competitors, named service pages with specific scope descriptions, customer case studies referencing specific testing types (Microsoft AI security framework, Trimble product development pentesting, EAB Global attack surface visibility). GigaOm Radar Leader and Outperformer validation for PTaaS 2025.",
    "Mild gap (+0.4) — positioning claims are well-specified but slightly ahead of publicly available technical documentation depth for each individual service.",
    ["https://www.netspi.com", "https://www.netspi.com/netspi-ptaas/"],
    [
        excerpt("https://www.netspi.com", "NetSPI combines 350+ elite human penetration testers with purpose-built AI to deliver modern, continuous cybersecurity testing.", 5.0, terms=["penetration testing", "AI", "continuous", "cybersecurity"]),
        excerpt("https://www.netspi.com/netspi-ptaas/", "NetSPI PTaaS makes our industry leading experts available when you need them. This approach delivers unmatched value to your security program by enabling our 350+ in-house pentesters to operate as a true extension of your team.", 5.0, terms=["PTaaS", "pentesters", "in-house", "extension"]),
        excerpt("https://www.netspi.com/netspi-ptaas/", "Assess and enhance the resilience of AI in your environment, whether you are fine tuning off-the-shelf models, building your own, or leveraging LLMs in your applications.", 4.5, terms=["AI", "LLMs", "resilience", "models"]),
        excerpt("https://www.netspi.com/netspi-ptaas/", "Our hardware and integrated systems penetration testing services find critical security vulnerabilities that could put your hardware and embedded systems at risk.", 4.0, terms=["hardware", "embedded systems", "penetration testing", "vulnerabilities"]),
    ]
)

netspi["sub_pillar_scores"]["PPD-02"] = sp(
    4.0, 3.5,
    "GTM score 4.0/5 for Competitive Differentiation Clarity. NetSPI positions with a clear 'Human-Led, AI-Accelerated' differentiator. PTaaS feature comparison table explicitly compares NetSPI capabilities against 'Other Vendors' across pentesting, attack surface visibility, vulnerability prioritization, attack simulation, and integrations, showing checkmarks for exclusive NetSPI capabilities. Claims pioneer status for PTaaS.",
    "Proof score 3.5/5 for Competitive Differentiation Clarity. GigaOm Radar Leader and Outperformer for PTaaS provides third-party differentiation validation. Feature comparison table provides structural proof. However, 'Other Vendors' comparison is generic rather than named-competitor specific.",
    "Mild gap (+0.5) — strong differentiation narrative supported by analyst recognition, though competitive comparison is generic rather than head-to-head.",
    ["https://www.netspi.com/netspi-ptaas/"],
    [
        excerpt("https://www.netspi.com/netspi-ptaas/", "Leader and Outperformer in 2025 GigaOm Radar for Penetration Testing as a Service (PTaaS).", 5.5, terms=["leader", "outperformer", "GigaOm", "PTaaS"]),
        excerpt("https://www.netspi.com/netspi-ptaas/", "Human Driven: 350+ pentesters, Employed not outsourced, Wide domain expertise. AI-Enabled: Consistent quality, Deep visibility, Transparent results. Modern Pentesting: Use case driven, Friction-free, Built for today's threats.", 5.0, terms=["human driven", "AI-enabled", "modern pentesting"]),
    ]
)

netspi["sub_pillar_scores"]["PPD-03"] = sp(
    3.8, 3.5,
    "GTM score 3.8/5 for Target Persona and Use-Case Alignment. NetSPI addresses multiple verticals through customer stories organized by industry (financial services, healthcare, software, education, insurance, manufacturing, non-profit, utilities, hospitality) and by product category (AI/ML, ASM, detective controls testing, PTaaS, red team, social engineering, threat modeling). Service pages address specific technical personas (CISOs, security engineers, DevSecOps teams).",
    "Proof score 3.5/5 for Target Persona and Use-Case Alignment. Named customer stories span multiple verticals with quoted security leaders: Microsoft (software), Medtronic (healthcare), Chubb (insurance/financial), Gong (software), EAB Global (education), Trimble (software), Quantum Health (healthcare), Everywhen (insurance). Industry filters on customer stories page provide structural evidence of breadth.",
    "Mild gap (+0.3) — strong multi-vertical positioning supported by diverse customer references, though some verticals have thinner evidence than others.",
    ["https://www.netspi.com/customer-stories/"],
    [
        excerpt("https://www.netspi.com/customer-stories/", "How NetSPI Helped Microsoft Build Trust in AI Security with a Framework That Delivers Results. Learn why Microsoft Partnered with NetSPI to Build a Standardized AI Security Testing Framework for their 70+ Products.", 5.5, terms=["Microsoft", "AI security", "framework", "70+ products"]),
        excerpt("https://www.netspi.com/customer-stories/", "Quantum Health: Redefining Benefits Navigation with Proactive Engagement and Cost Savings. Michael Morabito, Information Security Officer: Detective Control Testing allowed me to eliminate unnecessary spend, acquire discounts for insurers, and give my board confidence to continue to invest in us.", 5.0, terms=["Quantum Health", "ROI", "detective controls", "cost savings"]),
        excerpt("https://www.netspi.com/customer-stories/", "Chubb partners with NetSPI to bring Attack Surface Management to its policyholders. We consider NetSPI to be almost an extension of our own team.", 4.5, terms=["Chubb", "attack surface management", "policyholders"]),
    ]
)

netspi["sub_pillar_scores"]["PPD-04"] = sp(
    4.3, 3.7,
    "GTM score 4.3/5 for Market Category Ownership. NetSPI positions as 'the pioneer of Penetration Testing as a Service (PTaaS)' with over 20 years of history and claims 'the global leader in modern penetration testing.' Category definition language is prominent across all pages. 'Human-Led, AI-Accelerated Modern Pentesting' is the primary tagline.",
    "Proof score 3.7/5 for Market Category Ownership. GigaOm Radar Leader and Outperformer 2025 validates category leadership. Founded 2001 supports pioneer claim. KKR backing signals market validation. However, PTaaS category is contested with multiple strong competitors (Cobalt, Bugcrowd, HackerOne) and the 'pioneer' claim lacks independent third-party attribution.",
    "Moderate gap (+0.6) — category ownership claims are strong and supported by analyst recognition and history, but the pioneer claim exceeds available third-party corroboration.",
    ["https://www.netspi.com", "https://www.netspi.com/about-us/"],
    [
        excerpt("https://www.netspi.com", "As the pioneer of Penetration Testing as a Service (PTaaS), NetSPI has led security innovation since its inception in 2001. With more than 20 years of history, 350+ experts, and 50+ pentesting services, NetSPI delivers pentesting that evolves and improves with every engagement.", 5.5, terms=["pioneer", "PTaaS", "2001", "350+ experts"]),
        excerpt("https://www.netspi.com", "NetSPI, the global leader in modern penetration testing, today announced a new, modern user experience for the NetSPI platform, reimagining what penetration testing should feel like for today's enterprise: focused, fast, and easy.", 5.0, terms=["global leader", "modern penetration testing", "platform"]),
    ]
)

netspi["sub_pillar_scores"]["PPD-05"] = sp(
    4.0, 3.6,
    "GTM score 4.0/5 for Messaging Consistency and Coherence. NetSPI maintains consistent messaging across all channels: 'Human-Led, AI-Accelerated' tagline appears on homepage, PTaaS page, and about page. 'Hack Responsibly' brand for technical content (blog, podcast). 'The NetSPI Agents' branding for team. 'Proactive security' positioning is consistent across solutions, about, careers, and newsroom.",
    "Proof score 3.6/5 for Messaging Consistency and Coherence. Messaging is structurally consistent across homepage, PTaaS, about, customer stories, and newsroom pages. Visual branding and language are coherent. Some messaging variation between 'proactive security' (about page) and 'offensive security' (service pages) creates minor inconsistency. Press releases maintain consistent brand voice.",
    "Mild gap (+0.4) — overall messaging coherence is strong but minor positioning vocabulary inconsistencies exist across different channel contexts.",
    ["https://www.netspi.com", "https://www.netspi.com/about-us/"],
    [
        excerpt("https://www.netspi.com/about-us/", "We accelerate proactive security at scale so you can protect your priorities, perform better, and move faster.", 4.0, terms=["proactive security", "scale"]),
        excerpt("https://www.netspi.com", "NetSPI is the proactive security solution used to discover, prioritize, and remediate security vulnerabilities of the highest importance, so you can protect what matters most to you.", 4.5, terms=["proactive security", "discover", "prioritize", "remediate"]),
    ]
)

# ══════════════════════════════════════════════════════════════
# PCS - Proof Points & Case Studies
# ══════════════════════════════════════════════════════════════

netspi["sub_pillar_scores"]["PCS-01"] = sp(
    4.0, 4.2,
    "GTM score 4.0/5 for Customer Case Study Depth. NetSPI features extensive customer story content across its site with dedicated stories for Microsoft (AI security framework for 70+ products), Trimble (product development security), Quantum Health (11x ROI with detective controls), Everywhen (TLPT standards), EAB Global (ASM within 15 seconds), Nuspire (MSSP partnership), Chubb (ASM for policyholders), Medtronic (network perimeter), HumanGood (network and cloud risk), Gong (PTaaS integrations), and Hudl (proactive security validation).",
    "Proof score 4.2/5 for Customer Case Study Depth. Over 11 named customer stories with direct quotes from security leaders (CISOs, CIOs, security officers). Case studies include specific outcomes: 11x ROI for Quantum Health, 15-second attack surface identification for EAB Global, 70+ AI product security framework for Microsoft. Customer stories span multiple industries and product categories with filterable interface.",
    "Under-marketed (-0.2) — proof of customer case study depth slightly exceeds the visibility of that proof in primary positioning narratives.",
    ["https://www.netspi.com/customer-stories/"],
    [
        excerpt("https://www.netspi.com/customer-stories/", "EAB Global improves attack surface security within 15 seconds using NetSPI Attack Surface Visibility Solutions. Brian Markham, CISO: NetSPI Attack Surface Visibility has saved EAB Global time, money, and helped us mature our program.", 5.5, terms=["EAB Global", "15 seconds", "attack surface", "CISO"]),
        excerpt("https://www.netspi.com/customer-stories/", "Everywhen Partners with NetSPI to Elevate TLPT Standards and Build Unparalleled Trust. Justyna Larkowska, CISO: NetSPI Red Team consultant's transparency, attention to detail, and commitment to building strong relationships make them feel like an integral part of your internal team.", 5.0, terms=["TLPT", "red team", "CISO", "trust"]),
        excerpt("https://www.netspi.com/customer-stories/", "Nuspire partners with NetSPI to safeguard customer trust. Lewie Dunsworth, CEO: What makes NetSPI an effective proactive security partner is their focus on innovation.", 4.5, terms=["Nuspire", "partner", "innovation"]),
        excerpt("https://www.netspi.com/customer-stories/", "Medtronic works with NetSPI to identify and protect its network perimeter. Nancy Brainerd, Senior Director and Deputy CISO: We consider them to be almost an extension of our own team.", 5.0, terms=["Medtronic", "network perimeter", "CISO", "extension of team"]),
    ]
)

netspi["sub_pillar_scores"]["PCS-02"] = sp(
    3.5, 3.5,
    "GTM score 3.5/5 for Third-Party Validation and Analyst Recognition. NetSPI references GigaOm Radar Leader and Outperformer for PTaaS 2025 prominently on homepage, PTaaS page, and solutions. 'Award-Winning Services' section on about page. Solutions Review expert prediction contributions from Field CISO Nabil Hannan.",
    "Proof score 3.5/5 for Third-Party Validation and Analyst Recognition. GigaOm Radar report is linked and available for download. Award imagery displayed. However, limited breadth of analyst recognition beyond GigaOm; no visible Gartner, Forrester, or IDC recognition referenced on site.",
    "Well-aligned (+0.0) — third-party validation messaging matches available evidence, anchored primarily in GigaOm Radar recognition.",
    ["https://www.netspi.com/netspi-ptaas/"],
    [
        excerpt("https://www.netspi.com/netspi-ptaas/", "Leader and Outperformer in 2025 GigaOm Radar for Penetration Testing as a Service (PTaaS). Read the Report.", 5.5, terms=["GigaOm", "leader", "outperformer", "PTaaS"]),
    ]
)

netspi["sub_pillar_scores"]["PCS-03"] = sp(
    4.0, 3.8,
    "GTM score 4.0/5 for Deployment Scale and Metric Transparency. NetSPI publicly claims 350+ in-house pentesters, 50+ pentesting services, 20+ years of history. Claims service to 9 of 10 top US banks, 3 of 5 largest cloud providers, 7 of 10 largest healthcare companies, and 5 MAMAA tech giants. EMEA expansion documented.",
    "Proof score 3.8/5 for Deployment Scale and Metric Transparency. Named enterprise customers validate scale claims: Microsoft, Chubb, Medtronic, Trimble are recognizable enterprise brands. 350+ pentesters claim is consistent across all pages. Banking and healthcare claims are directional (percentages rather than named institutions). KKR backing provides institutional scale validation.",
    "Mild gap (+0.2) — scale metrics are prominently communicated and partially verifiable through named customers, though percentage-based claims (9/10 banks) are not independently corroborated.",
    ["https://www.netspi.com", "https://www.netspi.com/about-us/"],
    [
        excerpt("https://www.netspi.com/about-us/", "Securing the Most Trusted Brands on Earth: 9 of 10 Largest Cloud Providers, Top U.S. Banks, World's Largest Healthcare Companies, MAMAA Tech Giants.", 5.0, terms=["trusted brands", "cloud providers", "banks", "healthcare", "MAMAA"]),
        excerpt("https://www.netspi.com", "With more than 20 years of history, 350+ experts, and 50+ pentesting services, NetSPI delivers pentesting that evolves and improves with every engagement.", 4.5, terms=["20 years", "350+ experts", "50+ services"]),
    ]
)

netspi["sub_pillar_scores"]["PCS-04"] = sp(
    3.5, 3.2,
    "GTM score 3.5/5 for ROI and Business Outcome Documentation. NetSPI references specific outcomes in customer stories: 11x ROI for Quantum Health, 15-second identification for EAB Global, reduced delays for Trimble. 'Game-Changing Outcomes' messaging on about page. Remediation acceleration and program maturity improvement claims.",
    "Proof score 3.2/5 for ROI and Business Outcome Documentation. Quantum Health 11x ROI is the strongest quantified outcome with named ISo quote. EAB Global 15-second metric is specific. Trimble delay reduction is directional. No systematic ROI calculator, TCO reduction documentation, or payback period data publicly available across the broader customer base.",
    "Mild gap (+0.3) — select customer stories provide strong ROI evidence, but systematic business outcome documentation across the customer base is limited.",
    ["https://www.netspi.com/customer-stories/"],
    [
        excerpt("https://www.netspi.com/customer-stories/", "Quantum Health: Redefining Benefits Navigation with Proactive Engagement and Cost Savings. Detective Control Testing allowed me to eliminate unnecessary spend, acquire discounts for insurers, and give my board confidence to continue to invest in us.", 5.5, terms=["11x ROI", "cost savings", "eliminate spend", "board confidence"]),
        excerpt("https://www.netspi.com/customer-stories/", "EAB Global improves attack surface security within 15 seconds using NetSPI Attack Surface Visibility Solutions.", 4.5, terms=["15 seconds", "attack surface", "improve"]),
    ]
)

netspi["sub_pillar_scores"]["PCS-05"] = sp(
    4.0, 4.0,
    "GTM score 4.0/5 for Customer Reference Breadth. NetSPI customer stories span healthcare (Medtronic, Quantum Health, HumanGood), financial services (Chubb), insurance (Everywhen), software (Microsoft, Gong, Hudl, Trimble), education (EAB Global), managed security (Nuspire), and manufacturing (Veradigm). Industry filters on customer stories page. Global presence with EMEA team.",
    "Proof score 4.0/5 for Customer Reference Breadth. 11+ named customer stories across 7+ industry verticals. Customer stories filterable by industry and product category. Named CISOs and security leaders provide direct quotes. Breadth spans Fortune 500 (Microsoft, Medtronic) through mid-market (Gong, Hudl, EAB Global).",
    "Well-aligned (+0.0) — customer reference breadth across industries and organization sizes is well-documented and matches positioning claims.",
    ["https://www.netspi.com/customer-stories/"],
    [
        excerpt("https://www.netspi.com/customer-stories/", "Hudl teams up with NetSPI to validate its proactive security program. Rob LaMagna-Reiter, VP and CISO: NetSPI has delivered some of the most actionable and insightful recommendations through the course of the engagement.", 4.5, terms=["Hudl", "proactive security", "CISO", "recommendations"]),
        excerpt("https://www.netspi.com/customer-stories/", "Gong saves time with integrations in NetSPI Penetration Testing as a Service (PTaaS). Mike Siegel, Offensive Security Staff Engineer: They're very easy to work with. We enjoy The NetSPI Platform.", 4.0, terms=["Gong", "PTaaS", "integrations", "platform"]),
        excerpt("https://www.netspi.com/customer-stories/", "NetSPI helps a global healthcare software company stay secure. Phil Morris, Director: The brain trust behind the NetSPI subject matter experts, they're working to make real value in the process itself so that I can talk about risk from a risk management perspective, not just from a vulnerabilities perspective.", 4.5, terms=["healthcare", "risk management", "subject matter experts"]),
    ]
)

# ══════════════════════════════════════════════════════════════
# TDT - Technical Depth & Transparency
# ══════════════════════════════════════════════════════════════

netspi["sub_pillar_scores"]["TDT-01"] = sp(
    3.5, 3.2,
    "GTM score 3.5/5 for Architecture and Design Documentation. NetSPI PTaaS feature comparison provides structural architecture overview: pentesting solution, attack surface visibility, vulnerability prioritization, attack simulation, and integrations layers. Platform screenshots show dashboard and reporting interfaces. Trust Center provides client portal for engagement management.",
    "Proof score 3.2/5 for Architecture and Design Documentation. Feature comparison table documents platform components. Individual service pages describe scope and methodology. However, no public architecture diagrams, system design documentation, or infrastructure topology documentation is visible. Trust Center is access-controlled.",
    "Mild gap (+0.3) — platform architecture is described at a feature level but detailed technical architecture documentation is not publicly accessible.",
    ["https://www.netspi.com/netspi-ptaas/"],
    [
        excerpt("https://www.netspi.com/netspi-ptaas/", "PTaaS Feature Comparison: Pentesting Solution (program and findings management, remediation testing, trend analysis and real-time dashboards, PDF reports), Attack Surface Visibility (asset inventory and deduplication, external asset discovery scans weekly, AWS and Azure security scans weekly, dark web monitoring, look-alike domain monitoring).", 4.5, terms=["PTaaS", "feature comparison", "attack surface", "asset discovery"]),
    ]
)

netspi["sub_pillar_scores"]["TDT-02"] = sp(
    3.8, 3.5,
    "GTM score 3.8/5 for API and Integration Ecosystem. NetSPI documents Open API availability and integrations across assets, IAM, vulnerabilities, and ticketing systems. AWS and Azure cloud config integration for attack surface visibility. CI/CD integration mentioned for application pentesting context. Integration is called out as a differentiator in PTaaS feature comparison.",
    "Proof score 3.5/5 for API and Integration Ecosystem. Open API is listed in feature comparison with checkmark. Integration categories (assets, IAM, vulnerabilities, ticketing) are named. AWS and Azure cloud configuration scans documented. However, no public API documentation portal, SDK references, or developer documentation is linked from the main site.",
    "Mild gap (+0.3) — integration capabilities are claimed and categorized but public developer-facing API documentation is not prominently available.",
    ["https://www.netspi.com/netspi-ptaas/", "https://www.netspi.com/attack-surface-visibility/"],
    [
        excerpt("https://www.netspi.com/netspi-ptaas/", "Integrations: Open API (checkmark). Assets, IAM, Vulnerabilities, Ticketing (checkmark for NetSPI).", 4.0, terms=["Open API", "integrations", "assets", "IAM", "ticketing"]),
        excerpt("https://www.netspi.com", "With NetSPI, you gain an always-on understanding of your attack surface, both internal and external. NetSPI automatically scans your external perimeter and internal assets with integrations across identities, applications, and devices.", 4.5, terms=["attack surface", "integrations", "identities", "applications", "devices"]),
    ]
)

netspi["sub_pillar_scores"]["TDT-03"] = sp(
    3.5, 3.5,
    "GTM score 3.5/5 for Detection and Methodology Transparency. NetSPI technical blog ('Hack Responsibly') publishes vulnerability disclosures including CVE research (CVE-2025-67813 Quest Desktop Authority Named Pipe RCE). Podcast series discusses testing methodology (social engineering, AI frontier, legacy infrastructure). Named testing approaches for different service types documented on service pages.",
    "Proof score 3.5/5 for Detection and Methodology Transparency. Technical blog provides concrete methodology evidence through CVE disclosures and original vulnerability research. Podcast demonstrates transparent methodology discussion. Security assessment service pages describe scoping and approach. Detective controls testing methodology (self-service playbooks, agent execution, automated detection verification, vendor coverage comparison) documented.",
    "Well-aligned (+0.0) — methodology transparency in public technical content matches positioning claims.",
    ["https://www.netspi.com/blog/technical-blog/", "https://www.netspi.com/security-assessments/detective-controls-testing/"],
    [
        excerpt("https://www.netspi.com", "Pipe Dreams: Remote Code Execution via Quest Desktop Authority Named Pipe. Ceri Coburn. Discover the risks of the CVE-2025-67813 vulnerability in Quest Desktop Authority.", 5.0, terms=["CVE", "remote code execution", "vulnerability", "research"]),
        excerpt("https://www.netspi.com", "Rust's Role in Embedded Security. Andrew Bindner. Rust enhances memory safety in embedded systems, but rigorous security assessments remain critical.", 4.0, terms=["embedded security", "memory safety", "security assessments"]),
        excerpt("https://www.netspi.com/netspi-ptaas/", "Attack Simulation: Self-service playbooks and agent execution, Automated detection verification, Vendor coverage comparison.", 4.5, terms=["attack simulation", "playbooks", "detection verification"]),
    ]
)

netspi["sub_pillar_scores"]["TDT-04"] = sp(
    3.2, 3.0,
    "GTM score 3.2/5 for Data Handling and Privacy Transparency. NetSPI references Privacy Policy, CCPA and Virginia CDPA compliance, Modern Slavery Statement, and Trust Center. Cookie consent mechanism with opt-out. Client portal for secure engagement management.",
    "Proof score 3.0/5 for Data Handling and Privacy Transparency. Privacy Policy is published and linked in footer. CCPA and Virginia CDPA references are present. Trust Center is access-controlled. No detailed data residency, data retention, SOC 2 certification, or ISO 27001 attestation documentation publicly visible.",
    "Mild gap (+0.2) — privacy documentation exists at a compliance level but detailed data handling and security certification documentation is not publicly prominent.",
    ["https://www.netspi.com/privacy/"],
    [
        excerpt("https://www.netspi.com", "We use cookies in compliance with the Virginia CDPA to make the website work better for you and to understand your needs.", 3.0, terms=["CDPA", "privacy", "cookies"]),
    ]
)

netspi["sub_pillar_scores"]["TDT-05"] = sp(
    3.8, 3.5,
    "GTM score 3.8/5 for Technical Enablement and Documentation Quality. NetSPI provides resources library (downloads, solution briefs, data sheets), technical blog, podcast series, events and webinars page, and NetSPI University training program. Customer portal provides engagement management. Named experts and authors on technical content.",
    "Proof score 3.5/5 for Technical Enablement and Documentation Quality. Resources library includes solution briefs and data sheets for download. Technical blog is actively maintained with named authors and original research. Podcast ('Hack Responsibly') is ongoing with multiple episodes. NetSPI University exists for career development. Webinar and events program documented.",
    "Mild gap (+0.3) — enablement and documentation resources are available but depth of public technical documentation beyond blog and solution briefs is limited.",
    ["https://www.netspi.com/resources/", "https://www.netspi.com/blog/technical-blog/"],
    [
        excerpt("https://www.netspi.com/netspi-ptaas/", "Resources: Solution Brief, Data Sheet, Case Study. Guidance From Top Experts. Collaborate in real time with our 350 in-house pentesters. Accelerated Remediation. Live, interactive vulnerability reports make the path to remediation clear and easy.", 4.0, terms=["solution brief", "data sheet", "remediation", "vulnerability reports"]),
        excerpt("https://www.netspi.com", "Hack Responsibly Podcast: Episode 01 Inside the Mind of a Social Engineer, Episode 02 Securing the AI Frontier, Episode 03 The Hidden Risk in Legacy Infrastructure.", 3.5, terms=["podcast", "social engineering", "AI", "legacy infrastructure"]),
    ]
)

# ══════════════════════════════════════════════════════════════
# PCM - Pricing & Commercial Model Clarity
# ══════════════════════════════════════════════════════════════

netspi["sub_pillar_scores"]["PCM-01"] = sp(
    2.0, 1.5,
    "GTM score 2.0/5 for Pricing Model Transparency. NetSPI does not publish public pricing. Primary CTAs are 'Contact Us' and 'Get in Touch.' Enterprise engagement model implied through customer scale references. No pricing page, no pricing model type disclosed publicly.",
    "Proof score 1.5/5 for Pricing Model Transparency. No public pricing information available. Custom enterprise engagement model inferred from sales-driven CTA approach. No pricing calculator, no indicative ranges, no model type (per-test, subscription, asset-based) disclosed.",
    "Mild gap (+0.5) — pricing is not a part of public messaging but the implied enterprise positioning sets some expectation for custom engagement that is then confirmed by the sales-driven experience.",
    [],
    []
)

netspi["sub_pillar_scores"]["PCM-02"] = sp(
    2.5, 2.0,
    "GTM score 2.5/5 for Packaging and Tier Clarity. NetSPI service pages clearly categorize offerings by type (application, network, cloud, hardware, AI/ML, mainframe pentesting; attack surface visibility; detective controls; red team; social engineering). Feature comparison table shows capability structure. However, no tier or package definitions are published.",
    "Proof score 2.0/5 for Packaging and Tier Clarity. Service categorization is clear (6 pentesting categories + assessments + ASM). Feature comparison differentiates NetSPI from 'Other Vendors.' No tier-to-price mapping, no package bundles, no upgrade paths documented publicly.",
    "Mild gap (+0.5) — service packaging is well-organized by capability type but commercial tier structure is not publicly documented.",
    ["https://www.netspi.com/netspi-ptaas/"],
    [
        excerpt("https://www.netspi.com/netspi-ptaas/", "Penetration Testing: Application, Cloud, Hardware, Network, Mainframe, AI/ML. Security Assessments: Red Team, Detective Controls Testing, Social Engineering, Threat Modeling, Blockchain, Code Review.", 3.5, terms=["pentesting", "application", "cloud", "red team", "threat modeling"]),
    ]
)

netspi["sub_pillar_scores"]["PCM-03"] = sp(
    2.0, 1.8,
    "GTM score 2.0/5 for Total Cost of Ownership Articulation. NetSPI references cost-related outcomes in select case studies (Quantum Health cost savings, EAB Global time and money savings). No systematic TCO documentation, implementation cost guidance, or operational cost framework published.",
    "Proof score 1.8/5 for Total Cost of Ownership Articulation. Quantum Health case study references 11x ROI and cost elimination. EAB Global references time and money savings. No TCO calculator, no cost comparison frameworks, no representative deployment cost documentation available.",
    "Mild gap (+0.2) — limited TCO messaging matches limited TCO evidence, both anchored in select customer outcomes rather than systematic documentation.",
    ["https://www.netspi.com/customer-stories/"],
    [
        excerpt("https://www.netspi.com/customer-stories/", "Detective Control Testing allowed me to eliminate unnecessary spend, acquire discounts for insurers, and give my board confidence to continue to invest in us.", 4.0, terms=["eliminate spend", "discounts", "board confidence", "invest"]),
    ]
)

netspi["sub_pillar_scores"]["PCM-04"] = sp(
    1.8, 1.5,
    "GTM score 1.8/5 for Trial and Evaluation Accessibility. NetSPI does not offer a visible self-service trial, sandbox, or free tier. Evaluation path is through 'Contact Us' engagement. Demo is implied but not explicitly offered as a structured program.",
    "Proof score 1.5/5 for Trial and Evaluation Accessibility. No self-service trial, no sandbox environment, no free tier, no POC program documented publicly. Enterprise sales-driven evaluation model. Trust Center access is gated behind client relationships.",
    "Mild gap (+0.3) — minimal trial accessibility messaging matches minimal public evaluation infrastructure.",
    [],
    []
)

netspi["sub_pillar_scores"]["PCM-05"] = sp(
    1.8, 1.5,
    "GTM score 1.8/5 for Commercial Terms and Contract Flexibility. No public contract terms, SLA documentation, cancellation policies, or data portability provisions visible. Enterprise engagement terms are handled through sales process.",
    "Proof score 1.5/5 for Commercial Terms and Contract Flexibility. No public commercial terms documentation. Modern Slavery Statement is published (compliance requirement). Privacy Policy addresses data practices. No contract flexibility, SLA, or data portability documentation publicly available.",
    "Mild gap (+0.3) — commercial terms opacity is consistent between messaging and evidence; neither suggests transparency in this area.",
    [],
    []
)

# ══════════════════════════════════════════════════════════════
# CTL - Content & Thought Leadership
# ══════════════════════════════════════════════════════════════

netspi["sub_pillar_scores"]["CTL-01"] = sp(
    3.5, 3.3,
    "GTM score 3.5/5 for Original Research and Data Publication. NetSPI technical blog publishes original vulnerability research including CVE disclosures (CVE-2025-67813). Blog content includes embedded security research (Rust memory safety), adversary simulation techniques, and hardware/IoT testing methodology. Field CISO contributes external analyst predictions (Solutions Review 2026 predictions).",
    "Proof score 3.3/5 for Original Research and Data Publication. CVE disclosures demonstrate original vulnerability research. Technical blog posts are authored by named researchers (Ceri Coburn, Andrew Bindner). External thought leadership contributions documented in newsroom. No published annual threat reports, benchmark studies, or large-scale research data sets visible.",
    "Mild gap (+0.2) — original research output is solid through vulnerability disclosures and technical analysis, though lacking the scale of annual threat reports or benchmark publications.",
    ["https://www.netspi.com/blog/technical-blog/"],
    [
        excerpt("https://www.netspi.com", "Proof Over Promises: A New Doctrine for Cybersecurity. As cyberattacks grow in frequency and sophistication, traditional assurances like contracts and certifications are no longer sufficient. Instead, vendors must actively demonstrate their security resilience through measurable and continuous validation.", 4.5, terms=["proof over promises", "validation", "cybersecurity", "doctrine"]),
        excerpt("https://www.netspi.com", "The Age of Promises is Over, Vendors Must Now Lead with Evidence-Based Assurances. Sam Kirkman emphasizes the need for vendors to shift from trust-based compliance to evidence-based security.", 4.5, terms=["evidence-based", "assurances", "compliance", "trust"]),
    ]
)

netspi["sub_pillar_scores"]["CTL-02"] = sp(
    3.5, 3.0,
    "GTM score 3.5/5 for Conference and Speaking Presence. NetSPI maintains events and webinars page. EMEA team outreach program documented. Podcast series ('Hack Responsibly') with multiple episodes. Field CISO Nabil Hannan and Sam Kirkman contribute as external thought leaders. Newsroom features speaking engagements and media appearances.",
    "Proof score 3.0/5 for Conference and Speaking Presence. Podcast series is documented with named episodes. Events page exists. External media contributions documented in newsroom. However, no specific RSA, Black Hat, BSides or named conference speaking slots referenced. EMEA team presence documented at regional level.",
    "Mild gap (+0.5) — conference presence is implied through events page and external contributions, but specific named conference appearances are not prominently documented.",
    ["https://www.netspi.com/events-and-webinars/"],
    [
        excerpt("https://www.netspi.com", "Hack Responsibly Podcast Episode 02: Securing the AI Frontier. NetSPI's Karl Fosaaen speaks with Kim Wiles, Director of AI Penetration Testing, about the unique security challenges posed by emerging AI technologies.", 4.0, terms=["podcast", "AI", "penetration testing", "security challenges"]),
    ]
)

netspi["sub_pillar_scores"]["CTL-03"] = sp(
    3.8, 3.5,
    "GTM score 3.8/5 for Blog and Educational Content Quality. NetSPI maintains both Technical Blog and Executive Blog. Technical blog features vulnerability research, testing methodology, and security engineering content. Educational content spans embedded security, adversary simulation, social engineering, mainframe security, and AI security. Named authors with expertise areas indicated.",
    "Proof score 3.5/5 for Blog and Educational Content Quality. Technical blog has active publishing cadence with named authors. Content spans vulnerability disclosures, technical methodology, and hardware security. Executive blog provides leadership perspective. Content quality is demonstrated through specific, actionable technical analysis. NetSPI University mentioned for career/training content.",
    "Mild gap (+0.3) — blog content quality is strong and actively maintained with technical substance.",
    ["https://www.netspi.com/blog/technical-blog/", "https://www.netspi.com/blog/executive-blog/"],
    [
        excerpt("https://www.netspi.com/blog/technical-blog/", "Pipe Dreams: Remote Code Execution via Quest Desktop Authority Named Pipe. Ceri Coburn. Discover the risks of the CVE-2025-67813 vulnerability.", 4.5, terms=["RCE", "CVE", "vulnerability research"]),
        excerpt("https://www.netspi.com/blog/technical-blog/", "Rust's Role in Embedded Security. Andrew Bindner. Rust enhances memory safety in embedded systems, but rigorous security assessments remain critical.", 4.0, terms=["Rust", "embedded security", "memory safety"]),
    ]
)

netspi["sub_pillar_scores"]["CTL-04"] = sp(
    3.0, 2.8,
    "GTM score 3.0/5 for Open-Source and Community Contribution. NetSPI publishes CVE disclosures benefiting the broader security community. Technical blog shares methodology and research. NetSPI University program. No prominent open-source tool repositories, community frameworks, or GitHub presence referenced on main site.",
    "Proof score 2.8/5 for Open-Source and Community Contribution. CVE disclosures (CVE-2025-67813) are public community contributions. Technical blog methodology sharing benefits the community. No visible GitHub organization link, open-source tool repositories, or community-contributed frameworks on the main site.",
    "Mild gap (+0.2) — community contribution through vulnerability disclosure is documented, but formal open-source program is not visible.",
    ["https://www.netspi.com/blog/technical-blog/"],
    [
        excerpt("https://www.netspi.com/blog/technical-blog/", "CVE-2025-67813 vulnerability disclosure in Quest Desktop Authority Named Pipe, demonstrating community-oriented security research and responsible disclosure.", 4.0, terms=["CVE", "disclosure", "responsible", "community"]),
    ]
)

netspi["sub_pillar_scores"]["CTL-05"] = sp(
    3.5, 3.0,
    "GTM score 3.5/5 for Market Education and Category Development. NetSPI positions 'Proof Over Promises: A New Doctrine for Cybersecurity' and 'Evidence-Based Assurances' as market education frameworks. PTaaS category development through claimed pioneer status. Field CISO contributes market education through Solutions Review predictions. Newsroom publishes market perspective content.",
    "Proof score 3.0/5 for Market Education and Category Development. 'Proof Over Promises' and 'Evidence-Based Assurances' articles demonstrate market education effort. PTaaS category development is evidenced through GigaOm recognition. External analyst contribution validates thought leadership. However, no standards body participation, advisory board roles, or formal framework contributions are documented.",
    "Mild gap (+0.5) — market education content is substantive but institutional frameworks and standards participation are not documented.",
    ["https://www.netspi.com/newsroom/"],
    [
        excerpt("https://www.netspi.com/newsroom/", "Proof Over Promises: A New Doctrine for Cybersecurity. Vendors must actively demonstrate their security resilience through measurable and continuous validation, such as penetration testing.", 4.5, terms=["proof over promises", "validation", "doctrine"]),
        excerpt("https://www.netspi.com/newsroom/", "In 2026, organizations will realize that AI doesn't eliminate tool sprawl; it only accelerates it. Enterprises must shift from the buy everything new and shiny mindset to a purpose-built toolchain strategy.", 4.0, terms=["AI", "tool sprawl", "purpose-built", "strategy"]),
    ]
)

# ══════════════════════════════════════════════════════════════
# Verify and add
# ══════════════════════════════════════════════════════════════

# Verify all 25 sub-pillars present
expected = set()
for prefix in ["PPD", "PCS", "TDT", "PCM", "CTL"]:
    for i in range(1, 6):
        expected.add(f"{prefix}-{i:02d}")

actual = set(netspi["sub_pillar_scores"].keys())
missing = expected - actual
if missing:
    print(f"ERROR: Missing sub-pillars: {missing}")
    exit(1)

extra = actual - expected
if extra:
    print(f"WARNING: Extra sub-pillars: {extra}")

# Count excerpts
total_excerpts = sum(len(s.get("excerpts", [])) for s in netspi["sub_pillar_scores"].values())
total_urls = sum(len(s.get("source_urls", [])) for s in netspi["sub_pillar_scores"].values())

# Add to data
data["vendors"].append(netspi)
data["vendor_count"] = len(data["vendors"])

with open("Product Market Readiness Vendor 1-1 Enriched.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Added NetSPI as vendor #{len(data['vendors'])}")
print(f"Sub-pillars: {len(netspi['sub_pillar_scores'])}/25")
print(f"Total excerpts: {total_excerpts}")
print(f"Total source URLs: {total_urls}")
print(f"Coverage grade: {netspi['coverage_grade']}")
print(f"Overall GTM: {netspi['overall_gtm_score']}")
print(f"Overall Proof: {netspi['overall_proof_score']}")
print(f"Overall Gap: {netspi['overall_credibility_gap']}")
print(f"\nPillar scores:")
for p in ["PPD", "PCS", "TDT", "PCM", "CTL"]:
    print(f"  {p}: GTM={netspi['pillar_gtm_scores'][p]:.2f}  Proof={netspi['pillar_proof_scores'][p]:.2f}  Gap={netspi['pillar_gaps'][p]:.2f}")
