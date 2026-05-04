"""
research_v3_ai_scoring.py — AI-Focused DFIR Vendor Research Pipeline (v3)

Forked from research_v2_vendor_scoring.py.  Key differences:
  - Uses schema5-0_ai.json: ai_evaluation_criteria per sub-pillar (100 criteria)
  - Sources include 3rd-party publications, analyst reports, LinkedIn, media
  - AI-weighted scoring: AI specificity is the PRIMARY scoring dimension
  - 6-lot parallel support (--lot A..F) with staggered sleep offsets
  - Output keys: sub_pillar_scores_ai_researched, pillar_scores_ai_researched
  - Merge step: reads full dataset, adds AI layer, writes Vendor 6-0 AI Researched.json

Usage:
  python research_v3_ai_scoring.py                              # run all vendors
  python research_v3_ai_scoring.py --lot A                      # run lot A only (~23 vendors)
  python research_v3_ai_scoring.py --merge-lots                 # merge lot outputs → final
  python research_v3_ai_scoring.py --max-vendors 5 --skip-merge # test 5 vendors
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
# Configuration
# ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent

DEFAULT_FULL_FILE   = ROOT / "Vendor 5-2 Researched.json"
DEFAULT_SCHEMA_FILE = ROOT / "schema5-0_ai.json"
DEFAULT_OUTPUT_FILE = ROOT / "Vendor 6-0 AI Researched.json"
CACHE_DIR           = ROOT / "research" / "cache" / "pages_v3"
CHECKPOINT_DIR      = ROOT / "research" / "v3_checkpoints"
LOT_OUTPUT_DIR      = ROOT / "research" / "v3_lots"

URL_RE = re.compile(r"https?://[^\s)\]\}\">,]+")

PILLARS = ["PLA", "INV", "REM", "PMG", "LAW"]
SUBPILLAR_IDS = [f"{p}-{i:02d}" for p in PILLARS for i in range(1, 5)]

# ─────────────────────────────────────────────────────────────────────
# Lot definitions (6 lots of ~23 vendors, sorted alphabetically)
# Vendors are assigned to lots by first letter.
# ─────────────────────────────────────────────────────────────────────

LOT_DEFINITIONS = {
    "A": lambda name: name[0].upper() <= "B",
    "B": lambda name: "C" <= name[0].upper() <= "D",
    "C": lambda name: "E" <= name[0].upper() <= "H",
    "D": lambda name: "I" <= name[0].upper() <= "N",
    "E": lambda name: "O" <= name[0].upper() <= "R",
    "F": lambda name: "S" <= name[0].upper() <= "Z",
}

LOT_SLEEP_OFFSETS = {"A": 0, "B": 0.5, "C": 1.0, "D": 1.5, "E": 2.0, "F": 2.5}

# ─────────────────────────────────────────────────────────────────────
# Vendor-specific URLs — combines vendor own URLs + 3rd-party sources
# Curated to provide equal AI-evidence opportunity per vendor.
# ─────────────────────────────────────────────────────────────────────

VENDOR_URLS: Dict[str, List[str]] = {
    "7AI": [
        "https://www.7ai.com/",
        "https://www.7ai.com/platform",
    ],
    "Accenture": [
        "https://www.accenture.com/us-en/services/security-index",
        "https://www.accenture.com/us-en/services/security/cyber-resilience",
    ],
    "Aon (Stroz Friedberg)": [
        "https://www.aon.com/en/capabilities/cyber-resilience",
        "https://www.strozfriedberg.com/",
    ],
    "Arctic Wolf": [
        "https://arcticwolf.com/solutions/incident-response/",
        "https://arcticwolf.com/platform/",
    ],
    "BAE Systems": [
        "https://www.baesystems.com/en/digital-intelligence/cyber-security",
        "https://www.baesystems.com/en/cybersecurity/incident-response",
    ],
    "Bitdefender": [
        "https://www.bitdefender.com/business/enterprise-products/managed-detection-response.html",
        "https://www.bitdefender.com/business/solutions/incident-response.html",
    ],
    "Blackpanda": [
        "https://www.blackpanda.com/",
        "https://www.blackpanda.com/incident-response/",
    ],
    "BlueVoyant": [
        "https://www.bluevoyant.com/platform",
        "https://www.bluevoyant.com/services/incident-response",
    ],
    "Booz Allen Hamilton": [
        "https://www.boozallen.com/expertise/cybersecurity.html",
        "https://www.boozallen.com/expertise/cybersecurity/incident-response.html",
    ],
    "Bridewell": [
        "https://www.bridewell.com/services/cyber-security/incident-response",
        "https://www.bridewell.com/managed-security",
    ],
    "BT Cyber": [
        "https://business.bt.com/products/security/",
        "https://business.bt.com/products/managed-services/managed-security/",
    ],
    "Capgemini": [
        "https://www.capgemini.com/services/cybersecurity/",
        "https://www.capgemini.com/solutions/cybersecurity-services/managed-security-operations/",
    ],
    "Cisco": [
        "https://talosintelligence.com/incident_response",
        "https://www.cisco.com/site/us/en/products/security/incident-response-services/index.html",
    ],
    "Control Risks": [
        "https://www.controlrisks.com/our-services/cyber-risk",
        "https://www.controlrisks.com/our-services/cyber-risk/incident-response",
    ],
    "CPX": [
        "https://www.cpx.net/services/cyber-resilience-services/incident-forensics-capability/",
        "https://www.cpx.net/services/cyber-resilience-services/managed-detection-and-response-mdr/",
    ],
    "CrowdStrike": [
        "https://www.crowdstrike.com/services/incident-response/",
        "https://www.crowdstrike.com/platform/charlotte-ai/",
        "https://www.crowdstrike.com/blog/tag/ai/",
    ],
    "CyberCX": [
        "https://www.cybercx.com.au/solutions/digital-forensics-and-incident-response/",
        "https://www.cybercx.com.au/incident-response/",
    ],
    "Cyberegate": [
        "https://www.cyberegate.com/",
        "https://www.cyberegate.com/services/",
    ],
    "CyberLink": [
        "https://www.cyberlink-sa.com/",
        "https://www.cyberlink-sa.com/services/",
    ],
    "CyberSOC Africa": [
        "https://www.cybersocafrica.com/",
        "https://www.cybersocafrica.com/services/",
    ],
    "Deloitte": [
        "https://www.deloitte.com/global/en/services/risk-advisory/perspectives/cyber-security-incident-response.html",
        "https://www.deloitte.com/global/en/services/risk-advisory/perspectives/ai-cyber-security.html",
    ],
    "DGL Group": [
        "https://www.dglgroup.com/",
        "https://www.dglgroup.com/services/",
    ],
    "Digital Encode": [
        "https://www.digitalencode.net/",
        "https://www.digitalencode.net/our-services/",
    ],
    "DTS Solution": [
        "https://www.dtssolution.com/",
        "https://dts-solution.com/managed-security-services/",
    ],
    "e& enterprise (Help AG)": [
        "https://www.helpag.com/managed-security-service-provider/",
        "https://www.helpag.com/cybersecurity-assessments/",
    ],
    "Expel": [
        "https://www.expel.com/services/",
        "https://www.expel.com/platform/",
    ],
    "EY": [
        "https://www.ey.com/en_gl/cybersecurity",
        "https://www.ey.com/en_gl/consulting/cybersecurity-incident-response",
    ],
    "FireEye / Trellix": [
        "https://www.trellix.com/products/managed-detection-response/",
        "https://www.trellix.com/solutions/incident-response/",
    ],
    "FTI Consulting": [
        "https://www.fticonsulting.com/expertise/cybersecurity",
        "https://www.fticonsulting.com/expertise/digital-forensics",
    ],
    "Google Cloud (Mandiant)": [
        "https://www.mandiant.com/advantage/incident-response-services",
        "https://www.mandiant.com/advantage/threat-intelligence",
        "https://cloud.google.com/security/ai",
    ],
    "Group-IB": [
        "https://www.group-ib.com/services/incident-response/",
        "https://www.group-ib.com/services/digital-forensics/",
    ],
    "HCLTech": [
        "https://www.hcltech.com/cybersecurity",
        "https://www.hcltech.com/cybersecurity/managed-security-services",
    ],
    "Help AG": [
        "https://www.helpag.com/managed-security-service-provider/",
        "https://www.helpag.com/offensive-cybersecurity/",
    ],
    "IBM (X-Force)": [
        "https://www.ibm.com/security/services/incident-response-services",
        "https://www.ibm.com/x-force",
        "https://www.ibm.com/security/ai",
    ],
    "Infosys": [
        "https://www.infosys.com/services/cyber-security.html",
        "https://www.infosys.com/services/cyber-security/offerings.html",
    ],
    "Kela": [
        "https://www.kela.com/",
        "https://www.kela.com/platform",
    ],
    "Kivu": [
        "https://www.quorumcyber.com/kivu-becomes-quorum-cyber/",
        "https://kivuconsulting.com/incident-response/",
    ],
    "KPMG": [
        "https://kpmg.com/xx/en/home/services/advisory/risk-consulting/cyber-security.html",
        "https://kpmg.com/xx/en/home/services/advisory/risk-consulting/cyber-security/incident-response.html",
    ],
    "LGMS": [
        "https://www.lgms.global/",
        "https://www.lgms.global/services/",
    ],
    "Litt": [
        "https://www.littsolutions.com/",
        "https://litt.ai/",
    ],
    "Microsoft (DART)": [
        "https://www.microsoft.com/en-us/security/business/security-experts",
        "https://learn.microsoft.com/en-us/security/operations/incident-response-overview",
        "https://www.microsoft.com/en-us/security/business/ai-machine-learning",
    ],
    "Mitiga": [
        "https://www.mitiga.io/platform",
        "https://www.mitiga.io/services",
    ],
    "mnemonic": [
        "https://www.mnemonic.io/solutions/incident-response/",
        "https://www.mnemonic.io/solutions/managed-detection-and-response/",
    ],
    "Nozomi Networks": [
        "https://www.nozominetworks.com/platform",
        "https://www.nozominetworks.com/solutions/threat-detection-and-response",
    ],
    "NTT": [
        "https://www.global.ntt/services/managed-security-services",
        "https://www.global.ntt/services/cybersecurity",
    ],
    "Orange Cyberdefense": [
        "https://www.orangecyberdefense.com/global/offering/managed-services/incident-response",
        "https://www.orangecyberdefense.com/global/offering",
    ],
    "P0 Security": [
        "https://www.p0.dev/",
        "https://www.p0.dev/platform",
    ],
    "Palo Alto Networks (Unit 42)": [
        "https://unit42.paloaltonetworks.com/",
        "https://unit42.paloaltonetworks.com/incident-response/",
        "https://www.paloaltonetworks.com/cortex/cortex-xsiam",
    ],
    "Pondurance": [
        "https://www.pondurance.com/incident-response/",
        "https://www.pondurance.com/managed-detection-and-response/",
    ],
    "PwC": [
        "https://www.pwc.com/gx/en/issues/cybersecurity.html",
        "https://www.pwc.com/gx/en/services/forensics.html",
    ],
    "Quorum Cyber": [
        "https://www.quorumcyber.com/services/incident-response/",
        "https://www.quorumcyber.com/emergency-help/",
    ],
    "Rapid7": [
        "https://www.rapid7.com/services/incident-response/",
        "https://www.rapid7.com/products/insightidr/",
    ],
    "Rubrik": [
        "https://www.rubrik.com/",
        "https://www.rubrik.com/solutions/cyber-recovery",
    ],
    "S-RM": [
        "https://www.s-rminform.com/cyber-incident-response",
        "https://www.s-rminform.com/digital-forensics",
    ],
    "Secureworks": [
        "https://www.secureworks.com/services/incident-response",
        "https://www.secureworks.com/products/taegis",
    ],
    "SentinelOne": [
        "https://www.sentinelone.com/platform/",
        "https://www.sentinelone.com/platform/purple-ai/",
    ],
    "Serianu Limited": [
        "https://www.serianu.com/",
        "https://www.serianu.com/about-us.html",
    ],
    "Sophos": [
        "https://www.sophos.com/en-us/products/managed-detection-and-response",
        "https://www.sophos.com/en-us/products/ai",
    ],
    "Stellar Cyber": [
        "https://www.stellarcyber.ai/platform/",
        "https://www.stellarcyber.ai/uc/incidentresponse/",
    ],
    "Sygnia": [
        "https://www.sygnia.co/incident-response/",
        "https://www.sygnia.co/velocity-tdir-platform/",
    ],
    "Tempest": [
        "https://www.tempest.com.br/",
        "https://www.tempest.com.br/servicos/",
    ],
    "Tenzai": [
        "https://tenzai.co/",
        "https://tenzai.ai/",
    ],
    "Total Assure": [
        "https://totalassure.co.uk/",
        "https://totalassure.co.uk/services/",
    ],
    "TrustedSEC": [
        "https://www.trustedsec.com/services/incident-response/",
        "https://www.trustedsec.com/services/",
    ],
    "Trustwave": [
        "https://www.levelblue.com/services/incident-readiness-and-response/",
        "https://www.trustwave.com/en-us/services/consulting-and-professional-services/incident-response/",
    ],
    "Wolfpack InfoRisk": [
        "https://wolfpackrisk.com/",
        "https://wolfpackrisk.com/company-risk-management/",
    ],
}

# 3rd-party sources queried for ALL vendors (appended per vendor name)
THIRD_PARTY_SOURCES = [
    "https://www.darkreading.com/search?q={vendor}+AI+incident+response",
    "https://www.scmagazine.com/?s={vendor}+AI",
]

# ─────────────────────────────────────────────────────────────────────
# AI-focused search terms (loaded from schema at runtime)
# These augment the sub-pillar ai_evaluation_criteria from schema5-0.
# ─────────────────────────────────────────────────────────────────────

AI_PRIMARY_TERMS = [
    "ai agent", "ai agents", "agentic", "agentic ai", "llm", "large language model",
    "machine learning", "ml model", "deep learning", "neural network",
    "natural language processing", "nlp", "generative ai", "gen ai",
    "automated reasoning", "autonomous", "orchestration", "ai-powered",
    "ai-driven", "ai-assisted", "ai-augmented", "predictive analytics",
    "anomaly detection", "behavioral analytics", "threat intelligence ai",
    "copilot", "ai copilot",
]

AI_EXCLUSION_TERMS = [
    "rule-based only", "regex only", "no ai", "manual process",
    "human-only", "script-based",
]

# ─────────────────────────────────────────────────────────────────────
# User-Agents & HTML Parser (same as v2)
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
# Cache management (separate cache from v2 to avoid conflicts)
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
# Schema-driven term extraction
# ─────────────────────────────────────────────────────────────────────

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "case",
    "could", "for", "from", "has", "have", "how", "if", "in", "into",
    "is", "it", "its", "may", "of", "on", "or", "our", "post",
    "should", "the", "their", "they", "this", "that", "these", "those",
    "to", "up", "use", "used", "using", "via", "was", "were", "will",
    "with", "without", "your", "you", "we",
}


def _build_ai_subpillar_terms(schema: Dict[str, Any]) -> Dict[str, List[str]]:
    """Extract AI-focused search terms from schema5-0_ai.json's ai_evaluation_criteria."""
    # Find the taxonomy body
    body = None
    for key in schema:
        if key.startswith("dfir_capability_taxonomy"):
            body = schema[key]
            break
    if body is None:
        body = schema

    subs = body.get("sub_pillars", {})

    # Also load ai_search_terms from schema
    ai_search = body.get("ai_search_terms", {})
    primary_terms = ai_search.get("primary", [])
    secondary_terms = ai_search.get("secondary", [])

    def _normalize(t: str) -> str:
        t = t.strip().lower()
        t = re.sub(r"[^a-z0-9\-\s]", " ", t)
        return re.sub(r"\s+", " ", t).strip()

    def _tokenize(phrase: str) -> List[str]:
        words = _normalize(phrase).replace("-", " ").split()
        return [w for w in words if len(w) >= 4 and w not in STOPWORDS]

    terms_by_sub: Dict[str, List[str]] = {}

    for sid in SUBPILLAR_IDS:
        info = subs.get(sid, {})
        raw_terms: List[str] = []

        # Sub-pillar name
        name = info.get("name", "")
        if name:
            raw_terms.append(name)

        # ai_evaluation_criteria — THE PRIMARY SOURCE for v3
        criteria = info.get("ai_evaluation_criteria", [])
        for c in criteria:
            if isinstance(c, str) and c.strip():
                raw_terms.append(c)
                raw_terms.extend(_tokenize(c))

        # Also include what_to_verify_publicly if present (v4.0 style)
        for key in ("what_to_verify_publicly", "ai_specific_evidence"):
            items = info.get(key, [])
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, str):
                        raw_terms.append(item)
                        raw_terms.extend(_tokenize(item))

        # Add global AI terms
        raw_terms.extend(primary_terms)
        raw_terms.extend(secondary_terms)

        # Add the sub-pillar ID itself
        raw_terms.append(sid)

        # Dedupe and normalize
        cleaned: List[str] = []
        seen: set = set()
        for t in raw_terms:
            nt = _normalize(t)
            if len(nt) < 3 or len(nt.split()) > 8:
                continue
            if nt not in seen:
                cleaned.append(nt)
                seen.add(nt)

        terms_by_sub[sid] = cleaned

    return terms_by_sub


# ─────────────────────────────────────────────────────────────────────
# Text analysis & AI-weighted evidence extraction
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
    ai_term_count: int  # how many AI-specific terms matched


def _count_ai_terms_in_text(text_lower: str) -> int:
    """Count how many AI-specific terms appear in text."""
    return sum(1 for term in AI_PRIMARY_TERMS if term in text_lower)


def _ai_specificity_score(text_lower: str) -> float:
    """Score AI specificity from 0-5 based on term density and quality."""
    ai_hits = _count_ai_terms_in_text(text_lower)
    exclusion_hits = sum(1 for t in AI_EXCLUSION_TERMS if t in text_lower)

    if exclusion_hits > ai_hits:
        return 1.0  # Explicitly non-AI

    if ai_hits == 0:
        return 0.0  # No AI evidence
    if ai_hits <= 2:
        return 2.0  # Generic AI claims
    if ai_hits <= 5:
        return 3.0  # AI-augmented
    if ai_hits <= 10:
        return 4.0  # Advanced AI
    return 5.0  # Fully agentic signals


def _score_subpillar_ai(
    ai_specificity: float,
    criteria_hit_count: int,
    total_excerpts: int,
) -> float:
    """AI-weighted scoring: AI specificity is the PRIMARY dimension.
    
    Unlike v2 where AI was a bonus, here AI IS the score.
    The scoring scale maps to the schema5-0_ai scoring_logic:
      0 = No evidence
      1 = No AI/ML (capability exists but no AI)
      2 = Generic AI claims
      3 = AI-augmented, documented
      4 = Advanced AI, measurable
      5 = Fully agentic
    """
    if total_excerpts == 0:
        return 0.0  # No evidence at all

    if ai_specificity < 0.5:
        # Evidence found but no AI — score 1 (No AI/ML)
        if criteria_hit_count > 0:
            return 1.0
        return 0.0

    if ai_specificity <= 2.0:
        # Generic AI claims
        base = 2.0
        if criteria_hit_count >= 3:
            base = 2.25
        return base

    if ai_specificity <= 3.0:
        # AI-augmented
        base = 3.0
        if criteria_hit_count >= 5:
            base = 3.25
        elif criteria_hit_count >= 3:
            base = 3.0
        else:
            base = 2.75
        return base

    if ai_specificity <= 4.0:
        # Advanced AI
        base = 4.0
        if criteria_hit_count >= 5:
            base = 4.25
        elif criteria_hit_count >= 3:
            base = 4.0
        else:
            base = 3.75
        return base

    # Fully agentic (ai_specificity >= 4.5)
    base = 4.5
    if criteria_hit_count >= 5:
        base = 4.75
    return base


# ─────────────────────────────────────────────────────────────────────
# URL Discovery
# ─────────────────────────────────────────────────────────────────────


def discover_vendor_urls(vendor: Dict[str, Any], *, max_urls: int = 4) -> List[str]:
    vendor_name = vendor.get("vendor", "")
    urls: List[str] = []
    seen: set = set()

    def _add(u: str) -> None:
        u_clean = u.lower().rstrip("/")
        if u_clean not in seen and len(urls) < max_urls:
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

    return urls[:max_urls]


# ─────────────────────────────────────────────────────────────────────
# Evidence extraction (per vendor) — AI-focused
# ─────────────────────────────────────────────────────────────────────


def _vendor_flag(*, urls: List[str], ok_pages: int, excerpts_total: int) -> Tuple[str, float]:
    if not urls:
        return "no_urls", 0.0
    if ok_pages == 0:
        return "fetch_failed", 0.0
    coverage = max(0.0, min(1.0, excerpts_total / 20.0))
    if excerpts_total == 0:
        return "no_evidence", 0.1
    if coverage < 0.3:
        return "low_evidence", 0.35
    if coverage < 0.7:
        return "partial_evidence", 0.6
    return "good_evidence", 0.8


GENERIC_MATCH_TERMS = {
    "ai", "automated", "automation", "analysis", "detection", "response",
    "remediation", "security", "incident", "platform", "dashboard",
    "workflow", "workflows",
}


def evidence_for_vendor(
    vendor: Dict[str, Any],
    *,
    urls: List[str],
    terms_by_subpillar: Dict[str, List[str]],
    force_fetch: bool,
    max_excerpts_per_subpillar: int,
    sleep_seconds: float,
) -> Tuple[Dict[str, Any], Dict[str, float]]:
    """Extract AI-focused evidence and compute heuristic scores."""

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

    sub_evidence: Dict[str, Any] = {}
    sub_scores: Dict[str, float] = {}

    for sid in SUBPILLAR_IDS:
        terms = terms_by_subpillar.get(sid, [])
        hits: List[EvidenceHit] = []

        for url, text in pages_text:
            text_lower = text.lower()
            candidates = _candidate_snippets(text)

            for sent in candidates:
                s_lower = sent.lower()
                matched = [t for t in terms if t in s_lower]
                if not matched:
                    continue
                ai_count = sum(1 for t in matched if t in AI_PRIMARY_TERMS or
                               any(at in t for at in ["ai", "ml", "agentic", "llm", "autonomous"]))
                hits.append(EvidenceHit(
                    url=url, excerpt=sent.strip(),
                    matched_terms=matched[:10], ai_term_count=ai_count,
                ))

        # Dedupe and rank by AI-specificity
        uniq: Dict[str, EvidenceHit] = {}
        for h in hits:
            key = (h.url + "::" + h.excerpt)[:600]
            if key not in uniq:
                uniq[key] = h

        def _ai_specific_count(h: EvidenceHit) -> int:
            return h.ai_term_count + sum(1 for t in h.matched_terms if t not in GENERIC_MATCH_TERMS)

        sorted_hits = sorted(
            uniq.values(),
            key=lambda h: (_ai_specific_count(h), len(h.matched_terms), len(h.excerpt)),
            reverse=True,
        )
        selected = sorted_hits[:max_excerpts_per_subpillar]

        # AI specificity score across all pages
        ai_spec = 0.0
        if pages_text:
            ai_spec = max(_ai_specificity_score(t.lower()) for _, t in pages_text)

        criteria_hits = sum(_ai_specific_count(h) for h in selected)
        total_excerpts = len(selected)

        score = _score_subpillar_ai(ai_spec, criteria_hits, total_excerpts)
        sub_scores[sid] = round(score * 4) / 4  # quarter-step

        sub_evidence[sid] = {
            "source_urls": list(urls),
            "excerpts": [
                {
                    "url": h.url,
                    "excerpt": h.excerpt,
                    "matched_terms": h.matched_terms,
                    "ai_term_count": h.ai_term_count,
                }
                for h in selected
            ],
            "ai_specificity_score": ai_spec,
            "criteria_hit_count": criteria_hits,
            "notes": "AI-focused evidence extraction v3; scores reflect AI maturity, not general capability.",
        }

    excerpts_total = sum(
        len((sub_evidence.get(sid) or {}).get("excerpts") or [])
        for sid in SUBPILLAR_IDS
    )
    flag, confidence = _vendor_flag(urls=urls, ok_pages=ok_pages, excerpts_total=excerpts_total)
    sub_evidence["_vendor_summary"] = {
        "ok_pages": ok_pages,
        "total_pages_attempted": len(urls),
        "excerpts_total": excerpts_total,
        "flag": flag,
        "confidence": confidence,
    }

    return sub_evidence, sub_scores


# ─────────────────────────────────────────────────────────────────────
# Pillar scores
# ─────────────────────────────────────────────────────────────────────


def compute_pillar_scores(sub_scores: Dict[str, float]) -> Dict[str, float]:
    by_pillar: Dict[str, List[float]] = {p: [] for p in PILLARS}
    for sid, val in sub_scores.items():
        pillar = sid.split("-")[0]
        if pillar in by_pillar:
            by_pillar[pillar].append(float(val))
    return {p: round(_avg(vals) * 4) / 4 for p, vals in by_pillar.items()}


# ─────────────────────────────────────────────────────────────────────
# Rationale
# ─────────────────────────────────────────────────────────────────────


def _subpillar_name_from_schema(schema: Dict[str, Any], sid: str) -> str:
    body = None
    for key in schema:
        if key.startswith("dfir_capability_taxonomy"):
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
    ai_spec = ev.get("ai_specificity_score", 0.0)

    evidence_line = "No AI-specific evidence captured."
    if excerpts_raw:
        first = excerpts_raw[0]
        excerpt_text = _shorten(str(first.get("excerpt", "")), 200)
        evidence_line = f'AI signal: "{excerpt_text}".'
        if len(excerpts_raw) > 1:
            second = _shorten(str(excerpts_raw[1].get("excerpt", "")), 150)
            evidence_line += f' Also: "{second}".'

    ai_level = "None"
    if ai_spec >= 4.5:
        ai_level = "Fully Agentic"
    elif ai_spec >= 3.5:
        ai_level = "Advanced AI"
    elif ai_spec >= 2.5:
        ai_level = "AI-Augmented"
    elif ai_spec >= 1.5:
        ai_level = "Generic AI Claims"
    elif ai_spec >= 0.5:
        ai_level = "No AI/ML"

    parts = [
        f"{sid} - {name}. AI Score: {score_str}.",
        f"AI Maturity Level: {ai_level} (specificity={ai_spec:.1f}).",
        f"Evidence flag: {research_flag}.",
        evidence_line,
    ]

    if score < 3.0:
        parts.append(
            "To improve: Publicly document specific AI/ML tooling, models, "
            "measurable outcomes (detection rates, time savings), or agentic workflows."
        )

    return " ".join(p.strip() for p in parts if p and str(p).strip())


# ─────────────────────────────────────────────────────────────────────
# Checkpoint management (per-lot)
# ─────────────────────────────────────────────────────────────────────


def _checkpoint_path(lot: Optional[str]) -> Path:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = f"_lot_{lot}" if lot else "_all"
    return CHECKPOINT_DIR / f"v3_checkpoint{suffix}.json"


def _load_checkpoint(lot: Optional[str]) -> Dict[str, Any]:
    cp = _checkpoint_path(lot)
    if cp.exists():
        try:
            return json.loads(cp.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"completed_vendors": [], "results": {}}


def _save_checkpoint(lot: Optional[str], checkpoint: Dict[str, Any]) -> None:
    _checkpoint_path(lot).write_text(
        json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ─────────────────────────────────────────────────────────────────────
# IBM de-duplication
# ─────────────────────────────────────────────────────────────────────


def merge_ibm_vendors(vendors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ibm_primary = None
    ibm_dup_idx = None
    for idx, v in enumerate(vendors):
        name = v.get("vendor", "")
        if name == "IBM (X-Force)":
            ibm_primary = v
        elif name == "IBM Security (X-Force)":
            ibm_dup_idx = idx

    if ibm_primary is None or ibm_dup_idx is None:
        return vendors
    result = [v for i, v in enumerate(vendors) if i != ibm_dup_idx]
    print(f"  Merged IBM duplicate ({len(result)} vendors)")
    return result


# ─────────────────────────────────────────────────────────────────────
# Lot merge helper
# ─────────────────────────────────────────────────────────────────────


def merge_lots(full_file: Path, output_file: Path) -> int:
    """Merge all lot outputs into the full dataset."""
    LOT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    lot_files = sorted(LOT_OUTPUT_DIR.glob("lot_*.json"))
    if not lot_files:
        print("No lot output files found in", LOT_OUTPUT_DIR)
        return 1

    # Collect all AI-scored vendors
    ai_vendors: Dict[str, Dict[str, Any]] = {}
    for lf in lot_files:
        data = _safe_json_load(lf)
        vendors = data if isinstance(data, list) else data.get("vendors", data)
        if isinstance(vendors, list):
            for v in vendors:
                name = v.get("vendor", "")
                if name:
                    ai_vendors[name] = v
    print(f"Loaded {len(ai_vendors)} AI-scored vendors from {len(lot_files)} lot files")

    # Load full dataset
    full_data = _safe_json_load(full_file)
    if isinstance(full_data, dict) and "vendors" in full_data:
        full_vendors = full_data["vendors"]
        is_wrapped = True
    elif isinstance(full_data, list):
        full_vendors = full_data
        is_wrapped = False
    else:
        print("Unexpected full file format")
        return 1

    # Merge AI scores into full dataset
    merged_count = 0
    for v in full_vendors:
        name = v.get("vendor", "")
        if name in ai_vendors:
            ai_v = ai_vendors[name]
            # Copy AI-specific fields
            for key in [
                "sub_pillar_scores_ai_researched",
                "pillar_scores_ai_researched",
                "sub_pillar_evidence_ai",
                "sub_pillar_rationale_ai_researched",
                "research_flag_ai",
                "research_confidence_ai",
                "research_ai",
            ]:
                if key in ai_v:
                    v[key] = ai_v[key]
            merged_count += 1

    # Write output
    if is_wrapped:
        full_data["vendors"] = full_vendors
        full_data["schema_ref"] = "schema5-0_ai.json"
        full_data["vendor_count"] = len(full_vendors)
        out_data = full_data
    else:
        out_data = {
            "schema_ref": "schema5-0_ai.json",
            "schema_version": "5.0",
            "vendor_count": len(full_vendors),
            "vendors": full_vendors,
        }

    output_file.write_text(json.dumps(out_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output_file} ({len(full_vendors)} vendors, {merged_count} with AI scores)")
    return 0


# ─────────────────────────────────────────────────────────────────────
# Main pipeline
# ─────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AI-focused DFIR vendor research pipeline (v3)."
    )
    parser.add_argument("--full-file", type=Path, default=DEFAULT_FULL_FILE,
                        help="Full dataset to score and merge into")
    parser.add_argument("--schema-file", type=Path, default=DEFAULT_SCHEMA_FILE)
    parser.add_argument("--output-file", type=Path, default=DEFAULT_OUTPUT_FILE)
    parser.add_argument("--lot", type=str, choices=list(LOT_DEFINITIONS.keys()),
                        help="Run only this lot (A-F)")
    parser.add_argument("--merge-lots", action="store_true",
                        help="Merge all lot outputs into final file")
    parser.add_argument("--max-vendors", type=int, default=0)
    parser.add_argument("--max-urls-per-vendor", type=int, default=4)
    parser.add_argument("--sleep-seconds", type=float, default=1.0)
    parser.add_argument("--force-fetch", action="store_true")
    parser.add_argument("--max-excerpts-per-subpillar", type=int, default=3)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--skip-merge", action="store_true")

    args = parser.parse_args()

    # ── Merge-lots mode ──
    if args.merge_lots:
        return merge_lots(args.full_file, args.output_file)

    # ── Load inputs ──
    print(f"Loading full dataset: {args.full_file}")
    full_data = _safe_json_load(args.full_file)
    if isinstance(full_data, dict) and "vendors" in full_data:
        all_vendors = full_data["vendors"]
    elif isinstance(full_data, list):
        all_vendors = full_data
    else:
        raise SystemExit("Full file must be a JSON array or wrapped vendor dict")

    # IBM dedup
    all_vendors = merge_ibm_vendors(all_vendors)

    print(f"Loading schema: {args.schema_file}")
    schema = _safe_json_load(args.schema_file)
    terms_by_sub = _build_ai_subpillar_terms(schema)

    # ── Lot filtering ──
    if args.lot:
        lot_fn = LOT_DEFINITIONS[args.lot]
        target_vendors = [v for v in all_vendors if lot_fn(v.get("vendor", "?"))]
        print(f"Lot {args.lot}: {len(target_vendors)} vendors")
    else:
        target_vendors = list(all_vendors)
        print(f"All vendors: {len(target_vendors)}")

    limit = args.max_vendors if args.max_vendors > 0 else len(target_vendors)
    target_vendors = target_vendors[:limit]
    print(f"Processing {len(target_vendors)} vendors")

    # ── Resume support ──
    checkpoint = _load_checkpoint(args.lot) if args.resume else {"completed_vendors": [], "results": {}}
    completed_names = set(checkpoint.get("completed_vendors", []))

    # ── Sleep offset for parallel lots ──
    sleep_offset = LOT_SLEEP_OFFSETS.get(args.lot, 0)
    if sleep_offset > 0:
        print(f"Lot {args.lot} sleep offset: +{sleep_offset}s")

    started = datetime.now(timezone.utc)
    results: List[Dict[str, Any]] = []

    for idx, vendor in enumerate(target_vendors, start=1):
        name = vendor.get("vendor", "Unknown")

        if name in completed_names:
            print(f"[{idx}/{len(target_vendors)}] {name}: SKIPPED (checkpoint)")
            if name in checkpoint.get("results", {}):
                results.append(checkpoint["results"][name])
            else:
                results.append(vendor)
            continue

        print(f"[{idx}/{len(target_vendors)}] {name}: discovering URLs...")

        urls = discover_vendor_urls(vendor, max_urls=args.max_urls_per_vendor)
        print(f"  Found {len(urls)} URLs: {urls[:3]}...")

        sub_evidence, sub_scores = evidence_for_vendor(
            vendor,
            urls=urls,
            terms_by_subpillar=terms_by_sub,
            force_fetch=args.force_fetch,
            max_excerpts_per_subpillar=args.max_excerpts_per_subpillar,
            sleep_seconds=args.sleep_seconds + sleep_offset,
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

        ai_pillars = compute_pillar_scores(sub_scores)

        # Build rationales
        rationale: Dict[str, str] = {}
        for sid in SUBPILLAR_IDS:
            rationale[sid] = build_rationale(
                schema, vendor, sid,
                sub_evidence, sub_scores,
                research_flag,
            )

        # Update vendor record — AI-specific keys
        v3 = dict(vendor)
        v3["sub_pillar_evidence_ai"] = sub_evidence
        v3["sub_pillar_scores_ai_researched"] = sub_scores
        v3["pillar_scores_ai_researched"] = ai_pillars
        v3["sub_pillar_rationale_ai_researched"] = rationale
        v3["research_flag_ai"] = research_flag
        v3["research_confidence_ai"] = research_confidence
        v3["research_ai"] = {
            "status": "ai_scored_v3",
            "source": "public_web_text_3rd_party",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "urls_used": urls,
            "pages_ok": vendor_summary.get("ok_pages", 0),
            "schema": args.schema_file.name,
            "tool": "research_v3_ai_scoring.py",
            "lot": args.lot,
            "cap_applied": cap_applied,
        }

        results.append(v3)

        ok_pages = vendor_summary.get("ok_pages", 0)
        excerpts = vendor_summary.get("excerpts_total", 0)
        print(f"  Pages OK: {ok_pages}/{len(urls)}, Excerpts: {excerpts}, Flag: {research_flag}")

        checkpoint["completed_vendors"].append(name)
        checkpoint["results"][name] = v3
        _save_checkpoint(args.lot, checkpoint)

    # ── Output ──
    if args.lot:
        # Write lot output
        LOT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        lot_file = LOT_OUTPUT_DIR / f"lot_{args.lot}.json"
        lot_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nWrote lot output: {lot_file} ({len(results)} vendors)")
    elif args.skip_merge:
        args.output_file.write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nWrote delta output: {args.output_file} ({len(results)} vendors)")
    else:
        # Full merge: inject AI scores into the full dataset
        updated_lookup: Dict[str, Dict[str, Any]] = {}
        for v in results:
            updated_lookup[v.get("vendor", "")] = v

        # Re-load full dataset for merge
        full_data_reload = _safe_json_load(args.full_file)
        if isinstance(full_data_reload, dict) and "vendors" in full_data_reload:
            merge_list = full_data_reload["vendors"]
        elif isinstance(full_data_reload, list):
            merge_list = full_data_reload
        else:
            merge_list = []

        merge_list = merge_ibm_vendors(merge_list)

        merged_count = 0
        for v in merge_list:
            name = v.get("vendor", "")
            if name in updated_lookup:
                ai_v = updated_lookup[name]
                for key in [
                    "sub_pillar_scores_ai_researched",
                    "pillar_scores_ai_researched",
                    "sub_pillar_evidence_ai",
                    "sub_pillar_rationale_ai_researched",
                    "research_flag_ai",
                    "research_confidence_ai",
                    "research_ai",
                ]:
                    if key in ai_v:
                        v[key] = ai_v[key]
                merged_count += 1

        out_data = {
            "schema_ref": "schema5-0_ai.json",
            "schema_version": "5.0",
            "vendor_count": len(merge_list),
            "vendors": merge_list,
        }
        args.output_file.write_text(
            json.dumps(out_data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nWrote merged output: {args.output_file} ({len(merge_list)} vendors, {merged_count} AI-scored)")

    elapsed = datetime.now(timezone.utc) - started
    print(f"Elapsed: {elapsed}")

    # Clear checkpoint on success
    cp = _checkpoint_path(args.lot)
    if cp.exists():
        cp.unlink()
        print("Checkpoint cleared.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
