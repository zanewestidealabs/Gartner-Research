"""Review and validate all AIUC-1 mappings in the v2.0 schema."""
import json

with open('Secure_by_Design_AI_Controls_Schema_v2.json') as f:
    d = json.load(f)

root = d['secure_by_design_ai_controls_v2.0']
crosswalk = root['aiuc1_crosswalk']
pillars = root['pillars']
sub_pillars = root['sub_pillars']

# === 1. Verify every AIUC-1 crosswalk requirement appears in the sub-pillar's aiuc1_mapping ===
missing_from_sp = []
for code, entry in crosswalk.items():
    if code == 'description':
        continue
    target_sps = entry.get('sub_pillars', [])
    for sp in target_sps:
        sp_mapping = sub_pillars.get(sp, {}).get('aiuc1_mapping', {})
        if isinstance(sp_mapping, dict) and code not in sp_mapping:
            missing_from_sp.append(f'{code} -> {sp}')
        elif isinstance(sp_mapping, list) and code not in sp_mapping:
            missing_from_sp.append(f'{code} -> {sp}')

print('=== CHECK 1: Crosswalk -> Sub-pillar consistency ===')
if missing_from_sp:
    for m in missing_from_sp:
        print(f'  MISSING: {m}')
else:
    print('  PASS: All crosswalk entries reflected in sub-pillar aiuc1_mapping')

# === 2. Verify every sub-pillar aiuc1_mapping code exists in crosswalk ===
orphan_codes = []
for sp_code, sp_data in sub_pillars.items():
    mapping = sp_data.get('aiuc1_mapping', {})
    codes = mapping.keys() if isinstance(mapping, dict) else mapping
    for code in codes:
        if code not in crosswalk:
            orphan_codes.append(f'{sp_code}: {code}')

print()
print('=== CHECK 2: Sub-pillar codes all in crosswalk ===')
if orphan_codes:
    for o in orphan_codes:
        print(f'  ORPHAN: {o}')
else:
    print('  PASS: All sub-pillar AIUC-1 codes exist in crosswalk')

# === 3. Verify pillar aggregation is correct ===
print()
print('=== CHECK 3: Pillar aggregation accuracy ===')
pillar_prefix_map = {}
for sp_code in sub_pillars:
    prefix = sp_code.split('-')[0]
    pillar_prefix_map.setdefault(prefix, []).append(sp_code)

for pillar_code in ['INF', 'IAM', 'NDS', 'DSO', 'TRM', 'SAF', 'REL']:
    expected = {}
    for sp_code in sorted(pillar_prefix_map.get(pillar_code, [])):
        sp_m = sub_pillars[sp_code].get('aiuc1_mapping', {})
        if isinstance(sp_m, dict):
            for code in sp_m:
                expected.setdefault(code, []).append(sp_code)

    actual = pillars[pillar_code].get('aiuc1_requirements', {})
    actual_codes = set(actual.keys())
    expected_codes = set(expected.keys())

    if actual_codes == expected_codes:
        print(f'  {pillar_code}: PASS ({len(actual_codes)} reqs)')
    else:
        extra = actual_codes - expected_codes
        missing = expected_codes - actual_codes
        if extra:
            print(f'  {pillar_code}: EXTRA in pillar: {extra}')
        if missing:
            print(f'  {pillar_code}: MISSING from pillar: {missing}')

# === 4. Coverage totals ===
print()
print('=== CHECK 4: Total AIUC-1 coverage ===')
all_aiuc_in_crosswalk = set(k for k in crosswalk if k != 'description')
all_aiuc_in_subpillars = set()
for sp_data in sub_pillars.values():
    m = sp_data.get('aiuc1_mapping', {})
    if isinstance(m, dict):
        all_aiuc_in_subpillars.update(m.keys())

missing_coverage = all_aiuc_in_crosswalk - all_aiuc_in_subpillars
print(f'  Crosswalk: {len(all_aiuc_in_crosswalk)} reqs')
print(f'  Sub-pillars cover: {len(all_aiuc_in_subpillars)} reqs')
if missing_coverage:
    print(f'  MISSING (in crosswalk but not in any sub-pillar): {sorted(missing_coverage)}')
else:
    print(f'  PASS: 100% coverage - every crosswalk req mapped to sub-pillars')

# === 5. Mandatory coverage ===
print()
print('=== CHECK 5: Mandatory requirement coverage ===')
mandatory_reqs = [k for k, v in crosswalk.items() if k != 'description' and v.get('mandatory')]
mandatory_covered = [r for r in mandatory_reqs if r in all_aiuc_in_subpillars]
mandatory_missing = [r for r in mandatory_reqs if r not in all_aiuc_in_subpillars]
print(f'  Mandatory total: {len(mandatory_reqs)}')
print(f'  Mandatory covered: {len(mandatory_covered)}')
if mandatory_missing:
    print(f'  MANDATORY GAPS: {sorted(mandatory_missing)}')
else:
    print(f'  PASS: All mandatory requirements fully mapped')

# === 6. E007/E014 merged check ===
print()
print('=== CHECK 6: Merged requirements (E007, E014) ===')
for code in ['E007', 'E014']:
    entry = crosswalk.get(code, {})
    note = entry.get('note', 'NO NOTE')
    sps = entry.get('sub_pillars', [])
    print(f'  {code}: note="{note}", sub_pillars={sps}')

# === 7. Full mapping table ===
print()
print('=== FULL MAPPING TABLE ===')
print(f'{"AIUC-1":<8} {"Mandatory":<10} {"Category":<22} {"Requirement":<50} {"Sub-Pillars"}')
print('-' * 120)
for code in sorted(all_aiuc_in_crosswalk, key=lambda x: (x[0], int(x[1:]))):
    entry = crosswalk[code]
    mand = 'YES' if entry.get('mandatory') else 'no'
    cat = entry.get('category', '')
    req = entry.get('requirement', '')
    sps = entry.get('sub_pillars', [])
    note = f"  [{entry['note']}]" if 'note' in entry else ''
    print(f'{code:<8} {mand:<10} {cat:<22} {req:<50} {", ".join(sps)}{note}')

# === 8. Sub-pillars with no AIUC-1 mapping ===
print()
print('=== SUB-PILLARS WITHOUT AIUC-1 MAPPING (v1.0 originals) ===')
for sp_code in sorted(sub_pillars.keys()):
    m = sub_pillars[sp_code].get('aiuc1_mapping', {})
    if (isinstance(m, dict) and len(m) == 0) or (isinstance(m, list) and len(m) == 0):
        print(f'  {sp_code}: {sub_pillars[sp_code]["name"]}')
