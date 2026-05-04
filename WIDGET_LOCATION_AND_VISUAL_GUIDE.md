# Widget Location & Visual Guide

## Where to Find It

**Page**: Analysis (📈 tab on left navigation)  
**Section**: Main dashboard grid  
**Widget Title**: "Researched vs Validated Analysis"  
**Default State**: Visible and enabled  

---

## Page Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  DFIR Vendor Marketplace Analysis 2026                    ⚙ 🌙   │
│  Filter and analyze incident response vendors                   │
└──────────────────────────────────────────────────────────────────┘

Navigation                          Main Content Area
├─ 📊 Dashboard                    ┌────────────────────────────────┐
├─ 🏢 Vendors                      │  Filters & Search               │
├─ 📈 Analysis  ← YOU ARE HERE    │  [Active Filters Panel]        │
├─ 🧮 Cross-Section               ├────────────────────────────────┤
└─ 📖 Legend                       │  Analytics & Reporting         │
                                   │  ⚙ Customize Widgets          │
                                   │                                │
                                   │  ╔══════════╦══════════════╗   │
                                   │  ║ Region   ║ Pillar       ║   │
                                   │  ║ Chart    ║ Chart        ║   │
                                   │  ╚══════════╩══════════════╝   │
                                   │                                │
                                   │  ╔══════════╦══════════════╗   │
                                   │  ║ Spec.    ║ Type         ║   │
                                   │  ║ Chart    ║ Chart        ║   │
                                   │  ╚══════════╩══════════════╝   │
                                   │                                │
                                   │  ╔══════════╦══════════════╗   │
                                   │  ║ AI       ║ Startup      ║   │
                                   │  ║ Chart    ║ Chart        ║   │
                                   │  ╚══════════╩══════════════╝   │
                                   │                                │
                                   │  ╔════════════════════════╗    │
                                   │  ║ Pillar Radar           ║    │
                                   │  ║                        ║    │
                                   │  ╚════════════════════════╝    │
                                   │                                │
                                   │  ╔════════════════════════╗    │
                                   │  ║ Comparison Radar       ║    │
                                   │  ║ (5 vendors)            ║    │
                                   │  ╚════════════════════════╝    │
                                   │                                │
                                   │  ╔════════════════════════════╗│
                                   │  ║ NEW: Researched vs Validated║
                                   │  ║ [⚙]                    ║ ≡ ║
                                   │  ║                            ║
                                   │  ║  All Vendors (n=300)       ║
                                   │  ║                            ║
                                   │  ║  ╔════════╗  ╔════════╗    ║
                                   │  ║  ║📊Res.  ║  ║✓Val.   ║    ║
                                   │  ║  ║Radar   ║  ║Radar   ║    ║
                                   │  ║  ╚════════╝  ╚════════╝    ║
                                   │  ║                            ║
                                   │  ║  Delta Analysis Table      ║
                                   │  ║  ┌─────────────────────┐  ║
                                   │  ║  │ PLA  3.75  3.85  +.1│  ║
                                   │  ║  │ INV  4.20  4.15  -.1│  ║
                                   │  ║  │ REM  3.95  4.10  +.2│  ║
                                   │  ║  │ PMG  3.60  3.62  +.0│  ║
                                   │  ║  │ LAW  3.40  3.45  +.0│  ║
                                   │  ║  └─────────────────────┘  ║
                                   │  ╚════════════════════════════╝
                                   │                                │
                                   │  ╔════════════════════════╗    │
                                   │  ║ Summary Statistics     ║    │
                                   │  ║ Count: 300  Avg: 3.85  ║    │
                                   │  ╚════════════════════════╝    │
                                   └────────────────────────────────┘
```

---

## Widget Appearance

### In Dashboard View

```
┌──────────────────────────────────────────────────────────────────┐
│  Researched vs Validated Analysis                    ⚙      ≡     │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│                      All Vendors (n=300)                         │
│                                                                   │
│         ┌──────────────────────┐    ┌──────────────────────┐    │
│         │   📊 Researched      │    │   ✓ Validated       │    │
│         │      Scores          │    │      Scores          │    │
│         │                      │    │                      │    │
│         │        PLA           │    │        PLA           │    │
│         │       /   \          │    │       /   \          │    │
│         │      /     \         │    │      /     \         │    │
│         │    PMG     INV       │    │    PMG     INV       │    │
│         │     |       |        │    │     |       |        │    │
│         │    LAW     REM       │    │    LAW     REM       │    │
│         │      \     /         │    │      \     /         │    │
│         │       \   /          │    │       \   /          │    │
│         │        REM          │    │        REM           │    │
│         │  [Blue overlay]      │    │  [Green overlay]     │    │
│         └──────────────────────┘    └──────────────────────┘    │
│                                                                   │
│  Delta Analysis (Validated - Researched)                         │
│  ┌─────────┬───────────┬──────────┬────────┬────────┐           │
│  │ Metric  │Researched │Validated │  Delta │  % Δ   │           │
│  ├─────────┼───────────┼──────────┼────────┼────────┤           │
│  │ PLA     │   3.50    │   3.68   │ 🟢+0.18│  +5%   │           │
│  │ INV     │   4.25    │   4.10   │ 🔴-0.15│  -4%   │           │
│  │ REM     │   3.80    │   4.02   │ 🟢+0.22│  +6%   │           │
│  │ PMG     │   3.45    │   3.51   │ ⚪+0.06│  +2%   │           │
│  │ LAW     │   3.20    │   3.25   │ ⚪+0.05│  +2%   │           │
│  └─────────┴───────────┴──────────┴────────┴────────┘           │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Configuration Modal

```
┌────────────────────────────────────────────────────────────────────┐
│ Configure Researched vs Validated Comparison              [×]     │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Category Type                         Category Value             │
│  ┌──────────────────────────────┐     ┌──────────────────────┐   │
│  │▼ All Vendors                 │     │▼ N/A - All Vendors   │   │
│  │  Region                      │     │                      │   │
│  │  Startup / Established       │     │                      │   │
│  │  AI-First / Traditional      │     │                      │   │
│  │  IR Focus Type               │     │                      │   │
│  └──────────────────────────────┘     └──────────────────────┘   │
│                                                                    │
│  Axes                                                              │
│  ┌──────────────────────────────┐                                │
│  │▼ Pillars (5)                 │                                │
│  │  Sub-pillars (20)            │                                │
│  │  Both (25)                   │                                │
│  └──────────────────────────────┘                                │
│                                                                    │
│  ☑ Show Delta (Difference) Metrics                               │
│                                                                    │
│                                    [Save]  [Cancel]              │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### When Category Type is "Region"

```
┌────────────────────────────────────────────────────────────────────┐
│ Configure Researched vs Validated Comparison              [×]     │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Category Type                         Category Value             │
│  ┌──────────────────────────────┐     ┌──────────────────────┐   │
│  │▼ Region (contains)           │     │▼ Select...           │   │
│  │  All Vendors                 │     │  Global              │   │
│  │  Startup / Established       │     │  North America       │   │
│  │  AI-First / Traditional      │     │  Europe              │   │
│  │  IR Focus Type               │     │  APAC                │   │
│  └──────────────────────────────┘     │  Latin America       │   │
│                                        └──────────────────────┘   │
│                                                                    │
│  Axes                                                              │
│  ┌──────────────────────────────┐                                │
│  │▼ Pillars (5)                 │                                │
│  │  Sub-pillars (20)            │                                │
│  │  Both (25)                   │                                │
│  └──────────────────────────────┘                                │
│                                                                    │
│  ☑ Show Delta (Difference) Metrics                               │
│                                                                    │
│                                    [Save]  [Cancel]              │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Widget Position in Grid

The widget occupies a **3×2 grid slot** (3 columns wide, 2 rows tall):

```
Row 1  [1col: Region]  [1col: Pillar]  [1col: Spec]
Row 2  [1col: Type]    [1col: AI]       [1col: Startup]
Row 3  [2col: Radar]            [2col: Radar]
Row 4  [2col: Radar]            [2col: Radar]
Row 5  ┌─────────────────────────────────────────┐
Row 6  │  NEW WIDGET (3 cols × 2 rows)           │
       │  - Side-by-side radars                  │
       │  - Delta analysis table                 │
       └─────────────────────────────────────────┘
Row 7  [Summary Stats (full width)]
```

---

## Color Scheme

### Radar Chart Colors

```
Researched Radar          Validated Radar
└─ Blue (#0078d4)        └─ Green (#107c10)
   Fill: rgba(0,120,212,0.18)  Fill: rgba(16,124,16,0.18)
```

### Delta Metrics Colors

```
Positive Delta (🟢 Green #107c10)
  └─ Validated score > Researched score
  └─ Research was conservative

Negative Delta (🔴 Orange #d83b01)
  └─ Validated score < Researched score
  └─ Research was optimistic

Neutral Delta (⚪ Gray #a19f9d)
  └─ |Delta| < 0.05
  └─ Research was accurate
```

---

## Interactive Elements

### Gear Icon (⚙)
- **Location**: Top-right of widget header
- **Action**: Click to open configuration modal
- **Tooltip**: "Configure Comparison"

### Configuration Modal
- **Close**: Click [×] button or click outside modal
- **Save**: Click [Save] to apply changes
- **Cancel**: Click [Cancel] to discard changes

### Category Dropdowns
- **Type dropdown**: Changes available category values
- **Value dropdown**: Populated based on vendor data
- **Auto-disable**: Value field disabled when Type = "All Vendors"

### Axes Selection
- **Pillars** (default): 5 main dimensions
- **Sub-pillars**: 20 detailed dimensions
- **Both**: All 25 dimensions combined

### Delta Toggle
- **Enabled (default)**: Shows delta table below radars
- **Disabled**: Hides delta table, shows only radars

---

## Text Labels

### Widget Header
```
Researched vs Validated Analysis                      ⚙
```

### Configuration Title
```
Configure Researched vs Validated Comparison
```

### Radar Labels
```
📊 Researched Scores     ✓ Validated Scores
```

### Delta Table Header
```
Delta Analysis (Validated - Researched)
```

### Table Columns
```
Metric | Researched | Validated | Delta | % Δ
```

### Category Label
```
[All Vendors] (n=300)
```
or
```
REGION: Global (n=45)
STARTUP: Startup (n=28)
AI_FIRST: AI-First (n=120)
IR_FOCUS_TYPE: Core Competency (n=180)
```

---

## Responsive Behavior

### Desktop (>1200px)
```
Side-by-side layout (2 columns)
- Left 50%: Researched radar
- Right 50%: Validated radar
- Full width: Delta table
```

### Tablet (768px - 1200px)
```
Stacked layout (1 column)
- Full width: Researched radar
- Full width: Validated radar
- Full width: Delta table
```

### Mobile (<768px)
```
Single column, condensed
- Radars may overlap slightly
- Delta table scrollable horizontally
- Configuration modal full-screen
```

---

## Empty States

### No Matching Vendors
```
┌──────────────────────────────────────────────┐
│ No vendors match the selected category.      │
│ Click the gear (⚙) to configure.             │
└──────────────────────────────────────────────┘
```

### Loading State
(Typically instant, but if delayed)
```
┌──────────────────────────────────────────────┐
│ Generating comparison...                      │
└──────────────────────────────────────────────┘
```

---

## Keyboard Navigation

### Tab Order
1. Configuration button (⚙)
2. Category Type dropdown (modal)
3. Category Value dropdown (modal)
4. Axes dropdown (modal)
5. Delta checkbox (modal)
6. Save button (modal)
7. Cancel button (modal)

### Keyboard Shortcuts
- **Enter**: Open/close modal, trigger Save
- **Escape**: Close modal without saving
- **Tab**: Move between form elements
- **Space**: Toggle checkbox, activate dropdown

---

## Accessibility Features

✓ ARIA labels on buttons ("Configure Comparison")  
✓ SVG charts with aria-label descriptions  
✓ Semantic HTML in delta table  
✓ Keyboard navigation support  
✓ High contrast colors (WCAG AA compatible)  
✓ Focus indicators on interactive elements  
✓ Semantic heading hierarchy  

---

## Integration with Other Widgets

### Works With
- **Filters**: Respects active filters on Analysis page
- **Score Mode**: Shows both modes (researched + validated) regardless
- **Dark Mode**: Colors adapt to light/dark theme
- **Widget Customization**: Can be hidden/shown

### Doesn't Duplicate
- **Comparison Radar**: This widget is different (2 modes vs 5 vendors)
- **Pillar Radar**: This widget is different (dual comparison vs single view)
- **Individual charts**: This provides category-level analysis

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│  RESEARCHED VS VALIDATED COMPARISON WIDGET      │
├─────────────────────────────────────────────────┤
│                                                 │
│  Location: Analysis tab → Main grid             │
│  Size: 3 columns × 2 rows                       │
│  Default: Visible, configured for "All Vendors" │
│                                                 │
│  How to Use:                                    │
│  1. Click gear icon (⚙)                         │
│  2. Select category type (Region, etc.)         │
│  3. Select category value (Global, etc.)        │
│  4. Choose axes (Pillars, Sub-pillars, Both)    │
│  5. Toggle delta metrics (on/off)               │
│  6. Click Save                                  │
│                                                 │
│  What You See:                                  │
│  • Left radar: Researched (blue)                │
│  • Right radar: Validated (green)               │
│  • Table: Score differences & percentages       │
│                                                 │
│  Colors Mean:                                   │
│  🟢 Green = Validation showed improvements      │
│  🔴 Orange = Validation showed regression       │
│  ⚪ Gray = Little change                        │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

That's where your new widget lives and how it looks! Enjoy using it! 🎉
