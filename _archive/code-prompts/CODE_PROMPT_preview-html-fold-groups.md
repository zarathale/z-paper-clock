---
status: shipped
started: 2026-05-10
shipped: 2026-05-10
owner: Zarathale (Alan)
target: preview-html-fold-groups
---

_Shipped 2026-05-10; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md / claude-work/STATUS.md for current state._

## What You Are Doing and Why

The Bench-mode fold panel in `preview.html` renders all of a piece's folds as a flat,
alphabetically-ordered slider list. For simple pieces (5–8 folds) this is fine. For
piece 066 — a 7-pane wrap strip that closes into a tube — it breaks down: 22 sliders
appear undifferentiated, making it impossible to tune the ring geometry (6 pane-to-pane
folds that must collectively sum to 360°) without hunting through the list, and
impossible to move all 7 tab flaps together in one gesture.

This prompt adds **automatic fold-group detection and grouped rendering** to the
`renderPanelsFirstScene` fold slider builder. When the parser produces fold IDs that
match known naming patterns (pane-strip, tab-flap, cross-piece), the slider panel
reorganises into labelled collapsible sections with group-level controls. Pieces with
no recognised patterns fall back silently to the existing flat list — no regression.

The driving use case is piece 066 in Bench mode. The feature is generic and will
naturally benefit any future strip-style piece that follows the same layer conventions.

## Prerequisites — confirm before starting

- `preview.html` exists at repo root, passes `node --check preview.html`
- `work/pieces/066/066.svg` exists and has fold IDs matching the patterns listed in Task 1
- No in-flight `claude/preview-html-fold-groups` branch already open

## Read These Files First

1. `preview.html` — full file; focus on:
   - CSS block starting at line ~41 (`#fold-controls` and siblings)
   - `createSliderRow` at line ~584
   - HTML for `#fold-controls` / `#per-fold-sliders` at line ~347
   - `renderPanelsFirstScene` fold slider section: lines ~5841–5948
   - The `pathHingeMap` wiring and how `items` drive quaternion on slider `input` events
2. `work/pieces/066/066.svg` — grep for `id="fold-` to confirm all 22 fold IDs
3. `LAYER-CONVENTIONS.md` — fold id convention (marker-bound fold ids section)

## Target File Structure Changes

```
preview.html    ← update: CSS additions + new helper functions + grouped fold slider builder
```

No other files touched. No new files.

## Numbered Tasks

---

### Task 1 — Confirm 066 fold ID patterns (read-only diagnostic)

Run in bash before writing any code:

```bash
grep -o 'id="fold-[^"]*"' work/pieces/066/066.svg | sort -u
```

Expected output (22 folds in four groups):

```
# Pane-strip (6): both parts start with "pane"
id="fold-pane1-pane2"
id="fold-pane3-pane2"
id="fold-pane4-pane3"
id="fold-pane5-pane4"
id="fold-pane6-pane5"
id="fold-pane7-pane6"

# Closure (1): tabaa-paneX
id="fold-tabaa-pane7"

# Tab-flap (6): tabX-paneY (not tabaa)
id="fold-taba-pane1"
id="fold-tabb-pane2"
id="fold-tabc-pane3"
id="fold-tabd-pane4"
id="fold-tabe-pane5"
id="fold-tabf-pane6"
id="fold-tabg-pane7"   ← 7 tab folds total

# Cross-piece (7): letter+digits-paneX
id="fold-b65-pane1"
id="fold-c65-pane2"
id="fold-d65-pane3"
id="fold-e65-pane4"
id="fold-f65-pane5"
id="fold-g65-pane6"
id="fold-h65-pane7"
```

If the grep output differs materially, check `066.svg` and adjust the regex patterns
in Task 2 to match what's actually there. Do not proceed past Task 1 with stale assumptions.

---

### Task 2 — Add `classifyFoldId(foldId)` helper

Add this function near the other fold-related helpers, just **before** the
`renderPanelsFirstScene` function definition (around line ~5572):

```js
// ─── Fold-group classification ────────────────────────────────────────────────
// Returns a group key for fold slider grouping, or null if unrecognised.
// Keyed on the SVG fold id string (the raw `id="fold-..."` attribute value).
//
// Recognised patterns (all require the `fold-` prefix):
//   pane-strip  — fold-paneX-paneY      (both segments start with "pane")
//   closure     — fold-tabaa-paneX      (tab-aa closes the strip into a ring)
//   tab-flap    — fold-tabX-paneY       (non-aa tab folds down for side-piece glue)
//   cross-piece — fold-[letter][N]-paneY (landing-marker fold for external tab attach)
//
// Returns null for anything that doesn't match — falls back to flat rendering.
function classifyFoldId(foldId) {
  if (/^fold-pane[^-]+-pane[^-]+$/.test(foldId))   return 'pane-strip';
  if (/^fold-tabaa-/.test(foldId))                   return 'closure';
  if (/^fold-tab[a-z]+-pane/.test(foldId))           return 'tab-flap';
  if (/^fold-[a-z]+\d+[a-z]?-pane/.test(foldId))    return 'cross-piece';
  return null;
}
```

---

### Task 3 — Add CSS for fold group UI

In the CSS block near `#fold-controls` (around line ~41), **add** the following rules
after the existing `#fold-controls` block:

```css
/* ── Fold group sections (renderPanelsFirstScene grouped mode) ─────────────── */
.fold-group { margin-top: 6px; }
.fold-group-header {
  display: flex; align-items: center; gap: 6px;
  padding: 2px 0 3px; border-bottom: 1px solid #2e2e2e;
  cursor: pointer; user-select: none;
}
.fold-group-toggle {
  color: #555; font-size: 10px; min-width: 10px; flex-shrink: 0;
}
.fold-group-label {
  flex: 1; font-size: 11px; font-weight: bold; color: #8cf;
}
.fold-group-sum {
  font-size: 10px; color: #fa8; min-width: 64px; text-align: right;
}
.fold-group-body { display: flex; flex-direction: column; gap: 2px; margin-top: 3px; }
.fold-group-body.collapsed { display: none; }
.fold-group-controls {
  display: flex; align-items: center; gap: 4px; padding: 2px 0;
}
.fold-group-controls button {
  font-size: 10px; padding: 1px 6px;
  background: #2a2a2a; color: #aaa;
  border: 1px solid #444; border-radius: 3px; cursor: pointer;
}
.fold-group-controls button:hover { background: #383838; }
.fold-master-row {
  display: flex; align-items: center; gap: 6px; padding: 2px 0;
}
.fold-master-row label {
  font-size: 10px; color: #888; min-width: 90px;
}
```

---

### Task 4 — Refactor the fold slider builder inside `renderPanelsFirstScene`

Locate the fold slider builder inside `renderPanelsFirstScene`. It currently starts
at the line:
```js
  if (pathHingeMap.size > 0) {
```
…and ends just before:
```js
  } else {
    globalFoldRow.style.display = 'none';
  }
```

**Replace the entire `if (pathHingeMap.size > 0) { ... }` block** with the version
below. The 3D rotation logic inside the per-slider `input` listener is **unchanged**
— only the DOM building around it changes.

```js
  if (pathHingeMap.size > 0) {
    globalFoldRow.style.display = '';
    if (!sceneMode) {
      globalFoldSlider.value = 0;
      globalFoldVal.textContent = '0%';
    }

    // ── Collect slider descriptors (same loop as before, DOM not yet built) ──
    const seen = new Set();
    const sliderDescs = [];   // [{ fold, pid, items, isCurved, defAngle, isAuthored, initialValue, displayLabel }]

    for (const fold of pf.folds) {
      const pid = prefixKey(fold.id);
      if (seen.has(pid) || !pathHingeMap.has(pid)) continue;
      seen.add(pid);

      const items = pathHingeMap.get(pid) || [];
      const isCurved   = items.length > 0 && items[0].mode === 'curved';
      const layerDefault = fold.polarity === 'valley' ? -90 : 90;
      const defAngle   = fold.defaultAngle != null ? fold.defaultAngle : layerDefault;
      const isAuthored = fold.defaultAngle != null;

      let initialValue = 0;
      if (assembledMap && Object.prototype.hasOwnProperty.call(assembledMap, fold.id)) {
        const raw = assembledMap[fold.id];
        const num = Number(raw);
        if (Number.isFinite(num)) {
          initialValue = num;
          fromSidecar.push({ id: fold.id, value: num });
        } else {
          console.warn('[panels-first] assembled.folds[' + JSON.stringify(fold.id) +
            '] is not a finite number:', raw, '— falling through to default-angle precedence.');
          if (fold.defaultAngle != null) initialValue = fold.defaultAngle;
        }
      } else if (fold.defaultAngle != null) {
        initialValue = fold.defaultAngle;
      }

      let displayLabel;
      if (fold.a && fold.b) {
        displayLabel = (fold.step != null ? fold.step + '-' : '') +
          'fold-' + fold.a + '-' + fold.b;
      } else {
        const baseId = fold.id;
        displayLabel = baseId.startsWith('_') ? baseId.slice(1) : baseId;
      }
      if (sceneMode && pieceIdPrefix) displayLabel = pieceIdPrefix + ':' + displayLabel;

      sliderDescs.push({ fold, pid, items, isCurved, defAngle, isAuthored, initialValue, displayLabel });
    }

    // ── Determine whether any fold group is present ──────────────────────────
    // If no fold id matches a known group, fall back to flat rendering (no regression).
    const hasGroups = sliderDescs.some(d => classifyFoldId(d.fold.id) !== null);

    // ── Helper: build one slider row + wire its 3D rotation ─────────────────
    function buildFoldSliderRow(d) {
      const { row, slider } = createSliderRow({
        label: d.displayLabel,
        labelTitle: d.displayLabel + (d.isCurved ? ' (curved fold; v0 sketch)' : ''),
        min: -180, max: 180, step: 1, value: d.initialValue,
        dataset: { pathId: d.pid, defaultAngle: d.defAngle }
      });
      const xN = document.createElement('span');
      xN.style.cssText = 'color:#666;font-size:10px;min-width:22px';
      xN.textContent = '×' + d.items.length;
      row.appendChild(xN);
      const degBadge = document.createElement('span');
      degBadge.title = 'Assembled angle' + (d.isAuthored ? ' (authored in id)' : ' (layer default)');
      degBadge.style.cssText = 'color:' + (d.isAuthored ? '#8cf' : '#666') +
        ';font-size:10px;min-width:36px;text-align:right;flex-shrink:0';
      degBadge.textContent = '→' + (d.defAngle > 0 ? '+' : '') + d.defAngle + '°';
      row.appendChild(degBadge);
      if (d.isCurved) {
        const cb = document.createElement('span');
        cb.title = 'Descriptive curved fold — approximate visual sketch only';
        cb.style.cssText = 'color:#fc6;font-size:10px';
        cb.textContent = '≈';
        row.appendChild(cb);
      }

      // Wire 3D rotation
      if (d.initialValue !== 0) {
        for (const item of d.items) {
          if (item.mode === 'fold') {
            item.target.quaternion.setFromAxisAngle(
              item.axis, -(item.signFwd || 1) * d.initialValue * Math.PI / 180
            );
          } else if (item.mode === 'curved') {
            item.target.quaternion.setFromAxisAngle(item.axis, d.initialValue * Math.PI / 180);
          }
        }
      }
      slider.addEventListener('input', () => {
        const deg = parseFloat(slider.value);
        for (const item of d.items) {
          if (item.mode === 'fold') {
            item.target.quaternion.setFromAxisAngle(
              item.axis, -(item.signFwd || 1) * deg * Math.PI / 180
            );
          } else if (item.mode === 'curved') {
            item.target.quaternion.setFromAxisAngle(item.axis, deg * Math.PI / 180);
          }
        }
        requestRender();
      });

      return { row, slider };
    }

    // ── FLAT rendering (no groups detected) ──────────────────────────────────
    if (!hasGroups) {
      for (const d of sliderDescs) {
        const { row } = buildFoldSliderRow(d);
        perFoldSliders.appendChild(row);
      }

    // ── GROUPED rendering ────────────────────────────────────────────────────
    } else {
      // Group order defines the visual stacking order in the panel.
      const GROUP_ORDER    = ['pane-strip', 'closure', 'tab-flap', 'cross-piece', null];
      const GROUP_LABELS   = {
        'pane-strip':  'Pane strip',
        'closure':     'Closure',
        'tab-flap':    'Tab flaps',
        'cross-piece': 'Cross-piece landings',
        null:          'Other',
      };
      // cross-piece group starts collapsed (not the primary focus when folding solo)
      const STARTS_COLLAPSED = new Set(['cross-piece']);

      // Bucket folds by group
      const buckets = new Map();
      for (const d of sliderDescs) {
        const g = classifyFoldId(d.fold.id);
        if (!buckets.has(g)) buckets.set(g, []);
        buckets.get(g).push(d);
      }

      // Render each populated group in order
      for (const g of GROUP_ORDER) {
        if (!buckets.has(g)) continue;
        const members = buckets.get(g);

        const groupEl   = document.createElement('div');
        groupEl.className = 'fold-group';

        // ── Group header (click to collapse/expand) ──
        const header = document.createElement('div');
        header.className = 'fold-group-header';

        const toggleSpan = document.createElement('span');
        toggleSpan.className = 'fold-group-toggle';
        const collapsed0 = STARTS_COLLAPSED.has(g);
        toggleSpan.textContent = collapsed0 ? '▶' : '▼';

        const labelSpan = document.createElement('span');
        labelSpan.className = 'fold-group-label';
        labelSpan.textContent = (GROUP_LABELS[g] || g || 'Other') + ' (' + members.length + ')';

        // Sum readout — only shown for pane-strip group
        let sumSpan = null;
        if (g === 'pane-strip') {
          sumSpan = document.createElement('span');
          sumSpan.className = 'fold-group-sum';
          sumSpan.title = 'Sum of all pane-to-pane fold angles. ' +
            'For a closed tube, target ≈ 360°.';
          sumSpan.textContent = 'Σ = 0°';
        }

        header.appendChild(toggleSpan);
        header.appendChild(labelSpan);
        if (sumSpan) header.appendChild(sumSpan);

        // ── Group body ──
        const body = document.createElement('div');
        body.className = 'fold-group-body' + (collapsed0 ? ' collapsed' : '');

        // Collapse toggle
        header.addEventListener('click', () => {
          const isCollapsed = body.classList.toggle('collapsed');
          toggleSpan.textContent = isCollapsed ? '▶' : '▼';
        });

        groupEl.appendChild(header);

        // ── Group controls (above individual sliders) ─────────────────────
        const ctrlRow = document.createElement('div');
        ctrlRow.className = 'fold-group-controls';

        if (g === 'pane-strip') {
          // "Equal" button: distributes 360° equally across all pane-strip sliders
          const equalBtn = document.createElement('button');
          equalBtn.textContent = 'Equal (÷360°)';
          equalBtn.title = 'Set each pane fold to 360° ÷ ' + members.length +
            ' = ' + Math.round(360 / members.length) + '° (closed tube target)';
          equalBtn.addEventListener('click', () => {
            const each = 360 / members.length;
            for (const d of members) {
              const sliderEl = body.querySelector('[data-path-id="' + d.pid + '"] input[type=range]') ||
                body.querySelector('.slider-row[data-path-id="' + d.pid + '"] input');
              if (sliderEl) {
                sliderEl.value = each;
                sliderEl.dispatchEvent(new Event('input', { bubbles: true }));
              }
            }
          });
          ctrlRow.appendChild(equalBtn);

          // "Flat" button: set all pane folds to 0°
          const flatBtn2 = document.createElement('button');
          flatBtn2.textContent = 'Flat';
          flatBtn2.title = 'Set all pane folds to 0°';
          flatBtn2.addEventListener('click', () => {
            for (const d of members) {
              const sliderEl = body.querySelector('[data-path-id="' + d.pid + '"] input[type=range]') ||
                body.querySelector('.slider-row[data-path-id="' + d.pid + '"] input');
              if (sliderEl) { sliderEl.value = 0; sliderEl.dispatchEvent(new Event('input', { bubbles: true })); }
            }
          });
          ctrlRow.appendChild(flatBtn2);
        }

        if (g === 'tab-flap' || g === 'closure') {
          // Master sub-slider: moves all sliders in the group simultaneously
          const masterRow = document.createElement('div');
          masterRow.className = 'fold-master-row';
          const masterLabel = document.createElement('label');
          masterLabel.textContent = 'All ' + (GROUP_LABELS[g] || g);
          const masterSlider = document.createElement('input');
          masterSlider.type = 'range';
          masterSlider.min = '-180'; masterSlider.max = '180'; masterSlider.step = '1';
          masterSlider.value = '0';
          masterSlider.style.flex = '1';
          const masterVal = document.createElement('span');
          masterVal.style.cssText = 'font-size:10px;color:#aaa;min-width:32px;text-align:right';
          masterVal.textContent = '0°';
          masterSlider.addEventListener('input', () => {
            masterVal.textContent = masterSlider.value + '°';
            // Drive all individual sliders in this group
            for (const d of members) {
              const sliderEl = body.querySelector('[data-path-id="' + d.pid + '"] input[type=range]') ||
                body.querySelector('.slider-row[data-path-id="' + d.pid + '"] input');
              if (sliderEl) { sliderEl.value = masterSlider.value; sliderEl.dispatchEvent(new Event('input', { bubbles: true })); }
            }
          });
          masterRow.appendChild(masterLabel);
          masterRow.appendChild(masterSlider);
          masterRow.appendChild(masterVal);

          // Quick buttons
          const flatB = document.createElement('button');
          flatB.textContent = 'Flat';
          flatB.style.cssText = 'font-size:10px;padding:1px 5px;background:#2a2a2a;color:#aaa;border:1px solid #444;border-radius:3px;cursor:pointer;margin-left:2px';
          flatB.addEventListener('click', () => { masterSlider.value = 0; masterSlider.dispatchEvent(new Event('input')); });
          const downB = document.createElement('button');
          downB.textContent = '90°';
          downB.style.cssText = flatB.style.cssText;
          downB.title = 'Fold all tabs 90° down';
          downB.addEventListener('click', () => { masterSlider.value = 90; masterSlider.dispatchEvent(new Event('input')); });
          masterRow.appendChild(flatB);
          masterRow.appendChild(downB);

          ctrlRow.appendChild(masterRow);
        }

        if (ctrlRow.children.length > 0) body.appendChild(ctrlRow);

        // ── Individual slider rows ────────────────────────────────────────
        for (const d of members) {
          const { row } = buildFoldSliderRow(d);
          body.appendChild(row);
        }

        // ── Wire up sum readout for pane-strip (runs after sliders are built) ─
        if (g === 'pane-strip' && sumSpan) {
          const updateSum = () => {
            let s = 0;
            for (const d of members) {
              const sl = body.querySelector('[data-path-id="' + d.pid + '"] input[type=range]') ||
                body.querySelector('.slider-row[data-path-id="' + d.pid + '"] input');
              if (sl) s += parseFloat(sl.value) || 0;
            }
            const diff = Math.round(s - 360);
            sumSpan.textContent = 'Σ = ' + Math.round(s) + '°' +
              (Math.abs(diff) > 1 ? (diff > 0 ? ' (+' + diff + ')' : ' (' + diff + ')') : ' ✓');
            sumSpan.style.color = Math.abs(diff) <= 5 ? '#7ec894' : '#fa8';
          };
          body.addEventListener('input', updateSum);
          // Initialise readout
          updateSum();
        }

        groupEl.appendChild(body);
        perFoldSliders.appendChild(groupEl);
      }
    }

  } else {
```

**IMPORTANT:** The closing `} else {` above must connect cleanly to the existing
`globalFoldRow.style.display = 'none';` block that was already there. Do not add
a second `} else {` — just replace the single old one.

---

### Task 5 — Fix querySelectorAll in global fold slider listener

The existing `globalFoldSlider` `input` listener (outside `renderPanelsFirstScene`)
drives all `.slider-row` elements inside `#per-fold-sliders`. In grouped mode,
per-fold slider rows are now nested inside `.fold-group-body` divs, which are
themselves inside `.fold-group` divs — but they still have the class `slider-row`
and their `input[type=range]` elements work the same way. The existing
`querySelectorAll('#per-fold-sliders .slider-row')` selector will still find them
because CSS descendant selection is not limited to direct children.

**Verify** the global slider and the `flatBtn` / `assembledBtn` handlers
(lines near `#globalFoldSlider`) all use `querySelectorAll('#per-fold-sliders .slider-row')`
or similar descendant queries (not `> .slider-row` direct-child queries). If any use `>`,
remove the `>`. This is likely already fine — just confirm.

---

### Task 6 — Handle `data-path-id` dataset on rows

Inside `buildFoldSliderRow`, the `createSliderRow` call passes `dataset: { pathId: pid, defaultAngle: defAngle }`. This sets `row.dataset.pathId = pid`. The master sub-slider logic in Task 4 queries for the individual slider using:

```js
body.querySelector('[data-path-id="' + d.pid + '"] input[type=range]')
```

This relies on `row.dataset.pathId` being rendered as the HTML attribute `data-path-id` on the `.slider-row` div. Confirm that `createSliderRow`'s dataset loop (`for (const k of Object.keys(dataset)) row.dataset[k] = ...`) does set this attribute — it does, because the JS `dataset` API maps camelCase to kebab-case automatically (`pathId` → `data-path-id`). No code change needed; just verify the selector works by loading 066 in Bench mode after the change and checking devtools.

---

## Verification Checklist

**Code-side (before pushing):**

1. `node --check preview.html` — no syntax errors
2. `grep -c 'classifyFoldId' preview.html` → returns ≥ 3 (definition + calls in Task 4)
3. `grep -c 'fold-group' preview.html` → returns ≥ 5 (CSS class names + JS strings)
4. `grep -c 'pane-strip' preview.html` → returns ≥ 4 (regex, GROUP_ORDER, GROUP_LABELS, label text)
5. `grep -c 'hasGroups' preview.html` → returns ≥ 2 (declaration + branch)
6. Confirm no `querySelectorAll('#per-fold-sliders > .slider-row')` direct-child selector exists: `grep -n "per-fold-sliders >" preview.html` → no output
7. `grep -c 'buildFoldSliderRow' preview.html` → returns ≥ 2 (definition + call inside FLAT branch + calls inside GROUPED branch = at least 2)
8. Confirm `classifyFoldId` is defined BEFORE `renderPanelsFirstScene` (line number of `classifyFoldId` < line number of `async function renderPanelsFirstScene`)

**Browser — Alan runs after merge (Bench mode, piece 066):**

1. Load `preview.html` → type `066` → click Load. Confirm the fold panel shows **4 labelled group sections** (Pane strip, Closure, Tab flaps, Cross-piece landings) instead of a flat list.
2. **Pane strip group**: 6 individual sliders + "Equal (÷360°)" + "Flat" buttons + sum readout "Σ = 0°". Click "Equal (÷360°)" → all 6 sliders jump to 60° and the 3D mesh closes into a tube shape. Sum readout shows "Σ = 360° ✓" in green.
3. Adjust one pane slider by hand → sum readout updates live, turns amber when off 360°, green when within ±5°.
4. **Closure group**: fold-tabaa-pane7 slider with master sub-slider. Moving master drives the individual slider and the 3D mesh.
5. **Tab flaps group**: 7 individual sliders + master sub-slider + Flat + 90° buttons. Pressing "90°" folds all 7 tab flaps to 90° simultaneously.
6. **Cross-piece landings group**: starts **collapsed** (▶ toggle). Click to expand → 7 individual sliders appear.
7. Reload with a **simple piece** (e.g. `069`): fold panel renders in flat mode (no group headers), same as before this change.
8. **Global "Fold all" slider** still works — moving it drives all fold sliders across all groups.
9. **"Save assembled pose" button** still captures all per-fold slider values (including those inside group bodies) correctly.

## What NOT to Change

- `renderScene` (cut-line-first path) — untouched
- Cluster / `sceneMode` paths in `renderPanelsFirstScene` — untouched; groups are
  only rendered in Bench mode (sceneMode = false). In sceneMode, `perFoldSliders`
  is cleared + appended-to per piece as before, with no group detection.
- `pathHingeMap` structure or wiring
- `createSliderRow`, `attachNumberInput` — untouched
- The global `globalFoldSlider` event listener — verify but do not change
- `assembledMap` / sidecar loading — the `fromSidecar` diagnostics array and
  sidecar precedence logic are **inside** `buildFoldSliderRow` and stay unchanged
- `savePoseBtn` / `save-pose-row` logic — untouched; it reads `.slider-row [data-path-id]`
  which still resolves through the group DOM

## Manual Tests

| Step | Action | Expected |
|---|---|---|
| A | Load `066` in Bench mode | 4 group sections visible in fold panel |
| B | Click "Equal (÷360°)" | All 6 pane sliders → 60°; piece closes into tube; Σ = 360° ✓ |
| C | Drag one pane slider | Sum updates; mesh moves |
| D | Press "90°" in Tab flaps | All 7 tab sliders → 90°; tabs fold down in 3D |
| E | Click Cross-piece header | Group expands/collapses; individual sliders appear |
| F | Load `069` | Flat slider list (no groups); existing behaviour unchanged |
| G | Move global "Fold all" slider | All sliders + 3D response as before |
| H | Save assembled pose | JSON snippet includes all fold ids from all groups |
