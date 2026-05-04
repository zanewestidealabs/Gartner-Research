"""Quick analysis of MDR 2.0 scores and excerpt coverage."""
import json
from collections import Counter

with open("MDR Services Vendor 2-0 Researched.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)

vendors = data["vendors"]

# Sample vendors
for vi in [0, 15, 50, 80]:
    v = vendors[vi]
    vn = v["vendor"]
    scores = v.get("sub_pillar_scores_current", {})
    ev = v.get("sub_pillar_evidence", {})
    total_exc = sum(len(ev.get(sp, {}).get("excerpts", [])) for sp in scores)
    avg_score = sum(float(s) for s in scores.values()) / max(len(scores), 1)
    print(f"[{vi}] {vn}: avg={avg_score:.2f}, excerpts={total_exc}")
    # Sample excerpt
    for sp_id in list(scores.keys())[:1]:
        exc = ev.get(sp_id, {}).get("excerpts", [])
        if exc:
            print(f"  {sp_id} excerpt: \"{exc[0]['excerpt'][:120]}...\"")
    print()

# Score distribution
all_scores = []
for v in vendors:
    for sp_id, sc in v.get("sub_pillar_scores_current", {}).items():
        all_scores.append(float(sc))

dist = Counter(all_scores)
print("Score distribution across all 93 vendors × 32 sub-pillars:")
for s in sorted(dist.keys()):
    print(f"  {s}: {dist[s]} ({dist[s]/len(all_scores)*100:.1f}%)")
print(f"Total: {len(all_scores)} sub-pillar scores")
print(f"Mean: {sum(all_scores)/len(all_scores):.2f}")

# Excerpt coverage vs score
print("\nExcerpt coverage by score level:")
score_excerpt = {}
for v in vendors:
    scores = v.get("sub_pillar_scores_current", {})
    ev = v.get("sub_pillar_evidence", {})
    for sp_id, sc in scores.items():
        sc = float(sc)
        n_exc = len(ev.get(sp_id, {}).get("excerpts", []))
        bucket = int(sc)
        if bucket not in score_excerpt:
            score_excerpt[bucket] = {"total": 0, "with_excerpts": 0, "excerpt_count": 0}
        score_excerpt[bucket]["total"] += 1
        if n_exc > 0:
            score_excerpt[bucket]["with_excerpts"] += 1
        score_excerpt[bucket]["excerpt_count"] += n_exc

for s in sorted(score_excerpt.keys()):
    d = score_excerpt[s]
    pct = d["with_excerpts"] / max(d["total"], 1) * 100
    avg_e = d["excerpt_count"] / max(d["total"], 1)
    print(f"  Score {s}: {d['total']} sub-pillars, {pct:.0f}% have excerpts, avg {avg_e:.1f} excerpts")

# Check how many vendors have v2_researched scores == current scores (all should be same)
same_count = 0
diff_count = 0
for v in vendors:
    curr = v.get("sub_pillar_scores_current", {})
    v2r = v.get("sub_pillar_scores_v2_researched", {})
    for sp_id in curr:
        if float(curr.get(sp_id, 0)) == float(v2r.get(sp_id, 0)):
            same_count += 1
        else:
            diff_count += 1
print(f"\nv2_researched vs current: {same_count} same, {diff_count} different")
