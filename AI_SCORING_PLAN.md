# AI-Focused Schema Revision, Schema-Linked Vendor Files & 3rd Score Layer

**Created:** 2026-02-06  
**Status:** In Progress  
**Objective:** Add a 3rd scoring pass ("AI-researched") using a new AI-explicit schema, tag all vendor files to their schema, add a schema selector to the UI, and build a parallel research pipeline for all 138 vendors.

---

## Background

The existing system has two scoring layers:
- **Validated** (`sub_pillar_scores_validated`) — manually validated DFIR capability scores
- **Researched** (`sub_pillar_scores_researched`) — web-researched scores from vendor websites using `schema4-0_enhanced.json`

This plan adds a 3rd layer:
- **AI-Researched** (`sub_pillar_scores_ai_researched`) — scores focused exclusively on AI/ML capabilities, using 3rd-party sources in addition to vendor websites, evaluated against `schema5-0_ai.json`

All three score layers coexist in each vendor record. The same 20 sub-pillar IDs (PLA-01 through LAW-04) are shared across all schemas, providing a 1:1 mapping.

---

## Step 1: Create Full Backup

**Purpose:** Preserve the entire workspace before any changes.

**Actions:**
- ZIP `g:\My Drive\Gartner\` → `Gartner_Backup_2026-02-06_PreAI.zip`
- SCP a copy to production at `/home/vm-ssh/`
- Verify backup integrity

**Files included:**
- All vendor JSON files (vendor3-3.json through Vendor 5-2 Researched.json)
- Application files (app.py, static/, templates/)
- Schema files (schema3-3.json, schema4-0_enhanced.json)
- Research scripts and cache (research/, research_v2_vendor_scoring.py)
- Documentation (.md files)

---

## Step 2: Create `schema5-0_ai.json`

**Purpose:** Define AI-specific evaluation criteria for each of the 20 sub-pillars.

**Source:** Fork `schema4-0_enhanced.json` (same 5 pillars, same 20 sub-pillar IDs)

**Key changes from v4.0:**

| Aspect | schema4-0_enhanced.json | schema5-0_ai.json |
|--------|------------------------|-------------------|
| Top-level key | `dfir_capability_taxonomy_v4.0_enhanced` | `dfir_capability_taxonomy_v5.0_ai` |
| Sub-pillar fields | `what_to_verify_publicly`, `ai_specific_evidence` | `ai_evaluation_criteria` (4–5 concrete AI capabilities) |
| Scoring scale | Generic DFIR + AI maturity | AI-centric only |
| Source policy | Vendor websites only | Vendor sites + 3rd-party publications + media + LinkedIn |
| Schema lineage | `based_on: v3.2` | `parent: schema4-0_enhanced.json`, `sub_pillar_id_mapping: identical` |

**Scoring scale (AI-centric):**

| Score | Meaning |
|-------|---------|
| 0 | No publicly verifiable evidence of AI/ML in this capability |
| 1 | No AI/ML mentioned; capability is entirely manual/traditional |
| 2 | Generic AI claims without technical specifics or evidence |
| 3 | AI-augmented: documented AI/ML tools with human oversight, specific use cases described |
| 4 | Advanced AI: specialized ML models, measurable outcomes, partially automated with validation |
| 5 | Fully Agentic: autonomous AI systems with governance gates, documented model performance |

**Source policy:**

Valid evidence sources (in priority order):
1. Vendor's own website (product pages, documentation, whitepapers)
2. Analyst reports (Gartner, Forrester, IDC, KuppingerCole)
3. Technical media (Dark Reading, SC Media, CSO Online, The Record, BleepingComputer, SecurityWeek)
4. Case studies from technical media companies
5. LinkedIn articles and posts by vendor employees or analysts
6. Conference presentations (RSA, Black Hat, DEF CON, SANS)
7. Academic papers and research publications

**`ai_evaluation_criteria` examples (PLA-01 — Visibility Gap Analysis):**
- ML-driven telemetry gap detection across endpoint/network/cloud sources
- Automated asset classification using trained models
- AI-generated coverage recommendations with confidence scores and explainability
- Continuous drift detection using anomaly models on log/telemetry feeds
- Automated risk-prioritized remediation suggestions for coverage gaps

---

## Step 3: Tag All Vendor Files with `schema_ref`

**Purpose:** Link each vendor file to the schema it was scored against, enabling schema-based filtering.

**Format — dual tagging (wrapper + per-vendor):**

```json
{
  "schema_ref": "schema4-0_enhanced.json",
  "schema_version": "4.0",
  "vendors": [
    {
      "vendor": "7AI",
      "schema_ref": "schema4-0_enhanced.json",
      ...
    }
  ]
}
```

**File → Schema mapping:**

| Vendor File | Schema Ref | Schema Version |
|-------------|-----------|----------------|
| `vendor3-3.json` | `schema3-3.json` | 3.2 |
| `vendor3-4.json` | `schema3-3.json` | 3.2 |
| `vendor3-5.json` | `schema3-3.json` | 3.2 |
| `Vendor 4-0 Validated.json` | `schema4-0_enhanced.json` | 4.0 |
| `Vendor 4-1 Researched.json` | `schema4-0_enhanced.json` | 4.0 |
| `Vendor 5-0 Researched.json` | `schema4-0_enhanced.json` | 4.0 |
| `Vendor 5-1 Researched.json` | `schema4-0_enhanced.json` | 4.0 |
| `Vendor 5-2 Researched.json` | `schema4-0_enhanced.json` | 4.0 |
| `Vendor 6-0 AI Researched.json` *(future)* | `schema5-0_ai.json` | 5.0 |

**Code changes:**
- `load_vendor_data()` in `app.py`: if `isinstance(data, dict) and "vendors" in data`, extract `data["vendors"]`; otherwise fall back to bare array handling.

---

## Step 4: Add Schema Selector to App Backend

**Purpose:** Let the user select a schema, which filters the vendor file dropdown to only show files scored against that schema.

**New `app_state` field:**
```python
current_schema_file = 'schema3-3.json'
```

**New endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/schema-files` | GET | Discover all `schema*.json` files, return `[{filename, name, version}]` |
| `/api/schema-detail` | GET | Load current schema, return normalized pillars/sub-pillars/definitions/scoring |
| `/api/switch-schema` | POST | Set `app_state.current_schema_file`, return `{success, current}` |

**Modified endpoints:**

| Endpoint | Change |
|----------|--------|
| `/api/vendor-files` | Accept `?schema=<filename>` query param; filter files by `schema_ref` in wrapper |
| `/api/sub-pillars` | Load dynamically from current schema instead of hardcoded `schema3-3.json` |
| `/api/definitions` | Load dynamically from current schema |

**Schema normalization layer:**
Since v3.2, v4.0, and v5.0 schemas have different internal structures, `/api/schema-detail` normalizes to a common format:
```json
{
  "schema_file": "schema5-0_ai.json",
  "version": "5.0",
  "pillars": {
    "PLA": {"name": "Planning & Preparation", "focus": "..."},
    ...
  },
  "sub_pillars": {
    "PLA-01": {"name": "Visibility Gap Analysis", "definition": "...", "criteria": [...]},
    ...
  },
  "scoring_scale": {"0": "...", "1": "...", ...},
  "source_policy": {...}
}
```

---

## Step 5: Wire Schema Selector in Frontend

**Purpose:** Schema dropdown in the UI that filters vendor files and updates sub-pillar labels dynamically.

**HTML changes (`index.html`):**
- Add schema dropdown (`<select id="schema-select">`) above the existing vendor file dropdown
- Remove hardcoded sub-pillar names from sidebar filter buttons (lines 362–410); replace with dynamic rendering

**JavaScript changes (`app.js`):**

1. **Schema dropdown:**
   - `loadSchemaFiles()` → fetch `/api/schema-files`, populate `#schema-select`
   - On schema change → POST `/api/switch-schema`, then re-fetch `/api/vendor-files?schema=<selected>`, repopulate vendor dropdown
   - Re-fetch `/api/schema-detail` to update sub-pillar labels in sidebar and detail modal

2. **4th score mode:**
   - Add `"ai_researched"` to `scoreMode` system
   - Reads from `sub_pillar_scores_ai_researched` / `pillar_scores_ai_researched`
   - Show this option in score mode dropdown **only** when selected schema is `schema5-0_ai.json`
   - Update vendor detail modal Evidence & Rationale tab to show AI-specific rationale when in this mode

3. **Dynamic sub-pillar rendering:**
   - Store schema detail in `appState.schemaDetail`
   - Use `schemaDetail.sub_pillars[id].name` for labels throughout the app instead of hardcoded strings
   - Update column visibility, export, radar chart, and cross-section config to use dynamic labels

---

## Step 6: Build `research_v3_ai_scoring.py`

**Purpose:** Research all 138 vendors for AI-specific capabilities using `schema5-0_ai.json` criteria.

**Source:** Fork `research_v2_vendor_scoring.py`

**Key differences from v2:**

| Aspect | v2 | v3 |
|--------|----|----|
| Schema | `schema4-0_enhanced.json` | `schema5-0_ai.json` |
| Evidence sources | Vendor websites only | Vendor sites + 3rd-party publications + media + LinkedIn |
| Match terms | `what_to_verify_publicly` + `ai_specific_evidence` | `ai_evaluation_criteria` |
| Scoring weight | Hit count with AI bonus (+0.25) | AI-specific term matches weighted heavily |
| Output keys | `sub_pillar_scores_researched` | `sub_pillar_scores_ai_researched` |
| Parallelism | Sequential (42 vendors) | 6 lots of ~23 vendors each |

**AI-specific search terms (weighted heavily):**
`agentic`, `autonomous AI`, `LLM`, `large language model`, `ML model`, `machine learning pipeline`, `neural network`, `generative AI`, `AI-driven`, `AI-powered`, `deep learning`, `NLP`, `natural language processing`, `computer vision`, `reinforcement learning`, `transformer`, `GPT`, `copilot`, `AI agent`, `automated reasoning`, `AI orchestration`

**Output keys per vendor:**
```json
{
  "sub_pillar_scores_ai_researched": {"PLA-01": 2.75, ...},
  "pillar_scores_ai_researched": {"PLA": 2.50, ...},
  "sub_pillar_rationale_ai_researched": {"PLA-01": "AI score rationale...", ...},
  "sub_pillar_evidence_ai": {"PLA-01": {...}, ...},
  "research_flag_ai": "good_evidence",
  "research_confidence_ai": 0.8,
  "research_ai": {
    "status": "completed",
    "schema_ref": "schema5-0_ai.json",
    "timestamp_utc": "2026-02-06T...",
    "source_types": ["vendor_website", "analyst_report", "media", "linkedin"],
    ...
  }
}
```

### Parallel Lot Breakdown (138 vendors ÷ 6)

All 138 vendors sorted alphabetically and split into 6 lots:

| Lot | Range | Count | Delta File | Checkpoint |
|-----|-------|-------|-----------|-----------|
| **A** | 7AI → Capgemini | 23 | `ai_delta_lot_A.json` | `research/v3_checkpoint_A.json` |
| **B** | Cisco → CyberSOC Africa | 23 | `ai_delta_lot_B.json` | `research/v3_checkpoint_B.json` |
| **C** | Digital Encode → HCLTech | 23 | `ai_delta_lot_C.json` | `research/v3_checkpoint_C.json` |
| **D** | Help AG → Mitiga | 23 | `ai_delta_lot_D.json` | `research/v3_checkpoint_D.json` |
| **E** | mnemonic → S-RM | 23 | `ai_delta_lot_E.json` | `research/v3_checkpoint_E.json` |
| **F** | Serianu → Wolfpack InfoRisk | 23 | `ai_delta_lot_F.json` | `research/v3_checkpoint_F.json` |

**Execution (6 parallel processes):**
```
python research_v3_ai_scoring.py --lot A --sleep-seconds 1.0
python research_v3_ai_scoring.py --lot B --sleep-seconds 1.5
python research_v3_ai_scoring.py --lot C --sleep-seconds 2.0
python research_v3_ai_scoring.py --lot D --sleep-seconds 2.5
python research_v3_ai_scoring.py --lot E --sleep-seconds 3.0
python research_v3_ai_scoring.py --lot F --sleep-seconds 3.5
```

Staggered sleep offsets to avoid rate-limiting collisions across lots.

**Merge step:**
```
python research_v3_ai_scoring.py --merge-lots --base "Vendor 5-2 Researched.json" --output "Vendor 6-0 AI Researched.json"
```

Combines all 6 lot outputs into the base dataset, producing the final file with all 3 score layers.

---

## Step 7: Batch Deploy to Production

**Purpose:** Deploy all changes to production at 192.168.15.51:5000 in a single coordinated update.

**Files to deploy:**

| File | Change |
|------|--------|
| `app.py` | Schema selector endpoints, refactored schema loading, updated `load_vendor_data()` |
| `static/app.js` | Schema dropdown, 4th score mode, dynamic sub-pillar labels |
| `templates/index.html` | Schema dropdown HTML, dynamic sidebar |
| `schema5-0_ai.json` | New AI-focused schema |
| `Vendor 6-0 AI Researched.json` | Final output with all 3 score layers |
| All existing vendor JSON files | Re-tagged with `schema_ref` wrappers |

**Deployment steps:**
1. SCP all files to `/home/vm-ssh/gartner/`
2. `sudo systemctl restart gartner.service`
3. Verify: `curl http://localhost:5000/api/schema-files` returns 3 schemas
4. Verify: `curl http://localhost:5000/api/vendor-files?schema=schema5-0_ai.json` returns Vendor 6-0
5. Verify: Load Vendor 6-0 in browser, switch to AI-Researched score mode, confirm scores render

---

## Cross-Schema Score Layer Mapping

All schemas share the same 20 sub-pillar IDs, enabling a single vendor record to hold all score layers:

```
vendor_record = {
  "vendor": "Example Corp",
  
  // Layer 1: Manual (from schema3-3 / schema4-0)
  "sub_pillar_scores_current":       {"PLA-01": 3.0, ...},
  "sub_pillar_scores_validated":     {"PLA-01": 3.25, ...},
  
  // Layer 2: Web-researched (from schema4-0)
  "sub_pillar_scores_researched":    {"PLA-01": 2.75, ...},
  
  // Layer 3: AI-researched (from schema5-0)
  "sub_pillar_scores_ai_researched": {"PLA-01": 1.50, ...},
  
  // Schema tracking
  "schema_ref": "schema5-0_ai.json"
}
```

The frontend's score mode selector determines which layer to display:
- **Current (Raw)** → `sub_pillar_scores_current`
- **Validated** → `sub_pillar_scores_validated`
- **Researched** → `sub_pillar_scores_researched`
- **AI-Researched** → `sub_pillar_scores_ai_researched`

---

## Risk & Mitigation

| Risk | Mitigation |
|------|-----------|
| Backup failure | Verify ZIP integrity before proceeding; keep production copy |
| Schema migration breaks existing views | `load_vendor_data()` handles both wrapped and bare-array formats; fallback to current behavior |
| 3rd-party sources blocked/rate-limited | Curated URL lists per vendor; staggered sleep offsets across lots; retry with backoff |
| Score mode mismatch | AI-researched mode only visible when schema5-0 is selected; fallback to researched if AI scores missing |
| Parallel lots conflict on cache | Shared cache directory with SHA1-keyed files (no conflicts — same URL = same hash) |
