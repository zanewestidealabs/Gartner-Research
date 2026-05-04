"""
Fetch any uncached URLs into research/cache/pages_cnapp/ using the same cache
key (md5 of URL) as _research_cnapp_v11.fetch_page. Run once after editing
VENDOR_URLS so the v1.2 deep-dive can re-extract from fresh cached pages.
"""
import time
import urllib.error
import urllib.request

from _research_cnapp_v11 import VENDOR_URLS, CACHE_DIR, _cache_path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")


def fetch(url: str) -> tuple[bool, int]:
    cp = _cache_path(url)
    if cp.exists():
        return True, cp.stat().st_size
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cp.write_text(html, encoding="utf-8")
        return True, len(html.encode("utf-8"))
    except urllib.error.HTTPError as e:
        return False, e.code
    except Exception:
        return False, -1


def main() -> None:
    total = sum(len(u) for u in VENDOR_URLS.values())
    print(f"Refreshing cache for {total} URLs across {len(VENDOR_URLS)} vendors")
    print(f"Cache dir: {CACHE_DIR}\n")

    for vendor, urls in VENDOR_URLS.items():
        print(f"=== {vendor} ===")
        for url in urls:
            cached_before = _cache_path(url).exists()
            ok, info = fetch(url)
            tag = "CACHED" if cached_before else ("FETCH " if ok else "FAIL  ")
            size_or_err = f"{info:>7}" if ok else f"err={info}"
            print(f"  {tag} {size_or_err}  {url}")
            if not cached_before and ok:
                time.sleep(1.0)
        print()


if __name__ == "__main__":
    main()
