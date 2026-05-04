"""Quick check of MDR vendor evidence completeness."""
import json

with open("MDR Services Vendor Capability 1-0 Seed.json", "r", encoding="utf-8-sig") as f:
    d = json.load(f)

for v in d["vendors"][:5]:
    name = v["vendor"]
    ev = v.get("sub_pillar_evidence", {})
    scores = v.get("sub_pillar_scores_current", {})
    ev_with_notes = sum(1 for k, val in ev.items() if val.get("notes", "").strip())
    ev_with_urls = sum(1 for k, val in ev.items() if val.get("source_urls"))
    print(f"{name}: {len(scores)} scores, {len(ev)} evidence, {ev_with_notes} notes, {ev_with_urls} with URLs")
    for sp_id in ["TDR-01", "AIO-01"]:
        if sp_id in ev:
            e = ev[sp_id]
            notes = e.get("notes", "")[:150]
            urls = len(e.get("source_urls", []))
            print(f"  {sp_id} (score {scores.get(sp_id)}): {urls} URLs, notes: {notes}")

print(f"\nTotal vendors: {len(d['vendors'])}")
