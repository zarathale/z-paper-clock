# z-paper-clock

Personal project repo for a model paper-clock build, studying *Make Your Own Working Paper Clock* by James Smith Rudolph (Harper & Row 1983; Perennial 2003 reprint). The `source/` folder holds reference scans and transcriptions of the book, kept here strictly for personal study. Anything published from this project should be original, derivative work — not a republication of the book.

## Two halves

**The study** — complete and stable. `source/` holds dewarped scans, transcribed prose, and a comprehensive label/notation pass on all 13 plates. Reference material; not republished from this repo.

**The build** — actively being designed. `work/` is where derivative work grows: a per-piece authoring pipeline (auto-trace + hand-edit) and, eventually, a 3D viewer that turns the cut-out plates into an interactive model of the assembled clock. The build's spec is `work/SPEC-3D-VIEWER.md`; the milestone sequence is in `ROADMAP.md`.

## Layout

- `source/` — reference archive (personal use only)
  - `inventory.md` — page-by-page log mapping scan filenames to printed pages and content
  - `pieces/` — per-piece source archive (lossless PNG, `NNN.png`); the pipeline reads from here
  - `scans-chunks/` — multi-piece chunk captures kept as recovery references
  - `transcriptions/` — markdown text of the book's prose and embedded-label content
  - `_archive/phone-scans-2025/` — gen-1 (handheld phone) raw + clean + prepped, archived 2026-04-30 after gutter warp survived pre-processing
- `work/` — derivative design and exploration
  - `SPEC-3D-VIEWER.md` — build spec; the source of truth for the viewer
  - `pieces.csv` — master index of all 123 pieces in the build
  - `pipeline/` — Python scripts (auto-trace, layer-split, validate)
  - `_archive/m1-plate-d-phone/` — M1 gen-1 outputs against the archived phone scans
- `ROADMAP.md` — build milestone sequence (M0.5 → M6)
- `CLAUDE.md` — working conventions for collaboration with Claude (Cowork ↔ Code workflow, session notes, git, naming)
- `sessions/` — session-by-session working notes
- `CODE_PROMPT_*.md` — per-task orchestration prompts handed to Code sessions; kept after ship as decision records

## Status

The study side is complete: full transcriptions of all prose and embedded-label content, plus the gen-1 cleaned scan archive (now retired to `source/_archive/`).

The build side is mid-onboarding to a **chunk-and-crop** workflow on a flat-bed home scanner — scan multi-piece chunks, hand-crop to per-piece PNGs in editing software, archive the chunks as recovery references. The pipeline reads `source/pieces/NNN.png` directly. M0.5 is the active milestone (chunk-and-crop populating the per-piece archive; pipeline reshape).

## A note on scope

The book is held here for personal reference only. The book is in print and available from HarperCollins; if you want to build the clock, buy a copy. This repo exists to support a derivative paper-clock project, not to redistribute the source.
