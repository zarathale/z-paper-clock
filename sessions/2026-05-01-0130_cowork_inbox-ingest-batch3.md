---
date: 2026-05-01
start_time: "01:30"
end_time: "02:00"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Third ingest pass on `inbox/`. Sixteen new per-piece PNGs to promote, including the editor crops of pieces 34/35/94 out of the stitched composites from the prior session. After this pass, 95% of the master list is captured.

## What was done

**Per-piece moves to `source/pieces/`** — all 16 currently `pending` in `pieces.csv`, all flipped to `captured`:

| Piece | Plate | Section | Notes |
|---|---|---|---|
| 003 | B | framework | Vertical frame strip (paired with 1) |
| 005 | B | framework | Vertical frame strip (paired with 2) |
| 008 | B | framework | Vertical frame strip (paired with 6) |
| 012 | B | framework | Bracket piece (12/13/14 top row — 13/14 still pending) |
| 015 | B | framework | Bracket piece (15/16/17 bottom row — 16/17 still pending) |
| 034 | G | motor-wheel | Tight crop out of `34_35_stitched.png` |
| 035 | G | motor-wheel | Tight crop out of `34_35_stitched.png` |
| 065 | F | anchor-pendulum | Zig-zag anchor arm |
| 067 | F | anchor-pendulum | Rear plate of the anchor; flap labels a–f |
| 073 | F | hands | Star-shaped hands-assembly wheel |
| 075 | F | hands | Star-shaped hands-assembly wheel |
| 076 | F | hands | Small rectangular piece for minute-hand assembly |
| 080 | F | hands | Small rectangle ("Push into wheel 78") |
| 094 | H | anchor-pendulum | Crop out of `94_stitched.png` (composite already tight; no further cropping needed) |
| 120 | F | reference | Axle-mount cardboard square |
| 121 | M | face-case | Clock face — 5088×7016 px (~8.48″×11.69″ at 600 DPI), full-page color capture |

Crop quality is good across the batch — printed-area margins are 0–52 px on every file (most are <30 px). Tight enough that downstream `02-trace.py` should chew on these without complaint.

**`080.jpeg` parked.** The same piece arrived in `inbox/` as both `080.jpeg` (64 KB) and `080.png` (113 KB). md5s differ but pixel-mean abs difference is 0.17 — same content, with the JPG being a slightly lossy intermediate of the PNG (or vice versa). The PNG went to `source/pieces/080.png` as the canonical archive; the JPG went to `source/scans-chunks/080.jpeg` as a redundant intermediate. Nothing deleted.

**Stitched composites from prior session.** After Zarathale's editor pass, both `34_35_stitched.png` and `94_stitched.png` are no longer present in `source/scans-chunks/`. The Affinity/Photoshop save flow apparently moved or replaced them. The L/R partials (`34_35_l.jpeg`, `34_35_r.jpeg`, `94_l.jpeg`, `94_r.jpeg`) remain in `source/scans-chunks/`, so re-stitching is possible if recovery is ever needed — the stitcher script is at `outputs/stitch_lr.py` in the workspace temp dir (still not promoted to the repo; flagged in batch 2 session note as "promote if more L/R captures surface").

**Cumulative state: 117 of 123 captured.** 6 still pending:

- **013, 014** — plate B brackets, companions to the captured 012 (top row 12/13/14)
- **016, 017** — plate B brackets, companions to the captured 015 (bottom row 15/16/17)
- **090** — plate F reduction-gear pulley/gear-stack disc
- **110** — plate A face-frame end rail (the only plate-A piece still missing; 1, 2, 6, 7 all captured)

**Filesystem ↔ pieces.csv parity confirmed:** 117 captured rows ↔ 117 PNG files in `source/pieces/`, zero mismatches.

**`source/scans-chunks/` housekeeping (parallel work, by Zarathale).** Visible in `git status` from this session: Z renamed `10.jpeg` → `010.jpeg` (3-digit consistency), deleted some superseded chunks (`092.jpeg`, `100.jpeg`), modified one (`097.png`), and added byte-identical per-piece copies of 034/035/092/097/100 to `source/scans-chunks/` alongside the canonical copies in `source/pieces/`. The duplicate per-piece copies are Z's deliberate redundant archive — left untouched. The chunks-folder is the recovery zone, so a few extra copies are harmless.

**Files touched (this session, by Cowork):**

- 16 mv to `source/pieces/`
- 1 mv to `source/scans-chunks/` (`080.jpeg`)
- `work/pieces.csv` — 16 status flips
- `CLAUDE.md` — `source/pieces/` row bumped (101 → 117); new dated footer entry
- `ROADMAP.md` — M0.5.4 progress (101 → 117) + still-pending list trimmed

## Open questions

None new. The two open items from prior sessions remain:

1. **Promote `stitch_lr.py` to `work/scripts/`?** Still no decision. With only 6 captures left and likely no more L/R partials needed (those 6 pieces are all small-to-moderate, fittable under the lid), this may not be worth promoting at all. Flagging for closeout: if the remaining 6 land cleanly without stitching, archive the script as a one-off rather than promoting.

2. **Stitch quality vs. editor stitch.** Now that 094 is in `source/pieces/` directly from the cv2 stitched composite, downstream tracing is the next quality check on the seam. If `02-trace.py` produces a clean silhouette across the seam region, that's strong evidence the stitch was good. If it doesn't, fall-back is re-stitching from the L/R partials in Affinity.

## Next-session handoff

The remaining 6 captures should be quick:

- **Plate B brackets 013, 014, 016, 017** — these sit adjacent to the already-captured 012/015 in two 1×3 rows. Likely a single bed capture for the top row (12/13/14, with 12 already in hand for cross-check) and another for the bottom (15/16/17). Per spec, multi-piece chunks list complete pieces in ascending order — so a top-row chunk would be named `12_13_14.{jpeg,png}` (re-capturing 12 alongside 13/14 is fine; the cleanest of the two captures stays in `source/pieces/`).
- **Plate F piece 090** — single small disc; quick capture.
- **Plate A piece 110** — face-frame end rail; sits alongside other plate-A pieces (1, 2, 6, 7, 110) Z has already captured.

Once those land, M0.5.4 closes. Then M0.5.5 (ingest skill audit) becomes meaningful — the helper script queued via `CODE_PROMPT_M0.5.2-piece-scan-ingest.md` should report a clean 123/123 captured archive with no pending. After that, M0.5.6 (pipeline reshape: archive `01-crop.py`, repoint `02-trace.py` at `source/pieces/`) is the next Code session and unblocks M2.

Commit message for Zarathale to paste into GitHub Desktop is at the end of the closing chat message (subject and body in two separate code blocks).
