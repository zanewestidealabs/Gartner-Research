"""
JS-render the CNAPP vendor pages that plain urllib couldn't get useful HTML from
(blocked by bot wall, served empty SPA shell, or 404 on direct fetch but exists
behind hash routing). Writes the rendered HTML into the same MD5-keyed cache
file used by _research_cnapp_v11/_v12 so the deep-dive can re-extract.

Usage:
    python _render_cnapp_js.py            # render the default JS_URLS list
    python _render_cnapp_js.py --vendor "Sophos"  # only that vendor
"""
from __future__ import annotations
import argparse
import asyncio
from typing import Dict, List

from playwright.async_api import async_playwright

from _research_cnapp_v11 import CACHE_DIR, _cache_path

# Pages where the prior urllib fetch returned 0 bytes / 403 / 404
JS_URLS: Dict[str, List[str]] = {
    "Sophos": [
        "https://www.sophos.com/en-us/products/cloud-native-security",
        "https://www.sophos.com/en-us/cybersecurity-explained/cnapp",
        "https://www.sophos.com/en-us/cybersecurity-explained/cloud-security",
        "https://www.sophos.com/en-us/cybersecurity-explained/what-is-cspm",
        "https://www.sophos.com/en-us/products/managed-detection-and-response",
    ],
    "Check Point": [
        "https://www.checkpoint.com/cloudguard/workload/",
        "https://www.checkpoint.com/cloudguard/spectral/",
        "https://www.checkpoint.com/cloudguard/cnapp/",
        "https://www.checkpoint.com/cloudguard/cloud-network-security/",
        "https://www.checkpoint.com/cloudguard/cloud-detection-response/",
    ],
    "Sweet Security": [
        "https://sweet.security/platform",
        "https://sweet.security/runtime-cspm",
        "https://sweet.security/cloud-detection-response",
        "https://sweet.security/non-human-identity",
    ],
    "Upwind": [
        "https://www.upwind.io/platform",
        "https://www.upwind.io/feature/cspm",
        "https://www.upwind.io/feature/cwpp",
        "https://www.upwind.io/feature/dspm",
        "https://www.upwind.io/feature/api-security",
        "https://www.upwind.io/feature/runtime",
    ],
    "Caveonix": [
        "https://www.caveonix.com/products/",
        "https://www.caveonix.com/solutions/cloud-security/",
        "https://www.caveonix.com/platform/",
    ],
    "Bitdefender": [
        "https://www.bitdefender.com/business/products/gravityzone-cloud-security.html",
        "https://www.bitdefender.com/business/enterprise-products/cloud-security.html",
        "https://www.bitdefender.com/business/solutions/cloud-workload-security.html",
    ],
    "Uptycs": [
        "https://www.uptycs.com/platform",
        "https://www.uptycs.com/products",
        "https://www.uptycs.com/products/kubernetes-and-container-security",
        "https://www.uptycs.com/products/cloud-workload-protection",
    ],
    "Orca Security": [
        "https://orca.security/platform/cspm/",
        "https://orca.security/platform/cwpp/",
        "https://orca.security/platform/ciem/",
        "https://orca.security/platform/dspm/",
        "https://orca.security/platform/cdr/",
        "https://orca.security/cloud-security/cnapp/",
    ],
    "AccuKnox": [
        "https://www.accuknox.com/zero-trust-security",
        "https://www.accuknox.com/kubernetes-security",
        "https://www.accuknox.com/saas",
    ],
    "Snyk": [
        "https://snyk.io/product/cloud-security/",
        "https://snyk.io/solutions/cloud-native-application-security/",
        "https://snyk.io/product/container-security/",
    ],
    "Tenable": [
        "https://www.tenable.com/products/tenable-cloud-security/cnapp",
        "https://www.tenable.com/products/tenable-cloud-security/cspm",
        "https://www.tenable.com/products/tenable-cloud-security/ciem",
        "https://www.tenable.com/products/tenable-cloud-security/dspm",
    ],
    "Rapid7": [
        "https://www.rapid7.com/products/insightcloudsec/cspm/",
        "https://www.rapid7.com/products/insightcloudsec/cwpp/",
        "https://www.rapid7.com/products/insightcloudsec/ciem/",
        "https://www.rapid7.com/products/exposure-command/",
    ],
    "Datadog": [
        "https://www.datadoghq.com/product/cloud-security-management/cspm/",
        "https://www.datadoghq.com/product/cloud-security-management/ciem/",
        "https://www.datadoghq.com/product/cloud-security-management/sensitive-data-scanner/",
        "https://www.datadoghq.com/product/cloud-workload-security/",
    ],
    "Trend Micro": [
        "https://www.trendmicro.com/en_us/business/products/hybrid-cloud/cloud-one-container-security.html",
        "https://www.trendmicro.com/en_us/business/campaigns/trend-vision-one.html",
    ],
    "Fortinet": [
        "https://www.fortinet.com/products/public-cloud-security/lacework-forticnapp.html",
        "https://www.fortinet.com/products/public-cloud-security/forticnapp",
    ],
    "Wiz": [
        "https://www.wiz.io/solutions/cloud-detection-response",
        "https://www.wiz.io/solutions/code-security",
        "https://www.wiz.io/solutions/api-security",
        "https://www.wiz.io/solutions/kubernetes-security",
    ],
    "CrowdStrike": [
        "https://www.crowdstrike.com/platform/cloud-security/cloud-detection-response/",
    ],
    "SentinelOne": [
        "https://www.sentinelone.com/products/singularity-cloud-security/",
        "https://www.sentinelone.com/platform/singularity-data-lake/",
    ],
    "Sysdig": [
        "https://sysdig.com/kubernetes-security/",
        "https://sysdig.com/cloud-detection-and-response/",
        "https://sysdig.com/runtime-security/",
        "https://sysdig.com/use-cases/ciem/",
    ],
    "Qualys": [
        "https://www.qualys.com/apps/container-runtime-security/",
        "https://www.qualys.com/apps/cloud-security/",
        "https://www.qualys.com/solutions/cloud-security/",
    ],
}

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

CONCURRENCY = 4
TIMEOUT_MS  = 30000
WAIT_MS     = 2500   # extra time after networkidle for SPA hydration


async def render(context, url: str) -> tuple[bool, int, str]:
    page = await context.new_page()
    try:
        try:
            await page.goto(url, wait_until="networkidle", timeout=TIMEOUT_MS)
        except Exception:
            # Some sites never reach networkidle — fall back to domcontentloaded
            await page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT_MS)
        await page.wait_for_timeout(WAIT_MS)
        # Scroll so lazy-loaded content materializes
        try:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(800)
            await page.evaluate("window.scrollTo(0, 0)")
        except Exception:
            pass
        html = await page.content()
        return True, len(html.encode("utf-8")), html
    except Exception as e:
        return False, 0, str(e)
    finally:
        await page.close()


async def render_vendor(browser, vendor: str, urls: List[str]) -> None:
    context = await browser.new_context(
        user_agent=UA,
        viewport={"width": 1366, "height": 900},
        locale="en-US",
    )
    print(f"\n=== {vendor} ===")
    sem = asyncio.Semaphore(CONCURRENCY)

    async def one(url: str):
        async with sem:
            cp = _cache_path(url)
            ok, size, payload = await render(context, url)
            if ok and size > 5000:
                CACHE_DIR.mkdir(parents=True, exist_ok=True)
                cp.write_text(payload, encoding="utf-8")
                print(f"  RENDER  {size:>7}b  {url}")
            else:
                tag = "EMPTY" if ok else "FAIL "
                print(f"  {tag}            {url}  ({size}b)")

    await asyncio.gather(*(one(u) for u in urls))
    await context.close()


async def main_async(only_vendor: str | None) -> None:
    targets = JS_URLS if only_vendor is None else {only_vendor: JS_URLS[only_vendor]}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for vendor, urls in targets.items():
            await render_vendor(browser, vendor, urls)
        await browser.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vendor", help="Render only this vendor")
    args = ap.parse_args()
    asyncio.run(main_async(args.vendor))


if __name__ == "__main__":
    main()
