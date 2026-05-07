---
status: shipped
started: 2026-05-06
shipped: 2026-05-06
owner: Zarathale (Alan)
target: preview-html-multi-piece-scene
---

_Shipped 2026-05-06 (PR #17, commit `101f233`); paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / claude-work/STATUS.md / claude-work/QUEUE.md for current state._

# CODE_PROMPT — multi-piece scene assembly in `preview.html`

Add a "Scene" mode to `preview.html` that loads multiple panels-first pieces into one THREE.js scene and positions them relative to each other using the cross-piece connection graph. Single-piece mode is unchanged.

---

## What You Are Doing and Why

`preview.html` currently renders one piece at a time. The panels-aware parser (PR #15, 2026-05-05) populates `parsed.panelsFirst.attachPoints` for every panels-first piece, but those attach points are inert — no consumer. The connection graph at `claude-work/state/connection-graph.json` was built specifically to be the bridge between pieces.

This prompt wires them up. The deliverable is: type `065,066,067,068,069` into a new "Scene" input field, press Load, and see all five pieces of the anchor cluster rendered together in one scene — with pieces 067 and 069 correctly co-positioned at their shared `pivot-anchor` point.

This is CHARTER §6 commitment #2 ("first piece end-to-end") extended to a multi-piece cluster. After this ships, the path to M3 (the full flat viewer) is visible.

Scope: **single file (`preview.html`)**, additive changes only. Single-piece mode and the cut-line-first fallback are untouched.

---

## Prerequisites — confirm before starting

- `preview.html` runs cleanly; panels-first dispatch is live. Verify: `localhost:8000/preview.html?piece=069` shows `panels-first ✓ — 11 panels, 10 folds`.
- PRs #15 + #16 are on `main` (panels-aware parser + fold-step/closure-attach).
- `claude-work/state/connection-graph.json` exists and is non-empty. Verify: `head -5 claude-work/state/connection-graph.json` shows `{ "pieces": {...`.
- `work/pieces/065/065.svg`, `066/066.svg`, `067/067.svg`, `068/068.svg`, `069/069.svg` all exist.

---

## Read These Files First

1. `preview.html` — full file. Key functions: `renderPanelsFirstScene` (lines ~2465–2830), `parsePanelsFirstAttachPoints` (lines ~2415–2451), `loadPieceById` (lines ~400–435), `elementCentroid` (grep for `function elementCentroid`), `buildSlab`, `MM_PER_UNIT`, `pathHingeMap`, `currentSlabPivot`, `scene`.
2. `claude-work/state/connection-graph.json` — understand the `edges` array shape and the `shared_pivots` array.
3. `LAYER-CONVENTIONS.md` — the `attach-points` layer section for what `pivot-<name>`, `attach-<letter><piece>`, and `landing-<tab><piece>` mean.
4. `CODE_PROMPT_preview-html-panels-aware.md` (shipped) — reference for how `parseSVG` returns `panelsFirst`.

---

## Target File Structure Changes

```
preview.html    ← update: add Scene mode UI + multi-piece loader + pivot-align placement
```

No other files changed.

---

## Numbered Tasks

### Task 1 — Load connection graph at startup

At the top of the `<script>` section (alongside other module-level state), add:

```js
let connectionGraph = null;   // loaded once at startup from claude-work/state/connection-graph.json
```

At the bottom of the `DOMContentLoaded` handler (after the existing piece-id logic), add a non-blocking fetch:

```js
fetch('claude-work/state/connection-graph.json')
  .then(r => r.ok ? r.json() : null)
  .then(g => { connectionGraph = g; })
  .catch(() => {});  // scene mode still works without it (uses pivot heuristic only)
```

The fetch is fire-and-forget. Scene mode degrades gracefully if the file isn't reachable.

---

### Task 2 — Scene mode UI

Add a second input row below the existing piece-ID row in the HTML `<header>` section. Immediately after the `<div id="pieceRow">` block:

```html
<div id="sceneRow" style="margin-top:4px; display:flex; align-items:center; gap:6px;">
  <label for="sceneInput" style="white-space:nowrap; font-size:12px;">Scene:</label>
  <input id="sceneInput" type="text" placeholder="065,066,067,068,069" style="flex:1; font-size:13px; padding:2px 4px;" />
  <button id="loadSceneBtn" style="font-size:12px; padding:2px 6px;">Load</button>
</div>
```

In the script, wire up the button:

```js
const sceneInput  = document.getElementById('sceneInput');
const loadSceneBtn = document.getElementById('loadSceneBtn');
loadSceneBtn.addEventListener('click', () => loadScene(sceneInput.value));
sceneInput.addEventListener('keydown', e => { if (e.key === 'Enter') loadScene(sceneInput.value); });
```

---

### Task 3 — `loadScene(rawIds)` function

Add a new `async function loadScene(rawIds)` near `loadPieceById`. Behaviour:

1. Parse `rawIds`: split on `,`, trim whitespace, zero-pad each to 3 digits (same logic as `loadPieceById`).
2. Clear the current single-piece state exactly as `renderScene` does (`scene.remove(currentSlabPivot)`, dispose meshes, `currentAxleWires`, `pathHingeMap = new Map()`).
3. Also clear any existing scene-mode objects: maintain a module-level `let sceneGroups = [];` array of `THREE.Group` objects added by the last `loadScene` call. On each new call, remove + dispose them all from `scene`, then reset to `[]`.
4. For each piece id: `fetch('work/pieces/' + id + '/' + id + '.svg')`, call `parseSVG(svgText, id)`, call `derivePPM(parsed, callback)` — but **batch** the PPM derivation: all pieces in a scene share the same scan-DPI assumption. Use the first piece's PPM for all (or fallback-1 if the first piece has no scan image). This avoids N sequential image loads.
5. After all pieces are parsed: call `renderSceneMulti(parsedArray)`.
6. Show a "Scene: N pieces" banner in the banners area (reuse `addBanner`).

**Important:** `loadScene` sets `currentPieceId = null` and disables `reloadPieceBtn` to make clear single-piece mode is not active.

---

### Task 4 — `renderSceneMulti(parsedArray)` function

Add `async function renderSceneMulti(parsedArray)`. This is the placement engine.

**Step 4a — compute per-piece slab groups.**

For each `parsed` in `parsedArray`:
- If `parsed.panelsFirst` is truthy: call `renderPanelsFirstScene(parsed)` — but first refactor `renderPanelsFirstScene` to **return** its top-level `THREE.Group` (currently named `pivot`) rather than adding it to `scene` directly (see Task 5). Then `renderSceneMulti` collects those groups.
- If not panels-first: skip that piece with a console warning. Cut-line-first pieces are not supported in scene mode in this prompt.

**Step 4b — initial placement: side-by-side grid.**

For each piece's group, compute its bounding box in local space (use `THREE.Box3.setFromObject`). Place pieces along the X axis with 5 mm gaps:

```
offset_x = sum of (prev piece widths + 5mm gaps)
group.position.x = offset_x + (piece_width / 2)   // center the piece at offset
```

This is the layout if pivot-alignment doesn't apply. Pieces without a shared pivot get this default placement.

**Step 4c — pivot alignment.**

After initial placement, check `connectionGraph.graph.pivot_clusters` — an object whose keys are pivot names and values are arrays of piece-id strings (e.g. `{ "anchor": ["067", "069"] }`). For each pivot cluster:

1. Among the pieces in `parsedArray` that appear in this cluster, find the `attach-points` element with `id="pivot-<name>"` in each piece's parsed bundle.
2. Compute the world-space position of that element's centroid using the formula already used in `renderPanelsFirstScene` for axles:
   ```
   wx = (centroid.x - silBbox.cx) * MM_PER_UNIT + group.position.x
   wy = -(centroid.y - silBbox.cy) * MM_PER_UNIT + group.position.y
   ```
3. Pick the **first** piece in the cluster as the "anchor" (don't move it). For each subsequent piece in the cluster, compute the delta `(anchor_world_pivot - this_world_pivot)` and apply `group.position.add(delta)`.

After pivot alignment, the two pieces sharing `pivot-anchor` (067 and 069) will have their pivot-marker centroids coincide in world space.

**Step 4d — add all groups to scene.**

```js
for (const g of slabGroups) { scene.add(g); sceneGroups.push(g); }
```

**Step 4e — camera fit.**

After all groups are placed, compute the union bounding box across all groups and call the existing camera-fit logic (if preview.html has one) or do a simple `camera.position.set(cx, cy, diagLen * 1.5)`. Make sure `controls.target.set(cx, cy, 0)` is updated too.

---

### Task 5 — Refactor `renderPanelsFirstScene` to return its group

Currently `renderPanelsFirstScene` adds `pivot` to `scene` directly and sets `currentSlabPivot = pivot`. Change it so:

- When called from `renderScene` (single-piece mode): behaviour unchanged. Still sets `currentSlabPivot` and adds to `scene`.
- When called from `renderSceneMulti`: accept an optional `{sceneMode: true}` options argument. When `sceneMode` is true, skip the `scene.add(pivot)` and `currentSlabPivot = pivot` lines, and instead **return** the group so the caller can position it.

The cleanest implementation: add a `returnGroup = false` parameter. When `true`, skip `scene.add` + `currentSlabPivot` and return the group.

**Also:** `renderPanelsFirstScene` currently reads `p.axles[0]` for the rotation pivot and wraps the whole slab in a `THREE.Group` called `pivot` positioned at the axle. In scene mode, the axle-rotation wrapper is still correct — but the outer group's `position` will be overridden by `renderSceneMulti`'s placement step. This is fine; the axle offset is stored inside the group, not in world space.

**Also:** fold sliders. In scene mode, `pathHingeMap` entries from all pieces get merged. Sliders need piece-ID prefixes so they don't collide: when `sceneMode` is true, prefix each fold's slider label and `pathId` key with the piece id (`"069:fold-main-tabf"` not `"fold-main-tabf"`). `pathHingeMap` keys must match whatever the slider wiring uses — keep them consistent.

---

### Task 6 — Per-piece attach-point centroid capture

`parsePanelsFirstAttachPoints` currently records the element type but not the centroid. Add centroid capture:

In `parsePanelsFirstAttachPoints`, for each element that passes the id-parse step, call `elementCentroid(child)` (already in preview.html for axle parsing) and store it on the entry:

```js
entry.centroid = elementCentroid(child);  // {x, y} in viewBox coords, or null
```

This is the data `renderSceneMulti` reads in Task 4c to find pivot positions.

---

### Task 7 — Connection-graph edge annotations in console

After `renderSceneMulti` places pieces, log a structured summary to the console:

```
[scene] loaded 5 pieces: 065 066 067 068 069
[scene] pivot-anchor: pieces 067,069 — aligned (delta: {x: ..., y: ...})
[scene] cross-piece edges in scene: 18 valid (out of 24 total in graph)
```

No UI change — console only. This confirms the placement logic fired and gives Alan a quick sanity check.

---

## Verification Checklist

After implementation:

1. **Single-piece regression.** `?piece=069` still shows `panels-first ✓ — 11 panels, 10 folds, root: abc`. Fold sliders work. No console errors.
2. **Two-piece scene.** Type `067,069` into Scene input, press Load. Two pieces appear. Banner: `Scene: 2 pieces`. Console: `pivot-anchor: pieces 067,069 — aligned`. The two pieces visually share a common point in the scene (the pivot-anchor centroid).
3. **Full anchor cluster.** Type `065,066,067,068,069`. Five pieces appear side-by-side (065 + 066 to the left, 067/069 pivot-aligned to the right, 068 placed near 069 based on initial layout). No console errors. Sliders labeled with piece-id prefix (`069:fold-main-tabf` etc.).
4. **Pendulum rod cluster.** Type `070,071,072`. Three pieces appear. 070's fold sliders show 0 resolved folds (expected — the stale fold-id names on 070 are a known open item, not a regression). 071 and 072 render cleanly.
5. **Graceful degradation.** Remove `claude-work/state/connection-graph.json` temporarily (or rename it). Reload. `loadScene` still loads pieces; pivot alignment is skipped (no shared_pivots data); side-by-side default placement used. Banner shows `Scene: N pieces (no graph)`. Restore the file.
6. **No GPU leaks.** Load a scene, then load a second scene. In Chrome DevTools → Memory, confirm no obvious growth in THREE.js geometry/material objects.

---

## What NOT to Change

- The cut-line-first legacy path (`buildFaceGraph`, `extendFoldsToSilhouette`, cut-trim, face-graph diagnostic harness, Dump button). Not touched.
- Single-piece mode UI (piece-id row, Reload button, `?piece=NNN` URL param). Not touched.
- `parseSVG`, `parsePanelsLayer`, `parsePanelsFirstFolds`, `buildHingeTree`. Not touched.
- `claude-work/state/connection-graph.json`. Read-only input.
- No changes to LAYER-CONVENTIONS.md, DECISIONS.md, or any doc outside preview.html.

---

## Manual Tests (Alan runs after merge)

| Test | Pre-condition | Expected |
|---|---|---|
| Anchor cluster | `localhost:8000/preview.html`, type `065,066,067,068,069`, Load | 5 pieces in scene; 066 is obviously a long strip; 067+069 share a point |
| Fold sliders | In the anchor cluster scene, drag the "069:…" sliders | Piece 069 hinges fold; other pieces unaffected |
| Reload single | Click in piece-id field, type `069`, press Enter | Single-piece mode resumes; scene is cleared |
| Daemon render | Run `echo "069" > claude-work/state/render-triggers/trigger.txt` | Daemon renders single-piece 069 (scene mode not expected to work via daemon trigger in v0) |

---

## Notes

- **Exact attach-landing alignment is out of scope for this prompt.** Getting 065's `attach-e66` element to physically touch 066's `tabe` panel face-to-face requires computing face normals, panel orientations in 3D after folding, and likely the full M4 assembly transform system. The v0 placement here is "shared pivot = same point in world space; everything else = default side-by-side." That's already meaningful and visual.
- **070's unresolved folds** (`fold-panelsideb-tabb`, `fold-panelsidec-tabc`) are a known authoring slip — the fold ids reference stale panel names. They'll show as unresolved (0/2 folds resolved) in scene mode just as they do in single-piece mode. Not a bug in this prompt.
- **097 collision-suffix** (`attach-a991`–`a994`) produces 4 invalid edges in the connection graph. Those edges are filtered from the scene's cross-piece summary (they reference pieces 991–994 which don't exist). Console logs them as `skipped (partner not in parsedArray)`.
