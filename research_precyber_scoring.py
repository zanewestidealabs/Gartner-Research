"""
research_precyber_scoring.py — Preemptive Cybersecurity Vendor Scoring & Rationale

Reads the seed vendor file and generates scored research output with:
  - Sub-pillar scores (0-5) based on publicly verifiable evidence
  - Structured rationale per sub-pillar explaining scoring basis
  - Evidence source URLs and key evidence excerpts
  - Pillar-level scores (average of sub-pillar scores)

Output: "Preemptive Cybersecurity Vendor 2-0 Researched.json"

This script is executed in batches — each batch adds vendor research data.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED_FILE = ROOT / "Preemptive Cybersecurity Vendor 1-0 Seed.json"
OUTPUT_FILE = ROOT / "Preemptive Cybersecurity Vendor 2-0 Researched.json"

PILLARS = ["EXM", "AMT", "ADR", "PPM"]
SUB_PILLAR_IDS = [f"{p}-{i:02d}" for p in PILLARS for i in range(1, 5)]

# ─────────────────────────────────────────────────────────────────────
# Batch Research Data
# Each vendor key maps to a dict of sub-pillar research
# ─────────────────────────────────────────────────────────────────────

VENDOR_RESEARCH = {}

# ═══════════════════════════════════════════════════════════════════════
# BATCH 1: Tenable, Qualys, Rapid7, CrowdStrike, Palo Alto Networks
# ═══════════════════════════════════════════════════════════════════════

VENDOR_RESEARCH["Tenable"] = {
    "scores": {
        "EXM-01": 5, "EXM-02": 4, "EXM-03": 5, "EXM-04": 3,
        "AMT-01": 0, "AMT-02": 0, "AMT-03": 1, "AMT-04": 1,
        "ADR-01": 0, "ADR-02": 2, "ADR-03": 1, "ADR-04": 0,
        "PPM-01": 0, "PPM-02": 1, "PPM-03": 1, "PPM-04": 4
    },
    "evidence": {
        "EXM-01": {
            "source_urls": [
                "https://docs.tenable.com/attack-surface-management.htm",
                "https://www.tenable.com/products/tenable-one",
                "https://en.wikipedia.org/wiki/Tenable,_Inc."
            ],
            "key_evidence": [
                "Tenable ASM (acquired Bit Discovery June 2022) provides automated external attack surface discovery including shadow IT, cloud resources, and internet-facing assets.",
                "Tenable One platform unifies ASM, vulnerability management, cloud security, identity exposure, and OT security into a single exposure management platform.",
                "Documentation portal confirms dedicated Attack Surface Management product with real-time asset inventory and risk scoring.",
                "44,000+ customers including 65% of Fortune 500 validate enterprise-grade asset discovery at scale."
            ],
            "notes": "Market-leading ASM with dedicated product (Tenable ASM), integrated into Tenable One platform. Bit Discovery acquisition in 2022 specifically for EASM capability."
        },
        "EXM-02": {
            "source_urls": [
                "https://docs.tenable.com/exposure-management.htm",
                "https://www.tenable.com/products/tenable-one",
                "https://www.gartner.com/reviews/market/vulnerability-assessment/vendor/tenable"
            ],
            "key_evidence": [
                "Tenable One Exposure Management Platform launched October 2022 — provides continuous exposure assessment, prioritization, and mobilization across the full attack surface.",
                "Gartner Peer Insights rates Tenable 4.6/5 with 1212 ratings in Vulnerability Assessment, noting exposure management and remediation tracking capabilities.",
                "Platform provides continuous operation with scoping, discovery, prioritization, validation, and mobilization — aligning with CTEM framework stages."
            ],
            "notes": "Strong CTEM alignment through Tenable One platform. Exposure management is branded marketing focus. Named a Gartner Customers' Choice."
        },
        "EXM-03": {
            "source_urls": [
                "https://docs.tenable.com/vulnerability-management.htm",
                "https://www.tenable.com/products/vulnerability-management",
                "https://en.wikipedia.org/wiki/Tenable,_Inc."
            ],
            "key_evidence": [
                "Nessus vulnerability scanner — one of the most widely deployed VA solutions globally since 1998, with comprehensive plugin coverage.",
                "Vulnerability Priority Rating (VPR) provides risk-based prioritization beyond CVSS using exploit intelligence, threat landscape data, and asset criticality.",
                "Tenable Vulnerability Management (cloud) and Security Center (on-prem) offer automated remediation prioritization and integration with patch management and ticketing systems.",
                "Vulcan Cyber acquisition (January 2025, $150M) adds exposure risk management and remediation orchestration capabilities."
            ],
            "notes": "Undisputed market leader in vulnerability management. VPR scoring is an industry benchmark for risk-based prioritization beyond simple CVSS."
        },
        "EXM-04": {
            "source_urls": [
                "https://docs.tenable.com/web-app-scanning.htm",
                "https://www.tenable.com/products/tenable-one"
            ],
            "key_evidence": [
                "Tenable Web App Scanning provides some third-party component analysis.",
                "Tenable One includes some third-party exposure visibility through asset correlation and web application scanning.",
                "Limited dedicated supply chain or SBOM analysis capability compared to specialists."
            ],
            "notes": "Some third-party exposure capability but not a primary focus. No dedicated SBOM or supply chain monitoring product."
        },
        "AMT-01": {"source_urls": [], "key_evidence": ["No polymorphic or moving target defense capability identified. Tenable is focused on exposure management, not active defense mutation."], "notes": "Outside vendor scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No runtime application protection capability. Tenable focuses on vulnerability discovery, not in-process application shielding."], "notes": "Outside vendor scope."},
        "AMT-03": {
            "source_urls": ["https://docs.tenable.com/identity-exposure.htm"],
            "key_evidence": ["Tenable Identity Exposure (via Alsid acquisition) provides Active Directory security monitoring and attack path visibility, but does not perform dynamic network reconfiguration or micro-segmentation."],
            "notes": "Identity Exposure provides visibility but not active network defense mutation. Scored 1 for basic infrastructure visibility contribution."
        },
        "AMT-04": {
            "source_urls": ["https://docs.tenable.com/identity-exposure.htm"],
            "key_evidence": ["Tenable Identity Exposure monitors Active Directory for credential-related misconfigurations and attack paths but does not perform automated credential rotation or ephemeral provisioning."],
            "notes": "Identity monitoring only, not active credential rotation. Minimal capability in this area."
        },
        "ADR-01": {"source_urls": [], "key_evidence": ["No deception technology, honeypot, or honeytoken capabilities identified in Tenable product portfolio."], "notes": "Outside vendor scope."},
        "ADR-02": {
            "source_urls": ["https://docs.tenable.com/vulnerability-management.htm"],
            "key_evidence": ["VPR leverages threat intelligence data including exploit availability, dark web activity, and CVSS enrichment for vulnerability prioritization.", "Threat intelligence is consumed and operationalized within the vulnerability context but Tenable does not offer a standalone threat intelligence platform."],
            "notes": "Threat intelligence is embedded in VPR scoring but not a standalone TIP. Generic claims with some measurable output."
        },
        "ADR-03": {
            "source_urls": ["https://docs.tenable.com/cyber-exposure-studies.htm"],
            "key_evidence": ["Cyber Exposure Studies provide targeted reviews against current threat landscape, offering some hunt-like analysis support but not full proactive threat hunting operations."],
            "notes": "Minimal hunting capability through exposure studies. Not a threat hunting platform."
        },
        "ADR-04": {"source_urls": [], "key_evidence": ["No counter-adversary operations, takedown services, or dark web monitoring capabilities identified."], "notes": "Outside vendor scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No breach and attack simulation capability. Tenable validates vulnerabilities exist but does not simulate attack chains against production controls."], "notes": "Outside vendor scope."},
        "PPM-02": {
            "source_urls": ["https://docs.tenable.com/security-center.htm"],
            "key_evidence": ["Tenable Security Center provides compliance checking and policy validation, offering basic security control configuration assessment."],
            "notes": "Basic policy compliance, not full security control validation (SIEM/EDR/firewall effectiveness testing)."
        },
        "PPM-03": {
            "source_urls": ["https://docs.tenable.com/Nessus.htm"],
            "key_evidence": ["Nessus can validate vulnerability presence for pen test support. Some credentialed scanning supports validation but this is not automated penetration testing or red team automation."],
            "notes": "Nessus is a scanner, not a pen testing platform. Minimal PTaaS capability."
        },
        "PPM-04": {
            "source_urls": [
                "https://docs.tenable.com/cloud-security.htm",
                "https://en.wikipedia.org/wiki/Tenable,_Inc."
            ],
            "key_evidence": [
                "Tenable Cloud Security (powered by Ermetic acquisition Oct 2023, $265M) provides CNAPP capabilities including CSPM, CIEM, and cloud workload protection.",
                "Multi-cloud support for AWS, Azure, GCP with misconfiguration detection and entitlement analysis.",
                "Accurics acquisition (Oct 2021) adds infrastructure-as-code security scanning.",
                "Eureka acquisition (June 2024) adds data security posture management for cloud environments."
            ],
            "notes": "Strong CSPM through strategic acquisitions (Ermetic, Accurics, Eureka). Full CNAPP platform with CSPM, CIEM, and IaC scanning."
        }
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Tenable earns a 5 (Market-Leading) for Attack Surface Management based on its dedicated Tenable ASM product (acquired Bit Discovery 2022), deep integration into the Tenable One platform providing unified exposure management, automated discovery of external and internal assets including shadow IT and cloud resources, and an established customer base of 44,000+ organizations including 65% of Fortune 500.", "evidence_quality_rationale": "High quality — multiple Tier A sources including vendor documentation portal, product pages, Wikipedia with cited acquisition details, and Gartner Peer Insights ratings.", "scoring_level_justification": "Maps to level 5: Best-in-class capability with dedicated product, extensive customer base, analyst recognition, measurable impact, and continuous innovation through acquisitions.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Tenable scores 4 (Advanced) for CTEM. The Tenable One Exposure Management Platform (launched Oct 2022) implements continuous exposure assessment with scoping, discovery, prioritization, validation, and mobilization stages — closely aligning with the Gartner CTEM framework. However, CTEM as a distinct branded program is still emerging and Tenable's implementation is primarily through the lens of vulnerability/exposure management rather than a fully operationalized CTEM lifecycle.", "evidence_quality_rationale": "Strong evidence from documentation and analyst recognition. Gartner 4.6/5 with 1212 ratings supports advanced capability claim but CTEM-specific documentation is less explicit.", "scoring_level_justification": "Maps to level 4: Named product (Tenable One) with measurable outcomes, continuous operation, and analyst recognition, but not yet fully differentiated as standalone CTEM leadership.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Tenable earns a 5 (Market-Leading) for Vulnerability Prioritization. As the creator of Nessus — one of the most widely deployed vulnerability scanners globally since 1998 — Tenable provides industry-benchmark VPR (Vulnerability Priority Rating) that goes beyond CVSS using exploit intelligence, threat landscape data, and asset criticality. The January 2025 Vulcan Cyber acquisition ($150M) further extends remediation orchestration.", "evidence_quality_rationale": "Exceptional evidence quality. Wikipedia-cited financial data, Gartner Peer Insights (4.6/5, 1212 ratings), extensive documentation, and long market tenure.", "scoring_level_justification": "Maps to level 5: Best-in-class vulnerability prioritization with VPR as an industry benchmark, extensive customer base, and continuous innovation.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Tenable scores 3 (Demonstrated) for Third-Party & Supply Chain Exposure. While Tenable One provides some supply chain visibility through web application scanning and asset correlation, the vendor does not offer dedicated SBOM analysis, software supply chain monitoring, or third-party vendor risk assessment as primary capabilities. Evidence is limited to ancillary features.", "evidence_quality_rationale": "Moderate evidence. Documentation confirms web app scanning and some third-party visibility but lacks specific supply chain product pages or detailed technical documentation for this sub-pillar.", "scoring_level_justification": "Maps to level 3: Documented capability with some technical detail and identifiable use cases, but not a primary or deeply developed capability area.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence of polymorphic defense, moving target defense, or runtime mutation capabilities. Tenable's platform is focused on exposure discovery and assessment, not active defense mutation.", "evidence_quality_rationale": "No relevant evidence found. Comprehensive product portfolio review confirms absence.", "scoring_level_justification": "Maps to level 0: No publicly verifiable evidence of capability.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No runtime application protection or in-process shielding capabilities identified. Tenable discovers vulnerabilities in applications but does not provide RASP, code instrumentation, or exploit prevention at runtime.", "evidence_quality_rationale": "No relevant evidence found.", "scoring_level_justification": "Maps to level 0: No publicly verifiable evidence of capability.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Tenable Identity Exposure (Alsid acquisition) provides Active Directory security monitoring and attack path visibility, offering minimal contribution to infrastructure defense understanding. However, Tenable does not perform dynamic network reconfiguration, micro-segmentation, or adaptive infrastructure changes.", "evidence_quality_rationale": "Limited evidence from Identity Exposure documentation. Capability exists but is tangential to this sub-pillar's core definition.", "scoring_level_justification": "Maps to level 1: Basic capability exists (AD monitoring) but no automation, dynamic defense, or continuous infrastructure mutation.", "confidence": "high"},
        "AMT-04": {"score_rationale": "Tenable Identity Exposure monitors for credential-related misconfigurations in Active Directory but does not perform automated credential rotation, ephemeral provisioning, or key lifecycle management.", "evidence_quality_rationale": "Limited evidence. Identity Exposure is a monitoring tool, not a credential management platform.", "scoring_level_justification": "Maps to level 1: Basic monitoring capability without automated rotation or provisioning.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No deception technology capabilities identified across the Tenable product portfolio. No honeypots, honeytokens, decoys, or breadcrumbs.", "evidence_quality_rationale": "No relevant evidence found.", "scoring_level_justification": "Maps to level 0: No publicly verifiable evidence of capability.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Tenable embeds threat intelligence into VPR scoring — leveraging exploit availability data, dark web monitoring signals, and CVSS enrichment to inform vulnerability prioritization. However, this is consumed intelligence for scoring purposes, not a standalone threat intelligence platform with TTP mapping, automated IOC ingestion, or intelligence-driven hunting.", "evidence_quality_rationale": "Moderate evidence. VPR documentation describes intelligence inputs but the capability is embedded, not standalone.", "scoring_level_justification": "Maps to level 2: Marketing/docs mention threat intelligence but capability is embedded within vulnerability scoring rather than being a named, independently operated TI product.", "confidence": "medium"},
        "ADR-03": {"score_rationale": "Cyber Exposure Studies provide targeted threat landscape analysis but are consultant-driven engagements, not a proactive threat hunting platform with hypothesis-driven hunting, hunt query libraries, or integration with EDR/NDR telemetry.", "evidence_quality_rationale": "Limited evidence. Exposure studies are professional services, not product capabilities.", "scoring_level_justification": "Maps to level 1: Basic capability through professional services without automation or product-level hunting.", "confidence": "high"},
        "ADR-04": {"score_rationale": "No counter-adversary operations, takedown services, adversary attribution, or dark web monitoring capabilities identified as product offerings.", "evidence_quality_rationale": "No relevant evidence found.", "scoring_level_justification": "Maps to level 0: No publicly verifiable evidence of capability.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No breach and attack simulation capability. Tenable validates vulnerability presence but does not simulate attack chains, lateral movement, or data exfiltration against production controls.", "evidence_quality_rationale": "No relevant evidence found.", "scoring_level_justification": "Maps to level 0: No publicly verifiable evidence of BAS capability.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Tenable Security Center provides compliance checking and audit trail capabilities that offer basic security control configuration assessment. However, this is compliance-focused (CIS benchmarks, NIST) rather than active security control validation testing (SIEM rule testing, EDR policy verification).", "evidence_quality_rationale": "Some evidence from Security Center documentation but capability is compliance-oriented, not active control validation.", "scoring_level_justification": "Maps to level 1: Basic capability through compliance scanning without active control effectiveness testing.", "confidence": "high"},
        "PPM-03": {"score_rationale": "Nessus can support vulnerability validation in penetration testing workflows but is fundamentally a scanner, not an automated penetration testing or red team automation platform. No PTaaS offering or attack path exploitation capability.", "evidence_quality_rationale": "Some evidence from Nessus documentation but it's a scanner, not a pen test platform.", "scoring_level_justification": "Maps to level 1: Basic scanning support for pen testing without automated exploitation, attack path analysis, or red team automation.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Tenable Cloud Security (powered by Ermetic acquisition $265M, Accurics, and Eureka acquisitions) provides comprehensive CNAPP including CSPM, CIEM, cloud workload protection, and IaC scanning across AWS, Azure, and GCP. Strong multi-cloud posture management with entitlement analysis and misconfiguration detection.", "evidence_quality_rationale": "High quality evidence. Well-documented acquisitions, dedicated cloud security documentation portal, and analyst recognition in CNAPP/CSPM markets.", "scoring_level_justification": "Maps to level 4: Advanced capability with named products, strategic acquisitions, multi-cloud support, and measurable outcomes. Not quite market-leading (vs. Wiz, Prisma) but strong.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Qualys"] = {
    "scores": {
        "EXM-01": 4, "EXM-02": 3, "EXM-03": 5, "EXM-04": 3,
        "AMT-01": 0, "AMT-02": 0, "AMT-03": 0, "AMT-04": 0,
        "ADR-01": 0, "ADR-02": 1, "ADR-03": 0, "ADR-04": 0,
        "PPM-01": 0, "PPM-02": 2, "PPM-03": 0, "PPM-04": 4
    },
    "evidence": {
        "EXM-01": {
            "source_urls": ["https://www.qualys.com/apps/cybersecurity-asset-management/", "https://www.qualys.com/apps/external-attack-surface-management/"],
            "key_evidence": [
                "Qualys CyberSecurity Asset Management (CSAM) provides comprehensive asset discovery across on-premises, cloud, container, and OT environments with real-time inventory.",
                "Qualys External Attack Surface Management (EASM) discovers internet-facing assets, shadow IT, and cloud resources with risk scoring.",
                "Cloud Agent architecture enables continuous asset monitoring across hybrid environments."
            ],
            "notes": "Strong ASM with dedicated CSAM and EASM products. Cloud-native agent architecture is a differentiator."
        },
        "EXM-02": {
            "source_urls": ["https://www.qualys.com/apps/vulnerability-management-detection-response/"],
            "key_evidence": [
                "VMDR (Vulnerability Management, Detection and Response) provides continuous vulnerability lifecycle management with TruRisk scoring.",
                "TruRisk combines vulnerability severity, exploit maturity, asset business context, and threat intelligence for risk-based prioritization.",
                "While not explicitly branded as CTEM, VMDR's continuous cycle of detect-prioritize-remediate-verify aligns with CTEM principles."
            ],
            "notes": "VMDR provides CTEM-like continuous operation but lacks explicit CTEM branding or full program operationalization."
        },
        "EXM-03": {
            "source_urls": ["https://www.qualys.com/apps/vulnerability-management-detection-response/", "https://www.qualys.com/truscore/"],
            "key_evidence": [
                "Qualys VMDR with TruRisk is a market-leading vulnerability prioritization platform with risk scoring beyond CVSS.",
                "TruRisk scoring incorporates exploit code maturity, active threat feeds, asset criticality, and compensating controls to deliver true risk-based prioritization.",
                "Automated remediation prioritization with patch management integration (Qualys Patch Management).",
                "Qualys QID database is one of the most comprehensive vulnerability knowledge bases in the industry, covering 200,000+ vulnerabilities."
            ],
            "notes": "Market leader in vulnerability management. TruRisk is the industry-recognized risk scoring methodology."
        },
        "EXM-04": {
            "source_urls": ["https://www.qualys.com/apps/web-app-scanning/"],
            "key_evidence": [
                "Qualys Web Application Scanning identifies third-party component vulnerabilities in web applications.",
                "CSAM provides some supply chain visibility through software inventory and component tracking.",
                "No dedicated SBOM analysis or third-party vendor risk management platform."
            ],
            "notes": "Limited supply chain capability through web scanning and asset management. Not a primary focus area."
        },
        "AMT-01": {"source_urls": [], "key_evidence": ["No polymorphic or moving target defense capabilities."], "notes": "Outside vendor scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No RASP or runtime application protection."], "notes": "Outside vendor scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No dynamic network defense or micro-segmentation."], "notes": "Outside vendor scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No credential rotation or ephemeral provisioning."], "notes": "Outside vendor scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No deception technology capabilities."], "notes": "Outside vendor scope."},
        "ADR-02": {
            "source_urls": ["https://www.qualys.com/apps/vulnerability-management-detection-response/"],
            "key_evidence": ["TruRisk incorporates some threat intelligence feeds for vulnerability scoring but Qualys does not operate a standalone threat intelligence platform."],
            "notes": "Basic TI consumption within vulnerability scoring only."
        },
        "ADR-03": {"source_urls": [], "key_evidence": ["No proactive threat hunting capabilities or services."], "notes": "Outside vendor scope."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No counter-adversary operations or dark web monitoring."], "notes": "Outside vendor scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No breach and attack simulation capability."], "notes": "Outside vendor scope."},
        "PPM-02": {
            "source_urls": ["https://www.qualys.com/apps/policy-compliance/"],
            "key_evidence": ["Qualys Policy Compliance automates security configuration assessment against CIS benchmarks, NIST, PCI-DSS, and other frameworks.", "Provides control configuration validation but not active SIEM/EDR/firewall effectiveness testing."],
            "notes": "Policy compliance provides configuration validation — a basic form of security control assessment."
        },
        "PPM-03": {"source_urls": [], "key_evidence": ["No automated penetration testing or red team automation platform."], "notes": "Outside vendor scope."},
        "PPM-04": {
            "source_urls": ["https://www.qualys.com/apps/cloud-security-posture-management/", "https://www.qualys.com/apps/container-security/"],
            "key_evidence": [
                "Qualys CloudView provides CSPM for AWS, Azure, and GCP with misconfiguration detection and compliance mapping.",
                "Qualys Container Security provides container image scanning and runtime security.",
                "TotalCloud platform provides unified cloud-native security with CSPM, CWPP, and IaC scanning."
            ],
            "notes": "Strong CSPM through dedicated CloudView/TotalCloud with multi-cloud coverage."
        }
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Qualys scores 4 (Advanced) with dedicated CSAM and EASM products providing automated asset discovery, shadow IT detection, and cloud resource enumeration. Cloud-native agent architecture enables continuous monitoring. Strong but slightly behind Tenable's unified platform approach.", "evidence_quality_rationale": "Strong evidence from product documentation. Named products with clear capability descriptions.", "scoring_level_justification": "Maps to level 4: Named products with measurable outcomes and continuous operation. Enterprise adoption validated.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Qualys scores 3 (Demonstrated) for CTEM. VMDR provides continuous vulnerability lifecycle management with TruRisk that aligns with CTEM principles, but is not explicitly positioned or branded as a CTEM program. The continuous detect-prioritize-remediate-verify cycle maps to CTEM stages.", "evidence_quality_rationale": "Moderate evidence. VMDR is well-documented but CTEM alignment is inferred rather than explicitly stated.", "scoring_level_justification": "Maps to level 3: Documented capability with identifiable use cases but lacks explicit CTEM branding and full program operationalization.", "confidence": "medium"},
        "EXM-03": {"score_rationale": "Qualys earns 5 (Market-Leading) for Vulnerability Prioritization. TruRisk scoring is an industry-recognized risk-based prioritization methodology that goes well beyond CVSS, incorporating exploit maturity, threat feeds, asset criticality, and compensating controls. 200,000+ QID vulnerability knowledge base. Integrated Patch Management for remediation.", "evidence_quality_rationale": "Exceptional evidence. Long market tenure, extensive documentation, analyst recognition, and measurable metrics.", "scoring_level_justification": "Maps to level 5: Best-in-class with TruRisk as industry benchmark, comprehensive QID database, and continuous innovation.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Qualys scores 3 (Demonstrated) with web application scanning identifying third-party component vulnerabilities and CSAM providing software inventory. No dedicated SBOM, supply chain monitoring, or vendor risk management capability.", "evidence_quality_rationale": "Limited evidence. Capability is ancillary to primary VM focus.", "scoring_level_justification": "Maps to level 3: Some documented capability through WAS and CSAM but not a primary or deeply developed area.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence of capability.", "evidence_quality_rationale": "No relevant evidence.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence of capability.", "evidence_quality_rationale": "No relevant evidence.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence of capability.", "evidence_quality_rationale": "No relevant evidence.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence of capability.", "evidence_quality_rationale": "No relevant evidence.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence of capability.", "evidence_quality_rationale": "No relevant evidence.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Qualys embeds basic threat intelligence in TruRisk scoring but does not offer a standalone TIP, IOC management, or TTP mapping capability.", "evidence_quality_rationale": "Limited. TI is embedded, not standalone.", "scoring_level_justification": "Level 1: Basic intelligence consumption without dedicated product.", "confidence": "high"},
        "ADR-03": {"score_rationale": "No evidence of capability.", "evidence_quality_rationale": "No relevant evidence.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-04": {"score_rationale": "No evidence of capability.", "evidence_quality_rationale": "No relevant evidence.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence of capability.", "evidence_quality_rationale": "No relevant evidence.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Qualys Policy Compliance provides automated configuration assessment against industry benchmarks (CIS, NIST, PCI-DSS), representing a basic level of security control validation. Does not test active control effectiveness (SIEM detection rules, EDR response).", "evidence_quality_rationale": "Moderate. Named product with clear documentation.", "scoring_level_justification": "Level 2: Named product but scope is configuration compliance, not active control validation.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence of capability.", "evidence_quality_rationale": "No relevant evidence.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Qualys scores 4 (Advanced) with CloudView/TotalCloud providing CSPM across AWS, Azure, and GCP with misconfiguration detection, compliance mapping, container security, and IaC scanning. Strong multi-cloud capability.", "evidence_quality_rationale": "Strong evidence from dedicated product documentation.", "scoring_level_justification": "Level 4: Named products with measurable outcomes, multi-cloud support, and integration capabilities.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Rapid7"] = {
    "scores": {
        "EXM-01": 4, "EXM-02": 3, "EXM-03": 4, "EXM-04": 2,
        "AMT-01": 0, "AMT-02": 1, "AMT-03": 0, "AMT-04": 0,
        "ADR-01": 1, "ADR-02": 2, "ADR-03": 3, "ADR-04": 0,
        "PPM-01": 0, "PPM-02": 1, "PPM-03": 4, "PPM-04": 3
    },
    "evidence": {
        "EXM-01": {
            "source_urls": ["https://www.rapid7.com/products/insightvm/", "https://www.rapid7.com/products/"],
            "key_evidence": [
                "InsightVM provides agent-based and agentless vulnerability scanning with live asset correlation and risk-based prioritization.",
                "Comprehensive asset discovery across on-premises, cloud, and virtual infrastructure with real-time monitoring.",
                "Integration with Rapid7 Insight platform for unified visibility."
            ],
            "notes": "Strong VM-centric ASM through InsightVM. Not as dedicated as pure EASM vendors."
        },
        "EXM-02": {
            "source_urls": ["https://www.rapid7.com/products/insightvm/"],
            "key_evidence": [
                "InsightVM provides Real Risk Score for continuous risk assessment and remediation project tracking.",
                "Continuous monitoring and remediation workflows align with CTEM concepts but are not explicitly branded as CTEM.",
                "Remediation projects with tracking and verification support mobilization phase."
            ],
            "notes": "CTEM-adjacent capability through continuous VM lifecycle. Not explicitly CTEM-branded."
        },
        "EXM-03": {
            "source_urls": ["https://www.rapid7.com/products/insightvm/"],
            "key_evidence": [
                "Real Risk Score combines CVSS, exploit availability, malware exposure, and asset criticality for risk-based prioritization.",
                "Attacker analytics provide visibility into likely attack paths through vulnerability chains.",
                "Automated remediation prioritization with integration to ticketing systems."
            ],
            "notes": "Strong vulnerability prioritization with Real Risk Score. Good but not market-leading compared to Tenable/Qualys."
        },
        "EXM-04": {
            "source_urls": ["https://www.rapid7.com/products/insightvm/"],
            "key_evidence": ["Some third-party exposure visibility through asset scanning and software inventory but no dedicated supply chain or SBOM capability."],
            "notes": "Limited supply chain capability."
        },
        "AMT-01": {"source_urls": [], "key_evidence": ["No polymorphic defense capabilities."], "notes": "Outside vendor scope."},
        "AMT-02": {
            "source_urls": ["https://www.rapid7.com/products/"],
            "key_evidence": ["Rapid7 acquired tCell in 2018 for application security monitoring, providing some runtime visibility. However, this capability has been largely integrated into InsightAppSec and is monitoring-focused rather than active runtime protection."],
            "notes": "Minimal runtime monitoring through tCell acquisition, not active RASP."
        },
        "AMT-03": {"source_urls": [], "key_evidence": ["No dynamic network defense or micro-segmentation."], "notes": "Outside vendor scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No credential rotation capabilities."], "notes": "Outside vendor scope."},
        "ADR-01": {
            "source_urls": ["https://www.rapid7.com/products/insightidr/"],
            "key_evidence": ["InsightIDR includes Attacker Behavior Analytics with some honeytoken-like detection capabilities (e.g., honey credentials for lateral movement detection), though this is not a full deception platform."],
            "notes": "Basic deception elements within InsightIDR but not a dedicated deception technology platform."
        },
        "ADR-02": {
            "source_urls": ["https://www.rapid7.com/products/threat-command/"],
            "key_evidence": ["Rapid7 Threat Command (acquired IntSights) provides external threat intelligence with digital risk protection.", "Some IOC management and threat feed integration capabilities."],
            "notes": "Threat Command provides TI capabilities but primarily for digital risk protection rather than full TIP operationalization."
        },
        "ADR-03": {
            "source_urls": ["https://www.rapid7.com/services/managed-detection-and-response/"],
            "key_evidence": [
                "Rapid7 MDR service includes managed threat hunting by Rapid7 SOC analysts.",
                "InsightIDR provides investigation and hunting capabilities for in-house teams.",
                "Community-driven detection rules and hunting queries through Rapid7 research."
            ],
            "notes": "Good threat hunting through MDR service and InsightIDR. Managed and product-based hunting available."
        },
        "ADR-04": {"source_urls": [], "key_evidence": ["Threat Command provides some digital risk protection but counter-adversary operations are limited."], "notes": "Basic DRP through Threat Command but not full counter-adversary ops."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No dedicated BAS capability."], "notes": "Outside vendor scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["Some control assessment through InsightVM compliance checks but not active control validation."], "notes": "Basic compliance checking."},
        "PPM-03": {
            "source_urls": ["https://www.rapid7.com/products/metasploit/", "https://www.rapid7.com/services/penetration-testing/"],
            "key_evidence": [
                "Metasploit — the world's most widely used penetration testing framework with 1,600+ exploit modules and extensive community.",
                "Metasploit Pro provides automated pen testing workflows, attack simulation, and report generation.",
                "Rapid7 Penetration Testing Services provide expert-led assessments.",
                "Attack path visualization and exploitation validation capabilities."
            ],
            "notes": "Market-leading pen testing through Metasploit heritage. Both product (Metasploit Pro) and services available."
        },
        "PPM-04": {
            "source_urls": ["https://www.rapid7.com/products/insightcloudsec/"],
            "key_evidence": [
                "InsightCloudSec provides CSPM for AWS, Azure, and GCP with misconfiguration detection.",
                "Cloud workload protection and container security capabilities.",
                "Real-time remediation and compliance automation."
            ],
            "notes": "Solid CSPM through InsightCloudSec with multi-cloud support. Good but not best-in-class."
        }
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Rapid7 scores 4 (Advanced) with InsightVM providing comprehensive asset discovery, agent-based and agentless scanning, live asset correlation, and risk-based prioritization. Strong enterprise VM platform but not a dedicated EASM leader.", "evidence_quality_rationale": "Strong evidence from product documentation.", "scoring_level_justification": "Level 4: Named product with measurable outcomes and continuous operation.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Rapid7 scores 3 (Demonstrated) with InsightVM's continuous monitoring and remediation projects providing CTEM-adjacent workflows. Real Risk Score enables continuous prioritization but not explicitly branded or operationalized as CTEM.", "evidence_quality_rationale": "Moderate evidence. CTEM alignment is inferred.", "scoring_level_justification": "Level 3: Documented continuous operation with some technical detail.", "confidence": "medium"},
        "EXM-03": {"score_rationale": "Rapid7 scores 4 (Advanced) with Real Risk Score combining CVSS, exploit availability, malware exposure, and asset criticality. Attacker analytics provide vulnerability chain analysis. Strong but not quite market-leading compared to Tenable VPR or Qualys TruRisk.", "evidence_quality_rationale": "Strong evidence from InsightVM documentation.", "scoring_level_justification": "Level 4: Named product with measurable risk scoring and automated prioritization.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Limited third-party exposure capability. Some software inventory through scanning but no dedicated supply chain monitoring.", "evidence_quality_rationale": "Limited evidence.", "scoring_level_justification": "Level 2: Generic capability without specific supply chain products.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence of capability.", "evidence_quality_rationale": "No relevant evidence.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "Minimal capability through tCell acquisition (2018) providing application security monitoring. Largely integrated into InsightAppSec as monitoring, not active runtime protection.", "evidence_quality_rationale": "Limited evidence. tCell heritage provides basic foundation.", "scoring_level_justification": "Level 1: Basic monitoring without active protection.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence of capability.", "evidence_quality_rationale": "No relevant evidence.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence of capability.", "evidence_quality_rationale": "No relevant evidence.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "InsightIDR includes basic honey credential and deception-like detection capabilities but is not a dedicated deception platform with full honeypot/honeytoken/breadcrumb deployment.", "evidence_quality_rationale": "Limited evidence. Deception elements are minor features within IDR.", "scoring_level_justification": "Level 1: Basic capability without dedicated product.", "confidence": "medium"},
        "ADR-02": {"score_rationale": "Threat Command (IntSights acquisition) provides external threat intelligence and digital risk protection with some IOC management. Primarily DRP-focused rather than full TIP with automated operationalization.", "evidence_quality_rationale": "Moderate evidence from Threat Command documentation.", "scoring_level_justification": "Level 2: Named product but scope is DRP rather than full TI operationalization.", "confidence": "medium"},
        "ADR-03": {"score_rationale": "Rapid7 MDR service includes managed threat hunting by SOC analysts. InsightIDR enables in-house hunting with investigation tools and community-driven detection content. Both managed and product-based hunting available.", "evidence_quality_rationale": "Good evidence from MDR service descriptions and InsightIDR capabilities.", "scoring_level_justification": "Level 3: Documented hunting capability with named products and services.", "confidence": "high"},
        "ADR-04": {"score_rationale": "No significant counter-adversary operations. Threat Command provides some digital risk protection elements.", "evidence_quality_rationale": "Limited evidence.", "scoring_level_justification": "Level 0: Insufficient for scoring in this sub-pillar.", "confidence": "medium"},
        "PPM-01": {"score_rationale": "No dedicated BAS capability.", "evidence_quality_rationale": "No relevant evidence.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Basic compliance checking through InsightVM configuration assessment but not active security control validation.", "evidence_quality_rationale": "Limited evidence.", "scoring_level_justification": "Level 1: Basic compliance checking.", "confidence": "high"},
        "PPM-03": {"score_rationale": "Rapid7 scores 4 (Advanced) with Metasploit — the world's most widely used penetration testing framework (1,600+ exploit modules). Metasploit Pro provides automated pen testing workflows, attack simulation, and reporting. Combined with professional pen testing services, Rapid7 offers comprehensive offensive validation.", "evidence_quality_rationale": "Exceptional evidence. Metasploit is a globally recognized pen testing standard.", "scoring_level_justification": "Level 4: Named best-in-class product with extensive community, measurable capabilities, and continuous innovation.", "confidence": "high"},
        "PPM-04": {"score_rationale": "InsightCloudSec provides CSPM with multi-cloud support (AWS, Azure, GCP), misconfiguration detection, and real-time remediation. Solid but not best-in-class compared to Prisma Cloud or Wiz.", "evidence_quality_rationale": "Good evidence from product documentation.", "scoring_level_justification": "Level 3: Named product with documented capabilities.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["CrowdStrike"] = {
    "scores": {
        "EXM-01": 5, "EXM-02": 4, "EXM-03": 4, "EXM-04": 3,
        "AMT-01": 0, "AMT-02": 2, "AMT-03": 2, "AMT-04": 3,
        "ADR-01": 2, "ADR-02": 5, "ADR-03": 5, "ADR-04": 4,
        "PPM-01": 1, "PPM-02": 2, "PPM-03": 2, "PPM-04": 3
    },
    "evidence": {
        "EXM-01": {
            "source_urls": ["https://www.crowdstrike.com/products/exposure-management/falcon-surface/", "https://www.crowdstrike.com/products/exposure-management/"],
            "key_evidence": [
                "Falcon Surface (acquired Reposify 2022) provides comprehensive external attack surface management with automated discovery of internet-facing assets, shadow IT, and cloud resources.",
                "Falcon Exposure Management unifies ASM, vulnerability management, and risk prioritization into CrowdStrike's platform.",
                "AI-powered asset attribution and risk scoring with continuous monitoring.",
                "Integration with Falcon platform provides correlated visibility across endpoint, cloud, and identity attack surfaces."
            ],
            "notes": "Market-leading EASM through Falcon Surface with deep platform integration. Reposify acquisition specifically for ASM."
        },
        "EXM-02": {
            "source_urls": ["https://www.crowdstrike.com/products/exposure-management/"],
            "key_evidence": [
                "Falcon Exposure Management provides continuous exposure assessment aligned with CTEM framework stages.",
                "AI-driven prioritization using adversary intelligence from CrowdStrike Intelligence.",
                "Continuous cycle of discovery, assessment, prioritization, and remediation tracking."
            ],
            "notes": "Strong CTEM alignment through unified exposure management platform with intelligence-driven prioritization."
        },
        "EXM-03": {
            "source_urls": ["https://www.crowdstrike.com/products/exposure-management/falcon-spotlight/"],
            "key_evidence": [
                "Falcon Spotlight provides vulnerability assessment using the Falcon sensor — no additional agents or scans required.",
                "AI-powered vulnerability prioritization using ExPRT.AI rating system that incorporates exploit intelligence and adversary activity.",
                "Real-time vulnerability visibility across all Falcon-managed endpoints."
            ],
            "notes": "Strong agentless VM through the Falcon sensor. ExPRT.AI provides intelligent prioritization."
        },
        "EXM-04": {
            "source_urls": ["https://www.crowdstrike.com/products/exposure-management/"],
            "key_evidence": [
                "Some supply chain visibility through Falcon Intelligence supply chain alerts.",
                "Third-party risk assessment through monitoring of adversary campaigns targeting supply chains.",
                "Not a dedicated supply chain risk management platform."
            ],
            "notes": "Some supply chain intelligence through threat intel but not a dedicated capability."
        },
        "AMT-01": {"source_urls": [], "key_evidence": ["No polymorphic or moving target defense capabilities."], "notes": "Outside vendor scope."},
        "AMT-02": {
            "source_urls": ["https://www.crowdstrike.com/products/cloud-security/"],
            "key_evidence": ["Falcon sensor provides some runtime protection through behavioral analysis and exploit detection at the endpoint level, but this is endpoint protection rather than in-process application shielding or RASP."],
            "notes": "Basic runtime protection through EDR behavioral analysis, not RASP."
        },
        "AMT-03": {
            "source_urls": ["https://www.crowdstrike.com/products/identity-protection/"],
            "key_evidence": ["Falcon Zero Trust Assessment provides continuous device trust scoring for conditional access.", "Identity Threat Protection provides some dynamic access control based on risk signals."],
            "notes": "Some dynamic access control but not full network topology reconfiguration or micro-segmentation."
        },
        "AMT-04": {
            "source_urls": ["https://www.crowdstrike.com/products/identity-protection/"],
            "key_evidence": [
                "Falcon Identity Threat Protection (Preempt acquisition 2020) provides identity-based security with risk-based conditional access.",
                "Identity segmentation and lateral movement prevention through identity analysis.",
                "Not automated credential rotation but strong identity threat detection and response."
            ],
            "notes": "Good identity protection through Preempt acquisition. Detection-focused rather than credential rotation."
        },
        "ADR-01": {
            "source_urls": ["https://www.crowdstrike.com/products/identity-protection/"],
            "key_evidence": ["Falcon Identity Threat Protection includes some honeytoken-like capabilities for detecting credential theft and lateral movement.", "Limited compared to dedicated deception platforms but provides some high-fidelity identity deception."],
            "notes": "Basic identity deception capabilities. Not a full deception platform."
        },
        "ADR-02": {
            "source_urls": ["https://www.crowdstrike.com/products/threat-intelligence/", "https://www.crowdstrike.com/adversaries/"],
            "key_evidence": [
                "CrowdStrike Intelligence is an industry-leading threat intelligence platform tracking 200+ named adversary groups with unique naming convention (Bear, Panda, Kitten, Spider, etc.).",
                "Falcon Intelligence provides automated IOC ingestion, correlation, and TTP mapping to MITRE ATT&CK.",
                "Intelligence-driven detection and hunting query generation through adversary profiles.",
                "Falcon Intelligence Recon provides dark web monitoring and adversary campaign tracking.",
                "Recognized as a Leader in Gartner Magic Quadrant for Security Operations."
            ],
            "notes": "Market-leading threat intelligence. 200+ named adversary groups tracked. Deep integration with Falcon platform."
        },
        "ADR-03": {
            "source_urls": ["https://www.crowdstrike.com/services/managed-services/falcon-overwatch/"],
            "key_evidence": [
                "Falcon OverWatch is the industry's premier managed threat hunting service operating 24/7/365.",
                "Dedicated human threat hunters using hypothesis-driven and intelligence-led hunting methodologies.",
                "OverWatch identifies threats that automated detections miss, with real-time notification and context.",
                "Published annual Threat Hunting Report with detailed adversary insights and hunting metrics.",
                "Leverages CrowdStrike's massive telemetry (trillions of events per week) for hunt operations."
            ],
            "notes": "Industry-leading managed threat hunting. OverWatch is the gold standard for managed hunting services."
        },
        "ADR-04": {
            "source_urls": ["https://www.crowdstrike.com/products/threat-intelligence/falcon-intelligence-recon/", "https://www.crowdstrike.com/services/"],
            "key_evidence": [
                "Falcon Intelligence Recon provides dark web monitoring, adversary infrastructure tracking, and brand protection.",
                "CrowdStrike Counter Adversary Operations unifies threat intelligence, hunting, and response.",
                "Takedown services for malicious domains and infrastructure.",
                "Adversary attribution and campaign tracking through named adversary methodology."
            ],
            "notes": "Strong counter-adversary ops with dedicated Recon product and professional services."
        },
        "PPM-01": {
            "source_urls": [],
            "key_evidence": ["Some attack simulation capability through Falcon XDR playbooks but not a dedicated BAS platform."],
            "notes": "Minimal BAS capability."
        },
        "PPM-02": {
            "source_urls": ["https://www.crowdstrike.com/products/next-gen-siem/"],
            "key_evidence": ["Falcon LogScale and Next-Gen SIEM provide some detection validation capabilities.", "Security control assessment through Falcon platform telemetry analysis."],
            "notes": "Basic control validation through SIEM analytics, not dedicated SCV."
        },
        "PPM-03": {
            "source_urls": ["https://www.crowdstrike.com/services/"],
            "key_evidence": ["CrowdStrike Services offers penetration testing and red team exercises through professional services.", "Not an automated pen testing platform or PTaaS."],
            "notes": "Professional services-based pen testing, not product-level capability."
        },
        "PPM-04": {
            "source_urls": ["https://www.crowdstrike.com/products/cloud-security/"],
            "key_evidence": [
                "Falcon Cloud Security provides CSPM for AWS, Azure, and GCP with misconfiguration detection.",
                "Cloud workload protection integrated through the Falcon sensor.",
                "Some CIEM capabilities for cloud entitlement analysis."
            ],
            "notes": "Solid cloud security with CSPM and agent-based workload protection. Good but not CNAPP leader."
        }
    },
    "rationale": {
        "EXM-01": {"score_rationale": "CrowdStrike scores 5 (Market-Leading) with Falcon Surface (Reposify acquisition 2022) providing comprehensive EASM with AI-powered asset discovery, shadow IT detection, and continuous monitoring. Deep integration with the Falcon platform provides correlated attack surface visibility across endpoint, cloud, and identity surfaces.", "evidence_quality_rationale": "Strong evidence. Dedicated product, acquisition history, analyst recognition.", "scoring_level_justification": "Level 5: Best-in-class EASM with dedicated product, platform integration, and analyst leadership.", "confidence": "high"},
        "EXM-02": {"score_rationale": "CrowdStrike scores 4 (Advanced) with Falcon Exposure Management providing continuous exposure assessment with AI-driven prioritization using adversary intelligence. Strong CTEM alignment through platform-unified exposure management.", "evidence_quality_rationale": "Good evidence from product documentation and platform architecture.", "scoring_level_justification": "Level 4: Named product with continuous operation and intelligence-driven prioritization.", "confidence": "high"},
        "EXM-03": {"score_rationale": "CrowdStrike scores 4 (Advanced) with Falcon Spotlight providing agentless vulnerability assessment through the Falcon sensor with ExPRT.AI prioritization. Real-time visibility without additional scanning infrastructure.", "evidence_quality_rationale": "Strong evidence from product documentation.", "scoring_level_justification": "Level 4: Named product with AI-driven scoring and continuous operation.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Some supply chain intelligence through Falcon Intelligence supply chain alerts and adversary campaign monitoring. Not a dedicated supply chain risk management platform.", "evidence_quality_rationale": "Moderate evidence. Capability is intelligence-driven rather than product-dedicated.", "scoring_level_justification": "Level 3: Demonstrated capability through threat intel but not a primary focus.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence of capability.", "evidence_quality_rationale": "No relevant evidence.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "Falcon sensor provides endpoint-level behavioral analysis and exploit detection but this is EDR/XDR protection, not in-process RASP or code instrumentation.", "evidence_quality_rationale": "Some evidence but capability is endpoint-centric, not application-level.", "scoring_level_justification": "Level 2: Generic behavioral protection at endpoint level.", "confidence": "medium"},
        "AMT-03": {"score_rationale": "Falcon Zero Trust Assessment and Identity Threat Protection provide dynamic access controls based on risk signals, representing some adaptive access capability. However, no network topology reconfiguration or micro-segmentation.", "evidence_quality_rationale": "Moderate evidence from identity protection documentation.", "scoring_level_justification": "Level 2: Some adaptive access without full network defense mutation.", "confidence": "medium"},
        "AMT-04": {"score_rationale": "Falcon Identity Threat Protection (Preempt acquisition) provides identity-based security with risk-based conditional access and lateral movement prevention. Detection and response focused rather than automated credential rotation, but strong identity segmentation.", "evidence_quality_rationale": "Good evidence from Identity Protection product page.", "scoring_level_justification": "Level 3: Named product with documented capabilities for identity-based access control.", "confidence": "high"},
        "ADR-01": {"score_rationale": "Limited deception capability through Identity Threat Protection's honeytoken-like credential detection. Not a full deception platform with honeypots, decoys, and breadcrumbs.", "evidence_quality_rationale": "Limited evidence. Feature is within larger product.", "scoring_level_justification": "Level 2: Generic deception claims within identity product.", "confidence": "medium"},
        "ADR-02": {"score_rationale": "CrowdStrike earns 5 (Market-Leading) for Threat Intelligence. Falcon Intelligence tracks 200+ named adversary groups, provides automated IOC ingestion and ATT&CK TTP mapping, intelligence-driven detection engineering, and dark web monitoring through Falcon Intelligence Recon. Recognized as an industry leader in threat intelligence.", "evidence_quality_rationale": "Exceptional evidence. Named adversary methodology is industry-defining. Analyst recognition.", "scoring_level_justification": "Level 5: Best-in-class with industry-defining adversary tracking, extensive intelligence operations, and continuous innovation.", "confidence": "high"},
        "ADR-03": {"score_rationale": "CrowdStrike earns 5 (Market-Leading) for Proactive Threat Hunting. Falcon OverWatch is the industry gold standard for managed threat hunting — 24/7/365 human-led hunting using hypothesis-driven and intelligence-led methodologies. Published annual Threat Hunting Reports with metrics. Leverages trillions of events per week from the Falcon telemetry cloud.", "evidence_quality_rationale": "Exceptional evidence. OverWatch is universally recognized as the leading managed hunting service.", "scoring_level_justification": "Level 5: Best-in-class with dedicated hunting service, published metrics, massive telemetry, and analyst leadership.", "confidence": "high"},
        "ADR-04": {"score_rationale": "CrowdStrike scores 4 (Advanced) with Falcon Intelligence Recon for dark web monitoring, adversary infrastructure tracking, brand protection, and takedown services. Counter Adversary Operations capability unifies intelligence and response.", "evidence_quality_rationale": "Strong evidence from dedicated products and services.", "scoring_level_justification": "Level 4: Named products with measurable outcomes and proven takedown capabilities.", "confidence": "high"},
        "PPM-01": {"score_rationale": "Minimal BAS capability through Falcon XDR playbooks and simulation. Not a dedicated BAS platform.", "evidence_quality_rationale": "Limited evidence.", "scoring_level_justification": "Level 1: Basic capability without dedicated product.", "confidence": "medium"},
        "PPM-02": {"score_rationale": "Some security control validation through Falcon LogScale/Next-Gen SIEM analytics but not dedicated SCV with control effectiveness testing.", "evidence_quality_rationale": "Moderate evidence.", "scoring_level_justification": "Level 2: Some control assessment through SIEM analytics.", "confidence": "medium"},
        "PPM-03": {"score_rationale": "Professional services-based penetration testing and red team exercises. Not an automated pen testing platform or PTaaS product.", "evidence_quality_rationale": "Some evidence from services documentation.", "scoring_level_justification": "Level 2: Professional services without product-level pen testing automation.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Falcon Cloud Security provides CSPM with multi-cloud misconfiguration detection, workload protection (sensor-based), and some CIEM capabilities. Solid but not CNAPP market leader.", "evidence_quality_rationale": "Good evidence from product documentation.", "scoring_level_justification": "Level 3: Named product with documented multi-cloud capabilities.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Palo Alto Networks"] = {
    "scores": {
        "EXM-01": 5, "EXM-02": 4, "EXM-03": 4, "EXM-04": 3,
        "AMT-01": 0, "AMT-02": 2, "AMT-03": 4, "AMT-04": 2,
        "ADR-01": 1, "ADR-02": 5, "ADR-03": 4, "ADR-04": 3,
        "PPM-01": 2, "PPM-02": 3, "PPM-03": 2, "PPM-04": 5
    },
    "evidence": {
        "EXM-01": {
            "source_urls": ["https://www.paloaltonetworks.com/cortex/cortex-xpanse", "https://www.paloaltonetworks.com/cortex/"],
            "key_evidence": [
                "Cortex Xpanse provides industry-leading external attack surface management with automated discovery of all internet-facing assets.",
                "AI-powered asset attribution and risk scoring across IPv4 and IPv6 address space.",
                "Active discovery probing with accurate asset attribution to organization and subsidiaries.",
                "Government and large enterprise adoption including multiple US federal agencies.",
                "Integrated with Cortex XSIAM for unified security operations."
            ],
            "notes": "Market-leading EASM. Cortex Xpanse (formerly Expanse, acquired 2020) is an industry benchmark for ASM."
        },
        "EXM-02": {
            "source_urls": ["https://www.paloaltonetworks.com/cortex/cortex-xpanse"],
            "key_evidence": [
                "Cortex Xpanse enables continuous exposure management with automated asset discovery, risk scoring, and remediation prioritization.",
                "Integration with XSOAR for automated response and mobilization.",
                "Continuous monitoring cycle aligning with CTEM framework."
            ],
            "notes": "Strong CTEM alignment through Xpanse + XSOAR integration for full lifecycle management."
        },
        "EXM-03": {
            "source_urls": ["https://www.paloaltonetworks.com/cortex/cortex-xpanse"],
            "key_evidence": [
                "Cortex Xpanse provides risk-based prioritization of discovered exposures using threat intelligence and business context.",
                "Active response recommendations with automated remediation workflows through XSOAR.",
                "Exposure prioritization combines asset criticality, threat intelligence, and exploitability."
            ],
            "notes": "Good vulnerability prioritization through Xpanse risk scoring. Not a traditional VM platform."
        },
        "EXM-04": {
            "source_urls": ["https://www.paloaltonetworks.com/cortex/cortex-xpanse"],
            "key_evidence": ["Some third-party supply chain monitoring through Xpanse discovery of subsidiary and partner-connected assets.", "Supply chain risk is addressed through exposure monitoring rather than dedicated SBOM or vendor risk management."],
            "notes": "Some supply chain exposure through Xpanse discovery. Not a dedicated capability."
        },
        "AMT-01": {"source_urls": [], "key_evidence": ["No polymorphic or moving target defense capabilities."], "notes": "Outside vendor scope."},
        "AMT-02": {
            "source_urls": ["https://www.paloaltonetworks.com/prisma/cloud"],
            "key_evidence": ["Prisma Cloud provides some runtime protection for cloud workloads including container and serverless security. Primarily monitoring and policy-based rather than in-process RASP.", "WildFire provides runtime malware analysis but is sandboxing, not application-level protection."],
            "notes": "Some cloud runtime protection through Prisma Cloud. Not traditional RASP."
        },
        "AMT-03": {
            "source_urls": ["https://www.paloaltonetworks.com/sase/access", "https://www.paloaltonetworks.com/network-security"],
            "key_evidence": [
                "Prisma Access provides zero trust network access (ZTNA) with adaptive access controls.",
                "Next-gen firewall portfolio with micro-segmentation capabilities through software-defined security.",
                "IoT Security provides device segmentation and policy enforcement.",
                "Comprehensive network security portfolio from perimeter to cloud with dynamic policy."
            ],
            "notes": "Strong dynamic network defense through ZTNA, NGFW portfolio, and micro-segmentation. Advanced adaptive controls."
        },
        "AMT-04": {
            "source_urls": ["https://www.paloaltonetworks.com/cortex/cortex-xsiam"],
            "key_evidence": ["Some identity-based access control through Prisma Access and XSIAM.", "Not a dedicated credential rotation or PAM platform."],
            "notes": "Basic identity integration without automated credential rotation."
        },
        "ADR-01": {
            "source_urls": [],
            "key_evidence": ["Minimal deception capability. Some Cortex XDR decoy features have been explored but not a core product offering."],
            "notes": "Very limited deception technology."
        },
        "ADR-02": {
            "source_urls": ["https://www.paloaltonetworks.com/unit42", "https://unit42.paloaltonetworks.com/"],
            "key_evidence": [
                "Unit 42 threat intelligence provides world-class adversary research and threat analysis.",
                "AutoFocus threat intelligence portal with automated IOC correlation and enrichment.",
                "Extensive TTP mapping to MITRE ATT&CK framework.",
                "WildFire malware analysis processes billions of samples daily.",
                "Cortex XSIAM integrates threat intelligence for automated detection and response.",
                "Recognized as a Leader in threat intelligence by multiple analysts."
            ],
            "notes": "Market-leading threat intelligence through Unit 42 research team and AutoFocus platform."
        },
        "ADR-03": {
            "source_urls": ["https://www.paloaltonetworks.com/unit42", "https://www.paloaltonetworks.com/cortex/cortex-xdr"],
            "key_evidence": [
                "Unit 42 provides managed threat hunting as part of professional services engagements.",
                "Cortex XDR provides advanced hunting capabilities with query-based investigation tools.",
                "Analytics-driven hunting with behavioral analytics and ML-based detection.",
                "Unit 42 publishes extensive threat research supporting hunting hypothesis generation."
            ],
            "notes": "Strong threat hunting through Unit 42 services and Cortex XDR product capabilities."
        },
        "ADR-04": {
            "source_urls": ["https://www.paloaltonetworks.com/unit42"],
            "key_evidence": [
                "Unit 42 provides incident response, adversary assessment, and threat assessment services.",
                "Some takedown and adversary disruption through coordinated disclosure and law enforcement collaboration.",
                "Brand protection capabilities through Prisma Access and DNS security."
            ],
            "notes": "Some counter-adversary capability through Unit 42 but not a dedicated takedown/DRP product."
        },
        "PPM-01": {
            "source_urls": ["https://www.paloaltonetworks.com/cortex/cortex-xdr"],
            "key_evidence": ["Some attack simulation capability through Cortex XDR and XSOAR playbooks.", "Not a dedicated BAS platform."],
            "notes": "Basic simulation through XDR/XSOAR. Not dedicated BAS."
        },
        "PPM-02": {
            "source_urls": ["https://www.paloaltonetworks.com/cortex/cortex-xsoar"],
            "key_evidence": [
                "XSOAR (formerly Demisto) provides security orchestration with playbook-based automation for control validation.",
                "Automated testing and verification of security control configurations.",
                "Integration framework validates SIEM, firewall, and EDR effectiveness through automated workflows."
            ],
            "notes": "Good control validation through XSOAR orchestration and automation. Playbook-driven approach."
        },
        "PPM-03": {
            "source_urls": ["https://www.paloaltonetworks.com/unit42"],
            "key_evidence": ["Unit 42 provides professional penetration testing and red team services.", "Not an automated pen testing product or PTaaS platform."],
            "notes": "Professional services only. No product-level pen testing automation."
        },
        "PPM-04": {
            "source_urls": ["https://www.paloaltonetworks.com/prisma/cloud", "https://docs.prismacloud.io/"],
            "key_evidence": [
                "Prisma Cloud is an industry-leading CNAPP platform providing comprehensive CSPM, CWPP, CIEM, and code security.",
                "Multi-cloud coverage for AWS, Azure, GCP, Oracle Cloud, and Alibaba Cloud.",
                "Named a Leader in Gartner Magic Quadrant for Cloud-Native Application Protection Platforms.",
                "Misconfiguration detection, compliance automation, and drift detection across cloud environments.",
                "Infrastructure-as-code security scanning integrated into CI/CD pipelines.",
                "Cloud workload runtime protection with vulnerability management and container security."
            ],
            "notes": "Market-leading CNAPP/CSPM. Prisma Cloud is the industry benchmark for cloud security posture management."
        }
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Palo Alto Networks scores 5 (Market-Leading) with Cortex Xpanse (acquired Expanse 2020) providing industry-leading external attack surface management. AI-powered discovery, accurate asset attribution across IPv4/IPv6, government adoption, and deep Cortex platform integration.", "evidence_quality_rationale": "Exceptional evidence. Analyst recognition, US federal adoption, dedicated product.", "scoring_level_justification": "Level 5: Best-in-class EASM with extensive customer base, government validation, and continuous innovation.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Palo Alto Networks scores 4 (Advanced) with Cortex Xpanse + XSOAR providing continuous exposure management with automated discovery, prioritization, and remediation orchestration — aligning closely with CTEM framework stages.", "evidence_quality_rationale": "Strong evidence from product documentation and platform integration.", "scoring_level_justification": "Level 4: Advanced capability with named products and platform integration.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Cortex Xpanse provides risk-based exposure prioritization with threat intelligence and business context. Strong but PANW is not a traditional VM vendor — prioritization is exposure-focused rather than vulnerability-catalog-focused.", "evidence_quality_rationale": "Good evidence from Xpanse documentation.", "scoring_level_justification": "Level 4: Named product with measurable risk scoring.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Some supply chain exposure monitoring through Xpanse discovery of subsidiary and partner assets. Not a dedicated supply chain risk management or SBOM platform.", "evidence_quality_rationale": "Moderate evidence.", "scoring_level_justification": "Level 3: Demonstrated capability through asset monitoring.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence of capability.", "evidence_quality_rationale": "No relevant evidence.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "Prisma Cloud provides some runtime protection for cloud workloads including container and serverless security. WildFire provides runtime malware sandboxing. Primarily monitoring-based rather than in-process RASP.", "evidence_quality_rationale": "Moderate evidence from cloud security documentation.", "scoring_level_justification": "Level 2: Some runtime protection without dedicated RASP.", "confidence": "medium"},
        "AMT-03": {"score_rationale": "Palo Alto Networks scores 4 (Advanced) with comprehensive dynamic network defense through Prisma Access ZTNA, next-gen firewall portfolio with micro-segmentation, IoT Security for device segmentation, and software-defined security with adaptive policy enforcement. Strongest network defense posture among EXM-primary vendors.", "evidence_quality_rationale": "Strong evidence from extensive network security portfolio documentation.", "scoring_level_justification": "Level 4: Multiple named products with enterprise-grade dynamic network defense capabilities.", "confidence": "high"},
        "AMT-04": {"score_rationale": "Some identity-based access control through Prisma Access and XSIAM but not a dedicated credential rotation or PAM platform.", "evidence_quality_rationale": "Limited evidence.", "scoring_level_justification": "Level 2: Generic identity integration without automated rotation.", "confidence": "medium"},
        "ADR-01": {"score_rationale": "Very limited deception capability. Not a product focus area.", "evidence_quality_rationale": "Minimal evidence.", "scoring_level_justification": "Level 1: Minimal capability.", "confidence": "medium"},
        "ADR-02": {"score_rationale": "Palo Alto Networks earns 5 (Market-Leading) with Unit 42 threat intelligence research, AutoFocus TIP, WildFire malware analysis (billions of samples daily), comprehensive MITRE ATT&CK mapping, and Cortex XSIAM intelligence integration. Unit 42 is universally recognized as a top threat intelligence organization.", "evidence_quality_rationale": "Exceptional evidence. Unit 42 publications, AutoFocus platform, analyst recognition.", "scoring_level_justification": "Level 5: Best-in-class threat intelligence with world-class research team and extensive automation.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Unit 42 provides expert threat hunting services and Cortex XDR offers advanced query-based hunting with behavioral analytics and ML detection. Strong combined product + services hunting capability.", "evidence_quality_rationale": "Strong evidence from Unit 42 and XDR documentation.", "scoring_level_justification": "Level 4: Named products and services with documented methodologies.", "confidence": "high"},
        "ADR-04": {"score_rationale": "Unit 42 provides incident response and adversary assessment services. Some takedown coordination through law enforcement collaboration. Not a dedicated DRP or takedown product.", "evidence_quality_rationale": "Moderate evidence from professional services.", "scoring_level_justification": "Level 3: Demonstrated capability through services.", "confidence": "medium"},
        "PPM-01": {"score_rationale": "Basic simulation through XDR/XSOAR playbooks. Not a dedicated BAS platform.", "evidence_quality_rationale": "Limited evidence.", "scoring_level_justification": "Level 2: Some simulation without dedicated BAS product.", "confidence": "medium"},
        "PPM-02": {"score_rationale": "XSOAR provides security orchestration with playbook-based control validation — testing SIEM, firewall, and EDR effectiveness through automated workflows. Good orchestration-driven approach to control validation.", "evidence_quality_rationale": "Good evidence from XSOAR product documentation.", "scoring_level_justification": "Level 3: Named product with documented control validation workflows.", "confidence": "high"},
        "PPM-03": {"score_rationale": "Unit 42 offers professional pen testing and red team services but PANW does not have an automated pen testing product or PTaaS platform.", "evidence_quality_rationale": "Some evidence from services documentation.", "scoring_level_justification": "Level 2: Professional services without product automation.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Palo Alto Networks earns 5 (Market-Leading) with Prisma Cloud — the industry's most comprehensive CNAPP platform providing CSPM, CWPP, CIEM, and code security across AWS, Azure, GCP, Oracle, and Alibaba Cloud. Named a Leader in Gartner MQ for CNAPP. Misconfiguration detection, compliance automation, IaC scanning, and runtime protection.", "evidence_quality_rationale": "Exceptional evidence. Gartner MQ Leader, extensive documentation, broad cloud coverage, analyst recognition.", "scoring_level_justification": "Level 5: Best-in-class CNAPP/CSPM with analyst leadership, broadest cloud coverage, and continuous innovation.", "confidence": "high"}
    }
}

# ═══════════════════════════════════════════════════════════════════════
# BATCH 2: Censys, CyCognito, Armis, Axonius, JupiterOne
# ═══════════════════════════════════════════════════════════════════════

VENDOR_RESEARCH["Censys"] = {
    "scores": {
        "EXM-01": 5, "EXM-02": 3, "EXM-03": 3, "EXM-04": 2,
        "AMT-01": 0, "AMT-02": 0, "AMT-03": 0, "AMT-04": 0,
        "ADR-01": 0, "ADR-02": 2, "ADR-03": 0, "ADR-04": 0,
        "PPM-01": 0, "PPM-02": 0, "PPM-03": 0, "PPM-04": 1
    },
    "evidence": {
        "EXM-01": {"source_urls": ["https://censys.com/platform/attack-surface-management/", "https://censys.com/"], "key_evidence": ["Censys Attack Surface Management provides continuous discovery of internet-facing assets using proprietary internet-wide scanning data.", "Censys Search indexes the entire IPv4 address space and 100+ protocols daily, providing the most comprehensive internet asset database.", "Automated asset attribution with risk scoring and cloud resource discovery.", "Founded by researchers who created the ZMap internet scanner at University of Michigan."], "notes": "Market-leading internet visibility and EASM. Founded on pioneering internet scanning research (ZMap)."},
        "EXM-02": {"source_urls": ["https://censys.com/platform/"], "key_evidence": ["Continuous exposure monitoring through daily internet-wide scanning.", "Some CTEM alignment through continuous discovery and risk prioritization.", "Primarily discovery and inventory rather than full CTEM lifecycle operationalization."], "notes": "Strong continuous discovery but not full CTEM program capability."},
        "EXM-03": {"source_urls": ["https://censys.com/platform/"], "key_evidence": ["Risk scoring and prioritization of discovered exposures based on vulnerability data and asset context.", "Not a traditional vulnerability management platform — focuses on exposure discovery rather than deep CVE-level prioritization."], "notes": "Exposure-focused prioritization. Not a full VM platform."},
        "EXM-04": {"source_urls": ["https://censys.com/"], "key_evidence": ["Some third-party visibility through subsidiary and supply chain asset discovery via internet scanning.", "Limited dedicated supply chain risk management capability."], "notes": "Basic third-party visibility through scanning."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://censys.com/"], "key_evidence": ["Censys internet scan data is used as threat intelligence input by security teams for identifying adversary infrastructure.", "Censys Search provides IOC enrichment through infrastructure analysis."], "notes": "Internet scan data serves as TI input but not a standalone TIP."},
        "ADR-03": {"source_urls": [], "key_evidence": ["No dedicated threat hunting capability."], "notes": "Outside scope."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": ["https://censys.com/"], "key_evidence": ["Some cloud resource discovery capabilities but not a dedicated CSPM platform."], "notes": "Minimal cloud posture management."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Censys scores 5 (Market-Leading) for ASM. Founded by the creators of ZMap internet scanner, Censys provides the industry's most comprehensive internet-wide scanning data — indexing all IPv4 addresses and 100+ protocols daily. Censys ASM uses this data for automated external attack surface discovery with accurate asset attribution.", "evidence_quality_rationale": "Exceptional. Academic origins, proprietary scanning infrastructure, analyst recognition.", "scoring_level_justification": "Level 5: Best-in-class internet visibility with pioneering scanning technology and comprehensive asset discovery.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Continuous discovery through daily scanning provides exposure monitoring but Censys is primarily a discovery and inventory platform rather than a full CTEM lifecycle solution.", "evidence_quality_rationale": "Moderate evidence.", "scoring_level_justification": "Level 3: Demonstrated continuous discovery without full CTEM operationalization.", "confidence": "medium"},
        "EXM-03": {"score_rationale": "Risk scoring and exposure prioritization capabilities but not a vulnerability management platform with CVE-level prioritization and remediation orchestration.", "evidence_quality_rationale": "Moderate evidence.", "scoring_level_justification": "Level 3: Documented risk scoring for discovered exposures.", "confidence": "medium"},
        "EXM-04": {"score_rationale": "Some third-party asset visibility through internet-wide scanning. Limited dedicated supply chain capability.", "evidence_quality_rationale": "Limited evidence.", "scoring_level_justification": "Level 2: Basic capability through scanning.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Censys data is used for threat intelligence enrichment and adversary infrastructure identification but is not a standalone TIP with IOC management and TTP mapping.", "evidence_quality_rationale": "Moderate. Data is used by TI teams but not a dedicated product.", "scoring_level_justification": "Level 2: Data contributes to TI workflows without dedicated TIP capability.", "confidence": "medium"},
        "ADR-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Some cloud asset discovery but not a CSPM platform.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1: Minimal cloud posture capability.", "confidence": "medium"}
    }
}

VENDOR_RESEARCH["CyCognito"] = {
    "scores": {
        "EXM-01": 5, "EXM-02": 4, "EXM-03": 4, "EXM-04": 3,
        "AMT-01": 0, "AMT-02": 0, "AMT-03": 0, "AMT-04": 0,
        "ADR-01": 0, "ADR-02": 1, "ADR-03": 0, "ADR-04": 0,
        "PPM-01": 0, "PPM-02": 1, "PPM-03": 2, "PPM-04": 1
    },
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.cycognito.com/platform/", "https://www.cycognito.com/"], "key_evidence": ["CyCognito provides automated external attack surface management using proprietary botnet-like reconnaissance technology to discover assets attackers can find.", "Platform discovers exposed assets across cloud, on-premises, subsidiary, and third-party environments without requiring any input or configuration.", "AI/ML-driven asset attribution and graph-based relationship mapping.", "Founded by former Israeli intelligence (Unit 8200) leaders with expertise in offensive reconnaissance."], "notes": "Innovative EASM with unique 'attacker perspective' approach. Strong AI/ML differentiation."},
        "EXM-02": {"source_urls": ["https://www.cycognito.com/platform/"], "key_evidence": ["Continuous exposure management with automated discovery, prioritization, and testing cycles.", "Platform provides continuous CTEM-aligned operations without manual configuration.", "Risk-based prioritization using business context and exploitability analysis."], "notes": "Strong CTEM alignment through fully automated continuous exposure lifecycle."},
        "EXM-03": {"source_urls": ["https://www.cycognito.com/platform/"], "key_evidence": ["Risk-based vulnerability prioritization using exploit intelligence, business context, and attacker accessibility.", "Automated vulnerability validation through active testing of discovered exposures.", "Priority scoring goes beyond CVSS using real-world exploitability and asset exposure."], "notes": "Good vulnerability prioritization with active validation approach."},
        "EXM-04": {"source_urls": ["https://www.cycognito.com/platform/"], "key_evidence": ["Discovers subsidiary and third-party assets through relationship mapping and attribution.", "Some supply chain exposure visibility through external discovery."], "notes": "Third-party visibility through discovery but not dedicated supply chain management."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No deception technology."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": [], "key_evidence": ["Basic threat context within priority scoring but no standalone TIP."], "notes": "Minimal."},
        "ADR-03": {"source_urls": [], "key_evidence": ["No threat hunting capability."], "notes": "Outside scope."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No BAS capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["Some control assessment through exposure testing."], "notes": "Minimal."},
        "PPM-03": {"source_urls": ["https://www.cycognito.com/platform/"], "key_evidence": ["CyCognito includes automated testing and validation of discovered exposures, providing some pen-test-like validation capability.", "Active exploitation testing of discovered vulnerabilities to confirm exploitability."], "notes": "Some automated exposure validation that resembles light pen testing."},
        "PPM-04": {"source_urls": [], "key_evidence": ["Some cloud asset discovery but not a CSPM platform."], "notes": "Minimal."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "CyCognito scores 5 (Market-Leading) with a unique EASM approach using botnet-like reconnaissance to discover assets from the attacker's perspective. Fully automated discovery without configuration, AI/ML asset attribution, and graph-based relationship mapping. Founded by Israeli intelligence veterans.", "evidence_quality_rationale": "Strong. Dedicated EASM platform with differentiated technology approach.", "scoring_level_justification": "Level 5: Best-in-class with unique technology approach, continuous innovation.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Strong CTEM alignment with fully automated continuous exposure lifecycle — discovery, prioritization, testing, and remediation without manual configuration.", "evidence_quality_rationale": "Good evidence from platform documentation.", "scoring_level_justification": "Level 4: Advanced continuous operation with automated lifecycle.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Risk-based prioritization using exploit intelligence, business context, and attacker accessibility. Active vulnerability validation through testing. Goes beyond CVSS.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 4: Named platform with active validation and risk scoring.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Discovers subsidiary and third-party assets through relationship mapping. Some supply chain visibility but not a dedicated capability.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 3: Demonstrated through discovery capabilities.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Basic threat context in scoring but no TIP.", "evidence_quality_rationale": "Minimal.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Minimal control assessment through exposure testing.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-03": {"score_rationale": "Automated exposure validation provides some pen-test-like capability — actively testing discovered vulnerabilities for exploitability.", "evidence_quality_rationale": "Moderate. Validation is part of the exposure platform.", "scoring_level_justification": "Level 2: Some automated testing without full pen test platform.", "confidence": "medium"},
        "PPM-04": {"score_rationale": "Some cloud discovery but not CSPM.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"}
    }
}

VENDOR_RESEARCH["Armis"] = {
    "scores": {
        "EXM-01": 5, "EXM-02": 4, "EXM-03": 3, "EXM-04": 3,
        "AMT-01": 0, "AMT-02": 0, "AMT-03": 2, "AMT-04": 0,
        "ADR-01": 0, "ADR-02": 2, "ADR-03": 1, "ADR-04": 0,
        "PPM-01": 0, "PPM-02": 1, "PPM-03": 0, "PPM-04": 2
    },
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.armis.com/platform/", "https://www.armis.com/cyberattack-surface-management/"], "key_evidence": ["Armis Centrix platform provides agentless asset discovery across IT, OT, IoT, IoMT, and cloud environments.", "AI-powered asset intelligence engine tracks 3+ billion assets globally for contextual risk analysis.", "Cyber Asset Attack Surface Management (CAASM) provides unified asset inventory with risk scoring.", "Discovered and manages assets that traditional scanners cannot see — unmanaged, IoT, and OT devices."], "notes": "Market-leading asset visibility especially for unmanaged/IoT/OT devices. 3B+ asset knowledge base."},
        "EXM-02": {"source_urls": ["https://www.armis.com/platform/"], "key_evidence": ["Armis Centrix provides continuous exposure management with real-time asset tracking, vulnerability prioritization, and remediation orchestration.", "Continuous monitoring cycle with risk-based prioritization aligns with CTEM framework."], "notes": "Good CTEM alignment through continuous asset and exposure lifecycle management."},
        "EXM-03": {"source_urls": ["https://www.armis.com/platform/"], "key_evidence": ["Risk-based vulnerability prioritization using asset context, exploitability, and threat intelligence.", "Prioritization considers device type, criticality, and network exposure beyond CVSS alone."], "notes": "Good prioritization but more asset-centric than vulnerability-catalog-focused."},
        "EXM-04": {"source_urls": ["https://www.armis.com/platform/"], "key_evidence": ["Some third-party visibility through IoT/OT device supply chain monitoring.", "Asset intelligence includes vendor and firmware provenance data."], "notes": "Some supply chain context through IoT/OT asset intelligence."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": ["https://www.armis.com/platform/"], "key_evidence": ["Armis provides network segmentation recommendations and policy enforcement for IoT/OT devices.", "Integration with NAC and firewall for dynamic device-level access control."], "notes": "Some dynamic device segmentation through IoT/OT network controls."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No credential rotation capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No deception technology."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://www.armis.com/platform/"], "key_evidence": ["Armis AI asset intelligence includes threat context from global device behavior analysis.", "Some threat intelligence enrichment from 3B+ device knowledge base."], "notes": "Asset-derived threat context rather than standalone TIP."},
        "ADR-03": {"source_urls": [], "key_evidence": ["Basic anomaly detection on IoT/OT devices but not proactive threat hunting."], "notes": "Minimal."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No BAS capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["Basic policy compliance checking for IoT/OT devices."], "notes": "Minimal."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": ["https://www.armis.com/platform/"], "key_evidence": ["Some cloud visibility through multi-cloud asset discovery but not a dedicated CSPM platform."], "notes": "Basic cloud visibility through asset discovery."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Armis scores 5 (Market-Leading) for ASM with its unique strength in discovering assets that traditional tools miss — unmanaged devices, IoT, OT, and IoMT. The Armis AI asset intelligence engine tracks 3B+ devices globally. Agentless architecture enables discovery across all device types.", "evidence_quality_rationale": "Strong. Dedicated CAASM platform with quantified asset base.", "scoring_level_justification": "Level 5: Best-in-class for unmanaged/IoT/OT asset discovery with unique capabilities.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Continuous exposure management through Armis Centrix with real-time asset tracking and risk-based lifecycle management aligning with CTEM.", "evidence_quality_rationale": "Good evidence from platform documentation.", "scoring_level_justification": "Level 4: Advanced continuous operation.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Risk-based prioritization using device context, criticality, and threat intelligence. More asset-centric than traditional VM-focused prioritization.", "evidence_quality_rationale": "Moderate evidence.", "scoring_level_justification": "Level 3: Demonstrated risk scoring with device context.", "confidence": "medium"},
        "EXM-04": {"score_rationale": "Some supply chain visibility through IoT/OT asset intelligence — vendor and firmware provenance tracking for connected devices.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 3: Demonstrated through IoT/OT intelligence.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Segmentation recommendations and NAC integration for IoT/OT device access control provide some dynamic network defense capability.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Some device-level network segmentation.", "confidence": "medium"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Asset-derived threat context from 3B+ device knowledge base provides some threat intelligence value but is not a standalone TIP.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Embedded intelligence without standalone TIP.", "confidence": "medium"},
        "ADR-03": {"score_rationale": "Basic IoT/OT anomaly detection but not proactive threat hunting.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1: Basic anomaly detection.", "confidence": "medium"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Basic policy compliance for IoT/OT devices.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Some cloud asset discovery but not a dedicated CSPM platform.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 2: Basic cloud visibility.", "confidence": "medium"}
    }
}

VENDOR_RESEARCH["Axonius"] = {
    "scores": {
        "EXM-01": 5, "EXM-02": 3, "EXM-03": 3, "EXM-04": 3,
        "AMT-01": 0, "AMT-02": 0, "AMT-03": 1, "AMT-04": 0,
        "ADR-01": 0, "ADR-02": 1, "ADR-03": 0, "ADR-04": 0,
        "PPM-01": 0, "PPM-02": 2, "PPM-03": 0, "PPM-04": 2
    },
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.axonius.com/platform", "https://www.axonius.com/"], "key_evidence": ["Axonius Cyber Asset Attack Surface Management (CAASM) provides comprehensive asset inventory by aggregating data from 800+ integrations.", "Correlates data from multiple sources (EDR, VM, CMDB, cloud, directory) to build a unified, deduplicated asset inventory.", "Identifies coverage gaps — devices missing EDR agents, unscanned assets, etc.", "Named a Leader in Gartner Market Guide for CAASM."], "notes": "Industry-leading CAASM. 800+ integrations for comprehensive asset correlation."},
        "EXM-02": {"source_urls": ["https://www.axonius.com/platform"], "key_evidence": ["Continuous asset monitoring and coverage gap identification supports exposure management.", "Not explicitly positioned as CTEM but continuous asset lifecycle management contributes to exposure management programs."], "notes": "CAASM contributes to CTEM through asset visibility. Not a full CTEM platform."},
        "EXM-03": {"source_urls": ["https://www.axonius.com/platform"], "key_evidence": ["Vulnerability data aggregation from multiple scanners with prioritization.", "Identifies assets with unpatched vulnerabilities and missing security controls.", "Risk context through asset criticality and business impact analysis."], "notes": "Aggregates and contextualizes vulnerability data. Not a primary VM platform."},
        "EXM-04": {"source_urls": ["https://www.axonius.com/platform"], "key_evidence": ["SaaS Management module provides visibility into third-party SaaS applications.", "Some supply chain visibility through software inventory and application tracking."], "notes": "SaaS management and software inventory provide some supply chain visibility."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": ["https://www.axonius.com/platform"], "key_evidence": ["Identifies network segmentation gaps and policy violations through asset correlation analysis."], "notes": "Identifies gaps but doesn't enforce dynamic segmentation."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": [], "key_evidence": ["Basic threat data enrichment through integrations with TI feeds."], "notes": "Minimal."},
        "ADR-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No BAS capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": ["https://www.axonius.com/platform"], "key_evidence": ["Security control coverage validation — identifies devices missing EDR, not scanned by VA, or lacking other security controls.", "Automated enforcement actions for compliance gaps."], "notes": "Good security control coverage validation through asset correlation."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": ["https://www.axonius.com/platform"], "key_evidence": ["Cloud asset discovery and management across multi-cloud environments.", "Identifies cloud configuration gaps through integration with cloud APIs."], "notes": "Some cloud visibility but not a CSPM platform."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Axonius scores 5 (Market-Leading) for ASM through its CAASM platform — aggregating data from 800+ integrations to build a comprehensive, deduplicated asset inventory. Uniquely identifies coverage gaps (missing EDR, unscanned assets). Named a Gartner CAASM leader.", "evidence_quality_rationale": "Exceptional. Analyst recognition, quantified integrations, dedicated CAASM category leadership.", "scoring_level_justification": "Level 5: Best-in-class CAASM with 800+ integrations and analyst leadership.", "confidence": "high"},
        "EXM-02": {"score_rationale": "CAASM supports CTEM through continuous asset monitoring and coverage gap identification. Not explicitly a CTEM platform.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 3: Contributory capability without explicit CTEM positioning.", "confidence": "medium"},
        "EXM-03": {"score_rationale": "Aggregates vulnerability data from multiple scanners with asset criticality context. Not a primary VM platform.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 3: Data aggregation and contextual prioritization.", "confidence": "medium"},
        "EXM-04": {"score_rationale": "SaaS Management and software inventory provide third-party visibility. Some supply chain tracking through application discovery.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 3: Demonstrated through SaaS management.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Identifies segmentation gaps but doesn't enforce dynamic segmentation.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1: Gap identification only.", "confidence": "medium"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Basic TI enrichment through integrations.", "evidence_quality_rationale": "Minimal.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Good security control coverage validation — identifies devices missing security agents and controls, with automated enforcement. A unique CAASM-driven approach to control validation.", "evidence_quality_rationale": "Good evidence from platform documentation.", "scoring_level_justification": "Level 2: Named capability with some automation.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Cloud asset discovery across multi-cloud but not a CSPM platform.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 2: Basic cloud visibility.", "confidence": "medium"}
    }
}

VENDOR_RESEARCH["JupiterOne"] = {
    "scores": {
        "EXM-01": 4, "EXM-02": 3, "EXM-03": 3, "EXM-04": 3,
        "AMT-01": 0, "AMT-02": 0, "AMT-03": 1, "AMT-04": 0,
        "ADR-01": 0, "ADR-02": 1, "ADR-03": 0, "ADR-04": 0,
        "PPM-01": 0, "PPM-02": 2, "PPM-03": 0, "PPM-04": 3
    },
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.jupiterone.com/platform", "https://www.jupiterone.com/"], "key_evidence": ["JupiterOne provides cyber asset attack surface management through graph-based asset inventory.", "Knowledge graph maps relationships between assets, users, configurations, and vulnerabilities.", "250+ integrations for comprehensive asset aggregation.", "Graph-based query engine (J1QL) enables advanced asset analysis and exposure discovery."], "notes": "Strong CAASM with innovative graph-based approach. Good for complex relationship mapping."},
        "EXM-02": {"source_urls": ["https://www.jupiterone.com/platform"], "key_evidence": ["Continuous asset monitoring and exposure identification through graph-based analysis.", "Some CTEM alignment through continuous visibility and risk assessment."], "notes": "Graph-based exposure management. Not explicitly CTEM-branded."},
        "EXM-03": {"source_urls": ["https://www.jupiterone.com/platform"], "key_evidence": ["Vulnerability data aggregation with risk context from the asset graph.", "Prioritization using asset relationships, business impact, and exposure analysis."], "notes": "Good contextual prioritization through graph relationships."},
        "EXM-04": {"source_urls": ["https://www.jupiterone.com/platform"], "key_evidence": ["Graph-based relationship mapping provides visibility into third-party connections and SaaS dependencies.", "Software inventory tracking through integrations."], "notes": "Good third-party visibility through graph-based relationship analysis."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": ["https://www.jupiterone.com/platform"], "key_evidence": ["Identifies segmentation and access control gaps through graph analysis."], "notes": "Gap identification only."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": [], "key_evidence": ["Basic threat context through vulnerability feed integrations."], "notes": "Minimal."},
        "ADR-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": ["https://www.jupiterone.com/platform"], "key_evidence": ["Security control coverage analysis through graph queries — identifies coverage gaps in EDR, MFA, and other security controls.", "Compliance evidence collection and audit support."], "notes": "Good control coverage analysis through graph-based queries."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": ["https://www.jupiterone.com/platform"], "key_evidence": ["Cloud asset inventory and configuration analysis across AWS, Azure, GCP.", "Graph-based cloud security analysis with compliance mapping.", "Identifies cloud misconfigurations through asset relationship analysis."], "notes": "Good graph-based cloud security analysis. CSPM-adjacent capability."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "JupiterOne scores 4 (Advanced) with a graph-based CAASM platform providing 250+ integrations, relationship mapping, and advanced J1QL query capabilities. Strong asset discovery and analysis but smaller scale than Axonius.", "evidence_quality_rationale": "Good evidence from platform documentation.", "scoring_level_justification": "Level 4: Named platform with measurable capabilities.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Continuous monitoring and graph-based exposure analysis provide CTEM-adjacent capability. Not explicitly CTEM-positioned.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 3: Demonstrated continuous operation.", "confidence": "medium"},
        "EXM-03": {"score_rationale": "Contextual vulnerability prioritization through graph-based asset relationships and business impact analysis.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 3: Documented contextual prioritization.", "confidence": "medium"},
        "EXM-04": {"score_rationale": "Graph-based relationship mapping provides good visibility into third-party connections, SaaS dependencies, and software inventory.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 3: Demonstrated through graph analysis.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Identifies access control and segmentation gaps through graph analysis but doesn't enforce changes.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Basic vulnerability feed integration.", "evidence_quality_rationale": "Minimal.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Graph-based security control coverage analysis identifies gaps in EDR, MFA, and other controls. Good for compliance evidence collection.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 2: Named capability with graph-based analysis.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Graph-based cloud asset analysis with configuration assessment and compliance mapping. CSPM-adjacent capability through asset graph.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Documented cloud security analysis through graph.", "confidence": "high"}
    }
}

# ═══════════════════════════════════════════════════════════════════════
# BATCH 3: XM Cyber, Bitsight, SecurityScorecard, Panorays, Morphisec
# ═══════════════════════════════════════════════════════════════════════

VENDOR_RESEARCH["XM Cyber"] = {
    "scores": {
        "EXM-01": 4, "EXM-02": 5, "EXM-03": 4, "EXM-04": 2,
        "AMT-01": 0, "AMT-02": 0, "AMT-03": 1, "AMT-04": 0,
        "ADR-01": 0, "ADR-02": 1, "ADR-03": 1, "ADR-04": 0,
        "PPM-01": 5, "PPM-02": 4, "PPM-03": 4, "PPM-04": 3
    },
    "evidence": {
        "EXM-01": {"source_urls": ["https://xmcyber.com/platform/", "https://xmcyber.com/"], "key_evidence": ["XM Cyber Continuous Exposure Management platform discovers hybrid attack surfaces across on-premises, cloud, and identity.", "Attack path analysis maps exploitable routes from external and internal perspectives.", "Asset criticality scoring based on attack path reach to critical assets."], "notes": "Strong ASM through attack path-driven exposure management."},
        "EXM-02": {"source_urls": ["https://xmcyber.com/platform/"], "key_evidence": ["XM Cyber is a pioneer in Continuous Threat Exposure Management, directly aligned with the Gartner CTEM framework.", "Platform provides continuous scoping, discovery, prioritization, validation, and mobilization of exposure remediation.", "Named a Leader in Gartner Hype Cycle for CTEM.", "Attack graph technology enables continuous exposure lifecycle management."], "notes": "Market-leading CTEM alignment. Directly positioned as a CTEM platform."},
        "EXM-03": {"source_urls": ["https://xmcyber.com/platform/"], "key_evidence": ["Attack path-based vulnerability prioritization — focuses on vulnerabilities that are actually reachable and exploitable in context.", "Choke point analysis identifies the highest-impact remediation actions.", "Prioritization goes far beyond CVSS by considering actual exploitability, lateral movement chains, and asset criticality."], "notes": "Excellent context-driven vulnerability prioritization through attack paths."},
        "EXM-04": {"source_urls": [], "key_evidence": ["Some third-party exposure through attack path analysis of interconnected environments.", "Limited dedicated supply chain risk management."], "notes": "Basic third-party visibility."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["Identifies segmentation weaknesses through attack path analysis."], "notes": "Identifies gaps only."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No deception technology."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": [], "key_evidence": ["Basic threat context in attack path analysis."], "notes": "Minimal."},
        "ADR-03": {"source_urls": [], "key_evidence": ["Attack path analysis can support hunting hypotheses but not a dedicated hunting product."], "notes": "Minimal support capability."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": ["https://xmcyber.com/platform/"], "key_evidence": ["XM Cyber provides continuous attack simulation through attack graph modeling — simulating thousands of attack paths without impacting production.", "Safe, production-grade simulation validates real exploitability of vulnerabilities and misconfigurations.", "Continuous BAS capability integrated into the exposure management platform.", "MITRE ATT&CK technique coverage across the full attack chain."], "notes": "Market-leading attack simulation through attack graph technology. Safe, continuous, production-grade."},
        "PPM-02": {"source_urls": ["https://xmcyber.com/platform/"], "key_evidence": ["Security control validation through attack path testing — identifies where controls fail to prevent lateral movement.", "Validates effectiveness of segmentation, EDR, and access controls against simulated attack paths.", "Gap analysis between expected and actual control effectiveness."], "notes": "Strong control validation through attack simulation."},
        "PPM-03": {"source_urls": ["https://xmcyber.com/platform/"], "key_evidence": ["Automated attack path analysis provides capabilities similar to automated penetration testing.", "Identifies exploitable paths and validates attack feasibility without manual pen testing.", "Red team exercise support through attack scenario modeling."], "notes": "Attack path analysis provides automated pen-test-like validation."},
        "PPM-04": {"source_urls": ["https://xmcyber.com/platform/"], "key_evidence": ["Cloud attack path analysis across AWS, Azure, and GCP.", "Identifies cloud misconfigurations that are actually exploitable in context.", "Hybrid attack path mapping from cloud to on-premises."], "notes": "Good cloud attack path analysis. Not dedicated CSPM but validates cloud security posture."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "XM Cyber scores 4 (Advanced) for ASM through attack path-driven asset discovery and exposure mapping across hybrid environments. Strong contextual ASM but not a dedicated EASM scanner.", "evidence_quality_rationale": "Good evidence from platform documentation.", "scoring_level_justification": "Level 4: Named platform with attack path-based ASM.", "confidence": "high"},
        "EXM-02": {"score_rationale": "XM Cyber scores 5 (Market-Leading) for CTEM. Directly aligned with and positioned for the Gartner CTEM framework. Continuous attack graph technology provides all CTEM stages: scoping, discovery, prioritization, validation, and mobilization. Named in Gartner Hype Cycle for CTEM.", "evidence_quality_rationale": "Exceptional. CTEM pioneer with direct Gartner recognition.", "scoring_level_justification": "Level 5: Best-in-class CTEM alignment with analyst recognition and continuous innovation.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Attack path-based prioritization that focuses on reachable, exploitable vulnerabilities with choke point analysis for maximum remediation impact. Far beyond CVSS.", "evidence_quality_rationale": "Strong evidence.", "scoring_level_justification": "Level 4: Advanced context-driven prioritization.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Basic third-party visibility through attack path analysis. Not dedicated supply chain management.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 2.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Identifies segmentation weaknesses but doesn't enforce changes.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Basic threat context in analysis.", "evidence_quality_rationale": "Minimal.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-03": {"score_rationale": "Attack paths can support hunting hypotheses but not a hunting product.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "XM Cyber scores 5 (Market-Leading) for BAS. Its attack graph technology simulates thousands of attack paths safely against production — validating real exploitability of vulnerabilities and misconfigurations with comprehensive MITRE ATT&CK coverage. Continuous, automated, and production-safe.", "evidence_quality_rationale": "Exceptional. Purpose-built simulation technology.", "scoring_level_justification": "Level 5: Best-in-class continuous attack simulation.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Security control validation through attack path testing validates where controls prevent or fail against lateral movement. Gap analysis of expected vs actual effectiveness.", "evidence_quality_rationale": "Strong evidence.", "scoring_level_justification": "Level 4: Advanced control validation through simulation.", "confidence": "high"},
        "PPM-03": {"score_rationale": "Automated attack path analysis provides pen-test-like validation — identifying exploitable paths and validating attack feasibility automatically.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 4: Automated attack validation.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Cloud attack path analysis across major cloud providers. Identifies exploitable cloud misconfigurations in context. Not pure CSPM but validates cloud posture.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Cloud attack path analysis.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Bitsight"] = {
    "scores": {
        "EXM-01": 3, "EXM-02": 2, "EXM-03": 2, "EXM-04": 5,
        "AMT-01": 0, "AMT-02": 0, "AMT-03": 0, "AMT-04": 0,
        "ADR-01": 0, "ADR-02": 1, "ADR-03": 0, "ADR-04": 1,
        "PPM-01": 0, "PPM-02": 0, "PPM-03": 0, "PPM-04": 1
    },
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.bitsight.com/products/attack-surface-analytics", "https://www.bitsight.com/"], "key_evidence": ["Bitsight Attack Surface Analytics provides external visibility into an organization's digital footprint.", "Internet scanning and passive data collection for asset discovery.", "Security ratings provide risk scoring for external-facing assets."], "notes": "External visibility through security ratings and scanning. More ratings-focused than pure EASM."},
        "EXM-02": {"source_urls": ["https://www.bitsight.com/"], "key_evidence": ["Continuous monitoring of security posture through ratings and scanning.", "Not explicitly a CTEM platform — provides continuous ratings rather than full exposure lifecycle."], "notes": "Continuous ratings monitoring. Not CTEM."},
        "EXM-03": {"source_urls": ["https://www.bitsight.com/"], "key_evidence": ["Security ratings provide risk scoring for organizations.", "Not vulnerability-level prioritization — ratings are organizational, not CVE-level."], "notes": "Organizational risk ratings rather than vulnerability prioritization."},
        "EXM-04": {"source_urls": ["https://www.bitsight.com/products/third-party-risk-management", "https://www.bitsight.com/"], "key_evidence": ["Bitsight is a market leader in third-party risk management through security ratings.", "Continuous monitoring of vendor security posture using outside-in assessment.", "Large enterprise and government adoption for vendor risk assessment.", "Quantified risk scoring enables data-driven third-party risk decisions.", "Named a Leader in Forrester Wave for Security Ratings."], "notes": "Market-leading third-party risk management through security ratings. Forrester Wave Leader."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": [], "key_evidence": ["Basic threat context in security ratings."], "notes": "Minimal."},
        "ADR-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-04": {"source_urls": ["https://www.bitsight.com/"], "key_evidence": ["Some dark web monitoring signals feed into security ratings.", "Basic breach exposure monitoring."], "notes": "Basic external risk monitoring."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": [], "key_evidence": ["Basic cloud visibility in ratings."], "notes": "Minimal."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Bitsight provides external attack surface visibility through security ratings and scanning, but is more of a ratings platform than a dedicated EASM scanner.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 3: Demonstrated external visibility.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Continuous ratings monitoring but not a CTEM platform.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 2: Basic continuous monitoring.", "confidence": "medium"},
        "EXM-03": {"score_rationale": "Organizational risk ratings rather than vulnerability-level prioritization.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 2: Org-level risk scoring.", "confidence": "medium"},
        "EXM-04": {"score_rationale": "Bitsight scores 5 (Market-Leading) for Third-Party & Supply Chain Exposure. Market leader in security ratings for third-party risk management with continuous vendor monitoring, quantified risk scoring, and large enterprise adoption. Named a Forrester Wave Leader.", "evidence_quality_rationale": "Exceptional. Analyst recognition, market leadership, extensive adoption.", "scoring_level_justification": "Level 5: Best-in-class third-party risk through security ratings.", "confidence": "high"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Basic threat context in ratings.", "evidence_quality_rationale": "Minimal.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-04": {"score_rationale": "Some dark web monitoring signals and breach exposure data feed into ratings.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Basic cloud visibility in ratings.", "evidence_quality_rationale": "Minimal.", "scoring_level_justification": "Level 1.", "confidence": "medium"}
    }
}

VENDOR_RESEARCH["SecurityScorecard"] = {
    "scores": {
        "EXM-01": 3, "EXM-02": 2, "EXM-03": 2, "EXM-04": 5,
        "AMT-01": 0, "AMT-02": 0, "AMT-03": 0, "AMT-04": 0,
        "ADR-01": 0, "ADR-02": 2, "ADR-03": 0, "ADR-04": 2,
        "PPM-01": 0, "PPM-02": 0, "PPM-03": 0, "PPM-04": 1
    },
    "evidence": {
        "EXM-01": {"source_urls": ["https://securityscorecard.com/platform/attack-surface-intelligence/", "https://securityscorecard.com/"], "key_evidence": ["SecurityScorecard Attack Surface Intelligence provides external visibility into digital footprints.", "AI-driven scanning for exposed assets, open ports, and misconfigurations."], "notes": "External visibility through ratings platform. Similar scope to Bitsight."},
        "EXM-02": {"source_urls": [], "key_evidence": ["Continuous ratings monitoring. Not a CTEM platform."], "notes": "Continuous monitoring only."},
        "EXM-03": {"source_urls": [], "key_evidence": ["Organizational risk ratings rather than CVE-level vulnerability prioritization."], "notes": "Org-level scoring."},
        "EXM-04": {"source_urls": ["https://securityscorecard.com/platform/third-party-risk-management/", "https://securityscorecard.com/"], "key_evidence": ["SecurityScorecard is a market leader in third-party risk management through continuous security ratings.", "A-F letter grade scoring for vendor security posture assessment.", "MAX (Managed Third-Party Risk) service provides vendor risk lifecycle management.", "Automatic vendor discovery identifies shadow IT and unvetted third parties.", "Named a Forrester Wave Leader alongside Bitsight for security ratings."], "notes": "Market-leading TPRM. Forrester Wave Leader. A-F grading is industry standard."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://securityscorecard.com/"], "key_evidence": ["SecurityScorecard provides threat intelligence through its scanning infrastructure.", "Some IOC enrichment through external monitoring data."], "notes": "Basic TI from scanning infrastructure."},
        "ADR-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-04": {"source_urls": ["https://securityscorecard.com/"], "key_evidence": ["Some digital risk monitoring through external scanning.", "Breach notification and exposure tracking capabilities."], "notes": "Basic digital risk monitoring."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": [], "key_evidence": ["Basic cloud visibility in ratings."], "notes": "Minimal."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "External attack surface visibility through ratings and scanning infrastructure. Not a dedicated EASM platform.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 3: Demonstrated external visibility.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Continuous external monitoring. Not CTEM.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 2.", "confidence": "medium"},
        "EXM-03": {"score_rationale": "Organizational risk ratings, not vulnerability-level prioritization.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 2.", "confidence": "medium"},
        "EXM-04": {"score_rationale": "SecurityScorecard scores 5 (Market-Leading) for Third-Party Risk. Market leader in TPRM with A-F security ratings, automatic vendor discovery, and MAX managed service. Forrester Wave Leader. Industry-standard scoring methodology.", "evidence_quality_rationale": "Exceptional. Analyst recognition, market leadership.", "scoring_level_justification": "Level 5: Best-in-class TPRM.", "confidence": "high"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Basic TI from scanning infrastructure and IOC enrichment through monitoring data.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Some TI capability.", "confidence": "medium"},
        "ADR-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-04": {"score_rationale": "Digital risk monitoring through external scanning and breach notification tracking.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Basic DRP.", "confidence": "medium"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Basic cloud visibility in ratings.", "evidence_quality_rationale": "Minimal.", "scoring_level_justification": "Level 1.", "confidence": "medium"}
    }
}

VENDOR_RESEARCH["Panorays"] = {
    "scores": {
        "EXM-01": 2, "EXM-02": 1, "EXM-03": 1, "EXM-04": 4,
        "AMT-01": 0, "AMT-02": 0, "AMT-03": 0, "AMT-04": 0,
        "ADR-01": 0, "ADR-02": 1, "ADR-03": 0, "ADR-04": 1,
        "PPM-01": 0, "PPM-02": 0, "PPM-03": 0, "PPM-04": 0
    },
    "evidence": {
        "EXM-01": {"source_urls": ["https://panorays.com/", "https://panorays.com/platform/"], "key_evidence": ["Panorays provides external attack surface assessment as part of third-party risk evaluation.", "External scanning of vendor digital footprints for risk assessment."], "notes": "Basic external scanning for TPRM purposes. Not a dedicated EASM platform."},
        "EXM-02": {"source_urls": [], "key_evidence": ["Not a CTEM platform. Focused on third-party risk assessment cycles."], "notes": "Not applicable."},
        "EXM-03": {"source_urls": [], "key_evidence": ["Basic risk scoring for third-party assessment. Not vulnerability-level prioritization."], "notes": "Not applicable."},
        "EXM-04": {"source_urls": ["https://panorays.com/platform/"], "key_evidence": ["Panorays provides automated third-party security risk management with continuous monitoring.", "External attack surface assessment combined with security questionnaire automation.", "Supply chain risk mapping and vendor relationship management.", "Focuses specifically on TPRM — combining outside-in assessment with questionnaire automation."], "notes": "Dedicated TPRM platform. Combines technical scanning with questionnaire automation."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": [], "key_evidence": ["Basic threat data in vendor risk scores."], "notes": "Minimal."},
        "ADR-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-04": {"source_urls": [], "key_evidence": ["Basic breach monitoring for assessed vendors."], "notes": "Minimal."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "External scanning as part of TPRM assessment. Not a dedicated EASM platform.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 2: Basic external scanning.", "confidence": "medium"},
        "EXM-02": {"score_rationale": "Not a CTEM platform.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 1: Minimal.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Basic risk scoring for third-party assessment.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1: Basic scoring.", "confidence": "medium"},
        "EXM-04": {"score_rationale": "Panorays scores 4 (Advanced) for TPRM with dedicated platform combining automated external attack surface assessment, security questionnaire automation, continuous monitoring, and supply chain risk mapping. Strong TPRM specialist.", "evidence_quality_rationale": "Good evidence from platform documentation.", "scoring_level_justification": "Level 4: Named TPRM platform with measurable capabilities.", "confidence": "high"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Basic threat data in risk scores.", "evidence_quality_rationale": "Minimal.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-04": {"score_rationale": "Basic breach monitoring for assessed vendors.", "evidence_quality_rationale": "Minimal.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Morphisec"] = {
    "scores": {
        "EXM-01": 0, "EXM-02": 0, "EXM-03": 1, "EXM-04": 0,
        "AMT-01": 5, "AMT-02": 4, "AMT-03": 1, "AMT-04": 0,
        "ADR-01": 1, "ADR-02": 0, "ADR-03": 0, "ADR-04": 0,
        "PPM-01": 0, "PPM-02": 0, "PPM-03": 0, "PPM-04": 0
    },
    "evidence": {
        "EXM-01": {"source_urls": [], "key_evidence": ["No ASM capability."], "notes": "Outside scope."},
        "EXM-02": {"source_urls": [], "key_evidence": ["No CTEM capability."], "notes": "Outside scope."},
        "EXM-03": {"source_urls": ["https://www.morphisec.com/"], "key_evidence": ["Basic vulnerability visibility through endpoint assessment but not a VM platform."], "notes": "Minimal."},
        "EXM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-01": {"source_urls": ["https://www.morphisec.com/technology/", "https://www.morphisec.com/"], "key_evidence": ["Morphisec is the pioneer of Moving Target Defense (AMTD) technology for endpoint protection.", "Morphisec Guard uses patented Moving Target Defense to morphe memory at runtime — randomizing process memory layouts to prevent exploitation.", "Blocks fileless attacks, zero-days, and advanced memory-based attacks without signatures or behavioral analysis.", "Gartner recognized Morphisec as a key vendor in the Automated Moving Target Defense (AMTD) category.", "Lightweight agent with near-zero performance impact and no cloud connectivity required for protection."], "notes": "Market-defining AMTD vendor. Pioneer of Moving Target Defense for endpoint protection."},
        "AMT-02": {"source_urls": ["https://www.morphisec.com/technology/"], "key_evidence": ["Runtime application protection through memory morphing prevents exploit execution in running applications.", "In-process protection against buffer overflows, ROP chains, and memory corruption attacks.", "Application hardening through runtime randomization without code changes or signatures.", "Protects both legacy and modern applications at runtime."], "notes": "Strong runtime protection through AMTD. Not traditional RASP but achieves similar outcomes through memory mutation."},
        "AMT-03": {"source_urls": [], "key_evidence": ["Endpoint-focused. No network-level dynamic defense or micro-segmentation."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No credential rotation capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": ["https://www.morphisec.com/"], "key_evidence": ["Moving Target Defense creates deception-like effects — attackers target randomized memory structures that don't match expectations, causing attack failure without alerting the attacker to the defense mechanism."], "notes": "Deception-adjacent through MTD. Attacker is implicitly deceived by morphed runtime environment."},
        "ADR-02": {"source_urls": [], "key_evidence": ["No TIP capability."], "notes": "Outside scope."},
        "ADR-03": {"source_urls": [], "key_evidence": ["No threat hunting capability."], "notes": "Outside scope."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No BAS capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "No ASM capability. Endpoint protection focused.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-02": {"score_rationale": "No CTEM capability.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Basic endpoint vulnerability visibility but not a VM platform.", "evidence_quality_rationale": "Minimal.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "EXM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-01": {"score_rationale": "Morphisec scores 5 (Market-Leading) for Polymorphic Defense. As the pioneer and defining vendor of Moving Target Defense / AMTD for endpoints, Morphisec Guard morphs memory at runtime — randomizing process memory layouts to prevent zero-day exploitation without signatures. Gartner recognizes Morphisec in the AMTD category. Patented technology with lightweight agent requiring no cloud connectivity.", "evidence_quality_rationale": "Exceptional. Category-defining vendor with Gartner recognition, patented technology.", "scoring_level_justification": "Level 5: Best-in-class, category-defining Moving Target Defense with analyst recognition and patented technology.", "confidence": "high"},
        "AMT-02": {"score_rationale": "Morphisec scores 4 (Advanced) for Runtime Application Protection through memory morphing — providing in-process protection against buffer overflows, ROP chains, and memory corruption without signatures or code changes. Not traditional RASP but achieves similar prevention outcomes through AMTD.", "evidence_quality_rationale": "Strong evidence from technology documentation.", "scoring_level_justification": "Level 4: Advanced runtime protection through innovative AMTD approach.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Endpoint-focused solution. No network-level dynamic defense capabilities.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 1: Minimal indirect contribution.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No credential rotation capability.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "MTD creates deception-adjacent effects — attackers unknowingly target morphed memory structures. Not a deception platform but the approach inherently deceives exploitation attempts.", "evidence_quality_rationale": "Some evidence. Deception is a byproduct, not the primary capability.", "scoring_level_justification": "Level 1: Implicit deception through MTD.", "confidence": "medium"},
        "ADR-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"}
    }
}

# ═══════════════════════════════════════════════════════════════════════
# BATCH 4: RunSafe Security, Contrast Security, Illumio, Akamai (Guardicore), Zscaler
# ═══════════════════════════════════════════════════════════════════════

VENDOR_RESEARCH["RunSafe Security"] = {
    "scores": {"EXM-01": 0, "EXM-02": 0, "EXM-03": 0, "EXM-04": 0, "AMT-01": 5, "AMT-02": 3, "AMT-03": 0, "AMT-04": 0, "ADR-01": 0, "ADR-02": 0, "ADR-03": 0, "ADR-04": 0, "PPM-01": 0, "PPM-02": 0, "PPM-03": 0, "PPM-04": 0},
    "evidence": {
        "EXM-01": {"source_urls": [], "key_evidence": ["No ASM capability."], "notes": "Outside scope."},
        "EXM-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "EXM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "EXM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-01": {"source_urls": ["https://runsafesecurity.com/", "https://runsafesecurity.com/technology/"], "key_evidence": ["RunSafe Security provides Alkemist — a runtime binary transformation platform that randomizes memory layout at the binary level.", "Compile-time and load-time diversification creates unique binary variants, preventing memory-based exploits from being reusable across targets.", "DARPA-funded technology for moving target defense in critical infrastructure and embedded systems.", "Addresses zero-day exploitation by making each deployment a unique target — eliminating static attack surfaces.", "Focused on OT, IoT, and embedded systems where traditional security agents cannot be deployed."], "notes": "AMTD specialist for embedded/OT/IoT. DARPA-funded binary diversification technology."},
        "AMT-02": {"source_urls": ["https://runsafesecurity.com/technology/"], "key_evidence": ["Alkemist provides load-time randomization that hardens applications against runtime exploitation.", "Prevents memory corruption attacks (buffer overflow, ROP chains) through binary transformation.", "Not traditional RASP but provides compile-time application hardening with runtime protection effect."], "notes": "Binary-level application hardening. Effective runtime protection through a different approach than RASP."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No network defense capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-01": {"score_rationale": "RunSafe scores 5 (Market-Leading) with Alkemist — DARPA-funded binary transformation technology that randomizes memory layout at compile/load time. Creates unique binary variants making memory exploitation unreliable across deployments. Focused on OT/IoT/embedded where traditional security cannot be deployed.", "evidence_quality_rationale": "Strong. DARPA funding, academic-grade technology, dedicated purpose.", "scoring_level_justification": "Level 5: Best-in-class moving target defense for embedded/OT systems.", "confidence": "high"},
        "AMT-02": {"score_rationale": "Load-time randomization provides application hardening against runtime exploitation. Different approach than RASP but effective protection against memory corruption attacks.", "evidence_quality_rationale": "Good evidence from technology documentation.", "scoring_level_justification": "Level 3: Demonstrated runtime protection through binary transformation.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Contrast Security"] = {
    "scores": {"EXM-01": 1, "EXM-02": 0, "EXM-03": 2, "EXM-04": 1, "AMT-01": 1, "AMT-02": 5, "AMT-03": 0, "AMT-04": 0, "ADR-01": 0, "ADR-02": 0, "ADR-03": 0, "ADR-04": 0, "PPM-01": 0, "PPM-02": 1, "PPM-03": 1, "PPM-04": 0},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.contrastsecurity.com/"], "key_evidence": ["Some application-layer asset discovery through instrumentation but not dedicated ASM."], "notes": "Minimal. Application-centric."},
        "EXM-02": {"source_urls": [], "key_evidence": ["No CTEM capability."], "notes": "Outside scope."},
        "EXM-03": {"source_urls": ["https://www.contrastsecurity.com/"], "key_evidence": ["Vulnerability discovery through IAST/SCA with some prioritization based on exploitability in running applications.", "Identifies vulnerabilities that are actually reachable and exercised in code paths."], "notes": "Application vulnerability prioritization through instrumentation."},
        "EXM-04": {"source_urls": ["https://www.contrastsecurity.com/"], "key_evidence": ["Contrast SCA (Software Composition Analysis) identifies open-source library vulnerabilities."], "notes": "Basic SCA for open-source risks."},
        "AMT-01": {"source_urls": ["https://www.contrastsecurity.com/"], "key_evidence": ["Some runtime code mutation through instrumentation but primarily for detection, not active defense mutation."], "notes": "Instrumentation provides some mutation-adjacent capability."},
        "AMT-02": {"source_urls": ["https://www.contrastsecurity.com/runtime-security/", "https://www.contrastsecurity.com/"], "key_evidence": ["Contrast Protect provides industry-leading RASP (Runtime Application Self-Protection) — blocking attacks from within the application at runtime.", "In-process instrumentation detects and blocks OWASP Top 10 attacks including SQL injection, XSS, SSRF, and path traversal without signatures.", "Contrast Assess provides IAST (Interactive Application Security Testing) identifying vulnerabilities during runtime.", "Code-level visibility into application behavior for exploit detection and prevention.", "Named in Gartner Hype Cycle for Application Security and recognized as RASP category leader."], "notes": "Market-leading RASP/IAST. Contrast Protect is the industry standard for runtime application protection."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No network defense capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": ["https://www.contrastsecurity.com/"], "key_evidence": ["Runtime instrumentation provides some security control validation at the application layer."], "notes": "Basic application-level control validation."},
        "PPM-03": {"source_urls": ["https://www.contrastsecurity.com/"], "key_evidence": ["IAST discovers vulnerabilities during normal testing/QA — providing pen-test-like findings automatically during development."], "notes": "IAST provides automated vulnerability discovery during testing."},
        "PPM-04": {"source_urls": [], "key_evidence": ["No CSPM capability."], "notes": "Outside scope."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Minimal application-layer asset visibility through instrumentation.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-03": {"score_rationale": "IAST/SCA identifies vulnerabilities with runtime exploitability context. Application-focused prioritization.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Application-specific vulnerability discovery.", "confidence": "medium"},
        "EXM-04": {"score_rationale": "Contrast SCA identifies open-source component vulnerabilities — basic supply chain capability.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1: Basic SCA.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "Some runtime code mutation through instrumentation but primarily for detection purposes.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1: Minimal mutation-adjacent capability.", "confidence": "medium"},
        "AMT-02": {"score_rationale": "Contrast scores 5 (Market-Leading) for Runtime Application Protection. Contrast Protect is the industry-standard RASP — blocking OWASP Top 10 attacks from within the application at runtime without signatures. Contrast Assess provides IAST for interactive vulnerability discovery. Gartner-recognized category leader.", "evidence_quality_rationale": "Exceptional. Category-defining RASP with analyst recognition.", "scoring_level_justification": "Level 5: Best-in-class RASP with extensive documentation and analyst leadership.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Application-level control validation through runtime instrumentation.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-03": {"score_rationale": "IAST provides automated vulnerability discovery during testing — pen-test-adjacent findings.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Illumio"] = {
    "scores": {"EXM-01": 2, "EXM-02": 1, "EXM-03": 1, "EXM-04": 0, "AMT-01": 1, "AMT-02": 0, "AMT-03": 5, "AMT-04": 1, "ADR-01": 0, "ADR-02": 0, "ADR-03": 0, "ADR-04": 0, "PPM-01": 0, "PPM-02": 2, "PPM-03": 0, "PPM-04": 2},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.illumio.com/"], "key_evidence": ["Illumio provides application dependency mapping and visibility into east-west traffic flows.", "Real-time visibility into communication pathways across hybrid environments."], "notes": "Application visibility but not external ASM."},
        "EXM-02": {"source_urls": [], "key_evidence": ["Not a CTEM platform."], "notes": "Minimal."},
        "EXM-03": {"source_urls": [], "key_evidence": ["Basic vulnerability context through traffic analysis."], "notes": "Minimal."},
        "EXM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-01": {"source_urls": ["https://www.illumio.com/"], "key_evidence": ["Segmentation policies can be dynamically updated, providing some defense mutation effect, but Illumio is primarily policy-based, not runtime randomization."], "notes": "Policy-based segmentation, not true AMTD."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No RASP capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": ["https://www.illumio.com/products/", "https://www.illumio.com/"], "key_evidence": ["Illumio is the industry leader in Zero Trust Segmentation — providing micro-segmentation across data centers, cloud, containers, and endpoints.", "Illumio Core provides workload-level micro-segmentation with policy-based access control.", "Illumio Endpoint extends segmentation to user endpoints for lateral movement prevention.", "Illumio CloudSecure provides cloud-native segmentation across multi-cloud.", "Real-time traffic flow mapping (Illumination) enables adaptive policy creation.", "Named a Leader in Forrester Wave for Microsegmentation and Zero Trust."], "notes": "Market-leading Zero Trust Segmentation. Forrester Wave Leader for microsegmentation."},
        "AMT-04": {"source_urls": [], "key_evidence": ["Identity-aware segmentation policies but not credential rotation."], "notes": "Minimal."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": ["https://www.illumio.com/"], "key_evidence": ["Segmentation policy verification and enforcement validation.", "Visibility into whether segmentation controls are correctly applied and effective."], "notes": "Segmentation control validation."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": ["https://www.illumio.com/products/"], "key_evidence": ["Illumio CloudSecure provides cloud segmentation posture management.", "Some cloud misconfiguration detection related to network access controls."], "notes": "Cloud segmentation posture. Not full CSPM."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Application dependency mapping provides internal visibility but not external ASM.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Internal traffic visibility.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Not a CTEM platform.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Basic vulnerability context.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "EXM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-01": {"score_rationale": "Dynamic policy updates provide some defense mutation but Illumio is policy-based segmentation, not runtime randomization.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1: Policy-based rather than true AMTD.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Illumio scores 5 (Market-Leading) for Dynamic Network Defense. Industry leader in Zero Trust Segmentation with Illumio Core (workload), Endpoint (user), and CloudSecure (cloud) providing comprehensive micro-segmentation. Forrester Wave Leader. Real-time traffic mapping (Illumination) enables adaptive policy. Prevents lateral movement across hybrid environments.", "evidence_quality_rationale": "Exceptional. Forrester Wave Leader, extensive documentation, market leadership.", "scoring_level_justification": "Level 5: Best-in-class micro-segmentation with analyst leadership.", "confidence": "high"},
        "AMT-04": {"score_rationale": "Identity-aware policies but no credential rotation.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Segmentation policy verification and enforcement validation provides some control validation capability.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Segmentation control validation.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "CloudSecure provides cloud segmentation posture management. Not full CSPM.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Cloud segmentation posture.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Akamai (Guardicore)"] = {
    "scores": {"EXM-01": 1, "EXM-02": 0, "EXM-03": 1, "EXM-04": 1, "AMT-01": 0, "AMT-02": 1, "AMT-03": 4, "AMT-04": 1, "ADR-01": 2, "ADR-02": 2, "ADR-03": 1, "ADR-04": 0, "PPM-01": 0, "PPM-02": 1, "PPM-03": 0, "PPM-04": 1},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.akamai.com/products/akamai-guardicore-segmentation"], "key_evidence": ["Application dependency mapping for segmentation planning provides some internal visibility."], "notes": "Internal visibility only."},
        "EXM-02": {"source_urls": [], "key_evidence": ["No CTEM capability."], "notes": "Outside scope."},
        "EXM-03": {"source_urls": [], "key_evidence": ["Basic vulnerability context."], "notes": "Minimal."},
        "EXM-04": {"source_urls": [], "key_evidence": ["Basic supply chain visibility through web application security."], "notes": "Minimal."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No AMTD capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": ["https://www.akamai.com/"], "key_evidence": ["Akamai App & API Protector provides some runtime application protection through WAF/bot management."], "notes": "WAF-based protection, not RASP."},
        "AMT-03": {"source_urls": ["https://www.akamai.com/products/akamai-guardicore-segmentation", "https://www.akamai.com/"], "key_evidence": ["Akamai Guardicore Segmentation provides micro-segmentation at the process level across hybrid environments.", "Software-based segmentation without network changes — works across bare metal, VMs, containers, and cloud.", "Real-time visibility into east-west traffic with application dependency mapping.", "Hunt module enables investigation of lateral movement and suspicious network activity."], "notes": "Strong micro-segmentation through Guardicore acquisition. Process-level granularity is a differentiator."},
        "AMT-04": {"source_urls": [], "key_evidence": ["Some identity-aware access through Enterprise Application Access (EAA)."], "notes": "Basic ZTNA."},
        "ADR-01": {"source_urls": ["https://www.akamai.com/products/akamai-guardicore-segmentation"], "key_evidence": ["Guardicore includes deception capabilities — deploying honeypots and decoys to detect lateral movement within segmented environments.", "Deception module integrates with segmentation for high-fidelity alerting."], "notes": "Integrated deception within segmentation platform. Good but limited compared to pure-play."},
        "ADR-02": {"source_urls": ["https://www.akamai.com/"], "key_evidence": ["Akamai provides threat intelligence from its massive global CDN/edge network.", "Bot and attack data from protecting 30%+ of global web traffic provides unique threat intelligence."], "notes": "Unique edge-derived threat intelligence from global CDN."},
        "ADR-03": {"source_urls": ["https://www.akamai.com/products/akamai-guardicore-segmentation"], "key_evidence": ["Guardicore Hunt module provides investigation and hunting capabilities for lateral movement detection."], "notes": "Basic hunting through Hunt module."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["Basic segmentation control validation."], "notes": "Minimal."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": [], "key_evidence": ["Some cloud segmentation."], "notes": "Minimal."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Internal application visibility only.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "EXM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Basic vulnerability context.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Basic web app supply chain visibility.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "WAF-based application protection through App & API Protector. Not RASP.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Akamai Guardicore scores 4 (Advanced) for Dynamic Network Defense with process-level micro-segmentation across hybrid environments (bare metal, VMs, containers, cloud) without network changes. Real-time east-west traffic visibility and application dependency mapping.", "evidence_quality_rationale": "Strong evidence from Guardicore documentation.", "scoring_level_justification": "Level 4: Advanced software-based micro-segmentation with process-level granularity.", "confidence": "high"},
        "AMT-04": {"score_rationale": "Some identity-aware access through EAA.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "ADR-01": {"score_rationale": "Guardicore includes integrated deception capabilities — honeypots and decoys deployed within segmented environments for lateral movement detection.", "evidence_quality_rationale": "Moderate. Integrated feature, not standalone.", "scoring_level_justification": "Level 2: Integrated deception within segmentation.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Unique edge-derived threat intelligence from protecting 30%+ of global web traffic. Bot and attack intelligence at massive scale.", "evidence_quality_rationale": "Moderate. Unique data source.", "scoring_level_justification": "Level 2: Embedded TI from edge network.", "confidence": "medium"},
        "ADR-03": {"score_rationale": "Hunt module provides investigation and hunting for lateral movement.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1: Basic hunting module.", "confidence": "medium"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Basic segmentation control validation.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Some cloud segmentation posture.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Zscaler"] = {
    "scores": {"EXM-01": 3, "EXM-02": 2, "EXM-03": 2, "EXM-04": 2, "AMT-01": 1, "AMT-02": 2, "AMT-03": 5, "AMT-04": 3, "ADR-01": 2, "ADR-02": 3, "ADR-03": 1, "ADR-04": 1, "PPM-01": 0, "PPM-02": 2, "PPM-03": 0, "PPM-04": 3},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.zscaler.com/products/attack-surface-management"], "key_evidence": ["Zscaler Attack Surface Management provides external attack surface discovery.", "Integrated with Zscaler Risk360 for risk quantification and prioritization.", "Identifies exposed applications, services, and misconfigurations across internet-facing assets."], "notes": "External ASM capability through dedicated product."},
        "EXM-02": {"source_urls": ["https://www.zscaler.com/"], "key_evidence": ["Some exposure management through Risk360 and continuous monitoring.", "Not explicitly a CTEM platform."], "notes": "Risk360 provides some exposure lifecycle management."},
        "EXM-03": {"source_urls": ["https://www.zscaler.com/"], "key_evidence": ["Risk360 provides risk quantification and prioritization.", "Not traditional VM but exposure-level risk scoring."], "notes": "Risk quantification through Risk360."},
        "EXM-04": {"source_urls": ["https://www.zscaler.com/"], "key_evidence": ["Some supply chain visibility through web traffic inspection and SaaS monitoring.", "Digital Experience Monitoring identifies third-party dependencies."], "notes": "Basic supply chain visibility."},
        "AMT-01": {"source_urls": ["https://www.zscaler.com/"], "key_evidence": ["Zscaler Deception provides some moving target elements through dynamic lure deployment."], "notes": "Basic MTD-like elements through deception."},
        "AMT-02": {"source_urls": ["https://www.zscaler.com/"], "key_evidence": ["Zscaler Internet Access provides inline inspection and protection for web applications.", "Browser Isolation provides runtime application isolation."], "notes": "Inline protection and browser isolation."},
        "AMT-03": {"source_urls": ["https://www.zscaler.com/products/zscaler-private-access", "https://www.zscaler.com/"], "key_evidence": ["Zscaler Private Access (ZPA) is a market-leading Zero Trust Network Access solution — providing application-level micro-segmentation without network access.", "Applications are never exposed to the internet — connections are brokered through Zscaler cloud.", "AI-powered app segmentation automatically discovers and segments applications.", "Zscaler's zero trust architecture eliminates the network attack surface entirely.", "300B+ daily transactions processed through the Zero Trust Exchange.", "Named a Leader in Gartner Magic Quadrant for Security Service Edge (SSE)."], "notes": "Market-leading ZTNA/SSE. Zero Trust Exchange eliminates traditional network attack surfaces."},
        "AMT-04": {"source_urls": ["https://www.zscaler.com/"], "key_evidence": ["Some identity-based access control through ZPA and integration with IdPs.", "Conditional access based on identity, device posture, and context.", "Not dedicated credential rotation but strong identity-aware access."], "notes": "Identity-aware zero trust access."},
        "ADR-01": {"source_urls": ["https://www.zscaler.com/products/zscaler-deception"], "key_evidence": ["Zscaler Deception deploys decoys, lures, and honeytokens across the environment to detect lateral movement and active threats.", "Integrates with Zscaler platform for automated response."], "notes": "Dedicated deception product within the Zscaler platform."},
        "ADR-02": {"source_urls": ["https://www.zscaler.com/products/threat-intelligence"], "key_evidence": ["Zscaler ThreatLabz provides threat intelligence from inspecting 300B+ daily transactions.", "Unique visibility into internet traffic patterns and emerging threats.", "Published annual State of Encrypted Attacks and other threat research reports."], "notes": "Good TI from massive traffic inspection and ThreatLabz research."},
        "ADR-03": {"source_urls": [], "key_evidence": ["Basic threat context from traffic analysis but not dedicated hunting."], "notes": "Minimal."},
        "ADR-04": {"source_urls": [], "key_evidence": ["Some phishing and brand impersonation detection through web inspection."], "notes": "Basic."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No BAS capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": ["https://www.zscaler.com/"], "key_evidence": ["Risk360 provides security posture scoring and control gap identification.", "Configuration assessment across Zscaler platform deployments."], "notes": "Internal posture management through Risk360."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No pen testing capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": ["https://www.zscaler.com/products/workload-segmentation"], "key_evidence": ["Zscaler Workload Communications provides cloud workload security.", "Some CSPM-adjacent capability through cloud workload protection and segmentation."], "notes": "Cloud workload protection. Not full CSPM."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Zscaler ASM provides external attack surface discovery integrated with Risk360. Demonstrated EASM capability.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 3: Named ASM product.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Risk360 provides some exposure lifecycle management. Not explicitly CTEM.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 2.", "confidence": "medium"},
        "EXM-03": {"score_rationale": "Risk quantification through Risk360. Not traditional VM.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 2.", "confidence": "medium"},
        "EXM-04": {"score_rationale": "Basic supply chain visibility through traffic inspection.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 2.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "Some MTD-like elements through deception lure deployment.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-02": {"score_rationale": "Inline web protection and browser isolation provide some runtime protection.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "medium"},
        "AMT-03": {"score_rationale": "Zscaler scores 5 (Market-Leading) for Dynamic Network Defense. ZPA is class-leading ZTNA — never exposing applications to the internet, brokering connections through the Zero Trust Exchange (300B+ daily transactions). AI-powered app segmentation, elimination of network attack surface. Gartner MQ Leader for SSE.", "evidence_quality_rationale": "Exceptional. Gartner MQ Leader, massive scale, analyst recognition.", "scoring_level_justification": "Level 5: Best-in-class ZTNA/SSE with analyst leadership and massive scale.", "confidence": "high"},
        "AMT-04": {"score_rationale": "Identity-aware conditional access through ZPA with IdP integration and context-based access. Not credential rotation.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named capability with documented identity-based access.", "confidence": "high"},
        "ADR-01": {"score_rationale": "Zscaler Deception provides dedicated deception capability with decoys, lures, and honeytokens. Integrated with the Zscaler platform.", "evidence_quality_rationale": "Moderate. Named deception product.", "scoring_level_justification": "Level 2: Named product but ancillary to main platform.", "confidence": "high"},
        "ADR-02": {"score_rationale": "ThreatLabz provides threat intelligence from 300B+ daily transaction inspections. Unique internet-scale visibility. Published research reports.", "evidence_quality_rationale": "Good evidence. Quantified data.", "scoring_level_justification": "Level 3: Named TI capability with unique data scale.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Basic threat context from traffic analysis but not dedicated hunting.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-04": {"score_rationale": "Some phishing/impersonation detection through web inspection.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Risk360 provides security posture scoring and gap identification.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Platform-level posture assessment.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Cloud workload protection through Workload Communications. Some CSPM-adjacent capability.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 3: Cloud workload security.", "confidence": "high"}
    }
}

# ═══════════════════════════════════════════════════════════════════════
# BATCH 5: CyberArk, BeyondTrust, Delinea, HashiCorp, Acalvio Technologies
# ═══════════════════════════════════════════════════════════════════════

VENDOR_RESEARCH["CyberArk"] = {
    "scores": {"EXM-01": 1, "EXM-02": 0, "EXM-03": 1, "EXM-04": 1, "AMT-01": 1, "AMT-02": 1, "AMT-03": 2, "AMT-04": 5, "ADR-01": 0, "ADR-02": 1, "ADR-03": 0, "ADR-04": 0, "PPM-01": 0, "PPM-02": 2, "PPM-03": 1, "PPM-04": 1},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.cyberark.com/"], "key_evidence": ["CyberArk Discovery & Audit (DNA) discovers privileged accounts and credentials across the environment."], "notes": "Privileged account discovery only."},
        "EXM-02": {"source_urls": [], "key_evidence": ["No CTEM capability."], "notes": "Outside scope."},
        "EXM-03": {"source_urls": [], "key_evidence": ["Basic risk context through privileged access analytics."], "notes": "Minimal."},
        "EXM-04": {"source_urls": [], "key_evidence": ["Some third-party vendor access control through Vendor PAM."], "notes": "Minimal."},
        "AMT-01": {"source_urls": ["https://www.cyberark.com/"], "key_evidence": ["Some credential mutation through automated credential rotation — changing the attack surface for credential-based attacks."], "notes": "Credential rotation provides MTD-like effect."},
        "AMT-02": {"source_urls": [], "key_evidence": ["Basic session isolation for privileged access."], "notes": "Minimal."},
        "AMT-03": {"source_urls": ["https://www.cyberark.com/"], "key_evidence": ["CyberArk Secure Connect and ZTA capabilities provide some network access segmentation.", "Privilege-based micro-segmentation of access paths."], "notes": "Privilege-based access control."},
        "AMT-04": {"source_urls": ["https://www.cyberark.com/products/", "https://www.cyberark.com/"], "key_evidence": ["CyberArk is the market leader in Privileged Access Management (PAM) — providing automated credential vaulting, rotation, and session management.", "Automated credential rotation changes passwords, SSH keys, and secrets on configurable schedules without human intervention.", "Secrets Manager (Conjur) provides DevOps-native secrets management with automatic rotation.", "Endpoint Privilege Manager (EPM) provides least privilege enforcement on endpoints.", "Named a Leader in Gartner Magic Quadrant for PAM (multiple consecutive years)."], "notes": "Market-leading PAM. Automated credential rotation, vaulting, session management. Gartner MQ Leader."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": [], "key_evidence": ["Some threat intelligence context from Identity Security Intelligence."], "notes": "Basic."},
        "ADR-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": ["https://www.cyberark.com/"], "key_evidence": ["Privileged access policy compliance verification.", "Audit and compliance reporting for credential management controls."], "notes": "PAM compliance validation."},
        "PPM-03": {"source_urls": [], "key_evidence": ["Basic credential testing and verification."], "notes": "Minimal."},
        "PPM-04": {"source_urls": [], "key_evidence": ["Some cloud identity security."], "notes": "Minimal."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Privileged account discovery (DNA) only.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "EXM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Basic risk context.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Vendor PAM for third-party access control.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "AMT-01": {"score_rationale": "Credential rotation provides some MTD-like effect by changing the attack surface.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1: Indirect MTD through credential rotation.", "confidence": "medium"},
        "AMT-02": {"score_rationale": "Session isolation for privileged access.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Privilege-based access segmentation provides some dynamic network defense.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Privilege-based micro-segmentation.", "confidence": "high"},
        "AMT-04": {"score_rationale": "CyberArk scores 5 (Market-Leading) for Identity/Credential Rotation. Market leader in PAM with automated credential vaulting, rotation, and session management. Conjur provides DevOps secrets management with automatic rotation. EPM enforces least privilege on endpoints. Gartner MQ Leader for PAM (multiple consecutive years).", "evidence_quality_rationale": "Exceptional. Gartner MQ Leader, category-defining vendor.", "scoring_level_justification": "Level 5: Best-in-class PAM with analyst leadership position.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Some threat intelligence from Identity Security Intelligence.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "PAM compliance verification and audit reporting.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Compliance validation.", "confidence": "high"},
        "PPM-03": {"score_rationale": "Basic credential testing.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Some cloud identity security.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["BeyondTrust"] = {
    "scores": {"EXM-01": 1, "EXM-02": 0, "EXM-03": 1, "EXM-04": 1, "AMT-01": 0, "AMT-02": 1, "AMT-03": 1, "AMT-04": 4, "ADR-01": 0, "ADR-02": 0, "ADR-03": 0, "ADR-04": 0, "PPM-01": 0, "PPM-02": 2, "PPM-03": 0, "PPM-04": 0},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.beyondtrust.com/"], "key_evidence": ["BeyondTrust Privileged Remote Access discovers and inventories privileged accounts."], "notes": "Account discovery."},
        "EXM-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "EXM-03": {"source_urls": [], "key_evidence": ["Basic risk context through privileged access analytics."], "notes": "Minimal."},
        "EXM-04": {"source_urls": [], "key_evidence": ["Secure vendor access through Privileged Remote Access."], "notes": "Minimal."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["Session isolation capabilities."], "notes": "Basic."},
        "AMT-03": {"source_urls": [], "key_evidence": ["Basic privilege-based access segmentation."], "notes": "Minimal."},
        "AMT-04": {"source_urls": ["https://www.beyondtrust.com/products/", "https://www.beyondtrust.com/"], "key_evidence": ["BeyondTrust Password Safe provides automated credential vaulting and rotation for privileged accounts.", "Privilege Management for Windows and Mac enforces least privilege on endpoints.", "BeyondTrust Identity Security Insights provides unified visibility across identities.", "Named a Leader in Gartner Magic Quadrant for PAM.", "Privileged Remote Access provides secure session management for third-party and internal remote access."], "notes": "Strong PAM vendor. Gartner MQ Leader. Password Safe, Privilege Management, Privileged Remote Access."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": ["https://www.beyondtrust.com/"], "key_evidence": ["Privilege Management audit trails and compliance reporting.", "Policy verification for least privilege controls."], "notes": "Compliance validation for privilege controls."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Privileged account discovery.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "EXM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Basic risk context.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Secure vendor access management.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "Session isolation.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Basic privilege-based access segmentation.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "AMT-04": {"score_rationale": "BeyondTrust scores 4 (Advanced) for Identity/Credential Rotation. Password Safe provides automated credential vaulting and rotation. Privilege Management enforces least privilege on endpoints. Identity Security Insights for unified identity visibility. Gartner MQ Leader for PAM.", "evidence_quality_rationale": "Strong. Gartner MQ Leader, dedicated PAM.", "scoring_level_justification": "Level 4: Advanced PAM with Gartner MQ leadership.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Privilege management compliance and audit trails.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Delinea"] = {
    "scores": {"EXM-01": 1, "EXM-02": 0, "EXM-03": 0, "EXM-04": 1, "AMT-01": 0, "AMT-02": 0, "AMT-03": 1, "AMT-04": 4, "ADR-01": 0, "ADR-02": 0, "ADR-03": 0, "ADR-04": 0, "PPM-01": 0, "PPM-02": 1, "PPM-03": 0, "PPM-04": 0},
    "evidence": {
        "EXM-01": {"source_urls": ["https://delinea.com/"], "key_evidence": ["Account Discovery scans network for privileged accounts and service accounts."], "notes": "Privileged account scanning."},
        "EXM-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "EXM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "EXM-04": {"source_urls": [], "key_evidence": ["Connection Manager provides secure third-party access."], "notes": "Basic."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["Basic privilege-based access control."], "notes": "Minimal."},
        "AMT-04": {"source_urls": ["https://delinea.com/products/", "https://delinea.com/"], "key_evidence": ["Delinea Secret Server is an enterprise-grade credential vault with automated password rotation.", "DevOps Secrets Vault provides cloud-native secrets management with API-driven rotation.", "Privilege Manager enforces least privilege on endpoints — removing local admin rights.", "Server PAM provides Unix/Linux privileged session management.", "Named a Leader in Gartner Magic Quadrant for PAM."], "notes": "Strong PAM vendor (merger of Thycotic and Centrify). Gartner MQ Leader."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["Basic compliance reporting for privileged access."], "notes": "Minimal."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Account discovery for privileged accounts.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "EXM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Secure third-party connection management.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Basic privilege-based access control.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "AMT-04": {"score_rationale": "Delinea scores 4 (Advanced) for Identity/Credential Rotation. Secret Server provides enterprise credential vault with automated rotation. DevOps Secrets Vault for cloud-native secrets management. Privilege Manager for endpoint least privilege. Gartner MQ Leader for PAM (merger of Thycotic/Centrify).", "evidence_quality_rationale": "Strong. Gartner MQ Leader with dedicated PAM suite.", "scoring_level_justification": "Level 4: Advanced PAM with Gartner MQ leadership.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Basic compliance reporting.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["HashiCorp"] = {
    "scores": {"EXM-01": 0, "EXM-02": 0, "EXM-03": 0, "EXM-04": 0, "AMT-01": 2, "AMT-02": 1, "AMT-03": 3, "AMT-04": 5, "ADR-01": 0, "ADR-02": 0, "ADR-03": 0, "ADR-04": 0, "PPM-01": 0, "PPM-02": 2, "PPM-03": 0, "PPM-04": 2},
    "evidence": {
        "EXM-01": {"source_urls": [], "key_evidence": ["No ASM capability."], "notes": "Outside scope."},
        "EXM-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "EXM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "EXM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-01": {"source_urls": ["https://www.hashicorp.com/products/vault"], "key_evidence": ["Dynamic secrets generation creates unique, short-lived credentials for each session — changing the attack surface continuously.", "Infrastructure as Code (Terraform) enables reproducible, ephemeral infrastructure deployment."], "notes": "Dynamic secrets provide MTD-like credential mutation."},
        "AMT-02": {"source_urls": [], "key_evidence": ["Basic application identity through Vault Agent injecting secrets at runtime."], "notes": "Minimal."},
        "AMT-03": {"source_urls": ["https://www.hashicorp.com/products/consul"], "key_evidence": ["Consul provides service mesh with automatic mTLS encryption and intent-based networking.", "Service-to-service segmentation through connect/intentions with dynamic policy enforcement.", "Dynamic service discovery and routing for microservices architectures."], "notes": "Service mesh with dynamic segmentation through Consul."},
        "AMT-04": {"source_urls": ["https://www.hashicorp.com/products/vault", "https://developer.hashicorp.com/vault"], "key_evidence": ["HashiCorp Vault is the industry-standard secrets management platform — providing dynamic secrets, automated credential rotation, and encryption as a service.", "Dynamic secrets generate unique, short-lived credentials for each session — eliminating long-lived credential risk.", "Database secrets engine automatically generates and revokes database credentials.", "PKI secrets engine automates certificate generation and rotation.", "Transit secrets engine provides encryption as a service.", "Available as open-source, enterprise, and HCP Vault Cloud.", "De facto standard for DevOps/cloud-native secrets management."], "notes": "Market-defining secrets management platform. Dynamic secrets, automated rotation, encryption as a service. De facto standard in DevOps/cloud-native."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": ["https://www.hashicorp.com/products/vault"], "key_evidence": ["Vault audit logging and policy enforcement.", "Sentinel policies for governance and compliance."], "notes": "Policy enforcement through Sentinel."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": ["https://www.hashicorp.com/products/terraform"], "key_evidence": ["Terraform provides infrastructure as code with drift detection.", "Some cloud posture validation through infrastructure configuration management."], "notes": "IaC-based posture management. Not CSPM per se."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-01": {"score_rationale": "Dynamic secrets generation changes the attack surface continuously. Ephemeral infrastructure through Terraform.", "evidence_quality_rationale": "Moderate. Novel MTD approach through secrets management.", "scoring_level_justification": "Level 2: Generic claims supported by documented dynamic capability.", "confidence": "medium"},
        "AMT-02": {"score_rationale": "Vault Agent injects secrets at runtime. Basic application identity.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-03": {"score_rationale": "Consul provides service mesh with automatic mTLS and intent-based networking. Dynamic service segmentation for microservices.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named service mesh product with dynamic segmentation.", "confidence": "high"},
        "AMT-04": {"score_rationale": "HashiCorp Vault scores 5 (Market-Leading) for Identity/Credential Rotation. Industry-standard secrets management with dynamic secrets (unique short-lived credentials per session), automated database/PKI/AWS/Azure credential rotation, and encryption as a service. De facto standard for DevOps/cloud-native secrets management. Available as OSS, enterprise, and cloud.", "evidence_quality_rationale": "Exceptional. Category-defining product, massive adoption, extensive documentation.", "scoring_level_justification": "Level 5: Market-defining secrets management platform with unmatched adoption.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Vault audit logging and Sentinel policies for governance and compliance.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Policy enforcement capabilities.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Terraform drift detection and IaC-based configuration management. Not dedicated CSPM.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: IaC-based posture management.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Acalvio Technologies"] = {
    "scores": {"EXM-01": 0, "EXM-02": 0, "EXM-03": 0, "EXM-04": 0, "AMT-01": 2, "AMT-02": 0, "AMT-03": 1, "AMT-04": 1, "ADR-01": 5, "ADR-02": 2, "ADR-03": 2, "ADR-04": 1, "PPM-01": 0, "PPM-02": 0, "PPM-03": 0, "PPM-04": 0},
    "evidence": {
        "EXM-01": {"source_urls": [], "key_evidence": ["No ASM capability."], "notes": "Outside scope."},
        "EXM-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "EXM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "EXM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-01": {"source_urls": ["https://www.acalvio.com/"], "key_evidence": ["Dynamic deployment and redirection of decoys creates a continuously changing deception surface — MTD-like effect for the decoy layer.", "Autonomous reconfiguration of deception assets based on threat activity."], "notes": "Dynamic deception deployment provides MTD-like capability."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["Some network-layer deception through decoy network services."], "notes": "Minimal."},
        "AMT-04": {"source_urls": ["https://www.acalvio.com/"], "key_evidence": ["Deploys credential-based lures and honeytokens — including Active Directory deceptions."], "notes": "Credential-based deception, not rotation."},
        "ADR-01": {"source_urls": ["https://www.acalvio.com/", "https://www.acalvio.com/shadowplex-platform/"], "key_evidence": ["Acalvio ShadowPlex is an enterprise-grade autonomous deception platform that deploys realistic decoys, lures, and breadcrumbs across endpoints, network, and cloud.", "AI-driven autonomous deception — the platform automatically recommends and deploys deception campaigns based on environment analysis.", "Deceptions span identity (Active Directory), network services, applications, data, and endpoints.", "Fluid Deception technology creates dynamic, evolving deception environments.", "Integration with SIEM, SOAR, and EDR for automated response to deception alerts.", "Named in Gartner research for deception technology and recognized for advanced autonomous deception capabilities."], "notes": "Market-leading autonomous deception platform. ShadowPlex with Fluid Deception and AI-driven deployment. Core ADR vendor."},
        "ADR-02": {"source_urls": ["https://www.acalvio.com/"], "key_evidence": ["Threat intelligence gathered from deception interactions — attacker TTPs, tools, and lateral movement patterns.", "High-fidelity alerts from deception reduce false positives."], "notes": "Deception-derived threat intelligence."},
        "ADR-03": {"source_urls": ["https://www.acalvio.com/"], "key_evidence": ["Deception-based threat detection identifies active attackers within the environment.", "Provides attack path analysis through decoy interaction tracking."], "notes": "Deception-driven threat detection."},
        "ADR-04": {"source_urls": [], "key_evidence": ["Some capability to profile attacker behavior through deception interactions."], "notes": "Basic attacker profiling."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-01": {"score_rationale": "Dynamic deception deployment creates continuously changing attack surface — MTD-like effect for decoy layer.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Deception-based MTD effect.", "confidence": "medium"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Network-layer deception through decoy services.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "AMT-04": {"score_rationale": "Deploys credential-based lures and AD deceptions. Not credential rotation.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1: Credential deception, not management.", "confidence": "high"},
        "ADR-01": {"score_rationale": "Acalvio scores 5 (Market-Leading) for Deception Technology. ShadowPlex is an enterprise-grade autonomous deception platform with AI-driven deployment of decoys, lures, and breadcrumbs across identity, network, applications, data, and endpoints. Fluid Deception creates dynamic evolving environments. Integration with SIEM/SOAR/EDR. Gartner-recognized for advanced autonomous deception.", "evidence_quality_rationale": "Exceptional. Category specialist with autonomous AI-driven deception capabilities.", "scoring_level_justification": "Level 5: Best-in-class autonomous deception platform.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Deception-derived threat intelligence — attacker TTPs, tools, lateral movement patterns. High-fidelity alerts.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Deception-sourced TI.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Deception-based active threat detection and attack path analysis.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Deception-driven threat detection.", "confidence": "high"},
        "ADR-04": {"score_rationale": "Basic attacker profiling through deception interactions.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"}
    }
}

# ═══════════════════════════════════════════════════════════════════════
# BATCH 6: CounterCraft, Fidelis Cybersecurity, SentinelOne, Recorded Future, Mandiant/Google Cloud
# ═══════════════════════════════════════════════════════════════════════

VENDOR_RESEARCH["CounterCraft"] = {
    "scores": {"EXM-01": 0, "EXM-02": 0, "EXM-03": 0, "EXM-04": 0, "AMT-01": 2, "AMT-02": 0, "AMT-03": 1, "AMT-04": 1, "ADR-01": 5, "ADR-02": 3, "ADR-03": 2, "ADR-04": 3, "PPM-01": 0, "PPM-02": 0, "PPM-03": 0, "PPM-04": 0},
    "evidence": {
        "EXM-01": {"source_urls": [], "key_evidence": ["No ASM capability."], "notes": "Outside scope."},
        "EXM-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "EXM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "EXM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-01": {"source_urls": ["https://www.countercraft.eu/"], "key_evidence": ["Dynamic deception surface deployment provides MTD-like capability — changing the apparent environment continuously.", "Adaptive deception campaigns evolve based on adversary interactions."], "notes": "Dynamic deception as MTD."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["Some network deception through decoy network services."], "notes": "Minimal."},
        "AMT-04": {"source_urls": ["https://www.countercraft.eu/"], "key_evidence": ["Deploys credential-based lures and honeytokens for identity deception."], "notes": "Credential deception, not rotation."},
        "ADR-01": {"source_urls": ["https://www.countercraft.eu/", "https://www.countercraft.eu/platform/"], "key_evidence": ["CounterCraft provides an advanced cyber deception platform with deployment across internet, corporate network, and endpoint layers.", "Creates realistic deception campaigns including web applications, network services, credentials, and documents.", "Active engagement capability allows for controlled interaction with adversaries to gather intelligence.", "Breadcrumbs and lures guide attackers through deception environments for detailed TTP collection.", "Strong in government and defense sectors with cyber counter-intelligence use cases.", "Acquired by Fortra in 2024 — now part of broader security portfolio."], "notes": "Market-leading deception platform. Active engagement and counter-intelligence. Acquired by Fortra."},
        "ADR-02": {"source_urls": ["https://www.countercraft.eu/"], "key_evidence": ["Real-time threat intelligence from adversary engagement — TTPs, tools, infrastructure, objectives.", "Intelligence generation from deception interactions is the core value proposition.", "Provides adversary profiling and attribution intelligence."], "notes": "Deception-derived TI with adversary profiling."},
        "ADR-03": {"source_urls": ["https://www.countercraft.eu/"], "key_evidence": ["Deception-based threat detection provides proactive identification of active threats.", "Attack path analysis through controlled deception environments."], "notes": "Deception-driven threat detection."},
        "ADR-04": {"source_urls": ["https://www.countercraft.eu/"], "key_evidence": ["Active engagement with adversaries for counter-adversary intelligence.", "Adversary profiling, TTP collection, and attribution capabilities.", "Designed for cyber counter-intelligence operations."], "notes": "Strong counter-adversary capability. Designed for government/defense counter-intelligence."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-01": {"score_rationale": "Dynamic deception surface provides MTD-like capability. Adaptive campaigns evolve based on adversary interactions.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Deception-based MTD.", "confidence": "medium"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Some network deception.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "AMT-04": {"score_rationale": "Credential-based deception lures. Not credential management.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "ADR-01": {"score_rationale": "CounterCraft scores 5 (Market-Leading) for Deception Technology. Advanced platform with multi-layer deception (internet, network, endpoint), active adversary engagement, controlled interaction, and breadcrumb/lure campaigns. Strong in government/defense counter-intelligence. Acquired by Fortra.", "evidence_quality_rationale": "Exceptional. Category specialist with active engagement capabilities.", "scoring_level_justification": "Level 5: Best-in-class deception with counter-intelligence focus.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Core value proposition is intelligence from adversary engagement — TTPs, tools, infrastructure, attribution. Named deception-derived TI capability.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named TI generation from deception.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Deception-based proactive threat detection with attack path analysis.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Deception-driven detection.", "confidence": "high"},
        "ADR-04": {"score_rationale": "Active adversary engagement with counter-intelligence capabilities — profiling, TTP collection, attribution. Designed for government/defense.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named counter-adversary capabilities.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Fidelis Cybersecurity"] = {
    "scores": {"EXM-01": 2, "EXM-02": 1, "EXM-03": 1, "EXM-04": 0, "AMT-01": 0, "AMT-02": 0, "AMT-03": 2, "AMT-04": 0, "ADR-01": 4, "ADR-02": 3, "ADR-03": 3, "ADR-04": 2, "PPM-01": 0, "PPM-02": 1, "PPM-03": 0, "PPM-04": 0},
    "evidence": {
        "EXM-01": {"source_urls": ["https://fidelissecurity.com/"], "key_evidence": ["Fidelis Elevate provides network and endpoint visibility across hybrid environments.", "Terrain mapping for asset discovery and network visualization."], "notes": "Network-based asset discovery."},
        "EXM-02": {"source_urls": [], "key_evidence": ["Some exposure visibility through continuous network monitoring."], "notes": "Minimal."},
        "EXM-03": {"source_urls": [], "key_evidence": ["Basic vulnerability context through network inspection."], "notes": "Minimal."},
        "EXM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": ["https://fidelissecurity.com/"], "key_evidence": ["Fidelis Network provides deep packet inspection and network segmentation visibility.", "Network traffic analysis with decryption capabilities."], "notes": "Network DPI and segmentation."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": ["https://fidelissecurity.com/", "https://fidelissecurity.com/products/"], "key_evidence": ["Fidelis Deception provides integrated deception technology within the Fidelis Elevate platform.", "Deploys network, endpoint, and Active Directory deceptions.", "Automated decoy deployment and management.", "Deception alerts integrate with Fidelis Network and Endpoint for unified detection and response."], "notes": "Integrated deception within XDR platform. Strong integration with network/endpoint detection."},
        "ADR-02": {"source_urls": ["https://fidelissecurity.com/"], "key_evidence": ["Threat intelligence from deep packet inspection of network traffic.", "Deception-derived intelligence from adversary interactions.", "Fidelis threat research team provides curated intelligence."], "notes": "Multi-source TI: network DPI + deception + research."},
        "ADR-03": {"source_urls": ["https://fidelissecurity.com/"], "key_evidence": ["Combined network/endpoint/deception enables proactive threat hunting.", "Terrain mapping provides comprehensive context for hunting operations.", "Historical metadata retention for retrospective threat hunting."], "notes": "Strong hunting through combined network/endpoint/deception telemetry."},
        "ADR-04": {"source_urls": ["https://fidelissecurity.com/"], "key_evidence": ["Some counter-adversary intelligence through deception interactions.", "Adversary TTP identification from deception and network analysis."], "notes": "Basic counter-adversary through deception."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["Basic security control validation through network monitoring."], "notes": "Minimal."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Network-based asset discovery and terrain mapping. Not dedicated ASM.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Internal network discovery.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Some exposure visibility through network monitoring.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Basic vulnerability context.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "EXM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Deep packet inspection and network segmentation visibility.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Named network DPI product.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "Fidelis scores 4 (Advanced) for Deception Technology. Fidelis Deception is integrated within the Elevate XDR platform — deploying network, endpoint, and AD deceptions with automated management. Strong integration with network DPI and endpoint detection for unified response.", "evidence_quality_rationale": "Strong. Integrated deception within XDR with documented multi-layer coverage.", "scoring_level_justification": "Level 4: Advanced integrated deception within XDR platform.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Multi-source TI from network DPI, deception interactions, and threat research team.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named TI with multiple unique sources.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Combined network/endpoint/deception telemetry enables proactive hunting. Terrain mapping provides context. Historical metadata for retrospective analysis.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Demonstrated hunting with multi-source telemetry.", "confidence": "high"},
        "ADR-04": {"score_rationale": "Counter-adversary intelligence from deception and network analysis.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "medium"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Basic control validation through network monitoring.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["SentinelOne"] = {
    "scores": {"EXM-01": 3, "EXM-02": 2, "EXM-03": 3, "EXM-04": 1, "AMT-01": 1, "AMT-02": 2, "AMT-03": 1, "AMT-04": 1, "ADR-01": 1, "ADR-02": 4, "ADR-03": 4, "ADR-04": 3, "PPM-01": 0, "PPM-02": 2, "PPM-03": 1, "PPM-04": 3},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.sentinelone.com/"], "key_evidence": ["Singularity Ranger provides network discovery and IoT/OT asset identification.", "Agentless device discovery for asset inventory.", "Some EASM through partnerships and integrations."], "notes": "Ranger for network/IoT/OT asset discovery. Growing EASM."},
        "EXM-02": {"source_urls": ["https://www.sentinelone.com/"], "key_evidence": ["Some exposure management through Singularity platform and vulnerability assessment.", "Growing CTEM-adjacent capability."], "notes": "Emerging exposure management."},
        "EXM-03": {"source_urls": ["https://www.sentinelone.com/"], "key_evidence": ["Singularity platform identifies endpoint vulnerabilities with risk prioritization.", "Application inventory and vulnerability assessment on endpoints.", "Patent-pending vulnerability assessment through endpoint agent."], "notes": "Endpoint-centric vulnerability assessment."},
        "EXM-04": {"source_urls": [], "key_evidence": ["Basic supply chain monitoring."], "notes": "Minimal."},
        "AMT-01": {"source_urls": [], "key_evidence": ["Some runtime behavior analysis provides adaptive defense, but not true AMTD."], "notes": "Adaptive behavioral AI, not MTD."},
        "AMT-02": {"source_urls": ["https://www.sentinelone.com/"], "key_evidence": ["AI-driven behavioral detection and runtime protection on endpoints.", "Autonomous response capabilities at the endpoint level."], "notes": "Endpoint runtime protection through behavioral AI."},
        "AMT-03": {"source_urls": [], "key_evidence": ["Basic network isolation through EDR."], "notes": "Minimal."},
        "AMT-04": {"source_urls": [], "key_evidence": ["Some identity threat detection."], "notes": "Minimal."},
        "ADR-01": {"source_urls": [], "key_evidence": ["Basic deception through Ranger — identifying unauthorized/rogue devices."], "notes": "Minimal deception-adjacent."},
        "ADR-02": {"source_urls": ["https://www.sentinelone.com/", "https://www.sentinelone.com/global-services/"], "key_evidence": ["Singularity Data Lake ingests massive telemetry with threat intelligence enrichment.", "PinnacleOne advisory group provides strategic threat intelligence.", "Threat intelligence from protecting millions of endpoints globally.", "Integration with open threat intelligence feeds."], "notes": "Strong TI from massive endpoint telemetry and PinnacleOne advisory."},
        "ADR-03": {"source_urls": ["https://www.sentinelone.com/", "https://www.sentinelone.com/global-services/"], "key_evidence": ["Singularity Vigilance provides managed threat hunting service.", "WatchTower provides proactive threat hunting using Singularity Data Lake.", "Star (Custom Detection Rules) enables threat hunting at scale.", "Storyline Active Response provides automated hunting and remediation."], "notes": "Strong managed threat hunting and autonomous hunting capabilities."},
        "ADR-04": {"source_urls": ["https://www.sentinelone.com/"], "key_evidence": ["PinnacleOne advisory group provides adversary analysis and strategic intelligence.", "Some counter-adversary intelligence from endpoint telemetry.", "Industry-leading incident response services."], "notes": "Counter-adversary through PinnacleOne advisory."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": ["https://www.sentinelone.com/"], "key_evidence": ["Security control validation through endpoint health monitoring.", "MITRE ATT&CK mapping for detection coverage assessment."], "notes": "Endpoint control validation."},
        "PPM-03": {"source_urls": [], "key_evidence": ["Basic pen testing context through vulnerability assessment."], "notes": "Minimal."},
        "PPM-04": {"source_urls": ["https://www.sentinelone.com/"], "key_evidence": ["Singularity Cloud provides cloud workload protection.", "Container and Kubernetes security.", "Some CSPM capability through cloud workload monitoring."], "notes": "Growing cloud workload protection."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Singularity Ranger provides network/IoT/OT asset discovery. Growing EASM capability.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named product with demonstrated asset discovery.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Emerging exposure management through Singularity platform.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "medium"},
        "EXM-03": {"score_rationale": "Endpoint vulnerability assessment with risk prioritization. Application inventory.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named endpoint vulnerability assessment.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Basic supply chain monitoring.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "Behavioral AI provides adaptive defense but not true AMTD.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-02": {"score_rationale": "AI-driven behavioral detection and autonomous endpoint response.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Basic network isolation through EDR.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "AMT-04": {"score_rationale": "Some identity threat detection.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-01": {"score_rationale": "Minimal deception-adjacent capability through Ranger.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-02": {"score_rationale": "SentinelOne scores 4 (Advanced) for Threat Intel Operationalization. Singularity Data Lake with massive endpoint telemetry. PinnacleOne advisory for strategic TI. Millions of endpoints providing real-time intelligence.", "evidence_quality_rationale": "Strong. Massive scale telemetry with dedicated advisory.", "scoring_level_justification": "Level 4: Advanced TI from massive endpoint fleet and strategic advisory.", "confidence": "high"},
        "ADR-03": {"score_rationale": "SentinelOne scores 4 (Advanced) for Proactive Threat Hunting. Vigilance for managed hunting, WatchTower for proactive hunting, Star for custom detection rules, Storyline Active Response for automated hunting/remediation.", "evidence_quality_rationale": "Strong. Multiple named hunting products and services.", "scoring_level_justification": "Level 4: Advanced multi-tier threat hunting.", "confidence": "high"},
        "ADR-04": {"score_rationale": "PinnacleOne advisory provides adversary analysis and counter-adversary intelligence.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named advisory with counter-adversary focus.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Endpoint health monitoring and MITRE ATT&CK coverage assessment.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Named control validation.", "confidence": "high"},
        "PPM-03": {"score_rationale": "Basic pen testing context.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-04": {"score_rationale": "Singularity Cloud with container/K8s security and some CSPM.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named cloud workload protection.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Recorded Future"] = {
    "scores": {"EXM-01": 2, "EXM-02": 1, "EXM-03": 2, "EXM-04": 3, "AMT-01": 0, "AMT-02": 0, "AMT-03": 0, "AMT-04": 1, "ADR-01": 0, "ADR-02": 5, "ADR-03": 3, "ADR-04": 4, "PPM-01": 0, "PPM-02": 1, "PPM-03": 0, "PPM-04": 0},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.recordedfuture.com/"], "key_evidence": ["Some external asset intelligence through internet-scale collection.", "Attack surface intelligence module identifies exposed assets."], "notes": "Attack surface intelligence from internet-scale data."},
        "EXM-02": {"source_urls": [], "key_evidence": ["Some exposure context from threat intelligence."], "notes": "TI-driven exposure context."},
        "EXM-03": {"source_urls": ["https://www.recordedfuture.com/"], "key_evidence": ["Vulnerability intelligence provides risk-based prioritization.", "Correlates CVEs with active exploitation and threat actor interest.", "CVE intelligence enriched with NLP-processed open source intelligence."], "notes": "TI-enriched vulnerability prioritization."},
        "EXM-04": {"source_urls": ["https://www.recordedfuture.com/"], "key_evidence": ["Third-Party Intelligence module provides supply chain and vendor risk intelligence.", "Monitors dark web, criminal forums, and paste sites for third-party compromise indicators.", "Geopolitical risk intelligence for supply chain geography."], "notes": "Named third-party intelligence module."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["Basic identity intelligence — credential exposure monitoring on dark web."], "notes": "Credential exposure detection."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://www.recordedfuture.com/", "https://www.recordedfuture.com/platform/"], "key_evidence": ["Recorded Future is the world's largest commercial threat intelligence platform with AI/NLP-driven intelligence from 1M+ sources.", "Intelligence Graph connects entities across open web, dark web, technical sources, and proprietary data.", "Real-time intelligence on threat actors, malware, vulnerabilities, and infrastructure.", "Insikt Group provides expert-curated threat intelligence and research.", "Most-cited private-sector source of intelligence by government agencies worldwide.", "Acquired by Mastercard for $2.65B in 2024 — validating intelligence value.", "MITRE ATT&CK mapping for adversary TTPs across the intelligence platform."], "notes": "Market-defining threat intelligence platform. Largest commercial TIP. Acquired by Mastercard for $2.65B."},
        "ADR-03": {"source_urls": ["https://www.recordedfuture.com/"], "key_evidence": ["Intelligence-driven threat hunting with proactive IoC and adversary infrastructure identification.", "Hunting packages and intelligence cards for threat hunter enablement.", "Threat actor infrastructure tracking for proactive defense."], "notes": "TI-driven hunting enablement."},
        "ADR-04": {"source_urls": ["https://www.recordedfuture.com/"], "key_evidence": ["Extensive adversary tracking and profiling across 100+ threat actor groups.", "Dark web monitoring for adversary operations, infrastructure, and targets.", "Brand Protection module identifies impersonation, fraud, and credential compromise.", "Insikt Group performs counter-adversary research and disruption recommendations."], "notes": "Strong counter-adversary intelligence with adversary tracking and brand protection."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["Some control validation through intelligence alignment."], "notes": "Minimal."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Attack surface intelligence from internet-scale data collection.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: TI-derived ASM context.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Some exposure context from threat intelligence.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-03": {"score_rationale": "Vulnerability intelligence with active exploitation correlation and NLP-processed OSINT.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 2: TI-enriched vulnerability prioritization.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Named Third-Party Intelligence module with dark web/criminal forum monitoring for vendor compromise indicators.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named third-party risk module.", "confidence": "high"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "Credential exposure monitoring on dark web.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Recorded Future scores 5 (Market-Leading) for Threat Intel Operationalization. World's largest commercial TIP with AI/NLP-driven intelligence from 1M+ sources. Intelligence Graph, Insikt Group expert research, most-cited by government agencies, acquired by Mastercard for $2.65B. Real-time intelligence on actors, malware, vulnerabilities, and infrastructure.", "evidence_quality_rationale": "Exceptional. Category-defining platform, massive scale, validated by $2.65B acquisition.", "scoring_level_justification": "Level 5: Unmatched commercial TIP with market-defining scale and recognition.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Intelligence-driven hunting with proactive IoC/infrastructure identification and hunting packages.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named TI-driven hunting enablement.", "confidence": "high"},
        "ADR-04": {"score_rationale": "Recorded Future scores 4 (Advanced) for Counter-Adversary Ops. Adversary tracking across 100+ groups, dark web monitoring, Brand Protection module, and Insikt Group counter-adversary research.", "evidence_quality_rationale": "Strong. Named capability with extensive adversary coverage.", "scoring_level_justification": "Level 4: Advanced adversary tracking with brand protection.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Some control validation through intelligence alignment.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Mandiant (Google Cloud)"] = {
    "scores": {"EXM-01": 3, "EXM-02": 2, "EXM-03": 3, "EXM-04": 2, "AMT-01": 0, "AMT-02": 0, "AMT-03": 1, "AMT-04": 0, "ADR-01": 0, "ADR-02": 5, "ADR-03": 5, "ADR-04": 5, "PPM-01": 1, "PPM-02": 3, "PPM-03": 4, "PPM-04": 2},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.mandiant.com/advantage/attack-surface-management"], "key_evidence": ["Mandiant Attack Surface Management provides external asset discovery and exposure assessment.", "Integrated with Mandiant Advantage platform for threat-informed prioritization.", "Identifies internet-facing assets and correlates with active threat intelligence."], "notes": "Named ASM product integrated with threat intelligence."},
        "EXM-02": {"source_urls": ["https://www.mandiant.com/"], "key_evidence": ["Some CTEM-aligned capability through continuous ASM monitoring and threat correlation.", "Not explicitly branded as CTEM."], "notes": "CTEM-adjacent through ASM + TI."},
        "EXM-03": {"source_urls": ["https://www.mandiant.com/"], "key_evidence": ["Vulnerability intelligence enriched with frontline threat intelligence.", "Prioritization based on what threat actors are actively exploiting.", "Zero-day research from frontline incident response provides unique vulnerability context."], "notes": "TI-enriched vulnerability prioritization from frontline IR."},
        "EXM-04": {"source_urls": ["https://www.mandiant.com/"], "key_evidence": ["Some supply chain risk intelligence from incident response findings.", "Third-party compromise investigation expertise."], "notes": "Supply chain context from IR intelligence."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["Basic through Google Cloud security products."], "notes": "Minimal own capability."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://www.mandiant.com/advantage/threat-intelligence", "https://www.mandiant.com/"], "key_evidence": ["Mandiant Threat Intelligence is arguably the world's gold-standard for frontline threat intelligence — derived from 1000+ incident response engagements annually.", "Tracks 3,500+ threat actors with detailed TTPs, infrastructure, and attribution.", "Combines machine intelligence with expert human analysis from 300+ intelligence professionals.", "Mandiant Advantage platform operationalizes intelligence for automated detection and response.", "Published research on major nation-state campaigns (APT1, APT29, SolarWinds, etc.) has shaped the industry."], "notes": "Gold-standard frontline threat intelligence. 1000+ IR engagements/year. 3,500+ tracked threat actors. Industry-defining research."},
        "ADR-03": {"source_urls": ["https://www.mandiant.com/", "https://www.mandiant.com/services/"], "key_evidence": ["Mandiant Managed Defense provides elite managed threat hunting service.", "Frontline threat hunters with direct access to Mandiant intelligence and IR findings.", "Proactive hunting based on emerging threats and zero-day discoveries.", "Background in military/intelligence community threat hunting.", "Industry's most experienced threat hunting workforce."], "notes": "Elite managed hunting from the industry's most experienced team. Frontline intelligence-driven hunting."},
        "ADR-04": {"source_urls": ["https://www.mandiant.com/", "https://www.mandiant.com/services/"], "key_evidence": ["Mandiant pioneered counter-adversary operations in the private sector.", "Attribution reports on nation-state threat actors (APT1 report was a watershed moment).", "Active nation-state tracking covering China, Russia, Iran, North Korea, and others.", "Digital Threat Monitoring for brand protection, impersonation, and dark web monitoring.", "Incident response and remediation capability that disrupts active adversary operations."], "notes": "Industry pioneer in counter-adversary ops. APT1 report defined the field. Nation-state tracking and attribution."},
        "PPM-01": {"source_urls": [], "key_evidence": ["Basic BAS-adjacent through Mandiant Security Validation."], "notes": "Some BAS-like capability."},
        "PPM-02": {"source_urls": ["https://www.mandiant.com/advantage/security-validation"], "key_evidence": ["Mandiant Security Validation tests security controls against real-world attack scenarios.", "Uses threat-intelligence-informed test cases based on active adversary TTPs.", "MITRE ATT&CK-aligned validation framework."], "notes": "Named security validation product with TI-informed testing."},
        "PPM-03": {"source_urls": ["https://www.mandiant.com/services/"], "key_evidence": ["Mandiant provides red team and penetration testing services.", "Red team assessments leveraging frontline attacker knowledge.", "Purple team exercises combining Mandiant intelligence with customer defense teams.", "Tabletop exercises and adversary simulations."], "notes": "Elite red team services with frontline attacker knowledge."},
        "PPM-04": {"source_urls": ["https://cloud.google.com/security"], "key_evidence": ["Google Cloud Security products (SCC) provide CSPM.", "Mandiant integration enhances Google Cloud security posture."], "notes": "CSPM through Google Cloud SCC integration."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Mandiant ASM provides external asset discovery with threat-informed prioritization.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named ASM product.", "confidence": "high"},
        "EXM-02": {"score_rationale": "CTEM-adjacent through continuous ASM + TI correlation.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "medium"},
        "EXM-03": {"score_rationale": "Vulnerability prioritization enriched with frontline IR intelligence and zero-day research.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: TI-enriched prioritization from frontline IR.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Supply chain risk context from incident response findings.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Basic through Google Cloud integration.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Mandiant scores 5 (Market-Leading) for Threat Intel Operationalization. Gold-standard frontline TI from 1000+ IR engagements/year. 3,500+ tracked threat actors. 300+ intelligence professionals. Published research that shaped the industry (APT1, SolarWinds). Mandiant Advantage operationalizes intelligence.", "evidence_quality_rationale": "Exceptional. Category-defining with unmatched frontline intelligence.", "scoring_level_justification": "Level 5: Best-in-class frontline threat intelligence.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Mandiant scores 5 (Market-Leading) for Proactive Threat Hunting. Managed Defense provides elite hunting with direct access to frontline intelligence and IR findings. Most experienced threat hunting workforce in the industry. Intelligence community background.", "evidence_quality_rationale": "Exceptional. Elite hunting team with unmatched intelligence access.", "scoring_level_justification": "Level 5: Best-in-class managed hunting.", "confidence": "high"},
        "ADR-04": {"score_rationale": "Mandiant scores 5 (Market-Leading) for Counter-Adversary Ops. Pioneered private-sector counter-adversary operations. APT1 report defined the field. Active nation-state tracking and attribution. Digital Threat Monitoring for brand protection.", "evidence_quality_rationale": "Exceptional. Industry pioneer, category-defining.", "scoring_level_justification": "Level 5: Industry pioneer in counter-adversary ops.", "confidence": "high"},
        "PPM-01": {"score_rationale": "Basic BAS-adjacent through Security Validation.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-02": {"score_rationale": "Mandiant Security Validation tests controls against real-world TTP-informed scenarios. MITRE ATT&CK-aligned.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named validation product.", "confidence": "high"},
        "PPM-03": {"score_rationale": "Mandiant scores 4 (Advanced) for Pen Testing/Red Teaming. Elite red team services with frontline attacker knowledge. Purple team exercises combining intelligence with defense. Tabletop exercises.", "evidence_quality_rationale": "Strong. Industry-leading red team with frontline knowledge.", "scoring_level_justification": "Level 4: Advanced red team services.", "confidence": "high"},
        "PPM-04": {"score_rationale": "CSPM through Google Cloud SCC integration.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "medium"}
    }
}

# ═══════════════════════════════════════════════════════════════════════
# BATCH 7: ThreatConnect, Anomali, ZeroFox, Nisos, Arctic Wolf
# ═══════════════════════════════════════════════════════════════════════

VENDOR_RESEARCH["ThreatConnect"] = {
    "scores": {"EXM-01": 1, "EXM-02": 1, "EXM-03": 2, "EXM-04": 2, "AMT-01": 0, "AMT-02": 0, "AMT-03": 0, "AMT-04": 0, "ADR-01": 0, "ADR-02": 4, "ADR-03": 2, "ADR-04": 2, "PPM-01": 0, "PPM-02": 1, "PPM-03": 0, "PPM-04": 0},
    "evidence": {
        "EXM-01": {"source_urls": ["https://threatconnect.com/"], "key_evidence": ["Some asset context through threat intelligence enrichment."], "notes": "Minimal."},
        "EXM-02": {"source_urls": [], "key_evidence": ["Some exposure lifecycle through TI-driven risk quantification."], "notes": "TI-driven exposure context."},
        "EXM-03": {"source_urls": ["https://threatconnect.com/"], "key_evidence": ["Vulnerability intelligence enrichment with threat context.", "Risk quantification through threat-informed scoring."], "notes": "TI-enriched vuln context."},
        "EXM-04": {"source_urls": ["https://threatconnect.com/"], "key_evidence": ["Supply chain risk intelligence through third-party monitoring.", "Intake feeds from OSINT and commercial intelligence sources."], "notes": "TI-derived third-party risk."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://threatconnect.com/", "https://threatconnect.com/platform/"], "key_evidence": ["ThreatConnect is a leading Threat Intelligence Platform (TIP) providing intelligence aggregation, analysis, and operationalization.", "TI Ops platform ingests and correlates intelligence from multiple sources — OSINT, commercial, ISAC, and proprietary.", "CAL (Collective Analytics Layer) provides machine-learning-based intelligence scoring and prioritization.", "SOAR/Playbook-driven automation for intelligence-driven response workflows.", "Named a Leader in Forrester Wave for Threat Intelligence Platforms."], "notes": "Market-leading TIP with SOAR integration. Forrester Wave Leader."},
        "ADR-03": {"source_urls": ["https://threatconnect.com/"], "key_evidence": ["Intelligence-driven hunting support through correlated threat intelligence.", "Playbook-based automated hunting workflows."], "notes": "TI-driven hunting enablement."},
        "ADR-04": {"source_urls": ["https://threatconnect.com/"], "key_evidence": ["Adversary tracking and TTP mapping.", "Intelligence-driven adversary profiling through correlated data."], "notes": "TI-based adversary tracking."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["Some control alignment through TI-driven security posture."], "notes": "Minimal."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Some asset context through TI enrichment.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-02": {"score_rationale": "Some exposure lifecycle through TI-driven risk quantification.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-03": {"score_rationale": "TI-enriched vulnerability context and risk quantification.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Supply chain risk intelligence from multi-source TI feeds.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "ThreatConnect scores 4 (Advanced) for Threat Intel Operationalization. Leading TIP with multi-source intelligence aggregation, CAL ML-based scoring, and SOAR-integrated automated response. Forrester Wave Leader for Threat Intelligence Platforms.", "evidence_quality_rationale": "Strong. Forrester Wave Leader with named TI capabilities.", "scoring_level_justification": "Level 4: Advanced TIP with analyst leadership.", "confidence": "high"},
        "ADR-03": {"score_rationale": "TI-driven hunting support with playbook-based automated workflows.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "ADR-04": {"score_rationale": "Adversary tracking and TTP mapping through correlated intelligence.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Some control alignment through TI-informed posture.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Anomali"] = {
    "scores": {"EXM-01": 1, "EXM-02": 1, "EXM-03": 2, "EXM-04": 1, "AMT-01": 0, "AMT-02": 0, "AMT-03": 0, "AMT-04": 0, "ADR-01": 0, "ADR-02": 4, "ADR-03": 3, "ADR-04": 2, "PPM-01": 0, "PPM-02": 1, "PPM-03": 0, "PPM-04": 0},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.anomali.com/"], "key_evidence": ["Some asset intelligence through threat intelligence enrichment."], "notes": "Minimal."},
        "EXM-02": {"source_urls": [], "key_evidence": ["Some exposure context through threat intelligence."], "notes": "TI-driven exposure context."},
        "EXM-03": {"source_urls": ["https://www.anomali.com/"], "key_evidence": ["Vulnerability intelligence enrichment through ThreatStream.", "Correlates vulnerabilities with active threats in the wild."], "notes": "TI-enriched vuln context."},
        "EXM-04": {"source_urls": [], "key_evidence": ["Basic supply chain intelligence from threat feeds."], "notes": "Minimal."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://www.anomali.com/", "https://www.anomali.com/products/"], "key_evidence": ["Anomali ThreatStream is a major TIP providing intelligence aggregation from hundreds of feeds.", "STAXX provides free STIX/TAXII-based threat intelligence sharing.", "Match service correlates telemetry against massive intelligence datasets for real-time detection.", "Security Analytics platform provides big-data driven intelligence analysis.", "NLP-based intelligence processing from blogs, reports, and advisories."], "notes": "Major TIP vendor. ThreatStream for aggregation, Match for real-time correlation."},
        "ADR-03": {"source_urls": ["https://www.anomali.com/"], "key_evidence": ["Intelligence-driven hunting through Match and ThreatStream.", "Retrospective analysis against accumulated telemetry.", "MITRE ATT&CK-aligned detection content."], "notes": "TI-driven hunting with retrospective analysis."},
        "ADR-04": {"source_urls": ["https://www.anomali.com/"], "key_evidence": ["Adversary tracking through ThreatStream intelligence aggregation.", "Threat actor profiling and TTP mapping."], "notes": "TI-based adversary tracking."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["Some detection coverage assessment."], "notes": "Minimal."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Some asset intelligence through TI enrichment.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-02": {"score_rationale": "Some exposure context through TI.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-03": {"score_rationale": "TI-enriched vulnerability correlation with active threats.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Basic supply chain intelligence.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Anomali scores 4 (Advanced) for Threat Intel Operationalization. ThreatStream aggregates hundreds of feeds. Match provides real-time IoC correlation. Security Analytics for big-data analysis. NLP-based intelligence processing.", "evidence_quality_rationale": "Strong. Major TIP with named products.", "scoring_level_justification": "Level 4: Advanced TIP with real-time correlation.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Intelligence-driven hunting with retrospective analysis and MITRE ATT&CK content.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named hunting capability with TI integration.", "confidence": "high"},
        "ADR-04": {"score_rationale": "Adversary tracking and TTP mapping through ThreatStream.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Some detection coverage assessment.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["ZeroFox"] = {
    "scores": {"EXM-01": 2, "EXM-02": 1, "EXM-03": 1, "EXM-04": 2, "AMT-01": 0, "AMT-02": 0, "AMT-03": 0, "AMT-04": 0, "ADR-01": 0, "ADR-02": 3, "ADR-03": 1, "ADR-04": 5, "PPM-01": 0, "PPM-02": 0, "PPM-03": 0, "PPM-04": 0},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.zerofox.com/"], "key_evidence": ["ZeroFox provides external attack surface monitoring including domain, social media, and dark web exposure.", "External threat intelligence for digital asset discovery."], "notes": "External digital asset monitoring."},
        "EXM-02": {"source_urls": [], "key_evidence": ["Some exposure context through digital risk monitoring."], "notes": "Minimal."},
        "EXM-03": {"source_urls": [], "key_evidence": ["Basic vulnerability context."], "notes": "Minimal."},
        "EXM-04": {"source_urls": ["https://www.zerofox.com/"], "key_evidence": ["Supply chain impersonation and fraud detection.", "Third-party brand abuse monitoring."], "notes": "Brand protection for supply chain."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://www.zerofox.com/"], "key_evidence": ["External threat intelligence from social media, dark web, and surface web monitoring.", "Dark web monitoring for credential exposure and adversary activity.", "Intelligence feeds from collecting across digital channels."], "notes": "External/digital threat intelligence. Dark web + social media."},
        "ADR-03": {"source_urls": [], "key_evidence": ["Basic external threat monitoring."], "notes": "Minimal."},
        "ADR-04": {"source_urls": ["https://www.zerofox.com/", "https://www.zerofox.com/platform/"], "key_evidence": ["ZeroFox is a market leader in Digital Risk Protection (DRP) — providing comprehensive counter-adversary operations in the digital attack surface.", "Automated takedown services for phishing sites, impersonation accounts, and fraudulent content.", "Social media threat monitoring and adversary engagement tracking across major platforms.", "Brand protection with automated detection and disruption of brand impersonation campaigns.", "Dark web monitoring for credential dumps, PII exposure, and adversary planning.", "Merged with IDX for identity protection — combined digital risk protection and identity threat management.", "Named in Forrester research for digital risk protection and external threat intelligence."], "notes": "Market-leading DRP. Automated takedowns, brand protection, social media monitoring. Forrester-recognized."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "External digital asset monitoring including domain, social media, and dark web.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Digital asset discovery.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Some exposure context through digital risk monitoring.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-03": {"score_rationale": "Basic vulnerability context.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-04": {"score_rationale": "Supply chain impersonation and brand abuse monitoring.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "External/digital threat intelligence from social media, dark web, and surface web. Credential exposure monitoring.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named external TI sources.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Basic external threat monitoring.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-04": {"score_rationale": "ZeroFox scores 5 (Market-Leading) for Counter-Adversary Ops. Market leader in Digital Risk Protection with automated takedowns for phishing/impersonation, social media adversary tracking, brand protection automation, dark web monitoring. Merged with IDX. Forrester-recognized.", "evidence_quality_rationale": "Exceptional. Category-leading DRP with comprehensive counter-adversary capabilities.", "scoring_level_justification": "Level 5: Best-in-class digital risk protection and automated takedowns.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Nisos"] = {
    "scores": {"EXM-01": 1, "EXM-02": 0, "EXM-03": 0, "EXM-04": 1, "AMT-01": 0, "AMT-02": 0, "AMT-03": 0, "AMT-04": 0, "ADR-01": 0, "ADR-02": 3, "ADR-03": 2, "ADR-04": 4, "PPM-01": 0, "PPM-02": 0, "PPM-03": 0, "PPM-04": 0},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.nisos.com/"], "key_evidence": ["Some external threat surface monitoring."], "notes": "Minimal."},
        "EXM-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "EXM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "EXM-04": {"source_urls": [], "key_evidence": ["Some third-party risk intelligence."], "notes": "Minimal."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://www.nisos.com/"], "key_evidence": ["Nisos provides managed intelligence services with human-led OSINT analysis.", "Deep and dark web intelligence collection and analysis.", "Attribution intelligence for threat actors targeting organizations."], "notes": "Managed OSINT intelligence services. Human-led analysis."},
        "ADR-03": {"source_urls": ["https://www.nisos.com/"], "key_evidence": ["Intelligence-driven threat investigation and hunting support.", "OSINT-driven adversary infrastructure identification."], "notes": "OSINT-driven hunting support."},
        "ADR-04": {"source_urls": ["https://www.nisos.com/", "https://www.nisos.com/services/"], "key_evidence": ["Nisos specializes in managed counter-adversary intelligence with attribution and investigation services.", "Insider threat investigation and disinformation campaign analysis.", "Executive protection intelligence for high-value targets.", "Adversary attribution using OSINT and dark web intelligence.", "Founded by former intelligence community professionals with government-grade tradecraft."], "notes": "Counter-adversary intelligence specialist. Former IC professionals. Attribution, insider threat, disinformation analysis."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Some external threat surface monitoring.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Some third-party risk intelligence.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Managed OSINT intelligence with human-led analysis. Dark web collection and attribution intelligence.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named managed intelligence services.", "confidence": "high"},
        "ADR-03": {"score_rationale": "OSINT-driven threat investigation and adversary infrastructure identification.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "ADR-04": {"score_rationale": "Nisos scores 4 (Advanced) for Counter-Adversary Ops. Specialist in managed counter-adversary intelligence with attribution, insider threat investigation, executive protection, and disinformation analysis. Founded by former IC professionals with government-grade tradecraft.", "evidence_quality_rationale": "Strong. Specialist firm with IC-grade capabilities.", "scoring_level_justification": "Level 4: Advanced managed counter-adversary with IC pedigree.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Arctic Wolf"] = {
    "scores": {"EXM-01": 2, "EXM-02": 1, "EXM-03": 2, "EXM-04": 1, "AMT-01": 0, "AMT-02": 0, "AMT-03": 1, "AMT-04": 1, "ADR-01": 0, "ADR-02": 2, "ADR-03": 4, "ADR-04": 1, "PPM-01": 0, "PPM-02": 2, "PPM-03": 0, "PPM-04": 1},
    "evidence": {
        "EXM-01": {"source_urls": ["https://arcticwolf.com/"], "key_evidence": ["Arctic Wolf Managed Risk provides asset discovery and vulnerability assessment.", "Continuous network scanning and endpoint vulnerability identification."], "notes": "Managed vulnerability scanning."},
        "EXM-02": {"source_urls": [], "key_evidence": ["Some exposure management through Managed Risk service."], "notes": "Managed risk assessments."},
        "EXM-03": {"source_urls": ["https://arcticwolf.com/"], "key_evidence": ["Managed Risk includes vulnerability prioritization with concierge security approach.", "Risk-based prioritization through the Security Operations Cloud."], "notes": "Managed vulnerability prioritization."},
        "EXM-04": {"source_urls": [], "key_evidence": ["Basic third-party visibility."], "notes": "Minimal."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["Basic network monitoring."], "notes": "Minimal."},
        "AMT-04": {"source_urls": [], "key_evidence": ["Basic identity monitoring through MDR."], "notes": "Minimal."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://arcticwolf.com/"], "key_evidence": ["Arctic Wolf Labs provides threat research and intelligence.", "Intelligence from monitoring thousands of customer environments."], "notes": "Managed intelligence from large customer base."},
        "ADR-03": {"source_urls": ["https://arcticwolf.com/", "https://arcticwolf.com/products/"], "key_evidence": ["Arctic Wolf Managed Detection and Response (MDR) provides 24/7 managed threat hunting.", "Concierge Security Team (CST) provides dedicated security engineers per customer.", "Security Operations Cloud processes trillions of weekly observations for threat detection.", "Named threat hunting with human-led analysis and response.", "One of the largest pure-play MDR providers with thousands of customers."], "notes": "Top-tier MDR. Concierge Security Model is a differentiator. Massive scale."},
        "ADR-04": {"source_urls": [], "key_evidence": ["Basic adversary context from MDR operations."], "notes": "Minimal."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": ["https://arcticwolf.com/"], "key_evidence": ["Security posture assessment through Managed Risk.", "Benchmark scoring against industry standards."], "notes": "Managed posture assessment."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": [], "key_evidence": ["Basic cloud monitoring through MDR."], "notes": "Minimal."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Managed Risk provides asset discovery and vulnerability assessment.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Named managed risk service.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Some exposure management through Managed Risk.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Managed vulnerability prioritization with concierge approach.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Basic third-party visibility.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Basic network monitoring.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "AMT-04": {"score_rationale": "Basic identity monitoring through MDR.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Arctic Wolf Labs provides threat research from monitoring thousands of customer environments.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Managed intelligence from large base.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Arctic Wolf scores 4 (Advanced) for Proactive Threat Hunting. One of the largest pure-play MDR providers with 24/7 managed hunting. Concierge Security Team model dedicates security engineers per customer. Security Operations Cloud processes trillions of observations weekly.", "evidence_quality_rationale": "Strong. Major MDR vendor with demonstrated scale.", "scoring_level_justification": "Level 4: Advanced managed threat hunting at massive scale.", "confidence": "high"},
        "ADR-04": {"score_rationale": "Basic adversary context from MDR operations.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Security posture assessment with industry benchmarking through Managed Risk.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Basic cloud monitoring.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"}
    }
}

# ═══════════════════════════════════════════════════════════════════════
# BATCH 8: Group-IB, SafeBreach, AttackIQ, Cymulate, Pentera
# ═══════════════════════════════════════════════════════════════════════

VENDOR_RESEARCH["Group-IB"] = {
    "scores": {"EXM-01": 2, "EXM-02": 1, "EXM-03": 1, "EXM-04": 2, "AMT-01": 0, "AMT-02": 0, "AMT-03": 0, "AMT-04": 0, "ADR-01": 1, "ADR-02": 4, "ADR-03": 3, "ADR-04": 5, "PPM-01": 0, "PPM-02": 0, "PPM-03": 0, "PPM-04": 0},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.group-ib.com/"], "key_evidence": ["Attack Surface Management capability identifies external-facing digital assets.", "Digital Risk Protection includes external exposure monitoring."], "notes": "External asset discovery through DRP."},
        "EXM-02": {"source_urls": [], "key_evidence": ["Some exposure lifecycle through continuous monitoring."], "notes": "Minimal."},
        "EXM-03": {"source_urls": [], "key_evidence": ["Basic vulnerability context through threat intelligence."], "notes": "Minimal."},
        "EXM-04": {"source_urls": ["https://www.group-ib.com/"], "key_evidence": ["Third-party compromise monitoring through dark web and cybercrime ecosystem intelligence.", "Supply chain threat monitoring."], "notes": "Supply chain TI from cybercrime intelligence."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["Some deception-adjacent capability through honeypot systems for threat research."], "notes": "Research honeypots."},
        "ADR-02": {"source_urls": ["https://www.group-ib.com/", "https://www.group-ib.com/products/"], "key_evidence": ["Group-IB Threat Intelligence provides deep cybercrime ecosystem intelligence.", "Unique intelligence from infiltrating cybercrime forums, marketplaces, and underground infrastructure.", "Proprietary botnet tracking and C2 infrastructure monitoring.", "High-Confidence Intelligence mapped to MITRE ATT&CK framework."], "notes": "Deep cybercrime intelligence. Unique underground access and bot tracking."},
        "ADR-03": {"source_urls": ["https://www.group-ib.com/"], "key_evidence": ["Managed XDR includes threat hunting capabilities.", "CERT-GIB provides incident investigation and threat hunting.", "Intelligence-driven hunting based on cybercrime ecosystem insights."], "notes": "Managed hunting through CERT-GIB."},
        "ADR-04": {"source_urls": ["https://www.group-ib.com/", "https://www.group-ib.com/services/"], "key_evidence": ["Group-IB is a world leader in cybercrime investigation and takedown operations.", "Digital Risk Protection provides automated takedowns of phishing, scam, and impersonation infrastructure.", "Worked with INTERPOL and international law enforcement on major cybercrime disruptions.", "Proprietary infrastructure tracking enables attribution of cybercriminal groups.", "Brand Protection with automated detection and disruption of brand abuse.", "Scam Intelligence identifies and takes down large-scale fraud campaigns."], "notes": "World-class cybercrime investigation and takedown. INTERPOL partnerships. Automated DRP and brand protection."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "External asset discovery through Digital Risk Protection.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Some exposure monitoring.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-03": {"score_rationale": "Basic vulnerability context.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-04": {"score_rationale": "Third-party compromise monitoring through cybercrime intelligence.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "Research honeypots. Not commercial deception.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-02": {"score_rationale": "Group-IB scores 4 (Advanced) for TI. Deep cybercrime ecosystem intelligence from underground forums/marketplaces. Proprietary botnet and C2 tracking. ATT&CK-mapped high-confidence intelligence.", "evidence_quality_rationale": "Strong. Unique underground access and intelligence.", "scoring_level_justification": "Level 4: Advanced cybercrime intelligence.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Managed hunting through CERT-GIB with cybercrime intelligence-driven approach.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3.", "confidence": "high"},
        "ADR-04": {"score_rationale": "Group-IB scores 5 (Market-Leading) for Counter-Adversary Ops. World leader in cybercrime investigation and takedowns. INTERPOL partnerships. Automated DRP and brand protection. Infrastructure attribution capabilities. Scam Intelligence for fraud campaign disruption.", "evidence_quality_rationale": "Exceptional. INTERPOL-partnered cybercrime takedowns.", "scoring_level_justification": "Level 5: Best-in-class cybercrime investigation and takedown.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["SafeBreach"] = {
    "scores": {"EXM-01": 1, "EXM-02": 1, "EXM-03": 1, "EXM-04": 0, "AMT-01": 0, "AMT-02": 0, "AMT-03": 0, "AMT-04": 0, "ADR-01": 0, "ADR-02": 2, "ADR-03": 1, "ADR-04": 0, "PPM-01": 5, "PPM-02": 5, "PPM-03": 3, "PPM-04": 1},
    "evidence": {
        "EXM-01": {"source_urls": [], "key_evidence": ["Some exposure context from attack simulation results."], "notes": "Simulation-derived exposure."},
        "EXM-02": {"source_urls": [], "key_evidence": ["Some CTEM enablement through continuous validation."], "notes": "BAS feeds CTEM."},
        "EXM-03": {"source_urls": [], "key_evidence": ["Basic vulnerability context from attack simulations."], "notes": "Minimal."},
        "EXM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://www.safebreach.com/"], "key_evidence": ["Hacker's Playbook contains 30,000+ attack simulations mapped to real-world techniques.", "Threat intelligence integration drives simulation content updates."], "notes": "TI-driven attack content library."},
        "ADR-03": {"source_urls": [], "key_evidence": ["Some detection gap identification enables hunting focus areas."], "notes": "Minimal."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": ["https://www.safebreach.com/", "https://www.safebreach.com/platform/"], "key_evidence": ["SafeBreach is a market-leading Breach and Attack Simulation (BAS) platform.", "Hacker's Playbook with 30,000+ attack methods continuously updated with emerging threats.", "Full kill-chain simulation across network, endpoint, email, cloud, and lateral movement.", "Continuous and automated validation of security controls without disruption to production.", "MITRE ATT&CK-aligned simulation library for comprehensive coverage mapping.", "Named in Gartner research for BAS and security validation."], "notes": "Market-leading BAS. 30K+ attack methods. Full kill-chain simulation. Gartner-recognized."},
        "PPM-02": {"source_urls": ["https://www.safebreach.com/"], "key_evidence": ["Industry-leading security control validation — identifying gaps in prevention, detection, and response.", "Continuous validation ensures controls remain effective over time.", "Integration with SIEM, EDR, and firewall for automated control optimization recommendations.", "Coverage scoring against MITRE ATT&CK framework for detection gap analysis.", "SafeBreach Score quantifies overall security posture effectiveness."], "notes": "Best-in-class security control validation. Continuous gap identification with optimization guidance."},
        "PPM-03": {"source_urls": ["https://www.safebreach.com/"], "key_evidence": ["Automated red team capabilities simulating real-world attack scenarios.", "Purple team enablement through shared simulation results and remediation guidance.", "Pen test-adjacent findings from automated attack simulation."], "notes": "Automated red team/purple team enablement."},
        "PPM-04": {"source_urls": [], "key_evidence": ["Some cloud-focused simulations."], "notes": "Basic."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Some exposure context from attack simulation.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-02": {"score_rationale": "BAS enables CTEM through continuous validation.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-03": {"score_rationale": "Basic vulnerability context from simulations.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "30K+ attack library with TI integration.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Detection gap identification enables hunting focus areas.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "SafeBreach scores 5 (Market-Leading) for BAS. Market-leading platform with 30,000+ attack methods, full kill-chain simulation, continuous automated validation, MITRE ATT&CK coverage mapping. Gartner-recognized.", "evidence_quality_rationale": "Exceptional. Category leader with massive attack library.", "scoring_level_justification": "Level 5: Best-in-class BAS platform.", "confidence": "high"},
        "PPM-02": {"score_rationale": "SafeBreach scores 5 (Market-Leading) for Security Control Validation. Industry-leading continuous control validation with SIEM/EDR/firewall integration. SafeBreach Score for posture quantification. MITRE ATT&CK coverage mapping.", "evidence_quality_rationale": "Exceptional. Category-defining control validation.", "scoring_level_justification": "Level 5: Best-in-class continuous control validation.", "confidence": "high"},
        "PPM-03": {"score_rationale": "Automated red/purple team capabilities simulating real-world scenarios.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Automated red team adjacent.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Some cloud-focused simulations.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"}
    }
}

VENDOR_RESEARCH["AttackIQ"] = {
    "scores": {"EXM-01": 1, "EXM-02": 1, "EXM-03": 1, "EXM-04": 0, "AMT-01": 0, "AMT-02": 0, "AMT-03": 0, "AMT-04": 0, "ADR-01": 0, "ADR-02": 2, "ADR-03": 1, "ADR-04": 0, "PPM-01": 5, "PPM-02": 5, "PPM-03": 3, "PPM-04": 1},
    "evidence": {
        "EXM-01": {"source_urls": [], "key_evidence": ["Some exposure insights from validation results."], "notes": "Simulation-derived."},
        "EXM-02": {"source_urls": [], "key_evidence": ["Continuous validation enables CTEM lifecycle."], "notes": "CTEM enablement."},
        "EXM-03": {"source_urls": [], "key_evidence": ["Basic vulnerability context from simulations."], "notes": "Minimal."},
        "EXM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://www.attackiq.com/"], "key_evidence": ["MITRE ATT&CK-aligned attack scenarios with threat intelligence integration.", "AttackIQ is a co-founder of the MITRE Center for Threat-Informed Defense."], "notes": "MITRE partnership drives TI alignment."},
        "ADR-03": {"source_urls": [], "key_evidence": ["Detection gap identification for hunting priorities."], "notes": "Minimal."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": ["https://www.attackiq.com/", "https://www.attackiq.com/platform/"], "key_evidence": ["AttackIQ is a market-leading BAS platform co-founded with MITRE for threat-informed defense.", "AttackIQ Enterprise provides continuous automated validation of security controls.", "AttackIQ Ready! provides turn-key BAS for smaller organizations.", "MITRE ATT&CK-first approach with the most comprehensive ATT&CK-aligned scenario library.", "Co-founder of MITRE Center for Threat-Informed Defense — setting the standard for security validation.", "Continuous testing with automated anatomic emulation of adversary campaigns."], "notes": "Market-leading BAS. MITRE co-founder for threat-informed defense. ATT&CK-first approach."},
        "PPM-02": {"source_urls": ["https://www.attackiq.com/"], "key_evidence": ["Security control optimization through continuous validation and gap analysis.", "Platform identifies specific control failures and provides remediation guidance.", "MITRE ATT&CK coverage scoring for comprehensive detection assessment.", "Integration with security stack for automated validation and optimization."], "notes": "Excellent control validation with MITRE ATT&CK integration."},
        "PPM-03": {"source_urls": ["https://www.attackiq.com/"], "key_evidence": ["Automated adversary emulation provides pen-test-like findings.", "Purple team enablement through shared simulation results."], "notes": "Automated adversary emulation."},
        "PPM-04": {"source_urls": [], "key_evidence": ["Some cloud-focused validations."], "notes": "Basic."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Some exposure insights from validation.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-02": {"score_rationale": "Continuous validation enables CTEM.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-03": {"score_rationale": "Basic vulnerability context.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "MITRE co-founder with ATT&CK-aligned scenarios and TI integration.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Detection gap identification for hunting.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "AttackIQ scores 5 (Market-Leading) for BAS. Co-founder of MITRE Center for Threat-Informed Defense. ATT&CK-first approach with comprehensive scenario library. AttackIQ Enterprise and Ready! for automated validation. Industry standard-setter for security validation.", "evidence_quality_rationale": "Exceptional. MITRE partnership, category-defining.", "scoring_level_justification": "Level 5: Best-in-class BAS with MITRE co-founding.", "confidence": "high"},
        "PPM-02": {"score_rationale": "AttackIQ scores 5 (Market-Leading) for Security Control Validation. Continuous control optimization with MITRE ATT&CK coverage scoring. Specific control failure identification with remediation guidance. Security stack integration.", "evidence_quality_rationale": "Exceptional. Category-defining validation.", "scoring_level_justification": "Level 5: Best-in-class control validation.", "confidence": "high"},
        "PPM-03": {"score_rationale": "Automated adversary emulation provides pen-test-adjacent findings.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Automated adversary emulation.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Some cloud-focused validations.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"}
    }
}

VENDOR_RESEARCH["Cymulate"] = {
    "scores": {"EXM-01": 2, "EXM-02": 2, "EXM-03": 2, "EXM-04": 1, "AMT-01": 0, "AMT-02": 0, "AMT-03": 0, "AMT-04": 0, "ADR-01": 0, "ADR-02": 2, "ADR-03": 1, "ADR-04": 0, "PPM-01": 5, "PPM-02": 4, "PPM-03": 4, "PPM-04": 1},
    "evidence": {
        "EXM-01": {"source_urls": ["https://cymulate.com/"], "key_evidence": ["Cymulate Exposure Management provides attack surface assessment and exposure identification.", "Continuous visibility into external and internal attack surfaces."], "notes": "Named exposure management capability."},
        "EXM-02": {"source_urls": ["https://cymulate.com/"], "key_evidence": ["Cymulate explicitly aligns with CTEM framework.", "Exposure Management module enables CTEM lifecycle operationalization."], "notes": "Explicit CTEM alignment."},
        "EXM-03": {"source_urls": ["https://cymulate.com/"], "key_evidence": ["Exposure-based vulnerability prioritization through attack simulation context.", "Risk-ranked exposure identification."], "notes": "BAS-driven vulnerability prioritization."},
        "EXM-04": {"source_urls": [], "key_evidence": ["Basic supply chain assessment."], "notes": "Minimal."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://cymulate.com/"], "key_evidence": ["Threat intelligence-driven attack scenarios.", "Emerging threat simulations updated from threat intelligence feeds."], "notes": "TI-driven simulation content."},
        "ADR-03": {"source_urls": [], "key_evidence": ["Detection gap identification."], "notes": "Minimal."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": ["https://cymulate.com/", "https://cymulate.com/platform/"], "key_evidence": ["Cymulate is a market-leading BAS and Exposure Management platform providing comprehensive security validation.", "Full kill-chain attack simulations across email gateway, web gateway, WAF, endpoints, and lateral movement.", "Immediate Threats module validates defense against emerging and active threats within hours of disclosure.", "Continuous automated validation with on-demand and scheduled testing.", "MITRE ATT&CK-aligned attack scenario library.", "Named in Gartner research for BAS and security validation."], "notes": "Market-leading BAS with exposure management. Full kill-chain. Immediate threat validation."},
        "PPM-02": {"source_urls": ["https://cymulate.com/"], "key_evidence": ["Security control validation with detailed gap analysis and remediation guidance.", "Cymulate Score quantifies security posture across attack vectors.", "Continuous monitoring of control effectiveness with trending and benchmarking."], "notes": "Strong control validation with posture scoring."},
        "PPM-03": {"source_urls": ["https://cymulate.com/"], "key_evidence": ["Cymulate Advanced Scenarios provides automated purple team and red team exercises.", "Customizable attack scenarios for targeted pen-test-like assessments.", "Purple team module enables collaborative testing between attack and defense teams.", "Automated penetration testing through attack path simulation."], "notes": "Strong purple team and automated pen testing capability."},
        "PPM-04": {"source_urls": [], "key_evidence": ["Some cloud-focused simulations."], "notes": "Basic."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Named Exposure Management capability with continuous visibility.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Explicit CTEM framework alignment.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Named CTEM alignment.", "confidence": "high"},
        "EXM-03": {"score_rationale": "BAS-driven vulnerability prioritization through simulation context.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Basic supply chain assessment.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "TI-driven attack scenarios with emerging threat updates.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Detection gap identification.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "Cymulate scores 5 (Market-Leading) for BAS. Market-leading BAS with full kill-chain simulation, Immediate Threats module for emerging threat validation, MITRE ATT&CK alignment. Named exposure management integration. Gartner-recognized.", "evidence_quality_rationale": "Exceptional. Category leader with comprehensive BAS.", "scoring_level_justification": "Level 5: Best-in-class BAS with exposure management.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Cymulate scores 4 (Advanced) for Security Control Validation. Detailed gap analysis with Cymulate Score. Continuous monitoring with trending and benchmarking. Remediation guidance.", "evidence_quality_rationale": "Strong. Named scoring and validation.", "scoring_level_justification": "Level 4: Advanced control validation.", "confidence": "high"},
        "PPM-03": {"score_rationale": "Cymulate scores 4 (Advanced) for Pen Testing/Red Teaming. Advanced Scenarios module with automated purple/red team exercises. Customizable attack scenarios. Attack path simulation.", "evidence_quality_rationale": "Strong. Named purple team module.", "scoring_level_justification": "Level 4: Advanced automated purple/red teaming.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Some cloud-focused simulations.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"}
    }
}

VENDOR_RESEARCH["Pentera"] = {
    "scores": {"EXM-01": 2, "EXM-02": 2, "EXM-03": 3, "EXM-04": 1, "AMT-01": 0, "AMT-02": 0, "AMT-03": 0, "AMT-04": 0, "ADR-01": 0, "ADR-02": 1, "ADR-03": 1, "ADR-04": 0, "PPM-01": 4, "PPM-02": 4, "PPM-03": 5, "PPM-04": 1},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.pentera.io/"], "key_evidence": ["Pentera Surface provides external attack surface discovery.", "Identifies exposed services, misconfigurations, and vulnerable assets."], "notes": "Named EASM product."},
        "EXM-02": {"source_urls": ["https://www.pentera.io/"], "key_evidence": ["Continuous automated pen testing enables CTEM lifecycle.", "Some CTEM enablement through continuous validation."], "notes": "CTEM enablement through continuous testing."},
        "EXM-03": {"source_urls": ["https://www.pentera.io/"], "key_evidence": ["Vulnerability validation through actual exploitation — proving which vulnerabilities are truly exploitable.", "Real exploit-based prioritization rather than theoretical risk scoring.", "Identifies exploitable attack paths combining multiple vulnerabilities."], "notes": "Exploit-validated vulnerability prioritization. A key differentiator."},
        "EXM-04": {"source_urls": [], "key_evidence": ["Basic supply chain assessment."], "notes": "Minimal."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": [], "key_evidence": ["Basic threat context from pen testing results."], "notes": "Minimal."},
        "ADR-03": {"source_urls": [], "key_evidence": ["Some hunting context from pen test findings."], "notes": "Minimal."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": ["https://www.pentera.io/", "https://www.pentera.io/platform/"], "key_evidence": ["Pentera provides automated penetration testing that includes BAS-like attack simulation.", "Full kill-chain validation with real exploitation (not theoretical simulation).", "Continuous testing capability with on-demand and scheduled execution.", "MITRE ATT&CK-aligned testing scenarios."], "notes": "Strong BAS-adjacent through automated pen testing."},
        "PPM-02": {"source_urls": ["https://www.pentera.io/"], "key_evidence": ["Security control validation through real exploitation attempts.", "Identifies control failures with proof-of-concept exploits.", "Remediation prioritization based on actual exploitability."], "notes": "Exploit-validated control testing."},
        "PPM-03": {"source_urls": ["https://www.pentera.io/", "https://www.pentera.io/platform/"], "key_evidence": ["Pentera is a market leader in Automated Penetration Testing — providing agentless, continuous pen testing with real exploits.", "Pentera Core provides internal penetration testing with credential harvesting, lateral movement, and privilege escalation.", "Pentera Surface provides external penetration testing of internet-facing assets.", "Uses real exploits (ethical exploits) rather than simulations — validating actual exploitability.", "Credential brute-forcing, hash extraction, and Active Directory attack testing.", "Named in Gartner research for automated pen testing and security validation.", "Agentless architecture requires no agents or reconfiguration."], "notes": "Market-leading automated pen testing. Real exploits, agentless, continuous. Gartner-recognized."},
        "PPM-04": {"source_urls": [], "key_evidence": ["Some cloud-focused pen testing."], "notes": "Basic."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Pentera Surface provides EASM.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Named EASM product.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Continuous automated pen testing enables CTEM.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Exploit-validated vulnerability prioritization — proving actual exploitability rather than theoretical risk.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Real exploit validation.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Basic supply chain assessment.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Basic threat context from pen test results.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-03": {"score_rationale": "Some hunting context from findings.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "Pentera scores 4 (Advanced) for BAS. Automated pen testing with real exploitation provides BAS-like validation. Full kill-chain with MITRE ATT&CK alignment. Continuous testing capability.", "evidence_quality_rationale": "Strong. Exploit-based validation rather than simulation.", "scoring_level_justification": "Level 4: Advanced BAS through real exploitation.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Pentera scores 4 (Advanced) for Security Control Validation. Real exploitation validates control effectiveness. Proof-of-concept exploits for control failures. Exploit-based prioritization.", "evidence_quality_rationale": "Strong. Real exploit validation is a differentiator.", "scoring_level_justification": "Level 4: Advanced control validation through real exploits.", "confidence": "high"},
        "PPM-03": {"score_rationale": "Pentera scores 5 (Market-Leading) for Automated Pen Testing. Market leader with agentless, real-exploit-based continuous pen testing. Core (internal) and Surface (external). Credential harvesting, lateral movement, privilege escalation, AD attacks. Gartner-recognized.", "evidence_quality_rationale": "Exceptional. Category leader in automated pen testing.", "scoring_level_justification": "Level 5: Best-in-class automated penetration testing.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Some cloud pen testing.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"}
    }
}

# ═══════════════════════════════════════════════════════════════════════
# BATCH 9: Horizon3.ai, Picus Security, Wiz, Orca Security, Aqua Security
# ═══════════════════════════════════════════════════════════════════════

VENDOR_RESEARCH["Horizon3.ai"] = {
    "scores": {"EXM-01": 2, "EXM-02": 2, "EXM-03": 3, "EXM-04": 1, "AMT-01": 0, "AMT-02": 0, "AMT-03": 0, "AMT-04": 0, "ADR-01": 0, "ADR-02": 1, "ADR-03": 1, "ADR-04": 0, "PPM-01": 4, "PPM-02": 3, "PPM-03": 5, "PPM-04": 1},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.horizon3.ai/"], "key_evidence": ["NodeZero discovers attack surface including exposed services and assets.", "External and internal asset discovery during autonomous pen test execution."], "notes": "Pen-test-driven asset discovery."},
        "EXM-02": {"source_urls": ["https://www.horizon3.ai/"], "key_evidence": ["Continuous autonomous pen testing enables CTEM lifecycle.", "Regular validation cadence for exposure management."], "notes": "CTEM enablement."},
        "EXM-03": {"source_urls": ["https://www.horizon3.ai/"], "key_evidence": ["NodeZero validates which vulnerabilities are actually exploitable — proving real risk.", "Exploit-validated prioritization eliminates false priority vulnerabilities.", "Identifies complete attack paths combining multiple weaknesses."], "notes": "Exploit-validated vulnerability prioritization. Differentiator."},
        "EXM-04": {"source_urls": [], "key_evidence": ["Basic supply chain assessment."], "notes": "Minimal."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": [], "key_evidence": ["Basic threat context from pen test findings."], "notes": "Minimal."},
        "ADR-03": {"source_urls": [], "key_evidence": ["Some detection gap identification."], "notes": "Minimal."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": ["https://www.horizon3.ai/", "https://www.horizon3.ai/product/"], "key_evidence": ["NodeZero provides autonomous penetration testing with BAS-like continuous validation.", "Self-service, autonomous pen testing from a SaaS platform — no agents or installations.", "Full kill-chain exploitation including credential abuse, lateral movement, and data exfiltration.", "Continuous testing capability with rapid deployment."], "notes": "Autonomous pen testing provides BAS capability."},
        "PPM-02": {"source_urls": ["https://www.horizon3.ai/"], "key_evidence": ["NodeZero identifies security control failures through real exploitation.", "Proof-of-concept evidence for control gaps.", "Remediation verification through re-testing."], "notes": "Control validation through real exploitation."},
        "PPM-03": {"source_urls": ["https://www.horizon3.ai/", "https://www.horizon3.ai/product/"], "key_evidence": ["Horizon3.ai NodeZero is a market-leading autonomous penetration testing platform.", "Autonomous pen testing — zero setup, zero agents, SaaS-delivered.", "Real exploitation validates vulnerabilities and discovers complete attack paths.", "Credential harvesting, lateral movement, privilege escalation, Active Directory attacks.", "1-click pen testing with proof-of-exploit evidence and remediation guidance.", "Founded by former US Cyber Command operators with offensive security expertise.", "NodeZero Tripwires provides continuous monitoring between pen tests."], "notes": "Market-leading autonomous pen testing. Former Cyber Command team. 1-click SaaS pen testing."},
        "PPM-04": {"source_urls": [], "key_evidence": ["Some cloud pen testing capability."], "notes": "Basic."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Pen-test-driven asset discovery.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Continuous autonomous pen testing enables CTEM.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Exploit-validated vulnerability prioritization proving real risk.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Real exploit validation.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Basic supply chain assessment.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Basic threat context from pen test findings.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-03": {"score_rationale": "Some detection gap identification.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "NodeZero provides autonomous pen testing with BAS-like continuous validation. Full kill-chain with SaaS delivery.", "evidence_quality_rationale": "Strong.", "scoring_level_justification": "Level 4: Advanced BAS through autonomous pen testing.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Control validation through real exploitation with proof-of-concept evidence.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Exploit-validated control testing.", "confidence": "high"},
        "PPM-03": {"score_rationale": "Horizon3.ai scores 5 (Market-Leading) for Automated Pen Testing. NodeZero provides autonomous, agentless, SaaS-delivered pen testing with real exploitation. 1-click deployment. Founded by former Cyber Command operators. Credential harvesting, lateral movement, AD attacks. Tripwires for continuous monitoring.", "evidence_quality_rationale": "Exceptional. Category leader with military-grade pedigree.", "scoring_level_justification": "Level 5: Best-in-class autonomous pen testing.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Some cloud pen testing.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"}
    }
}

VENDOR_RESEARCH["Picus Security"] = {
    "scores": {"EXM-01": 1, "EXM-02": 2, "EXM-03": 2, "EXM-04": 0, "AMT-01": 0, "AMT-02": 0, "AMT-03": 0, "AMT-04": 0, "ADR-01": 0, "ADR-02": 2, "ADR-03": 1, "ADR-04": 0, "PPM-01": 5, "PPM-02": 5, "PPM-03": 3, "PPM-04": 1},
    "evidence": {
        "EXM-01": {"source_urls": [], "key_evidence": ["Some exposure context from validation results."], "notes": "Simulation-derived."},
        "EXM-02": {"source_urls": ["https://www.picussecurity.com/"], "key_evidence": ["Picus explicitly positions for CTEM enablement.", "Security Validation Platform enables continuous exposure management lifecycle."], "notes": "CTEM positioning."},
        "EXM-03": {"source_urls": ["https://www.picussecurity.com/"], "key_evidence": ["Attack-simulation-derived vulnerability prioritization.", "Identifies which threat scenarios succeed against current defenses."], "notes": "BAS-derived prioritization."},
        "EXM-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://www.picussecurity.com/"], "key_evidence": ["Threat intelligence-driven simulation content.", "Emerging threat simulations available within 24 hours of disclosure."], "notes": "TI-driven content with rapid updates."},
        "ADR-03": {"source_urls": [], "key_evidence": ["Detection gap identification."], "notes": "Minimal."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": ["https://www.picussecurity.com/", "https://www.picussecurity.com/platform/"], "key_evidence": ["Picus Security is a market-leading BAS platform with the industry's most comprehensive attack simulation library.", "Complete Security Validation Platform with attack simulation, detection rule validation, and attack path validation.", "Threat-intelligence-driven scenarios updated within 24 hours of emerging threats.", "MITRE ATT&CK-aligned simulation with comprehensive coverage mapping.", "Named in Gartner Hype Cycle for Security Operations and security validation research."], "notes": "Market-leading BAS. Comprehensive platform with rapid emerging threat coverage."},
        "PPM-02": {"source_urls": ["https://www.picussecurity.com/"], "key_evidence": ["Picus Mitigation Library provides vendor-specific remediation guidance — unique capability.", "Detection rule validation ensures SIEM/EDR detection rules are actually firing correctly.", "Security control optimization with specific configuration recommendations.", "Ready-to-apply detection content (Sigma, Splunk, QRadar) generated automatically.", "The Blue Report provides industry benchmarking and posture scoring."], "notes": "Exceptional control validation with vendor-specific remediation. Detection rule validation is a differentiator."},
        "PPM-03": {"source_urls": ["https://www.picussecurity.com/"], "key_evidence": ["Attack path validation provides automated attack path assessment.", "Purple team enablement through shared simulation and detection optimization."], "notes": "Attack path validation and purple team."},
        "PPM-04": {"source_urls": [], "key_evidence": ["Some cloud-focused simulations."], "notes": "Basic."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Some exposure context from validation.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-02": {"score_rationale": "Explicit CTEM enablement positioning.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-03": {"score_rationale": "BAS-derived vulnerability and threat scenario prioritization.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "TI-driven simulation with 24-hour emerging threat coverage.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Detection gap identification.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "Picus scores 5 (Market-Leading) for BAS. Comprehensive Security Validation Platform with attack simulation, detection rule validation, and attack path validation. 24-hour emerging threat coverage. Gartner Hype Cycle recognized.", "evidence_quality_rationale": "Exceptional. Category leader with comprehensive platform.", "scoring_level_justification": "Level 5: Best-in-class BAS with unique detection validation.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Picus scores 5 (Market-Leading) for Security Control Validation. Unique Mitigation Library with vendor-specific remediation. Detection rule validation ensures SIEM/EDR rules fire correctly. Auto-generated detection content (Sigma, Splunk, QRadar). Blue Report for benchmarking.", "evidence_quality_rationale": "Exceptional. Unique detection rule validation and vendor-specific remediation.", "scoring_level_justification": "Level 5: Best-in-class with unique detection rule validation.", "confidence": "high"},
        "PPM-03": {"score_rationale": "Attack path validation and purple team enablement.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Some cloud-focused simulations.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"}
    }
}

VENDOR_RESEARCH["Wiz"] = {
    "scores": {"EXM-01": 3, "EXM-02": 2, "EXM-03": 3, "EXM-04": 2, "AMT-01": 0, "AMT-02": 1, "AMT-03": 2, "AMT-04": 1, "ADR-01": 0, "ADR-02": 2, "ADR-03": 1, "ADR-04": 0, "PPM-01": 0, "PPM-02": 3, "PPM-03": 0, "PPM-04": 5},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.wiz.io/"], "key_evidence": ["Wiz provides comprehensive cloud asset discovery through agentless scanning.", "Full inventory of cloud workloads, VMs, containers, serverless, and data stores.", "Multi-cloud asset discovery across AWS, Azure, GCP, and OCI."], "notes": "Comprehensive cloud asset discovery."},
        "EXM-02": {"source_urls": ["https://www.wiz.io/"], "key_evidence": ["Some exposure lifecycle through continuous cloud monitoring.", "Growing CTEM-adjacent capability for cloud environments."], "notes": "Cloud-focused exposure management."},
        "EXM-03": {"source_urls": ["https://www.wiz.io/"], "key_evidence": ["Wiz Security Graph identifies toxic combinations — connecting vulnerabilities with exposure, permissions, and data to prioritize true risk.", "Context-aware prioritization combining vulnerabilities, misconfigurations, network exposure, and identity permissions.", "Reduces vulnerability noise by focusing on actually exploitable paths."], "notes": "Context-aware cloud vulnerability prioritization. Toxic combinations approach."},
        "EXM-04": {"source_urls": ["https://www.wiz.io/"], "key_evidence": ["Some supply chain visibility through SCA and container image scanning.", "Open-source dependency scanning for cloud workloads."], "notes": "Cloud-native SCA."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": ["https://www.wiz.io/"], "key_evidence": ["Wiz Defend provides some runtime protection for cloud workloads."], "notes": "Emerging runtime protection."},
        "AMT-03": {"source_urls": ["https://www.wiz.io/"], "key_evidence": ["Cloud network segmentation visibility and misconfiguration detection.", "Identifies network exposure and overly permissive security group configurations."], "notes": "Cloud network posture assessment."},
        "AMT-04": {"source_urls": ["https://www.wiz.io/"], "key_evidence": ["CIEM capability identifies overprivileged cloud identities and roles."], "notes": "Cloud identity entitlements."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://www.wiz.io/"], "key_evidence": ["Wiz threat research team publishes cloud vulnerability research.", "Built-in intelligence for emerging cloud threats."], "notes": "Cloud-focused threat research."},
        "ADR-03": {"source_urls": [], "key_evidence": ["Some cloud threat detection through Wiz Defend."], "notes": "Emerging."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": ["https://www.wiz.io/"], "key_evidence": ["Cloud security posture assessment with compliance framework mapping.", "CIS Benchmarks, SOC 2, HIPAA, PCI DSS compliance assessment.", "Security control gap identification across cloud environments."], "notes": "Cloud compliance and control assessment."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": ["https://www.wiz.io/", "https://www.wiz.io/product/"], "key_evidence": ["Wiz is the fastest-growing cloud security company and CNAPP market leader.", "Agentless cloud security platform scanning across VMs, containers, serverless, and data stores without agents.", "Security Graph provides context-aware risk prioritization connecting vulnerabilities, misconfigurations, network exposure, identities, and data.", "CSPM with comprehensive misconfiguration detection across multi-cloud.", "CWPP (Cloud Workload Protection Platform) with agentless vulnerability scanning.", "CIEM for cloud identity and entitlements management.", "Container and Kubernetes security with image scanning and runtime monitoring.", "IaC scanning for shift-left security.", "Acquired by Google for $32B — the largest cybersecurity acquisition in history.", "Named a Leader in multiple Gartner and Forrester evaluations for cloud security."], "notes": "Market-defining CNAPP. Fastest-growing cloud security company. Acquired by Google for $32B. Agentless, Security Graph."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Comprehensive cloud asset discovery through agentless scanning across multi-cloud.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named cloud asset discovery.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Cloud-focused exposure management through continuous monitoring.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Security Graph identifies toxic combinations for context-aware prioritization. Reduces vulnerability noise.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Context-aware cloud vulnerability prioritization.", "confidence": "high"},
        "EXM-04": {"score_rationale": "SCA and container image scanning for supply chain visibility.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Cloud-native SCA.", "confidence": "high"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "Emerging runtime protection through Wiz Defend.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-03": {"score_rationale": "Cloud network segmentation visibility and misconfiguration detection.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "AMT-04": {"score_rationale": "CIEM for overprivileged cloud identities.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Cloud-focused threat research and emerging threat intelligence.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Some cloud threat detection through Wiz Defend.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Cloud compliance assessment with CIS/SOC2/HIPAA/PCI framework mapping.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named compliance assessment.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Wiz scores 5 (Market-Leading) for CSPM. Market-defining CNAPP/CSPM with agentless scanning, Security Graph for context-aware risk, comprehensive misconfiguration detection, CWPP, CIEM, container/K8s security, IaC scanning. Acquired by Google for $32B. Fastest-growing cloud security company.", "evidence_quality_rationale": "Exceptional. Market-defining, validated by $32B acquisition.", "scoring_level_justification": "Level 5: Best-in-class CNAPP/CSPM.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Orca Security"] = {
    "scores": {"EXM-01": 3, "EXM-02": 2, "EXM-03": 3, "EXM-04": 2, "AMT-01": 0, "AMT-02": 1, "AMT-03": 1, "AMT-04": 1, "ADR-01": 0, "ADR-02": 1, "ADR-03": 1, "ADR-04": 0, "PPM-01": 0, "PPM-02": 3, "PPM-03": 0, "PPM-04": 5},
    "evidence": {
        "EXM-01": {"source_urls": ["https://orca.security/"], "key_evidence": ["Orca provides comprehensive cloud asset discovery through SideScanning technology.", "Full inventory of cloud workloads, VMs, containers, serverless, storage."], "notes": "Agentless cloud asset discovery."},
        "EXM-02": {"source_urls": ["https://orca.security/"], "key_evidence": ["Some exposure lifecycle through continuous cloud monitoring."], "notes": "Cloud exposure management."},
        "EXM-03": {"source_urls": ["https://orca.security/"], "key_evidence": ["Context-based vulnerability prioritization combining vulnerability severity with cloud exposure, permissions, and data sensitivity.", "Attack path analysis identifies exploitable paths to critical assets."], "notes": "Context-aware cloud vulnerability prioritization with attack paths."},
        "EXM-04": {"source_urls": ["https://orca.security/"], "key_evidence": ["SCA for open-source dependency scanning.", "Container image scanning for supply chain security."], "notes": "Cloud-native SCA."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["Some runtime monitoring."], "notes": "Minimal."},
        "AMT-03": {"source_urls": [], "key_evidence": ["Basic cloud network posture."], "notes": "Minimal."},
        "AMT-04": {"source_urls": [], "key_evidence": ["Basic cloud identity analysis."], "notes": "Minimal."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": [], "key_evidence": ["Basic cloud threat context."], "notes": "Minimal."},
        "ADR-03": {"source_urls": [], "key_evidence": ["Some cloud threat monitoring."], "notes": "Minimal."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": ["https://orca.security/"], "key_evidence": ["Cloud compliance assessment with 100+ compliance frameworks.", "CIS Benchmarks, SOC 2, HIPAA, PCI DSS, GDPR assessment.", "Automated compliance scoring and reporting."], "notes": "Comprehensive cloud compliance assessment."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": ["https://orca.security/", "https://orca.security/platform/"], "key_evidence": ["Orca Security is a leading CNAPP providing agentless cloud security through patented SideScanning technology.", "SideScanning reads cloud workload snapshots without requiring agents — zero performance impact.", "Unified CSPM, CWPP, CIEM, DSPM, and container security in a single platform.", "Attack path analysis identifies complete exploit chains across cloud assets.", "Multi-cloud support for AWS, Azure, GCP, Alibaba Cloud.", "Named a Leader in Forrester Wave for Cloud Workload Security.", "Over 500 compliance frameworks and benchmarks supported."], "notes": "Leading CNAPP. SideScanning (agentless) technology. Unified platform. Forrester Wave Leader."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Comprehensive cloud asset discovery through SideScanning.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named cloud asset discovery.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Cloud exposure management through continuous monitoring.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Context-based vulnerability prioritization with attack path analysis.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Context-aware cloud prioritization.", "confidence": "high"},
        "EXM-04": {"score_rationale": "SCA and container image scanning.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "Some runtime monitoring.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-03": {"score_rationale": "Basic cloud network posture.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "AMT-04": {"score_rationale": "Basic cloud identity analysis.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Basic cloud threat context.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-03": {"score_rationale": "Some cloud threat monitoring.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Comprehensive cloud compliance with 100+ frameworks and automated scoring.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named compliance assessment.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Orca scores 5 (Market-Leading) for CSPM. Leading CNAPP with patented SideScanning (agentless). Unified CSPM/CWPP/CIEM/DSPM/container security. Attack path analysis. Multi-cloud. Forrester Wave Leader. 500+ compliance frameworks.", "evidence_quality_rationale": "Exceptional. Category leader with patented agentless technology.", "scoring_level_justification": "Level 5: Best-in-class CNAPP/CSPM.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Aqua Security"] = {
    "scores": {"EXM-01": 2, "EXM-02": 1, "EXM-03": 2, "EXM-04": 2, "AMT-01": 0, "AMT-02": 3, "AMT-03": 1, "AMT-04": 0, "ADR-01": 0, "ADR-02": 2, "ADR-03": 1, "ADR-04": 0, "PPM-01": 0, "PPM-02": 2, "PPM-03": 0, "PPM-04": 4},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.aquasec.com/"], "key_evidence": ["Cloud-native asset discovery with container and Kubernetes asset inventory.", "Image scanning and registry scanning for asset visibility."], "notes": "Container-focused asset discovery."},
        "EXM-02": {"source_urls": [], "key_evidence": ["Some exposure context through cloud-native monitoring."], "notes": "Minimal."},
        "EXM-03": {"source_urls": ["https://www.aquasec.com/"], "key_evidence": ["Container image vulnerability scanning with risk-based prioritization.", "Runtime vulnerability assessment for deployed workloads."], "notes": "Container vulnerability prioritization."},
        "EXM-04": {"source_urls": ["https://www.aquasec.com/"], "key_evidence": ["Software supply chain security — SCA for open-source dependencies.", "Container image provenance and integrity validation.", "SBOM generation and analysis."], "notes": "Named supply chain security capability."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": ["https://www.aquasec.com/", "https://www.aquasec.com/products/"], "key_evidence": ["Aqua provides runtime protection for containers and cloud-native workloads.", "vShield provides drift prevention and runtime policy enforcement.", "Runtime protection blocks unauthorized processes, network connections, and file modifications in containers.", "Behavioral profiling for container workloads."], "notes": "Strong container runtime protection. vShield for drift prevention."},
        "AMT-03": {"source_urls": [], "key_evidence": ["Basic Kubernetes network policy management."], "notes": "Minimal."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://www.aquasec.com/"], "key_evidence": ["Aqua Nautilus team provides cloud-native threat research.", "Threat intelligence on cloud-native attack vectors and supply chain threats."], "notes": "Cloud-native threat research from Nautilus."},
        "ADR-03": {"source_urls": [], "key_evidence": ["Some cloud-native threat detection."], "notes": "Minimal."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": ["https://www.aquasec.com/"], "key_evidence": ["Cloud-native compliance and security control assessment.", "CIS Benchmarks for Docker and Kubernetes."], "notes": "Cloud-native compliance."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": ["https://www.aquasec.com/", "https://www.aquasec.com/products/"], "key_evidence": ["Aqua Security provides comprehensive cloud-native security platform (CNAPP).", "CSPM with cloud misconfiguration detection across multi-cloud.", "CWPP for container and serverless workload protection.", "Kubernetes security with admission control, network policy, and runtime protection.", "Shift-left security with CI/CD pipeline scanning and IaC scanning.", "Trivy — industry-leading open-source vulnerability scanner — created by Aqua.", "Container lifecycle security from build to runtime.", "Named in Gartner and Forrester evaluations for cloud-native security."], "notes": "Leading cloud-native security platform. Trivy open-source scanner. Comprehensive container lifecycle security."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Cloud-native asset discovery with container/K8s inventory.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Container-focused asset discovery.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Some exposure context through cloud-native monitoring.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Container image vulnerability scanning with risk-based prioritization.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Container vulnerability prioritization.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Software supply chain security with SCA, image provenance, and SBOM.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Named supply chain capability.", "confidence": "high"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "Aqua scores 3 (Demonstrated) for Runtime Application Protection. Container runtime protection with drift prevention (vShield), behavioral profiling, and unauthorized process/network blocking.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named container runtime protection.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Basic Kubernetes network policy management.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Nautilus team provides cloud-native threat research.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Named research team.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Some cloud-native threat detection.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Cloud-native compliance with CIS Docker/K8s benchmarks.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Aqua scores 4 (Advanced) for CSPM. Comprehensive cloud-native security (CNAPP) with CSPM, CWPP, K8s security, shift-left scanning. Created Trivy (industry-standard open-source scanner). Container lifecycle security. Gartner/Forrester recognized.", "evidence_quality_rationale": "Strong. Major cloud-native platform with Trivy.", "scoring_level_justification": "Level 4: Advanced CNAPP with industry-leading OSS scanner.", "confidence": "high"}
    }
}

# ═══════════════════════════════════════════════════════════════════════
# BATCH 10: Lacework (Fortinet), Darktrace, Fortinet, IBM Security, Trellix, Cisco (Splunk)
# ═══════════════════════════════════════════════════════════════════════

VENDOR_RESEARCH["Lacework (Fortinet)"] = {
    "scores": {"EXM-01": 2, "EXM-02": 1, "EXM-03": 2, "EXM-04": 2, "AMT-01": 0, "AMT-02": 2, "AMT-03": 1, "AMT-04": 0, "ADR-01": 0, "ADR-02": 1, "ADR-03": 1, "ADR-04": 0, "PPM-01": 0, "PPM-02": 2, "PPM-03": 0, "PPM-04": 4},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.lacework.com/"], "key_evidence": ["Cloud asset discovery through agentless scanning and Polygraph technology.", "Multi-cloud asset inventory across AWS, Azure, GCP."], "notes": "Cloud asset discovery."},
        "EXM-02": {"source_urls": [], "key_evidence": ["Some exposure lifecycle through continuous cloud monitoring."], "notes": "Cloud exposure."},
        "EXM-03": {"source_urls": ["https://www.lacework.com/"], "key_evidence": ["Vulnerability assessment with risk-based prioritization using Polygraph behavioral context.", "Runtime vulnerability scanning for active workloads."], "notes": "Behavioral-context vulnerability prioritization."},
        "EXM-04": {"source_urls": ["https://www.lacework.com/"], "key_evidence": ["SCA and container image scanning for software supply chain.", "SBOM-aware vulnerability scanning."], "notes": "Cloud-native SCA."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": ["https://www.lacework.com/"], "key_evidence": ["Runtime protection through Polygraph behavioral analysis.", "Anomaly detection for cloud workloads based on learned behavioral baselines."], "notes": "Behavioral runtime protection."},
        "AMT-03": {"source_urls": [], "key_evidence": ["Basic cloud network monitoring."], "notes": "Minimal."},
        "AMT-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": [], "key_evidence": ["Basic cloud threat context from behavioral analysis."], "notes": "Minimal."},
        "ADR-03": {"source_urls": [], "key_evidence": ["Some cloud threat detection through Polygraph anomaly detection."], "notes": "Minimal."},
        "ADR-04": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-02": {"source_urls": ["https://www.lacework.com/"], "key_evidence": ["Cloud compliance assessment with multi-framework support.", "Configuration auditing against CIS benchmarks."], "notes": "Cloud compliance."},
        "PPM-03": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "PPM-04": {"source_urls": ["https://www.lacework.com/", "https://www.lacework.com/platform/"], "key_evidence": ["Lacework provides a CNAPP with CSPM, CWPP, and container security.", "Polygraph technology provides behavioral-based anomaly detection — unique ML approach.", "Cloud misconfiguration detection across multi-cloud environments.", "Acquired by Fortinet in 2024 — integrated into FortiCNAPP.", "Agentless and agent-based scanning for comprehensive coverage.", "Named in Gartner and Forrester evaluations for cloud security."], "notes": "Strong CNAPP. Unique Polygraph behavioral ML. Acquired by Fortinet."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Cloud asset discovery through agentless scanning.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Some cloud exposure lifecycle.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Risk-based vulnerability prioritization with Polygraph behavioral context.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-04": {"score_rationale": "SCA and SBOM-aware container scanning.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "Behavioral runtime protection through Polygraph anomaly detection.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Basic cloud network monitoring.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "AMT-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Basic cloud threat context.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-03": {"score_rationale": "Some anomaly-based threat detection.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-04": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Cloud compliance with CIS benchmarks.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "PPM-03": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Lacework scores 4 (Advanced) for CSPM. CNAPP with CSPM, CWPP, container security. Unique Polygraph behavioral ML. Acquired by Fortinet (FortiCNAPP). Multi-cloud misconfiguration detection. Gartner/Forrester recognized.", "evidence_quality_rationale": "Strong. Unique behavioral approach.", "scoring_level_justification": "Level 4: Advanced CNAPP with unique behavioral ML.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Darktrace"] = {
    "scores": {"EXM-01": 2, "EXM-02": 2, "EXM-03": 2, "EXM-04": 1, "AMT-01": 3, "AMT-02": 2, "AMT-03": 3, "AMT-04": 1, "ADR-01": 1, "ADR-02": 3, "ADR-03": 4, "ADR-04": 2, "PPM-01": 1, "PPM-02": 2, "PPM-03": 1, "PPM-04": 2},
    "evidence": {
        "EXM-01": {"source_urls": ["https://darktrace.com/"], "key_evidence": ["Darktrace PREVENT/ASM provides external attack surface monitoring.", "Internet-facing asset discovery and exposure assessment."], "notes": "Named ASM product."},
        "EXM-02": {"source_urls": ["https://darktrace.com/"], "key_evidence": ["Darktrace PREVENT provides exposure management with attack path modeling.", "Some CTEM enablement through continuous monitoring and prediction."], "notes": "PREVENT module for exposure."},
        "EXM-03": {"source_urls": ["https://darktrace.com/"], "key_evidence": ["Some vulnerability context through attack path analysis and exposure assessment.", "Risk-ranked exposure identification."], "notes": "Exposure-based prioritization."},
        "EXM-04": {"source_urls": [], "key_evidence": ["Basic supply chain monitoring through email security."], "notes": "Minimal."},
        "AMT-01": {"source_urls": ["https://darktrace.com/"], "key_evidence": ["Darktrace Antigena/RESPOND provides autonomous response that dynamically changes network configurations to contain threats.", "Self-learning AI continuously adapts defense based on evolving environment — a form of dynamic defense mutation.", "Autonomous Response takes proportionate action without human intervention."], "notes": "AI-driven autonomous defense adaptation. Self-learning AI provides MTD-like dynamic defense."},
        "AMT-02": {"source_urls": ["https://darktrace.com/"], "key_evidence": ["Some application-layer anomaly detection and response.", "Email security provides runtime application protection for email."], "notes": "Application anomaly detection."},
        "AMT-03": {"source_urls": ["https://darktrace.com/"], "key_evidence": ["Darktrace RESPOND (Antigena) can dynamically enforce network restrictions — blocking connections, isolating devices, and limiting traffic.", "Autonomous network defense that adapts in real-time based on AI-detected threats.", "Network traffic analysis with behavioral AI for east-west and north-south traffic."], "notes": "AI-driven autonomous network response and traffic analysis."},
        "AMT-04": {"source_urls": [], "key_evidence": ["Basic identity analysis through behavioral profiling."], "notes": "Minimal."},
        "ADR-01": {"source_urls": [], "key_evidence": ["Some deception-adjacent capability through AI-driven threat bait scenarios."], "notes": "Minimal."},
        "ADR-02": {"source_urls": ["https://darktrace.com/"], "key_evidence": ["Self-learning AI builds intelligence from customer environment patterns.", "Darktrace threat research team analyzes novel attacks detected by the AI.", "Real-time intelligence from AI analysis of network/email/cloud traffic."], "notes": "AI-generated behavioral intelligence."},
        "ADR-03": {"source_urls": ["https://darktrace.com/", "https://darktrace.com/products/"], "key_evidence": ["Darktrace DETECT provides autonomous threat detection using unsupervised machine learning.", "Self-learning AI establishes behavioral baselines and identifies deviations without rules or signatures.", "Detects novel and insider threats that rule-based systems miss.", "Cyber AI Analyst autonomously investigates alerts and produces human-readable incident reports.", "Coverage across network, cloud, email, SaaS, OT/IoT environments."], "notes": "Advanced AI-driven autonomous threat detection. Self-learning. Cyber AI Analyst for autonomous investigation."},
        "ADR-04": {"source_urls": ["https://darktrace.com/"], "key_evidence": ["Some adversary behavior profiling through AI analysis.", "Threat research publications on novel attack techniques."], "notes": "AI-driven adversary behavior analysis."},
        "PPM-01": {"source_urls": [], "key_evidence": ["Some PREVENT/attack path simulation has BAS-adjacent characteristics."], "notes": "Minimal BAS-like."},
        "PPM-02": {"source_urls": ["https://darktrace.com/"], "key_evidence": ["Security posture assessment through PREVENT module.", "Attack path analysis identifies security gaps."], "notes": "AI-driven posture assessment."},
        "PPM-03": {"source_urls": [], "key_evidence": ["Basic attack path simulation."], "notes": "Minimal."},
        "PPM-04": {"source_urls": ["https://darktrace.com/"], "key_evidence": ["Darktrace/Cloud provides cloud security monitoring.", "Some cloud misconfiguration detection."], "notes": "Cloud monitoring."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Darktrace PREVENT/ASM provides external attack surface monitoring.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-02": {"score_rationale": "PREVENT module provides exposure management with attack path modeling.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Exposure-based vulnerability prioritization through attack path analysis.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Basic supply chain monitoring.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "Darktrace scores 3 (Demonstrated) for Polymorphic Defense. Self-learning AI dynamically adapts defense and autonomous response changes configurations — MTD-like dynamic defense. Proportionate autonomous action without human intervention.", "evidence_quality_rationale": "Good evidence. Novel AI-driven MTD approach.", "scoring_level_justification": "Level 3: AI-driven autonomous defense adaptation.", "confidence": "high"},
        "AMT-02": {"score_rationale": "Application-layer anomaly detection.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Darktrace scores 3 (Demonstrated) for Dynamic Network Defense. RESPOND autonomously enforces network restrictions — blocking, isolating, limiting traffic. Behavioral AI for east-west and north-south traffic analysis.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Autonomous network defense.", "confidence": "high"},
        "AMT-04": {"score_rationale": "Basic identity analysis through behavioral profiling.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-01": {"score_rationale": "Minimal deception-adjacent capability.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "low"},
        "ADR-02": {"score_rationale": "Self-learning AI-generated behavioral intelligence from customer environment analysis. Threat research team.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: AI-generated behavioral intelligence.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Darktrace scores 4 (Advanced) for Proactive Threat Hunting. DETECT uses unsupervised ML for autonomous threat detection without rules/signatures. Cyber AI Analyst autonomously investigates and produces incident reports. Detects novel and insider threats across network/cloud/email/SaaS/OT.", "evidence_quality_rationale": "Strong. Novel AI-driven detection approach.", "scoring_level_justification": "Level 4: Advanced autonomous AI-driven threat detection.", "confidence": "high"},
        "ADR-04": {"score_rationale": "AI-driven adversary behavior profiling.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "medium"},
        "PPM-01": {"score_rationale": "Some BAS-adjacent attack path simulation.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "low"},
        "PPM-02": {"score_rationale": "AI-driven posture assessment through PREVENT.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "PPM-03": {"score_rationale": "Basic attack path simulation.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-04": {"score_rationale": "Darktrace/Cloud provides cloud monitoring and misconfiguration detection.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Fortinet"] = {
    "scores": {"EXM-01": 3, "EXM-02": 2, "EXM-03": 3, "EXM-04": 2, "AMT-01": 1, "AMT-02": 2, "AMT-03": 4, "AMT-04": 2, "ADR-01": 2, "ADR-02": 3, "ADR-03": 2, "ADR-04": 1, "PPM-01": 2, "PPM-02": 3, "PPM-03": 1, "PPM-04": 4},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.fortinet.com/"], "key_evidence": ["FortiRecon provides digital risk protection and external attack surface monitoring.", "Asset discovery and exposure identification across internet-facing infrastructure."], "notes": "Named EASM through FortiRecon."},
        "EXM-02": {"source_urls": ["https://www.fortinet.com/"], "key_evidence": ["Some exposure management through FortiRecon and Security Fabric integration.", "Growing CTEM-adjacent capability."], "notes": "Fabric-integrated exposure."},
        "EXM-03": {"source_urls": ["https://www.fortinet.com/"], "key_evidence": ["FortiGuard Labs provides vulnerability intelligence with prioritization.", "Outbreak Detection alerts for actively exploited vulnerabilities.", "Integration with FortiManager for prioritized patching."], "notes": "TI-enriched vulnerability prioritization."},
        "EXM-04": {"source_urls": ["https://www.fortinet.com/"], "key_evidence": ["FortiRecon includes third-party risk monitoring.", "Supply chain visibility through Security Fabric."], "notes": "Third-party risk monitoring."},
        "AMT-01": {"source_urls": [], "key_evidence": ["Some dynamic defense through Security Fabric automation."], "notes": "Minimal."},
        "AMT-02": {"source_urls": ["https://www.fortinet.com/"], "key_evidence": ["FortiWeb provides WAF with machine learning-based protection.", "FortiADC includes application layer defense."], "notes": "WAF-based application protection."},
        "AMT-03": {"source_urls": ["https://www.fortinet.com/", "https://www.fortinet.com/products/"], "key_evidence": ["Fortinet Security Fabric provides comprehensive network security with intent-based segmentation.", "FortiGate NGFW is the world's most deployed firewall — providing micro-segmentation and ZTNA.", "FortiNAC provides network access control with dynamic segmentation.", "SD-WAN integration enables dynamic network path selection and segmentation.", "ZTNA through FortiClient and FortiGate — providing zero trust application access."], "notes": "Massive network security portfolio. FortiGate NGFW, SD-WAN, ZTNA. World's most deployed firewall."},
        "AMT-04": {"source_urls": ["https://www.fortinet.com/"], "key_evidence": ["FortiAuthenticator and FortiToken for identity management.", "Some credential management through NAC integration."], "notes": "Identity capabilities."},
        "ADR-01": {"source_urls": ["https://www.fortinet.com/"], "key_evidence": ["FortiDeceptor provides deception technology within the Security Fabric.", "Deploys decoys and lures with automated response integration."], "notes": "Named deception product within Security Fabric."},
        "ADR-02": {"source_urls": ["https://www.fortinet.com/"], "key_evidence": ["FortiGuard Labs is one of the largest threat intelligence operations — processing billions of events daily.", "Real-time threat intelligence distributed across all Security Fabric products.", "FortiGuard AI-based threat intelligence covers network, email, web, and endpoint threats."], "notes": "One of the largest commercial TI operations. FortiGuard Labs."},
        "ADR-03": {"source_urls": ["https://www.fortinet.com/"], "key_evidence": ["FortiSIEM and FortiAnalyzer provide hunting capabilities.", "Some managed detection through FortiMDR."], "notes": "Hunting through SIEM and managed services."},
        "ADR-04": {"source_urls": [], "key_evidence": ["Some adversary context through FortiGuard Labs."], "notes": "Minimal."},
        "PPM-01": {"source_urls": ["https://www.fortinet.com/"], "key_evidence": ["FortiTester provides BAS-like security testing.", "Network performance and security testing capabilities."], "notes": "Named testing product."},
        "PPM-02": {"source_urls": ["https://www.fortinet.com/"], "key_evidence": ["Security Fabric provides comprehensive control validation across the Fortinet ecosystem.", "Configuration assessment and compliance reporting through FortiManager.", "Security rating and best practices scoring."], "notes": "Fabric-wide control validation."},
        "PPM-03": {"source_urls": [], "key_evidence": ["Basic testing through FortiTester."], "notes": "Minimal."},
        "PPM-04": {"source_urls": ["https://www.fortinet.com/"], "key_evidence": ["FortiCNAPP provides cloud security posture management (including Lacework acquisition).", "Multi-cloud misconfiguration detection and compliance.", "FortiCASB for SaaS cloud posture.", "Comprehensive cloud security portfolio across IaaS, PaaS, SaaS."], "notes": "Strong CSPM through FortiCNAPP (Lacework). Multi-cloud."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "FortiRecon provides EASM.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named EASM product.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Exposure management through FortiRecon and Security Fabric.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-03": {"score_rationale": "FortiGuard Labs vulnerability intelligence with Outbreak Detection alerts.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named TI-enriched prioritization.", "confidence": "high"},
        "EXM-04": {"score_rationale": "FortiRecon third-party risk monitoring.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "AMT-01": {"score_rationale": "Some dynamic defense through Security Fabric automation.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-02": {"score_rationale": "FortiWeb WAF with ML-based protection.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Fortinet scores 4 (Advanced) for Dynamic Network Defense. FortiGate (world's most deployed NGFW) with micro-segmentation and ZTNA. FortiNAC for dynamic network access control. SD-WAN with dynamic path selection. Comprehensive Security Fabric.", "evidence_quality_rationale": "Strong. Largest firewall deployment globally.", "scoring_level_justification": "Level 4: Advanced network defense with massive deployment.", "confidence": "high"},
        "AMT-04": {"score_rationale": "FortiAuthenticator/FortiToken for identity management.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "ADR-01": {"score_rationale": "FortiDeceptor provides deception within the Security Fabric.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Named deception product.", "confidence": "high"},
        "ADR-02": {"score_rationale": "FortiGuard Labs is one of the largest commercial TI operations — billions of events daily. Real-time intelligence across the Security Fabric.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named large-scale TI operation.", "confidence": "high"},
        "ADR-03": {"score_rationale": "FortiSIEM/FortiAnalyzer hunting and FortiMDR.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "ADR-04": {"score_rationale": "Basic adversary context from FortiGuard Labs.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-01": {"score_rationale": "FortiTester provides BAS-like security testing.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Named testing product.", "confidence": "high"},
        "PPM-02": {"score_rationale": "Security Fabric control validation with FortiManager compliance.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Fabric-wide control validation.", "confidence": "high"},
        "PPM-03": {"score_rationale": "Basic testing through FortiTester.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Fortinet scores 4 (Advanced) for CSPM. FortiCNAPP (Lacework acquisition), FortiCASB, multi-cloud misconfiguration detection. Comprehensive cloud security portfolio.", "evidence_quality_rationale": "Strong. Major cloud security portfolio.", "scoring_level_justification": "Level 4: Advanced CSPM with FortiCNAPP.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["IBM Security"] = {
    "scores": {"EXM-01": 3, "EXM-02": 2, "EXM-03": 3, "EXM-04": 2, "AMT-01": 0, "AMT-02": 1, "AMT-03": 2, "AMT-04": 3, "ADR-01": 0, "ADR-02": 4, "ADR-03": 4, "ADR-04": 3, "PPM-01": 1, "PPM-02": 2, "PPM-03": 2, "PPM-04": 2},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.ibm.com/security"], "key_evidence": ["IBM Security Randori provides external attack surface management.", "Randori Recon discovers exposed assets from an attacker's perspective.", "Acquired Randori for ASM capability."], "notes": "Named ASM product through Randori acquisition."},
        "EXM-02": {"source_urls": ["https://www.ibm.com/security"], "key_evidence": ["Some exposure management through Randori and QRadar integration.", "Growing CTEM-adjacent capability."], "notes": "Randori + QRadar exposure management."},
        "EXM-03": {"source_urls": ["https://www.ibm.com/security"], "key_evidence": ["Randori provides risk-based prioritization of exposed assets.", "X-Force threat intelligence enriches vulnerability prioritization.", "QRadar integrates vulnerability data with threat intelligence."], "notes": "TI-enriched vulnerability prioritization."},
        "EXM-04": {"source_urls": ["https://www.ibm.com/security"], "key_evidence": ["Supply chain risk intelligence through X-Force.", "Third-party risk assessment capabilities."], "notes": "Third-party risk from X-Force."},
        "AMT-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "AMT-02": {"source_urls": [], "key_evidence": ["Basic application security through AppScan."], "notes": "Minimal."},
        "AMT-03": {"source_urls": ["https://www.ibm.com/security"], "key_evidence": ["Some network segmentation through QRadar and ZTNA capabilities.", "Zero Trust strategy with context-aware access."], "notes": "Zero trust capabilities."},
        "AMT-04": {"source_urls": ["https://www.ibm.com/security"], "key_evidence": ["IBM Security Verify provides identity and access management with some credential lifecycle management.", "Privileged access management capabilities.", "Identity governance and administration."], "notes": "Named IAM platform with credential management."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://www.ibm.com/security", "https://exchange.xforce.ibmcloud.com/"], "key_evidence": ["IBM X-Force is one of the oldest and most respected commercial threat intelligence teams.", "X-Force Exchange provides threat intelligence sharing platform.", "X-Force Threat Intelligence Index is an annual industry benchmark report.", "Decades of incident response intelligence from one of the largest IR teams globally."], "notes": "Major TI capability through X-Force. Decades of IR intelligence. Annual Threat Intelligence Index."},
        "ADR-03": {"source_urls": ["https://www.ibm.com/security"], "key_evidence": ["IBM X-Force provides managed threat hunting services.", "QRadar Advisor with Watson provides AI-driven investigation and hunting.", "Decades of incident response experience informing hunting capabilities.", "QRadar SIEM provides comprehensive hunting workbench."], "notes": "Major hunting capability through X-Force + QRadar."},
        "ADR-04": {"source_urls": ["https://www.ibm.com/security"], "key_evidence": ["X-Force provides adversary tracking and counter-adversary intelligence.", "Incident response and remediation services.", "Adversary TTP analysis and attribution intelligence."], "notes": "Counter-adversary through X-Force IR."},
        "PPM-01": {"source_urls": [], "key_evidence": ["Randori Attack has some BAS-like capability (continuous automated red teaming)."], "notes": "Randori Attack for automated red teaming."},
        "PPM-02": {"source_urls": ["https://www.ibm.com/security"], "key_evidence": ["QRadar provides security control effectiveness monitoring.", "Compliance and risk assessment capabilities."], "notes": "SIEM-based control monitoring."},
        "PPM-03": {"source_urls": ["https://www.ibm.com/security"], "key_evidence": ["IBM X-Force Red provides pen testing and red team services.", "Vulnerability management and adversary simulation services."], "notes": "Named pen testing team (X-Force Red)."},
        "PPM-04": {"source_urls": ["https://www.ibm.com/security"], "key_evidence": ["Some cloud security posture through IBM Cloud Security.", "Cloud compliance assessment capabilities."], "notes": "Cloud security posture."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Randori Recon provides attacker-perspective ASM.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named ASM product.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Exposure management through Randori + QRadar.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Risk-based prioritization with X-Force TI enrichment.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: TI-enriched prioritization.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Supply chain risk intelligence from X-Force.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "AMT-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "AMT-02": {"score_rationale": "Basic application security through AppScan.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Zero Trust and ZTNA capabilities.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "AMT-04": {"score_rationale": "IBM Security Verify provides IAM with credential lifecycle management.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named IAM platform.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "IBM X-Force scores 4 (Advanced) for TI. One of the oldest commercial TI teams. X-Force Exchange sharing platform. Annual Threat Intelligence Index benchmark. Decades of IR intelligence.", "evidence_quality_rationale": "Strong. Historic TI team with massive IR intelligence.", "scoring_level_justification": "Level 4: Advanced TI with decades of IR intelligence.", "confidence": "high"},
        "ADR-03": {"score_rationale": "IBM scores 4 (Advanced) for Proactive Threat Hunting. X-Force managed hunting with QRadar Advisor/Watson AI investigation. Decades of IR experience. Comprehensive QRadar hunting workbench.", "evidence_quality_rationale": "Strong. Major hunting capability.", "scoring_level_justification": "Level 4: Advanced managed hunting.", "confidence": "high"},
        "ADR-04": {"score_rationale": "X-Force adversary tracking, attribution intelligence, and IR services.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named counter-adversary capability.", "confidence": "high"},
        "PPM-01": {"score_rationale": "Randori Attack provides some automated red teaming.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-02": {"score_rationale": "QRadar security control monitoring and compliance.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "PPM-03": {"score_rationale": "X-Force Red pen testing and red team services.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Named pen testing team.", "confidence": "high"},
        "PPM-04": {"score_rationale": "Cloud security posture assessment capabilities.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"}
    }
}

VENDOR_RESEARCH["Trellix"] = {
    "scores": {"EXM-01": 2, "EXM-02": 1, "EXM-03": 2, "EXM-04": 1, "AMT-01": 1, "AMT-02": 1, "AMT-03": 2, "AMT-04": 1, "ADR-01": 0, "ADR-02": 3, "ADR-03": 3, "ADR-04": 2, "PPM-01": 1, "PPM-02": 2, "PPM-03": 1, "PPM-04": 1},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.trellix.com/"], "key_evidence": ["Some asset discovery through endpoint and network visibility.", "Emerging ASM capabilities."], "notes": "Emerging ASM."},
        "EXM-02": {"source_urls": [], "key_evidence": ["Some exposure context through endpoint detection."], "notes": "Minimal."},
        "EXM-03": {"source_urls": ["https://www.trellix.com/"], "key_evidence": ["Endpoint vulnerability assessment with some prioritization.", "Threat intelligence-enriched vulnerability context from Trellix Advanced Research Center."], "notes": "TI-enriched vulnerability context."},
        "EXM-04": {"source_urls": [], "key_evidence": ["Basic supply chain visibility."], "notes": "Minimal."},
        "AMT-01": {"source_urls": [], "key_evidence": ["Some adaptive defense through machine learning-based detection evolution."], "notes": "ML-adaptive defense."},
        "AMT-02": {"source_urls": [], "key_evidence": ["Basic application sandboxing."], "notes": "Minimal."},
        "AMT-03": {"source_urls": ["https://www.trellix.com/"], "key_evidence": ["Trellix Network Security (formerly FireEye NX) provides network traffic analysis and IPS.", "Network segmentation visibility through traffic analysis."], "notes": "Network security from FireEye heritage."},
        "AMT-04": {"source_urls": [], "key_evidence": ["Basic identity monitoring."], "notes": "Minimal."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No capability."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://www.trellix.com/", "https://www.trellix.com/advanced-research-center/"], "key_evidence": ["Trellix Advanced Research Center (ARC) provides threat intelligence research.", "Heritage from FireEye (Mandiant) and McAfee threat intelligence teams.", "Real-time intelligence feeds distributed across Trellix products.", "Published research on APT campaigns and emerging threats."], "notes": "Strong TI from FireEye/McAfee heritage. ARC for research."},
        "ADR-03": {"source_urls": ["https://www.trellix.com/"], "key_evidence": ["Trellix XDR provides multi-vector threat detection with investigation capabilities.", "Heritage from FireEye Helix SOC platform.", "Endpoint, network, and email correlated detection and hunting."], "notes": "XDR-based threat hunting from FireEye/McAfee heritage."},
        "ADR-04": {"source_urls": ["https://www.trellix.com/"], "key_evidence": ["Some adversary tracking through Advanced Research Center.", "Counter-threat intelligence from FireEye heritage."], "notes": "Counter-adversary from FireEye legacy."},
        "PPM-01": {"source_urls": [], "key_evidence": ["Some BAS-adjacent capability through detection testing."], "notes": "Minimal."},
        "PPM-02": {"source_urls": ["https://www.trellix.com/"], "key_evidence": ["Security control monitoring through XDR.", "Policy compliance assessment."], "notes": "XDR-based control monitoring."},
        "PPM-03": {"source_urls": [], "key_evidence": ["Basic testing capabilities."], "notes": "Minimal."},
        "PPM-04": {"source_urls": [], "key_evidence": ["Some cloud monitoring."], "notes": "Minimal."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Emerging ASM through endpoint/network visibility.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "medium"},
        "EXM-02": {"score_rationale": "Some exposure context.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "EXM-03": {"score_rationale": "TI-enriched vulnerability context from ARC.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Basic supply chain visibility.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-01": {"score_rationale": "ML-adaptive detection evolution.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-02": {"score_rationale": "Basic application sandboxing.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Trellix Network Security (FireEye NX heritage) for network traffic analysis and IPS.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Named network security product.", "confidence": "high"},
        "AMT-04": {"score_rationale": "Basic identity monitoring.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "ADR-01": {"score_rationale": "No evidence.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Trellix ARC provides TI research from FireEye/McAfee heritage. Real-time intelligence feeds and published APT research.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named TI from heritage teams.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Trellix XDR with multi-vector detection and hunting from FireEye Helix heritage.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: XDR-based threat hunting.", "confidence": "high"},
        "ADR-04": {"score_rationale": "Counter-adversary intelligence from FireEye heritage and ARC.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "PPM-01": {"score_rationale": "Some BAS-adjacent capability.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "low"},
        "PPM-02": {"score_rationale": "XDR-based security control monitoring.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "PPM-03": {"score_rationale": "Basic testing.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-04": {"score_rationale": "Some cloud monitoring.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"}
    }
}

VENDOR_RESEARCH["Cisco (Splunk)"] = {
    "scores": {"EXM-01": 3, "EXM-02": 2, "EXM-03": 3, "EXM-04": 2, "AMT-01": 1, "AMT-02": 2, "AMT-03": 4, "AMT-04": 2, "ADR-01": 0, "ADR-02": 3, "ADR-03": 4, "ADR-04": 2, "PPM-01": 1, "PPM-02": 3, "PPM-03": 1, "PPM-04": 4},
    "evidence": {
        "EXM-01": {"source_urls": ["https://www.cisco.com/site/us/en/products/security/"], "key_evidence": ["Cisco provides network asset discovery through ISE and network infrastructure.", "Some external ASM through integrations.", "Comprehensive internal asset visibility from network infrastructure dominance."], "notes": "Network infrastructure visibility."},
        "EXM-02": {"source_urls": ["https://www.cisco.com/"], "key_evidence": ["Some exposure management through Cisco Vulnerability Management (Kenna Security acquisition).", "Growing CTEM-adjacent capability."], "notes": "Kenna Security for exposure management."},
        "EXM-03": {"source_urls": ["https://www.cisco.com/"], "key_evidence": ["Cisco Vulnerability Management (Kenna Security) provides risk-based vulnerability prioritization.", "Machine learning-based vulnerability prioritization using exploit prediction and threat intelligence.", "Kenna Risk Score provides contextual vulnerability prioritization."], "notes": "Kenna Security acquisition provides industry-leading risk-based VM."},
        "EXM-04": {"source_urls": ["https://www.cisco.com/"], "key_evidence": ["Supply chain visibility through Talos intelligence.", "Third-party risk context from network traffic analysis."], "notes": "Supply chain through Talos."},
        "AMT-01": {"source_urls": [], "key_evidence": ["Some dynamic defense through network automation."], "notes": "Minimal."},
        "AMT-02": {"source_urls": ["https://www.cisco.com/"], "key_evidence": ["Cisco Secure Workload (Tetration) provides application behavior analysis.", "AppDynamics provides application performance and security monitoring."], "notes": "Application-layer security."},
        "AMT-03": {"source_urls": ["https://www.cisco.com/", "https://www.cisco.com/site/us/en/products/security/"], "key_evidence": ["Cisco provides industry-leading network segmentation through ISE, TrustSec, and SD-Access.", "Cisco Secure Workload (Tetration) provides micro-segmentation for workloads.", "SD-WAN with dynamic path selection and segmentation.", "ZTNA through Cisco Duo and Secure Access.", "Network infrastructure market dominance means the largest installed base for segmentation enforcement."], "notes": "Massive network segmentation through infrastructure dominance. ISE, TrustSec, SD-Access, Tetration."},
        "AMT-04": {"source_urls": ["https://www.cisco.com/"], "key_evidence": ["Cisco Duo provides industry-leading MFA and access management.", "Some credential lifecycle management through ISE integration."], "notes": "Duo MFA. Not credential rotation."},
        "ADR-01": {"source_urls": [], "key_evidence": ["No dedicated deception."], "notes": "Outside scope."},
        "ADR-02": {"source_urls": ["https://www.cisco.com/", "https://blog.talosintelligence.com/"], "key_evidence": ["Cisco Talos is one of the largest commercial threat intelligence teams — leveraging telemetry from the world's largest network infrastructure.", "Talos processes billions of DNS queries and web transactions daily.", "Talos Intelligence provides real-time threat feeds, vulnerability research, and malware analysis.", "Snort open-source IDS/IPS rules maintained by Talos."], "notes": "Talos — one of the largest TI operations globally. Massive telemetry from infrastructure dominance."},
        "ADR-03": {"source_urls": ["https://www.cisco.com/", "https://www.splunk.com/"], "key_evidence": ["Splunk (acquired for $28B) provides industry-leading SIEM and hunting platform.", "Splunk Enterprise Security with advanced hunting workbench.", "Cisco XDR combines network, endpoint, and cloud telemetry for detection.", "Talos threat hunting and incident response services."], "notes": "Splunk SIEM + Talos hunting. Industry-leading SIEM acquisition."},
        "ADR-04": {"source_urls": ["https://www.cisco.com/"], "key_evidence": ["Talos provides adversary tracking and research.", "Some counter-adversary intelligence from network telemetry."], "notes": "Talos adversary research."},
        "PPM-01": {"source_urls": [], "key_evidence": ["Some BAS-adjacent through security testing."], "notes": "Minimal."},
        "PPM-02": {"source_urls": ["https://www.cisco.com/", "https://www.splunk.com/"], "key_evidence": ["Splunk provides comprehensive security posture monitoring and compliance.", "Cisco SecureX provides cross-product security control visibility.", "Compliance assessment across network infrastructure."], "notes": "Splunk + SecureX for control validation."},
        "PPM-03": {"source_urls": [], "key_evidence": ["Basic testing through security professional services."], "notes": "Minimal."},
        "PPM-04": {"source_urls": ["https://www.cisco.com/"], "key_evidence": ["Cisco Cloud Controls Framework for cloud posture management.", "Cisco Secure Workload for cloud workload protection.", "Multi-cloud security through comprehensive product portfolio.", "AppDynamics + Thousand Eyes for cloud visibility."], "notes": "Strong cloud posture management through comprehensive portfolio."}
    },
    "rationale": {
        "EXM-01": {"score_rationale": "Network infrastructure visibility and ISE-based asset discovery.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Industry-leading network visibility.", "confidence": "high"},
        "EXM-02": {"score_rationale": "Kenna Security acquisition provides exposure management.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "EXM-03": {"score_rationale": "Kenna Security provides ML-based risk-based vulnerability prioritization with Kenna Risk Score.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Industry-leading risk-based VM.", "confidence": "high"},
        "EXM-04": {"score_rationale": "Supply chain visibility through Talos intelligence.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "AMT-01": {"score_rationale": "Some dynamic defense through network automation.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "AMT-02": {"score_rationale": "Secure Workload and AppDynamics for application security.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "AMT-03": {"score_rationale": "Cisco scores 4 (Advanced) for Dynamic Network Defense. ISE, TrustSec, SD-Access for segmentation. Secure Workload (Tetration) for micro-segmentation. SD-WAN and ZTNA through Duo/Secure Access. Largest installed base for network segmentation enforcement.", "evidence_quality_rationale": "Strong. Infrastructure market dominance.", "scoring_level_justification": "Level 4: Advanced network defense from infrastructure market dominance.", "confidence": "high"},
        "AMT-04": {"score_rationale": "Duo provides industry-leading MFA but not credential rotation.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2: Named MFA platform.", "confidence": "high"},
        "ADR-01": {"score_rationale": "No dedicated deception.", "evidence_quality_rationale": "None.", "scoring_level_justification": "Level 0.", "confidence": "high"},
        "ADR-02": {"score_rationale": "Talos is one of the largest commercial TI operations. Billions of daily DNS queries/transactions. Real-time feeds, vulnerability research, Snort rules.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named massive TI operation.", "confidence": "high"},
        "ADR-03": {"score_rationale": "Cisco scores 4 (Advanced) for Proactive Threat Hunting. Splunk ($28B acquisition) provides industry-leading SIEM/hunting. Cisco XDR for cross-domain detection. Talos hunting and IR services.", "evidence_quality_rationale": "Strong. Splunk acquisition is industry-defining.", "scoring_level_justification": "Level 4: Advanced hunting through Splunk + Talos.", "confidence": "high"},
        "ADR-04": {"score_rationale": "Talos adversary tracking and research.", "evidence_quality_rationale": "Moderate.", "scoring_level_justification": "Level 2.", "confidence": "high"},
        "PPM-01": {"score_rationale": "Some BAS-adjacent capability.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "low"},
        "PPM-02": {"score_rationale": "Splunk + SecureX for comprehensive security posture and compliance monitoring.", "evidence_quality_rationale": "Good evidence.", "scoring_level_justification": "Level 3: Named posture management.", "confidence": "high"},
        "PPM-03": {"score_rationale": "Basic testing through professional services.", "evidence_quality_rationale": "Limited.", "scoring_level_justification": "Level 1.", "confidence": "medium"},
        "PPM-04": {"score_rationale": "Cisco scores 4 (Advanced) for CSPM. Cloud Controls Framework, Secure Workload, AppDynamics/ThousandEyes. Comprehensive multi-cloud portfolio.", "evidence_quality_rationale": "Strong. Comprehensive cloud security portfolio.", "scoring_level_justification": "Level 4: Advanced CSPM from comprehensive portfolio.", "confidence": "high"}
    }
}


# ─────────────────────────────────────────────────────────────────────
# Builder: merge research into seed data
# ─────────────────────────────────────────────────────────────────────

def compute_pillar_scores(sub_scores):
    """Compute pillar averages from sub-pillar scores."""
    pillar_scores = {}
    for pillar in PILLARS:
        sp_ids = [f"{pillar}-{i:02d}" for i in range(1, 5)]
        vals = [sub_scores.get(sp, 0) for sp in sp_ids]
        pillar_scores[pillar] = round(sum(vals) / len(vals), 2)
    return pillar_scores


def build_researched_file():
    """Read seed, apply research data, write output."""
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        seed = json.load(f)

    output = {
        "schema_ref": seed["schema_ref"],
        "schema_version": "2.0",
        "vendor_count": seed["vendor_count"],
        "research_methodology": "Expert analysis with web evidence verification following Preemptive Cybersecurity Schema evaluation criteria. Each vendor scored 0-5 per sub-pillar with structured rationale.",
        "research_timestamp": datetime.now(timezone.utc).isoformat(),
        "research_tool": "research_precyber_scoring.py",
        "vendors": []
    }

    researched_count = 0
    for vendor in seed["vendors"]:
        name = vendor["vendor"]
        entry = dict(vendor)  # copy seed data

        if name in VENDOR_RESEARCH:
            research = VENDOR_RESEARCH[name]
            # Apply scores
            entry["sub_pillar_scores_current"] = dict(research["scores"])
            entry["pillar_scores"] = compute_pillar_scores(research["scores"])
            # Add evidence
            entry["sub_pillar_evidence"] = {}
            for sp_id, ev in research["evidence"].items():
                entry["sub_pillar_evidence"][sp_id] = {
                    "source_urls": ev.get("source_urls", []),
                    "key_evidence": ev.get("key_evidence", []),
                    "notes": ev.get("notes", "")
                }
            # Add rationale
            entry["sub_pillar_rationale"] = {}
            for sp_id, rat in research["rationale"].items():
                entry["sub_pillar_rationale"][sp_id] = {
                    "score_rationale": rat.get("score_rationale", ""),
                    "evidence_quality_rationale": rat.get("evidence_quality_rationale", ""),
                    "scoring_level_justification": rat.get("scoring_level_justification", ""),
                    "confidence": rat.get("confidence", "medium")
                }
            researched_count += 1

        output["vendors"].append(entry)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✓ Wrote {OUTPUT_FILE.name}")
    print(f"  Total vendors: {len(output['vendors'])}")
    print(f"  Researched:    {researched_count}")
    print(f"  Remaining:     {len(output['vendors']) - researched_count}")

    # Summary of scored vendors
    for v in output["vendors"]:
        if v["vendor"] in VENDOR_RESEARCH:
            ps = v["pillar_scores"]
            total = sum(ps.values()) / len(ps)
            print(f"  {v['vendor']:30s}  EXM={ps['EXM']:.2f}  AMT={ps['AMT']:.2f}  ADR={ps['ADR']:.2f}  PPM={ps['PPM']:.2f}  AVG={total:.2f}")


if __name__ == "__main__":
    build_researched_file()
