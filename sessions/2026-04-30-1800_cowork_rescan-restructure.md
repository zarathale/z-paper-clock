---
date: 2026-04-30
start_time: "18:00"
end_time: "18:30"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Restructure the repo to receive gen-2 source scans (flat-bed home scanner) after gen-1 phone scans were determined unsuitable for the auto-trace pipeline.

## What was done

**Trigger.** Zarathale opened the M1-shipped piece 031 in Inkscape and observed a clear bow on what should be a straight east-west top edge — gutter warp from the gen-1 handheld phone capture survived the pre-processing pipeline. Decision in chat: source-quality fix beats any tracing-pass refinement; capture all 27 pages on a flat-bed home scanner instead.

**Four-question intake** (via AskUserQuestion):

1. *Archive plan* → consolidated archive folder under `source/_archive/phone-scans-2025/` (and `work/_archive/m1-plate-d-phone/` for derivatives).
2. *Intake path* → canonical paths preserved; new `source/scans-intake/` drop folder added for in-flight scans.
3. *Scanner specs* → 600 DPI, color JPG, sRGB.
4. *Filenames* → reuse existing names from `inventory.md` (zero downstream churn).

**Files moved.**

```
source/scans-raw     → source/_archive/phone-scans-2025/scans-raw      (27 files)
source/scans-clean   → source/_archive/phone-scans-2025/scans-clean    (27 files)
source/scans-prepped → source/_archive/phone-scans-2025/scans-prepped  (13 files)

work/pieces             → work/_archive/m1-plate-d-phone/pieces        (11 piece dirs)
work/auto-trace-test    → work/_archive/m1-plate-d-phone/auto-trace-test
work/auto-trace-test-v2 → work/_archive/m1-plate-d-phone/auto-trace-test-v2
work/scripts/RESCAN_FINDINGS.md → work/_archive/m1-plate-d-phone/RESCAN_FINDINGS.md
```

**Files created.**

- `source/_archive/phone-scans-2025/README.md` — archive note explaining gen-1 status.
- `source/scans-raw/`, `source/scans-clean/`, `source/scans-prepped/` — recreated empty (with `.gitkeep`).
- `source/scans-intake/` — new drop folder with `README.md` and `.gitkeep`.
- `source/SCAN-INTAKE-CHECKLIST.md` — capture standard, per-file QC checks (top-edge straight, no gutter warp, all corners captured, even illumination, no moiré, sane color), promotion procedure, full intake-loop reference.
- `work/_archive/m1-plate-d-phone/README.md` — explains why M1 outputs were archived; flags that the 11 sidecars are scan-independent and can copy forward verbatim.
- `sessions/2026-04-30-1800_cowork_rescan-restructure.md` (this note).

**Files updated.**

- `source/inventory.md` — new "Scan generations" section; folder layout includes `scans-intake/`; status section split into "Transcriptions: complete" and "Scans: gen-2 in progress."
- `CLAUDE.md` — "Where We Are" status table reworked: gen-1 archived, gen-2 in progress, M0.5 added, M1 flipped to "shipped against gen-1 (archived); to be re-run." "Architectural Decisions (Closed)" Rescans row reversed and footnoted with the date. Two new "Known Issues" entries: pre-processing parameters likely need re-tuning for flat-bed input; `pieces.csv` bbox fractions need re-validation.
- `ROADMAP.md` — added M0.5 (gen-2 rescan + pipeline re-bring-up) with 9-task table; archived M1 detail section with status note pointing at M0.5; M2 dependency updated to M0.5.

**Files explicitly NOT touched.**

- `source/transcriptions/*` — text content is scan-independent; carries forward unchanged.
- `work/pipeline/*` — the four pipeline scripts and Makefile. Battle-tested in M1; will run unchanged against gen-2.
- `work/scripts/preprocess_scans.py` — stays put. May want parameter re-tuning for flat-bed input; that's a M0.5 task, not done here.
- `work/pieces.csv` — left in place. Bbox fractions were derived from gen-1 plate D and are likely close-enough for gen-2; flagged for re-validation in M0.5.0.6.
- `CODE_PROMPT_M1-pipeline-plate-d.md` and `CODE_PROMPT_M1-fix-pipeline-trace.md` — preserved as shipped decision records per CLAUDE.md convention.
- `work/SPEC-3D-VIEWER.md` — design source of truth, scan-independent.

**Verification (post-move).**

```
$ ls source/
_archive  inventory.md  scans-clean  scans-intake  scans-prepped  scans-raw  transcriptions

$ ls source/_archive/phone-scans-2025/
scans-clean  scans-prepped  scans-raw  README.md

$ ls work/
SPEC-3D-VIEWER.md  _archive  pieces.csv  pipeline  scripts

$ ls work/_archive/m1-plate-d-phone/
README.md  RESCAN_FINDINGS.md  auto-trace-test  auto-trace-test-v2  pieces
```

Canonical scan paths exist and contain only `.gitkeep`. Archive paths exist and are populated. Pipeline + scripts unchanged. Transcriptions untouched.

## Open questions

None blocking. M0.5 task list is fully populated in `ROADMAP.md`; first step is at the scanner.

## Next-session handoff

Zarathale: scan all 27 pages per `source/SCAN-INTAKE-CHECKLIST.md`, plates first. QC each scan against the six checks before promoting. Once scans-prepped/ is repopulated, the next Code session can re-run M1 pipeline on gen-2 plate D (M0.5 task 0.5.7). The 11 gen-1 sidecars at `work/_archive/m1-plate-d-phone/pieces/0NN/piece-0NN.json` should be copied forward verbatim — only the SVGs need to be regenerated.
