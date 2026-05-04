"""Dump vendor names, service types, and description snippets for delivery_model classification."""
import json

with open("MDR Services Vendor 2-1 Consolidated.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for v in data["vendors"]:
    name = v.get("vendor", "?")
    stype = v.get("mdr_service_type", "?")
    desc = v.get("description", "")[:150]
    kdiff = v.get("key_differentiators", "")[:150]
    print(f"--- {name} [{stype}]")
    print(f"  DESC: {desc}")
    print(f"  DIFF: {kdiff}")
