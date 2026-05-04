# MDR Services Schema - Field Reference

**Schema File:** `MDR_Services_Schema.json`  
**Version:** 1.0  
**Date:** March 2026  
**Lineage:** Extends Preemptive Cybersecurity Schema v1.0; incorporates DFIR Capability Taxonomy v3.2 (IR Assistance Component model) and Secure-by-Design AI Controls Schema v1.0 (AI governance patterns)

---

## Overview

This schema evaluates Managed Detection and Response (MDR) service providers across two independent evaluation scales:

1. **Capability Maturity Scale** - 8 pillars × 4 sub-pillars = 32 sub-pillars, scored 0–5
2. **Pricing Model Evaluation Scale** - 5 dimensions, scored 0–5

The dual-scale design reflects the reality that MDR vendor selection depends on both *what* the vendor can do (capabilities) and *how* they charge for it (commercial construct transparency and maturity).

---

## Dual Evaluation Architecture

### Scale 1: Capability Maturity (0–5)

| Score | Level | Description |
|-------|-------|-------------|
| 0 | No Evidence | No publicly verifiable evidence of capability in this sub-pillar |
| 1 | Minimal | Basic or manual capability; no automation, analytics, or continuous operation |
| 2 | Generic Claims | Marketing mentions the capability but lacks named products, technical docs, metrics, or specifics |
| 3 | Demonstrated | Documented capability with named products or features, some technical detail, and identifiable use cases |
| 4 | Advanced | Named products with measurable outcomes, integration points, customer validation, or analyst recognition. Automation and continuous operation present |
| 5 | Market-Leading | Best-in-class capability with deep technical evidence, extensive customer base, analyst leadership recognition, measurable impact metrics, and continuous innovation |

### Scale 2: Pricing Model Evaluation (0–5)

| Score | Level | Description |
|-------|-------|-------------|
| 0 | No Evidence | No public information available about this pricing dimension |
| 1 | Opaque | Pricing exists but is entirely opaque - no public detail on structure, components, or methodology |
| 2 | Basic | General pricing information available but limited transparency - bundled quotes without component breakdown |
| 3 | Structured | Defined pricing structure with identifiable components, documented on website or in sales materials |
| 4 | Transparent & Flexible | Clear component-based pricing with published tiers, calculators, or configurators. Demonstrated client flexibility |
| 5 | Composable Best Practice | Fully composable pricing model with transparent subscription, usage, fixed, and success-fee components. Real-time usage dashboards, documented KPI alignment, and demonstrated risk-sharing mechanisms |

---

## Capability Pillars (Scale 1)

### TDR - Standard Threat Detection, Investigation & Response

The core MDR baseline. Every MDR provider should demonstrate competence here. This pillar evaluates the fundamental detection-to-response pipeline.

| Sub-Pillar | Name | Focus |
|------------|------|-------|
| TDR-01 | Signal Correlation & Alert Triage | Multi-source telemetry correlation, alert prioritization, false positive reduction |
| TDR-02 | Investigation & Root Cause Analysis | Guided investigation, attack chain reconstruction, scope determination |
| TDR-03 | Response Orchestration & Containment | Automated/human-initiated response, playbooks, containment actions |
| TDR-04 | SLA & MTTD/MTTR Performance | Published SLAs, measurable detection/response times, performance reporting |

---

### PTI - Preemptive Threat Intelligence

Traditionally the domain of specialized threat research companies (e.g., Recorded Future), this capability is now increasingly achievable through domain-specific AI agents and LLMs. Evaluates the vendor's ability to operationalize threat intelligence proactively rather than reactively.

| Sub-Pillar | Name | Focus |
|------------|------|-------|
| PTI-01 | Threat Intelligence Operationalization | Feed ingestion, IOC correlation, intelligence-to-detection pipeline |
| PTI-02 | Predictive Threat Analytics | ML-driven threat forecasting, vulnerability trend analysis, exploitability prediction |
| PTI-03 | Behavior-Based Anomaly Detection | UEBA, behavioral baselines, insider threat detection, lateral movement detection |
| PTI-04 | Dark Web & Adversary Tracking | Dark web monitoring, leaked credentials, adversary campaign tracking, early warning |

---

### ADA - Autonomous Deception & AMTD

Proactive, preventative capabilities that shift MDR from reactive monitoring to actively disrupting adversary operations. Evaluates deception technology, dynamic defense, and attack surface management.

| Sub-Pillar | Name | Focus |
|------------|------|-------|
| ADA-01 | Deception Technology & Honeypots | Managed deception deployment, honeypots/tokens, breadcrumbs, high-fidelity alerting |
| ADA-02 | Automated Moving Target Defense | Runtime mutation, dynamic micro-segmentation, credential rotation, AMTD |
| ADA-03 | Dynamic Attack Surface Management | EASM, continuous asset discovery, exposure assessment, shadow IT detection |
| ADA-04 | Counter-Adversary Operations | Takedown services, threat hunting, adversary attribution, campaign disruption |

---

### DIS - Disinformation & Identity Security

Emerging capability area addressing threats that evade traditional security controls - deepfakes, impersonation, and narrative attacks targeting organizational reputation and executive identity.

| Sub-Pillar | Name | Focus |
|------------|------|-------|
| DIS-01 | Deepfake & Synthetic Media Detection | AI-generated content detection, synthetic audio/video, media authentication |
| DIS-02 | Identity Impersonation Defense | BEC detection, executive impersonation, account takeover, credential stuffing |
| DIS-03 | Narrative & Social Engineering Detection | Influence operations, social engineering campaigns, phishing analysis |
| DIS-04 | Brand & Executive Protection | Brand monitoring, domain squatting, social media impersonation, reputation defense |

---

### IRA - IR Support & Assistance

MDR-adjacent incident response capability modeled as the "Assistance Component" from the DFIR capability taxonomy - IR as a service feature within MDR, not pureplay DFIR. Evaluates how well the MDR provider can help clients through incidents without requiring separate DFIR retainers.

| Sub-Pillar | Name | Focus |
|------------|------|-------|
| IRA-01 | Incident Scoping & Triage | Severity assessment, affected system identification, evidence preservation guidance |
| IRA-02 | Containment & Isolation Support | Host isolation, network segmentation, credential suspension, evidence preservation |
| IRA-03 | Recovery & Restoration Guidance | Backup verification, eradication support, system rebuild recommendations |
| IRA-04 | Post-Incident Review & Reporting | After-action review, root cause analysis, improvement recommendations |

---

### AIO - AI Adoption in MDR Operations

Comprehensive assessment of how AI is actually embedded in MDR service delivery - beyond marketing claims. Evaluates whether AI delivers measurable operational improvements or is superficial.

| Sub-Pillar | Name | Focus |
|------------|------|-------|
| AIO-01 | AI in Detection Engineering | AI-assisted rule creation, ML false positive reduction, detection coverage assessment |
| AIO-02 | AI in Investigation & Triage | Automated triage, AI-generated summaries, context enrichment, case prioritization |
| AIO-03 | AI in Response Automation | Autonomous resolution, adaptive response, multi-step remediation beyond SOAR |
| AIO-04 | AI Transparency & Explainability | Explainable outputs, audit trails, clear AI vs. human delineation, quality metrics |

---

### AID - AI Development & Platform Maturity

The vendor's AI investment depth - domain-specific models, governance, supply chain assurance, and innovation pipeline. Distinguishes genuine AI engineering from generic GPT-wrapper implementations.

| Sub-Pillar | Name | Focus |
|------------|------|-------|
| AID-01 | Domain-Specific AI / LLM Investment | Named security AI models, security-specific training, published research |
| AID-02 | AI Model Governance & Lifecycle | Model versioning, pre-deployment testing, drift detection, update cadence |
| AID-03 | AI Supply Chain & Trustworthiness | Foundation model provenance, third-party AI risk, training data governance |
| AID-04 | AI-Driven Service Innovation | New AI-enabled services, expanded coverage, innovation pipeline |

---

### SOG - Service Operations & Governance

Operational maturity of the MDR service - the human and process foundation that ensures consistent, accountable service delivery regardless of AI adoption level.

| Sub-Pillar | Name | Focus |
|------------|------|-------|
| SOG-01 | 24/7 SOC Coverage & Analyst Model | Geographic coverage, tier structure, dedicated/named analysts, certifications |
| SOG-02 | Client Engagement & Transparency | Onboarding, business reviews, escalation paths, client portals, satisfaction |
| SOG-03 | Compliance & Regulatory Alignment | SOC 2, ISO 27001, regulated industry support, data residency |
| SOG-04 | Reporting Quality & Metrics | Executive and technical reporting, trend analysis, KPI dashboards, ROI reporting |

---

## Pricing Model Evaluation Dimensions (Scale 2)

These dimensions are derived directly from Gartner's composable pricing research:
- *Pricing Constructs That Support Profitable BPS Revenue* (G00826132, April 2025)
- *Outcome-Based Pricing Fails Tech CEOs in Services* (G00846386, February 2026)

| Code | Dimension | What It Evaluates |
|------|-----------|-------------------|
| PRC-SUB | Subscription Transparency | Clarity of recurring fees: human time, platform, AI tools, bundles |
| PRC-USG | Usage-Based Alignment | Consumption-based fees: API calls, data volume, compute, AI inference |
| PRC-FIX | Fixed Delivery Pricing | One-time costs: setup, integration, customization, playbook creation |
| PRC-SUC | Success & Outcome Fees | Fees-at-risk, success bonuses, per-resolution fees, KPI-linked pricing |
| PRC-COM | Composability & Model Maturity | Overall model maturity: combinable components, predictable budgeting, risk balance |

### Pricing Capability Alignment

| Pricing Component | Most Applicable MDR Capabilities |
|-------------------|----------------------------------|
| Subscriptions | Standard TDIR, Disinformation monitoring, Deception-as-a-Service |
| Usage-Based | Preemptive Threat Intelligence (AI compute, data volume, inference) |
| Fixed Delivery | AMTD environment deployment, complex integrations, custom playbooks |
| Success Fees | TDIR performance (MTTD/MTTR), AI-automated resolution per-incident |

---

## Coverage Grade

Letter grade based on percentage of capability sub-pillars with score ≥ 1:

| Grade | Sub-Pillars Covered | Percentage |
|-------|---------------------|------------|
| A | 26–32 | 81–100% |
| B | 20–25 | 63–78% |
| C | 14–19 | 44–59% |
| D | 8–13 | 25–41% |
| F | 1–7 | 3–22% |

---

## Market Position Classifications

### MDR Service Type

| Type | Definition |
|------|------------|
| Pureplay MDR | Primary business is managed detection and response services |
| Extended MDR | MDR as core offering within a broader managed security services portfolio |
| Platform MDR | Technology vendor offering MDR built atop their own EDR/XDR platform |
| IR-Enhanced MDR | MDR provider with significant DFIR retainer and incident response capabilities |

### IR Focus Type (from DFIR Schema)

| Type | Definition |
|------|------------|
| Core Competency | Incident response is a primary service line with dedicated DFIR specialists |
| Assistance Component | IR provided as support layer or feature within the MDR contract |

---

## ROI Measurement Framework

Based on the research finding that AI integration in MDR will NOT reduce costs but should be evaluated on enhanced speed, quality, and scope:

| Category | KPIs |
|----------|------|
| Detection & Response Speed | MTTD reduction %, MTTR reduction %, SLA adherence rate |
| Resolution Autonomy | Incidents resolved without client intervention, client clarification volume |
| Expanded Visibility | Alert investigation increase vs. baseline, telemetry sources covered |
| Alert & Output Quality | False positive rate trend, AI hallucination incidents, report quality |
| Internal Resource Impact | Analyst time freed, client triage burden reduction, analyst upskilling |
| Business Impact | Financial damage prevention, reputation damage prevention, regulatory penalty avoidance |

---

## Vendor Fields

| Field | Type | Description |
|-------|------|-------------|
| vendor | string | Official company name |
| website | string | Primary company URL |
| headquarters | string | HQ city, state/country |
| year_founded | integer | Year founded |
| employee_count_range | string | Estimated employee bracket |
| funding_stage | string | Seed, Series A-F, IPO, Acquired, Bootstrapped |
| total_funding | string | Total funding raised to date |
| is_startup | boolean | Founded within last 7 years OR pre-IPO with <500 employees |
| is_ai_first | boolean | AI/ML is a core differentiator in MDR service delivery |
| region | string | Primary region of operation |
| mdr_service_type | string | Pureplay MDR, Extended MDR, Platform MDR, or IR-Enhanced MDR |
| ir_focus_type | string | Core Competency or Assistance Component |
| target_market | string | SMB, Mid-Market, Enterprise, All |
| primary_capability | string | Strongest capability pillar code |
| capability_coverage | array | Sub-pillar codes with demonstrated capability |
| capability_coverage_count | integer | Count of sub-pillars covered (out of 32) |
| pricing_model_type | string | Subscription-Only, Usage-Based, Composable, Outcome-Based, Hybrid |
| description | string | Brief vendor and service approach description |
| key_differentiators | string | What sets this vendor apart |
| product_names | array | Key product/platform/service names |
| telemetry_sources | array | Supported types: Endpoint, Network, Cloud, Identity, Email, OT/IoT |
| mitre_coverage | string | Documented MITRE ATT&CK coverage level |

---

## Source Documents

| Document | Gartner ID | Key Contribution to Schema |
|----------|-----------|---------------------------|
| Pricing Constructs That Support Profitable BPS Revenue | G00826132 | Composable pricing framework, Figure 1 & 2 |
| Outcome-Based Pricing Fails Tech CEOs in Services | G00846386 | Why outcome-based pricing fails, composable alternative |
| NotebookLM MDR Research | N/A | MDR capability definitions, AI pricing impact, ROI measurement |
| Agentic AI: The New Digital Forensics Workhorse | G00846698 | DFIR → MDR IR Assistance Component model |
| Preemptive Cybersecurity Schema v1.0 | N/A | Parent schema structure, pillar/sub-pillar pattern |
| Secure-by-Design AI Controls Schema v1.0 | N/A | AI governance patterns, maturity scoring model |
| DFIR Capability Taxonomy v3.2 | N/A | IR pillar structure, "Assistance Component" concept |
