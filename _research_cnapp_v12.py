"""
CNAPP Vendor Deep-Dive Research v1.2

Reuses cached HTML pages from v1.1 (research/cache/pages_cnapp/) and produces
higher-quality evidence with:

  - Per-URL excerpt provenance (each evidence source links to the exact page
    where the matching text was found, not just urls[0])
  - Aggressive boilerplate stripping (nav, cookie banners, footer chrome,
    "Sign in / Get a demo" CTAs) so excerpts contain actual capability prose
  - Quality filter: excerpts must contain >= 2 capability tokens OR a multi-word
    capability phrase to count as evidence
  - Capability-specific rationale composition (lists found terms, counts pages
    of evidence, names capability gaps explicitly) instead of a template
  - Confidence tiers: high (>=3 quality excerpts), medium (1-2), low (0)

Reuses VENDOR_URLS, VENDOR_META, SP_TERMS, SP_LABELS, PILLAR_TERMS, CNAPP_GENERIC
from _research_cnapp_v11.py via direct import.

Output: CNAPP Vendor 1-2 Researched.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Reuse vendor / pillar / term registries from v1.1
from _research_cnapp_v11 import (
    PILLARS,
    SUB_PILLAR_IDS,
    SP_TO_PILLAR,
    SP_LABELS,
    SP_TERMS,
    PILLAR_TERMS,
    CNAPP_GENERIC,
    VENDOR_META,
    VENDOR_URLS,
    VENDOR_GROUPS as GROUPS,
)

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
ROOT          = Path(__file__).resolve().parent
SEED_PATH     = ROOT / "CNAPP Vendor 1-0 Seed.json"
V11_PATH      = ROOT / "CNAPP Vendor 1-1 Researched.json"
OUTPUT_PATH   = ROOT / "CNAPP Vendor 1-2 Researched.json"
CACHE_DIR     = ROOT / "research" / "cache" / "pages_cnapp"

# ─────────────────────────────────────────────────────────────────────────────
# Tunables
# ─────────────────────────────────────────────────────────────────────────────
MAX_EVIDENCE_PER_SP = 4
MIN_EXCERPT_LEN     = 80
MAX_EXCERPT_LEN     = 420
WINDOW              = 320           # chars on each side of match
MIN_TOKENS_QUALITY  = 2             # # capability tokens required for "quality" excerpt
MAX_ADJUSTMENT      = 1.0           # max +/- adjustment from seed
SEED_PENALTY_NONE   = 0.80          # multiplier when zero evidence found

# ─────────────────────────────────────────────────────────────────────────────
# Boilerplate patterns to strip
# ─────────────────────────────────────────────────────────────────────────────
BOILERPLATE_PATTERNS = [
    r"cookie\s+(?:settings|preferences|policy|banner|consent)",
    r"modern\s+slavery\s+statement",
    r"sign\s*in\b",
    r"\bget\s+a\s+demo\b",
    r"\bbook\s+a\s+demo\b",
    r"\brequest\s+(?:a\s+)?demo\b",
    r"\bcontact\s+sales\b",
    r"\bstart\s+(?:free|trial)\b",
    r"\bfree\s+trial\b",
    r"\bprivacy\s+policy\b",
    r"\bterms\s+of\s+service\b",
    r"\ball\s+rights\s+reserved\b",
    r"\bsubscribe\s+to\s+our\s+newsletter\b",
    r"\bexperiencing\s+an\s+incident\??",
    r"©\s*\d{4}",
]
BOILERPLATE_RE = re.compile("|".join(BOILERPLATE_PATTERNS), re.IGNORECASE)

NAV_LINE_RE = re.compile(
    r"^\s*(?:platform|solutions?|pricing|resources?|customers?|company|"
    r"products?|partners?|blog|support|login|sign[\s\-]?in|sign[\s\-]?up|"
    r"about(?:\s+us)?|contact(?:\s+us)?|careers?|investors?|legal|"
    r"docs?|documentation|community)\s*$",
    re.IGNORECASE,
)


# Per-sub-pillar generic single-word fallback keywords. These broaden the net
# so that natural prose like "misconfiguration" or "kubernetes" gets caught
# even when the more specific multi-word phrases in SP_TERMS don't appear.
SP_GENERIC: Dict[str, List[str]] = {
    "CSPM-01": ["misconfiguration", "remediate", "remediation", "posture", "openstack", "openshift"],
    "CSPM-02": ["compliance", "benchmark", "framework", "audit"],
    "CSPM-03": ["inventory", "discovery", "asset", "exposure"],
    "CSPM-04": ["prioritization", "risk score", "business impact", "executive", "dashboard", "context"],
    "CWPP-01": ["runtime", "workload", "agent", "agentless", "ebpf", "daemonset", "sidecar", "behavioral"],
    "CWPP-02": ["vulnerability", "exploit", "epss", "reachability"],
    "CWPP-03": ["kubernetes", "container", "k8s", "kspm"],
    "CWPP-04": ["serverless", "agentless", "lambda", "functions"],
    "CIEM-01": ["identity", "permission", "entitlement", "iam"],
    "CIEM-02": ["least privilege", "right-size", "over-privileged", "access review"],
    "CIEM-03": ["non-human", "service account", "machine identity", "secrets"],
    "CIEM-04": ["just-in-time", "privilege escalation", "temporary access", "standing access"],
    "SHIFT-01": ["iac", "terraform", "cloudformation", "policy as code"],
    "SHIFT-02": ["image scanning", "registry", "container image", "image vulnerability"],
    "SHIFT-03": ["ci/cd", "pipeline", "github actions", "developer"],
    "SHIFT-04": ["sca", "composition", "sbom", "mbom", "aibom", "dependency"],
    "SHIFT-05": ["jira", "servicenow", "slack", "teams", "pagerduty", "webhook", "ticketing", "workflow"],
    "CDR-01":  ["threat detection", "alert", "mitre", "anomaly"],
    "CDR-02":  ["attack path", "graph", "blast radius", "lateral"],
    "CDR-03":  ["forensics", "investigation", "timeline", "incident"],
    "CDR-04":  ["automated response", "playbook", "soar", "remediation"],
    "DSPM-01": ["sensitive data", "classification", "pii", "discovery"],
    "DSPM-02": ["data exposure", "data access", "public data", "data risk"],
    "DSPM-03": ["shadow data", "data flow", "lineage", "forgotten"],
    "DSPM-04": ["gdpr", "hipaa", "data residency", "regulatory"],
    "FRNG-01": ["ai", "llm", "genai", "ai security"],
    "FRNG-02": ["api security", "api inventory", "shadow api", "api risk"],
    "FRNG-03": ["microsegmentation", "network", "vpc", "east-west"],
    "FRNG-04": ["secrets", "api key", "credential", "token"],
}


# ─────────────────────────────────────────────────────────────────────────────
# Cache helpers
# ─────────────────────────────────────────────────────────────────────────────
def cache_path_for(url: str) -> Path:
    h = hashlib.md5(url.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{h}.html"


def load_cached(url: str) -> Optional[str]:
    p = cache_path_for(url)
    if not p.exists():
        return None
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Cleaner: HTML → readable text with boilerplate stripped
# ─────────────────────────────────────────────────────────────────────────────
def html_to_text_clean(html: str) -> str:
    text = re.sub(r"<(script|style|noscript|svg|nav|header|footer|aside|form)[^>]*>.*?</\1>",
                  " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    text = re.sub(r"<head[^>]*>.*?</head>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    # Block elements → newline
    text = re.sub(
        r"<(?:br|p|div|h[1-6]|li|tr|td|th|section|article)[^>]*>",
        "\n", text, flags=re.IGNORECASE,
    )
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"[ \t]+", " ", text)

    # Filter out boilerplate-heavy lines and nav lines
    cleaned_lines: List[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if NAV_LINE_RE.match(line):
            continue
        if len(line) < 25 and BOILERPLATE_RE.search(line):
            continue
        # Skip lines that are mostly punctuation/single words
        if len(line) < 15 and not re.search(r"[a-z]{4,}", line, re.IGNORECASE):
            continue
        cleaned_lines.append(line)

    out = "\n".join(cleaned_lines)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip()


# ─────────────────────────────────────────────────────────────────────────────
# Per-page evidence extraction
# ─────────────────────────────────────────────────────────────────────────────
def find_excerpts_in_page(text: str, terms: List[str]) -> List[dict]:
    """
    Scan one page's cleaned text for capability term hits and return one excerpt
    per non-overlapping window. Each result has: text, matched_terms, quality.
    """
    if not text:
        return []
    ltext = text.lower()
    used_ranges: List[Tuple[int, int]] = []
    excerpts: List[dict] = []

    # Sort terms longest-first so phrases match before single keywords
    sorted_terms = sorted(set(terms), key=lambda s: -len(s))

    for term in sorted_terms:
        tl = term.lower()
        pos = 0
        while True:
            idx = ltext.find(tl, pos)
            if idx == -1:
                break

            # Skip if this match falls inside a window we already captured
            if any(s <= idx <= e for s, e in used_ranges):
                pos = idx + len(tl)
                continue

            start = max(0, idx - WINDOW)
            end   = min(len(text), idx + len(term) + WINDOW)
            # Snap to word boundaries
            if start > 0:
                space = text.find(" ", start)
                if space != -1 and space - start < 60:
                    start = space + 1
            if end < len(text):
                space = text.rfind(" ", 0, end)
                if space != -1 and end - space < 60:
                    end = space

            snip = text[start:end].strip()
            snip = re.sub(r"\s+", " ", snip)

            if len(snip) < MIN_EXCERPT_LEN:
                pos = idx + len(tl)
                continue

            # Skip if excerpt is mostly boilerplate
            bp_hits = len(BOILERPLATE_RE.findall(snip))
            if bp_hits >= 3:
                pos = idx + len(tl)
                continue

            # Count distinct capability terms in this window. Multi-word
            # phrases are stronger signals than single keywords.
            snip_lower = snip.lower()
            matched = [t for t in sorted_terms if t.lower() in snip_lower]
            phrase_matches = sum(1 for t in matched if " " in t or "-" in t)
            single_matches = len(matched) - phrase_matches
            # Quality if: any 2-word phrase + at least 1 other match,
            # OR 3+ single-keyword matches,
            # OR 2+ phrase matches alone.
            if phrase_matches >= 2:
                quality = "high"
            elif phrase_matches >= 1 and len(matched) >= 2:
                quality = "high"
            elif single_matches >= 3:
                quality = "high"
            else:
                quality = "low"

            used_ranges.append((start, end))
            excerpts.append({
                "text":           snip[:MAX_EXCERPT_LEN],
                "matched_terms":  matched[:6],
                "primary_term":   term,
                "quality":        quality,
            })

            pos = end
            if len(excerpts) >= 8:
                return excerpts

    return excerpts


# ─────────────────────────────────────────────────────────────────────────────
# Score calibration
# ─────────────────────────────────────────────────────────────────────────────
def score_with_evidence(per_page_evidence: List[dict], seed_score: float) -> Tuple[float, float]:
    """
    Returns (calibrated_score, evidence_strength 0..1).
    Strength combines (a) number of pages with quality evidence, (b) total quality
    excerpts, (c) presence of multi-word phrase matches.
    """
    if not per_page_evidence:
        return max(0.0, round(seed_score * SEED_PENALTY_NONE, 1)), 0.0

    high_quality = [e for ev in per_page_evidence for e in ev["excerpts"]
                    if e["quality"] == "high"]
    pages_with_quality = sum(
        1 for ev in per_page_evidence
        if any(e["quality"] == "high" for e in ev["excerpts"])
    )

    # Strength: 0.4 * pages, 0.1 per quality excerpt, capped at 1.0
    strength = min(1.0, 0.4 * pages_with_quality + 0.1 * len(high_quality))
    if not high_quality:
        # Only low-quality matches
        strength = min(0.4, 0.15 * len(per_page_evidence))

    adjusted = seed_score + (strength - 0.5) * 2 * MAX_ADJUSTMENT
    adjusted = max(0.0, min(5.0, adjusted))
    adjusted = round(adjusted * 2) / 2  # 0.5 steps
    return adjusted, round(strength, 2)


# ─────────────────────────────────────────────────────────────────────────────
# Rationale composition (capability-specific, not template)
# ─────────────────────────────────────────────────────────────────────────────
def compose_rationale(vendor: str, sp_id: str, score: float,
                      per_page_evidence: List[dict], meta: dict) -> str:
    sp_name = SP_LABELS[sp_id]
    pillar  = SP_TO_PILLAR[sp_id]
    products = ", ".join(meta.get("products", [])[:3]) or vendor

    quality_excerpts = [
        (ev["url"], e) for ev in per_page_evidence
        for e in ev["excerpts"] if e["quality"] == "high"
    ]
    low_excerpts = [
        (ev["url"], e) for ev in per_page_evidence
        for e in ev["excerpts"] if e["quality"] == "low"
    ]
    pages_with_evidence = sum(1 for ev in per_page_evidence if ev["excerpts"])

    # Aggregate term hits across all pages
    all_terms: List[str] = []
    for ev in per_page_evidence:
        for e in ev["excerpts"]:
            all_terms.extend(e["matched_terms"])
    unique_terms = sorted(set(all_terms), key=lambda t: -all_terms.count(t))[:5]

    if not per_page_evidence:
        return (
            f"No public-page evidence found for {sp_name} ({sp_id}). "
            f"Searched {vendor} product pages for terms including "
            f"'{SP_TERMS[sp_id][0]}', '{SP_TERMS[sp_id][1] if len(SP_TERMS[sp_id]) > 1 else ''}' "
            f"with no relevant matches. Score {score}/5 reflects analyst seed estimate "
            f"discounted for absent public documentation. Pillar: {pillar}. "
            f"Recommendation: review vendor demo, RFI response, or analyst report for confirmation."
        )

    if quality_excerpts:
        url, ex = quality_excerpts[0]
        terms_str = ", ".join(f'"{t}"' for t in unique_terms) if unique_terms else "capability keywords"
        snippet = ex["text"][:240].replace("\n", " ").strip()
        return (
            f"{vendor} ({products}) — score {score}/5 for {sp_name}. "
            f"Found {len(quality_excerpts)} high-quality and {len(low_excerpts)} supporting "
            f"reference(s) across {pages_with_evidence} page(s) matching {terms_str}. "
            f'Primary evidence ({url}): "{snippet}…" '
            f"Pillar: {pillar}. "
            f"Analyst context: {meta.get('analyst', 'no analyst note')[:180]}"
        )

    # Only low-quality matches
    url, ex = low_excerpts[0]
    snippet = ex["text"][:200].replace("\n", " ").strip()
    return (
        f"{vendor} ({products}) — score {score}/5 for {sp_name}. "
        f"Limited evidence: only single-keyword matches across {pages_with_evidence} page(s); "
        f"no clear capability-statement language found. "
        f'Best supporting reference ({url}): "{snippet}…" '
        f"Pillar: {pillar}. Confidence is low; verify via demo or RFI."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Build evidence_sources list with proper per-page provenance
# ─────────────────────────────────────────────────────────────────────────────
def build_evidence_sources(per_page_evidence: List[dict]) -> List[dict]:
    sources: List[dict] = []

    # 1. High-quality matches first, one per URL
    seen_urls: set = set()
    for ev in per_page_evidence:
        url = ev["url"]
        if url in seen_urls:
            continue
        for e in ev["excerpts"]:
            if e["quality"] == "high":
                sources.append({
                    "url":            url,
                    "tier":           "A",
                    "type":           "Vendor Documentation",
                    "relevance":      0.9,
                    "excerpt":        e["text"][:MAX_EXCERPT_LEN],
                    "matched_terms":  e["matched_terms"],
                    "quality":        "high",
                })
                seen_urls.add(url)
                break
        if len(sources) >= MAX_EVIDENCE_PER_SP:
            break

    # 2. Fill with low-quality matches if we have room
    if len(sources) < MAX_EVIDENCE_PER_SP:
        for ev in per_page_evidence:
            url = ev["url"]
            if url in seen_urls:
                continue
            for e in ev["excerpts"]:
                if e["quality"] == "low":
                    sources.append({
                        "url":            url,
                        "tier":           "A",
                        "type":           "Vendor Documentation",
                        "relevance":      0.6,
                        "excerpt":        e["text"][:MAX_EXCERPT_LEN],
                        "matched_terms":  e["matched_terms"],
                        "quality":        "low",
                    })
                    seen_urls.add(url)
                    break
            if len(sources) >= MAX_EVIDENCE_PER_SP:
                break

    return sources


# ─────────────────────────────────────────────────────────────────────────────
# Per-vendor research using cache only
# ─────────────────────────────────────────────────────────────────────────────
def deep_research_vendor(vendor_entry: dict) -> dict:
    name = vendor_entry["vendor"]
    meta = VENDOR_META.get(name, {})
    urls = VENDOR_URLS.get(name, [])
    result = deepcopy(vendor_entry)

    # Load + clean every cached page once
    page_texts: List[Tuple[str, str]] = []   # (url, cleaned_text)
    for url in urls:
        html = load_cached(url)
        if not html:
            continue
        cleaned = html_to_text_clean(html)
        if cleaned:
            page_texts.append((url, cleaned))

    print(f"  > {name:25s}  cached pages: {len(page_texts)}/{len(urls)}")

    sub_scores:  Dict[str, float] = {}
    rationales:  Dict[str, dict]  = {}

    for sp_id in SUB_PILLAR_IDS:
        pillar     = SP_TO_PILLAR[sp_id]
        seed_score = float(meta.get("seed_scores", {}).get(pillar, 0))

        # Search terms: sub-pillar-specific phrases + all pillar-level phrases
        # + a small set of generic capability keywords so we don't miss
        # natural-language matches like "misconfiguration" or "runtime"
        sp_keywords = SP_GENERIC.get(sp_id, [])
        terms = (list(SP_TERMS.get(sp_id, []))
                 + list(PILLAR_TERMS.get(pillar, []))
                 + sp_keywords)

        # Scan each page independently so we keep URL provenance
        per_page_evidence: List[dict] = []
        for url, text in page_texts:
            excerpts = find_excerpts_in_page(text, terms)
            if excerpts:
                per_page_evidence.append({
                    "url":      url,
                    "excerpts": excerpts,
                })

        score, strength = score_with_evidence(per_page_evidence, seed_score)
        sub_scores[sp_id] = score

        sources = build_evidence_sources(per_page_evidence)
        high_count = sum(1 for s in sources if s["quality"] == "high")
        if   high_count >= 3: confidence = "high"
        elif high_count >= 1: confidence = "medium"
        elif sources:         confidence = "low"
        else:                 confidence = "none"

        rationales[sp_id] = {
            "score":               score,
            "rationale":           compose_rationale(name, sp_id, score, per_page_evidence, meta),
            "evidence_sources":    sources,
            "confidence":          confidence,
            "evidence_count":      sum(len(ev["excerpts"]) for ev in per_page_evidence),
            "evidence_strength":   strength,
            "seed_score":          seed_score,
            "pages_with_evidence": len(per_page_evidence),
        }

    # Pillar score = mean of 4 sub-pillars rounded to 0.5
    pillar_scores: Dict[str, float] = {}
    for pillar in PILLARS:
        sps  = [sp for sp in SUB_PILLAR_IDS if SP_TO_PILLAR[sp] == pillar]
        vals = [sub_scores[sp] for sp in sps]
        avg  = sum(vals) / len(vals) if vals else 0.0
        pillar_scores[pillar] = round(avg * 2) / 2

    scored_count = sum(1 for v in sub_scores.values() if v >= 1)
    if   scored_count >= 22: grade = "A"
    elif scored_count >= 17: grade = "B"
    elif scored_count >= 11: grade = "C"
    elif scored_count >= 6:  grade = "D"
    else:                    grade = "F"

    result["pillar_scores"]              = pillar_scores
    result["sub_pillar_scores_current"]  = sub_scores
    result["capability_coverage_count"]  = scored_count
    result["coverage_grade"]             = grade
    result["rationales_v1"]              = rationales
    result["research_metadata"] = {
        "researched_at":  datetime.now(timezone.utc).isoformat(),
        "pages_fetched":  len(page_texts),
        "total_urls":     len(urls),
        "schema_version": "CNAPP_Schema.json v1.1",
        "research_pass":  "v1.2 deep-dive (cache-based, per-page provenance)",
        "analyst_seed":   meta.get("analyst", ""),
    }
    return result


# ─────────────────────────────────────────────────────────────────────────────
# IO + driver
# ─────────────────────────────────────────────────────────────────────────────
def load_seed() -> dict:
    with open(SEED_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_existing_output() -> dict:
    if OUTPUT_PATH.exists():
        with open(OUTPUT_PATH, encoding="utf-8") as f:
            return json.load(f)
    # Otherwise start from v1.1 if present, else seed
    src = V11_PATH if V11_PATH.exists() else SEED_PATH
    with open(src, encoding="utf-8") as f:
        data = json.load(f)
    data["assessment_type"] = "deep_research_v1.2"
    return data


def save_output(data: dict) -> None:
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def vendor_index(vendors: list) -> Dict[str, int]:
    return {v["vendor"]: i for i, v in enumerate(vendors)}


def run_group(group_num: int) -> None:
    if group_num not in GROUPS:
        raise SystemExit(f"Unknown group {group_num}; valid: {sorted(GROUPS.keys())}")

    group = GROUPS[group_num]
    print(f"\n{'='*60}")
    print(f"  Group {group_num}: {group['label']} (DEEP DIVE v1.2)")
    print(f"  Vendors: {', '.join(group['vendors'])}")
    print(f"{'='*60}\n")

    data = load_existing_output()
    idx  = vendor_index(data["vendors"])

    for vendor_name in group["vendors"]:
        if vendor_name not in idx:
            print(f"  [WARN] vendor '{vendor_name}' not found in dataset, skipping")
            continue
        i = idx[vendor_name]
        data["vendors"][i] = deep_research_vendor(data["vendors"][i])

    save_output(data)
    print(f"\n  [SAVED] {OUTPUT_PATH.name}\n")


def main() -> None:
    p = argparse.ArgumentParser(description="CNAPP deep-dive research v1.2 (cache-based)")
    p.add_argument("--group", type=int, help="Run a single group (1-5)")
    p.add_argument("--all", action="store_true", help="Run all groups")
    p.add_argument("--list-groups", action="store_true", help="List groups and exit")
    args = p.parse_args()

    if args.list_groups:
        for n, g in GROUPS.items():
            print(f"  Group {n}: {g['label']}")
            for v in g["vendors"]:
                print(f"    - {v}")
        return

    if args.all:
        for n in sorted(GROUPS.keys()):
            run_group(n)
        return

    if args.group:
        run_group(args.group)
        return

    p.print_help()


if __name__ == "__main__":
    main()
