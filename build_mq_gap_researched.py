#!/usr/bin/env python3
"""
build_mq_gap_researched.py — MQ Gap 2-0 Researched
=====================================================
Derives MQ Gap sub-pillar scores from existing MDR capability, pricing,
and metadata using rule-based heuristics. Maximises reuse of existing data;
remaining gaps are flagged for manual follow-up.

Sources:
  1. MDR Services Vendor 2-1 Consolidated.json  (capability + metadata)
  2. MDR Services Vendor Pricing 2-1 AI Enriched.json  (pricing + business model)
  3. MDR Services Vendor MQ Gap 1-0 Seed.json  (template)
  4. MQ_Gap_Schema_1_0.json  (schema reference)

Output: MDR Services Vendor MQ Gap 2-0 Researched.json
"""
import json, re, math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ── Load all source data ─────────────────────────────────────────────

def load_json(name):
    with open(ROOT / name, "r", encoding="utf-8") as f:
        return json.load(f)

cap_data  = load_json("MDR Services Vendor 2-1 Consolidated.json")
prc_data  = load_json("MDR Services Vendor Pricing 2-1 AI Enriched.json")
seed_data = load_json("MDR Services Vendor MQ Gap 1-0 Seed.json")
schema    = load_json("MQ_Gap_Schema_1_0.json")

# Index pricing by vendor name
pricing_by_vendor = {v["vendor"]: v for v in prc_data["vendors"]}

# Index capability by vendor name
cap_by_vendor = {v["vendor"]: v for v in cap_data["vendors"]}

# ── Helper utilities ─────────────────────────────────────────────────

def clamp(val, lo=0.0, hi=5.0):
    return max(lo, min(hi, round(val, 1)))

def text_lower(v, *keys):
    """Concatenate multiple text fields from a vendor dict, lowercased."""
    parts = []
    for k in keys:
        val = v.get(k, "")
        if isinstance(val, str):
            parts.append(val.lower())
        elif isinstance(val, list):
            parts.append(" ".join(str(x).lower() for x in val))
        elif isinstance(val, dict):
            parts.append(" ".join(str(x).lower() for x in val.values()))
    return " ".join(parts)

def keyword_count(text, keywords):
    """Count how many of the keywords appear in text."""
    return sum(1 for kw in keywords if kw.lower() in text)

def keyword_score(text, keywords, scale_max=5.0, divisor=None):
    """Score 0-5 based on fraction of keywords matched."""
    if not keywords:
        return 0.0
    d = divisor or len(keywords)
    matched = keyword_count(text, keywords)
    return clamp((matched / d) * scale_max)

EMPLOYEE_SIZE_ORDER = {
    "1-10": 1, "10-20": 1.5, "20-50": 2, "50-100": 2.5,
    "100-200": 3, "200-500": 3.5, "500-1000": 4, "1000-2000": 4,
    "2000-5000": 4.5, "5000-10000": 5, "10000+": 5,
}

FUNDING_STAGE_VIABILITY = {
    "IPO": 5.0, "PE-Backed": 4.0, "Acquired": 3.5, "Subsidiary": 3.5,
    "Series F": 3.5, "Series E": 3.5, "Series D": 3.5,
    "Series C": 3.0, "Series B": 2.5, "Series A": 2.0,
    "Seed": 1.5, "Pre-Seed": 1.0, "Private": 3.0,
    "Government": 4.0, "Bootstrapped": 2.5,
}

REGION_REACH = {
    "Global": 5, "North America": 3, "Europe": 3, "Asia-Pacific": 3,
    "Middle East": 2, "Latin America": 2, "Africa": 2, "Oceania": 2,
}

# ── Sub-pillar scoring functions ─────────────────────────────────────

# === VIA: Financial Viability ===

def score_via_01(cap, prc):
    """VIA-01: Revenue & Growth Trajectory"""
    base = 1.0
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    funding = FUNDING_STAGE_VIABILITY.get(cap.get("funding_stage", ""), 2.0)
    # IPO = public financials, strong signal
    if cap.get("funding_stage") == "IPO":
        base = 4.0
    elif cap.get("funding_stage") in ("PE-Backed", "Acquired", "Subsidiary"):
        base = 3.0
    else:
        base = max(funding - 0.5, 1.0)
    # Adjust for size: bigger companies likely have more revenue
    size_bonus = (emp - 2.5) * 0.3
    score = base + size_bonus
    # Text signals
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    growth_kw = ["rapid growth", "fastest growing", "hypergrowth", "revenue",
                 "revenue growth", "billion", "million arr", "unicorn",
                 "market leader", "global leader", "industry leader"]
    score += keyword_count(txt, growth_kw) * 0.2
    rationale = (f"Funding: {cap.get('funding_stage','Unknown')}, "
                 f"Employees: {cap.get('employee_count_range','Unknown')}. "
                 f"Derived from company size and funding maturity indicators.")
    return clamp(score), rationale, "medium"

def score_via_02(cap, prc):
    """VIA-02: Profitability & Financial Health"""
    funding = cap.get("funding_stage", "")
    emp = cap.get("employee_count_range", "")
    base = FUNDING_STAGE_VIABILITY.get(funding, 2.0)
    # IPO companies with large teams are likely profitable or near
    if funding == "IPO" and emp in ("5000-10000", "10000+"):
        score = 4.5
    elif funding == "IPO":
        score = 4.0
    elif funding in ("PE-Backed", "Subsidiary"):
        score = 3.5
    elif funding == "Acquired":
        score = 3.0
    elif funding in ("Series D", "Series E", "Series F"):
        score = 2.5
    elif funding in ("Series B", "Series C"):
        score = 2.0
    else:
        score = base - 0.5
    # Total funding text can help
    tf = cap.get("total_funding", "")
    if tf:
        tf_lower = tf.lower()
        if "billion" in tf_lower:
            score = max(score, 4.0)
        elif "$" in tf_lower:
            # Try to extract amount
            m = re.search(r'\$(\d+)', tf_lower)
            if m and int(m.group(1)) >= 500:
                score = max(score, 3.5)
            elif m and int(m.group(1)) >= 200:
                score = max(score, 3.0)
    rationale = (f"Funding stage: {funding}. "
                 f"Total funding: {tf or 'Not disclosed'}. "
                 f"Financial health inferred from funding maturity and company scale.")
    return clamp(score), rationale, "medium" if funding else "low"

def score_via_03(cap, prc):
    """VIA-03: Customer Base & Retention"""
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis",
                     "notable_differentiation")
    # Look for customer count signals
    customer_kw = ["customer", "client", "organization", "enterprise",
                   "fortune 500", "fortune 100", "global 2000", "thousands",
                   "peer insights", "g2", "gartner"]
    kc = keyword_count(txt, customer_kw)
    emp_score = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    # Larger companies generally have more customers
    base = emp_score * 0.6 + kc * 0.3
    # IPO = must have meaningful customer base
    if cap.get("funding_stage") == "IPO":
        base = max(base, 3.5)
    # Target market signals
    if cap.get("target_market") == "Enterprise":
        base += 0.3
    elif cap.get("target_market") == "Mid-Market + Enterprise":
        base += 0.2
    rationale = (f"Customer base inferred from company size ({cap.get('employee_count_range','')}) "
                 f"and funding stage ({cap.get('funding_stage','')}).")
    return clamp(base), rationale, "low"

def score_via_04(cap, prc):
    """VIA-04: Market Position & Competitive Standing"""
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis",
                     "notable_differentiation", "mitre_coverage")
    analyst_kw = ["gartner", "forrester", "idc", "magic quadrant", "wave",
                  "marketscape", "leader", "visionary", "strong performer",
                  "mitre att&ck", "mitre engenuity", "se labs", "av-test",
                  "market leader", "industry leader"]
    kc = keyword_count(txt, analyst_kw)
    # Use overall MDR capability score as a proxy for competitive standing
    ps = cap.get("pillar_scores_v2_1") or cap.get("pillar_scores", {})
    avg_pillar = sum(ps.values()) / max(len(ps), 1) if ps else 2.0
    base = avg_pillar * 0.5 + kc * 0.35
    if cap.get("funding_stage") == "IPO":
        base += 0.5
    rationale = (f"Market position derived from MDR capability scores (avg {avg_pillar:.1f}), "
                 f"analyst recognition signals ({kc} matches), and funding stage.")
    return clamp(base), rationale, "medium"

# === SLE: Sales Execution & Channel ===

def score_sle_01(cap, prc):
    """SLE-01: Sales Channel & Partner Ecosystem"""
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    partner_kw = ["partner", "channel", "reseller", "mssp", "marketplace",
                  "alliance", "distributor", "var", "oem", "msp program",
                  "partner program", "technology partner", "aws marketplace",
                  "azure marketplace", "google marketplace"]
    kc = keyword_count(txt, partner_kw)
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    # Larger companies typically have bigger channel programs
    base = emp * 0.4 + kc * 0.4
    if cap.get("funding_stage") == "IPO":
        base += 0.5
    if cap.get("delivery_model") in ("Managed Service", "Hybrid"):
        base += 0.2
    rationale = (f"Channel inference: {kc} partner/channel keywords found. "
                 f"Company size ({cap.get('employee_count_range','')}) used as partner ecosystem proxy.")
    return clamp(base), rationale, "low"

def score_sle_02(cap, prc):
    """SLE-02: Sales Motion & Go-to-Market"""
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    sales_kw = ["free trial", "poc", "proof of concept", "demo", "self-service",
                "product-led", "try", "free assessment", "risk assessment",
                "quick start", "onboarding", "pilot"]
    kc = keyword_count(txt, sales_kw)
    # Platform MDR tends to have more self-serve options
    base = 2.0
    if cap.get("mdr_service_type") == "Platform MDR":
        base += 0.5
    elif cap.get("mdr_service_type") == "Turnkey MDR":
        base += 0.3
    base += kc * 0.35
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    base += (emp - 2.5) * 0.2
    rationale = (f"Sales motion: {kc} GTM keywords. Service type: {cap.get('mdr_service_type','')}.")
    return clamp(base), rationale, "low"

def score_sle_03(cap, prc):
    """SLE-03: Geographic Sales Coverage"""
    region = cap.get("region", "")
    hq = cap.get("headquarters", "").lower()
    base = REGION_REACH.get(region, 2.0)
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    geo_kw = ["global", "worldwide", "international", "multi-region",
              "americas", "emea", "apac", "asia", "europe", "middle east",
              "latin america", "japan", "australia", "uk", "germany",
              "follow-the-sun", "24/7 global"]
    kc = keyword_count(txt, geo_kw)
    base += kc * 0.2
    if region == "Global":
        base = max(base, 4.0)
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    if emp >= 4.5:
        base += 0.3
    rationale = (f"Region: {region}. HQ: {cap.get('headquarters','')}. "
                 f"{kc} geographic keywords found.")
    return clamp(base), rationale, "medium"

def score_sle_04(cap, prc):
    """SLE-04: Customer Acquisition Efficiency"""
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    acq_kw = ["roi", "calculator", "assessment", "benchmark", "webinar",
              "content", "blog", "whitepaper", "event", "conference",
              "community", "open source", "freemium", "free tier"]
    kc = keyword_count(txt, acq_kw)
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    base = 1.5 + kc * 0.3 + (emp - 2.5) * 0.2
    # Pricing transparency is a demand gen signal
    if prc:
        pmd = prc.get("pricing_model_details", {})
        if pmd.get("published_pricing"):
            base += 0.3
        if pmd.get("pricing_calculator_available"):
            base += 0.3
    rationale = (f"Acquisition efficiency: {kc} demand-gen keywords. "
                 f"Pricing transparency factored in.")
    return clamp(base), rationale, "low"

# === MKR: Market Responsiveness ===

def score_mkr_01(cap, prc):
    """MKR-01: Product Release Cadence & Velocity"""
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    release_kw = ["release", "update", "launch", "new feature", "platform update",
                  "continuous", "agile", "devops", "cloud-native", "saas",
                  "real-time", "next-gen", "latest version"]
    kc = keyword_count(txt, release_kw)
    # Cloud-native / SaaS companies tend to release faster
    base = 2.0
    if "saas" in txt or "cloud-native" in txt or "cloud platform" in txt:
        base += 0.5
    if cap.get("is_ai_first"):
        base += 0.3
    base += kc * 0.25
    # Innovation pillar scores as proxy for product velocity
    ps = cap.get("pillar_scores_v2_1") or cap.get("pillar_scores", {})
    aio = ps.get("AIO", 2.0)
    aid = ps.get("AID", 2.0)
    base += (aio + aid - 4.0) * 0.2
    rationale = (f"Release cadence: {kc} velocity keywords. "
                 f"AI innovation scores (AIO={aio:.1f}, AID={aid:.1f}) as proxy.")
    return clamp(base), rationale, "low"

def score_mkr_02(cap, prc):
    """MKR-02: Competitive Response & Adaptation"""
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    adapt_kw = ["ai-native", "ai-first", "generative ai", "llm", "gpt",
                "next-generation", "evolved", "transformed", "pivoted",
                "expanded", "acquired", "integrated", "xdr", "extended"]
    kc = keyword_count(txt, adapt_kw)
    base = 2.0
    if cap.get("is_ai_first"):
        base += 0.7
    # year_founded: newer companies are arguably more responsive
    yf = cap.get("year_founded", 2015)
    if yf and yf >= 2018:
        base += 0.3
    elif yf and yf <= 2005:
        # Older but surviving = adapted successfully
        base += 0.2
    base += kc * 0.25
    # High AIO/AID = adapted to AI trend
    ps = cap.get("pillar_scores_v2_1") or cap.get("pillar_scores", {})
    aio = ps.get("AIO", 2.0)
    if aio >= 4.0:
        base += 0.5
    elif aio >= 3.0:
        base += 0.2
    rationale = (f"Competitive adaptation: {kc} adaptation keywords. "
                 f"Founded {yf}. AI-first: {cap.get('is_ai_first', False)}. AIO={aio:.1f}.")
    return clamp(base), rationale, "medium"

def score_mkr_03(cap, prc):
    """MKR-03: M&A & Strategic Investment Track Record"""
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    ma_kw = ["acquired", "acquisition", "merged", "merger", "acquired by",
             "strategic investment", "joint venture", "spin-off", "divest",
             "bought", "consolidated", "integrated acquisition"]
    kc = keyword_count(txt, ma_kw)
    base = 1.5
    funding = cap.get("funding_stage", "")
    if funding == "Acquired":
        base = 3.0
    elif funding == "IPO":
        base = 3.0  # IPO companies often have M&A history
    elif funding in ("PE-Backed", "Subsidiary"):
        base = 2.5
    base += kc * 0.3
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    if emp >= 4.5:
        base += 0.3
    rationale = (f"M&A signals: {kc} M&A keywords. Funding: {funding}.")
    return clamp(base), rationale, "low"

def score_mkr_04(cap, prc):
    """MKR-04: Customer-Driven Feature Delivery"""
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    cust_kw = ["customer feedback", "advisory board", "user community",
               "feature request", "roadmap", "co-development", "beta program",
               "customer-driven", "customer portal", "community"]
    kc = keyword_count(txt, cust_kw)
    base = 1.5 + kc * 0.35
    # SOG portal/dashboard score as proxy
    ps = cap.get("sub_pillar_scores_v2_1") or cap.get("sub_pillar_scores_current", {})
    sog01 = ps.get("SOG-01", 2.0)
    sog04 = ps.get("SOG-04", 2.0)
    if isinstance(sog01, (int, float)) and isinstance(sog04, (int, float)):
        base += (sog01 + sog04 - 4.0) * 0.15
    rationale = (f"Customer-driven delivery: {kc} community/feedback keywords. "
                 f"SOG-01={sog01}, SOG-04={sog04} as customer engagement proxy.")
    return clamp(base), rationale, "low"

# === MKE: Marketing Execution & Brand ===

def score_mke_01(cap, prc):
    """MKE-01: Brand Awareness & Market Presence"""
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    funding = cap.get("funding_stage", "")
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis",
                     "mitre_coverage")
    brand_kw = ["leader", "market leader", "well-known", "recognized",
                "award", "named", "top", "best", "gartner", "forrester",
                "idc", "mitre", "industry leader"]
    kc = keyword_count(txt, brand_kw)
    base = emp * 0.5 + kc * 0.3
    if funding == "IPO":
        base += 0.5
    # Overall capability score as brand proxy (better known vendors score higher)
    ps = cap.get("pillar_scores_v2_1") or cap.get("pillar_scores", {})
    avg = sum(ps.values()) / max(len(ps), 1) if ps else 2.0
    base += (avg - 2.5) * 0.3
    rationale = (f"Brand presence: {kc} recognition keywords. "
                 f"Size: {cap.get('employee_count_range','')}. Funding: {funding}.")
    return clamp(base), rationale, "medium"

def score_mke_02(cap, prc):
    """MKE-02: Content & Thought Leadership"""
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    content_kw = ["threat report", "threat intelligence", "research", "blog",
                  "whitepaper", "report", "annual report", "threat landscape",
                  "threat briefing", "publication", "thought leader"]
    kc = keyword_count(txt, content_kw)
    # PTI pillar = produces threat intelligence = content proxy
    ps = cap.get("pillar_scores_v2_1") or cap.get("pillar_scores", {})
    pti = ps.get("PTI", 2.0)
    base = 1.5 + kc * 0.3 + (pti - 2.0) * 0.3
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    if emp >= 4.5:
        base += 0.3
    rationale = (f"Content leadership: {kc} content keywords. PTI score={pti:.1f} as proxy.")
    return clamp(base), rationale, "low"

def score_mke_03(cap, prc):
    """MKE-03: Event & Conference Presence"""
    # Primarily size-driven heuristic
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    funding = cap.get("funding_stage", "")
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    event_kw = ["rsa", "black hat", "conference", "event", "summit",
                "def con", "booth", "sponsor", "keynote"]
    kc = keyword_count(txt, event_kw)
    base = emp * 0.4 + kc * 0.4
    if funding == "IPO":
        base += 0.5
    rationale = (f"Event presence: {kc} event keywords. Size-derived proxy.")
    return clamp(base), rationale, "low"

def score_mke_04(cap, prc):
    """MKE-04: Digital Presence & Messaging Clarity"""
    txt = text_lower(cap, "description", "key_differentiators")
    # Vendors with clear differentiation text have better messaging
    desc_len = len(cap.get("description", ""))
    diff_len = len(cap.get("key_differentiators", ""))
    base = 2.0
    if desc_len > 200:
        base += 0.5
    if diff_len > 100:
        base += 0.5
    # Product names count = product line clarity
    pn = cap.get("product_names", [])
    if len(pn) >= 3:
        base += 0.3
    elif len(pn) >= 1:
        base += 0.1
    # Website quality proxy: has website
    if cap.get("website"):
        base += 0.2
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    base += (emp - 2.5) * 0.15
    rationale = (f"Digital presence: description length={desc_len}, "
                 f"differentiators length={diff_len}, products={len(pn)}.")
    return clamp(base), rationale, "low"

# === CXQ: Customer Experience Quality ===

def score_cxq_01(cap, prc):
    """CXQ-01: Peer Review Ratings"""
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis",
                     "notable_differentiation")
    review_kw = ["peer insights", "g2", "trustradius", "peerspot",
                 "customers' choice", "leader badge", "high performer",
                 "4.5", "4.6", "4.7", "4.8", "rated"]
    kc = keyword_count(txt, review_kw)
    # SOG as customer satisfaction proxy
    ps = cap.get("pillar_scores_v2_1") or cap.get("pillar_scores", {})
    sog = ps.get("SOG", 2.5)
    base = sog * 0.5 + kc * 0.4 + 0.5
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    if emp >= 4.0:
        base += 0.2  # Larger vendors get more reviews
    rationale = (f"Peer reviews: {kc} review platform keywords. "
                 f"SOG score={sog:.1f} as CX proxy.")
    return clamp(base), rationale, "low"

def score_cxq_02(cap, prc):
    """CXQ-02: Support Quality & Responsiveness"""
    # SOG pillar + TDR-04 (SLA) are direct proxies
    sp = cap.get("sub_pillar_scores_v2_1") or cap.get("sub_pillar_scores_current", {})
    sog01 = sp.get("SOG-01", 2.0)
    sog02 = sp.get("SOG-02", 2.0)
    tdr04 = sp.get("TDR-04", 2.0)
    if isinstance(sog01, (int, float)) and isinstance(sog02, (int, float)) and isinstance(tdr04, (int, float)):
        base = sog01 * 0.3 + sog02 * 0.3 + tdr04 * 0.3 + 0.3
    else:
        base = 2.0
    txt = text_lower(cap, "description", "key_differentiators")
    support_kw = ["24/7", "dedicated", "tam", "csm", "premium support",
                  "sla", "response time", "follow-the-sun"]
    kc = keyword_count(txt, support_kw)
    base += kc * 0.15
    rationale = (f"Support quality: SOG-01={sog01}, SOG-02={sog02}, TDR-04={tdr04}. "
                 f"+{kc} support keywords.")
    return clamp(base), rationale, "medium"

def score_cxq_03(cap, prc):
    """CXQ-03: Onboarding & Time-to-Value"""
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    onboard_kw = ["onboarding", "deployment", "time-to-value", "quick start",
                  "rapid deployment", "same-day", "agent", "agentless",
                  "cloud-native", "automated deployment", "easy to deploy"]
    kc = keyword_count(txt, onboard_kw)
    base = 2.0 + kc * 0.35
    # Platform MDR with SaaS delivery = faster onboarding
    if cap.get("mdr_service_type") == "Platform MDR":
        base += 0.3
    if cap.get("delivery_model") == "Managed Service":
        base += 0.2
    # IRA sub-pillar scores hint at deployment capability
    sp = cap.get("sub_pillar_scores_v2_1") or cap.get("sub_pillar_scores_current", {})
    ira01 = sp.get("IRA-01", 2.0)
    if isinstance(ira01, (int, float)):
        base += (ira01 - 2.5) * 0.15
    rationale = (f"Onboarding: {kc} deployment keywords. "
                 f"Service type: {cap.get('mdr_service_type','')}.")
    return clamp(base), rationale, "low"

def score_cxq_04(cap, prc):
    """CXQ-04: Customer Success & Expansion"""
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    success_kw = ["customer success", "csm", "qbr", "quarterly business review",
                  "community", "user group", "training", "certification",
                  "academy", "knowledge base", "expansion", "upsell",
                  "customer advisory"]
    kc = keyword_count(txt, success_kw)
    base = 1.5 + kc * 0.3
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    base += (emp - 2.5) * 0.2
    # Outcome maturity from pricing = customer value delivery quality
    if prc:
        omr = prc.get("outcome_maturity_rating_v2", prc.get("outcome_maturity_rating", 2))
        if isinstance(omr, (int, float)):
            base += (omr - 2.5) * 0.25
    rationale = (f"Customer success: {kc} success keywords. "
                 f"Outcome maturity from pricing data factored in.")
    return clamp(base), rationale, "low"

# === MKU: Market Understanding & Vision ===

def score_mku_01(cap, prc):
    """MKU-01: Market Vision & Direction"""
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    vision_kw = ["vision", "strategy", "roadmap", "future", "next-generation",
                 "platform play", "convergence", "security operations",
                 "xdr", "sase", "zero trust", "ai-native", "autonomous",
                 "consolidation", "unified platform"]
    kc = keyword_count(txt, vision_kw)
    base = 1.5 + kc * 0.3
    # Innovation scores as vision proxy
    ps = cap.get("pillar_scores_v2_1") or cap.get("pillar_scores", {})
    aio = ps.get("AIO", 2.0)
    aid = ps.get("AID", 2.0)
    base += (aio + aid - 4.0) * 0.2
    if cap.get("is_ai_first"):
        base += 0.3
    # Larger companies with broad capability = broader vision
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    if emp >= 4.5:
        base += 0.2
    rationale = (f"Market vision: {kc} vision keywords. AIO={aio:.1f}, AID={aid:.1f}. "
                 f"AI-first: {cap.get('is_ai_first', False)}.")
    return clamp(base), rationale, "medium"

def score_mku_02(cap, prc):
    """MKU-02: Product Roadmap & R&D Investment"""
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    rd_kw = ["r&d", "research", "patent", "innovation lab", "labs",
             "roadmap", "next version", "upcoming", "beta", "preview",
             "new capability", "product development"]
    kc = keyword_count(txt, rd_kw)
    # AIO + AID as R&D output proxy
    ps = cap.get("pillar_scores_v2_1") or cap.get("pillar_scores", {})
    aio = ps.get("AIO", 2.0)
    aid = ps.get("AID", 2.0)
    base = (aio + aid) / 2 * 0.6 + kc * 0.25 + 0.5
    # Pricing roadmap signals forward investment
    if prc:
        pr = prc.get("pricing_roadmap", [])
        if pr:
            base += min(len(pr), 3) * 0.15
    rationale = (f"R&D investment: {kc} R&D keywords. "
                 f"AIO={aio:.1f}, AID={aid:.1f} as innovation output proxy.")
    return clamp(base), rationale, "medium"

def score_mku_03(cap, prc):
    """MKU-03: Platform & Ecosystem Strategy"""
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    platform_kw = ["platform", "api", "sdk", "marketplace", "integration",
                   "ecosystem", "plugin", "app store", "open architecture",
                   "siem integration", "soar integration", "xdr platform",
                   "developer", "extensible"]
    kc = keyword_count(txt, platform_kw)
    base = 1.5 + kc * 0.3
    # Telemetry breadth = integration depth
    ts = cap.get("telemetry_sources", [])
    base += min(len(ts), 5) * 0.2
    # Service type
    if cap.get("mdr_service_type") == "Platform MDR":
        base += 0.3
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    if emp >= 4.5:
        base += 0.2
    rationale = (f"Platform strategy: {kc} platform keywords. "
                 f"Telemetry sources: {len(ts)}. Service type: {cap.get('mdr_service_type','')}.")
    return clamp(base), rationale, "medium"

def score_mku_04(cap, prc):
    """MKU-04: Business Model Maturity"""
    base = 2.0
    if prc:
        # Pricing data provides strong business model signals
        pos = prc.get("pricing_overall_score_v2", prc.get("pricing_overall_score", 2.0))
        omr = prc.get("outcome_maturity_rating_v2", prc.get("outcome_maturity_rating", 2))
        if isinstance(pos, (int, float)):
            base = pos * 0.5 + 0.5
        if isinstance(omr, (int, float)):
            base += (omr - 2.0) * 0.2
        # Pricing model diversity
        pmd = prc.get("pricing_model_details", {})
        model_count = sum(1 for k in ["subscription_components", "usage_components",
                                        "fixed_components", "success_fee_components",
                                        "outcome_linked_components"]
                         if pmd.get(k))
        base += model_count * 0.15
        # AI pricing influence = commercial sophistication
        api = prc.get("ai_pricing_influence", 0)
        if isinstance(api, (int, float)):
            base += (api - 2.0) * 0.1
        rationale = (f"Business model: pricing score={pos}, outcome maturity={omr}, "
                     f"model diversity={model_count}, AI pricing influence={api:.1f}.")
    else:
        rationale = "No pricing data available. Minimal business model inference."
    return clamp(base), rationale, "medium" if prc else "low"

# === VIG: Vertical & Geographic Strategy ===

def score_vig_01(cap, prc):
    """VIG-01: Vertical-Specific Solutions"""
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    vert_kw = ["healthcare", "hipaa", "hitrust", "financial", "pci", "banking",
               "government", "fedramp", "defense", "manufacturing", "retail",
               "energy", "education", "legal", "pharma", "insurance",
               "vertical", "industry-specific", "sector"]
    kc = keyword_count(txt, vert_kw)
    # SOG-03 = compliance certifications
    sp = cap.get("sub_pillar_scores_v2_1") or cap.get("sub_pillar_scores_current", {})
    sog03 = sp.get("SOG-03", 2.0)
    if isinstance(sog03, (int, float)):
        base = sog03 * 0.4 + kc * 0.3 + 0.5
    else:
        base = 1.5 + kc * 0.3
    if cap.get("target_market") == "Enterprise":
        base += 0.2
    rationale = (f"Vertical solutions: {kc} vertical keywords. SOG-03={sog03}.")
    return clamp(base), rationale, "low"

def score_vig_02(cap, prc):
    """VIG-02: Industry Concentration & References"""
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    # Count distinct verticals mentioned
    verticals = ["healthcare", "financial", "government", "manufacturing",
                 "retail", "energy", "education", "technology", "media",
                 "telecom", "transportation", "legal", "pharma"]
    vert_count = sum(1 for v in verticals if v in txt)
    base = 1.0 + vert_count * 0.4
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    if emp >= 4.0:
        base += 0.3
    rationale = (f"Industry concentration: {vert_count} distinct verticals mentioned in evidence.")
    return clamp(base), rationale, "low"

def score_vig_03(cap, prc):
    """VIG-03: Regional & Global Coverage"""
    region = cap.get("region", "")
    hq = cap.get("headquarters", "").lower()
    base = REGION_REACH.get(region, 2.0)
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    # SOC location signals
    soc_kw = ["soc in", "data center", "data residency", "gdpr",
              "eu data", "data sovereignty", "follow-the-sun",
              "multi-region", "regional soc", "global soc"]
    kc = keyword_count(txt, soc_kw)
    base += kc * 0.25
    # Large global vendors
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    if emp >= 4.5 and region in ("Global", "North America"):
        base += 0.3
    rationale = (f"Regional coverage: region={region}, {kc} SOC/data residency keywords.")
    return clamp(base), rationale, "medium"

def score_vig_04(cap, prc):
    """VIG-04: Localization & Regional Adaptation"""
    region = cap.get("region", "")
    txt = text_lower(cap, "description", "key_differentiators", "capability_analysis")
    local_kw = ["multi-language", "localized", "japanese", "german", "french",
                "spanish", "portuguese", "korean", "chinese", "local partner",
                "regional partner", "in-country", "native language"]
    kc = keyword_count(txt, local_kw)
    if region == "Global":
        base = 3.0
    elif region in ("Europe", "Asia-Pacific"):
        base = 2.5
    else:
        base = 1.5
    base += kc * 0.4
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    if emp >= 4.5:
        base += 0.3
    rationale = (f"Localization: {kc} localization keywords. Region={region}.")
    return clamp(base), rationale, "low"


# ── Scoring dispatch table ───────────────────────────────────────────

SCORING_FUNCTIONS = {
    "VIA-01": score_via_01, "VIA-02": score_via_02,
    "VIA-03": score_via_03, "VIA-04": score_via_04,
    "SLE-01": score_sle_01, "SLE-02": score_sle_02,
    "SLE-03": score_sle_03, "SLE-04": score_sle_04,
    "MKR-01": score_mkr_01, "MKR-02": score_mkr_02,
    "MKR-03": score_mkr_03, "MKR-04": score_mkr_04,
    "MKE-01": score_mke_01, "MKE-02": score_mke_02,
    "MKE-03": score_mke_03, "MKE-04": score_mke_04,
    "CXQ-01": score_cxq_01, "CXQ-02": score_cxq_02,
    "CXQ-03": score_cxq_03, "CXQ-04": score_cxq_04,
    "MKU-01": score_mku_01, "MKU-02": score_mku_02,
    "MKU-03": score_mku_03, "MKU-04": score_mku_04,
    "VIG-01": score_vig_01, "VIG-02": score_vig_02,
    "VIG-03": score_vig_03, "VIG-04": score_vig_04,
}

PILLAR_SUB_MAP = {
    "VIA": ["VIA-01", "VIA-02", "VIA-03", "VIA-04"],
    "SLE": ["SLE-01", "SLE-02", "SLE-03", "SLE-04"],
    "MKR": ["MKR-01", "MKR-02", "MKR-03", "MKR-04"],
    "MKE": ["MKE-01", "MKE-02", "MKE-03", "MKE-04"],
    "CXQ": ["CXQ-01", "CXQ-02", "CXQ-03", "CXQ-04"],
    "MKU": ["MKU-01", "MKU-02", "MKU-03", "MKU-04"],
    "VIG": ["VIG-01", "VIG-02", "VIG-03", "VIG-04"],
}


# ── Main processing ──────────────────────────────────────────────────

def process_vendor(seed_vendor):
    """Score all 28 gap sub-pillars for one vendor."""
    vname = seed_vendor["vendor"]
    cap = cap_by_vendor.get(vname, {})
    prc = pricing_by_vendor.get(vname)

    sub_scores = {}
    pillar_scores = {}
    rationales = {}

    for pillar_id, sp_ids in PILLAR_SUB_MAP.items():
        pillar_rationales = {}
        sp_score_list = []
        for sp_id in sp_ids:
            fn = SCORING_FUNCTIONS[sp_id]
            score, rationale, confidence = fn(cap, prc)
            sub_scores[sp_id] = score
            sp_score_list.append(score)
            pillar_rationales[sp_id] = {
                "score": score,
                "rationale": rationale,
                "evidence_sources": ["Derived from existing MDR capability and pricing data"],
                "confidence": confidence
            }
        pillar_scores[pillar_id] = round(sum(sp_score_list) / len(sp_score_list), 2)
        rationales[pillar_id] = pillar_rationales

    # Determine overall confidence
    all_confs = [r["confidence"] for prats in rationales.values()
                 for r in prats.values()]
    high_count = all_confs.count("high")
    med_count = all_confs.count("medium")
    if high_count + med_count >= 20:
        overall_conf = "medium"
    elif high_count + med_count >= 10:
        overall_conf = "medium"
    else:
        overall_conf = "low"

    # Update seed vendor
    seed_vendor["mq_gap_pillar_scores"] = pillar_scores
    seed_vendor["mq_gap_sub_pillar_scores"] = sub_scores
    seed_vendor["mq_gap_rationales"] = rationales
    seed_vendor["mq_gap_research_status"] = "auto_derived"
    seed_vendor["mq_gap_research_confidence"] = overall_conf
    seed_vendor["mq_gap_derivation_method"] = "heuristic_from_existing_mdr_data"

    return seed_vendor


def main():
    print("Loading source data...")
    print(f"  Capability vendors: {len(cap_data['vendors'])}")
    print(f"  Pricing vendors: {len(prc_data['vendors'])}")
    print(f"  Seed vendors: {len(seed_data['vendors'])}")

    print(f"\nScoring {len(seed_data['vendors'])} vendors across 28 gap sub-pillars...")

    processed = []
    score_stats = {sp: [] for sp in SCORING_FUNCTIONS}

    for i, sv in enumerate(seed_data["vendors"]):
        result = process_vendor(sv)
        processed.append(result)
        for sp_id, score in result["mq_gap_sub_pillar_scores"].items():
            score_stats[sp_id].append(score)
        if (i + 1) % 25 == 0:
            print(f"  Processed {i+1}/{len(seed_data['vendors'])}...")

    # Sort by vendor name
    processed.sort(key=lambda x: x["vendor"])

    # Build output
    output = {
        "schema_ref": "MQ_Gap_Schema_1_0.json",
        "schema_version": "1.0",
        "source_schema": "MDR",
        "assessment_type": "mq_gap_researched",
        "description": "MQ Gap criteria scores derived from existing MDR capability and pricing data using rule-based heuristics. All 28 sub-pillars scored for all vendors.",
        "derivation_method": "Heuristic scoring using existing vendor metadata, capability pillar/sub-pillar scores, pricing data, text mining of descriptions/differentiators/capability analysis.",
        "source_files": [
            "MDR Services Vendor 2-1 Consolidated.json",
            "MDR Services Vendor Pricing 2-1 AI Enriched.json"
        ],
        "vendor_count": len(processed),
        "gap_pillars": list(PILLAR_SUB_MAP.keys()),
        "gap_sub_pillars": list(SCORING_FUNCTIONS.keys()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script": "build_mq_gap_researched.py",
        "vendors": processed
    }

    out_file = ROOT / "MDR Services Vendor MQ Gap 2-0 Researched.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nGenerated {out_file.name}")
    print(f"  Vendors: {len(processed)}")

    # Print sub-pillar score distribution
    print(f"\n  Sub-pillar score ranges:")
    for sp_id in sorted(score_stats):
        scores = score_stats[sp_id]
        avg = sum(scores) / len(scores)
        lo = min(scores)
        hi = max(scores)
        print(f"    {sp_id}: avg={avg:.1f}  min={lo:.1f}  max={hi:.1f}")

    # Pillar averages
    print(f"\n  Pillar averages across all vendors:")
    for pid in PILLAR_SUB_MAP:
        sp_avgs = []
        for sp_id in PILLAR_SUB_MAP[pid]:
            sp_avgs.append(sum(score_stats[sp_id]) / len(score_stats[sp_id]))
        print(f"    {pid}: {sum(sp_avgs)/len(sp_avgs):.2f}")

    # Tier breakdown
    tiers = {}
    for sv in processed:
        t = sv.get("mq_gap_research_tier", "unknown")
        tiers[t] = tiers.get(t, 0) + 1
    print(f"\n  Tier distribution:")
    for t in sorted(tiers):
        print(f"    {t}: {tiers[t]}")


if __name__ == "__main__":
    main()
