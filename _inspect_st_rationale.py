import json

d = json.load(open('MDR Services Vendor 2-1 Consolidated.json', encoding='utf-8'))
cs = [v for v in d['vendors'] if v['vendor'] == 'CrowdStrike'][0]

for key in ['sub_pillar_rationale_v2', 'sub_pillar_rationale_v2_1', 'sub_pillar_rationale_v2_1_text', 'sub_pillar_rationale_v2_consolidated']:
    val = cs[key]['TDR-01']
    print(f'--- {key} [TDR-01] ---')
    if isinstance(val, dict):
        print(json.dumps(val, indent=2)[:600])
    else:
        print(str(val)[:400])
    print()

print('--- evidence_quality_summary ---')
print(cs['evidence_quality_summary'][:300])
print()
print('--- capability_analysis ---')
print(cs['capability_analysis'][:300])
print()
print('--- notable_differentiation ---')
print(cs['notable_differentiation'][:300])
print()
print('--- notable_differentiation_v2_1 ---')
print(cs['notable_differentiation_v2_1'][:300])
print()
print('--- v2_1_adjustment_summary ---')
print(json.dumps(cs['v2_1_adjustment_summary'], indent=2)[:500])
print()
print('--- research_confidence ---', cs['research_confidence'])
print('--- research_confidence_v2_1 ---', cs['research_confidence_v2_1'])
print('--- delivery_model ---', cs['delivery_model'])
