"""
Build Preemptive Cybersecurity Vendor 6-0 v3.json from 5-0 Combined.json.

Score migration: all sub_pillar_scores_current values shift +1, capped at 5.
  Old 0 -> New 1 (No or Basic Capability)
  Old 1 -> New 2 (Marketing Mention or Basic Manual)
  Old 2 -> New 3 (Demonstrated)
  Old 3 -> New 4 (Advanced)
  Old 4 -> New 5 (Market-Leading)
  Old 5 -> New 5 (Market-Leading, capped)

Per vendor changes:
  - sub_pillar_scores_v2     = archived copy of original sub_pillar_scores_current
  - sub_pillar_scores_v3     = remapped scores
  - sub_pillar_scores_current = same as v3 (so 'current' mode in UI uses v3)
  - pillar_scores             = recomputed mean of v3 scores per pillar
  - coverage_grade            = recomputed with score >= 2 threshold (16 cap sub-pillars)
  - schema_version            = "3.0"
"""

import json
from pathlib import Path
from collections import Counter

SRC = Path('Preemptive Cybersecurity Vendor 5-0 Combined.json')
DST = Path('Preemptive Cybersecurity Vendor 6-0 v3.json')

# The 16 capability sub-pillars used for coverage grade (not services maturity)
CAPABILITY_SUB_PILLARS = [
    'EXM-01', 'EXM-02', 'EXM-03', 'EXM-04',
    'AMT-01', 'AMT-02', 'AMT-03', 'AMT-04',
    'ADR-01', 'ADR-02', 'ADR-03', 'ADR-04',
    'PPM-01', 'PPM-02', 'PPM-03', 'PPM-04',
]

# Coverage grade thresholds (# of capability sub-pillars with score >= 2)
GRADE_THRESHOLDS = [
    (13, 'A'),
    (10, 'B'),
    (7,  'C'),
    (4,  'D'),
    (1,  'F'),
    (0,  'F'),
]

PILLARS = ['EXM', 'AMT', 'ADR', 'PPM', 'SVC']


def remap_score(s):
    """Shift score +1, cap at 5."""
    return min(int(s) + 1, 5)


def compute_pillar_scores(sub_scores):
    """Mean of v3 sub-pillar scores per pillar."""
    out = {}
    for p in PILLARS:
        keys = [k for k in sub_scores if k.startswith(p + '-')]
        vals = [sub_scores[k] for k in keys if sub_scores[k] >= 1]
        out[p] = round(sum(vals) / len(vals), 4) if vals else 0.0
    return out


def compute_coverage_grade(sub_scores):
    """Count capability sub-pillars with score >= 2; assign A-F grade."""
    covered = sum(1 for sp in CAPABILITY_SUB_PILLARS if sub_scores.get(sp, 0) >= 2)
    for threshold, grade in GRADE_THRESHOLDS:
        if covered >= threshold:
            return grade, covered
    return 'F', 0


def main():
    print(f'Loading: {SRC}')
    vendors = json.loads(SRC.read_text(encoding='utf-8'))
    print(f'  {len(vendors)} vendors loaded')

    migrated = []
    stats_before = Counter()
    stats_after = Counter()
    grade_dist = Counter()
    pillar_totals = {p: 0.0 for p in PILLARS}

    for v in vendors:
        v2_scores = dict(v.get('sub_pillar_scores_current', {}))

        # Count v2 score distribution
        for val in v2_scores.values():
            stats_before[int(val)] += 1

        # Remap to v3
        v3_scores = {k: remap_score(val) for k, val in v2_scores.items()}

        # Count v3 score distribution
        for val in v3_scores.values():
            stats_after[int(val)] += 1

        # Recompute pillar scores
        new_pillar_scores = compute_pillar_scores(v3_scores)
        for p in PILLARS:
            pillar_totals[p] += new_pillar_scores.get(p, 0)

        # Recompute coverage grade
        new_grade, covered_count = compute_coverage_grade(v3_scores)
        grade_dist[new_grade] += 1

        # Build updated vendor record
        nv = dict(v)
        nv['sub_pillar_scores_v2'] = v2_scores         # archive
        nv['sub_pillar_scores_v3'] = v3_scores          # explicit v3 key
        nv['sub_pillar_scores_current'] = v3_scores     # 'current' mode in UI
        nv['pillar_scores'] = new_pillar_scores
        nv['coverage_grade'] = new_grade
        nv['coverage_sub_pillar_count'] = covered_count
        nv['schema_version'] = '3.0'
        migrated.append(nv)

    n = len(migrated)

    # Write output
    DST.write_text(json.dumps(migrated, indent=2, ensure_ascii=False), encoding='utf-8')

    print(f'\nWritten: {DST}')
    print(f'Total vendors: {n}')

    print('\n--- Score distribution ---')
    print('v2 scores:')
    for k in sorted(stats_before):
        print(f'  {k}: {stats_before[k]:4d} sub-pillar entries')
    print('v3 scores:')
    for k in sorted(stats_after):
        print(f'  {k}: {stats_after[k]:4d} sub-pillar entries')
    print('  (no score 0 should appear below)')

    print('\n--- Coverage grade distribution (v3) ---')
    for g in ['A', 'B', 'C', 'D', 'F']:
        print(f'  {g}: {grade_dist[g]}')

    print('\n--- Pillar averages across all vendors (v3) ---')
    for p in PILLARS:
        print(f'  {p}: {pillar_totals[p]/n:.3f}')

    # Sanity check: no score 0 in v3
    zero_found = sum(1 for v in migrated
                     for val in v['sub_pillar_scores_current'].values()
                     if val == 0)
    if zero_found:
        print(f'\nWARNING: {zero_found} score-0 entries still found in v3 data!')
    else:
        print('\nSanity check PASSED: no score-0 entries in v3 data.')


if __name__ == '__main__':
    main()
