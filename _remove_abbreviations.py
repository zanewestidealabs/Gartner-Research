"""Remove pillar abbreviations and KC from report text in precyber_market_insight_reports.json."""
import json, re, pathlib

FILE = pathlib.Path(__file__).parent / "precyber_market_insight_reports.json"

data = json.loads(FILE.read_text(encoding="utf-8"))

# ── Pillar full names ──
PILLARS = {
    "EXM": "Exposure Management",
    "AMT": "Adversary Management",
    "PPM": "Posture & Policy Management",
    "ADR": "Autonomous Detection & Response",
    "SVC": "Services & Capability Maturity",
}

def clean(text):
    if not isinstance(text, str):
        return text

    # 1. Remove bracketed definitions like "(EXM)" or "[EXM]" after the full name
    #    e.g. "Exposure Management (EXM)" → "Exposure Management"
    #         "Exposure Management [EXM]" → "Exposure Management"
    for abbr, full in PILLARS.items():
        # Full name followed by bracketed abbreviation
        text = re.sub(re.escape(full) + r'\s*\(' + abbr + r'\)', full, text)
        text = re.sub(re.escape(full) + r'\s*\[' + abbr + r'\]', full, text)

    # 2. Handle "KC Phase(s) N" patterns → "Kill Chain Phase(s) N"
    text = re.sub(r'\bKC\s+(Phases?\s)', r'Kill Chain \1', text)
    # "KC 1-3" style → "Kill Chain Phases 1-3"
    text = re.sub(r'\bKC\s+(\d)', r'Kill Chain Phases \1', text)

    # 3. Replace standalone pillar abbreviations with full names
    #    Use word boundaries but avoid matching inside longer words
    for abbr, full in PILLARS.items():
        text = re.sub(r'\b' + abbr + r'\b', full, text)

    # 4. Clean up awkward repetitions from step 3 applied after step 1
    #    e.g. "Exposure Management Management" won't happen because step 1 removes (EXM)
    #    But catch "Services & Capability Maturity Maturity" etc.
    for full in PILLARS.values():
        doubled = full + " " + full.split()[-1]
        text = text.replace(doubled, full)

    # 5. Handle any remaining "KC" as standalone word
    text = re.sub(r'\bKC\b', 'Kill Chain', text)

    return text


def process_value(obj):
    """Recursively process all string values in the JSON structure."""
    if isinstance(obj, str):
        return clean(obj)
    elif isinstance(obj, list):
        return [process_value(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: process_value(v) for k, v in obj.items()}
    return obj


# Count before
before_json = json.dumps(data)
abbr_counts_before = {}
for abbr in list(PILLARS.keys()) + ["KC"]:
    abbr_counts_before[abbr] = len(re.findall(r'\b' + abbr + r'\b', before_json))

# Process
data = process_value(data)

# Count after
after_json = json.dumps(data)
abbr_counts_after = {}
for abbr in list(PILLARS.keys()) + ["KC"]:
    abbr_counts_after[abbr] = len(re.findall(r'\b' + abbr + r'\b', after_json))

# Write
FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

print("=== Abbreviation Removal Report ===")
for abbr in list(PILLARS.keys()) + ["KC"]:
    b, a = abbr_counts_before[abbr], abbr_counts_after[abbr]
    print(f"  {abbr}: {b} → {a}  (removed {b - a})")
print(f"\nFile size: {len(before_json):,} → {len(after_json):,} chars")
print("Done.")
