# Buyer Voice Report Model

This package contains two separate datasets that should use the same Buyer Voice schema:

- `Corpora - Raw GEAR/GEAR - OpenAI - 07252026.csv`
- `Corpora - Raw GEAR/GEAR - ServiceNow Commercial Friction Set.csv`

The datasets are not vendor score files. They are Gartner end-user interaction corpora used to produce buyer-voice reports. Each report should preserve the raw GEAR record, use the NotebookLM formatter projection for analysis, and validate every output claim against source interactions.

## What The Formatter Does

`Script/gear_notebooklm_formatter_w_quarter.py` converts a raw GEAR CSV into quarter-split text files for NotebookLM.

It keeps only these fields:

| Raw GEAR column | Formatted report field |
|---|---|
| `First Response Date` | `Date` |
| `Reference Number` | `Reference Number` |
| `Account Region` | `Buyer Region` |
| `Enterprise Sector` | `Buyer Industry` |
| `Role Name` | `Buyer Role` |
| `Purpose` | `Purpose` |
| `Question Asked` | `Question Asked` |
| `Associate Name` | `Analyst Name` |
| `Discussion Summary` | `Discussion Summary` |

It also derives a calendar quarter from `First Response Date` and splits output files at roughly 450,000 words so NotebookLM can ingest them.

Implication for the app: the raw CSV remains canonical, but the report view should emphasize the formatter projection because that is the analytical unit used by the prompts.

## Dataset 1: OpenAI Buyer Voice

Source file: `GEAR - OpenAI - 07252026.csv`

Known shape:

- 3,555 interactions
- Date range: 2026-01-02 through 2026-07-23
- Quarter split: 2026 Q1 = 1,478; 2026 Q2 = 1,704; 2026 Q3 = 373
- Current package framing: OpenAI-anchored enterprise buyer conversations, all industries

Prompt goal:

Surface what enterprise buyers are asking about OpenAI and its products: where they are considering OpenAI, what they want to know, what worries them, how they compare OpenAI with alternatives, and what they report about using it.

Main report outputs:

1. Full-corpus discovery report
   - Bottom-up list of distinct buyer questions about OpenAI
   - Buyer-language phrasing
   - Qualitative prevalence: `Pervasive`, `Significant`, `Moderate`, `Niche`
   - Concentration by buyer role, industry, and region
   - 2-4 reference numbers per theme
   - Out-of-pattern and thin-signal observations

2. Theme consolidation report
   - Consolidated themes from discovered questions
   - Theme boundaries and awkward fits
   - Questions assigned to each theme
   - Qualitative prevalence based on the full corpus, not citation counts
   - Representative references spanning roles, sectors, and months

3. Market-cut reports
   - Enterprise AI Assistants
   - Enterprise AI Coding Agents
   - Each market cut needs an explicit qualifying record set
   - Spread is assessed against the qualifying subset, not the full OpenAI corpus
   - Filtering/anchoring audit should explain why records are included or excluded

4. Verification reports
   - Workforce coverage check
   - Market filtering audit
   - Direction-of-lean analysis for competitive comparisons

OpenAI-specific guardrails:

- Do not characterize other vendors' overall market standing from this corpus.
- Treat bare `GPT` as ambiguous unless the record supports OpenAI attribution.
- Preserve Azure OpenAI as both OpenAI technology and Microsoft commercial context.
- Exclude supply-side interactions where a technology vendor is asking for go-to-market or competitive intelligence.
- Do not state counts in slide-facing output.

## Dataset 2: ServiceNow Commercial Friction

Source file: `GEAR - ServiceNow Commercial Friction Set.csv`

Known shape:

- 4,114 interactions
- Date range: 2026-01-02 through 2026-07-30
- Quarter split: 2026 Q1 = 1,829; 2026 Q2 = 1,799; 2026 Q3 = 486
- Current package framing: ServiceNow commercial and economic friction, 1Q26 through July 2026

Prompt goal:

Report what enterprise buyers say about the commercial and economic dimensions of ServiceNow: pricing, packaging, licensing, renewal, contracting, business case, alternatives, value realization, and cost-offset tactics.

Main report outputs:

1. Bottom-up commercial discovery report
   - Everything buyers raise about cost, price, packaging, licensing, renewal, contracting, business case, economic justification, and alternatives
   - Buyer-language concern names
   - Roles and sectors represented
   - Quarter presence across Q1, Q2, and partial Q3
   - 2-4 reference numbers per concern

2. Supplied-category consolidation report
   - Uses five supplied categories only after discovery:
     - AI-Native Pricing and Packaging
     - Platform Displacement and Cost Alternatives
     - Renewal Cost and Contract Leverage
     - AI Business Case and ROI Proof Gap
     - Cost-Offset Tactics Using ServiceNow's Own Tools
   - Themes that do not fit belong in `Outside The Taxonomy`, not forced into a bucket
   - Prevalence is re-rated fresh at the consolidated theme level

3. ROI/value justification report
   - Separate pass for business case, value proof, adoption, and realization
   - Ignores pricing mechanics unless buyers raise them as part of justifying spend
   - Intended to recover signal missed by the first commercial framing

4. Validation reports
   - Claim support by theme
   - Figure provenance checks
   - Single-buyer versus multiple-buyer support
   - Buyer composition support by role, industry, region, and quarter

ServiceNow-specific guardrails:

- The five categories are naming buckets, not the search space.
- Flag negotiation tactics, leverage plays, and cost-avoidance approaches as `[SENSITIVITY REVIEW]`.
- Mark every numerical figure as `[SINGLE ACCOUNT]` or `[MULTIPLE ACCOUNTS]`.
- Treat July/3Q26 as partial and directional.
- Do not report raw counts in slide-facing output.

## Shared Report Contract

Every Buyer Voice report should include:

| Section | Purpose |
|---|---|
| Dataset summary | Source file, date range, quarter coverage, interaction count, scope |
| Scope and exclusions | What is in scope, what was excluded, and why |
| Discovery output | Bottom-up buyer questions or concerns |
| Theme output | Consolidated themes in buyer language |
| Rating output | Spread, trajectory where applicable, persistence where applicable |
| Buyer composition | Roles, industries/sectors, and regions represented |
| Evidence ledger | Reference numbers, source field, excerpt, and voice attribution |
| Validation findings | Unsupported claims, thin themes, redaction issues, attribution issues |

## Evidence Rules

- `Question Asked` is direct buyer voice.
- `Discussion Summary` must be used, but each statement from it needs attribution:
  - buyer-raised
  - analyst voice
  - attribution uncertain
- Analyst voice is not buyer voice.
- Every theme or rating must trace to multiple interactions unless labeled as an isolated observation.
- Every cited `Reference Number` must resolve to the source CSV.
- Buyer questions should remain verbatim or lightly paraphrased only to remove identifying detail.
- Client-identifying detail must be redacted before deliverable use.

## App Implication

The app should treat these files as two Buyer Voice datasets, not vendor datasets:

- `openai_2026_ytd`
- `servicenow_commercial_2026_ytd`

Both should use `Buyer_Voice_Schema_1_0.json`.

The first useful app report views should be:

1. Dataset Overview
2. Interaction Explorer
3. Discovery Themes
4. Theme Ratings
5. Evidence Ledger
6. Validation Findings

