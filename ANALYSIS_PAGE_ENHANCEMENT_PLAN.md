# Analysis Page Enhancement Plan: Researched vs Validated Comparison

## Current State Review

### Application Architecture
- **Framework**: Flask backend (Python) + Vanilla JavaScript frontend
- **Current Score Modes**: 3 modes available via dropdown:
  - `validated` - Uses `pillar_scores_validated` / `granular_mapping_validated`
  - `researched` - Uses `sub_pillar_scores_researched` 
  - `current` - Uses raw `pillar_scores` / `granular_mapping`
- **Active Score Mode**: Controlled by global `appState.scoreMode`

### Vendor Data Structure
Each vendor record contains multiple score sets:
```json
{
  "vendor": "CompanyName",
  "region": "Global",
  "is_startup": true,
  "is_ai_first": true,
  "ir_focus_type": "Core Competency",
  "specialization": "...",
  
  // Main scores (raw/current)
  "pillar_scores": {
    "PLA": 4.5, "INV": 5.0, "REM": 4.25, "PMG": 4.25, "LAW": 4.5
  },
  "granular_mapping": { /* sub-pillar scores */ },
  
  // Validated scores
  "pillar_scores_validated": { /* validated pillar scores */ },
  "granular_mapping_validated": { /* validated sub-pillar scores */ },
  
  // Researched scores
  "sub_pillar_scores_researched": {
    "PLA-01": 5.0, "PLA-02": 4.0, ... /* all 20 sub-pillars */
  },
  "sub_pillar_scores_validated": {
    "PLA-01": 5.0, "PLA-02": 4.0, ...
  }
}
```

### Current Comparison Radar Implementation

**Location**: [static/app.js](static/app.js#L3081-L3600) & [templates/index.html](templates/index.html#L443-L495)

**Features**:
- Compares up to 5 series (competitors) simultaneously
- Comparison types:
  - **Vendor**: Individual vendors side-by-side
  - **Region**: All vendors in a region vs others
  - **AI-First**: AI-First vs Traditional cohorts
  - **Startup**: Startup vs Established cohorts
  - **IR Focus Type**: By IR service type
  
- **Axes options**:
  - **Pillars**: 5 main pillars (PLA, INV, REM, PMG, LAW)
  - **Sub-pillars**: 20 detailed sub-capabilities
  - **Both**: All 25 dimensions

- **Current Limitation**: 
  - All 5 series use the same score mode (determined by global `appState.scoreMode`)
  - Cannot directly compare Researched vs Validated data for the same category
  - Users must switch score modes globally, losing the previous dataset

### Key Functions
- `renderComparisonRadar()` - Renders SVG radar chart
- `matchVendorsForSelection()` - Filters vendors based on selected category
- `computePillarAveragesForVendors()` - Calculates average pillar scores
- `computeSubPillarAveragesForVendors()` - Calculates average sub-pillar scores
- `getEffectivePillarScores()` - Selects correct score set based on mode
- `getEffectiveGranularMapping()` - Selects correct granular mapping based on mode

---

## Enhancement Requirement Analysis

### User Request
> "On the Analysis page in the comparison radar I want to be able to compare the results of a category such as all vendors average or just global vendors between the Researched data and scores and validated results and scores."

### Interpretation
The user wants to:
1. Compare **one category** (e.g., "Global Region", "All Vendors Average") 
2. Across **two data sets**:
   - Researched scores
   - Validated scores
3. **Within a single radar chart view**

**Example Use Case**:
- Select "Global Vendors" category
- See two overlay lines:
  - Blue line = Average scores from Researched data
  - Red line = Average scores from Validated data
- Visually identify discrepancies between research and validation phases

---

## Implementation Strategy

### Option 1: **Score Mode Series** (Recommended)
Add a new comparison type: **"Score Mode Comparison"**

**Changes Required**:

1. **Backend** (`app.py`):
   - No changes needed (all data already available)

2. **Frontend** (`app.js`):
   - Add new comparison type: `scoreMode`
   - Extend `getComparisonOptions()` to return score modes when type = 'scoreMode'
   - Modify `matchVendorsForSelection()` to handle scoreMode type
   - Create `computeAveragesForScoreMode()` to calculate averages across all vendors for a specific score mode
   - Update `renderComparisonRadar()` to support mixed score mode series

3. **HTML** (`index.html`):
   - Add "Score Mode Comparison" option to comparison-radar-type dropdown

**Workflow**:
1. User selects "Score Mode Comparison" type
2. Category selector appears (Region, Startup, etc.)
3. User selects a category (e.g., "Global")
4. System auto-populates 5 series with:
   - S1: Category average from Researched
   - S2: Category average from Validated
   - S3-S5: Available for additional comparisons

**Pros**:
- Clean, intuitive UI workflow
- Reuses existing radar infrastructure
- User can still add other series for multi-dimensional analysis
- Minimal code changes

**Cons**:
- Adds one more type option (5 → 6 comparison types)

---

### Option 2: **Per-Series Score Mode Toggle**
Allow each of the 5 series to independently specify their score mode

**Changes Required**:

1. **Data Structure** (`app.js`):
   ```javascript
   const comparisonRadarState = {
       type: 'vendor',
       selections: [
           { value: '', scoreMode: 'validated' },
           { value: '', scoreMode: 'researched' },
           // etc
       ],
       axes: 'pillars'
   };
   ```

2. **UI** (`index.html`):
   - Extend config modal to show score mode selector for each series
   - 5 vendor/category selectors + 5 score mode selectors (10 dropdowns)

3. **Calculation** (`app.js`):
   - Modify `computePillarAveragesForVendors()` to accept scoreMode parameter
   - Modify `computeSubPillarAveragesForVendors()` to accept scoreMode parameter
   - Update series rendering to use per-series score mode

**Pros**:
- Maximum flexibility
- Can compare any combination (e.g., "Global Researched" vs "US Validated" vs "Startup Researched")
- Most powerful option

**Cons**:
- More complex UI
- Larger state structure
- Risk of confusing user with too many options

---

### Option 3: **Dedicated Comparison View**
Create a new widget specifically for "Researched vs Validated" comparison

**Changes Required**:
- New section in Analysis page
- Dedicated UI for selecting category and score modes
- Parallel radar charts (side-by-side) showing Researched and Validated
- Difference metrics (delta analysis)

**Pros**:
- Focused user experience for this specific task
- Can add specialized features (delta overlay, statistics)

**Cons**:
- Duplicates radar rendering logic
- Takes up more screen real estate
- Adds complexity to Analysis page

---

## Recommended Approach: **Option 1 + Option 2 Hybrid**

### Phase 1: Quick Win (Option 1)
Implement "Score Mode Comparison" type with smart auto-population:
- When type = "Score Mode Comparison"
- Show category selector (Region, Startup, etc.)
- Auto-populate S1 with researched, S2 with validated
- User can manually edit if desired

### Phase 2: Advanced Feature (Option 2)
Add per-series score mode controls as an "Advanced" toggle in the config modal:
- Keep simple UI by default
- Power users can enable advanced mode
- Each series shows score mode dropdown

---

## Implementation Details for Option 1

### 1. HTML Changes
```html
<!-- In comparison-radar-type select, add: -->
<option value="scoreMode">Score Mode Comparison</option>

<!-- New element in modal (conditionally shown): -->
<div id="comparison-radar-category" style="display:none;">
    <label>
        Category Type
        <select id="comparison-radar-category-type">
            <option value="">Select...</option>
            <option value="region">Region</option>
            <option value="startup">Startup/Established</option>
            <option value="ai_first">AI-First/Traditional</option>
            <option value="ir_focus_type">IR Focus Type</option>
        </select>
    </label>
    <label>
        Category Value
        <select id="comparison-radar-category-value">
            <option value="">Select...</option>
            <!-- Populated dynamically -->
        </select>
    </label>
</div>
```

### 2. JavaScript Changes
```javascript
// Extend comparisonRadarState
const comparisonRadarState = {
    type: 'vendor',
    selections: ['', '', '', '', ''],
    axes: 'pillars',
    // New fields for score mode comparison
    scoreModeCategoryType: '',  // region | startup | ai_first | ir_focus_type
    scoreModeCategoryValue: ''  // e.g., "Global" | "Startup"
};

// Extend getComparisonOptions()
function getComparisonOptions(typeOverride = null) {
    // ... existing code ...
    
    if (type === 'scoreMode') {
        return ['Researched', 'Validated', 'Current'];
    }
    
    return [];
}

// New function
function populateScoreModeComparison() {
    const categoryTypeSelect = document.getElementById('comparison-radar-category-type');
    const categoryValueSelect = document.getElementById('comparison-radar-category-value');
    
    if (!categoryTypeSelect) return;
    
    // Get unique values for selected category type
    const vendors = appState.filteredVendors || appState.vendors || [];
    const categoryType = categoryTypeSelect.value;
    const values = getUniqueValuesForField(vendors, categoryType);
    
    // Populate category value dropdown
    categoryValueSelect.innerHTML = '<option value="">Select...</option>';
    values.forEach(v => {
        const opt = document.createElement('option');
        opt.value = v;
        opt.textContent = v;
        categoryValueSelect.appendChild(opt);
    });
}

// Modify matchVendorsForSelection() to handle scoreMode
function matchVendorsForSelection(selectionValue, vendorsForAverages) {
    // ... existing code ...
    
    if (comparisonRadarState.type === 'scoreMode') {
        const label = selectionValue;
        const categoryType = comparisonRadarState.scoreModeCategoryType;
        const categoryValue = comparisonRadarState.scoreModeCategoryValue;
        
        // Filter vendors by category, return with label showing score mode
        const filtered = filterVendorsByCategory(vendorsForAverages, categoryType, categoryValue);
        return { label: `${label} (${categoryValue})`, vendors: filtered };
    }
    
    // ... existing code ...
}

// New calculation function
function filterVendorsByCategory(vendors, categoryType, categoryValue) {
    if (!categoryType || !categoryValue) return [];
    
    const val = categoryValue.toLowerCase();
    return (vendors || []).filter(v => {
        if (categoryType === 'region') {
            return String(v.region || '').toLowerCase().includes(val);
        }
        if (categoryType === 'startup') {
            const want = val === 'startup';
            return !!v.is_startup === want;
        }
        if (categoryType === 'ai_first') {
            const want = val === 'ai-first';
            return !!v.is_ai_first === want;
        }
        if (categoryType === 'ir_focus_type') {
            return String(v.ir_focus_type || '') === categoryValue;
        }
        return false;
    });
}
```

### 3. Event Handler Changes
```javascript
// When type changes to 'scoreMode'
typeSelect.addEventListener('change', () => {
    draftState.type = typeSelect.value;
    
    if (typeSelect.value === 'scoreMode') {
        // Show category selectors
        document.getElementById('comparison-radar-category').style.display = 'block';
        // Auto-populate score mode series
        draftState.selections = ['Researched', 'Validated', '', '', ''];
        populateScoreModeComparison();
    } else {
        // Hide category selectors
        document.getElementById('comparison-radar-category').style.display = 'none';
        draftState.selections = ['', '', '', '', ''];
    }
    
    populateComparisonRadarDropdowns();
});

// When category type changes
document.getElementById('comparison-radar-category-type').addEventListener('change', () => {
    draftState.scoreModeCategoryType = this.value;
    populateScoreModeComparison();
});

// When category value changes
document.getElementById('comparison-radar-category-value').addEventListener('change', () => {
    draftState.scoreModeCategoryValue = this.value;
});
```

---

## Testing Scenarios

### Test Case 1: Basic Score Mode Comparison
1. Navigate to Analysis tab
2. Click gear icon on Comparison Radar
3. Select "Score Mode Comparison" type
4. Select "Region" category and "Global" value
5. Verify S1 shows "Researched (Global)" and S2 shows "Validated (Global)"
6. Save and verify radar shows both lines overlaid

### Test Case 2: Different Categories
Repeat Test Case 1 with:
- Startup vs Established
- AI-First vs Traditional
- Different regions

### Test Case 3: Data Validation
Compare rendered values against vendor JSON data:
- Calculate average pillar scores for researched mode
- Calculate average pillar scores for validated mode
- Verify radar points match calculations

### Test Case 4: Sub-Pillar Comparison
1. Set axes to "Sub-pillars"
2. Perform score mode comparison
3. Verify 20 sub-pillar dimensions render correctly

---

## Benefits of This Enhancement

1. **Insight into Research Quality**: Spot discrepancies between initial research and validated data
2. **Market Trends**: Identify if certain categories score consistently higher/lower in validation
3. **Risk Assessment**: Categories with large deltas might indicate research gaps
4. **Single-View Analysis**: No need to toggle score modes and lose previous visualization
5. **Quick Baseline**: Built-in "Researched vs Validated" scenario without manual selection

---

## Files to Modify

1. **[templates/index.html](templates/index.html#L460)** (3-5 lines)
   - Add "Score Mode Comparison" option to dropdown

2. **[static/app.js](static/app.js#L3081-L3600)** (100-150 lines)
   - Add comparisonRadarState fields
   - Extend getComparisonOptions()
   - Add UI toggle functions
   - Modify matchVendorsForSelection()
   - Add helper functions

---

## Risk Assessment

- **Low Risk**: No backend changes required
- **Low Risk**: Existing functionality untouched
- **Medium Complexity**: ~200 lines of new code
- **No Data Structure Changes**: Uses existing vendor data
- **Backward Compatible**: Old configurations still work

---

## Next Steps

1. Review this plan with stakeholders
2. Confirm Option 1 is desired approach
3. Begin Phase 1 implementation
4. Test with provided vendor datasets
5. Consider Phase 2 for advanced per-series score modes
