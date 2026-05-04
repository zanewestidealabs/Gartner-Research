"""Spot-check specific vendor sub-pillar evidence."""
import json, sys

vendor_name = sys.argv[1] if len(sys.argv) > 1 else "Zscaler"

with open("Preemptive Cybersecurity Vendor 1-1 Validated.json", encoding="utf-8") as f:
    data = json.load(f)

for v in data["vendors"]:
    if v["vendor"] == vendor_name:
        ev = v.get("sub_pillar_evidence", {})
        print(f"=== {vendor_name} ===")
        print(f"Research flag: {v.get('research_flag', 'N/A')}")
        print(f"Pillar scores: {v.get('pillar_scores', {})}")
        print()
        for sid in sorted(ev.keys()):
            if sid.startswith("_"):
                continue
            e = ev[sid]
            sp = e.get("sub_pillar_specificity", "?")
            sh = e.get("schema_criteria_hits", "?")
            ph = e.get("pillar_term_hits", "?")
            ch = e.get("criteria_hit_count", "?")
            ne = len(e.get("excerpts", []))
            score = v.get("sub_pillar_scores_validated", {}).get(sid, "?")
            print(f"  {sid}: score={score}  specificity={sp}  schema_hits={sh}  pillar_hits={ph}  criteria_hits={ch}  excerpts={ne}")
        break
else:
    print(f"Vendor '{vendor_name}' not found")
