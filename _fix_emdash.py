"""Remove em dashes from condensed_analysis and condensed_notes sections."""
import json

path = "Reports/846698_market_insight.json"
with open(path, "r", encoding="utf-8") as f:
    d = json.load(f)

count = 0

for s in d["sections"]:
    if s["id"] not in ("condensed_analysis", "condensed_notes"):
        continue

    # Handle subsections (condensed_analysis)
    for sub in s.get("subsections", []):
        for i, p in enumerate(sub.get("paragraphs", [])):
            if "\u2014" in p:
                old = p
                # Apply contextual replacements
                p = p.replace("purpose\u2014SHAP", "purpose, SHAP")
                p = p.replace("follow\u2014memory dump triggers, artifact searches\u2014providing", "follow, such as memory dump triggers and artifact searches, providing")
                p = p.replace("attribution\u2014identifying", "attribution, identifying")
                p = p.replace("timelines\u2014both the collection process and the evidence itself\u2014at", "timelines, both the collection process and the evidence itself, at")
                p = p.replace('Daubert and Federal Rule 901\u2014govern', "Daubert and Federal Rule 901, govern")
                p = p.replace("path\u2014forensics", "path: forensics")
                p = p.replace("elements\u2014planning, program management, compliance support\u2014rather", "elements, such as planning, program management, and compliance support, rather")
                p = p.replace('"black box"\u2014no', '"black box," with no')
                # Catch any remaining
                p = p.replace("\u2014", ", ")
                if p != old:
                    sub["paragraphs"][i] = p
                    count += 1

    # Handle methodology field
    if "methodology" in s and "\u2014" in s["methodology"]:
        s["methodology"] = s["methodology"].replace("\u2014", ", ")
        count += 1

    # Handle notes (condensed_notes)
    for note in s.get("notes", []):
        for i, p in enumerate(note.get("paragraphs", [])):
            if "\u2014" in p:
                old = p
                p = p.replace("area\u2014containment, recovery, and remediation (3.72)\u2014is", "area, containment, recovery, and remediation (3.72), is")
                p = p.replace("area\u2014containment, recovery, and remediation\u2014is", "area, containment, recovery, and remediation, is")
                p = p.replace("(+0.59)\u2014the activities", "(+0.59). These are the activities")
                p = p.replace("(+0.59)\u2014high-skill", "(+0.59). These are high-skill")
                p = p.replace("component\u2014a tool", "component, a tool")
                p = p.replace("(0.13 points)\u2014areas", "(0.13 points). These are areas")
                p = p.replace("carry weight\u2014areas", "carry weight. These are areas")
                p = p.replace("metrics\u2014specialized", "metrics: specialized")
                p = p.replace("carry significant value\u2014areas", "carry significant value. These are areas")
                p = p.replace("carry significant weight\u2014areas", "carry significant weight. These are areas")
                p = p.replace("Their weakest\u2014containment", "Their weakest area, containment")
                p = p.replace('"black box"\u2014no', '"black box," with no')
                # process-driven functions
                p = p.replace("3.59)\u2014process-driven", "3.59). These are process-driven")
                # Catch any remaining
                p = p.replace("\u2014", ", ")
                if p != old:
                    note["paragraphs"][i] = p
                    count += 1

with open(path, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f"Fixed {count} paragraphs with em dashes in JSON.")

# Now fix the markdown file too
md_path = "846698_Market_Insight_v1.md"
with open(md_path, "r", encoding="utf-8") as f:
    md = f.read()

# Find the condensed sections and replace em dashes only in them
lines = md.split("\n")
in_condensed = False
md_count = 0
for i, line in enumerate(lines):
    if line.startswith("## Condensed Analysis") or line.startswith("## Condensed Notes"):
        in_condensed = True
        continue
    if line.startswith("## ") and not line.startswith("## Condensed"):
        in_condensed = False
        continue
    if in_condensed and "\u2014" in line:
        old_line = line
        # Apply same contextual replacements
        line = line.replace("purpose\u2014SHAP", "purpose, SHAP")
        line = line.replace("follow\u2014memory dump triggers, artifact searches\u2014providing", "follow, such as memory dump triggers and artifact searches, providing")
        line = line.replace("attribution\u2014identifying", "attribution, identifying")
        line = line.replace("timelines\u2014both the collection process and the evidence itself\u2014at", "timelines, both the collection process and the evidence itself, at")
        line = line.replace("Daubert and Federal Rule 901\u2014govern", "Daubert and Federal Rule 901, govern")
        line = line.replace("path\u2014forensics", "path: forensics")
        line = line.replace("elements\u2014planning, program management, compliance support\u2014rather", "elements, such as planning, program management, and compliance support, rather")
        line = line.replace('"black box"\u2014no', '"black box," with no')
        line = line.replace("area\u2014containment, recovery, and remediation (3.72)\u2014is", "area, containment, recovery, and remediation (3.72), is")
        line = line.replace("area\u2014containment, recovery, and remediation\u2014is", "area, containment, recovery, and remediation, is")
        line = line.replace("(+0.59)\u2014the activities", "(+0.59). These are the activities")
        line = line.replace("(+0.59)\u2014high-skill", "(+0.59). These are high-skill")
        line = line.replace("component\u2014a tool", "component, a tool")
        line = line.replace("(0.13 points)\u2014areas", "(0.13 points). These are areas")
        line = line.replace("carry weight\u2014areas", "carry weight. These are areas")
        line = line.replace("metrics\u2014specialized", "metrics: specialized")
        line = line.replace("carry significant value\u2014areas", "carry significant value. These are areas")
        line = line.replace("carry significant weight\u2014areas", "carry significant weight. These are areas")
        line = line.replace("Their weakest\u2014containment", "Their weakest area, containment")
        line = line.replace("3.59)\u2014process-driven", "3.59). These are process-driven")
        line = line.replace("\u2014", ", ")
        if line != old_line:
            lines[i] = line
            md_count += 1

with open(md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Fixed {md_count} lines with em dashes in markdown.")
