"""Verify v2.1 consolidated output structure and sample rationale."""
import json

with open("Preemptive Cybersecurity Vendor 2-1 Consolidated.json", encoding="utf-8") as f:
    d = json.load(f)

v = d["vendors"][0]
print(f"Vendor: {v['vendor']}")
print(f"Has vendor_summary_v2_1: {'vendor_summary_v2_1' in v}")
summary = v.get("vendor_summary_v2_1", {})
print(f"Coverage: {summary.get('coverage_count','?')} = {summary.get('coverage_grade','?')}")
print(f"Quality: {summary.get('quality_avg','?'):.2f} = {summary.get('quality_grade','?')}")
print(f"Pillar avgs: {summary.get('pillar_averages',{})}")

rat = v.get("sub_pillar_rationale_v2_consolidated", {})
print(f"Has consolidated rationale: {len(rat)} sub-pillars")

first_key = list(rat.keys())[0] if rat else None
if first_key:
    print(f"\nSample rationale ({first_key}):")
    print(rat[first_key][:600])
