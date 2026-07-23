import json
from pathlib import Path

SCHEMA = Path('ai_platform_ecosystem_framework_v1.json')
data = json.loads(SCHEMA.read_text(encoding='utf-8-sig'))

local = data['vendor_role_profiles'].get('local_infra')
if local:
    before = len(local['components'])
    local['components'] = [c for c in local['components'] if not (c['id'].startswith('local-amd') or c['id'].startswith('local-intel'))]
    after = len(local['components'])
    print(f"Removed {before-after} AMD/Intel components from local_infra.")
    SCHEMA.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
else:
    print("local_infra vendor not found.")
