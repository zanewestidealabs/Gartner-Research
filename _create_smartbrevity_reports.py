"""
Create Smart Brevity condensed versions of buyer-facing-general and cpo-product-strategy-general
MDR pricing insight reports. Adds them to mdr_market_insight_reports.json as new dropdown options.

Smart Brevity principles:
- Lead with the strongest point
- Cut filler words and phrases
- Active voice throughout
- Front-load value in every sentence
- Preserve ALL data points and substantive claims
- ~25% reduction target
- No em dashes (use commas, colons, periods instead)
"""
import json
import copy

JSON_PATH = "mdr_market_insight_reports.json"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Find source reports
buyer_gen = None
cpo_gen = None
for r in data["reports"]:
    if r["id"] == "buyer-facing-general":
        buyer_gen = r
    elif r["id"] == "cpo-product-strategy-general":
        cpo_gen = r

assert buyer_gen is not None, "buyer-facing-general not found"
assert cpo_gen is not None, "cpo-product-strategy-general not found"

# ============================================================
# BUYER GENERAL CONDENSED
# ============================================================
buyer_condensed = {
    "id": "buyer-facing-general-condensed",
    "label": "Buyer / General (Smart Brevity)",
    "title": buyer_gen["title"],
    "summary": "AI is reshaping MDR cost structures, but most providers have not adapted their pricing models. Outcome-based pricing remains underadopted despite clear buyer demand for measurable results. At 2.35/5.0 overall, the MDR market is in early-stage pricing maturity, with outcome-linked fees nearly absent.",
    "spa": "By 2028, 40% of MDR contracts will include at least one outcome-linked pricing component tied to measurable security improvements, up from less than 5% today. Vendors that fail to develop outcome-based commercial models by 2027 face a structural competitive disadvantage.",
    "findings": [
        {
            "header": "Outcome-based pricing adoption is negligible across the MDR market.",
            "body": "Of 95 vendors assessed, PRC-SUC (success and outcome fees) averages just 1.63/5.0. 82 vendors (86%) score 2.0 or below, and only two score above 3.0. The median is 1.0, the lowest possible, meaning most MDR providers have made zero progress toward tying commercial terms to measurable outcomes."
        },
        {
            "header": "AI-mature vendors demonstrate measurably higher pricing sophistication.",
            "body": "Vendors with Significant or higher AI pricing influence (19 providers) average 2.86 across all pricing dimensions versus 1.84 for Minimal-influence vendors (27 providers), a 1.02-point gap on a 5-point scale. This holds across every dimension but is most pronounced in outcome alignment (PRC-OUT): 2.58 versus 1.04."
        },
        {
            "header": "The market misunderstands outcome-based pricing.",
            "body": "Most vendors equate \"outcomes\" with SLA uptime guarantees or breach notification speeds. True outcome-based pricing ties commercial terms to measurable security improvements: MTTD/MTTR reduction, quantifiable risk posture gains, or incident frequency reduction commitments backed by financial mechanisms such as breach warranties or performance-based fee adjustments."
        },
        {
            "header": "Composable pricing is a prerequisite for outcome-based evolution; two-thirds of vendors remain subscription-only.",
            "body": "64 of 95 vendors (67%) operate pure subscription models, averaging just 1.34 on PRC-SUC. The 27 composable-model vendors average 2.41 on the same dimension, nearly double. Outcome-based pricing requires modularity that subscription-only models cannot support."
        },
        {
            "header": "AI is creating an efficiency dividend that vendors capture rather than share with buyers.",
            "body": "AI-driven automation is reducing per-incident detection and response costs, but vendors improve margins without passing gains to clients. PRC-USG averages just 2.14/5.0, meaning buyers have no visibility into how AI efficiency improvements affect their service cost."
        },
        {
            "header": "The pricing maturity gap between leaders and laggards is widening, driven by AI adoption differences.",
            "body": "Top-10 vendors by pricing score average 3.65/5.0 versus the market average of 2.35, a 1.30-point spread. Top performers uniformly show higher AI influence (3.5+), composable pricing, and at least nascent outcome-linked terms. This gap will widen as AI-first vendors fund outcome guarantees that subscription-only providers cannot match."
        }
    ],
    "recommendations": [
        {
            "header": "Redefine outcome-based pricing in concrete, measurable terms.",
            "body": "Move beyond SLA guarantees. Establish commercial structures tied to quantifiable security outcomes: MTTD/MTTR improvement commitments, coverage expansion metrics, incident frequency reduction targets, and risk score improvements, backed by breach warranties, performance credits, or shared-savings arrangements. Start with one outcome metric tied to a fee adjustment and expand."
        },
        {
            "header": "Build an AI efficiency-sharing pricing layer.",
            "body": "Establish transparent mechanisms (efficiency dashboards, cost-per-incident trending, AI utilization reporting) showing buyers how automation reduces delivery costs. Tie at least a portion of pricing to efficiency metrics through consumption-based components or graduated discount structures. Vendors that share the AI dividend early will secure longer contracts and higher retention."
        },
        {
            "header": "Transition from subscription-only to composable pricing architectures.",
            "body": "Decompose monolithic subscription tiers into modular components (base detection, response orchestration, threat hunting, incident retainer, outcome guarantees) that buyers assemble by risk profile. Composable vendors score 2.80 versus 2.16 for subscription-only across all pricing dimensions (30% premium), with an even wider gap on outcome-linked pricing (2.41 vs. 1.34)."
        },
        {
            "header": "Invest in AI pricing-influence capabilities as a direct commercial differentiator.",
            "body": "The 1.02-point gap between AI-mature and AI-minimal vendors is the strongest predictor of pricing model maturity. Treat AI investment as the enabler of commercial model innovation: usage-based billing from AI workload telemetry, outcome guarantees underwritten by AI-validated detection."
        },
        {
            "header": "Develop a phased roadmap from transparency to outcomes, anchored to AI maturity.",
            "body": "Most vendors cannot leap from subscription-only to full outcome-based pricing. Follow a clear sequence: (1) publish transparent pricing and tier definitions, (2) introduce usage-aligned components tied to data volume or endpoint count, (3) add composable modules, (4) introduce limited outcome commitments (e.g., MTTR guarantees with service credits), (5) implement full risk-sharing or performance-linked fees. Each stage unlocked by corresponding AI maturity."
        },
        {
            "header": "Establish competitive pricing intelligence as a standing practice.",
            "body": "With a 1.30-point spread between top-10 and market-average pricing scores and AI accelerating the divergence, vendors without structured pricing benchmarking lack visibility. Institute quarterly pricing assessments benchmarking each dimension against the market, tracking competitor evolution velocity, and identifying AI capabilities driving commercial changes in leaders."
        }
    ],
    "analysis_sections": [
        {
            "title": "What Outcome-Based Pricing Actually Means, and Why the Market Gets It Wrong",
            "body": "\"Outcome-based pricing\" has become an MDR marketing fixture. Vendors cite SLA response times or uptime guarantees as evidence of outcome alignment. This misrepresents the concept.\n\nTrue outcome-based pricing creates a direct financial link between what the buyer pays and the measurable security outcomes delivered. Commercial terms adjust based on metrics that matter: threat detection and containment speed, whether the attack surface is shrinking, incident frequency and severity trends, and cost of security per unit of business value.\n\nPractical forms include:\n\n- **Breach warranties**: Financial guarantees that pay out if a covered breach occurs, underwritten by vendor detection and response confidence.\n- **Performance-linked fee adjustments**: Pricing that flexes based on achieved MTTD/MTTR improvements against defined baselines.\n- **Risk-score-tied subscriptions**: Pricing linked to independently measured risk posture, where improvement reduces the fee.\n- **Shared savings models**: Fees tied to demonstrated cost avoidance or efficiency improvements.\n- **Incident severity caps**: Terms capping buyer financial exposure for incidents above a defined severity threshold.\n\nPRC-SUC averages just 1.63/5.0, nearly half the score of subscription transparency (3.52). The median is 1.0, meaning the typical MDR vendor has no outcome-linked mechanism. Even the top 10 on this dimension average only 3.20. The two vendors scoring above 3.0 (Accenture Security and Deloitte Cyber) are large consultancies with composable models, not pureplay MDR providers."
        },
        {
            "title": "Why Outcome-Based Pricing Adoption Lags",
            "body": "Several structural factors explain sluggish adoption despite buyer demand:\n\n**1. No measurement infrastructure.** Most MDR providers lack the telemetry, benchmarking, and reporting to measure and attribute outcomes rigorously enough for commercial commitments. Without normalized MTTD, MTTR, incident frequency, or coverage baselines, outcome commitments cannot be quantified.\n\n**2. Revenue predictability addiction.** Subscription models provide smooth, predictable revenue rewarded by investors. Outcome components introduce variability that finance teams resist. 64 of 95 vendors (67%) remain subscription-only, averaging 2.16 versus 2.80 for composable vendors.\n\n**3. Insufficient AI capability to underwrite guarantees.** A vendor cannot offer breach warranties or MTTR guarantees without AI-driven capabilities to consistently deliver. Vendors with Significant AI influence score 2.16 on PRC-SUC versus 1.04 for Minimal-tier. AI maturity is the prerequisite.\n\n**4. Misaligned organizational incentives.** Pricing decisions are often owned by finance or product management teams optimizing for margin protection, not by security operations teams that understand achievable outcomes.\n\n**5. Fear of accountability.** Outcome-linked pricing makes vendor performance transparent with real consequences. Many vendors prefer the opacity of flat-rate subscriptions where poor performance is masked.\n\n**6. Legacy contract structures.** Multi-year subscription contracts create inertia. Migration requires renegotiating hundreds of contracts, retraining sales, and rebuilding billing systems."
        },
        {
            "title": "AI Is Changing the Cost Equation, but Buyers Aren't Seeing It",
            "body": "Agentic AI is sharply reducing per-incident MDR delivery costs. Automated triage, AI-accelerated threat hunting, machine-driven response playbooks, and predictive detection enable more volume with fewer analysts. This should create a natural transition toward efficiency-sharing or outcome-aligned pricing.\n\nInstead, most vendors capture the AI efficiency dividend as margin improvement. PRC-USG averages just 2.14/5.0; most vendors have no mechanism for buyers to see or benefit from AI-driven cost reductions. The buyer pays the same subscription whether incidents are handled by a senior analyst spending hours on manual investigation or an AI agent resolving the same alert in minutes.\n\nThis will not hold. As buyers learn about AI capabilities and costs, they will demand transparency. The 19 Significant AI influence vendors (averaging 2.86 versus 1.84 for Minimal) are building this through AI workload dashboards, cost-per-incident reporting, and graduated tiers reflecting AI utilization. They are not more generous; they are more strategic. Sharing the efficiency dividend early builds competitive advantage rooted in trust and demonstrable value that subscription-only providers cannot replicate."
        },
        {
            "title": "The Composable Model Imperative",
            "body": "The data reveals a clear structural prerequisite for pricing evolution: composability. Composable-model vendors score 2.80 across all pricing dimensions versus 2.16 for subscription-only. On PRC-SUC, the gap is starker: 2.41 versus 1.34.\n\nOutcome-based pricing cannot be bolted onto a flat-rate subscription. It requires architectural flexibility to price different service layers differently: a base detection fee, a response orchestration component, an outcome guarantee overlay, a shared-savings mechanism. Each layer has distinct cost drivers, risk profiles, and measurement requirements.\n\nThe 27 composable vendors (28% of market) are positioned to add outcome-linked components over time. The 64 subscription-only vendors (67%) face a structural rebuild before outcomes can even be priced. As AI continues reshaping MDR delivery, this divide will widen into a lasting competitive gap."
        }
    ],
    "background": "The MDR market has experienced significant consolidation and commoditization pressure over the past three years. As core detection and response capabilities have become table stakes, pricing has emerged as a primary competitive battleground.\n\nThis assessment evaluated 95 MDR service providers across six pricing dimensions: subscription transparency (PRC-SUB), usage-based alignment (PRC-USG), fixed delivery pricing (PRC-FIX), success and outcome fees (PRC-SUC), composability and model maturity (PRC-COM), and pricing-to-outcomes alignment (PRC-OUT). Each scored on a 1-5 scale based on vendor documentation, public pricing information, and contracted engagement terms.\n\nThe market average of 2.35/5.0 places MDR in the \"developing\" stage. Subscription transparency leads at 3.52, reflecting basic commercial maturity in tier structures. Every other dimension falls below 3.0, with outcome dimensions (PRC-SUC at 1.63, PRC-OUT at 1.77) trailing significantly.\n\nThe AI enrichment layer reveals that 0 of 95 vendors reach the Transformative tier, 19 are Significant, 49 Emerging, and 27 Minimal. The 2.48/5.0 average AI pricing influence confirms the industry has not translated AI investment into commercial model innovation at scale.",
    "impact": "**For MDR vendors,** inability to deliver outcome-based pricing will become a serious competitive problem within two to three years. As AI-first vendors fund outcome guarantees (breach warranties, MTTR commitments, risk-score-linked pricing), providers that cannot match will compete solely on price and feature lists, a losing position in a commoditizing market. The 1.02-point gap between AI-mature and AI-minimal vendors is already visible in win rates and retention.\n\n**For buyers,** slow outcome-pricing adoption means they bear full risk of poor vendor performance. Subscription-only contracts carry no financial consequence for failed detection, slow response, or inconsistent coverage. Actively seek vendors willing to commit commercial terms to measurable outcomes; a vendor's refusal signals confidence concerns.\n\n**For the broader cybersecurity services market,** MDR pricing evolution is a leading indicator. As AI transforms cost structures across managed security services, outcome-aligned pricing pressure will extend to SOC-as-a-Service, vulnerability management, and security consulting.\n\nPlatform MDR providers (28 vendors, averaging 2.43, highest AI influence at 2.75) are best positioned to lead. Their platform investments provide outcome measurement telemetry, and their AI adoption creates the efficiency surplus for outcome guarantees. IR-enhanced providers (7 vendors, 2.64 average) have the highest pricing maturity but may be constrained by scale.\n\nPureplay providers (15 vendors, averaging 2.14, lowest AI influence at 2.13) face the greatest challenge. Without AI capability to underwrite outcome commitments or platform telemetry to measure them, they risk being squeezed between platform providers offering outcome guarantees and niche specialists offering deep expertise at premium rates.",
    "conclusion": "The MDR pricing picture shows a market in transition that has not arrived. Subscription transparency is reasonably mature, but outcome-based pricing is essentially absent. With 86% scoring 2.0 or below on PRC-SUC and a median of 1.0, the market has barely started.\n\nAI adoption is the single most predictive variable in pricing sophistication. The 1.02-point gap between AI-mature and AI-minimal vendors, and wider divergence on outcome dimensions (2.58 vs. 1.04 on PRC-OUT), make clear that AI capability enables pricing innovation. Vendors cannot credibly commit to outcome-based pricing without AI-driven detection, response, and measurement capabilities.\n\nThree parallel investments are required: AI capability maturity (to underwrite outcome guarantees), pricing architecture modernization (subscription-only to composable), and measurement infrastructure (transparent, trust-based outcome metrics). Treating pricing evolution as a finance exercise rather than capability development will leave vendors unable to compete.\n\nProduct leaders should not wait for buyer pressure. Vendors that establish outcome-linked terms while competitors remain subscription-only will set the standard and make it harder for followers to catch up. AI maturity enables pricing innovation, pricing innovation enables competitive differentiation, and differentiation determines long-term market position.",
    "glossary": buyer_gen.get("glossary", []),
    "evidence": buyer_gen.get("evidence", [])
}

# ============================================================
# CPO GENERAL CONDENSED
# ============================================================
cpo_condensed = {
    "id": "cpo-product-strategy-general-condensed",
    "label": "CPO / General (Smart Brevity)",
    "title": cpo_gen["title"],
    "summary": "Hype is pushing product teams to ship AI features that do not change what customers pay. Replacing SOAR with AI dominates the MDR space but creates an illusion of value without commercial differentiation. Product architecture, not sales strategy, is the primary barrier to pricing innovation.",
    "spa": "By 2028, fewer than 15% of MDR providers will have shipped a pricing model where AI-driven capabilities directly change what the customer pays, despite over 80% claiming AI integration. Product teams that confuse AI feature presence with AI pricing influence will lose share to vendors whose roadmaps connect AI investment to measurable commercial differentiation.",
    "findings": [
        {
            "header": "Product teams are shipping AI features that do not move the pricing needle.",
            "body": "Of 95 MDR vendors, average AI pricing influence is just 2.48/5.0, and zero reach the Transformative tier. 49 vendors (52%) sit at Emerging: AI features added to detection or triage, but no connection to pricing model changes. Product investment in AI is high; product impact on commercial models is near zero."
        },
        {
            "header": "SOAR-to-AI relabeling is the dominant product pattern, and it is not working.",
            "body": "Most product teams are replacing SOAR playbook automation with AI/ML-driven triage and response orchestration. The 49 Emerging-tier vendors (doing exactly this) average just 2.20 across pricing dimensions, barely above 1.84 for Minimal-tier vendors with no AI at all. Swapping SOAR for AI without changing the commercial model produces the same subscription pricing at the same margins."
        },
        {
            "header": "The 1.02-point gap between AI tiers is a product strategy signal.",
            "body": "Significant AI influence vendors score 2.86 across pricing dimensions versus 1.84 for Minimal. The gap exists because Significant-tier vendors built AI in ways that change what they sell: usage-based billing on AI workload volume, outcome guarantees underwritten by detection confidence, composable modules enabled by AI-driven service decomposition. Product decisions drove commercial differentiation."
        },
        {
            "header": "Outcome-based pricing (PRC-SUC at 1.63/5.0) is a product capability gap, not a sales problem.",
            "body": "Outcome-linked pricing requires product capabilities most MDR platforms lack: normalized outcome measurement, confidence-scored detection underwriting SLA commitments, and modular architecture separating base detection from outcome guarantee overlays. Until product builds these, sales has nothing to price against."
        },
        {
            "header": "Two-thirds of vendors are locked into subscription-only models because of product architecture.",
            "body": "64 of 95 vendors (67%) operate subscription-only. The root cause is monolithic architecture: a single detection-and-response pipeline delivered as a flat service. Without product-level decomposition into separately measurable, separately deliverable components, pricing teams cannot create composable or outcome-linked tiers. Composable vendors score 2.80 versus 2.16 for subscription-only."
        },
        {
            "header": "Top-10 pricing leaders all made deliberate product architecture choices enabling their commercial models.",
            "body": "Top-10 vendors average 3.65/5.0 versus the market's 2.35. Every one has (a) composable or hybrid pricing, (b) Significant or higher AI influence, (c) at least one measurable outcome metric exposed to customers. These were product decisions made 12-18 months before pricing models shipped. Product teams not making equivalent investments now will not compete on pricing in 2027-2028."
        }
    ],
    "recommendations": [
        {
            "header": "Treat AI as a pricing architecture enabler, not a feature checkbox.",
            "body": "Tie every AI investment to a specific commercial model capability it unlocks. If an AI feature does not enable a new pricing dimension (usage-based metering, outcome measurement, confidence-scored SLAs, modular service decomposition), question whether it belongs on the roadmap. The 1.02-point gap is driven by AI that changes what you sell, not AI that improves what you deliver for free."
        },
        {
            "header": "Decompose the monolithic pipeline into separately priceable service components.",
            "body": "The single biggest architecture blocker to pricing innovation is the flat, bundled MDR service. Break the pipeline into discrete, measurable components: base detection and alerting, response orchestration, proactive threat hunting, outcome guarantee overlays, efficiency reporting. Each needs its own telemetry, SLA surface, and cost model. Composable vendors outscore subscription-only by 30% across all pricing dimensions."
        },
        {
            "header": "Build outcome measurement into the product, not the dashboard.",
            "body": "PRC-SUC scores 1.63/5.0 because most products cannot measure outcomes in ways supporting commercial commitments. Ship normalized MTTD/MTTR measurement, risk posture scoring, incident frequency tracking, and coverage breadth metrics as first-class product features with APIs, not after-the-fact dashboard reports. Pricing cannot commit to outcomes the product cannot measure."
        },
        {
            "header": "Replace the SOAR-to-AI migration with an AI-to-pricing pipeline.",
            "body": "The dominant pattern (replace SOAR playbooks with AI orchestration) is a dead end for commercial differentiation. Focus next investment on connecting AI to pricing mechanics: AI workload telemetry enabling usage-based billing, detection confidence scores underwriting MTTR guarantees, efficiency metrics supporting shared-savings pricing. If the AI does not change what you charge, it only changes your cost."
        },
        {
            "header": "Set a 12-month milestone to enable at least one outcome-linked pricing component.",
            "body": "The jump from Minimal to Significant AI influence (1.84 to 2.86 on pricing dimensions) shows what is possible. Target shipping foundational capabilities for one outcome-linked tier within 12 months. Reasonable first target: an MTTR guarantee with service credits, backed by AI-driven response orchestration and normalized measurement. This single capability moves a vendor from the 86% stuck at PRC-SUC 2.0 or below into the competitive tier."
        },
        {
            "header": "Establish quarterly product-pricing alignment reviews with commercial teams.",
            "body": "The disconnect between product capability and commercial model is why pricing innovation lags. Institute a quarterly review mapping product milestones to pricing model changes they enable, feeding pricing team blockers back into the product backlog, and analyzing competitor product-pricing moves for architectural patterns to replicate or counter."
        }
    ],
    "analysis_sections": [
        {
            "title": "The SOAR-to-AI Swap: Why Product Teams Are Building the Wrong Thing",
            "body": "The dominant MDR product investment over the past 18 months: replace SOAR-based playbook automation with AI/ML-driven orchestration. Vendors rewrite triage logic to use ML classifiers, replace manual investigation with AI-assisted enrichment, and swap static playbooks with AI decision engines.\n\nThe engineering is often sound, reducing triage time, lowering false positive rates, and improving analyst efficiency. The problem: none of these improvements appear in the commercial model. The vendor still sells a flat subscription. The customer still pays per-seat or per-endpoint. AI reduces the vendor's delivery cost without changing the customer's commercial experience.\n\nThe data makes this visible: 49 Emerging-tier vendors (AI features shipped but not connected to pricing) average 2.20 across pricing dimensions. 27 Minimal-tier vendors (no meaningful AI in pricing) average 1.84. That is a 0.36-point gap for all the AI investment. The 19 Significant-tier vendors, who built AI in ways changing their commercial model, average 2.86, a full point above Emerging.\n\nShipping better AI is not enough. The AI has to change what you can sell."
        },
        {
            "title": "Product Architecture Is the Real Pricing Bottleneck",
            "body": "When product leaders ask why pricing cannot offer composable or outcome-linked models, the answer is almost always product architecture. Outcome-based pricing requires:\n\n- **Normalized outcome metrics**: MTTD, MTTR, detection coverage, incident frequency, measured per-customer with baselines, trending, and attribution. Most products measure aggregate operational metrics for internal use, not per-customer outcome metrics for commercial use.\n\n- **Modular service boundaries**: To price detection separately from response, or base service from outcome guarantees, the product must deliver these as separable components with independent SLAs and telemetry.\n\n- **Confidence scoring**: To underwrite MTTR guarantees or breach warranties, the product needs detection and response confidence expressed in a way finance teams can model.\n\n- **Usage telemetry**: Per-customer metering of AI workload volume, incident complexity, and resource consumption.\n\n64 of 95 vendors lack these capabilities. Their product delivers MDR as a monolithic pipeline: alerts in, incidents and responses out. No internal boundary exists where a pricing team could insert a usage meter, outcome metric, or component boundary. Architecture dictates subscription-only pricing.\n\nThe 27 composable-model vendors invested in decomposition. Their 30% pricing premium (2.80 vs. 2.16) comes from product giving pricing something to work with."
        },
        {
            "title": "What the Top 10 Did Differently, a Product Perspective",
            "body": "The top-10 vendors by pricing score (averaging 3.65/5.0) share common product architecture patterns that directly enabled their commercial models:\n\n**Modular telemetry from day one.** They built metering and measurement as product infrastructure, not reporting afterthoughts. Per-customer outcome tracking, AI utilization metrics, and detection confidence scoring are product features with APIs, not dashboard widgets.\n\n**Deliberate service decomposition.** They separated their pipeline into independently deliverable, independently measurable components. This was a product architecture decision, not a pricing team request.\n\n**AI capability mapped to commercial enablement.** Their AI roadmaps included specific pricing model milestones: \"this detection confidence threshold enables this SLA tier\" or \"this automation level enables this consumption-based component.\"\n\n**Outcome measurement as product truth.** They automated outcome baselining, trending, and attribution, then exposed these as customer-facing metrics. When pricing offered MTTR guarantees, the product already measured MTTR per-customer with statistical rigor.\n\nThese decisions were made 12-18 months before the pricing models shipped. Product leaders replicate this by embedding pricing-enablement milestones in product roadmaps now, not after the pricing team asks."
        },
        {
            "title": "The AI-to-Pricing Pipeline: A Product Roadmap Framework",
            "body": "Product teams need a structured framework for connecting AI capabilities to commercial model outcomes. The following progression maps product investments to the pricing capabilities they unlock:\n\n**Stage 1: AI-Enhanced Operations (current state for most).** AI improves internal efficiency (triage speed, false positive reduction, analyst productivity). Pricing impact: none. The customer sees no commercial change.\n\n**Stage 2: AI-Enabled Telemetry.** AI generates per-customer measurement infrastructure: workload volume tracking, detection confidence scoring, outcome baselining. Pricing impact: enables usage-based components and transparent efficiency reporting.\n\n**Stage 3: AI-Driven Service Decomposition.** AI capabilities mature enough to deliver separable service tiers: automated detection and alerting, AI-assisted investigation, human-validated response, proactive threat hunting. Pricing impact: enables composable pricing with independently priced modules.\n\n**Stage 4: AI-Underwritten Outcome Guarantees.** AI detection and response confidence is high enough and measurable enough to underwrite commercial commitments: MTTR guarantees, detection coverage commitments, risk score improvement targets. Pricing impact: enables outcome-linked pricing components with financial mechanisms.\n\n**Stage 5: AI-Native Commercial Model.** The full pricing model is architecturally dependent on AI capabilities: dynamic pricing based on real-time risk assessment, automated outcome measurement triggering pricing adjustments, AI-driven service optimization affecting what the customer pays. Pricing impact: transformative, creating a commercial model competitors cannot replicate without equivalent AI capability.\n\nOur data shows 0 vendors at Stage 5, 19 between Stages 2-3 (Significant tier), 49 at Stage 1 (Emerging), and 27 below Stage 1 (Minimal). The product roadmap question: what will it take to move one stage in 12 months?"
        }
    ],
    "background": "The MDR market has consolidated significantly over three years, with core detection and response capabilities becoming table stakes. Pricing has emerged as a primary competitive battleground and vendor positioning indicator.\n\nThis assessment evaluated 95 MDR providers across six pricing dimensions on a 1-5 scale. The 2.35/5.0 market average places MDR in the \"developing\" stage. Subscription transparency leads at 3.52; every other dimension falls below 3.0, with outcome dimensions (PRC-SUC at 1.63, PRC-OUT at 1.77) trailing significantly.\n\nThe AI enrichment layer: 0 of 95 vendors reach Transformative, 19 are Significant, 49 Emerging, 27 Minimal. The 2.48/5.0 average confirms the industry has not translated AI investment into commercial model innovation at scale.",
    "impact": "**For MDR vendors,** inability to deliver outcome-based pricing becomes a serious competitive problem within two to three years. As AI-first vendors fund outcome guarantees, providers that cannot match will compete solely on price and feature lists. The 1.02-point gap is already visible in win rates and retention.\n\n**For product leaders specifically,** the implication is direct: pricing innovation is blocked by product architecture, not commercial strategy. The top-10 pricing leaders built measurement infrastructure, modular service boundaries, and AI-to-pricing pipelines into their product 12-18 months before shipping competitive pricing models. Product teams that treat pricing model support as a finance or sales concern will find their commercial teams unable to compete.\n\n**For the market,** the MDR pricing evolution is a leading indicator. As AI transforms cost structures across managed security services, outcome-aligned pricing pressure will extend to SOC-as-a-Service, vulnerability management, and security consulting.\n\nPlatform providers (28 vendors, 2.43 average, highest AI influence at 2.75) are best positioned. IR-enhanced providers (7 vendors, 2.64) have the highest pricing maturity but are constrained by scale. Pureplay providers (15 vendors, 2.14, lowest AI influence at 2.13) face the greatest challenge without AI capability or platform telemetry for outcome commitments.",
    "conclusion": "MDR pricing is in transition but has not arrived. Subscription transparency is mature; outcome-based pricing is essentially absent. With 86% scoring 2.0 or below on PRC-SUC and a median of 1.0, the market has barely started.\n\nAI adoption is the single most predictive variable. The 1.02-point gap and wider divergence on outcome dimensions (2.58 vs. 1.04 on PRC-OUT) confirm that AI capability enables pricing innovation. For product leaders, the critical realization is that this is a product problem: AI maturity, modular architecture, and measurement infrastructure must be built at the product level before commercial teams can act.\n\nThree parallel product investments are required: AI capability maturity (to underwrite outcome guarantees), service architecture decomposition (from monolithic to composable), and measurement infrastructure (per-customer, API-accessible outcome metrics). Treating pricing evolution as a finance exercise rather than a product capability priority will leave vendors unable to compete.\n\nProduct leaders should act now. The 12-18 month lag between product architecture decisions and commercial model capability means investments made today determine competitiveness in 2027-2028. AI maturity enables pricing innovation, pricing innovation enables competitive differentiation, and differentiation determines market position.",
    "glossary": cpo_gen.get("glossary", []),
    "evidence": cpo_gen.get("evidence", [])
}

# ============================================================
# ADD TO JSON
# ============================================================
# Remove any existing condensed versions first
data["reports"] = [r for r in data["reports"] if r["id"] not in (
    "buyer-facing-general-condensed", "cpo-product-strategy-general-condensed"
)]

data["reports"].append(buyer_condensed)
data["reports"].append(cpo_condensed)

with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Verify
ids = [r["id"] for r in data["reports"]]
print(f"Reports: {ids}")
print(f"Total: {len(data['reports'])} reports")

# Check for em dashes
for r in data["reports"]:
    if r["id"].endswith("-condensed"):
        emdash_count = 0
        for key in ["summary", "spa", "background", "impact", "conclusion"]:
            if "\u2014" in r.get(key, ""):
                emdash_count += 1
        for f in r.get("findings", []):
            if "\u2014" in f.get("header", "") + f.get("body", ""): emdash_count += 1
        for rec in r.get("recommendations", []):
            if "\u2014" in rec.get("header", "") + rec.get("body", ""): emdash_count += 1
        for a in r.get("analysis_sections", []):
            if "\u2014" in a.get("title", "") + a.get("body", ""): emdash_count += 1
        print(f"  {r['id']}: {emdash_count} em dashes remaining")

print("Done!")
