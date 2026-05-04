"""Comprehensive check of v3-0 data: scores, rationale, evidence for all 8 SVC sub-pillars."""
import json

with open("Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json", "r", encoding="utf-8-sig") as f:
    vendors = json.load(f)

print(f"{len(vendors)} vendors\n")

svc_codes = ["EXM-05", "AMT-05", "ADR-05", "PPM-05", "SVC-01", "SVC-02", "SVC-03", "SVC-04"]
prc_codes = ["PRC-SUB", "PRC-USG", "PRC-FIX", "PRC-SUC", "PRC-COM", "PRC-OUT"]

# Check 3 sample vendors in detail
for vname in ["Tenable", "CrowdStrike", "ZeroFox"]:
    v = next(x for x in vendors if x["vendor"] == vname)
    print(f"{'='*70}")
    print(f"VENDOR: {vname}")
    print(f"{'='*70}")
    
    # 1. Scores
    scores = v.get("sub_pillar_scores_current", {})
    print(f"\n  SCORES ({len(scores)} sub-pillars):")
    for c in svc_codes:
        print(f"    {c}: {scores.get(c, 'MISSING')}")
    
    # 2. Evidence
    evidence = v.get("sub_pillar_evidence", {})
    print(f"\n  EVIDENCE ({len(evidence)} entries):")
    for c in svc_codes:
        ev = evidence.get(c, {})
        if ev:
            excerpts = ev.get("excerpts", [])
            st = ev.get("search_term_hits", ev.get("matched_search_terms", "?"))
            ct = ev.get("criteria_text_hits", ev.get("cooccurrence_pages", "?"))
            dm = ev.get("domain_term_hits", "N/A")
            notes = ev.get("notes", "")
            print(f"    {c}: {len(excerpts)} excerpts, st={st}, ct/cooc={ct}, dm={dm}")
            if excerpts:
                print(f"         First excerpt: {excerpts[0].get('excerpt','')[:120]}...")
        else:
            print(f"    {c}: NO EVIDENCE")
    
    # 3. Rationale
    rationale = v.get("sub_pillar_rationale_v2_consolidated", {})
    print(f"\n  RATIONALE ({len(rationale)} entries):")
    for c in svc_codes:
        r = rationale.get(c, "MISSING")
        if r and r != "MISSING":
            print(f"    {c}: {str(r)[:150]}...")
        else:
            print(f"    {c}: {r}")
    
    # 4. Pricing
    pscores = v.get("pricing_dimension_scores", {})
    prev = v.get("pricing_evidence", {})
    prat = v.get("pricing_rationales", {})
    print(f"\n  PRICING SCORES: {pscores}")
    print(f"  PRICING EVIDENCE: {len(prev)} dims with evidence")
    print(f"  PRICING RATIONALE: {len(prat)} dims with rationale")
    
    # 5. Pillar scores
    ps = v.get("pillar_scores", {})
    print(f"\n  PILLAR SCORES: {ps}")
    print(f"  Outcome: {v.get('outcome_maturity_label','?')} ({v.get('outcome_maturity_rating','?')})")
    print(f"  Coverage: {v.get('coverage_grade','?')} ({v.get('capability_coverage_count','?')}/24)")
    print()

# Summary: count how many vendors have all required data
print(f"\n{'='*70}")
print("COMPLETENESS CHECK")
print(f"{'='*70}")
missing_scores = 0
missing_evidence = 0
missing_rationale = 0
missing_pricing = 0
for v in vendors:
    scores = v.get("sub_pillar_scores_current", {})
    evidence = v.get("sub_pillar_evidence", {})
    rationale = v.get("sub_pillar_rationale_v2_consolidated", {})
    for c in svc_codes:
        if c not in scores:
            missing_scores += 1
        if c not in evidence:
            missing_evidence += 1
        if c not in rationale:
            missing_rationale += 1
    for c in prc_codes:
        if c not in v.get("pricing_dimension_scores", {}):
            missing_pricing += 1

print(f"  Missing SVC scores: {missing_scores}")
print(f"  Missing SVC evidence: {missing_evidence}")
print(f"  Missing SVC rationale: {missing_rationale}")
print(f"  Missing pricing scores: {missing_pricing}")
