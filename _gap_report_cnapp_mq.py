"""
_gap_report_cnapp_mq.py
─────────────────────────
Inventories the 1-3 file and produces a gap matrix:

  ● ledger-grounded   (sub_pillar has 1+ entry in evidence_ledger / sub_pillar_evidence excerpts)
  ○ heuristic-only    (mq_gap_rationale present but no source-grounded evidence)
  · missing           (neither rationale nor evidence)

Outputs:
  - Console: vendor × sub_pillar matrix + per-vendor / per-sub-pillar totals
  - JSON:    cnapp_mq_gap_report.json with structured cell-by-cell status
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC_PRIMARY = ROOT / "CNAPP MQ Vendor 1-4 Harvested.json"
SRC_FALLBACK = ROOT / "CNAPP MQ Vendor 1-3 Researched.json"
SRC = SRC_PRIMARY if SRC_PRIMARY.exists() else SRC_FALLBACK
OUT = ROOT / "cnapp_mq_gap_report.json"

PILLAR_MAP: dict[str, list[str]] = {
    "VIA": ["VIA-01", "VIA-02", "VIA-03", "VIA-04"],
    "SLE": ["SLE-01", "SLE-02", "SLE-03", "SLE-04"],
    "MKR": ["MKR-01", "MKR-02", "MKR-03", "MKR-04"],
    "MKE": ["MKE-01", "MKE-02", "MKE-03", "MKE-04"],
    "CXQ": ["CXQ-01", "CXQ-02", "CXQ-03", "CXQ-04"],
    "MKU": ["MKU-01", "MKU-02", "MKU-03"],
    "VIG": ["VIG-01", "VIG-02", "VIG-03", "VIG-04"],
}
ALL_SP = [sp for sps in PILLAR_MAP.values() for sp in sps]


def cell_status(vendor: dict, sid: str) -> str:
    # Ledger-grounded if sub_pillar_evidence has excerpts OR sources
    ev = (vendor.get("sub_pillar_evidence") or {}).get(sid) or {}
    has_evidence = (ev.get("excerpts") and len(ev["excerpts"]) > 0) or (
        ev.get("sources") and len(ev["sources"]) > 0
    )
    if has_evidence:
        # Distinguish harvested (auto) vs ledger (curated/v12) vs paywall-skipped
        st = (ev.get("enrichment_status") or "").lower()
        if st == "harvested":
            return "harvested"
        if st == "needs_targeted_research":
            return "needs_research"
        return "ledger"
    if (ev.get("enrichment_status") or "").lower() == "needs_targeted_research":
        return "needs_research"
    # Heuristic if mq_gap_rationale text exists for sid
    rats = vendor.get("mq_gap_rationales") or {}
    for sub_map in rats.values():
        if isinstance(sub_map, dict) and sid in sub_map:
            info = sub_map[sid]
            if isinstance(info, dict) and (info.get("rationale") or "").strip():
                return "heuristic"
    return "missing"


def main() -> int:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    vendors = data.get("vendors") or []

    matrix = {}            # vendor -> {sid -> status}
    statuses = ["ledger", "harvested", "heuristic", "needs_research", "missing"]
    totals = {s: 0 for s in statuses}
    by_vendor = defaultdict(lambda: {s: 0 for s in statuses})
    by_sp = defaultdict(lambda: {s: 0 for s in statuses})

    for v in vendors:
        name = v.get("vendor")
        matrix[name] = {}
        for sid in ALL_SP:
            st = cell_status(v, sid)
            matrix[name][sid] = st
            totals[st] += 1
            by_vendor[name][st] += 1
            by_sp[sid][st] += 1

    # ── Console matrix ──
    sym = {"ledger": "●", "harvested": "◐", "heuristic": "○", "needs_research": "?", "missing": "·"}
    print("CNAPP-MQ Gap Matrix  (●=ledger  ◐=harvested  ○=heuristic  ?=paywall/needs-research  ·=missing)\n")
    header = " " * 22 + " ".join(sid[-2:] for sid in ALL_SP) + "  led hrv het ?   mis"
    print(header)
    print("-" * len(header))
    for name in sorted(matrix.keys()):
        cells = "  ".join(sym[matrix[name][sid]] for sid in ALL_SP)
        bv = by_vendor[name]
        print(f"{name:22.22s}  {cells}    {bv['ledger']:>3d} {bv['harvested']:>3d} {bv['heuristic']:>3d} {bv['needs_research']:>3d} {bv['missing']:>3d}")

    print()
    print(f"TOTAL CELLS: {sum(totals.values())}")
    grounded = totals['ledger'] + totals['harvested']
    print(f"  ● ledger-grounded : {totals['ledger']:>4d}  ({100*totals['ledger']/648:.1f}%)")
    print(f"  ◐ harvested       : {totals['harvested']:>4d}  ({100*totals['harvested']/648:.1f}%)")
    print(f"  ★ total grounded  : {grounded:>4d}  ({100*grounded/648:.1f}%)")
    print(f"  ○ heuristic-only  : {totals['heuristic']:>4d}  ({100*totals['heuristic']/648:.1f}%)")
    print(f"  ? needs research  : {totals['needs_research']:>4d}  ({100*totals['needs_research']/648:.1f}%)")
    print(f"  · missing         : {totals['missing']:>4d}  ({100*totals['missing']/648:.1f}%)")

    print("\nBy sub-pillar (ledger-grounded count, sorted ascending — these are gap priorities):")
    for sid in sorted(ALL_SP, key=lambda s: by_sp[s]["ledger"]):
        b = by_sp[sid]
        print(f"  {sid}: ledger={b['ledger']:>2d}  heuristic={b['heuristic']:>2d}  missing={b['missing']:>2d}")

    OUT.write_text(json.dumps({
        "totals": totals,
        "by_vendor": dict(by_vendor),
        "by_sub_pillar": dict(by_sp),
        "matrix": matrix,
    }, indent=2), encoding="utf-8")
    print(f"\nDetailed JSON: {OUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
