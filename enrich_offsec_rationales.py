"""
enrich_offsec_rationales.py — Rewrite thin OffSec rationales into analyst-quality assessments
================================================================================================

Processes all sub_pillar_evidence entries in the v2.1 file. For entries with
thin rationales (starting with "X provides this capability" or very short),
rewrites them into proper analyst-style rationales that:

  - Reference the scoring rubric (0-5 scale)
  - Incorporate evidence from extracted excerpts
  - Include specific product names, metrics, and technical detail
  - Explain WHY the score was given, not just WHAT the vendor does
  - Follow the pattern established by the hand-crafted Batch 1 rationales

Usage:
  python enrich_offsec_rationales.py             # enrich and write
  python enrich_offsec_rationales.py --dry-run    # preview without writing
  python enrich_offsec_rationales.py --batch 1/3  # process batch N of M
  python enrich_offsec_rationales.py --merge      # merge batch files
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent
VENDOR_FILE = ROOT / "Offensive Security Vendor 2-1 Consolidated.json"
SCHEMA_FILE = ROOT / "Offensive_Security_Schema.json"

PILLARS = ["ASM", "VUL", "OFT", "APP", "REM"]
SUB_PILLAR_IDS = [f"{p}-{i:02d}" for p in PILLARS for i in range(1, 6)]

# Score rubric for reference in rationale construction
SCORE_RUBRIC = {
    0: "No Evidence",
    1: "Minimal: Basic or manual capability; no automation or continuous operation",
    2: "Generic Claims: Marketing mentions but lacks specifics, named products, or metrics",
    3: "Demonstrated: Documented capability with named products, some technical detail",
    4: "Advanced: Named products with measurable outcomes, integration, analyst recognition",
    5: "Market-Leading: Best-in-class with deep technical evidence, analyst leadership, measurable impact",
}


def load_schema() -> Dict[str, Dict[str, Any]]:
    """Load sub-pillar definitions from schema."""
    with open(SCHEMA_FILE, "r", encoding="utf-8-sig") as f:
        raw = json.load(f)
    body = raw.get("offensive_security_taxonomy_v1.0", raw)
    sp_data = body.get("sub_pillars", {})
    result = {}
    for sp_id, info in sp_data.items():
        if sp_id in SUB_PILLAR_IDS:
            result[sp_id] = {
                "name": info.get("name", sp_id),
                "expanded_definition": info.get("expanded_definition", ""),
                "what_to_verify_publicly": info.get("what_to_verify_publicly", []),
            }
    return result


def is_thin_rationale(rationale: str) -> bool:
    """Check if a rationale needs enrichment."""
    if not rationale:
        return True
    if "provides this capability" in rationale.lower():
        return True
    if len(rationale) < 80:
        return True
    return False


def extract_existing_facts(rationale: str) -> List[str]:
    """Extract useful factual claims from existing thin rationale."""
    facts = []
    # Remove the "X provides this capability." prefix
    text = re.sub(r'^[^.]+provides this capability\.?\s*', '', rationale, flags=re.IGNORECASE)
    # Split into sentences
    sentences = re.split(r'(?<=[.!])\s+', text)
    for s in sentences:
        s = s.strip()
        if len(s) > 15 and s not in facts:
            facts.append(s)
    return facts


def build_enriched_rationale(
    vendor_name: str,
    sp_id: str,
    score: int,
    existing_rationale: str,
    evidence: Dict[str, Any],
    schema_sp: Dict[str, Any],
) -> str:
    """Build an analyst-quality rationale from existing data + excerpts."""

    sp_name = schema_sp.get("name", sp_id)
    sp_def = schema_sp.get("expanded_definition", "")
    criteria = schema_sp.get("what_to_verify_publicly", [])
    excerpts = evidence.get("excerpts", [])
    sources = evidence.get("sources", [])

    # Extract existing facts (strip "provides this capability" prefix)
    existing_facts = extract_existing_facts(existing_rationale)


    # Get product names from sources
    product_names = set()
    skip_words = {"documentation", "docs", "analyst", "recognition", "report"}
    for src in sources:
        title = src.get("title", "")
        # Extract product name (usually before the dash)
        pname = ""
        if " — " in title:
            pname = title.split(" — ")[0].strip()
        elif " - " in title:
            pname = title.split(" - ")[0].strip()
        if pname and pname != vendor_name:
            if not any(w in pname.lower() for w in skip_words):
                product_names.add(pname)

    # Determine score justification language
    if score >= 5:
        score_qualifier = "market-leading"
        score_evidence_need = "Deep technical evidence, analyst leadership recognition, and measurable impact metrics support this assessment."
    elif score >= 4:
        score_qualifier = "advanced"
        score_evidence_need = "Named products with measurable outcomes, integration points, and analyst recognition are documented."
    elif score >= 3:
        score_qualifier = "demonstrated"
        score_evidence_need = "Documented capability with named products and identifiable technical detail."
    elif score >= 2:
        score_qualifier = "limited"
        score_evidence_need = "Marketing references exist but lack specific technical documentation or measurable outcomes."
    elif score >= 1:
        score_qualifier = "minimal"
        score_evidence_need = "Basic or manual capability without automation or continuous operation."
    else:
        score_qualifier = "absent"
        score_evidence_need = "No publicly verifiable evidence of capability."

    # Build the rationale
    parts = []

    # Opening: what the vendor does for this sub-pillar
    if product_names:
        product_str = ", ".join(sorted(product_names)[:3])
        parts.append(f"{vendor_name} delivers {score_qualifier} {sp_name.lower()} capability through {product_str}.")
    else:
        parts.append(f"{vendor_name} provides {score_qualifier} {sp_name.lower()} capability.")

    # Body: existing facts (cleaned of boilerplate)
    for fact in existing_facts[:4]:
        # Don't duplicate what we already said
        if fact.lower() not in parts[0].lower():
            parts.append(fact)

    # Evidence from excerpts (if high-relevance, score 6+ to avoid generic headlines)
    high_relevance_excerpts = []
    for ex in excerpts[:5]:
        text = ex.get("excerpt", "")
        relevance = ex.get("relevance_score", 0)
        if relevance >= 6 and len(text) > 40:
            clean = text.strip()
            if len(clean) > 200:
                clean = clean[:200].rsplit(" ", 1)[0] + "..."
            high_relevance_excerpts.append(clean)
    if high_relevance_excerpts and score >= 3:
        best = high_relevance_excerpts[0]
        if best.lower() not in " ".join(parts).lower():
            parts.append(f"Public documentation confirms: \"{best}\"")

    # Score justification
    parts.append(f"Score {score}/5 ({score_qualifier}): {score_evidence_need}")

    # Source count
    source_types = set()
    for src in sources:
        tier = src.get("tier", "")
        stype = src.get("type", "")
        if tier and stype:
            source_types.add(f"{stype} (Tier {tier})")
    if source_types:
        parts.append(f"Evidence base: {', '.join(sorted(source_types)[:3])}.")

    return " ".join(parts)


def merge_batches():
    """Merge batch output files into the main v2.1 file."""
    print("Merging rationale batch files...")
    with open(VENDOR_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    batch_files = sorted(ROOT.glob("offsec_rationale_batch_*.json"))
    if not batch_files:
        print("ERROR: No batch files found (offsec_rationale_batch_*.json)")
        return

    print(f"  Found {len(batch_files)} batch files")
    vendors_updated = 0

    for bf in batch_files:
        print(f"  Reading {bf.name}...")
        with open(bf, "r", encoding="utf-8") as f:
            batch_data = json.load(f)

        batch_vendors = {v["vendor"]: v for v in batch_data["vendors"]}
        for vendor in data["vendors"]:
            vname = vendor["vendor"]
            if vname in batch_vendors:
                bv = batch_vendors[vname]
                if "sub_pillar_evidence" in bv:
                    vendor["sub_pillar_evidence"] = bv["sub_pillar_evidence"]
                vendors_updated += 1

    with open(VENDOR_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nMerge complete: {vendors_updated} vendors updated")
    print(f"Written to {VENDOR_FILE.name}")

    for bf in batch_files:
        bf.unlink()
        print(f"  Removed {bf.name}")


def main():
    parser = argparse.ArgumentParser(description="Enrich OffSec rationales")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--batch", type=str, default="")
    parser.add_argument("--merge", action="store_true")
    args = parser.parse_args()

    if args.merge:
        merge_batches()
        return

    print("=" * 60)
    print("Offensive Security Rationale Enrichment")
    print("=" * 60)

    with open(VENDOR_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    schema = load_schema()
    print(f"Schema: {len(schema)} sub-pillars loaded")

    vendors = data["vendors"]

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
        print(f"Batch {batch_num}/{batch_total}: vendors {start+1}-{end}")

    total_enriched = 0
    total_kept = 0
    total_scored = 0

    for vi, vendor in enumerate(vendors):
        vname = vendor["vendor"]
        scores = vendor.get("sub_pillar_scores_current", {})
        evidence = vendor.get("sub_pillar_evidence", {})
        vendor_enriched = 0

        for sp_id in SUB_PILLAR_IDS:
            sc = scores.get(sp_id, 0)
            if sc == 0:
                continue
            total_scored += 1

            ev = evidence.get(sp_id, {})
            rat = ev.get("rationale", "")
            sp_schema = schema.get(sp_id, {})

            if is_thin_rationale(rat):
                new_rat = build_enriched_rationale(
                    vname, sp_id, sc, rat, ev, sp_schema
                )
                ev["rationale"] = new_rat
                evidence[sp_id] = ev
                vendor_enriched += 1
                total_enriched += 1
            else:
                total_kept += 1

        if vendor_enriched > 0:
            print(f"  [{vi+1}/{len(vendors)}] {vname}: {vendor_enriched} rationales enriched")

    print(f"\n{'=' * 60}")
    print(f"Total scored entries: {total_scored}")
    print(f"Rationales enriched: {total_enriched}")
    print(f"Rationales kept (already adequate): {total_kept}")

    if not args.dry_run:
        if args.batch:
            out_file = ROOT / f"offsec_rationale_batch_{batch_num}.json"
            batch_data = dict(data)
            batch_data["vendors"] = vendors
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(batch_data, f, indent=2, ensure_ascii=False)
            print(f"Written to {out_file.name}")
        else:
            with open(VENDOR_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Written to {VENDOR_FILE.name}")
    else:
        print("[DRY RUN] No files written")

    print("=" * 60)


if __name__ == "__main__":
    main()
