"""Verify PMR scoring results and check remaining work."""
import json
import os
from collections import Counter

with open('Product Market Readiness Vendor 1-0 Seed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
vendors = data['vendors']

scored = [v for v in vendors if v.get('overall_gtm_score', 0) > 0]
unscored = [v for v in vendors if v.get('overall_gtm_score', 0) == 0]
print(f'Total: {len(vendors)}, Scored: {len(scored)}, Unscored: {len(unscored)}')

# Verify CrowdStrike
cs = [v for v in vendors if v['vendor'] == 'CrowdStrike'][0]
print(f'\nCrowdStrike:')
print(f'  GTM={cs["overall_gtm_score"]}, Proof={cs["overall_proof_score"]}, Gap={cs["overall_credibility_gap"]}, Grade={cs["coverage_grade"]}')
print(f'  Pillar GTM: {cs["pillar_gtm_scores"]}')
print(f'  Pillar Proof: {cs["pillar_proof_scores"]}')
sp01 = cs['sub_pillar_scores']['PPD-01']
print(f'  PPD-01: gtm={sp01["gtm_messaging_score"]}, proof={sp01["proof_of_execution_score"]}')
print(f'  PPD-01 gtm_rationale: {sp01["gtm_rationale"][:120]}')
print(f'  PPD-01 source_urls: {sp01["source_urls"][:2]}')

# Check Secure by Design
sbd_files = [f for f in os.listdir('.') if 'secure' in f.lower() and 'vendor' in f.lower()]
print(f'\nSecure by Design vendor files: {sbd_files}')

# Unscored schema distribution  
schema_counts = Counter()
for v in unscored:
    for s in v.get('source_schemas', []):
        schema_counts[s] += 1
print(f'\nUnscored vendor schema distribution: {dict(schema_counts)}')

# Single-schema vendors that could still be scored
single_schema_unscored = Counter()
for v in unscored:
    schemas = v.get('source_schemas', [])
    if len(schemas) == 1:
        single_schema_unscored[schemas[0]] += 1
print(f'Single-schema unscored: {dict(single_schema_unscored)}')
