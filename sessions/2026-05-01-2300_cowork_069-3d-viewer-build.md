---
date: 2026-05-01
start_time: "23:00"
end_time: "TBD"
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
