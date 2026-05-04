import json, re

with open("analyst_take_reports.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)
v3 = [r for r in data["reports"] if r["id"]=="aiuc1-agentic-compliance-v3-cpo"][0]

for i, s in enumerate(v3["body_sections"]):
    print(f"=== SECTION {i}: {s['heading']} ===")
    print(s["body"])
    print()

# Contractions
for i, s in enumerate(v3["body_sections"]):
    for m in re.finditer(r"\w+['\u2019]\w+", s["body"]):
        print(f"  S{i} body contraction: {m.group()}")
    for m in re.finditer(r"\w+['\u2019]\w+", s["heading"]):
        print(f"  S{i} heading contraction: {m.group()}")

# Label and subtitle
print(f"\nLabel: {v3['label']}")
print(f"Subtitle: {v3['subtitle']}")
