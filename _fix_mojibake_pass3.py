"""Fix the last 2 mojibake remnants ftfy mangled."""
SRC = 'static/app.js'
with open(SRC, 'r', encoding='utf-8') as f:
    t = f.read()

# 1) "Detail â—'" should be "Detail ◂" (left-pointing small triangle)
old1 = "'Detail \u00e2\u2014\u0027'"   # 'Detail â—''
new1 = "'Detail \u25c2'"               # 'Detail ◂'
print('pat1 count:', t.count(old1))
t = t.replace(old1, new1)

# 2) 'âš"' should be '⚔' (crossed swords) for "Offensive (Threat Actors)"
# Original triple was â š " which decodes from cp1252 bytes E2 9A 94 = U+2694 ⚔
old2 = '\u00e2\u0161"'                  # â š "
new2 = '\u2694'                         # ⚔
print('pat2 count:', t.count(old2))
t = t.replace(old2, new2)

with open(SRC, 'w', encoding='utf-8', newline='\n') as f:
    f.write(t)
print('done')
