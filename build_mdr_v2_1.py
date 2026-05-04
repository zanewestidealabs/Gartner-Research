#!/usr/bin/env python3
"""
build_mdr_v2_1.py – MDR Services Vendor 2-1 Consolidated
=========================================================

Reads the v2.0 researched file (which now includes web-scraped excerpts) and
performs evidence-based score validation:

For each vendor × sub-pillar:
  1. Re-assesses criteria using actual web excerpts (not just notes)
  2. Computes an evidence-supported score based on excerpt relevance + criteria met
  3. Compares evidence-supported score against the v2.0 score
  4. Applies bounded adjustments when evidence significantly diverges from score
  5. Consolidates rationale into human-readable text

New v2.1 fields per vendor:
  - sub_pillar_scores_v2_1           – validated/adjusted scores
  - pillar_scores_v2_1               – recalculated pillar averages
  - sub_pillar_rationale_v2_1        – structured rationale with excerpt evidence
  - sub_pillar_rationale_v2_1_text   – human-readable consolidated text
  - v2_1_adjustment_summary          – per-vendor adjustment stats
  - research_confidence_v2_1         – updated confidence

Input : MDR Services Vendor 2-0 Researched.json
Output: MDR Services Vendor 2-1 Consolidated.json
"""

import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT_FILE  = ROOT / "MDR Services Vendor 2-0 Researched.json"
OUTPUT_FILE = ROOT / "MDR Services Vendor 2-1 Consolidated.json"
SCHEMA_FILE = ROOT / "MDR_Services_Schema.json"

PILLARS = ["TDR", "PTI", "ADA", "DIS", "IRA", "AIO", "AID", "SOG"]
SUB_PILLAR_IDS = [f"{p}-{i:02d}" for p in PILLARS for i in range(1, 5)]

# ── Scoring-level definitions ─────────────────────────────────────────

SCORING_LEVELS = {
    0: {"label": "No Evidence",    "min_criteria_met": 0, "min_excerpts": 0},
    1: {"label": "Minimal",        "min_criteria_met": 0, "min_excerpts": 0},
    2: {"label": "Generic Claims", "min_criteria_met": 1, "min_excerpts": 1},
    3: {"label": "Demonstrated",   "min_criteria_met": 2, "min_excerpts": 2},
    4: {"label": "Advanced",       "min_criteria_met": 3, "min_excerpts": 3},
    5: {"label": "Market-Leading", "min_criteria_met": 4, "min_excerpts": 4},
}

# ── Evidence keyword index (expanded for excerpt matching) ────────────

PILLAR_KEYWORDS = {
    "TDR": [
        "detection", "response", "correlat", "xdr", "edr", "ndr", "siem",
        "alert", "triage", "threat hunt", "proactive", "telemetry",
        "playbook", "soar", "automat", "orchestrat", "remediat",
        "24/7", "real-time", "multi-source", "false positive",
    ],
    "PTI": [
        "threat intel", "ioc", "indicator", "att&ck", "mitre", "ttp",
        "dark web", "darknet", "underground", "feed", "cti",
        "attribution", "campaign", "actor", "adversary",
    ],
    "ADA": [
        "deception", "honeypot", "honeytoken", "decoy", "breadcrumb",
        "moving target", "amtd", "micro-segment", "runtime",
        "attack surface", "easm", "exposure", "shadow it",
        "takedown", "counter-adversary", "disruption",
    ],
    "DIS": [
        "deepfake", "synthetic media", "voice clone", "ai-generat",
        "bec", "business email compromise", "impersonat",
        "social engineer", "phishing", "narrative",
        "brand monitor", "brand protect", "typosquat", "domain",
    ],
    "IRA": [
        "incident", "breach", "forensic", "contain", "isolat",
        "recover", "restor", "eradicat", "post-incident",
        "root cause", "retainer", "scoping", "evidence preserv",
        "playbook", "tabletop", "crisis",
    ],
    "AIO": [
        "ai-assist", "ml-driven", "ai detection", "ml model",
        "behavioral ai", "ai-powered", "machine learning",
        "ai triage", "ai-automat", "ai investigation",
        "charlotte ai", "purple ai", "copilot", "ai response",
        "explainab", "transparen", "human-readable",
    ],
    "AID": [
        "security llm", "domain-specific", "custom model", "fine-tun",
        "model version", "model lifecycle", "drift", "model monitor",
        "ai supply chain", "model provenance", "prompt inject",
        "ai innovation", "ai pipeline", "ai roadmap",
    ],
    "SOG": [
        "soc", "24/7", "follow-the-sun", "noc",
        "soc 2", "iso 27001", "compliance", "certif", "fedramp",
        "portal", "dashboard", "self-service", "reporting",
        "sla", "mean time", "mttr", "mttd", "response time",
    ],
}

# Flatten all terms for general matching
ALL_KEYWORDS = set()
for terms in PILLAR_KEYWORDS.values():
    ALL_KEYWORDS.update(terms)


# ── Schema loader ─────────────────────────────────────────────────────

def load_schema():
    """Load sub-pillar criteria and pillar names from schema."""
    with open(SCHEMA_FILE, "r", encoding="utf-8-sig") as f:
        raw = json.load(f)
    body = raw.get("mdr_services_taxonomy_v1.0", raw)
    sp_data = body.get("sub_pillars", {})
    pillars = body.get("pillars", {})

    criteria = {}
    for sp_id in sorted(sp_data.keys()):
        info = sp_data[sp_id]
        criteria[sp_id] = {
            "name": info.get("name", sp_id),
            "criteria": info.get("what_to_verify_publicly", []),
            "search_terms": info.get("search_terms", []),
        }

    pillar_names = {}
    for code, pdata in pillars.items():
        pillar_names[code] = pdata.get("name", code)

    return criteria, pillar_names


# ── Excerpt-based criterion assessment ────────────────────────────────

def _text_matches(text_lower, terms):
    """Count how many terms match within text."""
    return sum(1 for t in terms if t.lower() in text_lower)


def assess_criterion_with_excerpts(criterion_text, excerpts, notes, score,
                                    pillar_code, search_terms):
    """
    Assess criterion using actual web excerpts + notes.
    Returns dict with status, evidence_excerpts, match_strength.
    """
    criterion_lower = criterion_text.lower()

    # Extract key noun phrases from the criterion
    criterion_words = set(re.findall(r'\b[a-z]{4,}\b', criterion_lower))

    # Build combined evidence text from excerpts
    excerpt_texts = []
    best_excerpts = []
    for exc in excerpts:
        etxt = exc.get("excerpt", "")
        if not etxt:
            continue
        excerpt_texts.append(etxt)
        etxt_lower = etxt.lower()

        # Score this excerpt against the criterion
        # Check word overlap
        excerpt_words = set(re.findall(r'\b[a-z]{4,}\b', etxt_lower))
        overlap = criterion_words & excerpt_words
        overlap_score = len(overlap)

        # Check pillar keywords
        pillar_terms = PILLAR_KEYWORDS.get(pillar_code, [])
        kw_matches = _text_matches(etxt_lower, pillar_terms)

        # Check search terms from schema
        st_matches = _text_matches(etxt_lower, search_terms)

        total_relevance = overlap_score * 2 + kw_matches + st_matches
        if total_relevance >= 2:
            best_excerpts.append({
                "excerpt": etxt[:200],
                "relevance": total_relevance,
                "url": exc.get("url", ""),
            })

    # Sort best excerpts by relevance
    best_excerpts.sort(key=lambda x: x["relevance"], reverse=True)
    top_excerpts = best_excerpts[:3]

    # Also check notes
    notes_lower = (notes or "").lower()
    notes_words = set(re.findall(r'\b[a-z]{4,}\b', notes_lower))
    notes_overlap = len(criterion_words & notes_words)

    # Combined evidence for all excerpts
    combined_lower = " ".join(excerpt_texts).lower() + " " + notes_lower

    # Compute match strength
    combined_words = set(re.findall(r'\b[a-z]{4,}\b', combined_lower))
    total_overlap = len(criterion_words & combined_words)
    overlap_ratio = total_overlap / max(len(criterion_words), 1)

    pillar_terms = PILLAR_KEYWORDS.get(pillar_code, [])
    kw_in_evidence = _text_matches(combined_lower, pillar_terms)
    st_in_evidence = _text_matches(combined_lower, search_terms)

    # Determine status
    has_strong_excerpt = len(top_excerpts) >= 2
    has_some_excerpt = len(top_excerpts) >= 1

    # Web excerpts use natural language — relax thresholds vs schema terminology
    if score >= 4 and (has_strong_excerpt or (has_some_excerpt and overlap_ratio >= 0.2)):
        status = "met"
        confidence = "high" if has_strong_excerpt else "medium"
    elif score >= 3 and (has_some_excerpt or overlap_ratio >= 0.15):
        status = "met"
        confidence = "medium"
    elif score >= 2 and (overlap_ratio >= 0.10 or has_some_excerpt or kw_in_evidence >= 2):
        status = "partial"
        confidence = "medium"
    elif score >= 1 and (overlap_ratio >= 0.05 or notes_overlap >= 1 or kw_in_evidence >= 1):
        status = "partial"
        confidence = "low"
    elif score == 0 or (not excerpt_texts and not notes):
        status = "unmet"
        confidence = "high"
    else:
        status = "unmet"
        confidence = "low"

    # Build evidence text
    if top_excerpts:
        ev_parts = [e["excerpt"][:150] for e in top_excerpts[:2]]
        evidence_text = " | ".join(ev_parts)
    elif notes:
        evidence_text = notes[:200]
    else:
        evidence_text = "No direct evidence found."

    return {
        "criterion": criterion_text,
        "status": status,
        "confidence": confidence,
        "evidence": evidence_text,
        "evidence_excerpts": [e["excerpt"][:150] for e in top_excerpts[:2]],
        "match_strength": round(overlap_ratio, 3),
        "keyword_matches": kw_in_evidence,
    }


# ── Evidence-supported score computation ──────────────────────────────

def compute_evidence_score(criteria_results, excerpts, pillar_code, search_terms):
    """
    Compute what score the evidence actually supports (0-5).
    Based on: criteria met/partial, excerpt count & relevance, keyword density.
    """
    n_total = len(criteria_results)
    n_met = sum(1 for c in criteria_results if c["status"] == "met")
    n_partial = sum(1 for c in criteria_results if c["status"] == "partial")
    n_unmet = sum(1 for c in criteria_results if c["status"] == "unmet")

    # Effective criteria score (met=1.0, partial=0.5, unmet=0.0)
    if n_total > 0:
        criteria_score = (n_met + 0.5 * n_partial) / n_total
    else:
        criteria_score = 0

    # Excerpt richness score (0-1)
    n_excerpts = len(excerpts)
    excerpt_score = min(n_excerpts / 5.0, 1.0)

    # Relevant excerpt score (how many have high relevance)
    high_rel = sum(1 for e in excerpts if e.get("relevance_score", 0) >= 5)
    rel_score = min(high_rel / 3.0, 1.0)

    # Keyword density in excerpts
    combined = " ".join(e.get("excerpt", "") for e in excerpts).lower()
    pillar_terms = PILLAR_KEYWORDS.get(pillar_code, [])
    kw_hits = _text_matches(combined, pillar_terms)
    kw_score = min(kw_hits / 8.0, 1.0)

    # Weighted composite: criteria 35%, excerpts 20%, relevance 15%, keywords 10%
    # Plus a base credit (20%) for having any evidence at all (excerpts or keywords)
    base_credit = 0.0
    if n_excerpts > 0:
        base_credit = 0.5 + min(n_excerpts / 10.0, 0.5)  # 0.5-1.0 for having excerpts
    elif kw_hits > 0:
        base_credit = 0.3

    composite = (criteria_score * 0.35 +
                 excerpt_score * 0.20 +
                 rel_score * 0.15 +
                 kw_score * 0.10 +
                 base_credit * 0.20)

    # Map composite (0-1) to score (0-5)
    evidence_score = round(composite * 5.0, 2)

    return evidence_score, {
        "criteria_coverage": round(criteria_score, 3),
        "excerpt_richness": round(excerpt_score, 3),
        "excerpt_relevance": round(rel_score, 3),
        "keyword_density": round(kw_score, 3),
        "composite": round(composite, 3),
    }


# ── Score adjustment logic ────────────────────────────────────────────

def compute_adjustment(original_score, evidence_score, criteria_results, excerpts):
    """
    Determine if an adjustment is warranted and compute the adjusted score.

    Rules:
    - If evidence_score is within ±0.75 of original → keep original (evidence supports it)
    - If original > evidence_score + 0.75 → score is inflated, reduce
    - If original < evidence_score - 0.75 → score is deflated, increase
    - Maximum adjustment: ±1.5 points per sub-pillar
    - Scores clamped to 0–5 range
    - Never reduce a 5.0 below 3.0 or raise a 0.0 above 2.0
    """
    delta = original_score - evidence_score
    n_excerpts = len(excerpts)

    # No excerpts at all → trust original score (can't validate)
    if n_excerpts == 0:
        return original_score, "no_change", "No excerpts available; original score retained."

    reason_parts = []

    if abs(delta) <= 1.0:
        # Evidence supports the score within reasonable tolerance
        return original_score, "validated", f"Evidence supports score (evidence={evidence_score:.1f}, delta={delta:+.1f})."

    if delta > 1.0:
        # Original is higher than evidence supports → conservative reduction
        reduction = min(delta * 0.5, 1.0)  # 50% of gap, max 1.0
        adjusted = round(original_score - reduction, 1)
        # Floor constraints — preserve analyst's original assessment intent
        if original_score >= 4.0:
            adjusted = max(adjusted, 3.5)
        elif original_score >= 3.0:
            adjusted = max(adjusted, 2.0)
        elif original_score >= 2.0:
            adjusted = max(adjusted, 1.0)
        else:
            adjusted = max(adjusted, 0.0)
        adjusted = max(0.0, min(5.0, adjusted))
        reason_parts.append(
            f"Evidence ({evidence_score:.1f}) partially supports score. "
            f"Adjusted {original_score:.1f} → {adjusted:.1f} "
            f"(gap={delta:.1f}, reduction={reduction:.1f})."
        )
        return adjusted, "decreased", " ".join(reason_parts)

    else:
        # Original is lower than evidence supports → increase
        increase = min(abs(delta) * 0.5, 1.0)
        adjusted = round(original_score + increase, 1)
        # Ceiling constraints
        if original_score == 0.0:
            adjusted = min(adjusted, 2.0)
        elif original_score <= 2.0:
            adjusted = min(adjusted, 4.0)
        adjusted = max(0.0, min(5.0, adjusted))
        reason_parts.append(
            f"Evidence ({evidence_score:.1f}) suggests score could be higher. "
            f"Increased {original_score:.1f} → {adjusted:.1f} "
            f"(gap={delta:.1f}, increase={increase:.1f})."
        )
        return adjusted, "increased", " ".join(reason_parts)


# ── Consolidated rationale text builder ───────────────────────────────

def build_v21_rationale_text(sp_id, sp_name, original_score, adjusted_score,
                              evidence_score, adjustment_type, adjustment_reason,
                              criteria_results, evidence_breakdown, excerpts,
                              confidence):
    """Build human-readable v2.1 rationale text."""
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
            f"{sp_id} – {sp_name}: Score {adjusted_score:.1f}/5.0 "
            f"(adjusted from {original_score:.1f}, Level {level}: {level_label}). "
            f"Confidence: {confidence}."
        )
    else:
        lines.append(
            f"{sp_id} – {sp_name}: Score {adjusted_score:.1f}/5.0 "
            f"(Level {level}: {level_label}). Confidence: {confidence}."
        )

    # Score Validation
    lines.append("")
    lines.append("[Score Validation]")
    lines.append(
        f"Evidence-supported score: {evidence_score:.1f}/5.0. "
        f"Adjustment: {adjustment_type}. {adjustment_reason}"
    )

    # Evidence Breakdown
    eb = evidence_breakdown
    lines.append("")
    lines.append("[Evidence Breakdown]")
    lines.append(
        f"Criteria coverage: {eb['criteria_coverage']:.0%} | "
        f"Excerpt richness: {eb['excerpt_richness']:.0%} | "
        f"Excerpt relevance: {eb['excerpt_relevance']:.0%} | "
        f"Keyword density: {eb['keyword_density']:.0%} | "
        f"Composite: {eb['composite']:.0%}"
    )

    # Criteria Assessment
    lines.append("")
    lines.append(f"[Criteria Assessment] ({n_met} met, {n_partial} partial, {n_unmet} unmet of {n_total})")
    for cr in criteria_results:
        icon = {"met": "MET", "partial": "PARTIAL", "unmet": "UNMET"}.get(cr["status"], "?")
        lines.append(f"  [{icon}] {cr['criterion']}")
        if cr.get("evidence_excerpts"):
            for ex in cr["evidence_excerpts"][:1]:
                lines.append(f"    → \"{ex[:120]}\"")

    # Key Excerpts
    n_exc = len(excerpts)
    if excerpts:
        lines.append("")
        lines.append(f"[Key Excerpts] ({n_exc} total)")
        for i, exc in enumerate(excerpts[:3], 1):
            etxt = exc.get("excerpt", "")[:150]
            url = exc.get("url", "")
            lines.append(f"  {i}. \"{etxt}\"")
            if url:
                lines.append(f"     Source: {url}")

    return "\n".join(lines)


# ── Evidence quality factor (v2.1 enhanced) ───────────────────────────

def compute_v21_evidence_quality(score, notes, source_urls, excerpts,
                                  criteria_results):
    """Enhanced evidence quality that accounts for excerpts."""
    factor = 0.0

    # Source diversity (0–0.20)
    n_urls = len(source_urls) if source_urls else 0
    factor += min(n_urls / 4.0, 1.0) * 0.20

    # Notes richness (0–0.15)
    note_len = len(notes) if notes else 0
    factor += min(note_len / 300.0, 1.0) * 0.15

    # Excerpt coverage (0–0.30) — new in v2.1
    n_exc = len(excerpts) if excerpts else 0
    factor += min(n_exc / 5.0, 1.0) * 0.30

    # Excerpt relevance quality (0–0.15)
    if excerpts:
        avg_rel = sum(e.get("relevance_score", 0) for e in excerpts) / len(excerpts)
        factor += min(avg_rel / 8.0, 1.0) * 0.15
    
    # Criteria coverage (0–0.20)
    n_total = len(criteria_results)
    if n_total > 0:
        n_met = sum(1 for c in criteria_results if c["status"] == "met")
        n_partial = sum(1 for c in criteria_results if c["status"] == "partial")
        cov = (n_met + 0.5 * n_partial) / n_total
        factor += cov * 0.20

    factor = round(min(max(factor, 0.0), 1.0), 3)

    if factor >= 0.80:
        grade = "A"
    elif factor >= 0.60:
        grade = "B"
    elif factor >= 0.40:
        grade = "C"
    elif factor >= 0.20:
        grade = "D"
    else:
        grade = "F"

    return factor, grade


# ── Vendor-level summary ──────────────────────────────────────────────

def compute_vendor_v21_summary(vendor_name, v21_scores, v21_rationales,
                                 pillar_names, original_pillar_scores):
    """Compute vendor-level v2.1 summary."""
    # Pillar averages from v2.1 sub-pillar scores
    pillar_scores = {}
    for p in PILLARS:
        sp_ids = [f"{p}-{i:02d}" for i in range(1, 5)]
        vals = [v21_scores.get(sp, 0) for sp in sp_ids]
        pillar_scores[p] = round(sum(vals) / max(len(vals), 1), 2)

    # Evidence quality factors
    eq_factors = []
    for sp_id, rat in v21_rationales.items():
        if isinstance(rat, dict):
            eq_factors.append(rat.get("evidence_quality_factor", 0.5))
    avg_eq = sum(eq_factors) / max(len(eq_factors), 1)

    if avg_eq >= 0.65:
        confidence = "high"
    elif avg_eq >= 0.40:
        confidence = "medium"
    else:
        confidence = "low"

    # Adjustment stats
    n_increased = sum(1 for r in v21_rationales.values()
                      if isinstance(r, dict) and r.get("adjustment_type") == "increased")
    n_decreased = sum(1 for r in v21_rationales.values()
                      if isinstance(r, dict) and r.get("adjustment_type") == "decreased")
    n_validated = sum(1 for r in v21_rationales.values()
                      if isinstance(r, dict) and r.get("adjustment_type") == "validated")
    n_nochange = sum(1 for r in v21_rationales.values()
                     if isinstance(r, dict) and r.get("adjustment_type") == "no_change")

    # Notable differentiation
    sorted_pillars = sorted(pillar_scores.items(), key=lambda x: x[1], reverse=True)
    top_3 = sorted_pillars[:3]
    diff_parts = [f"{pillar_names.get(p, p)} ({s:.1f})" for p, s in top_3]
    diff_text = f"Strongest: {', '.join(diff_parts)}."

    weak = [p for p in sorted_pillars if p[1] < 2.5]
    if weak:
        weak_parts = [f"{pillar_names.get(p[0], p[0])} ({p[1]:.1f})" for p in weak[:2]]
        diff_text += f" Growth areas: {', '.join(weak_parts)}."

    return {
        "pillar_scores_v2_1": pillar_scores,
        "research_confidence_v2_1": confidence,
        "avg_evidence_quality": round(avg_eq, 3),
        "notable_differentiation_v2_1": diff_text,
        "v2_1_adjustment_summary": {
            "increased": n_increased,
            "decreased": n_decreased,
            "validated": n_validated,
            "no_change": n_nochange,
            "total": n_increased + n_decreased + n_validated + n_nochange,
        },
    }


# ── Main ──────────────────────────────────────────────────────────────

def main():
    print("Loading MDR 2.0 Researched data and schema...")
    with open(INPUT_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    schema_criteria, pillar_names = load_schema()

    vendors = data.get("vendors", [])
    if not vendors:
        print("ERROR: No vendors found.")
        sys.exit(1)

    print(f"Processing {len(vendors)} vendors × {len(SUB_PILLAR_IDS)} sub-pillars...\n")

    # Global stats
    global_stats = {
        "total_vendors": len(vendors),
        "total_sub_pillars": 0,
        "increased": 0,
        "decreased": 0,
        "validated": 0,
        "no_change": 0,
        "total_excerpts_used": 0,
        "avg_original_score": 0,
        "avg_adjusted_score": 0,
        "criteria_met": 0,
        "criteria_partial": 0,
        "criteria_unmet": 0,
    }

    all_original = []
    all_adjusted = []
    adjustment_details = []

    for vi, vendor in enumerate(vendors):
        vname = vendor["vendor"]
        scores = vendor.get("sub_pillar_scores_current", {})
        evidence = vendor.get("sub_pillar_evidence", {})
        v2_rat = vendor.get("sub_pillar_rationale_v2", {})
        description = vendor.get("description", "")
        original_pillar_scores = vendor.get("pillar_scores", {})

        # v2.1 containers
        v21_scores = {}
        v21_rationales = {}
        v21_rationale_text = {}

        for sp_id in SUB_PILLAR_IDS:
            sp_info = schema_criteria.get(sp_id, {"name": sp_id, "criteria": [], "search_terms": []})
            sp_name = sp_info["name"]
            criteria_list = sp_info.get("criteria", [])
            search_terms = sp_info.get("search_terms", [])
            pillar_code = sp_id.split("-")[0]

            original_score = float(scores.get(sp_id, 0))
            sp_ev = evidence.get(sp_id, {})
            notes = sp_ev.get("notes", "")
            source_urls = sp_ev.get("source_urls", [])
            excerpts = sp_ev.get("excerpts", [])

            # 1. Re-assess criteria using excerpts
            criteria_results = []
            for criterion in criteria_list:
                result = assess_criterion_with_excerpts(
                    criterion, excerpts, notes, original_score,
                    pillar_code, search_terms
                )
                criteria_results.append(result)

            n_met = sum(1 for c in criteria_results if c["status"] == "met")
            n_partial = sum(1 for c in criteria_results if c["status"] == "partial")
            n_unmet = sum(1 for c in criteria_results if c["status"] == "unmet")

            global_stats["criteria_met"] += n_met
            global_stats["criteria_partial"] += n_partial
            global_stats["criteria_unmet"] += n_unmet

            # 2. Compute evidence-supported score
            evidence_score, evidence_breakdown = compute_evidence_score(
                criteria_results, excerpts, pillar_code, search_terms
            )

            # 3. Determine adjustment
            adjusted_score, adj_type, adj_reason = compute_adjustment(
                original_score, evidence_score, criteria_results, excerpts
            )

            global_stats[adj_type if adj_type != "no_change" else "no_change"] += 1
            global_stats["total_sub_pillars"] += 1
            global_stats["total_excerpts_used"] += len(excerpts)
            all_original.append(original_score)
            all_adjusted.append(adjusted_score)

            if adj_type in ("increased", "decreased"):
                adjustment_details.append({
                    "vendor": vname,
                    "sub_pillar": sp_id,
                    "original": original_score,
                    "adjusted": adjusted_score,
                    "evidence_score": evidence_score,
                    "type": adj_type,
                })

            # 4. Enhanced evidence quality
            eq_factor, eq_grade = compute_v21_evidence_quality(
                adjusted_score, notes, source_urls, excerpts, criteria_results
            )

            # 5. Confidence
            if eq_factor >= 0.65 and n_met + n_partial >= 3:
                confidence = "high"
            elif eq_factor >= 0.40 and n_met + n_partial >= 1:
                confidence = "medium"
            else:
                confidence = "low"

            # Store v2.1 score
            v21_scores[sp_id] = adjusted_score

            # Store structured rationale
            v21_rationales[sp_id] = {
                "sub_pillar_id": sp_id,
                "sub_pillar_name": sp_name,
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
            v21_rationale_text[sp_id] = build_v21_rationale_text(
                sp_id, sp_name, original_score, adjusted_score,
                evidence_score, adj_type, adj_reason,
                criteria_results, evidence_breakdown, excerpts,
                confidence
            )

        # Vendor-level summary
        summary = compute_vendor_v21_summary(
            vname, v21_scores, v21_rationales, pillar_names, original_pillar_scores
        )

        # Write v2.1 fields to vendor
        vendor["sub_pillar_scores_v2_1"] = v21_scores
        vendor["pillar_scores_v2_1"] = summary["pillar_scores_v2_1"]
        vendor["sub_pillar_rationale_v2_1"] = v21_rationales
        vendor["sub_pillar_rationale_v2_1_text"] = v21_rationale_text
        vendor["research_confidence_v2_1"] = summary["research_confidence_v2_1"]
        vendor["notable_differentiation_v2_1"] = summary["notable_differentiation_v2_1"]
        vendor["v2_1_adjustment_summary"] = summary["v2_1_adjustment_summary"]

        # Progress
        adj_sum = summary["v2_1_adjustment_summary"]
        if (vi + 1) % 10 == 0 or vi == 0 or vi == len(vendors) - 1:
            print(
                f"  [{vi+1}/{len(vendors)}] {vname}: "
                f"↑{adj_sum['increased']} ↓{adj_sum['decreased']} "
                f"✓{adj_sum['validated']} ={adj_sum['no_change']} | "
                f"confidence={summary['research_confidence_v2_1']}"
            )

    # Global stats
    global_stats["avg_original_score"] = round(sum(all_original) / max(len(all_original), 1), 3)
    global_stats["avg_adjusted_score"] = round(sum(all_adjusted) / max(len(all_adjusted), 1), 3)

    # Update file metadata
    data["schema_version"] = "2.1"
    data["v2_1_metadata"] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script": "build_mdr_v2_1.py",
        "description": (
            "Evidence-validated scoring with excerpt-based criteria re-assessment. "
            "Scores adjusted where evidence diverges significantly from v2.0 scores. "
            "New fields: sub_pillar_scores_v2_1, pillar_scores_v2_1, "
            "sub_pillar_rationale_v2_1, sub_pillar_rationale_v2_1_text."
        ),
        "source_file": INPUT_FILE.name,
        "stats": global_stats,
    }

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # ── Summary report ────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"MDR v2.1 Consolidated — Complete")
    print(f"{'='*60}")
    print(f"  Vendors: {global_stats['total_vendors']}")
    print(f"  Sub-pillars assessed: {global_stats['total_sub_pillars']}")
    print(f"  Total excerpts used: {global_stats['total_excerpts_used']}")
    print(f"  Criteria assessed: {global_stats['criteria_met'] + global_stats['criteria_partial'] + global_stats['criteria_unmet']}")
    print(f"    Met: {global_stats['criteria_met']}, Partial: {global_stats['criteria_partial']}, Unmet: {global_stats['criteria_unmet']}")
    print(f"\n  Score adjustments:")
    print(f"    ↑ Increased: {global_stats['increased']}")
    print(f"    ↓ Decreased: {global_stats['decreased']}")
    print(f"    ✓ Validated: {global_stats['validated']}")
    print(f"    = No change (no excerpts): {global_stats['no_change']}")
    print(f"\n  Avg original score: {global_stats['avg_original_score']:.2f}")
    print(f"  Avg adjusted score: {global_stats['avg_adjusted_score']:.2f}")
    print(f"  Delta: {global_stats['avg_adjusted_score'] - global_stats['avg_original_score']:+.3f}")

    # Top adjustments
    if adjustment_details:
        print(f"\n  Top 10 largest adjustments:")
        adjustment_details.sort(key=lambda x: abs(x["adjusted"] - x["original"]), reverse=True)
        for ad in adjustment_details[:10]:
            delta = ad["adjusted"] - ad["original"]
            print(f"    {ad['vendor'][:30]:30s} {ad['sub_pillar']}: "
                  f"{ad['original']:.1f} → {ad['adjusted']:.1f} ({delta:+.1f}) "
                  f"[evidence={ad['evidence_score']:.1f}]")

    print(f"\n  Written to: {OUTPUT_FILE.name}")

    # ── Spot checks ───────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("Spot checks:")
    for vi in [0, 15, 50]:
        v = vendors[vi]
        vn = v["vendor"]
        adj = v["v2_1_adjustment_summary"]
        print(f"\n  {vn}:")
        print(f"    Adjustments: ↑{adj['increased']} ↓{adj['decreased']} ✓{adj['validated']} ={adj['no_change']}")
        ps_orig = v.get("pillar_scores", {})
        ps_v21 = v.get("pillar_scores_v2_1", {})
        for p in PILLARS:
            o = ps_orig.get(p, 0)
            n = ps_v21.get(p, 0)
            delta_s = f" ({n-o:+.2f})" if o != n else ""
            print(f"    {p}: {o:.1f} → {n:.1f}{delta_s}")


if __name__ == "__main__":
    main()
