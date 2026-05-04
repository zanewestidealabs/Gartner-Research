import json

with open('Offensive Security Vendor 1-0 Seed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

vendors = data['vendors']
print(f"Total vendors: {len(vendors)}")
print(f"Schema: {data['schema_file']}")
print()

# Count by vendor type
types = {}
for v in vendors:
    t = v.get('vendor_type', 'Unknown')
    types[t] = types.get(t, 0) + 1
print("By vendor type:")
for t, c in sorted(types.items()):
    print(f"  {t}: {c}")

# Count by primary capability
caps = {}
for v in vendors:
    c = v.get('primary_capability', 'Unknown')
    caps[c] = caps.get(c, 0) + 1
print("\nBy primary capability:")
for c, n in sorted(caps.items()):
    print(f"  {c}: {n}")

# Count by AI maturity
ai = {}
for v in vendors:
    level = v.get('ai_maturity_level', 0)
    ai[level] = ai.get(level, 0) + 1
print("\nBy AI maturity level:")
for level in sorted(ai.keys()):
    print(f"  Level {level}: {ai[level]} vendors")

# Count by region
regions = {}
for v in vendors:
    r = v.get('region', 'Unknown')
    regions[r] = regions.get(r, 0) + 1
print("\nBy region:")
for r, c in sorted(regions.items()):
    print(f"  {r}: {c}")

# Coverage stats
print("\nCapability coverage per vendor:")
for v in vendors:
    cov = v.get('capability_coverage', [])
    pillars_covered = set(c[:3] for c in cov)
    print(f"  {v['vendor']:45s} {len(cov):2d} sub-pillars  {len(pillars_covered)} pillars  [{', '.join(sorted(pillars_covered))}]")

# Verify all sub-pillar IDs are valid
valid_ids = set()
for prefix in ['ASM', 'VUL', 'OFT', 'APP', 'REM']:
    for i in range(1, 6):
        valid_ids.add(f"{prefix}-{i:02d}")

invalid = []
for v in vendors:
    for c in v.get('capability_coverage', []):
        if c not in valid_ids:
            invalid.append((v['vendor'], c))

if invalid:
    print(f"\nINVALID sub-pillar IDs found:")
    for vendor, sid in invalid:
        print(f"  {vendor}: {sid}")
else:
    print(f"\nAll sub-pillar IDs valid ({len(valid_ids)} possible)")

print("\nVALID JSON - Seed file created successfully!")
