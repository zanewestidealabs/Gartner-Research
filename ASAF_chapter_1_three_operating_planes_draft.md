# ASAF Chapter 1 Draft — The Three Operating Planes

**Working book title:** _The End of the Tiered SOC_  
**Chapter:** 1  
**Source base:** Note 1 of `static/docs_asaf_market_notes.json`

---

## Chapter 1 — The Three Operating Planes

The tiered SOC was a labor model before it was a theory. It described how work moved through human specialization: initial triage, deeper investigation, and escalation into more expert handling. For a long period, that model was useful because it aligned with the real constraints of the operation. Humans had to inspect signals, interpret evidence, form judgments, and decide what to do next. The architecture of the SOC was therefore organized around how human effort was allocated and escalated.

That is precisely why the model now fails.

The problem is not that L1, L2, and L3 were always wrong. The problem is that they are no longer the right abstraction for the system that advanced enterprises are building. A tier model tells you who handles work. It does not tell you how a security operation behaves as a control system. It does not explain how signals are produced, how hypotheses are formed, how actions are bounded, or how governance shapes runtime behavior. It describes a staffing structure, not an operational architecture.

The replacement model is better expressed through three operating planes:

- **Sensing**
- **Reasoning**
- **Control**

These are not new team names. They are not merely cleaner labels for the same labor pyramid. They describe distinct roles in a signal-processing system that increasingly mediates security operations through machine sensing, machine inference, bounded agent execution, and governed feedback loops.

That is why the three-plane model matters. It shifts the reader’s attention away from analyst workflow and toward system behavior.

---

## Why the tier model became the wrong abstraction

The tier model made sense when the core operating problem was distributing human investigative labor efficiently. Its assumptions were implicit but powerful:

- alerts arrive as the primary operating input
- humans interpret most of them
- escalations are the main mechanism for increasing judgment quality
- playbooks and workflows support people, but do not fundamentally replace them
- operational quality can be measured largely through human throughput and response timing

Once those assumptions start to fail, the model becomes harder to defend.

The first failure is at the input layer. In a tiered SOC, the system often begins with alerts. In an agentic operating model, the system must begin with continuous, adversary-informed signal production. If alerts remain the dominant unit of input, the system is already downstream of the real architectural problem.

The second failure is at the reasoning layer. A tiered model assumes that deeper expertise is accessed through escalation. But escalation is a workflow pattern, not an inference model. A system that can form and test hypotheses across signals does not improve by sending the same unit of work higher in the human chain; it improves by reasoning over better evidence in a more coherent substrate.

The third failure is at the action layer. The tier model assumes that meaningful action is either manual or manually authorized by default. But once agent execution becomes bounded, governed, and auditable, the key design question is not which tier approves the action. It is what authority model governs the action and whether the system can prove why it was taken.

In short, the tier model overfits to a human-processing architecture. The three-plane model better fits a governed control system.

---

## The three planes as an architectural model

The three-plane model replaces the labor hierarchy with a systems hierarchy.

### Sensing

The Sensing plane is the input layer of the operation. Its job is not merely to generate alerts. Its job is to produce continuous, adversary-validated, confidence-bearing signals that are useful to reasoning. Sensing replaces the old world in which L1 teams existed largely to absorb noisy alert streams and convert them into something a deeper investigator could use.

### Reasoning

The Reasoning plane is the inferential layer. Its job is to form hypotheses, weigh evidence, update confidence, direct targeted investigation, and produce instructions for action. It replaces the idea that the core analytical problem is “which analyst should take the next alert?” The real problem becomes: “What does the system believe is happening, how strongly, and why?”

### Control

The Control plane is the action and constraint layer. It includes execution, authority, governance, and the mechanisms that determine what can happen in the system under what conditions. It replaces the old world in which L3 expertise, manual approvals, and playbook operators formed the effective action layer of the SOC.

Seen together, the three planes define a signal architecture:

- sensing produces meaningful inputs
- reasoning transforms inputs into judgments
- control constrains and executes outcomes

That is a materially different architecture from alert → analyst → escalation.

---

## Why planes are a systems concept, not a team chart

One of the easiest mistakes a reader can make is to reinterpret the three planes as a rebranded org chart. That would miss the point.

A team chart asks questions like:

- Which people sit where?
- Who owns which workflow?
- Who escalates to whom?

A systems model asks different questions:

- Where is signal created?
- Where is inference performed?
- Where are actions authorized, constrained, and executed?
- How does information feed back into the system over time?

Those are not the same questions. And they produce different product requirements.

A platform may support Sensing without owning Reasoning. A vendor may claim to support Control but only execute pre-authored playbooks without meaningful authority modeling. Another product may appear narrower in features but be structurally more important because it materially deepens the Reasoning plane or writes unique evidence back into the shared operational graph.

This is why the three-plane model improves strategic clarity. It lets architects and buyers evaluate what a product actually contributes to the system rather than what job description it most resembles.

---

## What each plane replaces in practice

The easiest way to see the difference is to compare the old model with the new one in operational terms.

### Tiered SOC pattern

1. a rule fires and produces an alert
2. an analyst triages the alert
3. more complex alerts are escalated
4. another analyst investigates
5. a senior responder or engineer decides whether to act
6. playbooks or manual workflows execute the response

This sequence treats escalation as the main mechanism for converting weak input into better output.

### Three-plane pattern

1. continuous sensing produces adversary-informed signals
2. the reasoning plane forms and tests hypotheses across evidence
3. the control plane authorizes and executes bounded action
4. outcomes, evidence, and policy-relevant signals flow back into the system

This sequence treats the operation as a loop rather than a queue.

The old pattern is optimized for distributing human labor. The new pattern is optimized for producing governed system behavior.

---

## A buyer test for true plane position

The three-plane model is also valuable because it exposes vague vendor claims.

Many vendors will say they span multiple parts of the modern SOC. That claim is no longer meaningful unless it can be expressed in plane terms.

A practical buyer should ask at least four questions.

### 1. Which plane do you primarily operate in?

If a vendor cannot answer this clearly, it usually means the product narrative is organized around feature lists, not architectural contribution.

### 2. What signal do you send to adjacent planes?

Consuming data from another part of the system is not the same thing as contributing to it. A multi-plane product must be able to describe what it emits, not just what it ingests.

### 3. Is that contribution inbound only or bidirectional?

Inbound-only integration is not architectural depth. In a real operating loop, products increasingly need to write back signals, evidence, policy objects, confidence states, or action outcomes.

### 4. What happens if your product is removed?

If the answer is mostly inconvenience, the product is likely peripheral. If the answer is degradation of reasoning quality, governance integrity, or loop coherence, the product is more structurally important.

These questions shift vendor evaluation from “does it have the feature?” to “does it belong in the architecture?”

---

## Why Reasoning becomes especially strategic

Although all three planes matter, the Reasoning plane has unusual strategic weight.

The market is full of products that claim signal visibility and many that claim automation. Far fewer can articulate how structured, hypothesis-driven reasoning actually works in their system. That gap matters because Reasoning is the bridge between seeing and doing. If it is weak, the system either collapses back into human triage or executes brittle automation without trustworthy inference.

That makes Reasoning one of the hardest dimensions to fake. A vendor may market correlation, enrichment, or workflow routing as reasoning. But reasoning in this architecture means the ability to operate against a shared model, form alternatives, manage uncertainty, and produce action-worthy judgments. That is not the same thing as connecting alerts in a prettier interface.

This is one reason the three-plane model is a better evaluative lens than the tier model. The tier model hides inferential depth behind human escalation. The plane model makes inferential quality visible as an explicit part of architecture.

---

## A concrete operating-model scene

Imagine a vendor briefing in which a platform claims to cover “the full SOC lifecycle.” In the older market vocabulary, that sounds persuasive. The platform detects, enriches, prioritizes, automates, and reports.

Now reframe the same claim using the three planes.

- In **Sensing**, the product consumes telemetry and emits alerts, but it does not produce adversary-validated, confidence-bearing signals.
- In **Reasoning**, it correlates related events, but it does not form structured hypotheses or manage alternative explanations.
- In **Control**, it executes pre-authored playbooks, but it does not model authority scope or generate auditable governance artifacts.

What initially sounded like full-spectrum coverage now looks like a collection of useful but shallow functions sitting mostly at the edges of the architecture.

That is the power of the plane model. It exposes whether a product is actually participating in the new system or simply speaking fluent legacy.

---

## Why this chapter matters

This chapter matters because every later dimension in ASAF becomes easier to understand once the reader abandons the tier metaphor.

Without this shift, the rest of the framework can be misunderstood as an elaborate enhancement stack for the existing SOC. With this shift, the later chapters read correctly: not as point improvements, but as parts of a replacement architecture.

That is especially important for product and market interpretation. Once the system is read in plane terms, it becomes easier to see why some categories are structurally advantaged, why others are merely useful but non-decisive, and why some categories disappear once Stage 2 becomes the buyer baseline.

---

## Three takeaways

- The three-plane model replaces a human labor hierarchy with a systems architecture built around signal, inference, and governed action.
- L1/L2/L3 is no longer the best abstraction for evaluating advanced security operations products or designing the future SOC.
- Vendors that cannot clearly identify their plane position and adjacent-plane contribution are usually describing workflow convenience, not architectural necessity.

## Two implications

- Buyers should evaluate security platforms by their plane contribution and loop participation rather than by feature breadth inside the old tier model.
- Vendors should assume that vague “end-to-end SOC” claims will become less persuasive as buyers shift from staffing logic to architectural logic.

## Bridge to Chapter 2

If Sensing is the first plane, the next question is what kind of output the new architecture actually requires. That is where the argument goes next: from the plane model itself to the new capability floor of the Sensing Fabric.
