import json
from pathlib import Path

SCHEMA = Path('ai_platform_ecosystem_framework_v1.json')
data = json.loads(SCHEMA.read_text(encoding='utf-8-sig'))

print("\nFOUNDATION MODELS BY VENDOR (L3)")
for vkey, v in data['vendor_role_profiles'].items():
    models = [c['name'] for c in v.get('components', []) if c.get('layer') == 'L3' and 'foundation-model' in c.get('type','')]
    print(f"- {vkey}: {', '.join(models) if models else '[none]'}")
