# Quick Start: Researched vs Validated Comparison Widget

## Location
- **Page**: Analysis tab
- **Widget**: "Researched vs Validated Analysis" 
- **Position**: Takes up 3 columns × 2 rows in the dashboard grid

## What It Does

Compares average vendor scores from two phases:
1. **Researched Phase** (📊 Blue radar) - Initial research scores
2. **Validated Phase** (✓ Green radar) - Final validated/confirmed scores

Shows you:
- How vendor capabilities measured during research
- How those same capabilities measured after validation
- Where research was accurate, overstated, or understated

---

## How to Use

### Step 1: Open Configuration
Click the **gear icon (⚙)** in the widget header

![Widget Header]
```
┌─────────────────────────────────────────┐
│ Researched vs Validated Analysis    ⚙   │
└─────────────────────────────────────────┘
```

### Step 2: Select Category Type
Choose what vendors to compare:

| Option | Description | Example |
|--------|-------------|---------|
| **All Vendors** | Entire vendor database | Compare all 300+ vendors |
| **Region** | By geographic region | "Global", "North America" |
| **Startup / Established** | Company maturity | "Startup" or "Established" |
| **AI-First / Traditional** | AI approach | "AI-First" or "Traditional" |
| **IR Focus Type** | Service model | "Core Competency" or "Assistance Component" |

### Step 3: Select Category Value
(Only if not "All Vendors")

Available options auto-populate based on your vendor data:
- **Region**: Global, North America, Europe, APAC, etc.
- **Startup**: Startup or Established
- **AI-First**: AI-First or Traditional
- **IR Focus Type**: Core Competency, Assistance Component, etc.

### Step 4: Choose Axes (Dimensions)
Select what to measure:

| Option | Dimensions | Use Case |
|--------|-----------|----------|
| **Pillars** (default) | 5 main pillars | High-level overview |
| **Sub-pillars** | 20 detailed capabilities | Deep dive analysis |
| **Both** | All 25 dimensions | Comprehensive view |

**The 5 Pillars**:
- **PLA**: Planning - Organizational Readiness
- **INV**: Investigation - Evidence & Analysis
- **REM**: Remediation - Threat Containment
- **PMG**: Program Management - Incident Lifecycle
- **LAW**: Legal - Judicial Support

### Step 5: Toggle Delta Metrics (Optional)
Enable/disable the "Delta Analysis" table:
- ☑ Enabled (default): Shows detailed comparison table
- ☐ Disabled: Shows only radar charts

### Step 6: Click Save
Configuration is applied and saved to your browser

---

## Reading the Results

### Visual Comparison (Radar Charts)

```
Researched Scores (Blue)          Validated Scores (Green)
        
            PLA                           PLA
          /     \                       /     \
       PMG       INV                 PMG       INV
        |         |                   |         |
       LAW       REM                 LAW       REM
          \     /                       \     /
           REM                           REM
```

**What to look for**:
- **Blue extends farther**: Research scores were higher
- **Green extends farther**: Validation revealed stronger capabilities
- **Same shape**: Research was accurate

### Delta Analysis Table

| Metric | Researched | Validated | Delta | % Δ |
|--------|-----------|-----------|-------|-----|
| PLA | 3.50 | 3.68 | 🟢 +0.18 | +5% |
| INV | 4.25 | 4.10 | 🔴 -0.15 | -4% |
| REM | 3.80 | 4.02 | 🟢 +0.22 | +6% |
| PMG | 3.45 | 3.51 | ⚪ +0.06 | +2% |
| LAW | 3.20 | 3.25 | ⚪ +0.05 | +2% |

**Understanding the colors**:
- 🟢 **Green**: Validated score higher (research was conservative)
- 🔴 **Orange**: Validated score lower (research was optimistic)
- ⚪ **Gray**: Difference <0.05 (minimal change)

---

## Example Scenarios

### Scenario 1: Compare All Global Vendors
1. Open configuration
2. Select: Category Type = "Region" → Value = "Global"
3. Axes = "Pillars"
4. Enable Delta
5. **Result**: See how researched vs validated scores differ for all global vendors

**Questions answered**:
- Did global vendors meet research expectations?
- Which pillars were underestimated?
- Which were overestimated?

### Scenario 2: Startup vs Established Deep Dive
1. Open configuration
2. **First comparison**: Category = "Startup/Established" → "Startup", Axes = "Sub-pillars"
3. **Note down** the delta values
4. Click gear again
5. **Second comparison**: Same settings but select "Established"
6. **Compare**: Which type has bigger research/validation gaps?

**Questions answered**:
- Do startups have more measurement uncertainty?
- Which company type has more accurate research?
- Which capabilities are hardest to assess?

### Scenario 3: AI-First Investigation
1. Open configuration
2. Category = "AI-First / Traditional" → "AI-First"
3. Axes = "Both" (all 25 dimensions)
4. Enable Delta
5. **Result**: Detailed analysis of 25 AI-focused capabilities

**Questions answered**:
- Are AI vendors measured differently?
- Which AI capabilities were over/understated?
- Validation confidence in AI assessments?

---

## Interpretation Guide

### What Delta Tells You

**Positive Delta (+) - Green**
- Validated score > Researched score
- Interpretation: Research was conservative/cautious
- Vendor actually stronger than initially assessed
- Example: Thought INV was 4.0, validated as 4.25

**Negative Delta (-) - Orange**
- Validated score < Researched score
- Interpretation: Research was optimistic
- Vendor not as strong as initially assessed
- Example: Thought REM was 4.5, validated as 4.2

**Neutral Delta (≈) - Gray**
- Difference < 0.05
- Interpretation: Research was accurate
- No significant change during validation

### Large Deltas (|Delta| > 0.3)
High deltas might indicate:
- Significant assessment errors
- Categories that changed implementation
- Areas needing re-research
- Data quality issues

---

## Tips & Tricks

### 💡 Tip 1: Find Assessment Gaps
- Look for pillars with largest absolute deltas
- Those indicate least accurate research

### 💡 Tip 2: Compare Categories
- Run comparison for Region A, then Region B
- See if research quality varies geographically

### 💡 Tip 3: Validation Confidence
- Large deltas = low confidence in research
- Small deltas = research was reliable

### 💡 Tip 4: Market Insights
- Compare "All Vendors" with subcategories
- See how different segments were assessed

### 💡 Tip 5: Deep Dive
- Start with Pillars (5 dimensions)
- Switch to Both (25 dimensions) for details
- Identify which sub-pillars caused delta

---

## Widget Settings

Settings automatically save to your browser. To reset:
1. Click gear icon
2. Set to defaults:
   - Category Type: "All Vendors"
   - Axes: "Pillars"
   - Delta: Enabled
3. Click Save

To hide widget entirely:
- Click "⚙ Customize Widgets" button at top
- Uncheck "Researched vs Validated Comparison"
- Click Save Preferences

---

## Frequently Asked Questions

**Q: Why are some deltas negative?**
A: Means validated scores were lower than researched scores. Common and normal - indicates research may have been optimistic.

**Q: What does vendor count mean?**
A: The number in parentheses (n=45) shows how many vendors match your selected category.

**Q: Can I compare just two specific vendors?**
A: This widget compares categories (cohorts). Use the "Comparison Radar" widget for individual vendor comparisons.

**Q: Why are some values 0?**
A: Vendors without data in that dimension. Uses available data to calculate averages.

**Q: What's the difference between Sub-pillars and Both?**
A: "Sub-pillars" shows only the 20 detailed dimensions. "Both" shows all 5 main pillars + 20 sub-pillars = 25 total.

**Q: Does filtering affect the widget?**
A: Yes! If you apply filters on the Analysis page, this widget updates to show only filtered vendors.

**Q: Can I export the data?**
A: Currently visual only. You can screenshot or manually record values from the delta table.

---

## Troubleshooting

**Widget shows "No vendors match"**
- Category value you selected doesn't exist
- Try different region or category type
- Click gear and re-select value

**Numbers look wrong**
- Check vendor data file has been loaded
- Verify "Score Mode" dropdown (top right) is not set incorrectly
- Refresh page to reload data

**Radar charts not appearing**
- Browser may be blocking SVG rendering
- Try different browser
- Clear cache and refresh

**Settings not saving**
- Browser localStorage may be disabled
- Check privacy/incognito mode settings
- Try regular (non-private) browsing

---

## Next Steps

Now that you have the Researched vs Validated widget, you can:

1. **Identify Measurement Gaps**: Which capabilities were hardest to assess?
2. **Improve Research Process**: Use deltas to calibrate future research
3. **Market Analysis**: Compare how different segments were validated
4. **Quality Metrics**: Track validation accuracy over time
5. **Risk Assessment**: Large deltas = high uncertainty areas

Enjoy your new analysis capabilities! 🎉
