# ASAF Framework Foundations: Stages, Principles, and Governing Logic

**Working Draft — Agentic SOC Architecture Framework (ASAF) | Framework Reference**

---

## Why a Foundation Section Exists

Every operational framework carries assumptions. ASAF carries several: that autonomy is better structured as a continuum than a switch; that ethics belongs inside the control loop, not above it; that human roles evolve rather than disappear. These assumptions do not belong buried inside dimension chapters. They shape how everything else in this framework should be read.

This section does three things. It maps the six maturity stages — what they mean, what separates them, and what realistic adoption looks like. It states the eight governing principles — the architectural commitments that distinguish ASAF from a collection of best practices. And it shows how those principles connect across the eleven dimensions that form the framework's operational logic.

---

## Part One: The Six Maturity Stages

The ASAF maturity model describes a transformation in how security operations are structured — from alert-queue processing by human analysts to a self-regulating autonomous control system governed by humans. The six stages are not milestones on a project plan. They are structural configurations, each with a characteristic operational posture, human role model, and governance approach.

Most large enterprises in 2025 sit at Stage 0 or 1. A small number have begun Stage 2 transitions. Stage 3 is the credible near-term target for advanced security programs over the next three to five years.

---

### Stage 0 — Traditional (Tiered SOC)

The classic L1/L2/L3 analyst model that has defined enterprise security operations since the early 2000s. Operations are alert-driven and reactive. Human analysts process queues, follow runbooks, and escalate according to tier boundaries. SIEM and SOAR are the primary tools. Governance lives in policy documents that are reviewed episodically.

**Autonomy level:** None. Humans execute every detection, triage, investigation, and response action.

**Human model:** Tiered analysts with senior analysts as escalation endpoints and managers as approvers.

**Governance model:** Static policy documents. Periodic compliance reviews. No real-time enforcement.

**Detection posture:** Alert-queue processing. Signature and rule-based detection. SIEM correlation as the primary aggregation layer.

**Knowledge model:** Tribal knowledge, runbooks, and unstructured wikis. No structured operational knowledge graph.

**Characteristic failure mode:** Alert fatigue and throughput bottlenecks drive hiring cycles without improving detection quality. The system scales human cost faster than it scales detection capability.

*Approximate timeline: Dominant model from 2020 to 2024.*

---

### Stage 1 — Assisted (AI-Augmented)

AI and automation assist analysts with triage, enrichment, and playbook execution. Humans still own all decisions. Automation reduces mean-time-to-respond for known threat patterns. Alert fatigue begins to be addressed — but the tier model remains structurally intact.

**Autonomy level:** Low. Automation executes pre-approved playbooks. Humans approve all significant actions.

**Human model:** Tiered analysts assisted by automation. Senior analysts focus on complex investigations.

**Governance model:** Policy codified in playbooks. Automated compliance checks on known scenarios. Policy remains document-centric.

**Detection posture:** ML-assisted prioritization. Behavioral anomaly detection augmenting signature rules.

**Knowledge model:** Structured runbooks. Case management with enrichment. Basic threat intelligence integration.

**Characteristic failure mode:** Automation debt. Playbooks proliferate without governance or maintenance. False positive rates are suppressed rather than solved.

*Approximate timeline: Dominant model from 2024 to 2025.*

---

### Stage 2 — Supervised Autonomy (Agents with Approval Gates)

Agents execute bounded, pre-authorized investigation and response tasks autonomously. Humans approve significant actions through intent-based authorization. The tier model weakens as agents absorb L1 and L2 workloads.

**Autonomy level:** Moderate. Agents autonomously investigate and contain within pre-authorized scope. Humans approve scope-expanding actions.

**Human model:** Analysts become agent supervisors. Role identity shifts from throughput execution to oversight and exception handling.

**Governance model:** Governance rules embedded in agent execution frameworks. Authority scope defined per agent class. Policy begins to become machine-interpretable.

**Detection posture:** Agent-driven detection hypotheses. Continuous signal fusion. CTEM integration begins.

**Knowledge model:** Security Knowledge Graph prototype. Policy and evidence begin to link. Adversary model is tracked.

**Characteristic failure mode:** Governance theater — authority boundaries defined in documents but not technically enforced. The tier model persists in behavior even as titles change.

*Approximate timeline: Leading-edge programs from 2025 to 2026.*

---

### Stage 3 — Directed Autonomy (Intent-Driven Operations)

Humans define operational intent, scope constraints, and ethical boundaries. Agents plan, reason, and execute autonomously within those bounds. Escalation is replaced by bounded exception handling. The tier model is fully eliminated.

**Autonomy level:** High. Agents plan multi-step investigation and response chains. Humans define scope and handle genuine novelty.

**Human model:** Post-tier roles emerge: Security Architects define scope and intent. Response Authorities approve novel actions. Governance Officers maintain ethical bounds.

**Governance model:** Machine-interpretable policy. An ethics engine runs as an operational control loop. Authority is modeled in the knowledge graph.

**Detection posture:** Competing hypothesis model. Continuous pre-emptive and reactive operations. Exposure-driven prioritization is the primary operational model.

**Knowledge model:** Active Security Knowledge Graph. Governance, confidence, and adversary entities are first-class nodes.

**Characteristic failure mode:** Governance engine gaps — ethics and authority modeled incompletely, with edge cases exposed in incidents. Human role identity crisis as governance roles feel less valued than operational roles.

*Approximate timeline: Advanced programs from 2026 to 2027.*

---

### Stage 4 — Collaborative Agentic (Agent-First with Human Governance)

Agent-first operations across all security functions. Humans govern legitimacy, ethics, and organizational intent. Agents coordinate, compete, and resolve conflicts autonomously. DFIR, threat research, and exposure management are continuous functions — not projects.

**Autonomy level:** Very high. Agents handle all operational execution. Humans maintain governance authority and handle ethics-boundary decisions.

**Human model:** Governance Officers hold ethical veto authority. Security Strategists define long-horizon intent. Assurance Officers validate agent behavior continuously.

**Governance model:** Governance as a continuous operational signal. The ethics engine enforces proportionality, legality, and scope in real time.

**Detection posture:** Fully continuous. CTEM, DFIR, threat research, and response are unified and simultaneously active.

**Knowledge model:** Full SKG operational. The graph drives planning, reasoning, orchestration, and artifact generation.

**Characteristic failure mode:** Governance overconfidence — governance officers trust the system without adequate oversight rigor. Vendor concentration limits constitutional authority.

*Approximate timeline: Vanguard programs from 2027 to 2028.*

---

### Stage 5 — Fully Agentic (Autonomous Control System)

Security Operations is a self-regulating autonomous control system. Agents continuously sense, reason, act, and learn across all security domains. Humans govern intent, audit outcomes, and hold constitutional authority over the system's ethical and legal boundaries.

**Autonomy level:** Full. Agents operate the security control system. Humans govern the governing model itself.

**Human model:** Constitutional Governance role defines system values and authority boundaries. Chief Trust Officer owns audit and legitimacy. Strategic Security Architect owns long-horizon system design.

**Governance model:** Ethics and governance are part of the operating kernel. Every action is governed, logged, explainable, and revocable.

**Detection posture:** Predictive and pre-emptive by default. Adversary modeling informs continuous exposure management and detection architecture.

**Knowledge model:** The SKG is self-evolving. It continuously integrates threat intelligence, incident learning, and governance updates without human curation.

**Characteristic failure mode:** Adversarial manipulation of governance boundaries. Adversaries probe authority models and attempt to exploit confidence thresholds. Constitutional resilience requires continuous red-team testing.

*Approximate timeline: Theoretical horizon from 2028 to 2030.*

---

## What Stage Are You At?

The ASAF Maturity Worksheet in the appendix provides a structured self-assessment across all eleven dimensions. Most enterprise programs find that their stage varies significantly by dimension — they may be at Stage 2 in agent execution while remaining at Stage 0 in knowledge graph architecture. That variance is the diagnostic signal. The lowest-scoring dimensions constrain the capability ceiling of the dimensions that score higher.

The most common stage distribution in 2025: Stage 1 across SEN and RSN, Stage 0 across GOV and OPS, Stage 0 to 1 across LRN and HUM.

---

## Part Two: The Eight Governing Principles

The governing principles are not aspirational statements. They are architectural commitments — choices about how the framework is structured that distinguish it from incremental process improvement. An organization can adopt ASAF's tools without adopting its principles. But if it does, it will build a more expensive version of what it already has.

Each principle is stated as a factual claim about how agentic security operations work at maturity. Disagreement with a principle is disagreement with the framework's premises, not disagreement with its implementation details.

---

### P1 — Security Operations is a Cybernetic System

> "Security Operations is a cybernetic system — a continuous feedback loop of sensing, reasoning, action, and learning — not a linear workflow of tiered human escalations."

The cybernetic model is foundational. A cybernetic system maintains a desired state through continuous sensing and corrective action. A linear escalation model does not — it responds to threshold crossings, not continuous state divergence. The difference between these architectures is not a matter of tool selection. It is a matter of how the system is designed to behave when it encounters something it has not seen before.

ASAF's four primary dimensions — SEN, RSN, ACT, LRN — form the operational feedback loop. The remaining seven dimensions structure, govern, coordinate, and sustain it. But the loop is primary. Everything else serves the loop.

---

### P2 — Governance is an Operational Control Signal

> "Ethics, governance, and authority are operational control signals that shape every action in real time. They are not oversight layers applied after the fact."

The most common failure mode in autonomous security systems is treating governance as an external audit function — a checkpoint that reviews what the system did. ASAF treats governance as a continuous constraint that shapes what the system can do. The GOV dimension does not sit above the operational loop. It sits inside it, as a real-time limiting function on every action the ACT and AGT dimensions can execute.

This principle has architectural consequences. Governance cannot be an API call to a compliance database. It must be machine-interpretable policy embedded in the authority model, evaluated on every action before it is executed.

---

### P3 — Autonomy Must Be Bounded, Proportional, Explainable, and Revocable

> "Autonomy must be scoped, proportional, explainable, auditable, and revocable. Unbounded autonomy is an architectural failure, not a capability goal."

No mature security architecture pursues maximum autonomy. It pursues appropriate autonomy — the level of autonomous action that is both operationally effective and organizationally defensible. The boundary between appropriate and inappropriate autonomy shifts with organizational maturity, regulatory context, and incident history. The framework that makes that boundary explicit, technical, and adjustable is more valuable than the framework that maximizes agent capability.

Bounded autonomy is not a limitation on ASAF. It is a design goal.

---

### P4 — Operations Are Continuous and Bidirectional

> "Planning, detection, response, and learning operate continuously and bidirectionally. Every action feeds the knowledge model; every new signal may alter the operational plan."

Sequential operations — detect, then investigate, then respond, then close — are efficient for known scenarios. They are brittle for unknown ones. Continuous bidirectional operations maintain parallel detection, investigation, and response threads simultaneously. A new signal does not wait for the previous response to close. It enters the system immediately, is reasoned about, and may generate new action threads before existing ones resolve.

This principle defines the OPS dimension's ambition: not faster escalation chains, but the structural elimination of the need for escalation chains.

---

### P5 — Humans Govern Intent, Not Alert Queues

> "Humans govern intent, scope, and legitimacy — not alert queues. Human value is derived from judgment, authority, and ethical accountability, not task throughput."

This principle defines what "human in the loop" means in a mature agentic security operation. Humans are not in the loop to process more alerts. They are in the loop to define what the system is trying to accomplish, to set the ethical and legal boundaries within which it operates, and to hold accountability for its outcomes.

The shift from throughput work to governance work is not a reduction in human importance. It is an increase in the quality of human contribution. But it requires a different skill set, a different org chart, and a different relationship to the technology.

---

### P6 — The Security Knowledge Graph is the Operational Spine

> "The Security Knowledge Graph is the operational spine — connecting policy, evidence, adversary intelligence, confidence, authority, and audit artifacts as first-class entities."

The SKG is not a SIEM replacement. It is not a threat intelligence platform. It is the shared data model through which all dimensions in the framework communicate. When an agent reasons about a threat, it reasons over the SKG. When governance evaluates an action, it queries the SKG. When learning updates detection, it updates the SKG. When an audit asks why an action was taken, the answer is in the SKG.

Without the SKG, ASAF's dimensions are well-designed components. With it, they are a coordinated system.

---

### P7 — Operations Are Non-Linear

> "Agentic operations do not follow linear kill-chain or escalation models. They operate as competing hypotheses, parallel investigations, and continuous exposure management."

The kill chain model describes how adversaries operate. It has been incorrectly used as a model for how defenders should operate. Defenders who wait for the kill chain to progress before acting give adversaries time. Defenders who run competing hypotheses in parallel, investigate multiple threads simultaneously, and manage exposure continuously do not.

Non-linear operations require a different reasoning architecture (competing hypothesis evaluation, not sequential triage), a different operational model (concurrent threads, not queue processing), and a different knowledge substrate (graph-structured relationships, not flat case records).

---

### P8 — Every Decision Must Be Traceable

> "Every decision, action, and outcome must be traceable through the system to its authorizing scope, evidence chain, confidence level, and governance approval."

Traceability is not an audit requirement imposed on the system. It is an operational requirement for operating autonomous systems responsibly. When an autonomous agent takes a consequential action — isolating a system, blocking an account, triggering a remediation — there must be a complete record of what evidence justified the action, what authority permitted it, what confidence threshold triggered it, and what governance rule allowed it to execute without human approval.

Traceability is how organizations maintain accountability for autonomous decisions. It is also how they improve the system: patterns in the traceability record reveal where confidence thresholds are miscalibrated, where governance boundaries are too narrow or too wide, and where detection quality is degrading.

---

## How the Principles Connect to the Dimensions

Each of the eleven ASAF dimensions expresses one or more of these eight principles in operational terms.

| Dimension | Primary Principle Expression |
|-----------|------------------------------|
| SEN — Sensing Fabric | P1: Provides the continuous sensing input to the cybernetic loop |
| RSN — Reasoning & Planning | P1, P7: Runs competing hypotheses; plans continuous, non-linear operations |
| ACT — Autonomous Action & Response | P3, P8: Bounded execution with full traceability of every action |
| GOV — Ethics, Governance & Authority | P2, P3: Governance as real-time operational signal; authority as technical constraint |
| LRN — Learning & Continuous DFIR | P1, P4: Closes the cybernetic loop; continuous bidirectional learning |
| OPS — Operational Interaction Model | P4, P7: Continuous bidirectional, non-linear operations architecture |
| HUM — Human Roles & Governance Interface | P5: Human governance of intent, not throughput |
| AGT — Agent Architecture & Coordination | P3, P8: Coordinated agents with bounded authority and traceable actions |
| SKG — Security Knowledge Graph | P6: The operational spine connecting all dimensions |
| MET — Metrics, Audit & Assurance | P8: Operationalizes traceability as continuous measurement |
| TRN — Transformation Readiness | P5: Manages the organizational transition to human governance roles |

---

## A Note on Implementation Sequence

The principles are interdependent, but the dimensions have a practical implementation priority order. Most organizations must sequence their ASAF adoption across three waves:

**Wave 1 — Foundation:** SEN (signal quality), SKG (knowledge substrate), and GOV (authority model). These three dimensions must reach at least Stage 1 before meaningful progress is possible elsewhere. Poor signal quality undermines all reasoning. An absent knowledge graph means there is no shared substrate. An absent authority model means agents cannot be given meaningful scope.

**Wave 2 — Operational Core:** RSN (reasoning), AGT (agent coordination), ACT (autonomous action), and OPS (operational model). With the foundation in place, these four dimensions define the operational capability of the system.

**Wave 3 — Sustainment and Governance:** LRN (learning loops), HUM (human governance roles), MET (measurement), and TRN (transformation management). These dimensions sustain and improve the system over time and ensure the human organization can govern what it has built.

This sequencing is not mandatory — organizations will find variation based on existing capabilities. But programs that attempt to build Wave 3 capabilities before Wave 1 foundations are in place consistently fail to achieve durable autonomous operations.
