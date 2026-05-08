# Gartner Research Intelligence Platform — Full Architecture

> **Version:** 1.0 | **Date:** May 2026 | **Status:** Design Reference  
> **Audience:** Platform Architect / Lead Developer  
> **Scope:** Post-Phase 4 target state — full production deployment on GKE

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Technology Stack](#3-technology-stack)
4. [GKE Deployment Architecture](#4-gke-deployment-architecture)
5. [Authentication & Authorization](#5-authentication--authorization)
6. [Data Architecture](#6-data-architecture)
7. [Frontend Architecture (React)](#7-frontend-architecture-react)
8. [API Layer (Fastify)](#8-api-layer-fastify)
9. [Agent Platform (FastAPI Workers)](#9-agent-platform-fastapi-workers)
10. [Research Workflow — Full Phase Flow](#10-research-workflow--full-phase-flow)
11. [PouchDB Offline Sync Strategy](#11-pouchdb-offline-sync-strategy)
12. [Storage Architecture](#12-storage-architecture)
13. [CI/CD Pipeline](#13-cicd-pipeline)
14. [Build Phases](#14-build-phases)
15. [Cost Model](#15-cost-model)
16. [LLM Token Cost Analysis](#16-llm-token-cost-analysis)
17. [CouchDB Cluster Sizing](#17-couchdb-cluster-sizing)
18. [Security Architecture & Controls](#18-security-architecture--controls)

---

## 1. Executive Summary

The Gartner Research Intelligence Platform replaces a local Flask/single-file application with a cloud-native, collaborative research platform deployed on Google Kubernetes Engine. It enables Gartner analysts to:

- **Build and publish research schemas** via a UI-driven schema builder
- **Execute AI-assisted research** through configurable agent tasks with model selection
- **Collaborate in real time** — scores, excerpts, and vendor data shared across all analysts
- **Work offline** via PouchDB selective sync to IndexedDB
- **Access and cite** Gartner research, external reports, and scraped data with full audit trail

All access is gated by Google Workspace SSO via GCP Identity-Aware Proxy — zero custom auth code required.

---

## 2. System Architecture Overview

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                          GARTNER RESEARCH PLATFORM                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

  ┌────────────────────────────────────────────────────────────────────────┐
  │                         ANALYST BROWSER                                │
  │                                                                        │
  │   ┌──────────────┐  ┌───────────────┐  ┌──────────────┐  ┌─────────┐ │
  │   │   Research   │  │    Schema     │  │    Agent     │  │ Offline │ │
  │   │  Workspace   │  │    Builder    │  │   Console    │  │  Mode   │ │
  │   │  (Charts,    │  │  (Drag/Drop,  │  │  (LLM tasks, │  │(PouchDB)│ │
  │   │  Matrices,   │  │   Versioning, │  │   Streaming, │  │         │ │
  │   │  Orbital,    │  │   Publishing) │  │   Model sel) │  │         │ │
  │   │  Radar)      │  │               │  │               │  │         │ │
  │   └──────────────┘  └───────────────┘  └──────────────┘  └─────────┘ │
  │                                                                        │
  │         React 18 + TypeScript + Vite    ←→   PouchDB (IndexedDB)      │
  └──────────────────────────┬─────────────────────────────────────────────┘
                             │ HTTPS / WSS
                             │
  ┌──────────────────────────▼─────────────────────────────────────────────┐
  │                    GCP LOAD BALANCER + CLOUD CDN                       │
  │                  (Managed TLS Certificate — Let's Encrypt)             │
  └──────────────────────────┬─────────────────────────────────────────────┘
                             │
  ┌──────────────────────────▼─────────────────────────────────────────────┐
  │               IDENTITY-AWARE PROXY (IAP)                               │
  │           @gartner.com Google Workspace accounts only                  │
  │     X-Goog-Authenticated-User-Email injected on every request          │
  └──────────────────────────┬─────────────────────────────────────────────┘
                             │
  ┌──────────────────────────▼─────────────────────────────────────────────┐
  │                    GKE AUTOPILOT CLUSTER                               │
  │                    (us-central1, multi-zone)                           │
  │                                                                        │
  │  ┌─────────────────────┐        ┌──────────────────────────────────┐  │
  │  │   FASTIFY API       │        │    FASTAPI WORKER SERVICE        │  │
  │  │   (Node.js)         │        │    (Python)                      │  │
  │  │                     │        │                                  │  │
  │  │  • REST endpoints   │        │  • Agent orchestration           │  │
  │  │  • WebSocket server │  Redis │  • LLM API calls                 │  │
  │  │  • Auth middleware  │◄──────►│  • Web scraping                  │  │
  │  │  • File upload      │  Queue │  • Data pipeline scripts         │  │
  │  │  • Schema CRUD      │        │  • PDF extraction                │  │
  │  │  • Vendor CRUD      │        │  • Score computation             │  │
  │  │  • 3–10 replicas    │        │  • HPA autoscaled                │  │
  │  │  • HPA enabled      │        │  • 1–20 replicas                 │  │
  │  └──────────┬──────────┘        └──────────────┬───────────────────┘  │
  │             │                                   │                      │
  │             └──────────────┬────────────────────┘                     │
  │                            │                                           │
  │            ┌───────────────┼───────────────────┐                      │
  │            │               │                   │                      │
  │   ┌────────▼──────┐  ┌─────▼──────┐  ┌────────▼──────┐              │
  │   │  COUCHDB      │  │   REDIS    │  │  CLOUD        │              │
  │   │  StatefulSet  │  │  (Cache +  │  │  STORAGE      │              │
  │   │  3-node HA    │  │   Queue)   │  │  (GCS)        │              │
  │   │  Persistent   │  │            │  │               │              │
  │   │  Disk 200GB   │  │            │  │  Scrape cache │              │
  │   │               │  │            │  │  Uploads      │              │
  │   │  ↕ PouchDB    │  │            │  │  Exports      │              │
  │   │  replication  │  │            │  │  Agent output │              │
  │   └───────────────┘  └────────────┘  └───────────────┘              │
  │                                                                        │
  └────────────────────────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────────────────────────────┐
  │                    EXTERNAL MODEL APIS                                 │
  │                                                                        │
  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
  │   │  Vertex AI   │  │   OpenAI     │  │  Anthropic   │               │
  │   │  (Gemini     │  │  (GPT-5)     │  │  (Claude     │               │
  │   │   3.1 Pro)   │  │              │  │  Sonnet 4.6) │               │
  │   └──────────────┘  └──────────────┘  └──────────────┘               │
  │             API keys stored in GCP Secret Manager                     │
  └────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

### Frontend
| Layer | Technology | Rationale |
|---|---|---|
| Framework | **React 18 + TypeScript** | Component reuse, type safety, team scale |
| Build tool | **Vite** | Sub-second HMR, optimized prod bundles, code splitting |
| State management | **Zustand** | Lightweight, no boilerplate, works with PouchDB reactively |
| Charts/Viz | **D3.js** (existing logic migrated) | Orbital map, radar, sankey — preserve existing visualizations |
| Offline DB | **PouchDB** | IndexedDB wrapper, CouchDB-compatible replication |
| WebSockets | **Socket.io client** | Agent streaming, live collaboration |
| Styling | **Tailwind CSS** | Consistent design system, purged in prod |
| HTTP client | **TanStack Query** | Caching, background refetch, optimistic updates |

### API Gateway
| Layer | Technology | Rationale |
|---|---|---|
| Runtime | **Node.js 22 LTS** | Native async, same language as frontend |
| Framework | **Fastify 5** | 2-3x faster than Express, schema validation built-in |
| WebSockets | **Socket.io** | Agent task streaming to browser |
| Auth | **GCP IAP middleware** | Validates `X-Goog-IAP-JWT-Assertion` header |
| Validation | **Zod** | Runtime schema validation on all inputs |

### Worker Service
| Layer | Technology | Rationale |
|---|---|---|
| Runtime | **Python 3.12** | Preserves all existing scripts |
| Framework | **FastAPI** | Async, Pydantic validation, native background tasks |
| Agent orchestration | **Google ADK / LangChain** | Multi-model, tool use, streaming |
| Task queue | **Redis + Bull (Node side)** | Job queuing between Fastify and FastAPI workers |
| Scraping | **Playwright + BeautifulSoup** | Existing scraping logic migrated |
| PDF extraction | **pdfplumber** | Existing capability |
| LLM clients | **google-genai, openai, anthropic** | Direct SDK calls |

### Infrastructure
| Component | Technology |
|---|---|
| Container orchestration | GKE Autopilot (us-central1) |
| Container registry | Artifact Registry |
| Database | CouchDB 3.4 (StatefulSet, 3 nodes) |
| Cache / queue | Redis 7 (Cloud Memorystore or pod) |
| Object storage | Cloud Storage (GCS) |
| CDN | Cloud CDN (static assets) |
| TLS | Google-managed certificate |
| Auth | GCP Identity-Aware Proxy |
| Secrets | GCP Secret Manager |
| Monitoring | Cloud Monitoring + Cloud Logging |
| CI/CD | GitHub Actions → Cloud Build → GKE |

---

## 4. GKE Deployment Architecture

### 4.1 Cluster Configuration

```
GKE AUTOPILOT CLUSTER — us-central1 (PRIVATE CLUSTER)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Mode:          Autopilot (Google-managed nodes, no SSH access)
  Region:        us-central1 (zones a, b, c — multi-zone HA)
  Network:       gartner-research-vpc (private subnet 10.0.0.0/20)
  Nodes:         No public IPs — private nodes only
  Control plane: Private endpoint + Authorized Networks only
  Release channel: Regular (auto-patched)
  Workload Identity: Enabled (no service account key files)
  Binary Authorization: Enabled (only Artifact Registry images)
  Shielded nodes: Enabled (secure boot + vTPM)

  NAMESPACES
  ┌───────────────────────────────────────────────────────┐
  │  gartner-prod    ← production workloads               │
  │  gartner-staging ← pre-prod / testing                 │
  │  monitoring      ← Prometheus, Grafana stack          │
  │  external-secrets← ExternalSecrets operator           │
  └───────────────────────────────────────────────────────┘
```

### 4.2 Workload Sizing & HPA

```
POD RESOURCE SPECIFICATIONS — gartner-prod namespace
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌──────────────────┬──────────────────────┬────────────────────────────┐
  │ Workload         │ Resources per pod    │ Scaling                    │
  ├──────────────────┼──────────────────────┼────────────────────────────┤
  │ api (Fastify)    │ req: 1 CPU / 2 GB    │ min: 3  max: 12            │
  │                  │ lim: 2 CPU / 4 GB    │ HPA: CPU > 70%             │
  │                  │                      │ PDB: minAvailable: 2       │
  ├──────────────────┼──────────────────────┼────────────────────────────┤
  │ worker (FastAPI) │ req: 2 CPU / 4 GB    │ min: 2  max: 20            │
  │                  │ lim: 4 CPU / 8 GB    │ HPA: CPU > 60%             │
  │                  │                      │     OR Redis queue > 10    │
  │                  │                      │ PDB: minAvailable: 1       │
  ├──────────────────┼──────────────────────┼────────────────────────────┤
  │ couchdb-0/1/2    │ req: 2 CPU / 12 GB   │ StatefulSet: fixed 3       │
  │ (StatefulSet)    │ lim: 4 CPU / 16 GB   │ PDB: minAvailable: 2       │
  │                  │ PVC: 200 GB pd-ssd   │ (tolerates 1 node failure) │
  ├──────────────────┼──────────────────────┼────────────────────────────┤
  │ redis            │ req: 0.5 CPU / 4 GB  │ fixed: 1                   │
  │ (Cloud Memstore) │ lim: 1 CPU / 4 GB    │ (Memorystore HA tier)      │
  ├──────────────────┼──────────────────────┼────────────────────────────┤
  │ ingress-nginx    │ req: 0.5 CPU / 512MB │ min: 2  max: 4             │
  │ (controller)     │ lim: 1 CPU / 1 GB    │ HPA: CPU > 80%             │
  └──────────────────┴──────────────────────┴────────────────────────────┘

  APPROXIMATE NODE CAPACITY NEEDED (Autopilot auto-provisions)
  ┌──────────────────────────────────────────────────────────┐
  │  Steady state (3 api + 2 worker + 3 couch + ingress):    │
  │  CPU:  ~18 vCPU      RAM:  ~72 GB                        │
  │  Peak  (12 api + 20 worker):                             │
  │  CPU:  ~58 vCPU      RAM:  ~188 GB                       │
  │  Autopilot scales GCE nodes transparently to match.      │
  └──────────────────────────────────────────────────────────┘
```

### 4.3 Networking & Ingress

```
INGRESS / NETWORK TOPOLOGY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Internet → Cloud Armor → GLB → IAP → GKE Ingress (nginx)
                                               │
                     ┌─────────────────────────┤
                     │                         │
              /api/* + /socket.io/*       /static/*
                     │                         │
              api-svc:3000             Cloud CDN → GCS bucket
              (ClusterIP)

  Route table (nginx-ingress):
  ┌─────────────────────────────────────────────────────────┐
  │  /api/*         → api-svc:3000                          │
  │  /socket.io/*   → api-svc:3000  (WebSocket upgrade)    │
  │  /              → api-svc:3000  (serves index.html)     │
  │  /static/*      → redirect to Cloud CDN origin          │
  │                                                         │
  │  Headers enforced by nginx:                             │
  │  Strict-Transport-Security: max-age=31536000            │
  │  X-Content-Type-Options: nosniff                        │
  │  X-Frame-Options: DENY                                  │
  │  Content-Security-Policy: (strict — see §18)            │
  │  Referrer-Policy: strict-origin-when-cross-origin       │
  └─────────────────────────────────────────────────────────┘

  Internal service communication (ClusterIP, no internet exposure):
  ┌─────────────────────────────────────────────────────────┐
  │  api-svc     ←→  couchdb-svc   (port 5984, TLS)        │
  │  api-svc     ←→  redis-svc     (port 6379, TLS)        │
  │  worker-svc  ←→  couchdb-svc   (port 5984, TLS)        │
  │  worker-svc  ←→  redis-svc     (port 6379, TLS)        │
  │                                                         │
  │  worker-svc → Vertex AI / OpenAI / Anthropic            │
  │  (egress via Cloud NAT — no public node IPs)            │
  └─────────────────────────────────────────────────────────┘
```

### 4.4 Secrets & Identity

```
SECRETS MANAGEMENT (zero secret files on disk)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  GCP Secret Manager (source of truth)
  ├── gartner/couchdb-admin-password
  ├── gartner/openai-api-key
  ├── gartner/anthropic-api-key
  ├── gartner/redis-auth-string
  └── gartner/jwt-signing-key

  ExternalSecrets Operator syncs to K8s Secrets:
  ├── gartner-api-secret     (mounted into api pods)
  └── gartner-worker-secret  (mounted into worker pods)

  Workload Identity bindings (no service account JSON keys):
  ├── api ServiceAccount        → roles/secretmanager.secretAccessor
  │                             → roles/storage.objectAdmin (GCS)
  ├── worker ServiceAccount     → roles/secretmanager.secretAccessor
  │                             → roles/storage.objectAdmin (GCS)
  │                             → roles/aiplatform.user (Vertex AI)
  └── couchdb ServiceAccount    → roles/storage.objectAdmin (backup bucket)
```

---

## 5. Authentication & Authorization

```
AUTH FLOW — Google Workspace + GCP IAP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Analyst Browser
      │
      │  GET https://research.gartner.com/
      ▼
  GCP Load Balancer
      │
      │  Is IAP cookie present and valid?
      ▼
  ┌───┴────────────────────────────────────────┐
  │               IAP CHECK                    │
  │                                            │
  │  NO ──► Redirect to accounts.google.com   │
  │              │                             │
  │              │  User signs in with         │
  │              │  @gartner.com Google        │
  │              │  Workspace account          │
  │              │                             │
  │              ▼                             │
  │         Is domain @gartner.com?            │
  │         YES ──► Issue IAP cookie           │
  │         NO  ──► 403 Forbidden              │
  │                                            │
  │  YES ──► Validate JWT signature            │
  │          Inject headers:                   │
  │          X-Goog-Authenticated-User-Email   │
  │          X-Goog-Authenticated-User-ID      │
  │          X-Goog-IAP-JWT-Assertion          │
  └───────────────────┬────────────────────────┘
                      │
                      ▼
              Fastify API receives request
              with verified identity headers

  ROLE MODEL (Google Groups → IAP Access Levels)
  ┌────────────────────────────────────────────────┐
  │                                                │
  │  Group: all-analysts@gartner.com               │
  │    └── READ all schemas, vendors, scores       │
  │    └── CREATE own annotations, assessments     │
  │    └── RUN agent research tasks                │
  │                                                │
  │  Group: senior-analysts@gartner.com            │
  │    └── All above +                             │
  │    └── PUBLISH schemas (push to CouchDB)       │
  │    └── APPROVE vendor score changes            │
  │    └── MANAGE references                       │
  │                                                │
  │  Group: platform-admins@gartner.com            │
  │    └── All above +                             │
  │    └── MANAGE CouchDB databases                │
  │    └── VIEW audit logs                         │
  │    └── CONFIGURE agent models                  │
  │                                                │
  └────────────────────────────────────────────────┘

  FASTIFY MIDDLEWARE
  ┌─────────────────────────────────────────────┐
  │                                             │
  │  const user = req.headers                  │
  │    ['x-goog-authenticated-user-email']      │
  │    .replace('accounts.google.com:', '')     │
  │  // → "zwest@gartner.com"                  │
  │                                             │
  │  const groups = await getGroups(user)       │
  │  req.analyst = { email: user, groups }      │
  │                                             │
  └─────────────────────────────────────────────┘
```

---

## 6. Data Architecture

### 6.1 CouchDB Document Type Hierarchy

```
COUCHDB DATABASE: gartner_research
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  doc_type: "vendor"              ← CANONICAL ENTITY
  ┌──────────────────────────────────────────────┐
  │  _id: "vendor_crowdstrike"                   │
  │  name: "CrowdStrike"                         │
  │  aliases: ["CrowdStrike", "CRWD"]            │
  │  website, hq, founded, ticker...             │
  │  schemas_present: ["mdr","cnapp","offsec"]   │
  └──────────────┬───────────────────────────────┘
                 │ vendor_id (foreign key)
                 │
      ┌──────────┴──────────────────────────┐
      │                                     │
  doc_type: "vendor_score"           doc_type: "vendor_score"
  ┌────────────────────────────┐     ┌────────────────────────────┐
  │  schema_type: "mdr_vendor" │     │  schema_type: "cnapp_vendor"│
  │  cycle: "2025H2"           │     │  cycle: "2025H2"            │
  │  pillars: {                │     │  pillars: {                 │
  │    detection: 4.2,         │     │    cspm: 3.9,               │
  │    response: 3.8,          │     │    cwpp: 4.1,               │
  │    ...                     │     │    ...                      │
  │  }                         │     │  }                          │
  │  excerpt_ids: [...]        │     │  excerpt_ids: [...]         │
  └────────────────────────────┘     └─────────────────────────────┘

  doc_type: "schema"
  ┌──────────────────────────────────────────────┐
  │  _id: "schema_mdr_vendor_v2.1"               │
  │  schema_type: "mdr_vendor"                   │
  │  version: "2.1"                              │
  │  pillars: [ { id, name, weight, ... } ]      │
  │  published: true                             │
  │  published_by: "zwest@gartner.com"           │
  └──────────────────────────────────────────────┘

  doc_type: "reference"
  ┌──────────────────────────────────────────────┐
  │  _id: "ref_gartner_mq_mdr_2025"             │
  │  source: "gartner"                           │
  │  title: "Magic Quadrant for MDR 2025"        │
  │  url: "https://gartner.com/doc/G00XXXXXX"   │
  │  access_level: "gartner_internal"            │
  │  linked_schemas: ["mdr_vendor"]              │
  └──────────────┬───────────────────────────────┘
                 │ reference_id (foreign key)
                 │
  doc_type: "excerpt"
  ┌──────────────────────────────────────────────┐
  │  _id: "exc_001"                              │
  │  reference_id: "ref_gartner_mq_mdr_2025"    │
  │  vendor_id: "vendor_crowdstrike"             │
  │  pillar: "detection"                         │
  │  text: "CrowdStrike demonstrated..."         │
  │  score_influence: 0.85                       │
  └──────────────────────────────────────────────┘

  doc_type: "upload"
  ┌──────────────────────────────────────────────┐
  │  _id: "upload_abc123"                        │
  │  filename: "Forrester_Wave_MDR_2025.pdf"     │
  │  gcs_path: "gs://gartner-uploads/abc123.pdf" │
  │  extracted_text_gcs: "gs://.../abc123.txt"  │
  │  uploaded_by: "zwest@gartner.com"            │
  │  linked_schemas: ["mdr_vendor"]              │
  │  processing_status: "indexed"                │
  └──────────────────────────────────────────────┘

  doc_type: "agent_job"
  ┌──────────────────────────────────────────────┐
  │  _id: "job_xyz789"                           │
  │  task: "research_vendor_mdr"                 │
  │  models: ["gemini-3.1-pro","claude-sonnet-4-6"] │
  │  params: { vendor: "CrowdStrike", ... }      │
  │  status: "running" | "complete" | "failed"   │
  │  result_doc_ids: ["vendor_score_xyz"]        │
  │  created_by: "zwest@gartner.com"             │
  │  started_at, completed_at                    │
  └──────────────────────────────────────────────┘

  doc_type: "annotation"
  ┌──────────────────────────────────────────────┐
  │  _id: "ann_001"                              │
  │  target_id: "vendor_crowdstrike"             │
  │  target_type: "vendor"                       │
  │  text: "Strong in APAC — verify Tokyo SOC"  │
  │  created_by: "zwest@gartner.com"             │
  └──────────────────────────────────────────────┘
```

### 6.2 Storage Decision Matrix

```
DATA TYPE                        COUCHDB    GCS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Vendor identity (canonical)        ✓
Schema definitions                 ✓
Vendor scores per cycle            ✓
Reference metadata + URLs          ✓
Excerpts (quoted text)             ✓
Upload metadata + tags             ✓
Agent job records                  ✓
User annotations                   ✓
ASMF framework docs                ✓
─────────────────────────────────────────────────
Raw PDF / DOCX / XLSX files                  ✓
Extracted text from PDFs                     ✓
HTML scrape cache                            ✓
Agent raw research output                    ✓
Generated HTML exports                       ✓
Static frontend assets (CDN)                 ✓
```

---

## 7. Frontend Architecture (React)

### 7.1 Component Tree

```
src/
├── App.tsx                    ← Root, router, auth context
├── main.tsx                   ← Vite entry, PouchDB init
│
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx        ← Navigation (replaces tab system)
│   │   ├── Header.tsx         ← User info, breadcrumb
│   │   └── StatusBar.tsx      ← Sync status, agent activity
│   │
│   ├── research/
│   │   ├── VendorMatrix.tsx      ← ASMF maturity matrix
│   │   ├── RadarChart.tsx        ← Pillar radar (D3)
│   │   ├── OrbitalMap.tsx        ← 3D orbital canvas (D3)
│   │   ├── SankeyFlow.tsx        ← Effort flow (D3)
│   │   ├── ScoreCard.tsx         ← Vendor score summary
│   │   └── ExcerptPanel.tsx      ← Evidence viewer
│   │
│   ├── schema/
│   │   ├── SchemaBuilder.tsx     ← Drag/drop pillar builder
│   │   ├── SchemaList.tsx        ← Published schemas
│   │   ├── PillarEditor.tsx      ← Individual pillar config
│   │   └── SchemaPublish.tsx     ← Publish flow (senior analyst)
│   │
│   ├── vendor/
│   │   ├── VendorProfile.tsx     ← Cross-schema vendor view
│   │   ├── VendorScoreEditor.tsx ← Score entry + evidence linking
│   │   ├── VendorList.tsx        ← Filterable vendor table
│   │   └── VendorCompare.tsx     ← Side-by-side comparison
│   │
│   ├── agent/
│   │   ├── AgentConsole.tsx      ← Task input, model selector
│   │   ├── AgentStream.tsx       ← Live output via Socket.io
│   │   ├── AgentHistory.tsx      ← Past job results
│   │   └── ModelSelector.tsx     ← Gemini / GPT-5 / Claude Sonnet 4.6
│   │
│   ├── references/
│   │   ├── ReferenceList.tsx     ← All sources
│   │   ├── AddReference.tsx      ← URL + manual entry
│   │   ├── FileUpload.tsx        ← Drag/drop PDF upload
│   │   └── ExcerptLinker.tsx     ← Link text to vendor/pillar
│   │
│   └── asmf/
│       ├── ASMFFramework.tsx     ← Framework overview (existing)
│       ├── ASMFMatrix.tsx        ← Maturity matrix (existing)
│       ├── ASMFRadar.tsx         ← Target radar (existing)
│       └── ASMFAssessment.tsx    ← Self-assessment tool
│
├── hooks/
│   ├── useVendors.ts          ← TanStack Query + PouchDB
│   ├── useSchema.ts
│   ├── useAgentJob.ts         ← Socket.io subscription
│   ├── useSync.ts             ← PouchDB replication state
│   └── useAuth.ts             ← IAP user identity
│
├── lib/
│   ├── db.ts                  ← PouchDB singleton + replication
│   ├── api.ts                 ← Fastify API client (typed)
│   ├── socket.ts              ← Socket.io client singleton
│   └── export.ts              ← HTML/PDF export utilities
│
└── store/
    ├── schemaStore.ts         ← Zustand: active schema
    ├── filterStore.ts         ← Zustand: active filters
    └── agentStore.ts          ← Zustand: agent job queue
```

### 7.2 Code Splitting Strategy

```
INITIAL BUNDLE (< 150KB gzipped)
  ├── React runtime
  ├── Router
  ├── Auth/Layout
  └── Dashboard skeleton

LAZY LOADED CHUNKS (on route activation)
  ├── research-viz.chunk.js     ← D3 + all chart components
  ├── schema-builder.chunk.js   ← Schema editor
  ├── agent-console.chunk.js    ← Agent UI + Socket.io
  ├── vendor-profile.chunk.js   ← Cross-schema vendor view
  └── references.chunk.js       ← Reference/upload management

vs. CURRENT STATE
  app.js: 1.46MB uncompressed, no splitting, everything loads at once
```

---

## 8. API Layer (Fastify)

### 8.1 Route Structure

```
FASTIFY API — PORT 3000
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  AUTH MIDDLEWARE (all routes)
  X-Goog-Authenticated-User-Email → req.analyst

  /api/vendors
    GET    /                   ← list all canonical vendors
    GET    /:id                ← vendor + all schema scores
    POST   /                   ← create vendor (senior analyst)
    PATCH  /:id                ← update vendor identity

  /api/vendors/:id/scores
    GET    /                   ← all score docs for vendor
    GET    /:schema/:cycle     ← specific score document
    PUT    /:schema/:cycle     ← upsert score (with audit)

  /api/schemas
    GET    /                   ← list published schemas
    GET    /:id                ← full schema definition
    POST   /                   ← create draft (any analyst)
    POST   /:id/publish        ← publish (senior analyst only)
    PATCH  /:id                ← update draft

  /api/references
    GET    /                   ← list references (filterable)
    POST   /                   ← add reference (URL or manual)
    DELETE /:id                ← remove (senior analyst)

  /api/references/:id/excerpts
    GET    /                   ← excerpts for reference
    POST   /                   ← link excerpt to vendor/pillar
    DELETE /:excId             ← remove excerpt

  /api/uploads
    POST   /                   ← stream to GCS, create doc
    GET    /:id/status         ← processing status

  /api/agents/jobs
    GET    /                   ← job history for analyst
    POST   /                   ← submit new agent task
    GET    /:id                ← job status + result

  /api/asmf
    GET    /framework          ← ASMF framework doc
    GET    /orbital-map        ← orbital map data
    POST   /assessment         ← save self-assessment scores

  WebSocket: /socket.io
    event: "job:update"        ← agent task progress
    event: "job:complete"      ← task finished with result
    event: "sync:vendor"       ← live vendor score update
    event: "schema:published"  ← new schema available
```

### 8.2 CouchDB Proxy Pattern

```javascript
// Fastify never exposes CouchDB directly to browser
// All CouchDB access goes through validated API routes

// CORRECT — Fastify validates, then queries CouchDB
fastify.get('/api/vendors/:id', async (req, reply) => {
  const { id } = req.params  // Zod-validated, safe
  const vendor = await couch.get(`vendor_${id}`)
  const scores = await couch.find({
    selector: { doc_type: 'vendor_score', vendor_id: `vendor_${id}` }
  })
  return { vendor, scores: scores.docs }
})

// PouchDB replication is the ONLY direct browser→CouchDB path
// and is restricted by CouchDB user permissions to read-only
```

---

## 9. Agent Platform (FastAPI Workers)

### 9.1 Agent Task Flow

```
RESEARCH AGENT TASK FLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ANALYST UI
     │
     │  "Research CrowdStrike MDR capabilities,
     │   focus on APAC presence and detection speed.
     │   Use Gemini 3.1 Pro + Claude Sonnet 4.6 (dual)."
     │
     ▼
  FASTIFY API
     │  POST /api/agents/jobs
     │  { task: "research_vendor_mdr",
     │    vendor: "vendor_crowdstrike",
     │    models: ["gemini-3.1-pro", "claude-sonnet-4-6"],
     │    focus: ["apac", "detection_speed"] }
     │
     │  → Creates agent_job doc in CouchDB (status: queued)
     │  → Pushes job_id to Redis queue
     │  → Returns { job_id: "job_xyz789" } immediately
     │
     ▼
  SOCKET.IO — browser subscribes to job_xyz789 events
     │
     ▼
  FASTAPI WORKER (picks up from Redis)
     │
     ├─ STEP 1: CONTEXT LOADING
     │   ├── Fetch canonical vendor doc from CouchDB
     │   ├── Fetch existing score docs (all cycles)
     │   ├── Fetch relevant excerpts
     │   └── Fetch scrape cache from GCS if available
     │
     ├─ STEP 2: LIVE RESEARCH (if cache miss)
     │   ├── Playwright scrape vendor website
     │   ├── Search for recent press/news
     │   ├── Fetch Gartner Peer Insights ratings
     │   └── Cache raw HTML to GCS
     │
     ├─ STEP 3: LLM SYNTHESIS (dual-model by default)
     │   ├── Build context window with schema pillars
     │   ├── Dispatch to models in parallel:
     │   │   ├── Gemini 3.1 Pro (via Vertex AI)      ─┐ default
     │   │   ├── Claude Sonnet 4.6 (via Anthropic)   ─┘ dual pair
     │   │   └── GPT-5 (via OpenAI)  ← add-on (power tier / analyst opt-in)
     │   ├── Compare outputs — flag pillar divergence > 20%
     │   ├── Present both responses side-by-side in analyst UI
     │   └── Stream tokens → Redis pubsub → Fastify → Socket.io → Browser
     │
     ├─ STEP 4: STRUCTURED EXTRACTION
     │   ├── Extract pillar scores (JSON mode)
     │   ├── Extract supporting excerpts
     │   ├── Generate rationale text
     │   └── Validate against schema definition
     │
     └─ STEP 5: DRAFT COMMIT
         ├── Write vendor_score doc (status: draft)
         ├── Write excerpt docs with source links
         ├── Save agent_job result
         └── Emit job:complete → analyst browser

  ANALYST REVIEW
     │
     ├── Reviews AI-generated scores + rationale
     ├── Edits individual pillar scores
     ├── Adds/removes linked excerpts
     ├── Approves or requests revision
     └── Publishes (senior analyst) → status: published
```

### 9.2 Model Router

```
MODEL SELECTION LOGIC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  All research tasks run a minimum of 2 models in parallel.
  Outputs are shown side-by-side; analyst approves the final.

  Default (dual-model — all tiers)
    ├── Primary:   Gemini 3.1 Pro   ← GCP-native, Vertex AI billing
    └── Secondary: Claude Sonnet 4.6 ← long-form synthesis, reasoning

  Extended (add GPT-5 — power tier / analyst opt-in)
    └── GPT-5 ← complex reasoning, structured JSON extraction

  Draft / refresh mode (single model, cost-saving)
    └── gemini-3.1-flash  ← Fast, cheap, good for refresh jobs

  Available models
    ├── gemini-3.1-pro    ← Default primary (GCP/Vertex)
    ├── gemini-3.1-flash  ← Draft/refresh use cases
    ├── gpt-5             ← Complex reasoning add-on
    └── claude-sonnet-4-6 ← Default secondary (long synthesis)

  Cost guardrails (configurable per role, reflect dual-model default)
    ├── analyst:        max $20.00/task,  $100/mo
    ├── senior-analyst: max $40.00/task,  $300/mo
    └── admin:          unlimited

  All API keys from Secret Manager — never in code or env files
```

---

## 10. Research Workflow — Full Phase Flow

### Phase 1: Schema Creation

```
SCHEMA CREATION WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Analyst opens Schema Builder
       │
       ▼
  ┌──────────────────────────────────────────────┐
  │  SCHEMA BUILDER UI                           │
  │                                              │
  │  1. Name schema: "MDR Vendor v2.2"           │
  │  2. Add pillars (drag/drop):                 │
  │     ┌─────────────────────────────────────┐  │
  │     │ Pillar: Detection                   │  │
  │     │ Weight: 25%                         │  │
  │     │ Sub-pillars: [alert_fidelity,       │  │
  │     │               ttd, coverage]        │  │
  │     │ Scoring: 1-5 scale                  │  │
  │     │ Evidence required: yes              │  │
  │     └─────────────────────────────────────┘  │
  │  3. Set maturity descriptors per stage       │
  │  4. Save as draft                            │
  └──────────────────────────────────────────────┘
       │
       ▼ POST /api/schemas (status: draft)
       │
  Collaboration: other analysts can view draft,
  suggest pillar changes, add comments
       │
       ▼
  Senior analyst reviews and publishes
  POST /api/schemas/:id/publish
       │
       ▼
  Schema doc status → "published" in CouchDB
  All analysts see new schema in vendor score editor
  PouchDB sync pushes schema to offline cache
```

### Phase 2: Vendor Research

```
VENDOR RESEARCH WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  START: New vendor or new research cycle
       │
  ┌────▼────────────────────────────────────────┐
  │  Does canonical vendor doc exist?           │
  │                                             │
  │  NO ──► Analyst creates vendor:             │
  │         - Name, website, HQ, founding       │
  │         - Stock ticker, employee range      │
  │         POST /api/vendors                   │
  │                                             │
  │  YES ──► Load existing vendor profile       │
  └────────────────────┬────────────────────────┘
                       │
  ┌────────────────────▼────────────────────────┐
  │  RESEARCH OPTIONS                           │
  │                                             │
  │  A. Manual Research                         │
  │     ├── Analyst reads source material       │
  │     ├── Pastes excerpts into Evidence panel │
  │     ├── Links excerpts to vendor + pillar   │
  │     └── Enters pillar scores manually       │
  │                                             │
  │  B. Agent-Assisted Research                 │
  │     ├── Launch agent task from console      │
  │     ├── Agent scrapes + synthesizes         │
  │     ├── Draft scores populated              │
  │     └── Analyst reviews + edits             │
  │                                             │
  │  C. Hybrid (most common)                   │
  │     ├── Agent generates draft              │
  │     ├── Analyst adds Gartner-internal refs │
  │     ├── Adjusts scores with annotation     │
  │     └── Publishes with evidence chain      │
  └────────────────────┬────────────────────────┘
                       │
  ┌────────────────────▼────────────────────────┐
  │  SCORE ENTRY UI                             │
  │                                             │
  │  Pillar: Detection           Score: [4.2]  │
  │  Evidence:                                  │
  │    [exc_001] "CrowdStrike demonstrated..."  │
  │    [exc_020] "Forrester Wave: Leader..."    │
  │  Rationale:                                 │
  │    [AI draft, editable]                     │
  │                                             │
  │  Overall: 4.1 / 5.0                        │
  │  MQ Position: ATE 4.2 / CoV 3.9           │
  │                                             │
  │  [Save Draft]  [Submit for Review]         │
  └────────────────────┬────────────────────────┘
                       │
  ┌────────────────────▼────────────────────────┐
  │  REVIEW + PUBLISH                           │
  │                                             │
  │  Senior analyst reviews:                    │
  │  - Score distribution vs. peers            │
  │  - Evidence quality check                  │
  │  - Rationale completeness                  │
  │                                             │
  │  Approve ──► status: "published"           │
  │  Reject  ──► status: "needs_revision"       │
  │             + inline comments              │
  └────────────────────┬────────────────────────┘
                       │
                       ▼
  Published vendor_score doc visible to all analysts
  PouchDB sync propagates to subscribed offline clients
```

### Phase 3: Reference Management

```
REFERENCE WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  SOURCE TYPES & HANDLING
  ┌──────────────────────────────────────────────────────┐
  │                                                      │
  │  GARTNER RESEARCH LINK                               │
  │  ┌──────────────────────────────────────────────┐    │
  │  │ Analyst pastes Gartner doc URL               │    │
  │  │ System stores: title, doc_id, URL, date      │    │
  │  │ access_level: "gartner_internal"             │    │
  │  │ NOT synced to PouchDB offline                │    │
  │  └──────────────────────────────────────────────┘    │
  │                                                      │
  │  EXTERNAL REPORT UPLOAD (PDF/DOCX)                   │
  │  ┌──────────────────────────────────────────────┐    │
  │  │ 1. User drag/drops file onto FileUpload      │    │
  │  │ 2. Streams to GCS (signed upload URL)        │    │
  │  │ 3. Worker triggered:                         │    │
  │  │    ├── pdfplumber extracts text              │    │
  │  │    ├── Text saved to GCS                     │    │
  │  │    ├── LLM identifies vendors mentioned      │    │
  │  │    └── Suggests schema linkage               │    │
  │  │ 4. Analyst reviews suggestions               │    │
  │  │ 5. upload doc → status: "indexed"            │    │
  │  └──────────────────────────────────────────────┘    │
  │                                                      │
  │  WEB SOURCE (scraped)                                │
  │  ┌──────────────────────────────────────────────┐    │
  │  │ Agent fetches + caches to GCS                │    │
  │  │ Reference doc created automatically          │    │
  │  │ Excerpts extracted by LLM                    │    │
  │  └──────────────────────────────────────────────┘    │
  │                                                      │
  │  MANUAL EXCERPT                                      │
  │  ┌──────────────────────────────────────────────┐    │
  │  │ Analyst pastes text directly                 │    │
  │  │ Links to: vendor + pillar + reference        │    │
  │  │ Becomes citable evidence immediately         │    │
  │  └──────────────────────────────────────────────┘    │
  │                                                      │
  └──────────────────────────────────────────────────────┘

  EVIDENCE CHAIN (audit trail)
  ┌──────────────────────────────────────────────────────┐
  │                                                      │
  │  vendor_score.pillars.detection.excerpt_ids          │
  │    → ["exc_001", "exc_020", "exc_045"]              │
  │                                                      │
  │  exc_001.reference_id → "ref_gartner_mq_mdr_2025"  │
  │  exc_001.text         → "CrowdStrike demonstrated..." │
  │  exc_001.page         → 12                          │
  │                                                      │
  │  ref_gartner_mq_mdr_2025.url                        │
  │    → "https://gartner.com/doc/G00XXXXXX"           │
  │                                                      │
  │  Full chain: Score → Excerpt → Reference → Source   │
  │  Every score is traceable to its evidence           │
  └──────────────────────────────────────────────────────┘
```

### Phase 4: Publishing & Sharing

```
PUBLISHING WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Research complete, scores published in CouchDB
       │
  ┌────▼─────────────────────────────────────────┐
  │  EXPORT OPTIONS                              │
  │                                             │
  │  1. In-App View                             │
  │     └── Live charts, matrices, orbital      │
  │         Shareable URL for colleagues        │
  │                                             │
  │  2. HTML Export                             │
  │     └── Self-contained HTML file            │
  │         Includes all charts (SVG inline)    │
  │         No server required to view          │
  │                                             │
  │  3. Structured Data Export                  │
  │     └── JSON dump of vendor scores          │
  │         With full evidence chain            │
  │         Machine-readable for further        │
  │         analysis                            │
  │                                             │
  │  4. Live Share                              │
  │     └── Share URL to app with filters       │
  │         Recipient sees live data            │
  │         (must be @gartner.com via IAP)      │
  └─────────────────────────────────────────────┘
```

---

## 11. PouchDB Offline Sync Strategy

```
POUCHDB SELECTIVE SYNC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Browser                 Fastify API           CouchDB
    │                          │                    │
    │  App loads               │                    │
    │  PouchDB.replicate() ────┼───────────────────►│
    │    selector: {           │                    │
    │      doc_type: "vendor"  │                    │  Pull all
    │    }                     │                    │  ~200 vendor
    │◄─────────────────────────┼────────────────────│  identity docs
    │                          │                    │  (~200KB)
    │                          │                    │
    │  Analyst opens MDR view  │                    │
    │  PouchDB.replicate() ────┼───────────────────►│
    │    selector: {           │                    │  Pull MDR
    │      doc_type:           │                    │  scores only
    │        "vendor_score",   │                    │  (~500KB)
    │      schema_type: "mdr"  │                    │
    │    }                     │                    │
    │◄─────────────────────────┼────────────────────│
    │                          │                    │
    │  [OFFLINE — flight mode] │                    │
    │                          │                    │
    │  Read vendor data        │                    │
    │  from local IndexedDB    │                    │  (no network)
    │  All charts render ✓     │                    │
    │                          │                    │
    │  Analyst edits score     │                    │
    │  Saved to local PouchDB  │                    │  (queued)
    │                          │                    │
    │  [BACK ONLINE]           │                    │
    │                          │                    │
    │  PouchDB.sync() ─────────┼───────────────────►│  Push local
    │  (two-way)               │                    │  edits up
    │                          │                    │
    │◄─────────────────────────┼────────────────────│  Pull remote
    │                          │                    │  changes down

  WHAT SYNCS OFFLINE vs. STAYS SERVER-ONLY
  ┌──────────────────────────────────────────────┐
  │                                              │
  │  SYNCS TO POUCHDB (offline available)        │
  │  ✓ All canonical vendor docs                 │
  │  ✓ Published vendor scores (selected schema) │
  │  ✓ Published schema definitions              │
  │  ✓ Public reference metadata (URLs, titles)  │
  │  ✓ ASMF framework docs                       │
  │  ✓ User's own annotations                    │
  │                                              │
  │  SERVER-ONLY (requires online)               │
  │  ✗ Gartner-internal references               │
  │  ✗ Draft/unpublished scores                  │
  │  ✗ Upload files (GCS)                        │
  │  ✗ Agent job results (raw)                   │
  │  ✗ Other analysts' private annotations       │
  │                                              │
  └──────────────────────────────────────────────┘
```

---

## 12. Storage Architecture

```
GCP STORAGE LAYOUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  COUCHDB (Persistent Disk — pd-standard 50GB)
  ┌──────────────────────────────────────────────┐
  │  Database: gartner_research                  │
  │                                              │
  │  ~200  vendor docs          (~200KB)         │
  │  ~2000 vendor_score docs    (~20MB)          │
  │  ~500  schema docs          (~5MB)           │
  │  ~5000 excerpt docs         (~10MB)          │
  │  ~1000 reference docs       (~2MB)           │
  │  ~500  upload docs          (~1MB)           │
  │  ~10000 annotation docs     (~5MB)           │
  │  ~1000 agent_job docs       (~50MB)          │
  │                             ──────────       │
  │  Total estimate:            ~93MB            │
  │  Capacity:                  50GB             │
  │  Headroom:                  ample            │
  └──────────────────────────────────────────────┘

  CLOUD STORAGE (GCS)
  ┌──────────────────────────────────────────────┐
  │                                              │
  │  gs://gartner-research-prod/                 │
  │  │                                           │
  │  ├── scrape-cache/                           │
  │  │   ├── pages_mdr/        (HTML files)     │
  │  │   ├── pages_cnapp/                       │
  │  │   ├── pages_trism/                       │
  │  │   ├── pages_offsec/                      │
  │  │   └── pages_precyber/                    │
  │  │                                           │
  │  ├── uploads/                                │
  │  │   ├── {user_id}/                         │
  │  │   │   ├── {uuid}.pdf     (originals)     │
  │  │   │   └── {uuid}_text.txt (extracted)    │
  │  │                                           │
  │  ├── agent-outputs/                          │
  │  │   └── {job_id}/                          │
  │  │       ├── raw_research.txt               │
  │  │       └── structured_scores.json         │
  │  │                                           │
  │  └── exports/                                │
  │      ├── {user_id}/                         │
  │      │   └── ASMF_Framework_{date}.html     │
  │      └── public/  (shared exports)          │
  │                                              │
  │  Lifecycle rules:                            │
  │  - scrape-cache/: delete after 90 days      │
  │  - agent-outputs/: delete after 30 days     │
  │  - uploads/: never auto-delete              │
  └──────────────────────────────────────────────┘

  REDIS (Cloud Memorystore — 1GB)
  ┌──────────────────────────────────────────────┐
  │  Agent job queue (Bull)                      │
  │  Session cache                               │
  │  Rate limiting counters                      │
  │  Live collaboration state                    │
  └──────────────────────────────────────────────┘
```

---

## 13. CI/CD Pipeline

```
CI/CD PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Developer pushes to GitHub
       │
       ▼
  ┌────────────────────────────────────────────────────┐
  │  GitHub Actions: CI                                │
  │                                                    │
  │  ├── Lint (ESLint + Ruff)                         │
  │  ├── Type check (tsc --noEmit)                    │
  │  ├── Unit tests (Vitest + pytest)                 │
  │  ├── Build (vite build)                           │
  │  └── Docker build (validate only)                 │
  └────────────────────────┬───────────────────────────┘
                           │ on: push to main
                           ▼
  ┌────────────────────────────────────────────────────┐
  │  Cloud Build: Build + Push                         │
  │                                                    │
  │  ├── Build api image                              │
  │  │   FROM node:22-slim                            │
  │  │   → gcr.io/gartner-research/api:SHA            │
  │  │                                                │
  │  ├── Build worker image                           │
  │  │   FROM python:3.12-slim                        │
  │  │   → gcr.io/gartner-research/worker:SHA         │
  │  │                                                │
  │  └── Push static assets to GCS                   │
  │      gsutil rsync dist/ gs://cdn-bucket/          │
  │      (CDN cache invalidation triggered)           │
  └────────────────────────┬───────────────────────────┘
                           │
                           ▼
  ┌────────────────────────────────────────────────────┐
  │  GKE Deployment: Rolling update                    │
  │                                                    │
  │  kubectl set image deployment/api                  │
  │    api=gcr.io/.../api:SHA                         │
  │                                                    │
  │  kubectl set image deployment/worker               │
  │    worker=gcr.io/.../worker:SHA                   │
  │                                                    │
  │  Strategy: RollingUpdate                          │
  │    maxSurge: 1                                    │
  │    maxUnavailable: 0  ← zero downtime            │
  │                                                    │
  │  Automated rollback on health check failure       │
  └────────────────────────────────────────────────────┘

  ENVIRONMENTS
  ┌──────────────┬─────────────────┬──────────────────┐
  │  Branch      │  Environment    │  URL             │
  ├──────────────┼─────────────────┼──────────────────┤
  │  feature/*   │  —              │  Local only      │
  │  develop     │  staging        │  staging.*.com   │
  │  main        │  production     │  research.*.com  │
  └──────────────┴─────────────────┴──────────────────┘
```

---

## 14. Build Phases

```
PHASE 1 — BACKEND FOUNDATION              Target: Weeks 1-2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  □ Flask → FastAPI migration (app.py routes)
  □ CouchDB install + database setup
  □ Python migration script: JSON files → CouchDB docs
    (vendor canonical + schema-specific score docs)
  □ FastAPI routes mirroring existing Flask /api/* endpoints
  □ Existing app.js continues to work (no frontend changes)
  □ Dual-read: try CouchDB first, fall back to JSON files

  Deliverable: Flask replaced by FastAPI, data in CouchDB,
               zero user-visible change

PHASE 2 — GKE DEPLOYMENT                  Target: Weeks 3-4
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  □ Dockerfile for FastAPI app
  □ GKE Autopilot cluster creation
  □ CouchDB StatefulSet + PVC
  □ FastAPI Deployment + Service
  □ GCP Load Balancer + managed TLS
  □ IAP configured for @gartner.com
  □ GCS buckets created + scrape cache migrated
  □ Secret Manager for API keys
  □ Cloud Monitoring dashboards

  Deliverable: App running on GKE, accessible to all
               @gartner.com users via SSO

PHASE 3 — FASTIFY API + WEBSOCKETS        Target: Weeks 5-6
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  □ Fastify project setup (TypeScript)
  □ All REST routes from FastAPI replicated in Fastify
  □ Socket.io server for agent streaming
  □ Redis job queue (Bull)
  □ FastAPI becomes worker-only service
  □ File upload endpoint → GCS
  □ Auth middleware (IAP JWT validation)
  □ Role-based access control

  Deliverable: Fastify is primary API, FastAPI is
               async worker, WebSocket streaming ready

PHASE 4 — REACT FRONTEND                  Target: Weeks 7-10
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  □ Vite + React 18 + TypeScript project
  □ Component decomposition from app.js (26,600 lines)
    ├── All D3 visualizations → React components
    ├── ASMF framework, matrix, radar, orbital, sankey
    ├── MDR, CNAPP, TRISM, OffSec, PreCyber views
    └── Research workspace, scoring UI
  □ PouchDB integration + selective sync
  □ TanStack Query for server state
  □ Zustand for UI state
  □ Socket.io client for agent streaming
  □ Static assets → GCS + Cloud CDN
  □ Code splitting (lazy route loading)

  Deliverable: Full React frontend, offline capable,
               replaces app.js monolith entirely

PHASE 5 — AGENT PLATFORM                  Target: Weeks 11-14
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  □ Agent Console UI (React)
  □ Model selector (Gemini 3.1 Pro / GPT-5 / Claude Sonnet 4.6)
  □ Dual-model parallel dispatch with side-by-side diff view
  □ FastAPI agent orchestration with Google ADK
  □ Research agent: vendor → scrape → synthesize → score
  □ Schema builder UI (drag/drop pillar editor)
  □ Reference management UI
  □ File upload + PDF extraction pipeline
  □ Evidence linking UI
  □ Agent streaming output to browser via Socket.io
  □ Cost guardrails per role

  Deliverable: Full AI-assisted research platform,
               analysts can run research from UI

PHASE 6 — COLLABORATION + POLISH          Target: Weeks 15-16
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  □ Live score update notifications (Socket.io)
  □ Annotation system
  □ Score review + approval workflow
  □ Audit log UI (admin)
  □ Cross-schema vendor profile view
  □ Export pipeline (HTML, JSON)
  □ HPA tuning under load
  □ Performance testing (k6) to 5000 concurrent users

  Deliverable: Production-ready collaborative platform
```

---

## 15. Cost Model

### 15.1 GCP Infrastructure

```
MONTHLY GCP INFRASTRUCTURE COST (5000 users)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  GKE Autopilot (revised for actual pod specs — see §4.2)
  ├── API pods (3x, 1 CPU / 2GB RAM each)       ~$65/mo
  ├── Worker pods (2x avg, 2 CPU / 4GB RAM)     ~$90/mo
  ├── CouchDB pods (3x, 2 CPU / 12GB RAM each)  ~$185/mo
  └── Redis (Memorystore HA, 4GB)               ~$65/mo

  Storage
  ├── CouchDB pd-ssd PVCs (3x 200GB)           ~$102/mo
  ├── Cloud Storage GCS (~100GB active)         ~$2/mo
  └── Artifact Registry                         ~$2/mo

  Networking
  ├── Load Balancer                             ~$18/mo
  ├── Cloud CDN (static assets)                ~$5/mo
  ├── Cloud NAT (worker egress)                ~$5/mo
  └── Egress (~200GB/mo at scale)              ~$18/mo

  Other
  ├── Secret Manager                           ~$1/mo
  └── Cloud Monitoring + Logging               ~$10/mo
                                              ──────────
  Infrastructure subtotal:                    ~$568/mo

  Security services (§18.9)                   ~$ 56/mo
  BeyondCorp Enterprise (200 power users)     ~$240/mo
                                              ──────────
  Infrastructure + security total:            ~$864/mo
```

> Full cost model including LLM costs: see **§18.10**.

---

## 16. LLM Token Cost Analysis

### 16.1 Assumptions

```
RESEARCH ASSUMPTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Users:          5,000 analysts
  Research cadence: 1 major research task per analyst per quarter
  Vendors per task: 50 vendors (each researched individually)
  Research cycles:  4 per year (quarterly)
  Data retention:   6 months rolling
  Annual refresh:   All vendor-schema pairs refreshed ≥ 1x/year
  Vendor-schema pairs: ~400 (200 vendors × ~2 schemas avg)

  TOKEN BUDGET PER VENDOR (major research)
  ┌────────────────────────────────────────────────────┐
  │                                                    │
  │  INPUT CONTEXT (~21,000 tokens)                   │
  │  ├── Schema definition + pillar descriptors  3,000 │
  │  ├── Vendor profile (existing data)          3,000 │
  │  ├── Scraped website content (condensed)     8,000 │
  │  ├── Recent news / press releases            4,000 │
  │  ├── Existing excerpts + references          2,000 │
  │  └── Task prompt + instructions              1,000 │
  │                                                    │
  │  OUTPUT (~8,000 tokens)                           │
  │  ├── Pillar-by-pillar rationale              4,000 │
  │  ├── Extracted / generated excerpts          2,000 │
  │  ├── MQ positioning rationale                1,000 │
  │  └── Structured JSON scores                    500 │
  │                    + summary                   500 │
  │                                                    │
  │  TOTAL PER VENDOR: ~29,000 tokens               │
  │  TOTAL PER 50-VENDOR TASK: ~1,450,000 tokens    │
  └────────────────────────────────────────────────────┘
```

### 16.2 Model Pricing (late 2026 — estimated)

```
LLM PRICING COMPARISON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌────────────────────┬─────────────┬──────────────┬─────────────┐
  │ Model              │ Input       │ Output       │ Billing     │
  │                    │ (per MTok)  │ (per MTok)   │             │
  ├────────────────────┼─────────────┼──────────────┼─────────────┤
  │ Gemini 3.1 Pro     │ $2.00 *     │ $8.00 *      │ GCP/Vertex  │
  │ GPT-5              │ $5.00 *     │ $20.00 *     │ OpenAI      │
  │ Claude Sonnet 4.6  │ $3.00       │ $15.00       │ Anthropic   │
  └────────────────────┴─────────────┴──────────────┴─────────────┘

  * Gemini 3.1 Pro and GPT-5 pricing estimated; adjust when
    official pricing is published.

  DEFAULT PAIR: Gemini 3.1 Pro + Claude Sonnet 4.6 (runs in parallel
  for every research task — minimum 2 models per policy)

  NOTE: Only Gemini costs are covered by GCP credits.
  OpenAI and Anthropic require separate billing accounts.
```

### 16.3 Cost Per Vendor Research

```
COST PER VENDOR (21,000 input / 8,000 output tokens)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌────────────────────┬──────────┬──────────┬────────────────┐
  │ Model              │ Input $  │ Output $ │ Total/vendor   │
  ├────────────────────┼──────────┼──────────┼────────────────┤
  │ Gemini 3.1 Pro     │ $0.042   │ $0.064   │   $0.106       │
  │ GPT-5              │ $0.105   │ $0.160   │   $0.265       │
  │ Claude Sonnet 4.6  │ $0.063   │ $0.120   │   $0.183       │
  ├────────────────────┼──────────┼──────────┼────────────────┤
  │ Dual default       │          │          │   $0.289       │
  │ (Gemini + Claude)  │          │          │                │
  │ All 3 models       │          │          │   $0.554       │
  └────────────────────┴──────────┴──────────┴────────────────┘

COST PER 50-VENDOR RESEARCH TASK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌────────────────────────────────┬──────────────────────┐
  │ Model configuration            │ Cost (50 vendors)    │
  ├────────────────────────────────┼──────────────────────┤
  │ Gemini 3.1 Pro only (draft)    │  $5.30               │
  │ Claude Sonnet 4.6 only         │  $9.15               │
  │ GPT-5 only                     │  $13.25              │
  ├────────────────────────────────┼──────────────────────┤
  │ Dual default (Gemini + Claude) │  $14.45  ← standard  │
  │ All 3 models                   │  $27.70  ← power tier│
  └────────────────────────────────┴──────────────────────┘

  Dual-model default increases confidence in scores by
  exposing model disagreement as a signal for analyst review.
  Divergence > 20% on any pillar is flagged automatically.
```

### 16.4 Annual Research Cost — Full Scale (5,000 users)

```
SCENARIO A: ALL 5,000 USERS RUN QUARTERLY RESEARCH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  5,000 users × 4 quarters = 20,000 research tasks/year
  Each task: 50 vendors (minimum 2 models per task)

  ┌──────────────────────────────────────────────────────────┐
  │ QUARTERLY COST                                           │
  │                                                          │
  │ Model config        Tasks  Cost/task Quarterly   Annual  │
  │ ────────────────────────────────────────────────────── │
  │ Dual default        5,000   $14.45    $72,250   $289,000 │
  │ (Gemini+Claude)                                          │
  │ All 3 models        5,000   $27.70   $138,500   $554,000 │
  │ Draft only (Gemini) 5,000    $5.30    $26,500   $106,000 │
  └──────────────────────────────────────────────────────────┘

  Full-scale dual-default: ~$289,000/year = ~$24,083/mo LLM
  (Impractical without strict access controls — use tiered model)
```

### 16.5 Annual Research Cost — Realistic Tiered Scenario

```
SCENARIO B: TIERED USER MODEL (RECOMMENDED)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌──────────────────────────────────────────────────────────┐
  │ Tier         Users  Tasks/yr  Models          Vendors    │
  │ ──────────────────────────────────────────────────────── │
  │ Power        500    2,000     All 3 models    50/task    │
  │ (senior analysts running full vendor research)           │
  │                                                          │
  │ Standard     1,500  1,500     Dual default    20/task    │
  │ (analysts running spot-checks or focused research)       │
  │                                                          │
  │ Consumer     3,000  0         —               —         │
  │ (read-only, dashboards, no agent tasks)                  │
  └──────────────────────────────────────────────────────────┘

  POWER TIER (500 users, all 3 models, 50 vendors):
  ├── 2,000 tasks × $27.70/task = $55,400/year
  │   └── Gemini $10,600 + GPT-5 $26,500 + Claude $18,300

  STANDARD TIER (1,500 users, Gemini + Claude, 20 vendors):
  ├── Cost per task: 20 × $0.289 = $5.78
  └── 1,500 tasks × $5.78 = $8,670/year
      └── Gemini $3,180 + Claude $5,490

  TIERED TOTAL LLM: ~$64,070/year = ~$5,339/mo
                                    ───────────
  (vs. $289,000/year full-scale dual-default)

  Monthly LLM cost by provider (tiered):
  ├── Gemini 3.1 Pro (GCP):   $1,148/mo
  ├── GPT-5 (OpenAI):         $2,208/mo
  └── Claude Sonnet 4.6:      $1,983/mo
```

### 16.6 Annual Refresh Cycle Cost

```
AUTOMATED VENDOR DATA REFRESH (1x per year, all schemas)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ~400 vendor-schema pairs refreshed annually
  Refresh uses 70% of full research token budget
  (cached context reduces input tokens)
  Refresh runs dual-model (Gemini + Claude) by default.

  Refresh cost per pair (dual default, 70% budget):
  ├── 0.7 × $0.289 = $0.202/pair
  └── 400 × $0.202 = $80.80/year (~$7/mo)

  ┌──────────────────────────────────────────────────────┐
  │  Annual refresh: ~$81/year even with dual-model      │
  │  Negligible vs. active research costs                │
  └──────────────────────────────────────────────────────┘
```

### 16.7 Storage Cost for 6-Month Data Retention

```
6-MONTH RESEARCH DATA RETENTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Per vendor research instance:
  ├── Structured scores + rationale (CouchDB): ~16KB
  ├── Raw agent output text (GCS):             ~50KB
  └── Extracted excerpts (CouchDB):            ~6KB
  Total per vendor: ~72KB

  FULL SCALE (5,000 users, all research)
  ├── 20,000 tasks/yr × 50 vendors = 1,000,000 instances/yr
  ├── 6-month retention = 500,000 instances stored
  ├── GCS raw text: 500,000 × 50KB = 25GB = $0.50/mo
  ├── CouchDB docs: 500,000 × 22KB = 11GB extra
  └── Disk bump 50→100GB: ~$4/mo

  TIERED SCALE (realistic)
  ├── ~17,500 vendor instances at any time (6-mo window)
  ├── GCS: ~875MB = < $0.02/mo
  └── CouchDB: negligible additional

  ┌──────────────────────────────────────────────────────┐
  │  Storage for research data is negligible             │
  │  even at full scale: < $5/mo additional             │
  └──────────────────────────────────────────────────────┘
```

### 16.8 Total Cost Summary

```
TOTAL MONTHLY COST — SCENARIOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌────────────────────────────────────────────────────────────────┐
  │                   FULL SCALE           TIERED (recommended)    │
  │                (all 5k users,         (500 power all-3 +       │
  │                 dual-default)          1,500 standard dual)    │
  │ ──────────────────────────────────────────────────────────── │
  │ GCP Infrastructure       $320/mo              $320/mo          │
  │ LLM — Gemini 3.1 (GCP)  $8,833/mo           $1,148/mo         │
  │ LLM — GPT-5 (OpenAI)    $8,750/mo           $2,208/mo         │
  │ LLM — Claude 4.6 (Anth) $6,500/mo           $1,983/mo         │
  │ Storage (research data)  $    5/mo           $    1/mo         │
  │ Annual refresh (amort)   $    7/mo           $    7/mo         │
  │ ──────────────────────────────────────────────────────────── │
  │ TOTAL (dual default)    $24,415/mo           $5,667/mo         │
  │ TOTAL (Gemini only)     $ 3,628/mo           $  814/mo         │
  └────────────────────────────────────────────────────────────────┘

  * Full-scale dual is $293K/year — viable only with strict quota
    enforcement. Tiered model at $68K/year is the practical target.

  GCP CREDIT UTILIZATION ($1,000)
  ┌────────────────────────────────────────────────────────────────┐
  │  GCP credits cover:     GKE infra + Gemini 3.1 (Vertex AI)    │
  │  GCP credits do NOT cover: OpenAI (GPT-5), Anthropic (Claude) │
  │                                                                │
  │  Tiered scenario — GCP-billed items: $320 + $1,148 = $1,468/mo│
  │  Credits last: ~0.7 months of GCP costs                       │
  │  OR: if credits applied to infra only, ~3 months runway       │
  │                                                                │
  │  RECOMMENDED APPROACH:                                         │
  │  Use credits for GKE infra. Budget Gemini + external APIs      │
  │  separately. Apply credits to extend infra runway.             │
  └────────────────────────────────────────────────────────────────┘

  COST CONTROL MECHANISMS (enforce in Fastify middleware)
  ┌────────────────────────────────────────────────────────────────┐
  │  Role           Default models          Budget/task  Budget/mo │
  │  ──────────────────────────────────────────────────────────── │
  │  analyst        Gemini + Claude (dual)  $20.00       $100.00   │
  │  senior-analyst All 3 models            $40.00       $300.00   │
  │  admin          All models              Unlimited    Unlimited  │
  └────────────────────────────────────────────────────────────────┘
```

---

## 17. CouchDB Cluster Sizing

### 17.1 Data Volume Estimate

```
COUCHDB DATA VOLUME — 5,000 USERS, 6-MONTH RETENTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  DOCUMENT COUNTS (tiered realistic scenario)
  ┌────────────────────────────────────────────────────────┐
  │  doc_type          Count    Avg size   Total           │
  │  ─────────────────────────────────────────────────── ─ │
  │  vendor            200      22 KB      4.4 MB          │
  │  vendor_score      17,500   22 KB      385 MB          │
  │    (6-mo rolling)                                      │
  │  schema            50       10 KB      0.5 MB          │
  │  reference         2,000    5 KB       10 MB           │
  │  excerpt           50,000   2 KB       100 MB          │
  │  upload (meta)     5,000    2 KB       10 MB           │
  │  agent_job         10,000   5 KB       50 MB           │
  │  annotation        20,000   1 KB       20 MB           │
  │  ─────────────────────────────────────────────────── ─ │
  │  Raw data total:                       ~580 MB         │
  │  CouchDB indexes + B-trees (×3.5):     ~2 GB           │
  │  Compaction working space (×2):        ~5 GB           │
  │  WAL + replication logs:               ~1 GB           │
  │  ─────────────────────────────────────────────────── ─ │
  │  Working set per node:                 ~8 GB           │
  │                                                        │
  │  FULL-SCALE (500K vendor_score docs, 5k users):        │
  │  Raw data total:                       ~14 GB          │
  │  With indexes + compaction overhead:   ~50 GB / node   │
  └────────────────────────────────────────────────────────┘
```

### 17.2 Node Sizing

```
COUCHDB NODE SPECIFICATION (per node — 3 nodes total)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌─────────────────────────────────────────────────────────┐
  │  CPU:     4 vCPU  (request: 2 vCPU, limit: 4 vCPU)      │
  │  RAM:     16 GB   (request: 12 GB,  limit: 16 GB)       │
  │                                                         │
  │  RAM breakdown:                                         │
  │  ├── Working set in memory:          6–8 GB             │
  │  ├── B-tree indexes (hot):           2–3 GB             │
  │  ├── Erlang VM + OS:                 2 GB               │
  │  └── Buffer for burst + compaction:  3 GB               │
  │                                                         │
  │  Storage: 200 GB pd-ssd per node (NVMe SSD)             │
  │  ├── Active data + indexes:          ~8–50 GB           │
  │  ├── Compaction working space:       ×2.5 overhead       │
  │  ├── Backup + WAL logs:              ~10 GB             │
  │  └── 2-year growth headroom:         remainder           │
  │                                                         │
  │  Network: GKE internal (10 Gbps shared fabric)          │
  └─────────────────────────────────────────────────────────┘

  TOTAL CLUSTER FOOTPRINT
  ├── 3 nodes × 4 vCPU  = 12 vCPU
  ├── 3 nodes × 16 GB   = 48 GB RAM
  └── 3 nodes × 200 GB  = 600 GB raw storage
      (every document replicated on all 3 nodes)
```

### 17.3 Replication & Quorum

```
COUCHDB CLUSTER REPLICATION CONFIG (Erlang cluster)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  cluster/n = 3   ← number of nodes holding each shard
  cluster/q = 1   ← number of shards per database
  cluster/r = 2   ← nodes that must respond to a read
  cluster/w = 2   ← nodes that must acknowledge a write

  ┌──────────────────────────────────────────────────────┐
  │  Failure tolerance: 1 node failure with zero downtime│
  │  If 2 nodes fail: cluster enters read-only mode      │
  │  Write quorum (W=2): 2/3 nodes acknowledge commits   │
  │  Read quorum (R=2): cross-validated reads            │
  └──────────────────────────────────────────────────────┘

  ZONE DISTRIBUTION (anti-affinity)
  ├── couch-0  → us-central1-a
  ├── couch-1  → us-central1-b
  └── couch-2  → us-central1-c
      (K8s topologySpreadConstraints enforces zone spread)
```

### 17.4 Performance Envelope

```
EXPECTED PERFORMANCE — 3-NODE CLUSTER (4 CPU / 16 GB each)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌────────────────────────────────────────────────────────┐
  │  Operation              Throughput      Latency p99    │
  │  ────────────────────────────────────────────────────  │
  │  Single-doc read        ~6,000 req/s    < 5 ms         │
  │  Single-doc write (W=2) ~800 req/s      < 20 ms        │
  │  Mango query (indexed)  ~1,500 req/s    < 30 ms        │
  │  Bulk insert (100 docs) ~200 batch/s    < 100 ms       │
  │  PouchDB sync (repl)    ~200 concurrent 1-5 sec sync   │
  │  Agent job write burst  ~50 docs/s      < 50 ms        │
  └────────────────────────────────────────────────────────┘

  Concurrent analyst sessions:  ~1,000 (tiered)  ~3,000 (full)
  PouchDB browser sync sessions: ~200 concurrent  (throttled)
  CouchDB connections per node:  ~500 (pool managed by Fastify)

  SCALE TRIGGERS (upgrade path):
  ├── RAM utilisation > 80%  → Upgrade to 32 GB per node
  ├── Disk > 150 GB/node     → Resize PVC (online, no downtime)
  └── Write latency > 100ms  → Add 4th node + re-shard
```

### 17.5 Backup Strategy

```
COUCHDB BACKUP CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Continuous: CouchDB replication to a read replica in us-east1
  ├── Async replication lag: < 30 seconds
  └── Cross-region for DR (separate VPC peer)

  Scheduled backups (CronJob in K8s):
  ├── Hourly:   CouchDB _changes feed snapshot → GCS
  ├── Daily:    Full database dump (couchdb-backup) → GCS
  └── Weekly:   Full dump + PVC snapshot via GKE snapshot policy

  Retention:
  ├── Hourly snapshots:  48 hours
  ├── Daily dumps:       30 days
  └── Weekly dumps:      1 year

  Recovery time objective (RTO): < 1 hour (from daily backup)
  Recovery point objective (RPO): < 30 minutes (from replica)

  GCS backup bucket: gs://gartner-couchdb-backup/
  ├── Location: us (multi-region)
  ├── Storage class: Nearline (> 30 days auto-Coldline)
  └── Versioning: enabled (Object Lock for compliance)
```

---

## 18. Security Architecture & Controls

### 18.1 Security Layers Overview

```
DEFENCE-IN-DEPTH — LAYERED SECURITY MODEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  LAYER 1 — PERIMETER (Internet edge)
  ┌──────────────────────────────────────────────────────┐
  │  Cloud Armor WAF            DDoS L3/L4/L7 protection │
  │  Global Load Balancer       TLS termination, HTTPS   │
  │  Cloud CDN                  Static asset isolation   │
  └──────────────────────────────────────────────────────┘
            │
  LAYER 2 — IDENTITY & ACCESS (Zero Trust)
  ┌──────────────────────────────────────────────────────┐
  │  Identity-Aware Proxy (IAP)  BeyondCorp enforcement  │
  │  Google Workspace SSO        @gartner.com domain     │
  │  Context-aware access        Device posture checks   │
  │  IAM + Google Groups         Role-based access       │
  └──────────────────────────────────────────────────────┘
            │
  LAYER 3 — NETWORK SEGMENTATION
  ┌──────────────────────────────────────────────────────┐
  │  VPC with private subnets    No public node IPs      │
  │  VPC Firewall rules          Explicit allow-list     │
  │  K8s NetworkPolicy           Pod-to-pod micro-seg    │
  │  Cloud NAT                   Controlled egress       │
  │  Private Service Connect     GCS/APIs without egress │
  └──────────────────────────────────────────────────────┘
            │
  LAYER 4 — WORKLOAD SECURITY
  ┌──────────────────────────────────────────────────────┐
  │  GKE Shielded Nodes          Secure boot + vTPM      │
  │  Workload Identity           No service account keys │
  │  Binary Authorization        Only signed images run  │
  │  Pod Security Standards      Restricted profile      │
  │  K8s RBAC                    Least-privilege roles   │
  └──────────────────────────────────────────────────────┘
            │
  LAYER 5 — DATA SECURITY
  ┌──────────────────────────────────────────────────────┐
  │  Cloud KMS (CMEK)            Customer-managed keys   │
  │  GCS encryption              AES-256 at rest         │
  │  CouchDB TLS                 In-cluster TLS          │
  │  Secret Manager              No secrets in env vars  │
  │  VPC Service Controls        Data exfil prevention   │
  └──────────────────────────────────────────────────────┘
            │
  LAYER 6 — DETECTION & RESPONSE
  ┌──────────────────────────────────────────────────────┐
  │  Security Command Center     Threat intelligence     │
  │  Cloud Audit Logs            All control-plane ops   │
  │  VPC Flow Logs               Network traffic audit   │
  │  Container Threat Detection  Runtime anomaly detect  │
  │  Cloud Armor logs            WAF event stream        │
  └──────────────────────────────────────────────────────┘
```

### 18.2 Network Architecture & Firewall

```
VPC TOPOLOGY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  VPC: gartner-research-vpc
  ├── Subnet: gartner-gke-nodes    10.0.0.0/20   (us-central1)
  ├── Subnet: gartner-services     10.1.0.0/24   (us-central1)
  └── Subnet: gartner-db-replica   10.2.0.0/24   (us-east1 DR)

  Pod CIDR:       10.100.0.0/16   (secondary range, K8s pods)
  Service CIDR:   10.200.0.0/20   (secondary range, K8s services)

  VPC FIREWALL RULES (explicit allow, deny-all default)
  ┌───────────────────────────────────────────────────────────┐
  │  Rule                  Direction  Ports   Source          │
  │  ─────────────────────────────────────────────────────── │
  │  allow-glb-to-gke      ingress    443     35.191.0.0/16   │
  │                                           130.211.0.0/22  │
  │                                           (GLB health IPs)│
  │  allow-iap-to-gke      ingress    443     35.235.240.0/20 │
  │                                           (IAP forwarders)│
  │  allow-gke-internal    ingress    all     10.0.0.0/20     │
  │                                           10.100.0.0/16   │
  │                                           (pod/node CIDR) │
  │  allow-couch-internal  ingress    5984    10.100.0.0/16   │
  │                                           (pods only)     │
  │  allow-redis-internal  ingress    6379    10.100.0.0/16   │
  │  deny-all-ingress       ingress    all     0.0.0.0/0      │
  │  (implicit GCP default)                                   │
  │  deny-all-egress        egress     all     0.0.0.0/0      │
  │  allow-egress-apis      egress     443     199.36.153.8/30│
  │                                            (Private.goog) │
  │  allow-egress-llm       egress     443     0.0.0.0/0      │
  │                                    (worker pods only, tag)│
  │  allow-cloud-nat        egress     all     10.0.0.0/20    │
  └───────────────────────────────────────────────────────────┘

  CLOUD NAT (outbound for worker pods to reach LLM APIs):
  ├── NAT gateway: gartner-cloud-nat (us-central1)
  ├── Source: worker ServiceAccount pods only (network tag)
  └── All other pods: no internet egress
```

### 18.3 Cloud Armor WAF Configuration

```
CLOUD ARMOR SECURITY POLICY — gartner-research-policy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  RULE PRIORITY STACK
  ┌──────────────────────────────────────────────────────────┐
  │  Priority  Rule                            Action        │
  │  ──────────────────────────────────────────────────────  │
  │  100        IP allowlist (Gartner offices) ALLOW         │
  │             (corporate egress IPs + VPN ranges)          │
  │  200        Geo-restrict: allow only                     │
  │             US, UK, SG, AU, DE, JP, IN    ALLOW          │
  │             all others                    DENY           │
  │  300        OWASP CRS ModSec ruleset       DENY          │
  │             (SQLi, XSS, RCE, Path Traversal, etc.)       │
  │  400        Rate limit per IP:             THROTTLE       │
  │             100 req/min — /api/*                         │
  │             10 req/min  — /api/agents/jobs               │
  │  500        Adaptive protection:           DENY          │
  │             ML-based DDoS detection                      │
  │  2147483647 Default                        DENY          │
  └──────────────────────────────────────────────────────────┘

  ADDITIONAL CONTROLS:
  ├── Bot management: reCAPTCHA Enterprise on agent job submissions
  ├── JSON threat protection: max body size 1MB on /api/*
  ├── HTTP method restriction: only GET, POST, PUT, PATCH, DELETE
  └── Cloud Armor logs → Cloud Logging → Security Command Center
```

### 18.4 Zero Trust — BeyondCorp / IAP

```
ZERO TRUST ACCESS MODEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  PRINCIPLES
  ├── Never trust, always verify — no VPN required
  ├── Every request authenticated regardless of source network
  ├── Continuous verification — context checked per request
  └── Least privilege — role-based access at API layer

  IAP ACCESS LEVELS (context-aware)
  ┌──────────────────────────────────────────────────────────┐
  │  Level: corp-device                                      │
  │  ├── OS: Windows 11 / macOS 14+ with CrowdStrike/EDR     │
  │  ├── Certificate: Gartner managed device cert present    │
  │  └── Policy: required for senior-analyst + admin roles   │
  │                                                          │
  │  Level: verified-identity                                │
  │  ├── Account: @gartner.com verified                      │
  │  ├── MFA: enforced (Google Workspace MFA required)       │
  │  └── Policy: minimum for all access                      │
  └──────────────────────────────────────────────────────────┘

  GCP IAM BINDINGS (principle of least privilege)
  ┌──────────────────────────────────────────────────────────┐
  │  Entity                      Role                        │
  │  ──────────────────────────────────────────────────────  │
  │  all-analysts GGroup         IAP-secured Web App User    │
  │  senior-analysts GGroup      IAP-secured Web App User    │
  │                             + Logging Viewer             │
  │  platform-admins GGroup      Project Editor (scoped)     │
  │                             + Security Admin             │
  │  api ServiceAccount          Secrets Accessor            │
  │                             + Storage Object Admin       │
  │  worker ServiceAccount       Secrets Accessor            │
  │                             + Storage Object Admin       │
  │                             + Vertex AI User             │
  │  couchdb ServiceAccount      Storage Object Admin        │
  │                             (backup bucket only)         │
  │  ci-cd ServiceAccount        Artifact Registry Writer    │
  │                             + GKE Developer              │
  └──────────────────────────────────────────────────────────┘
```

### 18.5 Kubernetes NetworkPolicy (Pod Micro-Segmentation)

```
K8S NETWORKPOLICY — gartner-prod namespace
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Default policy: deny all ingress + egress on all pods
  Explicit allow rules added per workload:

  api pods:
  ├── ingress ALLOW from: nginx-ingress (port 3000)
  ├── egress  ALLOW to:   couchdb-svc   (port 5984)
  ├── egress  ALLOW to:   redis-svc     (port 6379)
  ├── egress  ALLOW to:   worker-svc    (port 8000)
  └── egress  ALLOW to:   kube-dns      (port 53)

  worker pods:
  ├── ingress ALLOW from: api pods      (port 8000)
  ├── egress  ALLOW to:   couchdb-svc   (port 5984)
  ├── egress  ALLOW to:   redis-svc     (port 6379)
  ├── egress  ALLOW to:   0.0.0.0/0     (port 443)  ← LLM APIs
  └── egress  ALLOW to:   kube-dns      (port 53)

  couchdb pods:
  ├── ingress ALLOW from: api pods      (port 5984)
  ├── ingress ALLOW from: worker pods   (port 5984)
  ├── ingress ALLOW from: couchdb pods  (ports 5986, 4369) ← cluster
  ├── egress  ALLOW to:   couchdb pods  (ports 5986, 4369)
  └── egress  ALLOW to:   kube-dns      (port 53)

  redis pods:
  ├── ingress ALLOW from: api pods      (port 6379)
  ├── ingress ALLOW from: worker pods   (port 6379)
  └── egress  ALLOW to:   kube-dns      (port 53)

  No pod can reach any other pod unless explicitly allowed.
  Implemented via Calico NetworkPolicy (GKE Dataplane V2).
```

### 18.6 Supply Chain & Container Security

```
CONTAINER SUPPLY CHAIN SECURITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  SOURCE → BUILD → SIGN → SCAN → ATTEST → DEPLOY
  │          │       │      │        │        │
  GitHub   Cloud   KMS   Artifact  Binary   GKE
  (SAST)   Build  sign  Registry  Auth    Autopilot
                        (scan)    policy

  ARTIFACT REGISTRY:
  ├── Repository: us-central1-docker.pkg.dev/gartner-research/
  ├── Vulnerability scanning: enabled (on push + continuous)
  ├── Block HIGH + CRITICAL CVEs from deployment
  └── Images tagged with git SHA (no :latest in prod)

  BINARY AUTHORIZATION POLICY:
  ├── Require attestation from Cloud Build (build provenance)
  ├── Require Vulnerability Scanner attestation (no HIGH/CRIT)
  ├── Deny all unsigned images
  └── Break-glass: admin can override with audit log entry

  GITHUB ACTIONS (CI) SAST CHECKS:
  ├── CodeQL (JS + Python) on every PR
  ├── Snyk dependency scan (block PRs with HIGH vulns)
  ├── Semgrep OWASP ruleset
  └── Secret scanning (Gitleaks + GitHub secret scan)

  BASE IMAGES:
  ├── api:     node:22-alpine (minimal attack surface)
  ├── worker:  python:3.12-slim-bookworm
  └── couchdb: apache/couchdb:3.4 (official)
  All images pinned to digest SHA, not tag.
```

### 18.7 Data Security & Encryption

```
DATA ENCRYPTION — AT REST + IN TRANSIT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  AT REST:
  ├── GCS buckets: CMEK via Cloud KMS
  │   Key ring: gartner-research-keyring (us-central1)
  │   Key rotation: automatic 90 days
  ├── CouchDB data (pd-ssd PVCs): GCE Disk encryption
  │   (Google-managed by default; CMEK optional upgrade)
  ├── Secret Manager: Google-managed HSM keys
  └── Artifact Registry: Google-managed keys

  IN TRANSIT:
  ├── Browser → GLB:        TLS 1.3 only (TLS 1.2 minimum)
  ├── GLB → GKE pods:       HTTPS (managed cert)
  ├── Pod → CouchDB:        mTLS via Istio sidecar (optional)
  │                         OR CouchDB native TLS
  ├── Pod → Redis:          TLS (Memorystore in-transit encryption)
  ├── Pod → LLM APIs:       TLS 1.3 (HTTPS to external)
  └── CouchDB → CouchDB:    Erlang cluster TLS (internal)

  VPC SERVICE CONTROLS PERIMETER:
  ├── Services in perimeter: GCS, Secret Manager, Artifact Registry,
  │                          Cloud KMS, GKE, Cloud Logging
  ├── Access policy: allow from gartner-research-vpc only
  └── Prevents data exfiltration via API calls from outside perimeter

  CORS POLICY (enforced in Fastify):
  ├── Allow-Origin: https://research.gartner.com only
  ├── Allow-Methods: GET, POST, PUT, PATCH, DELETE
  ├── Allow-Headers: Content-Type, Authorization
  └── Credentials: true (IAP cookie)
```

### 18.8 Audit, Logging & Threat Detection

```
AUDIT & DETECTION STACK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  CLOUD AUDIT LOGS (always-on):
  ├── Admin Activity:   all GCP control-plane changes
  ├── Data Access:      all CouchDB read/write via Fastify
  ├── System Events:    GKE node + pod events
  └── Policy Denied:    IAP denials, Cloud Armor blocks

  APPLICATION AUDIT (structured logs via Fastify):
  ├── Every API request: user, endpoint, method, status, ms
  ├── Agent job created/completed: user, model, cost_usd, vendor
  ├── Schema published: user, schema_id, version
  ├── Score approved/rejected: user, vendor, pillar_changes
  └── File uploaded: user, filename, gcs_path, extracted

  VPC FLOW LOGS:
  ├── All subnets: enabled (5-minute aggregation)
  ├── Exported to: Cloud Logging → BigQuery (30-day retention)
  └── Alerts: unexpected outbound traffic to non-allowlisted IPs

  SECURITY COMMAND CENTER (SCC) — Standard tier:
  ├── Web Security Scanner: weekly scan of research.gartner.com
  ├── Container Threat Detection: runtime anomaly in GKE pods
  ├── Event Threat Detection: crypto-mining, brute-force, C2 signals
  ├── Security Health Analytics: GCP misconfiguration checks
  └── Findings routed to: gartner-security@gartner.com + PagerDuty

  CLOUD MONITORING ALERTS:
  ┌──────────────────────────────────────────────────────────┐
  │  Alert                        Threshold   Channel        │
  │  ──────────────────────────────────────────────────────  │
  │  Cloud Armor block rate       > 50/min     security team │
  │  IAP denial rate              > 20/min     security team │
  │  CouchDB 5xx rate             > 1%         on-call       │
  │  Fastify error rate           > 2%         on-call       │
  │  Pod crash loop               any          on-call       │
  │  LLM cost per user/day        > $50        finance + mgr │
  │  Unusual egress volume        > 1 GB/hr    security team │
  └──────────────────────────────────────────────────────────┘
```

### 18.9 Required GCP Security Services

```
GCP SECURITY SERVICES — WHAT TO ENABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌────────────────────────────────┬──────────────┬──────────┐
  │ Service                        │ Tier         │ Est. /mo │
  ├────────────────────────────────┼──────────────┼──────────┤
  │ Cloud Armor                    │ Plus (WAF)   │ ~$35     │
  │ Identity-Aware Proxy           │ Included IAM │ $0       │
  │ BeyondCorp Enterprise          │ Standard     │ ~$6/user │
  │   (device posture, context)    │ (500 active) │ ~$3,000  │
  │ Security Command Center        │ Standard     │ ~$0      │
  │   (Essential tier is free)     │              │          │
  │ Cloud KMS (CMEK keys)          │ —            │ ~$6      │
  │ VPC Service Controls           │ Included VPC │ $0       │
  │ Binary Authorization           │ Included GKE │ $0       │
  │ Artifact Registry scanning     │ Included     │ $0       │
  │ Cloud Audit Logs               │ Included     │ $0       │
  │ VPC Flow Logs                  │ per-GB       │ ~$10     │
  │ Cloud NAT                      │ —            │ ~$5      │
  ├────────────────────────────────┼──────────────┼──────────┤
  │ SECURITY SUBTOTAL              │              │ ~$56/mo  │
  │ (excl. BeyondCorp per-user)    │              │          │
  │ BeyondCorp (optional, full ZT) │              │ +$3,000  │
  │ Without BeyondCorp (IAP only)  │              │ ~$56/mo  │
  └────────────────────────────────┴──────────────┴──────────┘

  NOTE: BeyondCorp Enterprise device posture is recommended
  for senior-analysts and admins only — not all 5,000 users.
  Standard IAP (identity-only, free) is sufficient for analysts.
  Estimated BeyondCorp cost for 200 power users: ~$240/mo.
```

### 18.10 Updated Total Cost (with Security)

```
REVISED MONTHLY COST — TIERED SCENARIO + SECURITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌──────────────────────────────────────────────────────────┐
  │ GCP Infrastructure (§15.1)          $320/mo              │
  │ Security services (WAF, KMS, etc.)  $ 56/mo              │
  │ BeyondCorp Enterprise (200 users)   $240/mo              │
  │ LLM — Gemini 3.1 Pro (GCP)          $1,148/mo            │
  │ LLM — GPT-5 (OpenAI)                $2,208/mo            │
  │ LLM — Claude Sonnet 4.6 (Anthropic) $1,983/mo            │
  │ Storage + refresh                   $    8/mo            │
  │ ─────────────────────────────────────────────────────── │
  │ TOTAL (tiered, with security)       $5,963/mo            │
  │ TOTAL (tiered, IAP-only security)   $5,667/mo            │
  │ TOTAL (Gemini only + security)      $  772/mo            │
  └──────────────────────────────────────────────────────────┘
```

---

*Document updated May 2026 — Gartner Research Intelligence Platform*  
*Architecture subject to revision as requirements evolve*
