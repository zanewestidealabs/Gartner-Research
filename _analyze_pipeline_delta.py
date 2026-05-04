"""
Compare vendor scores across pipeline stages: before evidence vs after evidence.
This reveals the REAL credibility gap — how much scores change when actual 
research, rationales, and excerpts are gathered.
"""
import json
from collections import defaultdict
import statistics

def load_vendors(filepath):
    """Load vendor dict keyed by vendor name."""
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
    vendors = data.get("vendors", [])
    return {v["vendor"]: v for v in vendors}

def get_pillar_scores(vendor):
    return vendor.get("pillar_scores", {})

def get_sub_scores(vendor):
    return vendor.get("sub_pillar_scores_current", {})

def has_evidence(vendor):
    """Check if vendor has populated evidence."""
    ev = vendor.get("sub_pillar_evidence", {})
    if not ev:
        return False
    for k, v in ev.items():
        if isinstance(v, dict):
            if v.get("source_urls") or v.get("excerpts") or v.get("rationale") or v.get("sources"):
                return True
    return False

# Define comparison pairs: (label, before_file, after_file)
COMPARISONS = [
    ("MDR Services (Seed → Consolidated)", 
     "MDR Services Vendor 1-0 Seed.json",
     "MDR Services Vendor 2-1 Consolidated.json"),
    ("AI TRiSM (Validated → Consolidated)",
     "AI TRiSM Vendor 1-1 Validated.json",
     "AI TRiSM Vendor 2-1 Consolidated.json"),
    ("Preemptive Cyber (Validated → Consolidated)",
     "Preemptive Cybersecurity Vendor 1-1 Validated.json",
     "Preemptive Cybersecurity Vendor 2-1 Consolidated.json"),
    ("Offensive Security (Researched → Consolidated)",
     "Offensive Security Vendor 2-0 Researched.json",
     "Offensive Security Vendor 2-1 Consolidated.json"),
]

all_pillar_deltas = []
all_sub_deltas = []
all_vendor_avg_deltas = []
schema_results = {}

for label, before_file, after_file in COMPARISONS:
    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"{'='*70}")
    
    before = load_vendors(before_file)
    after = load_vendors(after_file)
    
    # Find overlapping vendors with non-zero scores in both
    common = set(before.keys()) & set(after.keys())
    scored_common = []
    for name in common:
        b_scores = get_pillar_scores(before[name])
        a_scores = get_pillar_scores(after[name])
        # Need non-zero scores in BOTH stages
        if any(v > 0 for v in b_scores.values()) and any(v > 0 for v in a_scores.values()):
            scored_common.append(name)
    
    print(f"Before vendors: {len(before)}, After vendors: {len(after)}")
    print(f"Common vendors: {len(common)}, With scores in both: {len(scored_common)}")
    
    if not scored_common:
        print("  ** No vendors with scores in both stages — skipping **")
        continue
    
    # Evidence check
    before_with_ev = sum(1 for n in scored_common if has_evidence(before[n]))
    after_with_ev = sum(1 for n in scored_common if has_evidence(after[n]))
    print(f"With evidence — Before: {before_with_ev}/{len(scored_common)}, After: {after_with_ev}/{len(scored_common)}")
    
    # Compute pillar-level deltas
    pillar_deltas = defaultdict(list)
    vendor_deltas = []
    sub_pillar_deltas = defaultdict(list)
    
    for name in sorted(scored_common):
        b_pillars = get_pillar_scores(before[name])
        a_pillars = get_pillar_scores(after[name])
        b_subs = get_sub_scores(before[name])
        a_subs = get_sub_scores(after[name])
        
        # Pillar deltas (after - before): negative = score went DOWN after research
        vendor_pillar_deltas = []
        for p in b_pillars:
            if p in a_pillars and b_pillars[p] > 0 and a_pillars[p] > 0:
                delta = a_pillars[p] - b_pillars[p]
                pillar_deltas[p].append(delta)
                vendor_pillar_deltas.append(delta)
                all_pillar_deltas.append(delta)
        
        # Sub-pillar deltas
        for sp in b_subs:
            if sp in a_subs and b_subs[sp] > 0 and a_subs[sp] > 0:
                delta = a_subs[sp] - b_subs[sp]
                sub_pillar_deltas[sp].append(delta)
                all_sub_deltas.append(delta)
        
        if vendor_pillar_deltas:
            avg_delta = sum(vendor_pillar_deltas) / len(vendor_pillar_deltas)
            vendor_deltas.append((name, avg_delta, b_pillars, a_pillars))
            all_vendor_avg_deltas.append(avg_delta)
    
    # Summary stats
    went_down = [v for v in vendor_deltas if v[1] < -0.05]
    went_up = [v for v in vendor_deltas if v[1] > 0.05]
    stayed = [v for v in vendor_deltas if -0.05 <= v[1] <= 0.05]
    
    avg_deltas = [v[1] for v in vendor_deltas]
    print(f"\n  VENDOR-LEVEL RESULTS (n={len(vendor_deltas)}):")
    print(f"  Scores went DOWN after research:  {len(went_down)} ({len(went_down)/len(vendor_deltas)*100:.1f}%)")
    print(f"  Scores went UP after research:    {len(went_up)} ({len(went_up)/len(vendor_deltas)*100:.1f}%)")
    print(f"  Scores stayed similar (±0.05):    {len(stayed)} ({len(stayed)/len(vendor_deltas)*100:.1f}%)")
    print(f"  Average delta: {statistics.mean(avg_deltas):.3f}")
    print(f"  Median delta:  {statistics.median(avg_deltas):.3f}")
    if avg_deltas:
        print(f"  Std dev:       {statistics.stdev(avg_deltas):.3f}" if len(avg_deltas) > 1 else "")
    
    # Pillar breakdown
    print(f"\n  PILLAR-LEVEL DELTAS:")
    for p in sorted(pillar_deltas.keys()):
        vals = pillar_deltas[p]
        avg = statistics.mean(vals)
        down = sum(1 for v in vals if v < -0.05)
        print(f"    {p}: avg delta={avg:+.3f}, went down={down}/{len(vals)} ({down/len(vals)*100:.0f}%)")
    
    # Top score drops
    vendor_deltas.sort(key=lambda x: x[1])
    print(f"\n  TOP 5 LARGEST SCORE DROPS:")
    for name, delta, b, a in vendor_deltas[:5]:
        b_avg = sum(b.values())/len(b)
        a_avg = sum(a.values())/len(a)
        print(f"    {name}: {b_avg:.2f} → {a_avg:.2f} (delta={delta:+.3f})")
    
    print(f"\n  TOP 5 LARGEST SCORE INCREASES:")
    for name, delta, b, a in vendor_deltas[-5:][::-1]:
        b_avg = sum(b.values())/len(b)
        a_avg = sum(a.values())/len(a)
        print(f"    {name}: {b_avg:.2f} → {a_avg:.2f} (delta={delta:+.3f})")
    
    schema_results[label] = {
        "total": len(vendor_deltas),
        "went_down": len(went_down),
        "went_up": len(went_up),
        "stayed": len(stayed),
        "avg_delta": statistics.mean(avg_deltas),
        "down_pct": len(went_down)/len(vendor_deltas)*100,
    }

# ============================================================
# AGGREGATE CROSS-SCHEMA SUMMARY
# ============================================================
print(f"\n{'='*70}")
print(f"  CROSS-SCHEMA AGGREGATE SUMMARY")
print(f"{'='*70}")

if all_vendor_avg_deltas:
    total = len(all_vendor_avg_deltas)
    down = sum(1 for d in all_vendor_avg_deltas if d < -0.05)
    up = sum(1 for d in all_vendor_avg_deltas if d > 0.05)
    flat = total - down - up
    
    print(f"\nTotal vendors compared: {total}")
    print(f"Scores DECREASED after research: {down} ({down/total*100:.1f}%)")
    print(f"Scores INCREASED after research: {up} ({up/total*100:.1f}%)")
    print(f"Scores STABLE (±0.05):           {flat} ({flat/total*100:.1f}%)")
    print(f"\nMean delta:   {statistics.mean(all_vendor_avg_deltas):+.3f}")
    print(f"Median delta: {statistics.median(all_vendor_avg_deltas):+.3f}")
    
    # Distribution of delta magnitudes
    big_drop = sum(1 for d in all_vendor_avg_deltas if d < -0.5)
    mod_drop = sum(1 for d in all_vendor_avg_deltas if -0.5 <= d < -0.1)
    small_drop = sum(1 for d in all_vendor_avg_deltas if -0.1 <= d < -0.05)
    small_rise = sum(1 for d in all_vendor_avg_deltas if 0.05 < d <= 0.1)
    mod_rise = sum(1 for d in all_vendor_avg_deltas if 0.1 < d <= 0.5)
    big_rise = sum(1 for d in all_vendor_avg_deltas if d > 0.5)
    
    print(f"\n  DELTA MAGNITUDE DISTRIBUTION:")
    print(f"    Large drop (< -0.5):   {big_drop} ({big_drop/total*100:.1f}%)")
    print(f"    Moderate drop (-0.5 to -0.1): {mod_drop} ({mod_drop/total*100:.1f}%)")
    print(f"    Small drop (-0.1 to -0.05):   {small_drop} ({small_drop/total*100:.1f}%)")
    print(f"    Stable (±0.05):               {flat} ({flat/total*100:.1f}%)")
    print(f"    Small rise (+0.05 to +0.1):   {small_rise} ({small_rise/total*100:.1f}%)")
    print(f"    Moderate rise (+0.1 to +0.5): {mod_rise} ({mod_rise/total*100:.1f}%)")
    print(f"    Large rise (> +0.5):          {big_rise} ({big_rise/total*100:.1f}%)")

if all_sub_deltas:
    print(f"\n  SUB-PILLAR LEVEL:")
    print(f"    Total sub-pillar comparisons: {len(all_sub_deltas)}")
    sub_down = sum(1 for d in all_sub_deltas if d < 0)
    sub_up = sum(1 for d in all_sub_deltas if d > 0)
    sub_same = len(all_sub_deltas) - sub_down - sub_up
    print(f"    Went DOWN: {sub_down} ({sub_down/len(all_sub_deltas)*100:.1f}%)")
    print(f"    Went UP:   {sub_up} ({sub_up/len(all_sub_deltas)*100:.1f}%)")
    print(f"    No change: {sub_same} ({sub_same/len(all_sub_deltas)*100:.1f}%)")
    print(f"    Mean sub-pillar delta: {statistics.mean(all_sub_deltas):+.3f}")

# Per-schema summary table
print(f"\n  PER-SCHEMA SUMMARY:")
print(f"  {'Schema':<50} {'n':>4} {'Down%':>6} {'Up%':>6} {'AvgΔ':>7}")
print(f"  {'-'*73}")
for label, r in schema_results.items():
    up_pct = r['went_up']/r['total']*100
    print(f"  {label:<50} {r['total']:>4} {r['down_pct']:>5.1f}% {up_pct:>5.1f}% {r['avg_delta']:>+.3f}")
