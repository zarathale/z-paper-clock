---
status: shipped
started: 2026-05-09
shipped: 2026-05-09
owner: Zarathale (Alan)
target: preview-html-bench-transform
unblocked_by: _archive/code-prompts/CODE_PROMPT_preview-html-bench-cluster-foundation.md (PR A shipped 2026-05-10)
---

# CODE_PROMPT — preview.html Bench mode transform capture (PR B of three)

_Shipped 2026-05-09; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md / claude-work/STATUS.md for current state._

## What You Are Doing and Why

Second of three PRs landing `claude-work/DECISIONS.md` #13. PR A (foundational interaction + cutouts) is your dependency — the slider+text-entry pattern, camera lock/toggle, click-drag-on-piece via TransformControls, RGB axes, worktable backdrop, and Bench/Cluster mode toggle scaffold are all assumed to be in place before PR B begins.

PR B adds the **per-piece transform capture loop** for Bench mode:

1. **Per-piece transform UI** — six sliders (3 translation in mm, 3 rotation in degrees), each with the slider+text-entry pattern from PR A. Plus an origin badge showing which point the rotation pivots about.
2. **Auto-detect origin.** When a piece loads, scan for `pivot-anchor` mark > `axles[0]` line > centroid. Display the chosen origin and use it as TransformControls' rotation pivot.
3. **Sidecar `assembled.transform` read.** Extend the existing `maybeLoadSidecar` to also read `assembled.transform`. On piece load, apply the saved transform to the `pieceGroup` (introduced in PR A Task 4).
4. **Sidecar `assembled.transform` write.** Extend the "Save assembled pose" button to emit BOTH `assembled.folds` AND `assembled.transform` in the JSON snippet. Folds-only saves still work (the `transform` block is omitted if pose is identity).
5. **TransformControls drag ⟷ slider sync.** Dragging the gizmo updates the transform sliders + number inputs. Editing the sliders updates the gizmo and piece pose. Bidirectional.
6. **Pose capture for the pendulum cluster resumes here** — once PR B ships, the original session-opening ask (capture per-piece assembled poses for 071/070/098/095/094/069/068/066/099) becomes executable.

PR B does NOT touch multi-piece scene assembly or Cluster mode functionality (still stubbed). Wall mode is still deferred.

## Prerequisites — confirm before starting

- PR A has shipped and merged to `main`. preview.html has: cutouts as Shape holes, slider+text-entry helper (`createSliderRow`), camera-lock-with-toggle, TransformControls attached to a `pieceGroup` wrapping the piece's root mesh, RGB axes (origin + corner gizmo), worktable backdrop, Bench/Cluster mode toggle scaffold (Bench functional).
- DECISIONS #13 is closed and readable.
- DECISIONS #11 (`assembled.folds` shape) is closed and shipped (PR #19) — your `transform` block sits parallel to `folds` in the same `assembled` object.
- `claude-work/state/connection-graph.json` exists and contains `pivot_clusters`. Used to auto-detect whether a piece's transform `frame` defaults to `cluster` or `world`.

## Read These Files First

1. `claude-work/DECISIONS.md` #13 — the sidecar `assembled.transform` shape (translation, rotation_deg, rotation_order, frame, origin); auto-detect rules; per-mode coordinate frame.
2. `claude-work/DECISIONS.md` #11 — `assembled.folds` shape and "Save assembled pose" precedence/UX. Your transform-capture extension MUST preserve the existing folds save semantics.
3. `preview.html` — specifically the new Bench-mode infrastructure from PR A: `pieceGroup`, `transformControls`, `createSliderRow`, the camera lock/toggle, the worktable, the AxesHelper at world origin.
4. `preview.html` `maybeLoadSidecar` — the existing function that reads sidecar JSON for `assembled.folds`. You'll extend it to also read `assembled.transform`.
5. `preview.html` `showAssembledPoseModal` + the save-button handler — extends here to emit both `folds` and `transform`.
6. `claude-work/state/connection-graph.json` — `pivot_clusters` array. Used to look up which cluster a piece belongs to.

## Target File Structure Changes

```
preview.html                                           ← all preview-side changes
work/pieces/071/071.json                               ← (created by Alan, post-merge) — first sidecar with transform block
```

PR B itself produces no new repo files. Sidecar files for individual pieces are created by Alan post-merge as he uses Bench mode to capture poses.

## Numbered Tasks

### Task 1 — Compute and surface piece's natural origin

**Goal.** When a piece loads, determine its rotation origin per DECISIONS #13: `pivot-anchor` mark (in `<g id="attach-points">`) > first axle line (in `<g id="axles">`) > authored 2D centroid of silhouette. Store the origin as a 3D point in piece-local coordinates and the chosen kind as a string.

**Implementation.**

1. Add `computePieceOrigin(parsed)` returning `{ point: [x, y, z], kind: 'pivot-anchor' | 'axles[0]' | 'centroid' }`.
2. **`pivot-anchor` lookup.** Iterate parsed attach-points; if any has id `pivot-anchor`, return its centroid as the origin. (PR A's parsing of `attach-points` already produced `parsed.panelsFirst.attachPoints` — reuse that.)
3. **`axles[0]` lookup.** Else, iterate `<g id="axles">` for the first ellipse/circle/line. Return its centroid (for a line, the midpoint).
4. **Centroid fallback.** Else, compute the centroid of the silhouette polygon (existing util may already exist; if not, sum vertex coords / count).
5. **Z coordinate.** All three origins are in the piece's authored 2D plane (Z = 0 in piece-local space). The slab's extrusion is symmetric ±T/2, so the rotation pivot at Z = 0 sits midway through the slab thickness — natural choice.
6. **Surface on parsed.** `parsed.origin = { point, kind }`.

### Task 2 — Auto-detect cluster membership and default frame

**Goal.** When a piece loads, look up whether it belongs to a `pivot_clusters` entry in `connection-graph.json`. If yes, default `frame: cluster`; if no, default `frame: world`.

**Implementation.**

1. **Fetch connection-graph.json on first need.** Cache the result. Path is `claude-work/state/connection-graph.json` relative to repo root. If fetch fails, banner-warn ("Could not load cluster registry; transforms default to world frame") and proceed with `frame: world` for everything.
2. **Lookup helper.** `findPieceCluster(pieceId, graph) → string | null`. Iterates `graph.pivot_clusters`, returns the cluster name if `pieceId` is in any cluster's `pieces` array. Else null.
3. **Surface on parsed.** `parsed.cluster = clusterName || null`. Default frame: `parsed.cluster ? 'cluster' : 'world'`.

### Task 3 — Per-piece transform sliders + UI

**Goal.** A "Transform" panel appears in the side panel below the existing fold-sliders panel. Six sliders (3 translation, 3 rotation) using `createSliderRow` from PR A. Plus an origin badge.

**Implementation.**

1. **Panel structure.** New `<div id="transform-panel">` in the side panel. Heading: "Transform". Below the heading: an origin badge (small text: "Rotates around: pivot-anchor" / "axles[0]" / "centroid"). Below that: 6 slider rows.
2. **Translation rows.** Three sliders: tx (X mm), ty (Y mm), tz (Z mm). Range: -200 to +200 mm, step 0.1. Default 0.
3. **Rotation rows.** Three sliders: rx, ry, rz (degrees). Range: -180 to +180, step 0.1. Default 0. Snap to 15° on Shift (UI nicety; same convention as PR A's TransformControls Shift snap).
4. **Frame indicator.** A read-only badge below the sliders: "Frame: cluster (anchor)" or "Frame: world". Auto-detected per Task 2.
5. **Bidirectional binding.** Slider/text-input changes apply to `pieceGroup.position` and `pieceGroup.rotation` (the wrapping group from PR A). Use `THREE.Euler` with `XYZ` rotation order.
6. **TransformControls drag updates the sliders.** TransformControls fires `change` events. Read `pieceGroup.position` and `pieceGroup.rotation`, push the values to the slider/number inputs. Throttle to ~60fps via requestAnimationFrame; don't fire `onChange` recursively.
7. **Cluster mode panel hidden.** When mode toggles to Cluster, hide the Transform panel (Cluster mode handles per-piece selection separately in PR C).

### Task 4 — Apply origin offset to TransformControls

**Goal.** TransformControls' rotate handles should pivot around the piece's natural origin (Task 1), not the piece's geometric center.

**Implementation.**

1. **Wrap the slab inside `pieceGroup`.** The slab's mesh is positioned at `-origin.point` inside `pieceGroup`, so that `pieceGroup`'s local origin sits at the piece's natural origin. TransformControls is already attached to `pieceGroup` (PR A Task 4); rotation now pivots about the natural origin.
2. **Validate against pivot-anchor pieces.** Load piece 069 (has `pivot-anchor` in attach-points). Confirm rotation handles emanate from the pivot-anchor centroid, not the piece centroid.
3. **Validate against axle pieces.** Load piece 100 (has axles but no pivot-anchor). Confirm rotation handles emanate from the axle centroid.
4. **Validate against neither.** Load piece 071 (no pivot, no axles). Confirm rotation handles emanate from the silhouette centroid.

### Task 5 — Sidecar `assembled.transform` read on load

**Goal.** When a piece loads, if its sidecar contains `assembled.transform`, apply it to `pieceGroup` immediately.

**Implementation.**

1. **Extend `maybeLoadSidecar`.** It currently sets `currentAssembledFolds` from `assembled.folds`. Add: if `assembled.transform` exists, store it as `currentAssembledTransform = json.assembled.transform`.
2. **Apply on render.** After the piece is loaded and the panels-first scene is built (the place where assembled.folds is currently applied to fold sliders), apply the transform to `pieceGroup`:
   - `pieceGroup.position.set(...transform.translation)`
   - `pieceGroup.rotation.set(...transform.rotation_deg.map(d => d * Math.PI / 180), transform.rotation_order || 'XYZ')`
3. **Origin field validates.** If sidecar's `transform.origin` does NOT match the auto-detected origin (Task 1), banner-warn but apply the transform anyway. (User may have authored the sidecar with a different origin choice; honor it.)
4. **Frame field is informational only in Bench mode.** Bench mode renders the piece around its own origin regardless of frame; the frame field tells Cluster mode (PR C) and Wall mode (PR D) how to interpret the transform. Bench just applies it as-is.
5. **Console log.** Mirror the existing `assembled.folds applied` log: `[panels-first] assembled.transform applied: translation=[...], rotation_deg=[...], frame=cluster, origin=pivot-anchor`.

### Task 6 — Save extension: emit `transform` alongside `folds`

**Goal.** The "Save assembled pose" modal now contains both `folds` and `transform` blocks. If the piece's transform is identity (default), omit the `transform` block (keep the diff small). Same idea for folds (existing PR #19 behavior).

**Implementation.**

1. **Read pose state at save time.** Capture `pieceGroup.position` and `pieceGroup.rotation`. Convert rotation to degrees (XYZ order). Compare to identity (all zeros within ε = 0.01).
2. **Build payload.** If pose is non-identity:
   ```js
   payload.assembled.transform = {
     translation: [round2(x), round2(y), round2(z)],
     rotation_deg: [round2(rx), round2(ry), round2(rz)],
     rotation_order: 'XYZ',
     frame: parsed.cluster ? 'cluster' : 'world',
     origin: parsed.origin.kind
   };
   ```
   Where `round2` is the existing rounding helper (or `Math.round(v * 100) / 100`).
3. **Modal display unchanged.** The existing modal renders `JSON.stringify(payload, null, 2)`; the new block displays naturally.
4. **Note field.** The user may have typed in the existing `note` field; preserve that.
5. **Captured timestamp.** Reuse the existing `captured: new Date().toISOString()`.

### Task 7 — Frame-aware tweaks for cluster lookup

**Goal.** When Bench mode's auto-detected frame is `cluster`, the badge displays which cluster ("Frame: cluster (anchor)"). When `world`, it displays "Frame: world".

**Implementation.**

1. **Badge renders from `parsed.cluster`.** Already surfaced in Task 2.
2. **No behavioral difference in Bench mode** — the piece is rendered in its own local frame regardless. Frame is informational, baked into the saved sidecar so Cluster mode (PR C) and Wall mode (PR D) interpret it correctly.

## Verification Checklist

1. **Origin detection works.** Load 069 (pivot-anchor). Origin badge shows "Rotates around: pivot-anchor". Load 100 (axles, no pivot). Badge shows "axles[0]". Load 071 (neither). Badge shows "centroid".
2. **Transform sliders functional.** Drag tx slider to 50. Piece translates 50mm in +X. Type 30 in the rx number input. Piece rotates 30° about its origin's X axis. Edit the slider directly and confirm the number input mirrors it.
3. **TransformControls ↔ sliders synced.** Drag the TransformControls translate-X arrow. The tx slider/number both update live. Drag a rotate ring. The corresponding rotation slider updates live.
4. **Sidecar transform reads on load.** Manually create `work/pieces/071/071.json` with `{"assembled":{"transform":{"translation":[10,20,5],"rotation_deg":[15,30,45],"rotation_order":"XYZ","frame":"cluster","origin":"centroid"}}}`. Reload the piece. Confirm the piece appears already-translated and -rotated; sliders show the loaded values; console logs `[panels-first] assembled.transform applied: ...`.
5. **Sidecar transform writes on save.** Move 071 to a non-identity pose via sliders. Click Save assembled pose. Confirm the modal JSON contains an `assembled.transform` block with the expected values, frame `cluster` (since 071 is in the anchor cluster — verify via connection-graph.json), origin `centroid`, plus rounded translation/rotation values.
6. **Identity pose omits transform block.** Reset all transform sliders to 0. Click Save. Confirm the modal JSON has `assembled.folds` only (or empty assembled object if folds are also default), no `transform` block.
7. **Folds save semantics preserved.** PR #19 behavior unchanged: only folds whose slider value has moved off the precedence default are emitted.
8. **Frame badge correct.** 071 is in `pivot_clusters` (anchor cluster). Badge: "Frame: cluster (anchor)". A loose piece (e.g., a hypothetical piece not in any cluster — pick one from `pieces.csv` that's not in the connection graph) shows "Frame: world".
9. **Frame mismatch warning.** Hand-edit 071's sidecar to set `transform.origin: 'pivot-anchor'` (which 071 doesn't have). Reload. Banner warns about origin mismatch but transform still applies.
10. **No regression on PR A.** Cutouts still render, sliders still have text-entry, camera-lock-toggle still works, RGB axes + corner gizmo still visible, worktable backdrop intact, mode toggle scaffold unchanged.

## What NOT to Change

- `assembled.folds` shape, save semantics, precedence — preserved exactly.
- Cluster mode (still stubbed, banner unchanged).
- Multi-piece scene assembly — leave as-is from PR #17. PR C will rework that path under Cluster mode.
- TransformControls drag-to-OrbitControls disable handshake — already implemented in PR A.
- Origin-auto-detect for pieces without `pivot_clusters` lookup data (graceful fallback to `frame: world`).
- Connection-graph.json shape — read-only consumer.

## Manual tests (Alan runs after merge)

- Capture pendulum cluster pose: load 071. Set folds (3× 90°). Set transform to put it where the pendulum-rod ring sits in the assembled clock (relative to the anchor cluster pivot). Click Save. Hand-merge JSON into `work/pieces/071/071.json`. Reload — piece comes up already-folded AND already-positioned.
- Repeat for 070, 098, 095, 094, 069, 068, 066, 099.
- Sanity check: open `work/pieces/071/071.json` after saving and confirm the JSON is well-formed and matches DECISIONS #13 schema.
