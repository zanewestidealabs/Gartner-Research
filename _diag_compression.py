"""Deep dive: list vendor mix by archetype, then inspect one tech (CrowdStrike)
and one services (Arctic Wolf) vendor to see WHY scores compress to ~1.0.
"""
from __future__ import annotations
import json, re

DATA = json.load(open("Preemptive Cybersecurity Vendor 2-3 Holistic Validated.json", encoding="utf-8"))
SCHEMA = json.load(open("Preemptive_Cybersecurity_Schema_v2.json", encoding="utf-8"))
SUB = SCHEMA["preemptive_cybersecurity_taxonomy_v2.0"]["sub_pillars"]

print("=== Vendor list (52) ===")
for i, v in enumerate(sorted(DATA["vendors"], key=lambda x: (x.get("vendor") or "")), 1):
    name = v.get("vendor") or "?"
    cat = v.get("vendor_category") or v.get("category") or v.get("classification") or ""
    print(f"  {i:2d}. {name:<35s}  {cat}")

# Are PwC / Accenture / Deloitte / EY / KPMG present?
big4 = ["pwc", "pricewaterhousecoopers", "accenture", "deloitte", "kpmg", "ernst & young", " ey "]
present = [v.get("vendor") for v in DATA["vendors"] if any(b in (v.get("vendor") or "").lower() for b in big4)]
print("\nBig consultancies present:", present or "NONE")

# MDR/MSSP-flavored vendors present?
mssp_terms = ["mssp", "mdr", "managed", "service"]
mssp_present = []
for v in DATA["vendors"]:
    n = (v.get("vendor") or "").lower()
    cat = (v.get("vendor_category") or "").lower()
    if any(t in cat for t in mssp_terms):
        mssp_present.append(v.get("vendor"))
print("Service-led vendors (by category):", mssp_present or "n/a (no category field)")


def deep_dive(vname: str, sids: list[str]):
    v = next((x for x in DATA["vendors"] if vname.lower() in (x.get("vendor") or "").lower()), None)
    if not v:
        print(f"\n!! {vname} not found")
        return
    print(f"\n{'='*70}\nDEEP DIVE: {v['vendor']}\n{'='*70}")
    sps = v.get("sub_pillar_scores_current") or {}
    rats = v.get("sub_pillar_rationale_v2") or {}
    ev = v.get("sub_pillar_evidence") or {}
    for sid in sids:
        sp_def = SUB.get(sid, {})
        s = sps.get(sid)
        r = rats.get(sid) or {}
        eb = ev.get(sid) or {}
        excerpts = eb.get("excerpts") or []
        srcs = {e.get("url") for e in excerpts if isinstance(e, dict)}
        srcs.discard(None)
        print(f"\n--- {sid}  {sp_def.get('name','?')}  | score={s} | level={r.get('scoring_level')} | conf={r.get('confidence')} ---")
        print(f"  excerpts={len(excerpts)} sources={len(srcs)}")
        print(f"  search_terms: {sp_def.get('search_terms', [])[:6]}")
        for c in r.get("criteria_assessment", []):
            print(f"   [{c['status']:7s}] {c['criterion']}")
            if c.get("evidence"):
                print(f"           ev: {c['evidence'][:140]}")
        print("  raw excerpts (lengths):")
        for ex in excerpts:
            t = (ex.get("excerpt") or ex.get("text") or "").strip().replace("\n", " ")
            print(f"    [{len(t):4d}] {t[:160]}")


# Tech archetype: CrowdStrike (should be strong ADR/AMT)
deep_dive("CrowdStrike", ["ADR-01", "ADR-02", "AMT-01", "AMT-04"])

# Services archetype: Arctic Wolf (should be strong SVC, moderate ADR)
deep_dive("Arctic Wolf", ["SVC-01", "SVC-02", "SVC-03", "ADR-01"])
