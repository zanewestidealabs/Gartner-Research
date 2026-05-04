"""Analyze PMR startup vendors for product team analyst take v2."""
import json
from collections import Counter, defaultdict

with open("Product Market Readiness Vendor 1-1 Enriched.json", "r", encoding="utf-8") as f:
    data = json.load(f)
vendors = data.get("vendors", data) if isinstance(data, dict) else data

# Filter startups
startups = [v for v in vendors if v.get("is_startup") is True]
established = [v for v in vendors if v.get("is_startup") is not True]

print(f"Total vendors: {len(vendors)}")
print(f"Startups: {len(startups)}")
print(f"Established: {len(established)}")

# ── Pillar definitions ──
PILLARS = {
    "PPD": "Product Positioning & Differentiation",
    "PCS": "Proof Points & Case Studies",
    "TDT": "Technical Depth & Transparency",
    "PCM": "Pricing & Commercial Model Clarity",
    "CTL": "Content & Thought Leadership",
}

SUB_PILLARS = {
    "PPD": ["ppd_capability_claim_specificity", "ppd_competitive_differentiation_clarity",
             "ppd_target_persona_use_case_alignment", "ppd_market_category_ownership",
             "ppd_messaging_consistency_coherence"],
    "PCS": ["pcs_customer_case_study_depth", "pcs_third_party_validation_analyst_recognition",
             "pcs_deployment_scale_metric_transparency", "pcs_roi_business_outcome_documentation",
             "pcs_customer_reference_breadth"],
    "TDT": ["tdt_architecture_design_documentation", "tdt_api_integration_ecosystem",
             "tdt_detection_methodology_transparency", "tdt_data_handling_privacy_transparency",
             "tdt_technical_enablement_documentation_quality"],
    "PCM": ["pcm_pricing_model_transparency", "pcm_packaging_tier_clarity",
             "pcm_total_cost_ownership_articulation", "pcm_trial_evaluation_accessibility",
             "pcm_commercial_terms_contract_flexibility"],
    "CTL": ["ctl_original_research_data_publication", "ctl_conference_speaking_presence",
             "ctl_blog_educational_content_quality", "ctl_open_source_community_contribution",
             "ctl_market_education_category_development"],
}

# ── AI-focused detection using is_ai_first field ──
ai_startups = [v for v in startups if v.get("is_ai_first") is True]
non_ai_startups = [v for v in startups if v.get("is_ai_first") is not True]
ai_established = [v for v in established if v.get("is_ai_first") is True]
print(f"\nAI-first startups: {len(ai_startups)}")
print(f"Non-AI-first startups: {len(non_ai_startups)}")
print(f"AI-first established: {len(ai_established)}")

# ── Vendor types ──
print("\n=== STARTUP VENDOR TYPES ===")
vtype_counter = Counter()
for v in startups:
    vtype_counter[v.get('vendor_type', 'Unknown')] += 1
for vt, cnt in vtype_counter.most_common():
    print(f"  {vt}: {cnt}")

# ── Product names as proxy for verticals ──
print("\n=== STARTUP PRODUCT NAMES (sample) ===")
for v in startups[:20]:
    print(f"  {v.get('vendor','?')}: {v.get('product_names','?')} | type={v.get('vendor_type','?')} | ai_first={v.get('is_ai_first',False)}")

print("\n=== AI-FIRST STARTUP NAMES (all) ===")
for v in ai_startups:
    print(f"  {v.get('vendor','?')}: type={v.get('vendor_type','?')} | region={v.get('region','?')}")

# ── Regional distribution ──
print("\n=== STARTUP HQ REGIONS ===")
region_counter = Counter()
for v in startups:
    region_counter[v.get("hq_region", "Unknown")] += 1
for r, cnt in region_counter.most_common():
    print(f"  {r}: {cnt}")

# ── Coverage grades ──
print("\n=== STARTUP COVERAGE GRADES ===")
grade_counter = Counter()
for v in startups:
    grade_counter[v.get("coverage_grade", "?")] += 1
for g in sorted(grade_counter.keys()):
    print(f"  {g}: {grade_counter[g]}")

# ── Pillar-level gap analysis for startups ──
print("\n=== STARTUP PILLAR GAPS (avg GTM - Proof per pillar) ===")
for pcode, pname in PILLARS.items():
    gtm_vals = []
    proof_vals = []
    gap_vals = []
    for v in startups:
        pg = v.get("pillar_gtm_scores", {}).get(pcode)
        pp = v.get("pillar_proof_scores", {}).get(pcode)
        pgap = v.get("pillar_gaps", {}).get(pcode)
        if pg is not None:
            gtm_vals.append(pg)
        if pp is not None:
            proof_vals.append(pp)
        if pgap is not None:
            gap_vals.append(pgap)
    avg_gtm = sum(gtm_vals) / len(gtm_vals) if gtm_vals else 0
    avg_proof = sum(proof_vals) / len(proof_vals) if proof_vals else 0
    avg_gap = sum(gap_vals) / len(gap_vals) if gap_vals else 0
    print(f"  {pcode} ({pname}):")
    print(f"    Avg GTM: {avg_gtm:.2f}, Avg Proof: {avg_proof:.2f}, Avg Gap: {avg_gap:.2f}")

# ── Sub-pillar gap analysis for startups ──
print("\n=== STARTUP SUB-PILLAR GAPS (top 10 widest) ===")
sp_gaps = {}
for pcode, sps in SUB_PILLARS.items():
    for sp in sps:
        gaps = []
        for v in startups:
            scores = v.get("sub_pillar_scores", {}).get(sp, {})
            g = scores.get("credibility_gap")
            if g is not None:
                gaps.append(g)
        if gaps:
            sp_gaps[sp] = sum(gaps) / len(gaps)

sorted_gaps = sorted(sp_gaps.items(), key=lambda x: x[1], reverse=True)
for sp, gap in sorted_gaps[:10]:
    print(f"  {sp}: avg gap {gap:.3f}")

print("\n=== STARTUP SUB-PILLAR GAPS (bottom 5 - most under-marketed) ===")
for sp, gap in sorted_gaps[-5:]:
    print(f"  {sp}: avg gap {gap:.3f}")

# ── Compare AI startups vs non-AI startups pillar gaps ──
print("\n=== AI STARTUPS vs NON-AI STARTUPS PILLAR GAPS ===")
for pcode, pname in PILLARS.items():
    ai_gaps = [v.get("pillar_gaps", {}).get(pcode, 0) for v in ai_startups if v.get("pillar_gaps", {}).get(pcode) is not None]
    nonai_gaps = [v.get("pillar_gaps", {}).get(pcode, 0) for v in non_ai_startups if v.get("pillar_gaps", {}).get(pcode) is not None]
    ai_avg = sum(ai_gaps) / len(ai_gaps) if ai_gaps else 0
    nonai_avg = sum(nonai_gaps) / len(nonai_gaps) if nonai_gaps else 0
    print(f"  {pcode}: AI={ai_avg:.3f}  Non-AI={nonai_avg:.3f}  Delta={ai_avg - nonai_avg:.3f}")

# ── Overall credibility gap distribution for startups ──
print("\n=== STARTUP OVERALL CREDIBILITY GAP DISTRIBUTION ===")
gaps = [v.get("overall_credibility_gap", 0) for v in startups if v.get("overall_credibility_gap") is not None]
neg = [g for g in gaps if g < -0.1]
aligned = [g for g in gaps if -0.1 <= g <= 0.1]
mild = [g for g in gaps if 0.1 < g <= 0.5]
high = [g for g in gaps if g > 0.5]
print(f"  Under-represented (< -0.1): {len(neg)} ({100*len(neg)/len(gaps):.1f}%)")
print(f"  Aligned (-0.1 to 0.1): {len(aligned)} ({100*len(aligned)/len(gaps):.1f}%)")
print(f"  Mild over-rep (0.1 to 0.5): {len(mild)} ({100*len(mild)/len(gaps):.1f}%)")
print(f"  High over-rep (> 0.5): {len(high)} ({100*len(high)/len(gaps):.1f}%)")
print(f"  Mean gap: {sum(gaps)/len(gaps):.3f}")
print(f"  Median gap: {sorted(gaps)[len(gaps)//2]:.3f}")

# ── Where AI startups struggle most: sub-pillar detail ──
print("\n=== AI STARTUP SUB-PILLAR GAPS (top 10 widest) ===")
ai_sp_gaps = {}
for pcode, sps in SUB_PILLARS.items():
    for sp in sps:
        gaps_list = []
        for v in ai_startups:
            scores = v.get("sub_pillar_scores", {}).get(sp, {})
            g = scores.get("credibility_gap")
            if g is not None:
                gaps_list.append(g)
        if gaps_list:
            ai_sp_gaps[sp] = sum(gaps_list) / len(gaps_list)

sorted_ai = sorted(ai_sp_gaps.items(), key=lambda x: x[1], reverse=True)
for sp, gap in sorted_ai[:10]:
    print(f"  {sp}: avg gap {gap:.3f}")

# ── Proof weaknesses: which sub-pillars have lowest proof scores for startups ──
print("\n=== STARTUP WEAKEST PROOF SCORES (lowest avg) ===")
sp_proof = {}
for pcode, sps in SUB_PILLARS.items():
    for sp in sps:
        proofs = []
        for v in startups:
            scores = v.get("sub_pillar_scores", {}).get(sp, {})
            p = scores.get("proof_of_execution_score")
            if p is not None:
                proofs.append(p)
        if proofs:
            sp_proof[sp] = sum(proofs) / len(proofs)

sorted_proof = sorted(sp_proof.items(), key=lambda x: x[1])
for sp, avg in sorted_proof[:10]:
    print(f"  {sp}: avg proof {avg:.2f}")

# ── GTM strongest: where startups message most ──
print("\n=== STARTUP STRONGEST GTM MESSAGING (highest avg) ===")
sp_gtm = {}
for pcode, sps in SUB_PILLARS.items():
    for sp in sps:
        gtms = []
        for v in startups:
            scores = v.get("sub_pillar_scores", {}).get(sp, {})
            g = scores.get("gtm_messaging_score")
            if g is not None:
                gtms.append(g)
        if gtms:
            sp_gtm[sp] = sum(gtms) / len(gtms)

sorted_gtm = sorted(sp_gtm.items(), key=lambda x: x[1], reverse=True)
for sp, avg in sorted_gtm[:10]:
    print(f"  {sp}: avg gtm {avg:.2f}")

# ── Key excerpts patterns (what kind of evidence is missing) ──
print("\n=== STARTUP AVG EXCERPTS PER VENDOR ===")
total_excerpts = sum(
    len(scores.get("excerpts", []))
    for v in startups
    for scores in v.get("sub_pillar_scores", {}).values()
)
print(f"  Total excerpts across startups: {total_excerpts}")
print(f"  Avg per startup: {total_excerpts / len(startups):.1f}")

ai_excerpts = sum(
    len(scores.get("excerpts", []))
    for v in ai_startups
    for scores in v.get("sub_pillar_scores", {}).values()
)
print(f"  AI startup avg excerpts: {ai_excerpts / len(ai_startups):.1f}" if ai_startups else "  No AI startups")

# ── Vendor type analysis for all vendors ──
print("\n=== ALL VENDOR TYPES ===")
all_vtype = Counter()
for v in vendors:
    all_vtype[v.get('vendor_type', 'Unknown')] += 1
for vt, cnt in all_vtype.most_common():
    print(f"  {vt}: {cnt}")

# ── Established vs startup comparison ──
print("\n=== ESTABLISHED PILLAR GAPS (for comparison) ===")
for pcode, pname in PILLARS.items():
    gap_vals = [v.get('pillar_gaps', {}).get(pcode) for v in established if v.get('pillar_gaps', {}).get(pcode) is not None]
    avg_gap = sum(gap_vals) / len(gap_vals) if gap_vals else 0
    print(f"  {pcode}: avg gap {avg_gap:.3f}")

print("\nDone.")
