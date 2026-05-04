"""Round all PMR vendor scores to 2 decimal places to fix floating-point artifacts."""
import json

with open('Product Market Readiness Vendor 1-0 Seed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def round_dict(d, decimals=2):
    return {k: round(v, decimals) if isinstance(v, float) else v for k, v in d.items()}

count = 0
for v in data['vendors']:
    if v.get('overall_gtm_score', 0) == 0:
        continue
    v['pillar_gtm_scores'] = round_dict(v.get('pillar_gtm_scores', {}))
    v['pillar_proof_scores'] = round_dict(v.get('pillar_proof_scores', {}))
    v['pillar_gaps'] = round_dict(v.get('pillar_gaps', {}))
    v['overall_gtm_score'] = round(v.get('overall_gtm_score', 0), 2)
    v['overall_proof_score'] = round(v.get('overall_proof_score', 0), 2)
    v['overall_credibility_gap'] = round(v.get('overall_credibility_gap', 0), 2)
    
    for sp_code, sp_data in v.get('sub_pillar_scores', {}).items():
        if isinstance(sp_data, dict):
            for field in ['gtm_messaging_score', 'proof_of_execution_score', 'credibility_gap']:
                if field in sp_data and isinstance(sp_data[field], float):
                    sp_data[field] = round(sp_data[field], 1)
    count += 1

with open('Product Market Readiness Vendor 1-0 Seed.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Rounded scores for {count} vendors")
