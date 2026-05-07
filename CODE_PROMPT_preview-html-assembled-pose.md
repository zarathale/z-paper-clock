---
status: shipped
started: 2026-05-06
shipped: 2026-05-06
owner: Zarathale (Alan)
target: preview-html-assembled-pose
---

_Shipped 2026-05-06; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._

# CODE_PROMPT — `assembled.folds` load + save in `preview.html`

Two additions to `preview.html`:

1. **Load:** when a piece loads, read its sidecar's `assembled.folds` block and use those values as the per-fold slider's initial value (and apply the resulting fold rotations immediately, so the piece appears in its assembled pose at load time).
2. **Save:** add a "Save assembled pose" button that captures every panels-first per-fold slider's current value into a JSON snippet for Alan to copy or download. Browsers can't write to disk, so the workflow is copy-to-clipboard + download → Alan merges into `work/pieces/NNN/NNN.json` by hand.

This is the preview-side companion to DECISIONS #11 (the schema is locked there; this prompt implements the load + save).

## What You Are Doing and Why

Today's per-fold validation flow: open `preview.html?piece=NNN`, scrub the sliders to find a pose that physically makes sense, … and lose it on reload. The sidecar `assembled.folds` block makes the result durable. The preview becomes a tool Alan uses to *discover* the angle and *capture* it; the sidecar carries it forward.

Convention: SVG = originally-authored printed content (tabs, landings, fold lines as drawn on the print) — Alan's authoring lane. Sidecar = everything learned afterward (assembled poses, inferred connections, mechanism geometry) — Claude's lane on schema. This prompt strictly stays in the sidecar lane; no SVG re-authoring.

## Prerequisites — confirm before starting

- `preview.html` exists at repo root and runs cleanly (`python3 -m http.server 8770` from repo root, then open `http://localhost:8770/preview.html?piece=069`).
- Browser-side functions already wired: `loadPieceById`, `loadScene`, `maybeLoadSidecar`, `renderPanelsFirstScene`, `pathHingeMap`. The existing `maybeLoadSidecar` reads `function` blocks from the sidecar — extend the same call site.
- Per-fold sliders are built inside `renderPanelsFirstScene` (around lines 3010–3092). Each slider row carries `dataset.pathId` (the prefixed key into `pathHingeMap`) and `dataset.defaultAngle` (the fold's `defaultAngle` from its id `-<deg>` suffix, or null).
- Each fold object in `pf.folds` has fields: `id` (literal SVG id, including any Affinity `_` prefix), `polarity` (valley/mountain), `step`, `a`/`b` panel ids, `defaultAngle`, `descriptive` (optional).
- `claude-work/DECISIONS.md` row #11 captured (read it in full).
- `LAYER-CONVENTIONS.md` "Per-piece JSON sidecar" section documents the schema (read the `assembled.folds` subsection).
- No sidecars currently carry `assembled.folds` — this prompt is greenfield. The load must handle missing sidecar / missing block as the normal case.

## Read These Files First

1. `claude-work/DECISIONS.md` row #11 in full.
2. `LAYER-CONVENTIONS.md` — "Per-piece JSON sidecar" section, especially the `assembled.folds` subsection.
3. `preview.html` lines 250–260 (state vars), 414–447 (`loadPieceById`), 461–550 (`loadScene`), 719–748 (`maybeLoadSidecar` + `renderFunctionBlock` + `hideSidecarBlock`), 3010–3092 (per-fold slider build inside `renderPanelsFirstScene`).
4. `claude-work/state/connection-graph.json` — for reference on the panels-first piece set and example fold ids (069, 094, 095, 099 cover the interesting cases: standard folds, fold-step-prefixed folds, descriptive/curved folds).

## Target File Structure Changes

```
preview.html       ← update: extend maybeLoadSidecar to surface assembled.folds; thread it into renderPanelsFirstScene's slider build; add "Save assembled pose" UI
```

Single file. No new files. No sidecar files written by this prompt — the save path is copy/download, never `fetch(... { method: "PUT" })`.

## Numbered Tasks

### 1. State plumbing for `currentAssembledFolds`

Add a module-level state var near the existing piece-state vars (around line 250):

```javascript
// Loaded sidecar's assembled.folds map for the current single-piece load,
// or null if no sidecar / no assembled block. Keyed by literal SVG fold id
// (including any Affinity `_` underscore prefix). Read by renderPanelsFirstScene
// when building per-fold sliders.
let currentAssembledFolds = null;
```

Reset to `null` at the top of `loadScene` (alongside the existing single-piece state teardown, around line 482) and in `loadSvgFromString` for drag-drop / file-picker code paths (search for places `currentPieceId = null` is set; pair with `currentAssembledFolds = null` everywhere). The save button's enabled state depends on this var.

### 2. Extend `maybeLoadSidecar` to capture `assembled.folds`

Today `maybeLoadSidecar(id)` reads the sidecar and dispatches the `function` block to `renderFunctionBlock`. Extend it to also capture `assembled.folds` into `currentAssembledFolds`:

```javascript
async function maybeLoadSidecar(id) {
  currentAssembledFolds = null;  // reset before any async work
  const path = `work/pieces/${id}/${id}.json`;
  try {
    const r = await fetch(path + '?t=' + Date.now());
    if (!r.ok) { hideSidecarBlock(); return; }
    const json = await r.json();
    if (json && json.function) renderFunctionBlock(json.function);
    else hideSidecarBlock();
    if (json && json.assembled && json.assembled.folds &&
        typeof json.assembled.folds === 'object') {
      currentAssembledFolds = json.assembled.folds;
    }
  } catch {
    hideSidecarBlock();
  }
}
```

Important: `maybeLoadSidecar` is called AFTER `loadSvgFromString` in `loadPieceById` (line 446 — `await maybeLoadSidecar(id)` runs after parsing). That means the per-fold sliders have already been built by the time we know what `assembled.folds` says. Two options:

- **Option A (preferred):** flip the order in `loadPieceById` so the sidecar is fetched FIRST and `currentAssembledFolds` is populated before `loadSvgFromString` runs. Both calls await; flipping is a one-line change. Caveat: `loadSvgFromString` is also called from drag-drop / file-picker paths where there's no piece id and therefore no sidecar — that's fine; `currentAssembledFolds` stays `null`.
- **Option B:** after `maybeLoadSidecar` resolves, walk the existing slider rows and adjust them. More moving pieces; not recommended.

Go with Option A. Update `loadPieceById`:

```javascript
async function loadPieceById(rawId, source = 'piece-id') {
  // ... existing id normalization + path construction ...
  const svgText = await resp.text();
  currentPieceId = id;
  pieceInput.value = id;
  reloadPieceBtn.disabled = false;
  history.replaceState(null, '', `?piece=${id}`);
  await maybeLoadSidecar(id);                    // moved BEFORE loadSvgFromString
  loadSvgFromString(svgText, { source, pieceId: id, filename: `${id}.svg` });
}
```

(`loadSvgFromString` reads `currentAssembledFolds` indirectly through `renderPanelsFirstScene`; ordering is what makes the wire work.)

### 3. Use `currentAssembledFolds` as slider initial value in `renderPanelsFirstScene`

In the per-fold slider build (around line 3035–3070), after computing `defAngle` (the fold's `defaultAngle` or layer default):

```javascript
// Precedence for slider initial value:
//   1. assembled.folds[fold.id] (sidecar; literal id including any `_` prefix)
//   2. fold.defaultAngle (-<deg> suffix on the fold id, parsed during parseSVG)
//   3. 0
const assembledMap = (!sceneMode && currentAssembledFolds) ? currentAssembledFolds : null;
const assembledVal = assembledMap && Object.prototype.hasOwnProperty.call(assembledMap, fold.id)
  ? Number(assembledMap[fold.id])
  : null;
const initialValue = (assembledVal != null && Number.isFinite(assembledVal))
  ? assembledVal
  : (fold.defaultAngle != null ? fold.defaultAngle : 0);
```

Update the slider markup so the input's `value` attribute starts at `initialValue` (not the hardcoded `0`):

```javascript
'<input type="range" min="-180" max="180" step="1" value="' + initialValue + '">' +
'<span class="val">' + initialValue.toFixed(0) + '°</span>' +
```

After the row is appended, **drive the fold rotation immediately** so the piece appears in its assembled pose at load time:

```javascript
const slider  = row.querySelector('input');
const valSpan = row.querySelector('.val');
// Apply initial value to the geometry (only when non-zero — when zero, the
// piece's at-rest pose is already correct and we save a few quaternion ops).
if (initialValue !== 0) {
  for (const item of items) {
    if (item.mode === 'fold') {
      item.target.quaternion.setFromAxisAngle(
        item.axis,
        -(item.signFwd || 1) * initialValue * Math.PI / 180
      );
    } else if (item.mode === 'curved') {
      item.target.quaternion.setFromAxisAngle(item.axis, initialValue * Math.PI / 180);
    }
  }
}
slider.addEventListener('input', () => { /* unchanged from today */ });
```

The "scene mode" gate on `assembledMap` is intentional: in scene mode multiple pieces share the slider area and `currentAssembledFolds` only carries the single-piece load. Scene-mode load applies layer defaults (today's behavior) for now; per-piece assembled poses across a scene is a follow-up. Leave a comment noting that.

When `assembledVal` exists in the sidecar but isn't finite (NaN, null, string), fall through to `fold.defaultAngle` (next in the precedence chain) and emit a one-line console warning naming the offending fold-id and the malformed value. Don't crash.

### 4. Add the "Save assembled pose" UI

Visible only in single-piece mode (not scene mode) AND only when at least one panels-first per-fold slider is present. UI placement: a row inside `#fold-controls`, just below `#per-fold-sliders`. Markup:

```html
<div id="save-pose-row" class="slider-row" style="display:none; justify-content:flex-end; gap:6px;">
  <button id="savePoseBtn" style="font-size:11px; padding:2px 8px;">Save assembled pose</button>
</div>
```

Two display states: `style.display = ''` when active, `style.display = 'none'` otherwise. Toggle inside `renderPanelsFirstScene`'s slider-build block: at the end of the panels-first slider construction, set `style.display` based on `(!sceneMode && pf.folds.length > 0)`. Hide it in `renderScene` (the cut-line-first / single-piece pre-panels-first path) and in `renderSceneMulti`'s scene-mode branch.

Click handler builds the JSON snippet and presents a modal:

```javascript
document.getElementById('savePoseBtn').addEventListener('click', () => {
  if (!currentPieceId) return;
  const rows = document.querySelectorAll('#per-fold-sliders .slider-row');
  if (!rows.length) return;
  const folds = {};
  for (const row of rows) {
    const slider = row.querySelector('input[type=range]');
    if (!slider) continue;
    const pid = row.dataset.pathId;
    if (!pid) continue;
    // Strip the scene-mode piece-id prefix if present (single-piece mode never has it).
    // pid form in single-piece mode is the literal fold id; in scene mode it's "<piece>:<fold-id>".
    const foldId = pid.includes(':') ? pid.slice(pid.indexOf(':') + 1) : pid;
    const val = parseFloat(slider.value);
    if (Number.isFinite(val)) folds[foldId] = Math.round(val * 100) / 100;
  }
  const payload = {
    assembled: {
      folds,
      captured: new Date().toISOString(),
      note: ""
    }
  };
  showAssembledPoseModal(currentPieceId, payload);
});
```

Modal contents — a textarea pre-filled with `JSON.stringify(payload, null, 2)` plus three buttons: **Copy to clipboard**, **Download `<piece>.assembled.json`**, **Close**. The modal is a simple absolute-positioned overlay (no library — use the existing inline-style approach the rest of `preview.html` uses).

```javascript
function showAssembledPoseModal(pieceId, payload) {
  const text = JSON.stringify(payload, null, 2);
  const modal = document.createElement('div');
  modal.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:1000;' +
    'display:flex;align-items:center;justify-content:center;';
  modal.innerHTML =
    '<div style="background:#222;border:1px solid #444;border-radius:8px;padding:16px;' +
      'width:520px;max-width:90vw;max-height:80vh;display:flex;flex-direction:column;gap:8px;">' +
    '<div style="color:#ccc;font-size:12px;">' +
      '<strong>Save assembled pose for piece ' + pieceId + '</strong>' +
      '<div style="margin-top:4px;color:#999;font-size:11px;">' +
        'Merge this <code>assembled</code> block into <code>work/pieces/' + pieceId + '/' + pieceId + '.json</code>. ' +
        'If the file doesn\'t exist yet, create it with this as the full content.' +
      '</div>' +
    '</div>' +
    '<textarea readonly style="flex:1;min-height:240px;font-family:monospace;font-size:11px;' +
      'background:#111;color:#ddd;border:1px solid #333;padding:8px;">' +
      text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;') +
    '</textarea>' +
    '<div style="display:flex;gap:8px;justify-content:flex-end;">' +
      '<button id="poseCopy">Copy to clipboard</button>' +
      '<button id="poseDownload">Download</button>' +
      '<button id="poseClose">Close</button>' +
    '</div>' +
    '</div>';
  document.body.appendChild(modal);
  modal.querySelector('#poseCopy').addEventListener('click', () => {
    navigator.clipboard.writeText(text).then(
      () => { addBanner('Pose copied to clipboard.', 'info'); },
      () => { addBanner('Clipboard write failed; use Download instead.', 'warn'); }
    );
  });
  modal.querySelector('#poseDownload').addEventListener('click', () => {
    const blob = new Blob([text], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = pieceId + '.assembled.json';
    a.click();
    URL.revokeObjectURL(url);
  });
  modal.querySelector('#poseClose').addEventListener('click', () => modal.remove());
}
```

The modal closes on Close button click. (Esc / outside-click handlers are nice-to-have; skip for v1.)

### 5. Console diagnostics

In `renderPanelsFirstScene`, when at least one slider was initialized from `currentAssembledFolds`, emit one console line summarizing what loaded:

```javascript
const fromSidecar = []; // populate inside the per-fold loop when assembledVal != null
// after the loop:
if (fromSidecar.length > 0) {
  console.log('[panels-first] assembled.folds applied:', fromSidecar.length, 'folds:',
    fromSidecar.map(f => f.id + '=' + f.value + '°').join(', '));
}
```

Helps when debugging "did the sidecar load actually take effect?"

### 6. No effect in scene mode (this iteration)

Scene mode skips assembled-folds load. Document why with a comment near the `sceneMode` gate. The follow-up work — per-piece assembled poses applied independently to each piece in a scene — is a separate prompt; the current prompt only solves single-piece authoring.

## Verification Checklist

1. **Baseline regression: no sidecar.** Open `?piece=069`. Confirm:
   - All 10 fold sliders initialize to 0 (current behavior).
   - The piece renders flat (no rotations applied).
   - "Save assembled pose" button is visible.
   - Clicking the button shows the modal with a JSON payload listing all 10 folds at 0.
2. **Sidecar with assembled.folds.** Create temporary `work/pieces/069/069.json`:
   ```json
   {"assembled": {"folds": {"fold-main-bh": 90, "fold-main-ai": -45}, "note": "test"}}
   ```
   Reload `?piece=069`. Confirm:
   - The slider for `fold-main-bh` initializes to 90 and shows "90°"; the geometry shows the bh panel rotated.
   - The slider for `fold-main-ai` initializes to -45 and shows "-45°".
   - Other sliders initialize to 0.
   - Console logs `[panels-first] assembled.folds applied: 2 folds: ...`.
   - Delete the temporary sidecar before committing.
3. **Save round-trip.** With the test sidecar from #2 in place: scrub the `fold-main-g` slider to 60, click "Save assembled pose," click Copy. Paste into a scratch file; confirm the JSON contains `fold-main-g: 60` plus all 10 fold entries plus the existing assembled values, plus a `captured` timestamp.
4. **Affinity-prefix fold ids.** Test with piece 095 (which has `_3-fold-pane1-pane2`-style ids). Sidecar:
   ```json
   {"assembled": {"folds": {"_1-fold-pane3-pane4": 180, "_2-fold-pane2-pane3": 90}}}
   ```
   Confirm those two sliders pick up the values.
5. **Malformed sidecar value.** Sidecar has `{"assembled": {"folds": {"fold-main-bh": "not a number"}}}`. Confirm the slider for `fold-main-bh` falls through to 0 (no `defaultAngle` on this fold), a console.warn is emitted naming the fold-id and the value, and no crash.
6. **Sidecar with both `function` and `assembled` blocks.** Confirm the `function` block surfaces in the side panel as today AND `assembled.folds` applies to sliders. Both reads happen inside `maybeLoadSidecar`.
7. **Scene mode unaffected.** Run scene `065,066,067,068,069`. Confirm:
   - "Save assembled pose" button is hidden.
   - Sliders initialize to 0 regardless of any sidecar's assembled.folds (scene mode is opted out for this iteration).
   - The pivot-cluster alignment for 067+069 still works.
8. **R-key reload picks up sidecar changes.** Open `?piece=069` with the test sidecar; press R; confirm the assembled values reload (cache-busted fetch).
9. **`R` reload tolerates sidecar deletion.** Delete the test sidecar; press R; confirm sliders reset to 0; no errors.

## What NOT to Change

- The per-fold slider's `input` event handler (the rotation-on-scrub code).
- `parsePanelsFirstFolds`, `parsePanelsLayer`, `buildHingeTree`, `parseFoldLayer` — fold parsing is unchanged.
- The global "fold all" slider behavior (it interpolates 0 → defaultAngle as today; assembled.folds doesn't affect it).
- `pathHingeMap`, `axleGroup`, `currentSlabPivot`, the existing rotation slider, the `R` key.
- Scene mode's pivot-cluster alignment (PR #17).
- The `function` block read in `maybeLoadSidecar` and `renderFunctionBlock`.

## Manual tests

| When | Step | Expect |
|---|---|---|
| Pre-change | Load `?piece=069`, no sidecar | All sliders at 0, piece flat. |
| Post-change, no sidecar | Same | Identical: sliders at 0, piece flat, no console noise. |
| Post-change, sidecar with assembled | See Verification #2 | Specified folds load with values; piece renders pre-folded. |
| Post-change, save | See Verification #3 | Modal works; copy + download both produce parseable JSON. |
| Post-change, scene | See Verification #7 | Save button hidden; sliders unaffected by sidecar (gated). |

## Notes for the Code session

- **No backend changes.** The save path is browser-only — clipboard + download. Alan merges the JSON into the sidecar by hand.
- **Branch naming.** Per CLAUDE.md: `claude/preview-html-assembled-pose`. Rename if Claude Code starts on an auto-name branch.
- **Commit subject.** `preview.html: load + save assembled fold pose from sidecar`
- **Session note + PR.** Standard end-of-session ritual.

Once shipped, flip this file's front-matter `status` to `shipped`, add a `_Shipped YYYY-MM-DD; ..._` italic header below the front matter per CLAUDE.md convention, and leave it in place as the decision record.
