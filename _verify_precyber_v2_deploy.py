"""Verify PreCyber v2 schema is available on local and production."""
import urllib.request
import json

for label, base in [("LOCAL", "http://localhost:5000"), ("PROD", "http://192.168.15.51:5000")]:
    try:
        resp = urllib.request.urlopen(base + "/api/schema-files", timeout=5)
        data = json.loads(resp.read())
        schemas = data.get("schemas", [])
        precyber = [s for s in schemas if "Preemptive" in s.get("filename", "")]
        print("%s: %d total schemas, %d PreCyber schemas" % (label, len(schemas), len(precyber)))
        for s in precyber:
            fname = s.get("filename", "")
            title = s.get("display", {}).get("title", "")
            print("  -> %s (%s)" % (fname, title))
    except Exception as e:
        print("%s: ERROR - %s" % (label, e))
