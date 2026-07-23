"""APEF expansion v2 — fill gaps with latest (through May 2026) known products.

Idempotent: only adds components whose id is not already present.
"""
import json
from pathlib import Path

SCHEMA = Path('ai_platform_ecosystem_framework_v1.json')
data = json.loads(SCHEMA.read_text(encoding='utf-8-sig'))

ADDITIONS = {
    'anthropic': [
        # Newer model SKUs / variants
        {'id':'anthropic-claude-opus-45',    'name':'Claude Opus 4.5',       'layer':'L3','type':'foundation-model','integrates_with':['anthropic-api','aws-bedrock','gcp-vertex']},
        {'id':'anthropic-claude-haiku-45',   'name':'Claude Haiku 4.5',      'layer':'L3','type':'foundation-model','integrates_with':['anthropic-api','aws-bedrock','gcp-vertex']},
        # Embeddings (via Voyage acquisition)
        {'id':'anthropic-voyage-embed',      'name':'Voyage Embeddings',     'layer':'L3','type':'foundation-model','integrates_with':['anthropic-api']},
        # Cloud runtime — Anthropic uses AWS Trainium primary, GCP TPU secondary
        {'id':'anthropic-aws-trainium-runtime','name':'AWS Trainium Training Runtime','layer':'L2','type':'infra','integrates_with':['anthropic-claude-opus-45']},
        {'id':'anthropic-gcp-tpu-runtime',   'name':'GCP TPU Inference Runtime','layer':'L2','type':'infra','integrates_with':['anthropic-claude-sonnet-45']},
        # Platform additions
        {'id':'anthropic-claude-desktop',    'name':'Claude Desktop App',    'layer':'L5','type':'distribution','integrates_with':['anthropic-claude-ai']},
        {'id':'anthropic-claude-mobile',     'name':'Claude Mobile App',     'layer':'L5','type':'distribution','integrates_with':['anthropic-claude-ai']},
        {'id':'anthropic-skills-marketplace','name':'Agent Skills Marketplace','layer':'L4','type':'tooling','integrates_with':['anthropic-agent-skills']},
        # Safety
        {'id':'anthropic-rsp-v2',            'name':'Responsible Scaling Policy v2','layer':'L6','type':'safety'},
    ],
    'microsoft': [
        # New models
        {'id':'ms-phi-4-multimodal',     'name':'Phi-4 Multimodal',      'layer':'L3','type':'foundation-model','integrates_with':['azure-foundry']},
        {'id':'ms-phi-4-mini',           'name':'Phi-4 Mini',            'layer':'L3','type':'foundation-model','integrates_with':['azure-foundry']},
        {'id':'ms-phi-4-reasoning',      'name':'Phi-4 Reasoning',       'layer':'L3','type':'foundation-model','integrates_with':['azure-foundry']},
        {'id':'ms-mai-voice-1',          'name':'MAI-Voice-1',           'layer':'L3','type':'foundation-model','integrates_with':['m365-copilot']},
        {'id':'ms-mai-image-1',          'name':'MAI-Image-1',           'layer':'L3','type':'foundation-model','integrates_with':['m365-copilot']},
        # L2 cloud runtime
        {'id':'ms-aks-ai',               'name':'Azure Kubernetes Service (AI)','layer':'L2','type':'infra','integrates_with':['azure-ml']},
        {'id':'ms-container-apps-ai',    'name':'Azure Container Apps (Serverless GPU)','layer':'L2','type':'infra','integrates_with':['azure-foundry']},
        {'id':'ms-azure-batch-ai',       'name':'Azure Batch (AI Training)','layer':'L2','type':'infra','integrates_with':['azure-ml']},
        # L4 / L5 additions
        {'id':'ms-foundry-agent-svc',    'name':'Azure AI Foundry Agent Service','layer':'L4','type':'agent-platform','integrates_with':['azure-foundry']},
        {'id':'ms-copilot-tuning',       'name':'Copilot Tuning',        'layer':'L4','type':'tooling','integrates_with':['m365-copilot']},
        {'id':'ms-copilot-control',      'name':'Copilot Control System','layer':'L4','type':'governance','integrates_with':['m365-copilot']},
        {'id':'ms-copilot-vision',       'name':'Copilot Vision',        'layer':'L5','type':'distribution','integrates_with':['m365-copilot']},
        {'id':'ms-copilot-recall',       'name':'Recall (Copilot+ PC)',  'layer':'L5','type':'distribution','integrates_with':['ms-copilot-plus-pc']},
        {'id':'ms-copilot-actions',      'name':'Copilot Actions',       'layer':'L5','type':'distribution','integrates_with':['m365-copilot']},
        {'id':'ms-copilot-pages',        'name':'Copilot Pages',         'layer':'L5','type':'distribution','integrates_with':['m365-copilot']},
        # Hardware
        {'id':'ms-maia-200',             'name':'Maia 200 Accelerator',  'layer':'L1','type':'silicon'},
    ],
    'amazon': [
        # New models
        {'id':'aws-nova-premier',        'name':'Amazon Nova Premier',   'layer':'L3','type':'foundation-model','integrates_with':['aws-bedrock']},
        {'id':'aws-nova-sonic',          'name':'Amazon Nova Sonic (Speech)','layer':'L3','type':'foundation-model','integrates_with':['aws-bedrock']},
        {'id':'aws-nova-act',            'name':'Amazon Nova Act (Agent)','layer':'L3','type':'foundation-model','integrates_with':['aws-bedrock']},
        {'id':'aws-titan-text-v2',       'name':'Amazon Titan Text v2',  'layer':'L3','type':'foundation-model','integrates_with':['aws-bedrock']},
        # L2 runtime
        {'id':'aws-eks-ai',              'name':'Amazon EKS (AI Workloads)','layer':'L2','type':'infra','integrates_with':['aws-sagemaker']},
        {'id':'aws-ecs-ai',              'name':'Amazon ECS / Fargate (AI)','layer':'L2','type':'infra','integrates_with':['aws-bedrock']},
        {'id':'aws-batch-ai',            'name':'AWS Batch (Training)',  'layer':'L2','type':'infra','integrates_with':['aws-sagemaker']},
        # L4 / L5 additions
        {'id':'aws-q-apps',              'name':'Amazon Q Apps',         'layer':'L5','type':'distribution','integrates_with':['aws-q-business']},
        {'id':'aws-bedrock-data-auto',   'name':'Bedrock Data Automation','layer':'L4','type':'tooling','integrates_with':['aws-bedrock']},
        {'id':'aws-bedrock-studio',      'name':'Bedrock Studio',        'layer':'L4','type':'tooling','integrates_with':['aws-bedrock']},
        # Safety
        {'id':'aws-bedrock-eval',        'name':'Bedrock Model Evaluation','layer':'L6','type':'safety','integrates_with':['aws-bedrock']},
    ],
    'google': [
        # Latest Gemini + multimodal
        {'id':'google-gemini-25-computer-use','name':'Gemini 2.5 Computer Use','layer':'L3','type':'foundation-model','integrates_with':['google-vertex','google-gemini-api']},
        {'id':'google-gemini-robotics-er','name':'Gemini Robotics-ER',   'layer':'L3','type':'foundation-model','integrates_with':['google-vertex']},
        {'id':'google-gemma-3n',         'name':'Gemma 3n (on-device)',  'layer':'L3','type':'foundation-model'},
        {'id':'google-imagen-4-ultra',   'name':'Imagen 4 Ultra',        'layer':'L3','type':'foundation-model','integrates_with':['google-vertex']},
        {'id':'google-imagen-4-fast',    'name':'Imagen 4 Fast',         'layer':'L3','type':'foundation-model','integrates_with':['google-vertex']},
        {'id':'google-veo-31',           'name':'Veo 3.1 (video)',       'layer':'L3','type':'foundation-model','integrates_with':['google-vertex']},
        {'id':'google-text-embed-005',   'name':'Text Embedding 005',    'layer':'L3','type':'foundation-model','integrates_with':['google-vertex']},
        # L2 runtime
        {'id':'google-gke-ai',           'name':'GKE (AI Workloads)',    'layer':'L2','type':'infra','integrates_with':['google-vertex']},
        {'id':'google-vertex-training',  'name':'Vertex AI Training',    'layer':'L2','type':'infra','integrates_with':['google-vertex']},
        {'id':'google-vertex-pipelines', 'name':'Vertex AI Pipelines',   'layer':'L2','type':'infra','integrates_with':['google-vertex']},
        {'id':'google-cloud-run-gpu',    'name':'Cloud Run (GPU)',       'layer':'L2','type':'infra'},
        # L4 / L5
        {'id':'google-jules',            'name':'Jules (Coding Agent)',  'layer':'L4','type':'tooling','integrates_with':['google-gemini-api']},
        {'id':'google-project-astra',    'name':'Project Astra',         'layer':'L5','type':'distribution','integrates_with':['google-gemini-app']},
        {'id':'google-ai-mode-search',   'name':'AI Mode in Search',     'layer':'L5','type':'distribution','integrates_with':['google-gemini-app']},
        {'id':'google-deep-research',    'name':'Gemini Deep Research',  'layer':'L5','type':'distribution','integrates_with':['google-gemini-app']},
    ],
    'nvidia': [
        # Latest models
        {'id':'nvidia-llama-nemotron-ultra','name':'Llama Nemotron Ultra','layer':'L3','type':'foundation-model','integrates_with':['nvidia-nim']},
        {'id':'nvidia-llama-nemotron-super','name':'Llama Nemotron Super','layer':'L3','type':'foundation-model','integrates_with':['nvidia-nim']},
        {'id':'nvidia-llama-nemotron-nano','name':'Llama Nemotron Nano','layer':'L3','type':'foundation-model','integrates_with':['nvidia-nim']},
        {'id':'nvidia-cosmos-reason',    'name':'Cosmos Reason',         'layer':'L3','type':'foundation-model','integrates_with':['nvidia-nim']},
        {'id':'nvidia-cosmos-predict',   'name':'Cosmos Predict',        'layer':'L3','type':'foundation-model','integrates_with':['nvidia-nim']},
        {'id':'nvidia-cosmos-transfer',  'name':'Cosmos Transfer',       'layer':'L3','type':'foundation-model','integrates_with':['nvidia-nim']},
        {'id':'nvidia-nemo-megatron',    'name':'NeMo Megatron',         'layer':'L3','type':'foundation-model','integrates_with':['nvidia-nemo']},
        # Hardware refreshes
        {'id':'nvidia-vera-rubin',       'name':'Vera Rubin Superchip',  'layer':'L1','type':'silicon'},
        {'id':'nvidia-rubin-ultra',      'name':'Rubin Ultra',           'layer':'L1','type':'silicon'},
        # L4 additions
        {'id':'nvidia-nemo-agent-toolkit','name':'NeMo Agent Toolkit',   'layer':'L4','type':'agent-platform','integrates_with':['nvidia-nemo']},
        {'id':'nvidia-nim-agent-bp',     'name':'NIM Agent Blueprints',  'layer':'L4','type':'agent-platform','integrates_with':['nvidia-nim']},
    ],
    'openai': [
        # Newer models
        {'id':'openai-gpt5-pro',         'name':'GPT-5 Pro',             'layer':'L3','type':'foundation-model','integrates_with':['openai-api']},
        {'id':'openai-gpt5-codex',       'name':'GPT-5 Codex',           'layer':'L3','type':'foundation-model','integrates_with':['openai-api']},
        {'id':'openai-sora-2',           'name':'Sora 2',                'layer':'L3','type':'foundation-model','integrates_with':['openai-api']},
        {'id':'openai-o3-pro',           'name':'o3 Pro',                'layer':'L3','type':'foundation-model','integrates_with':['openai-api']},
        {'id':'openai-gpt-oss',          'name':'gpt-oss (open weight)', 'layer':'L3','type':'foundation-model'},
        {'id':'openai-gpt-realtime',     'name':'gpt-realtime',          'layer':'L3','type':'foundation-model','integrates_with':['openai-realtime-api']},
        # L4 platform
        {'id':'openai-apps-sdk',         'name':'Apps SDK',              'layer':'L4','type':'tooling','integrates_with':['openai-api']},
        {'id':'openai-agentkit',         'name':'AgentKit',              'layer':'L4','type':'agent-platform','integrates_with':['openai-agents-sdk']},
        {'id':'openai-chatkit',          'name':'ChatKit',               'layer':'L4','type':'tooling','integrates_with':['openai-api']},
        {'id':'openai-mcp-connectors',   'name':'MCP Connectors',        'layer':'L4','type':'tooling','integrates_with':['openai-api']},
        # L5 distribution
        {'id':'openai-chatgpt-atlas',    'name':'ChatGPT Atlas (Browser)','layer':'L5','type':'distribution','integrates_with':['openai-chatgpt']},
        {'id':'openai-chatgpt-pulse',    'name':'ChatGPT Pulse',         'layer':'L5','type':'distribution','integrates_with':['openai-chatgpt']},
        {'id':'openai-chatgpt-go',       'name':'ChatGPT Go',            'layer':'L5','type':'distribution','integrates_with':['openai-chatgpt']},
        # Safety
        {'id':'openai-model-spec',       'name':'Model Spec',            'layer':'L6','type':'safety'},
        {'id':'openai-deliberative-align','name':'Deliberative Alignment','layer':'L6','type':'safety'},
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
