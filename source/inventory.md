# Source Material Inventory

This is the inventory of source-material photographs for the model paper-clock project. The book scanned here is **_Make Your Own Working Paper Clock_** by **James Smith Rudolph**, with an introduction ("Clocks") by **Isaac Asimov** (Harper & Row 1983; reprinted Perennial 2003 by HarperCollins; designed by Jane Weinberger; ISBN 0-06-091066-6; 10" x 13" softcover, staple-bound). The cover advertises "160 pieces" of cut-out paper parts; pieces are printed on one side of each page only.

This material is held here strictly for personal reference. Anything published from this project should be original, derivative work — not a republication of the book.

## Scan generations

The repo is on **gen-2** scans: flat-bed home-scanner captures of the same 27 pages, captured starting 2026-04-30 to address gutter warp in the original phone scans. Capture standards and intake QC live in [`SCAN-INTAKE-CHECKLIST.md`](SCAN-INTAKE-CHECKLIST.md).

- **gen-1** (handheld phone, 2025–2026) — archived at [`_archive/phone-scans-2025/`](_archive/phone-scans-2025/). Reference-only.
- **gen-2** (flat-bed home scanner, 2026-04-30 onward) — populates the canonical paths below as scans come in.

Filenames are reused across generations so downstream paths (`pieces.csv`, the pipeline scripts, the spec) don't need to change.

## Folder layout

- `scans-intake/` — drop folder for in-flight scanner output before it passes the per-file QC checks. See [`scans-intake/README.md`](scans-intake/README.md).
- `scans-raw/` — promoted scans, renamed by page reference. Filenames sort in reading order.
- `scans-clean/` — cleaned versions: rotated to a single normalized orientation, perspective-corrected, deskewed, cropped to 10:13. (For gen-2, well-aligned raw scans may need only a copy across; gen-1 needed a manual dewarp pass.)
- `scans-prepped/` — flat-fielded + bleed-suppressed plates, output of `work/scripts/preprocess_scans.py`. Auto-trace input.
- `transcriptions/` — plain-text/markdown transcriptions of the introduction, author's note, instructions, and ancillary embedded labels. **Scan-independent**; carries forward unchanged across generations.

## File-naming convention

Format: `pNNN-short-description.jpg`, where `NNN` is the printed page number when known. For unnumbered pages the prefix encodes the section: `p000-` front cover; `p00x-plate-X-` for the cut-out plates A–M; `p099-` back cover.

## Page inventory (27 photos)

### Front matter

| File | Source | Description |
|---|---|---|
| `p000-cover-front.jpg` | IMG_4428 | Front cover. Title, author, "Preface by Isaac Asimov," "Cut this book into 160 pieces…" tagline. |
| `p001-title-page.jpg` | IMG_4436 | Page 1 — title page. "MAKE YOUR OWN WORKING PAPER CLOCK / JAMES SMITH RUDOLPH / HARPER / NEW YORK · LONDON · TORONTO · SYDNEY". |
| `p002-copyright-page.jpg` | IMG_4437 | Page 2 — copyright. "Copyright © 1983 by James Smith Rudolph. Introduction copyright © 1983 by Harper & Row…  Reprinted in Perennial 2003. Designed by Jane Weinberger. ISBN 0-06-091066-6." |

### Introduction — "Clocks" by Isaac Asimov

| File | Source | Description |
|---|---|---|
| `p003-preface-asimov-1.jpg` | IMG_4430 | Page 3 — title "Clocks by Isaac Asimov." History of timekeeping from sundials and water clocks through the medieval mechanical clock. |
| `p004-preface-asimov-2.jpg` | IMG_4431 | Page 4. Galileo, Huygens, Clement, the pendulum clock. Closes by recommending Rudolph's book. |

### Cut-out plates and figure pages (panels A–M)

The book's middle is filled with single-sided plates of numbered paper pieces (1 through ~120) plus two figure-summary pages. User confirmed exactly 13 panels: A–L per their shorthand, plus the clock face as M.

| Panel | File | Source | Sample pieces / contents |
|---|---|---|---|
| A | `p00x-plate-A-pieces-1-2-6-7-110.jpg` | IMG_4414 | 1, 2, 6, 7, 110 — long horizontal frame strips |
| B | `p00x-plate-B-pieces-3-5-8-12-16-93-113-118.jpg` | IMG_4415 | 3, 5, 8, 12–16, 93, 112, 113–118 — frame and bracket pieces |
| C | `p00x-plate-C-pieces-9-11-20-25-27-28.jpg` | IMG_4416 | 9, 11, 20–25, 27, 28 — frame pieces, small triangles |
| D | `p00x-plate-D-pieces-4-10-18-19-26-29-32-91-92.jpg` | IMG_4417 | 4, 10, 18, 19, 26, 29–32, 91, 92 — long frame, accordion/cylinder, round 92 |
| E | `p00x-plate-E-pieces-39-60-74-78-79-82-83-103-112.jpg` | IMG_4418 | 39, 60, 74, 78, 79, 82, 83, 103–107, 111, 112 — gears, axles, "Metal wire goes through the weight" |
| F | `p00x-plate-F-pieces-38-46-58-66-73-90-120.jpg` | IMG_4419 | 38, 46, 49, 58, 59, 61–66, 73–77, 81, 84–90, 120 — escapement-related toothed wheels and stars |
| G | `p00x-plate-G-spread-flat-pieces-33-36-50-57.jpg` | IMG_4439 | **Two-page spread, flat.** 33, 34, 35, 36, 37, 44, 45, 49, 50–57, 27, 32 — main wheels (motor, middle, escapement) and long bottom strips |
| H | `p00x-plate-H-spread-flat-pieces-67-100.jpg` | IMG_4441 | **Two-page spread, flat.** 53, 67–72, 74, 89, 94–100 — anchor, pendulum, weight piece (97), directional disc (100) with N/E/S/W markings |
| I | `p00x-plate-I-pieces-118-119.jpg` | IMG_4423 | 118, 119 — case sides (rectangular framed pieces with star markers) |
| J | `p00x-plate-J-pieces-101-102-108-109-117.jpg` | IMG_4424 | 101, 102, 108, 109, 117 — clock hands (108, 109), face frame backing (117) |
| K | `p00x-plate-K-figures-1-9-overview.jpg` | IMG_4425 | Reference page — Fig 1 (frame assembly), Fig 2 (pendulum support), Fig 3 (wall bracket), Fig 4 (hand wheels), Fig 5 (motor wheel), Fig 6 (motor-wheel teeth), Fig 7 (pulley), Fig 8 (escapement detail), Fig 9 (anchor / pendulum). |
| L | `p00x-plate-L-figures-10-16-assembled.jpg` | IMG_4426 | Reference page — Fig 10–16, including a fully assembled view ("ASSEMBLED") and the schematic diagram (Fig 13). |
| M | `p00x-plate-M-clock-face.jpg` | IMG_4435 | The printed clock face — rectangular tan/brown border, numbers 1–12, minute marks, center hole. Identified as **piece 122** in Fig. 15. |

### Author's Note

| File | Source | Description |
|---|---|---|
| `p033-authors-note.jpg` | IMG_4427 | Page 33. Author's account of finding the original 1947 Paris paperback, building the clock from it, then translating and redrawing the pieces for republication. |

### Instructions

| File | Source | Description |
|---|---|---|
| `p034-instructions-general-directions.jpg` | IMG_4407 | Page 34 — "Instructions for Assembly." I. General Directions: A. Fitting and Identification; B. Cutting and Folding. |
| `p035-instructions-construction-framework.jpg` | IMG_4408 | Page 35 — C. Gluing; D. Mounting; E. Axles. II. Construction. A. The Framework. |
| `p036-instructions-mechanism-motor-wheel.jpg` | IMG_4409 | Page 36 — Frame assembly continued (Figs 2/3). B. The Mechanism. 1. Motor Wheel. |
| `p037-instructions-middle-escapement-mounting.jpg` | IMG_4410 | Page 37 — 2. Middle Wheel; 3. Escapement Wheel; 4. Mounting the Wheels. |
| `p038-instructions-anchor-pendulum.jpg` | IMG_4411 | Page 38 — C. The Anchor and the Pendulum. |
| `p039-instructions-mechanism-hands-weight.jpg` | IMG_4412 | Page 39 — D. Mechanism of the Hands; E. The Weight. |
| `p040-instructions-face-case-adjustments.jpg` | IMG_4413 | Page 40 — F. The Face and the Case. III. Adjustments. Footnote re. transparent tape on face. |

### Back cover

| File | Source | Description |
|---|---|---|
| `p099-cover-back.jpg` | IMG_4429 | Back cover. ISBN-13 978-0-06-091066-2, "GAMES" category label, USD $18.99 / CAN $23.99, harpercollins.com. Photo of a boy with the partially assembled paper-clock parts on a table. |

## Status

**Transcriptions: complete.** `transcriptions/` contains five markdown files covering the covers and front-matter (front cover, title page, copyright page, back cover), the Asimov introduction, the author's note, the assembly instructions (pp. 34–40), and the embedded labels and figure captions printed on plates A–M. Audited 2026-04-29; carries forward unchanged across scan generations.

**Scans: gen-2 in progress.** Gen-1 (phone) archived at `_archive/phone-scans-2025/` as of 2026-04-30. Gen-2 (flat-bed home scanner) capture is underway; `scans-raw/`, `scans-clean/`, and `scans-prepped/` will repopulate as plates come in. See `SCAN-INTAKE-CHECKLIST.md` for capture standard and QC procedure, and `sessions/2026-04-30-1800_cowork_rescan-restructure.md` for the restructure decision.
