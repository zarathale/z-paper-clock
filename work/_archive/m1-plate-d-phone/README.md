# Archive — M1 Plate-D Outputs (gen-1)

This directory holds the M1 milestone outputs that were produced against the gen-1 phone scans (now archived at `source/_archive/phone-scans-2025/`).

## Why archived

The pipeline scripts (`work/pipeline/01-crop.py` through `04-validate-sidecars.py`) shipped clean and the 11 sidecars passed lint, but the underlying SVG silhouettes inherit the scan warp — visible in Inkscape on piece 31, where the top edge curves rather than running east–west. Re-running the same pipeline against gen-2 home-scanner input is expected to fix it without touching the pipeline code.

See `sessions/2026-04-30-1800_cowork_rescan-restructure.md` for the decision.

## What's here

```
work/_archive/m1-plate-d-phone/
├── pieces/                     — 11 piece directories (004 010 018 019 026 029 030 031 032 091 092)
│                                  Each has crop.png, raw.svg, bitmap.png, piece-NNN.svg (layered),
│                                  piece-NNN.json (sidecar — lint-clean)
├── auto-trace-test/            — v1 auto-trace experiment (handheld scans, pre-pre-processing)
├── auto-trace-test-v2/         — v2 auto-trace experiment (pre-processed handheld scans)
└── RESCAN_FINDINGS.md          — gen-1 per-plate scan-quality assessment
```

## What's NOT here (still active in `work/`)

- `work/pipeline/` — the four pipeline scripts and Makefile. They're scan-version-agnostic and will be re-run on gen-2 unchanged at minimum (parameters may want re-tuning).
- `work/scripts/preprocess_scans.py` — same. Ships flat-field + chroma-aware bleed suppression; tuning was for handheld phone bleed-through, may relax for flat-bed input.
- `work/pieces.csv` — bbox fractions describing each piece's location on its plate. Likely close-enough for gen-2 plate D once it's re-scanned, but flagged for re-validation in the rescan milestone.
- `work/SPEC-3D-VIEWER.md` — design source of truth, scan-independent.

## Sidecars: still useful

The 11 JSON sidecars in `pieces/0NN/piece-0NN.json` capture piece names, roles, connections, fold counts, figure references, and `introducedInStep` pointers — all sourced from `embedded-labels.md` and `instructions.md`, none of it scan-derived. When M1 is re-run on gen-2 plate D, the sidecars can be copied forward (only the SVGs need to be regenerated). Keeping them here as a reference rather than re-authoring from scratch.
