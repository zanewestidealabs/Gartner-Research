"""Verify v2.2 is served on local and production."""
import urllib.request
import json
import sys

def check(label, url):
    try:
        r = urllib.request.urlopen(url, timeout=10)
        d = json.loads(r.read())
        vendors = d.get('vendors', d) if isinstance(d, dict) else d
        if not vendors:
            print(f"{label}: No vendors returned")
            return
        v = vendors[0]
        rat = v.get('sub_pillar_rationale_researched', {})
        print(f"{label}: {len(vendors)} vendors, {len(rat)} rationale entries for {v['vendor']}")
        if rat:
            sp = sorted(rat.keys())[0]
            print(f"  {sp}: {rat[sp][:150]}...")
        else:
            print(f"  WARNING: No sub_pillar_rationale_researched field!")
    except Exception as e:
        print(f"{label}: ERROR - {e}")

check("LOCAL", "http://localhost:5000/api/vendors?file=Offensive+Security+Vendor+2-2+Researched.json")
check("PROD", "http://192.168.15.51:5000/api/vendors?file=Offensive+Security+Vendor+2-2+Researched.json")
