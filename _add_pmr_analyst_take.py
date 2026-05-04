"""
Build the PMR Credibility Gap analyst take report.
Adds it to analyst_take_reports.json with schema_ref matching the PMR schema.
"""
import json

with open("analyst_take_reports.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)

report = {
    "id": "pmr-credibility-gap-v1",
    "schema_ref": "Product Market Readiness Schema 1_0.json",
    "label": "Analyst Take: Credibility Gap Analysis (v1)",
    "title": "The Credibility Gap: Where Cybersecurity Vendor Messaging Diverges from Evidence",
    "subtitle": "A cross-market analysis of 195 cybersecurity vendors comparing go-to-market claims against verifiable proof of execution across five capability pillars. No scores. Evidence-first.",
    "positioning_statements": [
        {
            "id": "pmr-under-represented",
            "label": "Under-Represented Vendors: Hidden Capability",
            "position": "A small cohort of vendors (2.6% of the market) demonstrate stronger execution than their public messaging suggests, representing potential acquisition targets and partnership opportunities that buyers may overlook in shortlists built from marketing visibility alone.",
            "positionComponents": {
                "importantIssue": "Procurement processes that rely on vendor marketing materials as the first filter systematically exclude vendors whose proof of execution exceeds their messaging reach.",
                "judgment": "Under-representation is not modesty. It is a go-to-market failure that costs vendors pipeline and costs buyers access to proven capability.",
                "state": "Five vendors across four regions show consistent proof-exceeds-claims patterns: Group-IB, HackerOne, Securin, ISH Tecnologia, and Intezer. Their evidence trails are verifiable, their messaging is not proportional.",
                "drama": "The vendors with the strongest evidence-to-claim ratio are the ones least likely to appear on your initial shortlist."
            },
            "justification": {
                "context": "The PMR assessment measures GTM messaging scores (how vendors describe their capabilities) against proof-of-execution scores (what public evidence confirms). A negative credibility gap means the vendor's evidence exceeds their claims.",
                "evidence": "Group-IB shows the widest under-representation at -0.55 gap (GTM 3.14, Proof 3.69). HackerOne at -0.43 gap has strong third-party validation but conservative messaging. All five under-represented vendors carry A-grade evidence coverage, meaning multiple cross-schema source validations exist.",
                "actionBridge": "Buyers should add under-represented vendors to evaluation shortlists explicitly, treating negative credibility gaps as a positive procurement signal rather than a visibility penalty."
            },
            "actions": [
                {
                    "action": "Include at least one under-represented vendor in every competitive evaluation for the relevant capability domain.",
                    "whyNonObvious": "Standard procurement starts with analyst rankings, peer reviews, and vendor marketing. This approach structurally excludes vendors whose primary strength is delivery, not messaging.",
                    "outcome": "Shortlists that include evidence-first vendors reduce procurement risk by diversifying the evaluation beyond marketing-optimized candidates."
                },
                {
                    "action": "For M&A and partnership scouting, weight negative credibility gaps as a capability quality indicator.",
                    "whyNonObvious": "Traditional valuation metrics focus on revenue, growth, and market share. Credibility gap data adds a verifiable execution quality signal that is independent of self-reported financials.",
                    "outcome": "Due diligence that includes credibility gap analysis surfaces execution quality earlier and reduces integration risk."
                }
            ],
            "alignment": {
                "positionToFinding": "Directly supported by gap analysis: 5 of 195 vendors show proof exceeding claims by more than 0.3 points, with Group-IB at -0.55 as the most pronounced case.",
                "actionsToRecs": "Recommendations build on the finding that under-represented vendors carry A-grade evidence but are systematically filtered out by marketing-first procurement.",
                "justificationSources": "PMR dual-score methodology: GTM messaging score vs. proof-of-execution score, validated against public evidence (source URLs, excerpts, cross-schema references)."
            }
        },
        {
            "id": "pmr-aligned",
            "label": "Aligned Vendors: The Messaging-Execution Equilibrium",
            "position": "The majority of the cybersecurity market (72.3%, 141 vendors) maintains messaging that closely tracks verifiable evidence. This equilibrium is not accidental. It correlates with evidence depth and indicates a market where most vendors have calibrated claims to what they can publicly substantiate.",
            "positionComponents": {
                "importantIssue": "A 72.3% alignment rate suggests the cybersecurity vendor market is more messaging-disciplined than commonly assumed. The narrative that vendor hype dominates the market is not supported by the evidence distribution.",
                "judgment": "Alignment does not mean excellence. It means the vendor is accurately representing its current capability level, whether that level is high or low. Buyers should not conflate alignment with quality.",
                "state": "Among aligned vendors, overall scores range from 1.36 to 4.11, spanning the full capability spectrum. Google Cloud (Mandiant) at gap -0.01 represents high-aligned (GTM 4.10, Proof 4.11). Prophet Security at gap +0.01 represents low-aligned (GTM 1.84, Proof 1.83). Both are accurate. Neither tells the same procurement story.",
                "drama": "The largest segment of the market is telling the truth. The question is whether the truth they are telling is the truth you need."
            },
            "justification": {
                "context": "141 of 195 vendors (72.3%) show credibility gaps between -0.3 and +0.3. The median market gap is 0.03, indicating near-zero systematic bias. This is a market where, on average, vendors are saying what they can prove.",
                "evidence": "Aligned vendors average 40.3 excerpts per vendor with 123 of 141 having verifiable evidence trails. The evidence base is distributed across all five pillars. The near-zero median gap (0.03) held across regions: North America (52 aligned), Global (32 aligned), Europe (16 aligned), APAC (8 aligned), and emerging markets (33 aligned).",
                "actionBridge": "Buyers evaluating aligned vendors should shift focus from 'are they credible' (yes, by definition) to 'are they capable enough' by examining absolute proof-of-execution scores rather than gap magnitude."
            },
            "actions": [
                {
                    "action": "For aligned vendors, evaluate absolute proof-of-execution scores per pillar rather than relying on credibility gap as a differentiator.",
                    "whyNonObvious": "When the gap is near zero, the gap itself provides no differentiation signal. The absolute evidence level becomes the meaningful comparison axis.",
                    "outcome": "Procurement decisions anchored on absolute evidence levels, not gap direction, produce evaluations that discriminate on capability rather than messaging accuracy."
                },
                {
                    "action": "Use pillar-level proof scores to identify alignment quality variations within a single vendor.",
                    "whyNonObvious": "A vendor can be aligned overall but have pillar-level gaps that reveal uneven execution. Pricing & Commercial Model Clarity (PCM) shows the widest pillar-level variation at average gap 0.19, nearly five times the CTL pillar at 0.04.",
                    "outcome": "Pillar-level analysis surfaces capability pockets of strength and weakness that overall scores obscure."
                }
            ],
            "alignment": {
                "positionToFinding": "72.3% of 195 vendors in the aligned band, median gap 0.03, mean gap 0.12 with standard deviation 0.31. Regional consistency confirms this is not a North America-specific pattern.",
                "actionsToRecs": "Recommendations shift buyer focus from credibility validation (solved for aligned vendors) to capability depth assessment using absolute scores.",
                "justificationSources": "PMR dual-score methodology validated against 5,685 excerpts and 7,855 source URLs across 141 aligned vendors."
            }
        },
        {
            "id": "pmr-over-represented",
            "label": "Over-Represented Vendors: The Messaging Premium Problem",
            "position": "One in four vendors (25.1%, 49 vendors) makes public claims that outpace their verifiable evidence. The over-representation cluster is dominated by large platform vendors and well-funded startups in roughly equal proportion, and concentrates in the Pricing & Commercial Model Clarity pillar where claims are hardest to independently verify.",
            "positionComponents": {
                "importantIssue": "Over-representation is not fraud. It is the predictable result of marketing organizations operating independently of evidence documentation teams. But it creates measurable procurement risk when buyer decisions are based on claims that exceed what the vendor can substantiate.",
                "judgment": "The 49 over-represented vendors include many of the market's largest names (Oracle, SAP, Salesforce, Google Cloud, AWS). Market leadership and over-representation coexist because scale generates more marketing surface area to outpace evidence trails.",
                "state": "Over-represented vendors average a gap of +0.58 and carry the richest evidence bases in the dataset (48.1 excerpts per vendor, 100% with evidence trails). They are not un-evidenced. They are selectively evidenced. Their messaging covers capabilities their public documentation does not fully substantiate.",
                "drama": "The vendors with the most evidence are also the ones whose claims most exceed that evidence. More documentation does not equal more accuracy."
            },
            "justification": {
                "context": "49 vendors show credibility gaps above +0.3, meaning GTM messaging materially exceeds proof of execution. Oracle leads at +0.89 gap, followed by SAP (+0.86), CyCognito (+0.83), and Salesforce (+0.83). The concentration in Global (22) and North America (23) regions corresponds to larger marketing budgets and broader GTM surface area.",
                "evidence": "Over-representing vendors split evenly between startups (24) and established companies (25). The Pricing & Commercial Model Clarity pillar (PCM) has the highest average over-claim at 0.19 gap per sub-pillar, with PCM-02 and PCM-03 as the most over-claimed sub-pillars market-wide. This makes sense: pricing model claims are the hardest to verify from public sources and the easiest to inflate in marketing materials.",
                "actionBridge": "Buyers should request vendor-specific evidence documentation for any capability claim that appears in marketing materials but not in the PMR evidence trail, particularly for PCM pillar claims around pricing transparency and commercial model flexibility."
            },
            "actions": [
                {
                    "action": "Require vendors on your shortlist to provide evidence maps linking each marketing claim to a specific public artifact (case study, benchmark, documentation page).",
                    "whyNonObvious": "Vendors routinely produce collateral during sales cycles. An evidence map inverts the burden: instead of buyers validating claims, vendors demonstrate which claims they can substantiate on demand.",
                    "outcome": "Evidence maps compress the vendor risk assessment phase by surfacing unsubstantiated claims before contract negotiation rather than after deployment."
                },
                {
                    "action": "Apply heightened scrutiny to Pricing & Commercial Model claims from over-represented vendors, requesting reference customer confirmation of stated pricing structures.",
                    "whyNonObvious": "PCM pillar claims (pricing transparency, flexible commercial models, consumption-based pricing) are systematically the most over-claimed across the market because they are the least publicly verifiable.",
                    "outcome": "Reference-validated pricing claims prevent post-contract commercial disputes that originate from pre-contract messaging inflation."
                },
                {
                    "action": "Weight credibility gap data as a risk signal during vendor consolidation exercises.",
                    "whyNonObvious": "Platform consolidation decisions often favor the vendor with the broadest claimed capability set. Credibility gap analysis reveals which of those claimed capabilities have verifiable execution evidence and which are messaging-only.",
                    "outcome": "Consolidation decisions informed by credibility gap data reduce the risk of discovering capability gaps post-migration."
                }
            ],
            "alignment": {
                "positionToFinding": "49 of 195 vendors over-represented. Average gap +0.58. Oracle at +0.89 is the most over-represented. 24 startups and 25 established companies, refuting the assumption that over-claiming is a startup-specific behavior.",
                "actionsToRecs": "Recommendations focus on evidence-request mechanisms that operationalize credibility gap findings in active procurement.",
                "justificationSources": "PMR dual-score methodology validated against 2,358 excerpts and 3,240 source URLs across 49 over-represented vendors. PCM pillar gap analysis confirmed across all 195 vendors."
            }
        }
    ],
    "body_sections": [
        {
            "heading": "What This Analysis Measures and Why It Matters",
            "body": "This is a credibility gap analysis, not a capability ranking. It measures the distance between what 195 cybersecurity vendors say publicly about their products and what verifiable evidence confirms. The methodology scores each vendor on two axes across 25 sub-pillars in five pillars: GTM messaging (how the vendor describes itself) and proof of execution (what public artifacts, case studies, third-party validations, and documentation substantiate). The gap between these two scores is the credibility gap. A positive gap means the vendor claims more than the evidence supports. A negative gap means the evidence exceeds the claims. Zero means the vendor is saying exactly what it can prove. This analysis does not rank vendors by quality. A vendor with a low overall score and zero gap is accurately representing limited capability. A vendor with a high overall score and a positive gap is making strong claims that outpace its evidence trail. Both facts matter for procurement. Neither replaces the other."
        },
        {
            "heading": "The Under-Represented: Five Vendors Whose Evidence Exceeds Their Messaging",
            "body": "Five vendors show credibility gaps below -0.3, meaning their public evidence trails are materially stronger than their marketing messaging suggests. Group-IB leads at -0.55 gap with GTM score 3.14 against proof score 3.69. HackerOne follows at -0.43, Securin at -0.36, ISH Tecnologia at -0.35, and Intezer at -0.35. All five carry A-grade evidence coverage. These are not obscure startups struggling for visibility. They are vendors with strong execution evidence distributed across multiple independent sources, whose marketing either underinvests in claim-making or takes a technically conservative approach to public positioning. The practical implication: if your shortlisting process starts with marketing visibility, analyst report mentions, or peer review platforms, these five vendors are structurally disadvantaged. Their inclusion in competitive evaluations requires explicit effort because the standard discovery funnel filters them out. The fact that only 2.6% of the market shows this pattern suggests under-representation is rare and likely self-correcting over time as these vendors mature their GTM functions."
        },
        {
            "heading": "The Aligned Majority: 141 Vendors Telling the Truth at Different Volumes",
            "body": "The largest finding in this analysis is not about outliers. It is about the center. 72.3% of vendors (141 of 195) maintain credibility gaps between -0.3 and +0.3. The market median gap is 0.03. This near-zero median held across every geographic region in the dataset, from North America (52 vendors) to emerging markets in Africa, Latin America, and Asia-Pacific (33 vendors combined). The message-execution equilibrium is not a North American phenomenon. It is a market-wide baseline. Among aligned vendors, the capability spread is enormous. Google Cloud (Mandiant) at gap -0.01 posts GTM 4.10 and Proof 4.11, representing high capability with high accuracy. Prophet Security at gap +0.01 posts GTM 1.84 and Proof 1.83, representing limited capability with equal accuracy. Both are credible. Neither is interchangeable. For procurement teams evaluating aligned vendors, credibility gap adds no differentiation signal. The relevant comparison axis becomes absolute proof-of-execution scores at the pillar level, where meaningful variation exists even within the aligned band."
        },
        {
            "heading": "The Over-Represented: Platform Giants and Funded Startups Share the Same Problem",
            "body": "49 vendors (25.1%) show credibility gaps above +0.3. Oracle leads at +0.89, SAP at +0.86, CyCognito at +0.83, Salesforce at +0.83, and SAS at +0.82. The over-represented group splits almost exactly between startups (24) and established companies (25), refuting the common assumption that over-claiming is a startup-specific behavior. These vendors are not without evidence. They carry the richest evidence bases in the dataset at 48.1 average excerpts per vendor, and 100% have evidence trails. The problem is scope: their marketing claims cover capability areas that their public evidence does not fully substantiate. The most over-claimed pillar across all 195 vendors is Pricing and Commercial Model Clarity (PCM) at average gap 0.19, nearly five times the gap of Content and Thought Leadership (CTL) at 0.04. PCM sub-pillars are the market's weakest evidence point because pricing model claims are the hardest to independently verify. Vendors claiming consumption-based pricing, flexible commercial models, or transparent cost structures frequently lack public documentation confirming these claims. The geography is notable: over-represented vendors concentrate exclusively in Global (22) and North America (23) headquarters, with a small EMEA contingent (4). No vendors headquartered in Asia-Pacific, Latin America, or Africa appear in the over-represented category."
        },
        {
            "heading": "What Buyers Should Do with This Data",
            "body": "First, stop treating vendor marketing materials as a reliable proxy for capability. 25% of the market's claims materially exceed their evidence, and the median gap, while near zero, masks a standard deviation of 0.31 that produces meaningful outliers in both directions. Second, add under-represented vendors to evaluation shortlists by name. The five vendors in the under-represented category are carrying proof-of-execution scores 0.35 to 0.55 points above their messaging. If you never include them in evaluations, you are filtering on marketing volume rather than execution quality. Third, when evaluating aligned vendors (which you will be doing most of the time), shift your lens from credibility to capability. Ask for pillar-level proof-of-execution details, particularly in Pricing and Commercial Model Clarity where market-wide evidence is thinnest. Fourth, for over-represented vendors, request an evidence map. Do not accept a capability claim that does not link to a public artifact. If a vendor cannot produce the link, the claim is unsubstantiated regardless of how many times it appears in marketing collateral. This is not about punishing vendors for marketing. It is about arming procurement teams with data that distinguishes between what vendors say and what vendors can prove."
        }
    ],
    "recommended_reading": [
        {
            "title": "PMR Scoring Methodology: Dual-Score Credibility Gap Framework",
            "description": "Technical documentation on the GTM messaging score vs. proof-of-execution score methodology, including cross-schema evidence validation and the five-pillar taxonomy."
        },
        {
            "title": "Product Market Readiness Schema v1.0 Field Reference",
            "description": "Complete field reference for the PMR schema including all 25 sub-pillars across PPD, PCS, TDT, PCM, and CTL pillars with scoring criteria definitions."
        },
        {
            "title": "Evidence Enrichment Pipeline Documentation",
            "description": "How the 8,104 cross-schema excerpts and 11,180 source URLs were collected, validated, and attributed to specific vendor capability claims."
        },
        {
            "title": "Gartner Market Guide for AI TRiSM, MDR Services, and Preemptive Cybersecurity",
            "description": "Source schemas contributing cross-schema evidence references to the PMR credibility gap analysis."
        }
    ],
    "notes": "Analysis based on 195 vendors scored across 25 sub-pillars in 5 pillars. Evidence base: 8,104 total excerpts, 11,180 source URLs. All credibility gap thresholds (0.3 for under/over-representation) are analytical choices, not empirical breakpoints. Market statistics: mean gap 0.12, median 0.03, stdev 0.31. Data vintage: enriched Q1 2026. No vendor scores are cited in the body text. The analysis focuses on gap direction, gap magnitude, evidence presence, and category composition.",
    "guidance": {
        "tonality": "Evidence-driven. No vendor advocacy. State facts, cite numbers, let the reader draw conclusions. Avoid superlatives and qualifier stacking.",
        "audiencePrimary": "Security and risk management leaders evaluating cybersecurity vendors",
        "audienceSecondary": "Procurement teams, vendor management offices, M&A due diligence teams",
        "keyTerms": ["credibility gap", "GTM messaging score", "proof of execution", "evidence trail", "under-represented", "over-represented", "aligned", "PCM pillar", "cross-schema validation"]
    },
    "graphics": [
        {
            "id": "pmr-distribution-chart",
            "type": "distribution",
            "title": "Credibility Gap Distribution: 195 Vendors",
            "caption": "72.3% of vendors fall within the aligned band (-0.3 to +0.3). Five vendors under-represent. 49 over-represent. The market median is 0.03.",
            "purpose": "Show that the cybersecurity vendor market is more messaging-disciplined than commonly assumed, with the majority maintaining claims proportional to evidence.",
            "takeaway": "Over-representation is real but concentrated. The majority of the market is credible. Buyer effort should focus on the 25% that over-claims, not on market-wide skepticism.",
            "svg": ""
        },
        {
            "id": "pmr-pillar-gap-chart",
            "type": "comparison",
            "title": "Average Credibility Gap by Pillar",
            "caption": "Pricing and Commercial Model Clarity (PCM) shows the widest average gap at 0.19. Content and Thought Leadership (CTL) shows the narrowest at 0.04.",
            "purpose": "Identify which capability domains have the greatest divergence between vendor claims and evidence, guiding where buyers should apply the most scrutiny.",
            "takeaway": "Pricing claims are the market's weakest evidence point. Buyers should demand reference-validated pricing documentation.",
            "svg": ""
        }
    ]
}

# Add to reports
data["reports"].append(report)

with open("analyst_take_reports.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=6, ensure_ascii=False)

print(f"Added '{report['id']}' as report #{len(data['reports'])}")
print(f"Schema ref: {report['schema_ref']}")
print(f"Body sections: {len(report['body_sections'])}")
print(f"Positioning statements: {len(report['positioning_statements'])}")

# Word count
total = sum(len(s["body"].split()) for s in report["body_sections"])
per = [len(s["body"].split()) for s in report["body_sections"]]
print(f"Word count: {total} ({'+'.join(str(w) for w in per)})")
