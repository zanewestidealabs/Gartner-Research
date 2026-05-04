# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Server
```bash
python app.py
```

### Step 3: Open in Browser
Navigate to: **http://localhost:5000**

---

## 📋 What You Can Do

### 🔍 **Search & Filter Vendors**
- Type in the search box to find vendors by any field
- Click filter tags to narrow down results
- Click on column headers (ℹ️) for field descriptions

### 🌙 **Dark Mode**
- Click the moon icon (🌙) in the bottom left
- Your preference is saved automatically

### 📊 **View Dashboard**
- Click the dashboard icon to see statistics
- View distribution charts by region and capability

### 📖 **Understanding the Data**
- Click "Legend" to see scoring explanations
- Each pillar (PLA, INV, REM, PMG, LAW) is rated 1-5
- Color-coded scores: Red (low) → Blue (high)

### 🏢 **Vendor Details**
- Click any vendor name to see full details
- View all capability scores and granular mapping
- See company specialization and focus areas

---

## 🎯 Common Tasks

### Find Cloud-Focused Vendors
1. Search for "cloud" in the search box
2. Or filter by `specialization` containing "Cloud"

### Find AI-First Startups
1. Expand filter group "AI-First"
2. Click "True"
3. Expand filter group "Is Startup"  
4. Click "True"

### Find Global Leaders
1. Filter by `region` = "Global"
2. Filter by `ir_focus_type` = "Core Competency"
3. Look at vendors with highest pillar scores

### See Investigation Specialists
1. Sort table by INV column (highest scores first)
2. Or search for "Investigation" or "Forensic"

---

## 🆘 Troubleshooting

**Server won't start?**
- Make sure Python 3.7+ is installed
- Check if port 5000 is already in use
- Try: `python app.py --port 5001`

**Filters not working?**
- Try refreshing the page (Ctrl+F5)
- Check browser console (F12) for errors
- Click "Reset All" to clear filters

**Data not loading?**
- Ensure `vendor3-3.json` and `schema3-3.json` are in the app directory
- Check browser console for error messages

---

## 📚 For More Information

See **README.md** for:
- Detailed feature descriptions
- API endpoint documentation
- Customization instructions
- Field descriptions and scoring logic

---

## 💡 Pro Tips

1. **Multi-filter**: Click multiple filter values to combine criteria
2. **Quick filter**: Click any value in the table to instantly filter by that value
3. **Dark mode**: Saves preference for next visit
4. **Export data**: Copy table rows and paste into Excel
5. **Responsive**: Works on mobile, tablet, and desktop

---

**🎉 You're all set! Start exploring vendor data now!**
