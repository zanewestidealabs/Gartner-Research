"""
research_precyber_v2_rationale.py — Preemptive Cybersecurity Scoring Rationale & Evidence Quality

Reads Preemptive Cybersecurity Vendor 1-1 Validated.json and for each vendor / sub-pillar:
  1. Re-analyses ALL cached page content (from v1 evidence run)
  2. Searches for ADDITIONAL public pages (security/preemptive/product pages)
  3. Matches evidence against schema evaluation criteria (what_to_verify_publicly)
  4. Produces a structured scoring rationale explaining WHY the score is what it is
  5. Documents evidence quality factors (source diversity, specificity, depth)
  6. Adjusts scores when the rationale justifies a change (up or down)
  7. Writes output to "Preemptive Cybersecurity Vendor 2-0 Researched.json"

Usage:
  python research_precyber_v2_rationale.py                     # full run
  python research_precyber_v2_rationale.py --max-vendors 3     # test with 3
  python research_precyber_v2_rationale.py --dry-run           # show without writing
  python research_precyber_v2_rationale.py --no-fetch          # skip new URL discovery
"""

import argparse
import hashlib
import json
import random
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# ─────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent

DEFAULT_INPUT  = ROOT / "Preemptive Cybersecurity Vendor 1-1 Validated.json"
DEFAULT_OUTPUT = ROOT / "Preemptive Cybersecurity Vendor 2-0 Researched.json"
SCHEMA_FILE    = ROOT / "Preemptive_Cybersecurity_Schema.json"

CACHE_DIR = ROOT / "research" / "cache" / "pages_precyber"

PILLARS = ["EXM", "AMT", "ADR", "PPM"]
SUBPILLAR_IDS = [f"{p}-{i:02d}" for p in PILLARS for i in range(1, 5)]

# Scoring level descriptions — from PreCyber schema
SCORING_LEVELS = {
    0: "No Evidence — No publicly verifiable evidence of capability in this sub-pillar.",
    1: "Minimal — Basic or manual capability; no automation, analytics, or continuous operation.",
    2: "Generic Claims — Marketing mentions the capability but lacks named products, technical docs, or specifics.",
    3: "Demonstrated — Documented capability with named products or features, some technical detail, identifiable use cases.",
    4: "Advanced — Named products with measurable outcomes, integration points, customer validation, or analyst recognition.",
    5: "Market-Leading — Best-in-class with deep technical evidence, extensive customer base, analyst leadership recognition.",
}

# ─────────────────────────────────────────────────────────────────────
# Import term matching & infrastructure from v1
# ─────────────────────────────────────────────────────────────────────

from research_precyber_v1_evidence import (
    PRECYBER_PRIMARY_TERMS,
    PRECYBER_EXCLUSION_TERMS,
    PILLAR_SPECIFIC_TERMS,
    TERM_SYNONYMS,
    _term_in_text,
    _matched_terms_in_text,
    _candidate_snippets,
    _split_sentences,
    get_or_fetch_page,
    VENDOR_URLS,
)

# ─────────────────────────────────────────────────────────────────────
# HTML stripping (lightweight, stdlib-only)
# ─────────────────────────────────────────────────────────────────────

class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._parts: List[str] = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip = True
        elif tag in ("p", "div", "br", "li", "h1", "h2", "h3", "h4", "td", "th"):
            self._parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            self._parts.append(data)

    def get_text(self) -> str:
        return unescape("".join(self._parts))


def _html_to_text(html: str) -> str:
    parser = _TextExtractor()
    try:
        parser.feed(html)
    except Exception:
        pass
    text = parser.get_text()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _fetch_url_with_retry(url: str, retries: int = 1) -> Tuple[Optional[str], Optional[str]]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=6) as resp:
                ctype = resp.headers.get("Content-Type", "")
                raw = resp.read(500_000)
                encoding = "utf-8"
                if "charset=" in ctype:
                    encoding = ctype.split("charset=")[-1].split(";")[0].strip()
                return ctype, raw.decode(encoding, errors="replace")
        except urllib.error.HTTPError as he:
            if he.code < 500:
                return None, None
            if attempt < retries:
                time.sleep(2 * (attempt + 1))
        except KeyboardInterrupt:
            raise
        except Exception:
            if attempt < retries:
                time.sleep(2 * (attempt + 1))
    return None, None


def _fetch_url_playwright(url: str) -> Tuple[Optional[str], Optional[str]]:
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
        return "text/html", html
    except ImportError:
        return None, None
    except KeyboardInterrupt:
        raise
    except Exception:
        return None, None


def _cache_path_for_url(url: str) -> Path:
    h = hashlib.sha1(url.encode("utf-8"), usedforsecurity=False).hexdigest()
    return CACHE_DIR / f"{h}.json"


def get_or_fetch_page_local(url: str, *, force: bool = False) -> Dict[str, Any]:
    """Fetch a page with caching — mirrors v1 but self-contained."""
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
    # Playwright fallback: fires when urllib fails or returns bot-blocked content
    # Check extracted text (not raw HTML) so Cloudflare challenge pages trigger the fallback
    _extracted = _html_to_text(html) if html else ""
    if not _extracted or len(_extracted.strip()) < 200:
        pw_ctype, pw_html = _fetch_url_playwright(url)
        if pw_html:
            pw_text = _html_to_text(pw_html)
            if len(pw_text.strip()) > len(_extracted.strip()):
                ctype, html, _extracted = pw_ctype, pw_html, pw_text
    if not _extracted.strip():
        record = {
            "url": url, "fetched_at": datetime.now(timezone.utc).isoformat(),
            "ok": False, "content_type": ctype, "text": "", "error": "fetch_failed",
        }
    else:
        record = {
            "url": url, "fetched_at": datetime.now(timezone.utc).isoformat(),
            "ok": True, "content_type": ctype, "text": _extracted[:200_000], "error": None,
        }
    cache_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


# ─────────────────────────────────────────────────────────────────────
# Schema loader
# ─────────────────────────────────────────────────────────────────────

def load_schema() -> Dict[str, Any]:
    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    for key in schema:
        if key.startswith("preemptive_cybersecurity_taxonomy"):
            return schema[key]
    return schema


def get_sub_pillar_info(schema_body: Dict[str, Any], sid: str) -> Dict[str, Any]:
    """Get name, definition, criteria for a sub-pillar."""
    subs = schema_body.get("sub_pillars", {})
    info = subs.get(sid, {})
    return {
        "name": info.get("name", sid),
        "definition": info.get("expanded_definition", ""),
        "criteria": info.get("what_to_verify_publicly", []),
        "search_terms": info.get("search_terms", []),
    }


# ─────────────────────────────────────────────────────────────────────
# Additional URL discovery
# ─────────────────────────────────────────────────────────────────────

PILLAR_SEARCH_SUFFIXES = {
    "EXM": ["attack surface", "exposure management", "vulnerability management",
            "asset discovery", "supply chain risk"],
    "AMT": ["moving target defense", "runtime protection", "application hardening",
            "micro-segmentation", "privileged access"],
    "ADR": ["deception technology", "threat intelligence", "threat hunting",
            "adversary disruption", "dark web monitoring"],
    "PPM": ["breach attack simulation", "penetration testing", "security validation",
            "cloud security posture", "red team"],
}


def discover_additional_urls(vendor_name: str, existing_urls: List[str]) -> List[str]:
    """Try to find additional vendor pages from their existing evidence URLs."""
    additional: List[str] = []
    seen = {u.lower().rstrip("/") for u in existing_urls}

    domains: Set[str] = set()
    for url in existing_urls:
        match = re.match(r"https?://([^/]+)", url)
        if match:
            domains.add(match.group(1))

    # Common paths for preemptive cybersecurity content
    additional_paths = [
        "/security", "/platform", "/products", "/solutions",
        "/attack-surface-management", "/vulnerability-management",
        "/threat-intelligence", "/deception", "/zero-trust",
        "/cloud-security", "/penetration-testing", "/red-team",
        "/solutions/exposure-management", "/solutions/threat-hunting",
        "/solutions/attack-simulation", "/solutions/cloud-security",
        "/products/asm", "/products/cspm", "/products/xdr",
    ]

    for domain in domains:
        for path in additional_paths:
            candidate = f"https://{domain}{path}"
            if candidate.lower().rstrip("/") not in seen:
                additional.append(candidate)
                seen.add(candidate.lower().rstrip("/"))

    return additional[:5]


# ─────────────────────────────────────────────────────────────────────
# Evidence quality computation (inline — adapted from v4)
# ─────────────────────────────────────────────────────────────────────

QUALITY_WEIGHTS = {
    "source_diversity": 0.15,
    "evidence_volume": 0.20,
    "specificity_ratio": 0.20,
    "term_density": 0.25,
    "preemptive_signal": 0.10,
    "consistency": 0.10,
}

SOURCE_THRESHOLDS = {1: 0.2, 2: 0.5, 3: 0.7, 4: 0.85}


def compute_evidence_quality(evidence_block: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute evidence quality for a single sub-pillar evidence block."""
    if not evidence_block or not isinstance(evidence_block, dict):
        return {
            "quality_factor": 0.5,
            "components": {},
            "notes": "No evidence data — neutral quality assumed.",
        }

    source_urls = evidence_block.get("source_urls", [])
    if not isinstance(source_urls, list):
        source_urls = []
    excerpts = evidence_block.get("excerpts", [])
    if not isinstance(excerpts, list):
        excerpts = []

    hit_count = evidence_block.get("criteria_hit_count", 0) or 0
    specific_hit_count = (evidence_block.get("pillar_term_hits", 0) or 0) + \
                         (evidence_block.get("schema_criteria_hits", 0) or 0)
    preemptive_signal = evidence_block.get("sub_pillar_specificity", 0) or 0

    # 1. Source diversity
    n_sources = len(set(source_urls))
    source_factor = 0.0
    for threshold, factor in sorted(SOURCE_THRESHOLDS.items()):
        if n_sources >= threshold:
            source_factor = factor
    if n_sources >= 5:
        source_factor = 1.0

    # 2. Evidence volume
    volume_factor = min(len(excerpts) / 8.0, 1.0)

    # 3. Specificity ratio
    if hit_count > 0 and specific_hit_count > 0:
        specificity_factor = min(specific_hit_count / max(hit_count * 2, 1), 1.0)
    elif len(excerpts) > 0:
        total_specific = sum(
            ex.get("relevance_score", 0)
            for ex in excerpts if isinstance(ex, dict)
        )
        total_matched = sum(
            len(ex.get("matched_terms", [])) for ex in excerpts if isinstance(ex, dict)
        )
        specificity_factor = min(total_specific / max(total_matched * 2, 1), 1.0) if total_matched else 0.3
    else:
        specificity_factor = 0.0

    # 4. Term density
    if excerpts:
        total_specific_terms = sum(
            len(ex.get("matched_terms", []))
            for ex in excerpts if isinstance(ex, dict)
        )
        avg_terms = total_specific_terms / len(excerpts)
        term_density = min(avg_terms / 5.0, 1.0)
    else:
        term_density = 0.0

    # 5. Preemptive signal alignment
    if isinstance(preemptive_signal, (int, float)) and preemptive_signal > 0:
        signal_factor = min(preemptive_signal / 5.0, 1.0)
    else:
        signal_factor = 0.5

    # 6. Consistency
    unique_excerpt_urls = set()
    for ex in excerpts:
        if isinstance(ex, dict) and ex.get("url"):
            unique_excerpt_urls.add(ex["url"])
    if len(unique_excerpt_urls) >= 3:
        consistency = 1.0
    elif len(unique_excerpt_urls) == 2:
        consistency = 0.7
    elif len(unique_excerpt_urls) == 1 and len(excerpts) >= 2:
        consistency = 0.4
    elif len(excerpts) >= 1:
        consistency = 0.25
    else:
        consistency = 0.0

    # Weighted combination
    quality_factor = (
        source_factor * QUALITY_WEIGHTS["source_diversity"]
        + volume_factor * QUALITY_WEIGHTS["evidence_volume"]
        + specificity_factor * QUALITY_WEIGHTS["specificity_ratio"]
        + term_density * QUALITY_WEIGHTS["term_density"]
        + signal_factor * QUALITY_WEIGHTS["preemptive_signal"]
        + consistency * QUALITY_WEIGHTS["consistency"]
    )
    quality_factor = max(0.0, min(1.0, quality_factor))

    notes_parts = []
    if n_sources == 0:
        notes_parts.append("No source URLs")
    elif n_sources == 1:
        notes_parts.append("Single source only")
    if len(excerpts) == 0:
        notes_parts.append("No excerpts")
    if specificity_factor < 0.3:
        notes_parts.append("Low specificity")
    if quality_factor >= 0.7:
        notes_parts.append("Strong evidence")
    elif quality_factor >= 0.4:
        notes_parts.append("Moderate evidence")
    else:
        notes_parts.append("Weak evidence")

    return {
        "quality_factor": round(quality_factor, 4),
        "components": {
            "source_diversity": round(source_factor, 3),
            "evidence_volume": round(volume_factor, 3),
            "specificity_ratio": round(specificity_factor, 3),
            "term_density": round(term_density, 3),
            "preemptive_signal": round(signal_factor, 3),
            "consistency": round(consistency, 3),
        },
        "raw_counts": {
            "source_count": n_sources,
            "excerpt_count": len(excerpts),
            "hit_count": hit_count,
            "specific_hit_count": specific_hit_count,
            "preemptive_signal": preemptive_signal,
        },
        "notes": "; ".join(notes_parts) if notes_parts else "OK",
    }


# ─────────────────────────────────────────────────────────────────────
# Core analysis engine
# ─────────────────────────────────────────────────────────────────────

@dataclass
class CriterionAssessment:
    criterion: str
    status: str   # "met", "partial", "unmet"
    evidence: str
    confidence: str  # "high", "medium", "low"


@dataclass
class SubPillarRationale:
    sid: str
    name: str
    original_score: float
    adjusted_score: float
    scoring_level: int  # 0-5
    score_rationale: str
    evidence_quality_rationale: str
    criteria_assessment: List[CriterionAssessment]
    scoring_level_justification: str
    key_evidence: List[str]
    score_adjustment_reason: str
    additional_sources_found: int
    confidence: str
    evidence_quality_factor: float


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def assess_criterion(criterion: str, all_text: str, excerpts: List[Dict]) -> CriterionAssessment:
    """Assess whether a specific evaluation criterion is met by the evidence."""
    criterion_lower = _normalise(criterion)

    stop_extra = {"with", "that", "from", "into", "each", "also",
                  "this", "have", "been", "does", "more", "than",
                  "very", "will", "when", "what", "your", "they",
                  "based", "such", "only", "over", "both", "most",
                  "some", "well", "make", "like", "just", "take",
                  "across", "specific", "per"}

    key_words = [w for w in criterion_lower.split()
                 if len(w) >= 4 and w not in stop_extra]

    concept_pairs = []
    for i in range(len(key_words) - 1):
        pair = f"{key_words[i]} {key_words[i+1]}"
        concept_pairs.append(pair)

    text_lower = all_text.lower()

    word_hits = sum(1 for w in key_words if w in text_lower)
    word_coverage = word_hits / max(len(key_words), 1)

    pair_hits = sum(1 for p in concept_pairs if p in text_lower)

    synonym_hits = 0
    for w in key_words:
        if _term_in_text(w, text_lower) and w not in text_lower:
            synonym_hits += 1

    total_concept_coverage = (word_hits + synonym_hits) / max(len(key_words), 1)

    best_excerpt = ""
    best_excerpt_score = 0
    for ex in excerpts:
        ex_text = (ex.get("excerpt", "") or "").lower()
        ex_hits = sum(1 for w in key_words if w in ex_text)
        if ex_hits > best_excerpt_score:
            best_excerpt_score = ex_hits
            best_excerpt = ex.get("excerpt", "")[:200]

    sentences = _split_sentences(all_text)
    for sent in sentences:
        sent_lower = sent.lower()
        sent_hits = sum(1 for w in key_words if w in sent_lower)
        if sent_hits > best_excerpt_score:
            best_excerpt_score = sent_hits
            best_excerpt = sent[:200]

    if total_concept_coverage >= 0.7 and pair_hits >= 2:
        status = "met"
        confidence = "high"
    elif total_concept_coverage >= 0.5 and (pair_hits >= 1 or best_excerpt_score >= 3):
        status = "met"
        confidence = "medium"
    elif total_concept_coverage >= 0.4 or (pair_hits >= 1 and best_excerpt_score >= 2):
        status = "partial"
        confidence = "medium"
    elif word_hits >= 2:
        status = "partial"
        confidence = "low"
    else:
        status = "unmet"
        confidence = "high" if word_coverage == 0 else "medium"

    evidence_note = best_excerpt if best_excerpt else f"No direct evidence ({word_hits}/{len(key_words)} terms)"

    return CriterionAssessment(
        criterion=criterion,
        status=status,
        evidence=evidence_note,
        confidence=confidence,
    )


def determine_scoring_level(
    criteria_results: List[CriterionAssessment],
    pillar_term_hits: int,
    schema_criteria_hits: int,
    specificity: float,
    total_excerpts: int,
    has_metrics: bool,
    has_architecture_detail: bool,
    exclusion_hits: int,
    existing_score: float,
    existing_specificity: float,
) -> Tuple[int, str]:
    """Determine scoring level (0-5) anchored primarily on criteria assessment.

    Criteria coverage is the primary driver. How many of the sub-pillar's
    evaluation criteria (what_to_verify_publicly) are met by evidence determines
    the base level. Evidence quality signals can then raise or lower by at most
    one level, keeping the score firmly tied to criteria outcomes.

    Criteria coverage → base level:
      ≥85% met (4-5/5) → base 5
      ≥65% met (3-4/5) → base 4
      ≥45% met (2-3/5) → base 3
      ≥25% met (1-2/5) → base 2
      > 0%  (some partial) → base 1
      = 0%  no criteria met → based on presence signals only (max base 2)
    Evidence quality modifier: strong evidence with metrics/architecture can
    push +1 level; missing evidence penalises -1 level.
    """
    met_count = sum(1 for c in criteria_results if c.status == "met")
    partial_count = sum(1 for c in criteria_results if c.status == "partial")
    total_criteria = len(criteria_results)
    coverage = (met_count + partial_count * 0.5) / max(total_criteria, 1)

    v1_signal_strength = (
        min(existing_specificity / 5.0, 1.0) * 0.3 +
        min(pillar_term_hits / 8.0, 1.0) * 0.25 +
        min(schema_criteria_hits / 4.0, 1.0) * 0.25 +
        min(total_excerpts / 5.0, 1.0) * 0.2
    )

    justification_parts = []

    # Hard overrides
    if exclusion_hits > pillar_term_hits + schema_criteria_hits:
        justification_parts.append(f"Exclusion terms ({exclusion_hits}) outweigh positive signals.")
        return 1, " ".join(justification_parts)

    if total_excerpts == 0 and pillar_term_hits == 0 and schema_criteria_hits == 0:
        justification_parts.append("No evidence excerpts and no term matches found.")
        return 0, " ".join(justification_parts)

    # ── Primary: criteria-anchored base level ──────────────────────────
    if coverage >= 0.85:          # 4–5 of 5 criteria met
        base_level = 5
    elif coverage >= 0.65:        # 3–4 of 5 criteria met
        base_level = 4
    elif coverage >= 0.45:        # 2–3 of 5 criteria met
        base_level = 3
    elif coverage >= 0.25:        # 1–2 of 5 criteria met
        base_level = 2
    elif coverage > 0.0:          # only partial credit
        base_level = 1
    else:
        # Zero criteria met — cap at 2 based on general presence only
        if v1_signal_strength >= 0.5 and pillar_term_hits >= 6:
            base_level = 2   # Vendor is clearly in this space but criteria unverifiable
        elif v1_signal_strength >= 0.25 or pillar_term_hits >= 2 or total_excerpts >= 1:
            base_level = 1   # Minimal presence
        else:
            base_level = 0

    # ── Secondary: evidence quality modifier (±1 level, max 5) ─────────
    if (base_level >= 3 and v1_signal_strength >= 0.65
            and specificity >= 4.0 and (has_metrics or has_architecture_detail)):
        level = min(5, base_level + 1)
        justification_parts.append(
            f"Evidence-boosted: {met_count}/{total_criteria} criteria met, coverage={coverage:.0%}. "
            f"Strong evidence quality (signal={v1_signal_strength:.2f}, specificity={specificity:.1f}) "
            f"with {'metrics' if has_metrics else 'architecture detail'} elevated level "
            f"from {base_level} to {level}. "
            f"Schema hits: {schema_criteria_hits}, pillar hits: {pillar_term_hits}."
        )
    elif base_level >= 2 and total_excerpts == 0:
        level = max(1, base_level - 1)
        justification_parts.append(
            f"Evidence-penalized: {met_count}/{total_criteria} criteria met, coverage={coverage:.0%}. "
            f"No evidence excerpts; level reduced from {base_level} to {level}. "
            f"Signal={v1_signal_strength:.2f}, specificity={specificity:.1f}."
        )
    else:
        level = base_level
        signal_label = "Strong" if v1_signal_strength >= 0.6 else ("Moderate" if v1_signal_strength >= 0.35 else "Limited")
        justification_parts.append(
            f"{signal_label} evidence: {met_count}/{total_criteria} criteria met, coverage={coverage:.0%}. "
            f"V1 signal={v1_signal_strength:.2f}, specificity={specificity:.1f}. "
            f"Schema hits: {schema_criteria_hits}, pillar hits: {pillar_term_hits}. "
            f"Excerpts: {total_excerpts}."
        )

    return level, " ".join(justification_parts)


# Metric / architecture detection patterns
METRIC_PATTERNS = re.compile(
    r"\b(\d+\.?\d*\s*(%|percent|millisecond|ms|second|minute|latency|throughput|accuracy|precision|recall|f1|sla"
    r"|uptime|reduction|improvement|coverage|false.?positive|false.?negative|benchmark))"
    r"|\b(iso\s*\d|soc\s*\d|nist|fedramp|gdpr.compliant|hipaa.compliant|pci.dss)",
    re.IGNORECASE,
)

ARCHITECTURE_PATTERNS = re.compile(
    r"\b(api|sdk|rest|graphql|microservice|container|kubernetes|helm|terraform|ci/cd"
    r"|pipeline|webhook|plugin|connector|integration|real.?time|streaming|batch"
    r"|multi.?tenant|single.?tenant|on.?prem|cloud.?native|saas|paas|agent|orchestrat)",
    re.IGNORECASE,
)


def build_score_rationale(
    vendor_name: str,
    text_lower: str,
    all_excerpts: List[Dict],
    score: float,
    criteria_results: List[CriterionAssessment],
    level: int,
    level_justification: str,
    pillar_term_hits: int,
    schema_criteria_hits: int,
    specificity: float,
    source_count: int,
) -> str:
    met = [c for c in criteria_results if c.status == "met"]
    partial = [c for c in criteria_results if c.status == "partial"]
    unmet = [c for c in criteria_results if c.status == "unmet"]

    parts = []
    parts.append(f"{vendor_name} scores {score:.2f}/5.0 (Level {level}: {SCORING_LEVELS.get(level, 'Unknown')}).")
    parts.append(level_justification)

    if met:
        met_names = [c.criterion[:60] for c in met[:3]]
        parts.append(f"Criteria fully met ({len(met)}/{len(criteria_results)}): {'; '.join(met_names)}{'...' if len(met) > 3 else ''}.")

    if partial:
        partial_names = [c.criterion[:60] for c in partial[:2]]
        parts.append(f"Partially met ({len(partial)}): {'; '.join(partial_names)}.")

    if unmet:
        parts.append(f"Unmet criteria ({len(unmet)}): evidence gaps exist.")

    parts.append(f"Evidence basis: {len(all_excerpts)} excerpts from {source_count} source(s), "
                 f"{pillar_term_hits} pillar-term matches, {schema_criteria_hits} schema-criteria matches, "
                 f"specificity={specificity:.1f}.")

    return " ".join(parts)


def build_evidence_quality_rationale(
    evidence_block: Dict[str, Any],
    eq_analysis: Dict[str, Any],
    source_count: int,
    excerpt_count: int,
    criteria_met: int,
    criteria_total: int,
) -> str:
    quality = eq_analysis.get("quality_factor", 0.5)
    comps = eq_analysis.get("components", {})

    parts = []

    if quality >= 0.7:
        grade = "A (Strong)"
    elif quality >= 0.55:
        grade = "B (Good)"
    elif quality >= 0.4:
        grade = "C (Moderate)"
    else:
        grade = "D (Weak)"

    parts.append(f"Evidence quality: {quality:.1%} — Grade {grade}.")

    src_div = comps.get("source_diversity", 0)
    if src_div >= 0.7:
        parts.append(f"Source diversity is strong ({source_count} sources).")
    elif src_div >= 0.4:
        parts.append(f"Source diversity is moderate ({source_count} source(s)).")
    else:
        parts.append(f"Source diversity is weak ({source_count} source(s)).")

    vol = comps.get("evidence_volume", 0)
    if vol >= 0.7:
        parts.append(f"Volume is sufficient ({excerpt_count} excerpts).")
    elif vol >= 0.3:
        parts.append(f"Volume is moderate ({excerpt_count} excerpts).")
    else:
        parts.append(f"Volume is low ({excerpt_count} excerpts).")

    spec = comps.get("specificity_ratio", 0)
    if spec >= 0.5:
        parts.append(f"Term specificity is good ({spec:.2f}).")
    elif spec >= 0.2:
        parts.append(f"Term specificity is moderate ({spec:.2f}).")
    else:
        parts.append(f"Term specificity is low ({spec:.2f}).")

    con = comps.get("consistency", 0)
    if con >= 0.7:
        parts.append("Multiple sources corroborate the capability.")
    elif con >= 0.3:
        parts.append("Some cross-source confirmation exists.")
    else:
        parts.append("Limited cross-source confirmation.")

    parts.append(f"Schema criteria coverage: {criteria_met}/{criteria_total} met.")

    return " ".join(parts)


# ─────────────────────────────────────────────────────────────────────
# Per-vendor, per-sub-pillar analysis
# ─────────────────────────────────────────────────────────────────────

def analyse_sub_pillar(
    vendor_name: str,
    sid: str,
    sp_info: Dict[str, Any],
    evidence_block: Dict[str, Any],
    eq_analysis: Dict[str, Any],
    original_score: float,
    all_pages_text: List[Tuple[str, str]],
    pillar_terms: List[str],
) -> SubPillarRationale:
    """Deep analysis of a single sub-pillar for one vendor."""

    pillar = sid.split("-")[0]
    sp_name = sp_info.get("name", sid)
    criteria = sp_info.get("criteria", [])

    combined_text = " ".join(t for _, t in all_pages_text)
    text_lower = combined_text.lower()

    excerpts = evidence_block.get("excerpts", []) if evidence_block else []
    source_urls = evidence_block.get("source_urls", []) if evidence_block else []
    existing_specificity = evidence_block.get("sub_pillar_specificity", 0) if evidence_block else 0
    existing_schema_hits = evidence_block.get("schema_criteria_hits", 0) if evidence_block else 0
    existing_pillar_hits = evidence_block.get("pillar_term_hits", 0) if evidence_block else 0

    # 1. Re-assess each criterion
    criteria_results = []
    for criterion in criteria:
        assessment = assess_criterion(criterion, combined_text, excerpts)
        criteria_results.append(assessment)

    # 2. Count term hits
    pillar_terms_set = set(PILLAR_SPECIFIC_TERMS.get(pillar, []))
    pillar_term_hits = sum(1 for t in pillar_terms_set if _term_in_text(t, text_lower))

    schema_term_hits = 0
    for criterion in criteria:
        crit_lower = criterion.lower().strip()
        if len(crit_lower) >= 8:
            # Only match full phrases — do NOT split into individual words
            # (individual word matching inflates scores for generic terms)
            if _term_in_text(crit_lower, text_lower) or crit_lower in text_lower:
                schema_term_hits += 1

    # 3. Check metrics and architecture
    has_metrics = bool(METRIC_PATTERNS.search(combined_text))
    has_architecture = bool(ARCHITECTURE_PATTERNS.search(combined_text))

    exclusion_hits = sum(1 for t in PRECYBER_EXCLUSION_TERMS if t in text_lower)

    # 4. Compute specificity
    precyber_hits = sum(1 for t in PRECYBER_PRIMARY_TERMS if _term_in_text(t.lower(), text_lower))
    if precyber_hits == 0:
        specificity = 0.0
    elif precyber_hits <= 3:
        specificity = 1.5
    elif precyber_hits <= 8:
        specificity = 2.5
    elif precyber_hits <= 15:
        specificity = 3.5
    elif precyber_hits <= 25:
        specificity = 4.0
    else:
        specificity = 5.0

    # 5. Determine scoring level
    level, level_justification = determine_scoring_level(
        criteria_results=criteria_results,
        pillar_term_hits=pillar_term_hits,
        schema_criteria_hits=schema_term_hits,
        specificity=specificity,
        total_excerpts=len(excerpts),
        has_metrics=has_metrics,
        has_architecture_detail=has_architecture,
        exclusion_hits=exclusion_hits,
        existing_score=original_score,
        existing_specificity=existing_specificity,
    )

    # 6. Find top evidence
    best_evidence: List[str] = []
    for ex in sorted(excerpts, key=lambda e: e.get("relevance_score", 0), reverse=True)[:3]:
        text_snippet = ex.get("excerpt", "")[:200]
        if text_snippet:
            best_evidence.append(text_snippet)

    for criterion in criteria[:3]:
        crit_words = [w for w in criterion.lower().split() if len(w) >= 5]
        for sent in _split_sentences(combined_text):
            if len(best_evidence) >= 5:
                break
            sent_lower = sent.lower()
            hits = sum(1 for w in crit_words if w in sent_lower)
            if hits >= 2 and sent[:200] not in best_evidence:
                best_evidence.append(sent[:200])

    # 7. Compute adjusted score
    met_count = sum(1 for c in criteria_results if c.status == "met")
    partial_count = sum(1 for c in criteria_results if c.status == "partial")
    total_criteria = len(criteria_results)

    base_from_analysis = float(level)

    if total_criteria > 0:
        sub_level_boost = (met_count + partial_count * 0.3) / total_criteria
        adjusted = base_from_analysis + (sub_level_boost * 0.75)
    else:
        adjusted = base_from_analysis

    if has_metrics and level >= 3:
        adjusted += 0.15
    if has_architecture and level >= 3:
        adjusted += 0.10

    adjusted = min(5.0, max(0.0, adjusted))
    adjusted = round(adjusted * 4) / 4  # Round to 0.25

    # 8. Compare with original — cap adjustment at ±1.5 (only for re-scoring vendors with a prior score)
    MAX_ADJUSTMENT = 1.5
    score_diff = adjusted - original_score
    if original_score == 0.0:
        # Fresh scoring — no prior validated score exists; use analysis result directly
        adj_reason = (f"Fresh score {adjusted:.2f}: no prior validated score "
                     f"({met_count}/{total_criteria} criteria met, level={level}).")
    elif abs(score_diff) >= 0.5:
        if abs(score_diff) > MAX_ADJUSTMENT:
            adjusted = original_score + (MAX_ADJUSTMENT if score_diff > 0 else -MAX_ADJUSTMENT)
            adjusted = round(adjusted * 4) / 4  # re-snap to 0.25
            adjusted = min(5.0, max(0.0, adjusted))
        if adjusted > original_score:
            adj_reason = (f"Score increased from {original_score:.2f} to {adjusted:.2f}: "
                         f"deeper analysis found stronger evidence ({met_count}/{total_criteria} criteria met).")
        else:
            adj_reason = (f"Score decreased from {original_score:.2f} to {adjusted:.2f}: "
                         f"rationale analysis found weaker support ({met_count}/{total_criteria} criteria met).")
    else:
        adjusted = original_score
        adj_reason = f"Score confirmed at {original_score:.2f} — rationale analysis supports current score (level={level}, diff={score_diff:.2f})."

    # 9. Build rationales
    source_count = len(set(source_urls))

    score_rationale = build_score_rationale(
        vendor_name=vendor_name,
        text_lower=text_lower,
        all_excerpts=excerpts,
        score=adjusted,
        criteria_results=criteria_results,
        level=level,
        level_justification=level_justification,
        pillar_term_hits=pillar_term_hits,
        schema_criteria_hits=schema_term_hits,
        specificity=specificity,
        source_count=source_count,
    )

    evidence_quality_rationale = build_evidence_quality_rationale(
        evidence_block=evidence_block or {},
        eq_analysis=eq_analysis or {},
        source_count=source_count,
        excerpt_count=len(excerpts),
        criteria_met=met_count,
        criteria_total=total_criteria,
    )

    if met_count >= total_criteria * 0.6 and source_count >= 2:
        confidence = "high"
    elif met_count >= total_criteria * 0.3 or source_count >= 1:
        confidence = "medium"
    else:
        confidence = "low"

    return SubPillarRationale(
        sid=sid,
        name=sp_name,
        original_score=original_score,
        adjusted_score=adjusted,
        scoring_level=level,
        score_rationale=score_rationale,
        evidence_quality_rationale=evidence_quality_rationale,
        criteria_assessment=criteria_results,
        scoring_level_justification=level_justification,
        key_evidence=best_evidence[:5],
        score_adjustment_reason=adj_reason,
        additional_sources_found=0,
        confidence=confidence,
        evidence_quality_factor=eq_analysis.get("quality_factor", 0.5) if eq_analysis else 0.5,
    )


# ─────────────────────────────────────────────────────────────────────
# Full vendor analysis
# ─────────────────────────────────────────────────────────────────────

def analyse_vendor(
    vendor: Dict[str, Any],
    schema_body: Dict[str, Any],
    *,
    fetch_additional: bool = True,
    sleep_seconds: float = 1.0,
) -> Dict[str, Any]:
    """Complete rationale analysis for one vendor across all sub-pillars."""

    vendor_name = vendor.get("vendor", "Unknown")

    # Gather all existing evidence URLs
    evidence = vendor.get("sub_pillar_evidence", {})
    all_urls: List[str] = []
    seen_urls: Set[str] = set()

    for sid in SUBPILLAR_IDS:
        ev_block = evidence.get(sid, {})
        for u in ev_block.get("source_urls", []):
            if u.lower().rstrip("/") not in seen_urls:
                seen_urls.add(u.lower().rstrip("/"))
                all_urls.append(u)

    # Add curated URLs
    if vendor_name in VENDOR_URLS:
        for u in VENDOR_URLS[vendor_name]:
            if u.lower().rstrip("/") not in seen_urls:
                seen_urls.add(u.lower().rstrip("/"))
                all_urls.append(u)

    # Discover additional URLs
    additional_found = 0
    if fetch_additional and all_urls:
        additional = discover_additional_urls(vendor_name, all_urls)
        for u in additional:
            if u.lower().rstrip("/") not in seen_urls:
                seen_urls.add(u.lower().rstrip("/"))
                all_urls.append(u)
                additional_found += 1

    # Fetch all pages
    pages_text: List[Tuple[str, str]] = []
    for url in all_urls:
        was_cached = _cache_path_for_url(url).exists()
        try:
            rec = get_or_fetch_page_local(url, force=False)
            if rec.get("ok") is True and isinstance(rec.get("text"), str):
                pages_text.append((rec["url"], rec["text"]))
        except KeyboardInterrupt:
            raise
        except Exception:
            pass
        if not was_cached:
            time.sleep(sleep_seconds + random.uniform(0.3, 1.0))

    ok_pages = len(pages_text)

    # Get existing scores
    validated_scores = vendor.get("sub_pillar_scores_validated", {})
    eq_analysis_all = vendor.get("evidence_quality_analysis", {})

    # Analyse each sub-pillar
    rationale_results: Dict[str, SubPillarRationale] = {}

    for sid in SUBPILLAR_IDS:
        sp_info = get_sub_pillar_info(schema_body, sid)
        ev_block = evidence.get(sid, {})

        # Compute evidence quality for this sub-pillar
        eq_block = compute_evidence_quality(ev_block) if ev_block else {}

        original_score = validated_scores.get(sid, 0)

        pillar = sid.split("-")[0]
        pillar_terms = PILLAR_SPECIFIC_TERMS.get(pillar, [])

        rationale = analyse_sub_pillar(
            vendor_name=vendor_name,
            sid=sid,
            sp_info=sp_info,
            evidence_block=ev_block,
            eq_analysis=eq_block,
            original_score=original_score,
            all_pages_text=pages_text,
            pillar_terms=pillar_terms,
        )
        rationale.additional_sources_found = additional_found
        rationale_results[sid] = rationale

    return {
        "vendor_name": vendor_name,
        "pages_fetched": ok_pages,
        "total_urls": len(all_urls),
        "additional_sources_found": additional_found,
        "rationale_results": rationale_results,
    }


def rationale_to_dict(r: SubPillarRationale) -> Dict[str, Any]:
    return {
        "sub_pillar_id": r.sid,
        "sub_pillar_name": r.name,
        "original_score": r.original_score,
        "adjusted_score": r.adjusted_score,
        "scoring_level": r.scoring_level,
        "score_rationale": r.score_rationale,
        "evidence_quality_rationale": r.evidence_quality_rationale,
        "criteria_assessment": [
            {
                "criterion": ca.criterion,
                "status": ca.status,
                "evidence": ca.evidence,
                "confidence": ca.confidence,
            }
            for ca in r.criteria_assessment
        ],
        "scoring_level_justification": r.scoring_level_justification,
        "key_evidence": r.key_evidence,
        "score_adjustment": {
            "original": r.original_score,
            "adjusted": r.adjusted_score,
            "reason": r.score_adjustment_reason,
        },
        "additional_sources_found": r.additional_sources_found,
        "confidence": r.confidence,
        "evidence_quality_factor": r.evidence_quality_factor,
    }


# ─────────────────────────────────────────────────────────────────────
# Main pipeline
# ─────────────────────────────────────────────────────────────────────

def _save_output(data: dict, output_path: Path, vendors_processed: int,
                 total: int, stats: dict) -> None:
    output_data = dict(data)
    output_data["v2_research_metadata"] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script": "research_precyber_v2_rationale.py",
        "vendors_processed": vendors_processed,
        "total_vendors": total,
        "score_adjustments": {
            "increased": stats["increases"],
            "decreased": stats["decreases"],
            "unchanged": stats["unchanged"],
        },
    }
    output_path.write_text(
        json.dumps(output_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(
        description="PreCyber v2 — Scoring Rationale & Evidence Quality Analysis")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--max-vendors", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-fetch", action="store_true")
    parser.add_argument("--sleep", type=float, default=1.0)
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--force-reprocess", action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        print(f"  Input file not found: {input_path}")
        sys.exit(1)

    data = json.loads(input_path.read_text(encoding="utf-8"))
    vendors = data.get("vendors", [])

    # Resume support
    already_done: Set[str] = set()
    if output_path.exists() and not args.force_reprocess:
        try:
            existing = json.loads(output_path.read_text(encoding="utf-8"))
            existing_vendors = {v.get("vendor"): v for v in existing.get("vendors", [])}
            for vendor in vendors:
                vname = vendor.get("vendor")
                ev = existing_vendors.get(vname, {})
                if (ev.get("sub_pillar_rationale_v2")
                        and ev.get("sub_pillar_scores_v2_researched")
                        and len(ev["sub_pillar_scores_v2_researched"]) == 16):
                    vendor["sub_pillar_rationale_v2"] = ev["sub_pillar_rationale_v2"]
                    vendor["sub_pillar_scores_v2_researched"] = ev["sub_pillar_scores_v2_researched"]
                    vendor["pillar_scores_v2_researched"] = ev.get("pillar_scores_v2_researched", {})
                    vendor["evidence_quality_analysis"] = ev.get("evidence_quality_analysis", {})
                    already_done.add(vname)
        except Exception:
            pass

    schema_body = load_schema()

    total = len(vendors)
    if args.max_vendors > 0:
        vendors = vendors[:args.max_vendors]

    to_process = [(i, v) for i, v in enumerate(vendors)
                  if v.get("vendor") not in already_done]

    print("=" * 70)
    print("  PreCyber v2 — Scoring Rationale & Evidence Quality Analysis")
    print(f"  Input:  {input_path.name}")
    print(f"  Output: {output_path.name}")
    print(f"  Mode:   {'DRY RUN' if args.dry_run else 'WRITE'}")
    print(f"  Fetch:  {'Full discovery + fetch' if not args.no_fetch else 'Cache-first'}")
    print(f"  Batch:  Save every {args.batch_size} vendors")
    if already_done:
        print(f"  Resume: {len(already_done)} already done, {len(to_process)} remaining")
    print("=" * 70)
    print(f"\n  Processing {len(to_process)} of {len(vendors)} vendors...\n")

    stats = {"increases": 0, "decreases": 0, "unchanged": 0}
    total_sps = 0
    confidence_counts = {"high": 0, "medium": 0, "low": 0}
    processed_in_session = 0
    errors = []

    for batch_start in range(0, len(to_process), args.batch_size):
        batch = to_process[batch_start:batch_start + args.batch_size]

        for vi_idx, (orig_idx, vendor) in enumerate(batch, batch_start + 1):
            vendor_name = vendor.get("vendor", "Unknown")

            try:
                result = analyse_vendor(
                    vendor,
                    schema_body,
                    fetch_additional=not args.no_fetch,
                    sleep_seconds=args.sleep,
                )
            except Exception as exc:
                errors.append(vendor_name)
                print(f"  [{vi_idx:3d}/{len(to_process)}] {vendor_name:<38s} ERROR: {exc}")
                continue

            new_rationale = {}
            new_scores = {}
            new_pillar_scores = {}
            new_eq_analysis = {}
            adjustments = []

            for sid, rat in result["rationale_results"].items():
                new_rationale[sid] = rationale_to_dict(rat)
                new_scores[sid] = rat.adjusted_score
                total_sps += 1
                confidence_counts[rat.confidence] = confidence_counts.get(rat.confidence, 0) + 1

                # Compute evidence quality for storage
                ev_block = vendor.get("sub_pillar_evidence", {}).get(sid, {})
                new_eq_analysis[sid] = compute_evidence_quality(ev_block)

                if rat.adjusted_score > rat.original_score:
                    stats["increases"] += 1
                    adjustments.append(f"  + {sid}: {rat.original_score:.2f}->{rat.adjusted_score:.2f}")
                elif rat.adjusted_score < rat.original_score:
                    stats["decreases"] += 1
                    adjustments.append(f"  - {sid}: {rat.original_score:.2f}->{rat.adjusted_score:.2f}")
                else:
                    stats["unchanged"] += 1

            for pillar in PILLARS:
                sp_ids = [f"{pillar}-{i:02d}" for i in range(1, 5)]
                sp_scores = [new_scores[s] for s in sp_ids if s in new_scores]
                if sp_scores:
                    new_pillar_scores[pillar] = round(sum(sp_scores) / len(sp_scores), 2)

            overall = sum(new_pillar_scores.values()) / max(len(new_pillar_scores), 1)
            adj_count = len(adjustments)

            adj_text = f"{adj_count} adjusted" if adj_count > 0 else "no changes"
            print(f"  [{vi_idx:3d}/{len(to_process)}] {vendor_name:<38s} Score={overall:.2f} ({adj_text}, "
                  f"{result['pages_fetched']} pages, +{result['additional_sources_found']} new)")
            for a in adjustments:
                print(f"           {a}")

            vendor["sub_pillar_rationale_v2"] = new_rationale
            vendor["sub_pillar_scores_v2_researched"] = new_scores
            vendor["pillar_scores_v2_researched"] = new_pillar_scores
            vendor["evidence_quality_analysis"] = new_eq_analysis
            # Also update current/display scores
            vendor["sub_pillar_scores_current"] = new_scores
            vendor["pillar_scores"] = new_pillar_scores
            processed_in_session += 1

        if not args.dry_run:
            _save_output(data, output_path, len(already_done) + processed_in_session,
                         total, stats)
            print(f"  Batch saved ({len(already_done) + processed_in_session}/{len(vendors)} complete)\n")

    # Summary
    print(f"\n{'=' * 70}")
    print("  PRECYBER RATIONALE ANALYSIS SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Total vendors:              {total}")
    print(f"  Already done (resumed):     {len(already_done)}")
    print(f"  Processed this session:     {processed_in_session}")
    print(f"  Errors (skipped):           {len(errors)}")
    print(f"  Total sub-pillars analysed: {total_sps}")
    print(f"  Score adjustments:")
    print(f"    Increased:  {stats['increases']}")
    print(f"    Decreased:  {stats['decreases']}")
    print(f"    Unchanged:  {stats['unchanged']}")
    print(f"  Confidence distribution:")
    print(f"    High:   {confidence_counts.get('high', 0)}")
    print(f"    Medium: {confidence_counts.get('medium', 0)}")
    print(f"    Low:    {confidence_counts.get('low', 0)}")

    if errors:
        print(f"\n  Vendors with errors (re-run to retry):")
        for e in errors:
            print(f"    - {e}")

    if args.dry_run:
        print(f"\n  DRY RUN — no files written.")
    else:
        _save_output(data, output_path, len(already_done) + processed_in_session,
                     total, stats)
        print(f"\n  Saved to {output_path}")


if __name__ == "__main__":
    main()
