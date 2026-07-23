# Chapter LRN: Learning & Continuous DFIR

**Working Draft — Agentic SOC Architecture Framework (ASAF) | The Learning Dimension**

---

## The Chapter in One Claim

Most security operations programs treat learning as a project activity: run a post-incident review, write up findings, update a runbook, maybe create a new detection rule. The findings live in a document. The document is rarely read. The learning does not happen.

In a mature agentic SOC, learning is an operational function — as continuous and automatic as detection itself. Every incident, near-miss, and threat intelligence update is processed by a dedicated learning architecture that feeds improvements directly back into the detection fabric, reasoning engine, and Security Knowledge Graph. The system does not wait for a quarterly review to improve. It improves in real time, at machine speed, from every operational event that passes through it.

This dimension — **LRN: Learning & Continuous DFIR** — closes the cybernetic loop. Without it, the SOC senses, reasons, and acts, but does not get measurably better. With it, every adversary encounter makes the system more capable of detecting the next one.

---

## Why the Learning Loop Has Always Been Broken

The post-incident review is security operations' most systematically failed process. The reasons are structural, not attitudinal.

Analysts who run incident reviews are also responsible for the alert queue. Review cycles compete with operational throughput, and throughput always wins. Findings that reach written reports require manual translation into operational artifacts — new rules, updated runbooks, revised playbooks. That translation requires analyst time, which is the same resource already overcommitted to throughput. The improvement cycle, measured honestly, runs in weeks to months. By the time a new detection rule reflecting last month's incident is deployed, the adversary has already moved to a new technique.

The deeper problem is architectural. In a SIEM-and-SOAR model, the detection layer and the knowledge layer are separate systems with no automatic connection. A detection analyst learns something operationally significant during an investigation. That knowledge does not automatically enter the detection system. It enters a case management record, which may or may not be read, which may or may not prompt a rule update, which may or may not be deployed.

The Security Knowledge Graph changes this architecture. When SKG entities and relationships are first-class objects that agents can write to as well as read from, operational learning becomes a data flow problem rather than a process management problem.

---

## What the LRN Dimension Measures

LRN is evaluated across four sub-dimensions that track the speed, completeness, and automation of the learning cycle.

### LRN-01 — Incident Learning Integration

The systematic extraction of detection improvements, behavioral indicators, and governance lessons from resolved incidents and their integration back into the operational system.

At Stage 0: Post-incident reviews are episodic. Findings are captured in documents that are rarely operationalized. The detection system at the end of a year looks nearly identical to the detection system at the beginning of it, despite dozens of incidents.

At Stage 3: Incident learning is automated. New indicators, detectors, and authority boundary adjustments are generated from every incident, confidence-rated, and queued for deployment — without a human driving the process.

At Stage 5: DFIR is a permanent operational function, not a post-incident activity. The system learns continuously from active incidents, historical incident records, and near-misses without distinguishing between them. Every day the system is running is a day it is learning.

**The diagnostic question:** How systematically does your organization extract and integrate detection and response improvements from resolved incidents — and how quickly do they appear in production? If the answer involves a quarterly review cycle and manual rule-writing, you are at Stage 0 or 1. If the answer involves agent-driven extraction and automated deployment, you are approaching Stage 3.

---

### LRN-02 — Detection Improvement Loops

The automated feedback loop from detection performance — false positive rate, coverage gaps, missed detections — back into detection logic and sensor configuration.

Detection quality degrades without active maintenance. Adversaries change techniques. Environments change. Business applications that previously behaved in unusual ways become normal. The detection system that was well-tuned twelve months ago is producing noise today unless it has been continuously maintained.

At Stage 0: Detection tuning is manual and infrequent. False positive reduction depends on analyst initiative. There is no systematic tracking of detection performance as a metric.

At Stage 3: Detection improvement is fully automated within governed scope. Low-performing detectors are automatically tuned or retired. Coverage gaps against known adversary TTPs drive new detector generation.

At Stage 5: Detection architecture is self-improving at the rate of new threat intelligence and incident data. The system's detection capability increases measurably without human-driven tuning cycles.

**The diagnostic question:** How automatically does detection performance feedback — false positives, coverage gaps, missed events — drive improvements to detection logic? If tuning requires a dedicated analyst project, you are at Stage 0 or 1.

---

### LRN-03 — Adversary Intelligence Absorption

The speed and depth with which external threat intelligence — new TTPs, actor campaigns, IOCs, vulnerability research — is absorbed and operationalized.

Intelligence that does not translate into detection capability is expensive reporting. The gap between consuming a threat intelligence feed and actually detecting the TTPs that feed describes is often enormous: days to weeks for IOC-level matching, months or never for TTP-level behavioral detection.

At Stage 0: Threat intelligence is consumed as reports. Operationalization is manual and slow. The intel-to-detection cycle is measured in weeks.

At Stage 3: The adversary model in the SKG is automatically updated from structured intelligence sources. New TTPs generate detection hypotheses and coverage gap analyses without human intervention.

At Stage 5: Real-time intelligence fusion. The adversary model is continuously current. The detection posture adapts faster than adversary technique adoption cycles.

**The diagnostic question:** How quickly and completely does new external threat intelligence — new actor TTPs, campaign reports, zero-days — translate into updated detection and response posture? The gap between "we have the intel" and "we can detect it" is one of the clearest LRN maturity signals.

---

### LRN-04 — Knowledge Graph Evolution

The capacity of the Security Knowledge Graph to evolve — incorporating new entities, relationships, and confidence updates from operations, incidents, and intelligence — without requiring manual curation.

A static SKG is not a knowledge graph. It is a snapshot. The value of a knowledge graph in security operations comes from its currency: whether the adversary model, the asset model, the confidence scores, and the policy structures reflect operational reality today, not six months ago.

At Stage 0: Knowledge is captured in runbooks and wikis. Updates require manual curation. Knowledge is perpetually stale.

At Stage 3: The SKG evolves continuously from agent outputs, incident data, and intelligence feeds. Automated entity resolution and relationship inference reduce manual curation to high-stakes changes only.

At Stage 5: The SKG is a living operational system that continuously improves its own models. Knowledge quality is measurably higher over time without increasing human curation effort.

**The diagnostic question:** How autonomously does your security knowledge model evolve based on operational experience — without requiring manual data entry or curation?

---

## Why Continuous DFIR Is the Right Framing

Traditional DFIR is a reactive capability: something bad happens, the DFIR team is engaged, they investigate, they produce a report, they hand off lessons learned, and they stand down. This model has two fundamental problems.

First, it loses evidence. Most DFIR engagements begin days or weeks after the initial compromise. Log retention gaps, event overwrites, and memory loss mean the forensic record is incomplete at the start of every engagement.

Second, it produces learning that arrives too late to prevent the attack it was triggered by. The value of DFIR learning is prospective: it should inform future detection. But the lag between incident, investigation, report, and operationalization typically spans months. By the time new detectors reflecting the DFIR findings are deployed, adversaries have moved.

Continuous DFIR eliminates both problems. When forensic collection is ongoing — not triggered — evidence exists before it is needed. When DFIR findings are automatically extracted and fed into the learning pipeline, the improvement cycle runs at machine speed.

The LRN dimension operationalizes this: not DFIR as a project, but DFIR as an always-on operational posture.

---

## Signals, Connections, and Dependencies

LRN does not operate in isolation. It sits at the intersection of several critical ASAF information flows:

**SEN → LRN (Telemetry signal):** Every detection event — whether it generates an alert or not — is a potential learning signal. Missed detections, near-misses, and false positives all carry information about the detection architecture's coverage and calibration. The quality of SEN output constrains the quality of LRN input.

**ACT → LRN (Outcome signal):** Every autonomous action generates an outcome that should feed the learning system: whether containment was successful, whether the threat was correctly classified, whether the response was proportionate. Action outcomes are the most operationally grounded learning signals available.

**LRN → SEN (Learning feedback):** Detection improvements generated by LRN close the loop back to the sensing fabric. New detectors, updated thresholds, revised behavioral baselines — these are LRN outputs consumed by SEN. The speed of this loop directly determines how quickly the system improves its detection capability.

**LRN → SKG (Knowledge update):** LRN outputs that update the adversary model, asset model, and confidence structures in the SKG are consumed by every other dimension that queries the graph. LRN's improvements propagate across the entire system through the SKG.

**SKG → LRN (Context for absorption):** Adversary intelligence absorption is more effective when the existing SKG adversary model provides context for new intelligence. LRN uses SKG content to place new intelligence in the context of what is already known.

---

## Implications for Architecture

Organizations building toward LRN capability need to make three architectural decisions:

**1. Agent-extractable incident records.** If incident investigation data lives in case management systems that only humans can read and interpret, automated learning is impossible. The investigation record must be structured in a way that agents can extract behavioral indicators, timeline data, and confidence assessments automatically.

**2. Write-back access to the detection fabric.** Learning systems that can analyze but not modify detection logic require a human relay between the learning output and the operational system. This relay is the bottleneck. The detection improvement loop closes automatically only when the system has governed write-back access to its own detection layer.

**3. Entity lifecycle management in the SKG.** A knowledge graph that only adds entities but never retires or revises them will degrade in quality over time. LRN-04 maturity requires entity lifecycle management: automated confidence decay, relationship revision when evidence changes, and entity retirement when assets or adversary models become stale.

---

## Assessment: How Advanced Is Your Learning Architecture?

| Maturity Signal | Stage 0–1 | Stage 2–3 | Stage 4–5 |
|-----------------|-----------|-----------|-----------|
| Incident learning integration | Episodic reviews; findings in documents | Agent-assisted extraction; days to production | Continuous; automatic deployment within governed scope |
| Detection tuning cycle | Manual; weeks to months | Automated proposals; human approval | Autonomous; self-optimizing within governed scope |
| Intel-to-detection cycle | Weeks; IOC-level only | Hours; TTP-level behavioral detection | Real-time; adversary model continuously current |
| SKG evolution | Manual curation; stale | Partially automated; curated for high-stakes | Self-evolving; quality improving without manual effort |

---

## Bridge: From Learning to the Operational Model

LRN ensures the system improves from what it has experienced. But improvement is only valuable if the operational model that acts on what the system knows is itself well-designed.

The next dimension in the framework — **OPS: Operational Interaction Model** — addresses exactly this: not how the system learns, but how it structures the operational execution of what it knows. The shift from linear escalation chains to a non-linear, exposure-driven operational graph is the structural change that allows the learning capabilities described in this chapter to actually translate into faster, better-coordinated security operations.
