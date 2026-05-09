src = open('static/app.js', encoding='utf-8').read()
i = src.find("getElementById('docs-panel-body')")
nl = src.rfind('\n', 0, i) + 1
line = src[nl:src.find('\n', i)]
print(repr(line))
