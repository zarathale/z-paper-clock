---
status: draft
started: 2026-05-09
owner: Zarathale (Alan)
target: preview-html-cluster-mode
blocked_by: CODE_PROMPT_preview-html-bench-transform.md (PR B must ship first)
---

# CODE_PROMPT — preview.html Cluster mode multi-piece (PR C of three)

## What You Are Doing and Why

Third of three PRs landing `claude-work/DECISIONS.md` #13. PR A (foundational interaction + cutouts) and PR B (Bench mode transform capture) are dependencies — both must have shipped before PR C begins.

PR C makes **Cluster mode functional**, replacing the stub from PR A. Cluster mode is the multi-piece subassembly authoring tier: the user loads all the pieces of a single subassembly (e.g., the anchor cluster: 065/066/067/068/069), sees them placed in cluster-local space according to each piece's saved `assembled.transform` (PR B), and can independently manipulate any selected piece relative to the others until alignments are right.

Concretely PR C lands:

1. **Cluster-mode load.** A new "Load cluster" input/button that takes a cluster id (e.g., `anchor`) from `connection-graph.json`'s `pivot_clusters`. Loads every piece in the cluster, applies each piece's `assembled.folds` and `assembled.transform`, and renders them in one scene.
2. **Per-piece selection.** Click a piece to select it. Outline (or tint) the selected piece. Only the selected piece shows transform sliders + TransformControls handles.
3. **Distance readouts.** Click a connection point (an attach-point or marks-layer landing) on one piece, then a partner connection point on another piece, to pin a measurement. Live updates as pieces move. Shows current distance in mm. Multiple measurements can be pinned simultaneously.
4. **Per-piece save.** "Save selected piece" button writes back to that piece's sidecar with `frame: cluster`. Each piece's sidecar is independent; saves are scoped to the selected piece.
5. **Multi-piece scene assembly (PR #17) is replaced.** The existing scene mode (loaded via comma-separated piece-ids) is rewritten as a thin Cluster-mode wrapper. Old scene-mode entry points still work as backwards-compatible aliases.

PR C does NOT introduce wall+hook geometry (deferred to PR D / Wall mode), inter-piece edge data in sidecars (still per-piece per DECISIONS #13), or auto-snap of attach-points to landings (still M4 territory).

## Prerequisites — confirm before starting

- PR A and PR B have shipped and merged to `main`. preview.html has: cutouts as Shape holes, slider+text-entry, camera-lock-toggle, click-drag-on-piece via TransformControls, RGB axes, worktable, mode toggle UI, per-piece transform sliders, sidecar `assembled.transform` read+write, origin auto-detect, frame auto-detect, cluster lookup from connection-graph.json.
- DECISIONS #13 is closed. Cluster mode's design is documented there.
- `claude-work/state/connection-graph.json` exists with valid `pivot_clusters`.
- At least one cluster (e.g., `anchor`) has multiple pieces with saved `assembled.transform` blocks in their sidecars (Alan will have captured these via PR B's Bench mode prior to PR C shipping).

## Read These Files First

1. `claude-work/DECISIONS.md` #13 — three-mode design, cluster-local frame semantics.
2. `preview.html` — the Bench mode infrastructure from PR A and PR B is your foundation: `pieceGroup`, `transformControls`, transform sliders, origin auto-detect, sidecar load/save.
3. `preview.html` — existing PR #17 multi-piece scene mode (`loadScene`, `renderSceneMulti`, pivot-cluster co-location). PR C replaces this with a unified Cluster-mode flow.
4. `claude-work/state/connection-graph.json` — `pivot_clusters` array shape, cross-piece edges (used to identify connection points for distance readouts).
5. `claude-work/scripts/build_assembly_graph.py` — for understanding how connection points (attach + landing pairs) are derived; you don't run the script in this PR but you consume its output.

## Target File Structure Changes

```
preview.html                                  ← all preview-side changes
```

No new files. Sidecars get incremental updates as Alan captures cluster-relative poses.

## Numbered Tasks

### Task 1 — Cluster load entry point

**Goal.** When the user is in Cluster mode and types a cluster id (e.g., `anchor`) into the load input, every piece in that cluster loads simultaneously with its `assembled.folds` + `assembled.transform` applied.

**Implementation.**

1. **UI in Cluster mode.** Replace the "Cluster mode lands in PR C" stub from PR A with an input + Load button. Placeholder text: "Cluster id (e.g., anchor)".
2. **Resolve cluster.** On Load click, fetch `connection-graph.json` (already cached from PR B), find the cluster by name, get its `pieces` array.
3. **Load each piece.** For each piece id in the cluster, fetch `work/pieces/NNN/NNN.svg` and `work/pieces/NNN/NNN.json` (sidecar). Parse via the existing parsing pipeline (same code path Bench mode uses).
4. **Build per-piece groups.** Each piece gets its own `pieceGroup` (the wrapping group from PR A Task 4). Apply that piece's `assembled.transform` (Translation + Euler rotation, XYZ order) to its `pieceGroup`.
5. **Add to scene.** All `pieceGroup`s added to the same `THREE.Scene`. Pieces share the cluster-local frame: world origin = the cluster's pivot point.
6. **Banner on load.** "Cluster `anchor` loaded — 5 pieces." If a piece has no saved transform, banner-warn with that piece id (it'll sit at default position which may overlap others).

### Task 2 — Per-piece selection state

**Goal.** Clicking a piece selects it. Visual indication on the selected piece. Transform UI binds to the selected piece. Only one piece selected at a time.

**Implementation.**

1. **Raycasting on click.** Existing canvas mousedown handler is already split between camera-lock and TransformControls drag. Add: in Cluster mode, if camera is locked AND the click did NOT hit a TransformControls handle, raycast against all `pieceGroup`s and select the closest hit.
2. **Selected piece state.** Module-level `selectedPiece = null` (or piece id string). On selection change: detach TransformControls from previous piece (if any); attach to new piece; refresh transform sliders to reflect new piece's pose.
3. **Visual indicator.** Outline the selected piece. Simple approach: render a slightly-scaled-up duplicate at lower opacity (~0.3) in a contrasting color (e.g., cyan). Or use a simple `THREE.LineSegments` wireframe overlay. Pick the cheaper approach.
4. **Click empty space deselects.** Set `selectedPiece = null`, hide transform UI.
5. **Multi-piece scene with one selected.** Other pieces stay rendered with their own transforms; they're just not currently editable.

### Task 3 — Selected piece's transform UI

**Goal.** When a piece is selected, the same Transform panel from PR B appears, bound to the selected piece. Editing sliders moves the selected piece only.

**Implementation.**

1. **Reuse PR B's Transform panel.** Same DOM structure, same slider+text-entry pairs.
2. **Bind to selected piece.** Sliders write to `selectedPiece.pieceGroup.position` / `.rotation`. TransformControls is attached to `selectedPiece.pieceGroup`.
3. **On selection change.** Disconnect old bindings, refresh slider values from new piece's current pose, reconnect.
4. **Origin badge.** "Rotates around: <auto-detected origin> (piece <id>)". Updates with selection.
5. **Frame badge.** "Frame: cluster (<cluster name>)". Same value for every piece in the cluster (they share frame).
6. **Hidden when no piece selected.** Empty selection state; banner suggests "Click a piece to select it".

### Task 4 — Click-to-pin distance readouts

**Goal.** Click two connection points (attach-point or marks-layer landing) on different pieces to create a live distance measurement. Multiple measurements can coexist.

**Implementation.**

1. **Mode toggle for measurement.** Add a "Measure" toggle button in the Cluster-mode top bar. When active, click handler is in measurement mode (different from selection mode).
2. **First click.** Raycast against all attach-points and landings rendered as small spheres on each piece (you'll need to render those — see Task 5). Capture `{ pieceId, pointId, worldPos: <getWorldPosition of the marker mesh> }`.
3. **Second click.** Same raycast. Capture second point.
4. **Pin a measurement.** Add a `Measurement = { fromPieceId, fromPointId, toPieceId, toPointId, label }` to a `measurements: []` list. Render: a thin line between the two points (live-updated each frame); a text sprite at the midpoint showing the current distance in mm.
5. **Live update.** In the render loop, for each measurement, look up the current world positions of the two points (transforms move with their parent pieceGroups), recompute distance, update the line + label.
6. **Display readouts in the side panel.** A "Measurements" panel listing each measurement: "065:tab-c → 066:landing-c65: 12.4mm" with a remove button.
7. **Auto-suggest pairings.** If the user clicks a connection point that has a known partner in `connection-graph.json` cross-piece edges, banner-suggest the partner: "tab-c on 065 partners with landing-c65 on 066 — click that one next?". Helpful but not enforced.
8. **Toggle off measurement mode.** Click handler returns to selection mode.

### Task 5 — Render attach-points and landings as small spheres

**Goal.** In Cluster mode, each piece's attach-points and marks-layer landings are rendered as small (~1mm radius) colored spheres at their authored centroid. These are the click targets for measurements (Task 4) and provide visual feedback for cross-piece pairing.

**Implementation.**

1. **Iterate `parsed.panelsFirst.attachPoints`.** Each gets a small `THREE.Mesh` (`SphereGeometry(0.5, 8, 8)` — 1mm diameter) at its centroid in piece-local coords. Color: red for `attach`, blue for `landing` (per existing connection-graph kind taxonomy).
2. **Marks-layer landings.** Iterate parsed marks for ids matching `landing-<...>`. Add a sphere there too. Color: blue.
3. **Pivot-anchor.** Render as a yellow sphere (~2mm). Already the rotation pivot; the visual cue helps user orient.
4. **Add to `pieceGroup`.** Spheres are children of `pieceGroup`, so they move with the piece.
5. **Bench mode.** Optionally render the spheres in Bench mode too (helpful for visualizing connection geometry on a single piece). Hidden by default; a small "Show connection points" toggle in the side panel.

### Task 6 — Per-piece save in cluster context

**Goal.** "Save selected piece" button writes back to the selected piece's `work/pieces/NNN/NNN.json` with the new transform. Modal/copy/download flow same as Bench mode.

**Implementation.**

1. **Reuse the existing save modal logic from PR B.** When "Save selected piece" clicks, capture `selectedPiece.pieceGroup`'s current pose, build the same `assembled.transform` block, emit JSON snippet labeled "for piece NNN".
2. **Folds opt-in.** In Cluster mode, the user usually isn't editing folds (they're set in Bench mode). The save modal includes both `folds` and `transform` if either differs from sidecar; user can edit out the folds block by hand if they only want to update the transform. (Default behavior: include both.)
3. **No multi-piece save.** Each save is scoped to one piece. If the user wants to save multiple pieces' updates after rearranging, they save each piece individually. (A future "Save all touched pieces" button could batch this; not in PR C scope.)

### Task 7 — Backward-compat for old scene mode entry points

**Goal.** The PR #17 multi-piece scene mode (loaded via comma-separated piece ids in the URL or input) still works. It's now an implicit Cluster-mode invocation: piece ids → look up which cluster they belong to → load that cluster.

**Implementation.**

1. **URL param or comma-input handler.** When the existing scene-mode parser sees comma-separated ids (e.g., `?piece=065,066,067,068,069`), check if all ids belong to the same cluster. If yes, switch to Cluster mode and load that cluster. If no, banner-warn ("Pieces span multiple clusters; defaulting to ad-hoc scene") and load via the legacy ad-hoc path (each piece loaded independently in cluster-mode-but-no-cluster-frame state).
2. **Ad-hoc cluster fallback.** Pieces loaded ad-hoc with no shared cluster get `frame: world` for their default; transforms are interpreted in world space directly.

## Verification Checklist

1. **Cluster load works.** In Cluster mode, type `anchor` and click Load. All 5 anchor-cluster pieces (065/066/067/068/069) appear in the scene at their saved positions. Banner: "Cluster `anchor` loaded — 5 pieces."
2. **Per-piece selection.** Click piece 067. Cyan outline appears around it. Transform panel shows 067's pose. Click piece 069. Outline moves; transform panel re-binds.
3. **Move selected piece.** Drag the TransformControls translate-X arrow on selected 069. Only 069 moves; 067 etc. stay put.
4. **Slider drives selected piece.** Type 30 in 069's tx number input. 069 translates. 067 unchanged.
5. **Distance readout.** Toggle Measure on. Click `tab-c` sphere on 065. Click `landing-c65` sphere on 066. A line appears between them; a label shows the current distance in mm. Move 066 — distance updates live.
6. **Multiple measurements.** Pin a second measurement. Both render simultaneously.
7. **Save selected piece.** Move 069 to a non-default pose. Click Save selected piece. Modal shows JSON for 069 only with the new transform. Download or copy works.
8. **Backward-compat.** Load via URL `?piece=065,066,067,068,069`. Cluster mode auto-engages with `anchor`.
9. **Mode toggle still works.** Switch back to Bench mode. Single-piece flow resumes; cluster session is cleared from the scene.
10. **No regressions.** Bench mode (PR B), PR A interaction patterns, cutouts, sliders, camera, axes, all unchanged.

## What NOT to Change

- Sidecar shape from DECISIONS #13 — `assembled.transform` is per-piece in cluster-local frame; no inter-piece transforms in this PR (still M4 / Wall mode territory).
- Bench mode behavior from PR B — Cluster mode is additive.
- Wall mode — still deferred. No wall+hook geometry, no `work/assemblies/` files yet.
- Auto-snap from attach-points to landings — still manual placement only.

## Manual tests (Alan runs after merge)

- After PR B has captured Bench-mode poses for the anchor cluster (065-069), load Cluster mode → `anchor`. Confirm pieces sit in approximately the right relative positions.
- Pin distance measurements between every (tab, landing) pair authored in the SVGs (e.g., `tab-b` on 065 ↔ `landing-b65` on 066). Confirm reads update live.
- Manually adjust 067's transform until visual alignment with 069 is right (anchor + bearing box meet correctly). Click Save selected piece. Hand-merge JSON. Reload cluster. Confirm 067's new pose persists.
- Repeat for the rest of the anchor cluster, iterating until all distances are at zero (or close — depends on tab-into-landing insertion depth).
