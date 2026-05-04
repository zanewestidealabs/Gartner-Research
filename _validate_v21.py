import json

with open("Offensive Security Vendor 2-1 Consolidated.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Version: {data['seed_version']}")
print(f"Date: {data['seed_date']}")
print(f"Vendors: {len(data['vendors'])}")
print()

total_scored = 0
total_zero = 0
total_evidence = 0
total_sources = 0

for v in data["vendors"]:
    for sp, score in v["sub_pillar_scores_current"].items():
        if score > 0:
            total_scored += 1
        else:
            total_zero += 1
    for sp, ev in v.get("sub_pillar_evidence", {}).items():
        total_evidence += 1
        total_sources += len(ev.get("sources", []))

print(f"Scored cells: {total_scored}/{total_scored + total_zero}")
print(f"Zero cells: {total_zero}")
print(f"Evidence entries: {total_evidence}")
print(f"Source citations: {total_sources}")
print(f"Avg sources/evidence: {total_sources/total_evidence:.1f}")
print()

# File size
import os
size = os.path.getsize("Offensive Security Vendor 2-1 Consolidated.json")
print(f"File size: {size:,} bytes ({size/1024:.0f} KB)")
print()

# Spot check
for name in ["Wiz", "Snyk", "Cobalt", "SafeBreach", "Astra Security"]:
    v = next((x for x in data["vendors"] if x["vendor"] == name), None)
    if not v:
        print(f"{name}: NOT FOUND")
        continue
    ev_count = len(v.get("sub_pillar_evidence", {}))
    src_count = sum(len(e.get("sources", [])) for e in v.get("sub_pillar_evidence", {}).values())
    empty = sum(1 for e in v.get("sub_pillar_evidence", {}).values() if not e.get("sources"))
    print(f"{name}: {ev_count} evidence, {src_count} sources, {empty} empty")

    first_sp = list(v.get("sub_pillar_evidence", {}).keys())[0]
    ev = v["sub_pillar_evidence"][first_sp]
    print(f"  {first_sp} rationale: {ev['rationale'][:120]}...")
    print(f"  First source: {ev['sources'][0]['title']}")
    print()
