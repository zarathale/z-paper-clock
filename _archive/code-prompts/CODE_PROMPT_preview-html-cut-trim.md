---
status: shipped
started: 2026-05-04
shipped: 2026-05-04
owner: Zarathale (Alan)
target: preview-html-cut-trim
---

_Shipped 2026-05-04; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._

## What You Are Doing and Why

Replace `buildFaceGraph`'s half-plane infinite-line cuts with **authored-segment cuts** in `preview.html`. Each fold cuts only the extent the author drew in Affinity — not the full silhouette. Drop the `passive` field on `foldEdges` (every cut edge is now driven by definition). Simplify the BFS to a single pass. Add a `markerToRegionId` map and per-region `markerIds` list to the face-graph return as forward-look infrastructure for the eventual assembly engine.

This prompt was scoped at the 2026-05-04 cut-trim cowork session. Background: the previous Code session shipped the face-graph diagnostic harness (Dump button, 2D overlay, console summary). The 066 dump confirmed that **phantom strips between co-linear infinite-line cuts are the dominant failure mode** — 18 of 32 regions are tall thin slivers, 8 of those carry multiple fold-edge tags, 17 of 32 regions have ≤1 shared-edge neighbor (graph fragmented), 12 of 15 marker-bound folds have suspect candidate distances (>5 viewBox units). The right neighbor doesn't exist in the shared-edge index for these folds because the topology was already broken before adjacency search ran. A tightened picker can't fix this.

The fix is to respect what's already authored: each fold path Alan draws in Affinity has explicit start/end coordinates. The existing `extendedFold.authoredStart` / `authoredEnd` already capture this. Cut-trim just tells the cut step "use those endpoints; don't extend infinitely." The phantom-strip class of failure disappears at the source.

A survey across all 8 authored SVGs (001, 065, 066, 067, 069, 070, 071, 072) confirmed cut-trim is safe: it definitively fixes 066 (the actively broken case), produces marginally cleaner topology on 069, and is **strictly neutral on every other piece** — using authored segments cuts more conservatively than infinite-line extension, never less. No re-authoring required.

## Prerequisites — confirm before starting

- `preview.html` exists at repo root and runs cleanly via `localhost:8000/preview.html?piece=NNN` against pieces 001, 066, 069, 071.
- The face-graph diagnostic harness (Dump button + 2D overlay + console summary) is shipped — `CODE_PROMPT_preview-html-face-graph-diagnostics.md` is `status: shipped`.
- The marker-bound fold ids convention is in effect (parsing populates `marksCentroidsById` and `markerBoundId` on each fold). Don't redo any of that.
- `polygon-clipping` is loaded (line 9). The cut-trim algorithm doesn't rely on it for cuts (manual polygon splitting), but it stays loaded for the cutouts subtraction code path.
- No version bump (preview.html iteration).

## Read These Files First

1. `CLAUDE.md` — top sections + "Marker-bound fold ids" Architectural Decisions row + "Per-element ids inside fold layers" entry in File Naming Conventions. The cut-trim change preserves both conventions exactly as documented.
2. `sessions/2026-05-04-1145_code_preview-html-face-graph-diagnostics.md` — what the diagnostic harness shipped and what the 066 dump showed.
3. `sessions/2026-05-04-XXXX_cowork_cut-trim.md` (forthcoming at session-close; will be the cowork session that produced this prompt) — the 066 dump analysis, the survey across 8 SVGs, and the decision to ship cut-trim with two small forward-look additions.
4. `preview.html` lines 1504–1568 (`extendFoldsToSilhouette`) — read the comment on lines 1556–1559 about marker-bound folds. The function's `authoredStart` / `authoredEnd` fields are the input cut-trim consumes; the `start` / `end` fields (extended to silhouette boundary) become unused for the cut step but stay on the object for the diagnostic overlay's "extended fold line" rendering.
5. `preview.html` lines 1570–2192 (`buildFaceGraph` end-to-end). All of it — most of this file region is being rewritten or simplified. Note especially:
   - Lines 1665–1716: current half-plane cut step. **Replaced.**
   - Lines 1718–1733: sliver filter. **Kept as safety net but expected to filter 0.**
   - Lines 1749–1833: shared-edge index + per-fold candidate annotation. **Kept** — still useful for the diagnostic overlay even though adjacency comes for free now.
   - Lines 1835–2019: post-hoc adjacency search with marker-bound vs unidentified branches. **Replaced** — adjacency falls out of the cut step directly.
   - Lines 2021–2117: root + two-pass BFS. **Simplified to single pass** — no `passive` distinction means no need for the active-only first pass.
   - Lines 2121–2191: `_diag` payload. **Updated** for the new fields (`markerIds` per region, dropped `passiveFoldEdgeCount`).
6. `preview.html` lines 2389–2415 — hinge construction reads `edge.passive`. **Updated** — `passive` is gone; targetAngle is unconditional.
7. `preview.html` lines 2618 + 3071–3099 — console summary refers to `sliverCount` / `orphanCount` / `unknownTagCount` and `passive-edges` / `active-edges`. **Updated** — drop the `passive` line in the summary; keep slivers/orphans/unknown but expect them at 0 for healthy pieces.

## Target File Structure Changes

```
z-paper-clock/
├── preview.html                                          ← update: replace cut algorithm; drop passive; simplify BFS; add markerToRegionId
├── CODE_PROMPT_preview-html-cut-trim.md                  ← update: status flips to shipped on PR open
└── sessions/
    └── 2026-05-04-HHMM_code_preview-html-cut-trim.md     ← NEW: ship session note
```

No SVGs touched. No convention docs touched. The marker-bound fold ids convention stays exactly as documented; the new `mark-<letter>` marker class (in active use on piece 069) is inert from this algorithm's perspective and just flows through `marksCentroidsById` into `markerToRegionId`.

## Numbered Tasks

### 1. Add segment-vs-polygon intersection helpers

Insert these helpers near the existing geometric helpers (around `polyArea` / `pointInPolygon` / `halfPlanePoly`, lines ~1423–1502). They support segment-cut polygon splitting.

```js
// Segment-segment intersection. Returns null if parallel or out of range.
// Otherwise returns { point, t, s } where t is parameter along (a→b) and
// s is parameter along (c→d), both in [0, 1].
function segmentSegmentIntersection(a, b, c, d) {
  const dx1 = b[0] - a[0], dy1 = b[1] - a[1];
  const dx2 = d[0] - c[0], dy2 = d[1] - c[1];
  const det = dx1 * dy2 - dy1 * dx2;
  if (Math.abs(det) < 1e-10) return null;     // parallel
  const t = ((c[0] - a[0]) * dy2 - (c[1] - a[1]) * dx2) / det;
  const s = ((c[0] - a[0]) * dy1 - (c[1] - a[1]) * dx1) / det;
  // Half-open at vertex shared between consecutive edges to avoid double-counting
  if (t < -1e-9 || t > 1 + 1e-9) return null;
  if (s < -1e-9 || s > 1 + 1e-9) return null;
  return { point: [a[0] + t * dx1, a[1] + t * dy1], t, s };
}

// Find all points where the authored fold segment (p1→p2) crosses the polygon
// boundary. Returns [{ point, polyEdgeIdx, t (along segment) }] sorted by t.
// Deduplicates near-coincident hits at shared vertices.
function findSegmentPolygonCrossings(p1, p2, polygon) {
  const hits = [];
  const n = polygon.length;
  for (let i = 0; i < n; i++) {
    const q1 = polygon[i];
    const q2 = polygon[(i + 1) % n];
    const inter = segmentSegmentIntersection(p1, p2, q1, q2);
    if (inter) hits.push({ point: inter.point, polyEdgeIdx: i, t: inter.t });
  }
  hits.sort((a, b) => a.t - b.t);
  // Dedup: within 1e-6 of an already-recorded hit (vertex collisions report on both edges)
  const out = [];
  for (const h of hits) {
    const dup = out.some(o =>
      Math.hypot(o.point[0] - h.point[0], o.point[1] - h.point[1]) < 1e-6
    );
    if (!dup) out.push(h);
  }
  return out;
}

// Split a polygon at two cut points c1, c2 (each = { point, polyEdgeIdx }) on
// the polygon's boundary. Returns [polyA, polyB] — the two halves separated by
// the chord c1→c2. Walks the polygon vertices: polyA contains the boundary
// segment from c1 forward to c2; polyB contains the remaining boundary back
// from c2 to c1. Both halves are closed by the chord.
function splitPolygonAtChord(polygon, c1, c2) {
  // Order so first.polyEdgeIdx <= second.polyEdgeIdx; if equal, use t along the
  // edge (recompute by projecting c.point onto the polygon edge).
  function tOnEdge(c) {
    const i = c.polyEdgeIdx, n = polygon.length;
    const [ax, ay] = polygon[i], [bx, by] = polygon[(i + 1) % n];
    const dx = bx - ax, dy = by - ay;
    const len2 = dx * dx + dy * dy;
    if (len2 < 1e-20) return 0;
    return ((c.point[0] - ax) * dx + (c.point[1] - ay) * dy) / len2;
  }
  let first = c1, second = c2;
  if (first.polyEdgeIdx > second.polyEdgeIdx ||
     (first.polyEdgeIdx === second.polyEdgeIdx && tOnEdge(first) > tOnEdge(second))) {
    [first, second] = [second, first];
  }

  const n = polygon.length;
  const polyA = [];
  const polyB = [];

  // polyA: vertices [0..first.polyEdgeIdx], first.point, second.point, vertices (second.polyEdgeIdx+1..n-1)
  for (let i = 0; i <= first.polyEdgeIdx; i++) polyA.push(polygon[i]);
  polyA.push(first.point);
  polyA.push(second.point);
  for (let i = second.polyEdgeIdx + 1; i < n; i++) polyA.push(polygon[i]);

  // polyB: first.point, vertices (first.polyEdgeIdx+1..second.polyEdgeIdx), second.point
  polyB.push(first.point);
  for (let i = first.polyEdgeIdx + 1; i <= second.polyEdgeIdx; i++) polyB.push(polygon[i]);
  polyB.push(second.point);

  return [polyA, polyB];
}
```

### 2. Replace the cut step in `buildFaceGraph` (lines ~1665–1716)

The new cut step iterates folds; for each fold, iterates current regions; for each region, finds segment/polygon crossings and splits if and only if there are exactly 2 crossings. Other intersection counts (0, 1, 3+) leave the region whole or produce multiple sequential cuts — see "case handling" below.

**Important:** the cut step does NOT build `foldEdges` directly. After all cuts complete and the shared-edge index is built (existing diagnostic code, kept intact), Task 3 walks the shared edges and assigns each one to a fold by matching endpoints to the fold's authored line. This is robust against the polygon-identity-tracking problem (a half-A from cut #1 may be further cut by fold #2 into halves B1, B2; the original half-A reference is gone).

Replace the entire `for (const fold of extendedFolds) { ... }` block at lines 1677–1716 with:

```js
let totalUnknown = 0;

for (const fold of extendedFolds) {
  const p1 = fold.authoredStart;
  const p2 = fold.authoredEnd;
  const nextRegions = [];

  for (const region of regions) {
    const crossings = findSegmentPolygonCrossings(p1, p2, region.polygon);

    if (crossings.length === 0) {
      // Fold segment doesn't touch this region — keep whole.
      nextRegions.push(region);
      continue;
    }
    if (crossings.length === 1) {
      // One endpoint inside the region (or fold tangent at a vertex).
      // Physical paper folds don't have free interior endpoints — skip cut,
      // keep region whole, log diagnostic.
      console.warn('[preview.html] fold', fold.pathId, 'has 1 boundary crossing in region — interior fold endpoint? Skipping cut.');
      nextRegions.push(region);
      continue;
    }

    // Canonical case: 2+ crossings, even count → cut at consecutive pairs.
    // Odd count is degenerate (drop the last and warn).
    if (crossings.length % 2 !== 0) {
      console.warn('[preview.html] fold', fold.pathId, 'has', crossings.length,
                   'boundary crossings (odd) — dropping last for pairwise cut.');
      crossings.pop();
    }

    // Apply cuts sequentially. Each cut splits one of the working halves into
    // two; subsequent cuts apply to whichever half contains the next pair's
    // midpoint. For the canonical 2-crossing case this loop runs once.
    let workingHalves = [region];
    for (let i = 0; i < crossings.length; i += 2) {
      const c1 = crossings[i], c2 = crossings[i + 1];
      const midX = (c1.point[0] + c2.point[0]) / 2;
      const midY = (c1.point[1] + c2.point[1]) / 2;
      const target = workingHalves.find(h => pointInPolygon(midX, midY, h.polygon));
      if (!target) {
        console.warn('[preview.html] fold', fold.pathId, 'pair', i / 2, 'midpoint not in any working half');
        continue;
      }
      // Re-find crossings against the working half (cut points may have moved
      // when target was a result of an earlier cut in this loop).
      const rCrossings = findSegmentPolygonCrossings(p1, p2, target.polygon);
      if (rCrossings.length < 2) {
        console.warn('[preview.html] fold', fold.pathId, 'multi-cut re-find returned <2');
        continue;
      }
      // Find the rCrossings that match c1 / c2 by spatial proximity.
      const matchC1 = rCrossings.find(h => Math.hypot(h.point[0] - c1.point[0], h.point[1] - c1.point[1]) < 1e-3) || rCrossings[0];
      const matchC2 = rCrossings.find(h => Math.hypot(h.point[0] - c2.point[0], h.point[1] - c2.point[1]) < 1e-3) || rCrossings[1];
      const [polyA, polyB] = splitPolygonAtChord(target.polygon, matchC1, matchC2);
      if (polyA.length < 3 || polyB.length < 3) {
        console.warn('[preview.html] fold', fold.pathId, 'cut produced degenerate halves');
        continue;
      }
      const tagsA = computeEdgeTagsForCut(polyA, target.edgeTags, fold);
      const tagsB = computeEdgeTagsForCut(polyB, target.edgeTags, fold);
      const idx = workingHalves.indexOf(target);
      workingHalves.splice(idx, 1,
        { polygon: polyA, edgeTags: tagsA },
        { polygon: polyB, edgeTags: tagsB });
    }
    nextRegions.push(...workingHalves);
  }

  regions = nextRegions;
}
```

Replace the existing `computeEdgeTags` function (lines 1613–1663) with a simpler `computeEdgeTagsForCut`:

```js
// After a segment cut, the edges of an output sub-polygon are either:
// (a) a sub-segment of an input polygon edge (inherits the input edge's tag), or
// (b) the cut chord itself (gets the fold's pathId).
// Match each output edge by midpoint-distance to the cut chord first; otherwise
// nearest input edge.
function computeEdgeTagsForCut(outPoly, inputEdgeTags, fold) {
  const n = outPoly.length;
  const tags = new Array(n);
  const [fx1, fy1] = fold.authoredStart;
  const [fx2, fy2] = fold.authoredEnd;

  for (let i = 0; i < n; i++) {
    const [ax, ay] = outPoly[i];
    const [bx, by] = outPoly[(i + 1) % n];
    const mx = (ax + bx) / 2, my = (ay + by) / 2;

    // (a) is this edge the cut chord? — both endpoints lie on the fold's
    //     authored line within EDGE_EPS, AND the midpoint sits on the segment.
    const dA = ptToSegDist(ax, ay, fx1, fy1, fx2, fy2);
    const dB = ptToSegDist(bx, by, fx1, fy1, fx2, fy2);
    const dM = ptToSegDist(mx, my, fx1, fy1, fx2, fy2);
    if (dA < EDGE_EPS && dB < EDGE_EPS && dM < EDGE_EPS) {
      tags[i] = fold.pathId;
      continue;
    }

    // (b) match to nearest input edge by midpoint distance.
    let bestDist = Infinity, bestTag = 'unknown';
    for (const { mid, tag } of inputEdgeTags) {
      const d = Math.hypot(mx - mid[0], my - mid[1]);
      if (d < bestDist) { bestDist = d; bestTag = tag; }
    }
    if (bestDist < EDGE_EPS) tags[i] = bestTag;
    else { tags[i] = 'unknown'; totalUnknown++; }
  }
  return tags.map((tag, i) => {
    const [ax, ay] = outPoly[i];
    const [bx, by] = outPoly[(i + 1) % n];
    return { mid: [(ax + bx) / 2, (ay + by) / 2], tag };
  });
}
```

(Note: `totalUnknown` is captured from the enclosing scope, same as before. Hoist its declaration to before the cut loop.)

### 3. Build `foldEdges` from the shared-edge index (post-cut)

The diagnostic harness already builds the shared-edge index after the sliver filter (lines ~1749–1790, `edgeIndex` → `sharedEdges`). After cut-trim, every shared edge corresponds to either:

- **(a)** a fold's cut chord — both endpoints lie on the fold's authored line within `EDGE_EPS`. → becomes a `foldEdge`.
- **(b)** a sliver of original silhouette boundary that happens to sit between two regions because consecutive silhouette vertices are co-linear-with-an-internal-cut. → very rare; ignore (no foldEdge).

After the shared-edge index is built (existing code at lines 1764–1790), insert the `foldEdges` construction:

```js
// Build foldEdges from shared edges that lie on each fold's authored line.
// Each shared edge between two regions either corresponds to a fold's cut chord
// (both endpoints on the fold's authored segment within EDGE_EPS) or is a
// silhouette segment that happens to sit between two regions (very rare).
// One fold may produce multiple shared edges if it cut multiple separate
// regions or if its chord was further subdivided by a perpendicular fold.
const foldEdges = [];
const usedSharedEdgeKeys = new Set();

for (const fold of extendedFolds) {
  const [fx1, fy1] = fold.authoredStart;
  const [fx2, fy2] = fold.authoredEnd;
  for (const se of sharedEdges) {
    if (usedSharedEdgeKeys.has(se.key)) continue;  // each SE matches at most one fold
    const [[ax, ay], [bx, by]] = se.endpoints;
    const dA = ptToSegDist(ax, ay, fx1, fy1, fx2, fy2);
    const dB = ptToSegDist(bx, by, fx1, fy1, fx2, fy2);
    if (dA < EDGE_EPS && dB < EDGE_EPS) {
      foldEdges.push({
        pathId: fold.pathId,
        layer: fold.layer,
        polarity: fold.layer === 'folds-valley' ? 'valley' : 'mountain',
        defaultAngle: fold.defaultAngle,
        segment: se.endpoints,
        sourceFold: { id: fold.id, layer: fold.layer, sourceIndex: fold.sourceIndex },
        regionA: se.regionA,
        regionB: se.regionB
      });
      usedSharedEdgeKeys.add(se.key);
    }
  }
}
```

If a fold ends up with no `foldEdge` (its authored segment didn't actually subdivide any region — likely because it falls entirely outside the silhouette or is degenerate), banner-warn and continue:

```js
const foldsWithEdge = new Set(foldEdges.map(fe => fe.pathId));
for (const fold of extendedFolds) {
  if (!foldsWithEdge.has(fold.pathId)) {
    addBanner(`Fold "${fold.pathId}" — no cut chord found in face graph (degenerate fold or off-piece).`, 'warn');
  }
}
```

**Note on the deleted post-hoc adjacency (lines 1835–2019).** The entire post-hoc adjacency search — `edgeOnFold`, `MARKER_FOLD_EPS`, the marker-bound vs unidentified branching, the projection-and-overlap pairwise check, the `passive` segment-range check — is **all replaced by the seven lines above**. Delete lines 1835–2019 entirely. The marker-bound disambiguation (which-side-is-moving) happens in the BFS root selection (Step 6 + 7), not at adjacency-search time.

### 4. Drop the `passive` field everywhere

Cut-trim eliminates the class of edges that needed `passive`. Every `foldEdge` corresponds to a real authored cut chord. Remove these:

- The `passive` field on each `foldEdge` (already absent from the new construction in Task 3).
- The `passive` parameter and conditional in the BFS (Task 5).
- `edge.passive` reads in the hinge construction at lines 2389–2415:
  - Line 2393: replace `hinge.userData.targetAngle = edge.passive ? 0 : signFwd * (-edge.defaultAngle) * Math.PI / 180;` with the unconditional form `hinge.userData.targetAngle = signFwd * (-edge.defaultAngle) * Math.PI / 180;`.
  - Line 2397: delete `hinge.userData.passive = !!edge.passive;`.
  - Line 2411: replace `if (!edge.passive) {` with the unconditional `{` (every hinge registers in `pathHingeMap`).
- `_diag.summary.activeFoldEdgeCount` and `passiveFoldEdgeCount` (lines 2172–2173): replace both with a single `foldEdgeCount` field. (`foldEdgeCount` already exists at line 2171; just delete the active/passive lines.)
- `_diag.foldEdges[].passive` field (line 2154): delete.
- The `[face-graph]` console summary (lines 3076–3079): drop `passive-edges=${s.passiveFoldEdgeCount}` from the summary string. Keep `active-edges` if you like — but rename it to `fold-edges` since the active/passive distinction is gone.

Add a defensive check: at the end of `buildFaceGraph`, count `foldEdges` whose `regionA` or `regionB` doesn't exist in `regionMap`. If non-zero, banner-warn — that's a bug, not normal output.

### 5. Simplify the BFS to a single pass (lines 2047–2117)

Without `passive`, the two-pass distinction collapses. Replace the two-pass BFS with a single pass:

```js
const visited = new Set([rootId]);
let orphanCount = 0;

const adjList = new Map();
for (const [rId] of regionMap) adjList.set(rId, []);
for (const fe of foldEdges) {
  adjList.get(fe.regionA).push({ neighborId: fe.regionB, fe });
  adjList.get(fe.regionB).push({ neighborId: fe.regionA, fe });
}
// Sort by sourceIndex for deterministic ordering
for (const [, neighbors] of adjList)
  neighbors.sort((a, b) => a.fe.sourceFold.sourceIndex - b.fe.sourceFold.sourceIndex);

const queue = [rootId];
while (queue.length > 0) {
  const curId = queue.shift();
  const cur = regionMap.get(curId);
  for (const { neighborId, fe } of (adjList.get(curId) || [])) {
    if (visited.has(neighborId)) continue;
    visited.add(neighborId);
    const neighbor = regionMap.get(neighborId);
    neighbor.parentId = curId;
    neighbor.parentEdge = fe;
    cur.childEdges.push({ childId: neighborId, edge: fe });
    queue.push(neighborId);
  }
}

for (const [rId] of regionMap) {
  if (!visited.has(rId)) {
    orphanCount++;
    addBanner(`Region ${rId} is unreachable from root — rendered flat.`, 'warn');
  }
}
```

### 6. Add `markerToRegionId` map and per-region `markerIds` to face graph return

This is the forward-look infrastructure for the assembly engine. The data is already implicit in `marksCentroidsById` + `regionMap`; this step exposes it.

After Step 6 (root assignment) and before the BFS, add:

```js
// markerToRegionId: every marker in marksCentroidsById resolved to the region
// containing its centroid. The assembly engine (M4) consumes this for
// cross-piece pairing — tab-X.regionId on piece N pairs with landing-XN.regionId
// on piece M to drive the per-piece transforms. Today this is read-only data;
// no current consumer in preview.html.
const markerToRegionId = new Map();
const markersByRegion = new Map();
for (const [rId] of regionMap) markersByRegion.set(rId, []);
for (const [markerId, c] of marksCentroidsById) {
  for (const [rId, region] of regionMap) {
    if (pointInPolygon(c.x, c.y, region.polygon)) {
      markerToRegionId.set(markerId, rId);
      markersByRegion.get(rId).push(markerId);
      break;
    }
  }
}
```

Update the existing `_diag` const construction to add per-region `markerIds` and the `markerToRegionId` array, then add `markerToRegionId` (the Map) as a top-level return field:

```js
// Inside the existing _diag = { ... } construction (around line 2124),
// augment the regions[] array entries with markerIds:
regions: Array.from(regionMap.values()).map(r => ({
  id: r.id,
  polygon: r.polygon,
  area: polyArea(r.polygon),
  vertexCount: r.polygon.length,
  isRoot: r.isRoot,
  parentId: r.parentId,
  edgeTags: r.edgeTags.map(et => et.tag),
  markerIds: markersByRegion.get(r.id) || []          // NEW
})),

// And add a new top-level _diag field:
markerToRegionId: Array.from(markerToRegionId.entries()).map(
  ([markerId, rId]) => ({ markerId, regionId: rId })
),
```

Then update the return statement (around line 2182) to include the Map at the top level:

```js
return {
  rootId,
  regions: regionMap,
  foldEdges,
  sliverCount,
  orphanCount,
  unknownTagCount: totalUnknown,
  rootSource,
  markerToRegionId,        // NEW: forward-look for assembly engine
  _diag
};
```

### 7. Update the diagnostic overlay to render per-region marker lists

In `renderFaceGraphOverlay(diag)`, the marker centroids are already drawn (Task 6 of the previous prompt). With `markerToRegionId` exposed, each region can also display its marker-id list. Small addition: append the region-id label (lines that draw `region-N` text in `<text>` at region centroids) to include the marker-ids if present:

```js
// Inside renderFaceGraphOverlay, where region-id text labels are drawn:
const labelText = region.markerIds && region.markerIds.length > 0
  ? `${region.id} {${region.markerIds.join(', ')}}`
  : region.id;
text.textContent = labelText;
```

This is a 3-line edit. The marker dots themselves still render separately as before; the addition is just showing which region owns which marker.

### 8. Remove the now-unused `extendFoldsToSilhouette` extension behavior (optional cleanup)

The `start` / `end` fields on each `extendedFold` (the boundary-extended endpoints) are no longer used by the cut step. They're still used by the diagnostic overlay's "fold authored segments" rendering (which actually wants `authoredStart` / `authoredEnd` — Task 4 of the previous prompt explicitly says use authored, not extended).

The function `extendFoldsToSilhouette` itself can stay (it's still doing useful work computing `authoredStart`, `authoredEnd`, and the `pathId` defaulting), but the `start` / `end` extension is now dead code. **Don't delete the function or the extension code in this prompt** — the small amount of dead computation is cheap, and removing it expands the surface area of this change. Flag in the session note as a low-priority follow-up cleanup.

## Verification Checklist

1. **No console errors** when opening `localhost:8000/preview.html?piece=NNN` for each of: 001, 066, 069, 071, 072, 067. Page renders cleanly; thickness/rotation sliders work; orbit/zoom work.

2. **Piece 066 — the smoking gun.** Open `?piece=066`. Expect:
   - **Zero "Region region-XX is unreachable from root — rendered flat" banners.** (Was 6+ before cut-trim.)
   - **Zero "Marker-bound fold ... centroid not inside any region adjacent across this fold" banners.** (Was 4 before cut-trim.)
   - All 17 marker-bound folds produce a driven hinge in `pathHingeMap`. (Console: "Per-fold paths:" line.)
   - The Fold-all slider folds the whole strip into a recognizable column with side panels + closure, **no shards or slivers**.
   - Console summary: `regions=` somewhere in the 18–25 range (was 32, the surplus was slivers); `slivers-filtered=0`; `fold-edges` count matches the 21 authored folds (give or take edge cases).
   - Dump JSON, inspect: every fold has a `regionA`/`regionB` pair; every marker resolves to a real `regionId` in `markerToRegionId`.

3. **Piece 069 — regression check on unidentified-fold path.** Open `?piece=069`. Expect:
   - Same fold count as before (8 valley folds).
   - Same number of regions or one less. (Cut-trim may collapse two regions that were previously separated by phantom-strip noise; either is fine.)
   - Folding behavior visually unchanged.
   - All 11 markers (`tab-a..g`, `landing-a/b/h/i`, `mark-h`, `mark-i`) resolve in `markerToRegionId`. **`mark-h` and `mark-i` should resolve to whatever region contains them** (likely the central face); their presence in the dump is the verification that `mark-<letter>` flows through.

4. **Piece 071 — regression check on cutouts path.** Open `?piece=071`. Expect:
   - Cutouts still render as holes in the slab (visually unchanged).
   - 3 valley folds still produce 3 hinges.
   - 2 cross-piece landings (`landing-b70`, `landing-c70`) resolve in `markerToRegionId`.

5. **Piece 001 — regression check on long strip with auto-rename cluster.** Open `?piece=001`. Expect:
   - The Affinity auto-rename cluster (`fold-tab-a`, `-a1`, `-a2`, `-a3`, `fold-tab-d`, `-d1`) still has the old behavior — the rename cluster is a different problem, not addressed here. Some folds may not produce hinges; no regression vs. pre-cut-trim.
   - Region count and topology should be cleaner (fewer artifacts from the few co-linear-ish folds at x=1140).

6. **Piece 072 / 067 / 070 — sanity checks.**
   - 072: pure flat shape, no folds — should render flat with no warnings.
   - 067: flat receiver with 4 cross-piece landings — landings should all resolve in `markerToRegionId`.
   - 070: silhouette-wrapper authoring is broken (separate concern) — expect existing behavior, no new errors from cut-trim.

7. **Diagnostic dump** still works on every piece. JSON parses; payload includes the new `markerToRegionId` array and per-region `markerIds`.

8. **Diagnostic overlay** still works. Toggle it on each piece. Region labels now show `region-N {tab-c, landing-d}` style when markers are present; plain `region-N` otherwise.

9. **Console summary** prints `[face-graph] piece=... regions=... folds=... fold-edges=... shared-edges=... slivers-filtered=...` (no `passive-edges` line).

## What NOT to Change

- **Marker-bound fold id parsing.** Already correct; the `marksCentroidsById` and `markerBoundId` fields flow through unchanged.
- **`mark-<letter>` markers.** Inert from the algorithm's perspective — they flow through `marksCentroidsById` and into `markerToRegionId` like any other marker. No special-case code.
- **Convention docs.** No CLAUDE.md / LAYER-CONVENTIONS.md / SPEC changes from this prompt. The cut-trim change is implementation, not convention. (The `mark-<letter>` formal recognition + bare-form-landing fix on 065/069 + 001 auto-rename + 070 silhouette wrapper all belong to the next convention-cleanup pass.)
- **Cutouts subtraction path** (`<g id="cutouts">`). Not yet implemented end-to-end and out of scope for cut-trim. Cutouts that exist on piece 071 keep their current rendering.
- **Closure constraint** (cylinder wrap-around). Still parked.
- **Cross-piece pairing logic, transforms, group hierarchy.** That's M4 (assembly engine). This prompt only exposes the data the assembly engine will read.
- **The shared-edge index + per-fold candidate annotation** in the existing diagnostic harness (lines ~1749–1833). Keep — the overlay renders shared-edge lines, and after cut-trim those lines should be much sparser and cleaner. Useful sanity signal.

## Manual tests

After merge, Alan runs `localhost:8000/preview.html` and works through the test bench:

| Piece | Action | What to look for |
|---|---|---|
| 066 | Load via `?piece=066`. Click Fold-all slider to 100% / Assembled. | The strip folds into a column with side panels visible. No shards. No sliver banners. No "centroid not inside any region adjacent" banners. **The point of this prompt.** |
| 069 | Load. Toggle overlay. Move sliders. | Visually unchanged. Region labels in overlay show `mark-h` and `mark-i` belong to the central region. |
| 071 | Load. | Cutouts still render. Folds work. Landings resolve. |
| 001 | Load. Toggle overlay. | Long strip renders. Auto-renamed folds may still mis-bind; no regression vs. pre-cut-trim. |
| 072 | Load. | Pure flat shape, no warnings. |
| 067 | Load. | All 4 landings resolve in markerToRegionId (visible in dump JSON). |
| 070 | Load. | Existing rendering unchanged. No new errors. |

Goal: confirm 066 is fixed, 069 is unchanged-or-better, no regressions on others. Post a summary back in cowork. The next session reads it and picks up either (a) the convention-cleanup pass (001 auto-rename + 065/069 bare-form landings + 070 silhouette wrapper + `mark-<letter>` formal recognition) or (b) starting on the closure constraint design.
