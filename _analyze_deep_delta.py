"""
For Preemptive Cyber specifically, compare:
1. Seed scores (1-0, all zeros) 
2. Validated scores (1-1, initial scoring + light evidence)
3. Consolidated scores (2-1, deep research + full evidence)

Also look at MDR: seed scores (1-0, scored but NO evidence gathered)
vs consolidated (2-1, same scores but WITH evidence gathered).
The key question: do the MDR seed scores align with the evidence quality 
that was later gathered? (i.e., were the initial guesses accurate?)
"""
import json
from collections import defaultdict
import statistics

def load_vendors(filepath):
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
    return {v["vendor"]: v for v in data.get("vendors", [])}

# PreCyber: Validated → Consolidated (the only schema with actual score changes)
print("=" * 70)
print("  PREEMPTIVE CYBER: Validated vs Consolidated (Scores Actually Changed)")
print("=" * 70)

pc_val = load_vendors("Preemptive Cybersecurity Vendor 1-1 Validated.json")
pc_con = load_vendors("Preemptive Cybersecurity Vendor 2-1 Consolidated.json")

common = sorted(set(pc_val.keys()) & set(pc_con.keys()))
scored = [n for n in common 
          if any(v > 0 for v in pc_val[n].get("pillar_scores", {}).values()) and 
             any(v > 0 for v in pc_con[n].get("pillar_scores", {}).values())]

print(f"Vendors with scores in both: {len(scored)}")

# Sub-pillar level comparison
sub_deltas = []
sub_up = 0
sub_down = 0
sub_same = 0

for name in scored:
    v_subs = pc_val[name].get("sub_pillar_scores_current", {})
    c_subs = pc_con[name].get("sub_pillar_scores_current", {})
    
    for sp in v_subs:
        if sp in c_subs and v_subs[sp] > 0 and c_subs[sp] > 0:
            delta = c_subs[sp] - v_subs[sp]
            sub_deltas.append(delta)
            if delta > 0.1:
                sub_up += 1
            elif delta < -0.1:
                sub_down += 1
            else:
                sub_same += 1

total_sp = len(sub_deltas)
print(f"\nSub-pillar comparisons: {total_sp}")
print(f"  Scores went UP (>0.1):    {sub_up} ({sub_up/total_sp*100:.1f}%)")
print(f"  Scores went DOWN (<-0.1): {sub_down} ({sub_down/total_sp*100:.1f}%)")
print(f"  Scores stayed (±0.1):     {sub_same} ({sub_same/total_sp*100:.1f}%)")
print(f"  Mean delta: {statistics.mean(sub_deltas):+.2f}")
print(f"  Median delta: {statistics.median(sub_deltas):+.2f}")

# Distribution of deltas
for low, high, label in [(-5, -2, "Dropped 2+"), (-2, -1, "Dropped 1-2"), 
                          (-1, -0.5, "Dropped 0.5-1"), (-0.5, -0.1, "Dropped 0.1-0.5"),
                          (-0.1, 0.1, "Stable ±0.1"), (0.1, 0.5, "Rose 0.1-0.5"),
                          (0.5, 1, "Rose 0.5-1"), (1, 2, "Rose 1-2"), (2, 5, "Rose 2+")]:
    count = sum(1 for d in sub_deltas if low <= d < high)
    print(f"  {label}: {count} ({count/total_sp*100:.1f}%)")

# Vendor-level: who changed most
vendor_changes = []
for name in scored:
    v_pillars = pc_val[name].get("pillar_scores", {})
    c_pillars = pc_con[name].get("pillar_scores", {})
    
    v_avg = sum(v_pillars.values()) / len(v_pillars)
    c_avg = sum(c_pillars.values()) / len(c_pillars)
    delta = c_avg - v_avg
    vendor_changes.append((name, v_avg, c_avg, delta))

vendor_changes.sort(key=lambda x: x[3])

print(f"\n  TOP 10 SCORE DROPS (Validated → Consolidated):")
for name, before, after, delta in vendor_changes[:10]:
    print(f"    {name}: {before:.2f} → {after:.2f} ({delta:+.2f})")

print(f"\n  TOP 10 SCORE RISES (Validated → Consolidated):")
for name, before, after, delta in vendor_changes[-10:][::-1]:
    print(f"    {name}: {before:.2f} → {after:.2f} ({delta:+.2f})")

# MDR: The key question - did the seed scores (assigned without evidence) 
# align with the evidence that was later gathered?
print(f"\n{'='*70}")
print(f"  MDR: Comparing Initial Scores vs Evidence Quality Found Later")
print(f"{'='*70}")

mdr_con = load_vendors("MDR Services Vendor 2-1 Consolidated.json")

def compute_evidence_quality(ev_obj):
    if not isinstance(ev_obj, dict):
        return 0
    urls = ev_obj.get("source_urls", [])
    excerpts = ev_obj.get("excerpts", [])
    sources = ev_obj.get("sources", [])
    src_count = (len(urls) if isinstance(urls, list) else 0) + (len(sources) if isinstance(sources, list) else 0)
    exc_count = len(excerpts) if isinstance(excerpts, list) else 0
    
    # Relevance
    rel_scores = []
    if isinstance(excerpts, list):
        for ex in excerpts:
            if isinstance(ex, dict):
                rs = ex.get("relevance_score", 0)
                if rs:
                    rel_scores.append(float(rs))
    avg_rel = statistics.mean(rel_scores) if rel_scores else 0
    
    eq = 0
    if src_count >= 3: eq += 1.0
    elif src_count >= 1: eq += 0.5
    if exc_count >= 5: eq += 1.5
    elif exc_count >= 3: eq += 1.0
    elif exc_count >= 1: eq += 0.5
    eq += min(avg_rel / 100 * 1.5, 1.5) if avg_rel > 0 else 0
    
    return round(eq, 2)

# For each MDR vendor: compare their score vs evidence quality
mdr_vendor_stats = []
for name, v in mdr_con.items():
    subs = v.get("sub_pillar_scores_current", {})
    evidence = v.get("sub_pillar_evidence", {})
    pillars = v.get("pillar_scores", {})
    
    if not any(s > 0 for s in pillars.values()):
        continue
    
    score_gaps = []
    for sp_id, score in subs.items():
        if score == 0:
            continue
        ev_obj = evidence.get(sp_id, {})
        eq = compute_evidence_quality(ev_obj)
        score_gaps.append(score - eq)
    
    if score_gaps:
        avg_score = sum(subs[k] for k in subs if subs[k] > 0) / sum(1 for k in subs if subs[k] > 0)
        avg_gap = statistics.mean(score_gaps)
        mdr_vendor_stats.append((name, avg_score, avg_gap, len(score_gaps)))

mdr_vendor_stats.sort(key=lambda x: x[2], reverse=True)

high_score_high_gap = [v for v in mdr_vendor_stats if v[1] >= 3.5 and v[2] >= 1.5]
high_score_low_gap = [v for v in mdr_vendor_stats if v[1] >= 3.5 and v[2] < 1.0]
low_score_high_gap = [v for v in mdr_vendor_stats if v[1] < 2.5 and v[2] >= 1.5]

print(f"\nMDR Vendors analyzed: {len(mdr_vendor_stats)}")
print(f"\nHigh-score + High score-evidence gap (scored well, weak evidence): {len(high_score_high_gap)}")
for n, s, g, count in high_score_high_gap[:10]:
    print(f"  {n}: score={s:.2f}, gap={g:+.2f}")
    
print(f"\nHigh-score + Low score-evidence gap (scored well, strong evidence): {len(high_score_low_gap)}")
for n, s, g, count in high_score_low_gap[:10]:
    print(f"  {n}: score={s:.2f}, gap={g:+.2f}")

# Aggregate MDR gap
all_mdr_gaps = [v[2] for v in mdr_vendor_stats]
print(f"\nMDR Overall score-evidence gap: mean={statistics.mean(all_mdr_gaps):+.2f}, median={statistics.median(all_mdr_gaps):+.2f}")
above_1 = sum(1 for g in all_mdr_gaps if g > 1.0)
above_2 = sum(1 for g in all_mdr_gaps if g > 2.0)
print(f"Gap > 1.0: {above_1}/{len(all_mdr_gaps)} ({above_1/len(all_mdr_gaps)*100:.1f}%)")
print(f"Gap > 2.0: {above_2}/{len(all_mdr_gaps)} ({above_2/len(all_mdr_gaps)*100:.1f}%)")
