"""Sub-pillar gap analysis for startups."""
import json

d = json.load(open("Product Market Readiness Vendor 1-1 Enriched.json", "r", encoding="utf-8"))
v0 = d["vendors"][0]
labels = v0.get("sub_pillar_schema_labels", {})
vendors = d["vendors"]
startups = [v for v in vendors if v.get("is_startup") is True]
ai_startups = [v for v in startups if v.get("is_ai_first") is True]
non_ai_startups = [v for v in startups if v.get("is_ai_first") is not True]

def avg(lst):
    return sum(lst) / len(lst) if lst else 0

def get_vals(vlist, sp_id, field):
    return [v.get("sub_pillar_scores", {}).get(sp_id, {}).get(field) for v in vlist
            if v.get("sub_pillar_scores", {}).get(sp_id, {}).get(field) is not None]

print("=== STARTUP SUB-PILLAR GAPS (top 10 widest) ===")
gaps_all = {}
for sid in sorted(labels.keys()):
    vals = get_vals(startups, sid, "credibility_gap")
    if vals:
        gaps_all[sid] = avg(vals)
for sid, g in sorted(gaps_all.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {sid} ({labels[sid]}): {g:.3f}")

print("\n=== STARTUP SUB-PILLAR GAPS (bottom 5 - under-marketed) ===")
for sid, g in sorted(gaps_all.items(), key=lambda x: x[1])[:5]:
    print(f"  {sid} ({labels[sid]}): {g:.3f}")

print("\n=== AI-FIRST STARTUP SUB-PILLAR GAPS (top 10 widest) ===")
for sid in sorted(labels.keys()):
    vals = get_vals(ai_startups, sid, "credibility_gap")
    if vals:
        gaps_all[sid] = avg(vals)
for sid, g in sorted(gaps_all.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {sid} ({labels[sid]}): {g:.3f}")

print("\n=== STARTUP WEAKEST PROOF (lowest avg) ===")
proof_avgs = {}
for sid in sorted(labels.keys()):
    vals = get_vals(startups, sid, "proof_of_execution_score")
    if vals:
        proof_avgs[sid] = avg(vals)
for sid, p in sorted(proof_avgs.items(), key=lambda x: x[1])[:10]:
    print(f"  {sid} ({labels[sid]}): {p:.2f}")

print("\n=== STARTUP STRONGEST GTM (highest avg) ===")
gtm_avgs = {}
for sid in sorted(labels.keys()):
    vals = get_vals(startups, sid, "gtm_messaging_score")
    if vals:
        gtm_avgs[sid] = avg(vals)
for sid, g in sorted(gtm_avgs.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {sid} ({labels[sid]}): {g:.2f}")

print("\n=== PCM SUB-PILLAR: AI vs NON-AI STARTUPS ===")
for sid in sorted(labels.keys()):
    if not sid.startswith("PCM"):
        continue
    ai_vals = get_vals(ai_startups, sid, "credibility_gap")
    nai_vals = get_vals(non_ai_startups, sid, "credibility_gap")
    print(f"  {sid} ({labels[sid]}): AI={avg(ai_vals):.3f}  Non-AI={avg(nai_vals):.3f}")

print("\n=== PPD SUB-PILLAR: AI vs NON-AI STARTUPS ===")
for sid in sorted(labels.keys()):
    if not sid.startswith("PPD"):
        continue
    ai_vals = get_vals(ai_startups, sid, "credibility_gap")
    nai_vals = get_vals(non_ai_startups, sid, "credibility_gap")
    print(f"  {sid} ({labels[sid]}): AI={avg(ai_vals):.3f}  Non-AI={avg(nai_vals):.3f}")

print("\n=== REGION DISTRIBUTION (startups) ===")
from collections import Counter
regions = Counter(v.get("region", "Unknown") for v in startups)
for r, c in regions.most_common():
    print(f"  {r}: {c}")

print("\n=== REGION DISTRIBUTION (AI-first startups) ===")
ai_regions = Counter(v.get("region", "Unknown") for v in ai_startups)
for r, c in ai_regions.most_common():
    print(f"  {r}: {c}")

print("\nDone.")
