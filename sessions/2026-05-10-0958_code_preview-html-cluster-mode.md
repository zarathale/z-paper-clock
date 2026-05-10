---
date: 2026-05-10
start_time: "09:30"
end_time: "09:58"
mode: code
participant: Zarathale (Alan)
target: preview-html-cluster-mode
orchestration_prompt: CODE_PROMPT_preview-html-cluster-mode.md
---

## Goal

Land PR C of three (DECISIONS #13): Cluster-mode in `preview.html`. Multi-piece subassembly authoring tier — load every piece in a named cluster, see them placed via per-piece `assembled.transform`, select / manipulate / measure individual pieces.

## What was done

`preview.html` (+~1100 LOC net):

- **Cluster-mode UI scaffolding.** Topbar gains a `#cluster-controls` slot (cluster id input + Load + Measure toggle), shown only in cluster mode. Side panel gains `#cluster-panel` (selected piece label, Save selected piece, Deselect, Measurements list) and a Bench-only `#conn-toggle-row` (Show connection points checkbox). Removed the PR A `#cluster-stub` overlay and the CSS rules that hid the side panel sections in cluster mode now coexist with the new cluster controls.
- **Mode-aware "active piece" abstraction.** Introduced `getActivePieceContext()` returning `{ pieceGroup, pieceId, originKind, cluster, mode }` — Bench surfaces `currentPieceGroup`, Cluster surfaces the selected piece's pieceGroup. Refactored `attachTransformToCurrentPiece` (kept as alias) → `attachTransformToActivePiece`; `refreshTransformPanel`, `onTransformSliderInput`, `onTransformControlsChange`, and the Reset Transform handler all route through the new context. The Transform panel now binds to the selected cluster piece in cluster mode.
- **Mode swap teardown.** `setMode` calls `teardownBenchScene()` on bench → cluster swap and `teardownClusterScene()` on cluster → bench swap. Each teardown disposes geometry/materials, clears state globals, and resets the mode-specific UI sections.
- **`loadCluster(name)` + transitive walk.** New entry point: looks up `name` in `connectionGraph.graph.pivot_clusters`, expands the seed list by walking valid edges in either direction (caps at 50 pieces and banner-warns if exceeded — guards against an infinite walk). For the anchor cluster's seed `[067, 069]`, this expands to `[065, 066, 067, 068, 069]`.
- **`loadClusterPieces(ids, name)` per-piece load.** Fetches each piece's SVG + sidecar in parallel (with `NNN.svg` → `NNNa.svg` → `NNNb.svg` fallback for split pieces). Skips cut-line-first pieces with a per-piece warning (cluster mode v1 is panels-first only). Each piece runs through `renderPanelsFirstScene(p, { sceneMode: true })` to get a sceneGroup, which is then wrapped in a per-piece `pieceGroup` with sceneGroup offset by `-naturalOrigin3js` so `pieceGroup`'s local (0,0,0) is the natural rotation origin (mirrors Bench's `wrapForTransform` inner-group convention). Sidecar's `assembled.folds` is applied to the piece's hinges via `applyClusterPieceFolds`; sidecar's `assembled.transform` is applied to the pieceGroup via the now-shared `applyAssembledTransformToGroup`.
- **`loadClusterAdHoc(pieceIds)` for cross-cluster lists.** When a comma-list spans multiple clusters (or no cluster), pieces load with `frame: world`. When all ids share a cluster, auto-routes to `loadCluster(name)` with the full transitive membership.
- **Per-piece selection + visual indicator.** `selectClusterPiece(id)` toggles a per-piece cyan wireframe (`THREE.LineSegments` of an `EdgesGeometry(BoxGeometry)` sized to silBbox + outset thickness, child of sceneGroup so it rotates with the piece), attaches TransformControls to that piece's pieceGroup, refreshes the Transform panel + cluster panel labels.
- **Connection-point spheres.** `buildConnectionSpheresOnSceneGroup(p, sceneGroup, id)` adds 1mm-diameter colored balls (red attach, blue landing, yellow pivot-anchor) at each authored centroid as children of sceneGroup so they move with the piece. Sources: `panelsFirst.attachPoints` (pivot/attach distinction by `pivot-` prefix); `marksCentroidsById` for `tab-` and `landing-` markers (cross-piece partnering primitive). Same builder is reused for the optional Bench-mode "Show connection points" overlay (`showBenchConnectionPoints` / `hideBenchConnectionPoints`).
- **Click-to-pin distance measurements.** `Measure` toggle in topbar. Pointer-up handler raycasts: in select mode → pieceGroup hit → `selectClusterPiece`; in measure mode → connection-sphere hit → `pendingMeasurementPoint`. Second click pins a `Measurement` entry: 2-vertex `THREE.Line` between world positions + a `CanvasTexture`-backed `THREE.Sprite` label rendered as "X.X mm". `updateMeasurementVisuals()` re-resolves world positions each frame via `mesh.getWorldPosition`; canvas redraw debounced to ≥0.05mm change. Per-frame tick uses a dedicated `requestAnimationFrame` loop that triggers when `currentMode === 'cluster' && measurements.length > 0`. Side panel lists each measurement with a remove button. Suggests connection-graph partner via banner on first click (e.g. tab-c on 065 → "click landing-c65 on 066").
- **Per-piece save in cluster context.** `saveSelectedBtn` handler builds an `assembled` payload from the selected piece's `pieceGroup` pose. Identity transforms (within EPS=0.01) are omitted; existing sidecar `assembled.folds` is carried forward so the modal output is a complete `assembled` block (user can hand-edit folds out if they only want to update transform). `frame: 'cluster'` when `currentClusterName` is set and not `<ad-hoc>`; `frame: 'world'` otherwise. Reuses the existing `showAssembledPoseModal` (copy/download).
- **Backwards-compat for old comma-list scene mode.** `loadScene(rawIds)` (the existing scene input + `?piece=N,N,N` URL) now parses the list and calls `loadClusterAdHoc`. The old `renderSceneMulti` (200+ LOC of pivot-cluster co-location) is deleted entirely; the `sceneGroups` global is removed; the cleanup loop in `renderScene` that disposed old multi-piece groups is removed (mode-swap teardown handles it). Pre-PR-C URLs (`?piece=065,066,067,068,069`) auto-resolve to cluster `anchor`.
- **URL bootstrap.** New `?cluster=<name>` param; both `?cluster=` and `?piece=N,N,N` defer to `waitForConnectionGraph()` (3s timeout) so the transitive walk has data. `?piece=NNN` (single id) keeps Bench-mode behavior. Cluster load updates `history.replaceState` to `?cluster=<name>` so the URL reflects the active cluster.

Verification (via Claude Preview MCP against `python3.12 -m http.server`):

- Cluster `anchor` loads 5 pieces (065/066/067/068/069) — transitive walk works.
- 069's saved sidecar transform applied (Y=7.1mm, rX=99.5°); other 4 piece-load banners report missing transforms.
- Selection mesh becomes visible; Transform panel binds to selected piece (slider tx=30 moves only 069, leaves 067 unchanged).
- Two pinned measurements (`067:pivot-anchor → 069:pivot-anchor` reads 7.1mm; `067:landing-c69 → 069:landing-taba` reads 9.4mm); distances update live when 069 moves (30mm X-shift → distance becomes 30.8mm = √(30² + 7.1²)).
- Save selected piece emits a clean cluster-frame transform JSON for 069 only, carrying its 10 sidecar folds.
- Mode swap (cluster → bench → cluster) leaves zero stray pieces / measurements / spheres.
- Comma-list backcompat: `loadScene('065,066,067,068,069')` auto-resolves to cluster `anchor`.
- Bench mode regression check: `loadPieceById('069')` still works post-cluster (10 fold sliders, 6 transform sliders, panel visible, rotation hidden).
- Zero browser console errors throughout.

## Branch / commit

- Branch: `claude/preview-html-cluster-mode` (renamed from auto-generated `claude/practical-raman-5b957f` per CLAUDE.md rule before first commit)
- Commit: pending (this session note written before the commit)

## Open questions

- **Tab markers on 069.** 069's marks layer doesn't author `tab-c`/`tab-d`/etc. as separate markers (only `landing-taba`/`landing-tabb` closures + `h`/`i` section labels). Cross-piece tab→landing measurements between 067's landings and 069's tabs aren't measurable as a result. Not a PR C bug — the convention treats tab markers as authored-or-not per piece, and the SVG just doesn't have them. Surface to authoring side: if cross-tab measurements become important, those `tab-X` markers need to land in 069's marks layer.
- **069 sidecar's `rX = 99.5°`** is from a prior PR B capture. Not relevant to this PR but the loaded pose looks "tilted" in the preview screenshot — confirms the transform is being read + applied correctly.
- **Cluster-pose authoring loop.** The Cluster scene now puts every piece without a saved transform at world origin (which means everyone overlaps). Manual tests in the prompt describe the loop: select piece, drag/slider into place, save → merge → reload. PR C lays the rails; the actual pose-capture for the rest of the anchor cluster is the post-merge work.

## Next-session handoff

Per the manual-tests block in `CODE_PROMPT_preview-html-cluster-mode.md`: load Cluster → `anchor`, manually adjust 067/068/065/066 transforms until they sit correctly relative to 069, click Save selected piece for each one, merge JSON into the per-piece sidecars by hand, reload to confirm pose persistence. The four pieces without saved transforms surface as a banner-warn at load time. This is authoring work, not Code work — Cowork tracks it via `claude-work/STATUS.md`.
