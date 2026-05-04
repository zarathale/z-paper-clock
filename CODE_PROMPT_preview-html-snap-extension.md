---
status: ready-for-code
started: 2026-05-04
owner: Zarathale (Alan)
target: preview-html-snap-extension
---

## What You Are Doing and Why

Replace `extendFoldsToSilhouette`'s "always extend to nearest silhouette boundary" behavior with **snap-only extension**: each authored endpoint extends to the nearest silhouette intersection along the fold line *only if* that intersection is within `SNAP_TOL = 0.005 × diagLen` of the authored endpoint. Otherwise the endpoint stays at-authored.

This is the follow-up to `CODE_PROMPT_preview-html-cut-trim.md` (shipped 2026-05-04 21:03). Cut-trim correctly switched the cut step from infinite-line half-plane cuts to bounded segment cuts, and is strictly better on every piece in the test bench. But on piece 066 it left 13 unreachable regions, 10 missing fold chords, and a strip that still folds into shards. Root cause documented in `sessions/2026-05-04-2103_code_preview-html-cut-trim.md`: the cut step uses `fold.start`/`fold.end` (the existing silhouette-extended endpoints) rather than `fold.authoredStart`/`fold.authoredEnd`, because Alan typically draws a few units shy of the silhouette and a literal-authored cut returns zero crossings on those folds. The "extend to nearest boundary" workaround handles small authoring gaps but over-extends on folds whose authored endpoints are deep interior — `fold-tab-c` on 066 is a short tab fold whose nearest line-aligned silhouette intersection is ~12,000 units away at the strip top, so its extended chord cuts the whole column lengthwise and wipes out 10 other folds' chords on subsequent passes.

Snap-only fixes this. Folds with authored endpoints near the silhouette (Alan's normal case, ~6–14 units shy) snap to boundary and produce normal cuts. Folds with genuinely interior authored endpoints (tab folds, folds that meet other folds) keep their authored coordinates and produce small-extent cuts that don't over-reach. The closure-constraint design conversation (parked) is still the right long-term answer for cylinder topology, but it's a separate problem from cut over-reach.

## Prerequisites — confirm before starting

- `preview.html` exists at repo root and runs cleanly via `localhost:8000/preview.html?piece=NNN` against pieces 001, 066, 069, 070, 071, 072, 067.
- The cut-trim ship is in (`CODE_PROMPT_preview-html-cut-trim.md` is `status: shipped`).
- The face-graph diagnostic harness (Dump button + 2D overlay + console summary) is shipped — `CODE_PROMPT_preview-html-face-graph-diagnostics.md` is `status: shipped`.
- No version bump (preview.html iteration).

## Read These Files First

1. `CLAUDE.md` — top sections + "Marker-bound fold ids" Architectural Decisions row + "Per-element ids inside fold layers" entry in File Naming Conventions. The snap-only change preserves both conventions exactly as documented; no convention changes.
2. `sessions/2026-05-04-2103_code_preview-html-cut-trim.md` — what cut-trim shipped, the deviation from `authoredStart`/`authoredEnd`, and the 066 result with 10 missing chords. The "Future fix direction" section names this prompt.
3. `preview.html` lines 1580–1642 (`extendFoldsToSilhouette`) — the entire function. This is the only function changing. Note especially:
   - Lines 1604–1610: the existing line/silhouette intersection collection. **Kept intact.**
   - Lines 1612–1619: the `before`/`after` filter and `tMin`/`tMax` selection. **Replaced.**
   - Lines 1634–1635: `start`/`end` computation with the `EPS` push. **Replaced** (EPS handling moves into the new `tMinFinal`/`tMaxFinal` formulation).
4. `preview.html` line 1414 (`polyBbox`) — global helper, available to use here.
5. `preview.html` lines 1745–1747 (cut step) — confirms the cut step reads `fold.start`/`fold.end`. No change needed there; the new semantics propagate automatically.

## Target File Structure Changes

```
z-paper-clock/
├── preview.html                                              ← update: snap-only extension in extendFoldsToSilhouette
├── CODE_PROMPT_preview-html-snap-extension.md                ← update: status flips to shipped on PR open
└── sessions/
    └── 2026-05-04-HHMM_code_preview-html-snap-extension.md   ← NEW: ship session note
```

No SVGs touched. No convention docs touched.

## Numbered Tasks

### 1. Compute `diagLen` and `SNAP_TOL` at the top of `extendFoldsToSilhouette`

Insert at the top of the function body, after `const n = silhouette.length;` (line 1582):

```js
const bb = polyBbox(silhouette);
const diagLen = Math.hypot(bb.maxX - bb.minX, bb.maxY - bb.minY);
const SNAP_TOL = 0.005 * diagLen;
```

`polyBbox` is the global helper at line 1414. No new helper needed.

### 2. Replace the `tMin`/`tMax` selection with snap-only logic

In the `folds.map(fold => { ... })` callback (lines ~1594–1640), replace the existing `before`/`after`/`tMin`/`tMax` block (lines 1612–1619) with the snap-only version:

```js
// Snap-only extension: extend to nearest silhouette boundary intersection ONLY
// when the authored endpoint is within SNAP_TOL of that intersection. Otherwise
// use the authored coordinates exactly. This handles Alan's small authoring
// imprecision (typically 6–14 viewBox units shy of boundary) without
// over-extending folds whose authored endpoints are genuinely interior.
const before = ts.filter(t => t <= 0 + 1e-6);
const after  = ts.filter(t => t >= len - 1e-6);
const tMinCandidate = before.length > 0 ? Math.max(...before) : null;  // ≤ 0
const tMaxCandidate = after.length  > 0 ? Math.min(...after)  : null;  // ≥ len

const tMinFinal = (tMinCandidate !== null && Math.abs(tMinCandidate) < SNAP_TOL)
  ? tMinCandidate - EPS  // snap to boundary, push EPS past
  : 0;                    // no snap — use authored start exactly
const tMaxFinal = (tMaxCandidate !== null && Math.abs(tMaxCandidate - len) < SNAP_TOL)
  ? tMaxCandidate + EPS  // snap to boundary, push EPS past
  : len;                  // no snap — use authored end exactly
```

### 3. Update the `start`/`end` computation in the returned fold object

Replace lines 1634–1635:

```js
start: [sx + (tMin - EPS) * ux, sy + (tMin - EPS) * uy],
end:   [sx + (tMax + EPS) * ux, sy + (tMax + EPS) * uy],
```

with:

```js
start: [sx + tMinFinal * ux, sy + tMinFinal * uy],
end:   [sx + tMaxFinal * ux, sy + tMaxFinal * uy],
```

`EPS` is now folded into the snap branch only; the no-snap branch yields exact authored coordinates.

### 4. Update the function's leading comment

The current function header (or the inline comment at lines 1612–1613) describes "extend to NEAREST silhouette boundary in each direction." Update to reflect the new semantics:

```js
// Snap-only: each authored endpoint extends to the nearest silhouette boundary
// intersection along the fold line ONLY when within SNAP_TOL = 0.005 * diagLen
// of the authored endpoint. Otherwise the authored coordinate is used exactly.
// This handles small authoring imprecision (typically a few viewBox units
// shy of the silhouette boundary) without over-extending folds whose authored
// endpoints are interior — e.g., short tab folds on long strips, or folds
// that meet other folds at internal vertices. Settled 2026-05-04 in
// CODE_PROMPT_preview-html-snap-extension.md.
```

### 5. (No other code changes.)

The cut step (line 1746–1747), `computeEdgeTagsForCut` (lines 1697–1698), the sliver-detection step (line 1808), and the foldEdges shared-edge match (lines 1935–1936) all read `fold.start`/`fold.end` and `fold.authoredStart`/`fold.authoredEnd` and inherit the new semantics automatically. No edits there.

The diagnostic overlay (lines 2945, 2947) uses `fold.authoredStart`/`fold.authoredEnd`, which are unchanged. No edits there either.

The dead `bigBox` / `halfPlanePoly` / `toRing` / `toPCPoly` / `fromRing` / `edgeMidpoint` / `ADJ_EPS` cleanup noted in the cut-trim session note's open question #3 is **explicitly out of scope** for this prompt — keep minimal surface area.

## Verification Checklist

1. **No console errors** when opening `localhost:8000/preview.html?piece=NNN` for each of: 001, 066, 069, 070, 071, 072, 067. Page renders cleanly; thickness/rotation sliders work; orbit/zoom work.

2. **Piece 066 — the smoking gun.** Open `?piece=066`. Expect:
   - Console summary `regions=` near 21–25 (was 27 after cut-trim, 32 before).
   - Console summary `fold-edges` count at or near 21 (matches authored fold count). Was 20 after cut-trim.
   - **Zero "Region region-XX is unreachable from root — rendered flat" banners**, or at most 1–2. (Was 13 after cut-trim.)
   - **Zero "Fold ... no cut chord found in face graph" banners**, or at most 1. (Was 10 after cut-trim.)
   - All 17 marker-bound folds resolve to driven hinges in `pathHingeMap`.
   - Fold-all slider folds the strip into a recognizable column with side panels + closure, **no shards**.

3. **Piece 069 — regression check.** Open `?piece=069`. Expect:
   - Same fold count, region count, and fold-edge count as before (or one less in any). Folding behavior visually unchanged.
   - All 11 markers still resolve in `markerToRegionId`.

4. **Pieces 001, 070, 071, 072, 067 — regression checks.** Open each. Expect:
   - No new banners, no new console errors.
   - Region counts and topology equivalent to or cleaner than the cut-trim baseline.
   - Existing folding behavior unchanged.

5. **Diagnostic dump** still works on every piece. JSON parses; payload structure unchanged from cut-trim.

6. **Diagnostic overlay** still works on every piece. The "fold authored segments" rendering uses `authoredStart`/`authoredEnd` and is visually unchanged. The "extended fold line" rendering (if present in the overlay) is now visibly shorter on folds whose authored endpoints are interior — that's expected.

7. **Console summary** prints the same keys as after cut-trim: `[face-graph] piece=... regions=... folds=... fold-edges=... shared-edges=... slivers-filtered=...`.

## What NOT to Change

- **The cut step** (line 1745–1822). It reads `fold.start`/`fold.end` and inherits the new semantics for free. Leave it.
- **`computeEdgeTagsForCut`** (lines 1693–1722, approximate). Same — it reads `fold.start`/`fold.end`.
- **The shared-edge index** (lines ~1830–1870, approximate) and **fold-edges-from-shared-edges** logic (Task 3 of cut-trim, lines ~1925–1965). Both inherit automatically.
- **The single-pass BFS** (Task 5 of cut-trim). Untouched.
- **`markerToRegionId` and per-region `markerIds`** (Task 6 of cut-trim). Untouched.
- **The diagnostic overlay** (lines ~2940–2960). Renders `authoredStart`/`authoredEnd`; unchanged.
- **Convention docs.** No CLAUDE.md / LAYER-CONVENTIONS.md / SPEC changes from this prompt. The snap-only change is implementation, not convention.
- **Dead code cleanup.** `bigBox`, `halfPlanePoly`, `toRing`/`toPCPoly`/`fromRing`, `edgeMidpoint`, `ADJ_EPS` — out of scope. Keep them.
- **Closure constraint.** Still parked.

## Manual tests

After merge, Alan runs `localhost:8000/preview.html` and works through the test bench:

| Piece | Action | What to look for |
|---|---|---|
| 066 | Load via `?piece=066`. Click Fold-all slider to 100% / Assembled. | The strip folds into a column with side panels visible. **No shards.** No unreachable-region banners. No no-cut-chord banners. **The point of this prompt.** |
| 069 | Load. Toggle overlay. Move sliders. | Visually unchanged from post-cut-trim. |
| 071 | Load. | Cutouts still render. Folds work. Landings resolve. |
| 001 | Load. Toggle overlay. | Long strip renders. Auto-renamed fold cluster behavior unchanged (different problem). |
| 072 | Load. | Pure flat shape, no warnings. |
| 067 | Load. | All 4 landings resolve in `markerToRegionId`. |
| 070 | Load. | Existing rendering unchanged. No new errors. |

Goal: confirm 066 is now visually correct, 069 is unchanged, no regressions on the rest. Post a summary back in cowork. Next session reads it and decides whether to pick up the convention-cleanup pass (001 auto-rename + 065/069 bare-form landings + 070 silhouette wrapper + `mark-<letter>` formal recognition) or to start on the closure constraint design.
