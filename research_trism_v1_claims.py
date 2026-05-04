"""
research_trism_v1_claims.py — AI TRiSM Vendor Claims Research Pipeline

Evaluates vendors against the AI TriSM Schema 1_0.json using public web evidence.
Processes vendors in batches of 5 with a pause between batches, then merges
all batch results into the final output file.

Completely separate from DFIR research pipeline — different schema, different
pillar codes (GOV/RUN/INF vs PLA/INV/REM/PMG/LAW), different vendor list.

Usage:
  python research_trism_v1_claims.py                          # full run (62 vendors, batches of 5)
  python research_trism_v1_claims.py --batch-size 5           # explicit batch size
  python research_trism_v1_claims.py --batch-pause 30         # seconds between batches
  python research_trism_v1_claims.py --max-vendors 5          # test with 5 vendors
  python research_trism_v1_claims.py --resume                 # resume from last checkpoint
  python research_trism_v1_claims.py --merge-only             # just merge batch outputs
  python research_trism_v1_claims.py --force-fetch            # re-fetch cached pages
"""

import argparse
import csv
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
# Configuration — completely separate from DFIR pipeline
# ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent

DEFAULT_INPUT_FILE  = ROOT / "AI TRiSM Vendor 1-0 Seed.json"
DEFAULT_SCHEMA_FILE = ROOT / "AI TriSM Schema 1_0.json"
DEFAULT_OUTPUT_FILE = ROOT / "AI TRiSM Vendor 1-1 Validated.json"

# Separate cache and checkpoint dirs — never touch DFIR caches
CACHE_DIR           = ROOT / "research" / "cache" / "pages_trism"
CHECKPOINT_DIR      = ROOT / "research" / "trism_checkpoints"
BATCH_OUTPUT_DIR    = ROOT / "research" / "trism_batches"

URL_RE = re.compile(r"https?://[^\s)\]\}\">,]+")

PILLARS = ["GOV", "RUN", "INF"]
SUBPILLAR_IDS = [f"{p}-{i:02d}" for p in PILLARS for i in range(1, 5)]

# ─────────────────────────────────────────────────────────────────────
# AI TRiSM-specific search terms — distinct from DFIR AI terms
# These focus on governance, runtime controls, and information governance
# ─────────────────────────────────────────────────────────────────────

TRISM_PRIMARY_TERMS = [
    # Governance
    "ai governance", "ai risk", "ai trust", "ai catalog", "model inventory",
    "model card", "ai registry", "ai lineage", "data lineage", "ai audit",
    "ai compliance", "ai transparency", "ai accountability", "ai assurance",
    "ai posture", "model risk management", "ai ethics", "responsible ai",
    "ai policy", "ai regulation", "eu ai act", "nist ai rmf", "iso 42001",
    "ai bill of materials", "ai bom", "model governance",
    # Runtime
    "prompt injection", "jailbreak", "guardrails", "ai guardrails",
    "content filtering", "content safety", "runtime inspection",
    "ai firewall", "llm security", "model monitoring", "ai gateway",
    "ai proxy", "hallucination detection", "toxicity detection",
    "ai safety", "red teaming", "adversarial testing", "prompt defense",
    "runtime enforcement", "policy engine", "ai security",
    # Information Governance
    "data governance", "data classification", "data discovery",
    "data access control", "data loss prevention", "dlp",
    "dspm", "data security posture", "privacy enhancing",
    "data masking", "tokenization", "synthetic data",
    "differential privacy", "confidential computing",
    "access governance", "permission management", "oversharing",
    "data catalog", "data privacy", "consent management",
    # General AI
    "ai agent", "agentic ai", "llm", "large language model",
    "machine learning", "generative ai", "gen ai", "ai-powered",
    "ai-driven", "autonomous", "copilot", "ai copilot",
]

TRISM_EXCLUSION_TERMS = [
    "rule-based only", "no ai", "manual process only",
    "human-only review", "no automation",
]

# ─────────────────────────────────────────────────────────────────────
# Synonym / terminology variation expansion
# Maps canonical terms → list of alternative phrasings so that
# variations like "AI oversight" still count as a hit for "ai governance"
# ─────────────────────────────────────────────────────────────────────

TERM_SYNONYMS: Dict[str, List[str]] = {
    # ── Governance ──
    "ai governance":          ["artificial intelligence governance", "ai oversight",
                               "algorithmic governance", "ai management framework"],
    "ai risk":                ["artificial intelligence risk", "ai risk management",
                               "algorithmic risk", "ai threat"],
    "ai trust":               ["trustworthy ai", "trusted ai", "ai trustworthiness"],
    "ai catalog":             ["ai catalogue", "ai asset catalog", "ai model catalog"],
    "model inventory":        ["model catalog", "ml model inventory", "model repository",
                               "ai model registry"],
    "model card":             ["model documentation", "model factsheet", "model fact sheet",
                               "model datasheet"],
    "ai registry":            ["ai asset registry", "ai model registry", "ml registry"],
    "ai lineage":             ["model lineage", "ml lineage", "ai provenance",
                               "model provenance"],
    "data lineage":           ["data provenance", "data traceability", "data tracking",
                               "data flow tracking"],
    "ai audit":               ["ai auditing", "algorithmic audit", "algorithmic auditing",
                               "model audit", "model auditing"],
    "ai compliance":          ["ai regulatory compliance", "algorithmic compliance",
                               "ai regulation compliance"],
    "ai transparency":        ["algorithmic transparency", "model transparency",
                               "explainable ai", "xai", "model explainability",
                               "ai explainability"],
    "ai accountability":      ["algorithmic accountability", "ai responsibility"],
    "ai assurance":           ["ai quality assurance", "model assurance",
                               "ai validation"],
    "ai posture":             ["ai security posture", "ai risk posture"],
    "model risk management":  ["mrm", "model risk", "ml risk management"],
    "ai ethics":              ["ethical ai", "ai ethical framework",
                               "ethical artificial intelligence"],
    "responsible ai":         ["responsible artificial intelligence",
                               "ethical ai practices", "rai"],
    "ai policy":              ["ai use policy", "ai acceptable use",
                               "artificial intelligence policy"],
    "ai regulation":          ["ai regulatory", "ai law", "ai legislation"],
    "eu ai act":              ["european ai act", "eu artificial intelligence act"],
    "nist ai rmf":            ["nist ai risk management framework", "ai rmf",
                               "nist ai framework"],
    "iso 42001":              ["iso/iec 42001", "ai management system standard",
                               "iso 42001 ai"],
    "ai bill of materials":   ["ai bom", "aibom", "ai software bill of materials",
                               "ai sbom"],
    "model governance":       ["ml governance", "machine learning governance",
                               "model lifecycle governance"],

    # ── Runtime ──
    "prompt injection":       ["prompt attack", "prompt manipulation",
                               "adversarial prompting", "injection attack",
                               "prompt exploit"],
    "jailbreak":              ["jailbreaking", "jail break", "bypass guardrails",
                               "guardrail bypass"],
    "guardrails":             ["guard rails", "safety guardrails", "safety rails",
                               "ai guardrail"],
    "ai guardrails":          ["ai guard rails", "llm guardrails",
                               "llm guard rails"],
    "content filtering":      ["content moderation", "content screening",
                               "output filtering", "response filtering"],
    "content safety":         ["content moderation system", "safe content generation",
                               "content protection"],
    "runtime inspection":     ["runtime analysis", "runtime scanning",
                               "real-time inspection"],
    "ai firewall":            ["ai application firewall", "llm firewall",
                               "model firewall", "ai gateway firewall"],
    "llm security":           ["large language model security", "llm protection",
                               "llm safety", "foundation model security"],
    "model monitoring":       ["ml monitoring", "ai model monitoring",
                               "model observability", "ml observability",
                               "model performance monitoring"],
    "ai gateway":             ["ai api gateway", "llm gateway", "ai proxy gateway"],
    "ai proxy":               ["ai reverse proxy", "llm proxy"],
    "hallucination detection": ["hallucination prevention", "factuality checking",
                                "grounding detection", "hallucination mitigation",
                                "factual grounding"],
    "toxicity detection":     ["toxic content detection", "harmful content detection",
                               "toxicity filtering", "harmful output detection"],
    "ai safety":              ["ai safe deployment", "safe ai", "ai safety testing"],
    "red teaming":            ["red-teaming", "ai red team", "ai red-teaming",
                               "security red team"],
    "adversarial testing":    ["adversarial evaluation", "robustness testing",
                               "adversarial robustness", "attack simulation"],
    "prompt defense":         ["prompt protection", "prompt shielding",
                               "prompt security", "prompt hardening"],
    "runtime enforcement":    ["real-time enforcement", "runtime policy enforcement",
                               "inline enforcement"],
    "policy engine":          ["policy enforcement engine", "rule engine",
                               "policy evaluation engine", "opa"],
    "ai security":            ["artificial intelligence security",
                               "ai cybersecurity", "ai infosec"],

    # ── Information Governance ──
    "data governance":        ["information governance", "data management framework",
                               "enterprise data governance"],
    "data classification":    ["data categorization", "information classification",
                               "data tagging", "data labeling", "data labelling"],
    "data discovery":         ["data scanning", "data identification",
                               "sensitive data discovery", "data reconnaissance"],
    "data access control":    ["data access management", "access control policy",
                               "data authorization", "data access governance"],
    "data loss prevention":   ["data leak prevention", "data leakage prevention",
                               "data exfiltration prevention"],
    "dlp":                    ["data loss prevention", "data leak prevention"],
    "dspm":                   ["data security posture management"],
    "data security posture":  ["data security posture management", "dspm",
                               "data security assessment"],
    "privacy enhancing":      ["privacy preserving", "privacy enhancing technology",
                               "privacy enhancing technologies", "pet", "pets"],
    "data masking":           ["data anonymization", "data anonymisation",
                               "data de-identification", "data obfuscation",
                               "data pseudonymization"],
    "tokenization":           ["data tokenization", "token-based protection",
                               "data token replacement"],
    "synthetic data":         ["synthetic data generation", "artificial data",
                               "data synthesis", "synthetic dataset"],
    "differential privacy":   ["formal privacy", "epsilon-delta privacy",
                               "dp mechanism"],
    "confidential computing": ["trusted execution environment", "tee",
                               "secure enclave", "confidential ai"],
    "access governance":      ["identity governance", "access management",
                               "iga", "identity governance and administration"],
    "permission management":  ["entitlement management", "access rights management",
                               "privilege management"],
    "oversharing":            ["over-sharing", "data oversharing",
                               "excessive sharing", "data exposure"],
    "data catalog":           ["data catalogue", "metadata catalog",
                               "metadata catalogue", "data inventory"],
    "data privacy":           ["information privacy", "privacy protection",
                               "privacy compliance", "personal data protection"],
    "consent management":     ["consent tracking", "privacy consent",
                               "consent orchestration"],

    # ── General AI ──
    "ai agent":               ["ai agents", "intelligent agent", "autonomous agent",
                               "intelligent agents"],
    "agentic ai":             ["agentic artificial intelligence", "autonomous ai",
                               "agent-based ai"],
    "llm":                    ["large language model", "foundation model"],
    "large language model":   ["llm", "foundation model", "language model"],
    "machine learning":       ["ml", "deep learning", "neural network",
                               "neural networks"],
    "generative ai":          ["genai", "generative artificial intelligence",
                               "gen-ai"],
    "gen ai":                 ["genai", "generative ai", "gen-ai"],
    "ai-powered":             ["ai powered", "ai enabled", "ai-enabled",
                               "ai driven", "powered by ai"],
    "ai-driven":              ["ai driven", "ai-powered", "ai powered",
                               "driven by ai"],
    "copilot":                ["co-pilot", "ai assistant", "ai companion"],
    "ai copilot":             ["ai co-pilot", "ai assistant tool"],
}


def _term_in_text(term: str, text_lower: str) -> bool:
    """Check if a term OR any of its synonyms appear in lowered text."""
    if term in text_lower:
        return True
    synonyms = TERM_SYNONYMS.get(term)
    if synonyms:
        return any(syn in text_lower for syn in synonyms)
    return False


def _matched_terms_in_text(terms: List[str], text_lower: str) -> List[str]:
    """Return list of terms (from *terms*) that match text, including synonyms.
    Reports the canonical term name even when a synonym triggered the match."""
    return [t for t in terms if _term_in_text(t, text_lower)]


# ─────────────────────────────────────────────────────────────────────
# Vendor-specific URLs for AI TRiSM evaluation
# Curated per vendor, with 3rd-party sources appended dynamically
# ─────────────────────────────────────────────────────────────────────

VENDOR_URLS: Dict[str, List[str]] = {
    # ── Consultancies (Big 4 + Strategy) ──────────────────────────────
    "Accenture": [
        "https://www.accenture.com/us-en/services/applied-intelligence/ai-ethics-governance",
        "https://www.accenture.com/us-en/services/responsible-ai",
        "https://www.accenture.com/us-en/services/data-ai/data-governance",
        "https://www.accenture.com/us-en/services/security/cyber-resilience",
        "https://www.accenture.com/us-en/services/ai-artificial-intelligence-index",
    ],
    "Deloitte": [
        "https://www.deloitte.com/global/en/services/risk-advisory/services/ai-governance.html",
        "https://www2.deloitte.com/us/en/pages/deloitte-analytics/solutions/ethics-of-ai-framework.html",
        "https://www.deloitte.com/global/en/services/risk-advisory/perspectives/trustworthy-ai.html",
        "https://www2.deloitte.com/us/en/pages/about-deloitte/articles/responsible-ai.html",
        "https://www.deloitte.com/global/en/services/consulting/services/generative-ai.html",
    ],
    "PwC": [
        "https://www.pwc.com/gx/en/issues/data-and-analytics/artificial-intelligence/responsible-ai.html",
        "https://www.pwc.com/us/en/services/consulting/cloud-digital/data-analytics/artificial-intelligence.html",
        "https://www.pwc.com/gx/en/about/responsible-ai.html",
        "https://www.pwc.com/us/en/services/consulting/cybersecurity-risk-regulatory.html",
        "https://www.pwc.com/gx/en/issues/data-and-analytics/artificial-intelligence.html",
    ],
    "EY (Ernst & Young)": [
        "https://www.ey.com/en_us/ai/trusted-ai",
        "https://www.ey.com/en_gl/ai/responsible-ai",
        "https://www.ey.com/en_us/ai",
        "https://www.ey.com/en_us/cybersecurity",
        "https://www.ey.com/en_gl/ai/generative-ai",
    ],
    "KPMG": [
        "https://kpmg.com/us/en/articles/responsible-ai.html",
        "https://kpmg.com/us/en/capabilities-services/advisory-services/risk-and-compliance/trusted-ai.html",
        "https://kpmg.com/xx/en/home/insights/2023/responsible-ai.html",
        "https://kpmg.com/us/en/capabilities-services/advisory-services/cyber-security.html",
        "https://kpmg.com/us/en/articles/generative-artificial-intelligence.html",
    ],
    "BCG (Boston Consulting Group)": [
        "https://www.bcg.com/capabilities/artificial-intelligence",
        "https://www.bcg.com/capabilities/artificial-intelligence/responsible-ai",
        "https://www.bcg.com/capabilities/digital-technology-data/data-governance",
        "https://www.bcg.com/capabilities/digital-technology-data/cybersecurity",
        "https://www.bcg.com/publications/2023/what-responsible-ai-really-requires",
    ],
    "McKinsey & Company": [
        "https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai",
        "https://www.mckinsey.com/capabilities/quantumblack/our-insights/responsible-ai",
        "https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/ai-risk",
        "https://www.mckinsey.com/capabilities/quantumblack/our-insights/generative-ai",
        "https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights/data-governance",
    ],
    "Booz Allen Hamilton": [
        "https://www.boozallen.com/expertise/analytics/ai.html",
        "https://www.boozallen.com/expertise/analytics/responsible-ai.html",
        "https://www.boozallen.com/expertise/cybersecurity.html",
        "https://www.boozallen.com/expertise/analytics/data-governance.html",
        "https://www.boozallen.com/capabilities/digital-solutions/generative-ai.html",
    ],
    # ── Hyperscalers & Major Cloud ────────────────────────────────────
    "Microsoft": [
        "https://www.microsoft.com/en-us/ai/responsible-ai",
        "https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/content-filter",
        "https://www.microsoft.com/en-us/security/business/ai-machine-learning/microsoft-purview-ai-hub",
        "https://learn.microsoft.com/en-us/azure/ai-studio/concepts/rbac-ai-studio",
        "https://azure.microsoft.com/en-us/products/ai-services/",
        "https://www.microsoft.com/en-us/security/business/ai-machine-learning/microsoft-security-copilot",
    ],
    "Google Cloud": [
        "https://cloud.google.com/vertex-ai/docs/explainable-ai/overview",
        "https://cloud.google.com/model-armor/docs/overview",
        "https://ai.google/responsibility/responsible-ai-practices/",
        "https://cloud.google.com/security/ai",
        "https://cloud.google.com/discover/what-is-data-governance",
        "https://cloud.google.com/dataplex/docs/data-governance",
    ],
    "AWS (Amazon Web Services)": [
        "https://aws.amazon.com/sagemaker/clarify/",
        "https://aws.amazon.com/machine-learning/responsible-machine-learning/",
        "https://aws.amazon.com/bedrock/guardrails/",
        "https://aws.amazon.com/ai/generative-ai/",
        "https://aws.amazon.com/security/",
        "https://aws.amazon.com/big-data/datalakes-and-analytics/governance/",
    ],
    "Oracle": [
        "https://www.oracle.com/artificial-intelligence/",
        "https://www.oracle.com/artificial-intelligence/ai-infrastructure/",
        "https://www.oracle.com/security/",
        "https://www.oracle.com/security/cloud-security/data-safe/",
        "https://www.oracle.com/artificial-intelligence/generative-ai/",
        "https://docs.oracle.com/en/cloud/paas/data-safe/",
    ],
    # ── Platform / Enterprise Software ────────────────────────────────
    "Salesforce": [
        "https://www.salesforce.com/artificial-intelligence/trusted-ai/",
        "https://einstein.ai/trust",
        "https://www.salesforce.com/products/einstein-ai/",
        "https://help.salesforce.com/s/articleView?id=sf.generative_ai_trust_layer.htm",
        "https://www.salesforce.com/news/stories/salesforce-ai-trust-layer/",
    ],
    "SAP": [
        "https://www.sap.com/products/artificial-intelligence/ai-ethics.html",
        "https://www.sap.com/products/artificial-intelligence.html",
        "https://www.sap.com/about/trust-center/responsible-ai.html",
        "https://www.sap.com/products/data-management/data-governance.html",
        "https://www.sap.com/products/technology-platform/data-security.html",
    ],
    "ServiceNow": [
        "https://www.servicenow.com/products/ai-governance.html",
        "https://www.servicenow.com/products/now-assist.html",
        "https://www.servicenow.com/products/security-operations.html",
        "https://docs.servicenow.com/bundle/ai-governance/page/product/ai-governance/concept/ai-governance.html",
        "https://www.servicenow.com/solutions/ai.html",
    ],
    "Palantir": [
        "https://www.palantir.com/platforms/aip/",
        "https://www.palantir.com/newsroom/ai-security/",
        "https://www.palantir.com/platforms/gotham/",
        "https://www.palantir.com/platforms/foundry/",
        "https://blog.palantir.com/",
    ],
    "SAS": [
        "https://www.sas.com/en_us/solutions/ai/model-management.html",
        "https://www.sas.com/en_us/solutions/ai.html",
        "https://www.sas.com/en_us/solutions/data-management/data-governance.html",
        "https://www.sas.com/en_us/software/model-manager.html",
        "https://www.sas.com/en_us/software/information-governance.html",
    ],
    "Splunk": [
        "https://www.splunk.com/en_us/products/artificial-intelligence.html",
        "https://www.splunk.com/en_us/products/splunk-ai-assistant.html",
        "https://www.splunk.com/en_us/products/unified-security-and-observability-platform.html",
        "https://www.splunk.com/en_us/blog/ai.html",
        "https://www.splunk.com/en_us/products/security-analytics.html",
    ],
    "Elastic": [
        "https://www.elastic.co/elasticsearch/ai",
        "https://www.elastic.co/security",
        "https://www.elastic.co/enterprise-search",
        "https://www.elastic.co/blog/ai-security",
        "https://www.elastic.co/security/ai-assistant",
    ],
    # ── Security Vendors ──────────────────────────────────────────────
    "CrowdStrike": [
        "https://www.crowdstrike.com/platform/charlotte-ai/",
        "https://www.crowdstrike.com/blog/ai-security/",
        "https://www.crowdstrike.com/platform/",
        "https://www.crowdstrike.com/platform/falcon-data-protection/",
        "https://www.crowdstrike.com/platform/falcon-identity-protection/",
    ],
    "Palo Alto Networks": [
        "https://www.paloaltonetworks.com/prisma/ai-security",
        "https://www.paloaltonetworks.com/cortex/cortex-xsiam",
        "https://www.paloaltonetworks.com/ai-security",
        "https://docs.paloaltonetworks.com/ai-security",
        "https://www.paloaltonetworks.com/prisma/cloud/data-security",
    ],
    "Darktrace": [
        "https://darktrace.com/products/ai-security",
        "https://darktrace.com/cyber-ai-analyst",
        "https://darktrace.com/platform",
        "https://darktrace.com/products/detect",
        "https://darktrace.com/products/proactive-exposure-management",
    ],
    "Check Point Software": [
        "https://www.checkpoint.com/infinity/ai-copilot/",
        "https://www.checkpoint.com/ai-security/",
        "https://www.checkpoint.com/quantum/data-loss-prevention/",
        "https://www.checkpoint.com/cloudguard/",
        "https://www.checkpoint.com/infinity/",
    ],
    "Fortinet": [
        "https://www.fortinet.com/solutions/enterprise-midsize-business/ai-security",
        "https://www.fortinet.com/products/fortianalyzer",
        "https://www.fortinet.com/products/fortiai",
        "https://www.fortinet.com/products/data-loss-prevention",
        "https://www.fortinet.com/products/security-fabric",
    ],
    "Securonix": [
        "https://www.securonix.com/products/",
        "https://www.securonix.com/products/siem/",
        "https://www.securonix.com/products/ueba/",
        "https://www.securonix.com/platform/",
        "https://www.securonix.com/solutions/insider-threat-detection/",
    ],
    "Rapid7": [
        "https://www.rapid7.com/products/insightconnect/",
        "https://www.rapid7.com/products/",
        "https://www.rapid7.com/products/insightvm/",
        "https://www.rapid7.com/about/press-releases/ai-security/",
        "https://www.rapid7.com/solutions/",
    ],
    "Qualys": [
        "https://www.qualys.com/platform/",
        "https://www.qualys.com/apps/cybersecurity-asset-management/",
        "https://www.qualys.com/apps/policy-compliance/",
        "https://blog.qualys.com/vulnerabilities-threat-research",
        "https://www.qualys.com/platform/cloud-security/",
    ],
    "Tenable": [
        "https://www.tenable.com/products/tenable-ai-aware",
        "https://www.tenable.com/products/tenable-one",
        "https://www.tenable.com/data-security",
        "https://www.tenable.com/solutions/ai-security",
        "https://www.tenable.com/products/exposure-ai",
    ],
    "Proofpoint": [
        "https://www.proofpoint.com/us/products/information-protection/data-loss-prevention",
        "https://www.proofpoint.com/us/products/information-protection",
        "https://www.proofpoint.com/us/threat-reference/data-governance",
        "https://www.proofpoint.com/us/products",
        "https://www.proofpoint.com/us/solutions/gen-ai-security",
    ],
    "RSA Security": [
        "https://www.rsa.com/products/",
        "https://www.rsa.com/products/governance-and-lifecycle/",
        "https://www.rsa.com/resources/ai-cybersecurity/",
        "https://www.rsa.com/products/access-management/",
        "https://www.rsa.com/blog/",
    ],
    "Veracode": [
        "https://www.veracode.com/products/fix-ai",
        "https://www.veracode.com/products",
        "https://www.veracode.com/resources/ai-security",
        "https://www.veracode.com/products/software-composition-analysis",
        "https://www.veracode.com/solutions/ai-security",
    ],
    # ── Data Governance & AI-Native ───────────────────────────────────
    "OneTrust": [
        "https://www.onetrust.com/solutions/ai-governance/",
        "https://www.onetrust.com/products/ai-governance/",
        "https://www.onetrust.com/products/data-discovery/",
        "https://www.onetrust.com/products/privacy-management/",
        "https://www.onetrust.com/solutions/responsible-ai/",
    ],
    "DataRobot": [
        "https://www.datarobot.com/platform/mlops/",
        "https://www.datarobot.com/platform/ai-governance/",
        "https://www.datarobot.com/platform/",
        "https://www.datarobot.com/solutions/responsible-ai/",
        "https://www.datarobot.com/blog/",
    ],
    "Alation": [
        "https://www.alation.com/solutions/ai-governance/",
        "https://www.alation.com/product/data-catalog/",
        "https://www.alation.com/product/data-governance/",
        "https://www.alation.com/solutions/generative-ai/",
        "https://www.alation.com/blog/",
    ],
    "Immuta": [
        "https://www.immuta.com/platform/",
        "https://www.immuta.com/solutions/ai-security/",
        "https://www.immuta.com/solutions/data-governance/",
        "https://www.immuta.com/solutions/data-security/",
        "https://www.immuta.com/blog/",
    ],
    "BigID": [
        "https://bigid.com/platform/",
        "https://bigid.com/solutions/ai-data-governance/",
        "https://bigid.com/solutions/data-classification/",
        "https://bigid.com/solutions/data-security-posture-management/",
        "https://bigid.com/solutions/data-privacy/",
    ],
    "TrustArc": [
        "https://trustarc.com/solutions/ai-governance/",
        "https://trustarc.com/products/",
        "https://trustarc.com/solutions/privacy-compliance/",
        "https://trustarc.com/resources/",
        "https://trustarc.com/blog/",
    ],
    "OpenAI": [
        "https://openai.com/safety/",
        "https://platform.openai.com/docs/guides/safety-best-practices",
        "https://openai.com/policies/usage-policies",
        "https://openai.com/index/our-approach-to-ai-safety/",
        "https://openai.com/index/preparedness-framework-beta/",
        "https://openai.com/charter/",
    ],
    "Anthropic": [
        "https://www.anthropic.com/research",
        "https://docs.anthropic.com/en/docs/about-claude/use-case-guides/content-moderation",
        "https://www.anthropic.com/news/responsible-scaling-policy",
        "https://www.anthropic.com/news/core-views-on-ai-safety",
        "https://www.anthropic.com/news/claudes-character",
    ],
    # ── Identity & Access ─────────────────────────────────────────────
    "Okta": [
        "https://www.okta.com/identity-governance/",
        "https://www.okta.com/products/",
        "https://www.okta.com/blog/ai-identity-security/",
        "https://www.okta.com/solutions/ai/",
        "https://www.okta.com/products/privileged-access/",
    ],
    "Thales Group": [
        "https://www.thalesgroup.com/en/markets/digital-identity-and-security/data-protection",
        "https://cpl.thalesgroup.com/encryption/data-security-platform",
        "https://cpl.thalesgroup.com/access-management",
        "https://cpl.thalesgroup.com/data-discovery-classification",
        "https://www.thalesgroup.com/en/worldwide/digital-identity-and-security/ai",
    ],
    # ── IBM ───────────────────────────────────────────────────────────
    "IBM": [
        "https://www.ibm.com/watsonx/governance",
        "https://www.ibm.com/products/openscale",
        "https://www.ibm.com/topics/ai-governance",
        "https://www.ibm.com/products/watson-openscale",
        "https://www.ibm.com/products/guardium",
        "https://www.ibm.com/ai",
    ],
    "IBM Security": [
        "https://www.ibm.com/security/artificial-intelligence",
        "https://www.ibm.com/guardium",
        "https://www.ibm.com/security",
        "https://www.ibm.com/products/guardium-data-security-center",
        "https://www.ibm.com/products/verify-governance",
    ],
    # ── IT Services / Outsourcers ─────────────────────────────────────
    "Atos": [
        "https://atos.net/en/solutions/artificial-intelligence",
        "https://atos.net/en/solutions/cybersecurity",
        "https://atos.net/en/solutions/decarbonization/responsible-ai",
        "https://atos.net/en/solutions/trustworthy-ai",
        "https://atos.net/en/solutions/data-management",
    ],
    "Capgemini": [
        "https://www.capgemini.com/solutions/ai-and-analytics/responsible-ai/",
        "https://www.capgemini.com/solutions/ai-and-analytics/generative-ai/",
        "https://www.capgemini.com/solutions/cybersecurity/",
        "https://www.capgemini.com/solutions/data/",
        "https://www.capgemini.com/solutions/ai-and-analytics/",
    ],
    "CGI": [
        "https://www.cgi.com/en/artificial-intelligence",
        "https://www.cgi.com/en/cybersecurity",
        "https://www.cgi.com/en/data-management-analytics",
        "https://www.cgi.com/en/data-governance",
        "https://www.cgi.com/en/responsible-ai",
    ],
    "Cognizant": [
        "https://www.cognizant.com/us/en/services/ai",
        "https://www.cognizant.com/us/en/services/ai/responsible-ai",
        "https://www.cognizant.com/us/en/services/cybersecurity",
        "https://www.cognizant.com/us/en/services/data-modernization",
        "https://www.cognizant.com/us/en/services/ai/generative-ai",
    ],
    "DXC Technology": [
        "https://dxc.com/us/en/services/analytics-and-engineering/artificial-intelligence",
        "https://dxc.com/us/en/services/security",
        "https://dxc.com/us/en/services/analytics-and-engineering",
        "https://dxc.com/us/en/insights/perspectives/artificial-intelligence",
        "https://dxc.com/us/en/services/analytics-and-engineering/data-management",
    ],
    "Fujitsu": [
        "https://www.fujitsu.com/global/services/ai/",
        "https://www.fujitsu.com/global/solutions/business-technology/ai/",
        "https://www.fujitsu.com/global/services/cybersecurity/",
        "https://www.fujitsu.com/global/about/research/article/responsible-ai.html",
        "https://www.fujitsu.com/global/services/ai/responsible-ai/",
    ],
    "HCLTech": [
        "https://www.hcltech.com/artificial-intelligence",
        "https://www.hcltech.com/artificial-intelligence/responsible-ai",
        "https://www.hcltech.com/cybersecurity",
        "https://www.hcltech.com/data-and-analytics",
        "https://www.hcltech.com/generative-ai",
    ],
    "Infosys": [
        "https://www.infosys.com/services/ai-automation.html",
        "https://www.infosys.com/services/ai-automation/responsible-ai.html",
        "https://www.infosys.com/services/cyber-security.html",
        "https://www.infosys.com/services/data-analytics.html",
        "https://www.infosys.com/services/generative-ai.html",
    ],
    "LTI (Larsen & Toubro Infotech)": [
        "https://www.ltimindtree.com/services/ai-and-data-analytics/",
        "https://www.ltimindtree.com/services/cybersecurity/",
        "https://www.ltimindtree.com/services/cloud-infrastructure/",
        "https://www.ltimindtree.com/services/data-engineering/",
        "https://www.ltimindtree.com/solutions/generative-ai/",
    ],
    "Mindtree": [
        "https://www.ltimindtree.com/services/ai-and-data-analytics/",
        "https://www.ltimindtree.com/services/cybersecurity/",
        "https://www.ltimindtree.com/ltimindtree-ai/",
        "https://www.ltimindtree.com/services/data-engineering/",
        "https://www.ltimindtree.com/solutions/responsible-ai/",
    ],
    "Mphasis": [
        "https://www.mphasis.com/home/services/artificial-intelligence.html",
        "https://www.mphasis.com/home/services/digital-risk.html",
        "https://www.mphasis.com/home/services/data-analytics.html",
        "https://www.mphasis.com/home/services/cognitive-computing.html",
        "https://www.mphasis.com/home/services/cybersecurity.html",
    ],
    "NTT DATA": [
        "https://www.nttdata.com/global/en/services/artificial-intelligence",
        "https://www.nttdata.com/global/en/services/cybersecurity",
        "https://www.nttdata.com/global/en/services/data-intelligence",
        "https://www.nttdata.com/global/en/insights/responsible-ai",
        "https://www.nttdata.com/global/en/services/generative-ai",
    ],
    "Tata Consultancy Services": [
        "https://www.tcs.com/what-we-do/industries/ai",
        "https://www.tcs.com/what-we-do/services/cybersecurity",
        "https://www.tcs.com/what-we-do/services/data-analytics",
        "https://www.tcs.com/what-we-do/research-innovation/articles/responsible-ai",
        "https://www.tcs.com/what-we-do/services/cognitive-business-operations",
    ],
    "Tech Mahindra": [
        "https://www.techmahindra.com/en-in/artificial-intelligence/",
        "https://www.techmahindra.com/en-in/cybersecurity/",
        "https://www.techmahindra.com/en-in/data-privacy/",
        "https://www.techmahindra.com/en-in/responsible-ai/",
        "https://www.techmahindra.com/en-in/generative-ai/",
    ],
    "Wipro": [
        "https://www.wipro.com/ai/",
        "https://www.wipro.com/cybersecurity-and-risk/",
        "https://www.wipro.com/data-and-analytics/",
        "https://www.wipro.com/ai/responsible-ai/",
        "https://www.wipro.com/ai/generative-ai/",
    ],
    "Sopra Steria": [
        "https://www.soprasteria.com/expertise/artificial-intelligence",
        "https://www.soprasteria.com/expertise/cybersecurity",
        "https://www.soprasteria.com/expertise/data-intelligence",
        "https://www.soprasteria.com/about-us/responsible-digital",
        "https://www.soprasteria.com/expertise/ai-trust",
    ],
    "Unisys": [
        "https://www.unisys.com/solutions/digital-workplace/ai/",
        "https://www.unisys.com/solutions/cybersecurity-solutions/",
        "https://www.unisys.com/solutions/enterprise-computing/",
        "https://www.unisys.com/about-us/innovation/ai/",
        "https://www.unisys.com/solutions/digital-workplace/",
    ],
    # ── Industrial / Conglomerate ─────────────────────────────────────
    "Hitachi Consulting": [
        "https://www.hitachivantara.com/en-us/solutions/ai-analytics.html",
        "https://www.hitachivantara.com/en-us/solutions/data-governance.html",
        "https://social-innovation.hitachi/en-eu/digital/ai/",
        "https://www.hitachivantara.com/en-us/solutions/data-management.html",
        "https://social-innovation.hitachi/en-eu/case-studies/responsible-ai/",
    ],
    "Honeywell": [
        "https://www.honeywell.com/us/en/company/artificial-intelligence",
        "https://www.honeywell.com/us/en/cybersecurity",
        "https://www.honeywell.com/us/en/company/quantum",
        "https://www.honeywell.com/us/en/solutions/connected-enterprise",
        "https://www.honeywell.com/us/en/press/2024/ai-solutions",
    ],
    "Siemens": [
        "https://www.siemens.com/global/en/products/automation/industrial-ai.html",
        "https://www.siemens.com/global/en/products/services/cybersecurity.html",
        "https://www.siemens.com/global/en/products/xcelerator/ai.html",
        "https://www.siemens.com/global/en/company/digital-transformation/responsible-ai.html",
        "https://www.siemens.com/global/en/products/software/data-governance.html",
    ],
}

# 3rd-party sources queried for ALL vendors (vendor name substituted)
THIRD_PARTY_SOURCES = [
    "https://www.gartner.com/reviews/search?query={vendor}+AI+TRiSM",
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
# Cache management — separate from DFIR caches (pages_trism/)
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
# Schema-driven term extraction for AI TRiSM
# ─────────────────────────────────────────────────────────────────────

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "case",
    "could", "for", "from", "has", "have", "how", "if", "in", "into",
    "is", "it", "its", "may", "of", "on", "or", "our", "post",
    "should", "the", "their", "they", "this", "that", "these", "those",
    "to", "up", "use", "used", "using", "via", "was", "were", "will",
    "with", "without", "your", "you", "we",
}

# Pillar-specific terms — used to differentiate scores per pillar/sub-pillar
PILLAR_SPECIFIC_TERMS: Dict[str, List[str]] = {
    "GOV": [
        "ai governance", "ai registry", "ai catalog", "model inventory",
        "model card", "ai lineage", "ai audit", "ai compliance",
        "ai transparency", "ai accountability", "ai assurance", "ai posture",
        "model risk management", "ai ethics", "responsible ai", "ai policy",
        "ai regulation", "eu ai act", "nist ai rmf", "iso 42001",
        "ai bill of materials", "ai bom", "model governance", "ai risk",
        "ai trust", "trism",
    ],
    "RUN": [
        "prompt injection", "jailbreak", "guardrails", "ai guardrails",
        "content filtering", "content safety", "runtime inspection",
        "ai firewall", "llm security", "model monitoring", "ai gateway",
        "ai proxy", "hallucination detection", "toxicity detection",
        "ai safety", "red teaming", "adversarial testing", "prompt defense",
        "runtime enforcement", "policy engine", "ai security",
    ],
    "INF": [
        "data governance", "data classification", "data discovery",
        "data access control", "data loss prevention", "dlp",
        "dspm", "data security posture", "privacy enhancing",
        "data masking", "tokenization", "synthetic data",
        "differential privacy", "confidential computing",
        "access governance", "permission management", "oversharing",
        "data catalog", "data privacy", "consent management",
    ],
}


def _build_trism_subpillar_terms(schema: Dict[str, Any]) -> Dict[str, List[str]]:
    """Extract search terms per sub-pillar, returning TWO sets:
    - Schema-specific criteria terms (from ai_evaluation_criteria)  
    - Pillar-specific terms
    Returned as a single list but the first N are schema-specific.
    Also stores metadata for scoring differentiation.
    """
    body = None
    for key in schema:
        if key.startswith("ai_trism_taxonomy"):
            body = schema[key]
            break
    if body is None:
        body = schema

    subs = body.get("sub_pillars", {})

    def _normalize(t: str) -> str:
        t = t.strip().lower()
        t = re.sub(r"[^a-z0-9\-\s/]", " ", t)
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

        criteria = info.get("ai_evaluation_criteria", [])
        for c in criteria:
            if isinstance(c, str) and c.strip():
                schema_terms.append(c)
                schema_terms.extend(_tokenize(c))

        # ── Pillar-specific terms (medium priority) ──
        pillar_terms = PILLAR_SPECIFIC_TERMS.get(pillar, [])

        # ── Global TRiSM terms (low priority — only used for baseline detection) ──
        # NOT included in matching terms — only pillar-specific and schema terms
        # Global terms are used separately in specificity scoring

        # Combine schema + pillar terms (NOT global)
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


# Also store schema-specific terms separately for scoring weight
_schema_criteria_terms_cache: Dict[str, set] = {}


def _build_schema_criteria_set(schema: Dict[str, Any]) -> Dict[str, set]:
    """Extract ONLY the schema ai_evaluation_criteria per sub-pillar for weighting."""
    if _schema_criteria_terms_cache:
        return _schema_criteria_terms_cache

    body = None
    for key in schema:
        if key.startswith("ai_trism_taxonomy"):
            body = schema[key]
            break
    if body is None:
        body = schema

    subs = body.get("sub_pillars", {})

    def _normalize(t: str) -> str:
        t = t.strip().lower()
        t = re.sub(r"[^a-z0-9\-\s/]", " ", t)
        return re.sub(r"\s+", " ", t).strip()

    for sid in SUBPILLAR_IDS:
        info = subs.get(sid, {})
        criteria = info.get("ai_evaluation_criteria", [])
        cset = set()
        for c in criteria:
            if isinstance(c, str) and c.strip():
                cset.add(_normalize(c))
                # Also add individual significant words
                for w in _normalize(c).replace("-", " ").split():
                    if len(w) >= 5 and w not in STOPWORDS:
                        cset.add(w)
        _schema_criteria_terms_cache[sid] = cset

    return _schema_criteria_terms_cache


# ─────────────────────────────────────────────────────────────────────
# Text analysis & TRiSM-weighted evidence extraction
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
    trism_term_count: int  # how many TRiSM-specific terms matched


def _count_trism_terms_in_text(text_lower: str) -> int:
    """Count how many TRiSM-specific terms appear in text (with synonyms)."""
    return sum(1 for term in TRISM_PRIMARY_TERMS if _term_in_text(term, text_lower))


def _trism_specificity_score(text_lower: str) -> float:
    """Score TRiSM specificity from 0-5 based on term density.
    Maps to the AI TRiSM scoring logic:
      0 = No Evidence
      1 = No AI/ML (policy/process only)
      2 = Generic AI Claims
      3 = AI-Augmented (documented)
      4 = Advanced AI (measurable)
      5 = Fully Agentic
    """
    trism_hits = _count_trism_terms_in_text(text_lower)
    exclusion_hits = sum(1 for t in TRISM_EXCLUSION_TERMS if t in text_lower)

    if exclusion_hits > trism_hits:
        return 1.0

    if trism_hits == 0:
        return 0.0
    if trism_hits <= 2:
        return 2.0
    if trism_hits <= 5:
        return 3.0
    if trism_hits <= 10:
        return 4.0
    return 5.0


def _score_subpillar_trism(
    trism_specificity: float,
    criteria_hit_count: int,
    total_excerpts: int,
) -> float:
    """TRiSM-weighted scoring.
    
    Scoring scale from AI TriSM Schema 1_0.json:
      0 = No Evidence
      1 = No AI/ML
      2 = Generic AI Claims
      3 = AI-Augmented
      4 = Advanced AI
      5 = Fully Agentic
    """
    if total_excerpts == 0:
        return 0.0

    if trism_specificity < 0.5:
        if criteria_hit_count > 0:
            return 1.0
        return 0.0

    if trism_specificity <= 2.0:
        base = 2.0
        if criteria_hit_count >= 3:
            base = 2.25
        return base

    if trism_specificity <= 3.0:
        base = 3.0
        if criteria_hit_count >= 5:
            base = 3.25
        elif criteria_hit_count >= 3:
            base = 3.0
        else:
            base = 2.75
        return base

    if trism_specificity <= 4.0:
        base = 4.0
        if criteria_hit_count >= 5:
            base = 4.25
        elif criteria_hit_count >= 3:
            base = 4.0
        else:
            base = 3.75
        return base

    # Fully agentic
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
# URL Discovery for TRiSM vendors
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
# Evidence extraction (per vendor) — TRiSM-focused
# ─────────────────────────────────────────────────────────────────────


GENERIC_MATCH_TERMS = {
    "ai", "automated", "automation", "analysis", "detection", "response",
    "security", "platform", "dashboard", "workflow", "governance",
    "compliance", "privacy", "data",
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
    """Extract TRiSM-focused evidence and compute per-sub-pillar scores.
    
    Key difference from DFIR v3: scores are computed per-sub-pillar, not globally.
    Each sub-pillar gets its own specificity score based on:
    1. Schema-specific criteria matches (highest weight)
    2. Pillar-specific term matches (medium weight)
    3. Only generic terms (lowest weight)
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
                                  any(_term_in_text(c_term, s_lower) for c_term in criteria_set if len(c_term) >= 6))
                pillar_hits = sum(1 for t in matched if t in pillar_terms_set)
                relevance_score = schema_hits * 3 + pillar_hits * 2 + len(matched)

                hits.append(EvidenceHit(
                    url=url, excerpt=sent.strip(),
                    matched_terms=matched[:10],
                    trism_term_count=relevance_score,
                ))

        # Sort by relevance score descending, take top N
        hits.sort(key=lambda h: h.trism_term_count, reverse=True)
        top_hits = hits[:max_excerpts_per_subpillar]

        # ── Per-sub-pillar specificity scoring ──
        # Count pillar-specific terms in the text (not global)
        all_text_lower = " ".join(t for _, t in pages_text).lower()

        pillar_term_hits = sum(1 for t in pillar_terms_set if _term_in_text(t, all_text_lower))
        schema_criteria_hits = sum(1 for t in criteria_set if len(t) >= 5 and _term_in_text(t, all_text_lower))

        # Compute sub-pillar-specific specificity
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
            elif any(_term_in_text(t, all_text_lower) for t in TRISM_PRIMARY_TERMS):
                sp_specificity = 1.5
            else:
                sp_specificity = 0.0
        else:
            sp_specificity = 0.0

        # Check exclusion terms
        exclusion_hits = sum(1 for t in TRISM_EXCLUSION_TERMS if t in all_text_lower) if pages_text else 0
        if exclusion_hits > pillar_term_hits + schema_criteria_hits:
            sp_specificity = max(0.0, sp_specificity - 1.0)

        # Score using per-sub-pillar specificity
        criteria_hit_count = sum(1 for h in top_hits if h.trism_term_count > 2)
        score = _score_subpillar_trism(sp_specificity, criteria_hit_count, len(top_hits))

        sub_evidence[sid] = {
            "source_urls": list({h.url for h in top_hits}),
            "excerpts": [
                {
                    "url": h.url,
                    "excerpt": _shorten(h.excerpt, 260),
                    "matched_terms": h.matched_terms[:6],
                    "relevance_score": h.trism_term_count,
                }
                for h in top_hits
            ],
            "sub_pillar_specificity": round(sp_specificity, 2),
            "schema_criteria_hits": schema_criteria_hits,
            "pillar_term_hits": pillar_term_hits,
            "criteria_hit_count": criteria_hit_count,
            "notes": f"TRiSM claims extraction; {len(top_hits)} excerpts from {ok_pages} pages."
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
        if key.startswith("ai_trism_taxonomy"):
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

    evidence_line = "No TRiSM-specific evidence captured."
    if excerpts_raw:
        first = excerpts_raw[0]
        excerpt_text = _shorten(str(first.get("excerpt", "")), 200)
        evidence_line = f'TRiSM signal: "{excerpt_text}".'
        if len(excerpts_raw) > 1:
            second = _shorten(str(excerpts_raw[1].get("excerpt", "")), 150)
            evidence_line += f' Also: "{second}".'

    trism_level = "None"
    if sp_specificity >= 4.5:
        trism_level = "Fully Agentic"
    elif sp_specificity >= 3.5:
        trism_level = "Advanced AI"
    elif sp_specificity >= 2.5:
        trism_level = "AI-Augmented"
    elif sp_specificity >= 1.5:
        trism_level = "Generic AI Claims"
    elif sp_specificity >= 0.5:
        trism_level = "No AI/ML"

    parts = [
        f"{sid} - {name}. TRiSM Score: {score_str}.",
        f"TRiSM Maturity Level: {trism_level} (specificity={sp_specificity:.1f}).",
        f"Evidence flag: {research_flag}.",
        evidence_line,
    ]

    if score < 3.0:
        parts.append(
            "To improve: Publicly document specific AI governance, runtime enforcement, "
            "or information governance controls with measurable outcomes."
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
    return CHECKPOINT_DIR / "claims_progress.json"


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

    # Write output — always uses AI TRiSM schema_ref
    out_data = {
        "schema_ref": "AI TriSM Schema 1_0.json",
        "schema_version": "1.0",
        "vendor_count": len(merged),
        "research_tool": "research_trism_v1_claims.py",
        "research_timestamp": datetime.now(timezone.utc).isoformat(),
        "vendors": merged,
    }
    output_file.write_text(
        json.dumps(out_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nWrote merged output: {output_file.name}")
    print(f"  {len(merged)} vendors total, {scored_count} with TRiSM scores")
    return 0


# ─────────────────────────────────────────────────────────────────────
# Main — batch-of-5 processing loop
# ─────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description="AI TRiSM Vendor Claims Research")
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
    terms_by_sub = _build_trism_subpillar_terms(schema)
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

            trism_pillars = compute_pillar_scores(sub_scores)

            # Build rationales
            rationale: Dict[str, str] = {}
            for sid in SUBPILLAR_IDS:
                rationale[sid] = build_rationale(
                    schema, vendor, sid,
                    sub_evidence, sub_scores,
                    research_flag,
                )

            # Update vendor record — TRiSM-specific keys
            v_out = dict(vendor)
            v_out["sub_pillar_evidence"] = sub_evidence
            v_out["sub_pillar_scores_validated"] = sub_scores
            v_out["pillar_scores_validated"] = trism_pillars
            v_out["pillar_scores"] = trism_pillars  # also update display scores
            v_out["sub_pillar_scores_current"] = sub_scores  # sync current layer
            v_out["sub_pillar_rationale_validated"] = rationale
            v_out["research_flag"] = research_flag
            v_out["research_confidence"] = research_confidence
            v_out["research"] = {
                "status": "trism_validated_v1",
                "source": "public_web_text",
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "urls_used": urls,
                "pages_ok": vendor_summary.get("ok_pages", 0),
                "schema": args.schema_file.name,
                "tool": "research_trism_v1_claims.py",
                "cap_applied": cap_applied,
            }

            batch_results.append(v_out)

            ok_pages = vendor_summary.get("ok_pages", 0)
            excerpts = vendor_summary.get("excerpts_total", 0)
            print(f"    Pages OK: {ok_pages}/{len(urls)}, Excerpts: {excerpts}, "
                  f"Flag: {research_flag}")
            print(f"    Pillar scores: GOV={trism_pillars.get('GOV',0):.2f} "
                  f"RUN={trism_pillars.get('RUN',0):.2f} "
                  f"INF={trism_pillars.get('INF',0):.2f}")

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
