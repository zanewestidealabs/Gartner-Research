# Testing & Deployment Checklist

## Pre-Testing Verification

- [ ] All files have been modified (HTML, CSS, JS)
- [ ] Flask app loads: `python -c "import app; print('OK')"`
- [ ] No JavaScript console errors visible
- [ ] No HTML validation errors
- [ ] CSS file is valid

---

## Functional Testing

### Widget Rendering
- [ ] Widget appears on Analysis tab (📈)
- [ ] Widget shows in correct position (3 columns × 2 rows)
- [ ] Widget header displays "Researched vs Validated Analysis"
- [ ] Gear icon (⚙) visible in header
- [ ] Resize handle visible (≡)

### Initial State
- [ ] Widget loads with "All Vendors" as default category
- [ ] Both radar charts render immediately
- [ ] Radar charts have proper colors (blue & green)
- [ ] Delta table appears below radars
- [ ] Vendor count displays correctly
- [ ] No JavaScript errors in console

### Configuration Modal

#### Opening
- [ ] Click gear icon opens modal
- [ ] Modal title shows: "Configure Researched vs Validated Comparison"
- [ ] Modal has 4 dropdowns/toggles
- [ ] Close button (×) visible
- [ ] Save/Cancel buttons visible

#### Category Type Dropdown
- [ ] Can select "All Vendors"
- [ ] Can select "Region"
- [ ] Can select "Startup / Established"
- [ ] Can select "AI-First / Traditional"
- [ ] Can select "IR Focus Type"

#### Category Value Dropdown
- [ ] Shows "N/A - All Vendors" when type = "All Vendors"
- [ ] Shows list of regions when type = "Region"
- [ ] Shows "Startup" / "Established" when type = "Startup / Established"
- [ ] Shows "AI-First" / "Traditional" when type = "AI-First / Traditional"
- [ ] Shows list of IR focus types when type = "IR Focus Type"

#### Axes Selection
- [ ] Can select "Pillars (5)"
- [ ] Can select "Sub-pillars (20)"
- [ ] Can select "Both (25)"

#### Delta Metrics Toggle
- [ ] Checkbox is checked by default
- [ ] Can uncheck to hide delta table
- [ ] Can check to show delta table

#### Save Functionality
- [ ] Click Save applies changes to widget
- [ ] Modal closes after Save
- [ ] Widget updates with new configuration
- [ ] Vendor count updates if category changes

#### Cancel Functionality
- [ ] Click Cancel closes modal without changes
- [ ] Widget retains previous configuration
- [ ] No console errors

### Radar Charts

#### Researched Radar (Blue)
- [ ] Displays 5-point concentric rings
- [ ] Blue polygon overlay present
- [ ] 5 axis labels visible (PLA, INV, REM, PMG, LAW)
- [ ] Data points (dots) visible at polygon vertices
- [ ] Proper colors (blue stroke, light blue fill)

#### Validated Radar (Green)
- [ ] Displays 5-point concentric rings
- [ ] Green polygon overlay present
- [ ] 5 axis labels visible (PLA, INV, REM, PMG, LAW)
- [ ] Data points (dots) visible at polygon vertices
- [ ] Proper colors (green stroke, light green fill)

#### SVG Scaling
- [ ] Charts responsive to container size
- [ ] Charts resize with window resize
- [ ] Labels readable at different sizes
- [ ] No overlapping elements

### Delta Analysis Table

#### Table Structure
- [ ] Table header: "Delta Analysis (Validated - Researched)"
- [ ] Table has columns: Metric, Researched, Validated, Delta, % Δ
- [ ] 5 rows (one per pillar) with Axes = Pillars
- [ ] 20 rows (one per sub-pillar) with Axes = Sub-pillars
- [ ] 25 rows with Axes = Both

#### Data Values
- [ ] Researched column shows average researched scores
- [ ] Validated column shows average validated scores
- [ ] Delta column shows validated - researched
- [ ] % Δ column shows percentage change
- [ ] Values are positive/negative as appropriate

#### Color Coding
- [ ] Positive delta (>+0.05) displays in green
- [ ] Negative delta (<-0.05) displays in orange
- [ ] Neutral delta (between -0.05 and +0.05) displays in gray
- [ ] Plus sign (+) shows for positive values
- [ ] Minus sign (-) shows for negative values

#### Delta Toggle
- [ ] Table appears when delta toggle is checked
- [ ] Table disappears when delta toggle is unchecked
- [ ] Toggle state persists after Save

---

## Category Testing

### All Vendors Category
- [ ] Shows all vendors in average
- [ ] Displays correct total vendor count
- [ ] Radars fully rendered (scores ~2-4.5 range typical)
- [ ] Delta values reasonable (typically ±0.3)

### Region: Global
- [ ] Filter shows only Global vendors
- [ ] Vendor count reduced appropriately
- [ ] Radars update with new averages
- [ ] Delta table recalculates
- [ ] Counts match vendor data

### Region: North America
- [ ] Filter shows only N.A. vendors
- [ ] Vendor count appropriate for region
- [ ] Radars display regional averages
- [ ] Settings persist through page refresh

### Startup/Established
- [ ] Can compare startup companies
- [ ] Can compare established companies
- [ ] Vendor counts differ (typically 20-30 startups, rest established)
- [ ] Score profiles differ visibly (startups may have lower scores)

### AI-First/Traditional
- [ ] Can compare AI-first vendors (higher INV/REM typically)
- [ ] Can compare traditional vendors (more balanced)
- [ ] Vendor counts differ appropriately
- [ ] Score patterns show AI vs traditional differences

### IR Focus Type
- [ ] Can compare "Core Competency" vendors
- [ ] Can compare "Assistance Component" vendors
- [ ] Vendor counts appropriate for each type
- [ ] Scores differ by type (core competency typically higher)

---

## Axes Testing

### Pillars (5 Dimensions)
- [ ] Radar displays 5 axes: PLA, INV, REM, PMG, LAW
- [ ] Delta table shows 5 rows
- [ ] Compact visual (easy to read)
- [ ] Clear distinctions between pillars

### Sub-pillars (20 Dimensions)
- [ ] Radar displays 20 axes (PLA-01 through LAW-04)
- [ ] Delta table shows 20 rows
- [ ] Labels may overlap on small screens (acceptable)
- [ ] Detailed view shows capability breakdown
- [ ] Able to identify specific sub-pillar differences

### Both (25 Dimensions)
- [ ] Radar displays all 25 axes
- [ ] Delta table shows 25 rows
- [ ] May be crowded on small screens (acceptable)
- [ ] Provides most comprehensive view
- [ ] All major and minor dimensions visible

---

## State Persistence Testing

### LocalStorage Saving
- [ ] Open configuration, select Region → Global, save
- [ ] Open browser developer console: 
  ```javascript
  JSON.parse(localStorage.getItem('validationComparisonState'))
  ```
- [ ] Should show: `{categoryType: 'region', categoryValue: 'Global', ...}`

### Persistence After Refresh
- [ ] Configure widget with specific settings (e.g., Region → Europe, Sub-pillars)
- [ ] Press F5 to refresh page
- [ ] Widget should display same configuration
- [ ] Click gear to verify settings are as set before refresh

### Persistence After Tab Switch
- [ ] Configure widget (Region → APAC, Show Delta)
- [ ] Switch to different tab (Vendors, Cross-Section, etc.)
- [ ] Return to Analysis tab
- [ ] Configuration should be unchanged

### Clear Settings
- [ ] Open browser developer console
- [ ] Run: `localStorage.removeItem('validationComparisonState')`
- [ ] Refresh page
- [ ] Widget should show defaults (All Vendors, Pillars, Delta On)

---

## Dark Mode Testing

### Light Mode
- [ ] Widget renders in light colors
- [ ] Radars visible with proper contrast
- [ ] Delta table readable
- [ ] Text color appropriate for light background

### Dark Mode
- [ ] Click moon icon (🌙) in navigation
- [ ] Widget adapts to dark theme
- [ ] Radars visible with proper contrast
- [ ] Text color readable on dark background
- [ ] Color-coded deltas still distinguishable
- [ ] Toggle back to light mode - works fine

---

## Responsive Design Testing

### Desktop (1920×1080)
- [ ] Widget displays full 3×2 grid size
- [ ] Both radars side-by-side
- [ ] Delta table full width
- [ ] All text/numbers easily readable
- [ ] Resize handle works

### Tablet (1024×768)
- [ ] Widget stacks to single column
- [ ] Radars stack vertically
- [ ] Delta table stacks below
- [ ] Text remains readable
- [ ] No overlapping elements

### Mobile (375×667)
- [ ] Widget fits screen width
- [ ] Must scroll to see full widget
- [ ] Configuration modal is full-screen (appropriate for mobile)
- [ ] Text is readable
- [ ] Touch targets large enough for interaction

---

## Data Accuracy Testing

### Manual Calculation
1. Get vendor list with researched and validated scores
2. Manually calculate average for one pillar:
   ```
   Researched Avg = (vendor1.researched[PLA] + vendor2.researched[PLA] + ...) / count
   Validated Avg = (vendor1.validated[PLA] + vendor2.validated[PLA] + ...) / count
   ```
3. Compare with widget display values
4. Should match (within 0.01 due to rounding)

### Vendor Count Validation
- [ ] Manual count of vendors matching category
- [ ] Compare with displayed count in widget
- [ ] Should match exactly

### Delta Calculation
- [ ] Delta should = Validated - Researched
- [ ] Negative deltas show orange ✓
- [ ] Positive deltas show green ✓
- [ ] Percentage should = (Delta / Researched) × 100

### Missing Data Handling
- [ ] Vendors without researched scores: handled gracefully
- [ ] Vendors without validated scores: handled gracefully
- [ ] Returns 0 for missing values: verify correct
- [ ] Averages computed only on non-zero values: verify

---

## Error Handling Testing

### No Vendors Match Category
- [ ] Select impossible category (if possible)
- [ ] Widget shows: "No vendors match the selected category..."
- [ ] No JavaScript errors
- [ ] Gear icon still works
- [ ] Can configure to fix

### Missing Vendor Data
- [ ] Test with vendor JSON lacking researched scores
- [ ] Widget should derive from sub-pillars
- [ ] Or show zeros gracefully
- [ ] No crashes or console errors

### Malformed State in localStorage
- [ ] Manually set invalid JSON in localStorage
- [ ] Page refresh should not crash
- [ ] Should revert to defaults gracefully

### Very Large Vendor Count
- [ ] Test with 500+ vendors (if available)
- [ ] Performance should remain acceptable (<500ms load)
- [ ] Radars should still render
- [ ] No memory leaks

---

## Integration Testing

### With Filters
- [ ] Apply vendor filter on Analysis page
- [ ] Widget updates to show only filtered vendors
- [ ] Vendor count decreases
- [ ] Radars update accordingly
- [ ] Delta metrics recalculate

### With Score Mode
- [ ] Change Score Mode dropdown (top right)
- [ ] Widget continues to show both modes (research + validated)
- [ ] Score Mode dropdown doesn't affect this widget
- [ ] Other widgets respect the Score Mode change

### With Vendor File Switch
- [ ] Change vendor data file using file selector (top right)
- [ ] Widget updates with new vendor data
- [ ] Counts change appropriately
- [ ] Radars update

### With Customization Modal
- [ ] Click "⚙ Customize Widgets" at page top
- [ ] Find "Researched vs Validated Comparison" checkbox
- [ ] Uncheck it → widget hides (gets .hidden class)
- [ ] Check it → widget reappears
- [ ] Click Save Preferences
- [ ] Page refresh → preference persists

---

## Browser Compatibility Testing

### Chrome
- [ ] Latest Chrome version
- [ ] Widget renders correctly
- [ ] All interactive features work
- [ ] localStorage works
- [ ] No console warnings

### Firefox
- [ ] Latest Firefox version
- [ ] Widget renders correctly
- [ ] SVG charts display properly
- [ ] All features work
- [ ] No console warnings

### Safari
- [ ] Latest Safari version
- [ ] Widget renders
- [ ] CSS Grid layout works
- [ ] SVG rendering correct
- [ ] localStorage functional

### Edge
- [ ] Latest Edge version
- [ ] All features work
- [ ] Consistent with Chrome (both Chromium-based)

### Mobile Browsers
- [ ] Chrome on Android
- [ ] Safari on iOS
- [ ] Layout responsive
- [ ] Touch interactions work

---

## Performance Testing

### Initial Load
- [ ] Time to first render: <500ms
- [ ] No layout shift/jank
- [ ] SVG generates smoothly

### Configuration Change
- [ ] Modal opens: <100ms
- [ ] Widget updates on Save: <200ms
- [ ] No UI blocking
- [ ] Smooth transitions

### Large Vendor Set
- [ ] 300+ vendors: <500ms to compute averages
- [ ] 300+ vendors: <200ms to render radars
- [ ] No memory usage spike
- [ ] No performance degradation with multiple refreshes

### Zoom/Resize
- [ ] Window resize: radars update smoothly
- [ ] Page zoom (100-200%): still readable
- [ ] No lag or flicker

---

## Accessibility Testing

### Keyboard Navigation
- [ ] Tab through configuration modal elements
- [ ] Enter activates buttons
- [ ] Escape closes modal
- [ ] Shift+Tab goes backwards
- [ ] Focus visible on all elements

### Screen Reader
- [ ] Widget has descriptive heading
- [ ] SVG has aria-label
- [ ] Buttons have aria-label
- [ ] Form labels associated with inputs
- [ ] Table is semantic

### Color Contrast
- [ ] Text on background: AA standard minimum
- [ ] Delta colors distinguishable for colorblind users
- [ ] Blue/green colors have sufficient contrast

### Font Size
- [ ] Readable at 100% zoom
- [ ] Still readable at 200% zoom
- [ ] No text cutoff

---

## User Experience Testing

### First-Time User
- [ ] New user can find widget
- [ ] Configuration is intuitive
- [ ] Modal labels are clear
- [ ] Defaults make sense
- [ ] Results are understandable

### Experienced User
- [ ] Quick access to configuration
- [ ] Easy to switch between categories
- [ ] State persists (no need to reconfigure)
- [ ] Efficient workflow

### Interpretation
- [ ] Color-coded deltas are intuitive (green=good, red=bad)
- [ ] Vendor counts are clear
- [ ] Radar shape differences obvious
- [ ] Delta numbers understandable

---

## Regression Testing

### Existing Widgets Still Work
- [ ] Dashboard widget appears
- [ ] All charts render
- [ ] Vendor list works
- [ ] Filters work
- [ ] Legend displays

### Other Analysis Features
- [ ] Query builder works
- [ ] Filter application works
- [ ] Statistics update
- [ ] Other radars display

### Navigation
- [ ] All tabs accessible
- [ ] No broken links
- [ ] Page navigation works

---

## Final Sign-Off

### Code Quality
- [ ] No console errors
- [ ] No console warnings (legitimate)
- [ ] Code is readable
- [ ] Comments explain complex logic
- [ ] Indentation consistent

### Documentation
- [ ] User guide complete
- [ ] Technical docs complete
- [ ] Quick start available
- [ ] Troubleshooting tips included

### Deployment Readiness
- [ ] All files committed
- [ ] No uncommitted changes
- [ ] Ready for production
- [ ] User communication prepared

---

## Testing Sign-Off

| Category | Status | Notes | Date |
|----------|--------|-------|------|
| Functional | ☐ | | |
| Categories | ☐ | | |
| Axes | ☐ | | |
| State | ☐ | | |
| Dark Mode | ☐ | | |
| Responsive | ☐ | | |
| Data | ☐ | | |
| Errors | ☐ | | |
| Integration | ☐ | | |
| Browser | ☐ | | |
| Performance | ☐ | | |
| Accessibility | ☐ | | |
| UX | ☐ | | |
| Regression | ☐ | | |

---

## Known Issues & Workarounds

### Issue 1: [Description]
**Workaround**: [Solution]

### Issue 2: [Description]
**Workaround**: [Solution]

*(Update as testing reveals any issues)*

---

## Testing Complete! ✅

Once all checkboxes are marked, the widget is ready for:
- Production deployment
- User training
- Documentation finalization
- Support handoff
