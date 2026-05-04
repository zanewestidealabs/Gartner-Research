"""
extract_mdr_excerpts.py — MDR Vendor Evidence Excerpt Extraction Pipeline
=========================================================================

Fetches vendor web pages from source_urls, extracts text, finds sentences
matching MDR schema criteria and pillar terms, and populates the excerpts
array in each sub_pillar_evidence entry.

Mirrors the approach used in research_trism_v1_claims.py but adapted for
MDR-specific pillars (TDR, PTI, ADA, DIS, IRA, AIO, AID, SOG).

Features:
  - HTTP fetch with retry and user-agent rotation
  - Page content caching (research/cache/pages_mdr/)
  - Sentence extraction with term matching
  - Relevance scoring (schema criteria > pillar terms > generic)
  - Progress tracking and batch processing
  - Updates MDR Services Vendor 2-0 Researched.json in-place

Usage:
  python extract_mdr_excerpts.py                    # full run
  python extract_mdr_excerpts.py --max-vendors 5    # test with 5
  python extract_mdr_excerpts.py --force-fetch       # re-fetch cached pages
  python extract_mdr_excerpts.py --dry-run            # show stats without writing
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
VENDOR_FILE = ROOT / "MDR Services Vendor 2-0 Researched.json"
SCHEMA_FILE = ROOT / "MDR_Services_Schema.json"
CACHE_DIR = ROOT / "research" / "cache" / "pages_mdr"

PILLARS = ["TDR", "PTI", "ADA", "DIS", "IRA", "AIO", "AID", "SOG"]
SUB_PILLAR_IDS = [f"{p}-{i:02d}" for p in PILLARS for i in range(1, 5)]

MAX_EXCERPTS_PER_SP = 5
FETCH_SLEEP = 1.5  # seconds between HTTP fetches

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]


# ─────────────────────────────────────────────────────────────
# MDR Pillar-specific search terms
# ─────────────────────────────────────────────────────────────

PILLAR_TERMS = {
    "TDR": [
        "signal correlation", "alert triage", "xdr", "cross-domain", "multi-source",
        "telemetry", "edr", "ndr", "siem", "detection rule", "detection coverage",
        "alert grouping", "alert prioritization", "severity assessment",
        "real-time detection", "behavioral detection", "anomaly detection",
        "mitre att&ck", "threat detection", "investigation", "response",
    ],
    "PTI": [
        "threat intelligence", "ioc", "indicator of compromise", "threat feed",
        "ttp", "tactics techniques", "att&ck", "cti", "dark web", "darknet",
        "geopolitical", "campaign tracking", "threat landscape", "threat actor",
        "intelligence operationalization", "threat briefing", "attribution",
    ],
    "ADA": [
        "deception", "honeypot", "honeytoken", "decoy", "breadcrumb",
        "amtd", "moving target defense", "runtime mutation", "micro-segmentation",
        "attack surface", "easm", "shadow it", "asset discovery", "exposure",
        "counter-adversary", "takedown", "threat hunting", "hunt operations",
    ],
    "DIS": [
        "deepfake", "synthetic media", "voice clone", "ai-generated",
        "bec", "business email compromise", "impersonation", "executive protection",
        "social engineering", "phishing", "narrative attack", "influence operation",
        "brand protection", "brand monitoring", "typosquatting", "domain squatting",
        "identity impersonation", "account takeover",
    ],
    "IRA": [
        "incident response", "incident scoping", "severity assessment",
        "evidence preservation", "containment", "isolation", "quarantine",
        "recovery", "restoration", "eradication", "persistence",
        "post-incident", "after-action", "root cause", "lessons learned",
        "ir retainer", "breach response", "forensic",
    ],
    "AIO": [
        "ai detection", "ml-driven", "ai-assisted", "ai-powered",
        "ai triage", "ai investigation", "ai-automated", "ai-generated",
        "ai response", "ai-autonomous", "adaptive response", "ai remediation",
        "explainable ai", "ai transparency", "audit trail", "ai accuracy",
        "charlotte ai", "purple ai", "copilot", "generative ai", "llm",
        "machine learning", "neural", "natural language",
    ],
    "AID": [
        "security llm", "domain-specific ai", "custom model", "fine-tuning",
        "model governance", "model lifecycle", "model versioning", "drift detection",
        "ai supply chain", "model provenance", "prompt injection", "adversarial testing",
        "ai innovation", "ai pipeline", "ai roadmap", "ai investment",
        "nist ai rmf", "eu ai act", "responsible ai", "trustworthy ai",
    ],
    "SOG": [
        "soc", "24/7", "follow-the-sun", "security operation",
        "soc 2", "iso 27001", "compliance", "certification", "fedramp",
        "customer portal", "dashboard", "self-service", "reporting",
        "sla", "mean time", "mttr", "mttd", "response time",
        "service level", "analyst", "staffing", "onboarding",
    ],
}

# Generic MDR terms (lower priority matching)
MDR_GENERIC_TERMS = [
    "managed detection", "mdr", "managed security", "mssp",
    "security monitoring", "threat management", "cyber defense",
    "security service", "managed service", "soc as a service",
]


# ─────────────────────────────────────────────────────────────
# HTML text extraction (lightweight, no external dependencies)
# ─────────────────────────────────────────────────────────────

def html_to_text(html: str) -> str:
    """Convert HTML to plain text using regex-based extraction.
    
    Removes script/style blocks first, then strips tags, keeping
    visible text content. More robust than HTMLParser for modern SPAs.
    """
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
    for attempt in range(max_retries):
        timeout = 10.0 + attempt * 5.0
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
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                ctype = resp.headers.get("Content-Type", "")
                raw = resp.read()
                text = raw.decode("utf-8", errors="replace")
                return ctype, text
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt + random.uniform(0.5, 2.0))
            continue
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
    # Split on sentence boundaries and newlines
    raw = re.split(r'(?<=[.!?])\s+|\n+', text)
    sentences = []
    for s in raw:
        s = s.strip()
        if len(s) < 25:  # too short to be meaningful
            continue
        if len(s) > 500:  # too long — split further
            parts = re.split(r'[;,]\s+', s)
            for p in parts:
                p = p.strip()
                if len(p) >= 25:
                    sentences.append(p[:400])
        else:
            sentences.append(s)
    return sentences


def term_in_text(term: str, text_lower: str) -> bool:
    """Check if a term appears in text (case-insensitive, word boundary aware)."""
    t = term.lower()
    if t in text_lower:
        return True
    # Try without special chars
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

def load_schema_criteria() -> Dict[str, Dict[str, Any]]:
    """Load sub-pillar criteria from MDR schema."""
    with open(SCHEMA_FILE, "r", encoding="utf-8-sig") as f:
        raw = json.load(f)
    body = raw.get("mdr_services_taxonomy_v1.0", raw)
    sp_data = body.get("sub_pillars", {})

    result = {}
    for sp_id, info in sp_data.items():
        criteria = info.get("what_to_verify_publicly",
                            info.get("ai_evaluation_criteria", []))
        # Extract key terms from criteria text
        criteria_terms = set()
        for c in criteria:
            # Extract meaningful multi-word phrases
            words = re.findall(r'\b[a-z][a-z ]{3,}\b', c.lower())
            for w in words:
                w = w.strip()
                if len(w) >= 5 and w not in {"within", "across", "through", "including", "based"}:
                    criteria_terms.add(w)
        result[sp_id] = {
            "name": info.get("name", sp_id),
            "criteria": criteria,
            "criteria_terms": list(criteria_terms),
        }
    return result


# ─────────────────────────────────────────────────────────────
# Excerpt extraction for a single vendor
# ─────────────────────────────────────────────────────────────

def extract_excerpts_for_vendor(
    vendor: Dict[str, Any],
    schema_criteria: Dict[str, Dict[str, Any]],
    *,
    force_fetch: bool = False,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch all source URLs for a vendor, extract text, and find
    relevant excerpts for each sub-pillar.

    Returns: dict[sp_id -> list of excerpt dicts]
    """
    evidence = vendor.get("sub_pillar_evidence", {})

    # Collect all unique URLs across all sub-pillars
    all_urls = set()
    for sp_id in SUB_PILLAR_IDS:
        sp_ev = evidence.get(sp_id, {})
        for url in sp_ev.get("source_urls", []):
            if url and url.startswith("http"):
                all_urls.add(url)

    # Also grab vendor website if available
    website = vendor.get("website", "")
    if website and website.startswith("http"):
        all_urls.add(website)

    # Fetch all pages
    pages: List[Tuple[str, str]] = []  # (url, text)
    for url in sorted(all_urls):
        rec = get_or_fetch_page(url, force=force_fetch)
        if rec.get("ok") and rec.get("text"):
            pages.append((url, rec["text"]))
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

                # Match criteria terms (highest weight)
                criteria_matches = find_matching_terms(s_lower, criteria_terms)
                # Match pillar terms (medium weight)
                pillar_matches = find_matching_terms(s_lower, pillar_terms)
                # Match generic MDR terms (lowest weight)
                generic_matches = find_matching_terms(s_lower, MDR_GENERIC_TERMS)

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
        
        # Deduplicate: skip excerpts that are >70% similar to already selected
        selected = []
        for h in hits:
            if len(selected) >= MAX_EXCERPTS_PER_SP:
                break
            # Simple dedup: check if first 80 chars overlap
            h_prefix = h["excerpt"][:80].lower()
            is_dup = any(h_prefix in s["excerpt"][:100].lower() or 
                        s["excerpt"][:80].lower() in h_prefix
                        for s in selected)
            if not is_dup:
                selected.append(h)

        result[sp_id] = selected

    return result


# ─────────────────────────────────────────────────────────────
# Main pipeline
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Extract MDR vendor evidence excerpts")
    parser.add_argument("--max-vendors", type=int, default=0, help="Limit vendors processed (0=all)")
    parser.add_argument("--force-fetch", action="store_true", help="Re-fetch cached pages")
    parser.add_argument("--dry-run", action="store_true", help="Show stats without writing")
    args = parser.parse_args()

    print("Loading MDR vendor data and schema...")
    with open(VENDOR_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    schema_criteria = load_schema_criteria()

    vendors = data["vendors"]
    if args.max_vendors > 0:
        vendors = vendors[:args.max_vendors]

    print(f"Processing {len(vendors)} vendors...")
    total_excerpts = 0
    total_pages_fetched = 0
    vendors_with_excerpts = 0

    for vi, vendor in enumerate(vendors):
        vname = vendor["vendor"]
        print(f"  [{vi+1}/{len(vendors)}] {vname}...", end=" ", flush=True)

        try:
            excerpts_by_sp = extract_excerpts_for_vendor(
                vendor, schema_criteria, force_fetch=args.force_fetch
            )
        except Exception as e:
            print(f"ERROR: {e}")
            continue

        # Update evidence entries with excerpts
        evidence = vendor.get("sub_pillar_evidence", {})
        vendor_excerpt_count = 0
        for sp_id in SUB_PILLAR_IDS:
            sp_excerpts = excerpts_by_sp.get(sp_id, [])
            if sp_id in evidence:
                evidence[sp_id]["excerpts"] = sp_excerpts
            else:
                evidence[sp_id] = {
                    "source_urls": [],
                    "excerpts": sp_excerpts,
                    "notes": "",
                }
            vendor_excerpt_count += len(sp_excerpts)

        # Also update the rationale key_evidence with top excerpts
        rationale = vendor.get("sub_pillar_rationale_v2", {})
        for sp_id in SUB_PILLAR_IDS:
            sp_excerpts = excerpts_by_sp.get(sp_id, [])
            if sp_id in rationale and sp_excerpts:
                rationale[sp_id]["key_evidence"] = [
                    e["excerpt"][:250] for e in sp_excerpts[:4]
                ]
                rationale[sp_id]["additional_sources_found"] = len(sp_excerpts)

        total_excerpts += vendor_excerpt_count
        if vendor_excerpt_count > 0:
            vendors_with_excerpts += 1

        print(f"{vendor_excerpt_count} excerpts across {len(SUB_PILLAR_IDS)} sub-pillars")

    # Update metadata
    if "v2_research_metadata" in data:
        data["v2_research_metadata"]["excerpts_extracted_at"] = datetime.now(timezone.utc).isoformat()
        data["v2_research_metadata"]["excerpt_extraction_script"] = "extract_mdr_excerpts.py"
        data["v2_research_metadata"]["total_excerpts"] = total_excerpts
        data["v2_research_metadata"]["vendors_with_excerpts"] = vendors_with_excerpts

    if not args.dry_run:
        print(f"\nWriting updated file...")
        with open(VENDOR_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Written to {VENDOR_FILE.name}")
    else:
        print(f"\n[DRY RUN] Would write to {VENDOR_FILE.name}")

    print(f"\n=== Summary ===")
    print(f"  Vendors processed: {len(vendors)}")
    print(f"  Vendors with excerpts: {vendors_with_excerpts}")
    print(f"  Total excerpts extracted: {total_excerpts}")
    avg = total_excerpts / max(len(vendors), 1)
    print(f"  Average excerpts per vendor: {avg:.1f}")
    print(f"  Average excerpts per sub-pillar: {total_excerpts / max(len(vendors) * 32, 1):.1f}")


if __name__ == "__main__":
    main()
