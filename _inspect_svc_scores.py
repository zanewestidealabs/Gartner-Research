"""Examine SVC scores, rationale and evidence for key vendors."""
import json

with open("Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json", "r", encoding="utf-8") as f:
    vendors = json.load(f)

for name in ["Tenable", "CrowdStrike", "Palo Alto Networks", "Qualys", "Arctic Wolf", "Rapid7"]:
    v = next((x for x in vendors if x.get("vendor","") == name), None)
    if not v:
        continue
    print(f"\n{'='*60}")
    print(f"=== {name} ===")
    print(f"{'='*60}")

    # SVC scores
    sps = v.get("sub_pillar_scores_current", {})
    ps = v.get("pillar_scores", {})
    print(f"\nSVC Pillar Score: {ps.get('SVC', '?')}")
    for k in sorted(sps):
        if k.startswith("SVC"):
            print(f"  {k}: {sps[k]}")

    # Description / capability analysis
    desc = v.get("description", v.get("capability_analysis", ""))
    if desc:
        print(f"\nDescription (first 300 chars):")
        print(f"  {desc[:300]}")

    # SVC Rationale
    rat = v.get("sub_pillar_rationale_v2_consolidated", {})
    for k in sorted(rat):
        if k.startswith("SVC"):
            r = rat[k]
            txt = r if isinstance(r, str) else r.get("score_rationale", r.get("rationale", str(r)))
            print(f"\n--- {k} Rationale ---")
            print(f"  {txt[:500]}")

    # SVC Evidence excerpts
    ev = v.get("sub_pillar_evidence", {})
    for k in sorted(ev):
        if k.startswith("SVC"):
            e = ev[k]
            excerpts = e.get("excerpts", []) if isinstance(e, dict) else []
            urls = e.get("source_urls", []) if isinstance(e, dict) else []
            print(f"\n--- {k} Evidence: {len(excerpts)} excerpts ---")
            for ex in excerpts[:2]:
                txt = ex if isinstance(ex, str) else ex.get("excerpt", ex.get("text", ""))
                print(f"  >> {str(txt)[:250]}")
            if urls:
                print(f"  URLs: {urls[:3]}")

    # Pricing model info
    pmt = v.get("pricing_model_type", "")
    oml = v.get("outcome_maturity_label", "")
    omr = v.get("outcome_maturity_rating", "")
    sml = v.get("services_maturity_level", "")
    print(f"\nPricing Model Type: {pmt}")
    print(f"Outcome Maturity: {omr} ({oml})")
    print(f"Services Maturity Level: {sml}")
