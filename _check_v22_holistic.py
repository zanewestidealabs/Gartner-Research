import json
d = json.load(open("Preemptive Cybersecurity Vendor 2-3 Holistic Validated.json", encoding="utf-8"))
for vname in ["Mandiant", "HashiCorp", "Group-IB", "Trellix"]:
    v = next((x for x in d["vendors"] if vname in (x.get("vendor") or "")), None)
    if not v:
        continue
    print("===", v["vendor"], "===")
    for sid in ["EXM-04", "EXM-01", "ADR-01", "SVS-01", "AMT-01"]:
        r = v["sub_pillar_rationale_v2"].get(sid)
        s = v["sub_pillar_scores_current"].get(sid)
        if not r:
            continue
        cs = r["criteria_assessment"]
        m = sum(1 for c in cs if c["status"] == "met")
        p = sum(1 for c in cs if c["status"] == "partial")
        u = sum(1 for c in cs if c["status"] == "unmet")
        print(f"  {sid}: {s} | met={m} partial={p} unmet={u} | grade={r['evidence_quality_grade']} | conf={r['confidence']} | excerpts={r['excerpt_count']}")
        if vname == "Mandiant" and sid == "EXM-04":
            print("    rationale:", r["score_rationale"][:200])
            for c in cs:
                print(f"    [{c['status']:7s}] {c['criterion'][:60]}")
                if c["evidence"]:
                    print(f"             ev: {c['evidence'][:100]}")
