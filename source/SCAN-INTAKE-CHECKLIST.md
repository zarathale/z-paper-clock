# SCAN-INTAKE-CHECKLIST.md — gen-2 home-scanner intake

This is the standard for capturing, validating, and promoting gen-2 source scans. It supersedes the gen-1 phone-photo workflow that produced `source/_archive/phone-scans-2025/`.

The goal is **rectilinear silhouettes**: when piece 31 (or any piece) is auto-traced, the top edge runs east-to-west — not bowed, not keystoned. That's an upstream-of-pipeline problem, fixed at the scanner.

---

## Capture standard

| Setting | Value | Why |
|---|---|---|
| Resolution | **600 DPI** | Matches gen-1 effective resolution; sufficient for tracing piece detail; manageable file size. |
| Color mode | **Color** (24-bit RGB) | Bleed-through detection in `preprocess_scans.py` uses chroma. Greyscale would lose that signal. |
| Color profile | **sRGB** | Default for most home scanners; works with Pillow + scikit-image without conversion. |
| File format | **JPG, quality 92+** | Trade-off chosen 2026-04-30 vs. lossless TIFF. Files are 5–10× smaller; pipeline tolerates it (gen-1 was JPG q=92). Re-evaluate if trace quality regresses. |
| Bit depth | 8-bit per channel | sRGB JPG is 8-bit. No need for 16-bit. |
| Flat-bed | **Glass-down, book pressed flat** | The gutter warp in gen-1 was the root cause of the rescan. Press the spine down. Use a light hand to avoid spine cracking. |
| Orientation | **Cover-up, landscape (long edge against scanner) for 13" tall plates** | Matches gen-1 orientation; reduces post-processing rotation. Confirm against scanner's letter/legal max — 10" × 13" needs the scanner's longest dimension to be ≥13". |
| Background | **Black or dark cardstock** | Reduces page-edge halation. Many home scanners ship with a black scan-lid backing. |

**On scanner choice.** Any flat-bed will outperform a phone for this. If your scanner has a "book mode" that compensates for spine curvature, try with and without — sometimes the auto-correction warps in a different direction than the actual book.

---

## Capture order

Follow `source/inventory.md` page order so filenames match. The 13 plates are the highest-stakes scans (they feed the auto-trace pipeline). Front matter, instructions, and back cover are reference-only and tolerate looser standards.

**Plates first** (in order: A, B, C, D, E, F, G, H, I, J, K, L, M). When you finish a plate, run the per-file QC (below) immediately while the book is still on the glass — re-scanning is cheap, re-positioning is cheap, dragging out lurking warp into M2 is expensive.

**Note for spreads (G and H):** the gen-1 scans of these are flat 2-page spreads at 4800×3120 (20:13). Either scan as a spread (if your scanner is wide enough) or scan each page separately and stitch later. Decide before starting; mixing strategies mid-set will create headaches.

---

## File naming

Reuse the gen-1 names from `source/inventory.md`. The pipeline (`01-crop.py`, etc.) and `pieces.csv` reference these names exactly; preserving them means zero changes downstream.

```
p000-cover-front.jpg
p001-title-page.jpg
…
p00x-plate-A-pieces-1-2-6-7-110.jpg
p00x-plate-B-pieces-3-5-8-12-16-93-113-118.jpg
…
p00x-plate-M-clock-face.jpg
p099-cover-back.jpg
```

The full 27-file list is in `inventory.md` under "Page inventory."

**Lowercase only** — the macOS filesystem is case-insensitive. `Plate-A.jpg` and `plate-a.jpg` collide.

---

## Per-file QC checks (run before promoting from intake → raw)

These are the eyes-on-it checks. The book is still flat on the scanner glass at this point, so re-capturing is one click away.

### 1. Top edge runs straight

Open the scan in Preview / Inkscape / any image viewer with grid lines. The **top edge of the printed page** should be parallel to the top edge of the image. If you can see daylight between them at one corner — re-scan with the book repositioned.

This is the gen-1 failure mode. Catch it here, not in M1.

### 2. No gutter warp

The **spine-side margin** should be the same width top-to-bottom. If the inner margin pinches or bows toward the spine, the page wasn't pressed flat. Press harder, scan again.

### 3. All four corners fully captured

The image should include the full printed area plus a small border of unprinted page. If a piece runs off the edge, re-position.

### 4. Even illumination

Hold the scan at arm's length. Are there bright streaks, shadow bands, or hot spots? Most flat-beds are even by design — if they aren't, the lid may not be closing fully.

### 5. No moiré or aliasing on the printed art

Look closely at the gear-tooth strips on plates F and G. Moiré (false patterning) at 600 DPI is rare on offset-printed books like this one but can show on the gear teeth. If you see it, try 1200 DPI for that plate (and update this doc).

### 6. Sane color

Pages should look cream-on-cream, not blue-tinted (cool light) or yellow-tinted (warm light). Most flat-beds calibrate to sRGB; if yours doesn't, run the white-balance step in pre-processing.

If a scan fails any of 1–4, **re-scan**. If it fails 5 or 6 but 1–4 pass, log it in the intake notes and continue — those are correctable downstream; geometry isn't.

---

## Promotion: intake → raw

Once a scan passes the QC checks above:

```bash
cd ~/Documents/GitHub/z-paper-clock

# Rename and promote (example for plate A)
mv source/scans-intake/Scan_001.jpg \
   source/scans-raw/p00x-plate-A-pieces-1-2-6-7-110.jpg

# Verify the canonical filename matches inventory.md
grep 'p00x-plate-A' source/inventory.md
```

Repeat for every plate / page. When all 27 are in `scans-raw/`, the intake folder should be empty (or contain only files that didn't make the cut).

---

## Pipeline: raw → clean → prepped

After promotion, run the existing scripts to populate the downstream stages:

```bash
cd ~/Documents/GitHub/z-paper-clock

# 1. Manual: dewarp + perspective-correct + crop to 10:13 if needed.
#    Gen-1 used a manual GIMP pass to produce scans-clean/.
#    For gen-2, well-aligned home scans may not need this step at all —
#    if a raw scan is already rectilinear and at the right aspect ratio,
#    just copy it across:
cp source/scans-raw/p00x-plate-A-*.jpg source/scans-clean/

# 2. Pre-processing pipeline (flat-field + bleed suppression)
.venv/bin/python work/scripts/preprocess_scans.py \
    --src source/scans-clean \
    --dst source/scans-prepped

# 3. Spot check: open one prepped plate in an image viewer, confirm
#    bleed-through is suppressed and silhouettes are crisp.
```

**Pre-processing tuning note.** `preprocess_scans.py`'s flat-field strength and bleed-suppression chroma threshold were tuned for handheld phone scans with strong vignette and visible bleed-through. Flat-bed scans are much cleaner; the same parameters may over-correct. If gen-2 prepped plates look washed-out or detail-poor, dial back the flat-field strength first. Track findings in a new `work/scripts/RESCAN_FINDINGS.md` (gen-1 version archived under `work/_archive/m1-plate-d-phone/`).

---

## After all 27 files are in scans-prepped/

You're ready to re-run M1. The next milestone (provisionally **M0.5 — Re-bring-up pipeline on gen-2 plate D**, see `ROADMAP.md`) will validate the pipeline against the new input and decide whether to copy the gen-1 sidecars forward or re-author them.

The gen-1 sidecars at `work/_archive/m1-plate-d-phone/pieces/0NN/piece-0NN.json` are scan-independent (sourced from `embedded-labels.md` and `instructions.md`); they should copy forward verbatim. Only the SVGs need to be regenerated.

---

## Quick-reference: full intake loop

```bash
# Daily scanning session
cd ~/Documents/GitHub/z-paper-clock

# 1. Scan a plate; output lands in source/scans-intake/
# 2. QC the file (the six checks above)
# 3. Promote with the canonical name:
mv source/scans-intake/Scan_NNN.jpg source/scans-raw/<canonical-name>.jpg

# When all 27 are promoted:
.venv/bin/python work/scripts/preprocess_scans.py \
    --src source/scans-clean \
    --dst source/scans-prepped

# Then start M0.5: re-run M1 against gen-2 plate D and compare.
```
