import re

path = 'static/app.js'
with open(path, encoding='utf-8') as f:
    src = f.read()

# Find block_start: beginning of the comment line before renderPanel
i_rp = src.find('    function renderPanel(data) {')
assert i_rp > 0, 'renderPanel not found'
# Walk back past the function line's preceding newline to get comment line start
nl_before_func = src.rfind('\n', 0, i_rp - 1) + 1
block_start = nl_before_func

# Find block_end: beginning of the comment line before renderBlock
i_rb_comment = src.find('Render a content block')
assert i_rb_comment > 0, 'renderBlock comment not found'
nl_before_rb = src.rfind('\n', 0, i_rb_comment) + 1
block_end = nl_before_rb

print(f'Replacing chars {block_start}..{block_end} ({block_end - block_start} chars)')

new_block = '''    // ── Render panel: left nav + wrapped top tabs, one pane per section ──
    function renderPanel(data) {
        const sections = (data.tabs || []).flatMap(t => t.sections || []);
        if (!sections.length) { bodyEl.innerHTML = '<div class="docs-panel-loading">No content.</div>'; return; }

        // Left nav buttons
        if (navListEl) {
            navListEl.innerHTML = '';
            sections.forEach((sec, i) => {
                const btn = document.createElement('button');
                btn.className = 'docs-nav-btn' + (i === 0 ? ' active' : '');
                btn.dataset.sectId = sec.id;
                btn.textContent = sec.title;
                btn.title = sec.title;
                btn.addEventListener('click', () => switchSection(sec.id));
                navListEl.appendChild(btn);
            });
        }

        // Wrapped top tab pills
        tabsEl.innerHTML = '';
        sections.forEach((sec, i) => {
            const btn = document.createElement('button');
            btn.className = 'docs-tab-btn' + (i === 0 ? ' active' : '');
            btn.dataset.sectId = sec.id;
            btn.textContent = sec.title;
            btn.addEventListener('click', () => switchSection(sec.id));
            tabsEl.appendChild(btn);
        });

        // Content panes
        bodyEl.innerHTML = '';
        sections.forEach((sec, i) => {
            const pane = document.createElement('div');
            pane.className = 'docs-tab-content' + (i === 0 ? ' active' : '');
            pane.id = `docs-sec-${sec.id}`;
            const h2 = document.createElement('h2');
            h2.className = 'docs-section-title';
            h2.textContent = sec.title;
            pane.appendChild(h2);
            (sec.content || []).forEach(block => pane.appendChild(renderBlock(block)));
            bodyEl.appendChild(pane);
        });

        activeSect = sections[0].id;
        renderMermaidInPane(sections[0].id);
    }

    // ── Switch to a section ──────────────────────────────────────────────────
    function switchSection(sectId) {
        activeSect = sectId;
        // Update left nav (highlight + scroll into view)
        if (navListEl) {
            navListEl.querySelectorAll('.docs-nav-btn').forEach(b => {
                const isActive = b.dataset.sectId === sectId;
                b.classList.toggle('active', isActive);
                if (isActive) b.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            });
        }
        // Update tab pills
        tabsEl.querySelectorAll('.docs-tab-btn').forEach(b => b.classList.toggle('active', b.dataset.sectId === sectId));
        // Show content pane
        bodyEl.querySelectorAll('.docs-tab-content').forEach(p => p.classList.toggle('active', p.id === `docs-sec-${sectId}`));
        bodyEl.scrollTop = 0;
        renderMermaidInPane(sectId);
    }

'''

# Also update the variable declarations to add navListEl
old_vars = "    const panel     = document.getElementById('docs-panel');\n    const backdrop  = document.getElementById('docs-panel-backdrop');\n    const toggleBtn = document.getElementById('docs-panel-toggle');\n    const closeBtn  = document.getElementById('docs-panel-close');\n    const tabsEl    = document.getElementById('docs-tabs');\n    const bodyEl    = document.getElementById('docs-panel-body');"

new_vars = "    const panel      = document.getElementById('docs-panel');\n    const backdrop   = document.getElementById('docs-panel-backdrop');\n    const toggleBtn  = document.getElementById('docs-panel-toggle');\n    const closeBtn   = document.getElementById('docs-panel-close');\n    const tabsEl     = document.getElementById('docs-tabs');\n    const bodyEl     = document.getElementById('docs-panel-body');\n    const navListEl  = document.getElementById('docs-panel-nav-list');"

if old_vars in src:
    src = src.replace(old_vars, new_vars)
    print("Variables updated")
else:
    print("WARNING: Variable block not found as exact text, trying fuzzy...")
    # Try to find and replace around navListEl
    if 'navListEl' not in src:
        bodyEl_line = "    const bodyEl    = document.getElementById('docs-panel-body');"
        if bodyEl_line in src:
            src = src.replace(bodyEl_line, bodyEl_line + "\n    const navListEl = document.getElementById('docs-panel-nav-list');")
            print("navListEl added after bodyEl")

# Replace the renderPanel+switchSection block
src = src[:block_start] + new_block + src[block_end:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(src)

print(f"Done. File length: {len(src.splitlines())} lines")
# Verify
assert 'navListEl' in src
assert 'docs-nav-btn' in src
assert 'switchSection(sec.id)' in src
print("Assertions passed")
