"""Fix remaining triple-encoded mojibake patterns in static/app.js.
Each remaining pattern is a U+2xxx symbol whose 3 utf-8 bytes were each
mis-read as cp1252 then re-saved as utf-8. We detect and decode them.
"""
import re

SRC = 'static/app.js'

with open(SRC, 'r', encoding='utf-8') as f:
    text = f.read()

# Build inverse cp1252 lookup: char -> cp1252 byte
inv = {}
for b in range(256):
    try:
        c = bytes([b]).decode('cp1252')
        inv[c] = b
    except UnicodeDecodeError:
        pass

# Pattern: 3 chars where each chr is in cp1252 (single byte each).
# When the original was a 3-byte utf-8 sequence (E2 xx xx for U+2xxx symbols),
# the first byte E2 always decodes in cp1252 to "â" (U+00E2).
# So: scan for "â" followed by 2 chars all in cp1252.
def fix_triple(match):
    s = match.group(0)
    try:
        b1 = inv[s[0]]
        b2 = inv[s[1]]
        b3 = inv[s[2]]
        decoded = bytes([b1, b2, b3]).decode('utf-8')
        return decoded
    except (KeyError, UnicodeDecodeError):
        return s

# Scan: â followed by 2 cp1252-encodable chars
# Greedy heuristic: only fix if result is a printable BMP symbol char
def try_fix(s):
    try:
        b1 = inv[s[0]]; b2 = inv[s[1]]; b3 = inv[s[2]]
        d = bytes([b1, b2, b3]).decode('utf-8')
        if len(d) == 1 and 0x2000 <= ord(d) <= 0x2FFF or 0x25A0 <= ord(d) <= 0x27BF:
            return d
    except Exception:
        pass
    return None

out = []
i = 0
n = len(text)
fixed_count = 0
while i < n:
    if text[i] == 'â' and i + 2 < n:
        cand = try_fix(text[i:i+3])
        if cand:
            out.append(cand)
            i += 3
            fixed_count += 1
            continue
    out.append(text[i])
    i += 1

new_text = ''.join(out)
print(f'Fixed {fixed_count} triple-mojibake sequences')
print(f'Length: {len(text)} -> {len(new_text)}')

# Sanity-check no more â-patterns remain
remaining = re.findall(r'â[\u0080-\u00ff\u0100-\u30ff]{1,2}', new_text)
print(f'Remaining suspicious patterns: {len(remaining)}')
from collections import Counter
print(Counter(remaining).most_common(5))

if new_text != text:
    with open(SRC, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_text)
    print('Wrote fixed file')
