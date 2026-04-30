---
date: 2026-04-30
start_time: "15:00"
end_time: "TBD"
mode: code
participant: Zarathale (Alan)
target: M1-fix-pipeline-trace
orchestration_prompt: CODE_PROMPT_M1-fix-pipeline-trace.md
---

## Goal

Fix two bugs discovered during the M1 Inkscape review pass:
1. All 11 plate-D SVGs render as a tiny speck because potrace's transform was discarded
2. Piece 32's crop cuts off the bottom of the piece

## What was done

**Bug 1 — potrace transform (02-trace.py + 03-layer-split.py):**

- `_trace_native` now parses potrace's SVG output with ElementTree to extract the
  `transform` attribute from the wrapping `<g>` element (e.g.
  `translate(0,1622) scale(0.1,-0.1)`). Returns `(path_strs, transform)` instead
  of `[path_strs]`.
- `_trace_potracer` updated to same return type `(path_strs, "")` — potracer
  outputs pixel-space coords so no transform needed.
- `trace_piece` puts the transform on `<g id="potrace-paths" transform="...">` in
  raw.svg, so the viewBox and coordinate system stay consistent.
- `split_piece` reads the transform back from raw.svg's `potrace-paths` group and
  wraps all Inkscape layer groups in `<g transform="...">` in piece-NNN.svg.

**Bug 2 — piece 32 bbox (pieces.csv):**

- Visual inspection confirmed the old `bbox_h=0.260` crops off the rounded bottom
  of piece 32 (elongated oval tongue). Tested `bbox_h=0.320` against the plate-D
  prepped scan — full piece visible with small margin below.
- Updated `pieces.csv` row for piece 32: `bbox_h` 0.260 → 0.320.

**Pipeline re-run:**

- `01-crop.py` — piece 32 now 384×998 px (was 384×811)
- `02-trace.py` — all 11 pieces traced with transform preserved in raw.svg
- `03-layer-split.py` — all 11 pieces have transform wrapper in piece-NNN.svg
- `04-validate-sidecars.py` — same pre-existing 4 ERRs (piece-004 → 91/92
  asymmetric connections, not introduced by this session) + 4 WARNs (cross-plate
  pieces 25 not yet sidecared). No new ERRs from these changes.

**venv:**

The previous session's .venv (at the old worktree) ended up in Trash. Recreated
at repo root `/Users/mainstage/Documents/GitHub/z-paper-clock/.venv` using
`python3.12 -m venv .venv` with packages: Pillow, scipy, scikit-image, numpy,
lxml, potracer.

## Branch / commit

Branch: `claude/M1-fix-pipeline-trace`
Commit SHA: 409eddd7a646e28ebe0eb5dcc5f23c0ce5b83714

## Open questions

- The 4 ERRs from `04-validate-sidecars.py` are pre-existing (introduced in commit
  9f67619 when pieces 91/92 sidecars were created with `connections: []`). The
  validator requires reciprocation when a sidecar exists. Design intent is
  asymmetric (connection expressed only from piece 4's side). Resolution options:
  add matching connections to 091/092 sidecars, or add `"reciprocal": false` flag
  support to the validator. Deferred — not in scope for this session.

## Next-session handoff

- Verify pieces 026, 031, 032, 091, 092 render correctly in Inkscape (checklist
  items 1–7 from the orchestration prompt)
- Then proceed with M1 task 1.5: Inkscape hand-edit pass on plate D SVGs
  (assign valley/mountain fold paths, axle paths, glue zones to correct layers)
