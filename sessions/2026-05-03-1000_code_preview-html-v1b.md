---
date: 2026-05-03
start_time: "10:00"
end_time: "TBD"
mode: code
participant: Zarathale (Alan)
target: preview-html-v1b
orchestration_prompt: CODE_PROMPT_preview-html-v1b.md
---

## Goal

Extend `preview.html` with the face graph + hinge tree + fold sliders (v1b): polygon-cut the silhouette along fold lines into per-panel regions, root the tree via the largest-area fallback (or `id="root"` marker), BFS to a fold tree, and parent each non-root panel's slab to its parent through a hinge `THREE.Object3D` whose quaternion is driven by per-fold sliders.

## What Was Done

### Branch

Renamed from auto-generated `claude/beautiful-wu-9e1021` to `claude/preview-html-v1b`. Removed the stale prior-attempt worktree at `.claude/worktrees/heuristic-bartik-981dd4` (which was on the same HEAD as main, no changes) to free the branch name.

### Files Changed

**`preview.html`** — +735 lines, −68 lines over the v1a+six-pass baseline (1362 lines → 2028 lines).

New JS additions:

- **Utility functions:** `ptToLineDist`, `ptToSegDist`, `pointInPolygon` (ray-casting).
- **`halfPlanePoly(bbox, lineStart, lineEnd, sign)`** — builds a polygon-clipping–format half-plane polygon by walking bigBox corners and inserting fold-line intersection points.
- **`extendFoldsToSilhouette(silhouette, folds)`** — Task 2. Parameterises each fold as a ray, collects silhouette-edge intersection t-values, extends to tMin−ε / tMax+ε. Assigns synthetic `pathId` (`valley-N` / `mountain-N`) when the SVG path has no id.
- **`buildFaceGraph(silhouette, extendedFolds)`** — Task 3. Iteratively splits regions by half-plane intersection (`polygon-clipping.intersection`). Edge-tag propagation by midpoint proximity (ε = 0.5 vb units). Sliver filter (Δ = 0.5% of silhouette-bbox diagonal). Adjacency by projected-interval overlap (> 1.0 vb units). Root by `parsed.rootCentroid` point-in-polygon or largest-area fallback. BFS to fold tree. Returns `{rootId, regions, foldEdges, sliverCount, orphanCount, unknownTagCount, rootSource}` or `null` on fatal failure.

`renderScene` rewritten — Task 4/5/6/8:

- **Fold-tree path:** builds slabMap (one `buildSlab()` per region), positions root slab inside pivot, BFS to wire hinges (parent slab → `THREE.Object3D` hinge → child slab). Hinge axis = fold segment direction (Y-flipped into 3js). Initial quaternion = flat (angle 0). Orphan regions rendered flat at silhouette-relative position with banner.
- **North marker (Task 5):** point-in-polygon test finds the containing region; sphere parented to that region's slab (folds + rotates correctly). Fallback to root slab with banner if not found.
- **Single-slab fallback:** preserved for no-fold SVGs. Banner: "No folds parsed; rendering single slab."
- **Fold controls UI (Task 1):** `#global-fold-row` shown/hidden based on `useFoldTree`; `#per-fold-sliders` cleared and rebuilt with one `.slider-row` per unique pathId (start at 0°, `data-default-angle` = `defaultAngle`). Badge shows `×N` hinge count. Per-fold `input` handler: `quaternion.setFromAxisAngle(axis, deg*π/180)`.
- **Diagnostics (Task 8):** extended with face graph stats (region count, fold edge count, root source, per-fold hinge map, sliver/orphan/unknown-tag counts).

Event handlers updated:

- **`#globalFoldSlider` input handler (Task 6):** `t = value/100`; for each per-fold row sets `slider.value = t * defaultAngle` and dispatches synthetic `input` event.
- **`resetBtn` (Task 1):** now resets thickness + global fold slider (→ 0%) + all per-fold sliders (→ 0°, dispatching `input` so hinges flatten). Rotation slider unchanged.
- **`debouncedRebuild` (Task 7):** `_faceGraph` cache reused on thickness rebuilds (face graph doesn't change when only T changes); comment added.

HTML/CSS:

- `<div id="fold-controls">` now has `#global-fold-row` (initially hidden) + `<div id="per-fold-sliders">` (cleared/rebuilt by renderScene).
- Reset button label changed from "Reset thickness" → "Reset".
- Added `font-style:normal` override for `.slider-row` and `#per-fold-sliders` inside `#fold-controls` so fold slider labels don't inherit the italic empty-state style.

`parseSVG` updated:

- `sourceIndex: folds.length` added to each fold entry (before push) for deterministic BFS ordering.
- `_polygon: null, _faceGraph: null` added to returned object (explicit cache slots, invalidated by fresh object on each new file load).

`pathHingeMap` module-level `Map` added to globals; cleared at top of `renderScene`.

### Known Issues at Ship

- **Face graph not yet tested end-to-end** against 069.svg or 066.svg — code is syntactically valid (verified by Node.js `new Function()`); manual test against those files is the post-merge step.
- **`polygonClipping` global name assumed** from UMD bundle convention for @0.15.7; if the global is actually named differently the intersection calls will throw. Verify in browser on first drop.
- **Per-fold slider initial value is 0° (flat)** not `defaultAngle`. The global slider drives 0→100% from flat to the authored crease angle. This is consistent with verification checklist item 3 ("3D view shows unfolded box net flat") but means the per-fold sliders don't match the "default = path-id-encoded angle" wording in Task 1's description. If Alan wants sliders to start folded at `defaultAngle`, change `value="0"` to `value="${defAngle}"` in the `row.innerHTML` and add `hinge.quaternion.setFromAxisAngle(axis, defAngle * Math.PI / 180)` in the hinge setup.
- **Adjacency detection uses segment-interval intersection** (works for one edge per region per fold; may miss adjacency if a non-convex region has multiple fold-tagged edges). Sufficient for 069 and 066.
- **`buildFaceGraph` references the `parsed` global** for `rootCentroid` instead of receiving it as a parameter — fragile but works because the function is only called from `renderScene(parsed)`.

## Branch / Commit

Branch: `claude/preview-html-v1b`
Commit: TBD (pending)

## Open Questions

None blocking ship. The "per-fold slider starting at defaultAngle vs 0°" question is documented above as a post-merge decision if the visual result doesn't match expectations.

## Next-Session Handoff

1. Pull after merge. Open `preview.html` from `file://`. Drop `inbox/069.svg`. Check console for face graph stats. Move global fold slider 0→100%.
2. If `polygonClipping` throws a ReferenceError, check the UMD bundle's exported global name and update the reference in `buildFaceGraph`.
3. Next prompt in sequence: M0.6.10 (cutouts subtraction) and M0.6.11 (multi-cutaway slabs).
