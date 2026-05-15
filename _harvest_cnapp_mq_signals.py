"""
_harvest_cnapp_mq_signals.py
─────────────────────────────
Targeted public-web harvester for CNAPP-MQ gap cells.

Reads :  CNAPP MQ Vendor 1-3 Researched.json
Writes:  CNAPP MQ Vendor 1-4 Harvested.json
Cache :  .harvest_cache/<vendor-slug>.json   (raw fetched pages, reused on re-runs)

For each vendor, fetches a small set of common URL patterns
(home, /trial, /customers, /support, /blog, etc.) and runs deterministic
signal checks for the 18 sub-pillars where ledger evidence is weak/absent.

Each successful signal yields a sub_pillar_evidence entry:
  {
    "sub_pillar_id": "...",
    "rationale":     "<observed signal in plain English>",
    "sources": [
      {"type":"vendor_documentation","tier":"A","url":"...","title":"..."}
    ],
    "enrichment_status":"harvested",
    "harvested_at":"<iso>"
  }

Existing sub_pillar_evidence entries (from the v12 ledger) are preserved.
Only EMPTY cells are populated.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
import urllib3
from bs4 import BeautifulSoup  # type: ignore

# Public-marketing scraping; corporate MITM proxy may rewrite certs.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ROOT = Path(__file__).resolve().parent
SRC_PRIMARY = ROOT / "CNAPP MQ Vendor 1-4 Harvested.json"
SRC_FALLBACK = ROOT / "CNAPP MQ Vendor 1-3 Researched.json"
SRC = SRC_PRIMARY if SRC_PRIMARY.exists() else SRC_FALLBACK
DST = ROOT / "CNAPP MQ Vendor 1-4 Harvested.json"
CACHE_DIR = ROOT / ".harvest_cache"
CACHE_DIR.mkdir(exist_ok=True)

# Re-use the Playwright-rendered HTML cache built by _render_cnapp_js.py /
# _research_cnapp_v11.py for the CNAPP capability research. Sites blocked
# by WAF or rendered as SPA shells (Bitdefender, Microsoft, Sophos, Wiz, ...)
# are already cached here as fully-rendered HTML, keyed by MD5(url).
RENDER_CACHE = ROOT / "research" / "cache" / "pages_cnapp"


def _render_cache_path(url: str) -> Path:
    return RENDER_CACHE / f"{hashlib.md5(url.encode()).hexdigest()}.html"


# Per-vendor overrides for sites that block plain requests.
#   extra_urls : full URLs to also probe (often already in render cache)
#   timeout    : per-vendor read timeout override
#   max_workers: per-vendor parallelism override (lower = friendlier)
#   skip       : if True, don't fetch at all; rely solely on render cache
VENDOR_OVERRIDES: dict[str, dict] = {
    "Bitdefender": {
        "skip": True,  # WAF (Akamai) returns 403 to programmatic requests
        "extra_urls": [
            "https://www.bitdefender.com/business/products/gravityzone-cloud-security.html",
            "https://www.bitdefender.com/business/enterprise-products/cloud-security.html",
            "https://www.bitdefender.com/business/solutions/cloud-workload-security.html",
        ],
    },
    "Microsoft": {
        "timeout": 30,
        "max_workers": 2,  # azure.microsoft.com throttles parallel
        "extra_urls": [
            "https://azure.microsoft.com/en-us/products/defender-for-cloud/",
            "https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-cloud-introduction",
            "https://learn.microsoft.com/en-us/azure/defender-for-cloud/concept-cloud-security-posture-management",
            "https://www.microsoft.com/en-us/security/business/solutions/cloud-security",
        ],
    },
    "Sophos": {
        "extra_urls": [
            "https://www.sophos.com/en-us/products/cloud-native-security",
            "https://www.sophos.com/en-us/cybersecurity-explained/cnapp",
            "https://www.sophos.com/en-us/cybersecurity-explained/cloud-security",
            "https://www.sophos.com/en-us/products/managed-detection-and-response",
        ],
    },
    "Check Point": {
        "extra_urls": [
            "https://www.checkpoint.com/cloudguard/workload/",
            "https://www.checkpoint.com/cloudguard/cnapp/",
        ],
    },
    "Wiz": {
        "extra_urls": [
            "https://www.wiz.io/solutions/cloud-detection-response",
            "https://www.wiz.io/solutions/code-security",
            "https://www.wiz.io/solutions/kubernetes-security",
        ],
    },
    "CrowdStrike": {
        "extra_urls": [
            "https://www.crowdstrike.com/platform/cloud-security/cloud-detection-response/",
        ],
    },
}

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
EXTRA_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}
TIMEOUT = 6  # short — many probe URLs will 404 and slow URLs aren't worth waiting on

# ── URL patterns to probe per vendor (relative to website root) ──
PROBE_PATHS = [
    "",                      # home
    "/trial", "/free-trial", "/start-free", "/try", "/get-started",
    "/customers", "/case-studies",
    "/blog",
    "/support", "/sla",
    "/docs", "/documentation",
    "/integrations", "/marketplace", "/partners",
    "/about", "/about-us", "/company", "/locations",
    "/platform", "/why",
    "/changelog", "/releases", "/whats-new", "/roadmap",
    "/customer-success", "/services",
    "/research", "/labs", "/threat-research",
]


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def root_url(website: str) -> str:
    p = urlparse(website)
    return f"{p.scheme}://{p.netloc}"


def fetch(url: str, sess: requests.Session, timeout: int = TIMEOUT) -> tuple[int, str]:
    # First check the Playwright render cache from _render_cnapp_js.py.
    # If a fully-rendered HTML payload is already on disk for this URL,
    # use it directly — bypasses WAF/SPA problems entirely.
    rcp = _render_cache_path(url)
    if rcp.exists():
        try:
            html = rcp.read_text(encoding="utf-8", errors="replace")
            if html and len(html) > 1000:
                return 200, html
        except Exception:
            pass
    try:
        r = sess.get(url, timeout=timeout, allow_redirects=True, verify=False)
        return r.status_code, r.text if r.status_code == 200 else ""
    except Exception:
        return 0, ""


def harvest_vendor_pages(vendor_name: str, website: str) -> dict[str, dict]:
    """Fetch probe URLs (with cache) → {final_url: {status, title, text}}."""
    cache_path = CACHE_DIR / f"{slug(vendor_name)}.json"
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    overrides = VENDOR_OVERRIDES.get(vendor_name, {})
    timeout = overrides.get("timeout", TIMEOUT)
    max_workers = overrides.get("max_workers", 8)
    skip_live = bool(overrides.get("skip", False))
    extra_urls = overrides.get("extra_urls", [])

    sess = requests.Session()
    sess.headers["User-Agent"] = UA
    sess.headers.update(EXTRA_HEADERS)

    base = root_url(website)
    pages: dict[str, dict] = {}

    # Always include the website URL itself + any vendor-specific overrides
    if skip_live:
        # Only probe URLs that have a render-cache hit
        candidates = [u for u in ([website] + extra_urls) if _render_cache_path(u).exists()]
    else:
        candidates = (
            [website]
            + extra_urls
            + [urljoin(base + "/", p.lstrip("/")) for p in PROBE_PATHS if p]
        )
    # De-duplicate while preserving order
    deduped: list[str] = []
    seen_urls: set[str] = set()
    for u in candidates:
        if u not in seen_urls:
            seen_urls.add(u)
            deduped.append(u)

    import sys as _sys
    from concurrent.futures import ThreadPoolExecutor, as_completed

    results: dict[str, tuple[int, str]] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(fetch, u, sess, timeout): u for u in deduped}
        for fut in as_completed(futs):
            u = futs[fut]
            try:
                results[u] = fut.result()
            except Exception:
                results[u] = (0, "")
            _sys.stdout.write("." if results[u][0] == 200 else "x")
            _sys.stdout.flush()

    for url, (status, html) in results.items():
        if status != 200 or not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        title = (soup.title.string if soup.title and soup.title.string else "").strip()
        # Strip scripts/styles
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = re.sub(r"\s+", " ", soup.get_text(" ")).strip()
        html_lang = (soup.html.get("lang") if soup.html else "") or ""
        pages[url] = {
            "status": 200,
            "title": title[:200],
            "text": text[:80_000],
            "html_lang": html_lang,
        }

    print()  # newline after dot progress
    cache_path.write_text(json.dumps(pages, indent=2), encoding="utf-8")
    return pages


# ── Signal detectors ──
# Each returns (matched: bool, evidence_text: str, source_url: str, source_title: str) or None

def _find_page(pages: dict[str, dict], path_substrs: list[str]) -> tuple[str, dict] | None:
    for url, p in pages.items():
        low = url.lower()
        if any(sub in low for sub in path_substrs):
            return url, p
    return None


def _scan_text(pages: dict[str, dict], patterns: list[str]) -> tuple[str, dict, str] | None:
    """Return (url, page, matched_phrase) for first page containing any pattern."""
    for url, p in pages.items():
        text = p.get("text", "")
        low = text.lower()
        for pat in patterns:
            if pat.lower() in low:
                # extract a small context window
                idx = low.find(pat.lower())
                start = max(0, idx - 60)
                end = min(len(text), idx + len(pat) + 80)
                return url, p, text[start:end]
    return None


def detect_SLE_02(pages):  # Free trial / self-service
    hit = _find_page(pages, ["/trial", "/free-trial", "/start-free", "/get-started", "/try"])
    if hit:
        u, p = hit
        return f"Public free-trial / self-service start page exists: \"{p['title']}\"", u, p["title"]
    s = _scan_text(pages, ["free trial", "start free", "no credit card", "try for free"])
    if s:
        u, p, ph = s
        return f"Free-trial signaling on page: \"...{ph}...\"", u, p["title"]
    return None


def detect_SLE_04(pages):  # Free posture scan / risk assessment tool
    s = _scan_text(pages, ["free risk assessment", "free assessment", "free scan",
                           "posture scan", "free cloud risk", "complimentary assessment",
                           "free cspm scan"])
    if s:
        u, p, ph = s
        return f"Free assessment / scan tool referenced: \"...{ph}...\"", u, p["title"]
    return None


def detect_MKR_02(pages):  # CNAPP convergence announcements
    s = _scan_text(pages, ["CNAPP", "cloud-native application protection"])
    if s:
        u, p, ph = s
        return f"Public CNAPP positioning / convergence messaging: \"...{ph}...\"", u, p["title"]
    return None


def detect_MKE_02(pages):  # Cloud-threat research / blog cadence
    hit = _find_page(pages, ["/research", "/labs", "/threat", "/blog"])
    if hit:
        u, p = hit
        # Count blog post anchors heuristically
        return f"Public threat-research / blog presence: \"{p['title']}\"", u, p["title"]
    return None


def detect_MKE_04(pages):  # Digital presence & messaging clarity
    # Use the homepage title + length of first 500 chars
    home_url = next(iter(pages), None)
    if home_url:
        p = pages[home_url]
        snippet = p["text"][:200]
        return f"Homepage messaging captured: \"{snippet}...\"", home_url, p["title"]
    return None


def detect_CXQ_02(pages):  # Support quality / SLA
    hit = _find_page(pages, ["/support", "/sla"])
    if hit:
        u, p = hit
        return f"Public support / SLA page exists: \"{p['title']}\"", u, p["title"]
    s = _scan_text(pages, ["24/7 support", "premium support", "support sla", "service level agreement"])
    if s:
        u, p, ph = s
        return f"Support commitment language present: \"...{ph}...\"", u, p["title"]
    return None


def detect_CXQ_03(pages):  # Onboarding / time to first finding
    hit = _find_page(pages, ["/docs", "/documentation", "/getting-started"])
    if hit:
        u, p = hit
        return f"Public onboarding / documentation hub: \"{p['title']}\"", u, p["title"]
    s = _scan_text(pages, ["deploy in minutes", "5-minute", "time to value",
                           "agentless", "connect in minutes", "first finding"])
    if s:
        u, p, ph = s
        return f"Onboarding speed claim: \"...{ph}...\"", u, p["title"]
    return None


def detect_CXQ_04(pages):  # Customer success & expansion
    hit = _find_page(pages, ["/customer-success", "/services"])
    if hit:
        u, p = hit
        return f"Customer-success / services page exists: \"{p['title']}\"", u, p["title"]
    s = _scan_text(pages, ["technical account manager", "customer success manager",
                           "professional services", "premium services"])
    if s:
        u, p, ph = s
        return f"Customer-success program signaling: \"...{ph}...\"", u, p["title"]
    return None


def detect_VIG_02(pages):  # Industry concentration / customer logos
    hit = _find_page(pages, ["/customers", "/case-studies"])
    if hit:
        u, p = hit
        # Cheap industry diversity check
        text = p.get("text", "").lower()
        industries = ["financial", "banking", "healthcare", "retail", "manufacturing",
                      "government", "education", "technology", "telecom", "energy"]
        present = [i for i in industries if i in text]
        return (f"Customer page lists {len(present)} industry verticals: "
                f"{', '.join(present[:5])}{'...' if len(present)>5 else ''}",
                u, p["title"])
    return None


def detect_VIG_04(pages):  # Localization / regional adaptation
    langs = set()
    for p in pages.values():
        hl = (p.get("html_lang") or "").lower()
        if hl:
            langs.add(hl.split("-")[0])
    s = _scan_text(pages, ["/en-us/", "/ja/", "/de/", "/fr/", "/es/", "Japanese",
                           "Deutsch", "Français"])
    if s:
        u, p, ph = s
        return (f"Localization signal — html_lang={sorted(langs)}; locale path: \"...{ph}...\"",
                u, p["title"])
    if langs:
        home_url = next(iter(pages))
        return (f"Page language(s) declared: {sorted(langs)}", home_url, pages[home_url]["title"])
    return None


def detect_VIA_03(pages):  # Customer base & retention
    hit = _find_page(pages, ["/customers", "/case-studies"])
    if hit:
        u, p = hit
        m = re.search(r"(\d{2,5})\+?\s*(customers|enterprises|organizations|companies)",
                      p["text"], re.IGNORECASE)
        if m:
            return (f"Customer-base claim: \"{m.group(0)}\"", u, p["title"])
        return (f"Customer / case-study page exists: \"{p['title']}\"", u, p["title"])
    s = _scan_text(pages, ["customers worldwide", "fortune 500", "fortune 100",
                           "global 2000", "trusted by"])
    if s:
        u, p, ph = s
        return (f"Customer-base signaling: \"...{ph}...\"", u, p["title"])
    return None


def detect_MKU_02(pages):  # Roadmap & R&D
    hit = _find_page(pages, ["/roadmap", "/whats-new", "/changelog", "/releases"])
    if hit:
        u, p = hit
        return (f"Public roadmap / what's-new / release-notes page: \"{p['title']}\"",
                u, p["title"])
    return None


def detect_SLE_03(pages):  # Geographic sales coverage
    hit = _find_page(pages, ["/locations", "/about", "/company"])
    if hit:
        u, p = hit
        countries = ["United States", "United Kingdom", "Germany", "France", "Japan",
                     "Australia", "India", "Singapore", "Israel", "Canada", "Brazil"]
        present = [c for c in countries if c in p["text"]]
        if present:
            return (f"Office locations span {len(present)} countries: {', '.join(present[:6])}",
                    u, p["title"])
    return None


def detect_MKU_03(pages):  # Platform & ecosystem strategy
    hit = _find_page(pages, ["/integrations", "/marketplace", "/partners", "/ecosystem"])
    if hit:
        u, p = hit
        return (f"Ecosystem / integrations page: \"{p['title']}\"", u, p["title"])
    return None


def detect_MKU_01(pages):  # Vision & CNAPP convergence direction
    hit = _find_page(pages, ["/platform", "/why", "/vision"])
    if hit:
        u, p = hit
        return (f"Vision / platform-strategy page: \"{p['title']}\"", u, p["title"])
    return None


def detect_MKR_04(pages):  # Customer-driven feature delivery
    hit = _find_page(pages, ["/changelog", "/releases", "/whats-new", "/roadmap"])
    if hit:
        u, p = hit
        return (f"Public release-notes / changelog: \"{p['title']}\"", u, p["title"])
    s = _scan_text(pages, ["feature request", "ideas portal", "community vote", "user feedback"])
    if s:
        u, p, ph = s
        return (f"Customer-feedback channel: \"...{ph}...\"", u, p["title"])
    return None


# Sub-pillars we explicitly skip (would require Gartner / G2 / paywalled sources)
SKIP_DETECTORS = {"CXQ-01", "VIA-04"}

DETECTORS = {
    "SLE-02": detect_SLE_02,
    "SLE-04": detect_SLE_04,
    "MKR-02": detect_MKR_02,
    "MKE-02": detect_MKE_02,
    "MKE-04": detect_MKE_04,
    "CXQ-02": detect_CXQ_02,
    "CXQ-03": detect_CXQ_03,
    "CXQ-04": detect_CXQ_04,
    "VIG-02": detect_VIG_02,
    "VIG-04": detect_VIG_04,
    "VIA-03": detect_VIA_03,
    "MKU-02": detect_MKU_02,
    "SLE-03": detect_SLE_03,
    "MKU-03": detect_MKU_03,
    "MKU-01": detect_MKU_01,
    "MKR-04": detect_MKR_04,
}


def has_existing_evidence(vendor: dict, sid: str) -> bool:
    ev = (vendor.get("sub_pillar_evidence") or {}).get(sid) or {}
    if (ev.get("excerpts") and len(ev["excerpts"]) > 0):
        return True
    if (ev.get("sources") and len(ev["sources"]) > 0):
        return True
    return False


def main() -> int:
    print(f"[load] {SRC.name}")
    data = json.loads(SRC.read_text(encoding="utf-8"))
    vendors = data.get("vendors") or []
    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")

    summary = {"vendors": 0, "fetched_pages": 0, "filled": 0, "skipped_existing": 0,
               "no_signal": 0, "skip_paywalled": 0}

    for v in vendors:
        name = v.get("vendor")
        website = v.get("website") or ""
        if not website:
            print(f"  [skip] {name}: no website")
            continue
        print(f"\n[{name}] harvesting from {website}")
        pages = harvest_vendor_pages(name, website)
        summary["vendors"] += 1
        summary["fetched_pages"] += len(pages)
        print(f"  fetched {len(pages)} pages")

        ev_root = v.setdefault("sub_pillar_evidence", {})
        for sid, det in DETECTORS.items():
            if has_existing_evidence(v, sid):
                summary["skipped_existing"] += 1
                continue
            try:
                result = det(pages)
            except Exception as e:
                print(f"    {sid}: detector error: {e}")
                result = None
            if result is None:
                summary["no_signal"] += 1
                continue
            rationale, src_url, src_title = result
            ev_root[sid] = {
                "sub_pillar_id": sid,
                "rationale": rationale,
                "sources": [{
                    "type": "vendor_documentation",
                    "tier": "A",
                    "url": src_url,
                    "title": src_title or src_url,
                }],
                "excerpts": [{
                    "text": rationale,
                    "source_url": src_url,
                    "tier": "A",
                }],
                "enrichment_status": "harvested",
                "harvested_at": now_iso,
            }
            summary["filled"] += 1
            print(f"    {sid}: filled  ({src_url[:80]})")

        # Mark explicit skips so the UI can surface them clearly
        for sid in SKIP_DETECTORS:
            if has_existing_evidence(v, sid):
                continue
            ev_root[sid] = {
                "sub_pillar_id": sid,
                "rationale": "Requires paywalled / analyst source (Gartner Peer Insights, "
                             "MQ inclusion). Not harvestable from public web. Manual research needed.",
                "sources": [],
                "excerpts": [],
                "enrichment_status": "needs_targeted_research",
                "harvested_at": now_iso,
            }
            summary["skip_paywalled"] += 1

    data["harvest_metadata"] = {
        "harvested_at": now_iso,
        "source_file": SRC.name,
        "summary": summary,
        "detectors_used": sorted(DETECTORS.keys()),
        "detectors_skipped": sorted(SKIP_DETECTORS),
    }

    DST.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"\n[done] wrote {DST.name}")
    print(f"  Vendors processed     : {summary['vendors']}")
    print(f"  Pages fetched (total) : {summary['fetched_pages']}")
    print(f"  Cells newly filled    : {summary['filled']}")
    print(f"  Cells already grounded: {summary['skipped_existing']}")
    print(f"  No public signal      : {summary['no_signal']}")
    print(f"  Paywall-skipped       : {summary['skip_paywalled']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
