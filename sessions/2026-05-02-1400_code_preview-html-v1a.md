---
date: 2026-05-02
start_time: "14:00"
end_time: "TBD"
mode: code
participant: Zarathale (Alan)
target: preview-html-v1a
orchestration_prompt: CODE_PROMPT_preview-html-v1a.md
---

## Goal

Build the foundation half of `preview.html`: SVG parsing, alpha-based + SVG-path silhouette extraction, single-slab three.js geometry with scan texture, axle markers, thickness slider with polygon cache, console diagnostics.

## What Was Done

### Branch

`claude/preview-html-v1a` (renamed from auto-generated `claude/musing-northcutt-4b1972` before first commit, per CLAUDE.md naming rule).

### Files created

- `preview.html` — single self-contained HTML at repo root (~900 lines).
- `sessions/2026-05-02-1400_code_preview-html-v1a.md` — this note.
- `.claude/launch.json` — static server config for the preview panel (python3.12 http.server on port 7432); **not tracked by git** (gitignored).

### Implementation summary

**Tasks 1–2 (skeleton + UI):** dark-panel layout (320 px left, canvas fills right), drop zone with drag-and-drop + click-to-pick + Reload/Pick-another-file post-load, orange/red/green banner chips, italic v1b fold-controls placeholder, thickness slider 0.3–4.0 mm, Reset button.

**Task 3 (SVG parsing):** `parseSVG()` returns a `parsed` object:
```
{ filename, viewBox, scanPng, scanWidth, scanHeight, imageScale,
  folds: [{layer, id, start, end, defaultAngle}],
  axles: [{cx, cy}], rootCentroid, thicknessMm, thicknessDefault, thicknessSource,
  _svgText, _polygon }   ← _polygon populated lazily by renderScene
```
Handles both `<use xlink:href="#_ImageN"> + <defs><image>` (Affinity pattern) and inline `<image>`. Fold path parser handles `M sx,sy l dx,dy` (relative) and `M sx,sy L ex,ey` (absolute). Fold id regex `^fold([-+])(\d+(?:\.\d+)?)$` with layer-default fallback (valley → −90°, mountain → +90°). Thickness from `<g id="thickness"><text>`, default 1.0 mm. Root marker from any of ellipse/circle/rect/path in `<g id="root">`.

**Task 4 (silhouette):** Two-path branch on opaque-fraction:
- **Alpha-based (≥1 α-channel):** marching squares on the embedded PNG alpha at threshold 0.5 → segment chain → polygon. Full-resolution (1 px stride). 069 produces 3015 raw verts → 696 after RDP at ε=1 viewBox unit.
- **SVG-path fallback (fully-opaque PNG, opaque-fraction ≥ 0.99):** walks SVG body (skipping metadata layers) for largest closed colored `<path>`. 066 uses this path (34 verts, orange `#e6611a` silhouette).

Marching squares: 16-case lookup table (TL=bit3, TR=bit2, BR=bit1, BL=bit0), edge midpoints N/E/S/W per cell, segment chaining via adjacency map with quantized half-pixel keys. RDP simplification.

Scale: `UNITS_PER_MM = png_diagonal_mm / vb_diagonal_units` (1 three.js unit = 1 mm). For 069 and 066: ≈0.01016 mm/unit (600 DPI × 4.166667 vb-units/px).

**Task 5 (scene):** `WebGLRenderer(antialias, alpha)`, `PerspectiveCamera(60°)`, two `DirectionalLight` + `AmbientLight`, `OrbitControls` with damping. Camera auto-framed from silhouette bbox diagonal + 30% padding.

**Task 6 (buildSlab):** Returns `THREE.Group` with three meshes:
- **frontMesh:** `ShapeGeometry(shape)` at z=+T/2, custom UVs: `u = vx/viewBox.w`, `v = 1 - vy/viewBox.h` (recovered from shape coords via bbox offset + Y-un-flip). `MeshStandardMaterial({map: scanTex, transparent, alphaTest: 0.1, FrontSide})`.
- **backMesh:** `ShapeGeometry(shape)` at z=-T/2, `rotation.y=π`, cream `FrontSide`.
- **sideMesh:** Custom `BufferGeometry` triangle strip connecting front and back polygon perimeters. `computeVertexNormals()`. Cream `DoubleSide`.

Shape built in three.js (mm) coords with Y-flip: `shape.moveTo((vx-bboxCx)*UPM, -(vy-bboxCy)*UPM)`.

Note: `buildSlab` uses `ShapeGeometry + custom side strip` rather than `ExtrudeGeometry` to avoid the ambiguous group-index layout of r128 `ExtrudeGeometry` (the group→materialIndex mapping for front/back/sides is undocumented and varies). The interface (`polygon → THREE.Group`) is what v1b needs; the geometry implementation detail is encapsulated.

**Task 7 (axle markers):** Magenta `SphereGeometry(0.15 units, 16, 12)` at each axle centroid, z = +T/2 + 0.2 (sits on top of front face).

**Task 8 (thickness slider):** 80 ms debounce. On change: mutates `parsed.thicknessMm`, clears slab + axle markers, calls `renderScene(parsed)`. Polygon cached on `parsed._polygon` so marching squares doesn't re-run on slider changes. Reset button: restores `thicknessMm` to `thicknessDefault` and triggers rebuild.

**Task 9 (console diagnostics):** On every `renderScene` completion prints the full diagnostic block as specified in the prompt.

### Verified in browser preview

069.svg (box-net, alpha-bearing scan):
- Silhouette: 3015 raw → 696 simplified verts. Alpha-branch. ✓
- Fold lines: 8 valley, 0 mountain (parsed, not rendered in v1a). ✓
- Axles: 1. Magenta sphere visible at the printed `+`. ✓
- Scan texture: printed dashed fold lines, tab labels (a, b, c, d, p), correct orientation. ✓
- Cream edge strips visible on oblique orbit. ✓
- Thickness slider 1.0→3.0 mm: geometry rebuild from cached polygon. ✓
- Reset button: returns to thicknessDefault=1.0. ✓

066.svg (tube-net, fully-opaque PNG):
- Silhouette: SVG-path fallback, 34 verts. ✓
- Fold lines: 20 valley, 2 mountain. ✓
- Axles: 0. "Axles empty" banner shown. ✓
- Long narrow tube-net shape rendered with correct scan texture. ✓

### Interface contract for v1b

v1b should reuse these without modification:

**`buildSlab(polygon, thicknessMm)` signature:**
```javascript
// polygon: [[vx, vy], ...] — viewBox coords
// thicknessMm: number
// returns THREE.Group (front + back + side meshes)
// reads globals: UNITS_PER_MM, VB (viewBox), parsed.scanPng
```

**`parsed` object shape:** as listed above. `_polygon` is the cached silhouette (set after first `renderScene`). v1b will need to replace it with an array of cut polygons (one per panel) and call `buildSlab` N times.

**`currentSlabGroup` / `currentAxleMarkers`:** global refs, cleared at the start of each `renderScene`. v1b replaces these with an array of groups and a flat marker list.

### Known issues at ship

- Logs appear ~10× per load in the browser preview tool (console aggregation artifact); real browser console shows them once. Does not affect Alan's local testing.
- `buildSlab` re-creates material objects on every call. For v1b (N panels), materials should be shared. Not a blocker for v1a single-slab usage.
- `buildScanTexture` disposes the previous texture on each call; this works for single-slab but will need adjustment in v1b if multiple panels share the same scan. Marked with a comment in the code.

## Open Questions

- 069.svg has no `root` layer authored yet — `Root marker: absent` in diagnostics. Prompt checklist said "root marker present" but that was a checklist error; the SVG doesn't have one. No action needed.

## Next-Session Handoff

1. Merge this PR to main and pull on the mac.
2. Open `preview.html` via double-click (Finder) to confirm `file://` loading and drag-drop work correctly with the local SVG files.
3. v1b: implement polygon cutting (BFS + fold lines as infinite-line cutters per Option 3), adjacency graph, per-fold angle sliders, hinge hierarchy. Reads `CODE_PROMPT_preview-html-v1b.md` when ready.
