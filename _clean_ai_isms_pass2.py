"""Second pass: remove remaining em-dashes from precyber_market_insight_reports.json."""

import json

INPUT = 'precyber_market_insight_reports.json'

with open(INPUT, 'r', encoding='utf-8') as f:
    raw = f.read()

changes = []

def sub(old, new, reason=''):
    global raw
    if old in raw:
        raw = raw.replace(old, new)
        changes.append(reason)
    else:
        print(f'NOT FOUND: {reason}')

# REC 3 body
sub('a preemptive intelligence-driven program — a different value proposition',
    'a preemptive intelligence-driven program, a different value proposition',
    'rec3 body em-dash')

# REC 4 body
sub('The fragmented market structure — with most vendors concentrated in one or two domains — creates a target-rich acquisition environment',
    'The fragmented market structure (with most vendors concentrated in one or two areas) creates a target-rich acquisition environment',
    'rec4 em-dash pair + domain')

# REC 5 body
sub('the measurement infrastructure that full-spectrum platforms provide — and it is',
    'the measurement infrastructure that full-spectrum platforms provide, and it is',
    'rec5 em-dash')

# REC 6 body
sub('assemble multi-vendor preemptive stacks — combining best-of-breed EXM, AMT, ADR, and PPM platforms — and deliver them',
    'assemble multi-vendor preemptive stacks (combining best-of-breed EXM, AMT, ADR, and PPM platforms) and deliver them',
    'rec6 em-dash pair')

# ANALYSIS 1: Five Pillars - SVC description
sub("(SVC)**: The delivery layer — implementation, advisory, managed operations",
    "(SVC)**: The delivery layer, covering implementation, advisory, managed operations",
    'analysis1 SVC em-dash')

sub("requires competency across all five pillars — and the market overwhelmingly fails to provide this.",
    "requires competency across all five pillars, and the market overwhelmingly fails to provide this.",
    'analysis1 conclusion em-dash')

# ANALYSIS 2: By the Numbers - niche vendor list
sub("(Axonius, HashiCorp, Group-IB, Trellix — all scoring 0 on four of the five pillars)",
    "(Axonius, HashiCorp, Group-IB, Trellix, all scoring 0 on four of the five pillars)",
    'analysis2 em-dash')

# ANALYSIS 3: Service Delivery Gap
sub("Twenty-five of 51 vendors (49%) — nearly half the market — have",
    "Twenty-five of 51 vendors (49%), nearly half the market, have",
    'analysis3 opening em-dash pair')

sub("Average scores around 2.0 — basic implementation support",
    "Average scores around 2.0. Basic implementation support",
    'analysis3 SVC-01 em-dash')

sub("Moderate scores in the 2.0-2.5 range — most vendors offer",
    "Moderate scores in the 2.0-2.5 range. Most vendors offer",
    'analysis3 SVC-02 em-dash')

sub("capped at 1.0 for platform-only vendors — no managed service delivery option exists",
    "capped at 1.0 for platform-only vendors. No managed service delivery option exists",
    'analysis3 SVC-03 em-dash')

sub("Scores capped at 1.0-1.5 — AI capabilities exist in the product but",
    "Scores capped at 1.0-1.5. AI capabilities exist in the product but",
    'analysis3 SVC-04 em-dash')

sub("to crack the service delivery model — whether through internal build, acquisition, or structured partnerships — will establish",
    "to crack the service delivery model (whether through internal build, acquisition, or structured partnerships) will build",
    'analysis3 closing em-dash pair + establish')

# ANALYSIS 4: Adversary Intelligence Deficit
sub("that combine strong AMT with other pillars — Aqua Security (3.8 AMT), Morphisec (3.9 AMT), CyberArk (3.6 AMT), BeyondTrust (3.6 AMT) — use",
    "that combine strong AMT with other pillars, such as Aqua Security (3.8 AMT), Morphisec (3.9 AMT), CyberArk (3.6 AMT), and BeyondTrust (3.6 AMT), use",
    'analysis4 em-dash pair')

sub("from reactive to anticipatory — and the market opportunity is large",
    "from reactive to anticipatory, and the market opportunity is large",
    'analysis4 closing em-dash')

# ANALYSIS 5: Three Delivery Models - section intros
sub('**Direct Service Providers (11 vendors, 22%)** — These vendors',
    '**Direct Service Providers (11 vendors, 22%)**: These vendors',
    'analysis5 direct em-dash')

sub('**Platform-Plus-Partner Vendors (15 vendors, 29%)** — These vendors',
    '**Platform-Plus-Partner Vendors (15 vendors, 29%)**: These vendors',
    'analysis5 partner em-dash')

sub('**Platform-Only Vendors (25 vendors, 49%)** — Pure technology',
    '**Platform-Only Vendors (25 vendors, 49%)**: Pure technology',
    'analysis5 platform em-dash')

# ANALYSIS 6: phases
sub('**Phase 1 — Platform Extension (2025-2026)**',
    '**Phase 1: Platform Extension (2025-2026)**',
    'phase1 em-dash')

sub('**Phase 2 — Service Layer Development (2026-2028)**',
    '**Phase 2: Service Layer Development (2026-2028)**',
    'phase2 em-dash')

sub('**Phase 3 — Integrated Outcome Delivery (2028-2030)**',
    '**Phase 3: Integrated Outcome Delivery (2028-2030)**',
    'phase3 em-dash')

sub('preemptive security outcomes — quantified reduction in exploitable exposure, adversary dwell-time guarantees, autonomous remediation rates — tied to commercial terms',
    'preemptive security outcomes (quantified reduction in exploitable exposure, adversary dwell-time guarantees, autonomous remediation rates) tied to commercial terms',
    'phase3 outcomes em-dash pair')

sub('begin this strategic journey now — in 2025 and 2026 — will have a 3-5 year head start',
    'begin this strategic journey now, in 2025 and 2026, will have a three- to five-year head start',
    'phase3 timing em-dash pair + 3-5')

# BACKGROUND
sub('across five capability pillars — Exposure Management (EXM), Adversary Management',
    'across five capability pillars: Exposure Management (EXM), Adversary Management',
    'background pillars em-dash')

sub('Services & Capabilities (SVC) — each scored on a 1-5 maturity scale',
    'Services & Capabilities (SVC), each scored on a 1-5 maturity scale',
    'background SVC em-dash')

sub('of cybersecurity market participants — from hyperscale platform vendors (Crowd',
    'of cybersecurity market participants, from hyperscale platform vendors (Crowd',
    'background participants em-dash')

# IMPACT
sub('specialize in detection and response — essentially the ADR pillar',
    'specialize in detection and response, essentially the ADR pillar',
    'impact ADR em-dash')

# EVIDENCE
sub('Vendor Assessment, 2025-2026 — 51-vendor evaluation',
    'Vendor Assessment, 2025-2026: 51-vendor evaluation',
    'evidence em-dash')

sub('pillar scores by delivery model — Direct Service',
    'pillar scores by delivery model: Direct Service',
    'evidence model em-dash')

# Write
with open(INPUT, 'w', encoding='utf-8') as f:
    f.write(raw)

remaining = raw.count('\u2014')
print(f'Applied {len(changes)} replacements')
print(f'Em-dashes remaining: {remaining}')
if remaining > 0:
    import re
    for m in re.finditer(r'(.{30})\u2014(.{30})', raw):
        print(f'  ...{m.group(1)}|||{m.group(2)}...')
