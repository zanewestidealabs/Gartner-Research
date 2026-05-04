"""
Clean up AI-isms in the CPO v3 analyst take report.
Pass 2: targets actual current file content (straight quotes, remaining em dashes).
"""
import json, re

with open("analyst_take_reports.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)

v3 = [r for r in data["reports"] if r["id"] == "aiuc1-agentic-compliance-v3-cpo"][0]

raw_before = json.dumps(v3, ensure_ascii=False)
em_before = raw_before.count("\u2014")
print(f"Em dashes before: {em_before}")

b = v3["body_sections"]

# ============================================================
# 1. EM DASHES — replace all 6 remaining occurrences
# ============================================================

# Section 1 heading: "Doesn't — And"
b[1]["heading"] = b[1]["heading"].replace(
    "Doesn\u2019t \u2014 And",
    "Does Not, And"
).replace(
    "Doesn't \u2014 And",
    "Does Not, And"
)

# Section 1 body: "PCI DSS — it is"
b[1]["body"] = b[1]["body"].replace(
    "PCI DSS \u2014 it is",
    "PCI DSS. It is"
)

# Catch-all: any remaining em dashes in body sections
for section in b:
    section["body"] = section["body"].replace(" \u2014 ", ", ")
    section["heading"] = section["heading"].replace(" \u2014 ", ", ")

# Positioning statements and all nested string fields
def strip_emdash(text):
    """Replace em dashes with commas."""
    return text.replace(" \u2014 ", ", ").replace("\u2014", ", ")

def walk_and_clean(obj):
    """Recursively clean em dashes from all string values."""
    if isinstance(obj, str):
        return strip_emdash(obj)
    elif isinstance(obj, list):
        return [walk_and_clean(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: walk_and_clean(v) for k, v in obj.items()}
    return obj

v3["positioning_statements"] = walk_and_clean(v3["positioning_statements"])
v3["label"] = strip_emdash(v3["label"])
v3["subtitle"] = strip_emdash(v3["subtitle"])
v3["notes"] = strip_emdash(v3["notes"])
if "guidance" in v3:
    v3["guidance"] = walk_and_clean(v3["guidance"])

# ============================================================
# 2. CONTRACTIONS — expand to formal English (skip possessives)
# ============================================================
contraction_pairs = [
    ("I've", "I have"), ("I'd", "I would"), ("I'm", "I am"),
    ("you'll", "you will"), ("you're", "you are"), ("you've", "you have"),
    ("we'll", "we will"), ("we're", "we are"), ("we've", "we have"),
    ("they'll", "they will"), ("they're", "they are"), ("they've", "they have"),
    ("it's", "it is"), ("It's", "It is"),
    ("isn't", "is not"), ("doesn't", "does not"), ("don't", "do not"),
    ("won't", "will not"), ("can't", "cannot"), ("didn't", "did not"),
    ("wouldn't", "would not"), ("couldn't", "could not"), ("shouldn't", "should not"),
    ("hasn't", "has not"), ("haven't", "have not"), ("wasn't", "was not"),
    ("weren't", "were not"), ("aren't", "are not"),
    ("that's", "that is"), ("That's", "That is"),
    ("here's", "here is"), ("Here's", "Here is"),
    ("what's", "what is"), ("What's", "What is"),
    ("there's", "there is"), ("There's", "There is"),
    ("Doesn't", "Does Not"), ("doesn't", "does not"),
]

for section in b:
    for old, new in contraction_pairs:
        section["body"] = section["body"].replace(old, new)
        section["heading"] = section["heading"].replace(old, new)

# ============================================================
# 3. AI FORMULA PATTERNS
# ============================================================
# "The uncomfortable truth:" → "The gap:"
b[0]["body"] = b[0]["body"].replace(
    "The uncomfortable truth:",
    "The reality:"
)
# "Let me make this concrete" → "Consider"
b[2]["body"] = b[2]["body"].replace(
    "Let me make this concrete with the vertical where the gap is most dangerous: healthcare.",
    "Consider the vertical where the gap is most dangerous: healthcare."
)
# "I predict you'll" → "you will likely"
b[4]["body"] = b[4]["body"].replace(
    "I predict you will",
    "You will likely"
)

# ============================================================
# 4. VERIFY
# ============================================================
raw_after = json.dumps(v3, ensure_ascii=False)
em_after = raw_after.count("\u2014")
print(f"Em dashes after: {em_after}")

# Remaining contractions (exclude possessives like product's, platform's, customers')
for i, s in enumerate(b):
    matches = re.findall(r"\b(\w+'(?:ve|ll|re|d|m|s|t|nt))\b", s["body"], re.IGNORECASE)
    # Filter possessives
    real = [m for m in matches if m.lower() not in ("product's", "platform's", "customer's", "customers'", "buyer's")]
    if real:
        print(f"  Section {i} remaining contractions: {real}")
    matches_h = re.findall(r"\b(\w+'(?:ve|ll|re|d|m|s|t|nt))\b", s["heading"], re.IGNORECASE)
    if matches_h:
        print(f"  Section {i} heading remaining contractions: {matches_h}")

# Word count
total = sum(len(s["body"].split()) for s in b)
per_section = [len(s["body"].split()) for s in b]
print(f"Word count: {total} ({'+'.join(str(w) for w in per_section)})")

# Show headings and first 200 chars
for i, s in enumerate(b):
    print(f"\n--- Section {i}: {s['heading'][:70]} ---")
    print(s["body"][:200])

# Write
with open("analyst_take_reports.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=6, ensure_ascii=False)

print("\nDone.")
