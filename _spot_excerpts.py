"""Spot-check specific vendor sub-pillar excerpts."""
import json, sys

vendor_name = sys.argv[1] if len(sys.argv) > 1 else "Zscaler"
sid_filter = sys.argv[2] if len(sys.argv) > 2 else "AMT-01"

with open("Preemptive Cybersecurity Vendor 1-1 Validated.json", encoding="utf-8") as f:
    data = json.load(f)

for v in data["vendors"]:
    if v["vendor"] == vendor_name:
        ev = v.get("sub_pillar_evidence", {}).get(sid_filter, {})
        print(f"=== {vendor_name} / {sid_filter} ===")
        print(f"Sub-pillar specificity: {ev.get('sub_pillar_specificity', '?')}")
        print(f"Schema criteria hits: {ev.get('schema_criteria_hits', '?')}")
        print(f"Pillar term hits: {ev.get('pillar_term_hits', '?')}")
        print(f"Score: {v.get('sub_pillar_scores_validated', {}).get(sid_filter, '?')}")
        print()
        for i, exc in enumerate(ev.get("excerpts", [])[:3], 1):
            print(f"  Excerpt {i}: {exc.get('excerpt', '')[:200]}")
            print(f"    Terms: {exc.get('matched_terms', [])}")
            print(f"    Relevance: {exc.get('relevance_score', '?')}")
            print(f"    URL: {exc.get('url', '?')[:80]}")
            print()
        break
