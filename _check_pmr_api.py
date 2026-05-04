"""Quick check of what the API serves for PMR vendors."""
import urllib.request, json

r = urllib.request.urlopen('http://localhost:5000/api/vendors')
data = json.loads(r.read().decode())
vendors = data if isinstance(data, list) else data.get('vendors', [])
scored = [v for v in vendors if v.get('overall_gtm_score', 0) > 0]
print(f'API returned {len(vendors)} vendors, {len(scored)} scored')

if scored:
    v = scored[0]
    print(f'First scored: {v["vendor"]} GTM={v.get("overall_gtm_score")} Proof={v.get("overall_proof_score")}')
    subs = v.get('sub_pillar_scores', {})
    keys = list(subs.keys())[:2]
    for k in keys:
        print(f'  {k}: {subs[k]}')
else:
    v = vendors[0]
    print(f'First vendor: {v["vendor"]}')
    print(f'  overall_gtm_score: {v.get("overall_gtm_score")}')
    subs = v.get('sub_pillar_scores', {})
    keys = list(subs.keys())[:2]
    for k in keys:
        print(f'  {k}: {subs[k]}')

# Also check pmr-stats
r2 = urllib.request.urlopen('http://localhost:5000/api/pmr-stats')
stats = json.loads(r2.read().decode())
print(f'\nPMR stats vendor_count: {stats.get("vendor_count")}')
print(f'scored_vendors: {stats.get("scored_vendors")}')
gd = stats.get('grade_distribution', {})
print(f'grade_distribution: {gd}')
