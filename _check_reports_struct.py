import json
with open("analyst_take_reports.json", "r", encoding="utf-8-sig") as f:
    d = json.load(f)
print(type(d))
if isinstance(d, list):
    print(f"Array with {len(d)} reports")
    for i, r in enumerate(d):
        print(f"  {i}: id={r.get('id')}, schema={r.get('schema_ref','')}")
elif isinstance(d, dict):
    print(f"Keys: {list(d.keys())}")
    reports = d.get("reports", d.get("analyst_takes", []))
    print(f"Reports: {len(reports)}")
    for i, r in enumerate(reports):
        print(f"  {i}: id={r.get('id')}, schema={r.get('schema_ref','')}")
