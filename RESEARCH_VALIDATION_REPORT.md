# Research Validation Report
This report compares deterministic normalization scores (Vendor 4-0 Validated) to evidence-harvested heuristic scores (Vendor 4-1 Researched).
## Coverage
- Vendors in researched file: **139**
- Vendors with at least one captured excerpt: **96**

## Flags
- `good_evidence`: 96
- `no_evidence`: 30
- `fetch_failed`: 13

## Confidence
- Avg confidence: **0.57**
- Min/Max confidence: **0.00** / **0.80**

## Validation rule
- Enforced rule: if `research_flag` is not `good_evidence`, then `sub_pillar_scores_researched[SID] <= 3.0` for all 20 sub-pillars.
- Vendors violating the rule (should be 0): **0**
- Sub-pillar scores above 3.0 under non-good-evidence vendors (should be 0): **0**

## Researched score distribution (all sub-pillars)
- 0.25: 937 (33.7%)
- 0.75: 96 (3.5%)
- 1.25: 6 (0.2%)
- 1.75: 11 (0.4%)
- 2.25: 897 (32.3%)
- 2.75: 399 (14.4%)
- 3.25: 241 (8.7%)
- 3.75: 178 (6.4%)
- 4.50: 15 (0.5%)

## Largest changes (|validated - researched| >= 1.0)
- **mnemonic** LAW-01: Δ 4.75
- **mnemonic** INV-04: Δ 4.75
- **mnemonic** INV-03: Δ 4.75
- **Zscaler** INV-04: Δ 4.75
- **Wolfpack InfoRisk** PLA-03: Δ 4.75
- **Wolfpack InfoRisk** LAW-02: Δ 4.75
- **Trustwave** LAW-02: Δ 4.75
- **TrustedSEC** LAW-02: Δ 4.75
- **TrustedSEC** INV-02: Δ 4.75
- **Total Assure** REM-04: Δ 4.75
- **Total Assure** REM-01: Δ 4.75
- **Total Assure** PMG-01: Δ 4.75
- **Total Assure** PLA-04: Δ 4.75
- **Total Assure** PLA-02: Δ 4.75
- **Total Assure** PLA-01: Δ 4.75
- **Total Assure** INV-04: Δ 4.75
- **Tenzai** PLA-03: Δ 4.75
- **Tenzai** PLA-01: Δ 4.75
- **Tenzai** INV-04: Δ 4.75
- **Tenzai** INV-03: Δ 4.75
- **Tenzai** INV-02: Δ 4.75
- **Tenzai** INV-01: Δ 4.75
- **Sygnia** REM-03: Δ 4.75
- **Sygnia** PMG-04: Δ 4.75
- **Sygnia** PLA-03: Δ 4.75
- **Sygnia** LAW-02: Δ 4.75
- **Sweet Security** INV-04: Δ 4.75
- **Sweet Security** INV-01: Δ 4.75
- **Stellar Cyber** REM-03: Δ 4.75
- **Stellar Cyber** REM-01: Δ 4.75
- **Stellar Cyber** INV-03: Δ 4.75
- **Stellar Cyber** INV-02: Δ 4.75
- **S-RM** LAW-02: Δ 4.75
- **S-RM** LAW-01: Δ 4.75
- **S-RM** INV-03: Δ 4.75
- **Rubrik** REM-04: Δ 4.75
- **Rubrik** REM-03: Δ 4.75
- **Rubrik** REM-02: Δ 4.75
- **Rubrik** PLA-04: Δ 4.75
- **ReliaQuest** INV-03: Δ 4.75
- **Quorum Cyber** REM-01: Δ 4.75
- **Quorum Cyber** PLA-02: Δ 4.75
- **Quorum Cyber** PLA-01: Δ 4.75
- **Quorum Cyber** INV-03: Δ 4.75
- **PwC** PMG-03: Δ 4.75
- **PwC** PLA-01: Δ 4.75
- **PwC** LAW-02: Δ 4.75
- **Palo Alto Unit 42** REM-03: Δ 4.75
- **P0 Security** REM-04: Δ 4.75
- **P0 Security** REM-02: Δ 4.75

## Notes
- The researched scores are **heuristic suggestions** derived from publicly fetchable web text and schema keyword matching.
- The `sub_pillar_evidence` excerpts are intended as the *substance/justification* for each score, but they still require analyst review for final scoring.
