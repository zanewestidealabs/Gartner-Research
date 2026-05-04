import json
with open("/home/vm-ssh/gartner/MDR Services Vendor 2-1 Consolidated.json") as f:
    d = json.load(f)
for v in d["vendors"]:
    if "proficio" in v["vendor"].lower():
        print("Vendor:", v.get("vendor"))
        print("Status:", v.get("research_status"))
        print("Confidence:", v.get("research_confidence_v2_1"))
        p21 = v.get("pillar_scores_v2_1", {})
        for k in sorted(p21):
            print(f"  {k}: {p21[k]}")
        break
