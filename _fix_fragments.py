"""Fix specific sentence fragments and awkward constructions from automated cleanup."""
import json

with open('analyst_take_reports.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

r = data['reports'][1]

# Helper: find-and-replace in all string values recursively
fixes = [
    # Label: period should be hyphen
    ("Analyst Take. AIUC-1:", "Analyst Take - AIUC-1:"),

    # Body 0: fragment after period
    ("SaaS platforms. Scoring them against", "SaaS platforms, scoring them against"),
    ("autonomous actions. On data those", "autonomous actions on data those"),

    # Body 1: missing comma after parenthetical
    ("the network boundaries) AIUC-1 governs", "the network boundaries), AIUC-1 governs"),

    # Body 2 heading: comma in heading  
    ("The Healthcare Problem, and Why", "The Healthcare Problem and Why"),
    
    # Body 2: fragment  
    ("defined workflows. AI agents don't follow workflows. They reason", "defined workflows. AI agents don't follow workflows; they reason"),
    ("It's not just healthcare. Financial", "It's not just healthcare; financial"),

    # Body 3: broken sentence with fragments
    ("AIUC-1's third-party testing mandates. B001 (adversarial robustness), C010-C012 (harmful output testing), D002 (hallucination testing), D004 (tool call testing). Are vendor obligations",
     "AIUC-1's third-party testing mandates (B001 adversarial robustness, C010-C012 harmful output testing, D002 hallucination testing, D004 tool call testing) are vendor obligations"),
    ("That's not dumbing it down. That's making", "That's not dumbing it down; it's making"),

    # Body 4: fragment from paired em-dash
    ("Third (and this is the action that will differentiate leaders from followers) run a 10-case pilot audit.",
     "Third, run a 10-case pilot audit. This is the action that will differentiate leaders from followers."),
    ("Document this gap explicitly. It's the business case", "Document this gap explicitly; it's the business case"),
    ("not just in compliance, but in the trust", "not just in compliance but in the trust"),

    # PS0: fragment
    ("(but they audit the infrastructure, not the inference. When a healthcare",
     "(but they audit the infrastructure, not the inference). When a healthcare"),
    ("(including lineage graphs, tool call restrictions, and third-party hallucination testing) That directly close",
     "(including lineage graphs, tool call restrictions, and third-party hallucination testing) that directly close"),

    # PS1: fragments
    ("same AI governance gap as a 50,000-person hospital system, but zero budget",
     "same AI governance gap as a 50,000-person hospital system but zero budget"),
    ("on the customer organization. Requiring internal policies, audit readiness, and ongoing monitoring. For AI-specific risks",
     "on the customer organization, requiring internal policies, audit readiness, and ongoing monitoring. For AI-specific risks"),

    # PS2: fragment from em-dash to period
    ("flags a transaction as fraudulent. Can you explain why it did that? Can you prove it was authorized to? Today",
     "flags a transaction as fraudulent, can you explain why it did that? Can you prove it was authorized to? Today"),
    ("They reason, plan, invoke tools, and make decisions dynamically. Traditional audit logs capture what happened but not why",
     "They reason, plan, invoke tools, and make decisions dynamically. Traditional audit logs capture what happened, but not why"),

    # General: ". That" fragments (common from em-dash replacement)
    ("the inference). When", "the inference). When"),

    # Subtitle cleanup
    ("leave agentic AI ungoverned, and what AIUC-1 changes",
     "leave agentic AI ungoverned and what AIUC-1 changes"),
]

def apply_fixes(s):
    if not isinstance(s, str):
        return s
    for old, new in fixes:
        s = s.replace(old, new)
    return s

def fix_obj(obj):
    if isinstance(obj, str):
        return apply_fixes(obj)
    elif isinstance(obj, list):
        return [fix_obj(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: fix_obj(v) for k, v in obj.items()}
    return obj

data['reports'][1] = fix_obj(r)

with open('analyst_take_reports.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Fixes applied successfully")

# Quick verification
with open('analyst_take_reports.json', 'r', encoding='utf-8') as f:
    txt = f.read()
json.loads(txt)
print(f"JSON valid, {len(txt)} bytes")
print(f"Em-dashes remaining: {txt.count(chr(0x2014))}")
print(f"En-dashes remaining: {txt.count(chr(0x2013))}")
