"""Quick spot check of enriched PMR evidence quality."""
import json
import random

with open("Product Market Readiness Vendor 1-0 Seed.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)

vendors = data["vendors"]

# Pick 5 vendors that have excerpts
enriched = [v for v in vendors if any(sp.get("excerpts") for sp in v.get("sub_pillar_scores", {}).values())]
samples = random.sample(enriched, min(5, len(enriched)))

for sv in samples:
    name = sv["vendor"]
    print(f"\n{'='*60}")
    print(f"VENDOR: {name}")
    for sp_code in ["PPD-01", "PCS-02", "TDT-03", "CTL-01"]:
        sp = sv["sub_pillar_scores"].get(sp_code, {})
        print(f"\n  {sp_code}:")
        print(f"    GTM={sp.get('gtm_messaging_score')}, Proof={sp.get('proof_of_execution_score')}")
        gt = sp.get("gtm_rationale", "")
        print(f"    GTM rationale: {gt[:200]}")
        pr = sp.get("proof_rationale", "")
        print(f"    Proof rationale: {pr[:200]}")
        ga = sp.get("gap_assessment", "")
        print(f"    Gap: {ga[:150]}")
        exc = sp.get("excerpts", [])
        print(f"    Excerpts: {len(exc)}")
        if exc:
            print(f"      [0] rel={exc[0].get('relevance_score')}: {exc[0].get('excerpt','')[:120]}")
        urls = sp.get("source_urls", [])
        print(f"    URLs: {len(urls)}")
        em = sp.get("evidence_metadata", {})
        print(f"    Evidence: {em.get('evidence_strength')}, refs={em.get('source_schema_refs',[])} ")

# Check the 20 vendors with no evidence
no_ev = [v["vendor"] for v in vendors if not any(sp.get("excerpts") for sp in v.get("sub_pillar_scores", {}).values())]
print(f"\n{'='*60}")
print(f"Vendors with NO excerpts ({len(no_ev)}):")
for v in no_ev:
    print(f"  - {v}")
