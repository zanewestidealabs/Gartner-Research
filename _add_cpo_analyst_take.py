"""
Add a CPO-targeted v3 of the AIUC-1 Smart Brevity Analyst Take report.
Reframes the existing v2 from a Chief Product Officer's product development perspective.
Removes first-person healthcare-organization references ("our data") and replaces
them with third-person product-officer framing.
"""
import json
import copy

with open("analyst_take_reports.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)

# Find the v2 report
v2 = None
for r in data["reports"]:
    if r["id"] == "aiuc1-agentic-compliance-v2":
        v2 = r
        break

assert v2, "v2 report not found"

# Deep copy and modify
v3 = copy.deepcopy(v2)
v3["id"] = "aiuc1-agentic-compliance-v3-cpo"
v3["label"] = "Analyst Take - AIUC-1: CPO Perspective — Product Compliance for Agentic AI (v3)"
v3["title"] = "Analyst Take: Your Product's SOC 2 Doesn't Know What Your AI Agents Are Doing"
v3["subtitle"] = "Chief Product Officer perspective. Reframes AIUC-1 compliance as a product development and GTM imperative — from the builder's side of the table."

# ── Rewrite body sections ──

v3["body_sections"] = [
    {
        "heading": "Your Product's Compliance Stack Has an AI-Shaped Hole",
        "body": "Recently I have spent a significant amount of time talking to AI vendors building platforms and SaaS products trying to better understand how they are overcoming the controls necessary to secure their platforms and worrying about the compliance frameworks that the CISOs at their customers are concerned about. The uncomfortable truth: products that have earned SOC 2 Type II certification, HIPAA compliance, and PCI DSS Level 1 validation are simultaneously shipping AI agents that no existing audit has ever examined. This isn't theoretical — AI agents embedded in shipping products are querying databases, making API calls, generating recommendations, and taking autonomous actions on customer data that those compliance certifications are supposed to protect. SOC 2 audits your infrastructure, HIPAA audits PHI safeguards, PCI audits the cardholder data environment. None of them audit what happens when an AI agent inside your product chains together three tool calls and generates output from data it was never explicitly told to access. For product leaders, this isn't just a compliance risk — it's a GTM liability. Your customers' CISOs are beginning to ask questions that your current certifications cannot answer. AIUC-1 was built to close this gap, and the CPOs who move first will turn compliance into a competitive differentiator."
    },
    {
        "heading": "What AIUC-1 Actually Does That SOC 2 Doesn't — And Why Product Leaders Should Care",
        "body": "AIUC-1 is not a replacement for SOC 2, HIPAA, or PCI DSS. It's the missing layer on top. Where traditional frameworks govern the container — the infrastructure, the access controls, the network boundaries — AIUC-1 governs what the AI inside your product actually does. For a Chief Product Officer, this distinction is critical: your existing certifications tell buyers that your platform is secure. AIUC-1 tells them that your AI features are safe, reliable, and auditable. It introduces controls across six categories with no equivalent in traditional compliance. Data & Privacy asks whether your product's AI agents limit data collection to what's necessary, whether they can expose one customer's data to another, and whether they respect IP boundaries. Reliability tackles hallucination prevention, hallucination testing, and tool call safety — when your product's AI agent invokes an external API, are there restrictions on unsafe calls? Is that behavior tested by a third party? Accountability addresses transparency head-on: logging all model activity, mandating AI disclosure to users, and defining what I'd describe as an AI audit knowledge graph — a persistent, queryable structure that traces every AI decision from input context through reasoning to output action. For product teams, AIUC-1 compliance isn't just about avoiding risk. It's about building features that enterprise buyers can actually adopt without stalling in security review."
    },
    {
        "heading": "The Healthcare Product Problem — And Why It Matters for Every Regulated Vertical",
        "body": "Let me make this concrete with the vertical where this gap is most dangerous for product teams: healthcare. Consider a product team shipping an AI-powered clinical decision support platform. The product has earned SOC 2 Type II. The company will sign a HIPAA BAA. The platform's AI agents access EHR data, cross-reference drug interactions, and generate recommendations for clinicians. The question that will stall your next enterprise deal: when that AI agent pulls a patient record, what reasoning led it to do so? If it generates an incorrect drug interaction alert based on hallucinated data, can anyone — the customer, your support team, a regulator — reconstruct why? The answer today is no, and every healthcare CISO evaluating your product knows it. HIPAA was written for a world where humans access data through applications with defined workflows. AI agents don't follow workflows; they reason, plan, and act. The only way to make your product's AI auditable is through a knowledge graph that captures the full chain of agent perception, planning, tool invocation, and output. AIUC-1 is the first compliance framework to require this infrastructure. This isn't just healthcare — any product that ships AI agents touching regulated data faces the same black box problem. But healthcare is where the consequences are measured in patient safety and where procurement cycles will gate on this first."
    },
    {
        "heading": "Attainability: Why AIUC-1 Is a Product Advantage, Not Just a Compliance Cost",
        "body": "Here's what makes AIUC-1 different from yet another compliance framework that adds overhead to your product roadmap: 78.6% of its requirements are obligations on the AI vendor — which is you. That sounds like a burden, but it's actually the opportunity. Think about what this means from a GTM perspective. Traditional compliance (SOC 2, HIPAA, PCI DSS) creates overhead that your customers have to manage on their end. AIUC-1 flips this. Third-party testing mandates — adversarial robustness, harmful output testing, hallucination testing, tool call testing — are your obligations as the vendor, and they produce standardized artifacts that your customers can consume without building internal AI testing capability. A 200-person clinic evaluating your platform can ask 'show me your test results' with exactly the same confidence as a major health system. AIUC-1 certification works as a binary procurement signal: your product either passes third-party testing or it doesn't. For CPOs, this simplicity is the competitive lever. The first products in each regulated vertical to achieve AIUC-1 certification will compress their customers' security review cycles from months to days. That's a product advantage, not a compliance cost."
    },
    {
        "heading": "What Your Product Team Should Do This Quarter",
        "body": "Whether your product serves a 50-person clinic or a Fortune 500 health system, the starting point is the same: First, audit your own certifications. Pull your latest SOC 2 Type II report and any HIPAA documentation. Search for any mention of AI agents, model behavior, hallucination testing, or tool call safety. You won't find it — and your customers' security teams have already noticed. Document this gap; it's the product roadmap case for AIUC-1 investment. Second, run a 10-case reasoning chain audit on your own product. Pick 10 random actions your product's AI agents have taken in the last 30 days. Try to reconstruct the full reasoning chain: what triggered the action, what data was accessed, what tools were invoked, and why the AI produced the output it did. I predict you'll reconstruct less than 20% of that chain. That gap is your knowledge-graph infrastructure investment case. Third, get ahead of your buyers. Enterprise procurement teams are beginning to add AI-specific compliance questions to RFPs. The CPOs who can answer 'yes, here are our AIUC-1 test results' will close deals that competitors are still negotiating through security review. The window between 'AIUC-1 is emerging' and 'AIUC-1 is expected in every RFP' is measured in quarters, not years. Product leaders who treat this as a feature investment rather than a compliance tax will own the positioning advantage."
    },
]

# ── Rewrite positioning statements for CPO audience ──

v3["positioning_statements"] = [
    {
        "id": "healthcare-product-transparency",
        "label": "Healthcare AI Products: The Black Box Liability",
        "position": "Product teams shipping AI-powered platforms into healthcare face a compliance gap that no existing framework addresses: no existing framework (SOC 2, HIPAA, or PCI DSS) requires vendors to demonstrate what their AI agents actually do with patient data, how decisions are made, or whether autonomous actions can be audited end-to-end — and healthcare CISOs are now gating procurement on exactly these questions.",
        "positionComponents": {
            "importantIssue": "AI agents embedded in healthcare SaaS products operate autonomously on protected health information with no auditable trail of reasoning, tool calls, or data access patterns. This creates a product liability and procurement blocker that existing certifications cannot resolve.",
            "judgment": "AIUC-1 is the first framework to mandate auditable transparency mechanisms (including lineage graphs, tool call restrictions, and third-party hallucination testing) that directly close the agentic AI black box gap — giving product teams a certifiable answer to the questions blocking enterprise healthcare deals.",
            "state": "Without AIUC-1 or an equivalent AI-specific certification, product teams are asking customers to accept vendor self-attestations for AI behaviors that no current audit methodology can verify — and sophisticated buyers are pushing back.",
            "drama": "Your HIPAA BAA says nothing about what happens when your product's AI agent hallucinates a drug interaction or autonomously queries a patient record it was never prompted to access. Your customer's CISO knows this. Do you?"
        },
        "justification": {
            "context": "HIPAA was written for human-driven data workflows. SOC 2 Type II audits validate controls around logical access and change management — but they audit the infrastructure, not the inference. When a product's AI agent autonomously chains together tool calls (querying an EHR, cross-referencing a formulary, and generating a recommendation), no existing audit framework traces that chain of reasoning or validates that the agent stayed within its authorized scope.",
            "evidence": "AIUC-1 addresses this directly through 5 specific control categories: D001 (hallucination prevention), D003 (unsafe tool call restriction), E015 (model activity logging), A005 (cross-customer data isolation), and A006 (PII leakage prevention). These are AIUC-1-specific controls with no equivalent in SOC 2 or HIPAA. For product teams, implementing these controls creates certifiable evidence that accelerates procurement.",
            "actionBridge": "Product leaders should immediately begin mapping their AI agent architectures to AIUC-1 control requirements, prioritizing D001-D004 (reliability controls) and A005-A006 (data isolation controls) as the highest-impact areas for healthcare product certification."
        },
        "actions": [
            {
                "action": "Map your product's AI agent tool call chains to AIUC-1 requirements D001-D004 (reliability) and A005-A006 (data isolation), identifying gaps between current implementation and certification requirements.",
                "whyNonObvious": "Most product teams assume their existing security controls cover AI. They don't. AI agent behaviors (reasoning chains, tool invocation patterns, hallucination rates) are entirely out of scope for SOC 2 and HIPAA — and mapping the gap is the first step to closing it.",
                "outcome": "A concrete roadmap for AIUC-1 certification that product and engineering can prioritize alongside feature development."
            },
            {
                "action": "Implement an AI lineage graph or equivalent transparency mechanism that captures how your product's AI agents access, process, and output PHI across tool call chains — and expose it as an auditable artifact for customer security reviews.",
                "whyNonObvious": "The concept of a knowledge graph for AI agent auditability doesn't exist in traditional compliance — but it's exactly what healthcare CISOs will demand. Building it now converts a compliance requirement into a product differentiator.",
                "outcome": "A demonstrable, verifiable transparency mechanism that replaces trust-based assurances with artifact-based validation in procurement conversations."
            },
            {
                "action": "Establish a quarterly third-party AI testing cadence aligned to AIUC-1 requirements C010-C012 and D002/D004, specifically for hallucination rates and unauthorized tool call behaviors in your product.",
                "whyNonObvious": "Annual SOC 2 Type II audits are too infrequent for AI systems that change behavior with every model update. Proactively testing and publishing results positions your product ahead of the compliance curve.",
                "outcome": "Continuous assurance evidence that your product's AI agents remain within safety and reliability tolerances — and a procurement asset that competitors cannot match."
            }
        ],
        "alignment": {
            "positionToFinding": "Finding 1 (SOC 2/HIPAA gap for agentic AI) directly supports the position that traditional frameworks cannot govern AI behaviors in healthcare products, creating a procurement blocker that AIUC-1 certification resolves.",
            "actionsToRecs": [
                "Action 1 → Recommendation: Map product AI architecture to AIUC-1 control requirements",
                "Action 2 → Recommendation: Build lineage-graph transparency as a product feature",
                "Action 3 → Recommendation: Shift from annual audits to continuous AI product testing"
            ],
            "justificationSources": "AIUC-1 Standard (Categories A, C, D, E); NIST AI RMF 1.0 (Measure function); HIPAA Security Rule §164.312"
        }
    },
    {
        "id": "product-gtm-advantage",
        "label": "Product GTM: AIUC-1 as Competitive Differentiator",
        "position": "The first AI-powered products in each regulated vertical to achieve AIUC-1 certification will gain a structural procurement advantage — compressing buyer security review cycles from months to days and converting a compliance requirement into a GTM moat that undifferentiated competitors cannot quickly replicate.",
        "positionComponents": {
            "importantIssue": "Enterprise procurement cycles for AI-powered products are lengthening as security teams add AI-specific evaluation criteria that no existing vendor certification addresses. Product teams without AI-specific compliance evidence face 3-6 month security review delays.",
            "judgment": "AIUC-1's vendor-certification model produces standardized, third-party-validated test artifacts that directly answer the AI-specific questions blocking enterprise deals — converting compliance investment into sales acceleration.",
            "state": "Today, product teams respond to AI security questions in RFPs with ad hoc documentation, custom security questionnaire responses, and architecture review sessions. This doesn't scale and produces inconsistent buyer confidence.",
            "drama": "Your competitor just handed the CISO a standardized AIUC-1 test report. You handed them a 40-page security questionnaire and a promise to schedule an architecture review. Who closes the deal first?"
        },
        "justification": {
            "context": "Enterprise buyers in regulated verticals are adding AI-specific evaluation criteria to procurement processes faster than product teams can respond. Questions about AI hallucination testing, tool call safety, and data isolation are appearing in RFPs that product teams have no standardized way to answer. The result is extended security review cycles, custom documentation burdens, and lost deals to competitors who can provide clearer compliance evidence.",
            "evidence": "AIUC-1 produces standardized test artifacts for exactly these questions: B001 (third-party adversarial testing results), D002 (third-party hallucination testing results), C010-C012 (harmful output testing), and D003 (tool call safety validation). These artifacts are designed to be consumable by procurement teams without specialized AI expertise — functioning as the AI equivalent of a SOC 2 Type II report.",
            "actionBridge": "CPOs should prioritize AIUC-1 certification as a product investment with measurable GTM impact, not as a compliance cost center. The ROI model is straightforward: shortened security review cycles × deal velocity × competitive win rate."
        },
        "actions": [
            {
                "action": "Add AIUC-1 certification to your product roadmap as a GTM feature, not a compliance checkbox. Assign it product management ownership with clear milestones tied to target customer segments.",
                "whyNonObvious": "Most organizations treat compliance as a back-office function. Treating AIUC-1 as a product feature ensures it gets the engineering investment, PM prioritization, and marketing positioning it needs to drive revenue impact.",
                "outcome": "AIUC-1 certification delivered on a product timeline with GTM launch support, rather than trailing as an afterthought."
            },
            {
                "action": "Create a standard 'AI Trust Package' that bundles your AIUC-1 test artifacts with your existing SOC 2 report and any vertical-specific certifications, and make it available in your sales team's deal toolkit.",
                "whyNonObvious": "Buyers evaluate AI trust holistically. Presenting AIUC-1 alongside existing certifications in a single package signals maturity and prevents the AI compliance conversation from becoming a separate objection-handling exercise.",
                "outcome": "A repeatable sales asset that compresses security review cycles and differentiates your product in every competitive RFP."
            },
            {
                "action": "Benchmark your current security review cycle times for enterprise deals in regulated verticals. Set a target to reduce them by 50% within two quarters of achieving AIUC-1 certification.",
                "whyNonObvious": "Without a baseline, AIUC-1's GTM impact is anecdotal. Measuring deal velocity before and after certification creates the ROI narrative for continued compliance investment and demonstrates product-led growth impact.",
                "outcome": "Quantified evidence that AIUC-1 certification accelerates revenue, justifying ongoing investment in AI governance as a product function."
            }
        ],
        "alignment": {
            "positionToFinding": "Finding 2 (AI compliance as procurement blocker) directly supports the position that vendor-side certification creates measurable GTM advantage in regulated verticals.",
            "actionsToRecs": [
                "Action 1 → Recommendation: Treat AIUC-1 certification as a product feature with PM ownership",
                "Action 2 → Recommendation: Bundle AI trust artifacts into a sales-ready package",
                "Action 3 → Recommendation: Measure and optimize deal velocity impact"
            ],
            "justificationSources": "AIUC-1 Standard (vendor-side certification model); AIUC-1 Categories A, D mandatory requirements"
        }
    },
    {
        "id": "knowledge-graph-product-infrastructure",
        "label": "Building the AI Audit Layer Into Your Product",
        "position": "The fundamental technical challenge for product teams is that traditional observability and logging architectures cannot capture the dynamic reasoning chains of agentic AI — and the only way to make your product's AI agents auditable is through a persistent, queryable knowledge graph that captures the full chain of perception, reasoning, tool invocation, and output for every agent action.",
        "positionComponents": {
            "importantIssue": "AI agents in your product don't follow scripts. They reason, plan, invoke tools, and make decisions dynamically. Traditional application logs capture what happened, but not why — making it impossible for your customers (or your own team) to determine whether an AI agent's autonomous behavior was authorized, appropriate, and safe.",
            "judgment": "AIUC-1's requirements for model activity logging (E015), lineage tracking, and accountability graphs implicitly mandate a knowledge-graph-based audit infrastructure — and product teams that build this into their architecture now will have a structural compliance and product quality advantage.",
            "state": "No major compliance framework today requires tracing the reasoning chain of an autonomous system. AIUC-1 is the first to make this a testable, auditable control — and your product needs to be ready.",
            "drama": "When your product's AI agent autonomously reclassifies a patient risk score, flags a transaction as fraudulent, or escalates a support ticket, can your customer explain why it did that? Can your engineering team prove it was authorized to? If the answer is no, you have a product problem, not just a compliance gap."
        },
        "justification": {
            "context": "Traditional application observability (structured logs, APM traces, error tracking) captures discrete events. But agentic AI operates through multi-step reasoning chains: an agent perceives context, plans actions, invokes tools, evaluates results, and decides next steps. A conventional log entry records 'Agent called Patient API at 14:32:07' but doesn't capture that the agent decided to query that API because a previous tool call returned an ambiguous drug interaction. Without this reasoning chain, neither your customers' auditors nor your own engineering team can assess whether the agent's behavior was within scope.",
            "evidence": "AIUC-1 addresses this through three converging control families: E015 (model activity logging) requires capturing all inference requests and responses. Lineage requirements mandate tracing from code to data to model to decision to outcome. Accountability requirements demand a queryable structure mapping decisions to inputs, tool calls, and responsible owners. Together, these define the minimum viable specification for an AI audit knowledge graph that product teams must implement.",
            "actionBridge": "Product teams should begin implementing knowledge-graph-based audit infrastructure now — starting with tool call logging and reasoning chain capture — as a core platform capability rather than an afterthought. This is both a compliance prerequisite and a product quality investment that improves debugging, incident response, and customer trust."
        },
        "actions": [
            {
                "action": "Instrument your product's AI agent tool calls to capture: (1) triggering context, (2) the agent's reasoning for the invocation, (3) input parameters, (4) output, and (5) the agent's interpretation of the result — stored as linked nodes in a graph structure.",
                "whyNonObvious": "Most engineering teams log tool calls as flat event records. The graph structure is essential because auditors and your own incident response team need to traverse the reasoning chain ('Why did the agent call this API? What did it do with the result?'), which requires graph traversal, not log search.",
                "outcome": "An auditable, queryable chain of custody for every AI decision in your product — the foundation for AIUC-1 certification and a powerful debugging/incident response tool for your engineering team."
            },
            {
                "action": "Define and enforce 'agent scope boundaries' for every AI agent in your product — documenting which tools it may invoke, which data sources it may access, and under what conditions it must escalate to a human — enforced at the tool-call layer, not just in system prompts.",
                "whyNonObvious": "AIUC-1 D003 (restrict unsafe tool calls) and B006 (prevent unauthorized agent actions) are only testable if scope boundaries are codified in your product architecture. System prompts are not auditable controls — and your customers' security teams know this.",
                "outcome": "A testable, enforceable permission model that transforms vague prompt-based guardrails into auditable policy-as-code, satisfying both AIUC-1 requirements and enterprise buyer expectations."
            },
            {
                "action": "Run an internal audit: reconstruct the reasoning chain for 10 random AI agent actions from your product's production environment over the past 30 days. Document what you can and cannot reconstruct.",
                "whyNonObvious": "This exercise will expose your product's audit gap concretely. Most product teams discover they can reconstruct less than 20% of an agent's reasoning chain from existing logs — making the case for knowledge-graph infrastructure investment self-evident to engineering leadership.",
                "outcome": "A quantified gap assessment that justifies product investment in AI audit infrastructure and provides a baseline for measuring progress toward AIUC-1 readiness."
            }
        ],
        "alignment": {
            "positionToFinding": "Finding 3 (traditional observability cannot capture AI reasoning chains) directly supports the position that knowledge-graph-based auditability must be built into the product architecture.",
            "actionsToRecs": [
                "Action 1 → Recommendation: Implement graph-based reasoning chain capture as a product platform capability",
                "Action 2 → Recommendation: Codify agent scope boundaries as enforceable product policy",
                "Action 3 → Recommendation: Internal audit to quantify the current reasoning-chain gap"
            ],
            "justificationSources": "AIUC-1 Requirements E015, D003, B006; NIST AI RMF Measure Function"
        }
    }
]

# ── Update notes ──
v3["notes"] = "This Analyst Take is written for Chief Product Officers and product leaders at organizations building AI-powered SaaS products. It reframes the AIUC-1 compliance gap from a product development and GTM perspective — treating certification as a competitive differentiator rather than a compliance cost. Healthcare examples are presented from the product builder's perspective, not the healthcare organization's. The three positioning statements target: (1) Healthcare product teams facing procurement blockers, (2) CPOs seeking GTM advantage through compliance, (3) Engineering leaders building auditable AI architectures. All data, framework references, and AIUC-1 requirement citations are identical to the v2 Smart Brevity Edit. The 78.6% mandatory figure reflects 33 of 42 active AIUC-1 requirements (after merging E007→E004 and E014→E017)."

# ── Update guidance target role ──
v3["guidance"] = copy.deepcopy(v2["guidance"])
v3["guidance"]["ideation_prompts"]["target_role"] = "Chief Product Officers, VPs of Product, product managers, and engineering leaders at companies building AI-powered SaaS platforms — particularly those selling into regulated verticals (healthcare, financial services, government)."
v3["guidance"]["ideation_prompts"]["goals"] = "Help product leaders understand why AIUC-1 certification is a GTM differentiator, how to build auditable AI architectures, and how to convert compliance investment into measurable deal velocity improvement."

# ── Update graphic captions for CPO framing ──
if v3.get("graphics"):
    v3["graphics"] = copy.deepcopy(v2["graphics"])
    # Update the bottom line of the second graphic
    for g in v3["graphics"]:
        if "Compliance Model Flip" in g.get("title", ""):
            g["takeaway"] = "AIUC-1 shifts the compliance burden to the vendor — which is you. The first products to certify will compress buyer security review cycles from months to days."
            g["caption"] = "Traditional frameworks require your buyers to build internal audit capabilities. AIUC-1 inverts this: you produce the test artifacts, and buyers of any size can evaluate them. That's a product advantage."

# ── Insert into reports array ──
data["reports"].append(v3)

with open("analyst_take_reports.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=6, ensure_ascii=False)

print(f"Added report: {v3['id']}")
print(f"Label: {v3['label']}")
print(f"Total reports now: {len(data['reports'])}")
