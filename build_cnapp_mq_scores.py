#!/usr/bin/env python3
"""
build_cnapp_mq_scores.py — CNAPP Magic Quadrant Composite Scoring
==================================================================
Combines CNAPP capability scores + CNAPP MQ Gap scores into the 14
Magic Quadrant criteria (7 ATE + 7 COV) and computes weighted axis
composites + quadrant assignment by population median split.

Formulas exactly match CNAPP_MQ_Gap_Schema_App.json -> mq_scoring_mode.

Sources:
  1. CNAPP Vendor 1-2 Researched.json        (capability data)
  2. CNAPP MQ Vendor 1-1 Researched.json     (MQ gap heuristic scores)

Output: CNAPP Vendor MQ Scores.json
"""
import argparse
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def load_json(name):
    with open(ROOT / name, "r", encoding="utf-8") as f:
        return json.load(f)

# ── CLI ─────────────────────────────────────────────────────────────
_parser = argparse.ArgumentParser()
_parser.add_argument("--mode", choices=["v1", "v2"], default="v1",
                     help="v1 = heuristic (CNAPP MQ Vendor 1-1), v2 = evidence-enriched (1-2 with *_v12 keys)")
ARGS, _ = _parser.parse_known_args()
MODE = ARGS.mode

cap_data = load_json("CNAPP Vendor 1-2 Researched.json")
if MODE == "v2":
    gap_data = load_json("CNAPP MQ Vendor 1-2 Researched.json")
    GAP_PILLAR_KEY = "pillar_scores_v12"
    GAP_SUB_KEY = "sub_pillar_scores_v12"
    OUT_FILE = "CNAPP Vendor MQ Scores v2.json"
else:
    gap_data = load_json("CNAPP MQ Vendor 1-1 Researched.json")
    GAP_PILLAR_KEY = "mq_gap_pillar_scores"
    GAP_SUB_KEY = "mq_gap_sub_pillar_scores"
    OUT_FILE = "CNAPP Vendor MQ Scores.json"

cap_by_vendor = {v["vendor"]: v for v in cap_data["vendors"]}
gap_by_vendor = {v["vendor"]: v for v in gap_data["vendors"]}


def clamp(v, lo=0.0, hi=5.0):
    return round(max(lo, min(hi, v)), 2)

def cap_pillar(cap, code):
    ps = cap.get("pillar_scores", {}) or {}
    v = ps.get(code, 2.0)
    return v if isinstance(v, (int, float)) else 2.0

def gap_pillar(gap, code):
    ps = gap.get(GAP_PILLAR_KEY) or gap.get("mq_gap_pillar_scores", {}) or {}
    v = ps.get(code, 2.0)
    return v if isinstance(v, (int, float)) else 2.0

def gap_sub(gap, code):
    sp = gap.get(GAP_SUB_KEY) or gap.get("mq_gap_sub_pillar_scores", {}) or {}
    v = sp.get(code, 2.0)
    return v if isinstance(v, (int, float)) else 2.0

# ── ATE criteria ─────────────────────────────────────────────────────

def calc_ate_1(cap, gap):
    """ATE-1 Products/Services: CNAPP capability composite."""
    w = {"CSPM": 0.20, "CWPP": 0.18, "CIEM": 0.15, "SHIFT": 0.12,
         "CDR": 0.15, "DSPM": 0.12, "FRNG": 0.08}
    return clamp(sum(cap_pillar(cap, p) * wt for p, wt in w.items()))

def calc_ate_2(cap, gap):
    """ATE-2 Overall Viability: VIA pillar avg."""
    return clamp(gap_pillar(gap, "VIA"))

def calc_ate_3(cap, gap):
    """ATE-3 Sales Execution/Pricing: SLE pillar avg."""
    return clamp(gap_pillar(gap, "SLE"))

def calc_ate_4(cap, gap):
    """ATE-4 Market Responsiveness: MKR pillar avg."""
    return clamp(gap_pillar(gap, "MKR"))

def calc_ate_5(cap, gap):
    """ATE-5 Marketing Execution: MKE pillar avg."""
    return clamp(gap_pillar(gap, "MKE"))

def calc_ate_6(cap, gap):
    """ATE-6 Customer Experience: CXQ pillar avg."""
    return clamp(gap_pillar(gap, "CXQ"))

def calc_ate_7(cap, gap):
    """ATE-7 Operations: CDR*0.40 + CSPM*0.30 + CWPP*0.30."""
    return clamp(cap_pillar(cap, "CDR") * 0.40 +
                 cap_pillar(cap, "CSPM") * 0.30 +
                 cap_pillar(cap, "CWPP") * 0.30)

# ── COV criteria ─────────────────────────────────────────────────────

def calc_cov_1(cap, gap):
    """COV-1 Market Understanding: MKU-01."""
    return clamp(gap_sub(gap, "MKU-01"))

def calc_cov_2(cap, gap):
    """COV-2 Marketing Strategy: MKE-02*0.40 + MKE-04*0.60."""
    return clamp(gap_sub(gap, "MKE-02") * 0.40 +
                 gap_sub(gap, "MKE-04") * 0.60)

def calc_cov_3(cap, gap):
    """COV-3 Sales Strategy: SLE-01*0.40 + SLE-03*0.30 + SLE-04*0.30."""
    return clamp(gap_sub(gap, "SLE-01") * 0.40 +
                 gap_sub(gap, "SLE-03") * 0.30 +
                 gap_sub(gap, "SLE-04") * 0.30)

def calc_cov_4(cap, gap):
    """COV-4 Offering (Product) Strategy: (DSPM+FRNG)/2*0.50 + MKU-02*0.25 + MKU-03*0.25."""
    innov = (cap_pillar(cap, "DSPM") + cap_pillar(cap, "FRNG")) / 2.0
    return clamp(innov * 0.50 +
                 gap_sub(gap, "MKU-02") * 0.25 +
                 gap_sub(gap, "MKU-03") * 0.25)

def calc_cov_6(cap, gap):
    """COV-6 Vertical/Industry Strategy: avg(VIG-01, VIG-02)."""
    return clamp((gap_sub(gap, "VIG-01") + gap_sub(gap, "VIG-02")) / 2.0)

def calc_cov_7(cap, gap):
    """COV-7 Innovation: FRNG*0.40 + DSPM*0.30 + CDR*0.20 + SHIFT*0.10."""
    return clamp(cap_pillar(cap, "FRNG") * 0.40 +
                 cap_pillar(cap, "DSPM") * 0.30 +
                 cap_pillar(cap, "CDR") * 0.20 +
                 cap_pillar(cap, "SHIFT") * 0.10)

def calc_cov_8(cap, gap):
    """COV-8 Geographic Strategy: avg(VIG-03, VIG-04)."""
    return clamp((gap_sub(gap, "VIG-03") + gap_sub(gap, "VIG-04")) / 2.0)


ATE_CRITERIA = [
    ("ATE-1", "Products/Services",                0.23, calc_ate_1),
    ("ATE-2", "Overall Viability",                0.21, calc_ate_2),
    ("ATE-3", "Sales Execution/Pricing",          0.14, calc_ate_3),
    ("ATE-4", "Market Responsiveness & Track Record", 0.09, calc_ate_4),
    ("ATE-5", "Marketing Execution",              0.09, calc_ate_5),
    ("ATE-6", "Customer Experience",              0.12, calc_ate_6),
    ("ATE-7", "Operations",                       0.12, calc_ate_7),
]

COV_CRITERIA = [
    ("COV-1", "Market Understanding",             0.19, calc_cov_1),
    ("COV-2", "Marketing Strategy",               0.11, calc_cov_2),
    ("COV-3", "Sales Strategy",                   0.11, calc_cov_3),
    ("COV-4", "Offering (Product) Strategy",      0.22, calc_cov_4),
    ("COV-6", "Vertical/Industry Strategy",       0.09, calc_cov_6),
    ("COV-7", "Innovation",                       0.19, calc_cov_7),
    ("COV-8", "Geographic Strategy",              0.09, calc_cov_8),
]


def score_vendor(vname):
    cap = cap_by_vendor.get(vname, {})
    gap = gap_by_vendor.get(vname, {})

    ate_scores, ate_w = {}, 0.0
    for cid, cname, w, fn in ATE_CRITERIA:
        s = fn(cap, gap)
        ate_scores[cid] = {"name": cname, "score": s, "weight": w}
        ate_w += s * w

    cov_scores, cov_w = {}, 0.0
    for cid, cname, w, fn in COV_CRITERIA:
        s = fn(cap, gap)
        cov_scores[cid] = {"name": cname, "score": s, "weight": w}
        cov_w += s * w

    return {
        "vendor": vname,
        "website": cap.get("website", "") or gap.get("website", ""),
        "headquarters": cap.get("headquarters", "") or gap.get("headquarters", ""),
        "region": cap.get("region", "") or gap.get("region", ""),
        "year_founded": cap.get("year_founded") or gap.get("year_founded"),
        "employee_count_range": cap.get("employee_count_range", "") or gap.get("employee_count_range", ""),
        "funding_stage": cap.get("funding_stage", "") or gap.get("funding_stage", ""),
        "total_funding": cap.get("total_funding", "") or gap.get("total_funding", ""),
        "cnapp_vendor_type": cap.get("cnapp_vendor_type", "") or gap.get("cnapp_vendor_type", ""),
        "cloud_coverage": cap.get("cloud_coverage", "") or gap.get("cloud_coverage", ""),
        "deployment_model": cap.get("deployment_model", "") or gap.get("deployment_model", ""),
        "target_market": cap.get("target_market", "") or gap.get("target_market", ""),
        "is_ai_first": cap.get("is_ai_first", False),
        "capability_pillar_scores": cap.get("pillar_scores", {}),
        "capability_coverage_grade": cap.get("coverage_grade", ""),
        "mq_gap_pillar_scores": gap.get(GAP_PILLAR_KEY) or gap.get("mq_gap_pillar_scores", {}),
        "ability_to_execute": {
            "composite_score": clamp(ate_w),
            "criteria": ate_scores,
        },
        "completeness_of_vision": {
            "composite_score": clamp(cov_w),
            "criteria": cov_scores,
        },
        "quadrant": None,
        "mq_gap_research_tier": gap.get("mq_gap_research_tier", "tier_2"),
        "mq_gap_research_confidence": gap.get("mq_gap_research_confidence", "low"),
    }


def main():
    vendors = sorted(set(cap_by_vendor) | set(gap_by_vendor))
    print(f"Scoring {len(vendors)} vendors across 14 MQ criteria (7 ATE + 7 COV)...")

    results, ate_all, cov_all = [], [], []
    for v in vendors:
        r = score_vendor(v)
        results.append(r)
        ate_all.append(r["ability_to_execute"]["composite_score"])
        cov_all.append(r["completeness_of_vision"]["composite_score"])

    ate_med = statistics.median(ate_all)
    cov_med = statistics.median(cov_all)
    print(f"  ATE median: {ate_med:.2f}")
    print(f"  COV median: {cov_med:.2f}")

    quad_counts = {"Leaders": 0, "Challengers": 0,
                   "Visionaries": 0, "Niche Players": 0}
    for r in results:
        ate = r["ability_to_execute"]["composite_score"]
        cov = r["completeness_of_vision"]["composite_score"]
        if ate >= ate_med and cov >= cov_med:
            r["quadrant"] = "Leaders"
        elif ate >= ate_med:
            r["quadrant"] = "Challengers"
        elif cov >= cov_med:
            r["quadrant"] = "Visionaries"
        else:
            r["quadrant"] = "Niche Players"
        quad_counts[r["quadrant"]] += 1

    results.sort(key=lambda x: (-x["ability_to_execute"]["composite_score"],
                                 -x["completeness_of_vision"]["composite_score"]))

    out = {
        "schema_ref": "CNAPP_MQ_Gap_Schema_App.json",
        "title": "Magic Quadrant for Cloud-Native Application Protection Platforms",
        "methodology": ("Composite scores derived from CNAPP capability data "
                        "(7 pillars / 29 sub-pillars) and CNAPP MQ Gap heuristics "
                        "(7 pillars / 27 sub-pillars). 14 MQ criteria computed per "
                        "CNAPP_MQ_Gap_Schema_App.json mq_scoring_mode and weighted "
                        "to produce ATE (Y) and COV (X) composites. Quadrant assigned "
                        "by population median split."),
        "vendor_count": len(results),
        "axis_statistics": {
            "ability_to_execute": {
                "median": ate_med, "min": min(ate_all), "max": max(ate_all),
                "mean": round(statistics.mean(ate_all), 2),
                "stdev": round(statistics.stdev(ate_all), 2) if len(ate_all) > 1 else 0,
            },
            "completeness_of_vision": {
                "median": cov_med, "min": min(cov_all), "max": max(cov_all),
                "mean": round(statistics.mean(cov_all), 2),
                "stdev": round(statistics.stdev(cov_all), 2) if len(cov_all) > 1 else 0,
            },
        },
        "quadrant_boundaries": {
            "ate_threshold": ate_med, "cov_threshold": cov_med,
            "method": "Population median split",
        },
        "quadrant_distribution": quad_counts,
        "criterion_weights": {
            "ability_to_execute": {c[0]: {"name": c[1], "weight": c[2]} for c in ATE_CRITERIA},
            "completeness_of_vision": {c[0]: {"name": c[1], "weight": c[2]} for c in COV_CRITERIA},
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script": "build_cnapp_mq_scores.py",
        "vendors": results,
    }

    out["score_mode"] = MODE
    out_file = ROOT / OUT_FILE
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {out_file.name}")
    print(f"  Total vendors: {len(results)}")
    print("\n  Quadrant distribution:")
    for q, c in quad_counts.items():
        print(f"    {q}: {c}")
    for q in ("Leaders", "Challengers", "Visionaries", "Niche Players"):
        print(f"\n  {q}:")
        for r in [x for x in results if x["quadrant"] == q]:
            ate = r["ability_to_execute"]["composite_score"]
            cov = r["completeness_of_vision"]["composite_score"]
            print(f"    {r['vendor']:25s}  ATE={ate:.2f}  COV={cov:.2f}")


if __name__ == "__main__":
    main()
