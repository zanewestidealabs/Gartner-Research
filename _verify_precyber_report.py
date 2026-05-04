"""Verify PreCyber Market Insight report integration."""
import json

# Verify the precyber report JSON is valid
with open('precyber_market_insight_reports.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
reports = data.get('reports', [])
print(f'PreCyber reports: {len(reports)}')
for r in reports:
    rid = r.get('id', '?')
    label = r.get('label', '?')
    title = r.get('title', '?')[:60]
    findings = len(r.get('findings', []))
    recs = len(r.get('recommendations', []))
    analysis = len(r.get('analysis_sections', []))
    glossary = len(r.get('glossary', []))
    evidence = len(r.get('evidence', []))
    spa = r.get('spa', '')[:60]
    print(f'  ID: {rid}')
    print(f'  Label: {label}')
    print(f'  Title: {title}...')
    print(f'  Findings={findings}, Recs={recs}, Analysis={analysis}, Glossary={glossary}, Evidence={evidence}')
    print(f'  SPA: {spa}...')
    print()

# Verify app.py routes exist
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()
assert '/api/precyber-market-insight/perspectives' in content
assert '/api/precyber-market-insight' in content
print('app.py routes: OK')

# Verify index.html tab and panel exist
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()
assert 'precyber-market-insight' in content
assert 'pci-title' in content
assert 'pci-perspective-select' in content
print('index.html tab+panel: OK')

# Verify app.js has the new function
with open('static/app.js', 'r', encoding='utf-8') as f:
    content = f.read()
assert 'populatePreCyberMarketInsight' in content
assert '_pciCurrentPerspective' in content
assert '_pciRenderExecSummary' in content
print('static/app.js functions: OK')
print()
print('All verification checks passed!')
