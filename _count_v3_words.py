import json

with open("analyst_take_reports.json", "r", encoding="utf-8-sig") as f:
    d = json.load(f)

v3 = [r for r in d["reports"] if r["id"] == "aiuc1-agentic-compliance-v3-cpo"][0]
total = 0
for s in v3["body_sections"]:
    wc = len(s["body"].split())
    total += wc
    print(f"  {wc:4d} words: {s['heading']}")
print(f"\nTotal body: {total} words")
print(f"Target: under 900 words")
print(f"Delta: {total - 900}")
