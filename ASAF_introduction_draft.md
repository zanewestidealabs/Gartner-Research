# ASAF Introduction Draft

**Working book title:** _The End of the Tiered SOC_  
**Working subtitle:** _How security operations becomes a governed control system_

---

## Introduction

The most important change in security operations is not that AI is entering the SOC. It is that the tiered analyst model that defined the SOC for the last two decades is beginning to cease functioning as the governing architecture of the operation.

That is a different claim from the usual market story. The usual story says that AI improves the SOC: it makes analysts faster, triage smarter, detection more efficient, and workflows more automated. This book makes a more specific and more consequential argument. It argues that enterprise security operations is undergoing **architectural substitution**, not feature evolution. The operating model built around alert queues, analyst tiers, manual escalations, and playbook-mediated response is being replaced by a new control system built around continuous sensing, machine reasoning, bounded agent execution, runtime governance, and a shared operational intelligence spine.

At first glance, that can sound like rhetoric. It is not. The shift is already measurable. Enterprises operating at what this framework calls **Stage 2** are eliminating large portions of L1 and L2 workload from production security operations today. They are not merely enriching analysts with copilots. They are relocating more of the operating burden into systems that sense continuously, reason across evidence, act within governed bounds, and generate auditable decision chains. The practical implication is stark: products designed primarily to improve the old tier model are not simply at risk of margin compression. Many are at risk of becoming architecturally unnecessary.

This is why the distinction between decline and substitution matters. A declining model can often be optimized, stretched, or defended through incremental improvement. A substituted model can survive for a while in installed bases, but it stops governing the future. The question for security leaders, product leaders, architects, and investors is therefore not whether AI will “change the SOC.” The real question is which products, teams, and design assumptions still belong to a tiered operating system—and which belong to the one replacing it.

This book offers a framework for answering that question.

---

## Why this book exists now

Security operations has lived for years inside a deceptively stable abstraction. Alerts arrive. Analysts triage. More complex cases escalate. Humans investigate. Playbooks assist. Managers measure throughput, response time, and detection performance. Entire product categories, buying patterns, role definitions, and service models have been built around that sequence.

But the sequence is now breaking for structural reasons.

First, the unit of work is changing. In a tiered SOC, the atomic unit is often the alert or ticket. In an agentic operating model, the atomic unit becomes the **signal**, the **hypothesis**, the **authority-bounded action**, and the **evidence chain** that connects them. That shift changes what the system must produce and what humans are for.

Second, the control surface is changing. In the old model, control is spread across staffing patterns, runbooks, approval layers, and tribal expertise. In the new model, control increasingly resides in machine-interpretable governance, authority scope, reasoning quality, and the integrity of the shared operational model.

Third, the sources of strategic advantage are changing. In a tiered world, value often accumulates around workflow convenience, analyst throughput, alert consolidation, or specialized human services. In the emerging model, value increasingly accumulates around reasoning depth, graph contribution, governance architecture, and integration into the live cybernetic loop of the operation.

These shifts are no longer speculative. They are visible in leading enterprise programs, in product roadmaps, in buyer evaluation criteria, and in the growing gap between tools that assist an old architecture and platforms that help construct a new one.

This book exists because that gap needs a vocabulary.

---

## What ASAF is

ASAF stands for the **Agentic Security Operations Adoption Framework**. It is a staging and evaluation model for understanding how security operations moves from the traditional SOC to a governed, agent-orchestrated control system.

The framework has four core parts:

- **six maturity stages**, from Traditional operations to fully agentic operations
- **three operating planes** — Sensing, Reasoning, and Control — which replace the old L1/L2/L3 mental model
- **eleven dimensions**, which define the full capability surface of the new architecture
- **eight principles**, which define the non-negotiable operating assumptions of an agentic security system

ASAF is designed to do three things at once.

First, it helps leaders describe the transition with precision. Instead of talking vaguely about “AI-enabled SOC transformation,” it gives a reader a way to name what is changing, where a product sits, which capabilities matter most, and what stage an enterprise has actually reached.

Second, it helps buyers and architects evaluate platforms. It distinguishes between products that enable stage advancement, products that remain useful but non-structural, and products whose value proposition depends on unresolved Stage 0 and Stage 1 problems.

Third, it helps the market see that the future of security operations is not an analyst workflow with smarter tools attached. It is a new control system.

---

## The shape of the replacement

The cleanest way to understand the replacement architecture is to start with the three operating planes.

- **Sensing** replaces L1-style alert triage and initial classification with continuous, adversary-informed signal production.
- **Reasoning** replaces L2-style investigation with hypothesis-driven inference across a shared adversary and evidence model.
- **Control** replaces human-default escalation and playbook execution with bounded agent action governed by live authority constraints, policy, and traceability.

These planes do not operate as isolated product categories. They function as a continuous loop. Signals feed reasoning. Reasoning directs execution. Execution writes outcomes into the shared operational model. Governance constrains and recalibrates all three. Human oversight increasingly governs intent, exception handling, and legitimacy rather than serving as the default processing layer for every alert.

This is why the tier metaphor breaks down. Tiers describe escalation layers in a human labor model. Planes describe signal-processing roles in a system architecture. Once the unit of analysis changes from analyst workload to system behavior, the old tier model stops clarifying what matters.

---

## The stakes for vendors and buyers

One of the most important consequences of this shift is that the market does not reorganize around “best features.” It reorganizes around **architectural position**.

ASAF groups vendors into three categories:

- **Enablers** — products that accelerate stage advancement by contributing meaningfully to reasoning, execution, governance, or the shared intelligence spine
- **Neutral players** — products that remain useful in the environment but do not drive movement into the next operating model
- **Displaced categories** — products whose primary value depends on the tier model still being the organizing structure of the SOC

This matters because many products that look competitive in a feature checklist become non-competitive once evaluated in architectural terms. A broad-feature product with shallow loop participation may be less strategically important than a narrower product that writes evidence into the graph, shapes governance, or materially improves reasoning quality.

For buyers, this means the most important question is not merely, “Does this tool work?” It is, “Does this tool belong in the system we are becoming?”

For vendors, the equivalent question is even tougher: “Are we helping the customer move into the next architecture, or are we monetizing friction inside the old one?”

---

## Who this book is for

This book is written for readers who need a strategic but operationally precise view of the transition.

It is especially for:

- **CISOs and security leaders** deciding where the operating model is headed and which categories are exposed
- **security product leaders and platform builders** deciding whether their products enable stage advancement or merely optimize legacy workflows
- **platform architects and integration leaders** designing how sensing, reasoning, execution, governance, and shared intelligence should fit together
- **market strategists, investors, and GTM leaders** trying to distinguish structural winners from temporary feature leaders

You do not need to agree with every implication of the framework to use the book. But you do need to entertain its central premise: that the future of security operations is governed less by human tiering and more by the design of a machine-mediated control loop.

---

## How to read this book

This book is meant to be read front to back, because its argument accumulates.

The introduction establishes the burning platform and the shape of the framework. **Chapter 1** then replaces the reader’s inherited mental model by showing why Sensing, Reasoning, and Control are better descriptors of the new architecture than L1, L2, and L3. From there, the book moves plane by plane and then into the structural dimensions that make the full system coherent.

The reading arc is intentional:

1. first, understand why the old model is breaking
2. then understand the architecture that replaces it
3. then understand the dimensions that make the architecture operational
4. finally, understand how the whole system behaves as one cybernetic loop

Readers looking for a specific entry point can still use the later appendices and role-based artifacts. But the main text is designed as a cumulative argument, not a detached reference set.

---

## What this book argues

This book makes five claims.

1. The tiered SOC is no longer the correct organizing abstraction for advanced security operations.
2. The replacement model is architectural, not cosmetic.
3. The transition can be staged, assessed, and compared.
4. Governance, reasoning, and graph contribution are becoming structurally decisive.
5. Vendor categories will increasingly be defined by integration depth in the loop, not by feature breadth in isolation.

If those claims are right, then the future of security operations will not be determined by who best supports the old human workflow. It will be determined by who best helps enterprises build a governed system that can sense, reason, act, and prove what it did.

That is the argument this book will now build.

---

## Three takeaways

- The central shift is not “AI in the SOC,” but the end of the tiered SOC as the governing architecture.
- ASAF provides a way to stage, assess, and compare that transition with more precision than generic transformation language allows.
- The rest of the book explains the replacement model as a continuous argument, beginning with the three operating planes that displace the tier metaphor.

## Two implications

- Buyers should evaluate tools not just by utility, but by whether they belong in the architecture that is replacing the old model.
- Vendors should assume that products monetizing unresolved tier-model friction are structurally exposed as enterprises advance beyond Stage 1.

## Bridge to Chapter 1

If the tiered SOC is ending, the next question is not which tool wins inside the old structure. It is what architectural model replaces L1, L2, and L3—and why that model better describes the future of security operations.
