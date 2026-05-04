import argparse
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent
DEFAULT_VENDOR_FILE = ROOT / "Vendor 4-0 Validated.json"
DEFAULT_SCHEMA_FILE = ROOT / "schema4-0_enhanced.json"
DEFAULT_OUTPUT_FILE = ROOT / "Vendor 4-1 Researched.json"
CACHE_DIR = ROOT / "research" / "cache" / "pages"

URL_RE = re.compile(r"https?://[^\s)\]\}\">,]+")

PILLARS = ["PLA", "INV", "REM", "PMG", "LAW"]
SUBPILLAR_IDS = [
    "PLA-01",
    "PLA-02",
    "PLA-03",
    "PLA-04",
    "INV-01",
    "INV-02",
    "INV-03",
    "INV-04",
    "REM-01",
    "REM-02",
    "REM-03",
    "REM-04",
    "PMG-01",
    "PMG-02",
    "PMG-03",
    "PMG-04",
    "LAW-01",
    "LAW-02",
    "LAW-03",
    "LAW-04",
]


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: List[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        text = data.strip()
        if not text:
            return
        self._chunks.append(text)

    def get_text(self) -> str:
        return "\n".join(self._chunks)


def _safe_json_load(path: Path) -> Any:
    # Some files in this workspace may contain a UTF-8 BOM.
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8"), usedforsecurity=False).hexdigest()


def _fetch_url(url: str, timeout_seconds: float = 20.0) -> Tuple[Optional[str], Optional[str]]:
    """Return (content_type, html_text) or (None, None) on failure."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; Gartner-DFIR-Research/1.0; +https://example.invalid)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            ctype = resp.headers.get("Content-Type")
            raw = resp.read()
            # Best effort decode
            try:
                text = raw.decode("utf-8", errors="replace")
            except Exception:
                text = raw.decode(errors="replace")
            return ctype, text
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        return None, None


def _html_to_text(html: str) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(html)
    text = unescape(parser.get_text())
    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split_sentences(text: str) -> List[str]:
    # Simple sentence splitting that works reasonably for marketing pages.
    parts = re.split(r"(?<=[.!?])\s+", text)
    out: List[str] = []
    for p in parts:
        s = p.strip()
        if 20 <= len(s) <= 420:
            out.append(s)
    return out


def _candidate_snippets(text: str) -> List[str]:
    """Return candidate snippets for matching.

    Many vendor pages (especially modern marketing sites) have little punctuation.
    This function therefore prefers newline-delimited blocks and short paragraph windows.
    """
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]

    snippets: List[str] = []

    # Single lines
    for ln in lines:
        if 10 <= len(ln) <= 260:
            snippets.append(ln)

    # Two-line windows (common for headings + description)
    for a, b in zip(lines, lines[1:]):
        combo = f"{a} {b}".strip()
        if 20 <= len(combo) <= 320:
            snippets.append(combo)

    # Fall back to sentence splits for pages with punctuation.
    snippets.extend(_split_sentences(text))

    # Dedupe preserving order
    seen = set()
    out: List[str] = []
    for s in snippets:
        key = s.lower()[:240]
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out


@dataclass
class EvidenceHit:
    url: str
    excerpt: str
    matched_terms: List[str]


def _build_subpillar_terms(schema: Dict[str, Any]) -> Dict[str, List[str]]:
    tax = schema.get("dfir_capability_taxonomy_v4.0_enhanced", {})
    subs = tax.get("sub_pillars", {})

    stopwords = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "can",
        "case",
        "could",
        "for",
        "from",
        "has",
        "have",
        "how",
        "if",
        "in",
        "into",
        "is",
        "it",
        "its",
        "may",
        "of",
        "on",
        "or",
        "our",
        "post",
        "should",
        "the",
        "their",
        "they",
        "this",
        "that",
        "these",
        "those",
        "to",
        "up",
        "use",
        "used",
        "using",
        "via",
        "was",
        "were",
        "will",
        "with",
        "without",
        "your",
        "you",
        "we",
        "workflow",
        "workflows",
    }

    def normalize_term(t: str) -> str:
        t = t.strip().lower()
        t = re.sub(r"[^a-z0-9\-\s]", " ", t)
        t = re.sub(r"\s+", " ", t)
        return t

    def tokenize_keywords(t: str) -> List[str]:
        # For keyword tokenization, treat '-' as a delimiter (helps match 'chain-of-custody'
        # with page text that usually contains 'chain of custody').
        nt = normalize_term(t).replace("-", " ")
        toks = [w for w in nt.split() if len(w) >= 4 and w not in stopwords]
        # Keep unique order
        seen = set()
        out: List[str] = []
        for w in toks:
            if w not in seen:
                out.append(w)
                seen.add(w)
        return out

    terms_by_sub: Dict[str, List[str]] = {}
    for sid in SUBPILLAR_IDS:
        info = subs.get(sid, {})
        terms: List[str] = []

        name = info.get("name")
        if isinstance(name, str) and name.strip():
            terms.append(name)

        for key in ("what_to_verify_publicly", "ai_specific_evidence"):
            items = info.get(key)
            if isinstance(items, list):
                for it in items:
                    if isinstance(it, str) and it.strip():
                        terms.append(it)
                        # Also add keywords from longer guidance strings.
                        terms.extend(tokenize_keywords(it))

        # Add the id itself
        terms.append(sid)

        cleaned: List[str] = []
        seen = set()
        for t in terms:
            nt = normalize_term(t)
            if len(nt) < 4:
                continue
            # Keep short phrases; for longer strings we rely on extracted keywords.
            if len(nt.split()) > 5:
                continue
            if nt not in seen:
                cleaned.append(nt)
                seen.add(nt)

        # Add a few globally useful bigrams that tend to appear verbatim.
        bigrams: List[str] = []
        for phrase in cleaned:
            toks = phrase.split()
            if len(toks) == 1:
                continue
            if len(toks) == 2:
                bigrams.append(phrase)

        for b in bigrams:
            if b not in seen:
                cleaned.append(b)
                seen.add(b)

        terms_by_sub[sid] = cleaned

    return terms_by_sub


GENERIC_MATCH_TERMS = {
    # Too broad to justify a sub-pillar capability by itself.
    "ai",
    "agentic",
    "automated",
    "automation",
    "analysis",
    "investigation",
    "investigations",
    "detection",
    "response",
    "remediation",
    "security",
    "incident",
    "alerts",
    "alert",
    "platform",
    "dashboard",
    "dashboards",
    "report",
    "reports",
    "workflow",
    "workflows",
}


AI_SIGNAL_TERMS = [
    "ai agent",
    "ai agents",
    "agentic",
    "swarming",
    "llm",
    "large language model",
    "machine learning",
    "ml",
    "automated",
    "autonomous",
    "orchestration",
    "correlation",
    "timeline",
    "chain of custody",
    "evidence",
]


def _ai_signal_score(text_lower: str) -> float:
    hits = 0
    for term in AI_SIGNAL_TERMS:
        if term in text_lower:
            hits += 1
    # Heuristic mapping: 0..5
    if hits <= 1:
        return 1.5 if hits == 1 else 0.5
    if hits <= 3:
        return 2.5
    if hits <= 6:
        return 3.5
    if hits <= 9:
        return 4.25
    return 4.75


def _score_subpillar_from_hits(ai_score: float, hit_count: int) -> float:
    # Very conservative mapping.
    # - High AI signal alone does not justify high sub-pillar scores.
    # - We aim for a realistic spread across the spectrum.
    if hit_count <= 0:
        # No sub-pillar evidence found.
        return 0.75 if ai_score >= 2.5 else 0.25
    if hit_count == 1:
        return 1.75 if ai_score >= 2.5 else 1.25
    if hit_count <= 3:
        return 2.75 if ai_score >= 3.5 else 2.25
    if hit_count <= 6:
        return 3.75 if ai_score >= 3.5 else 3.25
    return 4.5


def _vendor_flag(*, urls: List[str], ok_pages: int, excerpts_total: int) -> Tuple[str, float]:
    """Return (flag, confidence_0_to_1)."""
    if not urls:
        return "no_urls", 0.0
    if ok_pages == 0:
        return "fetch_failed", 0.0

    # 20 sub-pillars; typical run collects up to 2 excerpts per sub-pillar.
    coverage = max(0.0, min(1.0, excerpts_total / 20.0))
    if excerpts_total == 0:
        return "no_evidence", 0.1
    if coverage < 0.3:
        return "low_evidence", 0.35
    if coverage < 0.7:
        return "partial_evidence", 0.6
    return "good_evidence", 0.8


def _avg(values: Iterable[float]) -> float:
    xs = list(values)
    return sum(xs) / len(xs) if xs else 0.0


def _ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_path_for_url(url: str) -> Path:
    return CACHE_DIR / f"{_sha1(url)}.json"


def get_or_fetch_page(url: str, *, force: bool, timeout_seconds: float) -> Dict[str, Any]:
    """Returns cached record: {url, fetched_at, ok, content_type, text, error}."""
    _ensure_cache_dir()
    cache_path = _cache_path_for_url(url)
    if cache_path.exists() and not force:
        return json.loads(cache_path.read_text(encoding="utf-8"))

    ctype, html = _fetch_url(url, timeout_seconds=timeout_seconds)
    if html is None:
        record = {
            "url": url,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "ok": False,
            "content_type": ctype,
            "text": "",
            "error": "fetch_failed",
        }
        cache_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return record

    text = _html_to_text(html)
    record = {
        "url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "ok": True,
        "content_type": ctype,
        "text": text[:200_000],
        "error": None,
    }
    cache_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


def extract_vendor_urls(vendor: Dict[str, Any], max_urls: int) -> List[str]:
    text = vendor.get("capability_analysis") or ""
    urls = URL_RE.findall(text)
    # Dedupe while preserving order
    seen = set()
    out: List[str] = []
    for u in urls:
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
        if len(out) >= max_urls:
            break
    return out


def evidence_for_vendor(
    vendor: Dict[str, Any],
    *,
    urls: List[str],
    terms_by_subpillar: Dict[str, List[str]],
    force_fetch: bool,
    timeout_seconds: float,
    max_excerpts_per_subpillar: int,
    sleep_seconds: float,
) -> Tuple[Dict[str, Any], Dict[str, float]]:
    # Fetch pages
    page_records: List[Dict[str, Any]] = []
    for u in urls:
        rec = get_or_fetch_page(u, force=force_fetch, timeout_seconds=timeout_seconds)
        page_records.append(rec)
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    # Build concatenated searchable text per page
    pages_text: List[Tuple[str, str]] = []
    for rec in page_records:
        if rec.get("ok") is True and isinstance(rec.get("text"), str):
            pages_text.append((rec["url"], rec["text"]))

    ok_pages = len(pages_text)

    # Evidence extraction
    sub_evidence: Dict[str, Any] = {}
    sub_scores: Dict[str, float] = {}

    for sid in SUBPILLAR_IDS:
        terms = terms_by_subpillar.get(sid, [])
        hits: List[EvidenceHit] = []

        for url, text in pages_text:
            text_lower = text.lower()
            ai_score = _ai_signal_score(text_lower)

            # Collect candidate excerpts
            candidates = _candidate_snippets(text)
            for sent in candidates:
                s_lower = sent.lower()
                matched = [t for t in terms if t in s_lower]
                if not matched:
                    continue
                # Keep excerpt only if there is at least one AI signal on the page
                if ai_score < 1.5:
                    continue
                hits.append(EvidenceHit(url=url, excerpt=sent.strip(), matched_terms=matched[:10]))

        # De-dup excerpts and keep the top N (prefer more term matches)
        uniq: Dict[str, EvidenceHit] = {}
        for h in hits:
            key = (h.url + "::" + h.excerpt)[:600]
            if key not in uniq:
                uniq[key] = h

        def specific_count(h: EvidenceHit) -> int:
            return sum(1 for t in h.matched_terms if t not in GENERIC_MATCH_TERMS)

        # Prefer excerpts that match more *specific* terms (not generic words like "automated").
        sorted_hits = sorted(
            uniq.values(),
            key=lambda h: (specific_count(h), len(h.matched_terms), len(h.excerpt)),
            reverse=True,
        )
        selected = sorted_hits[:max_excerpts_per_subpillar]

        # Heuristic score suggestion
        ai_score_overall = 0.0
        if pages_text:
            ai_score_overall = max(_ai_signal_score(t.lower()) for _, t in pages_text)

        specific_hits_total = sum(specific_count(h) for h in selected)
        suggested = _score_subpillar_from_hits(ai_score_overall, specific_hits_total)

        sub_scores[sid] = round(suggested * 4) / 4  # quarter-step
        sub_evidence[sid] = {
            "source_urls": urls,
            "excerpts": [
                {
                    "url": h.url,
                    "excerpt": h.excerpt,
                    "matched_terms": h.matched_terms,
                    "specific_term_count": specific_count(h),
                }
                for h in selected
            ],
            "ai_signal_score": ai_score_overall,
            "hit_count": len(selected),
            "specific_hit_count": specific_hits_total,
            "notes": "Heuristic evidence extraction; analyst review recommended.",
        }

    # Add vendor-level summary evidence flagging.
    excerpts_total = 0
    for sid in SUBPILLAR_IDS:
        excerpts_total += len((sub_evidence.get(sid) or {}).get("excerpts") or [])

    flag, confidence = _vendor_flag(urls=urls, ok_pages=ok_pages, excerpts_total=excerpts_total)
    sub_evidence["_vendor_summary"] = {
        "ok_pages": ok_pages,
        "excerpts_total": excerpts_total,
        "flag": flag,
        "confidence": confidence,
    }

    return sub_evidence, sub_scores


def compute_pillar_scores(sub_scores: Dict[str, float]) -> Dict[str, float]:
    by_pillar: Dict[str, List[float]] = {p: [] for p in PILLARS}
    for sid, val in sub_scores.items():
        pillar = sid.split("-")[0]
        if pillar in by_pillar:
            by_pillar[pillar].append(float(val))

    return {p: round(_avg(vals) * 4) / 4 for p, vals in by_pillar.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Evidence-based (heuristic) research pass for vendor scoring.")
    parser.add_argument("--vendor-file", type=Path, default=DEFAULT_VENDOR_FILE)
    parser.add_argument("--schema-file", type=Path, default=DEFAULT_SCHEMA_FILE)
    parser.add_argument("--output-file", type=Path, default=DEFAULT_OUTPUT_FILE)
    parser.add_argument("--max-vendors", type=int, default=0, help="0 = all vendors")
    parser.add_argument("--max-urls-per-vendor", type=int, default=2)
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    parser.add_argument("--sleep-seconds", type=float, default=0.25)
    parser.add_argument("--force-fetch", action="store_true")
    parser.add_argument("--max-excerpts-per-subpillar", type=int, default=2)
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=10,
        help="Write partial output every N vendors (0 disables).",
    )

    args = parser.parse_args()

    vendors = _safe_json_load(args.vendor_file)
    schema = _safe_json_load(args.schema_file)
    terms_by_sub = _build_subpillar_terms(schema)

    if not isinstance(vendors, list):
        raise SystemExit("vendor file must be a JSON array")

    limit = args.max_vendors if args.max_vendors and args.max_vendors > 0 else len(vendors)
    out: List[Dict[str, Any]] = []

    started = datetime.now(timezone.utc)

    for idx, vendor in enumerate(vendors[:limit], start=1):
        name = vendor.get("vendor")
        urls = extract_vendor_urls(vendor, max_urls=max(1, args.max_urls_per_vendor))

        sub_evidence, sub_scores = evidence_for_vendor(
            vendor,
            urls=urls,
            terms_by_subpillar=terms_by_sub,
            force_fetch=args.force_fetch,
            timeout_seconds=args.timeout_seconds,
            max_excerpts_per_subpillar=args.max_excerpts_per_subpillar,
            sleep_seconds=args.sleep_seconds,
        )

        researched_pillars = compute_pillar_scores(sub_scores)

        # Create compact, human-readable rationales derived from the selected excerpts.
        rationale: Dict[str, str] = {}
        for sid in SUBPILLAR_IDS:
            info = (sub_evidence.get(sid) or {})
            excerpts = info.get("excerpts") or []
            if not isinstance(excerpts, list) or not excerpts:
                rationale[sid] = "No supporting excerpt found in fetched public pages."
                continue
            top = excerpts[0]
            url = top.get("url")
            excerpt = top.get("excerpt")
            if isinstance(excerpt, str):
                excerpt = re.sub(r"\s+", " ", excerpt).strip()
                excerpt = excerpt[:260]
            rationale[sid] = f"Evidence: {excerpt} (source: {url})"

        vendor_summary = (sub_evidence.get("_vendor_summary") or {})
        if isinstance(vendor_summary, dict):
            research_flag = vendor_summary.get("flag")
            research_confidence = vendor_summary.get("confidence")
        else:
            research_flag = "unknown"
            research_confidence = 0.0

        # Criticality rule: if we don't have good vendor-level evidence coverage,
        # don't allow any sub-pillar to score above 3.0.
        cap_applied = False
        if research_flag != "good_evidence":
            for sid, val in list(sub_scores.items()):
                if float(val) > 3.0:
                    sub_scores[sid] = 3.0
                    cap_applied = True
                    if sid in sub_evidence and isinstance(sub_evidence.get(sid), dict):
                        sub_evidence[sid]["score_cap_applied"] = {
                            "cap": 3.0,
                            "reason": "research_flag_not_good_evidence",
                        }

        # Validation check: enforce invariant.
        if research_flag != "good_evidence":
            over = [sid for sid, val in sub_scores.items() if float(val) > 3.0]
            if over:
                raise SystemExit(
                    f"Validation failed: research_flag={research_flag} but scores > 3.0 for {over}"
                )

        # Recompute pillars if we modified any sub-pillar scores.
        if cap_applied:
            researched_pillars = compute_pillar_scores(sub_scores)

        v2 = dict(vendor)
        v2["sub_pillar_evidence"] = sub_evidence
        v2["sub_pillar_scores_researched"] = sub_scores
        v2["pillar_scores_researched"] = researched_pillars
        v2["sub_pillar_rationale_researched"] = rationale
        v2["research_flag"] = research_flag
        v2["research_confidence"] = research_confidence
        v2["research"] = {
            "status": "heuristic_collected",
            "source": "public_web_text",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "urls_used": urls,
            "pages_cached": len(urls),
            "schema": args.schema_file.name,
            "tool": "research_validate_vendors.py",
            "validation_rules": {
                "cap_non_good_evidence_subpillars_at": 3.0,
            },
            "cap_applied": bool(cap_applied),
        }

        out.append(v2)
        print(f"[{idx}/{limit}] {name}: fetched {len(urls)} urls")

        if args.checkpoint_every and args.checkpoint_every > 0 and (idx % args.checkpoint_every == 0):
            args.output_file.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Checkpoint: wrote {args.output_file} ({len(out)} vendors)")

    args.output_file.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    ended = datetime.now(timezone.utc)
    print(f"Wrote {args.output_file} ({len(out)} vendors). Elapsed: {ended - started}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
