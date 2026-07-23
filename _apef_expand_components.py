"""Expand APEF vendor components to be comprehensive and current (early-2026).

Adds widely-known platform-tier products/SKUs per vendor. Only appends
components whose id is not already present, so this script is idempotent.
"""
import json
from pathlib import Path

SCHEMA = Path('ai_platform_ecosystem_framework_v1.json')
data = json.loads(SCHEMA.read_text(encoding='utf-8-sig'))

# id -> partial component to ADD (vendor inferred from grouping below)
ADDITIONS = {
    'anthropic': [
        # Models — refresh with current family generations
        {'id':'anthropic-claude-opus-4',     'name':'Claude Opus 4',     'layer':'L3','type':'foundation-model','integrates_with':['anthropic-api','aws-bedrock','gcp-vertex']},
        {'id':'anthropic-claude-sonnet-45',  'name':'Claude Sonnet 4.5', 'layer':'L3','type':'foundation-model','integrates_with':['anthropic-api','aws-bedrock','gcp-vertex']},
        {'id':'anthropic-claude-haiku-4',    'name':'Claude Haiku 4',    'layer':'L3','type':'foundation-model','integrates_with':['anthropic-api','aws-bedrock','gcp-vertex']},
        # Platform / Developer surface
        {'id':'anthropic-api',               'name':'Anthropic Messages API','layer':'L4','type':'agent-platform'},
        {'id':'anthropic-claude-code',       'name':'Claude Code',           'layer':'L4','type':'tooling','integrates_with':['anthropic-api']},
        {'id':'anthropic-computer-use',      'name':'Computer Use (Tool)',   'layer':'L4','type':'tooling','integrates_with':['anthropic-claude-sonnet-45']},
        {'id':'anthropic-tool-use',          'name':'Tool Use / Function Calling','layer':'L4','type':'tooling','integrates_with':['anthropic-api']},
        {'id':'anthropic-prompt-caching',    'name':'Prompt Caching',        'layer':'L4','type':'tooling','integrates_with':['anthropic-api']},
        {'id':'anthropic-batch-api',         'name':'Message Batches API',   'layer':'L4','type':'tooling','integrates_with':['anthropic-api']},
        {'id':'anthropic-files-api',         'name':'Files / Citations API', 'layer':'L4','type':'tooling','integrates_with':['anthropic-api']},
        {'id':'anthropic-agent-skills',      'name':'Agent Skills',          'layer':'L4','type':'tooling','integrates_with':['anthropic-claude-code','anthropic-mcp']},
        # Distribution
        {'id':'anthropic-claude-ai',         'name':'Claude.ai (Consumer)',  'layer':'L5','type':'distribution','integrates_with':['anthropic-claude-sonnet-45']},
        {'id':'anthropic-claude-enterprise', 'name':'Claude for Enterprise', 'layer':'L5','type':'distribution','integrates_with':['anthropic-claude-ai']},
        {'id':'anthropic-projects',          'name':'Projects + Artifacts',  'layer':'L5','type':'distribution','integrates_with':['anthropic-claude-ai']},
        # Safety / governance
        {'id':'anthropic-aup',               'name':'Acceptable Use Policy', 'layer':'L6','type':'safety'},
        {'id':'anthropic-constitutional-ai', 'name':'Constitutional AI',     'layer':'L6','type':'safety'},
    ],
    'microsoft': [
        # Models
        {'id':'ms-phi-4',                'name':'Phi-4',                 'layer':'L3','type':'foundation-model','integrates_with':['azure-foundry']},
        {'id':'ms-phi-35-mini',          'name':'Phi-3.5 Mini',          'layer':'L3','type':'foundation-model','integrates_with':['azure-foundry']},
        {'id':'ms-mai-1',                'name':'MAI-1 (Microsoft AI)',  'layer':'L3','type':'foundation-model','integrates_with':['m365-copilot']},
        # Infra additions
        {'id':'azure-cobalt-100',        'name':'Azure Cobalt 100 (Arm)','layer':'L1','type':'infra'},
        {'id':'azure-boost',             'name':'Azure Boost',           'layer':'L1','type':'infra'},
        # Runtime / Platform
        {'id':'azure-ai-search',         'name':'Azure AI Search',       'layer':'L4','type':'tooling','integrates_with':['azure-foundry','azure-openai']},
        {'id':'ms-semantic-kernel',      'name':'Semantic Kernel',       'layer':'L4','type':'tooling'},
        {'id':'ms-autogen',              'name':'AutoGen',               'layer':'L4','type':'tooling'},
        {'id':'ms-fabric-ai',            'name':'Microsoft Fabric (AI)', 'layer':'L4','type':'tooling','integrates_with':['azure-foundry']},
        {'id':'azure-machine-learning',  'name':'Azure Machine Learning','layer':'L4','type':'agent-platform'},
        {'id':'azure-ai-evaluations',    'name':'Azure AI Evaluations',  'layer':'L4','type':'tooling','integrates_with':['azure-foundry']},
        # Distribution
        {'id':'ms-copilot-pages',        'name':'Copilot Pages',         'layer':'L5','type':'distribution','integrates_with':['m365-copilot']},
        {'id':'ms-windows-copilot-rt',   'name':'Windows Copilot Runtime','layer':'L5','type':'distribution'},
        {'id':'ms-copilot-plus-pc',      'name':'Copilot+ PCs',          'layer':'L5','type':'distribution','integrates_with':['ms-windows-copilot-rt']},
        {'id':'ms-dynamics-copilot',     'name':'Copilot for Dynamics 365','layer':'L5','type':'distribution'},
        {'id':'ms-security-copilot',     'name':'Microsoft Security Copilot','layer':'L5','type':'distribution','integrates_with':['azure-openai']},
        # Safety / governance
        {'id':'ms-purview-ai-hub',       'name':'Purview AI Hub',        'layer':'L6','type':'safety'},
        {'id':'azure-pyrit',             'name':'PyRIT (Red Team Toolkit)','layer':'L6','type':'safety'},
        {'id':'ms-responsible-ai-std',   'name':'Responsible AI Standard','layer':'L6','type':'safety'},
    ],
    'amazon': [
        # Models (Nova family)
        {'id':'amazon-nova-lite',        'name':'Amazon Nova Lite',      'layer':'L3','type':'foundation-model','integrates_with':['aws-bedrock']},
        {'id':'amazon-nova-micro',       'name':'Amazon Nova Micro',     'layer':'L3','type':'foundation-model','integrates_with':['aws-bedrock']},
        {'id':'amazon-nova-canvas',      'name':'Amazon Nova Canvas',    'layer':'L3','type':'foundation-model','integrates_with':['aws-bedrock']},
        {'id':'amazon-nova-reel',        'name':'Amazon Nova Reel',      'layer':'L3','type':'foundation-model','integrates_with':['aws-bedrock']},
        {'id':'amazon-titan-embed',      'name':'Amazon Titan Embeddings','layer':'L3','type':'foundation-model','integrates_with':['aws-bedrock']},
        # Infra additions
        {'id':'aws-trainium3',           'name':'AWS Trainium3',         'layer':'L1','type':'infra'},
        {'id':'aws-ultraserver',         'name':'Trn2 UltraServer',      'layer':'L1','type':'infra','integrates_with':['aws-trainium']},
        {'id':'aws-ec2-p5',              'name':'EC2 P5 (NVIDIA H100)',  'layer':'L1','type':'infra'},
        {'id':'aws-ec2-p5e',             'name':'EC2 P5e (NVIDIA H200)', 'layer':'L1','type':'infra'},
        # Runtime / Platform
        {'id':'aws-sagemaker-hyperpod', 'name':'SageMaker HyperPod',     'layer':'L2','type':'infra','integrates_with':['aws-trainium','aws-ec2-p5']},
        {'id':'aws-sagemaker-unified',   'name':'SageMaker Unified Studio','layer':'L4','type':'agent-platform','integrates_with':['aws-sagemaker']},
        {'id':'aws-bedrock-kb',          'name':'Bedrock Knowledge Bases','layer':'L4','type':'tooling','integrates_with':['aws-bedrock']},
        {'id':'aws-bedrock-agents',      'name':'Bedrock Agents',        'layer':'L4','type':'agent-platform','integrates_with':['aws-bedrock']},
        {'id':'aws-bedrock-marketplace', 'name':'Bedrock Marketplace',   'layer':'L4','type':'tooling','integrates_with':['aws-bedrock']},
        {'id':'aws-strands-agents',      'name':'Strands Agents SDK',    'layer':'L4','type':'tooling'},
        {'id':'aws-bedrock-flows',       'name':'Bedrock Prompt Flows',  'layer':'L4','type':'tooling','integrates_with':['aws-bedrock']},
        # Distribution
        {'id':'amazon-q-quicksight',     'name':'Q in QuickSight',       'layer':'L5','type':'distribution'},
        {'id':'amazon-q-connect',        'name':'Q in Connect',          'layer':'L5','type':'distribution'},
        {'id':'aws-app-studio',          'name':'AWS App Studio',        'layer':'L5','type':'distribution','integrates_with':['amazon-q-developer']},
        # Safety
        {'id':'aws-responsible-ai',      'name':'AWS Responsible AI',    'layer':'L6','type':'safety'},
    ],
    'google': [
        # Models — Gemini 3.x + multimodal family
        {'id':'google-gemini-3-pro',     'name':'Gemini 3.0 Pro',        'layer':'L3','type':'foundation-model','integrates_with':['gcp-vertex','google-ai-studio']},
        {'id':'google-gemini-3-flash',   'name':'Gemini 3.0 Flash',      'layer':'L3','type':'foundation-model','integrates_with':['gcp-vertex','google-ai-studio']},
        {'id':'google-gemini-3-ultra',   'name':'Gemini 3.0 Ultra',      'layer':'L3','type':'foundation-model','integrates_with':['gcp-vertex']},
        {'id':'google-gemini-flash-lite','name':'Gemini Flash Lite',     'layer':'L3','type':'foundation-model','integrates_with':['gcp-vertex','google-ai-studio']},
        {'id':'google-gemini-nano',      'name':'Gemini Nano (on-device)','layer':'L3','type':'foundation-model','integrates_with':['google-android-ai']},
        {'id':'google-gemma-3',          'name':'Gemma 3 (open)',        'layer':'L3','type':'foundation-model'},
        {'id':'google-imagen-4',         'name':'Imagen 4',              'layer':'L3','type':'foundation-model','integrates_with':['gcp-vertex']},
        {'id':'google-veo-3',            'name':'Veo 3 (video)',         'layer':'L3','type':'foundation-model','integrates_with':['gcp-vertex']},
        {'id':'google-lyria-2',          'name':'Lyria 2 (music)',       'layer':'L3','type':'foundation-model','integrates_with':['gcp-vertex']},
        {'id':'google-chirp-3',          'name':'Chirp 3 (speech)',      'layer':'L3','type':'foundation-model','integrates_with':['gcp-vertex']},
        # Infra
        {'id':'google-tpu-ironwood',     'name':'TPU v7 Ironwood',       'layer':'L1','type':'infra'},
        {'id':'google-axion',            'name':'Google Axion (Arm)',    'layer':'L1','type':'infra'},
        {'id':'google-a3-ultra',         'name':'A3 Ultra (NVIDIA H200)','layer':'L1','type':'infra'},
        # Platform / Runtime
        {'id':'google-ai-studio',        'name':'Google AI Studio',      'layer':'L4','type':'agent-platform'},
        {'id':'google-gemini-api',       'name':'Gemini API',            'layer':'L4','type':'agent-platform','integrates_with':['google-ai-studio']},
        {'id':'google-agentspace',       'name':'Google Agentspace',     'layer':'L4','type':'agent-platform','integrates_with':['gcp-vertex']},
        {'id':'google-vertex-grounding', 'name':'Vertex Grounding (Search/Maps)','layer':'L4','type':'tooling','integrates_with':['gcp-vertex']},
        {'id':'google-vertex-eval',      'name':'Vertex Gen AI Evaluation','layer':'L4','type':'tooling','integrates_with':['gcp-vertex']},
        {'id':'google-notebooklm',       'name':'NotebookLM',            'layer':'L5','type':'distribution'},
        # Distribution
        {'id':'google-gemini-app',       'name':'Gemini App',            'layer':'L5','type':'distribution','integrates_with':['google-gemini-3-pro']},
        {'id':'google-gemini-code-assist','name':'Gemini Code Assist',    'layer':'L5','type':'distribution'},
        {'id':'google-android-ai',       'name':'Android AICore',        'layer':'L5','type':'distribution'},
        {'id':'google-project-mariner',  'name':'Project Mariner',       'layer':'L4','type':'tooling','integrates_with':['google-gemini-3-pro']},
        # Safety
        {'id':'google-secure-ai-framework','name':'Secure AI Framework (SAIF)','layer':'L6','type':'safety'},
        {'id':'google-shieldgemma',      'name':'ShieldGemma',           'layer':'L6','type':'safety'},
    ],
    'nvidia': [
        # Compute
        {'id':'nvidia-rubin',            'name':'NVIDIA Rubin (R100)',   'layer':'L1','type':'infra'},
        {'id':'nvidia-blackwell-ultra',  'name':'Blackwell Ultra (B300)','layer':'L1','type':'infra'},
        {'id':'nvidia-gh200',            'name':'Grace Hopper GH200',    'layer':'L1','type':'infra'},
        {'id':'nvidia-gb300-nvl72',      'name':'GB300 NVL72',           'layer':'L1','type':'infra'},
        {'id':'nvidia-spectrum-x',       'name':'Spectrum-X Ethernet',   'layer':'L1','type':'infra'},
        {'id':'nvidia-quantum-x',        'name':'Quantum-X InfiniBand',  'layer':'L1','type':'infra'},
        {'id':'nvidia-bluefield-3',      'name':'BlueField-3 DPU',       'layer':'L1','type':'infra'},
        # Runtime
        {'id':'nvidia-cuda',             'name':'CUDA Platform',         'layer':'L2','type':'infra'},
        {'id':'nvidia-tensorrt-llm',     'name':'TensorRT-LLM',          'layer':'L2','type':'tooling'},
        {'id':'nvidia-triton',           'name':'Triton Inference Server','layer':'L2','type':'tooling'},
        # Models
        {'id':'nvidia-nemotron',         'name':'Nemotron Model Family', 'layer':'L3','type':'foundation-model','integrates_with':['nvidia-nim']},
        {'id':'nvidia-cosmos',           'name':'NVIDIA Cosmos (World Models)','layer':'L3','type':'foundation-model'},
        {'id':'nvidia-edify',            'name':'Picasso / Edify',       'layer':'L3','type':'foundation-model'},
        {'id':'nvidia-riva',             'name':'Riva (Speech)',         'layer':'L3','type':'foundation-model'},
        # Platform tooling
        {'id':'nvidia-ai-workbench',     'name':'AI Workbench',          'layer':'L4','type':'tooling'},
        {'id':'nvidia-nemo-retriever',   'name':'NeMo Retriever',        'layer':'L4','type':'tooling','integrates_with':['nvidia-nim']},
        {'id':'nvidia-nemo-curator',     'name':'NeMo Curator',          'layer':'L4','type':'tooling'},
        {'id':'nvidia-blueprints',       'name':'NVIDIA AI Blueprints',  'layer':'L4','type':'tooling','integrates_with':['nvidia-nim']},
        {'id':'nvidia-omniverse',        'name':'Omniverse',             'layer':'L4','type':'tooling'},
        {'id':'nvidia-rapids',           'name':'RAPIDS',                'layer':'L4','type':'tooling'},
        # Distribution
        {'id':'nvidia-dgx-spark',        'name':'DGX Spark',             'layer':'L5','type':'distribution'},
        {'id':'nvidia-dgx-station',      'name':'DGX Station',           'layer':'L5','type':'distribution'},
    ],
    'openai': [
        # Models
        {'id':'openai-gpt5-mini',        'name':'GPT-5 mini',            'layer':'L3','type':'foundation-model','integrates_with':['openai-api']},
        {'id':'openai-gpt5-nano',        'name':'GPT-5 nano',            'layer':'L3','type':'foundation-model','integrates_with':['openai-api']},
        {'id':'openai-gpt41',            'name':'GPT-4.1',               'layer':'L3','type':'foundation-model','integrates_with':['openai-api']},
        {'id':'openai-o4-mini',          'name':'o4-mini',               'layer':'L3','type':'foundation-model','integrates_with':['openai-api']},
        {'id':'openai-o1',               'name':'o1',                    'layer':'L3','type':'foundation-model','integrates_with':['openai-api']},
        {'id':'openai-dalle-3',          'name':'DALL·E 3',              'layer':'L3','type':'foundation-model','integrates_with':['openai-api']},
        {'id':'openai-gpt-image-1',      'name':'GPT-Image-1',           'layer':'L3','type':'foundation-model','integrates_with':['openai-api']},
        {'id':'openai-whisper',          'name':'Whisper',               'layer':'L3','type':'foundation-model','integrates_with':['openai-api']},
        {'id':'openai-embeddings-3',     'name':'text-embedding-3',      'layer':'L3','type':'foundation-model','integrates_with':['openai-api']},
        # Platform / Runtime
        {'id':'openai-realtime-api',     'name':'Realtime API',          'layer':'L4','type':'agent-platform','integrates_with':['openai-api']},
        {'id':'openai-agents-sdk',       'name':'OpenAI Agents SDK',     'layer':'L4','type':'tooling','integrates_with':['openai-api']},
        {'id':'openai-fine-tune',        'name':'Fine-tuning API',       'layer':'L4','type':'tooling','integrates_with':['openai-api']},
        {'id':'openai-evals',            'name':'Evals',                 'layer':'L4','type':'tooling','integrates_with':['openai-api']},
        {'id':'openai-codex',            'name':'Codex (SWE Agent)',     'layer':'L4','type':'tooling','integrates_with':['openai-api']},
        # Distribution
        {'id':'openai-chatgpt',          'name':'ChatGPT',               'layer':'L5','type':'distribution','integrates_with':['openai-gpt5']},
        {'id':'openai-chatgpt-edu',      'name':'ChatGPT Edu',           'layer':'L5','type':'distribution','integrates_with':['openai-chatgpt']},
        {'id':'openai-chatgpt-team',     'name':'ChatGPT Team',          'layer':'L5','type':'distribution','integrates_with':['openai-chatgpt']},
        {'id':'openai-gpt-store',        'name':'GPT Store',             'layer':'L5','type':'distribution','integrates_with':['openai-chatgpt']},
        # Infra (Stargate program announced 2025)
        {'id':'openai-stargate',         'name':'Stargate (Compute Program)','layer':'L1','type':'infra'},
        # Safety
        {'id':'openai-usage-policies',   'name':'Usage Policies',        'layer':'L6','type':'safety'},
        {'id':'openai-safety-evals',     'name':'Safety Evaluations Hub','layer':'L6','type':'safety'},
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
        # vendor + ensure required fields
        c.setdefault('integrates_with', [])
        vendor.setdefault('components', []).append(c)
        existing_ids.add(c['id'])
        added += 1

SCHEMA.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
total = sum(len(v.get('components', [])) for v in data['vendor_role_profiles'].values())
print(f'Added {added} components. Total now: {total}.')
for k, v in data['vendor_role_profiles'].items():
    print(f'  {k}: {len(v.get("components",[]))} components')
