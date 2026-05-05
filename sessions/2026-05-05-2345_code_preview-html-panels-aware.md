---
date: 2026-05-05
start_time: "23:45"
end_time: "00:30"
mode: code
participant: Zarathale (Alan)
target: preview-html-panels-aware
orchestration_prompt: CODE_PROMPT_preview-html-panels-aware.md
---

## Goal

Add a panels-first parser pathway to `preview.html` alongside the existing cut-line-first one, so SVGs with `<g id="panels">` render via the panels-aware path (per LAYER-CONVENTIONS.md / DECISIONS #6 + #7) and pre-pivot pieces fall through to legacy cut-line-first.

## What was done

`preview.html` gains an end-to-end panels-first dispatch:

- **Detection.** `parseSVG` probes for `<g id="panels">` with content; if present, it skips legacy `parseFoldLayer` (which was emitting a "fold- prefix but no matching marker" banner per panels-first fold) and instead populates `parsed.panelsFirst = { panels, folds, hingeTree, attachPoints, marks }`.
- **Panel parsing.** New `parsePanelsLayer` walks every id-bearing `path | rect | circle | ellipse | polygon | polyline` inside the panels layer, tolerating `cutaway*` / `cutout-*` ids per LAYER-CONVENTIONS. Each panel becomes `{id, polygon, bbox, centroid}`.
- **Fold parsing.** New `parsePanelsFirstFolds` mirrors the Python `parse_fold_bindings` from `claude-work/scripts/build_assembly_graph.py`: tries every split point of `fold-<a>-<b>` against the panel set, accepts optional `-<deg>` suffix for default angle, and records `<circle>`/`<ellipse>` folds as descriptive curved folds with cx/cy/r.
- **Hinge forest.** `buildHingeTree` produces a BFS spanning forest — each connected component of two-panel folds becomes its own sub-tree rooted at the highest-degree unvisited panel (alphabetical tiebreaker). Disconnected components surface as additional sub-roots; cycle folds are reported separately.
- **Renderer.** `renderPanelsFirstScene` reuses the existing `buildSlab`, `buildAxleWire`, `MM_PER_UNIT`, `pathHingeMap`, axle pivot, and slider machinery. For each sub-root, it places the slab at silhouette-relative position; BFS down each sub-tree wires `parent → THREE.Object3D hinge → child` (axis = fold direction in 3js coords, hinge origin at fold midpoint) and registers each fold in `pathHingeMap` with `{target, axis, signFwd, mode: 'fold'}`. The `signFwd` heuristic matches cut-line-first's polarity logic so valley/mountain behaviour is consistent across both paths.
- **Curved-fold sketch.** Descriptive `<circle>` / `<ellipse>` folds find their host panel by closest centroid, then wrap the host panel's slab with an extra `Object3D` rotator whose axis is the tangent direction at the closest point on the circle to the panel centroid. Slider input rotates the wrapper around its own origin (= the panel's centroid in world space). Approximate sketch — geometrically correct rotation would require splitting the slab along the curve; deferred to M6 mechanism animation per CODE_PROMPT task 7.
- **Dispatch banner.** Top of `renderScene` now emits `panels-first ✓ — N panels, M folds, root: <id>` for panels-first pieces, or `cut-line-first (legacy) parser` for everything else, so the active path is obvious during development.
- **Console diagnostics.** Panels-first path logs the panel list, fold counts (valley + mountain), sub-roots, descriptive/cycle counts, and attach-point/mark counts. The cut-line-first instrumentation (face-graph dump button, overlay) is hidden when panels-first is active — those buttons consume `_diag` from `buildFaceGraph`, which doesn't run on this path.

The legacy cut-line-first pathway (`buildFaceGraph`, `extendFoldsToSilhouette`, cut-trim, the diagnostic harness from PR #13) is **untouched** — pre-pivot pieces (058, 113, 002, etc.) still render through it. Two surgical changes outside the new code: (a) `parseSVG`'s `parseFoldLayer` calls are gated on `!isPanelsFirstAuthoring` so we don't emit "no matching marker" banners for `fold-<a>-<b>` ids; (b) the `cut-line-first (legacy) parser` banner is added at the top of the legacy path.

### Verified against the prompt's test pieces

| Piece | Layers | Result |
|---|---|---|
| 069 | panels-first | 11 panels, 10 valley folds, root `abc` (tied with `main` at 4 edges, alphabetical tiebreaker). Fold-all → 100% folds the box closed. |
| 068 | panels-first | 19 panels, 17 folds (16 valley + 1 mountain), 2 sub-trees (`pane7` main component + `c2` cluster of 4). All 17 sliders render. |
| 071 | panels-first | 4 panels (a/b/c/d), 3 folds, root `b` (highest degree, ties alphabetical). The `cutaway` sibling inside `<g id="panels">` is parser-tolerated per convention. |
| 099 | panels-first | 2 panels, 3 folds (1 line + 2 curved), root `main`. Curved-fold sliders produce visible approximate movement (host panel tilts around tangent axis). |
| 058 | cut-line-first | Banner reads "cut-line-first (legacy) parser"; existing single-slab fallback unchanged. |
| 113 | cut-line-first | Same legacy fallback chain (no `<g id="silhouette">` per "Known Issues"); behaviour unchanged. |

No console errors anywhere in the test sweep. Multi-piece scene assembly remains the next prompt; the connection-graph data parsed here (`attachPoints`, `marks`) is captured but not yet rendered.

## Branch / commit

- Branch: `claude/preview-html-panels-aware` (renamed from auto-generated `claude/eloquent-northcutt-e1f69e` per CLAUDE.md convention before first commit).
- Commit: TBD — see PR.

## Open questions

None blocking. Two notes for follow-up:

1. **Root selection on 069 picks `abc` instead of `main`** because both have degree 4 and alphabetical tiebreaker selects `abc`. The "main body" panel ergonomically would be the better visual root, but functional rendering is identical. A future enhancement could prefer panels named `main` / `pane1` / `body` when degrees tie.
2. **Curved fold rendering is a sketch.** The `fold-insidetabs` / `fold-outsidetabs` sliders on 099 rotate the entire host panel (`main`) around a synthesized tangent point. The geometrically-correct behaviour would split the slab along the curve and rotate the inner region only; that lives in M6 mechanism animation per CODE_PROMPT.

## Next-session handoff

The follow-up prompt is multi-piece scene assembly: walk `claude-work/state/connection-graph.json` and place pieces in 3D space using cross-piece attach/landing/pivot edges. The panels-first parser path now produces `parsed.panelsFirst.attachPoints` and `parsed.panelsFirst.marks` arrays for that consumer; today they're inert.
