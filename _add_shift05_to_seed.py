"""Add SHIFT-05 entries to CNAPP Vendor 1-0 Seed.json so v1.1 schema iterates 29 sub-pillars."""
import json, re
from pathlib import Path

p = Path("CNAPP Vendor 1-0 Seed.json")
txt = p.read_text(encoding="utf-8")

# Pattern A: id list arrays
list_pat = re.compile(r'("SHIFT-01", "SHIFT-02", "SHIFT-03", "SHIFT-04",)')
def list_repl(m):
    line = m.group(1)
    if 'SHIFT-05' in line:
        return line
    return line + ' "SHIFT-05",'
txt = list_pat.sub(list_repl, txt)

# Pattern B: score dicts
score_pat = re.compile(r'("SHIFT-01": 0, "SHIFT-02": 0, "SHIFT-03": 0, "SHIFT-04": 0,)')
def score_repl(m):
    line = m.group(1)
    if 'SHIFT-05' in line:
        return line
    return line + ' "SHIFT-05": 0,'
txt = score_pat.sub(score_repl, txt)

p.write_text(txt, encoding="utf-8")

d = json.loads(txt)
print(f"Vendors: {len(d['vendors'])}")
v0 = d["vendors"][0]
print(f"v0 sub_pillars_pending tail: {v0['sub_pillars_pending'][-6:]}")
print(f"v0 scores has SHIFT-05: {'SHIFT-05' in v0.get('sub_pillar_scores_current', {})}")
print(f"Total SHIFT-05 occurrences in file: {txt.count('SHIFT-05')}")
