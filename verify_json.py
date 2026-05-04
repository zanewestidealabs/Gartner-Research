import json

with open('vendor3-3.json') as f:
    data = json.load(f)

print(f'✅ Valid JSON')
print(f'✅ Vendor count: {len(data)}')
print(f'✅ First vendor: {data[0]["vendor"]}')
print(f'✅ Fields: {list(data[0].keys())}')

# Show sample vendor data
print(f'\n✅ Sample vendor data:')
print(f'   Vendor: {data[0]["vendor"]}')
print(f'   Region: {data[0]["region"]}')
print(f'   Pillar Scores: {data[0]["pillar_scores"]}')
