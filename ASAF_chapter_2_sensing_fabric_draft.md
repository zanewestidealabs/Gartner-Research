# ASAF Chapter 2 Draft — Sensing Fabric

**Working book title:** _The End of the Tiered SOC_  
**Chapter:** 2  
**Source base:** Note 2 of `static/docs_asaf_market_notes.json`

---

## Chapter 2 — Sensing Fabric

If the three-plane model replaces the tiered SOC, then the first practical question is what the system should actually receive as input. That question sounds obvious, but it is where much of the market still slips back into legacy thinking.

In the older architecture, the input layer of security operations was effectively the alert. Sensors produced alerts, alerts entered queues, analysts triaged them, and the rest of the operating model formed around the challenge of deciding which alerts deserved deeper human attention. Even when products improved fidelity, correlation, or prioritization, the architecture remained fundamentally alert-centric. The goal was better alert management.

ASAF argues that this is no longer enough.

In an agentic security architecture, the Sensing plane must produce more than alerts. It must produce **continuous, adversary-validated, confidence-scored signals** that the rest of the system can reason over. That distinction matters because an alert is primarily a notification event. A signal is an architectural input. An alert says, in effect, “something may require attention.” A meaningful signal says something closer to, “this pattern of evidence may reflect adversary behavior, here is the current confidence, here is the context that should travel with it, and here is how it relates to other observed conditions.”

That is a different output requirement. It changes what sensing systems are for.

This is why Chapter 2 begins with a sharper claim than the market usually hears: **signature detection and alert generation are Stage 0 capabilities**. They may still exist inside modern products, and they may still have utility, but they do not define the capability floor of an agentic operating system. In the new model, the question is not whether a tool can generate more alerts with fewer false positives. The question is whether it can emit the kind of adversary-relevant signal that allows reasoning, governance, and execution to behave as one system.

---

## Why better alerts are not the same thing as new architecture

The sensing discussion gets muddled because many vendors correctly observe that alert quality matters. Better fidelity matters. Lower noise matters. Richer context matters. The mistake is assuming that all progress at the input layer is therefore architectural progress.

It is not.

A better alert is still an alert if the system remains organized around notifying a human queue. A cleaner triage process is still a legacy process if the core output is designed for analysts to interpret downstream rather than for reasoning systems to act on directly. Many products improve alert economics without changing the architecture those alerts serve.

This is the critical difference between optimization and substitution.

Optimization asks: how do we make the alert stream less painful?

Substitution asks: what should replace the alert stream as the primary input to the operation?

That second question leads directly to the idea of a sensing fabric.

A fabric is not just a collection layer. It is not simply a broader telemetry aggregator. It is an input architecture that continuously translates raw observations into adversary-relevant signals that can be consumed by reasoning and updated over time. It treats sensing not as a front door to the analyst queue, but as a live producer of system-quality inputs.

That is why the phrase **Sensing Fabric** matters. It suggests continuity, composition, and bidirectional behavior. Signals are emitted, refined, written back, and recalibrated. The system does not merely observe. It learns what kinds of observations matter more as the rest of the loop evolves.

---

## What a sensing fabric must emit

To understand the chapter, it helps to name the qualities of a meaningful sensing output.

A mature sensing layer should emit at least four things.

### 1. Adversary relevance

The system must express not just that an event occurred, but why it may matter in an adversary context. That means the signal should already carry some view of tactic, behavior pattern, exposure relationship, or evidentiary relevance.

### 2. Confidence

The signal should not present every observation as equally meaningful. It should express current confidence, supporting evidence, and in stronger systems, the basis for uncertainty. This matters because the downstream reasoning layer needs something more useful than a binary trigger.

### 3. Context portability

The signal should travel with usable context: affected assets, related telemetry, time relationships, prior observations, and ties to known models or exposures. Without that, the reasoning plane must reconstruct too much of the world from scratch.

### 4. Updateability

A sensing output should not be a dead-end event. It should be something that can be refined, rescored, or rewritten as the system learns more. This is what allows sensing to become part of a loop rather than a one-time notifier.

Taken together, these qualities explain why the sensing plane in ASAF is not just “detection, but better.” It is the production of operationally meaningful signal.

---

## The stage progression of sensing

One of the strengths of the ASAF note series is that it makes the progression explicit. Sensing changes across stages, and the progression matters for both buyers and vendors.

At **Stage 0**, sensing is dominated by signature logic, alert generation, and static rules. The system recognizes known patterns and pushes events toward human review.

At **Stage 1**, sensing becomes more adaptive. Behavioral analytics, anomaly detection, and ML-supported detection improve coverage and reduce some noise. But the architecture is still largely alert-centric. Better analytics help the queue, but they do not replace it.

At **Stage 2**, the floor changes. Sensing begins to produce adversary-model-informed, confidence-scored outputs that are useful to an autonomous or semi-autonomous reasoning layer. This is where the market starts to diverge sharply. Some products market themselves as advanced because they reduce false positives. Others begin to act like genuine sensing systems because they emit structured signals that can drive inference.

At **Stage 3**, sensing becomes bidirectional. It does not only detect. It updates the adversary model in real time. Signals help reshape what the system believes, and the evolving system belief reshapes what the sensing layer prioritizes.

At **Stages 4 and 5**, the sensing layer becomes increasingly self-calibrating. Coverage, fidelity, and signal priority adjust continuously as the system’s model of adversary behavior and environmental exposure evolves.

The important point is not to memorize the ladder. It is to see that the progression moves from detection to signal production, then from signal production to live calibration.

---

## How sensing becomes bidirectional

This chapter also matters because it introduces one of the book’s recurring themes: **bidirectional operation**.

In a legacy model, sensing is mostly upstream. Telemetry comes in. Alerts go out. The information flow is one-way enough that teams can treat sensing as a separate product domain.

In an agentic model, that separation weakens.

A reasoning system that confirms or rejects adversary hypotheses should alter what the sensing layer looks for next. A governance system that changes authority or monitoring policy should alter sensing scope and fidelity. An exposure system that discovers a newly critical attack surface should alter sensing priorities. A shared knowledge graph that accumulates evidence should make the next emitted signals richer and more discriminating.

That is why sensing becomes bidirectional. It is still the input plane, but its behavior is increasingly shaped by what the rest of the system learns.

This matters strategically because many current tools are good at ingesting telemetry yet weak at participating in the feedback structure that makes a sensing fabric truly architectural. They can observe, but they cannot learn coherently with the system.

---

## An operating-model scene: alert flood versus sensing fabric

Imagine two enterprise programs looking at a burst of suspicious identity activity.

In the first environment, the system produces dozens or hundreds of related alerts. Some refer to impossible travel. Others flag anomalous login times. Others note risky geolocation or permission change behavior. Analysts inherit a noisy pile of fragments and begin deciding which items deserve attention. The work of constructing meaning happens downstream, under human load.

In the second environment, the sensing layer observes the same underlying activity but emits a smaller set of confidence-scored adversary-relevant signals. Those signals already bind together identity anomalies, privilege context, exposure relevance, asset criticality, and pattern similarity to prior behavior. Instead of dumping raw notifications into a queue, the system produces structured inputs for reasoning.

Both environments “detected” something. But only one produced the kind of input that helps a next-generation control system behave coherently.

That difference is the essence of the chapter.

---

## Why products that stop at alert improvement remain trapped

This is where the chapter becomes commercially sharp.

A vendor may legitimately say that its alerting is better than before. It may reduce false positives, add threat intelligence, group incidents, or prioritize by risk. All of that can matter. But if the product still imagines its primary task as delivering better items into a human-managed queue, it is still trapped in the old architecture.

That does not make the product valueless. It makes its strategic ceiling lower.

Products that remain alert-first can remain useful in Stage 1 and portions of Stage 2. But as enterprises expect sensing to emit structured signals for machine reasoning and bidirectional model updates, the old product story becomes cramped. The tool begins to look like an optimization layer for an operating model that is no longer the center of design.

This is why some detection categories will feel pressure even if their products continue improving. They are improving inside the wrong frame.

---

## Why this chapter matters

The sensing chapter matters because it is where the reader first sees what it means for the new architecture to require different outputs, not just better versions of old ones.

If the reader leaves this chapter believing that agentic security simply means fewer false positives, then the book has failed. The real point is stronger: the operation needs a different kind of input, because the rest of the system is no longer organized around alert queues and human escalation.

Once that shift becomes clear, the next problem becomes inevitable. If sensing emits better signals, what system interprets them? If alerts are no longer the primary organizing object, then investigation cannot remain alert by alert either.

That takes the book directly to reasoning.

---

## Three takeaways

- A sensing fabric is not just improved detection; it is an input architecture that emits adversary-relevant, confidence-shaped signals for the rest of the system.
- Better alerts can improve legacy operations without changing the architecture those operations depend on.
- The strategic shift in sensing is from notification to signal production, and then from signal production to bidirectional calibration.

## Two implications

- Buyers should test sensing products by the quality and structure of the outputs they emit for reasoning, not just by alert reduction or prioritization claims.
- Vendors should assume that products built mainly to improve alert queues face a lower strategic ceiling than products that help construct a real sensing fabric.

## Bridge to Chapter 3

Once the system begins receiving richer signals, the central problem is no longer alert volume. It is how the operation interprets those signals, forms judgments, and decides what they mean. That is the work of the Reasoning plane.
