"""
research_precyber_svc_pricing.py — Services + Pricing Research for Preemptive Cybersecurity
============================================================================================

Evaluates 51 PreCyber vendors on:
  - 8 new services maturity sub-pillars:
      EXM-05, AMT-05, ADR-05, PPM-05 (per-pillar services maturity)
      SVC-01, SVC-02, SVC-03, SVC-04 (standalone services pillar)
  - 6 pricing dimensions:
      PRC-SUB, PRC-USG, PRC-FIX, PRC-SUC, PRC-COM, PRC-OUT
  - Outcome maturity rating

Uses existing cached pages from research/cache/pages_precyber/ (260 pages) first,
then fetches additional service/pricing-specific URLs as needed.

Follows the same approach as research_precyber_v1_evidence.py for evidence extraction
and build_mdr_pricing_v2.py for pricing dimension scoring.

Output: Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json
  (merges new SVC/pricing data into existing v2.1 vendor records)

Usage:
  python research_precyber_svc_pricing.py                     # full run (51 vendors)
  python research_precyber_svc_pricing.py --max-vendors 5     # test with 5
  python research_precyber_svc_pricing.py --batch-size 5      # batch size
  python research_precyber_svc_pricing.py --force-fetch        # re-fetch cached pages
  python research_precyber_svc_pricing.py --resume             # resume from checkpoint
  python research_precyber_svc_pricing.py --merge-only         # just merge batches
"""

import argparse
import hashlib
import io
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Force UTF-8 output on Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent

INPUT_FILE  = ROOT / "Preemptive Cybersecurity Vendor 2-1 Consolidated.json"
SCHEMA_FILE = ROOT / "Preemptive_Cybersecurity_Schema_v2.json"
OUTPUT_FILE = ROOT / "Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json"

# Reuse existing precyber cache for pages already fetched
CACHE_DIR       = ROOT / "research" / "cache" / "pages_precyber"
CHECKPOINT_DIR  = ROOT / "research" / "precyber_svc_checkpoints"
BATCH_DIR       = ROOT / "research" / "precyber_svc_batches"

# The 8 new services sub-pillars to evaluate
SVC_SUBPILLARS = [
    "EXM-05", "AMT-05", "ADR-05", "PPM-05",
    "SVC-01", "SVC-02", "SVC-03", "SVC-04",
]

# The 6 pricing dimensions
PRICING_DIMS = ["PRC-SUB", "PRC-USG", "PRC-FIX", "PRC-SUC", "PRC-COM", "PRC-OUT"]

MAX_EXCERPTS = 5
FETCH_SLEEP  = 1.5

URL_RE = re.compile(r"https?://[^\s)\]\}\">,]+")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]


# ─────────────────────────────────────────────────────────────
# Service/pricing-specific URLs per vendor (curated)
# These are fetched IN ADDITION to existing cached pages
# ─────────────────────────────────────────────────────────────

SVC_PRICING_URLS: Dict[str, List[str]] = {
    "Tenable": [
        "https://www.tenable.com/products/tenable-one/pricing",
        "https://www.tenable.com/services",
        "https://www.tenable.com/partners/managed-security-service-providers",
        "https://www.tenable.com/products/managed-services",
    ],
    "Qualys": [
        "https://www.qualys.com/pricing/",
        "https://www.qualys.com/services/",
        "https://www.qualys.com/consulting/",
        "https://www.qualys.com/partners/managed-service-providers/",
    ],
    "Rapid7": [
        "https://www.rapid7.com/products/insightvm/pricing/",
        "https://www.rapid7.com/services/",
        "https://www.rapid7.com/services/managed-detection-and-response/",
        "https://www.rapid7.com/partners/managed-service-providers/",
    ],
    "CrowdStrike": [
        "https://www.crowdstrike.com/platform/pricing/",
        "https://www.crowdstrike.com/services/",
        "https://www.crowdstrike.com/services/managed-detection-and-response/",
        "https://www.crowdstrike.com/platform/falcon-complete/",
    ],
    "Palo Alto Networks": [
        "https://www.paloaltonetworks.com/cortex/cortex-xsiam/pricing",
        "https://www.paloaltonetworks.com/unit42",
        "https://www.paloaltonetworks.com/unit42/consulting",
        "https://www.paloaltonetworks.com/services",
    ],
    "Censys": [
        "https://censys.com/pricing/",
        "https://censys.com/managed-services/",
        "https://censys.com/professional-services/",
    ],
    "CyCognito": [
        "https://www.cycognito.com/pricing",
        "https://www.cycognito.com/services",
        "https://www.cycognito.com/platform/managed-services",
    ],
    "Armis": [
        "https://www.armis.com/pricing/",
        "https://www.armis.com/services/",
        "https://www.armis.com/managed-services/",
    ],
    "Axonius": [
        "https://www.axonius.com/pricing",
        "https://www.axonius.com/services",
        "https://www.axonius.com/solutions/managed-services",
    ],
    "JupiterOne": [
        "https://www.jupiterone.com/pricing",
        "https://www.jupiterone.com/services",
    ],
    "XM Cyber": [
        "https://www.xmcyber.com/pricing/",
        "https://www.xmcyber.com/services/",
        "https://www.xmcyber.com/managed-services/",
    ],
    "Bitsight": [
        "https://www.bitsight.com/pricing",
        "https://www.bitsight.com/products/managed-services",
        "https://www.bitsight.com/services",
    ],
    "SecurityScorecard": [
        "https://securityscorecard.com/pricing/",
        "https://securityscorecard.com/products/managed-services/",
        "https://securityscorecard.com/services/",
    ],
    "Panorays": [
        "https://www.panorays.com/pricing",
        "https://www.panorays.com/services",
    ],
    "Morphisec": [
        "https://www.morphisec.com/pricing/",
        "https://www.morphisec.com/services/",
        "https://www.morphisec.com/managed-services/",
    ],
    "RunSafe Security": [
        "https://runsafesecurity.com/pricing/",
        "https://runsafesecurity.com/services/",
    ],
    "Contrast Security": [
        "https://www.contrastsecurity.com/pricing",
        "https://www.contrastsecurity.com/services",
        "https://www.contrastsecurity.com/managed-services",
    ],
    "Illumio": [
        "https://www.illumio.com/pricing",
        "https://www.illumio.com/services",
        "https://www.illumio.com/solutions/professional-services",
    ],
    "Akamai (Guardicore)": [
        "https://www.akamai.com/products/akamai-guardicore-segmentation/pricing",
        "https://www.akamai.com/services",
        "https://www.akamai.com/products/managed-security-service",
    ],
    "Zscaler": [
        "https://www.zscaler.com/products/pricing",
        "https://www.zscaler.com/services",
        "https://www.zscaler.com/products/professional-services",
    ],
    "CyberArk": [
        "https://www.cyberark.com/pricing/",
        "https://www.cyberark.com/services/",
        "https://www.cyberark.com/products/managed-services/",
    ],
    "BeyondTrust": [
        "https://www.beyondtrust.com/pricing",
        "https://www.beyondtrust.com/services",
        "https://www.beyondtrust.com/services/professional-services",
    ],
    "Delinea": [
        "https://delinea.com/pricing",
        "https://delinea.com/services",
        "https://delinea.com/professional-services",
    ],
    "HashiCorp": [
        "https://www.hashicorp.com/products/vault/pricing",
        "https://www.hashicorp.com/services",
        "https://www.hashicorp.com/partners/managed-service-providers",
    ],
    "Acalvio Technologies": [
        "https://www.acalvio.com/pricing/",
        "https://www.acalvio.com/services/",
        "https://www.acalvio.com/solutions/managed-deception/",
    ],
    "CounterCraft": [
        "https://www.countercraft.eu/pricing/",
        "https://www.countercraft.eu/services/",
    ],
    "Fidelis Cybersecurity": [
        "https://fidelissecurity.com/pricing/",
        "https://fidelissecurity.com/services/",
        "https://fidelissecurity.com/products/managed-detection-response/",
    ],
    "SentinelOne": [
        "https://www.sentinelone.com/pricing/",
        "https://www.sentinelone.com/platform/singularity-completeness/",
        "https://www.sentinelone.com/platform/vigilance-respond/",
    ],
    "Recorded Future": [
        "https://www.recordedfuture.com/pricing",
        "https://www.recordedfuture.com/services",
        "https://www.recordedfuture.com/products/managed-intelligence",
    ],
    "Mandiant (Google Cloud)": [
        "https://www.mandiant.com/advantage/managed-defense",
        "https://www.mandiant.com/services",
        "https://www.mandiant.com/services/consulting",
    ],
    "ThreatConnect": [
        "https://www.threatconnect.com/pricing/",
        "https://www.threatconnect.com/services/",
    ],
    "Anomali": [
        "https://www.anomali.com/pricing",
        "https://www.anomali.com/services",
    ],
    "ZeroFox": [
        "https://www.zerofox.com/pricing/",
        "https://www.zerofox.com/services/",
        "https://www.zerofox.com/products/managed-services/",
    ],
    "Nisos": [
        "https://www.nisos.com/pricing/",
        "https://www.nisos.com/services/",
    ],
    "Arctic Wolf": [
        "https://arcticwolf.com/pricing/",
        "https://arcticwolf.com/solutions/managed-detection-and-response/",
        "https://arcticwolf.com/solutions/managed-risk/",
    ],
    "Group-IB": [
        "https://www.group-ib.com/pricing/",
        "https://www.group-ib.com/services/",
        "https://www.group-ib.com/products/managed-xdr/",
    ],
    "SafeBreach": [
        "https://www.safebreach.com/pricing/",
        "https://www.safebreach.com/services/",
    ],
    "AttackIQ": [
        "https://www.attackiq.com/pricing/",
        "https://www.attackiq.com/solutions/managed-services/",
        "https://www.attackiq.com/attackiq-ready/",
    ],
    "Cymulate": [
        "https://cymulate.com/pricing/",
        "https://cymulate.com/services/",
        "https://cymulate.com/products/managed-services/",
    ],
    "Pentera": [
        "https://pentera.io/pricing/",
        "https://pentera.io/services/",
    ],
    "Horizon3.ai": [
        "https://www.horizon3.ai/pricing/",
        "https://www.horizon3.ai/services/",
        "https://www.horizon3.ai/nodezero-as-a-service/",
    ],
    "Picus Security": [
        "https://www.picussecurity.com/pricing",
        "https://www.picussecurity.com/services",
    ],
    "Wiz": [
        "https://www.wiz.io/pricing",
        "https://www.wiz.io/services",
    ],
    "Orca Security": [
        "https://orca.security/pricing/",
        "https://orca.security/services/",
    ],
    "Aqua Security": [
        "https://www.aquasec.com/pricing/",
        "https://www.aquasec.com/services/",
    ],
    "Lacework (Fortinet)": [
        "https://www.lacework.com/pricing/",
        "https://www.lacework.com/services/",
    ],
    "Darktrace": [
        "https://darktrace.com/pricing",
        "https://darktrace.com/products/proactive-exposure-management",
        "https://darktrace.com/managed-services",
    ],
    "Fortinet": [
        "https://www.fortinet.com/solutions/enterprise-midsize-business/managed-security",
        "https://www.fortinet.com/support/support-services",
        "https://www.fortinet.com/products/fortiguard/services",
    ],
    "IBM Security": [
        "https://www.ibm.com/security/services",
        "https://www.ibm.com/products/qradar-siem/pricing",
        "https://www.ibm.com/security/managed-services",
    ],
    "Trellix": [
        "https://www.trellix.com/pricing/",
        "https://www.trellix.com/services/",
    ],
    "Cisco (Splunk)": [
        "https://www.cisco.com/site/us/en/services/security-services/index.html",
        "https://www.splunk.com/en_us/products/pricing.html",
        "https://www.cisco.com/site/us/en/solutions/security/managed-security/index.html",
    ],
}


# ─────────────────────────────────────────────────────────────
# Services-specific search terms per sub-pillar
# ─────────────────────────────────────────────────────────────

SVC_SEARCH_TERMS: Dict[str, List[str]] = {
    "EXM-05": [
        "managed ASM", "managed attack surface", "CTEM as a service",
        "managed exposure management", "managed vulnerability",
        "vulnerability management service", "exposure management service",
        "managed EASM", "outsourced vulnerability management",
        "managed attack surface management", "exposure operations",
        "managed discovery", "managed remediation", "vulnerability operations",
    ],
    "AMT-05": [
        "managed AMTD", "managed moving target defense", "managed RASP",
        "managed micro-segmentation", "managed zero trust",
        "managed PAM", "runtime protection service",
        "managed credential rotation", "segmentation as a service",
        "managed network defense", "managed identity", "managed privilege",
        "managed application protection", "zero trust service",
    ],
    "ADR-05": [
        "managed deception", "deception as a service", "managed threat hunting",
        "managed threat intelligence", "managed counter-adversary",
        "managed digital risk protection", "managed DRP",
        "outsourced threat hunting", "managed takedown service",
        "managed intelligence", "managed dark web", "managed hunting",
        "managed SOC", "threat hunting service",
    ],
    "PPM-05": [
        "managed BAS", "BAS as a service", "PTaaS",
        "pen testing as a service", "managed penetration testing",
        "managed security validation", "managed CSPM",
        "managed posture management", "continuous security validation service",
        "managed red team", "managed purple team", "managed simulation",
        "security validation service", "cloud security service",
    ],
    "SVC-01": [
        "professional services", "implementation services", "onboarding",
        "deployment support", "time-to-value", "integration services",
        "customer onboarding", "proof of value", "deployment services",
        "getting started", "setup services", "implementation methodology",
        "onboarding program", "rapid deployment",
    ],
    "SVC-02": [
        "security consulting", "advisory services", "maturity assessment",
        "security architecture review", "CTEM consulting",
        "strategic consulting", "customer success", "security advisory",
        "executive briefing", "security assessment", "gap analysis",
        "roadmap consulting", "strategic advisory",
    ],
    "SVC-03": [
        "managed services", "managed security", "MSSP",
        "managed detection", "24/7 SOC", "managed operations",
        "security operations", "managed preemptive", "MDR",
        "managed response", "continuous monitoring", "managed SOC",
        "dedicated analysts", "SLA-backed", "24x7",
    ],
    "SVC-04": [
        "AI automation", "autonomous security", "GenAI security",
        "agentic security", "AI-augmented SOC", "automated triage",
        "AI-driven response", "autonomous remediation",
        "self-healing security", "copilot security", "AI assistant",
        "machine learning security", "automated investigation",
        "AI-powered", "generative AI", "autonomous operations",
    ],
}

# Pricing search terms per dimension
PRICING_SEARCH_TERMS: Dict[str, List[str]] = {
    "PRC-SUB": [
        "subscription", "recurring", "annual", "monthly", "per-seat",
        "per-endpoint", "per-device", "per-user", "license", "tier",
        "plan", "bundle", "package", "platform fee", "pricing tier",
        "subscription pricing", "service tier", "standard plan",
        "premium plan", "enterprise plan", "base price",
    ],
    "PRC-USG": [
        "usage-based", "consumption", "pay-as-you-go", "metered",
        "per-gb", "data volume", "ingestion", "api call", "overage",
        "threshold", "usage dashboard", "variable cost",
        "consumption-based", "elastic pricing", "pay-per-use",
        "data ingestion", "log volume", "event volume",
    ],
    "PRC-FIX": [
        "fixed fee", "one-time", "setup", "deployment", "implementation",
        "integration", "onboarding", "project", "milestone",
        "professional services", "setup fee", "installation",
        "configuration", "customization", "deployment cost",
    ],
    "PRC-SUC": [
        "success fee", "outcome fee", "performance", "bonus", "penalty",
        "sla", "service level", "mttd", "mttr", "breach warranty",
        "guarantee", "per-incident", "fee-at-risk", "performance-linked",
        "outcome-based", "credit", "rebate", "financial consequence",
    ],
    "PRC-COM": [
        "composable", "modular", "flexible", "customizable",
        "hybrid pricing", "building block", "predictability",
        "risk-sharing", "transparent", "clear pricing",
        "scalable pricing", "mix and match", "configurable",
    ],
    "PRC-OUT": [
        "outcome", "value-based", "roi", "return on investment",
        "risk reduction", "value realization", "outcome-based sla",
        "pricing-to-outcome", "value delivery", "efficiency gain",
        "outcome alignment", "measurable outcome", "demonstrated value",
        "kpi-linked", "performance metric",
    ],
}

# Generic pricing terms (bonus matching for any dimension)
GENERIC_PRICING_TERMS = [
    "pricing", "price", "cost", "fee", "charge", "rate", "billing",
    "commercial", "contract", "proposal", "quote",
]

# Generic services terms (bonus matching for any SVC sub-pillar)
GENERIC_SVC_TERMS = [
    "services", "managed", "professional", "consulting", "advisory",
    "implementation", "deployment", "onboarding", "support",
    "operations", "SOC", "analysts", "SLA", "24/7", "monitoring",
]


# ─────────────────────────────────────────────────────────────
# HTML extraction
# ─────────────────────────────────────────────────────────────

class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: List[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs):
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip += 1

    def handle_endtag(self, tag: str):
        if tag in {"script", "style", "noscript", "svg"} and self._skip > 0:
            self._skip -= 1

    def handle_data(self, data: str):
        if self._skip > 0:
            return
        text = data.strip()
        if text:
            self._chunks.append(text)

    def get_text(self) -> str:
        return "\n".join(self._chunks)


def _html_to_text(html: str) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(html)
    text = unescape(parser.get_text())
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _normalize_text(s: str) -> str:
    s = (s or "").replace("\ufffd", " ").replace("\u00a0", " ")
    s = s.replace("\u2014", "-").replace("\u2013", "-")
    return " ".join(s.split())


def _shorten(s: str, max_len: int = 260) -> str:
    s = _normalize_text(s)
    return s if len(s) <= max_len else s[:max_len - 1] + "\u2026"


# ─────────────────────────────────────────────────────────────
# HTTP fetch with cache (reuses pages_precyber cache)
# ─────────────────────────────────────────────────────────────

def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8"), usedforsecurity=False).hexdigest()


def _cache_path(url: str) -> Path:
    return CACHE_DIR / f"{_sha1(url)}.json"


def _fetch_url_playwright_svc(url: str) -> Optional[str]:
    """Playwright headless-browser fallback for JS-heavy / bot-protected pages."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            try:
                ctx = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                    ),
                    locale="en-US",
                )
                page = ctx.new_page()
                page.goto(url, timeout=20_000, wait_until="domcontentloaded")
                html = page.content()
            finally:
                browser.close()
        return html
    except ImportError:
        return None
    except KeyboardInterrupt:
        raise
    except Exception:
        return None


def fetch_page(url: str, *, force: bool = False, _timeout: int = 6) -> Dict[str, Any]:
    """Fetch a URL with caching. Reuses the existing precyber cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cp = _cache_path(url)

    if cp.exists() and not force:
        try:
            cached = json.loads(cp.read_text(encoding="utf-8"))
            if cached.get("ok") is True:
                return cached
        except Exception:
            pass

    ua = random.choice(USER_AGENTS)
    req = urllib.request.Request(url, headers={
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "identity",
        "Connection": "keep-alive",
    }, method="GET")

    html = None
    render_engine = "urllib"
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=6) as resp:
                raw = resp.read()
                try:
                    html = raw.decode("utf-8", errors="replace")
                except Exception:
                    html = raw.decode(errors="replace")
                break
        except Exception:
            pass  # skip on any error, no retry sleep

    # Playwright fallback: fires when urllib fails or returns bot-blocked content.
    # Check extracted text (not raw HTML) so Cloudflare challenge pages trigger the fallback.
    _extracted = _html_to_text(html) if html else ""
    if not _extracted or len(_extracted.strip()) < 200:
        pw_html = _fetch_url_playwright_svc(url)
        if pw_html:
            pw_text = _html_to_text(pw_html)
            if len(pw_text.strip()) > len(_extracted.strip()):
                html, _extracted = pw_html, pw_text
                render_engine = "playwright"

    if _extracted.strip():
        record = {
            "url": url,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "ok": True,
            "content_type": None,
            "text": _extracted[:200_000],
            "error": None,
            "render_engine": render_engine,
        }
        cp.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return record

    record = {
        "url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "ok": False, "content_type": None, "text": "", "error": "fetch_failed",
        "render_engine": render_engine,
    }
    cp.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


# ─────────────────────────────────────────────────────────────
# Text analysis utilities
# ─────────────────────────────────────────────────────────────

def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if 20 <= len(p.strip()) <= 500]


def _candidate_snippets(text: str) -> List[str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    snippets = []
    for ln in lines:
        if 10 <= len(ln) <= 300:
            snippets.append(ln)
    for a, b in zip(lines, lines[1:]):
        combo = f"{a} {b}".strip()
        if 20 <= len(combo) <= 400:
            snippets.append(combo)
    snippets.extend(_split_sentences(text))
    seen = set()
    out = []
    for s in snippets:
        key = s.lower()[:200]
        if key not in seen:
            seen.add(key)
            out.append(s)
    return out


def _term_in_text(term: str, text_lower: str) -> bool:
    return term.lower() in text_lower


def _count_term_hits(terms: List[str], text_lower: str) -> int:
    return sum(1 for t in terms if _term_in_text(t, text_lower))


# ─────────────────────────────────────────────────────────────
# Schema loading
# ─────────────────────────────────────────────────────────────

def load_schema() -> Dict[str, Any]:
    raw = Path(SCHEMA_FILE).read_text(encoding="utf-8-sig")
    return json.loads(raw)


def get_schema_body(schema: Dict) -> Dict:
    for key in schema:
        if key.startswith("preemptive_cybersecurity_taxonomy"):
            return schema[key]
    return schema


def get_subpillar_info(schema: Dict, sid: str) -> Dict:
    body = get_schema_body(schema)
    return body.get("sub_pillars", {}).get(sid, {})


def get_pricing_dim_info(schema: Dict, dim_id: str) -> Dict:
    body = get_schema_body(schema)
    pe = body.get("pricing_evaluation", {})
    return pe.get("dimensions", {}).get(dim_id, {})


# ─────────────────────────────────────────────────────────────
# Vendor data loading
# ─────────────────────────────────────────────────────────────

def load_vendors() -> List[Dict[str, Any]]:
    raw = Path(INPUT_FILE).read_text(encoding="utf-8-sig")
    data = json.loads(raw)
    if isinstance(data, dict):
        if "vendors" in data:
            return data["vendors"]
        for key in data:
            if isinstance(data[key], list) and data[key] and isinstance(data[key][0], dict):
                return data[key]
    if isinstance(data, list):
        return data
    return []


# ─────────────────────────────────────────────────────────────
# URL discovery per vendor
# ─────────────────────────────────────────────────────────────

def discover_vendor_urls(vendor: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """Returns (existing_cached_urls, new_svc_pricing_urls)."""
    name = vendor.get("vendor", "")
    existing_urls = []
    seen = set()

    def _add(lst, u):
        u_clean = u.lower().rstrip("/")
        if u_clean not in seen:
            seen.add(u_clean)
            lst.append(u)

    # Collect URLs from existing evidence (already cached)
    evidence = vendor.get("sub_pillar_evidence", {})
    for sid, ev in evidence.items():
        if isinstance(ev, dict):
            for u in ev.get("source_urls", []):
                _add(existing_urls, u)

    # New service/pricing-specific URLs
    new_urls = []
    for u in SVC_PRICING_URLS.get(name, []):
        _add(new_urls, u)

    # Also add vendor website /services and /pricing if we can infer it
    website = vendor.get("website", "")
    if website:
        base = website.rstrip("/")
        for suffix in ["/services", "/pricing", "/managed-services", "/professional-services"]:
            _add(new_urls, base + suffix)

    return existing_urls, new_urls


# ─────────────────────────────────────────────────────────────
# Services sub-pillar scoring
# ─────────────────────────────────────────────────────────────

def score_svc_subpillar(
    sid: str,
    schema: Dict,
    pages_text: List[Tuple[str, str]],
) -> Tuple[float, Dict[str, Any]]:
    """Extract evidence and score a services maturity sub-pillar."""
    info = get_subpillar_info(schema, sid)
    search_terms = SVC_SEARCH_TERMS.get(sid, [])
    criteria = info.get("what_to_verify_publicly", [])
    all_text = " ".join(t for _, t in pages_text).lower()
    hits = []

    for url, text in pages_text:
        candidates = _candidate_snippets(text)
        for sent in candidates:
            s_lower = sent.lower()
            matched = []

            # Check search terms
            for term in search_terms:
                if _term_in_text(term, s_lower):
                    matched.append(term)

            # Check criteria phrases (partial matching)
            for cr in criteria:
                cr_words = set(re.findall(r"\b[a-z]{4,}\b", cr.lower()))
                sent_words = set(re.findall(r"\b[a-z]{4,}\b", s_lower))
                overlap = len(cr_words & sent_words)
                if overlap >= 3:
                    matched.append(f"criteria:{cr[:50]}")

            # Check generic SVC terms (lower weight)
            generic_hits = sum(1 for t in GENERIC_SVC_TERMS if _term_in_text(t, s_lower))

            if not matched and generic_hits < 2:
                continue

            # Relevance: criteria matches * 3 + search term matches * 2 + generic
            relevance = len([m for m in matched if m.startswith("criteria:")]) * 3 + \
                        len([m for m in matched if not m.startswith("criteria:")]) * 2 + \
                        generic_hits

            hits.append({
                "url": url,
                "excerpt": _shorten(sent),
                "matched_terms": matched[:8],
                "relevance_score": relevance,
            })

    # Sort by relevance, take top N
    hits.sort(key=lambda h: h["relevance_score"], reverse=True)
    top_hits = hits[:MAX_EXCERPTS]

    # Compute score based on evidence quality
    # Use SPECIFIC search terms (not generic) to differentiate
    search_term_hits = _count_term_hits(search_terms, all_text)
    # Require higher overlap (4+ words) for criteria to avoid false positives
    # from generic words like "managed", "service", "monitoring"
    criteria_text_hits = 0
    for cr in criteria:
        cr_words = set(re.findall(r"\b[a-z]{5,}\b", cr.lower()))  # 5+ char words only
        all_words = set(re.findall(r"\b[a-z]{5,}\b", all_text))
        overlap = cr_words & all_words
        # Exclude very common words that inflate scores
        common = {"service", "services", "managed", "security", "monitoring",
                  "operations", "continuous", "platform", "solutions", "analyst",
                  "teams", "coverage", "defined", "response", "detection"}
        meaningful_overlap = overlap - common
        if len(meaningful_overlap) >= 2 or (len(overlap) >= 4 and len(meaningful_overlap) >= 1):
            criteria_text_hits += 1

    # Maturity level determination — search terms are the PRIMARY signal
    # since they're specifically designed for each SVC sub-pillar
    if search_term_hits >= 5 and criteria_text_hits >= 3:
        score = 4.5
    elif search_term_hits >= 4 and criteria_text_hits >= 2:
        score = 4.0
    elif search_term_hits >= 3 and criteria_text_hits >= 1:
        score = 3.5
    elif search_term_hits >= 2:
        score = 3.0
    elif search_term_hits >= 1 and criteria_text_hits >= 1:
        score = 2.5
    elif search_term_hits >= 1:
        score = 2.0
    elif criteria_text_hits >= 2:
        score = 2.0
    elif _count_term_hits(GENERIC_SVC_TERMS, all_text) >= 5:
        score = 1.5
    elif top_hits:
        score = 1.0
    else:
        score = 0.0

    # Cap at 4.75 since market-leading requires deep validation
    score = min(score, 4.75)

    evidence = {
        "source_urls": list({h["url"] for h in top_hits}),
        "excerpts": top_hits,
        "search_term_hits": search_term_hits,
        "criteria_text_hits": criteria_text_hits,
        "score": round(score, 2),
        "notes": f"SVC evidence: {len(top_hits)} excerpts, {search_term_hits} term hits, {criteria_text_hits} criteria hits.",
    }

    return round(score, 2), evidence


# ─────────────────────────────────────────────────────────────
# Pricing dimension scoring
# ─────────────────────────────────────────────────────────────

def score_pricing_dimension(
    dim_id: str,
    schema: Dict,
    pages_text: List[Tuple[str, str]],
) -> Tuple[float, Dict[str, Any]]:
    """Extract evidence and score a pricing dimension."""
    dim_info = get_pricing_dim_info(schema, dim_id)
    search_terms = PRICING_SEARCH_TERMS.get(dim_id, [])
    criteria = dim_info.get("what_to_evaluate", [])

    all_text = " ".join(t for _, t in pages_text).lower()
    hits = []

    for url, text in pages_text:
        candidates = _candidate_snippets(text)
        for sent in candidates:
            s_lower = sent.lower()
            matched = []

            # Check search terms
            for term in search_terms:
                if _term_in_text(term, s_lower):
                    matched.append(term)

            # Check criteria phrases
            for cr in criteria:
                cr_words = set(re.findall(r"\b[a-z]{4,}\b", cr.lower()))
                sent_words = set(re.findall(r"\b[a-z]{4,}\b", s_lower))
                overlap = len(cr_words & sent_words)
                if overlap >= 3:
                    matched.append(f"criteria:{cr[:50]}")

            # Check generic pricing terms
            generic_hits = sum(1 for t in GENERIC_PRICING_TERMS if _term_in_text(t, s_lower))

            if not matched and generic_hits < 2:
                continue

            # Pricing-specific signals
            pricing_bonus = 0
            if re.search(r"\$[\d,.]+", s_lower):
                pricing_bonus += 3
                matched.append("contains_price")
            if re.search(r"\d+%", s_lower):
                pricing_bonus += 1
                matched.append("contains_percentage")
            if re.search(r"per[- ](?:endpoint|seat|user|device|gb|tb|asset|agent)", s_lower):
                pricing_bonus += 2
                matched.append("per_unit_pricing")
            if re.search(r"(?:annual|monthly|quarterly)\s+(?:fee|cost|rate|subscription)", s_lower):
                pricing_bonus += 2
                matched.append("recurring_pricing")

            relevance = len([m for m in matched if m.startswith("criteria:")]) * 3 + \
                        len([m for m in matched if not m.startswith("criteria:") and not m.startswith("contains") and m != "per_unit_pricing" and m != "recurring_pricing"]) * 2 + \
                        generic_hits + pricing_bonus

            hits.append({
                "url": url,
                "excerpt": _shorten(sent),
                "matched_terms": matched[:8],
                "relevance_score": relevance,
            })

    # Sort and take top N
    hits.sort(key=lambda h: h["relevance_score"], reverse=True)
    top_hits = hits[:MAX_EXCERPTS]

    # Compute score
    search_term_hits = _count_term_hits(search_terms, all_text)
    criteria_text_hits = 0
    for cr in criteria:
        cr_words = set(re.findall(r"\b[a-z]{4,}\b", cr.lower()))
        all_words = set(re.findall(r"\b[a-z]{4,}\b", all_text))
        if len(cr_words & all_words) >= 3:
            criteria_text_hits += 1

    # Has pricing signals?
    has_prices = bool(re.search(r"\$[\d,.]+", all_text))
    has_per_unit = bool(re.search(r"per[- ](?:endpoint|seat|user|device|gb|tb|asset|agent)", all_text))

    if criteria_text_hits >= 4 and search_term_hits >= 6:
        score = 4.5
    elif criteria_text_hits >= 3 and search_term_hits >= 4:
        score = 4.0
    elif criteria_text_hits >= 2 and search_term_hits >= 3:
        score = 3.5
    elif criteria_text_hits >= 2 or search_term_hits >= 3:
        score = 3.0
    elif criteria_text_hits >= 1 or search_term_hits >= 2:
        score = 2.5
    elif search_term_hits >= 1:
        score = 2.0
    elif _count_term_hits(GENERIC_PRICING_TERMS, all_text) >= 3:
        score = 1.5
    elif top_hits:
        score = 1.0
    else:
        score = 0.0

    # Pricing signal bonuses
    if has_prices and score < 4.0:
        score = min(score + 0.5, 4.0)
    if has_per_unit and score < 3.5:
        score = min(score + 0.25, 3.5)

    score = min(score, 4.75)

    # Assess criteria individually
    criteria_results = []
    combined_text = all_text
    for cr in criteria:
        cr_words = set(re.findall(r"\b[a-z]{4,}\b", cr.lower()))
        combined_words = set(re.findall(r"\b[a-z]{4,}\b", combined_text))
        overlap = len(cr_words & combined_words)
        ratio = overlap / max(len(cr_words), 1)
        if ratio >= 0.3:
            status = "met"
        elif ratio >= 0.15:
            status = "partial"
        else:
            status = "unmet"
        criteria_results.append({"criterion": cr, "status": status})

    evidence = {
        "source_urls": list({h["url"] for h in top_hits}),
        "excerpts": top_hits,
        "search_term_hits": search_term_hits,
        "criteria_text_hits": criteria_text_hits,
        "criteria_results": criteria_results,
        "has_prices": has_prices,
        "has_per_unit": has_per_unit,
        "score": round(score, 2),
        "notes": f"Pricing evidence: {len(top_hits)} excerpts, {search_term_hits} term hits, {criteria_text_hits} criteria hits.",
    }

    return round(score, 2), evidence


# ─────────────────────────────────────────────────────────────
# Outcome maturity rating
# ─────────────────────────────────────────────────────────────

def compute_outcome_maturity(pricing_scores: Dict[str, float]) -> Tuple[float, str]:
    """Compute overall outcome maturity rating from dimension scores."""
    out_score = pricing_scores.get("PRC-OUT", 0.0)
    com_score = pricing_scores.get("PRC-COM", 0.0)
    suc_score = pricing_scores.get("PRC-SUC", 0.0)
    avg_all = sum(pricing_scores.values()) / max(len(pricing_scores), 1)

    # Weighted blend emphasizing outcome dimensions
    maturity = 0.35 * out_score + 0.25 * com_score + 0.20 * suc_score + 0.20 * avg_all
    maturity = round(min(maturity, 5.0), 2)

    if maturity >= 4.0:
        label = "Outcome-Validated"
    elif maturity >= 3.0:
        label = "Outcome-Linked"
    elif maturity >= 2.0:
        label = "Outcome-Aware"
    elif maturity >= 1.0:
        label = "Input-Only"
    else:
        label = "No Evidence"

    return maturity, label


# ─────────────────────────────────────────────────────────────
# Rationale builder
# ─────────────────────────────────────────────────────────────

def build_svc_rationale(sid: str, schema: Dict, score: float, evidence: Dict) -> str:
    info = get_subpillar_info(schema, sid)
    name = info.get("name", sid)
    excerpts = evidence.get("excerpts", [])

    parts = [f"{sid} - {name}. Score: {score:.2f}/5."]

    if score >= 4.0:
        parts.append("Advanced services maturity with strong evidence.")
    elif score >= 3.0:
        parts.append("Demonstrated services capability with documented offerings.")
    elif score >= 2.0:
        parts.append("Basic services mentioned but limited evidence of operational maturity.")
    elif score >= 1.0:
        parts.append("Minimal services evidence; primarily technology-focused.")
    else:
        parts.append("No evidence of services capability for this domain.")

    if excerpts:
        first = excerpts[0].get("excerpt", "")
        parts.append(f'Evidence: "{_shorten(first, 180)}".')
        if len(excerpts) > 1:
            second = excerpts[1].get("excerpt", "")
            parts.append(f'Also: "{_shorten(second, 120)}".')

    return " ".join(parts)


def build_pricing_rationale(dim_id: str, schema: Dict, score: float, evidence: Dict) -> str:
    dim_info = get_pricing_dim_info(schema, dim_id)
    name = dim_info.get("name", dim_id)
    excerpts = evidence.get("excerpts", [])

    parts = [f"{dim_id} - {name}. Score: {score:.2f}/5."]

    if score >= 4.0:
        parts.append("Strong pricing transparency with specific evidence.")
    elif score >= 3.0:
        parts.append("Demonstrated pricing structure with some detail.")
    elif score >= 2.0:
        parts.append("Basic pricing information available but limited detail.")
    elif score >= 1.0:
        parts.append("Minimal pricing transparency; mostly marketing claims.")
    else:
        parts.append("No pricing information found publicly.")

    if evidence.get("has_prices"):
        parts.append("Specific pricing figures found.")
    if evidence.get("has_per_unit"):
        parts.append("Per-unit pricing model identified.")

    if excerpts:
        first = excerpts[0].get("excerpt", "")
        parts.append(f'Evidence: "{_shorten(first, 180)}".')

    return " ".join(parts)


# ─────────────────────────────────────────────────────────────
# Main vendor processing
# ─────────────────────────────────────────────────────────────

def process_vendor(
    vendor: Dict[str, Any],
    schema: Dict[str, Any],
    *,
    force_fetch: bool = False,
    lineage_sink=None,
) -> Dict[str, Any]:
    """Process a single vendor for SVC + pricing evidence."""
    name = vendor.get("vendor", "Unknown")
    print(f"\n{'='*60}")
    print(f"Processing: {name}")
    print(f"{'='*60}")

    # Discover URLs
    existing_urls, new_urls = discover_vendor_urls(vendor)
    print(f"  Existing cached URLs: {len(existing_urls)}")
    print(f"  New SVC/pricing URLs: {len(new_urls)}")

    # Load existing cached pages first (no fetch needed)
    pages = []
    cached_count = 0
    fetched_count = 0

    for url in existing_urls:
        cp = _cache_path(url)
        if cp.exists():
            try:
                cached = json.loads(cp.read_text(encoding="utf-8"))
                if lineage_sink is not None:
                    vendor_slug = re.sub(
                        r"[^a-z0-9]+",
                        "-",
                        str(name).lower(),
                    ).strip("-")
                    lineage_sink.capture_cache_file(
                        cp,
                        vendor_id=f"vendor:{vendor_slug or 'unknown'}",
                    )
                if cached.get("ok") and cached.get("text"):
                    pages.append((url, cached["text"]))
                    cached_count += 1
            except Exception:
                pass

    print(f"  Loaded {cached_count} pages from existing cache")

    # Fetch new service/pricing URLs
    for url in new_urls:
        rec = fetch_page(url, force=force_fetch)
        if lineage_sink is not None:
            vendor_slug = re.sub(
                r"[^a-z0-9]+",
                "-",
                str(name).lower(),
            ).strip("-")
            lineage_sink.capture(
                vendor_id=f"vendor:{vendor_slug or 'unknown'}",
                record=rec,
                cache_path=_cache_path(url),
                retrieval_method=rec.get("render_engine"),
            )
        if rec.get("ok") and rec.get("text"):
            pages.append((url, rec["text"]))
            fetched_count += 1
        time.sleep(FETCH_SLEEP + random.uniform(0.3, 1.5))

    print(f"  Fetched {fetched_count} new pages ({len(new_urls) - fetched_count} failed)")
    print(f"  Total pages for analysis: {len(pages)}")

    if not pages:
        print(f"  WARNING: No pages available for {name}")

    # ── Score services sub-pillars ──
    svc_scores = {}
    svc_evidence = {}
    svc_rationales = {}

    for sid in SVC_SUBPILLARS:
        score, ev = score_svc_subpillar(sid, schema, pages)
        svc_scores[sid] = score
        svc_evidence[sid] = ev
        svc_rationales[sid] = build_svc_rationale(sid, schema, score, ev)
        print(f"  {sid}: {score:.2f}/5 ({ev.get('search_term_hits', 0)} term hits, {ev.get('criteria_text_hits', 0)} criteria)")

    # ── Score pricing dimensions ──
    pricing_scores = {}
    pricing_evidence = {}
    pricing_rationales = {}

    for dim_id in PRICING_DIMS:
        score, ev = score_pricing_dimension(dim_id, schema, pages)
        pricing_scores[dim_id] = score
        pricing_evidence[dim_id] = ev
        pricing_rationales[dim_id] = build_pricing_rationale(dim_id, schema, score, ev)
        print(f"  {dim_id}: {score:.2f}/5 ({ev.get('search_term_hits', 0)} term hits)")

    # ── Outcome maturity ──
    outcome_rating, outcome_label = compute_outcome_maturity(pricing_scores)
    print(f"  Outcome maturity: {outcome_rating:.2f} ({outcome_label})")

    # ── Services maturity level classification ──
    avg_svc = sum(svc_scores.values()) / max(len(svc_scores), 1)
    if avg_svc >= 4.0:
        maturity_level = "ai_augmented"
    elif avg_svc >= 3.0:
        maturity_level = "managed"
    elif avg_svc >= 2.0:
        maturity_level = "consultative"
    else:
        maturity_level = "implementation_only"

    # ── Build enriched vendor record ──
    enriched = dict(vendor)

    # Add SVC scores to existing sub_pillar_scores_current
    existing_scores = enriched.get("sub_pillar_scores_current", {})
    existing_scores.update(svc_scores)
    enriched["sub_pillar_scores_current"] = existing_scores

    # Add SVC evidence to existing sub_pillar_evidence
    existing_evidence = enriched.get("sub_pillar_evidence", {})
    existing_evidence.update(svc_evidence)
    enriched["sub_pillar_evidence"] = existing_evidence

    # Add SVC rationales
    existing_rationales = enriched.get("sub_pillar_rationale_v2_consolidated", {})
    existing_rationales.update(svc_rationales)
    enriched["sub_pillar_rationale_v2_consolidated"] = existing_rationales

    # Update pillar scores (add SVC pillar, update existing pillars)
    pillar_scores = enriched.get("pillar_scores", {})
    # SVC pillar = avg of SVC-01..04
    svc_avg = sum(svc_scores.get(f"SVC-{i:02d}", 0) for i in range(1, 5)) / 4
    pillar_scores["SVC"] = round(svc_avg, 2)
    # Update existing pillar scores to include -05 sub-pillars
    for pillar in ["EXM", "AMT", "ADR", "PPM"]:
        sp_ids = [f"{pillar}-{i:02d}" for i in range(1, 6)]  # now includes -05
        vals = [existing_scores.get(sp, 0.0) for sp in sp_ids]
        pillar_scores[pillar] = round(sum(vals) / len(vals), 2)
    enriched["pillar_scores"] = pillar_scores

    # Add pricing data
    enriched["pricing_dimension_scores"] = pricing_scores
    enriched["pricing_evidence"] = pricing_evidence
    enriched["pricing_rationales"] = pricing_rationales
    enriched["outcome_maturity_rating"] = outcome_rating
    enriched["outcome_maturity_label"] = outcome_label

    # Update services maturity level
    enriched["services_maturity_level"] = maturity_level

    # Update coverage
    covered = [sp for sp, s in existing_scores.items() if s >= 2.0]
    enriched["capability_coverage"] = sorted(covered)
    enriched["capability_coverage_count"] = len(covered)

    # Coverage grade (out of 24 now)
    n = len(covered)
    if n >= 21:
        grade = "A"
    elif n >= 16:
        grade = "B"
    elif n >= 10:
        grade = "C"
    elif n >= 5:
        grade = "D"
    else:
        grade = "F"
    enriched["coverage_grade"] = grade

    # Research metadata
    enriched["svc_pricing_research"] = {
        "researched_at": datetime.now(timezone.utc).isoformat(),
        "cached_pages_used": cached_count,
        "new_pages_fetched": fetched_count,
        "total_pages_analyzed": len(pages),
        "svc_subpillars_scored": len(SVC_SUBPILLARS),
        "pricing_dimensions_scored": len(PRICING_DIMS),
    }

    return enriched


# ─────────────────────────────────────────────────────────────
# Checkpoint management
# ─────────────────────────────────────────────────────────────

def _progress_path() -> Path:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    return CHECKPOINT_DIR / "svc_pricing_progress.json"


def _load_progress() -> Dict[str, Any]:
    pp = _progress_path()
    if pp.exists():
        try:
            return json.loads(pp.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"completed_batches": [], "completed_vendors": []}


def _save_progress(progress: Dict[str, Any]):
    _progress_path().write_text(
        json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _batch_path(batch_num: int) -> Path:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    return BATCH_DIR / f"svc_batch_{batch_num:02d}.json"


def _save_batch(batch_num: int, vendors: List[Dict]):
    path = _batch_path(batch_num)
    path.write_text(
        json.dumps(vendors, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  Saved batch {batch_num} ({len(vendors)} vendors) to {path.name}")


# ─────────────────────────────────────────────────────────────
# Merge batches
# ─────────────────────────────────────────────────────────────

def merge_batches() -> int:
    """Merge all SVC/pricing batch outputs into the final vendor file."""
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    batch_files = sorted(BATCH_DIR.glob("svc_batch_*.json"))
    if not batch_files:
        print("No batch files found.")
        return 1

    scored = {}
    for bf in batch_files:
        try:
            data = json.loads(bf.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for v in data:
                    name = v.get("vendor", "")
                    if name:
                        scored[name] = v
        except Exception as e:
            print(f"  Warning: {bf.name}: {e}")

    print(f"Loaded {len(scored)} vendors from {len(batch_files)} batch files")

    # Load original vendor data
    vendors = load_vendors()
    print(f"Original vendor count: {len(vendors)}")

    # Merge
    final = []
    for v in vendors:
        name = v.get("vendor", "")
        if name in scored:
            final.append(scored[name])
        else:
            final.append(v)

    # Write output
    OUTPUT_FILE.write_text(
        json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nWrote {len(final)} vendors to {OUTPUT_FILE.name}")

    # Summary stats
    svc_scored = sum(1 for v in final if "pricing_dimension_scores" in v)
    print(f"  Vendors with SVC/pricing data: {svc_scored}/{len(final)}")

    if svc_scored > 0:
        # Average scores across dimensions
        for dim in SVC_SUBPILLARS + PRICING_DIMS:
            vals = []
            for v in final:
                s = v.get("sub_pillar_scores_current", {}).get(dim) or \
                    v.get("pricing_dimension_scores", {}).get(dim)
                if s is not None:
                    vals.append(s)
            if vals:
                avg = sum(vals) / len(vals)
                print(f"  {dim} avg: {avg:.2f}")

    return 0


# ─────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PreCyber SVC + Pricing Research")
    parser.add_argument("--max-vendors", type=int, default=0,
                        help="Max vendors to process (0=all)")
    parser.add_argument("--batch-size", type=int, default=5,
                        help="Vendors per batch")
    parser.add_argument("--batch-pause", type=float, default=10.0,
                        help="Seconds between batches")
    parser.add_argument("--force-fetch", action="store_true",
                        help="Re-fetch cached pages")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from last checkpoint")
    parser.add_argument("--merge-only", action="store_true",
                        help="Just merge batch outputs")
    parser.add_argument(
        "--couchdb-project-id",
        help="Research project ID for append-only CouchDB source lineage",
    )
    parser.add_argument(
        "--couchdb-run-id",
        help="Research run ID for append-only CouchDB source lineage",
    )
    args = parser.parse_args()

    lineage_sink = None
    checkpoint_store = None
    if bool(args.couchdb_project_id) != bool(args.couchdb_run_id):
        parser.error(
            "--couchdb-project-id and --couchdb-run-id must be supplied together"
        )
    if args.couchdb_project_id:
        from gartner_app.research.checkpoints import ResearchCheckpointStore
        from gartner_app.research.lineage import LegacyCacheLineageSink

        lineage_sink = LegacyCacheLineageSink.from_settings(
            project_id=args.couchdb_project_id,
            run_id=args.couchdb_run_id,
            actor="worker:research_precyber_svc_pricing",
        )
        checkpoint_store = ResearchCheckpointStore.from_settings(
            project_id=args.couchdb_project_id,
            run_id=args.couchdb_run_id,
            stage="svc_pricing",
            actor="worker:research_precyber_svc_pricing",
        )

    print("=" * 70)
    print("PreCyber Services + Pricing Research Pipeline")
    print("=" * 70)

    if args.merge_only:
        return merge_batches()

    # Load schema and vendors
    schema = load_schema()
    vendors = load_vendors()
    print(f"Loaded {len(vendors)} vendors from {INPUT_FILE.name}")
    print(f"Schema: {SCHEMA_FILE.name}")
    print(f"Evaluating: {len(SVC_SUBPILLARS)} SVC sub-pillars + {len(PRICING_DIMS)} pricing dimensions")

    # Count existing cached pages
    if CACHE_DIR.exists():
        cached_count = len(list(CACHE_DIR.glob("*.json")))
        print(f"Existing cached pages: {cached_count}")
    else:
        print("No existing cache found — will fetch all pages")

    # Limit vendors if requested
    if args.max_vendors > 0:
        vendors = vendors[:args.max_vendors]
        print(f"Limited to {len(vendors)} vendors")

    # Resume support
    if args.resume:
        progress = (
            checkpoint_store.load()
            if checkpoint_store is not None
            else _load_progress()
        )
    else:
        progress = {"completed_batches": [], "completed_vendors": []}
    completed_names = set(progress.get("completed_vendors", []))
    if completed_names:
        print(f"Resuming: {len(completed_names)} vendors already completed")

    # Batch processing
    remaining = [v for v in vendors if v.get("vendor", "") not in completed_names]
    total_batches = (len(remaining) + args.batch_size - 1) // args.batch_size
    start_batch = len(progress.get("completed_batches", []))

    print(f"\nProcessing {len(remaining)} vendors in {total_batches} batches of {args.batch_size}")
    print(f"Starting from batch {start_batch + 1}")
    print()

    for batch_idx in range(total_batches):
        batch_num = start_batch + batch_idx + 1
        batch_start = batch_idx * args.batch_size
        batch_end = min(batch_start + args.batch_size, len(remaining))
        batch_vendors = remaining[batch_start:batch_end]

        print(f"\n{'#'*60}")
        print(f"BATCH {batch_num}/{start_batch + total_batches}: {len(batch_vendors)} vendors")
        print(f"{'#'*60}")

        batch_results = []
        for v in batch_vendors:
            try:
                enriched = process_vendor(
                    v,
                    schema,
                    force_fetch=args.force_fetch,
                    lineage_sink=lineage_sink,
                )
                batch_results.append(enriched)
                progress["completed_vendors"].append(v.get("vendor", ""))
            except Exception as e:
                print(f"  ERROR processing {v.get('vendor', '?')}: {e}")
                batch_results.append(v)  # keep original on error

        _save_batch(batch_num, batch_results)
        progress["completed_batches"].append(batch_num)
        if checkpoint_store is not None:
            checkpoint_store.save(progress)
        else:
            _save_progress(progress)

        if batch_idx < total_batches - 1:
            print(f"\n  Pausing {args.batch_pause}s before next batch...")
            time.sleep(args.batch_pause)

    # Final merge
    print(f"\n{'='*60}")
    print("Merging all batches into final output...")
    print(f"{'='*60}")
    merge_batches()

    print("\nDone!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
