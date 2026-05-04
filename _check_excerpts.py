"""Check excerpt state in MDR data files."""
import json

for fname in ["MDR Services Vendor 2-0 Researched.json", "MDR Services Vendor Capability 1-0 Seed.json"]:
    print(f"\n=== {fname} ===")
    with open(fname, "r", encoding="utf-8-sig") as f:
        d = json.load(f)
    vendors = d["vendors"]
    empty_exc = 0
    has_exc = 0
    total_ev = 0
    for v in vendors:
        for sp_id, e in v.get("sub_pillar_evidence", {}).items():
            total_ev += 1
            exc = e.get("excerpts", [])
            if not exc:
                empty_exc += 1
            else:
                has_exc += 1
    print(f"  Total evidence entries: {total_ev}")
    print(f"  With excerpts: {has_exc}")
    print(f"  Empty excerpts: {empty_exc}")

    # Show a sample
    v0 = vendors[0]
    e0 = v0.get("sub_pillar_evidence", {}).get("TDR-01", {})
    print(f"  Sample TDR-01 ({v0['vendor']}):")
    print(f"    excerpts: {e0.get('excerpts', [])}")
    print(f"    notes: {e0.get('notes', '')[:200]}")
    print(f"    source_urls: {e0.get('source_urls', [])}")

# Compare with TRiSM which HAS excerpts
print("\n=== AI TRiSM 2-1 (reference) ===")
with open("AI TRiSM Vendor 2-1 Consolidated.json", "r", encoding="utf-8-sig") as f:
    t = json.load(f)
tv = t["vendors"][0]
te = tv.get("sub_pillar_evidence", {}).get("GOV-01", {})
print(f"  Sample GOV-01 ({tv['vendor']}):")
print(f"    excerpts ({len(te.get('excerpts', []))}): {str(te.get('excerpts', []))[:300]}")
print(f"    notes: {te.get('notes', '')[:200]}")
print(f"    source_urls: {te.get('source_urls', [])}")

# Check the rationale key_evidence field
print("\n=== MDR 2.0 key_evidence in rationale ===")
with open("MDR Services Vendor 2-0 Researched.json", "r", encoding="utf-8-sig") as f:
    d = json.load(f)
v0 = d["vendors"][0]
r0 = v0.get("sub_pillar_rationale_v2", {}).get("TDR-01", {})
print(f"  key_evidence: {r0.get('key_evidence', [])}")
