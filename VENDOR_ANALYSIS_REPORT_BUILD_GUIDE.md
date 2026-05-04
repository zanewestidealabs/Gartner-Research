# Vendor Analysis Report — Complete Build & Data Structure Guide

> **Purpose:** Fully document the Vendor Analysis (VA) report so it can be rebuilt exactly on a new instance for a different purpose. Covers every data structure, API contract, HTML element, CSS class, and JavaScript function.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Data Flow Diagram](#2-data-flow-diagram)
3. [Backend API Contracts](#3-backend-api-contracts)
4. [Application State (`appState`)](#4-application-state-appstate)
5. [Vendor Data Structure](#5-vendor-data-structure)
6. [HTML Template](#6-html-template)
7. [CSS Stylesheet](#7-css-stylesheet)
8. [JavaScript — Supporting Utility Functions](#8-javascript--supporting-utility-functions)
9. [JavaScript — VA Report Functions](#9-javascript--va-report-functions)
10. [Benchmark Computation](#10-benchmark-computation)
11. [Tab 1: Executive Summary](#11-tab-1-executive-summary)
12. [Tab 2: Pillar Scorecard](#12-tab-2-pillar-scorecard)
13. [Tab 3: Strengths & Weaknesses](#13-tab-3-strengths--weaknesses)
14. [Tab 4: Gap Analysis](#14-tab-4-gap-analysis)
15. [Tab 5: Priorities & Roadmap](#15-tab-5-priorities--roadmap)
16. [Tab 6: Capability Legend](#16-tab-6-capability-legend)
17. [Export to Standalone HTML](#17-export-to-standalone-html)
18. [Color System](#18-color-system)
19. [Rebuild Checklist](#19-rebuild-checklist)

---

## 1. Architecture Overview

The VA report is a **single-page JavaScript component** rendered inside a Flask/Jinja2 application. It has zero build tooling — all JS is vanilla ES6 in one file, all CSS is a single stylesheet.

```
┌──────────────────────────────────────────────────┐
│  Flask Backend (app.py)                           │
│    /api/metadata   → pillars, sub-pillars, schema │
│    /api/schema-detail → full schema definitions    │
│    /api/vendors    → vendor data array             │
└───────────────┬──────────────────────────────────┘
                │ JSON fetch on page load
                ▼
┌──────────────────────────────────────────────────┐
│  Client State (appState)                          │
│    .pillarsGrouped[]  — pillar+sub-pillar tree     │
│    .schemaDetail      — enriched schema reference  │
│    .vendors[]         — all vendor records          │
│    .scoreMode         — which score layer to read   │
│    ._vaBenchmarks     — computed benchmark cache    │
└───────────────┬──────────────────────────────────┘
                │ populateVendorAnalysisReport()
                ▼
┌──────────────────────────────────────────────────┐
│  VA Report UI                                     │
│    Vendor dropdown → _vaRenderReport(vendor)       │
│    6 inner tabs, each rendered by its own function │
│    Export → standalone HTML download               │
└──────────────────────────────────────────────────┘
```

**Files involved:**
| File | What | Lines (approximate) |
|------|------|-----|
| `templates/index.html` | HTML template with VA panel | ~40 lines of VA markup |
| `static/app.js` | All VA JavaScript | Lines 9720–10731 (~1,010 lines) |
| `static/app.js` | Supporting functions used by VA | Lines 860–1100, 263–272, 5644–5655 |
| `static/style.css` | All VA CSS | Lines 4951–5528 (~578 lines) |

---

## 2. Data Flow Diagram

```
Page Load
    │
    ├─ fetch('/api/metadata')
    │     → appState.pillarsGrouped = response.pillars_grouped
    │     → appState.fieldMetadata, scoreLegend, schemaIntent, etc.
    │
    ├─ fetch('/api/schema-detail')  (lazy, on first need)
    │     → appState.schemaDetail = response
    │
    └─ fetch('/api/vendors')
          → appState.vendors = response
          → appState._vaBenchmarks = null  (cache cleared on vendor reload)

User clicks "Vendor Analysis" report tab
    │
    └─ populateVendorAnalysisReport()
          ├─ computeVABenchmarks()  — caches in appState._vaBenchmarks
          ├─ Rebuilds <select> dropdown from appState.vendors
          └─ Attaches change + tab-switch listeners (once)

User selects a vendor from dropdown
    │
    └─ _vaRenderReport(vendor)
          ├─ _vaRenderExecSummary(vendor, bm)    → Tab 1
          ├─ _vaRenderPillarScorecard(vendor, bm) → Tab 2
          ├─ _vaRenderStrengthsWeaknesses(v, bm)  → Tab 3
          ├─ _vaRenderGapAnalysis(vendor, bm)      → Tab 4
          ├─ _vaRenderRoadmap(vendor, bm)          → Tab 5
          └─ _vaRenderCapabilityLegend()           → Tab 6
```

---

## 3. Backend API Contracts

### `/api/metadata` (GET)

Called on page load. Returns the schema structure.

```json
{
  "pillars_grouped": [
    {
      "code": "TDR",
      "name": "Threat Detection & Response",
      "description": "Capabilities around detection...",
      "sub_pillars": [
        {
          "id": "TDR-01",
          "name": "Real-Time Threat Detection",
          "definition": "Ability to detect threats in real time...",
          "activities": ["Monitor network traffic", "Analyze logs"]
        },
        { "id": "TDR-02", "name": "...", "definition": "...", "activities": [] }
      ],
      "ai_evidence_signals": ["ML detection models", "Automated triage"]
    }
  ],
  "field_metadata": { ... },
  "score_legend": { ... },
  "schema_intent": "string description of schema purpose",
  "schema_file": "MDR_Services_Schema.json",
  "pricing_evaluation": { ... },
  "pricing_score_legend": { ... }
}
```

**Critical fields for VA:**
- `pillars_grouped[].code` — pillar code (e.g., "TDR")
- `pillars_grouped[].name` — display name
- `pillars_grouped[].sub_pillars[].id` — sub-pillar ID (e.g., "TDR-01")
- `pillars_grouped[].sub_pillars[].name` — sub-pillar display name
- `pillars_grouped[].sub_pillars[].definition` — sub-pillar description
- `pillars_grouped[].sub_pillars[].activities[]` — evaluation criteria list
- `pillars_grouped[].ai_evidence_signals[]` — evidence signal tags

### `/api/schema-detail` (GET)

Returns enriched schema definitions (used by the Capability Legend tab).

```json
{
  "pillars": [
    {
      "code": "TDR",
      "name": "...",
      "focus": "...",
      "validated_pillar_score_rule": "Average of sub-pillar scores",
      "ai_evidence_signals": ["..."],
      "evidence_signals": ["..."]
    }
  ],
  "sub_pillars": [
    {
      "id": "TDR-01",
      "name": "...",
      "expanded_definition": "...",
      "what_to_verify_publicly": ["Check vendor docs for...", "..."],
      "ai_evaluation_criteria": ["Criterion 1", "Criterion 2"],
      "ai_specific_evidence": ["Evidence type 1", "..."]
    }
  ]
}
```

### `/api/vendors` (GET)

Returns the vendor data array. Structure documented in [Section 5](#5-vendor-data-structure).

---

## 4. Application State (`appState`)

Defined at the top of `app.js` as a global `const`:

```javascript
const appState = {
    vendors: [],              // Array of vendor objects
    pillarsGrouped: [],       // From /api/metadata → pillars_grouped
    originalPillarsGrouped: null,  // Backup when in pricing mode
    schemaDetail: null,       // From /api/schema-detail (lazy loaded)
    scoreMode: 'validated',   // Which score layer: validated | researched |
                              //   ai_researched | evidence_refined |
                              //   v2_1_consolidated | v2_researched |
                              //   pricing_v2 | current
    _vaBenchmarks: null,      // Cached benchmark object (cleared on schema/vendor change)
    subPillars: [],           // Flat list: [{ id, name, pillar, pillar_code }]
    pillarMetadata: {},       // { CODE: "Pillar Name" }
    fieldMetadata: {},        // From metadata API
    scoreLegend: {},          // From metadata API
    currentSchemaFileName: '',
    currentSchema: '',        // Used in export for label
    schemaIntent: '',
    pricingEvaluation: null,
    // ...other fields not used by VA
};
```

**`_vaBenchmarks` is cleared when:**
- Schema is switched (line ~2545)
- Vendors are reloaded (line ~2614)
- This forces `computeVABenchmarks()` to recalculate on next access.

---

## 5. Vendor Data Structure

Each vendor is a JSON object in the `appState.vendors[]` array. The VA report reads these fields:

### Core Identity Fields
```json
{
  "vendor": "CrowdStrike",
  "headquarters": "Austin, TX, USA",
  "year_founded": 2011,
  "employee_count_range": "5,000-10,000",
  "target_market": "Enterprise, Mid-Market",
  "description": "Cloud-native endpoint and MDR platform...",
  "capability_coverage": ["EDR", "NDR", "XDR"]
}
```

### Optional Type Fields (displayed if present)
```json
{
  "mdr_service_type": "Pure-Play MDR",
  "ir_focus_type": "Full IR",
  "product_type": "Platform-based",
  "platform_type": "XDR"
}
```

### Pillar Scores (top-level per-pillar averages)
The VA reads pillar scores based on `appState.scoreMode`. Precedence per mode:

| scoreMode | Primary Field | Fallback |
|-----------|--------------|----------|
| `validated` | `pillar_scores_validated` | `pillar_scores` |
| `researched` | `pillar_scores_researched` | compute from granular |
| `ai_researched` | `pillar_scores_ai_researched` | compute from granular |
| `evidence_refined` | `pillar_scores_evidence_refined` | compute from granular |
| `v2_researched` | `pillar_scores_v2_researched` | compute from granular |
| `v2_1_consolidated` | `pillar_scores_v2_1` | compute from granular |
| `current` | `pillar_scores` | compute from granular |
| `pricing_v2` | `pricing_dimension_scores_v2` | `pricing_dimension_scores` |

Shape: `{ "TDR": 4.13, "PTI": 3.75, ... }`

### Sub-Pillar Scores (granular per-sub-pillar)
Flat mapping of sub-pillar ID → numeric score:

```json
{
  "sub_pillar_scores_v2_1": {
    "TDR-01": 4.25,
    "TDR-02": 4.00,
    "TDR-03": 4.50,
    "TDR-04": 3.75,
    "PTI-01": 3.50,
    ...
  }
}
```

Available under mode-matched field names:
- `sub_pillar_scores_validated`
- `sub_pillar_scores_researched`
- `sub_pillar_scores_ai_researched`
- `sub_pillar_scores_evidence_refined`
- `sub_pillar_scores_v2_researched`
- `sub_pillar_scores_v2_1`
- `sub_pillar_scores_current`

Also accepted: `granular_mapping` / `granular_mapping_validated` (nested format `{ PILLAR: { SP_ID: score } }`).

### Sub-Pillar Rationale (per-sub-pillar rich assessment)

```json
{
  "sub_pillar_rationale_v2_1": {
    "TDR-01": {
      "sub_pillar_id": "TDR-01",
      "sub_pillar_name": "Real-Time Threat Detection",
      "original_score": 4.0,
      "evidence_score": 4.25,
      "adjusted_score": 4.25,
      "adjustment_type": "increase",
      "adjustment_reason": "Strong evidence of ML-based detection...",
      "scoring_level": "advanced",
      "criteria_assessment": [
        {
          "criterion": "Automated detection within 15 minutes",
          "status": "met",
          "evidence": "Vendor documentation states ..."
        },
        {
          "criterion": "Integration with 3+ SIEM platforms",
          "status": "partial",
          "evidence": "Two integrations confirmed..."
        },
        {
          "criterion": "Custom detection rule authoring",
          "status": "unmet",
          "evidence": ""
        }
      ],
      "evidence_breakdown": "...",
      "evidence_quality_factor": 0.85,
      "evidence_quality_grade": "B",
      "confidence": "high",
      "excerpt_count": 12
    }
  }
}
```

Fallback chain: `sub_pillar_rationale_v2_1` → `sub_pillar_rationale_v2_researched` → `sub_pillar_rationale`.

**Used by:** Strengths & Weaknesses (criteria_assessment, evidence_quality_grade, adjustment_reason), Roadmap (criteria_assessment for actions), Pillar Scorecard (evidence_quality_grade), Executive Summary (excerpt_count).

### Adjustment Summary
```json
{
  "v2_1_adjustment_summary": {
    "increased": 12,
    "decreased": 5,
    "validated": 8,
    "no_change": 7,
    "total": 32
  }
}
```

### Research Confidence
```json
{
  "research_confidence": "medium",
  "research_confidence_v2_1": "high"
}
```

### Sub-Pillar Schema Labels (fallback for display names)
```json
{
  "sub_pillar_schema_labels": {
    "TDR-01": "Real-Time Threat Detection",
    "TDR-02": "Advanced Analytics"
  }
}
```

---

## 6. HTML Template

Place this inside your report panel container. The VA report is activated when a "Vendor Analysis" report tab button is clicked.

```html
<!-- Vendor Analysis Report Panel -->
<div id="report-panel-vendor-analysis" class="report-panel">
    <div class="report-document">
        <div class="report-doc-header">
            <div class="report-doc-header-row">
                <h1>Vendor Analysis Report</h1>
                <button class="report-export-btn" onclick="exportVendorAnalysisHTML()" title="Export as standalone HTML">
                    <span class="icon">🌐</span> Export HTML
                </button>
            </div>
            <p class="report-doc-subtitle">Select a vendor to view capability analysis, gap assessment, and improvement roadmap.</p>
        </div>
        <div class="va-vendor-selector">
            <label for="va-vendor-dropdown">Select Vendor:</label>
            <select id="va-vendor-dropdown"><option value="">-- Choose a vendor --</option></select>
        </div>
        <div class="va-inner-tabs" id="va-inner-tabs" style="display:none;">
            <button class="va-inner-tab active" data-va-tab="exec-summary" type="button">Executive Summary</button>
            <button class="va-inner-tab" data-va-tab="pillar-scorecard" type="button">Pillar Scorecard</button>
            <button class="va-inner-tab" data-va-tab="strengths-weaknesses" type="button">Strengths &amp; Weaknesses</button>
            <button class="va-inner-tab" data-va-tab="gap-analysis" type="button">Gap Analysis</button>
            <button class="va-inner-tab" data-va-tab="roadmap" type="button">Priorities &amp; Roadmap</button>
            <button class="va-inner-tab" data-va-tab="capability-legend" type="button">Capability Legend</button>
        </div>
        <div id="va-tab-content">
            <div id="va-panel-exec-summary" class="va-inner-panel active"></div>
            <div id="va-panel-pillar-scorecard" class="va-inner-panel"></div>
            <div id="va-panel-strengths-weaknesses" class="va-inner-panel"></div>
            <div id="va-panel-gap-analysis" class="va-inner-panel"></div>
            <div id="va-panel-roadmap" class="va-inner-panel"></div>
            <div id="va-panel-capability-legend" class="va-inner-panel"></div>
        </div>
    </div>
</div>
```

**Activation trigger:** The report tab system calls `populateVendorAnalysisReport()` when `tabId === 'vendor-analysis'`:

```javascript
// In the report tab click handler:
} else if (tabId === 'vendor-analysis') {
    populateVendorAnalysisReport();
}
```

**Required tab button (elsewhere in your nav):**
```html
<button class="report-tab-btn" data-report-tab="vendor-analysis">Vendor Analysis</button>
```

---

## 7. CSS Stylesheet

All 578 lines of VA-specific CSS. Copy this block in its entirety.

```css
/* =============================================
   VENDOR ANALYSIS REPORT — Complete CSS
   ============================================= */

/* Vendor Selector */
.va-vendor-selector {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid var(--border-color, #e0e0e0);
    margin-bottom: 8px;
}
.va-vendor-selector label {
    font-weight: 600;
    font-size: 14px;
    color: var(--text-primary, #1a1a1a);
    white-space: nowrap;
}
.va-vendor-selector select {
    flex: 1;
    max-width: 400px;
    padding: 8px 12px;
    border: 1px solid var(--border-color, #d0d0d0);
    border-radius: 6px;
    font-size: 14px;
    background: var(--bg-primary, #fff);
    color: var(--text-primary, #1a1a1a);
}

/* Inner tabs */
.va-inner-tabs {
    display: flex;
    gap: 4px;
    padding: 8px 0 0 0;
    border-bottom: 2px solid var(--border-color, #e0e0e0);
    margin-bottom: 16px;
    flex-wrap: wrap;
}
.va-inner-tab {
    padding: 8px 16px;
    border: none;
    background: none;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-secondary, #666);
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all 0.15s;
    white-space: nowrap;
}
.va-inner-tab:hover {
    color: var(--text-primary, #1a1a1a);
    background: var(--bg-hover, rgba(0,0,0,0.03));
}
.va-inner-tab.active {
    color: #005a9e;
    border-bottom-color: #005a9e;
    font-weight: 600;
}
.va-inner-panel { display: none; }
.va-inner-panel.active { display: block; }

/* Executive Summary */
.va-exec-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 20px;
}
.va-exec-card {
    background: var(--bg-secondary, #f8f9fa);
    border: 1px solid var(--border-color, #e0e0e0);
    border-radius: 8px;
    padding: 16px;
}
.va-exec-card h3 {
    margin: 0 0 10px 0;
    font-size: 14px;
    color: var(--text-secondary, #666);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.va-exec-card .va-big-score {
    font-size: 36px;
    font-weight: 700;
    line-height: 1;
}
.va-exec-card .va-meta-row {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    font-size: 13px;
    color: var(--text-secondary, #666);
    margin-top: 6px;
}
.va-exec-card .va-meta-row span { white-space: nowrap; }
.va-exec-card .va-meta-label {
    font-weight: 600;
    color: var(--text-primary, #1a1a1a);
}

/* Radar Chart */
.va-radar-container {
    display: flex;
    justify-content: center;
    padding: 12px 0;
}
.va-radar-container canvas {
    max-width: 460px;
    max-height: 460px;
}
.va-radar-legend {
    display: flex;
    justify-content: center;
    gap: 24px;
    margin-top: 8px;
    font-size: 12px;
    color: var(--text-secondary, #666);
}
.va-radar-legend span {
    display: flex;
    align-items: center;
    gap: 6px;
}
.va-radar-legend .swatch {
    display: inline-block;
    width: 16px;
    height: 3px;
    border-radius: 2px;
}

/* Quick Callout Boxes */
.va-quick-callout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 16px;
}
.va-callout-box {
    padding: 14px;
    border-radius: 8px;
    border: 1px solid;
}
.va-callout-box.strengths {
    background: rgba(16, 124, 16, 0.06);
    border-color: rgba(16, 124, 16, 0.2);
}
.va-callout-box.weaknesses {
    background: rgba(209, 52, 56, 0.06);
    border-color: rgba(209, 52, 56, 0.2);
}
.va-callout-box h4 {
    margin: 0 0 8px 0;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}
.va-callout-box.strengths h4 { color: #107c10; }
.va-callout-box.weaknesses h4 { color: #d13438; }
.va-callout-box ul {
    margin: 0;
    padding-left: 18px;
    font-size: 13px;
    line-height: 1.6;
}

/* Pillar Scorecard */
.va-pillar-card {
    margin-bottom: 20px;
    border: 1px solid var(--border-color, #e0e0e0);
    border-radius: 8px;
    overflow: hidden;
}
.va-pillar-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: var(--bg-secondary, #f8f9fa);
    border-bottom: 1px solid var(--border-color, #e0e0e0);
    cursor: pointer;
}
.va-pillar-card-header:hover {
    background: var(--bg-hover, rgba(0,0,0,0.04));
}
.va-pillar-title {
    display: flex;
    align-items: center;
    gap: 10px;
}
.va-pillar-code {
    font-size: 12px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
    color: #fff;
    background: #005a9e;
}
.va-pillar-name {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary, #1a1a1a);
}
.va-pillar-scores {
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 13px;
}
.va-pillar-score-badge {
    font-size: 18px;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 6px;
    color: #fff;
}
.va-pillar-benchmark {
    color: var(--text-secondary, #666);
}
.va-pillar-body {
    padding: 12px 16px;
}
.va-sp-row {
    display: grid;
    grid-template-columns: 120px 1fr 60px 60px 60px 60px;
    gap: 8px;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border-color, #f0f0f0);
    font-size: 13px;
}
.va-sp-row:last-child { border-bottom: none; }
.va-sp-id {
    font-weight: 600;
    font-size: 12px;
    color: var(--text-secondary, #666);
}
.va-sp-name {
    color: var(--text-primary, #1a1a1a);
}
.va-sp-score {
    font-weight: 700;
    text-align: center;
    padding: 2px 6px;
    border-radius: 4px;
    color: #fff;
    font-size: 12px;
}
.va-sp-benchmark-val {
    text-align: center;
    font-size: 12px;
    color: var(--text-secondary, #666);
}
.va-sp-grade {
    text-align: center;
    font-weight: 600;
    font-size: 12px;
}
.va-grade-A { color: #005a9e; }
.va-grade-B { color: #107c10; }
.va-grade-C { color: #c19c00; }
.va-grade-D { color: #ff8c00; }
.va-grade-F { color: #d13438; }

/* Score bar (unused in current VA but available) */
.va-score-bar-wrap {
    position: relative;
    height: 8px;
    background: var(--bg-tertiary, #e8e8e8);
    border-radius: 4px;
    overflow: visible;
}
.va-score-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s;
}
.va-benchmark-marker {
    position: absolute;
    top: -3px;
    width: 2px;
    height: 14px;
    border-radius: 1px;
}
.va-benchmark-marker.avg { background: rgba(0,0,0,0.35); }
.va-benchmark-marker.top10 { background: #005a9e; }

/* Strengths & Weaknesses */
.va-sw-section { margin-bottom: 24px; }
.va-sw-section h3 {
    font-size: 16px;
    margin: 0 0 12px 0;
    padding-bottom: 6px;
    border-bottom: 2px solid;
}
.va-sw-section.strengths h3 { color: #107c10; border-color: #107c10; }
.va-sw-section.weaknesses h3 { color: #d13438; border-color: #d13438; }
.va-sw-card {
    padding: 12px 16px;
    margin-bottom: 10px;
    border: 1px solid var(--border-color, #e0e0e0);
    border-radius: 8px;
    border-left: 4px solid;
}
.va-sw-card.strength { border-left-color: #107c10; }
.va-sw-card.weakness { border-left-color: #d13438; }
.va-sw-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}
.va-sw-card-title {
    font-weight: 600;
    font-size: 14px;
    color: var(--text-primary, #1a1a1a);
}
.va-sw-card-scores {
    font-size: 12px;
    color: var(--text-secondary, #666);
    display: flex;
    gap: 10px;
}
.va-sw-card-body {
    font-size: 13px;
    color: var(--text-secondary, #555);
    line-height: 1.5;
}
.va-sw-card-body ul {
    margin: 4px 0 0 0;
    padding-left: 18px;
}
.va-sw-card-body .va-evidence-tag {
    display: inline-block;
    padding: 1px 6px;
    background: var(--bg-tertiary, #eee);
    border-radius: 3px;
    font-size: 11px;
    margin: 2px 2px 2px 0;
}

/* Gap Analysis Table */
.va-gap-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
.va-gap-table th {
    background: var(--bg-secondary, #f8f9fa);
    padding: 8px 10px;
    text-align: left;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    color: var(--text-secondary, #666);
    border-bottom: 2px solid var(--border-color, #e0e0e0);
}
.va-gap-table td {
    padding: 7px 10px;
    border-bottom: 1px solid var(--border-color, #f0f0f0);
}
.va-gap-table tr:hover td {
    background: var(--bg-hover, rgba(0,0,0,0.02));
}
.va-gap-table .va-gap-cell {
    text-align: center;
    font-weight: 600;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}
.va-gap-above-top10 { background: rgba(0, 90, 158, 0.1); color: #005a9e; }
.va-gap-above-avg { background: rgba(16, 124, 16, 0.1); color: #107c10; }
.va-gap-at-avg { background: rgba(193, 156, 0, 0.1); color: #c19c00; }
.va-gap-below-avg { background: rgba(209, 52, 56, 0.1); color: #d13438; }

/* Roadmap */
.va-roadmap-phase {
    margin-bottom: 24px;
    border: 1px solid var(--border-color, #e0e0e0);
    border-radius: 8px;
    overflow: hidden;
}
.va-phase-header {
    padding: 12px 16px;
    font-weight: 700;
    font-size: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.va-phase-header.phase1 { background: #e6f2e6; color: #107c10; }
.va-phase-header.phase2 { background: #fff8e1; color: #c19c00; }
.va-phase-header.phase3 { background: #e8f0fe; color: #005a9e; }
.va-phase-items { padding: 8px 16px; }
.va-roadmap-item {
    display: grid;
    grid-template-columns: 100px 1fr 60px 60px 60px;
    gap: 8px;
    align-items: start;
    padding: 10px 0;
    border-bottom: 1px solid var(--border-color, #f0f0f0);
    font-size: 13px;
}
.va-roadmap-item:last-child { border-bottom: none; }
.va-roadmap-sp-id {
    font-weight: 600;
    font-size: 12px;
    color: var(--text-secondary, #666);
}
.va-roadmap-detail { line-height: 1.5; }
.va-roadmap-detail .va-action-label {
    font-weight: 600;
    color: var(--text-primary, #1a1a1a);
}
.va-roadmap-detail .va-actions {
    margin: 2px 0 0 0;
    padding-left: 16px;
    color: var(--text-secondary, #555);
    font-size: 12px;
}
.va-roadmap-score-cell {
    text-align: center;
    font-weight: 600;
    font-size: 12px;
}
.va-priority-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}
.va-priority-high { background: rgba(209, 52, 56, 0.12); color: #d13438; }
.va-priority-medium { background: rgba(193, 156, 0, 0.12); color: #c19c00; }
.va-priority-low { background: rgba(16, 124, 16, 0.12); color: #107c10; }

/* Summary Stats Row */
.va-summary-stats {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin: 12px 0;
}
.va-stat {
    background: var(--bg-secondary, #f8f9fa);
    border: 1px solid var(--border-color, #e0e0e0);
    border-radius: 8px;
    padding: 10px 16px;
    text-align: center;
    min-width: 120px;
}
.va-stat-value {
    font-size: 22px;
    font-weight: 700;
    line-height: 1.2;
}
.va-stat-label {
    font-size: 11px;
    color: var(--text-secondary, #666);
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-top: 2px;
}

/* Responsive */
@media (max-width: 900px) {
    .va-exec-grid { grid-template-columns: 1fr; }
    .va-quick-callout { grid-template-columns: 1fr; }
    .va-sp-row { grid-template-columns: 80px 1fr 50px 50px 50px; }
    .va-roadmap-item { grid-template-columns: 80px 1fr 50px 50px 50px; }
}

/* Capability Legend */
.va-legend-pillar {
    margin-bottom: 12px;
    border: 1px solid var(--border-color, #e0e0e0);
    border-radius: 8px;
    overflow: hidden;
}
.va-legend-pillar-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    background: var(--bg-secondary, #f8f9fa);
    border-bottom: 1px solid var(--border-color, #e0e0e0);
    cursor: pointer;
    user-select: none;
    transition: background 0.15s;
}
.va-legend-pillar-header:hover {
    background: var(--bg-hover, rgba(0,0,0,0.04));
}
.va-legend-pillar-header .va-chevron {
    font-size: 12px;
    transition: transform 0.2s;
    color: var(--text-secondary, #666);
    flex-shrink: 0;
}
.va-legend-pillar-header.expanded .va-chevron {
    transform: rotate(90deg);
}
.va-legend-pillar-body {
    display: none;
    padding: 12px 16px;
}
.va-legend-pillar-body.expanded {
    display: block;
}
.va-legend-sp-card {
    margin-bottom: 14px;
    padding: 12px;
    background: var(--bg-primary, #fff);
    border: 1px solid var(--border-color, #f0f0f0);
    border-radius: 6px;
    border-left: 3px solid #005a9e;
}
.va-legend-sp-card:last-child { margin-bottom: 0; }
.va-legend-sp-header {
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin-bottom: 6px;
}
.va-legend-sp-id {
    font-size: 11px;
    font-weight: 700;
    color: #005a9e;
    background: rgba(0,90,158,0.08);
    padding: 2px 6px;
    border-radius: 3px;
}
.va-legend-sp-name {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary, #1a1a1a);
}
.va-legend-sp-def {
    font-size: 13px;
    color: var(--text-secondary, #555);
    margin-bottom: 8px;
    line-height: 1.5;
}
.va-legend-section-label {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    color: var(--text-secondary, #888);
    margin: 8px 0 4px 0;
}
.va-legend-criteria-list {
    margin: 0;
    padding-left: 18px;
    font-size: 12px;
    line-height: 1.6;
    color: var(--text-secondary, #555);
}
.va-legend-focus {
    font-size: 13px;
    color: var(--text-secondary, #666);
    font-style: italic;
    margin-bottom: 6px;
}
.va-legend-signals {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 4px;
}
.va-legend-signal-tag {
    display: inline-block;
    padding: 2px 8px;
    background: rgba(0,90,158,0.06);
    border: 1px solid rgba(0,90,158,0.15);
    border-radius: 3px;
    font-size: 11px;
    color: #005a9e;
}
```

**Required CSS Custom Properties (set on `:root` or the parent):**
```css
:root {
    --text-primary: #1a1a1a;
    --text-secondary: #666;
    --bg-primary: #fff;
    --bg-secondary: #f8f9fa;
    --bg-tertiary: #e8e8e8;
    --bg-hover: rgba(0,0,0,0.03);
    --border-color: #e0e0e0;
}
```

---

## 8. JavaScript — Supporting Utility Functions

These are used by VA but defined elsewhere in app.js. You must include them.

### `escapeHtml(value)`
```javascript
function escapeHtml(value) {
    const s = String(value ?? '');
    return s
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
```

### `getScoreColor(score)`
Returns a hex color string based on the 1–5 scoring scale:

```javascript
function getScoreColor(score) {
    if (score == null || isNaN(score)) return 'var(--text-secondary)';
    const s = Number(score);
    if (s >= 4)   return '#005a9e';   // blue — best-in-class
    if (s >= 3)   return '#107c10';   // green — advanced
    if (s >= 2)   return '#c19c00';   // gold — developing
    if (s >= 1)   return '#ff8c00';   // orange — basic
    return '#d13438';                 // red — minimal
}
```

### `getEffectiveGranularMapping(vendor)`
Returns the nested granular mapping `{ PILLAR: { SP_ID: score } }` for the current score mode. Full logic:

```javascript
function getEffectiveGranularMapping(vendor) {
    const mode = appState.scoreMode || 'validated';

    if (mode === 'pricing_v2') {
        const out = {};
        getActivePillarCodes().forEach(p => { out[p] = {}; });
        return out;
    }

    // Mode-specific flat sub-pillar score fields → converted via buildGranularMappingFromSubScores
    if (mode === 'v2_1_consolidated' && vendor.sub_pillar_scores_v2_1)
        return buildGranularMappingFromSubScores(vendor.sub_pillar_scores_v2_1);
    if (mode === 'v2_researched' && vendor.sub_pillar_scores_v2_researched)
        return buildGranularMappingFromSubScores(vendor.sub_pillar_scores_v2_researched);
    if (mode === 'evidence_refined' && vendor.sub_pillar_scores_evidence_refined)
        return buildGranularMappingFromSubScores(vendor.sub_pillar_scores_evidence_refined);
    if (mode === 'ai_researched' && vendor.sub_pillar_scores_ai_researched)
        return buildGranularMappingFromSubScores(vendor.sub_pillar_scores_ai_researched);
    if (mode === 'researched' && vendor.sub_pillar_scores_researched)
        return buildGranularMappingFromSubScores(vendor.sub_pillar_scores_researched);

    if (mode === 'current') {
        if (vendor.granular_mapping || vendor.granular_mapping_validated)
            return vendor.granular_mapping || vendor.granular_mapping_validated;
        if (vendor.sub_pillar_scores_current)
            return buildGranularMappingFromSubScores(vendor.sub_pillar_scores_current);
        if (vendor.sub_pillar_scores_validated)
            return buildGranularMappingFromSubScores(vendor.sub_pillar_scores_validated);
        return {};
    }

    // validated mode (default)
    if (vendor.granular_mapping_validated) return vendor.granular_mapping_validated;
    if (vendor.granular_mapping) return vendor.granular_mapping;
    if (vendor.sub_pillar_scores_validated)
        return buildGranularMappingFromSubScores(vendor.sub_pillar_scores_validated);
    if (vendor.sub_pillar_scores_researched)
        return buildGranularMappingFromSubScores(vendor.sub_pillar_scores_researched);
    if (vendor.sub_pillar_scores_current)
        return buildGranularMappingFromSubScores(vendor.sub_pillar_scores_current);
    return {};
}
```

### `buildGranularMappingFromSubScores(subScores)`
Converts a flat `{ SP_ID: score }` map to nested `{ PILLAR: { SP_ID: score } }` by splitting sub-pillar IDs on `-` to derive the pillar code:

```javascript
function buildGranularMappingFromSubScores(subScores) {
    const out = {};
    getActivePillarCodes().forEach(p => { out[p] = {}; });
    if (!subScores || typeof subScores !== 'object') return out;
    Object.entries(subScores).forEach(([sid, v]) => {
        if (!sid || typeof sid !== 'string') return;
        const pillar = sid.split('-')[0];
        if (!out[pillar]) out[pillar] = {};
        if (v === undefined || v === null || v === '' || Number.isNaN(Number(v))) return;
        out[pillar][sid] = Number(v);
    });
    return out;
}
```

**Convention:** Sub-pillar IDs **must** follow the pattern `PILLAR-NN` (e.g., `TDR-01`). The pillar code is the prefix before the first hyphen.

### `getEffectivePillarScores(vendor)`
Returns `{ PILLAR_CODE: score }` for the current score mode. Falls back through named properties, then tries computing from granular sub-pillar averages.

```javascript
function getEffectivePillarScores(vendor) {
    const mode = appState.scoreMode || 'validated';

    if (mode === 'pricing_v2') {
        return vendor.pricing_dimension_scores_v2 || vendor.pricing_dimension_scores || {};
    }

    // Direct property lookup by mode
    const modeToField = {
        v2_1_consolidated: 'pillar_scores_v2_1',
        v2_researched: 'pillar_scores_v2_researched',
        evidence_refined: 'pillar_scores_evidence_refined',
        ai_researched: 'pillar_scores_ai_researched',
        researched: 'pillar_scores_researched',
        validated: 'pillar_scores_validated',   // falls back to pillar_scores
        current: 'pillar_scores'
    };

    const field = modeToField[mode];
    if (field && vendor[field] && typeof vendor[field] === 'object') return vendor[field];
    if (mode === 'validated' && vendor.pillar_scores) return vendor.pillar_scores;

    // Final fallback: compute from granular mapping averages
    const computed = {};
    getActivePillarCodes().forEach(p => {
        const v = computePillarScoreFromGranular(vendor, p);
        if (v !== null) computed[p] = v;
    });
    return Object.keys(computed).length > 0 ? computed : (vendor.pillar_scores || {});
}
```

### `getActivePillarCodes()`
```javascript
function getActivePillarCodes() {
    const groups = appState.pillarsGrouped || [];
    if (Array.isArray(groups) && groups.length > 0) {
        return groups.map(g => g.code);
    }
    return ['PLA', 'INV', 'REM', 'PMG', 'LAW']; // fallback
}
```

---

## 9. JavaScript — VA Report Functions

Complete listing of all 21 VA-specific functions. Each is documented with its signature, inputs, and DOM target.

### Helper Functions (internal)

| Function | Purpose |
|----------|---------|
| `_vaGetPillarCodes()` | Returns `appState.pillarsGrouped.map(g => g.code)` |
| `_vaGetPillarName(code)` | Looks up pillar display name from pillarsGrouped |
| `_vaGetPillarImportance(code)` | Returns weight: 1.2 for first pillar, 1.1 for second and last, 1.0 otherwise |
| `_vaGetSubPillarIds()` | Flattens all sub-pillar IDs across all pillars |
| `_vaGetSubPillarIdsForPillar(code)` | Gets sub-pillar IDs for one pillar |
| `_vaFlattenGranular(nested)` | Converts `{ PILLAR: { SP: score } }` → flat `{ SP: score }` |
| `_vaGetVendorScores(vendor)` | Returns `{ sp: flatGranular, p: pillarScores }` |
| `_vaGetSpLabel(spId)` | Finds sub-pillar display name from pillarsGrouped, then vendor labels fallback |
| `_vaGetRationale(vendor, spId)` | Returns rationale object with fallback chain |
| `_vaPercentileRank(overallScore, sortedScores)` | Binary count percentile (0–100) |

### Core Functions

| Function | Purpose | DOM Target |
|----------|---------|-----------|
| `computeVABenchmarks()` | Compute and cache market stats | Writes to `appState._vaBenchmarks` |
| `populateVendorAnalysisReport()` | Entry point — builds dropdown, attaches events | `#va-vendor-dropdown` |
| `_vaRenderReport(vendor)` | Orchestrator — shows tabs, calls all 6 renderers | All panels |
| `_vaRenderExecSummary(vendor, bm)` | Executive Summary tab | `#va-panel-exec-summary` |
| `_vaDrawRadar(vendor, bm)` | Canvas radar chart | `#va-radar-canvas` |
| `_vaRenderPillarScorecard(vendor, bm)` | Expandable pillar detail cards | `#va-panel-pillar-scorecard` |
| `_vaRenderStrengthsWeaknesses(vendor, bm)` | Strength/weakness analysis | `#va-panel-strengths-weaknesses` |
| `_vaRenderGapAnalysis(vendor, bm)` | Full gap table | `#va-panel-gap-analysis` |
| `_vaRenderRoadmap(vendor, bm)` | Priority roadmap with phases | `#va-panel-roadmap` |
| `_vaRenderCapabilityLegend()` | Full schema reference with expand/collapse | `#va-panel-capability-legend` |
| `exportVendorAnalysisHTML()` | Generate standalone downloadable HTML | Browser download |

---

## 10. Benchmark Computation

`computeVABenchmarks()` computes statistics across **all vendors** and caches the result.

### Algorithm

```
For each vendor in appState.vendors:
    Get flat sub-pillar scores via _vaFlattenGranular(getEffectiveGranularMapping(vendor))
    Get pillar scores via getEffectivePillarScores(vendor)
    Collect each valid score into per-ID arrays

For each sub-pillar ID:
    marketAvg = mean of all vendor scores for that sub-pillar
    top10Avg = mean of top 10 vendor scores (sorted descending, take first 10)
    count = number of vendors with valid score

For each pillar code:
    marketAvg = mean of all vendor pillar scores
    top10Avg = mean of top 10 vendor pillar scores
    count = number of vendors with valid score

overallScores = sorted array of per-vendor overall averages (mean of all pillar scores)
```

### Output Shape

```javascript
{
    sp: {
        "TDR-01": { marketAvg: 2.85, top10Avg: 4.12, count: 90 },
        "TDR-02": { marketAvg: 2.71, top10Avg: 3.98, count: 88 },
        // ...
    },
    pillar: {
        "TDR": { marketAvg: 2.80, top10Avg: 4.05, count: 92 },
        "PTI": { marketAvg: 2.63, top10Avg: 3.88, count: 91 },
        // ...
    },
    overallScores: [1.23, 1.45, 1.67, ...],  // sorted ascending
    vendorCount: 95
}
```

---

## 11. Tab 1: Executive Summary

**Function:** `_vaRenderExecSummary(vendor, bm)`  
**Target:** `#va-panel-exec-summary`

### Layout

```
┌─────────────────────────────────┬─────────────────────────────┐
│ Vendor Overview Card            │ Overall Score Card          │
│  • Name (18px bold)             │  • Big score (36px, colored)│
│  • HQ, Founded, Employees      │  • Percentile, Confidence   │
│  • Target, Type, IR Focus etc.  │  • Market Average           │
│  • Description                  │                             │
└─────────────────────────────────┴─────────────────────────────┘
┌───────┬───────┬───────┬───────┬───────┐
│Overall│ Pct   │Excerpt│ Up/Dn │ Conf  │  ← Summary Stats Row
│ 3.21  │ 72nd  │ 245   │ 12/5  │ high  │
└───────┴───────┴───────┴───────┴───────┘
         ┌──────────────────────┐
         │    Radar Chart       │  ← 460×460 canvas
         │ (vendor, avg, top10) │
         └──────────────────────┘
         ── Radar Legend ──
┌───────────────────┬────────────────────┐
│ Top Strengths     │ Key Growth Areas   │
│  • TDR — 4.13     │  • AID — 2.13      │
│  • PTI — 3.75     │  • AIO — 2.86      │
│  • DIS — 3.41     │  • IRA — 3.00      │
└───────────────────┴────────────────────┘
```

### Key Computations
- **Overall score:** Mean of all pillar scores for the vendor
- **Percentile:** Count of vendors in `bm.overallScores` below this vendor's overall score, as percentage
- **Top 3 / Bottom 3:** Pillars sorted by score; top 3 shown as strengths, bottom 3 as growth areas
- **Total excerpts:** Sum of `_vaGetRationale(vendor, spId).excerpt_count` across all sub-pillars
- **Up/Down:** From `vendor.v2_1_adjustment_summary.increased` / `.decreased`
- **Confidence:** `vendor.research_confidence_v2_1` → `vendor.research_confidence` → `'N/A'`

### Radar Chart (`_vaDrawRadar`)
Rendered on `<canvas id="va-radar-canvas" width="460" height="460">`.

- 5 concentric grid rings (levels 1–5)
- N axis lines (one per pillar), labels at `R + 25px`
- Three overlaid polygons:
  1. **Top-10 average** — dashed green fill `rgba(16,124,16,0.04)`, stroke `#107c10`
  2. **Market average** — dashed orange fill `rgba(255,140,0,0.06)`, stroke `#ff8c00`
  3. **Vendor** — solid blue fill `rgba(0,90,158,0.12)`, stroke `#005a9e` (line width 2.5)
- Blue dots (radius 4) at vendor data points
- Start angle: `-Math.PI / 2` (top of circle)

---

## 12. Tab 2: Pillar Scorecard

**Function:** `_vaRenderPillarScorecard(vendor, bm)`  
**Target:** `#va-panel-pillar-scorecard`

### Layout

One expandable card per pillar:

```
┌────────────────────────────────────────────────────────────────┐
│ [TDR badge] Threat Detection & Response  Avg:2.80|Top10:4.05  │
│                                          +1.33        [4.13]  │  ← Header (click to expand)
├────────────────────────────────────────────────────────────────┤
│ ID       Sub-Pillar                Score  Avg  Top10  Grade   │  ← Header row
│ TDR-01   Real-Time Threat Det.     [4.25] 2.85 4.12   B      │
│ TDR-02   Advanced Analytics        [4.00] 2.71 3.98   B      │
│ TDR-03   Automated Triage          [4.50] 2.90 4.20   A      │
│ TDR-04   Alert Prioritization      [3.75] 2.65 3.85   C      │
└────────────────────────────────────────────────────────────────┘
```

- Header click toggles body visibility via inline `onclick`
- Badge color = `getScoreColor(pillarScore)`
- Delta = vendor score − market avg; green if ≥0, red if <0
- Grade = `rationale.evidence_quality_grade` (A/B/C/D/-)
- Grade color classes: `.va-grade-A` (blue), `.va-grade-B` (green), `.va-grade-C` (gold), `.va-grade-D` (orange), `.va-grade-F` (red)

---

## 13. Tab 3: Strengths & Weaknesses

**Function:** `_vaRenderStrengthsWeaknesses(vendor, bm)`  
**Target:** `#va-panel-strengths-weaknesses`

### Strength Criteria
A sub-pillar is a **strength** if:
- `score ≥ top10Avg - 0.3` (within 0.3 of top-10), OR
- `score ≥ marketAvg + 0.5` AND grade is A or B

Sorted by `(score - top10Avg)` descending. Capped at 12 cards.

### Weakness Criteria
A sub-pillar is a **weakness** if:
- `score < marketAvg - 0.3` (below market avg by >0.3), OR
- `(top10Avg - score) >= 1.0` (gap to top-10 ≥ 1.0)

Sorted by `(top10Avg - score)` descending. Capped at 12 cards.

### Card Content
Each card shows:
- Sub-pillar ID and name
- Score (colored), delta vs avg, delta vs top-10, evidence grade
- Number of criteria met / total
- Adjustment reason text (from rationale)
- Top 3 met criteria (for strengths) or unmet/partial criteria (for weaknesses)

---

## 14. Tab 4: Gap Analysis

**Function:** `_vaRenderGapAnalysis(vendor, bm)`  
**Target:** `#va-panel-gap-analysis`

### Summary Stats Row
- Count of sub-pillars: Above Top-10, Above Avg, Below Avg, Total

### Status Levels
| Condition | Level | Label | CSS Class |
|-----------|-------|-------|-----------|
| `score ≥ top10Avg` | above-top10 | Leader | `.va-gap-above-top10` |
| `score ≥ marketAvg` | above-avg | Above Avg | `.va-gap-above-avg` |
| `score ≥ marketAvg - 0.3` | at-avg | At Avg | `.va-gap-at-avg` |
| else | below-avg | Below Avg | `.va-gap-below-avg` |

### Table
Sorted by `gapTop10` ascending (largest gaps first — most negative values on top).

Columns: Pillar Code, Sub-Pillar Name, Score, Market Avg, Top-10 Avg, Gap to Avg, Gap to Top-10, Status Badge

Pillar change boundaries get `border-top: 2px solid`.

---

## 15. Tab 5: Priorities & Roadmap

**Function:** `_vaRenderRoadmap(vendor, bm)`  
**Target:** `#va-panel-roadmap`

### Priority Algorithm

For each sub-pillar with `gapTop10 > 0.1`:

```
gapFactor     = max(gapTop10, 0) × 2
importanceFac = pillarImportance × 1.5 × (gapAvg > 0 ? 1.2 : 0.5)
feasibility   = partialCriteria.length × 0.3 + (unmetExists ? 0.2 : 0)
priorityScore = gapFactor + importanceFac + feasibility
```

Where `pillarImportance` = `_vaGetPillarImportance(pillarCode)`:
- First pillar: 1.2
- Second pillar: 1.1
- Last pillar: 1.1
- All others: 1.0

### Target Score
```
target = min(max(score + gapTop10 × 0.7, score + 0.5), 5.0)
```
Rounded to 2 decimal places.

### Phase Division
Items sorted by `priorityScore` descending (highest priority first), then split:
- **Phase 1 (Quick Wins, 0–6 months):** Top 35% of items
- **Phase 2 (Core Investment, 6–12 months):** Next 35%
- **Phase 3 (Strategic Differentiation, 12–18 months):** Remaining

Minimum 1 item per phase (if any exist).

### Actions
Derived from the vendor's `criteria_assessment`:
- Up to 2 unmet criteria (truncated to 100 chars)
- Up to 1 partial criteria (prefixed with "Strengthen: ", truncated to 80 chars)

### Priority Badge
| Score | Label | CSS Class |
|-------|-------|-----------|
| ≥ 5 | high | `.va-priority-high` (red) |
| ≥ 3 | medium | `.va-priority-medium` (gold) |
| < 3 | low | `.va-priority-low` (green) |

### Estimated Improvement
Per phase: `sum(min(target - score, gapTop10))` for all items in that phase.

---

## 16. Tab 6: Capability Legend

**Function:** `_vaRenderCapabilityLegend()`  
**Target:** `#va-panel-capability-legend`

### Data Sources
- `appState.pillarsGrouped` — pillar tree with sub-pillars
- `appState.schemaDetail.pillars[]` — enriched pillar info (focus, score rule, ai_evidence_signals)
- `appState.schemaDetail.sub_pillars[]` — enriched sub-pillar info (what_to_verify_publicly, ai_evaluation_criteria, ai_specific_evidence, expanded_definition)

### Layout
- "Expand All" / "Collapse All" buttons at top
- One collapsible section per pillar:
  - Header: chevron ▶, pillar code badge, pillar name, sub-pillar count
  - Body:
    - Focus / description (italic)
    - Score rule (if available)
    - Evidence signals (tag badges)
    - Sub-pillar cards:
      - ID badge + name
      - Definition text
      - "What to Verify Publicly" list
      - Activities / Key Activities list
      - AI Evaluation Criteria list (if different from activities)
      - AI-Specific Evidence list

### Expand/Collapse Mechanism
Toggle CSS class `expanded` on both `.va-legend-pillar-header` and the next sibling `.va-legend-pillar-body`. The body has `display:none` by default and `display:block` when `.expanded`.

---

## 17. Export to Standalone HTML

**Function:** `exportVendorAnalysisHTML()`

### Process
1. Checks vendor is selected
2. Snapshots `<canvas id="va-radar-canvas">` to PNG data URI via `canvas.toDataURL('image/png')`
3. Reads `innerHTML` of all 6 panel divs
4. Replaces `<canvas>` in exec summary with `<img src="data:image/png;base64,...">` for the radar chart
5. For the capability legend, pre-expands all pillar headers/bodies
6. Collects relevant CSS rules from page stylesheets (any rule containing `va-`, `report-`, `--text-`, `--bg-`, or `--border-`)
7. Builds a complete standalone HTML document with:
   - CSS variables in `:root`
   - Sticky tab bar at top
   - Tab switching JS (`switchExportTab()`)
   - Legend expand/collapse JS (delegated click listeners)
   - Print media query (shows all panels)
   - Header with vendor name + schema label + date
   - Footer with generator credit
8. Creates a Blob and triggers download as `{vendorName}_{schemaLabel}_Analysis_{date}.html`

### Exported File Structure
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        :root { --text-primary: #1a1a1a; ... }
        /* reset + layout */
        /* Export tabs (sticky) */
        /* Collected VA CSS rules */
        @media print { /* show all panels */ }
    </style>
</head>
<body>
    <div class="header"> ... </div>
    <div class="export-tabs"> [6 tab buttons] </div>
    <div class="export-panel active" id="export-panel-exec-summary"> ... </div>
    <div class="export-panel" id="export-panel-pillar-scorecard"> ... </div>
    ... (4 more panels)
    <div class="footer"> ... </div>
    <script>
        function switchExportTab(key) { ... }
        // Delegated click for legend toggle
        // Expand All / Collapse All
    </script>
</body>
</html>
```

---

## 18. Color System

### Score Colors (1–5 scale)
| Range | Color | Hex | Meaning |
|-------|-------|-----|---------|
| ≥ 4.0 | Blue | `#005a9e` | Best-in-class / Fully Agentic |
| ≥ 3.0 | Green | `#107c10` | Advanced |
| ≥ 2.0 | Gold | `#c19c00` | Developing / AI-Augmented |
| ≥ 1.0 | Orange | `#ff8c00` | Basic |
| < 1.0 | Red | `#d13438` | Minimal |

### Evidence Grade Colors
| Grade | CSS Class | Color |
|-------|-----------|-------|
| A | `.va-grade-A` | Blue `#005a9e` |
| B | `.va-grade-B` | Green `#107c10` |
| C | `.va-grade-C` | Gold `#c19c00` |
| D | `.va-grade-D` | Orange `#ff8c00` |
| F | `.va-grade-F` | Red `#d13438` |

### Gap Status Colors
| Status | Background | Text |
|--------|-----------|------|
| Leader (above top-10) | `rgba(0, 90, 158, 0.1)` | `#005a9e` |
| Above Avg | `rgba(16, 124, 16, 0.1)` | `#107c10` |
| At Avg | `rgba(193, 156, 0, 0.1)` | `#c19c00` |
| Below Avg | `rgba(209, 52, 56, 0.1)` | `#d13438` |

### Priority Badge Colors
| Priority | Background | Text |
|----------|-----------|------|
| High | `rgba(209, 52, 56, 0.12)` | `#d13438` |
| Medium | `rgba(193, 156, 0, 0.12)` | `#c19c00` |
| Low | `rgba(16, 124, 16, 0.12)` | `#107c10` |

### Roadmap Phase Colors
| Phase | Background | Text |
|-------|-----------|------|
| Phase 1 (Quick Wins) | `#e6f2e6` | `#107c10` |
| Phase 2 (Core Investment) | `#fff8e1` | `#c19c00` |
| Phase 3 (Strategic) | `#e8f0fe` | `#005a9e` |

---

## 19. Rebuild Checklist

To rebuild this VA report on another instance:

### Step 1: Backend APIs
- [ ] Implement `/api/metadata` returning `{ pillars_grouped: [...] }` (see Section 3)
- [ ] Implement `/api/schema-detail` returning `{ pillars: [...], sub_pillars: [...] }` (see Section 3)
- [ ] Implement `/api/vendors` returning array of vendor objects (see Section 5)

### Step 2: Data Preparation
- [ ] Vendor objects must have at minimum:
  - `vendor` (string name)
  - `headquarters`, `year_founded`, `employee_count_range`, `target_market` (display fields)
  - At least one of the pillar score fields (`pillar_scores`, `pillar_scores_v2_1`, etc.)
  - At least one of the sub-pillar score fields (`sub_pillar_scores_current`, `sub_pillar_scores_v2_1`, etc.)
  - Optional but recommended: `sub_pillar_rationale_v2_1` with `criteria_assessment[]` and `evidence_quality_grade`
- [ ] Sub-pillar IDs must follow `PILLAR-NN` format (e.g., `TDR-01`)
- [ ] Schema must define pillars with codes, names, and sub-pillars with IDs and names

### Step 3: HTML
- [ ] Add the HTML template from Section 6
- [ ] Add a report tab button that triggers `populateVendorAnalysisReport()`

### Step 4: CSS
- [ ] Add all CSS from Section 7
- [ ] Ensure CSS custom properties are defined (`:root` block)

### Step 5: JavaScript
- [ ] Add `appState` object with required fields (Section 4)
- [ ] Add utility functions: `escapeHtml`, `getScoreColor`, `getActivePillarCodes`, `getEffectiveGranularMapping`, `buildGranularMappingFromSubScores`, `getEffectivePillarScores`, `computePillarScoreFromGranular` (Section 8)
- [ ] Add all 21 VA functions from Section 9 (full source in the original app.js, lines 9720–10731)
- [ ] Wire `populateVendorAnalysisReport()` to be called when the VA tab is activated
- [ ] Ensure `appState._vaBenchmarks = null` is set when vendors or schema change

### Step 6: Test
- [ ] Load page, verify dropdown populates with vendors sorted alphabetically
- [ ] Select a vendor, verify all 6 tabs render
- [ ] Check radar chart renders with correct polygons
- [ ] Verify pillar scorecard cards expand/collapse
- [ ] Verify strengths/weaknesses populate
- [ ] Verify gap table sorts by largest gap first
- [ ] Verify roadmap phases divide correctly
- [ ] Verify capability legend expand/collapse works
- [ ] Test Export HTML — download, open in browser, verify tabs work, scroll works, legend toggles work

### Minimum Viable Version
If you don't need all score modes, you can simplify:
1. Set `appState.scoreMode = 'current'` permanently
2. Only populate `pillar_scores` and `sub_pillar_scores_current` on vendor objects
3. Skip `getEffectiveGranularMapping` complexity — just use `buildGranularMappingFromSubScores(vendor.sub_pillar_scores_current)`
4. Skip rationale fields — strengths/weaknesses and roadmap will just show score gaps without criteria detail

---

*Document generated from source code analysis of the Gartner Research Analysis Platform.*
*Source files: `static/app.js` (lines 9720–10731, 860–1100, 263–272, 5644–5655), `templates/index.html` (lines 783–820), `static/style.css` (lines 4951–5528).*
