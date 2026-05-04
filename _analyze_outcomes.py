"""Analyze outcome maturity and pricing data for new outcomes-focused report."""
import json
from collections import Counter

d = json.load(open('MDR Services Vendor Pricing 2-1 AI Enriched.json', encoding='utf-8'))
vs = d['vendors']
print(f"Total vendors: {len(vs)}")

# Outcome maturity distribution (v2 preferred)
om_vals = []
for v in vs:
    om = v.get('outcome_maturity_rating_v2') or v.get('outcome_maturity_rating', 0)
    om_vals.append(om)
om_dist = Counter(om_vals)
print(f"\nOutcome maturity distribution: {dict(sorted(om_dist.items()))}")

# Pricing dimension stats
def get_score(v, dim):
    if v.get('pricing_dimension_scores_v2') and v['pricing_dimension_scores_v2']:
        return v['pricing_dimension_scores_v2'].get(dim, 0)
    return v.get('pricing_dimension_scores', {}).get(dim, 0)

dims = ['PRC-SUB', 'PRC-USG', 'PRC-FIX', 'PRC-SUC', 'PRC-COM', 'PRC-OUT']
for dim in dims:
    scores = [get_score(v, dim) for v in vs]
    avg = sum(scores) / len(scores) if scores else 0
    print(f"{dim}: avg={avg:.2f}, min={min(scores)}, max={max(scores)}")

# AI influence stats
ai_vals = [v.get('ai_pricing_influence', 0) for v in vs]
print(f"\nAI pricing influence: avg={sum(ai_vals)/len(ai_vals):.2f}")
ai_labels = Counter(v.get('ai_pricing_influence_label', 'Unknown') for v in vs)
print(f"AI tier distribution: {dict(ai_labels)}")

# Top 10 by outcome maturity
print("\nTop 10 by outcome maturity:")
top = sorted(vs, key=lambda x: x.get('outcome_maturity_rating_v2') or x.get('outcome_maturity_rating', 0), reverse=True)[:10]
for t in top:
    om = t.get('outcome_maturity_rating_v2') or t.get('outcome_maturity_rating', 0)
    suc = get_score(t, 'PRC-SUC')
    out = get_score(t, 'PRC-OUT')
    ai = t.get('ai_pricing_influence', 0)
    print(f"  {t['vendor']}: outcome={om}, PRC-SUC={suc}, PRC-OUT={out}, AI={ai:.1f}, type={t.get('pricing_model_type','')}")

# Outcome maturity vs AI influence correlation
print("\nOutcome maturity by AI tier:")
by_tier = {}
for v in vs:
    tier = v.get('ai_pricing_influence_label', 'Unknown')
    om = v.get('outcome_maturity_rating_v2') or v.get('outcome_maturity_rating', 0)
    by_tier.setdefault(tier, []).append(om)
for tier, vals in sorted(by_tier.items()):
    print(f"  {tier}: avg outcome={sum(vals)/len(vals):.2f}, count={len(vals)}")

# Pricing model type vs outcome maturity
print("\nOutcome maturity by pricing model type:")
by_pmt = {}
for v in vs:
    pmt = v.get('pricing_model_type', 'Unknown')
    om = v.get('outcome_maturity_rating_v2') or v.get('outcome_maturity_rating', 0)
    by_pmt.setdefault(pmt, []).append(om)
for pmt, vals in sorted(by_pmt.items()):
    print(f"  {pmt}: avg outcome={sum(vals)/len(vals):.2f}, count={len(vals)}")

# Vendors with outcome signals
print("\nVendors with outcome signals (v2):")
with_signals = [v for v in vs if v.get('outcome_signals_v2')]
print(f"  {len(with_signals)} of {len(vs)} have outcome signals")

# MDR service type vs outcome maturity
print("\nOutcome maturity by MDR service type:")
by_stype = {}
for v in vs:
    st = v.get('mdr_service_type', 'Unknown')
    om = v.get('outcome_maturity_rating_v2') or v.get('outcome_maturity_rating', 0)
    by_stype.setdefault(st, []).append(om)
for st, vals in sorted(by_stype.items()):
    print(f"  {st}: avg outcome={sum(vals)/len(vals):.2f}, count={len(vals)}")

# Capability scores (AIO pillar) vs outcome maturity
print("\nAIO capability vs outcome maturity:")
aio_bins = {}
for v in vs:
    aio = v.get('ai_capability_scores', {})
    if aio:
        aio_avg = sum(aio.values()) / len(aio) if aio else 0
        om = v.get('outcome_maturity_rating_v2') or v.get('outcome_maturity_rating', 0)
        bucket = f"{int(aio_avg)}-{int(aio_avg)+1}"
        aio_bins.setdefault(bucket, []).append(om)
for b, vals in sorted(aio_bins.items()):
    print(f"  AIO {b}: avg outcome={sum(vals)/len(vals):.2f}, count={len(vals)}")

# Key stats for report
print("\n=== KEY STATS FOR REPORT ===")
suc_scores = [get_score(v, 'PRC-SUC') for v in vs]
out_scores = [get_score(v, 'PRC-OUT') for v in vs]
om_all = [v.get('outcome_maturity_rating_v2') or v.get('outcome_maturity_rating', 0) for v in vs]

print(f"Vendors at outcome maturity <=1: {sum(1 for x in om_all if x <= 1)} ({sum(1 for x in om_all if x <= 1)/len(vs)*100:.0f}%)")
print(f"Vendors at outcome maturity <=2: {sum(1 for x in om_all if x <= 2)} ({sum(1 for x in om_all if x <= 2)/len(vs)*100:.0f}%)")
print(f"Vendors at outcome maturity >=3: {sum(1 for x in om_all if x >= 3)} ({sum(1 for x in om_all if x >= 3)/len(vs)*100:.0f}%)")
print(f"Vendors at outcome maturity >=4: {sum(1 for x in om_all if x >= 4)} ({sum(1 for x in om_all if x >= 4)/len(vs)*100:.0f}%)")
