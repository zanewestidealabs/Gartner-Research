"""APEF expansion v3 — fill in all missing 2026 models (Opus 4.6/4.7, Gemini 3.5, GPT-5.5, etc)."""
import json
from pathlib import Path

SCHEMA = Path('ai_platform_ecosystem_framework_v1.json')
data = json.loads(SCHEMA.read_text(encoding='utf-8-sig'))

ADDITIONS = {
    'anthropic': [
        {'id':'anthropic-claude-opus-46', 'name':'Claude Opus 4.6', 'layer':'L3','type':'foundation-model','integrates_with':['anthropic-api','aws-bedrock','gcp-vertex']},
        {'id':'anthropic-claude-opus-47', 'name':'Claude Opus 4.7', 'layer':'L3','type':'foundation-model','integrates_with':['anthropic-api','aws-bedrock','gcp-vertex']},
    ],
    'google': [
        {'id':'google-gemini-35-pro', 'name':'Gemini 3.5 Pro', 'layer':'L3','type':'foundation-model','integrates_with':['google-vertex','google-gemini-api']},
        {'id':'google-gemini-35-flash', 'name':'Gemini 3.5 Flash', 'layer':'L3','type':'foundation-model','integrates_with':['google-vertex','google-gemini-api']},
    ],
    'openai': [
        {'id':'openai-gpt-55', 'name':'GPT-5.5', 'layer':'L3','type':'foundation-model','integrates_with':['openai-api']},
    ],
}

added = 0
for vkey, comps_to_add in ADDITIONS.items():
    vendor = data['vendor_role_profiles'].get(vkey)
    if not vendor:
        print(f'! vendor missing: {vkey}'); continue
    existing_ids = {c['id'] for c in vendor.get('components', [])}
    for c in comps_to_add:
        if c['id'] in existing_ids: continue
        c.setdefault('integrates_with', [])
        vendor.setdefault('components', []).append(c)
        existing_ids.add(c['id'])
        added += 1

SCHEMA.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
total = sum(len(v.get('components', [])) for v in data['vendor_role_profiles'].values())
print(f'Added {added} components. Total now: {total}.')
for k, v in data['vendor_role_profiles'].items():
    print(f'  {k}: {len(v.get("components",[]))} components')
