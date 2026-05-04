"""Debug: check raw HTML from a cached fetch."""
import json, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "research" / "cache" / "pages_mdr"

url = "https://www.crowdstrike.com/en-us/services/managed-detection-and-response/"
h = hashlib.sha1(url.encode()).hexdigest()
cf = CACHE / f"{h}.json"

if cf.exists():
    rec = json.loads(cf.read_text(encoding="utf-8"))
    print(f"URL: {rec.get('url')}")
    print(f"ok: {rec.get('ok')}")
    print(f"error: {rec.get('error')}")
    print(f"text length: {len(rec.get('text', ''))}")
    print(f"text preview: '{rec.get('text', '')[:500]}'")
else:
    print(f"Not cached. Fetching raw...")
    import urllib.request, random
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "text/html,*/*"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read()
        html = raw.decode("utf-8", errors="replace")
        print(f"HTML length: {len(html)}")
        print(f"HTML preview: {html[:1000]}")
        
        # Try the parser
        from extract_mdr_excerpts import html_to_text
        text = html_to_text(html)
        print(f"\nExtracted text length: {len(text)}")
        print(f"Text preview: '{text[:500]}'")
