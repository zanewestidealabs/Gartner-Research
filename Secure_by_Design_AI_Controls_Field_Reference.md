# Secure-by-Design AI Controls — Schema & Field Reference

**Schema Version:** 1.0  
**Schema File:** `Secure_by_Design_AI_Controls_Schema.json`  
**Top-Level Key:** `secure_by_design_ai_controls_v1.0`  
**Created:** 2026-02-26  
**Source Document:** `AI_Adoption_Controls_NIST.md`  
**Purpose:** Maturity self-assessment framework for secure-by-design AI technology and service capabilities — targeting Chief Product Officers (CPOs) and product security leaders.

---

## Overview

This framework translates the NIST-aligned AI adoption controls into a structured, scoreable maturity assessment. It is designed for **Chief Product Officers** and product security teams who are embedding security, trust, and accountability into AI-powered products and services.

**Key design principles:**

- **Self-assessment first** — Scoring is maturity-based (1–5), not evidence-graded (0–5). Organizations rate themselves honestly, then validate with evidence artifacts.
- **Encryption explicit** — Data-at-rest and data-in-transit encryption are broken out as discrete, auditable sub-pillars rather than a single checkbox.
- **Accountability graphs** — Two complementary lineage/accountability graphs appear in the framework:
  - **DSO-05 (Auditability & Lineage Graph)** — Production-side: code → data → model → decision → outcome.
  - **TRM-05 (Lineage & Accountability Graph)** — Governance-side: risk assessment → approval → policy → deployment → finding → remediation.
- **NIST-anchored** — Every sub-pillar maps to AI RMF 1.0 functions (Govern, Map, Measure, Manage), with references to AI 600-1, the AI RMF Playbook, and COSAiS overlays.

> **Distinction from AI TRiSM schema:** The TRiSM schema evaluates *vendor* AI TRiSM capabilities (0–5 evidence scale). This schema evaluates an *organization's own* secure-by-design maturity (1–5 maturity scale).

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Schema (JSON)                         │
│  Secure_by_Design_AI_Controls_Schema.json                │
│  • 5 Pillars (INF, IAM, NDS, DSO, TRM)                  │
│  • 25 Sub-Pillars (4–6 per pillar)                       │
│  • 5 Maturity Criteria per sub-pillar (125 total)        │
│  • Scoring scale: 1–5 maturity levels                    │
│  • 90-day adoption plan with phased targets              │
│  • Assessment fields for organizational scoring          │
└──────────────────────────────────────────────────────────┘
```

---

## Scoring Scale (1–5 Maturity)

| Score | Level | Description |
|-------|-------|-------------|
| **1** | Not Started | No controls, processes, or awareness. The organization has not begun addressing this dimension. |
| **2** | Ad Hoc / Initial | Informal, reactive, or person-dependent practices. No documented policy or repeatable process. Controls applied inconsistently. |
| **3** | Defined / Repeatable | Documented policies and procedures exist. Controls applied consistently across most AI workloads. Some tooling in place. Measurement is limited. |
| **4** | Managed / Measured | Controls enforced via automation or tooling with defined metrics and KPIs. Evidence collected systematically. Regular reviews occur. Exceptions tracked. |
| **5** | Optimized / Adaptive | Continuous improvement driven by metrics, threat intelligence, and lessons learned. Controls self-adapt or are proactively tuned. Full auditability, cross-framework mapping, and executive reporting. |

### Evidence Expectations by Level

| Level | Expected Evidence |
|-------|-------------------|
| 1 | N/A |
| 2 | Informal notes, tribal knowledge, ad hoc procedures |
| 3 | Documented policies, architecture diagrams, runbooks, tool configurations |
| 4 | Automated dashboards, audit logs, KPI reports, test results, control validation records |
| 5 | Continuous assurance reports, executive dashboards, cross-framework crosswalks, improvement trends, third-party attestations |

---

## Coverage Grade

| Grade | Sub-Pillars ≥ Level 3 | Percentage |
|-------|------------------------|------------|
| **A** | 21–25 | 84–100% |
| **B** | 16–20 | 64–80% |
| **C** | 11–15 | 44–60% |
| **D** | 6–10 | 24–40% |
| **F** | 0–5 | 0–20% |

---

## Pillars & Sub-Pillars (5 Pillars × 4–6 Sub-Pillars = 25 Dimensions)

### Pillar 1: INF — Infrastructure for AI
*Hardened, isolated, and cryptographically protected compute and runtime environments for AI training, fine-tuning, and inference — with supply-chain assurance.*

**AI RMF Functions:** Govern / Manage / Measure

| Code | Sub-Pillar | Description |
|------|-----------|-------------|
| INF-01 | Hardened AI Runtime Isolation | Dedicated VNETs/VPCs, private endpoints, container/VM isolation for training and inference environments |
| INF-02 | Compute Access Governance | Controlled, auditable access to GPU/TPU clusters with least-privilege provisioning and cost controls |
| INF-03 | Encryption at Rest | AES-256+ encryption for all stored models, weights, datasets, and artifacts with enterprise key management |
| INF-04 | Encryption in Transit | TLS 1.3+ on all model-serving APIs, mTLS between AI services, encrypted data pipelines |
| INF-05 | AI Supply Chain Assurance | SBOM, provenance verification, and vulnerability scanning for ML frameworks, pretrained models, and dependencies |

### Pillar 2: IAM — Identity & Access for AI
*Fine-grained identity, authentication, and authorization controls for AI workspaces, APIs, agents, and HITL approval workflows.*

**AI RMF Functions:** Govern / Manage / Measure

| Code | Sub-Pillar | Description |
|------|-----------|-------------|
| IAM-01 | Fine-Grained AI Workspace IAM | RBAC/ABAC for AI workspaces, model registries, datasets, and endpoints with enterprise IdP integration |
| IAM-02 | AI API Authorization & HITL Approvals | Managed identities, scoped tokens, and HITL approval gates for high-risk AI actions |
| IAM-03 | Prompt & Response Guardrails by Role | Policy-aware input/output controls with role-based redaction, content safety, and jailbreak detection |
| IAM-04 | AI Agent Identity & Delegation | Unique agent identities, scoped delegation, action boundaries, and revocable trust chains for agentic AI |

### Pillar 3: NDS — Network & Data Security for AI
*Network isolation, boundary defenses, secure data pipelines, inference monitoring, and data sovereignty controls for AI workloads.*

**AI RMF Functions:** Govern / Manage / Map / Measure

| Code | Sub-Pillar | Description |
|------|-----------|-------------|
| NDS-01 | Segregated Training Networks | Air-gapped or broker-mediated training networks with no direct internet egress |
| NDS-02 | Model Boundary Defenses | WAF, rate limiting, prompt-injection filtering, and model-extraction defense at inference endpoints |
| NDS-03 | Secure Data Pipelines | Data provenance, integrity hashing, labeling governance, and poisoning/drift monitoring |
| NDS-04 | Inference Logging & Exfiltration Monitoring | Inference request/response logging with anomaly detection and exfiltration alerting |
| NDS-05 | Data Sovereignty & Privacy Controls | Data residency enforcement, cross-border transfer controls, PIAs, and data subject rights for AI data |

### Pillar 4: DSO — DevSecOps for AI (MLSecOps)
*Secure ML CI/CD, lineage/versioning, TEVV, risk-gated deployment, and production auditability through lineage graphs.*

**AI RMF Functions:** Govern / Manage / Map / Measure

| Code | Sub-Pillar | Description |
|------|-----------|-------------|
| DSO-01 | Secure ML CI/CD | Dependency scanning, model signing, reproducible environments, and automated security gates |
| DSO-02 | Model & Dataset Lineage / Versioning | Immutable versioning with lineage graphs and one-click rollback |
| DSO-03 | TEVV Before Release | Adversarial, bias, safety, reliability, and red-team testing before any model ships |
| DSO-04 | Risk-Gated Promotion to Production | HITL approvals, staged rollouts (canary/blue-green), kill-switch, and auto-rollback triggers |
| DSO-05 | **Auditability & Lineage Graph** | Graph-based audit trail: code → data → model → decision → outcome — queryable for regulatory and forensic use |

### Pillar 5: TRM — AI TRiSM (Trust, Risk & Security Management)
*Model governance, use-case risk assessment, trustworthiness controls, AI incident response, accountability graph, and enterprise crosswalks.*

**AI RMF Functions:** Govern / Map / Measure / Manage

| Code | Sub-Pillar | Description |
|------|-----------|-------------|
| TRM-01 | Model Governance | Approval workflows, ownership, lifecycle state management, and decommission procedures |
| TRM-02 | AI Risk Assessment by Use Case | Per-use-case risk assessment with impact, context, stakeholders, and failure mode analysis |
| TRM-03 | Trustworthiness Controls | Bias mitigation, explainability, privacy preservation, and robustness guarantees with metrics |
| TRM-04 | AI Incident Response & Monitoring | AI-specific runbooks for hallucinations, jailbreaks, data leakage; real-time monitoring and SOC integration |
| TRM-05 | **Lineage & Accountability Graph** | Governance-side accountability: risk assessment → approval → policy → deployment → finding → remediation |
| TRM-06 | Enterprise Framework Crosswalk | Living crosswalk to NIST CSF, ISO 42001, EU AI Act, and sector-specific regulations |

---

## The Two Accountability Graphs

This framework introduces two complementary graph structures that together provide end-to-end traceability from governance intent to production outcome:

### DSO-05: Auditability & Lineage Graph (Production)
```
code commit ──→ dataset version ──→ training run ──→ model artifact
     │                                                      │
     └───────────── reproducibility ─────────────────→ deployment
                                                            │
                                                    inference decision
                                                            │
                                                     downstream outcome
```
**Purpose:** Forensic reconstruction. "What code, data, and model produced this specific output?"

### TRM-05: Lineage & Accountability Graph (Governance)
```
risk assessment ──→ approval record ──→ policy version ──→ model deployment
                                                                │
                                                      monitoring finding
                                                                │
                                                      remediation action
```
**Purpose:** Organizational accountability. "Which governance artifacts authorized this AI system, and how were issues addressed?"

### Cross-Reference
At the **model deployment** node, both graphs converge — enabling full traceability from the boardroom decision to approve an AI use case down to the specific training data and code that produced an inference result.

---

## NIST Framework Mapping

| NIST Source | How It's Used |
|-------------|---------------|
| **AI RMF 1.0** (Govern, Map, Measure, Manage) | Every sub-pillar maps to 1–3 AI RMF functions |
| **AI 600-1** (Generative AI Profile) | GenAI-specific mitigations in IAM-03, NDS-02, NDS-04, DSO-03, TRM-04 |
| **AI RMF Playbook** | Suggested actions inform maturity criteria across all pillars |
| **COSAiS** (SP 800-53 Overlays) | Future binding: as overlays publish, bind sub-pillars to SP 800-53 control IDs (AC-*, AU-*, SI-*, PM-*) |

---

## 90-Day Adoption Plan

| Phase | Weeks | Focus | Target Sub-Pillars |
|-------|-------|-------|-------------------|
| **Stand Up Governance** | 1–3 | AI Risk Council, genAI policy, baseline scoring | TRM-01, TRM-02, TRM-06, IAM-01 |
| **Inventory & Risk-Map** | 2–5 | AI system inventory, impact mapping, workload tagging | TRM-02, DSO-02, INF-05, IAM-04 |
| **Foundational Protections** | 4–8 | IAM, network isolation, encryption, TEVV gates | INF-01, INF-03, INF-04, IAM-02, NDS-01, NDS-02, DSO-03 |
| **Measure, Monitor & Respond** | 6–12 | Telemetry, incident runbooks, lineage graphs, re-score | NDS-04, TRM-04, DSO-05, TRM-05, TRM-03 |

---

## Assessment Fields

### Organization Info

| Field | Type | Description |
|-------|------|-------------|
| `organization` | String | Name of the organization being assessed |
| `assessment_date` | Date | Date of the assessment (YYYY-MM-DD) |
| `assessor` | String | Name or role of the assessor |
| `business_unit` | String | Business unit or product line in scope |
| `ai_workload_types` | Array | AI workload types in scope: genAI, predictive, agentic, multi-agent, fine-tuning, RAG |

### Scores

| Field | Type | Description |
|-------|------|-------------|
| `overall_maturity_score` | Number | Average across all 25 sub-pillar scores (1.00–5.00) |
| `pillar_scores` | Object | Average maturity per pillar (INF, IAM, NDS, DSO, TRM) |
| `sub_pillar_scores` | Object | Maturity score (1–5) per sub-pillar, keyed by code |
| `coverage_grade` | String | Letter grade (A–F) based on sub-pillars scoring ≥3 |

### Evidence & Gaps

| Field | Type | Description |
|-------|------|-------------|
| `sub_pillar_evidence` | Object | Evidence notes or artifact references per sub-pillar |
| `sub_pillar_gaps` | Object | Identified gaps and recommended actions per sub-pillar |
| `priority_remediation` | Array | Ordered list of sub-pillar codes to prioritize for improvement |

---

## Quick-Start Checklist

- [ ] Approve AI governance policy and genAI acceptable-use profile (TRM-01, IAM-03)
- [ ] Stand up AI system inventory; classify genAI vs. predictive vs. agentic (TRM-02, IAM-04)
- [ ] Enforce least-privilege IAM and network isolation for AI services (IAM-01, IAM-02, NDS-01)
- [ ] Enable encryption at rest and in transit for all AI artifacts (INF-03, INF-04)
- [ ] Implement TEVV and risk gates before any AI feature ships (DSO-03, DSO-04)
- [ ] Configure boundary defenses for LLM endpoints (NDS-02)
- [ ] Operationalize AI monitoring and incident response (TRM-04, NDS-04)
- [ ] Deploy auditability graph (DSO-05) and accountability graph (TRM-05)
- [ ] Prepare enterprise framework crosswalk for audit reporting (TRM-06)
- [ ] Baseline-score all 25 sub-pillars and set 90-day improvement targets

---

## Sources

- **NIST AI Risk Management Framework (AI RMF 1.0)** — Govern, Map, Measure, Manage functions
- **NIST Generative AI Profile (AI 600-1)** — GenAI-specific actions and mitigations
- **NIST AI RMF Playbook** — Suggested actions by function/subcategory
- **NIST AI RMF Crosswalks & Resources** — Mappings to CSF, ISO, and other standards
- **COSAiS (SP 800-53 Control Overlays for Securing AI Systems)** — LLM, predictive, agent, and developer control overlays
