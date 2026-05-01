---
date: 2026-04-30
start_time: "23:59"
end_time: "00:30"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

First ingest pass on `inbox/` — promote 97 hand-cropped per-piece PNGs from the working zone into `source/pieces/`, park the one off-convention reference companion in `source/scans-chunks/`, and flip the corresponding `pieces.csv` rows from `pending` → `captured`. M0.5.4 step.

## What was done

Zarathale spent several hours hand-cropping per-piece PNGs from the gen-2 chunk archive in his image editor and saved them into `inbox/`. This session was the audit + promotion step.

**Audit (read-only inspection of `inbox/`).** 98 PNG files at the inbox root, plus an empty `_pending-rescan/`. Surfaced four flags:

1. `021.png` and `022.png` are byte-identical (md5-confirmed). The master list has both as folded brackets in plate C — Zarathale confirmed: "identical artwork, same image, treat as duplicate however you want." Promoted as separate files in their own slots; the convention stays "every piece ID has its own `source/pieces/NNN.png`."
2. `113.png`, `114.png`, `115.png`, `116.png` are all four byte-identical. Cross-shaped face-frame braces; same disposition.
3. `107.png` and `107-weight.png` exist side by side with different content. Per `pieces.csv`, ID 107 is the axle-dimension reference legend ("not a build piece"). Zarathale clarified that both files are reference content (axle dimensions + weight-suspension-wire dimensions), labeled "107" on the original page. Promoted `107.png` to `source/pieces/107.png` (canonical slot for the master-list row); parked `107-weight.png` as `source/scans-chunks/107-weight-reference.png` so the weight-wire dimensions stay accessible without polluting the per-piece archive.
4. None of the PNGs carry DPI metadata in the header. The intake checklist requires 600 DPI; the audit's WARN on missing tags is cosmetic since nothing downstream reads DPI. Verified empirically with a ruler measurement on piece 002 (long axis = 11 5/16″ in print; 6936 px / 11.3125″ = **613 DPI** effective). Above the spec; metadata absence is harmless.

**Move operations** (all `mv`, clean inbox):

- 97 inbox PNGs → `source/pieces/` (95 numeric IDs + `092a.png` + `112a.png`)
- `inbox/107-weight.png` → `source/scans-chunks/107-weight-reference.png`

**`pieces.csv` edit.** Flipped `status` from `pending` → `captured` for the 97 ingested IDs. Cross-checked against `source/pieces/`: zero mismatches in either direction. Final state: 97 captured / 26 pending / 123 total.

**The 26 still-pending IDs:** 003, 005, 008, 010, 012, 013, 014, 015, 016, 017, 034, 035, 065, 067, 073, 075, 076, 080, 090, 092, 094, 097, 100, 110, 120, 121. Concentrated in plate B framework brackets (12–17), plate F hands/anchor/pendulum, plate H pendulum-bob assembly, plus the clock face (121).

**Files touched:**

- 97 new files in `source/pieces/` (the ingest)
- 1 new file at `source/scans-chunks/107-weight-reference.png`
- 98 files removed from `inbox/` (clean working zone)
- `work/pieces.csv` — 97 status edits
- `CLAUDE.md` — bumped the `source/pieces/` row in the status table; appended a new dated footer entry
- `ROADMAP.md` — bumped M0.5.4 from `not-started` to `in-progress` with the 97-of-123 count and the still-pending list

## Open questions

None. The four audit flags all resolved in-conversation.

A residual to flag, not a question: the `107-weight-reference.png` filename is a one-off — `SCAN-INTAKE-CHECKLIST.md` doesn't define a naming pattern for non-build reference companions in `source/scans-chunks/`. Treating it as a one-off rather than a new pattern. If a similar case ever recurs (a second non-piece reference image that doesn't fit the chunk patterns), revisit the convention then.

## Next-session handoff

The natural next steps are:

- **Continue M0.5.4** — capture and crop the remaining 26 pieces. They should land in `inbox/` first, then a follow-up ingest pass repeats this same loop for them.
- **M0.5.2 helper** — the audit done by hand here is exactly what the ingest skill helper is meant to automate. `CODE_PROMPT_M0.5.2-piece-scan-ingest.md` is queued at repo root; once the helper is built, future ingest passes can run it instead of doing this work in chat.
- **M0.5.5** stays `not-started` — gates on full archive completeness (123/123 captured) before it can flip.

The pipeline reshape (M0.5.6 — archive `01-crop.py`, repoint `02-trace.py` at `source/pieces/`) is unblocked any time, but is most useful once a representative sample of pieces is captured. With 97/123 in place, that threshold is now met if Zarathale wants to run M0.5.6 in parallel with the remaining captures.

Commit message for Zarathale to paste into GitHub Desktop is at the end of the closing chat message (subject and body in two separate code blocks).
