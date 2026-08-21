# ServiceNow Buyer Voice: Prompts, Data Structure, and Analysis Opportunities

Updated: August 2026

This document separates the ServiceNow workstream from the OpenAI workstream. It focuses on what the ServiceNow GEAR export contains, what the NotebookLM prompts were trying to do, and what kinds of analysis are valid from this dataset.

## 1. What this dataset is

The ServiceNow dataset is a Gartner end-user inquiry corpus focused on ServiceNow commercial and economic friction.

| Attribute | Value |
|---|---|
| Source file | `buyervoice/Corpora - Raw GEAR/GEAR - ServiceNow Commercial Friction Set.csv` |
| Formatted files | `buyervoice/Corpora - Formatted/ServiceNow Commercial Mentions - 2026 Q*.txt` |
| Records | 4,114 |
| Date window | 2026-01-02 to 2026-07-30 |
| Primary vendor anchor | ServiceNow |
| Product/category context | Enterprise workflow platform, IT service management, workflow automation, licensing, renewal, pricing, AI packaging, commercial relationship |
| Primary analytical question | What commercial and economic friction are enterprise buyers raising about ServiceNow? |

This is not a general ServiceNow capability evaluation. It is not a customer satisfaction survey. It is a commercial-friction inquiry corpus: buyers are asking Gartner about licensing, renewal, pricing, packaging, negotiation, business case, and alternatives.

## 2. Raw data structure

The raw GEAR export contains the same major fields as the OpenAI export, but the analytical meaning differs because the pull is commercially framed.

| Field | Why it matters |
|---|---|
| `Reference Number` | Primary traceability key. Every theme, figure, or claim should resolve back to references. |
| `First Response Date` | Enables quarter analysis across 1Q26, 2Q26, and partial 3Q26. |
| `Account Region` | Buyer geography lens. |
| `Enterprise Sector` | Buyer industry/organization-type lens. |
| `Role Name` | Buyer role/function lens. |
| `Persona` | Gartner persona segmentation. |
| `Account Market` / `Enterprise Market` | Helps distinguish end-user, investor, tech-provider, and professional-services contexts. |
| `Purpose` | Especially useful for identifying proposal review, renewal, licensing, and negotiation records. |
| `Question Asked` | Cleanest buyer-voice field. |
| `Discussion Summary` | Rich commercial detail, but must be attributed carefully. |
| `Vendor Name` / `Vendor Enterprise` | More populated than OpenAI, but still not complete enough to be the only anchor. |
| `Core Topic` | Useful where present; often blank. |
| `Buysmart` | Buying-stage signal, especially selected-vendor negotiation. |

The formatted NotebookLM files keep:

- Date
- Reference Number
- Buyer Region
- Buyer Industry
- Buyer Role
- Purpose
- Question Asked
- Analyst Name
- Discussion Summary

## 3. What the ServiceNow data tells us structurally

### Geographic distribution

| Account Region | Records |
|---|---:|
| NORTHAM | 2,464 |
| EMEA | 1,234 |
| ASIAPAC | 308 |
| LATINAM | 70 |
| JAPAN | 38 |

The corpus is strongly North America and EMEA weighted. That is useful for broad enterprise-commercial analysis, but regional claims outside those two regions should be handled carefully.

### Sector distribution

| Enterprise Sector | Records |
|---|---:|
| Banking, Finance and Insurance | 885 |
| Government | 876 |
| Manufacturing | 795 |
| Healthcare | 492 |
| Services | 340 |
| Energy and Utilities | 284 |
| Retail | 184 |
| Education | 133 |
| Transportation | 100 |
| Media | 22 |

The strongest sector coverage is financial services, government, manufacturing, healthcare, and services. This supports analysis of broad commercial friction, but sub-sector-specific claims need evidence.

### Account market / organization type

| Account Market | Records |
|---|---:|
| End User | 3,789 |
| Tech Services Providers | 212 |
| Investors | 85 |
| Professional Services | 28 |

Most records are end-user inquiries. Investor and technology-provider records still exist and need filtering when the output is meant to represent buyer commercial experience.

### Role distribution

Top roles include:

- CIO or Head of Technology
- IT/Infrastructure and Operations roles
- IT - Other Role
- Divisional Technology Leader
- Enterprise Architecture
- Head of Infrastructure and/or IT Operations
- Enterprise Architect
- Program and Portfolio Management
- IT Sourcing / Procurement / Vendor Management
- IT/Cyber Security and Risk Management

This supports analysis of commercial friction across IT leadership, architecture, sourcing/procurement, infrastructure/operations, and program leadership.

### Interaction type

| Interaction Subtype | Records |
|---|---:|
| Inquiry | 3,097 |
| Document Review | 450 |
| Proposal Review | 436 |
| Sample Inquiry | 84 |
| Planning Call | 26 |

Compared with OpenAI, ServiceNow has many more proposal/document-review records. That is important: the dataset is especially strong for renewal, licensing, negotiation, and commercial-terms analysis.

### Buying-stage signal

| Buysmart | Records |
|---|---:|
| `-` | 3,433 |
| Stage C: Selected Vendor Negotiation | 439 |
| Stage A: Understanding Needs & Potential Solutions | 158 |
| Stage B: Vendor Selection | 84 |

ServiceNow has a meaningful selected-vendor negotiation subset. This is directly relevant to commercial-friction and renewal analysis.

### Vendor fields

ServiceNow appears more often in structured vendor fields than OpenAI:

- `Vendor Name = ServiceNow` appears in 920 records.
- `Vendor Enterprise = ServiceNow, Inc.` appears in 926 records.

But more than half of records still have blank vendor fields, so analysis still needs `Purpose`, `Question Asked`, and `Discussion Summary`.

## 4. Prompt Part 2: what the ServiceNow prompts are trying to achieve

The ServiceNow prompts define a buyer-voice analysis of commercial and economic friction around ServiceNow.

The persistent prompt’s core instruction is:

- analyze Gartner end-user interaction data;
- report what buyers say about ServiceNow’s commercial and economic dimensions;
- begin with open discovery;
- use supplied categories only after discovery;
- separate buyer voice from analyst voice;
- cite reference numbers;
- use qualitative prevalence only;
- mark figures with provenance;
- flag sensitive negotiation or cost-avoidance tactics.

## 5. Key ServiceNow prompt principles

### 1. Search unconstrained before naming anything

The prompt is explicit: the five categories are not the search space.

The analysis must first discover what buyers raise about:

- cost;
- pricing;
- packaging;
- licensing;
- renewal;
- contracting;
- business case;
- economic justification;
- alternatives.

Only after discovery should themes be organized into categories.

### 2. Supplied categories are naming buckets

The five supplied categories are:

1. AI-Native Pricing and Packaging
2. Platform Displacement and Cost Alternatives
3. Renewal Cost and Contract Leverage
4. AI Business Case and ROI Proof Gap
5. Cost-Offset Tactics Using ServiceNow's Own Tools

The prompt specifically warns against:

- searching only for bucket labels;
- discarding real concerns because they do not fit a bucket;
- forcing concerns into the nearest bucket;
- reporting the taxonomy back with examples attached.

### 3. Figures require provenance

Every percentage, dollar amount, price range, per-seat cost, uplift, or other figure must be marked:

- `[SINGLE ACCOUNT]`
- `[MULTIPLE ACCOUNTS]`

This is a key difference from OpenAI. ServiceNow commercial-friction work is much more likely to include pricing figures, renewal uplift, unit costs, or contract benchmarks.

### 4. Sensitivity review is part of the output

Where buyer content describes negotiation leverage, cost-avoidance, or audit-risk tactics, the prompt says to flag it inline as `[SENSITIVITY REVIEW]`.

This does not mean the finding should be discarded. It means it should be routed before external use.

### 5. Correction and validation passes are part of the method

The prompt pack includes correction examples where earlier output incorrectly:

- allowed market statistics to pass as buyer voice;
- included analyst statements inside buyer-voice themes;
- cited no discovery item for a merge;
- attributed a figure to the wrong vendor;
- treated single-interaction observations as themes.

This is important: the ServiceNow workflow expects iterative validation.

## 6. What analysis we can do from the ServiceNow dataset

### A. Commercial-friction discovery

Objective: identify everything buyers raise about the commercial/economic experience of ServiceNow.

Likely concern families:

- renewal price increases;
- contract leverage;
- discounting;
- locked spend and true-down limitations;
- SKU complexity;
- AI tier migration;
- token/credit consumption exposure;
- opaque pricing;
- benchmarking difficulty;
- business case and ROI proof;
- alternative platform evaluation;
- cost-offset tactics;
- audit exposure;
- implementation and services cost;
- support/package pressure.

### B. Supplied-category consolidation

Objective: organize discovered concerns into the five supplied categories after discovery.

Valid output:

- category;
- buyer-language theme;
- what buyers are actually saying;
- spread;
- trajectory;
- buyer composition;
- 2-4 reference numbers;
- merged discovery items;
- outside-taxonomy items.

### C. Renewal and negotiation analysis

ServiceNow has strong proposal-review and selected-vendor-negotiation signal.

This supports analysis of:

- renewal strategy;
- early renewal leverage;
- discounting;
- price uplift;
- benchmarking;
- contract lock-in;
- true-down constraints;
- unit-price opacity;
- negotiation tactics.

### D. AI-native pricing and packaging analysis

The data supports analysis of ServiceNow’s transition toward AI-embedded packaging and consumption models.

Questions this can answer:

- How are buyers reacting to AI-first subscription models?
- What are buyers asking about Pro Plus, Enterprise Plus, Now Assist, Prime, Advanced, or similar tiers?
- How do buyers understand token/credit or assist consumption?
- What budget uncertainty does consumption introduce?
- How do buyers manage migration from older modular pricing?

### E. ROI and business-case analysis

The prompt pack includes a dedicated ROI/value pass because one category initially came back thin.

This supports analysis of:

- what finance/executives require before approving ServiceNow spend;
- which metrics buyers use or reject;
- whether expected benefits are visible;
- underused capability already paid for;
- whether AI spend faces a different business-case burden;
- whether ServiceNow value is hard to prove because of adoption, process, or data foundation issues.

### F. Cost-offset and sensitivity analysis

The data can support internal analysis of buyer tactics, but this area requires careful handling.

Potential topics:

- license optimization;
- fulfiller versus stakeholder licensing;
- configuration workarounds;
- custom fields/tables;
- audit exposure;
- avoiding module expansion;
- using platform configuration to reduce spend.

This should not be turned into client-facing advice without review.

### G. Buyer composition analysis

Because the export includes region, sector, role, market, persona, and buying-stage markers, each theme can be profiled by:

- roles raising the concern;
- sectors represented;
- regions represented;
- whether the concern is broad or concentrated;
- whether it appears in negotiation-stage records;
- whether it appears consistently across quarters.

## 7. What the ServiceNow dataset should not be used for

The ServiceNow dataset should not be used to:

- evaluate ServiceNow product capability overall;
- measure customer satisfaction;
- generalize pricing figures without provenance;
- convert buyer tactics into Gartner recommendations;
- treat analyst-discovered contract issues as buyer voice;
- use supplied categories as the search space;
- ignore outside-taxonomy concerns;
- report July/3Q26 as a full-quarter trend;
- publish sensitive cost-offset tactics without review.

## 8. Analytical output model for ServiceNow

The ServiceNow output should be a separate deliverable with these report sections:

1. Dataset overview
2. Pull/query interpretation
3. Commercial-friction discovery
4. Supplied-category consolidation
5. Outside-taxonomy findings
6. Spread and trajectory ratings
7. Buyer composition by role, region, sector, market, and buying stage
8. Figure provenance table
9. Sensitivity review table
10. Evidence ledger by theme
11. Validation findings
12. Slide-facing output draft

## 9. What the schema should represent for ServiceNow

The schema should start from the data and analysis objects, not from generic vendor scoring.

Recommended schema direction: create a dedicated schema named `ServiceNow Buyer Data Analysis`.

This should be a buyer-perspective commercial-friction inquiry analysis schema. It should be closer in spirit to an ASAF-style framework/report structure than to a vendor-list scoring file. ServiceNow is the organization being analyzed, but the analytical unit is not a vendor row. The analytical units are inquiry records, buyer concerns, commercial-friction themes, supplied categories, figures, evidence, sensitivity flags, validation findings, and slide/report outputs.

The schema can share a common Buyer Voice data model with OpenAI, but it should allow ServiceNow-specific dimensions and report sections:

- commercial-friction discovery;
- supplied-category consolidation;
- outside-taxonomy themes;
- renewal and negotiation themes;
- AI-native pricing/package themes;
- ROI/business-case themes;
- cost-offset tactics;
- figure provenance;
- sensitivity review.

The existing vendor-score structure should not be the primary model. It can be reused only if the app needs a temporary compatibility layer for selecting an organization, but the long-term model should be `schema -> dataset -> inquiry/theme/report`, not `schema -> vendor list -> vendor scorecard`.

Core entities should include:

- `dataset`
- `gear_query_or_pull`
- `interaction`
- `buyer_profile`
- `vendor_anchor`
- `commercial_scope`
- `discovery_item`
- `supplied_category`
- `theme`
- `outside_taxonomy_theme`
- `theme_rating`
- `trajectory_rating`
- `figure_claim`
- `figure_provenance`
- `sensitivity_flag`
- `evidence_reference`
- `excerpt`
- `voice_attribution`
- `validation_finding`
- `slide_output`

For ServiceNow, the schema needs to support a vendor relationship/commercial-friction outcome with supplied categories, outside-taxonomy findings, figure provenance, and sensitivity review.

## 10. Schema and report architecture options

### Option A: use the existing vendor-data rails as a compatibility layer

This would treat ServiceNow as a single selectable entity in the existing app rails.

Pros:

- Fastest to wire into the current app.
- Reuses existing schema picker, analysis tab, and report tab behavior.
- Keeps a simple way to select ServiceNow as the active organization.

Cons:

- Misleading mental model: this is not a vendor capability scorecard.
- Commercial-friction themes, figure provenance, and sensitivity review do not fit cleanly into vendor score fields.
- Makes it too easy to compare ServiceNow with OpenAI even though the datasets answer different questions.

Use only as a bridge if needed.

### Option B: create a dedicated ASAF-like inquiry-analysis schema

This would model ServiceNow as its own buyer data analysis framework/report workspace.

Pros:

- Better aligned with the data.
- Supports tabs like Dataset, Query/Pull, Discovery, Categories, Outside Taxonomy, ROI Pass, Evidence, Figure Provenance, Sensitivity Review, Validation, and Slide Output.
- Avoids fake vendor scoring.
- Keeps ServiceNow and OpenAI separate while sharing the same underlying Buyer Voice object model.

Cons:

- Requires app work to create or adapt non-vendor report rails.
- Existing dashboards that expect `vendors[]` will not apply without a compatibility adapter.

Recommended direction: Option B.

## 11. Immediate next work

1. Stop treating the current Buyer Voice schema/vendor-score files as authoritative; mark them as exploratory/temporary.
2. Define a new `ServiceNow Buyer Data Analysis` schema around inquiry-analysis objects, not vendor rows.
3. Extract the ServiceNow prompt section into a clean prompt archive.
4. Document the likely GEAR query/pull interpretation: ServiceNow commercial-friction inquiry records across 1Q26 through July 2026.
5. Build a dataset profile from raw GEAR fields: region, sector, role, persona, account market, interaction subtype, buying stage, purpose, vendor fields, and date windows.
6. Generate bottom-up commercial-friction discovery items.
7. Consolidate into the five supplied categories after discovery.
8. Preserve outside-taxonomy findings.
9. Run the ROI/business-case pass separately.
10. Generate figure provenance tags.
11. Generate sensitivity flags.
12. Generate evidence ledgers with 2-4 reference examples per theme.
13. Design tabbed reports for:
    - Dataset Overview
    - Query/Pull Interpretation
    - Commercial-Friction Discovery
    - Supplied Categories
    - Outside Taxonomy
    - ROI / Business Case
    - Figure Provenance
    - Sensitivity Review
    - Evidence Ledger
    - Validation Findings
    - Slide Output
14. Rebuild the app integration around this schema/report model after the data model is agreed.
