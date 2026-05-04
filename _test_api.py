import urllib.request, json
r = urllib.request.urlopen('http://localhost:5000/api/precyber-market-insight/perspectives')
d = json.loads(r.read())
print(type(d))
if isinstance(d, dict):
    items = d.get('perspectives', d.get('reports', list(d.values())))
    if isinstance(items, list):
        for p in items:
            if isinstance(p, dict):
                print(f"  {p.get('id','?')}: {str(p.get('label','?'))[:80]}")
            else:
                print(f"  {p}")
        print(f"Total: {len(items)}")
    else:
        print(d)
elif isinstance(d, list):
    for p in d:
        print(f"  {p}")
    print(f"Total: {len(d)}")
else:
    print(d)

# Test the new report loads
r2 = urllib.request.urlopen('http://localhost:5000/api/precyber-market-insight?perspective=cpo-killchain-mitre-v2')
d2 = json.loads(r2.read())
print(f"\nNew report title: {d2.get('title','???')[:80]}")
print(f"Findings: {len(d2.get('findings',[]))}")
print(f"Recommendations: {len(d2.get('recommendations',[]))}")
print(f"Analysis sections: {len(d2.get('analysis_sections',[]))}")
print(f"Glossary: {len(d2.get('glossary',[]))}")
print(f"Evidence: {len(d2.get('evidence',[]))}")

# Test PPTX endpoint
try:
    r3 = urllib.request.urlopen('http://localhost:5000/api/precyber-kcmitre-pptx')
    print(f"\nPPTX endpoint: OK ({len(r3.read())} bytes)")
except Exception as e:
    print(f"\nPPTX endpoint: FAILED - {e}")
