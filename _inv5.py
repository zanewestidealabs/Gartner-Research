import json
sp_dict = json.load(open('CNAPP_MQ_Gap_Schema_App.json'))['cnapp_mq_gap_taxonomy_v1.0']['sub_pillars']
zero = ['SLE-02','SLE-04','MKR-02','MKE-02','MKE-04','CXQ-02','CXQ-03','CXQ-04','VIG-02','VIG-04']
sparse = [('VIA-03',1),('MKU-02',3),('SLE-03',7),('MKU-03',11),('CXQ-01',12),('MKU-01',12),('MKR-04',13),('VIA-04',14)]
print("=== ZERO-EVIDENCE SUB-PILLARS (10 dims × 24 vendors = 240 cells) ===\n")
for sid in zero:
    info = sp_dict.get(sid, {})
    print(f"{sid}  {info.get('name','?')}")
    wtv = info.get('what_to_verify_publicly') or []
    if wtv:
        print(f"    Verify: {wtv[0][:130]}")
    print()
print("=== SPARSE-EVIDENCE SUB-PILLARS (8 dims, partial coverage) ===\n")
for sid, cov in sparse:
    info = sp_dict.get(sid, {})
    print(f"{sid}  ({cov}/24)  {info.get('name','?')}")
    wtv = info.get('what_to_verify_publicly') or []
    if wtv:
        print(f"    Verify: {wtv[0][:130]}")
    print()
