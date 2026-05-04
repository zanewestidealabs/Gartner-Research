# PreCyber Research Pipeline Instructions

> Automated pipeline for scoring 51 Preemptive Cybersecurity vendors across 4 pillars and 16 sub-pillars using web-crawling evidence extraction, criterion-based rationale analysis, and consolidation. Matches the TRiSM pipeline methodology exactly.

---

## Pipeline Overview

```
Seed (1-0) ──► Stage 1: Evidence (1-1 Validated) ──► Stage 2: Rationale (2-0 Researched) ──► Stage 3: Consolidate (2-1 Consolidated)
```

| Stage | Script | Input | Output | Purpose |
|-------|--------|-------|--------|---------|
| Seed | `generate_precyber_seed.py` | Schema JSON | `Preemptive Cybersecurity Vendor 1-0 Seed.json` | Initial vendor list with metadata |
| 1 | `research_precyber_v1_evidence.py` | 1-0 Seed | `Preemptive Cybersecurity Vendor 1-1 Validated.json` | Web crawl + evidence extraction + scoring |
| 2 | `research_precyber_v2_rationale.py` | 1-1 Validated | `Preemptive Cybersecurity Vendor 2-0 Researched.json` | Deep criterion assessment + rationale generation |
| 3 | `build_precyber_v2_1.py` | 2-0 Researched | `Preemptive Cybersecurity Vendor 2-1 Consolidated.json` | Formatted rationales + vendor summaries |

---

## Schema Reference

**File:** `Preemptive_Cybersecurity_Schema.json`  
**Top key:** `preemptive_cybersecurity_taxonomy_v1.0`  
**Structure:** Flat (not grouped)

### Pillars & Sub-Pillars

| Pillar | Name | Sub-Pillars |
|--------|------|-------------|
| **EXM** | Exposure Management | EXM-01: Attack Surface Management, EXM-02: CTEM, EXM-03: Vulnerability Prioritization & Management, EXM-04: Third-Party & Supply Chain Exposure |
| **AMT** | Automated Moving Target Defense | AMT-01: Polymorphic & Morphing Defense, AMT-02: Runtime Application Protection, AMT-03: Dynamic Network & Infrastructure Defense, AMT-04: Identity & Credential Rotation |
| **ADR** | Adversary Disruption | ADR-01: Deception Technology, ADR-02: Threat Intelligence Operationalization, ADR-03: Proactive Threat Hunting, ADR-04: Counter-Adversary Operations |
| **PPM** | Preemptive Posture Management | PPM-01: Breach & Attack Simulation, PPM-02: Security Control Validation, PPM-03: Penetration Testing & Red Teaming, PPM-04: Cloud Security Posture Management |

### Scoring Scale (0–5)

| Score | Level | Meaning |
|-------|-------|---------|
| 0 | No Evidence | No publicly verifiable evidence |
| 1 | Minimal | Basic/manual capability only |
| 2 | Generic Claims | Marketing mentions without named products or technical detail |
| 3 | Demonstrated | Documented capability with named products, technical detail, use cases |
| 4 | Advanced | Named products with measurable outcomes, integration, analyst recognition |
| 5 | Market-Leading | Best-in-class with deep technical evidence, extensive customer base |

### Grades

**Coverage Grade** (sub-pillars with score > 0):
- A: 13–16 (81–100%), B: 10–12 (63–75%), C: 7–9 (44–56%), D: 4–6 (25–38%), F: 1–3 (6–19%)

**Quality Grade** (average evidence quality factor):
- A: ≥0.80, B: ≥0.60, C: ≥0.40, D: ≥0.20, F: <0.20

---

## Stage 1: Evidence Extraction (`research_precyber_v1_evidence.py`)

### What It Does
1. Loads the 1-0 Seed JSON (51 vendors)
2. For each vendor, fetches 5–6 curated URLs (defined in `VENDOR_URLS`)
3. Extracts text from HTML pages using `_HTMLTextExtractor`
4. Caches pages in `research/cache/pages_precyber/` (SHA1 hash filenames)
5. For each of 16 sub-pillars:
   - Builds per-sub-pillar term sets from schema `what_to_verify_publicly` + `search_terms`
   - Searches page text for term matches with synonym expansion
   - Scores specificity based on schema_criteria_hits and pillar_term_hits
   - Extracts top evidence excerpts ranked by relevance score
6. Assigns research_flag per vendor: `good_evidence`, `partial_evidence`, `low_evidence`, `fetch_failed`, `no_evidence`
7. Non-`good_evidence` vendors are capped at 3.0

### Key CLI Arguments

```bash
# Full run (all 51 vendors, 11 batches of 5)
python research_precyber_v1_evidence.py

# Resume from last checkpoint
python research_precyber_v1_evidence.py --resume

# Merge existing batch files only (no processing)
python research_precyber_v1_evidence.py --merge-only

# Faster batch pauses (default: 30s)
python research_precyber_v1_evidence.py --batch-pause 2

# Force re-fetch all URLs (ignore cache)
python research_precyber_v1_evidence.py --force-fetch

# Limit vendors for testing
python research_precyber_v1_evidence.py --max-vendors 5
```

### Scoring Logic (v1)

```
specificity calculation (per sub-pillar, per vendor):
  schema_criteria_hits ≥ 4  →  specificity = 5.0
  schema_criteria_hits ≥ 3  →  specificity = 4.0
  schema_criteria_hits ≥ 2 AND pillar_hits ≥ 3  →  specificity = 3.5
  schema_criteria_hits ≥ 1 AND pillar_hits ≥ 2  →  specificity = 3.0
  pillar_hits ≥ 3  →  specificity = 2.5
  pillar_hits ≥ 1  →  specificity = 2.0
  any primary term match  →  specificity = 1.5
  else  →  specificity = 0.0

score = _score_subpillar_precyber(specificity, criteria_hit_count, total_excerpts)
  specificity > 4.0  → base 4.5 (+0.25 if criteria_hit_count ≥ 5)
  specificity > 3.0  → base 4.0 (±0.25 based on criteria_hit_count)
  specificity > 2.0  → base 3.0 (±0.25 based on criteria_hit_count)
  specificity > 0.5  → base 2.0 (+0.25 if criteria_hit_count ≥ 3)
  else  → 0.0 or 1.0
```

### CRITICAL: Criteria Set Construction

The `_build_schema_criteria_set()` function must **NOT** split criterion phrases into individual words. Individual words like "automated", "monitoring", "management" match on every cybersecurity page and inflate all scores to 4.75. Only full phrases and `search_terms` from the schema are used.

### Batch Processing

- 11 batches of 5 vendors each
- Checkpoint file: `research/precyber_checkpoints/precyber_evidence_progress.json`
- Per-batch files: `research/precyber_batches/batch_01.json` through `batch_11.json`
- Page cache: `research/cache/pages_precyber/` (SHA1-hashed filenames, persists across runs)
- Default 30s pause between batches (use `--batch-pause 2` for faster runs)

### Output Fields per Vendor

```json
{
  "vendor": "...",
  "sub_pillar_evidence": { "EXM-01": { "source_urls": [], "excerpts": [], "sub_pillar_specificity": 0.0, "schema_criteria_hits": 0, "pillar_term_hits": 0 } },
  "sub_pillar_scores_validated": { "EXM-01": 0.0, ... },
  "pillar_scores": { "EXM": 0.0, "AMT": 0.0, "ADR": 0.0, "PPM": 0.0 },
  "research_flag": "good_evidence|partial_evidence|low_evidence|fetch_failed|no_evidence",
  "research_confidence": 0.0,
  "research": { "status": "validated", "source": "precyber_v1_evidence_pipeline", "timestamp": "..." }
}
```

---

## Stage 2: Rationale Analysis (`research_precyber_v2_rationale.py`)

### What It Does
1. Reads the 1-1 Validated JSON
2. Re-loads cached page text for each vendor
3. For each sub-pillar:
   - Assesses each `what_to_verify_publicly` criterion individually
   - Uses conceptual matching: key word extraction, concept pairs, synonym expansion
   - Determines scoring level (0–5) using 6-factor analysis
   - Generates detailed rationale text
   - Adjusts scores within ±1.5 of v1 score (only applied if diff ≥ 0.5)
4. Builds evidence quality rationale

### Key CLI Arguments

```bash
# Full run with additional URL discovery
python research_precyber_v2_rationale.py

# Skip new URL fetching (use cached pages only — much faster)
python research_precyber_v2_rationale.py --no-fetch

# Limit vendors for testing
python research_precyber_v2_rationale.py --max-vendors 5
```

### Score Adjustment Rules

- **±1.5 cap**: v2 score can differ from v1 by at most 1.5 points
- **0.5 threshold**: If difference < 0.5, v1 score is confirmed unchanged
- **Criterion status**: "met" (≥70% word coverage + pairs), "partial" (≥40%), "unmet"
- **Level 5** requires: v1_signal ≥ 0.7, coverage ≥ 60%, schema_hits ≥ 3, metrics or architecture, specificity ≥ 4.0
- **Level 4** requires: v1_signal ≥ 0.5, coverage ≥ 40%, schema_hits ≥ 2 or pillar_hits ≥ 4, specificity ≥ 3.0
- **Level 3** requires: v1_signal ≥ 0.3, some evidence present

### CRITICAL: No Word-Splitting in Schema Term Hits

Same as v1 — `schema_term_hits` must use full-phrase matching for criterion text. Do NOT split into individual words.

### Output Fields Added

```json
{
  "sub_pillar_rationale_v2": {
    "EXM-01": {
      "name": "...",
      "original_score": 0.0,
      "adjusted_score": 0.0,
      "scoring_level": 4,
      "score_rationale": "...",
      "evidence_quality_rationale": "...",
      "criteria_assessment": [ { "criterion": "...", "status": "met|partial|unmet", "evidence": "...", "confidence": "high|medium|low" } ],
      "key_evidence": ["..."],
      "score_adjustment": { "original": 0.0, "adjusted": 0.0, "reason": "..." },
      "confidence": "high|medium|low",
      "evidence_quality_factor": 0.0
    }
  }
}
```

---

## Stage 3: Consolidation (`build_precyber_v2_1.py`)

### What It Does
1. Reads the 2-0 Researched JSON
2. For each vendor's sub-pillar rationale:
   - Merges score rationale, evidence quality, adjustment reason
   - Formats criteria assessment with ✅/⚠️/❌ icons
   - Includes top 3 evidence excerpts (150 char limit)
3. Computes vendor summary:
   - Coverage count + grade (A–F)
   - Quality average + grade (A–F)
   - Pillar averages (EXM, AMT, ADR, PPM)
4. Writes consolidated JSON

### Usage

```bash
python build_precyber_v2_1.py
```

### Output Fields Added

```json
{
  "sub_pillar_rationale_v2_consolidated": {
    "EXM-01": "EXM-01 – Attack Surface Management: Score 4.75/5.0 (Level 4). Confidence: high.\n\n[Score Rationale]\n..."
  },
  "vendor_summary_v2_1": {
    "coverage_count": 16,
    "coverage_grade": "A",
    "quality_avg": 0.67,
    "quality_grade": "B",
    "pillar_averages": { "EXM": 4.81, "AMT": 3.56, "ADR": 3.38, "PPM": 4.56 }
  },
  "v2_1_metadata": { "schema_version": "2.1", ... }
}
```

---

## Full Pipeline Run (Copy-Paste)

```bash
cd "c:\Users\zwest\OneDrive\Gartner Research"

# Stage 1: Evidence extraction (~10-15 min first run, ~5 min with cache)
python research_precyber_v1_evidence.py --batch-pause 2

# Stage 2: Rationale analysis (~3-5 min)
python research_precyber_v2_rationale.py --no-fetch

# Stage 3: Consolidation (~5 sec)
python build_precyber_v2_1.py
```

### Resume After Interruption

```bash
# Stage 1: Resume from last completed batch
python research_precyber_v1_evidence.py --resume --batch-pause 2

# If all batches exist but merge didn't complete:
python research_precyber_v1_evidence.py --merge-only

# Stage 2: Automatically resumes (checks existing output file for completed vendors)
python research_precyber_v2_rationale.py --no-fetch
```

### Clean Re-Run

```bash
# Delete batch checkpoints and outputs
Remove-Item "research\precyber_batches\batch_*.json" -Force
Remove-Item "research\precyber_checkpoints\precyber_evidence_progress.json" -Force
Remove-Item "Preemptive Cybersecurity Vendor 1-1 Validated.json" -Force
Remove-Item "Preemptive Cybersecurity Vendor 2-0 Researched.json" -Force
Remove-Item "Preemptive Cybersecurity Vendor 2-1 Consolidated.json" -Force

# Re-run full pipeline
python research_precyber_v1_evidence.py --batch-pause 2
python research_precyber_v2_rationale.py --no-fetch
python build_precyber_v2_1.py
```

---

## Known Issues & Vendor Gaps

### Fetch-Failed Vendors (3)
These vendors returned 0 pages during crawling:
- **Axonius** — All URLs failed to fetch
- **HashiCorp** — All URLs failed to fetch  
- **Group-IB** — All URLs failed to fetch

### No Evidence (1)
- **Trellix** — Pages fetched but no preemptive cybersecurity evidence found (all scores 0.00)

### Fix: Update vendor URLs in `VENDOR_URLS` dict in `research_precyber_v1_evidence.py` with working URLs, then re-run Stage 1.

---

## Scoring Calibration Notes

### v1 → v2 Score Flow
- v1 produces conservative scores based on exact phrase matching
- v2 enriches with criterion-by-criterion assessment and can adjust ±1.5
- Typical v2 behavior: ~44% scores increase, ~4% decrease, ~52% unchanged

### Expected Score Distribution (after pipeline)
- 0.xx: ~8% (fetch failures)
- 2.xx: ~17% (vendors outside their pillar specialty)
- 3.xx: ~45% (demonstrated capability)
- 4.xx: ~30% (advanced/strong vendors)
- 5.xx: 0% (market-leading requires analyst confirmation)

### Anti-Inflation Guards
1. **No word splitting** in criteria set construction (v1 + v2)
2. **Full phrase matching** for schema criteria (3+ char minimum to include acronyms)
3. **±1.5 cap** on v2 score adjustments
4. **0.5 threshold** — small differences don't trigger adjustment
5. **Specificity thresholds** calibrated to page-level term density

---

## File Structure

```
research/
  cache/
    pages_precyber/       # Cached HTML pages (SHA1 hash filenames)
  precyber_batches/       # Per-batch checkpoint files
    batch_01.json ... batch_11.json
  precyber_checkpoints/
    precyber_evidence_progress.json  # Progress tracker for resume
```

## Quality Check Scripts

```bash
# Score distribution analysis (works on any vendor JSON)
python _check_v1_quality.py "Preemptive Cybersecurity Vendor 2-1 Consolidated.json"

# Spot-check individual vendor sub-pillar scores
python _spot_check.py "Tenable"

# Inspect specific vendor + sub-pillar evidence excerpts
python _spot_excerpts.py "Tenable" "EXM-01"
```

---

## Adding New Vendors

1. Add vendor entry to `Preemptive Cybersecurity Vendor 1-0 Seed.json`
2. Add 5–6 curated URLs to `VENDOR_URLS` in `research_precyber_v1_evidence.py`
3. Re-run full pipeline (or use `--max-vendors` to test)

## Modifying Sub-Pillar Criteria

1. Edit `what_to_verify_publicly` and/or `search_terms` in `Preemptive_Cybersecurity_Schema.json`
2. Delete page cache if schema changes require different URL crawling
3. Re-run full pipeline from Stage 1
