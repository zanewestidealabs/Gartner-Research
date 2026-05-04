"""
Analyze PMR vendor data for analyst take report.
Categorize vendors into under-represented, aligned, and over-represented.
"""
import json
from collections import defaultdict

with open("Product Market Readiness Vendor 1-1 Enriched.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)

vendors = data.get("vendors", data) if isinstance(data, dict) else data

print(f"Total vendors: {len(vendors)}")
print()

# Categorize by overall credibility gap
under = []   # gap < -0.3 (proof > GTM, under-claiming)
aligned = [] # -0.3 <= gap <= 0.3
over = []    # gap > 0.3 (GTM > proof, over-claiming)

for v in vendors:
    name = v.get("vendor") or v.get("vendor_name", "Unknown")
    gap = v.get("overall_credibility_gap")
    gtm = v.get("overall_gtm_score")
    proof = v.get("overall_proof_score")
    grade = v.get("coverage_grade", "")
    
    if gap is None:
        continue
    
    gap = float(gap)
    rec = {
        "name": name,
        "gap": gap,
        "gtm": float(gtm) if gtm else 0,
        "proof": float(proof) if proof else 0,
        "grade": grade,
        "pillar_gaps": v.get("pillar_gaps", {}),
        "pillar_gtm": v.get("pillar_gtm_scores", {}),
        "pillar_proof": v.get("pillar_proof_scores", {}),
        "sub_pillar_scores": v.get("sub_pillar_scores", {}),
        "vendor_type": v.get("vendor_type", ""),
        "region": v.get("region", ""),
        "is_startup": v.get("is_startup", False),
        "description": v.get("description", "")[:100],
    }
    
    if gap < -0.3:
        under.append(rec)
    elif gap > 0.3:
        over.append(rec)
    else:
        aligned.append(rec)

# Sort each category
under.sort(key=lambda x: x["gap"])
aligned.sort(key=lambda x: abs(x["gap"]))
over.sort(key=lambda x: x["gap"], reverse=True)

print(f"=== UNDER-REPRESENTED (proof > GTM, gap < -0.3): {len(under)} vendors ===")
for v in under[:15]:
    print(f"  {v['name']:40s} gap={v['gap']:+.2f}  GTM={v['gtm']:.2f}  Proof={v['proof']:.2f}  grade={v['grade']}")

print(f"\n=== ALIGNED (-0.3 <= gap <= 0.3): {len(aligned)} vendors ===")
for v in aligned[:15]:
    print(f"  {v['name']:40s} gap={v['gap']:+.2f}  GTM={v['gtm']:.2f}  Proof={v['proof']:.2f}  grade={v['grade']}")

print(f"\n=== OVER-REPRESENTED (GTM > proof, gap > 0.3): {len(over)} vendors ===")
for v in over[:15]:
    print(f"  {v['name']:40s} gap={v['gap']:+.2f}  GTM={v['gtm']:.2f}  Proof={v['proof']:.2f}  grade={v['grade']}")

# Summary stats
print(f"\n=== SUMMARY ===")
print(f"Under-represented: {len(under)} ({len(under)/len(vendors)*100:.1f}%)")
print(f"Aligned:           {len(aligned)} ({len(aligned)/len(vendors)*100:.1f}%)")
print(f"Over-represented:  {len(over)} ({len(over)/len(vendors)*100:.1f}%)")

# Average gaps
import statistics
if under:
    print(f"\nUnder-rep avg gap: {statistics.mean([v['gap'] for v in under]):.2f}")
if aligned:
    print(f"Aligned avg gap:   {statistics.mean([v['gap'] for v in aligned]):.2f}")
if over:
    print(f"Over-rep avg gap:  {statistics.mean([v['gap'] for v in over]):.2f}")

# Overall market stats
all_gaps = [v["gap"] for v in under + aligned + over]
print(f"\nMarket avg gap:    {statistics.mean(all_gaps):.2f}")
print(f"Market median gap: {statistics.median(all_gaps):.2f}")
print(f"Market stdev gap:  {statistics.stdev(all_gaps):.2f}")

# Evidence stats per category
def evidence_stats(group, label):
    total_excerpts = 0
    total_urls = 0
    vendors_with_evidence = 0
    for v in group:
        sps = v["sub_pillar_scores"]
        has_ev = False
        for sid, sp in sps.items():
            if isinstance(sp, dict):
                excerpts = sp.get("excerpts", [])
                urls = sp.get("source_urls", [])
                total_excerpts += len(excerpts) if isinstance(excerpts, list) else 0
                total_urls += len(urls) if isinstance(urls, list) else 0
                if excerpts or urls:
                    has_ev = True
        if has_ev:
            vendors_with_evidence += 1
    print(f"\n{label}:")
    print(f"  Vendors with evidence: {vendors_with_evidence}/{len(group)}")
    print(f"  Total excerpts: {total_excerpts}")
    print(f"  Total source URLs: {total_urls}")
    if group:
        print(f"  Avg excerpts/vendor: {total_excerpts/len(group):.1f}")

evidence_stats(under, "Under-represented evidence")
evidence_stats(aligned, "Aligned evidence")
evidence_stats(over, "Over-represented evidence")

# Pillar-level analysis
print("\n=== PILLAR GAP ANALYSIS ===")
pillar_gaps_all = defaultdict(list)
for v in under + aligned + over:
    for p, g in v["pillar_gaps"].items():
        if g is not None:
            pillar_gaps_all[p].append(float(g))

for p in sorted(pillar_gaps_all.keys()):
    gaps = pillar_gaps_all[p]
    print(f"  {p}: avg={statistics.mean(gaps):.2f}  median={statistics.median(gaps):.2f}  min={min(gaps):.2f}  max={max(gaps):.2f}")

# Deep dive: what are the most over-claimed sub-pillars?
print("\n=== TOP 10 MOST OVER-CLAIMED SUB-PILLARS (avg gap) ===")
sp_gaps = defaultdict(list)
for v in under + aligned + over:
    for sid, sp in v["sub_pillar_scores"].items():
        if isinstance(sp, dict) and sp.get("credibility_gap") is not None:
            sp_gaps[sid].append(float(sp["credibility_gap"]))

sp_avgs = [(sid, statistics.mean(gaps), len(gaps)) for sid, gaps in sp_gaps.items()]
sp_avgs.sort(key=lambda x: x[1], reverse=True)
for sid, avg, n in sp_avgs[:10]:
    print(f"  {sid}: avg_gap={avg:.2f} (n={n})")

print("\n=== TOP 10 MOST UNDER-CLAIMED SUB-PILLARS (avg gap) ===")
for sid, avg, n in sp_avgs[-10:]:
    print(f"  {sid}: avg_gap={avg:.2f} (n={n})")

# Startup vs established breakdown
startups_over = [v for v in over if v.get("is_startup")]
established_over = [v for v in over if not v.get("is_startup")]
print(f"\n=== STARTUP vs ESTABLISHED in Over-represented ===")
print(f"  Startups over-claiming: {len(startups_over)}")
print(f"  Established over-claiming: {len(established_over)}")

# Region breakdown
from collections import Counter
print(f"\n=== REGION BREAKDOWN ===")
for label, group in [("Under", under), ("Aligned", aligned), ("Over", over)]:
    regions = Counter(v.get("region", "Unknown") for v in group)
    print(f"  {label}: {dict(regions)}")
