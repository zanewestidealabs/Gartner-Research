"""
_render_precyber_zero_vendors.py
=================================
Playwright-render the public web pages for vendors whose original urllib fetch
returned 0 useful pages (SPAs / bot-walled / JS-required), then re-extract
sub-pillar evidence and patch the v3-0 SVC Pricing JSON in place.

Targets: vendors with all 16 product sub-pillar cells = 0.0 in the validated
output (Axonius, HashiCorp, Group-IB, Trellix). Mirrors the cache format used
by `research_precyber_v1_evidence.py` (sha1(url).json under
`research/cache/pages_precyber/`) so downstream tools see no difference from
a normal urllib fetch.

After rendering, calls `evidence_for_vendor` (16 product cells) and
`process_vendor` (8 services cells + pricing) on each target vendor and writes
the result back into `Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json`.

Usage:
    python _render_precyber_zero_vendors.py
    python _render_precyber_zero_vendors.py --vendor Axonius
    python _render_precyber_zero_vendors.py --render-only       # skip rescore
    python _render_precyber_zero_vendors.py --rescore-only      # skip render
    python _render_precyber_zero_vendors.py --extra-vendor Blumira

After this finishes, run `_revalidate_precyber_scoring.py` to refresh
`Preemptive Cybersecurity Vendor 2-3 Holistic Validated.json`.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

# Force UTF-8 stdout on Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / "research" / "cache" / "pages_precyber"
TARGET_FILE = ROOT / "Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json"

# ─────────────────────────────────────────────────────────────────────
# Vendors that fetched 0 useful pages, with curated URL lists.
# Includes the original VENDOR_URLS from research_precyber_v1_evidence.py
# plus services/pricing-friendly pages so SVC sub-pillars also benefit.
# ─────────────────────────────────────────────────────────────────────

ZERO_VENDOR_URLS: Dict[str, List[str]] = {
    "Axonius": [
        # Platform / EXM (verified 2024 URLs from axonius.com homepage crawl)
        "https://www.axonius.com/platform",
        "https://www.axonius.com/platform/cyber-assets",
        "https://www.axonius.com/platform/exposures",
        "https://www.axonius.com/platform/identities",
        "https://www.axonius.com/platform/saas-applications",
        "https://www.axonius.com/platform/software-assets",
        "https://www.axonius.com/solutions/exposure-management",
        "https://www.axonius.com/solutions/cyber-incident-response",
        "https://www.axonius.com/solutions/cyber-resilience-strategy",
        "https://www.axonius.com/solutions/it-asset-discovery",
        "https://www.axonius.com/solutions/improve-cmdb-data-quality",
        "https://www.axonius.com/solutions/verify-endpoint-compliance",
        "https://www.axonius.com/security-program",
        # Services / partners / company
        "https://www.axonius.com/partners",
        "https://www.axonius.com/customer-stories",
        "https://www.axonius.com/adapters",
        "https://www.axonius.com/federal-systems",
        "https://www.axonius.com/product-tour",
    ],
    "HashiCorp": [
        # AMT / credential rotation focus
        "https://www.hashicorp.com/products/vault",
        "https://www.hashicorp.com/products/boundary",
        "https://www.hashicorp.com/products/consul",
        "https://www.hashicorp.com/solutions/zero-trust-security",
        "https://www.hashicorp.com/solutions/secrets-management",
        "https://www.hashicorp.com/products/vault/dynamic-secrets",
        "https://www.hashicorp.com/products/vault/secrets-management",
        # Services / pricing
        "https://www.hashicorp.com/services",
        "https://www.hashicorp.com/partners/professional-services",
        "https://www.hashicorp.com/customer-success",
        "https://www.hashicorp.com/products/vault/pricing",
    ],
    "Group-IB": [
        # ADR focus
        "https://www.group-ib.com/products/threat-intelligence/",
        "https://www.group-ib.com/products/digital-risk-protection/",
        "https://www.group-ib.com/products/attack-surface-management/",
        "https://www.group-ib.com/products/fraud-protection/",
        "https://www.group-ib.com/products/managed-xdr/",
        "https://www.group-ib.com/services/threat-hunting/",
        "https://www.group-ib.com/services/incident-response/",
        "https://www.group-ib.com/services/dark-web-monitoring/",
        "https://www.group-ib.com/services/managed-services/",
        # Pricing / overview
        "https://www.group-ib.com/products/",
    ],
    "Trellix": [
        # ADR / XDR focus
        "https://www.trellix.com/platform/",
        "https://www.trellix.com/products/endpoint-security/",
        "https://www.trellix.com/products/network-security/",
        "https://www.trellix.com/products/xdr/",
        "https://www.trellix.com/solutions/threat-intelligence/",
        "https://www.trellix.com/products/helix-connect/",
        "https://www.trellix.com/services/",
        "https://www.trellix.com/services/professional-services/",
        "https://www.trellix.com/services/managed-detection-and-response/",
        "https://www.trellix.com/services/threat-intelligence-services/",
    ],

    # ─── Track B: tech vendors that scored thin in v2-3 due to weak cache ───
    "SentinelOne": [
        "https://www.sentinelone.com/platform/",
        "https://www.sentinelone.com/platform/singularity-endpoint/",
        "https://www.sentinelone.com/platform/singularity-cloud-security/",
        "https://www.sentinelone.com/platform/singularity-identity/",
        "https://www.sentinelone.com/platform/singularity-data-lake/",
        "https://www.sentinelone.com/platform/purple-ai/",
        "https://www.sentinelone.com/platform/singularity-xdr/",
        "https://www.sentinelone.com/services/vigilance-respond/",
        "https://www.sentinelone.com/services/threat-intelligence/",
        "https://www.sentinelone.com/services/",
        "https://www.sentinelone.com/cybersecurity-101/threat-intelligence/",
    ],
    "Darktrace": [
        "https://darktrace.com/products",
        "https://darktrace.com/products/detect",
        "https://darktrace.com/products/respond",
        "https://darktrace.com/products/heal",
        "https://darktrace.com/products/prevent",
        "https://darktrace.com/products/proactive-exposure-management",
        "https://darktrace.com/products/attack-surface-management",
        "https://darktrace.com/cyber-ai",
        "https://darktrace.com/services",
        "https://darktrace.com/services/managed-services",
    ],
    "Lacework (Fortinet)": [
        "https://www.lacework.com/platform",
        "https://www.lacework.com/platform/cloud-security-posture-management",
        "https://www.lacework.com/platform/cloud-workload-protection",
        "https://www.lacework.com/platform/vulnerability-management",
        "https://www.lacework.com/platform/code-security",
        "https://www.lacework.com/platform/kubernetes-security",
        "https://www.lacework.com/platform/threat-detection",
        "https://www.lacework.com/why-lacework/polygraph-data-platform",
    ],
    "Palo Alto Networks": [
        "https://www.paloaltonetworks.com/cortex",
        "https://www.paloaltonetworks.com/cortex/cortex-xsiam",
        "https://www.paloaltonetworks.com/cortex/cortex-xdr",
        "https://www.paloaltonetworks.com/cortex/cortex-xpanse",
        "https://www.paloaltonetworks.com/cortex/cortex-xsoar",
        "https://www.paloaltonetworks.com/unit42",
        "https://www.paloaltonetworks.com/unit42/incident-response",
        "https://www.paloaltonetworks.com/unit42/proactive-services",
        "https://www.paloaltonetworks.com/unit42/managed-services",
        "https://www.paloaltonetworks.com/services",
    ],
    "Cisco (Splunk)": [
        "https://www.splunk.com/en_us/products/enterprise-security.html",
        "https://www.splunk.com/en_us/products/splunk-security-orchestration-and-automation.html",
        "https://www.splunk.com/en_us/products/attack-analyzer.html",
        "https://www.splunk.com/en_us/products/user-behavior-analytics.html",
        "https://www.splunk.com/en_us/cyber-security.html",
        "https://www.cisco.com/site/us/en/products/security/index.html",
        "https://www.cisco.com/site/us/en/products/security/xdr/index.html",
        "https://www.cisco.com/site/us/en/products/security/talos/index.html",
        "https://www.cisco.com/c/en/us/products/security/managed-detection-response.html",
        "https://www.cisco.com/c/en/us/products/security/incident-response-services.html",
    ],

    # ─── Track A: Big-3 consultancy benchmark for SVC pillar ───
    "PwC": [
        "https://www.pwc.com/gx/en/issues/cybersecurity.html",
        "https://www.pwc.com/gx/en/services/consulting/cybersecurity-privacy.html",
        "https://www.pwc.com/us/en/services/consulting/cybersecurity-risk-regulatory.html",
        "https://www.pwc.com/us/en/services/consulting/cybersecurity-risk-regulatory/managed-services.html",
        "https://www.pwc.com/us/en/services/consulting/cybersecurity-risk-regulatory/cyber-security-strategy.html",
        "https://www.pwc.com/us/en/services/consulting/cybersecurity-risk-regulatory/threat-intelligence.html",
        "https://www.pwc.com/us/en/services/consulting/cybersecurity-risk-regulatory/cyber-incident-response.html",
        "https://www.pwc.com/us/en/services/consulting/cybersecurity-risk-regulatory/identity.html",
        "https://www.pwc.com/us/en/services/consulting/cybersecurity-risk-regulatory/third-party-risk-management.html",
        "https://www.pwc.com/gx/en/issues/cybersecurity/digital-trust-insights.html",
    ],
    "Accenture": [
        "https://www.accenture.com/us-en/services/cybersecurity",
        "https://www.accenture.com/us-en/services/cybersecurity/managed-security",
        "https://www.accenture.com/us-en/services/cybersecurity/cyber-strategy",
        "https://www.accenture.com/us-en/services/cybersecurity/cyber-resilience",
        "https://www.accenture.com/us-en/services/cybersecurity/cyber-protection",
        "https://www.accenture.com/us-en/services/cybersecurity/cyber-defense",
        "https://www.accenture.com/us-en/services/cybersecurity/threat-intelligence",
        "https://www.accenture.com/us-en/services/cybersecurity/cyber-industry",
        "https://www.accenture.com/us-en/services/cybersecurity/identity-access-management",
        "https://www.accenture.com/us-en/insights/security/state-cybersecurity",
    ],
    "Deloitte": [
        "https://www2.deloitte.com/us/en/pages/risk/solutions/cyber-risk-services.html",
        "https://www2.deloitte.com/us/en/pages/risk/solutions/cyber-strategy-services.html",
        "https://www2.deloitte.com/us/en/pages/risk/solutions/cyber-detect-respond.html",
        "https://www2.deloitte.com/us/en/pages/risk/solutions/managed-cyber-services.html",
        "https://www2.deloitte.com/us/en/pages/risk/solutions/identity-services.html",
        "https://www2.deloitte.com/us/en/pages/risk/solutions/data-privacy-protection.html",
        "https://www2.deloitte.com/us/en/pages/risk/solutions/cyber-cloud-services.html",
        "https://www2.deloitte.com/us/en/pages/risk/solutions/application-security.html",
        "https://www2.deloitte.com/us/en/pages/risk/solutions/threat-intelligence.html",
        "https://www2.deloitte.com/us/en/insights/topics/cyber-risk.html",
    ],
}

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
TIMEOUT_MS = 45000
WAIT_MS = 4500
CONCURRENCY = 2
MIN_USEFUL_TEXT = 500    # rendered text shorter than this is treated as bot-blocked
SECOND_WAIT_MS = 6000    # extra wait for SPA hydration when first render too short

# Phrases that indicate the page returned a bot-wall / WAF challenge
BOT_BLOCK_PATTERNS = [
    "vercel security checkpoint",
    "failed to verify your browser",
    "just a moment",          # Cloudflare
    "checking your browser",  # Cloudflare
    "attention required",     # Cloudflare
    "access denied",
    "please verify you are a human",
    "enable javascript and cookies",
    "perimeterx",
    "unfortunately, you are seeing this page",
]

# Lightweight anti-fingerprint init script — patches the most obvious giveaways
# that headless Chromium leaks. Not a full stealth bundle, but enough to clear
# Vercel/Cloudflare "easy" checks for many sites.
STEALTH_INIT_JS = r"""
() => {
  Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
  Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5].map(() => ({ name: 'Chrome PDF Plugin' }))
  });
  window.chrome = { runtime: {}, loadTimes: () => ({}), csi: () => ({}) };
  const originalQuery = window.navigator.permissions && window.navigator.permissions.query;
  if (originalQuery) {
    window.navigator.permissions.query = (parameters) => (
      parameters.name === 'notifications'
        ? Promise.resolve({ state: Notification.permission })
        : originalQuery(parameters)
    );
  }
  // WebGL vendor / renderer spoof
  try {
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function (parameter) {
      if (parameter === 37445) return 'Intel Inc.';
      if (parameter === 37446) return 'Intel Iris OpenGL Engine';
      return getParameter.call(this, parameter);
    };
  } catch (e) {}
}
"""

EXTRA_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
              "image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Chromium";v="126", "Not.A/Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


def _looks_bot_blocked(html: str) -> bool:
    if not html or len(html) < 4000:
        return True
    h = html.lower()
    return any(p in h for p in BOT_BLOCK_PATTERNS)


def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def _cache_path(url: str) -> Path:
    return CACHE_DIR / f"{_sha1(url)}.json"


def _write_cache(
    url: str,
    html: str | None,
    error: str | None = None,
    *,
    lineage_sink=None,
    vendor: str | None = None,
    headed: bool = False,
) -> int:
    """Write an entry into the v1 precyber cache format."""
    # Reuse v1's _html_to_text for byte-identical text shape
    from research_precyber_v1_evidence import _html_to_text
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cp = _cache_path(url)
    text_len = 0
    blocked = False
    if html and len(html) > 1000:
        if _looks_bot_blocked(html):
            blocked = True
        else:
            text = _html_to_text(html)
            text_len = len(text)
            if text_len >= MIN_USEFUL_TEXT:
                record = {
                    "url": url,
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "ok": True,
                    "content_type": "text/html",
                    "text": text[:200_000],
                    "error": None,
                    "render_engine": "playwright",
                }
                cp.write_text(json.dumps(record, ensure_ascii=False, indent=2),
                              encoding="utf-8")
                if lineage_sink is not None:
                    vendor_slug = re.sub(
                        r"[^a-z0-9]+",
                        "-",
                        (vendor or "unknown").lower(),
                    ).strip("-")
                    lineage_sink.capture(
                        vendor_id=f"vendor:{vendor_slug or 'unknown'}",
                        record=record,
                        cache_path=cp,
                        retrieval_method="playwright",
                        headed=headed,
                    )
                return text_len
    record = {
        "url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "ok": False,
        "content_type": "text/html",
        "text": "",
        "error": error or ("bot_blocked" if blocked else
                           ("too_short" if text_len else "empty_html")),
        "render_engine": "playwright",
        "raw_text_len": text_len,
    }
    cp.write_text(json.dumps(record, ensure_ascii=False, indent=2),
                  encoding="utf-8")
    if lineage_sink is not None:
        vendor_slug = re.sub(
            r"[^a-z0-9]+",
            "-",
            (vendor or "unknown").lower(),
        ).strip("-")
        lineage_sink.capture(
            vendor_id=f"vendor:{vendor_slug or 'unknown'}",
            record=record,
            cache_path=cp,
            retrieval_method="playwright",
            headed=headed,
        )
    return 0


# ─────────────────────────────────────────────────────────────────────
# Playwright rendering
# ─────────────────────────────────────────────────────────────────────


async def _render_one(context, url: str) -> str | None:
    page = await context.new_page()
    try:
        try:
            await page.goto(url, wait_until="networkidle", timeout=TIMEOUT_MS)
        except Exception:
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT_MS)
            except Exception as e:
                print(f"    GOTO  {url}  ({e.__class__.__name__})")
                return None
        await page.wait_for_timeout(WAIT_MS)
        try:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(900)
            await page.evaluate("window.scrollTo(0, 0)")
            await page.wait_for_timeout(400)
        except Exception:
            pass
        html = await page.content()
        # If blocked or unexpectedly short, give the SPA more time to hydrate
        # (Next.js app shells often need an extra few seconds for content
        # below the fold to materialize) and try a second snapshot.
        if _looks_bot_blocked(html) or len(html) < 8000:
            await page.wait_for_timeout(SECOND_WAIT_MS)
            try:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(800)
            except Exception:
                pass
            html = await page.content()
        return html
    except Exception as e:
        print(f"    FAIL  {url}  ({e.__class__.__name__})")
        return None
    finally:
        await page.close()


async def _render_vendor(
    browser,
    vendor: str,
    urls: List[str],
    *,
    lineage_sink=None,
    headed: bool = False,
) -> None:
    print(f"\n=== {vendor} ===")
    context = await browser.new_context(
        user_agent=UA,
        viewport={"width": 1366, "height": 900},
        locale="en-US",
        timezone_id="America/New_York",
        extra_http_headers=EXTRA_HEADERS,
    )
    await context.add_init_script(STEALTH_INIT_JS)
    sem = asyncio.Semaphore(CONCURRENCY)

    async def _one(u: str):
        async with sem:
            html = await _render_one(context, u)
            text_len = _write_cache(
                u,
                html,
                lineage_sink=lineage_sink,
                vendor=vendor,
                headed=headed,
            )
            if text_len > 0:
                tag = "OK"
            elif html and _looks_bot_blocked(html):
                tag = "BLOCK"
            elif html:
                tag = "SHORT"
            else:
                tag = "FAIL"
            print(f"  {tag:5} {text_len:>7} chars  {u}")

    await asyncio.gather(*(_one(u) for u in urls))
    await context.close()


async def _render_all(only_vendors: list[str] | None, extra_vendors: list[str],
                     headless: bool = True, lineage_sink=None) -> None:
    targets = dict(ZERO_VENDOR_URLS)
    if only_vendors:
        missing = [v for v in only_vendors if v not in targets]
        if missing:
            print(f"Vendor(s) {missing} not in ZERO_VENDOR_URLS; available: {list(targets)}")
            return
        targets = {v: targets[v] for v in only_vendors}
    for ev in extra_vendors:
        if ev in ZERO_VENDOR_URLS:
            continue
        # Try to discover URLs from the existing v1 catalog
        try:
            from research_precyber_v1_evidence import VENDOR_URLS
            if ev in VENDOR_URLS:
                targets[ev] = list(VENDOR_URLS[ev])
                print(f"(added extra vendor {ev}: {len(targets[ev])} URLs from VENDOR_URLS)")
            else:
                print(f"(skipping extra vendor {ev}: no URLs known)")
        except Exception as e:
            print(f"(could not load VENDOR_URLS: {e})")

    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--no-sandbox",
            ],
        )
        try:
            for vendor, urls in targets.items():
                await _render_vendor(
                    browser,
                    vendor,
                    urls,
                    lineage_sink=lineage_sink,
                    headed=not headless,
                )
        finally:
            await browser.close()


# ─────────────────────────────────────────────────────────────────────
# Re-extract evidence and patch the v3-0 file
# ─────────────────────────────────────────────────────────────────────


def _rescore_vendors(vendor_names: List[str]) -> None:
    """For each named vendor, regenerate sub_pillar_evidence + scores from
    the now-populated cache and write back to TARGET_FILE."""
    print(f"\n--- Re-scoring {len(vendor_names)} vendor(s) ---")
    if not TARGET_FILE.exists():
        print(f"  ERROR: {TARGET_FILE.name} not found")
        return

    data = json.loads(TARGET_FILE.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        vendor_list = data.get("vendors", [])
        wrapper = "dict"
    else:
        vendor_list = data
        wrapper = "list"

    # Late imports (heavy modules)
    from research_precyber_v1_evidence import (
        evidence_for_vendor as v1_evidence_for_vendor,
        discover_vendor_urls as v1_discover_urls,
        compute_pillar_scores as v1_compute_pillar_scores,
        _build_precyber_subpillar_terms,
    )
    from research_precyber_svc_pricing import (
        process_vendor as svc_process_vendor,
        load_schema as svc_load_schema,
    )

    schema_v2 = svc_load_schema()
    # The v1 extractor uses the original 16-cell schema; load whichever exists
    schema_v1_path = ROOT / "Preemptive_Cybersecurity_Schema.json"
    if schema_v1_path.exists():
        schema_v1 = json.loads(schema_v1_path.read_text(encoding="utf-8"))
    else:
        schema_v1 = schema_v2  # fallback
    terms_by_subpillar = _build_precyber_subpillar_terms(schema_v1)

    name_to_idx = {v.get("vendor"): i for i, v in enumerate(vendor_list)}
    for name in vendor_names:
        if name not in name_to_idx:
            print(f"  SKIP {name}: not in {TARGET_FILE.name}")
            continue
        idx = name_to_idx[name]
        v = vendor_list[idx]
        print(f"\n  >>> {name}")

        # 1) Use OUR curated list (or v1 catalog if we don't have an entry)
        urls = ZERO_VENDOR_URLS.get(name) or v1_discover_urls(v, max_urls=0)
        if not urls:
            print("    no URLs known; skipping")
            continue

        # 2) v1 evidence for the 16 product cells (reads from cache; sleep
        #    is tiny since cache is already warm)
        v1_evidence, v1_scores = v1_evidence_for_vendor(
            v,
            urls=urls,
            terms_by_subpillar=terms_by_subpillar,
            schema=schema_v1,
            force_fetch=False,
            max_excerpts_per_subpillar=5,
            sleep_seconds=0.0,
        )

        # 3) SVC + pricing processing for the 8 services cells (also cache-warm)
        v_with_v1 = dict(v)
        v_with_v1["sub_pillar_scores_current"] = dict(
            v.get("sub_pillar_scores_current") or {}
        )
        v_with_v1["sub_pillar_scores_current"].update(v1_scores)
        v_with_v1["sub_pillar_evidence"] = dict(v.get("sub_pillar_evidence") or {})
        v_with_v1["sub_pillar_evidence"].update(v1_evidence)

        try:
            enriched = svc_process_vendor(v_with_v1, schema_v2, force_fetch=False)
        except Exception as e:
            print(f"    process_vendor failed: {e}; falling back to v1-only patch")
            enriched = v_with_v1
            # Compute pillar scores from v1 only
            ps = v1_compute_pillar_scores(v1_scores)
            enriched["pillar_scores"] = ps

        # Persist back to vendor list
        vendor_list[idx] = enriched
        summary = enriched.get("sub_pillar_evidence", {}).get("_vendor_summary", {})
        print(f"    excerpts_total={summary.get('excerpts_total')} "
              f"ok_pages={summary.get('ok_pages')} "
              f"flag={summary.get('flag')}")
        print(f"    pillar_scores={enriched.get('pillar_scores')}")

    if wrapper == "dict":
        data["vendors"] = vendor_list
        out = data
    else:
        out = vendor_list

    TARGET_FILE.write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\n[done] wrote {TARGET_FILE.name}")
    print("Next: python _revalidate_precyber_scoring.py")


# ─────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--vendor", action="append", default=[],
                    help="Render only this vendor (repeatable). Defaults to all ZERO_VENDOR_URLS.")
    ap.add_argument("--extra-vendor", action="append", default=[],
                    help="Add another vendor (looked up in VENDOR_URLS); repeatable")
    ap.add_argument("--render-only", action="store_true",
                    help="Render Playwright pages, skip the rescore step")
    ap.add_argument("--rescore-only", action="store_true",
                    help="Skip rendering; assume cache is already warm")
    ap.add_argument("--headed", action="store_true",
                    help="Run Chromium with a visible window (helps clear Vercel/Cloudflare bot walls)")
    ap.add_argument(
        "--couchdb-project-id",
        help="Research project ID for append-only CouchDB source lineage",
    )
    ap.add_argument(
        "--couchdb-run-id",
        help="Research run ID for append-only CouchDB source lineage",
    )
    args = ap.parse_args()

    lineage_sink = None
    if bool(args.couchdb_project_id) != bool(args.couchdb_run_id):
        ap.error(
            "--couchdb-project-id and --couchdb-run-id must be supplied together"
        )
    if args.couchdb_project_id:
        from gartner_app.research.lineage import LegacyCacheLineageSink

        lineage_sink = LegacyCacheLineageSink.from_settings(
            project_id=args.couchdb_project_id,
            run_id=args.couchdb_run_id,
            actor="worker:render_precyber_zero_vendors",
        )

    if not args.rescore_only:
        asyncio.run(_render_all(args.vendor, args.extra_vendor,
                                headless=not args.headed,
                                lineage_sink=lineage_sink))

    if not args.render_only:
        if args.vendor:
            vendor_names = list(args.vendor)
        else:
            vendor_names = list(ZERO_VENDOR_URLS.keys()) + list(args.extra_vendor)
        _rescore_vendors(vendor_names)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
