"""Analyze PMR credibility gap data for market insight report."""
import json
from collections import defaultdict

with open("Product Market Readiness Vendor 1-0 Seed.json") as f:
    data = json.load(f)

vendors = data["vendors"]
scored = [v for v in vendors if v.get("pillar_gtm_scores") and any(
    s > 0 for s in v["pillar_gtm_scores"].values()
)]

print(f"Total vendors: {len(vendors)}")
print(f"Scored vendors: {len(scored)}")

# Overall gap distribution
gaps = []
for v in scored:
    gtm = v.get("pillar_gtm_scores", {})
    proof = v.get("pillar_proof_scores", {})
    if gtm and proof:
        avg_gtm = sum(gtm.values()) / len(gtm) if gtm else 0
        avg_proof = sum(proof.values()) / len(proof) if proof else 0
        avg_gap = avg_gtm - avg_proof
        gaps.append({"name": v["vendor"], "gap": round(avg_gap, 2),
                      "gtm": round(avg_gtm, 2), "proof": round(avg_proof, 2)})

# Sort by gap descending
gaps.sort(key=lambda x: x["gap"], reverse=True)

# Distribution buckets (without using grade labels)
critical = [g for g in gaps if g["gap"] > 2.0]
significant = [g for g in gaps if 1.1 <= g["gap"] <= 2.0]
moderate = [g for g in gaps if 0.6 <= g["gap"] <= 1.0]
minor_over = [g for g in gaps if 0.1 <= g["gap"] <= 0.5]
aligned = [g for g in gaps if -0.1 <= g["gap"] <= 0.0]
under_market = [g for g in gaps if g["gap"] < -0.1]

total = len(gaps)
print(f"\n=== GAP DISTRIBUTION (n={total}) ===")
print(f"Overclaim >2.0:     {len(critical):3d} ({len(critical)/total*100:.1f}%)")
print(f"Overclaim 1.1-2.0:  {len(significant):3d} ({len(significant)/total*100:.1f}%)")
print(f"Overclaim 0.6-1.0:  {len(moderate):3d} ({len(moderate)/total*100:.1f}%)")
print(f"Overclaim 0.1-0.5:  {len(minor_over):3d} ({len(minor_over)/total*100:.1f}%)")
print(f"Aligned -0.1-0.0:   {len(aligned):3d} ({len(aligned)/total*100:.1f}%)")
print(f"Under-market <-0.1: {len(under_market):3d} ({len(under_market)/total*100:.1f}%)")

# Aggregate: over-claimers vs under-marketers
over_all = [g for g in gaps if g["gap"] > 0.0]
under_all = [g for g in gaps if g["gap"] < 0.0]
exact_zero = [g for g in gaps if g["gap"] == 0.0]
print(f"\nOver-claiming (gap>0): {len(over_all)} ({len(over_all)/total*100:.1f}%)")
print(f"Aligned (gap=0):       {len(exact_zero)} ({len(exact_zero)/total*100:.1f}%)")
print(f"Under-marketing (gap<0): {len(under_all)} ({len(under_all)/total*100:.1f}%)")

# Pillar-level analysis
pillar_gaps = defaultdict(list)
for v in scored:
    gtm = v.get("pillar_gtm_scores", {})
    proof = v.get("pillar_proof_scores", {})
    for p in gtm:
        if p in proof:
            pillar_gaps[p].append(gtm[p] - proof[p])

print(f"\n=== PILLAR-LEVEL GAPS ===")
for p in sorted(pillar_gaps.keys()):
    vals = pillar_gaps[p]
    avg = sum(vals) / len(vals)
    over = sum(1 for v in vals if v > 0.0)
    print(f"{p}: avg gap={avg:.2f}, over-claiming={over}/{len(vals)} ({over/len(vals)*100:.0f}%)")

# Sub-pillar analysis - find worst gaps
sub_gaps = defaultdict(list)
for v in scored:
    subs = v.get("sub_pillar_scores", {})
    for sp, score_obj in subs.items():
        if isinstance(score_obj, dict):
            gtm = score_obj.get("gtm_messaging_score", 0)
            proof = score_obj.get("proof_of_execution_score", 0)
            sub_gaps[sp].append(gtm - proof)

print(f"\n=== SUB-PILLAR GAPS (TOP 10 WORST) ===")
sub_avgs = {sp: sum(vals)/len(vals) for sp, vals in sub_gaps.items()}
for sp, avg in sorted(sub_avgs.items(), key=lambda x: x[1], reverse=True)[:10]:
    count = len(sub_gaps[sp])
    over = sum(1 for v in sub_gaps[sp] if v > 0)
    print(f"{sp}: avg gap={avg:.2f}, {over}/{count} over-claim ({over/count*100:.0f}%)")

print(f"\n=== SUB-PILLAR GAPS (MOST ALIGNED) ===")
for sp, avg in sorted(sub_avgs.items(), key=lambda x: abs(x[1]))[:5]:
    print(f"{sp}: avg gap={avg:.2f}")

# Average scores
all_gtm = [g["gtm"] for g in gaps]
all_proof = [g["proof"] for g in gaps]
print(f"\n=== AVERAGES ===")
print(f"Mean GTM messaging: {sum(all_gtm)/len(all_gtm):.2f}")
print(f"Mean proof of exec: {sum(all_proof)/len(all_proof):.2f}")
print(f"Mean gap:           {sum(g['gap'] for g in gaps)/len(gaps):.2f}")
print(f"Median gap:         {sorted(g['gap'] for g in gaps)[len(gaps)//2]:.2f}")

# Top over-claimers and top under-marketers
print(f"\n=== TOP 10 OVER-CLAIMERS ===")
for g in gaps[:10]:
    print(f"  {g['name']}: gap={g['gap']}, gtm={g['gtm']}, proof={g['proof']}")

print(f"\n=== TOP 10 UNDER-MARKETERS ===")
for g in gaps[-10:]:
    print(f"  {g['name']}: gap={g['gap']}, gtm={g['gtm']}, proof={g['proof']}")

# Percentage of vendors where proof > messaging in at least one pillar
mixed_signal = 0
for v in scored:
    gtm = v.get("pillar_gtm_scores", {})
    proof = v.get("pillar_proof_scores", {})
    has_over = any(gtm.get(p, 0) > proof.get(p, 0) for p in gtm)
    has_under = any(gtm.get(p, 0) < proof.get(p, 0) for p in gtm)
    if has_over and has_under:
        mixed_signal += 1

print(f"\nMixed-signal vendors (over in some pillars, under in others): {mixed_signal} ({mixed_signal/total*100:.1f}%)")

# Vendor type breakdown if available  
types = defaultdict(list)
for v in scored:
    vtype = v.get("vendor_type", "Unknown")
    gtm = v.get("pillar_gtm_scores", {})
    proof = v.get("pillar_proof_scores", {})
    avg_gap = sum(gtm.values())/len(gtm) - sum(proof.values())/len(proof)
    types[vtype].append(avg_gap)

print(f"\n=== GAP BY VENDOR TYPE ===")
for vt, vals in sorted(types.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True):
    avg = sum(vals)/len(vals)
    print(f"  {vt} (n={len(vals)}): avg gap={avg:.2f}")

# Schema source breakdown
schemas = defaultdict(list)
for v in scored:
    src = ', '.join(v.get("source_schemas", ["Unknown"]))
    gtm = v.get("pillar_gtm_scores", {})
    proof = v.get("pillar_proof_scores", {})
    avg_gap = sum(gtm.values())/len(gtm) - sum(proof.values())/len(proof)
    schemas[src].append(avg_gap)

print(f"\n=== GAP BY SOURCE SCHEMA ===")
for s, vals in sorted(schemas.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True):
    avg = sum(vals)/len(vals)
    over = sum(1 for v in vals if v > 0)
    print(f"  {s} (n={len(vals)}): avg gap={avg:.2f}, over-claiming={over}/{len(vals)}")
