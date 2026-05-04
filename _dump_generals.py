"""Dump the buyer-facing-general and cpo-product-strategy-general reports to separate text files for reading."""
import json

d = json.load(open('mdr_market_insight_reports.json', 'r', encoding='utf-8'))

for r in d['reports']:
    if r['id'] in ('buyer-facing-general', 'cpo-product-strategy-general'):
        fname = f"_dump_{r['id']}.txt"
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(f"ID: {r['id']}\n")
            f.write(f"LABEL: {r['label']}\n")
            f.write(f"TITLE: {r['title']}\n\n")
            f.write(f"SUMMARY:\n{r['summary']}\n\n")
            f.write(f"SPA:\n{r['spa']}\n\n")
            f.write(f"FINDINGS ({len(r['findings'])}):\n")
            for i, item in enumerate(r['findings']):
                f.write(f"\n  [{i}] HEADER: {item['header']}\n")
                f.write(f"  BODY: {item['body']}\n")
            f.write(f"\nRECOMMENDATIONS ({len(r['recommendations'])}):\n")
            for i, item in enumerate(r['recommendations']):
                f.write(f"\n  [{i}] HEADER: {item['header']}\n")
                f.write(f"  BODY: {item['body']}\n")
            f.write(f"\nANALYSIS SECTIONS ({len(r['analysis_sections'])}):\n")
            for i, item in enumerate(r['analysis_sections']):
                f.write(f"\n  [{i}] TITLE: {item['title']}\n")
                f.write(f"  BODY: {item['body']}\n")
            f.write(f"\nBACKGROUND:\n{r['background']}\n\n")
            f.write(f"IMPACT:\n{r['impact']}\n\n")
            f.write(f"CONCLUSION:\n{r['conclusion']}\n\n")
            f.write(f"GLOSSARY ({len(r.get('glossary', []))}):\n")
            for g in r.get('glossary', []):
                f.write(f"  {g['term']}: {g['definition']}\n")
            f.write(f"\nEVIDENCE ({len(r.get('evidence', []))}):\n")
            for e in r.get('evidence', []):
                f.write(f"  {e}\n")
        print(f"Wrote {fname}")

print("Done")
