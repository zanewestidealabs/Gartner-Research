# Research Completion Plan — Incomplete Vendor Scoring

## Objective

Complete the researched sub-pillar and pillar scores for the **42 vendors** (after IBM de-duplication) in `Vendor 5-1 Incomplete Research Delta.json` that currently show **0.25 across all 20 sub-pillars**. These vendors failed initial automated research due to either `no_evidence` (30 vendors — pages fetched but no DFIR-specific terms matched) or `fetch_failed` (13 vendors — HTTP requests failed entirely).

The goal is to produce evidence-backed AI capability scores for every vendor across all 5 pillars (PLA, INV, REM, PMG, LAW) and 20 sub-pillars, aligned to the `schema4-0_enhanced.json` taxonomy and consistent with the 96 vendors already successfully researched.

**No vendor tiering or bias.** All vendors are researched with equal depth and identical methodology regardless of size, profile, or region. This is a pure capability mapping exercise.

---

## File Naming Convention

| File | Purpose |
|------|---------|
| `Vendor 5-1 Researched.json` | Current full dataset (139 vendors, 43 with incomplete research) |
| `Vendor 5-1 Incomplete Research Delta.json` | The 43 vendors needing research (input for research script) |
| `Vendor 5-1 Incomplete Research Summary.json` | Quick reference summary of incomplete vendors |
| `research_v2_vendor_scoring.py` | Enhanced research pipeline (new version) |
| `schema4-0_enhanced.json` | Scoring taxonomy and evidence definitions |
| `Vendor 5-2 Researched.json` | **Output** — merged full dataset with completed research |
| `RESEARCH_COMPLETION_PLAN.md` | This plan document |

### Superseded Scripts (retained for reference)

| File | Purpose |
|------|---------|
| `research_validate_vendors.py` | Original v1 research pipeline |
| `expand_research_rationales.py` | Original rationale expansion |

---

## Scoring Framework (schema4-0_enhanced.json)

### Scale (0–5): AI Integration Maturity

| Score | Label | Definition |
|:-----:|-------|------------|
| **1** | Manual | Process is explicitly human-led with no evidence of technological automation |
| **2** | Insufficient Evidence | Documentation confirms the service is provided, but does not verify AI integration |
| **3** | AI-Augmented | Assistive AI used for summarization, drafting, triage suggestions, or search optimization; humans remain primary decision-makers |
| **4** | Advanced AI | Specialized models perform correlation/classification at scale; workflows are partially automated but require human validation/approval |
| **5** | Fully Agentic | Autonomous systems plan tasks, execute tooling, and generate defensible documentation with measurable human oversight gates |

> **0.25** = the current default placeholder, meaning "no publicly verifiable evidence found."

### Evidence Quality Tiers

| Tier | Definition | Expected Score Range |
|:----:|-----------|:--------------------:|
| **A** | Direct vendor docs + technical detail (features, workflows, screenshots, API refs) | 3.75 – 4.5 |
| **B** | Vendor marketing with some specifics (named features, rough workflow) | 2.25 – 3.75 |
| **C** | Third-party mentions without technical verification | 1.25 – 2.25 |
| **D** | Unverifiable claims / vague statements | 0.25 – 0.75 |

### Key Guardrails

- Vendors without `good_evidence` status are **capped at 3.0** on all sub-pillar research scores
- `good_evidence` requires evidence coverage >= 70% of sub-pillars (confidence 0.8)
- `partial_evidence` requires 30–70% coverage (confidence 0.6)
- `low_evidence` is < 30% coverage (confidence 0.35)
- Scores should **never exceed validated scores** without strong justification
- AI-signal terms must be domain-specific, not generic marketing language

---

## The 20 Sub-Pillars and What Qualifies as Evidence

### PLA — Planning & Preparation

| ID | Sub-Pillar | Public Evidence Required | AI-Specific Evidence |
|----|-----------|-------------------------|---------------------|
| PLA-01 | Visibility Gap Analysis | Automated coverage maps (endpoint/network/identity/cloud), detection of missing audit trails, repeatable assessments | AI-assisted gap detection in telemetry, automated recommendations with explainability |
| PLA-02 | Behavioral Playbook Design | Named playbook libraries, decision-tree branching, SOAR/case-management integration | AI-generated playbook drafts with human approval, dynamic playbook suggestions |
| PLA-03 | TTX Automation | Scenario library, facilitation tooling, scoring/metrics, automated post-exercise reports | AI-driven scenario generation or role-play, automated lesson extraction |
| PLA-04 | Forensic Readiness Maturity | Standard mapping (ISO 27037, NIST), checklists, repeatable assessments | AI in policy/log-review correlation, automated evidence-readiness checks |

### INV — Forensic Investigation

| ID | Sub-Pillar | Public Evidence Required | AI-Specific Evidence |
|----|-----------|-------------------------|---------------------|
| INV-01 | Triage and Scoping | Triage workflows/decision criteria, automated enrichment, prioritized collection guidance | AI-assisted triage summaries with cited artifacts, automated scoping with confidence |
| INV-02 | Multi-Hop Timeline Reconstruction | Cross-source correlation, graph/timeline visualizations, exportable evidence-linked timelines | AI correlation of events into sequences, agentic collection + timeline building |
| INV-03 | Artifact Source Attribution | Provenance features (process tree, file paths, user/session context), hashing/signing, evidence linkage | AI-assisted clustering/attribution citing artifacts, automated provenance graphs |
| INV-04 | Malware & Reverse Engineering | Malware triage pipelines, sandboxing, unpacking/deobfuscation, report outputs (IOCs, YARA, TTP mapping) | AI-assisted code understanding/classification, automated IOC extraction with validation |

### REM — Remediation & Recovery

| ID | Sub-Pillar | Public Evidence Required | AI-Specific Evidence |
|----|-----------|-------------------------|---------------------|
| REM-01 | Containment & Isolation | Containment playbooks (EDR isolation, account disable, firewall rules), SOAR/EDR integration, preservation steps | AI-assisted containment recommendations with rationale, automated containment with approval gates |
| REM-02 | Root Cause Eradication | Persistence detection methods, remediation checklists tied to findings, validation steps confirming removal | AI-assisted persistence pattern detection, automated remediation guidance with citations |
| REM-03 | Recovery & Restoration Verification | Backup integrity verification, post-restoration monitoring, hardening steps tied to root cause | AI-supported restoration validation (anomaly detection), automated checks |
| REM-04 | Ransomware Negotiation & Forecasting | Negotiation support services/tooling, outcome forecasting methodology, structured actor intelligence | AI-supported pricing/outcome modeling, automated actor TTP clustering |

### PMG — Post-Incident Management

| ID | Sub-Pillar | Public Evidence Required | AI-Specific Evidence |
|----|-----------|-------------------------|---------------------|
| PMG-01 | Incident Coordination & Escalation | Case management/workflow tooling, role-based coordination, timeline/task tracking | AI-generated task plans with approval, automated incident status synthesis |
| PMG-02 | Forensic Quality & Compliance | Quality controls/review workflows, accreditation alignment, audit trail completeness | AI-assisted QA checks with traceability, automated audit trail validation |
| PMG-03 | Crisis & Board Communication | Report templates, executive briefing outputs, evidence-backed narrative generation | AI drafting with source citations, automated summarization with human review |
| PMG-04 | Post-Incident Learning & Review | AAR processes, root cause to improvement mapping, cross-incident benchmarking | AI-assisted extraction of themes/root causes, automated recommendation generation |

### LAW — Legal & Compliance

| ID | Sub-Pillar | Public Evidence Required | AI-Specific Evidence |
|----|-----------|-------------------------|---------------------|
| LAW-01 | Evidence Collection & Preservation | Collection methodology/tooling, chain-of-custody records, tamper-evident storage | AI-assisted triage preserving provenance, automated defensible documentation |
| LAW-02 | Expert Witness Testimony Support | Litigation support services, legal-standard report formats, expert testimony readiness | AI in report drafting with traceability, automated evidence cross-referencing |
| LAW-03 | Machine-Inclusive Chain of Custody | Audit logs including automation steps, model/version tracking, repeatable handoff procedures | Explicit logging of AI actions/prompts, controls preventing untracked modifications |
| LAW-04 | Admissibility Defense (Daubert Standard) | Documented methodology/validation, error rate disclosures, peer-reviewed alignment | AI model limitations disclosed in reports, validation of AI-assisted steps with human review |

---

## Vendors Requiring Research (43 → 42 after IBM merge)

### Group A — `fetch_failed` (13 vendors) — HTTP requests failed, need URL correction + re-fetch

| # | Vendor | Region | Original URL | Likely Issue |
|---|--------|--------|-------------|-------------|
| 1 | Cyberegate | Middle East (UAE) | https://cybergate.ad/ | Domain may be incorrect |
| 2 | Digital Encode | Africa (Nigeria) | https://digitalencode.com.ng/ | Site may block bots |
| 3 | Group-IB | Global | https://www.group-ib.com/ | Geo-blocking or bot detection |
| 4 | HCLTech | Global | https://www.hcltech.com/ | Bot detection / JS-heavy site |
| 5 | Infosys | Global | https://www.infosys.com/ | Bot detection / JS-heavy site |
| 6 | LGMS | APAC (Malaysia) | https://lgms.global/ | Site may be down |
| 7 | Litt | North America | https://litt.ai/ | Startup — site may have changed |
| 8 | Orange Cyberdefense | Europe / Global | https://www.orangecyberdefense.com/ | Bot detection |
| 9 | P0 Security | North America | https://www.p0.security/ | JS-rendered / bot detection |
| 10 | PwC | Global | https://www.pwc.com/ | Bot detection / complex site |
| 11 | Rubrik | Global | https://www.rubrik.com/ | JS-heavy / bot detection |
| 12 | Stellar Cyber | North America | https://stellarcyber.ai/ | Bot detection |
| 13 | Tenzai | Middle East | https://tenzai.ai/ | Startup — site may have changed |

### Group B — `no_evidence` (30 → 29 after IBM merge)

| # | Vendor | Region | Source URL |
|---|--------|--------|-----------|
| 1 | Aon (Stroz Friedberg) | Global | https://www.aon.com/ |
| 2 | Bitdefender | Europe / Global | https://www.bitdefender.com/ |
| 3 | Booz Allen Hamilton | North America / Global | https://www.boozallen.com/ |
| 4 | Bridewell | United Kingdom | https://www.bridewell.com/ |
| 5 | BT Cyber | Europe / Global | https://www.globalservices.bt.com/ |
| 6 | Capgemini | Global / EMEA | https://www.capgemini.com/ |
| 7 | Cisco | Global | https://talosintelligence.com/ |
| 8 | CPX | Middle East (UAE) | https://www.cpx.net/ |
| 9 | CyberCX | APAC (Australia) | https://cybercx.com.au/ |
| 10 | CyberLink | APAC (Taiwan) | https://www.cyberlink.com/ |
| 11 | CyberSOC Africa | Africa (Pan-Africa) | https://cybersocafrica.com/ |
| 12 | DTS Solution | Middle East (UAE) | https://dts-it.com/ |
| 13 | Expel | North America | https://expel.com/ |
| 14 | Help AG | Middle East (UAE) | https://www.helpag.com/ |
| 15 | IBM (X-Force) | Global | https://www.ibm.com/security/xforce |
| 16 | Kivu | North America | https://kivuconsulting.com/ |
| 17 | Mitiga | North America | https://www.mitiga.io/ |
| 18 | mnemonic | Europe (Norway) | https://www.mnemonic.no/ |
| 19 | Nozomi Networks | North America | https://www.nozominetworks.com/ |
| 20 | Pondurance | North America | https://www.pondurance.com/ |
| 21 | Quorum Cyber | United Kingdom | https://www.quorumcyber.com/ |
| 22 | S-RM | United Kingdom | https://www.s-rminform.com/ |
| 23 | Serianu Limited | Africa (Kenya) | https://www.serianu.com/ |
| 24 | Sygnia | Global | https://www.sygnia.co/ |
| 25 | Tempest | Latin America (Brazil) | https://www.tempest.com.br/ |
| 26 | Total Assure | United Kingdom | https://www.totalassure.com/ |
| 27 | TrustedSEC | North America | https://www.trustedsec.com/ |
| 28 | Trustwave | Global | https://www.trustwave.com/ |
| 29 | Wolfpack InfoRisk | Africa (South Africa) | https://wolfpackrisk.com/ |

> **IBM Security (X-Force)** merged into **IBM (X-Force)** — confirmed same organization, region, source URL, and validated scores.

---

## What Changed in v2 Research Script (`research_v2_vendor_scoring.py`)

### Improvements over `research_validate_vendors.py`

| Area | v1 Limitation | v2 Enhancement |
|------|---------------|----------------|
| **URL Discovery** | Only extracted URLs from `capability_analysis` field (usually 1 URL) | Multi-page discovery: homepage + `/incident-response`, `/services`, `/platform`, `/blog` paths. Also searches for DFIR-specific subpages |
| **Bot Evasion** | Basic User-Agent only | Rotates realistic User-Agent strings, adds `Accept-Language`, `Referer` headers, randomized delays |
| **Fetch Retry** | Single attempt, 20s timeout | 3 retries with exponential backoff (5s, 15s, 30s timeouts) |
| **URL Correction** | No correction for known bad URLs | Built-in URL mapping for known `fetch_failed` vendors (corrected domains) |
| **Input/Output** | Hardcoded to v4-0/v4-1 files | Accepts `Vendor 5-1 Incomplete Research Delta.json` as input, merges output into full dataset to produce `Vendor 5-2 Researched.json` |
| **Merge Step** | Separate manual process | Built-in merge: reads full `Vendor 5-1 Researched.json`, replaces updated vendor records, writes `Vendor 5-2 Researched.json` |
| **IBM De-dup** | Not handled | Merges `IBM Security (X-Force)` into `IBM (X-Force)`, keeping highest validated scores |
| **Rationale** | Separate script required | Integrated rationale generation (same logic as `expand_research_rationales.py`) |
| **Checkpointing** | Every N vendors | Per-vendor checkpoint + resume from partial runs |

### Unchanged (Consistent with v1)

- Same heuristic scoring function (`_score_subpillar_from_hits`)
- Same evidence quality tiers and 3.0 cap for non-`good_evidence` vendors
- Same AI signal terms and specific-vs-generic term classification
- Same HTML parsing and snippet extraction logic
- Same research cache structure under `research/cache/pages/`
- Same rationale template and confidence language tiers

---

## Execution Plan

### Phase 1: URL Discovery & Page Collection

For each vendor, collect content from **multiple pages** (not just the homepage):

1. **Primary URL** — Vendor homepage (fix broken URLs for `fetch_failed` group)
2. **IR / DFIR Service Page** — Discover `/incident-response`, `/services/dfir`, `/cyber-defense` paths
3. **Product / Platform Page** — Technology documentation, feature lists
4. **Blog / Whitepapers** — Technical posts about IR methodology, case studies

**Target:** 3–8 relevant URLs per vendor

### Phase 2: Evidence Extraction

For each vendor's collected pages, extract evidence mapped to each of the 20 sub-pillars:

1. **Scan for schema-specific terms** — Match terminology from `what_to_verify_publicly` and `ai_specific_evidence` fields
2. **Capture excerpts** — Direct quotes (10–320 chars) with matched terms noted
3. **Assess AI signal strength** — 15 AI-indicator terms scanned per page
4. **Record source URLs** for each piece of evidence

### Phase 3: Scoring

Apply the heuristic scoring model consistent with completed vendors:

| Specific Term Matches | AI Signal Present | Score Range |
|:---------------------:|:-----------------:|:-----------:|
| 0 | No | 0.25 – 0.75 |
| 0 | Yes (generic) | 0.75 – 1.25 |
| 1 | No | 1.25 |
| 1 | Yes | 1.75 |
| 2–3 | No | 2.25 |
| 2–3 | Yes | 2.75 |
| 4–6 | Any | 3.25 – 3.75 |
| 7+ | Strong | 4.0 – 4.5 |

### Phase 4: Rationale Generation

Each sub-pillar rationale (>= 180 chars) follows the established template:

```
"<ID> - <Name>. Score: <X.X>/5. Evidence flag/confidence: <flag> / <conf>.
<Excerpt with matched terms>. Sources observed: <URLs>.
<Ceiling explanation>. <Improvement guidance>."
```

### Phase 5: Record Assembly, Merge & Output

1. Update all research fields per vendor
2. Merge `IBM Security (X-Force)` into `IBM (X-Force)`
3. Replace updated records in full dataset
4. Write `Vendor 5-2 Researched.json` (138 vendors)
5. Validate JSON structure and score consistency

---

## Definition of Done

- [ ] All 42 vendors have researched sub-pillar scores != 0.25 (unless genuinely zero evidence after expanded research)
- [ ] All 42 vendors have updated `research_flag` and `research_confidence` values
- [ ] All 20 `sub_pillar_rationale_researched` entries populated per vendor (>= 180 chars each)
- [ ] `sub_pillar_evidence` populated with source URLs and excerpts
- [ ] Pillar scores are correct averages of their 4 sub-pillars
- [ ] No researched score exceeds its corresponding validated score without documented justification
- [ ] IBM duplicate merged into single record
- [ ] Output file `Vendor 5-2 Researched.json` passes JSON validation (138 vendors)
- [ ] Output deployed to production at 192.168.15.51
