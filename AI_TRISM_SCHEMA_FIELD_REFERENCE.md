# AI TRiSM Schema & Field Reference

> **Version:** 1.1 | **Last Updated:** 2026-02-20  
> **Schema File:** `AI TriSM Schema 1_1.json`  
> **Latest Vendor File:** `AI TRiSM Vendor 2-1 Consolidated.json`

This document provides a comprehensive mapping of every field, structure, and research methodology used in the AI TRiSM vendor scoring system. It serves as the authoritative reference for building future schemas and research pipelines.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Research Pipeline Stages](#2-research-pipeline-stages)
3. [File-Level Structure](#3-file-level-structure)
4. [Vendor-Level Fields](#4-vendor-level-fields)
5. [Score Layers & Modes](#5-score-layers--modes)
6. [Pillar Definitions (GOV / RUN / INF)](#6-pillar-definitions)
7. [Sub-Pillar Definitions & Criteria](#7-sub-pillar-definitions--criteria)
8. [Rationale Consolidation Logic](#8-rationale-consolidation-logic)
9. [Evidence Structure](#9-evidence-structure)
10. [Evidence Quality Analysis](#10-evidence-quality-analysis)
11. [Scoring Scale & Maturity Levels](#11-scoring-scale--maturity-levels)
12. [Source Policy & Tiers](#12-source-policy--tiers)
13. [Frontend Score Modes](#13-frontend-score-modes)
14. [Schema Registry & Multi-Schema Support](#14-schema-registry--multi-schema-support)

---

## 1. Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Schema (JSON)                         │
│  AI TriSM Schema 1_1.json                                │
│  • Pillars (GOV, RUN, INF)                               │
│  • Sub-pillars (12 total, 4 per pillar)                  │
│  • Evaluation criteria (5 per sub-pillar = 60 total)     │
│  • Scoring scale (0-5 maturity levels)                   │
│  • Source policy (tiers A/B/C)                           │
│  • Research methodology & consolidation logic            │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│              Research Pipeline                           │
│  v1.0 Seed → v1.1 Validated → v2.0 Researched           │
│                                    → v2.1 Consolidated   │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│              Vendor Data (JSON)                          │
│  AI TRiSM Vendor 2-1 Consolidated.json                   │
│  • 63 vendors × 12 sub-pillars = 756 scored items        │
│  • 4 score layers per vendor                             │
│  • Consolidated rationale per sub-pillar                 │
│  • Evidence excerpts with source URLs                    │
│  • Evidence quality grades (A–F)                         │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│              Frontend (Flask + JS)                       │
│  app.py  → /api/vendors, /api/metadata                   │
│  app.js  → Table, modals, analytics, cross-section view  │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Research Pipeline Stages

| Stage | File | Script | Description |
|-------|------|--------|-------------|
| **v1.0 Seed** | `AI TRiSM Vendor 1-0 Seed.json` | `generate_trism_seed.py` | Initial vendor list with raw pillar/sub-pillar scores from capability claims. No evidence validation. |
| **v1.1 Validated** | `AI TRiSM Vendor 1-1 Validated.json` | `research_validate_vendors.py` | Validates vendor existence, websites, basic claims. Produces validated scores and plain-text rationale strings. |
| **v2.0 Researched** | `AI TRiSM Vendor 2-0 Researched.json` | `research_trism_v2_rationale.py` | Deep research: fetches public evidence pages, evaluates content against schema criteria, produces structured rationale objects with evidence quality analysis and score adjustments. |
| **v2.1 Consolidated** | `AI TRiSM Vendor 2-1 Consolidated.json` | `build_trism_v2_1.py` | Data-only transform (no fetches): consolidates `score_rationale`, `evidence_quality_rationale`, and `score_adjustment.reason` into a single human-readable string per sub-pillar. |

### Pipeline Flow

```
generate_trism_seed.py
  └─→ AI TRiSM Vendor 1-0 Seed.json
        │
        ▼
research_validate_vendors.py
  └─→ AI TRiSM Vendor 1-1 Validated.json
        │
        ▼
research_trism_v2_rationale.py        (fetches public web pages)
  └─→ AI TRiSM Vendor 2-0 Researched.json
        │
        ▼
build_trism_v2_1.py                   (no fetches – data transform only)
  └─→ AI TRiSM Vendor 2-1 Consolidated.json
```

---

## 3. File-Level Structure

The vendor JSON file has these top-level keys:

| Key | Type | Description |
|-----|------|-------------|
| `schema_ref` | `string` | Reference to the schema file (e.g., `"AI TriSM Schema 1_0.json"`) |
| `schema_version` | `string` | Data version (e.g., `"2.1"`) |
| `vendor_count` | `integer` | Number of vendors in the file |
| `research_tool` | `string` | Tool used for research (e.g., `"claude-sonnet-4-20250514"`) |
| `research_timestamp` | `string` | ISO 8601 timestamp of research completion |
| `vendors` | `array[object]` | Array of vendor objects (see §4) |
| `v2_research_metadata` | `object` | Stats from v2.0 research run |
| `v2_1_metadata` | `object` | Stats from v2.1 consolidation run |

### v2_research_metadata

| Key | Type | Description |
|-----|------|-------------|
| `generated_at` | `string` | ISO 8601 timestamp |
| `script` | `string` | Script name that produced this data |
| `vendors_processed` | `integer` | Count of vendors processed |
| `total_vendors` | `integer` | Total vendor count in file |
| `score_adjustments` | `object` | Counts: `increased`, `decreased`, `unchanged` |

### v2_1_metadata

| Key | Type | Description |
|-----|------|-------------|
| `generated_at` | `string` | ISO 8601 timestamp |
| `script` | `string` | `"build_trism_v2_1.py"` |
| `description` | `string` | Purpose of this stage |
| `source_file` | `string` | Input file used |
| `stats` | `object` | `total_vendors`, `vendors_with_v2_rationale`, `sub_pillars_consolidated`, `sub_pillars_missing_rationale` |

---

## 4. Vendor-Level Fields

Each object in the `vendors` array contains:

### Identity & Classification

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `vendor` | `string` | `"Accenture"` | Vendor display name |
| `region` | `string` | `"Global"` | Geographic focus |
| `specialization` | `string` | `""` | Niche specialization (if any) |
| `is_startup` | `boolean` | `false` | Whether vendor is a startup |
| `is_ai_first` | `boolean` | `false` | Whether vendor is AI-first |
| `vendor_type` | `string` | `"Consultancy"` | Vendor category |
| `primary_trism_layer` | `string` | `""` | Primary TRiSM focus layer |
| `notable_differentiation` | `string` | `"Integrates proprietary..."` | Key differentiator text |
| `capability_analysis` | `string` | `""` | High-level capability narrative |

### Score Layers (Pillar-Level)

Each is a `dict` mapping pillar code → float score:

| Field | Keys | Source Stage | Description |
|-------|------|--------------|-------------|
| `pillar_scores` | `GOV`, `RUN`, `INF` | v1.0 Seed | Original raw scores |
| `pillar_scores_validated` | `GOV`, `RUN`, `INF` | v1.1 Validated | Scores after vendor validation |
| `pillar_scores_evidence_refined` | `GOV`, `RUN`, `INF` | v2.0 Researched | Scores refined by evidence quality factors |
| `pillar_scores_v2_researched` | `GOV`, `RUN`, `INF` | v2.0 Researched | Final researched scores (used as primary v2 scores) |

### Score Layers (Sub-Pillar-Level)

Each is a `dict` mapping sub-pillar ID → float score:

| Field | Keys | Source Stage | Description |
|-------|------|--------------|-------------|
| `sub_pillar_scores_current` | `GOV-01`..`INF-04` | v1.0 Seed | Original raw sub-pillar scores |
| `sub_pillar_scores_validated` | `GOV-01`..`INF-04` | v1.1 Validated | Validated sub-pillar scores |
| `sub_pillar_scores_evidence_refined` | `GOV-01`..`INF-04` | v2.0 Researched | Evidence-refined sub-pillar scores |
| `sub_pillar_scores_v2_researched` | `GOV-01`..`INF-04` | v2.0 Researched | Final researched sub-pillar scores |

### Rationale Layers

| Field | Type | Source Stage | Description |
|-------|------|--------------|-------------|
| `sub_pillar_rationale_validated` | `dict[sid → string]` | v1.1 | Plain-text rationale per sub-pillar |
| `sub_pillar_rationale_v2` | `dict[sid → object]` | v2.0 | Structured rationale objects (see §8.1) |
| `sub_pillar_rationale_v2_consolidated` | `dict[sid → string]` | v2.1 | Consolidated human-readable rationale (see §8) |

### Evidence & Quality

| Field | Type | Description |
|-------|------|-------------|
| `sub_pillar_evidence` | `dict[sid → object]` | Evidence excerpts, URLs, term matches per sub-pillar (see §9) |
| `evidence_quality_analysis` | `dict[sid → object + _vendor_summary]` | Per-sub-pillar quality analysis (see §10) |
| `evidence_quality_summary` | `object` | Vendor-level quality rollup (see §10) |
| `sub_pillar_schema_labels` | `dict[sid → string]` | Human-readable label for each sub-pillar ID |

### Research Metadata

| Field | Type | Description |
|-------|------|-------------|
| `research` | `object` | Research execution details (see below) |
| `research_flag` | `string` | Quality flag: `"good_evidence"`, `"needs_review"`, `"no_public_info"` |
| `research_confidence` | `float` | 0.0–1.0 confidence in research quality |

#### `research` object

| Key | Type | Description |
|-----|------|-------------|
| `status` | `string` | e.g., `"validated"` |
| `source` | `string` | e.g., `"web + research"` |
| `tool` | `string` | Model/tool used |
| `schema` | `string` | Schema file reference |
| `timestamp_utc` | `string` | ISO 8601 timestamp |
| `pages_ok` | `integer` | Number of web pages successfully fetched |
| `cap_applied` | `boolean` | Whether a score cap was applied |
| `urls_used` | `array[string]` | URLs fetched for evidence |

---

## 5. Score Layers & Modes

The system maintains multiple score layers to enable comparison across research stages:

| Score Mode | Pillar Field | Sub-Pillar Field | Stage | Description |
|------------|--------------|-------------------|-------|-------------|
| `current` | `pillar_scores` | `sub_pillar_scores_current` | v1.0 | Raw initial scores |
| `validated` | `pillar_scores_validated` | `sub_pillar_scores_validated` | v1.1 | Post-validation scores |
| `evidence_refined` | `pillar_scores_evidence_refined` | `sub_pillar_scores_evidence_refined` | v2.0 | Scores adjusted by evidence quality factor |
| `v2_researched` | `pillar_scores_v2_researched` | `sub_pillar_scores_v2_researched` | v2.0 | Final researched scores with criteria analysis |

### Score Derivation

```
v1.0 raw score
  │
  ├─→ v1.1 validated  (adjust for vendor existence/website verification)
  │
  ├─→ v2.0 researched (deep evidence-based rescoring):
  │     ├─→ Scoring level (0-5) assigned based on evidence strength
  │     ├─→ Criteria assessment (5 criteria per sub-pillar evaluated)
  │     ├─→ Evidence quality factor (0.0-1.0) computed
  │     └─→ Score adjusted up/down based on analytical findings
  │
  └─→ evidence_refined = v2 score × evidence_quality_factor
```

---

## 6. Pillar Definitions

### GOV — AI Governance
**Focus:** Visibility, accountability, and continuous assurance across all AI entities and use cases.

| Sub-Pillar | Name |
|------------|------|
| GOV-01 | AI Catalog & Inventory |
| GOV-02 | AI Data Mapping & Lineage |
| GOV-03 | Documentation, Audit & Approvals |
| GOV-04 | Continuous Assurance & Posture |

### RUN — Runtime Inspection & Enforcement
**Focus:** Single-pass, low-latency runtime controls that inspect inputs/outputs/activities and enforce enterprise policy.

| Sub-Pillar | Name |
|------------|------|
| RUN-01 | Unified Runtime Control Plane |
| RUN-02 | Security & Threat Defense |
| RUN-03 | Safety, Quality & Compliance Filtering |
| RUN-04 | Contextual Data Protection at Runtime |

### INF — Information Governance (for AI)
**Focus:** Data discovery, classification, access control, retention, and PETs to prevent oversharing and data compromise.

| Sub-Pillar | Name |
|------------|------|
| INF-01 | Data Discovery & Classification |
| INF-02 | Access Governance & Sharing Hygiene |
| INF-03 | Privacy-Enhancing Technologies (PETs) |
| INF-04 | Cross-Functional Operating Model |

---

## 7. Sub-Pillar Definitions & Criteria

Each sub-pillar has 5 evaluation criteria. Scores are determined by how many criteria are met, partially met, or unmet.

### GOV-01: AI Catalog & Inventory
**Definition:** Discovery and risk scoring of all AI entities (models, agents, apps), including ownership, lineage, and life-cycle state.

| # | Criterion |
|---|-----------|
| 1 | Automated discovery of embedded and homegrown AI entities |
| 2 | Risk scoring per entity with policy/control coverage mapping |
| 3 | Owner/approver attribution and versioned lifecycle records |
| 4 | Searchable registry with model cards/BOMs and runtime metrics |
| 5 | APIs to export catalog and integrate with SIEM/GRC |

### GOV-02: AI Data Mapping & Lineage
**Definition:** Map training, fine-tuning, RAG, and agent context data to each AI entity and maintain lineage over time.

| # | Criterion |
|---|-----------|
| 1 | Automated mapping of data sets to specific AI entities |
| 2 | Lineage tracking (provenance, transformations, access history) |
| 3 | Data quality & sensitivity labeling tied to AI usage |
| 4 | Impact analysis for dataset changes on governed AI entities |
| 5 | Interfaces with data catalogs/MDM for bidirectional sync |

### GOV-03: Documentation, Audit & Approvals
**Definition:** Automated generation and maintenance of model cards, audit trails, approvals/attestations, and third-party RFI workflows.

| # | Criterion |
|---|-----------|
| 1 | Automated documentation (model cards, BOM, reports) |
| 2 | Immutable audit trails of AI artifacts and state changes |
| 3 | Workflow for approvals/exceptions with evidence attachments |
| 4 | Third-party AI RFI/evidence exchange and validation |
| 5 | Compliance mapping to NIST AI RMF / ISO 42001 / EU AI Act |

### GOV-04: Continuous Assurance & Posture
**Definition:** Pre- and post-deployment evaluations, red teaming, risk/control validation, and compliance reporting.

| # | Criterion |
|---|-----------|
| 1 | Automated red teaming (prompt attacks, adversarial tests) with results back to risk posture |
| 2 | Continuous policy/control validation (bias, leakage, trust, alignment) |
| 3 | Runtime metrics feeding posture dashboards and alerts |
| 4 | Compliance reporting with evidence links and trend views |
| 5 | APIs for SIEM/SOAR/GRC integration |

### RUN-01: Unified Runtime Control Plane
**Definition:** Single-pass inspection with multiple policy engines (safety, legal/compliance, security) and blended risk scoring.

| # | Criterion |
|---|-----------|
| 1 | Parallel policy engines with aggregated risk/decisioning |
| 2 | Latency SLAs and throughput benchmarks documented |
| 3 | Deterministic escalation routes by violation class |
| 4 | Pluggable policies/models; provider-agnostic connectors |
| 5 | Evidence of reduced conflicts vs siloed controls |

### RUN-02: Security & Threat Defense
**Definition:** Detection and prevention of prompt injection, jailbreaks, adversarial inputs, and anomalous model/agent behavior.

| # | Criterion |
|---|-----------|
| 1 | Prompt-injection/jailbreak detection with measurable block rates |
| 2 | Model/app/agent monitoring for anomalous activities |
| 3 | Signature + ML hybrid techniques for robustness |
| 4 | Auto-remediation playbooks with rollback |
| 5 | Feeds to SIEM/SOAR for incident response |

### RUN-03: Safety, Quality & Compliance Filtering
**Definition:** Input/output checking for toxicity, IP/copyright, hallucinations, and regulatory/policy violations with explainer artifacts.

| # | Criterion |
|---|-----------|
| 1 | Content anomaly detection with precision/recall metrics |
| 2 | Hallucination & factuality checks with citations |
| 3 | IP/copyright filters and licensing policy enforcement |
| 4 | Regulatory templates (e.g., EU AI Act risk class checks) |
| 5 | Explainability artifacts (rationales, scores, evidence IDs) |

### RUN-04: Contextual Data Protection at Runtime
**Definition:** Dynamic classification, PBAC/least-privilege enforcement, and selective redaction/obfuscation in transit.

| # | Criterion |
|---|-----------|
| 1 | Dynamic content classification inline with AI sessions |
| 2 | PBAC/ABAC enforcement bound to user/app/agent purpose |
| 3 | Selective redaction/tokenization with low latency |
| 4 | Per-transaction data access logs and alerts |
| 5 | Integration with DSPM/DLP/IAM to adjust permissions |

### INF-01: Data Discovery & Classification
**Definition:** Discover and classify sensitive data across SaaS, cloud, and productivity platforms relevant to AI.

| # | Criterion |
|---|-----------|
| 1 | Automated discovery across structured/unstructured stores |
| 2 | ML-driven classifiers for sensitivity and ownership |
| 3 | Coverage metrics and blind-spot detection |
| 4 | Linkage to AI use cases/RAG indexes |
| 5 | Bulk remediation workflows |

### INF-02: Access Governance & Sharing Hygiene
**Definition:** Permissions hygiene at scale with least-privilege/PBAC and lifecycle (retention/ROT) enforcement.

| # | Criterion |
|---|-----------|
| 1 | Automated permission right-sizing recommendations |
| 2 | PBAC policies bound to AI purposes and contexts |
| 3 | Lifecycle policies (retention, ROT cleanup) with evidence |
| 4 | Alerting on oversharing hotspots relevant to AI copilots |
| 5 | Change impact simulations before enforcement |

### INF-03: Privacy-Enhancing Technologies (PETs)
**Definition:** Apply PETs across training, tuning, inference, and agentic workflows.

| # | Criterion |
|---|-----------|
| 1 | Runtime masking/redaction/tokenization with rehydration controls |
| 2 | Synthetic data/differential privacy for evaluations |
| 3 | Confidential computing/TEEs for sensitive workloads |
| 4 | Documented privacy risk reduction metrics |
| 5 | Governed key/secret management for AI contexts |

### INF-04: Cross-Functional Operating Model
**Definition:** Coordination across Security, D&A, Digital Workplace, IAM, and Compliance to sustain InfoGov for AI at scale.

| # | Criterion |
|---|-----------|
| 1 | Documented RACI and workflows for AI data access changes |
| 2 | Joint KPIs (oversharing reduction, MTTR for policy fixes) |
| 3 | Integrated change mgmt from detection → permission fix |
| 4 | TTX for InfoGov failure modes (e.g., oversharing in copilots) |
| 5 | Evidence of scaled adoption in M365/Workspace estates |

---

## 8. Rationale Consolidation Logic

### 8.1 V2 Structured Rationale Object

Each entry in `sub_pillar_rationale_v2` (keyed by sub-pillar ID) is an object:

| Key | Type | Description |
|-----|------|-------------|
| `sub_pillar_id` | `string` | e.g., `"GOV-01"` |
| `sub_pillar_name` | `string` | e.g., `"AI Catalog & Inventory"` |
| `original_score` | `float` | Score from v1.1 validated |
| `adjusted_score` | `float` | Final v2 score after evidence analysis |
| `scoring_level` | `integer` | Maturity level (0–5) assigned |
| `score_rationale` | `string` | **Primary rationale:** Why this score and level were assigned |
| `evidence_quality_rationale` | `string` | **Quality assessment:** Source diversity, volume, specificity, grade |
| `scoring_level_justification` | `string` | Brief justification for the maturity level |
| `criteria_assessment` | `array[object]` | Per-criterion evaluation (see below) |
| `key_evidence` | `array[string]` | Top evidence snippets used in scoring |
| `score_adjustment` | `object` | `{original, adjusted, reason}` — why score changed |
| `additional_sources_found` | `integer` | Extra sources discovered during research |
| `confidence` | `string` | `"high"`, `"medium"`, or `"low"` |
| `evidence_quality_factor` | `float` | 0.0–1.0 quality multiplier |

#### criteria_assessment entry

| Key | Type | Description |
|-----|------|-------------|
| `criterion` | `string` | The evaluation criterion text |
| `status` | `string` | `"met"`, `"partial"`, or `"unmet"` |
| `evidence` | `string` | Supporting evidence text (or gap description) |
| `confidence` | `string` | `"high"`, `"medium"`, or `"low"` |

### 8.2 V2.1 Consolidated Rationale

The `sub_pillar_rationale_v2_consolidated` field contains a single string per sub-pillar ID that merges all three rationale sources:

```
GOV-01 – AI Catalog & Inventory: Score 3.25/5.0 (Level 3). Confidence: medium.

[Score Rationale]
Vendor scores 3.25/5.0 (Level 3: AI-Augmented — Documented AI features...).
Evidence: coverage=20%, V1 signal=0.60...

[Evidence Quality]
Evidence quality: 54.5% — Grade C (Moderate). Source diversity is weak...

[Score Adjustment]
4.40 → 3.25: Score decreased from 4.40 to 3.25: rationale analysis found
weaker support than score suggests (0/5 criteria met, 3 key excerpts).

[Criteria Assessment] (0 met, 4 partial, 1 unmet of 5)
  ❌ UNMET: Automated discovery of embedded and homegrown AI entities
  ⚠️ PARTIAL: Risk scoring per entity with policy/control coverage mapping
  ...

[Key Evidence]
  1. Stay up-to-date with data security and privacy regulations...
  2. Data protection and privacy services...
```

### 8.3 Consolidation Rules

1. **Header:** `{sid} – {name}: Score {adjusted}/5.0 (Level {level}). Confidence: {confidence}.`
2. **[Score Rationale]:** Verbatim from `score_rationale`
3. **[Evidence Quality]:** Verbatim from `evidence_quality_rationale`
4. **[Score Adjustment]:** `{original} → {adjusted}: {reason}`
5. **[Criteria Assessment]:** Summary line + per-criterion status with icons
6. **[Key Evidence]:** Top 3 snippets (truncated to 150 chars)

---

## 9. Evidence Structure

Each entry in `sub_pillar_evidence` (keyed by sub-pillar ID) contains:

| Key | Type | Description |
|-----|------|-------------|
| `source_urls` | `array[string]` | URLs where evidence was found |
| `excerpts` | `array[object]` | Evidence excerpt objects (see below) |
| `pillar_term_hits` | `integer` | Count of pillar-specific terms found in evidence |
| `schema_criteria_hits` | `integer` | Count of schema criteria terms matched |
| `criteria_hit_count` | `integer` | Distinct criteria with at least one hit |
| `sub_pillar_specificity` | `float` | Term specificity score |
| `notes` | `string` | Additional research notes |

### Evidence Excerpt Object

| Key | Type | Description |
|-----|------|-------------|
| `url` | `string` | Source URL for this excerpt |
| `excerpt` | `string` | Text snippet from the source |
| `matched_terms` | `array[string]` | Terms that matched in this excerpt |
| `relevance_score` | `float` | Relevance score for this excerpt (0.0–1.0) |

---

## 10. Evidence Quality Analysis

### Per-Sub-Pillar (`evidence_quality_analysis.{sid}`)

Detailed quality breakdown per sub-pillar (structure varies, typically includes source diversity factor, volume metrics, specificity scores).

### Vendor Summary (`evidence_quality_analysis._vendor_summary`)

Aggregate quality metrics across all sub-pillars for the vendor.

### `evidence_quality_summary`

Top-level vendor quality rollup:

| Key | Type | Description |
|-----|------|-------------|
| `avg_quality_factor` | `float` | Average evidence quality across sub-pillars (0.0–1.0) |
| `overall_refined_score` | `float` | Overall score after quality refinement |
| `sub_pillars_scored` | `integer` | Count of sub-pillars with scores |
| `sub_pillars_with_evidence` | `integer` | Count of sub-pillars with evidence |
| `quality_grade` | `string` | Letter grade: `A` (≥80%), `B` (≥60%), `C` (≥40%), `D` (≥20%), `F` (<20%) |
| `timestamp_utc` | `string` | ISO 8601 timestamp |

### Quality Grade Scale

| Grade | Factor Range | Meaning |
|-------|-------------|---------|
| A | ≥ 0.80 | Strong — Multiple sources, high specificity, criteria well-covered |
| B | ≥ 0.60 | Good — Solid evidence but may lack source diversity |
| C | ≥ 0.40 | Moderate — Limited sources or low criteria coverage |
| D | ≥ 0.20 | Weak — Minimal evidence, unreliable scores |
| F | < 0.20 | Insufficient — Scores should not be trusted |

---

## 11. Scoring Scale & Maturity Levels

| Level | Label | Description |
|-------|-------|-------------|
| **0** | No Evidence | No publicly verifiable evidence of AI-enabled TRiSM in this capability. |
| **1** | No AI/ML | Policy/process or manual controls only; no AI-based enforcement, monitoring, or evaluation beyond simple rules/scripting. |
| **2** | Generic AI Claims | Marketing mentions AI/ML guardrails but lacks named models, policy engines, runtime hooks, metrics, or docs. |
| **3** | AI-Augmented | Documented AI models or policy engines assist humans (e.g., runtime detections, cataloging, or evaluations) with human approval gates; some use-case specifics disclosed. |
| **4** | Advanced AI | Named models/policy engines with measurable outcomes (block/allow rates, false-positive/negative, latency). Partially automated runtime enforcement with blended risk scoring; continuous assurance pipelines. |
| **5** | Fully Agentic | Autonomous TRiSM controls that plan, inspect, enforce, and auto-remediate within governance bounds; full auditability of AI actions, versioned models, error rates, and override points disclosed. |

### Score Assignment Logic

1. **V1 Signal:** Original score from seed/validated stage (0.0–5.0)
2. **Evidence Coverage:** Percentage of schema criteria with supporting evidence
3. **Pillar Term Hits:** Domain-specific terms found in evidence
4. **Schema Criteria Hits:** Direct matches to evaluation criteria
5. **Scoring Level:** Determined by evidence strength, not just claims
6. **Adjustment:** Score may be increased or decreased based on the gap between claimed and evidenced capability

---

## 12. Source Policy & Tiers

| Tier | Type | Weight | Examples |
|------|------|--------|----------|
| **A** | Vendor documentation | 1.00 | Product pages, Admin/Developer docs, API refs, Release notes, Security whitepapers |
| **A** | Analyst reports | 1.00 | Gartner Market Guide, Forrester Wave, IDC MarketScape, KuppingerCole |
| **B** | Technical media | 0.85 | SecurityWeek, Dark Reading, Help Net Security, CSO Online |
| **B** | Benchmarks/Case studies | 0.85 | Customer case studies, Public bake-offs, Government RFP evals |
| **C** | Conference/Academic | 0.70 | RSAC, Black Hat, DEF CON, arXiv, Standards drafts |
| **C** | Professional networks | 0.70 | Engineer-authored LinkedIn/Blogs with technical detail |

### Invalid Sources (never accepted)
- Unverifiable anonymous claims
- Paywalled content not publicly accessible
- Internal/confidential docs
- Generic sales collateral without technical detail

---

## 13. Frontend Score Modes

The frontend supports switching between score layers via the "Score Mode" dropdown:

| Mode | Display Name | Pillar Field | Sub-Pillar Field | Available When |
|------|-------------|--------------|-------------------|----------------|
| `current` | Current | `pillar_scores` | `sub_pillar_scores_current` | Always |
| `validated` | Validated | `pillar_scores_validated` | `sub_pillar_scores_validated` | v1.1+ files |
| `researched` | Researched | `pillar_scores_researched` | `sub_pillar_scores_researched` | DFIR files only |
| `ai_researched` | AI Researched | `pillar_scores_ai_researched` | `sub_pillar_scores_ai_researched` | DFIR files only |
| `v2_researched` | V2 Researched | `pillar_scores_v2_researched` | `sub_pillar_scores_v2_researched` | TRiSM v2.0+ files |
| `evidence_refined` | Evidence Refined | `pillar_scores_evidence_refined` | `sub_pillar_scores_evidence_refined` | v2.0+ files |

### Rationale Resolution Order

When displaying rationale in the vendor detail modal, the system checks:

1. `sub_pillar_rationale_v2_consolidated` → String (v2.1 consolidated)
2. `sub_pillar_rationale_v2` → Object (v2.0 structured — rendered with rich formatting)
3. `sub_pillar_rationale_researched` → String (DFIR pipeline)
4. Falls back to "No rationale available"

---

## 14. Schema Registry & Multi-Schema Support

The backend maintains a schema registry mapping schema files to their structural properties:

```python
SCHEMA_REGISTRY = {
    "schema3-3.json":        {"top_key": "dfir_vendor_taxonomy_v3.3", "structure": "nested"},
    "schema3-6.json":        {"top_key": "dfir_vendor_taxonomy_v3.6", "structure": "nested"},
    "schema3-7.json":        {"top_key": "dfir_vendor_taxonomy_v3.7", "structure": "nested"},
    "schema4-0_enhanced.json": {"top_key": "dfir_vendor_taxonomy_v4.0", "structure": "nested"},
    "schema5-0_ai.json":     {"top_key": "dfir_vendor_taxonomy_v5.0", "structure": "nested"},
    "AI TriSM Schema 1_0.json": {"top_key": "ai_trism_taxonomy_v1.0", "structure": "flat"},
    "AI TriSM Schema 1_1.json": {"top_key": "ai_trism_taxonomy_v1.1", "structure": "flat"},
}
```

### Key Differences: DFIR vs TRiSM Schemas

| Aspect | DFIR | TRiSM |
|--------|------|-------|
| Pillars | PLA, INV, REM, PMG, LAW (5) | GOV, RUN, INF (3) |
| Sub-pillars per pillar | 3–5 | 4 |
| Total sub-pillars | ~18 | 12 |
| Structure | Nested (pillars contain sub-pillars) | Flat (sub-pillars at top level) |
| Criteria per sub-pillar | Varies | 5 |
| Total evaluation criteria | ~60 | 60 |

---

## Appendix: File Inventory

| File | Purpose |
|------|---------|
| `AI TriSM Schema 1_0.json` | Schema v1.0 — pillars, sub-pillars, criteria, scoring scale |
| `AI TriSM Schema 1_1.json` | Schema v1.1 — adds research methodology, rationale consolidation logic |
| `AI TRiSM Vendor 1-0 Seed.json` | 63 vendors with initial scores |
| `AI TRiSM Vendor 1-1 Validated.json` | 63 vendors with validated scores and rationale |
| `AI TRiSM Vendor 2-0 Researched.json` | 63 vendors with deep research, evidence, structured rationale |
| `AI TRiSM Vendor 2-1 Consolidated.json` | 63 vendors with consolidated rationale strings |
| `generate_trism_seed.py` | Script: generate v1.0 seed |
| `research_validate_vendors.py` | Script: validate vendors (v1.1) |
| `research_trism_v2_rationale.py` | Script: deep research with evidence (v2.0) |
| `build_trism_v2_1.py` | Script: consolidate rationale (v2.1) |
| `app.py` | Flask backend |
| `static/app.js` | Frontend application |
| `templates/index.html` | HTML template |
