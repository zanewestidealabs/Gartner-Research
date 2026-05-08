"""
Agentic SOC Maturity Framework — Report Generator
Reads an ASMF self-assessment JSON and produces a standalone HTML report.

Usage:
    python _create_agentic_soc_report.py
    python _create_agentic_soc_report.py --assessment my_assessment.json
    python _create_agentic_soc_report.py --assessment my_assessment.json --output my_report.html
    python _create_agentic_soc_report.py --demo   (generates a demo report with sample scores)
"""

import json
import sys
import os
import argparse
from datetime import datetime

FRAMEWORK_FILE = "agentic_soc_framework_v1.json"

DIMENSION_SHORT = {
    "SEN": "Sensing Fabric",
    "RSN": "Reasoning & Planning",
    "ACT": "Autonomous Action",
    "GOV": "Ethics & Governance",
    "LRN": "Learning & DFIR",
    "OPS": "Operational Model",
    "HUM": "Human Roles",
    "AGT": "Agent Architecture",
    "SKG": "Knowledge Graph",
    "MET": "Metrics & Assurance",
    "TRN": "Transformation Readiness",
}

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

STAGE_COLORS = {
    0: "#6b7280",  # gray
    1: "#3b82f6",  # blue
    2: "#8b5cf6",  # purple
    3: "#f59e0b",  # amber
    4: "#10b981",  # emerald
    5: "#22c55e",  # green
}

STAGE_LABELS = {
    0: "Traditional",
    1: "Assisted",
    2: "Supervised Autonomy",
    3: "Directed Autonomy",
    4: "Collaborative Agentic",
    5: "Fully Agentic",
}


def load_framework():
    with open(FRAMEWORK_FILE, encoding="utf-8") as f:
        return json.load(f)


def build_demo_assessment(framework):
    """Generate a sample assessment for demo purposes."""
    import random
    random.seed(42)

    dims = framework["dimensions"]
    assessment = {
        "assessment_metadata": {
            "organization": "Example Enterprise Corp",
            "assessor": "Security Architecture Team",
            "assessment_date": datetime.today().strftime("%Y-%m-%d"),
            "scope": "Enterprise SOC — 9 analysts, internal + MDR retainer",
            "current_soc_model": "Internal L1/L2/L3 with SOAR, MDR retainer for after-hours coverage",
            "regulatory_context": "SOC 2 Type II, ISO 27001, DORA compliance program underway",
        },
        "dimensions": {},
        "transformation_priorities": {
            "horizon_1": {
                "label": "Immediate (0-6 months)",
                "focus": "Establish governance foundations and data quality",
                "key_actions": [
                    "Define formal agent authority model for existing SOAR automation",
                    "Build SKG prototype with asset, identity, and adversary entities",
                    "Map detection coverage against MITRE ATT&CK and identify top-10 TTP gaps",
                    "Redefine analyst job descriptions to include agent supervision responsibilities",
                ],
            },
            "horizon_2": {
                "label": "Near-term (6-18 months)",
                "focus": "Introduce supervised autonomy and eliminate L1 tier workload",
                "key_actions": [
                    "Deploy agent-driven investigation for high-volume known threat patterns",
                    "Implement machine-interpretable policy engine for core governance controls",
                    "Activate continuous DFIR for Tier 1 critical assets",
                    "Launch governance officer role and training program",
                ],
            },
            "horizon_3": {
                "label": "Strategic (18-36 months)",
                "focus": "Directed autonomy — post-tier operations with intent-based governance",
                "key_actions": [
                    "Eliminate tier model; implement post-tier authority roles fully",
                    "Deploy ethics guardrail engine as an operational control loop",
                    "Make SKG the primary reasoning substrate for all investigation decisions",
                    "Publish board-level autonomous operations posture report quarterly",
                ],
            },
        },
    }

    demo_scores = {
        "SEN": {"SEN-01": (1.5, 3), "SEN-02": (1.0, 3), "SEN-03": (1.0, 3), "SEN-04": (0.5, 3)},
        "RSN": {"RSN-01": (0.5, 3), "RSN-02": (1.0, 3), "RSN-03": (0.5, 2), "RSN-04": (0.5, 2)},
        "ACT": {"ACT-01": (1.5, 3), "ACT-02": (0.5, 3), "ACT-03": (0.5, 2), "ACT-04": (1.0, 3)},
        "GOV": {"GOV-01": (0.0, 3), "GOV-02": (0.0, 2), "GOV-03": (0.5, 3), "GOV-04": (1.0, 3)},
        "LRN": {"LRN-01": (1.0, 3), "LRN-02": (1.0, 3), "LRN-03": (1.5, 3), "LRN-04": (0.5, 3)},
        "OPS": {"OPS-01": (0.5, 3), "OPS-02": (1.0, 3), "OPS-03": (0.5, 3), "OPS-04": (1.0, 3)},
        "HUM": {"HUM-01": (0.5, 3), "HUM-02": (1.0, 3), "HUM-03": (0.5, 3), "HUM-04": (0.5, 2)},
        "AGT": {"AGT-01": (1.0, 3), "AGT-02": (0.5, 2), "AGT-03": (0.5, 2), "AGT-04": (1.0, 3)},
        "SKG": {"SKG-01": (1.0, 3), "SKG-02": (0.0, 3), "SKG-03": (1.0, 3), "SKG-04": (0.5, 3)},
        "MET": {"MET-01": (1.0, 3), "MET-02": (1.0, 3), "MET-03": (0.5, 2), "MET-04": (1.0, 3)},
        "TRN": {"TRN-01": (2.0, 4), "TRN-02": (1.5, 3), "TRN-03": (1.5, 3), "TRN-04": (0.5, 2)},
    }

    priority_map = {
        "GOV-01": "critical", "GOV-02": "critical", "ACT-02": "critical",
        "SKG-02": "critical", "HUM-01": "critical",
        "GOV-03": "high", "SEN-01": "high", "SEN-02": "high", "SKG-01": "high",
        "LRN-01": "high", "TRN-01": "high", "TRN-02": "high",
    }
    evidence_map = {
        "GOV-01": "Authority defined in RACI and policy only. No technical enforcement of automation scope boundaries.",
        "GOV-02": "Ethics is a section in the Acceptable Use Policy. No operational integration whatsoever.",
        "SKG-01": "Asset data in CMDB, identity in AD, threat intel in separate platform. No unified graph.",
        "SEN-01": "Endpoint and network covered well. SaaS and cloud coverage partial. Identity signal fusion absent.",
        "TRN-01": "CISO has articulated agentic vision in strategy doc. CTO aligned. Board briefed Q1 2026.",
        "ACT-02": "Playbook scope defined in SOAR tool. Enforcement is procedural, not technical. Gaps exist.",
    }

    for dim_id, sub_scores in demo_scores.items():
        dim_data = {"dimension_notes": "", "sub_dimensions": {}}
        for sd_id, (cur, tgt) in sub_scores.items():
            dim_data["sub_dimensions"][sd_id] = {
                "current_stage": cur,
                "target_stage": tgt,
                "priority": priority_map.get(sd_id, "medium"),
                "evidence_note": evidence_map.get(sd_id, ""),
                "gap_note": "",
                "owner": "",
            }
        assessment["dimensions"][dim_id] = dim_data

    return assessment


def compute_scores(framework, assessment):
    """Compute dimension and overall scores from the assessment."""
    dims = framework["dimensions"]
    dim_scores = {}

    for dim_id, dim_def in dims.items():
        if dim_id not in assessment.get("dimensions", {}):
            continue
        sds = assessment["dimensions"][dim_id].get("sub_dimensions", {})
        current_vals = []
        target_vals = []
        for sd_id in dim_def["sub_dimensions"]:
            sd_data = sds.get(sd_id, {})
            cur = sd_data.get("current_stage")
            tgt = sd_data.get("target_stage")
            if cur is not None:
                current_vals.append(float(cur))
            if tgt is not None:
                target_vals.append(float(tgt))
        dim_scores[dim_id] = {
            "current": round(sum(current_vals) / len(current_vals), 2) if current_vals else None,
            "target": round(sum(target_vals) / len(target_vals), 2) if target_vals else None,
            "weight": dim_def.get("weight", 0.09),
        }

    valid_current = [(v["current"], v["weight"]) for v in dim_scores.values() if v["current"] is not None]
    valid_target = [(v["target"], v["weight"]) for v in dim_scores.values() if v["target"] is not None]

    total_w_cur = sum(w for _, w in valid_current)
    total_w_tgt = sum(w for _, w in valid_target)

    overall_current = round(sum(s * w for s, w in valid_current) / total_w_cur, 2) if valid_current else None
    overall_target = round(sum(s * w for s, w in valid_target) / total_w_tgt, 2) if valid_target else None

    return dim_scores, overall_current, overall_target


def stage_label(score):
    if score is None:
        return "Unknown"
    if score < 1.0:
        return "Traditional"
    if score < 2.0:
        return "Assisted"
    if score < 3.0:
        return "Supervised Autonomy"
    if score < 4.0:
        return "Directed Autonomy"
    if score < 5.0:
        return "Collaborative Agentic"
    return "Fully Agentic"


def stage_color(score):
    if score is None:
        return "#6b7280"
    idx = min(5, max(0, int(score)))
    # interpolate
    return STAGE_COLORS.get(idx, "#6b7280")


def build_gap_table(framework, assessment):
    """Build a sorted list of all sub-dimension gaps."""
    gaps = []
    for dim_id, dim_def in framework["dimensions"].items():
        if dim_id not in assessment.get("dimensions", {}):
            continue
        sds = assessment["dimensions"][dim_id].get("sub_dimensions", {})
        for sd_id, sd_def in dim_def["sub_dimensions"].items():
            sd_data = sds.get(sd_id, {})
            cur = sd_data.get("current_stage")
            tgt = sd_data.get("target_stage")
            if cur is not None and tgt is not None:
                gap = float(tgt) - float(cur)
                priority = sd_data.get("priority", "medium")
                priority_val = PRIORITY_ORDER.get(str(priority).lower().split("|")[0].strip(), 2)
                gaps.append({
                    "dim_id": dim_id,
                    "sd_id": sd_id,
                    "sd_name": sd_def["name"],
                    "dim_name": DIMENSION_SHORT.get(dim_id, dim_id),
                    "current": float(cur),
                    "target": float(tgt),
                    "gap": gap,
                    "priority": str(priority).split("|")[0].strip(),
                    "priority_val": priority_val,
                    "evidence_note": sd_data.get("evidence_note", ""),
                    "gap_note": sd_data.get("gap_note", ""),
                    "owner": sd_data.get("owner", ""),
                    "assessment_question": sd_def.get("assessment_question", ""),
                })
    # Sort by priority then gap size (largest gaps first)
    gaps.sort(key=lambda x: (x["priority_val"], -x["gap"]))
    return gaps


def priority_badge(p):
    colors = {
        "critical": "#ef4444",
        "high": "#f97316",
        "medium": "#eab308",
        "low": "#6b7280",
    }
    p_clean = str(p).split("|")[0].strip().lower()
    color = colors.get(p_clean, "#6b7280")
    return f'<span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;text-transform:uppercase;">{p_clean}</span>'


def score_bar(current, target, max_val=5):
    cur_pct = (float(current) / max_val) * 100
    tgt_pct = (float(target) / max_val) * 100
    cur_color = stage_color(current)
    return f"""
    <div style="position:relative;height:20px;background:#1e293b;border-radius:4px;overflow:visible;min-width:120px;">
      <div style="position:absolute;left:0;top:0;height:100%;width:{cur_pct:.1f}%;background:{cur_color};border-radius:4px;opacity:0.85;"></div>
      <div style="position:absolute;left:{tgt_pct:.1f}%;top:-3px;width:2px;height:26px;background:#f8fafc;border-radius:1px;" title="Target: {target}"></div>
      <span style="position:absolute;right:4px;top:2px;font-size:10px;color:#94a3b8;">{current} → {target}</span>
    </div>"""


def render_radar_chart(framework, dim_scores):
    labels = [DIMENSION_SHORT.get(d, d) for d in framework["dimensions"].keys()]
    current_data = [dim_scores.get(d, {}).get("current") or 0 for d in framework["dimensions"].keys()]
    target_data = [dim_scores.get(d, {}).get("target") or 0 for d in framework["dimensions"].keys()]
    return f"""
    <canvas id="radarChart" width="420" height="420"></canvas>
    <script>
    (function() {{
        const ctx = document.getElementById('radarChart').getContext('2d');
        new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [
                    {{
                        label: 'Current State',
                        data: {json.dumps(current_data)},
                        backgroundColor: 'rgba(59,130,246,0.2)',
                        borderColor: 'rgba(59,130,246,0.9)',
                        borderWidth: 2,
                        pointBackgroundColor: 'rgba(59,130,246,1)',
                        pointRadius: 4,
                    }},
                    {{
                        label: 'Target State',
                        data: {json.dumps(target_data)},
                        backgroundColor: 'rgba(16,185,129,0.1)',
                        borderColor: 'rgba(16,185,129,0.7)',
                        borderWidth: 2,
                        borderDash: [5,5],
                        pointBackgroundColor: 'rgba(16,185,129,1)',
                        pointRadius: 4,
                    }}
                ]
            }},
            options: {{
                responsive: false,
                scales: {{
                    r: {{
                        min: 0, max: 5,
                        ticks: {{ stepSize: 1, color: '#64748b', backdropColor: 'transparent', font: {{ size: 10 }} }},
                        grid: {{ color: 'rgba(100,116,139,0.3)' }},
                        angleLines: {{ color: 'rgba(100,116,139,0.3)' }},
                        pointLabels: {{ color: '#94a3b8', font: {{ size: 11 }} }}
                    }}
                }},
                plugins: {{
                    legend: {{ labels: {{ color: '#94a3b8', font: {{ size: 12 }} }} }}
                }}
            }}
        }});
    }})();
    </script>"""


def render_stage_progress_bar(overall_current, overall_target):
    stages = [
        (0, "Traditional"), (1, "Assisted"), (2, "Supervised\nAutonomy"),
        (3, "Directed\nAutonomy"), (4, "Collaborative\nAgentic"), (5, "Fully\nAgentic")
    ]
    items = []
    for stage_id, label in stages:
        color = STAGE_COLORS[stage_id]
        is_current = abs(float(overall_current or 0) - stage_id) < 0.5
        is_target = abs(float(overall_target or 0) - stage_id) < 0.5
        border = "3px solid #f8fafc" if is_current else ("3px dashed #10b981" if is_target else "3px solid transparent")
        opacity = "1.0" if is_current else ("0.7" if is_target else "0.35")
        badge = ""
        if is_current:
            badge = '<div style="font-size:9px;background:#f8fafc;color:#0f172a;padding:1px 5px;border-radius:3px;margin-top:3px;font-weight:700;">CURRENT</div>'
        elif is_target:
            badge = '<div style="font-size:9px;background:#10b981;color:#fff;padding:1px 5px;border-radius:3px;margin-top:3px;font-weight:700;">TARGET</div>'
        label_html = label.replace("\n", "<br>")
        items.append(f"""
        <div style="display:flex;flex-direction:column;align-items:center;flex:1;">
          <div style="width:52px;height:52px;border-radius:50%;background:{color};border:{border};opacity:{opacity};
                      display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;color:#fff;">
            {stage_id}
          </div>
          <div style="font-size:10px;color:#94a3b8;text-align:center;margin-top:4px;line-height:1.3;">{label_html}</div>
          {badge}
        </div>""")

    connector = '<div style="flex:0 0 20px;height:2px;background:#334155;align-self:center;margin-top:-24px;"></div>'
    content = connector.join(items)
    return f'<div style="display:flex;align-items:flex-start;gap:0;padding:16px 8px;">{content}</div>'


def render_dimension_cards(framework, assessment, dim_scores):
    cards = []
    for dim_id, dim_def in framework["dimensions"].items():
        scores = dim_scores.get(dim_id, {})
        cur = scores.get("current")
        tgt = scores.get("target")
        if cur is None:
            continue
        cur_label = stage_label(cur)
        cur_color = stage_color(cur)
        gap = round((tgt or 0) - cur, 2)
        gap_str = f"+{gap}" if gap >= 0 else str(gap)

        sds = assessment["dimensions"].get(dim_id, {}).get("sub_dimensions", {})

        # Sub-dimension rows
        sd_rows = []
        for sd_id, sd_def in dim_def["sub_dimensions"].items():
            sd_data = sds.get(sd_id, {})
            sd_cur = sd_data.get("current_stage")
            sd_tgt = sd_data.get("target_stage")
            if sd_cur is None:
                continue
            priority = str(sd_data.get("priority", "medium")).split("|")[0].strip()
            evidence = sd_data.get("evidence_note", "") or ""
            stage_desc = dim_def["sub_dimensions"][sd_id]["stage_descriptors"].get(str(int(float(sd_cur))), "")
            sd_rows.append(f"""
            <tr style="border-bottom:1px solid #1e293b;">
              <td style="padding:8px 6px;font-size:12px;color:#64748b;white-space:nowrap;">{sd_id}</td>
              <td style="padding:8px 6px;font-size:12px;color:#e2e8f0;">{sd_def['name']}</td>
              <td style="padding:8px 6px;text-align:center;">{priority_badge(priority)}</td>
              <td style="padding:8px 6px;">{score_bar(sd_cur, sd_tgt)}</td>
              <td style="padding:8px 6px;font-size:11px;color:#64748b;max-width:280px;">{evidence[:120] + '…' if len(evidence) > 120 else evidence}</td>
            </tr>""")

        sd_table = f"""
        <table style="width:100%;border-collapse:collapse;margin-top:12px;">
          <thead>
            <tr style="border-bottom:1px solid #334155;">
              <th style="padding:6px;font-size:11px;color:#475569;text-align:left;white-space:nowrap;">ID</th>
              <th style="padding:6px;font-size:11px;color:#475569;text-align:left;">Sub-Dimension</th>
              <th style="padding:6px;font-size:11px;color:#475569;text-align:center;">Priority</th>
              <th style="padding:6px;font-size:11px;color:#475569;text-align:left;">Score (cur → tgt)</th>
              <th style="padding:6px;font-size:11px;color:#475569;text-align:left;">Evidence Note</th>
            </tr>
          </thead>
          <tbody>{''.join(sd_rows)}</tbody>
        </table>"""

        cards.append(f"""
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:20px;margin-bottom:16px;">
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
            <div style="background:{cur_color};color:#fff;padding:4px 12px;border-radius:20px;font-size:13px;font-weight:700;">{cur:.1f}</div>
            <div>
              <div style="font-size:16px;font-weight:700;color:#f1f5f9;">{dim_def['name']}</div>
              <div style="font-size:12px;color:#64748b;">{dim_def['description'][:120]}…</div>
            </div>
            <div style="margin-left:auto;text-align:right;">
              <div style="font-size:11px;color:#64748b;">Current</div>
              <div style="font-size:14px;font-weight:700;color:{cur_color};">{cur_label}</div>
              <div style="font-size:11px;color:#10b981;">Gap: {gap_str}</div>
            </div>
          </div>
          {sd_table}
        </div>""")

    return "".join(cards)


def render_gap_table_html(gaps, max_rows=20):
    rows = []
    for g in gaps[:max_rows]:
        pct_fill = int((g["current"] / 5) * 100)
        pct_tgt = int((g["target"] / 5) * 100)
        gap_color = "#ef4444" if g["gap"] >= 2 else ("#f59e0b" if g["gap"] >= 1 else "#10b981")
        rows.append(f"""
        <tr style="border-bottom:1px solid #1e293b;">
          <td style="padding:10px 8px;">{priority_badge(g['priority'])}</td>
          <td style="padding:10px 8px;font-size:12px;color:#64748b;">{g['dim_name']}</td>
          <td style="padding:10px 8px;font-size:13px;color:#e2e8f0;">{g['sd_name']}</td>
          <td style="padding:10px 8px;text-align:center;">
            <span style="font-size:13px;font-weight:700;color:{stage_color(g['current'])};">{g['current']}</span>
            <span style="color:#475569;"> → </span>
            <span style="font-size:13px;font-weight:700;color:#10b981;">{g['target']}</span>
          </td>
          <td style="padding:10px 8px;text-align:center;">
            <span style="font-size:14px;font-weight:700;color:{gap_color};">+{g['gap']:.1f}</span>
          </td>
          <td style="padding:10px 8px;font-size:11px;color:#64748b;max-width:240px;">{g['assessment_question'][:100]}…</td>
        </tr>""")

    return f"""
    <table style="width:100%;border-collapse:collapse;">
      <thead>
        <tr style="border-bottom:2px solid #334155;">
          <th style="padding:10px 8px;font-size:12px;color:#475569;text-align:left;">Priority</th>
          <th style="padding:10px 8px;font-size:12px;color:#475569;text-align:left;">Dimension</th>
          <th style="padding:10px 8px;font-size:12px;color:#475569;text-align:left;">Sub-Dimension</th>
          <th style="padding:10px 8px;font-size:12px;color:#475569;text-align:center;">Score</th>
          <th style="padding:10px 8px;font-size:12px;color:#475569;text-align:center;">Gap</th>
          <th style="padding:10px 8px;font-size:12px;color:#475569;text-align:left;">Assessment Question</th>
        </tr>
      </thead>
      <tbody>{''.join(rows)}</tbody>
    </table>"""


def render_transformation_roadmap(assessment):
    tp = assessment.get("transformation_priorities", {})
    horizon_colors = {
        "horizon_1": "#ef4444",
        "horizon_2": "#f59e0b",
        "horizon_3": "#3b82f6",
    }
    sections = []
    for key, color in horizon_colors.items():
        h = tp.get(key, {})
        label = h.get("label", key)
        focus = h.get("focus", "")
        actions = h.get("key_actions", [])
        action_items = "".join(
            f'<li style="padding:4px 0;font-size:13px;color:#94a3b8;">{a}</li>'
            for a in actions
        )
        sections.append(f"""
        <div style="background:#0f172a;border:1px solid #1e293b;border-left:4px solid {color};
                    border-radius:8px;padding:16px;flex:1;min-width:220px;">
          <div style="font-size:14px;font-weight:700;color:{color};margin-bottom:4px;">{label}</div>
          <div style="font-size:12px;color:#64748b;margin-bottom:10px;font-style:italic;">{focus}</div>
          <ul style="margin:0;padding-left:16px;">
            {action_items or '<li style="font-size:12px;color:#334155;">No actions defined</li>'}
          </ul>
        </div>""")
    return f'<div style="display:flex;gap:16px;flex-wrap:wrap;">{"".join(sections)}</div>'


def render_principles(framework):
    items = []
    for p in framework["principles"]:
        items.append(f"""
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:14px;flex:1;min-width:220px;">
          <div style="font-size:11px;font-weight:700;color:#3b82f6;margin-bottom:4px;">{p['id']} — {p['label']}</div>
          <div style="font-size:12px;color:#94a3b8;line-height:1.5;">{p['statement']}</div>
        </div>""")
    return f'<div style="display:flex;flex-wrap:wrap;gap:10px;">{"".join(items)}</div>'


def generate_html(framework, assessment, dim_scores, overall_current, overall_target):
    meta = assessment.get("assessment_metadata", {})
    org = meta.get("organization", "Organization")
    assessor = meta.get("assessor", "")
    date = meta.get("assessment_date", datetime.today().strftime("%Y-%m-%d"))
    scope = meta.get("scope", "")
    soc_model = meta.get("current_soc_model", "")
    regulatory = meta.get("regulatory_context", "")

    cur_label = stage_label(overall_current)
    tgt_label = stage_label(overall_target)
    cur_color = stage_color(overall_current)
    gaps = build_gap_table(framework, assessment)
    critical_gaps = [g for g in gaps if g["priority"] == "critical"]
    top_strengths = sorted(
        [(d, s["current"]) for d, s in dim_scores.items() if s["current"] is not None],
        key=lambda x: -x[1]
    )[:3]
    top_gap_dims = sorted(
        [(d, (s["target"] or 0) - (s["current"] or 0)) for d, s in dim_scores.items() if s["current"] is not None],
        key=lambda x: -x[1]
    )[:3]

    strength_items = "".join(
        f'<li style="color:#94a3b8;font-size:13px;padding:2px 0;">'
        f'<span style="color:{stage_color(sc)};font-weight:700;">{DIMENSION_SHORT.get(d, d)}</span> — Stage {sc:.1f} ({stage_label(sc)})</li>'
        for d, sc in top_strengths
    )
    gap_items = "".join(
        f'<li style="color:#94a3b8;font-size:13px;padding:2px 0;">'
        f'<span style="color:#f59e0b;font-weight:700;">{DIMENSION_SHORT.get(d, d)}</span> — Gap: +{g:.1f}</li>'
        for d, g in top_gap_dims
    )

    radar_js = render_radar_chart(framework, dim_scores)
    stage_bar = render_stage_progress_bar(overall_current, overall_target)
    dim_cards = render_dimension_cards(framework, assessment, dim_scores)
    gap_table = render_gap_table_html(gaps)
    roadmap = render_transformation_roadmap(assessment)
    principles = render_principles(framework)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ASMF Assessment — {org}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0a0f1a; color: #e2e8f0; font-family: 'Segoe UI', system-ui, sans-serif; }}
  .page {{ max-width: 1200px; margin: 0 auto; padding: 32px 24px; }}
  h1 {{ font-size: 28px; font-weight: 800; color: #f8fafc; }}
  h2 {{ font-size: 20px; font-weight: 700; color: #f1f5f9; margin: 32px 0 16px; border-bottom: 1px solid #1e293b; padding-bottom: 8px; }}
  h3 {{ font-size: 16px; font-weight: 600; color: #cbd5e1; margin: 16px 0 8px; }}
  .card {{ background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 20px; margin-bottom: 16px; }}
  .metric-card {{ background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 20px 24px; text-align: center; flex: 1; min-width: 160px; }}
  .metric-val {{ font-size: 36px; font-weight: 800; }}
  .metric-label {{ font-size: 12px; color: #64748b; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  .flex-row {{ display: flex; gap: 16px; flex-wrap: wrap; }}
  .section-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #475569; font-weight: 700; margin-bottom: 8px; }}
  @media print {{
    body {{ background: #fff; color: #111; }}
    .card, .metric-card {{ border: 1px solid #e5e7eb; background: #f9fafb; }}
  }}
</style>
</head>
<body>
<div class="page">

  <!-- HEADER -->
  <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:32px;flex-wrap:wrap;gap:16px;">
    <div>
      <div style="font-size:11px;color:#3b82f6;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;margin-bottom:4px;">
        Agentic SOC Maturity Framework (ASMF v1.0)
      </div>
      <h1>{org}</h1>
      <div style="font-size:13px;color:#64748b;margin-top:6px;">
        {f'Assessed by: {assessor} &nbsp;|&nbsp;' if assessor else ''} {date}
      </div>
      {f'<div style="font-size:12px;color:#475569;margin-top:4px;">{scope}</div>' if scope else ''}
    </div>
    <div style="text-align:right;">
      <div style="font-size:11px;color:#64748b;margin-bottom:4px;">Overall Maturity</div>
      <div style="font-size:42px;font-weight:800;color:{cur_color};line-height:1;">{overall_current:.2f}</div>
      <div style="font-size:14px;color:{cur_color};font-weight:600;">{cur_label}</div>
      <div style="font-size:12px;color:#10b981;margin-top:4px;">Target: {overall_target:.2f} — {tgt_label}</div>
    </div>
  </div>

  <!-- EXECUTIVE SUMMARY -->
  <div class="card">
    <div class="section-label">Executive Summary</div>
    <div class="flex-row" style="margin-bottom:16px;">
      <div class="metric-card">
        <div class="metric-val" style="color:{cur_color};">{overall_current:.2f}</div>
        <div class="metric-label">Current Stage</div>
        <div style="font-size:13px;color:{cur_color};margin-top:4px;font-weight:600;">{cur_label}</div>
      </div>
      <div class="metric-card">
        <div class="metric-val" style="color:#10b981;">{overall_target:.2f}</div>
        <div class="metric-label">Target Stage</div>
        <div style="font-size:13px;color:#10b981;margin-top:4px;font-weight:600;">{tgt_label}</div>
      </div>
      <div class="metric-card">
        <div class="metric-val" style="color:#f59e0b;">{overall_target - overall_current:.2f}</div>
        <div class="metric-label">Total Gap</div>
        <div style="font-size:13px;color:#64748b;margin-top:4px;">{len(gaps)} sub-dims scored</div>
      </div>
      <div class="metric-card">
        <div class="metric-val" style="color:#ef4444;">{len(critical_gaps)}</div>
        <div class="metric-label">Critical Gaps</div>
        <div style="font-size:13px;color:#64748b;margin-top:4px;">Require immediate attention</div>
      </div>
    </div>
    <div class="grid-2">
      <div>
        <h3>Top Strengths</h3>
        <ul style="padding-left:16px;">{strength_items}</ul>
      </div>
      <div>
        <h3>Largest Dimension Gaps</h3>
        <ul style="padding-left:16px;">{gap_items}</ul>
      </div>
    </div>
    {f'<div style="margin-top:16px;padding:12px;background:#1e293b;border-radius:6px;"><div style="font-size:11px;color:#475569;margin-bottom:4px;">SOC Model &amp; Context</div><div style="font-size:13px;color:#94a3b8;">{soc_model}</div></div>' if soc_model else ''}
    {f'<div style="margin-top:8px;padding:12px;background:#1e293b;border-radius:6px;"><div style="font-size:11px;color:#475569;margin-bottom:4px;">Regulatory Context</div><div style="font-size:13px;color:#94a3b8;">{regulatory}</div></div>' if regulatory else ''}
  </div>

  <!-- MATURITY STAGE OVERVIEW -->
  <h2>Maturity Stage Positioning</h2>
  <div class="card">
    {stage_bar}
    <div style="font-size:11px;color:#475569;text-align:center;margin-top:8px;">
      White circle = Current State &nbsp;|&nbsp; Green dashed = Target State
    </div>
  </div>

  <!-- RADAR CHART -->
  <h2>Capability Radar</h2>
  <div class="card" style="display:flex;justify-content:center;align-items:center;flex-wrap:wrap;gap:24px;">
    <div>{radar_js}</div>
    <div style="flex:1;min-width:200px;">
      <div style="font-size:13px;color:#64748b;margin-bottom:12px;">Scores by dimension (0–5 scale, matching maturity stage)</div>
      <table style="width:100%;border-collapse:collapse;">
        <thead>
          <tr style="border-bottom:1px solid #1e293b;">
            <th style="font-size:11px;color:#475569;text-align:left;padding:4px 6px;">Dimension</th>
            <th style="font-size:11px;color:#475569;text-align:center;padding:4px 6px;">Current</th>
            <th style="font-size:11px;color:#475569;text-align:center;padding:4px 6px;">Target</th>
            <th style="font-size:11px;color:#475569;text-align:center;padding:4px 6px;">Gap</th>
          </tr>
        </thead>
        <tbody>
          {''.join(
            f'<tr style="border-bottom:1px solid #0f172a;"><td style="padding:5px 6px;font-size:12px;color:#e2e8f0;">{DIMENSION_SHORT.get(d,d)}</td>'
            f'<td style="padding:5px 6px;text-align:center;font-size:12px;font-weight:700;color:{stage_color(dim_scores[d]["current"])};">{dim_scores[d]["current"]:.1f}</td>'
            f'<td style="padding:5px 6px;text-align:center;font-size:12px;color:#10b981;">{dim_scores[d]["target"]:.1f}</td>'
            f'<td style="padding:5px 6px;text-align:center;font-size:12px;color:#f59e0b;">+{(dim_scores[d]["target"] or 0)-(dim_scores[d]["current"] or 0):.1f}</td></tr>'
            for d in framework["dimensions"] if d in dim_scores and dim_scores[d]["current"] is not None
          )}
        </tbody>
      </table>
    </div>
  </div>

  <!-- PRIORITISED GAP TABLE -->
  <h2>Prioritised Gap Analysis</h2>
  <div class="card" style="overflow-x:auto;">{gap_table}</div>

  <!-- DIMENSION DEEP-DIVES -->
  <h2>Dimension Detail</h2>
  {dim_cards}

  <!-- TRANSFORMATION ROADMAP -->
  <h2>Transformation Roadmap</h2>
  <div class="card">{roadmap}</div>

  <!-- FRAMEWORK PRINCIPLES -->
  <h2>Framework Principles</h2>
  <div class="card">{principles}</div>

  <!-- MATURITY STAGE REFERENCE -->
  <h2>Maturity Stage Reference</h2>
  <div class="card" style="overflow-x:auto;">
    <table style="width:100%;border-collapse:collapse;min-width:700px;">
      <thead>
        <tr style="border-bottom:2px solid #334155;">
          <th style="padding:10px 8px;font-size:12px;color:#475569;text-align:left;">Stage</th>
          <th style="padding:10px 8px;font-size:12px;color:#475569;text-align:left;">Label</th>
          <th style="padding:10px 8px;font-size:12px;color:#475569;text-align:left;">Autonomy Level</th>
          <th style="padding:10px 8px;font-size:12px;color:#475569;text-align:left;">Human Model</th>
          <th style="padding:10px 8px;font-size:12px;color:#475569;text-align:left;">Governance Model</th>
          <th style="padding:10px 8px;font-size:12px;color:#475569;text-align:left;">Typical Year</th>
        </tr>
      </thead>
      <tbody>
        {''.join(
          f'<tr style="border-bottom:1px solid #1e293b;">'
          f'<td style="padding:10px 8px;"><span style="background:{STAGE_COLORS[int(sid)]};color:#fff;padding:3px 10px;border-radius:4px;font-weight:700;">{sid}</span></td>'
          f'<td style="padding:10px 8px;font-size:13px;color:#f1f5f9;font-weight:600;">{s["label"]}</td>'
          f'<td style="padding:10px 8px;font-size:12px;color:#94a3b8;">{s["autonomy_level"][:80]}…</td>'
          f'<td style="padding:10px 8px;font-size:12px;color:#94a3b8;">{s["human_model"][:80]}…</td>'
          f'<td style="padding:10px 8px;font-size:12px;color:#94a3b8;">{s["governance_model"][:80]}…</td>'
          f'<td style="padding:10px 8px;font-size:12px;color:#64748b;">{s["typical_year"]}</td>'
          f'</tr>'
          for sid, s in framework["maturity_stages"].items()
        )}
      </tbody>
    </table>
  </div>

  <!-- FOOTER -->
  <div style="margin-top:40px;padding-top:16px;border-top:1px solid #1e293b;display:flex;justify-content:space-between;align-items:center;">
    <div style="font-size:11px;color:#334155;">Agentic SOC Maturity Framework (ASMF) v1.0 &nbsp;|&nbsp; {date}</div>
    <div style="font-size:11px;color:#334155;">{org} &nbsp;|&nbsp; Confidential</div>
  </div>

</div>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="ASMF Report Generator")
    parser.add_argument("--assessment", default=None, help="Path to assessment JSON file")
    parser.add_argument("--output", default=None, help="Output HTML file path")
    parser.add_argument("--demo", action="store_true", help="Generate a demo report with sample scores")
    args = parser.parse_args()

    framework = load_framework()

    if args.demo or args.assessment is None:
        print("[INFO] Using demo assessment data...")
        assessment = build_demo_assessment(framework)
        out_file = args.output or "agentic_soc_report_demo.html"
    else:
        with open(args.assessment, encoding="utf-8") as f:
            assessment = json.load(f)
        org = assessment.get("assessment_metadata", {}).get("organization", "org").lower()
        org_slug = "".join(c if c.isalnum() else "_" for c in org)[:20]
        date_slug = datetime.today().strftime("%Y%m%d")
        out_file = args.output or f"agentic_soc_report_{org_slug}_{date_slug}.html"

    dim_scores, overall_current, overall_target = compute_scores(framework, assessment)

    if overall_current is None:
        print("[ERROR] No valid scores found in assessment. Make sure current_stage fields are populated.")
        sys.exit(1)

    html = generate_html(framework, assessment, dim_scores, overall_current, overall_target)

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK] Report generated: {out_file}")
    print(f"     Organization:    {assessment.get('assessment_metadata', {}).get('organization', 'N/A')}")
    print(f"     Overall Current: {overall_current:.2f} ({stage_label(overall_current)})")
    print(f"     Overall Target:  {overall_target:.2f} ({stage_label(overall_target)})")
    print(f"     Total Gap:       +{overall_target - overall_current:.2f}")


if __name__ == "__main__":
    main()
