#!/usr/bin/env python3
"""
build_trism_v2_1.py – Build AI TRiSM Vendor 2-1 from 2-0 Researched data.

This script reads the v2.0 researched file and consolidates three separate
rationale sources into a single human-readable rationale string per sub-pillar:

  1. score_rationale        – Why this score was assigned (level, evidence basis)
  2. evidence_quality_rationale – Source diversity, volume, specificity, grade
  3. score_adjustment.reason – Why the score was adjusted from its original value

The consolidated text is written to a new field:
  sub_pillar_rationale_v2_consolidated  (dict[sub_pillar_id → str])

No external fetches are performed; this is a pure data-transform step.

Input : AI TRiSM Vendor 2-0 Researched.json
Output: AI TRiSM Vendor 2-1 Consolidated.json
"""

import json
import os
import sys
from datetime import datetime, timezone

INPUT_FILE  = "AI TRiSM Vendor 2-0 Researched.json"
OUTPUT_FILE = "AI TRiSM Vendor 2-1 Consolidated.json"

# ── Helpers ──────────────────────────────────────────────────────────────

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
        parts.append(f"{sid} – {sp_name}: Score {adjusted:.2f}/5.0 (Level {level}). Confidence: {confidence}.")

    # 1) Score Rationale
    sr = (entry.get("score_rationale") or "").strip()
    if sr:
        parts.append(f"\n[Score Rationale]\n{sr}")

    # 2) Evidence Quality Rationale
    eqr = (entry.get("evidence_quality_rationale") or "").strip()
    if eqr:
        parts.append(f"\n[Evidence Quality]\n{eqr}")

    # 3) Score Adjustment Reasoning
    adj = entry.get("score_adjustment") or {}
    reason = (adj.get("reason") or "").strip()
    if reason:
        orig_s = f"{adj.get('original', 0):.2f}" if adj.get("original") is not None else "?"
        adj_s  = f"{adj.get('adjusted', 0):.2f}" if adj.get("adjusted") is not None else "?"
        parts.append(f"\n[Score Adjustment]\n{orig_s} → {adj_s}: {reason}")

    # 4) Criteria assessment summary (compact)
    ca = entry.get("criteria_assessment", [])
    if ca:
        met = sum(1 for c in ca if c.get("status") == "met")
        partial = sum(1 for c in ca if c.get("status") == "partial")
        unmet = sum(1 for c in ca if c.get("status") == "unmet")
        lines = [f"\n[Criteria Assessment] ({met} met, {partial} partial, {unmet} unmet of {len(ca)})"]
        for c in ca:
            icon = {"met": "✅", "partial": "⚠️", "unmet": "❌"}.get(c.get("status", ""), "?")
            crit = c.get("criterion", "")
            lines.append(f"  {icon} {c.get('status','').upper()}: {crit}")
        parts.append("\n".join(lines))

    # 5) Key evidence snippets (brief)
    ke = entry.get("key_evidence", [])
    if ke:
        lines = ["\n[Key Evidence]"]
        for i, e in enumerate(ke[:3], 1):
            snippet = str(e).strip()[:150]
            lines.append(f"  {i}. {snippet}{'…' if len(str(e)) > 150 else ''}")
        parts.append("\n".join(lines))

    return "\n".join(parts).strip()


def build_v2_1():
    """Main transform: read v2.0, produce v2.1 with consolidated rationale."""
    src = os.path.join(os.path.dirname(__file__), INPUT_FILE)
    if not os.path.exists(src):
        print(f"ERROR: {INPUT_FILE} not found.")
        sys.exit(1)

    with open(src, "r", encoding="utf-8-sig") as f:
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
    }

    for vendor in vendors:
        v2_rat = vendor.get("sub_pillar_rationale_v2", {})
        if not v2_rat:
            stats["sub_pillars_missing_rationale"] += 1
            # Still create the consolidated field (empty)
            vendor["sub_pillar_rationale_v2_consolidated"] = {}
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

    # Update file metadata
    data["schema_version"] = "2.1"
    data["v2_1_metadata"] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script": "build_trism_v2_1.py",
        "description": "Consolidated rationale from score_rationale + evidence_quality_rationale + score_adjustment into single readable text per sub-pillar.",
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


if __name__ == "__main__":
    build_v2_1()
