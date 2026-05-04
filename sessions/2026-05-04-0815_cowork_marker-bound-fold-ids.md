---
date: 2026-05-04
start_time: "07:18"
end_time: "09:30"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Diagnose piece 066's fold-tagging failure (the explicit pick-back-up topic from the
2026-05-03 BFS-fix session) and settle whatever convention or parser change resolves it.

## What was done

### Diagnosis

Piece 066 is the long-strip framework piece — saw-tooth silhouette, 6 spine panels
separated by 5 horizontal valley + 2 horizontal mountain inside folds, with side tabs
(a, aa, b, c, d, e, f, g) on one edge and landings (b65, c65, d65, e65, f65, g65, h65,
j68, aa) on the other edge. Every side tab/landing has its own vertical fold attaching
it to a spine panel.

Initial state: console showed Face graph: 32 regions, 19 fold edges, 19 orphans, 188
unknown-tag edges, 91 slivers filtered, and only 7 of 22 folds producing driven hinges
(valley-15..19 + mountain-20-21 — exactly the column-internal horizontals; valley-0..14,
the 14 vertical tab/landing folds, produced ZERO hinges).

**Root cause (settled mid-session):** the 14 vertical fold paths sit at four nearly-shared
x-coordinates on each side (x ≈ 2474/2491/2498/2501 right; x ≈ 479/498/502 left). The
iterative half-plane cut algorithm collapses co-linear folds: the first cut at each x
produces region splits, but downstream folds at the same x produce no-ops (everything's
already separated). Their pathIds never get attached to any region, so the adjacency
step's pathId-tag lookup returns empty.

### Convention work — marker-bound fold ids (settled 2026-05-04, two passes)

**First pass (morning).** Settled the marker-bound fold ids convention: a fold path's id
matches the id of any marker authored in `<g id="marks">` (today: `tab-X`, `landing-X<piece>`).
The parser binds the fold to the region containing that marker's centroid, bypassing the
geometric ambiguity of co-linear folds. Optional default-angle suffix: `tab-c-40`. Cross-layer
same-id pairs (`tab-c` in both `marks` and `folds-valley`) declared intentional.

Convention docs updated: CLAUDE.md (new "Marker-bound fold ids" Architectural Decisions row;
new "Per-element ids inside fold layers" entry in File Naming Conventions), LAYER-CONVENTIONS.md
(folds section extended), work/SPEC-3D-VIEWER.md (parser-consumption table row), WORKPLAN.md
(SVG-layer-authoring + preview.html-iteration tracks).

**Same-day revision (mid-morning).** First test against 066 surfaced the bug: Affinity Designer
auto-suffixes marker ids with `1` on export when they collide cross-layer with fold-path ids
(15 of 17 markers got renamed `tab-c → tab-c1`, etc. — the only two that escaped were
`landing-aa` and `landing-j68`, the two without fold-path counterparts). The same-id-across-layers
assumption doesn't survive Affinity's export pipeline.

Revised the convention: fold-path ids take a `fold-` prefix (`fold-tab-c`, `fold-landing-h65`).
The `fold-` prefix gives every fold-path id a unique form, so Affinity has no reason to
auto-rename anything. Markers stay clean. Optional angle suffix unchanged: `fold-tab-c-40`.

All convention docs re-updated to reflect the prefix. CLAUDE.md, LAYER-CONVENTIONS.md, WORKPLAN.md.

### Parser implementation — `preview.html`

Five edits landed in `preview.html`:

1. `parseSVG` now extracts `marksCentroidsById` (Map from marker id → centroid coordinates)
   from `<g id="marks">`, walking every id'd descendant.
2. `parseMarkerBoundFoldId(id)` helper resolves a fold-path id by stripping the `fold-` prefix,
   trying direct marker lookup, then stripping an optional trailing `-<digits>` as default angle.
3. `parseFoldLayer` calls the new helper, sets `fold.markerBoundId` and applies the layer-signed
   default angle when present. Banner-warns ids with the `fold-` prefix that don't resolve.
4. `extendFoldsToSilhouette` preserves `markerBoundId` through to the face-graph step.
5. `buildFaceGraph` accepts a `marksCentroidsById` parameter. For marker-bound folds, the
   adjacency lookup is geometric (regions whose edges lie on the fold's authored line, within
   `MARKER_FOLD_EPS = max(ADJ_EPS, 0.003 × diagLen)`) instead of pathId-tag-based. The marker
   centroid is then used to identify the moving region; pairs touching it are active, others
   passive.

### Test results against piece 066

Substantial improvement, not yet complete:

- Orphans: 19 → **5**
- Fold edges: 19 → **70**
- Per-fold paths producing hinges: **15+** (most marker-bound tabs and landings resolving;
  4 still trip the "centroid not inside any region adjacent across this fold" check —
  fold-tab-b, fold-tab-c, fold-tab-e, fold-landing-h65)

Visual: when the global Fold-all slider moves, most regions fold but the result is shards
and slivers rather than a clean assembled cylinder. The fold rotations are running but the
topology isn't quite right.

### Design pivot at session close

Alan flagged that the iterative-fix approach was patching the parser to compensate for an
authoring abstraction that's fundamentally too thin. The SVG geometry alone can't reliably
express the topology when folds are co-linear, drift, or otherwise fail clean geometric
inference.

Discussion went to a "panel-explicit fold ids" proposal (`fold-A-to-B` where A and B are
both panel marker ids) — but Alan pushed back on the authoring complexity, especially given
the lack of a Claude-assisted layer-renaming tool for Affinity Designer.

**Final direction (for next iteration, not implemented this session):** **shared-edge
topology**. Keep existing authoring as-is (no new markers, no `-to-` syntax). Replace the
parser's geometric adjacency search with a polygon-topology lookup:

1. Find the marker's region via centroid containment (one region, point-in-polygon, robust).
2. Find regions that physically share a polygon edge with that region (polygon-clipping
   produces clean shared edges; checking edge-coordinate equality is cheap and exact).
3. Among shared-edge neighbors, pick the one whose shared edge is geometrically closest to
   the fold's authored line. That's the active fold-edge.

Co-linear folds, drift, tag-overwrite all become non-issues because we're using polygon
topology (which polygon-clipping produces precisely) rather than fold-line geometry (which
is brittle).

## Files touched

- `LAYER-CONVENTIONS.md` — folds section extended with marker-bound subsection (twice — initial
  same-id, then revised to `fold-` prefix); last-updated header.
- `CLAUDE.md` — new Architectural Decisions row "Marker-bound fold ids"; new "Per-element ids
  inside fold layers" entry in File Naming Conventions (both updated for prefix); last-updated
  header.
- `work/SPEC-3D-VIEWER.md` — parser-consumption table row for `folds-valley` / `folds-mountain`
  updated with marker-bound mention.
- `WORKPLAN.md` — recent log entries on `SVG layer authoring` track and `preview.html iteration`
  track; both tracks' front-matter `next_action`; last-updated footer.
- `preview.html` — five edits: marks parsing, `parseMarkerBoundFoldId`, `parseFoldLayer` updates,
  `extendFoldsToSilhouette` preserves binding, `buildFaceGraph` accepts marks map and uses
  geometric adjacency for marker-bound folds with widened epsilon.
- `sessions/2026-05-04-0815_cowork_marker-bound-fold-ids.md` — this note.

## Open questions

1. **Shared-edge topology.** Adopt as the next-iteration parser direction? No new authoring
   needed. Cleanest fix for the residual 4 banner cases on 066.
2. **Closure constraint.** Still parked. Three options on the table (author-most/derive-one,
   author-shape, closure-as-slider). Becomes urgent once the fold animation works correctly
   for cylindrical pieces (066 is the canonical example).
3. **Authoring-tool gap.** Renaming layers in Affinity by hand is a real pain point. Worth
   exploring whether a `.af`-file-aware script (operating on the binary or the export) or an
   Affinity macro could help with batch-renaming fold-path layers.
4. **Pieces beyond 066.** Alan flagged that other long-strip pieces have the same fold
   structure (some are cylindrical, some aren't). The convention needs to apply consistently
   across them; 066 is just the test bed.

## Next-session handoff

Alan wants to pick this up with a fresh look on fold authoring standards.

**Read first:**
- This session note.
- Updated CLAUDE.md "Marker-bound fold ids" decision row + "Per-element ids inside fold layers"
  conventions row.
- Updated LAYER-CONVENTIONS.md folds section.
- The state of `preview.html`'s `buildFaceGraph` adjacency step (lines ~1737-1800), where
  the next iteration's shared-edge topology refactor will land.

**Likely next move:** sketch the shared-edge topology refactor as a CODE_PROMPT (probably
small — replace one block in `buildFaceGraph` with shared-edge neighbor lookup). Test against
066 and against any second strip-piece Alan onboards.

**Don't forget:** closure constraint is still on the open list. Once the topology question
is resolved on 066, the closure design becomes the next thing to settle (so the cylinder
actually closes when fully folded — tab-aa landing on landing-aa).
