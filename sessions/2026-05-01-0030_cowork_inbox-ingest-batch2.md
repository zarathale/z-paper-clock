---
date: 2026-05-01
start_time: "00:30"
end_time: "01:15"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Second ingest pass on `inbox/`. Four new per-piece PNGs to promote (010, 092, 097, 100), one byte-identical leftover (004), and four L/R partial captures for long pieces 34/35 and 94 that needed stitching before they could continue down the workflow.

## What was done

**Per-piece moves.** Five PNGs in inbox at the root, four of them actually new:

- `010.png`, `092.png`, `097.png`, `100.png` → `source/pieces/`. All four were `pending` in `pieces.csv`; status flipped to `captured`.
- `004.png` → `source/pieces/`. Byte-identical (md5 match) to the existing `source/pieces/004.png` from the first ingest pass. The mv is a no-op for the destination's content but cleans inbox/. No status change (already `captured`).

**L/R stitching (programmatic).** Four scanner partials in inbox: `34_35_l.jpeg` + `34_35_r.jpeg` (multi-piece partial covering pieces 34 and 35, plate G's long zig-zag motor-wheel teeth strips) and `94_l.jpeg` + `94_r.jpeg` (single-piece partial for piece 94, plate H's long pendulum-bob outer casing). Zarathale opted to stitch programmatically rather than continuing in Affinity (option B in the in-session question). Implementation: a one-shot Python helper using `cv2.matchTemplate` with `TM_CCOEFF_NORMED` to find the (dx, dy) overlap between L and R, followed by a vectorized linear-feathered blend across the overlap region. Both stitches scored above the 0.7 "solid" threshold:

| Pair | L size | R size | Output size | Overlap dx | Y-offset dy | Score |
|---|---|---|---|---|---|---|
| 34_35 | 6716×1122 | 6781×1124 | 10707×1135 | 2790 px | 11 px | 0.899 |
| 94 | 6846×1554 | 5503×1575 | 9539×1584 | 2810 px | 9 px | 0.919 |

At 600 DPI: stitched 34/35 ≈ 17.84″×1.89″; stitched 94 ≈ 15.90″×2.64″. Both consistent with the book's printed piece dimensions.

The L/R partials and the stitched composites all moved to `source/scans-chunks/`:

- `34_35_l.jpeg`, `34_35_r.jpeg`, `34_35_stitched.png`
- `94_l.jpeg`, `94_r.jpeg`, `94_stitched.png`

**Pieces 34, 35, 94 stay `pending` in `pieces.csv`.** The stitched composites are chunks, not per-piece crops — Zarathale still needs to open `34_35_stitched.png` and `94_stitched.png` in his editor and crop tightly to per-piece PNGs (`034.png`, `035.png`, `094.png`) before they land in `source/pieces/`. A future ingest pass will move those.

**Stitcher helper.** The Python script lives at the working-directory level only (not in the repo). It's a 100-line one-shot with `cv2.matchTemplate` + linear-blend composite; if Zarathale wants to keep this capability available, the next session can move it to `work/scripts/stitch_lr.py` and document it in `SCAN-INTAKE-CHECKLIST.md`. Holding off on that until there's signal that this approach scales to other long-piece captures — the spec still treats stitching as an editor-side step by default.

**Cumulative state after this session:** 101 of 123 pieces captured; 22 still pending: 003, 005, 008, 012, 013, 014, 015, 016, 017, 034, 035, 065, 067, 073, 075, 076, 080, 090, 094, 110, 120, 121. Concentration is now plate B framework brackets (12–17), plate F hands/anchor/pendulum, and the clock face (121). Pieces 34/35/94 are blocked on editor cropping, not new captures.

**Files touched:**

- 5 mv to `source/pieces/` (004 = no-op overwrite; 010/092/097/100 = new)
- 6 mv to `source/scans-chunks/` (4 partials + 2 stitched composites)
- `work/pieces.csv` — 4 status flips (010/092/097/100)
- `CLAUDE.md` — bumped `source/pieces/` and `source/scans-chunks/` rows; added a new dated footer entry
- `ROADMAP.md` — bumped M0.5.4 progress (97 → 101); updated still-pending list

## Open questions

**Should the stitcher live in the repo?** The current script is in the workspace temp directory, not committed. If Zarathale anticipates more L/R partial captures across the remaining 22 pending pieces (some of plate F's anchor/pendulum work could plausibly need stitching too), it's worth promoting the script to `work/scripts/stitch_lr.py` and adding a "Programmatic stitching (alternative)" subsection to `SCAN-INTAKE-CHECKLIST.md`. If this was a one-off and the rest of the pieces fit comfortably under the lid, no need.

**Stitch quality vs. editor stitch.** cv2's TM_CCOEFF_NORMED at 0.9 is a strong correlation, but it's not the same as a manual visual check. The seam region is a 2790-px-wide linear blend — should be invisible if the underlying captures had similar exposure. Worth a quick spot-check in Inkscape or Preview before the editor cropping pass to confirm the seam isn't ghosting. If it is, the L/R partials are still in `source/scans-chunks/` for a re-stitch in Affinity.

## Next-session handoff

Two distinct threads, in priority order:

1. **Continue M0.5.4** — capture and crop the remaining 22 pieces. Plate B framework brackets (12–17) likely need a single batch capture given they're a 2×3 grid in the same plate region. Plate F has a heavier load (065/067/073/075/076/080/090). Clock face (121) is one large capture probably from plate M (per `pieces.csv`). Pieces 003/005/008 are vertical frame strips paired with already-captured ones (1/2/6). Once captures land in inbox, the same ingest loop applies.

2. **Editor-side cropping for 34/35/94.** Open `source/scans-chunks/34_35_stitched.png` in Affinity, crop to two per-piece PNGs (`034.png` and `035.png`), save into inbox or directly to `source/pieces/` per Zarathale's preference. Same for `94_stitched.png` → `094.png`. Spot-check the seam region while you're in there.

The pipeline reshape (M0.5.6) is unblocked any time, but if Zarathale wants the trace pipeline to chew on the captured 101 pieces in parallel with the remaining captures, that's the natural next Code session — needs a `CODE_PROMPT_M0.5.6-pipeline-reshape.md`.

Commit message for Zarathale to paste into GitHub Desktop is at the end of the closing chat message (subject and body in two separate code blocks).
