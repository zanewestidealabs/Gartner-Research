"""
Clean AI-isms from cpo-killchain-mitre-v3 report:
- Em dashes (U+2014) → colons, periods, or commas based on context
- En dashes (U+2013) → hyphens for ranges
- Curly quotes (U+2018/U+2019) → straight quotes
"""
import json, pathlib, re

FILE = pathlib.Path(__file__).parent / 'precyber_market_insight_reports.json'
data = json.loads(FILE.read_text(encoding='utf-8'))
reports = data.get('reports', data) if isinstance(data, dict) else data
v3 = next(r for r in reports if r['id'] == 'cpo-killchain-mitre-v3')


def clean_text(s):
    if not isinstance(s, str):
        return s

    # En dashes in number ranges: "1–2" → "1-2", "2025–2026" → "2025-2026"
    s = re.sub(r'(\d)\u2013(\d)', r'\1-\2', s)

    # Em dashes used as parenthetical asides before closing context:
    # "dimensions—implementation, advisory, managed operations, autonomous delivery—create"
    # → "dimensions (implementation, advisory, managed operations, autonomous delivery) create"
    s = s.replace(
        'dimensions\u2014implementation, advisory, managed operations, autonomous delivery\u2014create',
        'dimensions (implementation, advisory, managed operations, autonomous delivery) create'
    )

    # Em dash between clause and clarification → colon
    patterns_colon = [
        ('bottleneck\u2014lowest', 'bottleneck: lowest'),
        ('coverage\u2014depends on', 'coverage; depends on'),
        ('coverage\u2014>90%', 'coverage (>90%'),
        ('phases\u2014where preemptive', 'phases, where preemptive'),
        ('layer\u2014determines', 'layer; determines'),
        ('lifecycle\u2014it amplifies', 'lifecycle; it amplifies'),
        ('overall\u2014dynamic segmentation', 'overall; dynamic segmentation'),
        ('coverage\u2014depends', 'coverage; depends'),
        ('Weakest coverage\u2014depends', 'Weakest coverage; depends'),
    ]
    for old, new in patterns_colon:
        s = s.replace(old, new)

    # Remaining em dashes → " - "
    s = s.replace('\u2014', ' - ')

    # Remaining en dashes → "-"
    s = s.replace('\u2013', '-')

    # Curly quotes → straight
    s = s.replace('\u2018', "'")
    s = s.replace('\u2019', "'")
    s = s.replace('\u201c', '"')
    s = s.replace('\u201d', '"')

    # Clean up double spaces from replacements
    s = re.sub(r'  +', ' ', s)

    return s


def clean_obj(obj):
    if isinstance(obj, str):
        return clean_text(obj)
    if isinstance(obj, list):
        return [clean_obj(item) for item in obj]
    if isinstance(obj, dict):
        return {k: clean_obj(v) for k, v in obj.items()}
    return obj


# Count before
before = json.dumps(v3)
em_before = before.count('\u2014')
en_before = before.count('\u2013')
cq_before = before.count('\u2018') + before.count('\u2019') + before.count('\u201c') + before.count('\u201d')

# Clean
cleaned = clean_obj(v3)

# Replace in reports list
for i, r in enumerate(reports):
    if r['id'] == 'cpo-killchain-mitre-v3':
        reports[i] = cleaned
        break

# Save
if isinstance(data, dict) and 'reports' in data:
    data['reports'] = reports
    out = data
elif isinstance(data, list):
    out = reports
else:
    out = reports

FILE.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')

# Count after
after = json.dumps(cleaned)
em_after = after.count('\u2014')
en_after = after.count('\u2013')
cq_after = after.count('\u2018') + after.count('\u2019') + after.count('\u201c') + after.count('\u201d')

print(f"SUCCESS: Cleaned AI-isms from v3 report.")
print(f"  Em dashes: {em_before} → {em_after}")
print(f"  En dashes: {en_before} → {en_after}")
print(f"  Curly quotes: {cq_before} → {cq_after}")
