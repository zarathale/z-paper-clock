---
date: 2026-05-10
start_time: "00:30"
end_time: "03:35"
mode: code
participant: Zarathale (Alan)
target: preview-html-bench-cluster-foundation
orchestration_prompt: CODE_PROMPT_preview-html-bench-cluster-foundation.md
---

## Goal

Ship PR A of three from DECISIONS #13 (three-mode preview.html). The foundational interaction + cutouts substrate — no transform capture, no Cluster mode behavior. Closes the unfinished cutouts-as-holes feature flagged at preview.html:1435 since 2026-05-02 and lays the camera/gizmo/transform-controls scaffolding that PR B (Bench transform capture) and PR C (Cluster mode) sit on top of.

## What was done

All seven tasks from the CODE_PROMPT landed in `preview.html`:

**Task 1 — Cutouts as Shape holes.** New `extractCutoutsFromLayer(p)` walks `<g id="cutouts">` and returns the `cutout-N` polygons; `parseSVG` surfaces them as `parsed.cutouts`. `buildSlab(polygon, T, cutoutPolygons)` filters cutouts by point-in-polygon containment against the slab's outer polygon and pushes them as `THREE.Path` holes onto both the front and back ShapeGeometry. All four `buildSlab` call sites updated (panels-first, cut-line-first face-graph regions, multi-cutaway, single-slab fallback). Verified on 071: cutout-1 routes to panel `b`, cutout-2 routes to panel `c`, each panel's front+back slab gets one hole — 4 hole-bearing slabs in the rendered scene. Comment at preview.html line ~1435 updated to reflect the now-implemented behavior.

Side-wall geometry inside holes is intentionally NOT generated in v0 — the front and back holes line up so you see straight through, which is acceptable on cardstock-thin slabs where the side wall would be invisible anyway. Calling that out in the buildSlab comment so a future pass doesn't read it as a bug.

**Task 2 — Slider + numeric text-entry.** New `attachNumberInput(slider, opts)` augments any range input with a paired number input and bidirectional binding (slider drag updates number; number typing clamps + step-snaps + dispatches the slider's `input` event so existing handlers fire unchanged). Static-HTML sliders (thickness, rotation, global-fold) get `attachNumberInput` calls right after their DOM refs are taken. Dynamic per-fold rows (in both `renderPanelsFirstScene` and the cut-line-first `renderScene` builder) refactored to use a higher-level `createSliderRow({ label, min, max, step, value, dataset, ... })` helper that returns `{ row, slider, num }` — caller appends badges (×N hinge count, →deg assembled badge, ≈ curved indicator). The `.val` span dropped from per-fold rows; the number input doubles as the value display. Verified on 066 — all 21 fold sliders have paired number inputs; typing 90 snaps the slider to 90; dragging to 45 mirrors to the number.

The `dataset.pathId` and `dataset.defaultAngle` attributes on each row are preserved exactly, so global-fold cascade, reset button, and save-pose all continue to find the rows via `row.querySelector('input[type=range]')` (which already used the typed selector).

**Task 3 — Camera lock + toggle.** `controls.enabled = false` set in `initScene` (default = locked). New top-bar button `cameraToggleBtn` flips it via `setCameraLocked(locked)`; toggling back to locked resets the camera to head-on (`(0, 0, dist)` looking at origin). Per-session memory only — no persistence; default = locked on every page load. Hint text in the canvas footer updated.

**Task 4 — TransformControls click-drag-on-piece.** `THREE.TransformControls` loaded from the same r128 CDN as core. Each piece load wraps `currentSlabPivot` + `currentAxleWires` in a new `currentPieceGroup` (`THREE.Group`) via `wrapForTransform()`; TransformControls attaches to that group. The wrapper means moving the gizmo translates the piece + its axle wires together, so visual coherence is preserved. Default mode `translate`; `R` switches to rotate, `T` back to translate (one-shot keys, ignored when typing into INPUT/TEXTAREA). Hold Shift to set 15° rotation snap + 5mm translation snap (cleared on keyup). Drag fires `dragging-changed`; while dragging, OrbitControls is forcibly disabled to prevent double-response in free-camera mode. TransformControls is hidden + detached when camera is in free mode (so OrbitControls owns the drag) and re-attached on lock. Top-bar `xformModeIndicator` shows the current mode with key hints; hidden when no piece is loaded.

The visual movement is NOT saved in this PR — that's PR B. Reload reverts the piece to default pose.

**Task 5 — RGB axes gizmos.** In-world `THREE.AxesHelper(50)` added to the scene at world origin (50mm long). Corner mini-gizmo: own `gizmoScene` + `gizmoCamera`, rendered after the main scene into an 80×80 viewport in the bottom-right (8px margin) using `setViewport`/`setScissor`. The gizmo camera mirrors the main camera's rotation by copying the (camera.position − controls.target) direction onto a fixed-distance gizmoCamera, so orbiting the main camera spins the corner gizmo in lockstep. `clearDepth()` between renders prevents the gizmo from being depth-occluded by the main scene.

**Task 6 — Worktable backdrop.** `THREE.PlaneGeometry(1000, 1000)` (1m square), pre-rotated to lie in the XZ plane (normal +Y). Material: `MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.9, metalness: 0 })` — flat dark gray, matte. `positionWorktableForPiece()` sets the worktable Y to `bbox.min.y - 5mm` after `wrapForTransform()` adds the piece group to scene. The existing AmbientLight + two DirectionalLights from initScene cover the lighting requirement.

**Task 7 — Bench/Cluster mode toggle scaffold.** Top-bar segmented control (Bench | Cluster) wired to `setMode(mode)`. Module-level `currentMode = 'bench'`. Cluster mode adds a `mode-cluster` body class; CSS hides per-piece UI sections (`#fold-controls`, `#thickness-section`, `#rotation-section`, `#diagnostics-section`, `#sceneRow`) and disables the piece-id input + Load + Reload buttons via opacity + pointer-events. Stub banner `#cluster-stub` shows centered: "Cluster mode lands in PR C — load a single piece in Bench mode for now." Switching back to Bench restores everything and re-attaches TransformControls to the current piece group. No persistence — default = Bench on each page load.

## Verification

Browser-side structural verification via `mcp__Claude_Preview__preview_eval` against a local `python3 -m http.server 8770`:

- 071 load → `parsed.cutouts.length === 2`, `currentPieceGroup` has 4 ShapeGeometry meshes with `parameters.shapes.holes.length === 1` (front+back of panels b and c — the two panels each cutout falls inside).
- 066 load → 21 fold-slider rows, all with paired `input[type=number]`. Typing 90 in row 0's number input → both inputs read 90. Dragging slider to 45 → number reads 45.
- Camera toggle → `cameraLocked` flips, `controls.enabled` mirrors `!cameraLocked`, button text + class flips, TC visibility + enabled mirrors lock state.
- Mode toggle → cluster mode sets `body.mode-cluster`, detaches TC, shows stub overlay; bench restores.
- Save assembled pose → emits `{ assembled: { folds: { ... }, captured: ..., note: "" } }` with no `transform` block — PR #19 shape preserved exactly.
- 002 (cut-line-first multi-cutaway) loads via legacy parser, pieceGroup wraps it, TC attaches.
- 113, 058 (panels-first) — same.
- DOM accessibility tree confirms top bar shows: Bench (active) | Cluster | Camera locked button; hint text updated.

What I couldn't visually verify in this headless setup: the corner gizmo's actual paint (the headless browser's `requestAnimationFrame` doesn't fire, so my modified animate loop — which renders the gizmo viewport after the main scene — never runs in eval). The structural correctness is verified (`gizmoScene` + `gizmoCamera` exist; viewport math matches three.js conventions); needs Alan's manual eyes-on confirmation in a real browser. Same caveat for: TransformControls handles visually appearing on the piece, worktable visual, and Shift-snap behavior.

## Branch / commit

Branch: `claude/preview-html-bench-cluster-foundation` (renamed from auto-generated `claude/keen-pike-b3322d` before first commit per CLAUDE.md).

Commit + push pending at session end.

## Open questions

- The corner gizmo viewport renders into a fixed 80×80 region anchored to the renderer canvas's bottom-right (CSS pixels). On very small viewports (< ~200px) the gizmo would dominate; on very large displays it's fine. No responsive sizing in v0 — defer if it surfaces.
- TransformControls' selectable Z-translate axis is included by default. For Bench mode, all three axes make sense (lift the piece off the worktable, slide it in any direction). PR B may want to constrain this — leaving fully 3D for now.
- The cut-line-first per-fold builder still hides the `assembledBadge` HTML string raw via `innerHTML` (then rehomes its children onto the row). Functional, but if a future pass refactors the cut-line-first slider builder, that's a clean place to migrate to fully-element construction.
- Headless screenshot timeout: `mcp__Claude_Preview__preview_screenshot` consistently times out on this page even though `canvas.toDataURL()` returns valid PNG bytes. Likely the screenshot tool waits for a frame that never paints in the headless rAF environment. Worked around with `toDataURL` + pixel sampling; flagged here in case it bites future verification.

## Next-session handoff

Two pieces of follow-up from this PR:

1. **Manual visual confirmation (Alan).** Open `preview.html?piece=071` in a real browser. Confirm:
   - Two interior holes are visible in the slab (the central cell + second cutout).
   - World-origin RGB axes show (50mm).
   - Corner gizmo (bottom-right, 80×80) shows RGB axes; orbiting the camera (toggle Camera free) rotates the gizmo in lockstep.
   - TransformControls handles appear on the piece when camera is locked. Drag an arrow → piece translates. Press R → handles become rotate rings. Press T → back to translate. Hold Shift while dragging a rotate ring → snaps to 15° increments. Hold Shift while translating → snaps to 5mm.
   - Worktable plane visible below the piece (dark gray).
   - Switch to Cluster mode → stub banner appears, per-piece UI hidden. Switch back → everything returns.
   - Number inputs next to the thickness, rotation (if axles), and global Fold-all sliders all type-snap correctly.

2. **PR B (Bench mode transform capture)** — the next CODE_PROMPT in the DECISIONS #13 sequence. Adds the per-piece transform UI (slider+number for tx/ty/tz + rx/ry/rz with the same `createSliderRow` helper PR A introduced), reads `assembled.transform` from the sidecar on load, and extends Save assembled pose to emit `{ folds, transform }` together. The TransformControls drag captures live into the transform sliders. Pendulum-cluster pose capture (the originally-blocked work that triggered DECISIONS #13) resumes against PR B once it ships.

PR C (Cluster mode multi-piece manipulation) follows PR B. PR D (Wall mode) deferred until subassembly authoring is far enough along to need it.
