---
date: 2026-05-01
start_time: "23:00"
end_time: "TBD-late"
mode: cowork
participant: Zarathale (Alan)
source: retroactive — reconstructed from context summary of two prior interrupted sessions + this session
---

## Goal

Pick up from the interrupted 3D build (summarized in `2026-05-01-0200_cowork_069-svg-export-and-scan-texture-pivot.md`) and deliver a working three.js viewer for piece 069: scan-as-texture, all panels including corner flaps and extensions, 1mm paper thickness slab geometry.

---

## What Was Done

### Viewer build — initial pass (5 panels, wrong scan)

Built `work/pieces/069/piece-069-viewer.html` using three.js r128 with OrbitControls. UV seam continuity confirmed working — texture wraps smoothly across fold creases at hinge lines. User confirmed: "hinge action works beautifully."

**Issues surfaced from first screenshots:**
- Corner gaps at box corners (corner flaps intentionally excluded — wrong call)
- Colored marks (yellow, blue, magenta) visible baked into the texture — wrong source: `inbox/069.png` is the Affinity export with all layers merged flat

### Source file verification

`source/pieces/069.png` confirmed as the correct texture source:
- Pixel-identical to the scan embedded in `inbox/069.svg` (mean diff 0.00, max diff 0 across all RGBA channels)
- Clean: max R-G channel diff = 6 across all opaque pixels (colored marks would be 200+)
- `inbox/069.png` is the merged Affinity export (scan + mark layers flattened) — do not use as texture

`inbox/069.svg` version verified: all expected layers present (Background, folds-valley × 8 paths, marks × 11 ellipses, axles × 1 ellipse, folds-mountain absent as expected — not yet authored). Both files pushed from Mac/Affinity 2026-05-01 22:53.

### User scope decisions

Alan explicitly expanded scope for the rebuild:

> "there's never a case when I want them hidden. let's just build it all together"

→ All 13 panels included: BASE, LEFT WALL, LEFT EXT, RIGHT WALL, RIGHT EXT, TOP WALL, TOP EXT, TL CORNER, TR CORNER, BOT WALL, BOT EXT, BL CORNER, BR CORNER.

> "want to address the thickness of the paper, e.g. 1mm thickness or similar to a sturdy cardstock… thickness of a piece (not a panel within a piece)"

→ `THICKNESS_MM` constant at top of file (piece-level, not panel-level). Each panel is a slab: front face (scan texture), back face (cream), 4 edge strips (cream). Scale: 1 mm / 4.14 mm-per-unit ≈ 0.241 three.js units. Live slider 0.3–4.0 mm in the UI.

### Rebuild — geometry and UV bug passes

**Bug 1 — UV vertex order (texture shear):**
`buildUVs()` had TL, BL, TR, BR. PlaneGeometry vertex buffer order is TL, TR, BL, BR (outer loop: row top→bottom; inner loop: column left→right). Swapping TR↔BL caused the texture to shear diagonally across triangle boundaries, misaligning the scan to the geometry. Fixed to TL, TR, BL, BR.

**Bug 2 — doubled panels:**
Initial `addPanel()` calls built 13 slabs; then `rebuildSlabs()` was called on init with an empty `slabRefs` list (nothing to remove), adding 13 more. 26 slabs total. Restructured to a single `buildAllSlabs()` function that exclusively owns the slab lifecycle. No separate initial-build call.

**Bug 3 — cream back face bleeding through alpha holes (DoubleSide):**
`creamMat` used `THREE.DoubleSide`, causing the back face of each slab to render from both directions. Through the alpha-transparent regions of the scan front face (alphaTest: 0.1 discards background pixels, no depth write), the cream back face was visible from the camera-facing side.

Alpha coverage scan confirmed partial transparency on several panels — this is the physical box net shape, not a crop error:

| Panel | Coverage |
|---|---|
| BASE, walls, BL/BR corner | 99–100% |
| LEFT EXT, RIGHT EXT | ~46–56% |
| TOP EXT, BOT EXT | ~44–50% |
| TL CORNER | 38% |
| TR CORNER | 44% |

Fix: split `creamMat` into `backMat` (FrontSide — invisible from camera-facing side after rotation.y=π) and `edgeMat` (DoubleSide — needed for visibility when orbiting). The transparent cutouts in the tabs now correctly show the dark background rather than cream bleed-through.

### Final state

`work/pieces/069/piece-069-viewer.html` — self-contained (~355 KB), `source/pieces/069.png` embedded as base64 data URL. Features:
- 13 panels with correct UV mapping (scan wraps continuously across fold hinges)
- Fold slider 0–100% (π/2 rotation per hinge)
- Thickness slider 0.3–4.0 mm (live rebuild of slab geometry)
- OrbitControls (orbit, zoom, pan)
- Two directional lights + ambient

User response: "this is really close!"

---

## Open Questions

- `folds-mountain` layer not yet authored on piece 069 — check the book for any mountain fold on this piece.
- Tabs c–g: which specific pieces do they connect to? (Needed for M4 assembly graph; not needed now.)
- Two spec revisions still queued (held since session A):
  - Layer model (marks / tab-X / landing-X naming convention)
  - Scan-as-texture material model + "downsample-for-viewer" pipeline stage

---

## Next-Session Handoff

1. Open `work/pieces/069/piece-069-viewer.html` in Chrome, verify fold animation and texture alignment look correct at all fold angles.
2. If the viewer looks good, write the two queued spec revisions into `work/SPEC-3D-VIEWER.md`.
3. Consider what a second test piece would look like — ideally a flat/non-folding piece from a different section to validate the workflow generalizes before building the pipeline.

---

## Pickup — 2026-05-01 (post-usage-cap restart)

Session resumed after the previous run hit a group usage cap mid-discussion. Reconstructed state from `sessions/restart-prompt2.rtf`:

**What happened after "this is really close!":** Alan posted screenshots showing thin white outline rectangles tracing slab perimeters on the four extension panels (top-ext, bot-ext, left-ext, right-ext) and the corner panels. Claude diagnosed two stacked causes:

1. `source/pieces/069.png` has a 1-px opaque-white border baked in at row 0 and row 801 (Affinity export artifact). When a slab samples its outer-edge UV, it lands on those white pixels — bright top/bottom edges of the rectangles.
2. The four ext panels were defined to the SVG viewBox edge, so the slab geometry extends well past the actual paper silhouette into alpha=0 territory. The front face is alpha-discarded there, but each slab still has cream `edgeMat` ribbons around its perimeter — those ribbons trace the empty rectangle outlines.

Claude drafted a three-edit proposal: (1) zero the alpha on the PNG's 1-px outer border at texture-load time in JS, (2) tighten ext panel bounds to the post-strip alpha bbox + add four outer fold pivots + reparent the ext panels onto them, (3) two-phase fold animation (walls 0–50%, tabs 50–100%).

**Alan course-corrected hard:** the white-border-strip plan was Claude's wrong instinct, not Alan's complaint. Pieces are hand-drawn, hand-cut, hand-edited — there will inconsistently be white margins or stray ink. Baking in a "strip the white" rule would scrub real artifact. Alan asked: *why* is the slab sampling that color, could it be a constant instead, does it matter once the scan renders correctly? And: prioritize refactoring to pull from the SVG; settle that first.

**Reframed root cause:** slab silhouette ≠ paper silhouette. Once the slabs are sized to the actual paper inside each fold-bounded region, the outer-edge sample lands on real paper (whatever color it is, ink and rough cuts and all) and the cream-ribbon outlines disappear by construction. The white border is a symptom, not the disease.

**SVG-driven refactor — what `inbox/069.svg` gives us:**

- `viewBox="0 0 3417 3342"` → SVG_W / SVG_H, no hardcoding
- `<image>` (embedded scan) + `matrix(4.166667,0,0,4.166667,0,0)` → the texture, in viewBox coords already
- `<g id="folds-valley">` 8 line paths → all 8 fold positions (BX1/BX2/BY1/BY2 + OX1/OX2/OY1/OY2) derived, not hardcoded
- `<g id="marks">` 11 ellipses (tab-a..tab-g, landing-a/b/h/i) → tab/landing positions for the M4 assembly graph
- `<g id="axles">` 1 ellipse `anchor-pivot` → pivot point at BASE center
- `<g id="folds-mountain">` empty on 069 (convention slot for other pieces)

Important authoring fact surfaced from re-grepping styles: `folds-valley` strokes are bright green `#3d0`, `marks` are bright yellow `#fff000`, `axles` are bright magenta `#f500ff`. Those are Alan's authoring colors to make layers obvious in Affinity — they are **not** the intended visual treatment for a render. So a "rasterize the whole SVG to a canvas" texture path would paint bright green over the scan's own dashed fold lines, yellow over tab dots, magenta over the printed `+`. Audit-mode visualization, not faithful render. Don't do that by default.

**Settled directions for the rebuild:**

- Standalone viewer that works on any SVG in the repo, not piece-069-specific.
- Polygon-traced paper-shaped slabs driven by alpha bounds inside each fold-bounded region (not rectangles).
- Texture: scan only (extract the embedded `<image>` from the SVG, use as texture). Faithful render — printed dashes / tab letters / `+` already live in the scan.
- 3D pivot sphere always visible at the axle position (it's a *position*, not a printed mark — useful from any orbit angle).
- Fold-line and mark overlays deferred to a follow-up (would be useful for catching authoring mistakes without re-opening Affinity, but not minimum-viable).

**Open decisions still on the table when the session capped out:**

- Where the standalone tool lives in the repo. Claude leaned `work/viewer-prototype/index.html` (clearly distinct from the eventual `work/viewer/` Vite production app per `SPEC-3D-VIEWER.md`); alternatives discussed were `work/tools/svg-3d-preview/index.html` and a repo-root `preview.html`.
- How the viewer picks an SVG. Claude leaned file picker / drag-drop (works on `file://`, zero ceremony) over URL params (which need a local server).
- The follow-up question that didn't get answered: should the viewer also be useful for catching SVG authoring mistakes (misplaced fold, missing mark) without re-opening Affinity? If yes, fold/mark overlays earn their seat in the first cut rather than later.

**Repo state at pickup:** no edits landed since the "this is really close!" state. `work/pieces/069/piece-069-viewer.html` is still the 13-panel rectangular-slab build with the white-rectangle outline issue. None of the proposed three edits were applied. Nothing is committed for the SVG-driven refactor — it's all design discussion above the line.

This session note stays open. Next move waits on Alan's call.

---

## Option 3 viability test on `inbox/069.svg`

Settled architectural directions: standalone viewer at repo root; file picker / drag-drop; no fold/mark overlays in v1; render flat with a warning when sidecar missing; SVG/JSON disagreement renders what it can and warns; per-piece JSON sidecar lives at `work/pieces/NNN/piece-NNN.json` per SPEC; panel data model starts simple (polygon + parent + hinge + fold direction).

Open architecture question Alan asked to test: does Option 3 (fully derived panel cut — silhouette ∩ all fold-valley + fold-mountain lines, treating each line as an infinite-line cutter) work cleanly on `inbox/069.svg`? Run the cut on the actual SVG and find out.

**SVG inspected.** viewBox 3417 × 3342. Embedded `<image>` (820 × 802 scan, scale matrix 4.166667). Three layers: `folds-valley` (8 paths), `marks` (11 ellipses), `axles` (1 ellipse at 1772, 1729). No `folds-mountain` (consistent with prior note).

**Fold-line shapes surprised me.** Six of the eight paths are short segments spanning a single panel boundary (paths 0/1 vertical at OX1/OX2 in y ∈ [BY1, BY2]; paths 4/5/6/7 horizontal at BY1/BY2/OY2/OY1 in x ∈ [BX1, BX2]). The other two — paths 2 and 3 — are *long* verticals at x = BX1 and x = BX2 that span y ∈ [OY1, BY2], crossing **two** panel-pair boundaries each (TL_CORNER↔TOP_WALL **and** LEFT_WALL↔BASE for path 2; mirror for path 3). The fold lines do NOT span the full silhouette.

**Cut algorithm.** Marching-squares on the alpha of `source/pieces/069.png`, scaled to viewBox coords → silhouette polygon (3015 vertices, valid, area 6.17M sq-units). Each fold line extended to silhouette-bbox + 100 margin (functioning as an infinite-line cutter). Sequential `shapely.ops.split` for each cut, accumulating regions. Result: **24 regions total**.

**Of those 24, 13 are real panels (all correctly classified by centroid)** and 11 are tiny slivers at fold-line intersections (max sliver area 7184 sq-units; smallest real panel is TL_CORNER at 92K — a 12× gap). Filter "drop regions < 1% of largest" cleanly keeps the 13 panels and discards every sliver.

Final per-panel summary (label, centroid, area, polygon vertex count):

| Panel | Centroid | Area | Verts |
|---|---|---|---|
| BASE | (1760, 1746) | 1,630,104 | 8 |
| T-WALL | (1760, 914) | 683,542 | 5 |
| B-WALL | (1760, 2571) | 666,841 | 5 |
| L-WALL | (820, 1746) | 569,828 | 50 |
| R-WALL | (2693, 1746) | 557,232 | 5 |
| T-EXT | (1749, 514) | 402,576 | 490 |
| B-EXT | (1763, 2950) | 361,830 | 473 |
| L-EXT | (431, 1751) | 313,051 | 422 |
| R-EXT | (3077, 1758) | 309,053 | 428 |
| TR | (2575, 924) | 97,976 | 353 |
| TL | (952, 912) | 92,503 | 242 |
| BL | (820, 2571) | 233,243 | 22 |
| BR | (2693, 2571) | 227,952 | 5 |

Vertex counts tell a story. BASE and the four walls are 5–50 verts (paper is rectangular, polygon traces the rect with a few fold-intersection points). The four corners and four ext tabs have 200–500 verts because their paper shapes are tapered/rounded — and the polygon now traces real paper edges, not slab rectangles. **This is exactly what kills the cream-rectangle outline issue from the previous viewer.**

Asymmetry between TL/TR (~95K) and BL/BR (~230K) is faithful, not a bug — TL/TR have rounded shoulders that taper to ~38–44% of the corner rectangle (matches the alpha-coverage table from the previous session note), BL/BR are full-coverage rectangles.

Test artifacts in `outputs/069-test/`:
- `analyze.py`, `cut.py`, `verify.py` — the diagnostic scripts
- `01-silhouette-and-folds.png` — silhouette outline + fold lines, before cuts
- `02-cut-result.png` — first cut pass (24 regions, slivers visible)
- `03-verification.png` — final 13 panels labeled, axle dot in BASE center

**Empirical conclusion:** Option 3 is viable on 069 with a 1% area filter to drop slivers. Zero per-piece authoring beyond the SVG layers Alan already draws. Per-panel polygon traces real paper edge. The JSON sidecar can carry only the fold tree (root, parent pointers, fold direction) — possibly even that derives from conventions (root = panel containing axles ellipse; parent = neighbor across nearest fold line; direction = layer name).

**Caveats worth knowing before this becomes the production path:**

- The 1% threshold is calibrated to 069. If a piece has a legitimate small panel (a tiny tab at <1% of base), the threshold misses it. Probably want "drop regions whose vertices all sit within Δ of a single fold line" instead — that's the actual sliver signature, not absolute size.
- Slivers appear because fold lines aren't perfectly axis-aligned (path 2 has 5.6 px horizontal drift across 1662 px vertical — 0.34% slope) and the silhouette is traced from a 820×802 PNG at viewBox-unit resolution (each PNG pixel = 4.17 viewBox units). Rasterizing the SVG at full viewBox resolution would shrink slivers further.
- Path 2 / path 3 (long verticals spanning two panel-pair boundaries) work as infinite-line cuts because the silhouette doesn't extend across them outside the spans they're authored for. That's *geometric coincidence* of how this specific piece is laid out, not a guaranteed property. A piece where two non-adjacent regions sit on the same x or y as a fold line in another panel would cut spuriously.

Status open: viable on 069, not yet validated on any other piece. Next-piece test would confirm or reveal where the algorithm needs more sophistication.

---

## Option 3 viability test on `inbox/066.svg` (re-export)

Initial 066 inbox file (timestamp 01:16) had only an empty `axles` group — no fold layers. Alan re-exported at 03:36 with the layers populated. Re-checked.

**066 is structurally very different from 069.** It's a long thin tube net for the pendulum-blade casing (§II.C anchor-pendulum). viewBox 2963 × 18867 (aspect 1:6.36). 22 fold lines (20 valley + 2 mountain). 16 mark ellipses + 1 rect. Empty axles. PNG is 100% opaque so silhouette source isn't alpha — it's the orange `#e6611a` path inside an unnamed group in the SVG body (34 vertices tracing the actual paper outline).

**Silhouette source needed a branch.** Parsed the orange path's `M+l` commands manually, since `find_contours` on a 100%-opaque alpha mask returns a 4-vertex bounding rectangle, not the actual paper. The viewer prototype will need this fallback: if PNG alpha is fully opaque (or near-fully), look for a closed colored path in the SVG body instead. Easy to detect — sum of opaque pixels / total pixels > 0.99.

**Cut result.** 22 fold lines extended to infinite-line cutters → 106 regions. 1% area filter → 22 real panels + 84 slivers. Sum-of-real-panels covers 98.13% of silhouette; slivers are 1.87% in aggregate.

The 22 panels resolve cleanly into a 7-section tube net: each section is a horizontal strip divided by 2 vertical fold lines into 3 columns (left edge tab + main face + right edge tab), plus 1 small bottom-edge tab. Vertical fold lines aren't fixed — they jog (paths 11, 8, 9, 2 are slightly diagonal) where the tube changes width between sections. The 2 mountain folds at y=8082 and y=11183 bracket the central section.

Topology summary:
- Section 1 (y ∈ [172, 4650]): top large strip
- Section 2 (y ∈ [4650, 6896])
- Section 3 (y ∈ [6896, 8082]) — narrower, diagonal verticals
- Section 4 (y ∈ [8082, 11183]) — central, between two mountain folds
- Section 5 (y ∈ [11183, 12374]) — narrower, diagonal verticals
- Section 6 (y ∈ [12374, 14995])
- Section 7 (y ∈ [14995, 18428]) — bottom large strip
- Bottom tab (y ∈ [18428, 18867])

Vertex counts are low (5–9 per panel) — paper is rectangular at every section, no rounded shoulders or tapered shapes like 069's corners and ext tabs.

**What I learned that's worth knowing:**

1. **The 1% sliver threshold is getting fragile.** On 069, the gap between smallest real panel (TL_CORNER 92K) and largest sliver (7K) was 12×. On 066, the gap is only ~2× (smallest real panel 88K, largest sliver 46K). If a piece has a legitimately narrow glue tab — say a 30-px-wide strip at the paper edge — it could fall below the threshold and be dropped as a sliver. For production, the sliver filter should switch to "drop regions whose vertices all sit within Δ of a single fold line" (geometric signature, scale-invariant) rather than "drop regions below k% of largest" (size-based, threshold-dependent).

2. **Mountain folds work the same as valley folds for cutting purposes.** The cut algorithm doesn't care about fold direction — both layers contribute infinite-line cutters and the result is the same. Valley vs. mountain is *animation* metadata (which way the panel rotates around the hinge), not *segmentation* metadata. The JSON sidecar records direction via the SVG layer name; the cut treats them identically.

3. **Diagonal "verticals" still cut as near-vertical lines.** Paths 11 (498→502, dx/dy=4/1208 ≈ 0.3% slope), 2, 8, 9 are slightly diagonal. The "infinite line through this segment" extension correctly handles them — the cut follows the line direction. No special-case logic needed.

4. **Path-d parsing matters.** The silhouette path uses absolute M followed by relative `l` segments, no Z. The path parser had to handle that correctly. Any other M/m/L/l/H/h/V/v/Z/z combination not yet supported. For production, use a real SVG path library or expand the parser. (Not a blocker — Affinity exports tend to be consistent within the same authoring file — but worth flagging.)

5. **Per-piece authoring state varies.** Even within the recent `inbox/` batch (065/066/067/069/070/071), only 069 had `folds-valley` populated in the original inbox push. 066 got it after a deliberate authoring pass. The viewer must detect what's authored and degrade gracefully — render flat with banner when fold layer missing, render axle marker only if axles populated, etc.

6. **The cut algorithm is surprisingly robust across very different topologies.** 069 = 8 fold lines, box net, 13 panels. 066 = 22 fold lines, tube net, 22 panels. Same code (silhouette → infinite-line cut → area filter) works on both with no piece-specific tuning beyond the silhouette source branch (alpha vs. SVG path).

Test artifacts in `outputs/066-test/`:
- `run.py` — the diagnostic script
- `066-verify.png` — labeled verification image (22 colored panels, valley folds in red, mountain folds in blue)

Status: Option 3 validated on 069 (box-net, 13 panels) and 066 (tube-net, 22 panels). Two pieces, two very different topologies, same algorithm produces clean results. Confidence is now reasonably high that the approach generalizes. Open caveats: 1% sliver threshold is fragile; per-piece authoring state varies; SVG path parser is minimal. None of these are blockers for the prototype — they're known-issue items to track as Option 3 ships.

---

## Architectural decisions settled in this session

After the 066 validation, conversation moved to nailing down conventions so the prototype can be built without a JSON sidecar. Decisions reached:

**Empty-layer graceful handling.** All optional layers skip cleanly when empty or absent.

| Layer | Empty / absent behavior |
|---|---|
| `folds-valley` | No valley folds. If `folds-mountain` also empty/absent → render flat with banner. |
| `folds-mountain` | No mountain folds. (Same flat-fallback if valley also empty.) |
| `marks` | No mark indicators rendered (not in v1 anyway). |
| `axles` | No pivot marker. No special root rule based on axle. |
| `thickness` (new, proposed) | Default 1mm. |
| `root` (new, proposed) | Fall back to "largest panel by area" heuristic. |

No piece-specific code paths. Each layer is read independently and contributes what it has.

**Per-fold angle via path id, layer-default fallback.** Alan agreed to the regex-based encoding:

- Path id matching `^fold(?P<sign>[-+])(?P<deg>\d+(?:\.\d+)?)$` → that's the signed fold angle in degrees.
- Anything else (no id, `fold` alone, `fold-anchor`, `tab-c`, etc.) → fall back to layer default: `folds-valley` → −90°, `folds-mountain` → +90°.
- Layer is just visual organization in Affinity when the id encodes an explicit angle; it's the doctrine for the default case.
- Examples: `fold-60` (acute valley), `fold+45` (mountain), `fold+135` (obtuse), `fold-90` (explicit, same as default if in valley).

Alan does NOT have pre-known angles for non-90° folds. He needs to *find* them by tweaking sliders interactively. So the prototype needs per-fold UI control and write-back of the discovered angles into the SVG path ids.

**Architectural shift — SVG as the single source of truth.** The viewer is no longer just a *viewer*; it's an authoring tool with read+write to SVG. Implications:

- Loading: parse all layers, apply ids, render.
- Editing: per-fold angle slider (UI proposal: click a fold line in the 3D view → select → angle slider replaces global animation slider for that fold; click empty space to deselect). Thickness slider (single, piece-level — already exists in 069 viewer, needs write-back).
- Saving: "Export updated SVG" button triggers a browser download of the modified SVG. User overwrites the source file manually. Surgical edit pattern: only attributes that changed are touched (path `id` for fold angles, `<text>` content inside `<g id="thickness">` for thickness). Path `d`-strings, embedded image data, layer structure all preserved untouched.
- File-system write-in-place isn't on the table for v1 (would require `showOpenFilePicker({mode:'readwrite'})`, Chrome-only, not universal).

**Thickness encoding (proposed, not yet validated).** Optional `<g id="thickness">` layer with a single hidden `<text>` child carrying the millimeter value:

```xml
<g id="thickness" inkscape:label="thickness">
  <text x="0" y="0" visibility="hidden">1.5</text>
</g>
```

Defaults to 1mm if the layer is missing or empty.

**Root identity (proposed, not yet validated).** Optional `<g id="root">` layer with a single marker (ellipse, rect, or path) inside the panel that should be the tree root. Viewer finds the marker, identifies which polygon contains it, uses that as the root. If `root` is empty or missing, fall back to "root = largest panel by area."

**Animation phasing in v1.** Single global slider 0–100% drives every fold from 0 to its target angle proportionally. Sequenced phasing (069's "walls then tabs") deferred — would be a future syntax extension on the path id (e.g., `fold-90.2` for "phase 2") but not designed now.

## Open question — Affinity SVG round-trip durability

The whole write-back model depends on Affinity preserving custom layers (`thickness`, `root`) and custom attributes through edit + re-export. Alan needs to do a 60-second test:

1. Hand-add a `<g id="thickness">` layer and a `<g id="root">` layer (with placeholder content) to an SVG.
2. Open in Affinity, re-export.
3. Inspect the re-exported file: did both layers survive? Did the text content / marker survive?

If both survive: write-back model is real, JSON sidecar truly optional.
If something gets stripped: adjust the encoding, or accept a minimal JSON sidecar for the affected metadata.

This is the most important de-risking step before any code lands.

## Open scope question

Two ways to ship the prototype:

1. **v1 read-only first, then v2 write-back as a follow-up.** Faster to first useful preview; lets Alan find right angles by tweaking and remember/author them manually for now; smaller increment.
2. **v1+v2 together.** Single ship with full read+write loop; bigger build; higher risk of late discoveries.

Claude leans (1). Alan to confirm.

## Next-session handoff

1. Run the Affinity round-trip test (or get Claude one re-exported sample with a hand-placed `thickness` and `root` layer). This unblocks the write-back encoding decision.
2. Confirm v1-only or v1+v2 scope for the prototype.
3. Decide what — if anything — to do about the convention-driven fold tree validation on 069 (was queued before the architecture conversation expanded; may be worth doing as part of v1 implementation rather than as a separate test).
4. After 1+2 settled: write `CODE_PROMPT_preview-html-v1.md` (or `v1+v2`) for the actual prototype implementation. File goes at repo root as `preview.html` per Alan's earlier call. Includes drag-drop, polygon panels via Option 3, axle marker (when populated), per-fold angle control, thickness control, scan-only texture, optional Export SVG button (if v2).
5. Per CLAUDE.md split, the prototype could be built directly in Cowork (precedent from the 069 viewer) or written as a CODE_PROMPT for Code mode. Lean: Cowork-direct since the file is a single self-contained HTML at root.

## Session ended out-of-context

Conversation ran long; Alan asked to close session quickly without finishing the v1/v2 scope question or the round-trip test. All architecture work captured above; nothing in the implementation path has been touched (no edits to `work/pieces/069/piece-069-viewer.html`, no `preview.html` created, no code committed).
