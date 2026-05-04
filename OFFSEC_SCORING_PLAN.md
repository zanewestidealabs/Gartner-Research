# Offensive Security Vendor Scoring — Gap Remediation Plan

**Created:** 2026-03-18  
**Status:** Ready for execution  
**Scope:** 45 vendors · 25 sub-pillars · 1,125 scoring cells  

---

## Current State Assessment

| Metric | Value |
|--------|-------|
| Total cells scored (≥1) | **815 / 1,125** (72.4%) |
| Total cells at zero | **310 / 1,125** (27.6%) |
| Evidence rationales populated | **815** (all scored cells have text) |
| Source citations populated | **0** (every `sources[]` array is empty) |
| Average rationale length | 1–3 sentences |

### Scoring Coverage by Pillar

| Pillar | Scored | Zero | % Covered | Sparsest Sub-pillar |
|--------|--------|------|-----------|---------------------|
| **ASM** | 165 | 60 | 73% | ASM-04 Shadow IT (~50%) |
| **VUL** | 175 | 50 | 78% | VUL-04 Exploitability (~40%) |
| **OFT** | 110 | 115 | **49%** | OFT-04 Attack Paths (18%) |
| **APP** | 95 | 130 | **42%** | APP-03 SCA (31%) |
| **REM** | 140 | 85 | 62% | REM-04 Closed-loop (27%) |

### Three Critical Gaps

1. **Empty source citations** — Schema requires `sources[]` with Tier A/B/C URLs; all 815 evidence entries have `[]`
2. **Thin rationales** — Many scored entries are single-sentence assertions lacking specifics (product names, metrics, analyst recognition)
3. **Legitimate vs. addressable zeros** — Of 310 zero-score cells, ~200 are legitimate (vendor doesn't compete there) and ~110 could potentially be scored at 1–2 if latent capabilities are researched

---

## Execution Plan

### Phase 1: Deepen Existing Rationales (Priority: HIGH)

**Goal:** Upgrade all 815 existing rationale entries from assertion-quality to evidence-quality.

Each rationale should include:
- Named product/feature (e.g., "Falcon Surface" not "CrowdStrike EASM")
- Quantifiable claim where possible (e.g., "200,000+ plugins", "30,000+ attack scenarios")
- Analyst recognition (e.g., "Gartner MQ Leader 2025", "Forrester Wave Leader Q3 2024")
- Competitive context (e.g., "one of three market leaders alongside X and Y")

**Batches (5 vendors each, prioritized by market impact):**

| Batch | Vendors | Focus |
|-------|---------|-------|
| P1-1 | Tenable, Qualys, Rapid7, CrowdStrike, Palo Alto Networks | Tier 1 — deepest rationale enrichment |
| P1-2 | Wiz, Pentera, XM Cyber, Microsoft, Google/Mandiant | Tier 1 — platform leaders |
| P1-3 | Snyk, Checkmarx, Veracode, SafeBreach, AttackIQ | AppSec + BAS leaders |
| P1-4 | Cymulate, Horizon3.ai, Tanium, Censys, Recorded Future | Specialists |
| P1-5 | Synopsys, SonarSource, Semgrep, Invicti, Contrast Security | AppSec depth |
| P1-6 | HackerOne, Bugcrowd, Hadrian, Detectify, Vulcan Cyber | Crowd + ASM |
| P1-7 | Nucleus, Brinqa, PlexTrac, GitLab, Cobalt | Orchestration + DevSecOps |
| P1-8 | Securin, FireCompass, Indusface, CloudSEK, SecPod | APAC + niche |
| P1-9 | Astra Security, NSFOCUS, NTT Security Holdings, Entersoft Security | APAC remaining |

**Deliverable:** Updated rationales in `sub_pillar_evidence[*].rationale`

---

### Phase 2: Populate Source Citations (Priority: HIGH)

**Goal:** Add 2–4 verifiable source citations per scored sub-pillar.

**Source Tier Requirements (from schema):**

| Tier | Type | Weight | Example |
|------|------|--------|---------|
| A | Vendor documentation | 1.0 | Product pages, datasheets, whitepapers |
| A | Analyst reports | 1.0 | Gartner MQ/Market Guide, Forrester Wave |
| B | Technical media | 0.85 | SC Magazine, Dark Reading, CSO Online |
| B | Benchmarks/Case studies | 0.85 | Customer testimonials, MITRE Engenuity |
| C | Conference/Academic | 0.7 | RSA, Black Hat, DEF CON presentations |
| C | Professional networks | 0.7 | LinkedIn thought leadership, GitHub repos |

**Target per evidence entry:**
```json
"sources": [
  {"type": "Vendor documentation", "tier": "A", "url": "https://...", "title": "..."},
  {"type": "Analyst reports", "tier": "A", "url": "https://...", "title": "..."}
]
```

**Execution:** Same 9-batch structure as Phase 1. Can be combined with rationale deepening to reduce passes.

---

### Phase 3: Fill Addressable Zero-Score Gaps (Priority: MEDIUM)

**Goal:** Research the ~110 addressable zero-score cells where vendors may have latent or emerging capabilities.

**Priority sub-pillars to investigate (most actionable gaps):**

| Sub-pillar | Current 0-scores | Likely addressable | Rationale |
|------------|-------------------|--------------------|-----------|
| ASM-04 (Shadow IT) | ~22 vendors | 8–10 | Many VM/cloud platforms have some shadow asset detection |
| VUL-04 (Exploitability) | ~27 vendors | 5–8 | Some vendors use EPSS/exploit intelligence as proxy validation |
| OFT-04 (Attack Paths) | ~37 vendors | 3–5 | Only applicable to vendors with graph/modeling capability |
| APP-02 (API Security) | ~25 vendors | 6–8 | Many DAST tools support API scanning |
| REM-04 (Closed-loop) | ~33 vendors | 8–10 | Many CI/CD and VM tools support re-scan verification |
| REM-01 (Auto Remediation) | ~30 vendors | 5–7 | WAF virtual patching, SOAR playbooks count |

**Approach:** Per batch, review each vendor's full product portfolio for capabilities not captured in the initial scoring. Score at 1–2 (Minimal/Generic) if capability exists but isn't a market focus. Leave at 0 if truly absent.

**Batches:** Same 9-batch structure. For each vendor, check:
1. Recent product announcements (2024–2026)
2. New acquisitions that add capabilities
3. Partner/integration-based capabilities (score at 1–2, not 3+)

---

### Phase 4: Score Calibration & Cross-Vendor Consistency (Priority: MEDIUM)

**Goal:** Ensure scores are calibrated consistently across vendors.

**Calibration rules:**
- A score of 5 should be reserved for ≤3 vendors per sub-pillar (true market leaders)
- A score of 4 requires named analyst recognition or documented market differentiation
- A score of 3 requires named products with documented capabilities
- Scores of 1–2 indicate capability exists but is not a market focus
- Score of 0 means no evidence of capability

**Checks to run:**
1. **5-score audit:** List all sub-pillars where >3 vendors score 5. Review and potentially downgrade.
2. **Cross-vendor comparison:** For each sub-pillar, rank all vendors and verify relative ordering makes market sense.
3. **Pillar balance:** Verify that pillar averages (mean of non-zero sub-scores) are reasonable — no vendor should average 5.0 or below 2.0 in active pillars.

---

### Phase 5: Output & Validation (Priority: HIGH)

**Goal:** Produce validated `Offensive Security Vendor 2-1 Consolidated.json`

**Validation checks:**
1. Every scored cell (≥1) has a rationale of ≥2 sentences
2. Every scored cell has ≥2 source citations with URLs
3. No vendor has scores outside their `capability_coverage` at 3+ (coverage must be updated if score added)
4. Pillar averages recalculated correctly
5. Score-5 audit: max 3 per sub-pillar
6. Schema compliance: all fields match `Offensive_Security_Schema.json` structure

**Output files:**
- `Offensive Security Vendor 2-1 Consolidated.json` — Final scored + sourced file
- Deploy to production via `deploy.bat`

---

## Execution Summary

| Phase | Work Items | Est. Batches |
|-------|-----------|--------------|
| 1. Deepen rationales | 815 entries | 9 batches of 5 vendors |
| 2. Populate sources | 815 entries × 2–4 sources | Combined with Phase 1 |
| 3. Fill zero-score gaps | ~110 cells | 9 batches (same vendors) |
| 4. Score calibration | Cross-vendor review | 5 pillar reviews |
| 5. Output & validation | Build + deploy | 1 validation pass |

**Recommended approach:** Combine Phases 1–3 into a single pass per batch. For each vendor, simultaneously:
- Enrich existing rationales with specifics
- Add source citations (URLs)
- Check for addressable zero-score gaps
- Output updated vendor data

This 3-in-1 approach requires **9 batches** total rather than 27 separate passes.

---

## Decision Points for User

1. **Source citation depth:** Should we target 2 sources per entry (faster) or 4 sources (higher quality)?
2. **Zero-score policy:** Should we leave legitimate zeros as-is, or add explicit "N/A — not in vendor's market" rationale?
3. **Output file naming:** `2-1 Consolidated` follows existing convention — confirm?
4. **Phase 4 calibration:** Should 5-scores be limited to top 3 vendors per sub-pillar, or is the current distribution acceptable?
5. **Execution cadence:** All 9 batches in one session, or review/approve after each batch?
