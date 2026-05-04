"""
research_trism_v2_rationale.py — AI TRiSM Scoring Rationale & Evidence Quality Analysis

Reads AI TRiSM Vendor 1-1 Validated.json and for each vendor / sub-pillar:
  1. Re-analyses ALL cached page content (from v1 research run)
  2. Searches for ADDITIONAL public pages (governance/security/privacy pages)
  3. Matches evidence against schema evaluation criteria
  4. Produces a structured scoring rationale explaining WHY the score is what it is
  5. Documents evidence quality factors (source diversity, specificity, depth)
  6. Adjusts scores when the rationale justifies a change (up or down)
  7. Writes output to "AI TRiSM Vendor 2-0 Researched.json" — new file, no modification of 1-1

Rationale structure per sub-pillar:
  {
    "score_rationale": "Detailed paragraph explaining why this score...",
    "evidence_quality_rationale": "Why evidence quality is graded X...",
    "criteria_assessment": { "criterion_text": "met|partial|unmet", ... },
    "scoring_level_justification": "Maps to level N because...",
    "key_evidence": ["most relevant excerpt 1", ...],
    "score_adjustment": { "original": 4.25, "adjusted": 4.0, "reason": "..." },
    "additional_sources_found": 2,
    "confidence": "high|medium|low"
  }

Usage:
  python research_trism_v2_rationale.py                      # full run
  python research_trism_v2_rationale.py --max-vendors 3      # test with 3
  python research_trism_v2_rationale.py --dry-run             # show without writing
  python research_trism_v2_rationale.py --no-fetch            # skip new URL discovery
"""

import argparse
import hashlib
import json
import random
import re
import sys
import textwrap
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

DEFAULT_INPUT  = ROOT / "AI TRiSM Vendor 1-1 Validated.json"
DEFAULT_OUTPUT = ROOT / "AI TRiSM Vendor 2-0 Researched.json"
SCHEMA_FILE    = ROOT / "AI TriSM Schema 1_0.json"

CACHE_DIR = ROOT / "research" / "cache" / "pages_trism"

PILLARS = ["GOV", "RUN", "INF"]
SUBPILLAR_IDS = [f"{p}-{i:02d}" for p in PILLARS for i in range(1, 5)]

# Scoring level descriptions — from schema but summarised for rationale
SCORING_LEVELS = {
    0: "No Evidence — No public material found relevant to this sub-pillar.",
    1: "No AI / Manual — Vendor has policy/process material but no AI/ML capability for this area.",
    2: "Generic AI Claims — Marketing mentions AI but without specifics; no measurable capabilities.",
    3: "AI-Augmented — Documented AI features with some technical detail; may lack measurables.",
    4: "Advanced AI — Measurable AI capabilities with evidence; specific metrics or architecture details.",
    5: "Fully Agentic / Best-in-Class — Autonomous, well-documented AI with benchmarks and proof points.",
}

# ─────────────────────────────────────────────────────────────────────
# Import synonym & term matching from v1
# ─────────────────────────────────────────────────────────────────────

from research_trism_v1_claims import (
    TRISM_PRIMARY_TERMS,
    TRISM_EXCLUSION_TERMS,
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


def _fetch_url_with_retry(url: str, retries: int = 2) -> Tuple[Optional[str], Optional[str]]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                ctype = resp.headers.get("Content-Type", "")
                raw = resp.read(500_000)
                encoding = "utf-8"
                if "charset=" in ctype:
                    encoding = ctype.split("charset=")[-1].split(";")[0].strip()
                return ctype, raw.decode(encoding, errors="replace")
        except urllib.error.HTTPError as he:
            # HTTP 4xx/5xx — don't retry client errors (404 etc), only retry server errors
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


def _cache_path_for_url(url: str) -> Path:
    # Use sha1 to match v1 cache filenames (research_trism_v1_claims.py)
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
# Schema loader
# ─────────────────────────────────────────────────────────────────────

def load_schema() -> Dict[str, Any]:
    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    for key in schema:
        if key.startswith("ai_trism_taxonomy"):
            return schema[key]
    return schema


def get_sub_pillar_info(schema_body: Dict[str, Any], sid: str) -> Dict[str, Any]:
    """Get name, definition, criteria, scoring levels for a sub-pillar."""
    subs = schema_body.get("sub_pillars", {})
    info = subs.get(sid, {})
    return {
        "name": info.get("name", sid),
        "definition": info.get("definition", ""),
        "criteria": info.get("ai_evaluation_criteria", []),
        "scoring_levels": info.get("scoring_levels", {}),
    }


# ─────────────────────────────────────────────────────────────────────
# Additional URL discovery — find vendor pages we may have missed
# ─────────────────────────────────────────────────────────────────────

# Sub-pillar to search query suffixes
PILLAR_SEARCH_SUFFIXES = {
    "GOV": ["ai governance", "responsible ai", "ai ethics", "model governance", "ai risk management"],
    "RUN": ["ai security", "llm guardrails", "prompt injection protection", "ai runtime", "content safety"],
    "INF": ["data governance", "data classification", "data privacy", "data security posture", "dlp"],
}


def discover_additional_urls(vendor_name: str, existing_urls: List[str]) -> List[str]:
    """Try to find additional vendor pages from their existing evidence URLs.
    
    Strategy: Take the base domain from existing URLs and try common paths
    like /ai, /governance, /security, /privacy, /trust, /responsible-ai
    """
    additional: List[str] = []
    seen = {u.lower().rstrip("/") for u in existing_urls}

    # Extract base domains from existing source URLs
    domains: Set[str] = set()
    for url in existing_urls:
        match = re.match(r"https?://([^/]+)", url)
        if match:
            domains.add(match.group(1))

    # Common paths for AI TRiSM-relevant content
    additional_paths = [
        "/ai", "/ai-governance", "/responsible-ai", "/ai-ethics",
        "/trust", "/trust-center", "/security", "/ai-security",
        "/privacy", "/data-governance", "/data-security",
        "/compliance", "/ai-compliance", "/solutions/ai",
        "/platform/ai", "/products/ai", "/services/ai",
        "/ai-safety", "/guardrails", "/llm-security",
    ]

    for domain in domains:
        for path in additional_paths:
            candidate = f"https://{domain}{path}"
            if candidate.lower().rstrip("/") not in seen:
                additional.append(candidate)
                seen.add(candidate.lower().rstrip("/"))

    return additional[:15]  # Cap at 15 additional discovery URLs


# ─────────────────────────────────────────────────────────────────────
# Core analysis engine
# ─────────────────────────────────────────────────────────────────────

@dataclass
class CriterionAssessment:
    """Assessment of a single evaluation criterion."""
    criterion: str
    status: str  # "met", "partial", "unmet"
    evidence: str  # supporting excerpt or explanation
    confidence: str  # "high", "medium", "low"


@dataclass
class SubPillarRationale:
    """Complete rationale for a sub-pillar score."""
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
    confidence: str  # "high", "medium", "low"
    evidence_quality_factor: float


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def assess_criterion(criterion: str, all_text: str, excerpts: List[Dict]) -> CriterionAssessment:
    """Assess whether a specific evaluation criterion is met by the evidence.
    
    Uses conceptual matching: decomposes the criterion into key concepts
    and checks if those concepts appear in the evidence, rather than
    requiring exact phrase matches.
    """
    criterion_lower = _normalise(criterion)
    
    # Extract meaningful concept words (≥4 chars, not stopwords)
    stop_extra = {"with", "that", "from", "into", "each", "also",
                  "this", "have", "been", "does", "more", "than",
                  "very", "will", "when", "what", "your", "they",
                  "based", "such", "only", "over", "both", "most",
                  "some", "well", "make", "like", "just", "take",
                  "across", "specific", "per"}
    
    key_words = [w for w in criterion_lower.split() 
                 if len(w) >= 4 and w not in stop_extra]
    
    # Also check for synonym expansions on key concept pairs
    concept_pairs = []
    for i in range(len(key_words) - 1):
        pair = f"{key_words[i]} {key_words[i+1]}"
        concept_pairs.append(pair)
    
    text_lower = all_text.lower()
    
    # Direct word hits in full text
    word_hits = sum(1 for w in key_words if w in text_lower)
    word_coverage = word_hits / max(len(key_words), 1)
    
    # Concept pair hits (2-word phrases from criterion)
    pair_hits = sum(1 for p in concept_pairs if p in text_lower)
    
    # Synonym-aware concept hits
    synonym_hits = 0
    for w in key_words:
        if _term_in_text(w, text_lower) and w not in text_lower:
            synonym_hits += 1
    
    total_concept_coverage = (word_hits + synonym_hits) / max(len(key_words), 1)
    
    # Find the best matching excerpt
    best_excerpt = ""
    best_excerpt_score = 0
    for ex in excerpts:
        ex_text = (ex.get("excerpt", "") or "").lower()
        ex_hits = sum(1 for w in key_words if w in ex_text)
        if ex_hits > best_excerpt_score:
            best_excerpt_score = ex_hits
            best_excerpt = ex.get("excerpt", "")[:200]
    
    # Also search full text for better-matching sentences
    sentences = _split_sentences(all_text)
    for sent in sentences:
        sent_lower = sent.lower()
        sent_hits = sum(1 for w in key_words if w in sent_lower)
        if sent_hits > best_excerpt_score:
            best_excerpt_score = sent_hits
            best_excerpt = sent[:200]
    
    # Determine status — more generous thresholds for conceptual matching
    if total_concept_coverage >= 0.5 and (pair_hits >= 1 or best_excerpt_score >= 2):
        status = "met"
        confidence = "high" if total_concept_coverage >= 0.7 else "medium"
    elif total_concept_coverage >= 0.3 or best_excerpt_score >= 2 or pair_hits >= 1:
        status = "partial"
        confidence = "medium"
    elif word_hits >= 1:
        status = "partial"
        confidence = "low"
    else:
        status = "unmet"
        confidence = "high" if word_coverage == 0 else "medium"
    
    evidence_note = best_excerpt if best_excerpt else f"No direct evidence found ({word_hits}/{len(key_words)} key terms in corpus)"
    
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
    """Determine the appropriate scoring level (0-5) with justification.
    
    Uses existing v1 evidence signals (specificity, hits, excerpts) as anchors
    alongside the new criteria assessment. The existing score is factored in
    as a prior — we need strong evidence to deviate significantly.
    """
    
    met_count = sum(1 for c in criteria_results if c.status == "met")
    partial_count = sum(1 for c in criteria_results if c.status == "partial")
    unmet_count = sum(1 for c in criteria_results if c.status == "unmet")
    total_criteria = len(criteria_results)
    met_ratio = met_count / max(total_criteria, 1)
    coverage = (met_count + partial_count * 0.5) / max(total_criteria, 1)
    
    # Combined signal strength from v1 research
    v1_signal_strength = (
        min(existing_specificity / 5.0, 1.0) * 0.3 +
        min(pillar_term_hits / 8.0, 1.0) * 0.25 +
        min(schema_criteria_hits / 4.0, 1.0) * 0.25 +
        min(total_excerpts / 5.0, 1.0) * 0.2
    )
    
    justification_parts = []
    
    # ── Exclusion override ──
    if exclusion_hits > pillar_term_hits + schema_criteria_hits:
        justification_parts.append(f"Exclusion terms ({exclusion_hits}) outweigh positive signals.")
        return 1, " ".join(justification_parts)
    
    # ── No evidence at all ──
    if total_excerpts == 0 and pillar_term_hits == 0 and schema_criteria_hits == 0:
        justification_parts.append("No evidence excerpts and no term matches found.")
        return 0, " ".join(justification_parts)
    
    # ── Level 5: Fully Agentic ──
    if (v1_signal_strength >= 0.7 and coverage >= 0.6
            and schema_criteria_hits >= 3 and (has_metrics or has_architecture_detail)
            and specificity >= 4.0):
        justification_parts.append(
            f"Strong evidence: {met_count}/{total_criteria} criteria met, coverage={coverage:.0%}. "
            f"V1 signal={v1_signal_strength:.2f}, specificity={specificity:.1f}. "
            f"{'Has metrics. ' if has_metrics else ''}{'Has architecture detail. ' if has_architecture_detail else ''}"
            f"Schema hits: {schema_criteria_hits}, pillar hits: {pillar_term_hits}."
        )
        return 5, " ".join(justification_parts)
    
    # ── Level 4: Advanced AI ──
    if (v1_signal_strength >= 0.5 and coverage >= 0.4
            and (schema_criteria_hits >= 2 or pillar_term_hits >= 4)
            and specificity >= 3.0):
        justification_parts.append(
            f"Good evidence: {met_count}/{total_criteria} criteria met, coverage={coverage:.0%}. "
            f"V1 signal={v1_signal_strength:.2f}, specificity={specificity:.1f}. "
            f"{'Has metrics. ' if has_metrics else ''}{'Has architecture details. ' if has_architecture_detail else ''}"
            f"Schema hits: {schema_criteria_hits}, pillar hits: {pillar_term_hits}."
        )
        return 4, " ".join(justification_parts)
    
    # ── Level 3: AI-Augmented ──
    if (v1_signal_strength >= 0.3 and
            (coverage >= 0.2 or pillar_term_hits >= 2 or schema_criteria_hits >= 1)):
        justification_parts.append(
            f"Moderate evidence: coverage={coverage:.0%}, "
            f"V1 signal={v1_signal_strength:.2f}. "
            f"Pillar terms: {pillar_term_hits}, schema criteria: {schema_criteria_hits}. "
            f"AI features documented but may lack quantitative proof."
        )
        return 3, " ".join(justification_parts)
    
    # ── Level 2: Generic AI Claims ──
    if pillar_term_hits >= 1 or specificity >= 1.5 or total_excerpts >= 1:
        justification_parts.append(
            f"Limited evidence: {pillar_term_hits} pillar terms, specificity={specificity:.1f}. "
            f"Marketing-level AI claims without substantive depth. "
            f"{total_excerpts} excerpt(s) found."
        )
        return 2, " ".join(justification_parts)
    
    # ── Level 1: No AI ──
    if total_excerpts > 0:
        justification_parts.append(
            f"Found {total_excerpts} excerpt(s) but no pillar-specific or schema matches. "
            f"Content appears to be policy/process without AI capability."
        )
        return 1, " ".join(justification_parts)
    
    return 0, "No relevant public evidence found for this sub-pillar."


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
    """Build a human-readable scoring rationale paragraph."""
    
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
        parts.append(f"Unmet criteria ({len(unmet)}): evidence gaps exist{'; specific gaps: ' + '; '.join(c.criterion[:50] for c in unmet[:2]) if len(unmet) <= 3 else ''}.")
    
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
    """Explain why evidence quality is what it is."""
    
    quality = eq_analysis.get("quality_factor", 0.5)
    comps = eq_analysis.get("components", {})
    
    parts = []
    
    # Overall grade
    if quality >= 0.7:
        grade = "A (Strong)"
    elif quality >= 0.55:
        grade = "B (Good)"
    elif quality >= 0.4:
        grade = "C (Moderate)"
    else:
        grade = "D (Weak)"
    
    parts.append(f"Evidence quality: {quality:.1%} — Grade {grade}.")
    
    # Source diversity
    src_div = comps.get("source_diversity", 0)
    if src_div >= 0.7:
        parts.append(f"Source diversity is strong ({source_count} sources, factor={src_div:.2f}).")
    elif src_div >= 0.4:
        parts.append(f"Source diversity is moderate ({source_count} source(s), factor={src_div:.2f}); additional independent sources would strengthen this.")
    else:
        parts.append(f"Source diversity is weak ({source_count} source(s), factor={src_div:.2f}); evidence relies on very few or single-source data.")
    
    # Evidence volume
    vol = comps.get("evidence_volume", 0)
    if vol >= 0.7:
        parts.append(f"Volume is sufficient ({excerpt_count} excerpts).")
    elif vol >= 0.3:
        parts.append(f"Volume is moderate ({excerpt_count} excerpts); more supporting material would help.")
    else:
        parts.append(f"Volume is low ({excerpt_count} excerpts); limited material found.")
    
    # Specificity
    spec = comps.get("specificity_ratio", 0)
    if spec >= 0.5:
        parts.append(f"Term specificity is good ({spec:.2f}); evidence uses domain-specific language.")
    elif spec >= 0.2:
        parts.append(f"Term specificity is moderate ({spec:.2f}); mix of generic and specific terms.")
    else:
        parts.append(f"Term specificity is low ({spec:.2f}); evidence language is mostly generic.")
    
    # Consistency
    con = comps.get("consistency", 0)
    if con >= 0.7:
        parts.append("Multiple independent sources corroborate the capability.")
    elif con >= 0.3:
        parts.append("Some cross-source confirmation exists.")
    else:
        parts.append("Limited cross-source confirmation; findings rely on single source.")
    
    # Criteria coverage
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
    scoring_levels_schema = sp_info.get("scoring_levels", {})
    
    # Combine all page text
    combined_text = " ".join(t for _, t in all_pages_text)
    text_lower = combined_text.lower()
    
    # Get existing evidence excerpts
    excerpts = evidence_block.get("excerpts", []) if evidence_block else []
    source_urls = evidence_block.get("source_urls", []) if evidence_block else []
    existing_specificity = evidence_block.get("sub_pillar_specificity", 0) if evidence_block else 0
    existing_schema_hits = evidence_block.get("schema_criteria_hits", 0) if evidence_block else 0
    existing_pillar_hits = evidence_block.get("pillar_term_hits", 0) if evidence_block else 0
    
    # ── 1. Re-assess each criterion against ALL available text ──
    criteria_results = []
    for criterion in criteria:
        assessment = assess_criterion(criterion, combined_text, excerpts)
        criteria_results.append(assessment)
    
    # ── 2. Count pillar & schema term hits (with synonyms) ──
    pillar_terms_set = set(PILLAR_SPECIFIC_TERMS.get(pillar, []))
    pillar_term_hits = sum(1 for t in pillar_terms_set if _term_in_text(t, text_lower))
    
    # Schema criteria as search terms
    schema_term_hits = 0
    for criterion in criteria:
        crit_lower = criterion.lower().strip()
        if len(crit_lower) >= 8:
            if _term_in_text(crit_lower, text_lower) or crit_lower in text_lower:
                schema_term_hits += 1
            else:
                # Check significant words from criterion
                crit_words = [w for w in crit_lower.split() if len(w) >= 5]
                if sum(1 for w in crit_words if w in text_lower) >= len(crit_words) * 0.5:
                    schema_term_hits += 1
    
    # ── 3. Check for metrics and architecture detail ──
    has_metrics = bool(METRIC_PATTERNS.search(combined_text))
    has_architecture = bool(ARCHITECTURE_PATTERNS.search(combined_text))
    
    # Detect exclusion terms
    exclusion_hits = sum(1 for t in TRISM_EXCLUSION_TERMS if t in text_lower)
    
    # ── 4. Compute specificity ──
    trism_term_hits = sum(1 for t in TRISM_PRIMARY_TERMS if _term_in_text(t, text_lower))
    if trism_term_hits == 0:
        specificity = 0.0
    elif trism_term_hits <= 2:
        specificity = 2.0
    elif trism_term_hits <= 5:
        specificity = 3.0
    elif trism_term_hits <= 10:
        specificity = 4.0
    else:
        specificity = 5.0
    
    # ── 5. Determine scoring level ──
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
    
    # ── 6. Find top evidence excerpts (re-rank from all text) ──
    best_evidence: List[str] = []
    
    # First, include existing high-relevance excerpts
    for ex in sorted(excerpts, key=lambda e: e.get("relevance_score", 0), reverse=True)[:3]:
        text_snippet = ex.get("excerpt", "")[:200]
        if text_snippet:
            best_evidence.append(text_snippet)
    
    # Also search all text for criterion-matching sentences
    for criterion in criteria[:3]:
        crit_words = [w for w in criterion.lower().split() if len(w) >= 5]
        for sent in _split_sentences(combined_text):
            if len(best_evidence) >= 5:
                break
            sent_lower = sent.lower()
            hits = sum(1 for w in crit_words if w in sent_lower)
            if hits >= 2 and sent[:200] not in best_evidence:
                best_evidence.append(sent[:200])
    
    # ── 7. Compute adjusted score ──
    # Start from the determined level, then adjust based on criteria coverage
    met_count = sum(1 for c in criteria_results if c.status == "met")
    partial_count = sum(1 for c in criteria_results if c.status == "partial")
    total_criteria = len(criteria_results)
    
    # Base from level
    base_from_analysis = float(level)
    
    # Fine-tune within the level based on criteria coverage
    if total_criteria > 0:
        sub_level_boost = (met_count + partial_count * 0.3) / total_criteria
        # This gives 0.0 to ~0.75 within the level
        adjusted = base_from_analysis + (sub_level_boost * 0.75)
    else:
        adjusted = base_from_analysis
    
    # Apply architecture/metrics bonus (up to 0.25)
    if has_metrics and level >= 3:
        adjusted += 0.15
    if has_architecture and level >= 3:
        adjusted += 0.10
    
    # Cap at 5.0 and round to 0.25 increments
    adjusted = min(5.0, max(0.0, adjusted))
    adjusted = round(adjusted * 4) / 4  # Round to nearest 0.25
    
    # ── 8. Compare with original score ──
    # Only adjust if the difference is significant (≥0.5) to avoid noise
    score_diff = abs(adjusted - original_score)
    if score_diff >= 0.5:
        if adjusted > original_score:
            adj_reason = (f"Score increased from {original_score:.2f} to {adjusted:.2f}: "
                         f"deeper analysis found stronger evidence ({met_count}/{total_criteria} criteria met, "
                         f"specificity={specificity:.1f}, v1 specificity={existing_specificity}).")
        else:
            adj_reason = (f"Score decreased from {original_score:.2f} to {adjusted:.2f}: "
                         f"rationale analysis found weaker support than score suggests "
                         f"({met_count}/{total_criteria} criteria met, {len(best_evidence)} key excerpts).")
    else:
        adjusted = original_score  # Keep original if within 0.5 tolerance
        adj_reason = f"Score confirmed at {original_score:.2f} — rationale analysis supports current score (analytical level={level}, diff={score_diff:.2f})."
    
    # ── 9. Build rationales ──
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
    
    # Confidence
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
        additional_sources_found=0,  # updated later
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
    
    # ── Gather ALL existing evidence URLs ──
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
    
    # ── Discover additional URLs if enabled ──
    additional_found = 0
    if fetch_additional and all_urls:
        additional = discover_additional_urls(vendor_name, all_urls)
        for u in additional:
            if u.lower().rstrip("/") not in seen_urls:
                seen_urls.add(u.lower().rstrip("/"))
                all_urls.append(u)
                additional_found += 1
    
    # ── Fetch all pages (cached first, fetch uncached as needed) ──
    pages_text: List[Tuple[str, str]] = []
    for url in all_urls:
        # Check cache before fetching so we know whether to throttle
        was_cached = _cache_path_for_url(url).exists()
        try:
            rec = get_or_fetch_page_local(url, force=False)
            if rec.get("ok") is True and isinstance(rec.get("text"), str):
                pages_text.append((rec["url"], rec["text"]))
        except KeyboardInterrupt:
            raise
        except Exception:
            pass  # Skip URLs that fail — don't crash the whole vendor
        # Throttle only when we actually hit the network
        if not was_cached:
            time.sleep(sleep_seconds + random.uniform(0.3, 1.0))
    
    ok_pages = len(pages_text)
    
    # ── Get existing scores ──
    validated_scores = vendor.get("sub_pillar_scores_validated", {})
    evidence_refined_scores = vendor.get("sub_pillar_scores_evidence_refined", {})
    eq_analysis_all = vendor.get("evidence_quality_analysis", {})
    
    # ── Analyse each sub-pillar ──
    rationale_results: Dict[str, SubPillarRationale] = {}
    
    for sid in SUBPILLAR_IDS:
        sp_info = get_sub_pillar_info(schema_body, sid)
        ev_block = evidence.get(sid, {})
        eq_block = eq_analysis_all.get(sid, {})
        
        # Use evidence_refined score as baseline (most recent), fall back to validated
        original_score = evidence_refined_scores.get(sid, validated_scores.get(sid, 0))
        
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
    """Serialise a SubPillarRationale to JSON-friendly dict."""
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
    """Write the current state of vendor data to disk."""
    output_data = dict(data)
    output_data["v2_research_metadata"] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script": "research_trism_v2_rationale.py",
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
    parser = argparse.ArgumentParser(description="AI TRiSM v2 — Scoring Rationale & Evidence Quality Analysis")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Input vendor JSON file")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output vendor JSON file")
    parser.add_argument("--max-vendors", type=int, default=0, help="Max vendors to process (0=all)")
    parser.add_argument("--dry-run", action="store_true", help="Print results without writing")
    parser.add_argument("--no-fetch", action="store_true", help="Skip additional URL discovery (still fetches uncached evidence URLs)")
    parser.add_argument("--sleep", type=float, default=1.0, help="Sleep between page fetches")
    parser.add_argument("--batch-size", type=int, default=5, help="Save progress every N vendors (default: 5)")
    parser.add_argument("--force-reprocess", action="store_true", help="Reprocess vendors even if they already have v2 data")
    args = parser.parse_args()

    # Load input
    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        print(f"  ❌ Input file not found: {input_path}")
        sys.exit(1)

    data = json.loads(input_path.read_text(encoding="utf-8"))
    vendors = data.get("vendors", [])

    # ── Resume support: if output file exists, load it and merge already-done vendors ──
    already_done: Set[str] = set()
    if output_path.exists() and not args.force_reprocess:
        try:
            existing = json.loads(output_path.read_text(encoding="utf-8"))
            existing_vendors = {v.get("vendor"): v for v in existing.get("vendors", [])}
            # Merge already-processed v2 fields back into our working data
            for vendor in vendors:
                vname = vendor.get("vendor")
                ev = existing_vendors.get(vname, {})
                if (ev.get("sub_pillar_rationale_v2")
                        and ev.get("sub_pillar_scores_v2_researched")
                        and len(ev["sub_pillar_scores_v2_researched"]) == 12):
                    vendor["sub_pillar_rationale_v2"] = ev["sub_pillar_rationale_v2"]
                    vendor["sub_pillar_scores_v2_researched"] = ev["sub_pillar_scores_v2_researched"]
                    vendor["pillar_scores_v2_researched"] = ev.get("pillar_scores_v2_researched", {})
                    already_done.add(vname)
        except Exception:
            pass  # Corrupted output — start fresh

    # Load schema
    schema_body = load_schema()

    total = len(vendors)
    if args.max_vendors > 0:
        vendors = vendors[:args.max_vendors]

    # Determine which vendors need processing
    to_process = [(i, v) for i, v in enumerate(vendors)
                  if v.get("vendor") not in already_done]

    print("=" * 70)
    print("  AI TRiSM v2 — Scoring Rationale & Evidence Quality Analysis")
    print(f"  Input:  {input_path.name}")
    print(f"  Output: {output_path.name}")
    print(f"  Mode:   {'DRY RUN' if args.dry_run else 'WRITE'}")
    print(f"  Fetch:  {'Full discovery + fetch' if not args.no_fetch else 'Cache-first (fetch uncached evidence URLs)'}")
    print(f"  Batch:  Save every {args.batch_size} vendors")
    if already_done:
        print(f"  Resume: {len(already_done)} vendors already done, {len(to_process)} remaining")
    print("=" * 70)
    print(f"\n  Processing {len(to_process)} of {len(vendors)} vendors "
          f"({len(already_done)} already done)...\n")

    # Track adjustments
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
                print(f"  [{vi_idx:3d}/{len(to_process)}] {vendor_name:<38s} ❌ ERROR: {exc}")
                continue

            # ── Build new vendor fields ──
            new_rationale = {}
            new_scores = {}
            new_pillar_scores = {}
            adjustments = []

            for sid, rat in result["rationale_results"].items():
                new_rationale[sid] = rationale_to_dict(rat)
                new_scores[sid] = rat.adjusted_score
                total_sps += 1
                confidence_counts[rat.confidence] = confidence_counts.get(rat.confidence, 0) + 1

                if rat.adjusted_score > rat.original_score:
                    stats["increases"] += 1
                    adjustments.append(f"  ↑ {sid}: {rat.original_score:.2f}→{rat.adjusted_score:.2f}")
                elif rat.adjusted_score < rat.original_score:
                    stats["decreases"] += 1
                    adjustments.append(f"  ↓ {sid}: {rat.original_score:.2f}→{rat.adjusted_score:.2f}")
                else:
                    stats["unchanged"] += 1

            # Compute pillar averages
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

            # Write back to vendor object in memory
            vendor["sub_pillar_rationale_v2"] = new_rationale
            vendor["sub_pillar_scores_v2_researched"] = new_scores
            vendor["pillar_scores_v2_researched"] = new_pillar_scores
            processed_in_session += 1

        # ── Save after each batch ──
        if not args.dry_run:
            _save_output(data, output_path, len(already_done) + processed_in_session,
                         total, stats)
            print(f"  💾 Batch saved ({len(already_done) + processed_in_session}/{len(vendors)} complete)\n")

    # ── Summary ──
    print(f"\n{'─' * 70}")
    print("  RATIONALE ANALYSIS SUMMARY")
    print(f"{'─' * 70}")
    print(f"  Total vendors in file:     {total}")
    print(f"  Already done (resumed):    {len(already_done)}")
    print(f"  Processed this session:    {processed_in_session}")
    print(f"  Errors (skipped):          {len(errors)}")
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
        print(f"\n  ⚠ Vendors with errors (re-run to retry):")
        for e in errors:
            print(f"    - {e}")

    if args.dry_run:
        print(f"\n  🔍 DRY RUN — no files written.")
    else:
        # Final save
        _save_output(data, output_path, len(already_done) + processed_in_session,
                     total, stats)
        print(f"\n  ✅ Saved to {output_path}")

    # ── Show top adjustments ──
    adj_count = stats["increases"] + stats["decreases"]
    if adj_count > 0:
        print(f"\n  Score adjustment examples (first 10):")
        count = 0
        for vendor in vendors:
            rat_v2 = vendor.get("sub_pillar_rationale_v2", {})
            for sid, rat_data in rat_v2.items():
                if isinstance(rat_data, dict):
                    adj = rat_data.get("score_adjustment", {})
                    if adj.get("original") != adj.get("adjusted"):
                        direction = "↑" if adj["adjusted"] > adj["original"] else "↓"
                        print(f"    {direction} {vendor['vendor']:<30s} {sid}: "
                              f"{adj['original']:.2f} → {adj['adjusted']:.2f}")
                        count += 1
                        if count >= 10:
                            break
            if count >= 10:
                break


if __name__ == "__main__":
    main()
