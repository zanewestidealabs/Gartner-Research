"""
Analyze the relationship between evidence quality and scores.
Compare: vendors/sub-pillars WITH rich evidence vs those WITHOUT.
This reveals whether scores assigned without evidence validation are inflated.
"""
import json
from collections import defaultdict
import statistics

def load_vendors(filepath):
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
    return data.get("vendors", [])

SCHEMA_FILES = {
    "AI TRiSM": "AI TRiSM Vendor 2-1 Consolidated.json",
    "MDR Services": "MDR Services Vendor 2-1 Consolidated.json",
    "Preemptive Cyber": "Preemptive Cybersecurity Vendor 2-1 Consolidated.json",
    "Offensive Security": "Offensive Security Vendor 2-1 Consolidated.json",
}

def count_evidence(ev_obj):
    """Count evidence items for a sub-pillar evidence object."""
    if not isinstance(ev_obj, dict):
        return 0, 0, False
    urls = ev_obj.get("source_urls", [])
    excerpts = ev_obj.get("excerpts", [])
    rationale = ev_obj.get("rationale", "")
    sources = ev_obj.get("sources", [])
    
    url_count = len(urls) if isinstance(urls, list) else 0
    excerpt_count = len(excerpts) if isinstance(excerpts, list) else 0
    source_count = len(sources) if isinstance(sources, list) else 0
    has_rationale = bool(rationale and len(str(rationale)) > 10)
    
    total_evidence = url_count + excerpt_count + source_count
    return total_evidence, excerpt_count, has_rationale

all_with_evidence = []  # (score, evidence_count, excerpt_count) for sub-pillars with evidence
all_without_evidence = []  # scores for sub-pillars without evidence
all_vendor_results = []  # per-vendor results

for schema_name, filepath in SCHEMA_FILES.items():
    print(f"\n{'='*70}")
    print(f"  {schema_name}")
    print(f"{'='*70}")
    
    vendors = load_vendors(filepath)
    
    sp_with_ev_scores = []
    sp_without_ev_scores = []
    sp_rich_ev_scores = []  # many excerpts
    sp_thin_ev_scores = []  # few excerpts
    
    vendor_summaries = []
    
    for v in vendors:
        name = v.get("vendor", "?")
        subs = v.get("sub_pillar_scores_current", {})
        evidence = v.get("sub_pillar_evidence", {})
        pillars = v.get("pillar_scores", {})
        
        if not any(s > 0 for s in pillars.values()):
            continue
            
        vendor_ev_count = 0
        vendor_excerpt_count = 0
        vendor_sp_count = 0
        vendor_scores = []
        vendor_ev_scores = []
        vendor_no_ev_scores = []
        
        for sp_id, score in subs.items():
            if score == 0:
                continue
            vendor_sp_count += 1
            vendor_scores.append(score)
            
            ev_obj = evidence.get(sp_id, {})
            ev_count, exc_count, has_rat = count_evidence(ev_obj)
            vendor_ev_count += ev_count
            vendor_excerpt_count += exc_count
            
            if ev_count > 0 or has_rat:
                sp_with_ev_scores.append(score)
                vendor_ev_scores.append(score)
                all_with_evidence.append((score, ev_count, exc_count))
                if exc_count >= 3:
                    sp_rich_ev_scores.append(score)
                else:
                    sp_thin_ev_scores.append(score)
            else:
                sp_without_ev_scores.append(score)
                vendor_no_ev_scores.append(score)
                all_without_evidence.append(score)
        
        if vendor_scores:
            avg_score = statistics.mean(vendor_scores)
            vendor_summaries.append({
                "name": name,
                "avg_score": avg_score,
                "ev_count": vendor_ev_count,
                "excerpt_count": vendor_excerpt_count,
                "sp_count": vendor_sp_count,
                "avg_ev_score": statistics.mean(vendor_ev_scores) if vendor_ev_scores else None,
                "avg_no_ev_score": statistics.mean(vendor_no_ev_scores) if vendor_no_ev_scores else None,
            })
    
    # Schema-level analysis
    print(f"\n  Sub-pillars WITH evidence:    {len(sp_with_ev_scores)}, avg score = {statistics.mean(sp_with_ev_scores):.2f}" if sp_with_ev_scores else "  No sub-pillars with evidence")
    print(f"  Sub-pillars WITHOUT evidence: {len(sp_without_ev_scores)}, avg score = {statistics.mean(sp_without_ev_scores):.2f}" if sp_without_ev_scores else "  No sub-pillars without evidence")
    
    if sp_with_ev_scores and sp_without_ev_scores:
        delta = statistics.mean(sp_without_ev_scores) - statistics.mean(sp_with_ev_scores)
        print(f"  ** Gap (no-evidence scores - evidence scores): {delta:+.2f} **")
    
    if sp_rich_ev_scores and sp_thin_ev_scores:
        print(f"\n  Rich evidence (3+ excerpts): {len(sp_rich_ev_scores)}, avg = {statistics.mean(sp_rich_ev_scores):.2f}")
        print(f"  Thin evidence (<3 excerpts): {len(sp_thin_ev_scores)}, avg = {statistics.mean(sp_thin_ev_scores):.2f}")
        delta2 = statistics.mean(sp_thin_ev_scores) - statistics.mean(sp_rich_ev_scores)
        print(f"  ** Gap (thin - rich): {delta2:+.2f} **")
    
    # Vendor-level: group by evidence richness
    ev_rich_vendors = [v for v in vendor_summaries if v["excerpt_count"] >= 10]
    ev_poor_vendors = [v for v in vendor_summaries if v["excerpt_count"] < 3]
    ev_mid_vendors = [v for v in vendor_summaries if 3 <= v["excerpt_count"] < 10]
    
    print(f"\n  VENDOR-LEVEL (by evidence richness):")
    if ev_rich_vendors:
        avg = statistics.mean([v["avg_score"] for v in ev_rich_vendors])
        print(f"    Evidence-rich (10+ excerpts): {len(ev_rich_vendors)} vendors, avg score = {avg:.2f}")
    if ev_mid_vendors:
        avg = statistics.mean([v["avg_score"] for v in ev_mid_vendors])
        print(f"    Evidence-moderate (3-9 excerpts): {len(ev_mid_vendors)} vendors, avg score = {avg:.2f}")
    if ev_poor_vendors:
        avg = statistics.mean([v["avg_score"] for v in ev_poor_vendors])
        print(f"    Evidence-poor (<3 excerpts): {len(ev_poor_vendors)} vendors, avg score = {avg:.2f}")
    
    if ev_rich_vendors and ev_poor_vendors:
        rich_avg = statistics.mean([v["avg_score"] for v in ev_rich_vendors])
        poor_avg = statistics.mean([v["avg_score"] for v in ev_poor_vendors])
        print(f"    ** Vendor gap (poor - rich): {poor_avg - rich_avg:+.2f} **")
    
    all_vendor_results.extend(vendor_summaries)

# ============================================================
# CROSS-SCHEMA AGGREGATE
# ============================================================
print(f"\n{'='*70}")
print(f"  CROSS-SCHEMA AGGREGATE")
print(f"{'='*70}")

if all_with_evidence and all_without_evidence:
    ev_scores = [x[0] for x in all_with_evidence]
    print(f"\nSub-pillars WITH evidence: {len(ev_scores)}, mean = {statistics.mean(ev_scores):.2f}")
    print(f"Sub-pillars WITHOUT evidence: {len(all_without_evidence)}, mean = {statistics.mean(all_without_evidence):.2f}")
    gap = statistics.mean(all_without_evidence) - statistics.mean(ev_scores)
    print(f"** AGGREGATE GAP (no-evidence - with-evidence): {gap:+.2f} **")

# Rich vs poor excerpts
rich_ev = [x[0] for x in all_with_evidence if x[2] >= 3]
thin_ev = [x[0] for x in all_with_evidence if x[2] < 3]
if rich_ev and thin_ev:
    print(f"\nRich evidence (3+ excerpts): {len(rich_ev)}, mean = {statistics.mean(rich_ev):.2f}")
    print(f"Thin evidence (<3 excerpts): {len(thin_ev)}, mean = {statistics.mean(thin_ev):.2f}")
    print(f"** Gap (thin - rich): {statistics.mean(thin_ev) - statistics.mean(rich_ev):+.2f} **")

# Global vendor-level
ev_rich = [v for v in all_vendor_results if v["excerpt_count"] >= 10]
ev_poor = [v for v in all_vendor_results if v["excerpt_count"] < 3]
ev_mid = [v for v in all_vendor_results if 3 <= v["excerpt_count"] < 10]

print(f"\nVENDOR-LEVEL AGGREGATE:")
for label, group in [("Evidence-rich (10+ excerpts)", ev_rich), 
                      ("Evidence-moderate (3-9)", ev_mid),
                      ("Evidence-poor (<3)", ev_poor)]:
    if group:
        scores = [v["avg_score"] for v in group]
        print(f"  {label}: {len(group)} vendors, avg score = {statistics.mean(scores):.2f}, median = {statistics.median(scores):.2f}")

if ev_rich and ev_poor:
    rich_avg = statistics.mean([v["avg_score"] for v in ev_rich])
    poor_avg = statistics.mean([v["avg_score"] for v in ev_poor])
    print(f"\n** VENDOR-LEVEL GAP (poor evidence avg - rich evidence avg): {poor_avg - rich_avg:+.2f} **")
    print(f"   Evidence-rich avg: {rich_avg:.2f}")
    print(f"   Evidence-poor avg: {poor_avg:.2f}")
    print(f"   This means vendors WITHOUT evidence score {abs(poor_avg - rich_avg):.2f} points {'higher' if poor_avg > rich_avg else 'lower'} on average")

# Check: among vendors that HAVE both evidence-backed and non-evidence subs
print(f"\n  WITHIN-VENDOR ANALYSIS (vendors with both evidence-backed and non-evidence sub-pillars):")
mixed_vendors = [v for v in all_vendor_results if v["avg_ev_score"] is not None and v["avg_no_ev_score"] is not None]
if mixed_vendors:
    internal_gaps = []
    for v in mixed_vendors:
        gap = v["avg_no_ev_score"] - v["avg_ev_score"]
        internal_gaps.append(gap)
    
    above = sum(1 for g in internal_gaps if g > 0)
    below = sum(1 for g in internal_gaps if g < 0)
    equal = sum(1 for g in internal_gaps if g == 0)
    
    print(f"  Vendors with both: {len(mixed_vendors)}")
    print(f"  Non-evidence subs scored HIGHER: {above} ({above/len(mixed_vendors)*100:.1f}%)")
    print(f"  Non-evidence subs scored LOWER:  {below} ({below/len(mixed_vendors)*100:.1f}%)")
    print(f"  Equal: {equal}")
    print(f"  Mean internal gap: {statistics.mean(internal_gaps):+.2f}")
