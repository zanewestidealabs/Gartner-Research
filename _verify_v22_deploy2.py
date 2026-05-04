"""Verify v2.2 is served on local and production by switching to it first."""
import urllib.request
import json

def switch_and_check(label, base_url):
    try:
        # Switch to v2.2 file
        req = urllib.request.Request(
            f"{base_url}/api/switch-vendor-file",
            data=json.dumps({"filename": "Offensive Security Vendor 2-2 Researched.json"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        resp = urllib.request.urlopen(req, timeout=10)
        switch_result = json.loads(resp.read())
        print(f"{label} switch: {switch_result.get('status', 'unknown')} -> {switch_result.get('current', '?')}")

        # Now get vendors
        r = urllib.request.urlopen(f"{base_url}/api/vendors", timeout=10)
        vendors = json.loads(r.read())
        if not vendors:
            print(f"  No vendors returned!")
            return

        v = vendors[0]
        rat = v.get('sub_pillar_rationale_researched', {})
        print(f"  {len(vendors)} vendors, {len(rat)} rationale entries for '{v['vendor']}'")
        if rat:
            sp = sorted(rat.keys())[0]
            print(f"  {sp}: {rat[sp][:180]}...")
        else:
            print(f"  WARNING: No sub_pillar_rationale_researched!")
    except Exception as e:
        print(f"{label}: ERROR - {e}")

switch_and_check("LOCAL", "http://localhost:5000")
switch_and_check("PROD", "http://192.168.15.51:5000")
