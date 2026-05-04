"""
Enrich PMR vendor entries with real evidence from source schemas.

This script:
1. Loads all 5 source schema vendor files (MDR, TRiSM, PreCyber, OffSec, SbD-AI)
2. For each PMR vendor, finds their source schema entries
3. Extracts existing evidence (excerpts, source URLs, rationales) from those
4. Maps evidence to PMR sub-pillars using the cross-schema pillar mapping
5. Rewrites rationales to reference specific evidence findings
6. Populates the excerpts array with real source text + relevance scores
7. Writes enriched output to 'Product Market Readiness Vendor 1-1 Enriched.json'
"""

import json
import os
import re
from collections import defaultdict
from copy import deepcopy

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Cross-schema pillar mapping (same as _score_pmr_vendors.py) ──
SOURCE_SCHEMAS = {
    'ai_trism': {
        'file': 'AI TRiSM Vendor 2-1 Consolidated.json',
        'pillar_map': {
            'GOV': [('PPD', 0.6), ('TDT', 0.4)],
            'RUN': [('PCS', 0.5), ('TDT', 0.5)],
            'INF': [('TDT', 0.4), ('PCM', 0.6)],
        }
    },
    'mdr_services': {
        'file': 'MDR Services Vendor 2-0 Researched.json',
        'pillar_map': {
            'TDR': [('PPD', 0.5), ('PCS', 0.5)],
            'PTI': [('TDT', 0.5), ('CTL', 0.5)],
            'ADA': [('PPD', 0.4), ('PCS', 0.6)],
            'DIS': [('PCS', 0.4), ('CTL', 0.6)],
            'IRA': [('PCS', 0.6), ('TDT', 0.4)],
            'AIO': [('TDT', 0.5), ('PPD', 0.5)],
            'SOG': [('PCM', 0.5), ('CTL', 0.5)],
        }
    },
    'preemptive_cyber': {
        'file': 'Preemptive Cybersecurity Vendor 2-1 Consolidated.json',
        'pillar_map': {
            'EXM': [('PPD', 0.5), ('PCS', 0.5)],
            'ADR': [('TDT', 0.4), ('PCS', 0.6)],
            'PPM': [('PCM', 0.5), ('CTL', 0.5)],
        }
    },
    'offensive_security': {
        'file': 'Offensive Security Vendor 2-0 Researched.json',
        'pillar_map': {
            'ASM': [('PPD', 0.5), ('TDT', 0.5)],
            'VUL': [('PCS', 0.5), ('TDT', 0.5)],
            'OFT': [('PPD', 0.5), ('CTL', 0.5)],
        }
    },
}

# Which PMR sub-pillars map to what kind of evidence
PMR_SUB_PILLAR_EVIDENCE_KEYS = {
    # PPD: Product Positioning & Differentiation - needs capability claims, differentiation, messaging
    'PPD-01': {'keywords': ['capability', 'feature', 'platform', 'solution', 'detect', 'protect', 'automate', 'AI', 'machine learning'], 'evidence_type': 'capability_claims'},
    'PPD-02': {'keywords': ['unique', 'differentiat', 'only', 'first', 'leader', 'patent', 'proprietary', 'competitive'], 'evidence_type': 'differentiation'},
    'PPD-03': {'keywords': ['enterprise', 'mid-market', 'SMB', 'CISO', 'SOC', 'analyst', 'team', 'use case', 'persona'], 'evidence_type': 'targeting'},
    'PPD-04': {'keywords': ['leader', 'gartner', 'forrester', 'market', 'category', 'pioneer', 'visionary', 'magic quadrant'], 'evidence_type': 'market_position'},
    'PPD-05': {'keywords': ['consistent', 'unified', 'platform', 'brand', 'messaging', 'coherent'], 'evidence_type': 'messaging_consistency'},
    # PCS: Proof Points & Case Studies - needs case studies, validations, metrics
    'PCS-01': {'keywords': ['case study', 'customer', 'success', 'deployment', 'implementation', 'story'], 'evidence_type': 'case_studies'},
    'PCS-02': {'keywords': ['gartner', 'forrester', 'analyst', 'recognition', 'award', 'certification', 'ISO', 'SOC 2'], 'evidence_type': 'third_party_validation'},
    'PCS-03': {'keywords': ['deploy', 'scale', 'endpoint', 'customer', 'metric', 'million', 'billion', 'enterprise'], 'evidence_type': 'deployment_metrics'},
    'PCS-04': {'keywords': ['ROI', 'return', 'cost', 'saving', 'outcome', 'business', 'value', 'reduction', 'efficiency'], 'evidence_type': 'roi_evidence'},
    'PCS-05': {'keywords': ['reference', 'customer', 'industry', 'vertical', 'sector', 'testimonial'], 'evidence_type': 'reference_breadth'},
    # TDT: Technical Depth & Transparency - needs architecture, API, methodology
    'TDT-01': {'keywords': ['architecture', 'design', 'framework', 'infrastructure', 'cloud', 'agent', 'platform'], 'evidence_type': 'architecture'},
    'TDT-02': {'keywords': ['API', 'integration', 'SIEM', 'SOAR', 'ecosystem', 'connector', 'plugin', 'marketplace'], 'evidence_type': 'integrations'},
    'TDT-03': {'keywords': ['detect', 'method', 'technique', 'MITRE', 'rule', 'signature', 'behavioral', 'heuristic'], 'evidence_type': 'detection_methodology'},
    'TDT-04': {'keywords': ['data', 'privacy', 'GDPR', 'compliance', 'retention', 'encryption', 'handling', 'sovereign'], 'evidence_type': 'data_privacy'},
    'TDT-05': {'keywords': ['documentation', 'guide', 'tutorial', 'training', 'certification', 'enablement', 'onboarding'], 'evidence_type': 'technical_docs'},
    # PCM: Pricing & Commercial Model - needs pricing, packaging, TCO
    'PCM-01': {'keywords': ['pricing', 'price', 'cost', 'subscription', 'per endpoint', 'per user', 'transparent'], 'evidence_type': 'pricing_model'},
    'PCM-02': {'keywords': ['tier', 'package', 'plan', 'bundle', 'basic', 'professional', 'enterprise', 'premium'], 'evidence_type': 'packaging'},
    'PCM-03': {'keywords': ['TCO', 'total cost', 'ownership', 'hidden', 'fee', 'license', 'implementation'], 'evidence_type': 'tco'},
    'PCM-04': {'keywords': ['trial', 'demo', 'free', 'evaluation', 'POC', 'proof of concept', 'test'], 'evidence_type': 'trial_access'},
    'PCM-05': {'keywords': ['contract', 'term', 'flexible', 'month', 'annual', 'commitment', 'SLA'], 'evidence_type': 'commercial_terms'},
    # CTL: Content & Thought Leadership - needs research, conference, blog, open source
    'CTL-01': {'keywords': ['research', 'report', 'study', 'data', 'finding', 'survey', 'whitepaper', 'publication'], 'evidence_type': 'research'},
    'CTL-02': {'keywords': ['conference', 'speak', 'RSA', 'Black Hat', 'summit', 'event', 'keynote', 'presentation'], 'evidence_type': 'conference'},
    'CTL-03': {'keywords': ['blog', 'article', 'educational', 'content', 'guide', 'how-to', 'insight'], 'evidence_type': 'blog_content'},
    'CTL-04': {'keywords': ['open source', 'github', 'community', 'contribution', 'project', 'repository', 'tool'], 'evidence_type': 'open_source'},
    'CTL-05': {'keywords': ['education', 'market', 'category', 'define', 'thought leader', 'framework', 'vision'], 'evidence_type': 'market_education'},
}

SUB_PILLAR_NAMES = {
    'PPD-01': 'Capability Claim Specificity',
    'PPD-02': 'Competitive Differentiation Clarity',
    'PPD-03': 'Target Persona & Use-Case Alignment',
    'PPD-04': 'Market Category Ownership',
    'PPD-05': 'Messaging Consistency & Coherence',
    'PCS-01': 'Customer Case Study Depth',
    'PCS-02': 'Third-Party Validation & Analyst Recognition',
    'PCS-03': 'Deployment Scale & Metric Transparency',
    'PCS-04': 'ROI & Business Outcome Documentation',
    'PCS-05': 'Customer Reference Breadth',
    'TDT-01': 'Architecture & Design Documentation',
    'TDT-02': 'API & Integration Ecosystem',
    'TDT-03': 'Detection & Methodology Transparency',
    'TDT-04': 'Data Handling & Privacy Transparency',
    'TDT-05': 'Technical Enablement & Documentation Quality',
    'PCM-01': 'Pricing Model Transparency',
    'PCM-02': 'Packaging & Tier Clarity',
    'PCM-03': 'Total Cost of Ownership Articulation',
    'PCM-04': 'Trial & Evaluation Accessibility',
    'PCM-05': 'Commercial Terms & Contract Flexibility',
    'CTL-01': 'Original Research & Data Publication',
    'CTL-02': 'Conference & Speaking Presence',
    'CTL-03': 'Blog & Educational Content Quality',
    'CTL-04': 'Open-Source & Community Contribution',
    'CTL-05': 'Market Education & Category Development',
}


def load_vendors(fname):
    """Load vendor list from a JSON file."""
    path = os.path.join(BASE, fname)
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'vendors' in data:
        return data['vendors']
    if isinstance(data, list):
        return data
    return []


def normalize_vendor_name(name):
    """Normalize vendor names for matching across schemas."""
    n = name.lower().strip()
    # Remove common suffixes
    for suffix in [', inc.', ', inc', ' inc.', ' inc', ', ltd', ', llc', ' llc',
                   ' corporation', ' corp.', ' corp', ' technologies', ' technology',
                   ' security', ' cybersecurity', ' solutions', ' software']:
        if n.endswith(suffix):
            n = n[:-len(suffix)]
    # Known aliases
    aliases = {
        'palo alto networks': 'palo alto networks',
        'check point software': 'check point',
        'check point software technologies': 'check point',
        'fortinet': 'fortinet',
        'crowdstrike': 'crowdstrike',
        'mandiant (google cloud)': 'mandiant',
        'aws (amazon web services)': 'aws',
        'google cloud': 'google',
        'ibm security': 'ibm',
    }
    return aliases.get(n, n)


def compute_relevance(text, keywords):
    """Compute keyword relevance score (0-10) for a text snippet."""
    if not text:
        return 0
    text_lower = text.lower()
    hit_count = sum(1 for kw in keywords if kw.lower() in text_lower)
    # Scale: 0 matches = 0, 1 = 3, 2 = 5, 3 = 7, 4+ = 8-10
    if hit_count == 0:
        return 0
    return min(hit_count * 2.5 + 0.5, 10)


def extract_evidence_for_pmr(vendor_name, source_schemas_data):
    """
    For a given PMR vendor, pull all available evidence from their source schema entries.
    Returns dict keyed by PMR sub-pillar code with evidence items.
    """
    norm_name = normalize_vendor_name(vendor_name)
    evidence_by_pmr_sub = defaultdict(lambda: {
        'source_urls': [],
        'excerpts': [],
        'source_rationales': [],
        'source_scores': [],
        'source_schema_refs': [],
    })

    for schema_key, schema_info in SOURCE_SCHEMAS.items():
        vendor_lookup = source_schemas_data.get(schema_key, {})
        # Find vendor in this schema
        src_vendor = None
        for vname, vrec in vendor_lookup.items():
            if normalize_vendor_name(vname) == norm_name or norm_name in normalize_vendor_name(vname) or normalize_vendor_name(vname) in norm_name:
                src_vendor = vrec
                break

        if not src_vendor:
            continue

        pillar_map = schema_info['pillar_map']
        src_evidence = src_vendor.get('sub_pillar_evidence', {})
        src_rationale = src_vendor.get('sub_pillar_rationale_v2', {})
        src_rationale_21 = src_vendor.get('sub_pillar_rationale_v2_1', {})
        src_rationale_text = src_vendor.get('sub_pillar_rationale_v2_1_text', {})
        src_pillar_scores = {}
        for k in ['pillar_scores_v2_researched', 'pillar_scores_v2_1', 'pillar_scores']:
            if src_vendor.get(k):
                src_pillar_scores = src_vendor[k]
                break

        # For each source pillar that maps to PMR pillars
        for src_pillar, pmr_targets in pillar_map.items():
            src_score = src_pillar_scores.get(src_pillar, 0)
            if not src_score:
                continue

            # Gather all evidence from sub-pillars of this source pillar
            pillar_urls = []
            pillar_excerpts = []
            pillar_rationales = []

            for src_sp_code, ev_data in src_evidence.items():
                if not src_sp_code.startswith(src_pillar):
                    continue
                if isinstance(ev_data, dict):
                    for url in ev_data.get('source_urls', []):
                        if url and url not in pillar_urls:
                            pillar_urls.append(url)
                    for exc in ev_data.get('excerpts', []):
                        if isinstance(exc, dict) and exc.get('excerpt'):
                            pillar_excerpts.append(exc)
                        elif isinstance(exc, str) and exc.strip():
                            pillar_excerpts.append({'excerpt': exc, 'url': '', 'relevance_score': 5})

            # Gather rationales
            for src_sp_code in sorted(src_rationale.keys()):
                if not src_sp_code.startswith(src_pillar):
                    continue
                rat = src_rationale[src_sp_code]
                if isinstance(rat, dict):
                    score_rat = rat.get('score_rationale', '')
                    if score_rat:
                        pillar_rationales.append(score_rat)
                    # Also grab key_evidence
                    for ke in rat.get('key_evidence', []):
                        if ke and isinstance(ke, str):
                            pillar_excerpts.append({'excerpt': ke, 'url': '', 'relevance_score': 6, 'source': f'{schema_key}:{src_sp_code}'})
                    # And criteria_assessment
                    for ca in rat.get('criteria_assessment', []):
                        if isinstance(ca, dict) and ca.get('evidence') and ca.get('status') == 'met':
                            pillar_excerpts.append({
                                'excerpt': ca['evidence'],
                                'url': '',
                                'relevance_score': 7,
                                'source': f'{schema_key}:{src_sp_code}',
                                'criterion': ca.get('criterion', '')
                            })

            # Also check rationale text variant
            for src_sp_code, rat_text in src_rationale_text.items():
                if src_sp_code.startswith(src_pillar) and isinstance(rat_text, str) and len(rat_text) > 20:
                    pillar_rationales.append(rat_text[:500])

            # Distribute evidence to PMR pillar targets
            for pmr_pillar, weight in pmr_targets:
                # Map to all 5 sub-pillars of this PMR pillar
                for i in range(1, 6):
                    pmr_sp = f'{pmr_pillar}-{i:02d}'
                    sp_keywords = PMR_SUB_PILLAR_EVIDENCE_KEYS.get(pmr_sp, {}).get('keywords', [])

                    # Add URLs (deduplicated)
                    for url in pillar_urls:
                        if url not in evidence_by_pmr_sub[pmr_sp]['source_urls']:
                            evidence_by_pmr_sub[pmr_sp]['source_urls'].append(url)

                    # Score and filter excerpts by relevance to this specific sub-pillar
                    for exc in pillar_excerpts:
                        exc_text = exc.get('excerpt', '')
                        relevance = compute_relevance(exc_text, sp_keywords)
                        if relevance >= 2.5:  # Minimum threshold
                            new_exc = {
                                'url': exc.get('url', ''),
                                'excerpt': exc_text[:400],
                                'relevance_score': round(relevance, 1),
                                'source_schema': schema_key,
                                'source_pillar': src_pillar,
                            }
                            if exc.get('matched_terms'):
                                new_exc['matched_terms'] = exc['matched_terms']
                            # Avoid exact duplicates
                            if not any(e['excerpt'] == new_exc['excerpt'] for e in evidence_by_pmr_sub[pmr_sp]['excerpts']):
                                evidence_by_pmr_sub[pmr_sp]['excerpts'].append(new_exc)

                    # Store source references
                    ref = f'{schema_key}:{src_pillar}={src_score}'
                    if ref not in evidence_by_pmr_sub[pmr_sp]['source_schema_refs']:
                        evidence_by_pmr_sub[pmr_sp]['source_schema_refs'].append(ref)

                    # Store relevant rationales
                    for rat in pillar_rationales:
                        rel = compute_relevance(rat, sp_keywords)
                        if rel >= 2.5 and rat not in evidence_by_pmr_sub[pmr_sp]['source_rationales']:
                            evidence_by_pmr_sub[pmr_sp]['source_rationales'].append(rat[:300])

    # Sort excerpts by relevance within each sub-pillar, keep top 5
    for sp_code in evidence_by_pmr_sub:
        evidence_by_pmr_sub[sp_code]['excerpts'].sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        evidence_by_pmr_sub[sp_code]['excerpts'] = evidence_by_pmr_sub[sp_code]['excerpts'][:5]
        evidence_by_pmr_sub[sp_code]['source_urls'] = evidence_by_pmr_sub[sp_code]['source_urls'][:6]
        evidence_by_pmr_sub[sp_code]['source_rationales'] = evidence_by_pmr_sub[sp_code]['source_rationales'][:3]

    return dict(evidence_by_pmr_sub)


def build_enriched_rationale(sp_code, sp_entry, evidence, vendor_name):
    """Build an evidence-grounded rationale for a PMR sub-pillar entry."""
    sp_name = SUB_PILLAR_NAMES.get(sp_code, sp_code)
    gtm = sp_entry.get('gtm_messaging_score', 0)
    proof = sp_entry.get('proof_of_execution_score', 0)
    gap = sp_entry.get('credibility_gap', 0)

    excerpts = evidence.get('excerpts', [])
    refs = evidence.get('source_schema_refs', [])
    urls = evidence.get('source_urls', [])
    src_rationales = evidence.get('source_rationales', [])

    n_excerpts = len(excerpts)
    n_urls = len(urls)
    n_refs = len(refs)

    # Evidence strength descriptor
    if n_excerpts >= 3:
        ev_strength = "strong cross-schema evidence"
    elif n_excerpts >= 1:
        ev_strength = "partial cross-schema evidence"
    elif n_refs >= 1:
        ev_strength = "score-based cross-schema mapping"
    else:
        ev_strength = "limited available evidence"

    # Build GTM rationale
    ref_str = "; ".join(refs[:3]) if refs else "no cross-schema references"

    if gtm >= 4:
        gtm_rat = (f"GTM score {gtm}/5 for {sp_name}. {vendor_name} demonstrates strong public-facing "
                   f"messaging in this area, supported by {ev_strength} ({ref_str}). ")
    elif gtm >= 3:
        gtm_rat = (f"GTM score {gtm}/5 for {sp_name}. {vendor_name} maintains clear capability "
                   f"positioning with {ev_strength} ({ref_str}). ")
    elif gtm >= 2:
        gtm_rat = (f"GTM score {gtm}/5 for {sp_name}. {vendor_name} provides generic category-level "
                   f"messaging with {ev_strength} ({ref_str}). ")
    elif gtm >= 1:
        gtm_rat = (f"GTM score {gtm}/5 for {sp_name}. {vendor_name} has minimal public messaging "
                   f"in this area ({ref_str}). ")
    else:
        gtm_rat = f"GTM score 0/5 for {sp_name}. No public messaging found for {vendor_name}."

    # Add top excerpt to GTM if available
    if excerpts:
        top_exc = excerpts[0]['excerpt'][:200]
        gtm_rat += f'Key evidence: "{top_exc}..."'

    # Build Proof rationale
    if proof >= 4:
        proof_rat = (f"Proof score {proof}/5 for {sp_name}. Verified through {n_excerpts} evidence "
                     f"excerpts from {n_urls} sources across {n_refs} schema references. ")
    elif proof >= 3:
        proof_rat = (f"Proof score {proof}/5 for {sp_name}. Supported by {n_excerpts} evidence "
                     f"excerpts with {ev_strength}. ")
    elif proof >= 2:
        proof_rat = (f"Proof score {proof}/5 for {sp_name}. Basic execution evidence from "
                     f"{n_refs} cross-schema assessment(s). ")
    elif proof >= 1:
        proof_rat = (f"Proof score {proof}/5 for {sp_name}. Minimal execution proof — "
                     f"{n_excerpts} excerpt(s) found. ")
    else:
        proof_rat = f"Proof score 0/5 for {sp_name}. No execution evidence found for {vendor_name}."

    # Add source rationale snippet if available
    if src_rationales:
        snippet = src_rationales[0][:180]
        proof_rat += f'Source assessment: "{snippet}..."'

    # Build gap assessment
    if abs(gap) <= 0.3:
        gap_text = f"Well-aligned ({gap:+.1f}) — messaging and execution evidence are consistent."
    elif gap > 1.5:
        gap_text = (f"Significant over-claim ({gap:+.1f}) — GTM messaging materially exceeds "
                    f"verifiable evidence. {n_excerpts} supporting excerpts found.")
    elif gap > 0.5:
        gap_text = (f"Moderate over-claim ({gap:+.1f}) — messaging somewhat ahead of documented "
                    f"execution evidence.")
    elif gap < -1.5:
        gap_text = (f"Significantly under-marketed ({gap:+.1f}) — execution evidence strongly "
                    f"exceeds public messaging.")
    elif gap < -0.3:
        gap_text = f"Under-marketed ({gap:+.1f}) — proof of execution exceeds current messaging."
    else:
        gap_text = f"Minor gap ({gap:+.1f})."

    return gtm_rat, proof_rat, gap_text


def main():
    # ── Load PMR vendor file ──
    pmr_path = os.path.join(BASE, "Product Market Readiness Vendor 1-0 Seed.json")
    with open(pmr_path, 'r', encoding='utf-8-sig') as f:
        pmr_data = json.load(f)

    pmr_vendors = pmr_data['vendors']
    print(f"Loaded {len(pmr_vendors)} PMR vendors")

    # ── Load all source schema vendor data ──
    source_schemas_data = {}  # schema_key -> {vendor_name: vendor_record}
    for schema_key, schema_info in SOURCE_SCHEMAS.items():
        fname = schema_info['file']
        vendors = load_vendors(fname)
        lookup = {v['vendor']: v for v in vendors if 'vendor' in v}
        source_schemas_data[schema_key] = lookup
        print(f"  {schema_key}: {len(lookup)} vendors from {fname}")

    # ── Enrich each PMR vendor ──
    stats = {
        'vendors_enriched': 0,
        'total_excerpts_added': 0,
        'total_urls_added': 0,
        'rationales_rewritten': 0,
        'vendors_no_evidence': 0,
    }

    for vendor in pmr_vendors:
        vname = vendor['vendor']
        sub_scores = vendor.get('sub_pillar_scores', {})
        if not sub_scores:
            stats['vendors_no_evidence'] += 1
            continue

        # Extract cross-schema evidence
        evidence_map = extract_evidence_for_pmr(vname, source_schemas_data)

        vendor_had_enrichment = False
        for sp_code, sp_entry in sub_scores.items():
            evidence = evidence_map.get(sp_code, {})
            excerpts = evidence.get('excerpts', [])
            urls = evidence.get('source_urls', [])

            # Update excerpts
            if excerpts:
                sp_entry['excerpts'] = excerpts
                stats['total_excerpts_added'] += len(excerpts)
                vendor_had_enrichment = True

            # Update URLs (merge with existing, dedup)
            existing_urls = sp_entry.get('source_urls', [])
            for url in urls:
                if url not in existing_urls:
                    existing_urls.append(url)
            sp_entry['source_urls'] = existing_urls[:6]
            stats['total_urls_added'] += len(urls)

            # Rewrite rationales with evidence-grounded text
            gtm_rat, proof_rat, gap_text = build_enriched_rationale(
                sp_code, sp_entry, evidence, vname
            )
            sp_entry['gtm_rationale'] = gtm_rat
            sp_entry['proof_rationale'] = proof_rat
            sp_entry['gap_assessment'] = gap_text
            stats['rationales_rewritten'] += 1

            # Add evidence metadata
            sp_entry['evidence_metadata'] = {
                'n_excerpts': len(excerpts),
                'n_source_urls': len(sp_entry.get('source_urls', [])),
                'n_schema_refs': len(evidence.get('source_schema_refs', [])),
                'evidence_strength': (
                    'strong' if len(excerpts) >= 3
                    else 'partial' if len(excerpts) >= 1
                    else 'score-based' if evidence.get('source_schema_refs')
                    else 'none'
                ),
                'source_schema_refs': evidence.get('source_schema_refs', []),
            }

        if vendor_had_enrichment:
            stats['vendors_enriched'] += 1
        else:
            stats['vendors_no_evidence'] += 1

    # ── Write enriched output ──
    output_path = os.path.join(BASE, "Product Market Readiness Vendor 1-1 Enriched.json")
    pmr_data['enrichment_metadata'] = {
        'source': 'Product Market Readiness Vendor 1-0 Seed.json',
        'enrichment_date': '2026-04-07',
        'method': 'Cross-schema evidence extraction from MDR, TRiSM, PreCyber, OffSec source files',
        'stats': stats,
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(pmr_data, f, indent=2, ensure_ascii=False)

    print(f"\n=== Enrichment Complete ===")
    print(f"  Vendors enriched (with excerpts): {stats['vendors_enriched']}")
    print(f"  Vendors with no cross-schema evidence: {stats['vendors_no_evidence']}")
    print(f"  Total excerpts added: {stats['total_excerpts_added']}")
    print(f"  Total URLs added: {stats['total_urls_added']}")
    print(f"  Rationales rewritten: {stats['rationales_rewritten']}")
    print(f"  Output: {output_path}")

    # ── Also update the seed file in-place ──
    with open(pmr_path, 'w', encoding='utf-8') as f:
        json.dump(pmr_data, f, indent=2, ensure_ascii=False)
    print(f"  Also updated seed file: {pmr_path}")

    # ── Sample output for verification ──
    print(f"\n=== Sample: CrowdStrike PPD-01 ===")
    cs = next((v for v in pmr_vendors if v['vendor'] == 'CrowdStrike'), None)
    if cs:
        entry = cs['sub_pillar_scores'].get('PPD-01', {})
        print(f"  GTM: {entry.get('gtm_messaging_score')}, Proof: {entry.get('proof_of_execution_score')}")
        print(f"  GTM Rationale: {entry.get('gtm_rationale', '')[:200]}")
        print(f"  Proof Rationale: {entry.get('proof_rationale', '')[:200]}")
        print(f"  Excerpts: {len(entry.get('excerpts', []))}")
        for i, exc in enumerate(entry.get('excerpts', [])[:2]):
            print(f"    [{i}] relevance={exc.get('relevance_score')}: {exc.get('excerpt', '')[:120]}...")
        print(f"  URLs: {len(entry.get('source_urls', []))}")
        em = entry.get('evidence_metadata', {})
        print(f"  Evidence: strength={em.get('evidence_strength')}, refs={em.get('source_schema_refs', [])}")


if __name__ == '__main__':
    main()
