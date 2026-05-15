"""
_adapt_cnapp_mq_rationale.py
─────────────────────────────
Adapter step (Hybrid plan, Phase 1).

Reads:  CNAPP MQ Vendor 1-2 Researched.json
Writes: CNAPP MQ Vendor 1-3 Researched.json

For each vendor, projects the CNAPP-MQ-specific fields
(`mq_gap_rationales`, `evidence_ledger`, `mq_gap_sub_pillar_scores`,
`mq_gap_pillar_scores`) onto the standard schema keys the existing
Evidence & Rationale renderer in `static/app.js` already understands:

  - sub_pillar_rationale_v2          (rich per-sub-pillar object)
  - sub_pillar_evidence              (excerpts + source_urls per sid)
  - sub_pillar_scores_v2_researched  (flat sid -> score)
  - pillar_scores_v2_researched      (flat pillar -> score)

Original CNAPP MQ keys are preserved untouched so the dedicated
research script (Phase 3) can continue iterating on them.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from collections import defaultdict
from typing import Any

SRC = "CNAPP MQ Vendor 1-2 Researched.json"
DST = "CNAPP MQ Vendor 1-3 Researched.json"


def _grade_from_confidence(conf: str | None) -> str:
    c = (conf or "").lower()
    if c in ("high", "h"):
        return "A"
    if c in ("med", "medium", "m"):
        return "B"
    if c in ("low", "l"):
        return "C"
    return "D"


def _quality_factor(conf: str | None, excerpt_count: int) -> float:
    base = {"high": 0.9, "med": 0.7, "medium": 0.7, "low": 0.45}.get(
        (conf or "").lower(), 0.35
    )
    bump = min(0.1, 0.025 * max(0, excerpt_count - 1))
    return round(base + bump, 3)


def adapt_vendor(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)

    rationales: dict[str, dict[str, Any]] = v.get("mq_gap_rationales") or {}
    ledger: list[dict[str, Any]] = v.get("evidence_ledger") or []
    sp_scores: dict[str, float] = v.get("mq_gap_sub_pillar_scores") or {}
    p_scores: dict[str, float] = v.get("mq_gap_pillar_scores") or {}

    # ── 1. Group ledger by sub_pillar ────────────────────────────────
    ledger_by_sid: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in ledger:
        sid = entry.get("sub_pillar")
        if sid:
            ledger_by_sid[sid].append(entry)

    # ── 2. Build sub_pillar_evidence (excerpts + source_urls) ────────
    evidence_out: dict[str, dict[str, Any]] = {}
    for sid, entries in ledger_by_sid.items():
        excerpts = []
        urls = []
        for e in entries:
            fact = e.get("fact") or ""
            url = e.get("source_url") or ""
            if fact:
                excerpts.append(
                    {
                        "excerpt": fact,
                        "url": url,
                        "matched_terms": [e.get("source_type") or ""]
                        if e.get("source_type")
                        else [],
                    }
                )
            if url and url not in urls:
                urls.append(url)
        evidence_out[sid] = {
            "source_urls": urls,
            "excerpts": excerpts,
        }

    # ── 3. Build sub_pillar_rationale_v2 (rich per-sid object) ───────
    rationale_v2: dict[str, dict[str, Any]] = {}
    for pillar, sub_map in rationales.items():
        if not isinstance(sub_map, dict):
            continue
        for sid, info in sub_map.items():
            if not isinstance(info, dict):
                continue
            base_score = info.get("score")
            adj_score = sp_scores.get(sid, base_score)
            conf = info.get("confidence")
            led_for_sid = ledger_by_sid.get(sid, [])
            ex_count = len(led_for_sid)
            entry: dict[str, Any] = {
                "score_rationale": info.get("rationale") or "",
                "confidence": conf or "unknown",
                "evidence_quality_factor": _quality_factor(conf, ex_count),
                "evidence_quality_grade": _grade_from_confidence(conf),
                "excerpt_count": ex_count,
            }
            # Score adjustment: use any ledger delta as the original→final story
            if led_for_sid and base_score is not None and adj_score is not None:
                try:
                    if abs(float(base_score) - float(adj_score)) >= 0.05:
                        entry["score_adjustment"] = {
                            "original": float(base_score),
                            "adjusted": float(adj_score),
                            "reason": (led_for_sid[0].get("fact") or "")[:160],
                        }
                except (TypeError, ValueError):
                    pass
            # Key evidence (string list) for Evidence panel fallback
            ke = [e.get("fact") for e in led_for_sid if e.get("fact")]
            if ke:
                entry["key_evidence"] = ke
            # Pull through evidence_sources from the original rationale
            es = info.get("evidence_sources")
            if es:
                entry["evidence_sources"] = list(es) if isinstance(es, list) else [es]
            rationale_v2[sid] = entry

    # ── 4. Mirror flat sub-pillar / pillar scores into v2_researched ─
    sub_scores_v2 = {sid: float(s) for sid, s in sp_scores.items()}
    pillar_scores_v2 = {p: float(s) for p, s in p_scores.items()}

    # ── 5. Stamp onto vendor ─────────────────────────────────────────
    out["sub_pillar_rationale_v2"] = rationale_v2
    out["sub_pillar_evidence"] = evidence_out
    out["sub_pillar_scores_v2_researched"] = sub_scores_v2
    out["pillar_scores_v2_researched"] = pillar_scores_v2
    # Help the Evidence tab guardrail message
    out["research_flag"] = (
        "good_evidence" if sum(len(es["excerpts"]) for es in evidence_out.values()) >= 5
        else "thin_evidence"
    )
    return out


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(here, SRC)
    dst_path = os.path.join(here, DST)
    if not os.path.exists(src_path):
        print(f"[error] source not found: {src_path}", file=sys.stderr)
        return 2

    with open(src_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    vendors = data.get("vendors") or []
    new_vendors = [adapt_vendor(v) for v in vendors]

    out = dict(data)
    out["vendors"] = new_vendors
    out["adapter_pass"] = "1.3-rationale-projection"
    out["adapter_generated_at"] = _dt.datetime.utcnow().isoformat() + "Z"
    out["adapter_script"] = os.path.basename(__file__)
    out["adapter_notes"] = (
        "Projects mq_gap_rationales + evidence_ledger onto standard "
        "sub_pillar_rationale_v2 / sub_pillar_evidence / "
        "sub_pillar_scores_v2_researched / pillar_scores_v2_researched "
        "so the existing Evidence & Rationale renderer surfaces the data."
    )

    with open(dst_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    # Stats
    total_excerpts = sum(
        sum(len(es.get("excerpts") or []) for es in v["sub_pillar_evidence"].values())
        for v in new_vendors
    )
    total_rationales = sum(len(v["sub_pillar_rationale_v2"]) for v in new_vendors)
    print(
        f"[ok] wrote {dst_path}\n"
        f"     vendors={len(new_vendors)} "
        f"rationales={total_rationales} excerpts={total_excerpts}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
