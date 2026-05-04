import json, urllib.request

# Check perspectives
r = urllib.request.urlopen('http://localhost:5000/api/mdr-market-insight/perspectives')
d = json.loads(r.read())
print(f"{len(d['perspectives'])} perspectives:")
for p in d['perspectives']:
    print(f"  {p['id']}: {p['label']}")

# Verify the new report loads
r2 = urllib.request.urlopen('http://localhost:5000/api/mdr-market-insight?perspective=cpo-outcome-metrics')
d2 = json.loads(r2.read())
print(f"\nNew report loaded: {d2['id']}")
print(f"Title: {d2['title']}")
print(f"Findings: {len(d2['findings'])}, Recs: {len(d2['recommendations'])}, Sections: {len(d2['analysis_sections'])}")
