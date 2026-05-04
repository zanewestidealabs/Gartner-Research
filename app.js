// Application State
const appState = {
    vendors: [],
    filteredVendors: [],
    filters: {},
    searchQuery: '',
    fieldMetadata: {},
    scoreLegend: {},
    scoreMode: 'validated', // validated | researched | ai_researched | current
    currentVendorFile: null,
    currentSchemaFile: null,
    schemaDetail: null,   // Cached schema detail from /api/schema-detail
    pillarsGrouped: [],
    currentView: 'vendors',
    subPillars: [],
    selectedSubPillars: [], // Array of sub-pillar IDs to display as columns
    pillarMetadata: {}, // Pillar codes and their names
    pillarVisibility: { PLA: true, INV: true, REM: true, PMG: true, LAW: true }, // Track pillar expand/collapse
    columnVisibility: {
        // Base columns
        vendor: true,
        region: true,
        specialization: true,
        ir_focus_type: true,
        is_ai_first: true,
        is_startup: true,
        // Pillars
        PLA: true,
        INV: true,
        REM: true,
        PMG: true,
        LAW: true
        // Sub-pillars will be added dynamically
    }
};

// Vendor report modal state
const vendorReportState = {
    vendor: null,
    vendorJson: ''
};

// Cross-section (pivot) sheet state
const crossSectionState = {
    metric: 'avg', // avg | count | percent

    // Exactly one axis should be cohorts and the other should be scores.
    xAxis: {
        type: 'cohorts', // cohorts | scores
        items: ['attr|region|Global']
    },
    yAxis: {
        type: 'scores', // scores | cohorts
        items: ['score|pillar|PLA']
    },

    // Cohort generation mode (kept for backward compatibility / optional use)
    cohortMode: 'cohorts', // cohorts | groupby
    groupByField: 'region',
    groupByTopN: 8
};

function loadCrossSectionState() {
    try {
        const raw = localStorage.getItem('crossSectionState');
        if (!raw) return;
        const parsed = JSON.parse(raw);
        if (parsed && typeof parsed === 'object') {
            // New model
            if (parsed.metric) crossSectionState.metric = parsed.metric;
            if (parsed.xAxis && typeof parsed.xAxis === 'object') {
                if (parsed.xAxis.type) crossSectionState.xAxis.type = parsed.xAxis.type;
                if (Array.isArray(parsed.xAxis.items)) crossSectionState.xAxis.items = parsed.xAxis.items.slice();
            }
            if (parsed.yAxis && typeof parsed.yAxis === 'object') {
                if (parsed.yAxis.type) crossSectionState.yAxis.type = parsed.yAxis.type;
                if (Array.isArray(parsed.yAxis.items)) crossSectionState.yAxis.items = parsed.yAxis.items.slice();
            }

            if (parsed.cohortMode) crossSectionState.cohortMode = parsed.cohortMode;
            if (parsed.groupByField) crossSectionState.groupByField = parsed.groupByField;
            if (parsed.groupByTopN) crossSectionState.groupByTopN = Number(parsed.groupByTopN) || crossSectionState.groupByTopN;

            // Migration from older model (xDim/yDim + cohorts[] + yMode + cellMetric)
            if (!parsed.xAxis && !parsed.yAxis) {
                const xDim = parsed.xDim || 'cohorts';
                const yDim = parsed.yDim || (xDim === 'cohorts' ? 'scores' : 'cohorts');
                crossSectionState.xAxis.type = xDim;
                crossSectionState.yAxis.type = yDim;

                const metric = parsed.cellMetric || (parsed.showDetail ? 'avg' : 'avg');
                crossSectionState.metric = metric;

                // Cohort items
                const cohorts = Array.isArray(parsed.cohorts) ? parsed.cohorts.slice() : ['attr|region|Global'];
                const cohortItems = cohorts.filter(Boolean).filter((v, idx) => idx < 50);
                // Score items derived from yMode
                const yMode = parsed.yMode || 'pillars';
                const scoreItems = [];
                if (yMode === 'pillars' || yMode === 'both') {
                    ['PLA', 'INV', 'REM', 'PMG', 'LAW'].forEach(p => scoreItems.push(`score|pillar|${p}`));
                }
                if (yMode === 'subpillars' || yMode === 'both') {
                    ['PLA', 'INV', 'REM', 'PMG', 'LAW'].forEach(p => {
                        for (let i = 1; i <= 4; i++) {
                            scoreItems.push(`score|subpillar|${p}-0${i}`);
                        }
                    });
                }
                if (!scoreItems.length) scoreItems.push('score|pillar|PLA');

                if (crossSectionState.xAxis.type === 'cohorts') {
                    crossSectionState.xAxis.items = cohortItems.length ? cohortItems : ['all'];
                    crossSectionState.yAxis.items = scoreItems;
                } else {
                    crossSectionState.xAxis.items = scoreItems;
                    crossSectionState.yAxis.items = cohortItems.length ? cohortItems : ['all'];
                }
            }
        }
    } catch {
        // ignore
    }
}

function persistCrossSectionState() {
    try {
        localStorage.setItem('crossSectionState', JSON.stringify(crossSectionState));
    } catch {
        // ignore
    }
}

function escapeHtml(value) {
    const s = String(value ?? '');
    return s
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function formatMaybeNumber(v, digits = 2) {
    if (v === undefined || v === null || v === '') return '-';
    const n = Number(v);
    if (Number.isFinite(n)) return n.toFixed(digits);
    return String(v);
}

function copyToClipboard(text) {
    if (!text) return;
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text);
        return;
    }
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
}

function downloadText(filename, text, mime = 'application/json') {
    const blob = new Blob([text], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function sanitizeFilenamePart(value) {
    return String(value || '')
        .trim()
        .replace(/\s+/g, '_')
        .replace(/[^a-zA-Z0-9_-]+/g, '_')
        .replace(/_+/g, '_')
        .replace(/^_+|_+$/g, '');
}

function getVendorsForExport() {
    if (Array.isArray(appState.filteredVendors) && appState.filteredVendors.length) return appState.filteredVendors;
    return Array.isArray(appState.vendors) ? appState.vendors : [];
}

function getUniqueTopLevelKeysFromVendors(vendors, { maxSamples = 200 } = {}) {
    const set = new Set();
    const list = Array.isArray(vendors) ? vendors : [];
    const n = Math.min(list.length, maxSamples);
    for (let i = 0; i < n; i++) {
        const v = list[i];
        if (!v || typeof v !== 'object') continue;
        Object.keys(v).forEach(k => set.add(k));
    }
    return Array.from(set).sort((a, b) => String(a).localeCompare(String(b)));
}

function getByDotPath(obj, path) {
    if (!path) return undefined;
    const parts = String(path).split('.').filter(Boolean);
    let cur = obj;
    for (const p of parts) {
        if (!cur || typeof cur !== 'object') return undefined;
        cur = cur[p];
    }
    return cur;
}

function setByDotPath(out, path, value) {
    const parts = String(path).split('.').filter(Boolean);
    if (!parts.length) return;
    let cur = out;
    for (let i = 0; i < parts.length - 1; i++) {
        const p = parts[i];
        if (!cur[p] || typeof cur[p] !== 'object') cur[p] = {};
        cur = cur[p];
    }
    cur[parts[parts.length - 1]] = value;
}

function pickFields(obj, fields) {
    const out = {};
    (fields || []).forEach(f => {
        const key = String(f || '').trim();
        if (!key) return;
        const val = key.includes('.') ? getByDotPath(obj, key) : obj?.[key];
        if (val === undefined) return;
        if (key.includes('.')) setByDotPath(out, key, val);
        else out[key] = val;
    });
    return out;
}

function getSchemaExportObject() {
    return {
        exported_at: new Date().toISOString(),
        vendor_file: appState.currentVendorFile,
        score_mode: appState.scoreMode,
        field_metadata: appState.fieldMetadata || {},
        score_legend: appState.scoreLegend || {},
        pillars_grouped: appState.pillarsGrouped || [],
        all_sub_pillars: appState.subPillars || [],
        pillar_metadata: appState.pillarMetadata || {}
    };
}

function exportVendorsJson({ scope = 'raw', fields = [] } = {}) {
    const vendors = getVendorsForExport();
    const dataset = sanitizeFilenamePart(appState.currentVendorFile || 'dataset') || 'dataset';
    const scoreMode = sanitizeFilenamePart(appState.scoreMode || 'validated') || 'validated';
    const suffix = (scope === 'selected') ? 'selected' : 'raw';
    const filename = `vendors_${scoreMode}_${suffix}_${dataset}.json`;

    const payload = (scope === 'selected')
        ? vendors.map(v => pickFields(v, fields))
        : vendors;

    downloadText(filename, JSON.stringify(payload, null, 2), 'application/json');
}

function valueForCsvCell(value) {
    if (value === undefined || value === null) return '';
    if (typeof value === 'string') return value;
    if (typeof value === 'number') return Number.isFinite(value) ? String(value) : '';
    if (typeof value === 'boolean') return value ? 'true' : 'false';
    // Objects/arrays -> JSON string in one cell
    try {
        return JSON.stringify(value);
    } catch {
        return String(value);
    }
}

function flattenObjectToDotMap(obj, { maxDepth = 6 } = {}) {
    const out = new Map();

    const walk = (value, prefix, depth) => {
        if (depth > maxDepth) {
            if (prefix) out.set(prefix, valueForCsvCell(value));
            return;
        }

        if (value === null || value === undefined) {
            if (prefix) out.set(prefix, '');
            return;
        }

        const t = typeof value;
        if (t === 'string' || t === 'number' || t === 'boolean') {
            if (prefix) out.set(prefix, valueForCsvCell(value));
            return;
        }

        // Arrays: keep as JSON in one column
        if (Array.isArray(value)) {
            if (prefix) out.set(prefix, valueForCsvCell(value));
            return;
        }

        // Plain object
        if (t === 'object') {
            const keys = Object.keys(value);
            if (!keys.length) {
                if (prefix) out.set(prefix, '');
                return;
            }
            keys.forEach(k => {
                const nextPrefix = prefix ? `${prefix}.${k}` : k;
                walk(value[k], nextPrefix, depth + 1);
            });
            return;
        }

        if (prefix) out.set(prefix, valueForCsvCell(value));
    };

    walk(obj, '', 0);
    return out;
}

function getAllDotPathsFromVendors(vendors, { maxDepth = 6, maxSamples = 2000 } = {}) {
    const set = new Set();
    const list = Array.isArray(vendors) ? vendors : [];
    const n = Math.min(list.length, maxSamples);
    for (let i = 0; i < n; i++) {
        const v = list[i];
        if (!v || typeof v !== 'object') continue;
        const map = flattenObjectToDotMap(v, { maxDepth });
        for (const k of map.keys()) {
            if (k) set.add(k);
        }
    }
    return Array.from(set).sort((a, b) => String(a).localeCompare(String(b)));
}

function exportSchemaJson() {
    const schema = getSchemaExportObject();
    const dataset = sanitizeFilenamePart(appState.currentVendorFile || 'dataset') || 'dataset';
    const filename = `schema_${dataset}.json`;
    downloadText(filename, JSON.stringify(schema, null, 2), 'application/json');
}

function getVendorsExportColumns() {
    const cols = [];
    cols.push({ key: 'vendor', label: 'Vendor', get: v => v?.vendor ?? '' });
    cols.push({ key: 'region', label: 'Region', get: v => v?.region ?? '' });
    cols.push({ key: 'specialization', label: 'Specialization', get: v => v?.specialization ?? '' });
    cols.push({ key: 'ir_focus_type', label: 'IR Focus Type', get: v => v?.ir_focus_type ?? '' });
    cols.push({ key: 'is_ai_first', label: 'AI-First', get: v => (v?.is_ai_first ? 'Yes' : 'No') });
    cols.push({ key: 'is_startup', label: 'Startup', get: v => (v?.is_startup ? 'Yes' : 'No') });

    const pillarOrder = ['PLA', 'INV', 'REM', 'PMG', 'LAW'];
    pillarOrder.forEach(code => {
        if (appState.columnVisibility && appState.columnVisibility[code] === false) return;
        const label = appState.fieldMetadata?.[code]?.name ? `${code} - ${appState.fieldMetadata[code].name}` : code;
        cols.push({
            key: code,
            label,
            get: (vendor) => {
                const scores = getEffectivePillarScores(vendor) || {};
                const val = scores[code];
                const n = Number(val);
                return Number.isFinite(n) ? n : '';
            }
        });
    });

    // Sub-pillars: export selected sub-pillars (respects selection, not expand/collapse)
    const selected = Array.isArray(appState.selectedSubPillars) ? appState.selectedSubPillars.slice() : [];
    const byPillar = new Map(pillarOrder.map(p => [p, []]));
    selected.forEach(id => {
        const p = String(id || '').split('-')[0];
        if (!byPillar.has(p)) byPillar.set(p, []);
        byPillar.get(p).push(String(id));
    });

    pillarOrder.forEach(p => {
        const ids = byPillar.get(p) || [];
        ids.forEach(subId => {
            if (appState.columnVisibility && appState.columnVisibility[subId] === false) return;
            cols.push({
                key: subId,
                label: subId,
                get: (vendor) => {
                    const map = getEffectiveGranularMapping(vendor);
                    const val = map?.[p]?.[subId];
                    const n = Number(val);
                    return Number.isFinite(n) ? n : '';
                }
            });
        });
    });

    return cols;
}

function exportVendorsCsv({ scope = 'table', fields = [] } = {}) {
    const vendors = getVendorsForExport();

    let cols = [];
    if (scope === 'table') {
        // Full “spreadsheet” export: one column per dot-path across the vendor JSON.
        const paths = getAllDotPathsFromVendors(vendors);
        cols = paths.map(path => ({
            key: path,
            label: path,
            get: (v) => {
                const map = flattenObjectToDotMap(v);
                return map.get(path) ?? '';
            }
        }));
    } else if (scope === 'raw') {
        const keys = getUniqueTopLevelKeysFromVendors(vendors);
        cols = keys.map(k => ({
            key: k,
            label: k,
            get: (v) => valueForCsvCell(v?.[k])
        }));
    } else if (scope === 'selected') {
        const selected = (fields || []).map(s => String(s || '').trim()).filter(Boolean);
        cols = selected.map(path => ({
            key: path,
            label: path,
            get: (v) => {
                const val = path.includes('.') ? getByDotPath(v, path) : v?.[path];
                return valueForCsvCell(val);
            }
        }));
    } else {
        cols = getVendorsExportColumns();
    }

    const lines = [];
    lines.push(cols.map(c => csvEscape(c.label)).join(','));
    vendors.forEach(v => {
        lines.push(cols.map(c => csvEscape(c.get(v))).join(','));
    });

    const dataset = sanitizeFilenamePart(appState.currentVendorFile || 'dataset') || 'dataset';
    const mode = sanitizeFilenamePart(appState.scoreMode || 'validated') || 'validated';
    const suffix = (scope === 'raw') ? 'raw' : (scope === 'selected' ? 'selected' : 'table');
    const filename = `vendors_${mode}_${suffix}_${dataset}.csv`;
    downloadText(filename, lines.join('\n'), 'text/csv');
}

function exportSchemaCsv() {
    const schema = getSchemaExportObject();
    const meta = schema.field_metadata || {};
    const entries = Object.entries(meta);
    const lines = [];
    lines.push(['Field', 'Name', 'Description'].map(csvEscape).join(','));
    entries
        .sort(([a], [b]) => String(a).localeCompare(String(b)))
        .forEach(([field, m]) => {
            const name = m?.name ?? '';
            const desc = m?.description ?? '';
            lines.push([field, name, desc].map(csvEscape).join(','));
        });

    const dataset = sanitizeFilenamePart(appState.currentVendorFile || 'dataset') || 'dataset';
    const filename = `schema_${dataset}.csv`;
    downloadText(filename, lines.join('\n'), 'text/csv');
}

function setupVendorsExportModal() {
    const openBtn = document.getElementById('vendors-export-open');
    const modal = document.getElementById('vendors-export-modal');
    if (!openBtn || !modal) return;

    const formatSel = document.getElementById('vendors-export-format');
    const dataSel = document.getElementById('vendors-export-data');
    const scopeWrap = document.getElementById('vendors-export-scope');
    const scopeSel = document.getElementById('vendors-export-scope-mode');
    const fieldsWrap = document.getElementById('vendors-export-fields');
    const fieldsSearch = document.getElementById('vendors-export-fields-search');
    const fieldsList = document.getElementById('vendors-export-fields-list');
    const fieldsCount = document.getElementById('vendors-export-fields-count');
    const selectVisibleBtn = document.getElementById('vendors-export-fields-select-visible');
    const selectAllBtn = document.getElementById('vendors-export-fields-select-all');
    const selectNoneBtn = document.getElementById('vendors-export-fields-select-none');
    const note = document.getElementById('vendors-export-note');
    const runBtn = document.getElementById('vendors-export-run');
    const cancelBtn = document.getElementById('vendors-export-cancel');

    const state = {
        availableFields: [],
        selectedFields: new Set(),
        search: ''
    };

    const defaultVisibleFields = () => {
        // Start from the same columns the user sees in the vendor table.
        const fields = [];
        ['vendor', 'region', 'specialization', 'ir_focus_type', 'is_ai_first', 'is_startup'].forEach(k => {
            if (appState.columnVisibility?.[k] !== false) fields.push(k);
        });
        ['PLA', 'INV', 'REM', 'PMG', 'LAW'].forEach(k => {
            // These are *computed* in UI; but still useful as raw fields if present.
            // Prefer exporting the validated/researched/current score objects instead.
            // We include pillar score objects if they exist.
        });
        // Include typical score objects if present.
        ['pillar_scores_validated', 'pillar_scores_researched', 'pillar_scores',
         'granular_mapping_validated', 'granular_mapping',
         'sub_pillar_scores_researched', 'capability_analysis', 'capability_analysis_source'
        ].forEach(k => fields.push(k));
        return fields;
    };

    const renderFields = () => {
        if (!fieldsList || !fieldsCount) return;
        const q = state.search.trim().toLowerCase();
        const visible = state.availableFields.filter(f => !q || String(f).toLowerCase().includes(q));
        fieldsList.innerHTML = '';

        visible.forEach(field => {
            const row = document.createElement('label');
            row.className = 'vendors-export-fields-item';
            const cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.checked = state.selectedFields.has(field);
            cb.addEventListener('change', () => {
                if (cb.checked) state.selectedFields.add(field);
                else state.selectedFields.delete(field);
                renderCounts();
            });
            const code = document.createElement('code');
            code.textContent = field;
            row.appendChild(cb);
            row.appendChild(code);
            fieldsList.appendChild(row);
        });

        renderCounts(visible.length);
    };

    const renderCounts = (visibleCountOverride) => {
        if (!fieldsCount) return;
        const visibleCount = (typeof visibleCountOverride === 'number')
            ? visibleCountOverride
            : state.availableFields.filter(f => !state.search.trim() || String(f).toLowerCase().includes(state.search.trim().toLowerCase())).length;
        fieldsCount.textContent = `${state.selectedFields.size} selected (${visibleCount} shown)`;
    };

    const ensureFieldsLoaded = () => {
        if (state.availableFields.length) return;
        const vendors = getVendorsForExport();
        const keys = getUniqueTopLevelKeysFromVendors(vendors);
        // Ensure a few important fields exist even if missing in sample
        const extras = ['vendor', 'region', 'specialization', 'ir_focus_type', 'is_ai_first', 'is_startup'];
        extras.forEach(k => {
            if (!keys.includes(k)) keys.unshift(k);
        });
        state.availableFields = Array.from(new Set(keys));

        // Initialize selected fields from saved state or visible defaults
        try {
            const saved = JSON.parse(localStorage.getItem('vendorsExportSelectedFields') || '[]');
            if (Array.isArray(saved) && saved.length) {
                saved.forEach(f => state.selectedFields.add(String(f)));
            } else {
                defaultVisibleFields().forEach(f => state.selectedFields.add(String(f)));
            }
        } catch {
            defaultVisibleFields().forEach(f => state.selectedFields.add(String(f)));
        }
    };

    const persistSelectedFields = () => {
        try {
            localStorage.setItem('vendorsExportSelectedFields', JSON.stringify(Array.from(state.selectedFields)));
        } catch {
            // ignore
        }
    };

    const syncScopeOptions = () => {
        if (!scopeSel) return;
        const format = formatSel?.value || 'csv';
        // For JSON: raw/selected only. For CSV: table/raw/selected.
        const wanted = (format === 'json')
            ? ['raw', 'selected']
            : ['table', 'raw', 'selected'];

        const existing = Array.from(scopeSel.options).map(o => o.value);
        const keep = existing.filter(v => wanted.includes(v));

        // Rebuild if mismatch
        const mismatch = keep.length !== wanted.length || wanted.some((v, i) => keep[i] !== v);
        if (!mismatch) return;

        const prev = scopeSel.value;
        scopeSel.innerHTML = '';
        wanted.forEach(v => {
            const opt = document.createElement('option');
            opt.value = v;
            opt.textContent = (v === 'table') ? 'Table columns (recommended)'
                : (v === 'raw') ? 'All fields (raw)'
                : 'Selected fields only';
            scopeSel.appendChild(opt);
        });
        scopeSel.value = wanted.includes(prev) ? prev : wanted[0];
    };

    const syncVisibility = () => {
        const format = formatSel?.value || 'csv';
        const data = dataSel?.value || 'vendors';

        const showScope = (data === 'vendors');
        if (scopeWrap) scopeWrap.style.display = showScope ? '' : 'none';

        if (showScope) syncScopeOptions();

        const scope = scopeSel?.value || (format === 'json' ? 'raw' : 'table');
        const showFields = showScope && scope === 'selected';
        if (fieldsWrap) fieldsWrap.style.display = showFields ? '' : 'none';

        if (showFields) {
            ensureFieldsLoaded();
            renderFields();
        }
    };

    const updateNote = () => {
        if (!note) return;
        const data = dataSel?.value || 'vendors';
        const format = formatSel?.value || 'csv';
        if (data === 'schema') {
            note.textContent = 'Schema export includes field metadata, score legend, pillars, and sub-pillars.';
        } else if (format === 'json') {
            note.textContent = 'Vendors JSON export can be raw (all fields) or limited to selected fields.';
        } else {
            note.textContent = 'Vendors CSV export can be table columns, all fields (raw), or selected fields.';
        }
    };

    openBtn.addEventListener('click', () => {
        syncVisibility();
        updateNote();
        modal.classList.add('show');
    });

    formatSel?.addEventListener('change', () => {
        syncVisibility();
        updateNote();
    });
    dataSel?.addEventListener('change', () => {
        syncVisibility();
        updateNote();
    });
    scopeSel?.addEventListener('change', () => {
        syncVisibility();
        updateNote();
    });

    fieldsSearch?.addEventListener('input', (e) => {
        state.search = String(e.target.value || '');
        renderFields();
    });

    selectNoneBtn?.addEventListener('click', () => {
        state.selectedFields.clear();
        renderFields();
        persistSelectedFields();
    });

    selectAllBtn?.addEventListener('click', () => {
        ensureFieldsLoaded();
        state.selectedFields = new Set(state.availableFields);
        renderFields();
        persistSelectedFields();
    });

    selectVisibleBtn?.addEventListener('click', () => {
        // Select the currently-visible vendor table fields + common score objects.
        state.selectedFields.clear();
        defaultVisibleFields().forEach(f => state.selectedFields.add(String(f)));
        renderFields();
        persistSelectedFields();
    });

    cancelBtn?.addEventListener('click', () => {
        modal.classList.remove('show');
    });

    runBtn?.addEventListener('click', () => {
        const format = formatSel?.value || 'csv';
        const data = dataSel?.value || 'vendors';
        const scope = scopeSel?.value || (format === 'json' ? 'raw' : 'table');

        if (data === 'schema') {
            if (format === 'json') exportSchemaJson();
            else exportSchemaCsv();
        } else {
            if (format === 'json') {
                if (scope === 'selected') {
                    const fields = Array.from(state.selectedFields).map(s => String(s)).filter(Boolean);
                    if (!fields.length) {
                        alert('Select at least one field to export.');
                        return;
                    }
                    persistSelectedFields();
                    exportVendorsJson({ scope: 'selected', fields });
                } else {
                    exportVendorsJson({ scope: 'raw' });
                }
            } else {
                if (scope === 'selected') {
                    const fields = Array.from(state.selectedFields).map(s => String(s)).filter(Boolean);
                    if (!fields.length) {
                        alert('Select at least one field to export.');
                        return;
                    }
                    persistSelectedFields();
                    exportVendorsCsv({ scope: 'selected', fields });
                } else if (scope === 'raw') {
                    exportVendorsCsv({ scope: 'raw' });
                } else {
                    exportVendorsCsv({ scope: 'table' });
                }
            }
        }

        modal.classList.remove('show');
    });
}

function getEffectiveGranularMapping(vendor) {
    const mode = appState.scoreMode || 'validated';

    if (mode === 'ai_researched' && vendor.sub_pillar_scores_ai_researched && typeof vendor.sub_pillar_scores_ai_researched === 'object') {
        return buildGranularMappingFromSubScores(vendor.sub_pillar_scores_ai_researched);
    }

    if (mode === 'researched' && vendor.sub_pillar_scores_researched && typeof vendor.sub_pillar_scores_researched === 'object') {
        return buildGranularMappingFromSubScores(vendor.sub_pillar_scores_researched);
    }

    if (mode === 'current') {
        return vendor.granular_mapping || vendor.granular_mapping_validated || {};
    }

    // validated
    return vendor.granular_mapping_validated || vendor.granular_mapping || {};
}

function buildGranularMappingFromSubScores(subScores) {
    const out = { PLA: {}, INV: {}, REM: {}, PMG: {}, LAW: {} };
    if (!subScores || typeof subScores !== 'object') return out;
    Object.entries(subScores).forEach(([sid, v]) => {
        if (!sid || typeof sid !== 'string') return;
        const pillar = sid.split('-')[0];
        if (!out[pillar]) return;
        if (v === undefined || v === null || v === '' || Number.isNaN(Number(v))) return;
        out[pillar][sid] = Number(v);
    });
    return out;
}

function computePillarScoreFromGranular(vendor, pillarCode) {
    const granular = getEffectiveGranularMapping(vendor);
    const pillarObj = granular?.[pillarCode];
    if (!pillarObj || typeof pillarObj !== 'object') return null;

    const codes = [`${pillarCode}-01`, `${pillarCode}-02`, `${pillarCode}-03`, `${pillarCode}-04`];
    const values = codes
        .map(c => pillarObj[c])
        .filter(v => v !== undefined && v !== null && v !== '' && !Number.isNaN(Number(v)))
        .map(v => Number(v));

    if (values.length === 0) return null;
    return values.reduce((a, b) => a + b, 0) / values.length;
}

function getEffectivePillarScores(vendor) {
    const mode = appState.scoreMode || 'validated';

    if (mode === 'ai_researched') {
        if (vendor.pillar_scores_ai_researched && typeof vendor.pillar_scores_ai_researched === 'object') {
            return vendor.pillar_scores_ai_researched;
        }
    } else if (mode === 'researched') {
        if (vendor.pillar_scores_researched && typeof vendor.pillar_scores_researched === 'object') {
            return vendor.pillar_scores_researched;
        }
        // Fall back to computing from researched granular mapping synthesized above
    } else if (mode === 'validated') {
        if (vendor.pillar_scores_validated && typeof vendor.pillar_scores_validated === 'object') {
            return vendor.pillar_scores_validated;
        }
    } else if (mode === 'current') {
        if (vendor.pillar_scores && typeof vendor.pillar_scores === 'object') {
            return vendor.pillar_scores;
        }
    }

    const computed = {};
    const pillarCodes = ['PLA', 'INV', 'REM', 'PMG', 'LAW'];
    pillarCodes.forEach(p => {
        const v = computePillarScoreFromGranular(vendor, p);
        if (v !== null) computed[p] = v;
    });

    if (Object.keys(computed).length > 0) return computed;

    // Final fallback
    return vendor.pillar_scores_validated || vendor.pillar_scores || {};
}

function setScoreMode(mode, { persist = true } = {}) {
    const allowed = new Set(['validated', 'researched', 'ai_researched', 'current']);
    const next = allowed.has(mode) ? mode : 'validated';
    appState.scoreMode = next;
    if (persist) {
        localStorage.setItem('scoreMode', next);
    }
    const sel = document.getElementById('score-mode-select');
    if (sel && sel.value !== next) sel.value = next;
    // Refresh UI
    renderVendors();
    updateVendorCount();
    if (document.querySelector('.analysis-content-wrapper') &&
        document.querySelector('.analysis-content-wrapper').style.display !== 'none') {
        updateAnalytics();
    }

    if (isCrossSectionViewActive()) {
        renderCrossSectionSheet();
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    await initializeApp();
    setupEventListeners();
    setupEditFormHandler();
    await setupSubPillars();
    await loadVendorFileSelector();
    await loadVendors();
    
    // Load metadata
    try {
        const metadataResponse = await fetch('/api/metadata');
        const metadata = await metadataResponse.json();
        appState.fieldMetadata = metadata.field_metadata;
        appState.scoreLegend = metadata.score_legend;
        appState.pillarsGrouped = metadata.pillars_grouped || [];
        appState.schemaIntent = metadata.schema_intent || '';
        appState.currentSchemaFileName = metadata.schema_file || '';
    } catch (error) {
        console.error('Error loading metadata:', error);
    }
    
    // Populate legend view
    populateLegendView();

    // Score mode selector (persisted)
    const savedMode = localStorage.getItem('scoreMode');
    if (savedMode) {
        setScoreMode(savedMode, { persist: false });
    } else {
        const sel = document.getElementById('score-mode-select');
        if (sel) sel.value = appState.scoreMode;
    }

    // Now that metadata exists, re-render cross-section if visible.
    if (isCrossSectionViewActive()) {
        renderCrossSectionSheet();
    }
});

async function initializeApp() {
    // Load dark mode preference
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
    }
}

function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', handleNavigation);
    });
    
    // Dark mode toggle
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) darkModeToggle.addEventListener('click', toggleDarkMode);
    
    // Search
    const searchInput = document.getElementById('search-input');
    if (searchInput) searchInput.addEventListener('input', handleSearch);
    
    // Reset filters
    const resetFiltersBtn = document.getElementById('reset-filters');
    if (resetFiltersBtn) resetFiltersBtn.addEventListener('click', resetFilters);
    
    // Toggle column visibility modal
    const toggleFieldsBtn = document.getElementById('toggle-fields-btn');
    if (toggleFieldsBtn) {
        toggleFieldsBtn.addEventListener('click', () => {
            populateColumnVisibilityModal();
            const modal = document.getElementById('column-visibility-modal');
            if (modal) modal.classList.add('show');
        });
    }
    
    // Column visibility checkboxes
    document.addEventListener('change', (e) => {
        if (e.target.classList.contains('col-visibility-check')) {
            const column = e.target.dataset.column;
            const isChecked = e.target.checked;
            const baseColumns = ['vendor', 'region', 'specialization', 'ir_focus_type', 'is_ai_first', 'is_startup'];
            
            // Prevent deselection of base columns
            if (baseColumns.includes(column) && !isChecked) {
                e.target.checked = true;
                return; // Don't allow unchecking base columns
            }
            
            if (['PLA', 'INV', 'REM', 'PMG', 'LAW'].includes(column)) {
                // For pillars, toggle visibility and sync sub-pillars
                appState.columnVisibility[column] = isChecked;
                if (!isChecked) {
                    // Deselect all sub-pillars for this pillar
                    appState.selectedSubPillars = appState.selectedSubPillars.filter(id => !id.startsWith(column));
                    appState.subPillars.forEach(sub => {
                        if (sub.id.startsWith(column)) {
                            appState.columnVisibility[sub.id] = false;
                            // Update modal checkboxes
                            const modalCheckbox = document.querySelector(`input[data-column="${sub.id}"]`);
                            if (modalCheckbox) {
                                modalCheckbox.checked = false;
                            }
                        }
                    });
                    // Uncheck the pillar checkbox in modal
                    const pillarCheckbox = document.querySelector(`input[data-column="${column}"]`);
                    if (pillarCheckbox) {
                        pillarCheckbox.checked = false;
                    }
                } else {
                    // Check the pillar checkbox in modal
                    const pillarCheckbox = document.querySelector(`input[data-column="${column}"]`);
                    if (pillarCheckbox) {
                        pillarCheckbox.checked = true;
                    }
                }
                applyFilters(); // Re-render with updated visibility
            } else if (column.match(/^[A-Z]+-\d+$/)) {
                // For sub-pillars, toggle in selectedSubPillars and sync parent pillar
                if (isChecked) {
                    if (!appState.selectedSubPillars.includes(column)) {
                        appState.selectedSubPillars.push(column);
                    }
                    appState.columnVisibility[column] = true;
                    // Enable parent pillar automatically
                    const parentPillar = column.split('-')[0];
                    appState.columnVisibility[parentPillar] = true;
                    // Check parent pillar in modal
                    const parentCheckbox = document.querySelector(`input[data-column="${parentPillar}"]`);
                    if (parentCheckbox) {
                        parentCheckbox.checked = true;
                    }
                } else {
                    appState.selectedSubPillars = appState.selectedSubPillars.filter(id => id !== column);
                    appState.columnVisibility[column] = false;
                }
                applyFilters();
            } else {
                // For base columns
                appState.columnVisibility[column] = isChecked;
                applyFilters();
            }
        }
    });
    
    // Modal close button
    const colModalCloseBtn = document.getElementById('col-modal-close-btn');
    if (colModalCloseBtn) {
        colModalCloseBtn.addEventListener('click', () => {
            const modal = document.getElementById('column-visibility-modal');
            if (modal) modal.classList.remove('show');
        });
    }
    
    // Field info icons
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('info-icon')) {
            const field = e.target.dataset.field;
            showFieldInfo(field);
        }
    });
    
    // Modal close buttons
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.target.closest('.modal').classList.remove('show');
        });
    });
    
    // Modal background click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('show');
            }
        });
    });

    setupVendorsExportModal();
    setupVendorReportModal();
    setupCrossSectionSheet();
}



function setupCrossSectionSheet() {
    const root = document.getElementById('cross-section-view');
    if (!root) return;

    loadCrossSectionState();

    // Keep inline summary and modal UI synced with state.
    renderCrossSectionConfigUI();

    const modal = document.getElementById('cross-section-config-modal');
    const openBtn = document.getElementById('cross-open-config');
    const clearBtn = document.getElementById('cross-config-clear');
    const clearXBtn = document.getElementById('cross-config-x-clear');
    const clearYBtn = document.getElementById('cross-config-y-clear');
    const metricSel = document.getElementById('cross-config-metric');
    const xTypeSel = document.getElementById('cross-config-x-type');
    const yTypeSel = document.getElementById('cross-config-y-type');

    const resetAxisItemsToDefault = (axis) => {
        axis.items = (axis.type === 'cohorts') ? ['all'] : ['score|pillar|PLA'];
    };

    const ensureAxisTypesValid = (changed) => {
        // Exactly one cohorts and one scores.
        const x = crossSectionState.xAxis.type;
        const y = crossSectionState.yAxis.type;
        if (x === y) {
            if (changed === 'x') {
                crossSectionState.yAxis.type = (x === 'cohorts') ? 'scores' : 'cohorts';
            } else {
                crossSectionState.xAxis.type = (y === 'cohorts') ? 'scores' : 'cohorts';
            }
        }
        if (xTypeSel) xTypeSel.value = crossSectionState.xAxis.type;
        if (yTypeSel) yTypeSel.value = crossSectionState.yAxis.type;

        // Disable invalid options
        if (xTypeSel) {
            Array.from(xTypeSel.options).forEach(o => (o.disabled = (o.value === crossSectionState.yAxis.type)));
        }
        if (yTypeSel) {
            Array.from(yTypeSel.options).forEach(o => (o.disabled = (o.value === crossSectionState.xAxis.type)));
        }
    };

    const openModal = () => {
        if (!modal) return;
        renderCrossSectionConfigUI();
        modal.classList.add('show');
    };

    openBtn?.addEventListener('click', openModal);

    clearBtn?.addEventListener('click', () => {
        resetAxisItemsToDefault(crossSectionState.xAxis);
        resetAxisItemsToDefault(crossSectionState.yAxis);
        persistCrossSectionState();
        renderCrossSectionConfigUI();
        renderCrossSectionSheet();
    });

    clearXBtn?.addEventListener('click', () => {
        resetAxisItemsToDefault(crossSectionState.xAxis);
        persistCrossSectionState();
        renderCrossSectionConfigUI();
        renderCrossSectionSheet();
    });

    clearYBtn?.addEventListener('click', () => {
        resetAxisItemsToDefault(crossSectionState.yAxis);
        persistCrossSectionState();
        renderCrossSectionConfigUI();
        renderCrossSectionSheet();
    });

    metricSel?.addEventListener('change', (e) => {
        crossSectionState.metric = e.target.value;
        persistCrossSectionState();
        renderCrossSectionConfigUI();
        renderCrossSectionSheet();
    });
    xTypeSel?.addEventListener('change', (e) => {
        crossSectionState.xAxis.type = e.target.value;
        ensureAxisTypesValid('x');
        // Reset to one item when type flips
        crossSectionState.xAxis.items = (crossSectionState.xAxis.type === 'cohorts') ? ['all'] : ['score|pillar|PLA'];
        persistCrossSectionState();
        renderCrossSectionConfigUI();
        renderCrossSectionSheet();
    });
    yTypeSel?.addEventListener('change', (e) => {
        crossSectionState.yAxis.type = e.target.value;
        ensureAxisTypesValid('y');
        crossSectionState.yAxis.items = (crossSectionState.yAxis.type === 'cohorts') ? ['all'] : ['score|pillar|PLA'];
        persistCrossSectionState();
        renderCrossSectionConfigUI();
        renderCrossSectionSheet();
    });

    document.getElementById('cross-config-x-add')?.addEventListener('click', () => {
        crossSectionState.xAxis.items.push(crossSectionState.xAxis.type === 'cohorts' ? 'all' : 'score|pillar|PLA');
        persistCrossSectionState();
        renderCrossSectionConfigUI();
        renderCrossSectionSheet();
    });
    document.getElementById('cross-config-y-add')?.addEventListener('click', () => {
        crossSectionState.yAxis.items.push(crossSectionState.yAxis.type === 'cohorts' ? 'all' : 'score|pillar|PLA');
        persistCrossSectionState();
        renderCrossSectionConfigUI();
        renderCrossSectionSheet();
    });

    const pillarOrder = ['PLA', 'INV', 'REM', 'PMG', 'LAW'];

    const getSubpillarKeysByPillar = () => {
        const map = new Map(pillarOrder.map(p => [p, []]));
        const groups = appState.pillarsGrouped || [];
        if (Array.isArray(groups) && groups.length) {
            groups.forEach(p => {
                const code = p.code;
                if (!map.has(code)) map.set(code, []);
                (p.sub_pillars || []).forEach(sp => {
                    map.get(code).push(`score|subpillar|${sp.id}`);
                });
            });
            return map;
        }
        pillarOrder.forEach(p => {
            for (let i = 1; i <= 4; i++) map.get(p).push(`score|subpillar|${p}-0${i}`);
        });
        return map;
    };

    const quickAddPillars = (axisKey) => {
        const target = axisKey === 'x' ? crossSectionState.xAxis : crossSectionState.yAxis;
        if (target.type !== 'scores') return;

        const existing = new Set(target.items);
        pillarOrder.forEach(p => {
            const key = `score|pillar|${p}`;
            if (!existing.has(key)) {
                target.items.push(key);
                existing.add(key);
            }
        });

        persistCrossSectionState();
        renderCrossSectionConfigUI();
        renderCrossSectionSheet();
    };

    const quickAddSubpillars = (axisKey) => {
        const target = axisKey === 'x' ? crossSectionState.xAxis : crossSectionState.yAxis;
        if (target.type !== 'scores') return;

        const subMap = getSubpillarKeysByPillar();
        const existing = new Set(target.items);

        const isSubpillarFor = (key, pillarCode) => {
            if (!String(key).startsWith('score|subpillar|')) return false;
            const id = String(key).split('|').slice(2).join('|');
            return String(id).startsWith(pillarCode);
        };

        const ensurePillarPresent = (pillarCode) => {
            const pKey = `score|pillar|${pillarCode}`;
            if (existing.has(pKey)) return;
            target.items.push(pKey);
            existing.add(pKey);
        };

        pillarOrder.forEach(p => {
            const subKeys = subMap.get(p) || [];
            if (!subKeys.length) return;

            // If pillars are present, insert sub-pillars directly after their pillar.
            // If not, add the pillar then insert.
            ensurePillarPresent(p);

            const pKey = `score|pillar|${p}`;
            const pIndex = target.items.indexOf(pKey);
            if (pIndex === -1) return;

            // Find insertion point: after the last contiguous sub-pillar for this pillar.
            let insertAt = pIndex + 1;
            while (insertAt < target.items.length && isSubpillarFor(target.items[insertAt], p)) {
                insertAt += 1;
            }

            const toInsert = subKeys.filter(k => !existing.has(k));
            if (toInsert.length) {
                target.items.splice(insertAt, 0, ...toInsert);
                toInsert.forEach(k => existing.add(k));
            }
        });

        persistCrossSectionState();
        renderCrossSectionConfigUI();
        renderCrossSectionSheet();
    };

    document.getElementById('cross-config-x-add-pillars')?.addEventListener('click', () => quickAddPillars('x'));
    document.getElementById('cross-config-y-add-pillars')?.addEventListener('click', () => quickAddPillars('y'));
    document.getElementById('cross-config-x-add-subpillars')?.addEventListener('click', () => quickAddSubpillars('x'));
    document.getElementById('cross-config-y-add-subpillars')?.addEventListener('click', () => quickAddSubpillars('y'));

    // Initialize modal control values
    if (metricSel) metricSel.value = crossSectionState.metric;
    if (xTypeSel) xTypeSel.value = crossSectionState.xAxis.type;
    if (yTypeSel) yTypeSel.value = crossSectionState.yAxis.type;
    ensureAxisTypesValid('x');

    // First render
    renderCrossSectionSheet();

    document.getElementById('cross-edit-filters')?.addEventListener('click', () => {
        // Jump to analysis view where filters are edited.
        const btn = document.querySelector('.nav-item[data-view="analysis"]');
        btn?.click();
    });

    document.getElementById('cross-export-csv')?.addEventListener('click', () => {
        exportCrossSectionCsv();
    });
}

function isCrossSectionViewActive() {
    const el = document.getElementById('cross-section-view');
    return !!el && el.classList.contains('active');
}

function getCrossSectionCohortOptions() {
    const options = [{ value: 'all', label: 'All vendors (current filtered set)' }];

    // Booleans
    options.push({ value: 'bool|is_startup|true', label: 'Startup = Yes' });
    options.push({ value: 'bool|is_startup|false', label: 'Startup = No' });
    options.push({ value: 'bool|is_ai_first|true', label: 'AI-First = Yes' });
    options.push({ value: 'bool|is_ai_first|false', label: 'AI-First = No' });

    // Regions/types/specs from full vendor list
    const regions = [...new Set(appState.vendors.map(v => v.region).filter(Boolean))].sort();
    regions.forEach(r => options.push({ value: `attr|region|${r}`, label: `Region contains ${r}` }));

    const types = [...new Set(appState.vendors.map(v => v.ir_focus_type).filter(Boolean))].sort();
    types.forEach(t => options.push({ value: `attr|ir_focus_type|${t}`, label: `IR Focus Type = ${t}` }));

    const specs = [...new Set(appState.vendors.map(v => v.specialization).filter(Boolean))].sort();
    specs.slice(0, 40).forEach(s => options.push({ value: `attr|specialization|${s}`, label: `Specialization = ${s}` }));

    const flags = [...new Set(appState.vendors.map(v => v.research_flag).filter(Boolean))].sort();
    flags.forEach(f => options.push({ value: `attr|research_flag|${f}`, label: `Research Flag = ${f}` }));

    return options;
}

function getCrossSectionScoreOptions() {
    const options = [];

    // Measures (do not depend on a pillar/sub-pillar)
    options.push({ value: 'score|measure|vendors_count', label: 'Measure: Vendors (count)' });
    options.push({ value: 'score|measure|vendors_percent', label: 'Measure: Vendors (% of total)' });

    // Pillars
    ['PLA', 'INV', 'REM', 'PMG', 'LAW'].forEach(code => {
        const label = appState.fieldMetadata?.[code]?.name ? `${code} - ${appState.fieldMetadata[code].name}` : code;
        options.push({ value: `score|pillar|${code}`, label: `Pillar: ${label}` });
    });

    // Sub-pillars
    const groups = appState.pillarsGrouped || [];
    if (Array.isArray(groups) && groups.length) {
        groups.forEach(p => (p.sub_pillars || []).forEach(sp => {
            options.push({ value: `score|subpillar|${sp.id}`, label: `Sub-pillar: ${sp.id} - ${sp.name}` });
        }));
    } else {
        ['PLA', 'INV', 'REM', 'PMG', 'LAW'].forEach(p => {
            for (let i = 1; i <= 4; i++) {
                const sid = `${p}-0${i}`;
                options.push({ value: `score|subpillar|${sid}`, label: `Sub-pillar: ${sid}` });
            }
        });
    }
    return options;
}

function scoreDefFromKey(key) {
    const parts = String(key || '').split('|');
    if (parts.length < 3) return { type: 'pillar', id: 'PLA', label: 'PLA' };
    const kind = parts[1];
    const id = parts.slice(2).join('|');
    if (kind === 'measure') {
        if (id === 'vendors_count') return { type: 'measure', id, label: 'Vendors (count)' };
        if (id === 'vendors_percent') return { type: 'measure', id, label: 'Vendors (% of total)' };
        return { type: 'measure', id, label: `Measure: ${id}` };
    }
    if (kind === 'pillar') {
        const code = id;
        const label = appState.fieldMetadata?.[code]?.name ? `${code} - ${appState.fieldMetadata[code].name}` : code;
        return { type: 'pillar', id: code, label };
    }
    if (kind === 'subpillar') {
        // Prefer metadata name if present
        const groups = appState.pillarsGrouped || [];
        for (const p of groups) {
            const sp = (p.sub_pillars || []).find(s => s.id === id);
            if (sp) return { type: 'subpillar', id, label: `${sp.id} - ${sp.name}` };
        }
        return { type: 'subpillar', id, label: id };
    }
    return { type: 'pillar', id: 'PLA', label: 'PLA' };
}

function normalizeAxisTypes() {
    // Ensure one cohorts and one scores.
    if (crossSectionState.xAxis.type === crossSectionState.yAxis.type) {
        crossSectionState.yAxis.type = (crossSectionState.xAxis.type === 'cohorts') ? 'scores' : 'cohorts';
    }
    if (!Array.isArray(crossSectionState.xAxis.items) || crossSectionState.xAxis.items.length === 0) {
        crossSectionState.xAxis.items = [crossSectionState.xAxis.type === 'cohorts' ? 'all' : 'score|pillar|PLA'];
    }
    if (!Array.isArray(crossSectionState.yAxis.items) || crossSectionState.yAxis.items.length === 0) {
        crossSectionState.yAxis.items = [crossSectionState.yAxis.type === 'cohorts' ? 'all' : 'score|pillar|PLA'];
    }
}

function renderCrossSectionConfigUI() {
    normalizeAxisTypes();

    const metricSummary = document.getElementById('cross-metric-summary');
    if (metricSummary) {
        metricSummary.textContent = crossSectionState.metric === 'avg'
            ? 'Average'
            : (crossSectionState.metric === 'count' ? 'Count' : '% of total');
    }

    const metricSel = document.getElementById('cross-config-metric');
    const xTypeSel = document.getElementById('cross-config-x-type');
    const yTypeSel = document.getElementById('cross-config-y-type');
    if (metricSel) metricSel.value = crossSectionState.metric;
    if (xTypeSel) xTypeSel.value = crossSectionState.xAxis.type;
    if (yTypeSel) yTypeSel.value = crossSectionState.yAxis.type;

    // disable invalid options
    if (xTypeSel) Array.from(xTypeSel.options).forEach(o => (o.disabled = (o.value === crossSectionState.yAxis.type)));
    if (yTypeSel) Array.from(yTypeSel.options).forEach(o => (o.disabled = (o.value === crossSectionState.xAxis.type)));

    const renderAxis = (axisKey) => {
        const axis = axisKey === 'x' ? crossSectionState.xAxis : crossSectionState.yAxis;
        const container = document.getElementById(axisKey === 'x' ? 'cross-config-x-items' : 'cross-config-y-items');
        if (!container) return;
        container.innerHTML = '';

        const options = axis.type === 'cohorts' ? getCrossSectionCohortOptions() : getCrossSectionScoreOptions();
        const addRow = (value, idx) => {
            const row = document.createElement('div');
            row.className = 'cross-axis-item';

            const sel = document.createElement('select');
            options.forEach(o => {
                const opt = document.createElement('option');
                opt.value = o.value;
                opt.textContent = o.label;
                sel.appendChild(opt);
            });
            // fallback selection if missing
            const wanted = value || (axis.type === 'cohorts' ? 'all' : 'score|pillar|PLA');
            sel.value = options.some(o => o.value === wanted) ? wanted : options[0]?.value;
            sel.addEventListener('change', (e) => {
                axis.items[idx] = e.target.value;
                persistCrossSectionState();
                renderCrossSectionSheet();
            });

            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'btn-secondary';
            removeBtn.textContent = 'Remove';
            removeBtn.addEventListener('click', () => {
                axis.items.splice(idx, 1);
                if (axis.items.length === 0) {
                    axis.items.push(axis.type === 'cohorts' ? 'all' : 'score|pillar|PLA');
                }
                persistCrossSectionState();
                renderCrossSectionConfigUI();
                renderCrossSectionSheet();
            });

            row.appendChild(sel);
            row.appendChild(removeBtn);
            container.appendChild(row);
        };

        axis.items.forEach((v, idx) => addRow(v, idx));

        // Enable/disable quick-add buttons based on axis type
        const pillsBtn = document.getElementById(axisKey === 'x' ? 'cross-config-x-add-pillars' : 'cross-config-y-add-pillars');
        const subsBtn = document.getElementById(axisKey === 'x' ? 'cross-config-x-add-subpillars' : 'cross-config-y-add-subpillars');
        if (pillsBtn) pillsBtn.style.display = axis.type === 'scores' ? '' : 'none';
        if (subsBtn) subsBtn.style.display = axis.type === 'scores' ? '' : 'none';
    };

    renderAxis('x');
    renderAxis('y');
}

function cohortPredicateFromKey(key) {
    if (!key || key === 'all') {
        return { label: 'All', predicate: () => true };
    }
    const parts = String(key).split('|');
    if (parts.length < 3) {
        return { label: String(key), predicate: () => true };
    }
    const kind = parts[0];
    const field = parts[1];
    const value = parts.slice(2).join('|');

    if (kind === 'bool') {
        const boolVal = value === 'true';
        return {
            label: `${field}=${boolVal ? 'Yes' : 'No'}`,
            predicate: (v) => !!v?.[field] === boolVal
        };
    }

    // Special handling: regions are often multi-valued strings (e.g., "Global; North America").
    // Use case-insensitive contains so cohorts like "Global" or "North America" work as expected.
    if (field === 'region') {
        const needle = String(value).toLowerCase();
        return {
            label: `region contains ${value}`,
            predicate: (v) => String(v?.region ?? '').toLowerCase().includes(needle)
        };
    }

    return {
        label: `${field}=${value}`,
        predicate: (v) => String(v?.[field] ?? '') === String(value)
    };
}

function filterByQueryBuilder(vendors) {
    let filtered = vendors;
    if (queryBuilderState.filters.length === 0) return filtered;

    return filtered.filter(vendor => {
        let result = true;
        for (let i = 0; i < queryBuilderState.filters.length; i++) {
            const filter = queryBuilderState.filters[i];

            let vendorValue;
            if (['PLA', 'INV', 'REM', 'PMG', 'LAW'].includes(filter.field)) {
                vendorValue = getEffectivePillarScores(vendor)?.[filter.field];
            } else if (filter.field === 'pillar') {
                vendorValue = getEffectivePillarScores(vendor)?.[filter.value] ? filter.value : null;
            } else if (/^(PLA|INV|REM|PMG|LAW)-0[1-4]$/.test(filter.field)) {
                const pillarCode = filter.field.substring(0, 3);
                vendorValue = getEffectiveGranularMapping(vendor)?.[pillarCode]?.[filter.field];
            } else {
                vendorValue = vendor[filter.field];
            }

            const filterValue = filter.value;
            let filterMatches = false;

            switch (filter.operator) {
                case 'equals':
                    filterMatches = String(vendorValue) === String(filterValue);
                    break;
                case 'does not equal':
                    filterMatches = String(vendorValue) !== String(filterValue);
                    break;
                case 'contains':
                    filterMatches = String(vendorValue).toLowerCase().includes(String(filterValue).toLowerCase());
                    break;
                case 'does not contain':
                    filterMatches = !String(vendorValue).toLowerCase().includes(String(filterValue).toLowerCase());
                    break;
                case '=':
                    filterMatches = Number(vendorValue) === Number(filterValue);
                    break;
                case '<':
                    filterMatches = Number(vendorValue) < Number(filterValue);
                    break;
                case '>':
                    filterMatches = Number(vendorValue) > Number(filterValue);
                    break;
                case '<=':
                    filterMatches = Number(vendorValue) <= Number(filterValue);
                    break;
                case '>=':
                    filterMatches = Number(vendorValue) >= Number(filterValue);
                    break;
                case '<>':
                    filterMatches = Number(vendorValue) !== Number(filterValue);
                    break;
                default:
                    filterMatches = true;
            }

            if (i === 0) {
                result = filterMatches;
            } else {
                const logicalOp = filter.logicalOperator;
                if (logicalOp === 'AND') {
                    result = result && filterMatches;
                } else if (logicalOp === 'OR') {
                    result = result || filterMatches;
                }
            }
        }
        return result;
    });
}

function getUnifiedFilteredVendorsForCrossSection() {
    // Start with vendor-page filters/search if present, then apply Analysis (query builder) filters.
    const hasVendorFilters = (Object.keys(appState.filters || {}).length > 0) || !!(appState.searchQuery);
    const base = hasVendorFilters ? (appState.filteredVendors || []) : (appState.vendors || []);
    return filterByQueryBuilder(base);
}

function buildCohortAxisDefs(vendors, items) {
    const keys = Array.isArray(items) ? items : [];
    const normalized = keys.length ? keys : ['all'];
    return normalized.map(k => {
        const { label, predicate } = cohortPredicateFromKey(k);
        return { key: k, label, predicate, vendors: vendors.filter(v => predicate(v)) };
    });
}

function buildScoreAxisDefs(items) {
    const keys = Array.isArray(items) ? items : [];
    const normalized = keys.length ? keys : ['score|pillar|PLA'];
    return normalized.map(scoreDefFromKey);
}

function computeAverageForRow(vendors, row) {
    let sum = 0;
    let n = 0;
    vendors.forEach(v => {
        let value;
        if (row.type === 'pillar') {
            value = getEffectivePillarScores(v)?.[row.id];
            if (value === undefined || value === null || value === '') {
                // fallback compute
                const computed = computePillarScoreFromGranular(v, row.id);
                value = computed;
            }
        } else {
            const pillar = row.id.substring(0, 3);
            value = getEffectiveGranularMapping(v)?.[pillar]?.[row.id];
        }
        const num = Number(value);
        if (Number.isFinite(num)) {
            sum += num;
            n += 1;
        }
    });
    if (n === 0) return { avg: null, n: 0 };
    return { avg: sum / n, n };
}

function computeCountForRow(vendors, row) {
    let n = 0;
    vendors.forEach(v => {
        let value;
        if (row.type === 'pillar') {
            value = getEffectivePillarScores(v)?.[row.id];
            if (value === undefined || value === null || value === '') {
                value = computePillarScoreFromGranular(v, row.id);
            }
        } else {
            const pillar = row.id.substring(0, 3);
            value = getEffectiveGranularMapping(v)?.[pillar]?.[row.id];
        }
        const num = Number(value);
        if (Number.isFinite(num)) n += 1;
    });
    return n;
}

function renderCrossSectionSheet() {
    const container = document.getElementById('cross-section-table');
    if (!container) return;

    const vendors = getUnifiedFilteredVendorsForCrossSection();
    const filtersSummary = document.getElementById('cross-filters-summary');
    if (filtersSummary) {
        const qbCount = queryBuilderState.filters.length;
        const vfCount = Object.keys(appState.filters || {}).length;
        const search = appState.searchQuery ? 'search' : '';
        const parts = [];
        if (vfCount) parts.push(`${vfCount} vendor filter(s)`);
        if (search) parts.push('search');
        if (qbCount) parts.push(`${qbCount} analysis filter(s)`);
        filtersSummary.textContent = parts.length ? `${parts.join(' + ')} • base vendors: ${vendors.length}` : `None • base vendors: ${vendors.length}`;
    }

    normalizeAxisTypes();
    const total = vendors.length;

    const xDefs = (crossSectionState.xAxis.type === 'cohorts')
        ? buildCohortAxisDefs(vendors, crossSectionState.xAxis.items)
        : buildScoreAxisDefs(crossSectionState.xAxis.items);
    const yDefs = (crossSectionState.yAxis.type === 'cohorts')
        ? buildCohortAxisDefs(vendors, crossSectionState.yAxis.items)
        : buildScoreAxisDefs(crossSectionState.yAxis.items);

    if (!vendors.length) {
        container.innerHTML = '<div class="cross-muted">No vendors match the active filters.</div>';
        return;
    }

    const cohortsOnColumns = (crossSectionState.xAxis.type === 'cohorts');
    const colDefs = xDefs;
    const rowDefs = yDefs;
    const metric = crossSectionState.metric;

    const headerCells = colDefs.map(d => {
        if (cohortsOnColumns) {
            return `<th>${escapeHtml(d.label)}</th>`;
        }
        return `<th>${escapeHtml(d.label)}</th>`;
    }).join('');

    const bodyRows = rowDefs.map(r => {
        const cells = colDefs.map(c => {
            // Exactly one axis is cohorts; other is scores.
            const cohort = cohortsOnColumns ? c : r;
            const score = cohortsOnColumns ? r : c;
            const cohortVendors = cohort.vendors;
            const cohortSize = cohortVendors.length;

            // Measures override the global metric
            if (score.type === 'measure') {
                if (score.id === 'vendors_count') {
                    return `<td><div class="cross-cell"><div class="avg">${cohortSize}</div></div></td>`;
                }
                if (score.id === 'vendors_percent') {
                    const pct = total ? ((cohortSize / total) * 100).toFixed(1) + '%' : '-';
                    return `<td><div class="cross-cell"><div class="avg">${escapeHtml(pct)}</div></div></td>`;
                }
                return `<td><div class="cross-cell"><div class="avg">-</div></div></td>`;
            }

            if (metric === 'avg') {
                const res = computeAverageForRow(cohortVendors, score);
                const primary = (res.avg === null) ? '-' : res.avg.toFixed(2);
                return `<td><div class="cross-cell"><div class="avg">${escapeHtml(primary)}</div></div></td>`;
            }
            if (metric === 'count') {
                const count = computeCountForRow(cohortVendors, score);
                return `<td><div class="cross-cell"><div class="avg">${count}</div></div></td>`;
            }
            if (metric === 'percent') {
                const count = computeCountForRow(cohortVendors, score);
                const pct = total ? ((count / total) * 100).toFixed(1) + '%' : '-';
                return `<td><div class="cross-cell"><div class="avg">${escapeHtml(pct)}</div></div></td>`;
            }

            return `<td><div class="cross-cell"><div class="avg">-</div></div></td>`;
        }).join('');

        return `<tr><td class="row-label">${escapeHtml(r.label)}</td>${cells}</tr>`;
    }).join('');

    const corner = cohortsOnColumns ? 'Score' : 'Cohort';
    container.innerHTML = `
        <table class="cross-table">
            <thead>
                <tr>
                    <th>${escapeHtml(corner)}</th>
                    ${headerCells}
                </tr>
            </thead>
            <tbody>
                ${bodyRows}
            </tbody>
        </table>
    `;
}

function exportCrossSectionCsv() {
    const vendors = getUnifiedFilteredVendorsForCrossSection();
    normalizeAxisTypes();
    const total = vendors.length;

    const colDefs = (crossSectionState.xAxis.type === 'cohorts')
        ? buildCohortAxisDefs(vendors, crossSectionState.xAxis.items)
        : buildScoreAxisDefs(crossSectionState.xAxis.items);
    const rowDefs = (crossSectionState.yAxis.type === 'cohorts')
        ? buildCohortAxisDefs(vendors, crossSectionState.yAxis.items)
        : buildScoreAxisDefs(crossSectionState.yAxis.items);

    const cohortsOnColumns = (crossSectionState.xAxis.type === 'cohorts');
    const metric = crossSectionState.metric;

    const lines = [];
    const corner = cohortsOnColumns ? 'Score' : 'Cohort';
    const header = [corner, ...colDefs.map(d => d.label)];
    lines.push(header.map(csvEscape).join(','));

    rowDefs.forEach(r => {
        const row = [r.label];
        colDefs.forEach(c => {
            const cohort = cohortsOnColumns ? c : r;
            const score = cohortsOnColumns ? r : c;
            const cohortVendors = cohort.vendors;
            const cohortSize = cohortVendors.length;

            if (score.type === 'measure') {
                if (score.id === 'vendors_count') {
                    row.push(String(cohortSize));
                } else if (score.id === 'vendors_percent') {
                    row.push(total ? ((cohortSize / total) * 100).toFixed(2) : '');
                } else {
                    row.push('');
                }
                return;
            }

            if (metric === 'avg') {
                const res = computeAverageForRow(cohortVendors, score);
                row.push(res.avg === null ? '' : res.avg.toFixed(4));
            } else if (metric === 'count') {
                row.push(String(computeCountForRow(cohortVendors, score)));
            } else if (metric === 'percent') {
                const count = computeCountForRow(cohortVendors, score);
                row.push(total ? ((count / total) * 100).toFixed(2) : '');
            } else {
                row.push('');
            }
        });
        lines.push(row.map(csvEscape).join(','));
    });

    const filename = `cross_section_${metric}_${(appState.currentVendorFile || 'dataset').replace(/[^a-zA-Z0-9_-]+/g, '_')}.csv`;
    downloadText(filename, lines.join('\n'), 'text/csv');
}

function csvEscape(v) {
    const s = String(v ?? '');
    if (/[",\n]/.test(s)) return '"' + s.replace(/"/g, '""') + '"';
    return s;
}

function setupVendorReportModal() {
    const modal = document.getElementById('vendor-details-modal');
    if (!modal) return;

    // Tab switching
    modal.querySelectorAll('.vendor-report-tab').forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            if (!tab) return;

            modal.querySelectorAll('.vendor-report-tab').forEach(t => {
                t.classList.toggle('active', t === btn);
                t.setAttribute('aria-selected', t === btn ? 'true' : 'false');
            });
            modal.querySelectorAll('.vendor-report-panel').forEach(p => {
                p.classList.toggle('active', p.dataset.panel === tab);
            });
        });
    });

    // Search within evidence/rationale
    const search = document.getElementById('vendor-report-search');
    if (search) {
        search.addEventListener('input', () => {
            const q = (search.value || '').trim().toLowerCase();
            const panel = document.getElementById('vendor-report-panel-evidence');
            if (!panel) return;
            panel.querySelectorAll('details.vendor-report-section').forEach(d => {
                const hay = (d.dataset.search || '').toLowerCase();
                d.style.display = !q || hay.includes(q) ? '' : 'none';
            });
        });
    }

    // Expand/collapse all
    const expandAll = document.getElementById('vendor-report-expand-all');
    const collapseAll = document.getElementById('vendor-report-collapse-all');
    if (expandAll) {
        expandAll.addEventListener('click', () => {
            const panel = document.getElementById('vendor-report-panel-evidence');
            if (!panel) return;
            panel.querySelectorAll('details.vendor-report-section').forEach(d => d.open = true);
        });
    }
    if (collapseAll) {
        collapseAll.addEventListener('click', () => {
            const panel = document.getElementById('vendor-report-panel-evidence');
            if (!panel) return;
            panel.querySelectorAll('details.vendor-report-section').forEach(d => d.open = false);
        });
    }

    // Copy/download
    const copyBtn = document.getElementById('vendor-report-copy-json');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            if (vendorReportState.vendorJson) copyToClipboard(vendorReportState.vendorJson);
        });
    }
    const dlBtn = document.getElementById('vendor-report-download-json');
    if (dlBtn) {
        dlBtn.addEventListener('click', () => {
            const v = vendorReportState.vendor;
            if (!v) return;
            const safeName = String(v.vendor || 'vendor').replace(/[^a-zA-Z0-9_-]+/g, '_');
            const filename = `${safeName}.json`;
            downloadText(filename, vendorReportState.vendorJson || JSON.stringify(v, null, 2));
        });
    }
}

function handleNavigation(e) {
    const view = e.currentTarget.dataset.view;
    
    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    e.currentTarget.classList.add('active');
    
    // Update active view
    document.querySelectorAll('.view-container').forEach(container => {
        container.classList.remove('active');
    });
    
    const viewElement = document.getElementById(`${view}-view`);
    if (viewElement) {
        viewElement.classList.add('active');
        appState.currentView = view;
        
        if (view === 'dashboard') {
            updateDashboard();
        } else if (view === 'analysis') {
            initializeAnalyticsTab();
        } else if (view === 'legend') {
            populateLegendView();
        } else if (view === 'cross-section') {
            refreshCrossSectionCohortDropdowns();
            renderCrossSectionSheet();
        }
    }
}

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
}

async function loadVendorFileSelector() {
    try {
        // ── Load schema selector first ──
        await loadSchemaFileSelector();

        const schemaParam = appState.currentSchemaFile ? `?schema=${encodeURIComponent(appState.currentSchemaFile)}` : '';
        const response = await fetch('/api/vendor-files' + schemaParam);
        const data = await response.json();
        
        const select = document.getElementById('vendor-file-select');
        select.innerHTML = '';
        
        // Populate dropdown with available files
        data.files.forEach(file => {
            const option = document.createElement('option');
            option.value = file.filename;
            option.textContent = `${file.name} (${file.count} vendors)`;
            select.appendChild(option);
        });
        
        // Set current selection
        select.value = data.current;
        appState.currentVendorFile = data.current;
        
        // Add apply button listener (idempotent)
        const applyBtn = document.getElementById('apply-vendor-file');
        if (applyBtn && !applyBtn.dataset.bound) {
            applyBtn.dataset.bound = 'true';
            applyBtn.addEventListener('click', switchVendorFile);
        }

        // Wire score mode selector
        const scoreSelect = document.getElementById('score-mode-select');
        if (scoreSelect && !scoreSelect.dataset.bound) {
            scoreSelect.dataset.bound = 'true';
            scoreSelect.addEventListener('change', (e) => setScoreMode(e.target.value));
        }
    } catch (error) {
    }
}

async function loadSchemaFileSelector() {
    try {
        const response = await fetch('/api/schema-files');
        const data = await response.json();

        const select = document.getElementById('schema-file-select');
        if (!select) return;
        select.innerHTML = '';

        // "All schemas" option
        const allOpt = document.createElement('option');
        allOpt.value = '';
        allOpt.textContent = 'All Schemas';
        select.appendChild(allOpt);

        data.schemas.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.filename;
            opt.textContent = s.name;
            select.appendChild(opt);
        });

        // Set current selection
        if (data.current) {
            select.value = data.current;
            appState.currentSchemaFile = data.current;
        }

        // Wire change handler (idempotent)
        if (!select.dataset.bound) {
            select.dataset.bound = 'true';
            select.addEventListener('change', async (e) => {
                await switchSchema(e.target.value);
            });
        }
    } catch (error) {
        console.error('Error loading schema files:', error);
    }
}

async function switchSchema(schemaFilename) {
    try {
        appState.currentSchemaFile = schemaFilename || '';

        // Tell backend which schema is active
        if (schemaFilename) {
            await fetch('/api/switch-schema', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: schemaFilename })
            });

            // Fetch schema detail for dynamic sub-pillar labels
            const detailResp = await fetch(`/api/schema-detail?schema=${encodeURIComponent(schemaFilename)}`);
            appState.schemaDetail = await detailResp.json();
        } else {
            appState.schemaDetail = null;
        }

        // Refresh vendor file dropdown (now filtered by schema)
        const schemaParam = schemaFilename ? `?schema=${encodeURIComponent(schemaFilename)}` : '';
        const response = await fetch('/api/vendor-files' + schemaParam);
        const data = await response.json();

        const select = document.getElementById('vendor-file-select');
        select.innerHTML = '';
        data.files.forEach(file => {
            const opt = document.createElement('option');
            opt.value = file.filename;
            opt.textContent = `${file.name} (${file.count} vendors)`;
            select.appendChild(opt);
        });

        // Auto-select the first file
        if (data.files.length > 0) {
            select.value = data.files[0].filename;
        }

        // Update sub-pillar labels in the sidebar if schema detail available
        updateSidebarSubPillarLabels();

        // Reload metadata
        try {
            const metadataResponse = await fetch('/api/metadata');
            const metadata = await metadataResponse.json();
            appState.fieldMetadata = metadata.field_metadata;
            appState.scoreLegend = metadata.score_legend;
            appState.pillarsGrouped = metadata.pillars_grouped || [];
            appState.schemaIntent = metadata.schema_intent || '';
            appState.currentSchemaFileName = metadata.schema_file || '';
        } catch (e) {}

        // Refresh the legend view if it's visible
        populateLegendView();
    } catch (error) {
        console.error('Error switching schema:', error);
    }
}

function updateSidebarSubPillarLabels() {
    const detail = appState.schemaDetail;
    if (!detail || !detail.sub_pillars) return;

    // Build lookup: ID → name
    const lookup = {};
    detail.sub_pillars.forEach(sp => { lookup[sp.id] = sp.name; });

    // Update sidebar buttons in analysis view
    document.querySelectorAll('.field-selector-btn.sub-pillar-btn').forEach(btn => {
        const field = btn.getAttribute('data-field');
        if (field && lookup[field]) {
            btn.textContent = lookup[field];
        }
    });
}

async function switchVendorFile() {
    try {
        const filename = document.getElementById('vendor-file-select').value;
        if (!filename) return;
        
        const response = await fetch('/api/switch-vendor-file', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename })
        });
        
        const result = await response.json();
        if (result.success) {
            appState.currentVendorFile = filename;

            // If backend auto-switched schema, update frontend state and UI
            if (result.schema_switched && result.current_schema) {
                const schemaSelect = document.getElementById('schema-file-select');
                if (schemaSelect && schemaSelect.value !== result.current_schema) {
                    schemaSelect.value = result.current_schema;
                    appState.currentSchemaFile = result.current_schema;

                    // Reload schema detail for sub-pillar labels
                    try {
                        const detailResp = await fetch(`/api/schema-detail?schema=${encodeURIComponent(result.current_schema)}`);
                        appState.schemaDetail = await detailResp.json();
                    } catch (e) {}

                    // Reload metadata (pillars, legend, intent)
                    try {
                        const metaResp = await fetch('/api/metadata');
                        const metadata = await metaResp.json();
                        appState.fieldMetadata = metadata.field_metadata;
                        appState.scoreLegend = metadata.score_legend;
                        appState.pillarsGrouped = metadata.pillars_grouped || [];
                        appState.schemaIntent = metadata.schema_intent || '';
                        appState.currentSchemaFileName = metadata.schema_file || '';
                    } catch (e) {}

                    // Refresh sub-pillar sidebar
                    await setupSubPillars();
                    updateSidebarSubPillarLabels();
                    populateLegendView();
                }
            }

            // Reload vendors and all dependent data
            await loadVendors();
            applyFilters();

            // Auto-switch score mode based on dataset name, unless user already chose one.
            const hasSaved = !!localStorage.getItem('scoreMode');
            if (!hasSaved) {
                if ((filename || '').toLowerCase().includes('researched')) {
                    setScoreMode('researched');
                } else if ((filename || '').toLowerCase().includes('validated')) {
                    setScoreMode('validated');
                }
            }
            
            // Immediately update analytics dashboard if visible
            if (document.querySelector('.analysis-content-wrapper') && 
                document.querySelector('.analysis-content-wrapper').style.display !== 'none') {
                updateAnalytics();
            }
        }
    } catch (error) {
    }
}

async function loadVendors() {
    try {
        const response = await fetch('/api/vendors');
        appState.vendors = await response.json();
        appState.filteredVendors = [...appState.vendors];

        // If user hasn't picked a mode yet, default based on file contents.
        const hasSaved = !!localStorage.getItem('scoreMode');
        if (!hasSaved) {
            const first = appState.vendors?.[0];
            if (first && first.pillar_scores_ai_researched) {
                setScoreMode('ai_researched');
            } else if (first && first.pillar_scores_researched) {
                setScoreMode('researched');
            } else {
                setScoreMode('validated');
            }
        }
        
        renderVendors();
        setupFilterPanel();
        updateVendorCount();
        initializeAnalyticsTab();
        populateComparisonRadarDropdowns();

        // Refresh cross-section cohort dropdowns (they include dynamic field values).
        refreshCrossSectionCohortDropdowns();
        if (isCrossSectionViewActive()) {
            renderCrossSectionSheet();
        }
    } catch (error) {
        document.querySelector('.vendor-count').textContent = 'Error loading vendors';
    }
}

async function setupFilterPanel() {
    try {
        // Load sub-pillars first (needed for table columns)
        await setupSubPillars();
        
        // Wait a tick to ensure DOM is ready
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Get dropdown elements
        const regionDropdown = document.getElementById('filter-region');
        const specDropdown = document.getElementById('filter-specialization');
        const irFocusDropdown = document.getElementById('filter-ir-focus');
        
        if (!regionDropdown || !specDropdown || !irFocusDropdown) {
            return;
        }
        
        // Test fetch with /api/vendors first
        // Get unique values for each filter field
        const regions = await fetch('/api/field-values/region').then(r => r.json()).catch(e => {
            return [];
        });
        const specs = await fetch('/api/field-values/specialization').then(r => r.json()).catch(e => {
            return [];
        });
        const irFocusTypes = await fetch('/api/field-values/ir_focus_type').then(r => r.json()).catch(e => {
            return [];
        });
        
        // Clear and populate Region dropdown
        regionDropdown.innerHTML = '<option value="">All</option>';
        regions.forEach(region => {
            const option = document.createElement('option');
            option.value = region;
            option.textContent = region;
            regionDropdown.appendChild(option);
        });
        
        // Populate Specialization dropdown
        specDropdown.innerHTML = '<option value="">All</option>';
        specs.forEach(spec => {
            const option = document.createElement('option');
            option.value = spec;
            option.textContent = spec;
            specDropdown.appendChild(option);
        });
        
        // Populate IR Focus Type dropdown
        irFocusDropdown.innerHTML = '<option value="">All</option>';
        irFocusTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type;
            irFocusDropdown.appendChild(option);
        });
        
        // Setup change event listeners for all dropdowns
        const startupDropdown = document.getElementById('filter-startup');
        const aiFirstDropdown = document.getElementById('filter-ai-first');
        
        regionDropdown.addEventListener('change', applyFilterDropdowns);
        specDropdown.addEventListener('change', applyFilterDropdowns);
        irFocusDropdown.addEventListener('change', applyFilterDropdowns);
        if (startupDropdown) startupDropdown.addEventListener('change', applyFilterDropdowns);
        if (aiFirstDropdown) aiFirstDropdown.addEventListener('change', applyFilterDropdowns);
        
    } catch (error) {
        // Silently fail
    }
}

function applyFilterDropdowns() {
    const region = document.getElementById('filter-region')?.value || '';
    const specialization = document.getElementById('filter-specialization')?.value || '';
    const irFocus = document.getElementById('filter-ir-focus')?.value || '';
    const startup = document.getElementById('filter-startup')?.value || '';
    const aiFirst = document.getElementById('filter-ai-first')?.value || '';
    
    // Clear all existing filters
    appState.filters = {};
    
    // Apply selected dropdown filters
    if (region) appState.filters['region'] = new Set([region]);
    if (specialization) appState.filters['specialization'] = new Set([specialization]);
    if (irFocus) appState.filters['ir_focus_type'] = new Set([irFocus]);
    
    if (startup === 'startup') appState.filters['is_startup'] = new Set(['true']);
    else if (startup === 'established') appState.filters['is_startup'] = new Set(['false']);
    
    if (aiFirst === 'yes') appState.filters['is_ai_first'] = new Set(['true']);
    else if (aiFirst === 'no') appState.filters['is_ai_first'] = new Set(['false']);
    
    applyFilters();
}

async function setupSubPillars() {
    try {
        const response = await fetch('/api/sub-pillars');
        const data = await response.json();
        appState.subPillars = data.all_sub_pillars;
        appState.pillarMetadata = {}; // Store pillar names
        
        // Store pillar names from API
        data.pillars.forEach(pillar => {
            appState.pillarMetadata[pillar.code] = pillar.name;
        });
        
        // Initialize columnVisibility for all sub-pillars - ALL SELECTED BY DEFAULT
        appState.subPillars.forEach(sub => {
            if (!appState.columnVisibility.hasOwnProperty(sub.id)) {
                appState.columnVisibility[sub.id] = true; // All selected by default
            }
        });
        
        // Initialize selectedSubPillars with all sub-pillar IDs
        appState.selectedSubPillars = appState.subPillars.map(sub => sub.id);
    } catch (error) {
    }
}

function populateColumnVisibilityModal() {
    const listContainer = document.getElementById('sub-pillars-visibility-list');
    listContainer.innerHTML = '';
    
    const pillarOrder = ['PLA', 'INV', 'REM', 'PMG', 'LAW'];
    
    pillarOrder.forEach(pillarCode => {
        const subPillarsForPillar = appState.subPillars.filter(s => s.id.startsWith(pillarCode));
        
        if (subPillarsForPillar.length > 0) {
            const pillarGroup = document.createElement('div');
            pillarGroup.className = 'column-pillar-group';
            const pillarName = appState.pillarMetadata[pillarCode] || pillarCode;
            pillarGroup.innerHTML = `<strong>${pillarName} (${pillarCode})</strong>`;
            
            subPillarsForPillar.forEach(sub => {
                const isInSelectedSubPillars = appState.selectedSubPillars.includes(sub.id);
                const label = document.createElement('label');
                label.innerHTML = `
                    <input type="checkbox" 
                           class="col-visibility-check" 
                           data-column="${sub.id}"
                           ${isInSelectedSubPillars ? 'checked' : ''}>
                    ${sub.id} - ${sub.name}
                `;
                pillarGroup.appendChild(label);
            });
            
            listContainer.appendChild(pillarGroup);
        }
    });
}

function handleSubPillarFilter(subPillarId, isChecked) {
    if (isChecked) {
        if (!appState.selectedSubPillars.includes(subPillarId)) {
            appState.selectedSubPillars.push(subPillarId);
        }
    } else {
        appState.selectedSubPillars = appState.selectedSubPillars.filter(id => id !== subPillarId);
    }
    renderVendors();
}

function addFilter(field, value) {
    if (!appState.filters[field]) {
        appState.filters[field] = new Set();
    }
    
    appState.filters[field].add(value);
    applyFilters();
}

function removeFilter(field, value) {
    if (appState.filters[field]) {
        appState.filters[field].delete(value);
        if (appState.filters[field].size === 0) {
            delete appState.filters[field];
        }
    }
    applyFilters();
}

function resetFilters() {
    appState.filters = {};
    appState.searchQuery = '';
    document.getElementById('search-input').value = '';
    applyFilters();
}

function handleSearch(e) {
    appState.searchQuery = e.target.value.toLowerCase();
    applyFilters();
}

function applyFilters() {
    appState.filteredVendors = appState.vendors.filter(vendor => {
        // Apply field filters
        for (const [field, values] of Object.entries(appState.filters)) {
            const vendorValue = String(vendor[field]).toLowerCase();
            if (!Array.from(values).some(v => vendorValue.includes(v.toLowerCase()))) {
                return false;
            }
        }
        
        // Apply search
        if (appState.searchQuery) {
            const searchableFields = [
                'vendor', 'region', 'specialization', 'ir_focus_type',
                'capability_analysis'
            ];
            const found = searchableFields.some(field => 
                String(vendor[field] || '').toLowerCase().includes(appState.searchQuery)
            );
            if (!found) return false;
        }
        
        return true;
    });
    
    renderVendors();
    updateVendorCount();

    // Keep Comparison Radar options aligned with current filter set
    populateComparisonRadarDropdowns();
    
    // Refresh analytics dashboard if visible
    if (document.querySelector('.analysis-content-wrapper').style.display !== 'none') {
        updateAnalytics();
    }

    // Keep cross-section sheet aligned with current filter set
    if (isCrossSectionViewActive()) {
        renderCrossSectionSheet();
    }
}

function refreshCrossSectionCohortDropdowns() {
    const root = document.getElementById('cross-section-view');
    if (!root) return;
    const selects = Array.from(document.querySelectorAll('.cross-cohort-select'));
    if (!selects.length) return;
    const opts = getCrossSectionCohortOptions();
    selects.forEach(sel => {
        const idx = Number(sel.dataset.index);
        const current = crossSectionState.cohorts[idx] || 'all';
        const prev = sel.value || current;
        sel.innerHTML = '';
        opts.forEach(o => {
            const opt = document.createElement('option');
            opt.value = o.value;
            opt.textContent = o.label;
            sel.appendChild(opt);
        });
        // preserve selection where possible
        sel.value = opts.some(o => o.value === prev) ? prev : current;
    });
}

function rebuildTableHeader() {
    const headerRow = document.querySelector('#header-row-1');
    
    // Remove existing sub-pillar headers
    headerRow.querySelectorAll('th.sub-pillar-header').forEach(h => h.remove());
    
    // Group sub-pillars by parent pillar
    const pillarGroups = {};
    appState.selectedSubPillars.forEach(subPillarId => {
        const pillarCode = subPillarId.split('-')[0];
        if (!pillarGroups[pillarCode]) {
            pillarGroups[pillarCode] = [];
        }
        pillarGroups[pillarCode].push(subPillarId);
    });
    
    // Find pillar headers and insert sub-pillar headers after each
    const pillarHeaders = Array.from(headerRow.querySelectorAll('th.pillar-column'));
    const pillarOrder = ['PLA', 'INV', 'REM', 'PMG', 'LAW'];
    
    pillarOrder.forEach((pillarCode, idx) => {
        const pillarHeader = pillarHeaders[idx];
        if (!pillarHeader) return;
        
        // Clear existing toggle button
        const existingToggle = pillarHeader.querySelector('.pillar-toggle');
        if (existingToggle) existingToggle.remove();
        
        // Add toggle button only if this pillar has sub-pillars selected
        if (pillarGroups[pillarCode] && pillarGroups[pillarCode].length > 0) {
            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'pillar-toggle';
            toggleBtn.textContent = appState.pillarVisibility[pillarCode] ? '▼' : '▶';
            toggleBtn.title = appState.pillarVisibility[pillarCode] ? 'Collapse' : 'Expand';
            toggleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                appState.pillarVisibility[pillarCode] = !appState.pillarVisibility[pillarCode];
                rebuildTableHeader();
                renderVendors();
            });
            pillarHeader.appendChild(toggleBtn);
            
            // Insert sub-pillar headers after this pillar (if visible)
            if (appState.pillarVisibility[pillarCode]) {
                let insertAfter = pillarHeader;
                pillarGroups[pillarCode].forEach(subPillarId => {
                    const subPillar = appState.subPillars.find(s => s.id === subPillarId);
                    if (subPillar) {
                        const th = document.createElement('th');
                        th.className = 'sub-pillar-header';
                        th.dataset.pillarGroup = pillarCode;
                        th.dataset.subPillarId = subPillarId;
                        th.title = subPillar.name;
                        th.textContent = subPillarId;
                        insertAfter.parentNode.insertBefore(th, insertAfter.nextSibling);
                        insertAfter = th;
                    }
                });
            }
        }
    });
}

function renderVendors() {
    const tbody = document.querySelector('#vendors-table tbody');
    tbody.innerHTML = '';
    
    if (appState.filteredVendors.length === 0) {
        tbody.innerHTML = '<tr><td colspan="11" style="text-align: center; padding: 24px;">No vendors found</td></tr>';
        return;
    }
    
    appState.filteredVendors.forEach((vendor, index) => {
        const row = document.createElement('tr');
        
        const pillarScores = ['PLA', 'INV', 'REM', 'PMG', 'LAW'];
        const effectivePillarScores = getEffectivePillarScores(vendor);
        const scoreValues = pillarScores.map(p => {
            return effectivePillarScores[p] ?? '-';
        });
        
        // Group sub-pillars by parent pillar
        const pillarGroups = {};
        appState.selectedSubPillars.forEach(subPillarId => {
            const pillarCode = subPillarId.split('-')[0];
            if (!pillarGroups[pillarCode]) {
                pillarGroups[pillarCode] = [];
            }
            pillarGroups[pillarCode].push(subPillarId);
        });
        
        // Build pillar and sub-pillar columns interleaved
        let pillarCols = '';
        const pillarOrder = ['PLA', 'INV', 'REM', 'PMG', 'LAW'];
        
        pillarOrder.forEach((pillarCode, idx) => {
            const score = scoreValues[idx];
            // Add parent pillar column
            pillarCols += `<td class="pillar-column" style="text-align: center;">${score !== '-' ? `<span class="pillar-score level-${Math.round(score)}">${score}</span>` : '<span>-</span>'}</td>`;
            
            // Add sub-pillar columns immediately after parent pillar (only if visible)
            if (pillarGroups[pillarCode] && appState.pillarVisibility[pillarCode]) {
                pillarGroups[pillarCode].forEach(subPillarId => {
                    const subScore = getEffectiveGranularMapping(vendor)?.[pillarCode]?.[subPillarId] || '-';
                    const displayScore = subScore !== '-' ? `<span class="pillar-score level-${Math.round(subScore)}">${subScore}</span>` : '<span>-</span>';
                    pillarCols += `<td class="sub-pillar-column" data-pillar-group="${pillarCode}"><div class="sub-score">${displayScore}</div></td>`;
                });
            }
        });
        
        row.innerHTML = `
            <td class="clickable-cell" data-vendor-name="${vendor.vendor}">${vendor.vendor}</td>
            <td class="clickable-cell" data-field="region" data-value="${vendor.region}">${vendor.region}</td>
            <td>${vendor.specialization || '-'}</td>
            <td class="clickable-cell" data-field="ir_focus_type" data-value="${vendor.ir_focus_type}">${vendor.ir_focus_type}</td>
            <td style="text-align: center;">
                <span class="bool-badge ${vendor.is_ai_first}">${vendor.is_ai_first ? 'Yes' : 'No'}</span>
            </td>
            <td style="text-align: center;">
                <span class="bool-badge ${vendor.is_startup}">${vendor.is_startup ? 'Yes' : 'No'}</span>
            </td>
            ${pillarCols}
        `;
        
        // Click handlers for vendor name
        row.querySelector('[data-vendor-name]').addEventListener('click', () => {
            showVendorDetails(vendor);
        });
        
        // Click handlers for filter fields
        row.querySelectorAll('[data-field]').forEach(cell => {
            cell.addEventListener('click', (e) => {
                const field = e.currentTarget.dataset.field;
                const value = e.currentTarget.dataset.value;
                if (value) {
                    addFilter(field, value);
                }
            });
        });
        
        tbody.appendChild(row);
    });
    
    // Rebuild table header to include sub-pillar columns
    rebuildTableHeader();
}

function updateVendorCount() {
    const count = appState.filteredVendors.length;
    const total = appState.vendors.length;
    document.querySelector('.vendor-count').textContent = 
        `${count} of ${total} vendors`;
}

function showFieldInfo(field) {
    const metadata = appState.fieldMetadata[field];
    if (!metadata) return;
    
    const modal = document.getElementById('field-info-modal');
    document.getElementById('modal-title').textContent = metadata.name;
    document.getElementById('modal-description').textContent = metadata.description;
    
    // Get unique values for this field
    const values = new Set();
    appState.vendors.forEach(vendor => {
        if (vendor[field] !== undefined) {
            values.add(String(vendor[field]));
        }
    });
    
    const valuesHtml = Array.from(values)
        .sort()
        .slice(0, 10)
        .map(v => `<span class="modal-value" data-field="${field}" data-value="${v}">${v}</span>`)
        .join('');
    
    document.getElementById('modal-values').innerHTML = valuesHtml;
    
    // Add click handlers to modal values
    document.querySelectorAll('.modal-value').forEach(tag => {
        tag.addEventListener('click', () => {
            const field = tag.dataset.field;
            const value = tag.dataset.value;
            addFilter(field, value);
            modal.classList.remove('show');
        });
    });
    
    modal.classList.add('show');
}

function showVendorDetails(vendor) {
    const modal = document.getElementById('vendor-details-modal');
    if (!modal) return;

    vendorReportState.vendor = vendor;
    try {
        vendorReportState.vendorJson = JSON.stringify(vendor, null, 2);
    } catch {
        vendorReportState.vendorJson = '';
    }

    // Reset tabs/search
    const search = document.getElementById('vendor-report-search');
    if (search) search.value = '';
    modal.querySelectorAll('.vendor-report-tab').forEach(t => {
        const isSummary = t.dataset.tab === 'summary';
        t.classList.toggle('active', isSummary);
        t.setAttribute('aria-selected', isSummary ? 'true' : 'false');
    });
    modal.querySelectorAll('.vendor-report-panel').forEach(p => {
        p.classList.toggle('active', p.dataset.panel === 'summary');
    });

    const titleEl = document.getElementById('vendor-report-title');
    const subtitleEl = document.getElementById('vendor-report-subtitle');
    if (titleEl) titleEl.textContent = vendor.vendor || 'Vendor Report';
    if (subtitleEl) {
        const mode = appState.scoreMode || 'validated';
        subtitleEl.textContent = `Score mode: ${mode}. Dataset: ${appState.currentVendorFile || 'unknown'}.`;
    }

    renderVendorReportPanels(vendor);
    modal.classList.add('show');
}

function renderVendorReportPanels(vendor) {
    const summary = document.getElementById('vendor-report-panel-summary');
    const scoresPanel = document.getElementById('vendor-report-panel-scores');
    const evidence = document.getElementById('vendor-report-panel-evidence');
    const raw = document.getElementById('vendor-report-panel-raw');
    if (!summary || !scoresPanel || !evidence || !raw) return;

    const pillarScores = getEffectivePillarScores(vendor) || {};
    const pillars = ['PLA', 'INV', 'REM', 'PMG', 'LAW'];
    const granular = getEffectiveGranularMapping(vendor) || {};

    const researchFlag = vendor.research_flag ? String(vendor.research_flag) : 'unknown';
    const researchConfidence = vendor.research_confidence !== undefined ? formatMaybeNumber(vendor.research_confidence, 2) : 'unknown';

    // Summary tab
    const analysisSource = vendor.capability_analysis_source ? String(vendor.capability_analysis_source) : '';
    const analysisSourceSafe = /^https?:\/\//i.test(analysisSource) ? analysisSource : '';
    const overviewHtml = `
        <div class="vendor-report-grid">
            <div class="vendor-report-card">
                <h3>Capability Analysis</h3>
                <div class="vendor-report-text">${escapeHtml(vendor.capability_analysis || 'No analysis available')}</div>
                ${analysisSourceSafe ? `<div class="vendor-report-sources"><strong>Source:</strong> <a href="${escapeHtml(analysisSourceSafe)}" target="_blank" rel="noopener noreferrer">${escapeHtml(analysisSourceSafe)}</a></div>` : ''}
            </div>
            <div class="vendor-report-card">
                <h3>Overview</h3>
                <div class="vendor-report-overview-list">
                    <div class="vendor-report-overview-item">
                        <div class="k">Region</div>
                        <div class="v">${escapeHtml(vendor.region || '-')}</div>
                    </div>
                    <div class="vendor-report-overview-item">
                        <div class="k">Specialization</div>
                        <div class="v">${escapeHtml(vendor.specialization || '-')}</div>
                    </div>
                    <div class="vendor-report-overview-item">
                        <div class="k">IR Focus Type</div>
                        <div class="v">${escapeHtml(vendor.ir_focus_type || '-')}</div>
                    </div>
                    <div class="vendor-report-overview-item">
                        <div class="k">AI-First</div>
                        <div class="v">${vendor.is_ai_first ? 'Yes' : 'No'}</div>
                    </div>
                    <div class="vendor-report-overview-item">
                        <div class="k">Startup</div>
                        <div class="v">${vendor.is_startup ? 'Yes' : 'No'}</div>
                    </div>
                    <div class="vendor-report-overview-item">
                        <div class="k">Research Flag</div>
                        <div class="v">${escapeHtml(researchFlag)}</div>
                    </div>
                    <div class="vendor-report-overview-item">
                        <div class="k">Research Confidence</div>
                        <div class="v">${escapeHtml(researchConfidence)}</div>
                    </div>
                </div>
            </div>
        </div>
        <details class="vendor-report-section" style="margin-top: 12px;">
            <summary><span><strong>All Fields</strong> (high-level)</span><span class="sub-score">Show</span></summary>
            <div class="vendor-report-section-body">
                ${renderVendorFieldTable(vendor)}
            </div>
        </details>
    `;
    summary.innerHTML = overviewHtml;

    // Scores tab
    const scoreTiles = `
        <div class="vendor-report-score-grid">
            ${pillars.map(p => {
                const score = pillarScores[p];
                const display = score === undefined ? '-' : (Number.isFinite(Number(score)) ? Number(score).toFixed(2) : String(score));
                const meta = appState.fieldMetadata?.[p];
                const label = meta?.name || p;
                return `
                    <div class="vendor-report-score-tile">
                        <div class="score">${escapeHtml(display)}</div>
                        <div class="label">${escapeHtml(label)} (${p})</div>
                    </div>
                `;
            }).join('')}
        </div>
    `;

    const subpillarTable = renderSubPillarScoreTable(vendor, granular);
    scoresPanel.innerHTML = `
        <div class="vendor-report-card">
            <h3>Pillar Scores (${escapeHtml(appState.scoreMode || 'validated')})</h3>
            ${scoreTiles}
        </div>
        <div class="vendor-report-card" style="margin-top: 12px;">
            <h3>Sub-Pillar Scores (${escapeHtml(appState.scoreMode || 'validated')})</h3>
            ${subpillarTable}
        </div>
    `;

    // Evidence & Rationale tab
    evidence.innerHTML = renderEvidenceAndRationale(vendor, granular);

    // Raw tab
    raw.innerHTML = `
        <div class="vendor-report-card">
            <h3>Raw Vendor JSON</h3>
            <div class="vendor-report-code">${escapeHtml(vendorReportState.vendorJson || JSON.stringify(vendor, null, 2))}</div>
        </div>
    `;
}

function renderVendorFieldTable(vendor) {
    const omit = new Set(['sub_pillar_rationale_researched', 'sub_pillar_evidence']);
    const keys = Object.keys(vendor || {}).filter(k => !omit.has(k)).sort();
    const rows = keys.map(k => {
        const v = vendor[k];
        let display;
        if (v === null || v === undefined) {
            display = '-';
        } else if (typeof v === 'string') {
            display = v.length > 400 ? (v.slice(0, 400) + '…') : v;
        } else if (typeof v === 'number' || typeof v === 'boolean') {
            display = String(v);
        } else if (Array.isArray(v)) {
            display = `[array] length=${v.length}`;
        } else if (typeof v === 'object') {
            const ks = Object.keys(v);
            display = `[object] keys=${ks.length}`;
        } else {
            display = String(v);
        }
        return `<tr><td style="padding:6px 8px; border-bottom:1px solid var(--border-color); color: var(--text-secondary); width: 220px;">${escapeHtml(k)}</td><td style="padding:6px 8px; border-bottom:1px solid var(--border-color);">${escapeHtml(display)}</td></tr>`;
    }).join('');

    return `
        <div style="overflow:auto; border:1px solid var(--border-color); border-radius:8px; background: var(--bg-primary);">
            <table style="width:100%; border-collapse: collapse; font-size: 12px;">
                <tbody>${rows || ''}</tbody>
            </table>
        </div>
    `;
}

function renderSubPillarScoreTable(vendor, granular) {
    const groups = appState.pillarsGrouped || [];
    const rows = [];

    // Build order from schema metadata if available
    if (Array.isArray(groups) && groups.length > 0) {
        groups.forEach(p => {
            (p.sub_pillars || []).forEach(sp => {
                const sid = sp.id;
                const pillarCode = sid?.split('-')?.[0];
                const score = granular?.[pillarCode]?.[sid];
                const display = score === undefined ? '-' : (Number.isFinite(Number(score)) ? Number(score).toFixed(2) : String(score));
                rows.push(`<tr>
                    <td style="padding:6px 8px; border-bottom:1px solid var(--border-color); width:110px;"><strong>${escapeHtml(sid)}</strong></td>
                    <td style="padding:6px 8px; border-bottom:1px solid var(--border-color);">${escapeHtml(sp.name || '')}</td>
                    <td style="padding:6px 8px; border-bottom:1px solid var(--border-color); width:110px; text-align:right;">${escapeHtml(display)}</td>
                </tr>`);
            });
        });
    } else {
        // Fallback: infer from mapping
        Object.entries(granular || {}).forEach(([pillar, scores]) => {
            Object.entries(scores || {}).forEach(([sid, score]) => {
                const display = score === undefined ? '-' : (Number.isFinite(Number(score)) ? Number(score).toFixed(2) : String(score));
                rows.push(`<tr>
                    <td style="padding:6px 8px; border-bottom:1px solid var(--border-color); width:110px;"><strong>${escapeHtml(sid)}</strong></td>
                    <td style="padding:6px 8px; border-bottom:1px solid var(--border-color);">${escapeHtml('')}</td>
                    <td style="padding:6px 8px; border-bottom:1px solid var(--border-color); width:110px; text-align:right;">${escapeHtml(display)}</td>
                </tr>`);
            });
        });
    }

    return `
        <div style="overflow:auto; border:1px solid var(--border-color); border-radius:8px; background: var(--bg-primary);">
            <table style="width:100%; border-collapse: collapse; font-size: 13px;">
                <thead>
                    <tr>
                        <th style="text-align:left; padding:8px; border-bottom:1px solid var(--border-color);">ID</th>
                        <th style="text-align:left; padding:8px; border-bottom:1px solid var(--border-color);">Sub-pillar</th>
                        <th style="text-align:right; padding:8px; border-bottom:1px solid var(--border-color);">Score</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows.join('')}
                </tbody>
            </table>
        </div>
    `;
}

function renderEvidenceAndRationale(vendor, granular) {
    const groups = appState.pillarsGrouped || [];
    const rationale = vendor.sub_pillar_rationale_researched && typeof vendor.sub_pillar_rationale_researched === 'object'
        ? vendor.sub_pillar_rationale_researched
        : {};

    const evidenceAll = vendor.sub_pillar_evidence && typeof vendor.sub_pillar_evidence === 'object'
        ? vendor.sub_pillar_evidence
        : {};

    const flag = vendor.research_flag ? String(vendor.research_flag) : 'unknown';

    const header = `
        <div class="vendor-report-card" style="margin-bottom: 12px;">
            <h3>Evidence & Rationale</h3>
            <div class="vendor-report-text">This section shows the most detailed researched justification available for each sub-pillar, including excerpts and source URLs when present.</div>
            ${flag !== 'good_evidence' ? `<div class="vendor-report-sources"><strong>Guardrail:</strong> When not flagged as good_evidence, sub-pillar scores should not exceed 3.0 without stronger public proof.</div>` : ''}
        </div>
    `;

    const sections = [];
    const addSection = (sid, name, definition) => {
        const pillarCode = sid?.split('-')?.[0];
        const score = granular?.[pillarCode]?.[sid];
        const displayScore = score === undefined ? '-' : (Number.isFinite(Number(score)) ? Number(score).toFixed(2) : String(score));

        const r = typeof rationale[sid] === 'string' ? rationale[sid].trim() : '';
        const ev = evidenceAll[sid];
        const urls = (ev && typeof ev === 'object' && Array.isArray(ev.source_urls)) ? ev.source_urls : [];
        const excerpts = (ev && typeof ev === 'object' && Array.isArray(ev.excerpts)) ? ev.excerpts : [];

        const excerptLines = [];
        excerpts.slice(0, 6).forEach((it, idx) => {
            if (typeof it === 'string') {
                excerptLines.push(`<div style="margin-bottom:8px;"><strong>Excerpt ${idx + 1}:</strong> ${escapeHtml(it)}</div>`);
            } else if (it && typeof it === 'object') {
                const txt = it.excerpt || it.text || '';
                const u = it.url || '';
                const terms = Array.isArray(it.matched_terms) ? it.matched_terms.filter(Boolean).slice(0, 8) : [];
                excerptLines.push(`
                    <div style="margin-bottom:10px;">
                        <div><strong>Excerpt ${idx + 1}:</strong> ${escapeHtml(String(txt || ''))}</div>
                        ${u ? `<div class="vendor-report-sources">URL: ${escapeHtml(u)}</div>` : ''}
                        ${terms.length ? `<div class="vendor-report-sources">Matched: ${escapeHtml(terms.join(', '))}</div>` : ''}
                    </div>
                `);
            }
        });

        const urlsHtml = urls && urls.length
            ? `<div class="vendor-report-sources"><strong>Sources:</strong> ${escapeHtml(urls.slice(0, 8).join(' | '))}</div>`
            : `<div class="vendor-report-sources"><strong>Sources:</strong> none captured</div>`;

        const rationaleHtml = r
            ? `<div class="vendor-report-text">${escapeHtml(r)}</div>`
            : `<div class="vendor-report-text">No researched sub-pillar rationale text is present for this item in the current dataset.</div>`;

        const defHtml = definition ? `<div class="vendor-report-sources"><strong>Definition:</strong> ${escapeHtml(definition)}</div>` : '';

        const searchBlob = `${sid} ${name || ''} ${definition || ''} ${r || ''} ${urls.join(' ')} ${excerpts.map(e => typeof e === 'string' ? e : (e?.excerpt || e?.text || '')).join(' ')}`;

        sections.push(`
            <details class="vendor-report-section" data-search="${escapeHtml(searchBlob)}">
                <summary>
                    <span><span class="sub-id">${escapeHtml(sid)}</span><span class="sub-name">${escapeHtml(name || '')}</span></span>
                    <span class="sub-score">${escapeHtml(displayScore)}</span>
                </summary>
                <div class="vendor-report-section-body">
                    ${defHtml}
                    <div style="margin-top: 10px;">
                        <h4 style="margin:0 0 6px 0; font-size: 13px;">Rationale</h4>
                        ${rationaleHtml}
                    </div>
                    <div style="margin-top: 10px;">
                        <h4 style="margin:0 0 6px 0; font-size: 13px;">Evidence (excerpts)</h4>
                        ${excerptLines.length ? excerptLines.join('') : '<div class="vendor-report-text">No sub-pillar excerpts captured.</div>'}
                        ${urlsHtml}
                    </div>
                </div>
            </details>
        `);
    };

    if (Array.isArray(groups) && groups.length) {
        groups.forEach(p => {
            (p.sub_pillars || []).forEach(sp => addSection(sp.id, sp.name, sp.definition));
        });
    } else {
        // Fallback: derive from granular
        Object.entries(granular || {}).forEach(([pillar, scores]) => {
            Object.keys(scores || {}).sort().forEach(sid => addSection(sid, sid, ''));
        });
    }

    return header + sections.join('');
}

function populateLegendView() {
    // ── Schema intent banner ──
    const legendContainer = document.querySelector('.legend-container');
    let existingBanner = document.getElementById('schema-intent-banner');
    if (existingBanner) existingBanner.remove();

    if (appState.schemaIntent) {
        const banner = document.createElement('div');
        banner.id = 'schema-intent-banner';
        banner.style.cssText = 'background: var(--bg-secondary); border-left: 4px solid var(--color-primary); padding: 12px 16px; margin-bottom: 20px; border-radius: 4px; font-size: 13px; color: var(--text-primary); line-height: 1.5;';
        banner.innerHTML = `<strong style="color: var(--color-primary);">Schema: ${appState.currentSchemaFileName || ''}</strong><br>${appState.schemaIntent}`;
        const firstH2 = legendContainer.querySelector('h2');
        if (firstH2) legendContainer.insertBefore(banner, firstH2);
    }

    // ── Scoring legend with full text from schema ──
    const legendGrid = document.querySelector('.legend-grid');
    const escapeAttr = (str) => String(str || '').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;');

    legendGrid.innerHTML = Object.entries(appState.scoreLegend).map(([score, description]) => {
        // Parse label and body: "Label: Body" or just "Body"
        const colonIdx = description.indexOf(':');
        const label = colonIdx > 0 ? description.substring(0, colonIdx).trim() : '';
        const body = colonIdx > 0 ? description.substring(colonIdx + 1).trim() : description;

        return `
        <div class="legend-item clickable-legend-score" data-score="${score}" data-description="${escapeAttr(description)}" style="cursor: pointer;">
            <div class="legend-item-header">
                <div class="legend-score">${score}</div>
                <div style="flex: 1;"><strong style="font-size: 13px;">${label}</strong></div>
                <button class="edit-btn edit-score" data-score="${score}" data-description="${escapeAttr(description)}" title="Edit">✏️</button>
            </div>
            <div class="legend-description">${body}</div>
        </div>
    `;
    }).join('');

    // Click handlers for score legend tiles (read-only popup)
    document.querySelectorAll('.clickable-legend-score').forEach(el => {
        el.addEventListener('click', (e) => {
            if (e.target.closest('.edit-btn')) return;
            const score = el.dataset.score;
            const desc = el.dataset.description;
            showScoreDetailsModal(score, desc);
        });
    });

    // Click handlers for edit score buttons
    document.querySelectorAll('.edit-score').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const score = btn.dataset.score;
            const description = btn.dataset.description;
            openEditModal('score', score, `Score ${score}`, description);
        });
    });

    // ── Pillars and sub-pillars with enriched schema data ──
    const pillarsGrid = document.querySelector('.pillars-grid');
    if (appState.pillarsGrouped && appState.pillarsGrouped.length > 0) {
        pillarsGrid.innerHTML = appState.pillarsGrouped.map(pillar => {
            return `
            <div class="pillar-section">
                <div class="pillar-header clickable-pillar" data-pillar-code="${pillar.code}" style="cursor: pointer;">
                    <div class="header-with-edit">
                        <h3>${pillar.code} - ${pillar.name}</h3>
                        <button class="edit-btn edit-pillar" data-pillar-code="${pillar.code}" data-pillar-name="${escapeAttr(pillar.name)}" data-pillar-desc="${escapeAttr(pillar.description || '')}" title="Edit">✏️</button>
                    </div>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px; line-height: 1.4;">${pillar.description || ''}</div>
                </div>
                <div class="sub-pillars-grid">
                    ${pillar.sub_pillars.map(sp => {
                        return `
                        <div class="sub-pillar-tile clickable-sub-pillar" data-sub-pillar-id="${sp.id}" style="cursor: pointer;">
                            <div class="tile-with-edit">
                                <div style="flex: 1;">
                                    <div class="sub-pillar-id">${sp.id}</div>
                                    <div class="sub-pillar-name">${sp.name}</div>
                                    <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px; line-height: 1.3;">${sp.definition ? (sp.definition.length > 120 ? sp.definition.substring(0, 117) + '...' : sp.definition) : ''}</div>
                                </div>
                                <button class="edit-btn edit-sub-pillar" data-sub-pillar-id="${sp.id}" data-sub-pillar-name="${escapeAttr(sp.name)}" data-sub-pillar-def="${escapeAttr(sp.definition || '')}" title="Edit">✏️</button>
                            </div>
                        </div>
                    `;
                    }).join('')}
                </div>
            </div>
        `;
        }).join('');

        // Click handlers for pillars (read-only detail popup)
        document.querySelectorAll('.clickable-pillar').forEach(el => {
            el.addEventListener('click', (e) => {
                if (e.target.closest('.edit-btn')) return;
                const code = el.dataset.pillarCode;
                const pillarObj = appState.pillarsGrouped.find(p => p.code === code);
                if (pillarObj) showPillarDetailsModal(pillarObj);
            });
        });

        // Click handlers for sub-pillars (read-only detail popup)
        document.querySelectorAll('.clickable-sub-pillar').forEach(el => {
            el.addEventListener('click', (e) => {
                if (e.target.closest('.edit-btn')) return;
                const id = el.dataset.subPillarId;
                // Find sub-pillar object from pillarsGrouped
                let spObj = null;
                for (const p of appState.pillarsGrouped) {
                    spObj = p.sub_pillars.find(sp => sp.id === id);
                    if (spObj) { spObj._pillarCode = p.code; spObj._pillarName = p.name; break; }
                }
                if (spObj) showSubPillarDetailsModal(spObj);
            });
        });

        // Click handlers for edit buttons
        document.querySelectorAll('.edit-pillar').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                openEditModal('pillar', btn.dataset.pillarCode, btn.dataset.pillarName, btn.dataset.pillarDesc);
            });
        });

        document.querySelectorAll('.edit-sub-pillar').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                openEditModal('sub-pillar', btn.dataset.subPillarId, btn.dataset.subPillarName, btn.dataset.subPillarDef);
            });
        });
    }

    // ── Field descriptions ──
    const fieldDescriptions = document.querySelector('.field-descriptions');
    const baseFields = ['vendor', 'region', 'specialization', 'ir_focus_type', 'is_ai_first', 'is_startup'];
    const pillarFields = ['PLA', 'INV', 'REM', 'PMG', 'LAW'];

    let html = '';

    html += '<div class="field-desc-section"><h3>Base Fields</h3>';
    baseFields.forEach(field => {
        if (appState.fieldMetadata[field]) {
            const meta = appState.fieldMetadata[field];
            html += `
                <div class="field-desc-item">
                    <div class="field-desc-header">
                        <div class="field-desc-title">${meta.name}</div>
                        <button class="edit-btn edit-field" data-field-id="${field}" data-field-name="${meta.name}" data-field-desc="${meta.description}" title="Edit">✏️</button>
                    </div>
                    <div class="field-desc-text">${meta.description}</div>
                </div>
            `;
        }
    });
    html += '</div>';

    html += '<div class="field-desc-section"><h3>Pillars</h3>';
    pillarFields.forEach(field => {
        if (appState.fieldMetadata[field]) {
            const meta = appState.fieldMetadata[field];
            html += `
                <div class="field-desc-item">
                    <div class="field-desc-header">
                        <div class="field-desc-title">${meta.name}</div>
                        <button class="edit-btn edit-field" data-field-id="${field}" data-field-name="${meta.name}" data-field-desc="${meta.description}" title="Edit">✏️</button>
                    </div>
                    <div class="field-desc-text">${meta.description}</div>
                </div>
            `;
        }
    });
    html += '</div>';

    fieldDescriptions.innerHTML = html;

    document.querySelectorAll('.edit-field').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            openEditModal('field', btn.dataset.fieldId, btn.dataset.fieldName, btn.dataset.fieldDesc);
        });
    });
}

// ── Read-only detail modals ──

function showScoreDetailsModal(score, description) {
    const modal = document.getElementById('pillar-details-modal');
    const title = document.getElementById('pillar-modal-title');
    const body = document.getElementById('pillar-modal-body');

    title.textContent = `Score ${score}`;
    body.innerHTML = `
        <div style="padding: 8px 0;">
            <div style="font-size: 36px; font-weight: bold; color: var(--color-primary); margin-bottom: 12px;">${score}</div>
            <p style="font-size: 14px; line-height: 1.6; color: var(--text-primary);">${description}</p>
            <div style="margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--border-color); font-size: 12px; color: var(--text-secondary);">
                Schema: ${appState.currentSchemaFileName || 'Default'}
            </div>
        </div>
    `;
    modal.classList.add('show');
}

function showPillarDetailsModal(pillarObj) {
    const modal = document.getElementById('pillar-details-modal');
    const title = document.getElementById('pillar-modal-title');
    const body = document.getElementById('pillar-modal-body');

    title.textContent = `${pillarObj.code} - ${pillarObj.name}`;

    let html = '<div style="padding: 8px 0;">';

    // Focus / Description
    if (pillarObj.description) {
        html += `
            <div style="margin-bottom: 16px;">
                <h4 style="margin: 0 0 6px 0; color: var(--color-primary); font-size: 13px;">Focus</h4>
                <p style="font-size: 13px; line-height: 1.6; color: var(--text-primary); margin: 0;">${pillarObj.description}</p>
            </div>
        `;
    }

    // Score rule
    if (pillarObj.validated_pillar_score_rule) {
        html += `
            <div style="margin-bottom: 16px;">
                <h4 style="margin: 0 0 6px 0; color: var(--color-primary); font-size: 13px;">Score Rule</h4>
                <p style="font-size: 12px; color: var(--text-secondary); margin: 0;">${pillarObj.validated_pillar_score_rule}</p>
            </div>
        `;
    }

    // AI Evidence Signals
    const signals = pillarObj.ai_evidence_signals || [];
    if (signals.length > 0) {
        html += `
            <div style="margin-bottom: 16px;">
                <h4 style="margin: 0 0 8px 0; color: var(--color-primary); font-size: 13px;">AI Evidence Signals</h4>
                <ul style="margin: 0; padding-left: 20px;">
                    ${signals.map(s => `<li style="font-size: 12px; color: var(--text-primary); margin-bottom: 6px; line-height: 1.4;">${s}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    // Sub-pillars list
    const subs = pillarObj.sub_pillars || [];
    if (subs.length > 0) {
        html += `
            <div style="margin-bottom: 8px;">
                <h4 style="margin: 0 0 8px 0; color: var(--color-primary); font-size: 13px;">Sub-Pillars</h4>
                ${subs.map(sp => `
                    <div style="padding: 8px 12px; margin-bottom: 6px; background: var(--bg-secondary); border-radius: 4px; border-left: 3px solid var(--color-primary);">
                        <div style="font-weight: 600; font-size: 12px;">${sp.id} - ${sp.name}</div>
                        <div style="font-size: 11px; color: var(--text-secondary); margin-top: 2px;">${sp.definition || ''}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    html += `
        <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border-color); font-size: 11px; color: var(--text-secondary);">
            Schema: ${appState.currentSchemaFileName || 'Default'}
        </div>
    `;
    html += '</div>';

    body.innerHTML = html;
    modal.classList.add('show');
}

function showSubPillarDetailsModal(spObj) {
    const modal = document.getElementById('pillar-details-modal');
    const title = document.getElementById('pillar-modal-title');
    const body = document.getElementById('pillar-modal-body');

    title.textContent = `${spObj.id} - ${spObj.name}`;

    let html = '<div style="padding: 8px 0;">';

    // Parent pillar
    if (spObj._pillarCode) {
        html += `<div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 12px;">Pillar: <strong>${spObj._pillarCode}</strong> - ${spObj._pillarName || ''}</div>`;
    }

    // Expanded definition
    if (spObj.definition) {
        html += `
            <div style="margin-bottom: 16px;">
                <h4 style="margin: 0 0 6px 0; color: var(--color-primary); font-size: 13px;">Expanded Definition</h4>
                <p style="font-size: 13px; line-height: 1.6; color: var(--text-primary); margin: 0;">${spObj.definition}</p>
            </div>
        `;
    }

    // Activities / Evaluation criteria
    const activities = spObj.activities || [];
    if (activities.length > 0) {
        // Determine the label based on schema
        const isAISchema = (appState.currentSchemaFileName || '').includes('5-0');
        const label = isAISchema ? 'AI Evaluation Criteria' : 'What to Verify Publicly';
        html += `
            <div style="margin-bottom: 16px;">
                <h4 style="margin: 0 0 8px 0; color: var(--color-primary); font-size: 13px;">${label}</h4>
                <ul style="margin: 0; padding-left: 20px;">
                    ${activities.map(a => `<li style="font-size: 12px; color: var(--text-primary); margin-bottom: 8px; line-height: 1.5;">${a}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    // If we have extra enriched data from schemaDetail
    const detail = appState.schemaDetail;
    if (detail && detail.sub_pillars) {
        const enriched = detail.sub_pillars.find(sp => sp.id === spObj.id);
        if (enriched) {
            // AI-specific evidence (v4.0)
            const aiSpecific = enriched.ai_specific_evidence || [];
            if (aiSpecific.length > 0) {
                html += `
                    <div style="margin-bottom: 16px;">
                        <h4 style="margin: 0 0 8px 0; color: var(--color-primary); font-size: 13px;">AI-Specific Evidence</h4>
                        <ul style="margin: 0; padding-left: 20px;">
                            ${aiSpecific.map(a => `<li style="font-size: 12px; color: var(--text-primary); margin-bottom: 6px; line-height: 1.4;">${a}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }

            // What to verify publicly (v4.0)
            const verify = enriched.what_to_verify_publicly || [];
            if (verify.length > 0 && activities !== verify) {
                html += `
                    <div style="margin-bottom: 16px;">
                        <h4 style="margin: 0 0 8px 0; color: var(--color-primary); font-size: 13px;">What to Verify Publicly</h4>
                        <ul style="margin: 0; padding-left: 20px;">
                            ${verify.map(a => `<li style="font-size: 12px; color: var(--text-primary); margin-bottom: 6px; line-height: 1.4;">${a}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }
        }
    }

    html += `
        <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border-color); font-size: 11px; color: var(--text-secondary);">
            Schema: ${appState.currentSchemaFileName || 'Default'}
        </div>
    `;
    html += '</div>';

    body.innerHTML = html;
    modal.classList.add('show');
}

function openEditModal(type, idOrCode, name, descriptionOrDef) {
    const modal = document.getElementById('edit-modal');
    const form = document.getElementById('edit-form');
    const idField = document.getElementById('edit-id');
    const nameField = document.getElementById('edit-name');
    const descField = document.getElementById('edit-description');
    
    idField.value = idOrCode;
    nameField.value = name;
    descField.value = descriptionOrDef;
    
    // Store the type and id for saving
    form.dataset.editType = type;
    form.dataset.editId = idOrCode;
    
    modal.classList.add('show');
}

function setupEditFormHandler() {
    const form = document.getElementById('edit-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const type = form.dataset.editType;
        const id = form.dataset.editId;
        const name = document.getElementById('edit-name').value;
        const description = document.getElementById('edit-description').value;
        
        try {
            const response = await fetch('/api/update-definition', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: type,
                    id: id,
                    name: name,
                    description: description
                })
            });
            
            if (response.ok) {
                // Close modal and refresh legend
                document.getElementById('edit-modal').classList.remove('show');
                // Reload metadata to update the display
                const metadataResponse = await fetch('/api/metadata');
                const metadata = await metadataResponse.json();
                appState.fieldMetadata = metadata.field_metadata;
                appState.scoreLegend = metadata.score_legend;
                appState.pillarsGrouped = metadata.pillars_grouped || [];
                populateLegendView();
            } else {
                alert('Failed to save changes');
            }
        } catch (error) {
            alert('Error saving changes');
        }
    });
}

function updateDashboard() {
    const vendors = appState.vendors;
    
    // Calculate statistics
    const stats = {
        total: vendors.length,
        aiFirst: vendors.filter(v => v.is_ai_first).length,
        startups: vendors.filter(v => v.is_startup).length,
        global: vendors.filter(v => v.region === 'Global').length
    };
    
    // Update stat cards
    document.getElementById('stat-total-vendors').textContent = stats.total;
    document.getElementById('stat-ai-first').textContent = stats.aiFirst;
    document.getElementById('stat-startups').textContent = stats.startups;
    document.getElementById('stat-global').textContent = stats.global;
    
    // Region distribution
    const regionDist = {};
    vendors.forEach(v => {
        regionDist[v.region] = (regionDist[v.region] || 0) + 1;
    });
    
    // Pillar averages
    const pillarAvgs = { PLA: 0, INV: 0, REM: 0, PMG: 0, LAW: 0 };
    vendors.forEach(v => {
        const scores = v.pillar_scores || {};
        Object.keys(pillarAvgs).forEach(p => {
            if (scores[p]) pillarAvgs[p] += scores[p];
        });
    });
    Object.keys(pillarAvgs).forEach(p => {
        pillarAvgs[p] = (pillarAvgs[p] / vendors.length).toFixed(2);
    });
    
    // Render charts
    renderRegionChart(regionDist);
    renderPillarChart(pillarAvgs);
}

function renderRegionChart(data) {
    const chart = document.getElementById('region-chart');
    const sorted = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8);
    
    const maxValue = Math.max(...sorted.map(d => d[1]));
    
    chart.innerHTML = sorted.map(([region, count]) => {
        const percentage = (count / maxValue) * 100;
        return `
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-size: 12px;">${region}</span>
                    <span style="font-size: 12px; font-weight: bold;">${count}</span>
                </div>
                <div style="height: 24px; background: var(--bg-tertiary); border-radius: 4px; overflow: hidden;">
                    <div style="height: 100%; width: ${percentage}%; background: linear-gradient(90deg, #0078d4, #107c10);"></div>
                </div>
            </div>
        `;
    }).join('');
}

function renderPillarChart(data) {
    const chart = document.getElementById('pillar-chart');
    const pillars = Object.entries(data).sort((a, b) => b[1] - a[1]);
    
    chart.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px;">
            ${pillars.map(([pillar, avg]) => `
                <div style="text-align: center;">
                    <div style="font-size: 20px; font-weight: bold; color: var(--color-primary);">${avg}</div>
                    <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">${pillar}</div>
                </div>
            `).join('')}
        </div>
    `;
}
// Analytics Tab Functions
// Widget visibility state
const DEFAULT_VISIBLE_WIDGETS = [
    'region-chart',
    'pillar-chart',
    'specialization-chart',
    'type-chart',
    'ai-chart',
    'startup-chart',
    'pillar-radar-chart',
    'comparison-radar-chart',
    'validation-comparison-chart',
    'summary-stats'
];

const widgetState = {
    visibleWidgets: new Set(DEFAULT_VISIBLE_WIDGETS)
};

// Load widget preferences from localStorage
function loadWidgetPreferences() {
    const saved = localStorage.getItem('visibleWidgets');
    if (saved) {
        try {
            widgetState.visibleWidgets = new Set(JSON.parse(saved));
        } catch {
            widgetState.visibleWidgets = new Set(DEFAULT_VISIBLE_WIDGETS);
        }

        // Migration: if new default widgets exist, show them by default
        DEFAULT_VISIBLE_WIDGETS.forEach(w => widgetState.visibleWidgets.add(w));
    }
    
    // Load widget sizes
    const savedSizes = localStorage.getItem('widgetSizes');
    if (savedSizes) {
        const sizes = JSON.parse(savedSizes);
        Object.entries(sizes).forEach(([widget, size]) => {
            const element = document.querySelector(`[data-widget="${widget}"]`);
            if (element) {
                element.style.setProperty('--col-span', size.colSpan);
                element.style.setProperty('--row-span', size.rowSpan);
                element.setAttribute('data-col-span', size.colSpan);
                element.setAttribute('data-row-span', size.rowSpan);
            }
        });
    }
}

// Save widget preferences to localStorage
function saveWidgetPreferences() {
    localStorage.setItem('visibleWidgets', JSON.stringify(Array.from(widgetState.visibleWidgets)));
    
    // Save widget sizes
    const sizes = {};
    document.querySelectorAll('[data-widget]').forEach(widget => {
        const widgetName = widget.getAttribute('data-widget');
        sizes[widgetName] = {
            colSpan: parseInt(widget.getAttribute('data-col-span')) || 1,
            rowSpan: parseInt(widget.getAttribute('data-row-span')) || 1
        };
    });
    localStorage.setItem('widgetSizes', JSON.stringify(sizes));
}

// Toggle widget visibility
function toggleWidget(widgetName, visible) {
    const widget = document.querySelector(`[data-widget="${widgetName}"]`);
    if (widget) {
        if (visible) {
            widget.classList.remove('hidden');
            widgetState.visibleWidgets.add(widgetName);
        } else {
            widget.classList.add('hidden');
            widgetState.visibleWidgets.delete(widgetName);
        }
    }
}

// Initialize widget customization UI
// Widget definitions for modal preview
const widgetDefinitions = {
    'region-chart': 'Vendor Distribution by Region',
    'pillar-chart': 'Average Pillar Capabilities',
    'specialization-chart': 'Specialization Breakdown',
    'type-chart': 'IR Focus Type Distribution',
    'ai-chart': 'AI-First vs Traditional',
    'startup-chart': 'Startup vs Established',
    'pillar-radar-chart': 'Pillar Capabilities Radar',
    'comparison-radar-chart': 'Comparison Radar (5-way)',
    'validation-comparison-chart': 'Score Layer Comparison',
    'summary-stats': 'Summary Statistics'
};

// Comparison Radar state
const comparisonRadarState = {
    type: 'vendor',
    selections: ['', '', '', '', ''],
    axes: 'pillars' // pillars | subpillars | both
};

const COMPARISON_RADAR_STORAGE_KEY = 'comparisonRadarState';

function loadComparisonRadarState() {
    try {
        const raw = localStorage.getItem(COMPARISON_RADAR_STORAGE_KEY);
        if (!raw) return;
        const parsed = JSON.parse(raw);
        if (parsed && typeof parsed === 'object') {
            if (typeof parsed.type === 'string') comparisonRadarState.type = parsed.type;
            if (typeof parsed.axes === 'string') comparisonRadarState.axes = parsed.axes;
            if (Array.isArray(parsed.selections) && parsed.selections.length === 5) {
                comparisonRadarState.selections = parsed.selections.map(v => (typeof v === 'string' ? v : ''));
            }
        }
    } catch {
        // Ignore invalid persisted state
    }
}

function saveComparisonRadarState() {
    try {
        localStorage.setItem(COMPARISON_RADAR_STORAGE_KEY, JSON.stringify({
            type: comparisonRadarState.type,
            axes: comparisonRadarState.axes,
            selections: comparisonRadarState.selections
        }));
    } catch {
        // Ignore storage errors (quota, privacy mode)
    }
}

function initializeComparisonRadarWidget() {
    const typeSelect = document.getElementById('comparison-radar-type');
    if (!typeSelect) return;

    // Avoid double binding
    if (typeSelect.dataset.bound === 'true') return;
    typeSelect.dataset.bound = 'true';

    // Load persisted state (once per page load)
    if (!initializeComparisonRadarWidget._loadedState) {
        loadComparisonRadarState();
        initializeComparisonRadarWidget._loadedState = true;
    }

    typeSelect.value = comparisonRadarState.type;
    const axesSelect = document.getElementById('comparison-radar-axes');
    if (axesSelect) axesSelect.value = comparisonRadarState.axes;

    // Config modal wiring
    const configBtn = document.getElementById('comparison-radar-config-btn');
    const modal = document.getElementById('comparison-radar-config-modal');
    const closeBtn = document.getElementById('comparison-radar-config-close');
    const saveBtn = document.getElementById('comparison-radar-config-save');
    const cancelBtn = document.getElementById('comparison-radar-config-cancel');

    let draftState = {
        type: comparisonRadarState.type,
        axes: comparisonRadarState.axes,
        selections: [...comparisonRadarState.selections]
    };

    function syncInputsFromDraft() {
        if (typeSelect) typeSelect.value = draftState.type;
        if (axesSelect) axesSelect.value = draftState.axes;
        populateComparisonRadarDropdowns();
    }

    function openModal() {
        if (!modal) return;
        draftState = {
            type: comparisonRadarState.type,
            axes: comparisonRadarState.axes,
            selections: [...comparisonRadarState.selections]
        };
        syncInputsFromDraft();
        modal.classList.add('show');
    }

    function closeModal() {
        if (!modal) return;
        modal.classList.remove('show');
    }

    function applyDraftToState() {
        comparisonRadarState.type = draftState.type;
        comparisonRadarState.axes = draftState.axes;
        comparisonRadarState.selections = [...draftState.selections];
        saveComparisonRadarState();
        populateComparisonRadarDropdowns();
    }

    function cancelDraft() {
        draftState = {
            type: comparisonRadarState.type,
            axes: comparisonRadarState.axes,
            selections: [...comparisonRadarState.selections]
        };
        closeModal();
    }

    if (configBtn && !configBtn.dataset.bound) {
        configBtn.dataset.bound = 'true';
        configBtn.addEventListener('click', openModal);
    }

    if (closeBtn && !closeBtn.dataset.bound) {
        closeBtn.dataset.bound = 'true';
        closeBtn.addEventListener('click', cancelDraft);
    }

    if (cancelBtn && !cancelBtn.dataset.bound) {
        cancelBtn.dataset.bound = 'true';
        cancelBtn.addEventListener('click', cancelDraft);
    }

    if (saveBtn && !saveBtn.dataset.bound) {
        saveBtn.dataset.bound = 'true';
        saveBtn.addEventListener('click', () => {
            // Read current inputs into draft
            draftState.type = typeSelect.value;
            if (axesSelect) draftState.axes = axesSelect.value;
            ['s1', 's2', 's3', 's4', 's5'].forEach((sid, idx) => {
                const el = document.getElementById(`comparison-radar-${sid}`);
                if (el) draftState.selections[idx] = el.value;
            });

            applyDraftToState();
            renderComparisonRadar();
            closeModal();
        });
    }

    if (modal && !modal.dataset.bound) {
        modal.dataset.bound = 'true';
        modal.addEventListener('click', (e) => {
            if (e.target === modal) cancelDraft();
        });
    }

    typeSelect.addEventListener('change', () => {
        draftState.type = typeSelect.value;
        // Reset selections when changing type
        draftState.selections = ['', '', '', '', ''];
        // Keep underlying state untouched until Save
        populateComparisonRadarDropdowns();

        // Clear UI selects explicitly (so we don't preserve stale values)
        ['s1', 's2', 's3', 's4', 's5'].forEach((sid) => {
            const el = document.getElementById(`comparison-radar-${sid}`);
            if (el) el.value = '';
        });
    });

    if (axesSelect) {
        axesSelect.addEventListener('change', () => {
            draftState.axes = axesSelect.value;
        });
    }

    ['s1', 's2', 's3', 's4', 's5'].forEach((sid, idx) => {
        const el = document.getElementById(`comparison-radar-${sid}`);
        if (!el) return;
        el.addEventListener('change', () => {
            draftState.selections[idx] = el.value;
        });
    });
}

function getComparisonOptions(typeOverride = null) {
    const vendors = (appState.filteredVendors && appState.filteredVendors.length)
        ? appState.filteredVendors
        : (appState.vendors || []);
    const type = typeOverride || comparisonRadarState.type;

    if (type === 'vendor') {
        return vendors
            .map(v => v.vendor)
            .filter(Boolean)
            .sort((a, b) => String(a).localeCompare(String(b)));
    }

    if (type === 'region') {
        const regions = Array.from(new Set(vendors.map(v => v.region).filter(Boolean))).sort((a, b) => String(a).localeCompare(String(b)));
        const macros = new Set();
        const joined = regions.join(' ').toLowerCase();
        ['america', 'europe', 'emea', 'apac', 'asia', 'global', 'latam', 'middle east', 'africa'].forEach(tok => {
            if (joined.includes(tok)) macros.add(tok);
        });
        const macroList = Array.from(macros).map(s => s.replace(/\b\w/g, c => c.toUpperCase()));
        return [...regions, ...macroList];
    }

    if (type === 'ai_first') {
        return ['AI-First', 'Not AI-First'];
    }

    if (type === 'startup') {
        return ['Startup', 'Established'];
    }

    if (type === 'ir_focus_type') {
        return Array.from(new Set(vendors.map(v => v.ir_focus_type).filter(Boolean))).sort((a, b) => String(a).localeCompare(String(b)));
    }

    return [];
}

function populateComparisonRadarDropdowns() {
    const typeSelect = document.getElementById('comparison-radar-type');
    const modal = document.getElementById('comparison-radar-config-modal');
    const isModalOpen = !!(modal && modal.classList.contains('show'));
    const effectiveType = typeSelect ? typeSelect.value : comparisonRadarState.type;

    const opts = getComparisonOptions(effectiveType);
    const emptyLabel = effectiveType === 'vendor' ? 'Select vendor…' : 'Select value…';
    const ids = ['s1', 's2', 's3', 's4', 's5'];

    const previousValues = ids.map((sid) => {
        const el = document.getElementById(`comparison-radar-${sid}`);
        return el ? el.value : '';
    });

    ids.forEach((sid, idx) => {
        const el = document.getElementById(`comparison-radar-${sid}`);
        if (!el) return;
        el.innerHTML = '';

        const empty = document.createElement('option');
        empty.value = '';
        empty.textContent = `${idx + 1}: ${emptyLabel}`;
        el.appendChild(empty);

        opts.forEach(v => {
            const opt = document.createElement('option');
            opt.value = String(v);
            opt.textContent = String(v);
            el.appendChild(opt);
        });

        const desired = (isModalOpen ? previousValues[idx] : (comparisonRadarState.selections[idx] || ''));
        const hasOption = desired && Array.from(el.options).some(o => o.value === desired);
        el.value = hasOption ? desired : '';

        if (!isModalOpen && desired && !hasOption) {
            comparisonRadarState.selections[idx] = '';
            saveComparisonRadarState();
        }
    });
}

function matchVendorsForSelection(selectionValue, vendorsForAverages) {
    const allVendors = appState.vendors || [];
    const type = comparisonRadarState.type;
    const val = (selectionValue || '').trim();
    if (!val) return { label: '', vendors: [] };

    if (type === 'vendor') {
        const v = allVendors.find(x => String(x.vendor) === val);
        return { label: val, vendors: v ? [v] : [] };
    }

    if (type === 'region') {
        const needle = val.toLowerCase();
        const matched = (vendorsForAverages || []).filter(v => String(v.region || '').toLowerCase().includes(needle));
        return { label: val, vendors: matched };
    }

    if (type === 'ai_first') {
        const want = val === 'AI-First';
        const matched = (vendorsForAverages || []).filter(v => !!v.is_ai_first === want);
        return { label: val, vendors: matched };
    }

    if (type === 'startup') {
        const want = val === 'Startup';
        const matched = (vendorsForAverages || []).filter(v => !!v.is_startup === want);
        return { label: val, vendors: matched };
    }

    if (type === 'ir_focus_type') {
        const matched = (vendorsForAverages || []).filter(v => String(v.ir_focus_type || '') === val);
        return { label: val, vendors: matched };
    }

    return { label: val, vendors: [] };
}

function computePillarAveragesForVendors(vendors) {
    const pillars = ['PLA', 'INV', 'REM', 'PMG', 'LAW'];
    const sums = { PLA: 0, INV: 0, REM: 0, PMG: 0, LAW: 0 };
    const counts = { PLA: 0, INV: 0, REM: 0, PMG: 0, LAW: 0 };

    (vendors || []).forEach(v => {
        const scores = getEffectivePillarScores(v) || {};
        pillars.forEach(p => {
            const x = scores[p];
            if (x !== undefined && x !== null && x !== '' && !Number.isNaN(Number(x))) {
                sums[p] += Number(x);
                counts[p] += 1;
            }
        });
    });

    const out = {};
    pillars.forEach(p => {
        out[p] = counts[p] ? (sums[p] / counts[p]) : 0;
    });
    return out;
}

function computeSubPillarAveragesForVendors(vendors) {
    const ordered = (appState.subPillars || []).map(s => s.id);
    const sums = {};
    const counts = {};
    ordered.forEach(id => { sums[id] = 0; counts[id] = 0; });

    (vendors || []).forEach(v => {
        const mapping = getEffectiveGranularMapping(v) || {};
        Object.values(mapping).forEach(pillarObj => {
            if (!pillarObj || typeof pillarObj !== 'object') return;
            Object.entries(pillarObj).forEach(([sid, val]) => {
                if (!(sid in sums)) return;
                const n = Number(val);
                if (Number.isNaN(n)) return;
                sums[sid] += n;
                counts[sid] += 1;
            });
        });
    });

    const out = {};
    ordered.forEach(id => {
        out[id] = counts[id] ? (sums[id] / counts[id]) : 0;
    });
    return out;
}

function renderComparisonRadar(vendorsForAverages = null) {
    const container = document.getElementById('comparison-radar-chart');
    if (!container) return;
    // Don't do work if widget is hidden
    const widgetEl = container.closest('[data-widget="comparison-radar-chart"]');
    if (widgetEl && widgetEl.classList.contains('hidden')) return;

    const baseVendors = vendorsForAverages || appState.filteredVendors || appState.vendors || [];
    const pillarAxes = ['PLA', 'INV', 'REM', 'PMG', 'LAW'];
    const subPillarAxes = (appState.subPillars || []).map(s => s.id);
    const axesMode = comparisonRadarState.axes || 'pillars';
    const axes = axesMode === 'subpillars'
        ? subPillarAxes
        : axesMode === 'both'
            ? [...pillarAxes, ...subPillarAxes]
            : pillarAxes;

    const seriesColors = [
        { stroke: '#0078d4', fill: 'rgba(0, 120, 212, 0.18)' },
        { stroke: '#107c10', fill: 'rgba(16, 124, 16, 0.18)' },
        { stroke: '#d83b01', fill: 'rgba(216, 59, 1, 0.18)' },
        { stroke: '#5c2d91', fill: 'rgba(92, 45, 145, 0.18)' },
        { stroke: '#a4262c', fill: 'rgba(164, 38, 44, 0.18)' }
    ];

    const selected = comparisonRadarState.selections
        .map((v, idx) => ({ v, idx }))
        .filter(x => x.v && x.v.trim().length > 0);

    if (selected.length === 0) {
        container.innerHTML = '<div style="color: var(--text-secondary); font-size: 12px; padding: 10px;">Click the gear (⚙) to configure up to 5 comparison series.</div>';
        return;
    }

    const computedSeries = selected.map(({ v, idx }) => {
        const { label, vendors } = matchVendorsForSelection(v, baseVendors);
        const pillarAvg = computePillarAveragesForVendors(vendors);
        const subAvg = computeSubPillarAveragesForVendors(vendors);
        const scores = axes.map(a => (pillarAxes.includes(a) ? (pillarAvg[a] || 0) : (subAvg[a] || 0)));
        return {
            label,
            count: (vendors || []).length,
            scores,
            color: seriesColors[idx % seriesColors.length]
        };
    }).filter(s => s.count > 0 || comparisonRadarState.type === 'vendor');

    const width = Math.max(320, container.clientWidth || 600);
    const height = Math.max(260, container.clientHeight || 420);
    const padding = 40;
    const cx = width / 2;
    const cy = height / 2;
    const radius = Math.min(width, height) / 2 - padding;

    const axisCount = axes.length;
    const angleStep = (Math.PI * 2) / axisCount;
    const startAngle = -Math.PI / 2;
    const scaleMax = 5;

    function pt(angle, r) {
        return { x: cx + Math.cos(angle) * r, y: cy + Math.sin(angle) * r };
    }

    // Background + grid
    let svg = `
        <svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-label="Comparison radar chart">
            <rect x="0" y="0" width="${width}" height="${height}" fill="transparent" />
    `;

    // Rings
    for (let i = 1; i <= scaleMax; i++) {
        const r = (radius * i) / scaleMax;
        svg += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="var(--border-color)" stroke-width="1" opacity="0.6" />`;
    }

    // Axes + labels
    const labelEvery = axisCount > 22 ? 3 : axisCount > 12 ? 2 : 1;
    const labelFont = axisCount > 22 ? 8 : axisCount > 12 ? 9 : 12;

    axes.forEach((p, i) => {
        const a = startAngle + i * angleStep;
        const end = pt(a, radius);
        svg += `<line x1="${cx}" y1="${cy}" x2="${end.x}" y2="${end.y}" stroke="var(--border-color)" stroke-width="1" opacity="0.8" />`;

        if (i % labelEvery === 0) {
            const labelPos = pt(a, radius + 16);
            const anchor = (Math.cos(a) > 0.2) ? 'start' : (Math.cos(a) < -0.2) ? 'end' : 'middle';
            svg += `<text x="${labelPos.x}" y="${labelPos.y}" font-size="${labelFont}" fill="var(--text-secondary)" text-anchor="${anchor}" dominant-baseline="middle"><title>${p}</title>${p}</text>`;
        }
    });

    // Series polygons
    computedSeries.forEach((s) => {
        const points = s.scores.map((val, i) => {
            const a = startAngle + i * angleStep;
            const r = radius * (Math.max(0, Math.min(scaleMax, Number(val))) / scaleMax);
            const p = pt(a, r);
            return `${p.x},${p.y}`;
        }).join(' ');

        svg += `<polygon points="${points}" fill="${s.color.fill}" stroke="${s.color.stroke}" stroke-width="2" />`;
        // Dots
        s.scores.forEach((val, i) => {
            const a = startAngle + i * angleStep;
            const r = radius * (Math.max(0, Math.min(scaleMax, Number(val))) / scaleMax);
            const p = pt(a, r);
            svg += `<circle cx="${p.x}" cy="${p.y}" r="3" fill="${s.color.stroke}" />`;
        });
    });

    svg += `</svg>`;

    const legend = computedSeries.map((s, i) => {
        const suffix = comparisonRadarState.type === 'vendor' ? '' : ` (n=${s.count})`;
        return `
            <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:var(--text-secondary); margin:2px 0;">
                <span style="display:inline-block; width:10px; height:10px; border-radius:2px; background:${s.color.stroke};"></span>
                <span>${s.label}${suffix}</span>
            </div>
        `;
    }).join('');

    container.innerHTML = `
        <div style="display:grid; grid-template-columns: 1fr 220px; gap: 12px; align-items: start; height: 100%;">
            <div style="min-width: 0;">${svg}</div>
            <div style="padding: 8px; border: 1px solid var(--border-color); border-radius: 8px; background: var(--bg-secondary);">
                <div style="font-weight: 600; font-size: 12px; color: var(--text-primary); margin-bottom: 6px;">Series</div>
                ${legend}
                <div style="margin-top: 8px; font-size: 11px; color: var(--text-secondary);">
                    Uses <strong>${appState.scoreMode}</strong> scores (${axesMode}).
                </div>
            </div>
        </div>
    `;
}

// ==================== Researched vs Validated Comparison Widget ====================

const validationComparisonState = {
    categoryType: 'all',  // all | region | startup | ai_first | ir_focus_type
    categoryValue: '',    // e.g., "Global", "Startup"
    axes: 'pillars',      // pillars | subpillars | both
    showDelta: true       // Show delta/difference metrics
};

const VALIDATION_COMPARISON_STORAGE_KEY = 'validationComparisonState';

function loadValidationComparisonState() {
    try {
        const raw = localStorage.getItem(VALIDATION_COMPARISON_STORAGE_KEY);
        if (!raw) return;
        const parsed = JSON.parse(raw);
        if (parsed && typeof parsed === 'object') {
            if (typeof parsed.categoryType === 'string') validationComparisonState.categoryType = parsed.categoryType;
            if (typeof parsed.categoryValue === 'string') validationComparisonState.categoryValue = parsed.categoryValue;
            if (typeof parsed.axes === 'string') validationComparisonState.axes = parsed.axes;
            if (typeof parsed.showDelta === 'boolean') validationComparisonState.showDelta = parsed.showDelta;
        }
    } catch {
        // Ignore invalid persisted state
    }
}

function saveValidationComparisonState() {
    try {
        localStorage.setItem(VALIDATION_COMPARISON_STORAGE_KEY, JSON.stringify({
            categoryType: validationComparisonState.categoryType,
            categoryValue: validationComparisonState.categoryValue,
            axes: validationComparisonState.axes,
            showDelta: validationComparisonState.showDelta
        }));
    } catch {
        // Ignore storage errors
    }
}

function getValidationComparisonCategoryValues(categoryType) {
    const vendors = appState.filteredVendors || appState.vendors || [];
    
    if (categoryType === 'all') {
        return [];
    }
    
    if (categoryType === 'region') {
        return Array.from(new Set(vendors.map(v => v.region).filter(Boolean))).sort((a, b) => String(a).localeCompare(String(b)));
    }
    
    if (categoryType === 'startup') {
        return ['Startup', 'Established'];
    }
    
    if (categoryType === 'ai_first') {
        return ['AI-First', 'Traditional'];
    }
    
    if (categoryType === 'ir_focus_type') {
        return Array.from(new Set(vendors.map(v => v.ir_focus_type).filter(Boolean))).sort((a, b) => String(a).localeCompare(String(b)));
    }
    
    return [];
}

function filterVendorsByValidationCategory(vendors, categoryType, categoryValue) {
    if (!categoryType || categoryType === 'all') return vendors;
    
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

function initializeValidationComparisonWidget() {
    const configBtn = document.getElementById('validation-comparison-config-btn');
    const modal = document.getElementById('validation-comparison-config-modal');
    const closeBtn = document.getElementById('validation-comparison-config-close');
    const saveBtn = document.getElementById('validation-comparison-config-save');
    const cancelBtn = document.getElementById('validation-comparison-config-cancel');
    
    if (!configBtn || !modal) return;
    
    if (!initializeValidationComparisonWidget._loadedState) {
        loadValidationComparisonState();
        initializeValidationComparisonWidget._loadedState = true;
    }
    
    const categoryTypeSelect = document.getElementById('validation-comparison-category-type');
    const categoryValueSelect = document.getElementById('validation-comparison-category-value');
    const axesSelect = document.getElementById('validation-comparison-axes');
    const showDeltaCheckbox = document.getElementById('validation-comparison-show-delta');
    
    let draftState = JSON.parse(JSON.stringify(validationComparisonState));
    
    function populateCategoryValues() {
        const categoryType = draftState.categoryType;
        const values = getValidationComparisonCategoryValues(categoryType);
        
        categoryValueSelect.innerHTML = categoryType === 'all' 
            ? '<option value="">N/A - All Vendors</option>'
            : '<option value="">Select...</option>';
        
        values.forEach(v => {
            const opt = document.createElement('option');
            opt.value = v;
            opt.textContent = v;
            categoryValueSelect.appendChild(opt);
        });
        
        categoryValueSelect.disabled = categoryType === 'all';
        categoryValueSelect.value = categoryType === 'all' ? '' : (draftState.categoryValue || '');
    }
    
    function openModal() {
        draftState = JSON.parse(JSON.stringify(validationComparisonState));
        categoryTypeSelect.value = draftState.categoryType;
        axesSelect.value = draftState.axes;
        showDeltaCheckbox.checked = draftState.showDelta;
        populateCategoryValues();
        modal.classList.add('show');
    }
    
    function closeModal() {
        modal.classList.remove('show');
    }
    
    function applyDraftToState() {
        validationComparisonState.categoryType = draftState.categoryType;
        validationComparisonState.categoryValue = draftState.categoryValue;
        validationComparisonState.axes = draftState.axes;
        validationComparisonState.showDelta = draftState.showDelta;
        saveValidationComparisonState();
        renderValidationComparison();
        closeModal();
    }
    
    if (configBtn && !configBtn.dataset.bound) {
        configBtn.dataset.bound = 'true';
        configBtn.addEventListener('click', openModal);
    }
    
    if (closeBtn && !closeBtn.dataset.bound) {
        closeBtn.dataset.bound = 'true';
        closeBtn.addEventListener('click', () => {
            draftState = JSON.parse(JSON.stringify(validationComparisonState));
            closeModal();
        });
    }
    
    if (cancelBtn && !cancelBtn.dataset.bound) {
        cancelBtn.dataset.bound = 'true';
        cancelBtn.addEventListener('click', () => {
            draftState = JSON.parse(JSON.stringify(validationComparisonState));
            closeModal();
        });
    }
    
    if (saveBtn && !saveBtn.dataset.bound) {
        saveBtn.dataset.bound = 'true';
        saveBtn.addEventListener('click', () => {
            draftState.categoryType = categoryTypeSelect.value;
            draftState.categoryValue = categoryValueSelect.value;
            draftState.axes = axesSelect.value;
            draftState.showDelta = showDeltaCheckbox.checked;
            applyDraftToState();
        });
    }
    
    if (categoryTypeSelect && !categoryTypeSelect.dataset.bound) {
        categoryTypeSelect.dataset.bound = 'true';
        categoryTypeSelect.addEventListener('change', () => {
            draftState.categoryType = categoryTypeSelect.value;
            draftState.categoryValue = '';
            populateCategoryValues();
        });
    }
    
    if (categoryValueSelect && !categoryValueSelect.dataset.bound) {
        categoryValueSelect.dataset.bound = 'true';
        categoryValueSelect.addEventListener('change', () => {
            draftState.categoryValue = categoryValueSelect.value;
        });
    }
    
    if (modal && !modal.dataset.bound) {
        modal.dataset.bound = 'true';
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                draftState = JSON.parse(JSON.stringify(validationComparisonState));
                closeModal();
            }
        });
    }
}

function computeAveragesForScoreMode(vendors, scoreMode) {
    const pillars = ['PLA', 'INV', 'REM', 'PMG', 'LAW'];
    const subPillars = (appState.subPillars || []).map(s => s.id);
    
    const pillarSums = { PLA: 0, INV: 0, REM: 0, PMG: 0, LAW: 0 };
    const pillarCounts = { PLA: 0, INV: 0, REM: 0, PMG: 0, LAW: 0 };
    const subPillarSums = {};
    const subPillarCounts = {};
    
    subPillars.forEach(id => { subPillarSums[id] = 0; subPillarCounts[id] = 0; });
    
    (vendors || []).forEach(v => {
        // Get scores based on mode
        let pillarScores, subPillarScores;
        
        if (scoreMode === 'ai_researched') {
            pillarScores = v.pillar_scores_ai_researched || {};
            subPillarScores = v.sub_pillar_scores_ai_researched || {};
            
            // If we don't have pillar_scores_ai_researched, derive from sub-pillars
            if (!v.pillar_scores_ai_researched && subPillarScores && Object.keys(subPillarScores).length > 0) {
                pillarScores = buildPillarScoresFromSubPillars(subPillarScores);
            }
        } else if (scoreMode === 'researched') {
            pillarScores = v.pillar_scores_researched || {};
            subPillarScores = v.sub_pillar_scores_researched || {};
            
            // If we don't have pillar_scores_researched, derive from sub-pillars
            if (!v.pillar_scores_researched && subPillarScores && Object.keys(subPillarScores).length > 0) {
                pillarScores = buildPillarScoresFromSubPillars(subPillarScores);
            }
        } else {
            // validated
            pillarScores = v.pillar_scores_validated || v.pillar_scores || {};
            subPillarScores = v.sub_pillar_scores_validated || v.sub_pillar_scores || {};
        }
        
        // Accumulate pillar scores
        pillars.forEach(p => {
            const val = pillarScores[p];
            if (val !== undefined && val !== null && !Number.isNaN(Number(val))) {
                pillarSums[p] += Number(val);
                pillarCounts[p] += 1;
            }
        });
        
        // Accumulate sub-pillar scores directly from sub_pillar_scores object
        Object.entries(subPillarScores || {}).forEach(([sid, val]) => {
            if (!(sid in subPillarSums)) return;
            const n = Number(val);
            if (Number.isNaN(n)) return;
            subPillarSums[sid] += n;
            subPillarCounts[sid] += 1;
        });
    });
    
    const pillarAvgs = {};
    pillars.forEach(p => {
        pillarAvgs[p] = pillarCounts[p] ? (pillarSums[p] / pillarCounts[p]) : 0;
    });
    
    const subPillarAvgs = {};
    subPillars.forEach(id => {
        subPillarAvgs[id] = subPillarCounts[id] ? (subPillarSums[id] / subPillarCounts[id]) : 0;
    });
    
    return { pillars: pillarAvgs, subPillars: subPillarAvgs, vendorCount: vendors.length };
}

function buildPillarScoresFromSubPillars(subPillarScores) {
    const pillars = { PLA: [], INV: [], REM: [], PMG: [], LAW: [] };
    
    Object.entries(subPillarScores || {}).forEach(([subId, score]) => {
        const pillarCode = subId.substring(0, 3);
        if (pillars[pillarCode]) {
            pillars[pillarCode].push(Number(score));
        }
    });
    
    const result = {};
    Object.entries(pillars).forEach(([pillar, scores]) => {
        if (scores.length > 0) {
            result[pillar] = scores.reduce((a, b) => a + b, 0) / scores.length;
        } else {
            result[pillar] = 0;
        }
    });
    
    return result;
}

function renderValidationRadar(container, data, title) {
    const pillarAxes = ['PLA', 'INV', 'REM', 'PMG', 'LAW'];
    const subPillarAxes = (appState.subPillars || []).map(s => s.id);
    const axesMode = validationComparisonState.axes || 'pillars';
    const axes = axesMode === 'subpillars'
        ? subPillarAxes
        : axesMode === 'both'
            ? [...pillarAxes, ...subPillarAxes]
            : pillarAxes;
    
    // Use fixed dimensions - SVG will scale responsively via viewBox
    const width = 350;
    const height = 320;
    const padding = 35;
    const cx = width / 2;
    const cy = height / 2;
    const radius = Math.min(width, height) / 2 - padding;
    
    const axisCount = axes.length;
    const angleStep = (Math.PI * 2) / axisCount;
    const startAngle = -Math.PI / 2;
    const scaleMax = 5;
    
    function pt(angle, r) {
        return { x: cx + Math.cos(angle) * r, y: cy + Math.sin(angle) * r };
    }
    
    // Build SVG
    let svg = `
        <svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-label="${title} radar chart">
            <rect x="0" y="0" width="${width}" height="${height}" fill="transparent" />
    `;
    
    // Rings
    for (let i = 1; i <= scaleMax; i++) {
        const r = (radius * i) / scaleMax;
        svg += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="var(--border-color)" stroke-width="1" opacity="0.6" />`;
    }
    
    // Axes
    const labelEvery = axisCount > 22 ? 3 : axisCount > 12 ? 2 : 1;
    const labelFont = axisCount > 22 ? 8 : axisCount > 12 ? 9 : 10;
    
    axes.forEach((p, i) => {
        const a = startAngle + i * angleStep;
        const end = pt(a, radius);
        svg += `<line x1="${cx}" y1="${cy}" x2="${end.x}" y2="${end.y}" stroke="var(--border-color)" stroke-width="1" opacity="0.8" />`;
        
        if (i % labelEvery === 0) {
            const labelPos = pt(a, radius + 14);
            const anchor = (Math.cos(a) > 0.2) ? 'start' : (Math.cos(a) < -0.2) ? 'end' : 'middle';
            svg += `<text x="${labelPos.x}" y="${labelPos.y}" font-size="${labelFont}" fill="var(--text-secondary)" text-anchor="${anchor}" dominant-baseline="middle"><title>${p}</title>${p}</text>`;
        }
    });
    
    // Data polygon
    const points = axes.map((axis, i) => {
        const val = pillarAxes.includes(axis) ? data.pillars[axis] : data.subPillars[axis];
        const a = startAngle + i * angleStep;
        const r = radius * (Math.max(0, Math.min(scaleMax, Number(val || 0))) / scaleMax);
        const p = pt(a, r);
        return `${p.x},${p.y}`;
    }).join(' ');
    
    const color = title.includes('Researched') 
        ? { stroke: '#0078d4', fill: 'rgba(0, 120, 212, 0.18)' }
        : { stroke: '#107c10', fill: 'rgba(16, 124, 16, 0.18)' };
    
    svg += `<polygon points="${points}" fill="${color.fill}" stroke="${color.stroke}" stroke-width="2" />`;
    
    // Dots
    axes.forEach((axis, i) => {
        const val = pillarAxes.includes(axis) ? data.pillars[axis] : data.subPillars[axis];
        const a = startAngle + i * angleStep;
        const r = radius * (Math.max(0, Math.min(scaleMax, Number(val || 0))) / scaleMax);
        const p = pt(a, r);
        svg += `<circle cx="${p.x}" cy="${p.y}" r="3" fill="${color.stroke}" />`;
    });
    
    svg += `</svg>`;
    
    container.innerHTML = svg;
}

function renderValidationRadarOverlay(container, researchedData, validatedData, aiResearchedData) {
    const pillarAxes = ['PLA', 'INV', 'REM', 'PMG', 'LAW'];
    const subPillarAxes = (appState.subPillars || []).map(s => s.id);
    const axesMode = validationComparisonState.axes || 'pillars';
    const axes = axesMode === 'subpillars'
        ? subPillarAxes
        : axesMode === 'both'
            ? [...pillarAxes, ...subPillarAxes]
            : pillarAxes;
    
    // Use fixed dimensions - SVG will scale responsively via viewBox
    const width = 450;
    const height = 400;
    const padding = 40;
    const cx = width / 2;
    const cy = height / 2;
    const radius = Math.min(width, height) / 2 - padding;
    
    const axisCount = axes.length;
    const angleStep = (Math.PI * 2) / axisCount;
    const startAngle = -Math.PI / 2;
    const scaleMax = 5;
    
    function pt(angle, r) {
        return { x: cx + Math.cos(angle) * r, y: cy + Math.sin(angle) * r };
    }
    
    // Build SVG
    let svg = `
        <svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-label="Score Comparison radar chart">
            <defs>
                <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                    <feDropShadow dx="0" dy="0" stdDeviation="1" flood-opacity="0.1"/>
                </filter>
            </defs>
            <rect x="0" y="0" width="${width}" height="${height}" fill="transparent" />
    `;
    
    // Rings
    for (let i = 1; i <= scaleMax; i++) {
        const r = (radius * i) / scaleMax;
        svg += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="var(--border-color)" stroke-width="1" opacity="0.6" />`;
    }
    
    // Scale labels
    svg += `<text x="${cx + 10}" y="${cy - radius - 8}" font-size="10" fill="var(--text-secondary)" opacity="0.7">5</text>`;
    svg += `<text x="${cx + 10}" y="${cy - radius * 0.8 - 8}" font-size="10" fill="var(--text-secondary)" opacity="0.7">4</text>`;
    svg += `<text x="${cx + 10}" y="${cy - radius * 0.6 - 8}" font-size="10" fill="var(--text-secondary)" opacity="0.7">3</text>`;
    
    // Axes
    const labelEvery = axisCount > 22 ? 3 : axisCount > 12 ? 2 : 1;
    const labelFont = axisCount > 22 ? 8 : axisCount > 12 ? 9 : 10;
    
    axes.forEach((p, i) => {
        const a = startAngle + i * angleStep;
        const end = pt(a, radius);
        svg += `<line x1="${cx}" y1="${cy}" x2="${end.x}" y2="${end.y}" stroke="var(--border-color)" stroke-width="1" opacity="0.8" />`;
        
        if (i % labelEvery === 0) {
            const labelPos = pt(a, radius + 18);
            const anchor = (Math.cos(a) > 0.2) ? 'start' : (Math.cos(a) < -0.2) ? 'end' : 'middle';
            svg += `<text x="${labelPos.x}" y="${labelPos.y}" font-size="${labelFont}" fill="var(--text-secondary)" text-anchor="${anchor}" dominant-baseline="middle"><title>${p}</title>${p}</text>`;
        }
    });
    
    // Render all polygons (validated first as base, then researched, then ai_researched on top)
    const datasets = [
        { data: validatedData, color: { stroke: '#107c10', fill: 'rgba(16, 124, 16, 0.15)' }, title: 'Validated' },
        { data: researchedData, color: { stroke: '#0078d4', fill: 'rgba(0, 120, 212, 0.15)' }, title: 'Researched' }
    ];
    
    if (aiResearchedData) {
        datasets.push({ data: aiResearchedData, color: { stroke: '#8b5cf6', fill: 'rgba(139, 92, 246, 0.15)' }, title: 'AI Researched' });
    }
    
    datasets.forEach(dataset => {
        const points = axes.map((axis, i) => {
            const val = pillarAxes.includes(axis) ? dataset.data.pillars[axis] : dataset.data.subPillars[axis];
            const a = startAngle + i * angleStep;
            const r = radius * (Math.max(0, Math.min(scaleMax, Number(val || 0))) / scaleMax);
            const p = pt(a, r);
            return `${p.x},${p.y}`;
        }).join(' ');
        
        svg += `<polygon points="${points}" fill="${dataset.color.fill}" stroke="${dataset.color.stroke}" stroke-width="2.5" filter="url(#shadow)" />`;
        
        // Dots
        axes.forEach((axis, i) => {
            const val = pillarAxes.includes(axis) ? dataset.data.pillars[axis] : dataset.data.subPillars[axis];
            const a = startAngle + i * angleStep;
            const r = radius * (Math.max(0, Math.min(scaleMax, Number(val || 0))) / scaleMax);
            const p = pt(a, r);
            svg += `<circle cx="${p.x}" cy="${p.y}" r="3.5" fill="${dataset.color.stroke}" stroke="white" stroke-width="1.5" />`;
        });
    });
    
    svg += `</svg>`;
    
    container.innerHTML = svg;
}

function renderValidationComparison(vendorsForAverages = null) {
    const container = document.getElementById('validation-comparison-chart');
    if (!container) return;
    
    const widgetEl = container.closest('[data-widget="validation-comparison-chart"]');
    if (widgetEl && widgetEl.classList.contains('hidden')) return;
    
    const baseVendors = vendorsForAverages || appState.filteredVendors || appState.vendors || [];
    const categoryType = validationComparisonState.categoryType;
    const categoryValue = validationComparisonState.categoryValue;
    
    const filteredVendors = filterVendorsByValidationCategory(baseVendors, categoryType, categoryValue);
    
    if (filteredVendors.length === 0) {
        container.innerHTML = '<div style="color: var(--text-secondary); font-size: 12px; padding: 16px; text-align: center;">No vendors match the selected category. Click the gear (⚙) to configure.</div>';
        return;
    }
    
    const researchedData = computeAveragesForScoreMode(filteredVendors, 'researched');
    const validatedData = computeAveragesForScoreMode(filteredVendors, 'validated');
    const aiResearchedData = computeAveragesForScoreMode(filteredVendors, 'ai_researched');
    
    const categoryLabel = categoryType === 'all' 
        ? 'All Vendors'
        : `${categoryType.toUpperCase()}: ${categoryValue}`;
    
    // Build HTML structure
    let html = `
        <div style="display: flex; flex-direction: column; gap: 12px; padding: 12px;">
            <div style="font-size: 13px; color: var(--text-primary); font-weight: 500; text-align: center;">
                ${categoryLabel} (n=${filteredVendors.length})
            </div>
            <div style="display: flex; gap: 16px; justify-content: center; font-size: 12px; flex-wrap: wrap;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="display: inline-block; width: 12px; height: 2px; background: #107c10;"></span>
                    <span style="color: #107c10;">Validated</span>
                </div>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="display: inline-block; width: 12px; height: 2px; background: #0078d4;"></span>
                    <span style="color: #0078d4;">Researched</span>
                </div>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="display: inline-block; width: 12px; height: 2px; background: #8b5cf6;"></span>
                    <span style="color: #8b5cf6;">AI Researched</span>
                </div>
            </div>
            <div class="validation-comparison-radar-container">
                <div class="validation-comparison-radar-section" style="grid-column: 1 / -1;">
                    <div class="validation-comparison-radar-chart" id="overlay-radar"></div>
                </div>
            </div>
    `;
    
    if (validationComparisonState.showDelta) {
        const pillarAxes = ['PLA', 'INV', 'REM', 'PMG', 'LAW'];
        const subPillarAxes = (appState.subPillars || []).map(s => s.id);
        const axesMode = validationComparisonState.axes || 'pillars';
        const axes = axesMode === 'subpillars'
            ? subPillarAxes
            : axesMode === 'both'
                ? [...pillarAxes, ...subPillarAxes]
                : pillarAxes;
        
        const deltaRows = axes.map(axis => {
            const isSubPillar = !pillarAxes.includes(axis);
            const resValue = isSubPillar ? (researchedData.subPillars[axis] || 0) : (researchedData.pillars[axis] || 0);
            const valValue = isSubPillar ? (validatedData.subPillars[axis] || 0) : (validatedData.pillars[axis] || 0);
            const aiValue = isSubPillar ? (aiResearchedData.subPillars[axis] || 0) : (aiResearchedData.pillars[axis] || 0);
            const deltaRV = valValue - resValue;
            const deltaRA = aiValue - resValue;
            const deltaRVClass = deltaRV > 0.05 ? 'validation-comparison-delta-positive' : deltaRV < -0.05 ? 'validation-comparison-delta-negative' : 'validation-comparison-delta-neutral';
            const deltaRAClass = deltaRA > 0.05 ? 'validation-comparison-delta-positive' : deltaRA < -0.05 ? 'validation-comparison-delta-negative' : 'validation-comparison-delta-neutral';
            
            return `
                <tr>
                    <td>${axis}</td>
                    <td style="color: #107c10;">${valValue.toFixed(2)}</td>
                    <td style="color: #0078d4;">${resValue.toFixed(2)}</td>
                    <td style="color: #8b5cf6;">${aiValue.toFixed(2)}</td>
                    <td class="${deltaRVClass}">${deltaRV > 0 ? '+' : ''}${deltaRV.toFixed(2)}</td>
                    <td class="${deltaRAClass}">${deltaRA > 0 ? '+' : ''}${deltaRA.toFixed(2)}</td>
                </tr>
            `;
        }).join('');
        
        html += `
            <div class="validation-comparison-delta-metrics">
                <div class="validation-comparison-delta-title">Delta Analysis</div>
                <table class="validation-comparison-delta-table">
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th style="color: #107c10;">Valid.</th>
                            <th style="color: #0078d4;">Res.</th>
                            <th style="color: #8b5cf6;">AI Res.</th>
                            <th>Δ V-R</th>
                            <th>Δ AI-R</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${deltaRows}
                    </tbody>
                </table>
            </div>
        `;
    }
    
    html += `</div>`;
    
    container.innerHTML = html;
    
    // Render overlaid radar
    setTimeout(() => {
        const overlayRadar = document.getElementById('overlay-radar');
        
        if (overlayRadar) renderValidationRadarOverlay(overlayRadar, researchedData, validatedData, aiResearchedData);
    }, 0);
}

// Store preview widget sizes for modal
const previewWidgetSizes = {};

function initializeWidgetCustomization() {
    loadWidgetPreferences();
    
    // Apply saved preferences to main dashboard
    document.querySelectorAll('[data-widget]').forEach(widget => {
        const widgetName = widget.getAttribute('data-widget');
        if (!widgetState.visibleWidgets.has(widgetName)) {
            widget.classList.add('hidden');
        }
    });
    
    // Customize button
    const customizeBtn = document.getElementById('customize-widgets-btn');
    const modal = document.getElementById('widget-customization-modal');
    const closeBtn = document.getElementById('modal-close-btn');
    const saveBtn = document.getElementById('save-widgets-btn');
    const cancelBtn = document.getElementById('cancel-widgets-btn');
    
    if (!customizeBtn) return;
    
    customizeBtn.addEventListener('click', () => {
        // Update checkboxes based on current state
        document.querySelectorAll('.widget-checkbox-group input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = widgetState.visibleWidgets.has(checkbox.value);
        });
        // Build preview grid
        buildWidgetPreviewGrid();
        modal.classList.add('active');
    });
    
    closeBtn.addEventListener('click', () => {
        modal.classList.remove('active');
    });
    
    cancelBtn.addEventListener('click', () => {
        modal.classList.remove('active');
    });
    
    saveBtn.addEventListener('click', () => {
        // Update visible widgets based on checkboxes
        document.querySelectorAll('.widget-checkbox-group input[type="checkbox"]').forEach(checkbox => {
            toggleWidget(checkbox.value, checkbox.checked);
        });
        
        // Apply preview sizes to main dashboard
        Object.entries(previewWidgetSizes).forEach(([widgetName, sizes]) => {
            const widget = document.querySelector(`[data-widget="${widgetName}"]`);
            if (widget) {
                widget.setAttribute('data-col-span', sizes.colSpan);
                widget.setAttribute('data-row-span', sizes.rowSpan);
                widget.style.setProperty('--col-span', sizes.colSpan);
                widget.style.setProperty('--row-span', sizes.rowSpan);
                widget.style.minHeight = (300 * sizes.rowSpan + 20 * (sizes.rowSpan - 1)) + 'px';
            }
        });
        
        saveWidgetPreferences();
        modal.classList.remove('active');
    });
    
    // Close modal when clicking outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
}

function buildWidgetPreviewGrid() {
    const previewGrid = document.getElementById('widget-preview-grid');
    previewGrid.innerHTML = '';
    previewWidgetSizes.length = 0; // Clear previous state
    
    let draggedWidget = null;
    let dragOffset = { x: 0, y: 0 };
    
    Object.entries(widgetDefinitions).forEach(([widgetId, widgetTitle]) => {
        const isVisible = widgetState.visibleWidgets.has(widgetId);
        
        // Get current sizes from main dashboard
        const mainWidget = document.querySelector(`[data-widget="${widgetId}"]`);
        const colSpan = mainWidget ? (parseInt(mainWidget.getAttribute('data-col-span')) || 1) : 1;
        const rowSpan = mainWidget ? (parseInt(mainWidget.getAttribute('data-row-span')) || 1) : 1;
        
        // Store preview sizes
        previewWidgetSizes[widgetId] = { colSpan, rowSpan };
        
        const previewWidget = document.createElement('div');
        previewWidget.className = `preview-widget ${!isVisible ? 'disabled' : ''}`;
        previewWidget.setAttribute('data-widget-id', widgetId);
        previewWidget.draggable = !isVisible ? false : true;
        previewWidget.style.setProperty('--col-span', colSpan);
        previewWidget.style.setProperty('--row-span', rowSpan);
        previewWidget.style.gridColumn = `span ${colSpan}`;
        previewWidget.style.gridRow = `span ${rowSpan}`;
        previewWidget.innerHTML = `
            <div style="text-align: center; width: 100%; cursor: grab; user-select: none;">
                <div style="font-weight: 500; margin-bottom: 4px;">⋮⋮ ${widgetTitle}</div>
                <div style="font-size: 10px; color: var(--text-secondary);">${colSpan}×${rowSpan}</div>
            </div>
            <div class="preview-resize-handle"></div>
        `;
        
        previewGrid.appendChild(previewWidget);
        
        // Add drag functionality
        previewWidget.addEventListener('dragstart', (e) => {
            draggedWidget = previewWidget;
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/html', previewWidget.innerHTML);
            previewWidget.style.opacity = '0.5';
        });
        
        previewWidget.addEventListener('dragover', (e) => {
            if (draggedWidget && draggedWidget !== previewWidget && !previewWidget.classList.contains('disabled')) {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                
                // Visual feedback
                previewWidget.style.borderColor = '#0078d4';
                previewWidget.style.borderWidth = '2px';
            }
        });
        
        previewWidget.addEventListener('dragleave', (e) => {
            if (previewWidget !== draggedWidget) {
                previewWidget.style.borderColor = '';
                previewWidget.style.borderWidth = '';
            }
        });
        
        previewWidget.addEventListener('drop', (e) => {
            e.preventDefault();
            if (draggedWidget && draggedWidget !== previewWidget) {
                // Swap the widgets in the DOM
                const draggedId = draggedWidget.getAttribute('data-widget-id');
                const targetId = previewWidget.getAttribute('data-widget-id');
                
                // Store current properties
                const draggedSizes = previewWidgetSizes[draggedId];
                const targetSizes = previewWidgetSizes[targetId];
                
                // Swap positions by swapping in the grid
                previewGrid.insertBefore(draggedWidget, previewWidget);
            }
        });
        
        previewWidget.addEventListener('dragend', (e) => {
            if (draggedWidget) {
                draggedWidget.style.opacity = '1';
                draggedWidget.style.borderColor = '';
                draggedWidget.style.borderWidth = '';
            }
            draggedWidget = null;
        });
        
        // Add resize functionality to preview widget
        const resizeHandle = previewWidget.querySelector('.preview-resize-handle');
        resizeHandle.addEventListener('mousedown', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const startX = e.clientX;
            const startY = e.clientY;
            const startColSpan = previewWidgetSizes[widgetId].colSpan;
            const startRowSpan = previewWidgetSizes[widgetId].rowSpan;
            
            function handleMouseMove(moveEvent) {
                const deltaX = moveEvent.clientX - startX;
                const deltaY = moveEvent.clientY - startY;
                
                // Each grid cell is approximately 100px (3 columns in ~300px area)
                let newColSpan = startColSpan + Math.round(deltaX / 110);
                let newRowSpan = startRowSpan + Math.round(deltaY / 110);
                
                // Clamp values
                newColSpan = Math.max(1, Math.min(3, newColSpan));
                newRowSpan = Math.max(1, Math.min(2, newRowSpan));
                
                previewWidget.style.gridColumn = `span ${newColSpan}`;
                previewWidget.style.gridRow = `span ${newRowSpan}`;
                
                // Update size indicator
                const sizeDiv = previewWidget.querySelector('div:last-of-type');
                if (sizeDiv) {
                    sizeDiv.innerHTML = `${newColSpan}×${newRowSpan}`;
                }
                
                // Update stored size
                previewWidgetSizes[widgetId] = { colSpan: newColSpan, rowSpan: newRowSpan };
            }
            
            function handleMouseUp() {
                document.removeEventListener('mousemove', handleMouseMove);
                document.removeEventListener('mouseup', handleMouseUp);
            }
            
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
        });
    });
}

// Query Builder State
const queryBuilderState = {
    filters: [] // Array of {field, operator, value}
};

// Define available fields and their operators
const queryBuilderFields = {
    vendor: {
        label: 'Vendor Name',
        operators: ['contains', 'equals', 'does not equal'],
        type: 'text'
    },
    region: {
        label: 'Region',
        operators: ['equals', 'does not equal', 'contains'],
        type: 'select',
        values: []
    },
    specialization: {
        label: 'Specialization',
        operators: ['contains', 'equals', 'does not equal'],
        type: 'select',
        values: []
    },
    ir_focus_type: {
        label: 'IR Focus Type',
        operators: ['equals', 'does not equal', 'contains'],
        type: 'select',
        values: []
    },
    is_ai_first: {
        label: 'AI-First',
        operators: ['yes', 'no'],
        type: 'boolean'
    },
    is_startup: {
        label: 'Startup',
        operators: ['yes', 'no'],
        type: 'boolean'
    },
    pillar: {
        label: 'Pillar',
        operators: ['equals', 'does not equal'],
        type: 'select',
        values: [
            { label: 'Planning & Preparation', value: 'PLA' },
            { label: 'Forensic Investigation', value: 'INV' },
            { label: 'Remediation', value: 'REM' },
            { label: 'Program Management', value: 'PMG' },
            { label: 'Criminal Proceedings', value: 'LAW' }
        ]
    },
    'PLA': {
        label: 'Planning & Preparation (Pillar Score)',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'INV': {
        label: 'Forensic Investigation (Pillar Score)',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'REM': {
        label: 'Remediation (Pillar Score)',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'PMG': {
        label: 'Program Management (Pillar Score)',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'LAW': {
        label: 'Criminal Proceedings (Pillar Score)',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'PLA-01': {
        label: 'Visibility Gap Analysis',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'PLA-02': {
        label: 'Behavioral Playbook Design',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'PLA-03': {
        label: 'Tabletop Exercise Automation',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'PLA-04': {
        label: 'Forensic Readiness Assessment',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'INV-01': {
        label: 'Triage and Scoping',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'INV-02': {
        label: 'Multi-Hop Timeline Reconstruction',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'INV-03': {
        label: 'Artifact Source Attribution',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'INV-04': {
        label: 'Malware and Reverse Engineering',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'REM-01': {
        label: 'Containment and Isolation',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'REM-02': {
        label: 'Root Cause Eradication',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'REM-03': {
        label: 'Recovery and Restoration',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'REM-04': {
        label: 'Ransomware Negotiation',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'PMG-01': {
        label: 'Incident Coordination',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'PMG-02': {
        label: 'Forensic Quality Management',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'PMG-03': {
        label: 'Crisis Communication',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'PMG-04': {
        label: 'Post-Incident Learning',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'LAW-01': {
        label: 'Evidence Collection & Preservation',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'LAW-02': {
        label: 'Expert Witness Support',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'LAW-03': {
        label: 'Machine-Inclusive Chain of Custody',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    },
    'LAW-04': {
        label: 'Admissibility Defense',
        operators: ['=', '<', '>', '<=', '>=', '<>'],
        type: 'numeric'
    }
};

function initializeAnalyticsTab() {
    // Only initialize once - check if already initialized
    if (window.analyticsInitialized) {
        updateAnalytics();
        return;
    }
    
    // Initialize widget customization
    initializeWidgetCustomization();
    
    // Populate field values
    const regions = [...new Set(appState.vendors.map(v => v.region))].sort();
    const specializations = [...new Set(appState.vendors.map(v => v.specialization))].sort();
    const types = [...new Set(appState.vendors.map(v => v.ir_focus_type))].sort();
    
    queryBuilderFields.region.values = regions;
    queryBuilderFields.specialization.values = specializations;
    queryBuilderFields.ir_focus_type.values = types;
    
    // Setup field selector buttons (only once)
    document.querySelectorAll('.field-selector-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const field = btn.dataset.field;
            addQueryFilter(field);
        });
    });
    
    // Reset button
    document.getElementById('add-filter-btn')?.addEventListener('click', () => {
        // This button is hidden for now, filters are added via field selector
    });
    
    // Mark as initialized
    window.analyticsInitialized = true;
    
    // Initial render
    renderQueryFilters();
    initializeComparisonRadarWidget();
    initializeValidationComparisonWidget();
    populateComparisonRadarDropdowns();
    renderValidationComparison();
    updateAnalytics();
}

function addQueryFilter(field) {
    // Add a new filter row with default operator
    const fieldConfig = queryBuilderFields[field];
    if (!fieldConfig) return;
    
    const operators = fieldConfig.operators;
    queryBuilderState.filters.push({
        logicalOperator: queryBuilderState.filters.length > 0 ? 'AND' : null,
        field: field,
        operator: operators[0],
        value: ''
    });
    
    renderQueryFilters();
}

function removeQueryFilter(index) {
    queryBuilderState.filters.splice(index, 1);
    renderQueryFilters();
    updateAnalytics();
}

function updateQueryFilter(index, property, value) {
    if (queryBuilderState.filters[index]) {
        queryBuilderState.filters[index][property] = value;
        updateAnalytics();
    }
}

function renderQueryFilters() {
    const container = document.getElementById('query-filters');
    container.innerHTML = '';
    
    if (queryBuilderState.filters.length === 0) {
        container.innerHTML = '<div class="no-filters-message">No filters applied. Select a field from the left to add filters.</div>';
        return;
    }
    
    queryBuilderState.filters.forEach((filter, index) => {
        const fieldConfig = queryBuilderFields[filter.field];
        if (!fieldConfig) return;
        
        const row = document.createElement('div');
        row.className = 'query-filter-row';
        
        // Logical operator (AND/OR) - only for filters after the first
        if (filter.logicalOperator) {
            const logicalOpSelect = document.createElement('select');
            logicalOpSelect.className = 'filter-logical-op';
            ['AND', 'OR'].forEach(op => {
                const option = document.createElement('option');
                option.value = op;
                option.textContent = op;
                if (op === filter.logicalOperator) option.selected = true;
                logicalOpSelect.appendChild(option);
            });
            logicalOpSelect.addEventListener('change', (e) => {
                updateQueryFilter(index, 'logicalOperator', e.target.value);
            });
            row.appendChild(logicalOpSelect);
        }
        
        // Field select
        const fieldSelect = document.createElement('select');
        fieldSelect.className = 'filter-field';
        Object.entries(queryBuilderFields).forEach(([key, config]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = config.label;
            if (key === filter.field) option.selected = true;
            fieldSelect.appendChild(option);
        });
        fieldSelect.addEventListener('change', (e) => {
            updateQueryFilter(index, 'field', e.target.value);
            renderQueryFilters();
        });
        
        // Operator select
        const operatorSelect = document.createElement('select');
        operatorSelect.className = 'filter-operator';
        fieldConfig.operators.forEach(op => {
            const option = document.createElement('option');
            option.value = op;
            option.textContent = op.charAt(0).toUpperCase() + op.slice(1);
            if (op === filter.operator) option.selected = true;
            operatorSelect.appendChild(option);
        });
        operatorSelect.addEventListener('change', (e) => {
            updateQueryFilter(index, 'operator', e.target.value);
        });
        
        // Value input/select
        let valueInput;
        if (fieldConfig.type === 'boolean') {
            valueInput = document.createElement('select');
            valueInput.className = 'filter-value';
            ['Yes', 'No'].forEach((val, i) => {
                const option = document.createElement('option');
                option.value = i === 0;
                option.textContent = val;
                if (String(filter.value) === String(i === 0)) option.selected = true;
                valueInput.appendChild(option);
            });
        } else if (fieldConfig.type === 'numeric') {
            valueInput = document.createElement('input');
            valueInput.className = 'filter-value';
            valueInput.type = 'number';
            valueInput.placeholder = 'Enter value (1-5)...';
            valueInput.min = '1';
            valueInput.max = '5';
            valueInput.value = filter.value;
        } else if (fieldConfig.type === 'select' && fieldConfig.values.length > 0) {
            valueInput = document.createElement('select');
            valueInput.className = 'filter-value';
            fieldConfig.values.forEach(val => {
                const option = document.createElement('option');
                // Handle both simple string values and object values (for pillar with label/value)
                if (typeof val === 'object') {
                    option.value = val.value;
                    option.textContent = val.label;
                    if (val.value === filter.value) option.selected = true;
                } else {
                    option.value = val;
                    option.textContent = val;
                    if (val === filter.value) option.selected = true;
                }
                valueInput.appendChild(option);
            });
        } else {
            valueInput = document.createElement('input');
            valueInput.className = 'filter-value';
            valueInput.type = 'text';
            valueInput.placeholder = 'Enter value...';
            valueInput.value = filter.value;
        }
        valueInput.addEventListener('change', (e) => {
            updateQueryFilter(index, 'value', e.target.value);
        });
        
        // Remove button
        const removeBtn = document.createElement('button');
        removeBtn.className = 'remove-filter-btn';
        removeBtn.textContent = '✕';
        removeBtn.addEventListener('click', () => removeQueryFilter(index));
        
        row.appendChild(fieldSelect);
        row.appendChild(operatorSelect);
        row.appendChild(valueInput);
        row.appendChild(removeBtn);
        
        container.appendChild(row);
    });
}

function updateAnalytics() {
    // Filter vendors based on query builder filters with logical operators (AND/OR)
    let filtered = appState.vendors;
    
    if (queryBuilderState.filters.length > 0) {
        filtered = filtered.filter(vendor => {
            let result = true;
            
            for (let i = 0; i < queryBuilderState.filters.length; i++) {
                const filter = queryBuilderState.filters[i];
                
                // Get vendor value - handle special cases for pillar scores, pillar, and nested granular_mapping for capabilities
                let vendorValue;
                
                if (['PLA', 'INV', 'REM', 'PMG', 'LAW'].includes(filter.field)) {
                    // Pillar score fields: prefer validated/computed pillar scores
                    vendorValue = getEffectivePillarScores(vendor)?.[filter.field];
                } else if (filter.field === 'pillar') {
                    // Check if vendor has the pillar score
                    vendorValue = getEffectivePillarScores(vendor)?.[filter.value] ? filter.value : null;
                } else if (['PLA-01', 'PLA-02', 'PLA-03', 'PLA-04', 
                     'INV-01', 'INV-02', 'INV-03', 'INV-04',
                     'REM-01', 'REM-02', 'REM-03', 'REM-04',
                     'PMG-01', 'PMG-02', 'PMG-03', 'PMG-04',
                     'LAW-01', 'LAW-02', 'LAW-03', 'LAW-04'].includes(filter.field)) {
                    // Extract pillar code (first 3 chars, e.g., "PLA" from "PLA-01")
                    const pillarCode = filter.field.substring(0, 3);
                    vendorValue = getEffectiveGranularMapping(vendor)?.[pillarCode]?.[filter.field];
                } else {
                    vendorValue = vendor[filter.field];
                }
                
                const filterValue = filter.value;
                let filterMatches = false;
                
                switch (filter.operator) {
                    case 'equals':
                        filterMatches = String(vendorValue) === String(filterValue);
                        break;
                    case 'does not equal':
                        filterMatches = String(vendorValue) !== String(filterValue);
                        break;
                    case 'contains':
                        filterMatches = String(vendorValue).toLowerCase().includes(String(filterValue).toLowerCase());
                        break;
                    case 'does not contain':
                        filterMatches = !String(vendorValue).toLowerCase().includes(String(filterValue).toLowerCase());
                        break;
                    case '=':
                        filterMatches = Number(vendorValue) === Number(filterValue);
                        break;
                    case '<':
                        filterMatches = Number(vendorValue) < Number(filterValue);
                        break;
                    case '>':
                        filterMatches = Number(vendorValue) > Number(filterValue);
                        break;
                    case '<=':
                        filterMatches = Number(vendorValue) <= Number(filterValue);
                        break;
                    case '>=':
                        filterMatches = Number(vendorValue) >= Number(filterValue);
                        break;
                    case '<>':
                        filterMatches = Number(vendorValue) !== Number(filterValue);
                        break;
                    default:
                        filterMatches = true;
                }
                
                // Apply logical operator
                if (i === 0) {
                    result = filterMatches;
                } else {
                    const logicalOp = filter.logicalOperator;
                    if (logicalOp === 'AND') {
                        result = result && filterMatches;
                    } else if (logicalOp === 'OR') {
                        result = result || filterMatches;
                    }
                }
            }
            
            return result;
        });
    }
    
    const filteredVendors = filtered;
    
    // Update statistics
    const totalCount = filteredVendors.length;
    const aiFirstCount = filteredVendors.filter(v => v.is_ai_first).length;
    const startupCount = filteredVendors.filter(v => v.is_startup).length;
    
    // Calculate average scores (score-mode-aware)
    let totalScore = 0;
    let scoreCount = 0;
    filteredVendors.forEach(v => {
        const scores = getEffectivePillarScores(v) || {};
        Object.values(scores).forEach(score => {
            if (score) {
                totalScore += score;
                scoreCount++;
            }
        });
    });
    const avgScore = scoreCount > 0 ? (totalScore / scoreCount).toFixed(2) : 0;
    
    // Update stat displays
    document.getElementById('analysis-stat-count').textContent = totalCount;
    document.getElementById('analysis-stat-avg-score').textContent = avgScore;
    document.getElementById('analysis-stat-ai-pct').textContent = 
        totalCount > 0 ? ((aiFirstCount / totalCount) * 100).toFixed(0) + '%' : '0%';
    document.getElementById('analysis-stat-startup-pct').textContent = 
        totalCount > 0 ? ((startupCount / totalCount) * 100).toFixed(0) + '%' : '0%';
    
    // Update charts
    renderAnalyticsRegionChart(filteredVendors);
    renderAnalyticsPillarChart(filteredVendors);
    renderAnalyticsPillarRadarChart(filteredVendors);
    renderAnalyticsSpecializationChart(filteredVendors);
    renderAnalyticsTypeChart(filteredVendors);
    renderAnalyticsAIChart(filteredVendors);
    renderAnalyticsStartupChart(filteredVendors);
    renderValidationComparison(filteredVendors);
}

function renderAnalyticsRegionChart(vendors) {
    const regionDist = {};
    vendors.forEach(v => {
        regionDist[v.region] = (regionDist[v.region] || 0) + 1;
    });
    
    const sorted = Object.entries(regionDist).sort((a, b) => b[1] - a[1]);
    const maxValue = Math.max(...sorted.map(d => d[1]));
    const chart = document.getElementById('analysis-region-chart');
    
    chart.innerHTML = sorted.map(([region, count]) => {
        const percentage = (count / maxValue) * 100;
        return `
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-size: 12px;">${region}</span>
                    <span style="font-size: 12px; font-weight: bold;">${count}</span>
                </div>
                <div style="height: 24px; background: var(--bg-tertiary); border-radius: 4px; overflow: hidden;">
                    <div style="height: 100%; width: ${percentage}%; background: linear-gradient(90deg, #0078d4, #107c10);"></div>
                </div>
            </div>
        `;
    }).join('');
}

function renderAnalyticsPillarChart(vendors) {
    const pillarAvgs = { PLA: 0, INV: 0, REM: 0, PMG: 0, LAW: 0 };
    const pillarCounts = { PLA: 0, INV: 0, REM: 0, PMG: 0, LAW: 0 };
    
    // Initialize sub-pillar tracking
    const subPillarAvgs = {};
    const subPillarCounts = {};
    ['PLA', 'INV', 'REM', 'PMG', 'LAW'].forEach(pillar => {
        for (let i = 1; i <= 4; i++) {
            const code = `${pillar}-0${i}`;
            subPillarAvgs[code] = 0;
            subPillarCounts[code] = 0;
        }
    });
    
    vendors.forEach(v => {
        const granularMapping = getEffectiveGranularMapping(v);
        
        // Calculate pillar averages
        Object.keys(pillarAvgs).forEach(p => {
            const score = computePillarScoreFromGranular(v, p);
            if (score !== null && score !== undefined && score !== '') {
                pillarAvgs[p] += Number(score);
                pillarCounts[p]++;
            }
        });
        
        // Calculate sub-pillar averages from granular_mapping
        Object.keys(granularMapping).forEach(pillar => {
            const pillarData = granularMapping[pillar];
            if (pillarData && typeof pillarData === 'object') {
                for (let i = 1; i <= 4; i++) {
                    const code = `${pillar}-0${i}`;
                    const fieldName = ['visibility', 'behavior', 'tabletop', 'forensic'][i - 1] ||
                                    ['triage', 'timeline', 'artifact', 'malware'][i - 1] ||
                                    ['containment', 'eradication', 'recovery', 'ransomware'][i - 1] ||
                                    ['coordination', 'comms', 'legal', 'insurance'][i - 1] ||
                                    ['compliance', 'audit', 'training', 'policy'][i - 1];
                    
                    const value = pillarData[fieldName] || pillarData[code];
                    if (value !== undefined && value !== null && value !== '' && !Number.isNaN(Number(value))) {
                        subPillarAvgs[code] += Number(value) || 0;
                        subPillarCounts[code]++;
                    }
                }
            }
        });
    });
    
    Object.keys(pillarAvgs).forEach(p => {
        pillarAvgs[p] = pillarCounts[p] > 0 ? (pillarAvgs[p] / pillarCounts[p]).toFixed(2) : 0;
    });
    
    Object.keys(subPillarAvgs).forEach(code => {
        subPillarAvgs[code] = subPillarCounts[code] > 0 ? (subPillarAvgs[code] / subPillarCounts[code]).toFixed(2) : 0;
    });
    
    const chart = document.getElementById('analysis-pillar-chart');
    const pillars = Object.entries(pillarAvgs).sort((a, b) => b[1] - a[1]);
    
    // Define pillar names and sub-pillars
    const pillarNames = {
        'PLA': 'Planning & Preparation',
        'INV': 'Forensic Investigation',
        'REM': 'Remediation & Recovery',
        'PMG': 'Post-Incident Management',
        'LAW': 'Legal & Compliance'
    };
    
    const subPillarMapping = {
        'PLA': ['PLA-01', 'PLA-02', 'PLA-03', 'PLA-04'],
        'INV': ['INV-01', 'INV-02', 'INV-03', 'INV-04'],
        'REM': ['REM-01', 'REM-02', 'REM-03', 'REM-04'],
        'PMG': ['PMG-01', 'PMG-02', 'PMG-03', 'PMG-04'],
        'LAW': ['LAW-01', 'LAW-02', 'LAW-03', 'LAW-04']
    };
    
    chart.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px;">
            ${pillars.map(([pillar, avg]) => `
                <div>
                    <!-- Pillar -->
                    <div style="text-align: center; margin-bottom: 8px; cursor: help; padding: 8px; border-radius: 4px; transition: background-color 0.2s;" title="${pillarNames[pillar]}">
                        <div style="font-size: 20px; font-weight: bold; color: var(--color-primary);">${avg}</div>
                        <div style="font-size: 12px; color: var(--text-secondary); font-weight: 600; margin-top: 4px;">${pillar}</div>
                    </div>
                    
                    <!-- Sub-pillars -->
                    <div style="font-size: 10px; border-top: 1px solid var(--border-color); padding-top: 8px;">
                        ${(subPillarMapping[pillar] || []).map(subPillarCode => {
                            const subPillarLabel = queryBuilderFields[subPillarCode]?.label || subPillarCode;
                            const subPillarAvg = subPillarAvgs[subPillarCode] || 0;
                            return `
                                <div style="display: flex; justify-content: space-between; align-items: center; padding: 4px 0; cursor: help;" title="${subPillarLabel}">
                                    <span style="color: var(--text-secondary);">${subPillarCode}</span>
                                    <span style="color: var(--text-primary); font-weight: 500;">${subPillarAvg}</span>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function renderAnalyticsPillarRadarChart(vendors) {
    const chart = document.getElementById('analysis-pillar-radar-chart');
    if (!chart) return;
    
    // Check for existing toggle state or create it
    if (!window.radarChartState) {
        window.radarChartState = {
            showSubPillars: true,
            showPillars: true,
            layers: { validated: true, researched: true, ai_researched: true }
        };
    }
    // Ensure layers exist for older state
    if (!window.radarChartState.layers) {
        window.radarChartState.layers = { validated: true, researched: true, ai_researched: true };
    }
    
    const scoreLayers = [
        { key: 'validated', label: 'Validated', color: '#107c10', fillColor: 'rgba(16, 124, 16, 0.15)' },
        { key: 'researched', label: 'Researched', color: '#0078d4', fillColor: 'rgba(0, 120, 212, 0.15)' },
        { key: 'ai_researched', label: 'AI Researched', color: '#8b5cf6', fillColor: 'rgba(139, 92, 246, 0.15)' }
    ];
    
    // Compute averages per score layer
    const layerData = {};
    scoreLayers.forEach(layer => {
        layerData[layer.key] = computeAveragesForScoreMode(vendors, layer.key);
    });
    
    // Sub-pillar labels lookup
    const subPillarLabels = {};
    ['PLA', 'INV', 'REM', 'PMG', 'LAW'].forEach(pillar => {
        for (let i = 1; i <= 4; i++) {
            const code = `${pillar}-0${i}`;
            subPillarLabels[code] = queryBuilderFields[code]?.label || code;
        }
    });
    
    // Create SVG radar chart with sub-pillars
    const size = Math.min(chart.offsetWidth - 40, chart.offsetHeight - 40);
    const center = size / 2;
    const radius = (size / 2) * 0.75;
    const levels = 5;
    const maxValue = 5;
    
    // All sub-pillars in order
    const subPillars = [];
    const pillarList = ['PLA', 'INV', 'REM', 'PMG', 'LAW'];
    pillarList.forEach(pillar => {
        for (let i = 1; i <= 4; i++) {
            subPillars.push(`${pillar}-0${i}`);
        }
    });
    
    const angles = subPillars.map((_, i) => (i * 2 * Math.PI) / subPillars.length - Math.PI / 2);
    
    // Create container for controls and chart
    let html = `
        <div style="padding: 12px 0;">
            <div style="display: flex; gap: 12px; margin-bottom: 8px; justify-content: center; flex-wrap: wrap;">
                <label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px; color: var(--text-primary);">
                    <input type="checkbox" id="radar-show-subpillars" ${window.radarChartState.showSubPillars ? 'checked' : ''} style="cursor: pointer;">
                    <span>Sub-Pillars</span>
                </label>
                <label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px; color: var(--text-primary);">
                    <input type="checkbox" id="radar-show-pillars" ${window.radarChartState.showPillars ? 'checked' : ''} style="cursor: pointer;">
                    <span>Pillars</span>
                </label>
            </div>
            <div style="display: flex; gap: 12px; margin-bottom: 12px; justify-content: center; flex-wrap: wrap; border-top: 1px solid var(--border-color); padding-top: 8px;">
                <span style="font-size: 11px; color: var(--text-secondary); font-weight: 600;">Score Layers:</span>
                ${scoreLayers.map(layer => `
                    <label style="display: flex; align-items: center; gap: 5px; cursor: pointer; font-size: 12px;">
                        <input type="checkbox" id="radar-layer-${layer.key}" ${window.radarChartState.layers[layer.key] ? 'checked' : ''} style="cursor: pointer; accent-color: ${layer.color};">
                        <span style="color: ${layer.color}; font-weight: 500;">${layer.label}</span>
                    </label>
                `).join('')}
            </div>
        </div>
    `;
    
    let svg = `<svg width="${size + 40}" height="${size + 40}" style="margin: auto; display: block;">`;
    svg += `<defs><style>
        .sub-pillar-label { font-size: 9px; }
        .pillar-label { font-size: 11px; font-weight: 600; }
        .level-label { font-size: 9px; fill: var(--text-secondary); }
    </style></defs>`;
    
    // Draw center point (0)
    svg += `<circle cx="${center + 20}" cy="${center + 20}" r="2" fill="var(--text-secondary)" opacity="0.5"/>`;
    svg += `<text x="${center + 20 - 8}" y="${center + 20 - 5}" class="level-label" font-size="8">0</text>`;
    
    // Draw level circles and labels
    for (let i = 1; i <= levels; i++) {
        const r = (radius * i) / levels;
        svg += `<circle cx="${center + 20}" cy="${center + 20}" r="${r}" stroke="var(--border-color)" stroke-width="1" fill="none" opacity="0.3"/>`;
        
        // Add level labels (1 at innermost, 5 at outermost)
        const levelValue = i;
        svg += `<text x="${center + 20 + r + 3}" y="${center + 20 - 3}" class="level-label">${levelValue}</text>`;
    }
    
    // Draw grid lines
    angles.forEach((angle) => {
        const x1 = center + 20;
        const y1 = center + 20;
        const x2 = center + 20 + radius * Math.cos(angle);
        const y2 = center + 20 + radius * Math.sin(angle);
        
        svg += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="var(--border-color)" stroke-width="0.5" opacity="0.3"/>`;
    });
    
    // Draw polygons for each enabled score layer
    const enabledLayers = scoreLayers.filter(l => window.radarChartState.layers[l.key]);
    
    enabledLayers.forEach(layer => {
        const data = layerData[layer.key];
        
        // Draw sub-pillar polygon - conditional
        if (window.radarChartState.showSubPillars) {
            let subPillarPathData = '';
            angles.forEach((angle, i) => {
                const value = parseFloat(data.subPillars[subPillars[i]] || 0);
                const scaledRadius = (value / maxValue) * radius;
                const x = center + 20 + scaledRadius * Math.cos(angle);
                const y = center + 20 + scaledRadius * Math.sin(angle);
                subPillarPathData += (i === 0 ? 'M' : 'L') + x + ',' + y;
            });
            subPillarPathData += 'Z';
            
            svg += `<path d="${subPillarPathData}" stroke="${layer.color}" stroke-width="2" fill="${layer.fillColor}" stroke-dasharray="${layer.key === 'ai_researched' ? '6,3' : layer.key === 'researched' ? '4,2' : 'none'}"/>`;
        }
        
        // Draw pillar overlay polygon - conditional
        if (window.radarChartState.showPillars && !window.radarChartState.showSubPillars) {
            let pillarPathData = '';
            const pillarSubcount = 4;
            angles.forEach((angle, i) => {
                const pillarIndex = Math.floor(i / pillarSubcount);
                const pillar = pillarList[pillarIndex];
                const value = parseFloat(data.pillars[pillar] || 0);
                const scaledRadius = (value / maxValue) * radius;
                const x = center + 20 + scaledRadius * Math.cos(angle);
                const y = center + 20 + scaledRadius * Math.sin(angle);
                pillarPathData += (i === 0 ? 'M' : 'L') + x + ',' + y;
            });
            pillarPathData += 'Z';
            
            svg += `<path d="${pillarPathData}" stroke="${layer.color}" stroke-width="2" fill="${layer.fillColor}" stroke-dasharray="${layer.key === 'ai_researched' ? '6,3' : layer.key === 'researched' ? '4,2' : 'none'}"/>`;
        }
    });
    
    // Add pillar labels (at the midpoint of each pillar's sub-pillars)
    pillarList.forEach((pillar, pillarIdx) => {
        const startIdx = pillarIdx * 4;
        const midIdx = startIdx + 2;
        const midAngle = angles[midIdx];
        const labelRadius = radius + 50;
        const labelX = center + 20 + labelRadius * Math.cos(midAngle);
        const labelY = center + 20 + labelRadius * Math.sin(midAngle);
        
        svg += `<text x="${labelX}" y="${labelY}" text-anchor="middle" dominant-baseline="middle" class="pillar-label" fill="var(--color-primary)" cursor="help" title="${pillar}">${pillar}</text>`;
    });
    
    // Add sub-pillar labels around the radar
    angles.forEach((angle, i) => {
        const labelRadius = radius + 30;
        const labelX = center + 20 + labelRadius * Math.cos(angle);
        const labelY = center + 20 + labelRadius * Math.sin(angle);
        const subPillarCode = subPillars[i];
        
        svg += `<text x="${labelX}" y="${labelY}" text-anchor="middle" dominant-baseline="middle" class="sub-pillar-label" fill="var(--text-secondary)" cursor="help" title="${subPillarLabels[subPillarCode]}">${subPillarCode}</text>`;
    });
    
    // Add dots for each enabled layer
    enabledLayers.forEach(layer => {
        const data = layerData[layer.key];
        
        // Add sub-pillar value dots - conditional
        if (window.radarChartState.showSubPillars) {
            angles.forEach((angle, i) => {
                const value = parseFloat(data.subPillars[subPillars[i]] || 0);
                const scaledRadius = (value / maxValue) * radius;
                const x = center + 20 + scaledRadius * Math.cos(angle);
                const y = center + 20 + scaledRadius * Math.sin(angle);
                
                svg += `<circle cx="${x}" cy="${y}" r="3" fill="${layer.color}" stroke="white" stroke-width="1.5"/>`;
            });
        }
        
        // Add pillar value dots - conditional
        if (window.radarChartState.showPillars && !window.radarChartState.showSubPillars) {
            pillarList.forEach((pillar, pillarIdx) => {
                const startIdx = pillarIdx * 4;
                const midIdx = startIdx + 2;
                const midAngle = angles[midIdx];
                const value = parseFloat(data.pillars[pillar] || 0);
                const scaledRadius = (value / maxValue) * radius;
                const x = center + 20 + scaledRadius * Math.cos(midAngle);
                const y = center + 20 + scaledRadius * Math.sin(midAngle);
                
                svg += `<circle cx="${x}" cy="${y}" r="3.5" fill="${layer.color}" stroke="white" stroke-width="1.5"/>`;
            });
        }
    });
    
    svg += `</svg>`;
    
    html += svg;
    
    chart.innerHTML = html;
    
    // Add toggle event listeners
    setTimeout(() => {
        const subPillarsCheckbox = document.getElementById('radar-show-subpillars');
        const pillarsCheckbox = document.getElementById('radar-show-pillars');
        
        if (subPillarsCheckbox) {
            subPillarsCheckbox.addEventListener('change', (e) => {
                window.radarChartState.showSubPillars = e.target.checked;
                renderAnalyticsPillarRadarChart(vendors);
            });
        }
        
        if (pillarsCheckbox) {
            pillarsCheckbox.addEventListener('change', (e) => {
                window.radarChartState.showPillars = e.target.checked;
                renderAnalyticsPillarRadarChart(vendors);
            });
        }
        
        // Score layer checkboxes
        scoreLayers.forEach(layer => {
            const cb = document.getElementById(`radar-layer-${layer.key}`);
            if (cb) {
                cb.addEventListener('change', (e) => {
                    window.radarChartState.layers[layer.key] = e.target.checked;
                    renderAnalyticsPillarRadarChart(vendors);
                });
            }
        });
    }, 100);
}

function renderAnalyticsSpecializationChart(vendors) {
    const specDist = {};
    vendors.forEach(v => {
        specDist[v.specialization] = (specDist[v.specialization] || 0) + 1;
    });
    
    const sorted = Object.entries(specDist).sort((a, b) => b[1] - a[1]).slice(0, 8);
    const chart = document.getElementById('analysis-specialization-chart');
    
    chart.innerHTML = sorted.map(([spec, count]) => `
        <div style="margin-bottom: 12px; font-size: 12px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span>${spec}</span>
                <span style="font-weight: bold;">${count}</span>
            </div>
        </div>
    `).join('');
}

function renderAnalyticsTypeChart(vendors) {
    const typeDist = {};
    vendors.forEach(v => {
        typeDist[v.ir_focus_type] = (typeDist[v.ir_focus_type] || 0) + 1;
    });
    
    const chart = document.getElementById('analysis-type-chart');
    const total = vendors.length;
    
    chart.innerHTML = Object.entries(typeDist).map(([type, count]) => {
        const percentage = (count / total) * 100;
        return `
            <div style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-size: 12px;">${type}</span>
                    <span style="font-size: 12px; font-weight: bold;">${count} (${percentage.toFixed(0)}%)</span>
                </div>
                <div style="height: 24px; background: var(--bg-tertiary); border-radius: 4px; overflow: hidden;">
                    <div style="height: 100%; width: ${percentage}%; background: linear-gradient(90deg, #ffb900, #107c10);"></div>
                </div>
            </div>
        `;
    }).join('');
}

function renderAnalyticsAIChart(vendors) {
    const aiCount = vendors.filter(v => v.is_ai_first).length;
    const nonAiCount = vendors.length - aiCount;
    const chart = document.getElementById('analysis-ai-chart');
    
    const aiPct = vendors.length > 0 ? (aiCount / vendors.length) * 100 : 0;
    
    chart.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
            <div style="text-align: center;">
                <div style="font-size: 28px; font-weight: bold; color: #0078d4;">${aiCount}</div>
                <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">AI-First</div>
                <div style="font-size: 14px; color: var(--text-primary); margin-top: 8px; font-weight: 600;">${aiPct.toFixed(0)}%</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 28px; font-weight: bold; color: #605e5c;">${nonAiCount}</div>
                <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Traditional</div>
                <div style="font-size: 14px; color: var(--text-primary); margin-top: 8px; font-weight: 600;">${(100 - aiPct).toFixed(0)}%</div>
            </div>
        </div>
    `;
}

function renderAnalyticsStartupChart(vendors) {
    const startupCount = vendors.filter(v => v.is_startup).length;
    const establishedCount = vendors.length - startupCount;
    const chart = document.getElementById('analysis-startup-chart');
    
    const startupPct = vendors.length > 0 ? (startupCount / vendors.length) * 100 : 0;
    
    chart.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
            <div style="text-align: center;">
                <div style="font-size: 28px; font-weight: bold; color: #107c10;">${startupCount}</div>
                <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Startups</div>
                <div style="font-size: 14px; color: var(--text-primary); margin-top: 8px; font-weight: 600;">${startupPct.toFixed(0)}%</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 28px; font-weight: bold; color: #605e5c;">${establishedCount}</div>
                <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Established</div>
                <div style="font-size: 14px; color: var(--text-primary); margin-top: 8px; font-weight: 600;">${(100 - startupPct).toFixed(0)}%</div>
            </div>
        </div>
    `;
}

function resetAnalyticsFilters() {
    document.getElementById('analysis-region-filter').value = '';
    document.getElementById('analysis-specialization-filter').value = '';
    document.getElementById('analysis-type-filter').value = '';
    document.getElementById('analysis-ai-first-filter').checked = false;
    document.getElementById('analysis-startup-filter').checked = false;
    updateAnalytics();
}