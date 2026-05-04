#!/usr/bin/env python3
"""
_research_proficio.py - Deep research pipeline for a single vendor (Proficio)
=============================================================================
Runs the full research flow:
  1. Fetch Proficio web pages and extract evidence excerpts
  2. Run v2.1 evidence-validated capability scoring (32 sub-pillars)
  3. Run v2 pricing dimension research (6 pricing dimensions)
  4. Merge results into the existing output files

Reuses logic from extract_mdr_excerpts.py, build_mdr_v2_1.py, build_mdr_pricing_v2.py
"""

import hashlib
import json
import math
import random
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent
SCHEMA_FILE = ROOT / "MDR_Services_Schema.json"
CAP_FILE = ROOT / "MDR Services Vendor 2-1 Consolidated.json"
PRICE_FILE = ROOT / "MDR Services Vendor Pricing 2-0 Researched.json"
CACHE_DIR_CAP = ROOT / "research" / "cache" / "pages_mdr"
CACHE_DIR_PRC = ROOT / "research" / "cache" / "pages_mdr_pricing"

VENDOR_NAME = "Proficio"

PILLARS = ["TDR", "PTI", "ADA", "DIS", "IRA", "AIO", "AID", "SOG"]
SUB_PILLAR_IDS = [f"{p}-{i:02d}" for p in PILLARS for i in range(1, 5)]
PRICING_DIMS = ["PRC-SUB", "PRC-USG", "PRC-FIX", "PRC-SUC", "PRC-COM", "PRC-OUT"]

MAX_EXCERPTS_PER_SP = 5
MAX_EXCERPTS_PER_DIM = 6
FETCH_SLEEP = 1.5

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
]

# Calibration
ORIGINAL_WEIGHT = 0.75
EVIDENCE_WEIGHT = 0.25
MAX_ADJUSTMENT = 0.8

# ==========================================================================
# Pillar-specific search terms
# ==========================================================================
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

MDR_GENERIC_TERMS = [
    "managed detection", "mdr", "managed security", "mssp",
    "security monitoring", "threat management", "cyber defense",
    "security service", "managed service", "soc as a service",
]

PRICING_TERMS = {
    "PRC-SUB": [
        "subscription", "recurring", "annual", "monthly", "per-seat", "per-endpoint",
        "per-device", "per-user", "license", "tier", "plan", "bundle", "package",
        "platform fee", "access fee", "managed service", "base price", "pricing tier",
        "subscription pricing", "recurring cost", "service tier", "standard plan",
        "premium plan", "enterprise plan", "pro plan", "pricing page", "cost",
        "analyst time", "human analyst", "ai tool", "software component",
        "included", "excluded", "breakdown", "transparent", "predictable",
    ],
    "PRC-USG": [
        "usage-based", "consumption", "pay-per-use", "pay-as-you-go", "metered",
        "api call", "data volume", "gb", "tb", "events per second", "eps",
        "compute hour", "inference", "overage", "burst", "threshold",
        "usage dashboard", "real-time usage", "usage monitoring", "usage tracking",
        "variable cost", "variable pricing", "elastic pricing",
    ],
    "PRC-FIX": [
        "one-time", "implementation", "setup fee", "deployment", "integration",
        "professional service", "consulting", "customization", "onboarding",
        "fixed fee", "project fee", "scope", "milestone", "deliverable",
        "change request", "statement of work", "sow",
    ],
    "PRC-SUC": [
        "success fee", "performance fee", "outcome fee", "bonus", "penalty",
        "sla credit", "sla penalty", "mttd", "mttr", "resolution rate",
        "per-resolution", "per-incident", "per-unit", "at-risk", "fee-at-risk",
        "performance-linked", "incentive", "kpi", "metric",
    ],
    "PRC-COM": [
        "composable", "modular", "a la carte", "mix and match", "flexible",
        "customizable", "configurable", "scalable", "predictable spending",
        "budget predictability", "risk-sharing", "reward", "penalty",
        "demystification", "transparency", "clear expectations",
    ],
    "PRC-OUT": [
        "outcome-based", "outcome-linked", "value-based", "roi", "return on investment",
        "risk reduction", "breach prevention", "cost avoidance", "cost saving",
        "value realization", "business value", "security outcome",
        "pricing-to-outcome", "outcome alignment", "measured result",
    ],
}

PRICING_GENERIC = [
    "pricing", "price", "cost", "fee", "rate", "charge",
    "commercial", "contract", "agreement", "engagement",
]

PILLAR_KEYWORDS_V21 = {
    "TDR": [
        "detection", "response", "correlat", "xdr", "edr", "ndr", "siem",
        "alert", "triage", "threat hunt", "proactive", "telemetry",
        "behavioral", "anomaly", "real-time", "automated containment",
    ],
    "PTI": [
        "threat intellig", "ioc", "indicator", "dark web", "darknet",
        "ttp", "campaign", "attribution", "geopolit", "adversar",
    ],
    "ADA": [
        "deception", "honeypot", "honeytoken", "decoy", "amtd",
        "moving target", "attack surface", "easm", "exposure",
    ],
    "DIS": [
        "deepfake", "synthetic media", "brand protect", "impersonat",
        "executive protect", "social engineer", "influence oper",
    ],
    "IRA": [
        "incident response", "forensic", "containment", "remediat",
        "recovery", "eradicat", "root cause", "breach response",
    ],
    "AIO": [
        "ai-powered", "ai-driven", "machine learn", "ml-based",
        "generative ai", "llm", "copilot", "automated",
        "ai triage", "neural", "adaptive",
    ],
    "AID": [
        "ai governance", "ai security", "adversarial", "model",
        "prompt injection", "ai supply chain", "ai framework",
    ],
    "SOG": [
        "soc 2", "iso 27001", "compliance", "sla", "24/7",
        "reporting", "governance", "mean time", "onboard",
    ],
}

# =========================================================================
# Utility functions (from extract_mdr_excerpts.py)
# =========================================================================

def html_to_text(html: str) -> str:
    text = re.sub(r'<(script|style|noscript|svg)[^>]*>.*?</\1>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<!--.*?-->', ' ', text, flags=re.DOTALL)
    text = re.sub(r'<head[^>]*>.*?</head>', ' ', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<(?:br|p|div|h[1-6]|li|tr|td|th|section|article|header|footer|nav|main)[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = unescape(text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n[ \t]*', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()

def fetch_url(url: str, *, max_retries: int = 2) -> Tuple[Optional[str], Optional[str]]:
    for attempt in range(max_retries):
        timeout = 10.0 + attempt * 5.0
        ua = random.choice(USER_AGENTS)
        req = urllib.request.Request(url, headers={
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "identity",
            "Connection": "keep-alive",
        }, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                ctype = resp.headers.get("Content-Type", "")
                raw = resp.read()
                text = raw.decode("utf-8", errors="replace")
                return ctype, text
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt + random.uniform(0.5, 2.0))
    return None, None

def get_or_fetch_page(url: str, cache_dir: Path, *, force: bool = False) -> Dict[str, Any]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{_sha1(url)}.json"
    if cache_path.exists() and not force:
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            if cached.get("ok"):
                return cached
        except Exception:
            pass
    ctype, html = fetch_url(url)
    if html is None:
        record = {"url": url, "fetched_at": datetime.now(timezone.utc).isoformat(), "ok": False, "text": "", "error": "fetch_failed"}
    else:
        text = html_to_text(html)
        record = {"url": url, "fetched_at": datetime.now(timezone.utc).isoformat(), "ok": True, "text": text[:200_000], "error": None}
    cache_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record

def split_sentences(text: str) -> List[str]:
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
    t = term.lower()
    if t in text_lower:
        return True
    t_clean = re.sub(r'[^a-z0-9 ]', '', t)
    if t_clean and t_clean in text_lower:
        return True
    return False

def find_matching_terms(text_lower: str, terms: List[str]) -> List[str]:
    return [t for t in terms if term_in_text(t, text_lower)]

# =========================================================================
# Schema loaders
# =========================================================================

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
        criteria_terms = set()
        for c in criteria:
            words = re.findall(r'\b[a-z][a-z ]{3,}\b', c.lower())
            for w in words:
                w = w.strip()
                if len(w) >= 5 and w not in {"within", "across", "through", "including", "based"}:
                    criteria_terms.add(w)
        result[sp_id] = {
            "name": info.get("name", sp_id),
            "criteria": criteria,
            "criteria_terms": list(criteria_terms),
            "search_terms": PILLAR_TERMS.get(sp_id.split("-")[0], []),
        }
    return result

def load_schema_pricing() -> Tuple[Dict, Dict, Dict]:
    """Load pricing dimensions from MDR schema."""
    with open(SCHEMA_FILE, "r", encoding="utf-8-sig") as f:
        raw = json.load(f)
    body = raw.get("mdr_services_taxonomy_v1.0", raw)
    pe = body.get("pricing_evaluation", {})
    dims_raw = pe.get("dimensions", {})
    dim_criteria = {}
    for dim_id, dinfo in dims_raw.items():
        criteria = dinfo.get("what_to_evaluate", [])
        criteria_terms = set()
        for c in criteria:
            for w in re.findall(r'\b[a-z][a-z ]{3,}\b', c.lower()):
                w = w.strip()
                if len(w) >= 5 and w not in {"within", "across", "through", "including", "based"}:
                    criteria_terms.add(w)
        dim_criteria[dim_id] = {
            "name": dinfo.get("name", dim_id),
            "definition": dinfo.get("definition", ""),
            "criteria": criteria,
            "criteria_terms": list(criteria_terms),
        }
    om = pe.get("outcome_maturity_rating", {})
    outcome_criteria = om.get("what_to_evaluate", [])
    outcome_scale = om.get("scale", {})
    return dim_criteria, outcome_criteria, outcome_scale

# =========================================================================
# Proficio URLs to research
# =========================================================================
PROFICIO_URLS = [
    "https://www.proficio.com",
    "https://www.proficio.com/managed-detection-and-response/",
    "https://www.proficio.com/prosoc-platform/",
    "https://www.proficio.com/solutions/",
    "https://www.proficio.com/threat-detection/",
    "https://www.proficio.com/incident-response/",
    "https://www.proficio.com/compliance/",
    "https://www.proficio.com/about/",
    "https://www.proficio.com/pricing/",
    "https://www.proficio.com/resources/",
    "https://www.proficio.com/partners/",
    "https://www.proficio.com/prosoc-managed-siem/",
    "https://www.proficio.com/active-defense/",
    "https://www.proficio.com/vulnerability-management/",
    "https://www.proficio.com/security-awareness-training/",
]

# =========================================================================
# Step 1: Fetch web pages
# =========================================================================

def fetch_all_pages(urls: List[str], cache_dir: Path) -> List[Tuple[str, str]]:
    """Fetch all URLs and return list of (url, text) for successful pages."""
    pages = []
    for url in urls:
        print(f"    Fetching {url}...", end=" ", flush=True)
        rec = get_or_fetch_page(url, cache_dir, force=False)
        if rec.get("ok") and rec.get("text"):
            text_len = len(rec["text"])
            pages.append((url, rec["text"]))
            print(f"OK ({text_len:,} chars)")
        else:
            print(f"FAILED ({rec.get('error', '?')})")
        time.sleep(FETCH_SLEEP + random.uniform(0.3, 1.0))
    return pages

# =========================================================================
# Step 2: Extract capability excerpts (per sub-pillar)
# =========================================================================

def extract_capability_excerpts(pages: List[Tuple[str, str]], schema_criteria: Dict) -> Dict[str, List[Dict]]:
    """Extract excerpts for each sub-pillar from fetched pages."""
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
                generic_matches = find_matching_terms(s_lower, MDR_GENERIC_TERMS)
                all_matches = list(set(criteria_matches + pillar_matches + generic_matches))
                if not all_matches:
                    continue
                relevance = len(criteria_matches) * 3 + len(pillar_matches) * 2 + len(generic_matches)
                hits.append({
                    "url": url,
                    "excerpt": sent[:300],
                    "matched_terms": all_matches[:8],
                    "relevance_score": relevance,
                })
        hits.sort(key=lambda h: h["relevance_score"], reverse=True)
        selected = []
        for h in hits:
            if len(selected) >= MAX_EXCERPTS_PER_SP:
                break
            h_prefix = h["excerpt"][:80].lower()
            is_dup = any(h_prefix in s["excerpt"][:100].lower() or s["excerpt"][:80].lower() in h_prefix for s in selected)
            if not is_dup:
                selected.append(h)
        result[sp_id] = selected
    return result

# =========================================================================
# Step 3: v2.1 evidence-based capability scoring
# =========================================================================

def assess_criterion(criterion: str, excerpts: List[Dict], notes: str,
                     original_score: float, pillar: str, search_terms: List[str]) -> Dict:
    """Assess a single criterion against excerpts."""
    if not excerpts and not notes:
        return {"criterion": criterion, "status": "unmet", "confidence": "low", "evidence": ""}
    all_text = " ".join(e["excerpt"] for e in excerpts).lower() + " " + notes.lower()
    criterion_lower = criterion.lower()
    key_phrases = re.findall(r'\b[a-z][a-z ]{3,}\b', criterion_lower)
    key_phrases = [p.strip() for p in key_phrases if len(p.strip()) >= 5]
    matched = sum(1 for p in key_phrases if p in all_text)
    pillar_kw = PILLAR_KEYWORDS_V21.get(pillar, [])
    kw_matches = sum(1 for kw in pillar_kw if kw in all_text)
    ratio = (matched / max(len(key_phrases), 1))
    best_excerpt = ""
    if excerpts:
        best = max(excerpts, key=lambda e: sum(1 for p in key_phrases if p in e["excerpt"].lower()))
        best_excerpt = best["excerpt"][:200]
    if ratio >= 0.4 or (kw_matches >= 3 and matched >= 1):
        status = "met"
        confidence = "high" if ratio >= 0.6 else "medium"
    elif ratio >= 0.2 or kw_matches >= 2:
        status = "partial"
        confidence = "medium"
    else:
        status = "unmet"
        confidence = "low"
    return {"criterion": criterion, "status": status, "confidence": confidence, "evidence": best_excerpt, "overlap_ratio": round(ratio, 2)}

def compute_evidence_score(criteria_results: List[Dict], excerpts: List[Dict],
                           pillar: str, search_terms: List[str]) -> Tuple[float, Dict]:
    """Compute evidence-based score from criteria assessment."""
    n_met = sum(1 for c in criteria_results if c["status"] == "met")
    n_partial = sum(1 for c in criteria_results if c["status"] == "partial")
    n_total = max(len(criteria_results), 1)

    criteria_score = min((n_met * 1.0 + n_partial * 0.5) / n_total * 5, 5)

    excerpt_text = " ".join(e["excerpt"] for e in excerpts).lower()
    pillar_kw = PILLAR_KEYWORDS_V21.get(pillar, [])
    kw_hits = sum(1 for kw in pillar_kw if kw in excerpt_text)

    if kw_hits >= 6:
        excerpt_bonus = 1.0
    elif kw_hits >= 3:
        excerpt_bonus = 0.5
    else:
        excerpt_bonus = 0.0

    volume_bonus = min(len(excerpts) * 0.1, 0.5)
    evidence_score = min(criteria_score + excerpt_bonus + volume_bonus, 5.0)

    breakdown = {
        "criteria_score": round(criteria_score, 2),
        "n_criteria_met": n_met,
        "n_criteria_partial": n_partial,
        "n_criteria_total": n_total,
        "keyword_hits": kw_hits,
        "excerpt_bonus": excerpt_bonus,
        "volume_bonus": round(volume_bonus, 2),
        "final_evidence_score": round(evidence_score, 2),
    }
    return evidence_score, breakdown

def compute_adjustment(original: float, evidence: float,
                       criteria_results: List[Dict], excerpts: List[Dict]) -> Tuple[float, str, str]:
    """Compute score adjustment."""
    if not excerpts:
        return original, "no_change", "No excerpts available."
    raw = ORIGINAL_WEIGHT * original + EVIDENCE_WEIGHT * evidence
    delta = raw - original
    delta = max(min(delta, MAX_ADJUSTMENT), -MAX_ADJUSTMENT)
    adjusted = round(max(0.0, min(original + delta, 5.0)), 2)
    if adjusted > original:
        return adjusted, "increased", f"Evidence suggests stronger capability (evidence={evidence:.1f}, delta={delta:+.2f})."
    elif adjusted < original:
        return adjusted, "decreased", f"Evidence suggests weaker capability (evidence={evidence:.1f}, delta={delta:+.2f})."
    else:
        return adjusted, "validated", f"Evidence supports score (evidence={evidence:.1f}, delta={delta:+.2f})."

def compute_evidence_quality(adjusted: float, notes: str, source_urls: List[str],
                             excerpts: List[Dict], criteria_results: List[Dict]) -> Tuple[float, str]:
    """Compute evidence quality factor and grade."""
    factor = 0.0
    n_met = sum(1 for c in criteria_results if c["status"] == "met")
    n_partial = sum(1 for c in criteria_results if c["status"] == "partial")
    factor += min(n_met * 0.15 + n_partial * 0.05, 0.5)
    factor += min(len(excerpts) * 0.08, 0.3)
    if source_urls:
        factor += min(len(source_urls) * 0.05, 0.15)
    if notes:
        factor += 0.05
    factor = min(factor, 1.0)
    if factor >= 0.65:
        grade = "A"
    elif factor >= 0.45:
        grade = "B"
    elif factor >= 0.25:
        grade = "C"
    else:
        grade = "D"
    return round(factor, 3), grade

def build_rationale_text(sp_id, sp_name, orig, adj, ev_score, adj_type, adj_reason,
                         criteria_results, ev_breakdown, excerpts, confidence):
    parts = [f"{sp_id} {sp_name}: {orig:.1f} -> {adj:.1f} ({adj_type})"]
    parts.append(adj_reason)
    parts.append(f"Evidence score: {ev_score:.1f} (criteria={ev_breakdown['criteria_score']:.1f}, kw_hits={ev_breakdown['keyword_hits']}, excerpts={len(excerpts)})")
    for cr in criteria_results:
        parts.append(f"  [{cr['status'].upper()}] {cr['criterion'][:80]}")
    parts.append(f"Confidence: {confidence}")
    return "\n".join(parts)

def run_capability_scoring(vendor: Dict, schema_criteria: Dict, cap_excerpts: Dict) -> Dict:
    """Run v2.1 evidence scoring for all 32 sub-pillars. Returns enriched vendor dict."""
    original_pillar_scores = vendor.get("pillar_scores", {})
    scores_current = vendor.get("sub_pillar_scores_current", {})
    v21_scores = {}
    v21_rationales = {}
    v21_rationale_text = {}
    stats = {"increased": 0, "decreased": 0, "validated": 0, "no_change": 0, "total": 32}
    all_confidences = []

    for sp_id in SUB_PILLAR_IDS:
        sp_info = schema_criteria.get(sp_id, {"name": sp_id, "criteria": [], "search_terms": []})
        sp_name = sp_info["name"]
        criteria_list = sp_info.get("criteria", [])
        pillar_code = sp_id.split("-")[0]
        original_score = float(scores_current.get(sp_id, vendor.get("sub_pillar_scores_v2_1", {}).get(sp_id, 0)))
        excerpts = cap_excerpts.get(sp_id, [])
        notes = ""
        source_urls = list(set(e["url"] for e in excerpts))

        # Assess criteria
        criteria_results = []
        for criterion in criteria_list:
            result = assess_criterion(criterion, excerpts, notes, original_score,
                                      pillar_code, sp_info.get("search_terms", []))
            criteria_results.append(result)

        # Compute evidence score
        evidence_score, ev_breakdown = compute_evidence_score(
            criteria_results, excerpts, pillar_code, sp_info.get("search_terms", []))

        # Adjustment
        adjusted_score, adj_type, adj_reason = compute_adjustment(
            original_score, evidence_score, criteria_results, excerpts)

        stats[adj_type if adj_type != "no_change" else "no_change"] += 1

        # Evidence quality
        eq_factor, eq_grade = compute_evidence_quality(
            adjusted_score, notes, source_urls, excerpts, criteria_results)

        n_met = sum(1 for c in criteria_results if c["status"] == "met")
        n_partial = sum(1 for c in criteria_results if c["status"] == "partial")
        if eq_factor >= 0.65 and n_met + n_partial >= 3:
            confidence = "high"
        elif eq_factor >= 0.40 and n_met + n_partial >= 1:
            confidence = "medium"
        else:
            confidence = "low"
        all_confidences.append(confidence)

        v21_scores[sp_id] = adjusted_score
        v21_rationales[sp_id] = {
            "sub_pillar_id": sp_id,
            "sub_pillar_name": sp_name,
            "original_score": original_score,
            "evidence_score": round(evidence_score, 2),
            "adjusted_score": adjusted_score,
            "adjustment_type": adj_type,
            "adjustment_reason": adj_reason,
            "scoring_level": min(max(int(round(adjusted_score)), 0), 5),
            "criteria_assessment": criteria_results,
            "evidence_breakdown": ev_breakdown,
            "evidence_quality_factor": eq_factor,
            "evidence_quality_grade": eq_grade,
            "confidence": confidence,
            "excerpt_count": len(excerpts),
        }
        v21_rationale_text[sp_id] = build_rationale_text(
            sp_id, sp_name, original_score, adjusted_score,
            evidence_score, adj_type, adj_reason,
            criteria_results, ev_breakdown, excerpts, confidence)

        # Update evidence
        if sp_id not in vendor.get("sub_pillar_evidence", {}):
            vendor.setdefault("sub_pillar_evidence", {})[sp_id] = {}
        vendor["sub_pillar_evidence"][sp_id]["excerpts"] = excerpts
        vendor["sub_pillar_evidence"][sp_id]["source_urls"] = source_urls

    # Compute pillar scores v2.1
    pillar_v21 = {}
    for p in PILLARS:
        ids = [f"{p}-{i:02d}" for i in range(1, 5)]
        vals = [v21_scores[sp] for sp in ids if sp in v21_scores]
        pillar_v21[p] = round(sum(vals) / max(len(vals), 1), 2) if vals else 0

    # Overall confidence
    high_count = all_confidences.count("high")
    med_count = all_confidences.count("medium")
    if high_count >= 16:
        overall_conf = "high"
    elif high_count + med_count >= 16:
        overall_conf = "medium"
    else:
        overall_conf = "low"

    # Notable differentiation
    sorted_pillars = sorted(pillar_v21.items(), key=lambda x: x[1], reverse=True)
    strongest = [f"{p} ({s:.1f})" for p, s in sorted_pillars[:3]]
    weakest = [f"{p} ({s:.1f})" for p, s in sorted_pillars[-2:]]
    notable = f"Strongest: {', '.join(strongest)}. Growth areas: {', '.join(weakest)}."

    # Evidence quality summary
    total_excerpts = sum(len(cap_excerpts.get(sp, [])) for sp in SUB_PILLAR_IDS)
    eq_pct = round(sum(1 for c in all_confidences if c in ("high", "medium")) / 32 * 100)

    # Write to vendor
    vendor["sub_pillar_scores_v2_1"] = v21_scores
    vendor["sub_pillar_scores_v2_researched"] = v21_scores
    vendor["pillar_scores_v2_1"] = pillar_v21
    vendor["pillar_scores_v2_researched"] = pillar_v21
    vendor["pillar_scores"] = pillar_v21  # update main pillar scores too
    vendor["sub_pillar_rationale_v2_1"] = v21_rationales
    vendor["sub_pillar_rationale_v2_1_text"] = v21_rationale_text
    vendor["sub_pillar_rationale_v2_consolidated"] = v21_rationale_text
    vendor["research_confidence_v2_1"] = overall_conf
    vendor["research_confidence"] = overall_conf
    vendor["notable_differentiation_v2_1"] = notable
    vendor["v2_1_adjustment_summary"] = stats
    vendor["evidence_quality_summary"] = f"{eq_pct}% evidence coverage ({total_excerpts} excerpts across 32 sub-pillars)."
    vendor["research_status"] = "completed"

    return vendor

# =========================================================================
# Step 4: Pricing excerpt extraction
# =========================================================================

def extract_pricing_excerpts(pages: List[Tuple[str, str]], dim_criteria: Dict) -> Dict[str, List[Dict]]:
    result = {}
    for dim_id in PRICING_DIMS:
        dc = dim_criteria.get(dim_id, {})
        criteria_terms = dc.get("criteria_terms", [])
        dim_terms = PRICING_TERMS.get(dim_id, [])
        hits = []
        for url, text in pages:
            sentences = split_sentences(text)
            for sent in sentences:
                s_lower = sent.lower()
                c_matches = find_matching_terms(s_lower, criteria_terms)
                d_matches = find_matching_terms(s_lower, dim_terms)
                g_matches = find_matching_terms(s_lower, PRICING_GENERIC)
                all_matches = list(set(c_matches + d_matches + g_matches))
                if not all_matches:
                    continue
                relevance = len(c_matches) * 3 + len(d_matches) * 2 + len(g_matches)
                # Extra boost if "proficio" mentioned alongside pricing terms
                if "proficio" in s_lower and len(d_matches) >= 1:
                    relevance += 2
                # Boost for "contains_percentage" or numeric (pricing signals)
                if re.search(r'\$[\d,]+|\d+%|per[\s-](?:seat|endpoint|device|user|month|year)', s_lower):
                    relevance += 2
                    all_matches.append("contains_percentage")
                hits.append({
                    "url": url, "excerpt": sent[:300],
                    "matched_terms": all_matches[:8], "relevance_score": relevance,
                })
        hits.sort(key=lambda h: h["relevance_score"], reverse=True)
        selected = []
        for h in hits:
            if len(selected) >= MAX_EXCERPTS_PER_DIM:
                break
            h_prefix = h["excerpt"][:80].lower()
            is_dup = any(h_prefix in s["excerpt"][:100].lower() or s["excerpt"][:80].lower() in h_prefix for s in selected)
            if not is_dup:
                selected.append(h)
        result[dim_id] = selected
    return result

# =========================================================================
# Step 5: Pricing evidence scoring
# =========================================================================

def assess_pricing_criterion(criterion: str, excerpts: List[Dict], dim_terms: List[str]) -> Dict:
    if not excerpts:
        return {"criterion": criterion, "status": "unmet", "evidence": "", "overlap_ratio": 0.0}
    all_text = " ".join(e["excerpt"] for e in excerpts).lower()
    key_phrases = [p.strip() for p in re.findall(r'\b[a-z][a-z ]{3,}\b', criterion.lower()) if len(p.strip()) >= 5]
    matched = sum(1 for p in key_phrases if p in all_text)
    ratio = matched / max(len(key_phrases), 1)
    kw_hits = sum(1 for kw in dim_terms if kw.lower() in all_text)
    best_excerpt = max(excerpts, key=lambda e: sum(1 for p in key_phrases if p in e["excerpt"].lower()))["excerpt"][:200] if excerpts else ""
    if ratio >= 0.4 or (kw_hits >= 3 and matched >= 1):
        status = "met"
    elif ratio >= 0.2 or kw_hits >= 2:
        status = "partial"
    else:
        status = "unmet"
    return {"criterion": criterion, "status": status, "evidence": best_excerpt, "overlap_ratio": round(ratio, 2)}

def run_pricing_scoring(vendor: Dict, dim_criteria: Dict, pricing_excerpts: Dict) -> Dict:
    """Run pricing evidence scoring for all 6 dimensions."""
    dim_scores_original = vendor.get("pricing_dimension_scores", {})
    dim_scores_v2 = {}
    dim_rationale_v2 = {}
    dim_rationale_text = {}
    stats = {"increased": 0, "decreased": 0, "validated": 0, "no_change": 0}

    for dim_id in PRICING_DIMS:
        dc = dim_criteria.get(dim_id, {})
        criteria = dc.get("criteria", [])
        dim_name = dc.get("name", dim_id)
        dim_terms = PRICING_TERMS.get(dim_id, [])
        excerpts = pricing_excerpts.get(dim_id, [])
        original = float(dim_scores_original.get(dim_id, 1))

        # Assess criteria
        criteria_results = []
        for c in criteria:
            criteria_results.append(assess_pricing_criterion(c, excerpts, dim_terms))

        n_met = sum(1 for c in criteria_results if c["status"] == "met")
        n_partial = sum(1 for c in criteria_results if c["status"] == "partial")
        n_total = max(len(criteria_results), 1)
        criteria_score = min((n_met * 1.0 + n_partial * 0.5) / n_total * 5, 5)

        # Keyword bonus
        excerpt_text = " ".join(e["excerpt"] for e in excerpts).lower()
        kw_hits = sum(1 for kw in dim_terms if kw.lower() in excerpt_text)
        kw_bonus = 1.0 if kw_hits >= 6 else 0.5 if kw_hits >= 3 else 0.0
        vol_bonus = min(len(excerpts) * 0.1, 0.5)
        evidence_score = min(criteria_score + kw_bonus + vol_bonus, 5.0)

        # Adjustment
        if not excerpts:
            adjusted, adj_type = original, "no_change"
        else:
            raw = ORIGINAL_WEIGHT * original + EVIDENCE_WEIGHT * evidence_score
            delta = max(min(raw - original, MAX_ADJUSTMENT), -MAX_ADJUSTMENT)
            adjusted = round(max(0.0, min(original + delta, 5.0)), 2)
            if adjusted > original:
                adj_type = "increased"
            elif adjusted < original:
                adj_type = "decreased"
            else:
                adj_type = "validated"
        stats[adj_type if adj_type != "no_change" else "no_change"] += 1

        # Evidence quality
        eq_factor = min(n_met * 0.15 + n_partial * 0.05 + len(excerpts) * 0.08, 1.0)
        if eq_factor >= 0.65:
            eq_grade, confidence = "A", "high"
        elif eq_factor >= 0.45:
            eq_grade, confidence = "B", "medium"
        elif eq_factor >= 0.25:
            eq_grade, confidence = "C", "medium"
        else:
            eq_grade, confidence = "D", "low"

        dim_scores_v2[dim_id] = adjusted
        dim_rationale_v2[dim_id] = {
            "dimension_id": dim_id,
            "dimension_name": dim_name,
            "original_score": original,
            "evidence_score": round(evidence_score, 2),
            "adjusted_score": adjusted,
            "adjustment_type": adj_type,
            "adjustment_reason": f"Evidence {adj_type} (evidence={evidence_score:.1f}, delta={adjusted-original:+.2f}).",
            "scoring_level": min(max(int(round(adjusted)), 0), 5),
            "criteria_assessment": criteria_results,
            "evidence_breakdown": {
                "criteria_score": round(criteria_score, 2),
                "n_criteria_met": n_met, "n_criteria_partial": n_partial, "n_criteria_total": n_total,
                "keyword_hits": kw_hits, "excerpt_bonus": kw_bonus, "volume_bonus": round(vol_bonus, 2),
            },
            "evidence_quality_factor": eq_factor,
            "evidence_quality_grade": eq_grade,
            "confidence": confidence,
            "excerpt_count": len(excerpts),
        }
        dim_rationale_text[dim_id] = (
            f"{dim_id} {dim_name}: {original:.1f} -> {adjusted:.1f} ({adj_type}). "
            f"Evidence score={evidence_score:.1f}, criteria met={n_met}/{n_total}, "
            f"excerpts={len(excerpts)}, confidence={confidence}."
        )

        # Update evidence
        vendor.setdefault("pricing_evidence", {})[dim_id] = {
            "source_urls": list(set(e["url"] for e in excerpts)),
            "excerpts": excerpts,
            "notes": f"Deep research extracted {len(excerpts)} excerpts.",
        }

    # Overall pricing score
    overall = round(sum(dim_scores_v2.values()) / max(len(dim_scores_v2), 1), 2)

    # Outcome maturity
    prc_suc = dim_scores_v2.get("PRC-SUC", 1)
    prc_out = dim_scores_v2.get("PRC-OUT", 1)
    prc_com = dim_scores_v2.get("PRC-COM", 1)
    om_raw = (prc_suc * 0.3 + prc_out * 0.4 + prc_com * 0.3)
    om_rating = min(max(int(round(om_raw)), 0), 5)

    # Confidence
    total_excerpts_prc = sum(len(pricing_excerpts.get(d, [])) for d in PRICING_DIMS)
    if total_excerpts_prc >= 18:
        prc_conf = "high"
    elif total_excerpts_prc >= 6:
        prc_conf = "medium"
    else:
        prc_conf = "low"

    # Write
    vendor["pricing_dimension_scores_v2"] = dim_scores_v2
    vendor["pricing_overall_score_v2"] = overall
    vendor["pricing_dimension_rationale_v2"] = dim_rationale_v2
    vendor["pricing_dimension_rationale_v2_text"] = dim_rationale_text
    vendor["pricing_adjustment_summary"] = stats
    vendor["pricing_research_confidence"] = prc_conf
    vendor["outcome_maturity_rating_v2"] = om_rating
    vendor["outcome_maturity_rationale_v2"] = (
        f"Outcome maturity: {om_rating}/5 (PRC-SUC={prc_suc:.1f}, PRC-OUT={prc_out:.1f}, PRC-COM={prc_com:.1f}). "
        f"Based on deep research with {total_excerpts_prc} pricing excerpts."
    )
    vendor["outcome_signals_v2"] = {
        "pricing_changes_on_outcomes": prc_out >= 3,
        "metrics_verifiable": prc_suc >= 3,
        "ai_efficiency_shared": any("ai" in e["excerpt"].lower() and "efficien" in e["excerpt"].lower()
                                    for exs in pricing_excerpts.values() for e in exs),
        "contract_embedded": prc_suc >= 3 and prc_com >= 3,
        "track_record": prc_out >= 3 and prc_suc >= 2,
        "roi_aligned": prc_out >= 2.5,
    }
    vendor["research_status"] = "completed"

    return vendor

# =========================================================================
# Main
# =========================================================================

def main():
    print("=" * 70)
    print(f"Deep Research Pipeline: {VENDOR_NAME}")
    print("=" * 70)

    # Load schemas
    print("\n[1/6] Loading schemas...")
    cap_schema = load_schema_criteria()
    prc_schema, outcome_criteria, outcome_scale = load_schema_pricing()
    print(f"  Capability: {len(cap_schema)} sub-pillars")
    print(f"  Pricing: {len(prc_schema)} dimensions")

    # Fetch web pages
    print(f"\n[2/6] Fetching {VENDOR_NAME} web pages...")
    cap_pages = fetch_all_pages(PROFICIO_URLS, CACHE_DIR_CAP)
    prc_pages = fetch_all_pages(PROFICIO_URLS, CACHE_DIR_PRC)
    print(f"  Fetched {len(cap_pages)} pages for capability, {len(prc_pages)} for pricing")

    # Load capability vendor
    print(f"\n[3/6] Running capability excerpt extraction + v2.1 scoring...")
    with open(CAP_FILE, "r", encoding="utf-8-sig") as f:
        cap_data = json.load(f)
    cap_vendors = cap_data["vendors"]
    prof_cap = None
    prof_cap_idx = None
    for i, v in enumerate(cap_vendors):
        if v.get("vendor", "").lower() == VENDOR_NAME.lower():
            prof_cap = v
            prof_cap_idx = i
            break
    if not prof_cap:
        print(f"  ERROR: {VENDOR_NAME} not found in {CAP_FILE.name}")
        sys.exit(1)

    # Extract capability excerpts
    cap_excerpts = extract_capability_excerpts(cap_pages, cap_schema)
    total_cap_exc = sum(len(v) for v in cap_excerpts.values())
    non_empty = sum(1 for v in cap_excerpts.values() if v)
    print(f"  Extracted {total_cap_exc} capability excerpts across {non_empty}/32 sub-pillars")

    # Run v2.1 scoring
    prof_cap = run_capability_scoring(prof_cap, cap_schema, cap_excerpts)
    adj = prof_cap["v2_1_adjustment_summary"]
    print(f"  Scoring complete: +{adj['increased']} -{adj['decreased']} ={adj['validated']} ~{adj['no_change']}")
    print(f"  Confidence: {prof_cap['research_confidence_v2_1']}")
    print(f"  Pillar scores v2.1: {json.dumps(prof_cap['pillar_scores_v2_1'])}")

    # Update in capability file
    cap_vendors[prof_cap_idx] = prof_cap
    with open(CAP_FILE, "w", encoding="utf-8") as f:
        json.dump(cap_data, f, indent=2, ensure_ascii=False)
    print(f"  Written to {CAP_FILE.name} ({len(cap_vendors)} vendors)")

    # Load pricing vendor
    print(f"\n[4/6] Running pricing excerpt extraction + v2 scoring...")
    with open(PRICE_FILE, "r", encoding="utf-8-sig") as f:
        prc_data = json.load(f)
    prc_vendors = prc_data["vendors"]
    prof_prc = None
    prof_prc_idx = None
    for i, v in enumerate(prc_vendors):
        if v.get("vendor", "").lower() == VENDOR_NAME.lower():
            prof_prc = v
            prof_prc_idx = i
            break
    if not prof_prc:
        print(f"  ERROR: {VENDOR_NAME} not found in {PRICE_FILE.name}")
        sys.exit(1)

    # Extract pricing excerpts
    prc_excerpts = extract_pricing_excerpts(prc_pages, prc_schema)
    total_prc_exc = sum(len(v) for v in prc_excerpts.values())
    prc_non_empty = sum(1 for v in prc_excerpts.values() if v)
    print(f"  Extracted {total_prc_exc} pricing excerpts across {prc_non_empty}/6 dimensions")

    # Run pricing scoring
    prof_prc = run_pricing_scoring(prof_prc, prc_schema, prc_excerpts)
    padj = prof_prc["pricing_adjustment_summary"]
    print(f"  Scoring complete: +{padj['increased']} -{padj['decreased']} ={padj['validated']} ~{padj['no_change']}")
    print(f"  Confidence: {prof_prc['pricing_research_confidence']}")
    print(f"  Pricing scores v2: {json.dumps(prof_prc['pricing_dimension_scores_v2'])}")
    print(f"  Overall: {prof_prc['pricing_overall_score_v2']}")
    print(f"  Outcome maturity: {prof_prc['outcome_maturity_rating_v2']}")

    # Update in pricing file
    prc_vendors[prof_prc_idx] = prof_prc
    with open(PRICE_FILE, "w", encoding="utf-8") as f:
        json.dump(prc_data, f, indent=2, ensure_ascii=False)
    print(f"  Written to {PRICE_FILE.name} ({len(prc_vendors)} vendors)")

    # Summary
    print(f"\n[5/6] Summary")
    print(f"  {'='*60}")
    print(f"  Vendor: {VENDOR_NAME}")
    print(f"  Capability excerpts: {total_cap_exc} across 32 sub-pillars")
    print(f"  Pricing excerpts: {total_prc_exc} across 6 dimensions")
    print(f"  Capability confidence: {prof_cap['research_confidence_v2_1']}")
    print(f"  Pricing confidence: {prof_prc['pricing_research_confidence']}")
    print(f"  ")
    print(f"  Capability Pillar Scores (v2.1):")
    for p in PILLARS:
        orig = prof_cap.get("pillar_scores", {}).get(p, 0)  # already updated
        v21 = prof_cap["pillar_scores_v2_1"].get(p, 0)
        print(f"    {p}: {v21:.2f}")
    print(f"  ")
    print(f"  Pricing Dimension Scores (v2):")
    for d in PRICING_DIMS:
        orig = prof_prc.get("pricing_dimension_scores", {}).get(d, 0)
        v2 = prof_prc["pricing_dimension_scores_v2"].get(d, 0)
        delta = v2 - orig
        delta_str = f" ({delta:+.2f})" if delta != 0 else ""
        print(f"    {d}: {orig:.1f} -> {v2:.2f}{delta_str}")
    print(f"    Overall: {prof_prc['pricing_overall_score_v2']}")

    print(f"\n[6/6] Done! Files updated in place.")
    print(f"  {CAP_FILE.name}: {VENDOR_NAME} researched")
    print(f"  {PRICE_FILE.name}: {VENDOR_NAME} researched")


if __name__ == "__main__":
    main()
