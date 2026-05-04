import json

d = json.load(open('Vendor 6-0 AI Researched.json', encoding='utf-8'))
blumira = [v for v in d['vendors'] if 'blumira' in v.get('vendor','').lower()]
print(f"DFIR 6-0: {len(d['vendors'])} vendors, Blumira found: {len(blumira)}, keys: {len(blumira[0]) if blumira else 0}")

d2 = json.load(open('Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json', encoding='utf-8'))
b2 = [v for v in d2 if 'blumira' in v.get('vendor','').lower()]
print(f"PreCyber 3-0: {len(d2)} vendors, Blumira found: {len(b2)}, keys: {len(b2[0]) if b2 else 0}")
