"""Check for remaining hardcoded stat values in the two PreCyber PPTX routes."""
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

infographic_start = content.find('def precyber_infographic_pptx')
infographic_end = content.find('\n@app.route', infographic_start + 100)
all_graphics_start = content.find('def precyber_all_graphics_pptx')
all_graphics_end = content.find('\n@app.route', all_graphics_start + 100)

suspicious_vals = {'27%','22%','29%','49%','92%','86%','78%','57%','55%','73%','45%','35%','37%','51','14','15','11','25','19','18'}

for name, body in [('infographic', content[infographic_start:infographic_end]),
                   ('all_graphics', content[all_graphics_start:all_graphics_end])]:
    pattern = r"'([0-9]+%?)'"
    found = set(re.findall(pattern, body))
    hits = found & suspicious_vals
    if hits:
        print(f'{name}: possibly hardcoded: {hits}')
        # Show context
        for h in hits:
            for m in re.finditer(r"'" + re.escape(h) + r"'", body):
                line_start = body.rfind('\n', 0, m.start()) + 1
                line_end = body.find('\n', m.end())
                print(f'  LINE: {body[line_start:line_end].strip()}')
    else:
        print(f'{name}: clean - no hardcoded stats found')
