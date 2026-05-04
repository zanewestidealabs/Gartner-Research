import json, os

fp = 'MDR Services Vendor Pricing 2-0 Researched.json'
sz = os.path.getsize(fp)
print(f'FILE_SIZE_MB={sz/1048576:.2f}')

with open(fp, 'r', encoding='utf-8-sig') as f:
    d = json.load(f)

vs = d['vendors']
print(f'VENDORS={len(vs)}')

v0 = vs[0]
# Check what name key is used
name_key = 'vendor_name' if 'vendor_name' in v0 else 'name' if 'name' in v0 else list(v0.keys())[:5]
print(f'NAME_KEY={name_key}')
vname = v0.get('vendor_name', v0.get('name', 'UNKNOWN'))
print(f'V0={vname}')
print(f'ALL_KEYS={sorted(v0.keys())}')
# Check evidence structure
ev0 = v0.get('pricing_dimension_evidence', {})
print(f'EVIDENCE_KEYS={sorted(ev0.keys()) if ev0 else "NONE"}')
# Check pricing_evidence
pe = v0.get('pricing_evidence', {})
if pe:
    pk0 = list(pe.keys())[0] if pe else ''
    print(f'PRICING_EV_KEYS={list(pe.keys())}')
    if pk0:
        pev0 = pe[pk0]
        print(f'PRICING_EV_SAMPLE_KEYS={sorted(pev0.keys()) if isinstance(pev0,dict) else type(pev0)}')
pds = v0.get('pricing_dimension_scores_v2', v0.get('pricing_dimension_scores', {}))
print(f'DIM_SCORES={pds}')
print(f'OVERALL={v0.get("pricing_overall_score_v2")}')
print(f'OMR={v0.get("outcome_maturity_rating_v2")}')
print(f'HAS_RAT={"pricing_dimension_rationale_v2_text" in v0}')
print(f'HAS_ADJ={"pricing_adjustment_summary" in v0}')
print(f'HAS_CONF={"pricing_research_confidence" in v0}')

te = 0
for v in vs:
    ev = v.get('pricing_dimension_evidence', {})
    for dim, info in ev.items():
        te += len(info.get('excerpts', []))
wr = sum(1 for v in vs if v.get('pricing_dimension_rationale_v2_text'))
print(f'TOTAL_EXCERPTS={te}')
print(f'VENDORS_WITH_RATIONALE={wr}')

# Sample a few vendors
for v in [vs[0], vs[30], vs[60], vs[92]]:
    name = v.get('vendor_name', v.get('name', 'UNKNOWN'))
    pds2 = v.get('pricing_dimension_scores_v2', v.get('pricing_dimension_scores', {}))
    ovr = v.get('pricing_overall_score_v2', v.get('pricing_overall_score', 0))
    omr = v.get('outcome_maturity_rating_v2', v.get('outcome_maturity_rating', 0))
    nexc = sum(len(ev.get('excerpts', [])) for ev in v.get('pricing_dimension_evidence', {}).values())
    print(f'  {name}: overall={ovr}, omr={omr}, excerpts={nexc}, dims={pds2}')
