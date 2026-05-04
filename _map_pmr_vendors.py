"""Map vendors across all schemas for PMR cross-schema scoring."""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))

def load_vendors(fname):
    """Load vendor list from a JSON file."""
    path = os.path.join(BASE, fname)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for k, v in data.items():
        if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict) and 'vendor' in v[0]:
            return v
    return []

# Source schema files (use consolidated/researched versions)
SOURCE_FILES = {
    'ai_trism': 'AI TRiSM Vendor 2-1 Consolidated.json',
    'mdr_services': 'MDR Services Vendor 2-0 Researched.json',
    'preemptive_cyber': 'Preemptive Cybersecurity Vendor 2-1 Consolidated.json',
    'offensive_security': 'Offensive Security Vendor 2-0 Researched.json',
}

# Try to find Secure by Design file
sbd_candidates = [
    'Secure by Design Vendor 2-0 Scored.json',
    'Secure by Design Vendor 2-0 Researched.json',
    'Secure by Design Vendor 1-0 Seed.json',
]
for c in sbd_candidates:
    if os.path.exists(os.path.join(BASE, c)):
        SOURCE_FILES['secure_by_design'] = c
        break

print("=" * 60)
print("SOURCE SCHEMA FILES")
print("=" * 60)
for k, v in SOURCE_FILES.items():
    vendors = load_vendors(v)
    print(f"\n{k}: {v}")
    print(f"  Vendor count: {len(vendors)}")
    if vendors:
        v0 = vendors[0]
        # Show score structure
        score_keys = [k2 for k2 in v0.keys() if 'score' in k2.lower() or 'pillar' in k2.lower()]
        print(f"  Score-related keys: {score_keys}")
        
        # Get sub-pillar score structure
        for skey in ['sub_pillar_scores_current', 'sub_pillar_scores']:
            sdata = v0.get(skey, {})
            if sdata:
                first_sp = list(sdata.keys())[0]
                first_val = sdata[first_sp]
                print(f"  {skey} -> first sub-pillar: {first_sp}")
                if isinstance(first_val, dict):
                    print(f"    Keys: {list(first_val.keys())[:10]}")
                    score_val = first_val.get('score', first_val.get('current_score', 'N/A'))
                    print(f"    Score value: {score_val}")
                else:
                    print(f"    Value: {first_val}")
                break
        
        # Show 5 vendor names
        names = [x['vendor'] for x in vendors[:5]]
        print(f"  Sample vendors: {names}")

# Load PMR seed
print("\n" + "=" * 60)
print("PMR SEED FILE")
print("=" * 60)
pmr_vendors = load_vendors('Product Market Readiness Vendor 1-0 Seed.json')
print(f"Total PMR vendors: {len(pmr_vendors)}")

# Map PMR vendors to their source schemas
pmr_by_schema = {}
for v in pmr_vendors:
    for src in v.get('source_schemas', []):
        pmr_by_schema.setdefault(src, []).append(v['vendor'])

print("\nPMR vendors by source schema:")
for schema, names in sorted(pmr_by_schema.items()):
    print(f"  {schema}: {len(names)} vendors")

# Find overlaps between PMR vendors and actual source vendor files
print("\n" + "=" * 60)
print("VENDOR OVERLAP ANALYSIS")
print("=" * 60)

pmr_names = {v['vendor'].lower(): v['vendor'] for v in pmr_vendors}

for schema_key, fname in SOURCE_FILES.items():
    source_vendors = load_vendors(fname)
    source_names = {v['vendor'].lower(): v['vendor'] for v in source_vendors}
    
    # Find exact matches
    exact = set(pmr_names.keys()) & set(source_names.keys())
    
    print(f"\n{schema_key} ({len(source_vendors)} source vendors):")
    print(f"  Exact name matches with PMR: {len(exact)}")
    
    # Show first 8 matched vendor names
    matched = sorted([source_names[n] for n in list(exact)[:8]])
    print(f"  Sample matches: {matched}")

# Find multi-schema vendors
print("\n" + "=" * 60)
print("MULTI-SCHEMA VENDORS (appear in 2+ source schemas)")
print("=" * 60)

multi = [(v['vendor'], v.get('source_schemas', [])) 
         for v in pmr_vendors 
         if len(v.get('source_schemas', [])) >= 2]
multi.sort(key=lambda x: len(x[1]), reverse=True)

for name, schemas in multi[:20]:
    print(f"  {name}: {schemas}")

print(f"\nTotal multi-schema vendors: {len(multi)}")

# Recommend 5 vendors per schema for initial scoring
print("\n" + "=" * 60)
print("RECOMMENDED 5 VENDORS PER SCHEMA FOR INITIAL SCORING")
print("=" * 60)

for schema_key, fname in SOURCE_FILES.items():
    source_vendors = load_vendors(fname)
    source_names_lower = {v['vendor'].lower() for v in source_vendors}
    
    # Find PMR vendors that are in this source schema AND have source data
    candidates = []
    for pv in pmr_vendors:
        if schema_key in pv.get('source_schemas', []):
            if pv['vendor'].lower() in source_names_lower:
                # Get cross-schema score info
                css = pv.get('cross_schema_scores', {}).get(schema_key, {})
                candidates.append((pv['vendor'], css.get('pillar_avg', 0), len(pv.get('source_schemas', []))))
    
    # Sort by pillar_avg descending, prefer multi-schema vendors
    candidates.sort(key=lambda x: (x[2], x[1]), reverse=True)
    
    print(f"\n{schema_key}:")
    for name, avg, num_schemas in candidates[:5]:
        print(f"  {name} (avg={avg:.2f}, schemas={num_schemas})")
