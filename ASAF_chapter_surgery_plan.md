# ASAF Chapter Surgery Plan

**Updated:** June 8, 2026  
**Source base:** `static/docs_asaf_market_notes.json` + `ASAF_AEOF_ebook_architecture.md`

## Purpose

This document turns the existing ASAF market insight series into a **chapter-by-chapter editorial conversion plan**.

It is not a summary of the framework. It is a **working rewrite map** for converting the note series into a book manuscript.

The goal is to answer, for every chapter:

- what to preserve
- what to cut or move
- what to expand
- what new connective tissue to write
- what visual should anchor the chapter
- what practical example should make the chapter feel lived-in

---

## Conversion rules for the full manuscript

Before editing individual chapters, keep these rules fixed across the whole book.

### Rule 1 — The book is no longer modular by default

The original note series was designed to support selective entry. The book should support **sequential accumulation**.

That means body chapters should stop repeating:

- note-series metadata
- dependency and standalone tables
- full framework reference tables in every chapter
- role-entry framing that belongs in the introduction

### Rule 2 — Every chapter must earn the next one

At the end of each chapter, the reader should understand:

- what changed
- why that matters
- why the next chapter is logically necessary

### Rule 3 — Tables remain supporting instruments

The notes lean heavily on tables. Keep the strongest ones, but make sure the prose does the argument work.

Use tables to:

- sharpen comparison
- compress stage differences
- summarize implications

Do **not** let tables replace the chapter narrative.

### Rule 4 — Add one operating-model example per chapter

Each chapter needs one concrete scene, such as:

- a vendor briefing diagnostic
- a buyer decision moment
- a Stage 0 versus Stage 3 operating snapshot
- a governance failure scenario
- a before-and-after workflow picture

### Rule 5 — End every chapter with a short payoff sequence

Each chapter should finish with:

1. **Three takeaways**
2. **Two implications**
3. **One bridge sentence to the next chapter**

---

## Recommended book flow

### Front matter

- Title page
- Subtitle
- Optional foreword or framing note
- How to read this book
- ASAF at a glance

### Introduction

- Adapted from Note 0

### Part I — Why the model is changing

- Chapter 1: The Three Operating Planes
- Chapter 2: Sensing Fabric
- Chapter 3: Reasoning Architecture
- Chapter 4: Agent Execution

### Part II — The new control system

- Chapter 5: Security Knowledge Graph
- Chapter 6: Governance & Ethics

### Part III — What changes operationally

- Chapter 7: Continuous Threat Exposure
- Chapter 8: Human Interface & Oversight
- Chapter 9: Measurement & Metrics
- Chapter 10: Transformation Management

### Part IV — The full system

- Chapter 11: The Integration Model

### Final conclusion

- new, not currently present in the source series

---

## Introduction surgery plan

### Source asset

Note 0 — Framework Overview

### What already works well in the introduction

- creates urgency
- names the architectural shift
- introduces the framework map
- names the three vendor categories
- provides a reading guide by role
- establishes that the change is measurable and staged

### What to preserve from Note 0

- the burning-platform argument
- the six stages / three planes / eleven dimensions as the map
- the three vendor categories
- the phrase-level sharpness around architectural substitution

### What to cut or move out of the introduction

Move the following into appendices or sidebars:

- dense framework-reference table detail
- note-series-specific navigation language
- explicit “published first; referenced last” series logic

### What to add to the introduction

- a stronger opening page that says **why this book exists now**
- a clearer reader promise
- a short map of who this book is for
- a concise chapter roadmap
- a stronger “how to use this book” section for buyers, vendors, and architects

### Recommended opening sequence

1. The end of the tiered SOC
2. Why this is architectural substitution, not feature evolution
3. What ASAF is
4. Who the book is for
5. How the rest of the book unfolds

### Recommended visual for the introduction

- one-page system map: 6 stages + 3 planes + 11 dimensions

### Recommended example for the introduction

- a short contrast between a traditional tiered SOC operating day and a Stage 2 program where L1/L2 workloads are already absorbed by agents

### Definition of done for the introduction

The introduction should make a first-time reader say:

> “I understand the problem, the structure of the framework, and why I should keep reading.”

---

## Chapter 1 surgery plan

### Chapter target for Chapter 1

**Chapter 1 — The Three Operating Planes**  
Source: Note 1

### What to preserve in Chapter 1

- Sensing / Reasoning / Control as the replacement architecture
- the claim that this is a signal-processing model, not an org chart
- the plane table mapping to what gets replaced

### What to reduce in Chapter 1

- note-series explanation about why this note comes before Notes 2–4
- full dependency scaffolding

### What to expand in Chapter 1

- show what a legacy L1/L2/L3 model looks like in daily practice
- show how the three-plane model changes system design, not just vocabulary
- add why a vendor’s inability to name its plane position is strategically revealing

### What to add in Chapter 1

- “Why the tier model became the wrong abstraction”
- “Why planes are a systems concept, not a team chart”
- “How buyers can test a vendor’s true plane position”
- a mock vendor briefing where a platform claims to span all planes but can only consume signals without producing governed outputs

### Recommended visual for Chapter 1

- L1/L2/L3 versus Sensing/Reasoning/Control replacement diagram

### Recommended bridge out of Chapter 1

Lead directly into Chapter 2: if Sensing is the first plane, the next question is what kind of signal the new architecture requires.

---

## Chapter 2 surgery plan

### Chapter target for Chapter 2

**Chapter 2 — Sensing Fabric (SEN)**  
Source: Note 2

### What to preserve in Chapter 2

- the claim that signature detection is a Stage 0 artifact
- the stage-by-stage capability progression
- the sub-dimension framing

### What to reduce in Chapter 2

- over-reliance on structured framework-reference tables in the body
- note-level role metadata beyond a concise mention

### What to expand in Chapter 2

- contrast alert output versus adversary-validated signal output in plain language
- explain what confidence-scored signals change for downstream reasoning
- show why detection tools that stop at alert quality improvement are still trapped in a legacy frame

### What to add in Chapter 2

- “What a sensing fabric must emit”
- “Why better alerts are not the same thing as new architecture”
- “How sensing becomes bidirectional”
- a side-by-side example of a Stage 0 alert flood and a Stage 2 sensing layer that emits confidence-scored adversary signals

### Recommended visual for Chapter 2

- Stage 0 alerting versus Stage 2 sensing-output comparison

### Recommended bridge out of Chapter 2

Once signals improve, the next problem is not volume. It is how the system reasons over them.

---

## Chapter 3 surgery plan

### Chapter target for Chapter 3

**Chapter 3 — Reasoning Architecture (RSN)**  
Source: Note 3

### What to preserve in Chapter 3

- the alert-centric versus hypothesis-driven comparison
- the claim that alert-by-alert investigation is architecturally obsolete
- the sub-dimension structure

### What to reduce in Chapter 3

- repetitive framework references that can move to appendix notes

### What to expand in Chapter 3

- explain what hypothesis-driven reasoning feels like operationally
- clarify how competing hypotheses reduce analyst anchoring bias
- tie reasoning more explicitly to the knowledge graph as an operational substrate

### What to add in Chapter 3

- “Why alert-centric investigation fails at scale”
- “What a reasoning engine actually does”
- “Why RSN becomes the hardest dimension to fake”
- a comparison between an analyst triaging single alerts and an RSN system evaluating multiple adversary hypotheses simultaneously

### Recommended visual for Chapter 3

- alert-centric investigation flow versus hypothesis-driven reasoning flow

### Recommended bridge out of Chapter 3

If reasoning forms the judgment, the next question is how the system acts without breaking trust.

---

## Chapter 4 surgery plan

### Chapter target for Chapter 4

**Chapter 4 — Agent Execution (AGT)**  
Source: Note 4

### What to preserve in Chapter 4

- bounded autonomy as the central claim
- declared authority scope, confidence thresholds, and audit chain generation
- the AGT sub-dimensions

### What to reduce in Chapter 4

- standalone note scaffolding

### What to expand in Chapter 4

- make the legal and governance stakes more concrete
- explain why “automation” and “bounded autonomy” are not synonyms
- show how confidence gating and authority scope turn execution into a governed system rather than a playbook library

### What to add in Chapter 4

- “Why automation is not the right category anymore”
- “What makes autonomy bounded”
- “Why governance failures become execution failures”
- a scenario where a product executes a containment action without authority modeling and creates legal or operational blowback

### Recommended visual for Chapter 4

- bounded autonomy execution triangle: authority, confidence, audit chain

### Recommended bridge out of Chapter 4

Once agents act, the system must retain memory, evidence, and policy context somewhere coherent.

---

## Chapter 5 surgery plan

### Chapter target for Chapter 5

**Chapter 5 — Security Knowledge Graph (SKG)**  
Source: Note 5

### What to preserve in Chapter 5

- the SKG as operational spine claim
- the read/write asymmetry
- the list of SKG entities and why they matter

### What to reduce in Chapter 5

- note-specific dependency table language

### What to expand in Chapter 5

- explain in more narrative terms why writing to the graph compounds value over time
- show why the SKG shifts competition from features to integration depth
- connect SKG more explicitly to reasoning, governance, and exposure posture

### What to add in Chapter 5

- “Why a shared graph changes architecture”
- “Read is useful; write is strategic”
- “How switching costs accumulate through evidence and policy contribution”
- a platform comparison showing one product that reads from common services versus one that writes unique evidence and hypothesis history into the shared model

### Recommended visual for Chapter 5

- SKG read/write asymmetry diagram

### Recommended bridge out of Chapter 5

If the graph stores policy, evidence, and authority, governance is no longer an external layer. It is part of runtime.

---

## Chapter 6 surgery plan

### Chapter target for Chapter 6

**Chapter 6 — Governance & Ethics (GOV)**  
Source: Note 6

### What to preserve in Chapter 6

- the claim that governance is a runtime signal
- the high-weight justification
- the asymmetry of governance failure versus detection failure
- the GOV sub-dimensions

### What to reduce in Chapter 6

- repeated framework tables in the body

### What to expand in Chapter 6

- legal, audit, regulatory, and board-level implications
- why governance becomes the trust boundary for autonomy
- the distinction between policy documents and machine-interpretable control signals

### What to add in Chapter 6

- “Why governance carries the highest weight”
- “What runtime governance means in practice”
- “Why trust cannot be layered on after the fact”
- a Stage 3 scenario where an autonomous action is blocked by runtime policy enforcement and that block preserves legitimacy

### Recommended visual for Chapter 6

- governance as control signal flowing through execution, sensing, and oversight

### Recommended bridge out of Chapter 6

Once governance and intelligence are in place, the remaining operational dimensions stop being side capabilities and start becoming live control signals.

---

## Chapter 7 surgery plan

### Chapter target for Chapter 7

**Chapter 7 — Continuous Threat Exposure (EXP)**  
Source: Note 7

### What to preserve in Chapter 7

- the shift from periodic assessment to continuous exposure signal
- the CTEM comparison table

### What to reduce in Chapter 7

- extra reference scaffolding

### What to expand in Chapter 7

- show how EXP should feed sensing, reasoning, and governance
- clarify why exposure posture becomes operationally relevant only when it is live and connected
- make the case against periodic reporting as a control model

### What to add in Chapter 7

- “Why periodic assessment is a legacy artifact”
- “What it means for exposure to become a live signal”
- “How exposure changes authority and prioritization”
- an example where exposure posture causes the governance system to narrow or expand permitted agent action

### Recommended visual for Chapter 7

- periodic assessment cycle versus continuous exposure signal loop

### Recommended bridge out of Chapter 7

If agents handle more of the operation, the human role changes from handling work to shaping and governing it.

---

## Chapter 8 surgery plan

### Chapter target for Chapter 8

**Chapter 8 — Human Interface & Oversight (HUM)**  
Source: Note 8

### What to preserve in Chapter 8

- the claim that the human role is redefined, not eliminated
- the role-across-stages table

### What to reduce in Chapter 8

- any framing that sounds like a standalone HR note rather than part of the operating-system argument

### What to expand in Chapter 8

- the role-redesign logic
- the distinction between analyst-elimination rhetoric and actual human-governance redesign
- what interfaces should surface when humans no longer live in alert queues

### What to add in Chapter 8

- “What humans stop doing”
- “What humans become more responsible for”
- “Why oversight is not the same thing as manual review”
- a Stage 0 analyst console versus a Stage 3 governance console comparison

### Recommended visual for Chapter 8

- human role shift across maturity stages

### Recommended bridge out of Chapter 8

Once the human role changes, the system also needs new proof that it is performing well.

---

## Chapter 9 surgery plan

### Chapter target for Chapter 9

**Chapter 9 — Measurement & Metrics (MET)**  
Source: Note 9

### What to preserve in Chapter 9

- the claim that MTTR and detection rate are Stage 0 metrics
- the comparison between legacy metrics and Stage 2+ replacements

### What to reduce in Chapter 9

- table overload without interpretive prose

### What to expand in Chapter 9

- explain why the old metrics overfit to human throughput
- show what a new KPI stack says about autonomy, reasoning quality, and governance health
- tie metrics more clearly to executive trust and transformation decisions

### What to add in Chapter 9

- “Why throughput metrics fail in an agentic system”
- “What the new metrics actually measure”
- “How metrics become governance evidence”
- a sample dashboard or scorecard contrasting legacy SOC KPIs with agentic-operations KPIs

### Recommended visual for Chapter 9

- legacy metrics versus agentic metrics dashboard layout

### Recommended bridge out of Chapter 9

Once you can measure the new operating model, you can finally manage the transformation into it.

---

## Chapter 10 surgery plan

### Chapter target for Chapter 10

**Chapter 10 — Transformation Management (TRN)**  
Source: Note 10

### What to preserve in Chapter 10

- the stage transition investment model
- the argument that vendors helping stage advancement become embedded
- the switching-cost logic around GOV and SKG

### What to reduce in Chapter 10

- note-specific GTM framing that reads as too narrow for a book chapter

### What to expand in Chapter 10

- explain what stage advancement really requires from buyers
- make the customer-success and sales implications feel strategic rather than tactical
- connect stage transitions back to the whole framework, not just the vendor opportunity

### What to add in Chapter 10

- “Why transformation is architectural, not linear change management”
- “How vendors become embedded in stage advancement”
- “Where switching costs form first”
- a buyer transformation journey where one vendor becomes structurally embedded by owning graph contribution and governance architecture

### Recommended visual for Chapter 10

- stage transition investment and lock-in map

### Recommended bridge out of Chapter 10

The final question is how all of these dimensions behave as one system rather than eleven separate capability checklists.

---

## Chapter 11 surgery plan

### Chapter target for Chapter 11

**Chapter 11 — The Integration Model**  
Source: Note 11

### What to preserve in Chapter 11

- the cybernetic loop
- the cross-dimensional integration map
- the vendor-category verdict
- the return-to-Note-0 logic

### What to reduce in Chapter 11

- standalone-note framing that treats this as a detachable capstone

### What to expand in Chapter 11

- make the integrated system feel more visual and more inevitable
- show why products are excluded before comparison if they cannot participate in the loop
- make the vendor-category argument more concrete with buyer-facing language

### What to add in Chapter 11

- “Why the loop is the architecture”
- “What integration depth means in real evaluation terms”
- “Why category verdicts are about system fit, not feature count”
- a hypothetical vendor evaluation where a broad-feature vendor loses to a narrower but deeply integrated enabler

### Recommended visual for Chapter 11

- full cybernetic loop diagram

### Recommended bridge out of Chapter 11

This chapter should not be the final stop. It should pass into a **new conclusion** that turns the integrated model into action for readers.

---

## New conclusion plan

This does not currently exist in the note series and should be written fresh.

### Title candidates for the conclusion

- **What Leaders Should Do Now**
- **The Next 12 Months**
- **From Framework to Decision**

### What the conclusion should contain

- what buyers should stop funding
- what capabilities are now structurally strategic
- how to identify real Stage 2+ platforms
- where neutral products become exposed
- what the market gets wrong when it frames this as “AI enhancement” rather than operating-model replacement

### Definition of done for the conclusion

The reader should leave the book with conviction, not just comprehension.

---

## Priority order for rewriting

If this is done in sequence, the most valuable rewrite order is:

1. Introduction (Note 0 rewrite)
2. Chapter 1 (Three Operating Planes)
3. Chapter 5 (SKG)
4. Chapter 6 (GOV)
5. Chapter 11 (Integration Model)
6. Chapters 2–4
7. Chapters 7–10
8. New conclusion

### Why this order works

- it locks the thesis first
- then the architecture
- then the spine and governance logic
- then the capstone
- then the operational dimensions

---

## Final editorial check

The ASAF manuscript is ready when:

- it no longer reads like 12 adjacent notes
- each chapter clearly hands off to the next
- the strongest tables remain but the prose carries the argument
- the human, governance, and transformation implications feel concrete
- the conclusion tells the reader what to do with the framework, not just what it is
