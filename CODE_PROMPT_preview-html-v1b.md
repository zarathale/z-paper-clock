---
status: draft
started: 2026-05-02
owner: Zarathale (Alan)
target: preview-html-v1b
parent: preview-html-v1
depends_on: preview-html-v1a
---

_Draft. This prompt presumes v1a's structure but doesn't yet know v1a's actual function signatures, variable names, or the precise shape of the `parsed` object. Re-tighten this prompt against v1a's session note (specifically the "function/variable names that v1b should reuse" section) before flipping `status` to `ready-for-code`. Edit targets in Tasks 1, 4, 6, 7 are the most likely to need adjustment._

## What You Are Doing and Why

Layer the fold-rendering half onto `preview.html` — extending the v1a foundation with polygon cutting (silhouette + N fold lines → N+1 panels), adjacency BFS (panels → fold tree rooted at the root-marker panel), per-fold UI controls, hinge hierarchy in three.js, and live fold animation. After v1b, dropping `inbox/069.svg` produces 13 panels that fold up into a box; dropping `inbox/066.svg` produces 22 panels with valleys + mountains bending in opposite directions.

This is v1b — the second half of the split of `CODE_PROMPT_preview-html-v1.md`. v1a shipped the parsing + flat slab rendering path (`preview.html` reads SVGs and renders the silhouette as a single flat slab). v1b cuts the silhouette and animates folds.

---

## Prerequisites — confirm before starting

- v1a has been merged to `main`. Confirm: `preview.html` exists at repo root and renders a single flat slab when 069 or 066 is dropped.
- Read v1a's session note (`sessions/2026-05-02-XXXX_code_preview-html-v1a.md`) for ship-time function names and structure. The names below (`buildSlab`, `parsed.folds`) are placeholders — adjust to match v1a's actual API.
- Modern browser via `file://`, no dev server.
- No existing `claude/preview-html-v1b` branch or worktree from prior attempts.

---

## Read These Files First

1. `CLAUDE.md`.
2. `CODE_PROMPT_preview-html-v1.md` — the unified prompt. Architectural rationale for the polygon-cut algorithm (Option 3), edge-tag propagation, sliver filter, and BFS over adjacency lives here.
3. `CODE_PROMPT_preview-html-v1a.md` — what shipped first. Don't re-derive the silhouette extraction or scene setup; reuse v1a's functions and `parsed` object.
4. `work/SPEC-3D-VIEWER.md`.
5. `sessions/2026-05-01-2300_cowork_069-3d-viewer-build.md` — full architectural context, Empty-Layer Behavior table, fold-tree algorithm specification.
6. `sessions/2026-05-02-XXXX_code_preview-html-v1a.md` — v1a ship note for current state of `preview.html`. Critical reading for function signatures and structure.
7. `outputs/069-test/cut.py` — reference cutter implementation in Python; the JS port uses `polygon-clipping` for the half-plane intersections.
8. `outputs/066-test/run.py` — 066 cut diagnostic.

---

## Target File Structure Changes

```
z-paper-clock/
├── preview.html                                  ← UPDATED: extend with cut + adjacency + hinges
├── sessions/
│   └── 2026-05-02-XXXX_code_preview-html-v1b.md  ← NEW: end-of-session note
└── CODE_PROMPT_preview-html-v1b.md               ← flip status to "shipped" at end
```

---

## Numbered Tasks

### Task 1 — Extend UI shell with fold sliders

Populate the v1a placeholder `<div id="fold-controls">` with:

1. **Global fold slider.** Range 0–100%. Drives every hinge from 0 to its target angle proportionally.
2. **Per-fold sliders.** Auto-generated from parsed fold lines, one slider per unique SVG path id. Label = path id (or `valley-N` / `mountain-N` if no id assigned). Range −180° to +180°. Default value = the path-id-encoded angle, or the layer default (−90 valley, +90 mountain) if no id encoding. Read-only metadata badge: how many hinges this path drives (most are "1 hinge"; on 069, paths 2 and 3 each drive "2 hinges").

Update v1a's Reset button to reset all fold sliders to their defaults (in addition to the thickness slider).

### Task 2 — Polygon cut

Given the silhouette polygon and N fold lines:

1. Compute the silhouette bbox + 100-unit margin. Call this `bigBox`.
2. For each fold line, extend it to an infinite-line cutter: parameterize the line (point + unit direction), then construct a half-plane polygon from `bigBox` clipped on each side of the line. Two half-plane polygons per fold line.
3. Maintain `regions` = array of `{polygon, edgeTags}`. Initialize with `[{polygon: silhouette, edgeTags: ['silhouette' for each edge]}]`.
4. For each fold line F (in input order):
   - For each region R in `regions`: intersect `R.polygon` with each of F's two half-planes via `polygonClipping.intersection`. This produces 0, 1, or more sub-polygons per half.
   - For each new sub-polygon, propagate edge tags: edges of R that survive get their original tag; new edges (introduced by the cut) get tagged with `F` (the fold line's id, or a synthetic id like `valley-3` if no id).
   - Replace R in `regions` with all sub-polygons.

Edge-tag propagation in detail: after a cut by F, every edge of the result polygon either (a) lies along F (within ε ≈ 0.5 viewBox units of F's infinite line) → tag = F, or (b) lies on an edge of the input R → inherit R's tag for that edge. Match output edges to input edges by midpoint distance.

Sliver filter — drop any region whose **every** vertex lies within Δ of a single fold line (signature: thin strips along a cut). Δ = 0.5% of the silhouette-bbox diagonal. Geometric, scale-invariant. (This replaces the size-based "drop regions < 1% of largest" filter, which was confirmed fragile in the 066 validation pass — smallest-real-panel:largest-sliver gap was only 2× on 066.)

Expected outputs: 069 → 13 polygons. 066 → 22 polygons. Bail with banner if the result is wildly different (e.g., < 3 panels — likely the cut algorithm broke).

If `polygon-clipping` proves unsuitable mid-implementation (e.g., a robustness issue with collinear vertices), `martinez-polygon-clipping@0.7.3` is an acceptable swap; document the swap reason in the session note.

### Task 3 — Adjacency graph and BFS

Build a graph where nodes are polygons and edges are fold-line segments shared between polygon pairs:

1. For each fold line F, collect the polygons that have at least one edge tagged F. Each pair of such polygons is potentially adjacent via F.
2. For each candidate pair (P_i, P_j) sharing tag F: check that they share an edge of nonzero length on F's line. Specifically: collect P_i's F-tagged edges and P_j's F-tagged edges; check whether any pair of edges (one from each) overlap on F's line by more than ε ≈ 1 viewBox unit. If yes: P_i and P_j are adjacent via F. Corner-touches (zero-length overlap) don't count.

Identify root:

- If `<g id="root">` had a marker (parsed in v1a, stored as `parsed.rootCentroid`): find the polygon containing the marker centroid (point-in-polygon test). Root = that polygon. If no polygon contains the marker, fall back to the largest-by-area heuristic and emit a banner warning.
- Otherwise: root = polygon with largest area.

BFS from root over the adjacency graph. Each non-root polygon V records `parent(V) = U` and `hinge(V) = F` from the BFS edge that first reached it. Iterate over fold lines in deterministic order (by parsed input index) so the tree is reproducible across reloads.

If BFS doesn't reach some polygon: it's an orphan. Render it flat at its silhouette position with a banner warning. Do not crash.

### Task 4 — Replace single-slab build with N-panel build

For each polygon (with edge tags from Task 2): call v1a's slab-builder function (`buildSlab(polygon)` or whatever it's named in v1a) to produce a slab mesh. Same three-material setup (front/back/edge), same UV mapping (each polygon's viewBox coords → texture UV — the texture is shared across all panels).

The v1a slab-builder should already accept an arbitrary polygon argument. If v1a hardcoded the silhouette inside the function, refactor it first (separate the polygon-input part from the silhouette-extraction part).

### Task 5 — Hinge hierarchy

Each non-root slab is a child of its parent's slab via an intermediate `Object3D` (the hinge):

1. Root slab: positioned at world origin, no parent.
2. For each non-root slab V with `parent(V) = U` and `hinge(V) = F`:
   - Create an `Object3D` (the hinge). Position it at the midpoint of F (the shared edge between U and V), expressed in V's local-coordinate frame. Orient it so its rotation axis is along F's direction.
   - Parent the hinge to U's slab. Parent V's slab to the hinge.
   - The hinge's rotation around its axis is the animation parameter.

The cleanest way to handle "hinge axis along F's direction" without trig: position the hinge at F's midpoint, then translate V's slab so that F's midpoint sits at the hinge's local origin. Then rotate the hinge around the axis from F's start to F's end. Quaternion approach: `hinge.quaternion.setFromAxisAngle(axis, currentAngle)`.

Per-fold sliders update the angles of all hinges driven by the same path id simultaneously (the "same fold path → same angle" rule from the session note). Maintain a map `pathId → [hinge, hinge, ...]` so a slider change iterates and updates all of them.

Global fold slider drives `t ∈ [0, 1]`; each hinge's angle = `t * targetAngle` for that hinge.

### Task 6 — Re-route axle markers to correct panels

In v1a, all axle markers attached to the single slab. Now: for each axle ellipse, find which polygon contains its centroid (point-in-polygon). Add the marker sphere as a child of that polygon's slab — it rides along when the panel folds.

Replace v1a's axle-attachment code; don't leave both implementations.

### Task 7 — Update live rebuild + reset for fold sliders

- **Per-fold slider**: cheap. Update the relevant hinges' rotation only. No geometry rebuild.
- **Global fold slider**: cheap. Update every hinge's rotation. No geometry rebuild.
- **Thickness slider**: expensive. Rebuild slab geometries — now N geometries instead of 1. Keep v1a's debounced handler.
- **Reset button**: reset thickness AND all fold sliders to defaults; trigger global update.

### Task 8 — Extend console diagnostics

Update v1a's diagnostic block to add lines after the existing ones:

```
Polygons after cut: <K>
Slivers filtered: <S>
Root: polygon at centroid (<x>, <y>), area <units²>, source: <root-marker | largest-by-area>
Tree depth: <D>
Orphans: <count>
Per-fold paths: [<id>: <hinge_count> hinges, default <angle>°, ...]
```

Total diagnostic block now matches the unified prompt's §Task 12.

---

## Verification Checklist

1. `preview.html` updated; still single self-contained file at repo root. v1a's behavior preserved for SVGs without fold layers (test by dropping a synthetic SVG with no `folds-valley` / `folds-mountain` layers — should fall back to single-slab render with a banner).
2. Drag-drop `inbox/069.svg`. Console reports: 13 polygons, 8 valley folds, 0 mountain, 0 orphans.
3. 3D view shows the unfolded box net flat (BASE in center, walls + corners + ext tabs around it). Scan texture mapped correctly across all 13 panels.
4. Move global fold slider 0 → 100%. Box folds up correctly: walls rotate up, then corners + ext tabs fold to vertical. Some panel interpenetration at intermediate angles is acceptable (no phase sequencing in v1).
5. Move thickness slider 1.0 → 4.0 mm. All 13 slabs grow.
6. Find the per-fold slider for path id `fold-90` (or similar) corresponding to a BASE↔WALL hinge. Move from −90° to 0°: that one wall returns to flat while others stay folded.
7. Drop `inbox/066.svg`. Console reports: 22 polygons, 20 valley + 2 mountain, 0 orphans.
8. 3D view: long narrow tube net flat. Global fold slider folds it into the tube shape with the two mountain folds bending opposite to the valleys.
9. Axle marker on 069 (and any axles on 066 if present) ride correctly with the panel that contains them.
10. No console errors during any interaction. No NaN positions.

---

## What NOT to Change

- Do not modify `work/pieces/069/piece-069-viewer.html`.
- Do not author or modify any SVG files in `inbox/` or `source/pieces/`.
- Do not create `work/viewer/`, `work/manifest.json`, or any per-piece JSON sidecars.
- Do not implement SVG writeback ("Export updated SVG" button). That's v2, scoped to a separate prompt after v1 ships.
- Do not implement marks-layer rendering, glue-zones, labels, or cutouts-layer parsing. v1 is silhouette + folds + axles + root + thickness, nothing else.
- Do not implement phase sequencing on the global fold slider. Single 0–100% drives all hinges proportionally.
- Do not regress v1a behavior. The single-slab fallback should still kick in for SVGs with no fold layers.
- Do not bump `work/viewer/package.json`.

---

## Manual tests (post-merge, on Alan's mac)

1. Pull `main` after merge. Verify `preview.html` is updated.
2. Drag-drop `inbox/069.svg`. Confirm 13-panel render. Move global fold slider through full range; confirm hinges work.
3. Drag-drop `inbox/066.svg`. Confirm 22-panel render with mountain folds bending opposite to valleys.
4. Pick any per-fold slider; sweep through −180° to +180°. Confirm only that hinge's panel(s) move (and that paths driving multiple hinges, like 069's path 2, move both hinges in sync).
5. Adjust thickness slider. Confirm rebuild is smooth (no stutters > ~150 ms) across N slabs.
6. Drop a synthetic SVG with no fold layers (e.g., a copy of 069 with `<g id="folds-valley">` deleted). Confirm v1a single-slab fallback still works with a banner.
7. Test "Reload" after editing the dropped file (e.g., rename a path id from `fold-90` to `fold-60` in a copy, drop the modified copy, confirm the angle changes in the per-fold slider default).

If any test surfaces an unexpected behavior, capture it in the session note's "Known issues at ship" section.

---

## Branch / commit / PR

- **Branch:** `claude/preview-html-v1b`
- **Commit subject** (imperative, lowercase, ≤70 chars): `extend preview.html: polygon cut + folds + hinge animation (v1b)`
- **PR title:** same as commit subject
- **PR description:**
  - One-line summary
  - "What changed" — `preview.html` → UPDATED; `sessions/...` → NEW session note
  - Manual test steps (link to "Manual tests" section above)
  - Branch name + commit SHA
  - Link to this prompt file

---

## End-of-session

1. Write the session note at `sessions/2026-05-02-XXXX_code_preview-html-v1b.md`. Include: branch name, commit SHA, what was done, what's in the PR, any known issues at ship.
2. Flip this prompt's `status` from `ready-for-code` to `shipped`. Add `shipped: 2026-05-02` (or the actual ship date) in the front matter. Add the italic header below the front matter:
   `_Shipped YYYY-MM-DD; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._`
3. Push branch, open PR via `gh pr create` directly. Return PR URL in the final chat message.
