"""
research_v4_evidence_scoring.py — Evidence-Quality Refined Scoring Pipeline (v4)

Reads existing vendor data (with sub_pillar_evidence) and produces
evidence-quality-refined scores that factor in the strength of the
underlying evidence for each sub-pillar score.

Scoring approach:
  - Base scores come from sub_pillar_scores_researched (or validated fallback)
  - Each base score (integer 0-5) is refined into 0.2-increment bands
    (e.g. a base of 4 → 4.0, 4.2, 4.4, 4.6, or 4.8) based on evidence quality
  - Evidence quality is computed from:
      • Source diversity (number of unique URLs)
      • Evidence volume (number of excerpts)
      • Specificity ratio (specific vs generic term matches)
      • Term density (specific terms per excerpt)
      • AI signal score alignment
      • Evidence consistency (do multiple sources agree?)
  - Output keys:
      sub_pillar_scores_evidence_refined   (flat dict: "PLA-01" → 4.6)
      pillar_scores_evidence_refined       (pillar averages)
      evidence_quality_analysis            (detailed per-sub-pillar breakdown)

Usage:
  python research_v4_evidence_scoring.py                         # process default file
  python research_v4_evidence_scoring.py --input "Vendor 5-2 Researched.json"
  python research_v4_evidence_scoring.py --input "Vendor 6-0 AI Researched.json"
  python research_v4_evidence_scoring.py --dry-run               # show scores without writing
"""

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent

PILLARS = ["PLA", "INV", "REM", "PMG", "LAW"]
SUBPILLAR_IDS = [f"{p}-{i:02d}" for p in PILLARS for i in range(1, 5)]

# Evidence quality weights (must sum to 1.0)
WEIGHTS = {
    "source_diversity": 0.15,
    "evidence_volume": 0.20,
    "specificity_ratio": 0.20,
    "term_density": 0.25,
    "ai_signal": 0.10,
    "consistency": 0.10,
}

# Thresholds for source diversity scoring
SOURCE_THRESHOLDS = {1: 0.2, 2: 0.5, 3: 0.7, 4: 0.85}  # n_sources → factor

# ─────────────────────────────────────────────────────────────────────
# Evidence Quality Computation
# ─────────────────────────────────────────────────────────────────────


def compute_evidence_quality(evidence_block: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyse a single sub-pillar's evidence block and return a quality
    assessment with component scores and an overall quality factor (0-1).
    """
    if not evidence_block or not isinstance(evidence_block, dict):
        return {
            "quality_factor": 0.5,  # neutral when no evidence
            "components": {},
            "notes": "No evidence data available — neutral quality assumed.",
        }

    source_urls = evidence_block.get("source_urls", [])
    if not isinstance(source_urls, list):
        source_urls = []
    excerpts = evidence_block.get("excerpts", [])
    if not isinstance(excerpts, list):
        excerpts = []

    # ── Normalise field names (DFIR vs TRiSM evidence formats) ──
    # DFIR uses: hit_count, specific_hit_count, ai_signal_score
    # TRiSM uses: criteria_hit_count, pillar_term_hits, sub_pillar_specificity
    hit_count = evidence_block.get("hit_count")
    if hit_count is None:
        hit_count = evidence_block.get("criteria_hit_count", 0)
    if hit_count is None:
        hit_count = 0

    specific_hit_count = evidence_block.get("specific_hit_count")
    if specific_hit_count is None:
        specific_hit_count = evidence_block.get("pillar_term_hits", 0)
        # Also consider schema_criteria_hits as additional specificity signal
        schema_hits = evidence_block.get("schema_criteria_hits", 0)
        if schema_hits and isinstance(schema_hits, (int, float)):
            specific_hit_count = (specific_hit_count or 0) + schema_hits
    if specific_hit_count is None:
        specific_hit_count = 0

    ai_signal = evidence_block.get("ai_signal_score")
    if ai_signal is None:
        # Use sub_pillar_specificity as proxy for AI signal (TRiSM)
        ai_signal = evidence_block.get("sub_pillar_specificity", 0)
    if ai_signal is None:
        ai_signal = 0

    # ── 1. Source diversity (0-1) ──
    n_sources = len(set(source_urls))  # deduplicate
    source_factor = 0.0
    for threshold, factor in sorted(SOURCE_THRESHOLDS.items()):
        if n_sources >= threshold:
            source_factor = factor
    if n_sources >= 5:
        source_factor = 1.0

    # ── 2. Evidence volume (0-1): excerpt count, capped at 8 ──
    volume_factor = min(len(excerpts) / 8.0, 1.0)

    # ── 3. Specificity ratio (0-1) ──
    # What fraction of hits are "specific" (domain-relevant terms)?
    if hit_count > 0 and specific_hit_count > 0:
        specificity_factor = min(specific_hit_count / max(hit_count * 2, 1), 1.0)
    elif len(excerpts) > 0:
        # Fallback: use per-excerpt specific_term_count or matched_terms + relevance_score
        total_specific = sum(
            ex.get("specific_term_count", 0) or ex.get("relevance_score", 0)
            for ex in excerpts if isinstance(ex, dict)
        )
        total_matched = sum(
            len(ex.get("matched_terms", [])) for ex in excerpts if isinstance(ex, dict)
        )
        specificity_factor = min(total_specific / max(total_matched * 2, 1), 1.0) if total_matched else 0.3
    else:
        specificity_factor = 0.0

    # ── 4. Term density (0-1) ──
    # Average specific terms per excerpt (cap at 5 per excerpt = perfect)
    if excerpts:
        total_specific_terms = sum(
            ex.get("specific_term_count", 0) or len(ex.get("matched_terms", []))
            for ex in excerpts if isinstance(ex, dict)
        )
        avg_terms_per_excerpt = total_specific_terms / len(excerpts)
        term_density = min(avg_terms_per_excerpt / 5.0, 1.0)
    else:
        term_density = 0.0

    # ── 5. AI signal alignment (0-1) ──
    if isinstance(ai_signal, (int, float)) and ai_signal > 0:
        ai_signal_factor = min(ai_signal / 5.0, 1.0)
    else:
        ai_signal_factor = 0.5  # neutral

    # ── 6. Consistency (0-1) ──
    # Do multiple excerpts from different URLs confirm the capability?
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

    # ── Weighted combination ──
    quality_factor = (
        source_factor * WEIGHTS["source_diversity"]
        + volume_factor * WEIGHTS["evidence_volume"]
        + specificity_factor * WEIGHTS["specificity_ratio"]
        + term_density * WEIGHTS["term_density"]
        + ai_signal_factor * WEIGHTS["ai_signal"]
        + consistency * WEIGHTS["consistency"]
    )
    quality_factor = max(0.0, min(1.0, quality_factor))

    # Build notes
    notes_parts = []
    if n_sources == 0:
        notes_parts.append("No source URLs")
    elif n_sources == 1:
        notes_parts.append("Single source only")
    if len(excerpts) == 0:
        notes_parts.append("No excerpts found")
    if specificity_factor < 0.3:
        notes_parts.append("Low term specificity")
    if term_density < 0.2:
        notes_parts.append("Low term density")
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
            "ai_signal": round(ai_signal_factor, 3),
            "consistency": round(consistency, 3),
        },
        "raw_counts": {
            "source_count": n_sources,
            "excerpt_count": len(excerpts),
            "hit_count": hit_count,
            "specific_hit_count": specific_hit_count,
            "ai_signal_score": ai_signal,
        },
        "notes": "; ".join(notes_parts) if notes_parts else "OK",
    }


def refine_score(base_score: float, quality_factor: float) -> float:
    """
    Refine a base score (0-5, typically integer) into a 0.2-increment
    score based on the evidence quality factor (0-1).

    Maps quality 0..1 → one of 5 sub-score buckets → offset 0.0, 0.2, 0.4, 0.6, 0.8
    E.g. base=4, quality=0.85 → bucket 4 → offset 0.8 → refined = 4.8
    """
    if base_score is None or (isinstance(base_score, float) and math.isnan(base_score)):
        return 0.0
    base = int(max(0, min(5, base_score)))
    # Map quality (0-1) to bucket 0-4
    bucket = min(4, int(quality_factor * 5))
    refined = base + bucket * 0.2
    return min(5.0, round(refined, 1))


# ─────────────────────────────────────────────────────────────────────
# Vendor Processing
# ─────────────────────────────────────────────────────────────────────


def get_best_sub_pillar_scores(vendor: Dict[str, Any]) -> Dict[str, float]:
    """
    Get the best available sub-pillar scores for a vendor.
    Priority: researched → validated → current → granular_mapping fallback
    """
    # Try researched first
    for key in [
        "sub_pillar_scores_researched",
        "sub_pillar_scores_validated",
        "sub_pillar_scores_current",
    ]:
        scores = vendor.get(key)
        if scores and isinstance(scores, dict) and len(scores) > 0:
            return {k: float(v) for k, v in scores.items() if v is not None}

    # Fallback: extract from granular_mapping
    for key in ["granular_mapping_validated", "granular_mapping"]:
        gm = vendor.get(key)
        if gm and isinstance(gm, dict):
            flat = {}
            for pillar_code, subs in gm.items():
                if isinstance(subs, dict):
                    for sid, val in subs.items():
                        if val is not None:
                            flat[sid] = float(val)
            if flat:
                return flat

    return {}


def get_evidence_data(vendor: Dict[str, Any]) -> Dict[str, Dict]:
    """
    Get the best available evidence data for a vendor.
    Priority: sub_pillar_evidence (v2 researched) → sub_pillar_evidence_ai (v3)
    """
    for key in ["sub_pillar_evidence", "sub_pillar_evidence_ai"]:
        ev = vendor.get(key)
        if ev and isinstance(ev, dict) and len(ev) > 0:
            return ev
    return {}


def process_vendor(vendor: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single vendor: compute evidence-refined scores for all sub-pillars.
    Returns a dict with all the new keys to add to the vendor record.
    """
    vendor_name = vendor.get("vendor", "Unknown")
    base_scores = get_best_sub_pillar_scores(vendor)
    evidence_data = get_evidence_data(vendor)

    sub_pillar_refined = {}
    evidence_analysis = {}
    quality_factors = []

    # Determine which sub-pillar IDs to process
    # Use all IDs found in base scores OR evidence data
    all_sids = sorted(set(list(base_scores.keys()) + list(evidence_data.keys())))
    if not all_sids:
        # Fallback to standard DFIR sub-pillars
        all_sids = SUBPILLAR_IDS

    for sid in all_sids:
        base = base_scores.get(sid)
        ev_block = evidence_data.get(sid)

        # Compute evidence quality
        eq = compute_evidence_quality(ev_block)
        quality_factor = eq["quality_factor"]
        quality_factors.append(quality_factor)

        # Compute refined score
        if base is not None:
            refined = refine_score(base, quality_factor)
        else:
            refined = None

        if refined is not None:
            sub_pillar_refined[sid] = refined

        evidence_analysis[sid] = {
            "base_score": base,
            "refined_score": refined,
            "quality_factor": eq["quality_factor"],
            "components": eq["components"],
            "notes": eq["notes"],
        }

    # Compute pillar-level averages from refined sub-pillar scores
    pillar_refined = {}
    # Detect pillar codes dynamically from the sub-pillar IDs
    detected_pillars = sorted(set(sid.split("-")[0] for sid in sub_pillar_refined.keys()))
    for pillar in detected_pillars:
        pillar_subs = [v for k, v in sub_pillar_refined.items() if k.startswith(pillar + "-")]
        if pillar_subs:
            pillar_refined[pillar] = round(sum(pillar_subs) / len(pillar_subs), 2)

    # Overall metrics
    avg_quality = round(sum(quality_factors) / len(quality_factors), 4) if quality_factors else 0.0
    overall_refined = (
        round(sum(pillar_refined.values()) / len(pillar_refined), 2)
        if pillar_refined
        else 0.0
    )

    return {
        "sub_pillar_scores_evidence_refined": sub_pillar_refined,
        "pillar_scores_evidence_refined": pillar_refined,
        "evidence_quality_analysis": evidence_analysis,
        "evidence_quality_summary": {
            "avg_quality_factor": avg_quality,
            "overall_refined_score": overall_refined,
            "sub_pillars_scored": len(sub_pillar_refined),
            "sub_pillars_with_evidence": sum(
                1 for sid in all_sids if evidence_data.get(sid)
            ),
            "quality_grade": (
                "A" if avg_quality >= 0.7
                else "B" if avg_quality >= 0.5
                else "C" if avg_quality >= 0.3
                else "D"
            ),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        },
    }


# ─────────────────────────────────────────────────────────────────────
# Main pipeline
# ─────────────────────────────────────────────────────────────────────


def load_vendor_file(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_vendor_file(path: Path, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✅ Saved to {path}")


def run_pipeline(
    input_path: Path,
    output_path: Optional[Path],
    dry_run: bool = False,
    max_vendors: int = 0,
) -> None:
    print(f"\n{'='*70}")
    print(f"  Evidence-Quality Refined Scoring Pipeline v4")
    print(f"  Input:  {input_path.name}")
    print(f"  Output: {output_path.name if output_path else 'in-place'}")
    print(f"  Mode:   {'DRY RUN' if dry_run else 'WRITE'}")
    print(f"{'='*70}\n")

    data = load_vendor_file(input_path)
    vendors = data.get("vendors", [])
    if not vendors:
        print("  ❌ No vendors found in input file.")
        return

    if max_vendors > 0:
        vendors = vendors[:max_vendors]

    total = len(vendors)
    print(f"  Processing {total} vendors...\n")

    # Stats tracking
    stats = {
        "total": total,
        "scored": 0,
        "no_evidence": 0,
        "quality_grades": {"A": 0, "B": 0, "C": 0, "D": 0},
    }

    results = []
    for i, vendor in enumerate(vendors):
        name = vendor.get("vendor", f"Vendor #{i}")
        result = process_vendor(vendor)

        summary = result["evidence_quality_summary"]
        grade = summary["quality_grade"]
        avg_q = summary["avg_quality_factor"]
        n_scored = summary["sub_pillars_scored"]
        n_evidence = summary["sub_pillars_with_evidence"]
        overall = summary["overall_refined_score"]

        stats["scored"] += 1
        stats["quality_grades"][grade] += 1
        if n_evidence == 0:
            stats["no_evidence"] += 1

        # Print progress
        if (i + 1) % 10 == 0 or i == 0 or i == total - 1:
            print(
                f"  [{i+1:3d}/{total}] {name:<35s} "
                f"Grade={grade} Quality={avg_q:.3f} "
                f"Refined={overall:.2f} "
                f"({n_scored} scored, {n_evidence} w/evidence)"
            )

        # Merge result into vendor
        updated = dict(vendor)
        updated.update(result)
        results.append(updated)

    # Replace vendor list
    data["vendors"] = results
    data["vendor_count"] = len(results)

    # Print summary
    print(f"\n{'─'*70}")
    print(f"  SCORING SUMMARY")
    print(f"{'─'*70}")
    print(f"  Total vendors processed:  {stats['scored']}")
    print(f"  Without evidence data:    {stats['no_evidence']}")
    print(f"  Quality grade distribution:")
    for grade in ["A", "B", "C", "D"]:
        count = stats["quality_grades"][grade]
        bar = "█" * count
        print(f"    Grade {grade}: {count:3d} {bar}")

    # Top 10 by refined score
    ranked = sorted(results, key=lambda v: v.get("evidence_quality_summary", {}).get("overall_refined_score", 0), reverse=True)
    print(f"\n  TOP 10 by Evidence-Refined Overall Score:")
    print(f"  {'Rank':>4s}  {'Vendor':<35s}  {'Refined':>8s}  {'Quality':>8s}  {'Grade':>5s}")
    for rank, v in enumerate(ranked[:10], 1):
        s = v.get("evidence_quality_summary", {})
        print(
            f"  {rank:4d}  {v.get('vendor', '?'):<35s}  "
            f"{s.get('overall_refined_score', 0):8.2f}  "
            f"{s.get('avg_quality_factor', 0):8.3f}  "
            f"{s.get('quality_grade', '?'):>5s}"
        )

    if dry_run:
        print(f"\n  🔍 DRY RUN — no files written.")
    else:
        out = output_path or input_path
        save_vendor_file(out, data)

    print()


# ─────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Evidence-Quality Refined Scoring Pipeline v4"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="Vendor 5-2 Researched.json",
        help="Input vendor JSON file (default: Vendor 5-2 Researched.json)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file (default: overwrite input)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show scores without writing to file",
    )
    parser.add_argument(
        "--max-vendors",
        type=int,
        default=0,
        help="Limit to N vendors (0 = all)",
    )
    args = parser.parse_args()

    input_path = ROOT / args.input
    if not input_path.exists():
        print(f"  ❌ Input file not found: {input_path}")
        sys.exit(1)

    output_path = ROOT / args.output if args.output else None

    run_pipeline(
        input_path=input_path,
        output_path=output_path,
        dry_run=args.dry_run,
        max_vendors=args.max_vendors,
    )


if __name__ == "__main__":
    main()
