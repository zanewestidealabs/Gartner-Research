import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent

PILLARS = ["PLA", "INV", "REM", "PMG", "LAW"]


def _safe_json_load(path: Path) -> Any:
    # Some files in this workspace may contain a UTF-8 BOM.
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except UnicodeDecodeError:
        return json.loads(path.read_text(encoding="utf-8"))


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _as_float(v: Any) -> Optional[float]:
    try:
        if v is None or v == "":
            return None
        return float(v)
    except Exception:
        return None


def _normalize_text(s: str) -> str:
    s = (s or "")
    # Common oddities from web-scraped excerpts.
    s = s.replace("\ufffd", " ")  # replacement char
    s = s.replace("\u00a0", " ")  # NBSP
    s = s.replace("\u2014", "-")  # em dash
    s = s.replace("\u2013", "-")  # en dash
    s = s.replace("\u2212", "-")  # minus sign
    s = " ".join(s.split())
    return s


def _shorten(s: str, max_len: int = 220) -> str:
    s = _normalize_text(s)
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"


def _ordered_subpillar_ids(schema: Dict[str, Any]) -> List[str]:
    tax = schema.get("dfir_capability_taxonomy_v4.0_enhanced", {})
    subs = tax.get("sub_pillars", {})
    if isinstance(subs, dict) and subs:
        ids = []
        for p in PILLARS:
            for i in range(1, 5):
                sid = f"{p}-{i:02d}"
                if sid in subs:
                    ids.append(sid)
        # Fallback: include any extras deterministically
        extras = [k for k in subs.keys() if isinstance(k, str) and k not in set(ids)]
        ids.extend(sorted(extras))
        return ids

    # Final fallback: known 20
    return [f"{p}-{i:02d}" for p in PILLARS for i in range(1, 5)]


def _subpillar_name(schema: Dict[str, Any], sid: str) -> str:
    tax = schema.get("dfir_capability_taxonomy_v4.0_enhanced", {})
    subs = tax.get("sub_pillars", {})
    if isinstance(subs, dict):
        sp = subs.get(sid) or {}
        if isinstance(sp, dict) and sp.get("name"):
            return str(sp["name"])
    return sid


def _evidence_for(vendor: Dict[str, Any], sid: str) -> Tuple[List[str], List[str]]:
    ev_all = vendor.get("sub_pillar_evidence") or {}
    ev = ev_all.get(sid) if isinstance(ev_all, dict) else None
    if not isinstance(ev, dict):
        return [], []

    urls_out = [str(u) for u in (ev.get("source_urls") or []) if u]

    excerpts_out: List[str] = []
    for item in (ev.get("excerpts") or []):
        if isinstance(item, dict):
            excerpt = item.get("excerpt")
            matched = item.get("matched_terms")
            excerpt_txt = _shorten(str(excerpt or ""), 260)
            if matched and isinstance(matched, list):
                mt = [str(t) for t in matched if t]
                if mt:
                    excerpt_txt = f"{excerpt_txt} (matched: {', '.join(mt[:6])})"
            if excerpt_txt.strip():
                excerpts_out.append(excerpt_txt)
            # Prefer per-excerpt URL if present
            u = item.get("url")
            if u:
                urls_out.append(str(u))
        elif isinstance(item, str):
            txt = _shorten(item, 260)
            if txt.strip():
                excerpts_out.append(txt)

    # Dedupe URLs preserving order
    seen = set()
    dedup_urls: List[str] = []
    for u in urls_out:
        if u in seen:
            continue
        seen.add(u)
        dedup_urls.append(u)

    return dedup_urls[:3], excerpts_out[:3]


def _score_for(vendor: Dict[str, Any], sid: str) -> Optional[float]:
    for key in ("sub_pillar_scores_researched", "sub_pillar_scores_validated", "sub_pillar_scores_current"):
        d = vendor.get(key) or {}
        if isinstance(d, dict) and sid in d:
            v = _as_float(d.get(sid))
            if v is not None:
                return _clamp(v, 0.0, 5.0)
    return None


def _explain_ceiling(score: float) -> str:
    if score >= 4.5:
        return "This is near the ceiling because the public-facing signals strongly and repeatedly describe concrete, DFIR-specific implementation, not just marketing claims."
    if score >= 4.0:
        return "The score is high because there are multiple concrete public signals, but we do not consistently see deep, end-to-end implementation detail across sources."
    if score >= 3.0:
        return "The score reflects moderate evidence: the capability is plausibly present, but public proof is not consistently detailed or independently corroborated."
    if score >= 2.0:
        return "The score is low-to-moderate because evidence is thin, generic, or indirect; we do not see enough specificity to justify a higher rating."
    if score >= 1.0:
        return "The score is low because we see only weak or generic signals, with little DFIR-specific detail."
    return "The score is minimal because we did not find credible public evidence for this sub-pillar."


def _what_to_improve() -> str:
    return (
        "To justify a higher score, we would expect clearer DFIR proof such as named tooling/workflows, "
        "detailed case studies, repeatable methodology documentation, certifications, or artifacts that show operational depth."
    )


def build_rationale(schema: Dict[str, Any], vendor: Dict[str, Any], sid: str) -> str:
    name = (
        (vendor.get("sub_pillar_schema_labels") or {}).get(sid)
        or _subpillar_name(schema, sid)
        or sid
    )
    name = _normalize_text(str(name))

    score = _score_for(vendor, sid)
    score_str = f"{score:.1f}/5" if score is not None else "N/A"

    flag = str(vendor.get("research_flag") or "unknown")
    conf = _normalize_text(str(vendor.get("research_confidence") or "unknown"))

    urls, excerpts = _evidence_for(vendor, sid)

    evidence_line = ""
    if excerpts:
        evidence_line = f"Public-source signals include: \"{_normalize_text(excerpts[0])}\"."
        if len(excerpts) > 1:
            evidence_line += f" Also: \"{_normalize_text(excerpts[1])}\"."
    else:
        evidence_line = "No sub-pillar-specific public excerpt was captured for this capability in our current evidence set."

    sources_line = ""
    if urls:
        sources_line = f"Sources observed: {', '.join(urls)}."

    scoring_guardrail = ""
    if flag != "good_evidence":
        scoring_guardrail = (
            "Because this vendor is not flagged as good_evidence, we apply a conservative guardrail: "
            "sub-pillar scores should not exceed 3.0 without stronger public proof."
        )

    if score is None:
        ceiling = "A researched score was not available for this sub-pillar; treat this as a data completeness gap rather than an affirmative capability claim."
    else:
        ceiling = _explain_ceiling(score)

    parts = [
        f"{sid} - {name}. Score: {score_str}.",
        f"Evidence flag/confidence: {flag} / {conf}.",
        evidence_line,
    ]
    if sources_line:
        parts.append(sources_line)
    if scoring_guardrail:
        parts.append(scoring_guardrail)
    parts.append(ceiling)
    parts.append(_what_to_improve())

    return " ".join(p.strip() for p in parts if p and str(p).strip())


def main() -> int:
    ap = argparse.ArgumentParser(description="Expand researched per-sub-pillar rationales for all vendors.")
    ap.add_argument("--input", default=str(ROOT / "Vendor 4-1 Researched.json"), help="Input researched JSON")
    ap.add_argument("--schema", default=str(ROOT / "schema4-0_enhanced.json"), help="Schema JSON")
    ap.add_argument("--output", default=str(ROOT / "Vendor 5-0 Researched.json"), help="Output JSON")
    ap.add_argument("--min-len", type=int, default=180, help="Minimum rationale length")
    ap.add_argument(
        "--force-all",
        action="store_true",
        help="Regenerate all rationales (ignore existing text)",
    )
    args = ap.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    schema_path = Path(args.schema)

    vendors = _safe_json_load(in_path)
    schema = _safe_json_load(schema_path)

    if not isinstance(vendors, list):
        raise SystemExit("Input JSON must be a list of vendors")

    sub_ids = _ordered_subpillar_ids(schema)

    updated = 0
    filled = 0
    total = 0

    for v in vendors:
        if not isinstance(v, dict):
            continue
        r = v.get("sub_pillar_rationale_researched")
        if not isinstance(r, dict):
            r = {}
        for sid in sub_ids:
            total += 1
            new_text = build_rationale(schema, v, sid)
            old = r.get(sid)
            if args.force_all or not isinstance(old, str) or len(old.strip()) < args.min_len:
                r[sid] = new_text
                filled += 1
            else:
                # Keep existing if it already meets minimum length
                pass
        v["sub_pillar_rationale_researched"] = r

        v.setdefault("research", {})
        if isinstance(v["research"], dict):
            v["research"].setdefault("rationale", {})
            if isinstance(v["research"].get("rationale"), dict):
                v["research"]["rationale"].update(
                    {
                        "version": "5-0",
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "min_length": args.min_len,
                        "coverage_subpillars": sub_ids,
                    }
                )
        updated += 1

    # Validate coverage
    missing = []
    for v in vendors:
        r = v.get("sub_pillar_rationale_researched") or {}
        if not isinstance(r, dict):
            missing.append((v.get("vendor"), "<rationale-not-dict>"))
            continue
        for sid in sub_ids:
            s = r.get(sid)
            if not isinstance(s, str) or not s.strip():
                missing.append((v.get("vendor"), sid))

    if missing:
        sample = "; ".join(f"{vn}:{sid}" for vn, sid in missing[:12])
        raise SystemExit(f"Missing rationale entries after generation: {len(missing)} (sample: {sample})")

    out_path.write_text(json.dumps(vendors, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {out_path} ({len(vendors)} vendors)")
    print(f"Sub-pillars: {len(sub_ids)}")
    print(f"Updated vendors processed: {updated}")
    print(f"Rationales created/replaced: {filled}/{total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
