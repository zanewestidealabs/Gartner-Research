"""Extract comprehensive pricing data for Market Insight note."""
import urllib.request, json

r = urllib.request.urlopen('http://localhost:5000/api/mdr-pricing')
d = json.loads(r.read())

ais = d.get('ai_influence_stats', {})
os_stats = d['overall_stats']
ds = d['dimension_stats']
cs = d['cohort_scores']
pb = d.get('pricing_benchmarks', {})

print('=== OVERALL ===')
print(f"Vendors: {d['vendor_count']}")
print(f"Market Avg: {os_stats['mean']:.2f}, Median: {os_stats['median']}, Min: {os_stats['min']}, Max: {os_stats['max']}")
print(f"Outcome Avg: {d['outcome_stats']['mean']:.2f}")

print()
print('=== AI INFLUENCE ===')
print(f"Mean: {ais['mean']:.2f}, Median: {ais['median']}, Min: {ais['min']}, Max: {ais['max']}")
for lbl in ['Transformative','Significant','Emerging','Minimal']:
    print(f"  {lbl}: {ais['by_label'].get(lbl,0)}")

print()
print('=== DIMENSION SCORES ===')
for dim in d['dimensions']:
    s = ds[dim]
    b = pb.get(dim, {})
    t10 = b.get('top10_avg')
    t10s = f"{t10:.2f}" if t10 else "?"
    print(f"  {dim} ({s['label']}): Avg={s['mean']:.2f}, Median={s['median']}, Top10={t10s}")

print()
print('=== BY MODEL TYPE ===')
for mt, avg in sorted(cs['by_model_type'].items(), key=lambda x: -x[1]):
    cnt = d['cohorts']['pricing_model_type'].get(mt, 0)
    ai = ais['by_model_type'].get(mt, 0)
    print(f"  {mt}: count={cnt}, avg_score={avg:.2f}, ai_influence={ai:.2f}")

print()
print('=== BY SERVICE TYPE ===')
for st, avg in sorted(cs['by_service_type'].items(), key=lambda x: -x[1]):
    cnt = d['cohorts']['mdr_service_type'].get(st, 0)
    ai = ais['by_service_type'].get(st, 0)
    print(f"  {st}: count={cnt}, avg_score={avg:.2f}, ai_influence={ai:.2f}")

print()
print('=== PRC-SUC (Success/Outcome-based) DETAIL ===')
suc = ds['PRC-SUC']
print(f"Avg: {suc['mean']:.2f}, Median: {suc['median']}, Min: {suc['min']}, Max: {suc['max']}")
low_suc = sum(1 for v in d['vendors'] if (v.get('pricing_dimension_scores',{}).get('PRC-SUC',0)) <= 2)
mid_suc = sum(1 for v in d['vendors'] if 2 < (v.get('pricing_dimension_scores',{}).get('PRC-SUC',0)) <= 3)
high_suc = sum(1 for v in d['vendors'] if (v.get('pricing_dimension_scores',{}).get('PRC-SUC',0)) > 3)
print(f"Score <=2: {low_suc}, Score 2.1-3: {mid_suc}, Score >3: {high_suc}")

print()
print('=== PRC-OUT (Outcome Maturity) DETAIL ===')
out = ds['PRC-OUT']
print(f"Avg: {out['mean']:.2f}, Median: {out['median']}, Min: {out['min']}, Max: {out['max']}")
low_out = sum(1 for v in d['vendors'] if (v.get('pricing_dimension_scores',{}).get('PRC-OUT',0)) <= 2)
high_out = sum(1 for v in d['vendors'] if (v.get('pricing_dimension_scores',{}).get('PRC-OUT',0)) > 3)
print(f"Score <=2: {low_out}, Score >3: {high_out}")

print()
print('=== AI vs PRICING CORRELATION ===')
sig_plus = [v for v in d['vendors'] if v.get('ai_pricing_influence_label') in ('Significant','Transformative')]
minimal = [v for v in d['vendors'] if v.get('ai_pricing_influence_label') == 'Minimal']
emerging = [v for v in d['vendors'] if v.get('ai_pricing_influence_label') == 'Emerging']
sig_avg = sum(v['pricing_overall_score'] for v in sig_plus)/len(sig_plus) if sig_plus else 0
min_avg = sum(v['pricing_overall_score'] for v in minimal)/len(minimal) if minimal else 0
emg_avg = sum(v['pricing_overall_score'] for v in emerging)/len(emerging) if emerging else 0
print(f"Significant+ ({len(sig_plus)} vendors): avg pricing = {sig_avg:.2f}")
print(f"Emerging ({len(emerging)} vendors): avg pricing = {emg_avg:.2f}")
print(f"Minimal ({len(minimal)} vendors): avg pricing = {min_avg:.2f}")
print(f"Gap (Sig+ vs Minimal): {sig_avg - min_avg:.2f}")

sig_suc = sum(v.get('pricing_dimension_scores',{}).get('PRC-SUC',0) for v in sig_plus)/len(sig_plus) if sig_plus else 0
min_suc = sum(v.get('pricing_dimension_scores',{}).get('PRC-SUC',0) for v in minimal)/len(minimal) if minimal else 0
print(f"PRC-SUC avg for Sig+: {sig_suc:.2f} vs Minimal: {min_suc:.2f}")

sig_out = sum(v.get('pricing_dimension_scores',{}).get('PRC-OUT',0) for v in sig_plus)/len(sig_plus) if sig_plus else 0
min_out = sum(v.get('pricing_dimension_scores',{}).get('PRC-OUT',0) for v in minimal)/len(minimal) if minimal else 0
print(f"PRC-OUT avg for Sig+: {sig_out:.2f} vs Minimal: {min_out:.2f}")

comp = [v for v in d['vendors'] if v.get('pricing_model_type') == 'Composable']
subo = [v for v in d['vendors'] if v.get('pricing_model_type') == 'Subscription-Only']
comp_suc = sum(v.get('pricing_dimension_scores',{}).get('PRC-SUC',0) for v in comp)/len(comp) if comp else 0
subo_suc = sum(v.get('pricing_dimension_scores',{}).get('PRC-SUC',0) for v in subo)/len(subo) if subo else 0
print(f"Composable PRC-SUC: {comp_suc:.2f} ({len(comp)} vendors), Sub-Only PRC-SUC: {subo_suc:.2f} ({len(subo)} vendors)")

# Top 10 vendors by PRC-SUC
print()
print('=== TOP 10 BY PRC-SUC ===')
by_suc = sorted(d['vendors'], key=lambda v: v.get('pricing_dimension_scores',{}).get('PRC-SUC',0), reverse=True)[:10]
for v in by_suc:
    suc_score = v.get('pricing_dimension_scores',{}).get('PRC-SUC',0)
    ai = v.get('ai_pricing_influence',0)
    print(f"  {v['vendor']}: PRC-SUC={suc_score}, AI={ai:.2f}, model={v.get('pricing_model_type','?')}")

# Region breakdown
print()
print('=== BY REGION ===')
for reg, avg in sorted(cs.get('by_region', cs.get('by_target_market', {})).items(), key=lambda x: -x[1]):
    cnt = d['cohorts'].get('region', d['cohorts'].get('target_market', {})).get(reg, 0)
    print(f"  {reg}: count={cnt}, avg_score={avg:.2f}")

# Strengths/weaknesses frequency
print()
print('=== COMMON STRENGTHS (top themes) ===')
from collections import Counter
all_str = []
all_weak = []
for v in d['vendors']:
    all_str.extend(v.get('pricing_strengths', []))
    all_weak.extend(v.get('pricing_weaknesses', []))
# Show first 100 chars of each for word freq
words_str = ' '.join(all_str).lower()
words_weak = ' '.join(all_weak).lower()
print(f"Total strengths across all vendors: {len(all_str)}")
print(f"Total weaknesses across all vendors: {len(all_weak)}")
