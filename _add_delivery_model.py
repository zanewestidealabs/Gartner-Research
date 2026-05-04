"""
Add delivery_model field to all MDR vendor files.

Delivery model values:
- "Platform Only": Vendor sells the platform, client operates it themselves
- "Platform + Partner": Vendor platform is delivered via MSSP partners to end customers
- "Managed Service": Vendor delivers both platform and operations as a unified service

Classification logic is based on how the vendor actually goes to market.
Some vendors have multiple motions (e.g., Sophos sells direct MDR AND through partners).
We classify by their PRIMARY delivery model for the MDR service specifically.
"""

import json
import copy

# ── Classification map ──────────────────────────────────────────────────
# Built from vendor descriptions, differentiators, and known business models.

DELIVERY_MODEL = {
    # Platform MDR vendors that sell managed service directly
    "CrowdStrike":          "Managed Service",      # Falcon Complete = fully managed MDR
    "Palo Alto Networks":   "Managed Service",      # Unit 42 MDR = managed service
    "SentinelOne":          "Managed Service",      # Singularity MDR (Vigilance) = managed
    "Sophos":               "Platform + Partner",   # Largest MDR by customer count, strong channel/MSSP partner ecosystem
    "Bitdefender":          "Managed Service",      # GravityZone MDR = managed service
    "Trend Micro":          "Managed Service",      # Vision One MDR = managed service
    "Microsoft":            "Platform + Partner",   # Defender Experts = managed, but huge partner ecosystem is primary delivery
    "Cisco":                "Platform + Partner",   # XDR platform + partner-delivered services
    "Fortinet":             "Platform + Partner",   # FortiGuard MDR but primarily through MSSP/partner channel
    "Darktrace":            "Managed Service",      # AI-native self-learning platform with managed service
    "Vectra AI":            "Platform Only",        # Primarily sells AI platform, partners may operate
    "Rapid7":               "Managed Service",      # InsightIDR MDR = managed service offering
    "ESET":                 "Managed Service",      # ESET MDR = managed detection and response service
    "Trellix":              "Platform Only",        # Primarily XDR platform, emerging managed service
    "Cynet":                "Managed Service",      # CyOps 24/7 MDR included with platform
    "Check Point":          "Managed Service",      # Infinity MDR/MPR = managed service
    "Kaspersky":            "Managed Service",      # Kaspersky MDR = managed service
    "F-Secure (WithSecure)":"Managed Service",      # WithSecure MDR = co-security managed service
    "Attivo Networks (SentinelOne)": "Platform Only", # Identity detection tech, now SentinelOne module
    "Stellar Cyber":        "Platform + Partner",   # Open XDR platform purpose-built for MSSPs
    "Radiant Security":     "Platform Only",        # AI SOC analyst platform, not managed service
    "Dropzone AI":          "Platform Only",        # Autonomous AI SOC analyst platform
    "Prophet Security":     "Platform Only",        # AI-powered SOC analyst platform
    "Lumu Technologies":    "Platform Only",        # Continuous compromise assessment platform
    "Securonix":            "Platform Only",        # Cloud-native SIEM platform, partners deliver MDR
    "LogRhythm (Exabeam)":  "Platform Only",        # SIEM/analytics platform, partners deliver MDR
    "Elastic":              "Platform Only",        # Open platform, not traditional MDR provider

    # Pureplay MDR - all managed service by definition
    "Arctic Wolf":          "Managed Service",      # Concierge Security Team = fully managed
    "Secureworks":          "Managed Service",      # Taegis MDR = managed service
    "Expel":                "Managed Service",      # Transparent MDR = fully managed
    "Red Canary":           "Managed Service",      # Outcome-focused MDR = fully managed
    "Deepwatch":            "Managed Service",      # Enterprise MDR = squad-based managed
    "Binary Defense":       "Managed Service",      # Open XDR MDR = managed service
    "Blackpoint Cyber":     "Platform + Partner",   # Purpose-built FOR MSP channel, partners deliver
    "Huntress":             "Platform + Partner",   # Built for SMB and MSP channel, partners deliver
    "Todyl":                "Platform + Partner",   # Unified platform purpose-built for MSPs
    "AirMDR":               "Managed Service",      # AI-first MDR = managed service
    "Underdefense":         "Managed Service",      # Analyst-led MDR = managed service
    "Critical Start":       "Managed Service",      # MDR with ZTAP = managed service
    "Metabase Q":           "Managed Service",      # Mexico-based MDR = managed service
    "Nclose":               "Managed Service",      # South African MDR = managed service
    "Proficio":             "Managed Service",      # ProSOC MDR = managed service
    "BlueVoyant":           "Managed Service",      # Managed SOC/MDR = managed service
    "First Watch Technologies": "Managed Service",  # Squad Model MDR = managed service

    # Extended MDR / MSSP - most deliver managed services
    "ReliaQuest":           "Platform Only",        # GreyMatter platform, customer operates
    "Ontinue":              "Managed Service",      # Microsoft-centric MXDR = managed service
    "Trustwave":            "Managed Service",      # SpiderLabs MDR = managed service
    "Swimlane":             "Platform Only",        # SOAR/automation platform, not MDR service
    "Recorded Future":      "Platform Only",        # Threat intelligence platform
    "Cyble":                "Platform Only",        # Threat intelligence platform
    "Flashpoint":           "Platform Only",        # Threat intelligence platform

    # Deception/AMTD specialists - platform only
    "Acalvio Technologies": "Platform Only",        # Deception technology platform
    "CounterCraft":         "Platform Only",        # Deception platform (Telefonica Tech)
    "Morphisec":            "Platform Only",        # AMTD technology platform

    # DRP/Disinfo specialists - platform only
    "ZeroFox":              "Platform Only",        # Digital risk protection platform
    "Nisos":                "Managed Service",      # Managed intelligence company
    "Blackbird.AI":         "Platform Only",        # Narrative intelligence platform
    "Reality Defender":     "Platform Only",        # Deepfake detection platform (API-first)

    # IR-Enhanced MDR
    "Google Cloud (Mandiant)":  "Managed Service",  # Mandiant MDR = managed service
    "IBM Security":             "Managed Service",  # IBM MDR Services = managed service
    "Mandiant (standalone reference)": "Managed Service", # Mandiant Managed Defense
    "Sygnia":               "Managed Service",      # Elite proactive MDR = managed
    "NCC Group":            "Managed Service",      # MDR + DFIR = managed service
    "CyberCX":              "Managed Service",      # Australia's largest MDR = managed service
    "Group-IB":             "Managed Service",      # Managed XDR service

    # Regional MSSPs / consultancies - managed services
    "Orange Cyberdefense":  "Managed Service",      # Europe's largest MSSP = managed service
    "Kudelski Security":    "Managed Service",      # Swiss MDR = managed service
    "Bridewell":            "Managed Service",      # UK MDR = managed service
    "mnemonic":             "Managed Service",      # Argus managed defense
    "Ensign InfoSecurity":  "Managed Service",      # APAC managed security
    "Verizon":              "Managed Service",      # Managed Security Services
    "NTT Security":         "Managed Service",      # Samurai MDR = managed
    "Optiv":                "Managed Service",      # MSSP/MDR integrator

    # Big 4 / System Integrators - managed service
    "Tata Consultancy Services": "Managed Service",
    "Infosys (Infosys Cyber Next)": "Managed Service",
    "Wipro (Wipro CyberSecurist)": "Managed Service",
    "Deloitte Cyber":       "Managed Service",
    "Accenture Security":   "Managed Service",
    "PwC Cybersecurity":    "Managed Service",
    "EY Cybersecurity":     "Managed Service",

    # LatAm
    "Tempest Security Intelligence": "Managed Service",
    "NeoSecure":            "Managed Service",
    "Scitum (Telmex)":      "Managed Service",
    "Fluid Attacks":        "Platform Only",        # Continuous security testing platform
    "Appgate":              "Platform Only",        # ZTNA + fraud prevention platform
    "Axur":                 "Platform Only",        # Digital risk protection platform
    "ISH Tecnologia":       "Managed Service",      # Brazilian MSSP
    "Globant (Security Studio)": "Managed Service", # Security advisory + managed

    # Africa
    "Performanta":          "Managed Service",      # South African MDR
    "Liquid C2 (Cassava Technologies)": "Managed Service", # Pan-African MSSP
    "Digital Encode":       "Managed Service",      # West African MSSP
    "Serianu (now Managed Security Africa)": "Managed Service", # East African
    "BCX (Telkom)":         "Managed Service",      # Telkom SA managed services
    "Cyanre Digital Forensics": "Managed Service",  # DFIR + managed forensics
    "DarkTrace Africa (via Convergence Partners)": "Platform + Partner", # Regional partner for Darktrace
    "Netstar":              "Managed Service",      # Cape Town managed IT + security
}

# ── Apply to all vendor files ────────────────────────────────────────────

FILES = [
    "MDR Services Vendor 1-0 Seed.json",
    "MDR Services Vendor 2-0 Researched.json",
    "MDR Services Vendor 2-1 Consolidated.json",
]

# Also check capability and pricing files
EXTRA_FILES = [
    "MDR Services Vendor Capability 1-0 Seed.json",
    "MDR Services Vendor Pricing 1-0 Seed.json",
    "MDR Services Vendor Pricing 2-0 Researched.json",
    "MDR Services Vendor Pricing 2-1 AI Enriched.json",
]

import os

for fname in FILES + EXTRA_FILES:
    if not os.path.exists(fname):
        print(f"SKIP (not found): {fname}")
        continue

    with open(fname, "r", encoding="utf-8") as f:
        data = json.load(f)

    vendors = data.get("vendors", [])
    updated = 0
    missing = []

    for v in vendors:
        name = v.get("vendor", "?")
        if name in DELIVERY_MODEL:
            v["delivery_model"] = DELIVERY_MODEL[name]
            updated += 1
        else:
            missing.append(name)

    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"OK: {fname} - {updated}/{len(vendors)} classified")
    if missing:
        print(f"  MISSING: {missing}")

# ── Summary stats ────────────────────────────────────────────────────────
print("\n=== Delivery Model Distribution (2-1 Consolidated) ===")
with open("MDR Services Vendor 2-1 Consolidated.json", "r", encoding="utf-8") as f:
    data = json.load(f)

from collections import Counter
counts = Counter(v.get("delivery_model", "UNSET") for v in data["vendors"])
for model, count in sorted(counts.items()):
    print(f"  {model}: {count}")
print(f"  TOTAL: {sum(counts.values())}")
