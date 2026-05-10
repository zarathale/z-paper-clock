---
status: shipped
started: 2026-05-10
shipped: 2026-05-10
owner: Zarathale (Alan)
target: preview-html-guided-stepper
---

_Shipped 2026-05-10; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md / claude-work/STATUS.md for current state._

## What You Are Doing and Why

Add a guided assembly stepper to `preview.html`'s Cluster mode. The stepper loads a
pre-authored step sequence (`claude-work/state/guided_sequence_anchor.json` — 68 steps for
the anchor cluster) and walks Alan through assembly one step at a time: fold this piece,
snap these connections, glue here, install the axle, check escapement depth. Each step
drives the tool's UI — highlighting the relevant pieces, activating snap mode for
connection steps, showing confirmation popups for lock-shape moments, and surfacing the
book's source quote alongside the instruction.

This is Cluster mode with a step sequence layer, not a new mode. Guided is toggled on/off
via a "Guide" button in the existing cluster controls topbar. The stepper uses the snap and
highlight infrastructure that already exists; it doesn't replace those paths.

The session that produced the step sequence and settled this design is
`sessions/2026-05-10-1040_cowork_guided-assembly-design.md`.

---

## Prerequisites — confirm before starting

- `preview.html` is at repo root; the inline `<script>` block is the full JS codebase.
- `claude-work/state/guided_sequence_anchor.json` exists (68 steps, 1 166 lines). The
  fetch path from `python3 -m http.server` at repo root is
  `claude-work/state/guided_sequence_anchor.json`.
- Snap (PR #25) and bridge-save (PR #26) are merged and on `main`. Functions
  `snapAllPairs`, `snapPair`, `setClusterTool`, `refreshSnapPanel`,
  `clusterPieces` (Map), `currentClusterName` all exist in the inline script block.
- `clusterPieces` keys are zero-padded three-digit piece ids (e.g., `"065"`). The
  guided sequence uses the same format in `piece`, `from_piece`, `to_piece`, and
  `ui.highlight_pieces` fields.

---

## Read These Files First

1. `preview.html` — full file. Pay particular attention to:
   - Topbar HTML (`#cluster-controls` span, line ~269–274)
   - `#cluster-panel` div and its children (line ~333–390)
   - `setClusterTool(tool)` function
   - `snapPair` and `snapAllPairs` — specifically the tail of each (where
     `refreshSnapPanel(); requestRender();` are called)
   - `loadClusterPieces` — specifically after all pieces are placed
   - `teardownClusterScene` — to know what to reset in `setGuidedMode(false)`
2. `claude-work/state/guided_sequence_anchor.json` — skim the `_meta`, `step_types`,
   and at least one step of each type to understand the schema.

---

## Target File Structure Changes

```
preview.html     ← update: add guided stepper (HTML, CSS, JS)
```

No other files change. Do NOT modify `guided_sequence_anchor.json`.

---

## Numbered Tasks

### Task 1 — "Guide" button in topbar cluster controls

In `#cluster-controls` (after `#snapToggleBtn`), add:

```html
<button id="guidedToggleBtn" title="Walk through the guided assembly sequence step by step">Guide</button>
```

Add CSS alongside the existing `#cluster-controls button#snapToggleBtn.active` rule:

```css
#cluster-controls button#guidedToggleBtn.active {
  background: #3a5a3a; color: #c8e8c8; border-color: #5a8a5a;
}
```

### Task 2 — Guided panel section in `#cluster-panel`

Insert the following **between** the save/deselect `<div style="display:flex; gap:6px;">` block
and the Measurements header `<div style="font-size:11px;color:#aaa;border-top...">`:

```html
<!-- Guided assembly stepper. Hidden unless guided mode is active. -->
<div id="guided-panel-section" hidden>
  <div style="font-size:11px;color:#aaa;border-top:1px solid #2a2a2a;padding-top:6px;
              display:flex;justify-content:space-between;align-items:baseline;">
    <strong>Assembly guide</strong>
    <span id="guided-counter" style="color:#666;font-weight:normal;"></span>
  </div>
  <div id="guided-step-card" style="margin-top:4px;"></div>
  <div style="display:flex;gap:6px;margin-top:6px;flex-wrap:wrap;">
    <button id="guidedPrevBtn"  style="font-size:11px;padding:2px 8px;">← Prev</button>
    <button id="guidedDoneBtn"  style="font-size:11px;padding:2px 8px;">Done ✓</button>
    <button id="guidedSkipBtn"  style="font-size:11px;padding:2px 8px;color:#888;">Skip</button>
  </div>
</div>
```

Add CSS for the step card and type badges (place near the snap-panel CSS block):

```css
/* Guided stepper */
#guided-step-card { font-size:11px; line-height:1.5; }
#guided-step-card .step-type-badge {
  display:inline-block; font-size:10px; padding:1px 5px; border-radius:3px;
  font-family:monospace; margin-bottom:4px;
}
#guided-step-card .step-desc    { color:#ddd; margin-bottom:4px; }
#guided-step-card .step-human   { color:#fa8; font-size:10px; margin-bottom:3px; }
#guided-step-card .step-quote   { color:#777; font-size:10px; font-style:italic;
                                   border-left:2px solid #333; padding-left:5px;
                                   margin-top:3px; }
#guided-step-card .step-action-btn {
  font-size:11px; padding:2px 8px; margin-top:4px; display:block; width:100%;
  text-align:left; background:#2a3a2a; border:1px solid #4a6a4a; color:#c8e8c8;
  cursor:pointer; border-radius:3px;
}
/* Type badge color map */
.badge-add-piece      { background:#2a4a2a; color:#8c8; }
.badge-fold           { background:#2a2a4a; color:#88c; }
.badge-glue-self      { background:#4a3a1a; color:#ca8; }
.badge-glue-cross     { background:#4a2a1a; color:#c88; }
.badge-glue-no        { background:#4a1a1a; color:#f88; }
.badge-lock-shape     { background:#3a1a4a; color:#b8c; }
.badge-snap-connection{ background:#1a3a4a; color:#8bc; }
.badge-check          { background:#4a4a1a; color:#cc8; }
.badge-install-bearing,
.badge-insert-axle,
.badge-orient,
.badge-pin            { background:#2a2a2a; color:#aaa; }
```

### Task 3 — Guided state variables

Near the existing snap-state variables block (around `let snapFrom = null`), add:

```js
// ── Guided stepper state ──────────────────────────────────────────────────────
let guidedMode       = false;
let guidedSequence   = null;   // parsed guided_sequence_<cluster>.json or null
let guidedStepIndex  = 0;      // index into guidedSequence.steps for current step
```

### Task 4 — Load guided sequence

```js
async function loadGuidedSequence(clusterName) {
  const path = `claude-work/state/guided_sequence_${clusterName}.json`;
  try {
    const r = await fetch(path + '?t=' + Date.now());
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    guidedSequence = await r.json();
    guidedStepIndex = 0;
    return true;
  } catch (e) {
    addBanner(`Guided: could not load sequence for "${clusterName}": ${e.message}`, 'warn');
    guidedSequence = null;
    return false;
  }
}
```

### Task 5 — setGuidedMode

```js
async function setGuidedMode(on) {
  if (on === guidedMode) return;
  guidedMode = on;
  const btn = document.getElementById('guidedToggleBtn');
  const sec = document.getElementById('guided-panel-section');
  if (!btn || !sec) return;

  if (on) {
    if (!currentClusterName || currentClusterName === '<ad-hoc>') {
      addBanner('Guided: load a named cluster first (e.g., anchor).', 'warn');
      guidedMode = false;
      return;
    }
    const ok = await loadGuidedSequence(currentClusterName);
    if (!ok) { guidedMode = false; return; }
    btn.classList.add('active');
    sec.hidden = false;
    renderGuidedPanel();
    applyGuidedStepBehavior(currentGuidedStep());
  } else {
    btn.classList.remove('active');
    sec.hidden = true;
    clearGuidedHighlights();
    guidedSequence = null;
  }
}
```

Wire up the button alongside the other cluster-controls listeners (near `snapToggleBtn`):

```js
document.getElementById('guidedToggleBtn')
  .addEventListener('click', () => setGuidedMode(!guidedMode));
```

### Task 6 — currentGuidedStep and navigation helpers

```js
function currentGuidedStep() {
  if (!guidedSequence) return null;
  return guidedSequence.steps[guidedStepIndex] || null;
}

function guidedTotalSteps() {
  return guidedSequence ? guidedSequence.steps.length : 0;
}

function advanceGuidedStep() {
  if (!guidedSequence) return;
  const n = guidedSequence.steps.length;
  if (guidedStepIndex < n - 1) {
    guidedStepIndex++;
    renderGuidedPanel();
    applyGuidedStepBehavior(currentGuidedStep());
  } else {
    addBanner('Guided: all steps complete! 🎉', 'ok');
  }
}

function retreatGuidedStep() {
  if (!guidedSequence || guidedStepIndex === 0) return;
  guidedStepIndex--;
  renderGuidedPanel();
  applyGuidedStepBehavior(currentGuidedStep());
}

function markGuidedStepDone(stepId) {
  advanceGuidedStep();
}
```

Wire up Prev / Done / Skip buttons near other cluster-panel button listeners:

```js
document.getElementById('guidedPrevBtn')
  .addEventListener('click', retreatGuidedStep);
document.getElementById('guidedDoneBtn')
  .addEventListener('click', async () => {
    const step = currentGuidedStep();
    if (!step) return;
    if (step.type === 'lock-shape') {
      const ui = step.ui || {};
      const confirmed = await showGuidedConfirmModal(
        ui.popup_title || `Lock ${step.piece || (step.pieces || []).join('+')}?`,
        ui.popup_body  || 'Like letting the glue dry — shape is set from here.',
        ui.popup_confirm || 'Lock it',
        ui.popup_cancel  || 'Keep editing'
      );
      if (!confirmed) return;
    }
    markGuidedStepDone(step.id);
  });
document.getElementById('guidedSkipBtn')
  .addEventListener('click', () => {
    const step = currentGuidedStep();
    if (step) advanceGuidedStep();
  });
```

### Task 7 — renderGuidedPanel

```js
function renderGuidedPanel() {
  if (!guidedSequence) return;
  const step    = currentGuidedStep();
  const total   = guidedTotalSteps();
  const counter = document.getElementById('guided-counter');
  const card    = document.getElementById('guided-step-card');
  const prevBtn = document.getElementById('guidedPrevBtn');
  const doneBtn = document.getElementById('guidedDoneBtn');
  if (!step || !card || !prevBtn || !doneBtn) return;

  counter.textContent = `${guidedStepIndex + 1} / ${total}`;
  prevBtn.disabled = (guidedStepIndex === 0);

  // For add-piece steps where the piece isn't in the scene yet, grey out Done ✓
  // so the primary action is clearly the "Add piece" button.
  if (step.type === 'add-piece') {
    const pid = step.piece;
    const inScene = pid && clusterPieces.has(String(parseInt(pid, 10)).padStart(3, '0'));
    doneBtn.disabled = !inScene;
    doneBtn.title = inScene ? '' : 'Add the piece to the scene first';
  } else {
    doneBtn.disabled = false;
    doneBtn.title = '';
  }

  // Badge class: 'badge-' + type (hyphens preserved, e.g. 'badge-snap-connection')
  const badgeClass = 'badge-' + step.type;
  const typeLabel  = step.type.replace(/-/g, '‑'); // non-breaking hyphens for badge

  // Build piece label for context header.
  // snap-connection steps use "from → to"; all others join with " + ".
  const piecesArr = [step.piece, step.from_piece, step.to_piece, ...(step.pieces || [])]
    .filter(Boolean);
  const piecesLabel = step.type === 'snap-connection'
    ? [step.from_piece, step.to_piece].filter(Boolean).join(' → ')
    : piecesArr.join(' + ');

  // Source quote block (omit if absent)
  const quoteHtml = step.source_quote
    ? `<div class="step-quote">${escHtml(step.source_quote)}</div>`
    : '';

  // Human-judgment note (shown only when requires_human: true)
  const humanHtml = step.requires_human && step.human_note
    ? `<div class="step-human">⚠ ${escHtml(step.human_note)}</div>`
    : '';

  // Action button for add-piece steps only (other types use Done ✓).
  // Note: doneBtn.disabled is already set above for add-piece steps.
  let actionBtnHtml = '';
  if (step.type === 'add-piece') {
    const pid = step.piece;
    const inScene = pid && clusterPieces.has(
      String(parseInt(pid, 10)).padStart(3, '0')
    );
    actionBtnHtml = inScene
      ? `<div style="color:#5c5;font-size:10px;margin-top:4px;">✓ ${pid} is in the scene</div>`
      : `<button class="step-action-btn" id="guided-add-piece-btn"
           data-piece="${escHtml(pid)}">Add piece ${pid} to scene</button>`;
  }

  card.innerHTML = `
    <span class="step-type-badge ${badgeClass}">${typeLabel}</span>
    ${piecesLabel ? `<span style="color:#888;font-size:10px;margin-left:5px;">${escHtml(piecesLabel)}</span>` : ''}
    <div class="step-desc">${escHtml(step.description)}</div>
    ${humanHtml}
    ${quoteHtml}
    ${actionBtnHtml}
  `;

  // Wire the add-piece button if present
  const addBtn = card.querySelector('#guided-add-piece-btn');
  if (addBtn) {
    addBtn.addEventListener('click', async () => {
      const pid = addBtn.dataset.piece;
      const normId = String(parseInt(pid, 10)).padStart(3, '0');
      const currentIds = [...clusterPieces.keys()];
      if (!currentIds.includes(normId)) {
        await loadClusterPieces([...currentIds, normId], currentClusterName);
      }
      renderGuidedPanel();
      applyGuidedStepBehavior(currentGuidedStep());
    });
  }
}

// Minimal HTML escaper for user-visible strings from the JSON.
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
```

> **Note:** The file has a local `escapeHtml` const inside `showAssembledPoseModal`
> (line ~6336) — it is not accessible at module scope. Add `escHtml` as a new
> module-level function as specified above; there is no duplication concern.

### Task 8 — applyGuidedStepBehavior

```js
function applyGuidedStepBehavior(step) {
  if (!step || !guidedMode) return;

  // 1. Highlight relevant pieces in the scene.
  const highlights = (step.ui && step.ui.highlight_pieces) || [];
  highlightGuidedPieces(highlights);

  // 2. Type-specific tool activations.
  if (step.type === 'snap-connection') {
    // Activate snap tool so the snap panel is ready.
    setClusterTool('snap');
    // Pre-highlight the from_piece's connection spheres if it's in the scene.
    // (The user still clicks to initiate the snap; we just put them in snap mode.)
  } else if (step.type === 'fold') {
    // Snap tool stays off; user works in the fold sliders on the selected piece.
    // Select the piece in the cluster if it's loaded, so the transform panel shows it.
    const pid = step.piece;
    if (pid) {
      const normId = String(parseInt(pid, 10)).padStart(3, '0');
      if (clusterPieces.has(normId) && selectedClusterPieceId !== normId) {
        selectClusterPiece(normId);
      }
    }
  } else {
    // For non-snap steps: exit snap mode if it was left active by an auto-advance.
    // (Manual snap activation by the user is also cleared — guided mode controls the tool.)
    if (clusterInteractionMode === 'snap') setClusterTool('select');
  }
}
```

### Task 9 — highlightGuidedPieces / clearGuidedHighlights

```js
// Set a warm amber emissive on highlighted pieces; zero-emissive on the rest.
function highlightGuidedPieces(pieceIds) {
  const normSet = new Set(
    (pieceIds || []).map(id => String(parseInt(id, 10)).padStart(3, '0'))
  );
  for (const [id, cp] of clusterPieces) {
    const emissive = normSet.has(id)
      ? new THREE.Color(0.18, 0.14, 0.02)   // warm amber
      : new THREE.Color(0, 0, 0);
    cp.pieceGroup.traverse(obj => {
      if (obj.isMesh && obj.material && 'emissive' in obj.material) {
        obj.material.emissive.copy(emissive);
      }
    });
  }
  requestRender();
}

function clearGuidedHighlights() {
  for (const cp of clusterPieces.values()) {
    cp.pieceGroup.traverse(obj => {
      if (obj.isMesh && obj.material && 'emissive' in obj.material) {
        obj.material.emissive.set(0, 0, 0);
      }
    });
  }
  requestRender();
}
```

### Task 10 — Lock-shape confirm modal

```js
// Promise-based confirm modal for lock-shape steps.
// Resolves true if user clicks confirm, false if cancel or closes.
function showGuidedConfirmModal(title, body, confirmLabel, cancelLabel) {
  return new Promise(resolve => {
    const overlay = document.createElement('div');
    overlay.style.cssText = [
      'position:fixed;inset:0;background:rgba(0,0,0,0.65);',
      'display:flex;align-items:center;justify-content:center;z-index:9999;'
    ].join('');

    const box = document.createElement('div');
    box.style.cssText = [
      'background:#1a1e22;border:1px solid #3a4a5a;border-radius:6px;',
      'padding:20px 24px;max-width:360px;font-size:13px;color:#ddd;',
      'display:flex;flex-direction:column;gap:12px;'
    ].join('');

    const h = document.createElement('strong');
    h.style.fontSize = '14px';
    h.textContent = title;

    const p = document.createElement('p');
    p.style.cssText = 'margin:0;color:#aaa;font-size:12px;line-height:1.5;';
    p.textContent = body;

    const btnRow = document.createElement('div');
    btnRow.style.cssText = 'display:flex;gap:8px;justify-content:flex-end;';

    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = cancelLabel;
    cancelBtn.style.cssText = 'font-size:12px;padding:4px 12px;';
    cancelBtn.addEventListener('click', () => { overlay.remove(); resolve(false); });

    const confirmBtn = document.createElement('button');
    confirmBtn.textContent = confirmLabel;
    confirmBtn.style.cssText = [
      'font-size:12px;padding:4px 12px;',
      'background:#3a5a3a;color:#c8e8c8;border-color:#5a8a5a;'
    ].join('');
    confirmBtn.addEventListener('click', () => { overlay.remove(); resolve(true); });

    btnRow.append(cancelBtn, confirmBtn);
    box.append(h, p, btnRow);
    overlay.appendChild(box);
    document.body.appendChild(overlay);
    confirmBtn.focus();
  });
}
```

### Task 11 — Auto-advance hooks

**In `snapAllPairs`**, at the very end (after the final `refreshSnapPanel(); requestRender();`
call), add:

```js
  // Guided stepper: auto-advance if the current step is a snap-connection for this pair.
  if (guidedMode) {
    const step = currentGuidedStep();
    if (step && step.type === 'snap-connection') {
      const sFrom = String(parseInt(step.from_piece, 10)).padStart(3, '0');
      const sTo   = String(parseInt(step.to_piece,   10)).padStart(3, '0');
      if (sFrom === snapNormId(tabPieceId) && sTo === snapNormId(landingPieceId)) {
        markGuidedStepDone(step.id);
      }
    }
  }
```

**In `loadClusterPieces`**, at the very end (after the banner `'X pieces.'` and
`console.log`), add:

```js
  // Guided stepper: if guided mode is on, re-render the panel (add-piece step may
  // now be completable / show "in scene" state) and re-apply step behavior.
  if (guidedMode && guidedSequence) {
    renderGuidedPanel();
    applyGuidedStepBehavior(currentGuidedStep());
  }
```

Also add one line at the end of `teardownClusterScene`:

```js
  // Clear guided state when cluster is torn down.
  if (guidedMode) setGuidedMode(false);
```

### Task 12 — Hide/reset guided mode on Bench switch

In `setMode`, in the branch that runs when switching TO bench (`teardownClusterScene()` is
called), ensure `setGuidedMode(false)` fires before or is covered by the teardown hook
added in Task 11. If `teardownClusterScene` now calls `setGuidedMode(false)`, no
additional change is needed here. Confirm this is the case.

---

## Verification Checklist

**Code-side (commit gate):**

1. `node --check preview.html` — no syntax errors.
2. Brace balance: `grep -o '{' preview.html | wc -l` equals `grep -o '}' preview.html | wc -l`.
3. All new symbols present:
   ```
   rg "guidedMode|guidedSequence|guidedStepIndex|loadGuidedSequence|setGuidedMode|currentGuidedStep|advanceGuidedStep|retreatGuidedStep|markGuidedStepDone|renderGuidedPanel|applyGuidedStepBehavior|highlightGuidedPieces|clearGuidedHighlights|showGuidedConfirmModal" preview.html | wc -l
   ```
   Should be well above 20 (each symbol appears in definition + call sites).
4. `guidedCompleted` does NOT appear in the file (it was removed in review; dead state):
   ```
   rg "guidedCompleted" preview.html
   ```
   Expected: no matches.
5. `guidedToggleBtn`, `guided-panel-section`, `guided-step-card`, `guided-counter`,
   `guidedPrevBtn`, `guidedDoneBtn`, `guidedSkipBtn` all present in HTML:
   ```
   rg "guidedToggleBtn|guided-panel-section|guided-step-card|guided-counter|guidedPrevBtn|guidedDoneBtn|guidedSkipBtn" preview.html
   ```
6. `escHtml` defined exactly once at module scope (distinct from the locally-scoped
   `escapeHtml` inside `showAssembledPoseModal`):
   ```
   rg "^function escHtml" preview.html
   ```
   Expected: exactly one match.
7. `teardownClusterScene` contains a `setGuidedMode(false)` call or equivalent.
8. Auto-advance hooks present in `snapAllPairs` and `loadClusterPieces`:
   ```
   rg "Guided stepper" preview.html
   ```
   Expected: at least 2 matches (one in each function).
9. `applyGuidedStepBehavior` else branch calls `setClusterTool('select')` when in snap mode:
   ```
   rg "clusterInteractionMode.*snap.*setClusterTool|setClusterTool.*select.*guided" preview.html
   ```

**Browser-side (Alan post-merge — Manual tests section below):**

Not run by Code. Do not start an HTTP server.

---

## What NOT to Change

- `guided_sequence_anchor.json` — read-only input; never modified by this PR.
- The snap panel (Zones A/B/C), snap logic, measurement logic, or save logic.
- Bench mode code paths.
- The existing `clusterPieces` data structure or `loadClusterPieces` signature.
- The `?cluster=anchor` URL routing or `loadCluster(name)` behavior (guided activates
  *after* the cluster is loaded, not instead of it).

---

## Manual tests (browser, post-merge)

Run from repo root: `python3 -m http.server 8770`, open
`http://localhost:8770/preview.html?cluster=anchor`.

1. **Guide button visible.** In Cluster mode, the "Guide" button appears in the topbar
   alongside Measure and Snap. In Bench mode the button is hidden.

2. **Guide activates.** Click "Guide" — button goes green, guided panel section appears
   above Measurements, counter shows "1 / 68", step card shows the `add-piece` badge and
   "Bring piece 065 into the field…", an "Add piece 065 to scene" button appears (since
   065 may not be pre-loaded when the URL loads the full cluster).

3. **Add-piece button.** If 065 is not in the scene, clicking "Add piece 065 to scene"
   adds it. Step card updates to show "✓ 065 is in the scene".

4. **Done ✓ advances.** Click Done ✓ — counter advances to "2 / 68", card now shows
   `fold` badge and "Apply all folds on piece 065…", piece 065 glows amber, other pieces
   are dimmed.

5. **Prev navigates back.** Click ← Prev — returns to step 1 / 68. Prev is disabled at
   step 1.

6. **Lock-shape popup.** Navigate to step 4 (c-040, lock-shape). Click Done ✓ — a modal
   appears: "Lock 065's shape?" with body text and "Lock it" / "Keep editing" buttons.
   Clicking "Keep editing" dismisses without advancing; "Lock it" advances to step 5.

7. **Snap-connection auto-advance.** Navigate to step 9 (c-090, snap-connection 065→066).
   Guided panel shows `snap-connection` badge; Snap tool auto-activates. Click a 065
   sphere → partners highlight. Click "Snap all 7 pairs → 066" in the snap panel. After
   snap fires, stepper auto-advances to step 10 (c-100, glue-cross).

8. **Piece highlighting.** At any step, `ui.highlight_pieces` pieces glow amber; others
   are neutral. Navigating steps changes which pieces glow.

9. **Guide off.** Click "Guide" again — panel hides, amber highlights clear, all pieces
   return to neutral emissive.

10. **Mode switch clears guided.** With Guide active, click "Bench" — guide turns off
    cleanly (no console errors, no lingering amber highlights).
