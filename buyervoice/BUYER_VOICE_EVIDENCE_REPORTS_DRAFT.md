# Buyer Voice Evidence Reports Draft

Updated: August 2026

This draft is now an index across two separate organization-specific Buyer Voice outcomes. It should not be treated as one blended report.

Use the outcome-specific documents as the primary working reports:

- `BUYER_VOICE_OPENAI_OUTCOME.md` for OpenAI slides 1-4.
- `BUYER_VOICE_SERVICENOW_OUTCOME.md` for ServiceNow slides 5-7.

The shared methodology remains in `BUYER_VOICE_METHODOLOGY_AND_EVIDENCE.md`.

Important: this is an audit-facing draft. Client-identifying detail, exact figures, and sensitive negotiation tactics require redaction and analyst review before external use.

## Outcome structure

| Slide | Vendor dataset | Report type | Objective |
|---|---|---|---|
| 1 | OpenAI | Cover/title | Introduce the OpenAI Buyer Voice analysis package. |
| 2 | OpenAI | Vendor view | Top buyer questions across the full OpenAI corpus. |
| 3 | OpenAI | Vendor-in-market view | OpenAI in Enterprise AI Assistants. |
| 4 | OpenAI | Vendor-in-market view | OpenAI/Codex in Enterprise AI Coding Agents. |
| 5 | ServiceNow | Vendor relationship matrix | Commercial friction across five supplied categories. |
| 6 | ServiceNow | Deep dive | AI-native pricing and packaging. |
| 7 | ServiceNow | Sensitive deep dive | Cost-offset tactics using ServiceNow tools. |

## Separation rule

OpenAI and ServiceNow have different organizations, source pulls, report questions, evidence bases, scoring justifications, and deliverable outcomes.

They share the Buyer Voice schema and methodology, but their reports should remain separate:

- OpenAI outcome: “What are enterprise buyers asking about OpenAI, including market-specific cuts?”
- ServiceNow outcome: “What commercial and economic friction are buyers raising about ServiceNow?”

## Slide 1: Buyer Voice Analysis for GGM

### Objective

Introduce the package as a Buyer Voice analysis output built from Gartner end-user interaction data.

### Required content

- Title
- Audience or sponsor
- Date/version
- Internal-use marker where appropriate

### Evidence requirement

No evidence table required. This slide is package framing.

## Slide 2: Top questions enterprise buyers are asking about OpenAI

### Objective

Show the most important buyer-question themes across the full OpenAI-anchored corpus.

### Dataset

- Source: `GEAR - OpenAI - 07252026.csv`
- Records: 3,555
- Date range: 2026-01-02 to 2026-07-23
- Anchor: OpenAI/vendor view

### Draft slide structure

| Theme | Prevalence | Roles asking | Evidence examples |
|---|---|---|---|
| Budget and commercial terms | Pervasive | IT Procurement, sourcing/vendor management, CIO, finance/FinOps, transformation | `20082892`, `20125463`, `19491723` |
| Evaluating and selecting | Pervasive | EA, CIO, IT leadership, software engineering, portfolio/investment roles | `19446349`, `19132786`, `19483074` |
| Guardrails and governance | Pervasive | CISO/security, CIO, EA, data governance, compliance | `20047573`, `19267455`, `19510207` |
| Orchestrating and integrating agents | Significant | EA, CIO, divisional technology, software engineering | `20204816`, `19510207`, `19446349` |
| Adoption and proving value | Significant | CIO, transformation, software engineering, enterprise applications, finance | `20055788`, `19491723`, `19446349` |
| Brand visibility in AI answers | Significant in the example deck; requires dedicated validation before final scoring | Marketing, digital, CX, strategy | Needs a dedicated evidence pass before externalization |

### Validation notes

- Exclude supply-side records where the asker is using Gartner to support their own competitive intelligence or go-to-market work.
- Treat bare `GPT` as ambiguous unless OpenAI attribution is supported.
- Do not infer overall standing for Anthropic, Microsoft, Google, AWS, or Meta from this OpenAI-anchored corpus.
- Do not show raw counts or reference numbers on the slide unless explicitly approved.

## Slide 3: What enterprise buyers are asking about OpenAI: Enterprise AI Assistants

### Objective

Show the OpenAI buyer voice inside the Enterprise AI Assistants market boundary.

### Dataset

- Source: same OpenAI corpus
- Scope: market-cut at prompt/analysis layer
- Anchor: vendor-in-market view

### Draft slide structure

| Theme | Prevalence | Roles asking | Evidence/source requirement |
|---|---|---|---|
| Choosing between assistants, or running more than one | Pervasive | CIO, EA, IT infrastructure/operations, strategy, category management | Qualifying set must show assistant comparison records. |
| Licensing, cost control, and proving value | Pervasive | Sourcing/procurement, CIO, CFO, EA, CHRO | Evidence should include licensing, credit, renewal, and ROI records. |
| Protecting enterprise data | Significant | CISO, compliance, EA, security operations, D&A | Evidence should include data handling, SharePoint, consumer-grade use, and contractual protection. |
| Governing what business users build | Moderate | Manager, EA, CIO, CDAO | Evidence should include custom GPT/tool proliferation and governance. |

### Evidence examples already supporting the market-cut logic

- `19132786`: Copilot versus ChatGPT Enterprise and business value/data-handling questions.
- `20047573`: ChatGPT Business to Enterprise and security/data considerations.
- `19267455`: SharePoint data, training, storage, and access restrictions.
- `20055788`: ChatGPT at scale, adoption, administration, and governance.

### Validation notes

- The market-cut must produce an explicit qualifying-reference list.
- Spread must be assessed against the qualifying subset, not the full OpenAI corpus.
- Do not infer buyer preference from competitor mentions alone.

## Slide 4: What enterprise buyers are asking about OpenAI: Enterprise AI Coding Agents

### Objective

Show the OpenAI/Codex buyer voice inside the Enterprise AI Coding Agents market boundary.

### Dataset

- Source: same OpenAI corpus
- Scope: market-cut at prompt/analysis layer
- Anchor: vendor-in-market view

### Draft slide structure

| Theme | Prevalence | Roles asking | Evidence/source requirement |
|---|---|---|---|
| Comparing coding agents and selecting a vendor | Significant | EA, CIO, infrastructure/operations, software engineering | Evidence should include Codex, Claude Code, GitHub Copilot, and comparison language. |
| Embedding agents into the SDLC | Significant | Software engineering, EA, IT operations | Evidence should include requirements, development, testing, standards, and modernization. |
| Governing what coding agents can reach | Moderate | Security/risk, CIO, EA | Evidence should include data/file-share access, zero trust, latency, and government/security concerns. |
| Budgeting developer token spend | Moderate | Procurement, software engineering, CIO | Evidence should include token, credit, power-user, or usage optimization concerns. |

### Evidence examples already supporting the market-cut logic

- `19446349`: evaluating AI coding assistants and Codex capabilities.
- `19510207`: Codex/GPT coding-agent risks, agents, external systems, and data movement.
- `20204816`: enablement framework for AI tools including OpenAI Codex.
- `20125463`: credit allocation and renegotiation after advanced capability usage.

### Validation notes

- This is a smaller qualifying set; thin themes should be labeled thin rather than inflated.
- Product names should remain exactly as they appear in the source record.

## Slide 5: Commercial friction across the five ServiceNow deep-dive areas

### Objective

Show the high-level ServiceNow commercial-friction matrix across supplied categories.

### Dataset

- Source: `GEAR - ServiceNow Commercial Friction Set.csv`
- Records: 4,114
- Date range: 2026-01-02 to 2026-07-30
- Anchor: vendor relationship view

### Draft slide structure

| Category/theme | Spread | Trajectory | Evidence examples |
|---|---|---|---|
| AI-native pricing and packaging | Significant to pervasive depending on subtheme | New/stable/intensifying by subtheme | `20127470`, `20110800`, `20182317` |
| Renewal cost and contract leverage | Pervasive | Stable | `20088577`, `20110800`, `20153161` |
| Platform displacement and cost alternatives | Pervasive in example deck; requires stricter separation from generic cost pressure | Intensifying/stable by subtheme | `20127470`, `20182317` plus additional displacement-specific pass |
| AI business case and ROI proof gap | Significant to pervasive | Stable/intensifying | `20127470`, `20110800`, `20182317` |
| Cost-offset tactics using ServiceNow's own tools | Moderate/significant | Stable | `20088577`, `20110800` plus deeper tactic-specific pass |

### Session implications

- Go deepest on renewal mechanics and TCO.
- Treat AI-native pricing as still forming.
- Treat July/3Q26 as partial and directional.
- Keep cost-offset tactics in analyst-review status before external use.

### Validation notes

- Supplied categories are naming buckets, not search terms.
- Outside-taxonomy findings should be retained.
- Every figure requires provenance.
- Tactic-sensitive content requires handling review.

## Slide 6: AI-native pricing and packaging

### Objective

Explain the ServiceNow AI-native pricing/package transition in buyer-language theme cards.

### Draft theme cards

| Theme | Spread/trajectory | Evidence examples | Validation notes |
|---|---|---|---|
| Forced migration to AI-native tiers at renewal | Significant / New | `20110800`, `20127470` | Requires careful wording and reference-level support for any mandatory-migration claim. |
| Budgeting volatility in token-based consumption | Pervasive / Stable | `20127470`, `20182317` | Figures and ratios require provenance tagging. |
| Duplicate spend with acquired platforms | Moderate / Intensifying in example deck | Requires a dedicated Moveworks/acquired-platform evidence pass | Do not assert duplicate spend without multiple-account support. |

### Buyer composition

Observed examples include IT category management, IT service management leadership, enterprise architecture, government, banking/finance/insurance, retail, and EMEA/North America coverage.

### Validation notes

- Tag figures as single-account or multiple-account.
- Mark July-only 3Q26 as partial.
- Keep analyst comments out of buyer-voice bullets.

## Slide 7: Cost-offset tactics using ServiceNow's own tools

### Objective

Explain buyer tactics for reducing ServiceNow spend inside the platform and clearly mark the content as sensitive.

### Draft theme cards

| Theme | Spread/trajectory | Evidence examples | Handling |
|---|---|---|---|
| Configuration workarounds to avoid license inflation | Moderate / Stable in example deck | Requires deeper tactic-specific evidence pass | Internal context until analyst review. |
| Fulfiller versus business stakeholder license optimization | Significant / Stable in example deck | Requires deeper role/license-specific evidence pass | Internal context until analyst review. |

### Handling note

This report is sensitive because it describes how buyers reduce spend and may include audit exposure. The narrative should be withheld from external use until reviewed.

### Validation notes

- Do not convert buyer tactics into Gartner recommendations.
- Separate buyer-reported behavior from analyst interpretation.
- Redact client-identifying details.
- Ensure claims rest on multiple distinct buyer interactions.

## Evidence-backed score implications

The evidence pass supports moving beyond the seed scoring:

- OpenAI moves up in source, discovery, evidence, and output readiness because the main slide themes can be tied to actual references.
- ServiceNow moves up in run/scoping, supplied-category assignment, rating, and output readiness because the matrix/deep-dive structure directly maps to the prompt and slide examples.
- Both remain capped on validation because complete evidence ledgers, attribution classification, redaction checks, and figure provenance are not fully automated yet.

See `Buyer Voice Vendor 1-1 Evidence.json` for the active evidence-backed scoring dataset.

## Required next pass before final publication

1. Generate full evidence ledgers for every slide theme.
2. Generate exact market-cut qualifying sets for slides 3 and 4.
3. Run supply-side exclusion for OpenAI.
4. Run buyer-versus-analyst attribution classification for all Discussion Summary excerpts.
5. Run redaction and figure provenance checks.
6. Re-rate spread/trajectory after validation.
7. Render slide-facing output with counts and references suppressed.
