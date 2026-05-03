# Regions and Face Graph — Design Spec

**Status:** draft
**Created:** 2026-05-03
**Standalone:** yes — may eventually merge into `SPEC-3D-VIEWER.md` but starts here so it can iterate independently.

---

## What this spec is for

Folding (F1 visual / F2 semantic / F3 experiential) and grouping (G1 transform-parenting / G2 glue-relationships) are both operations on *subdivisions of a piece*. Neither can be implemented with confidence until "what counts as a region of piece N" is a deterministic, computable thing. This spec defines that computation.

Regions are **not authored** — they are derived at load time from the layered SVG. Nothing new is written to the JSON sidecar. No pipeline stage is added. The SVG already carries the silhouette, cutouts, and fold lines; this spec says exactly how to turn those into a planar face graph.

---

## Definition: what is a region

A **region** is a maximal connected polygon of paper that lies between fold lines. Fold lines are the edges — they subdivide the silhouette into faces. The result is a planar graph:

- **Vertices** — fold-line endpoints, fold-line / fold-line intersections, and points where fold lines meet the silhouette boundary.
- **Edges** — fold-line segments between vertices (labelled valley or mountain) + silhouette-boundary arcs between adjacent vertices (unlabelled; they are the cut perimeter).
- **Faces** — the closed polygons formed by the planar subdivision; each face is one region.

A **cutout** (from `<g id="cutouts">`) is a hole punched through a region, not a region divider. The region that contains a cutout hole is still one region; the hole affects the rendered mesh (it's subtracted from the slab) but not the adjacency graph or fold tree.

**What is NOT a region:** glue tabs are not separate regions unless a fold line explicitly runs along their crease. Many tabs in this book fold along a scored crease that corresponds to a dashed or plus-sign mark — those marks will be in `folds-valley` or `folds-mountain`, and they *do* create region boundaries. A tab whose crease line is not in either fold layer is part of its parent region and folds as a rigid body with it.

---

## Algorithm: silhouette × fold lines → face polygons

**Inputs:**

- `silhouette` polygon (single closed path from `<g id="silhouette">`; holes from `<g id="cutouts">` are carried along but do not participate in the subdivision).
- `folds-valley` and `folds-mountain` open paths — each path is a sequence of `[start, end]` segments in SVG-space.

**Steps:**

1. **Extend fold lines to the silhouette boundary.** Each fold-line segment that doesn't reach the silhouette boundary is extended in both directions until it intersects the boundary (or another fold line that already reaches the boundary). This prevents T-junctions: a fold line that terminates inside the piece would not divide it into two closed faces. Extension uses parametric ray-casting against the silhouette polygon's edges. If a fold line is already boundary-to-boundary, no extension is needed. **Note:** extension is a geometric operation on the computed segments; it does not alter the authored SVG.

2. **Clip.** Use `polygon-clipping` (JavaScript; already loaded in `preview.html` via CDN) or Shapely (Python; already in `.venv`) to iteratively subtract each extended fold-line segment from the silhouette polygon. Each subtraction splits one polygon into two. After all fold lines are applied, the result is a set of non-overlapping polygons that together tile the silhouette.

3. **Collect faces.** Each output polygon is one region. Assign sequential ids: `region-0`, `region-1`, … in the order the clipping algorithm produces them (deterministic for a given SVG; re-ordered by BFS traversal in the next step).

4. **Build adjacency.** Two regions are adjacent if they share an edge that corresponds to a fold-line segment. Record the shared edge's polarity (valley or mountain) and its SVG-space segment `[start, end]`. Regions that share only a silhouette-boundary edge are topologically adjacent but not fold-adjacent — they are neighbors in the planar graph but are not connected by a hinge.

---

## Moving-side convention: the root marker

The face graph alone doesn't say which panel moves. The **`id="root"`** element inside the SVG (a reserved layer in `preview.html`, already parsed) resolves this.

- The region whose polygon contains the root marker's centroid is the **fixed base** — `foldAngle = 0` by definition; it never rotates relative to the piece's local coordinate frame.
- A **breadth-first search** from the root region across fold-adjacent edges produces the fold tree. Each non-root region's parent edge is the fold line between it and the region closer to the root in the BFS. The parent edge's polarity and geometry define the hinge axis for that region.
- In three.js: each region becomes a `THREE.Mesh` (extruded sub-polygon) parented to a `THREE.Group` located at the hinge axis. Rotating the group's `rotation.z` by `foldAngle` (CW positive, consistent with the axle convention) folds that panel and all of its descendants.

**What if there is no root marker?** Fall back: the largest-area region is the root. Emit a yellow banner in `preview.html` so the author knows to add one.

---

## Runtime data shape (TypeScript, computed live)

```typescript
interface FoldEdge {
  polarity: "valley" | "mountain";
  segment: [[number, number], [number, number]]; // SVG-space
  foldAngle: number;      // radians; 0 = flat; set by fold slider or assembly JSON
}

interface Region {
  id: string;             // "region-0", "region-1", ...
  polygon: [number, number][];  // SVG-space closed vertices
  holes: [number, number][][];  // cutout holes inside this region (may be empty)
  isRoot: boolean;
  parentEdge: FoldEdge | null;  // null on root region
  childEdges: { edge: FoldEdge; childId: string }[];
}

interface FaceGraph {
  rootRegionId: string;
  regions: Region[];      // indexed by id
}
```

The `FaceGraph` object is computed by the SVG parser at load time and held in memory. It is not serialized to the sidecar. The `foldAngle` field on each `FoldEdge` is the mutable state that the fold slider (and eventually the assembly JSON) drives.

---

## What regions enable downstream

| Capability | How regions unlock it |
|---|---|
| **F1 — visual fold** (v1b) | Polygon clip → per-region sub-mesh → `THREE.Group` hinge hierarchy → fold slider |
| **F2 — semantic fold** | `FoldEdge.polarity` encodes valley vs. mountain; fold tree encodes crease structure |
| **F3 — experiential fold** | Per-fold slider drives `foldAngle`; BFS ensures descendants follow parent |
| **G1 — transform parenting** | Fixed-base region is the attachment point for glue-joint transforms in the assembly graph |
| **G2 — semantic grouping** | Tab labels in the `labels` layer can be spatially joined to the region polygon that contains them, linking each glue tab to its region |
| **Mesh split for hinge animation** | Each region's `holes` array carries its cutouts; `ExtrudeGeometry` per region, subtracted by holes |

---

## Out of scope in v1

- **3D collision detection** during folding — panels may interpenetrate; no resolution.
- **Paper thickness during fold** — folds are modelled as zero-thickness creases; the 0.4 mm slab thickness does not offset the fold geometry.
- **Multi-fold sequencing** — no constraint on which fold happens before which; all fold sliders are independent.
- **Non-planar fold surfaces** — all fold lines are assumed straight in the SVG plane (no curved or geodesic creases).
- **Glue-tab geometry** — tabs are regions (or sub-regions), but the physical act of gluing (overlap, pressure area) is not modelled.

---

## Known stress case: pendulum arm self-fold

The pendulum arm (§II.C; exact piece ID to be confirmed against `embedded-labels.md`) folds onto itself — the fold line divides the piece into two halves that are mirror-images, and both halves are "the same piece." The question "which half is the moving side?" is answered by whichever half does **not** contain the root marker. This is structurally unambiguous once a root marker is authored.

**Open:** what if the two halves are symmetric and there is no meaningful canonical "fixed" end (e.g., a strip that folds at its midpoint and attaches to the framework at both ends)? This question will be resolved empirically during the pendulum POC. The SPEC will be updated with a resolution rule once the POC produces a concrete answer. Until then, the fallback (largest region = root) applies, and the author should add an explicit root marker to break any ambiguity.

---

## Relation to other docs

- **`SPEC-3D-VIEWER.md`** — the production viewer's hinge step ("If the piece has any folds, the silhouette is partitioned along the fold lines into sub-meshes, each parented to a hinge `Object3D`") is the upstream promise that this spec fulfils. When the viewer lands in M3+, this spec is the implementation contract for that step.
- **The v1b prompt for `preview.html`** (clean-start authoring pending; the original draft was archived 2026-05-03 to `_archive/code-prompts/CODE_PROMPT_preview-html-v1b.md`) — v1b's polygon-cut + adjacency BFS + hinge hierarchy in `preview.html` is the first implementation of this spec. That prompt should reference this document.
- **Pendulum POC track** (`WORKPLAN.md`) — the pendulum arm and bob are the first pieces that will be authored with fold lines populated and a root marker, making them the empirical test of this spec.

---

*Last updated: 2026-05-03 — initial draft. Decisions: live computation (not stored in sidecar); root-marker BFS drives moving-side; `polygon-clipping` (JS) + Shapely (Python) named as the implementation libraries; pendulum self-fold flagged as open stress case for POC validation.*
