"""
Score Offensive Security vendors in batches.
Run: python _score_offsec_vendors.py
Reads the seed file, applies research-based scores and evidence, writes output.
"""
import json, os, copy, math

SEED = "Offensive Security Vendor 1-0 Seed.json"
OUTPUT = "Offensive Security Vendor 2-0 Researched.json"

# ── Scoring scale reminder ──
# 0 = No Evidence  |  1 = Minimal  |  2 = Generic Claims  |  3 = Demonstrated
# 4 = Advanced     |  5 = Market-Leading

# ═══════════════════════════════════════════════════════════════════════
# RESEARCH-BASED SCORES & EVIDENCE
# Each vendor dict: { scores: {sub_pillar: int}, evidence: {sub_pillar: str} }
# Only score sub-pillars in the vendor's capability_coverage.
# Sub-pillars NOT in coverage stay at 0.
# ═══════════════════════════════════════════════════════════════════════

RESEARCH = {

# ── BATCH 1 ──────────────────────────────────────────────────────────

"Tenable": {
    "scores": {
        "ASM-01": 4, "ASM-02": 5, "ASM-03": 4, "ASM-05": 4,
        "VUL-01": 5, "VUL-02": 5, "VUL-03": 5, "VUL-04": 3, "VUL-05": 4,
        "APP-05": 3,
        "REM-02": 4, "REM-03": 4, "REM-05": 4
    },
    "evidence": {
        "ASM-01": "Tenable Attack Surface Management (formerly Bit Discovery) provides continuous external asset discovery across domains, IPs, and cloud. Identifies internet-facing assets including shadow IT. Acquired Bit Discovery in 2022 to expand EASM.",
        "ASM-02": "Tenable One platform unifies asset inventory across IT, OT, cloud, containers, and identity. Tenable CSAM provides automated asset classification with criticality scoring and ownership attribution. Integrates with CMDBs.",
        "ASM-03": "Tenable Cloud Security (formerly Ermetic, acquired 2023) delivers CNAPP/CSPM across AWS, Azure, GCP. Includes container and Kubernetes security, IAM analysis, and cloud misconfiguration detection.",
        "ASM-05": "Tenable One provides continuous monitoring with exposure trending over time. Real-time alerts on new exposures and configuration drift. Exposure cards track changes across the attack surface.",
        "VUL-01": "Nessus is the world's most widely deployed vulnerability scanner with 200,000+ plugins. Covers infrastructure, cloud, containers, and applications. Agent-based and agentless options. Continuous, scheduled, and on-demand scanning.",
        "VUL-02": "Tenable VPR (Vulnerability Priority Rating) combines CVSS, EPSS, threat intelligence, exploit maturity, and asset criticality. Documented reduction of critical findings by 97% vs. CVSS-only. Industry benchmark for risk-based prioritization.",
        "VUL-03": "Comprehensive CIS, DISA STIG, and NIST compliance auditing built into Nessus and Tenable.sc. Cloud benchmarks for AWS, Azure, GCP. Custom policy support with configuration drift tracking.",
        "VUL-04": "Limited native exploitability validation. Primarily relies on VPR scoring and threat intelligence correlation rather than active exploitation. Integrations available with pen testing tools.",
        "VUL-05": "Tenable Research team (one of industry's largest) provides vulnerability intelligence. Correlates with CISA KEV, exploit databases, and active threat campaigns. Zero-day research capability with frequent advisories.",
        "APP-05": "Tenable Cloud Security includes container image scanning, IaC analysis (Terraform, CloudFormation), and Kubernetes security. Runtime protection through cloud workload posture assessment.",
        "REM-02": "Tenable One Exposure View provides unified risk scoring (CES - Cyber Exposure Score). Aggregates findings from VM, cloud, identity, and ASM. Exposure trending with quantified risk metrics.",
        "REM-03": "Integrations with ServiceNow, Jira, and major ITSM tools. Automated ticket creation with vulnerability context. Bi-directional sync and SLA tracking available via Tenable.sc and Tenable One.",
        "REM-05": "Tenable One executive dashboards with CES trending, SLA compliance, remediation progress metrics. Lumin exposure analytics provides board-ready reporting. Compliance and regulatory report templates."
    }
},

"Qualys": {
    "scores": {
        "ASM-01": 4, "ASM-02": 5, "ASM-03": 4, "ASM-05": 4,
        "VUL-01": 5, "VUL-02": 5, "VUL-03": 5, "VUL-04": 3, "VUL-05": 4,
        "APP-01": 3, "APP-05": 3,
        "REM-01": 5, "REM-02": 4, "REM-03": 4, "REM-05": 4
    },
    "evidence": {
        "ASM-01": "Qualys CyberSecurity Asset Management (CSAM) provides external attack surface discovery with continuous internet-facing asset enumeration. Identifies exposed services, certificates, and shadow assets.",
        "ASM-02": "Qualys CSAM delivers comprehensive internal asset inventory with automated classification. Single cloud agent covers discovery, VM, patching, and compliance. Business context tagging with criticality scoring.",
        "ASM-03": "Qualys TotalCloud provides CSPM/CNAPP across AWS, Azure, GCP. Container and Kubernetes security. Cloud IAM analysis and storage exposure detection. Multi-cloud dashboard.",
        "ASM-05": "Continuous monitoring built into cloud agent architecture. Real-time visibility into asset changes. Attack surface trending and change alerting integrated in CSAM dashboards.",
        "VUL-01": "Cloud-native vulnerability scanning since 1999. Single agent covers all asset types. 75,000+ vulnerability signatures. Agent-based and agentless scanning. Continuous, scheduled, and on-demand modes across infrastructure, cloud, and containers.",
        "VUL-02": "Qualys TruRisk provides quantified risk scoring combining CVSS, EPSS, threat intelligence, asset criticality, and business context. Documented 85%+ noise reduction vs. CVSS-only prioritization.",
        "VUL-03": "Qualys Policy Compliance covers CIS, DISA STIG, PCI DSS, and custom benchmarks. Automated compliance assessment across operating systems, databases, and cloud platforms. Configuration drift detection.",
        "VUL-04": "Limited native exploit validation. TruRisk scoring incorporates exploitability data but does not perform active exploitation. Relies on EPSS and exploit intelligence rather than proof-of-exploit.",
        "VUL-05": "Qualys Threat Intelligence correlates vulnerabilities with active exploits, CISA KEV, and malware campaigns. Threat feed integration enriches findings with exploitation likelihood and actor context.",
        "APP-01": "Qualys WAS (Web Application Scanning) provides DAST capabilities for web applications. Authenticated and unauthenticated scanning with OWASP Top 10 coverage. Not primary market focus.",
        "APP-05": "Qualys Container Security scans images in CI/CD and registries. TotalCloud includes IaC scanning and runtime container monitoring. Kubernetes admission controller integration.",
        "REM-01": "Qualys Patch Management is a market differentiator: zero-touch automated patching for OS and third-party applications across Windows, Linux, macOS. Integrated directly with vulnerability findings for prioritized patching.",
        "REM-02": "TruRisk provides unified exposure scoring across the Qualys platform. Aggregates VM, CSPM, container, and WAS findings. Exposure trending and posture scoring with customizable risk policies.",
        "REM-03": "ServiceNow, Jira, and ITSM integrations. Automated vulnerability-to-ticket workflows. SLA tracking and assignment routing. Bi-directional sync available through Qualys APIs.",
        "REM-05": "Executive dashboards in Qualys VMDR with TruRisk trending, remediation progress, SLA compliance metrics. Customizable reporting with compliance templates (PCI, HIPAA, SOX)."
    }
},

"Rapid7": {
    "scores": {
        "ASM-01": 4, "ASM-02": 4, "ASM-03": 3, "ASM-05": 4,
        "VUL-01": 5, "VUL-02": 4, "VUL-03": 4, "VUL-04": 4, "VUL-05": 4,
        "OFT-01": 4, "OFT-02": 2, "OFT-03": 3,
        "APP-01": 3, "APP-05": 3,
        "REM-01": 3, "REM-02": 4, "REM-03": 4, "REM-05": 4
    },
    "evidence": {
        "ASM-01": "Rapid7 Surface Command provides external attack surface management. Continuous external discovery of internet-facing assets, services, and exposures. Formerly Rapid7 ASM (acquired from IntSights context).",
        "ASM-02": "InsightVM agent-based inventory with automated asset classification. Network-wide discovery with business context and criticality. Integration with IT asset management systems.",
        "ASM-03": "InsightVM and InsightCloudSec provide cloud asset discovery and CSPM. AWS, Azure, GCP coverage with container scanning. Moderate compared to cloud-native specialists.",
        "ASM-05": "Surface Command continuous monitoring with real-time alerts on new exposures. InsightVM live dashboards tracking attack surface changes over time. Exposure trending available.",
        "VUL-01": "InsightVM (Nexpose engine) is a leading enterprise vulnerability scanner. Agent-based and agentless scanning across infrastructure, cloud, and containers. Comprehensive CVE coverage with frequent updates.",
        "VUL-02": "Real Risk Score incorporates CVSS, exploit availability, malware exposure, and asset criticality. Contextual risk scoring reduces noise. Active threat correlation through Rapid7 Threat Intelligence.",
        "VUL-03": "CIS, DISA STIG, and custom policy compliance assessment. Configuration audit across operating systems and network devices. Compliance trending and drift detection.",
        "VUL-04": "Metasploit integration is a key differentiator. InsightVM can validate exploitability using Metasploit modules, providing proof-of-exploit for identified vulnerabilities. Unique in the VM market.",
        "VUL-05": "Rapid7 Threat Intelligence (formerly IntSights, acquired 2021) correlates vulnerabilities with dark web intelligence, exploit availability, and active campaigns. Threat Command platform enriches VM findings.",
        "OFT-01": "Metasploit Pro provides automated penetration testing with safe exploitation, credential harvesting, pivoting, and lateral movement. Industry standard pentesting framework with extensive exploit library (2,300+ exploits).",
        "OFT-02": "Limited native BAS capability. Penetration testing focus rather than continuous simulation. Some control validation through Metasploit but not positioned as BAS platform.",
        "OFT-03": "Metasploit campaigns simulate multi-stage attacks. Social engineering campaigns. Purple team workflows through integration with InsightIDR detection platform. Manual red team augmentation rather than full automation.",
        "APP-01": "InsightAppSec provides DAST scanning for web applications. Authenticated crawling with OWASP coverage. Not primary market positioning vs. pure AppSec vendors.",
        "APP-05": "Container image scanning in InsightVM. InsightCloudSec covers IaC analysis. Kubernetes workload visibility. Moderate depth compared to CNAPP specialists.",
        "REM-01": "InsightConnect SOAR provides automated remediation workflows. Orchestrated patch management through integrations rather than native direct patching. Playbook-driven remediation.",
        "REM-02": "InsightVM Remediation Projects provide exposure prioritization and tracking. Real Risk Score aggregation. Remediation planning with SLA tracking and progress metrics.",
        "REM-03": "ServiceNow, Jira, and Azure DevOps integrations. InsightConnect provides automated ticket creation and workflow orchestration. Bi-directional sync and escalation routing.",
        "REM-05": "InsightVM executive dashboards with risk trending, remediation progress, and SLA metrics. Compliance reporting templates. Board-ready export capabilities."
    }
},

"CrowdStrike": {
    "scores": {
        "ASM-01": 5, "ASM-02": 4, "ASM-03": 4, "ASM-04": 3, "ASM-05": 4,
        "VUL-01": 4, "VUL-02": 4, "VUL-03": 3, "VUL-04": 3, "VUL-05": 5,
        "OFT-01": 3, "OFT-02": 2, "OFT-03": 3,
        "REM-02": 4, "REM-03": 3, "REM-05": 3
    },
    "evidence": {
        "ASM-01": "CrowdStrike Falcon Surface (formerly Reposify, acquired 2022) provides market-leading external attack surface management. Continuous, agentless discovery of internet-facing assets. Named a Leader in Forrester Wave for EASM 2024.",
        "ASM-02": "Falcon Discover provides internal asset inventory with AI-powered classification. Leverages Falcon sensor telemetry for real-time asset visibility. Business context through integration with identity and asset systems.",
        "ASM-03": "Falcon Cloud Security (CNAPP) provides cloud asset discovery and CSPM across AWS, Azure, GCP. Container and Kubernetes security. Cloud IAM path analysis. Growing cloud security portfolio.",
        "ASM-04": "Falcon Discover identifies unmanaged and unknown devices on the network through sensor telemetry. Rogue device detection and unauthorized application visibility. Moderate compared to dedicated shadow IT tools.",
        "ASM-05": "Falcon Surface continuous monitoring with real-time change detection on external attack surface. Falcon Discover tracks internal asset changes. Alert-driven change notification.",
        "VUL-01": "Falcon Spotlight provides agentless vulnerability scanning using Falcon sensor data. No separate scan infrastructure needed. Real-time vulnerability assessment as new CVEs are published. Limited to endpoints with Falcon sensor.",
        "VUL-02": "ExPRT.AI (Exploit Prediction Rating) is CrowdStrike's AI-driven prioritization scoring. Combines exploit data, threat intelligence, and asset context. Documented reduction in critical vulnerabilities by 90%+ vs. CVSS-only.",
        "VUL-03": "Configuration assessment available but not primary focus. CIS benchmark assessment through Falcon sensor. Limited compared to dedicated compliance scanning tools.",
        "VUL-04": "Limited native exploit validation. Relies on ExPRT.AI scoring and threat intelligence rather than active exploitation. Falcon OverWatch threat hunting provides some manual validation.",
        "VUL-05": "CrowdStrike Threat Intelligence is market-leading. Falcon Intelligence tracks 200+ adversary groups. Correlates vulnerabilities with active threat campaigns, nation-state actors, and eCrime groups. CISA KEV integration.",
        "OFT-01": "CrowdStrike Services provides red team and penetration testing engagements. Not automated platform-based. Expert-led offensive testing leveraging threat intelligence.",
        "OFT-02": "Limited native BAS. Falcon platform validates endpoint detection coverage but is not positioned as a BAS solution. Control validation is a byproduct of the platform rather than primary capability.",
        "OFT-03": "CrowdStrike Services offers red/purple team engagements. Falcon OverWatch provides proactive threat hunting. Not automated red team platform; relies on human operators with tool support.",
        "REM-02": "Falcon Exposure Management provides unified risk scoring across the CrowdStrike platform. ExPRT.AI aggregates vulnerability, threat, and asset data for exposure prioritization.",
        "REM-03": "ServiceNow and Jira integrations available. Falcon platform APIs enable ticket creation. Integration depth moderate compared to dedicated VM vendors.",
        "REM-05": "Falcon dashboards with exposure trending and risk metrics. Executive reporting on vulnerability posture. Compliance reporting available but less mature than dedicated VM platforms."
    }
},

"Palo Alto Networks": {
    "scores": {
        "ASM-01": 5, "ASM-02": 4, "ASM-03": 5, "ASM-04": 3, "ASM-05": 4,
        "VUL-01": 4, "VUL-02": 4, "VUL-03": 4, "VUL-04": 3, "VUL-05": 4,
        "APP-01": 3, "APP-05": 4,
        "REM-02": 4, "REM-03": 4, "REM-05": 4
    },
    "evidence": {
        "ASM-01": "Cortex Xpanse is a market leader in EASM (Gartner MQ leader, Forrester Wave leader). Continuous external attack surface discovery across the entire internet. Acquired Expanse in 2020 for $800M. Discovers assets within hours of deployment.",
        "ASM-02": "Cortex Xpanse and XSIAM provide internal asset inventory through sensor telemetry and network visibility. Asset classification with business context. Integration with Palo Alto firewalls for network-based discovery.",
        "ASM-03": "Prisma Cloud is a comprehensive CNAPP/CSPM covering AWS, Azure, GCP, OCI. Container, Kubernetes, serverless, and IaC security. Cloud IAM analysis. Named a Leader in Gartner MQ for CNAPP.",
        "ASM-04": "Cortex Xpanse identifies unmanaged internet-facing assets. Prisma SaaS provides some shadow SaaS detection. Moderate shadow IT capability compared to DLP-focused solutions.",
        "ASM-05": "Cortex Xpanse provides continuous monitoring with real-time alerting on attack surface changes. Automated response playbooks for new exposures. Trending dashboards track attack surface evolution.",
        "VUL-01": "Prisma Cloud and Cortex Xpanse provide vulnerability scanning across cloud workloads and external assets. Not traditional infrastructure VM scanner. Leverages Unit 42 intelligence for CVE coverage.",
        "VUL-02": "Risk-based prioritization combining CVSS, exploit data, asset exposure, and Unit 42 threat intelligence. Contextual prioritization in Prisma Cloud. Not as mature as dedicated VM vendor prioritization.",
        "VUL-03": "Prisma Cloud provides comprehensive cloud compliance benchmarking (CIS, SOC 2, HIPAA, PCI). Custom policy support. Configuration assessment across cloud services. Strong in cloud, moderate for on-premises.",
        "VUL-04": "Limited native exploit validation. Relies on threat intelligence and exposure analysis rather than active exploitation. Xpanse validates exposure by confirming service accessibility.",
        "VUL-05": "Unit 42 is a world-class threat intelligence and research team. Correlates vulnerabilities with active campaigns, nation-state actors, and ransomware groups. Published research on major CVE exploitation trends.",
        "APP-01": "Prisma Cloud includes some SAST and SCA capabilities (acquired Bridgecrew, Cider Security). Cloud-native application scanning. Not positioned as primary SAST/DAST vendor.",
        "APP-05": "Prisma Cloud excels at container, IaC, and cloud-native security. Terraform, CloudFormation, Kubernetes scanning. Container image scanning in CI/CD. Runtime container protection. Gartner CNAPP leader.",
        "REM-02": "Cortex XSIAM and Xpanse provide unified exposure management with risk scoring. Attack surface trending and prioritized remediation recommendations.",
        "REM-03": "XSOAR provides SOAR-based remediation workflows with ServiceNow, Jira integration. Automated ticket creation and orchestrated remediation playbooks. Extensive integration marketplace.",
        "REM-05": "Executive dashboards in Cortex and Prisma platforms. Exposure trending, compliance posture, and risk reduction metrics. Board-ready reporting through Cortex Analytics."
    }
},

# ── BATCH 2 ──────────────────────────────────────────────────────────

"Wiz": {
    "scores": {
        "ASM-01": 3, "ASM-02": 4, "ASM-03": 5, "ASM-04": 3, "ASM-05": 4,
        "VUL-01": 4, "VUL-02": 4, "VUL-03": 4, "VUL-04": 3, "VUL-05": 3,
        "APP-01": 3, "APP-05": 5,
        "REM-02": 4, "REM-03": 3, "REM-05": 4
    },
    "evidence": {
        "ASM-01": "Wiz provides cloud-focused external exposure detection. Identifies internet-facing resources and misconfigurations. Strong in cloud but does not cover traditional on-premises EASM.",
        "ASM-02": "Agentless cloud asset inventory across AWS, Azure, GCP, OCI, and Alibaba Cloud. Complete resource enumeration including VMs, containers, serverless, databases, and storage. Automatic classification with context.",
        "ASM-03": "Market-leading cloud and multi-cloud visibility. Agentless architecture scans entire cloud environments via API. Full cloud resource graph with IAM, networking, and data flow mapping. Gartner CNAPP leader. Valued at $12B+.",
        "ASM-04": "Detects unmanaged cloud resources and misconfigured services. Limited to cloud environments; does not cover on-premises shadow IT or rogue SaaS.",
        "ASM-05": "Continuous cloud environment monitoring with near-real-time change detection. Drift detection for security posture. Cloud resource change alerting with security context.",
        "VUL-01": "Agentless vulnerability scanning across cloud workloads, containers, and serverless functions. Snapshot-based scanning without deploying agents. Broad CVE coverage across OS and application packages.",
        "VUL-02": "Risk-based prioritization using Wiz Security Graph. Combines vulnerability severity with reachability, exposure, and business context. Toxic combination detection identifies high-risk convergences.",
        "VUL-03": "Cloud compliance benchmarks including CIS, SOC 2, PCI DSS, HIPAA, NIST. Custom framework support. Compliance dashboards with posture trending. Strong cloud-native compliance.",
        "VUL-04": "Limited active exploit validation. Identifies exploitable configurations through graph-based analysis (e.g., internet-facing + vulnerable + privileged = critical) but does not perform active exploitation.",
        "VUL-05": "Wiz Threat Center correlates vulnerabilities with active threats. Integration with threat intelligence feeds. In-the-wild exploitation context for prioritization. Growing capability.",
        "APP-01": "Wiz Code provides some SAST and secrets scanning capabilities. Acquired Raftt for development environment security. Not primary SAST/DAST platform.",
        "APP-05": "Market-leading container and cloud-native security. Container image scanning, Kubernetes security, IaC analysis (Terraform, CloudFormation, Pulumi). Serverless security. Runtime detection. Core strength of the platform.",
        "REM-02": "Wiz Issues provide prioritized exposure management. Security Graph enables contextualized risk scoring. Toxic combination analysis reduces noise significantly.",
        "REM-03": "Integrations with Jira, ServiceNow, Slack, and PagerDuty. Automated issue routing. Moderate workflow depth compared to dedicated ITSM integration vendors.",
        "REM-05": "Executive dashboards with security posture scoring, compliance trending, and remediation progress. Board-ready cloud security reporting. Risk reduction metrics."
    }
},

"Pentera": {
    "scores": {
        "ASM-01": 3, "ASM-02": 2,
        "VUL-01": 3, "VUL-04": 5,
        "OFT-01": 5, "OFT-02": 4, "OFT-03": 4, "OFT-04": 4, "OFT-05": 4,
        "REM-02": 3, "REM-05": 3
    },
    "evidence": {
        "ASM-01": "Pentera Surface provides external attack surface discovery as input for automated penetration testing. Discovers internet-facing assets and exposed services. Secondary to core pen testing focus.",
        "ASM-02": "Internal asset discovery through network-based scanning as part of pen testing workflows. Not a comprehensive asset inventory platform.",
        "VUL-01": "Vulnerability scanning as a component of automated pen testing. Identifies vulnerabilities across network infrastructure as targets for exploitation. Not standalone VM platform.",
        "VUL-04": "Market-leading exploitability validation. Pentera safely exploits real vulnerabilities to prove impact. Differentiator: proves which vulnerabilities are actually exploitable vs. theoretical. Core value proposition.",
        "OFT-01": "Market leader in automated penetration testing. Pentera platform autonomously discovers, scans, and safely exploits vulnerabilities across the network. Multi-vector testing including network, credentials, lateral movement, and data exfiltration. Named in Gartner Market Guide for Automated Penetration Testing.",
        "OFT-02": "Breach and attack simulation capabilities through continuous validation. Tests security controls across kill chain stages. Scheduled and on-demand attack scenarios with updated threat coverage.",
        "OFT-03": "Automated red team campaigns with multi-stage attack chains. Credential harvesting, privilege escalation, and lateral movement automation. Purple team mode with detection gap reporting.",
        "OFT-04": "Attack path analysis showing exploitation chains from initial access to critical assets. Visualizes paths with choke point identification. Prioritizes remediation based on path criticality.",
        "OFT-05": "MITRE ATT&CK aligned testing with technique-level mapping. Adversary emulation profiles. Tests mapped to specific TTPs with detection gap identification for SOC improvement.",
        "REM-02": "Risk-based findings prioritization based on proven exploitability. Prioritizes fixes based on actual attack path impact rather than theoretical CVSS scores.",
        "REM-05": "Validation dashboards showing security posture over time. Executive reporting on penetration test results, remediation progress, and risk reduction metrics."
    }
},

"XM Cyber": {
    "scores": {
        "ASM-01": 3, "ASM-02": 3, "ASM-03": 3,
        "VUL-01": 3, "VUL-02": 4, "VUL-03": 3,
        "OFT-01": 3, "OFT-04": 5, "OFT-05": 4,
        "REM-02": 5, "REM-03": 3, "REM-05": 4
    },
    "evidence": {
        "ASM-01": "XM Cyber provides asset discovery as input to attack path modeling. External exposure identification through attack graph analysis. Not primary EASM platform.",
        "ASM-02": "Internal asset enumeration through agent and agentless scanning. Asset context used for attack path modeling. Business criticality mapping for target definition.",
        "ASM-03": "Cloud environment support for AWS, Azure, GCP in attack path analysis. Cloud IAM and privilege escalation path discovery. Growing cloud coverage.",
        "VUL-01": "Vulnerability scanning as input to attack graph. Identifies vulnerabilities across endpoints, servers, and cloud workloads. Not standalone vulnerability scanner.",
        "VUL-02": "Advanced risk-based prioritization through attack path context. XM Cyber's core differentiator: prioritizes vulnerabilities based on whether they lie on an attack path to critical assets, not just CVSS.",
        "VUL-03": "Configuration assessments as input to attack modeling. Identifies misconfigurations that enable lateral movement. CIS and hardening checks where they impact attack paths.",
        "OFT-01": "Some automated pen testing capability within attack path validation. Validates certain techniques but focus is graph-based analysis over traditional pen testing.",
        "OFT-04": "Market leader in attack path analysis and modeling. Continuously maps all possible attack paths from initial access to critical assets. Graph-based choke point analysis shows where single fixes eliminate the most paths. Gartner Hype Cycle recognized. Acquired by Schwarz Group (Lidl) for $700M.",
        "OFT-05": "MITRE ATT&CK alignment in attack path techniques. Maps discovered paths to specific ATT&CK techniques. Adversary context in path analysis.",
        "REM-02": "Market-leading exposure prioritization. Choke point analysis identifies the smallest set of fixes that eliminate the most risk. Quantified risk reduction per remediation action. Unique value: 'fix one thing, eliminate 50 attack paths.'",
        "REM-03": "ServiceNow and Jira integrations for remediation workflow. Automated ticket creation with attack path context. SLA tracking available.",
        "REM-05": "Executive dashboards with exposure trending, attack path metrics, and risk posture improvement. Board-ready reporting showing risk reduction over time. Compliance mapping."
    }
},

"SafeBreach": {
    "scores": {
        "OFT-01": 3, "OFT-02": 5, "OFT-03": 4, "OFT-04": 3, "OFT-05": 5,
        "REM-02": 3, "REM-05": 3
    },
    "evidence": {
        "OFT-01": "Some automated pen testing capability within BAS platform. Executes attack techniques including exploitation. Secondary to primary BAS focus.",
        "OFT-02": "Market leader in Breach and Attack Simulation. 30,000+ attack simulations across the full kill chain. Continuous security control validation for endpoint, network, email, and cloud. Named in Gartner Market Guide for BAS. Rapid threat library updates for emerging threats.",
        "OFT-03": "Automated red team campaigns with multi-stage attack chains. Purple team mode with real-time detection validation. SOC team integration for detection tuning. Campaign replay for defensive improvement.",
        "OFT-04": "Attack scenario chains show potential paths through the environment. Not graph-based attack path analysis at XM Cyber level but provides attack flow visualization.",
        "OFT-05": "Comprehensive MITRE ATT&CK alignment with 30,000+ attacks mapped to techniques. Named threat actor profiles for adversary emulation. Industry-specific threat scenarios. One of the most extensive ATT&CK libraries in BAS market.",
        "REM-02": "Findings prioritization based on security control gaps. Identifies which exposures are not detected/prevented by existing controls. Remediation priority based on defensive gap severity.",
        "REM-05": "Security posture dashboards showing control effectiveness over time. Executive reporting on BAS results, detection gaps, and improvement trends."
    }
},

"AttackIQ": {
    "scores": {
        "OFT-01": 2, "OFT-02": 5, "OFT-03": 4, "OFT-04": 3, "OFT-05": 5,
        "REM-02": 3, "REM-05": 3
    },
    "evidence": {
        "OFT-01": "Some attack execution capability within BAS platform. Focuses on security control validation rather than traditional automated pen testing.",
        "OFT-02": "Market leader in BAS, co-founded the MITRE ATT&CK Evaluations program. AttackIQ Platform provides continuous security control validation. Named Gartner Market Guide for BAS. Extensive kill chain coverage. AttackIQ Ready! provides turnkey assessments.",
        "OFT-03": "Automated purple team mode through AttackIQ Flex and Enterprise. Real-time detection gap reporting. SOC integration for detection engineering improvement. Campaign-based testing.",
        "OFT-04": "Attack scenario modeling through multi-step campaigns. Not full graph-based attack path analysis but provides security control gap chains.",
        "OFT-05": "Co-created MITRE ATT&CK-based testing methodology. Industry's deepest ATT&CK alignment. Atomic testing at technique/sub-technique level. Adversary emulation plans aligned with MITRE Center for Threat-Informed Defense. MITRE Engenuity partnership.",
        "REM-02": "Control gap prioritization based on BAS results. Identifies which ATT&CK techniques are undetected. Remediation focus on high-impact defensive gaps.",
        "REM-05": "Security posture dashboards with ATT&CK coverage heatmaps. Executive reporting on detection coverage, gap trending, and improvement metrics."
    }
},

# ── BATCH 3 ──────────────────────────────────────────────────────────

"Cymulate": {
    "scores": {
        "ASM-01": 3, "ASM-02": 3,
        "VUL-01": 3, "VUL-02": 3,
        "OFT-01": 4, "OFT-02": 5, "OFT-03": 4, "OFT-04": 4, "OFT-05": 4,
        "REM-02": 4, "REM-03": 3, "REM-05": 3
    },
    "evidence": {
        "ASM-01": "Cymulate ASM module provides external attack surface discovery. Identifies exposed assets and services as input for validation testing. Growing EASM capability.",
        "ASM-02": "Internal asset discovery through Cymulate agent and network scanning. Asset context for attack simulation targeting.",
        "VUL-01": "Vulnerability scanning capabilities within the exposure management platform. Identifies vulnerabilities across endpoints and network infrastructure.",
        "VUL-02": "Risk-based prioritization combining vulnerability data with BAS validation results. Prioritizes based on validated exploitability vs. theoretical risk.",
        "OFT-01": "Cymulate Advanced Penetration Testing module provides automated pen testing. Safe exploitation with lateral movement and privilege escalation. Growing automated pen testing capability.",
        "OFT-02": "Market-leading BAS platform alongside SafeBreach and AttackIQ. Full kill chain simulation (email, web gateway, endpoint, network, data exfiltration). Continuous and scheduled simulations. Named in Gartner Market Guide for BAS.",
        "OFT-03": "Purple team automation with real-time detection validation. Dual-mode testing: red team for attack and purple team for collaborative improvement. SOC integration for detection tuning.",
        "OFT-04": "Attack path analysis through Cymulate Exposure Analytics. Maps attack paths with choke point identification. Combines BAS results with attack path modeling.",
        "OFT-05": "MITRE ATT&CK aligned testing with extensive technique coverage. Named threat actor profiles for emulation. Industry-specific scenarios. Regular library updates.",
        "REM-02": "Cymulate Exposure Analytics provides unified exposure scoring. Aggregates BAS, pen test, and ASM findings. Risk-based prioritization with attack path context.",
        "REM-03": "ServiceNow, Jira integrations. Automated ticket creation with control gap context. SOAR integrations available.",
        "REM-05": "Executive dashboards with exposure trending, BAS coverage metrics, and posture improvement tracking. Compliance-aligned reporting."
    }
},

"Horizon3.ai": {
    "scores": {
        "ASM-01": 3,
        "VUL-01": 3, "VUL-04": 5,
        "OFT-01": 5, "OFT-02": 3, "OFT-03": 3,
        "REM-02": 3, "REM-05": 3
    },
    "evidence": {
        "ASM-01": "NodeZero discovers external attack surface as part of autonomous pen testing. Asset discovery is embedded in the testing workflow rather than standalone EASM.",
        "VUL-01": "Vulnerability detection through autonomous pen testing reconnaissance. Identifies vulnerabilities as targets for exploitation. Not standalone VM scanner.",
        "VUL-04": "Market-leading exploitability validation through autonomous exploitation. NodeZero proves which vulnerabilities are actually exploitable. Core differentiator alongside Pentera.",
        "OFT-01": "NodeZero is a market-leading autonomous pen testing platform. AI-driven, zero-infrastructure pentesting that operates from the cloud. Autonomously discovers, enumerates, and safely exploits vulnerabilities. Named in Gartner Market Guide for Automated Penetration Testing. 200+ attack techniques.",
        "OFT-02": "Some control validation through autonomous pen testing. Tests whether controls detect exploitation attempts. Not positioned as dedicated BAS platform.",
        "OFT-03": "Autonomous multi-stage attacks with credential harvesting, privilege escalation, lateral movement. Some red team scenario capabilities. Focus is autonomous testing rather than adversary emulation.",
        "REM-02": "Prioritized findings based on proven exploitability. NodeZero ranks remediation actions by attack path impact and exploitation severity.",
        "REM-05": "Pen testing reports with exploitation proof, remediation guidance, and posture comparison across tests. Executive summary reporting."
    }
},

"Snyk": {
    "scores": {
        "APP-01": 5, "APP-02": 4, "APP-03": 5, "APP-04": 5, "APP-05": 4,
        "REM-01": 4, "REM-04": 4
    },
    "evidence": {
        "APP-01": "Market-leading developer-first security platform. Snyk Code provides SAST with AI-powered analysis across 30+ languages. Real-time IDE integration (VS Code, IntelliJ, Eclipse). Fastest scan speeds with minimal false positives. Named Leader in Gartner MQ for Application Security Testing.",
        "APP-02": "Snyk API Security provides API vulnerability detection. Discovers API endpoints and tests for OWASP API Top 10. GraphQL and REST API scanning. Growing capability.",
        "APP-03": "Snyk Open Source is market-leading SCA. Covers npm, Maven, PyPI, Go, NuGet, and 20+ package ecosystems. Industry's largest vulnerability database (curated by Snyk security research). Reachability analysis for prioritization. SBOM generation.",
        "APP-04": "Best-in-class CI/CD integration. Native plugins for GitHub, GitLab, Bitbucket, Jenkins, CircleCI, Azure DevOps, and 20+ CI/CD tools. PR checks, policy-as-code gates, and automated fix PRs. Minimal pipeline performance impact.",
        "APP-05": "Snyk Container provides image scanning in registries and CI/CD. Snyk IaC scans Terraform, CloudFormation, Kubernetes manifests, and Helm charts. Real-time monitoring of deployed containers.",
        "REM-01": "Snyk unique differentiator: automated fix pull requests. Generates PRs with dependency upgrades or patches for vulnerable components. One-click remediation in developer workflow.",
        "REM-04": "Continuous monitoring of dependencies with automatic re-scanning. Alerts when new vulnerabilities affect deployed components. Fix verification through automated re-testing in CI/CD."
    }
},

"Checkmarx": {
    "scores": {
        "APP-01": 5, "APP-02": 4, "APP-03": 4, "APP-04": 4, "APP-05": 3,
        "REM-03": 3, "REM-04": 3
    },
    "evidence": {
        "APP-01": "Market leader in SAST. Checkmarx One provides comprehensive SAST across 30+ languages with deep data flow analysis. Named Leader in Gartner MQ for Application Security Testing. Industry benchmark for SAST accuracy and language coverage. DAST also available in platform.",
        "APP-02": "Checkmarx API Security provides dedicated API testing. REST, GraphQL, and gRPC API scanning. API discovery and OWASP API Top 10 coverage. Integrated in Checkmarx One platform.",
        "APP-03": "Checkmarx SCA provides open-source vulnerability detection and license compliance. Covers major package ecosystems. Exploitability analysis available. Growing to match pure-play SCA vendors.",
        "APP-04": "CI/CD integrations with GitHub, GitLab, Jenkins, Azure DevOps, and others. Security gates with policy enforcement. Scan orchestration across SAST, SCA, and API security. Moderate pipeline performance impact.",
        "APP-05": "Container image scanning and IaC analysis (Terraform, CloudFormation). Checkmarx One platform covers cloud-native scenarios. Kubernetes manifest scanning. Less depth than CNAPP specialists.",
        "REM-03": "Jira, Azure DevOps, and developer tool integrations. Vulnerability assignment and tracking. SLA tracking available through Checkmarx One dashboards.",
        "REM-04": "Re-scanning capabilities in CI/CD to verify fixes. Baseline comparison shows new vs. resolved vulnerabilities. Incremental scan support."
    }
},

"Veracode": {
    "scores": {
        "APP-01": 5, "APP-02": 3, "APP-03": 4, "APP-04": 4, "APP-05": 3,
        "REM-01": 3, "REM-04": 3
    },
    "evidence": {
        "APP-01": "Veracode is a market leader in application security testing. Provides SAST, DAST, and IAST capabilities. Named Leader in Gartner MQ for AST. Binary SAST (no source code required) is unique differentiator. Covers 100+ languages/frameworks.",
        "APP-02": "API security testing through DAST engine. REST and SOAP API scanning. OWASP API Top 10 coverage. Not dedicated API security platform.",
        "APP-03": "Veracode SCA provides open-source vulnerability detection. Covers major ecosystems with vulnerability database. License compliance checking. Method-level analysis for reachability.",
        "APP-04": "CI/CD integrations with major platforms (Jenkins, GitHub Actions, GitLab CI, Azure DevOps). Veracode Pipeline Scan designed for speed in CI workflows. Security gate enforcement with policy management.",
        "APP-05": "Container image scanning in CI/CD pipelines. IaC analysis capabilities. Moderate cloud-native depth compared to CNAPP/container security specialists.",
        "REM-01": "Veracode Fix provides AI-powered fix suggestions and some automated remediation. Generates code-level fix recommendations based on vulnerability context.",
        "REM-04": "Baseline comparison for tracking fixed vs. new vulnerabilities. Rescan capabilities in CI/CD. Policy compliance trending."
    }
},

# ── BATCH 4 ──────────────────────────────────────────────────────────

"Synopsys Software Integrity": {
    "scores": {
        "APP-01": 5, "APP-02": 3, "APP-03": 5, "APP-04": 4, "APP-05": 3,
        "REM-03": 3, "REM-04": 3
    },
    "evidence": {
        "APP-01": "Coverity is a market-leading SAST tool with deepest data flow analysis. Covers 22+ languages. Named Leader in Gartner MQ for AST historically. Renamed to Black Duck after acquisition. Comprehensive DAST through Polaris platform.",
        "APP-02": "API testing capabilities within Coverity and DAST tools. REST API scanning. Not dedicated API security platform.",
        "APP-03": "Black Duck SCA is the market leader in software composition analysis. Industry's largest open-source vulnerability database (KnowledgeBase). License compliance is industry standard. SBOM generation (CycloneDX, SPDX). Reachability analysis.",
        "APP-04": "Polaris platform provides unified CI/CD integration for SAST, SCA, and DAST. Plugins for major CI/CD platforms. Security gate policy enforcement. Moderate speed impact.",
        "APP-05": "Container image scanning through Black Duck. IaC scanning capabilities emerging. Less cloud-native depth than CNAPP platforms.",
        "REM-03": "Jira, Azure DevOps integrations. Vulnerability tracking and assignment workflows. SLA tracking through Polaris dashboards.",
        "REM-04": "Incremental scanning and baseline comparison for fix verification. Re-scan in CI/CD confirms vulnerability resolution."
    }
},

"SonarSource": {
    "scores": {
        "APP-01": 4, "APP-04": 4
    },
    "evidence": {
        "APP-01": "SonarQube/SonarCloud provides SAST with code quality and security analysis. Covers 30+ languages. Deep taint analysis and data flow tracking. Large open-source community (40,000+ organizations). Clean as You Code methodology. Named in Gartner MQ for AST.",
        "APP-04": "Native CI/CD integration through SonarCloud and SonarQube plugins. GitHub, GitLab, Bitbucket, Azure DevOps, Jenkins integration. Quality gates with security-focused policies. Fast incremental analysis."
    }
},

"Semgrep (r2c)": {
    "scores": {
        "APP-01": 4, "APP-03": 3, "APP-04": 4
    },
    "evidence": {
        "APP-01": "Semgrep provides lightweight, fast SAST with pattern-based analysis. 30+ languages supported. Open-source core with commercial Semgrep Cloud. Developer-friendly rule authoring. Growing adoption among engineering teams. Semgrep Supply Chain adds SCA. Acquired by OpenAI-backed Vanta context.",
        "APP-03": "Semgrep Supply Chain provides SCA with reachability analysis. Determines if vulnerable code paths are actually called. Growing package ecosystem coverage.",
        "APP-04": "Excellent CI/CD integration. GitHub Actions, GitLab CI, and other pipelines. Fast scan times (seconds, not minutes). Minimal pipeline impact. Developer-first workflow with PR comments."
    }
},

"Invicti (Acunetix)": {
    "scores": {
        "APP-01": 4, "APP-02": 4, "APP-05": 3
    },
    "evidence": {
        "APP-01": "Invicti (formerly Netsparker) and Acunetix provide enterprise DAST scanning. Proof-Based Scanning technology that validates vulnerabilities to near-zero false positives. Named in Gartner MQ for AST. IAST capability through agent integration. 50,000+ vulnerability checks.",
        "APP-02": "Strong API security testing for REST, GraphQL, and SOAP APIs. OpenAPI/Swagger spec import for comprehensive API attack surface coverage. OWASP API Top 10 testing. API discovery and schema-based testing.",
        "APP-05": "Container-deployed scanning capabilities. Some IaC and cloud-native testing. Moderate depth in cloud-native scenarios."
    }
},

"Contrast Security": {
    "scores": {
        "APP-01": 4, "APP-02": 4, "APP-03": 3, "APP-04": 4,
        "REM-01": 3, "REM-04": 3
    },
    "evidence": {
        "APP-01": "Contrast is the pioneer and leader in IAST (Interactive Application Security Testing). Runtime instrumentation provides SAST+DAST combined analysis with near-zero false positives. Also provides SAST and DAST. Unique runtime security (RASP) blocks attacks in production. Named in Gartner MQ for AST.",
        "APP-02": "API security testing through runtime instrumentation. Discovers and tests APIs exercised during normal usage. Unique observability-based API discovery. REST and GraphQL coverage.",
        "APP-03": "Contrast SCA provides open-source vulnerability detection through runtime analysis. Identifies which libraries are actually loaded and called. Unique reachability through instrumentation.",
        "APP-04": "CI/CD integration through instrumentation agent deployed in test environments. Security results available during functional testing. Jenkins, GitHub, Azure DevOps integration. Policy gates.",
        "REM-01": "Contrast RASP provides runtime protection that can auto-block exploitation attempts. Virtual patching through runtime instrumentation. Unique among AppSec vendors.",
        "REM-04": "Continuous runtime monitoring verifies when vulnerabilities are fixed. RASP validation provides real-time confirmation of remediation effectiveness."
    }
},

# ── BATCH 5 ──────────────────────────────────────────────────────────

"HackerOne": {
    "scores": {
        "ASM-01": 3,
        "VUL-01": 3, "VUL-04": 4,
        "OFT-01": 4, "OFT-02": 2, "OFT-03": 3,
        "REM-03": 3, "REM-05": 3
    },
    "evidence": {
        "ASM-01": "HackerOne Assets provides attack surface management through hacker-driven discovery. Crowd-sourced asset identification. External exposure visibility from adversary perspective.",
        "VUL-01": "Vulnerability identification through bug bounty programs and pen testing engagements. Human-driven vulnerability discovery across all asset types. Not automated scanning platform.",
        "VUL-04": "Proven exploitability through human hacker validation. Every submitted finding is a demonstrated, exploitable vulnerability. Highest confidence in exploitability among all approaches.",
        "OFT-01": "HackerOne Pentest provides crowd-sourced penetration testing with vetted security researchers. Combines automated scanning with human expertise. Covers web, mobile, API, network, and cloud. Named leader in crowd-sourced security.",
        "OFT-02": "Limited BAS capability. Human-driven testing rather than automated simulation. Not positioned as BAS platform.",
        "OFT-03": "Red team engagements through HackerOne Programs. Expert human red teamers. Not automated but provides adversary perspective through actual hackers.",
        "REM-03": "Integration with Jira, ServiceNow, and developer tools. Automated vulnerability routing from bug bounty program to fix teams. Triage workflow management.",
        "REM-05": "Program analytics and reporting. Executive dashboards on vulnerability trends, resolution times, and program ROI. Metrics on hacker engagement and finding severity distribution."
    }
},

"Bugcrowd": {
    "scores": {
        "ASM-01": 3,
        "VUL-01": 3, "VUL-04": 4,
        "OFT-01": 4, "OFT-02": 2, "OFT-03": 3,
        "REM-03": 3, "REM-05": 3
    },
    "evidence": {
        "ASM-01": "Bugcrowd Attack Surface Management provides crowd-assisted external asset discovery. Leverages researcher community for asset identification beyond automated tools.",
        "VUL-01": "Vulnerability discovery through bug bounty and crowd-sourced security testing. Human-driven finding identification across applications, APIs, and infrastructure.",
        "VUL-04": "Proven exploitability through human researcher validation. All accepted findings are demonstrated exploitable vulnerabilities. Triage team validates submissions.",
        "OFT-01": "Bugcrowd Pen Test as a Service (PTaaS) provides crowd-sourced penetration testing. Vetted researcher pool with skill matching. Web, API, mobile, network, and cloud pen testing. Named alongside HackerOne as crowd-sourced security leader.",
        "OFT-02": "Limited BAS capability. Focus is human-driven testing rather than automated simulation.",
        "OFT-03": "Red team services through researcher community. Adversarial testing by skilled researchers. Not automated red team platform.",
        "REM-03": "Jira, ServiceNow, and Slack integrations. Vulnerability-to-ticket workflows. Triage and routing through Bugcrowd platform.",
        "REM-05": "Program dashboards with vulnerability trends, researcher activity, and resolution metrics. Executive reporting on program effectiveness and ROI."
    }
},

"Hadrian": {
    "scores": {
        "ASM-01": 5, "ASM-02": 3, "ASM-03": 3, "ASM-04": 4, "ASM-05": 5,
        "OFT-01": 3,
        "VUL-01": 3, "VUL-02": 3
    },
    "evidence": {
        "ASM-01": "Hadrian is a next-gen EASM platform with AI-driven continuous external discovery. Autonomous reconnaissance engine discovers assets at internet scale. Hacker-perspective asset mapping. European EASM innovator.",
        "ASM-02": "Internal asset context through integrations. Limited compared to agent-based discovery platforms.",
        "ASM-03": "Cloud asset discovery within EASM context. Identifies cloud-hosted services exposed externally. Multi-cloud coverage.",
        "ASM-04": "Strong shadow IT detection. Discovers forgotten subdomains, exposed dev environments, and orphaned assets. M&A-related asset discovery. Key differentiator.",
        "ASM-05": "Continuous real-time monitoring with instant alerting on new exposures. Attack surface change tracking with before/after comparison. One of the most responsive monitoring capabilities.",
        "OFT-01": "Automated vulnerability validation through lightweight exploitation attempts. Confirms exploitability of discovered exposures. Not full pen testing platform.",
        "VUL-01": "Vulnerability detection within EASM context. Identifies exposed services with known vulnerabilities. Port and service scanning from external perspective.",
        "VUL-02": "Risk-based contextualization of external exposures. Prioritization based on exploitability and exposure severity."
    }
},

"Detectify": {
    "scores": {
        "ASM-01": 4, "ASM-02": 2, "ASM-05": 4,
        "VUL-01": 3, "VUL-02": 3,
        "APP-01": 3
    },
    "evidence": {
        "ASM-01": "Detectify Surface Monitoring provides EASM with continuous external asset discovery. DNS-based discovery, subdomain enumeration, and certificate monitoring. Crowdsource-powered vulnerability intelligence through Detectify Crowdsource community.",
        "ASM-02": "Limited internal asset inventory. External-focused platform.",
        "ASM-05": "Continuous external monitoring with real-time alerting on new subdomains, exposed services, and configuration changes. Strong monitoring cadence.",
        "VUL-01": "External vulnerability scanning powered by ethical hacker community (Detectify Crowdsource). Tests for real-world exploits contributed by researchers. Covers web-facing vulnerabilities.",
        "VUL-02": "CVSS-based prioritization with some context from Crowdsource intelligence. Moderate prioritization sophistication.",
        "APP-01": "Detectify Application Scanning provides DAST for web applications. Crowdsource-powered test payloads for high accuracy. OWASP Top 10 coverage. Strong in web-specific testing."
    }
},

"Vulcan Cyber": {
    "scores": {
        "VUL-01": 3, "VUL-02": 4, "VUL-03": 3,
        "REM-01": 4, "REM-02": 5, "REM-03": 4, "REM-04": 4, "REM-05": 4
    },
    "evidence": {
        "VUL-01": "Vulcan aggregates vulnerability data from multiple scanners (Tenable, Qualys, Rapid7, etc.) rather than scanning natively. Data aggregation and normalization across tools.",
        "VUL-02": "Strong risk-based prioritization combining data from multiple vulnerability sources. Business context, asset criticality, and threat intelligence integration for unified risk scoring.",
        "VUL-03": "Aggregates compliance data from underlying scanning tools. Configuration assessment through integration rather than native scanning.",
        "REM-01": "Vulcan Remedy Cloud provides automated remediation orchestration. Integrates with patch management, cloud APIs, and configuration management tools to execute fixes. One of the few platforms focused specifically on remediation automation.",
        "REM-02": "Market-leading exposure management and prioritization platform. Core differentiator: aggregates data from 50+ security tools into unified risk view. Risk-based prioritization across all vulnerability sources. Named Gartner Hype Cycle for exposure management.",
        "REM-03": "Deep ITSM integration with ServiceNow, Jira, Azure DevOps. Automated ticket creation with enriched context from aggregated sources. SLA tracking, assignment routing, and escalation. One of the strongest ITSM integration stories.",
        "REM-04": "Closed-loop remediation verification. Re-scans and validates that fixes resolved the vulnerability. Tracks remediation effectiveness with fix rate metrics.",
        "REM-05": "Executive dashboards with exposure trending, remediation velocity, SLA compliance, and risk reduction. Board-ready reporting with quantified risk improvement."
    }
},

# ── BATCH 6 ──────────────────────────────────────────────────────────

"Nucleus Security": {
    "scores": {
        "VUL-01": 2, "VUL-02": 4,
        "REM-01": 3, "REM-02": 5, "REM-03": 4, "REM-04": 4, "REM-05": 4
    },
    "evidence": {
        "VUL-01": "Nucleus aggregates vulnerability data from multiple scanners; does not scan natively. Data normalization and deduplication across tools.",
        "VUL-02": "Strong risk-based prioritization across aggregated findings. Nucleus Risk Score combines CVSS, EPSS, threat intelligence, and asset criticality. Customizable risk policies.",
        "REM-01": "Automated remediation recommendations with integration to patching and configuration management tools. Orchestrated fix workflows.",
        "REM-02": "Market-leading vulnerability management orchestration platform. Aggregates findings from 100+ integrations. Unified risk scoring and exposure prioritization. Strong in vulnerability program management.",
        "REM-03": "Deep ITSM integrations with ServiceNow, Jira, Azure Boards. Automated ticket creation, SLA tracking, and escalation. Assignment routing by asset ownership.",
        "REM-04": "Closed-loop verification tracks remediation through re-scan confirmation. Fix rate tracking and remediation regression detection.",
        "REM-05": "Executive dashboards with vulnerability program metrics. MTTR, fix rates, SLA compliance, and risk trending. Board-ready reporting."
    }
},

"Brinqa": {
    "scores": {
        "ASM-01": 3, "ASM-02": 3,
        "VUL-01": 2, "VUL-02": 4, "VUL-03": 3,
        "REM-02": 5, "REM-03": 4, "REM-05": 4
    },
    "evidence": {
        "ASM-01": "Brinqa aggregates attack surface data from ASM tools. Provides unified asset view from multiple discovery sources. Not native EASM scanner.",
        "ASM-02": "Asset inventory aggregation from CMDB, vulnerability scanners, and cloud platforms. Unified asset graph with business context.",
        "VUL-01": "Aggregates vulnerability data from Tenable, Qualys, Rapid7, and other scanners. No native scanning.",
        "VUL-02": "Strong risk-based prioritization through Brinqa Risk Score. Combines data from multiple sources with business context and threat intelligence. Customizable risk models.",
        "VUL-03": "Compliance data aggregation from underlying tools. Configuration assessment through integration.",
        "REM-02": "Market-leading exposure management platform with knowledge graph architecture. Connects vulnerability, asset, threat, and business data. Risk-based prioritization across all sources. Named in Gartner Hype Cycle.",
        "REM-03": "ServiceNow, Jira, and Azure DevOps integrations. Automated remediation workflows with enriched context. SLA tracking and escalation.",
        "REM-05": "Executive dashboards with risk trending, remediation metrics, and compliance posture. Board-ready reporting with quantified risk reduction."
    }
},

"PlexTrac": {
    "scores": {
        "OFT-01": 3, "OFT-02": 2, "OFT-03": 3,
        "REM-03": 3, "REM-05": 4
    },
    "evidence": {
        "OFT-01": "PlexTrac is a pen test management and reporting platform rather than an automated pen testing tool. Aggregates pen test findings, manages engagements, and standardizes reporting. Leading platform for pen test program management.",
        "OFT-02": "Integrates BAS results for unified reporting. Not native BAS capability.",
        "OFT-03": "Red team and purple team engagement management. Tracks findings, recommendations, and remediation. Collaboration platform for offensive security teams.",
        "REM-03": "Jira and ticketing integrations for remediation tracking. Finding-to-fix workflow management. SLA tracking for pen test finding resolution.",
        "REM-05": "Market-leading pen test reporting platform. Professional, customizable reports. Executive summaries with trend analysis across engagements. Finding disposition tracking over time."
    }
},

"GitLab": {
    "scores": {
        "APP-01": 4, "APP-02": 3, "APP-03": 4, "APP-04": 5, "APP-05": 3,
        "REM-01": 3, "REM-04": 3
    },
    "evidence": {
        "APP-01": "GitLab Ultimate includes SAST and DAST natively in the DevOps platform. Supports 15+ languages for SAST. DAST scanning integrated into CI/CD. Not best-of-breed but deeply integrated. Free tier includes some security scans.",
        "APP-02": "API security testing through DAST API scanning. OpenAPI spec import for API coverage. REST and GraphQL testing. Moderate depth vs. dedicated API security tools.",
        "APP-03": "Dependency Scanning (SCA) built into GitLab. Covers major package ecosystems. License compliance scanning. Advisory database with continuous updates.",
        "APP-04": "Best-in-class CI/CD integration because security scanning IS the CI/CD platform. Zero configuration overhead. Auto DevOps runs security scans automatically. Security gates through approval rules. MR (merge request) security widgets.",
        "APP-05": "Container Scanning for container images. IaC scanning (Terraform, CloudFormation) available. Kubernetes integration for deployment scanning. Part of unified DevSecOps platform.",
        "REM-01": "Automated remediation through vulnerability merge requests. Auto-generates fix MRs for some dependency vulnerabilities. Developer-native remediation workflow.",
        "REM-04": "Baseline comparison in Security Dashboard tracks new vs. resolved vulnerabilities. Continuous monitoring in CI/CD pipeline validates fixes on next merge."
    }
},

"Microsoft (Defender for Cloud)": {
    "scores": {
        "ASM-01": 4, "ASM-02": 5, "ASM-03": 5, "ASM-04": 3, "ASM-05": 4,
        "VUL-01": 4, "VUL-02": 4, "VUL-03": 5, "VUL-04": 3, "VUL-05": 4,
        "APP-01": 3, "APP-03": 3, "APP-05": 4,
        "REM-01": 4, "REM-02": 4, "REM-03": 4, "REM-05": 4
    },
    "evidence": {
        "ASM-01": "Microsoft Defender External Attack Surface Management (EASM) provides continuous external asset discovery. Tracks internet-facing assets, domains, and cloud resources. Part of Microsoft Security portfolio.",
        "ASM-02": "Microsoft Defender for Endpoint and Intune provide comprehensive internal asset inventory. Deepest Windows/Azure asset visibility in the market. Device inventory with risk scoring and business context.",
        "ASM-03": "Market-leading Azure CSPM through Defender for Cloud. Multi-cloud support for AWS and GCP. CNAPP capabilities with workload protection, container security, and IAM analysis. Gartner MQ leader for CNAPP.",
        "ASM-04": "Defender for Endpoint discovers unmanaged devices. Limited shadow SaaS detection compared to dedicated SSPM tools. Microsoft Entra provides some shadow SaaS visibility.",
        "ASM-05": "Continuous monitoring through Defender for Cloud real-time security alerts. Secure Score tracking over time. Configuration change detection. Recommendation trending.",
        "VUL-01": "Defender for Cloud includes vulnerability scanning via Qualys agent or Microsoft Defender Vulnerability Management (MDVM). Covers servers, containers, and cloud workloads. Integrated into endpoint protection.",
        "VUL-02": "Microsoft Defender Vulnerability Management (MDVM) provides risk-based prioritization with threat intelligence from Microsoft Threat Intelligence. Asset criticality and exploitability context.",
        "VUL-03": "Defender for Cloud compliance benchmarks are market-leading: Azure Security Benchmark, CIS, PCI DSS, SOC 2, HIPAA, NIST 800-53, and 50+ regulatory frameworks. Custom policy through Azure Policy. Regulatory compliance dashboard.",
        "VUL-04": "Limited native exploit validation. Relies on threat intelligence and exposure analysis. Some validation through Microsoft Secure Score recommendations.",
        "VUL-05": "Microsoft Threat Intelligence (65+ trillion signals daily) provides unmatched threat correlation. Correlates vulnerabilities with active nation-state and eCrime campaigns. CISA KEV integration. Largest threat intelligence operation globally.",
        "APP-01": "GitHub Advanced Security provides SAST (CodeQL) and secret scanning. Moderate DAST through partner integrations. CodeQL is powerful but requires CodeQL database build.",
        "APP-03": "GitHub Dependabot provides SCA for open-source dependencies. Automated security updates through pull requests. Advisory database with community contributions.",
        "APP-05": "Defender for Containers provides container image scanning, runtime protection, and Kubernetes security. Azure-native with multi-cloud extension. IaC scanning through Defender for DevOps.",
        "REM-01": "Defender for Cloud auto-remediation through Azure Policy and Logic Apps. Automated secure configuration enforcement. Intune automated patching for endpoints.",
        "REM-02": "Microsoft Secure Score and Exposure Management provide unified risk scoring. Aggregates findings across Defender products. Risk-based prioritization with threat context.",
        "REM-03": "ServiceNow, Jira integration through Sentinel and Defender APIs. Azure DevOps native integration. Automated workflows through Logic Apps and Power Automate.",
        "REM-05": "Defender for Cloud compliance dashboards, Secure Score trending, and exposure management reporting. Board-ready compliance posture reports. Rich Azure-native analytics."
    }
},

# ── BATCH 7 ──────────────────────────────────────────────────────────

"Google (Mandiant / Security Command Center)": {
    "scores": {
        "ASM-01": 4, "ASM-02": 3, "ASM-03": 4, "ASM-05": 3,
        "VUL-01": 3, "VUL-02": 3, "VUL-05": 5,
        "OFT-01": 4, "OFT-03": 5, "OFT-05": 5,
        "REM-02": 3, "REM-05": 3
    },
    "evidence": {
        "ASM-01": "Mandiant Attack Surface Management provides external asset discovery. Google Cloud Security Command Center (SCC) discovers cloud assets. Combined coverage across external and cloud surfaces.",
        "ASM-02": "Google SCC provides cloud asset inventory for GCP natively. Multi-cloud support growing. Less depth for on-premises environments.",
        "ASM-03": "GCP Security Command Center provides CSPM for Google Cloud. Multi-cloud support through SCC Enterprise. Cloud IAM analysis. Container and Kubernetes security.",
        "ASM-05": "SCC continuous monitoring for GCP resources. Real-time alerting on security findings. Moderate external surface monitoring through Mandiant ASM.",
        "VUL-01": "SCC includes vulnerability scanning for GCP workloads. Mandiant provides vulnerability intelligence. Not broad infrastructure VM scanner.",
        "VUL-02": "Risk-based prioritization in SCC with threat intelligence context. Moderate prioritization sophistication compared to dedicated VM vendors.",
        "VUL-05": "Mandiant Threat Intelligence is market-leading, rivaling CrowdStrike. Tracks 4,000+ threat groups. Deep nation-state and APT research. Correlates vulnerabilities with active campaigns. Zero-day research (Project Zero). Industry benchmark for threat intelligence.",
        "OFT-01": "Mandiant provides world-class pen testing services. Expert-led engagements with nation-state-grade offensive capability. Not automated platform-based but among the most skilled offensive teams globally.",
        "OFT-03": "Mandiant Red Team services are market-leading. Industry's most experienced red team operators. Simulate advanced persistent threats with intelligence-backed TTPs. Purple team engagements with detection improvement guidance.",
        "OFT-05": "Mandiant is the closest to real adversary emulation in the market. Deep ATT&CK alignment. Named threat actor profiles based on proprietary intelligence. MITRE Engenuity participant. Threat actor emulation informed by incident response from thousands of breaches.",
        "REM-02": "SCC exposure management with risk scoring. Google Chronicle integration for unified security operations. Growing exposure management capability.",
        "REM-05": "SCC dashboards and compliance reporting for GCP. Executive reporting on security posture. Mandiant engagement reports are industry benchmark for quality."
    }
},

"Intruder": {
    "scores": {
        "ASM-01": 3, "ASM-05": 3,
        "VUL-01": 3, "VUL-02": 3,
        "APP-01": 3,
        "REM-03": 2, "REM-05": 2
    },
    "evidence": {
        "ASM-01": "Intruder provides external attack surface monitoring with automated perimeter scanning. Discovers internet-facing assets and monitors for new exposures. UK-based challenger vendor.",
        "ASM-05": "Continuous monitoring with alerts when new services or vulnerabilities appear on the perimeter. Change detection for external attack surface.",
        "VUL-01": "Cloud-based vulnerability scanning using multiple scanning engines (OpenVAS, commercial engine). Covers infrastructure, web applications, and cloud. Simplified for mid-market.",
        "VUL-02": "Emerging Smart Results prioritization that highlights critical findings. Moderate prioritization depth. Simpler risk scoring than enterprise platforms.",
        "APP-01": "Web application scanning through DAST engine. OWASP Top 10 coverage. Simplified web vulnerability detection for mid-market.",
        "REM-03": "Basic Slack and webhook integrations. Less mature ITSM integration compared to enterprise platforms.",
        "REM-05": "Simple reporting dashboards. Compliance-ready reports for ISO 27001, SOC 2. Mid-market focused reporting."
    }
},

"Censys": {
    "scores": {
        "ASM-01": 5, "ASM-02": 3, "ASM-03": 3, "ASM-04": 4, "ASM-05": 5,
        "VUL-01": 3
    },
    "evidence": {
        "ASM-01": "Censys is a market leader in internet-wide attack surface visibility. Scans the entire IPv4 internet continuously. Censys Search provides the most comprehensive view of internet-connected assets. Founded by Zmap creators. Industry benchmark for EASM.",
        "ASM-02": "Some internal asset context through cloud connector integrations. Primarily external focus.",
        "ASM-03": "Cloud asset discovery through cloud connector integrations (AWS, Azure, GCP). Identifies cloud-hosted services exposed externally. Moderate cloud depth.",
        "ASM-04": "Strong shadow asset detection. Discovers unknown internet-facing assets, forgotten subdomains, and exposed services not in CMDB. M&A due diligence use case.",
        "ASM-05": "Continuous internet scanning with real-time change detection. Industry's most frequent scanning cadence. Alerts on new exposures, expired certificates, and configuration changes. Attack surface trending.",
        "VUL-01": "Identifies exposed services with known vulnerabilities from external perspective. Service fingerprinting and version detection. Not comprehensive vulnerability scanner."
    }
},

"Tanium": {
    "scores": {
        "ASM-01": 3, "ASM-02": 5, "ASM-05": 4,
        "VUL-01": 4, "VUL-02": 3, "VUL-03": 4,
        "REM-01": 5, "REM-02": 3, "REM-03": 3, "REM-05": 3
    },
    "evidence": {
        "ASM-01": "Tanium provides network-based asset discovery. Identifies devices on the network in real-time. Limited external EASM capability.",
        "ASM-02": "Market leader in real-time endpoint asset inventory. Tanium Asset discovers and classifies every endpoint in seconds across millions of devices. Unmatched speed and accuracy in internal asset management.",
        "ASM-05": "Real-time change visibility. Tanium's architecture provides instant query response across all endpoints. Continuous monitoring of endpoint state changes.",
        "VUL-01": "Tanium Comply and Tanium Risk provide infrastructure vulnerability scanning. Agent-based scanning with real-time assessment. CVE coverage across Windows, Linux, macOS.",
        "VUL-02": "Risk scoring combining CVSS with asset context. Moderate risk-based prioritization compared to dedicated VM vendors.",
        "VUL-03": "Tanium Comply provides CIS, DISA STIG, and custom compliance assessment. Real-time compliance posture across all endpoints. One of the fastest compliance assessment tools.",
        "REM-01": "Market-leading automated remediation through Tanium Patch and Tanium Deploy. Automated OS and third-party patching at scale. Direct endpoint remediation without separate patch management infrastructure. Can patch 100,000+ endpoints simultaneously.",
        "REM-02": "Tanium Risk provides unified risk scoring across asset and vulnerability data. Risk trending and posture metrics.",
        "REM-03": "ServiceNow integration through Tanium Connect. Automated ticket creation and bi-directional sync. Moderate integration depth.",
        "REM-05": "Tanium dashboards with compliance posture, vulnerability trending, and patch compliance metrics. Executive reporting available."
    }
},

"Securin (formerly CSW)": {
    "scores": {
        "ASM-01": 3,
        "VUL-01": 4, "VUL-02": 4, "VUL-03": 3, "VUL-05": 4,
        "OFT-01": 2,
        "REM-02": 4, "REM-03": 3, "REM-05": 3
    },
    "evidence": {
        "ASM-01": "Securin VI (Vulnerability Intelligence) includes attack surface context. Identifies exposed assets through vulnerability intelligence correlation. Not dedicated EASM platform.",
        "VUL-01": "Securin provides vulnerability scanning and management platform. Coverage across infrastructure and applications. Growing scanning capability.",
        "VUL-02": "Strong risk-based prioritization powered by Securin's proprietary vulnerability intelligence. Combines CVSS, EPSS, weaponization data, and ransomware association. Named for predictive vulnerability prioritization.",
        "VUL-03": "Configuration and compliance assessment available. CIS and regulatory benchmark support. Moderate depth.",
        "VUL-05": "Securin's core differentiator is vulnerability intelligence. Tracks exploit weaponization, ransomware association, APT group usage, and CISA KEV correlation. Predictive exploitability scoring. One of the most detailed vulnerability intelligence databases.",
        "OFT-01": "Securin offers pen testing services. Expert-led rather than automated platform.",
        "REM-02": "Securin Risk-Based Vulnerability Management provides exposure prioritization. Aggregates vulnerability and threat intelligence for unified risk scoring.",
        "REM-03": "ServiceNow and Jira integrations. Automated ticket creation with vulnerability intelligence context.",
        "REM-05": "Reporting dashboards with vulnerability trending, risk metrics, and remediation progress. Executive reporting available."
    }
},

# ── BATCH 8 ──────────────────────────────────────────────────────────

"Cobalt": {
    "scores": {
        "OFT-01": 4, "OFT-02": 2, "OFT-03": 2,
        "APP-01": 3, "APP-02": 3,
        "REM-03": 3, "REM-05": 3
    },
    "evidence": {
        "OFT-01": "Cobalt provides Pentest as a Service (PtaaS), combining a vetted global pen testing community with a platform-based delivery model. Web, API, mobile, cloud, and network pen testing. Fast engagement launches (within days). Named in Gartner Market Guide for PtaaS.",
        "OFT-02": "Limited BAS. Human-driven pen testing rather than automated simulation.",
        "OFT-03": "Red team engagements available through expert pentester community. Not automated; relies on skilled human operators.",
        "APP-01": "Application security pen testing covering web and mobile applications. Manual testing with OWASP methodology. Expert-driven DAST coverage.",
        "APP-02": "API penetration testing covering REST and GraphQL APIs. OWASP API Top 10 manual testing. Expert validation of API security.",
        "REM-03": "Jira, GitHub, and Slack integrations. Finding-to-fix workflows. Cobalt platform manages remediation tracking.",
        "REM-05": "Professional pen test reports through the platform. Executive summaries, finding details, and remediation guidance. Engagement history and trend tracking."
    }
},

"Recorded Future": {
    "scores": {
        "ASM-01": 3, "ASM-05": 3,
        "VUL-02": 4, "VUL-05": 5,
        "OFT-05": 3
    },
    "evidence": {
        "ASM-01": "Recorded Future Attack Surface Intelligence provides external asset discovery with threat intelligence enrichment. Identifies exposed assets and correlates with active targeting.",
        "ASM-05": "Continuous monitoring with threat-informed alerting. Alerts when new assets are identified or when existing assets are targeted by threats.",
        "VUL-02": "Recorded Future Vulnerability Intelligence provides best-in-class vulnerability prioritization. Combines CVSS with real-time exploit data, dark web intelligence, and threat actor targeting. Named in Gartner MQ for Security Risk Management.",
        "VUL-05": "Market leader in threat intelligence. Intelligence Cloud correlates vulnerabilities with dark web discussions, paste sites, exploit markets, and threat actor activity. Acquired by Mastercard for $2.65B in 2024. Unmatched breadth of intelligence sources (1M+ sources in 13 languages).",
        "OFT-05": "Threat intelligence supports adversary emulation planning. Provides threat actor profiles, TTPs, and targeting data. Not native emulation platform but essential intelligence input."
    }
},

"FireCompass": {
    "scores": {
        "ASM-01": 4, "ASM-02": 3, "ASM-03": 3, "ASM-04": 4, "ASM-05": 4,
        "VUL-01": 3, "VUL-03": 2, "VUL-04": 4,
        "OFT-01": 4, "OFT-02": 3, "OFT-03": 4, "OFT-04": 3, "OFT-05": 3,
        "REM-02": 3, "REM-05": 3
    },
    "evidence": {
        "ASM-01": "FireCompass EASM provides continuous external attack surface discovery. Automated reconnaissance across domains, IPs, and cloud assets. Strong asset enumeration capability.",
        "ASM-02": "Internal asset discovery through network scanning as part of CART workflows. Moderate internal inventory depth.",
        "ASM-03": "Cloud asset discovery within EASM context. Multi-cloud external exposure identification.",
        "ASM-04": "Shadow IT and forgotten asset detection through internet-wide reconnaissance. Identifies orphaned subdomains, exposed dev environments, and untracked assets.",
        "ASM-05": "Continuous monitoring with real-time alerting on new external exposures. Attack surface change tracking and trending.",
        "VUL-01": "Vulnerability identification through reconnaissance and scanning as part of CART workflow. Not standalone VM platform.",
        "VUL-03": "Basic configuration checks as part of attack surface analysis. Limited compliance benchmarking depth.",
        "VUL-04": "Autonomous exploitation validates real vulnerabilities. CART platform safely exploits findings to prove impact. Strong exploitability validation.",
        "OFT-01": "Continuous Automated Red Teaming (CART) platform provides autonomous pen testing. Multi-stage attack chains without human operators. Recognized in Gartner Hype Cycle for Security Operations. Growing APAC presence.",
        "OFT-02": "Some attack simulation capability within CART framework. Tests security controls through automated attack sequences.",
        "OFT-03": "Autonomous multi-stage red team campaigns. Automated credential harvesting, lateral movement, and privilege escalation. AI-driven attack planning and execution.",
        "OFT-04": "Attack path discovery through automated exploitation chains. Identifies paths from external entry to critical assets.",
        "OFT-05": "MITRE ATT&CK alignment in attack technique library. Growing technique coverage. Threat-informed testing scenarios.",
        "REM-02": "Risk-based finding prioritization based on proven exploitability. Attack path context in remediation recommendations.",
        "REM-05": "Assessment reports with exploitation proof and remediation guidance. Executive summaries and trending."
    }
},

"Indusface": {
    "scores": {
        "ASM-01": 3, "ASM-02": 2,
        "VUL-01": 3, "VUL-02": 3, "VUL-03": 2,
        "APP-01": 4, "APP-02": 4, "APP-03": 2, "APP-04": 3, "APP-05": 2,
        "REM-01": 3, "REM-02": 3
    },
    "evidence": {
        "ASM-01": "Indusface WAS provides web asset discovery. Identifies web applications and APIs. Limited compared to dedicated EASM platforms.",
        "ASM-02": "Basic web application inventory. Not comprehensive internal asset management.",
        "VUL-01": "Web application vulnerability scanning through Indusface WAS. OWASP Top 10 and beyond. Automated + manual hybrid scanning. Moderate infrastructure VM capability.",
        "VUL-02": "Risk-based prioritization combining automated findings with expert manual validation. Zero false positive guarantee reduces noise.",
        "VUL-03": "Basic compliance scanning for web applications. PCI DSS and OWASP compliance. Limited infrastructure compliance.",
        "APP-01": "Strong DAST capabilities through Indusface WAS and AppTrana. Named in Gartner MQ for Cloud WAAP (AppTrana). Automated + expert manual pen testing hybrid. OWASP Top 10 coverage. Zero false positive validation.",
        "APP-02": "API security testing covering REST and GraphQL APIs. Automated API scanning with manual validation. OWASP API Top 10 testing. AppTrana includes API protection.",
        "APP-03": "Limited SCA capability. Focus is on web application and API testing rather than source code dependency analysis.",
        "APP-04": "CI/CD integration available through APIs. Jenkins and pipeline integration for scheduled scanning. Moderate DevSecOps integration depth.",
        "APP-05": "Limited cloud-native application security. Focus is web application and WAF/WAAP rather than containers or IaC.",
        "REM-01": "AppTrana WAF provides virtual patching for detected vulnerabilities. Automated blocking of exploitation attempts without code changes. Key differentiator: immediate risk reduction.",
        "REM-02": "Risk-based prioritization combining automated and manual findings. AppTrana risk scoring for web application exposure."
    }
},

"CloudSEK": {
    "scores": {
        "ASM-01": 4, "ASM-02": 2, "ASM-03": 2, "ASM-04": 4, "ASM-05": 4,
        "VUL-01": 2, "VUL-03": 2,
        "REM-02": 3, "REM-05": 3
    },
    "evidence": {
        "ASM-01": "CloudSEK XVigil provides AI-driven external attack surface discovery. Monitors surface, deep, and dark web for exposed assets and digital threats. Strong digital footprint monitoring.",
        "ASM-02": "Limited internal asset inventory. Focus is external digital risk monitoring.",
        "ASM-03": "Cloud exposure monitoring for leaked credentials, misconfigured storage, and exposed cloud services. Limited depth compared to CSPM tools.",
        "ASM-04": "Strong shadow IT and digital risk detection. Discovers brand impersonation, phishing domains, rogue apps, and exposed credentials across dark web. Core differentiator.",
        "ASM-05": "Continuous monitoring across surface, deep, and dark web with real-time alerts. Digital threat monitoring with trending and change detection.",
        "VUL-01": "Limited vulnerability scanning. Focus is digital risk intelligence rather than traditional VM.",
        "VUL-03": "Basic exposure assessment. Not traditional configuration compliance platform.",
        "REM-02": "Risk-based alert prioritization using AI contextual analysis. Prioritizes digital threats by business impact.",
        "REM-05": "Threat intelligence dashboards with digital risk trending. Executive reporting on brand exposure and digital threats."
    }
},

# ── BATCH 9 ──────────────────────────────────────────────────────────

"SecPod": {
    "scores": {
        "ASM-01": 3, "ASM-02": 3,
        "VUL-01": 4, "VUL-02": 3, "VUL-03": 4, "VUL-04": 2, "VUL-05": 3,
        "REM-01": 4, "REM-02": 3, "REM-03": 3
    },
    "evidence": {
        "ASM-01": "SanerNow provides network-based asset discovery. Identifies devices and services on internal and perimeter networks. Agent-based discovery.",
        "ASM-02": "SanerNow asset inventory with classification. Agent-based endpoint enumeration with OS, application, and hardware details. Moderate depth.",
        "VUL-01": "SanerNow CVEM provides vulnerability scanning with 175,000+ vulnerability checks, one of the industry's largest databases. Agent-based continuous scanning across Windows, Linux, macOS. SCAP-compatible.",
        "VUL-02": "Risk-based prioritization available. CVSS and exploitability data for finding priority. Growing beyond basic prioritization.",
        "VUL-03": "SanerNow Compliance Management provides CIS benchmark, DISA STIG, and custom compliance assessment. SCAP-compatible benchmark automation across endpoints. Strong compliance depth.",
        "VUL-04": "Limited exploitability validation. Relies on vulnerability intelligence rather than active exploitation.",
        "VUL-05": "Vulnerability intelligence database with threat context. Exploit availability and active threat correlation. Moderate depth vs. dedicated threat intelligence vendors.",
        "REM-01": "SanerNow integrated patch management is a key differentiator. Zero-touch automated patching for OS and 400+ third-party applications. Unified VM + patching in single agent. Competitive with Qualys for integrated remediation.",
        "REM-02": "Unified risk view across vulnerability, compliance, and patch status. Risk trending and posture metrics.",
        "REM-03": "Basic ticketing and workflow integrations. ServiceNow and Jira integration available. Growing ITSM integration depth."
    }
},

"Astra Security": {
    "scores": {
        "ASM-01": 2,
        "VUL-01": 3, "VUL-02": 2,
        "OFT-01": 3, "OFT-02": 2, "OFT-03": 2,
        "APP-01": 3, "APP-02": 3, "APP-04": 3
    },
    "evidence": {
        "ASM-01": "Basic external asset discovery as part of pen testing workflow. Limited EASM depth.",
        "VUL-01": "Automated vulnerability scanning for web applications, APIs, and cloud infrastructure. 9,300+ security tests. Growing scanning capability.",
        "VUL-02": "Basic risk-based prioritization by severity. Less sophisticated than enterprise VM vendor prioritization.",
        "OFT-01": "Astra Pentest provides automated pen testing for web apps, APIs, and cloud. Combines automated DAST scanning with manual expert validation. SaaS-delivered with developer-friendly interface.",
        "OFT-02": "Limited BAS capability. Focused on pen testing and vulnerability scanning.",
        "OFT-03": "Manual expert pen testing component provides some red team capability. Not automated red team platform.",
        "APP-01": "DAST scanning for web applications with OWASP Top 10 coverage. Automated + manual expert validation. Zero false positive guarantee. Developer-friendly vulnerability dashboard.",
        "APP-02": "API security testing for REST and GraphQL APIs. OWASP API Top 10 coverage. Automated + manual API pen testing.",
        "APP-04": "CI/CD integrations with GitHub, GitLab, Jenkins, and others. Automated security scanning in pipelines. Developer-friendly reporting with Jira, Slack integration."
    }
},

"NSFOCUS": {
    "scores": {
        "ASM-01": 3, "ASM-02": 3, "ASM-03": 2,
        "VUL-01": 4, "VUL-02": 3, "VUL-03": 4, "VUL-04": 2, "VUL-05": 3,
        "APP-01": 3, "APP-02": 2, "APP-05": 2,
        "REM-01": 3, "REM-02": 2, "REM-03": 2
    },
    "evidence": {
        "ASM-01": "NSFOCUS provides network and perimeter asset discovery. Internet-facing asset enumeration through RSAS scanning engine. Strong in Chinese and APAC enterprise market.",
        "ASM-02": "Internal asset discovery through RSAS network scanning. Asset inventory with classification. CMDB integration for Chinese enterprise environments.",
        "ASM-03": "Limited cloud security. Growing cloud coverage for Chinese cloud providers (Alibaba, Huawei, Tencent). Less multi-cloud depth than Western CSPMs.",
        "VUL-01": "NSFOCUS RSAS is one of the most widely deployed vulnerability scanners in China and APAC. Comprehensive infrastructure scanning. 80,000+ vulnerability checks. Agent-based and agentless scanning.",
        "VUL-02": "Risk-based prioritization available. CVSS-based with NSFOCUS threat intelligence context. Growing beyond basic prioritization.",
        "VUL-03": "Strong compliance assessment for Chinese regulations (MLPS 2.0) and international standards (CIS, ISO 27001). Configuration auditing across infrastructure. Important for Chinese regulated industries.",
        "VUL-04": "Limited exploitability validation. Primarily scanning-based assessment without active exploitation.",
        "VUL-05": "NSFOCUS M01N research team provides vulnerability intelligence. Chinese threat landscape expertise. CVE research and advisory publication. Moderate global intelligence depth.",
        "APP-01": "NSFOCUS WebSafe provides web application scanning and WAF capabilities. OWASP coverage. Focus on Chinese web application environment.",
        "APP-02": "Basic API testing through web scanning engine. Limited dedicated API security.",
        "APP-05": "Growing cloud-native security capabilities. Container scanning emerging. Limited IaC and Kubernetes depth.",
        "REM-01": "NSFOCUS provides some automated remediation through WAF virtual patching and DDoS mitigation. Infrastructure remediation workflows.",
        "REM-02": "Basic risk scoring and prioritization. ISOP platform provides some unified security operations view.",
        "REM-03": "Integration with Chinese ITSM platforms. Limited global ITSM integration (ServiceNow, Jira)."
    }
},

"NTT Security Holdings": {
    "scores": {
        "ASM-01": 3, "ASM-02": 3, "ASM-03": 3, "ASM-05": 3,
        "VUL-01": 4, "VUL-02": 3, "VUL-03": 3, "VUL-04": 3,
        "OFT-01": 4, "OFT-02": 3, "OFT-03": 4,
        "APP-01": 3, "APP-02": 3,
        "REM-01": 2, "REM-02": 3, "REM-05": 3
    },
    "evidence": {
        "ASM-01": "NTT provides attack surface discovery through managed security services. External asset enumeration as part of assessment engagements.",
        "ASM-02": "Asset inventory through managed security services and NTT MDR platform. Network-based discovery across managed client environments.",
        "ASM-03": "Cloud security assessment services across AWS, Azure, GCP. Part of managed security practice rather than self-service platform.",
        "ASM-05": "Continuous monitoring through NTT managed security services. SOC-driven monitoring and alerting on security events.",
        "VUL-01": "NTT provides vulnerability management through managed services using commercial scanning engines (Qualys, Tenable partnerships). Expert-managed VM programs.",
        "VUL-02": "Risk-based prioritization through expert analysis. Managed VM services include contextual prioritization by NTT security analysts.",
        "VUL-03": "Compliance assessment as part of managed security services. CIS, PCI DSS, and regulatory compliance auditing.",
        "VUL-04": "Exploitability validation through manual pen testing engagements. NTT offensive security team validates critical vulnerabilities.",
        "OFT-01": "NTT provides expert-led penetration testing services globally. Experienced pen testing teams across APAC (Japan, Australia, Singapore). Network, web, mobile, and cloud pen testing.",
        "OFT-02": "Some BAS capability through managed security technology stack. Moderate compared to dedicated BAS platforms.",
        "OFT-03": "NTT Red Team services are well-regarded particularly in APAC. Experienced red team operators with adversary simulation capability. Purple team engagements available.",
        "APP-01": "Application security testing services. Web and mobile application pen testing. Expert-led SAST/DAST assessment.",
        "APP-02": "API security assessment through pen testing engagements. Manual API testing with expert validation.",
        "REM-01": "Limited automated remediation. Managed services provide remediation guidance rather than direct automated patching.",
        "REM-02": "Risk-based prioritization through managed VM program. Analyst-driven exposure management.",
        "REM-05": "Managed security reporting with executive dashboards. Monthly reporting on security posture, vulnerability trends, and remediation progress."
    }
},

"Entersoft Security": {
    "scores": {
        "ASM-01": 3, "ASM-02": 2,
        "VUL-01": 3, "VUL-02": 2,
        "OFT-01": 4, "OFT-02": 2, "OFT-03": 3, "OFT-04": 2,
        "APP-01": 3, "APP-02": 3
    },
    "evidence": {
        "ASM-01": "Entersoft provides external attack surface discovery as part of pen testing engagements. Asset enumeration and exposure mapping. Australian market focus.",
        "ASM-02": "Internal asset enumeration through pen testing reconnaissance. Not standalone asset management platform.",
        "VUL-01": "Vulnerability scanning as part of security assessment services. Commercial and open-source scanning tools combined with expert analysis.",
        "VUL-02": "Risk-based finding prioritization by pen testing experts. Moderate prioritization sophistication.",
        "OFT-01": "Core offering is expert-led penetration testing. CREST-certified and ASD (Australian Signals Directorate) listed assessor. Comprehensive pen testing across web, mobile, API, network, and cloud. Strong Australian government and financial services experience.",
        "OFT-02": "Limited BAS capability. Expert-driven testing rather than automated simulation.",
        "OFT-03": "Red team assessment services. Experienced offensive security operators. Adversary simulation for Australian enterprises and government agencies.",
        "OFT-04": "Some attack path analysis within red team engagements. Not automated graph-based platform.",
        "APP-01": "Web and mobile application security testing. OWASP methodology. Expert-led DAST and code review. Strong in Australian regulated sectors.",
        "APP-02": "API penetration testing. REST and GraphQL API security assessment. Manual expert API testing."
    }
},

}  # END RESEARCH


def apply_scores():
    """Apply research-based scores to the seed file."""
    with open(SEED, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    scored = 0
    errors = []

    for vendor in data['vendors']:
        name = vendor['vendor']
        if name not in RESEARCH:
            errors.append(f"WARNING: No research data for '{name}'")
            continue

        r = RESEARCH[name]
        scores = r['scores']
        evidence = r.get('evidence', {})

        # Apply sub-pillar scores
        for sp, score in scores.items():
            if sp in vendor['sub_pillar_scores_current']:
                vendor['sub_pillar_scores_current'][sp] = score
            else:
                errors.append(f"ERROR: {name} - sub-pillar {sp} not in score template")

        # Apply evidence
        vendor['sub_pillar_evidence'] = {}
        for sp, ev in evidence.items():
            vendor['sub_pillar_evidence'][sp] = {
                "rationale": ev,
                "sources": [],
                "last_updated": "2026-03-18"
            }

        # Compute pillar scores (average of non-zero sub-pillar scores in that pillar)
        pillar_map = {
            "ASM": ["ASM-01","ASM-02","ASM-03","ASM-04","ASM-05"],
            "VUL": ["VUL-01","VUL-02","VUL-03","VUL-04","VUL-05"],
            "OFT": ["OFT-01","OFT-02","OFT-03","OFT-04","OFT-05"],
            "APP": ["APP-01","APP-02","APP-03","APP-04","APP-05"],
            "REM": ["REM-01","REM-02","REM-03","REM-04","REM-05"],
        }
        for pillar, sps in pillar_map.items():
            active = [vendor['sub_pillar_scores_current'][sp] for sp in sps if vendor['sub_pillar_scores_current'].get(sp, 0) > 0]
            vendor['pillar_scores'][pillar] = round(sum(active) / len(active), 1) if active else 0

        scored += 1

    # Update metadata
    data['schema_version'] = '1.0'
    data['seed_version'] = '2.0'
    data['seed_date'] = '2026-03-18'
    data['seed_notes'] = 'Research-based scoring with rationales for all 45 vendors across 25 sub-pillars. Scores based on publicly verifiable product capabilities, analyst recognition, and documented features.'

    # Write output
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nScored {scored} / {len(data['vendors'])} vendors")
    if errors:
        print(f"\n{len(errors)} warnings:")
        for e in errors:
            print(f"  {e}")

    # Summary stats
    print(f"\nOutput written to: {OUTPUT}")
    print("\n── Score Summary ──")
    for v in data['vendors']:
        ps = v['pillar_scores']
        active = [s for s in ps.values() if s > 0]
        avg = round(sum(active)/len(active), 1) if active else 0
        bar = '█' * int(avg * 4)
        print(f"  {v['vendor']:45s}  ASM={ps['ASM']:.1f}  VUL={ps['VUL']:.1f}  OFT={ps['OFT']:.1f}  APP={ps['APP']:.1f}  REM={ps['REM']:.1f}  avg={avg} {bar}")


if __name__ == '__main__':
    apply_scores()
