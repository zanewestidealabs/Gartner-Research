"""Remove AI-isms from precyber_market_insight_reports.json.

Targets:
- Em-dashes (—) replaced with commas, colons, or parentheses depending on context
- Overused AI filler words (fundamentally, notably, paradigm, landscape, etc.)
- Cliches (one throat to choke, inflection point, paradox, etc.)
"""

import json, re, sys

INPUT = 'precyber_market_insight_reports.json'

with open(INPUT, 'r', encoding='utf-8') as f:
    raw = f.read()

changes = []

def sub(old, new, reason=''):
    global raw
    if old in raw:
        raw = raw.replace(old, new)
        changes.append(f'  {reason}: "{old[:60]}..." -> "{new[:60]}..."' if len(old) > 60 else f'  {reason}: "{old}" -> "{new}"')

# ═══════════════════════════════════════════════════════
# LABEL / TITLE / SUMMARY
# ═══════════════════════════════════════════════════════
sub('CPO / Product Strategy — Market Fragmentation & Service Opportunity',
    'CPO / Product Strategy: Market Fragmentation & Service Opportunity',
    'label em-dash')

sub('Market Insight: The Preemptive Cybersecurity Market Is Dangerously Fragmented — Full-Spectrum Vendors Will Define the Next Era',
    'Market Insight: The Preemptive Cybersecurity Market Is Dangerously Fragmented. Full-Spectrum Vendors Will Define the Next Era',
    'title em-dash')

sub('The vast majority of vendors — platform providers and service operators alike — compete',
    'The vast majority of vendors, platform providers and service operators alike, compete',
    'summary em-dash pair')

# ═══════════════════════════════════════════════════════
# SPA
# ═══════════════════════════════════════════════════════
sub('Vendors that develop full-spectrum capability strategies — either through organic investment, acquisition, or managed service partnerships — by 2028 will capture disproportionate market share',
    'Vendors that develop full-spectrum capability strategies (through organic investment, acquisition, or managed service partnerships) by 2028 will capture outsized market share',
    'SPA em-dash pair + disproportionate')

# Wait — disproportionate was already an AI-ism. Replace outsized too. 
# Actually "outsized" was flagged. Use "significant" instead.
sub('will capture outsized market share',
    'will capture significant market share',
    'outsized')

# ═══════════════════════════════════════════════════════
# FINDING 1
# ═══════════════════════════════════════════════════════
sub('The preemptive cybersecurity market is fundamentally fragmented',
    'The preemptive cybersecurity market is heavily fragmented',
    'fundamentally')

sub('five preemptive cybersecurity pillars — Exposure Management (EXM), Adversary Management & Threat Intelligence (AMT), Autonomous Detection & Response (ADR), Posture & Policy Management (PPM), and Services & Capabilities (SVC) — only',
    'five preemptive cybersecurity pillars (Exposure Management [EXM], Adversary Management & Threat Intelligence [AMT], Autonomous Detection & Response [ADR], Posture & Policy Management [PPM], and Services & Capabilities [SVC]), only',
    'finding1 em-dash pair')

# ═══════════════════════════════════════════════════════
# FINDING 2
# ═══════════════════════════════════════════════════════
sub('Buyers looking for integrated preemptive programs that include adversary-centric threat anticipation and managed delivery must navigate a fragmented vendor landscape with limited choices.',
    'Buyers looking for integrated preemptive programs that include adversary-centric threat anticipation and managed delivery face a fragmented market with limited choices.',
    'navigate + landscape')

# ═══════════════════════════════════════════════════════
# FINDING 3
# ═══════════════════════════════════════════════════════
sub('Their strengths in technology — averaging 3.07 on EXM and 2.84 on PPM — are not complemented',
    'Their strengths in technology (averaging 3.07 on EXM and 2.84 on PPM) are not complemented',
    'finding3 em-dash pair')

# ═══════════════════════════════════════════════════════
# FINDING 4
# ═══════════════════════════════════════════════════════
sub('The 11 direct service providers — vendors that operate their own SOCs and analyst teams to deliver managed outcomes — score',
    'The 11 direct service providers, vendors that operate their own SOCs and analyst teams to deliver managed outcomes, score',
    'finding4 em-dash pair')

sub('or policy governance — the very capabilities that define preemptive cybersecurity.',
    'or policy governance, the core capabilities that define preemptive cybersecurity.',
    'the very capabilities + em-dash')

# ═══════════════════════════════════════════════════════
# FINDING 5
# ═══════════════════════════════════════════════════════
sub('The 15 platform-plus-partner vendors — those that provide technology and rely on MSSP/channel partners for managed service delivery — show',
    'The 15 platform-plus-partner vendors, those that provide technology and rely on MSSP/channel partners for managed service delivery, show',
    'finding5 em-dash pair')

# ═══════════════════════════════════════════════════════
# FINDING 6
# ═══════════════════════════════════════════════════════
sub('Only three vendors achieve a minimum pillar score above 2.5 across all five domains — and they represent different delivery models.',
    'Only three vendors achieve a minimum pillar score above 2.5 across all five domains, and they represent different delivery models.',
    'finding6 em-dash')

sub('minimum pillar scores above 2.5 — meaning no significant blind spots',
    'minimum pillar scores above 2.5, meaning no significant blind spots',
    'finding6 body em-dash')

sub('This extreme concentration at the top illustrates how rare',
    'This concentration at the top shows how rare',
    'illustrates + extreme')

# ═══════════════════════════════════════════════════════
# RECOMMENDATION 1
# ═══════════════════════════════════════════════════════
sub("the underrepresented pillars — particularly AMT and SVC, which are the market's most significant blind spots.",
    "the underrepresented pillars, particularly AMT and SVC, which are the market's biggest gaps.",
    'rec1 em-dash + blind spots')

# ═══════════════════════════════════════════════════════
# RECOMMENDATION 2
# ═══════════════════════════════════════════════════════
sub('Platform vendors must develop a credible service delivery strategy — organic, acquired, or partnered.',
    'Platform vendors must develop a service delivery strategy: organic, acquired, or partnered.',
    'rec2 header em-dash + credible')

sub('The choice depends on scale, investment appetite, and time-to-market requirements — but the status quo of no service strategy is a strategic liability.',
    'The choice depends on scale, investment appetite, and time-to-market requirements, but the status quo of no service strategy is a strategic liability.',
    'rec2 body em-dash')

# ═══════════════════════════════════════════════════════
# RECOMMENDATION 3
# ═══════════════════════════════════════════════════════
sub("Investing in adversary management capabilities — threat anticipation, adversary profiling, attack surface intelligence — transforms the value proposition from",
    "Investing in adversary management capabilities (threat anticipation, adversary profiling, attack surface intelligence) shifts the value proposition from",
    'rec3 em-dash pair + transforms')

sub("a fundamentally different value proposition that commands premium pricing.",
    "a different value proposition that commands premium pricing.",
    'fundamentally')

# ═══════════════════════════════════════════════════════
# RECOMMENDATION 4
# ═══════════════════════════════════════════════════════
sub('close specific pillar gaps within 12-18 months.',
    'close specific pillar gaps within 12 to 18 months.',
    'style')

# ═══════════════════════════════════════════════════════
# RECOMMENDATION 5
# ═══════════════════════════════════════════════════════
sub('outcome-linked components: measurable reduction',
    'outcome-linked components, such as measurable reduction',
    'colon to comma')

sub('and it is the commercial translation of the strategic advantage that fragmented competitors cannot match.',
    'and it is the commercial expression of the advantage that fragmented competitors cannot match.',
    'translation -> expression')

# ═══════════════════════════════════════════════════════
# ANALYSIS SECTION 1: Five Pillars
# ═══════════════════════════════════════════════════════
sub('It encompasses five interconnected capability pillars',
    'It spans five interconnected capability pillars',
    'encompasses')

sub("Only 55% of vendors address this pillar, making it the market's most significant gap after services.",
    'Only 55% of vendors address this pillar, making it the second-largest gap behind services.',
    'most significant gap')

# ═══════════════════════════════════════════════════════
# ANALYSIS SECTION 2: By the Numbers
# ═══════════════════════════════════════════════════════
sub('Notably, no platform-only vendor achieves full-spectrum coverage',
    'No platform-only vendor achieves full-spectrum coverage',
    'Notably')

sub('all scoring 0 on four of five pillars',
    'all scoring 0 on four of the five pillars',
    'style')

# ═══════════════════════════════════════════════════════
# ANALYSIS SECTION 3: Service Delivery Gap
# ═══════════════════════════════════════════════════════
sub('This creates a paradox: the most technologically sophisticated preemptive platforms cannot be translated into managed outcomes without a third-party service layer.',
    'The result: the most technologically sophisticated preemptive platforms cannot be turned into managed outcomes without a third-party service layer.',
    'paradox')

sub('For platform CPOs, this is both a risk and an opportunity. The risk is commoditization: as platforms converge on feature parity, the differentiator shifts',
    'For platform CPOs, this is both a risk and an opportunity. The risk is commoditization: as platforms converge on feature parity, the differentiator moves',
    'shifts -> moves')

sub('establish a competitive moat that feature-level competitors cannot easily replicate.',
    'establish a competitive advantage that feature-level competitors cannot easily replicate.',
    'moat')

# ═══════════════════════════════════════════════════════
# ANALYSIS SECTION 4: Adversary Intelligence Deficit
# ═══════════════════════════════════════════════════════
sub('the gap is even more stark: 64% score below',
    'the gap is wider: 64% score below',
    'stark')

sub('Detection rules are based on known indicators rather than predicted adversary behavior.',
    'Detection rules rely on known indicators rather than predicted adversary behavior.',
    'are based on -> rely on')

sub('This deficit has direct operational consequences.',
    'This gap has direct operational consequences.',
    'deficit -> gap')

sub('for CPOs evaluating portfolio strategy, AMT is an underinvested domain with outsized impact.',
    'For CPOs evaluating portfolio strategy, AMT is an underinvested domain with high impact.',
    'outsized')

sub('For CPOs evaluating portfolio strategy, AMT is an underinvested domain with high impact.',
    'For CPOs evaluating portfolio strategy, AMT is an underinvested area with high impact.',
    'domain -> area')

# ═══════════════════════════════════════════════════════
# ANALYSIS SECTION 5: Three Delivery Models
# ═══════════════════════════════════════════════════════
sub('Their strategic advantage is operational accountability: when the service fails, there is one throat to choke.',
    'Their strategic advantage is operational accountability: when the service fails, there is a single point of ownership.',
    'one throat to choke')

sub('Their limitation is platform depth: average EXM (3.60) and PPM (2.97) scores trail behind platform vendors, reflecting an operational model optimized for service delivery rather than comprehensive platform capability.',
    'Their limitation is platform depth: average EXM (3.60) and PPM (2.97) scores trail behind platform vendors, reflecting an operational model built for service delivery rather than broad platform capability.',
    'comprehensive + optimized')

sub("the inherent limitations of partner-delegated service delivery. The vendor builds the platform; the partner delivers the outcome. This introduces accountability gaps that become visible when managed services underperform.",
    "the limitations of partner-delegated service delivery. The vendor builds the platform; the partner delivers the outcome. This creates accountability gaps that surface when managed services underperform.",
    'inherent + introduces + visible')

sub('The strategic takeaway: no single delivery model has solved the full-spectrum challenge.',
    'The takeaway: no single delivery model has solved the full-spectrum challenge.',
    'strategic takeaway')

# ═══════════════════════════════════════════════════════
# ANALYSIS SECTION 6: Full-Spectrum Opportunity 2030
# ═══════════════════════════════════════════════════════
sub('This manifests as formal MSSP certification programs',
    'This takes the form of formal MSSP certification programs',
    'manifests')

sub("These are not capabilities that can be acquired overnight.",
    "None of these can be built overnight.",
    'style')

# ═══════════════════════════════════════════════════════
# BACKGROUND
# ═══════════════════════════════════════════════════════
sub('represents an emerging category that shifts the security paradigm from reactive detection',
    'is an emerging category that moves security from reactive detection',
    'paradigm + represents')

sub('and neutralization. Unlike traditional cybersecurity approaches that focus on identifying and containing threats after they penetrate defenses, preemptive cybersecurity aims to',
    'and neutralization. Where traditional cybersecurity focuses on identifying and containing threats after they penetrate defenses, preemptive cybersecurity aims to',
    'Unlike -> Where')

sub('each scored on a 1-5 maturity scale with defined sub-pillar criteria. Vendors were additionally classified by delivery model:',
    'each scored on a 1-5 maturity scale with defined sub-pillar criteria. Vendors were also classified by delivery model:',
    'additionally -> also')

sub('direct service providers (11 vendors) that operate their own SOCs and deliver managed outcomes, platform-plus-partner models (15 vendors) that build technology and rely on channel/MSSP partners for service delivery, and platform-only providers (25 vendors) that offer technology licensing with no managed service component.',
    'direct service providers (11 vendors) that operate their own SOCs and deliver managed outcomes; platform-plus-partner models (15 vendors) that build technology and rely on channel/MSSP partners for service delivery; and platform-only providers (25 vendors) that offer technology licensing with no managed service component.',
    'comma-separated list to semicolons')

sub('driven by compliance automation and configuration governance demand.',
    'driven by compliance automation and configuration governance.',
    'demand')

sub('This diversity makes the fragmentation findings more significant: the gap is not between large and small vendors but between the very few that have assembled comprehensive preemptive capability and the many that remain locked into one or two specializations.',
    'This diversity makes the fragmentation findings more telling: the gap is not between large and small vendors, but between the few that have assembled broad preemptive capability and the many that remain in one or two specializations.',
    'significant + comprehensive + locked into + very few')

# ═══════════════════════════════════════════════════════
# IMPACT
# ═══════════════════════════════════════════════════════
sub('the common thread is urgency: the window for strategic positioning is open now and will narrow as consolidation reshapes the competitive landscape.',
    'the common thread is urgency: the window for strategic positioning is open now and will shrink as consolidation reshapes the market.',
    'landscape')

sub('The data makes the case for breadth: the 14 full-spectrum vendors average 3.35 across all pillars, while three-pillar vendors average 2.67 — a gap that reflects both broader capability and deeper specialization within each domain.',
    'The data makes the case for breadth: the 14 full-spectrum vendors average 3.35 across all pillars while three-pillar vendors average 2.67, a gap that reflects both broader capability and deeper specialization within each area.',
    'em-dash + domain')

sub("This is not a minor gap — it represents a fundamentally different market position.",
    "This is not a minor gap. It reflects a different market position.",
    'em-dash + fundamentally + represents')

sub('The fragmented technology landscape is an advantage if service providers can become the integration and orchestration layer.',
    'The fragmented technology market is an advantage if service providers can become the integration and orchestration layer.',
    'landscape')

sub('This positioning justifies premium pricing and longer contract terms.',
    'This positioning supports premium pricing and longer contract terms.',
    'justifies -> supports')

sub('MSSPs that extend from reactive MDR into proactive preemptive operations will differentiate sharply from the growing field of commodity managed detection providers.',
    'MSSPs that move from reactive MDR into proactive preemptive operations will stand apart from the growing field of commodity managed detection providers.',
    'differentiate sharply + extend')

sub('This complexity tax is substantial, and it creates strong buyer pull for vendors that can reduce it through integrated offerings.',
    'This complexity cost is real, and it creates strong buyer pull for vendors that can reduce it through integrated offerings.',
    'tax + substantial')

sub('We expect the current ratio of 14 full-spectrum vendors (27% of market) to grow to 50%+ by 2030, driven by M&A activity focused on filling pillar gaps — particularly AMT and SVC acquisitions by platform-strong vendors.',
    'We expect the current ratio of 14 full-spectrum vendors (27% of market) to grow past 50% by 2030, driven by M&A activity focused on filling pillar gaps, particularly AMT and SVC acquisitions by platform-strong vendors.',
    'em-dash + 50%+')

# ═══════════════════════════════════════════════════════
# CONCLUSION
# ═══════════════════════════════════════════════════════
sub('The preemptive cybersecurity market is at an inflection point defined by a central paradox: the security approach that buyers need — proactive, multi-pillar, outcome-oriented — is one that almost no vendor currently delivers comprehensively.',
    'The preemptive cybersecurity market faces a central tension: the security approach that buyers need (proactive, multi-pillar, outcome-oriented) is one that almost no vendor delivers end-to-end.',
    'inflection point + paradox + em-dashes + comprehensively')

sub('This fragmentation is not a market failure — it is a market opportunity.',
    'This fragmentation is not a market failure; it is a market opportunity.',
    'em-dash')

sub('will establish competitive positions that narrow-spectrum competitors cannot easily challenge.',
    'will build competitive positions that narrow-spectrum competitors cannot easily match.',
    'establish + challenge')

sub("Platform vendors should prioritize adversary intelligence and service delivery — the two largest market gaps.",
    "Platform vendors should prioritize adversary intelligence and service delivery, the two largest market gaps.",
    'em-dash')

sub("Do we have a path to full-spectrum coverage by 2028?** Whether through organic investment, acquisition, or structured partnerships, the window to establish preemptive market position is two to three years.",
    "Do we have a path to full-spectrum coverage by 2028?** Whether through organic investment, acquisition, or structured partnerships, the window to build preemptive market position is two to three years.",
    'establish -> build')

sub("The preemptive cybersecurity market will consolidate around vendors that can credibly answer",
    "The preemptive cybersecurity market will consolidate around vendors that can answer",
    'credibly')

sub("2. **Can we deliver preemptive outcomes, or do we deliver tools that require the buyer to create outcomes?** The distinction between technology vendors and outcome vendors will define competitive positioning by 2028.",
    "2. **Can we deliver preemptive outcomes, or do we sell tools that require the buyer to create outcomes?** The gap between technology vendors and outcome vendors will define competitive positioning by 2028.",
    'deliver -> sell, distinction -> gap')

sub('credibly deliver.', 'deliver.', 'credibly')
sub('credibly address', 'address', 'credibly')

# ═══════════════════════════════════════════════════════
# GLOSSARY
# ═══════════════════════════════════════════════════════
sub('A security paradigm focused on proactively anticipating',
    'A security approach focused on proactively anticipating',
    'paradigm')

# ═══════════════════════════════════════════════════════
# Catch remaining em-dashes
# ═══════════════════════════════════════════════════════
# Count remaining
remaining = raw.count('\u2014')
if remaining > 0:
    print(f'\n  {remaining} em-dashes remain. Scanning context...')
    for m in re.finditer(r'.{30}\u2014.{30}', raw):
        print(f'    ...{m.group()}...')

# Write output
with open(INPUT, 'w', encoding='utf-8') as f:
    f.write(raw)

print(f'\nApplied {len(changes)} replacements:')
for c in changes:
    print(c)

# Final count
final_emdashes = raw.count('\u2014')
print(f'\nEm-dashes: 65 -> {final_emdashes}')
