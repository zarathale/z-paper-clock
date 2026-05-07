---
status: shipped
started: 2026-05-04
shipped: 2026-05-04
owner: Zarathale (Alan)
target: preview-html-face-graph-diagnostics
---

_Shipped 2026-05-04; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._

## What You Are Doing and Why

Add a diagnostic harness to `preview.html` that exposes the face graph computed by `buildFaceGraph` for inspection — JSON dump, 2D debug overlay rendering regions/shared-edges/folds in unique colors, and a structured console summary. **No algorithm change.** Purely additive instrumentation.

This prompt was scoped at the 2026-05-04 11:00 cowork session (see session note). Background: the previous session (2026-05-04 08:15, marker-bound fold ids) shipped a parser change that improved piece 066 from 19 → 5 orphans but left the cylinder folding into shards/slivers. Discussion at session close pivoted to a "shared-edge topology" refactor as the likely next move. When we sat down to write that refactor, the diagnosis went deeper: there are at least two interacting failure modes on 066 (over-broad adjacency from infinite-line cuts, AND phantom strips from co-linear cuts producing spurious regions), and going straight from "patches aren't enough" to "rewrite the algorithm" skips the step where we look at the actual data and find out which failure dominates.

So before committing to shared-edge OR cut-trim OR multi-tag as the algorithm direction, build the harness that lets us *see* what's happening on 066. Compute the shared-edge index (a structure we'd need anyway for shared-edge topology) but use it only to expose the graph for inspection — the real adjacency step keeps its current behavior. Once Alan has looked at 066's actual face graph, the next CODE_PROMPT picks the algorithm with eyes open.

The harness also has a permanent payoff: any future piece whose folds don't render correctly gets the same inspection tools. This isn't throwaway diagnostic code.

## Prerequisites — confirm before starting

- `preview.html` exists at repo root and runs cleanly on `001/001.svg`, `066/066.svg`, `069/069.svg` via drag-drop.
- `polygon-clipping` is already loaded (used in `buildFaceGraph` step 1). No new library.
- The marker-bound fold ids convention is in effect (parsing already populates `marksCentroidsById` and `markerBoundId` on each fold). Don't redo any of that.
- The stray `work/pieces/066/001.svg` was deleted earlier this session. Confirm gone before testing.
- No version bump (preview.html iteration).

## Read These Files First

1. `CLAUDE.md` — top sections + "Marker-bound fold ids" Architectural Decisions row + "Per-element ids inside fold layers" entry in File Naming Conventions.
2. `sessions/2026-05-04-0815_cowork_marker-bound-fold-ids.md` — diagnosis of 066's fold-tagging failure and the pivot that ended the session.
3. `sessions/2026-05-04-1100_cowork_face-graph-diagnostics.md` (filename approximate; this session's note will land at session close) — discussion that produced this prompt: the option space (shared-edge, cut-trim, multi-tag, panels, diagnose-first) and the choice to instrument before committing.
4. `preview.html` lines 623–822 (`parseSVG`) — where `marksCentroidsById` is built and folds get `markerBoundId`.
5. `preview.html` lines 1494–1556 (`extendFoldsToSilhouette`) — the input shape `buildFaceGraph` consumes.
6. `preview.html` lines 1562–2020 (`buildFaceGraph` end-to-end). All of it: cuts, sliver filter, adjacency, root, BFS.
7. `preview.html` wherever the rendered scene's UI lives (search for `addBanner` and the per-piece-load entry path) — to find a good place for a "Dump face graph" button and a "Toggle debug overlay" button.

## Target File Structure Changes

```
z-paper-clock/
├── preview.html                                                       ← update: build shared-edge index, expose face-graph JSON, add 2D debug overlay
├── CODE_PROMPT_preview-html-face-graph-diagnostics.md                 ← update: status flips to shipped on PR open
└── sessions/
    └── 2026-05-04-HHMM_code_preview-html-face-graph-diagnostics.md    ← NEW: ship session note
```

No SVGs, no pipeline scripts, no convention docs touched. The marker-bound fold ids convention stays exactly as documented.

## Numbered Tasks

### 1. Build the shared-edge index inside `buildFaceGraph` (post-sliver-filter)

Insert this between step 4 (sliver filter) and step 5 (adjacency) in `buildFaceGraph`. After `regionMap` is populated and before `const foldEdges = []`. The index is computed but **not yet consumed by step 5** — the adjacency algorithm stays unchanged. We're building the structure so we can dump it.

Polygon-clipping produces matching coordinates for shared seams between adjacent regions; quantize to ~1e-4 viewBox units in the key to absorb float-precision slop.

```js
// ── Step 4.5: Shared-edge index (DIAGNOSTIC ONLY in this prompt) ─────────────
// Index every region edge by canonical endpoint pair. Edges with exactly two
// regions are shared seams — the topological adjacency primitive a future
// algorithm prompt may consume. For now, exposed only via the debug dump and
// overlay; the adjacency algorithm in step 5 below is UNCHANGED.
const QUANT = 1e4;  // multiplier; rounding granularity = 1/QUANT viewBox units
function quantPt([x, y]) { return [Math.round(x * QUANT), Math.round(y * QUANT)]; }
function edgeKey(a, b) {
  const [qa, qb] = [quantPt(a), quantPt(b)];
  const [lo, hi] = (qa[0] < qb[0] || (qa[0] === qb[0] && qa[1] <= qb[1])) ? [qa, qb] : [qb, qa];
  return `${lo[0]},${lo[1]}|${hi[0]},${hi[1]}`;
}

const edgeIndex = new Map();   // key → [{rId, eIdx}, ...]
for (const [rId, region] of regionMap) {
  const n = region.polygon.length;
  for (let i = 0; i < n; i++) {
    const key = edgeKey(region.polygon[i], region.polygon[(i + 1) % n]);
    if (!edgeIndex.has(key)) edgeIndex.set(key, []);
    edgeIndex.get(key).push({ rId, eIdx: i });
  }
}

const sharedEdges = [];   // {regionA, regionB, eIdxA, eIdxB, mid, length, endpoints, key}
for (const [key, entries] of edgeIndex) {
  if (entries.length !== 2) continue;
  const a = entries[0], b = entries[1];
  if (a.rId === b.rId) continue;
  const rA = regionMap.get(a.rId);
  const [ax, ay] = rA.polygon[a.eIdx];
  const [bx, by] = rA.polygon[(a.eIdx + 1) % rA.polygon.length];
  sharedEdges.push({
    key,
    regionA: a.rId, regionB: b.rId,
    eIdxA: a.eIdx, eIdxB: b.eIdx,
    mid: [(ax + bx) / 2, (ay + by) / 2],
    length: Math.hypot(bx - ax, by - ay),
    endpoints: [[ax, ay], [bx, by]]
  });
}
```

### 2. Compute a "would-be-shared-edge-active-binding" preview per fold

In the same diagnostic block (still before step 5 runs), compute for each fold what the shared-edge topology *would* assign as its active hinge if we shipped that algorithm. **This does not affect the actual `foldEdges` output**; it's recorded onto the fold object for the diagnostic dump.

Use the simplest scoring (minimum distance from shared-edge midpoint to fold's authored line, with marker-bound case restricted to the marker's region's shared edges). Don't bother with direction/segment filters here — the goal is to expose the candidate set for inspection, not to settle on the right scoring. The scoring debate is a question for the post-diagnosis prompt.

```js
function ptToFoldLine(px, py, fold) {
  const [fax, fay] = fold.start;
  const dx = fold.end[0] - fax, dy = fold.end[1] - fay;
  const len = Math.hypot(dx, dy);
  if (len < 1e-10) return Infinity;
  return Math.abs((py - fay) * dx - (px - fax) * dy) / len;
}

const sharedByRegion = new Map();
for (const [rId] of regionMap) sharedByRegion.set(rId, []);
for (const se of sharedEdges) {
  sharedByRegion.get(se.regionA).push(se);
  sharedByRegion.get(se.regionB).push(se);
}

// Annotate each fold with its top-3 candidate shared edges (sorted by
// distance ascending). For marker-bound folds, candidates are restricted
// to the marker region's shared edges.
for (const fold of extendedFolds) {
  let pool = sharedEdges;
  let markerRegionId = null;
  if (fold.markerBoundId) {
    const c = marksCentroidsById.get(fold.markerBoundId);
    if (c) {
      for (const [rId, region] of regionMap) {
        if (pointInPolygon(c.x, c.y, region.polygon)) { markerRegionId = rId; break; }
      }
      if (markerRegionId) pool = sharedByRegion.get(markerRegionId) || [];
    }
  }
  const scored = pool.map(se => ({ se, dist: ptToFoldLine(se.mid[0], se.mid[1], fold) }));
  scored.sort((a, b) => a.dist - b.dist);
  fold._diagCandidates = scored.slice(0, 3).map(({ se, dist }) => ({
    sharedEdgeKey: se.key,
    regionA: se.regionA, regionB: se.regionB,
    midpoint: se.mid, endpoints: se.endpoints, length: se.length,
    distToFoldLine: dist
  }));
  fold._diagMarkerRegionId = markerRegionId;
}
```

### 3. Build the diagnostic dump payload at the end of `buildFaceGraph`

Just before `buildFaceGraph` returns, attach the diagnostic payload to the return object so the caller can dump or render it. **Don't change the existing return shape** — add a single new key `_diag` whose absence is benign.

```js
const diag = {
  pieceFile: parsed && parsed.filename ? parsed.filename : null,
  viewBox: parsed && parsed.viewBox ? parsed.viewBox : null,
  silhouettePolygon: silhouette,
  regions: Array.from(regionMap.values()).map(r => ({
    id: r.id,
    polygon: r.polygon,
    area: polyArea(r.polygon),
    vertexCount: r.polygon.length,
    isRoot: r.isRoot,
    parentId: r.parentId,
    edgeTags: r.edgeTags.map(et => et.tag)
  })),
  folds: extendedFolds.map(f => ({
    id: f.id,
    pathId: f.pathId,
    layer: f.layer,
    markerBoundId: f.markerBoundId,
    defaultAngle: f.defaultAngle,
    authoredStart: f.authoredStart,
    authoredEnd: f.authoredEnd,
    extendedStart: f.start,
    extendedEnd: f.end,
    sharedEdgeCandidates: f._diagCandidates || [],
    markerRegionId: f._diagMarkerRegionId || null
  })),
  foldEdges: foldEdges.map(fe => ({
    pathId: fe.pathId,
    layer: fe.layer,
    polarity: fe.polarity,
    passive: fe.passive,
    regionA: fe.regionA,
    regionB: fe.regionB,
    segment: fe.segment,
    sourceFoldId: fe.sourceFold && fe.sourceFold.id || null
  })),
  sharedEdges: sharedEdges.map(se => ({
    key: se.key,
    regionA: se.regionA, regionB: se.regionB,
    midpoint: se.mid, endpoints: se.endpoints, length: se.length
  })),
  marksCentroidsById: Array.from(marksCentroidsById.entries()).map(([id, c]) => ({
    markerId: id, x: c.x, y: c.y
  })),
  summary: {
    regionCount: regionMap.size,
    foldCount: extendedFolds.length,
    foldEdgeCount: foldEdges.length,
    activeFoldEdgeCount: foldEdges.filter(fe => !fe.passive).length,
    passiveFoldEdgeCount: foldEdges.filter(fe => fe.passive).length,
    sharedEdgeCount: sharedEdges.length,
    rootId: rootId,
    rootSource: rootSource,
    sliverFiltered: sliverCount,
    totalUnknownEdgeTags: totalUnknown
  }
};

return { rootId, regions: regionMap, foldEdges, _diag: diag };
```

(Adjust the existing return statement at the bottom of `buildFaceGraph` accordingly. Currently it returns `{ rootId, regions: regionMap, foldEdges }`; just add `_diag`.)

### 4. Add diagnostics buttons to the left panel

Insert a new `#diagnostics-section` block in the panel HTML, **between `#rotation-section` and `#help`** (around line 168 in the current `preview.html`). The structure mirrors the other panel sections.

```html
<div id="diagnostics-section">
  <div class="diag-row" style="display:flex; gap:6px;">
    <button id="dumpFaceGraphBtn" disabled
            title="Download the most recent face graph as JSON">Dump face graph</button>
    <button id="toggleFaceGraphOverlayBtn" disabled
            title="Toggle the 2D face-graph diagnostic overlay over the 3D view">Show overlay</button>
  </div>
</div>
```

Add a single CSS rule next to the other section rules in the existing `<style>` block:

```css
#diagnostics-section { display:flex; flex-direction:column; gap:6px; }
```

JS wiring (place near the other `document.getElementById(...)` lines around 222–227, and the click handlers near the existing button wiring):

```js
const dumpFaceGraphBtn         = document.getElementById('dumpFaceGraphBtn');
const toggleFaceGraphOverlayBtn = document.getElementById('toggleFaceGraphOverlayBtn');

function downloadFaceGraphDump() {
  const fg = window.__lastFaceGraph;
  if (!fg || !fg._diag) {
    addBanner('No face graph available — load a piece first.', 'warn');
    return;
  }
  const blob = new Blob([JSON.stringify(fg._diag, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const piece = (fg._diag.pieceFile || 'unknown').replace(/[^A-Za-z0-9_-]/g, '_');
  const ts = new Date().toISOString().replace(/[:.]/g, '-');
  const a = document.createElement('a');
  a.href = url; a.download = `face-graph-${piece}-${ts}.json`;
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

dumpFaceGraphBtn.addEventListener('click', downloadFaceGraphDump);
```

Both buttons start `disabled`. Enable both at the end of `renderScene` (around line 2063+) when `parsed` and the face graph are present, and disable them again at the top of `renderScene` while a new build is in flight. The overlay button's click handler is wired in Task 5; here, just enable/disable.

Set `window.__lastFaceGraph = faceGraphResult;` immediately after the `buildFaceGraph` call inside `renderScene` (search for the existing call site there). That single line is what the dump button relies on.

### 5. Add a 2D face-graph diagnostic overlay

The overlay is **a 2D diagnostic chart drawn over the 3D view**, not a projective alignment with it. The 3D scene is rendered with arbitrary orbit-camera state and may be tilted/rotated; the overlay sits in viewBox-space (top-down, flat) and shows the face graph as its own visualization. To make this clear and stop users expecting alignment, the overlay carries a semi-opaque dark backdrop so the 3D view fades behind it while the overlay is on.

**Mount point.** Append the overlay element to `#canvas-host` (so it inherits the canvas region's positioning and resizes with it). Insert it AFTER `renderer.domElement` (also a child of `#canvas-host`, appended at line 243). The overlay is a single `<svg>` element styled to fill its parent:

```js
const canvasHost = document.getElementById('canvas-host');
const overlaySvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
overlaySvg.id = 'face-graph-overlay';
overlaySvg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
overlaySvg.style.cssText = [
  'position:absolute', 'inset:0',
  'width:100%', 'height:100%',
  'pointer-events:none',
  'background:rgba(26,26,26,0.88)',  // matches body bg #1a1a1a at 0.88 opacity
  'display:none',                      // toggled to 'block' on activation
].join(';') + ';';
canvasHost.appendChild(overlaySvg);
```

Set the SVG `viewBox` to match the loaded piece's viewBox each time the overlay is re-rendered. **Y-axis stays SVG-native (y-down)** — viewBox-space — to match how the rest of the diagnostic data is keyed. (The 3D scene flips Y elsewhere; do not mirror that in the overlay.)

**Render layers**, drawn in this order so labels stay on top:

1. **Silhouette polygon** — thin outline, `stroke:#888; stroke-width: ${diagLen * 0.001}; fill:none`.
2. **Regions** — each filled `<polygon>` with a distinct color: `hsl(${(i * 137.508) % 360}, 55%, 62%)` (golden-angle spread), `fill-opacity:0.55`, stroke a darker variant `hsl(... , 45%, 35%)`, `stroke-width: ${diagLen * 0.0008}`.
3. **Shared edges** — `<line>` per entry in `_diag.sharedEdges`, `stroke:#bbb; stroke-width: ${diagLen * 0.0015}; stroke-linecap:round`.
4. **Fold authored segments** — `<line>` per entry in `_diag.folds`, color by layer (`folds-valley` → `#7af`, `folds-mountain` → `#f87`), `stroke-width: ${diagLen * 0.002}; stroke-dasharray: ${diagLen * 0.005} ${diagLen * 0.003}`. Use `authoredStart` / `authoredEnd`, not the extended endpoints.
5. **Top-1 shared-edge candidate per fold** — for each fold with `_diagCandidates[0]`, draw the candidate edge as a thicker overlay (`stroke-width: ${diagLen * 0.003}`) in green (`#7d7`) if `_diagMarkerRegionId` is non-null AND that region is one of `_diagCandidates[0].regionA` / `regionB` (good binding), amber (`#fc6`) otherwise. Layer this on top of the gray shared-edge line so the suspect/good signal stands out.
6. **Marker centroids** — `<circle r="${diagLen * 0.004}" fill="#fff">` per `_diag.marksCentroidsById` entry, with a `<text>` label offset by `(${diagLen * 0.006}, 0)`, `font-size:${diagLen * 0.012}; fill:#fff; paint-order:stroke; stroke:#000; stroke-width:${diagLen * 0.001}; stroke-linejoin:round`. The paint-order trick gives the text a thin black outline so it's readable against any region color.
7. **Region id labels** — `<text>` at each region's centroid (compute via simple polygon-centroid formula). Smaller font (`font-size:${diagLen * 0.008}`), same paint-order black-stroke trick.

(Compute `diagLen` once from the viewBox: `Math.hypot(vb.w, vb.h)`. All sizes scale relative to it so 069's 3417×3342 viewBox and 001's 28975×4871 viewBox both look readable.)

**Legend panel.** Add a small fixed-position HTML legend on top of (sibling to) the overlay SVG, also a child of `#canvas-host`, top-right:

```js
const legend = document.createElement('div');
legend.id = 'face-graph-legend';
legend.style.cssText = [
  'position:absolute', 'top:8px', 'right:8px',
  'background:rgba(0,0,0,0.65)', 'color:#ddd',
  'padding:6px 10px', 'border-radius:4px',
  'font-size:11px', 'line-height:1.5',
  'pointer-events:none', 'display:none',
  'max-width:260px',
].join(';') + ';';
legend.innerHTML = `
  <div style="font-weight:600;margin-bottom:4px">Face-graph diagnostic</div>
  <div>regions = unique colors (arbitrary)</div>
  <div><span style="color:#bbb">━</span> shared edges</div>
  <div><span style="color:#7af">- - -</span> valley folds &nbsp; <span style="color:#f87">- - -</span> mountain folds</div>
  <div><span style="color:#7d7">━</span> top candidate (good binding)</div>
  <div><span style="color:#fc6">━</span> top candidate (suspect)</div>
  <div style="margin-top:4px;color:#888">2D viewBox-space; not aligned to 3D camera.</div>`;
canvasHost.appendChild(legend);
```

**Toggle behavior.** State variable `window.__faceGraphOverlay = false;` initially. The `toggleFaceGraphOverlayBtn` click handler:

```js
toggleFaceGraphOverlayBtn.addEventListener('click', () => {
  window.__faceGraphOverlay = !window.__faceGraphOverlay;
  const on = window.__faceGraphOverlay;
  overlaySvg.style.display = on ? 'block' : 'none';
  legend.style.display     = on ? 'block' : 'none';
  toggleFaceGraphOverlayBtn.textContent = on ? 'Hide overlay' : 'Show overlay';
  if (on && window.__lastFaceGraph) renderFaceGraphOverlay(window.__lastFaceGraph._diag);
});
```

Re-render the overlay on each successful `buildFaceGraph` call when `__faceGraphOverlay` is on. Implement `renderFaceGraphOverlay(diag)` to clear `overlaySvg.replaceChildren()` and rebuild. Pure function of `_diag` — no external state.

**On window resize.** The overlay's CSS-driven `inset:0; width:100%; height:100%;` makes it follow `#canvas-host`'s size automatically. SVG `preserveAspectRatio="xMidYMid meet"` keeps the diagram letterboxed without distortion. No explicit resize handler needed.

### 6. Add a structured console summary on each face-graph build

After `buildFaceGraph` completes, log a summary block to the console (always, not gated by debug flag — preview.html already runs in console-open authoring mode). Format:

```
[face-graph] piece=<filename> regions=<N> folds=<F> active-edges=<A> passive-edges=<P> shared-edges=<S> slivers-filtered=<X>
[face-graph] folds:
  ✓ fold-tab-c (marker-bound: tab-c) → marker-region=region-7 → top-shared-edge=region-7↔region-12 dist=0.4
  ✓ fold-landing-h65 (marker-bound: landing-h65) → marker-region=region-3 → top-shared-edge=region-3↔region-9 dist=0.2
  ✗ fold-tab-b (marker-bound: tab-b) → marker-region=region-5 → top-shared-edge=region-5↔region-11 dist=27.1  [SUSPECT: distance > 5u]
  ⊘ valley-7 (unidentified) → top-shared-edge=region-2↔region-6 dist=0.3
  …
```

Where:
- ✓ = marker-bound, top candidate's distance is small (< 5 viewBox units, configurable)
- ✗ = marker-bound, top candidate's distance is large (likely the fold's hinge wasn't found in the marker's region's shared edges — suspect)
- ⊘ = unidentified fold (no marker binding)

Use `console.log` with `console.group`/`console.groupEnd` so the per-fold list is collapsible.

## Verification Checklist

1. `preview.html` opens cleanly in Chrome/Firefox without console errors against `001/001.svg`, `066/066.svg`, `069/069.svg`. The existing rendering and behavior on each piece is **unchanged** (same banners, same fold count in animation, same visual result).

2. **Dump button works.** Click "Dump face graph" after loading each test piece. Downloaded JSON parses cleanly (`jq . face-graph-066-*.json | head -100`) and contains every field listed in Task 3.

3. **Debug overlay renders correctly.**
   - Toggle on while 066 is loaded. The 3D view fades behind the dark backdrop; visible above it: regions in distinct golden-angle-spread colors with id labels, shared edges as `#bbb` strokes, valley folds as blue dashed lines, mountain folds as red dashed lines, marker dots with labels (white text with thin black outline so they read against any region color), top-candidate highlights in green (good binding) or amber (suspect).
   - Top-right corner shows the legend panel.
   - Button text flips to "Hide overlay" while active. Toggle off — overlay and legend hide; button returns to "Show overlay".
   - Resize the window — overlay stays letterboxed (no distortion) thanks to `preserveAspectRatio="xMidYMid meet"`.
   - Drag-load a different piece while the overlay is on — re-renders for the new piece (new viewBox, new region colors, new candidate edges).

4. **Console summary prints on every load.** Check browser console for the structured `[face-graph]` block. On 066, expect roughly:
   - regions=20–35
   - folds=21
   - shared-edges count proportional to regions (typically 1.5–2× region count)
   - Several ✓ entries and several ✗ or ⊘ depending on actual data — that's exactly what we want to see in this prompt's payoff.

5. **No regression in interactive use.** The Fold-all slider, per-fold sliders (if any), and 3D orbit/zoom all keep working. Overlay being on/off doesn't affect them (overlay has `pointer-events: none`).

6. **Re-run on 069.** It should mostly print ✓/⊘ entries with small distances (069's folds have unique geometry, so candidates should bind well). If 069 surfaces ✗ entries, that's diagnostic info worth flagging in the session note.

## What NOT to Change

- **`buildFaceGraph` algorithm.** Steps 1–7 (cuts, sliver filter, adjacency, root, BFS) keep their current behavior exactly. We're adding a parallel computation (the shared-edge index + per-fold candidate annotation) and exposing it. The actual `foldEdges` output is unchanged.
- **Marker-bound fold id parsing.** Already correct.
- **Viewer / extrusion / texture / axle rotation.** Unchanged — overlay is additive, doesn't replace the 3D view.
- **Convention docs.** No CLAUDE.md / LAYER-CONVENTIONS.md / SPEC changes from this prompt. The diagnostic harness is implementation, not convention.
- **The `passive` field's semantics.** That cleanup (split into `kind: 'driven' | 'structural'`) was discussed in cowork as orthogonal to this prompt — it'll roll into whichever algorithm refactor follows the diagnosis. Don't touch it here.

## Manual tests

After merge, Alan runs preview.html locally and works through the test bench:

| Piece | Action | What to look for |
|---|---|---|
| 069 | Load, dump JSON, toggle overlay on | Every fold ✓ with small distance. Overlay shows clean panel coloring, all shared edges accounted for. **Baseline of "looks healthy."** |
| 001 | Load, dump JSON, toggle overlay on | Auto-renamed `fold-tab-a/-a1/-a2/-a3` cluster: see how many of them produce ✗ vs ✓. Overlay shows whether marker regions resolve correctly despite the duplicate ids. |
| 066 | Load, dump JSON, toggle overlay on | **The point of this prompt.** Look at: (a) how many of the 17 marker-bound folds produce ✓ vs ✗, (b) whether shards/slivers in the colored region map correspond to "phantom strips" between co-linear cuts, (c) whether top-candidate shared edges actually look like the right hinges, (d) whether some marker regions have NO shared edges (true sliver outcome). |

Goal: Alan posts a summary back in cowork with what 066's debug overlay shows. That summary picks the next CODE_PROMPT — shared-edge with tightened picker (algorithm-only, expecting cut-trim later), shared-edge AND cut-trim together, or some other direction the data surfaces.
