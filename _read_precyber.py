import json
with open('precyber_market_insight_reports.json', 'r', encoding='utf-8') as fh:
    data = json.load(fh)
for r in data['reports']:
    rid = r['id']
    print(f"\n{'='*80}")
    print(f"ID: {rid}")
    print(f"Label: {r['label']}")
    print(f"Title: {r['title']}")
    print(f"SPA: {r.get('spa','N/A')[:300]}")
    print(f"Summary: {r['summary'][:300]}")
    print(f"\nFindings ({len(r.get('findings',[]))}):")
    for i,f_ in enumerate(r.get('findings',[])):
        print(f"  [{i+1}] {f_['header']}")
        print(f"      {f_['body'][:300]}")
    print(f"\nRecommendations ({len(r.get('recommendations',[]))}):")
    for i,rec in enumerate(r.get('recommendations',[])):
        print(f"  [{i+1}] {rec['header']}")
        print(f"      {rec['body'][:250]}")
