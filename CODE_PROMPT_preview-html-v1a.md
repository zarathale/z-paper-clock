---
status: ready-for-code
started: 2026-05-02
owner: Zarathale (Alan)
target: preview-html-v1a
parent: preview-html-v1
---

## What You Are Doing and Why

Build the foundation half of `preview.html` — a single self-contained HTML file at the repo root that loads a per-piece SVG via drag-drop and renders the paper silhouette as a single flat extruded slab with the embedded scan as the front-face texture. This is the "no folds yet" rendering path: SVG parsing, silhouette extraction, three.js scene setup, single-slab geometry, axle markers, thickness slider, and console diagnostics.

This is v1a — the first half of a two-part split of the original `CODE_PROMPT_preview-html-v1.md` (which hit the 32000-output-token ceiling on two earlier Code attempts on 2026-05-01 and 2026-05-02). v1b layers polygon cutting + adjacency BFS + hinge hierarchy + fold animation onto the same `preview.html` after this ships. The split is for execution, not architecture: the unified design vision lives in the original prompt and remains the source of truth for design rationale.

v1a is checkable on its own — drop `inbox/069.svg` or `inbox/066.svg`, see the flat box-net or tube-net rendered as a single slab with the scan texture mapped on top, axle markers visible, thickness slider working. Folds parsed but unused (count printed to console; UI placeholder reserved for v1b).

---

## Prerequisites — confirm before starting

- `inbox/069.svg` exists with populated `folds-valley` (8 paths), `marks` (11 ellipses), `axles` (1 ellipse). Verify with: `grep -c '<g id="folds-valley">' inbox/069.svg`
- `inbox/066.svg` exists with populated `folds-valley` (20 paths), `folds-mountain` (2 paths), `marks` (16 ellipses + 1 rect). Verify with: `grep -c '<g id="folds-mountain">' inbox/066.svg`
- `source/pieces/069.png` and `source/pieces/066.png` exist (used as fallback alpha source if SVG-embedded PNG extraction fails).
- A modern browser that runs `file://` HTML cleanly (Chrome/Edge/Safari/Firefox). The viewer is opened by double-clicking `preview.html`; no dev server.
- No Python, Node, or build tooling needed for this milestone. Pure browser-side HTML/JS/CSS.
- No existing `preview.html` at repo root from prior failed attempts. As of 2026-05-02 the repo is clean (no `preview.html`, no commits on `claude/preview-html-v1` ahead of `main`). If a stale `claude/preview-html-v1` branch or worktree exists, prune before starting: `git branch -D claude/preview-html-v1` and `git worktree prune`.

---

## Read These Files First

1. `CLAUDE.md` — working conventions, especially "How This Project Divides Between Cowork and Code" and "Versioning Policy" (no version bump for this prototype; milestone label `preview-html-v1a` carries the identifier).
2. `CODE_PROMPT_preview-html-v1.md` — the unified prompt this split derives from. Architecture, layer model, and design rationale all live there. Treat it as required background; this prompt restates the v1a scope, not the design.
3. `work/SPEC-3D-VIEWER.md` — full viewer spec. The per-piece sidecar / layer-model section is the mental model.
4. `sessions/2026-05-01-2300_cowork_069-3d-viewer-build.md` — architectural context, layer encoding decisions (path-id-encoded fold angles, layer-default fallback, `<g id="root">` and `<g id="thickness">` semantics, Affinity round-trip results), Empty-Layer Behavior table. Required reading.
5. `outputs/069-test/cut.py` — Python diagnostic. **For v1a, only the silhouette-extraction sections are relevant** (marching squares on alpha). The cutter logic is v1b territory.
6. `outputs/066-test/run.py` — 066 diagnostic, including the SVG-path silhouette fallback for fully-opaque PNGs.
7. `work/pieces/069/piece-069-viewer.html` — prior 069-specific viewer. Useful as reference for three.js r128 setup (lights, materials, OrbitControls, alphaTest texture handling). Do not modify.

---

## Target File Structure Changes

```
z-paper-clock/
├── preview.html                                  ← NEW: this is what we author
├── sessions/
│   └── 2026-05-02-XXXX_code_preview-html-v1a.md  ← NEW: end-of-session note
└── CODE_PROMPT_preview-html-v1a.md               ← flip status to "shipped" at end
```

No other files touched.

---

## Numbered Tasks

### Task 1 — File skeleton and CDN imports

Create `preview.html` at repo root. Single self-contained HTML file: `<!DOCTYPE html>` + `<html>` + `<head>` (with inline `<style>`) + `<body>` (with the UI shell, an empty `<canvas>` host, an inline `<script>` block).

CDN imports — use these exact URLs (precedent from `work/pieces/069/piece-069-viewer.html`):

- Three.js r128: `https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`
- OrbitControls (matched to r128): `https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js`
- polygon-clipping (UMD bundle): `https://unpkg.com/polygon-clipping@0.15.7/dist/polygon-clipping.umd.js`

All three loaded in `<head>` via `<script src="...">`. Note: `polygon-clipping` exposes `window.polygonClipping` and is **not used in v1a** but is loaded now so v1b doesn't need to touch the import section. If a more reliable mirror is needed mid-session, `https://cdn.jsdelivr.net/npm/polygon-clipping@0.15.7/dist/polygon-clipping.umd.js` is acceptable.

### Task 2 — UI shell (v1a subset)

Page layout: a left-side controls panel (~320 px wide, fixed), a right-side canvas filling the rest. Controls panel sections, top to bottom:

1. **Drop zone.** A bordered rectangle with the text "Drop an SVG here, or click to pick a file." Clicking opens a file input dialog; drag-and-drop accepts `.svg` files. After load, replace with "Loaded: `<filename>`" + a "Reload" button (re-parses the cached file content from memory) + a "Pick another file" button.
2. **Status / banners.** A vertically stacked list of warning chips. Drives off the parsing pass: "no fold-valley layer", "no fold-mountain layer", "axles empty (no pivot marker)", "thickness layer missing — using 1.0 mm default", "root layer missing", silhouette-extraction failure messages, etc. Color-code: orange for "default applied", red for "render degraded", green/none when everything is clean.
3. **Fold-controls placeholder.** An empty `<div id="fold-controls">` with an HTML comment `<!-- populated in v1b: global fold slider + per-fold sliders -->` so v1b has a clear target. Render an italic "Fold controls — added in v1b" placeholder text inside it for clarity in v1a.
4. **Thickness slider.** Range 0.3–4.0 mm, default value = parsed thickness or 1.0 mm. Live-rebuilds slab geometry on change.
5. **Reset button.** Resets the thickness slider to its default. (No fold sliders to reset in v1a.)

Style: dark background (#1a1a1a), light text, sans-serif. No external CSS. Functional, not pretty.

### Task 3 — SVG parsing (full, including folds for v1b handoff)

Parse the dropped file's text via `DOMParser`. Extract:

- **viewBox** from `<svg>` attribute. Required. Bail with banner if absent.
- **Embedded scan PNG.** Look for `<image>` element (or `<use xlink:href="#_ImageN">` referencing a `<defs><image id="_ImageN" xlink:href="data:image/png;base64,...">`). Decode the base64 data URL and load into an `Image` element, then draw to an offscreen canvas to access pixel data.
- **Per-layer extraction.** For each `<g id="X">` in the document, where X ∈ {`folds-valley`, `folds-mountain`, `axles`, `root`, `thickness`}: record presence, child count, and child elements. Layers that aren't present or contain no usable children must degrade gracefully per the Empty-Layer Behavior table in the session note.

For path d-attribute parsing on fold lines: handle the subset that Affinity exports use — absolute `M`, relative `l`, absolute `L`, no curves on fold lines. Each fold line is a single straight segment of the form `M sx,sy l dx,dy` or `M sx,sy L ex,ey`. Extract `(start, end)` as `[sx, sy]` and `[sx+dx, sy+dy]` (or `[ex, ey]`). If a fold-layer path doesn't conform, skip it with a console warning rather than crashing.

For the `<text>` inside `<g id="thickness">`: read the text content, parse as `parseFloat`, default to 1.0 if NaN.

For the marker inside `<g id="root">`: accept any of `<ellipse>`, `<circle>`, `<rect>`, `<path>`. Compute its centroid in viewBox coords (for ellipse/circle: cx, cy; for rect: x+w/2, y+h/2; for path: parse vertices, average). Store the centroid; v1a doesn't use it for panel selection (only one panel exists), but v1b does.

For each fold path, parse the `id` attribute. Match against `^fold(?P<sign>[-+])(?P<deg>\d+(?:\.\d+)?)$`. If matched: signed angle = `(sign === '-' ? -1 : +1) * parseFloat(deg)`. If not: layer default — `folds-valley` → −90°, `folds-mountain` → +90°.

**Storage shape (so v1b can pick it up unchanged):** parse all five layers and stash into a single `parsed` object — e.g., `parsed = { viewBox, scanPng, folds: [{layer, id, start, end, defaultAngle}, ...], axles: [{cx, cy}, ...], rootCentroid, thicknessMm }`. v1a reads `viewBox`, `scanPng`, `axles`, `rootCentroid` (for diagnostics), and `thicknessMm`. v1a parses but does not consume `folds`.

### Task 4 — Silhouette extraction

Two paths, branched on alpha density:

**Primary (alpha-based).** Decode the embedded PNG to canvas pixel data. Count opaque pixels (alpha > 250) vs. total. If opaque-fraction < 0.99, treat as alpha-bearing and run marching squares on the alpha channel at threshold 0.5 to extract the silhouette polygon. Scale extracted vertices from PNG-pixel space into viewBox space via the embedded image's transform (look for `transform="matrix(sx,0,0,sy,tx,ty)"` on the `<use>` or `<image>` element; default to identity if absent).

**Fallback (SVG-path-based).** If opaque-fraction ≥ 0.99, the PNG provides no silhouette signal. Walk the SVG body (children of `<svg>`, excluding `<defs>` and the canonical metadata layers) for a closed colored path — any `<path>` with `style="...fill:#xxxxxx..."` and a `d` attribute that traces a closed shape. Parse the path d-string (handling absolute `M` + relative `l` + closing `z`) into a polygon. On 066, this is an orange `#e6611a` path with 34 vertices.

If neither path produces a usable silhouette: bail with a banner ("no silhouette found — check that the SVG has either an alpha-bearing scan or a colored silhouette path") and render an empty scene.

Marching-squares implementation: roll your own (small, ~50 lines). Reference: process the alpha grid, emit edge segments per cell based on the 16-case lookup, chain segments into a closed polygon. Simplify the output polygon with Ramer-Douglas-Peucker at ε ≈ 1 viewBox unit before passing downstream — this brings 069's 3015-vertex raw silhouette down to a few hundred without losing the silhouette shape.

### Task 5 — three.js scene setup

Standard r128 boilerplate: `WebGLRenderer({antialias: true, alpha: true})`, `PerspectiveCamera(60, aspect, 0.1, 10000)`, `Scene`. Lights:

- `AmbientLight(0xffffff, 0.6)`
- Two `DirectionalLight(0xffffff, 0.5)` at positions roughly `(1, 1, 1)` and `(-1, -1, 1)` relative to the scene center.

`OrbitControls` on the canvas. Initial camera position: framed to fit the silhouette bbox with ~30% padding. Compute camera distance from FOV + bounding box diagonal.

ViewBox-to-three.js scale: pick a constant such that 1 mm of paper ≈ 1 three.js unit. The 069 viewer used `1 mm / 4.14 mm-per-viewBox-unit ≈ 0.241`, but that was specific to its hardcoded geometry. For preview.html, derive: `UNITS_PER_MM = (viewBox_diagonal_mm) / (viewBox_diagonal_units)`, where `viewBox_diagonal_mm` is computed from the embedded scan's pixel dimensions assuming 600 DPI (`scan_diag_px / 600 * 25.4`). If the scan dimensions can't be determined, fall back to `UNITS_PER_MM = 1` and emit a banner warning ("scale unknown; thickness in viewBox units").

### Task 6 — Slab geometry (single slab in v1a)

Build a single `THREE.Shape` from the silhouette polygon vertices (in viewBox coords, centered on the silhouette bbox center). Extrude with `THREE.ExtrudeGeometry(shape, {depth: thicknessUnits, bevelEnabled: false})` where `thicknessUnits = thicknessMm * UNITS_PER_MM`.

Materials per face — three materials, applied via `geometry.groups`:

- **Front face** (the side facing +Z by default): `MeshStandardMaterial({map: scanTexture, transparent: true, alphaTest: 0.1, side: FrontSide})`. UV-mapped from the polygon's viewBox coords into the scan texture's `[0,1]` UV space.
- **Back face**: `MeshStandardMaterial({color: 0xf0e0c8 /* cream */, side: FrontSide})`.
- **Edge strips** (the extruded sides): `MeshStandardMaterial({color: 0xf0e0c8, side: DoubleSide})`. DoubleSide is necessary so edges remain visible from any orbit angle.

UV mapping: for each front-face vertex at viewBox coord `(vx, vy)`, the UV is `(vx / viewBox_w, 1 - vy / viewBox_h)` (Y flipped because SVG Y grows downward, UV Y grows upward).

ExtrudeGeometry produces two cap faces and the side strips. Use the `geometry.groups` indices that ExtrudeGeometry assigns: in r128, the front/back/sides correspond to specific group indices — verify empirically by coloring each group differently in a one-off debug pass before settling materials.

**Implement this as a function** like `buildSlab(polygon)` that takes a polygon (array of `[x, y]` viewBox-space vertices) and returns the configured `THREE.Mesh`. v1a calls it once with the silhouette. v1b will call it N times — one per cut polygon — without rewriting the function. Position the v1a slab at world origin.

### Task 7 — Axle markers

If `<g id="axles">` is populated: for each ellipse, add a small sphere (`SphereGeometry(radius=0.15 * UNITS_PER_MM, 16, 12)`, `MeshStandardMaterial({color: 0xff00ff})`) at the axle's centroid in viewBox coords (relative to the silhouette bbox center, matching the slab's local frame).

In v1a, all axle markers attach to the single slab. v1b will re-route each marker to the panel containing its centroid (point-in-polygon).

### Task 8 — Live rebuild on thickness change

Thickness slider triggers a slab geometry rebuild via `buildSlab(...)`. Use a debounced handler (50–100 ms) to avoid thrashing.

Reset button: reset thickness slider to default; trigger rebuild.

### Task 9 — Console diagnostics

On every load, print to the console (not the UI — debugging only):

```
[preview.html] Loaded <filename>
viewBox: <w>x<h>
Silhouette: <vertex count> verts, area <units²>
Fold lines: <N valley>, <M mountain>  (parsed but not rendered in v1a)
Root marker: <present | absent>, centroid (<x>, <y>)
Thickness: <mm> mm (source: <text-layer | default>)
Axles: <count>
UNITS_PER_MM: <value> (source: <derived-from-scan | fallback-1>)
```

v1b will extend this list with cut/adjacency/tree-depth diagnostics.

---

## Verification Checklist

1. `preview.html` exists at repo root, single self-contained file (verify: `wc -l preview.html`, confirm one file, no external assets beyond CDN scripts).
2. Open via `file://` (double-click). Page loads. Drop zone + thickness slider + (placeholder for v1b fold controls) + empty banner area render. No console errors before a file is dropped.
3. Drag-drop `inbox/069.svg`. Console reports: 8 valley folds, 0 mountain folds, 1 axle, root marker present.
4. 3D view shows a single flat slab with the box-net scan as the front face. Cream back face + edge strips visible from oblique angles. Magenta axle marker visible at the axle centroid.
5. Move thickness slider 1.0 → 4.0 mm. Slab thickness visibly grows; rebuild stutter < ~150 ms.
6. Reset button: returns thickness to default.
7. Drag-drop `inbox/066.svg`. Console reports: 20 valley folds, 2 mountain folds.
8. 3D view shows the long narrow tube-net silhouette as a single flat slab with the tube-net scan correctly mapped (silhouette extracted via the SVG-path fallback, since 066's PNG is fully opaque).
9. No console errors during any interaction. No NaN positions, no unhandled promise rejections, no missing-texture warnings.

---

## What NOT to Change

- Do not implement polygon cutting, adjacency, BFS, or hinge hierarchy. Those are v1b.
- Do not implement per-fold sliders or the global fold slider. Those are v1b.
- Do not modify `work/pieces/069/piece-069-viewer.html` (historical reference; preserved as the rectangular-slab predecessor).
- Do not author or modify any SVG files in `inbox/` or `source/pieces/`. The viewer is read-only against these.
- Do not create `work/viewer/`, `work/manifest.json`, or any per-piece JSON sidecars.
- Do not implement marks-layer rendering, glue-zones, labels, or cutouts-layer parsing.
- Do not bump `work/viewer/package.json` (doesn't exist yet, won't until M3).

---

## Manual tests (post-merge, on Alan's mac)

1. Pull `main` after merge. Verify `preview.html` is at repo root.
2. Double-click `preview.html` in Finder. Browser opens it via `file://`.
3. Drag-drop `inbox/069.svg`. Confirm single flat slab with box-net texture. Axle marker visible.
4. Drag-drop `inbox/066.svg`. Confirm single flat slab with tube-net texture (SVG-path silhouette fallback in play).
5. Adjust thickness slider. Confirm rebuild is smooth.
6. Test the "Reload" button after edits to the dropped file's source (e.g., manually rename a path id, drop the modified copy, confirm console reflects the change).

If any test surfaces an unexpected behavior, capture it in the session note's "Known issues at ship" section. Don't hold the merge for non-critical issues — v1a is a foundation; minor render glitches that don't block validation are acceptable and tracked for follow-up in v1b.

---

## Branch / commit / PR

- **Branch:** `claude/preview-html-v1a` (per CLAUDE.md naming rule — no auto-generated random names; if Code starts on an auto-generated branch, rename before first commit)
- **Commit subject** (imperative, lowercase, ≤70 chars): `add preview.html: parsing + flat slab render (v1a, no folds)`
- **PR title:** same as commit subject
- **PR description:**
  - One-line summary
  - "What changed" — `preview.html` → NEW; `sessions/...` → NEW session note
  - Manual test steps (link to "Manual tests" section above)
  - Branch name + commit SHA
  - Link to this prompt file

---

## End-of-session

1. Write the session note at `sessions/2026-05-02-XXXX_code_preview-html-v1a.md` per the CLAUDE.md sessions convention. Include: branch name, commit SHA, what was done, what's in the PR, function/variable names that v1b should reuse (especially the `buildSlab` signature and the `parsed` object shape), any known issues at ship.
2. Flip this prompt's front-matter `status` from `ready-for-code` to `shipped`. Add `shipped: 2026-05-02` (or the actual ship date) in the front matter. Add the italic header below the front matter:
   `_Shipped YYYY-MM-DD; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._`
3. Push branch, open PR via `gh pr create` directly. Return PR URL in the final chat message.
