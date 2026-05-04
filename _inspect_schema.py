"""Inspect schema structure for rationale generation."""
import json

schema = json.load(open("AI TriSM Schema 1_0.json", encoding="utf-8"))
print("Top keys:", list(schema.keys())[:5])

body = None
for k in schema:
    if "trism" in k.lower():
        body = schema[k]
        break

if body:
    subs = body.get("sub_pillars", {})
    for sid in ["GOV-01", "GOV-02", "RUN-01", "INF-01"]:
        info = subs.get(sid, {})
        print(f"\n{sid}:")
        print(f"  name: {info.get('name')}")
        defn = info.get("definition", "")
        print(f"  definition: {defn[:200]}")
        crit = info.get("ai_evaluation_criteria", [])
        print(f"  ai_evaluation_criteria ({len(crit)}): {crit[:4]}")
        levels = info.get("scoring_levels", {})
        for lev in ["1", "2", "3", "4", "5"]:
            lvl_text = levels.get(lev, "")
            if lvl_text:
                print(f"  level {lev}: {lvl_text[:150]}")
