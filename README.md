# Gartner Research Platform

The local application is a Flask API/UI gateway backed by a secured,
loopback-only Apache CouchDB instance. It supports DFIR, MDR, Preemptive
Cybersecurity, CNAPP, AI TRiSM, Offensive Security, Product Market Readiness,
and Agentic SOC research workflows.

## Current quick start

```powershell
Set-Location C:\Gartner
.\.venv\Scripts\Activate.ps1
python -m flask --app app run --host 127.0.0.1 --port 5000
```

Open `http://127.0.0.1:5000`. The ignored `.env` must contain the local gateway
credentials and `DATA_BACKEND=couchdb`. See
[`docs/local-development.md`](docs/local-development.md) for bootstrap,
verification, backup, restore, and troubleshooting commands.

The JSON files retained in the repository are migration/rollback sources, not
the active persistence layer. Browser clients never connect directly to
CouchDB.

A comprehensive web application for analyzing and filtering Digital Forensics & Incident Response (DFIR) vendors based on capabilities, specializations, and market positioning.

## Features

### 🔍 **Smart Filtering & Search**
- **Free-text search** across all vendor fields
- **Click-to-filter** on any value in the list
- **Field-based filters** with expandable filter groups
- **Multi-select filtering** to narrow results by multiple criteria
- **Reset filters** with one click

### 📊 **Field Descriptions & Metadata**
- **Info icons** on every column header
- **Pop-up tooltips** showing full field names and descriptions
- **Scoring legend** explaining the 1-5 capability scale
- **Comprehensive field key** documenting all available data

### 🎨 **Modern User Interface**
- **Dark mode** with toggle button (preference saved)
- **Left navigation rail** with collapsible flyout
- **Responsive design** that works on all screen sizes
- **Dashboard view** with statistics and charts
- **Interactive vendor modals** showing detailed information

### 📈 **Analytics Dashboard**
- Total vendor count statistics
- AI-First vendor tracking
- Startup vs. established company split
- Global vendor distribution
- Average pillar score visualization

### 🏢 **Vendor Data Display**
- **5 DFIR Pillars**: Planning (PLA), Investigation (INV), Remediation (REM), Program Management (PMG), Legal (LAW)
- **Color-coded capability scores** (1-5 scale)
- **Granular mapping** showing sub-capability ratings
- **Capability analysis** with company descriptions
- **Region, specialization, and focus type** classification

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Quick Start

1. **Navigate to the application directory:**
   ```bash
   cd "g:\My Drive\Gartner"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server:**
   ```bash
   python app.py
   ```

   Or on Windows, double-click `run.bat`

4. **Open in browser:**
   - Navigate to `http://localhost:5000`
   - The app will automatically load all vendor data

## How to Use

### Basic Navigation
- **Dashboard Tab**: View overall statistics and charts
- **Vendors Tab**: Browse and filter vendor listings
- **Legend Tab**: See scoring explanations and field definitions
- **Dark Mode Toggle**: Click the moon icon to toggle dark/light mode

### Filtering Vendors

#### Method 1: Field-Based Filters
1. Click on a filter group title to expand it
2. Click on any value tag to add it to the active filters
3. Multiple selections are combined (AND logic)
4. Click "Reset All" to clear all filters

#### Method 2: Free-Text Search
1. Type in the "Search all fields..." box
2. Results update in real-time as you type
3. Searches across vendor names, regions, specializations, and analyses

#### Method 3: Click-to-Filter
1. Click on any clickable value in the table (vendor name, region, focus type)
2. The table immediately filters to show only matching results
3. Combine multiple clicks to narrow results further

### Understanding the Data

#### Field Descriptions
- Click the **ℹ️ icon** on any column header
- A modal will show:
  - Full field name (not abbreviations)
  - Detailed description of what the field means
  - Sample values for that field

#### Pillar Scores (1-5 Scale)
- **1** = Manual (human-led, no automation)
- **2** = Insufficient Evidence (service provided but AI not verified)
- **3** = AI-Augmented (basic generative AI assistants)
- **4** = Advanced AI (specialized models with human validation)
- **5** = Fully Agentic (autonomous systems)

Color coding:
- 🔴 Red (1-2): Limited capability
- 🟠 Orange (2-3): Basic capability
- 🟡 Yellow (3): Moderate capability
- 🟢 Green (4): Strong capability
- 🔵 Blue (5): Expert capability

#### Vendor Categories
- **Core Competency**: IR is the primary work product
- **Assistance Component**: IR provided as feature/support
- **AI-First**: Company primarily uses AI-driven approaches
- **Startup**: Newer companies (vs. established firms)

### Viewing Vendor Details
1. Click on any **vendor name** in the table
2. A detailed modal opens showing:
   - Full capability analysis
   - All pillar scores visualized
   - Granular mapping (sub-capability ratings)
   - Company classification (region, specialization, etc.)

### Dashboard Analytics
- **Stat Cards**: Quick metrics on total vendors, AI-first count, startups, global coverage
- **Region Chart**: Distribution of vendors by geographic region
- **Pillar Chart**: Average capability scores across all pillars

## File Structure

```
g:\My Drive\Gartner\
├── app.py                 # Flask backend server
├── requirements.txt       # Python dependencies
├── run.bat               # Windows startup script
├── schema3-3.json        # DFIR capability taxonomy
├── vendor3-3.json        # Vendor data
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── style.css         # Styling and dark mode
    └── app.js            # Client-side JavaScript
```

## API Endpoints

### GET `/`
Main application page with all interactive features.

### GET `/api/vendors`
Get filtered vendors. Query parameters:
- `search`: Free-text search query
- `filter_<field>`: Filter by specific field value

Example: `/api/vendors?search=cloud&filter_region=Global`

### GET `/api/field-values/<field>`
Get all unique values for a specific field.

Example: `/api/field-values/region`

### GET `/api/metadata`
Get field metadata and scoring legend.

## Filtering Examples

### Example 1: Find AI-First Startups in North America
1. Filter by `is_ai_first` = True
2. Filter by `is_startup` = True
3. Filter by `region` = North America

### Example 2: Find Investigation Specialists
1. Search for: "investigation" OR "forensic"
2. Look for vendors with INV score of 5

### Example 3: Find Global Leaders
1. Filter by `region` = Global
2. Filter by `ir_focus_type` = Core Competency
3. Sort by average pillar scores

## Performance Notes

- The application loads all vendor data into memory (60+ vendors)
- Filtering happens client-side for instant results
- Supports up to 1000+ vendors without noticeable performance impact

## Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- IE 11: ❌ Not supported (use modern browser)

## Customization

### Adding New Vendors
Edit `vendor3-3.json` and add new vendor objects following the existing structure.

### Modifying Fields
Update the `FIELD_METADATA` dictionary in `app.py` to add descriptions for new fields.

### Styling
Edit `static/style.css` to customize colors, fonts, and layout.

## Troubleshooting

### Port Already in Use
If port 5000 is in use, edit `app.py` line 81:
```python
app.run(debug=True, port=5001)  # Use 5001 instead
```

### Dark Mode Not Persisting
Clear browser cache or check localStorage in developer tools.

### Filters Not Working
- Ensure JavaScript is enabled
- Check browser console (F12) for errors
- Try resetting filters with "Reset All" button

## Future Enhancements

- [ ] Export filtered results to CSV/Excel
- [ ] Advanced statistical analysis
- [ ] Vendor comparison tool
- [ ] Custom report generation
- [ ] Data caching for improved performance
- [ ] Advanced charting with drill-down capabilities

## License

This application is provided for research and analysis purposes.

## Support

For issues or feature requests, please refer to the documentation or check the browser console for error messages.
