#!/usr/bin/env python3
"""
_research_cnapp_mq.py — CNAPP MQ Gap 1-1 Researched
====================================================
Derives the 27 CNAPP MQ Gap sub-pillar scores (VIA, SLE, MKR, MKE, CXQ,
MKU, VIG) from existing CNAPP capability data + vendor metadata using
rule-based heuristics. Mirrors build_mq_gap_researched.py (MDR) but
adapted for CNAPP-specific signals (no pricing schema, CNAPP-flavored
keywords, hyperscaler/marketplace/cloud-native signals).

Sources:
  1. CNAPP Vendor 1-2 Researched.json   (capability + metadata)
  2. CNAPP MQ Vendor 1-0 Seed.json      (template — 24 vendors)
  3. CNAPP_MQ_Gap_Schema_App.json       (schema reference)

Output: CNAPP MQ Vendor 1-1 Researched.json
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ── Load source data ─────────────────────────────────────────────────

def load_json(name):
    with open(ROOT / name, "r", encoding="utf-8") as f:
        return json.load(f)

cap_data  = load_json("CNAPP Vendor 1-2 Researched.json")
seed_data = load_json("CNAPP MQ Vendor 1-0 Seed.json")

cap_by_vendor = {v["vendor"]: v for v in cap_data["vendors"]}

# ── Helpers ──────────────────────────────────────────────────────────

def clamp(val, lo=0.0, hi=5.0):
    return max(lo, min(hi, round(val, 1)))

def text_lower(v, *keys):
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
    return sum(1 for kw in keywords if kw.lower() in text)

EMPLOYEE_SIZE_ORDER = {
    "1-10": 1, "10-50": 1.5, "50-100": 2, "50-200": 2,
    "100-200": 2.5, "100-500": 2.7, "200-500": 3, "200-1000": 3.2,
    "500-1000": 3.5, "500-2000": 3.7, "1000-5000": 4,
    "1000-10000": 4.3, "5000-10000": 4.5, "10000+": 5,
}

FUNDING_STAGE_VIABILITY = {
    "IPO": 5.0, "Public": 5.0, "PE-Backed": 4.0, "Acquired": 3.5,
    "Subsidiary": 3.5, "Late Stage VC": 3.5,
    "Series F": 3.5, "Series E": 3.3, "Series D": 3.0,
    "Series C": 2.8, "Series B": 2.3, "Series A": 1.8,
    "Seed": 1.3, "Pre-Seed": 1.0, "Private": 3.0,
    "Bootstrapped": 2.5,
}

REGION_REACH = {
    "Global": 5, "North America": 3, "Europe": 3, "Asia-Pacific": 3,
    "Middle East": 2, "Latin America": 2, "Africa": 2, "Oceania": 2,
    "Israel": 2.5,
}

# ── Capability helpers ───────────────────────────────────────────────

def get_pillar(cap, code):
    ps = cap.get("pillar_scores", {})
    v = ps.get(code, 2.0)
    return v if isinstance(v, (int, float)) else 2.0

def get_sub(cap, code):
    sp = cap.get("sub_pillar_scores_current", {})
    v = sp.get(code, 2.0)
    return v if isinstance(v, (int, float)) else 2.0

def cap_avg(cap):
    ps = cap.get("pillar_scores", {})
    nums = [v for v in ps.values() if isinstance(v, (int, float))]
    return sum(nums) / len(nums) if nums else 2.0

def parse_total_funding(tf):
    """Extract dollar amount in millions. '$1.9B' -> 1900, '$300M' -> 300."""
    if not tf:
        return 0
    t = tf.lower().replace(",", "").replace("$", "")
    m = re.search(r"([\d.]+)\s*([bm])", t)
    if not m:
        return 0
    n = float(m.group(1))
    return n * 1000 if m.group(2) == "b" else n

# ── Sub-pillar scoring ───────────────────────────────────────────────

# === VIA: Financial Viability ===

def score_via_01(cap):
    """VIA-01: Revenue & Cloud-Security Growth Trajectory"""
    funding = cap.get("funding_stage", "")
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    base = FUNDING_STAGE_VIABILITY.get(funding, 2.0)
    if funding == "IPO":
        base = 4.0
    elif funding in ("PE-Backed", "Subsidiary", "Acquired"):
        base = 3.0
    base += (emp - 2.5) * 0.3
    txt = text_lower(cap, "description", "key_differentiators")
    growth_kw = ["fastest growing", "fastest-growing", "hypergrowth", "rapid growth",
                 "billion", "unicorn", "market leader", "industry leader",
                 "leader", "dominant", "fastest"]
    base += keyword_count(txt, growth_kw) * 0.25
    tf_m = parse_total_funding(cap.get("total_funding", ""))
    if tf_m >= 1500:
        base += 0.7
    elif tf_m >= 500:
        base += 0.4
    elif tf_m >= 100:
        base += 0.2
    rationale = (f"Funding: {funding}, Size: {cap.get('employee_count_range','?')}, "
                 f"Total funding: {cap.get('total_funding','n/a')}.")
    return clamp(base), rationale, "medium"

def score_via_02(cap):
    """VIA-02: Profitability & Cash Position"""
    funding = cap.get("funding_stage", "")
    emp = cap.get("employee_count_range", "")
    if funding == "IPO" and emp in ("5000-10000", "10000+"):
        score = 4.5
    elif funding == "IPO":
        score = 4.0
    elif funding in ("PE-Backed", "Subsidiary"):
        score = 3.5
    elif funding == "Acquired":
        score = 3.0
    elif funding in ("Series E", "Series F", "Late Stage VC"):
        score = 2.8
    elif funding in ("Series C", "Series D"):
        score = 2.3
    elif funding in ("Series A", "Series B"):
        score = 1.8
    else:
        score = FUNDING_STAGE_VIABILITY.get(funding, 2.0) - 0.3
    tf_m = parse_total_funding(cap.get("total_funding", ""))
    if tf_m >= 1000:
        score = max(score, 3.5)
    rationale = (f"Funding stage {funding}; total funding {cap.get('total_funding','n/a')}.")
    return clamp(score), rationale, "medium"

def score_via_03(cap):
    """VIA-03: Customer Base & Retention"""
    txt = text_lower(cap, "description", "key_differentiators")
    cust_kw = ["customer", "fortune 500", "fortune 100", "global 2000",
               "thousands of", "enterprise customers", "peer insights",
               "g2", "trusted by"]
    kc = keyword_count(txt, cust_kw)
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    base = emp * 0.55 + kc * 0.3
    if cap.get("funding_stage") in ("IPO", "Public"):
        base = max(base, 3.5)
    if cap.get("target_market") == "Enterprise":
        base += 0.3
    rationale = (f"Customer base inferred from size ({cap.get('employee_count_range','?')}) "
                 f"and funding stage; {kc} customer-base keywords.")
    return clamp(base), rationale, "low"

def score_via_04(cap):
    """VIA-04: CNAPP Investment Commitment"""
    # Pure-Play CNAPP vendors are 100% committed; platform vendors prove via R&D
    vt = cap.get("cnapp_vendor_type", "")
    if vt == "Pure-Play CNAPP":
        base = 4.5
    elif vt in ("Hyperscaler-Native CNAPP", "Platform Vendor with CNAPP"):
        base = 3.5
    elif vt == "Adjacent (Container/Workload Specialist)":
        base = 3.0
    else:
        base = 2.5
    avg = cap_avg(cap)
    base += (avg - 2.5) * 0.4
    if cap.get("is_ai_first"):
        base += 0.3
    txt = text_lower(cap, "description", "key_differentiators")
    invest_kw = ["acquisition", "acquired", "invested", "expanded platform",
                 "new capability", "launched", "rolled out", "released"]
    base += keyword_count(txt, invest_kw) * 0.15
    rationale = (f"CNAPP commitment: vendor type={vt}, avg cap={avg:.2f}.")
    return clamp(base), rationale, "medium"

# === SLE: Sales Execution & Channel ===

def score_sle_01(cap):
    """SLE-01: Hyperscaler & Cloud Marketplace Reach"""
    txt = text_lower(cap, "description", "key_differentiators")
    hs_kw = ["aws", "azure", "google cloud", "gcp", "marketplace",
             "co-sell", "isv accelerate", "azure marketplace",
             "aws marketplace", "google marketplace", "hyperscaler",
             "cloud-native", "multi-cloud"]
    kc = keyword_count(txt, hs_kw)
    cc = (cap.get("cloud_coverage") or "").lower()
    base = 1.5 + kc * 0.25
    if "multi-cloud" in cc or "multicloud" in cc:
        base += 0.7
    elif "hybrid" in cc:
        base += 0.4
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    base += (emp - 2.5) * 0.2
    if cap.get("funding_stage") in ("IPO", "Public"):
        base += 0.3
    rationale = (f"Hyperscaler reach: {kc} marketplace/co-sell keywords; cloud coverage={cc}.")
    return clamp(base), rationale, "medium"

def score_sle_02(cap):
    """SLE-02: MSP/MSSP Channel Strategy"""
    txt = text_lower(cap, "description", "key_differentiators")
    chan_kw = ["mssp", "msp", "channel", "partner program", "reseller",
               "service provider", "managed service", "alliance",
               "distribution"]
    kc = keyword_count(txt, chan_kw)
    base = 1.5 + kc * 0.4
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    base += (emp - 2.5) * 0.2
    if cap.get("cnapp_vendor_type") == "Platform Vendor with CNAPP":
        base += 0.5
    rationale = (f"MSP/MSSP channel: {kc} channel keywords."
                 f" Vendor type: {cap.get('cnapp_vendor_type','?')}.")
    return clamp(base), rationale, "low"

def score_sle_03(cap):
    """SLE-03: Self-Serve / Free-Trial Motion"""
    txt = text_lower(cap, "description", "key_differentiators")
    selfsvc_kw = ["free trial", "free tier", "self-service", "agentless",
                  "15-minute", "minutes to deploy", "quick start",
                  "freemium", "try free", "no agent"]
    kc = keyword_count(txt, selfsvc_kw)
    base = 1.5 + kc * 0.45
    dm = (cap.get("deployment_model") or "").lower()
    if "agentless" in dm:
        base += 0.6
    elif "hybrid" in dm:
        base += 0.3
    if cap.get("cnapp_vendor_type") == "Pure-Play CNAPP":
        base += 0.3
    rationale = (f"Self-serve motion: {kc} self-serve keywords; deployment={dm}.")
    return clamp(base), rationale, "low"

def score_sle_04(cap):
    """SLE-04: Enterprise Field Sales Coverage"""
    region = cap.get("region", "")
    base = REGION_REACH.get(region, 2.0)
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    base += (emp - 2.5) * 0.3
    if cap.get("target_market") == "Enterprise":
        base += 0.5
    txt = text_lower(cap, "description", "key_differentiators")
    geo_kw = ["global", "worldwide", "international", "regional offices",
              "field sales", "americas", "emea", "apac"]
    base += keyword_count(txt, geo_kw) * 0.2
    rationale = (f"Field sales: region={region}, size={cap.get('employee_count_range','?')}.")
    return clamp(base), rationale, "low"

# === MKR: Market Responsiveness & Track Record ===

def score_mkr_01(cap):
    """MKR-01: Cloud-Threat Trend Responsiveness"""
    txt = text_lower(cap, "description", "key_differentiators")
    trend_kw = ["ai-spm", "dspm", "ciem", "agentless", "runtime",
                "cloud detection", "cdr", "ai security", "llm security",
                "ai-native", "generative ai", "kubernetes", "serverless"]
    kc = keyword_count(txt, trend_kw)
    base = 1.5 + kc * 0.25
    # Capability breadth = trend coverage
    avg = cap_avg(cap)
    base += (avg - 2.5) * 0.4
    if cap.get("is_ai_first"):
        base += 0.4
    rationale = (f"Trend responsiveness: {kc} trend keywords; avg cap={avg:.2f}; "
                 f"AI-first: {cap.get('is_ai_first', False)}.")
    return clamp(base), rationale, "medium"

def score_mkr_02(cap):
    """MKR-02: Multi-Cloud & Coverage Expansion"""
    cc = (cap.get("cloud_coverage") or "").lower()
    base = 2.0
    if "multi-cloud" in cc or "multicloud" in cc:
        base = 4.0
    elif "hybrid" in cc:
        base = 3.0
    elif "single" in cc:
        base = 2.0
    txt = text_lower(cap, "description", "key_differentiators")
    cov_kw = ["aws", "azure", "google cloud", "gcp", "oracle cloud",
              "alibaba", "openstack", "openshift", "private cloud",
              "kubernetes", "containers", "serverless", "lambda"]
    kc = keyword_count(txt, cov_kw)
    base += kc * 0.15
    rationale = (f"Coverage expansion: cloud_coverage={cc}; {kc} cloud platform keywords.")
    return clamp(base), rationale, "medium"

def score_mkr_03(cap):
    """MKR-03: M&A & Convergence Activity"""
    txt = text_lower(cap, "description", "key_differentiators")
    ma_kw = ["acquired", "acquisition", "merger", "merged", "bought",
             "strategic investment", "joint venture", "consolidation"]
    kc = keyword_count(txt, ma_kw)
    base = 1.5 + kc * 0.4
    funding = cap.get("funding_stage", "")
    if funding in ("IPO", "Public", "Subsidiary", "Acquired", "PE-Backed"):
        base += 0.6
    if cap.get("cnapp_vendor_type") == "Platform Vendor with CNAPP":
        base += 0.5  # platforms typically grow via M&A
    rationale = (f"M&A/convergence: {kc} M&A keywords; funding={funding}.")
    return clamp(base), rationale, "low"

def score_mkr_04(cap):
    """MKR-04: Release Cadence & Roadmap Velocity"""
    txt = text_lower(cap, "description", "key_differentiators")
    vel_kw = ["weekly", "monthly", "release", "launched", "new",
              "continuous", "agile", "rapid", "roadmap", "preview",
              "ga", "general availability"]
    kc = keyword_count(txt, vel_kw)
    base = 2.0 + kc * 0.2
    # Innovation pillars (FRNG, DSPM) = velocity proxy
    frng = get_pillar(cap, "FRNG")
    dspm = get_pillar(cap, "DSPM")
    base += (frng + dspm - 4.0) * 0.25
    if cap.get("is_ai_first"):
        base += 0.3
    rationale = (f"Release velocity: {kc} cadence keywords; FRNG={frng}, DSPM={dspm}.")
    return clamp(base), rationale, "low"

# === MKE: Marketing Execution & Brand ===

def score_mke_01(cap):
    """MKE-01: Brand Awareness & Industry Recognition"""
    funding = cap.get("funding_stage", "")
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    txt = text_lower(cap, "description", "key_differentiators")
    rec_kw = ["leader", "magic quadrant", "forrester wave", "idc marketscape",
              "gartner", "forrester", "idc", "named", "recognized",
              "award", "fastest growing", "industry-leading"]
    kc = keyword_count(txt, rec_kw)
    base = emp * 0.5 + kc * 0.3
    if funding in ("IPO", "Public"):
        base += 0.7
    if cap.get("cnapp_vendor_type") == "Pure-Play CNAPP":
        base += 0.3
    avg = cap_avg(cap)
    base += (avg - 2.5) * 0.2
    rationale = (f"Brand: {kc} recognition keywords; size={cap.get('employee_count_range','?')}; funding={funding}.")
    return clamp(base), rationale, "medium"

def score_mke_02(cap):
    """MKE-02: Cloud-Threat Research Output"""
    txt = text_lower(cap, "description", "key_differentiators")
    res_kw = ["threat research", "research team", "labs", "threat intelligence",
              "annual report", "threat landscape", "vulnerability research",
              "cves", "zero-day", "blog", "publication"]
    kc = keyword_count(txt, res_kw)
    base = 1.5 + kc * 0.35
    cdr = get_pillar(cap, "CDR")
    base += (cdr - 2.5) * 0.3
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    if emp >= 4:
        base += 0.3
    rationale = (f"Research output: {kc} research keywords; CDR={cdr}.")
    return clamp(base), rationale, "low"

def score_mke_03(cap):
    """MKE-03: Conference & Event Presence"""
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    funding = cap.get("funding_stage", "")
    txt = text_lower(cap, "description", "key_differentiators")
    event_kw = ["rsa", "re:inforce", "kubecon", "black hat", "conference",
                "summit", "ignite", "fal.con", "explore", "velocity",
                "sponsor", "keynote"]
    kc = keyword_count(txt, event_kw)
    base = emp * 0.45 + kc * 0.45
    if funding in ("IPO", "Public"):
        base += 0.5
    rationale = (f"Event presence: {kc} event keywords; size proxy used.")
    return clamp(base), rationale, "low"

def score_mke_04(cap):
    """MKE-04: Digital Presence & Messaging Clarity"""
    desc_len = len(cap.get("description", "") or "")
    diff_len = len(cap.get("key_differentiators", "") or "")
    base = 2.0
    if desc_len > 250:
        base += 0.6
    elif desc_len > 100:
        base += 0.3
    if diff_len > 150:
        base += 0.6
    elif diff_len > 50:
        base += 0.3
    pn = cap.get("product_names") or []
    if len(pn) >= 3:
        base += 0.3
    elif len(pn) >= 1:
        base += 0.15
    if cap.get("website"):
        base += 0.2
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    base += (emp - 2.5) * 0.15
    rationale = (f"Digital presence: desc_len={desc_len}, diff_len={diff_len}, products={len(pn)}.")
    return clamp(base), rationale, "low"

# === CXQ: Customer Experience Quality ===

def score_cxq_01(cap):
    """CXQ-01: Peer Review Ratings (Gartner Peer Insights, G2)"""
    txt = text_lower(cap, "description", "key_differentiators")
    rev_kw = ["peer insights", "g2", "trustradius", "peerspot",
              "customers' choice", "leader badge", "high performer",
              "rated"]
    kc = keyword_count(txt, rev_kw)
    avg = cap_avg(cap)
    base = avg * 0.4 + kc * 0.4 + 0.5
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    if emp >= 4:
        base += 0.2
    rationale = (f"Peer reviews: {kc} review platform keywords; capability avg={avg:.2f}.")
    return clamp(base), rationale, "low"

def score_cxq_02(cap):
    """CXQ-02: Onboarding & Time-to-Value"""
    txt = text_lower(cap, "description", "key_differentiators")
    onb_kw = ["agentless", "15-minute", "minutes", "rapid deployment",
              "quick start", "time-to-value", "onboarding", "deploy in",
              "no agent", "cloud connector", "instant"]
    kc = keyword_count(txt, onb_kw)
    base = 2.0 + kc * 0.4
    dm = (cap.get("deployment_model") or "").lower()
    if "agentless" in dm:
        base += 0.7
    elif "hybrid" in dm:
        base += 0.3
    rationale = (f"Onboarding: {kc} TTV keywords; deployment_model={dm}.")
    return clamp(base), rationale, "medium"

def score_cxq_03(cap):
    """CXQ-03: Support & Customer Success Programs"""
    txt = text_lower(cap, "description", "key_differentiators")
    sup_kw = ["24/7", "dedicated", "tam", "csm", "customer success",
              "premium support", "sla", "follow-the-sun",
              "support engineer", "training", "academy"]
    kc = keyword_count(txt, sup_kw)
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    base = 1.5 + kc * 0.3 + (emp - 2.5) * 0.3
    if cap.get("funding_stage") in ("IPO", "Public"):
        base += 0.4
    rationale = (f"Support quality: {kc} support keywords; size={cap.get('employee_count_range','?')}.")
    return clamp(base), rationale, "low"

def score_cxq_04(cap):
    """CXQ-04: Operational Reliability (uptime, agent stability)"""
    avg = cap_avg(cap)
    cwpp = get_pillar(cap, "CWPP")
    cspm = get_pillar(cap, "CSPM")
    base = (cwpp + cspm) / 2 * 0.5 + avg * 0.3
    txt = text_lower(cap, "description", "key_differentiators")
    rel_kw = ["uptime", "high availability", "redundancy", "fault tolerant",
              "scalable", "production-ready", "enterprise-grade"]
    base += keyword_count(txt, rel_kw) * 0.25
    if cap.get("funding_stage") in ("IPO", "Public", "Subsidiary"):
        base += 0.3
    rationale = (f"Reliability: CWPP={cwpp}, CSPM={cspm}; capability avg={avg:.2f}.")
    return clamp(base), rationale, "low"

# === MKU: Market Understanding & Vision (3 sub-pillars in v1.0) ===

def score_mku_01(cap):
    """MKU-01: CNAPP Convergence Vision Articulation"""
    txt = text_lower(cap, "description", "key_differentiators")
    vis_kw = ["unified platform", "cnapp", "consolidation", "convergence",
              "single platform", "platform play", "code-to-cloud",
              "shift left", "runtime", "ai-spm", "graph", "context",
              "vision", "strategy"]
    kc = keyword_count(txt, vis_kw)
    base = 1.5 + kc * 0.25
    avg = cap_avg(cap)
    base += (avg - 2.5) * 0.4
    breadth = cap.get("capability_coverage_count", 0) or 0
    base += min(breadth, 7) * 0.1
    if cap.get("is_ai_first"):
        base += 0.3
    rationale = (f"Convergence vision: {kc} vision keywords; coverage={breadth}/7; cap avg={avg:.2f}.")
    return clamp(base), rationale, "medium"

def score_mku_02(cap):
    """MKU-02: Roadmap & Innovation Investment"""
    frng = get_pillar(cap, "FRNG")
    dspm = get_pillar(cap, "DSPM")
    cdr = get_pillar(cap, "CDR")
    base = (frng * 0.4 + dspm * 0.3 + cdr * 0.3) * 0.7 + 0.5
    txt = text_lower(cap, "description", "key_differentiators")
    rd_kw = ["roadmap", "patent", "research", "labs", "ai", "llm",
             "generative", "next-generation", "innovative", "novel"]
    base += keyword_count(txt, rd_kw) * 0.2
    if cap.get("is_ai_first"):
        base += 0.4
    rationale = (f"Innovation roadmap: FRNG={frng}, DSPM={dspm}, CDR={cdr}; AI-first={cap.get('is_ai_first', False)}.")
    return clamp(base), rationale, "medium"

def score_mku_03(cap):
    """MKU-03: Ecosystem & API/Integration Strategy"""
    txt = text_lower(cap, "description", "key_differentiators")
    eco_kw = ["api", "sdk", "integration", "marketplace", "ecosystem",
              "siem", "soar", "ticketing", "jira", "servicenow",
              "slack", "teams", "webhook", "open architecture",
              "extensible", "developer"]
    kc = keyword_count(txt, eco_kw)
    base = 1.5 + kc * 0.3
    # SHIFT-05 (ticketing) and FRNG-02 (api security) as proxies
    s05 = get_sub(cap, "SHIFT-05")
    base += (s05 - 2.5) * 0.3
    if cap.get("cnapp_vendor_type") == "Pure-Play CNAPP":
        base += 0.2
    rationale = (f"Ecosystem strategy: {kc} integration keywords; SHIFT-05={s05}.")
    return clamp(base), rationale, "medium"

# === VIG: Vertical & Geographic Strategy ===

def score_vig_01(cap):
    """VIG-01: Regulated Vertical Solutions (FedRAMP, HIPAA, PCI)"""
    txt = text_lower(cap, "description", "key_differentiators")
    vert_kw = ["fedramp", "il5", "hipaa", "hitrust", "pci", "pci-dss",
               "soc 2", "iso 27001", "fisma", "stig", "cmmc",
               "healthcare", "financial services", "public sector",
               "government", "defense", "regulated"]
    kc = keyword_count(txt, vert_kw)
    cspm = get_pillar(cap, "CSPM")
    base = 1.0 + kc * 0.3 + (cspm - 2.5) * 0.3
    if cap.get("funding_stage") in ("IPO", "Public", "Subsidiary"):
        base += 0.4
    rationale = (f"Regulated verticals: {kc} compliance keywords; CSPM={cspm}.")
    return clamp(base), rationale, "low"

def score_vig_02(cap):
    """VIG-02: Industry Concentration & References"""
    txt = text_lower(cap, "description", "key_differentiators")
    verticals = ["healthcare", "financial", "government", "manufacturing",
                 "retail", "energy", "education", "technology", "media",
                 "telecom", "transportation", "pharma", "insurance"]
    vc = sum(1 for v in verticals if v in txt)
    base = 1.0 + vc * 0.4
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    if emp >= 4:
        base += 0.3
    rationale = (f"Industry concentration: {vc} distinct verticals mentioned."
                 )
    return clamp(base), rationale, "low"

def score_vig_03(cap):
    """VIG-03: Regional Cloud Region & Data Residency Coverage"""
    region = cap.get("region", "")
    base = REGION_REACH.get(region, 2.0)
    txt = text_lower(cap, "description", "key_differentiators")
    geo_kw = ["data residency", "data sovereignty", "gdpr", "eu data",
              "regional", "multi-region", "govcloud", "sovereign cloud",
              "in-region", "data center"]
    kc = keyword_count(txt, geo_kw)
    base += kc * 0.3
    emp = EMPLOYEE_SIZE_ORDER.get(cap.get("employee_count_range", ""), 2.0)
    if emp >= 4 and region in ("Global", "North America", "Europe"):
        base += 0.4
    rationale = (f"Regional coverage: region={region}; {kc} residency keywords.")
    return clamp(base), rationale, "medium"

def score_vig_04(cap):
    """VIG-04: Localization & Regional Adaptation"""
    region = cap.get("region", "")
    txt = text_lower(cap, "description", "key_differentiators")
    loc_kw = ["multi-language", "localized", "japanese", "german", "french",
              "spanish", "korean", "chinese", "regional partner",
              "in-country", "native language", "european", "apac"]
    kc = keyword_count(txt, loc_kw)
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
    rationale = (f"Localization: {kc} localization keywords; region={region}.")
    return clamp(base), rationale, "low"

# ── Dispatch ─────────────────────────────────────────────────────────

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
    "MKU-03": score_mku_03,
    "VIG-01": score_vig_01, "VIG-02": score_vig_02,
    "VIG-03": score_vig_03, "VIG-04": score_vig_04,
}

PILLAR_SUB_MAP = {
    "VIA": ["VIA-01", "VIA-02", "VIA-03", "VIA-04"],
    "SLE": ["SLE-01", "SLE-02", "SLE-03", "SLE-04"],
    "MKR": ["MKR-01", "MKR-02", "MKR-03", "MKR-04"],
    "MKE": ["MKE-01", "MKE-02", "MKE-03", "MKE-04"],
    "CXQ": ["CXQ-01", "CXQ-02", "CXQ-03", "CXQ-04"],
    "MKU": ["MKU-01", "MKU-02", "MKU-03"],
    "VIG": ["VIG-01", "VIG-02", "VIG-03", "VIG-04"],
}

# ── Main ─────────────────────────────────────────────────────────────

def process_vendor(seed_v):
    vname = seed_v["vendor"]
    cap = cap_by_vendor.get(vname, {})
    if not cap:
        # No capability data — still score from seed metadata only
        cap = {k: seed_v.get(k) for k in ("description", "key_differentiators",
                                          "funding_stage", "employee_count_range",
                                          "region", "target_market", "year_founded",
                                          "total_funding", "cnapp_vendor_type",
                                          "cloud_coverage", "deployment_model")}
        cap["pillar_scores"] = (seed_v.get("existing_data_hints") or {}).get("pillar_scores", {})

    sub_scores = {}
    pillar_scores = {}
    rationales = {}

    for pillar_id, sp_ids in PILLAR_SUB_MAP.items():
        prats = {}
        sp_list = []
        for sp_id in sp_ids:
            score, rationale, conf = SCORING_FUNCTIONS[sp_id](cap)
            sub_scores[sp_id] = score
            sp_list.append(score)
            prats[sp_id] = {
                "score": score,
                "rationale": rationale,
                "evidence_sources": ["Derived from CNAPP capability data + vendor metadata"],
                "confidence": conf,
            }
        pillar_scores[pillar_id] = round(sum(sp_list) / len(sp_list), 2)
        rationales[pillar_id] = prats

    # Overall confidence
    confs = [r["confidence"] for prats in rationales.values() for r in prats.values()]
    med_high = confs.count("high") + confs.count("medium")
    overall = "medium" if med_high >= 12 else "low"

    seed_v["mq_gap_pillar_scores"] = pillar_scores
    seed_v["mq_gap_sub_pillar_scores"] = sub_scores
    seed_v["mq_gap_rationales"] = rationales
    # Aliases so generic Schema Viewer (which expects pillar_scores /
    # sub_pillar_scores_current) renders the MQ gap scores correctly.
    seed_v["pillar_scores"] = pillar_scores
    seed_v["sub_pillar_scores_current"] = sub_scores
    seed_v["mq_gap_research_status"] = "auto_derived"
    seed_v["mq_gap_research_tier"] = "tier_2"
    seed_v["mq_gap_research_confidence"] = overall
    seed_v["mq_gap_derivation_method"] = "heuristic_from_cnapp_capability_data"
    return seed_v


def main():
    print(f"Loading source data...")
    print(f"  CNAPP capability vendors: {len(cap_data['vendors'])}")
    print(f"  CNAPP MQ seed vendors:    {len(seed_data['vendors'])}")

    print(f"\nScoring {len(seed_data['vendors'])} vendors x 27 sub-pillars...")
    processed = []
    score_stats = {sp: [] for sp in SCORING_FUNCTIONS}

    for sv in seed_data["vendors"]:
        r = process_vendor(sv)
        processed.append(r)
        for sp_id, sc in r["mq_gap_sub_pillar_scores"].items():
            score_stats[sp_id].append(sc)

    processed.sort(key=lambda x: x["vendor"])

    output = {
        "schema_ref": "CNAPP_MQ_Gap_Schema_App.json",
        "schema_version": "1.0",
        "source_schema": "CNAPP",
        "assessment_type": "mq_gap_researched",
        "description": "CNAPP MQ Gap criteria scores derived from CNAPP capability data + vendor metadata using rule-based heuristics. All 27 sub-pillars scored for all 24 vendors.",
        "derivation_method": "Heuristic scoring using CNAPP pillar/sub-pillar scores, vendor metadata, cnapp_vendor_type, cloud_coverage, deployment_model, and text mining of descriptions/differentiators.",
        "source_files": [
            "CNAPP Vendor 1-2 Researched.json",
            "CNAPP MQ Vendor 1-0 Seed.json",
        ],
        "vendor_count": len(processed),
        "gap_pillars": list(PILLAR_SUB_MAP.keys()),
        "gap_sub_pillars": list(SCORING_FUNCTIONS.keys()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script": "_research_cnapp_mq.py",
        "vendors": processed,
    }

    out = ROOT / "CNAPP MQ Vendor 1-1 Researched.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {out.name}  ({len(processed)} vendors, 27 sub-pillars)")

    print("\nSub-pillar score ranges (min / mean / max):")
    for sp in sorted(score_stats):
        s = score_stats[sp]
        print(f"  {sp}:  {min(s):.1f} / {sum(s)/len(s):.2f} / {max(s):.1f}")


if __name__ == "__main__":
    main()
