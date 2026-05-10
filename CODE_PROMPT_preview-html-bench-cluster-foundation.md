---
status: ready-for-code
started: 2026-05-09
owner: Zarathale (Alan)
target: preview-html-bench-cluster-foundation
---

# CODE_PROMPT — preview.html foundational interaction + cutouts (PR A of three)

## What You Are Doing and Why

This is the first of three PRs landing the design captured in `claude-work/DECISIONS.md` #13 (three-mode preview.html: Bench / Cluster / Wall + sidecar `assembled.transform`). PR A is the foundational interaction-and-rendering substrate; PR B adds Bench-mode transform capture; PR C adds Cluster-mode multi-piece manipulation. PR D (Wall mode) is deferred until enough subassemblies exist to make it useful.

You are NOT doing transform capture, sidecar `assembled.transform` read/write, or multi-piece scene assembly in this PR. Those land in PR B and PR C. You ARE doing:

1. **Cutouts as Shape holes** — close the unfinished feature flagged at preview.html:1435 where `<g id="cutouts">` paths are recognized but never subtracted from the extruded slab.
2. **Slider + numeric text-entry** — every numeric slider (fold angles, thickness, future transform sliders) gets a bidirectional number input next to it.
3. **Camera lock + toggle** — camera defaults to looking head-on at the piece; OrbitControls is gated behind a toggle button. Per-session memory; resets to default on each page load.
4. **Click-drag-on-piece via TransformControls** — when camera is locked, dragging on the piece moves/rotates it via TransformControls handles (translate arrows + rotate rings). The visual change is **not** saved in this PR (that's PR B).
5. **RGB axes gizmos** — AxesHelper at world origin + a fixed-corner mini-axes gizmo always visible regardless of camera or piece position.
6. **Worktable backdrop** — flat dark plane behind the piece; no grid for now.
7. **Bench/Cluster mode toggle UI scaffold** — top-bar segmented control. Bench is the existing single-piece flow (functional). Cluster is a stub that displays "Cluster mode lands in PR C" until that PR ships.

The motivation for separating this from PR B: this is a pure interaction + rendering rewrite that doesn't change any data model. PR B layers on top with sidecar shape changes. Splitting them keeps each diff coherent and ships PR A as a usable improvement (cutouts + sliders + camera ergonomics) even before transform capture lands.

## Prerequisites — confirm before starting

- preview.html exists at repo root and currently ships PR #19's `assembled.folds` load + save.
- `work/pieces/071/071.svg` has both `<g id="silhouette"><path id="cutaway">` and a sibling `<g id="cutouts">` containing `<path id="cutout-1">` and `<path id="cutout-2">`. This is the primary cutouts test target.
- three.js version in preview.html (CDN-loaded) supports `THREE.TransformControls` (since r70) and `THREE.AxesHelper` (since r68). If TransformControls isn't already imported, add it from the same CDN as three core.
- `claude-work/DECISIONS.md` #13 is closed and readable.

## Read These Files First

1. `claude-work/DECISIONS.md` #13 — the three-mode design + sidecar `assembled.transform` shape + interaction patterns. This is your design contract.
2. `claude-work/DECISIONS.md` #11 — `assembled.folds` shape (already shipped; you're preserving its read-and-save semantics, just rewrapping the UI).
3. `preview.html:1425-1500` — current `extractSilhouetteFromLayer` with the comment "<g id="cutouts"> is a SIBLING layer (interior holes); v1a-fix does NOT consume it." — Task 1 lifts this restriction.
4. `preview.html:3700-3800` — current Shape building + ShapeGeometry creation. Task 1 attaches holes here.
5. `preview.html:3859-3960` — current "Save assembled pose" flow. Your slider+text-entry rewrite must preserve this exactly; transform-capture extension is PR B's job.
6. `LAYER-CONVENTIONS.md` "Cut-layer authoring convention" — confirms the `cutaway` / `cutout-N` schema.
7. `work/pieces/071/071.svg` — visual + parser test target for cutouts.

## Target File Structure Changes

```
preview.html                                  ← all changes here (single-file tool)
```

No new files in this PR. May need to add a small CSS block for the new mode-toggle and slider-row styles, plus the corner-gizmo viewport.

## Numbered Tasks

### Task 1 — Cutouts: extract from `<g id="cutouts">` and apply as Shape holes

**Goal.** When a piece's SVG has a sibling `<g id="cutouts">` layer with `cutout-1`, `cutout-2`, ... paths, those paths are subtracted from the extruded slab as interior holes. Today the parser recognizes them but the renderer ignores them.

**Implementation.**

1. **Parse the cutouts layer.** In or alongside `extractSilhouetteFromLayer`, add `extractCutoutsFromLayer(p)` that walks `<g id="cutouts">` and returns an array of polygon arrays (`[[vx, vy], ...]`) — one polygon per `cutout-N` path. Use the same `shapeToPolygon` helper. Tolerate Affinity-wrapper `<g>` nodes (querySelectorAll('*') walks descendants). Reject anything that isn't a path with `id="cutout-N"` (warn via banner and skip).

2. **Surface cutouts on the parsed object.** Extend the parsed-piece shape to carry `parsed.cutouts: Array<Polygon>` alongside the existing silhouette polygons. Update `parseSVG` (or wherever the parsed-piece object is constructed).

3. **Build holes when constructing the front/back ShapeGeometry.** Around lines 3722-3771, where `THREE.Shape` is constructed from the silhouette polygon, add the cutout polygons as `shape.holes = [hole1, hole2, ...]`. Each hole is a `THREE.Path` constructed from a cutout polygon. Both `fgeo` (front) and `bgeo` (back) ShapeGeometries must include the holes.

4. **Coordinate convention.** Cutout polygons are in the same SVG coordinate space as the silhouette; the same y-flip and unit-scaling that applies to silhouette applies to cutouts. Reuse the existing transform pipeline.

5. **Test against piece 071.** Loading 071 should now show two interior holes: the central cell (`cutout-1`) and... whatever `cutout-2` is in 071 (verify against the SVG). Both holes should be visible from the front and back faces.

6. **Update the comment at line 1435.** Change `"v1a-fix does NOT consume it"` to a short note that PR A consumes it as Shape holes; reference DECISIONS #13.

**Banner messages.** If `<g id="cutouts">` exists but no `cutout-N` paths are found inside, banner-warn ("`<g id=\"cutouts\">` present but empty"). If a `cutout-N` path can't be parsed as a closed polygon, banner-warn with the id.

### Task 2 — Slider + numeric text-entry pattern

**Goal.** Every numeric slider in preview.html — existing fold sliders, the thickness slider, and any other slider that surfaces — has a number input next to it. Typing a number snaps the slider; dragging the slider updates the number. Bidirectional.

**Implementation.**

1. **Define a helper.** Add `createSliderRow({ id, label, min, max, step, value, onChange })` that returns a DOM element containing the label, the `<input type="range">`, and an `<input type="number">` paired with it. Both inputs share min/max/step. The number input is narrow (~6 ch). Both call `onChange(newValue)` on change.

2. **Replace existing slider construction call sites.** Find every place a slider is currently created (fold sliders in `parsePanelsFirstFolds` consumer / scene rendering; thickness slider; any others). Switch them to `createSliderRow`. Preserve all existing dataset attributes (notably `pathId` for fold sliders) on the slider element so save/load logic continues to find them.

3. **Bidirectional binding.** When the slider's `input` event fires, update the number input's value. When the number input's `input` event fires, clamp to [min, max], snap to step, and update the slider value. Both paths call the shared `onChange`.

4. **Default value.** Mirror existing slider defaults exactly. For fold sliders: `assembled.folds[id]` from sidecar > fold-id `-<deg>` suffix > 0 (PR #19 precedence preserved).

5. **Style.** Inline number input next to the slider. Tight spacing. Label above (or to the left if horizontal layout fits).

**Acceptance check.** Load piece 066 (21 folds). Each fold slider has a number input. Typing 90 in the number input snaps the slider to 90. Dragging the slider updates the number. The "Save assembled pose" button still works exactly as before (PR #19 semantics preserved).

### Task 3 — Camera lock + toggle

**Goal.** Default camera looks head-on at the loaded piece. OrbitControls is disabled by default. A "Camera" toggle button in the top bar enables OrbitControls when active. Per-session memory; resets to default on next page load.

**Implementation.**

1. **Default camera state.** When a piece loads (single-piece mode), camera position is set to `(originX, originY, +Zdistance)` looking at the piece origin (where origin = piece's natural origin per Task 6). Z-distance auto-fits the piece bounding box (existing fit-to-view logic stays).

2. **Toggle button.** Add a button in the top bar with id `cameraToggleBtn`, labeled "Camera locked" by default, toggling to "Camera free" when active. Visual state: locked = subdued; free = highlighted.

3. **OrbitControls gating.** Set `orbitControls.enabled = false` by default. Toggle flips it. When toggled OFF (locked), reset camera to head-on (the piece may have been orbited around).

4. **Per-session memory.** Don't persist across page loads. Just hold the state in a local variable. On page reload, default = locked.

5. **Mouse cursor cue.** When camera is locked, the cursor on the canvas is `default` (or `grab` over the piece — see Task 4). When camera is free, cursor is `move` (existing OrbitControls behavior).

### Task 4 — Click-drag-on-piece via TransformControls

**Goal.** When camera is locked (default), clicking and dragging on the loaded piece manipulates the piece via TransformControls handles. Translate arrows (3 colored) + rotate rings (3 colored) appear on the piece. Visual movement only — no save in this PR.

**Implementation.**

1. **Import TransformControls.** Same CDN as three core. `THREE.TransformControls` should be accessible.

2. **Wrap the piece in a manipulable group.** When a piece is loaded, place its root mesh inside a `THREE.Group` (call it `pieceGroup`). TransformControls attaches to this group, not directly to the mesh. This is the group whose transform will be saved in PR B.

3. **Attach TransformControls.** When camera is locked AND a piece is loaded:
   - Create `transformControls = new THREE.TransformControls(camera, renderer.domElement)`.
   - `transformControls.attach(pieceGroup)`.
   - Add to scene: `scene.add(transformControls)`.
   - Default mode: `'translate'`. Press 'R' on the keyboard to switch to `'rotate'`; press 'T' to switch back. Render a small mode indicator near the gizmo or in the top bar.
   - Snap-to-degree: hold Shift to snap rotation to 15° increments and translation to 5mm increments. (TransformControls supports `setRotationSnap` / `setTranslationSnap`.)

4. **Coordinate dragging with OrbitControls.** TransformControls fires a `dragging-changed` event. While dragging, set `orbitControls.enabled = false` to prevent the camera from also responding (only matters when camera is in free mode).

5. **Hide TransformControls when camera is in free mode.** When the user toggles camera free, detach TransformControls (or `.visible = false`). Re-attach on toggle back to locked.

6. **No save in this PR.** Movement is visual-only. The gizmo position on next page reload reverts to the default. PR B wires sidecar persistence.

### Task 5 — RGB axes gizmos

**Goal.** Visual reference axes — both an in-world AxesHelper at the piece origin and a small fixed-corner gizmo always visible.

**Implementation.**

1. **In-world axes.** `const worldAxes = new THREE.AxesHelper(50)` (50 mm long). Add to the scene at world origin. Render permanently. When piece origin is determined (Task 6), the AxesHelper sits at world origin and the piece is centered around it.

2. **Fixed-corner gizmo.** A second small axes scene rendered in a corner of the viewport.
   - Create a separate `THREE.Scene` (`gizmoScene`) and `THREE.PerspectiveCamera` (`gizmoCamera`) sized for ~80x80 pixels.
   - Add a `THREE.AxesHelper(1)` to `gizmoScene`.
   - Mirror the main camera's rotation (NOT translation) to `gizmoCamera`. So as the user orbits the main scene (when camera is free), the corner gizmo rotates in lockstep, showing world orientation.
   - In the render loop, after rendering the main scene, set the renderer's viewport to the corner box and render `gizmoScene` with `gizmoCamera`. Then reset viewport.
   - Position: bottom-right corner, 8px margin, 80x80 pixels.

3. **Coordinate convention.** Both gizmos use the world frame from DECISIONS #13: +X red, +Y green, +Z blue. (This is three.js AxesHelper's default — no override needed.)

### Task 6 — Worktable backdrop

**Goal.** Below the piece (in -Y), a flat dark plane provides visual grounding. Replaces the current scene's blank background for Bench mode.

**Implementation.**

1. **Geometry.** `THREE.PlaneGeometry(1000, 1000)` (1m x 1m). Material: `THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.9, metalness: 0 })` — dark gray, matte.

2. **Position.** Plane lies in the XZ plane (normal = +Y). Y position is set so the worktable sits just below the piece's lowest point — query the piece bounding box and place at `bbox.min.y - 5mm`.

3. **Lighting.** If the existing scene doesn't have a directional light, add one above the piece (e.g., `directionalLight = new THREE.DirectionalLight(0xffffff, 0.7); directionalLight.position.set(0, 200, 100)`). Plus an `AmbientLight(0x444444, 0.5)` for fill. Confirm the worktable looks dark gray, not invisible.

4. **No grid initially.** No `THREE.GridHelper` overlay — keep it clean. (Grid can land in a later iteration if useful.)

### Task 7 — Bench/Cluster mode toggle UI scaffold

**Goal.** Top-bar segmented control with two options: **Bench** (functional, default) and **Cluster** (stub). Switching to Cluster shows a placeholder banner; switching back to Bench restores normal flow.

**Implementation.**

1. **Top-bar element.** Add a segmented control (two radio-style buttons) in the top bar near the existing piece-id input. Default: Bench selected.

2. **State.** Module-level `currentMode = 'bench'`. Switching toggles the value.

3. **Bench mode (default).** All existing single-piece flow — load by id, sliders, save assembled pose, etc. No behavioral change in this mode beyond what Tasks 1-6 introduce.

4. **Cluster mode (stub).** Hide the per-piece UI (sliders, save buttons, current piece display). Show a centered banner: "Cluster mode lands in PR C — load a single piece in Bench mode for now." Disable the piece-id input in this mode.

5. **Persist within session.** Don't save mode across page loads. Default = Bench on each load.

## Verification Checklist

1. **Cutouts render.** Load piece 071 via `?piece=071` URL param. Both `cutout-1` (center cell) and `cutout-2` are visible as interior holes in the extruded slab, on both front and back faces. No banner warnings.
2. **Slider+text-entry works.** Load piece 066. Each of the 21 fold sliders has a paired number input. Typing 90 in any number input snaps that slider to 90. Dragging the slider updates the number. Save assembled pose still emits the correct JSON (PR #19 unchanged behavior).
3. **Camera locked by default.** Load any piece. Camera shows it head-on. Click-drag does NOT orbit the camera. The "Camera" toggle button in the top bar shows "Camera locked".
4. **Camera toggle works.** Click the toggle. Button label changes to "Camera free". Click-drag now orbits. Toggle back: camera resets to head-on, click-drag stops orbiting.
5. **Click-drag manipulates the piece.** With camera locked, click on the piece. TransformControls handles appear (3 colored arrows). Drag an arrow — piece translates. Press 'R'. Handles change to rotate rings. Drag a ring — piece rotates. The change is visual only; reload the page and the piece is back at default pose.
6. **Snap-to-degree.** Hold Shift while rotating. Rotation snaps to 15° increments. Hold Shift while translating. Translation snaps to 5mm increments.
7. **RGB world axes visible.** Load any piece. Red/Green/Blue lines emanate from world origin, ~50mm long. The corner mini-gizmo (bottom-right) shows the same RGB axes; orbiting the camera (with camera free) rotates the corner gizmo in lockstep.
8. **Worktable visible.** Background under the piece is dark gray, not blank. Piece sits above the worktable.
9. **Mode toggle scaffold works.** Top bar has Bench | Cluster segmented control. Bench = default, fully functional. Switch to Cluster: piece UI disappears, "Cluster mode lands in PR C" banner shows. Switch back: normal flow returns.
10. **No regression on existing flows.** Drag-drop SVG load, piece-id load, scene mode (multi-piece via comma-separated ids), Save assembled pose, all work as before. The save modal emits the same JSON shape as PR #19 — `assembled.folds` only, no `transform` block (that lands in PR B).

## What NOT to Change

- Sidecar JSON shape. `assembled.folds` reads + writes stay identical to PR #19. Adding `assembled.transform` is PR B's work; do not touch it here.
- `parsePanelsFirstFolds`, `buildFaceGraph`, hinge tree, `parsePanelsLayer`, `attachPoints`, closure-attach logic. All untouched.
- Scene mode (multi-piece via comma-separated ids) — keep working as it does today. The Bench/Cluster mode toggle is a separate UI surface; it doesn't replace scene mode in this PR. (Scene mode functionality eventually moves under Cluster mode in PR C.)
- The cut-line-first legacy parser. Untouched.
- Per-piece thickness inference, slab construction, scan-texture mapping, back-face mirror, fold-driven half-plane cuts. Untouched mechanically — only the Shape construction at lines 3722-3771 gains `shape.holes`.

## Manual tests (Alan runs after merge)

- Load piece 071 via piece-id loader. Confirm: both interior holes render; slider + text-entry works on the 3 fold sliders; camera is locked head-on; click-drag manipulates the piece; corner axes gizmo is visible.
- Load piece 066. Confirm 21 fold sliders all have number inputs; mode toggle UI is visible in top bar.
- Switch to Cluster mode. Confirm stub banner appears. Switch back to Bench. Confirm normal flow resumes.
- Save assembled pose on a piece with non-default fold values. Confirm the emitted JSON matches PR #19 shape exactly.
