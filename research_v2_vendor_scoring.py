"""
research_v2_vendor_scoring.py — Enhanced DFIR Vendor Research Pipeline (v2)

Enhancements over v1 (research_validate_vendors.py):
  - Multi-page URL discovery (IR pages, product pages, blogs)
  - Bot-evasion with rotating User-Agents, realistic headers, randomized delays
  - Retry with exponential backoff (3 attempts)
  - Built-in URL correction for known fetch_failed vendors
  - Integrated rationale generation (no separate expand script needed)
  - IBM de-duplication (merges IBM Security (X-Force) into IBM (X-Force))
  - Merge step: reads full dataset, replaces updated records, writes final output
  - Per-vendor checkpointing with resume support

Usage:
  python research_v2_vendor_scoring.py
  python research_v2_vendor_scoring.py --delta-file "Vendor 5-1 Incomplete Research Delta.json"
  python research_v2_vendor_scoring.py --force-fetch --max-urls-per-vendor 6
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

DEFAULT_DELTA_FILE = ROOT / "Vendor 5-1 Incomplete Research Delta.json"
DEFAULT_FULL_FILE = ROOT / "Vendor 5-1 Researched.json"
DEFAULT_SCHEMA_FILE = ROOT / "schema4-0_enhanced.json"
DEFAULT_OUTPUT_FILE = ROOT / "Vendor 5-2 Researched.json"
CACHE_DIR = ROOT / "research" / "cache" / "pages"
CHECKPOINT_FILE = ROOT / "research" / "v2_checkpoint.json"

URL_RE = re.compile(r"https?://[^\s)\]\}\">,]+")

PILLARS = ["PLA", "INV", "REM", "PMG", "LAW"]
SUBPILLAR_IDS = [
    f"{p}-{i:02d}" for p in PILLARS for i in range(1, 5)
]

# ─────────────────────────────────────────────────────────────────────
# DFIR/IR-specific URLs for all 42 vendors (equal treatment, no bias)
# ─────────────────────────────────────────────────────────────────────

CORRECTED_URLS: Dict[str, List[str]] = {
    # ── All 42 vendors — DFIR/IR-specific URLs (equal treatment) ──
    "Aon (Stroz Friedberg)": [
        "https://www.aon.com/en/capabilities/cyber-resilience",
        "https://www.aon.com/cyber-solutions/",
        "https://www.strozfriedberg.com/",
    ],
    "Bitdefender": [
        "https://www.bitdefender.com/business/enterprise-products/managed-detection-response.html",
        "https://www.bitdefender.com/business/solutions/incident-response.html",
        "https://www.bitdefender.com/business/solutions/digital-forensics.html",
    ],
    "Booz Allen Hamilton": [
        "https://www.boozallen.com/expertise/cybersecurity.html",
        "https://www.boozallen.com/markets/commercial-solutions/incident-response.html",
        "https://www.boozallen.com/expertise/cybersecurity/incident-response.html",
    ],
    "Bridewell": [
        "https://www.bridewell.com/services/cyber-security",
        "https://www.bridewell.com/services/cyber-security/incident-response",
        "https://www.bridewell.com/services/24x7-incident-response-services",
        "https://www.bridewell.com/managed-security",
    ],
    "BT Cyber": [
        "https://business.bt.com/products/security/",
        "https://business.bt.com/products/managed-services/managed-security/",
        "https://www.globalservices.bt.com/en/solutions/products/managed-security",
    ],
    "Capgemini": [
        "https://www.capgemini.com/services/cybersecurity/",
        "https://www.capgemini.com/solutions/cyber-defense-center/",
        "https://www.capgemini.com/solutions/cybersecurity-services/managed-security-operations/",
    ],
    "Cisco": [
        "https://talosintelligence.com/",
        "https://talosintelligence.com/incident_response",
        "https://www.cisco.com/site/us/en/products/security/incident-response-services/index.html",
    ],
    "CPX": [
        "https://www.cpx.net/services/",
        "https://www.cpx.net/services/cyber-resilience-services/incident-forensics-capability/",
        "https://www.cpx.net/services/cyber-resilience-services/managed-detection-and-response-mdr/",
    ],
    "CyberCX": [
        "https://www.cybercx.com.au/solutions/digital-forensics-and-incident-response/",
        "https://www.cybercx.com.au/incident-response/",
        "https://www.cybercx.com.au/solutions/digital-forensic-investigation-services/",
    ],
    "Cyberegate": [
        "https://www.cyberegate.com/",
        "https://www.cyberegate.com/services/",
        "https://cyberegate.com/",
    ],
    "CyberLink": [
        "https://www.cyberlink-sa.com/",
        "https://www.cyberlink-sa.com/services/",
        "https://www.cyberlink.com/",
    ],
    "CyberSOC Africa": [
        "https://www.cybersocafrica.com/",
        "https://www.cybersocafrica.com/services/",
        "https://cybersocafrica.com/",
    ],
    "Digital Encode": [
        "https://www.digitalencode.net/",
        "https://www.digitalencode.net/live-response/",
        "https://www.digitalencode.net/our-services/",
    ],
    "DTS Solution": [
        "https://www.dtssolution.com/",
        "https://dts-solution.com/",
        "https://dts-solution.com/managed-security-services/",
    ],
    "Expel": [
        "https://www.expel.com/services/",
        "https://www.expel.com/platform/",
        "https://www.expel.com/solutions/",
        "https://expel.com/managed-detection-and-response/",
    ],
    "Group-IB": [
        "https://www.group-ib.com/services/incident-response/",
        "https://www.group-ib.com/services/digital-forensics/",
        "https://www.group-ib.com/services/",
        "https://www.group-ib.com/products/",
    ],
    "HCLTech": [
        "https://www.hcltech.com/cybersecurity",
        "https://www.hcltech.com/cybersecurity/managed-security-services",
        "https://www.hcltech.com/cyber-security",
    ],
    "Help AG": [
        "https://www.helpag.com/managed-security-service-provider/",
        "https://www.helpag.com/cybersecurity-assessments/",
        "https://www.helpag.com/offensive-cybersecurity/",
    ],
    "IBM (X-Force)": [
        "https://www.ibm.com/security/services/incident-response-services",
        "https://www.ibm.com/x-force",
        "https://www.ibm.com/services/offensive-security",
        "https://www.ibm.com/security",
    ],
    "IBM Security (X-Force)": [
        "https://www.ibm.com/security/services/incident-response-services",
        "https://www.ibm.com/x-force",
    ],
    "Infosys": [
        "https://www.infosys.com/services/cyber-security.html",
        "https://www.infosys.com/services/cyber-security/offerings.html",
        "https://www.infosys.com/services/cyber-security/insights.html",
    ],
    "Kivu": [
        "https://www.quorumcyber.com/kivu-becomes-quorum-cyber/",
        "https://www.quorumcyber.com/emergency-help/",
        "https://kivuconsulting.com/",
        "https://kivuconsulting.com/incident-response/",
    ],
    "LGMS": [
        "https://www.lgms.global/",
        "https://www.lgms.global/services/",
        "https://www.lgms.global/digital-forensics/",
    ],
    "Litt": [
        "https://www.littsolutions.com/",
        "https://www.littsolutions.com/services/",
        "https://litt.ai/",
    ],
    "Mitiga": [
        "https://www.mitiga.io/platform",
        "https://www.mitiga.io/services",
        "https://www.mitiga.io/cloud-investigation-and-response/",
    ],
    "mnemonic": [
        "https://www.mnemonic.io/solutions/incident-response/",
        "https://www.mnemonic.io/solutions/managed-detection-and-response/",
        "https://www.mnemonic.io/",
    ],
    "Nozomi Networks": [
        "https://www.nozominetworks.com/platform",
        "https://www.nozominetworks.com/solutions/threat-detection-and-response",
        "https://www.nozominetworks.com/professional-services",
    ],
    "Orange Cyberdefense": [
        "https://www.orangecyberdefense.com/global/offering/managed-services/incident-response",
        "https://www.orangecyberdefense.com/global/offering/managed-services",
        "https://www.orangecyberdefense.com/global/offering",
    ],
    "P0 Security": [
        "https://www.p0.dev/",
        "https://www.p0.dev/platform",
        "https://www.p0.dev/solutions",
        "https://p0.dev/",
    ],
    "Pondurance": [
        "https://www.pondurance.com/incident-response/",
        "https://www.pondurance.com/managed-detection-and-response/",
        "https://www.pondurance.com/incident-response-retainer/",
    ],
    "PwC": [
        "https://www.pwc.com/gx/en/issues/cybersecurity.html",
        "https://www.pwc.com/gx/en/services/forensics.html",
        "https://www.pwc.com/gx/en/services/consulting/cybersecurity-privacy-forensics.html",
    ],
    "Quorum Cyber": [
        "https://www.quorumcyber.com/services/incident-response/",
        "https://www.quorumcyber.com/emergency-help/",
        "https://www.quorumcyber.com/services/",
        "https://www.quorumcyber.com/services/clarity-extend-enhanced-detection-and-response/",
    ],
    "Rubrik": [
        "https://www.rubrik.com/",
        "https://www.rubrik.com/products/",
        "https://www.rubrik.com/solutions/cyber-recovery",
    ],
    "S-RM": [
        "https://www.s-rminform.com/cyber-incident-response",
        "https://www.s-rminform.com/digital-forensics",
        "https://www.s-rminform.com/offensive-security",
    ],
    "Serianu Limited": [
        "https://www.serianu.com/",
        "https://www.serianu.com/about-us.html",
        "https://www.serianu.com/contact.html",
    ],
    "Stellar Cyber": [
        "https://www.stellarcyber.ai/platform/",
        "https://www.stellarcyber.ai/uc/incidentresponse/",
        "https://www.stellarcyber.ai/platform/capabilities-ndr/",
    ],
    "Sygnia": [
        "https://www.sygnia.co/incident-response/",
        "https://www.sygnia.co/solutions/incident-response-retainer/",
        "https://www.sygnia.co/solutions/respond-recover/",
        "https://www.sygnia.co/velocity-tdir-platform/",
    ],
    "Tempest": [
        "https://www.tempest.com.br/",
        "https://www.tempest.com.br/en/",
        "https://www.tempest.com.br/servicos/",
    ],
    "Tenzai": [
        "https://tenzai.co/",
        "https://tenzai.ai/",
    ],
    "Total Assure": [
        "https://totalassure.co.uk/",
        "https://totalassure.co.uk/services/",
        "https://www.totalassure.co.uk/cyber-security/",
    ],
    "TrustedSEC": [
        "https://www.trustedsec.com/services/incident-response/",
        "https://www.trustedsec.com/services/",
        "https://www.trustedsec.com/report-a-breach/",
    ],
    "Trustwave": [
        "https://www.levelblue.com/services/incident-readiness-and-response/",
        "https://www.levelblue.com/services/digital-forensics/",
        "https://www.levelblue.com/services/cyber-incident-response/",
        "https://www.trustwave.com/en-us/services/consulting-and-professional-services/incident-response/",
    ],
    "Wolfpack InfoRisk": [
        "https://wolfpackrisk.com/",
        "https://wolfpackrisk.com/company-risk-management/",
        "https://wolfpackrisk.com/report-a-cybercrime/",
    ],
}

# ─────────────────────────────────────────────────────────────────────
# Additional DFIR-relevant URL paths to discover per vendor
# ─────────────────────────────────────────────────────────────────────

DFIR_SUBPATHS = [
    "/incident-response",
    "/incident-response/",
    "/services/incident-response",
    "/services/incident-response/",
    "/services/dfir",
    "/services/dfir/",
    "/services/digital-forensics",
    "/services/cyber-security",
    "/solutions/incident-response",
    "/products/",
    "/platform/",
    "/cyber-security",
    "/cybersecurity",
    "/forensics",
    "/threat-intelligence",
]

# ─────────────────────────────────────────────────────────────────────
# Rotating User-Agents for bot evasion
# ─────────────────────────────────────────────────────────────────────

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# ─────────────────────────────────────────────────────────────────────
# HTML Parser
# ─────────────────────────────────────────────────────────────────────


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
        if not text:
            return
        self._chunks.append(text)

    def get_text(self) -> str:
        return "\n".join(self._chunks)


# ─────────────────────────────────────────────────────────────────────
# Utility functions
# ─────────────────────────────────────────────────────────────────────


def _safe_json_load(path: Path) -> Any:
    """Load JSON with BOM tolerance."""
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8"), usedforsecurity=False).hexdigest()


def _avg(values: Iterable[float]) -> float:
    xs = list(values)
    return sum(xs) / len(xs) if xs else 0.0


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _normalize_text(s: str) -> str:
    s = (s or "")
    s = s.replace("\ufffd", " ").replace("\u00a0", " ")
    s = s.replace("\u2014", "-").replace("\u2013", "-").replace("\u2212", "-")
    s = " ".join(s.split())
    return s


def _shorten(s: str, max_len: int = 220) -> str:
    s = _normalize_text(s)
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "\u2026"


def _html_to_text(html: str) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(html)
    text = unescape(parser.get_text())
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ─────────────────────────────────────────────────────────────────────
# HTTP Fetch with retry & bot evasion
# ─────────────────────────────────────────────────────────────────────


def _fetch_url_with_retry(
    url: str,
    *,
    max_retries: int = 2,
    timeouts: Tuple[float, ...] = (10.0, 15.0),
) -> Tuple[Optional[str], Optional[str]]:
    """Return (content_type, html_text) with retry. Returns (None, None) on failure."""
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
# Cache management
# ─────────────────────────────────────────────────────────────────────


def _ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_path_for_url(url: str) -> Path:
    return CACHE_DIR / f"{_sha1(url)}.json"


def get_or_fetch_page(url: str, *, force: bool, timeout_seconds: float) -> Dict[str, Any]:
    """Returns cached record: {url, fetched_at, ok, content_type, text, error}."""
    _ensure_cache_dir()
    cache_path = _cache_path_for_url(url)

    if cache_path.exists() and not force:
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            # If previously failed, re-try in v2
            if cached.get("ok") is True:
                return cached
            # Fall through to re-fetch failed pages
        except Exception:
            pass

    ctype, html = _fetch_url_with_retry(url)

    if html is None:
        record = {
            "url": url,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "ok": False,
            "content_type": ctype,
            "text": "",
            "error": "fetch_failed",
        }
        cache_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return record

    text = _html_to_text(html)
    record = {
        "url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "ok": True,
        "content_type": ctype,
        "text": text[:200_000],
        "error": None,
    }
    cache_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


# ─────────────────────────────────────────────────────────────────────
# URL Discovery
# ─────────────────────────────────────────────────────────────────────


def discover_vendor_urls(vendor: Dict[str, Any], *, max_urls: int = 4) -> List[str]:
    """Discover multiple relevant URLs for a vendor."""
    vendor_name = vendor.get("vendor", "")
    urls: List[str] = []
    seen: set = set()

    def _add(u: str) -> None:
        u = u.rstrip("/") + "/"  # Normalize trailing slash
        u_clean = u.lower().rstrip("/")
        if u_clean not in seen and len(urls) < max_urls:
            seen.add(u_clean)
            urls.append(u)

    # 1. Corrected URLs for known problematic vendors
    if vendor_name in CORRECTED_URLS:
        for u in CORRECTED_URLS[vendor_name]:
            _add(u)

    # 2. URLs from capability_analysis field
    cap_text = vendor.get("capability_analysis") or ""
    for u in URL_RE.findall(cap_text):
        _add(u)

    # 3. capability_analysis_source
    src = vendor.get("capability_analysis_source")
    if src:
        _add(src)

    # 4. Discover DFIR subpaths from base domain
    base_urls = list(urls)  # Copy current list
    for base in base_urls:
        # Extract domain
        match = re.match(r"(https?://[^/]+)", base)
        if not match:
            continue
        domain = match.group(1)
        for subpath in DFIR_SUBPATHS:
            candidate = domain + subpath
            _add(candidate)
            if len(urls) >= max_urls:
                break
        if len(urls) >= max_urls:
            break

    return urls[:max_urls]


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

    # Dedupe preserving order
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


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "case",
    "could", "for", "from", "has", "have", "how", "if", "in", "into",
    "is", "it", "its", "may", "of", "on", "or", "our", "post",
    "should", "the", "their", "they", "this", "that", "these", "those",
    "to", "up", "use", "used", "using", "via", "was", "were", "will",
    "with", "without", "your", "you", "we", "workflow", "workflows",
}

GENERIC_MATCH_TERMS = {
    "ai", "agentic", "automated", "automation", "analysis",
    "investigation", "investigations", "detection", "response",
    "remediation", "security", "incident", "alerts", "alert",
    "platform", "dashboard", "dashboards", "report", "reports",
    "workflow", "workflows",
}

AI_SIGNAL_TERMS = [
    "ai agent", "ai agents", "agentic", "swarming", "llm",
    "large language model", "machine learning", "ml", "automated",
    "autonomous", "orchestration", "correlation", "timeline",
    "chain of custody", "evidence",
]


def _build_subpillar_terms(schema: Dict[str, Any]) -> Dict[str, List[str]]:
    """Extract search terms per sub-pillar from schema definitions."""
    tax = schema.get("dfir_capability_taxonomy_v4.0_enhanced", {})
    subs = tax.get("sub_pillars", {})

    def normalize_term(t: str) -> str:
        t = t.strip().lower()
        t = re.sub(r"[^a-z0-9\-\s]", " ", t)
        t = re.sub(r"\s+", " ", t)
        return t

    def tokenize_keywords(t: str) -> List[str]:
        nt = normalize_term(t).replace("-", " ")
        toks = [w for w in nt.split() if len(w) >= 4 and w not in STOPWORDS]
        seen: set = set()
        out: List[str] = []
        for w in toks:
            if w not in seen:
                out.append(w)
                seen.add(w)
        return out

    terms_by_sub: Dict[str, List[str]] = {}
    for sid in SUBPILLAR_IDS:
        info = subs.get(sid, {})
        terms: List[str] = []

        name = info.get("name")
        if isinstance(name, str) and name.strip():
            terms.append(name)

        for key in ("what_to_verify_publicly", "ai_specific_evidence"):
            items = info.get(key)
            if isinstance(items, list):
                for it in items:
                    if isinstance(it, str) and it.strip():
                        terms.append(it)
                        terms.extend(tokenize_keywords(it))

        terms.append(sid)

        cleaned: List[str] = []
        seen: set = set()
        for t in terms:
            nt = normalize_term(t)
            if len(nt) < 4 or len(nt.split()) > 5:
                continue
            if nt not in seen:
                cleaned.append(nt)
                seen.add(nt)

        # Add bigrams
        for phrase in list(cleaned):
            toks = phrase.split()
            if len(toks) == 2 and phrase not in seen:
                cleaned.append(phrase)
                seen.add(phrase)

        terms_by_sub[sid] = cleaned

    return terms_by_sub


def _ai_signal_score(text_lower: str) -> float:
    """Score AI signal strength from page text."""
    hits = sum(1 for term in AI_SIGNAL_TERMS if term in text_lower)
    if hits <= 1:
        return 1.5 if hits == 1 else 0.5
    if hits <= 3:
        return 2.5
    if hits <= 6:
        return 3.5
    if hits <= 9:
        return 4.25
    return 4.75


def _score_subpillar_from_hits(ai_score: float, hit_count: int) -> float:
    """Conservative heuristic mapping from evidence to score.
    
    AI signal provides a +0.25 bonus when present, but is NOT required.
    Traditional DFIR vendors score on evidence strength alone.
    """
    ai_bonus = 0.25 if ai_score >= 2.5 else 0.0
    if hit_count <= 0:
        return 0.25
    if hit_count == 1:
        return 1.25 + ai_bonus
    if hit_count <= 3:
        return 2.25 + ai_bonus
    if hit_count <= 6:
        return 3.25 + ai_bonus
    return 4.25 + ai_bonus


def _vendor_flag(*, urls: List[str], ok_pages: int, excerpts_total: int) -> Tuple[str, float]:
    """Return (flag, confidence)."""
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


# ─────────────────────────────────────────────────────────────────────
# Evidence extraction (per vendor)
# ─────────────────────────────────────────────────────────────────────


def evidence_for_vendor(
    vendor: Dict[str, Any],
    *,
    urls: List[str],
    terms_by_subpillar: Dict[str, List[str]],
    force_fetch: bool,
    timeout_seconds: float,
    max_excerpts_per_subpillar: int,
    sleep_seconds: float,
) -> Tuple[Dict[str, Any], Dict[str, float]]:
    """Extract evidence and compute heuristic scores for all sub-pillars."""

    # Fetch pages
    page_records: List[Dict[str, Any]] = []
    for u in urls:
        rec = get_or_fetch_page(u, force=force_fetch, timeout_seconds=timeout_seconds)
        page_records.append(rec)
        delay = sleep_seconds + random.uniform(0.5, 2.0)
        time.sleep(delay)

    # Build searchable text per successful page
    pages_text: List[Tuple[str, str]] = []
    for rec in page_records:
        if rec.get("ok") is True and isinstance(rec.get("text"), str):
            pages_text.append((rec["url"], rec["text"]))

    ok_pages = len(pages_text)

    # Evidence extraction per sub-pillar
    sub_evidence: Dict[str, Any] = {}
    sub_scores: Dict[str, float] = {}

    for sid in SUBPILLAR_IDS:
        terms = terms_by_subpillar.get(sid, [])
        hits: List[EvidenceHit] = []

        for url, text in pages_text:
            text_lower = text.lower()
            ai_score = _ai_signal_score(text_lower)

            candidates = _candidate_snippets(text)
            for sent in candidates:
                s_lower = sent.lower()
                matched = [t for t in terms if t in s_lower]
                if not matched:
                    continue
                # AI signal is used as a score modifier, NOT a gate
                hits.append(EvidenceHit(url=url, excerpt=sent.strip(), matched_terms=matched[:10]))

        # Dedupe and rank
        uniq: Dict[str, EvidenceHit] = {}
        for h in hits:
            key = (h.url + "::" + h.excerpt)[:600]
            if key not in uniq:
                uniq[key] = h

        def specific_count(h: EvidenceHit) -> int:
            return sum(1 for t in h.matched_terms if t not in GENERIC_MATCH_TERMS)

        sorted_hits = sorted(
            uniq.values(),
            key=lambda h: (specific_count(h), len(h.matched_terms), len(h.excerpt)),
            reverse=True,
        )
        selected = sorted_hits[:max_excerpts_per_subpillar]

        # Heuristic score
        ai_score_overall = 0.0
        if pages_text:
            ai_score_overall = max(_ai_signal_score(t.lower()) for _, t in pages_text)

        specific_hits_total = sum(specific_count(h) for h in selected)
        suggested = _score_subpillar_from_hits(ai_score_overall, specific_hits_total)

        sub_scores[sid] = round(suggested * 4) / 4  # quarter-step
        sub_evidence[sid] = {
            "source_urls": [u for u in urls],
            "excerpts": [
                {
                    "url": h.url,
                    "excerpt": h.excerpt,
                    "matched_terms": h.matched_terms,
                    "specific_term_count": specific_count(h),
                }
                for h in selected
            ],
            "ai_signal_score": ai_score_overall,
            "hit_count": len(selected),
            "specific_hit_count": specific_hits_total,
            "notes": "Heuristic evidence extraction v2; analyst review recommended.",
        }

    # Vendor-level summary
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
# Pillar score computation
# ─────────────────────────────────────────────────────────────────────


def compute_pillar_scores(sub_scores: Dict[str, float]) -> Dict[str, float]:
    by_pillar: Dict[str, List[float]] = {p: [] for p in PILLARS}
    for sid, val in sub_scores.items():
        pillar = sid.split("-")[0]
        if pillar in by_pillar:
            by_pillar[pillar].append(float(val))
    return {p: round(_avg(vals) * 4) / 4 for p, vals in by_pillar.items()}


# ─────────────────────────────────────────────────────────────────────
# Rationale generation (integrated from expand_research_rationales.py)
# ─────────────────────────────────────────────────────────────────────


def _subpillar_name(schema: Dict[str, Any], sid: str) -> str:
    tax = schema.get("dfir_capability_taxonomy_v4.0_enhanced", {})
    subs = tax.get("sub_pillars", {})
    if isinstance(subs, dict):
        sp = subs.get(sid) or {}
        if isinstance(sp, dict) and sp.get("name"):
            return str(sp["name"])
    return sid


def _explain_ceiling(score: float) -> str:
    if score >= 4.5:
        return (
            "This is near the ceiling because the public-facing signals strongly "
            "and repeatedly describe concrete, DFIR-specific implementation, not just marketing claims."
        )
    if score >= 4.0:
        return (
            "The score is high because there are multiple concrete public signals, "
            "but we do not consistently see deep, end-to-end implementation detail across sources."
        )
    if score >= 3.0:
        return (
            "The score reflects moderate evidence: the capability is plausibly present, "
            "but public proof is not consistently detailed or independently corroborated."
        )
    if score >= 2.0:
        return (
            "The score is low-to-moderate because evidence is thin, generic, or indirect; "
            "we do not see enough specificity to justify a higher rating."
        )
    if score >= 1.0:
        return (
            "The score is low because we see only weak or generic signals, "
            "with little DFIR-specific detail."
        )
    return "The score is minimal because we did not find credible public evidence for this sub-pillar."


def _what_to_improve() -> str:
    return (
        "To justify a higher score, we would expect clearer DFIR proof such as named tooling/workflows, "
        "detailed case studies, repeatable methodology documentation, certifications, or artifacts "
        "that show operational depth."
    )


def build_rationale(
    schema: Dict[str, Any],
    vendor: Dict[str, Any],
    sid: str,
    sub_evidence: Dict[str, Any],
    sub_scores: Dict[str, float],
    research_flag: str,
    research_confidence: float,
) -> str:
    """Build >= 180 char rationale string for a single sub-pillar."""
    name = (
        (vendor.get("sub_pillar_schema_labels") or {}).get(sid)
        or _subpillar_name(schema, sid)
        or sid
    )
    name = _normalize_text(str(name))

    score = sub_scores.get(sid)
    score_str = f"{score:.1f}/5" if score is not None else "N/A"
    conf_str = str(research_confidence)

    # Extract excerpts
    ev = sub_evidence.get(sid, {})
    excerpts_raw = ev.get("excerpts", [])
    excerpts: List[str] = []
    for item in excerpts_raw:
        if isinstance(item, dict):
            txt = _shorten(str(item.get("excerpt", "")), 260)
            matched = item.get("matched_terms", [])
            if matched:
                txt = f"{txt} (matched: {', '.join(str(t) for t in matched[:6])})"
            if txt.strip():
                excerpts.append(txt)

    source_urls = ev.get("source_urls", [])

    # Build rationale
    evidence_line = ""
    if excerpts:
        evidence_line = f'Public-source signals include: "{excerpts[0]}".'
        if len(excerpts) > 1:
            evidence_line += f' Also: "{excerpts[1]}".'
    else:
        evidence_line = (
            "No sub-pillar-specific public excerpt was captured for this capability "
            "in our current evidence set."
        )

    sources_line = ""
    if source_urls:
        sources_line = f"Sources observed: {', '.join(source_urls[:3])}."

    scoring_guardrail = ""
    if research_flag != "good_evidence":
        scoring_guardrail = (
            "Because this vendor is not flagged as good_evidence, we apply a conservative guardrail: "
            "sub-pillar scores should not exceed 3.0 without stronger public proof."
        )

    ceiling = _explain_ceiling(score if score is not None else 0.0)

    parts = [
        f"{sid} - {name}. Score: {score_str}.",
        f"Evidence flag/confidence: {research_flag} / {conf_str}.",
        evidence_line,
    ]
    if sources_line:
        parts.append(sources_line)
    if scoring_guardrail:
        parts.append(scoring_guardrail)
    parts.append(ceiling)
    parts.append(_what_to_improve())

    return " ".join(p.strip() for p in parts if p and str(p).strip())


# ─────────────────────────────────────────────────────────────────────
# IBM de-duplication
# ─────────────────────────────────────────────────────────────────────


def merge_ibm_vendors(vendors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge 'IBM Security (X-Force)' into 'IBM (X-Force)' if both exist with same region."""
    ibm_primary = None
    ibm_dup = None
    ibm_dup_idx = None

    for idx, v in enumerate(vendors):
        name = v.get("vendor", "")
        if name == "IBM (X-Force)":
            ibm_primary = v
        elif name == "IBM Security (X-Force)":
            ibm_dup = v
            ibm_dup_idx = idx

    if ibm_primary is None or ibm_dup is None:
        return vendors  # Nothing to merge

    # Only merge if same region
    if ibm_primary.get("region") != ibm_dup.get("region"):
        print(f"  IBM vendors have different regions - skipping merge")
        return vendors

    # Keep the richer capability_analysis
    if len(ibm_dup.get("capability_analysis", "")) > len(ibm_primary.get("capability_analysis", "")):
        ibm_primary["capability_analysis"] = ibm_dup["capability_analysis"]

    # Merge: keep highest validated scores per pillar/sub-pillar
    for key in ("pillar_scores_validated", "pillar_scores"):
        primary_scores = ibm_primary.get(key, {})
        dup_scores = ibm_dup.get(key, {})
        for p, val in dup_scores.items():
            if p not in primary_scores or val > primary_scores.get(p, 0):
                primary_scores[p] = val
        ibm_primary[key] = primary_scores

    for key in ("sub_pillar_scores_validated", "sub_pillar_scores_current"):
        primary_scores = ibm_primary.get(key, {})
        dup_scores = ibm_dup.get(key, {})
        for sid, val in dup_scores.items():
            if sid not in primary_scores or val > primary_scores.get(sid, 0):
                primary_scores[sid] = val
        ibm_primary[key] = primary_scores

    # Remove duplicate
    result = [v for idx, v in enumerate(vendors) if idx != ibm_dup_idx]
    print(f"  Merged 'IBM Security (X-Force)' into 'IBM (X-Force)' ({len(result)} vendors)")
    return result


# ─────────────────────────────────────────────────────────────────────
# Checkpoint management
# ─────────────────────────────────────────────────────────────────────


def _load_checkpoint() -> Dict[str, Any]:
    if CHECKPOINT_FILE.exists():
        try:
            return json.loads(CHECKPOINT_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"completed_vendors": [], "results": {}}


def _save_checkpoint(checkpoint: Dict[str, Any]) -> None:
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_FILE.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────
# Main pipeline
# ─────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enhanced evidence-based research pipeline for DFIR vendor scoring (v2)."
    )
    parser.add_argument("--delta-file", type=Path, default=DEFAULT_DELTA_FILE,
                        help="Input: vendors needing research")
    parser.add_argument("--full-file", type=Path, default=DEFAULT_FULL_FILE,
                        help="Full dataset for merge step")
    parser.add_argument("--schema-file", type=Path, default=DEFAULT_SCHEMA_FILE)
    parser.add_argument("--output-file", type=Path, default=DEFAULT_OUTPUT_FILE)
    parser.add_argument("--max-vendors", type=int, default=0, help="0 = all vendors")
    parser.add_argument("--max-urls-per-vendor", type=int, default=6)
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    parser.add_argument("--sleep-seconds", type=float, default=1.0)
    parser.add_argument("--force-fetch", action="store_true",
                        help="Re-fetch all pages (ignore cache)")
    parser.add_argument("--max-excerpts-per-subpillar", type=int, default=2)
    parser.add_argument("--resume", action="store_true",
                        help="Resume from checkpoint")
    parser.add_argument("--skip-merge", action="store_true",
                        help="Skip merge step (output delta only)")

    args = parser.parse_args()

    # Load inputs
    print(f"Loading delta file: {args.delta_file}")
    delta_vendors = _safe_json_load(args.delta_file)
    if not isinstance(delta_vendors, list):
        raise SystemExit("Delta file must be a JSON array")

    print(f"Loading schema: {args.schema_file}")
    schema = _safe_json_load(args.schema_file)
    terms_by_sub = _build_subpillar_terms(schema)

    # IBM de-duplication on delta
    delta_vendors = merge_ibm_vendors(delta_vendors)

    limit = args.max_vendors if args.max_vendors > 0 else len(delta_vendors)
    delta_vendors = delta_vendors[:limit]
    print(f"Processing {len(delta_vendors)} vendors")

    # Resume support
    checkpoint = _load_checkpoint() if args.resume else {"completed_vendors": [], "results": {}}
    completed_names = set(checkpoint.get("completed_vendors", []))

    started = datetime.now(timezone.utc)
    results: List[Dict[str, Any]] = []

    for idx, vendor in enumerate(delta_vendors, start=1):
        name = vendor.get("vendor", "Unknown")

        # Skip if already completed in checkpoint
        if name in completed_names:
            print(f"[{idx}/{len(delta_vendors)}] {name}: SKIPPED (checkpoint)")
            # Load from checkpoint results
            if name in checkpoint.get("results", {}):
                results.append(checkpoint["results"][name])
            else:
                results.append(vendor)
            continue

        print(f"[{idx}/{len(delta_vendors)}] {name}: discovering URLs...")

        # Discover URLs
        urls = discover_vendor_urls(vendor, max_urls=args.max_urls_per_vendor)
        print(f"  Found {len(urls)} URLs: {urls[:3]}...")

        # Extract evidence
        sub_evidence, sub_scores = evidence_for_vendor(
            vendor,
            urls=urls,
            terms_by_subpillar=terms_by_sub,
            force_fetch=args.force_fetch,
            timeout_seconds=args.timeout_seconds,
            max_excerpts_per_subpillar=args.max_excerpts_per_subpillar,
            sleep_seconds=args.sleep_seconds,
        )

        # Get vendor flag
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
                    if sid in sub_evidence and isinstance(sub_evidence[sid], dict):
                        sub_evidence[sid]["score_cap_applied"] = {
                            "cap": 3.0,
                            "reason": "research_flag_not_good_evidence",
                        }

        # Compute pillar scores
        researched_pillars = compute_pillar_scores(sub_scores)

        # Build rationales
        rationale: Dict[str, str] = {}
        for sid in SUBPILLAR_IDS:
            rationale[sid] = build_rationale(
                schema, vendor, sid,
                sub_evidence, sub_scores,
                research_flag, research_confidence,
            )

        # Update vendor record
        v2 = dict(vendor)
        v2["sub_pillar_evidence"] = sub_evidence
        v2["sub_pillar_scores_researched"] = sub_scores
        v2["pillar_scores_researched"] = researched_pillars
        v2["sub_pillar_rationale_researched"] = rationale
        v2["research_flag"] = research_flag
        v2["research_confidence"] = research_confidence
        v2["research"] = {
            "status": "heuristic_collected_v2",
            "source": "public_web_text",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "urls_used": urls,
            "pages_cached": len(urls),
            "pages_ok": vendor_summary.get("ok_pages", 0),
            "schema": args.schema_file.name,
            "tool": "research_v2_vendor_scoring.py",
            "validation_rules": {
                "cap_non_good_evidence_subpillars_at": 3.0,
            },
            "cap_applied": bool(cap_applied),
        }

        # Update capability_analysis_source if original was broken
        if urls:
            v2["capability_analysis_source"] = urls[0]

        results.append(v2)

        # Report
        ok_pages = vendor_summary.get("ok_pages", 0)
        excerpts = vendor_summary.get("excerpts_total", 0)
        print(f"  Pages OK: {ok_pages}/{len(urls)}, Excerpts: {excerpts}, Flag: {research_flag}, Confidence: {research_confidence}")

        # Checkpoint
        checkpoint["completed_vendors"].append(name)
        checkpoint["results"][name] = v2
        _save_checkpoint(checkpoint)

    # ─────────────────────────────────────────────────────────────────
    # Merge step
    # ─────────────────────────────────────────────────────────────────

    if args.skip_merge:
        # Write delta-only output
        args.output_file.write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nWrote delta output: {args.output_file} ({len(results)} vendors)")
    else:
        print(f"\nMerging into full dataset: {args.full_file}")
        full_vendors = _safe_json_load(args.full_file)
        if not isinstance(full_vendors, list):
            raise SystemExit("Full file must be a JSON array")

        # IBM de-duplication on full dataset
        full_vendors = merge_ibm_vendors(full_vendors)

        # Build lookup of updated vendors by name
        updated_lookup: Dict[str, Dict[str, Any]] = {}
        for v in results:
            updated_lookup[v.get("vendor", "")] = v

        # Replace records
        merged: List[Dict[str, Any]] = []
        replaced = 0
        for v in full_vendors:
            name = v.get("vendor", "")
            if name in updated_lookup:
                merged.append(updated_lookup[name])
                replaced += 1
            else:
                merged.append(v)

        # Write merged output
        args.output_file.write_text(
            json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Wrote merged output: {args.output_file} ({len(merged)} vendors, {replaced} updated)")

    elapsed = datetime.now(timezone.utc) - started
    print(f"Elapsed: {elapsed}")

    # Cleanup checkpoint on success
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()
        print("Checkpoint cleared.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
