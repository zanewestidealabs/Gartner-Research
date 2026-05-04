# Feature Showcase & Usage Guide

## 🎯 All Features at a Glance

### 1. 🔍 Advanced Search & Filtering

#### Free-Text Search
- **How**: Type in "Search all fields..." box at the top
- **What it does**: Searches across vendor name, region, specialization, and capability analysis
- **Examples**:
  - Search `"cloud"` → finds all cloud-focused vendors
  - Search `"forensic"` → finds investigation specialists
  - Search `"Europe"` → finds European vendors

#### Click-to-Filter on Values
- **How**: Click on any value in the vendor table
- **What happens**: Automatically adds that value as a filter
- **Examples**:
  - Click vendor name `"Deloitte"` → shows only Deloitte
  - Click region `"Europe"` → shows only European vendors
  - Click focus type `"Core Competency"` → filters by focus type

#### Field-Based Filter Groups
- **How**: Expand filter group and click on tag values
- **Available filters**:
  - Vendor (company name)
  - Region (geographic location)
  - Specialization (primary focus)
  - IR Focus Type (Core vs. Assistance)
  - Is Startup (true/false)
  - Is AI-First (true/false)
- **Logic**: Multiple selections = AND (all must match)

#### Reset Filters
- **Button**: "Reset All" at top of filter panel
- **Effect**: Clears all active filters instantly
- **Keyboard**: No shortcut, use button only

---

### 2. 📖 Field Descriptions & Documentation

#### Info Icon on Column Headers
- **Location**: Next to each column title in table
- **Icon**: ℹ️
- **Action**: Click to show field information modal

#### Field Information Modal
Shows for each field:
- **Full Name** (e.g., "Planning (PLA)" instead of just "PLA")
- **Description** (what the field means)
- **Sample Values** (examples from the data)
- **Filter by Value** (click any value to add filter)

#### Example Fields:
- **PLA** → "Planning (PLA)" - Organizational Readiness and Breach Preparation
- **INV** → "Investigation (INV)" - Evidence Identification, Collection, and Analytical Reconstruction
- **REM** → "Remediation (REM)" - Threat Containment and Business Restoration
- **PMG** → "Program Management (PMG)" - Incident Lifecycle Oversight and Communication
- **LAW** → "Legal (LAW)" - Legal Admissibility and Judicial Support

#### Legend View
- **Navigation**: Click "Legend" in left navigation rail
- **Contains**:
  - Scoring legend (1-5 scale with explanations)
  - All field descriptions
  - Capability definitions
  - Organized grid layout

---

### 3. 🌙 Dark Mode

#### Toggle Dark Mode
- **Button**: Moon icon (🌙) in bottom-left navigation rail
- **Action**: Click to toggle between light and dark themes
- **Persistence**: Saved to browser localStorage (remembers preference)
- **Applies to**: All UI elements - tables, modals, filters, text

#### Dark Mode Colors
- **Text**: White on dark background
- **Backgrounds**: Dark gray (#1e1e1e, #2d2d2d)
- **Accent colors**: Blue (#0078d4), Green (#107c10) - unchanged
- **Borders**: Light gray on dark background
- **Pillar scores**: Same color scheme as light mode

#### Automatic Theme
- Detects browser preference (system dark mode)
- Applies automatically on first visit
- Can override with toggle button
- Smooth transition animation (0.3s)

---

### 4. 🎨 Professional User Interface

#### Left Navigation Rail
- **Width**: 60px fixed sidebar
- **Items**:
  - Logo (DFIR gradient)
  - Dashboard (📊)
  - Vendors (🏢)
  - Analysis (📈)
  - Legend (📖)
  - Dark Mode Toggle (🌙)
- **Interaction**: Click to switch views
- **Active State**: Blue highlight shows current view

#### Main Content Area
- **Header**: Title and description
- **Content**: Changes based on selected view
- **Filters**: Always visible in Vendors view
- **Table**: Responsive vendor data display

#### Vendor Table
- **Columns**:
  - Vendor Name (clickable)
  - Region (clickable for filtering)
  - Specialization
  - IR Focus Type (clickable)
  - PLA score (color-coded circle)
  - INV score (color-coded circle)
  - REM score (color-coded circle)
  - PMG score (color-coded circle)
  - LAW score (color-coded circle)
  - AI-First (badge)
  - Startup (badge)
- **Sticky Header**: Scrolls with table data
- **Hover Effects**: Rows highlight on hover
- **Clickable Cells**: Color-coded blue for interactive cells

#### Color-Coded Scores
- **Level 1** (Red #d13438): Limited/Manual
- **Level 2** (Orange #ff8c00): Insufficient Evidence
- **Level 3** (Yellow #ffb900): AI-Augmented
- **Level 4** (Green #107c10): Advanced AI
- **Level 5** (Blue #005a9e): Fully Agentic

---

### 5. 📊 Dashboard Analytics

#### Statistics Cards
Shows:
- **Total Vendors**: Count of all companies in database
- **AI-First Companies**: Vendors with AI-first approach
- **Startups**: Newer companies (vs. established)
- **Global Vendors**: Companies operating globally

#### Regional Distribution Chart
- **Type**: Horizontal bar chart
- **Data**: Vendor count by region
- **Top 8 regions** shown
- **Color**: Green-to-blue gradient
- **Interactive**: Shows exact count on hover

#### Pillar Scores Chart
- **Type**: 5-cell grid display
- **Shows**: Average capability score for each pillar
- **Pillars**: PLA, INV, REM, PMG, LAW
- **Scale**: 1.0 to 5.0
- **Color**: Blue text on colored background

---

### 6. 🏢 Vendor Details Modal

#### Trigger
- Click on any vendor name in the table

#### Content Displayed
- **Vendor Name**: Large heading
- **Capability Analysis**: Full description with company details
- **Key Information**:
  - Region
  - Specialization
  - IR Focus Type
  - AI-First status
  - Startup status
- **Pillar Scores**: All 5 pillars with visual scores
- **Granular Mapping**: Sub-capability ratings grid

#### Interaction
- Click vendor name again to close
- Click outside modal to close
- Click X button to close
- Smooth slide-up animation on open

---

## 🎓 Usage Scenarios

### Scenario 1: Find Best Investigation Specialists
1. Click "Legend" to see field definitions
2. Find vendors with INV score of 5
3. Click filter group "Specialization"
4. Click "Forensics" or "Investigation"
5. Review vendors in filtered list

### Scenario 2: Identify AI-First Startups
1. Expand "Is AI-First" filter group
2. Click "True"
3. Expand "Is Startup" filter group
4. Click "True"
5. View filtered results (e.g., Binalyze, Mitiga, Dropzone AI)

### Scenario 3: Compare Global Leaders
1. Filter by Region = "Global"
2. Filter by IR Focus Type = "Core Competency"
3. Sort by average pillar scores (highest first)
4. Click vendor names to compare details
5. Check specialization and capability analysis

### Scenario 4: Search for Cloud-Native Solutions
1. Type "cloud" in search box
2. Results filter automatically
3. Or search "container" for container forensics
4. Or search "Kubernetes" for K8s specialists

### Scenario 5: Build a Scorecard
1. Visit Legend view
2. Understand each pillar
3. Click vendor names to compare scores
4. Use notes/screenshots for analysis
5. Compare vendors side-by-side

---

## 💡 Pro Tips

### Tip 1: Combine Multiple Filters
- Click multiple filter values to narrow results
- All selected filters work together (AND logic)
- Example: Click "Global" region AND "Core Competency" type

### Tip 2: Use Search for Partial Matches
- Search box finds any text match
- Useful for finding related terms
- Example: Search "APT" finds APT-focused vendors

### Tip 3: Click Table Values Directly
- Faster than using filter groups
- Instantly filters to that value
- Works on vendor name, region, focus type

### Tip 4: Switch to Dark Mode for Evening
- Reduces eye strain
- Preference saved automatically
- All colors remain clearly visible

### Tip 5: Read Field Descriptions
- Every column has an info icon
- Explains what field means
- Shows sample values
- Learn the scoring system

### Tip 6: Use Dashboard for Insights
- Get quick overview of market
- See regional distribution
- Understand average capabilities
- Identify market gaps

### Tip 7: Export Data
- Select table rows and copy (Ctrl+C)
- Paste into Excel for analysis
- Create custom reports
- Further filtering in spreadsheet

### Tip 8: Bookmark Filtered Views
- Apply filters and bookmark URL
- URL contains filter parameters
- Share links with colleagues
- Return to saved views

---

## 🔧 Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Search focus | Ctrl+F |
| Select all text | Ctrl+A |
| Copy selection | Ctrl+C |
| Refresh page | F5 or Ctrl+R |
| Open DevTools | F12 |
| Full screen | F11 |
| Reload (hard) | Ctrl+Shift+R |

---

## ❓ Frequently Asked Questions

### Q: Can I sort the table?
A: Column headers are not sortable in this version. Use filtering to narrow results, then review in table order.

### Q: Can I export the data?
A: Yes! Copy the table rows (Ctrl+C) and paste into Excel, Google Sheets, etc.

### Q: Does filtering save automatically?
A: No, filters are session-based. Refresh the page and they clear. Bookmark the URL to save filter state.

### Q: Can I add new vendors?
A: Edit `vendor3-3.json` to add new vendors. Server must be restarted.

### Q: How do I change colors?
A: Edit `static/style.css` to customize colors. Look for `:root` CSS variables.

### Q: Is there a mobile app?
A: No, but the web app is responsive and works on mobile browsers.

### Q: Can multiple people access it simultaneously?
A: Yes! Share the URL. Each person gets their own session.

### Q: How do I deploy to production?
A: See deployment instructions in README.md

---

## 🎯 Feature Comparison

| Feature | Implemented | Notes |
|---------|-------------|-------|
| Free-text search | ✅ | Across all fields |
| Click-to-filter | ✅ | On table values |
| Field descriptions | ✅ | Info modal on headers |
| Dark mode | ✅ | Persistent preference |
| Left navigation | ✅ | 5 views + dark toggle |
| Vendor details | ✅ | Full modal view |
| Dashboard | ✅ | Stats + charts |
| Sorting | ❌ | Use filtering instead |
| Pagination | ❌ | All vendors shown |
| Export | ✅ | Copy to clipboard |
| Responsive design | ✅ | Mobile/tablet ready |
| Keyboard shortcuts | ✅ | Standard browser shortcuts |

---

## 🌟 Highlights

✨ **No external dependencies** - Pure HTML/CSS/JavaScript  
⚡ **Instant filtering** - Client-side processing  
🎨 **Professional design** - Modern UI with smooth animations  
🌙 **Dark mode support** - Beautiful in any lighting  
📱 **Fully responsive** - Works on any device  
🔍 **Powerful search** - Find vendors easily  
📊 **Analytics dashboard** - Understand the market  
💾 **Data persistence** - Dark mode preference saved  

---

**Everything you need to analyze DFIR vendors - all in one web app!**
