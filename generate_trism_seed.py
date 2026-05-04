"""
generate_trism_seed.py — Parse AI TRiSM vendor CSV and generate seed JSON file.

Reads: Rank - AI TRiSM Services - Top 60 Providers(Sheet1).csv
Writes: AI TRiSM Vendor 1-0 Seed.json
Schema: AI TriSM Schema 1_0.json

Completely separate from DFIR vendor files.
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CSV_FILE = ROOT / "Rank - AI TRiSM Services - Top 60 Providers(Sheet1).csv"
SCHEMA_FILE = ROOT / "AI TriSM Schema 1_0.json"
OUTPUT_FILE = ROOT / "AI TRiSM Vendor 1-0 Seed.json"

# ─────────────────────────────────────────────────────────────────────
# Vendor type classification (based on primary business model)
# ─────────────────────────────────────────────────────────────────────
VENDOR_TYPE_MAP = {
    # Big-4 / Consultancies
    "Accenture": "Consultancy",
    "Deloitte": "Consultancy",
    "PwC": "Consultancy",
    "EY (Ernst & Young)": "Consultancy",
    "KPMG": "Consultancy",
    "Capgemini": "Consultancy",
    "Cognizant": "Consultancy",
    "Tata Consultancy Services": "Consultancy",
    "Infosys": "Consultancy",
    "Wipro": "Consultancy",
    "HCLTech": "Consultancy",
    "Booz Allen Hamilton": "Consultancy",
    "BCG (Boston Consulting Group)": "Consultancy",
    "McKinsey & Company": "Consultancy",
    "Hitachi Consulting": "Consultancy",
    "DXC Technology": "Consultancy",
    "Fujitsu": "Consultancy",
    "Atos": "Consultancy",
    "NTT DATA": "Consultancy",
    "CGI": "Consultancy",
    "LTI (Larsen & Toubro Infotech)": "Consultancy",
    "Mphasis": "Consultancy",
    "Tech Mahindra": "Consultancy",
    "Mindtree": "Consultancy",
    "Sopra Steria": "Consultancy",
    "Unisys": "Consultancy",

    # Hyperscalers / Platform Vendors
    "Microsoft": "Hyperscaler",
    "Google Cloud": "Hyperscaler",
    "AWS (Amazon Web Services)": "Hyperscaler",
    "IBM": "Platform Vendor",
    "SAP": "Platform Vendor",
    "Oracle": "Platform Vendor",
    "Salesforce": "Platform Vendor",
    "ServiceNow": "Platform Vendor",
    "Palantir": "Platform Vendor",
    "SAS": "Platform Vendor",
    "Splunk": "Platform Vendor",
    "Elastic": "Platform Vendor",

    # Industrial
    "Siemens": "Platform Vendor",
    "Honeywell": "Platform Vendor",

    # Security Vendors
    "Securonix": "Security Vendor",
    "Darktrace": "Security Vendor",
    "Rapid7": "Security Vendor",
    "CrowdStrike": "Security Vendor",
    "Palo Alto Networks": "Security Vendor",
    "Fortinet": "Security Vendor",
    "Check Point Software": "Security Vendor",
    "Proofpoint": "Security Vendor",
    "Okta": "Security Vendor",
    "Qualys": "Security Vendor",
    "Tenable": "Security Vendor",
    "RSA Security": "Security Vendor",
    "Thales Group": "Security Vendor",
    "Veracode": "Security Vendor",
    "IBM Security": "Security Vendor",

    # Data Governance
    "OneTrust": "Data Governance",
    "TrustArc": "Data Governance",
    "Alation": "Data Governance",
    "Immuta": "Data Governance",
    "BigID": "Data Governance",

    # AI-Native
    "DataRobot": "AI-Native",
    "OpenAI": "AI-Native",
    "Anthropic": "AI-Native",
}

# is_ai_first: vendors whose core business is AI
AI_FIRST_VENDORS = {
    "Darktrace", "DataRobot", "OpenAI", "Anthropic", "Palantir",
}

# is_startup: vendors that are/were startups (smaller, newer entrants)
STARTUP_VENDORS = {
    "Darktrace", "DataRobot", "BigID", "Immuta", "Alation",
    "OpenAI", "Anthropic", "TrustArc", "Securonix",
}

PILLARS = ["GOV", "RUN", "INF"]
SUBPILLAR_IDS = [f"{p}-{i:02d}" for p in PILLARS for i in range(1, 5)]


def load_schema_labels():
    """Load sub-pillar names from the schema file."""
    with open(SCHEMA_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    top_key = list(data.keys())[0]
    schema = data[top_key]
    labels = {}
    for sp_id, sp_data in schema.get("sub_pillars", {}).items():
        labels[sp_id] = sp_data.get("name", sp_id)
    return labels


def parse_csv():
    """Parse the vendor CSV and return list of (name, differentiation) tuples."""
    vendors = []
    with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Skip header rows (rows 0 and 1 in 0-indexed = spreadsheet rows 1-2)
    # Vendor data starts at row index 2 (spreadsheet row 3)
    for row in rows[2:]:
        if not row or not row[0].strip():
            continue
        name = row[0].strip()
        # Skip if this looks like a header
        if name.lower() == "company name":
            continue
        diff = row[1].strip() if len(row) > 1 else ""
        vendors.append((name, diff))

    return vendors


def build_vendor_record(name, differentiation, schema_labels):
    """Build a single vendor record for the seed file."""
    vendor_type = VENDOR_TYPE_MAP.get(name, "")
    is_ai_first = name in AI_FIRST_VENDORS
    is_startup = name in STARTUP_VENDORS

    return {
        "vendor": name,
        "region": "Global",
        "specialization": "",
        "is_startup": is_startup,
        "is_ai_first": is_ai_first,
        "vendor_type": vendor_type,
        "primary_trism_layer": "",
        "notable_differentiation": differentiation,
        "capability_analysis": "",
        "pillar_scores": {p: 0 for p in PILLARS},
        "sub_pillar_scores_current": {sp: 0 for sp in SUBPILLAR_IDS},
        "sub_pillar_schema_labels": dict(schema_labels),
    }


def main():
    print(f"Reading schema: {SCHEMA_FILE.name}")
    schema_labels = load_schema_labels()
    print(f"  Sub-pillar labels: {len(schema_labels)}")
    for sp_id, name in sorted(schema_labels.items()):
        print(f"    {sp_id}: {name}")

    print(f"\nParsing CSV: {CSV_FILE.name}")
    vendors_raw = parse_csv()
    print(f"  Found {len(vendors_raw)} vendors")

    # Build vendor records
    vendors = []
    for name, diff in vendors_raw:
        v = build_vendor_record(name, diff, schema_labels)
        vendors.append(v)
        vtype = v["vendor_type"] or "Unclassified"
        flags = []
        if v["is_ai_first"]:
            flags.append("AI-First")
        if v["is_startup"]:
            flags.append("Startup")
        flag_str = f" [{', '.join(flags)}]" if flags else ""
        print(f"  {len(vendors):2d}. {name} — {vtype}{flag_str}")

    # Build output
    output = {
        "schema_ref": "AI TriSM Schema 1_0.json",
        "schema_version": "1.0",
        "vendor_count": len(vendors),
        "vendors": vendors,
    }

    OUTPUT_FILE.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nWrote: {OUTPUT_FILE.name}")
    print(f"  {len(vendors)} vendors, schema_ref={output['schema_ref']}")


if __name__ == "__main__":
    main()
