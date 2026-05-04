"""
build_mdr_v2_researched.py  —  MDR Vendor 2-0 Researched
=========================================================

Reads the MDR capability seed file (1-0) and MDR schema, then generates
a 2-0 researched vendor file with deep sub-pillar rationales following the
same structure used in AI TRiSM 2-1 and Preemptive Cybersecurity 2-0.

For each vendor × sub-pillar:
  • score_rationale            – why the vendor received this score
  • evidence_quality_rationale – strength of the evidence base
  • scoring_level_justification – maps score → capability maturity level
  • criteria_assessment         – per-criterion met/partial/unmet
  • key_evidence                – up to 4 key evidence excerpts
  • confidence                  – high / medium / low
  • evidence_quality_factor     – 0.0–1.0

Vendor-level additions:
  • research_confidence
  • evidence_quality_summary
  • notable_differentiation
  • sub_pillar_rationale_v2_consolidated  – readable text per sub-pillar

Output: "MDR Services Vendor 2-0 Researched.json"
Pricing is excluded (to be addressed separately).
"""

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CAP_FILE = ROOT / "MDR Services Vendor Capability 1-0 Seed.json"
SCHEMA_FILE = ROOT / "MDR_Services_Schema.json"
OUTPUT_FILE = ROOT / "MDR Services Vendor 2-0 Researched.json"

PILLARS = ["TDR", "PTI", "ADA", "DIS", "IRA", "AIO", "AID", "SOG"]
SUB_PILLAR_IDS = [f"{p}-{i:02d}" for p in PILLARS for i in range(1, 5)]

# ── Scoring-level definitions (from schema) ──────────────────────────

SCORING_LEVELS = {
    0: {"label": "No Evidence", "desc": "No publicly verifiable evidence of capability in this sub-pillar."},
    1: {"label": "Minimal", "desc": "Basic or manual capability; no automation, analytics, or continuous operation."},
    2: {"label": "Generic Claims", "desc": "Marketing mentions the capability but lacks named products, technical docs, metrics, or specifics."},
    3: {"label": "Demonstrated", "desc": "Documented capability with named products or features, some technical detail, and identifiable use cases."},
    4: {"label": "Advanced", "desc": "Named products with measurable outcomes, integration points, customer validation, or analyst recognition. Automation and continuous operation present."},
    5: {"label": "Market-Leading", "desc": "Best-in-class capability with deep technical evidence, extensive customer base, analyst leadership recognition, measurable impact metrics, and continuous innovation."},
}


def load_schema_criteria():
    """Load sub-pillar criteria from the MDR schema."""
    with open(SCHEMA_FILE, "r", encoding="utf-8-sig") as f:
        raw = json.load(f)
    body = raw.get("mdr_services_taxonomy_v1.0", raw)
    sp_data = body.get("sub_pillars", {})

    result = {}
    for sp_id in sorted(sp_data.keys()):
        info = sp_data[sp_id]
        criteria = info.get("what_to_verify_publicly",
                            info.get("ai_evaluation_criteria", []))
        result[sp_id] = {
            "name": info.get("name", sp_id),
            "criteria": criteria,
        }
    return result


def load_pillar_names():
    """Load pillar code -> name mapping from schema."""
    with open(SCHEMA_FILE, "r", encoding="utf-8-sig") as f:
        raw = json.load(f)
    body = raw.get("mdr_services_taxonomy_v1.0", raw)
    pillars = body.get("pillars", {})
    result = {}
    for code, pdata in pillars.items():
        result[code] = pdata.get("name", code)
    return result


# ── Evidence-quality estimation ──────────────────────────────────────

def estimate_evidence_quality(score, notes, source_urls, criteria_count_met,
                               criteria_count_partial, criteria_total):
    """Produce evidence_quality_factor (0–1) and a letter grade."""
    factor = 0.0

    # Source diversity (0–0.25)
    n_urls = len(source_urls) if source_urls else 0
    factor += min(n_urls / 4.0, 1.0) * 0.25

    # Notes richness (0–0.25)
    note_len = len(notes) if notes else 0
    factor += min(note_len / 300.0, 1.0) * 0.25

    # Criteria coverage (0–0.25)
    if criteria_total > 0:
        cov = (criteria_count_met + 0.5 * criteria_count_partial) / criteria_total
        factor += cov * 0.25

    # Score alignment (0–0.25): higher scored vendors expected to have richer evidence
    factor += min(score / 5.0, 1.0) * 0.25

    factor = round(min(max(factor, 0.0), 1.0), 3)

    if factor >= 0.80:
        grade = "A (Strong)"
    elif factor >= 0.60:
        grade = "B (Good)"
    elif factor >= 0.40:
        grade = "C (Moderate)"
    elif factor >= 0.20:
        grade = "D (Weak)"
    else:
        grade = "F (Insufficient)"

    return factor, grade


# ── Criterion assessment engine ──────────────────────────────────────

# Keywords that strongly signal a sub-pillar criterion is addressed
CRITERION_KEYWORD_MAP = {
    # TDR
    "signal correlation": ["correlat", "xdr", "cross-domain", "multi-source", "telemetry fusion"],
    "alert triage": ["triage", "alert priorit", "severity", "alert grouping"],
    "threat hunting": ["threat hunt", "hunt", "hypothesis-driven", "proactive", "overwatch", "falcon overwat"],
    "response automation": ["soar", "automated response", "playbook", "orchestrat", "auto-remediat"],
    # PTI
    "threat intelligence": ["threat intel", "ioc", "indicator", "feed", "cti"],
    "ttp mapping": ["ttp", "att&ck", "mitre", "attack pattern"],
    "dark web": ["dark web", "darknet", "underground", "tor"],
    # ADA
    "deception": ["deception", "honeypot", "honeytoken", "decoy", "breadcrumb"],
    "amtd": ["amtd", "moving target", "runtime mutation", "micro-segment"],
    "attack surface": ["easm", "attack surface", "asset discovery", "shadow it", "exposure"],
    "counter-adversary": ["takedown", "adversary", "counter-adversary", "disruption"],
    # DIS
    "deepfake": ["deepfake", "synthetic media", "voice clone", "ai-generat"],
    "bec": ["bec", "business email compromise", "impersonat", "executive protect"],
    "social engineering": ["social engineer", "phishing", "narrative attack"],
    "brand protection": ["brand monitor", "brand protect", "typosquat", "domain squat"],
    # IRA
    "incident scoping": ["scoping", "severity assess", "triage", "evidence preserv"],
    "containment": ["isolat", "contain", "quarantine", "block"],
    "recovery": ["recover", "restor", "eradicat", "rebuild", "harden"],
    "post-incident": ["post-incident", "after-action", "root cause", "lesson", "aar", "pir"],
    # AIO
    "ai detection": ["ai-assist", "ml-driven", "ai detection", "ml model", "behavioral ai", "ai-powered detection"],
    "ai triage": ["ai triage", "ai-automat", "ai-generat", "ai investigation", "charlotte ai", "purple ai", "copilot"],
    "ai response": ["ai response", "ai-autonomous", "adaptive response", "ai-coordinated"],
    "ai transparency": ["explainab", "audit trail", "transparen", "human-readable"],
    # AID
    "domain ai": ["security llm", "domain-specific", "security ai", "custom model", "fine-tun"],
    "ai governance": ["model version", "model lifecycle", "drift detect", "model monitor"],
    "ai supply chain": ["ai supply chain", "model provenance", "prompt inject", "adversarial test"],
    "ai innovation": ["ai innovation", "ai-enabled", "ai pipeline", "ai roadmap"],
    # SOG
    "soc operations": ["soc", "24/7", "follow-the-sun", "noc"],
    "compliance": ["soc 2", "iso 27001", "compliance", "certif", "fedramp"],
    "customer portal": ["portal", "dashboard", "self-service", "reporting"],
    "sla": ["sla", "mean time", "mttr", "mttd", "response time"],
}


def assess_criterion(criterion_text, notes, score, vendor_desc="", vendor_name=""):
    """Assess whether a criterion is met, partial, or unmet based on evidence."""
    if score == 0:
        return {
            "criterion": criterion_text,
            "status": "unmet",
            "evidence": "No publicly verifiable evidence found for this capability.",
            "confidence": "high",
        }

    # Combine all textual evidence
    combined = f"{notes} {vendor_desc} {vendor_name}".lower()
    criterion_lower = criterion_text.lower()

    # Check for keyword matches
    match_count = 0
    matched_keywords = []
    for category, kws in CRITERION_KEYWORD_MAP.items():
        for kw in kws:
            if kw.lower() in criterion_lower or kw.lower() in combined:
                match_count += 1
                matched_keywords.append(kw)

    # Also check if any words from the criterion itself appear in evidence
    criterion_words = set(re.findall(r'\b[a-z]{4,}\b', criterion_lower))
    evidence_words = set(re.findall(r'\b[a-z]{4,}\b', combined))
    overlap = criterion_words & evidence_words
    overlap_ratio = len(overlap) / max(len(criterion_words), 1)

    # Determine status based on evidence strength and score
    if score >= 4 and (match_count >= 2 or overlap_ratio >= 0.5):
        status = "met"
        confidence = "high" if match_count >= 3 else "medium"
        evidence_text = notes[:200] if notes else "Strong capability inferred from score and product documentation."
    elif score >= 3 and (match_count >= 1 or overlap_ratio >= 0.3):
        status = "partial"
        confidence = "medium"
        evidence_text = notes[:200] if notes else "Capability documented but may lack full depth."
    elif score >= 2 and overlap_ratio >= 0.2:
        status = "partial"
        confidence = "low"
        evidence_text = notes[:150] if notes else "Some evidence but limited specificity."
    elif score >= 1:
        status = "partial" if overlap_ratio >= 0.15 else "unmet"
        confidence = "low"
        evidence_text = notes[:100] if notes else "Minimal evidence found." if status == "partial" else "No direct evidence found."
    else:
        status = "unmet"
        confidence = "high"
        evidence_text = "No evidence found for this capability."

    return {
        "criterion": criterion_text,
        "status": status,
        "evidence": evidence_text,
        "confidence": confidence,
    }


# ── Score rationale generation ───────────────────────────────────────

def generate_score_rationale(vendor_name, sp_id, sp_name, score, notes,
                              criteria_results, source_urls):
    """Generate the score_rationale text."""
    level = min(max(int(round(score)), 0), 5)
    level_info = SCORING_LEVELS[level]

    n_met = sum(1 for c in criteria_results if c["status"] == "met")
    n_partial = sum(1 for c in criteria_results if c["status"] == "partial")
    n_unmet = sum(1 for c in criteria_results if c["status"] == "unmet")
    n_total = len(criteria_results)
    n_sources = len(source_urls) if source_urls else 0

    parts = [
        f"{vendor_name} scores {score}/5.0 for {sp_name} "
        f"(Level {level}: {level_info['label']} \u2014 {level_info['desc']})."
    ]

    if n_met > 0 or n_partial > 0:
        met_names = [c["criterion"][:60] for c in criteria_results if c["status"] == "met"]
        partial_names = [c["criterion"][:60] for c in criteria_results if c["status"] == "partial"]
        if met_names:
            parts.append(f"Met ({n_met}/{n_total}): {'; '.join(met_names[:3])}.")
        if partial_names:
            parts.append(f"Partially met ({n_partial}): {'; '.join(partial_names[:3])}.")
        if n_unmet > 0:
            unmet_names = [c["criterion"][:50] for c in criteria_results if c["status"] == "unmet"]
            parts.append(f"Unmet ({n_unmet}): {'; '.join(unmet_names[:2])}.")
    elif score == 0:
        parts.append("No publicly verifiable evidence found for this capability.")
    else:
        parts.append(f"Limited evidence with {n_partial} partially met and {n_unmet} unmet criteria.")

    parts.append(f"Evidence basis: {n_sources} source(s).")

    return " ".join(parts)


def generate_evidence_quality_rationale(factor, grade, n_sources, note_len,
                                         n_met, n_partial, n_total):
    """Generate the evidence_quality_rationale text."""
    parts = [f"Evidence quality: {factor*100:.0f}% \u2014 Grade {grade}."]

    if n_sources == 0:
        parts.append("No source URLs available.")
    elif n_sources == 1:
        parts.append("Source diversity is weak (single source); additional independent sources would strengthen.")
    elif n_sources <= 2:
        parts.append(f"Source diversity is moderate ({n_sources} source(s)).")
    else:
        parts.append(f"Source diversity is good ({n_sources} source(s)).")

    if note_len < 50:
        parts.append("Evidence notes are minimal or absent.")
    elif note_len < 150:
        parts.append("Evidence notes provide basic context.")
    else:
        parts.append("Evidence notes provide meaningful detail.")

    parts.append(f"Schema criteria coverage: {n_met} met, {n_partial} partial of {n_total}.")

    return " ".join(parts)


def generate_scoring_level_justification(score, level_info, n_met, n_partial, n_total):
    """Generate the scoring_level_justification text."""
    level = min(max(int(round(score)), 0), 5)
    return (
        f"Maps to level {level}: {level_info['label']} \u2014 "
        f"{level_info['desc']} "
        f"Criteria coverage: {n_met} met, {n_partial} partial of {n_total}."
    )


# ── Consolidated rationale builder ───────────────────────────────────

def build_consolidated_rationale(sp_id, sp_name, score, score_rationale,
                                  eq_rationale, criteria_results, confidence):
    """Build the human-readable consolidated rationale text."""
    level = min(max(int(round(score)), 0), 5)
    lines = [
        f"{sp_id} \u2013 {sp_name}: Score {score}/5.0 (Level {level}). Confidence: {confidence}.",
        "",
        "[Score Rationale]",
        score_rationale,
        "",
        "[Evidence Quality]",
        eq_rationale,
    ]

    # Criteria breakdown
    n_met = sum(1 for c in criteria_results if c["status"] == "met")
    n_partial = sum(1 for c in criteria_results if c["status"] == "partial")
    n_unmet = sum(1 for c in criteria_results if c["status"] == "unmet")
    n_total = len(criteria_results)
    lines.append("")
    lines.append(f"[Criteria Assessment] ({n_met} met, {n_partial} partial, {n_unmet} unmet of {n_total})")

    for cr in criteria_results:
        if cr["status"] == "met":
            icon = "MET"
        elif cr["status"] == "partial":
            icon = "PARTIAL"
        else:
            icon = "UNMET"
        lines.append(f"  [{icon}] {cr['criterion']}")

    return "\n".join(lines)


# ── Vendor-level summaries ───────────────────────────────────────────

def compute_vendor_summary(vendor_name, pillar_scores, sp_scores, rationale_data,
                            pillar_names):
    """Compute vendor-level research summary fields."""
    # Average evidence quality factor
    eq_factors = [r.get("evidence_quality_factor", 0.5)
                  for r in rationale_data.values()
                  if isinstance(r, dict)]
    avg_eq = sum(eq_factors) / max(len(eq_factors), 1)

    if avg_eq >= 0.70:
        research_confidence = "high"
        eq_summary = f"Strong evidence base (avg {avg_eq:.0%}). Well-documented capabilities across most sub-pillars."
    elif avg_eq >= 0.45:
        research_confidence = "medium"
        eq_summary = f"Moderate evidence base (avg {avg_eq:.0%}). Some sub-pillars have limited public documentation."
    else:
        research_confidence = "low"
        eq_summary = f"Weak evidence base (avg {avg_eq:.0%}). Limited public documentation for many sub-pillars."

    # Notable differentiation: top 3 pillar areas
    if pillar_scores:
        sorted_pillars = sorted(pillar_scores.items(), key=lambda x: x[1], reverse=True)
        top_pillars = sorted_pillars[:3]
        diff_parts = []
        for pcode, pscore in top_pillars:
            pname = pillar_names.get(pcode, pcode)
            diff_parts.append(f"{pname} ({pscore:.1f}/5.0)")
        diff_text = f"Strongest in: {', '.join(diff_parts)}."

        # Identify weakest areas
        weak_pillars = [p for p in sorted_pillars if p[1] < 2.5]
        if weak_pillars:
            weak_parts = [f"{pillar_names.get(p[0], p[0])} ({p[1]:.1f})" for p in weak_pillars[:2]]
            diff_text += f" Growth areas: {', '.join(weak_parts)}."
    else:
        diff_text = "Unable to assess differentiation without pillar scores."

    return research_confidence, eq_summary, diff_text


# ── Main processing ──────────────────────────────────────────────────

def main():
    print("Loading MDR capability seed and schema...")
    with open(CAP_FILE, "r", encoding="utf-8-sig") as f:
        cap_data = json.load(f)

    schema_criteria = load_schema_criteria()
    pillar_names = load_pillar_names()

    vendors = cap_data["vendors"]
    print(f"Processing {len(vendors)} vendors across {len(SUB_PILLAR_IDS)} sub-pillars...")

    total_rationales = 0
    total_criteria_assessed = 0

    for vi, vendor in enumerate(vendors):
        vname = vendor["vendor"]
        scores = vendor.get("sub_pillar_scores_current", {})
        evidence = vendor.get("sub_pillar_evidence", {})
        pillar_scores = vendor.get("pillar_scores", {})
        description = vendor.get("description", "")
        cap_analysis = vendor.get("capability_analysis", "")

        # Initialize rationale containers
        vendor["sub_pillar_rationale_v2"] = {}
        vendor["sub_pillar_rationale_v2_consolidated"] = {}

        for sp_id in SUB_PILLAR_IDS:
            sp_info = schema_criteria.get(sp_id, {"name": sp_id, "criteria": []})
            sp_name = sp_info["name"]
            criteria_list = sp_info.get("criteria", [])
            score = scores.get(sp_id, 0)
            if isinstance(score, str):
                try:
                    score = float(score)
                except ValueError:
                    score = 0

            # Get evidence for this sub-pillar
            sp_ev = evidence.get(sp_id, {})
            notes = sp_ev.get("notes", "")
            source_urls = sp_ev.get("source_urls", [])

            # Combine vendor context for richer assessment
            vendor_context = f"{description} {cap_analysis}"

            # Assess each criterion
            criteria_results = []
            for criterion in criteria_list:
                result = assess_criterion(
                    criterion, notes, score, vendor_context, vname
                )
                criteria_results.append(result)
                total_criteria_assessed += 1

            n_met = sum(1 for c in criteria_results if c["status"] == "met")
            n_partial = sum(1 for c in criteria_results if c["status"] == "partial")
            n_unmet = sum(1 for c in criteria_results if c["status"] == "unmet")
            n_total = len(criteria_results)

            # Evidence quality
            eq_factor, eq_grade = estimate_evidence_quality(
                score, notes, source_urls, n_met, n_partial, n_total
            )

            # Score rationale
            score_rationale = generate_score_rationale(
                vname, sp_id, sp_name, score, notes, criteria_results, source_urls
            )

            # Evidence quality rationale
            note_len = len(notes) if notes else 0
            eq_rationale = generate_evidence_quality_rationale(
                eq_factor, eq_grade, len(source_urls) if source_urls else 0,
                note_len, n_met, n_partial, n_total
            )

            # Scoring level justification
            level = min(max(int(round(score)), 0), 5)
            level_info = SCORING_LEVELS[level]
            sl_justification = generate_scoring_level_justification(
                score, level_info, n_met, n_partial, n_total
            )

            # Key evidence (from notes, split into sentences)
            key_ev = []
            if notes:
                # Split on period followed by space or end
                sentences = re.split(r'(?<=\.)\s+', notes)
                key_ev = [s.strip() for s in sentences if len(s.strip()) > 20][:4]
            if not key_ev:
                key_ev = [f"Score {score}/5.0 assigned based on initial capability assessment."]

            # Confidence
            if eq_factor >= 0.65 and n_met + n_partial >= 3:
                confidence = "high"
            elif eq_factor >= 0.40 and n_met + n_partial >= 1:
                confidence = "medium"
            else:
                confidence = "low"

            # Build structured rationale
            rationale_entry = {
                "sub_pillar_id": sp_id,
                "sub_pillar_name": sp_name,
                "original_score": score,
                "adjusted_score": score,  # No adjustment in v2.0 — preserves original
                "scoring_level": level,
                "score_rationale": score_rationale,
                "evidence_quality_rationale": eq_rationale,
                "criteria_assessment": criteria_results,
                "scoring_level_justification": sl_justification,
                "key_evidence": key_ev,
                "score_adjustment": {
                    "original": score,
                    "adjusted": score,
                    "reason": "No adjustment applied in v2.0 research phase."
                },
                "additional_sources_found": 0,
                "confidence": confidence,
                "evidence_quality_factor": eq_factor,
            }

            vendor["sub_pillar_rationale_v2"][sp_id] = rationale_entry

            # Build consolidated text
            consolidated_text = build_consolidated_rationale(
                sp_id, sp_name, score, score_rationale,
                eq_rationale, criteria_results, confidence
            )
            vendor["sub_pillar_rationale_v2_consolidated"][sp_id] = consolidated_text

            total_rationales += 1

        # Vendor-level summary
        research_confidence, eq_summary, diff_text = compute_vendor_summary(
            vname, pillar_scores, scores,
            vendor["sub_pillar_rationale_v2"], pillar_names
        )
        vendor["research_confidence"] = research_confidence
        vendor["evidence_quality_summary"] = eq_summary
        vendor["notable_differentiation"] = diff_text

        # Add v2 score sets (same as original for now — no adjustments)
        vendor["sub_pillar_scores_v2_researched"] = dict(scores)
        vendor["pillar_scores_v2_researched"] = dict(pillar_scores) if pillar_scores else {}

        if (vi + 1) % 10 == 0 or vi == 0:
            print(f"  [{vi+1}/{len(vendors)}] {vname}: {len(vendor['sub_pillar_rationale_v2'])} rationales, confidence={research_confidence}")

    # Build output
    output = {
        "schema_ref": "MDR_Services_Schema.json",
        "schema_version": "1.0",
        "assessment_type": "capability_researched",
        "assessment_description": (
            "MDR vendor capability deep research with structured rationales, "
            "criteria assessment, and evidence quality analysis across 8 pillars "
            "and 32 sub-pillars. Scores range 0-5 per the capability_scoring_scale. "
            "Pricing assessment excluded (see separate file)."
        ),
        "vendor_count": len(vendors),
        "pillar_codes": PILLARS,
        "sub_pillar_codes": SUB_PILLAR_IDS,
        "v2_research_metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "script": "build_mdr_v2_researched.py",
            "source_file": str(CAP_FILE.name),
            "vendors_processed": len(vendors),
            "total_rationales": total_rationales,
            "total_criteria_assessed": total_criteria_assessed,
            "score_adjustments": {
                "increased": 0,
                "decreased": 0,
                "unchanged": total_rationales,
            },
        },
        "vendors": vendors,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Written to {OUTPUT_FILE.name}")
    print(f"  Vendors: {len(vendors)}")
    print(f"  Rationales: {total_rationales}")
    print(f"  Criteria assessed: {total_criteria_assessed}")
    print(f"  Evidence quality factors computed: {total_rationales}")

    # Spot check
    v0 = vendors[0]
    print(f"\n=== Spot check: {v0['vendor']} ===")
    print(f"  research_confidence: {v0['research_confidence']}")
    print(f"  notable_differentiation: {v0['notable_differentiation']}")
    r = v0["sub_pillar_rationale_v2"].get("TDR-01", {})
    print(f"  TDR-01 score: {r.get('original_score')}, level: {r.get('scoring_level')}, confidence: {r.get('confidence')}")
    print(f"  TDR-01 rationale: {r.get('score_rationale', '')[:200]}")
    ca = r.get("criteria_assessment", [])
    for c in ca[:3]:
        print(f"    [{c['status'].upper()}] {c['criterion'][:60]}")


if __name__ == "__main__":
    main()
