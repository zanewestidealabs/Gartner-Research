import json
import re

with open("analyst_take_reports.json", "r", encoding="utf-8-sig") as f:
    d = json.load(f)

print("Valid JSON. Reports:")
for r in d["reports"]:
    print(f"  {r['id']} -> schema={r.get('schema_ref','None')} -> {r['label'][:70]}")

v3 = [r for r in d["reports"] if r["id"] == "aiuc1-agentic-compliance-v3-cpo"][0]
print(f"\nv3 body_sections: {len(v3['body_sections'])}")
for s in v3["body_sections"]:
    print(f"  - {s['heading']}")
print(f"v3 positioning_statements: {len(v3['positioning_statements'])}")
for p in v3["positioning_statements"]:
    print(f"  - {p['id']}: {p['label']}")

# Check for first-person healthcare org references
issues = []
for s in v3["body_sections"]:
    body_lower = s["body"].lower()
    if "our data" in body_lower:
        issues.append(f"Body '{s['heading']}' has 'our data'")
    if "our phi" in body_lower:
        issues.append(f"Body '{s['heading']}' has 'our PHI'")
    if re.search(r"whether you.re a 50-person clinic", body_lower):
        issues.append(f"Body '{s['heading']}' has buyer-side clinic framing")

if issues:
    print(f"\nISSUES FOUND: {issues}")
else:
    print("\nNo first-person healthcare-org references found. CPO framing verified.")
