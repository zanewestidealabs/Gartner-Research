# 🌐 PRODUCTION ACCESS GUIDE

**Application**: DFIR Vendor Analysis Platform with Query Builder  
**Status**: ✅ LIVE  
**URL**: http://192.168.15.51:5000  
**Last Updated**: January 30, 2026

---

## 📍 ACCESSING THE APPLICATION

### Web Browser
Simply navigate to: **http://192.168.15.51:5000**

The application will load with:
- Dashboard view (default)
- Vendor list with search and filtering
- Analysis page with new Query Builder
- Legend showing DFIR pillar definitions

---

## 🔍 USING THE QUERY BUILDER

### Location
**Analysis Tab** → Top of page under "Analytics & Reporting"

### Quick Start
1. Click "Analysis" in the left sidebar
2. Click any field button on the left (e.g., "Region")
3. A filter row appears with dropdowns
4. Select operator and enter value
5. Results update instantly!

### Example Queries

#### Find EMEA vendors
1. Click "Region" button
2. Operator: "equals"
3. Value: "EMEA"
4. Result: Shows only EMEA vendors and their distribution

#### Find AI-First vendors in North America
1. Click "Region" button → "equals" → "North America"
2. Click "AI-First" button → "equals" → "Yes"
3. Result: Filtered to North America AI vendors

#### Find vendors containing "Mandiant" in name
1. Click "Vendor Name" button
2. Operator: "contains"
3. Value: "Mandiant"
4. Result: All vendors with "Mandiant" in their name

### Filter Operators
- **equals**: Exact match
- **does not equal**: Opposite of equals
- **contains**: Partial text match (case-insensitive)
- **does not contain**: Excludes matches

### Removing Filters
Click the ✕ button on any filter row to delete it instantly.

---

## 📊 WHAT YOU'LL SEE

### Charts (Auto-Update with Filters)
- **Vendor Distribution by Region** - How vendors spread globally
- **Average Pillar Capabilities** - DFIR pillar strength analysis
- **Specialization Breakdown** - Primary areas of focus
- **IR Focus Type** - Core competency vs assistance
- **AI-First vs Traditional** - AI adoption rate
- **Startup vs Established** - Company maturity

### Statistics
- **Vendors Analyzed**: Count of filtered results
- **Average Pillar Score**: Mean capability rating
- **AI-First %**: Percentage of AI-native vendors
- **Startup %**: Percentage of startup companies

---

## 🔗 QUICK LINKS

| Feature | Path |
|---------|------|
| Home | `/` |
| Dashboard | `/#dashboard` |
| Vendor List | `/#vendors` |
| Analysis (Query Builder) | `/#analysis` |
| Legend | `/#legend` |
| API: All Vendors | `/api/vendors` |
| API: Vendor Metadata | `/api/metadata` |

---

## 🐛 TROUBLESHOOTING

### Page Won't Load
1. Check URL is correct: `http://192.168.15.51:5000`
2. Try refreshing the page (Ctrl+F5)
3. Clear browser cache if needed

### Charts Not Updating
1. Try removing and re-adding filters
2. Refresh the page
3. Check browser console for errors (F12)

### Filters Not Working
1. Ensure you're on the Analysis tab
2. Try adding a filter for a different field
3. Refresh and try again

### Slow Performance
1. This is expected with 86 vendors loaded
2. Try narrowing filters to get faster results
3. Close other browser tabs

---

## 💡 TIPS & TRICKS

### Multi-Filter Strategy
- Filters combine with AND logic
- Start broad, then narrow results
- Each filter reduces the result set

### Analytics Use Cases
1. **Market Research**: Find vendors by region/specialization
2. **Competitive Analysis**: Compare capabilities by sector
3. **Startup Tracking**: Filter for emerging companies
4. **AI Adoption**: See which vendors are AI-first
5. **Geographic Coverage**: Understand regional distribution

### Export Data
- Copy data from filters and paste into Excel
- Use browser's Print function (Ctrl+P) for reports
- Charts can be saved as images (right-click → Save)

---

## 📞 SUPPORT

### API Endpoints

#### Get All Vendors
```
GET http://192.168.15.51:5000/api/vendors
Returns: JSON array of all vendors
```

#### Get Metadata
```
GET http://192.168.15.51:5000/api/metadata
Returns: Field descriptions and score legend
```

---

## 🚀 NEW FEATURES (Jan 30, 2026)

### Query Builder
- Intuitive field selection via buttons
- Dynamic filter rows that update in real-time
- Support for text, select, and boolean fields
- Drag-free interface with instant results

### Real-Time Analytics
- All charts update as you filter
- Statistics recalculate automatically
- No page reload needed
- Smooth performance with 86 vendors

### Responsive Design
- Works on desktop, tablet, and mobile
- Dark mode support
- Accessible color scheme
- Touch-friendly buttons

---

## 📋 SYSTEM INFO

**Server**: 192.168.15.51  
**OS**: Ubuntu Linux  
**Python**: 3.10.12  
**Framework**: Flask 3.0.0  
**Port**: 5000  
**Service**: gartner.service (systemd)  
**Status**: Running (auto-restart enabled)

---

**Deployment Date**: January 30, 2026  
**Last Status Check**: 05:24 UTC  
**API Status**: ✅ Operational
