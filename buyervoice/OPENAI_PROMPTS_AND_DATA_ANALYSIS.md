# OpenAI Buyer Voice: Prompts, Data Structure, and Analysis Opportunities

Updated: August 2026

This document separates the OpenAI workstream from the ServiceNow workstream. It focuses on what the OpenAI GEAR export contains, what the NotebookLM prompts were trying to do, and what kinds of analysis are valid from this dataset.

## 1. What this dataset is

The OpenAI dataset is a Gartner end-user inquiry corpus anchored on OpenAI and OpenAI-related product mentions.

| Attribute | Value |
|---|---|
| Source file | `buyervoice/Corpora - Raw GEAR/GEAR - OpenAI - 07252026.csv` |
| Formatted files | `buyervoice/Corpora - Formatted/OpenAI Mentions - 2026 Q*.txt` |
| Records | 3,555 |
| Date window | 2026-01-02 to 2026-07-23 |
| Primary vendor anchor | OpenAI |
| Product/category context | Generative AI platforms, enterprise AI assistants, AI coding agents, AI governance, AI adoption, AI commercial terms |
| Primary analytical question | What are enterprise buyers asking Gartner about OpenAI, and how do those questions change when viewed through specific AI markets? |

This is not a consumer sentiment dataset. It is not a product review dataset. It is an inquiry-question dataset: buyers came to Gartner with questions, problems, comparisons, decisions, and negotiation needs.

## 2. Raw data structure

The raw GEAR export contains a broad record of each interaction. The important analytical fields are:

| Field | Why it matters |
|---|---|
| `Reference Number` | Primary traceability key. Every claim or theme should resolve back to references. |
| `First Response Date` | Enables quarter/month analysis and July partial-period treatment. |
| `Account Region` | Buyer geography lens. |
| `Enterprise Sector` | Buyer industry/organization-type lens. |
| `Role Name` | Buyer role/function lens. |
| `Persona` | Gartner persona segmentation. |
| `Account Market` / `Enterprise Market` | Helps distinguish end-user, investor, tech-provider, and professional-services contexts. |
| `Purpose` | Often gives the clearest shorthand for the inquiry objective. |
| `Question Asked` | Cleanest buyer-voice field. This is the buyer’s explicit framing. |
| `Discussion Summary` | Richer conversation summary. Must be used, but it mixes buyer statements with analyst framing. |
| `Vendor Name` / `Vendor Enterprise` | Vendor context, often blank or multi-vendor. Useful but not sufficient alone. |
| `Core Topic` | Gartner topic tag where present; often blank. |
| `Buysmart` | Buying-stage marker where present. |

The formatted NotebookLM files are a projection of the raw export, not the canonical source. They keep:

- Date
- Reference Number
- Buyer Region
- Buyer Industry
- Buyer Role
- Purpose
- Question Asked
- Analyst Name
- Discussion Summary

## 3. What the OpenAI data tells us structurally

### Geographic distribution

| Account Region | Records |
|---|---:|
| NORTHAM | 2,154 |
| EMEA | 872 |
| ASIAPAC | 300 |
| JAPAN | 135 |
| LATINAM | 94 |

The corpus is heavily North America-weighted, with meaningful EMEA coverage and smaller Asia-Pacific, Japan, and Latin America representation.

### Sector distribution

| Enterprise Sector | Records |
|---|---:|
| Banking, Finance and Insurance | 952 |
| Manufacturing | 648 |
| Government | 614 |
| Healthcare | 400 |
| Services | 348 |
| Retail | 229 |
| Energy and Utilities | 121 |
| Education | 115 |
| Transportation | 82 |
| Media | 37 |

The highest-volume sectors are financial services, manufacturing, government, healthcare, and services. This means many OpenAI findings can be tested for role/sector breadth, but sector-specific claims should still be evidence-backed rather than assumed.

### Account market / organization type

| Account Market | Records |
|---|---:|
| End User | 3,201 |
| Tech Services Providers | 221 |
| Investors | 101 |
| Professional Services | 32 |

Most records are end-user inquiries, but there are enough investors and tech/services providers that demand-side filtering matters. The prompt explicitly warns that supply-side or competitive-intelligence inquiries should be excluded when the output is supposed to represent buyer demand.

### Role distribution

Top roles include:

- CIO or Head of Technology
- IT - Other Role
- Divisional Technology Leader
- Enterprise Architecture - Other Role
- IT/Infrastructure and Operations - Other Role
- CISO or Head of Information Security
- Data and Analytics roles
- CTO
- IT/Cyber Security and Risk Management
- Program and Portfolio Management

This supports analysis around executive technology decision-making, architecture, security/governance, procurement/commercial terms, and adoption.

### Interaction type

| Interaction Subtype | Records |
|---|---:|
| Inquiry | 3,045 |
| Document Review | 238 |
| Sample Inquiry | 103 |
| Proposal Review | 55 |
| Planning Call | 54 |

This is primarily an inquiry corpus. Proposal/document review records are especially useful for commercial and contracting themes, but the majority of signal comes from advisory inquiries.

### Vendor fields

The OpenAI vendor fields are frequently blank:

- `Vendor Name` is `-` in 2,867 records.
- `Vendor Enterprise` is `-` in 2,895 records.

This matters because the pull was anchored by search logic, not only by the structured vendor field. The analysis cannot rely solely on `Vendor Name`; it must use `Purpose`, `Question Asked`, and `Discussion Summary`.

## 4. Prompt Part 1: what the OpenAI prompts are trying to achieve

The OpenAI prompts define a disciplined buyer-voice analysis for an OpenAI-anchored corpus.

The persistent prompt’s core instruction is:

- act as an independent market analyst;
- observe what buyers are asking about OpenAI;
- avoid advocacy for OpenAI or any competitor;
- discover themes before imposing categories;
- preserve buyer wording;
- distinguish buyer voice from analyst voice;
- cite reference numbers for traceability;
- exclude supply-side inquiries;
- report prevalence qualitatively, not numerically.

### Key OpenAI prompt principles

#### 1. Unconstrained discovery first

The first pass asks the model to go wide:

- surface every distinct thing buyers want to know;
- keep differentiated buyer questions separate;
- include comparison questions;
- avoid organizing or ranking too early.

The point is not to begin with a schema. The point is to let the inquiry corpus reveal the question space.

#### 2. Theme consolidation second

After discovery, the second pass consolidates buyer questions into themes. The prompt says the earlier discovered questions are the spine, but the model must judge theme boundaries against the full corpus.

This means a theme is not just a label. It must have:

- boundary logic;
- supporting interactions;
- buyer-language framing;
- prevalence rating;
- role/industry concentration where supported.

#### 3. Market cuts are analysis-layer scopes

The OpenAI slides include:

- full OpenAI corpus;
- Enterprise AI Assistants;
- Enterprise AI Coding Agents.

The same raw corpus supports all three. The market cut happens in the analysis/prompt layer, not through separate GEAR exports.

#### 4. Other vendors are relational only

Other vendors such as Microsoft, Anthropic, Google, AWS, Meta, Copilot, Claude, Gemini, Bedrock, and Llama appear where buyers compare them with OpenAI. The prompt forbids using this corpus to characterize those vendors’ overall market standing.

Valid:

- “Buyers compare OpenAI with Microsoft Copilot on data handling and enterprise readiness.”

Invalid:

- “Microsoft has stronger market standing than OpenAI.”

#### 5. Demand-side filtering is required

Some records may be investors, technology providers, or other organizations asking about the market rather than buying OpenAI for their own use. The prompt says to judge each interaction by who is asking and why.

## 5. What analysis we can do from the OpenAI dataset

### A. Full-corpus buyer-question analysis

Objective: identify the top questions enterprise buyers ask about OpenAI.

Likely theme families:

- Budget, pricing, credits, renewal, and commercial terms
- Evaluating ChatGPT Enterprise, OpenAI direct, Azure OpenAI, Copilot, Claude, Gemini, and other alternatives
- Guardrails, governance, sensitive data, privacy, and unsanctioned use
- Custom GPTs, agents, orchestration, gateways, and integration patterns
- Adoption, enablement, training, AI literacy, and ROI
- Coding agents, Codex, GitHub Copilot, Claude Code, and developer workflow impact
- Brand visibility and AI-answer exposure, where evidence supports it

### B. Enterprise AI Assistants market-cut analysis

Objective: analyze OpenAI inside the enterprise AI assistant market.

Questions this can answer:

- Are buyers choosing one assistant or supporting several?
- How do they compare ChatGPT Enterprise, Microsoft Copilot, Claude, Gemini, and Azure OpenAI?
- What are they asking about data protection and enterprise controls?
- How are they governing employee-built GPTs or assistants?
- How are they justifying overlapping spend?

### C. Enterprise AI Coding Agents market-cut analysis

Objective: analyze OpenAI/Codex inside AI coding-agent adoption.

Questions this can answer:

- How are buyers comparing Codex, GitHub Copilot, Claude Code, and other coding agents?
- Where do they expect coding agents to fit in the SDLC?
- What access, file-share, repository, and security controls concern them?
- How are token/credit consumption models changing developer-tool budgeting?

### D. Commercial and negotiation analysis

The OpenAI data contains proposal review and commercial inquiries. This supports analysis of:

- ChatGPT Enterprise renewals;
- credit allocation and overage;
- token or consumption-based pricing;
- contract structure;
- OpenAI direct versus Azure OpenAI;
- enterprise discounting and commitments.

### E. Governance and risk analysis

The data supports analysis of:

- sensitive data entering ChatGPT;
- unsanctioned AI use;
- SharePoint/data indexing concerns;
- custom GPT governance;
- agentic system governance;
- procurement and security approval processes.

### F. Buyer composition analysis

Because the export includes region, sector, role, market, and persona, each theme can be profiled by:

- roles asking;
- sectors represented;
- regions represented;
- whether it is concentrated or broad;
- whether it appears in end-user records versus investor/tech-provider records.

## 6. What the OpenAI dataset should not be used for

The OpenAI dataset should not be used to:

- measure total market share;
- rank OpenAI against competitors overall;
- infer sentiment or satisfaction;
- claim other vendors’ overall standing;
- report consumer behavior;
- assume all `GPT` mentions are OpenAI;
- treat record counts as slide-facing prevalence;
- present investor or supply-side questions as enterprise buyer demand without filtering.

## 7. Analytical output model for OpenAI

The OpenAI output should be a separate deliverable with these report sections:

1. Dataset overview
2. Pull/query interpretation
3. Demand-side filtering notes
4. Full-corpus buyer-question themes
5. Enterprise AI Assistants market-cut themes
6. Enterprise AI Coding Agents market-cut themes
7. Buyer composition by role, region, sector, and market
8. Evidence ledger by theme
9. Validation gaps
10. Slide-facing output draft

## 8. What the schema should represent for OpenAI

The schema should start from the data and analysis objects, not from generic vendor scoring.

Recommended schema direction: create a dedicated schema named `OpenAI Buyer Data Analysis`.

This should be a buyer-perspective inquiry analysis schema. It should be closer in spirit to an ASAF-style framework/report structure than to a vendor-list scoring file. OpenAI is the organization being analyzed, but the analytical unit is not a vendor row. The analytical units are buyer questions, inquiry records, themes, market cuts, evidence, and slide/report outputs.

The schema can share a common Buyer Voice data model with ServiceNow, but it should allow OpenAI-specific dimensions and report sections:

- full-corpus OpenAI inquiry themes;
- Enterprise AI Assistants market-cut themes;
- Enterprise AI Coding Agents market-cut themes;
- OpenAI-vs-adjacent-vendor comparison context;
- OpenAI commercial/credit/renewal questions;
- OpenAI governance, data, agent, adoption, and value questions.

The existing vendor-score structure should not be the primary model. It can be reused only if the app needs a temporary compatibility layer for selecting an organization, but the long-term model should be `schema -> dataset -> inquiry/theme/report`, not `schema -> vendor list -> vendor scorecard`.

Core entities should include:

- `dataset`
- `gear_query_or_pull`
- `interaction`
- `buyer_profile`
- `vendor_anchor`
- `analysis_scope`
- `market_cut`
- `buyer_question`
- `theme`
- `theme_rating`
- `evidence_reference`
- `excerpt`
- `voice_attribution`
- `validation_finding`
- `slide_output`

For OpenAI, the schema needs to support one vendor anchor with multiple market-cut scopes.

## 9. Schema and report architecture options

### Option A: use the existing vendor-data rails as a compatibility layer

This would treat OpenAI as a single selectable entity in the existing app rails.

Pros:

- Fastest to wire into the current app.
- Reuses existing schema picker, analysis tab, and report tab behavior.
- Keeps a simple way to select OpenAI as the active organization.

Cons:

- Misleading mental model: this is not a vendor capability scorecard.
- Forces buyer questions and themes into score fields that were built for vendor comparisons.
- Makes it too easy to blend OpenAI and ServiceNow as if they were comparable vendor rows.

Use only as a bridge if needed.

### Option B: create a dedicated ASAF-like inquiry-analysis schema

This would model OpenAI as its own buyer data analysis framework/report workspace.

Pros:

- Better aligned with the data.
- Supports tabs like Dataset, Query/Pull, Buyer Questions, Market Cuts, Themes, Evidence, Validation, and Slide Output.
- Avoids fake vendor scoring.
- Keeps OpenAI and ServiceNow separate while sharing the same underlying Buyer Voice object model.

Cons:

- Requires app work to create or adapt non-vendor report rails.
- Existing dashboards that expect `vendors[]` will not apply without a compatibility adapter.

Recommended direction: Option B.

## 10. Immediate next work

1. Stop treating the current Buyer Voice schema/vendor-score files as authoritative; mark them as exploratory/temporary.
2. Define a new `OpenAI Buyer Data Analysis` schema around inquiry-analysis objects, not vendor rows.
3. Extract the OpenAI prompt section into a clean prompt archive.
4. Document the likely GEAR query/pull interpretation: OpenAI/product mentions across 2026 YTD inquiry records.
5. Build a dataset profile from raw GEAR fields: region, sector, role, persona, account market, interaction subtype, buying stage, purpose, vendor fields, and date windows.
6. Generate a first-pass buyer-question inventory from `Question Asked`.
7. Use `Discussion Summary` to enrich themes while tagging buyer versus analyst voice.
8. Build explicit qualifying sets for Enterprise AI Assistants and Enterprise AI Coding Agents.
9. Produce evidence ledgers with 2-4 reference examples per theme.
10. Design tabbed reports for:
    - Dataset Overview
    - Query/Pull Interpretation
    - Full-Corpus Buyer Questions
    - Enterprise AI Assistants
    - Enterprise AI Coding Agents
    - Buyer Composition
    - Evidence Ledger
    - Validation Findings
    - Slide Output
11. Rebuild the app integration around this schema/report model after the data model is agreed.
