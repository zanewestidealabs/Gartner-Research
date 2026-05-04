# Preemptive Cybersecurity — Schema & Evaluation Field Reference

**Schema Version:** 1.0  
**Schema File:** `Preemptive_Cybersecurity_Schema.json`  
**Top-Level Key:** `preemptive_cybersecurity_taxonomy_v1.0`  
**Created:** 2026-02-23  
**Purpose:** Evaluate vendors against the preemptive cybersecurity capability taxonomy — proactive defense architectures that prevent, disrupt, and neutralize threats before exploitation occurs.

---

## Overview

This schema defines the evaluation framework for vendors in the **Preemptive Cybersecurity** market. Unlike reactive security (detect-and-respond), preemptive cybersecurity shifts the advantage to defenders by:

- **Discovering and closing exposures** before adversaries find them
- **Dynamically mutating** the environment to deny static targeting
- **Actively disrupting** adversary operations through deception and counter-operations
- **Continuously validating** that defenses actually work against real attack techniques

> **Key distinction:** Vendors are evaluated on **capability alignment** with the preemptive definition — not solely on whether they use AI. AI-first and startup markers are retained for market segmentation but are secondary to capability coverage.

---

## Scoring Scale (0-5)

| Score | Level | Description |
|-------|-------|-------------|
| **0** | No Evidence | No publicly verifiable evidence of capability in this sub-pillar |
| **1** | Minimal | Basic or manual capability; no automation, analytics, or continuous operation |
| **2** | Generic Claims | Marketing mentions the capability but lacks named products, technical docs, or specifics |
| **3** | Demonstrated | Documented capability with named products or features, some technical detail, identifiable use cases |
| **4** | Advanced | Named products with measurable outcomes, integration points, customer validation, or analyst recognition |
| **5** | Market-Leading | Best-in-class capability with deep technical evidence, extensive customer base, analyst leadership recognition |

---

## Pillars & Sub-Pillars (4 Pillars × 4 Sub-Pillars = 16 Dimensions)

### Pillar 1: EXM — Exposure Management
*Continuous discovery, assessment, and prioritization of exposures across the full attack surface before adversaries can exploit them.*

| Code | Sub-Pillar | Description |
|------|-----------|-------------|
| EXM-01 | Attack Surface Management | Continuous discovery of all external/internal assets, shadow IT, cloud resources, and third-party integrations for real-time attack surface visibility |
| EXM-02 | Continuous Threat Exposure Management | Operationalized programs that scope, discover, prioritize, validate, and mobilize exposure responses on a continuous cycle (Gartner CTEM framework) |
| EXM-03 | Vulnerability Prioritization & Management | Risk-based prioritization using exploitability context, threat intelligence, asset criticality, and business impact beyond CVSS alone |
| EXM-04 | Third-Party & Supply Chain Exposure | Monitoring exposure from third-party vendors, supply chain dependencies, open-source components, and partner integrations |

### Pillar 2: AMT — Automated Moving Target Defense
*Dynamic mutation and randomization of the IT environment to increase attacker uncertainty, cost, and complexity.*

| Code | Sub-Pillar | Description |
|------|-----------|-------------|
| AMT-01 | Polymorphic & Morphing Defense | Runtime mutation of memory layouts, network configs, API endpoints, and system identifiers to prevent static targeting |
| AMT-02 | Runtime Application Protection | In-process protection through instrumentation, code hardening, and real-time exploit prevention without signatures |
| AMT-03 | Dynamic Network & Infrastructure Defense | Automated reconfiguration of network topology and micro-segmentation to deny adversaries a stable operating environment |
| AMT-04 | Identity & Credential Rotation | Automated rotation and ephemeral provisioning of credentials, tokens, and keys to limit credential-based attack windows |

### Pillar 3: ADR — Adversary Disruption
*Active measures to deceive, misdirect, delay, and disrupt adversary operations — exposing TTPs before damage occurs.*

| Code | Sub-Pillar | Description |
|------|-----------|-------------|
| ADR-01 | Deception Technology | Decoys, honeypots, honeytokens, and breadcrumbs to detect lateral movement and reconnaissance with high-fidelity alerts |
| ADR-02 | Threat Intelligence Operationalization | Automated ingestion, correlation, and actioning of threat intelligence to preemptively block adversary infrastructure and TTPs |
| ADR-03 | Proactive Threat Hunting | Hypothesis-driven hunting that proactively searches for adversary presence and pre-attack indicators before alerts trigger |
| ADR-04 | Counter-Adversary Operations | Attribution, tracking, takedowns, adversary infrastructure disruption, and dark web monitoring |

### Pillar 4: PPM — Preemptive Posture Management
*Continuous validation, simulation, and hardening to ensure defenses work against real-world attack techniques.*

| Code | Sub-Pillar | Description |
|------|-----------|-------------|
| PPM-01 | Breach & Attack Simulation | Automated simulation of attack chains against production environments to validate detection and prevention controls |
| PPM-02 | Security Control Validation | Systematic testing that deployed security controls are correctly configured, active, and effective |
| PPM-03 | Penetration Testing & Red Teaming | Automated/continuous penetration testing and red team capabilities that identify exploitable paths |
| PPM-04 | Cloud Security Posture Management | Continuous assessment of cloud configurations, entitlements, and workload security against best practices |

---

## Vendor Fields

### Identity & Company Info

| Field | Type | Description |
|-------|------|-------------|
| `vendor` | String | Official company name |
| `website` | URL | Primary company URL |
| `headquarters` | String | HQ city, state/country |
| `year_founded` | Integer | Year the company was founded |
| `employee_count_range` | String | Estimated employee bracket (e.g., "51-200", "201-500") |
| `funding_stage` | String | Latest funding round: Seed, Series A-F, IPO, Acquired, Bootstrapped |
| `total_funding` | String | Total funding raised to date |

### Market Markers

| Field | Type | Description |
|-------|------|-------------|
| `is_startup` | Boolean | Founded within last 7 years OR pre-IPO with <500 employees |
| `is_ai_first` | Boolean | AI/ML is a core differentiator in their primary product — **secondary to capability alignment** |
| `ir_focus_type` | String | Primary market focus: SMB, Mid-Market, Enterprise, All |
| `region` | String | Primary region of operation |
| `specialization` | String | Primary security specialization |

### Capability Evaluation

| Field | Type | Description |
|-------|------|-------------|
| `primary_capability` | String | Single strongest preemptive capability pillar code (EXM, AMT, ADR, PPM) |
| `capability_coverage` | Array | List of sub-pillar codes where vendor has demonstrated capability |
| `capability_coverage_count` | Integer | Number of sub-pillars covered out of 16 total |
| `product_names` | Array | Key product or platform names |
| `description` | String | Brief description of vendor and their preemptive security approach |
| `key_differentiators` | String | What sets this vendor apart in preemptive cybersecurity |

---

## Coverage Grade

| Grade | Sub-Pillars Covered | Percentage |
|-------|---------------------|------------|
| **A** | 13-16 | 81-100% |
| **B** | 10-12 | 63-75% |
| **C** | 7-9 | 44-56% |
| **D** | 4-6 | 25-38% |
| **F** | 1-3 | 6-19% |

> **Note:** Most vendors will cover 3-6 sub-pillars (Grade D-C). Very few will achieve Grade A. This is expected — the schema intentionally spans the full preemptive landscape to reveal capability gaps and market white space.

---

## Evidence Policy

### Valid Sources (by tier)

| Tier | Type | Examples | Weight |
|------|------|----------|--------|
| **A** | Vendor documentation | Product pages, Admin docs, API refs, Release notes, Whitepapers | 1.0 |
| **A** | Analyst reports | Gartner MQ/Market Guide, Forrester Wave, IDC MarketScape, KuppingerCole | 1.0 |
| **B** | Technical media | SecurityWeek, Dark Reading, Help Net Security, CSO Online, The Hacker News | 0.85 |
| **B** | Benchmarks/Case studies | Customer case studies, Public bake-offs, Government RFP evals | 0.85 |
| **C** | Conference/Academic | RSAC, Black Hat, DEF CON, arXiv, Standards drafts | 0.7 |
| **C** | Professional networks | Engineer-authored LinkedIn/Blogs with technical detail | 0.7 |

---

## Evaluation Philosophy

1. **Capability-first:** The primary evaluation criterion is whether the vendor's product delivers capabilities that align with the preemptive cybersecurity definition. AI usage is noted but not required.

2. **Coverage as differentiator:** Vendors are not expected to cover all 16 sub-pillars. Coverage breadth reveals platform plays vs. point solutions and identifies market consolidation opportunities.

3. **Depth over breadth:** A vendor with deep capability in 4 sub-pillars (score 4-5) is valued higher than one with shallow presence across 10 sub-pillars (score 1-2).

4. **Preemptive vs. reactive distinction:** Vendors must demonstrate that their capabilities operate **before** an incident — not just faster detection-and-response. SOAR, SIEM, and EDR alone do not qualify unless they include explicit preemptive capabilities (e.g., BAS integration, deception, AMTD).

5. **Market markers are secondary:** `is_ai_first` and `is_startup` are retained for segmentation and trend analysis but do not influence capability scores.

---

## Integration Notes

- **Schema file:** `Preemptive_Cybersecurity_Schema.json`
- **Top-level key:** `preemptive_cybersecurity_taxonomy_v1.0`
- **Structure type:** `flat` (compatible with app.py schema loader)
- **Registered in:** `SCHEMA_REGISTRY` and `SCHEMA_DISPLAY` in `app.py`
- **Abbreviation:** `PreCyber`
- **Vendor data file convention:** `Preemptive_Cybersecurity_Vendor_[version].json`
- **Dimensions:** 4 pillars × 4 sub-pillars = **16 total evaluation dimensions**

---
*This schema and reference guide are designed to be updated as the preemptive cybersecurity landscape evolves.*
