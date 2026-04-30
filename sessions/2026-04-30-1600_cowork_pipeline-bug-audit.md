---
date: 2026-04-30
start_time: "16:00"
end_time: "TBD"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Audit and correct transcription errors flagged by the M1 linter (pieces 91, 92, and their connection to piece 4), then attempt the M1 Inkscape hand-edit pass — which revealed a systematic pipeline bug blocking all Inkscape work.

## What was done

### Sidecar/transcription corrections

Investigated the 4 linter WARNs. Two were clean (pieces 4 and 10 referencing piece 25 — valid cross-plate references that resolve in M2). Two required correction:

- **Piece 92** (`embedded-labels.md` + `piece-092.json`): transcription error recorded labels as `a₄₁`/`b₄₁`. Scan verification confirmed the disc has plain `a` (12 o'clock) and `b` (6 o'clock) — orientation markers only, no target subscript. The `₄₁` was a misread. Connection is expressed from piece 4's side.
- **Piece 91** (`embedded-labels.md` + `piece-091.json`): similar pattern. Plain `a` and `b` labels. Piece 4 carries the outward positioning guides for both spacers.
- **Piece 4** (`piece-004.json`): added `91a`, `91b`, `92a`, `92b` connections (piece 4 carries the positioning guides for the spacer stack with dotted curved/square outlines).
- `embedded-labels.md`: corrected piece 91 entry (added `a` label, added note about piece 4's guides), corrected piece 92 entry (fixed labels, noted transcription error), updated pieces 4/10 entry (added description of spacer positioning guides).

Files changed:
- `source/transcriptions/embedded-labels.md`
- `work/pieces/091/piece-091.json`
- `work/pieces/092/piece-092.json`
- `work/pieces/004/piece-004.json`

### Pipeline bug discovered

Attempted M1 task 1.5 (Inkscape hand-edit pass). Piece 26 (auto-trace-clean) appeared as a tiny speck in Inkscape. Verified across pieces 31, 32, 91, 92 — all broken. Two bugs found:

**Bug 1 (all pieces):** `_trace_native` in `02-trace.py` strips potrace's `<g transform="...">` wrapper when extracting path elements. Potrace outputs paths in a scaled/flipped coordinate space (typical: `translate(0, H) scale(0.1, -0.1)`). Without the transform, paths render far outside the declared viewBox. Confirmed by inspecting piece-026.svg: paths have coordinates in the thousands (e.g., `M3284 16069`) against a 576×1622 viewBox.

**Bug 2 (piece 32):** bbox in `pieces.csv` too short — crop cuts off the bottom of the elongated oval tongue.

### CODE_PROMPT written

`CODE_PROMPT_M1-fix-pipeline-trace.md` — ready for Code. Status: `ready-for-code`. Covers:
- Diagnostic to confirm potrace transform format
- Fix to `_trace_native` (capture transform, return alongside path strings)
- Fix to `trace_piece` (include transform in raw.svg's path group)
- Fix to `03-layer-split.py` (wrap layer groups in outer transform group)
- Piece 32 bbox correction in `pieces.csv`
- Full pipeline re-run for plate D
- Verification checklist (open 5 specific pieces in Inkscape)

## Open questions

- None blocking the Code session. Piece 32 bbox correction requires Code to inspect the scan and determine the correct `bbox_h` value.
- After the pipeline fix, task 1.5 (Inkscape hand-edit pass) can proceed on: pieces 18, 19, 29, 30 (auto-trace-edit) and pieces 4, 10 (hand-trace). Pieces 26, 31, 32, 91, 92 are auto-trace-clean and need no Inkscape work beyond the visual verify step.

## Next-session handoff

Run the Code session with `CODE_PROMPT_M1-fix-pipeline-trace.md`. After that ships and Zarathale pulls main, do the Inkscape hand-edit pass on the 6 pieces that need it (18, 19, 29, 30 auto-trace-edit; 4, 10 hand-trace). That closes M1 fully.
