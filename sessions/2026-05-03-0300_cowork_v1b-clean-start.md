---
date: 2026-05-03
start_time: "03:00"
end_time: "03:55"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Author a clean-start `CODE_PROMPT_preview-html-v1b.md` against the actual current state of `preview.html` (post-v1a + cut-layer + texture-flip + back-face-mirror + perf + thickness-fix + axle-rotation) and `work/SPEC-REGIONS.md`. Continuation of the immediately-prior session that archived the earlier draft (`sessions/2026-05-03-0200_cowork_v1b-archive.md`).

## What Was Done

### Recon

Read the current `preview.html` (~1362 lines) for real signatures and globals:

- Globals: `currentSlabPivot` (single rotation pivot wrapping the slab), `currentAxleWires` (world-anchored, outside pivot), `parsed`, `MM_PER_UNIT`, `VB`, render-on-demand `needsRender` + `requestRender()`.
- `parseSVG` returns the documented `parsed` shape (filename, viewBox, scanPng, scanWidth, scanHeight, imageScale, folds, axles, north, rootCentroid, thicknessMm/Default/Source, _svgText).
- `extractSilhouette(p)` is the async Tier-1/2/3 dispatcher (line 754); v1b consumes its return polygon as input to the face graph.
- `renderScene(p)` (line 1049) handles teardown, silhouette extract (cached on `p._polygon`), `buildSlab`, pivot wrap at active-axle position, axle wires, optional north sphere, camera frame, diagnostics. v1b restructures the slab/wrap/north section but preserves teardown + axle-wires loop + camera + diagnostics.
- `buildSlab(polygon, thicknessMm)` returns a `THREE.Group` of front + back + side meshes; v1b calls it once per region, unmodified.
- Thickness rebuild is `debouncedRebuild` (80ms); rotation slider writes only `currentSlabPivot.rotation.z`.

Verified test SVGs:

- `inbox/069.svg` exists with `<g id="silhouette">` + `<g id="folds-valley">` (8) + `<g id="axles">` (1 ellipse). No mountains, no root marker.
- `inbox/066.svg` exists with `<g id="folds-valley">` (20) + `<g id="folds-mountain">` (2) + `<g id="axles">` (no ellipses; banner at load). No silhouette layer, no root marker.

Both fall back to "largest area = root + banner" per the SPEC fallback. Matches the prior draft's expected counts (069 → 13 regions, 066 → 22 regions).

### Decisions surfaced + settled

Three scope-blocking calls confirmed via AskUserQuestion mid-session:

- **Test piece coverage:** 069 + 066 only (recommended). Adds neither 067 (cutaway-id) nor a synthetic no-folds SVG to the automated checklist; the synthetic-no-folds case becomes a Manual Test step instead.
- **Polarity in UI:** implicit only (recommended). Per-fold slider's default value (±90° from layer) carries the polarity story; no V/M badge in the row.
- **Rotation pivot composition:** wraps the whole fold tree (settled in the prior archive session). Non-root slabs are descendants of root slab is descendant of `currentSlabPivot`. Existing rotation slider continues to work without modification.

Implicit decisions baked in:

- **Algorithmic framing follows SPEC-REGIONS.md.** Step 1: extend each fold line to silhouette boundary (prevents T-junctions). Step 2: iteratively split via `polygon-clipping` half-plane intersection (`intersection()` of each region with each fold's two half-planes). The SPEC's "subtract" wording is conceptual; the `polygon-clipping` API is half-plane-shaped; output is the same. Edge-tag propagation by midpoint distance with `ε ≈ 0.5` viewBox units (carried from the archived draft). Sliver filter `Δ = 0.5% of silhouette-bbox diagonal`.
- **Data shape lifts SPEC-REGIONS interfaces** (`Region`, `FoldEdge`, `FaceGraph`) into vanilla JS objects with the same field names, so cross-doc reading stays clean.
- **Axle wires stay world-anchored, outside the pivot, unchanged.** They mark "where the wire enters/exits the original flat layout"; if a non-root panel folds and the active axle happens to be on it, accept the visual disconnect (the fold tree still rotates around the original axle position). The `north` orientation marker DOES move into its containing region's slab (Task 5) so it folds with its panel.

### Authored

`CODE_PROMPT_preview-html-v1b.md` at repo root (status: ready-for-code, depends_on: v1a + the six follow-up passes, supersedes: the archived path). Sections per CLAUDE.md prompt-format spec: front matter, What You Are Doing and Why, Prerequisites, Read These Files First (7 entries), Target File Structure Changes, 8 Numbered Tasks, Verification Checklist (12 items), What NOT to Change, Manual tests (10 steps), Branch / commit / PR (with the canonical `gh pr create` command), End-of-session.

The eight tasks:

1. Populate `<div id="fold-controls">` with global + per-fold sliders; consolidate Reset.
2. `extendFoldsToSilhouette(silhouette, folds)` — extend each fold line to the silhouette boundary in both directions.
3. `buildFaceGraph(silhouette, extendedFolds)` — half-plane split via polygon-clipping, edge-tag propagation, sliver filter, adjacency, root selection (with rootCentroid → fallback to largest area), BFS for fold tree.
4. Replace single-slab build with N-region fold tree wired through `currentSlabPivot`. Single-slab fallback path preserved when `parsed.folds.length === 0`.
5. Re-route the optional `north` sphere into its containing region's slab (point-in-polygon).
6. Wire global + per-fold slider input handlers as cheap quaternion updates (no rebuild).
7. Update `debouncedRebuild` for N panels; add a `parsed._faceGraph` cache invalidated on each `loadSVG`.
8. Extend the diagnostic block with face-graph stats (regions, fold edges, root source, per-fold path → hinge-count, sliver count, orphan count, unknown-tag-edge count).

### Downstream doc-sweep

- **`WORKPLAN.md` — preview.html iteration track:** `next_action` rewritten from "author a clean-start v1b…" to "hand `CODE_PROMPT_preview-html-v1b.md` (status: ready-for-code…) to a Code session." Recent log gained an entry for the authoring; the prior archival entry was kept.
- **`WORKPLAN.md` — regions track:** `next_action` updated from "bake SPEC-REGIONS.md into the clean-start v1b prompt (when authored)" to noting that the SPEC is now referenced from the authored prompt and the v1b ship will be the empirical test of the SPEC's algorithm.
- **`ROADMAP.md` — M0.6 row 0.6.9:** task title sharpened (now "face graph (extend folds → split via polygon-clipping) + adjacency BFS + hinge tree + …"); status flipped `not-started` → `ready-for-code`; owner column simplified to Code; Notes column points at the new prompt + this session note.
- **`work/SPEC-REGIONS.md` — Relation-to-other-docs section:** softened pointer flipped back to a hard pointer at the new authored path, with a note that Tasks 2 + 3 lift the SPEC's two-step algorithm and its data-shape interfaces.

### Not touched (deliberate)

- `CLAUDE.md` (status table row "v1b (polygon cut + hinge animation) … pending" remains valid until v1b ships; author the close-out edit then).
- `PROJECT-STATE.md` ("v1b queued" — accurate until ship).
- `work/SPEC-3D-VIEWER.md` ("v1b territory" / "v1b+ concern" — abstract enough; no edits needed).
- The archived prompt at `_archive/code-prompts/CODE_PROMPT_preview-html-v1b.md` (decision record; left alone).
- `share/` directory — already lagging on other doc work (flagged in the prior session note).
- `CODE_PROMPT_preview-html-v1.md` (the unified-then-split prompt; its supersession note still reads correctly as historical record; the question of whether v1 itself wants its own status update remains parked).

## Open Questions

- The new v1b prompt assumes `polygon-clipping@0.15.7` handles the half-plane intersection robustly. Real authored fold lines may produce collinear vertices, zero-area outputs, or the rare self-intersecting result that needs the `martinez-polygon-clipping` swap the prompt mentions. First Code-session ship will tell us.
- Edge-tag matching tolerance `ε = 0.5` viewBox units is carried from the archived draft. The 0.5% sliver-filter delta is also carried. Both numbers are rough; if the first ship surfaces edge cases, recalibrate.
- Per-region thickness rebuild may be slow on real fold counts (13 + 22 panels). If it stutters worse than tolerable, a follow-up prompt should swap the rebuild for an in-place geometry mutation (mutate position attributes; recompute side-strip; reuse the front/back ShapeGeometry — rough sketch).

## Next-Session Handoff

1. (Code) Pick up `CODE_PROMPT_preview-html-v1b.md`. Read the seven prerequisite files in order. Implement the eight tasks. Ship.
2. (Cowork, after v1b ships) Sweep CLAUDE.md status table + PROJECT-STATE.md + WORKPLAN.md for "v1b queued / pending" wording and flip to "v1b shipped." Decide on the parked v1 unified-prompt status question.
3. (Cowork, separately) Pendulum-piece-ID lookup against `embedded-labels.md` §II.C, in service of the pendulum POC track. Independent of v1b ship; can run in parallel.
