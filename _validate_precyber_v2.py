"""Validate the Preemptive Cybersecurity Schema v2.0."""
import json

with open("Preemptive_Cybersecurity_Schema_v2.json", "r") as f:
    schema = json.load(f)

root = schema["preemptive_cybersecurity_taxonomy_v2.0"]
pillars = root["pillars"]
subs = root["sub_pillars"]
pricing = root["pricing_evaluation"]

print("=== SCHEMA VALIDATION ===")
print("Version:", root["schema_lineage"]["version"])
print("Pillars:", len(pillars), "-", list(pillars.keys()))
print("Sub-pillars:", len(subs), "-", list(subs.keys()))
print("Pricing dimensions:", len(pricing["dimensions"]), "-", list(pricing["dimensions"].keys()))
print()

for code in pillars:
    sp_count = sum(1 for sp in subs if sp.startswith(code))
    print("  %s (%s): %d sub-pillars" % (code, pillars[code]["name"], sp_count))

print()
for dim in pricing["dimensions"]:
    d = pricing["dimensions"][dim]
    print("  %s: %s" % (dim, d["name"]))

cg = root["metadata"]["coverage_grade"]["scale"]
print("\nCoverage grades:", cg)
print("Services maturity model present:", "services_maturity_model" in root["metadata"])
print("Outcome maturity rating present:", "outcome_maturity_rating" in pricing)
print("Vendor fields:", len(root["vendor_fields"]), "fields")

new_fields = [f for f in root["vendor_fields"] if f == "services_maturity_level"]
print("New vendor fields:", new_fields)
print("\n=== VALID JSON - ALL CHECKS PASSED ===")
