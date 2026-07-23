import json
from pathlib import Path

SCHEMA = Path('ai_platform_ecosystem_framework_v1.json')
data = json.loads(SCHEMA.read_text(encoding='utf-8-sig'))

# 1. Find and remove local_infra vendor, collect its components
local = data['vendor_role_profiles'].pop('local_infra', None)
if not local:
    print('No local_infra vendor found.')
    exit(0)

local_components = local.get('components', [])

# 2. Prepare new IDs for NVIDIA
id_map = {
    'local-nvidia-h100': 'nvidia-h100-local',
    'local-vllm': 'nvidia-vllm',
    'local-triton': 'nvidia-triton-local',
    'local-mlflow': 'nvidia-mlflow-local',
    'local-docker-compose': 'nvidia-docker-compose-local',
}

# 3. Add to NVIDIA vendor
nvidia = data['vendor_role_profiles']['nvidia']
for c in local_components:
    old_id = c['id']
    if old_id in id_map:
        c['id'] = id_map[old_id]
        # Add '(Local)' to name if not present
        if '(Local)' not in c['name']:
            c['name'] += ' (Local)'
        nvidia['components'].append(c)

# 4. Update integrates_with references in all vendors
for v in data['vendor_role_profiles'].values():
    for c in v.get('components', []):
        if 'integrates_with' in c:
            c['integrates_with'] = [id_map.get(x, x) for x in c['integrates_with']]

SCHEMA.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
print('Merged local/on-prem into NVIDIA. Removed local_infra vendor.')
