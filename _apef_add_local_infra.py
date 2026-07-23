import json
from pathlib import Path

SCHEMA = Path('ai_platform_ecosystem_framework_v1.json')
data = json.loads(SCHEMA.read_text(encoding='utf-8-sig'))

# 1. Add local_infra vendor if not present
if 'local_infra' not in data['vendor_role_profiles']:
    data['vendor_role_profiles']['local_infra'] = {
        "vendor": "Local/On-Prem",
        "primary_roles": ["On-prem/edge AI platform"],
        "strongest_layers": ["L1", "L2", "L4"],
        "typical_buying_reason": "Data residency, privacy, or cost for running AI workloads locally.",
        "watchouts": ["Requires in-house ops and MLOps maturity"],
        "executive_summary": "Local/On-Prem infrastructure enables organizations to run AI models on dedicated hardware for privacy, cost, or latency reasons. Popular for open models and regulated workloads.",
        "components": [
            {"id": "local-nvidia-h100", "name": "NVIDIA H100 (Local)", "layer": "L1", "type": "silicon"},
            {"id": "local-amd-mi300", "name": "AMD MI300 (Local)", "layer": "L1", "type": "silicon"},
            {"id": "local-intel-gaudi3", "name": "Intel Gaudi3 (Local)", "layer": "L1", "type": "silicon"},
            {"id": "local-vllm", "name": "vLLM Server", "layer": "L2", "type": "runtime"},
            {"id": "local-triton", "name": "NVIDIA Triton Inference Server", "layer": "L2", "type": "runtime"},
            {"id": "local-mlflow", "name": "MLflow", "layer": "L4", "type": "tooling"},
            {"id": "local-docker-compose", "name": "Docker Compose", "layer": "L4", "type": "orchestration"}
        ]
    }

# 2. Link hybrid-capable models to local runtime
for vkey in ["google", "meta", "openai"]:
    vendor = data['vendor_role_profiles'].get(vkey)
    if not vendor:
        continue
    for c in vendor.get('components', []):
        if c.get('name', '').lower().startswith("gemma") or c.get('name', '').startswith("Gemini Nano") or c.get('name', '').startswith("Llama") or c.get('name', '').startswith("gpt-oss"):
            c.setdefault('integrates_with', [])
            if "local-vllm" not in c['integrates_with']:
                c['integrates_with'].append("local-vllm")

# 3. Save
SCHEMA.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
print("Local/On-Prem vendor and hybrid links added.")
