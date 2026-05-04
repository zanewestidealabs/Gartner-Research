#!/usr/bin/env python3
"""
build_offsec_v2_2.py

Produce Offensive Security Vendor 2-2 Researched.json from v2.1, adding the
`sub_pillar_rationale_researched` field that the frontend requires.

The rationale format matches Vendor 5-0 Researched.json (the gold standard):
  "{SP_ID} - {Name}. Score: {N}/5. Evidence flag/confidence: {flag} / {conf}.
   Public-source signals include: \"{excerpt1}\". Also: \"{excerpt2}\".
   Sources observed: {urls}. {ceiling_explanation}. {improvement_guidance}."

Reads:
  - Offensive Security Vendor 2-1 Consolidated.json  (scores, evidence, excerpts)
  - Offensive_Security_Schema.json                   (sub-pillar names, scoring rubric)

Writes:
  - Offensive Security Vendor 2-2 Researched.json
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── Files ──────────────────────────────────────────────────────────────
INPUT_FILE = "Offensive Security Vendor 2-1 Consolidated.json"
SCHEMA_FILE = "Offensive_Security_Schema.json"
OUTPUT_FILE = "Offensive Security Vendor 2-2 Researched.json"

# ── Sub-pillar names from schema ───────────────────────────────────────
SP_NAMES: Dict[str, str] = {}


def load_schema() -> Dict[str, Any]:
    """Load schema and populate SP_NAMES."""
    with open(SCHEMA_FILE, encoding="utf-8") as f:
        schema = json.load(f)
    tax = schema.get("offensive_security_taxonomy_v1.0", schema)
    subs = tax.get("sub_pillars", {})
    for sp_id, sp_data in subs.items():
        SP_NAMES[sp_id] = sp_data.get("name", sp_id)
    return schema


# ── Scoring rubric labels ─────────────────────────────────────────────
SCORE_LABELS = {
    0: "No Evidence",
    1: "Minimal",
    2: "Generic Claims",
    3: "Demonstrated",
    4: "Advanced",
    5: "Market-Leading",
}


def score_label(score: float) -> str:
    """Return the rubric label for a given score."""
    rounded = round(score)
    if rounded in SCORE_LABELS:
        return SCORE_LABELS[rounded]
    # For fractional scores, pick the lower bracket
    lower = int(score)
    if lower in SCORE_LABELS:
        return SCORE_LABELS[lower]
    return "Unscored"


# ── Excerpt text shortening ───────────────────────────────────────────
def shorten(text: str, max_len: int = 260) -> str:
    """Shorten text to max_len chars, ending on a word boundary."""
    text = " ".join(text.split())  # Normalize whitespace
    if len(text) <= max_len:
        return text
    cut = text[:max_len].rsplit(" ", 1)[0]
    return cut.rstrip(".,;:!? ") if cut else text[:max_len]


# ── Ceiling explanation (offensive-security-specific) ──────────────────
def explain_ceiling(score: float) -> str:
    """Return a score-band explanation for why the score is at this level."""
    if score >= 4.5:
        return (
            "This is near the ceiling because the public-facing signals strongly "
            "and repeatedly describe concrete, offensive-security-specific implementation, "
            "not just marketing claims."
        )
    if score >= 4.0:
        return (
            "The score is high because there are multiple concrete public signals, "
            "but we do not consistently see deep, end-to-end implementation detail across sources."
        )
    if score >= 3.0:
        return (
            "The score reflects moderate evidence: the capability is plausibly present, "
            "but public proof is not consistently detailed or independently corroborated."
        )
    if score >= 2.0:
        return (
            "The score is low-to-moderate because evidence is thin, generic, or indirect; "
            "we do not see enough specificity to justify a higher rating."
        )
    if score >= 1.0:
        return (
            "The score is low because we see only weak or generic signals, "
            "with little offensive-security-specific detail."
        )
    return "The score is minimal because we did not find credible public evidence for this sub-pillar."


def what_to_improve() -> str:
    """Return generic guidance on what would raise the score."""
    return (
        "To justify a higher score, we would expect clearer proof such as named "
        "products/features, detailed technical documentation, measurable outcomes, "
        "customer case studies, analyst recognition, or integration artifacts "
        "that show operational depth."
    )


# ── Build one rationale string ────────────────────────────────────────
def build_rationale(
    vendor: Dict[str, Any],
    sp_id: str,
    score: float,
    evidence: Dict[str, Any],
    research_flag: str,
    research_confidence: float,
) -> str:
    """
    Build a rationale string matching the Vendor 5-0 gold-standard format.

    Format:
      {SP_ID} - {Name}. Score: {score}/5.
      Evidence flag/confidence: {flag} / {confidence}.
      Public-source signals include: "{excerpt1} (matched: term1, term2)".
      Also: "{excerpt2} (matched: ...)".
      Sources observed: {url1}, {url2}.
      {ceiling_explanation}
      {improvement_guidance}
    """
    name = SP_NAMES.get(sp_id, sp_id)
    score_str = f"{score:.1f}/5" if score is not None else "N/A"
    conf_str = str(research_confidence)

    ev = evidence.get(sp_id, {})

    # Extract excerpt text with matched terms
    excerpts_raw = ev.get("excerpts", [])
    excerpt_strings: List[str] = []
    for item in excerpts_raw:
        if isinstance(item, dict):
            txt = shorten(str(item.get("excerpt", "")), 260)
            matched = item.get("matched_terms", [])
            if matched:
                txt = f"{txt} (matched: {', '.join(str(t) for t in matched[:6])})"
            if txt.strip():
                excerpt_strings.append(txt)

    # Source URLs
    source_urls = ev.get("source_urls", [])

    # Build evidence line
    if excerpt_strings:
        evidence_line = f'Public-source signals include: "{excerpt_strings[0]}".'
        if len(excerpt_strings) > 1:
            evidence_line += f' Also: "{excerpt_strings[1]}".'
    else:
        evidence_line = (
            "No sub-pillar-specific public excerpt was captured for this capability "
            "in the current evidence set."
        )

    # Sources line
    sources_line = ""
    if source_urls:
        sources_line = f"Sources observed: {', '.join(source_urls[:4])}."

    # Guardrail for non-good evidence vendors
    guardrail = ""
    if research_flag != "good_evidence":
        guardrail = (
            "Because this vendor is not flagged as good_evidence, we apply a conservative "
            "guardrail: sub-pillar scores should not exceed 3.0 without stronger public proof."
        )

    ceiling = explain_ceiling(score if score is not None else 0.0)
    improve = what_to_improve()

    # Assemble
    parts = [
        f"{sp_id} - {name}. Score: {score_str}.",
        f"Evidence flag/confidence: {research_flag} / {conf_str}.",
        evidence_line,
    ]
    if sources_line:
        parts.append(sources_line)
    if guardrail:
        parts.append(guardrail)
    parts.append(ceiling)
    parts.append(improve)

    return " ".join(p.strip() for p in parts if p and str(p).strip())


# ── Determine research flag from evidence quality ──────────────────────
def compute_research_flag(vendor: Dict[str, Any]) -> tuple:
    """Compute research_flag and confidence from evidence quality."""
    spe = vendor.get("sub_pillar_evidence", {})
    total_excerpts = 0
    total_sources = 0
    sps_with_excerpts = 0
    total_sps = 0

    for sp_id, ev in spe.items():
        if not isinstance(ev, dict):
            continue
        total_sps += 1
        excerpts = ev.get("excerpts", [])
        sources = ev.get("source_urls", ev.get("sources", []))
        total_excerpts += len(excerpts)
        total_sources += len(sources) if isinstance(sources, list) else 0
        if excerpts:
            sps_with_excerpts += 1

    if total_sps == 0:
        return "no_evidence", 0.0

    coverage = sps_with_excerpts / total_sps
    if coverage >= 0.6 and total_excerpts >= 10:
        return "good_evidence", round(min(coverage, 0.95), 2)
    elif coverage >= 0.3:
        return "partial_evidence", round(coverage * 0.7, 2)
    else:
        return "weak_evidence", round(coverage * 0.5, 2)


# ── Main processing ──────────────────────────────────────────────────
def main():
    print(f"Loading schema: {SCHEMA_FILE}")
    load_schema()
    print(f"  {len(SP_NAMES)} sub-pillars loaded")

    print(f"Loading input: {INPUT_FILE}")
    with open(INPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    vendors = data.get("vendors", [])
    print(f"  {len(vendors)} vendors loaded")

    # Statistics
    total_rationales = 0
    vendors_with_flag = 0
    vendors_good = 0

    for v in vendors:
        vendor_name = v.get("vendor", "Unknown")
        sps = v.get("sub_pillar_scores_current", {})
        spe = v.get("sub_pillar_evidence", {})

        # Determine research flag
        if "research_flag" not in v:
            flag, conf = compute_research_flag(v)
            v["research_flag"] = flag
            v["research_confidence"] = conf
        else:
            flag = v["research_flag"]
            conf = v.get("research_confidence", 0.0)
            vendors_with_flag += 1

        if flag == "good_evidence":
            vendors_good += 1

        # Build rationale for every sub-pillar that has a score
        rationale_map: Dict[str, str] = {}
        for sp_id in sorted(SP_NAMES.keys()):
            score = sps.get(sp_id)
            if score is None:
                continue
            score = float(score)
            rationale_map[sp_id] = build_rationale(
                v, sp_id, score, spe, flag, conf
            )
            total_rationales += 1

        # Set the top-level field the frontend expects
        v["sub_pillar_rationale_researched"] = rationale_map

        # Ensure research metadata
        if "research" not in v:
            v["research"] = {}
        v["research"]["v2_2_rationale_generated"] = True
        v["research"]["v2_2_timestamp_utc"] = datetime.now(timezone.utc).isoformat()

    # Update metadata
    if "metadata" not in data:
        data["metadata"] = {}
    data["metadata"]["version"] = "2.2"
    data["metadata"]["build_tool"] = "build_offsec_v2_2.py"
    data["metadata"]["build_timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    data["metadata"]["rationale_count"] = total_rationales

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    file_size = Path(OUTPUT_FILE).stat().st_size
    print(f"\nOutput: {OUTPUT_FILE}")
    print(f"  Size: {file_size:,} bytes ({file_size/1024:.0f} KB)")
    print(f"  Vendors: {len(vendors)}")
    print(f"  Rationales generated: {total_rationales}")
    print(f"  Research flags: {vendors_good} good_evidence, {len(vendors)-vendors_good} other")


if __name__ == "__main__":
    main()
