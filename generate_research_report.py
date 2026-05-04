import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent

SUBPILLARS = [
    "PLA-01",
    "PLA-02",
    "PLA-03",
    "PLA-04",
    "INV-01",
    "INV-02",
    "INV-03",
    "INV-04",
    "REM-01",
    "REM-02",
    "REM-03",
    "REM-04",
    "PMG-01",
    "PMG-02",
    "PMG-03",
    "PMG-04",
    "LAW-01",
    "LAW-02",
    "LAW-03",
    "LAW-04",
]


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _avg(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _safe_float(v: Any) -> float:
    try:
        return float(v)
    except Exception:
        return 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validated", type=Path, default=ROOT / "Vendor 4-0 Validated.json")
    ap.add_argument("--researched", type=Path, default=ROOT / "Vendor 4-1 Researched.json")
    ap.add_argument("--out", type=Path, default=ROOT / "RESEARCH_VALIDATION_REPORT.md")
    args = ap.parse_args()

    validated = _load(args.validated)
    researched = _load(args.researched)

    v_by_name = {v.get("vendor"): v for v in validated}

    flag_counts = Counter()
    conf_values: List[float] = []

    capped_vendors = 0
    capped_subpillars = 0

    deltas: List[Tuple[float, str, str]] = []  # abs_delta, vendor, sid

    score_dist = Counter()
    excerpt_vendor_count = 0

    for v in researched:
        name = v.get("vendor")
        flag = v.get("research_flag", "unknown")
        flag_counts[str(flag)] += 1

        conf = _safe_float(v.get("research_confidence"))
        conf_values.append(conf)

        ev = v.get("sub_pillar_evidence") or {}
        any_ex = False
        for sid in SUBPILLARS:
            info = ev.get(sid) or {}
            if (info.get("excerpts") or []):
                any_ex = True
                break
        if any_ex:
            excerpt_vendor_count += 1

        cur = v_by_name.get(name) or {}
        cur_scores = (cur.get("sub_pillar_scores_validated") or {})
        res_scores = (v.get("sub_pillar_scores_researched") or {})

        if str(flag) != "good_evidence":
            # cap rule: no sub-pillar > 3.0
            for sid in SUBPILLARS:
                b = _safe_float(res_scores.get(sid))
                if b > 3.0:
                    capped_subpillars += 1
            if any(_safe_float(res_scores.get(sid)) > 3.0 for sid in SUBPILLARS):
                capped_vendors += 1

        for sid in SUBPILLARS:
            a = _safe_float(cur_scores.get(sid))
            b = _safe_float(res_scores.get(sid))
            score_dist[b] += 1
            d = abs(a - b)
            if d >= 1.0:
                deltas.append((d, str(name), sid))

    deltas.sort(reverse=True)

    lines: List[str] = []
    lines.append("# Research Validation Report\n")
    lines.append("This report compares deterministic normalization scores (Vendor 4-0 Validated) to evidence-harvested heuristic scores (Vendor 4-1 Researched).\n")

    lines.append("## Coverage\n")
    lines.append(f"- Vendors in researched file: **{len(researched)}**\n")
    lines.append(f"- Vendors with at least one captured excerpt: **{excerpt_vendor_count}**\n")
    lines.append("\n")

    lines.append("## Flags\n")
    for k, v in sorted(flag_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"- `{k}`: {v}\n")
    lines.append("\n")

    lines.append("## Confidence\n")
    lines.append(f"- Avg confidence: **{_avg(conf_values):.2f}**\n")
    lines.append(f"- Min/Max confidence: **{min(conf_values):.2f}** / **{max(conf_values):.2f}**\n")
    lines.append("\n")

    lines.append("## Validation rule\n")
    lines.append("- Enforced rule: if `research_flag` is not `good_evidence`, then `sub_pillar_scores_researched[SID] <= 3.0` for all 20 sub-pillars.\n")
    lines.append(f"- Vendors violating the rule (should be 0): **{capped_vendors}**\n")
    lines.append(f"- Sub-pillar scores above 3.0 under non-good-evidence vendors (should be 0): **{capped_subpillars}**\n")
    lines.append("\n")

    lines.append("## Researched score distribution (all sub-pillars)\n")
    total_scores = sum(score_dist.values())
    for score in sorted(score_dist.keys()):
        c = score_dist[score]
        pct = (c / total_scores * 100.0) if total_scores else 0.0
        lines.append(f"- {score:.2f}: {c} ({pct:.1f}%)\n")
    lines.append("\n")

    lines.append("## Largest changes (|validated - researched| >= 1.0)\n")
    for d, name, sid in deltas[:50]:
        lines.append(f"- **{name}** {sid}: Δ {d:.2f}\n")
    if not deltas:
        lines.append("- (No changes >= 1.0 found)\n")

    lines.append("\n")
    lines.append("## Notes\n")
    lines.append("- The researched scores are **heuristic suggestions** derived from publicly fetchable web text and schema keyword matching.\n")
    lines.append("- The `sub_pillar_evidence` excerpts are intended as the *substance/justification* for each score, but they still require analyst review for final scoring.\n")

    args.out.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
