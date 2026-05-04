"""
build_mdr_pricing_v2.py — MDR Pricing Evaluation Research Pipeline
====================================================================

Complete pricing research pipeline that mirrors the capability scoring depth:
  1. Fetches vendor web pages from pricing evidence URLs
  2. Extracts pricing-relevant excerpts per dimension (PRC-SUB through PRC-OUT)
  3. Re-assesses each dimension's criteria using actual web evidence
  4. Computes evidence-validated scores with adjustment tracking
  5. Builds structured rationale + human-readable text per dimension
  6. Computes outcome maturity rating from evidence
  7. Writes MDR Services Vendor Pricing 2-0 Researched.json

Schema alignment:
  - 6 pricing dimensions: PRC-SUB, PRC-USG, PRC-FIX, PRC-SUC, PRC-COM, PRC-OUT
  - 5 criteria per dimension (what_to_evaluate from schema)
  - Scoring 0-5 aligned with pricing_evaluation.outcome_maturity_rating scale
  - Outcome maturity rating assessed independently from dimension scores

Usage:
  python build_mdr_pricing_v2.py                     # full run
  python build_mdr_pricing_v2.py --max-vendors 5     # test with 5
  python build_mdr_pricing_v2.py --force-fetch        # re-fetch cached pages
  python build_mdr_pricing_v2.py --dry-run             # analyze without writing
"""

import argparse
import hashlib
import io
import json
import os
import random
import re
import statistics
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html import unescape
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
INPUT_FILE = ROOT / "MDR Services Vendor Pricing 1-0 Seed.json"
OUTPUT_FILE = ROOT / "MDR Services Vendor Pricing 2-0 Researched.json"
SCHEMA_FILE = ROOT / "MDR_Services_Schema.json"
CACHE_DIR = ROOT / "research" / "cache" / "pages_mdr_pricing"

PRICING_DIMS = ["PRC-SUB", "PRC-USG", "PRC-FIX", "PRC-SUC", "PRC-COM", "PRC-OUT"]

MAX_EXCERPTS_PER_DIM = 6
FETCH_SLEEP = 1.5  # seconds between HTTP fetches

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]

# Scoring levels (same 0-5 scale as capabilities)
SCORING_LEVELS = {
    0: {"label": "No Evidence", "description": "No public information available"},
    1: {"label": "Input-Only / Minimal", "description": "Pricing entirely input-based or minimal transparency"},
    2: {"label": "Outcome-Aware / Generic", "description": "References outcomes in marketing but pricing not structurally linked"},
    3: {"label": "Outcome-Linked / Demonstrated", "description": "Specific pricing components tied to measurable outcomes or demonstrated transparency"},
    4: {"label": "Outcome-Validated / Advanced", "description": "Verified outcome metrics with balanced risk-sharing and client dashboards"},
    5: {"label": "Outcome-Native / Market-Leading", "description": "Entire commercial model designed around verifiable outcome delivery"},
}


# ─────────────────────────────────────────────────────────────
# Pricing dimension-specific search terms
# ─────────────────────────────────────────────────────────────

PRICING_TERMS = {
    "PRC-SUB": [
        "subscription", "recurring", "annual", "monthly", "per-seat", "per-endpoint",
        "per-device", "per-user", "license", "tier", "plan", "bundle", "package",
        "platform fee", "access fee", "managed service", "base price", "pricing tier",
        "subscription pricing", "recurring cost", "service tier", "standard plan",
        "premium plan", "enterprise plan", "pro plan", "pricing page", "cost",
        "analyst time", "human analyst", "ai tool", "software component",
        "included", "excluded", "breakdown", "transparent", "predictable",
    ],
    "PRC-USG": [
        "usage-based", "consumption", "pay-as-you-go", "metered", "per-gb",
        "data volume", "ingestion", "api call", "compute hour", "inference",
        "overage", "threshold", "usage dashboard", "real-time", "monitoring",
        "variable cost", "consumption-based", "elastic pricing", "pay-per-use",
        "data ingestion", "log volume", "event volume", "usage tracking",
        "measurement", "billing", "utilization", "cloud consumption",
    ],
    "PRC-FIX": [
        "fixed fee", "one-time", "setup", "deployment", "implementation",
        "integration", "onboarding", "project", "milestone", "deliverable",
        "scope", "change request", "professional services", "fixed price",
        "setup fee", "installation", "configuration", "customization",
        "playbook", "tuning", "initial deployment", "project cost",
        "implementation fee", "deployment cost", "fixed-price", "flat fee",
    ],
    "PRC-SUC": [
        "success fee", "outcome fee", "performance", "bonus", "penalty",
        "sla", "service level", "mttd", "mttr", "resolution", "breach",
        "warranty", "guarantee", "per-resolution", "per-incident", "risk",
        "fee-at-risk", "fees at risk", "performance-linked", "incentive",
        "success-based", "outcome-based", "result-based", "credit", "rebate",
        "financial consequence", "penalty clause", "breach prevention",
    ],
    "PRC-COM": [
        "composable", "modular", "flexible", "customizable", "mix and match",
        "a la carte", "configurable", "hybrid pricing", "combine", "assemble",
        "building block", "module", "component", "predictability", "budget",
        "spending", "risk-sharing", "transparent", "demystif", "clear pricing",
        "composite", "blended", "multi-model", "adaptable", "scalable pricing",
    ],
    "PRC-OUT": [
        "outcome", "value-based", "roi", "return on investment", "business value",
        "security outcome", "risk reduction", "mttd reduction", "mttr reduction",
        "value realization", "outcome-based sla", "financial consequence",
        "pricing-to-outcome", "value delivery", "efficiency gain", "cost saving",
        "outcome alignment", "value metric", "kpi-linked", "performance metric",
        "outcome-linked", "measurable outcome", "demonstrated value",
        "outcome-washing", "input-based", "breach prevention",
    ],
}

# Generic pricing terms (bonus matching for any dimension)
GENERIC_PRICING_TERMS = [
    "pricing", "price", "cost", "fee", "charge", "rate", "billing",
    "commercial", "contract", "agreement", "proposal", "quote",
    "mdr", "managed detection", "managed service", "security service",
]


# ─────────────────────────────────────────────────────────────
# HTML extraction (regex-based, same as extract_mdr_excerpts.py)
# ─────────────────────────────────────────────────────────────

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_SCRIPT_STYLE_RE = re.compile(
    r"<\s*(script|style|noscript|svg|path|meta|link)[^>]*>.*?</\s*\1\s*>",
    re.DOTALL | re.IGNORECASE,
)


def html_to_text(html: str) -> str:
    """Strip HTML tags, scripts, styles → plain text."""
    text = _SCRIPT_STYLE_RE.sub(" ", html)
    text = unescape(text)
    text = _TAG_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text).strip()
    return text


def extract_sentences(text: str) -> List[str]:
    """Split text into sentence-like chunks."""
    raw = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    sentences = []
    for s in raw:
        s = s.strip()
        if len(s) < 30 or len(s) > 1500:
            continue
        word_count = len(s.split())
        if word_count < 5:
            continue
        sentences.append(s)
    return sentences


# ─────────────────────────────────────────────────────────────
# HTTP fetch with caching
# ─────────────────────────────────────────────────────────────

def fetch_page(url: str, force: bool = False) -> Optional[str]:
    """Fetch a URL with caching and retry."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
    cache_path = CACHE_DIR / f"{url_hash}.txt"

    if not force and cache_path.exists():
        text = cache_path.read_text(encoding="utf-8", errors="replace")
        if text.strip():
            return text

    headers = {"User-Agent": random.choice(USER_AGENTS)}
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read()
                encoding = resp.headers.get_content_charset() or "utf-8"
                html = raw.decode(encoding, errors="replace")
                text = html_to_text(html)
                if text and len(text) > 100:
                    cache_path.write_text(text, encoding="utf-8")
                    return text
                return None
        except Exception:
            if attempt < 2:
                time.sleep(2 ** attempt)
    return None


# ─────────────────────────────────────────────────────────────
# Schema loading
# ─────────────────────────────────────────────────────────────

def load_schema_pricing():
    """Load pricing evaluation criteria from schema."""
    with open(SCHEMA_FILE, "r", encoding="utf-8-sig") as f:
        schema = json.load(f)
    pe = schema["mdr_services_taxonomy_v1.0"]["pricing_evaluation"]
    dims = pe.get("dimensions", {})
    omr = pe.get("outcome_maturity_rating", {})

    dim_criteria = {}
    for dim_id in PRICING_DIMS:
        dim_data = dims.get(dim_id, {})
        criteria = dim_data.get("what_to_evaluate", [])
        dim_criteria[dim_id] = {
            "name": dim_data.get("name", dim_id),
            "definition": dim_data.get("definition", ""),
            "criteria": criteria,
            "model_alignment": dim_data.get("pricing_model_alignment", ""),
            "complementarity_note": dim_data.get("complementarity_note", ""),
        }

    outcome_criteria = omr.get("evaluation_criteria", [])
    outcome_scale = omr.get("scale", {}).get("scoring_logic", {})

    return dim_criteria, outcome_criteria, outcome_scale


# ─────────────────────────────────────────────────────────────
# Excerpt extraction per dimension
# ─────────────────────────────────────────────────────────────

def score_sentence_for_dim(sentence: str, dim_id: str, criteria: List[str],
                           search_terms: List[str]) -> Tuple[float, List[str]]:
    """Score a sentence's relevance to a pricing dimension."""
    sent_lower = sentence.lower()
    sent_words = set(re.findall(r"\b[a-z]{3,}\b", sent_lower))
    matched_terms = []
    score = 0.0

    # 1. Check criteria keyword overlap
    for criterion in criteria:
        crit_words = set(re.findall(r"\b[a-z]{4,}\b", criterion.lower()))
        overlap = len(crit_words & sent_words)
        if overlap >= 3:
            score += 3.0
            matched_terms.append(f"criteria:{criterion[:50]}")
        elif overlap >= 2:
            score += 1.5
            matched_terms.append(f"criteria:{criterion[:50]}")

    # 2. Check dimension-specific terms
    for term in search_terms:
        if term.lower() in sent_lower:
            score += 2.0
            matched_terms.append(term)

    # 3. Generic pricing terms (small bonus)
    for term in GENERIC_PRICING_TERMS:
        if term.lower() in sent_lower:
            score += 0.3
            matched_terms.append(f"generic:{term}")

    # 4. Bonus for specific pricing signals
    pricing_signals = [
        (r"\$[\d,.]+", 3.0, "contains_price"),
        (r"\d+%\s", 1.0, "contains_percentage"),
        (r"per[- ](?:endpoint|seat|user|device|gb|tb)", 2.0, "per_unit_pricing"),
        (r"(?:annual|monthly|quarterly)\s+(?:fee|cost|rate|subscription)", 2.0, "recurring_pricing"),
        (r"(?:sla|service level)\s+(?:agreement|guarantee|commitment)", 2.0, "sla_reference"),
        (r"(?:free|trial|demo|proof of concept|poc)", 1.0, "trial_available"),
    ]
    for pattern, bonus, label in pricing_signals:
        if re.search(pattern, sent_lower):
            score += bonus
            matched_terms.append(label)

    return score, list(dict.fromkeys(matched_terms))  # deduplicate preserving order


def extract_pricing_excerpts(sentences: List[str], dim_id: str,
                              criteria: List[str], url: str,
                              max_excerpts: int = MAX_EXCERPTS_PER_DIM) -> List[Dict]:
    """Extract top-scoring pricing excerpts for a dimension from sentences."""
    search_terms = PRICING_TERMS.get(dim_id, [])
    scored = []
    for sent in sentences:
        score, terms = score_sentence_for_dim(sent, dim_id, criteria, search_terms)
        if score > 1.0 and terms:
            scored.append((score, sent, terms))

    scored.sort(key=lambda x: -x[0])
    excerpts = []
    seen_text = set()
    for score, sent, terms in scored[:max_excerpts * 2]:  # oversample then dedup
        # Dedup by checking substring overlap
        key = sent[:80].lower()
        if key in seen_text:
            continue
        seen_text.add(key)
        excerpts.append({
            "excerpt": sent[:800],
            "url": url,
            "relevance_score": round(score, 2),
            "matched_terms": terms[:8],
        })
        if len(excerpts) >= max_excerpts:
            break

    return excerpts


# ─────────────────────────────────────────────────────────────
# Criteria assessment with evidence
# ─────────────────────────────────────────────────────────────

def assess_pricing_criterion(criterion_text: str, excerpts: List[Dict],
                              notes: str, original_score: float,
                              dim_id: str) -> Dict:
    """Assess a single pricing criterion using excerpts + notes."""
    crit_lower = criterion_text.lower()
    crit_words = set(re.findall(r"\b[a-z]{4,}\b", crit_lower))

    # Combine all excerpt texts
    excerpt_texts = []
    for ex in excerpts:
        txt = ex.get("excerpt", "") if isinstance(ex, dict) else str(ex)
        if txt:
            excerpt_texts.append(txt)

    # Check dim-specific keywords
    dim_terms = PRICING_TERMS.get(dim_id, [])
    dim_kws = set()
    for t in dim_terms:
        for w in re.findall(r"\b[a-z]{3,}\b", t.lower()):
            dim_kws.add(w)

    # Evidence matching
    combined_lower = " ".join(excerpt_texts).lower() + " " + (notes or "").lower()
    combined_words = set(re.findall(r"\b[a-z]{4,}\b", combined_lower))

    # Overlap ratios
    overlap = len(crit_words & combined_words)
    overlap_ratio = overlap / max(len(crit_words), 1)

    # Notes-specific check
    notes_lower = (notes or "").lower()
    notes_words = set(re.findall(r"\b[a-z]{4,}\b", notes_lower))
    notes_overlap = len(crit_words & notes_words)

    # Dim keywords in evidence
    kw_in_evidence = len(dim_kws & combined_words)

    # Determine status
    if overlap_ratio >= 0.15 and kw_in_evidence >= 2:
        status = "met"
        evidence_text = excerpt_texts[0][:200] if excerpt_texts else notes[:200] if notes else ""
    elif original_score >= 1 and (overlap_ratio >= 0.05 or notes_overlap >= 1 or kw_in_evidence >= 1):
        status = "partial"
        evidence_text = excerpt_texts[0][:200] if excerpt_texts else notes[:200] if notes else ""
    elif original_score == 0 or (not excerpt_texts and not notes):
        status = "unmet"
        evidence_text = "No evidence found"
    elif notes:
        status = "partial"
        evidence_text = notes[:200]
    else:
        status = "unmet"
        evidence_text = "Insufficient evidence"

    return {
        "criterion": criterion_text,
        "status": status,
        "evidence": evidence_text,
        "overlap_ratio": round(overlap_ratio, 3),
    }


# ─────────────────────────────────────────────────────────────
# Evidence score computation
# ─────────────────────────────────────────────────────────────

def compute_pricing_evidence_score(excerpts: List[Dict], notes: str,
                                    criteria_results: List[Dict],
                                    dim_id: str) -> Tuple[float, Dict]:
    """Compute an evidence-based score for a pricing dimension."""
    n_met = sum(1 for c in criteria_results if c["status"] == "met")
    n_partial = sum(1 for c in criteria_results if c["status"] == "partial")
    n_unmet = sum(1 for c in criteria_results if c["status"] == "unmet")
    n_total = max(len(criteria_results), 1)

    # Base evidence score from criteria
    criteria_score = (n_met * 1.0 + n_partial * 0.5) / n_total * 5.0

    # Excerpt richness bonus (conservative)
    excerpt_count = len(excerpts)
    if excerpt_count >= 4:
        excerpt_bonus = 0.3
    elif excerpt_count >= 2:
        excerpt_bonus = 0.15
    else:
        excerpt_bonus = 0.0

    # Pricing signal bonus (from excerpt matched terms)
    pricing_signal_count = 0
    for ex in excerpts:
        terms = ex.get("matched_terms", []) if isinstance(ex, dict) else []
        for t in terms:
            if t in ("contains_price", "per_unit_pricing", "recurring_pricing", "sla_reference"):
                pricing_signal_count += 1

    signal_bonus = min(pricing_signal_count * 0.10, 0.35)

    # Notes bonus
    notes_bonus = 0.0
    if notes and len(notes) > 50:
        notes_bonus = 0.25

    evidence_score = criteria_score + excerpt_bonus + signal_bonus + notes_bonus
    evidence_score = min(max(evidence_score, 0.0), 5.0)

    breakdown = {
        "criteria_score": round(criteria_score, 2),
        "n_met": n_met,
        "n_partial": n_partial,
        "n_unmet": n_unmet,
        "excerpt_count": excerpt_count,
        "excerpt_bonus": round(excerpt_bonus, 2),
        "pricing_signal_count": pricing_signal_count,
        "signal_bonus": round(signal_bonus, 2),
        "notes_bonus": round(notes_bonus, 2),
        "total": round(evidence_score, 2),
    }

    return evidence_score, breakdown


# ─────────────────────────────────────────────────────────────
# Score adjustment
# ─────────────────────────────────────────────────────────────

def adjust_pricing_score(original: float, evidence_score: float) -> Tuple[float, str, str]:
    """Compute adjusted score with capped delta."""
    # Weighted blend: 0.75 × original + 0.25 × evidence (conservative for pricing)
    blended = 0.75 * original + 0.25 * evidence_score
    delta = blended - original

    # Cap adjustment at ±0.75
    max_adj = 0.75
    if delta > max_adj:
        delta = max_adj
    elif delta < -max_adj:
        delta = -max_adj

    adjusted = round(original + delta, 2)
    adjusted = min(max(adjusted, 0.0), 5.0)

    # Determine adjustment type
    actual_delta = adjusted - original
    if abs(actual_delta) < 0.05:
        adj_type = "validated"
        reason = f"Evidence supports score (evidence={evidence_score:.1f}, delta={actual_delta:+.2f})."
    elif actual_delta > 0:
        adj_type = "increased"
        reason = f"Evidence suggests stronger pricing transparency (evidence={evidence_score:.1f}, delta={actual_delta:+.2f})."
    else:
        adj_type = "decreased"
        reason = f"Evidence suggests weaker pricing transparency than scored (evidence={evidence_score:.1f}, delta={actual_delta:+.2f})."

    return adjusted, adj_type, reason


# ─────────────────────────────────────────────────────────────
# Evidence quality assessment
# ─────────────────────────────────────────────────────────────

def compute_pricing_evidence_quality(score: float, notes: str,
                                      source_urls: List[str],
                                      excerpts: List[Dict],
                                      criteria_results: List[Dict]) -> Tuple[float, str]:
    """Compute evidence quality factor and grade for pricing."""
    factors = []

    # URL coverage
    n_urls = len(source_urls)
    if n_urls >= 2:
        factors.append(0.25)
    elif n_urls >= 1:
        factors.append(0.15)
    else:
        factors.append(0.0)

    # Excerpt coverage
    n_excerpts = len(excerpts)
    if n_excerpts >= 4:
        factors.append(0.30)
    elif n_excerpts >= 2:
        factors.append(0.20)
    elif n_excerpts >= 1:
        factors.append(0.10)
    else:
        factors.append(0.0)

    # Criteria met ratio
    n_met = sum(1 for c in criteria_results if c["status"] == "met")
    n_partial = sum(1 for c in criteria_results if c["status"] == "partial")
    n_total = max(len(criteria_results), 1)
    met_ratio = (n_met + 0.5 * n_partial) / n_total
    factors.append(met_ratio * 0.30)

    # Notes quality
    notes_len = len(notes or "")
    if notes_len >= 100:
        factors.append(0.15)
    elif notes_len >= 30:
        factors.append(0.08)
    else:
        factors.append(0.0)

    eq_factor = min(sum(factors), 1.0)

    # Grade
    if eq_factor >= 0.65:
        grade = "A"
    elif eq_factor >= 0.45:
        grade = "B"
    elif eq_factor >= 0.25:
        grade = "C"
    elif eq_factor >= 0.10:
        grade = "D"
    else:
        grade = "F"

    return eq_factor, grade


# ─────────────────────────────────────────────────────────────
# Rationale text builder
# ─────────────────────────────────────────────────────────────

def build_pricing_rationale_text(dim_id: str, dim_name: str,
                                  original_score: float, adjusted_score: float,
                                  evidence_score: float, adj_type: str, adj_reason: str,
                                  criteria_results: List[Dict],
                                  evidence_breakdown: Dict,
                                  excerpts: List[Dict],
                                  confidence: str,
                                  model_alignment: str) -> str:
    """Build human-readable pricing rationale text."""
    level = min(max(int(round(adjusted_score)), 0), 5)
    level_label = SCORING_LEVELS[level]["label"]

    n_met = sum(1 for c in criteria_results if c["status"] == "met")
    n_partial = sum(1 for c in criteria_results if c["status"] == "partial")
    n_unmet = sum(1 for c in criteria_results if c["status"] == "unmet")
    n_total = len(criteria_results)

    lines = []

    # Header
    if adjusted_score != original_score:
        lines.append(
            f"{dim_id} – {dim_name}: Score {adjusted_score:.1f}/5.0 "
            f"(adjusted from {original_score:.1f}, Level {level}: {level_label}). "
            f"Confidence: {confidence}."
        )
    else:
        lines.append(
            f"{dim_id} – {dim_name}: Score {adjusted_score:.1f}/5.0 "
            f"(Level {level}: {level_label}). Confidence: {confidence}."
        )

    # Score Validation
    lines.append("")
    lines.append("[Score Validation]")
    lines.append(
        f"Evidence-supported score: {evidence_score:.1f}/5.0. "
        f"Adjustment: {adj_type}. {adj_reason}"
    )

    # Evidence Breakdown
    eb = evidence_breakdown
    lines.append("")
    lines.append("[Evidence Breakdown]")
    lines.append(
        f"Criteria score: {eb['criteria_score']:.1f}/5.0 "
        f"(met={eb['n_met']}, partial={eb['n_partial']}, unmet={eb['n_unmet']}). "
        f"Excerpt bonus: +{eb['excerpt_bonus']:.2f} ({eb['excerpt_count']} excerpts). "
        f"Pricing signal bonus: +{eb['signal_bonus']:.2f} ({eb['pricing_signal_count']} signals). "
        f"Notes bonus: +{eb['notes_bonus']:.2f}."
    )

    # Criteria Assessment
    lines.append("")
    lines.append("[Criteria Assessment]")
    for cr in criteria_results:
        icon = {"met": "✅", "partial": "⚠️", "unmet": "❌"}.get(cr["status"], "?")
        lines.append(f"  {icon} {cr['status'].upper()}: {cr['criterion'][:100]}")
        if cr.get("evidence") and cr["evidence"] != "No evidence found":
            lines.append(f"     Evidence: {cr['evidence'][:150]}")

    # Model alignment context
    if model_alignment:
        lines.append("")
        lines.append("[Pricing Model Alignment]")
        lines.append(f"  {model_alignment[:300]}")

    # Key excerpts
    if excerpts:
        lines.append("")
        lines.append("[Key Pricing Evidence]")
        for i, ex in enumerate(excerpts[:3], 1):
            txt = ex.get("excerpt", "") if isinstance(ex, dict) else str(ex)
            lines.append(f"  Excerpt {i}: {txt[:250]}")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# Outcome maturity rating assessment
# ─────────────────────────────────────────────────────────────

def assess_outcome_maturity(vendor: Dict, dim_scores: Dict,
                             dim_rationales: Dict,
                             outcome_criteria: List[str],
                             outcome_scale: Dict) -> Tuple[int, str, Dict]:
    """Assess the vendor's outcome maturity rating from pricing evidence."""
    original_omr = vendor.get("outcome_maturity_rating", 0)

    # Gather signals from dimension scores and rationale
    prc_suc = dim_scores.get("PRC-SUC", 0)
    prc_out = dim_scores.get("PRC-OUT", 0)
    prc_com = dim_scores.get("PRC-COM", 0)

    # Check outcome criteria from all excerpts
    all_excerpts_text = ""
    for dim_id, rat in dim_rationales.items():
        if isinstance(rat, dict):
            ca = rat.get("criteria_assessment", [])
            for c in ca:
                if c.get("evidence") and c["evidence"] != "No evidence found":
                    all_excerpts_text += " " + c["evidence"]

    # Also include pricing analysis and notes
    pricing_analysis = vendor.get("pricing_analysis", "")
    oe = vendor.get("outcome_evidence", {})
    outcome_notes = oe.get("notes", "") if isinstance(oe, dict) else ""
    combined_text = (all_excerpts_text + " " + pricing_analysis + " " + outcome_notes).lower()

    # Score outcome maturity based on evidence
    outcome_signals = {
        "pricing_changes_on_outcomes": bool(re.search(r"pric\w*\s+(?:adjust|change|var)\w*.*outcome", combined_text)),
        "metrics_verifiable": bool(re.search(r"(?:independent|third.party|jointly|verif)", combined_text)),
        "ai_efficiency_shared": bool(re.search(r"(?:ai|automat)\w*\s+(?:efficien|sav|gain|pass)", combined_text)),
        "contract_embedded": bool(re.search(r"(?:contract|agreement)\s+.*(?:outcome|result|performance)", combined_text)),
        "track_record": bool(re.search(r"(?:track record|renewal|retention|expansion|growth)", combined_text)),
        "roi_aligned": bool(re.search(r"(?:roi|return on invest|value realiz)", combined_text)),
    }

    signal_count = sum(outcome_signals.values())
    # Base from PRC-SUC and PRC-OUT scores
    base = (prc_suc * 0.4 + prc_out * 0.4 + prc_com * 0.2)
    # Signal bonus
    signal_bonus = signal_count * 0.2
    computed_omr = base + signal_bonus
    computed_omr = min(max(round(computed_omr), 0), 5)

    # Blend with original
    adjusted_omr = round(0.6 * original_omr + 0.4 * computed_omr)
    adjusted_omr = min(max(adjusted_omr, 0), 5)

    omr_rationale = (
        f"Outcome maturity: {adjusted_omr}/5 "
        f"(original={original_omr}, computed={computed_omr:.1f}). "
        f"Based on PRC-SUC={prc_suc:.1f}, PRC-OUT={prc_out:.1f}, PRC-COM={prc_com:.1f}. "
        f"Outcome signals detected: {signal_count}/6 "
        f"({', '.join(k for k,v in outcome_signals.items() if v) or 'none'}). "
        f"Scale: {outcome_scale.get(str(adjusted_omr), 'N/A')}"
    )

    return adjusted_omr, omr_rationale, outcome_signals


# ─────────────────────────────────────────────────────────────
# Vendor-level summary
# ─────────────────────────────────────────────────────────────

def compute_vendor_pricing_summary(vendor_name: str, dim_scores: Dict,
                                    dim_rationales: Dict,
                                    original_dim_scores: Dict) -> Dict:
    """Compute vendor-level pricing summary."""
    # Pricing overall score
    if dim_scores:
        overall = sum(dim_scores.values()) / len(dim_scores)
    else:
        overall = 0.0

    # Adjustment summary
    increased = 0
    decreased = 0
    validated = 0
    no_change = 0
    for dim_id, rat in dim_rationales.items():
        if isinstance(rat, dict):
            adj_type = rat.get("adjustment_type", "")
            if adj_type == "increased":
                increased += 1
            elif adj_type == "decreased":
                decreased += 1
            elif adj_type == "validated":
                validated += 1
            else:
                no_change += 1

    # Confidence
    eq_factors = [rat.get("evidence_quality_factor", 0) for rat in dim_rationales.values() if isinstance(rat, dict)]
    avg_eq = statistics.mean(eq_factors) if eq_factors else 0

    if avg_eq >= 0.50 and validated + increased >= 4:
        confidence = "high"
    elif avg_eq >= 0.30:
        confidence = "medium"
    else:
        confidence = "low"

    # Strongest/weakest dimensions
    if dim_scores:
        strongest = max(dim_scores, key=dim_scores.get)
        weakest = min(dim_scores, key=dim_scores.get)
    else:
        strongest = weakest = "N/A"

    return {
        "pricing_overall_score_v2": round(overall, 2),
        "pricing_dimension_scores_v2": dim_scores,
        "pricing_adjustment_summary": {
            "increased": increased,
            "decreased": decreased,
            "validated": validated,
            "no_change": no_change,
        },
        "pricing_research_confidence": confidence,
        "avg_evidence_quality": round(avg_eq, 3),
        "strongest_dimension": strongest,
        "weakest_dimension": weakest,
    }


# ─────────────────────────────────────────────────────────────
# Main pipeline
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="MDR Pricing Research Pipeline")
    parser.add_argument("--max-vendors", type=int, default=0, help="Limit vendors for testing")
    parser.add_argument("--force-fetch", action="store_true", help="Re-fetch cached pages")
    parser.add_argument("--dry-run", action="store_true", help="Analyze only, don't write")
    args = parser.parse_args()

    print("=" * 70)
    print("MDR Pricing Evaluation Research Pipeline v2.0")
    print("=" * 70)

    # Load schema
    dim_criteria, outcome_criteria, outcome_scale = load_schema_pricing()
    print(f"\nLoaded schema: {len(dim_criteria)} pricing dimensions")
    for dim_id, dc in dim_criteria.items():
        print(f"  {dim_id}: {dc['name']} ({len(dc['criteria'])} criteria)")

    # Load vendor data
    with open(INPUT_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    vendors = data.get("vendors", data if isinstance(data, list) else [])
    print(f"\nLoaded {len(vendors)} vendors from {INPUT_FILE.name}")

    if args.max_vendors > 0:
        vendors = vendors[: args.max_vendors]
        print(f"  Limited to {len(vendors)} vendors for testing")

    # -- Phase 1: Fetch & extract excerpts --
    print(f"\n{'-' * 60}")
    print("Phase 1: Fetching web pages & extracting pricing excerpts")
    print(f"{'-' * 60}")

    total_excerpts = 0
    vendors_with_excerpts = 0
    fetch_count = 0

    for vi, vendor in enumerate(vendors):
        vname = vendor["vendor"]
        pricing_ev = vendor.get("pricing_evidence", {})
        vendor_total = 0

        # Collect all unique URLs for this vendor
        all_urls = set()
        for dim_id in PRICING_DIMS:
            ev = pricing_ev.get(dim_id, {})
            for url in ev.get("source_urls", []):
                if url and url.startswith("http"):
                    all_urls.add(url)

        # Also collect from outcome evidence
        oe = vendor.get("outcome_evidence", {})
        if isinstance(oe, dict):
            for url in oe.get("source_urls", []):
                if url and url.startswith("http"):
                    all_urls.add(url)

        # Fetch all pages
        url_sentences = {}
        for url in all_urls:
            text = fetch_page(url, force=args.force_fetch)
            if text:
                sentences = extract_sentences(text)
                url_sentences[url] = sentences
                fetch_count += 1
                if fetch_count % 20 == 0:
                    time.sleep(FETCH_SLEEP)

        # Extract excerpts per dimension
        for dim_id in PRICING_DIMS:
            ev = pricing_ev.get(dim_id, {})
            dim_urls = ev.get("source_urls", [])
            criteria = dim_criteria[dim_id]["criteria"]

            all_excerpts = []
            for url in dim_urls:
                if url in url_sentences:
                    excerpts = extract_pricing_excerpts(
                        url_sentences[url], dim_id, criteria, url
                    )
                    all_excerpts.extend(excerpts)

            # Also try all other vendor URLs if we got few excerpts
            if len(all_excerpts) < 2:
                for url, sentences in url_sentences.items():
                    if url not in dim_urls:
                        extra = extract_pricing_excerpts(
                            sentences, dim_id, criteria, url, max_excerpts=2
                        )
                        all_excerpts.extend(extra)

            # Sort by relevance and deduplicate
            all_excerpts.sort(key=lambda x: -x.get("relevance_score", 0))
            final_excerpts = []
            seen = set()
            for ex in all_excerpts:
                key = ex.get("excerpt", "")[:60].lower()
                if key not in seen:
                    seen.add(key)
                    final_excerpts.append(ex)
                if len(final_excerpts) >= MAX_EXCERPTS_PER_DIM:
                    break

            # Store excerpts back into evidence
            if dim_id not in pricing_ev:
                pricing_ev[dim_id] = {"source_urls": [], "excerpts": [], "notes": ""}
            pricing_ev[dim_id]["excerpts"] = final_excerpts
            vendor_total += len(final_excerpts)

        vendor["pricing_evidence"] = pricing_ev
        total_excerpts += vendor_total
        if vendor_total > 0:
            vendors_with_excerpts += 1

        if (vi + 1) % 10 == 0 or vi == 0 or vi == len(vendors) - 1:
            print(f"  [{vi+1}/{len(vendors)}] {vname}: {vendor_total} excerpts")

    print(f"\nPhase 1 complete: {total_excerpts} excerpts across {vendors_with_excerpts}/{len(vendors)} vendors")

    # -- Phase 2: Evidence-validated scoring --
    print(f"\n{'-' * 60}")
    print("Phase 2: Evidence-validated pricing scoring")
    print(f"{'-' * 60}")

    all_original = []
    all_adjusted = []
    adjustment_counts = {"increased": 0, "decreased": 0, "validated": 0, "no_change": 0}

    for vi, vendor in enumerate(vendors):
        vname = vendor["vendor"]
        dim_scores_orig = vendor.get("pricing_dimension_scores", {})
        pricing_ev = vendor.get("pricing_evidence", {})
        pricing_analysis = vendor.get("pricing_analysis", "")
        model_details = vendor.get("pricing_model_details", {})

        v2_dim_scores = {}
        v2_dim_rationales = {}
        v2_dim_rationale_text = {}

        for dim_id in PRICING_DIMS:
            dc = dim_criteria[dim_id]
            dim_name = dc["name"]
            criteria = dc["criteria"]
            model_alignment = dc.get("model_alignment", "")

            original_score = float(dim_scores_orig.get(dim_id, 0))
            ev = pricing_ev.get(dim_id, {})
            notes = ev.get("notes", "")
            source_urls = ev.get("source_urls", [])
            excerpts = ev.get("excerpts", [])

            # Add pricing_analysis as supplementary notes
            combined_notes = notes
            if pricing_analysis:
                combined_notes = notes + " " + pricing_analysis if notes else pricing_analysis

            # 1. Assess criteria
            criteria_results = []
            for criterion in criteria:
                result = assess_pricing_criterion(
                    criterion, excerpts, combined_notes, original_score, dim_id
                )
                criteria_results.append(result)

            # 2. Compute evidence score
            evidence_score, evidence_breakdown = compute_pricing_evidence_score(
                excerpts, combined_notes, criteria_results, dim_id
            )

            # 3. Adjust score
            adjusted_score, adj_type, adj_reason = adjust_pricing_score(
                original_score, evidence_score
            )

            all_original.append(original_score)
            all_adjusted.append(adjusted_score)
            if adj_type in adjustment_counts:
                adjustment_counts[adj_type] += 1

            # 4. Evidence quality
            eq_factor, eq_grade = compute_pricing_evidence_quality(
                adjusted_score, combined_notes, source_urls, excerpts, criteria_results
            )

            # 5. Confidence
            n_met = sum(1 for c in criteria_results if c["status"] == "met")
            n_partial = sum(1 for c in criteria_results if c["status"] == "partial")
            if eq_factor >= 0.55 and n_met + n_partial >= 3:
                confidence = "high"
            elif eq_factor >= 0.30 and n_met + n_partial >= 1:
                confidence = "medium"
            else:
                confidence = "low"

            # Store validated score
            v2_dim_scores[dim_id] = adjusted_score

            # Store structured rationale
            v2_dim_rationales[dim_id] = {
                "dimension_id": dim_id,
                "dimension_name": dim_name,
                "original_score": original_score,
                "evidence_score": round(evidence_score, 2),
                "adjusted_score": adjusted_score,
                "adjustment_type": adj_type,
                "adjustment_reason": adj_reason,
                "scoring_level": min(max(int(round(adjusted_score)), 0), 5),
                "criteria_assessment": criteria_results,
                "evidence_breakdown": evidence_breakdown,
                "evidence_quality_factor": eq_factor,
                "evidence_quality_grade": eq_grade,
                "confidence": confidence,
                "excerpt_count": len(excerpts),
            }

            # Build readable text
            v2_dim_rationale_text[dim_id] = build_pricing_rationale_text(
                dim_id, dim_name, original_score, adjusted_score,
                evidence_score, adj_type, adj_reason,
                criteria_results, evidence_breakdown, excerpts,
                confidence, model_alignment
            )

        # Outcome maturity rating
        adjusted_omr, omr_rationale, outcome_signals = assess_outcome_maturity(
            vendor, v2_dim_scores, v2_dim_rationales,
            outcome_criteria, outcome_scale
        )

        # Vendor summary
        summary = compute_vendor_pricing_summary(
            vname, v2_dim_scores, v2_dim_rationales,
            dim_scores_orig
        )

        # Write v2 fields to vendor
        vendor["pricing_dimension_scores_v2"] = v2_dim_scores
        vendor["pricing_overall_score_v2"] = summary["pricing_overall_score_v2"]
        vendor["pricing_dimension_rationale_v2"] = v2_dim_rationales
        vendor["pricing_dimension_rationale_v2_text"] = v2_dim_rationale_text
        vendor["outcome_maturity_rating_v2"] = adjusted_omr
        vendor["outcome_maturity_rationale_v2"] = omr_rationale
        vendor["outcome_signals_v2"] = outcome_signals
        vendor["pricing_adjustment_summary"] = summary["pricing_adjustment_summary"]
        vendor["pricing_research_confidence"] = summary["pricing_research_confidence"]
        vendor["pricing_dimension_labels"] = {
            dim_id: dim_criteria[dim_id]["name"] for dim_id in PRICING_DIMS
        }

        if (vi + 1) % 10 == 0 or vi == 0 or vi == len(vendors) - 1:
            adj_s = summary["pricing_adjustment_summary"]
            print(
                f"  [{vi+1}/{len(vendors)}] {vname}: "
                f"overall={summary['pricing_overall_score_v2']:.2f} "
                f"UP:{adj_s['increased']} DN:{adj_s['decreased']} "
                f"OK:{adj_s['validated']} EQ:{adj_s['no_change']} | "
                f"OMR: {vendor.get('outcome_maturity_rating', 0)}->{adjusted_omr}"
            )

    # -- Summary statistics --
    print(f"\n{'-' * 60}")
    print("Pipeline Summary")
    print(f"{'-' * 60}")

    n_dims = len(all_original)
    deltas = [a - o for o, a in zip(all_original, all_adjusted)]

    print(f"  Dimensions assessed: {n_dims}")
    print(f"  Excerpts extracted: {total_excerpts}")
    print(f"  Vendors with excerpts: {vendors_with_excerpts}/{len(vendors)}")
    print(f"\n  Score adjustments:")
    print(f"    Validated (no change):  {adjustment_counts['validated']} ({adjustment_counts['validated']/n_dims*100:.1f}%)")
    print(f"    Increased:              {adjustment_counts['increased']} ({adjustment_counts['increased']/n_dims*100:.1f}%)")
    print(f"    Decreased:              {adjustment_counts['decreased']} ({adjustment_counts['decreased']/n_dims*100:.1f}%)")
    print(f"\n  Original scores: mean={statistics.mean(all_original):.2f}, stdev={statistics.stdev(all_original):.2f}")
    print(f"  Adjusted scores: mean={statistics.mean(all_adjusted):.2f}, stdev={statistics.stdev(all_adjusted):.2f}")
    print(f"  Net delta: {statistics.mean(deltas):+.3f}")

    # Per-dimension stats
    print(f"\n  Per-dimension averages:")
    for dim_id in PRICING_DIMS:
        orig_vals = [float(v.get("pricing_dimension_scores", {}).get(dim_id, 0)) for v in vendors]
        adj_vals = [float(v.get("pricing_dimension_scores_v2", {}).get(dim_id, 0)) for v in vendors]
        print(f"    {dim_id}: {statistics.mean(orig_vals):.2f} → {statistics.mean(adj_vals):.2f} (delta={statistics.mean(adj_vals)-statistics.mean(orig_vals):+.2f})")

    # ── Write output ──
    if not args.dry_run:
        output_data = {
            "schema_ref": "MDR_Services_Schema.json",
            "schema_version": "2.0",
            "data_type": "pricing",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "pipeline": "build_mdr_pricing_v2.py",
            "vendor_count": len(vendors),
            "dimensions": PRICING_DIMS,
            "dimension_labels": {dim_id: dim_criteria[dim_id]["name"] for dim_id in PRICING_DIMS},
            "summary": {
                "total_excerpts": total_excerpts,
                "vendors_with_excerpts": vendors_with_excerpts,
                "adjustment_counts": adjustment_counts,
                "original_mean": round(statistics.mean(all_original), 3),
                "adjusted_mean": round(statistics.mean(all_adjusted), 3),
                "net_delta": round(statistics.mean(deltas), 4),
            },
            "vendors": vendors,
        }

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        size_mb = OUTPUT_FILE.stat().st_size / 1024 / 1024
        print(f"\n  Written: {OUTPUT_FILE.name} ({size_mb:.1f} MB)")
    else:
        print("\n  [DRY RUN] No file written.")

    print("\nDone.")


if __name__ == "__main__":
    main()
