import json
d = json.load(open("Preemptive Cybersecurity Vendor 1-0 Seed.json"))
for i, v in enumerate(d["vendors"]):
    print(f"{i+1}. {v['vendor']} ({v['primary_capability']})")
