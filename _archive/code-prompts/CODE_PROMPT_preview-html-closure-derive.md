---
status: shipped
started: 2026-05-10
shipped: 2026-05-10
owner: Zarathale (Alan)
target: preview-html-closure-derive
---

_Shipped 2026-05-10; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md / claude-work/STATUS.md for current state._

## What You Are Doing and Why

Piece 066 is a seven-panel wrap strip that must fold into a closed rectangular channel. The closure fold (`fold-tabaa-pane7`) connects the tab at one end of the strip to a landing mark on the other end (`landing-tabaa` on pane1). Right now that fold has a free slider — there is no geometric constraint, so the strip ends never touch regardless of what values you set. The Σ readout in the pane-strip group also has a sign bug: it always compares against +360° when valley-fold strips close at −360°.

This prompt implements **derive-one closure**: after any pane-strip fold changes, the viewer computes the angle that would rotate the tabaa panel to land its centroid on the `landing-tabaa` mark in world space, and applies that angle as a read-only derived value. A "Lock ⊗" toggle in the Closure group enables/disables derivation — off by default so existing free-slider behaviour is unaffected for pieces that have no authored landing mark.

Secondary fix: the Σ readout and Equal button learn to target ±360° (whichever sign minimises the gap) rather than always +360°.

## Prerequisites — confirm before starting

- `preview.html` exists at repo root; `node --check` passes on its extracted `<script>` body.
- Piece 066 SVG exists at `work/pieces/066/066.svg` and includes `id="landing-tabaa"` inside `<g id="marks">` and `id="fold-tabaa-pane7"` inside a fold layer.
- `classifyFoldId('fold-tabaa-pane7')` returns `'closure'` (already implemented in `preview.html`).
- THREE.js r128 is loaded; `scene`, `requestRender`, `MM_PER_UNIT`, `pathHingeMap`, `addBanner` are all module-level globals confirmed present.

## Read These Files First

1. `preview.html` lines 650–700 (module-level state declarations around `pathHingeMap`)
2. `preview.html` lines 5630–5850 (`renderPanelsFirstScene` — slab build loop, hinge tree traversal, `pathHingeMap` population)
3. `preview.html` lines 5980–6010 (`buildFoldSliderRow` — how sliders drive `setFromAxisAngle`)
4. `preview.html` lines 6020–6220 (grouped slider rendering — where the closure group's controls are built and where `body.addEventListener('input', updateSum)` is wired)
5. `preview.html` lines 6181–6200 (the `updateSum` closure + pane-strip body input listener — the trigger point for derivation)

## Target File Structure Changes

```
preview.html    ← update: 5 targeted edits (no other file changes)
```

## Numbered Tasks

---

### Task 1 — Module-level state (near line 654, alongside `pathHingeMap`)

Add three new module-level declarations directly after `let pathHingeMap = new Map();`:

```js
let panelSlabMap   = new Map(); // panelId (Bench) or 'piece:panelId' (Cluster) → THREE.Group slab
let closureSliderRef = null;    // <input type=range> for the active closure fold slider, if any
let closureDerivationEnabled = false; // true when "Lock ⊗" toggle is ON
```

Also reset `closureSliderRef` and `closureDerivationEnabled` in the teardown block that already resets `pathHingeMap` to `new Map()` (the block around line 1044 that fires on piece unload / clear). Add:

```js
panelSlabMap = new Map();
closureSliderRef = null;
closureDerivationEnabled = false;
```

---

### Task 2 — Populate `panelSlabMap` in `renderPanelsFirstScene` (near line 5681)

The existing slab-build loop is:

```js
const slabMap = new Map();
for (const [id, panel] of pf.panels) {
  slabMap.set(id, buildSlab(panel.polygon, T, p.cutouts));
}
```

Change it to also populate `panelSlabMap`:

```js
const slabMap = new Map();
if (!sceneMode) panelSlabMap = new Map();   // reset for single-piece; scene-mode caller resets once
for (const [id, panel] of pf.panels) {
  const slab = buildSlab(panel.polygon, T, p.cutouts);
  slabMap.set(id, slab);
  panelSlabMap.set(prefixKey(id), slab);    // prefixKey is already defined in scope
}
```

No other changes to this loop.

---

### Task 3 — `deriveClosureFold()` function

Add this function **just before** `renderPanelsFirstScene` (i.e., just above the line `async function renderPanelsFirstScene`). It is a standalone module-level function.

```js
// ─── Closure-fold derivation (derive-one) ────────────────────────────────────
// After pane-strip folds change, computes the angle that rotates the closure
// tab panel (tabaa) so its centroid lands on the `landing-tabaa` mark in world
// space. Sets the closure slider + drives the Three.js hinge directly.
//
// Requires: panelSlabMap populated, pathHingeMap populated, scene graph current.
// Safe to call in single-piece Bench mode only (pieceIdPrefix is '' there).
function deriveClosureFold() {
  if (!closureDerivationEnabled) return;

  // ── 1. Find the closure fold descriptor from `parsed` ───────────────────
  const pf = parsed && parsed.panelsFirst;
  if (!pf) return;

  let closureFoldId = null;
  for (const f of pf.folds) {
    if (classifyFoldId(f.id) === 'closure') { closureFoldId = f.id; break; }
  }
  if (!closureFoldId) return;

  // ── 2. Find the child panel (tabaa) from the hinge tree ─────────────────
  let tabChildId = null;
  for (const [panelId, node] of pf.hingeTree.nodes) {
    if (node.fold && node.fold.id === closureFoldId) { tabChildId = panelId; break; }
  }
  if (!tabChildId) return;

  // ── 3. Get the closure hinge from pathHingeMap ───────────────────────────
  // In Bench (single-piece) mode pieceIdPrefix is '' so keys are bare panel ids.
  const closureKey = closureFoldId;   // bare id in Bench mode
  const hingeItems = pathHingeMap.get(closureKey);
  if (!hingeItems || !hingeItems.length) return;
  const { target: hinge, axis, signFwd } = hingeItems[0];

  // ── 4. Find the landing mark centroid and which panel hosts it ───────────
  const landingMarkId = 'landing-tabaa';
  const landingCentroid = parsed.marksCentroidsById && parsed.marksCentroidsById.get(landingMarkId);
  if (!landingCentroid) {
    addBanner('deriveClosureFold: no "' + landingMarkId + '" mark found — author it in the marks layer first.', 'warn');
    return;
  }

  let landingPanelId = null;
  for (const [pid, panel] of pf.panels) {
    const bb = panel.bbox;
    if (landingCentroid.x >= bb.minX && landingCentroid.x <= bb.maxX &&
        landingCentroid.y >= bb.minY && landingCentroid.y <= bb.maxY) {
      landingPanelId = pid; break;
    }
  }
  if (!landingPanelId) {
    addBanner('deriveClosureFold: "' + landingMarkId + '" not contained in any panel bbox — cannot derive.', 'warn');
    return;
  }

  // ── 5. Get slabs from panelSlabMap ───────────────────────────────────────
  const tabaaSlab   = panelSlabMap.get(tabChildId);
  const landingSlab = panelSlabMap.get(landingPanelId);
  if (!tabaaSlab || !landingSlab) return;

  // ── 6. Reset closure hinge to θ=0, update world matrices, measure v0 ────
  hinge.quaternion.set(0, 0, 0, 1);
  scene.updateMatrixWorld(true);

  const v0 = new THREE.Vector3();
  tabaaSlab.getWorldPosition(v0);    // tabaa centroid in world space at θ=0

  // ── 7. Landing-tabaa world position ─────────────────────────────────────
  const bb = pf.panels.get(landingPanelId).bbox;
  const landingLocal = new THREE.Vector3(
    (landingCentroid.x - bb.cx) * MM_PER_UNIT,
    -(landingCentroid.y - bb.cy) * MM_PER_UNIT,
    0
  );
  const landingWorld = landingSlab.localToWorld(landingLocal);

  // ── 8. Hinge world position + world axis ────────────────────────────────
  const hingeWorldPos = new THREE.Vector3();
  hinge.getWorldPosition(hingeWorldPos);

  const parentWorldQ = new THREE.Quaternion();
  hinge.parent.getWorldQuaternion(parentWorldQ);
  const worldAxis = axis.clone().applyQuaternion(parentWorldQ).normalize();

  // ── 9. Project onto plane ⊥ worldAxis, compute signed angle ─────────────
  const r0 = v0.clone().sub(hingeWorldPos);
  const rT = landingWorld.clone().sub(hingeWorldPos);
  r0.addScaledVector(worldAxis, -r0.dot(worldAxis));
  rT.addScaledVector(worldAxis, -rT.dot(worldAxis));

  const lenProduct = r0.length() * rT.length();
  if (lenProduct < 1e-6) return;   // degenerate (landing on hinge axis)

  const crossVec = new THREE.Vector3().crossVectors(r0, rT);
  const sinTheta = crossVec.dot(worldAxis) / lenProduct;
  const cosTheta = r0.dot(rT)              / lenProduct;
  const thetaRad = Math.atan2(sinTheta, cosTheta);

  // ── 10. Apply derived rotation to the hinge ──────────────────────────────
  hinge.quaternion.setFromAxisAngle(axis, thetaRad);

  // ── 11. Convert to slider convention and update the UI ───────────────────
  // Convention: setFromAxisAngle(axis, -(signFwd) * sliderDeg * PI/180) = thetaRad
  // → sliderDeg = -thetaRad * 180/PI / signFwd
  const sliderDeg = -(thetaRad * 180 / Math.PI) / (signFwd || 1);
  const sliderDegRounded = Math.round(sliderDeg * 10) / 10;

  if (closureSliderRef) {
    // Update value + number display without re-dispatching 'input' (avoids loop).
    // The hinge is already positioned above; no need to re-fire the rotation.
    closureSliderRef.value = String(sliderDegRounded);
    // Sync the attached number input if present (it's the next sibling of type=number)
    const numInput = closureSliderRef.parentElement &&
      closureSliderRef.parentElement.querySelector('input[type=number]');
    if (numInput) numInput.value = sliderDegRounded;
  }

  requestRender();
}
```

---

### Task 4 — Wire the Lock toggle and trigger (two sub-edits in grouped renderer)

#### 4a — Closure group: add "Lock ⊗" toggle + capture `closureSliderRef`

Find the block that renders the 'closure' group's individual slider rows (inside the `for (const d of members)` loop for the closure bucket). Currently `buildFoldSliderRow(d)` is called and `{ row }` is appended to `body`. Change the closure group's per-member loop to also:
- Capture the slider reference into `closureSliderRef`
- Add a `fold-derived-row` CSS class to mark the row as derived when the toggle is on

The cleanest insertion is in the group controls block (`if (g === 'tab-flap' || g === 'closure')`), adding a "Lock ⊗" button to the `ctrlRow` for the closure group only:

```js
if (g === 'tab-flap' || g === 'closure') {
  // ... existing master sub-slider code unchanged ...

  // NEW: Lock toggle for closure group only
  if (g === 'closure') {
    const lockBtn = document.createElement('button');
    lockBtn.textContent = closureDerivationEnabled ? 'Unlock ⊗' : 'Lock ⊗';
    lockBtn.title = 'Derive the closure fold angle geometrically (requires landing-tabaa mark)';
    lockBtn.style.cssText = 'font-size:10px;padding:1px 6px;background:#1a2a1a;color:#7ec894;' +
      'border:1px solid #4a7a4a;border-radius:3px;cursor:pointer;margin-left:4px';
    lockBtn.addEventListener('click', () => {
      closureDerivationEnabled = !closureDerivationEnabled;
      lockBtn.textContent = closureDerivationEnabled ? 'Unlock ⊗' : 'Lock ⊗';
      lockBtn.style.background = closureDerivationEnabled ? '#0a1a0a' : '#1a2a1a';
      if (closureSliderRef) {
        closureSliderRef.disabled = closureDerivationEnabled;
        closureSliderRef.style.opacity = closureDerivationEnabled ? '0.45' : '1';
      }
      if (closureDerivationEnabled) deriveClosureFold();
    });
    ctrlRow.appendChild(lockBtn);
  }
}
```

And in the per-member loop for the closure bucket, capture the slider reference:

```js
for (const d of members) {
  const { row, slider } = buildFoldSliderRow(d);
  if (g === 'closure') {
    closureSliderRef = slider;   // capture for deriveClosureFold
    slider.disabled = closureDerivationEnabled;
    slider.style.opacity = closureDerivationEnabled ? '0.45' : '1';
  }
  body.appendChild(row);
}
```

Note: `buildFoldSliderRow` currently only returns `{ row }` — change it to `return { row, slider };` (it already has `slider` in scope; just add it to the return). Verify the return statement is at the bottom of `buildFoldSliderRow`.

#### 4b — Pane-strip body: trigger derivation after sum update

The existing listener (around line 6194) is:

```js
body.addEventListener('input', updateSum);
```

Replace with:

```js
body.addEventListener('input', () => {
  updateSum();
  if (closureDerivationEnabled) deriveClosureFold();
});
```

This fires `deriveClosureFold` every time a pane-strip slider changes, keeping the closure angle live.

---

### Task 5 — Fix Σ readout and Equal button to handle ±360°

#### 5a — Σ readout: target ±360°, whichever is closer

The existing `updateSum` function computes `diff = Math.round(s - 360)`. For valley-fold strips (all angles negative), the physical target is −360°. Replace the diff logic:

```js
const diffPos = s - 360;
const diffNeg = s + 360;
const diff = Math.round(Math.abs(diffPos) <= Math.abs(diffNeg) ? diffPos : diffNeg);
const target = Math.abs(diffPos) <= Math.abs(diffNeg) ? 360 : -360;
sumSpan.textContent = 'Σ = ' + Math.round(s) + '°' +
  (Math.abs(diff) > 1 ? (diff > 0 ? ' (+' + diff + ')' : ' (' + diff + ')') : ' ✓');
sumSpan.style.color = Math.abs(diff) <= 5 ? '#7ec894' : '#fa8';
```

(Only the `diffPos/diffNeg` logic and `target` variable change; `sumSpan.textContent` pattern stays the same as before but now uses the corrected `diff`.)

#### 5b — Equal button: distribute in the sign direction of the current mean

The existing Equal button handler sets `each = 360 / members.length`. Replace:

```js
equalBtn.addEventListener('click', () => {
  // Determine sign from current slider mean; default to +360° if all zero
  let currentSum = 0;
  for (const d of members) {
    const sl = body.querySelector('[data-path-id="' + d.pid + '"] input[type=range]') ||
      body.querySelector('.slider-row[data-path-id="' + d.pid + '"] input');
    if (sl) currentSum += parseFloat(sl.value) || 0;
  }
  const sign = currentSum < -1 ? -1 : 1;
  const each = sign * 360 / members.length;
  for (const d of members) {
    const sliderEl = body.querySelector('[data-path-id="' + d.pid + '"] input[type=range]') ||
      body.querySelector('.slider-row[data-path-id="' + d.pid + '"] input');
    if (sliderEl) {
      sliderEl.value = each;
      sliderEl.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }
});
```

Also update the Equal button's `title` and `textContent` to reflect the ±:

```js
equalBtn.textContent = 'Equal (÷±360°)';
equalBtn.title = 'Set each pane fold to ±360° ÷ ' + members.length +
  ' = ±' + Math.round(360 / members.length) + '° (sign follows current average)';
```

---

## Verification Checklist

### (a) Code-side — commit gate

1. **Syntax**: extract the `<script>` body from `preview.html` to a temp `.js` file; `node --check tempfile.js` exits 0.
2. **`panelSlabMap` declared**: `grep -c "let panelSlabMap" preview.html` → 1.
3. **`panelSlabMap` populated**: `grep -c "panelSlabMap.set" preview.html` → 1 (inside the slab-build loop).
4. **`deriveClosureFold` defined**: `grep -c "function deriveClosureFold" preview.html` → 1.
5. **`closureSliderRef` assigned**: `grep -c "closureSliderRef = slider" preview.html` → 1.
6. **Trigger wired**: `grep -c "closureDerivationEnabled.*deriveClosureFold\|deriveClosureFold.*closureDerivationEnabled" preview.html` → ≥ 1.
7. **Lock button present**: `grep -c "Lock ⊗\|Unlock ⊗" preview.html` → ≥ 2 (the two textContent strings).
8. **`buildFoldSliderRow` returns `{ row, slider }`**: grep for the return statement; confirm `slider` is in the returned object.
9. **Σ fix**: `grep -c "diffPos\|diffNeg" preview.html` → ≥ 2.

### (b) Browser (Alan post-merge)

1. Open `http://localhost:8000/preview.html?piece=066`.
2. Pane-strip group renders with 6 folds; Closure group has 1 fold (`fold-tabaa-pane7`) and a **Lock ⊗** button.
3. Click **Equal (÷±360°)**. All pane-strip sliders move to the same value; Σ readout turns green (✓ near ±360°).
4. Click **Lock ⊗** (turns green/active). The closure slider grays out.
5. Adjust any pane-strip slider by a few degrees. The closure slider value updates automatically, and the tabaa panel visually snaps toward the landing-tabaa mark.
6. Open browser console. No errors. Check: `deriveClosureFold` called without throwing.
7. Click **Unlock ⊗**. The closure slider becomes interactive again.
8. Load a piece without a `landing-tabaa` mark (e.g., 069). No "Lock ⊗" behaviour should throw — confirm no console errors on load.
9. With Lock ⊗ on, hit **Save assembled pose**. Sidecar JSON should include the derived closure fold value alongside the pane-strip values.

## What NOT to Change

- `buildHingeTree` — no changes to tree construction.
- `classifyFoldId` — already correct.
- `pathHingeMap` key format or population logic.
- Scene mode (`sceneMode: true`) code paths — derivation is Bench-mode only; the `if (!sceneMode)` guard on `panelSlabMap = new Map()` keeps scene mode unaffected.
- The cut-line-first render path (`renderScene`) — no changes.
- Any file outside `preview.html`.

## Manual tests

| Step | Expected |
|---|---|
| Load 066; Equal (÷±360°) | Σ readout turns green; 3D view shows a closed or nearly-closed channel shape |
| Lock ⊗; drag pane-strip slider | tabaa panel tracks the landing mark; closure slider value updates live |
| Unlock ⊗; drag closure slider manually | free movement as before |
| Load 069 (no closure fold) | No "Lock ⊗" button appears; no errors |
| Lock ⊗ on 066; Save assembled pose | Downloaded JSON includes all fold angles including the derived closure value |
