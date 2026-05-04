"""Fix all SbD-AI v2 schema references in the v2 Analyst Take entry.
Replace with AIUC-1-only language per user directive."""

import json, copy

with open("analyst_take_reports.json", "r", encoding="utf-8") as f:
    data = json.load(f)

r = data["reports"][2]  # v2 entry
assert r["id"] == "aiuc1-agentic-compliance-v2", f"Wrong entry: {r['id']}"

ps = r["positioning_statements"]
ps0 = ps[0]  # healthcare
ps1 = ps[1]  # smb
ps2 = ps[2]  # knowledge-graph

# ── PS0 (Healthcare) ──────────────────────────────────────────────────

# PS0 justification.evidence: remove "These map to the TRM and REL pillars of the SbD-AI v2 framework"
old = ps0["justification"]["evidence"]
ps0["justification"]["evidence"] = old.replace(
    "These map to the TRM and REL pillars of the SbD-AI v2 framework, requiring",
    "These are AIUC-1-specific controls with no equivalent in SOC 2 or HIPAA, requiring"
)

# PS0 actions[1].whyNonObvious: remove DSO-05
old = ps0["actions"][1]["whyNonObvious"]
ps0["actions"][1]["whyNonObvious"] = old.replace(
    "AIUC-1's E015 (activity logging) and DSO-05 (lineage graph) formalize this as an auditable artifact.",
    "AIUC-1's E015 (activity logging) requirement formalizes the lineage graph as an auditable artifact."
)

# PS0 alignment.justificationSources: remove SbD-AI v2
ps0["alignment"]["justificationSources"] = (
    "AIUC-1 Standard (Categories A, C, D, E); NIST AI RMF 1.0 (Measure function); HIPAA Security Rule \u00a7164.312"
)

# ── PS1 (SMB) ─────────────────────────────────────────────────────────

# PS1 justification.evidence: remove SbD-AI v2 coverage grading
old = ps1["justification"]["evidence"]
ps1["justification"]["evidence"] = old.replace(
    "The SbD-AI v2 framework's coverage grading system (A through F) further simplifies this into a purchasable signal.",
    "AIUC-1 certification further simplifies this into a binary procurement signal: the vendor either passes third-party testing or it doesn't."
)

# PS1 actions[1]: replace SbD-AI v2 coverage grade action
ps1["actions"][1]["action"] = (
    "Require AIUC-1 compliance evidence for any AI-powered SaaS platform that accesses regulated data. "
    "Prioritizing vendors that can demonstrate third-party testing results for mandatory requirements."
)
ps1["actions"][1]["whyNonObvious"] = (
    "Most procurement teams lack the expertise to evaluate AI-specific technical controls. "
    "AIUC-1's vendor-side certification model produces standardized test artifacts that require no specialized knowledge to interpret."
)
ps1["actions"][1]["outcome"] = (
    "SMBs can make informed AI vendor selection decisions using the same third-party testing evidence that large enterprises require."
)

# PS1 alignment.actionsToRecs[1]
ps1["alignment"]["actionsToRecs"][1] = (
    "Action 2 \u2192 Recommendation: AIUC-1 compliance evidence as procurement requirement"
)

# PS1 alignment.justificationSources: remove SbD-AI v2 Coverage Grade Scale
ps1["alignment"]["justificationSources"] = (
    "AIUC-1 Standard (vendor-side certification model); AIUC-1 Categories A, D mandatory requirements"
)

# ── PS2 (Knowledge Graph) ─────────────────────────────────────────────

# PS2 positionComponents.judgment: remove DSO-05 and TRM-05 codes
old = ps2["positionComponents"]["judgment"]
ps2["positionComponents"]["judgment"] = old.replace(
    "model activity logging (E015), lineage tracking (DSO-05), and accountability graphs (TRM-05)",
    "model activity logging (E015), lineage tracking, and accountability graphs"
)

# PS2 justification.evidence: replace DSO-05 and TRM-05 references
old = ps2["justification"]["evidence"]
# First replacement: the three-control paragraph
old = old.replace(
    "E015 (model activity logging) requires capturing all inference requests and responses; "
    "DSO-05 (auditability and lineage graph) mandates tracing the code \u2192 data \u2192 model \u2192 decision \u2192 outcome chain; "
    "and TRM-05 (lineage and accountability graph) requires a queryable structure that maps model decisions to their data inputs, tool calls, and responsible owners.",
    "E015 (model activity logging) requires capturing all inference requests and responses. "
    "The standard further mandates tracing the full chain from code to data to model to decision to outcome through auditability and lineage requirements, "
    "and requires a queryable structure that maps model decisions to their data inputs, tool calls, and responsible owners."
)
# Second replacement: SbD-AI v2 REL-02 sentence
old = old.replace(
    "The SbD-AI v2 framework further reinforces this through REL-02 (tool call safety) requiring",
    "AIUC-1 further reinforces this through D003 (restrict unsafe tool calls), requiring"
)
ps2["justification"]["evidence"] = old

# PS2 alignment.justificationSources
ps2["alignment"]["justificationSources"] = (
    "AIUC-1 Requirements E015, D003, B006; NIST AI RMF Measure Function"
)

# ── Body Section 3 (Attainability) ────────────────────────────────────

body3 = r["body_sections"][3]["body"]
r["body_sections"][3]["body"] = body3.replace(
    "The A-through-F coverage grading collapses 40 sub-pillars of technical maturity into a letter grade that fits in a procurement spreadsheet. "
    "That's not dumbing it down; it's making AI governance accessible to the organizations that need it most.",
    "AIUC-1 certification works as a binary procurement signal: a vendor either passes third-party testing or it doesn't. "
    "That simplicity is the point; it makes AI governance accessible to the organizations that need it most."
)

# ── Recommended Reading [0] ───────────────────────────────────────────
# Keep the entry (it's a valid recommended reading) but update relevance
r["recommended_reading"][0]["relevance"] = (
    "The companion maturity assessment framework with full AIUC-1 requirement crosswalk. "
    "Useful for organizations seeking detailed technical evaluation beyond binary certification."
)

# ── Notes ─────────────────────────────────────────────────────────────
old_notes = r["notes"]
r["notes"] = old_notes.replace(
    "All AIUC-1 requirement references (e.g. D001, E015, B006) map to the SbD-AI v2 schema crosswalk.",
    "All requirement references follow the AIUC-1 standard's numbering scheme (e.g. D001, E015, B006) across six categories (A through F)."
)

# ── Guidance: cutting_room_floor ──────────────────────────────────────
old_crf = r["guidance"]["ideation_prompts"]["cutting_room_floor"]
r["guidance"]["ideation_prompts"]["cutting_room_floor"] = old_crf.replace(
    "The detailed AIUC-1 crosswalk analysis from the SbD-AI v2 schema development, covering all 42 active requirements across 7 pillars.",
    "The detailed AIUC-1 requirement analysis covering all 42 active requirements across 6 categories."
)

# ── Verify no remaining SbD-AI v2 refs in body text ──────────────────
dumped = json.dumps(r, ensure_ascii=False)
checks = ["SbD-AI", "sub-pillar", "40 sub", "DSO-05", "TRM-05", "REL-02", "7 pillar"]
found = []
for term in checks:
    if term.lower() in dumped.lower():
        # Find context
        idx = dumped.lower().find(term.lower())
        ctx = dumped[max(0, idx-40):idx+len(term)+40]
        found.append(f"  [{term}] ...{ctx}...")

if found:
    print("WARNING: Remaining references found:")
    for f in found:
        print(f)
else:
    print("CLEAN: No SbD-AI v2 schema references remain.")

# ── Word count for body sections ──────────────────────────────────────
total = 0
for i, sec in enumerate(r["body_sections"]):
    wc = len(sec["body"].split())
    total += wc
    print(f"  S{i}: {wc} words")
print(f"  TOTAL: {total} words")

# ── Save ──────────────────────────────────────────────────────────────
with open("analyst_take_reports.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("\nDone. File saved.")
