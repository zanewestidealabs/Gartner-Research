import json
with open("analyst_take_reports.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)
r = data["reports"][3]
print("Keys:", list(r.keys()))
print("body_sections count:", len(r.get("body_sections", [])))
for i, s in enumerate(r["body_sections"]):
    print(f"  section {i} keys: {list(s.keys())}")
print("positioning_statements count:", len(r.get("positioning_statements", [])))
for i, p in enumerate(r.get("positioning_statements", [])):
    print(f"  stmt {i} keys: {list(p.keys())}")
    if "positionComponents" in p:
        print(f"    positionComponents keys: {list(p['positionComponents'].keys())}")
    if "justification" in p:
        print(f"    justification keys: {list(p['justification'].keys())}")
    if "actions" in p:
        print(f"    actions[0] keys: {list(p['actions'][0].keys())}")
    if "alignment" in p:
        print(f"    alignment keys: {list(p['alignment'].keys())}")
print("graphics count:", len(r.get("graphics", [])))
print("recommended_reading count:", len(r.get("recommended_reading", [])))
