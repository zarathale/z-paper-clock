---
date: 2026-05-06
start_time: "23:00"
end_time: "01:00"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

PM-mode session to make `tag-pieces.html` productively pullable after the 2026-05-05 capture closure, conduct the v2 tagging pass against all 123 pieces, and audit the resulting export for note-vs-tag contradictions before merge into `work/piece_characters_v2.yaml`.

## What was done

### `tag-pieces.html` — data refresh

Refreshed the embedded data snapshot. 6 stale `status:"pending"` rows (013/014/016/017/090/110) flipped to `captured` in `PIECES`; `INITIAL_STATE` flips them to `tagged`. Bracket clones 013/014/016/017 inherit 012's `folded / bracket-tab` (byte-identical drawings per the 2026-05-05 cluster resolution). 110 keeps its embedded-labels pair-tag note; 090 keeps its speculative-tag flag. Comments above both blocks document the patch and the localStorage caveat (clear site data once if seeded under v2 schema before 2026-05-06).

### `tag-pieces.html` — subtype dropdown UX

Replaced the subtype text-input + datalist autocomplete with an alpha-sorted `<select>` dropdown built from `SUBTYPE_VOCABULARY`. Final option is "Other (type below)…" → reveals a custom text input for coining new slugs. `populateSubtypeList()` rewritten to populate the select; `renderCard()` subtype-display logic handles three branches (no subtype / vocabulary match / custom-coined). `change` and `input` event handlers split between the dropdown and the custom field. `SELECT` added to the keyboard-shortcut bypass list (was just `TEXTAREA`/`INPUT`) so typing in the dropdown doesn't fire character shortcuts. Driver: Alan flagged that slug-only autocomplete didn't help him pick best-fit subtypes during sustained tagging.

### Cheat-sheet authoring

`claude-work/to-alan/tag-pieces-reference/README.md` — distilled from `work/piece_characters_v2.yaml` lines 1-175. Decision tree for the 7 characters with example pieces at each leaf; the two clarifications worth knowing (glue is agnostic — flat-decorative vs flat-laminate both collapse into plain `flat`; sliding axles count — any pin/wire/rod pass-through is an axle marker); status-value semantics including pair-tag's "ignore for net-new tagging" framing; what-to-trust-on-each-card priority list (image first, v1_was as breadcrumb, per-piece note, pieces.csv inventory prose as background only); edge cases from the 2026-05-03 walkthrough. `subtypes.md` is the per-subtype dictionary — definition + piece list for every slug currently in use, organized by visual category (Frame rails, Brackets, Boxes, Tubes, Teeth strips, Discs, Pinion mounts, Anchor/pendulum, Bob, Frame braces, Hands, Case, Misc rings, Other), with the unused-vocabulary slugs called out separately. README's Subtype section points at `subtypes.md`. Both gained a "Navigating directly to a piece" section after I confirmed the existing Jump-by-id feature (`Jump` button + `j` shortcut, `prompt()` for id, validates against `PIECE_BY_ID`, resets filters if needed).

### `claude-work/QUEUE.md` reorder

Now #1 stays "tag 123 pieces in tag-pieces.html" but updated to reflect post-refresh pullability + the localStorage caveat. Soon reordered with reasoning: architecture call (DECISIONS #4) promoted to #2 (three substantive `preview.html` ships now push the question per STATUS Charter-rollout); audit-v2 + dashboard CODE_PROMPT surfaced explicitly at #3 (was buried in STATUS asset-state as a post-tag follow-on); attach-x convention demoted to #4; 093a/093b fold paths added at #5 (was in STATUS SVG-layer-authoring open-questions); build-graph split-pieces extension demoted to #6. Footer log entry captures the reasoning.

### Tagging session + export audit

Alan tagged 123/123 pieces in one bench session — distribution shifted significantly:

| character | pre-session | post-session | Δ |
|---|---|---|---|
| flat | 28 | 11 | −17 |
| flat-cutout | 4 | 0 | −4 |
| flat-axle | 28 | 28 | 0 |
| flat-axle-cutout | 17 | 11 | −6 |
| folded | 40 | 60 | +20 |
| folded-axle | 4 | 12 | +8 |
| reference | 1 | 1 | 0 |

First export at 2026-05-07T03:34Z; second post-triage export at 2026-05-07T04:00Z. Both saved at `claude-work/state/piece_characters_export-2026-05-07.yaml` (the second overwrote the first).

Audit flagged 14 piece IDs as note-vs-tag contradictions across 11 cluster-types: cutout-removed (038/046/047/062/064/087); cutout-added (058/059); flat-cutout→folded (043/044/071/079); axle-added (048); axle-removed (100); folds-removed (067). Alan resolved 12 of 14 across two triage rounds — 8 in round 1 with bracketed editor comments preserved in-place (038/046/047/058/059/062/064/087), 5 in round 2 with clean note rewrites (043/044/048/067/071). Plus a bonus clarifying note added on 081 (not a contradiction; same tag both passes, but the new note resolves a stale "[this has a starshaped alignment mark in the center, not a cutout]" claim from the 2026-05-03 framing).

## Open questions

- **079** still tagged `flat` (was `flat-axle-cutout`); note still asserts cutouts cut through both layers as a stack. Likely missed in round 2 triage rather than intentional — partner 78 stayed `flat-axle-cutout` with the back-to-back stack-cut convention, and 79 is supposed to be the back-side glued partner. Re-review.
- **100** still tagged `flat` (was `flat-axle`); note still asserts the sliding-axles convention should make this `flat-axle`. The sliding-axles convention itself was added to the v2 schema specifically because of this piece — if the tag stays `flat`, the convention needs revisiting. Re-review.
- **`flat-cutout` went to zero pieces.** All 4 v1→v2 flat-cutout pieces reclassified (043/044 → folded; 071 → folded-axle; 079 unresolved). Stays reserved in the schema or retire? DECISIONS-worthy once the picture is final.
- **071's implicit cutout** under `folded-axle`. The v2 schema header's parenthetical "(cutouts)" permits this, but it's worth making explicit if/when more pieces follow the pattern (the schema currently lacks a `folded-cutout` character — folded with cutout but no axle; no piece needs that today).

## Next-session handoff

1. Alan re-reviews 079 and 100 via Jump (`j` → 079, `j` → 100), either re-tags + re-exports or annotates.
2. Notes-cleanup pass on the full export — merge bracketed editor remarks ("[has interior cutout]" etc.) into clean prose; strip stale "RECLASSIFIED v1→v2 to X" lines pointing at characters Alan moved away from; drop pieces.csv-quote prose where eyes-on-piece corrected it; rewrite 081's bracket-only note.
3. Merge cleaned export into `work/piece_characters_v2.yaml` preserving the 175-line schema header. (Export's per-piece block replaces the YAML's `characters:` section; header stays intact.)
4. **Soon #3 (audit-v2 + dashboard)** becomes pullable — author `expected_layers.yaml` v1 keyed by character; merge `character` + `subtype` into `pieces.csv`; draft `CODE_PROMPT_dashboard-and-audit-v2.md`.

## Files touched

- `tag-pieces.html` — data refresh (PIECES + INITIAL_STATE + 2 comment blocks); subtype dropdown conversion (HTML structure, `populateSubtypeList`, `renderCard` subtype-display, save handlers, no-piece reset); `SELECT` added to keyboard bypass.
- `claude-work/QUEUE.md` — Now/Soon rewrite + footer log entry.
- `claude-work/to-alan/tag-pieces-reference/README.md` — new file (cheat sheet).
- `claude-work/to-alan/tag-pieces-reference/subtypes.md` — new file (subtype dictionary).
- `claude-work/state/piece_characters_export-2026-05-07.yaml` — new file (saved twice; final reflects round-2 triage state).

## Doc-sweep

- `tag-pieces.html` data refresh: CLAUDE.md status table already at 123/123 (closed 2026-05-05); `pieces.csv` is canonical state; README.md reflects 123/123. No downstream sweep needed.
- Subtype-dropdown UX change: no other doc references the autocomplete-vs-dropdown UX. Cheat sheet already updated in same pass.
- Cheat-sheet folder under `to-alan/tag-pieces-reference/`: per `to-alan/README.md` lifecycle, gets cleared after the tag-pieces session ships (i.e., once audit-v2 + dashboard land in Soon #3). Stays open for now.

No CLAUDE.md or README.md edits needed.
