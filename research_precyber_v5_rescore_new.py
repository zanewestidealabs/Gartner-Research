"""
research_precyber_v5_rescore_new.py — Re-score all new (v3-pipeline) vendors with the fixed scoring
=====================================================================================================

The original v3 pipeline had a bug: new vendors with no prior validated score
(original_score == 0) were capped at 1.5 for all sub-pillars by the ±MAX_ADJUSTMENT guard.
The fix has been applied to research_precyber_v2_rationale.py (skip cap when original_score == 0).

This script:
  1. Identifies the vendors in 3-0 that are NOT in 2-3 (v3-pipeline new vendors)
  2. Skips vendors currently graded F (--skip-f, default on) — blocked websites
  3. Resumes from existing checkpoints (avoids re-fetching already-completed vendors)
  4. Clears cache+checkpoint only for vendors that need a fresh run
  5. Runs them through S2→S3→S4 and writes 3-3 Rescored New.json

Merge afterwards:
  python merge_precyber_v3.py --source "Preemptive Cybersecurity Vendor 3-3 Rescored New.json"

Usage:
  python research_precyber_v5_rescore_new.py
  python research_precyber_v5_rescore_new.py --sleep 0.5 --batch-pause 5
  python research_precyber_v5_rescore_new.py --dry-run
  python research_precyber_v5_rescore_new.py --no-skip-f   # include F vendors too
"""

import argparse
import hashlib
import io
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List

if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT        = Path(__file__).resolve().parent
LIVE_FILE   = ROOT / "Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json"
V23_FILE    = ROOT / "Preemptive Cybersecurity Vendor 2-3 Holistic Validated.json"
OUTPUT_FILE = ROOT / "Preemptive Cybersecurity Vendor 3-3 Rescored New.json"
BATCH_DIR   = ROOT / "research" / "precyber_v3_batches"
CACHE_DIR   = ROOT / "research" / "cache" / "pages_precyber"

from research_precyber_v2_rationale import (
    load_schema as load_schema_v2,
    VENDOR_URLS,
)
from research_precyber_svc_pricing import (
    load_schema as load_schema_svc,
)
from research_precyber_v3_new_vendors import run_stage2, run_stage3, run_stage4


def _cache_path_for_url(url: str) -> Path:
    h = hashlib.sha1(url.encode("utf-8"), usedforsecurity=False).hexdigest()
    return CACHE_DIR / f"{h}.json"


def checkpoint_path(vendor_name: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in vendor_name)
    return BATCH_DIR / f"v3_{safe}.json"


def load_vendors(skip_f: bool) -> tuple[List[Dict], List[Dict], List[str]]:
    """Return (all_v30_vendors, vendors_to_run, skipped_names)."""
    v30 = json.loads(LIVE_FILE.read_text(encoding="utf-8"))
    if isinstance(v30, dict):
        v30 = v30.get("vendors", [])
    v23_names = {v["vendor"] for v in json.loads(V23_FILE.read_text(encoding="utf-8"))["vendors"]}
    new_vendors = [v for v in v30 if v.get("vendor") not in v23_names]
    skipped: List[str] = []
    to_run: List[Dict] = []
    for v in new_vendors:
        if skip_f and v.get("coverage_grade") == "F":
            skipped.append(v["vendor"])
        else:
            to_run.append(v)
    return v30, to_run, skipped


def clear_vendor_cache(vendor_name: str) -> int:
    urls = VENDOR_URLS.get(vendor_name, [])
    cleared = 0
    for url in urls:
        cp = _cache_path_for_url(url)
        if cp.exists():
            cp.unlink()
            cleared += 1
    return cleared


def clear_checkpoint(vendor_name: str) -> bool:
    cp = checkpoint_path(vendor_name)
    if cp.exists():
        cp.unlink()
        return True
    return False


def load_checkpoint(vendor_name: str) -> Dict | None:
    cp = checkpoint_path(vendor_name)
    if cp.exists():
        return json.loads(cp.read_text(encoding="utf-8"))
    return None


def run_vendor(vendor: dict, schema_v2: dict, schema_svc: dict,
               *, sleep_seconds: float, idx: int, total: int) -> dict:
    vendor_name = vendor.get("vendor", "?")
    cap = vendor.get("primary_capability", "?")
    url_count = len(VENDOR_URLS.get(vendor_name, []))
    prefix = f"[{idx:2d}/{total}] {vendor_name} [{cap}]"

    # Resume from checkpoint if available
    existing = load_checkpoint(vendor_name)
    if existing:
        grade = existing.get("coverage_grade", "?")
        avg = sum(existing.get("sub_pillar_scores_v2_researched", {}).values())
        cnt = max(len(existing.get("sub_pillar_scores_v2_researched", {})), 1)
        print(f"  {prefix} — RESUMED from checkpoint  grade={grade}  avg={avg/cnt:.2f}")
        return existing

    print(f"  {prefix} — {url_count} URL(s)  fetching...")

    v = run_stage2(vendor, schema_v2, sleep_seconds=sleep_seconds)
    pages = v.pop("_pages_fetched", 0)
    scores_v2 = v.get("sub_pillar_scores_v2_researched", {})
    avg_score = sum(scores_v2.values()) / max(len(scores_v2), 1)
    print(f"  {prefix} — S2 done  {pages} pages  avg={avg_score:.2f}")

    v = run_stage3(v)
    grade = v.get("coverage_grade", "?")

    v = run_stage4(v, schema_svc)
    svc_pages = v.pop("_svc_pages_fetched", 0)
    svc_total = v.pop("_svc_pages_total", 0)
    svc_maturity = v.get("services_maturity_level", "?")
    outcome = v.get("outcome_maturity_rating", 0)

    # Checkpoint
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    checkpoint_path(vendor_name).write_text(
        json.dumps(v, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  {prefix} — DONE  grade={grade}  svc={svc_pages}/{svc_total}  maturity={svc_maturity}  outcome={outcome}  ✓")
    return v


def main():
    parser = argparse.ArgumentParser(description="PreCyber v5 — Re-score new vendors with fixed scoring")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sleep", type=float, default=0.5)
    parser.add_argument("--batch-pause", type=int, default=5)
    parser.add_argument("--no-skip-f", action="store_true", help="Include F-grade vendors (default: skip them)")
    args = parser.parse_args()

    skip_f = not args.no_skip_f
    all_vendors, to_run, skipped = load_vendors(skip_f)

    print(f"\nPreCyber v5 — Re-score New Vendors (fixed scoring)")
    print(f"  Source : {LIVE_FILE.name}")
    print(f"  Output : {OUTPUT_FILE.name}")
    print(f"  To run : {len(to_run)} vendors")
    if skipped:
        print(f"  Skipped: {len(skipped)} F-grade vendors — {', '.join(skipped)}")
    print()

    # Categorise: checkpoint exists (resume) vs needs fresh run
    resumable = [v for v in to_run if checkpoint_path(v["vendor"]).exists()]
    fresh     = [v for v in to_run if not checkpoint_path(v["vendor"]).exists()]

    if resumable:
        print(f"Resuming {len(resumable)} already-checkpointed vendor(s):")
        for v in resumable:
            print(f"  ✓ {v['vendor']}")
    if fresh:
        print(f"\nClearing caches for {len(fresh)} vendor(s) that need a fresh run:")
        for v in fresh:
            name = v["vendor"]
            n = clear_vendor_cache(name)
            print(f"  {name}: cleared {n} cache file(s)")

    if args.dry_run:
        print("\n[dry-run] No fetching performed.")
        return

    schema_v2  = load_schema_v2()
    schema_svc = load_schema_svc()

    print(f"\n{'─'*70}")
    print(f"  Processing {len(to_run)} vendors")
    print(f"{'─'*70}")

    results: List[dict] = []
    for i, vendor in enumerate(to_run, 1):
        result = run_vendor(vendor, schema_v2, schema_svc,
                            sleep_seconds=args.sleep, idx=i, total=len(to_run))
        results.append(result)
        if i < len(to_run) and not load_checkpoint(vendor["vendor"]):
            # Only pause after a fresh fetch, not a resume
            time.sleep(args.batch_pause)

    print(f"\n{'─'*70}")
    OUTPUT_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(results)} vendor records → {OUTPUT_FILE.name}")

    grades: Dict[str, int] = {}
    for v in results:
        g = v.get("coverage_grade", "F")
        grades[g] = grades.get(g, 0) + 1
    print("\nGrade summary (rescored vendors only):")
    for g, n in sorted(grades.items()):
        bar = "█" * n
        print(f"  {g}: {n:2d}  {bar}")
    if skipped:
        print(f"  F: {len(skipped):2d}  (skipped — blocked sites: {', '.join(skipped)})")

    print(f"\nNext step: python merge_precyber_v3.py --source \"{OUTPUT_FILE.name}\"")


if __name__ == "__main__":
    main()
