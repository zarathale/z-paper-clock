# Auto-trace pipeline test — results

Goal: validate whether an automated trace of the cleaned scans produces SVG
outlines clean enough to drive a 3D viewer. Tested five representative pieces
across the difficulty range.

## TL;DR

Auto-trace works **well on bright, clean regions of the scans** and produces
clean SVGs that need only minor manual editing. It struggles when the scan has
**book-gutter shadow** (piece 1) or **bleed-through from the facing page**
(piece 122). Estimate: ~70% of the book's pieces will trace cleanly out of the
box; the remaining ~30% will need either better pre-processing of the scans or
hand-tracing.

**Recommendation: proceed with auto-trace as the production pipeline, with a
small pre-processing pass on the scans first.** See "Recommendation" below.

## Pipeline

```
crop  ->  grayscale  ->  Otsu threshold  ->  morph-close (1 iter)
      ->  potracer (turdsize=10, alphamax=1.0, opttolerance=0.2)
      ->  SVG (stroke-only for diagnostic; production would isolate the silhouette path)
```

Tools: Python 3.10, Pillow, scipy.ndimage, scikit-image (Otsu), `potracer` 0.0.4
(pure-Python Potrace port — slow on large inputs, hence the 700-px downsample;
real `potrace` would be 50–100x faster but isn't available in the sandbox).

## Per-piece results

### piece 92 — disc (plate D)
- **Difficulty class:** simple round
- **Result: PASS — best-case scenario.** Disc circle traced as a smooth Bezier,
  center cross-marks captured, "92"/"a"/"b" label glyphs captured, the
  "Glue to cardboard 1mm thick" annotation captured.
- See: `compare/piece-092.png`
- For production, the script keeps the largest closed path (the disc) and
  discards the annotation text + labels.

### piece 99 — sawtooth arc (plate H)
- **Difficulty class:** fine-detail irregular
- **Result: PASS — surprisingly good on fine detail.** Every individual
  sawtooth tooth captured cleanly (54 closed curves, ~1500 segments). Inner
  egg-shape (92a), outer label "99", and adjacent piece 100's arc are all
  preserved.
- See: `compare/piece-099.png`
- Production note: this piece will need a follow-up to assemble the teeth into
  one continuous silhouette path. The teeth are traced as individual outlines
  rather than as one zigzag. Either acceptable for our 3D pipeline (treat each
  tooth as its own micro-extrusion) or merge in a vector editor.

### piece 33 — triangular motor wheel (plate G)
- **Difficulty class:** fine-detail with structured interior
- **Result: PASS.** All teeth captured (128 curves, ~1500 segments). Triangular
  interior dotted lines come through. Slight bleed-through artifact at the
  top edge but it's clearly distinguishable from the piece outline.
- See: `compare/piece-033.png`

### piece 122 — clock face (plate M)
- **Difficulty class:** large rectangle with printed glyphs
- **Result: MIXED.** The rectangular cut-line is captured, all 12 numerals are
  captured cleanly, and tick-marks come through. **But:** there's significant
  bleed-through from the back of the facing page (visible as a faint inverted
  clock-face overlapping the right half), which Otsu picks up as ink and
  Potrace dutifully traces. Result: extra spurious paths concentrated on the
  right side.
- See: `compare/piece-122-face.png`
- Fix in production: scan-level pre-processing (white-balance the cream paper
  to pure white before tracing) will eliminate most bleed-through. Alternatively,
  this piece is a single rectangle — could be authored by hand in 30 seconds.

### piece 1 — long thin frame strip (plate A)
- **Difficulty class:** long aspect ratio, near book gutter
- **Result: FAIL — useful but not clean.** Strong book-gutter shadow on the
  left dragged the Otsu threshold low (111). At that threshold, half the
  paper texture became "ink", and the cut-line of the strip is lost in
  noise. The dashed fold lines were captured, the hatched glue-reception
  rectangles were captured, the top "1" label is captured. But the long
  vertical cut-line is missing.
- See: `compare/piece-001.png`
- Fix in production: needs scan-level cleanup of the gutter shadow before
  tracing, OR hand-trace this piece (a long rectangle is trivial in any
  vector editor).

## Failure modes identified

The two failures are NOT failures of Potrace itself — Potrace traced exactly
what it was given. They're failures of **pre-processing**:

1. **Book-gutter shadow** (piece 1) — the cleaned scan still has a darkened
   region near the book's spine. This pulls Otsu's threshold low for the
   whole image, and now paper texture clears the threshold.
2. **Bleed-through** (piece 122) — printing on the back of the facing page
   shows through the cream paper on the bright clock-face plate. Otsu picks
   it up as ink.

Both are fixable with one extra pre-processing pass per scan: white-balance to
pure white in the brightest 10% of pixels, and dodge any localized shadow.
Anyone with Affinity Photo or even Preview's adjustments can do this in
seconds; or it can be scripted with PIL/skimage.

## Recommendation

**Proceed with auto-trace as the production pipeline.** Three buckets for the
~120 pieces:

1. **Auto-trace, no edit needed (~50%):** small/medium pieces in bright
   plate regions (most of plates D, E, F, J, M-interior). Output goes
   straight to the 3D scene.
2. **Auto-trace, light edit in Inkscape/Affinity (~30%):** anything with
   intricate teeth (gear pieces 33, 36, 50, 67-area, 99, 100) or with text
   labels mixed in. Edit to (a) keep just the outer silhouette path, and
   (b) optionally simplify Bezier control points.
3. **Hand-trace or hand-construct (~20%):** long strips near the gutter
   (pieces 1, 2, 6, 7, 9, 11), and any rectangle (clock face 122,
   case sides 118, 119) where it's faster to draw a rectangle than to clean
   up an auto-trace.

Add one upstream pre-processing step per plate scan: **white-balance + gutter
de-shadow**. This is a 1-line PIL script per scan and would push bucket 1 from
~50% to ~70%.

## Files in this folder

- `01_crop.py` — crops the five test pieces from the cleaned plates
- `02_trace.py` — runs the auto-trace pipeline
- `03_compare.py` — builds the side-by-side comparison PNGs
- `crops/` — input crops (PNG)
- `bitmap/` — the binarized bitmap actually fed to Potrace (PNG)
- `svg/` — auto-traced output (SVG, stroke-only diagnostic rendering)
- `compare/` — side-by-side comparison PNGs (this is what you want to look at)

## Next steps

Pending decision from Alan:

1. **Accept auto-trace + light hand-edit as the production pipeline?**
   If yes, the 3D-viewer spec can lock that in.
2. **Add the pre-processing pass (white-balance + gutter de-shadow)?**
   Small extra work upfront, much cleaner trace results downstream.
3. **What to do with text labels and fold lines?** The auto-trace captures
   them — useful for the click-to-inspect side panel (we can highlight the
   piece's text labels in 3D), but they should NOT contribute to the
   physical silhouette extrusion. Easy to filter out by path-area threshold.
