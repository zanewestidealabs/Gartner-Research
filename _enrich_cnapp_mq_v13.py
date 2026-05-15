"""
_enrich_cnapp_mq_v13.py
─────────────────────────
CNAPP MQ Vendor enrichment — v1.3 → v1.4 Consolidated.

Mirrors the established `_enrich_offsec_v21.py` pattern:
  - Per-vendor ENRICHMENTS dict keyed by sub_pillar
  - Each sub_pillar entry: {rationale (2-4 sentences), sources[]}
  - Each source: {type, tier (A/B/C), url, title}
  - Optional new_scores: {sub_pillar: int}  for previously-zero cells
  - apply_enrichments() recalculates pillar averages and stamps metadata

Pipeline:
  Input  : CNAPP MQ Vendor 1-3 Researched.json   (adapter output)
  Output : CNAPP MQ Vendor 1-4 Consolidated.json

Two-phase strategy to guarantee 100% sub-pillar coverage:

  PHASE A (seeded automatically by this script):
    - Walks every (vendor × sub_pillar) cell.
    - If the cell has at least one evidence_ledger entry, builds a
      {rationale, sources[]} entry from the existing fact + URL.
    - Otherwise, builds a "needs_research" placeholder using the
      heuristic mq_gap_rationale text + the vendor website as a
      single Tier-C source. Flagged so a later batch can replace it.

  PHASE B (manual curation, optional, batch-by-batch):
    - Add full {rationale + 4 sources A/B/C} entries to ENRICHMENTS
      below for each vendor batch you want to deepen.
    - Re-run the script; phase B overrides phase A per cell.

Run: python _enrich_cnapp_mq_v13.py
"""
from __future__ import annotations

import copy
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "CNAPP MQ Vendor 1-3 Researched.json"
OUTPUT = ROOT / "CNAPP MQ Vendor 1-4 Consolidated.json"

# Pillar → list of sub_pillar codes (used for pillar score recompute)
PILLAR_MAP: dict[str, list[str]] = {
    "VIA": ["VIA-01", "VIA-02", "VIA-03", "VIA-04"],
    "SLE": ["SLE-01", "SLE-02", "SLE-03", "SLE-04"],
    "MKR": ["MKR-01", "MKR-02", "MKR-03", "MKR-04"],
    "MKE": ["MKE-01", "MKE-02", "MKE-03", "MKE-04"],
    "CXQ": ["CXQ-01", "CXQ-02", "CXQ-03", "CXQ-04"],
    "MKU": ["MKU-01", "MKU-02", "MKU-03"],
    "VIG": ["VIG-01", "VIG-02", "VIG-03", "VIG-04"],
}
ALL_SUB_PILLARS: list[str] = [sp for sps in PILLAR_MAP.values() for sp in sps]

SOURCE_TYPE_TIER: dict[str, str] = {
    # Tier A — primary, authoritative
    "vendor_about": "A", "vendor_company": "A", "vendor_product": "A",
    "vendor_docs": "A", "vendor_customers": "A", "vendor_partners": "A",
    "vendor_compliance": "A", "press_release": "A", "investor_relations": "A",
    "analyst_recognition": "A", "analyst_quote": "A",
    "gartner_peer_insights": "A", "case_study": "A", "case_studies": "A",
    "press_release_index": "A", "vendor_blog": "A",
    # Tier B — secondary technical/news
    "tier1_press": "B", "tier2_press": "B", "industry_award": "B",
    "industry_blog": "B", "technical_media": "B",
    # Tier C — community / professional
    "github": "C", "professional_networks": "C", "community": "C",
}


def _tier_for(src_type: str | None) -> str:
    return SOURCE_TYPE_TIER.get((src_type or "").lower(), "C")


def _title_for(src_type: str | None, vendor: str) -> str:
    label = (src_type or "source").replace("_", " ").title()
    return f"{vendor} — {label}"


# ═══════════════════════════════════════════════════════════════════════
# ENRICHMENTS  —  Phase B manual curation lives here.
# Schema mirrors _enrich_offsec_v21.py exactly:
#
#   "VendorName": {
#       "new_scores": {"VIA-01": 3, ...},   # optional, for zero cells
#       "evidence": {
#           "VIA-01": {
#               "rationale": "2-4 sentence narrative with product names, "
#                            "metrics, analyst recognition...",
#               "sources": [
#                   {"type": "Vendor documentation", "tier": "A",
#                    "url": "https://...", "title": "..."},
#                   {"type": "Analyst reports", "tier": "A",
#                    "url": "https://...", "title": "..."},
#                   {"type": "Technical media", "tier": "B",
#                    "url": "https://...", "title": "..."},
#                   {"type": "Benchmarks/Case studies", "tier": "B",
#                    "url": "https://...", "title": "..."}
#               ]
#           },
#           ...
#       }
#   }
#
# Add vendors batch-by-batch. Anything missing here falls back to the
# Phase A auto-seed (existing ledger evidence or needs_research placeholder).
# ═══════════════════════════════════════════════════════════════════════
ENRICHMENTS: dict[str, dict[str, Any]] = {
    # Populate batches here following the offsec v2.1 pattern.
    # Suggested first batch (high-stakes leaders):
    #   "Wiz": {...}, "CrowdStrike": {...}, "Palo Alto Networks": {...},
    #   "Microsoft": {...}, "Aqua Security": {...}
}


# ── Phase A auto-seed ─────────────────────────────────────────────────


def _seed_from_ledger(vendor: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Walk every sub_pillar; build {rationale, sources[]} from existing
    evidence_ledger or fall back to the heuristic mq_gap rationale."""
    name = vendor.get("vendor", "Unknown")
    website = (vendor.get("website") or "").strip()
    ledger = vendor.get("evidence_ledger") or []
    rationales = vendor.get("mq_gap_rationales") or {}

    # group ledger by sub_pillar
    led_by_sid: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for e in ledger:
        sid = e.get("sub_pillar")
        if sid:
            led_by_sid[sid].append(e)

    # flatten heuristic rationales (pillar → sub → info) → sid → info
    heur: dict[str, dict[str, Any]] = {}
    for pillar, sub_map in rationales.items():
        if isinstance(sub_map, dict):
            for sid, info in sub_map.items():
                if isinstance(info, dict):
                    heur[sid] = info

    out: dict[str, dict[str, Any]] = {}
    for sid in ALL_SUB_PILLARS:
        led = led_by_sid.get(sid, [])
        h = heur.get(sid, {})
        heur_text = (h.get("rationale") or "").strip()
        conf = (h.get("confidence") or "").lower()

        if led:
            facts = [str(e.get("fact") or "").strip() for e in led if e.get("fact")]
            narrative = " ".join(facts) if facts else heur_text
            sources = []
            seen_urls = set()
            for e in led:
                url = (e.get("source_url") or "").strip()
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                src_type = e.get("source_type") or "vendor_about"
                sources.append({
                    "type": src_type,
                    "tier": _tier_for(src_type),
                    "url": url,
                    "title": _title_for(src_type, name),
                })
            out[sid] = {
                "rationale": narrative or heur_text or "No researched rationale.",
                "sources": sources,
                "enrichment_status": "ledger_seeded" if sources else "needs_research",
                "evidence_count": len(sources),
                "confidence": conf or "medium",
            }
        else:
            # No ledger evidence → placeholder using heuristic rationale + website
            placeholder_sources: list[dict[str, Any]] = []
            if website:
                placeholder_sources.append({
                    "type": "vendor_about",
                    "tier": "C",
                    "url": website,
                    "title": f"{name} — Vendor Website (placeholder)",
                })
            out[sid] = {
                "rationale": heur_text or f"No public evidence captured for {sid}; score derived from vendor metadata only.",
                "sources": placeholder_sources,
                "enrichment_status": "needs_research",
                "evidence_count": len(placeholder_sources),
                "confidence": "low",
            }
    return out


# ── Pipeline ──────────────────────────────────────────────────────────


def apply_enrichments() -> int:
    if not INPUT.exists():
        print(f"[error] input not found: {INPUT}")
        return 2
    with INPUT.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    vendors = data.get("vendors") or []
    seeded_cells = 0
    overridden_cells = 0
    placeholder_cells = 0
    total_sources = 0

    for v in vendors:
        name = v.get("vendor", "Unknown")
        # Phase A: seed every sub-pillar from ledger / heuristic
        seeded = _seed_from_ledger(v)

        # Phase B: override per ENRICHMENTS
        manual = ENRICHMENTS.get(name) or {}
        ev_overrides = manual.get("evidence") or {}
        new_scores = manual.get("new_scores") or {}

        for sid, override in ev_overrides.items():
            srcs = override.get("sources") or []
            seeded[sid] = {
                "rationale": override.get("rationale") or "",
                "sources": srcs,
                "enrichment_status": "curated",
                "evidence_count": len(srcs),
                "confidence": override.get("confidence") or "high",
            }
            overridden_cells += 1

        # Apply new_scores into the score dict
        sub_scores = v.setdefault("mq_gap_sub_pillar_scores", {})
        for sid, sc in new_scores.items():
            sub_scores[sid] = float(sc)

        # Tally
        for sid, entry in seeded.items():
            seeded_cells += 1
            total_sources += len(entry.get("sources") or [])
            if entry.get("enrichment_status") == "needs_research":
                placeholder_cells += 1

        # Stamp onto vendor
        v["sub_pillar_evidence"] = seeded
        # Mirror to standard renderer keys (already done by adapter, refresh)
        v["sub_pillar_scores_v2_researched"] = {sid: float(s) for sid, s in sub_scores.items()}

        # Recalculate pillar averages from sub_pillar scores
        pillar_scores = {}
        for pillar, sps in PILLAR_MAP.items():
            vals = [float(sub_scores[sp]) for sp in sps if sub_scores.get(sp) not in (None, "", 0)]
            pillar_scores[pillar] = round(sum(vals) / len(vals), 2) if vals else 0.0
        v["mq_gap_pillar_scores"] = pillar_scores
        v["pillar_scores_v2_researched"] = pillar_scores

        # Refresh sub_pillar_rationale_v2 so the existing renderer still
        # displays narrative + score_rationale (in addition to the new
        # offsec-style sources[] block).
        rat_v2: dict[str, dict[str, Any]] = {}
        for sid, entry in seeded.items():
            rat_v2[sid] = {
                "score_rationale": entry["rationale"],
                "confidence": entry["confidence"],
                "evidence_quality_grade": (
                    "A" if entry["evidence_count"] >= 4 else
                    "B" if entry["evidence_count"] >= 2 else
                    "C" if entry["evidence_count"] >= 1 else "D"
                ),
                "evidence_quality_factor": min(0.95, 0.4 + 0.15 * entry["evidence_count"]),
                "excerpt_count": entry["evidence_count"],
                "key_evidence": [s["url"] for s in entry["sources"][:4]],
                "evidence_sources": [s["type"] for s in entry["sources"]],
            }
        v["sub_pillar_rationale_v2"] = rat_v2

        # research_flag for the UI guardrail message
        good = sum(1 for e in seeded.values() if e["evidence_count"] >= 3)
        v["research_flag"] = "good_evidence" if good >= 14 else "thin_evidence"

    # Top-level metadata
    out = dict(data)
    out["vendors"] = vendors
    out["enrichment_pass"] = "1.4-consolidated"
    out["enrichment_pattern"] = "offsec_v21_style"
    out["enrichment_generated_at"] = datetime.now(timezone.utc).isoformat()
    out["enrichment_script"] = os.path.basename(__file__)
    out["enrichment_notes"] = (
        "Sub-pillar evidence in offsec v2.1 schema (rationale + sources[]). "
        "Phase A auto-seeds from existing ledger; Phase B overrides via "
        "ENRICHMENTS dict. Cells with enrichment_status='needs_research' "
        "require manual deepening to reach 4-source citation standard."
    )

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print("CNAPP MQ ENRICHMENT v1.3 → v1.4")
    print(f"{'=' * 60}")
    print(f"Vendors processed:        {len(vendors)}")
    print(f"Total sub-pillar cells:   {seeded_cells}")
    print(f"  - manually curated:     {overridden_cells}")
    print(f"  - ledger-seeded:        {seeded_cells - overridden_cells - placeholder_cells}")
    print(f"  - needs_research:       {placeholder_cells}")
    print(f"Source citations total:   {total_sources}")
    avg_per_cell = total_sources / seeded_cells if seeded_cells else 0
    print(f"Avg sources / sub-pillar: {avg_per_cell:.2f}  (target: >= 4)")
    print(f"\nOutput: {OUTPUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(apply_enrichments())
