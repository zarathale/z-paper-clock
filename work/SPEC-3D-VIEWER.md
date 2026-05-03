# 3D Paper-Clock Viewer — Build Spec

**Status:** draft, ready for review
**Predecessor docs:** `work/_archive/m1-plate-d-phone/auto-trace-test/RESULTS.md`, `work/_archive/m1-plate-d-phone/RESCAN_FINDINGS.md` (both archived 2026-04-30 with the gen-1 phone scans they document; conclusions still hold)
**Source materials:** `source/pieces/` (per-piece archive, lossless PNG, populating from chunk-and-crop capture per `source/SCAN-INTAKE-CHECKLIST.md`), `source/scans-chunks/` (multi-piece chunk captures kept as recovery references), `source/transcriptions/` (5 markdown files, scan-independent)

This spec locks in the production pipeline for turning the cleaned scans of *Make Your Own Working Paper Clock* into an interactive 3D viewer of the assembled clock, with each cut-out piece individually inspectable and cross-referenced to the book's own labels and figures.

The decisions feeding into this spec are settled:

1. The production trace pipeline is **auto-trace + light hand-edit + hand-trace for gutter strips and rectangles** (per `RESULTS.md` and the v2 verification on the pre-processed scans).
2. The pre-processing pass (LAB-luminance flat-field + levels stretch + chroma-aware bleed-through suppression) was developed against gen-1 (handheld phone) scans and is now archived. Under chunk-and-crop, pre-processing becomes per-piece if/when needed — flat-bed gen-2 captures are cleaner and the gen-1 parameters likely over-correct. The gen-1 v2 auto-trace test confirmed bright-region pieces traced cleanly; piece 1 — a thin frame strip — remains in the hand-trace bucket as planned. (Original gen-1 results live in `work/_archive/m1-plate-d-phone/auto-trace-test-v2/RESULTS.md`.)
3. Per piece, the SVG is split into separate layers: silhouette (the only thing that extrudes), fold lines (valley vs. mountain), letters and labels, and other instructional marks (axle centers, glue-zone hatching, construction dotted lines).

**Note (2026-04-30):** the original "no rescans required" stance was reversed twice in the same day. First reversal: after M1 plate-D output revealed gutter warp from the gen-1 phone scans, a full plate-by-plate rescan on a flat-bed home scanner was queued as **M0.5**. Second reversal (later that day): the home scanner can't fit a whole plate. The plate-rescan plan was retired and replaced with **chunk-and-crop** — capture multi-piece chunks (filename listing the COMPLETE pieces inside, ascending), archive the chunks to `source/scans-chunks/` as recovery references, and hand-crop each piece in editing software to a lossless `source/pieces/NNN.png`. The pipeline reads `source/pieces/` directly. Gen-1 sources are archived to `source/_archive/phone-scans-2025/`. The two earlier "cosmetic rescans" (plate L thumb, plate A higher-resolution) are subsumed by the gen-2 capture standard in `source/SCAN-INTAKE-CHECKLIST.md`. M0.5 is the active onboarding milestone (see `ROADMAP.md`).

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
| `marks` | Construction lines, dotted alignment guides, anything not in the above. | Dotted, etc. | Decal on the front face. |

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
  "function": {                            // OPTIONAL; populated only on §II.B + §II.C pieces (see below)
    "type": "gear",                        // "gear" | "compound" | "escape_wheel" | "anchor" | "pendulum" | "hand_arbor"
    "toothCount": 60,                      // rim tooth count; required for gear / compound / escape_wheel
    "pinionToothCount": null,              // pinion tooth count on same arbor for compound gears; null otherwise
    "axleCentroidSvg": [123.4, 78.9],      // SVG coordinates of the axle hole, registered against `axles` markers
    "drives": 39                           // piece id this gear drives next; null for terminal pieces (escape wheel, anchor, pendulum)
  },
  "introducedInStep": "II.B.1 Motor Wheel",   // section in instructions.md
  "figureRefs": ["K/Fig 5", "K/Fig 6", "L/Fig 12"],
  "notes": "Paired with piece 34 (back) and piece 37 (tooth strip). See embedded-labels.md panel G."
}
```

The `connections` array is the spine of the assembly graph; it's compiled from `embedded-labels.md` by hand (one-time pass — the labels are already transcribed). The `figureRefs` are used by the inspect panel to cross-link to the K/L figure plates.

The `function` block is **optional and only present on §II.B (gear train) + §II.C (anchor / pendulum / escapement) pieces** — the ~25–30 mechanism pieces whose geometry has to satisfy the ticking constraint. It captures the *intended* mechanism values without modifying the SVG: the trace stays artifact-faithful with all its human-drawn, human-scanned imperfections; the `function` block records what the page meant. The anchor unit is **escape-wheel advance per tick** — one tick = the escape wheel rotates `2π/toothCount` rad, and every other gear's rotation per tick is derived from the chain via the `drives` references. The book's stated period in `instructions.md` is a sanity check on the chain, not a primary input. Per resolved product decision #5, the M2 gear-ratio validation script reads `function` blocks (see Phasing). Pieces outside §II.B + §II.C have no `function` block — framework, hands, weight, face, and case sidecars stay purely artifact-faithful. Hand rotation rates inherit from the gear chain at animation time and don't need their own block. (See CLAUDE.md "Architectural Decisions" → *Faithful trace + functional sidecar* for the full statement.)

## Authoring pipeline (chunk → piece)

For each piece, the steps, roughly in order of automation:

1. **Capture.** Multi-piece chunks scanned on a flat-bed home scanner; chunk filename lists the COMPLETE pieces inside, ascending (e.g., `33_37_40_41_50.jpeg`). Chunks land in `source/scans-chunks/` as recovery references. See `source/SCAN-INTAKE-CHECKLIST.md`.
2. **Crop (manual).** Each piece is hand-cropped from its chunk in editing software (Affinity / Photoshop / equivalent) and saved as a lossless `source/pieces/NNN.png` (three-digit zero-padded; letter variants `092a.png`, `112a.png`). The per-piece archive is the pipeline's input — there is no programmatic crop stage. The piece-scan ingest skill (in progress at `.claude/skills/piece-scan-ingest/`; see `ROADMAP.md` M0.5.2) validates the per-piece archive against `pieces.csv` and surfaces filename or image-health issues. Read-only — never modifies `pieces.csv`.
3. **Trace.** For pieces in the auto-trace buckets, run `potrace` on the binarized per-piece PNG. Implementation: `work/pipeline/02-trace.py` (shipped in M1, slated for repoint in M0.5.6 to read `source/pieces/NNN.png` directly). Production uses the native `potrace` binary (50–100× faster than the pure-Python `potracer` fallback). Output is a single-layer SVG with all printed marks as one undifferentiated set of paths.
4. **Layer-split.** A second pass classifies each path into one of the canonical layers above by stroke style (dashed → valley fold; plus-sign → mountain fold; etc.) and by area threshold (largest closed path → silhouette; small text-shape paths grouped → labels). Pieces in the "auto-trace + light edit" bucket land in Inkscape at this point for a 30–60 second cleanup; pieces in the "hand-trace" bucket are drawn from scratch over the per-piece PNG.
5. **Sidecar.** The JSON is authored once per piece by hand, by reading off `embedded-labels.md` and `instructions.md`. We expect ~120 sidecars; estimate 1–3 minutes each, ≈ 4 hours total.
6. **Validate.** A linter checks: silhouette is one closed path; folds are open paths; every `tab` in `connections` is referenced by some other piece's `atTab` (one-directional connections opt out via `reciprocal: false`); every `axle.id` referenced is also referenced from at least one other piece (so axles aren't orphaned).

The pipeline is deterministic and re-runnable from the per-piece archive onward. Re-cropping a piece (e.g., to fix a tight border) only needs steps 3–4 to re-run; the JSON sidecars are stable. **Historical note:** under the gen-1 (phone-scan) era, step 2 was a programmatic crop driven by per-piece bbox fractions in `pieces.csv` (`work/pipeline/01-crop.py`). Bbox columns were dropped from `pieces.csv` in the chunk-and-crop pivot (2026-04-30) and `01-crop.py` is slated for archival. The `pieces.csv` schema is now `id, plate, section, bucket, status, notes`.

## SVG-to-3D conversion

At viewer load time:

1. **Parse SVG.** Three.js's `SVGLoader` produces `THREE.Shape` objects from each path. The viewer inspects `inkscape:label` to bucket shapes by layer.
2. **Extrude the silhouette.** `THREE.ExtrudeGeometry(silhouetteShape, { depth: extrudeMm, bevelEnabled: false })`. Cutouts go into the shape's `holes` array.
3. **Bake decals.** A 2D canvas is set up at the silhouette's bounding-box resolution. The `folds-valley`, `folds-mountain`, `glue-zones`, `labels`, and `marks` layers are rendered into the canvas as flat ink. The canvas becomes a `CanvasTexture` mapped to the front face of the extrusion.
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
| `face-and-case` | §II.F | 110, 111, 112, 112a, 113–116, 117, 118, 119, 121 |

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
source/                          (read-only after intake; reference archive)
  pieces/                        per-piece source archive: NNN.png, lossless, NNN[a].png; pipeline input
  scans-chunks/                  multi-piece chunk captures kept as recovery references; saved here directly from the scanner
  scans-raw/                     legacy plate-oriented raw (kept; mostly unused)
  scans-clean/                   legacy plate-oriented clean (kept; mostly unused)
  scans-prepped/                 legacy plate-oriented prepped (kept; mostly unused)
  transcriptions/                5 markdown files (scan-independent)
  inventory.md
  SCAN-INTAKE-CHECKLIST.md       chunk-and-crop capture + QC standard
  _archive/
    phone-scans-2025/            gen-1 (handheld phone) raw + clean + prepped, archived 2026-04-30
work/
  pieces/                        per-piece working folder; one folder per piece; populated as authoring proceeds
    NNN/
      NNN.af                     authoring file (Affinity Designer; the editable source)
      NNN.svg                    latest export (preview.html / pipeline / viewer all read this)
      NNN.json                   sidecar
  assemblies/                    (NEW; populates in M4)
    framework.json
    motor-wheel.json
    ... (one per group)
    assembly.json                top-level composition
  pipeline/                      Python pipeline (M1 era; M0.5.6 reshape pending)
    01-crop.py                   ARCHIVED — bbox-driven plate-slicing stage, retired in chunk-and-crop pivot
    02-trace.py                  M0.5.6: repoint to read source/pieces/NNN.png directly
    03-layer-split.py            M0.5.6: align with new trace input
    04-validate-sidecars.py
    05-build-manifest.py
    Makefile
  viewer/                        (NEW; populates in M3)
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
      crops/                     per-piece reference PNG (sourced from source/pieces/)
    package.json
    vite.config.ts
  pieces.csv                     master index of all 123 pieces; schema id, plate, section, bucket, status, notes
  scripts/
    build_master_list.py         generator for pieces.csv from embedded-labels.md
    preprocess_scans.py          gen-1-era pre-processing; per-piece re-tuning if needed under chunk-and-crop
  _archive/
    m1-plate-d-phone/            (archived 2026-04-30) gen-1 M1 outputs: pieces/, auto-trace-test/, auto-trace-test-v2/, RESCAN_FINDINGS.md, RESULTS.md
  SPEC-3D-VIEWER.md              this document
```

## Phasing and milestones

The build is organized so each milestone produces something usable on its own; the work doesn't have to land all at once.

**M1 — Authoring pipeline end-to-end on plate D.** *Shipped against gen-1 (phone) scans 2026-04-30; outputs archived to `work/_archive/m1-plate-d-phone/`.* Traced 11 plate-D pieces (4, 10, 18, 19, 26, 29–32, 91, 92), wrote 11 sidecars, validator passing (with a `reciprocal: false` flag added for one-directional connections). Cost: ~6.5 hours including pipeline coding. Demonstrated the spec is buildable. The pipeline stages built in M1 will be re-run against the gen-2 per-piece archive once M0.5 (chunk-and-crop onboarding + pipeline reshape) closes.

**M2 — All pieces traced.** Run the pipeline across plates A–J on the gen-2 per-piece archive. Plates K and L are figure references — those go in as plate-image assets, not pieces. Plate M is one piece (121). Estimate: ~25–35 hours of trace + edit + sidecar work. Output: ~120 piece directories under `work/pieces/`, manifest.json builds cleanly. Includes a gear-ratio validation sub-task per resolved decision #5.

**M3 — Flat viewer.** Bring up the three.js scene with all pieces rendered flat, in a grid laid out by plate. Hover, click, and inspect-panel work. No assembly transforms yet. Output: viewer is browsable, every piece can be inspected. This is the gut-check that the spec works in 3D before committing to the assembly authoring effort.

**M4 — Assemblies.** Author the per-group transforms, group by group, in approximate book order: framework first (§II.A), then mechanism groups, then face/case. Iterate against Fig. 13 and the prose. Output: clock takes its real shape; exploded view works.

**M5 — Polish and inspect-panel content.** Wire the figure references, instruction-step blockquotes, plate-thumbnail highlighting. Tune lighting and camera defaults. Output: the viewer feels finished.

**M6 (stretch) — Mechanism animation.** Compute gear ratios and angular velocities from tooth counts in `embedded-labels.md`; rotate. Pendulum amplitude/period from rod length. Hands advance on real time. Output: it's a clock.

## Product decisions (resolved 2026-04-30)

All five product decisions called out in the original draft are now resolved. See `ROADMAP.md` "Resolved product decisions" for the full resolution table; the questions and resolutions are summarized here.

1. **Layer-toggle visual: hide vs. translucent.** **Resolved: translucent (~20% opacity) as the default behavior, with a single global "hide instead" switch in a settings menu.** Per-toggle 3-state UI rejected. Original recommendation was translucent with per-toggle preference; the global-switch model is simpler.
2. **Aesthetic target: photographic vs. illustrative.** **Resolved: ship illustrative first in M3 (flat viewer); iterate toward photographic in M5 (polish) if time allows. No runtime toggle.** Original recommendation was photographic-with-illustrative-toggle; reversed because M3's job is the geometry gut-check and a runtime toggle doubles material/lighting work.
3. **Mobile support depth.** **Resolved: defer mobile entirely. Desktop-only for v0.1.0; mobile becomes a Post-M5 milestone.** Original recommendation was full mobile interactivity in v1; reversed because hobby-project audience is desktop-first and shipping sooner is the priority.
4. **Hosting.** **Resolved: GitHub Pages off this repo (the repo is public). Source-vs-derivative split is enforced by what gets copied into the build artifact, not by repo-splitting.** The deployed site contains only per-piece `crop.png`, SVGs, and JSON — `source/scans-prepped/` stays in-repo as personal reference but is not republished as a deployed asset.
5. **Mechanism animation in v1.** **Resolved: animation stays in M6 stretch. A gear-ratio validation script is added as a sub-task of M2 (all pieces traced)** so transcription tooth-count inconsistencies surface before M4 (assemblies) work begins. Animation itself depends on M4's transforms anyway, so pulling animation forward wasn't useful; the data validation is the value.

## Sequence

M1 shipped against gen-1 phone scans on 2026-04-30 and is archived. The next concrete step is **M0.5** — chunk-and-crop onboarding (populating `source/pieces/`) and a small pipeline reshape (archive `01-crop.py`, repoint `02-trace.py` at `source/pieces/`, update the Makefile target chain). Running in parallel since 2026-05-01 is **M0.6** — the `preview.html` authoring/QA tool (see next section). After M0.5 closes, **M2** runs the pipeline across all plates against the gen-2 per-piece archive. See `ROADMAP.md` for the milestone breakdown.

## Authoring/QA preview tool (`preview.html`)

While the production viewer described above lives at `work/viewer/` and ships in M3+, the build leans on a separate tool at `preview.html` (repo root) for authoring and QA today. **preview.html** is a single self-contained HTML file that loads a per-piece SVG via drag-drop and renders the paper silhouette as a 3D extruded slab with the embedded scan as the front-face texture. It runs from `file://` — double-click to open, no dev server, no build step. It's the working surface where new SVG conventions get test-driven, and it's the daily check that "this piece traces correctly and the layers parse the way we think they do" before the production pipeline ever runs.

The tool entered the repo on 2026-05-02 (v1a foundation) and accumulated cut-layer parsing, texture-flip + back-face fixes, a perf pass (render-on-demand), thickness extrusion correctness, and axle rotation through the rest of the day. Its detailed milestone breakdown lives in `ROADMAP.md` M0.6.

### What it consumes

A single per-piece SVG, loaded by piece id from the canonical home `work/pieces/NNN/NNN.svg` (M0.6.14, queued) — with legacy drag-drop retained for ad-hoc inspection of any SVG outside the canonical tree. The SVG carries the embedded scan PNG (typically as `<image>` referenced through `<use xlink:href="#_ImageN">`, the pattern Affinity Designer exports) and uses the canonical layered structure documented in CLAUDE.md's File Naming Conventions. The tool reads:

| Layer | What the tool does with it |
|---|---|
| `silhouette` (with `cutaway` / `cutaway-N` children) | Extracts the cut polygon. Tier 1 of the silhouette source chain. |
| `cutouts` (sibling of silhouette, with `cutout-N` children) | Reserved; not yet consumed. Will be subtracted from the slab when the cutouts pass lands. |
| `folds-valley` / `folds-mountain` | Parses each fold path (`M..l` or `M..L`) to start / end coords. Currently parsed and counted but not rendered as hinges (v1b territory). |
| `axles` | Each `<ellipse>` / `<circle>` → axle marker. An optional `id="north"` element inside the same layer defines the +0° orientation cue. |
| `root` | Optional centroid marker (ellipse / circle / rect / path). Reserved for future fold-tree rooting. |
| `thickness` | Optional `<text>` node giving thickness in mm. Falls back to 0.4 mm (cardstock-typical). |

The tool is read-only — it never writes back to the SVG, and never modifies anything under `source/` or `work/`. Authoring slips surface as yellow / red banners in the side panel rather than silent render glitches.

### Silhouette source chain

The cut polygon is resolved through three priority tiers, with a banner at every fallback so authoring misses are loud:

1. **`<g id="silhouette">` layer** — the canonical authored cut. Parser walks descendants (Affinity wraps children in an unnamed `<g>`; the wrapper is transparent). `cutaway` / `cutaway-N` ids → silhouette polygon; `mask` / `mask-N` ids → ignored visual frame; anything else → `console.warn` so typos don't disappear.
2. **PNG alpha** — marching squares + segment chaining at α = 0.5 if the embedded scan has any transparency. Yellow banner when this kicks in.
3. **Largest colored path heuristic** — last resort, for fully-opaque PNGs without an authored silhouette layer. Yellow banner. Excludes metadata layer ids and authored cut-layer ids so the heuristic never mistakes a `mask` rect for the silhouette.

The chain was settled in `sessions/2026-05-02-1500_cowork_preview-html-cut-layer-spec.md` and shipped via `CODE_PROMPT_preview-html-cut-layer.md`.

### Current feature set

**Slab rendering.** The silhouette polygon is built into a `THREE.Shape`, extruded as a front cap (`THREE.ShapeGeometry` + scan-textured `MeshStandardMaterial`, `FrontSide`) + back cap (same shape, cream `BackSide` so it's only visible from −Z) + custom `BufferGeometry` side walls (cream `DoubleSide`). UV mapping uses `(vx / VB.w, 1 - vy / VB.h)` — the `1 -` Y-flip pairs with three.js's default `flipY: true` on textures so the visual top of the scan lands on the geometric top of the slab.

**Thickness control.** A slider runs 0.3–4.0 mm. Default is whatever the SVG's `thickness` layer gives, falling back to 0.4 mm (cardstock-typical). Slider changes debounce a slab rebuild at 80 ms. The thickness value flows directly into three.js as mm = three.js units; `MM_PER_UNIT` is the viewBox-units → mm scale, derived from the embedded scan dimensions assuming 600 DPI (verified at ~613 effective DPI on piece 002).

**Axle rotation.** Pieces with a populated `axles` layer get a Rotation slider (−180° to +180°, **CW positive** by clock convention — three.js's CCW-positive `rotation.z` is negated at the slider boundary). The slab pivots around the active axle (`axles[0]`; multi-axle support deferred until a piece needs it). Each authored axle renders as a 1 mm-diameter shiny silver cylinder (metalness 0.9, roughness 0.25), positioned **outside** the rotation pivot so it stays fixed in world space — matching the physical clock where the axle wire is mounted to the framework and the piece rotates around it. The future bearing (knitting-needle stub glued to the piece) will render **inside** the pivot when authoring data arrives.

**Orientation cue.** An optional `id="north"` element inside `<g id="axles">` defines the +0° direction via the (active-axle → north) vector. It renders as a brass-gold sphere (color `0xb89e5b`) **inside** the rotation pivot, so it visualises the current angle relative to the as-authored 0°. The two materials (silver-cylinder framework, brass-gold sphere passenger) are deliberately distinct so they read as separate roles rather than as a single "marker."

**Performance.** Render-on-demand: `renderer.render()` only fires when the scene or camera changed. OrbitControls' `change` event sets a `needsRender` flag; programmatic mutations call `requestRender()`; `controls.update()` returning truthy while damping is settling also triggers a render. Pixel ratio is capped at 2 (Retina + 4K externals can hit 3+, which makes the fragment shader 2.25× more expensive for no perceptible quality gain on a static slab). Slab + axle teardown disposes geometries and materials; the scan texture is cached on the `Image` so repeated thickness rebuilds don't re-upload.

**Diagnostics.** Every load logs viewBox dimensions, silhouette vertex count + area, fold counts, root presence, thickness + source, axle count, and `MM_PER_UNIT` to the console. Banners surface authoring misses in the side panel.

### What's not yet there

The tool ships v1a + cut-layer + texture-flip + back-face-mirror + perf + thickness fix + axle rotation as of 2026-05-02. **v1b is queued** in `CODE_PROMPT_preview-html-v1b.md`: polygon cutting (silhouette × N fold lines → N+1 panels via `polygon-clipping`), adjacency BFS (panels → fold tree rooted at the root-marker panel), per-fold UI sliders + a global fold slider, hinge hierarchy in three.js, and live fold animation. The polygon-clipping library is already loaded via CDN; the `<div id="fold-controls">` shell is present as a placeholder. v1b's prompt is currently `status: draft` and depends on tightening against v1a's actual function signatures before flipping to `ready-for-code`.

Other deferred work, in rough priority order:

- **Source-of-truth piece-id loader (M0.6.14).** Today the tool only loads SVGs via drag-drop from arbitrary paths. With the 2026-05-03 filesystem restructure, every piece has a canonical home at `work/pieces/NNN/NNN.svg` — the tool should grow a piece-id input (text field with autocomplete, or dropdown populated from the directory listing) that loads `work/pieces/NNN/NNN.svg` directly, plus a "reload" button for the iterate-fast workflow after a fresh export from Affinity. A nice-to-have: also read `work/pieces/NNN/NNN.json` when present and surface `function`-block contents in the side panel. Drag-drop stays as a fallback for ad-hoc inspection of SVGs outside the canonical tree. Spec'd in `CODE_PROMPT_preview-html-source-of-truth.md`.
- **Cutouts subtraction.** The `cutouts` layer is parsed-aware-of but not yet subtracted from the slab. A piece like 71 (with a center cell) renders as a solid slab today. The convention is locked in; the implementation isn't.
- **Multi-cutaway slabs.** Pieces with `cutaway-1`, `cutaway-2`, … currently render only the first with a banner. Multi-slab support is a v1b+ concern.
- **Rotated / skewed `<use>` transforms.** The scan-image transform parser reads `matrix(sx, 0, 0, sy, tx, ty)` only; rotation / skew components (b, c) are silently dropped (`TODO(070)` in code).
- **UV offsets from `<use>` `x` / `y` / `imageScale`.** Front-face UVs assume the PNG covers `[0, VB.w] × [0, VB.h]` exactly; ~7 px slip on 067, sub-pixel on 069 (`TODO(uv-offsets)` in code).

### Path forward — preview.html vs. `work/viewer/`

The original SPEC scoped the production viewer at `work/viewer/` (TypeScript + Vite + three.js + Tailwind, deployable to GitHub Pages, M3 milestone). preview.html started as a single-piece authoring/QA prototype distinct from that production viewer.

The split is no longer obvious. preview.html now carries the production silhouette parser, the cut-layer convention, the thickness model, the axle / north convention, the textured-slab render, and a real-world performance budget. Most of what M3 needs to ship for one piece exists today inside preview.html. The remaining production-viewer surface (per-piece manifest, multi-piece grid layout, hover + click + inspect panel, layer toggles, GitHub Pages deploy) is integration and UX work, not new rendering primitives.

**Open question (May 2026): does preview.html graduate into `work/viewer/`, or stay a separate authoring/QA tool while `work/viewer/` is built fresh in TS / Vite?** Three plausible directions:

1. **Port preview.html into `work/viewer/`.** Lift the parsing + extrusion + axle code into TypeScript modules, wrap them in a Vite app, add the production UX (manifest, multi-piece layout, inspect panel). Keeps the convention-discovery work intact and avoids re-authoring the parser. Cost: TS migration of ~500 lines of working JS, plus the M3 production-UX work.
2. **Keep preview.html as the authoring/QA tool; build `work/viewer/` independently.** preview.html stays single-piece, single-file, opened from `file://`. `work/viewer/` is rebuilt in TS / Vite from the SPEC, using preview.html as a reference implementation rather than as the substrate. Higher total code volume, but each tool stays clean for its purpose.
3. **Promote preview.html and skip `work/viewer/`.** Stay single-file HTML for the production deploy too; add a `?piece=NNN` URL parameter, a manifest fetch, and a piece picker; deploy via GitHub Pages by serving the same `preview.html` with the manifest + asset folders alongside it. Lowest code volume; loses the TS / Vite scaffolding the SPEC originally chose for type safety + dev ergonomics. Reasonable to revisit if the production viewer's complexity stays modest.

This decision is open. The roadmap row M0.6 tracks preview.html's continued development independent of the resolution; whichever path is chosen, the v1b polygon-cut + hinge work and the cutouts + multi-cutaway work happen against `preview.html` first, then either port forward (option 1 / 3) or fork forward into `work/viewer/` (option 2). Recommended next step before deciding: ship v1b on preview.html and live with the result for a few pieces. The polygon-cut + adjacency BFS + hinge hierarchy is the largest remaining piece of architectural risk; if it works cleanly in plain JS at preview.html scope, option 1 or 3 becomes the obvious move; if it gets tangled, the rebuild-in-TS option earns its keep.
