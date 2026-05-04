"""Inspect PreCyber vendor data and check for cached pages."""
import json, os

with open("Preemptive Cybersecurity Vendor 2-1 Consolidated.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)

vendors = data if isinstance(data, list) else data.get("vendors", [data])
print("Type:", type(data).__name__)
print("Vendors:", len(vendors))

if vendors:
    v = vendors[0]
    print("First vendor:", v.get("vendor", "?"))
    print("Keys:", sorted(v.keys()))
    sps = v.get("sub_pillar_scores_current", {})
    print("Sub-pillar codes:", sorted(sps.keys()))
    print("Has SVC codes:", any(k.startswith("SVC") for k in sps.keys()))

    # List all vendors
    print("\n--- ALL VENDORS ---")
    for i, vv in enumerate(vendors):
        name = vv.get("vendor", "?")
        grade = vv.get("coverage_grade", "?")
        print("%2d. %s (grade: %s)" % (i+1, name, grade))

# Check for cached pages
for cache_dir in ["research/cache/pages_precyber", "research/cache", "research"]:
    if os.path.exists(cache_dir):
        contents = os.listdir(cache_dir)
        print("\nCache dir '%s': %d items" % (cache_dir, len(contents)))
        if len(contents) <= 20:
            for item in contents:
                print("  ", item)
        break
else:
    print("\nNo research cache found")
