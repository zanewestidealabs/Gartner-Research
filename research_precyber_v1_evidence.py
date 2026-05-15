"""
research_precyber_v1_evidence.py — Preemptive Cybersecurity Vendor Evidence Pipeline

Evaluates vendors against the Preemptive_Cybersecurity_Schema.json using public web
evidence.  Processes vendors in batches of 5 with a pause between batches, then merges
all batch results into the final output file.

Completely separate from TRiSM / DFIR research pipelines — different schema, different
pillar codes (EXM/AMT/ADR/PPM), different vendor list.

Usage:
  python research_precyber_v1_evidence.py                     # full run (51 vendors, batches of 5)
  python research_precyber_v1_evidence.py --batch-size 5      # explicit batch size
  python research_precyber_v1_evidence.py --batch-pause 30    # seconds between batches
  python research_precyber_v1_evidence.py --max-vendors 5     # test with 5 vendors
  python research_precyber_v1_evidence.py --resume            # resume from last checkpoint
  python research_precyber_v1_evidence.py --merge-only        # just merge batch outputs
  python research_precyber_v1_evidence.py --force-fetch       # re-fetch cached pages
"""

import argparse
import hashlib
import json
import random
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────────────
# Configuration — completely separate from TRiSM / DFIR pipelines
# ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent

DEFAULT_INPUT_FILE  = ROOT / "Preemptive Cybersecurity Vendor 1-0 Seed.json"
DEFAULT_SCHEMA_FILE = ROOT / "Preemptive_Cybersecurity_Schema.json"
DEFAULT_OUTPUT_FILE = ROOT / "Preemptive Cybersecurity Vendor 1-1 Validated.json"

# Separate cache and checkpoint dirs
CACHE_DIR           = ROOT / "research" / "cache" / "pages_precyber"
CHECKPOINT_DIR      = ROOT / "research" / "precyber_checkpoints"
BATCH_OUTPUT_DIR    = ROOT / "research" / "precyber_batches"

URL_RE = re.compile(r"https?://[^\s)\]\}\">,]+")

PILLARS = ["EXM", "AMT", "ADR", "PPM"]
SUBPILLAR_IDS = [f"{p}-{i:02d}" for p in PILLARS for i in range(1, 5)]

# ─────────────────────────────────────────────────────────────────────
# Preemptive Cybersecurity–specific search terms
# Covers all 4 pillars: Exposure Management, Automated Moving Target
# Defense, Adversary Disruption, Preemptive Posture Management
# ─────────────────────────────────────────────────────────────────────

PRECYBER_PRIMARY_TERMS = [
    # ── Exposure Management (EXM) ──
    "attack surface management", "ASM", "external attack surface",
    "EASM", "asset discovery", "shadow IT", "digital footprint",
    "cyber asset management", "CTEM", "continuous threat exposure",
    "exposure management", "threat exposure", "exposure prioritization",
    "vulnerability prioritization", "risk-based vulnerability",
    "VPT", "vulnerability management", "exploit prediction",
    "patch prioritization", "remediation prioritization",
    "third-party risk", "supply chain security", "vendor risk management",
    "SBOM", "software supply chain", "third-party exposure",
    "open source risk", "software bill of materials",
    # ── Automated Moving Target Defense (AMT) ──
    "moving target defense", "AMTD", "polymorphic defense",
    "runtime randomization", "address space randomization",
    "memory randomization", "dynamic defense", "RASP",
    "runtime protection", "application shielding",
    "runtime application self-protection", "code instrumentation",
    "exploit prevention", "application hardening",
    "micro-segmentation", "software-defined perimeter",
    "network randomization", "zero trust network",
    "dynamic segmentation", "adaptive network",
    "credential rotation", "ephemeral credentials",
    "key rotation", "token rotation", "just-in-time access",
    "secret rotation", "privileged access management",
    # ── Adversary Disruption (ADR) ──
    "deception technology", "honeypot", "honeytoken",
    "decoy", "breadcrumb", "deception platform",
    "cyber deception", "distributed deception",
    "threat intelligence platform", "TIP",
    "threat intelligence operationalization",
    "IOC enrichment", "adversary tracking",
    "threat feed", "MITRE ATT&CK",
    "threat hunting", "proactive hunting",
    "hypothesis-driven hunting", "hunt operations",
    "adversary hunting", "managed threat hunting",
    "detection engineering", "counter-adversary",
    "adversary disruption", "takedown service",
    "dark web monitoring", "adversary attribution",
    "digital risk protection", "brand protection",
    # ── Preemptive Posture Management (PPM) ──
    "breach and attack simulation", "BAS",
    "attack simulation", "purple team",
    "control validation", "security validation",
    "adversary simulation", "security control validation",
    "control effectiveness", "detection validation",
    "SIEM validation", "EDR validation",
    "control gap analysis", "security posture validation",
    "penetration testing", "automated pentest",
    "red team", "continuous pentest",
    "attack path analysis", "PTaaS",
    "offensive security", "exploitation testing",
    "CSPM", "cloud security posture",
    "cloud misconfiguration", "CIEM",
    "cloud entitlement", "CNAPP",
    "cloud workload protection", "cloud compliance",
    # ── General preemptive/proactive terms ──
    "preemptive security", "proactive defense",
    "proactive security", "preemptive cybersecurity",
    "continuous validation", "continuous monitoring",
    "automated remediation", "risk scoring",
    "attack path", "lateral movement",
    "zero trust", "threat prevention",
]

PRECYBER_EXCLUSION_TERMS = [
    "reactive only", "response-only", "manual-only process",
    "no automation", "human-only review", "compliance-only",
    "deprecated product",
]

# ─────────────────────────────────────────────────────────────────────
# Synonym / terminology variation expansion
# Maps canonical terms → list of alternative phrasings
# ─────────────────────────────────────────────────────────────────────

TERM_SYNONYMS: Dict[str, List[str]] = {
    # ── Exposure Management ──
    "attack surface management":    ["attack surface reduction", "attack surface visibility",
                                     "external surface management", "ASM platform",
                                     "attack surface monitoring"],
    "ASM":                          ["attack surface management", "EASM"],
    "external attack surface":      ["EASM", "external surface", "internet-facing assets",
                                     "external exposure"],
    "EASM":                         ["external attack surface management",
                                     "external surface management"],
    "asset discovery":              ["asset identification", "asset inventory",
                                     "asset enumeration", "asset scanning",
                                     "continuous asset discovery"],
    "shadow IT":                    ["shadow IT discovery", "unsanctioned IT",
                                     "rogue assets", "unknown assets",
                                     "unmanaged assets"],
    "digital footprint":            ["digital footprint mapping", "internet footprint",
                                     "online footprint", "external footprint"],
    "cyber asset management":       ["CAASM", "cyber asset attack surface management",
                                     "asset management platform"],
    "CTEM":                         ["continuous threat exposure management",
                                     "threat exposure management program",
                                     "Gartner CTEM"],
    "continuous threat exposure":   ["ongoing threat exposure", "continuous exposure assessment",
                                     "always-on exposure management"],
    "exposure management":          ["exposure reduction", "exposure assessment",
                                     "exposure management platform"],
    "vulnerability prioritization": ["risk-based prioritization", "vuln prioritization",
                                     "prioritized remediation", "vulnerability ranking"],
    "risk-based vulnerability":     ["risk-based VM", "context-based vulnerability",
                                     "threat-aware vulnerability"],
    "VPT":                          ["vulnerability priority technology",
                                     "vulnerability prioritization technology"],
    "vulnerability management":     ["VM", "vuln management", "vulnerability scanning",
                                     "vulnerability assessment"],
    "exploit prediction":           ["exploit probability", "EPSS",
                                     "exploit prediction scoring", "exploitability analysis"],
    "patch prioritization":         ["intelligent patching", "prioritized patching",
                                     "patch management prioritization"],
    "third-party risk":             ["third party risk", "3rd party risk",
                                     "TPRM", "vendor risk",
                                     "third-party risk management"],
    "supply chain security":        ["software supply chain security",
                                     "supply chain risk management",
                                     "supply chain integrity"],
    "vendor risk management":       ["VRM", "vendor security assessment",
                                     "third-party vendor risk"],
    "SBOM":                         ["software bill of materials",
                                     "software composition analysis",
                                     "software supply chain transparency"],
    "software supply chain":        ["software supply chain risk",
                                     "open source supply chain",
                                     "dependency management"],
    "open source risk":             ["open source vulnerability",
                                     "open source security",
                                     "OSS risk", "SCA"],

    # ── Automated Moving Target Defense ──
    "moving target defense":        ["MTD", "moving target", "dynamic target defense",
                                     "automated moving target"],
    "AMTD":                         ["automated moving target defense",
                                     "automated MTD"],
    "polymorphic defense":          ["polymorphic protection", "morphing defense",
                                     "code polymorphism", "runtime polymorphism"],
    "runtime randomization":        ["ASLR", "address space layout randomization",
                                     "runtime mutation", "runtime diversity"],
    "address space randomization":  ["ASLR", "memory layout randomization",
                                     "stack randomization"],
    "RASP":                         ["runtime application self-protection",
                                     "runtime app security", "in-app protection"],
    "runtime protection":           ["runtime security", "runtime defense",
                                     "real-time application protection"],
    "application shielding":        ["app shielding", "application protection",
                                     "application armor", "code shielding"],
    "code instrumentation":         ["bytecode instrumentation", "binary instrumentation",
                                     "inline instrumentation"],
    "exploit prevention":           ["exploit protection", "exploit blocking",
                                     "exploit mitigation", "anti-exploit"],
    "application hardening":        ["app hardening", "binary hardening",
                                     "code hardening", "software hardening"],
    "micro-segmentation":          ["microsegmentation", "micro segmentation",
                                     "workload segmentation", "network segmentation"],
    "software-defined perimeter":   ["SDP", "software defined perimeter",
                                     "zero trust perimeter"],
    "zero trust network":           ["ZTNA", "zero trust network access",
                                     "zero trust architecture"],
    "credential rotation":          ["password rotation", "credential cycling",
                                     "automated credential rotation"],
    "ephemeral credentials":        ["short-lived credentials", "temporary credentials",
                                     "ephemeral tokens", "one-time credentials"],
    "key rotation":                 ["encryption key rotation", "API key rotation",
                                     "key lifecycle management"],
    "token rotation":               ["token lifecycle", "token refresh",
                                     "session token rotation"],
    "just-in-time access":          ["JIT access", "just in time access",
                                     "JIT provisioning", "on-demand access"],
    "secret rotation":              ["secrets management", "vault rotation",
                                     "secrets lifecycle"],
    "privileged access management": ["PAM", "privileged access", "privileged identity",
                                     "privilege management", "PIM"],

    # ── Adversary Disruption ──
    "deception technology":         ["deception platform", "deception-based defense",
                                     "deception-based detection", "active deception"],
    "honeypot":                     ["honey pot", "honeypots", "decoy system",
                                     "decoy server", "production honeypot"],
    "honeytoken":                   ["honey token", "honeytokens", "canary token",
                                     "canary tokens", "breadcrumb token"],
    "decoy":                        ["decoys", "decoy asset", "decoy network",
                                     "decoy file", "decoy credential"],
    "breadcrumb":                   ["breadcrumbs", "lure", "bait",
                                     "deception lure"],
    "cyber deception":              ["network deception", "deception defense",
                                     "deception operations"],
    "threat intelligence platform": ["TIP", "threat intel platform",
                                     "threat intelligence management"],
    "threat intelligence operationalization": ["operationalized threat intel",
                                              "actionable threat intelligence",
                                              "threat intel automation"],
    "IOC enrichment":               ["indicator enrichment", "indicator of compromise",
                                     "IOC correlation", "threat indicator"],
    "adversary tracking":           ["threat actor tracking", "adversary profiling",
                                     "attacker tracking", "APT tracking"],
    "MITRE ATT&CK":                ["MITRE attack framework", "ATT&CK framework",
                                     "ATT&CK mapping", "ATT&CK coverage",
                                     "MITRE technique"],
    "threat hunting":               ["threat hunt", "proactive threat detection",
                                     "active hunting", "cyber hunting"],
    "proactive hunting":            ["proactive threat hunting", "active threat hunting",
                                     "hypothesis-driven hunting"],
    "managed threat hunting":       ["MDR hunting", "managed detection and hunting",
                                     "outsourced hunting"],
    "detection engineering":        ["detection content development",
                                     "detection rule engineering",
                                     "SIEM content engineering"],
    "counter-adversary":            ["counter adversary", "adversary counter-operations",
                                     "threat neutralization"],
    "adversary disruption":         ["attacker disruption", "threat disruption",
                                     "adversary interference"],
    "takedown service":             ["domain takedown", "phishing takedown",
                                     "infrastructure takedown", "site takedown"],
    "dark web monitoring":          ["darknet monitoring", "deep web monitoring",
                                     "dark web intelligence", "underground monitoring"],
    "adversary attribution":        ["threat attribution", "attacker attribution",
                                     "campaign attribution"],
    "digital risk protection":      ["DRP", "digital risk monitoring",
                                     "digital risk management", "DRPS"],
    "brand protection":             ["brand monitoring", "brand impersonation detection",
                                     "brand abuse detection"],

    # ── Preemptive Posture Management ──
    "breach and attack simulation":  ["BAS", "attack simulation platform",
                                      "continuous BAS", "automated BAS"],
    "BAS":                           ["breach attack simulation",
                                      "breach and attack simulation"],
    "attack simulation":             ["adversary emulation", "threat simulation",
                                      "attack emulation"],
    "purple team":                   ["purple teaming", "purple team automation",
                                      "purple team exercise"],
    "control validation":            ["security control testing",
                                      "control effectiveness testing",
                                      "defensive control validation"],
    "security validation":           ["continuous security validation",
                                      "security measurement", "security verification"],
    "security control validation":   ["detection control validation",
                                      "prevention control validation",
                                      "security control testing"],
    "control effectiveness":         ["control efficacy", "defense effectiveness",
                                      "security effectiveness"],
    "detection validation":          ["detection coverage testing",
                                      "detection gap analysis",
                                      "alert validation"],
    "penetration testing":           ["pen testing", "pentest", "pen test",
                                      "penetration test", "ethical hacking"],
    "automated pentest":             ["automated penetration testing",
                                      "autonomous pentest", "continuous pentest"],
    "red team":                      ["red teaming", "red team exercise",
                                      "red team operation", "adversarial red team"],
    "attack path analysis":          ["attack path mapping", "attack graph",
                                      "attack path visualization",
                                      "attack path management"],
    "PTaaS":                         ["pen testing as a service",
                                      "penetration testing as a service",
                                      "pentest as a service"],
    "CSPM":                          ["cloud security posture management",
                                      "cloud posture management",
                                      "cloud security assessment"],
    "cloud security posture":        ["cloud posture", "cloud security assessment",
                                      "cloud security configuration"],
    "cloud misconfiguration":        ["cloud misconfig", "cloud configuration error",
                                      "cloud security misconfiguration"],
    "CIEM":                          ["cloud infrastructure entitlement management",
                                      "cloud entitlement management",
                                      "cloud permission management"],
    "CNAPP":                         ["cloud native application protection",
                                      "cloud native application protection platform",
                                      "cloud native security"],
    "cloud workload protection":     ["CWP", "CWPP", "cloud workload security",
                                      "workload protection platform"],

    # ── General preemptive/proactive ──
    "preemptive security":           ["preemptive defense", "preemptive protection",
                                      "preventive security"],
    "proactive defense":             ["proactive security", "proactive protection",
                                      "active defense"],
    "zero trust":                    ["zero trust architecture", "ZTA",
                                      "zero trust model", "zero trust security"],
    "continuous monitoring":         ["continuous security monitoring",
                                      "always-on monitoring", "24/7 monitoring"],
    "risk scoring":                  ["risk rating", "risk quantification",
                                      "risk assessment score"],
    "attack path":                   ["attack chain", "kill chain",
                                      "attack vector", "exploit path"],
    "lateral movement":              ["lateral spread", "east-west movement",
                                      "internal propagation"],
}


def _term_in_text(term: str, text_lower: str) -> bool:
    """Check if a term OR any of its synonyms appear in lowered text."""
    if term in text_lower:
        return True
    synonyms = TERM_SYNONYMS.get(term)
    if synonyms:
        return any(syn.lower() in text_lower for syn in synonyms)
    return False


def _matched_terms_in_text(terms: List[str], text_lower: str) -> List[str]:
    """Return list of terms (from *terms*) that match text, including synonyms.
    Reports the canonical term name even when a synonym triggered the match."""
    return [t for t in terms if _term_in_text(t, text_lower)]


# ─────────────────────────────────────────────────────────────────────
# Vendor-specific URLs for Preemptive Cybersecurity evaluation
# Curated per vendor — 5-6 URLs focusing on preemptive capabilities
# ─────────────────────────────────────────────────────────────────────

VENDOR_URLS: Dict[str, List[str]] = {
    "Tenable": [
        "https://www.tenable.com/products/tenable-one",
        "https://www.tenable.com/products/tenable-asm",
        "https://www.tenable.com/products/vulnerability-management",
        "https://www.tenable.com/exposure-management",
        "https://www.tenable.com/solutions/cloud-security",
        "https://www.tenable.com/products/exposure-ai",
    ],
    "Qualys": [
        "https://www.qualys.com/platform/",
        "https://www.qualys.com/apps/external-attack-surface-management/",
        "https://www.qualys.com/apps/vulnerability-management-detection-response/",
        "https://www.qualys.com/apps/cybersecurity-asset-management/",
        "https://www.qualys.com/platform/cloud-security/",
        "https://blog.qualys.com/vulnerabilities-threat-research",
    ],
    "Rapid7": [
        "https://www.rapid7.com/products/insightvm/",
        "https://www.rapid7.com/products/insightconnect/",
        "https://www.rapid7.com/products/metasploit/",
        "https://www.rapid7.com/products/insightappsec/",
        "https://www.rapid7.com/solutions/cloud-security/",
        "https://www.rapid7.com/products/velociraptor/",
    ],
    "CrowdStrike": [
        "https://www.crowdstrike.com/platform/",
        "https://www.crowdstrike.com/platform/falcon-exposure-management/",
        "https://www.crowdstrike.com/platform/falcon-identity-protection/",
        "https://www.crowdstrike.com/platform/falcon-surface/",
        "https://www.crowdstrike.com/platform/falcon-cloud-security/",
        "https://www.crowdstrike.com/platform/threat-intelligence/",
    ],
    "Palo Alto Networks": [
        "https://www.paloaltonetworks.com/cortex/cortex-xsiam",
        "https://www.paloaltonetworks.com/cortex/cortex-xpanse",
        "https://www.paloaltonetworks.com/prisma/cloud",
        "https://www.paloaltonetworks.com/cortex/cortex-xdr",
        "https://www.paloaltonetworks.com/unit42",
        "https://www.paloaltonetworks.com/network-security/zero-trust",
    ],
    "Censys": [
        "https://censys.com/platform/",
        "https://censys.com/attack-surface-management/",
        "https://censys.com/exposure-management/",
        "https://censys.com/solutions/",
        "https://censys.com/resources/",
    ],
    "CyCognito": [
        "https://www.cycognito.com/platform",
        "https://www.cycognito.com/products/attack-surface-management",
        "https://www.cycognito.com/products/testing",
        "https://www.cycognito.com/solutions/exposure-management",
        "https://www.cycognito.com/resources/",
    ],
    "Armis": [
        "https://www.armis.com/platform/",
        "https://www.armis.com/platform/asset-intelligence/",
        "https://www.armis.com/platform/vulnerability-management/",
        "https://www.armis.com/cyberwarfare/",
        "https://www.armis.com/solutions/",
    ],
    "Axonius": [
        "https://www.axonius.com/platform",
        "https://www.axonius.com/solutions/asset-management",
        "https://www.axonius.com/solutions/vulnerability-management",
        "https://www.axonius.com/solutions/cloud-security",
        "https://www.axonius.com/resources/",
    ],
    "JupiterOne": [
        "https://www.jupiterone.com/platform",
        "https://www.jupiterone.com/solutions/cyber-asset-management",
        "https://www.jupiterone.com/solutions/vulnerability-management",
        "https://www.jupiterone.com/solutions/cloud-security",
        "https://www.jupiterone.com/resources/",
    ],
    "XM Cyber": [
        "https://www.xmcyber.com/platform/",
        "https://www.xmcyber.com/solution/attack-path-management/",
        "https://www.xmcyber.com/solution/continuous-exposure-management/",
        "https://www.xmcyber.com/solution/remediation-prioritization/",
        "https://www.xmcyber.com/resources/",
    ],
    "Bitsight": [
        "https://www.bitsight.com/products",
        "https://www.bitsight.com/products/security-ratings",
        "https://www.bitsight.com/products/third-party-risk-management",
        "https://www.bitsight.com/products/attack-surface-analytics",
        "https://www.bitsight.com/solutions/",
    ],
    "SecurityScorecard": [
        "https://securityscorecard.com/platform/",
        "https://securityscorecard.com/products/security-ratings/",
        "https://securityscorecard.com/products/attack-surface-intelligence/",
        "https://securityscorecard.com/products/third-party-risk/",
        "https://securityscorecard.com/solutions/",
    ],
    "Panorays": [
        "https://www.panorays.com/platform",
        "https://www.panorays.com/product/third-party-security-management",
        "https://www.panorays.com/product/supply-chain-discovery",
        "https://www.panorays.com/product/risk-assessment",
        "https://www.panorays.com/resources/",
    ],
    "Morphisec": [
        "https://www.morphisec.com/moving-target-defense/",
        "https://www.morphisec.com/products/",
        "https://www.morphisec.com/solutions/automated-moving-target-defense/",
        "https://www.morphisec.com/solutions/anti-ransomware/",
        "https://www.morphisec.com/resources/",
    ],
    "RunSafe Security": [
        "https://runsafesecurity.com/technology/",
        "https://runsafesecurity.com/products/",
        "https://runsafesecurity.com/solutions/moving-target-defense/",
        "https://runsafesecurity.com/solutions/memory-safety/",
        "https://runsafesecurity.com/resources/",
    ],
    "Contrast Security": [
        "https://www.contrastsecurity.com/runtime-security",
        "https://www.contrastsecurity.com/contrast-assess",
        "https://www.contrastsecurity.com/contrast-protect",
        "https://www.contrastsecurity.com/contrast-scan",
        "https://www.contrastsecurity.com/solutions/",
    ],
    "Illumio": [
        "https://www.illumio.com/products",
        "https://www.illumio.com/solutions/zero-trust-segmentation",
        "https://www.illumio.com/solutions/micro-segmentation",
        "https://www.illumio.com/solutions/ransomware-containment",
        "https://www.illumio.com/resources/",
    ],
    "Akamai (Guardicore)": [
        "https://www.akamai.com/products/akamai-guardicore-segmentation",
        "https://www.akamai.com/solutions/zero-trust",
        "https://www.akamai.com/products/hunt-threat-hunting",
        "https://www.akamai.com/solutions/security",
        "https://www.akamai.com/resources/",
    ],
    "Zscaler": [
        "https://www.zscaler.com/products/zero-trust-exchange",
        "https://www.zscaler.com/products/zscaler-private-access",
        "https://www.zscaler.com/products/zscaler-digital-experience",
        "https://www.zscaler.com/products/zscaler-deception",
        "https://www.zscaler.com/solutions/cloud-security-posture-management",
    ],
    "CyberArk": [
        "https://www.cyberark.com/products/privileged-access-manager/",
        "https://www.cyberark.com/products/secrets-manager/",
        "https://www.cyberark.com/products/endpoint-privilege-manager/",
        "https://www.cyberark.com/products/cloud-entitlements-manager/",
        "https://www.cyberark.com/solutions/zero-trust/",
    ],
    "BeyondTrust": [
        "https://www.beyondtrust.com/products/privileged-access-management",
        "https://www.beyondtrust.com/products/password-safe",
        "https://www.beyondtrust.com/products/privilege-management",
        "https://www.beyondtrust.com/solutions/zero-trust-security",
        "https://www.beyondtrust.com/resources/",
    ],
    "Delinea": [
        "https://delinea.com/products/secret-server",
        "https://delinea.com/products/privilege-manager",
        "https://delinea.com/products/server-suite",
        "https://delinea.com/products/devops-secrets-vault",
        "https://delinea.com/solutions/zero-trust-privilege",
    ],
    "HashiCorp": [
        "https://www.hashicorp.com/products/vault",
        "https://www.hashicorp.com/products/boundary",
        "https://www.hashicorp.com/products/consul",
        "https://www.hashicorp.com/solutions/zero-trust-security",
        "https://www.hashicorp.com/solutions/secrets-management",
    ],
    "Acalvio Technologies": [
        "https://www.acalvio.com/products/",
        "https://www.acalvio.com/platform/",
        "https://www.acalvio.com/solutions/deception-technology/",
        "https://www.acalvio.com/solutions/active-defense/",
        "https://www.acalvio.com/resources/",
    ],
    "CounterCraft": [
        "https://www.countercraft.eu/platform/",
        "https://www.countercraft.eu/products/",
        "https://www.countercraft.eu/solutions/deception/",
        "https://www.countercraft.eu/solutions/threat-intelligence/",
        "https://www.countercraft.eu/resources/",
    ],
    "Fidelis Cybersecurity": [
        "https://fidelissecurity.com/products/deception/",
        "https://fidelissecurity.com/products/network/",
        "https://fidelissecurity.com/products/endpoint/",
        "https://fidelissecurity.com/solutions/",
        "https://fidelissecurity.com/resources/",
    ],
    "SentinelOne": [
        "https://www.sentinelone.com/platform/",
        "https://www.sentinelone.com/platform/singularity-xdr/",
        "https://www.sentinelone.com/platform/singularity-identity/",
        "https://www.sentinelone.com/platform/singularity-cloud/",
        "https://www.sentinelone.com/resources/",
    ],
    "Recorded Future": [
        "https://www.recordedfuture.com/platform",
        "https://www.recordedfuture.com/products/threat-intelligence",
        "https://www.recordedfuture.com/products/attack-surface-intelligence",
        "https://www.recordedfuture.com/products/threat-hunting",
        "https://www.recordedfuture.com/resources/",
    ],
    "Mandiant (Google Cloud)": [
        "https://www.mandiant.com/advantage/threat-intelligence",
        "https://www.mandiant.com/advantage/attack-surface-management",
        "https://www.mandiant.com/advantage/security-validation",
        "https://www.mandiant.com/advantage/managed-defense",
        "https://www.mandiant.com/resources/",
    ],
    "ThreatConnect": [
        "https://www.threatconnect.com/platform/",
        "https://www.threatconnect.com/threat-intelligence-platform/",
        "https://www.threatconnect.com/threat-intelligence-operations/",
        "https://www.threatconnect.com/solutions/",
        "https://www.threatconnect.com/resources/",
    ],
    "Anomali": [
        "https://www.anomali.com/platform",
        "https://www.anomali.com/products/threatstream",
        "https://www.anomali.com/products/match",
        "https://www.anomali.com/solutions/threat-intelligence/",
        "https://www.anomali.com/resources/",
    ],
    "ZeroFox": [
        "https://www.zerofox.com/platform/",
        "https://www.zerofox.com/products/external-cybersecurity/",
        "https://www.zerofox.com/products/dark-web-monitoring/",
        "https://www.zerofox.com/products/takedowns/",
        "https://www.zerofox.com/solutions/digital-risk-protection/",
    ],
    "Nisos": [
        "https://www.nisos.com/services/",
        "https://www.nisos.com/solutions/managed-intelligence/",
        "https://www.nisos.com/solutions/threat-actor-monitoring/",
        "https://www.nisos.com/solutions/digital-risk/",
        "https://www.nisos.com/resources/",
    ],
    "Arctic Wolf": [
        "https://arcticwolf.com/solutions/",
        "https://arcticwolf.com/solutions/managed-detection-and-response/",
        "https://arcticwolf.com/solutions/managed-risk/",
        "https://arcticwolf.com/solutions/security-operations/",
        "https://arcticwolf.com/resources/",
    ],
    "Group-IB": [
        "https://www.group-ib.com/products/threat-intelligence/",
        "https://www.group-ib.com/products/digital-risk-protection/",
        "https://www.group-ib.com/products/attack-surface-management/",
        "https://www.group-ib.com/products/fraud-protection/",
        "https://www.group-ib.com/resources/",
    ],
    "SafeBreach": [
        "https://www.safebreach.com/platform/",
        "https://www.safebreach.com/use-cases/breach-and-attack-simulation/",
        "https://www.safebreach.com/use-cases/security-control-validation/",
        "https://www.safebreach.com/use-cases/attack-surface-management/",
        "https://www.safebreach.com/resources/",
    ],
    "AttackIQ": [
        "https://www.attackiq.com/platform/",
        "https://www.attackiq.com/solutions/breach-and-attack-simulation/",
        "https://www.attackiq.com/solutions/security-optimization/",
        "https://www.attackiq.com/solutions/purple-teaming/",
        "https://www.attackiq.com/resources/",
    ],
    "Cymulate": [
        "https://cymulate.com/platform/",
        "https://cymulate.com/products/breach-and-attack-simulation/",
        "https://cymulate.com/products/continuous-automated-red-teaming/",
        "https://cymulate.com/products/attack-surface-management/",
        "https://cymulate.com/resources/",
    ],
    "Pentera": [
        "https://pentera.io/platform/",
        "https://pentera.io/products/pentera-core/",
        "https://pentera.io/products/pentera-surface/",
        "https://pentera.io/solutions/automated-penetration-testing/",
        "https://pentera.io/resources/",
    ],
    "Horizon3.ai": [
        "https://www.horizon3.ai/platform/",
        "https://www.horizon3.ai/nodezero/",
        "https://www.horizon3.ai/solutions/autonomous-pentesting/",
        "https://www.horizon3.ai/solutions/attack-surface-management/",
        "https://www.horizon3.ai/resources/",
    ],
    "Picus Security": [
        "https://www.picussecurity.com/platform",
        "https://www.picussecurity.com/products/security-control-validation",
        "https://www.picussecurity.com/products/attack-simulation",
        "https://www.picussecurity.com/solutions/",
        "https://www.picussecurity.com/resources/",
    ],
    "Wiz": [
        "https://www.wiz.io/platform",
        "https://www.wiz.io/solutions/cspm",
        "https://www.wiz.io/solutions/vulnerability-management",
        "https://www.wiz.io/solutions/cloud-detection-and-response",
        "https://www.wiz.io/resources/",
    ],
    "Orca Security": [
        "https://orca.security/platform/",
        "https://orca.security/solutions/cloud-security-posture-management/",
        "https://orca.security/solutions/vulnerability-management/",
        "https://orca.security.solutions/cloud-detection-response/",
        "https://orca.security/resources/",
    ],
    "Aqua Security": [
        "https://www.aquasec.com/products/cloud-native-app-protection/",
        "https://www.aquasec.com/products/cspm/",
        "https://www.aquasec.com/products/runtime-protection/",
        "https://www.aquasec.com/products/supply-chain-security/",
        "https://www.aquasec.com/resources/",
    ],
    "Lacework (Fortinet)": [
        "https://www.lacework.com/platform/",
        "https://www.lacework.com/solutions/cloud-security/",
        "https://www.lacework.com/solutions/vulnerability-management/",
        "https://www.lacework.com/solutions/cloud-compliance/",
        "https://www.lacework.com/resources/",
    ],
    "Darktrace": [
        "https://darktrace.com/products/proactive-exposure-management",
        "https://darktrace.com/products/detect",
        "https://darktrace.com/products/prevent",
        "https://darktrace.com/platform",
        "https://darktrace.com/cyber-ai-analyst",
    ],
    "Fortinet": [
        "https://www.fortinet.com/solutions/enterprise-midsize-business/security-fabric",
        "https://www.fortinet.com/products/fortianalyzer",
        "https://www.fortinet.com/products/fortigate",
        "https://www.fortinet.com/products/fortideceptor",
        "https://www.fortinet.com/solutions/enterprise-midsize-business/cloud-security",
    ],
    "IBM Security": [
        "https://www.ibm.com/security",
        "https://www.ibm.com/products/qradar-siem",
        "https://www.ibm.com/products/guardium",
        "https://www.ibm.com/products/randori",
        "https://www.ibm.com/products/verify-privilege-vault",
    ],
    "Trellix": [
        "https://www.trellix.com/platform/",
        "https://www.trellix.com/products/endpoint-security/",
        "https://www.trellix.com/products/network-security/",
        "https://www.trellix.com/products/xdr/",
        "https://www.trellix.com/solutions/threat-intelligence/",
    ],
    "Cisco (Splunk)": [
        "https://www.cisco.com/site/us/en/solutions/security/index.html",
        "https://www.cisco.com/site/us/en/products/security/index.html",
        "https://www.splunk.com/en_us/products/security-analytics.html",
        "https://www.cisco.com/site/us/en/products/security/zero-trust.html",
        "https://www.splunk.com/en_us/products/unified-security-and-observability-platform.html",
    ],

    # ── SVC: MSSPs & SIs (added v3) ──────────────────────────────────
    "Trustwave": [
        "https://www.trustwave.com/en-us/services/managed-security-services/",
        "https://www.trustwave.com/en-us/services/managed-detection-and-response/",
        "https://www.trustwave.com/en-us/capabilities/threat-intelligence/",
        "https://www.trustwave.com/en-us/services/security-testing/",
        "https://www.trustwave.com/en-us/resources/",
    ],
    "Cyderes": [
        "https://www.cyderes.com/services/",
        "https://www.cyderes.com/services/managed-detection-response/",
        "https://www.cyderes.com/services/security-operations/",
        "https://www.cyderes.com/technology-partners/",
        "https://www.cyderes.com/about/",
    ],
    "Optiv": [
        "https://www.optiv.com/services/managed-security-services",
        "https://www.optiv.com/services/security-operations",
        "https://www.optiv.com/services/threat-intelligence",
        "https://www.optiv.com/services/vulnerability-management",
        "https://www.optiv.com/services/",
    ],
    "Leidos Cybersecurity": [
        "https://www.leidos.com/markets/defense/cybersecurity",
        "https://www.leidos.com/capabilities/cybersecurity",
        "https://www.leidos.com/services/cybersecurity",
        "https://www.leidos.com/resources/",
    ],
    "BT Security": [
        "https://www.bt.com/business/security",
        "https://www.bt.com/business/security/managed-security-services",
        "https://www.bt.com/business/security/threat-intelligence",
        "https://www.bt.com/business/security/soc-services",
        "https://www.bt.com/business/security/partners",
    ],
    "Orange Cyberdefense": [
        "https://www.orangecyberdefense.com/global/services/managed-detection-response/",
        "https://www.orangecyberdefense.com/global/services/threat-intelligence/",
        "https://www.orangecyberdefense.com/global/services/security-monitoring/",
        "https://www.orangecyberdefense.com/global/services/vulnerability-intelligence/",
    ],
    "Wipro CyberTransformation": [
        "https://www.wipro.com/cybersecurity/",
        "https://www.wipro.com/cybersecurity/managed-detection-and-response/",
        "https://www.wipro.com/cybersecurity/vulnerability-risk-management/",
        "https://www.wipro.com/cybersecurity/cyber-defense-services/",
    ],
    "Infosys Cybersecurity": [
        "https://www.infosys.com/services/cybersecurity.html",
        "https://www.infosys.com/services/cybersecurity/offerings/managed-detection-response.html",
        "https://www.infosys.com/services/cybersecurity/offerings/threat-intelligence.html",
        "https://www.infosys.com/about/partners/technology-alliances.html",
        "https://www.infosys.com/services/cybersecurity/partners.html",
    ],
    "NTT Data": [
        "https://www.nttdata.com/global/en/services/security",
        "https://www.nttdata.com/global/en/services/security/managed-security-services",
        "https://www.nttdata.com/global/en/services/security/threat-intelligence",
        "https://www.nttdata.com/global/en/about-us/alliances",
        "https://www.nttdata.com/global/en/partners",
    ],
    "Tata Consultancy Services (TCS) Security": [
        "https://www.tcs.com/what-we-do/industries/cybersecurity",
        "https://www.tcs.com/what-we-do/products-platforms/cyber-defense-suite",
        "https://www.tcs.com/what-we-do/industries/cybersecurity/managed-security-services",
        "https://www.tcs.com/who-we-are/alliances",
        "https://www.tcs.com/who-we-are/alliances/cybersecurity",
    ],
    # ── EXM additions (added v3) ──────────────────────────────────────
    "Noetic Cyber": [
        "https://www.noeticcyber.com/platform/",
        "https://www.noeticcyber.com/solutions/cyber-asset-attack-surface-management/",
        "https://www.noeticcyber.com/solutions/vulnerability-management/",
        "https://www.noeticcyber.com/solutions/cloud-security/",
    ],
    "Ionix (formerly Cyberpion)": [
        "https://ionix.io/platform/",
        "https://ionix.io/solutions/external-attack-surface-management/",
        "https://ionix.io/solutions/digital-supply-chain/",
        "https://ionix.io/solutions/threat-intelligence/",
    ],
    "Silentpush": [
        "https://www.silentpush.com/platform/",
        "https://www.silentpush.com/products/",
        "https://www.silentpush.com/solutions/attack-surface-management/",
        "https://www.silentpush.com/solutions/threat-intelligence/",
    ],
    "Fletch (formerly Cronus Cyber)": [
        "https://fletch.ai/platform/",
        "https://fletch.ai/solutions/",
        "https://fletch.ai/products/continuous-threat-exposure/",
        "https://fletch.ai/resources/",
    ],
    # ── ADR additions (added v3) ──────────────────────────────────────
    "Flashpoint": [
        "https://flashpoint.io/platform/",
        "https://flashpoint.io/products/threat-intelligence/",
        "https://flashpoint.io/products/vulnerability-intelligence/",
        "https://flashpoint.io/resources/",
    ],
    "Cyberint (Check Point)": [
        "https://cyberint.com/platform/",
        "https://cyberint.com/solutions/threat-intelligence/",
        "https://cyberint.com/solutions/digital-risk-protection/",
        "https://cyberint.com/solutions/attack-surface-management/",
    ],
    "Cybersixgill": [
        "https://cybersixgill.com/platform/",
        "https://cybersixgill.com/products/darkfeed/",
        "https://cybersixgill.com/solutions/threat-intelligence/",
        "https://cybersixgill.com/resources/",
    ],
    "Illusive Networks": [
        "https://www.illusive.com/platform/",
        "https://www.illusive.com/solutions/deception/",
        "https://www.illusive.com/solutions/attack-surface-reduction/",
        "https://www.illusive.com/solutions/identity-security/",
    ],
    "Sygnia": [
        "https://www.sygnia.co/services/",
        "https://www.sygnia.co/services/incident-response/",
        "https://www.sygnia.co/services/threat-intelligence/",
        "https://www.sygnia.co/services/proactive-security/",
    ],
    "Stroz Friedberg (Aon)": [
        "https://www.aon.com/cyber-solutions/stroz-friedberg/",
        "https://www.aon.com/cyber-solutions/incident-response/",
        "https://www.aon.com/cyber-solutions/digital-forensics/",
    ],
    # ── PPM additions (added v3) ──────────────────────────────────────
    "Zafran Security": [
        "https://www.zafran.io/platform/",
        "https://www.zafran.io/solutions/vulnerability-management/",
        "https://www.zafran.io/solutions/risk-prioritization/",
        "https://www.zafran.io/resources/",
    ],
    "Opus Security": [
        "https://www.opus.security/platform/",
        "https://www.opus.security/solutions/cloud-security-posture/",
        "https://www.opus.security/solutions/vulnerability-management/",
        "https://www.opus.security/integrations/",
    ],
    "Brinqa": [
        "https://www.brinqa.com/platform/",
        "https://www.brinqa.com/solutions/vulnerability-management/",
        "https://www.brinqa.com/solutions/attack-surface-intelligence/",
        "https://www.brinqa.com/solutions/risk-prioritization/",
    ],
    "PlexTrac": [
        "https://plextrac.com/platform/",
        "https://plextrac.com/solutions/penetration-testing/",
        "https://plextrac.com/solutions/vulnerability-management/",
        "https://plextrac.com/solutions/red-team/",
    ],
    "Hadrian": [
        "https://www.hadrian.io/platform/",
        "https://www.hadrian.io/solutions/autonomous-security-testing/",
        "https://www.hadrian.io/solutions/attack-surface-management/",
    ],
    "Veracode": [
        "https://www.veracode.com/platform",
        "https://www.veracode.com/products/binary-static-analysis-sast",
        "https://www.veracode.com/products/dynamic-analysis-dast",
        "https://www.veracode.com/products/software-composition-analysis",
        "https://www.veracode.com/products/penetration-testing",
    ],
    "Vulcan Cyber": [
        "https://vulcan.io/platform/",
        "https://vulcan.io/solutions/vulnerability-management/",
        "https://vulcan.io/solutions/risk-based-prioritization/",
        "https://vulcan.io/integrations/",
        "https://vulcan.io/resources/",
    ],
    # ── AMT additions (added v3) ──────────────────────────────────────
    "ColorTokens": [
        "https://colortokens.com/platform/",
        "https://colortokens.com/solutions/microsegmentation/",
        "https://colortokens.com/solutions/zero-trust/",
        "https://colortokens.com/solutions/ransomware-protection/",
    ],
    "Titaniam": [
        "https://titaniam.io/platform/",
        "https://titaniam.io/solutions/data-in-use-encryption/",
        "https://titaniam.io/solutions/ransomware-protection/",
    ],
    "Akeyless": [
        "https://www.akeyless.io/platform/",
        "https://www.akeyless.io/solutions/secrets-management/",
        "https://www.akeyless.io/solutions/machine-identity/",
        "https://www.akeyless.io/solutions/zero-trust/",
    ],
    "Aembit": [
        "https://aembit.io/platform/",
        "https://aembit.io/solutions/workload-identity/",
        "https://aembit.io/solutions/non-human-identity/",
    ],
}

# 3rd-party sources queried for ALL vendors (vendor name substituted)
THIRD_PARTY_SOURCES = [
    "https://www.gartner.com/reviews/search?query={vendor}+preemptive+cybersecurity",
]

# ─────────────────────────────────────────────────────────────────────
# User-Agents & HTML Parser
# ─────────────────────────────────────────────────────────────────────

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: List[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        text = data.strip()
        if text:
            self._chunks.append(text)

    def get_text(self) -> str:
        return "\n".join(self._chunks)


# ─────────────────────────────────────────────────────────────────────
# Utility functions
# ─────────────────────────────────────────────────────────────────────


def _safe_json_load(path: Path) -> Any:
    raw = path.read_text(encoding="utf-8-sig")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        obj, _ = decoder.raw_decode(raw.lstrip())
        return obj


def _avg(values: Iterable[float]) -> float:
    xs = list(values)
    return sum(xs) / len(xs) if xs else 0.0


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8"), usedforsecurity=False).hexdigest()


def _normalize_text(s: str) -> str:
    s = (s or "")
    s = s.replace("\ufffd", " ").replace("\u00a0", " ")
    s = s.replace("\u2014", "-").replace("\u2013", "-").replace("\u2212", "-")
    s = " ".join(s.split())
    return s


def _shorten(s: str, max_len: int = 220) -> str:
    s = _normalize_text(s)
    return s if len(s) <= max_len else s[:max_len - 1] + "\u2026"


def _html_to_text(html: str) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(html)
    text = unescape(parser.get_text())
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ─────────────────────────────────────────────────────────────────────
# HTTP Fetch with retry
# ─────────────────────────────────────────────────────────────────────


def _fetch_url_with_retry(
    url: str,
    *,
    max_retries: int = 2,
    timeouts: Tuple[float, ...] = (10.0, 15.0),
) -> Tuple[Optional[str], Optional[str]]:
    for attempt in range(max_retries):
        timeout = timeouts[min(attempt, len(timeouts) - 1)]
        ua = random.choice(USER_AGENTS)
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": ua,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "identity",
                "Connection": "keep-alive",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                ctype = resp.headers.get("Content-Type")
                raw = resp.read()
                try:
                    text = raw.decode("utf-8", errors="replace")
                except Exception:
                    text = raw.decode(errors="replace")
                return ctype, text
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, OSError):
            if attempt < max_retries - 1:
                backoff = (2 ** attempt) + random.uniform(0.5, 2.0)
                time.sleep(backoff)
            continue
    return None, None


# ─────────────────────────────────────────────────────────────────────
# Cache management — separate from TRiSM caches (pages_precyber/)
# ─────────────────────────────────────────────────────────────────────


def _cache_path_for_url(url: str) -> Path:
    return CACHE_DIR / f"{_sha1(url)}.json"


def get_or_fetch_page(url: str, *, force: bool) -> Dict[str, Any]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = _cache_path_for_url(url)

    if cache_path.exists() and not force:
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            if cached.get("ok") is True:
                return cached
        except Exception:
            pass

    ctype, html = _fetch_url_with_retry(url)

    if html is None:
        record = {
            "url": url, "fetched_at": datetime.now(timezone.utc).isoformat(),
            "ok": False, "content_type": ctype, "text": "", "error": "fetch_failed",
        }
    else:
        text = _html_to_text(html)
        record = {
            "url": url, "fetched_at": datetime.now(timezone.utc).isoformat(),
            "ok": True, "content_type": ctype, "text": text[:200_000], "error": None,
        }
    cache_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


# ─────────────────────────────────────────────────────────────────────
# Pillar-specific terms — differentiate scores per pillar/sub-pillar
# ─────────────────────────────────────────────────────────────────────

PILLAR_SPECIFIC_TERMS: Dict[str, List[str]] = {
    "EXM": [
        "attack surface management", "ASM", "EASM", "external attack surface",
        "asset discovery", "shadow IT", "digital footprint", "cyber asset management",
        "CTEM", "continuous threat exposure", "exposure management",
        "vulnerability prioritization", "risk-based vulnerability",
        "vulnerability management", "exploit prediction", "patch prioritization",
        "third-party risk", "supply chain security", "vendor risk management",
        "SBOM", "software supply chain", "open source risk",
        "CAASM", "exposure prioritization",
    ],
    "AMT": [
        "moving target defense", "AMTD", "polymorphic defense",
        "runtime randomization", "address space randomization",
        "memory randomization", "RASP", "runtime protection",
        "application shielding", "code instrumentation",
        "exploit prevention", "application hardening",
        "micro-segmentation", "software-defined perimeter",
        "zero trust network", "dynamic segmentation",
        "credential rotation", "ephemeral credentials",
        "key rotation", "token rotation", "just-in-time access",
        "secret rotation", "privileged access management",
        "ZTNA", "PAM",
    ],
    "ADR": [
        "deception technology", "honeypot", "honeytoken",
        "decoy", "breadcrumb", "cyber deception",
        "threat intelligence platform", "TIP",
        "threat intelligence operationalization",
        "IOC enrichment", "adversary tracking", "MITRE ATT&CK",
        "threat hunting", "proactive hunting",
        "managed threat hunting", "detection engineering",
        "counter-adversary", "adversary disruption",
        "takedown service", "dark web monitoring",
        "adversary attribution", "digital risk protection",
        "brand protection",
    ],
    "PPM": [
        "breach and attack simulation", "BAS",
        "attack simulation", "purple team",
        "control validation", "security validation",
        "adversary simulation", "security control validation",
        "control effectiveness", "detection validation",
        "penetration testing", "automated pentest",
        "red team", "attack path analysis", "PTaaS",
        "offensive security", "exploitation testing",
        "CSPM", "cloud security posture",
        "cloud misconfiguration", "CIEM", "CNAPP",
        "cloud workload protection", "cloud compliance",
    ],
}


# ─────────────────────────────────────────────────────────────────────
# Schema-driven term extraction for Preemptive Cybersecurity
# ─────────────────────────────────────────────────────────────────────

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "case",
    "could", "for", "from", "has", "have", "how", "if", "in", "into",
    "is", "it", "its", "may", "of", "on", "or", "our", "post",
    "should", "the", "their", "they", "this", "that", "these", "those",
    "to", "up", "use", "used", "using", "via", "was", "were", "will",
    "with", "without", "your", "you", "we",
}


def _build_precyber_subpillar_terms(schema: Dict[str, Any]) -> Dict[str, List[str]]:
    """Extract search terms per sub-pillar from the PreCyber schema.

    Uses:
      - sub_pillar name
      - expanded_definition
      - what_to_verify_publicly (analogous to TRiSM ai_evaluation_criteria)
      - search_terms (explicit in PreCyber schema)
      - pillar-specific terms
    """
    body = None
    for key in schema:
        if key.startswith("preemptive_cybersecurity_taxonomy"):
            body = schema[key]
            break
    if body is None:
        body = schema

    subs = body.get("sub_pillars", {})

    def _normalize(t: str) -> str:
        t = t.strip().lower()
        t = re.sub(r"[^a-z0-9\-\s/&]", " ", t)
        return re.sub(r"\s+", " ", t).strip()

    def _tokenize(phrase: str) -> List[str]:
        words = _normalize(phrase).replace("-", " ").split()
        return [w for w in words if len(w) >= 4 and w not in STOPWORDS]

    terms_by_sub: Dict[str, List[str]] = {}

    for sid in SUBPILLAR_IDS:
        info = subs.get(sid, {})
        pillar = sid.split("-")[0]

        # ── Schema-specific terms (highest priority) ──
        schema_terms: List[str] = []

        name = info.get("name", "")
        if name:
            schema_terms.append(name)

        defn = info.get("expanded_definition", "")
        if defn:
            schema_terms.append(defn)
            schema_terms.extend(_tokenize(defn))

        # what_to_verify_publicly = PreCyber's evaluation criteria
        criteria = info.get("what_to_verify_publicly", [])
        for c in criteria:
            if isinstance(c, str) and c.strip():
                schema_terms.append(c)
                schema_terms.extend(_tokenize(c))

        # search_terms = explicit terms from schema
        search = info.get("search_terms", [])
        for t in search:
            if isinstance(t, str) and t.strip():
                schema_terms.append(t.strip().lower())

        # ── Pillar-specific terms (medium priority) ──
        pillar_terms = PILLAR_SPECIFIC_TERMS.get(pillar, [])

        # Combine schema + pillar terms
        raw_terms = schema_terms + pillar_terms
        raw_terms.append(sid)

        cleaned: List[str] = []
        seen: set = set()
        for t in raw_terms:
            nt = _normalize(t)
            if len(nt) < 3 or len(nt.split()) > 10:
                continue
            if nt not in seen:
                cleaned.append(nt)
                seen.add(nt)

        terms_by_sub[sid] = cleaned

    return terms_by_sub


# Cache for schema criteria terms (what_to_verify_publicly)
_schema_criteria_terms_cache: Dict[str, set] = {}


def _build_schema_criteria_set(schema: Dict[str, Any]) -> Dict[str, set]:
    """Extract ONLY the what_to_verify_publicly per sub-pillar for weighting."""
    if _schema_criteria_terms_cache:
        return _schema_criteria_terms_cache

    body = None
    for key in schema:
        if key.startswith("preemptive_cybersecurity_taxonomy"):
            body = schema[key]
            break
    if body is None:
        body = schema

    subs = body.get("sub_pillars", {})

    def _normalize(t: str) -> str:
        t = t.strip().lower()
        t = re.sub(r"[^a-z0-9\-\s/&]", " ", t)
        return re.sub(r"\s+", " ", t).strip()

    for sid in SUBPILLAR_IDS:
        info = subs.get(sid, {})
        criteria = info.get("what_to_verify_publicly", [])
        cset = set()
        for c in criteria:
            if isinstance(c, str) and c.strip():
                cset.add(_normalize(c))
                # NOTE: Do NOT split phrases into individual words —
                # individual words like "automated", "monitoring" etc.
                # match on *every* cybersecurity page & inflate scores.
        # Also add search_terms from schema
        search = info.get("search_terms", [])
        for t in search:
            if isinstance(t, str) and t.strip():
                cset.add(_normalize(t))
        _schema_criteria_terms_cache[sid] = cset

    return _schema_criteria_terms_cache


# ─────────────────────────────────────────────────────────────────────
# Text analysis & evidence extraction
# ─────────────────────────────────────────────────────────────────────


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if 20 <= len(p.strip()) <= 420]


def _candidate_snippets(text: str) -> List[str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    snippets: List[str] = []
    for ln in lines:
        if 10 <= len(ln) <= 260:
            snippets.append(ln)
    for a, b in zip(lines, lines[1:]):
        combo = f"{a} {b}".strip()
        if 20 <= len(combo) <= 320:
            snippets.append(combo)
    snippets.extend(_split_sentences(text))

    seen: set = set()
    out: List[str] = []
    for s in snippets:
        key = s.lower()[:240]
        if key not in seen:
            seen.add(key)
            out.append(s)
    return out


@dataclass
class EvidenceHit:
    url: str
    excerpt: str
    matched_terms: List[str]
    relevance_score: int  # weighted relevance: schema_hits*3 + pillar_hits*2 + len


def _count_precyber_terms_in_text(text_lower: str) -> int:
    """Count how many preemptive cybersecurity terms appear in text."""
    return sum(1 for term in PRECYBER_PRIMARY_TERMS if _term_in_text(term.lower(), text_lower))


def _precyber_specificity_score(text_lower: str) -> float:
    """Score preemptive cyber specificity from 0-5 based on term density.

    Maps to the PreCyber scoring logic:
      0 = No Evidence
      1 = Minimal (basic / manual only)
      2 = Generic Claims (marketing, no named products)
      3 = Demonstrated (documented, named products)
      4 = Advanced (measurable outcomes, integration)
      5 = Market-Leading (best-in-class, analyst recognition)
    """
    hits = _count_precyber_terms_in_text(text_lower)
    exclusion_hits = sum(1 for t in PRECYBER_EXCLUSION_TERMS if t in text_lower)

    if exclusion_hits > hits:
        return 1.0

    if hits == 0:
        return 0.0
    if hits <= 2:
        return 2.0
    if hits <= 5:
        return 3.0
    if hits <= 10:
        return 4.0
    return 5.0


def _score_subpillar_precyber(
    specificity: float,
    criteria_hit_count: int,
    total_excerpts: int,
) -> float:
    """Preemptive Cybersecurity–weighted scoring.

    Scoring scale from Preemptive_Cybersecurity_Schema.json:
      0 = No Evidence
      1 = Minimal
      2 = Generic Claims
      3 = Demonstrated
      4 = Advanced
      5 = Market-Leading
    """
    if total_excerpts == 0:
        return 0.0

    if specificity < 0.5:
        if criteria_hit_count > 0:
            return 1.0
        return 0.0

    if specificity <= 2.0:
        base = 2.0
        if criteria_hit_count >= 3:
            base = 2.25
        return base

    if specificity <= 3.0:
        base = 3.0
        if criteria_hit_count >= 5:
            base = 3.25
        elif criteria_hit_count >= 3:
            base = 3.0
        else:
            base = 2.75
        return base

    if specificity <= 4.0:
        base = 4.0
        if criteria_hit_count >= 5:
            base = 4.25
        elif criteria_hit_count >= 3:
            base = 4.0
        else:
            base = 3.75
        return base

    # Market-Leading
    base = 4.5
    if criteria_hit_count >= 5:
        base = 4.75
    return base


def compute_pillar_scores(sub_scores: Dict[str, float]) -> Dict[str, float]:
    """Average sub-pillar scores into pillar scores."""
    result: Dict[str, float] = {}
    for pillar in PILLARS:
        sp_ids = [f"{pillar}-{i:02d}" for i in range(1, 5)]
        vals = [sub_scores.get(sp, 0.0) for sp in sp_ids]
        result[pillar] = round(_avg(vals), 2)
    return result


# ─────────────────────────────────────────────────────────────────────
# URL Discovery for PreCyber vendors
# ─────────────────────────────────────────────────────────────────────


def discover_vendor_urls(vendor: Dict[str, Any], *, max_urls: int = 0) -> List[str]:
    """Discover URLs for a vendor. max_urls=0 means unlimited."""
    vendor_name = vendor.get("vendor", "")
    urls: List[str] = []
    seen: set = set()

    def _add(u: str) -> None:
        u_clean = u.lower().rstrip("/")
        if u_clean not in seen and (max_urls == 0 or len(urls) < max_urls):
            seen.add(u_clean)
            urls.append(u)

    # 1. Curated URLs from VENDOR_URLS
    if vendor_name in VENDOR_URLS:
        for u in VENDOR_URLS[vendor_name]:
            _add(u)

    # 2. URLs from capability_analysis field
    cap_text = vendor.get("capability_analysis") or ""
    for u in URL_RE.findall(cap_text):
        _add(u)

    # 3. capability_analysis_source
    src = vendor.get("capability_analysis_source")
    if src:
        _add(src)

    return urls if max_urls == 0 else urls[:max_urls]


# ─────────────────────────────────────────────────────────────────────
# Evidence extraction (per vendor) — PreCyber-focused
# ─────────────────────────────────────────────────────────────────────


GENERIC_MATCH_TERMS = {
    "security", "platform", "dashboard", "workflow", "automation",
    "analysis", "detection", "response", "compliance", "monitoring",
    "protection", "management", "assessment",
}


def _vendor_flag(*, urls: List[str], ok_pages: int, excerpts_total: int) -> Tuple[str, float]:
    if not urls:
        return "no_urls", 0.0
    if ok_pages == 0:
        return "fetch_failed", 0.0
    coverage = max(0.0, min(1.0, excerpts_total / 15.0))
    if excerpts_total == 0:
        return "no_evidence", 0.1
    if coverage < 0.3:
        return "low_evidence", 0.35
    if coverage < 0.7:
        return "partial_evidence", 0.6
    return "good_evidence", 0.8


def evidence_for_vendor(
    vendor: Dict[str, Any],
    *,
    urls: List[str],
    terms_by_subpillar: Dict[str, List[str]],
    schema: Dict[str, Any],
    force_fetch: bool,
    max_excerpts_per_subpillar: int,
    sleep_seconds: float,
) -> Tuple[Dict[str, Any], Dict[str, float]]:
    """Extract preemptive-cyber evidence and compute per-sub-pillar scores.

    Each sub-pillar gets its own specificity score based on:
    1. Schema-specific criteria matches (what_to_verify_publicly) — highest weight
    2. Pillar-specific term matches — medium weight
    3. Only generic terms — lowest weight
    """

    page_records: List[Dict[str, Any]] = []
    for u in urls:
        rec = get_or_fetch_page(u, force=force_fetch)
        page_records.append(rec)
        delay = sleep_seconds + random.uniform(0.5, 2.0)
        time.sleep(delay)

    pages_text: List[Tuple[str, str]] = []
    for rec in page_records:
        if rec.get("ok") is True and isinstance(rec.get("text"), str):
            pages_text.append((rec["url"], rec["text"]))

    ok_pages = len(pages_text)

    # Get schema criteria sets for differentiated scoring
    criteria_sets = _build_schema_criteria_set(schema)

    sub_evidence: Dict[str, Any] = {}
    sub_scores: Dict[str, float] = {}

    for sid in SUBPILLAR_IDS:
        pillar = sid.split("-")[0]
        terms = terms_by_subpillar.get(sid, [])
        pillar_terms_set = set(PILLAR_SPECIFIC_TERMS.get(pillar, []))
        criteria_set = criteria_sets.get(sid, set())
        hits: List[EvidenceHit] = []

        for url, text in pages_text:
            candidates = _candidate_snippets(text)

            for sent in candidates:
                s_lower = sent.lower()
                matched = _matched_terms_in_text(terms, s_lower)
                if not matched:
                    continue

                # Count matches by specificity tier
                schema_hits = sum(1 for t in matched
                                  if t in criteria_set or
                                  any(_term_in_text(c_term, s_lower) for c_term in criteria_set if len(c_term) >= 3))
                pillar_hits = sum(1 for t in matched if t in pillar_terms_set)
                relevance_score = schema_hits * 3 + pillar_hits * 2 + len(matched)

                hits.append(EvidenceHit(
                    url=url, excerpt=sent.strip(),
                    matched_terms=matched[:10],
                    relevance_score=relevance_score,
                ))

        # Sort by relevance descending, take top N
        hits.sort(key=lambda h: h.relevance_score, reverse=True)
        top_hits = hits[:max_excerpts_per_subpillar]

        # ── Per-sub-pillar specificity scoring ──
        all_text_lower = " ".join(t for _, t in pages_text).lower()

        pillar_term_hits = sum(1 for t in pillar_terms_set if _term_in_text(t, all_text_lower))
        schema_criteria_hits = sum(1 for t in criteria_set if len(t) >= 3 and _term_in_text(t, all_text_lower))

        # Compute sub-pillar specificity
        if pages_text:
            if schema_criteria_hits >= 4:
                sp_specificity = 5.0
            elif schema_criteria_hits >= 3:
                sp_specificity = 4.0
            elif schema_criteria_hits >= 2 and pillar_term_hits >= 3:
                sp_specificity = 3.5
            elif schema_criteria_hits >= 1 and pillar_term_hits >= 2:
                sp_specificity = 3.0
            elif pillar_term_hits >= 3:
                sp_specificity = 2.5
            elif pillar_term_hits >= 1:
                sp_specificity = 2.0
            elif any(_term_in_text(t.lower(), all_text_lower) for t in PRECYBER_PRIMARY_TERMS):
                sp_specificity = 1.5
            else:
                sp_specificity = 0.0
        else:
            sp_specificity = 0.0

        # Check exclusion terms
        exclusion_hits = sum(1 for t in PRECYBER_EXCLUSION_TERMS if t in all_text_lower) if pages_text else 0
        if exclusion_hits > pillar_term_hits + schema_criteria_hits:
            sp_specificity = max(0.0, sp_specificity - 1.0)

        # Score using per-sub-pillar specificity
        criteria_hit_count = sum(1 for h in top_hits if h.relevance_score > 2)
        score = _score_subpillar_precyber(sp_specificity, criteria_hit_count, len(top_hits))

        sub_evidence[sid] = {
            "source_urls": list({h.url for h in top_hits}),
            "excerpts": [
                {
                    "url": h.url,
                    "excerpt": _shorten(h.excerpt, 260),
                    "matched_terms": h.matched_terms[:6],
                    "relevance_score": h.relevance_score,
                }
                for h in top_hits
            ],
            "sub_pillar_specificity": round(sp_specificity, 2),
            "schema_criteria_hits": schema_criteria_hits,
            "pillar_term_hits": pillar_term_hits,
            "criteria_hit_count": criteria_hit_count,
            "notes": f"PreCyber evidence extraction; {len(top_hits)} excerpts from {ok_pages} pages."
        }
        sub_scores[sid] = round(score, 2)

    # Vendor summary
    total_excerpts = sum(len(sub_evidence[sid]["excerpts"]) for sid in SUBPILLAR_IDS)
    flag, confidence = _vendor_flag(urls=urls, ok_pages=ok_pages, excerpts_total=total_excerpts)

    sub_evidence["_vendor_summary"] = {
        "ok_pages": ok_pages,
        "total_pages": len(page_records),
        "excerpts_total": total_excerpts,
        "flag": flag,
        "confidence": round(confidence, 2),
    }

    return sub_evidence, sub_scores


# ─────────────────────────────────────────────────────────────────────
# Rationale builder
# ─────────────────────────────────────────────────────────────────────


def _subpillar_name_from_schema(schema: Dict[str, Any], sid: str) -> str:
    body = None
    for key in schema:
        if key.startswith("preemptive_cybersecurity_taxonomy"):
            body = schema[key]
            break
    if body is None:
        body = schema
    subs = body.get("sub_pillars", {})
    sp = subs.get(sid, {})
    return sp.get("name", sid) if isinstance(sp, dict) else sid


def build_rationale(
    schema: Dict[str, Any],
    vendor: Dict[str, Any],
    sid: str,
    sub_evidence: Dict[str, Any],
    sub_scores: Dict[str, float],
    research_flag: str,
) -> str:
    name = _subpillar_name_from_schema(schema, sid)
    score = sub_scores.get(sid, 0.0)
    score_str = f"{score:.2f}/5"

    ev = sub_evidence.get(sid, {})
    excerpts_raw = ev.get("excerpts", [])
    sp_specificity = ev.get("sub_pillar_specificity", 0.0)

    evidence_line = "No preemptive-cyber evidence captured."
    if excerpts_raw:
        first = excerpts_raw[0]
        excerpt_text = _shorten(str(first.get("excerpt", "")), 200)
        evidence_line = f'Evidence: "{excerpt_text}".'
        if len(excerpts_raw) > 1:
            second = _shorten(str(excerpts_raw[1].get("excerpt", "")), 150)
            evidence_line += f' Also: "{second}".'

    maturity_level = "None"
    if sp_specificity >= 4.5:
        maturity_level = "Market-Leading"
    elif sp_specificity >= 3.5:
        maturity_level = "Advanced"
    elif sp_specificity >= 2.5:
        maturity_level = "Demonstrated"
    elif sp_specificity >= 1.5:
        maturity_level = "Generic Claims"
    elif sp_specificity >= 0.5:
        maturity_level = "Minimal"

    parts = [
        f"{sid} - {name}. Score: {score_str}.",
        f"Maturity Level: {maturity_level} (specificity={sp_specificity:.1f}).",
        f"Evidence flag: {research_flag}.",
        evidence_line,
    ]

    if score < 3.0:
        parts.append(
            "To improve: Publicly document specific preemptive capabilities with "
            "named products, measurable outcomes, and technical details."
        )

    return " ".join(p.strip() for p in parts if p and str(p).strip())


# ─────────────────────────────────────────────────────────────────────
# Checkpoint management (per-batch)
# ─────────────────────────────────────────────────────────────────────


def _batch_checkpoint_path(batch_num: int) -> Path:
    BATCH_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return BATCH_OUTPUT_DIR / f"batch_{batch_num:02d}.json"


def _progress_checkpoint_path() -> Path:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    return CHECKPOINT_DIR / "precyber_evidence_progress.json"


def _load_progress() -> Dict[str, Any]:
    cp = _progress_checkpoint_path()
    if cp.exists():
        try:
            return json.loads(cp.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"completed_batches": [], "completed_vendors": []}


def _save_progress(progress: Dict[str, Any]) -> None:
    _progress_checkpoint_path().write_text(
        json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _save_batch(batch_num: int, vendors: List[Dict[str, Any]]) -> None:
    path = _batch_checkpoint_path(batch_num)
    path.write_text(
        json.dumps(vendors, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ─────────────────────────────────────────────────────────────────────
# Merge all batches into final output
# ─────────────────────────────────────────────────────────────────────


def merge_batches(input_file: Path, output_file: Path) -> int:
    """Merge all batch outputs into the final vendor file."""
    BATCH_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    batch_files = sorted(BATCH_OUTPUT_DIR.glob("batch_*.json"))
    if not batch_files:
        print("No batch output files found in", BATCH_OUTPUT_DIR)
        return 1

    # Collect all scored vendors
    scored_vendors: Dict[str, Dict[str, Any]] = {}
    for bf in batch_files:
        try:
            batch_data = json.loads(bf.read_text(encoding="utf-8"))
            if isinstance(batch_data, list):
                for v in batch_data:
                    name = v.get("vendor", "")
                    if name:
                        scored_vendors[name] = v
        except Exception as e:
            print(f"  Warning: error reading {bf.name}: {e}")
    print(f"Loaded {len(scored_vendors)} scored vendors from {len(batch_files)} batch files")

    # Load original seed file
    seed_data = _safe_json_load(input_file)
    if isinstance(seed_data, dict) and "vendors" in seed_data:
        seed_vendors = seed_data["vendors"]
    else:
        print("Unexpected seed file format")
        return 1

    # Merge: replace seed vendors with scored versions, keep order
    merged = []
    scored_count = 0
    for v in seed_vendors:
        name = v.get("vendor", "")
        if name in scored_vendors:
            merged.append(scored_vendors[name])
            scored_count += 1
        else:
            merged.append(v)

    # Write output
    out_data = {
        "schema_ref": "Preemptive_Cybersecurity_Schema.json",
        "schema_version": "1.0",
        "vendor_count": len(merged),
        "research_tool": "research_precyber_v1_evidence.py",
        "research_timestamp": datetime.now(timezone.utc).isoformat(),
        "vendors": merged,
    }
    output_file.write_text(
        json.dumps(out_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nWrote merged output: {output_file.name}")
    print(f"  {len(merged)} vendors total, {scored_count} with PreCyber scores")
    return 0


# ─────────────────────────────────────────────────────────────────────
# Main — batch-of-5 processing loop
# ─────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description="Preemptive Cybersecurity Vendor Evidence Research")
    parser.add_argument("--input-file", type=Path, default=DEFAULT_INPUT_FILE)
    parser.add_argument("--schema-file", type=Path, default=DEFAULT_SCHEMA_FILE)
    parser.add_argument("--output-file", type=Path, default=DEFAULT_OUTPUT_FILE)
    parser.add_argument("--batch-size", type=int, default=5,
                        help="Vendors per batch (default: 5)")
    parser.add_argument("--batch-pause", type=float, default=30.0,
                        help="Seconds to pause between batches (default: 30)")
    parser.add_argument("--sleep-seconds", type=float, default=1.0,
                        help="Seconds between URL fetches (default: 1)")
    parser.add_argument("--max-vendors", type=int, default=0,
                        help="Limit total vendors (0=all)")
    parser.add_argument("--max-urls-per-vendor", type=int, default=0,
                        help="Max URLs per vendor (0=unlimited, default: 0)")
    parser.add_argument("--max-excerpts-per-subpillar", type=int, default=5,
                        help="Max evidence excerpts per sub-pillar (default: 5)")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from last checkpoint")
    parser.add_argument("--merge-only", action="store_true",
                        help="Just merge existing batch outputs into final file")
    parser.add_argument("--force-fetch", action="store_true",
                        help="Re-fetch cached pages")
    args = parser.parse_args()

    # ── Merge-only mode ──
    if args.merge_only:
        return merge_batches(args.input_file, args.output_file)

    # ── Load schema ──
    print(f"Loading schema: {args.schema_file.name}")
    schema = _safe_json_load(args.schema_file)
    terms_by_sub = _build_precyber_subpillar_terms(schema)
    for sid in SUBPILLAR_IDS:
        print(f"  {sid}: {len(terms_by_sub.get(sid, []))} terms")

    # ── Load vendors ──
    print(f"\nLoading vendors: {args.input_file.name}")
    input_data = _safe_json_load(args.input_file)
    if isinstance(input_data, dict) and "vendors" in input_data:
        all_vendors = input_data["vendors"]
    elif isinstance(input_data, list):
        all_vendors = input_data
    else:
        print("Unexpected input file format")
        return 1

    # Sort alphabetically for consistent batching
    all_vendors.sort(key=lambda v: v.get("vendor", "").lower())

    # Apply limit
    limit = args.max_vendors if args.max_vendors > 0 else len(all_vendors)
    target_vendors = all_vendors[:limit]
    print(f"  {len(target_vendors)} vendors to process")

    # ── Resume support ──
    progress = _load_progress() if args.resume else {"completed_batches": [], "completed_vendors": []}
    completed_batches = set(progress.get("completed_batches", []))

    # ── Build batches ──
    batches: List[List[Dict[str, Any]]] = []
    for i in range(0, len(target_vendors), args.batch_size):
        batches.append(target_vendors[i:i + args.batch_size])

    total_batches = len(batches)
    print(f"  {total_batches} batches of {args.batch_size}")

    # ── Process batches ──
    started = datetime.now(timezone.utc)

    for batch_idx, batch in enumerate(batches, start=1):
        batch_names = [v.get("vendor", "?") for v in batch]
        batch_label = f"[Batch {batch_idx}/{total_batches}]"

        if batch_idx in completed_batches:
            print(f"\n{batch_label} SKIPPED (checkpoint): {', '.join(batch_names)}")
            continue

        print(f"\n{'='*70}")
        print(f"{batch_label} Processing: {', '.join(batch_names)}")
        print(f"{'='*70}")

        batch_results: List[Dict[str, Any]] = []

        for v_idx, vendor in enumerate(batch, start=1):
            name = vendor.get("vendor", "Unknown")
            print(f"\n  [{v_idx}/{len(batch)}] {name}: discovering URLs...")

            urls = discover_vendor_urls(vendor, max_urls=args.max_urls_per_vendor)
            print(f"    Found {len(urls)} URLs")
            for u in urls:
                print(f"      {u}")

            sub_evidence, sub_scores = evidence_for_vendor(
                vendor,
                urls=urls,
                terms_by_subpillar=terms_by_sub,
                schema=schema,
                force_fetch=args.force_fetch,
                max_excerpts_per_subpillar=args.max_excerpts_per_subpillar,
                sleep_seconds=args.sleep_seconds,
            )

            vendor_summary = sub_evidence.get("_vendor_summary", {})
            research_flag = vendor_summary.get("flag", "unknown")
            research_confidence = vendor_summary.get("confidence", 0.0)

            # Apply 3.0 cap for non-good_evidence vendors
            cap_applied = False
            if research_flag != "good_evidence":
                for sid in list(sub_scores.keys()):
                    if float(sub_scores[sid]) > 3.0:
                        sub_scores[sid] = 3.0
                        cap_applied = True

            precyber_pillars = compute_pillar_scores(sub_scores)

            # Build rationales
            rationale: Dict[str, str] = {}
            for sid in SUBPILLAR_IDS:
                rationale[sid] = build_rationale(
                    schema, vendor, sid,
                    sub_evidence, sub_scores,
                    research_flag,
                )

            # Update vendor record — PreCyber-specific keys
            v_out = dict(vendor)
            v_out["sub_pillar_evidence"] = sub_evidence
            v_out["sub_pillar_scores_validated"] = sub_scores
            v_out["pillar_scores_validated"] = precyber_pillars
            v_out["pillar_scores"] = precyber_pillars
            v_out["sub_pillar_scores_current"] = sub_scores
            v_out["sub_pillar_rationale_validated"] = rationale
            v_out["research_flag"] = research_flag
            v_out["research_confidence"] = research_confidence
            v_out["research"] = {
                "status": "precyber_validated_v1",
                "source": "public_web_text",
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "urls_used": urls,
                "pages_ok": vendor_summary.get("ok_pages", 0),
                "schema": args.schema_file.name,
                "tool": "research_precyber_v1_evidence.py",
                "cap_applied": cap_applied,
            }

            batch_results.append(v_out)

            ok_pages = vendor_summary.get("ok_pages", 0)
            excerpts = vendor_summary.get("excerpts_total", 0)
            print(f"    Pages OK: {ok_pages}/{len(urls)}, Excerpts: {excerpts}, "
                  f"Flag: {research_flag}")
            print(f"    Pillar scores: EXM={precyber_pillars.get('EXM',0):.2f} "
                  f"AMT={precyber_pillars.get('AMT',0):.2f} "
                  f"ADR={precyber_pillars.get('ADR',0):.2f} "
                  f"PPM={precyber_pillars.get('PPM',0):.2f}")

        # ── Save batch checkpoint ──
        _save_batch(batch_idx, batch_results)
        progress["completed_batches"].append(batch_idx)
        progress["completed_vendors"].extend([v.get("vendor", "") for v in batch_results])
        _save_progress(progress)

        print(f"\n{batch_label} SAVED: {len(batch_results)} vendors")
        print(f"  Batch file: {_batch_checkpoint_path(batch_idx).name}")

        # ── Pause between batches ──
        if batch_idx < total_batches:
            print(f"  Pausing {args.batch_pause:.0f}s before next batch...")
            time.sleep(args.batch_pause)

    # ── Merge all batches ──
    print(f"\n{'='*70}")
    print("Merging all batches into final output...")
    print(f"{'='*70}")
    merge_result = merge_batches(args.input_file, args.output_file)

    elapsed = datetime.now(timezone.utc) - started
    print(f"\nTotal elapsed: {elapsed}")

    # Clear progress checkpoint
    cp = _progress_checkpoint_path()
    if cp.exists():
        cp.unlink()
        print("Progress checkpoint cleared.")

    return merge_result


if __name__ == "__main__":
    raise SystemExit(main())
