"""Fix mojibake in static/app.js using ftfy. Backs up original first."""
import shutil, ftfy, sys

SRC = 'static/app.js'
BAK = 'static/app.js.bak_mojibake'

with open(SRC, 'r', encoding='utf-8') as f:
    text = f.read()

print(f'Original length: {len(text)} chars')

# Counts before
samples = ['â€"', 'â€"', 'ðŸ', 'â€', 'â€"']
for s in samples:
    print(f'  {s!r}: {text.count(s)}')

fixed = ftfy.fix_text(text)
print(f'Fixed length:    {len(fixed)} chars')

# Counts after
for s in samples:
    print(f'  {s!r}: {fixed.count(s)}')

if fixed == text:
    print('No changes.')
    sys.exit(0)

shutil.copy2(SRC, BAK)
with open(SRC, 'w', encoding='utf-8', newline='\n') as f:
    f.write(fixed)
print(f'Wrote fixed file. Backup at {BAK}')
