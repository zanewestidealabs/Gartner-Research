# Buyer Voice Methodology, Evidence Scoring, and Report Production Model

Updated: August 2026

## Purpose

This document defines how the Buyer Voice schema should be used to turn raw GEAR exports into slide-ready buyer-voice reports and evidence-backed vendor scoring.

The current Buyer Voice package contains two vendor-specific datasets:

- `OpenAI`: `buyervoice/Corpora - Raw GEAR/GEAR - OpenAI - 07252026.csv`
- `ServiceNow`: `buyervoice/Corpora - Raw GEAR/GEAR - ServiceNow Commercial Friction Set.csv`

Slides 1-7 in `buyervoice/Deck/Buyer Voice - Slide Examples - Aug 2026.pptx` are the target output forms. Slides 8 onward explain the methodology, operating model, judgment points, and automation roadmap used to get the data into that form.

## Core distinction

Buyer Voice scoring is not product scoring.

The Buyer Voice vendor score measures how ready a vendor-specific corpus is for producing defensible Buyer Voice analysis:

- Is the source package complete?
- Are interactions normalized and traceable?
- Are report scopes explicit?
- Are themes discovered before they are categorized?
- Are ratings qualitative and evidence-backed?
- Are excerpts and reference numbers available?
- Are slide claims separated from evidence?
- Are validation, attribution, redaction, and sensitivity checks performed?

The score should therefore be read as corpus/report readiness, not as a claim that OpenAI or ServiceNow is better or worse as a vendor.

## Slide objectives

### Slide 1: title

Objective: introduce the Buyer Voice analysis package and frame the deck as a working example of Gartner interaction data turned into analyst-ready output.

### Slide 2: OpenAI full-corpus buyer questions

Objective: show the top buyer questions across the full OpenAI-anchored corpus.

Required output:

- Theme and buyer-question table
- Qualitative prevalence
- Roles asking
- Source note

Expected themes in the example:

- Budget and commercial terms
- Evaluating and selecting
- Guardrails and governance
- Orchestrating and integrating agents
- Adoption and proving value
- How our brand shows up in AI answers

Method implication: this is a vendor view. It should read the full OpenAI corpus and surface what enterprise buyers ask when OpenAI is the anchor.

### Slide 3: OpenAI Enterprise AI Assistants market cut

Objective: show what buyers ask about OpenAI within a defined Enterprise AI Assistants market boundary.

Required output:

- Market-cut title
- Buyer-question themes
- Prevalence
- Roles asking
- Source note

Expected themes in the example:

- Choosing between assistants or running more than one
- Licensing, cost control, and proving value
- Protecting enterprise data
- Governing what business users build

Method implication: this is a vendor-in-market view. The market cut happens at the analysis layer, not by re-pulling the raw data.

### Slide 4: OpenAI Enterprise AI Coding Agents market cut

Objective: show what buyers ask about OpenAI/Codex within the Enterprise AI Coding Agents market boundary.

Required output:

- Market-cut title
- Buyer-question themes
- Prevalence
- Roles asking
- Source note

Expected themes in the example:

- Comparing coding agents and selecting a vendor
- Embedding agents into the software development lifecycle
- Governing what coding agents can reach
- Budgeting developer token spend

Method implication: this is a narrower vendor-in-market view. The qualifying set must pass both the market-boundary test and the OpenAI anchoring test.

### Slide 5: ServiceNow commercial friction matrix

Objective: summarize buyer commercial and economic friction across five supplied deep-dive areas.

Required output:

- Category/theme matrix
- Spread rating
- Trajectory rating
- Session implications
- Sensitivity note where needed

Expected supplied categories:

- AI-native pricing and packaging
- Renewal cost and contract leverage
- Platform displacement and cost alternatives
- AI business case and ROI proof gap
- Cost-offset tactics using ServiceNow's own tools

Method implication: this is a vendor relationship view. The five categories are naming buckets used after discovery, not search terms that constrain discovery.

### Slide 6: ServiceNow AI-native pricing and packaging deep dive

Objective: expand one ServiceNow commercial-friction category into evidence-backed theme cards.

Required output:

- Category title and kicker
- Theme cards
- Spread and trajectory
- Buyer narrative
- Buyer composition
- Source note

Expected themes in the example:

- Forced migration to AI-native tiers at renewal
- Budgeting volatility in token-based consumption
- Duplicate spend with acquired platforms

Method implication: this is a deep-dive report. It should be written after the matrix pass and should preserve figure provenance if any prices, percentages, or ranges appear.

### Slide 7: ServiceNow cost-offset tactics deep dive

Objective: expand a sensitive commercial-friction category into theme cards and explicitly mark handling risk.

Required output:

- Category title and kicker
- Theme cards
- Spread and trajectory
- Buyer narrative
- Buyer composition
- Handling note

Expected themes in the example:

- Configuration workarounds to avoid license inflation
- Fulfiller versus business stakeholder license optimization

Method implication: this section is not automatically client-facing. It describes buyer tactics for reducing spend and may include audit exposure. It requires analyst sensitivity review before external use.

### Slide 8 onward: methodology and approach

Objective: document how the outputs are produced and where judgment is required.

The methodology slides define:

- the source-to-output model;
- how one pull can answer multiple asks;
- anchor types;
- what is teachable versus what requires practitioner judgment;
- what is automated, what should be automated, and what stays manual;
- risks created by GEAR retirement and uncertainty in future source systems.

## Data pipeline

### 1. Canonical source

The raw GEAR CSV is the canonical record source. The application should always preserve the raw row and reference number.

Required raw fields:

- `Reference Number`
- `First Response Date`
- `Account Region`
- `Enterprise Sector`
- `Role Name`
- `Purpose`
- `Question Asked`
- `Associate Name`
- `Discussion Summary`
- `Vendor Enterprise`
- `Vendor Name`
- all remaining raw fields as retained context

### 2. Formatter projection

`buyervoice/Script/gear_notebooklm_formatter_w_quarter.py` creates the NotebookLM-facing projection. It keeps the following report fields:

| Raw GEAR field | Report field |
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

The formatter groups records by quarter and splits large text outputs under the NotebookLM word limit. These files are useful for model ingestion, but they do not replace the raw CSV.

### 3. Prompt-layer analysis

The NotebookLM prompts operate in this order:

1. Load the persistent rulebook.
2. Run open discovery.
3. Consolidate discovered items into themes.
4. Apply scope or supplied-category organization.
5. Rate spread and trajectory.
6. Select references and excerpts.
7. Validate claims, attribution, and redaction before output.

The critical discipline is that discovery comes before taxonomy.

## Analysis anchors

Every Buyer Voice report must state its anchor.

| Anchor | Meaning | Example |
|---|---|---|
| Market view | No vendor anchor; asks where demand is heading. | Future AI assistant demand. |
| Vendor view | One vendor across all topics. | Slide 2, OpenAI full corpus. |
| Vendor-in-market view | One vendor inside a defined market. | Slides 3-4, OpenAI assistants/coding agents. |
| Vendor relationship view | Commercial, support, renewal, contracting, value, and customer-experience lens. | Slides 5-7, ServiceNow commercial friction. |
| Absence view | Where a vendor does not appear and which conversations it is missing from. | Future report type. |

## Evidence rules

### Buyer voice fields

`Question Asked` is direct buyer voice.

`Discussion Summary` must be used because it contains rich context, but it is mixed voice. Every statement used from it needs one of these attribution states:

- buyer-raised;
- analyst voice;
- attribution uncertain.

Analyst voice is not buyer voice. Gartner recommendations, market statistics, and analyst conclusions may be used only in labeled context, never as buyer-voice evidence.

### Reference rules

Every theme or claim must trace to reference numbers.

Rules:

- Write reference numbers as plain text in audit output.
- Use 2-4 references per theme.
- References are exemplars, not statistical weight.
- Select references that span role, industry, region, or month where possible.
- A theme must rest on multiple buyer interactions.
- Single-record findings are isolated observations, not themes.

### Redaction and sensitivity

Before any client-facing output:

- remove named client organizations;
- remove specific prices, seat counts, and headcounts unless explicitly approved;
- mark negotiation tactics and cost-offset tactics for analyst review;
- mark numerical figures as single-account or multiple-account when used internally;
- suppress reference numbers and raw counts from slide-facing output unless approved.

## Rating model

### Spread

Spread is qualitative. It combines recurrence with breadth across buyer roles, sectors, and regions.

| Spread | Meaning |
|---|---|
| Pervasive | Near-universal or very broad across the qualifying set. |
| Significant | Common and recurring across a large share of conversations. |
| Moderate | Real and repeated, but concentrated in certain buyer types or use cases. |
| Niche | Present, but narrow or limited to a small set of contexts. |

Counts can inform judgment but should not be emitted in slide-facing output.

### Trajectory

Trajectory compares quarters and must account for partial periods.

| Trajectory | Meaning |
|---|---|
| New | Appears meaningfully only in the latest comparison period. |
| Intensifying | Stronger or more frequent in later periods. |
| Stable | Present across periods without clear acceleration or decline. |
| Fading | Weaker or less frequent in later periods. |

For the current ServiceNow dataset, 3Q26 is July-only and must be marked partial/directional.

## Evidence-backed scoring

The Buyer Voice schema scores the readiness of the corpus/report package.

Scores should be increased when:

- raw and formatted sources are present;
- corpus date windows and record counts are known;
- reference numbers resolve;
- report scopes are explicit;
- themes map to multiple evidence records;
- report outputs separate slide-facing claims from audit support;
- validation checks are explicit and can be run.

Scores should be capped when:

- evidence ledgers are sampled rather than fully generated;
- market cuts lack explicit qualifying-reference lists;
- claim validation is manual;
- redaction and attribution checks are documented but not automated;
- figures are not fully provenance-tagged.

### Current evidence-backed assessment

The package has strong source, interaction, discovery, and report-output readiness. It should move beyond seed scoring because the scoring can now point to actual GEAR reference examples. However, validation should remain below productionized level until the app generates full evidence ledgers and automated claim checks.

## Evidence samples used for score justification

The examples below are audit-facing support snippets. They demonstrate that the slide themes exist in the raw GEAR exports and can be traced back to reference numbers. They are not the complete evidence base.

### OpenAI evidence examples

| Theme | Example reference support |
|---|---|
| Budget and commercial terms | `20082892`: renewal of ChatGPT Enterprise and advice on pricing/benchmarking; `20125463`: exceeding credit allocations and renegotiating credit allowances; `19491723`: renewal process and optimizing total spend. |
| Evaluating and selecting | `19446349`: evaluating AI coding assistants and Codex capabilities; `19132786`: differences between Copilot and ChatGPT Enterprise; `19483074`: OpenAI and Anthropic contracting patterns. |
| Guardrails and governance | `20047573`: business/security ramifications and data considerations moving from ChatGPT Business to Enterprise; `19267455`: SharePoint data, training, storage, and access concerns; `19510207`: risks around Codex, agents, external systems, and data movement. |
| Orchestrating and integrating agents | `20204816`: framework for enabling AI tools including Copilot Agent, Copilot Studio, ChatGPT, and Codex; `19510207`: agents, external systems, and data movement; `19446349`: Codex scale and comparison to other tools. |
| Adoption and proving value | `20055788`: launched ChatGPT at scale and working through adoption and operationalization; `19491723`: optimizing spend and increasing efficiencies; `19446349`: client success stories and ability to scale. |
| Brand visibility in AI answers | Evidence exists but should be treated as a narrower market/brand-exposure signal and validated with a dedicated pass before scoring it as broad as the other themes. |

### ServiceNow evidence examples

| Theme | Example reference support |
|---|---|
| AI-native pricing and packaging | `20127470`: transition from modular pricing to integrated AI platform commercial model; `20110800`: AI-first subscription models, Pro Plus, Enterprise Plus, and Now Assist; `20182317`: SaaS licensing shifting toward usage and consumption models. |
| Renewal cost and contract leverage | `20088577`: renewal, potential price hike, early renewal, and negotiation strategy; `20110800`: renewal options and commercial best practices; `20153161`: renewal, discounting, increases, and commercial trends. |
| Platform displacement and cost alternatives | `20127470`: flexibility and cost transparency concerns as ServiceNow changes model; `20182317`: comparison to changing SaaS licensing models; additional pass needed to separate true displacement from general cost pressure. |
| AI business case and ROI proof gap | `20127470`: cost transparency and pitfalls; `20110800`: price uplift and maximizing leverage; `20182317`: return and business-case implications from consumption-based models. |
| Cost-offset tactics using ServiceNow tools | `20088577`: renewal strategy and favorable terms; `20110800`: managing uplift and leverage; deeper evidence pass is required before externalizing tactic-specific claims. |

## Report production workflow

### Step 1: source intake

Register the dataset:

- dataset ID;
- vendor anchor;
- source file;
- date range;
- record count;
- quarter distribution;
- formatter projection files;
- prompt package;
- deck/report target.

### Step 2: corpus eligibility

For each interaction:

- confirm it belongs to the vendor or scope;
- exclude supply-side interactions where the asker is selling into the market;
- mark ambiguous vendor mentions;
- preserve uncertain records for audit rather than silently dropping them.

### Step 3: discovery

Run open discovery:

- identify buyer questions or concerns;
- keep buyer language;
- do not force themes into a pre-existing taxonomy;
- label thin or isolated observations.

### Step 4: consolidation

Merge discovered items into themes:

- name the theme in buyer language;
- document what belongs and what does not;
- preserve awkward fits;
- for supplied categories, assign after discovery.

### Step 5: rating

Apply the rubric:

- spread;
- trajectory where quarters support it;
- persistence where needed;
- optional sentiment or competitive scenario only when supported.

### Step 6: evidence ledger

For each theme:

- 2-4 reference numbers;
- source field;
- excerpt;
- role, sector, region, month;
- attribution state;
- redaction status.

### Step 7: claim registry

For each slide/report claim:

- claim text;
- claim type;
- theme linkage;
- reference support;
- validation status;
- sensitivity/redaction status.

### Step 8: slide assembly

Render the slide form:

- slide-facing title;
- kicker;
- theme cards or table;
- spread/trajectory dots;
- roles asking or buyer composition;
- source note;
- no raw counts or references by default.

### Step 9: validation

Before publication:

- every reference resolves;
- every theme has multiple interactions unless labeled isolated;
- Discussion Summary claims have attribution;
- no analyst voice is mixed into buyer voice;
- figures have provenance;
- buyer composition claims are supported;
- sensitive content is reviewed;
- client identifiers are redacted.

## App implementation implications

The app should support three linked objects:

1. `Buyer_Voice_Schema_1_0.json`: the schema and scoring structure.
2. Buyer Voice vendor-score JSON: corpus/report readiness for OpenAI and ServiceNow, with evidence references.
3. Buyer Voice report JSON/API: slide-aligned report definitions, generated themes, evidence ledgers, and validation findings.

The Reports tab should show:

- Overview;
- OpenAI full corpus;
- OpenAI market cuts;
- ServiceNow matrix;
- ServiceNow deep dives;
- Method and operating model.

The Vendors/Analysis rails should show:

- corpus readiness scores;
- pillar/sub-pillar scorecards;
- evidence-backed rationales;
- validation gaps;
- next automation steps.

## Next automation targets

1. Generate complete evidence ledgers from raw CSVs.
2. Generate exact qualifying-reference sets for OpenAI market cuts.
3. Add demand-side/supply-side classification.
4. Add buyer-versus-analyst attribution classification for Discussion Summary.
5. Add redaction and figure-provenance checks.
6. Generate slide JSON from theme/claim/evidence objects.
7. Export slide-aligned report markdown or PPTX.
