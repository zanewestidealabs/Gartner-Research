"""Quick validation of OffSec v2.1 evidence after excerpt extraction."""
import json

with open("Offensive Security Vendor 2-1 Consolidated.json", "r", encoding="utf-8") as f:
    data = json.load(f)

vendors = data["vendors"]
print(f"Vendors: {len(vendors)}")
print(f"File size: {len(json.dumps(data)):,} chars")

total_excerpts = 0
total_sources = 0
vendors_with_excerpts = 0
hit_count_entries = 0

for v in vendors:
    ev = v.get("sub_pillar_evidence", {})
    v_excerpts = 0
    for sp_id, e in ev.items():
        excerpts = e.get("excerpts", [])
        sources = e.get("sources", [])
        v_excerpts += len(excerpts)
        total_sources += len(sources)
        if e.get("hit_count"):
            hit_count_entries += 1
    total_excerpts += v_excerpts
    if v_excerpts > 0:
        vendors_with_excerpts += 1

print(f"Vendors with excerpts: {vendors_with_excerpts}/{len(vendors)}")
print(f"Total excerpts: {total_excerpts}")
print(f"Total source citations: {total_sources}")
print(f"Avg excerpts/vendor: {total_excerpts/len(vendors):.1f}")
print(f"Evidence entries with hit_count: {hit_count_entries}")

# Sample from 3 vendors
for idx in [0, 20, 44]:
    v = vendors[idx]
    vname = v["vendor"]
    ev = v.get("sub_pillar_evidence", {})
    sp_ids = sorted(ev.keys())
    if not sp_ids:
        continue
    sp = sp_ids[0]
    e = ev[sp]
    print(f"\n--- {vname} / {sp} ---")
    rat = e.get("rationale", "")
    print(f"  Rationale: {rat[:120]}...")
    print(f"  Sources: {len(e.get('sources', []))}")
    print(f"  Excerpts: {len(e.get('excerpts', []))}")
    print(f"  hit_count: {e.get('hit_count')}")
    print(f"  specific_hit_count: {e.get('specific_hit_count')}")
    notes = e.get("notes", "")
    print(f"  notes: {notes[:140]}")
    excerpts = e.get("excerpts", [])
    if excerpts:
        ex = excerpts[0]
        print(f"  Top excerpt (score {ex['relevance_score']}):")
        print(f"    {ex['excerpt'][:200]}")
        print(f"    matched: {ex['matched_terms']}")
