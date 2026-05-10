---
date: 2026-05-09
start_time: "22:19"
end_time: "22:19"
mode: code
participant: Zarathale (Alan)
target: preview-html-bench-transform
orchestration_prompt: CODE_PROMPT_preview-html-bench-transform.md
---

## Goal

Land PR B of three for DECISIONS #13: per-piece transform capture loop in `preview.html` Bench mode.

## What was done

Implemented all 7 tasks from the orchestration prompt:

1. **`computePieceOrigin`** — precedence `pivot-anchor` mark > `axles[0]` > centroid (panels-first union bbox; viewBox center fallback). Returns `{vbX, vbY, kind}`.
2. **`findPieceCluster`** — iterates `connectionGraph.graph.pivot_clusters` `{name: [ids]}` and returns the cluster name or null. Reuses the existing `connectionGraph` cache.
3. **Transform panel UI** — new `<div id="transform-panel">` between fold-controls and thickness-section. Heading + origin badge ("Rotates around: …") + frame badge ("Frame: …") + 6 sliders (X/Y/Z mm, rX/rY/rZ deg) using `createSliderRow` (slider + paired number input) + a "Reset transform" button.
4. **Origin offset** — `wrapForTransform` now creates an inner group inside `pieceGroup`, holds the slab pivot + axle wires, and offsets it by `-currentPieceOrigin3js` so `pieceGroup`'s local (0,0,0) IS the natural origin. TransformControls' rotate handles emanate from there.
5. **Sidecar `assembled.transform` read** — `maybeLoadSidecar` now also stores `currentAssembledTransform`. `applyAssembledTransformIfAny()` runs inside `wrapForTransform` to apply translation + Euler rotation to `pieceGroup`. Origin-mismatch produces a warning banner but the transform applies anyway. Console line `[panels-first] assembled.transform applied: …` mirrors the existing folds line.
6. **Sidecar `assembled.transform` write** — save handler now appends a `transform` block (rounded to 2dp) when the pose is non-identity (any of 6 values |·|>0.01). Identity pose omits the block. Folds emit semantics unchanged.
7. **Frame-aware badge** — `parsed.cluster` ? "Frame: cluster (anchor)" : "Frame: world".

Bidirectional sync: each transform slider's `input` event writes `pieceGroup.position` + `.rotation`; TransformControls' `change` event reads them back into the sliders via `setSliderValueQuiet` (no event re-fire) on a `requestAnimationFrame` flag to prevent recursion.

Mode integration: `setMode('cluster')` hides the panel; `setMode('bench')` shows it. Scene mode (`loadScene`) clears all per-piece transform context and hides the panel.

### Verification (browser-tested via Claude Preview against the worktree on `localhost:8770`)

| Check | Result |
|---|---|
| 069 → origin badge "pivot-anchor", frame "cluster (anchor)", inner offset (-0.13, 0) mm | ✅ |
| 065 → origin badge "axles[0]", frame "world", inner offset (3.78, -4.76) mm | ✅ |
| 071 → origin badge "centroid", frame "world", inner offset (0, 0) | ✅ |
| Slider input → `pieceGroup` position+rotation update | ✅ |
| TC `change` → all 6 sliders + paired number inputs update | ✅ |
| Sidecar `transform` read on load (071 with pose 10/20/5 + 15/30/45°) — pieceGroup applied, sliders show values, console logs apply line | ✅ |
| Sidecar save with non-identity pose — modal JSON contains `transform` block with frame=world, origin=centroid, rounded values | ✅ |
| Identity pose save — JSON has folds only, no transform block | ✅ |
| Origin-mismatch warning (sidecar `origin: pivot-anchor` on 071 which has none) — warn banner fires, transform still applies | ✅ |
| Cluster mode hides Transform panel; Bench mode shows it | ✅ |
| Zero console errors across all flows | ✅ |

### Notes vs the prompt

- **Verification step 8 cluster check.** The prompt suggested 071 for the "Frame: cluster (anchor)" case, but `connection-graph.json` `pivot_clusters` only contains `{anchor: ["067", "069"]}` — 071 isn't in any cluster. Tested with **069** instead (also in `anchor`), which surfaces the same code path.
- **Verification step 4 piece 100 origin.** The prompt described 100 as having axles. The committed `100.svg` actually has no axles layer — its panels-first SVG has only `silhouette` + `panels`. Tested the **`axles[0]`** path with **065** instead (axles + attach-points but no `pivot-anchor`).
- **`pivot_clusters` shape clarification.** The prompt described iteration as "any cluster's `pieces` array", but the actual JSON shape is `{clusterName: [pieceId, ...]}` (flat). Implementation iterates `Object.entries(pcs)` and checks `Array.isArray(ids) && ids.includes(pieceId)`.
- **Save UX detail.** The previous "no fold sliders to capture" early-return was relaxed: save now proceeds whenever there are folds OR a non-identity transform (avoids preventing transform-only saves on no-folds pieces).

## Branch / commit

- Branch: `claude/preview-html-bench-transform`
- Commits: TBD (commit + push + PR after this note)

## Open questions

None blocking. Two follow-ups noted but out of PR-B scope:

- **Sidecar `transform` precedence vs slider drag** — currently sidecar applies on every load and the user-typed slider state is overwritten on `R` reload. Right behavior for capture workflow ("the sidecar IS the saved state"); revisit if Alan wants a "don't reload my in-progress pose" mode.
- **Cluster-membership data is sparse.** Only 067/069 are in any cluster today. Authoring more `pivot-anchor` marks across panels-first pieces will widen the cluster surface naturally.

## Next-session handoff

PR B unblocks **PR C** (`CODE_PROMPT_preview-html-cluster-mode.md`, currently `draft` blocked-by PR B). Pose-capture for the pendulum cluster (071/070/098/095/094/069/068/066/099) — the original 2026-05-09 evening session ask — is now executable in Bench mode against the merged PR B.
