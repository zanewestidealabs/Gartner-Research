import json
with open("Product Market Readiness Vendor 1-0 Seed.json", "r", encoding="utf-8-sig") as f:
    d = json.load(f)
cs = [v for v in d["vendors"] if v["vendor"] == "CrowdStrike"][0]
e = cs["sub_pillar_scores"]["PPD-01"]
print("Local file check:")
print(f"  Excerpts count: {len(e.get('excerpts', []))}")
print(f"  Has evidence_metadata: {'evidence_metadata' in e}")
print(f"  Has enrichment_metadata: {'enrichment_metadata' in d}")
print(f"  Enrichment date: {d.get('enrichment_metadata', {}).get('enrichment_date', 'N/A')}")
print(f"  Stats: {d.get('enrichment_metadata', {}).get('stats', {})}")
