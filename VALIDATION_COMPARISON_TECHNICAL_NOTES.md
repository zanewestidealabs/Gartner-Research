# Technical Integration Notes: Validation Comparison Widget

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    HTML Template                        │
│  - Widget Container (data-widget="validation-...")     │
│  - Configuration Modal                                  │
│  - Modal Form (category selectors, axes, delta)        │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              JavaScript State Management               │
│  - validationComparisonState (category, axes, etc.)   │
│  - localStorage persistence                            │
│  - Event handlers for config modal                      │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│            Data Processing Functions                    │
│  - filterVendorsByValidationCategory()                 │
│  - computeAveragesForScoreMode()                       │
│  - buildPillarScoresFromSubPillars()                   │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Rendering Functions                        │
│  - renderValidationRadar() [SVG]                       │
│  - renderValidationComparison() [Main]                 │
│  - Delta metrics table HTML                             │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    CSS Styling                          │
│  - validation-comparison-* classes                      │
│  - Responsive grid layout                               │
│  - Color-coded delta indicators                         │
└─────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
Page Load
  │
  ├─ initializeValidationComparisonWidget()
  │   ├─ Load persisted state from localStorage
  │   ├─ Bind config button click handler
  │   ├─ Bind modal event handlers
  │   └─ Populate category dropdowns
  │
  └─ renderValidationComparison()
      ├─ Get filtered vendors from appState
      ├─ filterVendorsByValidationCategory()
      │   └─ Apply category type/value filters
      ├─ computeAveragesForScoreMode('researched')
      │   ├─ Sum pillar scores
      │   ├─ Sum sub-pillar scores
      │   └─ Calculate averages
      ├─ computeAveragesForScoreMode('validated')
      │   ├─ Sum pillar scores
      │   ├─ Sum sub-pillar scores
      │   └─ Calculate averages
      ├─ Generate HTML structure
      ├─ Render researched radar (SVG)
      │   └─ renderValidationRadar(researched-container, ...)
      ├─ Render validated radar (SVG)
      │   └─ renderValidationRadar(validated-container, ...)
      └─ Render delta table (if enabled)
          ├─ Loop through axes
          ├─ Calculate delta (validated - researched)
          ├─ Apply color coding
          └─ Insert table rows

Config Modal -> Save
  │
  ├─ Update validationComparisonState
  ├─ saveValidationComparisonState() [localStorage]
  ├─ renderValidationComparison() [immediate update]
  └─ Modal closes
```

---

## State Object Structure

```javascript
// Widget-specific state
validationComparisonState = {
  categoryType: 'all',           // Category dimension
  categoryValue: '',             // Specific category selection
  axes: 'pillars',               // Comparison dimensionality
  showDelta: true                // Delta metrics visibility
}

// Persisted to localStorage key: 'validationComparisonState'
// Survives page refresh and browser restarts
```

---

## Key Functions Reference

### `loadValidationComparisonState()`
**Purpose**: Restore user preferences from localStorage  
**Called**: Once during widget initialization  
**Parameters**: None  
**Returns**: void  
**Side Effects**: Modifies `validationComparisonState` object

### `saveValidationComparisonState()`
**Purpose**: Persist current state to localStorage  
**Called**: When user clicks Save in config modal  
**Parameters**: None  
**Returns**: void  
**Storage**: `localStorage['validationComparisonState']`

### `getValidationComparisonCategoryValues(categoryType)`
**Purpose**: Get available options for selected category type  
**Parameters**:
- `categoryType` (string): 'all' | 'region' | 'startup' | 'ai_first' | 'ir_focus_type'

**Returns**: Array of unique values from vendor data  
**Example**: 
```javascript
getValidationComparisonCategoryValues('region')
// Returns: ['Global', 'North America', 'Europe', 'APAC', ...]
```

### `filterVendorsByValidationCategory(vendors, categoryType, categoryValue)`
**Purpose**: Filter vendor array based on category criteria  
**Parameters**:
- `vendors` (array): Full vendor dataset
- `categoryType` (string): Category dimension to filter on
- `categoryValue` (string): Specific value to match

**Returns**: Filtered vendor array  
**Logic**:
- For 'region': substring match (case-insensitive)
- For 'startup': boolean match (is_startup property)
- For 'ai_first': boolean match (is_ai_first property)
- For 'ir_focus_type': exact match

### `computeAveragesForScoreMode(vendors, scoreMode)`
**Purpose**: Calculate average scores for vendor set in given mode  
**Parameters**:
- `vendors` (array): Vendor dataset to analyze
- `scoreMode` (string): 'researched' | 'validated'

**Returns**:
```javascript
{
  pillars: {
    PLA: 3.75,
    INV: 4.25,
    REM: 3.95,
    PMG: 3.60,
    LAW: 3.40
  },
  subPillars: {
    'PLA-01': 4.0,
    'PLA-02': 3.5,
    // ... all 20 sub-pillars
  },
  vendorCount: 45
}
```

**Data Sources by Mode**:
- `researched`:
  - Primary: `vendor.pillar_scores_researched`
  - Fallback: Derived from `sub_pillar_scores_researched`
  
- `validated`:
  - Primary: `vendor.pillar_scores_validated`
  - Fallback: `vendor.pillar_scores` (current/raw)

### `buildPillarScoresFromSubPillars(subPillarScores)`
**Purpose**: Derive pillar averages from sub-pillar data  
**Used when**: `pillar_scores_researched` unavailable  
**Parameters**:
- `subPillarScores` (object): All 20 sub-pillar scores

**Returns**:
```javascript
{
  PLA: 3.85,  // Average of PLA-01, PLA-02, PLA-03, PLA-04
  INV: 4.20,  // Average of INV-01 through INV-04
  // ... etc for REM, PMG, LAW
}
```

### `renderValidationRadar(container, data, title)`
**Purpose**: Generate SVG radar chart for single dataset  
**Parameters**:
- `container` (HTMLElement): Target container for SVG
- `data` (object): Output from `computeAveragesForScoreMode()`
- `title` (string): Chart label (e.g., "Researched")

**Returns**: void (SVG injected into container.innerHTML)  
**Output**: SVG with:
- Concentric rings (scale 1-5)
- Radial axes (labeled)
- Data polygon (filled)
- Vertex dots (data points)

**Colors**:
- Researched: Blue (#0078d4)
- Validated: Green (#107c10)

### `renderValidationComparison(vendorsForAverages)`
**Purpose**: Main widget rendering function  
**Called**: On page load, config save, filter change  
**Parameters**:
- `vendorsForAverages` (array, optional): Pre-filtered vendors
  - If null: Uses `appState.filteredVendors` or `appState.vendors`

**Returns**: void (HTML injected into widget container)  
**Process**:
1. Applies category filter
2. Calculates both score modes
3. Generates layout HTML
4. Renders two radar charts
5. Optionally adds delta table

---

## CSS Classes Reference

### Layout Classes
- `.validation-comparison-content` - Main widget container
- `.validation-comparison-radar-container` - Two-column grid
- `.validation-comparison-radar-section` - Individual side panel
- `.validation-comparison-radar-title` - Side label
- `.validation-comparison-radar-chart` - SVG container

### Form Classes
- `.validation-comparison-form` - Config modal grid layout
- `.validation-comparison-form-actions` - Button container
- `.validation-comparison-form select` - Dropdown styling

### Delta Table Classes
- `.validation-comparison-delta-metrics` - Table container
- `.validation-comparison-delta-title` - Table header
- `.validation-comparison-delta-table` - Table element
- `.validation-comparison-delta-positive` - Green text (higher validated)
- `.validation-comparison-delta-negative` - Orange text (lower validated)
- `.validation-comparison-delta-neutral` - Gray text (minimal delta)

---

## Integration Points

### With appState
- Reads: `appState.vendors`, `appState.filteredVendors`, `appState.subPillars`
- Does NOT modify appState
- Uses global vendor data

### With updateAnalytics()
- `renderValidationComparison()` called at end of `updateAnalytics()`
- Means widget updates whenever:
  - Filters are applied/removed
  - Score mode changes
  - Vendor file switches
  - Page refreshes

### With Widget Customization
- Widget appears in customize modal with checkbox
- Can be hidden via "Customize Widgets" button
- Follows same grid layout system as other widgets

---

## Event Handlers

### Configuration Modal
```javascript
// Config button click
document.getElementById('validation-comparison-config-btn')
  .addEventListener('click', openModal)

// Category type change
document.getElementById('validation-comparison-category-type')
  .addEventListener('change', updateCategoryValues)

// Save button
document.getElementById('validation-comparison-config-save')
  .addEventListener('click', applyChanges)
```

### Auto-updates
- Widget auto-renders when `updateAnalytics()` is called
- No need for manual refresh
- Respects active filters

---

## Performance Considerations

### Optimization Strategies
1. **SVG Rendering**: Uses native SVG (not Canvas)
   - Scales smoothly
   - No redraw on window resize
   
2. **Lazy Calculation**: Only computes when needed
   - Not during page load if widget hidden
   - Skips calculation if container has `.hidden` class

3. **Efficient Filtering**: Single-pass vendor filtering
   - O(n) complexity where n = vendor count
   
4. **Memoization**: Persists state in localStorage
   - Avoids recalculation on page refresh
   
### Scaling Limits
- **Vendor Count**: Tested with 300+ vendors, no performance issues
- **Sub-pillar Count**: 20 sub-pillars work well (25 with both mode slightly slower)
- **Category Values**: Can handle 50+ regions, specializations, etc.

---

## Browser Compatibility

### Required Features
- localStorage (for state persistence)
- SVG support (for radar charts)
- ES6 syntax (arrow functions, const/let)
- CSS Grid (for layout)
- CSS Custom Properties (for theming)

### Tested Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Graceful Degradation
- SVG: Falls back to error message if unavailable
- localStorage: Silently continues without persistence
- CSS Grid: Responsive fallback to single column

---

## Debugging Tips

### Check Widget State
```javascript
// In browser console
console.log(validationComparisonState)
console.log(localStorage.getItem('validationComparisonState'))
```

### Force Refresh
```javascript
// Recompute widget with current state
renderValidationComparison()

// Reload from storage
loadValidationComparisonState()
renderValidationComparison()
```

### Check Vendor Data
```javascript
// Verify vendors have researched/validated scores
appState.vendors[0].pillar_scores_researched
appState.vendors[0].pillar_scores_validated
appState.vendors[0].sub_pillar_scores_researched
```

### Monitor Category Filtering
```javascript
// Check which vendors match category
const vendors = appState.vendors
const filtered = filterVendorsByValidationCategory(
  vendors, 'region', 'Global'
)
console.log(`Matched: ${filtered.length} vendors`)
```

---

## Known Limitations

1. **No Individual Vendor Comparison**
   - Widget compares categories (cohorts), not individual vendors
   - Use "Comparison Radar" widget for single vendor comparisons

2. **Fixed Scale (1-5)**
   - Assumes all pillar scores scale to 1-5
   - Works with current data structure

3. **No Historical Data**
   - Only compares current researched vs validated
   - Doesn't track changes over time

4. **Mobile Responsiveness**
   - Stacks to single column on <1200px
   - Some crowding possible on small screens

---

## Future Extensibility

The widget is designed to support:

1. **Additional Score Modes**
   - Add new mode option in `computeAveragesForScoreMode()`
   - Example: `scoreMode === 'updated'`

2. **Custom Delta Calculations**
   - Extend delta table with percentile rank
   - Add median, mode calculations

3. **Export Functionality**
   - CSV export of delta table
   - PNG export of radar charts

4. **Multi-Category Comparison**
   - Compare 3+ categories side-by-side
   - Instead of just 2 (researched vs validated)

5. **Trend Analysis**
   - If validation happens in phases
   - Track delta progress over time

---

## Testing Checklist

- [ ] Widget renders on Analysis page
- [ ] Config modal opens/closes
- [ ] Category type dropdown works
- [ ] Category value dropdown populates correctly
- [ ] Axes selection works (all 3 options)
- [ ] Delta metrics toggle works
- [ ] Save persists state to localStorage
- [ ] Page refresh restores saved state
- [ ] Radars render without errors
- [ ] Colors match (blue for researched, green for validated)
- [ ] Delta table shows correct values
- [ ] Delta colors correct (green positive, orange negative)
- [ ] Widget responds to page filters
- [ ] Widget hides when filtered results = 0
- [ ] Multiple vendors improve readability (radars more filled)

---

## Support & Maintenance

For questions about this widget:
1. Check [VALIDATION_COMPARISON_QUICK_START.md](VALIDATION_COMPARISON_QUICK_START.md) for user guide
2. Review this technical document for architecture
3. Check browser console for JavaScript errors
4. Verify vendor data structure matches expected schema
5. Test with provided vendor JSON files
