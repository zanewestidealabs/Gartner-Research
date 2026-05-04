"""
extract_offsec_excerpts.py — Offensive Security Evidence Excerpt Extraction
===========================================================================

Fetches vendor web pages from source_urls and vendor websites, extracts text,
finds sentences matching Offensive Security schema criteria and pillar terms,
and populates the excerpts array in each sub_pillar_evidence entry.

Adapted from extract_mdr_excerpts.py for Offensive Security pillars
(ASM, VUL, OFT, APP, REM).

Features:
  - HTTP fetch with retry and user-agent rotation
  - Page content caching (research/cache/pages_offsec/)
  - Sentence extraction with term matching
  - Relevance scoring (schema criteria > pillar terms > generic)
  - Progress tracking and batch processing
  - Updates Offensive Security Vendor 2-1 Consolidated.json in-place

Usage:
  python extract_offsec_excerpts.py                    # full run
  python extract_offsec_excerpts.py --max-vendors 5    # test with 5
  python extract_offsec_excerpts.py --force-fetch       # re-fetch cached pages
  python extract_offsec_excerpts.py --dry-run            # show stats without writing
  python extract_offsec_excerpts.py --batch 1/3          # process batch 1 of 3
  python extract_offsec_excerpts.py --merge               # merge batch files
"""

import argparse
import hashlib
import json
import random
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent
VENDOR_FILE = ROOT / "Offensive Security Vendor 2-1 Consolidated.json"
SCHEMA_FILE = ROOT / "Offensive_Security_Schema.json"
CACHE_DIR = ROOT / "research" / "cache" / "pages_offsec"

PILLARS = ["ASM", "VUL", "OFT", "APP", "REM"]
SUB_PILLAR_IDS = [f"{p}-{i:02d}" for p in PILLARS for i in range(1, 6)]

MAX_EXCERPTS_PER_SP = 5
FETCH_SLEEP = 0.3  # seconds between HTTP fetches (low — different domains)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]


# ─────────────────────────────────────────────────────────────
# Offensive Security pillar-specific search terms
# ─────────────────────────────────────────────────────────────

PILLAR_TERMS = {
    "ASM": [
        "easm", "attack surface management", "external attack surface",
        "shadow it", "asset discovery", "asset inventory", "digital footprint",
        "cloud posture", "cspm", "cnapp", "cloud security posture",
        "internet-facing", "attack surface monitoring", "exposure",
        "certificate transparency", "subdomain enumeration", "dns analysis",
        "orphaned asset", "unknown asset", "shadow asset",
        "continuous monitoring", "drift detection", "configuration drift",
        "cloud asset", "hybrid cloud", "multi-cloud",
        "asset classification", "criticality scoring", "cmdb",
        "kubernetes", "container", "serverless",
    ],
    "VUL": [
        "vulnerability scanner", "vulnerability assessment", "vulnerability management",
        "cve", "cvss", "epss", "vulnerability prioritization",
        "risk-based", "risk scoring", "rbvm",
        "authenticated scanning", "unauthenticated scanning",
        "agent-based", "agentless", "nessus", "qualys",
        "configuration assessment", "cis benchmark", "disa stig",
        "compliance scanning", "security baseline", "hardening",
        "exploitability", "exploit validation", "proof of exploit",
        "false positive", "compensating control",
        "threat intelligence", "threat correlation", "cisa kev",
        "exploit availability", "in-the-wild", "dark web",
        "vulnerability intelligence", "threat feed",
    ],
    "OFT": [
        "penetration testing", "pentest", "pen test", "automated pentest",
        "breach and attack simulation", "bas", "attack simulation",
        "red team", "purple team", "adversary simulation",
        "adversary emulation", "mitre att&ck", "att&ck", "ttp",
        "attack path", "attack graph", "choke point",
        "lateral movement", "privilege escalation", "credential harvesting",
        "safe exploitation", "exploit execution", "kill chain",
        "security control validation", "detection gap",
        "ransomware simulation", "data exfiltration",
        "continuous validation", "security validation",
        "evasion", "obfuscation", "living off the land", "fileless",
    ],
    "APP": [
        "sast", "dast", "iast", "rasp",
        "static analysis", "dynamic analysis", "code scanning",
        "application security", "appsec", "application testing",
        "api security", "api testing", "graphql", "rest api", "openapi",
        "software composition analysis", "sca", "sbom",
        "open source", "dependency", "license compliance",
        "ci/cd", "pipeline", "devops", "devsecops", "shift-left",
        "github", "gitlab", "jenkins", "azure devops",
        "container scanning", "iac", "terraform", "cloudformation",
        "infrastructure as code", "kubernetes security",
        "ide integration", "developer experience", "pull request",
        "owasp", "code review", "secure coding",
    ],
    "REM": [
        "remediation", "patching", "patch management",
        "auto-remediation", "automated fix", "patch deployment",
        "exposure management", "exposure prioritization",
        "risk scoring", "unified risk", "posture scoring",
        "servicenow", "jira", "ticketing", "itsm",
        "workflow", "sla tracking", "escalation",
        "closed-loop", "verification", "re-scanning", "regression",
        "mttr", "fix rate", "remediation rate",
        "executive dashboard", "board-ready", "compliance reporting",
        "risk posture", "trending", "metrics",
    ],
}

# Generic offensive security terms (lower priority matching)
OFFSEC_GENERIC_TERMS = [
    "security", "vulnerability", "threat", "risk", "exposure",
    "platform", "solution", "capability", "detection", "protection",
    "automated", "continuous", "real-time", "integration",
    "enterprise", "cloud", "managed",
]


# ─────────────────────────────────────────────────────────────
# HTML text extraction (lightweight, no external dependencies)
# ─────────────────────────────────────────────────────────────

def html_to_text(html: str) -> str:
    """Convert HTML to plain text using regex-based extraction."""
    # Remove script, style, noscript, svg blocks entirely
    text = re.sub(r'<(script|style|noscript|svg)[^>]*>.*?</\1>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', ' ', text, flags=re.DOTALL)
    # Remove <head> block
    text = re.sub(r'<head[^>]*>.*?</head>', ' ', text, flags=re.DOTALL | re.IGNORECASE)
    # Insert newlines for block tags
    text = re.sub(r'<(?:br|p|div|h[1-6]|li|tr|td|th|section|article|header|footer|nav|main)[^>]*>', '\n', text, flags=re.IGNORECASE)
    # Strip remaining tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decode HTML entities
    text = unescape(text)
    # Collapse whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n[ \t]*', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ─────────────────────────────────────────────────────────────
# HTTP fetch with retry and caching
# ─────────────────────────────────────────────────────────────

def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()


def fetch_url(url: str, *, max_retries: int = 2) -> Tuple[Optional[str], Optional[str]]:
    """Fetch a URL, return (content_type, html) or (None, None)."""
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED

    for attempt in range(max_retries):
        timeout = 12.0 + attempt * 5.0
        ua = random.choice(USER_AGENTS)
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": ua,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "identity",
                "Connection": "keep-alive",
            },
            method="GET",
        )
        try:
            handler = urllib.request.HTTPSHandler(context=ctx)
            opener = urllib.request.build_opener(handler)
            with opener.open(req, timeout=timeout) as resp:
                ctype = resp.headers.get("Content-Type", "")
                raw = resp.read()
                text = raw.decode("utf-8", errors="replace")
                return ctype, text
        except (urllib.error.URLError, urllib.error.HTTPError, OSError,
                TimeoutError, ConnectionError, ssl.SSLError) as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt + random.uniform(0.5, 2.0))
            continue
        except Exception:
            break
    return None, None


def get_or_fetch_page(url: str, *, force: bool = False) -> Dict[str, Any]:
    """Fetch with caching."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / f"{_sha1(url)}.json"

    if cache_path.exists() and not force:
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            if cached.get("ok") is True:
                return cached
        except Exception:
            pass

    ctype, html = fetch_url(url)

    if html is None:
        record = {
            "url": url,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "ok": False,
            "text": "",
            "error": "fetch_failed",
        }
    else:
        text = html_to_text(html)
        record = {
            "url": url,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "ok": True,
            "text": text[:200_000],
            "error": None,
        }

    cache_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


# ─────────────────────────────────────────────────────────────
# Sentence extraction and term matching
# ─────────────────────────────────────────────────────────────

def split_sentences(text: str) -> List[str]:
    """Split text into candidate sentences/snippets."""
    raw = re.split(r'(?<=[.!?])\s+|\n+', text)
    sentences = []
    for s in raw:
        s = s.strip()
        if len(s) < 25:
            continue
        if len(s) > 500:
            parts = re.split(r'[;,]\s+', s)
            for p in parts:
                p = p.strip()
                if len(p) >= 25:
                    sentences.append(p[:400])
        else:
            sentences.append(s)
    return sentences


def term_in_text(term: str, text_lower: str) -> bool:
    """Check if a term appears in text (case-insensitive)."""
    t = term.lower()
    if t in text_lower:
        return True
    t_clean = re.sub(r'[^a-z0-9 ]', '', t)
    if t_clean and t_clean in text_lower:
        return True
    return False


def find_matching_terms(text_lower: str, terms: List[str]) -> List[str]:
    """Find which terms match in the text."""
    return [t for t in terms if term_in_text(t, text_lower)]


# ─────────────────────────────────────────────────────────────
# Schema criteria loader
# ─────────────────────────────────────────────────────────────

_SKIP_WORDS = {"within", "across", "through", "including", "based", "their",
               "these", "those", "with", "that", "from", "have", "been", "this",
               "such", "each", "other", "both", "than", "more", "into", "over"}

def load_schema_criteria() -> Dict[str, Dict[str, Any]]:
    """Load sub-pillar criteria from Offensive Security schema."""
    with open(SCHEMA_FILE, "r", encoding="utf-8-sig") as f:
        raw = json.load(f)
    body = raw.get("offensive_security_taxonomy_v1.0", raw)
    sp_data = body.get("sub_pillars", {})

    result = {}
    for sp_id, info in sp_data.items():
        if sp_id not in SUB_PILLAR_IDS:
            continue
        criteria = info.get("what_to_verify_publicly", [])
        search_terms = info.get("search_terms", [])

        # Extract key terms from criteria text
        criteria_terms = set()
        for c in criteria:
            words = re.findall(r'\b[a-z][a-z ]{3,}\b', c.lower())
            for w in words:
                w = w.strip()
                if len(w) >= 5 and w not in _SKIP_WORDS:
                    criteria_terms.add(w)
        # Also add schema-defined search terms
        for t in search_terms:
            if len(t) >= 3:
                criteria_terms.add(t.lower())

        result[sp_id] = {
            "name": info.get("name", sp_id),
            "criteria": criteria,
            "criteria_terms": list(criteria_terms),
        }
    return result


# ─────────────────────────────────────────────────────────────
# URL collection from vendor evidence
# ─────────────────────────────────────────────────────────────

def collect_vendor_urls(vendor: Dict[str, Any]) -> List[str]:
    """Collect all unique fetchable URLs for this vendor."""
    urls = set()

    # Vendor website
    website = vendor.get("website", "")
    if website and website.startswith("http"):
        urls.add(website)

    # URLs from source entries in evidence
    for sp_id, ev in vendor.get("sub_pillar_evidence", {}).items():
        # New format: sources array with url field
        for src in ev.get("sources", []):
            url = src.get("url", "")
            if url and url.startswith("http"):
                urls.add(url)
        # Old format: source_urls list
        for url in ev.get("source_urls", []):
            if url and url.startswith("http"):
                urls.add(url)

    return sorted(urls)


# ─────────────────────────────────────────────────────────────
# Excerpt extraction for a single vendor
# ─────────────────────────────────────────────────────────────

def extract_excerpts_for_vendor(
    vendor: Dict[str, Any],
    schema_criteria: Dict[str, Dict[str, Any]],
    *,
    force_fetch: bool = False,
) -> Tuple[Dict[str, List[Dict[str, Any]]], int, int]:
    """
    Fetch all source URLs for a vendor, extract text, and find
    relevant excerpts for each sub-pillar.

    Returns: (dict[sp_id -> list of excerpt dicts], pages_fetched, pages_ok)
    """
    all_urls = collect_vendor_urls(vendor)

    # Fetch all pages
    pages: List[Tuple[str, str]] = []  # (url, text)
    pages_fetched = 0
    pages_ok = 0
    for url in all_urls:
        rec = get_or_fetch_page(url, force=force_fetch)
        pages_fetched += 1
        if rec.get("ok") and rec.get("text"):
            pages.append((url, rec["text"]))
            pages_ok += 1
        time.sleep(FETCH_SLEEP + random.uniform(0.3, 1.0))

    # Extract excerpts per sub-pillar
    result = {}
    for sp_id in SUB_PILLAR_IDS:
        pillar = sp_id.split("-")[0]
        sp_info = schema_criteria.get(sp_id, {})
        criteria_terms = sp_info.get("criteria_terms", [])
        pillar_terms = PILLAR_TERMS.get(pillar, [])

        hits = []
        for url, text in pages:
            sentences = split_sentences(text)
            for sent in sentences:
                s_lower = sent.lower()

                criteria_matches = find_matching_terms(s_lower, criteria_terms)
                pillar_matches = find_matching_terms(s_lower, pillar_terms)
                generic_matches = find_matching_terms(s_lower, OFFSEC_GENERIC_TERMS)

                all_matches = list(set(criteria_matches + pillar_matches + generic_matches))
                if not all_matches:
                    continue

                # Relevance score: criteria × 3, pillar × 2, generic × 1
                relevance = len(criteria_matches) * 3 + len(pillar_matches) * 2 + len(generic_matches)

                hits.append({
                    "url": url,
                    "excerpt": sent[:300],
                    "matched_terms": all_matches[:8],
                    "relevance_score": relevance,
                })

        # Sort by relevance descending, deduplicate similar excerpts
        hits.sort(key=lambda h: h["relevance_score"], reverse=True)

        selected = []
        for h in hits:
            if len(selected) >= MAX_EXCERPTS_PER_SP:
                break
            h_prefix = h["excerpt"][:80].lower()
            is_dup = any(
                h_prefix in s["excerpt"][:100].lower() or
                s["excerpt"][:80].lower() in h_prefix
                for s in selected
            )
            if not is_dup:
                selected.append(h)

        result[sp_id] = selected

    return result, pages_fetched, pages_ok


# ─────────────────────────────────────────────────────────────
# Main pipeline
# ─────────────────────────────────────────────────────────────

def merge_batches():
    """Merge batch output files into the main v2.1 file."""
    print("Merging batch files...")
    with open(VENDOR_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    batch_files = sorted(ROOT.glob("offsec_batch_*.json"))
    if not batch_files:
        print("ERROR: No batch files found (offsec_batch_*.json)")
        return

    print(f"  Found {len(batch_files)} batch files")
    vendors_updated = 0
    total_excerpts = 0

    for bf in batch_files:
        print(f"  Reading {bf.name}...")
        with open(bf, "r", encoding="utf-8") as f:
            batch_data = json.load(f)

        # Build lookup of batch vendors by name
        batch_vendors = {v["vendor"]: v for v in batch_data["vendors"]}

        for vendor in data["vendors"]:
            vname = vendor["vendor"]
            if vname in batch_vendors:
                bv = batch_vendors[vname]
                # Copy over evidence with excerpts
                if "sub_pillar_evidence" in bv:
                    vendor["sub_pillar_evidence"] = bv["sub_pillar_evidence"]
                    for sp_id, ev in bv["sub_pillar_evidence"].items():
                        total_excerpts += len(ev.get("excerpts", []))
                vendors_updated += 1

    data['seed_notes'] = (
        'Consolidated scoring with enriched rationales, source citations, and '
        'automated excerpt extraction. Evidence includes real text excerpts from '
        'vendor web pages with relevance scoring and matched term analysis.'
    )

    with open(VENDOR_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nMerge complete:")
    print(f"  Vendors updated: {vendors_updated}")
    print(f"  Total excerpts:  {total_excerpts}")
    print(f"  Written to {VENDOR_FILE.name}")

    # Clean up batch files
    for bf in batch_files:
        bf.unlink()
        print(f"  Removed {bf.name}")


def main():
    parser = argparse.ArgumentParser(description="Extract OffSec vendor evidence excerpts")
    parser.add_argument("--max-vendors", type=int, default=0, help="Limit vendors processed (0=all)")
    parser.add_argument("--force-fetch", action="store_true", help="Re-fetch cached pages")
    parser.add_argument("--dry-run", action="store_true", help="Show stats without writing")
    parser.add_argument("--batch", type=str, default="", help="Batch spec e.g. '1/3' for batch 1 of 3")
    parser.add_argument("--merge", action="store_true", help="Merge batch output files")
    args = parser.parse_args()

    if args.merge:
        merge_batches()
        return

    print("=" * 60)
    print("Offensive Security Evidence Excerpt Extraction Pipeline")
    print("=" * 60)

    print("\nLoading vendor data and schema...")
    with open(VENDOR_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    schema_criteria = load_schema_criteria()
    print(f"  Schema: {len(schema_criteria)} sub-pillar criteria loaded")
    for sp_id, info in sorted(schema_criteria.items())[:3]:
        print(f"    {sp_id}: {len(info['criteria_terms'])} criteria terms")

    vendors = data["vendors"]
    if args.max_vendors > 0:
        vendors = vendors[:args.max_vendors]

    # Batch slicing
    batch_num = 0
    batch_total = 1
    if args.batch:
        parts = args.batch.split("/")
        batch_num = int(parts[0])
        batch_total = int(parts[1])
        chunk_size = len(vendors) // batch_total
        start = (batch_num - 1) * chunk_size
        end = start + chunk_size if batch_num < batch_total else len(vendors)
        vendors = vendors[start:end]
        print(f"  Batch {batch_num}/{batch_total}: vendors {start+1}-{end} ({len(vendors)} vendors)")

    print(f"\nProcessing {len(vendors)} vendors...")
    total_excerpts = 0
    total_pages_fetched = 0
    total_pages_ok = 0
    vendors_with_excerpts = 0
    sp_excerpt_counts = {sp: 0 for sp in SUB_PILLAR_IDS}

    for vi, vendor in enumerate(vendors):
        vname = vendor["vendor"]
        print(f"\n  [{vi+1}/{len(vendors)}] {vname}", flush=True)

        urls = collect_vendor_urls(vendor)
        print(f"    URLs to fetch: {len(urls)}")

        try:
            excerpts_by_sp, fetched, ok = extract_excerpts_for_vendor(
                vendor, schema_criteria, force_fetch=args.force_fetch
            )
        except Exception as e:
            print(f"    ERROR: {e}")
            continue

        total_pages_fetched += fetched
        total_pages_ok += ok
        print(f"    Pages fetched: {ok}/{fetched} OK")

        # Update evidence entries with excerpts
        evidence = vendor.get("sub_pillar_evidence", {})
        vendor_excerpt_count = 0
        sps_with_hits = 0

        for sp_id in SUB_PILLAR_IDS:
            sp_excerpts = excerpts_by_sp.get(sp_id, [])
            if sp_id in evidence:
                # Merge excerpts into existing evidence — preserve rationale and sources
                evidence[sp_id]["excerpts"] = sp_excerpts
                if sp_excerpts:
                    # Add source_urls from excerpts
                    excerpt_urls = list(set(e["url"] for e in sp_excerpts))
                    existing_source_urls = evidence[sp_id].get("source_urls", [])
                    all_urls = list(set(existing_source_urls + excerpt_urls))
                    evidence[sp_id]["source_urls"] = all_urls

                    # Compute hit_count and specific_hit_count
                    all_terms = set()
                    specific_terms = set()
                    for ex in sp_excerpts:
                        for t in ex.get("matched_terms", []):
                            all_terms.add(t)
                            # criteria_terms are "specific"
                            sp_info = schema_criteria.get(sp_id, {})
                            if t in sp_info.get("criteria_terms", []):
                                specific_terms.add(t)

                    evidence[sp_id]["hit_count"] = len(all_terms)
                    evidence[sp_id]["specific_hit_count"] = len(specific_terms)

                    # Add notes
                    top_score = sp_excerpts[0]["relevance_score"] if sp_excerpts else 0
                    evidence[sp_id]["notes"] = (
                        f"Automated excerpt extraction; {len(sp_excerpts)} excerpts from "
                        f"{len(excerpt_urls)} pages. Top relevance: {top_score}. "
                        f"Analyst review recommended for scoring adjustment."
                    )

            vendor_excerpt_count += len(sp_excerpts)
            sp_excerpt_counts[sp_id] += len(sp_excerpts)
            if sp_excerpts:
                sps_with_hits += 1

        total_excerpts += vendor_excerpt_count
        if vendor_excerpt_count > 0:
            vendors_with_excerpts += 1

        print(f"    Excerpts: {vendor_excerpt_count} across {sps_with_hits}/{len(SUB_PILLAR_IDS)} sub-pillars")

    # Update metadata
    data['seed_notes'] = (
        'Consolidated scoring with enriched rationales, source citations, and '
        'automated excerpt extraction. Evidence includes real text excerpts from '
        'vendor web pages with relevance scoring and matched term analysis.'
    )

    if not args.dry_run:
        if args.batch:
            out_file = ROOT / f"offsec_batch_{batch_num}.json"
            # Write just the processed vendors to a batch file
            batch_data = dict(data)
            batch_data["vendors"] = vendors
            print(f"\nWriting batch file...")
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(batch_data, f, indent=2, ensure_ascii=False)
            print(f"Written to {out_file.name}")
        else:
            print(f"\nWriting updated file...")
            with open(VENDOR_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Written to {VENDOR_FILE.name}")
    else:
        print(f"\n[DRY RUN] Would write to {VENDOR_FILE.name}")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'=' * 60}")
    print(f"  Vendors processed:      {len(vendors)}")
    print(f"  Vendors with excerpts:  {vendors_with_excerpts}")
    print(f"  Pages fetched:          {total_pages_ok}/{total_pages_fetched} OK")
    print(f"  Total excerpts:         {total_excerpts}")
    avg_per_vendor = total_excerpts / max(len(vendors), 1)
    avg_per_sp = total_excerpts / max(len(vendors) * len(SUB_PILLAR_IDS), 1)
    print(f"  Avg excerpts/vendor:    {avg_per_vendor:.1f}")
    print(f"  Avg excerpts/sub-pillar: {avg_per_sp:.2f}")

    # Sub-pillar coverage
    print(f"\n  Excerpt coverage by sub-pillar:")
    for sp_id in SUB_PILLAR_IDS:
        name = schema_criteria.get(sp_id, {}).get("name", sp_id)
        cnt = sp_excerpt_counts[sp_id]
        print(f"    {sp_id} ({name}): {cnt} excerpts")

    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
