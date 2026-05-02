---
date: 2026-05-02
start_time: "23:00"
end_time: "23:30"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Fix the long-standing bug where the thickness slider in `preview.html` updates the displayed value but the slab stays visibly flat in the 3D view.

## What was done

Diagnosed the bug end-to-end in `preview.html` and shipped the fix in the same Cowork session (small-enough surgical edit to skip a CODE_PROMPT handoff).

**Root cause.** The variable `UNITS_PER_MM` was misnamed — its actual computation (`pngDiagMm / vbDiag`) makes it **mm per viewBox unit**, not units per mm. The doc-comment at the head of `derivePPM` already spelled out the right relationship ("multiply a viewBox measurement by UNITS_PER_MM to get mm"), but the variable name read as a vbUnit→mm conversion factor that *should* be applied to anything mm-flavored. So both `renderScene` and `buildSlab` did:

```js
const T = thicknessMm * UNITS_PER_MM;
```

…which gives `mm × (mm/vbUnit)` — nonsense units, and a tiny number. Sanity-checked against piece 067 (viewBox 3613×7434, scan 867×1782 px at 600 DPI): `MM_PER_UNIT ≈ 0.0102`. At slider = 1.0 mm, the slab was 0.0102 three.js units thick on a ~36.7 mm-wide piece — a 1:3600 thickness:width ratio, invisibly flat from any non-edge-on viewing angle. Even slider = 4.0 mm only got to 1:900.

**Fixes applied** (all in `preview.html`):

1. Renamed `UNITS_PER_MM` → `MM_PER_UNIT` throughout the file (replace_all). Pure rename, no behavior change. The doc-comment (`MM_PER_UNIT = (viewBox diagonal in mm) / (viewBox diagonal in viewBox units)`) now reads as a correct identity statement.
2. In `renderScene` (axle-marker `T`) and `buildSlab` (slab `T`), changed `T = thicknessMm * MM_PER_UNIT` → `T = thicknessMm`. Since 1 three.js unit = 1 mm and `thicknessMm` is already mm, no multiplier is needed. The XY conversions still need `MM_PER_UNIT` (they go vbUnit → mm) and were left untouched. Added explanatory comments at both sites pointing at the prior bug so the next reader doesn't recreate it.
3. Bumped axle marker radius from 0.15 to 1.0 mm and adjusted the Z offset to `T/2 + AXLE_R + 0.1` so the sphere sits cleanly above the now-properly-thick front face. Original 0.15 was invisibly small against typical piece widths once the T fix made the slab geometry consistent in mm.

**Doc-sweep.** Grepped for `UNITS_PER_MM` repo-wide; the only other matches are in shipped CODE_PROMPTs (`CODE_PROMPT_preview-html-v1.md`, `CODE_PROMPT_preview-html-v1a.md`, `CODE_PROMPT_preview-html-texture-flip.md`) and prior session notes (`2026-05-02-1700_cowork_067-svg-id-swap.md`, `2026-05-02-1400_code_preview-html-v1a.md`). Per CLAUDE.md these are decision records and stay as-shipped. No changes to SPEC, ROADMAP, README, or CLAUDE.md — the rename and bugfix don't alter any spec or convention, just internal naming + math inside the preview tool.

**Files touched.** `preview.html` only (plus this session note).

## Open questions

None blocking. After Alan reloads `preview.html` and confirms the slab visibly extrudes:

- The new axle-marker size (1.0 mm radius, magenta) may want a different size or color once Alan eyeballs it on a couple of pieces. Easy to tweak via `AXLE_R` constant in `renderScene`.
- Worth a quick check on a piece with a noticeable scan-derived `MM_PER_UNIT` other than ~0.01 (e.g. a face/case piece if any have very different viewBox-vs-scan ratios) just to confirm the slab proportions still feel right across the range.

## Next-session handoff

1. Alan: reload `preview.html`, drag in any piece SVG (065, 066, 067, 069 — all in `inbox/`), confirm the slab now visibly extrudes and the slider responsively changes thickness from ~0.3 mm to ~4.0 mm.
2. If happy: commit message below. If the slab extrusion is over- or under-shooting expectations, capture the actual measurements and we'll re-tune the `MM_PER_UNIT` derivation (likely the 600 DPI assumption — piece 002 was measured at ~613 DPI).
3. Axle markers may want re-sizing or recoloring after Alan sees them on a real piece.

## Addendum — default/fallback thickness 1.0 → 0.4 mm

Alan confirmed the extrusion fix worked, then asked for the default/fallback thickness to drop from 1.0 mm to 0.4 mm — closer to the actual cardstock weight he plans to build with. Three spots in `preview.html`: slider's initial DOM `value` attribute, the parser's fallback assignment in `parseSVG`, and the warning banner text. No code-path changes; pure constant tweak. Commit can fold into the same commit as the extrusion fix, or ship as a tiny follow-up.
