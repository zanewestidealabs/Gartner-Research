"""Merge capability + pricing data into the MDR seed file."""
import json

# Load the three files
with open('MDR Services Vendor 1-0 Seed.json', 'r', encoding='utf-8-sig') as f:
    seed = json.load(f)
with open('MDR Services Vendor Capability 1-0 Seed.json', 'r', encoding='utf-8-sig') as f:
    cap = json.load(f)
with open('MDR Services Vendor Pricing 1-0 Seed.json', 'r', encoding='utf-8-sig') as f:
    pricing = json.load(f)

# Build lookups by vendor name
cap_lookup = {v['vendor']: v for v in cap['vendors']}
price_lookup = {v['vendor']: v for v in pricing['vendors']}

# Fields to copy from capability
CAP_FIELDS = [
    'pillar_scores', 'sub_pillar_scores_current', 'sub_pillar_schema_labels',
    'sub_pillar_evidence', 'capability_coverage', 'capability_analysis',
    'research_status'
]
# Fields to copy from pricing
PRICE_FIELDS = [
    'pricing_dimension_scores', 'pricing_dimension_labels', 'pricing_overall_score',
    'outcome_maturity_rating', 'pricing_evidence', 'outcome_evidence',
    'pricing_analysis', 'pricing_model_details'
]

merged_count = 0
for vendor in seed['vendors']:
    name = vendor['vendor']
    # Merge capability data
    if name in cap_lookup:
        cv = cap_lookup[name]
        for field in CAP_FIELDS:
            if field in cv:
                vendor[field] = cv[field]
    # Merge pricing data
    if name in price_lookup:
        pv = price_lookup[name]
        for field in PRICE_FIELDS:
            if field in pv:
                vendor[field] = pv[field]
    if name in cap_lookup or name in price_lookup:
        merged_count += 1

# Add schema_ref
seed['schema_ref'] = 'MDR_Services_Schema.json'

with open('MDR Services Vendor 1-0 Seed.json', 'w', encoding='utf-8') as f:
    json.dump(seed, f, indent=2, ensure_ascii=False)

print(f"Merged {merged_count} vendors with capability + pricing data")
print(f"Total vendors in seed: {len(seed['vendors'])}")
# Quick validation
v0 = seed['vendors'][0]
print(f"First vendor: {v0['vendor']}")
print(f"  Has pillar_scores: {'pillar_scores' in v0}")
print(f"  Has sub_pillar_scores_current: {'sub_pillar_scores_current' in v0}")
print(f"  Has pricing_dimension_scores: {'pricing_dimension_scores' in v0}")
print(f"  pillar_scores: {v0.get('pillar_scores', {})}")
