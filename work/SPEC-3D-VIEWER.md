# 3D Paper-Clock Viewer — Build Spec

**Status:** draft, ready for review
**Predecessor docs:** `work/auto-trace-test/RESULTS.md`, `work/scripts/RESCAN_FINDINGS.md`
**Source materials:** `source/scans-prepped/` (13 plates), `source/transcriptions/` (5 markdown files)

This spec locks in the production pipeline for turning the cleaned scans of *Make Your Own Working Paper Clock* into an interactive 3D viewer of the assembled clock, with each cut-out piece individually inspectable and cross-referenced to the book's own labels and figures.

The decisions feeding into this spec are settled:

1. The production trace pipeline is **auto-trace + light hand-edit + hand-trace for gutter strips and rectangles** (per `RESULTS.md` and the v2 verification on the pre-processed scans).
2. The pre-processing pass (LAB-luminance flat-field + levels stretch + chroma-aware bleed-through suppression) has been run against all 13 plates, with output in `source/scans-prepped/`. The v2 auto-trace test confirms the four bright-region test pieces (33, 92, 99, 122) now trace cleanly; piece 1 — a thin frame strip — remains in the hand-trace bucket as planned.
3. Per piece, the SVG is split into separate layers: silhouette (the only thing that extrudes), fold lines (valley vs. mountain), letters and labels, and other instructional marks (axle centers, glue-zone hatching, construction dotted lines).

No rescans are required to start the build. The two cosmetic rescan candidates from `RESCAN_FINDINGS.md` (plate L thumb, plate A higher resolution) remain optional and can be deferred without blocking.

## Goals and non-goals

The viewer is a static, single-page web app that lets a curious reader rotate, zoom, and inspect a 3D model of the assembled paper clock. Hovering over any piece highlights it; clicking opens a side panel with the piece number, its embedded labels (lettered glue tabs, fold notation, axle markers), the prose-instruction step in which the piece is first introduced, and a small reference crop of the piece on its source plate. An "exploded" slider fans the assembly outward along its assembly direction so the reader can see how the layers nest. Toggles let the reader hide the case to expose the mechanism, hide the face to expose the hands' carriage, and so on.

Out of scope for v1: simulating the working clock (escapement tick, pendulum swing, gears rotating, hands advancing). The data model and asset pipeline must not preclude this — gear tooth counts and axle relationships are captured in the per-piece JSON — but no animation logic ships in v1.

Also out of scope: a fold-paper authoring tool. The build pipeline is one-way (scan → SVG → 3D) and edits happen in Inkscape/Affinity, not in the viewer.

## Per-piece data model

Each cut-out piece is represented by two files: a layered SVG that captures every printed mark, and a JSON sidecar that captures everything you can't see in the SVG.

### Layered SVG

Authoring convention: one SVG per piece, with these named groups (Inkscape layer names; rendered as `<g inkscape:label="...">`):

| Layer | Contents | Stroke style on plate | Role in 3D |
|---|---|---|---|
| `silhouette` | One closed path: the outer cut-line. | Solid. | Extruded. The only layer that becomes geometry. |
| `cutouts` | Closed paths for interior cut-out windows (e.g., piece 71's center cell, piece 53's pinion hole). | Solid, interior. | Subtracted from the silhouette extrusion. |
| `folds-valley` | Open paths along dashed fold lines. | Dashed. | Decal on the front face; also defines hinge axes for the assembled view. |
| `folds-mountain` | Open paths along plus-sign fold lines. | Plus-sign. | Decal on the front face; also defines hinge axes (opposite sign). |
| `axles` | Point markers (small circles or `+`) at axle/pin-hole centers. | `+` glyph. | Used to align pieces sharing an axle; visually marked as a small recess in the front face. |
| `glue-zones` | Closed paths for hatched glue-reception rectangles. | Hatched fill. | Decal on the front face only; not extruded. |
| `labels` | Text glyphs: piece number, glue-tab letters with subscripts, instruction notes. | Print. | Decal on the front face. |
| `marks-other` | Construction lines, dotted alignment guides, anything not in the above. | Dotted, etc. | Decal on the front face. |

Authoring rules: silhouette must be one path with even-odd fill; if the auto-trace produces multiple disjoint shapes (as on the sawtooth pieces 99, 33), they are merged in Inkscape with a path-union before save. Fold layers carry the fold's polarity in the layer name, never in stroke style — the viewer keys off the layer name. Text in the `labels` layer is preserved as `<text>` (not converted to paths) wherever the auto-trace produced glyph shapes, so the inspect panel can read the label text directly from the SVG.

### JSON sidecar

For each piece N, a sibling `piece-N.json` carrying the data the SVG can't:

```
{
  "id": 33,
  "plate": "G",
  "name": "Motor wheel — gear ring (front)",
  "role": "mechanism / motor-wheel",
  "material": "paper",                     // "paper" | "cardboard-1mm" | "wire" | "knitting-needle-2mm"
  "extrudeMm": 0.2,                        // paper ≈ 0.2 mm; cardboard 1.0
  "axles": [
    { "id": "motor-wheel-axle", "type": "knitting-needle-2mm", "centerMarker": "+" }
  ],
  "connections": [
    { "tab": "a",   "to": 34, "atTab": "a" },
    { "tab": "b₃₄", "to": 34, "atTab": "b" }
  ],
  "folds": {
    "valley":   [{ "id": "fold-1", "hingedSubpieceIds": ["main", "tab-a"] }],
    "mountain": []
  },
  "introducedInStep": "II.B.1 Motor Wheel",   // section in instructions.md
  "figureRefs": ["K/Fig 5", "K/Fig 6", "L/Fig 12"],
  "notes": "Paired with piece 34 (back) and piece 37 (tooth strip). See embedded-labels.md panel G."
}
```

The `connections` array is the spine of the assembly graph; it's compiled from `embedded-labels.md` by hand (one-time pass — the labels are already transcribed). The `figureRefs` are used by the inspect panel to cross-link to the K/L figure plates.

## Authoring pipeline (scan → piece)

For each piece, the steps, roughly in order of automation:

1. **Locate.** A `pieces.csv` index lists every piece with its plate, source-image bbox, and the bucket from `RESULTS.md` (auto-trace clean / auto-trace + edit / hand-trace). The bbox is set once, by hand, from the prepped scan.
2. **Crop.** A short Python script reads `pieces.csv` and produces `work/pieces/NNN/crop.png` from the prepped plate. (Same logic as `auto-trace-test-v2/01_crop.py`.)
3. **Trace.** For pieces in the auto-trace buckets, run `potrace` on the binarized crop. The `auto-trace-test-v2/02_trace.py` pipeline is the starting point; for production, swap pure-Python `potracer` for the native `potrace` binary (50–100× faster; we'll add it to the build environment). Output is a single-layer SVG with all printed marks as one undifferentiated set of paths.
4. **Layer-split.** A second pass classifies each path into one of the canonical layers above by stroke style (dashed → valley fold; plus-sign → mountain fold; etc.) and by area threshold (largest closed path → silhouette; small text-shape paths grouped → labels). Pieces in the "auto-trace + light edit" bucket land in Inkscape at this point for a 30–60 second cleanup; pieces in the "hand-trace" bucket are drawn from scratch over the crop image.
5. **Sidecar.** The JSON is authored once per piece by hand, by reading off `embedded-labels.md` and `instructions.md`. We expect ~120 sidecars; estimate 1–3 minutes each, ≈ 4 hours total.
6. **Validate.** A linter checks: silhouette is one closed path; folds are open paths; every `tab` in `connections` is referenced by some other piece's `atTab`; every `axle.id` referenced is also referenced from at least one other piece (so axles aren't orphaned).

The pipeline is deterministic and re-runnable. If the prepped scan is regenerated (e.g., a rescan is added later), only steps 1–4 need to re-run; the JSON sidecars are stable.

## SVG-to-3D conversion

At viewer load time:

1. **Parse SVG.** Three.js's `SVGLoader` produces `THREE.Shape` objects from each path. The viewer inspects `inkscape:label` to bucket shapes by layer.
2. **Extrude the silhouette.** `THREE.ExtrudeGeometry(silhouetteShape, { depth: extrudeMm, bevelEnabled: false })`. Cutouts go into the shape's `holes` array.
3. **Bake decals.** A 2D canvas is set up at the silhouette's bounding-box resolution. The `folds-valley`, `folds-mountain`, `glue-zones`, `labels`, and `marks-other` layers are rendered into the canvas as flat ink. The canvas becomes a `CanvasTexture` mapped to the front face of the extrusion.
4. **Material.** Front face: cream paper diffuse + the decal texture multiplied in. Back face: plain cream. Edges: slightly darker (paper edge). For pieces marked `cardboard-1mm`, swap the cream for a brown-board diffuse.
5. **Hinges.** If the piece has any folds, the silhouette is partitioned along the fold lines into sub-meshes, each parented to a hinge `Object3D`. The hinge angle is part of the assembly transform (default 0° for a flat development; the assembly JSON sets the actual fold angle when the piece is in place).

The silhouette extrusion approach gives the right look for paper at the resolution we care about (the viewer is 1 m away, the pieces are 1–2 mm thick). We do not model paper bend deformation; folds are sharp creases.

## Assembly model

The clock's assembly graph is a tree of nested `Object3D` groups, with leaves being individual pieces. Top-level groups, in book order:

| Group | Source section | Pieces (representative) |
|---|---|---|
| `framework` | §II.A | 1, 2, 3, 5, 6, 7, 8, 9, 11, 12–17, 19, 20, 21, 22, 25, 27, 28, 29, 30, 31 |
| `wall-bracket` | §II.A | 23, 24, 25, 26 |
| `motor-wheel` | §II.B.1 | 33, 34, 35, 36, 37, 50, 90 |
| `middle-wheel` | §II.B.2 | 39, 50–57, 53, 58 |
| `escapement-wheel` | §II.B.3 | 58, 60, 61–66 |
| `wheel-mounting` | §II.B.4 | 18, 19, 27, 28 |
| `anchor-and-pendulum` | §II.C | 67, 68, 69, 70, 71, 72, 92, 92a, 94, 95, 96, 97, 98, 99, 100 |
| `hands-mechanism` | §II.D | 4, 75, 76, 77, 81, 84, 89, 91, 108, 109 |
| `weight` | §II.E | 101, 102 |
| `face-and-case` | §II.F | 110, 111, 112, 112a, 113–116, 117, 118, 119, 122 |

Each group lives in its own `assemblies/<group>.json` listing the pieces it contains, the local transform of each piece (translation in mm, rotation in radians, fold-angle for hinged pieces), and any axles passing through the group. The viewer composes groups via a top-level `assembly.json` that places each group in clock-coordinate space.

Authoring the transforms: this is the largest hand-authoring effort in the build. The starting positions come from Fig. 13 (the schematic cross-section on plate L), Fig. 1 (frame perspective on plate K), and the prose in §II of `instructions.md`. Each group is positioned, then iterated by hand against the figures. Estimate 2–6 hours per group; 8 groups; ~30 hours total. This is the long pole.

## Viewer behavior

The default view shows the assembled clock face-on, scaled to fit the canvas, with neutral lighting. Standard interactions:

- **Orbit / zoom / pan.** `OrbitControls` from three.js. Damping on. Auto-rotate off.
- **Hover.** The piece under the cursor is outlined (a thin emissive edge) and its number floats above it.
- **Click.** Selects the piece. The inspect side panel opens with the piece's data.
- **Exploded slider.** A range input from 0 (assembled) to 1 (fully exploded). At each value, every group's children translate outward along the group's assembly direction by a per-group factor; hinged sub-pieces unfold to flat. At slider=1, every piece is shown flat in its development form, like the original plates.
- **Layer toggles.** Checkboxes for each top-level group; unchecked groups become invisible (or translucent — see open decision below).
- **Fold-line overlay toggle.** When on, fold-line decals are emphasized (saturated red for valley, blue for mountain) so the reader can see how the development was creased.
- **Reset camera.** Returns to the default front view.

The viewer is keyboard-navigable (Tab cycles selection, arrows orbit, Esc closes inspect panel). Mobile layout: the inspect panel becomes a bottom sheet; pinch zooms.

## Inspect side panel

When a piece is selected, the side panel shows:

- **Header.** Piece number, role name (from JSON `name`), and plate letter with a small thumbnail of the plate, the piece highlighted.
- **Reference crop.** The same `crop.png` used in the trace pipeline, captioned with the prepped-scan filename so the reader can find it on disk.
- **Embedded labels.** The full per-piece entry from `embedded-labels.md`, rendered as Markdown.
- **Folds.** Counts: "3 valley folds, 1 mountain fold." Labeled list.
- **Connections.** Each entry from `connections` rendered as a clickable chip — clicking the chip selects the connected piece.
- **Axles.** Each axle this piece sits on, with the axle's other passengers as clickable chips.
- **Instructions reference.** A blockquote of the relevant paragraph from `instructions.md` (matched by `introducedInStep`), with a "View full step" link that scrolls a separate instructions panel.
- **Figures.** Thumbnails of K/L figures listed in `figureRefs`, click-to-zoom.

The panel is data-driven by `manifest.json` (a build artifact — the union of all per-piece JSONs plus the assembly JSON, plus references into the transcriptions). Nothing in the panel is hand-authored at viewer build time.

## Tech stack

- **Frontend:** TypeScript, Vite, three.js. No React or Vue — the viewer is small enough that vanilla TS with a couple of UI components keeps the bundle lean and the code readable. Tailwind for the inspect panel layout.
- **3D:** three.js `r160`+ for native `SVGLoader` and `ExtrudeGeometry`. `OrbitControls` from `three/addons`.
- **Build:** `pnpm`, `vite`. Deployable as static files; target host is GitHub Pages or any static CDN.
- **Asset pipeline:** Python 3.10+ with Pillow, scikit-image, lxml. Driven by a top-level `Makefile` so each stage (preprocess, crop, trace, layer-split, manifest-build) is a discrete, cacheable target.
- **Linter:** the JSON sidecar linter is plain Python; runs in CI before manifest build.

Native `potrace` will be added to the build environment (the v2 test used pure-Python `potracer` for sandbox compatibility). For local builds we install the system package; for CI, we either install via apt or fall back to `potracer` with the slower runtime.

## File and folder layout

Continuing the existing repo conventions:

```
source/                          (read-only; already populated)
  scans-prepped/                 13 cleaned plate JPGs
  scans-clean/                   pre-prep version, retained as audit trail
  transcriptions/                5 markdown files
  inventory.md
work/
  pieces/                        per-piece authoring (NEW)
    NNN/
      crop.png
      piece-NNN.svg              layered, hand-finalized
      piece-NNN.json             sidecar
  assemblies/                    (NEW)
    framework.json
    motor-wheel.json
    ... (one per group)
    assembly.json                top-level composition
  pipeline/                      (NEW; replaces ad-hoc scripts)
    01-crop.py
    02-trace.py
    03-layer-split.py
    04-validate-sidecars.py
    05-build-manifest.py
    Makefile
  viewer/                        (NEW; the web app)
    index.html
    src/
      main.ts
      scene.ts                   three.js setup, lighting, camera
      pieces.ts                  SVG → mesh
      assembly.ts                group composition, transforms, hinges
      inspect-panel.ts
      ui.ts                      sliders, toggles, hover state
    public/
      manifest.json              build artifact
      pieces/                    per-piece SVG + JSON, copied from work/pieces
      crops/                     per-piece reference PNG
    package.json
    vite.config.ts
  pieces.csv                     master index: piece → plate → bucket → bbox
  RESULTS.md                     (existing) auto-trace test results
  scripts/
    preprocess_scans.py          (existing)
    RESCAN_FINDINGS.md           (existing)
  auto-trace-test/               (existing) v1 tests, retained
  auto-trace-test-v2/            (existing) v2 tests, retained
  SPEC-3D-VIEWER.md              this document
```

## Phasing and milestones

The build is organized so each milestone produces something usable on its own; the work doesn't have to land all at once.

**M1 — Authoring pipeline end-to-end on plate D.** Plate D is the simplest and the cleanest. Trace all 9 pieces, write all 9 sidecars, get the linter passing. Output: `work/pieces/004/` through `work/pieces/092/` complete. Cost: ~6 hours including pipeline coding. Demonstrates the spec is buildable.

**M2 — All pieces traced.** Run the pipeline across plates A–J. Plates K and L are figure references — those go in as plate-image assets, not pieces. Plate M is one piece (122). Estimate: ~25–35 hours of trace + edit + sidecar work. Output: ~120 piece directories under `work/pieces/`, manifest.json builds cleanly.

**M3 — Flat viewer.** Bring up the three.js scene with all pieces rendered flat, in a grid laid out by plate. Hover, click, and inspect-panel work. No assembly transforms yet. Output: viewer is browsable, every piece can be inspected. This is the gut-check that the spec works in 3D before committing to the assembly authoring effort.

**M4 — Assemblies.** Author the per-group transforms, group by group, in approximate book order: framework first (§II.A), then mechanism groups, then face/case. Iterate against Fig. 13 and the prose. Output: clock takes its real shape; exploded view works.

**M5 — Polish and inspect-panel content.** Wire the figure references, instruction-step blockquotes, plate-thumbnail highlighting. Tune lighting and camera defaults. Output: the viewer feels finished.

**M6 (stretch) — Mechanism animation.** Compute gear ratios and angular velocities from tooth counts in `embedded-labels.md`; rotate. Pendulum amplitude/period from rod length. Hands advance on real time. Output: it's a clock.

## Open product decisions

Calling these out so they don't ambush us mid-build. None of them block M1 or M2.

1. **Layer-toggle visual: hide vs. translucent.** When the case is toggled off, does it disappear entirely, or fade to ~20% opacity so the reader still has a spatial reference? Translucent is more informative; "hidden" is faster to read. Recommend translucent with a per-toggle preference.
2. **Aesthetic target: photographic vs. illustrative.** Two coherent looks are available: photographic (textured cream paper with the actual printed labels visible at scale) or illustrative (clean, slightly diagrammatic, edges emphasized for clarity). Photographic feels truer to the book; illustrative reads better in screenshots. Recommend photographic for the viewer, illustrative as a per-session toggle.
3. **Mobile support depth.** Read-only inspect panel on small screens, or full orbit/explode interactivity? Recommend full interactivity with a simplified UI; the viewer is small enough that mobile WebGL handles it.
4. **Hosting.** GitHub Pages off this repo, a separate paper-clock-viewer repo, or self-hosted? GitHub Pages off this repo is simplest and keeps the source close. Need to confirm the public/private split — the source scans stay personal-reference per the README, so the deployed site cannot include `source/scans-prepped/` directly; only the per-piece `crop.png` (which is a derivative work) and the SVGs/JSON ship to production.
5. **Mechanism animation in v1.** The schedule above puts it in M6 stretch. Would you rather pull it forward — say, after M3 — to validate that the gear ratios from `embedded-labels.md` are consistent before sinking time into the full assembly authoring? It's defensible either way.

## Sequence

Once the open decisions above are addressed (or accepted as recommended), the next concrete step is M1: pick plate D, build the pipeline scripts (`01-crop.py` through `04-validate-sidecars.py`), and trace + sidecar all 9 of its pieces. That's the smallest deliverable that proves the spec.
