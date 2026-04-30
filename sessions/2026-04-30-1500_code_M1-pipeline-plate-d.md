---
date: 2026-04-30
start_time: "15:00"
end_time: "TBD"
mode: code
participant: Zarathale (Alan)
target: M1-pipeline-plate-d
orchestration_prompt: CODE_PROMPT_M1-pipeline-plate-d.md
---

## Goal

Build the per-piece authoring pipeline (01-crop.py through 04-validate-sidecars.py + Makefile) and run it end-to-end on plate D's 11 pieces.

## What was done

**Prerequisites resolved before writing code:**
- Installed Python 3.12 and native potrace via `brew install python@3.12 potrace`
- Created `.venv` at repo root with `python3.12 -m venv .venv`
- Installed all required packages: `Pillow scipy scikit-image numpy lxml potracer`

**Files created:**
- `work/pipeline/01-crop.py` — reads `work/pieces.csv`, resolves plate → prepped scan via glob, crops each piece using fractional bbox coords, writes `work/pieces/NNN/crop.png`
- `work/pipeline/02-trace.py` — prefers native potrace (confirmed on PATH); falls back to pure-Python potracer. Grayscale → Otsu threshold (-10 bias) → morphological close → trace → `raw.svg` + `bitmap.png`
- `work/pipeline/03-layer-split.py` — classifies paths from `raw.svg` into 8 canonical layers (largest closed path = silhouette; contained >5% area = cutouts; small closed = labels; open paths = marks-other); writes `piece-NNN.svg` with all 8 layer groups always present
- `work/pipeline/04-validate-sidecars.py` — lints `piece-NNN.json` sidecars for required fields, id/filename match, plate/CSV consistency, reciprocal connections and axles; exits 0 with "no sidecars found" when directory is empty
- `work/pipeline/Makefile` — `crop`, `trace`, `layers`, `validate`, `pieces`, `clean` phony targets; `clean` removes pipeline outputs but preserves JSON sidecars

**Pipeline run results:**
- `make pieces` ran end-to-end with no tracebacks
- 11 piece directories created: 004 010 018 019 026 029 030 031 032 091 092
- Each contains `crop.png`, `bitmap.png`, `raw.svg`, `piece-NNN.svg`
- `make validate` exits 0 with "No sidecars found" (expected — sidecars are M1 Cowork follow-up)
- `make clean` removes pipeline outputs and leaves JSON sidecars intact (verified with stub)
- Deliberate plate-mismatch test: validator correctly reported `ERROR: plate "X" does not match pieces.csv plate "D"` and exited non-zero

**Observations from the trace run:**
- Piece 032 produced only 5 paths total (1 silhouette, 4 labels, no cutouts) — consistent with it being a simple rectangular piece per embedded-labels.md
- Pieces 004 and 010 (the tall hand-trace-bucket strips) produced 365 and 205 paths respectively — heavily detailed, will need significant Inkscape cleanup in task 1.5
- Native potrace confirmed in use at startup ("using native potrace")
- No per-piece threshold overrides were needed for plate D

**Notes on the cutout classification threshold:**
The 5% area threshold for distinguishing cutouts from labels works well for disc and gear-shaped pieces (092, 026, 029) but places nearly all paths in `cutouts` for the tall strip pieces (004, 010) because their many interior shapes are large relative to a very tall silhouette. These will be reclassified during the Inkscape pass (task 1.5).

## Branch / commit

Branch: `claude/vigorous-rhodes-06b447`
Commit SHA: 60a9fb6
PR: https://github.com/Zarathale/z-paper-clock/pull/1

## Open questions

- None blocking M1 Code work. The Inkscape hand-edit pass (task 1.5) and sidecar authoring (task 1.6) are Cowork-owned follow-ups.
- The `.venv` path in the Makefile (`../../.venv/bin/python`) assumes the virtualenv lives at repo root. If Zarathale uses a different Python env, the PYTHON variable at the top of the Makefile can be overridden: `make PYTHON=python3.12 pieces`.

## Next-session handoff

The next Cowork session (M1 task 1.5 + 1.6) should:
1. Open each `work/pieces/NNN/piece-NNN.svg` in Inkscape and do the light hand-edit pass — move valley/mountain folds out of marks-other, pull axle markers out, clean up cutout misclassifications on the tall strips.
2. Author the 11 `piece-NNN.json` sidecars by reading `embedded-labels.md` §Panel D.
3. Run `make validate` against the completed sidecars and iterate until clean.
