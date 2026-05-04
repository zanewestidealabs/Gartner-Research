"""Debug: check URL validity across multiple vendors and find working pages."""
import json, urllib.request, urllib.error, random, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENDOR_FILE = ROOT / "MDR Services Vendor 2-0 Researched.json"

with open(VENDOR_FILE, "r", encoding="utf-8-sig") as f:
    data = json.load(f)

ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"

# Collect unique URLs across all vendors
all_urls = set()
url_to_vendors = {}
for v in data["vendors"][:10]:  # first 10 vendors
    vname = v["vendor"]
    website = v.get("website", "")
    for sp_id, sp_ev in v.get("sub_pillar_evidence", {}).items():
        for u in sp_ev.get("source_urls", []):
            if u and u.startswith("http"):
                all_urls.add(u)
                url_to_vendors.setdefault(u, []).append(vname)

print(f"Unique URLs across first 10 vendors: {len(all_urls)}")

# Check a sample
sample = sorted(all_urls)[:20]
results = {"ok": 0, "fail": 0}
for url in sample:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": ua}, method="HEAD")
        with urllib.request.urlopen(req, timeout=8) as resp:
            results["ok"] += 1
            print(f"  OK  {resp.status} {url[:80]}")
    except urllib.error.HTTPError as e:
        results["fail"] += 1
        print(f"  ERR {e.code} {url[:80]}")
    except Exception as e:
        results["fail"] += 1
        print(f"  ERR {type(e).__name__} {url[:80]}")
    time.sleep(0.5)

print(f"\nResults: {results['ok']} OK, {results['fail']} failed out of {len(sample)} tested")

# Also try vendor websites directly
print(f"\n--- Vendor websites ---")
for v in data["vendors"][:10]:
    website = v.get("website", "")
    if not website:
        continue
    try:
        req = urllib.request.Request(website, headers={"User-Agent": ua}, method="HEAD")
        with urllib.request.urlopen(req, timeout=8) as resp:
            print(f"  OK  {resp.status} {v['vendor']}: {website}")
    except urllib.error.HTTPError as e:
        print(f"  ERR {e.code} {v['vendor']}: {website}")
    except Exception as e:
        print(f"  ERR {type(e).__name__} {v['vendor']}: {website}")
    time.sleep(0.5)
