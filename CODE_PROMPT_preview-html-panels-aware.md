---
status: ready-for-code
started: 2026-05-05
owner: Zarathale (Alan)
target: preview-html-panels-aware
---

# CODE_PROMPT — panels-aware parser pathway in `preview.html`

Single-piece scope. Add a panels-first parser pathway alongside the existing cut-line-first one, so SVGs with `<g id="panels">` render via the panels-aware path; SVGs without it fall through to legacy cut-line-first. Multi-piece scene assembly comes in a follow-up prompt.

---

## What You Are Doing and Why

The 2026-05-05 cowork session ratified the panels-first authoring conventions across an end-to-end batch of 9 pieces (065/066/067/068/069/070/071/072 + 099). The connection-graph audit script (`claude-work/scripts/build_assembly_graph.py`) reads these SVGs and resolves all 24 cross-piece edges cleanly. **The data structure is settled and the conventions are stable.** What's missing is the renderer — `preview.html` still uses cut-line-first parsing (`buildFaceGraph` + `extendFoldsToSilhouette` + cut-trim) which the orientation/awareness model decision (DECISIONS #6) marked as legacy.

This prompt adds the panels-first pathway:

- **Detect** panels-first SVGs (presence of non-empty `<g id="panels">`) and dispatch to the new pathway
- **Parse** panels (closed polygons → 3D extruded slabs, one per panel id)
- **Parse** folds (`fold-<a>-<b>` ids → hinge axes between panel pairs; descriptive forms → single-panel hinges)
- **Build** a hinge tree (panels become nodes; folds become edges; root panel as anchor)
- **Render** the piece in 3D with per-fold rotation sliders, similar to the existing cut-line-first path
- **Fall through** to cut-line-first when no panels layer is present (so legacy pieces keep working)

This unblocks the first piece end-to-end milestone (CHARTER §6 commitment #2): once it ships, any panels-first piece can be rendered, folded, and inspected. Multi-piece assembly (using the cross-piece connection graph from `claude-work/state/connection-graph.json`) is the *next* prompt and lives downstream of this one.

---

## Prerequisites — confirm before starting

- `work/pieces/069/069.svg` exists and has `<g id="panels">` with 11 panels (the canonical clean example)
- `work/pieces/068/068.svg` exists with 19 panels + 17 folds (more complex example)
- `work/pieces/071/071.svg` exists with 4 panels + 3 folds (small + cutouts)
- `work/pieces/099/099.svg` exists with 2 panels + 3 folds incl. two `<circle>` curved folds
- `claude-work/scripts/build_assembly_graph.py` is on disk; running `python3 claude-work/scripts/build_assembly_graph.py` produces `claude-work/state/connection-graph.json` with 10 panels-first pieces processed
- `claude-work/state/connection-graph.json` exists with `pieces` keyed by 3-digit id and `graph.edges` validating 24/24
- `LAYER-CONVENTIONS.md` reflects the panels-first conventions (single doc; LAYERS.md was deleted in the same pass)
- `preview.html` exists at repo root; the existing cut-line-first pathway works against pre-pivot pieces (e.g., 058)
- Three.js + the existing material/lighting setup load successfully when `preview.html` is opened locally

---

## Read These Files First

1. `LAYER-CONVENTIONS.md` (full read; this is the formal spec for what the parser consumes)
2. `claude-work/DECISIONS.md` rows #6 + #7 (the orientation pivot + comprehensive convention lock-in)
3. `claude-work/scripts/build_assembly_graph.py` (the parsing logic; mirror it in JS where reasonable — especially `parse_panel_ids`, `parse_fold_bindings`, `parse_attach_points`, `parse_marks`, and `_find_letter_match`)
4. `claude-work/state/connection-graph.json` (sample output; `pieces['069']` is the cleanest reference for what the JS parser should produce)
5. `preview.html` in full — especially the existing cut-line-first parser, the `currentSlabPivot`/`buildSlab(polygon, thicknessMm)` extrusion path, the `extractSilhouette` Tier-1/2/3 chain, and the `requestRender()` render-on-demand loop. The new panels-aware path runs *parallel* to this; do not modify the cut-line-first code beyond what's needed for dispatch
6. `work/pieces/069/069.svg` (the canonical clean example); compare its layer structure to the JSON output in `connection-graph.json`
7. `claude-work/CHARTER.md` §3 + §5 (the relevant bits about Code-mode work in `claude-work/`)

---

## Target File Structure Changes

```
preview.html                                  ← UPDATE: add panels-aware pathway alongside cut-line-first; dispatch on panels-layer presence
claude-work/CODE_PROMPT_preview-html-panels-aware.md  ← (this file moves here on ship; not at repo root) — actually, keep at repo root per CLAUDE.md convention
```

No new files. No new dependencies. Three.js + the existing CDN imports cover everything needed.

---

## Numbered Tasks

### 1. Add panels-first detection and parser dispatch

In `preview.html`, after the SVG document is loaded but before `extractSilhouette` runs, add:

```js
function hasPanelsFirstAuthoring(svgDoc) {
  const panels = svgDoc.querySelector('g[id="panels"]');
  if (!panels) return false;
  const children = panels.querySelectorAll('path, rect, circle, ellipse, polygon, polyline');
  return children.length > 0;
}
```

Dispatch in the existing pipeline: if `hasPanelsFirstAuthoring(svgDoc)` returns true, call the new `parsePanelsFirst(svgDoc)` and `renderPanelsFirst(parsed)` path. Otherwise fall through to the existing cut-line-first path unchanged.

Display a banner in the UI showing which path is active (e.g., `"panels-first parser"` vs `"cut-line-first parser (legacy)"`) so it's obvious during development.

### 2. Implement `parsePanelsFirst(svgDoc)` — extract panels

Walk the `<g id="panels">` layer. For each id-bearing child element (`path`, `rect`, `ellipse`, `circle`, `polygon`):

1. Skip elements whose id starts with `cutaway` or `cutout-` (parser tolerance per LAYER-CONVENTIONS — these are authoring slips that belong in `silhouette` or `cutouts`)
2. Skip elements whose id is `panels` (the layer's own id)
3. Convert the element's geometry to a closed polygon in viewBox coordinates:
   - `<path>`: parse `d` attribute via the existing path-parsing utility (the same one cut-line-first uses for silhouette)
   - `<rect>`: 4 corners
   - `<ellipse>`/`<circle>`: sample N points around the boundary (e.g., N=64)
   - `<polygon>`/`<polyline>`: read `points` attribute
4. Store as `panels[<id>] = { id: <id>, polygon: [...points], element: <DOM ref> }`

Return the panels map.

### 3. Implement `parseFolds(svgDoc, panels)` — extract fold bindings

Walk both `<g id="folds-valley">` and `<g id="folds-mountain">`. For each id-bearing child:

1. If id starts with `fold-`, parse the rest:
   - **Two-panel form `fold-<a>-<b>` or `fold-<a>-<b>-<deg>`**: try every split point `i` in `rest.split('-')`. The first split where `panels[a]` and `panels[b]` both exist is the binding. If a trailing `-<digits>` follows the second panel name, treat as default angle (degrees).
   - **Descriptive form `fold-<x>` (single token, no panel pair found)**: store as `descriptive` fold with no panel binding
2. Capture geometry:
   - `<path>`: extract start/end points from the path's `d` (first M and last L/M point)
   - `<line>`: x1/y1/x2/y2
   - `<circle>`/`<ellipse>`: cx/cy + r (curved fold; parser stores cx/cy/r and treats the fold as a circular hinge — see Task 7)
3. Tag with `polarity`: `valley` or `mountain` (from layer membership)
4. Tag with `defaultAngle`: parsed integer degrees if `-<digits>` suffix was present

Return a `folds[]` array. Each fold has `{ id, polarity, a, b, descriptive, start, end, defaultAngle, geometry: 'line' | 'circle' }`.

### 4. Implement `parseConnectionGraph(svgDoc, panels)` — extract attach-points + marks

Walk `<g id="attach-points">` and `<g id="marks">`. Mirror the logic in `claude-work/scripts/build_assembly_graph.py` (`parse_attach_points`, `parse_marks`, `parse_connection_id`).

For attach-points, recognize:
- `attach-<letter><piece>`: `kind: 'attach', letter, partner`
- `landing-<tab><piece>`: `kind: 'landing', tab, partner`
- `pivot-<name>`: `kind: 'pivot', name`
- `hole` (bare): `kind: 'hole', letter: null, partner: null`
- `hole-<letter><piece>`: `kind: 'hole', letter, partner`
- `<letter>` (bare letter, ≤ 8 chars): `kind: 'letter-target', letter`
- Bare `<letter><piece>`: shorthand for `attach-<letter><piece>` — same kind/letter/partner extraction
- `back-<form>` prefix: `side: 'back'` and the rest follows the standard form

For marks, recognize:
- `landing-<tab><piece>` (typed cross-piece): same kind as attach-points landing, but tagged `source: 'marks'`
- `landing-<panel-id>` (no piece suffix): same-piece closure landing; tag `kind: 'closure-landing'`
- `align-<letter><piece>`: cross-piece registration
- `cut-<descriptive>`: cuts (passage or accommodation)
- Bare letter (singleton): decorative
- Bare letter (multi-instance, count > 1): multi-instance marker; oriented frame for N≥2

This data is stored on the `parsed` object but **not yet rendered** in this prompt — single-piece scope means we render only this one piece's panels + folds. The connection-graph data lands inert for now; the next prompt's multi-piece pathway consumes it.

### 5. Build the hinge tree

A hinge tree is a directed tree rooted at one panel; every other panel is connected to its parent by exactly one fold. Construct it:

1. Build an undirected adjacency map: `adj[panelId] = [{ neighbor: <panelId>, fold: <foldRef> }, ...]`
2. Pick a root panel — heuristic: the panel with the most adjacency edges (the "main" body panel typically — fits 069's `main`, 068's `pane1`, etc.). If there's a tie, pick alphabetically.
3. BFS from root: for each panel, its parent is the panel reached on first visit; record the fold that connects them.
4. Detect cycles in the adjacency graph — they're authoring errors (a panel can't be reached by two distinct fold paths from root). Banner-warn but continue with the BFS-spanning tree.
5. Surface descriptive folds (`fold-insidetabs` etc. with no two-panel binding) as a separate `descriptiveFolds[]` list — they fold one panel against itself or against an unmodelled cluster; rendering treats them with single-panel rotation around the fold axis.

Return `{ root: <panelId>, tree: { panelId: { parent, fold, children: [...] } }, descriptiveFolds: [...] }`.

### 6. Render panels + apply hinges

For each panel in the tree:

1. Build a 3D `THREE.Group` per panel, parented to its parent panel's group (so child rotations compose with parent's)
2. Inside the group: extrude the panel polygon as a slab using the existing `buildSlab(polygon, thicknessMm)` (the same path the cut-line-first uses, just per-panel instead of per-piece)
3. Apply the panel's local transform: position the group so the fold axis (between this panel and its parent) is at the group's local origin; the slab geometry is offset accordingly
4. The fold axis is the line from `fold.start` to `fold.end` (or the circle's tangent for curved folds — see Task 7); rotate around this axis when the fold's slider changes
5. Wire up a slider per fold: range −180° to +180°, default `fold.defaultAngle ?? 0`; valley folds rotate one direction, mountain folds rotate the opposite (matching the existing cut-line-first polarity convention; reuse the same code if possible)

The root panel sits flat (no parent transform). All other panels rotate relative to their parent through their connecting fold.

For descriptive folds: render the slider but apply the rotation to a sub-region of the parent panel (single-panel fold). Acceptable v0: render the descriptive fold's slider and document that the visual effect is approximate for curved/circular folds (see Task 7) — getting it pixel-perfect is the M6 mechanism animation's problem.

### 7. Curved fold support (light touch)

For `<circle>`/`<ellipse>` fold elements (descriptive folds):

- Store `geometry: 'circle'` with `cx, cy, r` (or ellipse rx/ry)
- For rendering, treat as the simplest possible: a circular hinge at the slider angle bends the *region inside the circle* relative to the *region outside* (or vice versa) by the slider's angle. The actual 3D shape would be a conical surface; v0 can approximate by rotating the inner region around the circle's tangent at a single point (pick the point closest to the panel's centroid).
- This is intentionally a sketch — the saw-tooth crescent (099) is the only piece in the current batch with curved folds, and a partial render is fine. Document the approximation in code comments.

### 8. UI: piece-id loader, render-on-demand, banner

The existing piece-id loader (the `?piece=NNN` URL param + `R` keybind from M0.6.14) keeps working. Add:

- A label showing `"panels-first ✓"` or `"cut-line-first (legacy)"` so the active path is obvious
- A panel/fold count summary (e.g., `"11 panels, 10 folds, root: main"`)
- A console log on each parse showing what the parser saw (panels, folds, hinge tree, descriptive folds)
- The render-on-demand pattern — only re-render when sliders change or piece reloads

Sliders already exist for cut-line-first folds. For panels-first, generate one slider per fold from the hinge tree's edges (excluding root-touching folds get the same treatment). Label each slider with the fold id (e.g., `fold-main-tabb`).

---

## Verification Checklist

Run these after implementation:

1. **Loads cleanly:** Open `preview.html` locally; no console errors. Loading no piece (default state) is unchanged from cut-line-first.
2. **Dispatch banner:** Loading 058 (a pre-pivot piece without panels) shows `"cut-line-first (legacy)"`. Loading 069 shows `"panels-first ✓"` with `"11 panels, 10 folds"` summary.
3. **069 renders:** All 11 panels visible. Sliders for the 10 folds produce visible rotations. Setting all valley folds to 90° folds the box closed.
4. **068 renders:** All 19 panels visible. Sliders for the 17 folds (16 valley + 1 mountain) produce visible rotations. Hinge tree picks a sensible root (likely `pane1`).
5. **071 renders:** 4 panels visible. Sliders for the 3 folds. Closing all 3 folds at 90° forms the square ring shape.
6. **099 renders:** 2 panels visible. The straight `fold-main-tabb` slider produces a tab fold. The two curved `fold-insidetabs` / `fold-outsidetabs` sliders produce *some* visible movement (approximate is fine).
7. **No regression:** Loading a pre-pivot piece (058 or 113) still works via the cut-line-first path. The dispatch banner confirms the path.
8. **Lint:** No new ESLint errors; existing build pipeline still runs (if any).

---

## What NOT to Change

- The existing cut-line-first parser (`buildFaceGraph`, `extendFoldsToSilhouette`, cut-trim, the diagnostic harness from PR #13). It stays alive for legacy pieces.
- The render-on-demand `requestRender()` loop, three.js material setup, lighting, camera controls — all reused.
- `extractSilhouette` Tier-1/2/3 — used by cut-line-first; unchanged.
- The piece-id loader (M0.6.14's URL param + `R` keybind) — reused.
- Any per-piece SVG content in `work/pieces/` — read-only.
- `preview.html`'s file location at repo root — keep there per established convention.
- `claude-work/scripts/build_assembly_graph.py` — read-only; the JS parser mirrors its logic but doesn't depend on it at runtime.

---

## Manual tests (post-merge)

| Test | Pre-condition | Action | Expected |
|---|---|---|---|
| Panels-first dispatch | 069 has panels layer | Open `preview.html?piece=069` | Banner says "panels-first ✓"; 11 panels render; 10 fold sliders shown |
| Cut-line-first fallback | 058 has no panels layer | Open `preview.html?piece=058` | Banner says "cut-line-first (legacy)"; existing cut-line-first render unchanged |
| Box closes on 069 | 069 panels-first loaded | Set all valley sliders to 90° | Anchor-bearing box folds into 3D box shape |
| Reload via R | 069 loaded | Press R | Re-fetches and re-parses 069; banner + counts unchanged |
| 068 renders | 068 has panels-first authoring | Open `preview.html?piece=068` | 19 panels; 17 fold sliders; no console errors |
| Curved fold sketch | 099 has two `<circle>` folds | Open `preview.html?piece=099` | Two curved-fold sliders produce approximate movement; not pixel-perfect, just non-broken |

---

*Drafted 2026-05-05 in cowork session `sessions/2026-05-05-2330_cowork_panels-first-batch-and-graph.md`. Single-piece scope; multi-piece scene assembly follows in a sibling prompt once this lands.*
