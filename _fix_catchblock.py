lines = open('static/app.js', encoding='utf-8').readlines()
# Line 27218 (0-indexed 27217) is broken:
# It has the innerHTML template literal start concatenated with the renderPanel comment.
# Fix: replace with proper catch block close + renderPanel comment
old = lines[27217]
assert 'style="color:    //' in old, f"Unexpected content: {repr(old[:100])}"

new_line = (
    '            bodyEl.innerHTML = `<div class="docs-panel-loading" style="color:#e74c3c">'
    'Failed to load: ${escapeHtml(err.message)}</div>`;\n'
    '        }\n'
    '    }\n'
    '\n'
    '    // Render panel: left nav + wrapped top tabs, one pane per section\n'
)
lines[27217] = new_line
open('static/app.js', 'w', encoding='utf-8').writelines(lines)
print('Fixed. Lines:', len(open('static/app.js', encoding='utf-8').readlines()))
