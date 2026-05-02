---
status: ready-for-code
started: 2026-05-02
owner: Zarathale (Alan)
target: preview-html-v1
---

## What You Are Doing and Why

Build `preview.html` at the repo root — a single self-contained HTML file that renders any per-piece SVG (from `inbox/` or eventually `work/pieces/NNN/`) as a 3D paper model with hinge animation. The viewer loads via drag-drop, parses the SVG's canonical layers (`folds-valley`, `folds-mountain`, `axles`, `root`, `thickness`), cuts the paper silhouette into per-panel polygons using fold lines as infinite-line cutters, builds a fold-tree by BFS over the panel adjacency graph, and renders each panel as an extruded slab with the embedded scan as the front-face texture. v1 is **read-only** — no SVG writeback, no JSON sidecars touched.

This replaces the piece-069-specific rectangular-slab viewer at `work/pieces/069/piece-069-viewer.html` with a piece-agnostic prototype. The polygon-cut algorithm (Option 3) was validated on `inbox/069.svg` (box net, 13 panels) and `inbox/066.svg` (tube net, 22 panels) in `outputs/069-test/` and `outputs/066-test/` during the 2026-05-01 evening session — same algorithm produces clean panels for both topologies. v1 read-only first lets us validate the rendering path before adding writeback complexity in a separate v2 prompt. The prototype lives at repo root (`preview.html`) and is deliberately distinct from `work/viewer/` (the production Vite app, scheduled for M3).

---

## Prerequisites — confirm before starting

- `inbox/069.svg` exists with populated `folds-valley` (8 paths), `marks` (11 ellipses), `axles` (1 ellipse). Verify with: `grep -c '<g id="folds-valley">' inbox/069.svg`
- `inbox/066.svg` exists with populated `folds-valley` (20 paths), `folds-mountain` (2 paths), `marks` (16 ellipses + 1 rect). Verify with: `grep -c '<g id="folds-mountain">' inbox/066.svg`
- `source/pieces/069.png` and `source/pieces/066.png` exist (used as fallback alpha source if SVG-embedded PNG extraction fails)
- A modern browser that runs `file://` HTML cleanly (Chrome/Edge/Safari/Firefox). The viewer is opened by double-clicking `preview.html`; no dev server.
- No Python, Node, or build tooling needed for this milestone. Pure browser-side HTML/JS/CSS.

---

## Read These Files First

1. `CLAUDE.md` — working conventions, especially "How This Project Divides Between Cowork and Code" and "Versioning Policy" (this milestone is pre-v0.1.0 — no version bump for the prototype, milestone label `preview-html-v1` carries the identifier)
2. `work/SPEC-3D-VIEWER.md` — full viewer spec. The per-piece sidecar / layer-model section is the mental model; v1 implements a subset (silhouette + folds + axles + root + thickness). Two SPEC revisions are queued in the prior session note but **do not block this prompt** — the architecture is captured below and in §"Architectural decisions settled in this session" of the session note.
3. `sessions/2026-05-01-2300_cowork_069-3d-viewer-build.md` — full architectural context. Required reading. Contains the Option 3 validation walk-through on 069 and 066, the layer encoding decisions (path-id-encoded fold angles, layer-default fallback, `<g id="root">` and `<g id="thickness">` semantics, Affinity round-trip results), and the fold-tree algorithm specification.
4. `outputs/069-test/cut.py` and `outputs/069-test/verify.py` — the Python diagnostic scripts that produced the 13-panel cut on 069. Use as reference for the JS port: same silhouette extraction (marching squares on alpha), same infinite-line-cutter approach. The shapely-equivalent step in JS uses `polygon-clipping` (see Task 4).
5. `outputs/066-test/run.py` — the diagnostic for 066, including the SVG-path silhouette fallback for fully-opaque PNGs.
6. `work/pieces/069/piece-069-viewer.html` — the prior 069-specific viewer. Useful as reference for three.js r128 setup (lights, materials, OrbitControls, alphaTest texture handling). Do not modify; preserved as historical reference.

---

## Target File Structure Changes

```
z-paper-clock/
├── preview.html                                ← NEW: this is what we author
├── sessions/
│   └── 2026-05-02-XXXX_code_preview-html-v1.md ← NEW: end-of-session note
└── CODE_PROMPT_preview-html-v1.md              ← flip status to "shipped" at end
```

No other files touched. No additions to `work/` (the eventual production viewer at `work/viewer/` is M3, not now).

---

## Numbered Tasks

### Task 1 — File skeleton and CDN imports

Create `preview.html` at repo root. Single self-contained HTML file: `<!DOCTYPE html>` + `<html>` + `<head>` (with inline `<style>`) + `<body>` (with the UI shell, an empty `<canvas>` host, an inline `<script>` block).

CDN imports — use these exact URLs (precedent from `work/pieces/069/piece-069-viewer.html`):

- Three.js r128: `https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`
- OrbitControls (matched to r128): `https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js`
- polygon-clipping (UMD bundle): `https://unpkg.com/polygon-clipping@0.15.7/dist/polygon-clipping.umd.js`

All three loaded in `<head>` via `<script src="...">`. Note: `polygon-clipping` exposes `window.polygonClipping`. If a more reliable mirror is needed mid-session, `https://cdn.jsdelivr.net/npm/polygon-clipping@0.15.7/dist/polygon-clipping.umd.js` is acceptable. If `polygon-clipping` proves unsuitable (e.g., a robustness issue mid-implementation), `martinez-polygon-clipping@0.7.3` is an acceptable swap; document the swap reason in the session note.

### Task 2 — UI shell

Page layout: a left-side controls panel (~320 px wide, fixed), a right-side canvas filling the rest. Controls panel sections, top to bottom:

1. **Drop zone.** A bordered rectangle with the text "Drop an SVG here, or click to pick a file." Clicking opens a file input dialog; drag-and-drop accepts `.svg` files. After load, replace with "Loaded: `<filename>`" + a "Reload" button (re-parses the cached file content from memory) + a "Pick another file" button.
2. **Status / banners.** A vertically stacked list of warning chips. Drives off the parsing pass: "no fold-valley layer", "no fold-mountain layer", "axles empty (no pivot marker)", "thickness layer missing — using 1.0 mm default", "root layer missing — using largest panel by area", etc. Color-code: orange for "default applied", red for "render degraded", green/none when everything is clean.
3. **Global fold slider.** Range 0–100%. Drives every hinge from 0 to its target angle proportionally.
4. **Per-fold sliders.** Auto-generated from the parsed fold lines, one slider per unique SVG path id. Label = path id (or `valley-N` / `mountain-N` if no id assigned). Range −180° to +180°. Default value = the path-id-encoded angle, or the layer default (−90 valley, +90 mountain) if no id encoding. Read-only metadata badge: how many hinges this path drives (most are "1 hinge"; on 069, paths 2 and 3 each drive "2 hinges").
5. **Thickness slider.** Range 0.3–4.0 mm, default value = parsed thickness or 1.0 mm. Live-rebuilds slab geometry on change.
6. **Reset button.** Resets all sliders to their defaults (does not reload the file).

Style: dark background (#1a1a1a), light text, sans-serif. No external CSS. Keep it functional, not pretty.

### Task 3 — SVG parsing

Parse the dropped file's text via `DOMParser`. Extract:

- **viewBox** from `<svg>` attribute. Required. Bail with banner if absent.
- **Embedded scan PNG.** Look for `<image>` element (or `<use xlink:href="#_ImageN">` referencing a `<defs><image id="_ImageN" xlink:href="data:image/png;base64,...">`). Decode the base64 data URL and load into an `Image` element, then draw to an offscreen canvas to access pixel data.
- **Per-layer extraction.** For each `<g id="X">` in the document, where X ∈ {`folds-valley`, `folds-mountain`, `axles`, `root`, `thickness`}: record presence, child count, and child elements. Layers that aren't present or contain no usable children must degrade gracefully per the Empty-Layer Behavior table in the session note.

For path d-attribute parsing on fold lines: handle the subset that Affinity exports use — absolute `M`, relative `l`, absolute `L`, no curves on fold lines. Each fold line is a single straight segment of the form `M sx,sy l dx,dy` or `M sx,sy L ex,ey`. Extract `(start, end)` as `[sx, sy]` and `[sx+dx, sy+dy]` (or `[ex, ey]`). If a fold-layer path doesn't conform, skip it with a console warning rather than crashing.

For the `<text>` inside `<g id="thickness">`: read the text content, parse as `parseFloat`, default to 1.0 if NaN.

For the marker inside `<g id="root">`: accept any of `<ellipse>`, `<circle>`, `<rect>`, `<path>`. Compute its centroid in viewBox coords (for ellipse/circle: cx, cy; for rect: x+w/2, y+h/2; for path: parse vertices, average). The viewer needs only the centroid — not the marker geometry.

For each fold path, parse the `id` attribute. Match against `^fold(?P<sign>[-+])(?P<deg>\d+(?:\.\d+)?)$`. If matched: signed angle = `(sign === '-' ? -1 : +1) * parseFloat(deg)`. If not: layer default — `folds-valley` → −90°, `folds-mountain` → +90°.

### Task 4 — Silhouette extraction

Two paths, branched on alpha density:

**Primary (alpha-based).** Decode the embedded PNG to canvas pixel data. Count opaque pixels (alpha > 250) vs. total. If opaque-fraction < 0.99, treat as alpha-bearing and run marching squares on the alpha channel at threshold 0.5 to extract the silhouette polygon. Scale extracted vertices from PNG-pixel space into viewBox space via the embedded image's transform (look for `transform="matrix(sx,0,0,sy,tx,ty)"` on the `<use>` or `<image>` element; default to identity if absent).

**Fallback (SVG-path-based).** If opaque-fraction ≥ 0.99, the PNG provides no silhouette signal. Walk the SVG body (children of `<svg>`, excluding `<defs>` and the canonical metadata layers) for a closed colored path — any `<path>` with `style="...fill:#xxxxxx..."` and a `d` attribute that traces a closed shape. Parse the path d-string (handling absolute `M` + relative `l` + closing `z`) into a polygon. On 066, this is an orange `#e6611a` path with 34 vertices.

If neither path produces a usable silhouette: bail with a banner ("no silhouette found — check that the SVG has either an alpha-bearing scan or a colored silhouette path") and render an empty scene.

Marching-squares implementation: roll your own (small, ~50 lines). Reference: process the alpha grid, emit edge segments per cell based on the 16-case lookup, chain segments into a closed polygon. Simplify the output polygon with Ramer-Douglas-Peucker at ε ≈ 1 viewBox unit before passing downstream — this brings 069's 3015-vertex raw silhouette down to a few hundred without losing the silhouette shape.

### Task 5 — Polygon cut

Given the silhouette polygon and N fold lines:

1. Compute the silhouette bbox + 100-unit margin. Call this `bigBox`.
2. For each fold line, extend it to an infinite-line cutter: parameterize the line (point + unit direction), then construct a half-plane polygon from `bigBox` clipped on each side of the line. Two half-plane polygons per fold line.
3. Maintain `regions` = array of `{polygon, edgeTags}`. Initialize with `[{polygon: silhouette, edgeTags: ['silhouette' for each edge]}]`.
4. For each fold line F (in input order):
   - For each region R in `regions`: intersect `R.polygon` with each of F's two half-planes via `polygonClipping.intersection`. This produces 0, 1, or more sub-polygons per half.
   - For each new sub-polygon, propagate edge tags: edges of R that survive get their original tag; new edges (introduced by the cut) get tagged with `F` (the fold line's id, or a synthetic id like `valley-3` if no id).
   - Replace R in `regions` with all sub-polygons.

Edge-tag propagation in detail: after a cut by F, every edge of the result polygon either (a) lies along F (within ε ≈ 0.5 viewBox units of F's infinite line) → tag = F, or (b) lies on an edge of the input R → inherit R's tag for that edge. Match output edges to input edges by midpoint distance.

Sliver filter — drop any region whose **every** vertex lies within Δ of a single fold line (signature: thin strips along a cut). Δ = 0.5% of the silhouette-bbox diagonal. Geometric, scale-invariant. Replaces the size-based "drop regions < 1% of largest" filter, which was confirmed fragile in the 066 validation pass (smallest-real-panel:largest-sliver gap was only 2× on 066).

Expected outputs: 069 → 13 polygons. 066 → 22 polygons. Bail with banner if the result is wildly different (e.g., < 3 panels — likely the cut algorithm broke).

### Task 6 — Adjacency graph and BFS

Build a graph where nodes are polygons and edges are fold-line segments shared between polygon pairs:

1. For each fold line F, collect the polygons that have at least one edge tagged F. Each pair of such polygons is potentially adjacent via F.
2. For each candidate pair (P_i, P_j) sharing tag F: check that they share an edge of nonzero length on F's line. Specifically: collect P_i's F-tagged edges and P_j's F-tagged edges; check whether any pair of edges (one from each) overlap on F's line by more than ε ≈ 1 viewBox unit. If yes: P_i and P_j are adjacent via F. Corner-touches (zero-length overlap) don't count.

Identify root:

- If `<g id="root">` had a marker: find the polygon containing the marker centroid (point-in-polygon test). Root = that polygon. If no polygon contains the marker, fall back to the largest-by-area heuristic and emit a banner warning.
- Otherwise: root = polygon with largest area.

BFS from root over the adjacency graph. Each non-root polygon V records `parent(V) = U` and `hinge(V) = F` from the BFS edge that first reached it. Iterate over fold lines in deterministic order (by parsed input index) so the tree is reproducible across reloads.

If BFS doesn't reach some polygon: it's an orphan. Render it flat at its silhouette position with a banner warning. Do not crash.

### Task 7 — three.js scene setup

Standard r128 boilerplate: `WebGLRenderer({antialias: true, alpha: true})`, `PerspectiveCamera(60, aspect, 0.1, 10000)`, `Scene`. Lights:

- `AmbientLight(0xffffff, 0.6)`
- Two `DirectionalLight(0xffffff, 0.5)` at positions roughly `(1, 1, 1)` and `(-1, -1, 1)` relative to the scene center.

`OrbitControls` on the canvas. Initial camera position: framed to fit the silhouette bbox with ~30% padding. Compute camera distance from FOV + bounding box diagonal.

ViewBox-to-three.js scale: pick a constant such that 1 mm of paper ≈ 1 three.js unit. The 069 viewer used `1 mm / 4.14 mm-per-viewBox-unit ≈ 0.241`, but that was specific to its hardcoded geometry. For preview.html, derive: viewBox dimensions in pixels of the original scan × DPI conversion (specs say ~600 DPI on the gen-2 captures, viewBox roughly matches scan PNG size × 4.166667). Take the simpler path: pick `UNITS_PER_MM = (viewBox_diagonal_mm) / (viewBox_diagonal_units)`, where `viewBox_diagonal_mm` is computed from the embedded scan's pixel dimensions assuming 600 DPI (`scan_diag_px / 600 * 25.4`). If the scan dimensions can't be determined, fall back to `UNITS_PER_MM = 1` and emit a banner warning ("scale unknown; thickness in viewBox units").

### Task 8 — Slab geometry

For each polygon (with edge tags from Task 5):

1. Build a `THREE.Shape` from polygon vertices (in viewBox coords, centered on the silhouette bbox center).
2. Extrude with `THREE.ExtrudeGeometry(shape, {depth: thicknessUnits, bevelEnabled: false})` where `thicknessUnits = thicknessMm * UNITS_PER_MM`.
3. Materials per face — three materials per slab, applied via `geometry.groups`:
   - **Front face** (the side facing +Z by default): `MeshStandardMaterial({map: scanTexture, transparent: true, alphaTest: 0.1, side: FrontSide})`. UV-mapped from the polygon's viewBox coords into the scan texture's `[0,1]` UV space.
   - **Back face**: `MeshStandardMaterial({color: 0xf0e0c8 /* cream */, side: FrontSide})`.
   - **Edge strips** (the extruded sides): `MeshStandardMaterial({color: 0xf0e0c8, side: DoubleSide})`. DoubleSide is necessary so edges remain visible from any orbit angle.

The split into three materials (vs. the 069 viewer's two) is intentional and was the resolution to the cream-bleed bug in the 069 viewer build. Front and back use `FrontSide` so the back face never bleeds through alpha-discarded front pixels.

UV mapping: for each front-face vertex at viewBox coord `(vx, vy)`, the UV is `(vx / viewBox_w, 1 - vy / viewBox_h)` (Y flipped because SVG Y grows downward, UV Y grows upward). This maps the slab onto the scan texture in viewBox-aligned space.

ExtrudeGeometry produces two cap faces and the side strips. Use the `geometry.groups` indices that ExtrudeGeometry assigns: in r128, the front/back/sides correspond to specific group indices — verify empirically by coloring each group differently in a one-off debug pass before settling materials.

### Task 9 — Hinge hierarchy

Each non-root slab is a child of its parent's slab via an intermediate `Object3D` (the hinge):

1. Root slab: positioned at world origin, no parent.
2. For each non-root slab V with `parent(V) = U` and `hinge(V) = F`:
   - Create an `Object3D` (the hinge). Position it at the midpoint of F (the shared edge between U and V), expressed in V's local-coordinate frame. Orient it so its rotation axis is along F's direction.
   - Parent the hinge to U's slab. Parent V's slab to the hinge.
   - The hinge's rotation around its axis is the animation parameter.

The cleanest way to handle "hinge axis along F's direction" without trig: position the hinge at F's midpoint, then translate V's slab so that F's midpoint sits at the hinge's local origin. Then rotate the hinge around the axis from F's start to F's end. Quaternion approach: `hinge.quaternion.setFromAxisAngle(axis, currentAngle)`.

Per-fold sliders update the angles of all hinges driven by the same path id simultaneously (the "same fold path → same angle" rule from the session note). Maintain a map `pathId → [hinge, hinge, ...]` so a slider change iterates and updates all of them.

Global fold slider drives `t ∈ [0, 1]`; each hinge's angle = `t * targetAngle` for that hinge.

### Task 10 — Axle markers

If `<g id="axles">` is populated: for each ellipse, find which polygon contains its centroid. Add a small sphere (`SphereGeometry(radius=0.15 * UNITS_PER_MM, 16, 12)`, `MeshStandardMaterial({color: 0xff00ff})`) at the axle's centroid, positioned in that polygon's local frame so it rides along when the polygon folds.

The sphere is always visible regardless of orbit angle — that's the point. It marks a *position*, not a printed mark on the paper.

### Task 11 — Live rebuild on slider changes

Three sliders trigger different rebuilds:

- **Per-fold slider**: cheap. Update the relevant hinges' rotation only. No geometry rebuild.
- **Global fold slider**: cheap. Update every hinge's rotation. No geometry rebuild.
- **Thickness slider**: expensive. Rebuild slab geometries. Use a debounced handler (50–100 ms) to avoid thrashing.

Reset button: reset all sliders to defaults; trigger global update.

### Task 12 — Console diagnostics

On every load, print to the console (not the UI — debugging only):

```
[preview.html] Loaded <filename>
viewBox: <w>x<h>
Silhouette: <vertex count> verts, area <units²>
Fold lines: <N valley>, <M mountain>
Polygons after cut: <K>
Slivers filtered: <S>
Root: polygon at centroid (<x>, <y>), area <units²>, source: <root-marker | largest-by-area>
Tree depth: <D>
Orphans: <count>
Thickness: <mm> mm (source: <text-layer | default>)
Per-fold paths: [<id>: <hinge_count> hinges, default <angle>°, ...]
```

Helps debug new pieces without re-running the Python diagnostic scripts.

---

## Verification Checklist

1. `preview.html` exists at repo root, single self-contained file (verify: `wc -l preview.html` and confirm one file, no external assets beyond CDN scripts).
2. Open `preview.html` in Chrome via `file://` (double-click). Page loads. Drop zone + empty controls panel render. No console errors before any file is dropped.
3. Drag-drop `inbox/069.svg` onto the drop zone. Console reports: 13 polygons, 8 fold lines (valley), 0 mountain folds, 0 orphans. Banners may report "no folds-mountain layer" — that's expected for 069.
4. 3D view shows the unfolded box net flat (BASE in center, walls + corners + ext tabs around it). Scan texture mapped correctly across all panels.
5. Move the global fold slider 0 → 100%. The box folds up correctly: walls rotate up, then corners + ext tabs fold to vertical. Some panels may interpenetrate at intermediate angles — that's expected without phase sequencing.
6. Move thickness slider 1.0 → 4.0 mm. Slab thickness visibly grows.
7. Find the per-fold slider for path id `fold-90` (or similar) corresponding to one of the BASE↔WALL hinges. Move from −90° to 0°: that one wall returns to flat while the others stay folded.
8. Drop `inbox/066.svg`. Console reports: 22 polygons, 20 fold-valley + 2 fold-mountain, 0 orphans.
9. 3D view shows the long narrow tube net flat. Global fold slider folds it into the tube shape (with the two mountain folds bending opposite to the valleys).
10. No console errors during any interaction. No NaN positions, no unhandled promise rejections, no missing-texture warnings.

---

## What NOT to Change

- Do not modify `work/pieces/069/piece-069-viewer.html` (historical reference; preserved as the rectangular-slab predecessor).
- Do not author or modify any SVG files in `inbox/` or `source/pieces/`. The viewer is read-only against these.
- Do not create `work/viewer/`, `work/manifest.json`, or any per-piece JSON sidecars — those belong to M3 and the production viewer, not this prototype.
- Do not implement SVG writeback ("Export updated SVG" button). That is v2, scoped to a separate prompt after v1 ships.
- Do not implement marks-layer rendering, glue-zones, labels, or cutouts-layer parsing. v1 is silhouette + folds + axles + root + thickness, nothing else.
- Do not implement phase sequencing on the global fold slider (069's "walls then tabs"). Single global slider 0–100% drives all hinges proportionally for v1.
- Do not bump `work/viewer/package.json` (doesn't exist yet, won't until M3).

---

## Manual tests (post-merge, on Alan's mac)

1. Pull `main` after merge. Verify `preview.html` is at repo root.
2. Double-click `preview.html` in Finder. Browser opens it via `file://`.
3. Drag-drop `inbox/069.svg`. Confirm 13-panel render. Move global fold slider through full range. Confirm hinges work.
4. Drag-drop `inbox/066.svg`. Confirm 22-panel render with mountain folds bending opposite to valleys.
5. Pick any per-fold slider; sweep through −180° to +180°. Confirm only that hinge's panel(s) move (and that paths driving multiple hinges, like 069's path 2, move both hinges in sync).
6. Adjust thickness slider. Confirm rebuild is smooth (no stutters > ~150 ms).
7. Test the "Reload" button after edits to the dropped file's source: does re-parse pick up changes? (E.g., manually rename a path id from `fold-90` to `fold-60` in a copy of the SVG, drop the modified copy, confirm the angle changes.)

If any test surfaces an unexpected behavior, capture it in the session note's "Known issues at ship" section. Don't hold the merge for non-critical issues — v1 is a prototype; minor render glitches that don't block validation are acceptable and tracked for follow-up.

---

## Branch / commit / PR

- **Branch:** `claude/preview-html-v1` (per CLAUDE.md naming rule — no auto-generated random names)
- **Commit subject** (imperative, lowercase, ≤70 chars): `add preview.html: standalone svg-driven 3d viewer (v1 read-only)`
- **PR title:** same as commit subject
- **PR description:**
  - One-line summary
  - "What changed" — `preview.html` → NEW; `sessions/...` → NEW session note
  - Manual test steps (link to "Manual tests" section above)
  - Branch name + commit SHA
  - Link to this prompt file

---

## End-of-session

1. Write the session note at `sessions/2026-05-02-XXXX_code_preview-html-v1.md` per the CLAUDE.md sessions convention. Include: branch name, commit SHA, what was done, what's in the PR, any known issues at ship.
2. Flip this prompt's front-matter `status` from `ready-for-code` to `shipped`. Add `shipped: 2026-05-02` (or the actual ship date) in the front matter. Add the italic header below the front matter:
   `_Shipped YYYY-MM-DD; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._`
3. Push branch, open PR via `gh pr create` directly. Return PR URL in the final chat message.
