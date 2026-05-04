"""Re-score the -05 per-pillar services maturity sub-pillars.

The original run used overly specific multi-word phrases (e.g. "managed ASM",
"CTEM as a service") that produced 0 search-term hits.  This script:

  1. Uses broader, more matchable search terms
  2. Adds co-occurrence scoring (pillar terms + services terms on same page)
  3. Re-reads all cached pages (no new fetches)
  4. Overwrites ONLY the -05 scores/evidence/rationales in the v3-0 file
"""

import json, hashlib, re, sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
from html.parser import HTMLParser

VENDOR_FILE  = Path("Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json")
SCHEMA_FILE  = Path("Preemptive_Cybersecurity_Schema_v2.json")
CACHE_DIR    = Path("research/cache/pages_precyber")
MAX_EXCERPTS = 5

RESCORE_IDS = ["EXM-05", "AMT-05", "ADR-05", "PPM-05"]

# ──────────────────────────────────────────────────────────────
# Improved search terms: shorter phrases that actually appear on
# vendor pages, plus each pillar's domain-specific terms
# ──────────────────────────────────────────────────────────────

# Pillar-specific domain terms (what the -05 sub-pillar is about)
PILLAR_DOMAIN_TERMS: Dict[str, List[str]] = {
    "EXM-05": [
        "attack surface", "exposure management", "vulnerability management",
        "CTEM", "EASM", "external attack surface", "asset discovery",
        "risk exposure", "continuous threat exposure", "vulnerability assessment",
        "attack surface management", "digital footprint", "shadow IT discovery",
        "internet-facing assets", "cyber asset attack surface",
    ],
    "AMT-05": [
        "moving target defense", "AMTD", "runtime protection", "RASP",
        "micro-segmentation", "microsegmentation", "zero trust",
        "credential rotation", "privilege access", "identity protection",
        "network segmentation", "application shielding", "runtime security",
        "dynamic defense", "automated remediation",
    ],
    "ADR-05": [
        "deception", "threat hunting", "threat intelligence",
        "adversary", "cyber threat intelligence", "dark web",
        "digital risk protection", "DRP", "brand protection",
        "takedown", "counter-adversary", "threat actor",
        "intelligence feed", "threat landscape", "IOC",
    ],
    "PPM-05": [
        "breach and attack simulation", "BAS", "penetration testing",
        "pen test", "security validation", "CSPM", "cloud security posture",
        "posture management", "red team", "purple team",
        "continuous validation", "security assessment", "compliance posture",
        "configuration audit", "security benchmark",
    ],
}

# Services/maturity terms that indicate managed/outsourced capability
SERVICES_MATURITY_TERMS = [
    "managed service", "managed services", "as a service", "as-a-service",
    "professional service", "professional services", "consulting",
    "outsourced", "fully managed", "managed offering",
    "service delivery", "service provider", "MSSP", "MDR",
    "dedicated analyst", "dedicated team", "security operations center",
    "SOC-as-a-service", "24/7 monitoring", "24x7", "round-the-clock",
    "service level agreement", "SLA", "managed program",
    "turnkey", "white-glove", "concierge", "service catalog",
    "managed platform", "hosted service", "cloud-delivered",
]

# Refined search terms per -05 sub-pillar: still specific but matchable
SVC_SEARCH_TERMS_V2: Dict[str, List[str]] = {
    "EXM-05": [
        # Specific managed + exposure combos (shorter/more matchable)
        "managed vulnerability", "managed exposure",
        "managed attack surface", "managed discovery",
        "vulnerability management service", "exposure service",
        "vulnerability scanning service", "managed EASM",
        # Platform-as-service patterns
        "attack surface management platform",
        "continuous exposure", "exposure assessment",
        "asset inventory service", "managed remediation",
        # Broader: exposure + managed co-occurrence (scored separately)
    ],
    "AMT-05": [
        "managed zero trust", "zero trust service",
        "managed segmentation", "managed identity",
        "runtime protection service", "managed privilege",
        "identity service", "access management service",
        "managed RASP", "application protection service",
        "managed network defense", "segmentation service",
        "managed access", "identity protection service",
    ],
    "ADR-05": [
        "managed threat hunting", "threat hunting service",
        "managed intelligence", "threat intelligence service",
        "managed deception", "deception service",
        "managed threat intelligence", "digital risk service",
        "managed takedown", "brand protection service",
        "dark web monitoring", "managed SOC",
        "threat hunting program", "intelligence service",
    ],
    "PPM-05": [
        "penetration testing service", "pen testing service",
        "managed penetration", "managed red team",
        "BAS service", "security validation service",
        "managed CSPM", "posture management service",
        "managed assessment", "managed compliance",
        "managed simulation", "continuous testing service",
        "PTaaS", "pen test as a service",
    ],
}


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _cache_path(url: str) -> Path:
    h = hashlib.sha1(url.encode()).hexdigest()
    return CACHE_DIR / f"{h}.json"


def _term_in_text(term: str, text_lower: str) -> bool:
    return term.lower() in text_lower


def _count_term_hits(terms: List[str], text_lower: str) -> int:
    return sum(1 for t in terms if _term_in_text(t, text_lower))


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if 20 <= len(p.strip()) <= 500]


def _candidate_snippets(text: str) -> List[str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    snippets = []
    for ln in lines:
        sents = _split_sentences(ln)
        if sents:
            snippets.extend(sents)
        elif 20 <= len(ln) <= 500:
            snippets.append(ln)
    seen = set()
    out = []
    for s in snippets:
        key = s.lower()[:200]
        if key not in seen:
            seen.add(key)
            out.append(s)
    return out


def _shorten(text: str, maxlen: int = 300) -> str:
    if len(text) <= maxlen:
        return text
    return text[:maxlen - 3] + "..."


# ──────────────────────────────────────────────────────────────
# Co-occurrence scoring: pillar domain + services terms on same page
# ──────────────────────────────────────────────────────────────

def score_cooccurrence(sid: str, pages_text: List[Tuple[str, str]]) -> Tuple[int, int, List[dict]]:
    """Score how many pages have BOTH pillar-domain terms AND services terms.
    Returns (cooccurrence_pages, total_domain_hits, cooccurrence_excerpts)."""
    domain_terms = PILLAR_DOMAIN_TERMS.get(sid, [])
    cooccurrence_pages = 0
    total_domain_hits = 0
    cooccurrence_excerpts = []

    for url, text in pages_text:
        text_lower = text.lower()
        domain_hits = _count_term_hits(domain_terms, text_lower)
        svc_hits = _count_term_hits(SERVICES_MATURITY_TERMS, text_lower)

        if domain_hits > 0:
            total_domain_hits += domain_hits

        if domain_hits >= 2 and svc_hits >= 2:
            cooccurrence_pages += 1

            # Find sentences that contain both domain and services terms
            snippets = _candidate_snippets(text)
            for sent in snippets:
                s_lower = sent.lower()
                d = [t for t in domain_terms if t.lower() in s_lower]
                s = [t for t in SERVICES_MATURITY_TERMS if t.lower() in s_lower]
                if d and s:
                    cooccurrence_excerpts.append({
                        "url": url,
                        "excerpt": _shorten(sent),
                        "domain_terms": d[:3],
                        "service_terms": s[:3],
                    })

    return cooccurrence_pages, total_domain_hits, cooccurrence_excerpts[:MAX_EXCERPTS]


# ──────────────────────────────────────────────────────────────
# Enhanced -05 scoring
# ──────────────────────────────────────────────────────────────

def score_05_subpillar(
    sid: str,
    pages_text: List[Tuple[str, str]],
) -> Tuple[float, Dict[str, Any]]:
    """Score a -05 services maturity sub-pillar using improved methodology."""
    search_terms = SVC_SEARCH_TERMS_V2.get(sid, [])
    domain_terms = PILLAR_DOMAIN_TERMS.get(sid, [])

    all_text = " ".join(t for _, t in pages_text).lower()

    # 1) Direct search term hits (refined terms)
    search_term_hits = _count_term_hits(search_terms, all_text)
    matched_search = [t for t in search_terms if t.lower() in all_text]

    # 2) Co-occurrence scoring
    cooccurrence_pages, domain_hits, cooc_excerpts = score_cooccurrence(sid, pages_text)

    # 3) Collect best excerpts (from search terms + co-occurrence)
    all_hits = []

    for url, text in pages_text:
        snippets = _candidate_snippets(text)
        for sent in snippets:
            s_lower = sent.lower()
            matched = []
            relevance = 0

            # Search term matches (high value)
            for term in search_terms:
                if term.lower() in s_lower:
                    matched.append(term)
                    relevance += 4

            # Domain + services co-occurrence in snippet (medium value)
            d_found = [t for t in domain_terms if t.lower() in s_lower]
            s_found = [t for t in SERVICES_MATURITY_TERMS if t.lower() in s_lower]
            if d_found and s_found:
                matched.extend([f"domain:{d}" for d in d_found[:2]])
                matched.extend([f"svc:{s}" for s in s_found[:2]])
                relevance += len(d_found) * 2 + len(s_found)

            if relevance > 0:
                all_hits.append({
                    "url": url,
                    "excerpt": _shorten(sent),
                    "matched_terms": matched[:8],
                    "relevance_score": relevance,
                })

    all_hits.sort(key=lambda h: h["relevance_score"], reverse=True)
    top_hits = all_hits[:MAX_EXCERPTS]

    # Scoring rubric combining search terms + co-occurrence
    # search_term_hits: specific managed+domain phrases found
    # cooccurrence_pages: pages with both domain and services language
    # domain_hits: how much pillar content exists

    if search_term_hits >= 5 and cooccurrence_pages >= 3:
        score = 4.5
    elif search_term_hits >= 4 and cooccurrence_pages >= 2:
        score = 4.0
    elif search_term_hits >= 3 and cooccurrence_pages >= 2:
        score = 3.75
    elif search_term_hits >= 3 or (search_term_hits >= 2 and cooccurrence_pages >= 3):
        score = 3.5
    elif search_term_hits >= 2 and cooccurrence_pages >= 1:
        score = 3.0
    elif search_term_hits >= 2 or (search_term_hits >= 1 and cooccurrence_pages >= 2):
        score = 2.75
    elif search_term_hits >= 1 and cooccurrence_pages >= 1:
        score = 2.5
    elif search_term_hits >= 1 or cooccurrence_pages >= 2:
        score = 2.25
    elif cooccurrence_pages >= 1:
        score = 2.0
    elif domain_hits >= 5:
        score = 1.5  # Domain present but no managed services signal
    elif top_hits:
        score = 1.0
    else:
        score = 0.0

    score = min(score, 4.75)

    evidence = {
        "source_urls": list({h["url"] for h in top_hits}),
        "excerpts": top_hits,
        "search_term_hits": search_term_hits,
        "matched_search_terms": matched_search,
        "cooccurrence_pages": cooccurrence_pages,
        "domain_term_hits": domain_hits,
        "cooccurrence_excerpts": cooc_excerpts[:3],
        "score": round(score, 2),
        "notes": (
            f"Services maturity: {search_term_hits} direct hits, "
            f"{cooccurrence_pages} co-occurrence pages, "
            f"{domain_hits} domain hits, {len(top_hits)} excerpts."
        ),
    }

    return round(score, 2), evidence


def build_rationale(sid: str, score: float, evidence: Dict) -> str:
    """Build a human-readable rationale for a -05 score."""
    pillar = sid.split("-")[0]
    pillar_names = {
        "EXM": "Exposure Management",
        "AMT": "AMTD",
        "ADR": "Adversary Disruption",
        "PPM": "Posture & Preemptive Management",
    }
    pname = pillar_names.get(pillar, pillar)

    st = evidence.get("search_term_hits", 0)
    cp = evidence.get("cooccurrence_pages", 0)
    dm = evidence.get("domain_term_hits", 0)

    parts = [f"Services maturity for {pname}: scored {score:.1f}/5."]

    if st > 0:
        matched = evidence.get("matched_search_terms", [])
        parts.append(f"Found {st} specific managed-service terms ({', '.join(matched[:5])}).")
    if cp > 0:
        parts.append(f"{cp} pages show co-occurrence of {pname.lower()} domain terms with services/managed language.")
    if dm > 0 and st == 0 and cp == 0:
        parts.append(f"Domain coverage is present ({dm} term hits) but no dedicated managed service offering detected.")
    if score == 0:
        parts.append("No evidence of managed services for this pillar found.")

    return " ".join(parts)


# ──────────────────────────────────────────────────────────────
# Load cached pages for a vendor
# ──────────────────────────────────────────────────────────────

def load_vendor_pages(vendor: Dict) -> List[Tuple[str, str]]:
    """Load ALL cached pages associated with this vendor (existing + SVC/pricing)."""
    pages = []
    seen_urls = set()

    def _try_load(url: str):
        if url in seen_urls:
            return
        seen_urls.add(url)
        cp = _cache_path(url)
        if cp.exists():
            try:
                cached = json.loads(cp.read_text(encoding="utf-8"))
                if cached.get("ok") and cached.get("text"):
                    pages.append((url, cached["text"]))
            except Exception:
                pass

    # URLs from all existing evidence
    for ev in vendor.get("sub_pillar_evidence", {}).values():
        if isinstance(ev, dict):
            for u in ev.get("source_urls", []):
                _try_load(u)

    # URLs from pricing evidence
    for ev in vendor.get("pricing_evidence", {}).values():
        if isinstance(ev, dict):
            for u in ev.get("source_urls", []):
                _try_load(u)

    # URLs from svc_pricing_research metadata
    svc_meta = vendor.get("svc_pricing_research", {})
    for u in svc_meta.get("existing_urls", []):
        _try_load(u)
    for u in svc_meta.get("new_urls_fetched", []):
        _try_load(u)

    # URLs from research metadata
    for u in vendor.get("research", {}).get("urls_fetched", []):
        _try_load(u)

    return pages


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────

def main():
    # Load vendor data
    raw = VENDOR_FILE.read_text(encoding="utf-8-sig")
    data = json.loads(raw)
    vendors = data if isinstance(data, list) else data.get("vendors", [])
    print(f"Loaded {len(vendors)} vendors from {VENDOR_FILE.name}\n")

    updated = 0
    score_totals = {sid: [] for sid in RESCORE_IDS}

    for i, vendor in enumerate(vendors):
        name = vendor.get("vendor", "Unknown")
        pages = load_vendor_pages(vendor)

        if not pages:
            print(f"[{i+1:2d}/51] {name}: 0 pages — SKIP")
            # Set scores to 0
            for sid in RESCORE_IDS:
                vendor.setdefault("sub_pillar_scores_current", {})[sid] = 0.0
                score_totals[sid].append(0.0)
            continue

        results = {}
        for sid in RESCORE_IDS:
            score, evidence = score_05_subpillar(sid, pages)
            results[sid] = (score, evidence)
            score_totals[sid].append(score)

        # Print summary
        score_str = "  ".join(f"{sid}={results[sid][0]:.1f}" for sid in RESCORE_IDS)
        page_count = len(pages)
        print(f"[{i+1:2d}/51] {name} ({page_count}p): {score_str}")

        # Print details for first few or interesting ones
        for sid in RESCORE_IDS:
            sc, ev = results[sid]
            old = vendor.get("sub_pillar_scores_current", {}).get(sid, 0)
            if abs(sc - old) > 0.5 or i < 3:
                st = ev.get("search_term_hits", 0)
                cp = ev.get("cooccurrence_pages", 0)
                dm = ev.get("domain_term_hits", 0)
                mt = ev.get("matched_search_terms", [])
                print(f"         {sid}: {old:.1f} -> {sc:.1f}  (st={st} cp={cp} dm={dm} terms={mt[:4]})")

        # Update vendor record
        for sid in RESCORE_IDS:
            score, evidence = results[sid]
            vendor.setdefault("sub_pillar_scores_current", {})[sid] = score
            vendor.setdefault("sub_pillar_evidence", {})[sid] = evidence
            vendor.setdefault("sub_pillar_rationale_v2_consolidated", {})[sid] = build_rationale(sid, score, evidence)

        # Recalculate pillar scores to include updated -05
        scores = vendor.get("sub_pillar_scores_current", {})
        pillar_scores = vendor.get("pillar_scores", {})
        for pillar in ["EXM", "AMT", "ADR", "PPM"]:
            sp_ids = [f"{pillar}-{j:02d}" for j in range(1, 6)]
            vals = [scores.get(sp, 0.0) for sp in sp_ids]
            pillar_scores[pillar] = round(sum(vals) / len(vals), 2)
        vendor["pillar_scores"] = pillar_scores

        # Recalculate coverage
        covered = [sp for sp, s in scores.items() if s >= 2.0]
        vendor["capability_coverage"] = sorted(covered)
        vendor["capability_coverage_count"] = len(covered)
        n = len(covered)
        if n >= 21: grade = "A"
        elif n >= 16: grade = "B"
        elif n >= 10: grade = "C"
        elif n >= 5: grade = "D"
        else: grade = "F"
        vendor["coverage_grade"] = grade

        updated += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"Re-scored {updated} vendors")
    print(f"\nScore distribution after re-scoring:")
    for sid in RESCORE_IDS:
        vals = score_totals[sid]
        avg = sum(vals) / len(vals)
        nonzero = [v for v in vals if v > 0]
        bins = {}
        for v in vals:
            b = f"{v:.1f}"
            bins[b] = bins.get(b, 0) + 1
        print(f"  {sid}: avg={avg:.2f}, min={min(vals):.1f}, max={max(vals):.1f}, >0={len(nonzero)}/{len(vals)}")
        print(f"         distribution: {dict(sorted(bins.items()))}")

    # Write output
    out_file = VENDOR_FILE  # Overwrite in place
    out_data = vendors  # It was a bare list
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)
    print(f"\nWrote updated data to {out_file.name} ({out_file.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
