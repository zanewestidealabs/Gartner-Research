"""Quick quality check of PreCyber vendor output."""
import json, statistics, sys

fname = sys.argv[1] if len(sys.argv) > 1 else "Preemptive Cybersecurity Vendor 1-1 Validated.json"
print(f"File: {fname}\n")

with open(fname, encoding="utf-8") as f:
    data = json.load(f)

vendors = data.get("vendors", data.get("preemptive_cybersecurity_taxonomy_v1.0", {}).get("vendors", []))
print(f"Total vendors: {len(vendors)}")

# Research flags
flags = {}
for v in vendors:
    rf = v.get("research_flag", "none")
    flags[rf] = flags.get(rf, 0) + 1
print(f"Research flags: {flags}")

# Pillar score stats
all_scores = []
for v in vendors:
    ps = v.get("pillar_scores", {})
    for p in ["EXM", "AMT", "ADR", "PPM"]:
        s = ps.get(p, 0)
        if isinstance(s, dict):
            s = s.get("score", 0)
        all_scores.append(s)

print(f"Pillar scores: min={min(all_scores):.2f}  max={max(all_scores):.2f}  "
      f"mean={statistics.mean(all_scores):.2f}  median={statistics.median(all_scores):.2f}  "
      f"stdev={statistics.stdev(all_scores):.2f}")

# Fetch failed
print("\nFetch-failed vendors:")
for v in vendors:
    if v.get("research_flag") == "fetch_failed":
        print(f"  {v['vendor']}")

# Low scorers
print("\nVendors with any pillar < 3.0:")
for v in vendors:
    ps = v.get("pillar_scores", {})
    low = []
    for p in ["EXM", "AMT", "ADR", "PPM"]:
        s = ps.get(p, 0)
        if isinstance(s, dict):
            s = s.get("score", 0)
        if s < 3.0:
            low.append(f"{p}={s:.2f}")
    if low:
        print(f"  {v['vendor']}: {' '.join(low)}")

# High scorers (all pillars >= 4.5)
print("\nVendors with ALL pillars >= 4.5:")
count_high = 0
for v in vendors:
    ps = v.get("pillar_scores", {})
    all_high = True
    vals = []
    for p in ["EXM", "AMT", "ADR", "PPM"]:
        s = ps.get(p, 0)
        if isinstance(s, dict):
            s = s.get("score", 0)
        vals.append(s)
        if s < 4.5:
            all_high = False
    if all_high:
        count_high += 1
        print(f"  {v['vendor']}: EXM={vals[0]:.2f} AMT={vals[1]:.2f} ADR={vals[2]:.2f} PPM={vals[3]:.2f}")
print(f"  Total: {count_high}/{len(vendors)}")

# Score histogram
print("\nPillar score distribution:")
buckets = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
for s in all_scores:
    b = min(int(s), 5)
    buckets[b] = buckets.get(b, 0) + 1
for b in sorted(buckets):
    print(f"  {b}.xx: {buckets[b]} ({buckets[b]/len(all_scores)*100:.1f}%)")
