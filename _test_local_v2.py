"""Quick local API test for SbD-AI v2 schema."""
import urllib.request, json

r = urllib.request.urlopen('http://127.0.0.1:5000/api/schema-files')
data = json.loads(r.read())
for s in data['schemas']:
    fn = s['filename']
    if 'Secure' in fn:
        d = s['display']
        print(f"{fn} -> abbr={d['abbr']}, title={d['title'][:60]}")

print()
r2 = urllib.request.urlopen('http://127.0.0.1:5000/api/schema-detail?schema=Secure_by_Design_AI_Controls_Schema_v2.json')
detail = json.loads(r2.read())
pillars = detail.get('pillars', {})
sps = detail.get('sub_pillars', {})
print(f"SbD-AI v2 schema-detail: {len(pillars)} pillars, {len(sps)} sub-pillars")
if isinstance(pillars, list):
    for p in pillars:
        code = p.get('code', p.get('name', '?'))
        cov = p.get('aiuc1_coverage', {})
        print(f"  {code}: {cov}")
elif isinstance(pillars, dict):
    for pk, pv in pillars.items():
        cov = pv.get('aiuc1_coverage', {})
        print(f"  {pk}: {cov}")

# Check a sub-pillar AIUC-1 mapping
if isinstance(sps, list):
    sample = next((s for s in sps if s.get('id') == 'NDS-04' or s.get('code') == 'NDS-04'), None)
elif isinstance(sps, dict):
    sample = sps.get('NDS-04', {})
else:
    sample = None
if sample:
    mapping = sample.get('aiuc1_mapping', {})
    print()
    print(f"NDS-04 aiuc1_mapping: {json.dumps(mapping, indent=2)}")
else:
    print("NDS-04 not found in sub_pillars")
