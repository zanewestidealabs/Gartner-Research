"""
Reclassify and re-score SVC sub-pillars based on delivery model distinction.

Core insight: SVC-03 (Managed Operations & Continuous Delivery) should evaluate
whether the VENDOR ITSELF delivers managed services to end clients — not whether
the vendor's platform can be used by MSSPs/partners to deliver services.

Delivery model taxonomy:
  direct_service  — Vendor directly delivers managed services with own SOC/analysts
  platform_plus_partner — Vendor provides platform; partners/MSSPs deliver managed ops
  platform_only   — No managed service delivery (vendor or partner); technology licensing only

Scoring adjustments by delivery model:
  SVC-01 (Implementation): Largely unaffected — professional services exist in all models
  SVC-02 (Advisory): Largely unaffected — consulting/advisory exists in all models
  SVC-03 (Managed Ops): MAJOR adjustment for platform vendors:
    - direct_service: score based on actual managed ops evidence
    - platform_plus_partner: cap at 2.0 (partner enablement, not direct delivery)
    - platform_only: cap at 1.0 (no managed service option)
  SVC-04 (AI/Autonomous): Adjust based on context:
    - Platform AI features ≠ AI in service delivery
    - AI in the product (e.g., VPR scoring) is EXM/ADR capability, not service delivery AI
"""
import json
import os
import copy
from datetime import datetime

VENDOR_FILE = "Preemptive Cybersecurity Vendor 3-0 SVC Pricing.json"

# ── Vendor delivery model classification ─────────────────────────────
# Based on public information about each vendor's service delivery model.
#
# direct_service: Vendor operates SOC, employs analysts, delivers outcome to client
# platform_plus_partner: Vendor sells platform; MSSP partners deliver managed services
# platform_only: No managed service option; technology licensing only

DELIVERY_MODEL = {
    # === Direct service providers ===
    "Arctic Wolf":         "direct_service",     # Concierge Security — vendor-operated SOC
    "Mandiant (Google Cloud)": "direct_service",  # Mandiant Managed Defense is vendor-delivered
    "IBM Security":        "direct_service",     # IBM X-Force managed services
    "CrowdStrike":         "direct_service",     # Falcon Complete is vendor-delivered MDR
    "SentinelOne":         "direct_service",     # Vigilance MDR is vendor-delivered
    "Rapid7":              "direct_service",     # Managed Detection & Response (MDR) team
    "Fidelis Cybersecurity": "direct_service",   # Fidelis MDR with own analysts
    "ZeroFox":             "direct_service",     # Managed services with own analysts
    "Darktrace":           "direct_service",     # Darktrace managed services (HEAL, Proactive Threat Notification)
    "Cisco (Splunk)":      "direct_service",     # Cisco Talos managed services

    # === Platform + partner model ===
    "Tenable":             "platform_plus_partner",  # Professional services in-house; MSSP partners deliver managed ops
    "Palo Alto Networks":  "platform_plus_partner",  # Unit 42 consulting; NextWave MSSP partners for managed ops
    "Fortinet":            "platform_plus_partner",  # FortiGuard services + MSSP partners; some direct via SOCaaS
    "Qualys":              "platform_plus_partner",  # Platform vendor; partners deliver managed VM
    "CyberArk":            "platform_plus_partner",  # Identity platform; C3 Alliance partners deliver managed PAM
    "Zscaler":             "platform_plus_partner",  # Zero trust platform; partners deliver managed SASE
    "Akamai (Guardicore)": "platform_plus_partner",  # Platform + Akamai managed security services (mostly WAF/DDoS focused)
    "Armis":               "platform_plus_partner",  # Asset intelligence platform; partners deliver managed services
    "Censys":              "platform_plus_partner",  # ASM platform; no direct managed services
    "BeyondTrust":         "platform_plus_partner",  # PAM platform; partners deliver managed PAM
    "Delinea":             "platform_plus_partner",  # PAM platform; partners deliver
    "Illumio":             "platform_plus_partner",  # Zero trust segmentation platform; partner-delivered services
    "Lacework (Fortinet)": "platform_plus_partner",  # Cloud security platform; partner-delivered
    "Bitsight":            "platform_plus_partner",  # Ratings platform; partner ecosystem
    "SecurityScorecard":   "platform_plus_partner",  # Ratings platform; partner ecosystem

    # === Platform only (technology licensing) ===
    "CyCognito":           "platform_only",     # Automated ASM — no managed services
    "Pentera":             "platform_only",     # Automated pentesting — technology only
    "AttackIQ":            "platform_only",     # BAS platform — technology only
    "Cymulate":            "platform_only",     # BAS/ESPM — technology only
    "Picus Security":      "platform_only",     # Security validation — technology only
    "SafeBreach":          "platform_only",     # BAS platform — technology only
    "Horizon3.ai":         "platform_only",     # Autonomous pentesting — technology only
    "XM Cyber":            "platform_only",     # Attack path analysis — technology only
    "Wiz":                 "platform_only",     # Cloud security platform — technology only
    "Orca Security":       "platform_only",     # Cloud security platform — technology only
    "Aqua Security":       "platform_only",     # Container/cloud security — technology only
    "Morphisec":           "platform_only",     # AMTD — technology only
    "RunSafe Security":    "platform_only",     # Binary hardening — technology only
    "CounterCraft":        "platform_only",     # Deception — technology only
    "Acalvio Technologies":"platform_only",     # Deception — technology only
    "JupiterOne":          "platform_only",     # CAASM — technology only
    "Axonius":             "platform_only",     # CAASM — technology only
    "HashiCorp":           "platform_only",     # Infrastructure automation — technology only
    "Contrast Security":   "platform_only",     # AppSec — technology only
    "ThreatConnect":       "platform_only",     # TIP — technology only (orchestration platform)
    "Anomali":             "platform_only",     # TIP — technology only
    "Recorded Future":     "platform_only",     # Threat intelligence SaaS — technology only
    "Panorays":            "platform_only",     # TPRM — technology only
    "Group-IB":            "platform_only",     # Threat intel + managed attribution — mostly platform
    "Trellix":             "platform_only",     # XDR platform — technology only
    "Nisos":               "direct_service",    # Managed intelligence services — analyst-delivered
}


def classify_svc03_score(vendor_name, current_score, delivery_model, evidence):
    """
    Re-score SVC-03 based on delivery model.

    direct_service: Keep score if evidence supports direct managed ops delivery.
      - Must show: own SOC, own analysts, SLA commitments, 24/7 monitoring
    platform_plus_partner:
      - Cap at 2.5 max. Score reflects quality of partner enablement program.
      - 2.5 = Formal MSSP program with certification, tools, and co-delivery
      - 2.0 = Partner program exists but limited enablement
      - 1.5 = Partners mentioned but no formal program
    platform_only:
      - Cap at 1.0 (no managed service option whatsoever)
    """
    if delivery_model == "direct_service":
        # For direct service providers, validate the score isn't inflated
        # Scores above 4.0 require strong evidence of dedicated analyst teams,
        # SLA-backed delivery, and operational governance
        if current_score > 4.0:
            # Check if evidence actually supports elite managed ops
            ev_text = _extract_evidence_text(evidence)
            has_soc = any(term in ev_text for term in ["24/7", "soc ", "security operations center"])
            has_sla = any(term in ev_text for term in ["sla", "service level", "response time"])
            has_analysts = any(term in ev_text for term in ["dedicated analyst", "named analyst", "analyst team", "concierge"])
            if has_soc and (has_sla or has_analysts):
                return current_score  # Evidence supports high score
            return 3.5  # Strong managed service but lacks elite evidence
        return current_score

    elif delivery_model == "platform_plus_partner":
        # Platform vendors don't deliver managed services directly
        ev_text = _extract_evidence_text(evidence)
        has_formal_mssp = any(term in ev_text for term in [
            "mssp program", "mssp partner", "partner program",
            "managed service provider partner", "partner-delivered"
        ])
        has_partner_enablement = any(term in ev_text for term in [
            "partner certification", "partner training", "partner portal",
            "technology alliance", "ecosystem partner"
        ])
        if has_formal_mssp and has_partner_enablement:
            return 2.5
        elif has_formal_mssp:
            return 2.0
        else:
            return 1.5

    else:  # platform_only
        return 1.0


def classify_svc04_score(vendor_name, current_score, delivery_model, evidence):
    """
    Re-score SVC-04 based on delivery model.

    SVC-04 evaluates AI in SERVICE DELIVERY — not AI in the product itself.
    For platform vendors, AI features are product capabilities (scored in EXM/AMT/ADR/PPM),
    not service delivery automation.

    direct_service:
      - Score reflects AI in their managed service delivery (auto-triage, AI analysts)
      - Keep current score if evidence shows AI in service delivery context
    platform_plus_partner:
      - Cap at 2.0 — platform AI helps partners but vendor doesn't deliver services
      - 2.0 = Platform has AI automation that partners leverage in service delivery
      - 1.5 = Platform has AI but no evidence of service delivery context
    platform_only:
      - Cap at 1.0 — AI is in the product, not in service delivery
    """
    if delivery_model == "direct_service":
        # Validate: is the AI evidence about service delivery or just product features?
        ev_text = _extract_evidence_text(evidence)
        service_ai_indicators = [
            "automated triage", "ai-driven response", "autonomous", "agentic",
            "ai analyst", "copilot", "automated investigation", "ai-augmented soc",
            "automated remediation", "self-healing", "ai-powered detection and response",
            "threat ai", "managed threat hunting"
        ]
        product_only_indicators = [
            "vulnerability priority", "risk scoring", "exposure", "asset discovery",
            "scanning", "compliance", "policy"
        ]
        service_hits = sum(1 for t in service_ai_indicators if t in ev_text)
        product_hits = sum(1 for t in product_only_indicators if t in ev_text)

        if service_hits > 0:
            return current_score  # Legitimate service delivery AI
        elif product_hits > service_hits:
            return min(current_score, 2.5)  # AI is product-level, not service delivery
        return current_score

    elif delivery_model == "platform_plus_partner":
        ev_text = _extract_evidence_text(evidence)
        platform_ai = any(term in ev_text for term in [
            "ai", "ml", "machine learning", "generative ai", "automation"
        ])
        if platform_ai:
            return 2.0
        return 1.5

    else:  # platform_only
        ev_text = _extract_evidence_text(evidence)
        has_ai = any(term in ev_text for term in ["ai", "ml", "machine learning", "automation"])
        if has_ai:
            return 1.5  # Has AI but no service delivery context
        return 1.0


def _extract_evidence_text(evidence):
    """Extract all evidence text from an evidence dict for text matching."""
    if not evidence or not isinstance(evidence, dict):
        return ""
    parts = []
    for key, val in evidence.items():
        if not key.startswith("SVC"):
            continue
        if isinstance(val, dict):
            for ex in val.get("excerpts", []):
                if isinstance(ex, str):
                    parts.append(ex)
                elif isinstance(ex, dict):
                    parts.append(ex.get("excerpt", ex.get("text", "")))
        elif isinstance(val, str):
            parts.append(val)
    return " ".join(parts).lower()


def reclassify_and_rescore():
    filepath = os.path.join(os.path.dirname(__file__), VENDOR_FILE)
    with open(filepath, "r", encoding="utf-8") as f:
        vendors = json.load(f)

    stats = {"adjusted": 0, "svc03_changes": 0, "svc04_changes": 0, "model_counts": {}}
    changes = []

    for v in vendors:
        name = v.get("vendor", "?")
        model = DELIVERY_MODEL.get(name, "platform_only")
        stats["model_counts"][model] = stats["model_counts"].get(model, 0) + 1

        evidence = v.get("sub_pillar_evidence", {})
        sps = v.get("sub_pillar_scores_current", {})
        old_03 = sps.get("SVC-03", 0)
        old_04 = sps.get("SVC-04", 0)

        # Re-classify SVC-03 and SVC-04
        new_03 = classify_svc03_score(name, old_03, model, evidence)
        new_04 = classify_svc04_score(name, old_04, model, evidence)

        changed = False
        change_detail = {"vendor": name, "model": model}

        if abs(new_03 - old_03) > 0.01:
            change_detail["SVC-03"] = f"{old_03} -> {new_03}"
            stats["svc03_changes"] += 1
            changed = True

        if abs(new_04 - old_04) > 0.01:
            change_detail["SVC-04"] = f"{old_04} -> {new_04}"
            stats["svc04_changes"] += 1
            changed = True

        if changed:
            stats["adjusted"] += 1
            changes.append(change_detail)

            # Apply new scores
            sps["SVC-03"] = new_03
            sps["SVC-04"] = new_04

            # Also update in validated and v2_researched dicts
            for key in ["sub_pillar_scores_validated", "sub_pillar_scores_v2_researched"]:
                d = v.get(key, {})
                if "SVC-03" in d:
                    d["SVC-03"] = new_03
                if "SVC-04" in d:
                    d["SVC-04"] = new_04

            # Recalculate SVC pillar score as average of SVC-01..04
            svc_scores = [sps.get(f"SVC-0{i}", 0) for i in range(1, 5)]
            svc_avg = round(sum(svc_scores) / len(svc_scores), 2) if svc_scores else 0
            old_pillar = v.get("pillar_scores", {}).get("SVC", 0)
            v["pillar_scores"]["SVC"] = svc_avg

            for pk in ["pillar_scores_validated", "pillar_scores_v2_researched"]:
                d = v.get(pk, {})
                if "SVC" in d:
                    d["SVC"] = svc_avg

            change_detail["SVC_pillar"] = f"{old_pillar} -> {svc_avg}"

            # Update rationale for changed sub-pillars
            rat = v.get("sub_pillar_rationale_v2_consolidated", {})
            if abs(new_03 - old_03) > 0.01 and "SVC-03" in rat:
                old_rat = rat["SVC-03"]
                model_note = (
                    f"[Delivery Model Adjustment] Vendor classified as '{model}'. "
                )
                if model == "platform_plus_partner":
                    model_note += (
                        f"Score adjusted from {old_03} to {new_03}. "
                        f"Vendor does not deliver managed services directly — "
                        f"managed operations are delivered by MSSP/channel partners "
                        f"using the vendor's platform. Score reflects partner enablement quality, "
                        f"not direct managed service delivery."
                    )
                elif model == "platform_only":
                    model_note += (
                        f"Score adjusted from {old_03} to {new_03}. "
                        f"No managed service option available. Technology/platform licensing only."
                    )
                else:
                    model_note += f"Score maintained at {new_03} for direct service provider."

                if isinstance(old_rat, str):
                    rat["SVC-03"] = model_note + "\n\n[Original Rationale] " + old_rat
                elif isinstance(old_rat, dict):
                    old_rat["delivery_model_adjustment"] = model_note
                    old_rat["original_score"] = old_03
                    old_rat["adjusted_score"] = new_03

            if abs(new_04 - old_04) > 0.01 and "SVC-04" in rat:
                old_rat = rat["SVC-04"]
                model_note = (
                    f"[Delivery Model Adjustment] Vendor classified as '{model}'. "
                )
                if model == "platform_plus_partner":
                    model_note += (
                        f"Score adjusted from {old_04} to {new_04}. "
                        f"AI/ML capabilities are platform product features, not AI in service delivery. "
                        f"Platform AI enables partner-delivered services but vendor does not deliver services directly."
                    )
                elif model == "platform_only":
                    model_note += (
                        f"Score adjusted from {old_04} to {new_04}. "
                        f"AI/ML is a product feature, not a service delivery mechanism. "
                        f"No managed service delivery context for AI automation."
                    )
                else:
                    model_note += f"Score adjusted from {old_04} to {new_04}. AI evidence is product-level, not service delivery."

                if isinstance(old_rat, str):
                    rat["SVC-04"] = model_note + "\n\n[Original Rationale] " + old_rat
                elif isinstance(old_rat, dict):
                    old_rat["delivery_model_adjustment"] = model_note
                    old_rat["original_score"] = old_04
                    old_rat["adjusted_score"] = new_04

            # Store delivery model classification
            v["delivery_model"] = model

    # Write back
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(vendors, f, indent=2, ensure_ascii=False)

    # Report
    print(f"\n{'='*70}")
    print(f"SVC RE-SCORING REPORT — Delivery Model Classification")
    print(f"{'='*70}")
    print(f"\nVendor counts by delivery model:")
    for m, c in sorted(stats["model_counts"].items()):
        print(f"  {m}: {c} vendors")
    print(f"\nAdjusted: {stats['adjusted']} vendors")
    print(f"  SVC-03 changes: {stats['svc03_changes']}")
    print(f"  SVC-04 changes: {stats['svc04_changes']}")
    print()

    for c in sorted(changes, key=lambda x: x["vendor"]):
        parts = [f"{c['vendor']} ({c['model']})"]
        if "SVC-03" in c:
            parts.append(f"  SVC-03: {c['SVC-03']}")
        if "SVC-04" in c:
            parts.append(f"  SVC-04: {c['SVC-04']}")
        if "SVC_pillar" in c:
            parts.append(f"  SVC pillar: {c['SVC_pillar']}")
        print("\n".join(parts))
        print()

    # Final summary table
    print(f"\n{'='*70}")
    print(f"FINAL SVC SCORES (sorted by SVC pillar)")
    print(f"{'='*70}")
    with open(filepath, "r", encoding="utf-8") as f:
        vendors = json.load(f)
    rows = []
    for v in vendors:
        ps = v.get("pillar_scores", {})
        sps = v.get("sub_pillar_scores_current", {})
        name = v.get("vendor", "?")
        dm = v.get("delivery_model", DELIVERY_MODEL.get(name, "?"))
        svc = ps.get("SVC", 0)
        rows.append((svc, name, sps.get("SVC-01",0), sps.get("SVC-02",0),
                      sps.get("SVC-03",0), sps.get("SVC-04",0), dm))
    rows.sort(key=lambda x: -x[0])
    print(f"{'Vendor':<28} {'SVC':>4} {'01':>5} {'02':>5} {'03':>5} {'04':>5}  {'Model'}")
    print("-" * 90)
    for svc, name, s1, s2, s3, s4, dm in rows:
        print(f"{name:<28} {svc:>4} {s1:>5} {s2:>5} {s3:>5} {s4:>5}  {dm}")


if __name__ == "__main__":
    reclassify_and_rescore()
