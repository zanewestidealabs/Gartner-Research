#!/usr/bin/env python3
"""
build_precyber_v2_1.py – Build Preemptive Cybersecurity Vendor 2-1 from 2-0 Researched data.

This script reads the v2.0 researched file and consolidates three separate
rationale sources into a single human-readable rationale string per sub-pillar:

  1. score_rationale             – Why this score was assigned (level, evidence basis)
  2. evidence_quality_rationale  – Source diversity, volume, specificity, grade
  3. score_adjustment.reason     – Why the score was adjusted from its original value

The consolidated text is written to a new field:
  sub_pillar_rationale_v2_consolidated  (dict[sub_pillar_id → str])

Additionally computes per-vendor summary metrics:
  - coverage_grade   (A–F based on sub-pillars with score > 0)
  - quality_grade    (A–F based on average evidence_quality_factor)
  - pillar_averages  (mean score per pillar)

No external fetches are performed; this is a pure data-transform step.

Input : Preemptive Cybersecurity Vendor 2-0 Researched.json
Output: Preemptive Cybersecurity Vendor 2-1 Consolidated.json
"""

import json
import os
import sys
from datetime import datetime, timezone

INPUT_FILE  = "Preemptive Cybersecurity Vendor 2-0 Researched.json"
OUTPUT_FILE = "Preemptive Cybersecurity Vendor 2-1 Consolidated.json"

PILLARS = ["EXM", "AMT", "ADR", "PPM"]
SUBPILLAR_IDS = [
    "EXM-01", "EXM-02", "EXM-03", "EXM-04",
    "AMT-01", "AMT-02", "AMT-03", "AMT-04",
    "ADR-01", "ADR-02", "ADR-03", "ADR-04",
    "PPM-01", "PPM-02", "PPM-03", "PPM-04",
]

# Coverage grade thresholds (out of 16 sub-pillars)
COVERAGE_GRADES = [
    (13, "A"),  # 81-100%
    (10, "B"),  # 63-75%
    ( 7, "C"),  # 44-56%
    ( 4, "D"),  # 25-38%
    ( 1, "F"),  # 6-19%
]

# Quality grade thresholds (evidence_quality_factor average)
QUALITY_THRESHOLDS = [
    (0.80, "A"),
    (0.60, "B"),
    (0.40, "C"),
    (0.20, "D"),
    (0.00, "F"),
]


# ── Helpers ──────────────────────────────────────────────────────────────

def _coverage_grade(count: int) -> str:
    """Return A–F grade based on number of sub-pillars with score > 0."""
    for threshold, grade in COVERAGE_GRADES:
        if count >= threshold:
            return grade
    return "F"


def _quality_grade(avg_quality: float) -> str:
    """Return A–F grade based on average evidence quality factor."""
    for threshold, grade in QUALITY_THRESHOLDS:
        if avg_quality >= threshold:
            return grade
    return "F"


def consolidate_rationale(entry: dict) -> str:
    """Merge the three rationale sources into one readable paragraph."""
    parts = []

    sid = entry.get("sub_pillar_id", "")
    sp_name = entry.get("sub_pillar_name", "")
    adjusted = entry.get("adjusted_score")
    original = entry.get("original_score")
    level = entry.get("scoring_level")
    confidence = entry.get("confidence", "")

    # Header line
    if sid and sp_name and adjusted is not None:
        parts.append(
            f"{sid} – {sp_name}: Score {adjusted:.2f}/5.0 "
            f"(Level {level}). Confidence: {confidence}."
        )

    # 1) Score Rationale
    sr = (entry.get("score_rationale") or "").strip()
    if sr:
        parts.append(f"\n[Score Rationale]\n{sr}")

    # 2) Evidence Quality Rationale
    eq = (entry.get("evidence_quality_rationale") or "").strip()
    if eq:
        parts.append(f"\n[Evidence Quality]\n{eq}")

    # 3) Score Adjustment
    adj = entry.get("score_adjustment") or {}
    reason = ""
    if isinstance(adj, dict):
        reason = (adj.get("reason") or "").strip()
    elif isinstance(adj, str):
        reason = adj.strip()

    if reason and original is not None and adjusted is not None:
        parts.append(
            f"\n[Score Adjustment] {original:.2f} → {adjusted:.2f}: {reason}"
        )
    elif reason:
        parts.append(f"\n[Score Adjustment] {reason}")

    # 4) Criteria Assessment summary
    criteria = entry.get("criteria_assessment") or []
    if criteria and isinstance(criteria, list):
        met = sum(1 for c in criteria if c.get("met") is True)
        partial = sum(1 for c in criteria if c.get("partially_met") is True)
        unmet = len(criteria) - met - partial
        icons = f"✅ {met}  ⚠️ {partial}  ❌ {unmet}"
        parts.append(f"\n[Criteria Assessment] {icons}")

    # 5) Key Evidence snippets (top 3, 150 char limit)
    evidence = entry.get("key_evidence") or []
    if evidence and isinstance(evidence, list):
        top = evidence[:3]
        snippets = []
        for ev in top:
            if isinstance(ev, dict):
                txt = ev.get("snippet") or ev.get("text") or str(ev)
            else:
                txt = str(ev)
            txt = txt.strip()
            if len(txt) > 150:
                txt = txt[:147] + "..."
            snippets.append(f"  • {txt}")
        if snippets:
            parts.append("\n[Key Evidence]\n" + "\n".join(snippets))

    return "\n".join(parts).strip()


def compute_vendor_summary(vendor: dict, consolidated: dict) -> dict:
    """Compute coverage grade, quality grade, and pillar averages."""
    v2_rat = vendor.get("sub_pillar_rationale_v2", {})

    # Count sub-pillars with score > 0
    covered = 0
    quality_factors = []
    pillar_scores = {p: [] for p in PILLARS}

    for sid in SUBPILLAR_IDS:
        entry = v2_rat.get(sid, {})
        if not isinstance(entry, dict):
            continue
        score = entry.get("adjusted_score") or entry.get("original_score") or 0
        if score > 0:
            covered += 1

        # Collect quality factor
        qf = entry.get("evidence_quality_factor")
        if qf is not None and isinstance(qf, (int, float)):
            quality_factors.append(qf)

        # Collect pillar score
        pillar = sid.split("-")[0]
        if pillar in pillar_scores:
            pillar_scores[pillar].append(score)

    avg_quality = sum(quality_factors) / len(quality_factors) if quality_factors else 0.0

    pillar_avgs = {}
    for p, scores in pillar_scores.items():
        if scores:
            pillar_avgs[p] = round(sum(scores) / len(scores), 2)
        else:
            pillar_avgs[p] = 0.0

    return {
        "coverage_count": covered,
        "coverage_grade": _coverage_grade(covered),
        "quality_avg": round(avg_quality, 3),
        "quality_grade": _quality_grade(avg_quality),
        "pillar_averages": pillar_avgs,
    }


# ── Main ─────────────────────────────────────────────────────────────────

def build_v2_1():
    """Read v2.0, consolidate rationale, write v2.1."""
    src = os.path.join(os.path.dirname(__file__), INPUT_FILE)
    if not os.path.exists(src):
        print(f"ERROR: {INPUT_FILE} not found.")
        sys.exit(1)

    with open(src, "r", encoding="utf-8") as f:
        data = json.load(f)

    vendors = data.get("vendors", [])
    if not vendors:
        print("ERROR: No vendors found in input file.")
        sys.exit(1)

    stats = {
        "total_vendors": len(vendors),
        "vendors_with_v2_rationale": 0,
        "sub_pillars_consolidated": 0,
        "sub_pillars_missing_rationale": 0,
        "coverage_grade_distribution": {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0},
        "quality_grade_distribution": {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0},
    }

    for vendor in vendors:
        v2_rat = vendor.get("sub_pillar_rationale_v2", {})
        if not v2_rat:
            stats["sub_pillars_missing_rationale"] += 1
            vendor["sub_pillar_rationale_v2_consolidated"] = {}
            vendor["vendor_summary_v2_1"] = {
                "coverage_count": 0,
                "coverage_grade": "F",
                "quality_avg": 0.0,
                "quality_grade": "F",
                "pillar_averages": {p: 0.0 for p in PILLARS},
            }
            stats["coverage_grade_distribution"]["F"] += 1
            stats["quality_grade_distribution"]["F"] += 1
            continue

        stats["vendors_with_v2_rationale"] += 1
        consolidated = {}

        for sid, entry in v2_rat.items():
            if isinstance(entry, dict):
                consolidated[sid] = consolidate_rationale(entry)
                stats["sub_pillars_consolidated"] += 1
            elif isinstance(entry, str):
                consolidated[sid] = entry.strip()
                stats["sub_pillars_consolidated"] += 1
            else:
                consolidated[sid] = ""
                stats["sub_pillars_missing_rationale"] += 1

        vendor["sub_pillar_rationale_v2_consolidated"] = consolidated

        # Compute vendor summary metrics
        summary = compute_vendor_summary(vendor, consolidated)
        vendor["vendor_summary_v2_1"] = summary
        stats["coverage_grade_distribution"][summary["coverage_grade"]] += 1
        stats["quality_grade_distribution"][summary["quality_grade"]] += 1

    # Update file metadata
    data["schema_version"] = "2.1"
    data["v2_1_metadata"] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script": "build_precyber_v2_1.py",
        "description": (
            "Consolidated rationale from score_rationale + evidence_quality_rationale "
            "+ score_adjustment into single readable text per sub-pillar. "
            "Added vendor_summary_v2_1 with coverage/quality grades and pillar averages."
        ),
        "source_file": INPUT_FILE,
        "stats": stats,
    }

    # Write output
    dst = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Built {OUTPUT_FILE}")
    print(f"   Vendors: {stats['total_vendors']}")
    print(f"   With v2 rationale: {stats['vendors_with_v2_rationale']}")
    print(f"   Sub-pillars consolidated: {stats['sub_pillars_consolidated']}")
    print(f"   Missing rationale entries: {stats['sub_pillars_missing_rationale']}")
    print(f"   Coverage grades: {stats['coverage_grade_distribution']}")
    print(f"   Quality grades:  {stats['quality_grade_distribution']}")


if __name__ == "__main__":
    build_v2_1()
