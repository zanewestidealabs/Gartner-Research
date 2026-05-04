"""Apply CNAPP schema v1.1 changes in-place (in CNAPP_Schema.json).
Bumps version to 1.1, renames, expands sub-pillars, adds SHIFT-05, flags
CDR/DSPM/FRNG as non-core.
"""
import json
from pathlib import Path
from collections import OrderedDict

SCHEMA = Path("CNAPP_Schema.json")
data = json.loads(SCHEMA.read_text(encoding="utf-8"))

# Rebuild under v1.1 key
old_key = "cnapp_taxonomy_v1.0"
new_key = "cnapp_taxonomy_v1.1"
root = data.pop(old_key)

# ── schema_lineage ────────────────────────────────────────────────────────
root.setdefault("schema_lineage", {})
root["schema_lineage"]["version"] = "1.1"
root["schema_lineage"]["change_log"] = root["schema_lineage"].get("change_log", []) + [
    {
        "version": "1.1",
        "date": "2026-05-01",
        "changes": [
            "CSPM pillar: emphasize multicloud (AWS/Azure/GCP minimum) + private-cloud (OpenStack/OpenShift) coverage",
            "CSPM-01: renamed to 'Multicloud Misconfiguration Detection & Guided Auto-Remediation'",
            "CSPM-03: added 'toxic combination' detection",
            "CSPM-04: renamed to include Business Impact Scoring & Executive Reporting",
            "CWPP-01: renamed to 'Workload Runtime Monitoring' (dropped EDR); added agent vs agentless and agent-type taxonomy",
            "CWPP-02: removed CI/CD aspect (moved to SHIFT-03)",
            "SHIFT-04: added SCA, MBOM, AIBOM",
            "SHIFT-05: NEW sub-pillar — Ticketing & Workflow Integration",
            "CDR, DSPM, FRNG flagged tier=non-core (evaluate-if-present); scoring math unchanged",
        ],
    }
]

# ── pillar tier flags ─────────────────────────────────────────────────────
TIERS = {
    "CSPM":  "core",
    "CWPP":  "core",
    "CIEM":  "core",
    "SHIFT": "core",
    "CDR":   "non-core (evaluate if present)",
    "DSPM":  "non-core (evaluate if present)",
    "FRNG":  "non-core (evaluate if present)",
}
for pid, tier in TIERS.items():
    root["pillars"][pid]["tier"] = tier

# ── CSPM pillar focus + evidence_signals additions ────────────────────────
cspm = root["pillars"]["CSPM"]
cspm["focus"] = (
    "The foundational CNAPP capability — continuous assessment of cloud "
    "infrastructure configurations, compliance posture, and security "
    "benchmarks across hyperscaler environments (minimum AWS, Azure, GCP; "
    "additional providers and private-cloud stacks such as OpenStack and "
    "OpenShift count as differentiators). Covers misconfig detection, "
    "guided remediation, asset inventory with toxic-combination analysis, "
    "and business-impact-aware risk scoring."
)
extra_cspm_signals = [
    "Multicloud breadth — AWS, Azure, GCP at minimum; bonus for Oracle, Alibaba, IBM Cloud",
    "Private cloud coverage — OpenStack, OpenShift, VMware Cloud Foundation, Nutanix",
]
for s in extra_cspm_signals:
    if s not in cspm["evidence_signals"]:
        cspm["evidence_signals"].append(s)

# ── CWPP pillar — clarify agent vs agentless ──────────────────────────────
cwpp = root["pillars"]["CWPP"]
cwpp["focus"] = (
    "Runtime and pre-runtime protection for cloud workloads — virtual "
    "machines, containers, Kubernetes pods, and serverless functions. "
    "Evaluates BOTH agent-based and agentless deployment models, depth of "
    "vulnerability management, real-time vs point-in-time analysis, and "
    "the breadth of supported agent types (OS agent, K8s DaemonSet, "
    "sidecar, embedded SDK, eBPF sensor, kernel module, serverless "
    "wrapper, container-runtime hook)."
)
extra_cwpp_signals = [
    "Clear documentation of agent-based vs agentless deployment options",
    "Real-time runtime monitoring AND point-in-time snapshot analysis",
    "Multiple agent types supported (OS agent, K8s DaemonSet, sidecar, eBPF, kernel module, serverless wrapper, container-runtime hook, embedded SDK)",
]
for s in extra_cwpp_signals:
    if s not in cwpp["evidence_signals"]:
        cwpp["evidence_signals"].append(s)

# ── Sub-pillar updates ────────────────────────────────────────────────────
sp = root["sub_pillars"]

# CSPM-01 — guided auto-remediation
sp["CSPM-01"]["name"] = "Multicloud Misconfiguration Detection & Guided Auto-Remediation"
sp["CSPM-01"]["expanded_definition"] = (
    "Continuous detection of misconfigurations across AWS, Azure, GCP "
    "(and ideally Oracle, Alibaba, IBM, plus private-cloud stacks such as "
    "OpenStack and OpenShift), paired with guided auto-remediation — "
    "remediation actions are proposed via playbooks, ticketed for review, "
    "and applied with rollback and audit trail rather than silently "
    "auto-fixed."
)
sp["CSPM-01"]["what_to_verify_publicly"] = [
    "Documented rule count and coverage across AWS, Azure, GCP misconfigurations",
    "Additional cloud provider coverage (Oracle, Alibaba, IBM Cloud) as differentiators",
    "Private-cloud coverage (OpenStack, OpenShift, VMware) where applicable",
    "Guided remediation workflow — proposed fix, approval/ticket, rollback, audit trail",
    "Real-time vs scheduled scan modes for continuous monitoring",
]
sp["CSPM-01"]["search_terms"] = [
    "cloud misconfiguration",
    "CSPM",
    "cloud security posture",
    "guided remediation",
    "auto-remediation",
    "remediation playbook",
    "cloud compliance",
    "OpenStack security",
    "OpenShift security",
    "S3 bucket exposure",
]

# CSPM-03 — add toxic combination
sp["CSPM-03"]["expanded_definition"] = (
    "Continuous discovery of cloud assets across providers with "
    "relationship and graph mapping. Critical capability is detection of "
    "TOXIC COMBINATIONS — high-risk multi-factor exposures such as a "
    "publicly-exposed workload + over-privileged role + sensitive data "
    "access — surfaced as prioritized attack paths."
)
sp["CSPM-03"]["what_to_verify_publicly"] = [
    "Breadth of asset types discovered across cloud services and providers",
    "Relationship/graph mapping (network topology, IAM connections, data flows)",
    "Toxic-combination detection (e.g., public exposure + privileged identity + sensitive data)",
    "Shadow IT and unmanaged resource discovery",
    "Attack path / blast radius visualization",
]
sp["CSPM-03"]["search_terms"] = [
    "cloud asset inventory",
    "cloud visibility",
    "attack surface",
    "toxic combination",
    "attack path",
    "blast radius",
    "cloud resource discovery",
    "graph analysis cloud",
]

# CSPM-04 — business impact scoring + executive overviews
sp["CSPM-04"]["name"] = "Risk Prioritization, Business Impact Scoring & Executive Reporting"
sp["CSPM-04"]["expanded_definition"] = (
    "Contextual risk scoring that combines exploitability (EPSS, KEV), "
    "asset criticality, exposure, and BUSINESS IMPACT (revenue tier, "
    "regulatory scope, data sensitivity). Surfaces results both to "
    "operators (prioritized backlog) and executives (board-level "
    "dashboards, trend overviews, risk-by-business-unit views)."
)
sp["CSPM-04"]["what_to_verify_publicly"] = [
    "Contextual risk scoring incorporating multiple risk factors",
    "Exploitability enrichment (EPSS, KEV catalog, threat intelligence)",
    "Asset criticality / business-impact weighting (revenue, regulation, data sensitivity)",
    "Executive dashboards and overview reports (board-ready, by business unit, trend)",
    "Quantitative cyber-risk reporting (e.g., CRQ, dollar-loss estimates)",
]
sp["CSPM-04"]["search_terms"] = [
    "cloud risk prioritization",
    "contextual risk scoring",
    "business impact",
    "executive dashboard",
    "executive report",
    "risk quantification",
    "EPSS cloud",
    "alert prioritization",
]

# CWPP-01 — Workload Runtime Monitoring (drop EDR)
sp["CWPP-01"]["name"] = "Workload Runtime Monitoring"
sp["CWPP-01"]["expanded_definition"] = (
    "Continuous runtime visibility into cloud workloads — VMs, containers, "
    "Kubernetes pods, serverless. Evaluates BOTH agent-based and agentless "
    "approaches; real-time runtime telemetry vs point-in-time snapshot "
    "analysis; and the breadth of supported agent types: OS agent for VM, "
    "Kubernetes DaemonSet, sidecar container, embedded SDK, eBPF-based "
    "sensor, kernel module, function/serverless runtime wrapper, and "
    "container runtime hook."
)
sp["CWPP-01"]["what_to_verify_publicly"] = [
    "Both agent-based AND agentless runtime monitoring modes documented",
    "Real-time runtime telemetry AND point-in-time snapshot analysis",
    "Agent types supported: OS agent (VM), K8s DaemonSet, sidecar container, embedded SDK, eBPF sensor, kernel module, serverless wrapper, container-runtime hook",
    "Behavioral anomaly detection for processes, file system, and network activity",
    "File integrity monitoring (FIM) and drift detection",
]
sp["CWPP-01"]["search_terms"] = [
    "workload runtime monitoring",
    "runtime visibility",
    "agentless workload",
    "agent-based workload",
    "eBPF",
    "Kubernetes DaemonSet",
    "sidecar security",
    "kernel module",
    "container runtime hook",
    "serverless runtime",
    "file integrity monitoring",
]

# CWPP-02 — remove CI/CD aspect (moved to SHIFT-03)
sp["CWPP-02"]["expanded_definition"] = (
    "Vulnerability assessment for running workloads (OS packages, "
    "libraries, application dependencies) with exploitability "
    "prioritization (EPSS, KEV, reachability). Pre-deployment image "
    "scanning lives in SHIFT-02; CI/CD pipeline gating lives in SHIFT-03. "
    "This sub-pillar focuses on RUNTIME-aware vulnerability findings."
)
sp["CWPP-02"]["what_to_verify_publicly"] = [
    "Vulnerability scanning coverage across OS packages, libraries, and application dependencies for running workloads",
    "EPSS or KEV-based exploitability prioritization reducing actionable CVE volume",
    "Runtime-aware vulnerability assessment (packages actually loaded vs. installed)",
    "Reachability analysis to identify exploitable code paths",
]
sp["CWPP-02"]["search_terms"] = [
    "runtime vulnerability",
    "workload vulnerability",
    "EPSS prioritization",
    "KEV catalog",
    "reachability analysis",
    "CVE exploitability",
]

# SHIFT-04 — SCA, SBOM/MBOM/AIBOM
sp["SHIFT-04"]["name"] = "Software Supply Chain — SCA, SBOM, MBOM & AIBOM"
sp["SHIFT-04"]["expanded_definition"] = (
    "Software Composition Analysis (SCA) for open-source dependencies; "
    "Software Bill of Materials (SBOM) generation in SPDX/CycloneDX; "
    "Model Bill of Materials (MBOM) for ML model lineage; AI Bill of "
    "Materials (AIBOM) for GenAI components, training data, and model "
    "provenance. Includes dependency confusion / typosquatting detection."
)
sp["SHIFT-04"]["what_to_verify_publicly"] = [
    "Software Composition Analysis (SCA) for open-source dependencies",
    "SBOM generation in SPDX or CycloneDX format",
    "MBOM (Model Bill of Materials) for ML/AI model lineage",
    "AIBOM (AI Bill of Materials) for GenAI components, training data, model provenance",
    "Dependency confusion and typosquatting detection",
    "Third-party / transitive dependency vulnerability tracking",
]
sp["SHIFT-04"]["search_terms"] = [
    "SCA",
    "software composition analysis",
    "SBOM",
    "MBOM",
    "AIBOM",
    "AI bill of materials",
    "model bill of materials",
    "supply chain security",
    "dependency confusion",
    "CycloneDX",
    "SPDX",
]

# SHIFT-05 — NEW: Ticketing & Workflow Integration
sp["SHIFT-05"] = {
    "name": "Ticketing & Workflow Integration",
    "expanded_definition": (
        "Native, bi-directional integrations with enterprise ticketing, "
        "workflow, and ChatOps systems so that cloud security findings flow "
        "into the developer / SRE / SecOps work queues already in use. "
        "Includes Jira, ServiceNow, Linear, Asana for ticketing; Slack and "
        "Microsoft Teams for ChatOps; PagerDuty and Opsgenie for "
        "on-call/incident; and webhooks for custom workflow."
    ),
    "what_to_verify_publicly": [
        "Native Jira integration with bi-directional sync (status, assignee, comments)",
        "Native ServiceNow integration",
        "Slack and/or Microsoft Teams ChatOps integration",
        "PagerDuty / Opsgenie on-call integration for high-severity findings",
        "Webhook / outbound automation for custom workflows",
        "Linear, Asana, GitHub Issues coverage as differentiators",
    ],
    "search_terms": [
        "Jira integration",
        "ServiceNow integration",
        "Slack integration",
        "Microsoft Teams integration",
        "PagerDuty integration",
        "Opsgenie",
        "ticketing integration",
        "workflow automation",
        "webhook",
        "ChatOps",
    ],
    "scoring_guidance": {
        "1": "No documented ticketing or workflow integrations",
        "2": "One ticketing integration (typically Jira) only; minimal workflow",
        "3": "Jira + ServiceNow + Slack/Teams; basic webhook support",
        "4": "Bi-directional sync to Jira and ServiceNow; multiple ChatOps; PagerDuty/Opsgenie; documented webhook framework",
        "5": "Comprehensive workflow ecosystem — bi-directional Jira/ServiceNow/Linear, Slack+Teams ChatOps, PagerDuty+Opsgenie, customizable workflow engine, marketplace of pre-built playbooks",
    },
}

# Reorder sub_pillars so SHIFT-05 sits after SHIFT-04
ordered = OrderedDict()
desired_order = [
    "CSPM-01","CSPM-02","CSPM-03","CSPM-04",
    "CWPP-01","CWPP-02","CWPP-03","CWPP-04",
    "CIEM-01","CIEM-02","CIEM-03","CIEM-04",
    "SHIFT-01","SHIFT-02","SHIFT-03","SHIFT-04","SHIFT-05",
    "CDR-01","CDR-02","CDR-03","CDR-04",
    "DSPM-01","DSPM-02","DSPM-03","DSPM-04",
    "FRNG-01","FRNG-02","FRNG-03","FRNG-04",
]
for k in desired_order:
    if k in sp:
        ordered[k] = sp[k]
root["sub_pillars"] = ordered

# Also keep an evidence_signals entry on SHIFT pillar mentioning ticketing
shift = root["pillars"]["SHIFT"]
extra = "Ticketing & workflow integration (Jira, ServiceNow, Slack/Teams, PagerDuty, webhooks)"
if extra not in shift.get("evidence_signals", []):
    shift.setdefault("evidence_signals", []).append(extra)

# ── Write back ────────────────────────────────────────────────────────────
data[new_key] = root
SCHEMA.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

print("OK — wrote v1.1 to CNAPP_Schema.json")
print(f"   Top key: {new_key}")
print(f"   Sub-pillars: {len(root['sub_pillars'])} (was 28, added SHIFT-05)")
print(f"   Pillars tagged with tier: {len(TIERS)}")
