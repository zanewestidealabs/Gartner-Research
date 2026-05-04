"""Clean AI'isms (em-dashes, en-dashes, AI vocabulary) from AIUC-1 Analyst Take report."""
import json, re

with open('analyst_take_reports.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

report = data['reports'][1]

def clean_text(s):
    if not isinstance(s, str):
        return s

    # 1) En-dashes -> hyphens (ranges like 400-900, A-F)
    s = s.replace('\u2013', '-')

    # 2) Handle paired em-dashes (parenthetical asides)
    def fix_paired(m):
        before = m.group(1)
        aside = m.group(2).strip()
        after = m.group(3)
        return before + ' (' + aside + ') ' + after
    s = re.sub(r'(\S) \u2014 ([^\u2014]{3,120}?) \u2014 (\S)', fix_paired, s)

    # 3) Em-dash before conjunctions -> comma
    s = re.sub(r' \u2014 (and |but |or |so |yet |not )', r', \1', s)

    # 4) Em-dash mid-sentence -> period + capitalize
    def emdash_to_period(m):
        before = m.group(1)
        after = m.group(2)
        if after and after[0].islower():
            after = after[0].upper() + after[1:]
        return before + '. ' + after
    s = re.sub(r'([a-z]) \u2014 ([A-Za-z])', emdash_to_period, s)

    # 5) Remaining em-dashes before text -> period + capitalize
    def final_emdash(m):
        after = m.group(1)
        if after and after[0].islower():
            after = after[0].upper() + after[1:]
        return '. ' + after
    s = re.sub(r' \u2014 ([A-Za-z\'"])', final_emdash, s)

    # 6) Any leftover em-dashes in labels/titles
    s = s.replace(' \u2014 ', ': ')
    s = s.replace('\u2014', '-')

    # 7) Fix "unprecedented" 
    s = s.replace('an unprecedented compliance gap', 'a compliance gap that no existing framework addresses')
    s = s.replace('unprecedented', 'significant')

    # 8) Clean up double spaces
    s = re.sub(r'  +', ' ', s)

    # 9) Fix ". ." or ":." patterns
    s = s.replace('. .', '.')
    s = s.replace(':.', ':')

    return s

def clean_obj(obj):
    if isinstance(obj, str):
        return clean_text(obj)
    elif isinstance(obj, list):
        return [clean_obj(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: clean_obj(v) for k, v in obj.items()}
    return obj

data['reports'][1] = clean_obj(report)

with open('analyst_take_reports.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Verify
with open('analyst_take_reports.json', 'r', encoding='utf-8') as f:
    txt = f.read()
em = txt.count('\u2014')
en = txt.count('\u2013')
print(f'Remaining em-dashes: {em} (should be ~6 from template)')
print(f'Remaining en-dashes: {en} (should be ~4 from template)')
json.loads(txt)
print('JSON valid: OK')
print(f'File size: {len(txt)} bytes')
