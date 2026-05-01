# SCAN-INTAKE-CHECKLIST.md — gen-2 chunk-and-crop intake

This is the standard for capturing source material on a flat-bed home scanner that's smaller than the book's plates, and producing a clean per-piece archive. It supersedes the gen-1 phone-photo workflow (archived under `_archive/phone-scans-2025/`) and the earlier gen-2 plate-oriented draft of this document (which assumed whole-plate captures fit the bed — they don't).

The deliverable is `source/pieces/NNN.png` for every piece in `work/pieces.csv`, derived by hand-cropping multi-piece chunk scans in your editor of choice. The pipeline reads `source/pieces/` directly; there's no "plate slicing" stage anymore.

---

## The chunk-and-crop loop, end to end

1. **Scan a chunk.** Place the open book on the flat-bed and capture whatever pieces fit cleanly under the lid. Output → `inbox/`.
2. **Verify which pieces are complete.** Run the per-file QC checks (below). A piece is "complete" if its full silhouette is visible and not edge-clipped.
3. **Rename to canonical chunk form.** `NN_NN_NN.{jpeg,png}` listing the complete pieces inside, in ascending order. Single-piece chunks → `NN.{jpeg,png}`. Stitched composites → `NN_NN_stitched.png`. (See "Naming" below.)
4. **(If needed) Stitch L+R captures.** When a piece is too long for the bed, scan as `NN_NN_l.jpeg` + `NN_NN_r.jpeg` and stitch in your editor → `NN_NN_stitched.png` (lossless PNG to preserve seam fidelity).
5. **Crop each named piece.** Open the chunk in your editor (Affinity / Photoshop / Preview / GIMP), crop tightly around each complete piece, save as `source/pieces/NNN.png` (lossless PNG, three-digit zero-padded). Letter variants → `NNNa.png`.
6. **Archive the chunk.** Once all named pieces are extracted, move the chunk file (plus L/R partials and any stitched composite) from `inbox/` to `source/scans-chunks/`. The chunk lives there as the recovery path if a piece needs re-cropping later.
7. **Audit.** Run the ingest skill (forthcoming — see `work/pieces.csv` for the master list it'll validate against). It checks filenames, image health, and reports inventory status.

---

## Capture standard

| Setting | Value | Why |
|---|---|---|
| Resolution | **600 DPI** | Matches gen-1 effective resolution; sufficient for tracing piece detail; manageable file size. |
| Color mode | **Color** (24-bit RGB) | Bleed-through detection in any future pre-processing pass uses chroma. |
| Color profile | **sRGB** | Default for most home scanners; works with Pillow + scikit-image without conversion. |
| File format | **JPG, quality 92+** for chunks; **PNG (lossless)** for stitched composites and per-piece archive | Chunks are intermediate (some redundancy with the per-piece crops); PNG matters where lossiness compounds (stitching seams, archive). |
| Bit depth | 8-bit per channel | sRGB JPG/PNG are 8-bit. No need for 16-bit. |
| Flat-bed | **Glass-down, book pressed flat** | Gutter warp was the gen-1 root cause. Press the spine down. Use a light hand to avoid spine cracking. |
| Orientation | **As long-edge fits the bed** | Don't fight the scanner's geometry. Rotate / re-orient as needed so the chunk fits without cropping a piece. |
| Background | **Black or dark cardstock** | Reduces page-edge halation. Many home scanners ship with a black scan-lid backing. |

---

## Capture order

There's no required global order — capture chunks as you go. Plate-by-plate is convenient because pieces of the same functional group tend to live on the same plate, but isn't required. What matters is that every piece in `work/pieces.csv` ends up complete in *at least one* chunk. The ingest skill will surface any that aren't.

For a fresh plate, a useful heuristic:

- **Pass 1: pieces that fit comfortably under the lid.** Take wide chunks (4–8 pieces each) covering as much of the plate as possible. Capture each chunk only once it sits flat with no warp.
- **Pass 2: pieces that hang past the bed edge.** L+R partials, then stitch.
- **Pass 3: edge-case pieces that wouldn't crop cleanly from pass 1.** Re-scan tight to that piece. Filename these as single-piece chunks (`NN.jpeg`).

Capturing the same piece in multiple chunks is fine — only one chunk feeds the per-piece crop, the others stay in `source/scans-chunks/` as alternate views.

---

## Naming

### Chunks (multi-piece captures)

```
NN_NN_NN.{jpeg,png}            multi-piece chunk listing the COMPLETE pieces inside, in ascending order
NN.{jpeg,png}                  single-piece chunk (only one piece fully captured)
NN_l.jpeg / NN_r.jpeg          single-piece L/R partial captures pre-stitching
NN_NN_l.jpeg / NN_NN_r.jpeg    multi-piece L/R partial captures pre-stitching
NN_stitched.png                stitched composite for a single piece (PNG, lossless seam preservation)
NN_NN_stitched.png             stitched composite for a multi-piece chunk (PNG, lossless seam preservation)
```

The numeric prefix lists every piece whose silhouette is fully visible and not edge-clipped in the chunk. Partially-visible neighbors are intentionally omitted from the filename — they're cues for which pieces a chunk can be a re-crop source for. Letter-variant pieces (e.g. `92a`) sort alphanumerically with their numeric base, so `92a_98_99.jpeg` is correct ascending order.

Examples (all currently in `source/scans-chunks/`):

- `43_44_45.jpeg` — complete pieces 43, 44, 45. (Piece 36 may be partially visible at the edge but isn't complete, so it doesn't appear in the filename.)
- `34_35_l.jpeg` + `34_35_r.jpeg` + `34_35_stitched.png` — left/right halves and the stitched composite for the long-strip pair pieces 34 and 35.
- `4_18_19_26_29_30_31_32_91_92.jpeg` — large chunk covering most of plate D except piece 10.
- `10.jpeg` — single-piece chunk for piece 10 (which extends past the bed in the wide-chunk capture).

### Per-piece archive

```
source/pieces/NNN.png       three-digit zero-padded piece number
source/pieces/NNNa.png      letter variant (only 092a and 112a in this book)
```

Lowercase only. PNG only. The pipeline reads from this folder directly.

---

## Per-file QC checks (run before promoting a chunk from inbox/ → source/scans-chunks/)

Eyes-on checks. The book is still flat on the scanner glass at this point, so re-capturing is one click away.

### 1. Top edge of every named piece runs straight

Open the chunk in Preview / Inkscape / any image viewer with grid lines. For each piece you'll list in the filename, the printed top edge should be parallel to the image's top edge. If a piece bows or keystones — re-scan that piece's region with the book repositioned, or push it to a different chunk where it sits flatter.

This is the gen-1 failure mode (gutter warp on piece 31). Catching it here is much cheaper than catching it after the auto-trace pass.

### 2. No gutter warp on captured pieces

For pieces near the spine, the spine-side margin should be the same width top-to-bottom. If the inner margin pinches or bows toward the spine, the page wasn't pressed flat. Press harder, scan again.

### 3. Every piece you want to name in the filename is fully captured

The chunk should include the complete printed area of each named piece, plus a small border of unprinted page around it. If a piece runs off the edge — drop it from the filename. Either it's complete in another chunk (fine) or it needs a separate targeted capture.

### 4. Even illumination

Hold the scan at arm's length. Bright streaks, shadow bands, or hot spots? The lid may not be closing fully. Most flat-beds are even by design — if yours isn't, re-seat the book.

### 5. No moiré or aliasing on the printed art

Look closely at the gear-tooth strips on plates F and G. Moiré at 600 DPI is rare on offset-printed books like this one but can show on the gear teeth. If you see it, try 1200 DPI for that chunk and update this doc.

### 6. Sane color

Pages should look cream-on-cream, not blue-tinted (cool light) or yellow-tinted (warm light). Most flat-beds calibrate to sRGB; if yours doesn't, log it and address downstream.

If a chunk fails any of 1–3 for one or more named pieces: drop those pieces from the filename and either re-capture or accept that another chunk will be the source. If it fails 5 or 6 but 1–3 pass: log it but don't re-scan; those issues are correctable in the per-piece crop or downstream.

---

## Per-piece crop

After a chunk passes QC and is promoted to `source/scans-chunks/`, open it in your editor and:

1. **Crop tightly** around each named piece — typically 50–200 px of unprinted page on each side. Don't crop into the printed silhouette; the auto-trace pipeline needs the complete edge.
2. **Don't rotate** — leave the piece's orientation as it appears on the plate. The viewer's hierarchical Object3D groups handle rotation at assembly time.
3. **Don't dewarp or flat-field at this step** — the source archive holds the raw cropped piece. Any pre-processing (flat-field, bleed suppression) happens later if needed, in a separate pipeline stage that reads from `source/pieces/`.
4. **Save as PNG** with the canonical filename: `source/pieces/NNN.png`. Lossless. RGB or RGBA mode.
5. **Spot-check** the saved file briefly in an image viewer at 100% — confirm no edges are clipped, no extreme JPG artifacts (your editor shouldn't introduce them, but worth a glance).

For the rare letter-variant pieces (currently `092a` and `112a`), use `NNNa.png`.

If two chunks have the same piece complete, pick the cleaner one for the crop. The other stays in `source/scans-chunks/` as a backup.

---

## Promotion: inbox → source/scans-chunks/ + source/pieces/

Once chunk QC passes and per-piece crops are saved:

```bash
cd ~/Documents/GitHub/z-paper-clock

# Rename the chunk to canonical form (example for a 3-piece chunk)
mv inbox/Scan_001.jpg inbox/43_44_45.jpeg

# After cropping pieces 43, 44, 45 to source/pieces/043.png etc., archive the chunk:
mv inbox/43_44_45.jpeg source/scans-chunks/

# Sanity check: pieces landed
ls source/pieces/04[3-5].png
```

---

## Pipeline note

Under the chunk-and-crop model, `source/pieces/` is the canonical pipeline input. The historical `01-crop.py` (which sliced plates using `pieces.csv` bbox fractions) is being archived in a follow-on session — there's no plate to slice anymore. The pipeline starts at `02-trace.py` reading `source/pieces/NNN.png` directly.

Pre-processing (flat-field, bleed suppression) becomes a per-piece operation if/when needed. Flat-bed home scans are typically clean enough that pre-processing may be a no-op on most pieces; re-tune `work/scripts/preprocess_scans.py` per-piece if specific captures need it. Capture findings in a fresh `work/scripts/RESCAN_FINDINGS.md`.

---

## Quick-reference: full intake loop

```bash
# Daily scanning session
cd ~/Documents/GitHub/z-paper-clock

# 1. Scan chunk(s); output lands in inbox/
# 2. QC each chunk (six checks above)
# 3. Rename to canonical chunk form:
mv inbox/Scan_NNN.jpg inbox/<NN_NN_NN>.jpeg

# 4. (If stitching needed) merge L+R in editor → inbox/<NN_NN>_stitched.png
# 5. Crop each named piece in editor → source/pieces/NNN.png (PNG, lossless)
# 6. Archive the chunk:
mv inbox/<NN_NN_NN>.jpeg source/scans-chunks/
# (also move L/R partials + stitched composite if any)

# 7. (Future) run the ingest skill to audit source/pieces/ against work/pieces.csv:
#    "ingest pieces" or "audit piece archive"
```

---

## Notes

- The `inbox/` folder is the working zone for in-flight scans. Once a chunk is processed, it should not stay there. A chunk lingering in `inbox/` for more than a session is a sign that some piece in it needs a follow-up capture — flag it.
- `inbox/_pending-rescan/` (gitignored) is a place to set aside scans that need a re-do without committing them to the archive.
- Capturing a piece in *multiple* chunks is normal and useful. The first complete capture becomes the source for `source/pieces/NNN.png`; the rest are backups in `source/scans-chunks/`.
- Don't re-author transcriptions. `source/transcriptions/*.md` are scan-independent and complete.
- The master piece list is `work/pieces.csv`. If a piece you're cropping isn't in the master list, either you found a piece the transcriptions missed (rare) or you misread a label (more likely). Pause and verify before adding to `source/pieces/`.
