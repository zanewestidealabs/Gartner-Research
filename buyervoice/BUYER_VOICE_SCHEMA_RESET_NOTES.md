# Buyer Voice Schema Reset Notes

Updated: August 2026

## Current conclusion

The current Buyer Voice schema and vendor-score approach should be treated as exploratory. It helped us learn the data shape, but it is not the right long-term model.

The right model starts from buyer inquiry data, not vendor scoring.

## Proposed direction

Create two separate buyer data analysis schemas:

1. `OpenAI Buyer Data Analysis`
2. `ServiceNow Buyer Data Analysis`

These schemas should share a common Buyer Voice object model, because the raw GEAR fields and evidence workflow are the same. But each schema should have its own outcome-specific dimensions, reports, themes, and validation requirements.

## Why not one vendor-score schema?

OpenAI and ServiceNow are not two rows in one comparable vendor analysis.

They are two different inquiry datasets:

- OpenAI: AI platform, enterprise AI assistant, coding-agent, governance, adoption, and commercial questions.
- ServiceNow: workflow-platform commercial friction, pricing, packaging, licensing, renewal, ROI, alternatives, and cost-offset questions.

The buyer questions, product categories, prompt objectives, and slide outputs are different. A shared vendor-score structure forces a false comparison.

## Better app model

The better app model is closer to ASAF/framework/report rails:

```text
schema
  -> dataset
  -> GEAR query / pull interpretation
  -> interactions
  -> buyer profile
  -> analysis scope
  -> questions / discovery items
  -> themes / categories / market cuts
  -> evidence references and excerpts
  -> ratings / provenance / sensitivity
  -> validation findings
  -> slide/report output
```

The app may still use a temporary compatibility adapter where a single organization appears as a selectable entity, but the real data model should not be `vendors[]`.

## Shared object model

Both schemas should support:

- `dataset`
- `gear_query_or_pull`
- `interaction`
- `buyer_profile`
- `organization_anchor`
- `analysis_scope`
- `buyer_question` or `discovery_item`
- `theme`
- `theme_rating`
- `evidence_reference`
- `excerpt`
- `voice_attribution`
- `validation_finding`
- `report_output`
- `slide_output`

## OpenAI-specific additions

OpenAI needs:

- `market_cut`
- `comparison_vendor_context`
- `assistant_market_scope`
- `coding_agent_market_scope`
- `ambiguous_gpt_mention`
- `supply_side_exclusion`

Recommended report tabs:

- Dataset Overview
- Query/Pull Interpretation
- Full-Corpus Buyer Questions
- Enterprise AI Assistants
- Enterprise AI Coding Agents
- Buyer Composition
- Evidence Ledger
- Validation Findings
- Slide Output

## ServiceNow-specific additions

ServiceNow needs:

- `commercial_scope`
- `supplied_category`
- `outside_taxonomy_theme`
- `trajectory_rating`
- `figure_claim`
- `figure_provenance`
- `sensitivity_flag`
- `roi_business_case_pass`

Recommended report tabs:

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

## Considerations and concerns before rebuild

1. Should the app expose these as two separate schemas, or as one shared Buyer Voice schema with two configured outcome profiles?
2. Do we want to keep any backward-compatible vendor-file adapter so existing dashboard code can load an organization, or should we remove Buyer Voice from vendor rails entirely?
3. Should OpenAI and ServiceNow have independent report tabs under Reports, or should there be one Buyer Voice tab with two organization subtabs?
4. How much automated extraction should happen now versus being represented as documented methodology?
5. Should the first rebuild prioritize schema correctness, report rendering, or evidence-ledger generation?
6. What is the minimum evidence threshold for a theme before it appears in a slide-facing report?
7. Should the raw GEAR query/pull definition be stored as a first-class object, even if the original exact GEAR query is not available?

## Recommended next decision

Decide between:

- two fully separate schemas: `OpenAI Buyer Data Analysis` and `ServiceNow Buyer Data Analysis`; or
- one shared `Buyer Voice Inquiry Analysis` schema with two outcome profiles.

My recommendation is two separate schemas that share a common underlying object model. That gives us separation in the UI and reports while avoiding duplicated data-field definitions.
