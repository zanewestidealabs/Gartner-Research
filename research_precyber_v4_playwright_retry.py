"""
research_precyber_v4_playwright_retry.py — Re-run F-grade vendors with Playwright fallback
============================================================================================

Reads the 3-0 master file, identifies all vendors with coverage_grade == 'F',
clears their URL caches and checkpoints, then re-runs them through the full
Stages 2→3→4 pipeline (which now uses Playwright as a fallback for failed/empty fetches).

Outputs:
  - Per-vendor checkpoints overwritten in research/precyber_v3_batches/
  - Final file: Preemptive Cybersecurity Vendor 3-2 Playwright Retry.json
  - Run: python merge_precyber_v3.py --source "3-2" afterwards to integrate

Usage:
  python research_precyber_v4_playwright_retry.py           # all F-grade vendors
  python research_precyber_v4_playwright_retry.py --dry-run # show plan
  python research_precyber_v4_playwright_retry.py --sleep 1  # seconds between fetches
"""

import argparse
import hashlib
import io
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT       = Path(__file__).resolve().parent
LIVE_FILE  = ROOT / "Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json"
OUTPUT_FILE = ROOT / "Preemptive Cybersecurity Vendor 3-2 Playwright Retry.json"
BATCH_DIR  = ROOT / "research" / "precyber_v3_batches"
CACHE_DIR  = ROOT / "research" / "cache" / "pages_precyber"

PILLARS = ["EXM", "AMT", "ADR", "PPM"]
SUBPILLAR_IDS = [f"{p}-{i:02d}" for p in PILLARS for i in range(1, 5)]
COVERAGE_GRADES_V2 = [(21, "A"), (16, "B"), (10, "C"), (5, "D"), (1, "F")]


def coverage_grade(count: int) -> str:
    for threshold, grade in COVERAGE_GRADES_V2:
        if count >= threshold:
            return grade
    return "F"


# ─────────────────────────────────────────────────────────────────────
# Stage imports
# ─────────────────────────────────────────────────────────────────────
from research_precyber_v2_rationale import (
    analyse_vendor,
    rationale_to_dict,
    load_schema as load_schema_v2,
    compute_evidence_quality,
    VENDOR_URLS,
    PILLARS as V2_PILLARS,
)
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

# Borrow consolidation logic from v3
from research_precyber_v3_new_vendors import run_stage2, run_stage3, run_stage4


def _cache_path_for_url(url: str) -> Path:
    h = hashlib.sha1(url.encode("utf-8"), usedforsecurity=False).hexdigest()
    return CACHE_DIR / f"{h}.json"


def checkpoint_path(vendor_name: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in vendor_name)
    return BATCH_DIR / f"v3_{safe}.json"


def load_f_grade_vendors() -> List[Dict]:
    """Return vendors from 3-0 with coverage_grade == 'F'."""
    raw = json.loads(LIVE_FILE.read_text(encoding="utf-8"))
    vendors = raw if isinstance(raw, list) else raw.get("vendors", [])
    return [v for v in vendors if v.get("coverage_grade") == "F"]


def clear_vendor_cache(vendor_name: str):
    """Delete cached URL fetches for a vendor so Playwright gets a fresh try."""
    urls = VENDOR_URLS.get(vendor_name, [])
    cleared = 0
    for url in urls:
        cp = _cache_path_for_url(url)
        if cp.exists():
            cp.unlink()
            cleared += 1
    return cleared


def clear_checkpoint(vendor_name: str):
    cp = checkpoint_path(vendor_name)
    if cp.exists():
        cp.unlink()
        return True
    return False


def run_vendor(vendor: dict, schema_v2: dict, schema_svc: dict,
               *, sleep_seconds: float) -> dict:
    vendor_name = vendor.get("vendor", "?")
    print(f"\n  ► {vendor_name} [{vendor.get('primary_capability', '?')}]")

    print(f"    [S2] Fetching evidence + scoring 16 capability sub-pillars...")
    v = run_stage2(vendor, schema_v2, sleep_seconds=sleep_seconds)
    pages = v.pop("_pages_fetched", 0)
    scores_v2 = v.get("sub_pillar_scores_v2_researched", {})
    avg_score = sum(scores_v2.values()) / max(len(scores_v2), 1)
    print(f"    [S2] Done — {pages} pages, avg capability score {avg_score:.2f}")

    print(f"    [S3] Consolidating rationale + computing grades...")
    v = run_stage3(v)
    print(f"    [S3] Coverage grade: {v.get('coverage_grade', '?')}")

    print(f"    [S4] Scoring SVC sub-pillars + pricing dimensions...")
    v = run_stage4(v, schema_svc)
    svc_pages = v.pop("_svc_pages_fetched", 0)
    svc_total = v.pop("_svc_pages_total", 0)
    svc_maturity = v.get("services_maturity_level", "?")
    outcome_rating = v.get("outcome_maturity_rating", 0)
    print(f"    [S4] {svc_pages}/{svc_total} pages for SVC/pricing scoring")
    print(f"    [S4] Services maturity: {svc_maturity}, outcome rating: {outcome_rating}")

    return v


def main():
    parser = argparse.ArgumentParser(description="PreCyber v4 — Playwright retry for F-grade vendors")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without fetching")
    parser.add_argument("--sleep", type=float, default=0.5,
                        help="Seconds between page fetches within a vendor")
    parser.add_argument("--batch-pause", type=int, default=10,
                        help="Seconds to pause between batches")
    args = parser.parse_args()

    vendors = load_f_grade_vendors()
    print(f"\nPreCyber v4 Playwright Retry — F-grade Vendors")
    print(f"  Source file : {LIVE_FILE.name}")
    print(f"  Output file : {OUTPUT_FILE.name}")
    print(f"  Vendors     : {len(vendors)} F-grade to retry")
    print()
    for v in vendors:
        urls = VENDOR_URLS.get(v.get("vendor", ""), [])
        print(f"  {v.get('vendor', '?')} [{v.get('primary_capability', '?')}]"
              f" — {len(urls)} URL(s)")
    print()

    if args.dry_run:
        print("DRY-RUN: no fetches performed.")
        return

    # Clear caches and checkpoints for all F vendors
    print("── Clearing caches + checkpoints ──")
    for vendor in vendors:
        vname = vendor.get("vendor", "?")
        n_cache = clear_vendor_cache(vname)
        n_ckpt = 1 if clear_checkpoint(vname) else 0
        print(f"  {vname}: cleared {n_cache} cache file(s), {n_ckpt} checkpoint(s)")

    schema_v2 = load_schema_v2()
    schema_svc = load_schema_svc()
    BATCH_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    print(f"\n── Processing {len(vendors)} vendors ──")
    for i, vendor in enumerate(vendors):
        vname = vendor.get("vendor", "?")
        try:
            result = run_vendor(vendor, schema_v2, schema_svc, sleep_seconds=args.sleep)
            BATCH_DIR.mkdir(parents=True, exist_ok=True)
            safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in vname)
            ckpt = BATCH_DIR / f"v3_{safe}.json"
            ckpt.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"    ✓ Checkpointed: {vname}")
            results.append(result)
        except KeyboardInterrupt:
            print("\nInterrupted.")
            break
        except Exception as exc:
            print(f"    ERROR {vname}: {exc}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            results.append(vendor)  # keep original on error

        if i < len(vendors) - 1 and args.batch_pause > 0:
            time.sleep(args.batch_pause)

    OUTPUT_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(results)} vendor records → {OUTPUT_FILE.name}")

    # Summary
    grades = Counter(r.get("coverage_grade", "?") for r in results)
    print("\nGrade summary:")
    for g in ["A", "B", "C", "D", "F", "?"]:
        if grades[g]:
            print(f"  {g}: {grades[g]}")

    print(f"\nNext step: python merge_precyber_v3.py --source \"{OUTPUT_FILE.name}\"")


if __name__ == "__main__":
    main()
