"""Distribution + polarity analysis for the v2-2 holistic scores.

Goals:
  1) Show overall score distribution (how many cells at each level / score band)
  2) For each vendor, show pillar profile and identify "peak" pillars
  3) Surface vendors whose evidence is RICH (many excerpts, many sources) but
     whose top score is still <=2.0 — those are the cases where the rubric is
     most likely too strict (rich evidence not converting to capability credit)
  4) Compare a tech vendor vs a services vendor profile
"""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path

DATA = json.load(open("Preemptive Cybersecurity Vendor 2-3 Holistic Validated.json", encoding="utf-8"))
SCHEMA = json.load(open("Preemptive_Cybersecurity_Schema_v2.json", encoding="utf-8"))
SUB = SCHEMA["preemptive_cybersecurity_taxonomy_v2.0"]["sub_pillars"]

PILLARS = sorted({sid.split("-")[0] for sid in SUB})
print("PILLARS:", PILLARS)

# 1) overall score distribution
score_bins = Counter()
level_bins = Counter()
status_bins = Counter()
all_scores = []
for v in DATA["vendors"]:
    sps = v.get("sub_pillar_scores_current") or {}
    rats = v.get("sub_pillar_rationale_v2") or {}
    for sid, s in sps.items():
        score_bins[round(float(s) * 4) / 4] += 1
        all_scores.append(float(s))
        r = rats.get(sid) or {}
        level_bins[r.get("scoring_level", "?")] += 1
        for c in r.get("criteria_assessment", []):
            status_bins[c.get("status", "?")] += 1

print("\n=== overall score distribution (52 vendors x 24 sub-pillars = 1248 cells) ===")
for s in sorted(score_bins):
    bar = "#" * (score_bins[s] // 8)
    print(f"  {s:>4} : {score_bins[s]:4d}  {bar}")
print(f"  mean={sum(all_scores)/len(all_scores):.2f}  median={sorted(all_scores)[len(all_scores)//2]:.2f}  max={max(all_scores):.2f}")

print("\n=== level distribution ===")
for lv in sorted(level_bins):
    print(f"  L{lv}: {level_bins[lv]}")

print("\n=== criterion status distribution (across all cells) ===")
total_crit = sum(status_bins.values()) or 1
for st, n in status_bins.most_common():
    print(f"  {st:7s}: {n:5d} ({n/total_crit:.1%})")

# 2) per-vendor pillar profile + peaks
print("\n=== per-vendor pillar profile (mean sub-pillar score per pillar) ===")
print(f"{'vendor':<32s} " + " ".join(f"{p:>5s}" for p in PILLARS) + "  peak")
rows = []
for v in DATA["vendors"]:
    name = (v.get("vendor") or "?")[:30]
    sps = v.get("sub_pillar_scores_current") or {}
    by_p = defaultdict(list)
    for sid, s in sps.items():
        by_p[sid.split("-")[0]].append(float(s))
    means = {p: (sum(by_p[p]) / len(by_p[p]) if by_p[p] else 0) for p in PILLARS}
    overall = sum(sps.values()) / max(len(sps), 1)
    peak_p = max(means, key=means.get)
    peak_v = means[peak_p]
    polarity = peak_v - (sum(means.values()) - peak_v) / max(len(PILLARS) - 1, 1)
    rows.append((name, means, overall, peak_p, peak_v, polarity))

# sort by overall mean desc
for name, means, overall, peak_p, peak_v, polarity in sorted(rows, key=lambda r: -r[2])[:15]:
    cells = " ".join(f"{means[p]:5.2f}" for p in PILLARS)
    print(f"{name:<32s} {cells}   {peak_p}={peak_v:.2f}  Δ={polarity:+.2f}  μ={overall:.2f}")

print("\n=== bottom 10 (lowest mean) ===")
for name, means, overall, peak_p, peak_v, polarity in sorted(rows, key=lambda r: r[2])[:10]:
    cells = " ".join(f"{means[p]:5.2f}" for p in PILLARS)
    print(f"{name:<32s} {cells}   {peak_p}={peak_v:.2f}  Δ={polarity:+.2f}  μ={overall:.2f}")

# 3) Rich-evidence-but-low-score: candidates for "rubric too strict"
print("\n=== RICH EVIDENCE BUT LOW SCORE (top capability cap <= 2.0 despite >=4 excerpts and >=2 sources) ===")
candidates = []
for v in DATA["vendors"]:
    name = (v.get("vendor") or "?")
    sps = v.get("sub_pillar_scores_current") or {}
    rats = v.get("sub_pillar_rationale_v2") or {}
    ev = v.get("sub_pillar_evidence") or {}
    for sid, s in sps.items():
        if float(s) > 2.0:
            continue
        eb = ev.get(sid) or {}
        ex = eb.get("excerpts") or []
        srcs = {e.get("url") for e in ex if isinstance(e, dict)}
        srcs.discard(None)
        if len(ex) >= 4 and len(srcs) >= 2:
            candidates.append((name, sid, float(s), len(ex), len(srcs)))
candidates.sort(key=lambda r: -r[3])
for c in candidates[:20]:
    print(f"  {c[0]:<32s} {c[1]:<7s} score={c[2]} excerpts={c[3]} sources={c[4]}")
print(f"  ... total such cells: {len(candidates)}")

# 4) Polarity ranking
print("\n=== TOP POLARITY (peak pillar dominates rest) ===")
for name, means, overall, peak_p, peak_v, polarity in sorted(rows, key=lambda r: -r[5])[:10]:
    cells = " ".join(f"{means[p]:5.2f}" for p in PILLARS)
    print(f"{name:<32s} {cells}   {peak_p}={peak_v:.2f}  Δ={polarity:+.2f}")

print("\n=== FLAT (lowest polarity, weak across the board) ===")
for name, means, overall, peak_p, peak_v, polarity in sorted(rows, key=lambda r: r[5])[:10]:
    cells = " ".join(f"{means[p]:5.2f}" for p in PILLARS)
    print(f"{name:<32s} {cells}   {peak_p}={peak_v:.2f}  Δ={polarity:+.2f}")
