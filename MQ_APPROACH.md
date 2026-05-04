# Magic Quadrant Construction — Reusable Approach

## Overview

This document defines the repeatable methodology for constructing a Magic Quadrant analysis from any existing vendor schema in this platform. The approach is modular: it maximizes reuse of scored vendor data already in the system and surgically fills gaps with a supplemental "MQ Gap" schema.

---

## Step 1: Map Existing Schema to MQ Criteria

For each of the 15 MQ criteria (7 Ability-to-Execute, 8 Completeness-of-Vision), identify which existing schema fields provide coverage.

**Coverage levels:**
- **≥60% Covered** → Use existing data directly; no gap research needed
- **30–59% Covered** → Combine existing data with targeted gap research
- **<30% Covered** → Requires full gap research

**For MDR, the mapping yielded:**
| Coverage Level | Criteria |
|---|---|
| ≥60% | ATE-1 Products (85%), ATE-7 Operations (60%), COV-7 Innovation (70%) |
| 30–59% | ATE-3 Pricing (50%), ATE-6 CX (55%), COV-4 Offering (50%), COV-5 Business Model (50%) |
| <30% | ATE-2 Viability (25%), ATE-4 Responsiveness (20%), ATE-5 Marketing (30%), COV-1 Market Understanding (25%), COV-2 Marketing Strategy (25%), COV-3 Sales Strategy (20%), COV-6 Vertical (15%), COV-8 Geographic (10%) |

## Step 2: Build the MQ Gap Schema

Create a supplemental schema that covers **only** the gap criteria identified in Step 1. Structure as pillars → sub-pillars using the same 0–5 scoring scale.

**Design rules:**
1. Each gap pillar maps to 1–3 MQ criteria (keep the mapping explicit in the schema)
2. Use 3–4 sub-pillars per pillar (enough depth without over-engineering)
3. Include scoring guidance per level so any researcher produces consistent scores
4. Include evidence source lists so research is directed and reproducible
5. Don't duplicate what the existing schema already scores — reference it in formulas instead

**For MDR, the gap schema has 7 pillars / 28 sub-pillars:**
- VIA (Financial Viability) → ATE-2
- SLE (Sales Execution & Channel) → ATE-3 + COV-3
- MKR (Market Responsiveness) → ATE-4
- MKE (Marketing & Brand) → ATE-5 + COV-2
- CXQ (Customer Experience Quality) → ATE-6 supplement
- MKU (Market Understanding & Vision) → COV-1 + COV-4 + COV-5
- VIG (Vertical & Geographic) → COV-6 + COV-8

## Step 3: Define the MQ Scoring Mode

Each MQ criterion gets a formula combining:
- **Existing schema scores** (pillar_scores, sub-pillar scores, pricing scores)
- **Gap schema scores** (pillar averages or weighted sub-pillars)

Formulas produce a 0–5 score per criterion. The 7 ATE criteria are weighted to produce a composite ATE score (Y-axis), and the 8 COV criteria produce a composite COV score (X-axis).

**Weighting rules (from Gartner methodology):**
- **High weight** = 0.16–0.20 of axis total
- **Medium weight** = 0.10–0.14 of axis total
- **Low weight** = 0.06–0.08 of axis total
- All weights on each axis must sum to 1.0

## Step 4: Seed the MQ Gap Vendor Data

Create a seed file with all vendors from the main schema. Pre-populate any fields derivable from existing data:
- `funding_stage` → informs VIA-02 (profitability proxy)
- `employee_count_range` → informs VIA-01 (revenue proxy) and SLE/VIG sizing
- `year_founded` → informs MKR track record
- `region` / `headquarters` → informs VIG-03/04
- `target_market` → informs VIG-01/02

**File naming:** `{Schema} Vendor MQ Gap 1-0 Seed.json`

## Step 5: Research & Score Gap Data

For each vendor, research the gap sub-pillars using the evidence sources listed in the schema. Score 0–5 with rationale text.

**Research approach (tiered by vendor importance):**
1. **Tier 1 — Top 20 vendors** (by existing overall_score): Full deep research on all 28 sub-pillars
2. **Tier 2 — Mid 40 vendors**: Standard research with emphasis on VIA and MKR (highest-weight gaps)
3. **Tier 3 — Bottom 40 vendors**: Efficient research using primarily public web presence and review platforms

**Per-sub-pillar research output:**
```json
{
  "score": 3,
  "rationale": "Brief evidence-based justification",
  "evidence_sources": ["url1", "url2"],
  "confidence": "high|medium|low"
}
```

## Step 6: Compute MQ Positions

Run the scoring formulas to produce per-vendor:
- 15 individual MQ criterion scores (0–5)
- Composite ATE score (weighted sum, 0–5)
- Composite COV score (weighted sum, 0–5)
- Quadrant placement (Leaders/Challengers/Visionaries/Niche Players)

**Quadrant boundaries:** Set at the population median of each axis. This ensures the quadrant is calibrated to the specific vendor set rather than absolute thresholds.

## Step 7: Build the Report Tab

Add an interactive MQ visualization to the frontend:
- Scatter plot with COV (X) and ATE (Y) axes
- Vendor dots with labels, colored by quadrant
- Click-through to vendor detail showing all 15 criterion scores
- Export as Markdown table

---

## Applying to Other Schemas

To build an MQ for any schema (DFIR, PreCyber, TRiSM, etc.):

1. Run Step 1 mapping against that schema's pillars/sub-pillars
2. Many gap pillars will be **identical** across schemas (VIA, SLE, MKR, MKE are vendor-level, not domain-specific)
3. Only CXQ and MKU may need schema-specific adjustments (different product focus)
4. VIG is fully reusable as-is
5. If a vendor appears in multiple schemas, gap research carries over — research once, reuse everywhere

**Shared pillars across all schemas:** VIA, SLE, MKR, MKE, VIG (5 of 7 = 71% reuse)
**Schema-specific pillars:** CXQ (peer reviews differ by domain), MKU (roadmap/vision is domain-specific)

---

## File Inventory

| File | Purpose |
|---|---|
| `MQ_Gap_Schema_1_0.json` | Gap schema definition with scoring guidance |
| `{Schema} Vendor MQ Gap 1-0 Seed.json` | Vendor seed data with pre-populated fields |
| `{Schema} Vendor MQ Gap 2-0 Researched.json` | Vendor data after gap research |
| `build_mq_gap_seed.py` | Script to generate seed from existing vendor data |
| `build_mq_scores.py` | Script to compute MQ criteria from combined data |
| `MQ_APPROACH.md` | This document |
