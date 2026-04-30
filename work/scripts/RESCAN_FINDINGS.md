# Rescan findings — after pre-processing

After running the new `preprocess_scans.py` pipeline (LAB-luminance flat-field
+ levels stretch + chroma-aware bleed-through suppression) against all 13
plates, the source quality is dramatically improved. Comparing the
auto-trace test results against the same five test pieces, only one piece
still has issues, and only two plates are flagged as candidates for rescan.

## Bottom line

**No rescans are strictly required.** The pre-processing was effective enough
that all 13 plates now produce usable input. Two are flagged as nice-to-have
rescans for cosmetic / quality reasons; both can be deferred without
blocking the build.

## Plate-by-plate result

| Plate | Pre-processing fixed | Remaining issue | Rescan? |
|---|---|---|---|
| A | gutter shadow ✓ | thin frame-strip cut-lines occasionally break under binarization (pieces 1, 2, 6, 7) | optional, higher-res |
| B | left-edge shadow on piece 112 ✓ | minor: same thin-cut-line issue on pieces 3, 5, 8, 12–17 | not needed |
| C | clean already | none | no |
| D | clean already | none | no |
| E | clean already | none | no |
| F | left-edge shadow on pieces 65, 66 ✓ | none | no |
| G (spread) | bleed and slight darkening ✓ | minor: faint vertical seam down the middle (page binding) | not needed |
| H (spread) | bleed-through on right side ✓ | minor: faint vertical seam down the middle | not needed |
| I | clean already | pieces 118, 119 photographed sideways/inverted, right half of frame is the facing-page edge | software-fixable, no rescan |
| J | minor improvement | none | no |
| K | minor improvement | none | no (figure reference, not pieces) |
| L | minor improvement | **visible thumb in bottom-right corner** | optional, cosmetic |
| M | bleed-through on right ✓; brown border preserved ✓ | none | no |

## Specific rescan candidates

### Plate L — optional cosmetic rescan
Visible thumb in the bottom-right corner of the photograph. It overlaps the
"ASSEMBLED" label area (Fig 14, Fig 13). Doesn't affect any cut-out piece
silhouettes (this is a figure-reference page), but if you'd like clean
imagery for the inspect-panel reference views in the 3D viewer, a rescan
would help.

**Why optional:** Fig 13 (the schematic diagram) is the most useful figure
on this plate — it's NOT obscured by the thumb. Same for Fig 14
(ASSEMBLED). The thumb is in dead space.

### Plate A — optional higher-resolution rescan
The frame-strip pieces (1, 2, 6, 7, 110) on plate A have very thin printed
cut-lines. Pre-processing got rid of the gutter shadow that was destroying
auto-trace, but binarization on the cleaned scan still produces a slightly
porous outline because the cut-line is so thin. Same issue is present at a
smaller scale on plates B (pieces 3, 5, 8, 12–17) and C (pieces 9, 11, 20).

A rescan at higher resolution (e.g., 4K instead of the current ~2400px on
the long edge) would make these thin cut-lines bolder relative to the
sampling grid.

**Why optional:** The frame strips are essentially long thin rectangles.
Hand-tracing them in Affinity Designer or Inkscape takes about 30 seconds
each, and the result is geometrically perfect. We were always going to put
the frame strips in the "hand-trace" bucket anyway.

## Software fixes that are NOT rescans

A few residual issues will be addressed in scripts, not by rescanning:

- **Plate I orientation.** Pieces 118/119 are photographed with the page
  rotated 180°. Fix: a one-line PIL rotate at extraction time.
- **Plate I empty right half.** The frame includes the edge of the facing
  page. Fix: tighten the crop at extraction time.
- **Plates G and H spread seams.** A faint vertical line down the middle of
  each spread where the binding sits. Fix: a one-line dodge at the seam
  column at extraction time. (Alternative: ignore — the seam is faint
  enough that pieces near it are still cleanly separable.)

## Recommendation

Proceed to spec without rescans. If at some point during the build we hit
specific pieces that are unrecoverable, we can target a single-page rescan
of just that plate at that time — much cheaper than rescanning everything
preemptively.

If you'd like to do the optional plate-L rescan now anyway (it's a small
one-page job), I'd take it — it would mean the inspect panel gets a
pristine "ASSEMBLED" reference image. Plate A is the lower-priority one
since hand-tracing the frame strips is already the plan.
