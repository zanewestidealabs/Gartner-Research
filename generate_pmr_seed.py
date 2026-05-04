"""
generate_pmr_seed.py — Generate Product Market Readiness seed vendor file.

Reads all existing consolidated/researched vendor data files across
AI TRiSM, MDR Services, Preemptive Cyber, Offensive Security, and Secure by Design
schemas and produces a deduplicated cross-schema seed file with 25 sub-pillars
(5 pillars × 5 sub-pillars each) using dual scoring (GTM Messaging + Proof of Execution).

Writes: Product Market Readiness Vendor 1-0 Seed.json
Schema: Product Market Readiness Schema 1_0.json
"""

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent

# ── Source vendor files (use most consolidated version available) ──────
VENDOR_SOURCES = {
    "ai_trism": {
        "file": ROOT / "AI TRiSM Vendor 2-1 Consolidated.json",
        "label": "AI TRiSM",
        "pillar_key": "pillar_scores"
    },
    "mdr_services": {
        "file": ROOT / "MDR Services Vendor 2-0 Researched.json",
        "label": "MDR Services",
        "pillar_key": "pillar_scores"
    },
    "preemptive_cyber": {
        "file": ROOT / "Preemptive Cyber Vendor 2-1 Consolidated.json",
        "label": "Preemptive Cyber",
        "pillar_key": "pillar_scores"
    },
    "offensive_security": {
        "file": ROOT / "Offensive Security Vendor 2-0 Researched.json",
        "label": "Offensive Security",
        "pillar_key": "pillar_scores"
    },
    "secure_by_design": {
        "file": ROOT / "Secure by Design Vendor 2-0 Scored.json",
        "label": "Secure by Design",
        "pillar_key": "pillar_scores"
    }
}

# Fallback files if primary doesn't exist
FALLBACKS = {
    "ai_trism": [
        ROOT / "AI TRiSM Vendor 2-0 Researched.json",
        ROOT / "AI TRiSM Vendor 1-0 Seed.json"
    ],
    "mdr_services": [
        ROOT / "MDR Services Vendor 2-1 Consolidated.json",
        ROOT / "MDR Services Vendor 1-0 Seed.json"
    ],
    "preemptive_cyber": [
        ROOT / "Preemptive Cyber Vendor 2-0 Researched.json",
        ROOT / "Preemptive Cybersecurity Vendor 1-0 Seed.json"
    ],
    "offensive_security": [
        ROOT / "Offensive Security Vendor 2-2 Researched.json",
        ROOT / "Offensive Security Vendor 1-0 Seed.json"
    ],
    "secure_by_design": [
        ROOT / "Secure by Design Vendor 6-0 AI Researched.json",
        ROOT / "Secure by Design Vendor 5-0 Scored.json",
        ROOT / "Secure by Design Vendor 4-0 Scored.json",
        ROOT / "Secure by Design Vendor 3-4 Scored.json"
    ]
}

OUTPUT_FILE = ROOT / "Product Market Readiness Vendor 1-0 Seed.json"
SCHEMA_FILE = "Product Market Readiness Schema 1_0.json"

# ── PMR sub-pillar definitions ────────────────────────────────────────
PMR_PILLARS = ["PPD", "PCS", "TDT", "PCM", "CTL"]
PMR_SUB_PILLARS = {
    "PPD-01": "Capability Claim Specificity",
    "PPD-02": "Competitive Differentiation Clarity",
    "PPD-03": "Target Persona & Use-Case Alignment",
    "PPD-04": "Market Category Ownership",
    "PPD-05": "Messaging Consistency & Coherence",
    "PCS-01": "Customer Case Study Depth",
    "PCS-02": "Third-Party Validation & Analyst Recognition",
    "PCS-03": "Deployment Scale & Metric Transparency",
    "PCS-04": "ROI & Business Outcome Documentation",
    "PCS-05": "Customer Reference Breadth",
    "TDT-01": "Architecture & Design Documentation",
    "TDT-02": "API & Integration Ecosystem",
    "TDT-03": "Detection & Methodology Transparency",
    "TDT-04": "Data Handling & Privacy Transparency",
    "TDT-05": "Technical Enablement & Documentation Quality",
    "PCM-01": "Pricing Model Transparency",
    "PCM-02": "Packaging & Tier Clarity",
    "PCM-03": "Total Cost of Ownership Articulation",
    "PCM-04": "Trial & Evaluation Accessibility",
    "PCM-05": "Commercial Terms & Contract Flexibility",
    "CTL-01": "Original Research & Data Publication",
    "CTL-02": "Conference & Speaking Presence",
    "CTL-03": "Blog & Educational Content Quality",
    "CTL-04": "Open-Source & Community Contribution",
    "CTL-05": "Market Education & Category Development"
}

# ── Name normalization for deduplication ──────────────────────────────
NAME_ALIASES = {
    "underdefense": "UnderDefense",
    "tcs (tata consultancy)": "Tata Consultancy Services",
    "tata consultancy services": "Tata Consultancy Services",
    "ey (ernst & young)": "EY (Ernst & Young)",
    "ey": "EY (Ernst & Young)",
    "aws (amazon web services)": "AWS (Amazon Web Services)",
    "aws": "AWS (Amazon Web Services)",
    "bcg (boston consulting group)": "BCG (Boston Consulting Group)",
    "lti (larsen & toubro infotech)": "LTI (Larsen & Toubro Infotech)",
    "ibm security": "IBM",
    "ibm": "IBM",
    "google cloud": "Google Cloud",
    "google": "Google Cloud",
}


def normalize_name(name: str) -> str:
    """Normalize vendor name for dedup. Returns canonical form."""
    key = name.strip().lower()
    return NAME_ALIASES.get(key, name.strip())


def resolve_file(schema_key: str) -> Path | None:
    """Find the best available vendor file for a schema domain."""
    cfg = VENDOR_SOURCES[schema_key]
    if cfg["file"].exists():
        return cfg["file"]
    for fb in FALLBACKS.get(schema_key, []):
        if fb.exists():
            return fb
    return None


def load_vendors(filepath: Path) -> list[dict]:
    """Load vendor list from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("vendors", [])


def extract_cross_scores(vendor: dict, pillar_key: str) -> dict:
    """Extract pillar-level scores for cross-reference."""
    scores = vendor.get(pillar_key, {})
    if not scores:
        return {}
    non_zero = {k: v for k, v in scores.items() if v and v > 0}
    if not non_zero:
        return {}
    avg = round(sum(non_zero.values()) / len(non_zero), 2)
    top_pillar = max(non_zero, key=non_zero.get)
    return {
        "pillar_avg": avg,
        "top_pillar": top_pillar,
        "top_score": non_zero[top_pillar],
        "scored_pillars": len(non_zero)
    }


def build_pmr_vendor(canonical_name: str, appearances: dict) -> dict:
    """Build a PMR seed vendor entry from cross-schema appearances."""
    # Pick the richest source for metadata
    best = None
    best_fields = 0
    for schema_key, vendor_data in appearances.items():
        n = len([v for v in vendor_data.values() if v])
        if n > best_fields:
            best = vendor_data
            best_fields = n

    # Cross-schema scores
    cross_scores = {}
    for schema_key, vendor_data in appearances.items():
        cfg = VENDOR_SOURCES[schema_key]
        cs = extract_cross_scores(vendor_data, cfg["pillar_key"])
        if cs:
            cross_scores[schema_key] = cs

    # Build initial zero scores
    pillar_gtm = {p: 0 for p in PMR_PILLARS}
    pillar_proof = {p: 0 for p in PMR_PILLARS}
    pillar_gaps = {p: 0.0 for p in PMR_PILLARS}
    sub_gtm = {sp: 0 for sp in PMR_SUB_PILLARS}
    sub_proof = {sp: 0 for sp in PMR_SUB_PILLARS}
    sub_gaps = {sp: 0.0 for sp in PMR_SUB_PILLARS}

    return {
        "vendor": canonical_name,
        "website": best.get("website", ""),
        "headquarters": best.get("headquarters", ""),
        "region": best.get("region", ""),
        "vendor_type": best.get("vendor_type", ""),
        "is_startup": best.get("is_startup", False),
        "is_ai_first": best.get("is_ai_first", False),
        "description": best.get("description", ""),
        "key_differentiators": best.get("key_differentiators", ""),
        "product_names": best.get("product_names", []),
        "source_schemas": sorted(appearances.keys()),
        "cross_schema_scores": cross_scores,
        "pillar_gtm_scores": pillar_gtm,
        "pillar_proof_scores": pillar_proof,
        "pillar_gaps": pillar_gaps,
        "overall_gtm_score": 0,
        "overall_proof_score": 0,
        "overall_credibility_gap": 0.0,
        "coverage_grade": "F",
        "sub_pillar_scores": {
            sp_id: {
                "gtm_messaging_score": 0,
                "proof_of_execution_score": 0,
                "credibility_gap": 0.0,
                "gtm_rationale": "",
                "proof_rationale": "",
                "gap_assessment": "",
                "source_urls": [],
                "excerpts": []
            }
            for sp_id in PMR_SUB_PILLARS
        },
        "sub_pillar_schema_labels": dict(PMR_SUB_PILLARS)
    }


def main():
    print("=" * 70)
    print("Product Market Readiness — Seed Generator")
    print("=" * 70)

    # ── Step 1: Load all vendor sources ───────────────────────────────
    all_vendors: dict[str, dict] = {}  # canonical_name -> {schema_key: vendor_data}

    for schema_key, cfg in VENDOR_SOURCES.items():
        filepath = resolve_file(schema_key)
        if not filepath:
            print(f"  ⚠ {cfg['label']:25s} — no vendor file found, skipping")
            continue

        vendors = load_vendors(filepath)
        print(f"  ✓ {cfg['label']:25s} — {len(vendors):3d} vendors from {filepath.name}")

        for v in vendors:
            name = normalize_name(v.get("vendor", ""))
            if not name:
                continue
            if name not in all_vendors:
                all_vendors[name] = {}
            all_vendors[name][schema_key] = v

    print(f"\n  Total unique vendors: {len(all_vendors)}")

    # ── Step 2: Build PMR seed entries ────────────────────────────────
    pmr_vendors = []
    for canonical_name in sorted(all_vendors.keys()):
        appearances = all_vendors[canonical_name]
        pmr_vendor = build_pmr_vendor(canonical_name, appearances)
        pmr_vendors.append(pmr_vendor)

    # ── Step 3: Stats ─────────────────────────────────────────────────
    multi_schema = [v for v in pmr_vendors if len(v["source_schemas"]) >= 2]
    three_plus = [v for v in pmr_vendors if len(v["source_schemas"]) >= 3]
    print(f"  Multi-schema vendors (2+): {len(multi_schema)}")
    print(f"  Cross-cutting vendors (3+): {len(three_plus)}")

    for v in three_plus:
        schemas = ", ".join(v["source_schemas"])
        print(f"    {v['vendor']:30s} [{len(v['source_schemas'])}] {schemas}")

    # ── Step 4: Write seed file ───────────────────────────────────────
    output = {
        "schema_ref": SCHEMA_FILE,
        "schema_version": "1.0",
        "seed_version": "1.0",
        "seed_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seed_notes": (
            "Cross-schema seed file aggregating all unique vendors from AI TRiSM, "
            "MDR Services, Preemptive Cyber, Offensive Security, and Secure by Design schemas. "
            "Each vendor has 25 sub-pillars (5 pillars × 5) with dual GTM Messaging and "
            "Proof of Execution scores initialized to 0. Cross-schema capability scores "
            "are pre-populated for vendors appearing in existing schemas."
        ),
        "vendor_count": len(pmr_vendors),
        "pillar_codes": PMR_PILLARS,
        "sub_pillar_count": len(PMR_SUB_PILLARS),
        "vendors": pmr_vendors
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"\n  ✓ Written: {OUTPUT_FILE.name} ({size_kb:.0f} KB, {len(pmr_vendors)} vendors)")
    print("=" * 70)


if __name__ == "__main__":
    main()
