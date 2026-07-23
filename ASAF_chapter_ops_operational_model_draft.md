# Chapter OPS: Operational Interaction Model

**Working Draft — Agentic SOC Architecture Framework (ASAF) | The Operations Dimension**

---

## The Chapter in One Claim

The escalation chain is not a governance structure. It is a throughput management workaround — a mechanism for routing decisions through the organization because the organization has no other way to move decisions without moving people. When agentic systems can reason, act, and coordinate without human hand-offs, the escalation chain does not become faster. It becomes unnecessary.

The **OPS: Operational Interaction Model** dimension describes the structural change in how security operations are organized when escalation is no longer the primary coordination mechanism. The shift is from linear workflows — sequential, human-gated, queue-driven — to a dynamic, non-linear operational graph where exposure management, detection, response, and DFIR operate as concurrent, interconnected functions.

This dimension does not describe a new tool. It describes a new way of thinking about operational architecture — and why the architecture matters as much as the capability.

---

## The Problem with Linear Operations

Linear security operations have a defining characteristic: each stage in a workflow requires the previous stage to complete. An alert must be triaged before it is investigated. Investigation must conclude before response is authorized. Response must close before lessons are captured. Each transition between stages requires a human hand-off or a system interface.

The costs of linear operations are visible in every SOC metric that matters.

**Mean time to detect** is padded by queue depth. Alerts that could be investigated immediately wait behind earlier arrivals that take longer to triage.

**Mean time to respond** is padded by escalation latency. An alert that reaches a senior analyst after three hours in a queue and two tier escalations has lost hours that a motivated adversary used productively.

**Coverage breadth** is constrained by analyst availability. Every alert the system could generate but does not — because it would generate too many for analysts to process — is a gap in detection coverage. The alert volume an organization can process is not determined by what the detection layer is capable of producing. It is determined by how many analysts are available to process it.

And then there is the structural vulnerability that linear operations share with every linear system: a bottleneck at any stage propagates backward through the entire chain. During a high-volume event — a ransomware campaign, a phishing wave, a coordinated attack — linear operations collapse under exactly the conditions when they most need to perform.

---

## The Non-Linear Alternative

A non-linear operational model does not use escalation chains as its primary coordination mechanism. It uses confidence scores, authority boundaries, and real-time exposure data.

When a detection event enters a non-linear operational system, it does not join a queue. It is evaluated against the current exposure model, classified by confidence, and routed — through an authority-aware dispatch model — to the appropriate response path. High-confidence, low-novelty events execute through pre-authorized agent chains without human involvement. Low-confidence events, or events involving novel behavior, generate investigation threads that run in parallel with existing operational activity. The system does not stop processing other events while it investigates one.

This changes the operational resource model fundamentally. In a linear system, analyst capacity determines operational throughput — there is a hard ceiling at human processing speed. In a non-linear agentic system, agent coordination capacity determines operational throughput — the ceiling is set by the authority model and governance architecture, not by the number of humans available.

The remaining human role is not oversight of individual decisions. It is governance of the system's authority model: defining what agents can do without approval, what triggers an exception, and what constitutes a genuine novelty requiring human judgment.

---

## What the OPS Dimension Measures

OPS is evaluated across four sub-dimensions that track the degree of non-linearity, exposure-integration, DFIR continuity, and escalation elimination in the operational model.

### OPS-01 — Non-linear Workflow Architecture

The degree to which operational workflows are structured as dynamic, context-driven graphs rather than fixed linear sequences or escalation chains.

At Stage 0: All operations follow linear playbook sequences. The escalation chain is the primary coordination mechanism. There is no dynamic workflow branching based on evidence or confidence.

At Stage 2: Workflows are modeled as directed graphs. Branching is driven by evidence and confidence levels. Multiple parallel paths can be active simultaneously for a single detection event.

At Stage 3: Operations are modeled as a dynamic graph. Workflow paths are selected by agents based on real-time context. No fixed escalation chain is required for in-scope events.

At Stage 5: Operations are continuous, non-linear, and self-organizing. The system maintains optimal operational posture across all active threads simultaneously.

**The diagnostic question:** Are your security operation workflows fundamentally designed as linear sequences and escalation chains, or as dynamic, context-driven operational graphs?

---

### OPS-02 — Exposure-driven Operational Prioritization

The use of real-time exposure data to prioritize operational attention and resource allocation across prevention, detection, and response.

A critical alert on a non-critical asset is not operationally equivalent to the same alert on a business-critical system with active exploitable vulnerabilities. Linear priority models — sorting by severity score — cannot make this distinction because they do not carry asset criticality, current exposure status, and active threat context in the same data model.

At Stage 0: Priority is driven by alert severity scores. There is no integration of exposure context. Critical alerts on non-critical assets receive the same treatment as critical alerts on the most sensitive systems.

At Stage 2: Exposure surface is mapped and integrated into the operational priority model. Agents weight responses by exploitability and business impact of affected assets.

At Stage 4: Real-time exposure changes automatically reprioritize active operational threads. Emerging exposures trigger immediate detection posture adjustments.

At Stage 5: Operational priority is a continuous function of live exposure, active adversary activity, and organizational risk posture — updated in real time without human intervention.

**The diagnostic question:** Does your operational prioritization dynamically reflect current exposure levels, or is it primarily driven by alert severity and analyst availability?

---

### OPS-03 — Continuous DFIR as Operational Posture

The transformation of Digital Forensics and Incident Response from a reactive, project-based activity to a continuous operational discipline that permanently informs the rest of the security system.

Continuous DFIR is not simply "DFIR running all the time." It is DFIR integrated into the operational fabric as a data source and feedback mechanism — not a separate team that is engaged post-incident and disengaged after the report.

At Stage 0: DFIR is entirely reactive. It is activated only after confirmed incidents. Forensic capability is limited. Significant evidence is routinely lost due to log retention gaps.

At Stage 2: DFIR tooling is continuously active. Agents perform ongoing forensic collection in high-risk environments. DFIR findings are fed back into detection.

At Stage 3: Continuous DFIR is an operational mode. Agents maintain forensic state across high-risk assets continuously. DFIR and detection share a unified investigation graph.

At Stage 5: DFIR is indistinguishable from normal operations. The system maintains complete forensic state across the environment continuously. Incident investigation is always pre-populated — no evidence has been lost.

**The diagnostic question:** Is DFIR a reactive project triggered by incidents, or a continuous operational function that operates alongside detection and prevention at all times?

---

### OPS-04 — Decision Propagation Without Escalation

The capability to propagate security decisions across the operational system without requiring human escalation — through confidence-rated automated decisions and bounded authority models.

Escalation is a symptom of a system that lacks the authority model and confidence architecture to make decisions autonomously. When every decision above a certain complexity threshold must flow to a human, the human becomes the bottleneck. The organizational response — hire more senior analysts — adds cost without changing the structural problem.

At Stage 0: Escalation is the only coordination mechanism. All decisions above analyst authority require human hand-off. Significant latency occurs at every tier boundary.

At Stage 2: An agent authority model allows direct decision execution without escalation. Only scope-exceeding decisions escalate to humans. Escalation is the exception, not the rule.

At Stage 3: Decisions propagate through the operational graph via confidence and authority signals. Humans receive decisions for approval, not for analysis.

At Stage 5: Escalation is structurally eliminated. The authority model handles all decision routing. Humans are engaged as principals — providing intent, setting scope, and handling ethical boundary conditions — not as escalation endpoints.

**The diagnostic question:** Can your system resolve the majority of security decisions autonomously within defined authority scope — without requiring human escalation as the coordination mechanism?

---

## The Relationship Between OPS and the Tier Model

The tier model — L1, L2, L3 analysts with defined escalation paths between them — is the operational expression of Stage 0 OPS thinking. It is not a governance structure. It is an operational routing mechanism that made sense when humans were the only actors capable of making security decisions.

The progression through OPS maturity stages is, in part, a progression through the structural elimination of the tier model:

- At OPS Stage 1, automation handles some L1 volume and the tier model persists.
- At OPS Stage 2, agents absorb L1 and L2 workloads; the tier model weakens but survives.
- At OPS Stage 3, the tier model is eliminated. Roles shift from tier-defined to authority-defined.
- At OPS Stage 4–5, operational decisions are routed by authority model, not org chart. The concept of "tier" no longer applies.

This is not an aspirational claim about the distant future of security operations. It is a structural consequence of deploying agentic systems with well-defined authority models. Organizations that deploy agents without redesigning their operational model will find that the agents accelerate the existing escalation chain rather than replacing it — and will capture only a fraction of the available value.

---

## OPS Connects to Every Other Dimension

The Operational Interaction Model is the dimension most often underestimated in ASAF implementations. Organizations focus on agent capability (AGT), detection quality (SEN), or reasoning sophistication (RSN), and treat the operational model as an implementation detail.

It is not. The OPS dimension is the dimension through which all other capabilities are expressed operationally.

**OPS and SEN:** The operational model determines how detection signals are prioritized and routed. A non-linear OPS architecture allows detection signals to be evaluated in parallel across multiple investigation threads. A linear architecture forces every signal through a queue regardless of how the signal was generated.

**OPS and RSN:** Reasoning quality is constrained by the operational model's ability to route reasoning outputs to action. If RSN produces a high-confidence, multi-step investigation plan but the operational model routes its outputs through an escalation queue, reasoning speed is irrelevant.

**OPS and GOV:** The authority model that governs agent scope is the mechanism by which OPS-04 (decision propagation without escalation) is operationalized. OPS maturity requires GOV maturity — specifically, GOV's ability to define and technically enforce agent authority boundaries.

**OPS and LRN:** Continuous DFIR (OPS-03) and learning feedback (LRN) are operationally complementary. OPS-03 ensures forensic state is continuously available. LRN ensures that forensic findings are systematically extracted and fed into detection and knowledge improvements. Neither is fully effective without the other.

**OPS and SKG:** Exposure-driven prioritization (OPS-02) requires an active SKG exposure model. The SKG must carry asset criticality, current vulnerability data, and active threat context in a form that the operational routing model can query in real time. OPS maturity is therefore bounded by SKG maturity.

---

## Signals, Connections, and Dependencies

**SKG → OPS (Context signal):** The SKG exposure model, adversary data, and asset criticality graph are the primary inputs to exposure-driven operational prioritization. OPS is a consumer of SKG content.

**RSN → OPS (Hypothesis signal):** Reasoning outputs — detection hypotheses, investigation plans, exposure assessments — inform how OPS routes operational activity. The non-linear workflow architecture executes the plans RSN generates.

**OPS → ACT (Routing signal):** OPS routes decisions and action authorizations to the ACT dimension through the authority model. OPS determines what gets executed and in what sequence.

**LRN → OPS (Learning feedback):** Continuous DFIR findings (LRN) improve the operational model's forensic state and feedback into OPS-03's posture. Learning outcomes may also trigger operational model adjustments.

**HUM → OPS (Intent signal):** Humans define operational scope and exception handling criteria through the HUM dimension. These intent signals define the boundaries within which OPS routes autonomously.

---

## Assessment: How Non-linear Is Your Operational Model?

| Maturity Signal | Stage 0–1 | Stage 2–3 | Stage 4–5 |
|----------------|-----------|-----------|-----------|
| Workflow structure | Linear playbooks; escalation chain dominant | Directed graph; parallel paths active | Continuous dynamic graph; self-organizing |
| Priority model | Alert severity only | Asset criticality + exposure context | Real-time exposure + adversary activity + risk posture |
| DFIR posture | Reactive; activated post-incident | Continuous in high-risk environments | Fully continuous; evidence always pre-populated |
| Decision coordination | Escalation as primary mechanism | Authority model; escalation as exception | Escalation structurally eliminated |

---

## Bridge: From Operational Model to Integration

The eleven dimensions of ASAF do not operate independently. Each dimension produces signals consumed by others. OPS makes those signal flows operationally coherent — it is the architecture that determines how signals from SEN become inputs to RSN, how RSN outputs become directives for ACT, how ACT outcomes return to SKG and LRN.

The final chapter in this series — **Chapter 11: The Integration Model** — takes the perspective of the full system and describes how all eleven dimensions connect, what the complete signal topology looks like, and what organizations actually need to build to make the framework operational at the scale of a live security program.
