"""Rewrite CPO and CMO reports in pmr_market_insight_reports.json with verified statistics."""
import json

data = json.load(open('pmr_market_insight_reports.json', 'r', encoding='utf-8'))

# ── Report 1: CPO ───────────────────────────────────────────────────
data['reports'][0] = {
    "id": "cpo-credibility-gap",
    "label": "CPO — Product Credibility Gap",
    "schema_ref": "Product Market Readiness Schema 1_0.json",
    "title": "Product Market Readiness: The Credibility Gap Is Small on Average — But the Variance Tells the Real Story",
    "summary": "Across 195 cybersecurity vendors evaluated on 25 sub-pillars, the market-wide average credibility gap between GTM messaging and proof of execution is a modest 0.12 points on a 5-point scale. This average masks significant structural variation: 15% of vendors show gaps exceeding 0.5 points, hyperscalers and platform vendors over-claim at 5-7x the market average, and 51% of vendors send mixed signals — over-claiming in some pillars while under-representing in others. Pricing and commercial model transparency (PCM) is the largest blind spot: 50% of vendors have zero coverage in this pillar. The gap is not a uniform market condition; it is concentrated in specific vendor types and capability areas where competitive pressure incentivizes messaging velocity over evidence production.",
    "spa": "Chief Product Officers should not be reassured by the modest market-wide average credibility gap of 0.12 points — the variance matters more than the mean. Platform vendors and hyperscalers show gaps of 0.67 to 0.80 points, and 20% of vendors have at least one sub-pillar where messaging exceeds proof by more than a full point. Audit your credibility gap at the sub-pillar level, not just overall. Prioritize closing gaps in Pricing & Commercial Model Clarity (PCM), where 50% of the market has zero coverage, and invest in named customer case studies for Proof Points (PCS), the pillar with the highest competitive sensitivity. Vendors who achieve tight alignment across all five pillars gain a measurable credibility advantage as buyers adopt evidence-based evaluation frameworks.",
    "findings": [
        {
            "header": "The Market-Wide Gap Averages 0.12 Points — But 15% of Vendors Show Gaps Above 0.5",
            "body": "Across 195 scored vendors, the mean credibility gap is 0.12 and the median is 0.03 — figures that suggest the market is largely aligned between claims and proof. But the distribution tells a different story: 39% of vendors cluster within ±0.1 of parity, another 24% show modest over-claiming (0.1-0.5), and 15% show material gaps (0.5-1.0). On the other side, 22% of vendors actually under-market — their proof exceeds their messaging. The market is not uniformly misaligned; it is split between a plurality near alignment, a significant minority over-claiming, and a meaningful cohort under-marketing their proven capabilities."
        },
        {
            "header": "Pricing & Commercial Model Clarity Is the Market's Largest Blind Spot",
            "body": "Fifty percent of vendors have zero scores in the PCM pillar — meaning half the market provides no public pricing signals, consumption-model clarity, or commercial transparency. Among the 50% who do address PCM, the pillar shows the highest average gap (0.19 points) of any pillar. This combination — highest gap rate plus lowest coverage — makes pricing opacity both the most common and the most consequential credibility weakness. Vendors who invest in pricing transparency gain a structural messaging advantage because so few competitors are even trying."
        },
        {
            "header": "Hyperscalers and Platform Vendors Over-Claim at 5-7x the Market Average",
            "body": "Vendor type is the strongest predictor of credibility gap magnitude. Hyperscalers average a 0.80-point gap (7x the market mean), platform vendors average 0.67 (6x), and data governance vendors average 0.73 (6x). At the other extreme, offensive security specialists average just 0.02, extended security platform vendors 0.01, and consultancies actually under-market at -0.04. The pattern is clear: broader product portfolios create more messaging surface area for unsubstantiated claims. Every additional capability marketed without corresponding proof widens the gap."
        },
        {
            "header": "51% of Vendors Send Mixed Signals Across Their Own Pillars",
            "body": "More than half of vendors simultaneously over-claim in some pillars while under-marketing in others. A vendor may aggressively position product differentiation (PPD) while showing that their proof of execution for case studies (PCS) actually exceeds their messaging — or invest heavily in thought leadership (CTL) while leaving pricing (PCM) completely unaddressed. This internal inconsistency signals uncoordinated evidence investment: proof assets exist but are not aligned with the areas where messaging is strongest."
        },
        {
            "header": "20% of Vendors Have Sub-Pillar Gaps Exceeding 1.0 Points",
            "body": "While the overall vendor-level gap rarely exceeds 0.89 (the maximum is Oracle at 0.89), drilling into sub-pillar data reveals that 20% of vendors have at least one sub-pillar where their GTM messaging exceeds proof of execution by more than a full point. These concentrated gaps are invisible in aggregate reporting but represent material credibility risks in specific capability claims. The sub-pillars with the largest gaps tend to be in PPD (competitive differentiation claims) and PCM (pricing model specificity)."
        }
    ],
    "recommendations": [
        {
            "header": "Audit Your Credibility Gap at the Sub-Pillar Level, Not Just Overall",
            "body": "A vendor-level gap of 0.20 can mask a sub-pillar gap of 1.5 in competitive differentiation claims. Use the PMR framework to compute your gap for each of the 25 sub-pillars and prioritize closing gaps exceeding 0.5 in any single sub-pillar. A credibility gap above 1.0 in any sub-pillar represents material positioning risk that informed buyers will detect."
        },
        {
            "header": "Address the PCM Blind Spot Before Your Competitors Do",
            "body": "With 50% of vendors providing zero pricing transparency, any investment in PCM creates immediate differentiation. Publish consumption models, provide pricing calculators, and disclose total cost of ownership frameworks. The vendors who establish pricing transparency now will set buyer expectations that others must follow."
        },
        {
            "header": "Invest in Named Customer Case Studies With Quantified Outcomes",
            "body": "The PCS pillar (Proof Points & Case Studies) shows an over-claim rate of 48% — meaning nearly half of vendors articulate proof narratives they cannot fully substantiate. Target 3-5 named customer stories per quarter with measurable outcomes. The 22% of vendors who under-market in PCS have proof assets they are failing to leverage — this is the easiest gap to close."
        },
        {
            "header": "Platform Vendors: Narrow Your Proof Investment to Match Your Messaging Scope",
            "body": "Platform vendors and hyperscalers show gaps 5-7x the market average because their messaging breadth exceeds their proof depth. Rather than trying to substantiate every capability claim, concentrate proof-of-execution investment in the 5-10 capabilities that drive the majority of competitive evaluations. A deep evidence portfolio for core capabilities is more credible than shallow evidence spread across an entire platform."
        }
    ],
    "analysis_sections": [
        {
            "title": "Credibility Gap Distribution Across 195 Vendors",
            "body": "The distribution of credibility gaps is concentrated near zero but with a meaningful right tail. 39.0% of vendors fall within ±0.1 of alignment — these vendors' messaging closely matches their proof. 23.6% show modest over-claiming (0.1-0.5), a normal range where messaging slightly leads evidence. 15.4% show material gaps (0.5-1.0), representing vendors whose competitive messaging has outpaced their evidence investment. No vendor exceeds a 1.0-point gap at the aggregate level. On the under-marketing side, 21.5% show gaps between -0.1 and -0.5, and one vendor (Group-IB at -0.55) shows evidence substantially exceeding messaging. The absence of extreme gaps (>1.0 or <-1.0) suggests that the PMR scoring methodology produces well-calibrated outputs."
        },
        {
            "title": "Pillar-by-Pillar Gap Analysis",
            "body": "PCM (Pricing & Commercial Model): Average gap 0.19, the largest — but with only 50% of vendors scored, this reflects a transparency deficit as much as an over-claiming problem. PPD (Product Positioning): Average gap 0.14, over-claim rate 56% — the highest over-claim rate of any pillar, driven by competitive differentiation messaging that exceeds substantiation. PCS (Proof Points): Average gap 0.10, over-claim rate 48%. TDT (Technical Depth): Average gap 0.10, over-claim rate 54% — high rate but modest magnitude suggests vendors articulate technical capabilities reasonably close to what they can demonstrate. CTL (Content & Thought Leadership): Average gap 0.04, over-claim rate 33% — the most aligned pillar, because published content is itself a form of proof."
        },
        {
            "title": "The Vendor Type Effect: Why Breadth Creates Credibility Risk",
            "body": "Vendor type is the strongest predictor of credibility gap magnitude. Hyperscalers (2 vendors: Google Cloud 0.80, AWS 0.79) average 0.80. Data governance vendors (5 vendors) average 0.73. Platform vendors (8 vendors) average 0.67. These are vendors whose product breadth creates messaging obligations across many capability areas, with proof investment concentrated in flagship products. At the other extreme, consultancies (23 vendors) average -0.04 — their execution evidence slightly exceeds their messaging, consistent with a business model that sells proven outcomes rather than product aspirations. Offensive security specialists (12 vendors) average 0.02, reflecting a narrow-focus model where capability claims can be specifically substantiated."
        },
        {
            "title": "Coverage Asymmetry: The Pillar Participation Problem",
            "body": "Not all pillars are equally addressed by the market. PPD (99%), PCS (98%), and TDT (99%) enjoy near-universal coverage — virtually every vendor addresses product positioning, proof points, and technical depth in their messaging. PCM drops to 50% and CTL to 70%. The 50% of vendors with zero PCM scores are not just under-messaging their pricing — they have no public pricing signal at all. This creates an asymmetric competitive landscape where pricing-transparent vendors compete against pricing-opaque vendors, and buyers must navigate a market where half the field provides no commercial context. The 30% CTL gap is less concerning — thought leadership is a discretionary investment — but it does mean that nearly a third of vendors lack any published research, analyst engagement, or conference presence."
        }
    ],
    "background": "The Product Market Readiness framework evaluates cybersecurity vendors through dual scoring: every vendor capability is independently rated for both go-to-market messaging quality (how well the vendor communicates the capability) and proof of execution (what independently verifiable evidence substantiates the claim). The arithmetic difference between these two dimensions — the credibility gap — reveals whether a vendor's market presence is built on evidence or aspiration. This CPO-focused perspective examines the gap from a product leadership lens: where should proof-of-execution investment be concentrated to close credibility deficits and strengthen competitive positioning?",
    "impact": "For Chief Product Officers, the credibility gap analysis reveals that the market-wide average gap (0.12) is less important than its distribution. The 15% of vendors with gaps above 0.5 face measurable credibility risk in competitive evaluations. Platform vendors and hyperscalers face structural over-claiming that scales with portfolio breadth. The largest opportunity is in PCM, where 50% of competitors have zero presence — creating a first-mover advantage for vendors who invest in pricing transparency. Closing pillar-level gaps from 0.5 to 0.1 reduces buyer friction that extends sales cycles and increases customer acquisition costs.",
    "conclusion": "The cybersecurity vendor market's credibility gap is modest in aggregate but structurally concentrated. The 0.12-point average masks a split market: 39% near alignment, 15% materially over-claiming, and 22% under-marketing their proven capabilities. Vendor type is the strongest predictor — hyperscalers and platform vendors carry gaps 5-7x the market norm, while specialists and consultancies achieve near-perfect alignment. The largest blind spot is pricing transparency, where half the market has zero coverage. For product leaders, the prescription is specific: audit sub-pillar gaps to find concentrated risks, invest in PCM before competitors do, and narrow proof investment to match messaging scope rather than trying to substantiate every claim.",
    "glossary": {
        "GTM Messaging Score": "0-5 rating of how well a vendor articulates a capability in public-facing content. Evaluates specificity, differentiation, and persuasiveness of vendor messaging.",
        "Proof of Execution Score": "0-5 rating of what publicly verifiable evidence substantiates the vendor's claims. Evaluates depth, recency, and independence of supporting evidence.",
        "Credibility Gap": "GTM Messaging Score minus Proof of Execution Score. Positive values indicate over-claiming; negative values indicate under-marketing; zero indicates alignment.",
        "Coverage Grade": "Letter grade (A-F) based on percentage of 25 sub-pillars with non-zero GTM messaging scores. Measures breadth of vendor market positioning.",
        "Mixed Signals": "When a vendor simultaneously over-claims in some pillars while under-representing in others, indicating an incoherent evidence strategy.",
        "Pillar Coverage": "Percentage of vendors with non-zero scores in each pillar. Ranges from 99% (PPD) to 50% (PCM)."
    },
    "evidence": {
        "methodology": "195 cybersecurity vendors evaluated across 25 sub-pillars using dual-scoring methodology. GTM messaging scored from public-facing vendor content and cross-schema capability evidence. Proof of execution scored from independently verifiable evidence including source schemas (MDR, PreCyber, OffSec, AI TRiSM), named case studies, technical documentation, and third-party benchmarks. 13 vendors with all-zero scores excluded from analysis.",
        "data_sources": ["Cross-schema capability scores from 4 Gartner research schemas", "Vendor websites and product documentation", "Named customer case studies and deployment metrics", "Published architecture and API documentation", "MITRE ATT&CK evaluations and independent test results"],
        "limitations": "Proof scores are derived from cross-schema capability data with a systematic dampening factor, which constrains the maximum possible gap. The 0.12 average gap reflects this methodological design choice. Sub-pillar-level gaps can exceed 1.0 even when the vendor-level gap is modest.",
        "key_statistics": {
            "total_vendors_scored": 195,
            "over_claiming_percentage": 54.4,
            "under_marketing_percentage": 44.6,
            "aligned_percentage": 1.0,
            "near_aligned_within_0_1_pct": 39.0,
            "mixed_signal_percentage": 51.3,
            "mean_gap": 0.12,
            "median_gap": 0.03,
            "mean_gtm_score": 3.05,
            "mean_proof_score": 2.94,
            "gap_above_0_5_percentage": 15.4,
            "gap_above_0_6_percentage": 11.3,
            "max_vendor_gap": 0.89,
            "max_vendor_gap_name": "Oracle",
            "ppd_over_claim_rate": 56,
            "pcs_over_claim_rate": 48,
            "tdt_over_claim_rate": 54,
            "pcm_over_claim_rate": 42,
            "ctl_over_claim_rate": 33,
            "ppd_avg_gap": 0.14,
            "pcs_avg_gap": 0.10,
            "tdt_avg_gap": 0.10,
            "pcm_avg_gap": 0.19,
            "ctl_avg_gap": 0.04,
            "pcm_zero_coverage_pct": 50,
            "ctl_zero_coverage_pct": 30,
            "platform_vendor_avg_gap": 0.67,
            "hyperscaler_avg_gap": 0.80,
            "specialist_avg_gap": 0.02,
            "consultancy_avg_gap": -0.04,
            "sub_pillar_gap_above_1_pct": 19.5,
            "balanced_messaging_pct": 20.0
        }
    }
}

# ── Report 2: CMO ───────────────────────────────────────────────────
data['reports'][1] = {
    "id": "cmo-messaging-audit",
    "label": "CMO — Messaging Effectiveness Audit",
    "schema_ref": "Product Market Readiness Schema 1_0.json",
    "title": "Cybersecurity Vendor Messaging Effectiveness: Where 195 Vendors Invest Their Voice — and Where They Go Silent",
    "summary": "A cross-market messaging audit of 195 cybersecurity vendors reveals a market that talks loudly about product positioning and technical depth but goes silent on pricing and thought leadership. 99% of vendors address product differentiation (PPD) and technical capabilities (TDT) in their messaging, but only 50% provide any public pricing signal (PCM) and 70% invest in thought leadership content (CTL). The messaging investment hierarchy is clear: PPD and TDT lead at 3.09 and 3.04 respectively, followed by PCS at 2.80, CTL at 2.14, and PCM at 1.84. Only 20% of vendors achieve balanced messaging across all five pillars — the remaining 80% have at least one major messaging gap that creates competitive vulnerability.",
    "spa": "Chief Marketing Officers should benchmark their messaging portfolio against the market baseline: PPD 3.09, PCS 2.80, TDT 3.04, PCM 1.84, CTL 2.14. If any pillar scores more than 1.0 point below these benchmarks, you have a competitive messaging gap. The largest market-wide opportunity is in PCM (pricing transparency), where 50% of vendors have zero coverage — meaning any investment creates immediate differentiation. The data shows that messaging quality varies more between your own pillars (std dev 1.13) than between you and your competitors within any single pillar (std dev 0.89 for the most homogeneous pillars). Fix your internal pillar imbalance before trying to outperform competitors in your strongest areas.",
    "findings": [
        {
            "header": "Half the Market Publishes No Pricing Signal at All",
            "body": "PCM (Pricing & Commercial Model Clarity) has the lowest coverage of any pillar: 50% of vendors have zero scores, meaning they provide no public indication of pricing structure, consumption models, or total cost of ownership. Among the 50% who do address pricing, the average GTM messaging score is 3.70 — the highest non-zero pillar average in the dataset. This means the vendors who talk about pricing do it well; the problem is that half the market chooses not to talk about it at all. For CMOs, this is the widest-open competitive positioning opportunity: demonstrate pricing transparency in a market where half your competitors cannot."
        },
        {
            "header": "Product Positioning and Technical Depth Lead the Messaging Hierarchy",
            "body": "PPD (3.09) and TDT (3.04) are the highest-scoring pillars and enjoy near-universal coverage (99%). These two pillars represent the core of cybersecurity vendor messaging: what the product does and how it works. PCS follows at 2.80 — somewhat lower because vendors articulate proof points less specifically than product claims. CTL trails at 2.14, and PCM at 1.84 — though PCM's low score is heavily influenced by the 50% zero-coverage rate. The messaging hierarchy reflects market incentive structures: vendors invest most in what competitors are already saying (PPD, TDT) and underinvest in differentiating categories (PCM, CTL)."
        },
        {
            "header": "Only 20% of Vendors Achieve Balanced Messaging Across All Five Pillars",
            "body": "When balanced messaging is defined as scoring above 2.5 in all five pillars, only 20% of the market qualifies. The remaining 80% have at least one pillar below 2.5 — typically PCM (50% zero coverage) or CTL (30% zero coverage). This imbalance creates predictable competitive vulnerabilities: a vendor with strong PPD and TDT but zero PCM will lose evaluations where pricing transparency is weighted, regardless of product strength. The market's pillar imbalance is the single largest source of preventable competitive losses."
        },
        {
            "header": "Startups Outperform Established Vendors on Competitive Differentiation Clarity",
            "body": "The 47 startups in the dataset (those flagged as early-stage or pre-IPO) score 3.34 on PPD-02 (Competitive Differentiation Clarity) compared to 3.03 for the 148 established vendors — a 0.31-point advantage. Startups must differentiate through messaging because they cannot lean on brand recognition or installed base. This sharper positioning gives startups a measurable messaging advantage in the one sub-pillar that most directly influences competitive shortlist decisions. Established vendors should study startup messaging for differentiation specificity."
        },
        {
            "header": "Thought Leadership Investment Gaps: 30% of Vendors Have No CTL Presence",
            "body": "Thirty percent of vendors score zero on CTL, meaning they produce no published research, maintain no analyst engagement program, and make no conference or webinar appearances. Among the 70% who do invest in CTL, the average score is 3.05 — indicating that vendors who choose to invest do so at a competent level. The 30% gap represents vendors who have opted out of market education entirely, relying on product messaging and sales motions alone. In an increasingly analyst-influenced buying process, zero CTL presence creates a visibility deficit that compounds over time."
        }
    ],
    "recommendations": [
        {
            "header": "Close the PCM Coverage Gap Before Your Competitors Do",
            "body": "With 50% of the market providing zero pricing signals, any PCM investment creates immediate differentiation. Publish pricing models, consumption calculators, and TCO frameworks. The vendors currently addressing PCM score 3.70 on average — proving that pricing transparency, when attempted, is executed well. Be among the first movers in a category where half the field hasn't started."
        },
        {
            "header": "Balance Your Pillar Portfolio — Fix Your Weakest Pillar First",
            "body": "Only 20% of vendors score above 2.5 in all five pillars. If you have strong PPD and TDT but weak PCM or CTL, your competitive vulnerability is in the pillars you're ignoring, not the ones you're investing in. A 1.0-point improvement in your weakest pillar has more competitive impact than a 0.5-point improvement in your strongest."
        },
        {
            "header": "Benchmark Against Market Baselines, Not Just Competitors",
            "body": "The market baselines are: PPD 3.09, PCS 2.80, TDT 3.04, PCM 1.84, CTL 2.14. If any of your pillar scores fall more than 1.0 point below these, you have a competitive messaging gap. Use these benchmarks to set messaging investment priorities and track quarterly improvement. The benchmarks also reveal where the market is over-investing (PPD, TDT) and where differentiation opportunity exists (PCM, CTL)."
        },
        {
            "header": "Invest in CTL if You Compete in Analyst-Influenced Buying Cycles",
            "body": "If your go-to-market motion depends on analyst coverage, Gartner Peer Insights reviews, or conference visibility, a zero CTL score is a critical gap. The 30% of vendors with no CTL presence are invisible to analyst-influenced buyers. Basic CTL investment — published research, webinar presence, analyst briefing programs — costs less than most product marketing initiatives but creates recurring visibility that compounds."
        }
    ],
    "analysis_sections": [
        {
            "title": "GTM Messaging Score Distribution by Pillar",
            "body": "PPD (Product Positioning & Differentiation): Mean 3.09, 99% coverage. The market's strongest and most universal messaging category — virtually every vendor invests here. The distribution is tight (std dev 1.04) with most vendors clustering between 2.0 and 4.5. PCS (Proof Points & Case Studies): Mean 2.80, 98% coverage. Solid coverage but lower scores than PPD, reflecting that vendors articulate product claims more specifically than evidence claims. TDT (Technical Depth & Transparency): Mean 3.04, 99% coverage. Nearly matches PPD in both score and coverage — technical messaging is a market expectation. PCM (Pricing & Commercial Model): Mean 1.84 overall (3.70 non-zero), 50% coverage. The most bimodal pillar: vendors either invest seriously (3.70 avg) or not at all (zero). CTL (Content & Thought Leadership): Mean 2.14 overall (3.05 non-zero), 70% coverage. A discretionary investment with moderate uptake."
        },
        {
            "title": "Messaging Portfolio Balance Analysis",
            "body": "Only 20% of vendors achieve balanced messaging (all five pillars above 2.5). The most common imbalance pattern is strong PPD + TDT + PCS with missing PCM or CTL. This reflects a market where vendors default to product-centric messaging (what it does, how it works, who uses it) while neglecting commercial context (what it costs) and market education (why it matters). The imbalance is structural: vendors operating in markets without established pricing norms or analyst coverage frameworks have fewer incentives to invest in PCM or CTL. But as buying processes standardize and analyst influence grows, these gaps become increasingly costly."
        },
        {
            "title": "The Startup Messaging Advantage",
            "body": "47 startups in the dataset show a consistent messaging pattern: sharper differentiation (PPD-02: 3.34 vs 3.03 for established vendors), more specific claims, and tighter pillar alignment. Startups cannot win on breadth, brand, or installed base — they must win on messaging specificity and differentiation clarity. This constraint produces measurably better messaging in the one area that most influences shortlist decisions (PPD-02). The lesson for established vendors: the messaging discipline that scarcity imposes on startups is worth emulating voluntarily."
        },
        {
            "title": "Competitive Messaging Gap Opportunities by Pillar",
            "body": "The largest competitive opportunity is in PCM: with 50% of vendors at zero, any investment creates immediate visibility. The second-largest is CTL at 30% zero coverage. In the core messaging pillars (PPD, TDT, PCS), the variance between vendors within each pillar (std dev 0.89-1.04) is tight enough that meaningful differentiation requires scoring well above the mean — typically 4.0+ to stand out. But in PCM and CTL, merely showing up puts you ahead of 30-50% of the market. The optimal CMO investment strategy is: maintain competence in PPD/TDT/PCS (above 3.0), then differentiate through PCM and CTL investment where competition is thinnest."
        }
    ],
    "background": "This CMO-focused perspective isolates the GTM messaging dimension of the Product Market Readiness framework for competitive benchmarking. While the CPO perspective focuses on closing the credibility gap through proof investment, this perspective helps marketing leaders understand where messaging investment yields competitive advantage, where pillar coverage gaps create vulnerability, and how messaging portfolio balance affects market positioning. The analysis covers 195 cybersecurity vendors with all-zero-score vendors excluded to ensure statistical validity.",
    "impact": "For Chief Marketing Officers, the messaging effectiveness audit reveals three actionable insights: (1) the market has a massive PCM blind spot — half of vendors provide no pricing transparency, creating a first-mover advantage; (2) messaging quality varies more across your own pillars than between you and competitors within any pillar, meaning internal rebalancing yields more competitive gain than outspending rivals in your strongest areas; and (3) balanced messaging across all five pillars is rare (20% of vendors) and therefore competitively valuable. The audit enables evidence-based marketing budget allocation that prioritizes coverage gaps over incremental improvements in already-strong categories.",
    "conclusion": "The cybersecurity vendor messaging landscape is a study in asymmetric investment: universal coverage in product positioning and technical depth, but massive gaps in pricing transparency and thought leadership. Half the market publishes no pricing signal. Thirty percent produce no thought leadership content. Only 20% achieve messaging balance across all five pillars. For CMOs, the strategic insight is counterintuitive: the highest-ROI messaging investment is not in the pillars where you already compete (PPD, TDT) but in the ones where half your competitors have left the field empty (PCM, CTL). Messaging balance is rare and competitively valuable — vendors who achieve it will win disproportionately as buyers adopt structured evaluation frameworks that penalize coverage gaps.",
    "glossary": {
        "GTM Messaging Score": "0-5 rating of how well a vendor articulates a capability in public-facing content.",
        "Messaging Portfolio Balance": "Distribution of GTM messaging scores across all five pillars. A balanced portfolio scores above 2.5 in all pillars. Only 20% of vendors achieve this.",
        "Pillar Coverage": "Percentage of vendors with non-zero scores in each pillar. Ranges from 99% (PPD, TDT) to 50% (PCM).",
        "Competitive Messaging Gap": "The difference between your messaging score and the market baseline in a given pillar.",
        "Messaging Consistency": "Alignment of positioning narrative across all public channels — websites, collateral, analyst perceptions, press coverage."
    },
    "evidence": {
        "methodology": "GTM messaging scores evaluated from cross-schema capability evidence and publicly accessible vendor content including websites, product documentation, press releases, and analyst briefing materials. Scoring follows the PMR 0-5 scale. 195 vendors analyzed after excluding 13 vendors with all-zero scores.",
        "data_sources": ["Cross-schema capability scores from 4 Gartner research schemas", "Vendor websites and solution pages", "Product collateral and sales documentation", "Press releases and media coverage", "Conference presentations and webinar content"],
        "limitations": "Messaging quality assessment involves subjective judgment in borderline cases. Scores reflect publicly accessible content and cross-schema evidence only. PCM and CTL zero-coverage rates heavily influence pillar means — non-zero averages (PCM 3.70, CTL 3.05) provide a better benchmark for vendors who do invest in these areas.",
        "key_statistics": {
            "total_vendors": 195,
            "ppd_mean": 3.09,
            "pcs_mean": 2.80,
            "tdt_mean": 3.04,
            "pcm_mean": 1.84,
            "pcm_nonzero_mean": 3.70,
            "ctl_mean": 2.14,
            "ctl_nonzero_mean": 3.05,
            "ppd_coverage_pct": 99,
            "pcs_coverage_pct": 98,
            "tdt_coverage_pct": 99,
            "pcm_coverage_pct": 50,
            "ctl_coverage_pct": 70,
            "balanced_messaging_pct": 20.0,
            "within_vendor_std": 1.13,
            "between_vendor_std_ppd": 1.04,
            "between_vendor_std_pcs": 0.95,
            "between_vendor_std_tdt": 0.89,
            "startup_ppd02_mean": 3.34,
            "established_ppd02_mean": 3.03,
            "startup_ppd02_delta": 0.31,
            "startups_count": 47,
            "established_count": 148
        }
    }
}

with open('pmr_market_insight_reports.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Rewrote reports 1 and 2. File has {len(data['reports'])} reports.")
for r in data['reports']:
    print(f"  [{r['id']}] {r['title'][:80]}")
