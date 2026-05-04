#!/usr/bin/env python3
"""
build_mq_scores.py — Magic Quadrant Scoring Calculator
=======================================================
Combines MDR capability, pricing, and MQ Gap data to produce the 15 MQ
criteria scores plus composite ATE (Y) and COV (X) axis positions.

Sources:
  1. MDR Services Vendor 2-1 Consolidated.json
  2. MDR Services Vendor Pricing 2-1 AI Enriched.json
  3. MDR Services Vendor MQ Gap 2-0 Researched.json
  4. MQ_Gap_Schema_1_0.json (formula definitions)

Output: MDR Services Vendor MQ Scores.json
"""
import json, statistics
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def load_json(name):
    with open(ROOT / name, "r", encoding="utf-8") as f:
        return json.load(f)

cap_data = load_json("MDR Services Vendor 2-1 Consolidated.json")
prc_data = load_json("MDR Services Vendor Pricing 2-1 AI Enriched.json")
gap_data = load_json("MDR Services Vendor MQ Gap 2-0 Researched.json")

cap_by_vendor = {v["vendor"]: v for v in cap_data["vendors"]}
prc_by_vendor = {v["vendor"]: v for v in prc_data["vendors"]}
gap_by_vendor = {v["vendor"]: v for v in gap_data["vendors"]}

def clamp(val, lo=0.0, hi=5.0):
    return round(max(lo, min(hi, val)), 2)

def safe_avg(vals):
    nums = [v for v in vals if isinstance(v, (int, float))]
    return sum(nums) / len(nums) if nums else 2.0

def get_pillar(cap, pillar_code):
    ps = cap.get("pillar_scores_v2_1") or cap.get("pillar_scores", {})
    return ps.get(pillar_code, 2.0)

def get_sub(cap, sp_code):
    sp = cap.get("sub_pillar_scores_v2_1") or cap.get("sub_pillar_scores_current", {})
    v = sp.get(sp_code, 2.0)
    return v if isinstance(v, (int, float)) else 2.0

def get_gap_pillar(gap, pillar_code):
    ps = gap.get("mq_gap_pillar_scores", {})
    return ps.get(pillar_code, 2.0)

def get_gap_sub(gap, sp_code):
    sp = gap.get("mq_gap_sub_pillar_scores", {})
    v = sp.get(sp_code, 2.0)
    return v if isinstance(v, (int, float)) else 2.0

# ── MQ Criteria Scoring Functions ────────────────────────────────────

def calc_ate_1(cap, prc, gap):
    """ATE-1: Products/Services — Weighted average of MDR pillar scores"""
    weights = {"TDR": 0.25, "PTI": 0.15, "ADA": 0.05, "DIS": 0.05,
               "IRA": 0.15, "AIO": 0.15, "AID": 0.10, "SOG": 0.10}
    score = sum(get_pillar(cap, p) * w for p, w in weights.items())
    return clamp(score)

def calc_ate_2(cap, prc, gap):
    """ATE-2: Overall Viability — VIA pillar average"""
    return clamp(get_gap_pillar(gap, "VIA"))

def calc_ate_3(cap, prc, gap):
    """ATE-3: Sales Execution/Pricing — 40% pricing + 60% SLE"""
    pricing_score = 2.0
    if prc:
        pricing_score = prc.get("pricing_overall_score_v2",
                                prc.get("pricing_overall_score", 2.0))
    sle = get_gap_pillar(gap, "SLE")
    return clamp(pricing_score * 0.40 + sle * 0.60)

def calc_ate_4(cap, prc, gap):
    """ATE-4: Market Responsiveness — MKR pillar average"""
    return clamp(get_gap_pillar(gap, "MKR"))

def calc_ate_5(cap, prc, gap):
    """ATE-5: Marketing Execution — MKE pillar average"""
    return clamp(get_gap_pillar(gap, "MKE"))

def calc_ate_6(cap, prc, gap):
    """ATE-6: Customer Experience — 50% SOG + 50% CXQ"""
    sog = get_pillar(cap, "SOG")
    cxq = get_gap_pillar(gap, "CXQ")
    return clamp(sog * 0.50 + cxq * 0.50)

def calc_ate_7(cap, prc, gap):
    """ATE-7: Operations — 40% SOG + 30% IRA + 30% TDR-04"""
    sog = get_pillar(cap, "SOG")
    ira = get_pillar(cap, "IRA")
    tdr04 = get_sub(cap, "TDR-04")
    return clamp(sog * 0.40 + ira * 0.30 + tdr04 * 0.30)

def calc_cov_1(cap, prc, gap):
    """COV-1: Market Understanding — 50% MKU-01 + 25% target breadth + 25% service maturity"""
    mku01 = get_gap_sub(gap, "MKU-01")
    # Target market breadth
    tm = cap.get("target_market", "")
    tm_score = {"Enterprise": 3.0, "Mid-Market + Enterprise": 3.5,
                "Mid-Market": 2.5, "SMB + Mid-Market": 2.5,
                "SMB": 2.0}.get(tm, 2.0)
    # Service type maturity
    st = cap.get("mdr_service_type", "")
    st_score = {"Platform MDR": 4.0, "Turnkey MDR": 3.5, "Hybrid MDR": 3.5,
                "Consulting-Led MDR": 3.0, "Niche MDR": 2.5}.get(st, 2.5)
    return clamp(mku01 * 0.50 + tm_score * 0.25 + st_score * 0.25)

def calc_cov_2(cap, prc, gap):
    """COV-2: Marketing Strategy — MKE pillar (shared with ATE-5)"""
    return clamp(get_gap_pillar(gap, "MKE"))

def calc_cov_3(cap, prc, gap):
    """COV-3: Sales Strategy — weighted SLE sub-pillars"""
    s1 = get_gap_sub(gap, "SLE-01") * 0.35
    s2 = get_gap_sub(gap, "SLE-02") * 0.25
    s3 = get_gap_sub(gap, "SLE-03") * 0.25
    s4 = get_gap_sub(gap, "SLE-04") * 0.15
    return clamp(s1 + s2 + s3 + s4)

def calc_cov_4(cap, prc, gap):
    """COV-4: Offering Strategy — 25% AIO + 25% AID + 25% MKU-02 + 25% MKU-03"""
    aio = get_pillar(cap, "AIO")
    aid = get_pillar(cap, "AID")
    mku02 = get_gap_sub(gap, "MKU-02")
    mku03 = get_gap_sub(gap, "MKU-03")
    return clamp(aio * 0.25 + aid * 0.25 + mku02 * 0.25 + mku03 * 0.25)

def calc_cov_5(cap, prc, gap):
    """COV-5: Business Model — 35% pricing + 30% outcome + 35% MKU-04"""
    pricing_score = 2.0
    if prc:
        pricing_score = prc.get("pricing_overall_score_v2",
                                prc.get("pricing_overall_score", 2.0))
    omr = 2.0
    if prc:
        omr = prc.get("outcome_maturity_rating_v2",
                       prc.get("outcome_maturity_rating", 2.0))
    mku04 = get_gap_sub(gap, "MKU-04")
    return clamp(pricing_score * 0.35 + omr * 0.30 + mku04 * 0.35)

def calc_cov_6(cap, prc, gap):
    """COV-6: Vertical/Industry Strategy — 50% VIG-01 + 50% VIG-02"""
    v1 = get_gap_sub(gap, "VIG-01")
    v2 = get_gap_sub(gap, "VIG-02")
    return clamp(v1 * 0.50 + v2 * 0.50)

def calc_cov_7(cap, prc, gap):
    """COV-7: Innovation — MDR innovation pillars + gap R&D/competitive"""
    aio = get_pillar(cap, "AIO")
    aid = get_pillar(cap, "AID")
    ada = get_pillar(cap, "ADA")
    dis = get_pillar(cap, "DIS")
    mku02 = get_gap_sub(gap, "MKU-02")
    mkr02 = get_gap_sub(gap, "MKR-02")
    mkr03 = get_gap_sub(gap, "MKR-03")
    return clamp(aio * 0.20 + aid * 0.20 + ada * 0.15 + dis * 0.10 +
                 mku02 * 0.15 + mkr02 * 0.10 + mkr03 * 0.10)

def calc_cov_8(cap, prc, gap):
    """COV-8: Geographic Strategy — 50% VIG-03 + 50% VIG-04"""
    v3 = get_gap_sub(gap, "VIG-03")
    v4 = get_gap_sub(gap, "VIG-04")
    return clamp(v3 * 0.50 + v4 * 0.50)

# ── Axis weights from schema ────────────────────────────────────────

ATE_CRITERIA = [
    ("ATE-1", "Products/Services", 0.20, calc_ate_1),
    ("ATE-2", "Overall Viability", 0.18, calc_ate_2),
    ("ATE-3", "Sales Execution/Pricing", 0.12, calc_ate_3),
    ("ATE-4", "Market Responsiveness", 0.12, calc_ate_4),
    ("ATE-5", "Marketing Execution", 0.06, calc_ate_5),
    ("ATE-6", "Customer Experience", 0.18, calc_ate_6),
    ("ATE-7", "Operations", 0.14, calc_ate_7),
]

COV_CRITERIA = [
    ("COV-1", "Market Understanding", 0.18, calc_cov_1),
    ("COV-2", "Marketing Strategy", 0.10, calc_cov_2),
    ("COV-3", "Sales Strategy", 0.10, calc_cov_3),
    ("COV-4", "Offering Strategy", 0.18, calc_cov_4),
    ("COV-5", "Business Model", 0.12, calc_cov_5),
    ("COV-6", "Vertical/Industry Strategy", 0.08, calc_cov_6),
    ("COV-7", "Innovation", 0.16, calc_cov_7),
    ("COV-8", "Geographic Strategy", 0.08, calc_cov_8),
]

# ── Main ─────────────────────────────────────────────────────────────

def score_vendor(vname):
    cap = cap_by_vendor.get(vname, {})
    prc = prc_by_vendor.get(vname)
    gap = gap_by_vendor.get(vname, {})

    # Score all 15 criteria
    ate_scores = {}
    ate_weighted = 0.0
    for cid, cname, weight, fn in ATE_CRITERIA:
        score = fn(cap, prc, gap)
        ate_scores[cid] = {"name": cname, "score": score, "weight": weight}
        ate_weighted += score * weight

    cov_scores = {}
    cov_weighted = 0.0
    for cid, cname, weight, fn in COV_CRITERIA:
        score = fn(cap, prc, gap)
        cov_scores[cid] = {"name": cname, "score": score, "weight": weight}
        cov_weighted += score * weight

    ate_composite = clamp(ate_weighted)
    cov_composite = clamp(cov_weighted)

    return {
        "vendor": vname,
        "website": cap.get("website", ""),
        "headquarters": cap.get("headquarters", ""),
        "region": cap.get("region", ""),
        "employee_count_range": cap.get("employee_count_range", ""),
        "funding_stage": cap.get("funding_stage", ""),
        "mdr_service_type": cap.get("mdr_service_type", ""),
        "target_market": cap.get("target_market", ""),
        "ability_to_execute": {
            "composite_score": ate_composite,
            "criteria": ate_scores
        },
        "completeness_of_vision": {
            "composite_score": cov_composite,
            "criteria": cov_scores
        },
        "quadrant": None,  # Set after medians computed
        "mq_gap_research_tier": gap.get("mq_gap_research_tier", "unknown"),
    }


def main():
    all_vendors = sorted(set(cap_by_vendor.keys()) | set(gap_by_vendor.keys()))

    print(f"Computing MQ scores for {len(all_vendors)} vendors...")

    results = []
    ate_all = []
    cov_all = []

    for vname in all_vendors:
        r = score_vendor(vname)
        results.append(r)
        ate_all.append(r["ability_to_execute"]["composite_score"])
        cov_all.append(r["completeness_of_vision"]["composite_score"])

    # Compute medians for quadrant boundaries
    ate_median = statistics.median(ate_all)
    cov_median = statistics.median(cov_all)

    print(f"\n  ATE median: {ate_median:.2f}")
    print(f"  COV median: {cov_median:.2f}")

    # Assign quadrants
    quadrant_counts = {"Leaders": 0, "Challengers": 0,
                       "Visionaries": 0, "Niche Players": 0}
    for r in results:
        ate = r["ability_to_execute"]["composite_score"]
        cov = r["completeness_of_vision"]["composite_score"]
        if ate >= ate_median and cov >= cov_median:
            r["quadrant"] = "Leaders"
        elif ate >= ate_median and cov < cov_median:
            r["quadrant"] = "Challengers"
        elif ate < ate_median and cov >= cov_median:
            r["quadrant"] = "Visionaries"
        else:
            r["quadrant"] = "Niche Players"
        quadrant_counts[r["quadrant"]] += 1

    # Sort by ATE desc then COV desc
    results.sort(key=lambda x: (-x["ability_to_execute"]["composite_score"],
                                 -x["completeness_of_vision"]["composite_score"]))

    output = {
        "schema_ref": "MQ_Gap_Schema_1_0.json",
        "title": "Magic Quadrant for Managed Detection & Response Services",
        "methodology": "Composite scores derived from MDR capability (8 pillars), pricing (6 dimensions), and MQ Gap (7 pillars/28 sub-pillars) data. ATE and COV each have weighted criteria per Gartner MQ methodology.",
        "vendor_count": len(results),
        "axis_statistics": {
            "ability_to_execute": {
                "median": ate_median,
                "min": min(ate_all),
                "max": max(ate_all),
                "mean": round(statistics.mean(ate_all), 2),
                "stdev": round(statistics.stdev(ate_all), 2)
            },
            "completeness_of_vision": {
                "median": cov_median,
                "min": min(cov_all),
                "max": max(cov_all),
                "mean": round(statistics.mean(cov_all), 2),
                "stdev": round(statistics.stdev(cov_all), 2)
            }
        },
        "quadrant_boundaries": {
            "ate_threshold": ate_median,
            "cov_threshold": cov_median,
            "method": "Population median split"
        },
        "quadrant_distribution": quadrant_counts,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script": "build_mq_scores.py",
        "vendors": results
    }

    out_file = ROOT / "MDR Services Vendor MQ Scores.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nGenerated {out_file.name}")
    print(f"  Total vendors: {len(results)}")
    print(f"\n  Quadrant distribution:")
    for q, c in quadrant_counts.items():
        print(f"    {q}: {c}")

    # Show top 5 per quadrant
    for q in ["Leaders", "Challengers", "Visionaries", "Niche Players"]:
        print(f"\n  Top 5 {q}:")
        q_vendors = [r for r in results if r["quadrant"] == q]
        for r in q_vendors[:5]:
            ate = r["ability_to_execute"]["composite_score"]
            cov = r["completeness_of_vision"]["composite_score"]
            print(f"    {r['vendor']:30s}  ATE={ate:.2f}  COV={cov:.2f}")


if __name__ == "__main__":
    main()
