---
status: ready-for-code
started: 2026-05-03
owner: Zarathale (Alan)
target: preview-html-v1b
parent: preview-html-v1
depends_on: preview-html-v1a + cut-layer + texture-flip + back-face-mirror + perf + thickness-fix + axle-rotation
supersedes: _archive/code-prompts/CODE_PROMPT_preview-html-v1b.md (archived 2026-05-03)
---

## What You Are Doing and Why

Layer the fold-rendering half onto `preview.html`. v1a + the six follow-up passes shipped through 2026-05-03 give the foundation: SVG parse, three-tier silhouette extraction, single-slab `buildSlab(polygon, thicknessMm)`, world-anchored silver axle wires, optional brass-gold `north` orientation sphere, and a per-piece axle rotation slider that pivots the whole slab around `axles[0]`. v1b adds the **face graph**: cut the silhouette along its fold lines into a set of regions (one per face of the planar subdivision), root the graph at the region containing the `id="root"` marker (or fall back to the largest region with a banner), BFS to a fold tree, and parent each non-root region's slab to its parent's slab through a hinge `THREE.Object3D` whose Z rotation is driven by sliders.

After v1b, dropping `inbox/069.svg` produces 13 panels that fold up into a box net; dropping `inbox/066.svg` produces 22 panels with valleys + mountains bending in opposite directions. The rotation pivot continues to wrap the **whole fold tree**, so rotating the piece in space and folding the piece are independent compositions. The data model and step-1 algorithm follow `work/SPEC-REGIONS.md`; the implementation uses `polygon-clipping@0.15.7` (already loaded by `preview.html`).

---

## Prerequisites — confirm before starting

- `preview.html` is the current shipped state at repo root (~1362 lines as of 2026-05-03). v1a's foundation plus six follow-up passes (cut-layer convention, texture flip, back-face mirror, render-on-demand performance, thickness-extrusion fix, axle rotation slider) all merged.
- `polygon-clipping@0.15.7` is loaded via the third `<script>` tag in `<head>`. If the script tag was removed, restore it before starting Task 3.
- `inbox/069.svg` exists, has `<g id="silhouette">`, `<g id="folds-valley">` (8 paths), `<g id="axles">` (1 ellipse), no `<g id="folds-mountain">`, no `<g id="root">`.
- `inbox/066.svg` exists, has `<g id="folds-valley">` (20 paths), `<g id="folds-mountain">` (2 paths), `<g id="axles">` (no ellipses; banner at load), no silhouette layer (Tier 2 / Tier 3 fallback runs), no `<g id="root">`.
- Modern browser via `file://`. No dev server.
- No existing `claude/preview-html-v1b` branch or worktree from prior attempts.

---

## Read These Files First

1. `CLAUDE.md` — working conventions (the prompt-format and session-note requirements at the bottom matter for end-of-session).
2. `work/SPEC-REGIONS.md` — the upstream concept doc. Definitions of *region*, *face graph*, *FoldEdge*, *fold tree*; the two-step algorithm (extend fold lines to silhouette boundary, then iteratively split); root-marker BFS; the runtime data shape; what's out of scope in v1.
3. `preview.html` — the current shipped file. Especially:
   - Globals block (lines ~108–133): `currentSlabPivot`, `currentAxleWires`, `parsed`, `MM_PER_UNIT`, `VB`, `needsRender`, `requestRender()`.
   - `parseSVG` (line 278) and the comment-block `parsed = { … }` shape (lines ~120–130). Note `folds[].layer` is `'folds-valley'` | `'folds-mountain'`; `defaultAngle` is the path-id-encoded value (`fold-90` → −90, `fold+45` → +45) or the layer default (`-90` / `+90`).
   - `extractSilhouette` (line 754, async dispatcher Tier 1 → Tier 2 → Tier 3). v1b consumes its return polygon — do not modify.
   - `renderScene(p)` (line 1049): teardown → silhouette extract → `buildSlab` → wrap in `currentSlabPivot` at active-axle position → axle wires (world-anchored, outside pivot) → optional north sphere (inside pivot) → frame camera → diagnostics. v1b restructures the slab/wrap/north section but preserves the teardown, axle-wires loop, camera framing, and diagnostics scaffold.
   - `buildSlab(polygon, thicknessMm)` (line 1193): polygon → THREE.Group of front + back + side meshes. **Do not modify**; v1b calls it once per region.
   - Thickness rebuild (`debouncedRebuild`, line 1303): the cached-polygon optimization from v1a is invalidated by v1b — see Task 7.
   - Rotation slider handler (line 1333): writes `currentSlabPivot.rotation.z`. v1b leaves this **unchanged** — the pivot continues to wrap the entire fold tree.
4. `_archive/code-prompts/CODE_PROMPT_preview-html-v1b.md` — the archived earlier draft. Useful for the polygon-cut algorithm sketch, edge-tag matching by midpoint distance, the sliver-filter calibration (Δ = 0.5% of silhouette-bbox diagonal), and the `069 → 13` / `066 → 22` expected counts. **Do not** reuse the variable names or task numbering — those targeted v1a-only state.
5. `sessions/2026-05-01-2300_cowork_069-3d-viewer-build.md` — the original architectural conversation that produced the polygon-cut + adjacency-BFS approach. Especially the Empty-Layer Behavior table and the "same fold path id → same hinge angle" rule (multiple fold-line segments sharing one path id all read the same per-fold slider).
6. `sessions/2026-05-02-1400_code_preview-html-v1a.md` — for the parsed-object shape and `buildSlab`'s contract.
7. `sessions/2026-05-03-0200_cowork_v1b-archive.md` — captures the eight since-v1a constraints v1b must thread (axle pivot composition, silhouette priority chain, silver-cylinder/north-sphere markers, texture flip, back-face mirror, render-on-demand, thickness via `MM_PER_UNIT`, default 0.4 mm).

---

## Target File Structure Changes

```
z-paper-clock/
├── preview.html                                  ← UPDATED: extend with face graph + hinges + fold sliders
├── sessions/
│   └── 2026-05-03-XXXX_code_preview-html-v1b.md  ← NEW: end-of-session note
└── CODE_PROMPT_preview-html-v1b.md               ← flip status to "shipped" at end
```

No new files, no folder moves, no deletions.

---

## Numbered Tasks

### Task 1 — Populate the `<div id="fold-controls">` shell

Replace the placeholder content (currently the italic "Fold controls — added in v1b" string) with two slider clusters, both initially empty and populated by `renderScene` after the face graph is built:

1. **Global fold slider.** Range 0–100%, step 1, default 0. Drives every hinge from 0° to its `targetAngle` proportionally. Label "Fold all"; live value in a `.val` span (e.g. "0%").
2. **Per-fold slider container.** A child `<div id="per-fold-sliders">` that `renderScene` clears and re-fills with one row per **unique fold path id** (folds without an `id` attribute get a synthetic id `valley-N` / `mountain-N` based on their parsed-input index inside their layer). Each row: label = path id; range −180° to +180°, step 1; default = `defaultAngle` carried through from `parsed.folds`; metadata badge showing the hinge-count this id drives (`×1` typical; on 069's path 2 / path 3, `×2` because each path is shared between adjacent regions). Same `.slider-row` styling as the thickness and rotation rows.

Match the existing CSS hooks (`.slider-row`, `.val`, `accent-color: #c9a96e`). Keep the global + per-fold cluster inside `<div id="fold-controls">` so the existing italic-empty-state CSS rule still applies when the cluster is empty.

Update the existing **Reset thickness** button to also reset every per-fold slider to its default and the global slider to 0; rename the visible label to **"Reset"** and bind it to a single handler that touches thickness, global fold, and all per-fold sliders. The rotation-section's reset stays separate — rotation is still its own concern.

### Task 2 — Extend each fold line to the silhouette boundary

Per `SPEC-REGIONS.md` step 1: every fold line that doesn't already terminate at the silhouette boundary must be extended in both directions until it intersects the silhouette polygon's edge. This prevents T-junctions where a fold line ends inside the piece and fails to divide it into two closed faces.

Add `extendFoldsToSilhouette(silhouette, folds)` returning an array `extendedFolds` of `{layer, id, defaultAngle, start, end, sourceIndex}` where `start` and `end` lie on the silhouette boundary (or strictly outside, with the segment passing through the boundary). Algorithm per fold:

1. Parameterize the fold as `P(t) = origin + t · direction`, where `origin = startSVG`, `direction = (endSVG − startSVG) / |endSVG − startSVG|`.
2. For each edge of the silhouette polygon, compute the line–line intersection's `t` value. Keep all `t` values from intersections that lie within the silhouette edge's segment range.
3. Pick `tMin = min(t < tStartFold, intersections)` and `tMax = max(t > tEndFold, intersections)` where `tStartFold = 0` and `tEndFold = |endSVG − startSVG|`. If a side has no boundary intersection (numerically degenerate; should not happen on valid input), nudge by 1e-6 inward and try again, then bail with a banner.
4. Return `{ start: P(tMin − ε), end: P(tMax + ε), … }` where `ε = 0.5` viewBox units (matches the cut-tag tolerance below). The `−ε` / `+ε` ensures the extended line strictly crosses the silhouette boundary so the half-plane intersection in Task 3 cuts cleanly.

If an authored fold is already strictly boundary-to-boundary (rare on real pieces — most fold lines authored in Affinity terminate at decorative endpoints inside the silhouette), the algorithm leaves it essentially unchanged (just extends by `ε` on each end).

`sourceIndex` is the fold's index inside `parsed.folds` after parse, kept so the BFS in Task 3 can iterate folds in deterministic order across reloads.

### Task 3 — Build the face graph

Add `buildFaceGraph(silhouette, extendedFolds)` returning a `FaceGraph` shaped after `SPEC-REGIONS.md`:

```js
// FaceGraph
{
  rootId: 'region-N',
  regions: Map<string, Region>,    // keyed by region id
  foldEdges: FoldEdge[]             // every shared edge, deduped, in BFS-discovery order
}

// Region
{
  id: 'region-K',                   // assigned in clip order; BFS does not renumber
  polygon: [[vx, vy], ...],          // closed, no duplicate first-vertex-at-end (polygon-clipping convention)
  isRoot: false,
  parentId: 'region-J' | null,       // null on root
  parentEdge: FoldEdge | null,       // null on root; the FoldEdge whose hinge swings this region
  childEdges: [{ childId, edge }, ...]
}

// FoldEdge
{
  pathId: 'fold-90' | 'valley-3' | 'mountain-1' | …,
  layer: 'folds-valley' | 'folds-mountain',
  polarity: 'valley' | 'mountain',
  defaultAngle: number,               // degrees; carried from parsed.folds[i].defaultAngle
  segment: [[ax, ay], [bx, by]],      // SVG-space; the shared edge between parent and child regions
  sourceFold: { id, layer, sourceIndex } // back-pointer for BFS deterministic ordering
}
```

Steps:

1. **Build cutter polygons.** For each extended fold, build two half-plane polygons by clipping a `bigBox` (the silhouette's bounding box expanded by 100 viewBox units) against the line `(start, end)`. Use `polygon-clipping`'s `intersection()` of the bigBox with the half-plane polygon; the half-plane polygon is constructed by taking the bigBox corners on one side of the line plus the two intersections of the line with the bigBox edges, ordered correctly. Standard half-plane construction; an explicit helper `halfPlanePoly(bigBox, line, sign)` keeps it readable.
2. **Iteratively split.** Initialize `regions = [{ polygon: silhouette, edgeTags: ['silhouette' for each edge] }]`. For each extended fold `F` (in `sourceIndex` order): for each region `R` in `regions`, intersect `R.polygon` with each of `F`'s two half-plane polygons via `polygonClipping.intersection`. Each intersection is a list of polygons (typically one per side; possibly more if `R` was already non-convex from prior cuts). For every output sub-polygon, propagate edge tags (next step). Replace `R` in `regions` with all sub-polygons across both halves.
3. **Edge-tag propagation.** After cutting `R` by `F`, each edge of an output polygon is either (a) within `ε = 0.5` viewBox units of `F`'s infinite line — tag it `F.id` — or (b) close to one of `R`'s original edges — inherit that edge's tag. Match by midpoint distance: for each output edge, compute its midpoint; for every input edge of `R`, compute the input edge midpoint; pick the smallest-distance match within `ε`. If no match within `ε` and the edge is also not on `F`'s line, tag it `'unknown'` and bump a counter for the diagnostic block (do not bail).
4. **Sliver filter.** Drop any region whose every vertex lies within `Δ` of a single fold line. `Δ = 0.005 × diag(silhouette bbox)` (geometric, scale-invariant). Increment a sliver-count for diagnostics. Authored fold lines that *exactly* coincide with a silhouette edge can produce zero-area or near-zero-area slivers; this filter catches them without dropping legitimate small panels.
5. **Adjacency.** Two regions are adjacent via fold path `pid` if they each have at least one edge tagged with that fold's id, and those edges overlap on the fold's infinite line by more than `1.0` viewBox units (corner-touches with zero-length overlap don't count). Record the overlap segment as the `FoldEdge.segment`.
6. **Root.** If `parsed.rootCentroid` exists, find the region whose polygon contains it via point-in-polygon (a small ray-casting helper is fine — no library needed). If no region contains the marker, fall back to the largest-area region and emit a banner. If `rootCentroid` is null (069 + 066 today), use largest-area silently — that's the SPEC-REGIONS fallback rule.
7. **BFS.** Visit regions starting from root. For each newly-reached region V, set `V.parentId = U` and `V.parentEdge = the FoldEdge connecting U and V` (with `polarity`, `defaultAngle`, `segment` populated from the fold whose id matched in step 5). Iterate fold-edges out of each region in `sourceIndex` order so the tree is reproducible across reloads. If a region is unreachable from root (orphan), render it flat at its silhouette-coords position with a banner; do not crash.

If `polygon-clipping` proves brittle on a specific authored input (collinear vertices, zero-area output, etc.), `martinez-polygon-clipping@0.7.3` is an acceptable swap. Document the swap reason in the session note.

### Task 4 — Build the fold tree (slabs + hinges) and wire it into `currentSlabPivot`

Replace the single-`buildSlab(silhouette)` call inside `renderScene` (currently lines ~1077–1104, the block that creates `slab` and assembles `pivot`). The new flow:

1. If `parsed.folds.length === 0`, take the **single-slab fallback path** (current v1a behavior preserved): `buildSlab(silhouette, T)` → wrap in pivot → done. No fold-controls populated. Banner-OK: "No folds parsed; rendering single slab."
2. Otherwise, call `extendFoldsToSilhouette(silhouette, parsed.folds)` then `buildFaceGraph(silhouette, extendedFolds)`.
3. Build a `Map<regionId, THREE.Group>` slab cache: for each region, call `buildSlab(region.polygon, T)`. This returns a slab whose internal coordinate frame is centered at *its own* polygon's bbox center (because `buildSlab` uses `polyBbox(polygon)` for the local origin). Track each region's slab-frame offset relative to the silhouette's bbox center; we need this to align child slabs to parent slabs at flat (rotation = 0) state.
4. Build the hinge tree:
   - **Root region's slab** is positioned at the silhouette's bbox-relative coords: `slab.position.set((rootBbox.cx − silhouetteBbox.cx) · MM_PER_UNIT, −(rootBbox.cy − silhouetteBbox.cy) · MM_PER_UNIT, 0)`. (The Y sign flip matches the convention in `renderScene` lines ~1096–1098 and `buildSlab`.) This places the root slab so its visible geometry sits where it would in the unfolded silhouette.
   - **For each non-root region V** with `parentId = U`, `parentEdge.segment = [[ax,ay],[bx,by]]`:
     - Create `hinge = new THREE.Object3D()`. Position it at the segment midpoint, expressed in **U's local frame** (so subtract U's slab-position from the midpoint world coords): `hingeLocalX = (midX − Uslab.position.x)`, similarly Y.
     - Compute the rotation axis from the segment in 3js coords: `axis = ((bx − ax)·MM_PER_UNIT, −(by − ay)·MM_PER_UNIT, 0)`, normalized. Store `hinge.userData.axis = axis` and `hinge.userData.targetAngle = parentEdge.defaultAngle * Math.PI / 180`. Initial rotation: `hinge.quaternion.setFromAxisAngle(axis, 0)` (flat at load).
     - Translate V's slab so that the hinge's local origin matches V's polygon's bbox-relative coord at the segment midpoint: `Vslab.position.set(hingeLocalX − (Vbbox.cx − silhouetteBbox.cx) · MM_PER_UNIT, …, 0)` so V appears coplanar with U at angle = 0.
     - `hinge.add(Vslab)`; `Uslab.add(hinge)`.
     - Track `(pathId → hinge[])` so the per-fold slider in Task 6 can iterate. Multiple fold segments sharing a path id (e.g., 069's paths 2 + 3) each create their own hinge but all share one slider value.
5. Wrap the **root slab** in `currentSlabPivot` (a fresh `THREE.Group`). Position the pivot at the active axle's world coords as before — `pivot.position.set(activeAxle3js.x, activeAxle3js.y, 0)` — and offset the root slab inside the pivot by `−activeAxle3js` so it sits at its world-correct location at rotation = 0. The pivot now wraps the entire fold tree because non-root slabs are descendants of the root slab.
6. Axle wires (the per-axle `buildAxleWire` loop at renderScene lines ~1110–1118) **stay unchanged**: world-anchored, OUTSIDE the pivot, at each axle's silhouette-coords position. They do not fold with their containing panel — they represent the framework wire.
7. Camera-frame logic, diagnostic block, the `rotationSection.hidden` guard, and the rotation slider current-value application all stay where they are.

The `currentSlabPivot.traverse(…)` teardown loop at the top of `renderScene` already disposes geometries and materials recursively, so the new tree teardown requires no extra code.

### Task 5 — Re-route the optional `north` orientation marker into its containing region

Currently (renderScene lines ~1124–1141) the north sphere is added to `pivot` as a direct child, positioned at `(p.north − activeAxle3js)` in the pivot's local frame. With folds present, `p.north`'s SVG coords might land inside a non-root region — its visual position should ride with that region during folding.

In the fold-tree path, after Task 4 builds the slab map: if `parsed.north` is non-null and `parsed.axles.length > 0`, find the region whose polygon contains `parsed.north` (point-in-polygon, same helper as Task 3.6). Position the sphere relative to that region's slab's local frame; add it as a child of that slab. It now folds with its panel and rotates with the pivot, both correctly.

If point-in-polygon returns no match (north lies inside an orphan region or the region with the bug from Task 3 step 4), fall back to attaching to the root slab and banner-warn.

### Task 6 — Wire fold sliders into hinge rotations

Two cheap in-place updates, both call `requestRender()` and skip geometry rebuild:

- **Per-fold slider input handler.** On `input`, read the slider value `deg`, look up `pathId → hinge[]`, and for each hinge: `hinge.quaternion.setFromAxisAngle(hinge.userData.axis, deg * π / 180)`. Update the row's `.val` span. Sign: positive deg = positive rotation around the stored axis. The axis direction (segment start → end in 3js coords) determines whether positive deg appears as valley-style or mountain-style folding; this is fine because the path-id encoding (`fold-90` / `fold+90`) carries the polarity into `defaultAngle`, and the slider's default value reflects that.
- **Global fold slider input handler.** On `input`, read `t = value / 100`, then for every per-fold slider: set its slider to `t × targetAngle` (where `targetAngle = parentEdge.defaultAngle` for that hinge, taken from the per-fold default), and dispatch a synthetic `input` event so the per-fold handler fires. This keeps the per-fold UI in sync. Update the global row's `.val` span ("`<n>%`").

The one-handler-per-row approach (rather than one global handler with a switch) keeps the per-fold UI generation inside Task 1's renderScene-time clearing-and-rebuilding cycle clean.

### Task 7 — Update the thickness rebuild for N panels

The current `debouncedRebuild` (line 1303) sets `parsed.thicknessMm` and calls `renderScene(parsed)`. `renderScene` short-circuits on the cached `parsed._polygon`, so silhouette extraction doesn't re-run on slider tweaks. With folds, the same `_polygon` cache works, **but the face graph itself is also a function of the silhouette + folds, both of which are stable across thickness changes**. Add a parallel cache `parsed._faceGraph` set inside `renderScene` after Task 3 runs (or null if the single-slab path was taken). Reuse it on thickness rebuilds to skip the recomputation.

Invalidate `parsed._polygon` AND `parsed._faceGraph` on each new `loadSVG` (set both to null at the top of `loadSVG`, or at the bottom of `parseSVG` if cleaner).

The 80 ms debounce stays. Per-region rebuild may be visibly slower than v1a's single-slab rebuild on large fold counts (069 → 13 slabs each rebuilt; 066 → 22 slabs); accept this. If real-world responsiveness suffers later, a follow-up prompt can swap the rebuild for an in-place geometry mutation.

### Task 8 — Extend the diagnostic block

After the existing `console.log` block in `renderScene` (lines ~1176–1183), append:

```js
if (faceGraph) {
  console.log('Face graph:', faceGraph.regions.size, 'regions,',
              faceGraph.foldEdges.length, 'fold edges,',
              `root: ${faceGraph.rootId} (${rootSource})`);
  console.log('Per-fold paths:',
              [...pathHingeMap.entries()]
                .map(([id, hinges]) => `${id}: ${hinges.length} hinge${hinges.length > 1 ? 's' : ''}`)
                .join(', '));
  if (sliverCount > 0)  console.log('Slivers filtered:', sliverCount);
  if (orphanCount > 0)  console.log('Orphans (rendered flat with banner):', orphanCount);
  if (unknownTagCount > 0) console.log('Unknown-tag edges:', unknownTagCount);
}
```

Where `rootSource = 'root-marker' | 'largest-by-area'`. Keep the rest of the v1a diagnostic block intact.

---

## Verification Checklist

1. `preview.html` is still a single self-contained file at repo root. Line count rises (estimate +400–500 lines for cuts + hinge tree + UI; reasonable to land around 1750–1850 lines).
2. v1a single-slab fallback still works on an SVG with no fold layers (test with a copy of 069 that has `<g id="folds-valley">` deleted, or any piece SVG without fold authoring). Banner: "No folds parsed; rendering single slab." Slab renders, thickness slider works, axle/rotation sliders behave per v1a.
3. Drop `inbox/069.svg`. Diagnostic block reports: Silhouette (Tier 1 from `<g id="silhouette">`); Face graph: 13 regions, 8 fold edges, root: `region-N` (largest-by-area); Per-fold paths: 8 entries — most `×1`, but the two paths shared between BASE↔WALL and WALL↔CORNER each show `×2` (or whatever the actual count is — the spec call is `1 path id, N hinges using it`).
4. 3D view shows the unfolded box net flat (BASE in center, walls + corners + ext tabs around it). Scan texture mapped correctly across all 13 panels (no rotation/mirror artifacts).
5. Move global fold slider 0 → 100%. Box folds up: walls rotate up first, then corners and ext tabs rotate to vertical relative to their walls. Some panel interpenetration at intermediate angles is acceptable — v1 has no phase sequencing or collision resolution.
6. Move thickness slider 1.0 → 4.0 mm. All 13 slabs grow. Rebuild visible-but-tolerable lag (a few hundred ms per tick is fine; if it stutters worse, log a follow-up but do not block).
7. Find a per-fold slider whose default is −90° (corresponds to a BASE↔WALL valley). Move from −90° to 0°: that one wall returns to flat while others remain folded.
8. Move axle rotation slider while folds are partway up. Entire folded assembly rotates around the axle wire as a rigid body. (This is the rotation-pivot-wraps-fold-tree composition.)
9. Drop `inbox/066.svg`. Diagnostic: 22 regions, 22 fold edges (20 valley + 2 mountain), root: largest-by-area, Axles empty banner unchanged. Long narrow tube net renders flat.
10. Move global fold slider 0 → 100% on 066. Mountains bend opposite to valleys (sign of `defaultAngle` carries through). Tube doesn't perfectly close — that's a phase-sequencing limitation, not a bug.
11. Reset button resets thickness, every per-fold slider, and the global slider. Rotation slider has its own Reset and is unchanged by this button.
12. No console errors during any interaction. No `NaN` positions. Render-on-demand still drops to idle when no slider is being touched.

---

## What NOT to Change

- Do not modify `buildSlab(polygon, thicknessMm)`. v1b calls it once per region; the contract is exactly what v1a + back-face-mirror + texture-flip + thickness-fix shipped.
- Do not modify `extractSilhouette(p)` or any of its three tiers. The polygon it returns is the input to the face graph.
- Do not modify `buildScanTexture` or its cache (`_scanTexCache` / `_scanTexCacheSrc`).
- Do not modify the axle-wire loop or `buildAxleWire`. Wires stay world-anchored, outside the pivot. (The optional `north` sphere does move into the panel that contains it — see Task 5.)
- Do not modify the rotation slider handler. `currentSlabPivot.rotation.z` continues to be the only thing it writes; the pivot now wraps the whole fold tree, so rotation composes correctly with folds for free.
- Do not change `tex.flipY` (default `true` is correct; verified in the texture-flip pass).
- Do not regress render-on-demand. Per-fold + global slider input handlers must call `requestRender()`. No per-frame work.
- Do not implement cutouts subtraction (`<g id="cutouts">` `cutout-N` children). That's the next prompt (M0.6.10).
- Do not implement multi-cutaway slabs. That's M0.6.11.
- Do not implement marks-layer rendering, glue-zones rendering, or labels rendering. v1 scope is silhouette + folds + axles + thickness, nothing else.
- Do not implement phase sequencing on the global fold slider. Single 0–100% drives all hinges proportionally to their `targetAngle`.
- Do not implement SVG writeback / "Export updated SVG." Out of v1 scope; would be its own prompt.
- Do not bump `work/viewer/package.json` or any version. `preview.html` is pre-v0.1.0; the per-prompt milestone label is the identifier.

---

## Manual tests (post-merge, on Alan's mac)

1. Pull `main` after merge. Verify `preview.html` is updated.
2. Open `preview.html` via Finder double-click (`file://`). Drag-drop `inbox/069.svg`. Confirm 13-panel render and the diagnostic block.
3. Sweep the global fold slider through 0 → 100% → 0. Box folds up, then back down. Some interpenetration mid-fold is expected.
4. Pick any per-fold slider (start with one whose label suggests BASE↔WALL); sweep through −180° → +180°. Confirm only that hinge's panel(s) move, and that path ids driving multiple hinges (069's paths 2 / 3 if applicable) move both hinges in sync.
5. Adjust thickness 0.4 → 4.0 mm. Confirm rebuild is debounced and tolerable across 13 slabs.
6. Drag-drop `inbox/066.svg`. Confirm 22-panel render, 20 valley + 2 mountain in diagnostics, axles-empty banner.
7. Sweep global fold slider on 066. Confirm mountains bend opposite to valleys.
8. Drop a synthetic SVG with no fold layers (copy 069, remove `<g id="folds-valley">`). Confirm v1a single-slab fallback with the "No folds parsed; rendering single slab" banner.
9. With 069 loaded mid-fold, move the rotation slider through −180° → +180°. Confirm the entire folded assembly rotates around the axle wire as one body. The wire stays in place (world-anchored).
10. Reset button: confirm thickness, per-fold sliders (every one), and global slider all return to defaults. Rotation slider is unchanged (its own Reset still works).

Capture any unexpected behavior in the session note's "Known issues at ship" section. Of particular interest if seen: `polygon-clipping` producing zero-area or self-intersecting outputs on real authored SVGs; per-fold counts off by one (likely an edge-tag matching `ε` issue); orphan regions on either test SVG (none expected).

---

## Branch / commit / PR

- **Branch:** `claude/preview-html-v1b`. If Claude Code starts on an auto-generated random-name branch (e.g. `claude/vigorous-rhodes-…`), rename via `git branch -m claude/preview-html-v1b` before the first commit.
- **Commit subject** (imperative, lowercase, ≤70 chars): `extend preview.html: face graph + hinge tree + fold sliders (v1b)`
- **PR title:** same as commit subject.
- **PR description:**
  - One-line summary.
  - "What changed" — `preview.html` → UPDATED; `sessions/2026-05-03-XXXX_code_preview-html-v1b.md` → NEW.
  - Manual test steps (link or paraphrase the section above).
  - Branch name + commit SHA(s).
  - Link to this prompt file at repo root.

Canonical PR command (run directly; `gh` is installed and authenticated on Alan's mac):

```bash
gh pr create \
  --base main \
  --head "$(git branch --show-current)" \
  --title "extend preview.html: face graph + hinge tree + fold sliders (v1b)" \
  --body-file "<path-to-prepared-body.md>"
```

---

## End-of-session

1. Write the session note at `sessions/2026-05-03-XXXX_code_preview-html-v1b.md`. Include: branch name, commit SHA, what was done, what's in the PR, and any known issues at ship (especially around `polygon-clipping` edge cases, sliver-filter calibration, edge-tag tolerance `ε`).
2. Flip this prompt's `status` from `ready-for-code` to `shipped`. Add `shipped: 2026-05-03` (or actual ship date) in the front matter. Add the standard italic header below the front matter:
   `_Shipped YYYY-MM-DD; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._`
3. Push branch, open PR via `gh pr create`. Return the PR URL in the final chat message so Alan can review and merge in-browser.
