# Archive — Phone Scans (gen-1)

This directory holds the original gen-1 source scans of *Make Your Own Working Paper Clock*: phone photographs captured in 2025–2026, dewarped, perspective-corrected, and pre-processed.

## Why archived

Captured with a handheld phone, these scans carry persistent gutter warp and uneven lighting that survived the cleaning pipeline. Visible downstream as bowed top edges, keystoned silhouettes, and traced paths that don't match the printed geometry — see `sessions/2026-04-30-1800_cowork_rescan-restructure.md` for the trigger (piece 31 in Inkscape, post-M1).

The decision was made on 2026-04-30 to set them aside and re-scan all 13 plates plus the text/cover pages on a flat-bed home scanner. See `source/SCAN-INTAKE-CHECKLIST.md` for the gen-2 capture standard.

## Layout

```
source/_archive/phone-scans-2025/
├── scans-raw/      — 27 originals (handheld phone, IMG_4407–4441)
├── scans-clean/    — 27 dewarped, perspective-corrected (10:13 portrait, 2400×3120)
└── scans-prepped/  — 13 plate scans, flat-fielded + bleed-suppressed (auto-trace input)
```

Filenames match the gen-2 set so a path-by-path comparison is possible if needed.

## What's NOT here

- `source/transcriptions/` — text content is independent of scan quality; remains canonical at the active path.
- `source/inventory.md` — same: still applies to gen-2 (filenames preserved per "Reuse existing names" decision).
- `work/_archive/m1-plate-d-phone/` — M1 plate-D pipeline outputs that were derived from these scans live there.

## Restoring (if ever needed)

These files are reference-only. Don't move them back into `source/scans-{raw,clean,prepped}/` — that would mix generations and confuse the pipeline. If a comparison is needed, copy individual files into a temp working directory.
