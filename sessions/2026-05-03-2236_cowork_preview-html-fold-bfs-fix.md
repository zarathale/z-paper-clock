---
date: 2026-05-03
start_time: "22:00"
end_time: "22:36"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Debug and fix fold animation bugs in `preview.html` for piece 069 — continued from earlier
context window that ran out before the "b tab orphaned" issue was resolved.

## What was done

This session picked up mid-debug from a compacted context. Four bugs had already been fixed
in the prior half of the session:

1. **`ptToSegDist` in `computeEdgeTags`** — changed both fold-check locations from
   `ptToLineDist` (infinite line) to `ptToSegDist` (finite segment). Prevents edge midpoints
   far outside a fold's authored extent from being tagged with that fold.

2. **`extendFoldsToSilhouette` nearest-boundary fix** — swapped `Math.min/max` to
   `Math.max/min` so extensions use the *nearest* silhouette boundary hit in each direction,
   not the farthest. This stopped valley-5 from spanning the full silhouette width through
   the side-arm panels.

3. **`authoredStart`/`authoredEnd` on extended folds** — `extendFoldsToSilhouette` now
   returns the pre-extension authored endpoints alongside the extended `start`/`end`.

4. **Passive fold edges in adjacency step** — fold edges whose overlap midpoint falls outside
   the authored segment range are marked `passive: true`. This preserves BFS connectivity for
   arm sub-regions without creating driven hinges or sliders for them. Fixed the "i" and "h"
   panels that were orphaned when out-of-range edges were simply rejected.

**This session: two-pass BFS fix for the "b tab orphaned" bug.**

Root cause: the single-pass BFS mixed active and passive fold edges. `right-outer-arm` was
reachable from center via fold-1 (sourceIndex=1, lower than fold-4's sourceIndex=4 for
c-panel), so it was visited first. `right-outer-arm` had a passive fold-4 edge pointing at
`b-tab` — fold-4 extends rightward past its authored x=2456 end to x≈2931, creating a
passive fold-4 boundary between `right-outer-arm` and the b-tab region. BFS grabbed b-tab
as a child of `right-outer-arm` via that passive edge before c-panel was even processed.
b-tab should be a child of c-panel via the active fold-1 edge.

Fix: **two-pass BFS** in `buildFaceGraph` Step 7.

- **Pass 1** — active edges only (`adjListActive`). Correct driven-hinge parents are
  established first. c-panel claims b-tab via the active fold-1 edge as intended.
- **Pass 2** — all edges (`adjListAll`), starting from the full pass-1 visited frontier.
  Regions only reachable via passive edges (arm sub-regions from half-plane over-extension
  like the "i" and "h" panels) are picked up and attached without animation.

This supersedes the single `adjList` / single `queue` approach. The code comment explains
the b-tab example so future readers understand why two passes are needed.

**Result:** piece 069 loads, folds, and assembles correctly — confirmed in browser.

## Files touched

- `preview.html` — Step 7 of `buildFaceGraph` rewritten (two-pass BFS, two adjacency lists).
  No other changes this session; all other fixes were already in the file from the prior half.

## Open questions

- **Piece 066 has 19 orphans and 188 unknown-tag edges.** Console screenshot captured at
  session close. Piece 066 has 20 valley + 2 mountain folds and 34 silhouette vertices —
  more complex geometry. Likely the same class of issue (passive edges and/or edge-tagging
  gaps) but needs its own investigation. Logged for next session.

## Next-session handoff

Open `preview.html?piece=066` and read the console:
- 32 regions, 19 fold edges, root=region-17 (largest-by-area)
- 91 slivers filtered, 19 orphans, 188 unknown-tag edges

Start by understanding the silhouette geometry (read `work/pieces/066/066.svg`), map the
fold lines against it, and identify which regions are orphaned and why. The large unknown-tag
count (188) is the first clue — something structural about 066's authoring is confusing the
edge-tagger.
