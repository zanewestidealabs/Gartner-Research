import re
src = open('static/app.js', encoding='utf-8').read()
rp = re.search(r'    // .{0,50}Render panel.{0,80}\n    function renderPanel', src)
rb = re.search(r'\n    // .{0,50}Render a content block.{0,80}\n    function renderBlock', src)
print('renderPanel match:', repr(rp.group()[:80]) if rp else 'NOT FOUND')
print('renderBlock match:', repr(rb.group()[:80]) if rb else 'NOT FOUND')
m = re.search(r'    const bodyEl\s*=\s*document\.getElementById\(.*panel-body.*\);', src)
print('bodyEl line:', repr(m.group()) if m else 'NOT FOUND')
