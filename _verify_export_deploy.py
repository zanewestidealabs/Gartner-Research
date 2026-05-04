"""Verify that the tabbed export code is deployed on local and production."""
import urllib.request
import json

SIGNATURE = "switchTab"  # unique function name in the new export code

for label, base in [("LOCAL", "http://localhost:5000"), ("PROD", "http://192.168.15.51:5000")]:
    try:
        # Check API is up
        resp = urllib.request.urlopen(f"{base}/api/vendors", timeout=5)
        vendors = json.loads(resp.read())
        vcount = len(vendors) if isinstance(vendors, list) else len(vendors.get("vendors", []))

        # Check app.js contains new export code
        resp2 = urllib.request.urlopen(f"{base}/static/app.js", timeout=5)
        js = resp2.read().decode("utf-8", errors="replace")
        has_tabs = SIGNATURE in js
        has_sp_card = "sp-card-header" in js
        has_build_tabs = "_buildExportHtmlPage(tabs," in js

        status = "TABBED EXPORT DEPLOYED" if (has_tabs and has_sp_card and has_build_tabs) else "OLD EXPORT (not updated)"
        print(f"{label}: {vcount} vendors — {status}")
    except Exception as e:
        print(f"{label}: UNREACHABLE — {e}")
