# source/scans-chunks/ — multi-piece flat-bed chunk archive

Reference archive of multi-piece scanner-bed chunk captures. Held here so per-piece crops in `source/pieces/` can be re-derived if a tighter margin or different rotation is ever needed.

## Naming

```
NN_NN_NN.{jpeg,png}            — multi-piece chunk listing the COMPLETE pieces inside
NN.{jpeg,png}                  — single-piece chunk (only one piece fully captured)
NN_l.jpeg / NN_r.jpeg          — single-piece L/R partial captures pre-stitching
NN_NN_l.jpeg / NN_NN_r.jpeg    — multi-piece L/R partial captures pre-stitching
NN_stitched.png                — stitched composite (single piece)
NN_NN_stitched.png             — stitched composite (multi-piece)
```

The numeric prefix lists, in ascending order, every piece whose silhouette is **fully visible and not edge-clipped** in the chunk. Partially-visible neighbors are intentionally omitted from the filename — that's the cue for which pieces a chunk can be a source for. Letter-variant pieces (e.g. `92a`) sort alphanumerically with their numeric base, so `92a_98_99.jpeg` is correct ascending order.

Examples:

- `43_44_45.jpeg` — chunk with pieces 43, 44, 45 fully captured. (Piece 36 may be partially visible at the edge but isn't complete, so it doesn't appear in the filename.)
- `34_35_l.jpeg` + `34_35_r.jpeg` + `34_35_stitched.png` — left/right halves and the stitched composite for the long-strip pair pieces 34 and 35.
- `10.jpeg` — single-piece chunk; only piece 10 is fully captured (other pieces in the same scan-bed view are partially clipped or already complete in another chunk).
- `4_18_19_26_29_30_31_32_91_92.jpeg` — large chunk covering most of plate D except piece 10 (which falls in `10.jpeg`).

## Workflow

1. Scan a chunk on the flat-bed → output lands in `inbox/`.
2. Visually verify which pieces are fully captured; rename to the canonical `NN_NN_NN.ext`.
3. (If needed) Stitch L+R partials in your editor. Save the stitched output as PNG (lossless) for archival.
4. Crop each named piece into `source/pieces/NNN.png`.
5. Once all named pieces are extracted, move the chunk file (plus L/R partials and stitched composite) from `inbox/` to here.
6. Commit. These files are the recovery path if a piece needs re-cropping.

## Notes

- Chunk files are reference assets, not pipeline input. The pipeline reads `source/pieces/`.
- Chunks can be JPG (q=92+) since they're captured directly from the scanner; stitched composites should be PNG to preserve seam fidelity.
- If a piece appears partially in multiple chunks but isn't fully captured anywhere, it needs a targeted re-scan — log it and move on.
- The `inbox/` folder is the working-zone equivalent of an in-flight intake; once a chunk is processed, it should not stay there.
