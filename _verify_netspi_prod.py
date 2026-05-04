import json
d = json.load(open("/home/vm-ssh/gartner/Product Market Readiness Vendor 1-1 Enriched.json"))
ns = [v for v in d["vendors"] if v["vendor"] == "NetSPI"]
print("vendor_count:", d["vendor_count"])
print("NetSPI found:", len(ns))
if ns:
    v = ns[0]
    print("type:", v["vendor_type"])
    print("sub_pillars:", len(v["sub_pillar_scores"]))
    print("gtm:", v["overall_gtm_score"])
    print("proof:", v["overall_proof_score"])
