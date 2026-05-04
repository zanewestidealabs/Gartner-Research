"""
JS-render OEDIV SecuRisk pages that plain urllib couldn't fetch (blocked by
bot wall / TLS fingerprint / JS challenge on www.oediv-securisk.de).

Writes rendered HTML into the same SHA1-keyed JSON cache files that
_research_oediv.py / _research_proficio.py read on next run, so re-running
the deep-dive will pick up the rendered pages without re-fetching.

Usage:
    python _render_oediv_js.py
"""
from __future__ import annotations
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright

# Reuse the exact helpers the research pipeline uses
from _research_oediv import (
    CACHE_DIR_CAP,
    CACHE_DIR_PRC,
    PROFICIO_URLS as OEDIV_URLS,  # variable kept the proficio name in the clone
    _sha1,
    html_to_text,
)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

CONCURRENCY = 3
TIMEOUT_MS = 30000
WAIT_MS = 2500   # extra wait after networkidle for SPA hydration
MIN_USEFUL_BYTES = 3000


async def _dismiss_cookie_banner(page) -> None:
    """Best-effort: accept/decline cookie banners (esp. Cyfidelity SPA) so the
    underlying content renders into the DOM."""
    selectors = [
        'button:has-text("Alle Cookies erlauben")',
        'button:has-text("Alle akzeptieren")',
        'button:has-text("Accept all")',
        'button:has-text("Accept All")',
        'button:has-text("Nur erforderliche Cookies erlauben")',
        'button:has-text("Nur notwendige")',
        'button:has-text("Allow all")',
        '[id*="cookie"] button',
    ]
    for sel in selectors:
        try:
            btn = await page.query_selector(sel)
            if btn:
                await btn.click(timeout=1500)
                await page.wait_for_timeout(800)
                return
        except Exception:
            continue


async def render(context, url: str) -> tuple[bool, int, str]:
    page = await context.new_page()
    try:
        try:
            await page.goto(url, wait_until="networkidle", timeout=TIMEOUT_MS)
        except Exception:
            await page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT_MS)
        await page.wait_for_timeout(WAIT_MS)
        # Cyfidelity SPA hides content behind a cookie consent dialog;
        # dismiss before scraping so the body has real text.
        if "cyfidelity.com" in url:
            await _dismiss_cookie_banner(page)
            await page.wait_for_timeout(2000)
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


def _write_cache(cache_dir: Path, url: str, html: str) -> int:
    cache_dir.mkdir(parents=True, exist_ok=True)
    text = html_to_text(html)
    record = {
        "url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "ok": True,
        "text": text[:200_000],
        "error": None,
    }
    cache_path = cache_dir / f"{_sha1(url)}.json"
    cache_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(record["text"])


async def main_async() -> None:
    sem = asyncio.Semaphore(CONCURRENCY)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=UA,
            viewport={"width": 1366, "height": 900},
            locale="en-US",
        )

        ok_count = 0
        fail_count = 0
        empty_count = 0

        async def one(url: str):
            nonlocal ok_count, fail_count, empty_count
            async with sem:
                ok, size, payload = await render(context, url)
                if ok and size >= MIN_USEFUL_BYTES:
                    text_len_cap = _write_cache(CACHE_DIR_CAP, url, payload)
                    text_len_prc = _write_cache(CACHE_DIR_PRC, url, payload)
                    print(f"  RENDER  html={size:>7}b  text={text_len_cap:>6}c  {url}")
                    ok_count += 1
                elif ok:
                    print(f"  EMPTY   html={size:>7}b                        {url}")
                    empty_count += 1
                else:
                    print(f"  FAIL    {payload[:80]:<80}  {url}")
                    fail_count += 1

        await asyncio.gather(*(one(u) for u in OEDIV_URLS))
        await context.close()
        await browser.close()

        print()
        print(f"Summary: rendered={ok_count}  empty={empty_count}  failed={fail_count}  total={len(OEDIV_URLS)}")


if __name__ == "__main__":
    asyncio.run(main_async())
