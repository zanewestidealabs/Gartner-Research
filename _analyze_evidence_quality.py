"""
Deep analysis of evidence QUALITY vs assigned scores.
Compare: high-score sub-pillars vs evidence quality indicators.
This shows where scores outpace the actual evidence strength.
"""
import json
from collections import defaultdict
import statistics

def load_vendors(filepath):
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
    return data.get("vendors", [])

SCHEMA_FILES = {
    "AI TRiSM": "AI TRiSM Vendor 2-1 Consolidated.json",
    "MDR Services": "MDR Services Vendor 2-1 Consolidated.json",
    "Preemptive Cyber": "Preemptive Cybersecurity Vendor 2-1 Consolidated.json",
    "Offensive Security": "Offensive Security Vendor 2-1 Consolidated.json",
}

def analyze_evidence_quality(ev_obj):
    """Extract evidence quality metrics from a sub-pillar evidence object."""
    if not isinstance(ev_obj, dict):
        return None
    
    metrics = {}
    
    # Source count
    urls = ev_obj.get("source_urls", [])
    sources = ev_obj.get("sources", [])
    metrics["source_count"] = len(urls) if isinstance(urls, list) else 0
    metrics["source_count"] += len(sources) if isinstance(sources, list) else 0
    
    # Excerpt analysis
    excerpts = ev_obj.get("excerpts", [])
    if isinstance(excerpts, list) and excerpts:
        relevance_scores = []
        for ex in excerpts:
            if isinstance(ex, dict):
                rs = ex.get("relevance_score", 0)
                if rs:
                    relevance_scores.append(float(rs))
        metrics["excerpt_count"] = len(excerpts)
        metrics["avg_relevance"] = statistics.mean(relevance_scores) if relevance_scores else 0
        metrics["max_relevance"] = max(relevance_scores) if relevance_scores else 0
    else:
        metrics["excerpt_count"] = 0
        metrics["avg_relevance"] = 0
        metrics["max_relevance"] = 0
    
    # Specificity and criteria hits
    metrics["specificity"] = ev_obj.get("sub_pillar_specificity", 0) or 0
    metrics["criteria_hits"] = ev_obj.get("schema_criteria_hits", 0) or ev_obj.get("criteria_hit_count", 0) or 0
    
    # Rationale
    rat = ev_obj.get("rationale", "") or ev_obj.get("notes", "")
    metrics["has_rationale"] = bool(rat and len(str(rat)) > 20)
    
    return metrics

# Collect all score-vs-evidence pairs
all_pairs = []  # (score, evidence_quality_score, schema, vendor, sub_pillar)

for schema_name, filepath in SCHEMA_FILES.items():
    vendors = load_vendors(filepath)
    
    for v in vendors:
        name = v.get("vendor", "?")
        subs = v.get("sub_pillar_scores_current", {})
        evidence = v.get("sub_pillar_evidence", {})
        
        for sp_id, score in subs.items():
            if score == 0:
                continue
            
            ev_obj = evidence.get(sp_id, {})
            metrics = analyze_evidence_quality(ev_obj)
            
            if metrics:
                # Compute a composite evidence quality score (0-5 scale)
                # Based on: sources, excerpts, relevance, specificity, criteria hits
                eq = 0
                if metrics["source_count"] >= 3:
                    eq += 1.0
                elif metrics["source_count"] >= 1:
                    eq += 0.5
                
                if metrics["excerpt_count"] >= 5:
                    eq += 1.5
                elif metrics["excerpt_count"] >= 3:
                    eq += 1.0
                elif metrics["excerpt_count"] >= 1:
                    eq += 0.5
                
                eq += min(metrics["avg_relevance"] / 100 * 1.5, 1.5) if metrics["avg_relevance"] > 0 else 0
                
                if metrics["specificity"] >= 0.7:
                    eq += 0.5
                elif metrics["specificity"] >= 0.3:
                    eq += 0.25
                
                if metrics["criteria_hits"] >= 3:
                    eq += 0.5
                elif metrics["criteria_hits"] >= 1:
                    eq += 0.25
                
                all_pairs.append({
                    "score": score,
                    "eq": round(eq, 2),
                    "schema": schema_name,
                    "vendor": name,
                    "sub_pillar": sp_id,
                    "sources": metrics["source_count"],
                    "excerpts": metrics["excerpt_count"],
                    "relevance": metrics["avg_relevance"],
                    "specificity": metrics["specificity"],
                })

print(f"Total score-evidence pairs: {len(all_pairs)}")

# Bin by evidence quality
eq_bins = {
    "Strong (EQ 3.0+)": [p for p in all_pairs if p["eq"] >= 3.0],
    "Moderate (EQ 1.5-3.0)": [p for p in all_pairs if 1.5 <= p["eq"] < 3.0],
    "Weak (EQ 0.5-1.5)": [p for p in all_pairs if 0.5 <= p["eq"] < 1.5],
    "Absent (EQ <0.5)": [p for p in all_pairs if p["eq"] < 0.5],
}

print(f"\n{'='*70}")
print(f"  SCORE vs EVIDENCE QUALITY")
print(f"{'='*70}")

for label, pairs in eq_bins.items():
    if pairs:
        scores = [p["score"] for p in pairs]
        eqs = [p["eq"] for p in pairs]
        print(f"\n  {label}:")
        print(f"    Count: {len(pairs)} sub-pillars")
        print(f"    Average assigned score: {statistics.mean(scores):.2f}")
        print(f"    Average EQ score:       {statistics.mean(eqs):.2f}")
        
        # Score distribution
        high = sum(1 for s in scores if s >= 4.0)
        mid = sum(1 for s in scores if 2.5 <= s < 4.0)
        low = sum(1 for s in scores if s < 2.5)
        print(f"    Score ≥4.0: {high} ({high/len(scores)*100:.1f}%)")
        print(f"    Score 2.5-4.0: {mid} ({mid/len(scores)*100:.1f}%)")
        print(f"    Score <2.5: {low} ({low/len(scores)*100:.1f}%)")

# Compute the REAL gap: difference between score and evidence quality
print(f"\n{'='*70}")
print(f"  THE REAL CREDIBILITY GAP: Score vs Evidence Quality")
print(f"{'='*70}")

gaps = [(p["score"] - p["eq"]) for p in all_pairs]
positive_gaps = [g for g in gaps if g > 0.5]  # Score exceeds evidence by >0.5
aligned_gaps = [g for g in gaps if -0.5 <= g <= 0.5]
negative_gaps = [g for g in gaps if g < -0.5]

print(f"\nAll {len(gaps)} sub-pillar score-vs-evidence comparisons:")
print(f"  Score EXCEEDS evidence quality (gap>0.5): {len(positive_gaps)} ({len(positive_gaps)/len(gaps)*100:.1f}%)")
print(f"  Roughly aligned (±0.5):                   {len(aligned_gaps)} ({len(aligned_gaps)/len(gaps)*100:.1f}%)")
print(f"  Evidence EXCEEDS score (gap<-0.5):         {len(negative_gaps)} ({len(negative_gaps)/len(gaps)*100:.1f}%)")
print(f"  Mean gap: {statistics.mean(gaps):+.2f}")
print(f"  Median gap: {statistics.median(gaps):+.2f}")

# More detailed distribution
dist = [
    ("Score > EQ by 3+", lambda g: g >= 3.0),
    ("Score > EQ by 2-3", lambda g: 2.0 <= g < 3.0),
    ("Score > EQ by 1-2", lambda g: 1.0 <= g < 2.0),
    ("Score > EQ by 0.5-1", lambda g: 0.5 <= g < 1.0),
    ("Aligned (±0.5)", lambda g: -0.5 <= g < 0.5),
    ("EQ > Score by 0.5-1", lambda g: -1.0 <= g < -0.5),
    ("EQ > Score by 1+", lambda g: g < -1.0),
]

print(f"\n  DETAILED DISTRIBUTION:")
for label, fn in dist:
    count = sum(1 for g in gaps if fn(g))
    print(f"    {label}: {count} ({count/len(gaps)*100:.1f}%)")

# Per-schema breakdown
print(f"\n  PER-SCHEMA GAP (Score - Evidence Quality):")
for schema in SCHEMA_FILES:
    schema_gaps = [p["score"] - p["eq"] for p in all_pairs if p["schema"] == schema]
    if schema_gaps:
        over = sum(1 for g in schema_gaps if g > 0.5)
        print(f"    {schema}: mean={statistics.mean(schema_gaps):+.2f}, score>EQ={over}/{len(schema_gaps)} ({over/len(schema_gaps)*100:.0f}%)")

# Per-vendor analysis: vendors with biggest score-evidence disconnect
print(f"\n  TOP 15 VENDORS: Largest Score-Evidence Disconnect:")
vendor_gaps = defaultdict(list)
for p in all_pairs:
    vendor_gaps[f"{p['vendor']} ({p['schema']})"].append(p["score"] - p["eq"])

vendor_avg_gaps = [(k, statistics.mean(v), len(v)) for k, v in vendor_gaps.items()]
vendor_avg_gaps.sort(key=lambda x: x[1], reverse=True)

for name, avg_gap, n in vendor_avg_gaps[:15]:
    print(f"    {name}: avg gap={avg_gap:+.2f} (n={n})")

print(f"\n  TOP 10 VENDORS: Best Evidence-Score Alignment:")
for name, avg_gap, n in vendor_avg_gaps[-10:][::-1]:
    print(f"    {name}: avg gap={avg_gap:+.2f} (n={n})")
