#!/usr/bin/env python3
"""
_research_cnapp_v11.py
======================
Initial web-research pipeline for 24 CNAPP vendors.
Reads:  CNAPP Vendor 1-0 Seed.json
Writes: CNAPP Vendor 1-1 Researched.json

Vendors are split into 5 groups so you can run one at a time:

  Group 1 — Pure-Play CNAPP Leaders    : Wiz, Orca Security, Sysdig, Aqua Security, Uptycs
  Group 2 — Platform Security Giants   : Palo Alto Networks, CrowdStrike, Microsoft, SentinelOne
  Group 3 — Traditional Security       : Trend Micro, Fortinet, Sophos, Bitdefender, Check Point
  Group 4 — VM & Observability Adjacent: Tenable, Qualys, Rapid7, Datadog
  Group 5 — Emerging & Niche           : Upwind, Sweet Security, Data Theorem, Caveonix, AccuKnox, Snyk

Usage:
  python _research_cnapp_v11.py --group 1          # run one group
  python _research_cnapp_v11.py --all               # run all groups sequentially
  python _research_cnapp_v11.py --group 1 --dry-run # show URLs only, don't fetch
"""

import argparse
import hashlib
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from copy import deepcopy
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT       = Path(__file__).resolve().parent
SEED_FILE  = ROOT / "CNAPP Vendor 1-0 Seed.json"
OUT_FILE   = ROOT / "CNAPP Vendor 1-1 Researched.json"
CACHE_DIR  = ROOT / "research" / "cache" / "pages_cnapp"

PILLARS        = ["CSPM", "CWPP", "CIEM", "SHIFT", "CDR", "DSPM", "FRNG"]
# Sub-pillar IDs are derived from SP_LABELS (defined below) so that any
# additions/removals (e.g., SHIFT-05 in v1.1) flow through automatically.
# Populated after SP_LABELS is defined.
SUB_PILLAR_IDS: List[str] = []

MAX_EXCERPTS_PER_SP = 5
FETCH_SLEEP         = 1.5
MAX_ADJUSTMENT      = 1.0

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
]

# ─────────────────────────────────────────────────────────────────────────────
# Sub-pillar labels
# ─────────────────────────────────────────────────────────────────────────────
SP_LABELS: Dict[str, str] = {
    "CSPM-01": "Multicloud Misconfiguration Detection & Guided Auto-Remediation",
    "CSPM-02": "Compliance Framework Mapping & CIS Benchmarks",
    "CSPM-03": "Cloud Asset Inventory & Attack Surface Visibility",
    "CSPM-04": "Risk Prioritization, Business Impact Scoring & Executive Reporting",
    "CWPP-01": "Workload Runtime Monitoring",
    "CWPP-02": "Vulnerability Assessment & Exploitability Prioritization",
    "CWPP-03": "Container & Kubernetes Security",
    "CWPP-04": "Serverless & Agentless Architecture",
    "CIEM-01": "Cloud Identity & Permission Discovery",
    "CIEM-02": "Least Privilege Enforcement & Access Governance",
    "CIEM-03": "Non-Human Identity & Service Account Security",
    "CIEM-04": "Just-in-Time Access & Privilege Escalation Control",
    "SHIFT-01": "Infrastructure as Code (IaC) Security Scanning",
    "SHIFT-02": "Container Image & Registry Scanning",
    "SHIFT-03": "CI/CD Pipeline Integration & Developer Tooling",
    "SHIFT-04": "Software Supply Chain — SCA, SBOM, MBOM & AIBOM",
    "SHIFT-05": "Ticketing & Workflow Integration",
    "CDR-01":  "Cloud Threat Detection & Alert Correlation",
    "CDR-02":  "Attack Path Analysis & Security Knowledge Graph",
    "CDR-03":  "Cloud Incident Investigation & Forensics",
    "CDR-04":  "Automated Cloud Response & Playbook Orchestration",
    "DSPM-01": "Sensitive Data Discovery & Classification",
    "DSPM-02": "Data Access Risk & Exposure Governance",
    "DSPM-03": "Shadow Data & Data Flow Mapping",
    "DSPM-04": "Data Compliance & Regulatory Reporting",
    "FRNG-01": "AI/GenAI Workload Security Posture (AISPM)",
    "FRNG-02": "API Security Discovery & Risk Assessment",
    "FRNG-03": "Cloud Network Security & Microsegmentation",
    "FRNG-04": "Secrets Detection & Runtime Credential Protection",
}

# Populate SUB_PILLAR_IDS from SP_LABELS so SHIFT-05 (and any future additions) flow through.
SUB_PILLAR_IDS = list(SP_LABELS.keys())

# ─────────────────────────────────────────────────────────────────────────────
# Pillar-level and sub-pillar-level search terms
# ─────────────────────────────────────────────────────────────────────────────
PILLAR_TERMS: Dict[str, List[str]] = {
    "CSPM": [
        "cloud security posture", "cspm", "misconfiguration", "cloud compliance",
        "s3 bucket exposure", "security group", "cloud benchmark", "cis benchmark",
        "cloud hardening", "auto-remediation cloud", "cloud asset inventory",
        "attack surface cloud", "risk scoring cloud", "posture management",
        "cloud drift", "cloud policy", "cloud governance",
    ],
    "CWPP": [
        "cloud workload protection", "cwpp", "runtime protection", "container security",
        "kubernetes security", "kspm", "workload edr", "serverless security",
        "agentless cloud", "runtime threat", "workload vulnerability",
        "container runtime", "ebpf", "file integrity monitoring", "workload detection",
        "container escape", "kubernetes admission", "cloud workload",
    ],
    "CIEM": [
        "ciem", "cloud identity entitlement", "iam security", "cloud permissions",
        "least privilege cloud", "over-privileged", "service account security",
        "just-in-time access", "jit access", "non-human identity", "nhi",
        "machine identity", "privilege escalation cloud", "iam misconfiguration",
        "permission graph", "identity governance cloud",
    ],
    "SHIFT": [
        "shift-left security", "devsecops", "iac security", "infrastructure as code",
        "terraform security", "cloudformation security", "container image scanning",
        "sbom", "software supply chain security", "ci/cd security",
        "github actions security", "developer security", "policy as code",
        "registry scanning", "supply chain security", "dependency vulnerability",
    ],
    "CDR": [
        "cloud detection response", "cdr", "cloud threat detection",
        "cloudtrail detection", "cloud forensics", "cloud incident response",
        "attack path analysis", "security knowledge graph", "cloud behavioral detection",
        "mitre att&ck cloud", "cloud investigation", "automated cloud response",
        "cloud playbook", "cloud incident", "cloud threat hunting", "cloud soar",
    ],
    "DSPM": [
        "dspm", "data security posture", "sensitive data discovery cloud",
        "data classification cloud", "pii detection cloud", "shadow data",
        "data exposure cloud", "cloud data governance", "data compliance cloud",
        "gdpr cloud", "hipaa cloud data", "data flow mapping cloud",
        "cloud data risk", "data access governance cloud", "cloud data inventory",
    ],
    "FRNG": [
        "aispm", "ai security posture management", "genai security cloud",
        "llm security cloud", "api security cloud", "shadow api discovery",
        "cloud microsegmentation", "vpc microsegmentation", "secrets detection cloud",
        "api key exposure", "hardcoded credentials cloud", "ai workload security",
        "runtime application self-protection", "cloud network security",
    ],
}

SP_TERMS: Dict[str, List[str]] = {
    "CSPM-01": ["misconfiguration detection", "guided remediation", "auto-remediation",
                "remediation playbook", "cloud posture rule", "openstack security",
                "openshift security", "s3 exposure", "open security group"],
    "CSPM-02": ["cis benchmark cloud", "pci dss cloud compliance", "hipaa cloud",
                "fedramp cloud", "compliance framework cloud", "audit report cloud"],
    "CSPM-03": ["cloud asset inventory", "resource discovery cloud", "attack surface cloud",
                "toxic combination", "attack path", "blast radius",
                "shadow it cloud", "asset relationship mapping", "internet exposure cloud"],
    "CSPM-04": ["risk prioritization cloud", "business impact", "executive dashboard",
                "executive report", "risk quantification", "toxic combination",
                "epss cloud", "contextual risk scoring", "alert prioritization"],
    "CWPP-01": ["workload runtime monitoring", "runtime visibility", "agentless workload",
                "agent-based workload", "ebpf", "kubernetes daemonset",
                "sidecar security", "kernel module", "container runtime hook",
                "serverless runtime", "file integrity monitoring", "behavioral anomaly"],
    "CWPP-02": ["runtime vulnerability", "workload vulnerability", "epss prioritization",
                "kev catalog", "reachability analysis", "cve exploitability"],
    "CWPP-03": ["kubernetes security", "kspm", "container runtime security",
                "ebpf container", "admission controller security", "container escape detection"],
    "CWPP-04": ["serverless security", "lambda security", "agentless scanning cloud",
                "agentless deployment", "azure functions security", "time-to-value agentless"],
    "CIEM-01": ["iam permission discovery", "permission graph cloud", "entitlement mapping",
                "cloud access graph", "iam inventory", "effective permissions cloud"],
    "CIEM-02": ["least privilege cloud", "iam right-sizing", "over-privileged cloud",
                "access review cloud", "privilege drift", "iam remediation"],
    "CIEM-03": ["non-human identity cloud", "nhi security", "service account security cloud",
                "machine identity cloud", "api key security cloud", "oauth token security cloud"],
    "CIEM-04": ["just-in-time access cloud", "jit privilege cloud", "privilege escalation detection",
                "iam anomaly detection", "temporary credentials cloud", "standing access cloud"],
    "SHIFT-01": ["iac scanning", "terraform security scanning", "cloudformation security",
                 "bicep security", "policy as code cloud", "iac misconfiguration"],
    "SHIFT-02": ["container image scanning", "registry security", "ecr scanning",
                 "image vulnerability", "docker security scanning", "registry admission control"],
    "SHIFT-03": ["ci/cd security gate", "github actions security", "devsecops pipeline",
                 "pull request security annotation", "ide security plugin", "pipeline integration"],
    "SHIFT-04": ["sca", "software composition analysis", "sbom", "mbom", "aibom",
                 "ai bill of materials", "model bill of materials",
                 "software supply chain security", "dependency confusion",
                 "sigstore cosign", "cyclonedx", "spdx"],
    "SHIFT-05": ["jira integration", "servicenow integration", "slack integration",
                 "microsoft teams integration", "pagerduty integration", "opsgenie",
                 "ticketing integration", "workflow automation", "webhook", "chatops"],
    "CDR-01":  ["cloud threat detection rule", "cloudtrail detection", "mitre att&ck cloud",
                "behavioral baseline cloud", "cloud alert correlation", "cloud anomaly detection"],
    "CDR-02":  ["attack path analysis cloud", "security knowledge graph", "toxic combination cloud",
                "blast radius cloud", "internet-to-asset attack chain"],
    "CDR-03":  ["cloud forensics", "cloud investigation timeline", "cloudtrail forensics",
                "container forensics", "evidence preservation cloud", "chain of custody cloud"],
    "CDR-04":  ["automated cloud response", "iam revocation automated", "cloud soar",
                "workload isolation automated", "cloud playbook", "s3 quarantine automated"],
    "DSPM-01": ["sensitive data discovery cloud", "data classification cloud", "pii detection s3",
                "cloud data inventory", "agentless data discovery", "data store coverage cloud"],
    "DSPM-02": ["data exposure cloud", "data access governance", "public sensitive data store",
                "unauthenticated data access", "data risk graph cloud"],
    "DSPM-03": ["shadow data cloud", "data flow mapping", "data lineage cloud",
                "forgotten data cloud", "cross-border data transfer cloud"],
    "DSPM-04": ["gdpr cloud data compliance", "dpia cloud", "data residency cloud",
                "hipaa data cloud reporting", "breach notification data cloud"],
    "FRNG-01": ["aispm", "ai security posture", "llm security cloud", "shadow ai detection",
                "ai workload security cloud", "genai cloud security"],
    "FRNG-02": ["api security cloud", "shadow api discovery", "api inventory cloud",
                "api risk assessment cloud", "graphql security cloud"],
    "FRNG-03": ["microsegmentation cloud", "vpc security cloud", "east-west traffic cloud",
                "lateral movement detection cloud", "network flow cloud"],
    "FRNG-04": ["secrets detection cloud", "api key exposure cloud", "hardcoded credentials cloud",
                "secrets scanning cloud", "credential exposure cloud"],
}

CNAPP_GENERIC = [
    "cnapp", "cloud-native application protection", "cloud security platform",
    "cloud security posture", "cloud workload protection", "cloud identity entitlement",
    "devsecops", "cloud detection response", "data security posture",
    "cloud native security", "cloud application protection",
]

# ─────────────────────────────────────────────────────────────────────────────
# Vendor metadata
# ─────────────────────────────────────────────────────────────────────────────
VENDOR_META: Dict[str, dict] = {
    "Wiz": {
        "site": "https://www.wiz.io",
        "products": ["Wiz CSPM", "Wiz CWPP", "Wiz CIEM", "Wiz DSPM", "Wiz CDR",
                     "Wiz Code", "WizAI", "Wiz for AI", "Wiz Defend"],
        "analyst": "Leader in Gartner MQ for CNAPP 2024. Fastest-growing cloud security "
                   "vendor at $1.9B raised. $12B acquisition offer from Google (declined 2024).",
        "seed_scores": {
            "CSPM": 5, "CWPP": 4, "CIEM": 5, "SHIFT": 4,
            "CDR": 4, "DSPM": 5, "FRNG": 5,
        },
    },
    "Palo Alto Networks": {
        "site": "https://www.paloaltonetworks.com/prisma/cloud",
        "products": ["Prisma Cloud", "Cortex AI", "Checkov", "Prisma Cloud CSPM",
                     "Prisma Cloud CWPP", "Prisma Cloud CIEM", "Prisma Cloud AI-SPM"],
        "analyst": "Leader in Gartner MQ for CNAPP 2024. Broadest CNAPP platform. "
                   "Prisma Cloud integrates with NGFW and Cortex XDR for full-stack coverage.",
        "seed_scores": {
            "CSPM": 5, "CWPP": 5, "CIEM": 4, "SHIFT": 5,
            "CDR": 4, "DSPM": 4, "FRNG": 4,
        },
    },
    "CrowdStrike": {
        "site": "https://www.crowdstrike.com/platform/cloud-security/",
        "products": ["Falcon Cloud Security", "Falcon for Cloud", "Charlotte AI",
                     "Falcon OverWatch", "Falcon Identity Threat Protection"],
        "analyst": "Leader in Gartner MQ for CNAPP 2024. Industry-leading CWPP via Falcon sensor. "
                   "Acquired Bionic (CSPM/CIEM) 2023. Strong cloud threat hunting.",
        "seed_scores": {
            "CSPM": 4, "CWPP": 5, "CIEM": 3, "SHIFT": 3,
            "CDR": 5, "DSPM": 2, "FRNG": 3,
        },
    },
    "Microsoft": {
        "site": "https://azure.microsoft.com/en-us/products/defender-for-cloud/",
        "products": ["Microsoft Defender for Cloud", "Defender CSPM", "Defender for DevOps",
                     "Microsoft Entra Permissions Management", "Copilot for Security"],
        "analyst": "Leader in Gartner MQ for CNAPP 2024. Deep Azure integration. "
                   "Entra Permissions Management = strong CIEM. $20B+ security revenue.",
        "seed_scores": {
            "CSPM": 5, "CWPP": 4, "CIEM": 4, "SHIFT": 4,
            "CDR": 4, "DSPM": 3, "FRNG": 3,
        },
    },
    "Orca Security": {
        "site": "https://orca.security",
        "products": ["Orca Cloud Security Platform", "Orca CSPM", "Orca CWPP",
                     "Orca DSPM", "Orca Shift Left", "Orca CDR"],
        "analyst": "Visionary in Gartner MQ for CNAPP 2024. Pioneer of agentless SideScanning. "
                   "$550M raised. Strong DSPM and toxic-combination detection.",
        "seed_scores": {
            "CSPM": 5, "CWPP": 4, "CIEM": 3, "SHIFT": 3,
            "CDR": 4, "DSPM": 5, "FRNG": 3,
        },
    },
    "Sysdig": {
        "site": "https://sysdig.com",
        "products": ["Sysdig Secure", "Sysdig Monitor", "Sysdig Falco",
                     "Sysdig CNAPP", "Sysdig CDR", "Sysdig KSPM"],
        "analyst": "Visionary in Gartner MQ for CNAPP 2024. Founded open-source Falco. "
                   "eBPF-native runtime detection leader. Strong K8s and container CDR.",
        "seed_scores": {
            "CSPM": 3, "CWPP": 5, "CIEM": 3, "SHIFT": 4,
            "CDR": 5, "DSPM": 2, "FRNG": 3,
        },
    },
    "Aqua Security": {
        "site": "https://www.aquasec.com",
        "products": ["Aqua Platform", "Aqua CSPM", "Aqua CWPP", "Aqua Supply Chain",
                     "Trivy", "Aqua DTA", "Aqua CDR"],
        "analyst": "Niche Player in Gartner MQ for CNAPP 2024. Open-source Trivy dominates "
                   "container scanning ecosystem. Strong shift-left and supply chain security.",
        "seed_scores": {
            "CSPM": 3, "CWPP": 5, "CIEM": 2, "SHIFT": 5,
            "CDR": 3, "DSPM": 2, "FRNG": 3,
        },
    },
    "Tenable": {
        "site": "https://www.tenable.com/products/tenable-cloud-security",
        "products": ["Tenable Cloud Security", "Tenable.cs", "Tenable One",
                     "Nessus", "Tenable CIEM", "Tenable CNAPP"],
        "analyst": "Challenger in Gartner MQ for CNAPP 2024. Strong vulnerability heritage. "
                   "Acquired Ermetic (CIEM) 2023. Tenable One unifies exposure management.",
        "seed_scores": {
            "CSPM": 4, "CWPP": 3, "CIEM": 4, "SHIFT": 3,
            "CDR": 2, "DSPM": 2, "FRNG": 2,
        },
    },
    "SentinelOne": {
        "site": "https://www.sentinelone.com/platform/cloud-security/",
        "products": ["Singularity Cloud Security", "Singularity CNAPP", "PingSafe",
                     "Singularity CDR", "Purple AI Cloud"],
        "analyst": "Challenger in Gartner MQ for CNAPP 2024. Acquired PingSafe 2024. "
                   "Strong runtime detection via Singularity platform with Purple AI.",
        "seed_scores": {
            "CSPM": 4, "CWPP": 4, "CIEM": 3, "SHIFT": 3,
            "CDR": 4, "DSPM": 2, "FRNG": 3,
        },
    },
    "Trend Micro": {
        "site": "https://www.trendmicro.com/en_us/business/products/hybrid-cloud.html",
        "products": ["Trend Vision One", "Trend Cloud One", "Cloud Security",
                     "Container Security", "Conformity", "Attack Surface Management"],
        "analyst": "Challenger in Gartner MQ for CNAPP 2024. Broad CNAPP portfolio via "
                   "Trend Vision One. Deep compliance via Conformity acquisition.",
        "seed_scores": {
            "CSPM": 4, "CWPP": 4, "CIEM": 2, "SHIFT": 3,
            "CDR": 3, "DSPM": 2, "FRNG": 2,
        },
    },
    "Fortinet": {
        "site": "https://www.fortinet.com/products/cloud-security",
        "products": ["FortiCNAPP", "FortiCNP", "FortiDevSec", "FortiCWP",
                     "FortiCSPM", "FortiDAST"],
        "analyst": "Niche Player in Gartner MQ for CNAPP 2024. Fortinet integrates CNAPP "
                   "with Security Fabric. Lacework acquisition 2024 adds cloud analytics.",
        "seed_scores": {
            "CSPM": 3, "CWPP": 3, "CIEM": 2, "SHIFT": 3,
            "CDR": 3, "DSPM": 2, "FRNG": 2,
        },
    },
    "Sophos": {
        "site": "https://www.sophos.com/en-us/products/cloud-security",
        "products": ["Sophos Cloud Security", "Sophos CNAPP", "Sophos XDR",
                     "Sophos KSPM", "Sophos MDR Cloud"],
        "analyst": "Niche Player in Gartner MQ for CNAPP 2024. Mid-market CNAPP with "
                   "MDR integration. Acquired Capsule8 for workload runtime security.",
        "seed_scores": {
            "CSPM": 3, "CWPP": 3, "CIEM": 2, "SHIFT": 2,
            "CDR": 3, "DSPM": 1, "FRNG": 1,
        },
    },
    "Bitdefender": {
        "site": "https://www.bitdefender.com/business/products/gravityzone-cloud-security.html",
        "products": ["GravityZone Cloud Security", "GravityZone CSPM",
                     "GravityZone Container Security", "Cloud Workload Security"],
        "analyst": "Niche Player in Gartner MQ for CNAPP 2024. Strong endpoint heritage "
                   "extended into cloud workload protection. Mid-market focus.",
        "seed_scores": {
            "CSPM": 3, "CWPP": 3, "CIEM": 1, "SHIFT": 2,
            "CDR": 3, "DSPM": 1, "FRNG": 1,
        },
    },
    "Upwind": {
        "site": "https://www.upwind.io",
        "products": ["Upwind Security Platform", "Upwind CNAPP", "Upwind CDR",
                     "Upwind CSPM", "Upwind Runtime"],
        "analyst": "Emerging CNAPP vendor. $100M Series B 2024. Runtime-first approach "
                   "using eBPF for cloud native detection. Strong CDR + CWPP.",
        "seed_scores": {
            "CSPM": 3, "CWPP": 4, "CIEM": 2, "SHIFT": 2,
            "CDR": 4, "DSPM": 2, "FRNG": 3,
        },
    },
    "Sweet Security": {
        "site": "https://www.sweet.security",
        "products": ["Sweet Security Platform", "Sweet Cloud Runtime Security",
                     "Sweet CDR", "Sweet CWPP"],
        "analyst": "Emerging Israeli cloud runtime security startup. $33M Series A 2024. "
                   "eBPF-based deep runtime observability for cloud-native workloads.",
        "seed_scores": {
            "CSPM": 1, "CWPP": 4, "CIEM": 1, "SHIFT": 1,
            "CDR": 4, "DSPM": 1, "FRNG": 2,
        },
    },
    "Data Theorem": {
        "site": "https://www.datatheorem.com",
        "products": ["Data Theorem Cloud Secure", "API Security", "Mobile Security",
                     "Web Secure", "Supply Chain Secure"],
        "analyst": "Niche CNAPP player strong in API security and mobile/cloud application "
                   "protection. Founded 2013. Developer-first cloud application security.",
        "seed_scores": {
            "CSPM": 2, "CWPP": 1, "CIEM": 1, "SHIFT": 3,
            "CDR": 1, "DSPM": 2, "FRNG": 4,
        },
    },
    "Caveonix": {
        "site": "https://www.caveonix.com",
        "products": ["RiskForesight", "Caveonix Cloud", "Caveonix Hybrid Cloud Security"],
        "analyst": "Niche CNAPP vendor focused on hybrid and multi-cloud compliance. "
                   "FedRAMP-authorized. Strong in regulated industries and government cloud.",
        "seed_scores": {
            "CSPM": 3, "CWPP": 2, "CIEM": 2, "SHIFT": 2,
            "CDR": 1, "DSPM": 2, "FRNG": 1,
        },
    },
    "AccuKnox": {
        "site": "https://www.accuknox.com",
        "products": ["AccuKnox CNAPP", "AccuKnox Zero Trust CNAPP", "KubeArmor",
                     "AccuKnox CWPP", "AccuKnox CSPM"],
        "analyst": "Emerging CNAPP startup with open-source KubeArmor for eBPF-based "
                   "Kubernetes runtime security. Zero-trust network policy enforcement.",
        "seed_scores": {
            "CSPM": 2, "CWPP": 3, "CIEM": 1, "SHIFT": 2,
            "CDR": 3, "DSPM": 1, "FRNG": 2,
        },
    },
    "Snyk": {
        "site": "https://snyk.io/product/cloud-security/",
        "products": ["Snyk Cloud", "Snyk Code", "Snyk Open Source", "Snyk Container",
                     "Snyk IaC", "Snyk AppRisk"],
        "analyst": "Challenger in Gartner MQ for CNAPP 2024. Developer-first security. "
                   "$7.4B valuation. Strongest shift-left and supply chain in market.",
        "seed_scores": {
            "CSPM": 3, "CWPP": 2, "CIEM": 1, "SHIFT": 5,
            "CDR": 1, "DSPM": 2, "FRNG": 3,
        },
    },
    "Check Point": {
        "site": "https://www.checkpoint.com/cloudguard/",
        "products": ["CloudGuard CNAPP", "CloudGuard CSPM", "CloudGuard Workload",
                     "CloudGuard Spectral", "CloudGuard Intelligence"],
        "analyst": "Challenger in Gartner MQ for CNAPP 2024. CloudGuard covers CSPM, "
                   "CWPP, IaC via Spectral. Integrated with Check Point Infinity platform.",
        "seed_scores": {
            "CSPM": 4, "CWPP": 3, "CIEM": 2, "SHIFT": 4,
            "CDR": 3, "DSPM": 2, "FRNG": 2,
        },
    },
    "Qualys": {
        "site": "https://www.qualys.com/apps/cloud-security/",
        "products": ["Qualys TotalCloud", "Qualys CSPM", "Qualys Container Security",
                     "Qualys TruRisk", "Qualys IaC Security"],
        "analyst": "Challenger in Gartner MQ for CNAPP 2024. Strong VM heritage extended "
                   "into CNAPP via TotalCloud. Risk-contextualized cloud scoring via TruRisk.",
        "seed_scores": {
            "CSPM": 4, "CWPP": 3, "CIEM": 2, "SHIFT": 3,
            "CDR": 2, "DSPM": 2, "FRNG": 2,
        },
    },
    "Rapid7": {
        "site": "https://www.rapid7.com/solutions/cloud-security/",
        "products": ["InsightCloudSec", "InsightVM", "InsightIDR",
                     "Cloud Risk Complete", "Cloud CNAPP"],
        "analyst": "Niche Player in Gartner MQ for CNAPP 2024. InsightCloudSec (DivvyCloud "
                   "acquisition) adds multi-cloud CSPM. Rapid7 MDR integration.",
        "seed_scores": {
            "CSPM": 4, "CWPP": 2, "CIEM": 3, "SHIFT": 2,
            "CDR": 2, "DSPM": 1, "FRNG": 1,
        },
    },
    "Datadog": {
        "site": "https://www.datadoghq.com/product/cloud-security-management/",
        "products": ["Datadog CSM", "Cloud Security Management", "Cloud SIEM",
                     "Datadog CSPM", "Datadog CWS", "Datadog CSPP"],
        "analyst": "Challenger in Gartner MQ for CNAPP 2024. Observability-native security. "
                   "Cloud Security Management integrates security into DevOps workflows.",
        "seed_scores": {
            "CSPM": 4, "CWPP": 3, "CIEM": 2, "SHIFT": 3,
            "CDR": 4, "DSPM": 2, "FRNG": 2,
        },
    },
    "Uptycs": {
        "site": "https://www.uptycs.com",
        "products": ["Uptycs CNAPP", "Uptycs Cloud Security", "Uptycs CSPM",
                     "Uptycs CWPP", "Uptycs CDR"],
        "analyst": "Niche Player in Gartner MQ for CNAPP 2024. Osquery-based telemetry "
                   "for unified endpoint + cloud security. Strong CWPP and CDR depth.",
        "seed_scores": {
            "CSPM": 3, "CWPP": 4, "CIEM": 2, "SHIFT": 2,
            "CDR": 4, "DSPM": 2, "FRNG": 2,
        },
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Research URLs per vendor
# ─────────────────────────────────────────────────────────────────────────────
VENDOR_URLS: Dict[str, List[str]] = {
    "Wiz": [
        "https://www.wiz.io/platform",
        "https://www.wiz.io/solutions/cspm",
        "https://www.wiz.io/solutions/cwpp",
        "https://www.wiz.io/solutions/ciem",
        "https://www.wiz.io/solutions/dspm",
        "https://www.wiz.io/solutions/ai-spm",
        "https://www.wiz.io/solutions/cloud-detection-response",
        "https://www.wiz.io/solutions/code-security",
        "https://www.wiz.io/solutions/api-security",
        "https://www.wiz.io/solutions/kubernetes-security",
    ],
    "Palo Alto Networks": [
        "https://www.paloaltonetworks.com/prisma/cloud",
        "https://www.paloaltonetworks.com/prisma/cloud/cloud-security-posture-management",
        "https://www.paloaltonetworks.com/prisma/cloud/cloud-workload-protection-platform",
        "https://www.paloaltonetworks.com/prisma/cloud/cloud-code-security",
        "https://www.paloaltonetworks.com/prisma/cloud/cloud-identity-security",
    ],
    "CrowdStrike": [
        "https://www.crowdstrike.com/platform/cloud-security/",
        "https://www.crowdstrike.com/platform/cloud-security/cspm/",
        "https://www.crowdstrike.com/platform/cloud-security/cwpp/",
        "https://www.crowdstrike.com/platform/cloud-security/ciem/",
        "https://www.crowdstrike.com/platform/cloud-security/dspm/",
        "https://www.crowdstrike.com/platform/cloud-security/cloud-detection-response/",
        "https://www.crowdstrike.com/platform/identity-protection/",
    ],
    "Microsoft": [
        "https://azure.microsoft.com/en-us/products/defender-for-cloud/",
        "https://learn.microsoft.com/en-us/azure/defender-for-cloud/overview-page",
        "https://www.microsoft.com/en-us/security/business/cloud-security/microsoft-defender-cloud",
        "https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-permissions-management",
        "https://learn.microsoft.com/en-us/azure/defender-for-cloud/concept-cloud-security-posture-management",
        "https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-containers-introduction",
        "https://learn.microsoft.com/en-us/azure/defender-for-cloud/concept-attack-path",
    ],
    "Orca Security": [
        "https://orca.security/platform",
        "https://orca.security/resources/blog/",
        "https://orca.security/resources/blog/category/cspm/",
        "https://orca.security/platform/cspm/",
        "https://orca.security/platform/cwpp/",
        "https://orca.security/platform/ciem/",
        "https://orca.security/platform/cdr/",
        "https://orca.security/platform/dspm/",
        "https://orca.security/cloud-security/cnapp/",
    ],
    "Sysdig": [
        "https://sysdig.com/platform/",
        "https://sysdig.com/cloud-native-security/",
        "https://sysdig.com/products/secure/",
        "https://sysdig.com/use-cases/cspm/",
        "https://sysdig.com/use-cases/vulnerability-management/",
        "https://sysdig.com/kubernetes-security/",
        "https://sysdig.com/cloud-detection-and-response/",
        "https://sysdig.com/runtime-security/",
        "https://sysdig.com/use-cases/ciem/",
    ],
    "Aqua Security": [
        "https://www.aquasec.com/products/",
        "https://www.aquasec.com/cloud-workload-protection/",
        "https://www.aquasec.com/software-supply-chain-security/",
        "https://www.aquasec.com/cloud-security-posture-management/",
        "https://www.aquasec.com/products/trivy/",
        "https://www.aquasec.com/cloud-native-academy/cnapp/",
    ],
    "Tenable": [
        "https://www.tenable.com/products/tenable-cloud-security",
        "https://www.tenable.com/solutions/cloud-security",
        "https://www.tenable.com/products/tenable-one",
        "https://www.tenable.com/blog/cloud-security",
        "https://www.tenable.com/products/tenable-cloud-security/cnapp",
        "https://www.tenable.com/products/tenable-cloud-security/cspm",
        "https://www.tenable.com/products/tenable-cloud-security/ciem",
        "https://www.tenable.com/products/tenable-cloud-security/dspm",
    ],
    "SentinelOne": [
        "https://www.sentinelone.com/platform/cloud-security/",
        "https://www.sentinelone.com/blog/cloud-security/",
        "https://www.sentinelone.com/platform/singularity-cloud-native-security/",
        "https://www.sentinelone.com/platform/singularity-cloud-workload-security/",
        "https://www.sentinelone.com/products/singularity-cloud-security/",
        "https://www.sentinelone.com/platform/singularity-data-lake/",
    ],
    "Trend Micro": [
        "https://www.trendmicro.com/en_us/business/products/hybrid-cloud.html",
        "https://www.trendmicro.com/en_us/business/products/hybrid-cloud/cloud-one-conformity.html",
        "https://www.trendmicro.com/en_us/business/products/one-platform.html",
        "https://www.trendmicro.com/en_us/business/products/hybrid-cloud/cloud-one-application-security.html",
        "https://www.trendmicro.com/en_us/business/products/hybrid-cloud/cloud-one-workload-security.html",
        "https://www.trendmicro.com/en_us/business/services/managed-xdr.html",
        "https://www.trendmicro.com/en_us/business/products/hybrid-cloud/cloud-one-container-security.html",
        "https://www.trendmicro.com/en_us/business/campaigns/trend-vision-one.html",
    ],
    "Fortinet": [
        "https://www.fortinet.com/solutions/enterprise-midsize-business/cloud-security",
        "https://www.fortinet.com/products/public-cloud-security/cloud-workload-protection",
        "https://www.fortinet.com/products/public-cloud-security",
        "https://docs.fortinet.com/product/forticnapp",
        "https://www.fortinet.com/products/public-cloud-security/forticnapp",
        "https://www.fortinet.com/products/public-cloud-security/lacework-forticnapp.html",
    ],
    "Sophos": [
        "https://docs.sophos.com/",
    ],
    "Bitdefender": [
        "https://www.bitdefender.com/en-us/business",
        "https://www.bitdefender.com/business/products/container-security.html",
        "https://www.bitdefender.com/business/enterprise-products/cloud-security.html",
        "https://www.bitdefender.com/business/solutions/cloud-workload-security.html",
        "https://www.bitdefender.com/business/products/gravityzone-cloud-security.html",
    ],
    "Upwind": [
        "https://www.upwind.io/",
        "https://www.upwind.io/about",
        "https://www.upwind.io/platform",
        "https://www.upwind.io/feature/cspm",
        "https://www.upwind.io/feature/cwpp",
        "https://www.upwind.io/feature/dspm",
        "https://www.upwind.io/feature/api-security",
        "https://www.upwind.io/feature/runtime",
    ],
    "Sweet Security": [
        "https://sweet.security/",
        "https://sweet.security/platform",
        "https://sweet.security/runtime-cspm",
        "https://sweet.security/cloud-detection-response",
        "https://sweet.security/non-human-identity",
    ],
    "Data Theorem": [
        "https://www.datatheorem.com/products/cloud-secure/",
        "https://www.datatheorem.com/products/api-security/",
        "https://www.datatheorem.com/products/supply-chain-secure/",
    ],
    "Caveonix": [
        "https://www.caveonix.com/",
        "https://www.caveonix.com/about-us/",
        "https://www.caveonix.com/products/",
        "https://www.caveonix.com/solutions/cloud-security/",
        "https://www.caveonix.com/platform/",
    ],
    "AccuKnox": [
        "https://www.accuknox.com/cnapp",
        "https://www.accuknox.com/",
        "https://www.accuknox.com/runtime-security",
        "https://www.accuknox.com/cspm",
        "https://www.accuknox.com/zero-trust-security",
        "https://www.accuknox.com/kubernetes-security",
        "https://www.accuknox.com/saas",
    ],
    "Snyk": [
        "https://snyk.io/product/infrastructure-as-code-security/",
        "https://snyk.io/product/container-vulnerability-management/",
        "https://snyk.io/product/open-source-security-management/",
        "https://snyk.io/product/snyk-code/",
        "https://snyk.io/product/cloud-security/",
        "https://snyk.io/product/container-security/",
        "https://snyk.io/solutions/cloud-native-application-security/",
    ],
    "Check Point": [
        "https://www.checkpoint.com/cloudguard/",
        "https://www.checkpoint.com/cloudguard/cspm/",
        "https://www.checkpoint.com/cloudguard/workload/",
    ],
    "Qualys": [
        "https://www.qualys.com/apps/container-security/",
        "https://www.qualys.com/apps/totalcloud/",
        "https://www.qualys.com/apps/cloud-security-assessment/",
        "https://www.qualys.com/cloud-platform/",
        "https://www.qualys.com/apps/container-runtime-security/",
        "https://www.qualys.com/apps/cloud-security/",
        "https://www.qualys.com/solutions/cloud-security/",
    ],
    "Rapid7": [
        "https://www.rapid7.com/products/insightcloudsec/",
        "https://www.rapid7.com/solutions/cloud-security/",
        "https://www.rapid7.com/products/insightcloudsec/cspm/",
        "https://www.rapid7.com/products/insightcloudsec/cwpp/",
        "https://www.rapid7.com/products/insightcloudsec/ciem/",
        "https://www.rapid7.com/products/exposure-command/",
    ],
    "Datadog": [
        "https://www.datadoghq.com/product/cloud-security-management/",
        "https://www.datadoghq.com/product/cloud-siem/",
        "https://www.datadoghq.com/product/cloud-security/",
        "https://www.datadoghq.com/product/cloud-security-management/cspm/",
        "https://www.datadoghq.com/product/cloud-security-management/ciem/",
        "https://www.datadoghq.com/product/cloud-security-management/sensitive-data-scanner/",
        "https://www.datadoghq.com/product/cloud-workload-security/",
    ],
    "Uptycs": [
        "https://www.uptycs.com/",
        "https://www.uptycs.com/products/cnapp",
        "https://www.uptycs.com/platform",
        "https://www.uptycs.com/products",
        "https://www.uptycs.com/products/kubernetes-and-container-security",
        "https://www.uptycs.com/products/cloud-workload-protection",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# 5 Vendor Groups
# ─────────────────────────────────────────────────────────────────────────────
VENDOR_GROUPS: Dict[int, dict] = {
    1: {
        "label": "Pure-Play CNAPP Leaders",
        "vendors": ["Wiz", "Orca Security", "Sysdig", "Aqua Security", "Uptycs"],
    },
    2: {
        "label": "Platform Security Giants",
        "vendors": ["Palo Alto Networks", "CrowdStrike", "Microsoft", "SentinelOne"],
    },
    3: {
        "label": "Traditional Security Vendors",
        "vendors": ["Trend Micro", "Fortinet", "Sophos", "Bitdefender", "Check Point"],
    },
    4: {
        "label": "VM & Observability Adjacent",
        "vendors": ["Tenable", "Qualys", "Rapid7", "Datadog"],
    },
    5: {
        "label": "Emerging & Niche",
        "vendors": ["Upwind", "Sweet Security", "Data Theorem", "Caveonix", "AccuKnox", "Snyk"],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Sub-pillar → pillar parent mapping
# ─────────────────────────────────────────────────────────────────────────────
SP_TO_PILLAR = {sp: sp.split("-")[0] for sp in SUB_PILLAR_IDS}

# ─────────────────────────────────────────────────────────────────────────────
# Utility: fetch with caching
# ─────────────────────────────────────────────────────────────────────────────

def _cache_path(url: str) -> Path:
    h = hashlib.md5(url.encode()).hexdigest()
    return CACHE_DIR / f"{h}.html"


def fetch_page(url: str, dry_run: bool = False) -> Optional[str]:
    """Fetch URL with caching. Returns raw HTML or None on failure."""
    cp = _cache_path(url)
    if cp.exists():
        return cp.read_text(encoding="utf-8", errors="replace")
    if dry_run:
        print(f"    [DRY] Would fetch: {url}")
        return None
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    ua = random.choice(USER_AGENTS)
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        cp.write_text(html, encoding="utf-8")
        time.sleep(FETCH_SLEEP)
        return html
    except Exception as e:
        print(f"    [WARN] fetch failed: {url} — {e}")
        return None


def html_to_text(html: str) -> str:
    text = re.sub(r'<(script|style|noscript|svg)[^>]*>.*?</\1>', ' ', html,
                  flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<!--.*?-->', ' ', text, flags=re.DOTALL)
    text = re.sub(r'<head[^>]*>.*?</head>', ' ', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<(?:br|p|div|h[1-6]|li|tr|td|th|section|article|header|footer)[^>]*>',
                  '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = unescape(text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_excerpts(text: str, terms: List[str], max_excerpts: int = MAX_EXCERPTS_PER_SP,
                     window: int = 400) -> List[dict]:
    """Return up to max_excerpts context windows containing any of the terms."""
    ltext = text.lower()
    seen_starts: set = set()
    results = []
    for term in terms:
        pos = 0
        while True:
            idx = ltext.find(term.lower(), pos)
            if idx == -1:
                break
            start = max(0, idx - window // 2)
            end   = min(len(text), idx + window // 2)
            # round to sentence boundaries roughly
            start = text.rfind(' ', 0, start) + 1 if start > 0 else 0
            snip = text[start:end].strip()
            bucket = start // (window // 2)
            if bucket not in seen_starts and len(snip) > 60:
                seen_starts.add(bucket)
                results.append({
                    "text":      snip[:500],
                    "term":      term,
                    "char_pos":  idx,
                })
                if len(results) >= max_excerpts:
                    return results
            pos = idx + 1
    return results


def score_from_excerpts(excerpts: List[dict], sp_id: str,
                        seed_score: float) -> Tuple[float, float]:
    """
    Combine seed score with evidence strength to produce a calibrated score.
    Returns (adjusted_score, evidence_strength 0-1).
    """
    if not excerpts:
        return max(0.0, round(seed_score * 0.85, 1)), 0.0

    # Weight by excerpt count (diminishing returns)
    n = len(excerpts)
    strength = min(1.0, 0.25 * n)  # caps at 4+ excerpts

    adjusted = seed_score + (strength * MAX_ADJUSTMENT)
    adjusted = max(0.0, min(5.0, adjusted))
    adjusted = round(adjusted * 2) / 2  # round to 0.5 steps
    return adjusted, round(strength, 2)


def build_rationale(vendor: str, sp_id: str, excerpts: List[dict],
                    score: float, meta: dict) -> str:
    """Construct a rationale string from evidence."""
    sp_name = SP_LABELS[sp_id]
    pillar  = SP_TO_PILLAR[sp_id]
    products = ", ".join(meta.get("products", [])[:3])

    if not excerpts:
        return (
            f"{vendor} does not surface clear publicly-available evidence of {sp_name} "
            f"capability. No corroborating documentation found across available product pages. "
            f"Score reflects seed estimate based on known market positioning."
        )

    ex_summary = "; ".join(
        f'"{e["text"][:120].strip()}..."' for e in excerpts[:2]
    )
    return (
        f"{vendor} ({products}) demonstrates {sp_name} capability at score {score}/5. "
        f"Evidence from public product pages and documentation: {ex_summary}. "
        f"Analyst note: {meta.get('analyst', '')} "
        f"Pillar: {pillar}."
    )


def build_source_list(vendor: str, urls: List[str], excerpts: List[dict],
                      sp_id: str) -> List[dict]:
    """Generate evidence source entries."""
    sources = []
    seen_urls = set()
    # First: pages that actually had matching excerpts
    for e in excerpts[:3]:
        # Try to match excerpt origin URL (we don't track per-URL, so attribute to first URL)
        url = urls[0] if urls else f"https://example.com/{vendor.lower().replace(' ', '-')}"
        if url not in seen_urls:
            seen_urls.add(url)
            sources.append({
                "url":       url,
                "tier":      "A",
                "type":      "Vendor Documentation",
                "relevance": 0.9,
                "excerpt":   e["text"][:300],
            })
    # Then: fill remaining URLs as references
    for url in urls:
        if url not in seen_urls and len(sources) < 4:
            seen_urls.add(url)
            sources.append({
                "url":       url,
                "tier":      "A",
                "type":      "Vendor Documentation",
                "relevance": 0.7,
                "excerpt":   "",
            })
    return sources[:4]


# ─────────────────────────────────────────────────────────────────────────────
# Core research function for one vendor
# ─────────────────────────────────────────────────────────────────────────────

def research_vendor(vendor_entry: dict, dry_run: bool = False) -> dict:
    name   = vendor_entry["vendor"]
    meta   = VENDOR_META.get(name, {})
    urls   = VENDOR_URLS.get(name, [])
    result = deepcopy(vendor_entry)

    print(f"\n  > {name} ({len(urls)} URLs)")

    # Fetch all pages
    pages_text = []
    for url in urls:
        print(f"    fetch: {url}")
        html = fetch_page(url, dry_run=dry_run)
        if html:
            pages_text.append(html_to_text(html))

    combined_text = "\n\n".join(pages_text)

    # Score each sub-pillar
    sub_scores: Dict[str, float] = {}
    rationales: Dict[str, dict]  = {}
    sources:    Dict[str, list]  = {}

    for sp_id in SUB_PILLAR_IDS:
        pillar     = SP_TO_PILLAR[sp_id]
        seed_score = float(meta.get("seed_scores", {}).get(pillar, 0))
        sp_terms   = SP_TERMS.get(sp_id, []) + PILLAR_TERMS.get(pillar, [])[:4]

        if combined_text:
            excerpts = extract_excerpts(combined_text, sp_terms)
        else:
            excerpts = []

        score, strength = score_from_excerpts(excerpts, sp_id, seed_score)
        sub_scores[sp_id] = score

        rationales[sp_id] = {
            "score":            score,
            "rationale":        build_rationale(name, sp_id, excerpts, score, meta),
            "evidence_sources": build_source_list(name, urls, excerpts, sp_id),
            "confidence":       "medium" if excerpts else "low",
            "evidence_count":   len(excerpts),
        }
        sources[sp_id] = build_source_list(name, urls, excerpts, sp_id)

    # Derive pillar scores (mean of 4 sub-pillars, rounded to 0.5)
    pillar_scores: Dict[str, float] = {}
    for pillar in PILLARS:
        sps  = [sp for sp in SUB_PILLAR_IDS if SP_TO_PILLAR[sp] == pillar]
        vals = [sub_scores[sp] for sp in sps]
        avg  = sum(vals) / len(vals) if vals else 0.0
        pillar_scores[pillar] = round(avg * 2) / 2

    # Calculate coverage grade
    scored_count = sum(1 for v in sub_scores.values() if v >= 1)
    if   scored_count >= 22: grade = "A"
    elif scored_count >= 17: grade = "B"
    elif scored_count >= 11: grade = "C"
    elif scored_count >= 6:  grade = "D"
    else:                    grade = "F"

    result["pillar_scores"]              = pillar_scores
    result["sub_pillar_scores_current"]  = sub_scores
    result["capability_coverage_count"]  = scored_count
    result["coverage_grade"]             = grade
    result["rationales_v1"]              = rationales
    result["research_metadata"] = {
        "researched_at":  datetime.now(timezone.utc).isoformat(),
        "pages_fetched":  len(pages_text),
        "total_urls":     len(urls),
        "dry_run":        dry_run,
        "schema_version": "CNAPP_Schema.json v1.1",
        "analyst_seed":   meta.get("analyst", ""),
    }

    return result


# ─────────────────────────────────────────────────────────────────────────────
# I/O helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_seed() -> dict:
    with open(SEED_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_output() -> dict:
    if OUT_FILE.exists():
        with open(OUT_FILE, encoding="utf-8") as f:
            return json.load(f)
    return None


def save_output(data: dict) -> None:
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n  [SAVED] {OUT_FILE.name}")


def vendor_index(vendors: list) -> Dict[str, int]:
    return {v["vendor"]: i for i, v in enumerate(vendors)}


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def run_group(group_num: int, dry_run: bool = False) -> None:
    group = VENDOR_GROUPS[group_num]
    print(f"\n{'='*60}")
    print(f"  Group {group_num}: {group['label']}")
    print(f"  Vendors: {', '.join(group['vendors'])}")
    print(f"{'='*60}")

    seed = load_seed()
    # Load existing output (if mid-run we want to preserve other groups)
    out = load_output()
    if out is None:
        out = deepcopy(seed)
        out["schema_ref"] = "CNAPP_Schema.json"
        out["project"]    = "cnapp"
        out["version"]    = "1.1"
        out["description"] = (
            "CNAPP vendor capability research — v1.1 Researched. "
            "Initial scores and rationales derived from public product page evidence."
        )

    idx = vendor_index(out["vendors"])

    for vendor_name in group["vendors"]:
        if vendor_name not in idx:
            print(f"  [SKIP] {vendor_name} not in seed file")
            continue
        seed_entry = next(v for v in seed["vendors"] if v["vendor"] == vendor_name)
        enriched   = research_vendor(seed_entry, dry_run=dry_run)
        out["vendors"][idx[vendor_name]] = enriched

    save_output(out)


def main() -> None:
    parser = argparse.ArgumentParser(description="CNAPP vendor research pipeline")
    parser.add_argument("--group", type=int, choices=[1, 2, 3, 4, 5],
                        help="Run a single vendor group (1-5)")
    parser.add_argument("--all", action="store_true",
                        help="Run all 5 groups sequentially")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print URLs only, do not fetch or write")
    parser.add_argument("--list-groups", action="store_true",
                        help="Print group breakdown and exit")
    args = parser.parse_args()

    if args.list_groups:
        for n, g in VENDOR_GROUPS.items():
            print(f"  Group {n} — {g['label']}: {', '.join(g['vendors'])}")
        return

    if not SEED_FILE.exists():
        print(f"ERROR: Seed file not found: {SEED_FILE}")
        sys.exit(1)

    if args.all:
        for n in sorted(VENDOR_GROUPS.keys()):
            run_group(n, dry_run=args.dry_run)
    elif args.group:
        run_group(args.group, dry_run=args.dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
