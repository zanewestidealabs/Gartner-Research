"""Diagnose why -05 sub-pillar search terms get 0 hits.
Check cached page text for actual services-related content per pillar."""
import json, hashlib, re
from pathlib import Path

CACHE = Path("research/cache/pages_precyber")

# Load a vendor's evidence to find their cached URLs
with open("Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)
vendors = data if isinstance(data, list) else data["vendors"]

# Current EXM-05 search terms
exm05_terms = [
    "managed ASM", "managed attack surface", "CTEM as a service",
    "managed exposure management", "managed vulnerability",
    "vulnerability management service", "exposure management service",
    "managed EASM", "outsourced vulnerability management",
    "managed attack surface management", "exposure operations",
    "managed discovery", "managed remediation", "vulnerability operations",
]

# Test against Tenable, CrowdStrike, Palo Alto
for vname in ["Tenable", "CrowdStrike", "Palo Alto Networks", "Rapid7"]:
    v = next(x for x in vendors if x["vendor"] == vname)
    evidence = v.get("sub_pillar_evidence", {})
    
    # Collect all unique source URLs from evidence
    all_urls = set()
    for sid, ev in evidence.items():
        if isinstance(ev, dict):
            for u in ev.get("source_urls", []):
                all_urls.add(u)
    
    # Load cached pages
    all_text = ""
    pages_loaded = 0
    for url in all_urls:
        h = hashlib.sha1(url.encode()).hexdigest()
        cache_file = CACHE / f"{h}.txt"
        if cache_file.exists():
            all_text += " " + cache_file.read_text(encoding="utf-8", errors="replace")
            pages_loaded += 1
    
    all_lower = all_text.lower()
    text_len = len(all_lower)
    
    print(f"\n{'='*60}")
    print(f"{vname}: {pages_loaded} pages, {text_len:,} chars")
    
    # Check EXM-05 terms
    print(f"\n  EXM-05 term matches:")
    for term in exm05_terms:
        count = all_lower.count(term.lower())
        if count > 0:
            print(f"    '{term}' => {count} occurrences")
    
    # What exposure-related terms DO exist?
    print(f"\n  Exposure/ASM related terms found:")
    for term in ["attack surface", "exposure management", "vulnerability management",
                 "CTEM", "external attack", "EASM", "asset discovery", "risk exposure",
                 "continuous monitoring", "exposure", "surface management"]:
        count = all_lower.count(term.lower())
        if count > 0:
            print(f"    '{term}' => {count}")
    
    # What services terms exist?
    print(f"\n  Services terms found:")
    for term in ["managed", "service", "professional service", "consulting",
                 "managed service", "as a service", "-as-a-service", "deployment service",
                 "mssp", "mdr service", "soc service"]:
        count = all_lower.count(term.lower())
        if count > 0:
            print(f"    '{term}' => {count}")
    
    # Look for CO-OCCURRENCE: pillar terms near services terms
    print(f"\n  Co-occurrence (within 200 chars):")
    pillar_terms = ["attack surface", "exposure", "vulnerability", "CTEM", "EASM"]
    svc_terms = ["managed", "service", "professional", "consulting", "as-a-service"]
    for pt in pillar_terms:
        for idx in [m.start() for m in re.finditer(re.escape(pt.lower()), all_lower)]:
            window = all_lower[max(0,idx-100):idx+100+len(pt)]
            for st in svc_terms:
                if st.lower() in window and pt.lower() in window:
                    # Extract a readable snippet
                    snippet = all_text[max(0,idx-50):idx+50+len(pt)].replace('\n',' ').strip()
                    print(f"    '{pt}' + '{st}': ...{snippet[:120]}...")
                    break
            else:
                continue
            break  # Only show first co-occurrence per pillar term
