"""Add PMR v2 analyst take: Product Team GTM Gaps for Startups."""
import json

with open("analyst_take_reports.json", "r", encoding="utf-8") as f:
    data = json.load(f)

report = {
    "id": "pmr-startup-gtm-gaps-v2",
    "schema_ref": "Product Market Readiness Schema 1_0.json",
    "label": "Analyst Take: Startup GTM Blind Spots (v2)",
    "title": "The Startup GTM Blind Spot: Where Product Teams Are Losing Ground Before the First Sales Call",
    "subtitle": "A market-level analysis of go-to-market messaging gaps among cybersecurity startups, with a focus on AI-first organizations and the structural weaknesses product teams need to address.",
    "positioning_statements": [
        {
            "id": "pmr-v2-positioning-gap",
            "label": "Product Positioning Outpaces Proof",
            "position": "Cybersecurity startups consistently invest in product positioning and differentiation messaging but fail to substantiate those claims with evidence that buyers can independently verify.",
            "positionComponents": {
                "importantIssue": "Startups are spending significant effort crafting competitive differentiation narratives and category ownership claims, yet the underlying proof, customer case studies, deployment metrics, and ROI documentation, does not keep pace.",
                "judgment": "This is not a marketing failure. It is a product team failure. The evidence required to close the gap between messaging and proof originates in product management, customer success, and engineering, not in the communications team.",
                "state": "Across the startup cohort, product positioning and differentiation shows the widest messaging-to-evidence gap of any pillar. The most inflated areas are target persona alignment, market category ownership, and competitive differentiation clarity.",
                "drama": "Startups are building cathedrals out of positioning language, but without the stone of verifiable proof, the first serious buyer inquiry brings the whole structure down."
            },
            "justification": {
                "context": "Buyers evaluating early-stage vendors have limited historical track record to rely on. Public positioning claims become a proxy for product maturity. When those claims lack substantiation, buyer confidence erodes rapidly, particularly among enterprise procurement teams accustomed to evidence-based vendor selection.",
                "evidence": "Product Positioning and Differentiation and Pricing and Commercial Model Clarity represent the widest gap areas across the startup cohort. The specific sub-dimensions driving the gap are target persona alignment, market category ownership, and competitive differentiation clarity, areas where startups invest heavily in narrative but provide limited third-party or customer-validated evidence.",
                "actionBridge": "Product teams should audit their public messaging against available supporting evidence and prioritize closing the gap in areas most visible to buyers: case study depth, deployment metrics, and commercial model transparency."
            },
            "actions": [
                {
                    "action": "Conduct a messaging-to-evidence audit for every public positioning claim. Map each claim to a verifiable proof point, and flag any claim without substantiation for immediate remediation.",
                    "whyNonObvious": "Most product teams assume that marketing owns this alignment. In practice, the evidence required, deployment data, customer outcomes, integration documentation, originates with product and engineering teams.",
                    "outcome": "A clear inventory of unsupported claims, enabling product teams to prioritize evidence generation alongside feature development."
                },
                {
                    "action": "Establish a quarterly evidence generation cadence tied to product releases. Every major release should include at least one customer case study, one deployment metric, and one third-party validation data point.",
                    "whyNonObvious": "This treats evidence as a first-class product deliverable rather than an afterthought for the marketing team to handle post-launch.",
                    "outcome": "Systematic reduction of the positioning-to-proof gap over successive release cycles."
                }
            ],
            "alignment": {
                "positionToFinding": "Directly derived from analysis of startup cohort pillar-level gaps, where PPD and PCM show the widest divergence between public messaging and substantiated evidence.",
                "actionsToRecs": "Actions map to closing the most buyer-visible gaps in the startup cohort: case studies, deployment metrics, and pricing transparency.",
                "justificationSources": "PMR schema analysis of 47 cybersecurity startups across 25 sub-dimensions."
            }
        },
        {
            "id": "pmr-v2-pricing-opacity",
            "label": "Pricing and Commercial Opacity Undermines Trust",
            "position": "Startups that are not AI-first have a pronounced blind spot around pricing and commercial model transparency, creating friction at the exact moment in the buyer journey where trust matters most.",
            "positionComponents": {
                "importantIssue": "Commercial model clarity, spanning pricing transparency, packaging, total cost of ownership, trial accessibility, and contract flexibility, represents the weakest proof area for startups overall. Non-AI-first startups show nearly double the gap of their AI-first peers across every pricing sub-dimension.",
                "judgment": "This reflects a fundamental product strategy choice. AI-first startups, many of which are platform-native and born in the cloud, have been forced by market dynamics to lead with transparent, self-service pricing models. Non-AI-first startups, often rooted in traditional enterprise sales motions, default to opaque, custom-quote models that create buyer friction.",
                "state": "Trial and evaluation accessibility and commercial terms flexibility are the widest individual sub-dimension gaps for non-AI-first startups. These are the areas where buyers form their first commercial impression of the vendor.",
                "drama": "Hiding your pricing does not make you look premium. It makes you look like you have something to hide."
            },
            "justification": {
                "context": "Enterprise buyers increasingly expect self-service evaluation and transparent pricing as a baseline, not a differentiator. The broader SaaS market has normalized free trials, public pricing pages, and clear tier structures. Cybersecurity startups that deviate from this expectation face higher-friction sales cycles and lower win rates.",
                "evidence": "Non-AI-first startups show roughly double the messaging-to-evidence gap in pricing model transparency, packaging and tier clarity, total cost of ownership, trial accessibility, and contract flexibility compared to AI-first startups. This is the single largest structural divergence between the two startup cohorts.",
                "actionBridge": "Product teams should treat commercial model transparency as a competitive weapon, not a concession. Leading with clear pricing reduces sales cycle friction and signals confidence in the product."
            },
            "actions": [
                {
                    "action": "Publish a public pricing page with at least tier-level guidance, even if enterprise deals require custom quotes. Include a self-service trial or sandbox environment.",
                    "whyNonObvious": "Many startups fear that public pricing will constrain deal flexibility. In practice, it establishes a baseline that accelerates initial buyer engagement and reduces time-to-qualified-opportunity.",
                    "outcome": "Reduced buyer friction and faster pipeline velocity for inbound leads."
                },
                {
                    "action": "Document total cost of ownership for a representative deployment scenario, including implementation, integration, and ongoing operational costs.",
                    "whyNonObvious": "Most startups only communicate license cost. Buyers evaluating risk need the full picture, and the absence of TCO documentation is interpreted as either inexperience or deliberate obfuscation.",
                    "outcome": "Stronger procurement alignment and fewer late-stage deal objections related to hidden costs."
                },
                {
                    "action": "Benchmark your commercial model transparency against AI-first peers in adjacent categories. Identify where you fall behind and close the gap systematically.",
                    "whyNonObvious": "AI-first startups have set a new buyer expectation for commercial transparency. Startups in adjacent categories that do not meet this bar are competing against a standard they may not even be aware of.",
                    "outcome": "Commercial model that meets or exceeds the buyer expectation established by the most transparent competitors."
                }
            ],
            "alignment": {
                "positionToFinding": "Derived from per-sub-pillar comparison of AI-first vs. non-AI-first startup cohorts across all five PCM sub-dimensions.",
                "actionsToRecs": "Actions target the three highest-gap sub-dimensions: trial accessibility, packaging clarity, and TCO documentation.",
                "justificationSources": "PMR schema analysis comparing 20 AI-first startups with 27 non-AI-first startups across 25 sub-dimensions."
            }
        },
        {
            "id": "pmr-v2-ai-first-category",
            "label": "AI-First Startups Overinvest in Category Ownership",
            "position": "AI-first cybersecurity startups demonstrate a distinctive pattern: strong technical depth and pricing transparency, but a tendency to overinvest in market category ownership and messaging consistency claims that outpace their ability to prove them.",
            "positionComponents": {
                "importantIssue": "AI-first startups show their widest positioning gaps in market category ownership and messaging consistency, areas where the temptation to stake a category-defining claim is strongest, and where the evidence bar is highest.",
                "judgment": "This is the specific trap of the AI-first narrative. When the product itself is built on novel technology, the instinct is to claim a new category. However, claiming to define a category requires a level of third-party validation, customer breadth, and market education that most early-stage organizations have not yet accumulated.",
                "state": "AI-first startups outperform their non-AI peers in technical depth, API ecosystem depth, and pricing transparency. Their weaknesses cluster in customer reference breadth, deployment scale documentation, and the category ownership claims themselves.",
                "drama": "Declaring yourself the category leader in a category nobody else recognizes is not positioning. It is aspiration disguised as strategy."
            },
            "justification": {
                "context": "The cybersecurity startup landscape, particularly in AI-adjacent categories, is dense with organizations claiming to define new market segments. Buyers and analysts have developed skepticism toward unsubstantiated category-creation narratives. Startups that invest in building verifiable evidence of customer adoption and deployment scale before making category claims earn more durable market positions.",
                "evidence": "Market category ownership and messaging consistency represent the widest individual sub-dimension gaps for AI-first startups. Their technical depth gaps are among the narrowest in the entire startup cohort, indicating that the technical product is often more mature than the go-to-market positioning supporting it.",
                "actionBridge": "Product teams at AI-first organizations should redirect a portion of their positioning investment from category-defining narratives toward building the evidence base, customer references, deployment case studies, and analyst validation, that makes those category claims credible."
            },
            "actions": [
                {
                    "action": "Defer category-defining claims until you can substantiate them with at least three named customer references, one analyst validation, and one quantified deployment metric.",
                    "whyNonObvious": "The instinct in AI-first organizations is to lead with vision. But premature category claims without proof create a positioning debt that compounds over time and erodes credibility with sophisticated buyers.",
                    "outcome": "Positioning claims arrive with built-in credibility, reducing the burden on sales to overcome skepticism."
                },
                {
                    "action": "Invest in conference presence and original research publication to build the market education foundation that supports category claims over time.",
                    "whyNonObvious": "Category ownership is earned through market education, not declared through positioning documents. Speaking slots, white papers, and original data build the intellectual authority that makes category claims stick.",
                    "outcome": "A durable foundation of thought leadership that supports, rather than precedes, category positioning."
                }
            ],
            "alignment": {
                "positionToFinding": "Derived from AI-first startup sub-pillar analysis where PPD-04 (Market Category Ownership) and PPD-05 (Messaging Consistency) show the widest gaps, contrasted with TDT sub-pillars showing among the narrowest.",
                "actionsToRecs": "Actions directly address the gap between technical maturity and positioning maturity in AI-first startups.",
                "justificationSources": "PMR schema analysis of 20 AI-first cybersecurity startups across 25 sub-dimensions."
            }
        },
        {
            "id": "pmr-v2-technical-strength",
            "label": "Technical Depth Is the Startup Advantage; Leverage It",
            "position": "Technical depth and transparency is the one area where cybersecurity startups most closely align their messaging with evidence, and product teams should recognize this as their strongest competitive foundation for buyer conversations.",
            "positionComponents": {
                "importantIssue": "Technical depth consistently shows the narrowest gap between what startups claim and what they can prove, particularly in detection methodology transparency, documentation quality, and architecture design. This is the pillar where startups are most credible.",
                "judgment": "Product teams often undervalue their technical depth in go-to-market conversations, defaulting to positioning and differentiation narratives. The data indicates that technical transparency is the area where startups have the most defensible story, and should be leading with it.",
                "state": "Detection methodology transparency, technical enablement documentation, and architecture design documentation are the three sub-dimensions with the narrowest messaging-to-evidence gap across the startup cohort. Open-source and community contribution also shows strong alignment.",
                "drama": "Your best story is the one you are not telling loudly enough."
            },
            "justification": {
                "context": "Enterprise buyers evaluating startups often compensate for the lack of brand recognition by going deep on technical diligence. Startups that lead with technical transparency reduce the perceived risk of early-stage vendor selection and differentiate from established vendors who often obscure technical details behind enterprise sales processes.",
                "evidence": "Technical Depth and Transparency shows the narrowest pillar-level gap for startups overall. The strongest alignment sits in detection methodology transparency, documentation quality, and architecture design. AI-first startups show even tighter alignment in this pillar, with average gaps roughly half of their positioning pillar gaps.",
                "actionBridge": "Product teams should ensure that technical depth, not just positioning narratives, is prominently featured in all buyer-facing materials, analyst briefings, and sales enablement content."
            },
            "actions": [
                {
                    "action": "Lead analyst briefings, sales decks, and buyer presentations with technical architecture and methodology content before positioning and differentiation narratives.",
                    "whyNonObvious": "Conventional sales practice leads with positioning. For startups where positioning claims outpace proof, leading with the strongest evidence area, technical depth, builds credibility before the positioning conversation begins.",
                    "outcome": "Higher buyer confidence in initial engagements, reducing the credibility burden on subsequent positioning claims."
                },
                {
                    "action": "Publish comprehensive API documentation, architecture diagrams, and integration guides as public-facing assets, not gated content.",
                    "whyNonObvious": "Technical transparency signals confidence. Gating technical documentation behind sales conversations signals that the product may not withstand scrutiny before a relationship is established.",
                    "outcome": "Increased inbound technical evaluation and reduced time-to-technical-validation for prospective buyers."
                }
            ],
            "alignment": {
                "positionToFinding": "Derived from TDT pillar showing the narrowest startup gap and the smallest individual sub-dimension gaps across the 25-dimension framework.",
                "actionsToRecs": "Actions target leveraging the existing strength rather than remediating a weakness.",
                "justificationSources": "PMR schema analysis of 47 cybersecurity startups and 20 AI-first startups across 25 sub-dimensions."
            }
        }
    ],
    "body_sections": [
        {
            "heading": "What We Looked At and Why Product Teams Should Care",
            "body": "This analysis examines the go-to-market readiness of 47 cybersecurity startups across 25 dimensions of product market positioning, spanning product differentiation, proof points, technical depth, pricing clarity, and thought leadership. For each dimension, we evaluated what startups claim in their public-facing messaging and what evidence exists to substantiate those claims. The resulting gap between messaging and proof is the core metric driving this analysis.\n\nProduct teams should care because the gap is not a marketing problem. The evidence required to close it, customer case studies, deployment metrics, ROI documentation, architectural transparency, and pricing clarity, originates in product management, engineering, and customer success. When the gap is wide, it signals that the product organization has not built the infrastructure to support the claims the go-to-market function is making. That disconnect is visible to every enterprise buyer running a structured evaluation."
        },
        {
            "heading": "The Positioning Trap: Startups Are Loud Where They Are Weakest",
            "body": "Product positioning and differentiation is the pillar where startups invest the most messaging energy and have the least evidence to back it up. The pattern is consistent: startups craft detailed narratives around competitive differentiation, target persona alignment, and market category ownership, but the underlying proof, named customer deployments, quantified outcomes, and third-party validation, does not match the volume of the claims.\n\nPricing and commercial model clarity tells a similar story. Startups message confidently about packaging, trials, and commercial flexibility, but the evidence trail is thin. Trial accessibility and contract flexibility are the sub-dimensions where messaging most outpaces reality. Non-AI-first startups are particularly exposed here, with roughly double the gap of AI-first peers across every pricing sub-dimension. AI-first organizations, built on cloud-native, self-service architectures, have been forced by market dynamics to lead with transparent commercial models. Traditional cybersecurity startups have not yet caught up.\n\nThe under-marketed strength, by contrast, is technical depth. Detection methodology transparency, architecture documentation, and API ecosystem depth show the tightest alignment between messaging and evidence. This is the pillar where startups are most credible and where they should be leading their buyer conversations."
        },
        {
            "heading": "The AI-First Pattern: Strong Under the Hood, Weak at the Podium",
            "body": "AI-first startups, roughly 40% of the startup cohort, present a distinctive profile. Their technical depth is strong and well-substantiated. Their pricing models are more transparent than their non-AI peers. But their positioning tells a different story.\n\nMarket category ownership is the widest individual gap for AI-first startups. These organizations, often built on novel technologies, have a natural instinct to claim new categories. The evidence base, customer references, analyst validation, deployment breadth, has not caught up to the ambition. Messaging consistency follows the same pattern: the narrative is polished and coherent, but the proof points supporting it are unevenly distributed across channels and contexts.\n\nCustomer reference breadth and deployment scale documentation are the companion weaknesses. AI-first startups tend to have deep but narrow proof: a handful of impressive deployments rather than broad-based adoption evidence. This creates risk in enterprise evaluations where buyers expect evidence of adoption across industries, geographies, and organization sizes.\n\nThe implication for product teams is clear. The technical product may be mature, but the go-to-market evidence infrastructure is not. Building that infrastructure, customer case studies, named references, quantified deployment metrics, analyst recognition, is product work, not marketing work."
        },
        {
            "heading": "Where Buyers See the Gaps Before You Do",
            "body": "Enterprise buyers running structured evaluations will surface these gaps systematically. A procurement team evaluating five startups side by side will quickly identify which organizations can substantiate their claims and which cannot. The most common failure mode is not that the product is inadequate, but that the evidence is missing, incomplete, or not organized for buyer consumption.\n\nThree areas surface most frequently in buyer due diligence. First, case study depth: buyers look for named customers with quantified outcomes in their industry and at their scale. Startups that offer generic testimonials instead of detailed case studies lose credibility at the first gate. Second, deployment metrics: uptime, events processed, customer count, and geographic coverage are table stakes in enterprise evaluation. Startups that cannot provide these figures are competing with one hand tied behind their back. Third, commercial model transparency: buyers expect to understand pricing, packaging, and total cost of ownership before engaging in a sales conversation. Startups that gate this information behind qualification calls create friction that slows pipeline and undermines buyer confidence.\n\nProduct teams that build evidence generation into their release cadence, treating case studies, metrics, and pricing documentation as first-class deliverables alongside feature releases, will close these gaps naturally over time."
        },
        {
            "heading": "What Product Teams Should Focus On Now",
            "body": "The data points to three priorities for cybersecurity startup product teams. First, close the proof gap in your strongest messaging areas. If your positioning narrative centers on differentiation and category ownership, ensure every claim maps to a verifiable proof point. Audit your public-facing content and flag any assertion that lacks supporting evidence.\n\nSecond, treat commercial model transparency as a product decision, not a sales decision. The divergence between AI-first and non-AI-first startups on pricing transparency is the single largest structural gap in the data. If your competitors are publishing pricing pages, offering free trials, and documenting total cost of ownership, and you are not, you are creating friction that your product cannot overcome.\n\nThird, lead with your technical depth. This is the area where startups are most credible and where the evidence most closely matches the messaging. Product teams that lead buyer conversations, analyst briefings, and sales enablement with technical architecture, methodology transparency, and API documentation build credibility before the positioning conversation begins.\n\nThe broader pattern is clear: the startup go-to-market gap is not a marketing problem. It is a product team problem. The evidence that buyers need originates in product management, engineering, and customer success. Until product teams own the evidence generation process as a core deliverable, the gap between what startups say and what they can prove will persist."
        }
    ],
    "recommended_reading": [
        {
            "title": "Market Guide for Cybersecurity Product Market Readiness",
            "id": "pmr-market-guide-2025",
            "relevance": "Comprehensive framework for evaluating vendor go-to-market maturity across all 25 sub-dimensions."
        },
        {
            "title": "How to Evaluate Startup Vendors for Enterprise Cybersecurity",
            "id": "startup-eval-guide-2025",
            "relevance": "Buyer-focused guidance on assessing early-stage vendor evidence and commercial maturity."
        },
        {
            "title": "Competitive Landscape: AI-First Cybersecurity Platforms",
            "id": "ai-first-landscape-2025",
            "relevance": "Market context for how AI-first organizations are reshaping buyer expectations around transparency and self-service."
        },
        {
            "title": "Predicts 2026: Cybersecurity Startups and Market Consolidation",
            "id": "predicts-2026-startups",
            "relevance": "Forward-looking analysis of startup survival patterns and the role of go-to-market maturity in acquisition decisions."
        }
    ],
    "notes": "Analysis based on Product Market Readiness Schema 1.0 evaluation of 195 cybersecurity vendors, of which 47 are classified as startups. 20 of 47 startups are classified as AI-first. Data vintage: Q1 2025 public-facing content. No vendor names are cited in this report. All findings are presented at cohort and market level. Pillar-level and sub-pillar-level patterns described in this report reflect directional trends across the startup cohort and are not intended as assessments of individual vendors.",
    "guidance": {
        "tonality": "Direct, evidence-informed, product-team-focused. Written for product leaders, not buyers. Avoids score-specific language; uses directional descriptions (widest gap, narrowest alignment, strongest area). No vendor names.",
        "audiencePrimary": "VP Product, Head of Product Marketing, Chief Product Officer at cybersecurity startups",
        "audienceSecondary": "Startup CEOs, CMOs, VCs evaluating portfolio companies, cybersecurity product strategy consultants",
        "keyTerms": [
            "go-to-market gap",
            "messaging-to-evidence alignment",
            "product positioning",
            "commercial model transparency",
            "technical depth",
            "proof infrastructure",
            "AI-first",
            "category ownership",
            "evidence generation cadence",
            "buyer evaluation"
        ]
    },
    "graphics": [
        {
            "id": "startup-pillar-gap-profile",
            "type": "comparison",
            "title": "Startup Go-to-Market Gap by Pillar",
            "caption": "Relative messaging-to-evidence gap across five product market readiness pillars for the startup cohort. Product Positioning and Pricing show the widest gaps; Technical Depth shows the narrowest.",
            "purpose": "Visualize where startup product teams are most exposed and most credible, directing attention to the highest-priority remediation areas.",
            "takeaway": "Startups are loudest where they are weakest and quietest where they are strongest.",
            "svg": ""
        },
        {
            "id": "ai-first-vs-non-ai-comparison",
            "type": "comparison",
            "title": "AI-First vs. Non-AI-First Startup Gap Comparison",
            "caption": "Pillar-level gap comparison between AI-first and non-AI-first startup cohorts. Non-AI-first startups show markedly wider gaps in Pricing and Commercial Model Clarity.",
            "purpose": "Illustrate the structural divergence in commercial transparency between AI-first and traditional cybersecurity startups.",
            "takeaway": "AI-first startups have set a new baseline for commercial transparency that non-AI-first startups have not matched.",
            "svg": ""
        }
    ]
}

data["reports"].append(report)

with open("analyst_take_reports.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=6, ensure_ascii=False)

# Word count
total = 0
for sec in report["body_sections"]:
    wc = len(sec["body"].split())
    total += wc
    print(f"  {sec['heading']}: {wc} words")
print(f"\nTotal body: {total} words")
print(f"Positioning statements: {len(report['positioning_statements'])}")
print(f"Report added as #{len(data['reports'])}: {report['id']}")
