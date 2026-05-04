# Research Validation Pipeline

This folder contains a *resumable* workflow to move from deterministic “score normalization” to evidence-based scoring.

## What it produces
- `Vendor 4-1 Researched.json` (default output):
  - Keeps the existing vendor record.
  - Adds `research` metadata.
  - Adds `sub_pillar_evidence` (URLs + excerpts).
  - Adds `sub_pillar_scores_researched` (heuristic suggestions based on public text signals).
  - Adds `pillar_scores_researched` (average of researched sub-pillars).

## How it works (high-level)
1. Extract URLs from each vendor’s `capability_analysis`.
2. Fetch those pages (with caching under `research/cache/pages/`).
3. Convert HTML to text, then search for:
   - AI/agentic signals
   - Sub-pillar specific terms (derived from `schema4-0_enhanced.json`)
4. Store short, defensible excerpts and the source URLs.

## Run
From the workspace root:

- Small dry run (3 vendors):
  - `G:/My Drive/Gartner/.venv/Scripts/python.exe research_validate_vendors.py --max-vendors 3 --max-urls-per-vendor 2`

- Full run (all vendors):
  - `G:/My Drive/Gartner/.venv/Scripts/python.exe research_validate_vendors.py --max-urls-per-vendor 3 --sleep-seconds 0.5`

## Notes
- This is a starting point: it *collects evidence* and provides heuristic scoring suggestions.
- Final “validated” scores still require analyst review, especially when the public text is marketing-heavy.
