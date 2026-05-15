import json

d = json.load(open('CNAPP Vendor 1-2 Researched.json', encoding='utf-8'))
print('=== CNAPP Vendor 1-2 Researched.json (capability schema) ===')
print('top keys:', list(d.keys())[:10])
vs = d.get('vendors') or []
print(f'vendors: {len(vs)}')
if vs:
    v = vs[0]
    print(f'first vendor: {v.get("vendor")}')
    keys = [k for k in v.keys() if 'rationale' in k or 'evidence' in k or 'source' in k]
    print('relevant keys:', keys)
    if 'sub_pillar_evidence' in v:
        spe = v['sub_pillar_evidence']
        sample_keys = list(spe.keys())[:2]
        for k in sample_keys:
            print(f'\n--- {k} ---')
            print(json.dumps(spe[k], indent=2)[:800])
    # Inventory all vendors
    print()
    print('Per-vendor sub_pillar_evidence count:')
    for vv in vs:
        spe = vv.get('sub_pillar_evidence') or {}
        n_with_sources = sum(1 for e in spe.values() if isinstance(e, dict) and e.get('sources'))
        print(f'  {vv.get("vendor"):30s}  total_sps={len(spe):3d}  with_sources={n_with_sources:3d}')
