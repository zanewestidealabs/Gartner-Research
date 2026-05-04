"""Create a Smart Brevity trimmed v2 of the AIUC-1 Analyst Take (~200 words cut)."""
import json, copy

with open('analyst_take_reports.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

original = data['reports'][1]
trimmed = copy.deepcopy(original)

trimmed['id'] = 'aiuc1-agentic-compliance-v2'
trimmed['label'] = 'Analyst Take - AIUC-1: Smart Brevity Edit (v2)'
trimmed['title'] = original['title']  # same title
trimmed['subtitle'] = 'Smart brevity edit. Strips inline control IDs from body narrative, tightens prose. Positioning statements retain full detail.'

# --- TRIMMED BODY SECTIONS ---

# Section 0: 168 -> ~148  (cut ~20)
trimmed['body_sections'][0]['body'] = (
    "I've spent the last year evaluating over 80 vendors building AI-powered "
    "products and SaaS platforms, scoring them against a maturity framework that "
    "maps to every major compliance standard CISOs care about. The uncomfortable "
    "truth: organizations that are SOC 2 Type II certified, HIPAA-compliant, and "
    "PCI DSS Level 1 validated are simultaneously running AI agents that no "
    "existing audit has ever examined.\n\n"
    "This isn't theoretical. These AI agents are querying databases, making API "
    "calls, generating recommendations, and taking autonomous actions on data those "
    "compliance frameworks are supposed to protect. SOC 2 audits your infrastructure. "
    "HIPAA audits your PHI safeguards. PCI audits your cardholder data environment. "
    "None of them audit what happens when an AI agent chains together three tool calls "
    "and generates output from data it was never explicitly told to access.\n\n"
    "This is the gap AIUC-1 was built to close."
)

# Section 1: 250 -> ~185  (cut ~65 - biggest win, strip all Category X labels)
trimmed['body_sections'][1]['body'] = (
    "AIUC-1 is not a replacement for SOC 2, HIPAA, or PCI DSS. It's the missing "
    "layer on top. Where traditional frameworks govern the container (the infrastructure, "
    "the access controls, the network boundaries), AIUC-1 governs what the AI inside "
    "that container actually does.\n\n"
    "It introduces controls across six categories with no equivalent in traditional "
    "compliance. Data & Privacy asks whether the AI agent limits data collection to "
    "what's necessary, whether it can expose one customer's data to another, and "
    "whether it respects IP boundaries. Security addresses adversarial inputs and "
    "endpoint scraping. Safety mandates testing for harmful outputs and out-of-scope "
    "behaviors. Reliability tackles hallucination prevention, hallucination testing, "
    "and tool call safety. When an AI agent invokes an external API, are there "
    "restrictions on unsafe calls? Is that behavior tested by a third party? No "
    "existing framework asks these questions.\n\n"
    "Accountability is where AIUC-1 addresses transparency head-on: logging all model "
    "activity, mandating AI disclosure to users, and defining what I'd describe as an "
    "AI audit knowledge graph. A persistent, queryable structure that traces every AI "
    "decision from input context through reasoning to output action."
)

# Section 2: 235 -> ~195  (cut ~40)
trimmed['body_sections'][2]['body'] = (
    "Let me make this concrete with the industry where this gap is most dangerous: "
    "healthcare.\n\n"
    "A mid-size health system adopts an AI-powered clinical decision support platform. "
    "The vendor has SOC 2 Type II. They'll sign a HIPAA BAA. The platform's AI agents "
    "access EHR data, cross-reference drug interactions, and generate recommendations "
    "for clinicians. The question no one is asking: when that AI agent pulls a patient "
    "record, what reasoning led it to do so? If it generates an incorrect drug "
    "interaction alert based on hallucinated data, can anyone reconstruct why?\n\n"
    "The answer today is no. HIPAA was written for a world where humans access data "
    "through applications with defined workflows. AI agents don't follow workflows; "
    "they reason, plan, and act. The only way to audit that reasoning is through a "
    "knowledge graph that captures the full chain of agent perception, planning, "
    "tool invocation, and output.\n\n"
    "AIUC-1 is the first compliance framework to require this infrastructure. It's "
    "not just healthcare; any vertical where AI agents touch regulated data faces "
    "the same black box problem. But healthcare is where the consequences are "
    "measured in patient safety, not just dollars."
)

# Section 3: 204 -> ~155  (cut ~49)
trimmed['body_sections'][3]['body'] = (
    "Here's what makes AIUC-1 different from yet another compliance framework that "
    "only large enterprises can implement: 78.6% of its requirements are mandatory "
    "obligations on the AI vendor, not the customer.\n\n"
    "Think about what this means for a 200-person company buying AI-powered software. "
    "SOC 2, HIPAA, and PCI DSS all create compliance overhead that scales poorly for "
    "smaller organizations. AIUC-1 flips this. Its third-party testing mandates "
    "(adversarial robustness, harmful output testing, hallucination testing, tool call "
    "testing) are vendor obligations that produce standardized artifacts. A small clinic "
    "can ask 'show me your test results' with exactly the same authority as a major "
    "health system.\n\n"
    "The A-through-F coverage grading collapses 40 sub-pillars of technical maturity "
    "into a letter grade that fits in a procurement spreadsheet. That's not dumbing it "
    "down; it's making AI governance accessible to the organizations that need it most."
)

# Section 4: 231 -> ~195  (cut ~36)
trimmed['body_sections'][4]['body'] = (
    "Whether you're a 50-person clinic or a Fortune 500 health system, the starting "
    "point is the same:\n\n"
    "First, audit your audit. Pull your latest SOC 2 Type II report and your HIPAA "
    "risk assessment. Search for any mention of AI agents, model behavior, hallucination "
    "testing, or tool call safety. You won't find it. Document this gap; it's the "
    "business case for AIUC-1 adoption.\n\n"
    "Second, add one question to every AI vendor evaluation: 'Can you provide AIUC-1 "
    "compliance evidence or equivalent AI-specific certification for the AI agents "
    "that will access our data?'\n\n"
    "Third, run a 10-case pilot audit. This is the action that will differentiate "
    "leaders from followers. Pick 10 random actions your current AI tools have taken "
    "in the last 30 days. Try to reconstruct the full reasoning chain: what triggered "
    "the action, what data was accessed, what tools were invoked, and why the AI "
    "produced the output it did. I predict you'll reconstruct less than 20% of that "
    "chain. That gap is your knowledge-graph business case.\n\n"
    "The window between 'AIUC-1 is emerging' and 'AIUC-1 is required' is measured "
    "in quarters, not years."
)

data['reports'].append(trimmed)

with open('analyst_take_reports.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Verify
with open('analyst_take_reports.json', 'r', encoding='utf-8') as f:
    d2 = json.load(f)

print(f"Reports: {len(d2['reports'])}")
for r in d2['reports']:
    wc = sum(len(s['body'].split()) for s in r.get('body_sections', []))
    print(f"  {r['id']}: {wc} words")

orig_wc = sum(len(s['body'].split()) for s in d2['reports'][1]['body_sections'])
trim_wc = sum(len(s['body'].split()) for s in d2['reports'][2]['body_sections'])
print(f"\nCut: {orig_wc - trim_wc} words ({orig_wc} -> {trim_wc})")
print(f"Em-dashes: {open('analyst_take_reports.json','r',encoding='utf-8').read().count(chr(0x2014))}")
