"""
Build MDR Services Vendor Pricing 2-1 AI Enriched JSON.

Merges capability data (AI pillar scores) with pricing data to compute:
  - ai_pricing_influence (1-5): How AI adoption influences pricing model maturity
  - pricing_strengths / pricing_weaknesses: Per-dimension analysis
  - pricing_recommendations: Phased improvement roadmap
  - ai_pricing_narrative: Explains the AI→pricing relationship per vendor

Inputs:
  - MDR Services Vendor 2-1 Consolidated.json  (capability scores)
  - MDR Services Vendor Pricing 2-0 Researched.json  (pricing scores)

Output:
  - MDR Services Vendor Pricing 2-1 AI Enriched.json
"""

import json
import statistics
from datetime import datetime, timezone

# ── Config ──────────────────────────────────────────────────────────────────
CAPABILITY_FILE = "MDR Services Vendor 2-1 Consolidated.json"
PRICING_FILE = "MDR Services Vendor Pricing 2-0 Researched.json"
OUTPUT_FILE = "MDR Services Vendor Pricing 2-1 AI Enriched.json"

DIMENSIONS = ["PRC-SUB", "PRC-USG", "PRC-FIX", "PRC-SUC", "PRC-COM", "PRC-OUT"]
DIMENSION_LABELS = {
    "PRC-SUB": "Subscription Transparency",
    "PRC-USG": "Usage-Based Alignment",
    "PRC-FIX": "Fixed Delivery Pricing",
    "PRC-SUC": "Success & Outcome Fees",
    "PRC-COM": "Composability & Overall Model Maturity",
    "PRC-OUT": "Pricing-to-Outcomes Alignment",
}

# Weights for AI Pricing Influence score
AI_WEIGHTS = {
    "AIO": 0.25,       # AI operational maturity
    "AID": 0.15,       # AI development/platform investment
    "PRC-OUT": 0.25,   # Pricing-to-outcomes alignment
    "PRC-SUC": 0.15,   # Success & outcome fee adoption
    "outcome": 0.15,   # Overall outcome maturity rating
    "ai_signal": 0.05, # ai_efficiency_shared boolean (×5 to scale)
}

# Dimension importance for roadmap priority (higher = more important for thesis)
DIM_IMPORTANCE = {
    "PRC-OUT": 1.3,  # Most thesis-relevant
    "PRC-SUC": 1.2,
    "PRC-COM": 1.1,
    "PRC-USG": 1.0,
    "PRC-SUB": 0.9,
    "PRC-FIX": 0.9,
}


def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def compute_ai_pricing_influence(cap_vendor, prc_vendor):
    """Compute the 1-5 AI Pricing Influence score."""
    aio = cap_vendor.get("pillar_scores", {}).get("AIO", 1)
    aid = cap_vendor.get("pillar_scores", {}).get("AID", 1)
    prc_out = prc_vendor.get("pricing_dimension_scores", {}).get("PRC-OUT", 1)
    prc_suc = prc_vendor.get("pricing_dimension_scores", {}).get("PRC-SUC", 1)
    outcome = prc_vendor.get("outcome_maturity_rating", 1)
    ai_signal = prc_vendor.get("outcome_signals_v2", {}).get("ai_efficiency_shared", False)

    raw = (
        AI_WEIGHTS["AIO"] * aio
        + AI_WEIGHTS["AID"] * aid
        + AI_WEIGHTS["PRC-OUT"] * prc_out
        + AI_WEIGHTS["PRC-SUC"] * prc_suc
        + AI_WEIGHTS["outcome"] * outcome
        + AI_WEIGHTS["ai_signal"] * (5 if ai_signal else 0)
    )

    # Bonus for AI-first companies
    if cap_vendor.get("is_ai_first", False):
        raw += 0.3

    return round(max(1.0, min(5.0, raw)), 2)


def classify_ai_influence(score):
    """Return a maturity label for the AI pricing influence score."""
    if score >= 4.0:
        return "Transformative"
    if score >= 3.0:
        return "Significant"
    if score >= 2.0:
        return "Emerging"
    return "Minimal"


def generate_ai_narrative(vendor_name, score, label, cap_vendor, prc_vendor):
    """Generate an AI→pricing narrative for a vendor."""
    aio = cap_vendor.get("pillar_scores", {}).get("AIO", 1)
    aid = cap_vendor.get("pillar_scores", {}).get("AID", 1)
    prc_out = prc_vendor.get("pricing_dimension_scores", {}).get("PRC-OUT", 1)
    prc_suc = prc_vendor.get("pricing_dimension_scores", {}).get("PRC-SUC", 1)
    model_type = prc_vendor.get("pricing_model_type", "Unknown")
    is_ai_first = cap_vendor.get("is_ai_first", False)

    parts = []

    # Opening
    if score >= 4.0:
        parts.append(
            f"{vendor_name} demonstrates a transformative relationship between AI adoption "
            f"and pricing model maturity (AI Pricing Influence: {score}/5)."
        )
    elif score >= 3.0:
        parts.append(
            f"{vendor_name} shows significant AI influence on its pricing approach "
            f"(AI Pricing Influence: {score}/5)."
        )
    elif score >= 2.0:
        parts.append(
            f"{vendor_name} has emerging connections between AI capabilities and pricing "
            f"structure (AI Pricing Influence: {score}/5)."
        )
    else:
        parts.append(
            f"{vendor_name}'s AI adoption has minimal visible influence on pricing model "
            f"maturity (AI Pricing Influence: {score}/5)."
        )

    # AI maturity context
    if aio >= 4:
        parts.append(
            f"With strong AI operational maturity (AIO: {aio}/5), the vendor has a solid "
            f"foundation for translating AI efficiency gains into pricing advantages."
        )
    elif aio >= 3:
        parts.append(
            f"Moderate AI operational maturity (AIO: {aio}/5) provides a developing "
            f"foundation for AI-driven pricing evolution."
        )
    else:
        parts.append(
            f"Lower AI operational maturity (AIO: {aio}/5) limits the potential for "
            f"AI-driven pricing transformation."
        )

    # Pricing model connection
    if prc_out >= 3 and prc_suc >= 3:
        parts.append(
            f"The vendor's pricing already reflects outcome alignment (PRC-OUT: {prc_out}, "
            f"PRC-SUC: {prc_suc}), suggesting AI capabilities are beginning to reshape "
            f"commercial models toward shared-risk and performance-based structures."
        )
    elif prc_out >= 2 or prc_suc >= 2:
        parts.append(
            f"Early outcome signals exist (PRC-OUT: {prc_out}, PRC-SUC: {prc_suc}) but "
            f"the pricing model has not yet fully absorbed AI-driven efficiency gains "
            f"into client-facing commercial terms."
        )
    else:
        parts.append(
            f"Outcome-based pricing elements remain nascent (PRC-OUT: {prc_out}, "
            f"PRC-SUC: {prc_suc}), indicating a gap between AI investment and "
            f"commercial model evolution."
        )

    # Model type context
    if model_type == "Composable":
        parts.append(
            "The composable pricing model provides structural flexibility to incorporate "
            "AI-driven modules and outcome-based pricing tiers as the market matures."
        )
    elif model_type == "Subscription-Only":
        parts.append(
            "The subscription-only model may constrain the vendor's ability to pass "
            "AI efficiency gains to clients through pricing innovation."
        )

    return " ".join(parts)


def compute_benchmarks(vendors):
    """Compute market average and top-10 average per pricing dimension."""
    benchmarks = {}
    for dim in DIMENSIONS:
        scores = []
        for v in vendors:
            s = v.get("pricing_dimension_scores", {}).get(dim)
            if s is not None:
                scores.append(s)
        if scores:
            sorted_scores = sorted(scores, reverse=True)
            top10 = sorted_scores[: min(10, len(sorted_scores))]
            benchmarks[dim] = {
                "market_avg": round(statistics.mean(scores), 2),
                "top10_avg": round(statistics.mean(top10), 2),
                "median": round(statistics.median(scores), 1),
                "count": len(scores),
            }
        else:
            benchmarks[dim] = {"market_avg": 0, "top10_avg": 0, "median": 0, "count": 0}

    # Overall score benchmarks
    overall_scores = [v.get("pricing_overall_score", 0) for v in vendors]
    sorted_overall = sorted(overall_scores, reverse=True)
    top10_overall = sorted_overall[: min(10, len(sorted_overall))]
    benchmarks["overall"] = {
        "market_avg": round(statistics.mean(overall_scores), 2),
        "top10_avg": round(statistics.mean(top10_overall), 2),
    }
    return benchmarks


def classify_strengths_weaknesses(vendor, benchmarks):
    """Classify each pricing dimension as strength, weakness, or neutral."""
    strengths = []
    weaknesses = []
    rationale_v2 = vendor.get("pricing_dimension_rationale_v2", {})

    for dim in DIMENSIONS:
        score = vendor.get("pricing_dimension_scores", {}).get(dim, 0)
        bm = benchmarks.get(dim, {})
        market_avg = bm.get("market_avg", 2.5)
        top10_avg = bm.get("top10_avg", 4.0)
        delta_avg = round(score - market_avg, 2)
        delta_top10 = round(score - top10_avg, 2)
        gap_to_top10 = round(top10_avg - score, 2)

        # Get rationale data
        dim_rationale = rationale_v2.get(dim, {})
        grade = dim_rationale.get("evidence_quality_grade", "")
        criteria = dim_rationale.get("criteria_assessment", [])
        met = [c for c in criteria if c.get("status") == "met"]
        partial = [c for c in criteria if c.get("status") == "partial"]
        unmet = [c for c in criteria if c.get("status") == "unmet"]
        adjustment_reason = dim_rationale.get("adjustment_reason", "")

        entry = {
            "dimension": dim,
            "label": DIMENSION_LABELS.get(dim, dim),
            "score": score,
            "market_avg": market_avg,
            "top10_avg": top10_avg,
            "delta_avg": delta_avg,
            "delta_top10": delta_top10,
            "gap_to_top10": gap_to_top10,
            "grade": grade,
            "met_count": len(met),
            "partial_count": len(partial),
            "unmet_count": len(unmet),
            "total_criteria": len(criteria),
            "met_criteria": [c.get("criterion", "")[:150] for c in met[:3]],
            "unmet_criteria": [c.get("criterion", "")[:150] for c in unmet[:3]],
            "partial_criteria": [c.get("criterion", "")[:150] for c in partial[:3]],
            "adjustment_reason": adjustment_reason[:200] if adjustment_reason else "",
        }

        # Strength classification
        is_strength = (
            score >= top10_avg - 0.3
            or (score >= market_avg + 0.5 and grade in ("A", "B"))
        )
        # Weakness classification
        is_weakness = score < market_avg - 0.3 or gap_to_top10 >= 1.0

        if is_strength:
            strengths.append(entry)
        elif is_weakness:
            weaknesses.append(entry)

    # Sort by delta
    strengths.sort(key=lambda x: x["delta_avg"], reverse=True)
    weaknesses.sort(key=lambda x: x["delta_avg"])

    return strengths, weaknesses


def generate_roadmap(vendor, benchmarks):
    """Generate a prioritized improvement roadmap for pricing."""
    items = []
    rationale_v2 = vendor.get("pricing_dimension_rationale_v2", {})

    for dim in DIMENSIONS:
        score = vendor.get("pricing_dimension_scores", {}).get(dim, 0)
        bm = benchmarks.get(dim, {})
        market_avg = bm.get("market_avg", 2.5)
        top10_avg = bm.get("top10_avg", 4.0)
        gap_avg = round(market_avg - score, 2)
        gap_top10 = round(top10_avg - score, 2)

        if gap_top10 <= 0.1:
            continue  # No improvement needed

        importance = DIM_IMPORTANCE.get(dim, 1.0)

        # Criteria analysis for actionable items
        dim_rationale = rationale_v2.get(dim, {})
        criteria = dim_rationale.get("criteria_assessment", [])
        partial = [c for c in criteria if c.get("status") == "partial"]
        unmet = [c for c in criteria if c.get("status") == "unmet"]

        # Feasibility: more partial items = easier wins
        feasibility = len(partial) * 0.3 + (0.2 if unmet else 0)

        # Priority score
        gap_factor = max(gap_top10, 0) * 2
        importance_factor = importance * 1.5 * (0.5 if gap_avg <= 0 else 1.2)
        priority_score = round(gap_factor + importance_factor + feasibility, 2)

        # Target score
        target = min(round(max(score + gap_top10 * 0.7, score + 0.5) * 100) / 100, 5.0)

        # Action items from unmet/partial criteria
        actions = []
        for c in unmet[:2]:
            actions.append(c.get("criterion", "")[:150])
        for c in partial[:2]:
            actions.append(f"Strengthen: {c.get('criterion', '')[:140]}")

        items.append({
            "dimension": dim,
            "label": DIMENSION_LABELS.get(dim, dim),
            "current_score": score,
            "target_score": target,
            "gap_to_avg": gap_avg,
            "gap_to_top10": gap_top10,
            "priority_score": priority_score,
            "importance": importance,
            "actions": actions[:4],
        })

    # Sort by priority descending
    items.sort(key=lambda x: x["priority_score"], reverse=True)

    # Assign phases
    total = len(items)
    if total == 0:
        return []

    phase1_end = max(1, round(total * 0.35))
    phase2_end = max(phase1_end + 1, round(total * 0.70))

    for i, item in enumerate(items):
        if i < phase1_end:
            item["phase"] = 1
            item["phase_name"] = "Quick Wins (0-6 months)"
        elif i < phase2_end:
            item["phase"] = 2
            item["phase_name"] = "Core Investment (6-12 months)"
        else:
            item["phase"] = 3
            item["phase_name"] = "Strategic Differentiation (12-18 months)"

        # Priority label
        if item["priority_score"] >= 5:
            item["priority_label"] = "high"
        elif item["priority_score"] >= 3:
            item["priority_label"] = "medium"
        else:
            item["priority_label"] = "low"

    return items


def generate_recommendations(vendor_name, strengths, weaknesses, roadmap, ai_score, cap_vendor):
    """Generate actionable recommendations for a vendor."""
    recommendations = []
    model_type = cap_vendor.get("pricing_model_type", "Unknown") if "pricing_model_type" in cap_vendor else "Unknown"

    # AI-driven recommendation
    if ai_score < 3.0:
        aio = cap_vendor.get("pillar_scores", {}).get("AIO", 1)
        if aio >= 3:
            recommendations.append({
                "priority": "high",
                "category": "AI-Pricing Alignment",
                "recommendation": (
                    f"Translate AI operational maturity (AIO: {aio}/5) into commercial "
                    f"differentiation by introducing AI-linked pricing mechanisms — such as "
                    f"efficiency-sharing credits, AI-driven SLA guarantees, or tiered "
                    f"pricing based on AI automation levels."
                ),
            })
        else:
            recommendations.append({
                "priority": "medium",
                "category": "AI-Pricing Foundation",
                "recommendation": (
                    "Invest in AI operational capabilities as a prerequisite for outcome-based "
                    "pricing evolution. Focus on AI-driven detection and response automation "
                    "to build the efficiency gains that can later be reflected in pricing."
                ),
            })
    else:
        recommendations.append({
            "priority": "medium",
            "category": "AI-Pricing Leadership",
            "recommendation": (
                "Continue leveraging AI maturity as a pricing differentiator. Consider "
                "publishing AI-driven efficiency metrics and tying contractual terms to "
                "measurable outcome improvements to maintain pricing leadership."
            ),
        })

    # Weakness-based recommendations
    for w in weaknesses[:2]:
        rec_text = f"Improve {w['label']} (current: {w['score']}, market avg: {w['market_avg']})."
        if w["unmet_criteria"]:
            rec_text += f" Priority: {w['unmet_criteria'][0]}"
        recommendations.append({
            "priority": "high" if w["gap_to_top10"] >= 1.5 else "medium",
            "category": w["label"],
            "recommendation": rec_text,
        })

    # Roadmap phase 1 recommendation
    phase1_items = [r for r in roadmap if r.get("phase") == 1]
    if phase1_items:
        dims_str = ", ".join(r["label"] for r in phase1_items[:3])
        recommendations.append({
            "priority": "high",
            "category": "Quick Wins",
            "recommendation": (
                f"Focus immediate pricing model improvements on: {dims_str}. "
                f"These dimensions offer the highest return on effort based on "
                f"gap-to-market analysis and criteria feasibility."
            ),
        })

    # Outcome maturity recommendation
    outcome = cap_vendor.get("outcome_maturity_rating", 1) if "outcome_maturity_rating" in cap_vendor else 1
    if outcome <= 2:
        recommendations.append({
            "priority": "medium",
            "category": "Outcome Maturity",
            "recommendation": (
                "Develop measurable outcome metrics (MTTD/MTTR improvement guarantees, "
                "incident reduction targets) that can be embedded in commercial terms. "
                "This is essential for transitioning to outcomes-based pricing."
            ),
        })

    return recommendations


def main():
    print("Loading data files...")
    cap_data = load_json(CAPABILITY_FILE)
    prc_data = load_json(PRICING_FILE)

    cap_vendors = {v["vendor"]: v for v in cap_data["vendors"]}
    prc_vendors = prc_data["vendors"]

    print(f"Capability vendors: {len(cap_vendors)}, Pricing vendors: {len(prc_vendors)}")

    # Compute benchmarks from pricing data
    benchmarks = compute_benchmarks(prc_vendors)
    print(f"Benchmarks computed: overall avg={benchmarks['overall']['market_avg']}, "
          f"top10={benchmarks['overall']['top10_avg']}")

    # Process each vendor
    enriched_vendors = []
    ai_scores = []

    for pv in prc_vendors:
        name = pv["vendor"]
        cv = cap_vendors.get(name)
        if not cv:
            print(f"  WARNING: No capability data for {name}")
            continue

        # Compute AI pricing influence
        ai_score = compute_ai_pricing_influence(cv, pv)
        ai_label = classify_ai_influence(ai_score)
        ai_narrative = generate_ai_narrative(name, ai_score, ai_label, cv, pv)
        ai_scores.append(ai_score)

        # Strengths & weaknesses
        strengths, weaknesses = classify_strengths_weaknesses(pv, benchmarks)

        # Roadmap
        roadmap = generate_roadmap(pv, benchmarks)

        # Recommendations
        recommendations = generate_recommendations(name, strengths, weaknesses, roadmap, ai_score, pv)

        # Merge all fields from pricing vendor + new enrichment
        enriched = dict(pv)  # Copy all original fields
        enriched["ai_pricing_influence"] = ai_score
        enriched["ai_pricing_influence_label"] = ai_label
        enriched["ai_pricing_narrative"] = ai_narrative
        enriched["ai_capability_scores"] = {
            "AIO": cv.get("pillar_scores", {}).get("AIO", 0),
            "AID": cv.get("pillar_scores", {}).get("AID", 0),
            "AIO_sub": {
                k: cv.get("sub_pillar_scores_current", {}).get(k, 0)
                for k in ["AIO-01", "AIO-02", "AIO-03", "AIO-04"]
            },
            "AID_sub": {
                k: cv.get("sub_pillar_scores_current", {}).get(k, 0)
                for k in ["AID-01", "AID-02", "AID-03", "AID-04"]
            },
            "is_ai_first": cv.get("is_ai_first", False),
        }
        enriched["pricing_strengths"] = strengths
        enriched["pricing_weaknesses"] = weaknesses
        enriched["pricing_roadmap"] = roadmap
        enriched["pricing_recommendations"] = recommendations

        enriched_vendors.append(enriched)

    # Sort by AI pricing influence descending
    enriched_vendors.sort(key=lambda x: x["ai_pricing_influence"], reverse=True)

    # Compute AI influence benchmarks
    ai_mean = round(statistics.mean(ai_scores), 2)
    ai_median = round(statistics.median(ai_scores), 1)
    ai_min = round(min(ai_scores), 2)
    ai_max = round(max(ai_scores), 2)

    # AI influence by model type
    model_type_ai = {}
    for v in enriched_vendors:
        mt = v.get("pricing_model_type", "Unknown")
        if mt not in model_type_ai:
            model_type_ai[mt] = []
        model_type_ai[mt].append(v["ai_pricing_influence"])
    model_type_ai_avgs = {
        k: round(statistics.mean(v), 2) for k, v in model_type_ai.items()
    }

    # AI influence by service type
    svc_type_ai = {}
    for v in enriched_vendors:
        st = v.get("mdr_service_type", "Unknown")
        if st not in svc_type_ai:
            svc_type_ai[st] = []
        svc_type_ai[st].append(v["ai_pricing_influence"])
    svc_type_ai_avgs = {
        k: round(statistics.mean(v), 2) for k, v in svc_type_ai.items()
    }

    # Count by AI influence label
    ai_label_counts = {}
    for v in enriched_vendors:
        lbl = v["ai_pricing_influence_label"]
        ai_label_counts[lbl] = ai_label_counts.get(lbl, 0) + 1

    # Build output
    output = {
        "schema_ref": "MDR_Services_Schema.json",
        "schema_version": "2.1",
        "data_type": "pricing_ai_enriched",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pipeline": "build_mdr_pricing_v2_1.py",
        "source_files": {
            "capability": CAPABILITY_FILE,
            "pricing": PRICING_FILE,
        },
        "vendor_count": len(enriched_vendors),
        "dimensions": DIMENSIONS,
        "dimension_labels": DIMENSION_LABELS,
        "ai_influence_weights": AI_WEIGHTS,
        "ai_influence_stats": {
            "mean": ai_mean,
            "median": ai_median,
            "min": ai_min,
            "max": ai_max,
            "by_label": ai_label_counts,
            "by_model_type": model_type_ai_avgs,
            "by_service_type": svc_type_ai_avgs,
        },
        "pricing_benchmarks": benchmarks,
        "summary": prc_data.get("summary", {}),
        "vendors": enriched_vendors,
    }

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Output written to {OUTPUT_FILE}")
    print(f"   Vendors enriched: {len(enriched_vendors)}")
    print(f"   AI Influence: mean={ai_mean}, median={ai_median}, range={ai_min}-{ai_max}")
    print(f"   Distribution: {ai_label_counts}")
    print(f"   By model type: {model_type_ai_avgs}")
    print(f"   By service type: {svc_type_ai_avgs}")


if __name__ == "__main__":
    main()
