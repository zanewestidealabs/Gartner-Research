"""Show before/after rationale comparison for quality review."""
import json
from enrich_offsec_rationales import load_schema, is_thin_rationale, build_enriched_rationale

with open("Offensive Security Vendor 2-1 Consolidated.json", "r", encoding="utf-8") as f:
    data = json.load(f)
schema = load_schema()

# Show 5 before/after examples across different vendors
count = 0
seen_vendors = set()
for v in data["vendors"]:
    vname = v["vendor"]
    if vname in seen_vendors:
        continue
    scores = v.get("sub_pillar_scores_current", {})
    ev = v.get("sub_pillar_evidence", {})
    for sp_id in sorted(ev.keys()):
        sc = scores.get(sp_id, 0)
        if sc == 0:
            continue
        e = ev[sp_id]
        rat = e.get("rationale", "")
        if is_thin_rationale(rat):
            new_rat = build_enriched_rationale(vname, sp_id, sc, rat, e, schema.get(sp_id, {}))
            print(f"=== {vname} / {sp_id} (score {sc}) ===")
            print(f"BEFORE: {rat}")
            print(f"\nAFTER:  {new_rat}")
            print()
            count += 1
            seen_vendors.add(vname)
            break
    if count >= 6:
        break
