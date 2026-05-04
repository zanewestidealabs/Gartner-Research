"""Quick debug: check URLs and page fetch for first vendor."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENDOR_FILE = ROOT / "MDR Services Vendor 2-0 Researched.json"

with open(VENDOR_FILE, "r", encoding="utf-8-sig") as f:
    data = json.load(f)

v = data["vendors"][0]
print(f"Vendor: {v['vendor']}")
print(f"Website: {v.get('website', 'N/A')}")
ev = v.get("sub_pillar_evidence", {})
all_urls = set()
for sp_id, sp_ev in sorted(ev.items()):
    urls = sp_ev.get("source_urls", [])
    for u in urls:
        all_urls.add(u)
    print(f"  {sp_id}: {len(urls)} URLs, excerpts={len(sp_ev.get('excerpts', []))}")

print(f"\nTotal unique URLs: {len(all_urls)}")
for u in sorted(all_urls)[:10]:
    print(f"  {u}")

# Check cache
CACHE = ROOT / "research" / "cache" / "pages_mdr"
if CACHE.exists():
    cached = list(CACHE.glob("*.json"))
    print(f"\nCached pages: {len(cached)}")
    if cached:
        import hashlib
        # find cache for first URL
        first_url = sorted(all_urls)[0] if all_urls else None
        if first_url:
            h = hashlib.sha1(first_url.encode()).hexdigest()
            cf = CACHE / f"{h}.json"
            if cf.exists():
                rec = json.loads(cf.read_text(encoding="utf-8"))
                print(f"  Cached page for {first_url[:80]}:")
                print(f"  ok={rec.get('ok')}, text_len={len(rec.get('text', ''))}")
                print(f"  Text preview: {rec.get('text', '')[:300]}")
else:
    print("\nNo cache directory yet")
