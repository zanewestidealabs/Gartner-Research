"""
CNAPP MQ Vendor 1-2 Enrichment Harness.

Reads `CNAPP MQ Vendor 1-1 Researched.json` (heuristic-only, tier_2) and applies
public-source evidence adjustments per sub-pillar (0-5 scale). Each adjustment
carries a citation, fact, magnitude, and confidence so the audit trail is preserved.

Evidence is encoded per vendor in EVIDENCE below. Sub-pillars without evidence
keep their v1.1 score. Status fields are flipped when at least one evidence record
exists for the vendor.

Output: `CNAPP MQ Vendor 1-2 Researched.json` plus a flat ledger
`CNAPP MQ Evidence Ledger.json` for review.

Usage: python _enrich_cnapp_mq_v12.py [--batch BATCH_NAME]
"""
from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "CNAPP MQ Vendor 1-1 Researched.json"
DST = ROOT / "CNAPP MQ Vendor 1-2 Researched.json"
LEDGER = ROOT / "CNAPP MQ Evidence Ledger.json"

# ---------------------------------------------------------------------------
# EVIDENCE: per-vendor list of {sub_pillar, delta, fact, source_url,
#   source_type, confidence}.
# Deltas applied to v1.1 score, clamped [0.0, 5.0].
# Magnitude convention:
#   +/- 0.3 small, 0.6 medium, 1.0 strong, 1.4 transformative.
# ---------------------------------------------------------------------------
BATCHES: dict[str, list[str]] = {
    "batch1": ["AccuKnox", "Aqua Security", "Bitdefender", "Caveonix", "Check Point"],
    "batch2": ["CrowdStrike", "Data Theorem", "Datadog", "Fortinet", "Microsoft"],
    "batch3": ["Orca Security", "Palo Alto Networks", "Qualys", "Rapid7", "SentinelOne"],
    "batch4": ["Snyk", "Sophos", "Sweet Security", "Sysdig", "Tenable"],
    "batch5": ["Trend Micro", "Uptycs", "Upwind", "Wiz"],
}

EVIDENCE: dict[str, list[dict[str, Any]]] = {
    # ----------------------------------------------------- AccuKnox
    "AccuKnox": [
        {"sp": "VIA-01", "delta": +0.3, "fact": "Active product cadence with v3.5 release notes (KnoxCtl, SCA, SPDX support) and 2026 roadmap publication signal continued investment though revenue undisclosed.", "url": "https://accuknox.com/blog/coming-up-in-3-5-release", "src": "vendor_blog", "conf": "med"},
        {"sp": "VIA-03", "delta": +0.4, "fact": "Maintains KubeArmor open-source project (CNCF sandbox) with public GitHub presence; provides organic developer-led pipeline distinct from paid marketing.", "url": "https://github.com/kubearmor/KubeArmor", "src": "github", "conf": "high"},
        {"sp": "MKE-01", "delta": -0.3, "fact": "Limited Tier-1 analyst/press coverage; cited mostly in niche outlets (TheNewStack, Intellyx) rather than DarkReading/SecurityWeek headline coverage.", "url": "https://intellyx.com/2024/08/01/accuknox-comprehensive-cloud-native-security/", "src": "industry_blog", "conf": "med"},
        {"sp": "MKR-01", "delta": +0.5, "fact": "Visible monthly product cadence (Mar-Apr 2026 blog: ClawArmor, AI-SPM roadmap, KnoxCtl) suggests faster release rhythm than peer score implies.", "url": "https://accuknox.com/blog", "src": "vendor_blog", "conf": "high"},
        {"sp": "MKR-03", "delta": +0.4, "fact": "Early mover on AI-SPM/AI-DR/AI-DSPM with published 2026 roadmap covering AI agent and ML pipeline security.", "url": "https://accuknox.com/blog/accuknox-ai-security-platform-roadmap-2026", "src": "vendor_blog", "conf": "high"},
        {"sp": "CXQ-01", "delta": -0.3, "fact": "Listed on Gartner Peer Insights and G2 but with limited review volume relative to leaders.", "url": "https://www.gartner.com/reviews/market/cloud-native-application-protection-platforms/vendor/accuknox", "src": "gartner_peer_insights", "conf": "med"},
        {"sp": "MKU-01", "delta": +0.3, "fact": "Published Mythos critique blog and runtime checklist demonstrate clear point-of-view on runtime-vs-static market direction.", "url": "https://accuknox.com/blog/mythos-production-environment-runtime-enforcement", "src": "vendor_blog", "conf": "med"},
        {"sp": "VIG-01", "delta": +0.4, "fact": "Confirmed offices in Menlo Park CA (HQ), Chennai and Bengaluru India - real cross-region engineering footprint.", "url": "https://accuknox.com/", "src": "vendor_about", "conf": "high"},
        {"sp": "VIG-03", "delta": -0.4, "fact": "FedRAMP / public-sector accreditation not advertised on vendor site footer; geography concentrated US+India.", "url": "https://accuknox.com/", "src": "vendor_about", "conf": "med"},
    ],

    # ----------------------------------------------------- Aqua Security
    "Aqua Security": [
        {"sp": "VIA-01", "delta": +0.8, "fact": "Aqua publicly states it protects '40%+ of the Fortune 100' as of 2025, indicating strong large-enterprise revenue base.", "url": "https://www.aquasec.com/customers/", "src": "vendor_customers", "conf": "high"},
        {"sp": "VIA-02", "delta": +0.6, "fact": "Investor base includes Insight Partners, Lightspeed, TLV, ION Crossover, StepStone - late-stage growth capital with Shlomo Kramer co-founder participation.", "url": "https://www.aquasec.com/about-us/", "src": "vendor_about", "conf": "high"},
        {"sp": "VIA-04", "delta": +0.4, "fact": "Planned CEO/exec transition (co-founders stepping back, Michael Dube CEO, Matthew Richards COO Nov 2025) executed as orderly succession - signal of operational maturity.", "url": "https://www.aquasec.com/news/aqua-security-announces-leadership-transition-as-company-enters-its-next-phase-of-growth/", "src": "press_release", "conf": "high"},
        {"sp": "MKR-01", "delta": +0.7, "fact": "Major 2026 platform pivot to runtime-led 'Aqua Compass' MCP server + Agentic Response + Risk Dashboards (Apr 2026) shows aggressive roadmap velocity.", "url": "https://www.aquasec.com/news/aqua-security-turns_runtime_intelligence_into_action_with_agentic_response_risk_daskboards/", "src": "press_release", "conf": "high"},
        {"sp": "MKR-03", "delta": +0.8, "fact": "Owns Trivy (most popular OSS vulnerability scanner) and 'Trivy Partner Connect' ecosystem (ActiveState, Root) - strong community-driven innovation moat.", "url": "https://www.aquasec.com/news/trivy-partner-connect-root-open-source-security/", "src": "press_release", "conf": "high"},
        {"sp": "MKE-01", "delta": +0.5, "fact": "Forbes 2026 senior-contributor coverage of strategic pivot ('Aqua Security Goes All In On Runtime Protection') indicates Tier-1 PR reach.", "url": "https://www.forbes.com/sites/tonybradley/2026/02/12/aqua-security-goes-all-in-on-runtime-protection/", "src": "tier1_press", "conf": "high"},
        {"sp": "MKE-03", "delta": +0.4, "fact": "CyberSecurity Breakthrough Award 2025 'AI Solution of the Year' for Aqua Secure AI - third-party AI category recognition.", "url": "https://www.aquasec.com/news/cybersecurity-solution-of-the-year-for-artificial-intelligence/", "src": "industry_award", "conf": "med"},
        {"sp": "CXQ-01", "delta": +0.5, "fact": "G2 reviews from Energy/Finance/Software customers; published case studies for GitLab, NCR, Bayad, ThoughtWorks, AIB, Spotnana, Bol.com show breadth of vertical adoption.", "url": "https://www.aquasec.com/customers/", "src": "case_studies", "conf": "high"},
        {"sp": "VIG-03", "delta": +0.6, "fact": "U.S. Federal Government Agency case studies confirm public-sector deployments; Tel Aviv + Burlington MA dual HQ supports global accounts.", "url": "https://www.aquasec.com/customers/federal-government-agency-anonymous-case-study/", "src": "case_study", "conf": "high"},
        {"sp": "MKU-02", "delta": +0.5, "fact": "Forbes commentary cites Aqua's deliberate 'go deep rather than wide' strategy at runtime - articulated differentiation versus full-suite peers.", "url": "https://www.forbes.com/sites/tonybradley/2026/02/12/aqua-security-goes-all-in-on-runtime-protection/", "src": "tier1_press", "conf": "high"},
    ],

    # ----------------------------------------------------- Bitdefender
    "Bitdefender": [
        {"sp": "VIA-01", "delta": +0.9, "fact": "Bitdefender is a privately-held global cybersecurity company with multi-hundred-million revenue base; Vitruvian Partners backing and broad consumer+enterprise revenue diversification.", "url": "https://www.bitdefender.com/en-us/company/", "src": "vendor_company", "conf": "high"},
        {"sp": "VIA-02", "delta": +0.5, "fact": "Profitable with sustained R&D investment; Ferrari F1 multi-year partnership renewed through 2026 indicates marketing budget headroom.", "url": "https://www.automotiveworld.com/news-releases/bitdefender-extends-multi-year-partnership-with-scuderia-ferrari-hp/", "src": "tier2_press", "conf": "med"},
        {"sp": "VIA-04", "delta": +0.4, "fact": "Acquired Mesh Security (June 2025) for email-security capability expansion - active M&A capacity.", "url": "https://www.msspalert.com/news/bitdefender-expands-email-security-with-mesh-acquisition-to-strengthen-xdr-mdr-and-msp-capabilities", "src": "tier2_press", "conf": "high"},
        {"sp": "SLE-01", "delta": +0.6, "fact": "Bitdefender Partner Advantage Network earned CRN 5-Star rating for the 11th consecutive year (March 2026) - exceptional channel breadth.", "url": "https://www.bitdefender.com/en-us/news/bitdefender-partner-advantage-network-earns-crn-5-star-rating-for-eleventh-consecutive-year.html", "src": "press_release", "conf": "high"},
        {"sp": "MKR-01", "delta": +0.5, "fact": "GravityZone Compliance Manager (June 2025), PHASR (April 2025) standalone, Security Data Lake (Nov 2025), Email Security (April 2026) - quarterly major-feature cadence.", "url": "https://www.bitdefender.com/en-us/news/", "src": "press_release_index", "conf": "high"},
        {"sp": "MKE-01", "delta": +0.7, "fact": "Sustained Tier-1 press coverage (Forbes, BleepingComputer, The Hacker News, SecurityWeek, Dark Reading, CSO, ComputerWeekly) on at least monthly basis through 2025-2026.", "url": "https://www.bitdefender.com/en-us/news/", "src": "press_release_index", "conf": "high"},
        {"sp": "MKE-03", "delta": +0.6, "fact": "Named Only Visionary in 2025 Gartner MQ for EPP and 2026 Gartner Peer Insights Customers' Choice for EPP - top analyst recognition (in adjacent endpoint market, validating brand strength).", "url": "https://www.bitdefender.com/en-us/news/bitdefender-named-a-2026-gartner-peer-insights-customers-choice-for-endpoint-protection-platforms.html", "src": "analyst_recognition", "conf": "high"},
        {"sp": "CXQ-01", "delta": +0.4, "fact": "Public case studies (Bruce Auto Group, Cora Systems, Campai BV) plus Gartner Peer Insights Customers' Choice indicate solid customer-experience metrics.", "url": "https://www.bitdefender.com/en-us/business/", "src": "case_studies", "conf": "high"},
        {"sp": "VIG-01", "delta": +0.7, "fact": "Truly global press footprint (German, French, Spanish, Italian, Japanese, Korean, Chinese coverage in 2025-2026) - confirms localized operations.", "url": "https://www.bitdefender.com/en-us/news/", "src": "press_release_index", "conf": "high"},
        {"sp": "VIG-03", "delta": +0.4, "fact": "OVHcloud EU sovereignty partnership (Oct 2025) for EU data sovereignty XDR delivery - signals public sector / regulated industry positioning.", "url": "https://www.channele2e.com/news/bitdefender-brings-eu-data-sovereignty-to-xdr-through-ovhcloud-partnership", "src": "tier2_press", "conf": "high"},
        # Reality check: Bitdefender's CNAPP product (CSPM Plus + CWP) is materially less mature than its EPP/XDR business.
        {"sp": "MKU-03", "delta": -0.4, "fact": "Cloud security ('Secure Your Cloud Posture' / CSPM Plus) is positioned as an extension of GravityZone rather than a CNAPP-pure-play strategy - less articulated CNAPP vision.", "url": "https://www.bitdefender.com/en-us/business/", "src": "vendor_business", "conf": "high"},
        {"sp": "MKR-04", "delta": -0.3, "fact": "CNAPP-specific innovation (CSPM/CWP) less differentiated than endpoint roadmap; runtime cloud features lag pure-play CNAPP vendors.", "url": "https://www.bitdefender.com/en-us/business/", "src": "vendor_business", "conf": "med"},
    ],

    # ----------------------------------------------------- Caveonix
    "Caveonix": [
        {"sp": "VIA-01", "delta": -0.8, "fact": "Caveonix.com domain redirects to cavhq.ai (re-brand pivot) - typical signal of low brand equity / strategic reset rather than steady growth.", "url": "https://www.caveonix.com/about/", "src": "vendor_redirect", "conf": "high"},
        {"sp": "VIA-02", "delta": -0.5, "fact": "No publicly announced funding rounds since 2021 Series A; rebrand without funding announcement suggests constrained runway.", "url": "https://www.cavhq.ai/about/", "src": "vendor_about", "conf": "med"},
        {"sp": "MKR-01", "delta": -0.4, "fact": "No major product release press in 2025-2026 mainstream cyber outlets; press cadence near-silent.", "url": "https://www.cavhq.ai/news", "src": "vendor_news", "conf": "med"},
        {"sp": "MKE-01", "delta": -0.7, "fact": "No 2025-2026 SecurityWeek/DarkReading/The Hacker News byline coverage discoverable - effectively absent from Tier-1 press cycle.", "url": "https://www.cavhq.ai/news", "src": "vendor_news", "conf": "high"},
        {"sp": "MKE-03", "delta": -0.5, "fact": "Not present in 2025 Gartner MQ for CNAPP nor Forrester Wave CNAPP - no recent top-tier analyst recognition.", "url": "https://www.cavhq.ai/", "src": "analyst_absence", "conf": "high"},
        {"sp": "CXQ-01", "delta": -0.4, "fact": "Minimal Gartner Peer Insights / G2 review volume; few publicly named reference customers.", "url": "https://www.cavhq.ai/customers", "src": "vendor_customers", "conf": "med"},
        {"sp": "MKU-02", "delta": +0.3, "fact": "Differentiated focus on hybrid/regulated and federal compliance (FedRAMP/FISMA/CMMC) is a coherent niche positioning despite limited scale.", "url": "https://www.cavhq.ai/", "src": "vendor_about", "conf": "med"},
        {"sp": "VIG-03", "delta": +0.4, "fact": "Federal/DoD compliance specialization (FedRAMP, FISMA, CMMC mappings) is a real vertical specialization.", "url": "https://www.cavhq.ai/", "src": "vendor_about", "conf": "med"},
        {"sp": "VIG-01", "delta": -0.5, "fact": "US-only operational footprint with no announced EMEA/APAC presence.", "url": "https://www.cavhq.ai/", "src": "vendor_about", "conf": "med"},
    ],

    # ----------------------------------------------------- Check Point
    "Check Point": [
        {"sp": "VIA-01", "delta": +1.2, "fact": "Check Point is NASDAQ-listed (CHKP) with ~$2.4B annual revenue and 30+ years of profitable operations - among the most financially stable cyber vendors.", "url": "https://www.checkpoint.com/about-us/investor-relations/", "src": "investor_relations", "conf": "high"},
        {"sp": "VIA-02", "delta": +1.0, "fact": "Strong cash position ($2B+) and active buyback program; CloudGuard line backed by parent's balance sheet.", "url": "https://www.checkpoint.com/about-us/investor-relations/", "src": "investor_relations", "conf": "high"},
        {"sp": "VIA-04", "delta": +0.6, "fact": "Stable executive bench (Nadav Zafrir CEO from Dec 2024) and recent Wiz strategic partnership executed at corp level - mature governance.", "url": "https://www.checkpoint.com/checkpoint-wiz-powering-the-new-era-of-cloud-security/", "src": "press_release", "conf": "high"},
        {"sp": "SLE-01", "delta": +1.0, "fact": "'Over 4,000 cloud customers' with '50% of top 50 Fortune 500' using Check Point - massive installed base advantage.", "url": "https://www.checkpoint.com/cloudguard/", "src": "vendor_product", "conf": "high"},
        {"sp": "SLE-03", "delta": +0.7, "fact": "Mature global channel partner program with named MSP/MSSP, AWS/Azure/GCP partner pages, partner locator.", "url": "https://www.checkpoint.com/partners/channel/", "src": "vendor_partners", "conf": "high"},
        # CNAPP-specific reality check: CloudGuard CNAPP is widely seen as catching up
        {"sp": "MKR-01", "delta": -0.4, "fact": "CloudGuard CNAPP innovation cadence trails pure-play CNAPP vendors; Wiz partnership (rather than organic build-out) acknowledges gap in CNAPP technology depth.", "url": "https://www.checkpoint.com/cloudguard/", "src": "vendor_product", "conf": "high"},
        {"sp": "MKR-03", "delta": -0.3, "fact": "CloudGuard innovation more focused on prevention/WAF/firewall heritage than CNAPP-native primitives like agentless scanning, code-to-cloud graph.", "url": "https://www.checkpoint.com/cloudguard/", "src": "vendor_product", "conf": "med"},
        {"sp": "MKE-01", "delta": +0.7, "fact": "Sustained Tier-1 press coverage as established cyber leader; consistent presence in DarkReading, SecurityWeek, ComputerWeekly.", "url": "https://www.checkpoint.com/press-releases/", "src": "press_release_index", "conf": "high"},
        {"sp": "MKE-03", "delta": +0.4, "fact": "Recognized in 2025 Gartner Market Guide for Cloud Web Application and API Security (WAAP-adjacent), GigaOM Cloud Network Security Leader.", "url": "https://www.checkpoint.com/cloudguard/", "src": "analyst_report", "conf": "high"},
        {"sp": "CXQ-01", "delta": +0.4, "fact": "4.4-star G2 rating and 4.3-star PeerSpot rating for CloudGuard cited on product page.", "url": "https://www.checkpoint.com/cloudguard/", "src": "vendor_product", "conf": "med"},
        {"sp": "MKU-01", "delta": -0.3, "fact": "Cloud security messaging anchored in 'prevention-first network heritage' rather than developer-first / shift-left CNAPP vision; Wiz partnership effectively outsources CNAPP-native vision.", "url": "https://www.checkpoint.com/cloudguard/", "src": "vendor_product", "conf": "high"},
        {"sp": "VIG-01", "delta": +1.0, "fact": "10+ language localizations (EN/ES/FR/DE/IT/PT/JA/ZH/KO/TW) and global office network - true tier-1 global footprint.", "url": "https://www.checkpoint.com/cloudguard/", "src": "vendor_product", "conf": "high"},
        {"sp": "VIG-03", "delta": +0.6, "fact": "Federal Government and Financial Services industry pages indicate active public-sector and regulated-vertical sales motion.", "url": "https://www.checkpoint.com/industry/government-federal-security/", "src": "vendor_industry", "conf": "high"},
    ],

    # ====================================================== BATCH 2 ======================================================

    # ----------------------------------------------------- CrowdStrike
    "CrowdStrike": [
        {"sp": "VIA-01", "delta": +1.4, "fact": "NASDAQ:CRWD with $4B+ ARR (FY25), publicly traded with strong cash position - tier-1 financial scale.", "url": "https://ir.crowdstrike.com/", "src": "investor_relations", "conf": "high"},
        {"sp": "VIA-02", "delta": +1.0, "fact": "33 cloud modules across multiple security markets including Falcon Cloud Security; consistent profitability and FCF generation.", "url": "https://ir.crowdstrike.com/", "src": "investor_relations", "conf": "high"},
        {"sp": "VIA-04", "delta": +0.6, "fact": "Mature exec team led by George Kurtz (founder/CEO since 2011), public board governance, sustained investor relations cadence.", "url": "https://www.crowdstrike.com/about-crowdstrike/executive-team/", "src": "vendor_about", "conf": "high"},
        {"sp": "SLE-01", "delta": +1.0, "fact": "Falcon Cloud Security customers include Vodafone Oman, Avalon Healthcare (100M members), Monvia - large enterprise references across regions.", "url": "https://www.crowdstrike.com/platform/cloud-security/", "src": "case_studies", "conf": "high"},
        {"sp": "SLE-03", "delta": +0.7, "fact": "Named Google Cloud Security Partner of the Year (2025, 2026 - Infrastructure Security) - top-tier hyperscaler channel position.", "url": "https://www.crowdstrike.com/en-us/press-releases/crowdstrike-named-google-cloud-security-partner-of-the-year-second-consecutive-year/", "src": "press_release", "conf": "high"},
        {"sp": "MKR-01", "delta": +0.8, "fact": "Quarterly Falcon platform releases with consistent cloud-security innovations: Application Explorer, Adversary Risk Intel, Timeline Explorer, Real-Time CDR for Google Cloud (April 2026).", "url": "https://www.crowdstrike.com/en-us/blog/crowdstrike-advances-cnapp-with-industry-first-adversary-informed-risk-prioritization/", "src": "vendor_blog", "conf": "high"},
        {"sp": "MKR-03", "delta": +0.7, "fact": "AI-SPM, AI workload security, agentless+agent unified architecture, code-to-runtime ASPM - full CNAPP innovation stack.", "url": "https://www.crowdstrike.com/en-us/platform/cloud-security/ai-spm/", "src": "vendor_product", "conf": "high"},
        {"sp": "MKR-04", "delta": +0.8, "fact": "Validated 100% detection/protection in 2025 MITRE ATT&CK Cloud Evaluation - independent benchmark of CNAPP runtime efficacy.", "url": "https://www.crowdstrike.com/en-us/resources/reports/mitre-2025/", "src": "third_party_eval", "conf": "high"},
        {"sp": "MKE-01", "delta": +1.0, "fact": "Sustained Tier-1 press coverage; multiple weekly press releases on CrowdStrike newsroom; regular DarkReading/SecurityWeek coverage.", "url": "https://www.crowdstrike.com/en-us/press-releases/", "src": "press_release_index", "conf": "high"},
        {"sp": "MKE-03", "delta": +1.0, "fact": "Named Leader in IDC MarketScape Worldwide CNAPP and Frost Radar CNAPP Leader for 4 consecutive times (2023-2026).", "url": "https://www.crowdstrike.com/en-us/press-releases/crowdstrike-named-frost-radar-leader-in-cnapp-fourth-consecutive-time/", "src": "analyst_recognition", "conf": "high"},
        {"sp": "CXQ-01", "delta": +0.8, "fact": "Forrester TEI 2026: 264% ROI over 3 years, payback under 6 months for Falcon Cloud Security; Gartner Peer Insights Customers' Choice in adjacent markets.", "url": "https://www.crowdstrike.com/en-us/press-releases/crowdstrike-falcon-cloud-security-delivered-264-percent-roi-over-three-years/", "src": "third_party_study", "conf": "high"},
        {"sp": "MKU-01", "delta": +0.7, "fact": "Articulated 'runtime-first' CNAPP vision and 'stop the breach' positioning; Project QuiltWorks frontier-AI coalition (April 2026) signals strategic thought leadership.", "url": "https://www.crowdstrike.com/en-us/press-releases/crowdstrike-launches-project-quiltworks/", "src": "press_release", "conf": "high"},
        {"sp": "VIG-01", "delta": +1.0, "fact": "JAPAC partner symposium in Da Nang Vietnam (April 2026), Korean/Japanese coverage, true global presence with regional press.", "url": "https://www.crowdstrike.com/en-us/press-releases/crowdstrike-recognizes-2026-japac-partner-award-winners-at-annual-partner-symposium/", "src": "press_release", "conf": "high"},
        {"sp": "VIG-03", "delta": +0.7, "fact": "FedRAMP Authorized for Falcon platform; well-established US public-sector and federal customers.", "url": "https://www.crowdstrike.com/en-us/products/", "src": "vendor_compliance", "conf": "high"},
    ],

    # ----------------------------------------------------- Data Theorem
    "Data Theorem": [
        {"sp": "VIA-01", "delta": +0.4, "fact": "Privately-held with mature customer base (2.8B+ end-users covered, 5 of top 7 largest banks) - modest size but high-quality revenue.", "url": "https://www.datatheorem.com/customers", "src": "vendor_customers", "conf": "high"},
        {"sp": "SLE-01", "delta": +0.6, "fact": "Marquee enterprise customers include Cisco Duo, Evernote, Coinbase, Salesforce, Goldman Sachs, Aetna, Atlassian, eBay, DocuSign, Box, Verizon, VMware.", "url": "https://www.datatheorem.com/customers", "src": "vendor_customers", "conf": "high"},
        {"sp": "MKR-03", "delta": +0.7, "fact": "Ranked #1 in Cloud Native Apps in 2025 Gartner Critical Capabilities for Application Security Testing - top-tier capability in CNAPP-adjacent AST domain.", "url": "https://www.datatheorem.com/resources/blog/data-theorem-ranked-1-in-cloud-native-api-security-2025-gartner-ast/", "src": "analyst_recognition", "conf": "high"},
        {"sp": "MKR-01", "delta": +0.5, "fact": "Released AI Governance, AppSec AI Agent products in 2025-2026; consistent product innovation across mobile/API/cloud/code surfaces.", "url": "https://www.datatheorem.com/products", "src": "vendor_product", "conf": "high"},
        # Reality-check: Data Theorem is API/mobile-led; CNAPP breadth is narrower than full-stack peers
        {"sp": "MKR-04", "delta": -0.4, "fact": "Cloud Secure module is one of seven products; CNAPP is not the central platform - breadth limited vs full-stack CNAPP vendors.", "url": "https://www.datatheorem.com/products", "src": "vendor_product", "conf": "high"},
        {"sp": "MKU-03", "delta": -0.3, "fact": "Strategic narrative led by Mobile/API security; CNAPP positioning is secondary to AppSec messaging.", "url": "https://www.datatheorem.com/about-us", "src": "vendor_about", "conf": "med"},
        {"sp": "MKE-03", "delta": +0.6, "fact": "Gartner endorsement quote on customer page from Neil MacDonald (Gartner Fellow) on CNAPP narrative - strong analyst-relations standing.", "url": "https://www.datatheorem.com/customers/gartner", "src": "analyst_quote", "conf": "med"},
        {"sp": "CXQ-01", "delta": +0.4, "fact": "Multiple deep-dive customer case studies (Shippo - 138 issues closed, Wildflower - 73 issues, Evernote - 105 issues) with named CISO endorsements.", "url": "https://www.datatheorem.com/customers", "src": "case_studies", "conf": "high"},
        {"sp": "VIG-01", "delta": -0.3, "fact": "US-centric brand presence; limited evidence of localized international press/marketing relative to peers.", "url": "https://www.datatheorem.com/about-us", "src": "vendor_about", "conf": "med"},
    ],

    # ----------------------------------------------------- Datadog
    "Datadog": [
        {"sp": "VIA-01", "delta": +1.4, "fact": "NASDAQ:DDOG, joined S&P 500 in July 2025; Forbes Global 2000; multi-billion ARR with consistent growth and profitability.", "url": "https://investors.datadoghq.com/news-releases/news-release-details/datadog-joins-sp-500-index", "src": "press_release", "conf": "high"},
        {"sp": "VIA-02", "delta": +1.0, "fact": "Multiple convertible debt offerings ($870M Dec 2024, $650M May 2020) plus strong FCF; sustained M&A capacity (Eppo, Metaplane 2025).", "url": "https://investors.datadoghq.com/news-releases/news-release-details/datadog-acquires-eppo-expand-its-ai-product-analytics", "src": "press_release", "conf": "high"},
        {"sp": "SLE-01", "delta": +0.8, "fact": "Reached 1,000 platform integrations in 2025; Flight Centre Travel Group, Mendix, and many global enterprise customer announcements.", "url": "https://investors.datadoghq.com/news-releases/news-release-details/datadog-reaches-1000-integrations-customers-continue-observe", "src": "press_release", "conf": "high"},
        {"sp": "SLE-03", "delta": +0.7, "fact": "2024 Google Cloud Technology Partner of the Year for AppDev and Marketplace; AWS Strategic Collaboration Agreement (Dec 2025) expanded.", "url": "https://investors.datadoghq.com/news-releases/news-release-details/datadog-receives-2024-google-cloud-technology-partner-year", "src": "press_release", "conf": "high"},
        {"sp": "MKR-01", "delta": +0.8, "fact": "DASH conference releases dozens of products annually; Cloud Security Management (CNAPP), Cloud SIEM, Bits AI Security Analyst (Mar 2026), MCP Server (Mar 2026) - high cadence.", "url": "https://investors.datadoghq.com/news-releases", "src": "press_release_index", "conf": "high"},
        {"sp": "MKR-03", "delta": +0.6, "fact": "Bits AI Security Analyst reduces threat investigation by 98%; LLM Observability, AI Security extensions show CNAPP+AI innovation depth.", "url": "https://investors.datadoghq.com/news-releases/news-release-details/bits-ai-security-analyst-reduces-threat-investigation-time-98", "src": "press_release", "conf": "high"},
        {"sp": "MKE-01", "delta": +1.0, "fact": "Sustained Tier-1 press cadence; investor coverage by Forbes/Bloomberg; weekly press releases.", "url": "https://investors.datadoghq.com/news-releases", "src": "press_release_index", "conf": "high"},
        {"sp": "MKE-03", "delta": +0.7, "fact": "Named Leader in 2025 Gartner MQ for Observability Platforms, 2025 MQ for Digital Experience Monitoring, AIOps Leader (Forrester) - strong cross-category analyst standing (CNAPP-adjacent).", "url": "https://investors.datadoghq.com/news-releases/news-release-details/datadog-named-leader-2025-gartnerr-magic-quadranttm", "src": "analyst_recognition", "conf": "high"},
        {"sp": "CXQ-01", "delta": +0.6, "fact": "Gartner Peer Insights Customers' Choice multiple years (APM, IT Infra Monitoring); breadth of certified case studies.", "url": "https://investors.datadoghq.com/news-releases/news-release-details/datadog-recognized-2020-gartner-peer-insights-customers-choice-0", "src": "analyst_recognition", "conf": "high"},
        {"sp": "VIG-01", "delta": +0.8, "fact": "Data centers in US, EU (Germany), Japan, Australia/NZ (2025); IRAP Protected status Australia (Oct 2025) - true global region footprint.", "url": "https://investors.datadoghq.com/news-releases/news-release-details/datadog-achieves-irap-protected-status-australia", "src": "press_release", "conf": "high"},
        {"sp": "VIG-03", "delta": +0.7, "fact": "FedRAMP Moderate authorized; FedRAMP High In Process (May 2025); GovRAMP High In Process (Aug 2025) - escalating federal commitment.", "url": "https://investors.datadoghq.com/news-releases/news-release-details/datadog-government-achieves-fedrampr-high-process-status-support", "src": "press_release", "conf": "high"},
        # Reality-check: Datadog CNAPP is observability-led; security purists may view as 'good-enough' CNAPP
        {"sp": "MKU-03", "delta": -0.3, "fact": "CNAPP messaging anchored to observability platform; Cloud Security Management is one capability among many vs pure-play CNAPP focus.", "url": "https://investors.datadoghq.com/news-releases/news-release-details/datadog-launches-cloud-security-management-provide-cloud-native", "src": "press_release", "conf": "med"},
    ],

    # ----------------------------------------------------- Fortinet
    "Fortinet": [
        {"sp": "VIA-01", "delta": +1.4, "fact": "NASDAQ:FTNT with $5B+ annual revenue and 30+ years of profitable operations - tier-1 financial scale.", "url": "https://investor.fortinet.com/", "src": "investor_relations", "conf": "high"},
        {"sp": "VIA-02", "delta": +1.0, "fact": "Strong balance sheet enabled $2.4B Lacework acquisition (Aug 2024) creating FortiCNAPP - dedicated CNAPP capability via M&A.", "url": "https://www.fortinet.com/products/forticnapp", "src": "vendor_product", "conf": "high"},
        {"sp": "VIA-04", "delta": +0.5, "fact": "Long-tenured CEO Ken Xie (founder), public board governance, sustained investor disclosures.", "url": "https://investor.fortinet.com/", "src": "investor_relations", "conf": "high"},
        {"sp": "SLE-01", "delta": +0.8, "fact": "FortiCNAPP customer references include Coveo, Careem, Monolithic Power Systems, Grupo Clariens - global enterprise base.", "url": "https://www.fortinet.com/products/forticnapp", "src": "case_studies", "conf": "high"},
        {"sp": "SLE-03", "delta": +1.0, "fact": "2026 Google Cloud Partner of the Year Award for Workload Security; deep AWS/Azure/GCP/OCI partnerships.", "url": "https://www.fortinet.com/corporate/about-us/newsroom/press-releases/2026/fortinet-wins-2026-google-cloud-partner-of-the-year-award-for-workload-security", "src": "press_release", "conf": "high"},
        {"sp": "MKR-04", "delta": +0.6, "fact": "2025 SC Award - Best Cloud Workload Protection Solution for FortiCNAPP - third-party CNAPP-specific recognition.", "url": "https://www.scworld.com/news/sc-award-winners-2025-fortinet-best-cloud-workload-protection-solution", "src": "industry_award", "conf": "high"},
        {"sp": "MKE-01", "delta": +1.0, "fact": "Sustained Tier-1 press coverage; multiple major announcements monthly; Fortinet 2026 Global Threat Landscape Report receives broad pickup.", "url": "https://www.fortinet.com/corporate/about-us/newsroom/press-releases", "src": "press_release_index", "conf": "high"},
        {"sp": "MKE-03", "delta": +0.6, "fact": "Lacework historical positioning as Visionary in Gartner CNAPP MQ; Fortinet broadly recognized as Leader in adjacent Gartner MQs (NGFW, SD-WAN).", "url": "https://www.fortinet.com/corporate/about-us/recognition", "src": "analyst_recognition", "conf": "high"},
        {"sp": "VIG-01", "delta": +1.0, "fact": "Truly global vendor with offices/operations across all geos; localized partnerships (Juventus FC, FC Barcelona, PGA Americas) signal global brand investment.", "url": "https://www.fortinet.com/corporate/about-us/about-us", "src": "vendor_about", "conf": "high"},
        {"sp": "VIG-03", "delta": +0.7, "fact": "Fortinet has FedRAMP authorizations across multiple products; long history serving public sector globally.", "url": "https://www.fortinet.com/corporate/about-us/product-certifications", "src": "vendor_compliance", "conf": "high"},
        # Reality check: FortiCNAPP is post-acquisition integration; CNAPP is not Fortinet's historical strength
        {"sp": "MKU-03", "delta": -0.4, "fact": "FortiCNAPP is a recently-integrated Lacework acquisition; CNAPP-pure-play vision still positioned as part of Fortinet Security Fabric rather than standalone strategy.", "url": "https://www.fortinet.com/products/forticnapp", "src": "vendor_product", "conf": "high"},
        {"sp": "MKR-01", "delta": -0.3, "fact": "FortiCNAPP roadmap velocity post-acquisition unclear vs pre-acquisition Lacework; integration into Fortinet Security Fabric in progress.", "url": "https://www.fortinet.com/products/forticnapp", "src": "vendor_product", "conf": "med"},
    ],

    # ----------------------------------------------------- Microsoft
    "Microsoft": [
        {"sp": "VIA-01", "delta": +1.4, "fact": "NASDAQ:MSFT - one of the world's largest companies by market cap; security business reportedly $20B+ ARR; Defender for Cloud at hyperscale within Azure ecosystem.", "url": "https://www.microsoft.com/en-us/investor/", "src": "investor_relations", "conf": "high"},
        {"sp": "VIA-02", "delta": +1.4, "fact": "Effectively unlimited R&D capacity; Defender for Cloud benefits from Microsoft Security R&D budget that surpasses entire CNAPP market combined.", "url": "https://www.microsoft.com/en-us/security/business/cloud-security/microsoft-defender-cloud", "src": "vendor_product", "conf": "high"},
        {"sp": "VIA-04", "delta": +0.8, "fact": "Public board governance, mature SLT, decades of operational discipline.", "url": "https://www.microsoft.com/en-us/investor/", "src": "investor_relations", "conf": "high"},
        {"sp": "SLE-01", "delta": +1.4, "fact": "Defender for Cloud auto-bundled with Azure subscriptions; default coverage gives massive installed base across Fortune 500.", "url": "https://www.microsoft.com/en-us/security/business/cloud-security/microsoft-defender-cloud", "src": "vendor_product", "conf": "high"},
        {"sp": "SLE-03", "delta": +1.0, "fact": "Microsoft partner ecosystem (Microsoft Partner Network, MISA - Microsoft Intelligent Security Association) is the largest in cybersecurity.", "url": "https://www.microsoft.com/en-us/security/business/intelligence", "src": "vendor_partners", "conf": "high"},
        {"sp": "MKR-03", "delta": +0.6, "fact": "Defender for Cloud covers AWS/Azure/GCP/on-prem with multi-cloud CSPM, CWPP, DSPM, AI-SPM - broad CNAPP feature footprint.", "url": "https://www.microsoft.com/en-us/security/business/cloud-security/microsoft-defender-cloud", "src": "vendor_product", "conf": "high"},
        {"sp": "MKE-01", "delta": +1.4, "fact": "Microsoft Security blog publishes weekly; Tier-1 press coverage virtually guaranteed across all major outlets globally.", "url": "https://www.microsoft.com/en-us/security/blog/", "src": "press_release_index", "conf": "high"},
        {"sp": "MKE-03", "delta": +0.7, "fact": "Named Leader in 2024 Forrester Wave for CNAPP; Leader across 6+ adjacent Gartner MQs (EPP, SIEM, Identity, Email Security).", "url": "https://www.microsoft.com/en-us/security/business/security-101/what-is-cnapp", "src": "analyst_recognition", "conf": "high"},
        {"sp": "CXQ-01", "delta": +0.6, "fact": "Defender for Cloud has high adoption due to Azure default-on positioning; Gartner Peer Insights ratings broadly positive.", "url": "https://www.gartner.com/reviews/market/cloud-native-application-protection-platforms/vendor/microsoft", "src": "gartner_peer_insights", "conf": "high"},
        {"sp": "VIG-01", "delta": +1.4, "fact": "Microsoft has direct sales presence in 100+ countries with localized products in 100+ languages - unmatched global footprint.", "url": "https://www.microsoft.com/en-us/about", "src": "vendor_about", "conf": "high"},
        {"sp": "VIG-03", "delta": +1.0, "fact": "FedRAMP High Authorized for Azure Government and Defender for Cloud; DoD IL5/IL6 authorizations; deep public-sector worldwide.", "url": "https://learn.microsoft.com/en-us/azure/compliance/", "src": "vendor_compliance", "conf": "high"},
        # Reality check: Defender for Cloud has been criticized as 'good enough' but not best-of-breed CNAPP
        {"sp": "MKR-04", "delta": -0.3, "fact": "Independent reviews and Gartner commentary often describe Defender for Cloud as 'capable but not best-of-breed CNAPP' vs Wiz/Palo Alto/Orca; multi-cloud parity to AWS/GCP still maturing.", "url": "https://www.gartner.com/reviews/market/cloud-native-application-protection-platforms/vendor/microsoft", "src": "gartner_peer_insights", "conf": "med"},
        {"sp": "MKU-01", "delta": -0.3, "fact": "CNAPP messaging anchored within broader Microsoft Security platform narrative rather than CNAPP-pure-play vision.", "url": "https://www.microsoft.com/en-us/security/business/cloud-security/microsoft-defender-cloud", "src": "vendor_product", "conf": "med"},
    ],

    # ====================================================== BATCH 3 ======================================================

    # ----------------------------------------------------- Orca Security
    "Orca Security": [
        {"sp": "VIA-01", "delta": +0.8, "fact": "Privately-held; raised $632M+ across funding rounds (Series A-D) reaching $1.8B+ valuation; one of CNAPP-pure-play category leaders.", "url": "https://orca.security/about/", "src": "vendor_about", "conf": "high"},
        {"sp": "VIA-02", "delta": +0.6, "fact": "Investors include CapitalG, GGV Capital, ICONIQ Growth, Redpoint, Temasek - tier-1 growth capital.", "url": "https://orca.security/about/", "src": "vendor_about", "conf": "high"},
        {"sp": "SLE-01", "delta": +0.7, "fact": "Customer base includes Lyft, Robinhood, Unity, Live Nation, Sisense - high-growth digital-native enterprises.", "url": "https://orca.security/customers/", "src": "vendor_customers", "conf": "high"},
        {"sp": "MKR-01", "delta": +0.8, "fact": "SideScanning patented technology pioneered agentless cloud security; consistent product innovation in agentless CSPM/CWPP/CDR/AI-SPM.", "url": "https://orca.security/platform/", "src": "vendor_product", "conf": "high"},
        {"sp": "MKR-03", "delta": +0.7, "fact": "Innovator in agentless approach, AI-SPM, attack-path analysis, unified data model - sets pace for CNAPP innovation.", "url": "https://orca.security/platform/", "src": "vendor_product", "conf": "high"},
        {"sp": "MKE-03", "delta": +0.8, "fact": "Named Leader in Forrester Wave for CNAPP 2024; Visionary/Leader in Gartner-adjacent assessments; recognized as CNAPP category co-creator.", "url": "https://orca.security/resources/analyst-reports/", "src": "analyst_recognition", "conf": "high"},
        {"sp": "MKE-01", "delta": +0.7, "fact": "Strong Tier-1 press presence on CNAPP topics; thought-leadership through Orca Cloud Risk Reports.", "url": "https://orca.security/resources/blog/", "src": "press_release_index", "conf": "high"},
        {"sp": "MKU-01", "delta": +0.8, "fact": "Articulated 'agentless-first' CNAPP vision and SideScanning category positioning - clear strategic narrative.", "url": "https://orca.security/platform/sidescanning-technology/", "src": "vendor_vision", "conf": "high"},
        {"sp": "CXQ-01", "delta": +0.6, "fact": "High Gartner Peer Insights ratings (4.7+ stars); customer testimonials from named enterprise CISOs.", "url": "https://www.gartner.com/reviews/market/cloud-native-application-protection-platforms/vendor/orca-security", "src": "gartner_peer_insights", "conf": "high"},
        {"sp": "VIG-01", "delta": +0.5, "fact": "Tel Aviv + Portland HQ; offices across NA, EMEA, APAC; localized customer base in EU and Japan.", "url": "https://orca.security/about/", "src": "vendor_about", "conf": "high"},
    ],

    # ----------------------------------------------------- Palo Alto Networks
    "Palo Alto Networks": [
        {"sp": "VIA-01", "delta": +1.4, "fact": "NYSE:PANW with $8B+ annual revenue; Prisma Cloud is one of the largest CNAPP businesses by revenue.", "url": "https://investors.paloaltonetworks.com/", "src": "investor_relations", "conf": "high"},
        {"sp": "VIA-02", "delta": +1.0, "fact": "Strong balance sheet enabled $700M+ in CNAPP-related M&A: Twistlock, RedLock, Bridgecrew, Cider Security, Dig Security, Talon - aggressive consolidation play.", "url": "https://www.paloaltonetworks.com/prisma/cloud", "src": "vendor_product", "conf": "high"},
        {"sp": "VIA-04", "delta": +0.6, "fact": "Mature exec team (Nikesh Arora CEO since 2018); public board governance; consistent investor disclosures.", "url": "https://investors.paloaltonetworks.com/", "src": "investor_relations", "conf": "high"},
        {"sp": "SLE-01", "delta": +1.0, "fact": "Prisma Cloud customer base spans Fortune 500 and global 2000; named customers include Accenture, NTT DATA, Bridgewater Associates.", "url": "https://www.paloaltonetworks.com/prisma/cloud", "src": "vendor_customers", "conf": "high"},
        {"sp": "MKR-01", "delta": +0.7, "fact": "Quarterly Prisma Cloud releases; Code-to-Cloud platform unification; AI Runtime Security integration.", "url": "https://www.paloaltonetworks.com/prisma/cloud", "src": "vendor_product", "conf": "high"},
        {"sp": "MKR-04", "delta": +0.7, "fact": "Most-comprehensive code-to-cloud feature footprint via stacked acquisitions; deep integration with Prisma Access/Cortex platforms.", "url": "https://www.paloaltonetworks.com/prisma/cloud", "src": "vendor_product", "conf": "high"},
        {"sp": "MKE-03", "delta": +1.0, "fact": "Named Leader in Forrester Wave CNAPP 2024; consistently top-positioned in analyst CNAPP reports.", "url": "https://www.paloaltonetworks.com/resources/research", "src": "analyst_recognition", "conf": "high"},
        {"sp": "MKE-01", "delta": +1.0, "fact": "Sustained Tier-1 press coverage; one of most-cited cybersecurity vendors globally.", "url": "https://www.paloaltonetworks.com/company/press", "src": "press_release_index", "conf": "high"},
        {"sp": "VIG-01", "delta": +1.0, "fact": "Global footprint across 150+ countries with localized GTM in EMEA, APJ, LATAM.", "url": "https://www.paloaltonetworks.com/company", "src": "vendor_about", "conf": "high"},
        {"sp": "VIG-03", "delta": +0.8, "fact": "FedRAMP High Authorized; deep US Federal customer base; IL5 authorization for DoD.", "url": "https://www.paloaltonetworks.com/industry/government", "src": "vendor_compliance", "conf": "high"},
        # Reality check: Prisma Cloud's bolt-on integration is a known weakness
        {"sp": "MKU-03", "delta": -0.3, "fact": "Prisma Cloud has been criticized in Gartner Peer Insights for integration friction across acquired components and complex pricing.", "url": "https://www.gartner.com/reviews/market/cloud-native-application-protection-platforms/vendor/palo-alto-networks", "src": "gartner_peer_insights", "conf": "med"},
    ],

    # ----------------------------------------------------- Qualys
    "Qualys": [
        {"sp": "VIA-01", "delta": +0.8, "fact": "NASDAQ:QLYS with $600M+ annual revenue and consistent profitability; long-tenured public company.", "url": "https://investor.qualys.com/", "src": "investor_relations", "conf": "high"},
        {"sp": "VIA-04", "delta": +0.5, "fact": "Mature public-company governance; Sumedh Thakar CEO; consistent investor disclosures.", "url": "https://investor.qualys.com/", "src": "investor_relations", "conf": "high"},
        {"sp": "SLE-01", "delta": +0.6, "fact": "10,000+ customer base from VMDR heritage; expanding TotalCloud CNAPP into existing accounts.", "url": "https://www.qualys.com/about/", "src": "vendor_about", "conf": "high"},
        {"sp": "MKR-03", "delta": +0.4, "fact": "TotalCloud combines CSPM, CWPP, IaC scanning, and FlexScan agentless approach - solid CNAPP feature breadth from VRM heritage.", "url": "https://www.qualys.com/apps/totalcloud/", "src": "vendor_product", "conf": "high"},
        {"sp": "MKE-01", "delta": +0.5, "fact": "Established Tier-1 press relationships; regular SecurityWeek/DarkReading coverage on threat-research and platform updates.", "url": "https://www.qualys.com/company/newsroom/", "src": "press_release_index", "conf": "high"},
        {"sp": "MKE-03", "delta": +0.4, "fact": "Named Leader in Gartner MQ for VRM/Vulnerability Assessment; CNAPP-adjacent recognition transferable.", "url": "https://www.qualys.com/research/analyst-reports/", "src": "analyst_recognition", "conf": "high"},
        {"sp": "VIG-01", "delta": +0.5, "fact": "Global presence with offices in NA/EMEA/APJ; localized data centers across 12+ regions.", "url": "https://www.qualys.com/company/", "src": "vendor_about", "conf": "high"},
        {"sp": "VIG-03", "delta": +0.6, "fact": "FedRAMP Moderate Authorized for Qualys Cloud Platform; broad federal customer base.", "url": "https://www.qualys.com/solutions/government/", "src": "vendor_compliance", "conf": "high"},
        # CNAPP-specific reality check: Qualys CNAPP is newer entry vs pure-plays
        {"sp": "MKR-01", "delta": -0.3, "fact": "TotalCloud CNAPP was launched comparatively late (2022-2023); innovation cadence trails pure-plays like Wiz/Orca.", "url": "https://www.qualys.com/apps/totalcloud/", "src": "vendor_product", "conf": "med"},
        {"sp": "MKU-01", "delta": -0.3, "fact": "Strategic narrative anchored to VRM/Exposure Management rather than CNAPP-pure-play vision.", "url": "https://www.qualys.com/", "src": "vendor_homepage", "conf": "med"},
    ],

    # ----------------------------------------------------- Rapid7
    "Rapid7": [
        {"sp": "VIA-01", "delta": +0.7, "fact": "NASDAQ:RPD with $800M+ annual revenue; established public cyber vendor.", "url": "https://investors.rapid7.com/", "src": "investor_relations", "conf": "high"},
        {"sp": "VIA-04", "delta": +0.5, "fact": "Public-company governance; long-tenured CEO Corey Thomas; consistent investor reporting.", "url": "https://investors.rapid7.com/", "src": "investor_relations", "conf": "high"},
        {"sp": "SLE-01", "delta": +0.5, "fact": "11,000+ customers globally; InsightCloudSec and Insight platform covering broad security ops scope.", "url": "https://www.rapid7.com/about/", "src": "vendor_about", "conf": "high"},
        {"sp": "MKR-03", "delta": +0.3, "fact": "InsightCloudSec (DivvyCloud acquisition) provides CNAPP CSPM/CIEM/IaC; integrated with broader Insight platform (InsightVM, InsightIDR).", "url": "https://www.rapid7.com/products/insightcloudsec/", "src": "vendor_product", "conf": "high"},
        {"sp": "MKE-01", "delta": +0.6, "fact": "Sustained Tier-1 press; Rapid7 Threat Report widely cited; consistent SecurityWeek/DarkReading coverage.", "url": "https://www.rapid7.com/about/press-releases/", "src": "press_release_index", "conf": "high"},
        {"sp": "VIG-01", "delta": +0.4, "fact": "Global presence with HQ Boston, offices across NA/EMEA/APJ.", "url": "https://www.rapid7.com/about/", "src": "vendor_about", "conf": "high"},
        {"sp": "VIG-03", "delta": +0.4, "fact": "FedRAMP authorizations across InsightVM and InsightIDR; meaningful federal presence.", "url": "https://www.rapid7.com/solutions/government/", "src": "vendor_compliance", "conf": "high"},
        # Reality check: Rapid7 CNAPP is secondary to MDR/XDR
        {"sp": "MKU-03", "delta": -0.4, "fact": "Strategic narrative led by MDR/SOC modernization; InsightCloudSec is one product within broader Insight portfolio rather than CNAPP-pure-play focus.", "url": "https://www.rapid7.com/", "src": "vendor_homepage", "conf": "high"},
        {"sp": "MKR-01", "delta": -0.3, "fact": "InsightCloudSec roadmap velocity reportedly trails CNAPP pure-plays; recent layoffs and restructuring (2024) raise execution-velocity concerns.", "url": "https://www.rapid7.com/products/insightcloudsec/", "src": "vendor_product", "conf": "med"},
    ],

    # ----------------------------------------------------- SentinelOne
    "SentinelOne": [
        {"sp": "VIA-01", "delta": +0.8, "fact": "NYSE:S with $700M+ annual revenue and growing; well-funded public cyber vendor.", "url": "https://investors.sentinelone.com/", "src": "investor_relations", "conf": "high"},
        {"sp": "VIA-02", "delta": +0.6, "fact": "Strong cash position; PingSafe acquisition (Jan 2024) gave SentinelOne dedicated CNAPP capability (Singularity Cloud Security).", "url": "https://www.sentinelone.com/press/sentinelone-acquires-pingsafe/", "src": "press_release", "conf": "high"},
        {"sp": "SLE-01", "delta": +0.6, "fact": "11,000+ customers globally; Singularity platform spans endpoint/cloud/identity/data.", "url": "https://www.sentinelone.com/about/", "src": "vendor_about", "conf": "high"},
        {"sp": "MKR-01", "delta": +0.5, "fact": "Singularity Cloud Security with PingSafe-based agentless CNAPP launched 2024; AI-SPM extensions through 2025-2026.", "url": "https://www.sentinelone.com/platform/cloud-security/", "src": "vendor_product", "conf": "high"},
        {"sp": "MKE-01", "delta": +0.7, "fact": "Sustained Tier-1 press coverage; SentinelLabs threat research widely cited.", "url": "https://www.sentinelone.com/press/", "src": "press_release_index", "conf": "high"},
        {"sp": "MKE-03", "delta": +0.5, "fact": "Named Leader in Gartner MQ for EPP; CNAPP-adjacent analyst credibility transferable.", "url": "https://www.sentinelone.com/resources/", "src": "analyst_recognition", "conf": "high"},
        {"sp": "VIG-01", "delta": +0.5, "fact": "Global presence; HQ Mountain View; offices across NA/EMEA/APJ.", "url": "https://www.sentinelone.com/about/", "src": "vendor_about", "conf": "high"},
        {"sp": "VIG-03", "delta": +0.5, "fact": "FedRAMP High Authorized; broad federal customer base.", "url": "https://www.sentinelone.com/government/", "src": "vendor_compliance", "conf": "high"},
        # Reality check: Singularity Cloud Security is recent integration
        {"sp": "MKR-04", "delta": -0.3, "fact": "Singularity Cloud Security is recently-acquired PingSafe technology; full platform integration with Singularity Data Lake still maturing.", "url": "https://www.sentinelone.com/platform/cloud-security/", "src": "vendor_product", "conf": "med"},
        {"sp": "MKU-03", "delta": -0.3, "fact": "Strategic narrative led by autonomous-XDR/endpoint heritage; CNAPP positioned as platform extension rather than pure-play.", "url": "https://www.sentinelone.com/", "src": "vendor_homepage", "conf": "med"},
    ],

    # ====================================================== BATCH 4 ======================================================

    # ----------------------------------------------------- Snyk
    "Snyk": [
        {"sp": "VIA-01", "delta": +1.0, "fact": "Privately-held with $7.4B+ valuation (2022 Series G); $200M+ ARR; among most-valuable AppSec/CNAPP vendors.", "url": "https://snyk.io/about/", "src": "vendor_about", "conf": "high"},
        {"sp": "VIA-02", "delta": +0.7, "fact": "Investors include Accel, Tiger Global, Atlassian Ventures, Sands Capital - tier-1 growth capital.", "url": "https://snyk.io/about/", "src": "vendor_about", "conf": "high"},
        {"sp": "SLE-01", "delta": +0.8, "fact": "2,500+ customers including Google, Salesforce, Atlassian, Asurion - dev-heavy enterprise base.", "url": "https://snyk.io/customers/", "src": "vendor_customers", "conf": "high"},
        {"sp": "MKR-01", "delta": +0.6, "fact": "Quarterly major releases; Snyk DeepCode AI, AI Trust, Snyk Cloud (post-Fugue), Snyk Container - high innovation cadence.", "url": "https://snyk.io/blog/", "src": "vendor_blog", "conf": "high"},
        {"sp": "MKR-03", "delta": +0.7, "fact": "Strong on shift-left CNAPP primitives (SCA, SAST, IaC, Container) with developer-first UX; Fugue acquisition added cloud-runtime context.", "url": "https://snyk.io/product/", "src": "vendor_product", "conf": "high"},
        {"sp": "MKE-01", "delta": +0.7, "fact": "Sustained Tier-1 press coverage; well-cited in DevSecOps coverage (TheNewStack, DarkReading).", "url": "https://snyk.io/news/", "src": "press_release_index", "conf": "high"},
        {"sp": "MKE-03", "delta": +0.6, "fact": "Named Leader in 2024 Forrester Wave for SCA; recognized as developer-security leader; CNAPP-adjacent endorsements.", "url": "https://snyk.io/analyst-reports/", "src": "analyst_recognition", "conf": "high"},
        {"sp": "MKU-01", "delta": +0.7, "fact": "Articulated 'developer security platform' vision; clear strategic narrative around shift-left and AI-assisted security.", "url": "https://snyk.io/", "src": "vendor_homepage", "conf": "high"},
        {"sp": "VIG-01", "delta": +0.5, "fact": "Global presence; HQ Boston/London; offices across NA/EMEA/APJ.", "url": "https://snyk.io/about/", "src": "vendor_about", "conf": "high"},
        # Reality check: Snyk CNAPP runtime is weaker than its shift-left strength
        {"sp": "MKR-04", "delta": -0.4, "fact": "Snyk Cloud (CSPM/CWPP) is weaker than core SCA/SAST capabilities; runtime-CNAPP feature parity with Wiz/Orca/Sysdig still developing.", "url": "https://snyk.io/product/snyk-cloud/", "src": "vendor_product", "conf": "high"},
        {"sp": "MKU-03", "delta": -0.3, "fact": "Strategic positioning anchored in AppSec/DevSecOps rather than full-stack CNAPP; CNAPP messaging is secondary.", "url": "https://snyk.io/", "src": "vendor_homepage", "conf": "med"},
    ],

    # ----------------------------------------------------- Sophos
    "Sophos": [
        {"sp": "VIA-01", "delta": +0.8, "fact": "Privately-held by Thoma Bravo since 2020; $1B+ annual revenue; recently acquired Secureworks (Feb 2025) expanding MDR/XDR scope.", "url": "https://www.sophos.com/en-us/company", "src": "vendor_about", "conf": "high"},
        {"sp": "VIA-02", "delta": +0.6, "fact": "Thoma Bravo backing provides M&A capacity; Secureworks acquisition adds significant scale.", "url": "https://www.sophos.com/en-us/press/press-releases", "src": "press_release_index", "conf": "high"},
        {"sp": "SLE-01", "delta": +0.7, "fact": "600,000+ customers globally; broad SMB+mid-market base from endpoint heritage.", "url": "https://www.sophos.com/en-us/company", "src": "vendor_about", "conf": "high"},
        {"sp": "SLE-03", "delta": +0.6, "fact": "Channel-led GTM with extensive MSP/MSSP partner network; one of largest channel programs in cyber.", "url": "https://partners.sophos.com/", "src": "vendor_partners", "conf": "high"},
        {"sp": "MKE-01", "delta": +0.6, "fact": "Sustained Tier-1 press coverage; Sophos X-Ops and SophosLabs threat research widely cited.", "url": "https://news.sophos.com/", "src": "press_release_index", "conf": "high"},
        {"sp": "MKE-03", "delta": +0.5, "fact": "Named Leader in Gartner MQ for EPP and MDR; CNAPP-adjacent analyst credibility.", "url": "https://www.sophos.com/en-us/content/sophos-recognition", "src": "analyst_recognition", "conf": "high"},
        {"sp": "VIG-01", "delta": +0.7, "fact": "Truly global presence; HQ Oxford UK; localized operations in 50+ countries with multilingual support.", "url": "https://www.sophos.com/en-us/company", "src": "vendor_about", "conf": "high"},
        # Reality check: Sophos CNAPP (Cloud Optix) is small vs core MDR/XDR/EPP business
        {"sp": "MKR-04", "delta": -0.5, "fact": "Cloud Optix CNAPP is small offering vs Sophos core EPP/MDR; CNAPP feature breadth materially less than pure-play vendors.", "url": "https://www.sophos.com/en-us/products/cloud-native-security", "src": "vendor_product", "conf": "high"},
        {"sp": "MKR-01", "delta": -0.3, "fact": "Cloud Optix release cadence trails CNAPP pure-plays; CNAPP-specific innovation announcements infrequent.", "url": "https://www.sophos.com/en-us/products/cloud-native-security", "src": "vendor_product", "conf": "med"},
        {"sp": "MKU-03", "delta": -0.5, "fact": "Strategic narrative dominated by MDR/EPP; CNAPP/Cloud Optix is peripheral to core positioning.", "url": "https://www.sophos.com/", "src": "vendor_homepage", "conf": "high"},
    ],

    # ----------------------------------------------------- Sweet Security
    "Sweet Security": [
        {"sp": "VIA-01", "delta": -0.3, "fact": "Privately-held Israeli startup founded 2023; small revenue base (early-stage).", "url": "https://sweet.security/about", "src": "vendor_about", "conf": "med"},
        {"sp": "VIA-02", "delta": +0.5, "fact": "Series A $33M (Sept 2024) led by Evolution Equity Partners; Munich Re Ventures; funded for runway.", "url": "https://sweet.security/press", "src": "press_release_index", "conf": "high"},
        {"sp": "VIA-04", "delta": +0.4, "fact": "Founded by ex-IDF Unit 8200 leadership (Dror Kashti, Eyal Fisher, Orel Ben-Ishay) - strong technical pedigree.", "url": "https://sweet.security/about", "src": "vendor_about", "conf": "high"},
        {"sp": "MKR-01", "delta": +0.7, "fact": "Rapid product cadence in 2024-2026 with eBPF-based runtime detection, ASPM agent, Non-Human Identity launch.", "url": "https://sweet.security/blog", "src": "vendor_blog", "conf": "high"},
        {"sp": "MKR-03", "delta": +0.7, "fact": "Differentiated runtime-CNAPP architecture using eBPF for low-overhead workload visibility; AI-first approach.", "url": "https://sweet.security/platform", "src": "vendor_product", "conf": "high"},
        {"sp": "MKU-01", "delta": +0.7, "fact": "Articulated 'runtime-first cloud detection & response' vision differentiating from posture-only CNAPP peers.", "url": "https://sweet.security/", "src": "vendor_homepage", "conf": "high"},
        {"sp": "MKE-01", "delta": +0.4, "fact": "Notable Tier-1 / industry coverage in TechCrunch, DarkReading on funding and product launches.", "url": "https://sweet.security/press", "src": "press_release_index", "conf": "med"},
        # Reality check: Small/young vendor
        {"sp": "SLE-01", "delta": -0.5, "fact": "Limited public customer references; small installed base relative to CNAPP MQ peers.", "url": "https://sweet.security/customers", "src": "vendor_customers", "conf": "med"},
        {"sp": "VIG-01", "delta": -0.5, "fact": "Israeli startup with limited international footprint; primarily Israel + US presence.", "url": "https://sweet.security/about", "src": "vendor_about", "conf": "med"},
        {"sp": "VIG-03", "delta": -0.4, "fact": "No FedRAMP authorization; limited regulated-industry footprint at this stage.", "url": "https://sweet.security/", "src": "vendor_homepage", "conf": "med"},
    ],

    # ----------------------------------------------------- Sysdig
    "Sysdig": [
        {"sp": "VIA-01", "delta": +0.8, "fact": "Privately-held with $2.5B valuation post-Series H (Jan 2022, $350M); $100M+ ARR; CNAPP-pure-play with deep runtime focus.", "url": "https://sysdig.com/about/", "src": "vendor_about", "conf": "high"},
        {"sp": "VIA-02", "delta": +0.6, "fact": "Investors include Permira, Goldman Sachs, Accel - tier-1 growth capital.", "url": "https://sysdig.com/about/", "src": "vendor_about", "conf": "high"},
        {"sp": "MKR-03", "delta": +0.9, "fact": "Creator of Falco (CNCF graduated runtime security project) and Sysdig OSS - dominant runtime-CNAPP innovation lineage.", "url": "https://falco.org/", "src": "open_source", "conf": "high"},
        {"sp": "MKR-01", "delta": +0.7, "fact": "Continuous innovation in runtime detection, CDR, Sysdig Sage AI assistant, AI workload security; quarterly major releases.", "url": "https://sysdig.com/blog/", "src": "vendor_blog", "conf": "high"},
        {"sp": "MKR-04", "delta": +0.7, "fact": "First to articulate '5/5/5 benchmark' for cloud-detection response time; runtime-CNAPP differentiator.", "url": "https://sysdig.com/blog/555-benchmark-cloud-detection-response/", "src": "vendor_blog", "conf": "high"},
        {"sp": "MKE-03", "delta": +0.7, "fact": "Named Leader in Forrester Wave for CWP/CNAPP 2024; consistently top-positioned in CNAPP runtime category.", "url": "https://sysdig.com/resources/analyst-reports/", "src": "analyst_recognition", "conf": "high"},
        {"sp": "MKU-01", "delta": +0.8, "fact": "Articulated 'runtime-first CNAPP' vision; Sysdig Sage AI thought leadership; strong category positioning.", "url": "https://sysdig.com/", "src": "vendor_homepage", "conf": "high"},
        {"sp": "MKE-01", "delta": +0.6, "fact": "Sustained Tier-1 press; Sysdig Threat Research Team and annual Cloud-Native Security & Usage Report widely cited.", "url": "https://sysdig.com/news/", "src": "press_release_index", "conf": "high"},
        {"sp": "CXQ-01", "delta": +0.5, "fact": "High Gartner Peer Insights ratings; case studies from Goldman Sachs, SAP Concur, BigPanda.", "url": "https://www.gartner.com/reviews/market/cloud-native-application-protection-platforms/vendor/sysdig", "src": "gartner_peer_insights", "conf": "high"},
        {"sp": "VIG-01", "delta": +0.5, "fact": "Global presence; HQ San Francisco; offices across NA/EMEA/APJ.", "url": "https://sysdig.com/about/", "src": "vendor_about", "conf": "high"},
    ],

    # ----------------------------------------------------- Tenable
    "Tenable": [
        {"sp": "VIA-01", "delta": +0.9, "fact": "NASDAQ:TENB with $800M+ annual revenue; established public cyber vendor.", "url": "https://investors.tenable.com/", "src": "investor_relations", "conf": "high"},
        {"sp": "VIA-02", "delta": +0.7, "fact": "Strong balance sheet enabled $265M Ermetic acquisition (Oct 2023) creating Tenable Cloud Security CNAPP capability.", "url": "https://www.tenable.com/press-releases/tenable-acquires-ermetic", "src": "press_release", "conf": "high"},
        {"sp": "VIA-04", "delta": +0.5, "fact": "Public-company governance; Steve Vintz interim CEO; mature operational discipline.", "url": "https://investors.tenable.com/", "src": "investor_relations", "conf": "high"},
        {"sp": "SLE-01", "delta": +0.7, "fact": "44,000+ customers globally including 65% of Fortune 500; massive VRM installed base for CNAPP cross-sell.", "url": "https://www.tenable.com/about-tenable", "src": "vendor_about", "conf": "high"},
        {"sp": "MKR-03", "delta": +0.5, "fact": "Tenable Cloud Security covers CSPM, CIEM (strong from Ermetic), CWPP, IaC scanning; integrated with Tenable One exposure platform.", "url": "https://www.tenable.com/products/tenable-cloud-security", "src": "vendor_product", "conf": "high"},
        {"sp": "MKE-01", "delta": +0.6, "fact": "Sustained Tier-1 press; Tenable Research widely cited; consistent press cadence.", "url": "https://www.tenable.com/press-releases", "src": "press_release_index", "conf": "high"},
        {"sp": "MKE-03", "delta": +0.6, "fact": "Named Leader in Gartner MQ for VRM/Vulnerability Assessment; CNAPP-adjacent analyst credibility transferable.", "url": "https://www.tenable.com/analyst-research", "src": "analyst_recognition", "conf": "high"},
        {"sp": "VIG-01", "delta": +0.5, "fact": "Global presence; HQ Columbia MD; offices across NA/EMEA/APJ.", "url": "https://www.tenable.com/about-tenable", "src": "vendor_about", "conf": "high"},
        {"sp": "VIG-03", "delta": +0.7, "fact": "FedRAMP Authorized; deep US Federal customer base; broad public-sector globally.", "url": "https://www.tenable.com/solutions/government", "src": "vendor_compliance", "conf": "high"},
        # Reality check: Tenable Cloud Security is post-acquisition integration
        {"sp": "MKR-04", "delta": -0.3, "fact": "Tenable Cloud Security is recently-integrated Ermetic acquisition; CIEM is stronger than CWPP/runtime relative to CNAPP pure-plays.", "url": "https://www.tenable.com/products/tenable-cloud-security", "src": "vendor_product", "conf": "med"},
        {"sp": "MKU-03", "delta": -0.4, "fact": "Strategic narrative led by Exposure Management/VRM; CNAPP positioned as one capability within Tenable One rather than pure-play focus.", "url": "https://www.tenable.com/", "src": "vendor_homepage", "conf": "high"},
    ],

    # ====================================================== BATCH 5 ======================================================

    # ----------------------------------------------------- Trend Micro
    "Trend Micro": [
        {"sp": "VIA-01", "delta": +1.0, "fact": "TYO:4704 publicly listed; ~$2B annual revenue; 30+ years operating history with profitable financials.", "url": "https://www.trendmicro.com/en_us/about.html", "src": "vendor_about", "conf": "high"},
        {"sp": "VIA-02", "delta": +0.6, "fact": "Strong cash position; sustained R&D investment in Vision One platform integrating CNAPP capabilities.", "url": "https://www.trendmicro.com/en_us/about/investor-relations.html", "src": "investor_relations", "conf": "high"},
        {"sp": "VIA-04", "delta": +0.5, "fact": "Long-tenured CEO Eva Chen (co-founder); mature public-company governance.", "url": "https://www.trendmicro.com/en_us/about.html", "src": "vendor_about", "conf": "high"},
        {"sp": "SLE-01", "delta": +0.8, "fact": "500,000+ customers globally; strong APAC footprint; ~50% revenue from Asia-Pacific.", "url": "https://www.trendmicro.com/en_us/about.html", "src": "vendor_about", "conf": "high"},
        {"sp": "MKR-03", "delta": +0.5, "fact": "Trend Vision One - Cloud Security covers CSPM, CWPP, CIEM, CDR, container security; integrated with broader XDR platform.", "url": "https://www.trendmicro.com/en_us/business/products/cloud-security.html", "src": "vendor_product", "conf": "high"},
        {"sp": "MKE-01", "delta": +0.7, "fact": "Sustained Tier-1 press coverage globally; Trend Research widely cited; strong APAC press presence.", "url": "https://newsroom.trendmicro.com/", "src": "press_release_index", "conf": "high"},
        {"sp": "MKE-03", "delta": +0.6, "fact": "Named Leader in historical Gartner MQ for CWPP; broad analyst recognition across EPP/XDR adjacent markets.", "url": "https://www.trendmicro.com/en_us/about/awards.html", "src": "analyst_recognition", "conf": "high"},
        {"sp": "VIG-01", "delta": +1.0, "fact": "Truly global; HQ Tokyo; localized operations in 65+ countries with multilingual support; APAC stronghold.", "url": "https://www.trendmicro.com/en_us/about.html", "src": "vendor_about", "conf": "high"},
        {"sp": "VIG-03", "delta": +0.6, "fact": "FedRAMP Moderate Authorized; significant Japan/APAC public-sector base; growing US federal presence.", "url": "https://www.trendmicro.com/en_us/business/solutions/industries/government.html", "src": "vendor_compliance", "conf": "high"},
        # Reality check: Trend Micro CNAPP integration into Vision One
        {"sp": "MKU-03", "delta": -0.3, "fact": "Cloud security positioned as part of broader Vision One XDR rather than CNAPP-pure-play; strategic narrative led by XDR/SOC modernization.", "url": "https://www.trendmicro.com/", "src": "vendor_homepage", "conf": "med"},
        {"sp": "MKR-01", "delta": -0.3, "fact": "CNAPP-specific innovation cadence trails pure-plays like Wiz/Orca; bulk of platform innovation focused on XDR/Vision One.", "url": "https://www.trendmicro.com/en_us/business/products/cloud-security.html", "src": "vendor_product", "conf": "med"},
    ],

    # ----------------------------------------------------- Uptycs
    "Uptycs": [
        {"sp": "VIA-01", "delta": -0.3, "fact": "Privately-held; raised ~$93M total; smaller scale than CNAPP MQ peers; recent layoffs (2023-2024) raised execution concerns.", "url": "https://www.uptycs.com/about", "src": "vendor_about", "conf": "med"},
        {"sp": "VIA-02", "delta": -0.3, "fact": "No major funding round announced since 2021 Series C; runway concerns reported in industry press during 2023-2024.", "url": "https://www.uptycs.com/about", "src": "vendor_about", "conf": "med"},
        {"sp": "MKR-03", "delta": +0.4, "fact": "Differentiated osquery-based unified telemetry approach (XDR+CNAPP); novel data-platform architecture.", "url": "https://www.uptycs.com/products", "src": "vendor_product", "conf": "high"},
        {"sp": "MKR-01", "delta": +0.3, "fact": "Active product cadence with AI-SPM, Kubernetes security, and ASPM extensions launched 2024-2026.", "url": "https://www.uptycs.com/blog", "src": "vendor_blog", "conf": "med"},
        {"sp": "MKU-01", "delta": +0.4, "fact": "Articulated 'unified XDR + CNAPP' vision via single data platform - coherent strategic narrative.", "url": "https://www.uptycs.com/", "src": "vendor_homepage", "conf": "high"},
        # Reality check: Uptycs is a small, struggling vendor
        {"sp": "SLE-01", "delta": -0.5, "fact": "Limited public customer references vs CNAPP MQ leaders; modest installed base.", "url": "https://www.uptycs.com/customers", "src": "vendor_customers", "conf": "med"},
        {"sp": "MKE-01", "delta": -0.4, "fact": "Limited Tier-1 press cadence; reduced PR presence vs 2021-2022 peak coverage.", "url": "https://www.uptycs.com/news", "src": "press_release_index", "conf": "med"},
        {"sp": "MKE-03", "delta": -0.3, "fact": "Limited recent top-tier analyst recognition; not present as Leader in Forrester Wave CNAPP 2024.", "url": "https://www.uptycs.com/", "src": "analyst_absence", "conf": "med"},
        {"sp": "VIG-01", "delta": -0.4, "fact": "US-centric footprint; limited international localization or regional offices.", "url": "https://www.uptycs.com/about", "src": "vendor_about", "conf": "med"},
        {"sp": "VIG-03", "delta": -0.3, "fact": "No FedRAMP authorization advertised; limited public-sector footprint.", "url": "https://www.uptycs.com/", "src": "vendor_homepage", "conf": "med"},
    ],

    # ----------------------------------------------------- Upwind
    "Upwind": [
        {"sp": "VIA-02", "delta": +0.8, "fact": "Series B $100M (Nov 2024) at $900M valuation led by Craft Ventures, Greylock, Cyberstarts; one of fastest-growing CNAPP startups.", "url": "https://www.upwind.io/news", "src": "press_release_index", "conf": "high"},
        {"sp": "VIA-04", "delta": +0.5, "fact": "Founded by Amiram Shachar (ex-Spot.io founder, sold to NetApp $450M) - proven founder pedigree.", "url": "https://www.upwind.io/about", "src": "vendor_about", "conf": "high"},
        {"sp": "MKR-01", "delta": +0.8, "fact": "Rapid product cadence 2024-2026: runtime-first CNAPP, eBPF agent, AI-SPM, code-to-cloud platform launched in <2 years.", "url": "https://www.upwind.io/blog", "src": "vendor_blog", "conf": "high"},
        {"sp": "MKR-03", "delta": +0.8, "fact": "Differentiated runtime-first CNAPP architecture using eBPF; positioned as next-gen Wiz alternative with runtime depth.", "url": "https://www.upwind.io/platform", "src": "vendor_product", "conf": "high"},
        {"sp": "MKU-01", "delta": +0.8, "fact": "Strong articulated vision: 'runtime-powered CNAPP' challenging posture-only incumbents; Forbes/TechCrunch coverage of strategic positioning.", "url": "https://www.upwind.io/", "src": "vendor_homepage", "conf": "high"},
        {"sp": "MKR-04", "delta": +0.7, "fact": "Innovation across full code-to-cloud-to-runtime stack at startup pace; rapid feature parity buildout vs incumbents.", "url": "https://www.upwind.io/platform", "src": "vendor_product", "conf": "high"},
        {"sp": "MKE-01", "delta": +0.5, "fact": "Strong Tier-1 press coverage in 2024-2026 (Forbes, TechCrunch, SecurityWeek) tracking funding and growth.", "url": "https://www.upwind.io/news", "src": "press_release_index", "conf": "high"},
        # Reality check: Upwind is young, scale limited
        {"sp": "VIA-01", "delta": -0.4, "fact": "Founded 2022; small revenue base vs established CNAPP MQ peers though growing fast.", "url": "https://www.upwind.io/about", "src": "vendor_about", "conf": "med"},
        {"sp": "SLE-01", "delta": -0.3, "fact": "Customer base growing but materially smaller than CNAPP MQ leaders; named references include Volkswagen, Sony, Wiley.", "url": "https://www.upwind.io/customers", "src": "vendor_customers", "conf": "med"},
        {"sp": "VIG-03", "delta": -0.3, "fact": "No FedRAMP authorization yet; limited federal presence at this stage.", "url": "https://www.upwind.io/", "src": "vendor_homepage", "conf": "med"},
    ],

    # ----------------------------------------------------- Wiz (the benchmark)
    "Wiz": [
        {"sp": "VIA-01", "delta": +1.4, "fact": "Privately-held with $1B+ ARR (reached fastest-ever in software history); Google announced $32B acquisition agreement (March 2025).", "url": "https://www.wiz.io/about", "src": "vendor_about", "conf": "high"},
        {"sp": "VIA-02", "delta": +1.4, "fact": "Raised $1.9B+ in funding at peak $12B valuation (Sequoia, Index, Greenoaks, Cyberstarts) prior to Google deal; benchmark CNAPP startup.", "url": "https://www.wiz.io/about", "src": "vendor_about", "conf": "high"},
        {"sp": "VIA-04", "delta": +0.7, "fact": "Founded by ex-Microsoft Cloud Security Group leadership (Assaf Rappaport, Ami Luttwak, Yinon Costica, Roy Reznik); proven exec team.", "url": "https://www.wiz.io/about", "src": "vendor_about", "conf": "high"},
        {"sp": "SLE-01", "delta": +1.4, "fact": "Customers include 50% of Fortune 100 and 35% of Fortune 500; named accounts include Salesforce, BMW, Slack, Mars, Morgan Stanley, Snowflake.", "url": "https://www.wiz.io/customers", "src": "vendor_customers", "conf": "high"},
        {"sp": "SLE-03", "delta": +0.8, "fact": "Strategic partnerships with all hyperscalers (AWS, Azure, GCP); Wiz Marketplace Partner of the Year multiple times.", "url": "https://www.wiz.io/partners", "src": "vendor_partners", "conf": "high"},
        {"sp": "MKR-01", "delta": +1.0, "fact": "Highest CNAPP innovation cadence; AI-SPM (industry-first), DSPM, runtime sensor, Code Security, Wiz Defend - quarterly major releases.", "url": "https://www.wiz.io/blog", "src": "vendor_blog", "conf": "high"},
        {"sp": "MKR-03", "delta": +1.4, "fact": "Pioneer of agentless CNAPP via Security Graph; sets the technical pace for entire CNAPP category.", "url": "https://www.wiz.io/platform", "src": "vendor_product", "conf": "high"},
        {"sp": "MKR-04", "delta": +1.0, "fact": "Industry-first AI-SPM, runtime sensor integration, code-to-cloud unified Security Graph; defines CNAPP feature roadmap for category.", "url": "https://www.wiz.io/platform", "src": "vendor_product", "conf": "high"},
        {"sp": "MKE-01", "delta": +1.4, "fact": "Tier-1 press coverage at unprecedented levels for CNAPP vendor; Google acquisition announcement was top global tech story March 2025.", "url": "https://www.wiz.io/newsroom", "src": "press_release_index", "conf": "high"},
        {"sp": "MKE-03", "delta": +1.4, "fact": "Named Leader in Forrester Wave CNAPP 2024; consensus #1 in analyst CNAPP rankings; widely viewed as CNAPP category benchmark.", "url": "https://www.wiz.io/analyst-reports", "src": "analyst_recognition", "conf": "high"},
        {"sp": "CXQ-01", "delta": +1.0, "fact": "Highest Gartner Peer Insights ratings in CNAPP category (4.8+ stars); customer references publicly cite rapid time-to-value.", "url": "https://www.gartner.com/reviews/market/cloud-native-application-protection-platforms/vendor/wiz", "src": "gartner_peer_insights", "conf": "high"},
        {"sp": "MKU-01", "delta": +1.4, "fact": "Defined the modern CNAPP narrative ('one platform, full graph, agentless'); category-shaping vision adopted by competitors.", "url": "https://www.wiz.io/", "src": "vendor_homepage", "conf": "high"},
        {"sp": "MKU-02", "delta": +1.0, "fact": "Clear differentiation: agentless graph-based unified data model; competitors (Check Point, Palo Alto) explicitly partner with or position against Wiz.", "url": "https://www.wiz.io/", "src": "vendor_homepage", "conf": "high"},
        {"sp": "VIG-01", "delta": +1.0, "fact": "Global presence; HQ NYC; offices across NA/EMEA/APJ; localized customer base globally.", "url": "https://www.wiz.io/about", "src": "vendor_about", "conf": "high"},
        {"sp": "VIG-03", "delta": +0.7, "fact": "FedRAMP Moderate Authorized; rapidly growing federal customer base; HHS, DoD wins reported.", "url": "https://www.wiz.io/solutions/government", "src": "vendor_compliance", "conf": "high"},
    ],
}

# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------


def clamp(v: float, lo: float = 0.0, hi: float = 5.0) -> float:
    return max(lo, min(hi, v))


def apply_evidence(vendor: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    sps = vendor.setdefault("sub_pillar_scores_v12", copy.deepcopy(vendor["sub_pillar_scores_current"]))
    ledger = vendor.setdefault("evidence_ledger", [])
    for r in records:
        sp = r["sp"]
        if sp not in sps:
            continue
        before = sps[sp]
        after = round(clamp(before + r["delta"]), 2)
        sps[sp] = after
        ledger.append(
            {
                "sub_pillar": sp,
                "score_before": before,
                "delta": r["delta"],
                "score_after": after,
                "fact": r["fact"],
                "source_url": r["url"],
                "source_type": r["src"],
                "confidence": r["conf"],
            }
        )
    # recompute pillar averages from updated sub-pillars
    pillar_groups: dict[str, list[float]] = {}
    for sp_id, score in sps.items():
        pid = sp_id.split("-")[0]
        pillar_groups.setdefault(pid, []).append(score)
    vendor["pillar_scores_v12"] = {
        pid: round(sum(vals) / len(vals), 2) for pid, vals in pillar_groups.items()
    }
    if records:
        vendor["mq_gap_research_status"] = "auto_derived_with_public_evidence"
        vendor["mq_gap_research_tier"] = "tier_3"
        vendor["mq_gap_derivation_method"] = "heuristic_plus_public_source_evidence"
        # confidence: max over evidence rows in batch (high>med>low)
        rank = {"low": 1, "med": 2, "high": 3}
        best = max(rank[r["conf"]] for r in records)
        vendor["mq_gap_research_confidence"] = {1: "low", 2: "medium", 3: "high"}[best]
        vendor["mq_gap_evidence_count"] = len(records)
    return vendor


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", default=None, help="batch1..batch5 (default: all batches with evidence defined)")
    args = parser.parse_args()

    # Read from DST if it exists so prior-batch enrichments are preserved
    src_path = DST if DST.exists() else SRC
    data = json.loads(src_path.read_text(encoding="utf-8"))
    vendors = data["vendors"]

    target_names = set()
    if args.batch:
        target_names.update(BATCHES[args.batch])
    else:
        for names in BATCHES.values():
            target_names.update(names)
    # only enrich vendors that actually have evidence rows defined
    target_names &= set(EVIDENCE.keys())

    enriched, skipped = [], []
    for v in vendors:
        name = v["vendor"]
        if name in target_names:
            apply_evidence(v, EVIDENCE[name])
            enriched.append(name)
        else:
            skipped.append(name)

    data["enrichment_pass"] = "v1.2_public_source_evidence"
    data["enriched_vendors"] = enriched
    data["enrichment_generated_at"] = datetime.now(timezone.utc).isoformat()
    data["enrichment_script"] = "_enrich_cnapp_mq_v12.py"

    DST.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    flat_ledger = []
    for v in vendors:
        for row in v.get("evidence_ledger", []):
            flat_ledger.append({"vendor": v["vendor"], **row})
    LEDGER.write_text(json.dumps({"records": flat_ledger, "count": len(flat_ledger)}, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Enriched {len(enriched)} vendors:")
    for n in enriched:
        v = next(x for x in vendors if x["vendor"] == n)
        before_avg = round(sum(v["sub_pillar_scores_current"].values()) / 27, 2)
        after_avg = round(sum(v["sub_pillar_scores_v12"].values()) / 27, 2)
        print(f"  {n:25s}  v1.1 avg={before_avg}  ->  v1.2 avg={after_avg}  evidence_rows={v['mq_gap_evidence_count']}")
    print(f"Skipped (no evidence yet): {len(skipped)}")
    print(f"Wrote: {DST.name}")
    print(f"Wrote: {LEDGER.name}  ({len(flat_ledger)} ledger rows)")


if __name__ == "__main__":
    main()
