"""
_revalidate_precyber_scoring.py
================================
Strict re-scoring of Preemptive Cybersecurity vendor sub-pillars to fix score
inflation discovered in the v2 rationale pipeline.

Symptom: Mandiant AMT-01 = 3.50/5.0 with 0/5 schema criteria met, NOT in
expected_coverage, content was generic "privileged access" threat-intel noise.
Audit shows 258 such cells across 47 vendors.

Reads existing data first:
  - "Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json"   (full 24-sub-pillar evidence + scores, includes SVC + *-05)
  - "Preemptive_Cybersecurity_Schema_v2.json"                (criteria definitions)

Writes:
  - "Preemptive Cybersecurity Vendor 2-3 Holistic Validated.json"  (corrected scores)
  - "precyber_score_delta_report.json"                       (per-cell deltas with reasons)
  - "precyber_research_targets.json"                         (cells flagged for fresh scraping)

Strict rubric tied to schema (criterion-satisfaction first, keyword hits secondary):
  L0  excerpts==0 AND no terms.
  L1  excerpts/terms present but met=0 AND partial=0 AND schema_hits<2.
  L2  schema_hits>=2 OR partial>=1 (some criterion language present, none fully met).
  L3  met >= 1 (at least one criterion verifiably satisfied).
  L4  met >= 2 AND schema_hits >= 2 AND specificity>=3 AND (metrics OR arch).
  L5  met >= 3 AND schema_hits >= 3 AND coverage>=0.6 AND specificity>=4 AND metrics AND arch.
  Within level: +0..0.5 from (met + 0.3*partial)/total, snapped to 0.25.
  IMPORTANT: schema_criteria_hits alone (single keyword matches) NEVER promote past L2.
  Vendor-claimed coverage (in_expected_coverage) does not bypass the met>=1 requirement
  for L3; instead it lifts the within-level adjustment by +0.25 when partial>=1.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json"
SCHEMA_FILE = ROOT / "Preemptive_Cybersecurity_Schema_v2.json"
# v2-3: holistic per-criterion evaluator (anchor + density + multi-excerpt
# corroboration) with structured rationale overlay. Earlier v2-2 file kept
# as the prior strict-only baseline for diff/audit.
DST = ROOT / "Preemptive Cybersecurity Vendor 2-3 Holistic Validated.json"
DELTA = ROOT / "precyber_score_delta_report_v23.json"
TARGETS = ROOT / "precyber_research_targets_v23.json"

METRIC_PATTERNS = re.compile(
    r"\b(\d+\.?\d*\s*(%|percent|millisecond|ms|second|minute|latency|throughput"
    r"|accuracy|precision|recall|f1|sla|uptime|reduction|improvement|coverage"
    r"|false.?positive|false.?negative|benchmark))"
    r"|\b(iso\s*\d|soc\s*\d|nist|fedramp|gdpr|hipaa|pci.dss)",
    re.IGNORECASE,
)
ARCHITECTURE_PATTERNS = re.compile(
    r"\b(api|sdk|rest|graphql|microservice|container|kubernetes|helm|terraform"
    r"|ci/cd|pipeline|webhook|plugin|connector|integration|real.?time|streaming"
    r"|multi.?tenant|on.?prem|cloud.?native|saas|paas|agent|orchestrat)",
    re.IGNORECASE,
)

STOPWORDS = {
    "with", "from", "into", "that", "this", "based", "across", "their", "them",
    "they", "have", "been", "using", "than", "more", "most", "such", "also",
    "system", "systems", "your", "ours", "where", "which", "while",
}


def evaluate_criterion(criterion: str, text_l: str) -> str:
    """Legacy single-text evaluator retained for back-compat.

    Most scoring now goes through ``evaluate_criterion_holistic`` which works
    over the full excerpt list and tracks anchor-phrase + concept density +
    multi-excerpt corroboration. This one-shot version is kept for callers
    that only have a flattened text blob.
    """
    words = [
        w for w in re.findall(r"[a-z][a-z0-9\-]{3,}", criterion.lower())
        if w not in STOPWORDS
    ]
    if not words:
        return "unmet"
    word_hits = sum(1 for w in words if w in text_l)
    word_coverage = word_hits / len(words)

    tokens = criterion.lower().split()
    bigram_hit = False
    for i in range(len(tokens) - 1):
        bg = f"{tokens[i]} {tokens[i+1]}".strip(".,;:")
        if len(bg) > 8 and bg in text_l:
            bigram_hit = True
            break

    if word_coverage >= 0.6 and bigram_hit:
        return "met"
    if word_coverage >= 0.4 and (bigram_hit or word_hits >= 3):
        return "partial"
    return "unmet"


# Minimum excerpt length (chars) before an excerpt is allowed to drive a
# 'met' or 'partial' verdict. Short marketing taglines (e.g., 65 chars)
# can mention concept words but never *verify* a capability claim.
_MIN_EXCERPT_LEN_FOR_SUPPORT = 80
_MIN_EXCERPT_LEN_FOR_STRONG  = 140


def _criterion_anchors(criterion: str, search_terms: list[str]) -> list[str]:
    """Return the set of anchor phrases that count as 'capability mention'.

    Includes:
      * the last 3 content words of the criterion (its specific claim)
      * any parenthetical inside the criterion (often the key term)
      * every multi-word phrase from the sub-pillar's ``search_terms`` (these
        are the schema-curated synonyms vendors actually use in marketing)
      * single-word search_terms longer than 6 chars (e.g., 'honeypot',
        'deception', 'onboarding') — short enough to over-match, so we keep
        only distinctive ones
    """
    out: list[str] = []
    seen: set[str] = set()

    cl = criterion.lower().strip()
    paren = re.search(r"\(([^)]+)\)", cl)
    if paren:
        inner = paren.group(1).strip()
        if inner and inner not in seen:
            seen.add(inner)
            out.append(inner)
    cl_clean = re.sub(r"\s*\([^)]*\)\s*", " ", cl).strip()
    toks = [t for t in re.findall(r"[a-z][a-z0-9\-]+", cl_clean)
            if t not in STOPWORDS and len(t) > 2]
    if len(toks) >= 3:
        a = " ".join(toks[-3:])
    elif toks:
        a = " ".join(toks)
    else:
        a = cl_clean
    if a and a not in seen:
        seen.add(a)
        out.append(a)

    for term in (search_terms or []):
        tl = term.lower().strip()
        if not tl or tl in seen:
            continue
        if " " in tl or "-" in tl:
            seen.add(tl)
            out.append(tl)
        elif len(tl) >= 7 and tl not in STOPWORDS:
            seen.add(tl)
            out.append(tl)
    return out


def _criterion_anchor(criterion: str) -> str:
    """Back-compat: return only the criterion-derived anchor (no search_terms)."""
    anchors = _criterion_anchors(criterion, [])
    return anchors[0] if anchors else criterion.lower().strip()


def _concept_tokens(criterion: str, search_terms: list[str]) -> set[str]:
    """Build the concept vocabulary for a criterion: criterion words plus
    sub-pillar search_terms (treated as synonyms / related concepts)."""
    out: set[str] = set()
    for src in [criterion] + list(search_terms or []):
        for tok in re.findall(r"[a-z][a-z0-9\-]+", src.lower()):
            if tok not in STOPWORDS and len(tok) > 3:
                out.add(tok)
    return out


def _anchor_present(anchor: str, text_l: str) -> bool:
    """Anchor matches if the exact phrase OR any consecutive 2-word slice of it
    appears in the excerpt. Single-word anchors require a whole-word match."""
    if not anchor:
        return False
    if anchor in text_l:
        return True
    parts = anchor.split()
    if len(parts) == 1:
        return bool(re.search(rf"\b{re.escape(parts[0])}\b", text_l))
    for i in range(len(parts) - 1):
        bg = f"{parts[i]} {parts[i+1]}"
        if len(bg) >= 7 and bg in text_l:
            return True
    return False


def evaluate_criterion_holistic(
    criterion: str,
    excerpts: list[dict],
    search_terms: list[str],
) -> dict:
    """Score a single criterion against the full excerpt list.

    Returns:
        {
          status: 'met' | 'partial' | 'unmet',
          evidence: best supporting excerpt (truncated, str),
          evidence_url: source URL of best excerpt,
          confidence: 'high' | 'medium' | 'low',
          signals: { anchor, anchor_hits, density_max,
                     strong_excerpts, partial_excerpts }
        }

    Logic:
      * For each excerpt: compute anchor_hit, concept density (# concept tokens
        present), and an excerpt support-score 0/1/2/3.
      * 'met' requires either (a) at least one strong (score=3) excerpt that is
        long-enough AND another supporting excerpt, or (b) a single very rich
        excerpt (>=200 chars, anchor + density>=4).
      * 'partial' requires at least one excerpt at score>=2 (anchor hit OR
        density>=4) of sufficient length.
      * 'unmet' otherwise.
    """
    anchors = _criterion_anchors(criterion, search_terms)
    primary_anchor = anchors[0] if anchors else ""
    concepts = _concept_tokens(criterion, search_terms)

    best = {"score": 0, "snippet": "", "url": "", "density": 0}
    anchor_hits = 0
    strong_excerpts = 0
    partial_excerpts = 0
    density_max = 0

    for ex in excerpts or []:
        if not isinstance(ex, dict):
            continue
        txt = ex.get("excerpt") or ex.get("text") or ""
        if not txt:
            continue
        txt_l = txt.lower()
        long_enough = len(txt) >= _MIN_EXCERPT_LEN_FOR_SUPPORT
        rich = len(txt) >= _MIN_EXCERPT_LEN_FOR_STRONG
        # An excerpt anchor-hits if ANY anchor (criterion or search_term) is present
        a_hit = any(_anchor_present(a, txt_l) for a in anchors)
        density = sum(1 for c in concepts if re.search(rf"\b{re.escape(c)}\b", txt_l))
        if a_hit:
            anchor_hits += 1
        if density > density_max:
            density_max = density

        if a_hit and density >= 3 and rich:
            score = 3
            strong_excerpts += 1
        elif a_hit and density >= 2 and long_enough:
            score = 2
            partial_excerpts += 1
        elif density >= 6 and rich:
            # Very rich passage covering many related concepts even without
            # the exact anchor phrase (e.g., paraphrased capability description).
            score = 2
            partial_excerpts += 1
        elif a_hit or (density >= 3 and long_enough):
            score = 1
        else:
            score = 0

        if score > best["score"] or (score == best["score"] and len(txt) > len(best["snippet"])):
            best = {"score": score, "snippet": txt, "url": ex.get("url", "") or "", "density": density}

    if strong_excerpts >= 1 and (strong_excerpts + partial_excerpts) >= 2:
        status = "met"
    elif best["score"] >= 3 and len(best["snippet"]) >= 200:
        status = "met"
    elif best["score"] >= 2 or strong_excerpts >= 1:
        status = "partial"
    else:
        status = "unmet"

    if status == "met":
        confidence = "high" if (strong_excerpts >= 2 or len(best["snippet"]) >= 250) else "medium"
    elif status == "partial":
        confidence = "medium" if (anchor_hits >= 1 and best["score"] >= 2) else "low"
    else:
        confidence = "low"

    snippet = best["snippet"].strip()
    if len(snippet) > 220:
        snippet = snippet[:217].rstrip() + "\u2026"
    return {
        "status": status,
        "evidence": snippet,
        "evidence_url": best["url"],
        "confidence": confidence,
        "signals": {
            "anchor": primary_anchor,
            "anchors_used": anchors,
            "anchor_hits": anchor_hits,
            "density_max": density_max,
            "strong_excerpts": strong_excerpts,
            "partial_excerpts": partial_excerpts,
        },
    }


def _combined_text(evidence_block: dict) -> str:
    parts: list[str] = []
    for ex in evidence_block.get("excerpts") or []:
        if isinstance(ex, dict):
            txt = ex.get("excerpt") or ex.get("text") or ""
            if txt:
                parts.append(txt)
    return " ".join(parts)


def assign_level(
    *,
    schema_criteria_hits: int,
    pillar_term_hits: int,
    excerpts: int,
    met_count: int,
    partial_count: int,
    total_criteria: int,
    specificity: float,
    has_metrics: bool,
    has_arch: bool,
    in_expected_coverage: bool,
) -> tuple[int, str]:
    coverage = (met_count + partial_count * 0.5) / max(total_criteria, 1)

    if excerpts == 0 and pillar_term_hits == 0 and schema_criteria_hits == 0:
        return 0, "No evidence excerpts and no pillar/schema term matches."

    if (schema_criteria_hits >= 3 and met_count >= 2
            and coverage >= 0.6 and specificity >= 4.0
            and has_metrics and has_arch):
        return 5, (f"Market-leading: {met_count}/{total_criteria} fully met, "
                   f"coverage={coverage:.0%}, schema_hits={schema_criteria_hits}, "
                   f"metrics+architecture present.")

    if (met_count >= 2 and schema_criteria_hits >= 2
            and specificity >= 3.0 and (has_metrics or has_arch)):
        return 4, (f"Advanced: {met_count}/{total_criteria} criteria met, "
                   f"schema_hits={schema_criteria_hits}, coverage={coverage:.0%}.")

    # L3 STRICTLY requires at least one criterion verifiably met.
    # Bare schema-keyword hits do NOT promote past L2 (prevents the prior
    # inflation where a single word like "rotation" anywhere in excerpts
    # produced a 3.0 with 0/N criteria met).
    if met_count >= 1:
        return 3, (f"Demonstrated: {met_count}/{total_criteria} criteria met, "
                   f"schema_hits={schema_criteria_hits}, "
                   f"pillar_terms={pillar_term_hits}.")

    # L2: language hints present but no criterion fully verified.
    if schema_criteria_hits >= 2 or partial_count >= 1:
        return 2, (f"Partial language: schema_hits={schema_criteria_hits}, "
                   f"{partial_count} partial / 0 met of {total_criteria}; "
                   f"no criterion verifiably satisfied.")

    if pillar_term_hits >= 1 or excerpts >= 1 or schema_criteria_hits >= 1:
        return 1, (f"Minimal: {pillar_term_hits} pillar terms, "
                   f"schema_hits={schema_criteria_hits}, {excerpts} excerpts; "
                   f"no schema criterion met or partially met.")

    return 1, "Minimal: only background mentions; no preemptive depth."


def fine_grain(level: int, met_count: int, partial_count: int, total_criteria: int) -> float:
    if total_criteria == 0:
        return float(level)
    # L0/L1 have no headroom (would imply 0 met/partial anyway).
    if level <= 1:
        return float(level)
    fine = (met_count + 0.3 * partial_count) / total_criteria
    adjusted = float(level) + 0.5 * min(fine, 1.0)
    return round(adjusted * 4) / 4


def rescore_subpillar(
    sid: str,
    sp_def: dict,
    evidence_block: dict | None,
    in_expected_coverage: bool,
    original_score: float,
) -> dict:
    evidence_block = evidence_block or {}
    criteria = sp_def.get("what_to_verify_publicly", []) or []
    search_terms = sp_def.get("search_terms") or sp_def.get("terms") or []
    excerpts = evidence_block.get("excerpts") or []
    schema_criteria_hits = int(evidence_block.get("schema_criteria_hits", 0) or 0)
    pillar_term_hits = int(evidence_block.get("pillar_term_hits", 0) or 0)
    specificity = float(evidence_block.get("sub_pillar_specificity", 0) or 0)

    text = _combined_text(evidence_block)
    has_metrics = bool(METRIC_PATTERNS.search(text)) if text else False
    has_arch = bool(ARCHITECTURE_PATTERNS.search(text)) if text else False

    crit_results: list[dict] = []
    for c in criteria:
        h = evaluate_criterion_holistic(c, excerpts, search_terms)
        crit_results.append({
            "criterion": c,
            "status": h["status"],
            "evidence": h["evidence"],
            "evidence_url": h["evidence_url"],
            "confidence": h["confidence"],
            "signals": h["signals"],
        })
    met_count = sum(1 for r in crit_results if r["status"] == "met")
    partial_count = sum(1 for r in crit_results if r["status"] == "partial")
    total_criteria = len(crit_results)

    level, justification = assign_level(
        schema_criteria_hits=schema_criteria_hits,
        pillar_term_hits=pillar_term_hits,
        excerpts=len(excerpts),
        met_count=met_count,
        partial_count=partial_count,
        total_criteria=total_criteria,
        specificity=specificity,
        has_metrics=has_metrics,
        has_arch=has_arch,
        in_expected_coverage=in_expected_coverage,
    )
    new_score = fine_grain(level, met_count, partial_count, total_criteria)

    unique_urls = {(ex.get("url") if isinstance(ex, dict) else None) for ex in excerpts}
    unique_urls.discard(None)
    if met_count >= max(2, int(total_criteria * 0.4)) and len(unique_urls) >= 2:
        confidence = "high"
    elif met_count >= 1 or schema_criteria_hits >= 1:
        confidence = "medium"
    else:
        confidence = "low"

    delta = round(new_score - original_score, 2)
    needs_research = False
    research_reason = ""
    # Only flag for fresh research when there's a real evidence gap, not just
    # a downward correction of a previously inflated score.
    if in_expected_coverage and new_score < 3.0:
        needs_research = True
        research_reason = ("Vendor claims coverage but evidence weak; "
                           "needs targeted scraping.")
    elif new_score >= 4.0 and confidence == "low":
        needs_research = True
        research_reason = "High score but low confidence; needs corroboration."
    elif delta >= 1.0:
        # Score went UP without basis — suspicious, verify
        needs_research = True
        research_reason = (f"Score moved upward {original_score:.2f} → {new_score:.2f} "
                           f"(Δ{delta:+.2f}); verify against vendor docs.")

    rationale_text = (
        f"{sid} – {sp_def.get('name', sid)}: Score {new_score:.2f}/5.0 (Level {level}). "
        f"Confidence: {confidence}. {justification} "
        f"Criteria: {met_count} met / {partial_count} partial / "
        f"{total_criteria - met_count - partial_count} unmet of {total_criteria}. "
        f"Schema-criteria term hits: {schema_criteria_hits}; pillar terms: {pillar_term_hits}; "
        f"specificity: {specificity:.1f}; sources: {len(unique_urls)}; excerpts: {len(excerpts)}. "
        f"{'Vendor-claimed coverage. ' if in_expected_coverage else ''}"
        f"Original v2 score was {original_score:.2f} (Δ{delta:+.2f})."
    )

    # Build a structured rationale matching the UI's expected format
    # (static/app.js expects score_rationale, criteria_assessment with
    # {criterion,status,evidence}, key_evidence, confidence, etc.). This
    # overlays the legacy `sub_pillar_rationale_v2` so displayed text +
    # criteria badges + evidence stay coherent with the strict revalidation.
    grade = (
        "A" if confidence == "high" and new_score >= 4.0 else
        "B" if confidence == "high" or new_score >= 3.0 else
        "C" if confidence == "medium" else
        "D" if (excerpts and (pillar_term_hits or schema_criteria_hits)) else
        "F"
    )
    eq_factor = round(min(1.0, (
        0.30 * min(len(excerpts), 5) / 5
        + 0.25 * min(len(unique_urls), 4) / 4
        + 0.20 * (met_count / max(total_criteria, 1))
        + 0.15 * (partial_count / max(total_criteria, 1))
        + 0.10 * (1.0 if (has_metrics or has_arch) else 0.0)
    )), 2)
    eq_rationale = (
        f"Evidence quality: {int(eq_factor*100)}% — Grade {grade}. "
        f"{len(unique_urls)} source(s), {len(excerpts)} excerpt(s); "
        f"{met_count}/{total_criteria} criteria fully verified, "
        f"{partial_count} partially supported. "
        f"{'Metrics present. ' if has_metrics else ''}"
        f"{'Architectural specifics present. ' if has_arch else ''}"
        f"Holistic per-criterion matching (anchor phrase + concept density + "
        f"multi-excerpt corroboration)."
    )
    # Best key_evidence: distinct supporting snippets, longest first
    supported_snippets: list[str] = []
    seen: set[str] = set()
    for cr in crit_results:
        snip = (cr.get("evidence") or "").strip()
        if snip and snip not in seen and cr.get("status") in ("met", "partial"):
            seen.add(snip)
            supported_snippets.append(snip)
    if not supported_snippets:
        for ex in sorted(
            (e for e in excerpts if isinstance(e, dict)),
            key=lambda e: -len(e.get("excerpt") or e.get("text") or ""),
        ):
            t = (ex.get("excerpt") or ex.get("text") or "").strip()
            if t and t not in seen:
                seen.add(t)
                supported_snippets.append(t[:220])
            if len(supported_snippets) >= 3:
                break
    key_evidence = supported_snippets[:4]

    structured_rationale = {
        "score_rationale": rationale_text,
        "original_score": float(original_score),
        "adjusted_score": float(new_score),
        "adjustment_reason": (
            f"Strict revalidation (Level {level}): "
            f"{met_count}/{total_criteria} met, {partial_count} partial. "
            f"Holistic per-criterion match against schema 'what_to_verify' "
            f"with anchor-phrase + concept-density + multi-excerpt corroboration."
        ),
        "confidence": confidence,
        "evidence_quality_factor": eq_factor,
        "evidence_quality_grade": grade,
        "evidence_quality_rationale": eq_rationale,
        "excerpt_count": len(excerpts),
        "criteria_assessment": [
            {
                "criterion": cr["criterion"],
                "status": cr["status"],
                "evidence": cr.get("evidence", ""),
                "confidence": cr.get("confidence", "low"),
            }
            for cr in crit_results
        ],
        "key_evidence": key_evidence,
        "scoring_level": level,
        "scoring_level_justification": justification,
    }

    return {
        "sid": sid,
        "name": sp_def.get("name", sid),
        "original_score": original_score,
        "new_score": new_score,
        "delta": delta,
        "level": level,
        "level_justification": justification,
        "confidence": confidence,
        "criteria_assessment": crit_results,
        "met_count": met_count,
        "partial_count": partial_count,
        "total_criteria": total_criteria,
        "schema_criteria_hits": schema_criteria_hits,
        "pillar_term_hits": pillar_term_hits,
        "specificity": specificity,
        "has_metrics": has_metrics,
        "has_architecture": has_arch,
        "in_expected_coverage": in_expected_coverage,
        "needs_research": needs_research,
        "research_reason": research_reason,
        "rationale": rationale_text,
        "structured_rationale": structured_rationale,
    }


def main() -> int:
    raw = json.loads(SRC.read_text(encoding="utf-8"))
    # 2-1 file is {vendors: [...]}; 3-0 file is a flat list. Normalize.
    if isinstance(raw, list):
        data = {"vendors": raw}
    else:
        data = raw
    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    schema_root = schema["preemptive_cybersecurity_taxonomy_v2.0"]
    sub_pillars_def = schema_root["sub_pillars"]  # dict sid -> {name, what_to_verify_publicly, ...}
    pillars_def = schema_root.get("pillars", {})
    if isinstance(pillars_def, list):
        pillar_ids = [p.get("id") if isinstance(p, dict) else p for p in pillars_def]
    else:
        pillar_ids = list(pillars_def.keys())

    # Map sid -> pillar id (e.g., "AMT-01" -> "AMT")
    def pillar_of(sid: str) -> str:
        return sid.split("-")[0]

    delta_records = []
    research_targets = []
    vendors_out = []

    for v in data.get("vendors", []):
        v_new = dict(v)  # shallow copy; we'll overlay corrected fields
        name = v.get("vendor")
        expected = set(v.get("expected_coverage") or [])
        original_scores = (
            v.get("sub_pillar_scores_v2_researched")
            or v.get("sub_pillar_scores_current")
            or {}
        )
        ev_map = v.get("sub_pillar_evidence", {}) or {}

        new_sp_scores: dict[str, float] = {}
        new_rationales: dict[str, str] = {}
        new_structured: dict[str, dict] = {}
        sp_records: dict[str, dict] = {}

        for sid, sp_def in sub_pillars_def.items():
            orig = float(original_scores.get(sid, 0.0) or 0.0)
            rec = rescore_subpillar(
                sid=sid,
                sp_def=sp_def,
                evidence_block=ev_map.get(sid),
                in_expected_coverage=(sid in expected),
                original_score=orig,
            )
            new_sp_scores[sid] = rec["new_score"]
            new_rationales[sid] = rec["rationale"]
            new_structured[sid] = rec["structured_rationale"]
            sp_records[sid] = rec

            delta_records.append({
                "vendor": name,
                "sid": sid,
                **{k: rec[k] for k in (
                    "original_score", "new_score", "delta", "level",
                    "confidence", "met_count", "partial_count",
                    "total_criteria", "schema_criteria_hits",
                    "in_expected_coverage", "needs_research",
                    "research_reason",
                )},
            })
            if rec["needs_research"]:
                research_targets.append({
                    "vendor": name,
                    "sid": sid,
                    "sub_pillar": rec["name"],
                    "in_expected_coverage": rec["in_expected_coverage"],
                    "current_score": rec["new_score"],
                    "reason": rec["research_reason"],
                    "what_to_verify": sp_def.get("what_to_verify_publicly", []),
                    "search_terms": sp_def.get("search_terms", []),
                })

        # Pillar averages
        new_pillar_scores: dict[str, float] = {}
        sub_by_pillar: dict[str, list[float]] = defaultdict(list)
        for sid, sc in new_sp_scores.items():
            sub_by_pillar[pillar_of(sid)].append(sc)
        for pid, scores in sub_by_pillar.items():
            new_pillar_scores[pid] = round((sum(scores) / len(scores)) * 4) / 4

        v_new["sub_pillar_scores_validated_v22"] = new_sp_scores
        v_new["pillar_scores_validated_v22"] = new_pillar_scores
        v_new["sub_pillar_rationale_validated_v22"] = new_rationales
        v_new["sub_pillar_records_v22"] = sp_records
        # Make these the canonical "current" so the UI picks them up
        v_new["sub_pillar_scores_current"] = new_sp_scores
        v_new["pillar_scores"] = new_pillar_scores
        # Also overwrite the legacy v2_researched fields so the UI's
        # "v2_researched" view mode reflects corrected scores instead of
        # the original inflated values (the UI reads these directly in
        # static/app.js when mode === 'v2_researched').
        v_new["sub_pillar_scores_v2_researched"] = new_sp_scores
        v_new["pillar_scores_v2_researched"] = new_pillar_scores
        # Snapshot the pre-revalidation legacy values for audit only.
        if "sub_pillar_scores_v2_researched_pre_v22" not in v_new:
            v_new["sub_pillar_scores_v2_researched_pre_v22"] = (
                v.get("sub_pillar_scores_v2_researched") or {}
            )
            v_new["pillar_scores_v2_researched_pre_v22"] = (
                v.get("pillar_scores_v2_researched") or {}
            )
        # Overlay the structured rationale onto sub_pillar_rationale_v2 so the
        # UI's Evidence & Rationale view shows criteria badges + key evidence
        # consistent with the strict score (avoids the prior contradiction
        # where the displayed text claimed "3/5 met" while the underlying
        # criteria_assessment array showed 0/2/3 unmet for thin marketing
        # tagline evidence). Snapshot the original once for audit.
        if "sub_pillar_rationale_v2_pre_v22" not in v_new:
            v_new["sub_pillar_rationale_v2_pre_v22"] = v.get("sub_pillar_rationale_v2") or {}
        v_new["sub_pillar_rationale_v2"] = new_structured
        vendors_out.append(v_new)

    # Build output
    out = dict(data)
    out["vendors"] = vendors_out
    out["validation_metadata"] = {
        "source_file": SRC.name,
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "validator": "_revalidate_precyber_scoring.py",
        "rubric": "Strict schema-criteria gating; see file header.",
        "vendors_count": len(vendors_out),
        "subpillars_evaluated": len(vendors_out) * len(sub_pillars_def),
    }

    DST.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    # Delta report
    delta_summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "totals": {
            "cells": len(delta_records),
            "decreased": sum(1 for r in delta_records if r["delta"] < -0.1),
            "increased": sum(1 for r in delta_records if r["delta"] > 0.1),
            "unchanged": sum(1 for r in delta_records if abs(r["delta"]) <= 0.1),
            "needs_research": sum(1 for r in delta_records if r["needs_research"]),
            "avg_delta": round(sum(r["delta"] for r in delta_records) / max(len(delta_records), 1), 3),
        },
        "deltas": delta_records,
    }
    DELTA.write_text(json.dumps(delta_summary, indent=2, ensure_ascii=False), encoding="utf-8")

    targets_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(research_targets),
        "targets": research_targets,
    }
    TARGETS.write_text(json.dumps(targets_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Console summary
    print(f"[done] wrote {DST.name}")
    print(f"  Vendors          : {len(vendors_out)}")
    print(f"  Cells re-scored  : {len(delta_records)}")
    s = delta_summary["totals"]
    print(f"  Decreased        : {s['decreased']}")
    print(f"  Increased        : {s['increased']}")
    print(f"  Unchanged        : {s['unchanged']}")
    print(f"  Avg delta        : {s['avg_delta']:+.3f}")
    print(f"  Flagged for research: {s['needs_research']}")
    print(f"  Delta report     : {DELTA.name}")
    print(f"  Research targets : {TARGETS.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
