---
date: 2026-05-04
start_time: "11:45"
end_time: "TBD"
mode: code
participant: Zarathale (Alan)
target: preview-html-face-graph-diagnostics
orchestration_prompt: CODE_PROMPT_preview-html-face-graph-diagnostics.md
---

## Goal

Ship the diagnostic harness specced in `CODE_PROMPT_preview-html-face-graph-diagnostics.md` — additive instrumentation on `buildFaceGraph` (shared-edge index + per-fold candidate annotation + JSON dump + 2D overlay + structured console summary) without changing the adjacency or BFS algorithms.

## What was done

All six tasks from the prompt landed in `preview.html`:

1. **Step 4.5 in `buildFaceGraph`** — new shared-edge index built post-sliver-filter via `edgeKey` (canonicalised quantised endpoint pair, granularity 1/1e4 viewBox units). Per-fold candidate annotation walks each `extendedFold`, pools shared edges by marker-region for marker-bound folds (full list otherwise), scores by `ptToFoldLine`, attaches top-3 to `fold._diagCandidates` + the resolved `_diagMarkerRegionId`. The actual adjacency in step 5 is unchanged.
2. **`_diag` payload on `buildFaceGraph` return** — adds `pieceFile`, `viewBox`, `silhouettePolygon`, regions (id/polygon/area/vertexCount/isRoot/parentId/edgeTags), folds (id/pathId/layer/markerBoundId/defaultAngle/authoredStart-End/extendedStart-End/sharedEdgeCandidates/markerRegionId), foldEdges (existing fields), sharedEdges, marksCentroidsById, summary block. Existing return fields preserved.
3. **Panel section** — `#diagnostics-section` between `#rotation-section` and `#help`, two buttons (Dump face graph / Show overlay), CSS rule mirroring the other section gaps. DOM refs added next to the existing const block.
4. **Dump button** — `downloadFaceGraphDump` reads `window.__lastFaceGraph._diag`, builds a Blob, triggers a download named `face-graph-<sanitised-piece>-<iso-timestamp>.json`. Disabled when no face graph is available; an error banner fires if clicked anyway.
5. **2D overlay + legend** — both mounted inside `#canvas-host` after `renderer.domElement`. Overlay is an `<svg preserveAspectRatio="xMidYMid meet">` with `position:absolute; inset:0; pointer-events:none; background:rgba(26,26,26,0.88)` so the 3D view fades behind a clearly different 2D viewBox-space chart. Seven render layers (silhouette / regions golden-angle hsl / shared edges / fold authored segments dashed / top-1 candidate green-or-amber / marker centroids white-with-text / region id labels at area-weighted centroids). All sizes scale relative to viewBox diagonal so 069 (3417×3342) and 001 (28975×4871) both render legibly. Legend top-right disclaims "2D viewBox-space; not aligned to 3D camera."
6. **Console summary** — `logFaceGraphSummary(_diag)` prints a one-line header (regions / folds / active-edges / passive-edges / shared-edges / slivers-filtered) plus a `console.groupCollapsed('[face-graph] folds:')` block with per-fold ✓/✗/⊘ marks. Threshold: 5 viewBox units. Fires once per fresh build (not on cached thickness rebuilds).

`renderScene` integration: disable buttons at top while a build is in flight; cache `window.__lastFaceGraph = faceGraph`; on fresh-build path call `logFaceGraphSummary(faceGraph._diag)`; if overlay is currently on, call `renderFaceGraphOverlay(faceGraph._diag)`; clear overlay if no face graph; re-enable buttons at end conditional on `faceGraph` being non-null.

## Verification

Tested all three pieces on `localhost:8770/preview.html?piece=NNN`:

- **069 baseline** — 14 regions, 8 folds (all unidentified), 17 shared edges, 9 slivers filtered, 6 passive fold edges. All ⊘ entries with `dist=0.00` — top candidate shared edges land exactly on each fold line (geometric adjacency had no trouble). Overlay shows a clean concentric-region pattern with 11 named markers (tab-a..g, landing-a/b/g/h) and 14 region labels.
- **001 auto-rename cluster** — 9 regions, 6 folds, 10 shared edges, 24 unknown-tag edges. `fold-tab-b` and `fold-tab-e` resolve correctly (`markerRegionId=region-8` / `region-0`, dist=0). The four `fold-tab-a/-a1/-a2/-a3` paths fall through `parseMarkerBoundFoldId` (only `tab-a` exists in `marksCentroidsById`; `tab-a1/2/3` don't), so they're flagged ⊘ unidentified — the diagnostic exposes that the auto-rename cluster needs re-authoring (or the parser needs sibling-rename tolerance). Existing parser banners ("fold- prefix but no matching marker…") fire as before.
- **066 the hard case** — 32 regions, 21 folds (15 marker-bound, 6 unidentified), 24 shared edges, **184 unknown-tag edges, 82 slivers filtered**. Of the 15 marker-bound folds: 1 ✓ (dist ≤ 5u), 12 ✗ (dist > 5u, suspect), 0 with marker centroid not in any region, **2 marker-bound where the marker region's shared-edge pool was empty** (no `_diagCandidates[0]`). The phantom-strip phenomenon is visible in the overlay as long thin colored bands running the full strip. The combination of "many ✗ marker-bound folds" + "82 slivers filtered" + "184 unknown-tag edges" is exactly the data the next algorithm prompt needs to choose between shared-edge-with-tightened-picker, cut-trim, or both.

Other checks:
- No console errors. Existing rendering on each piece (3D slab, axles, fold sliders, rotation slider, thickness slider, fold-all + Flat/Assembled buttons) all work as before.
- Overlay's `pointer-events: none` confirmed by `getComputedStyle` — orbit/zoom/pan pass through.
- Toggle button text flips Show ↔ Hide on click.
- Drag-loading a different piece while overlay is on re-renders for the new piece's viewBox + region colors + candidate edges (verified by toggling between 069 / 001 / 066).
- JSON dump verified parseable; payload sizes 29KB (001) / similar order on 066+069. All expected keys present.

## Files touched

- `preview.html` — additive only. New sections: shared-edge index + candidate annotation in `buildFaceGraph` (Step 4.5); `_diag` payload on return; `#diagnostics-section` panel HTML + CSS; DOM refs; `setupFaceGraphDiagnostics()` + `downloadFaceGraphDump()` + `polyCentroid2D()` + `renderFaceGraphOverlay()` + `logFaceGraphSummary()` helpers; `renderScene` start-of-function disable + post-build hook + end-of-function enable. Bootstrap calls `setupFaceGraphDiagnostics()` after `initScene()`.
- `CODE_PROMPT_preview-html-face-graph-diagnostics.md` — front matter flipped to `status: shipped` with `shipped: 2026-05-04`; italic time-of-write header added below the front matter.
- `sessions/2026-05-04-1145_code_preview-html-face-graph-diagnostics.md` — this note.

No SVGs, no pipeline scripts, no convention docs, no `pieces.csv` touched. The marker-bound fold ids convention is unchanged.

## Branch / commit

Branch: `claude/preview-html-face-graph-diagnostics` (renamed from auto-generated `claude/happy-gates-80598e` before any commit, per CLAUDE.md). Commit SHA + PR URL recorded post-push.

## Open questions

None from the implementation side — every task in the prompt landed cleanly. The post-merge cowork session reads what 066's debug overlay surfaced and picks the next algorithm prompt:

- 184 unknown-tag edges + 82 slivers + 12 ✗ marker-bound folds suggest BOTH over-broad adjacency AND phantom strips dominate on 066 — i.e. the answer is likely "shared-edge AND cut-trim together" rather than either alone. But the exact call is Alan's after looking at the 066 dump JSON in detail.

Two diagnostic data points worth flagging:

1. **2 marker-bound folds on 066 have empty shared-edge pools** — i.e. their marker region has no shared edges in the `sharedByRegion` index. That means the marker centroid landed in a region that's a "leaf" with no topological neighbors at all. Could be an authoring issue (marker placed in a sliver region the marker centroid happens to fall inside) or a real signal that the half-plane cut isolated some panels. Worth looking at in the dump.

2. **001's `fold-tab-a/-a1/-a2/-a3` cluster** — confirms the prompt's prediction. Either re-author 001 to give each path a unique tab marker, or grow `parseMarkerBoundFoldId` to accept a sibling-rename suffix (e.g. `tab-a1` → `tab-a` if the bare form exists). Diagnostic shows the geometric adjacency works fine for 001's 9 regions, so the absence of marker binding here is mostly cosmetic.

## Next-session handoff

**Cowork session reads 066's debug overlay JSON.** Open `preview.html?piece=066`, click Dump face graph, inspect the JSON. Look at: per-fold `sharedEdgeCandidates` for the 12 suspect entries; the 2 empty-shared-edge-pool folds; whether any region polygons are visibly the "phantom strips" the existing `passive`-edge handling was trying to mitigate. Use that to pick the next CODE_PROMPT — shared-edge-only (with tightened picker), shared-edge + cut-trim, or some other direction.

**Permanent payoff.** This harness stays in `preview.html` indefinitely. Any future piece whose folds don't render correctly gets the same Dump + Overlay + Console summary tools.
