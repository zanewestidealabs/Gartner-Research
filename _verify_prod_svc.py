import urllib.request, json

# Check vendor files list for PreCyber v2 schema
resp = urllib.request.urlopen("http://192.168.15.51:5000/api/vendor-files?schema=Preemptive_Cybersecurity_Schema_v2.json")
data = json.loads(resp.read())
for f in data.get("files", []):
    print(f"  {f['filename']:55s}  vendors={f.get('vendor_count', '?')}")

print()

# Check that v3-0 has 24 sub-pillar scores
resp2 = urllib.request.urlopen("http://192.168.15.51:5000/api/vendor-files?all=1")
data2 = json.loads(resp2.read())
for f in data2.get("files", []):
    if "3-0 SVC" in f["filename"]:
        print(f"Found: {f['filename']} with {f.get('vendor_count', '?')} vendors")
        break

# Load the actual vendor data from v3-0
resp3 = urllib.request.urlopen("http://192.168.15.51:5000/api/vendor-data?file=Preemptive+Cybersecurity+Vendor+3-0+SVC+Pricing.json")
vendors = json.loads(resp3.read())
if isinstance(vendors, dict) and "vendors" in vendors:
    vendors = vendors["vendors"]
print(f"\nv3-0 vendor count: {len(vendors)}")
v = vendors[0]
spc = v.get("sub_pillar_scores_current", {})
print(f"First vendor sub-pillar codes ({len(spc)}): {sorted(spc.keys())}")
pds = v.get("pricing_dimension_scores", {})
print(f"Pricing dims: {sorted(pds.keys())}")
print(f"Outcome maturity: {v.get('outcome_maturity_rating')}")
