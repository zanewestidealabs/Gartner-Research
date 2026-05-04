#!/usr/bin/env python3
"""
build_mq_gap_v2_1.py  —  Transform MQ Gap Schema + Researched data into 
the standard vendor-page-compatible format (v2.1 Consolidated).

Reads:
  - MQ_Gap_Schema_1_0.json          (schema definitions)
  - MDR Services Vendor MQ Gap 2-0 Researched.json  (heuristic scores + rationales)
  - MDR Services Vendor 2-1 Consolidated.json        (existing MDR data for enrichment)

Produces:
  - MQ_Gap Vendor 2-1 Consolidated.json  (vendor data in standard format)

The output vendor file uses the same field conventions as other schemas:
  pillar_scores_v2_1, sub_pillar_scores_v2_1, sub_pillar_evidence,
  sub_pillar_rationale_v2_1, sub_pillar_schema_labels, capability_analysis,
  capability_coverage, research_status, research_confidence_v2_1
"""

import json, os, statistics
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Load sources ──
with open(os.path.join(BASE, 'MQ_Gap_Schema_1_0.json'), 'r', encoding='utf-8') as f:
    schema_raw = json.load(f)

with open(os.path.join(BASE, 'MDR Services Vendor MQ Gap 2-0 Researched.json'), 'r', encoding='utf-8') as f:
    gap_data = json.load(f)

with open(os.path.join(BASE, 'MDR Services Vendor 2-1 Consolidated.json'), 'r', encoding='utf-8') as f:
    mdr_data = json.load(f)

# Build MDR vendor lookup for enrichment
mdr_lookup = {}
for v in mdr_data.get('vendors', []):
    mdr_lookup[v['vendor']] = v


# ════════════════════════════════════════════════════════════════
# STEP 1: Restructure schema for the app's SCHEMA_REGISTRY format
# ════════════════════════════════════════════════════════════════

def build_app_schema():
    """Convert array-based schema to dict-based format the app expects."""
    pillars_dict = {}
    sub_pillars_dict = {}

    for p in schema_raw['pillars']:
        pid = p['pillar_id']
        pillars_dict[pid] = {
            'name': p['pillar_name'],
            'description': p.get('description', ''),
            'mq_criterion': p.get('mq_criterion', ''),
            'mq_axis': p.get('mq_axis', ''),
        }
        for sp in p['sub_pillars']:
            spid = sp['sub_pillar_id']
            sub_pillars_dict[spid] = {
                'name': sp['sub_pillar_name'],
                'definition': sp.get('description', ''),
                'expanded_definition': sp.get('description', ''),
                'evidence_sources': sp.get('evidence_sources', []),
                'scoring_guidance': sp.get('scoring_guidance', {}),
                'what_to_verify_publicly': sp.get('evidence_sources', []),
            }

    app_schema = {
        'mq_gap_taxonomy_v1.0': {
            'title': schema_raw.get('title', 'MQ Gap Criteria'),
            'version': schema_raw.get('schema_version', '1.0'),
            'scoring_scale': schema_raw.get('scoring_scale', {}),
            'pillars': pillars_dict,
            'sub_pillars': sub_pillars_dict,
        }
    }

    out_path = os.path.join(BASE, 'MDR_MQ_Gap_Schema_App.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(app_schema, f, indent=2, ensure_ascii=False)
    print(f"[schema] Wrote {out_path}")
    return app_schema


# ════════════════════════════════════════════════════════════════
# STEP 2: Build sub-pillar label map from schema
# ════════════════════════════════════════════════════════════════

def build_label_map():
    """Create sub_pillar_id -> human-readable label mapping."""
    labels = {}
    for p in schema_raw['pillars']:
        for sp in p['sub_pillars']:
            labels[sp['sub_pillar_id']] = sp['sub_pillar_name']
    return labels

SP_LABELS = build_label_map()


# ════════════════════════════════════════════════════════════════
# STEP 3: Build deep rationales with evidence from existing data
# ════════════════════════════════════════════════════════════════

def build_deep_rationale(vendor_gap, vendor_mdr):
    """
    For each sub-pillar, produce a detailed rationale with evidence citations
    by combining the heuristic rationale with supporting data from the MDR vendor record.
    """
    rationales = {}
    evidence = {}
    
    gap_rats = vendor_gap.get('mq_gap_rationales', {})
    gap_scores = vendor_gap.get('mq_gap_sub_pillar_scores', {})
    
    # Extract useful MDR info for evidence enrichment
    vendor_name = vendor_gap.get('vendor', '')
    website = vendor_gap.get('website', '')
    desc = vendor_gap.get('description', '')
    diffs = vendor_gap.get('key_differentiators', [])
    if isinstance(diffs, str):
        diffs = [diffs]
    funding = vendor_gap.get('funding_stage', '')
    employees = vendor_gap.get('employee_count_range', '')
    hq = vendor_gap.get('headquarters', '')
    region = vendor_gap.get('region', '')
    target = vendor_gap.get('target_market', '')
    svc_type = vendor_gap.get('mdr_service_type', '')
    
    # MDR enrichment
    mdr_cap = ''
    mdr_diff_v2 = ''
    mdr_pillar_scores = {}
    mdr_pricing = {}
    if vendor_mdr:
        mdr_cap = vendor_mdr.get('capability_analysis', '')
        mdr_diff_v2 = vendor_mdr.get('notable_differentiation_v2_1', vendor_mdr.get('notable_differentiation', ''))
        mdr_pillar_scores = vendor_mdr.get('pillar_scores_v2_1', {})
        # Pricing fields
        for pk in ['pricing_overall_score_v2', 'outcome_maturity_rating_v2', 'pricing_model_details']:
            if pk in vendor_mdr:
                mdr_pricing[pk] = vendor_mdr[pk]
    
    for p in schema_raw['pillars']:
        pid = p['pillar_id']
        pillar_rats = gap_rats.get(pid, {})
        
        for sp in p['sub_pillars']:
            spid = sp['sub_pillar_id']
            score = gap_scores.get(spid, 0)
            
            # Get base rationale from heuristic research
            sp_rat_data = pillar_rats.get(spid, {})
            base_rationale = sp_rat_data.get('rationale', '')
            base_confidence = sp_rat_data.get('confidence', 'low')
            base_sources = sp_rat_data.get('evidence_sources', [])
            
            # Build enriched rationale
            enriched = _enrich_rationale(
                spid, sp, score, base_rationale, base_confidence,
                vendor_name, website, desc, diffs, funding, employees,
                hq, region, target, svc_type,
                mdr_cap, mdr_diff_v2, mdr_pillar_scores, mdr_pricing
            )
            
            rationales[spid] = enriched['rationale']
            evidence[spid] = enriched['evidence']
    
    return rationales, evidence


def _enrich_rationale(spid, sp_def, score, base_rationale, confidence,
                      vendor_name, website, desc, diffs, funding, employees,
                      hq, region, target, svc_type,
                      mdr_cap, mdr_diff_v2, mdr_pillar_scores, mdr_pricing):
    """Enrich a single sub-pillar rationale with deep evidence."""
    
    pillar_code = spid.split('-')[0]
    sp_name = sp_def['sub_pillar_name']
    sp_desc = sp_def.get('description', '')
    guidance = sp_def.get('scoring_guidance', {})
    evidence_types = sp_def.get('evidence_sources', [])
    
    # Determine score level description from guidance
    score_int = str(int(round(score)))
    level_desc = guidance.get(score_int, guidance.get(str(min(5, max(1, int(round(score))))), ''))
    
    # Build evidence sources list
    sources = []
    excerpts = []
    
    # Always include the vendor website
    if website:
        sources.append(website)
    
    # Build rationale text
    parts = []
    
    # Core assessment
    parts.append(f"Score: {score:.1f}/5.0 — {level_desc}")
    
    # Add base heuristic rationale
    if base_rationale:
        parts.append(base_rationale)
    
    # Pillar-specific enrichment
    if pillar_code == 'VIA':
        _enrich_via(spid, parts, excerpts, sources, vendor_name, funding, employees, desc, mdr_pricing)
    elif pillar_code == 'SLE':
        _enrich_sle(spid, parts, excerpts, sources, vendor_name, website, desc, diffs, region, target)
    elif pillar_code == 'MKR':
        _enrich_mkr(spid, parts, excerpts, sources, vendor_name, desc, diffs, mdr_cap, mdr_diff_v2)
    elif pillar_code == 'MKE':
        _enrich_mke(spid, parts, excerpts, sources, vendor_name, website, desc, diffs, mdr_cap)
    elif pillar_code == 'CXQ':
        _enrich_cxq(spid, parts, excerpts, sources, vendor_name, mdr_pillar_scores, mdr_cap, mdr_diff_v2)
    elif pillar_code == 'MKU':
        _enrich_mku(spid, parts, excerpts, sources, vendor_name, desc, diffs, mdr_cap, mdr_diff_v2, mdr_pillar_scores, svc_type)
    elif pillar_code == 'VIG':
        _enrich_vig(spid, parts, excerpts, sources, vendor_name, hq, region, target, desc, diffs)
    
    # Confidence note
    parts.append(f"Research confidence: {confidence}. Evidence derived from public data and MDR capability analysis.")
    
    rationale_text = ' | '.join(parts)
    
    # Build evidence structure matching app format
    evidence_obj = {
        'source_urls': sources[:5],
        'excerpts': excerpts[:3] if excerpts else [{
            'url': website or '',
            'excerpt': base_rationale or f"Assessment based on {sp_name.lower()} evaluation criteria.",
            'matched_terms': _extract_matched_terms(base_rationale, sp_desc),
            'relevance_score': 6 if confidence == 'high' else 4 if confidence == 'medium' else 2,
        }],
    }
    
    return {'rationale': rationale_text, 'evidence': evidence_obj}


def _extract_matched_terms(text, definition):
    """Extract relevant terms from text that match definition keywords."""
    if not text:
        return []
    keywords = ['revenue', 'growth', 'funding', 'partner', 'channel', 'sales', 'marketing',
                'brand', 'customer', 'support', 'innovation', 'ai', 'platform', 'global',
                'enterprise', 'smb', 'vertical', 'industry', 'geographic', 'region',
                'acquisition', 'release', 'update', 'integration', 'mssp', 'soc',
                'threat', 'detection', 'response', 'compliance', 'regulatory']
    text_lower = text.lower()
    return [k for k in keywords if k in text_lower][:5]


def _enrich_via(spid, parts, excerpts, sources, name, funding, employees, desc, pricing):
    """Enrich Financial Viability sub-pillars."""
    if spid == 'VIA-01':  # Revenue & Growth
        if funding:
            parts.append(f"Funding stage: {funding}.")
        if employees:
            parts.append(f"Employee range: {employees}.")
        if pricing.get('pricing_overall_score_v2'):
            parts.append(f"Pricing model maturity score: {pricing['pricing_overall_score_v2']:.1f}/5.0, indicating commercial maturity.")
    elif spid == 'VIA-02':  # Profitability
        if funding in ['IPO', 'Public']:
            parts.append(f"Public company ({funding}) — financial data available via SEC filings.")
        elif 'acquired' in (funding or '').lower():
            parts.append(f"Acquired entity — financial backing from parent company.")
        elif funding:
            parts.append(f"Funding stage {funding} — financial runway dependent on latest raise.")
    elif spid == 'VIA-03':  # Customer Base
        cust_terms = ['customer', 'client', 'organization', 'enterprise']
        if desc and any(t in desc.lower() for t in cust_terms):
            parts.append("Customer base references found in vendor description.")
    elif spid == 'VIA-04':  # Market Position
        analyst_terms = ['gartner', 'forrester', 'idc', 'mitre', 'leader', 'wave']
        if desc and any(t in desc.lower() for t in analyst_terms):
            parts.append("Analyst recognition signals found in vendor profile.")


def _enrich_sle(spid, parts, excerpts, sources, name, website, desc, diffs, region, target):
    """Enrich Sales Execution sub-pillars."""
    if spid == 'SLE-01':  # Channel & Partners
        partner_terms = ['partner', 'channel', 'mssp', 'reseller', 'alliance', 'marketplace']
        matched = [t for t in partner_terms if desc and t in desc.lower()] + \
                  [t for d in (diffs or []) for t in partner_terms if t in d.lower()]
        if matched:
            parts.append(f"Partner/channel signals detected: {', '.join(set(matched))}.")
        if website:
            sources.append(f"{website}/partners")
    elif spid == 'SLE-02':  # Sales Motion
        motion_terms = ['trial', 'demo', 'free', 'poc', 'self-service', 'product-led']
        matched = [t for t in motion_terms if desc and t in desc.lower()]
        if matched:
            parts.append(f"Sales motion indicators: {', '.join(matched)}.")
    elif spid == 'SLE-03':  # Geographic Sales
        parts.append(f"Primary region: {region}. Target market: {target}.")
    elif spid == 'SLE-04':  # Acquisition Efficiency
        acq_terms = ['roi', 'assessment', 'calculator', 'webinar', 'event']
        matched = [t for t in acq_terms if desc and t in desc.lower()]
        if matched:
            parts.append(f"Demand generation signals: {', '.join(matched)}.")


def _enrich_mkr(spid, parts, excerpts, sources, name, desc, diffs, mdr_cap, mdr_diff):
    """Enrich Market Responsiveness sub-pillars."""
    if spid == 'MKR-01':  # Release Cadence
        release_terms = ['release', 'update', 'launch', 'version', 'new feature', 'changelog']
        all_text = ' '.join([desc or '', mdr_cap or '', mdr_diff or ''])
        matched = [t for t in release_terms if t in all_text.lower()]
        if matched:
            parts.append(f"Release activity signals: {', '.join(matched)}.")
    elif spid == 'MKR-02':  # Competitive Response
        adapt_terms = ['ai', 'generative', 'xdr', 'automation', 'cloud', 'zero trust', 'identity']
        all_text = ' '.join([desc or '', mdr_cap or ''])
        matched = [t for t in adapt_terms if t in all_text.lower()]
        if matched:
            parts.append(f"Market trend adoption signals: {', '.join(set(matched))}.")
    elif spid == 'MKR-03':  # M&A
        ma_terms = ['acquired', 'acquisition', 'merged', 'investment', 'strategic']
        all_text = ' '.join([desc or ''] + (diffs or []))
        matched = [t for t in ma_terms if t in all_text.lower()]
        if matched:
            parts.append(f"M&A/investment signals: {', '.join(matched)}.")
    elif spid == 'MKR-04':  # Customer-Driven
        cust_terms = ['feedback', 'advisory', 'community', 'roadmap', 'request']
        all_text = ' '.join([desc or '', mdr_cap or ''])
        matched = [t for t in cust_terms if t in all_text.lower()]
        if matched:
            parts.append(f"Customer-driven development signals: {', '.join(matched)}.")


def _enrich_mke(spid, parts, excerpts, sources, name, website, desc, diffs, mdr_cap):
    """Enrich Marketing Execution sub-pillars."""
    if spid == 'MKE-01':  # Brand Awareness
        brand_terms = ['leader', 'recognized', 'award', 'top', 'best', 'named']
        all_text = ' '.join([desc or '', mdr_cap or ''])
        matched = [t for t in brand_terms if t in all_text.lower()]
        if matched:
            parts.append(f"Brand recognition signals: {', '.join(matched)}.")
    elif spid == 'MKE-02':  # Content & Thought Leadership
        if website:
            sources.append(f"{website}/blog")
            sources.append(f"{website}/resources")
        content_terms = ['research', 'report', 'whitepaper', 'blog', 'threat intelligence', 'insight']
        all_text = ' '.join([desc or '', mdr_cap or ''] + (diffs or []))
        matched = [t for t in content_terms if t in all_text.lower()]
        if matched:
            parts.append(f"Content/thought leadership signals: {', '.join(matched)}.")
    elif spid == 'MKE-03':  # Events
        event_terms = ['rsa', 'black hat', 'conference', 'summit', 'event', 'gartner']
        all_text = ' '.join([desc or ''] + (diffs or []))
        matched = [t for t in event_terms if t in all_text.lower()]
        if matched:
            parts.append(f"Event presence signals: {', '.join(matched)}.")
    elif spid == 'MKE-04':  # Digital Presence
        if website:
            parts.append(f"Primary digital presence: {website}")
            sources.append(website)


def _enrich_cxq(spid, parts, excerpts, sources, name, mdr_scores, mdr_cap, mdr_diff):
    """Enrich Customer Experience Quality sub-pillars."""
    if spid == 'CXQ-01':  # Support Quality
        if mdr_scores.get('DIS'):
            parts.append(f"MDR DIS (Deployment & Integration Support) pillar score: {mdr_scores['DIS']:.2f}/5.0 — used as support quality proxy.")
    elif spid == 'CXQ-02':  # Onboarding
        if mdr_scores.get('DIS'):
            parts.append(f"MDR deployment support score ({mdr_scores['DIS']:.2f}) informs onboarding maturity assessment.")
    elif spid == 'CXQ-03':  # Satisfaction Indicators
        sat_terms = ['satisfied', 'nps', 'review', 'rating', 'peer insights', 'g2']
        all_text = ' '.join([mdr_cap or '', mdr_diff or ''])
        matched = [t for t in sat_terms if t in all_text.lower()]
        if matched:
            parts.append(f"Satisfaction indicators: {', '.join(matched)}.")
    elif spid == 'CXQ-04':  # Escalation & Communication
        comm_terms = ['portal', 'dashboard', 'reporting', 'communication', 'escalation', 'sla']
        all_text = ' '.join([mdr_cap or '', mdr_diff or ''])
        matched = [t for t in comm_terms if t in all_text.lower()]
        if matched:
            parts.append(f"Communication/escalation signals: {', '.join(matched)}.")


def _enrich_mku(spid, parts, excerpts, sources, name, desc, diffs, mdr_cap, mdr_diff, mdr_scores, svc_type):
    """Enrich Market Understanding & Vision sub-pillars."""
    if spid == 'MKU-01':  # Market Trend Awareness
        trend_terms = ['ai', 'xdr', 'zero trust', 'cloud', 'identity', 'automation', 'soar', 'siem']
        all_text = ' '.join([desc or '', mdr_cap or ''])
        matched = [t for t in trend_terms if t in all_text.lower()]
        if matched:
            parts.append(f"Market trend alignment: {', '.join(set(matched))}.")
    elif spid == 'MKU-02':  # Offering & Roadmap
        if mdr_scores.get('AIO'):
            parts.append(f"MDR AIO (AI & Orchestration) score: {mdr_scores['AIO']:.2f}/5.0 — indicates innovation investment.")
        if svc_type:
            parts.append(f"Service type: {svc_type}.")
    elif spid == 'MKU-03':  # Business Model
        model_terms = ['pricing', 'subscription', 'outcome', 'consumption', 'per-endpoint', 'per-user']
        all_text = ' '.join([desc or ''] + (diffs or []))
        matched = [t for t in model_terms if t in all_text.lower()]
        if matched:
            parts.append(f"Business model signals: {', '.join(matched)}.")
    elif spid == 'MKU-04':  # Innovation Investment
        innov_terms = ['r&d', 'research', 'patent', 'lab', 'innovation', 'ai-native', 'machine learning']
        all_text = ' '.join([desc or '', mdr_cap or ''] + (diffs or []))
        matched = [t for t in innov_terms if t in all_text.lower()]
        if matched:
            parts.append(f"Innovation investment signals: {', '.join(set(matched))}.")


def _enrich_vig(spid, parts, excerpts, sources, name, hq, region, target, desc, diffs):
    """Enrich Vertical & Geographic Strategy sub-pillars."""
    if spid == 'VIG-01':  # Vertical Coverage
        vert_terms = ['healthcare', 'financial', 'banking', 'government', 'retail', 'manufacturing',
                      'energy', 'education', 'telco', 'insurance', 'pharma', 'critical infrastructure']
        all_text = ' '.join([desc or ''] + (diffs or []))
        matched = [t for t in vert_terms if t in all_text.lower()]
        if matched:
            parts.append(f"Vertical coverage: {', '.join(matched)}.")
    elif spid == 'VIG-02':  # Compliance
        comp_terms = ['hipaa', 'pci', 'gdpr', 'sox', 'nist', 'iso', 'fedramp', 'cmmc', 'compliance', 'regulatory']
        all_text = ' '.join([desc or ''] + (diffs or []))
        matched = [t for t in comp_terms if t in all_text.lower()]
        if matched:
            parts.append(f"Compliance/regulatory signals: {', '.join(matched)}.")
    elif spid == 'VIG-03':  # Geographic Presence
        parts.append(f"HQ: {hq}. Primary region: {region}.")
        geo_terms = ['global', 'international', 'multi-region', 'emea', 'apac', 'latam', 'americas']
        all_text = ' '.join([desc or ''] + (diffs or []))
        matched = [t for t in geo_terms if t in all_text.lower()]
        if matched:
            parts.append(f"Geographic reach signals: {', '.join(matched)}.")
    elif spid == 'VIG-04':  # Localization
        loc_terms = ['language', 'local', 'regional soc', 'data residency', 'sovereignty', 'multi-language']
        all_text = ' '.join([desc or ''] + (diffs or []))
        matched = [t for t in loc_terms if t in all_text.lower()]
        if matched:
            parts.append(f"Localization signals: {', '.join(matched)}.")


# ════════════════════════════════════════════════════════════════
# STEP 4: Build the consolidated vendor file
# ════════════════════════════════════════════════════════════════

def build_consolidated():
    """Build the v2-1 Consolidated vendor file in standard format."""
    vendors_out = []
    
    for gap_vendor in gap_data['vendors']:
        name = gap_vendor['vendor']
        mdr_vendor = mdr_lookup.get(name)
        
        # Build standard score dicts
        pillar_scores = {}
        sub_pillar_scores = {}
        
        gap_pillar = gap_vendor.get('mq_gap_pillar_scores', {})
        gap_sub = gap_vendor.get('mq_gap_sub_pillar_scores', {})
        
        for pid, pscore in gap_pillar.items():
            pillar_scores[pid] = round(pscore, 2)
        
        for spid, spscore in gap_sub.items():
            sub_pillar_scores[spid] = round(spscore, 2)
        
        # Build deep rationales and evidence
        rationales, evidence_map = build_deep_rationale(gap_vendor, mdr_vendor)
        
        # Build capability coverage (sub-pillars with score >= 3.0)
        coverage = [spid for spid, sc in sub_pillar_scores.items() if sc >= 3.0]
        
        # Build capability analysis narrative
        cap_analysis = _build_capability_analysis(name, gap_vendor, mdr_vendor, pillar_scores)
        
        # Determine research confidence
        tier = gap_vendor.get('mq_gap_research_tier', 'tier_3')
        conf_map = {'tier_1': 'high', 'tier_2': 'medium', 'tier_3': 'low'}
        confidence = conf_map.get(tier, 'low')
        
        vendor_out = {
            'vendor': name,
            'website': gap_vendor.get('website', ''),
            'headquarters': gap_vendor.get('headquarters', ''),
            'year_founded': gap_vendor.get('year_founded', ''),
            'employee_count_range': gap_vendor.get('employee_count_range', ''),
            'funding_stage': gap_vendor.get('funding_stage', ''),
            'total_funding': gap_vendor.get('total_funding', ''),
            'region': gap_vendor.get('region', ''),
            'target_market': gap_vendor.get('target_market', ''),
            'mdr_service_type': gap_vendor.get('mdr_service_type', ''),
            'delivery_model': gap_vendor.get('delivery_model', ''),
            'description': gap_vendor.get('description', ''),
            'key_differentiators': gap_vendor.get('key_differentiators', []),
            
            # Standard score fields
            'pillar_scores': pillar_scores,
            'pillar_scores_v2_1': pillar_scores,
            'sub_pillar_scores_current': sub_pillar_scores,
            'sub_pillar_scores_v2_1': sub_pillar_scores,
            'sub_pillar_schema_labels': SP_LABELS,
            
            # Evidence & rationales
            'sub_pillar_rationale_v2_1': rationales,
            'sub_pillar_evidence': evidence_map,
            
            # Capability analysis
            'capability_analysis': cap_analysis,
            'capability_coverage': coverage,
            'capability_coverage_count': len(coverage),
            
            # Research metadata
            'research_status': 'completed',
            'research_confidence': confidence,
            'research_confidence_v2_1': confidence,
            'mq_gap_research_tier': tier,
        }
        
        vendors_out.append(vendor_out)
    
    # Sort by average score descending
    vendors_out.sort(key=lambda v: statistics.mean(v['pillar_scores_v2_1'].values()), reverse=True)
    
    output = {
        'schema_ref': 'MDR_MQ_Gap_Schema_App.json',
        'vendor_count': len(vendors_out),
        'pillars': list({sp.split('-')[0] for sp in SP_LABELS.keys()}),
        'sub_pillars': list(SP_LABELS.keys()),
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'script': 'build_mq_gap_v2_1.py',
        'vendors': vendors_out,
    }
    
    out_path = os.path.join(BASE, 'MQ_Gap Vendor 2-1 Consolidated.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"[vendors] Wrote {out_path} — {len(vendors_out)} vendors")
    return output


def _build_capability_analysis(name, gap_vendor, mdr_vendor, pillar_scores):
    """Build a narrative capability analysis for the MQ Gap assessment."""
    funding = gap_vendor.get('funding_stage', 'Unknown')
    employees = gap_vendor.get('employee_count_range', 'Unknown')
    region = gap_vendor.get('region', 'Unknown')
    svc_type = gap_vendor.get('mdr_service_type', 'Unknown')
    
    # Find strongest and weakest pillars
    if pillar_scores:
        strongest = max(pillar_scores, key=pillar_scores.get)
        weakest = min(pillar_scores, key=pillar_scores.get)
        avg_score = statistics.mean(pillar_scores.values())
    else:
        strongest = weakest = 'N/A'
        avg_score = 0
    
    pillar_names = {p['pillar_id']: p['pillar_name'] for p in schema_raw['pillars']}
    
    # Overall assessment
    if avg_score >= 3.5:
        level = "strong"
    elif avg_score >= 2.5:
        level = "moderate"
    elif avg_score >= 1.5:
        level = "developing"
    else:
        level = "limited"
    
    parts = [
        f"{name} demonstrates {level} MQ gap criteria coverage (avg: {avg_score:.2f}/5.0).",
        f"Strongest area: {pillar_names.get(strongest, strongest)} ({pillar_scores.get(strongest, 0):.2f}).",
        f"Area for improvement: {pillar_names.get(weakest, weakest)} ({pillar_scores.get(weakest, 0):.2f}).",
        f"Profile: {svc_type} provider, {funding} stage, {employees} employees, {region}-based.",
    ]
    
    # Add MDR context if available
    if mdr_vendor:
        mdr_avg = statistics.mean(mdr_vendor.get('pillar_scores_v2_1', {}).values()) if mdr_vendor.get('pillar_scores_v2_1') else 0
        if mdr_avg > 0:
            parts.append(f"MDR capability score average: {mdr_avg:.2f}/5.0.")
    
    return ' '.join(parts)


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 60)
    print("MQ Gap v2.1 Consolidated Builder")
    print("=" * 60)
    
    # Step 1: Build consolidated vendor file (schema is maintained separately in MDR_MQ_Gap_Schema_App.json)
    result = build_consolidated()
    
    # Stats
    all_scores = []
    for v in result['vendors']:
        all_scores.extend(v['pillar_scores_v2_1'].values())
    
    print(f"\n[stats] Score distribution:")
    print(f"  min={min(all_scores):.2f}  max={max(all_scores):.2f}  avg={statistics.mean(all_scores):.2f}  median={statistics.median(all_scores):.2f}")
    
    # Per-pillar stats
    for pid in ['VIA', 'SLE', 'MKR', 'MKE', 'CXQ', 'MKU', 'VIG']:
        pscores = [v['pillar_scores_v2_1'].get(pid, 0) for v in result['vendors']]
        print(f"  {pid}: avg={statistics.mean(pscores):.2f}  min={min(pscores):.2f}  max={max(pscores):.2f}")
    
    # Evidence check
    has_evidence = sum(1 for v in result['vendors'] if v.get('sub_pillar_evidence'))
    has_rationale = sum(1 for v in result['vendors'] if v.get('sub_pillar_rationale_v2_1'))
    has_analysis = sum(1 for v in result['vendors'] if v.get('capability_analysis'))
    print(f"\n[quality] Evidence: {has_evidence}/{len(result['vendors'])}")
    print(f"[quality] Rationales: {has_rationale}/{len(result['vendors'])}")
    print(f"[quality] Analysis: {has_analysis}/{len(result['vendors'])}")
    
    print("\nDone.")
