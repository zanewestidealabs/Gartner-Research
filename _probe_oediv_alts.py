"""Probe Wayback availability + DuckDuckGo HTML for OEDIV SecuRisk evidence."""
import urllib.request, urllib.parse, json, re, sys

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'

WAYBACK_TARGETS = [
    'oediv-securisk.de',
    'www.oediv-securisk.de',
    'www.oediv-securisk.de/leistungen/',
    'www.oediv-securisk.de/leistungen/managed-security-services/',
    'www.oediv-securisk.de/leistungen/security-operations-center/',
    'www.oediv-securisk.de/leistungen/incident-response/',
    'www.oediv-securisk.de/leistungen/managed-detection-and-response/',
    'www.oediv-securisk.de/unternehmen/',
    'www.oediv-securisk.de/loesungen/',
    'www.oediv-securisk.de/services/',
    'www.oediv-securisk.de/en/',
    'oediv.de/securisk',
    'www.oediv.de/securisk',
    'www.oediv.de/de/loesungen/cyber-security/security-operations-center/',
]

print('=== WAYBACK AVAILABILITY ===')
for host in WAYBACK_TARGETS:
    api = 'https://archive.org/wayback/available?url=' + urllib.parse.quote(host)
    try:
        req = urllib.request.Request(api, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        snap = data.get('archived_snapshots', {}).get('closest', {})
        ts = snap.get('timestamp', '-')
        u = snap.get('url', '-')
        print(f'  {host}\n      ts={ts}  {u}')
    except Exception as e:
        print(f'  {host}  ERR {e}')

print('\n=== DUCKDUCKGO HTML SEARCH ===')
queries = [
    '"OEDIV SecuRisk" SOC',
    '"OEDIV SecuRisk" managed detection response',
    '"OEDIV" "SOC" Bielefeld',
    'OEDIV SecuRisk managed security services',
    'site:linkedin.com OEDIV SecuRisk',
]
for q in queries:
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(q)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode('utf-8', errors='ignore')
        # Pull result URLs
        links = re.findall(r'class="result__a"[^>]*href="([^"]+)"', html)
        # Decode duckduckgo redirects
        clean = []
        for l in links[:10]:
            m = re.search(r'uddg=([^&]+)', l)
            if m:
                clean.append(urllib.parse.unquote(m.group(1)))
            else:
                clean.append(l)
        print(f'\n  Q: {q}  ({len(clean)} hits)')
        for c in clean:
            print('    ', c[:140])
    except Exception as e:
        print(f'  Q: {q}  ERR {e}')
