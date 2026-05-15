"""
_reassess_precyber_scores.py
============================
Recomputes sub-pillar scores for all vendors in the v6 file using:
  - Stored criteria_assessment (status: met/partial/unmet per criterion)
  - Stored evidence signals (pillar_term_hits, schema_criteria_hits, excerpts)
  - The UPDATED determine_scoring_level (criteria-first scoring)

No web fetching required. Produces scores that directly align with
the criteria assessment data already in the file.

After running this script, rebuild v3 current scores and redeploy.
"""
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

VENDOR_FILE = Path("Preemptive Cybersecurity Vendor 6-0 v3.json")
SCHEMA_V2   = Path("Preemptive_Cybersecurity_Schema_v2.json")

# Sub-pillar IDs to reassess (capability pillars only — SVC handled separately)
PILLARS = ["EXM", "AMT", "ADR", "PPM"]
SUBPILLAR_IDS = [f"{p}-{i:02d}" for p in PILLARS for i in range(1, 5)]

SCORING_LEVELS = {
    0: "No Evidence — No publicly verifiable evidence of capability in this sub-pillar.",
    1: "Minimal — Basic or manual capability; no automation, analytics, or continuous operation.",
    2: "Generic Claims — Marketing mentions the capability but lacks named products, technical docs, or specifics.",
    3: "Demonstrated — Documented capability with named products or features, some technical detail, identifiable use cases.",
    4: "Advanced — Named products with measurable outcomes, integration points, customer validation, or analyst recognition.",
    5: "Market-Leading — Best-in-class with deep technical evidence, extensive customer base, analyst leadership recognition.",
}


@dataclass
class CriterionAssessment:
    criterion: str
    status: str   # "met", "partial", "unmet"
    evidence: str
    confidence: str


# Import the updated determine_scoring_level from the pipeline
from research_precyber_v2_rationale import determine_scoring_level, build_score_rationale


def _parse_rationale_signals(rationale_text: str) -> dict:
    """Extract stored numeric signals from the score_rationale text."""
    signals = {
        "v1_signal": 0.0,
        "specificity": 0.0,
        "schema_hits": 0,
        "pillar_hits": 0,
        "excerpt_count": 0,
    }
    if not rationale_text:
        return signals
    m = re.search(r"V1 signal[=:]?\s*(\d+\.\d+)", rationale_text, re.I)
    if m: signals["v1_signal"] = float(m.group(1))
    m = re.search(r"specificity[=:]?\s*(\d+\.\d+)", rationale_text, re.I)
    if m: signals["specificity"] = float(m.group(1))
    m = re.search(r"Schema hits[=:]?\s*(\d+)", rationale_text, re.I)
    if m: signals["schema_hits"] = int(m.group(1))
    m = re.search(r"pillar hits[=:]?\s*(\d+)", rationale_text, re.I)
    if m: signals["pillar_hits"] = int(m.group(1))
    m = re.search(r"(\d+) excerpts?\s+from", rationale_text, re.I)
    if m: signals["excerpt_count"] = int(m.group(1))
    return signals


def recompute_sub_pillar(vendor_name: str, sp_id: str, v2_entry: dict, ev_block: dict) -> dict:
    """Recompute score and rationale for one sub-pillar from stored data."""

    # Reconstruct CriterionAssessment objects from stored criteria_assessment
    ca_raw = v2_entry.get("criteria_assessment", [])
    criteria_results = [
        CriterionAssessment(
            criterion=c.get("criterion", ""),
            status=c.get("status", "unmet"),
            evidence=c.get("evidence", ""),
            confidence=c.get("confidence", "medium"),
        )
        for c in ca_raw
    ]

    if not criteria_results:
        return v2_entry  # Nothing to recompute

    # Pull evidence signals — prefer stored ev_block, fall back to parsing rationale text
    pillar_term_hits = int((ev_block or {}).get("pillar_term_hits", 0))
    schema_criteria_hits = int((ev_block or {}).get("schema_criteria_hits", 0))
    existing_specificity = float((ev_block or {}).get("sub_pillar_specificity", 0.0))
    excerpt_count = len((ev_block or {}).get("excerpts", []))

    # If ev_block missing signals, parse rationale text as fallback
    if pillar_term_hits == 0 and schema_criteria_hits == 0 and excerpt_count == 0:
        sig = _parse_rationale_signals(v2_entry.get("score_rationale", ""))
        pillar_term_hits = sig["pillar_hits"]
        schema_criteria_hits = sig["schema_hits"]
        existing_specificity = sig["specificity"]
        excerpt_count = sig["excerpt_count"]

    # Determine new scoring level using criteria-first logic
    level, level_justification = determine_scoring_level(
        criteria_results=criteria_results,
        pillar_term_hits=pillar_term_hits,
        schema_criteria_hits=schema_criteria_hits,
        specificity=existing_specificity,
        total_excerpts=excerpt_count,
        has_metrics=False,        # conservative — can't reconstruct without page text
        has_architecture_detail=False,
        exclusion_hits=0,
        existing_score=v2_entry.get("original_score", 0.0),
        existing_specificity=existing_specificity,
    )

    met_count = sum(1 for c in criteria_results if c.status == "met")
    partial_count = sum(1 for c in criteria_results if c.status == "partial")
    total_criteria = len(criteria_results)

    # Compute adjusted score: base from level + fractional criteria boost
    base = float(level)
    if total_criteria > 0:
        sub_boost = (met_count + partial_count * 0.3) / total_criteria
        adjusted = base + (sub_boost * 0.75)
    else:
        adjusted = base

    adjusted = min(5.0, max(0.0, adjusted))
    adjusted = round(adjusted * 4) / 4  # snap to 0.25 increments

    # Use stored original_score for adjustment narrative
    original_score = float(v2_entry.get("original_score", adjusted))
    score_diff = adjusted - original_score
    if original_score == 0.0:
        adj_reason = f"Fresh score {adjusted:.2f}: criteria-first assessment ({met_count}/{total_criteria} criteria met, level={level})."
    elif abs(score_diff) >= 0.25:
        direction = "increased" if score_diff > 0 else "decreased"
        adj_reason = (f"Score {direction} from {original_score:.2f} to {adjusted:.2f}: "
                     f"criteria-first reassessment ({met_count}/{total_criteria} criteria met, level={level}).")
    else:
        adjusted = original_score  # preserve if negligible change
        adj_reason = f"Score confirmed at {original_score:.2f} — criteria-first reassessment ({met_count}/{total_criteria} criteria met, level={level})."

    # Build score rationale text
    excerpts_list = (ev_block or {}).get("excerpts", [])
    score_rationale = build_score_rationale(
        vendor_name=vendor_name,
        text_lower="",
        all_excerpts=excerpts_list,
        score=adjusted,
        criteria_results=criteria_results,
        level=level,
        level_justification=level_justification,
        pillar_term_hits=pillar_term_hits,
        schema_criteria_hits=schema_criteria_hits,
        specificity=existing_specificity,
        source_count=len(set(u for u in (ev_block or {}).get("source_urls", []) if u)),
    )

    # Build updated entry preserving all existing fields
    updated = dict(v2_entry)
    updated["adjusted_score"] = adjusted
    updated["scoring_level"] = level
    updated["score_rationale"] = score_rationale
    updated["scoring_level_justification"] = level_justification
    updated["score_adjustment"] = {
        "original": original_score,
        "adjusted": adjusted,
        "reason": adj_reason,
    }
    # Keep existing evidence_quality_rationale, key_evidence, confidence, criteria_assessment
    return updated, adjusted


def rebuild_consolidated(vendor_name: str, sp_id: str, entry: dict) -> str:
    """Rebuild consolidated rationale string from updated entry."""
    parts = []
    sp_name = entry.get("sub_pillar_name", "")
    adjusted = entry.get("adjusted_score", 0.0)
    original = entry.get("original_score", adjusted)
    level = entry.get("scoring_level", 0)
    confidence = entry.get("confidence", "")

    if sp_id and sp_name and adjusted is not None:
        parts.append(f"{sp_id} – {sp_name}: Score {adjusted:.2f}/5.0 (Level {level}). Confidence: {confidence}.")

    sr = (entry.get("score_rationale") or "").strip()
    if sr:
        parts.append(f"\n[Score Rationale]\n{sr}")

    eq = (entry.get("evidence_quality_rationale") or "").strip()
    if eq:
        parts.append(f"\n[Evidence Quality]\n{eq}")

    adj = entry.get("score_adjustment") or {}
    reason = ""
    if isinstance(adj, dict):
        reason = (adj.get("reason") or "").strip()
        adj_orig = adj.get("original", original)
        adj_adj  = adj.get("adjusted", adjusted)
    else:
        reason = str(adj).strip()
        adj_orig, adj_adj = original, adjusted
    if reason:
        parts.append(f"\n[Score Adjustment] {adj_orig:.2f} → {adj_adj:.2f}: {reason}")

    criteria_list = entry.get("criteria_assessment") or []
    if criteria_list and isinstance(criteria_list, list):
        c_met     = sum(1 for c in criteria_list if c.get("status") == "met")
        c_partial = sum(1 for c in criteria_list if c.get("status") == "partial")
        c_unmet   = sum(1 for c in criteria_list if c.get("status") in ("unmet", "not_met"))
        icons = f"\u2705 {c_met}  \u26a0\ufe0f {c_partial}  \u274c {c_unmet}"
        parts.append(f"\n[Criteria Assessment] {icons}")

    key_evidence = entry.get("key_evidence") or []
    if key_evidence:
        ev_lines = "\n".join(f"  \u2022 {e[:140]}..." for e in key_evidence[:3])
        parts.append(f"\n[Key Evidence]\n{ev_lines}")

    return "\n".join(parts)


def main():
    print("Loading vendor file...")
    vendors = json.loads(VENDOR_FILE.read_text(encoding="utf-8"))
    print(f"  {len(vendors)} vendors loaded")

    total_updated = 0
    total_unchanged = 0
    score_changes: List[Tuple[str, str, float, float]] = []  # (vendor, sp_id, old, new)

    for vendor in vendors:
        vname = vendor.get("vendor", "?")
        v2 = vendor.get("sub_pillar_rationale_v2", {})
        ev_all = vendor.get("sub_pillar_evidence", {})

        if not v2:
            continue

        new_v2 = {}
        new_scores: Dict[str, float] = {}
        changed = False

        for sp_id in SUBPILLAR_IDS:
            entry = v2.get(sp_id)
            if not entry or not isinstance(entry, dict):
                continue

            ev_block = ev_all.get(sp_id) or {}
            result = recompute_sub_pillar(vname, sp_id, entry, ev_block)

            if isinstance(result, tuple):
                new_entry, new_score = result
            else:
                new_entry = result
                new_score = new_entry.get("adjusted_score", entry.get("adjusted_score", 0.0))

            new_v2[sp_id] = new_entry
            new_scores[sp_id] = new_score

            old_score = entry.get("adjusted_score", 0.0)
            if abs(new_score - old_score) >= 0.25:
                score_changes.append((vname, sp_id, old_score, new_score))
                changed = True
                total_updated += 1
            else:
                total_unchanged += 1

        if not new_v2:
            continue

        # Preserve any SVC/other sub-pillars not in our list
        for sp_id, entry in v2.items():
            if sp_id not in new_v2:
                new_v2[sp_id] = entry
                existing_score = entry.get("adjusted_score", 0.0)
                if existing_score:
                    new_scores[sp_id] = existing_score

        vendor["sub_pillar_rationale_v2"] = new_v2

        # Update researched scores
        vendor["sub_pillar_scores_v2_researched"] = new_scores

        # Recompute pillar averages
        new_pillar_scores = {}
        for pillar in PILLARS:
            sp_ids = [f"{pillar}-{i:02d}" for i in range(1, 5)]
            vals = [new_scores[s] for s in sp_ids if s in new_scores and new_scores[s] > 0]
            if vals:
                new_pillar_scores[pillar] = round(sum(vals) / len(vals), 2)
        vendor["pillar_scores_v2_researched"] = new_pillar_scores

        # Rebuild consolidated rationale
        new_consolidated = {}
        for sp_id, entry in new_v2.items():
            if isinstance(entry, dict):
                new_consolidated[sp_id] = rebuild_consolidated(vname, sp_id, entry)
        vendor["sub_pillar_rationale_v2_consolidated"] = new_consolidated

        # Update sub_pillar_scores_current (v3) to use new scores for the 16 capability SPs
        current = vendor.get("sub_pillar_scores_current", {})
        for sp_id, score in new_scores.items():
            if sp_id in SUBPILLAR_IDS:
                current[sp_id] = score
        vendor["sub_pillar_scores_current"] = current

        # Update pillar_scores_current
        pc = vendor.get("pillar_scores_current", {})
        for pillar, score in new_pillar_scores.items():
            pc[pillar] = score
        vendor["pillar_scores_current"] = pc

    print(f"\nReassessment complete:")
    print(f"  Sub-pillars updated (score changed ≥0.25): {total_updated}")
    print(f"  Sub-pillars unchanged: {total_unchanged}")

    if score_changes:
        print(f"\nTop score changes (largest absolute change):")
        score_changes.sort(key=lambda x: abs(x[3] - x[2]), reverse=True)
        for vname, sp_id, old, new in score_changes[:20]:
            direction = "↑" if new > old else "↓"
            print(f"  {direction}  {vname:40s} {sp_id}  {old:.2f} → {new:.2f}  (Δ{new-old:+.2f})")

    # Backup and write
    backup = VENDOR_FILE.with_name(VENDOR_FILE.stem + " BACKUP_pre_reassess.json")
    shutil.copy(VENDOR_FILE, backup)
    VENDOR_FILE.write_text(json.dumps(vendors, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten: {VENDOR_FILE.name}")
    print(f"Backup : {backup.name}")


if __name__ == "__main__":
    main()
