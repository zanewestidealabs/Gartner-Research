"""Add Graphics tab data to Analyst Take reports."""
import json
import os

JSON_PATH = os.path.join(os.path.dirname(__file__), 'analyst_take_reports.json')

# ── SVG Graphics for AIUC-1 reports ──────────────────────────────────────

# Graphic 1: The Compliance Gap — shows SOC2/HIPAA/PCI as layers that DON'T cover AI agent behavior
AIUC_GRAPHIC_1_SVG = '''<svg viewBox="0 0 700 420" xmlns="http://www.w3.org/2000/svg" style="max-width:680px;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;">
  <!-- Background -->
  <rect width="700" height="420" rx="12" fill="#1a1a2e"/>
  <!-- Title -->
  <text x="350" y="36" text-anchor="middle" fill="#fff" font-size="16" font-weight="700">The AI Compliance Gap: What Traditional Frameworks Actually Audit</text>
  <!-- Left column: What's Covered -->
  <text x="190" y="68" text-anchor="middle" fill="#6dd47e" font-size="12" font-weight="700">✓ WHAT TRADITIONAL FRAMEWORKS COVER</text>
  <!-- SOC 2 -->
  <rect x="30" y="82" width="320" height="50" rx="8" fill="#1e3a3a" stroke="#2d8a6e" stroke-width="1.5"/>
  <text x="46" y="105" fill="#6dd47e" font-size="11" font-weight="700">SOC 2 TYPE II</text>
  <text x="46" y="122" fill="#a0b4b0" font-size="10">Infrastructure · Access controls · Change mgmt</text>
  <circle cx="330" cy="107" r="10" fill="#2d8a6e"/><text x="330" y="111" text-anchor="middle" fill="#fff" font-size="10" font-weight="700">✓</text>
  <!-- HIPAA -->
  <rect x="30" y="140" width="320" height="50" rx="8" fill="#1e3a3a" stroke="#2d8a6e" stroke-width="1.5"/>
  <text x="46" y="163" fill="#6dd47e" font-size="11" font-weight="700">HIPAA</text>
  <text x="46" y="180" fill="#a0b4b0" font-size="10">PHI safeguards · Administrative controls · BAAs</text>
  <circle cx="330" cy="165" r="10" fill="#2d8a6e"/><text x="330" y="169" text-anchor="middle" fill="#fff" font-size="10" font-weight="700">✓</text>
  <!-- PCI DSS -->
  <rect x="30" y="198" width="320" height="50" rx="8" fill="#1e3a3a" stroke="#2d8a6e" stroke-width="1.5"/>
  <text x="46" y="221" fill="#6dd47e" font-size="11" font-weight="700">PCI DSS</text>
  <text x="46" y="238" fill="#a0b4b0" font-size="10">Cardholder data environment · Network segmentation</text>
  <circle cx="330" cy="223" r="10" fill="#2d8a6e"/><text x="330" y="227" text-anchor="middle" fill="#fff" font-size="10" font-weight="700">✓</text>
  <!-- Right column: What's NOT Covered (the gap) -->
  <text x="530" y="68" text-anchor="middle" fill="#e05252" font-size="12" font-weight="700">✗ WHAT NO FRAMEWORK AUDITS</text>
  <!-- Gap items -->
  <rect x="390" y="82" width="280" height="40" rx="8" fill="#3a1e1e" stroke="#a83232" stroke-width="1.5" stroke-dasharray="6,3"/>
  <text x="406" y="106" fill="#f08080" font-size="10" font-weight="600">AI agent reasoning chains</text>
  <rect x="390" y="130" width="280" height="40" rx="8" fill="#3a1e1e" stroke="#a83232" stroke-width="1.5" stroke-dasharray="6,3"/>
  <text x="406" y="154" fill="#f08080" font-size="10" font-weight="600">Autonomous tool call sequences</text>
  <rect x="390" y="178" width="280" height="40" rx="8" fill="#3a1e1e" stroke="#a83232" stroke-width="1.5" stroke-dasharray="6,3"/>
  <text x="406" y="202" fill="#f08080" font-size="10" font-weight="600">Hallucination rates &amp; testing</text>
  <rect x="390" y="226" width="280" height="40" rx="8" fill="#3a1e1e" stroke="#a83232" stroke-width="1.5" stroke-dasharray="6,3"/>
  <text x="406" y="250" fill="#f08080" font-size="10" font-weight="600">Cross-customer data isolation in AI</text>
  <!-- AIUC-1 Bridge -->
  <rect x="100" y="275" width="500" height="60" rx="10" fill="#162447" stroke="#0078d4" stroke-width="2"/>
  <text x="350" y="300" text-anchor="middle" fill="#5bb8f5" font-size="14" font-weight="800">AIUC-1: THE MISSING COMPLIANCE LAYER</text>
  <text x="350" y="320" text-anchor="middle" fill="#8cb4d4" font-size="11">6 control categories · 40+ requirements · Third-party validated</text>
  <!-- Arrow -->
  <path d="M350 335 L350 355" stroke="#0078d4" stroke-width="2" marker-end="url(#arrowBlue)"/>
  <defs><marker id="arrowBlue" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6" fill="#0078d4"/></marker></defs>
  <!-- Bottom outcome -->
  <rect x="150" y="355" width="400" height="45" rx="8" fill="#0e2a0e" stroke="#2d8a6e" stroke-width="1.5"/>
  <text x="350" y="376" text-anchor="middle" fill="#6dd47e" font-size="12" font-weight="700">Auditable AI Governance</text>
  <text x="350" y="392" text-anchor="middle" fill="#a0b4b0" font-size="10">Knowledge graphs · Lineage trails · Continuous testing</text>
</svg>'''

# Graphic 2: The Compliance Model Flip — vendor-side vs customer-side obligations
AIUC_GRAPHIC_2_SVG = '''<svg viewBox="0 0 700 380" xmlns="http://www.w3.org/2000/svg" style="max-width:680px;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;">
  <!-- Background -->
  <rect width="700" height="380" rx="12" fill="#1a1a2e"/>
  <!-- Title -->
  <text x="350" y="36" text-anchor="middle" fill="#fff" font-size="16" font-weight="700">AIUC-1 Flips the Compliance Model</text>
  <text x="350" y="56" text-anchor="middle" fill="#8899aa" font-size="11">78.6% of AIUC-1 requirements are vendor obligations, not customer obligations</text>
  <!-- Left: Traditional Model -->
  <text x="180" y="86" text-anchor="middle" fill="#e05252" font-size="13" font-weight="700">TRADITIONAL MODEL</text>
  <text x="180" y="102" text-anchor="middle" fill="#8899aa" font-size="10">(SOC 2 / HIPAA / PCI DSS)</text>
  <!-- Customer burden - large -->
  <rect x="60" y="115" width="240" height="140" rx="10" fill="#3a1e1e" stroke="#a83232" stroke-width="1.5"/>
  <text x="180" y="145" text-anchor="middle" fill="#f08080" font-size="24" font-weight="800">CUSTOMER</text>
  <text x="180" y="170" text-anchor="middle" fill="#f08080" font-size="12">Internal audit programs</text>
  <text x="180" y="186" text-anchor="middle" fill="#f08080" font-size="12">Dedicated compliance teams</text>
  <text x="180" y="202" text-anchor="middle" fill="#f08080" font-size="12">Annual assessment cycles</text>
  <text x="180" y="218" text-anchor="middle" fill="#f08080" font-size="12">Scales poorly for SMBs</text>
  <text x="180" y="242" text-anchor="middle" fill="#cc9999" font-size="10" font-style="italic">Heavy burden on every buyer</text>
  <!-- Vendor burden - small -->
  <rect x="110" y="262" width="140" height="48" rx="8" fill="#1e3a3a" stroke="#2d8a6e" stroke-width="1"/>
  <text x="180" y="283" text-anchor="middle" fill="#a0b4b0" font-size="11" font-weight="600">VENDOR</text>
  <text x="180" y="298" text-anchor="middle" fill="#a0b4b0" font-size="9">Self-attestation</text>
  <!-- VS divider -->
  <text x="350" y="200" text-anchor="middle" fill="#556677" font-size="22" font-weight="800">→</text>
  <!-- Right: AIUC-1 Model -->
  <text x="520" y="86" text-anchor="middle" fill="#5bb8f5" font-size="13" font-weight="700">AIUC-1 MODEL</text>
  <text x="520" y="102" text-anchor="middle" fill="#8899aa" font-size="10">(Vendor-side certification)</text>
  <!-- Customer burden - small -->
  <rect x="450" y="115" width="140" height="48" rx="8" fill="#1a2a1a" stroke="#2d8a6e" stroke-width="1"/>
  <text x="520" y="136" text-anchor="middle" fill="#6dd47e" font-size="11" font-weight="600">CUSTOMER</text>
  <text x="520" y="151" text-anchor="middle" fill="#a0b4b0" font-size="9">"Show me your results"</text>
  <!-- Vendor burden - large -->
  <rect x="400" y="175" width="240" height="140" rx="10" fill="#162447" stroke="#0078d4" stroke-width="1.5"/>
  <text x="520" y="205" text-anchor="middle" fill="#5bb8f5" font-size="24" font-weight="800">VENDOR</text>
  <text x="520" y="230" text-anchor="middle" fill="#5bb8f5" font-size="12">Third-party testing mandates</text>
  <text x="520" y="246" text-anchor="middle" fill="#5bb8f5" font-size="12">Standardized test artifacts</text>
  <text x="520" y="262" text-anchor="middle" fill="#5bb8f5" font-size="12">Hallucination &amp; safety testing</text>
  <text x="520" y="278" text-anchor="middle" fill="#5bb8f5" font-size="12">Continuous validation cycles</text>
  <text x="520" y="302" text-anchor="middle" fill="#8cb4d4" font-size="10" font-style="italic">Binary signal: pass or fail</text>
  <!-- Bottom insight -->
  <rect x="100" y="330" width="500" height="36" rx="8" fill="#0e2a0e" stroke="#2d8a6e" stroke-width="1.5"/>
  <text x="350" y="353" text-anchor="middle" fill="#6dd47e" font-size="12" font-weight="700">A 200-person clinic gets the same assurance as a major health system</text>
</svg>'''


def main():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    reports = data['reports']

    for r in reports:
        rid = r['id']

        # ── Template: add graphics guidance to writing guide ──
        if rid == 'analyst-take-template':
            g = r.get('guidance', {})
            # Add graphics guidance section
            g['graphics_guidance'] = {
                "requirement": "Every Analyst Take should include 2 original graphics that visually articulate the core argument.",
                "guidelines": [
                    "Each graphic should communicate one key insight — readers should grasp it within 5 seconds",
                    "Use high-contrast, dark-mode-friendly color palettes",
                    "Include a descriptive title, caption, and key takeaway for each graphic",
                    "Graphic 1 should typically visualize the core problem or gap being addressed",
                    "Graphic 2 should typically visualize the solution, framework, or recommended approach",
                    "Prefer diagrams, comparison charts, and process flows over decorative imagery",
                    "Keep text in graphics minimal — labels, not paragraphs",
                    "Graphics should stand alone — a reader seeing only the graphics should understand the argument"
                ],
                "graphic_types": [
                    "Gap analysis (what exists vs. what's missing)",
                    "Before/after comparison",
                    "Process flow or decision tree",
                    "Framework overview or control mapping",
                    "Maturity model progression",
                    "Risk/impact matrix"
                ]
            }
            # Add to checklist
            checklist = g.get('good_take_checklist', [])
            if 'Includes 2 original graphics' not in str(checklist):
                checklist.append('Includes 2 original graphics that visually articulate the core argument')
            g['good_take_checklist'] = checklist
            r['guidance'] = g

            # Add empty graphics array to template
            r['graphics'] = []
            print(f"  ✓ {rid}: added graphics guidance to writing guide")

        # ── AIUC v1: add 2 graphics ──
        elif rid == 'aiuc1-agentic-compliance':
            r['graphics'] = [
                {
                    "title": "The AI Compliance Gap",
                    "purpose": "Illustrates what traditional compliance frameworks audit vs. the AI agent behaviors that fall completely outside their scope",
                    "svg": AIUC_GRAPHIC_1_SVG,
                    "caption": "SOC 2, HIPAA, and PCI DSS audit infrastructure and safeguards — but none examine AI agent reasoning chains, tool call sequences, hallucination rates, or cross-customer data isolation. AIUC-1 closes this gap with 6 control categories and third-party validation.",
                    "takeaway": "Your organization may be fully compliant with every traditional framework and still have zero visibility into what AI agents are doing with regulated data."
                },
                {
                    "title": "The Compliance Model Flip",
                    "purpose": "Shows how AIUC-1 shifts the compliance burden from customer-side audit programs to vendor-side certification — making AI governance accessible to organizations of any size",
                    "svg": AIUC_GRAPHIC_2_SVG,
                    "caption": "Traditional frameworks require buyers to build internal audit capabilities that scale poorly. AIUC-1 inverts this: 78.6% of requirements are vendor obligations, producing standardized test artifacts that any buyer can evaluate.",
                    "takeaway": "AIUC-1 works as a binary signal — vendors either pass third-party testing or they don't. A 200-person clinic gets the same assurance as a major health system."
                }
            ]
            print(f"  ✓ {rid}: added 2 graphics")

        # ── AIUC v2: add same 2 graphics (same argument, smart brevity edit) ──
        elif rid == 'aiuc1-agentic-compliance-v2':
            r['graphics'] = [
                {
                    "title": "The AI Compliance Gap",
                    "purpose": "Illustrates what traditional compliance frameworks audit vs. the AI agent behaviors that fall completely outside their scope",
                    "svg": AIUC_GRAPHIC_1_SVG,
                    "caption": "SOC 2, HIPAA, and PCI DSS audit infrastructure and safeguards — but none examine AI agent reasoning chains, tool call sequences, hallucination rates, or cross-customer data isolation. AIUC-1 closes this gap with 6 control categories and third-party validation.",
                    "takeaway": "Your organization may be fully compliant with every traditional framework and still have zero visibility into what AI agents are doing with regulated data."
                },
                {
                    "title": "The Compliance Model Flip",
                    "purpose": "Shows how AIUC-1 shifts the compliance burden from customer-side audit programs to vendor-side certification — making AI governance accessible to organizations of any size",
                    "svg": AIUC_GRAPHIC_2_SVG,
                    "caption": "Traditional frameworks require buyers to build internal audit capabilities that scale poorly. AIUC-1 inverts this: 78.6% of requirements are vendor obligations, producing standardized test artifacts that any buyer can evaluate.",
                    "takeaway": "AIUC-1 works as a binary signal — vendors either pass third-party testing or they don't. A 200-person clinic gets the same assurance as a major health system."
                }
            ]
            print(f"  ✓ {rid}: added 2 graphics")

    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Updated {JSON_PATH}")


if __name__ == '__main__':
    main()
