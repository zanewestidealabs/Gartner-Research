"""
Generate Preemptive Cybersecurity Vendor Seed File
Creates the initial vendor list with zero scores for deep research.
"""
import json
from datetime import datetime

SCHEMA_REF = "Preemptive_Cybersecurity_Schema.json"
SCHEMA_VERSION = "1.0"

SUB_PILLAR_LABELS = {
    "EXM-01": "Attack Surface Management",
    "EXM-02": "Continuous Threat Exposure Management",
    "EXM-03": "Vulnerability Prioritization & Management",
    "EXM-04": "Third-Party & Supply Chain Exposure",
    "AMT-01": "Polymorphic & Morphing Defense",
    "AMT-02": "Runtime Application Protection",
    "AMT-03": "Dynamic Network & Infrastructure Defense",
    "AMT-04": "Identity & Credential Rotation",
    "ADR-01": "Deception Technology",
    "ADR-02": "Threat Intelligence Operationalization",
    "ADR-03": "Proactive Threat Hunting",
    "ADR-04": "Counter-Adversary Operations",
    "PPM-01": "Breach & Attack Simulation",
    "PPM-02": "Security Control Validation",
    "PPM-03": "Penetration Testing & Red Teaming",
    "PPM-04": "Cloud Security Posture Management",
}

# ── Vendor seed data ──────────────────────────────────────────────────
# Each vendor: (name, hq, region, specialization, is_startup, is_ai_first,
#               primary_capability, description, key_differentiators,
#               expected_coverage [list of sub-pillar codes])
VENDOR_SEEDS = [
    # ── EXM: Exposure Management ──
    ("Tenable", "Columbia, MD, USA", "North America", "Exposure Management",
     False, False, "EXM",
     "Exposure management platform covering vulnerability management, cloud security, and attack surface management.",
     "Tenable One platform unifying ASM, VM, and cloud security; Nessus heritage.",
     ["EXM-01", "EXM-02", "EXM-03", "EXM-04", "PPM-04"]),

    ("Qualys", "Foster City, CA, USA", "North America", "Vulnerability Management",
     False, False, "EXM",
     "Cloud-based vulnerability management, policy compliance, and asset discovery platform.",
     "Cloud-native agent architecture; VMDR with TruRisk scoring; broad asset coverage.",
     ["EXM-01", "EXM-03", "PPM-04"]),

    ("Rapid7", "Boston, MA, USA", "North America", "Vulnerability & Detection",
     False, False, "EXM",
     "Vulnerability management, detection & response, and cloud security platform.",
     "InsightVM with real risk scoring; Metasploit heritage for validation.",
     ["EXM-01", "EXM-03", "PPM-03", "PPM-04"]),

    ("CrowdStrike", "Austin, TX, USA", "Global", "Endpoint & Exposure",
     False, True, "EXM",
     "AI-native cybersecurity platform with exposure management, endpoint protection, and threat intelligence.",
     "Falcon platform with EASM, threat hunting (OverWatch), and AI-driven detection.",
     ["EXM-01", "EXM-02", "EXM-03", "ADR-02", "ADR-03"]),

    ("Palo Alto Networks", "Santa Clara, CA, USA", "Global", "Platform Security",
     False, True, "EXM",
     "Comprehensive security platform spanning network, cloud, and exposure management.",
     "Cortex Xpanse for ASM; Prisma Cloud for CSPM; XSIAM for AI-driven SOC.",
     ["EXM-01", "EXM-02", "EXM-03", "PPM-04", "ADR-02"]),

    ("Censys", "Ann Arbor, MI, USA", "North America", "Attack Surface Management",
     True, False, "EXM",
     "Internet-wide scanning and attack surface management platform.",
     "Comprehensive internet asset discovery; deep protocol scanning; exposure prioritization.",
     ["EXM-01", "EXM-02"]),

    ("CyCognito", "Palo Alto, CA, USA", "North America", "Attack Surface Management",
     True, True, "EXM",
     "Automated external attack surface management using attacker-perspective reconnaissance.",
     "Attacker-centric discovery; automated testing of discovered assets; risk prioritization.",
     ["EXM-01", "EXM-02", "EXM-03"]),

    ("Armis", "San Francisco, CA, USA", "North America", "Asset Intelligence",
     True, True, "EXM",
     "Agentless asset intelligence platform for managed, unmanaged, IoT, and OT devices.",
     "Agentless discovery across IT/OT/IoT; Armis Centrix platform; asset vulnerability mapping.",
     ["EXM-01", "EXM-02", "EXM-03"]),

    ("Axonius", "New York, NY, USA", "North America", "Cyber Asset Management",
     True, False, "EXM",
     "Cybersecurity asset management platform aggregating data from hundreds of sources.",
     "400+ adapter integrations; policy enforcement automation; SaaS management.",
     ["EXM-01", "EXM-03"]),

    ("JupiterOne", "Morrisville, NC, USA", "North America", "Cyber Asset Management",
     True, False, "EXM",
     "Cloud-native cyber asset attack surface management with graph-based relationships.",
     "Graph database for asset relationships; query-based security posture analysis.",
     ["EXM-01", "EXM-03", "PPM-04"]),

    ("XM Cyber", "Herzliya, Israel", "Global", "Exposure Management",
     True, True, "EXM",
     "Continuous exposure management with attack path analysis and remediation prioritization.",
     "Attack path modeling; business-critical asset focus; continuous validation.",
     ["EXM-01", "EXM-02", "EXM-03", "PPM-01", "PPM-03"]),

    ("Bitsight", "Boston, MA, USA", "North America", "Third-Party Risk",
     False, False, "EXM",
     "Security ratings platform for third-party risk management and cyber risk quantification.",
     "Security ratings with continuous monitoring; supply chain risk visibility; benchmarking.",
     ["EXM-04"]),

    ("SecurityScorecard", "New York, NY, USA", "North America", "Third-Party Risk",
     False, False, "EXM",
     "Security ratings and third-party risk management platform.",
     "A-F security ratings; attack surface intelligence; supply chain risk management.",
     ["EXM-01", "EXM-04"]),

    ("Panorays", "New York, NY, USA", "North America", "Third-Party Risk",
     True, True, "EXM",
     "AI-driven third-party security risk management platform.",
     "Automated security questionnaires; continuous monitoring; supply chain mapping.",
     ["EXM-04"]),

    # ── AMT: Automated Moving Target Defense ──
    ("Morphisec", "Be'er Sheva, Israel", "Global", "Moving Target Defense",
     True, False, "AMT",
     "Automated Moving Target Defense (AMTD) platform using memory morphing to prevent exploits.",
     "Patented Moving Target Defense technology; signatureless prevention; ultra-lightweight agent.",
     ["AMT-01", "AMT-02"]),

    ("RunSafe Security", "McLean, VA, USA", "North America", "Moving Target Defense",
     True, False, "AMT",
     "Software supply chain security and AMTD through binary code transformation.",
     "Alkemist platform for binary diversification; eliminates classes of memory exploits.",
     ["AMT-01", "AMT-02"]),

    ("Contrast Security", "Los Altos, CA, USA", "North America", "Application Security",
     True, False, "AMT",
     "Runtime application security with instrumentation-based RASP and IAST.",
     "Code-level runtime protection; DevSecOps integration; route intelligence.",
     ["AMT-02"]),

    ("Illumio", "Sunnyvale, CA, USA", "North America", "Micro-Segmentation",
     False, False, "AMT",
     "Zero trust segmentation platform for workload and network micro-segmentation.",
     "Real-time application dependency mapping; policy enforcement across hybrid environments.",
     ["AMT-03"]),

    ("Akamai (Guardicore)", "Cambridge, MA, USA", "Global", "Micro-Segmentation",
     False, False, "AMT",
     "Micro-segmentation and zero trust network security through Akamai Guardicore Segmentation.",
     "Process-level segmentation; deception capabilities; ransomware containment.",
     ["AMT-03", "ADR-01"]),

    ("Zscaler", "San Jose, CA, USA", "Global", "Zero Trust Network",
     False, True, "AMT",
     "Cloud-native zero trust platform providing secure access, threat protection, and data protection.",
     "Zero Trust Exchange architecture; inline inspection; SDP at scale.",
     ["AMT-03"]),

    ("CyberArk", "Newton, MA, USA", "Global", "Privileged Access Management",
     False, False, "AMT",
     "Identity security platform specializing in privileged access management and credential protection.",
     "Vault-based credential management; session isolation; secrets management; JIT access.",
     ["AMT-04"]),

    ("BeyondTrust", "Carlsbad, CA, USA", "North America", "Privileged Access Management",
     False, False, "AMT",
     "Privileged access management for secure remote access and endpoint privilege management.",
     "Privileged remote access; endpoint privilege management; secrets management.",
     ["AMT-04"]),

    ("Delinea", "San Francisco, CA, USA", "North America", "Privileged Access Management",
     False, False, "AMT",
     "Cloud-native privileged access management platform.",
     "Secret Server; Privilege Manager; cloud PAM; DevOps secrets management.",
     ["AMT-04"]),

    ("HashiCorp", "San Francisco, CA, USA", "Global", "Infrastructure & Secrets",
     False, False, "AMT",
     "Infrastructure automation and secrets management through HashiCorp Vault.",
     "Vault for dynamic secrets, encryption-as-a-service, and automated credential rotation.",
     ["AMT-04"]),

    # ── ADR: Adversary Disruption ──
    ("Acalvio Technologies", "Santa Clara, CA, USA", "North America", "Deception Technology",
     True, True, "ADR",
     "Autonomous deception platform using AI to deploy and manage deception across enterprise environments.",
     "ShadowPlex platform; autonomous deception; Active Defense capabilities.",
     ["ADR-01"]),

    ("CounterCraft", "San Sebastian, Spain", "EMEA", "Deception Technology",
     True, False, "ADR",
     "Cyber deception platform for threat intelligence and adversary engagement.",
     "Campaign-based deception; adversary behavior capture; threat intelligence generation.",
     ["ADR-01", "ADR-02"]),

    ("Fidelis Cybersecurity", "Bethesda, MD, USA", "North America", "Network Security & Deception",
     False, False, "ADR",
     "Network detection and response with integrated deception technology.",
     "Fidelis Deception combined with NDR; automated decoy deployment; threat hunting.",
     ["ADR-01", "ADR-03"]),

    ("SentinelOne", "Mountain View, CA, USA", "Global", "Endpoint & Deception",
     False, True, "ADR",
     "AI-powered endpoint security with integrated deception (Attivo Networks acquisition).",
     "Singularity platform with identity threat detection; AD deception; autonomous response.",
     ["ADR-01", "ADR-02", "ADR-03", "EXM-01"]),

    ("Recorded Future", "Somerville, MA, USA", "Global", "Threat Intelligence",
     False, True, "ADR",
     "AI-powered threat intelligence platform aggregating and analyzing global threat data.",
     "Intelligence Cloud; real-time threat feeds; dark web monitoring; geopolitical intelligence.",
     ["ADR-02", "ADR-04"]),

    ("Mandiant (Google Cloud)", "Reston, VA, USA", "Global", "Threat Intelligence & IR",
     False, True, "ADR",
     "Threat intelligence, incident response, and security validation capabilities.",
     "Mandiant Advantage platform; deep adversary tracking; threat hunting expertise.",
     ["ADR-02", "ADR-03", "PPM-01", "PPM-02"]),

    ("ThreatConnect", "Arlington, VA, USA", "North America", "Threat Intelligence Platform",
     False, False, "ADR",
     "Threat intelligence platform with orchestration and automation capabilities.",
     "TIP with SOAR integration; playbook automation; intelligence-driven workflows.",
     ["ADR-02"]),

    ("Anomali", "Redwood City, CA, USA", "North America", "Threat Intelligence Platform",
     False, True, "ADR",
     "AI-powered threat intelligence and detection platform.",
     "ThreatStream TIP; Match for retrospective analysis; intelligence-to-detection automation.",
     ["ADR-02", "ADR-03"]),

    ("ZeroFox", "Baltimore, MD, USA", "North America", "Digital Risk Protection",
     False, True, "ADR",
     "External cybersecurity and digital risk protection platform.",
     "Dark web monitoring; brand protection; takedown services; adversary disruption.",
     ["ADR-02", "ADR-04"]),

    ("Nisos", "Alexandria, VA, USA", "North America", "Managed Intelligence",
     True, False, "ADR",
     "Managed intelligence services for threat attribution and adversary tracking.",
     "Human-driven adversary attribution; counter-threat intelligence; executive protection.",
     ["ADR-04"]),

    ("Arctic Wolf", "Eden Prairie, MN, USA", "North America", "Managed Detection & Hunting",
     False, True, "ADR",
     "Security operations platform with managed detection, response, and threat hunting.",
     "Concierge security team; 24/7 managed hunting; security posture assessment.",
     ["ADR-03", "EXM-03"]),

    ("Group-IB", "Singapore", "APAC", "Threat Intelligence & Fraud",
     False, True, "ADR",
     "Threat intelligence, fraud protection, and digital risk protection platform.",
     "Adversary attribution; dark web intelligence; managed extended detection; takedowns.",
     ["ADR-02", "ADR-04"]),

    # ── PPM: Preemptive Posture Management ──
    ("SafeBreach", "Tel Aviv, Israel", "Global", "Breach & Attack Simulation",
     True, False, "PPM",
     "Continuous security validation through breach and attack simulation.",
     "Largest attack playbook library; continuous validation; security control optimization.",
     ["PPM-01", "PPM-02"]),

    ("AttackIQ", "San Diego, CA, USA", "North America", "Breach & Attack Simulation",
     True, False, "PPM",
     "Breach and attack simulation platform aligned with MITRE ATT&CK.",
     "MITRE ATT&CK alignment; automated security control validation; purple teaming.",
     ["PPM-01", "PPM-02"]),

    ("Cymulate", "Tel Aviv, Israel", "Global", "Security Validation",
     True, False, "PPM",
     "Extended security posture management with BAS, ASM, and purple teaming.",
     "Full kill chain simulation; automated purple teaming; exposure analytics.",
     ["PPM-01", "PPM-02", "EXM-01"]),

    ("Pentera", "Tel Aviv, Israel", "Global", "Automated Penetration Testing",
     True, False, "PPM",
     "Automated security validation through real-world penetration testing.",
     "Agentless automated pen testing; real exploit validation; continuous testing.",
     ["PPM-01", "PPM-03"]),

    ("Horizon3.ai", "San Francisco, CA, USA", "North America", "Autonomous Pen Testing",
     True, True, "PPM",
     "Autonomous penetration testing platform that finds and verifies exploitable attack paths.",
     "NodeZero autonomous pen testing; proof-of-exploit validation; no agents required.",
     ["PPM-03"]),

    ("Picus Security", "San Francisco, CA, USA", "North America", "Security Validation",
     True, False, "PPM",
     "Security control validation platform for continuous testing of detection and prevention.",
     "Complete Security Validation Platform; detection rule validation; mitigation guidance.",
     ["PPM-01", "PPM-02"]),

    ("Wiz", "New York, NY, USA", "Global", "Cloud Security",
     True, True, "PPM",
     "Agentless cloud security platform for CSPM, CWPP, CIEM, and code security.",
     "Agentless cloud scanning; graph-based risk analysis; multi-cloud support; rapid deployment.",
     ["PPM-04", "EXM-01", "EXM-03"]),

    ("Orca Security", "Portland, OR, USA", "North America", "Cloud Security",
     True, True, "PPM",
     "Agentless cloud security platform with SideScanning technology.",
     "SideScanning for agentless coverage; unified cloud security; risk prioritization.",
     ["PPM-04", "EXM-03"]),

    ("Aqua Security", "Ramat Gan, Israel", "Global", "Cloud Native Security",
     True, False, "PPM",
     "Cloud native security platform for containers, serverless, and Kubernetes.",
     "Container and Kubernetes security; runtime protection; software supply chain security.",
     ["PPM-04", "AMT-02", "EXM-04"]),

    ("Lacework (Fortinet)", "San Jose, CA, USA", "North America", "Cloud Security",
     False, True, "PPM",
     "Data-driven cloud security platform for CSPM and anomaly detection.",
     "Polygraph data platform; behavioral anomaly detection; cloud compliance.",
     ["PPM-04"]),

    # ── Multi-pillar / Platform vendors ──
    ("Darktrace", "Cambridge, UK", "EMEA", "AI Cyber Defense",
     False, True, "ADR",
     "AI-powered cyber defense platform using self-learning AI for threat detection and response.",
     "Self-Learning AI; Antigena autonomous response; network-level anomaly detection.",
     ["ADR-02", "ADR-03", "EXM-01"]),

    ("Fortinet", "Sunnyvale, CA, USA", "Global", "Platform Security",
     False, True, "PPM",
     "Broad security platform spanning network, endpoint, cloud, and security operations.",
     "Security Fabric architecture; FortiGuard Labs threat intel; FortiDeceptor.",
     ["ADR-01", "ADR-02", "PPM-04", "AMT-03"]),

    ("IBM Security", "Armonk, NY, USA", "Global", "Enterprise Security",
     False, True, "ADR",
     "Enterprise security platform with threat intelligence, SIEM, and security testing.",
     "X-Force threat intelligence; Randori for automated red teaming; QRadar SIEM.",
     ["ADR-02", "ADR-03", "PPM-03", "EXM-01"]),

    ("Trellix", "Milpitas, CA, USA", "Global", "Extended Detection & Response",
     False, True, "ADR",
     "XDR platform combining endpoint, network, and cloud security with threat intelligence.",
     "Living security approach; advanced threat research; integrated XDR platform.",
     ["ADR-02", "ADR-03"]),

    ("Cisco (Splunk)", "San Jose, CA, USA", "Global", "Platform Security",
     False, True, "PPM",
     "Security platform with network security, observability, and threat intelligence.",
     "Splunk for security analytics; Talos threat intelligence; networking-integrated security.",
     ["ADR-02", "PPM-02", "AMT-03"]),
]

def build_vendor(name, hq, region, specialization, is_startup, is_ai_first,
                 primary_capability, description, key_differentiators,
                 expected_coverage):
    """Build a single vendor seed record with zero scores."""
    return {
        "vendor": name,
        "headquarters": hq,
        "region": region,
        "specialization": specialization,
        "is_startup": is_startup,
        "is_ai_first": is_ai_first,
        "primary_capability": primary_capability,
        "description": description,
        "key_differentiators": key_differentiators,
        "expected_coverage": expected_coverage,
        "capability_coverage_count": len(expected_coverage),
        "ir_focus_type": "Enterprise",
        "pillar_scores": {
            "EXM": 0,
            "AMT": 0,
            "ADR": 0,
            "PPM": 0
        },
        "sub_pillar_scores_current": {sp: 0 for sp in SUB_PILLAR_LABELS},
        "sub_pillar_schema_labels": dict(SUB_PILLAR_LABELS),
    }

def main():
    vendors = []
    for seed in VENDOR_SEEDS:
        vendors.append(build_vendor(*seed))

    output = {
        "schema_ref": SCHEMA_REF,
        "schema_version": SCHEMA_VERSION,
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "vendor_count": len(vendors),
        "vendors": vendors
    }

    outfile = "Preemptive Cybersecurity Vendor 1-0 Seed.json"
    with open(outfile, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(vendors)} vendors → {outfile}")

    # Summary by primary pillar
    from collections import Counter
    pillar_counts = Counter(v["primary_capability"] for v in vendors)
    print(f"\nBy primary pillar:")
    for p, c in sorted(pillar_counts.items()):
        print(f"  {p}: {c} vendors")

    # Startup / AI-first counts
    startups = sum(1 for v in vendors if v["is_startup"])
    ai_first = sum(1 for v in vendors if v["is_ai_first"])
    print(f"\nStartups: {startups}/{len(vendors)}")
    print(f"AI-first: {ai_first}/{len(vendors)}")

    # Coverage distribution
    coverages = [v["capability_coverage_count"] for v in vendors]
    print(f"\nSub-pillar coverage range: {min(coverages)}-{max(coverages)}")
    print(f"Average coverage: {sum(coverages)/len(coverages):.1f}")

if __name__ == "__main__":
    main()
