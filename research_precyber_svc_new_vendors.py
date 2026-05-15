"""
research_precyber_svc_new_vendors.py
======================================
Runs the SVC + Pricing research pass on vendors in 3-0 that are missing
sub_pillar_scores_current (i.e., the new batch added after the original
research_precyber_svc_pricing.py run).

Steps:
  1. Load Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json
  2. Filter to vendors without sub_pillar_scores_current
  3. Pre-populate sub_pillar_scores_current from sub_pillar_scores_v2_researched
  4. Run SVC + pricing scoring (same logic as original script)
  5. Merge results back into 3-0 SVC Pricing.json
  6. Regenerate 5-0 Combined.json

Usage:
  python research_precyber_svc_new_vendors.py
  python research_precyber_svc_new_vendors.py --max-vendors 5
  python research_precyber_svc_new_vendors.py --batch-pause 5 --sleep 0.3
  python research_precyber_svc_new_vendors.py --resume
  python research_precyber_svc_new_vendors.py --merge-only
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

ROOT = Path(__file__).resolve().parent

INPUT_FILE  = ROOT / "Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json"
OUTPUT_FILE = ROOT / "Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json"
COMBINED_FILE = ROOT / "Preemptive Cybersecurity Vendor 5-0 Combined.json"
SCHEMA_FILE = ROOT / "Preemptive_Cybersecurity_Schema_v2.json"

CACHE_DIR      = ROOT / "research" / "cache" / "pages_precyber"
CHECKPOINT_DIR = ROOT / "research" / "precyber_svc_new_checkpoints"
BATCH_DIR      = ROOT / "research" / "precyber_svc_new_batches"

SVC_SUBPILLARS = [
    "EXM-05", "AMT-05", "ADR-05", "PPM-05",
    "SVC-01", "SVC-02", "SVC-03", "SVC-04",
]
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
# SVC/Pricing URLs for the 31 new vendors
# ─────────────────────────────────────────────────────────────

SVC_PRICING_URLS: Dict[str, List[str]] = {
    "Trustwave": [
        "https://www.trustwave.com/en-us/company/pricing/",
        "https://www.trustwave.com/en-us/services/",
        "https://www.trustwave.com/en-us/services/managed-security-services/",
        "https://www.trustwave.com/en-us/services/professional-services/",
    ],
    "Cyderes": [
        "https://www.cyderes.com/services/",
        "https://www.cyderes.com/solutions/",
        "https://www.cyderes.com/managed-detection-response/",
    ],
    "Optiv": [
        "https://www.optiv.com/services/",
        "https://www.optiv.com/solutions/managed-security-services/",
        "https://www.optiv.com/services/advisory-services/",
        "https://www.optiv.com/insights/pricing",
    ],
    "Leidos Cybersecurity": [
        "https://www.leidos.com/capabilities/cybersecurity",
        "https://www.leidos.com/capabilities/cybersecurity/managed-security-services",
        "https://www.leidos.com/capabilities/cybersecurity/incident-response",
    ],
    "BT Security": [
        "https://www.bt.com/business/solutions/cyber-security/",
        "https://www.bt.com/business/solutions/cyber-security/managed-security-services/",
        "https://www.bt.com/business/solutions/cyber-security/security-consulting/",
        "https://www.globalservices.bt.com/en/solutions/security",
    ],
    "Orange Cyberdefense": [
        "https://www.orangecyberdefense.com/global/solutions/",
        "https://www.orangecyberdefense.com/global/solutions/managed-security/",
        "https://www.orangecyberdefense.com/global/solutions/professional-services/",
        "https://www.orangecyberdefense.com/global/pricing/",
    ],
    "Wipro CyberTransformation": [
        "https://www.wipro.com/cybersecurity/",
        "https://www.wipro.com/cybersecurity/managed-security-services/",
        "https://www.wipro.com/cybersecurity/cyber-defense-services/",
        "https://www.wipro.com/cybersecurity/advisory-services/",
    ],
    "Infosys Cybersecurity": [
        "https://www.infosys.com/services/cyber-security.html",
        "https://www.infosys.com/services/cyber-security/managed-detection-response.html",
        "https://www.infosys.com/services/cyber-security/cybersecurity-consulting.html",
    ],
    "NTT Data": [
        "https://www.nttdata.com/global/en/services/security/",
        "https://www.nttdata.com/global/en/services/security/managed-security-services",
        "https://www.nttdata.com/global/en/services/security/advisory",
    ],
    "Tata Consultancy Services (TCS) Security": [
        "https://www.tcs.com/what-we-do/industries/cybersecurity",
        "https://www.tcs.com/what-we-do/services/cybersecurity/managed-security-services",
        "https://www.tcs.com/what-we-do/services/cybersecurity/advisory-compliance",
    ],
    "Noetic Cyber": [
        "https://www.noeticcyber.com/pricing/",
        "https://www.noeticcyber.com/product/",
        "https://www.noeticcyber.com/services/",
    ],
    "Ionix (formerly Cyberpion)": [
        "https://ionix.io/pricing/",
        "https://ionix.io/product/",
        "https://ionix.io/services/",
        "https://ionix.io/managed-services/",
    ],
    "Silentpush": [
        "https://www.silentpush.com/pricing/",
        "https://www.silentpush.com/product/",
        "https://www.silentpush.com/services/",
    ],
    "Fletch (formerly Cronus Cyber)": [
        "https://fletch.ai/pricing/",
        "https://fletch.ai/product/",
        "https://fletch.ai/services/",
        "https://fletch.ai/platform/",
    ],
    "Flashpoint": [
        "https://flashpoint.io/pricing/",
        "https://flashpoint.io/products/",
        "https://flashpoint.io/services/",
        "https://flashpoint.io/solutions/managed-intelligence/",
    ],
    "Cyberint (Check Point)": [
        "https://cyberint.com/pricing/",
        "https://cyberint.com/platform/",
        "https://cyberint.com/services/",
        "https://cyberint.com/managed-detection-response/",
    ],
    "Cybersixgill": [
        "https://cybersixgill.com/pricing/",
        "https://cybersixgill.com/platform/",
        "https://cybersixgill.com/services/",
        "https://cybersixgill.com/managed-services/",
    ],
    "Illusive Networks": [
        "https://illusive.com/pricing/",
        "https://illusive.com/products/",
        "https://illusive.com/services/",
        "https://www.illusivenetworks.com/pricing/",
    ],
    "Sygnia": [
        "https://www.sygnia.co/services/",
        "https://www.sygnia.co/services/incident-response/",
        "https://www.sygnia.co/services/proactive-services/",
        "https://www.sygnia.co/services/managed-services/",
    ],
    "Stroz Friedberg (Aon)": [
        "https://www.strozfriedberg.com/services/",
        "https://www.strozfriedberg.com/services/incident-response/",
        "https://www.aon.com/cyber-solutions/stroz-friedberg/",
        "https://www.aon.com/en/solutions/cyber",
    ],
    "Zafran Security": [
        "https://www.zafran.io/pricing/",
        "https://www.zafran.io/product/",
        "https://www.zafran.io/services/",
    ],
    "Opus Security": [
        "https://opus.security/pricing/",
        "https://opus.security/platform/",
        "https://opus.security/services/",
    ],
    "Brinqa": [
        "https://www.brinqa.com/pricing/",
        "https://www.brinqa.com/platform/",
        "https://www.brinqa.com/services/",
        "https://www.brinqa.com/solutions/",
    ],
    "PlexTrac": [
        "https://plextrac.com/pricing/",
        "https://plextrac.com/platform/",
        "https://plextrac.com/services/",
        "https://plextrac.com/solutions/",
    ],
    "Hadrian": [
        "https://hadrian.io/pricing/",
        "https://hadrian.io/product/",
        "https://hadrian.io/services/",
        "https://hadrian.io/platform/",
    ],
    "ColorTokens": [
        "https://colortokens.com/pricing/",
        "https://colortokens.com/platform/",
        "https://colortokens.com/services/",
        "https://colortokens.com/solutions/",
    ],
    "Titaniam": [
        "https://titaniam.io/pricing/",
        "https://titaniam.io/platform/",
        "https://titaniam.io/services/",
        "https://titaniam.io/solutions/",
    ],
    "Akeyless": [
        "https://www.akeyless.io/pricing/",
        "https://www.akeyless.io/platform/",
        "https://www.akeyless.io/services/",
        "https://www.akeyless.io/solutions/",
    ],
    "Aembit": [
        "https://aembit.io/pricing/",
        "https://aembit.io/platform/",
        "https://aembit.io/product/",
        "https://aembit.io/services/",
    ],
    "Veracode": [
        "https://www.veracode.com/pricing",
        "https://www.veracode.com/products/",
        "https://www.veracode.com/services/",
        "https://www.veracode.com/solutions/managed-services/",
    ],
    "Vulcan Cyber": [
        "https://vulcan.io/pricing/",
        "https://vulcan.io/platform/",
        "https://vulcan.io/services/",
        "https://vulcan.io/solutions/",
    ],
}


# ─────────────────────────────────────────────────────────────
# Utilities (copied from original script)
# ─────────────────────────────────────────────────────────────

def _cache_path(url: str) -> Path:
    h = hashlib.md5(url.encode()).hexdigest()
    return CACHE_DIR / f"{h}.json"


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._buf: List[str] = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg", "head"}:
            self._skip = True

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg", "head"}:
            self._skip = False
        if tag in {"p", "div", "li", "h1", "h2", "h3", "h4", "tr", "br"}:
            self._buf.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self._buf.append(data)

    def get_text(self) -> str:
        raw = "".join(self._buf)
        lines = [ln.strip() for ln in raw.splitlines()]
        lines = [ln for ln in lines if ln]
        return "\n".join(lines)


def _html_to_text(html: Optional[str]) -> str:
    if not html:
        return ""
    try:
        p = _TextExtractor()
        p.feed(unescape(html))
        return p.get_text()
    except Exception:
        return re.sub(r"<[^>]+>", " ", html or "")


def _fetch_url_playwright_svc(url: str) -> Optional[str]:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            try:
                page = browser.new_page()
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
            pass

    _extracted = _html_to_text(html) if html else ""
    if not _extracted or len(_extracted.strip()) < 200:
        pw_html = _fetch_url_playwright_svc(url)
        if pw_html:
            pw_text = _html_to_text(pw_html)
            if len(pw_text.strip()) > len(_extracted.strip()):
                html, _extracted = pw_html, pw_text

    if _extracted.strip():
        record = {
            "url": url,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "ok": True,
            "content_type": None,
            "text": _extracted[:200_000],
            "error": None,
        }
        cp.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return record

    record = {
        "url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "ok": False, "content_type": None, "text": "", "error": "fetch_failed",
    }
    cp.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


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
# Vendor loading
# ─────────────────────────────────────────────────────────────

def load_all_vendors() -> List[Dict[str, Any]]:
    """Load all vendors from 3-0 file."""
    raw = Path(INPUT_FILE).read_text(encoding="utf-8-sig")
    data = json.loads(raw)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if "vendors" in data:
            return data["vendors"]
        for key in data:
            if isinstance(data[key], list) and data[key] and isinstance(data[key][0], dict):
                return data[key]
    return []


def load_new_vendors() -> List[Dict[str, Any]]:
    """Return only vendors missing sub_pillar_scores_current."""
    all_v = load_all_vendors()
    new_v = [v for v in all_v if not v.get("sub_pillar_scores_current")]
    print(f"Total vendors: {len(all_v)}, New (missing sub_pillar_scores_current): {len(new_v)}")
    return new_v


# ─────────────────────────────────────────────────────────────
# URL discovery
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
            for url in ev.get("urls", []):
                if isinstance(url, str) and url.startswith("http"):
                    _add(existing_urls, url)
        elif isinstance(ev, list):
            for item in ev:
                if isinstance(item, dict):
                    for url in item.get("urls", []):
                        if isinstance(url, str) and url.startswith("http"):
                            _add(existing_urls, url)

    # Also collect from svc_evidence if present
    svc_evidence = vendor.get("svc_evidence", {})
    if isinstance(svc_evidence, dict):
        for url in svc_evidence.get("urls", []):
            if isinstance(url, str) and url.startswith("http"):
                _add(existing_urls, url)

    # Add curated SVC/pricing URLs for this vendor
    new_urls = []
    for url in SVC_PRICING_URLS.get(name, []):
        _add(new_urls, url)

    return existing_urls, new_urls


# ─────────────────────────────────────────────────────────────
# Scoring functions — import from original script
# ─────────────────────────────────────────────────────────────

def _import_original_scoring():
    """Import scoring functions from the original SVC pricing script."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "svc_orig",
        ROOT / "research_precyber_svc_pricing.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# We'll lazy-import and cache the original module
_orig_mod = None

def _get_orig():
    global _orig_mod
    if _orig_mod is None:
        _orig_mod = _import_original_scoring()
    return _orig_mod


def score_svc_subpillar(sid, schema, pages):
    return _get_orig().score_svc_subpillar(sid, schema, pages)


def score_pricing_dimension(dim_id, schema, pages):
    return _get_orig().score_pricing_dimension(dim_id, schema, pages)


def build_svc_rationale(sid, schema, score, ev):
    return _get_orig().build_svc_rationale(sid, schema, score, ev)


def build_pricing_rationale(dim_id, schema, score, ev):
    return _get_orig().build_pricing_rationale(dim_id, schema, score, ev)


def compute_outcome_maturity(pricing_scores):
    return _get_orig().compute_outcome_maturity(pricing_scores)


# ─────────────────────────────────────────────────────────────
# Process a single vendor
# ─────────────────────────────────────────────────────────────

def process_vendor(
    vendor: Dict[str, Any],
    schema: Dict[str, Any],
    *,
    force_fetch: bool = False,
) -> Dict[str, Any]:
    name = vendor.get("vendor", "Unknown")
    print(f"\n{'='*60}")
    print(f"Processing: {name}")
    print(f"{'='*60}")

    # Pre-populate sub_pillar_scores_current from v2_researched (16 core keys)
    vendor = dict(vendor)
    if not vendor.get("sub_pillar_scores_current"):
        v2r = vendor.get("sub_pillar_scores_v2_researched", {})
        if v2r:
            vendor["sub_pillar_scores_current"] = dict(v2r)
            print(f"  Pre-populated sub_pillar_scores_current from v2_researched ({len(v2r)} keys)")
        else:
            vendor["sub_pillar_scores_current"] = {}

    # Discover URLs
    existing_urls, new_urls = discover_vendor_urls(vendor)
    print(f"  Existing cached URLs: {len(existing_urls)}")
    print(f"  New SVC/pricing URLs: {len(new_urls)}")

    # Load existing cached pages
    pages = []
    cached_count = 0
    for url in existing_urls:
        cp = _cache_path(url)
        if cp.exists():
            try:
                cached = json.loads(cp.read_text(encoding="utf-8"))
                if cached.get("ok") and cached.get("text"):
                    pages.append((url, cached["text"]))
                    cached_count += 1
            except Exception:
                pass

    print(f"  Loaded {cached_count} pages from existing cache")

    # Fetch new SVC/pricing URLs
    fetched_count = 0
    for url in new_urls:
        rec = fetch_page(url, force=force_fetch)
        if rec.get("ok") and rec.get("text"):
            pages.append((url, rec["text"]))
            fetched_count += 1
        time.sleep(FETCH_SLEEP + random.uniform(0.3, 1.5))

    print(f"  Fetched {fetched_count} new pages ({len(new_urls) - fetched_count} failed)")
    print(f"  Total pages for analysis: {len(pages)}")

    if not pages:
        print(f"  WARNING: No pages available for {name}")

    # Score SVC sub-pillars
    svc_scores = {}
    svc_evidence = {}
    svc_rationales = {}

    for sid in SVC_SUBPILLARS:
        score, ev = score_svc_subpillar(sid, schema, pages)
        svc_scores[sid] = score
        svc_evidence[sid] = ev
        svc_rationales[sid] = build_svc_rationale(sid, schema, score, ev)
        print(f"  {sid}: {score:.2f}/5 ({ev.get('search_term_hits', 0)} term hits, {ev.get('criteria_text_hits', 0)} criteria)")

    # Score pricing dimensions
    pricing_scores = {}
    pricing_evidence = {}
    pricing_rationales = {}

    for dim_id in PRICING_DIMS:
        score, ev = score_pricing_dimension(dim_id, schema, pages)
        pricing_scores[dim_id] = score
        pricing_evidence[dim_id] = ev
        pricing_rationales[dim_id] = build_pricing_rationale(dim_id, schema, score, ev)
        print(f"  {dim_id}: {score:.2f}/5 ({ev.get('search_term_hits', 0)} term hits)")

    # Outcome maturity
    outcome_rating, outcome_label = compute_outcome_maturity(pricing_scores)
    print(f"  Outcome maturity: {outcome_rating:.2f} ({outcome_label})")

    # Services maturity level
    avg_svc = sum(svc_scores.values()) / max(len(svc_scores), 1)
    if avg_svc >= 4.0:
        maturity_level = "ai_augmented"
    elif avg_svc >= 3.0:
        maturity_level = "managed"
    elif avg_svc >= 2.0:
        maturity_level = "consultative"
    else:
        maturity_level = "implementation_only"

    # Build enriched vendor record
    enriched = dict(vendor)

    # Merge SVC scores into sub_pillar_scores_current (already has 16 core keys)
    existing_scores = enriched.get("sub_pillar_scores_current", {})
    existing_scores.update(svc_scores)
    enriched["sub_pillar_scores_current"] = existing_scores

    # Merge SVC evidence
    existing_evidence = enriched.get("sub_pillar_evidence", {})
    existing_evidence.update(svc_evidence)
    enriched["sub_pillar_evidence"] = existing_evidence

    # Merge SVC rationales
    existing_rationales = enriched.get("sub_pillar_rationale_v2_consolidated", {})
    existing_rationales.update(svc_rationales)
    enriched["sub_pillar_rationale_v2_consolidated"] = existing_rationales

    # Update pillar scores (add SVC pillar, update EXM/AMT/ADR/PPM with -05)
    pillar_scores = enriched.get("pillar_scores", {})
    svc_avg = sum(svc_scores.get(f"SVC-{i:02d}", 0) for i in range(1, 5)) / 4
    pillar_scores["SVC"] = round(svc_avg, 2)
    for pillar in ["EXM", "AMT", "ADR", "PPM"]:
        sp_ids = [f"{pillar}-{i:02d}" for i in range(1, 6)]
        vals = [existing_scores.get(sp, 0.0) for sp in sp_ids]
        pillar_scores[pillar] = round(sum(vals) / len(vals), 2)
    enriched["pillar_scores"] = pillar_scores

    # Pricing data
    enriched["pricing_dimension_scores"] = pricing_scores
    enriched["pricing_evidence"] = pricing_evidence
    enriched["pricing_rationales"] = pricing_rationales
    enriched["outcome_maturity_rating"] = outcome_rating
    enriched["outcome_maturity_label"] = outcome_label
    enriched["services_maturity_level"] = maturity_level

    return enriched


# ─────────────────────────────────────────────────────────────
# Checkpoint / batch helpers
# ─────────────────────────────────────────────────────────────

def _progress_file() -> Path:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    return CHECKPOINT_DIR / "progress.json"


def _load_progress() -> Dict:
    pf = _progress_file()
    if pf.exists():
        try:
            return json.loads(pf.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"completed_batches": [], "completed_vendors": []}


def _save_progress(progress: Dict):
    _progress_file().write_text(json.dumps(progress, indent=2), encoding="utf-8")


def _save_batch(batch_num: int, results: List[Dict]):
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    bf = BATCH_DIR / f"svc_new_batch_{batch_num:04d}.json"
    bf.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Saved batch {batch_num} → {bf.name}")


# ─────────────────────────────────────────────────────────────
# Merge batches back into 3-0 and regenerate 5-0
# ─────────────────────────────────────────────────────────────

def merge_batches() -> int:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    batch_files = sorted(BATCH_DIR.glob("svc_new_batch_*.json"))
    if not batch_files:
        print("No batch files found.")
        return 1

    # Collect all scored vendors from batches
    scored: Dict[str, Dict] = {}
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

    print(f"Loaded {len(scored)} newly scored vendors from {len(batch_files)} batch files")

    # Load current 3-0 (all vendors)
    all_vendors = load_all_vendors()
    print(f"Current 3-0 vendor count: {len(all_vendors)}")

    # Merge
    final = []
    updated = 0
    for v in all_vendors:
        name = v.get("vendor", "")
        if name in scored:
            final.append(scored[name])
            updated += 1
        else:
            final.append(v)

    # Write 3-0
    backup = OUTPUT_FILE.with_name(OUTPUT_FILE.stem + f" BACKUP_pre_svc_new_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    import shutil
    shutil.copy(OUTPUT_FILE, backup)
    print(f"Backup: {backup.name}")

    OUTPUT_FILE.write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated 3-0: {updated}/{len(all_vendors)} vendors enriched")

    # Regenerate 5-0
    COMBINED_FILE.write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Regenerated 5-0: {COMBINED_FILE.name}")

    # Grade summary
    grades: Dict[str, int] = {}
    missing_spc = 0
    for v in final:
        g = v.get("coverage_grade", "unscored")
        grades[g] = grades.get(g, 0) + 1
        if not v.get("sub_pillar_scores_current"):
            missing_spc += 1
    print("Grade distribution:")
    for g, n in sorted(grades.items()):
        print(f"  {g}: {n}")
    if missing_spc:
        print(f"WARNING: {missing_spc} vendors still missing sub_pillar_scores_current")
    else:
        print("All vendors now have sub_pillar_scores_current ✓")

    return 0


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PreCyber SVC + Pricing Research — New Vendors")
    parser.add_argument("--max-vendors", type=int, default=0,
                        help="Max new vendors to process (0=all)")
    parser.add_argument("--batch-size", type=int, default=5,
                        help="Vendors per batch")
    parser.add_argument("--batch-pause", type=float, default=10.0,
                        help="Seconds between batches")
    parser.add_argument("--sleep", type=float, default=0.0,
                        help="Extra sleep per vendor (seconds)")
    parser.add_argument("--force-fetch", action="store_true",
                        help="Re-fetch cached pages")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from last checkpoint")
    parser.add_argument("--merge-only", action="store_true",
                        help="Just merge batch outputs into 3-0 and regenerate 5-0")
    args = parser.parse_args()

    print("=" * 70)
    print("PreCyber SVC + Pricing Research — New Vendors Pipeline")
    print("=" * 70)

    if args.merge_only:
        return merge_batches()

    schema = load_schema()
    vendors = load_new_vendors()

    if args.max_vendors > 0:
        vendors = vendors[:args.max_vendors]
        print(f"Limited to {args.max_vendors} vendors")

    # Resume support
    progress = _load_progress() if args.resume else {"completed_batches": [], "completed_vendors": []}
    completed_names = set(progress.get("completed_vendors", []))
    if completed_names:
        print(f"Resuming: {len(completed_names)} vendors already completed")

    remaining = [v for v in vendors if v.get("vendor", "") not in completed_names]
    total_batches = (len(remaining) + args.batch_size - 1) // args.batch_size
    start_batch = len(progress.get("completed_batches", []))

    print(f"\nProcessing {len(remaining)} vendors in {total_batches} batches of {args.batch_size}")
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
                enriched = process_vendor(v, schema, force_fetch=args.force_fetch)
                batch_results.append(enriched)
                progress["completed_vendors"].append(v.get("vendor", ""))
            except Exception as e:
                print(f"  ERROR processing {v.get('vendor', '?')}: {e}")
                batch_results.append(v)

            if args.sleep > 0:
                time.sleep(args.sleep)

        _save_batch(batch_num, batch_results)
        progress["completed_batches"].append(batch_num)
        _save_progress(progress)

        if batch_idx < total_batches - 1 and args.batch_pause > 0:
            print(f"\nPausing {args.batch_pause}s between batches...")
            time.sleep(args.batch_pause)

    # Auto-merge after all batches complete
    print("\n" + "=" * 70)
    print("All batches complete — merging into 3-0 and regenerating 5-0")
    print("=" * 70)
    merge_batches()

    print("\nDone!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
