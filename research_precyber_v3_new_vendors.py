"""
research_precyber_v3_new_vendors.py — Full research pipeline for new vendors (v3 batch)
========================================================================================

Runs the complete research pipeline on vendors that exist in the 3-0 SVC Pricing file
but have NOT yet been scored (no sub_pillar_rationale_v2_consolidated).

Pipeline stages (per vendor):
  Stage 2 — Evidence fetch + rationale + scoring   (research_precyber_v2_rationale.analyse_vendor)
  Stage 3 — Consolidation, grading, pillar averages (build_precyber_v2_1 logic)
  Stage 4 — SVC sub-pillar + pricing dimension scoring (research_precyber_svc_pricing)

Note: Stage 1 (v1 evidence pre-pass) is skipped for new vendors because
      Stage 2 fetches pages directly from VENDOR_URLS and scores all sub-pillars.

Outputs:
  - Per-vendor JSON checkpoints in  research/precyber_v3_batches/
  - Final file: Preemptive Cybersecurity Vendor 3-1 New Vendors.json
  - Run merge_precyber_v3.py afterwards to integrate into 3-0

Usage:
  python research_precyber_v3_new_vendors.py                    # all unscored vendors
  python research_precyber_v3_new_vendors.py --max-vendors 3    # test with 3
  python research_precyber_v3_new_vendors.py --batch-size 5     # vendors per batch
  python research_precyber_v3_new_vendors.py --batch-pause 20   # seconds between batches
  python research_precyber_v3_new_vendors.py --pillar SVC       # only SVC vendors
  python research_precyber_v3_new_vendors.py --pillar EXM ADR   # multiple pillars
  python research_precyber_v3_new_vendors.py --resume           # skip already checkpointed
  python research_precyber_v3_new_vendors.py --merge-only       # merge existing checkpoints
  python research_precyber_v3_new_vendors.py --dry-run          # show plan without fetching
"""

import argparse
import io
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent

LIVE_FILE   = ROOT / "Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json"
SCHEMA_FILE = ROOT / "Preemptive_Cybersecurity_Schema_v2.json"
OUTPUT_FILE = ROOT / "Preemptive Cybersecurity Vendor 3-1 New Vendors.json"
BATCH_DIR   = ROOT / "research" / "precyber_v3_batches"

PILLARS = ["EXM", "AMT", "ADR", "PPM"]
SUBPILLAR_IDS = [f"{p}-{i:02d}" for p in PILLARS for i in range(1, 5)]
SVC_SUBPILLARS_LOCAL = ["EXM-05", "AMT-05", "ADR-05", "PPM-05", "SVC-01", "SVC-02", "SVC-03", "SVC-04"]
PRICING_DIMS_LOCAL   = ["PRC-SUB", "PRC-USG", "PRC-FIX", "PRC-SUC", "PRC-COM", "PRC-OUT"]

COVERAGE_GRADES_V2 = [(21, "A"), (16, "B"), (10, "C"), (5, "D"), (1, "F")]


def coverage_grade(count: int) -> str:
    for threshold, grade in COVERAGE_GRADES_V2:
        if count >= threshold:
            return grade
    return "F"


# ─────────────────────────────────────────────────────────────────────
# Stage imports — pull machinery from existing pipeline scripts
# ─────────────────────────────────────────────────────────────────────

# Stage 2: rationale analysis
from research_precyber_v2_rationale import (
    analyse_vendor,
    rationale_to_dict,
    load_schema as load_schema_v2,
    compute_evidence_quality,
    VENDOR_URLS,
    PILLARS as V2_PILLARS,
)

# Stage 4: SVC + pricing scoring
from research_precyber_svc_pricing import (
    score_svc_subpillar,
    score_pricing_dimension,
    build_svc_rationale,
    build_pricing_rationale,
    fetch_page as svc_fetch_page,
    SVC_SUBPILLARS as SVC_SUBPILLAR_LIST,
    PRICING_DIMS as PRICING_DIM_LIST,
    load_schema as load_schema_svc,
)


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────

def load_unscored_vendors(pillar_filter=None) -> List[Dict]:
    """Return vendors from 3-0 that lack sub_pillar_rationale_v2_consolidated."""
    raw = json.loads(LIVE_FILE.read_text(encoding="utf-8"))
    # File may be a list or a dict with a "vendors" key
    vendors = raw if isinstance(raw, list) else raw.get("vendors", [])
    unscored = [v for v in vendors if "sub_pillar_rationale_v2_consolidated" not in v]
    if pillar_filter:
        unscored = [v for v in unscored if v.get("primary_capability") in pillar_filter]
    return unscored


def checkpoint_path(vendor_name: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in vendor_name)
    return BATCH_DIR / f"v3_{safe}.json"


def is_checkpointed(vendor_name: str) -> bool:
    return checkpoint_path(vendor_name).exists()


def save_checkpoint(vendor_name: str, result: dict):
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    path = checkpoint_path(vendor_name)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


def load_checkpoint(vendor_name: str) -> dict:
    return json.loads(checkpoint_path(vendor_name).read_text(encoding="utf-8"))


# ─────────────────────────────────────────────────────────────────────
# Stage 2: Evidence + rationale scoring
# ─────────────────────────────────────────────────────────────────────

def run_stage2(vendor: dict, schema_body: dict, *, sleep_seconds: float = 1.0) -> dict:
    """Fetch evidence pages and score all 16 capability sub-pillars with rationale."""
    import copy
    v = copy.deepcopy(vendor)

    result = analyse_vendor(v, schema_body, fetch_additional=True, sleep_seconds=sleep_seconds)

    new_rationale: Dict[str, Any] = {}
    new_scores: Dict[str, float] = {}
    new_pillar_scores: Dict[str, float] = {}
    new_eq_analysis: Dict[str, Any] = {}

    for sid, rat in result["rationale_results"].items():
        new_rationale[sid] = rationale_to_dict(rat)
        new_scores[sid] = rat.adjusted_score
        ev_block = v.get("sub_pillar_evidence", {}).get(sid, {})
        new_eq_analysis[sid] = compute_evidence_quality(ev_block)

    for pillar in V2_PILLARS:
        sp_ids = [f"{pillar}-{i:02d}" for i in range(1, 5)]
        sp_scores = [new_scores[s] for s in sp_ids if s in new_scores]
        if sp_scores:
            new_pillar_scores[pillar] = round(sum(sp_scores) / len(sp_scores), 2)

    v["sub_pillar_rationale_v2"] = new_rationale
    v["sub_pillar_scores_v2_researched"] = new_scores
    v["pillar_scores_v2_researched"] = new_pillar_scores
    v["evidence_quality_analysis"] = new_eq_analysis
    v["_pages_fetched"] = result["pages_fetched"]

    return v


# ─────────────────────────────────────────────────────────────────────
# Stage 3: Consolidation (replicate build_precyber_v2_1 logic)
# ─────────────────────────────────────────────────────────────────────

def run_stage3(vendor: dict) -> dict:
    """Merge rationale sources, compute coverage grade and pillar averages."""
    import copy
    v = copy.deepcopy(vendor)

    rationale_map: Dict[str, Any] = v.get("sub_pillar_rationale_v2", {})
    scores: Dict[str, float] = v.get("sub_pillar_scores_v2_researched", {})

    consolidated: Dict[str, str] = {}
    for sid, entry in rationale_map.items():
        parts = []
        sp_name = entry.get("sub_pillar_name", "")
        adjusted = entry.get("adjusted_score")
        original = entry.get("original_score")
        level = entry.get("scoring_level")
        confidence = entry.get("confidence", "")

        if sid and sp_name and adjusted is not None:
            parts.append(
                f"{sid} – {sp_name}: Score {adjusted:.2f}/5.0 (Level {level}). Confidence: {confidence}."
            )

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
        elif isinstance(adj, str):
            reason = adj.strip()
        if reason and original is not None and adjusted is not None:
            parts.append(f"\n[Score Adjustment] {original:.2f} → {adjusted:.2f}: {reason}")
        elif reason:
            parts.append(f"\n[Score Adjustment] {reason}")

        criteria = entry.get("criteria_assessment", "")
        if criteria:
            parts.append(f"\n[Criteria Assessment] {criteria}")

        key_evidence = entry.get("key_evidence") or []
        if key_evidence:
            ev_lines = "\n".join(f"  • {e[:140]}..." for e in key_evidence[:3])
            parts.append(f"\n[Key Evidence]\n{ev_lines}")

        consolidated[sid] = "\n".join(parts)

    v["sub_pillar_rationale_v2_consolidated"] = consolidated

    scored_count = sum(1 for s in scores.values() if s and s > 0)
    v["coverage_grade"] = coverage_grade(scored_count)
    v["capability_coverage"] = [sp for sp, s in scores.items() if s and s > 0]

    v["vendor_summary_v2_1"] = {
        "coverage_count": scored_count,
        "coverage_grade": v["coverage_grade"],
        "pillar_averages": v.get("pillar_scores_v2_researched", {}),
    }

    return v


# ─────────────────────────────────────────────────────────────────────
# Stage 4: SVC sub-pillars + pricing dimensions
# ─────────────────────────────────────────────────────────────────────

def run_stage4(vendor: dict, schema_svc: dict) -> dict:
    """Score SVC sub-pillars and pricing dimensions, merge into vendor record."""
    import copy
    v = copy.deepcopy(vendor)
    vendor_name = v.get("vendor", "?")

    # Gather URLs for this vendor
    urls = list(VENDOR_URLS.get(vendor_name, []))
    if not urls:
        print(f"    [S4] WARNING: no VENDOR_URLS for {vendor_name}, SVC/pricing scores will be minimal")

    # Fetch pages (reuses cache via svc_fetch_page)
    pages_text: List[Tuple[str, str]] = []
    for url in urls:
        try:
            rec = svc_fetch_page(url, force=False)
            if rec.get("ok") and isinstance(rec.get("text"), str):
                pages_text.append((rec["url"], rec["text"]))
        except Exception as e:
            print(f"    [S4] fetch failed {url}: {e}")

    print(f"    [S4] {len(pages_text)}/{len(urls)} pages for SVC/pricing scoring")

    # Score SVC sub-pillars
    svc_evidence: Dict[str, Any] = {}
    svc_scores: Dict[str, float] = {}
    svc_rationales: Dict[str, str] = {}

    for sp_id in SVC_SUBPILLAR_LIST:
        score, ev = score_svc_subpillar(sp_id, schema_svc, pages_text)
        svc_evidence[sp_id] = ev
        svc_scores[sp_id] = score
        svc_rationales[sp_id] = build_svc_rationale(sp_id, schema_svc, score, ev)

    # Score pricing dimensions
    pricing_evidence: Dict[str, Any] = {}
    pricing_scores: Dict[str, float] = {}
    pricing_rationales: Dict[str, str] = {}

    for dim_id in PRICING_DIM_LIST:
        score, ev = score_pricing_dimension(dim_id, schema_svc, pages_text)
        pricing_evidence[dim_id] = ev
        pricing_scores[dim_id] = score
        pricing_rationales[dim_id] = build_pricing_rationale(dim_id, schema_svc, score, ev)

    # Merge SVC rationales into consolidated block
    consolidated = v.get("sub_pillar_rationale_v2_consolidated", {})
    consolidated.update(svc_rationales)
    v["sub_pillar_rationale_v2_consolidated"] = consolidated

    # Update coverage stats to include SVC sub-pillars
    all_scores = {**v.get("sub_pillar_scores_v2_researched", {}), **svc_scores}
    scored_count = sum(1 for s in all_scores.values() if s and s > 0)
    v["capability_coverage"] = [sp for sp, s in all_scores.items() if s and s > 0]
    v["coverage_grade"] = coverage_grade(scored_count)

    v["svc_evidence"] = svc_evidence
    v["pricing_evidence"] = pricing_evidence
    v["pricing_rationales"] = pricing_rationales

    # Services maturity level (SVC-01..04 average)
    svc_standalone = {sp: svc_scores[sp] for sp in ["SVC-01", "SVC-02", "SVC-03", "SVC-04"]}
    avg_svc = sum(svc_standalone.values()) / max(len(svc_standalone), 1)
    if avg_svc >= 4.5:
        v["services_maturity_level"] = "autonomous"
    elif avg_svc >= 3.5:
        v["services_maturity_level"] = "ai_augmented"
    elif avg_svc >= 2.5:
        v["services_maturity_level"] = "managed"
    elif avg_svc >= 1.5:
        v["services_maturity_level"] = "consultative"
    else:
        v["services_maturity_level"] = "implementation_only"

    # Outcome maturity rating from pricing scores
    p_scores = list(pricing_scores.values())
    if p_scores:
        v["outcome_maturity_rating"] = round(sum(p_scores) / len(p_scores), 2)

    v["svc_pricing_research"] = {
        "researched_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_version": "v3_new_vendors",
        "pages_fetched": len(pages_text),
        "svc_subpillars_scored": len(SVC_SUBPILLAR_LIST),
        "pricing_dimensions_scored": len(PRICING_DIM_LIST),
    }

    # Cleanup temp key
    v.pop("_pages_fetched", None)

    return v


# ─────────────────────────────────────────────────────────────────────
# Per-vendor pipeline runner
# ─────────────────────────────────────────────────────────────────────

def run_vendor(vendor: dict, schema_v2: dict, schema_svc: dict,
               *, sleep_seconds: float, dry_run: bool) -> dict:
    vendor_name = vendor.get("vendor", "?")
    urls = VENDOR_URLS.get(vendor_name, [])

    if dry_run:
        print(f"  [DRY-RUN] {vendor_name} [{vendor.get('primary_capability','?')}] — {len(urls)} URLs")
        for u in urls:
            print(f"    {u}")
        return vendor

    print(f"\n  ► {vendor_name} [{vendor.get('primary_capability','?')}]")

    print(f"    [S2] Fetching evidence + scoring 16 capability sub-pillars...")
    v = run_stage2(vendor, schema_v2, sleep_seconds=sleep_seconds)
    pages = v.pop("_pages_fetched", 0)
    scores_v2 = v.get("sub_pillar_scores_v2_researched", {})
    avg_score = sum(scores_v2.values()) / max(len(scores_v2), 1)
    print(f"    [S2] Done — {pages} pages, avg capability score {avg_score:.2f}")

    print(f"    [S3] Consolidating rationale + computing grades...")
    v = run_stage3(v)
    print(f"    [S3] Coverage grade: {v.get('coverage_grade','?')}")

    print(f"    [S4] Scoring SVC sub-pillars + pricing dimensions...")
    v = run_stage4(v, schema_svc)
    print(f"    [S4] Services maturity: {v.get('services_maturity_level','?')}, "
          f"outcome rating: {v.get('outcome_maturity_rating','?')}")

    return v


# ─────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PreCyber v3 full research pipeline for new vendors")
    parser.add_argument("--max-vendors", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--batch-pause", type=int, default=20,
                        help="Seconds to pause between batches (avoids rate-limiting)")
    parser.add_argument("--pillar", nargs="+", default=[],
                        help="Only process vendors with these primary_capability values")
    parser.add_argument("--resume", action="store_true",
                        help="Skip vendors already checkpointed")
    parser.add_argument("--merge-only", action="store_true",
                        help="Skip research; just merge existing checkpoints")
    parser.add_argument("--force-fetch", action="store_true",
                        help="Re-fetch cached pages")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show plan (URLs) without fetching")
    parser.add_argument("--sleep", type=float, default=1.0,
                        help="Seconds between page fetches within a vendor")
    args = parser.parse_args()

    pillar_filter = [p.upper() for p in args.pillar] if args.pillar else None
    vendors = load_unscored_vendors(pillar_filter)

    if args.max_vendors > 0:
        vendors = vendors[:args.max_vendors]

    print(f"\nPreCyber v3 Research Pipeline — New Vendor Scoring")
    print(f"  Input file : {LIVE_FILE.name}")
    print(f"  Output file: {OUTPUT_FILE.name}")
    print(f"  Vendors    : {len(vendors)} to process")
    if pillar_filter:
        print(f"  Pillar filter: {pillar_filter}")
    print(f"  Batch size : {args.batch_size}  |  Pause: {args.batch_pause}s  |  Fetch sleep: {args.sleep}s")
    print()

    breakdown = Counter(v.get("primary_capability", "?") for v in vendors)
    for p, c in sorted(breakdown.items()):
        print(f"  {p}: {c} vendor{'s' if c != 1 else ''}")
    print()

    if args.dry_run:
        print("── DRY-RUN MODE: showing URLs only, no fetches ──\n")
        schema_v2 = load_schema_v2()
        schema_svc = load_schema_svc()
        for v in vendors:
            run_vendor(v, schema_v2, schema_svc, sleep_seconds=0, dry_run=True)
        return

    # Load schemas
    schema_v2 = load_schema_v2()
    schema_svc = load_schema_svc()

    if not args.merge_only:
        batch_num = 0
        interrupted = False
        for batch_start in range(0, len(vendors), args.batch_size):
            batch = vendors[batch_start: batch_start + args.batch_size]
            batch_num += 1
            print(f"\n── Batch {batch_num} ──────────────────────────────────────────")

            for vendor in batch:
                vname = vendor.get("vendor", "?")
                if args.resume and is_checkpointed(vname):
                    print(f"  SKIP (already checkpointed): {vname}")
                    continue
                try:
                    result = run_vendor(
                        vendor, schema_v2, schema_svc,
                        sleep_seconds=args.sleep, dry_run=False
                    )
                    save_checkpoint(vname, result)
                    print(f"    ✓ Checkpointed: {vname}")
                except KeyboardInterrupt:
                    print("\nInterrupted. Progress saved to checkpoints.")
                    interrupted = True
                    break
                except Exception as exc:
                    print(f"    ERROR {vname}: {exc}", file=sys.stderr)
                    import traceback
                    traceback.print_exc(file=sys.stderr)

            if interrupted:
                break
            if batch_start + args.batch_size < len(vendors):
                print(f"\n  Pausing {args.batch_pause}s before next batch...")
                time.sleep(args.batch_pause)

    # Merge checkpoints → output file
    print(f"\n── Merging checkpoints → {OUTPUT_FILE.name} ──")
    results = []
    missing = []
    for vendor in vendors:
        vname = vendor.get("vendor", "?")
        if is_checkpointed(vname):
            results.append(load_checkpoint(vname))
            print(f"  + {vname}")
        else:
            missing.append(vname)
            results.append(vendor)  # keep seed record

    OUTPUT_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(results)} vendor records → {OUTPUT_FILE.name}")
    if missing:
        print(f"  Missing checkpoints ({len(missing)} kept as seed records):")
        for n in missing:
            print(f"    - {n}")
    print(f"\nNext step: python merge_precyber_v3.py")


if __name__ == "__main__":
    main()
